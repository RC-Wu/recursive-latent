#!/usr/bin/env python3
"""Compose one-to-one baseline comparison with overview callouts and zoom crops."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
RENDER_DIR = ROOT / "visuals/baseline_one_to_one_white_20260510/renders"
OUT_DIR = ROOT / "visuals/baseline_one_to_one_white_20260510"
OUT_PNG = OUT_DIR / "baseline_one_to_one_white_zoom_20260510.png"
PAPER_PNG = ROOT / "paper_siga/figures/baseline_one_to_one_white_zoom_20260510.png"

WHITE = (255, 255, 255)
INK = (22, 24, 26)
MUTED = (86, 90, 94)
LINE = (215, 219, 223)
ACCENT = (196, 60, 52)


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
            pass
    return ImageFont.load_default()


FT = font(48, True)
FH = font(27, True)
FB = font(20)
FS = font(16)


def open_white(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, WHITE + (255,))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def object_bbox(im: Image.Image) -> tuple[int, int, int, int]:
    arr = np.asarray(im.convert("RGB"))
    mask = np.any(arr < 246, axis=2)
    if not mask.any():
        return (0, 0, im.width, im.height)
    ys, xs = np.where(mask)
    pad = 28
    return (
        max(0, int(xs.min()) - pad),
        max(0, int(ys.min()) - pad),
        min(im.width, int(xs.max()) + pad),
        min(im.height, int(ys.max()) + pad),
    )


def callout_box(im: Image.Image, region: str) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = object_bbox(im)
    bw, bh = max(1, x1 - x0), max(1, y1 - y0)
    if region == "root":
        cx, cy = x0 + int(0.50 * bw), y0 + int(0.72 * bh)
    elif region == "tip":
        cx, cy = x0 + int(0.67 * bw), y0 + int(0.28 * bh)
    elif region == "facet":
        cx, cy = x0 + int(0.55 * bw), y0 + int(0.48 * bh)
    else:
        cx, cy = x0 + int(0.50 * bw), y0 + int(0.50 * bh)
    cw, ch = int(0.42 * bw), int(0.42 * bh)
    left = max(0, min(im.width - cw, cx - cw // 2))
    top = max(0, min(im.height - ch, cy - ch // 2))
    return (left, top, left + cw, top + ch)


def fit(im: Image.Image, size: tuple[int, int], cover: bool = False) -> Image.Image:
    w, h = size
    scale = max(w / im.width, h / im.height) if cover else min(w / im.width, h / im.height)
    resized = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.Resampling.LANCZOS)
    if cover:
        left = max(0, (resized.width - w) // 2)
        top = max(0, (resized.height - h) // 2)
        resized = resized.crop((left, top, left + w, top + h))
    out = Image.new("RGB", size, WHITE)
    out.paste(resized, ((w - resized.width) // 2, (h - resized.height) // 2))
    return out


def draw_panel(canvas: Image.Image, draw: ImageDraw.ImageDraw, key: str, x: int, y: int, w: int, h: int, region: str) -> None:
    src = open_white(RENDER_DIR / f"{key}.png")
    box = callout_box(src, region)
    overview = fit(src, (w, h), cover=False)
    canvas.paste(overview, (x, y))
    sx = overview.width / src.width
    sy = overview.height / src.height
    ox = x + (w - overview.width) // 2
    oy = y + (h - overview.height) // 2
    rect = (ox + int(box[0] * sx), oy + int(box[1] * sy), ox + int(box[2] * sx), oy + int(box[3] * sy))
    draw.rectangle(rect, outline=ACCENT, width=4)
    crop = fit(src.crop(box), (170, 145), cover=True)
    zx, zy = x + w - 188, y + h - 160
    draw.rectangle((zx - 2, zy - 2, zx + 172, zy + 147), outline=ACCENT, width=3)
    canvas.paste(crop, (zx, zy))


def main() -> None:
    rows = [
        ("L-system branch", "lsystem_branch_baseline_iso", "ours_vine_stage5_iso", "tip"),
        ("Space colonization tree", "sc_tree_canopy_baseline_iso", "ours_vine_root_iso", "root"),
        ("DLA cluster", "dla_cluster_baseline_iso", "ours_coral_octopus_iso", "junction"),
        ("IFS transform tree", "ifs_branch_tree_baseline_iso", "ours_pyrite_lattice_iso", "facet"),
    ]
    width, height = 2100, 2320
    canvas = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    draw.text((64, 42), "Matched baseline candidates with source-region zooms", font=FT, fill=INK)
    draw.text((64, 100), "White-background GLB renders. Red rectangles mark the crop used for the inset; final figures will replace these screening crops with tuned camera zooms.", font=FB, fill=MUTED)
    draw.text((515, 158), "Traditional baseline", font=FH, fill=MUTED)
    draw.text((1370, 158), "PS-RSLG candidate", font=FH, fill=MUTED)
    y = 205
    panel_w, panel_h = 830, 430
    for title, left_key, right_key, region in rows:
        draw.text((64, y + 20), title, font=FH, fill=INK)
        draw_panel(canvas, draw, left_key, 360, y, panel_w, panel_h, region)
        draw_panel(canvas, draw, right_key, 1210, y, panel_w, panel_h, region)
        draw.line((64, y + panel_h + 35, width - 64, y + panel_h + 35), fill=LINE, width=2)
        y += 515
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT_PNG)
    PAPER_PNG.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(PAPER_PNG)
    print(OUT_PNG)
    print(PAPER_PNG)


if __name__ == "__main__":
    main()
