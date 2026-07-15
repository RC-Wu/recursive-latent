#!/usr/bin/env python3
"""Compose a paper-style mesh-rendered projection ablation sheet."""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
RENDER_DIR = ROOT / "visuals/projection_ablation_blender_mesh_20260509/renders"
METRICS = ROOT / "results/projection_ablation_blender_mesh_metrics_20260509/mesh_quality_metrics.csv"
OUT = ROOT / "paper_siga/figures/projection_ablation_mesh_contact_20260509.png"


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

BG = (250, 249, 247)
TEXT = (32, 34, 36)
MUTED = (88, 92, 96)
LINE = (214, 211, 205)
GREEN = (31, 124, 85)
BROWN = (144, 94, 45)
RED = (144, 61, 55)
CARD = (255, 255, 253)


def read_metrics() -> dict[str, dict[str, str]]:
    with METRICS.open(newline="", encoding="utf-8") as f:
        return {row["label"]: row for row in csv.DictReader(f)}


def fit_image(path: Path, box: tuple[int, int]) -> Image.Image:
    if not path.exists():
        im = Image.new("RGB", box, (230, 228, 222))
        d = ImageDraw.Draw(im)
        d.text((18, box[1] // 2), "missing", font=BODY, fill=RED)
        return im
    im = Image.open(path).convert("RGB")
    bw, bh = box
    scale = max(bw / im.width, bh / im.height)
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.Resampling.LANCZOS)
    left = (im.width - bw) // 2
    top = (im.height - bh) // 2
    return im.crop((left, top, left + bw, top + bh))


def metric_text(row: dict[str, str]) -> tuple[str, tuple[int, int, int]]:
    comp = int(float(row["component_count"]))
    lcr = float(row["largest_component_vertex_ratio"])
    return f"raw mesh comps {comp}; LCR {lcr:.3f}", GREEN if comp <= 2 else (BROWN if comp < 10 else RED)


def main() -> None:
    metrics = read_metrics()
    rows = [
        ("vine", ["vine_direct", "vine_final_only", "vine_per_depth"]),
        ("tree", ["tree_direct", "tree_final_only", "tree_per_depth"]),
    ]
    labels = {
        "vine_direct": "direct recursion",
        "vine_final_only": "final-only projection",
        "vine_per_depth": "per-depth projection",
        "tree_direct": "direct recursion",
        "tree_final_only": "final-only projection",
        "tree_per_depth": "per-depth projection",
    }
    notes = {
        "direct recursion": "fragments are allowed to accumulate before cleanup",
        "final-only projection": "cleanup once after all recursive steps",
        "per-depth projection": "project every generated state before next handles are selected",
    }
    w, h = 2050, 1540
    im = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(im)
    draw.text((58, 40), "Projection-stabilized recursion: mesh evidence", font=TITLE, fill=TEXT)
    draw.text(
        (58, 95),
        "Same root family, operator, depth, renderer, and camera. These are Blender mesh renders, not point-cloud previews.",
        font=BODY,
        fill=MUTED,
    )

    x0, y0 = 58, 150
    col_w, row_h = 620, 610
    gap = 22
    image_box = (560, 350)
    for row_idx, (family, keys) in enumerate(rows):
        y = y0 + row_idx * (row_h + 44)
        draw.text((x0, y + 6), family, font=H2, fill=TEXT)
        for col_idx, key in enumerate(keys):
            x = x0 + 110 + col_idx * (col_w + gap)
            draw.rounded_rectangle((x, y, x + col_w, y + row_h), radius=8, fill=CARD, outline=LINE, width=1)
            title = labels[key]
            draw.text((x + 24, y + 20), title, font=H2, fill=TEXT)
            line, color = metric_text(metrics[key])
            draw.text((x + 24, y + 57), line, font=BODY, fill=color)
            draw.text((x + 24, y + 88), notes[title], font=SMALL, fill=MUTED)
            img = fit_image(RENDER_DIR / f"{key}_iso.png", image_box)
            im.paste(img, (x + 30, y + 128))
            draw.text((x + 36, y + 132), "iso", font=TINY, fill=(238, 237, 232))
            front = fit_image(RENDER_DIR / f"{key}_front.png", (260, 145))
            im.paste(front, (x + col_w - 292, y + row_h - 172))
            draw.rectangle((x + col_w - 292, y + row_h - 172, x + col_w - 32, y + row_h - 27), outline=LINE, width=1)
            draw.text((x + col_w - 286, y + row_h - 168), "front", font=TINY, fill=(238, 237, 232))

    draw.line((58, h - 84, w - 58, h - 84), fill=LINE, width=1)
    draw.text(
        (58, h - 60),
        "Reading: the main claim is finite-depth recursive support stabilization. It is not a claim that exported GLB/material islands are clean raw topology.",
        font=SMALL,
        fill=MUTED,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT)
    im.save(OUT.with_suffix(".pdf"), "PDF", resolution=300.0)
    print(OUT)


if __name__ == "__main__":
    main()
