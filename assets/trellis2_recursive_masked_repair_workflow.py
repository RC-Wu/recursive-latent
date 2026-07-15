#!/usr/bin/env python3
"""Masked Trellis2 shape-flow repair for recursive shape-SLat grammars."""

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


def coord_bounds(st):
    xyz = st.coords[:, 1:]
    return xyz.min(0).values, xyz.max(0).values


def clip_valid(coords, limit):
    return ((coords[:, 1:] >= 0) & (coords[:, 1:] <= limit)).all(dim=1)


def tip_continue(st, limit, fraction=0.35, shift_ratio=0.18):
    import torch

    coords = st.coords
    xyz = coords[:, 1:]
    lo, hi = coord_bounds(st)
    threshold = torch.quantile(xyz[:, 1].float(), 1.0 - fraction)
    mask = xyz[:, 1].float() >= threshold
    copied = coords[mask].clone()
    feats = st.feats[mask].clone()
    extent = (hi - lo).clamp_min(1)
    copied[:, 2] += max(1, int(extent[1].item() * shift_ratio))
    valid = clip_valid(copied, limit)
    return sparse_merge(torch.cat([st.feats, feats[valid]], dim=0), torch.cat([coords, copied[valid]], dim=0))


def tip_fork(st, limit, fraction=0.30, shift_ratio=0.16):
    import torch

    coords = st.coords
    xyz = coords[:, 1:]
    lo, hi = coord_bounds(st)
    threshold = torch.quantile(xyz[:, 1].float(), 1.0 - fraction)
    mask = xyz[:, 1].float() >= threshold
    extent = (hi - lo).clamp_min(1)
    dx = max(1, int(extent[0].item() * shift_ratio))
    dy = max(1, int(extent[1].item() * shift_ratio))
    dz = max(1, int(extent[2].item() * shift_ratio * 0.5))
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
    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def side_branch(st, limit, fraction=0.28, shift_ratio=0.18):
    import torch

    coords = st.coords
    xyz = coords[:, 1:]
    lo, hi = coord_bounds(st)
    threshold = torch.quantile(xyz[:, 1].float(), 1.0 - fraction)
    mask = xyz[:, 1].float() >= threshold
    extent = (hi - lo).clamp_min(1)
    copied = coords[mask].clone()
    copied[:, 1] += max(1, int(extent[0].item() * shift_ratio))
    copied[:, 2] += max(1, int(extent[1].item() * shift_ratio * 0.5))
    valid = clip_valid(copied, limit)
    return sparse_merge(torch.cat([st.feats, st.feats[mask].clone()[valid]], dim=0), torch.cat([coords, copied[valid]], dim=0))


def shrink_echo(st, limit, scale=0.72):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    center = (xyz.min(0).values + xyz.max(0).values) / 2
    copied_xyz = torch.round((xyz - center) * scale + center).to(coords.dtype)
    copied = torch.cat([coords[:, :1], copied_xyz], dim=1)
    valid = clip_valid(copied, limit)
    return sparse_merge(torch.cat([st.feats, st.feats.clone()[valid]], dim=0), torch.cat([coords, copied[valid]], dim=0))


def radial_y_clone(st, limit):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    center = (xyz.min(0).values + xyz.max(0).values) / 2
    rel = xyz - center
    rotated = torch.stack([-rel[:, 2], rel[:, 1], rel[:, 0]], dim=1) + center
    copied = torch.cat([coords[:, :1], torch.round(rotated).to(coords.dtype)], dim=1)
    valid = clip_valid(copied, limit)
    return sparse_merge(torch.cat([st.feats, st.feats.clone()[valid]], dim=0), torch.cat([coords, copied[valid]], dim=0))


