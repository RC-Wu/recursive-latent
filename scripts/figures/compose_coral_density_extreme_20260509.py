#!/usr/bin/env python3
"""Compose the extreme coral density textured-mesh control figure."""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
RENDER_DIR = ROOT / "visuals/coral_density_extreme_texture_20260509/renders"
METRICS = ROOT / "results/coral_density_extreme_texture_metrics_20260509/metrics.csv"
OUT = ROOT / "paper_siga/figures/coral_density_extreme_texture_20260509.png"


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
    ]
    for item in candidates:
        try:
            return ImageFont.truetype(item, size)
        except Exception:
            continue
    return ImageFont.load_default()


TITLE = font(42, True)
H2 = font(26, True)
BODY = font(20)
SMALL = font(16)
TINY = font(13)

BG = (248, 247, 244)
TEXT = (31, 34, 36)
MUTED = (86, 91, 96)
LINE = (210, 206, 198)
GREEN = (32, 120, 85)
BLUE = (49, 88, 125)
CARD = (255, 255, 253)


def read_metrics() -> dict[str, dict[str, str]]:
    with METRICS.open(newline="", encoding="utf-8") as f:
        return {row["label"]: row for row in csv.DictReader(f)}


def fit_image(path: Path, box: tuple[int, int]) -> Image.Image:
    if not path.exists():
        im = Image.new("RGB", box, (230, 228, 222))
        d = ImageDraw.Draw(im)
        d.text((18, box[1] // 2), "missing", font=BODY, fill=(145, 55, 55))
        return im
    im = Image.open(path).convert("RGB")
    bw, bh = box
    scale = max(bw / im.width, bh / im.height)
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.Resampling.LANCZOS)
    left = (im.width - bw) // 2
    top = (im.height - bh) // 2
    return im.crop((left, top, left + bw, top + bh))


def main() -> None:
    metrics = read_metrics()
    cases = [
        ("density_0p25", "lambda=0.25", "open, lower handle expansion"),
        ("density_0p45", "lambda=0.45", "low-mid density"),
        ("density_1p35", "lambda=1.35", "high density"),
        ("density_1p75", "lambda=1.75", "dense compact branching"),
    ]
    w, h = 2150, 1120
    im = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(im)
    draw.text((64, 42), "Same-condition density control: textured mesh endpoints", font=TITLE, fill=TEXT)
    draw.text(
        (64, 98),
        "Fixed coral family, stage, octopus-sucker guide, Trellis2 schedule, renderer, and camera. Only the grammar density parameter changes.",
        font=BODY,
        fill=MUTED,
    )
    card_w, card_h = 486, 840
    x0, y0, gap = 64, 165, 26
    for idx, (key, title, note) in enumerate(cases):
        x = x0 + idx * (card_w + gap)
        row = metrics[key]
        vox = int(float(row["occupied_voxels"]))
        occ_lcr = float(row["largest_occupancy_component_ratio_6n"])
        box_dim = float(row["box_count_dimension_proxy"])
        faces = int(float(row["faces"]))
        draw.rounded_rectangle((x, y0, x + card_w, y0 + card_h), radius=8, fill=CARD, outline=LINE, width=1)
        draw.rectangle((x, y0, x + 8, y0 + card_h), fill=BLUE if idx < 2 else GREEN)
        draw.text((x + 25, y0 + 24), title, font=H2, fill=TEXT)
        draw.text((x + 25, y0 + 60), note, font=SMALL, fill=MUTED)
        draw.text((x + 25, y0 + 91), f"occ comp 1 / LCR {occ_lcr:.3f}", font=BODY, fill=GREEN)
        draw.text((x + 25, y0 + 120), f"voxels {vox:,}; faces {faces:,}; D_box {box_dim:.2f}", font=SMALL, fill=MUTED)
        iso = fit_image(RENDER_DIR / f"{key}_iso.png", (430, 410))
        front = fit_image(RENDER_DIR / f"{key}_front.png", (430, 250))
        im.paste(iso, (x + 28, y0 + 170))
        draw.text((x + 34, y0 + 174), "iso", font=TINY, fill=(238, 237, 232))
        im.paste(front, (x + 28, y0 + 605))
        draw.text((x + 34, y0 + 609), "front", font=TINY, fill=(238, 237, 232))

    draw.line((64, h - 86, w - 64, h - 86), fill=LINE, width=1)
    draw.text(
        (64, h - 62),
        "This is a controllability/method-behavior panel, not an ablation. Raw GLB face components remain a material/UV diagnostic, not the primary support metric.",
        font=SMALL,
        fill=MUTED,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT)
    im.save(OUT.with_suffix(".pdf"), "PDF", resolution=300.0)
    print(OUT)


if __name__ == "__main__":
    main()
