import argparse
import json
import os
import time
import traceback
from pathlib import Path

import numpy as np

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

    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, projection="3d")
    if len(vertices):
        step = max(1, len(vertices) // 15000)
        pts = vertices[::step]
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=0.4, c=pts[:, 2], cmap="viridis")
        center = (vertices.min(0) + vertices.max(0)) / 2
        span = max(float((vertices.max(0) - vertices.min(0)).max()), 1e-3)
        ax.set_xlim(center[0] - span / 2, center[0] + span / 2)
        ax.set_ylim(center[1] - span / 2, center[1] + span / 2)
        ax.set_zlim(center[2] - span / 2, center[2] + span / 2)
    ax.set_title(title)
    ax.set_axis_off()
    ax.view_init(22, -45)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
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
        "name": "ZeroFeatureExtractor",
        "args": {"tokens": 1024, "channels": 1024},
    }
    data["args"]["rembg_model"] = {"name": "NoOpRembg", "args": {}}
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text(json.dumps(data, indent=2))


def build_pipeline(output_dir):
    import torch
    from trellis2.modules import image_feature_extractor
    from trellis2.pipelines import Trellis2ImageTo3DPipeline
    from trellis2.pipelines import rembg

    class ZeroFeatureExtractor:
        def __init__(self, tokens=1024, channels=1024):
            self.tokens = tokens
            self.channels = channels
            self.image_size = 512

        def to(self, device):
            return self

        def cuda(self):
            return self

        def cpu(self):
            return self

        def __call__(self, image):
            batch = len(image) if isinstance(image, list) else int(image.shape[0])
            return torch.zeros((batch, self.tokens, self.channels), device="cuda", dtype=torch.bfloat16)

    class NoOpRembg:
        def to(self, device):
            return self

        def cuda(self):
            return self

        def cpu(self):
            return self

        def __call__(self, image):
            return image

    image_feature_extractor.ZeroFeatureExtractor = ZeroFeatureExtractor
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
    local = output_dir / "zero_cond_pipeline"
    rewrite_pipeline_json(t2 / "pipeline.json", local / "pipeline.json", t2, ss)
    start = time.time()
    pipe = Trellis2ImageTo3DPipeline.from_pretrained(str(local))
    pipe.cuda()
    return pipe, time.time() - start


def run_seed(pipe, output_dir, seed, steps):
    import torch
    from PIL import Image

    seed_dir = output_dir / f"seed_{seed}"
    seed_dir.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (512, 512), "white")
    sampler = {"steps": steps}
    start = time.time()
    meshes, latents = pipe.run(
        image,
        seed=seed,
        pipeline_type="512",
        sparse_structure_sampler_params=sampler,
        shape_slat_sampler_params=sampler,
        tex_slat_sampler_params=sampler,
        preprocess_image=False,
        return_latent=True,
    )
    run_seconds = time.time() - start
    mesh = meshes[0]
    shape_slat, tex_slat, resolution = latents
    vertices = as_numpy(mesh.vertices)
    faces = as_numpy(mesh.faces).astype(np.int64)
    write_obj(seed_dir / "trellis2_zero_cond.obj", vertices, faces)
    render_preview(seed_dir / "trellis2_zero_cond_preview.png", vertices, f"zero-cond seed {seed}")
    return {
        "seed": seed,
        "status": "ok",
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed-start", type=int, default=120)
    parser.add_argument("--seed-count", type=int, default=10)
    parser.add_argument("--steps", type=int, default=2)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

    pipe, load_seconds = build_pipeline(args.out)
    results = []
    for seed in range(args.seed_start, args.seed_start + args.seed_count):
        try:
            results.append(run_seed(pipe, args.out, seed, args.steps))
        except Exception as exc:
            results.append(
                {
                    "seed": seed,
                    "status": "failed",
                    "error": repr(exc),
                    "traceback_tail": traceback.format_exc().splitlines()[-12:],
                }
            )
    ok = [r for r in results if r["status"] == "ok"]
    summary = {
        "kind": "zero_condition_seed_sweep_not_prompt_fidelity",
        "steps": args.steps,
        "seed_start": args.seed_start,
        "seed_count": args.seed_count,
        "load_seconds": load_seconds,
        "ok_count": len(ok),
        "failed_count": len(results) - len(ok),
        "results": results,
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
