#!/usr/bin/env python3
"""Compose pure-white textured GLB renders from the latest method-compare batch."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
SRC = ROOT / "visuals/ralph_positive_method_texture_xformers_20260509_223618"
FLAT = SRC / "pure_white_renders_2315/flat"
VIS_OUT = SRC / "ralph_positive_method_texture_contact_pure_white_20260509.png"
FIG_PNG = ROOT / "paper_siga/figures/ralph_positive_method_texture_contact_pure_white_20260509.png"
FIG_PDF = ROOT / "paper_siga/figures/ralph_positive_method_texture_contact_pure_white_20260509.pdf"

WHITE = (255, 255, 255)
INK = (24, 27, 31)
MUTED = (78, 84, 92)
FAINT = (224, 227, 232)
GOOD = (34, 111, 83)
WARN = (151, 93, 38)


PANELS = [
    {
        "key": "bismuth_sparse_bridge",
        "summary": "bismuth_fork_sparse_bridge",
        "title": "bismuth scaffold",
        "role": "positive: crystal-like connected scaffold",
        "color": GOOD,
    },
    {
        "key": "pyrite_sparse_bridge",
        "summary": "pyrite_fork_sparse_bridge",
        "title": "pyrite lattice",
        "role": "positive: lattice/symmetry case",
        "color": GOOD,
    },
    {
        "key": "coral_sparse_close",
        "summary": "coral_fork_sparse_close",
        "title": "coral / porous growth",
        "role": "positive: non-tree organic scaffold",
        "color": GOOD,
    },
    {
        "key": "dla_raw_boundary",
        "summary": "dla_raw_boundary",
        "title": "hard DLA boundary",
        "role": "boundary: not main positive evidence",
        "color": WARN,
    },
]


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


TITLE = font(46, True)
SUB = font(22)
HEAD = font(27, True)
BODY = font(20)
SMALL = font(17)


def crop_object(im: Image.Image, threshold: int = 248) -> Image.Image:
    rgb = im.convert("RGB")
    pix = rgb.load()
    xs: list[int] = []
    ys: list[int] = []
    step = 3
    for y in range(0, rgb.height, step):
        for x in range(0, rgb.width, step):
            r, g, b = pix[x, y]
            if min(r, g, b) < threshold:
                xs.append(x)
                ys.append(y)
    if not xs:
        return rgb
    pad = 52
    box = (
        max(0, min(xs) - pad),
        max(0, min(ys) - pad),
        min(rgb.width, max(xs) + pad),
        min(rgb.height, max(ys) + pad),
    )
    return rgb.crop(box)


def fit(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    w, h = size
    scale = min(w / im.width, h / im.height)
    resized = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.Resampling.LANCZOS)
    out = Image.new("RGB", size, WHITE)
    out.paste(resized, ((w - resized.width) // 2, (h - resized.height) // 2))
    return out


def read_summary(name: str) -> dict:
    return json.loads((SRC / name / "summary.json").read_text(encoding="utf-8"))


def main() -> None:
    canvas = Image.new("RGB", (2400, 1420), WHITE)
    draw = ImageDraw.Draw(canvas)
    draw.text((70, 54), "Trellis2 textured export after connectivity-first grammar execution", font=TITLE, fill=INK)
    draw.text(
        (70, 112),
        "Pure-white, no-ground Blender renders. Texture/PBR export is reported separately from topology evidence.",
        font=SUB,
        fill=MUTED,
    )
    draw.line((70, 160, 2330, 160), fill=FAINT, width=2)

    cell_w, cell_h = 1080, 520
    image_h = 370
    x0, y0 = 110, 215
    gap_x, gap_y = 90, 120
    for idx, panel in enumerate(PANELS):
        row = idx // 2
        col = idx % 2
        x = x0 + col * (cell_w + gap_x)
        y = y0 + row * (cell_h + gap_y)
        im = Image.open(FLAT / f"{panel['key']}_iso.png").convert("RGB")
        art = fit(crop_object(im), (cell_w, image_h))
        canvas.paste(art, (x, y + 72))
        draw.text((x, y), panel["title"], font=HEAD, fill=INK)
        draw.text((x, y + 34), panel["role"], font=BODY, fill=panel["color"])
        s = read_summary(panel["summary"])
        stats = f"{s['mesh_vertices']:,} verts / {s['mesh_faces']:,} faces   {s['shape_slat_tokens']:,} shape tokens   {s['pbr_voxel_tokens']:,} PBR voxels"
        draw.text((x, y + 455), stats, font=SMALL, fill=MUTED)

    draw.line((70, 1328, 2330, 1328), fill=FAINT, width=2)
    draw.text(
        (70, 1360),
        "Use bismuth/pyrite/coral as positive non-tree candidates; keep hard DLA as a stress/boundary panel unless occupancy-primary connectivity improves.",
        font=SMALL,
        fill=MUTED,
    )
    for out in (VIS_OUT, FIG_PNG, FIG_PDF):
        out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(VIS_OUT, "PNG", optimize=True)
    canvas.save(FIG_PNG, "PNG", optimize=True)
    canvas.save(FIG_PDF, "PDF", resolution=300.0)
    print(VIS_OUT)
    print(FIG_PNG)
    print(FIG_PDF)


if __name__ == "__main__":
    main()
