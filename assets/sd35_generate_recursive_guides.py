from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path

import torch
from PIL import Image, ImageDraw


@dataclass(frozen=True)
class GuidePrompt:
    name: str
    prompt: str
    negative: str


GUIDES = [
    GuidePrompt(
        "vine_root_asset",
        "single high quality 3D asset concept of a recursive vine root plant, twisting roots, layered leaf tendrils, rich green PBR material, studio product render, isolated object on clean light background",
        "text, watermark, logo, scene, multiple objects, blurry, low quality, flat icon",
    ),
    GuidePrompt(
        "branching_tree_asset",
        "single stylized recursive tree asset, exposed roots and branching crown, leaves with visible veins, natural bark and green foliage PBR material, studio product render, isolated object",
        "text, watermark, logo, forest scene, multiple objects, blurry, flat drawing",
    ),
    GuidePrompt(
        "crystal_radial_asset",
        "single radial recursive crystal growth asset, translucent mineral branches arranged with symmetry, sharp faceted geometry, subtle iridescent PBR material, studio render, isolated object",
        "text, watermark, logo, landscape, blurry, melted shape, low detail",
    ),
    GuidePrompt(
        "scifi_mechanical_asset",
        "single sci fi recursive mechanical module asset, nested metallic fins and repeating details, brushed metal and dark ceramic PBR material, studio product render, isolated object",
        "text, watermark, logo, vehicle, character, blurry, noisy background",
    ),
    GuidePrompt(
        "recursive_portal_asset",
        "single recursive portal ring sculpture asset, nested arches inside a circular frame, Escher inspired repeating geometry, polished stone and aged metal PBR material, studio render, isolated object",
        "text, watermark, logo, people, building scene, blurry, flat poster",
    ),
    GuidePrompt(
        "organic_octopus_asset",
        "single organic recursive sea creature asset, octopus-like tendrils with branching curl details, glossy wet green and blue PBR material, studio product render, isolated object",
        "text, watermark, logo, underwater scene, multiple animals, blurry, low quality",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="stabilityai/stable-diffusion-3.5-medium")
    parser.add_argument("--pipeline", choices=["auto", "sd3"], default="sd3")
    parser.add_argument("--dtype", choices=["float16", "bfloat16"], default="bfloat16")
    parser.add_argument("--variant", default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=7351)
    parser.add_argument("--steps", type=int, default=24)
    parser.add_argument("--guidance", type=float, default=4.5)
    parser.add_argument("--height", type=int, default=768)
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--max-guides", type=int, default=len(GUIDES))
    return parser.parse_args()


def make_contact_sheet(rows: list[dict], out_path: Path) -> None:
    thumbs = []
    for row in rows:
        image = Image.open(row["path"]).convert("RGB")
        image.thumbnail((360, 360), Image.LANCZOS)
        canvas = Image.new("RGB", (390, 430), (250, 249, 246))
        x = (390 - image.width) // 2
        y = 44 + (350 - image.height) // 2
        canvas.paste(image, (x, y))
        ImageDraw.Draw(canvas).text((16, 14), row["name"], fill=(32, 32, 32))
        thumbs.append(canvas)
    cols = 3
    rows_n = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (390 * cols, 430 * rows_n), (255, 255, 255))
    for idx, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((idx % cols) * 390, (idx // cols) * 430))
    sheet.save(out_path, quality=95)


def main() -> None:
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    # Import after env/PYTHONPATH setup so the same script works with project-local vendored diffusers.
    if args.pipeline == "sd3":
        from diffusers import StableDiffusion3Pipeline as Pipeline
    else:
        from diffusers import AutoPipelineForText2Image as Pipeline

    token = args.token_file.read_text().strip()
    if not token:
        raise RuntimeError("HF token file is empty")

    generator = torch.Generator(device="cuda").manual_seed(args.seed)
    torch_dtype = torch.float16 if args.dtype == "float16" else torch.bfloat16
    load_kwargs = {
        "torch_dtype": torch_dtype,
        "token": token,
        "cache_dir": os.environ.get("HF_HOME"),
        "use_safetensors": True,
    }
    if args.variant:
        load_kwargs["variant"] = args.variant
    pipe = Pipeline.from_pretrained(args.model, **load_kwargs)
    if hasattr(pipe, "safety_checker"):
        pipe.safety_checker = None
    pipe = pipe.to("cuda")
    if hasattr(pipe, "enable_attention_slicing"):
        pipe.enable_attention_slicing()

    rows = []
    for idx, guide in enumerate(GUIDES[: args.max_guides]):
        image = pipe(
            prompt=guide.prompt,
            negative_prompt=guide.negative,
            num_inference_steps=args.steps,
            guidance_scale=args.guidance,
            height=args.height,
            width=args.width,
            generator=generator,
        ).images[0]
        path = args.out / f"{idx:02d}_{guide.name}.png"
        image.save(path)
        rows.append(
            {
                "name": guide.name,
                "path": str(path),
                "prompt": guide.prompt,
                "negative": guide.negative,
                "model": args.model,
                "seed": args.seed,
                "steps": args.steps,
                "guidance": args.guidance,
                "height": args.height,
                "width": args.width,
            }
        )

    (args.out / "sd35_guides_manifest.json").write_text(
        json.dumps({"rows": rows}, indent=2),
        encoding="utf-8",
    )
    make_contact_sheet(rows, args.out / "sd35_guides_contact_sheet.png")


if __name__ == "__main__":
    main()
