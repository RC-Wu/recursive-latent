#!/usr/bin/env python3
"""Compose the coral density parameter-control textured mesh figure."""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
RENDER_DIR = ROOT / "visuals/coral_density_param_texture_20260509/renders"
METRICS = ROOT / "results/coral_density_param_texture_metrics_20260509/metrics.csv"
OUT = ROOT / "paper_siga/figures/coral_density_param_showcase_20260509.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def load_metrics() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    with METRICS.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            label = row["label"]
            for token in ["0p45", "0p70", "0p95", "1p20"]:
                if f"density_{token}" in label:
                    rows[token] = row
    return rows


def fit_image(path: Path, size: tuple[int, int]) -> Image.Image:
    img = Image.open(path).convert("RGB")
    img.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (57, 57, 56))
    x = (size[0] - img.width) // 2
    y = (size[1] - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def rounded_rect(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def main() -> None:
    metrics = load_metrics()
    tokens = [("0p45", "lambda = 0.45"), ("0p70", "lambda = 0.70"), ("0p95", "lambda = 0.95"), ("1p20", "lambda = 1.20")]
    W, H = 2200, 980
    bg = (246, 245, 242)
    canvas = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(canvas)
    title_f = font(54, bold=True)
    sub_f = font(24)
    head_f = font(30, bold=True)
    small_f = font(20)
    tiny_f = font(17)

    draw.text((70, 50), "Same-condition parameter control", fill=(35, 36, 38), font=title_f)
    draw.text(
        (70, 116),
        "Fixed connected coral grammar family, fixed stage, fixed octopus material guide; only density/compactness parameter changes.",
        fill=(82, 86, 91),
        font=sub_f,
    )
    draw.line((70, 164, W - 70, 164), fill=(205, 201, 193), width=2)

    margin_x, gap = 70, 28
    card_w = (W - 2 * margin_x - 3 * gap) // 4
    card_h = 690
    card_y = 205
    iso_size = (card_w - 52, 430)
    front_size = (210, 160)

    for idx, (token, label) in enumerate(tokens):
        x = margin_x + idx * (card_w + gap)
        rounded_rect(draw, (x, card_y, x + card_w, card_y + card_h), 12, (255, 255, 254), (216, 213, 207), 1)
        draw.text((x + 26, card_y + 22), label, fill=(31, 32, 34), font=head_f)
        iso = fit_image(RENDER_DIR / f"density_{token}_iso.png", iso_size)
        canvas.paste(iso, (x + 26, card_y + 78))
        # Front-view inset.
        inset_x = x + card_w - front_size[0] - 28
        inset_y = card_y + 78 + iso_size[1] - front_size[1] + 12
        rounded_rect(draw, (inset_x - 8, inset_y - 28, inset_x + front_size[0] + 8, inset_y + front_size[1] + 8), 6, (252, 252, 251), (214, 211, 205), 1)
        draw.text((inset_x, inset_y - 25), "front", fill=(89, 92, 96), font=tiny_f)
        front = fit_image(RENDER_DIR / f"density_{token}_front.png", front_size)
        canvas.paste(front, (inset_x, inset_y))

        row = metrics[token]
        vox = int(float(row["occupied_voxels"]))
        comps = int(float(row["primary_component_count"]))
        lcr = float(row["primary_largest_component_ratio"])
        dim = float(row["box_count_dimension_proxy"])
        yy = card_y + 545
        draw.text((x + 26, yy), f"occ. comps {comps}  LCR {lcr:.3f}", fill=(82, 86, 91), font=small_f)
        draw.text((x + 26, yy + 34), f"occupied voxels {vox:,}", fill=(82, 86, 91), font=small_f)
        draw.text((x + 26, yy + 68), f"box-count proxy {dim:.2f}", fill=(82, 86, 91), font=small_f)

        # Parameter marker strip.
        strip_y = card_y + card_h - 42
        x0 = x + 35
        x1 = x + card_w - 35
        draw.line((x0, strip_y, x1, strip_y), fill=(198, 198, 193), width=4)
        for j in range(4):
            xx = x0 + (x1 - x0) * j / 3
            color = (185, 78, 51) if j <= idx else (190, 194, 190)
            draw.ellipse((xx - 7, strip_y - 7, xx + 7, strip_y + 7), fill=color)

    draw.text(
        (70, H - 70),
        "Method-control figure: all panels are Trellis2 textured GLB renders from mesh inputs; raw GLB face components are diagnostic only, occupancy connectivity is the primary proxy.",
        fill=(96, 98, 100),
        font=small_f,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
