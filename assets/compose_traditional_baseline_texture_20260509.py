#!/usr/bin/env python3
"""Compose textured traditional-baseline comparison figure."""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
RENDER_DIR = ROOT / "visuals/traditional_baseline_texture_20260509/renders"
METRICS = ROOT / "results/traditional_baseline_texture_metrics_20260509/metrics.csv"
OUT = ROOT / "paper_siga/figures/traditional_baseline_texture_20260509.png"


def font(size: int, bold: bool = False):
    paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def load_metrics() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    with METRICS.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            label = row["label"]
            for key in ["sc_root_vine", "sc_tree_canopy", "lsystem_branch", "dla_cluster"]:
                if key in label:
                    out[key] = row
    return out


def fit(path: Path, size: tuple[int, int]) -> Image.Image:
    img = Image.open(path).convert("RGB")
    img.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (57, 57, 56))
    canvas.paste(img, ((size[0] - img.width) // 2, (size[1] - img.height) // 2))
    return canvas


def main() -> None:
    rows = load_metrics()
    cases = [
        ("sc_root_vine", "Space colonization root", "tree-root guide"),
        ("sc_tree_canopy", "Space colonization tree", "spiky-plant guide"),
        ("lsystem_branch", "L-system branch", "vine guide"),
        ("dla_cluster", "Voxel DLA cluster", "octopus guide"),
    ]
    W, H = 2200, 930
    canvas = Image.new("RGB", (W, H), (246, 245, 242))
    draw = ImageDraw.Draw(canvas)
    title_f = font(52, True)
    sub_f = font(24)
    head_f = font(28, True)
    small_f = font(19)

    draw.text((70, 48), "Traditional baselines through the same texture path", fill=(34, 35, 37), font=title_f)
    draw.text(
        (70, 112),
        "OBJ procedural baselines exported to Trellis2 textured GLB; this isolates why texture alone does not solve recursive asset structure.",
        fill=(82, 86, 91),
        font=sub_f,
    )
    draw.line((70, 160, W - 70, 160), fill=(205, 201, 193), width=2)

    card_w = (W - 140 - 3 * 28) // 4
    card_h = 650
    y = 205
    for i, (key, title, guide) in enumerate(cases):
        x = 70 + i * (card_w + 28)
        draw.rounded_rectangle((x, y, x + card_w, y + card_h), radius=12, fill=(255, 255, 254), outline=(216, 213, 207), width=1)
        draw.text((x + 24, y + 22), title, fill=(33, 34, 36), font=head_f)
        draw.text((x + 24, y + 58), guide, fill=(102, 106, 110), font=small_f)
        iso = fit(RENDER_DIR / f"{key}_iso.png", (card_w - 48, 405))
        canvas.paste(iso, (x + 24, y + 94))
        inset = fit(RENDER_DIR / f"{key}_front.png", (200, 145))
        ix = x + card_w - 230
        iy = y + 342
        draw.rounded_rectangle((ix - 8, iy - 28, ix + 208, iy + 153), radius=6, fill=(252, 252, 251), outline=(214, 211, 205), width=1)
        draw.text((ix, iy - 25), "front", fill=(88, 92, 96), font=small_f)
        canvas.paste(inset, (ix, iy))

        row = rows[key]
        comps = int(float(row["primary_component_count"]))
        lcr = float(row["primary_largest_component_ratio"])
        vox = int(float(row["occupied_voxels"]))
        yy = y + 535
        color = (172, 54, 54) if comps > 10 else (82, 86, 91)
        draw.text((x + 24, yy), f"occ. comps {comps}", fill=color, font=small_f)
        draw.text((x + 24, yy + 30), f"LCR {lcr:.3f}", fill=color, font=small_f)
        draw.text((x + 24, yy + 60), f"occupied voxels {vox:,}", fill=(82, 86, 91), font=small_f)

    draw.text(
        (70, H - 62),
        "Strict reading: these baselines can be textured, but the exported GLBs remain highly fragmented under the same occupancy proxy; they are not adequate textured recursive assets without projection-aware repair.",
        fill=(96, 98, 100),
        font=small_f,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
