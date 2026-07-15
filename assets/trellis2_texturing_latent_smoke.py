import argparse
import json
import os
import sys
import time
import traceback
import types
from pathlib import Path

import numpy as np
from PIL import Image

from triton_beegfs_cache_patch import apply_triton_beegfs_cache_patch

apply_triton_beegfs_cache_patch()


def install_import_stubs():
    if "nvdiffrast" not in sys.modules:
        nvd = types.ModuleType("nvdiffrast")
        torch_mod = types.ModuleType("nvdiffrast.torch")
        nvd.torch = torch_mod
        sys.modules["nvdiffrast"] = nvd
        sys.modules["nvdiffrast.torch"] = torch_mod


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
    parser.add_argument("--preprocess", action="store_true")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

    install_import_stubs()
    import torch
    import trimesh
    from trellis2.pipelines.trellis2_texturing import Trellis2TexturingPipeline
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
        "kind": "trellis2_mesh_texturing_latent_smoke_no_nvdiffrast_postprocess",
        "mesh": str(args.mesh),
        "image": str(args.image),
        "steps": args.steps,
        "seed": args.seed,
        "resolution": args.resolution,
        "preprocess": args.preprocess,
    }
    try:
        load_start = time.time()
        pipe = Trellis2TexturingPipeline.from_pretrained(str(local))
        pipe.cuda()
        summary["load_seconds"] = time.time() - load_start

        mesh = trimesh.load(str(args.mesh), force="mesh", process=False)
        image = Image.open(args.image)
        if args.preprocess:
            image = pipe.preprocess_image(image)
        else:
            image = image.convert("RGB")
        mesh = pipe.preprocess_mesh(mesh)

        torch.manual_seed(args.seed)
        run_start = time.time()
        cond = pipe.get_cond([image], args.resolution)
        shape_slat = pipe.encode_shape_slat(mesh, args.resolution)
        tex_model = pipe.models["tex_slat_flow_model_512"]
        tex_slat = pipe.sample_tex_slat(cond, tex_model, shape_slat, {"steps": args.steps})
        pbr_voxel = pipe.decode_tex_slat(tex_slat)
        summary["run_seconds"] = time.time() - run_start
        summary["mesh_vertices"] = int(len(mesh.vertices))
        summary["mesh_faces"] = int(len(mesh.faces))
        summary["shape_slat_tokens"] = int(shape_slat.coords.shape[0])
        summary["shape_slat_channels"] = int(shape_slat.feats.shape[1])
        summary["tex_slat_tokens"] = int(tex_slat.coords.shape[0])
        summary["tex_slat_channels"] = int(tex_slat.feats.shape[1])
        summary["pbr_voxel_tokens"] = int(pbr_voxel.coords.shape[0])
        summary["pbr_voxel_channels"] = int(pbr_voxel.feats.shape[1])
        summary["pbr_min"] = float(pbr_voxel.feats.min().detach().cpu())
        summary["pbr_max"] = float(pbr_voxel.feats.max().detach().cpu())
        summary["pbr_mean"] = float(pbr_voxel.feats.mean().detach().cpu())
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
