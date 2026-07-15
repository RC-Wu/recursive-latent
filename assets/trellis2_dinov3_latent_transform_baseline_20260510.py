#!/usr/bin/env python3
"""Trellis2 one-shot plus trivial sparse-latent transform baseline.

This is a negative-control baseline for the paper's gen-3D comparison.  It uses
the official DINOv3 image-conditioned Trellis2 pipeline entry, obtains shape and
texture SLAT latents, then applies only naive coordinate-level operations:

* identity decode;
* mirror-x decode;
* copy/shift an upper-z latent subset and merge duplicate coordinates.

It deliberately does not use PS-RSLG handles, per-depth admissibility projection,
root reachability gates, masked local naturalization, or re-encoding after each
recursive step.  It is therefore a "trivial latent-space recursion" baseline,
not an implementation of the proposed method.
"""

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


def as_numpy(x):
    if hasattr(x, "detach"):
        return x.detach().cpu().numpy()
    return np.asarray(x)


def write_obj(path: Path, vertices, faces) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for v in vertices:
            f.write(f"v {float(v[0]):.6f} {float(v[1]):.6f} {float(v[2]):.6f}\n")
        for face in faces:
            f.write(f"f {int(face[0]) + 1} {int(face[1]) + 1} {int(face[2]) + 1}\n")


def render_preview(path: Path, vertices, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")
    if len(vertices):
        step = max(1, len(vertices) // 25000)
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


def rewrite_pipeline_json(src: Path, dst: Path, snapshot: Path, ss_dec: Path, dinov3_model: Path) -> None:
    data = json.loads(src.read_text())
    models = data["args"]["models"]
    for key, value in list(models.items()):
        if key == "sparse_structure_decoder":
            models[key] = str(ss_dec / "ckpts/ss_dec_conv3d_16l8_fp16")
        elif isinstance(value, str) and value.startswith("ckpts/"):
            models[key] = str(snapshot / value)
    data["args"]["image_cond_model"] = {
        "name": "DinoV3FeatureExtractor",
        "args": {"model_name": str(dinov3_model)},
    }
    data["args"]["rembg_model"] = {"name": "NoOpRembg", "args": {}}
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(data, indent=2))


def merge_sparse_tensors(template, feats, coords):
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


def copy_shift_upper_z(st, frac_x: float = 0.30, frac_z: float = 0.22):
    import torch

    coords = st.coords
    xyz = coords[:, 1:]
    z_mid = int(torch.median(xyz[:, 2]).item())
    subset = xyz[:, 2] >= z_mid
    copied_coords = coords[subset].clone()
    copied_feats = st.feats[subset].clone()
    extent = (xyz.max(0).values - xyz.min(0).values).clamp_min(1)
    shift = copied_coords.new_tensor(
        [0, max(1, int(extent[0].item() * frac_x)), 0, max(1, int(extent[2].item() * frac_z))]
    )
    copied_coords = copied_coords + shift
    lo = xyz.min(0).values
    hi = xyz.max(0).values
    valid = ((copied_coords[:, 1:] >= lo) & (copied_coords[:, 1:] <= hi)).all(dim=1)
    feats = torch.cat([st.feats, copied_feats[valid]], dim=0)
    merged_coords = torch.cat([coords, copied_coords[valid]], dim=0)
    return merge_sparse_tensors(st, feats, merged_coords)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--dinov3-model", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260510)
    parser.add_argument("--preprocess", action="store_true")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

    import torch
    from trellis2.pipelines import Trellis2ImageTo3DPipeline
    from trellis2.pipelines import rembg

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
        "sparse_structure_flow_model",
        "sparse_structure_decoder",
        "shape_slat_flow_model_512",
        "shape_slat_decoder",
        "tex_slat_flow_model_512",
        "tex_slat_decoder",
    ]

    summary = {
        "kind": "trellis2_dinov3_trivial_latent_transform_baseline",
        "image": str(args.image),
        "steps": args.steps,
        "seed": args.seed,
        "preprocess": args.preprocess,
        "transforms": {},
        "status": "started",
    }
    try:
        hf = Path(os.environ["HF_HOME"])
        t2 = next((hf / "hub/models--microsoft--TRELLIS.2-4B/snapshots").iterdir())
        ss = next((hf / "hub/models--microsoft--TRELLIS-image-large/snapshots").iterdir())
        local = args.out / "dinov3_latent_transform_pipeline"
        rewrite_pipeline_json(t2 / "pipeline.json", local / "pipeline.json", t2, ss, args.dinov3_model)

        load_start = time.time()
        pipe = Trellis2ImageTo3DPipeline.from_pretrained(str(local))
        pipe.cuda()
        summary["load_seconds"] = time.time() - load_start

        image = Image.open(args.image)
        if not args.preprocess:
            image = image.convert("RGB")
        sampler = {"steps": args.steps}
        run_start = time.time()
        meshes, latents = pipe.run(
            image,
            seed=args.seed,
            pipeline_type="512",
            sparse_structure_sampler_params=sampler,
            shape_slat_sampler_params=sampler,
            tex_slat_sampler_params=sampler,
            preprocess_image=args.preprocess,
            return_latent=True,
        )
        summary["sample_seconds"] = time.time() - run_start
        shape_slat, tex_slat, resolution = latents
        summary["resolution"] = int(resolution)
        summary["base_shape_tokens"] = int(shape_slat.coords.shape[0])
        summary["base_tex_tokens"] = int(tex_slat.coords.shape[0])

        variants = {
            "identity": (shape_slat, tex_slat),
            "mirror_x": (mirror_x(shape_slat), mirror_x(tex_slat)),
            "copy_shift_upper_z": (copy_shift_upper_z(shape_slat), copy_shift_upper_z(tex_slat)),
        }
        for name, (shape_variant, tex_variant) in variants.items():
            variant_dir = args.out / name
            variant_dir.mkdir(parents=True, exist_ok=True)
            decode_start = time.time()
            decoded = pipe.decode_latent(shape_variant, tex_variant, int(resolution))[0]
            vertices = as_numpy(decoded.vertices)
            faces = as_numpy(decoded.faces).astype(np.int64)
            write_obj(variant_dir / "mesh.obj", vertices, faces)
            render_preview(variant_dir / "preview.png", vertices, name)
            summary["transforms"][name] = {
                "decode_seconds": time.time() - decode_start,
                "shape_tokens": int(shape_variant.coords.shape[0]),
                "tex_tokens": int(tex_variant.coords.shape[0]),
                "vertices": int(len(vertices)),
                "faces": int(len(faces)),
                "bbox_min": vertices.min(0).tolist() if len(vertices) else [0, 0, 0],
                "bbox_max": vertices.max(0).tolist() if len(vertices) else [0, 0, 0],
                "obj": str(variant_dir / "mesh.obj"),
                "preview": str(variant_dir / "preview.png"),
            }
        summary["cuda_memory_allocated"] = int(torch.cuda.memory_allocated())
        summary["cuda_memory_reserved"] = int(torch.cuda.memory_reserved())
        summary["status"] = "ok"
    except Exception as exc:
        summary["status"] = "failed"
        summary["error"] = repr(exc)
        summary["traceback_tail"] = traceback.format_exc().splitlines()[-80:]
    finally:
        (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
