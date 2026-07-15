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


def render_preview(path, mesh, title):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    vertices = np.asarray(mesh.vertices)
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--dinov3-model", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--seed", type=int, default=300)
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--texture-size", type=int, default=512)
    parser.add_argument("--preprocess", action="store_true")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

    import torch
    import trimesh
    from trellis2.pipelines import Trellis2TexturingPipeline
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
    Trellis2TexturingPipeline.model_names_to_load = [
        "shape_slat_encoder",
        "tex_slat_decoder",
        "tex_slat_flow_model_512",
    ]

    hf = Path(os.environ["HF_HOME"])
    t2 = next((hf / "hub/models--microsoft--TRELLIS.2-4B/snapshots").iterdir())
    local = args.out / "texturing_pipeline"
    rewrite_pipeline_json(t2 / "texturing_pipeline.json", local / "pipeline.json", t2, args.dinov3_model)

    summary = {
        "kind": "trellis2_mesh_texturing_smoke",
        "mesh": str(args.mesh),
        "image": str(args.image),
        "steps": args.steps,
        "seed": args.seed,
        "resolution": args.resolution,
        "texture_size": args.texture_size,
        "preprocess": args.preprocess,
    }
    try:
        load_start = time.time()
        pipe = Trellis2TexturingPipeline.from_pretrained(str(local))
        pipe.cuda()
        summary["load_seconds"] = time.time() - load_start

        mesh = trimesh.load(str(args.mesh), force="mesh", process=False)
        image = Image.open(args.image)
        if not args.preprocess:
            image = image.convert("RGB")
        run_start = time.time()
        out_mesh = pipe.run(
            mesh,
            image,
            seed=args.seed,
            tex_slat_sampler_params={"steps": args.steps},
            preprocess_image=args.preprocess,
            resolution=args.resolution,
            texture_size=args.texture_size,
        )
        summary["run_seconds"] = time.time() - run_start
        summary["vertices"] = int(len(out_mesh.vertices))
        summary["faces"] = int(len(out_mesh.faces))
        vertices = np.asarray(out_mesh.vertices)
        summary["bbox_min"] = vertices.min(0).tolist() if len(vertices) else [0, 0, 0]
        summary["bbox_max"] = vertices.max(0).tolist() if len(vertices) else [0, 0, 0]
        out_mesh.export(args.out / "textured_mesh.glb")
        render_preview(args.out / "textured_mesh_preview.png", out_mesh, f"texturing seed {args.seed}")
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
