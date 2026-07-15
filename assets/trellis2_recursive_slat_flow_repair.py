#!/usr/bin/env python3
"""Generative repair after recursive shape-SLat coordinate rewriting."""

from __future__ import annotations

import argparse
import json
import os
import time
import traceback
from pathlib import Path

import numpy as np
from PIL import Image

from triton_beegfs_cache_patch import apply_triton_beegfs_cache_patch

apply_triton_beegfs_cache_patch()


def write_obj(path: Path, vertices, faces) -> None:
    vertices = np.asarray(vertices)
    faces = np.asarray(faces)
    with path.open("w") as f:
        for v in vertices:
            f.write(f"v {float(v[0]):.6f} {float(v[1]):.6f} {float(v[2]):.6f}\n")
        for face in faces:
            f.write(f"f {int(face[0]) + 1} {int(face[1]) + 1} {int(face[2]) + 1}\n")


def render_preview(path: Path, vertices, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    vertices = np.asarray(vertices)
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")
    if len(vertices):
        step = max(1, len(vertices) // 30000)
        pts = vertices[::step]
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=0.18, c=pts[:, 2], cmap="viridis")
        center = (vertices.min(0) + vertices.max(0)) / 2
        span = max(float((vertices.max(0) - vertices.min(0)).max()), 1e-3)
        ax.set_xlim(center[0] - span / 2, center[0] + span / 2)
        ax.set_ylim(center[1] - span / 2, center[1] + span / 2)
        ax.set_zlim(center[2] - span / 2, center[2] + span / 2)
    ax.set_title(title)
    ax.set_axis_off()
    ax.view_init(22, -45)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def rewrite_pipeline_json(src, dst, snapshot, dinov3_model):
    data = json.loads(Path(src).read_text())
    models = data["args"]["models"]
    for key, value in list(models.items()):
        if isinstance(value, str) and value.startswith("ckpts/"):
            models[key] = str(Path(snapshot) / value)
    data["args"]["image_cond_model"] = {
        "name": "DinoV3FeatureExtractor",
        "args": {"model_name": str(dinov3_model)},
    }
    data["args"]["rembg_model"] = {"name": "NoOpRembg", "args": {}}
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text(json.dumps(data, indent=2))


def rewrite_model_path(path: str, snapshot: Path) -> str:
    return str(snapshot / path) if path.startswith("ckpts/") else path


def sparse_merge(feats, coords):
    import torch
    from trellis2.modules.sparse import SparseTensor

    unique, inverse = torch.unique(coords, dim=0, return_inverse=True)
    out = torch.zeros((unique.shape[0], feats.shape[1]), dtype=feats.dtype, device=feats.device)
    counts = torch.zeros((unique.shape[0], 1), dtype=feats.dtype, device=feats.device)
    out.index_add_(0, inverse, feats)
    counts.index_add_(0, inverse, torch.ones((feats.shape[0], 1), dtype=feats.dtype, device=feats.device))
    return SparseTensor(feats=out / counts.clamp_min(1), coords=unique)


def clip_valid(coords, limit):
    return ((coords[:, 1:] >= 0) & (coords[:, 1:] <= limit)).all(dim=1)


def tip_fork(st, limit):
    import torch

    coords = st.coords
    xyz = coords[:, 1:]
    lo = xyz.min(0).values
    hi = xyz.max(0).values
    threshold = torch.quantile(xyz[:, 1].float(), 0.70)
    mask = xyz[:, 1].float() >= threshold
    extent = (hi - lo).clamp_min(1)
    dx = max(1, int(extent[0].item() * 0.16))
    dy = max(1, int(extent[1].item() * 0.16))
    dz = max(1, int(extent[2].item() * 0.08))
    all_feats = [st.feats]
    all_coords = [coords]
    for sign in (-1, 1):
        copied = coords[mask].clone()
        copied[:, 1] += sign * dx
        copied[:, 2] += dy
        copied[:, 3] += -sign * dz
        valid = clip_valid(copied, limit)
        all_coords.append(copied[valid])
        all_feats.append(st.feats[mask].clone()[valid])
    return sparse_merge(__import__("torch").cat(all_feats, dim=0), __import__("torch").cat(all_coords, dim=0))


def tip_continue(st, limit):
    import torch

    coords = st.coords
    xyz = coords[:, 1:]
    lo = xyz.min(0).values
    hi = xyz.max(0).values
    threshold = torch.quantile(xyz[:, 1].float(), 0.65)
    mask = xyz[:, 1].float() >= threshold
    copied = coords[mask].clone()
    copied[:, 2] += max(1, int((hi[1] - lo[1]).item() * 0.18))
    valid = clip_valid(copied, limit)
    return sparse_merge(torch.cat([st.feats, st.feats[mask].clone()[valid]], dim=0), torch.cat([coords, copied[valid]], dim=0))


OPS = {"fork": tip_fork, "continue": tip_continue}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--dinov3-model", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--case-name", default=None)
    parser.add_argument("--grammar", choices=sorted(OPS), default="fork")
    parser.add_argument("--depths", type=int, default=2)
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--grid-resolution", type=int, default=512)
    parser.add_argument("--fit-scale", type=float, default=0.62)
    parser.add_argument("--seed", type=int, default=700)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

    case = args.case_name or args.mesh.stem
    summary = {
        "kind": "trellis2_recursive_slat_flow_repair",
        "case": case,
        "mesh": str(args.mesh),
        "image": str(args.image),
        "grammar": args.grammar,
        "depths": [],
        "steps": args.steps,
        "seed": args.seed,
    }

    try:
        import torch
        import trimesh
        import o_voxel
        from trellis2 import models
        from trellis2.modules.sparse import SparseTensor
        from trellis2.pipelines import Trellis2ImageTo3DPipeline, rembg

        class NoOpRembg:
            def to(self, device):
                return self
            def cuda(self):
                return self
            def cpu(self):
                return self
            def __call__(self, image):
                return image

        rembg.NoOpRembg = NoOpRembg
        Trellis2ImageTo3DPipeline.model_names_to_load = [
            "shape_slat_flow_model_512",
            "shape_slat_decoder",
        ]

        hf = Path(os.environ["HF_HOME"])
        snapshot = next((hf / "hub/models--microsoft--TRELLIS.2-4B/snapshots").iterdir())
        local = args.out / "repair_pipeline"
        rewrite_pipeline_json(snapshot / "pipeline.json", local / "pipeline.json", snapshot, args.dinov3_model)
        texturing_cfg = json.loads((snapshot / "texturing_pipeline.json").read_text())["args"]["models"]
        load_start = time.time()
        pipe = Trellis2ImageTo3DPipeline.from_pretrained(str(local))
        pipe.cuda()
        encoder = models.from_pretrained(rewrite_model_path(texturing_cfg["shape_slat_encoder"], snapshot)).eval().cuda()
        summary["load_seconds"] = time.time() - load_start

        mesh = trimesh.load(str(args.mesh), force="mesh", process=False)
        vertices_np = np.asarray(mesh.vertices).astype(np.float32)
        faces_np = np.asarray(mesh.faces).astype(np.int64)
        vmin = vertices_np.min(axis=0)
        vmax = vertices_np.max(axis=0)
        center = (vmin + vmax) / 2
        scale = args.fit_scale / max(float((vmax - vmin).max()), 1e-6)
        vertices_np = (vertices_np - center) * scale
        tmp = vertices_np[:, 1].copy()
        vertices_np[:, 1] = -vertices_np[:, 2]
        vertices_np[:, 2] = tmp
        voxel_indices, dual_vertices, intersected = o_voxel.convert.mesh_to_flexible_dual_grid(
            torch.from_numpy(vertices_np).float().cpu(),
            torch.from_numpy(faces_np).long().cpu(),
            grid_size=args.grid_resolution,
            aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
            face_weight=1.0,
            boundary_weight=0.2,
            regularization_weight=1e-2,
            timing=True,
        )
        sparse_vertices = SparseTensor(
            feats=dual_vertices * args.grid_resolution - voxel_indices,
            coords=torch.cat([torch.zeros_like(voxel_indices[:, 0:1]), voxel_indices], dim=-1),
        ).cuda()
        sparse_intersected = sparse_vertices.replace(intersected).cuda()

        image = Image.open(args.image)
        cond = pipe.get_cond([image], args.resolution)
        flow = pipe.models["shape_slat_flow_model_512"]
        limit = args.resolution // 16 - 1
        torch.manual_seed(args.seed)
        with torch.no_grad():
            st = encoder(sparse_vertices, sparse_intersected)
            for depth in range(args.depths + 1):
                depth_dir = args.out / f"depth_{depth:02d}"
                depth_dir.mkdir(parents=True, exist_ok=True)
                sample_start = time.time()
                repaired = pipe.sample_shape_slat(cond, flow, st.coords, {"steps": args.steps})
                mesh_out = pipe.decode_shape_slat(repaired, args.resolution)[0][0]
                vertices = mesh_out.vertices.detach().cpu().numpy()
                faces = mesh_out.faces.detach().cpu().numpy()
                write_obj(depth_dir / "mesh.obj", vertices, faces)
                render_preview(depth_dir / "preview.png", vertices, f"{case} repair {args.grammar} d{depth}")
                summary["depths"].append({
                    "depth": depth,
                    "input_tokens": int(st.coords.shape[0]),
                    "repaired_tokens": int(repaired.coords.shape[0]),
                    "vertices": int(len(vertices)),
                    "faces": int(len(faces)),
                    "bbox_min": vertices.min(0).tolist() if len(vertices) else [0, 0, 0],
                    "bbox_max": vertices.max(0).tolist() if len(vertices) else [0, 0, 0],
                    "seconds": time.time() - sample_start,
                })
                if depth < args.depths:
                    st = OPS[args.grammar](st, limit)
        summary["cuda_memory_allocated"] = int(torch.cuda.memory_allocated())
        summary["cuda_memory_reserved"] = int(torch.cuda.memory_reserved())
    except Exception as exc:
        summary["status"] = "failed"
        summary["error"] = repr(exc)
        summary["traceback_tail"] = traceback.format_exc().splitlines()[-120:]
    finally:
        (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
