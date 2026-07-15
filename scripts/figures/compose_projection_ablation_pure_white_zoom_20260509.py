#!/usr/bin/env python3
"""Compose a pure-white projection-ablation figure with detail zooms."""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
RENDER_DIR = ROOT / "visuals/projection_ablation_blender_mesh_20260509/renders_pure_white_flat_rerun2105"
METRICS = ROOT / "results/projection_ablation_blender_mesh_metrics_20260509/mesh_quality_metrics.csv"
FIG_DIR = ROOT / "paper_siga/figures"
OUT_PNG = FIG_DIR / "projection_ablation_pure_white_zoom_20260509.png"
OUT_PDF = FIG_DIR / "projection_ablation_pure_white_zoom_20260509.pdf"
VIS_OUT = ROOT / "visuals/projection_ablation_blender_mesh_20260509/projection_ablation_pure_white_zoom_20260509.png"


WHITE = (255, 255, 255)
INK = (25, 27, 29)
MUTED = (82, 86, 90)
FAINT = (222, 225, 222)
GOOD = (31, 112, 74)
WARN = (147, 90, 45)
BAD = (145, 54, 49)


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


TITLE = font(50, True)
SUB = font(24)
HEAD = font(30, True)
BODY = font(22)
SMALL = font(18)
TINY = font(15)


def read_metrics() -> dict[str, dict[str, str]]:
    with METRICS.open(newline="", encoding="utf-8") as f:
        return {row["label"]: row for row in csv.DictReader(f)}


def object_bbox(im: Image.Image, threshold: int = 248) -> tuple[int, int, int, int]:
    rgb = im.convert("RGB")
    pix = rgb.load()
    xs: list[int] = []
    ys: list[int] = []
    step = 2
    for y in range(0, rgb.height, step):
        for x in range(0, rgb.width, step):
            r, g, b = pix[x, y]
            if min(r, g, b) < threshold:
                xs.append(x)
                ys.append(y)
    if not xs:
        return (0, 0, rgb.width, rgb.height)
    pad = 30
    return (
        max(0, min(xs) - pad),
        max(0, min(ys) - pad),
        min(rgb.width, max(xs) + pad),
        min(rgb.height, max(ys) + pad),
    )


def crop_object(im: Image.Image, pad: int = 40) -> Image.Image:
    x0, y0, x1, y1 = object_bbox(im)
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def detail_crop(im: Image.Image, slot: str) -> Image.Image:
    x0, y0, x1, y1 = object_bbox(im)
    bw = max(1, x1 - x0)
    bh = max(1, y1 - y0)
    crop_w = int(bw * 0.46)
    crop_h = int(bh * 0.46)
    if slot == "upper":
        cx = x0 + int(bw * 0.55)
        cy = y0 + int(bh * 0.22)
    elif slot == "lower":
        cx = x0 + int(bw * 0.48)
        cy = y0 + int(bh * 0.72)
    else:
        cx = x0 + int(bw * 0.52)
        cy = y0 + int(bh * 0.50)
    left = max(0, min(im.width - crop_w, cx - crop_w // 2))
    top = max(0, min(im.height - crop_h, cy - crop_h // 2))
    return im.crop((left, top, left + crop_w, top + crop_h))


def fit(im: Image.Image, box: tuple[int, int], cover: bool = False) -> Image.Image:
    bw, bh = box
    scale = max(bw / im.width, bh / im.height) if cover else min(bw / im.width, bh / im.height)
    size = (max(1, int(im.width * scale)), max(1, int(im.height * scale)))
    im = im.resize(size, Image.Resampling.LANCZOS)
    if cover:
        left = max(0, (im.width - bw) // 2)
        top = max(0, (im.height - bh) // 2)
        im = im.crop((left, top, left + bw, top + bh))
    out = Image.new("RGB", (bw, bh), WHITE)
    out.paste(im, ((bw - im.width) // 2, (bh - im.height) // 2))
    return out


def metric_line(row: dict[str, str]) -> tuple[str, tuple[int, int, int]]:
    comp = int(float(row["component_count"]))
    lcr = float(row["largest_component_vertex_ratio"])
    color = GOOD if comp <= 2 else (WARN if comp <= 8 else BAD)
    return f"components {comp}   LCR {lcr:.3f}", color


def draw_cell(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    metrics: dict[str, dict[str, str]],
    key: str,
    title: str,
    x: int,
    y: int,
    w: int,
    h: int,
    crop_slot: str,
) -> None:
    src = Image.open(RENDER_DIR / f"{key}_iso.png").convert("RGB")
    full = fit(crop_object(src), (w, h - 108), cover=False)
    canvas.paste(full, (x, y + 82))
    draw.text((x, y), title, font=HEAD, fill=INK)
    line, color = metric_line(metrics[key])
    draw.text((x, y + 38), line, font=BODY, fill=color)

    z_w, z_h = 210, 170
    zoom = fit(detail_crop(src, crop_slot), (z_w, z_h), cover=True)
    zx = x + w - z_w - 18
    zy = y + h - z_h - 18
    draw.rectangle((zx - 1, zy - 1, zx + z_w + 1, zy + z_h + 1), outline=FAINT, width=2)
    canvas.paste(zoom, (zx, zy))
    draw.text((zx + 8, zy + 8), "local zoom", font=TINY, fill=MUTED)


def main() -> None:
    metrics = read_metrics()
    width, height = 2500, 1860
    canvas = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    draw.text((70, 46), "Per-depth projection suppresses recursive fragmentation", font=TITLE, fill=INK)
    draw.text(
        (70, 108),
        "Pure-white Blender mesh renders under matched root family, grammar operator, depth, material mode, and camera; insets show local detail.",
        font=SUB,
        fill=MUTED,
    )
    draw.line((70, 154, width - 70, 154), fill=FAINT, width=2)

    col_w = 720
    row_h = 640
    x0 = 120
    y0 = 210
    gap_x = 70
    gap_y = 130
    titles = [
        ("direct recursion", "direct", "upper"),
        ("final-only projection", "final_only", "center"),
        ("per-depth projection", "per_depth", "lower"),
    ]
    for row_idx, family in enumerate(["vine", "tree"]):
        y = y0 + row_idx * (row_h + gap_y)
        draw.text((70, y + 250), family, font=HEAD, fill=INK)
        draw.line((92, y + 292, 92, y + 470), fill=FAINT, width=2)
        for col_idx, (label, suffix, slot) in enumerate(titles):
            x = x0 + col_idx * (col_w + gap_x)
            key = f"{family}_{suffix}"
            draw_cell(canvas, draw, metrics, key, label, x, y, col_w, row_h, slot)

    draw.line((70, height - 88, width - 70, height - 88), fill=FAINT, width=2)
    draw.text(
        (70, height - 58),
        "Primary reading: direct states permit orphan chunks to become future handles; per-depth projection keeps the recursive support in the admissible connected set before the next expansion.",
        font=SMALL,
        fill=MUTED,
    )
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT_PNG, "PNG", optimize=True)
    canvas.save(OUT_PDF, "PDF", resolution=300.0)
    canvas.save(VIS_OUT, "PNG", optimize=True)
    print(OUT_PNG)
    print(OUT_PDF)
    print(VIS_OUT)


if __name__ == "__main__":
    main()
