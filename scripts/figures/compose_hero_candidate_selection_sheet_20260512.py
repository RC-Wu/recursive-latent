#!/usr/bin/env python3
"""Compose selected hero candidate overview renders into labeled contact sheets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WHITE = (255, 255, 255, 255)
TEXT = (34, 34, 34, 255)
MUTED = (105, 105, 105, 255)
STROKE = (220, 224, 228, 255)


def font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def alpha_to_white(path: Path) -> Image.Image:
    src = Image.open(path).convert("RGBA")
    base = Image.new("RGBA", src.size, WHITE)
    base.alpha_composite(src)
    return base


def content_crop(im: Image.Image, pad_ratio: float = 0.08) -> Image.Image:
    alpha = im.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        return im
    left, top, right, bottom = bbox
    side = max(right - left, bottom - top)
    pad = int(side * pad_ratio)
    return im.crop(
        (
            max(0, left - pad),
            max(0, top - pad),
            min(im.width, right + pad),
            min(im.height, bottom + pad),
        )
    )


def contain(im: Image.Image, box: tuple[int, int]) -> Image.Image:
    scale = min(box[0] / im.width, box[1] / im.height)
    size = (max(1, int(im.width * scale)), max(1, int(im.height * scale)))
    return im.resize(size, Image.Resampling.LANCZOS)


def draw_centered(draw: ImageDraw.ImageDraw, text: str, box: tuple[int, int, int, int], fnt, fill=TEXT) -> None:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    x = box[0] + (box[2] - box[0] - (bbox[2] - bbox[0])) // 2
    y = box[1] + (box[3] - box[1] - (bbox[3] - bbox[1])) // 2
    draw.text((x, y), text, font=fnt, fill=fill)


def compose(plan: dict, out: Path, ids: list[str], columns: int, title: str) -> None:
    cases = {case["id"]: case for case in plan["cases"]}
    missing = [case_id for case_id in ids if case_id not in cases]
    if missing:
        raise SystemExit(f"Missing case ids in plan: {missing}")

    tile_w = 500
    tile_h = 590
    image_h = 455
    gap = 24
    header_h = 58 if title else 0
    rows = (len(ids) + columns - 1) // columns
    width = gap + columns * tile_w + (columns - 1) * gap + gap
    height = gap + header_h + rows * tile_h + (rows - 1) * gap + gap
    canvas = Image.new("RGBA", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    title_font = font(28)
    label_font = font(20)
    path_font = font(13)
    if title:
        draw.text((gap, gap), title, font=title_font, fill=TEXT)

    y0 = gap + header_h
    for idx, case_id in enumerate(ids):
        row = idx // columns
        col = idx % columns
        x = gap + col * (tile_w + gap)
        y = y0 + row * (tile_h + gap)
        draw.rounded_rectangle((x, y, x + tile_w, y + tile_h), radius=8, outline=STROKE, width=2, fill=WHITE)
        case = cases[case_id]
        overview = Path(case["overview"]["path"])
        im_rgba = Image.open(overview).convert("RGBA")
        im = alpha_to_white(overview)
        crop = content_crop(im_rgba)
        crop_white = Image.new("RGBA", crop.size, WHITE)
        crop_white.alpha_composite(crop)
        fitted = contain(crop_white, (tile_w - 34, image_h - 18))
        px = x + (tile_w - fitted.width) // 2
        py = y + 16 + (image_h - fitted.height) // 2
        canvas.alpha_composite(fitted, (px, py))
        label = f"{idx + 1:02d}  {case.get('label', case_id)}"
        draw_centered(draw, label, (x + 10, y + image_h + 10, x + tile_w - 10, y + image_h + 42), label_font, TEXT)
        mesh = Path(case.get("mesh", ""))
        short = mesh.parent.name[:58]
        draw_centered(draw, short, (x + 10, y + image_h + 45, x + tile_w - 10, y + image_h + 76), path_font, MUTED)

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out, quality=96)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ids", nargs="+", required=True)
    parser.add_argument("--columns", type=int, default=5)
    parser.add_argument("--title", default="")
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    compose(plan, args.out, args.ids, args.columns, args.title)
    print(args.out)


if __name__ == "__main__":
    main()
