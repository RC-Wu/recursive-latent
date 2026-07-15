#!/usr/bin/env python3
"""Compose white-background depth/density control figures with zoom insets."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WHITE = (255, 255, 255)
INK = (28, 30, 32)
MUTED = (92, 96, 100)


DEPTH_ROWS = [
    ("Bismuth", ["Bismuth_depth_stage_01", "Bismuth_depth_stage_02", "Bismuth_depth_stage_03", "Bismuth_depth_stage_04"]),
    ("Pyrite", ["Pyrite_depth_stage_01", "Pyrite_depth_stage_02", "Pyrite_depth_stage_03", "Pyrite_depth_stage_04"]),
    ("Coral", ["Coral_depth_stage_01", "Coral_depth_stage_02", "Coral_depth_stage_03", "Coral_depth_stage_04"]),
]

DENSITY_ROW = [
    ("0.25", "Coral_density_0p25"),
    ("0.45", "Coral_density_0p45"),
    ("1.35", "Coral_density_1p35"),
    ("1.75", "Coral_density_1p75"),
]


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def flatten(path: Path) -> Image.Image:
    src = Image.open(path).convert("RGBA")
    base = Image.new("RGBA", src.size, WHITE + (255,))
    base.alpha_composite(src)
    return base.convert("RGB")


def make_pair(root: Path, case: str, size: int) -> Image.Image:
    case_dir = root / case
    overview = case_dir / "overview_callouts.png"
    if not overview.exists():
        overview = case_dir / "overview_raw.png"
    zoom = case_dir / "zoom_01.png"
    ov = flatten(overview).resize((size, size), Image.Resampling.LANCZOS)
    zm = flatten(zoom).resize((size, size), Image.Resampling.LANCZOS)
    pair = Image.new("RGB", (size * 2, size), WHITE)
    pair.paste(ov, (0, 0))
    pair.paste(zm, (size, 0))
    return pair


def draw_center(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fnt, fill=INK) -> None:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    draw.text((x - (bbox[2] - bbox[0]) / 2, y), text, font=fnt, fill=fill)


def compose_depth(root: Path, out: Path, pair_size: int) -> None:
    gap = max(22, pair_size // 18)
    row_label_w = max(120, pair_size // 2)
    title_h = max(70, pair_size // 5)
    row_h = pair_size + max(22, pair_size // 16)
    margin = max(32, pair_size // 10)
    width = margin * 2 + row_label_w + gap + 4 * pair_size * 2 + 3 * gap
    height = margin * 2 + title_h + len(DEPTH_ROWS) * row_h + (len(DEPTH_ROWS) - 1) * gap
    canvas = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    row_font = font(max(24, pair_size // 16), bold=True)
    title_font = font(max(22, pair_size // 18), bold=True)
    small_font = font(max(17, pair_size // 24), bold=False)
    x0 = margin + row_label_w + gap
    for i in range(4):
        x = x0 + i * (pair_size * 2 + gap)
        draw_center(draw, x + pair_size, margin, f"depth {i + 1}", title_font)
        draw_center(draw, x + pair_size // 2, margin + title_h - 30, "overview", small_font, fill=MUTED)
        draw_center(draw, x + pair_size + pair_size // 2, margin + title_h - 30, "zoom", small_font, fill=MUTED)
    y = margin + title_h
    for label, cases in DEPTH_ROWS:
        draw.text((margin, y + pair_size * 0.38), label, font=row_font, fill=INK)
        for idx, case in enumerate(cases):
            pair = make_pair(root, case, pair_size)
            x = x0 + idx * (pair_size * 2 + gap)
            canvas.paste(pair, (x, y))
        y += row_h + gap
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def compose_density(root: Path, out: Path, pair_size: int) -> None:
    gap = max(24, pair_size // 14)
    margin = max(34, pair_size // 10)
    title_h = max(70, pair_size // 5)
    width = margin * 2 + 4 * pair_size * 2 + 3 * gap
    height = margin * 2 + title_h + pair_size
    canvas = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    title_font = font(max(22, pair_size // 18), bold=True)
    small_font = font(max(17, pair_size // 24), bold=False)
    x0 = margin
    for idx, (density, case) in enumerate(DENSITY_ROW):
        x = x0 + idx * (pair_size * 2 + gap)
        draw_center(draw, x + pair_size, margin, f"density {density}", title_font)
        draw_center(draw, x + pair_size // 2, margin + title_h - 30, "overview", small_font, fill=MUTED)
        draw_center(draw, x + pair_size + pair_size // 2, margin + title_h - 30, "zoom", small_font, fill=MUTED)
        canvas.paste(make_pair(root, case, pair_size), (x, margin + title_h))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--depth-out", type=Path, required=True)
    parser.add_argument("--density-out", type=Path, required=True)
    parser.add_argument("--pair-size", type=int, default=260)
    args = parser.parse_args()
    compose_depth(args.root, args.depth_out, args.pair_size)
    compose_density(args.root, args.density_out, args.pair_size)
    print(args.depth_out, args.depth_out.stat().st_size)
    print(args.density_out, args.density_out.stat().st_size)


if __name__ == "__main__":
    main()
