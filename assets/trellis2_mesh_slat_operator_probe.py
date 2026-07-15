#!/usr/bin/env python3
"""Training-free sparse-latent operators starting from a mesh-first Trellis2 latent."""

from __future__ import annotations

import argparse
import json
import os
import time
import traceback
from pathlib import Path

import numpy as np

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
        step = max(1, len(vertices) // 25000)
        pts = vertices[::step]
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=0.2, c=pts[:, 2], cmap="viridis")
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


def rewrite_model_path(path: str, snapshot: Path) -> str:
    if path.startswith("ckpts/"):
        return str(snapshot / path)
    return path


def sparse_merge(feats, coords):
    import torch
    from trellis2.modules.sparse import SparseTensor

    unique, inverse = torch.unique(coords, dim=0, return_inverse=True)
    out = torch.zeros((unique.shape[0], feats.shape[1]), dtype=feats.dtype, device=feats.device)
    counts = torch.zeros((unique.shape[0], 1), dtype=feats.dtype, device=feats.device)
    out.index_add_(0, inverse, feats)
    counts.index_add_(0, inverse, torch.ones((feats.shape[0], 1), dtype=feats.dtype, device=feats.device))
    return SparseTensor(feats=out / counts.clamp_min(1), coords=unique)


def replace_coords(st, coords):
    from trellis2.modules.sparse import SparseTensor

    return SparseTensor(feats=st.feats.clone(), coords=coords.to(st.coords.device, dtype=st.coords.dtype))


def mirror_x(st):
    coords = st.coords.clone()
    lo = int(coords[:, 1].min().item())
    hi = int(coords[:, 1].max().item())
    coords[:, 1] = lo + hi - coords[:, 1]
    return replace_coords(st, coords)


def copy_high_y_shift(st, fraction: float = 0.35, shift_ratio: float = 0.22):
    import torch

    coords = st.coords
    xyz = coords[:, 1:]
    y = xyz[:, 1].float()
    threshold = torch.quantile(y, 1.0 - fraction)
    subset = y >= threshold
    copied_coords = coords[subset].clone()
    copied_feats = st.feats[subset].clone()
    extent = (xyz.max(0).values - xyz.min(0).values).clamp_min(1)
    shift = copied_coords.new_tensor([0, int(extent[0].item() * shift_ratio), int(extent[1].item() * shift_ratio), 0])
    copied_coords = copied_coords + shift
    lo = xyz.min(0).values
    hi = xyz.max(0).values
    valid = ((copied_coords[:, 1:] >= lo) & (copied_coords[:, 1:] <= hi)).all(dim=1)
    return sparse_merge(
        torch.cat([st.feats, copied_feats[valid]], dim=0),
        torch.cat([coords, copied_coords[valid]], dim=0),
    )


