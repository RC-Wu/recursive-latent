#!/usr/bin/env python3
"""Add gray callout boxes and compose the upright 4x4 comparison figure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WHITE = (255, 255, 255)
INK = (24, 24, 24)
CALLOUT = (124, 124, 124)


def draw_gray_box(raw_path: Path, out_path: Path, rect: tuple[int, int, int, int]) -> None:
    src = Image.open(raw_path).convert("RGBA")
    base = Image.new("RGBA", src.size, WHITE + (255,))
    base.alpha_composite(src)
    im = base.convert("RGB")
    draw = ImageDraw.Draw(im)
    width = max(3, im.width // 360)
    draw.rectangle(rect, outline=CALLOUT, width=width)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path)


def fit_square(path: Path, size: int) -> Image.Image:
    src = Image.open(path).convert("RGBA")
    base = Image.new("RGBA", src.size, WHITE + (255,))
    base.alpha_composite(src)
    image = base.convert("RGB")
    image.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (size, size), WHITE)
    canvas.paste(image, ((size - image.width) // 2, (size - image.height) // 2))
    return canvas


def times_font(size: int):
    for path in [
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
        "/Library/Fonts/Times New Roman Bold.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/Library/Fonts/Times New Roman.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def compose(rows: list[dict], out_path: Path, panel_size: int) -> None:
    label_w = int(panel_size * 0.88)
    gap = int(panel_size * 0.075)
    row_gap = int(panel_size * 0.08)
    margin = int(panel_size * 0.06)
    width = margin * 2 + label_w + gap + 4 * panel_size + 3 * gap
    height = margin * 2 + len(rows) * panel_size + (len(rows) - 1) * row_gap
    canvas = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    font = times_font(max(28, panel_size // 16))
    y = margin
    for row in rows:
        bbox = draw.textbbox((0, 0), row["row"], font=font)
        draw.text((margin, y + panel_size * 0.5 - (bbox[3] - bbox[1]) * 0.5), row["row"], fill=INK, font=font)
        panels = [
            Path(row["traditional"]["overview_gray_box"]),
            Path(row["traditional"]["zoom"]),
            Path(row["ours"]["overview_gray_box"]),
            Path(row["ours"]["zoom"]),
        ]
        x = margin + label_w + gap
        for panel in panels:
            canvas.paste(fit_square(panel, panel_size), (x, y))
            x += panel_size + gap
        y += panel_size + row_gap
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--panel-size", type=int, default=560)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    for row in manifest["rows"]:
        for side in ("traditional", "ours"):
            info = row[side]
            draw_gray_box(Path(info["overview_raw"]), Path(info["overview_gray_box"]), tuple(info["callout_rect"]))
    compose(manifest["rows"], args.out, args.panel_size)
    manifest["figure"] = str(args.out)
    args.manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(args.out)
    print(args.out.stat().st_size)


if __name__ == "__main__":
    main()
