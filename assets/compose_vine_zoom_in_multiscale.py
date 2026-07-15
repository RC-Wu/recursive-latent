#!/usr/bin/env python3
"""Compose Blender-rendered vine zoom panels into the paper figure."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_font(size: int):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", action="append", required=True, help="label=/path/to/panel.png")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--title", default="Recursive vine mesh: multi-scale Blender zoom-in")
    parser.add_argument("--width", type=int, default=3900)
    parser.add_argument("--height", type=int, default=1450)
    args = parser.parse_args()

    panels = []
    for item in args.panel:
        label, path = item.split("=", 1)
        panels.append((label, Path(path)))
    if len(panels) != 3:
        raise ValueError("Expected exactly three panels for this paper figure.")

    canvas = Image.new("RGBA", (args.width, args.height), (246, 244, 238, 255))
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(52)
    label_font = load_font(38)

    margin_x = 90
    gap = 60
    panel_size = (args.width - 2 * margin_x - 2 * gap) // 3
    panel_y = 135

    title_bbox = draw.textbbox((0, 0), args.title, font=title_font)
    title_x = args.width / 2 - (title_bbox[2] - title_bbox[0]) / 2
    draw.text((title_x, 42), args.title, font=title_font, fill=(32, 31, 28, 255))

    for idx, (label, path) in enumerate(panels):
        img = Image.open(path).convert("RGBA")
        img = img.resize((panel_size, panel_size), Image.Resampling.LANCZOS)
        x = margin_x + idx * (panel_size + gap)
        canvas.alpha_composite(img, (x, panel_y))
        draw.rectangle(
            (x, panel_y, x + panel_size, panel_y + panel_size),
            outline=(70, 70, 65, 255),
            width=3,
        )
        bbox = draw.textbbox((0, 0), label, font=label_font)
        label_x = x + panel_size / 2 - (bbox[2] - bbox[0]) / 2
        draw.text((label_x, panel_y + panel_size + 34), label, font=label_font, fill=(32, 31, 28, 255))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(args.out, quality=95)
    print(args.out)


if __name__ == "__main__":
    main()