def duplicate_scale_from_center(st, scale: float = 0.82):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    center = (xyz.min(0).values + xyz.max(0).values) / 2
    copied_xyz = torch.round((xyz - center) * scale + center).to(coords.dtype)
    copied_coords = torch.cat([coords[:, :1], copied_xyz], dim=1)
    return sparse_merge(torch.cat([st.feats, st.feats.clone()], dim=0), torch.cat([coords, copied_coords], dim=0))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--grid-resolution", type=int, default=None)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

    summary = {
        "kind": "trellis2_mesh_slat_operator_probe",
        "mesh": str(args.mesh),
        "resolution": args.resolution,
        "grid_resolution": args.grid_resolution or args.resolution,
        "transforms": {},
    }

    try:
        import torch
        import trimesh
        import o_voxel
        from trellis2 import models
        from trellis2.modules.sparse import SparseTensor

        hf = Path(os.environ["HF_HOME"])
        snapshot = next((hf / "hub/models--microsoft--TRELLIS.2-4B/snapshots").iterdir())
        pipeline_cfg = json.loads((snapshot / "pipeline.json").read_text())["args"]["models"]
        texturing_cfg = json.loads((snapshot / "texturing_pipeline.json").read_text())["args"]["models"]
        load_start = time.time()
        encoder = models.from_pretrained(rewrite_model_path(texturing_cfg["shape_slat_encoder"], snapshot)).eval().cuda()
        decoder = models.from_pretrained(rewrite_model_path(pipeline_cfg["shape_slat_decoder"], snapshot)).eval().cuda()
        summary["load_seconds"] = time.time() - load_start

        mesh = trimesh.load(str(args.mesh), force="mesh", process=False)
        vertices_np = np.asarray(mesh.vertices).astype(np.float32)
        vertices_min = vertices_np.min(axis=0)
        vertices_max = vertices_np.max(axis=0)
        center = (vertices_min + vertices_max) / 2
        scale = 0.99999 / max(float((vertices_max - vertices_min).max()), 1e-6)
        vertices_np = (vertices_np - center) * scale
        tmp = vertices_np[:, 1].copy()
        vertices_np[:, 1] = -vertices_np[:, 2]
        vertices_np[:, 2] = tmp
        faces_np = np.asarray(mesh.faces).astype(np.int64)
        vertices = torch.from_numpy(vertices_np).float()
        faces = torch.from_numpy(faces_np).long()
        grid_resolution = args.grid_resolution or args.resolution

        fdg_start = time.time()
        voxel_indices, dual_vertices, intersected = o_voxel.convert.mesh_to_flexible_dual_grid(
            vertices.cpu(),
            faces.cpu(),
            grid_size=grid_resolution,
            aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
            face_weight=1.0,
            boundary_weight=0.2,
            regularization_weight=1e-2,
            timing=True,
        )
        summary["fdg_seconds"] = time.time() - fdg_start
        sparse_vertices = SparseTensor(
            feats=dual_vertices * grid_resolution - voxel_indices,
            coords=torch.cat([torch.zeros_like(voxel_indices[:, 0:1]), voxel_indices], dim=-1),
        ).cuda()
        sparse_intersected = sparse_vertices.replace(intersected).cuda()
        with torch.no_grad():
            encode_start = time.time()
            shape_slat = encoder(sparse_vertices, sparse_intersected)
            summary["encode_seconds"] = time.time() - encode_start
            summary["base_shape_tokens"] = int(shape_slat.coords.shape[0])
            summary["base_shape_channels"] = int(shape_slat.feats.shape[1])
            decoder.set_resolution(args.resolution)
            decoder.low_vram = True
            variants = {
                "identity": shape_slat,
                "mirror_x": mirror_x(shape_slat),
                "copy_high_y_shift": copy_high_y_shift(shape_slat),
                "duplicate_scale_center_0p82": duplicate_scale_from_center(shape_slat, 0.82),
            }
            for name, variant in variants.items():
                out_dir = args.out / name
                out_dir.mkdir(parents=True, exist_ok=True)
                decode_start = time.time()
                decoded = decoder(variant)[0]
                vertices_out = decoded.vertices.detach().cpu().numpy()
                faces_out = decoded.faces.detach().cpu().numpy()
                write_obj(out_dir / "mesh.obj", vertices_out, faces_out)
                render_preview(out_dir / "preview.png", vertices_out, name)
                summary["transforms"][name] = {
                    "decode_seconds": time.time() - decode_start,
                    "shape_tokens": int(variant.coords.shape[0]),
                    "vertices": int(len(vertices_out)),
                    "faces": int(len(faces_out)),
                    "bbox_min": vertices_out.min(0).tolist() if len(vertices_out) else [0, 0, 0],
                    "bbox_max": vertices_out.max(0).tolist() if len(vertices_out) else [0, 0, 0],
                }
        summary["cuda_memory_allocated"] = int(torch.cuda.memory_allocated())
        summary["cuda_memory_reserved"] = int(torch.cuda.memory_reserved())
    except Exception as exc:
        summary["status"] = "failed"
        summary["error"] = repr(exc)
        summary["traceback_tail"] = traceback.format_exc().splitlines()[-80:]
    finally:
        (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
