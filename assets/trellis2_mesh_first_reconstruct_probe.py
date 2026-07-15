#!/usr/bin/env python3
"""Mesh-first Trellis2/O-Voxel reconstruction probes.

This tests whether a procedural mesh can enter Trellis2 through the native
mesh/O-Voxel path, without using image conditioning as the first step.
"""

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
        step = max(1, len(vertices) // 20000)
        pts = vertices[::step]
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=0.25, c=pts[:, 2], cmap="viridis")
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


def mesh_stats(vertices, faces) -> dict:
    vertices = np.asarray(vertices)
    faces = np.asarray(faces)
    out = {
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
    }
    if len(vertices):
        out["bbox_min"] = vertices.min(0).tolist()
        out["bbox_max"] = vertices.max(0).tolist()
        out["bbox_extent"] = (vertices.max(0) - vertices.min(0)).tolist()
    return out


def rewrite_model_path(path: str, snapshot: Path) -> str:
    if path.startswith("ckpts/"):
        return str(snapshot / path)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--grid-resolution", type=int, default=None)
    parser.add_argument("--save-ovoxel", action="store_true")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

    summary = {
        "kind": "trellis2_mesh_first_reconstruct_probe",
        "mesh": str(args.mesh),
        "resolution": args.resolution,
        "grid_resolution": args.grid_resolution or args.resolution,
    }

    try:
        import torch
        import trimesh
        import o_voxel
        from trellis2 import models
        from trellis2.modules.sparse import SparseTensor

        load_start = time.time()
        hf = Path(os.environ["HF_HOME"])
        snapshot = next((hf / "hub/models--microsoft--TRELLIS.2-4B/snapshots").iterdir())
        pipeline_cfg = json.loads((snapshot / "pipeline.json").read_text())["args"]["models"]
        texturing_cfg = json.loads((snapshot / "texturing_pipeline.json").read_text())["args"]["models"]
        encoder = models.from_pretrained(rewrite_model_path(texturing_cfg["shape_slat_encoder"], snapshot)).eval()
        decoder = models.from_pretrained(rewrite_model_path(pipeline_cfg["shape_slat_decoder"], snapshot)).eval()
        device = torch.device("cuda")
        encoder.to(device)
        decoder.to(device)
        summary["load_seconds"] = time.time() - load_start

        mesh = trimesh.load(str(args.mesh), force="mesh", process=False)
        original_vertices = np.asarray(mesh.vertices).copy()
        original_faces = np.asarray(mesh.faces).copy()
        summary["input_original"] = mesh_stats(original_vertices, original_faces)

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
        summary["input_normalized"] = mesh_stats(vertices_np, faces_np)
        write_obj(args.out / "input_normalized.obj", vertices_np, faces_np)
        render_preview(args.out / "input_normalized_preview.png", vertices_np, "normalized input")

        vertices = torch.from_numpy(vertices_np).float()
        faces = torch.from_numpy(faces_np).long()
        grid_resolution = args.grid_resolution or args.resolution

        encode_start = time.time()
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
        summary["fdg_seconds"] = time.time() - encode_start
        summary["fdg_voxels"] = int(voxel_indices.shape[0])
        summary["fdg_intersected_mean"] = float(intersected.float().mean())

        rec_vertices, rec_faces = o_voxel.convert.flexible_dual_grid_to_mesh(
            voxel_indices.cuda(),
            dual_vertices.cuda(),
            intersected.cuda().bool(),
            split_weight=None,
            grid_size=grid_resolution,
            aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
        )
        rec_vertices_np = rec_vertices.detach().cpu().numpy()
        rec_faces_np = rec_faces.detach().cpu().numpy()
        summary["ovoxel_roundtrip"] = mesh_stats(rec_vertices_np, rec_faces_np)
        write_obj(args.out / "ovoxel_roundtrip.obj", rec_vertices_np, rec_faces_np)
        render_preview(args.out / "ovoxel_roundtrip_preview.png", rec_vertices_np, "O-Voxel roundtrip")

        if args.save_ovoxel:
            packed_dual = dual_vertices * grid_resolution - voxel_indices
            packed_dual = (torch.clamp(packed_dual, 0, 1) * 255).type(torch.uint8)
            packed_intersected = (
                intersected[:, 0:1] + 2 * intersected[:, 1:2] + 4 * intersected[:, 2:3]
            ).type(torch.uint8)
            o_voxel.io.write(
                str(args.out / "input_fdg.vxz"),
                voxel_indices,
                {"dual_vertices": packed_dual, "intersected": packed_intersected},
            )

        slat_start = time.time()
        sparse_vertices = SparseTensor(
            feats=dual_vertices * grid_resolution - voxel_indices,
            coords=torch.cat([torch.zeros_like(voxel_indices[:, 0:1]), voxel_indices], dim=-1),
        ).to(device)
        sparse_intersected = sparse_vertices.replace(intersected).to(device)
        with torch.no_grad():
            shape_slat = encoder(sparse_vertices, sparse_intersected)
            decoder.set_resolution(args.resolution)
            decoder.low_vram = True
            decoded_meshes = decoder(shape_slat)
        summary["shape_slat_seconds"] = time.time() - slat_start
        summary["shape_slat_tokens"] = int(shape_slat.coords.shape[0])
        summary["shape_slat_channels"] = int(shape_slat.feats.shape[1])
        decoded = decoded_meshes[0]
        dec_vertices_np = decoded.vertices.detach().cpu().numpy()
        dec_faces_np = decoded.faces.detach().cpu().numpy()
        summary["shape_slat_reconstruct"] = mesh_stats(dec_vertices_np, dec_faces_np)
        write_obj(args.out / "shape_slat_reconstruct.obj", dec_vertices_np, dec_faces_np)
        render_preview(args.out / "shape_slat_reconstruct_preview.png", dec_vertices_np, "shape SLat reconstruct")
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
