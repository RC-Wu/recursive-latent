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


def write_obj(path, vertices, faces):
    with open(path, "w") as f:
        for v in vertices:
            f.write(f"v {float(v[0]):.6f} {float(v[1]):.6f} {float(v[2]):.6f}\n")
        for face in faces:
            f.write(f"f {int(face[0]) + 1} {int(face[1]) + 1} {int(face[2]) + 1}\n")


def render_preview(path, vertices, title):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

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


def rewrite_pipeline_json(src, dst, snapshot, ss_dec):
    data = json.loads(Path(src).read_text())
    models = data["args"]["models"]
    for key, value in list(models.items()):
        if key == "sparse_structure_decoder":
            models[key] = str(Path(ss_dec) / "ckpts/ss_dec_conv3d_16l8_fp16")
        elif isinstance(value, str) and value.startswith("ckpts/"):
            models[key] = str(Path(snapshot) / value)
    data["args"]["image_cond_model"] = {
        "name": "DinoV3FeatureExtractor",
        "args": {"model_name": "facebook/dinov3-vitl16-pretrain-lvd1689m"},
    }
    data["args"]["rembg_model"] = {"name": "NoOpRembg", "args": {}}
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text(json.dumps(data, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--dinov3-model", type=Path, required=True)
    parser.add_argument("--preprocess", action="store_true")
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--seed", type=int, default=300)
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
            if getattr(image, "mode", None) != "RGBA":
                image = image.convert("RGBA")
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

    hf = Path(os.environ["HF_HOME"])
    t2 = next((hf / "hub/models--microsoft--TRELLIS.2-4B/snapshots").iterdir())
    ss = next((hf / "hub/models--microsoft--TRELLIS-image-large/snapshots").iterdir())
    local = args.out / "dinov3_min_pipeline"
    rewrite_pipeline_json(t2 / "pipeline.json", local / "pipeline.json", t2, ss)
    data = json.loads((local / "pipeline.json").read_text())
    data["args"]["image_cond_model"]["args"]["model_name"] = str(args.dinov3_model)
    (local / "pipeline.json").write_text(json.dumps(data, indent=2))

    try:
        load_start = time.time()
        pipe = Trellis2ImageTo3DPipeline.from_pretrained(str(local))
        pipe.cuda()
        load_seconds = time.time() - load_start
        image = Image.open(args.image)
        if args.preprocess:
            image = image.convert("RGBA")
        else:
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
        run_seconds = time.time() - run_start
        mesh = meshes[0]
        shape_slat, tex_slat, resolution = latents
        vertices = as_numpy(mesh.vertices)
        faces = as_numpy(mesh.faces).astype(np.int64)
        write_obj(args.out / "trellis2_dinov3_min.obj", vertices, faces)
        render_preview(args.out / "trellis2_dinov3_min_preview.png", vertices, f"DINOv3 min seed {args.seed}")
        summary = {
            "kind": "dinov3_conditioned_min_smoke_no_rembg",
            "image": str(args.image),
            "steps": args.steps,
            "seed": args.seed,
            "preprocess": args.preprocess,
            "load_seconds": load_seconds,
            "run_seconds": run_seconds,
            "resolution": int(resolution),
            "vertices": int(len(vertices)),
            "faces": int(len(faces)),
            "bbox_min": vertices.min(0).tolist() if len(vertices) else [0, 0, 0],
            "bbox_max": vertices.max(0).tolist() if len(vertices) else [0, 0, 0],
            "shape_latent_tokens": int(shape_slat.coords.shape[0]),
            "shape_latent_channels": int(shape_slat.feats.shape[1]),
            "tex_latent_tokens": int(tex_slat.coords.shape[0]),
            "tex_latent_channels": int(tex_slat.feats.shape[1]),
            "cuda_memory_allocated": int(torch.cuda.memory_allocated()),
            "cuda_memory_reserved": int(torch.cuda.memory_reserved()),
        }
    except Exception as exc:
        summary = {
            "kind": "dinov3_conditioned_min_smoke_no_rembg",
            "image": str(args.image),
            "steps": args.steps,
            "seed": args.seed,
            "preprocess": args.preprocess,
            "status": "failed",
            "error": repr(exc),
            "traceback_tail": traceback.format_exc().splitlines()[-50:],
        }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