def compete_grow(st, limit, tip_fraction=0.32, attractor_count=96, step_ratio=0.10):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    y_threshold = torch.quantile(xyz[:, 1], 1.0 - tip_fraction)
    radius = torch.linalg.norm((xyz - center) / extent.clamp_min(1), dim=1)
    radius_threshold = torch.quantile(radius, 0.62)
    tip_mask = (xyz[:, 1] >= y_threshold) | (radius >= radius_threshold)
    tip_indices = torch.nonzero(tip_mask, as_tuple=False).flatten()
    if tip_indices.numel() == 0:
        return st

    angles = torch.linspace(0, 2 * torch.pi, attractor_count + 1, device=xyz.device)[:-1]
    bands = torch.arange(attractor_count, device=xyz.device) % 4
    band_height = 0.20 + 0.13 * bands.float()
    shell = torch.stack(
        [
            torch.cos(angles) * extent[0] * 0.52,
            extent[1] * band_height,
            torch.sin(angles) * extent[2] * 0.52,
        ],
        dim=1,
    )
    attractors = center + shell
    tip_xyz = xyz[tip_indices]
    nearest = torch.cdist(attractors, tip_xyz).argmin(dim=1)
    selected = torch.unique(nearest)

    new_coords = []
    new_feats = []
    step = torch.clamp(torch.round(extent * step_ratio), min=1)
    for local_idx in selected.tolist():
        assigned = attractors[nearest == local_idx]
        direction = assigned.mean(dim=0) - tip_xyz[local_idx]
        norm = torch.linalg.norm(direction).clamp_min(1e-6)
        delta = torch.round(direction / norm * step).to(coords.dtype)
        if torch.all(delta == 0):
            delta[1] = 1
        src_idx = tip_indices[local_idx]
        copied = coords[src_idx].clone()
        copied[1:] = copied[1:] + delta
        new_coords.append(copied[None, :])
        new_feats.append(st.feats[src_idx : src_idx + 1].clone())
    if not new_coords:
        return st
    copied_coords = torch.cat(new_coords, dim=0)
    copied_feats = torch.cat(new_feats, dim=0)
    valid = clip_valid(copied_coords, limit)
    if valid.sum() == 0:
        return st
    return sparse_merge(
        torch.cat([st.feats, copied_feats[valid]], dim=0),
        torch.cat([coords, copied_coords[valid]], dim=0),
    )


GRAMMARS = {
    "continue": ["tip_continue"],
    "fork": ["tip_fork"],
    "side": ["side_branch"],
    "fork_side": ["tip_fork", "side_branch"],
    "echo": ["shrink_echo", "tip_continue"],
    "radial": ["radial_y_clone"],
    "compete": ["compete_grow"],
    "compete_fork": ["compete_grow", "tip_fork"],
}


def apply_op(st, op, limit):
    if op == "tip_continue":
        return tip_continue(st, limit)
    if op == "tip_fork":
        return tip_fork(st, limit)
    if op == "side_branch":
        return side_branch(st, limit)
    if op == "shrink_echo":
        return shrink_echo(st, limit)
    if op == "radial_y_clone":
        return radial_y_clone(st, limit)
    if op == "compete_grow":
        return compete_grow(st, limit)
    raise ValueError(f"unknown op {op}")


def masked_repair(prev_st, candidate_st, flowed_st, blend_alpha: float):
    import torch
    from trellis2.modules.sparse import SparseTensor

    prev_coords_cpu = prev_st.coords.detach().cpu().tolist()
    prev_index = {tuple(int(x) for x in row): i for i, row in enumerate(prev_coords_cpu)}
    cand_coords_cpu = candidate_st.coords.detach().cpu().tolist()
    out_feats = flowed_st.feats.clone()
    preserved = 0
    new_tokens = 0
    for j, row in enumerate(cand_coords_cpu):
        idx = prev_index.get(tuple(int(x) for x in row))
        if idx is None:
            out_feats[j] = blend_alpha * flowed_st.feats[j] + (1.0 - blend_alpha) * candidate_st.feats[j].to(out_feats.device, dtype=out_feats.dtype)
            new_tokens += 1
        else:
            out_feats[j] = prev_st.feats[idx].to(out_feats.device, dtype=out_feats.dtype)
            preserved += 1
    return SparseTensor(feats=out_feats, coords=flowed_st.coords.clone()), preserved, new_tokens


def mesh_stats(vertices, faces) -> dict:
    vertices = np.asarray(vertices)
    faces = np.asarray(faces)
    out = {
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
        "bbox_min": vertices.min(0).tolist() if len(vertices) else [0, 0, 0],
        "bbox_max": vertices.max(0).tolist() if len(vertices) else [0, 0, 0],
    }
    if len(vertices):
        out["bbox_extent"] = (vertices.max(0) - vertices.min(0)).tolist()
    return out


