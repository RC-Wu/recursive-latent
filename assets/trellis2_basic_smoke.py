#!/usr/bin/env python3
"""Run a minimal Trellis2 image-to-3D smoke and export geometry-only evidence."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
from PIL import Image


def as_numpy(x):
    if hasattr(x, "detach"):
        return x.detach().cpu().numpy()
    return np.asarray(x)


def write_obj(path: Path, vertices: np.ndarray, faces: np.ndarray) -> None:
    with path.open("w") as f:
        for v in vertices:
            f.write(f"v {float(v[0]):.6f} {float(v[1]):.6f} {float(v[2]):.6f}\n")
        for face in faces:
            f.write(f"f {int(face[0]) + 1} {int(face[1]) + 1} {int(face[2]) + 1}\n")


def render_preview(path: Path, vertices: np.ndarray) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection="3d")
    if len(vertices):
        step = max(1, len(vertices) // 15000)
        pts = vertices[::step]
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=0.2, c=pts[:, 2], cmap="viridis")
        center = (vertices.min(axis=0) + vertices.max(axis=0)) / 2
        span = max(float((vertices.max(axis=0) - vertices.min(axis=0)).max()), 1e-3)
        ax.set_xlim(center[0] - span / 2, center[0] + span / 2)
        ax.set_ylim(center[1] - span / 2, center[1] + span / 2)
        ax.set_zlim(center[2] - span / 2, center[2] + span / 2)
    ax.set_axis_off()
    ax.view_init(22, -45)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--pipeline", default="microsoft/TRELLIS.2-4B")
    parser.add_argument("--pipeline-type", default="512")
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

    import torch
    from trellis2.pipelines import Trellis2ImageTo3DPipeline

    t0 = time.time()
    pipeline = Trellis2ImageTo3DPipeline.from_pretrained(args.pipeline)
    load_s = time.time() - t0
    pipeline.cuda()

    image = Image.open(args.image)
    sampler_params = {"steps": args.steps}
    t1 = time.time()
    result = pipeline.run(
        image,
        seed=args.seed,
        pipeline_type=args.pipeline_type,
        sparse_structure_sampler_params=sampler_params,
        shape_slat_sampler_params=sampler_params,
        tex_slat_sampler_params=sampler_params,
        return_latent=True,
    )
    run_s = time.time() - t1
    meshes, latents = result
    mesh = meshes[0]
    shape_slat, tex_slat, resolution = latents
    vertices = as_numpy(mesh.vertices)
    faces = as_numpy(mesh.faces).astype(np.int64)

    write_obj(args.out / "trellis2_basic_smoke.obj", vertices, faces)
    render_preview(args.out / "trellis2_basic_smoke_preview.png", vertices)

    summary = {
        "pipeline": args.pipeline,
        "pipeline_type": args.pipeline_type,
        "steps": args.steps,
        "seed": args.seed,
        "image": str(args.image),
        "load_seconds": load_s,
        "run_seconds": run_s,
        "resolution": int(resolution),
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
        "bbox_min": vertices.min(axis=0).tolist() if len(vertices) else [0, 0, 0],
        "bbox_max": vertices.max(axis=0).tolist() if len(vertices) else [0, 0, 0],
        "shape_latent_tokens": int(shape_slat.coords.shape[0]),
        "shape_latent_channels": int(shape_slat.feats.shape[1]),
        "tex_latent_tokens": int(tex_slat.coords.shape[0]),
        "tex_latent_channels": int(tex_slat.feats.shape[1]),
        "torch_cuda_mem_allocated": int(torch.cuda.memory_allocated()),
        "torch_cuda_mem_reserved": int(torch.cuda.memory_reserved()),
    }
    with (args.out / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

