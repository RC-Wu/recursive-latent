#!/usr/bin/env python3
"""Compose strict traditional-target versus selected PS-RSLG one-to-one zoom evidence."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
TRAD = ROOT / "case_gallery_for_user_20260510_remote_matched_candidates/01_traditional_targets"
OURS_V24 = ROOT / "visuals/strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510"
OURS_V25 = ROOT / "visuals/strict_visual_matched_texture_V25_root_sc_refine_zoom_white_20260510"
OUT_DIR = ROOT / "visuals/traditional_vs_v24_one_to_one_zoom_20260510"
OUT_PNG = OUT_DIR / "traditional_vs_v24_one_to_one_zoom_20260510.png"
OUT_PDF = OUT_DIR / "traditional_vs_v24_one_to_one_zoom_20260510.pdf"
PAPER_PNG = ROOT / "paper_siga/figures/traditional_vs_v24_one_to_one_zoom_20260510.png"

WHITE = (255, 255, 255)
INK = (18, 22, 26)
MUTED = (86, 92, 98)
LINE = (217, 221, 226)
ACCENT = (185, 50, 43)


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


FT = font(48, True)
FH = font(30, True)
FR = font(26, True)
FB = font(20)
FS = font(16)


def open_white(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, WHITE + (255,))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def fit_height(im: Image.Image, height: int) -> Image.Image:
    width = max(1, round(im.width * height / im.height))
    return im.resize((width, height), Image.Resampling.LANCZOS)


def fit_box(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = size
    scale = min(width / im.width, height / im.height)
    resized = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.Resampling.LANCZOS)
    out = Image.new("RGB", size, WHITE)
    out.paste(resized, ((width - resized.width) // 2, (height - resized.height) // 2))
    return out


ROWS = [
    {
        "family": "DLA / frontier",
        "tag": "cluster target -> staghorn asset",
        "traditional": TRAD / "strict_matched_traditional_targets_zoom_20260510__dla_coral_cluster_900__strict_matched_zoom_comparison.png",
        "ours": OURS_V24 / "V24_dla_staghorn_frontier/strict_matched_zoom_comparison.png",
        "metric": "V24: r0 1, LCR 1.000; 3/3 seeds stable",
    },
    {
        "family": "IFS / lattice",
        "tag": "fractal lattice -> pyrite copy bridges",
        "traditional": TRAD / "strict_matched_traditional_targets_zoom_20260510__ifs_fractal_lattice_d4__strict_matched_zoom_comparison.png",
        "ours": OURS_V24 / "V24_ifs_pyrite_lattice/strict_matched_zoom_comparison.png",
        "metric": "V24: r1 1, min r0 LCR 0.9997; tiny r0 islands",
    },
    {
        "family": "L-system / root fan",
        "tag": "branching root fan -> connected dense rootlets",
        "traditional": TRAD / "strict_matched_traditional_targets_zoom_20260510__lsys_root_fan_d5__strict_matched_zoom_comparison.png",
        "ours": OURS_V25 / "V25_root_smooth_D/strict_matched_zoom_comparison.png",
        "metric": "V25: r0 1, LCR 1.000; replaces V24 root caveat",
    },
    {
        "family": "Space colonization / crown",
        "tag": "attractor crown -> textured crown asset",
        "traditional": TRAD / "strict_matched_traditional_targets_zoom_20260510__sc_tree_crown_260__strict_matched_zoom_comparison.png",
        "ours": OURS_V25 / "V25_sc_tapered_B/strict_matched_zoom_comparison.png",
        "metric": "V25: r0 1, LCR 1.000; tapered visual candidate",
    },
]


def main() -> None:
    for row in ROWS:
        if not row["traditional"].exists():
            raise FileNotFoundError(row["traditional"])
        if not row["ours"].exists():
            raise FileNotFoundError(row["ours"])

    panel_h = 350
    cell_w = 1000
    gutter = 36
    row_label_w = 330
    margin_x = 60
    top = 150
    row_gap = 82
    width = margin_x * 2 + row_label_w + gutter + cell_w + gutter + cell_w
    height = top + len(ROWS) * panel_h + (len(ROWS) - 1) * row_gap + 92

    canvas = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    draw.text((margin_x, 32), "Strict traditional targets vs. selected PS-RSLG candidates", font=FT, fill=INK)
    draw.text(
        (margin_x, 90),
        "Each cell is an existing white-background camera-zoom strip: overview with callout, first zoom, second zoom.",
        font=FB,
        fill=MUTED,
    )

    x_label = margin_x
    x_trad = x_label + row_label_w + gutter
    x_ours = x_trad + cell_w + gutter
    draw.text((x_trad + 320, top - 42), "Traditional target", font=FH, fill=MUTED)
    draw.text((x_ours + 310, top - 42), "Selected candidate", font=FH, fill=MUTED)

    y = top
    for idx, row in enumerate(ROWS):
        draw.text((x_label, y + 14), row["family"], font=FR, fill=INK)
        draw.text((x_label, y + 52), row["tag"], font=FB, fill=MUTED)
        draw.text((x_label, y + panel_h - 58), row["metric"], font=FS, fill=MUTED)

        trad = fit_box(fit_height(open_white(row["traditional"]), panel_h), (cell_w, panel_h))
        ours = fit_box(fit_height(open_white(row["ours"]), panel_h), (cell_w, panel_h))
        canvas.paste(trad, (x_trad, y))
        canvas.paste(ours, (x_ours, y))

        draw.rectangle((x_trad, y, x_trad + cell_w, y + panel_h), outline=LINE, width=1)
        draw.rectangle((x_ours, y, x_ours + cell_w, y + panel_h), outline=LINE, width=1)
        draw.line((x_ours - gutter // 2, y, x_ours - gutter // 2, y + panel_h), fill=ACCENT, width=2)

        if idx < len(ROWS) - 1:
            draw.line((margin_x, y + panel_h + row_gap // 2, width - margin_x, y + panel_h + row_gap // 2), fill=LINE, width=1)
        y += panel_h + row_gap

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT_PNG)
    canvas.save(OUT_PDF, resolution=300.0)
    PAPER_PNG.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(PAPER_PNG)
    print(OUT_PNG)
    print(OUT_PDF)
    print(PAPER_PNG)


if __name__ == "__main__":
    main()