def decode_record(pipe, st, resolution, out_dir: Path, title: str) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    start = time.time()
    decoded = pipe.decode_shape_slat(st, resolution)[0][0]
    vertices = decoded.vertices.detach().cpu().numpy()
    faces = decoded.faces.detach().cpu().numpy()
    write_obj(out_dir / "mesh.obj", vertices, faces)
    render_preview(out_dir / "preview.png", vertices, title)
    stats = mesh_stats(vertices, faces)
    stats["decode_seconds"] = time.time() - start
    return stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--dinov3-model", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--case-name", default=None)
    parser.add_argument("--grammars", nargs="+", default=["fork", "fork_side", "side", "continue"])
    parser.add_argument("--depths", type=int, default=3)
    parser.add_argument("--steps", nargs="+", type=int, default=[1, 2, 4])
    parser.add_argument("--blend-alphas", nargs="+", type=float, default=[1.0])
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--grid-resolution", type=int, default=512)
    parser.add_argument("--fit-scale", type=float, default=0.62)
    parser.add_argument("--seed", type=int, default=720)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

    case = args.case_name or args.mesh.stem
    summary = {
        "kind": "trellis2_recursive_masked_repair_workflow",
        "case": case,
        "mesh": str(args.mesh),
        "image": str(args.image),
        "grammars": {},
        "steps": args.steps,
        "blend_alphas": args.blend_alphas,
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
        local = args.out / "masked_repair_pipeline"
        rewrite_pipeline_json(snapshot / "pipeline.json", local / "pipeline.json", snapshot, args.dinov3_model)
        texturing_cfg = json.loads((snapshot / "texturing_pipeline.json").read_text())["args"]["models"]
        pipe = Trellis2ImageTo3DPipeline.from_pretrained(str(local))
        pipe.cuda()
        encoder = models.from_pretrained(rewrite_model_path(texturing_cfg["shape_slat_encoder"], snapshot)).eval().cuda()
        flow = pipe.models["shape_slat_flow_model_512"]

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
        cond = pipe.get_cond([Image.open(args.image)], args.resolution)
        limit = args.resolution // 16 - 1
        torch.manual_seed(args.seed)

        with torch.no_grad():
            base_st = encoder(sparse_vertices, sparse_intersected)
            summary["base_tokens"] = int(base_st.coords.shape[0])
            summary["fdg_voxels"] = int(voxel_indices.shape[0])
            direct0 = decode_record(pipe, base_st, args.resolution, args.out / "base_direct", f"{case} base direct")
            summary["base_direct"] = direct0
            for grammar_name in args.grammars:
                ops = GRAMMARS[grammar_name]
                grammar_summary = {"ops": ops, "steps": {}}
                for step_count in args.steps:
                    if len(args.blend_alphas) == 1:
                        alpha_items = [("default", args.blend_alphas[0], args.out / grammar_name / f"steps_{step_count}")]
                    else:
                        alpha_items = [(f"alpha_{str(alpha).replace('.', 'p')}", alpha, args.out / grammar_name / f"steps_{step_count}" / f"alpha_{str(alpha).replace('.', 'p')}") for alpha in args.blend_alphas]
                    step_result = [] if len(args.blend_alphas) == 1 else {}
                    for alpha_key, alpha, step_dir in alpha_items:
                        st = base_st
                        alpha_summary = []
                        for depth in range(args.depths + 1):
                            depth_dir = step_dir / f"depth_{depth:02d}"
                            if depth == 0:
                                stats = decode_record(pipe, st, args.resolution, depth_dir / "masked", f"{case} {grammar_name} s{step_count} a{alpha:.2f} d0")
                                stats.update({"depth": depth, "tokens": int(st.coords.shape[0]), "preserved_tokens": int(st.coords.shape[0]), "new_tokens": 0, "blend_alpha": float(alpha)})
                                alpha_summary.append(stats)
                                continue
                            prev = st
                            candidate = st
                            for op in ops:
                                candidate = apply_op(candidate, op, limit)
                            sample_start = time.time()
                            flowed = pipe.sample_shape_slat(cond, flow, candidate.coords, {"steps": step_count})
                            repaired, preserved, new_tokens = masked_repair(prev, candidate, flowed, float(alpha))
                            stats = decode_record(pipe, repaired, args.resolution, depth_dir / "masked", f"{case} {grammar_name} masked s{step_count} a{alpha:.2f} d{depth}")
                            stats.update({
                                "depth": depth,
                                "tokens": int(repaired.coords.shape[0]),
                                "candidate_tokens": int(candidate.coords.shape[0]),
                                "preserved_tokens": int(preserved),
                                "new_tokens": int(new_tokens),
                                "blend_alpha": float(alpha),
                                "sample_seconds": time.time() - sample_start,
                            })
                            alpha_summary.append(stats)
                            st = repaired
                        if len(args.blend_alphas) == 1:
                            step_result = alpha_summary
                        else:
                            step_result[alpha_key] = alpha_summary
                    grammar_summary["steps"][str(step_count)] = step_result
                summary["grammars"][grammar_name] = grammar_summary
        summary["cuda_memory_allocated"] = int(torch.cuda.memory_allocated())
        summary["cuda_memory_reserved"] = int(torch.cuda.memory_reserved())
        summary["status"] = "ok"
    except Exception as exc:
        summary["status"] = "failed"
        summary["error"] = repr(exc)
        summary["traceback_tail"] = traceback.format_exc().splitlines()[-140:]
    finally:
        (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
        print(json.dumps(summary, indent=2))
        if summary.get("status") == "failed":
            raise SystemExit(1)


if __name__ == "__main__":
    main()
