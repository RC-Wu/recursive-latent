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


def rewrite_pipeline_json(src, dst, snapshot, ss_dec):
    data = json.loads(Path(src).read_text())
    models = data["args"]["models"]
    for key, value in list(models.items()):
        if key == "sparse_structure_decoder":
            models[key] = str(Path(ss_dec) / "ckpts/ss_dec_conv3d_16l8_fp16")
        elif isinstance(value, str) and value.startswith("ckpts/"):
            models[key] = str(Path(snapshot) / value)
    data["args"]["image_cond_model"] = {
        "name": "HandcraftedImageFeatureExtractor",
        "args": {"tokens": 1024, "channels": 1024},
    }
    data["args"]["rembg_model"] = {"name": "NoOpRembg", "args": {}}
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text(json.dumps(data, indent=2))


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


def copy_shift_upper_z(st):
    coords = st.coords
    xyz = coords[:, 1:]
    z_mid = torch_median_int(xyz[:, 2])
    subset = xyz[:, 2] >= z_mid
    copied_coords = coords[subset].clone()
    copied_feats = st.feats[subset].clone()
    extent = (xyz.max(0).values - xyz.min(0).values).clamp_min(1)
    shift = copied_coords.new_tensor([0, max(1, int(extent[0].item() * 0.25)), 0, max(1, int(extent[2].item() * 0.20))])
    copied_coords = copied_coords + shift
    limit = int(xyz.max().item())
    valid = ((copied_coords[:, 1:] >= 0) & (copied_coords[:, 1:] <= limit)).all(dim=1)
    feats = torch_cat([st.feats, copied_feats[valid]], dim=0)
    merged_coords = torch_cat([coords, copied_coords[valid]], dim=0)
    return merge_sparse_tensors(st, feats, merged_coords)


def torch_cat(items, dim=0):
    import torch

    return torch.cat(items, dim=dim)


def torch_median_int(x):
    import torch

    return int(torch.median(x).item())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--seed", type=int, default=300)
    parser.add_argument("--scale", type=float, default=1.0)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

    import torch
    import torch.nn.functional as F
    from trellis2.modules import image_feature_extractor
    from trellis2.pipelines import Trellis2ImageTo3DPipeline
    from trellis2.pipelines import rembg

    class HandcraftedImageFeatureExtractor:
        def __init__(self, tokens=1024, channels=1024):
            self.tokens = tokens
            self.channels = channels
            self.image_size = 512
            generator = torch.Generator(device="cpu").manual_seed(20260507)
            self.proj = torch.randn(8, channels, generator=generator) / np.sqrt(8)

        def to(self, device):
            self.proj = self.proj.to(device)
            return self

        def cuda(self):
            return self.to("cuda")

        def cpu(self):
            self.proj = self.proj.cpu()
            return self

        def __call__(self, image):
            if isinstance(image, list):
                tensors = []
                for item in image:
                    arr = np.asarray(item.resize((self.image_size, self.image_size)).convert("RGB"), dtype=np.float32) / 255.0
                    tensors.append(torch.from_numpy(arr).permute(2, 0, 1))
                x = torch.stack(tensors).cuda()
            else:
                x = image.cuda()
            gray = x.mean(dim=1, keepdim=True)
            gx = F.pad(gray[:, :, :, 1:] - gray[:, :, :, :-1], (0, 1, 0, 0))
            gy = F.pad(gray[:, :, 1:, :] - gray[:, :, :-1, :], (0, 0, 0, 1))
            pooled_rgb = F.adaptive_avg_pool2d(x, (32, 32))
            pooled_gray = F.adaptive_avg_pool2d(gray, (32, 32))
            pooled_edge = F.adaptive_avg_pool2d((gx.abs() + gy.abs()), (32, 32))
            yy, xx = torch.meshgrid(
                torch.linspace(-1, 1, 32, device=x.device),
                torch.linspace(-1, 1, 32, device=x.device),
                indexing="ij",
            )
            coords = torch.stack([xx, yy, xx * yy], dim=0).expand(x.shape[0], -1, -1, -1)
            base = torch.cat([pooled_rgb, pooled_gray, pooled_edge, coords], dim=1)
            base = base.flatten(2).transpose(1, 2)
            features = base @ self.proj.to(device=x.device, dtype=base.dtype)
            return (features * args.scale).to(torch.bfloat16)

    class NoOpRembg:
        def to(self, device):
            return self

        def cuda(self):
            return self

        def cpu(self):
            return self

        def __call__(self, image):
            return image

    image_feature_extractor.HandcraftedImageFeatureExtractor = HandcraftedImageFeatureExtractor
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
    local = args.out / "latent_transform_pipeline"
    rewrite_pipeline_json(t2 / "pipeline.json", local / "pipeline.json", t2, ss)

    summary = {
        "kind": "trellis2_latent_coordinate_transform_probe_handcrafted_proxy",
        "image": str(args.image),
        "steps": args.steps,
        "seed": args.seed,
        "scale": args.scale,
        "transforms": {},
    }
    try:
        load_start = time.time()
        pipe = Trellis2ImageTo3DPipeline.from_pretrained(str(local))
        pipe.cuda()
        summary["load_seconds"] = time.time() - load_start

        image = Image.open(args.image).convert("RGB")
        sampler = {"steps": args.steps}
        run_start = time.time()
        meshes, latents = pipe.run(
            image,
            seed=args.seed,
            pipeline_type="512",
            sparse_structure_sampler_params=sampler,
            shape_slat_sampler_params=sampler,
            tex_slat_sampler_params=sampler,
            preprocess_image=False,
            return_latent=True,
        )
        summary["sample_and_decode_seconds"] = time.time() - run_start
        shape_slat, tex_slat, resolution = latents

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
            }
    except Exception as exc:
        summary["status"] = "failed"
        summary["error"] = repr(exc)
        summary["traceback_tail"] = traceback.format_exc().splitlines()[-80:]
    finally:
        (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
