from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
RUN_DIR = ROOT / "visuals" / "pyrite_depth_hq_warm_showcase_20260509"
RENDER_DIR = RUN_DIR / "renders"
METRICS = RUN_DIR / "metrics_occ64.csv"
FIG_DIR = ROOT / "paper_siga" / "figures"
OUT_PNG = FIG_DIR / "pyrite_hq_depth_textured_showcase_20260509.png"
OUT_PDF = FIG_DIR / "pyrite_hq_depth_textured_showcase_20260509.pdf"

BG = (247, 247, 244)
PANEL = (255, 255, 255)
INK = (31, 34, 37)
MUTED = (91, 96, 101)
LINE = (217, 216, 210)
BLUE = (58, 88, 115)
GOLD = (156, 128, 64)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


F_TITLE = font(28, True)
F_SUB = font(16)
F_LABEL = font(19, True)
F_SMALL = font(13)
F_TINY = font(11)


def load_csv(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        return {row["label"]: row for row in csv.DictReader(f)}


def fit(canvas: Image.Image, im: Image.Image, box: tuple[int, int, int, int]) -> None:
    x, y, w, h = box
    im = im.convert("RGBA")
    scale = min(w / im.width, h / im.height)
    size = (max(1, int(im.width * scale)), max(1, int(im.height * scale)))
    resized = im.resize(size, Image.Resampling.LANCZOS)
    canvas.alpha_composite(resized, (x + (w - size[0]) // 2, y + (h - size[1]) // 2))


def crop_zoom(im: Image.Image, stage: int) -> Image.Image:
    w, h = im.size
    side = int(min(w, h) * (0.40 if stage <= 2 else 0.36))
    cx = int(w * (0.52 if stage < 4 else 0.56))
    cy = int(h * 0.50)
    return im.crop((max(0, cx - side // 2), max(0, cy - side // 2), min(w, cx + side // 2), min(h, cy + side // 2)))


def draw_badge(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: tuple[int, int, int]) -> None:
    x, y = xy
    pad_x, pad_y = 8, 4
    bbox = draw.textbbox((0, 0), text, font=F_TINY)
    w = bbox[2] - bbox[0] + pad_x * 2
    h = bbox[3] - bbox[1] + pad_y * 2
    draw.rounded_rectangle((x, y, x + w, y + h), radius=5, fill=fill)
    draw.text((x + pad_x, y + pad_y - 1), text, font=F_TINY, fill=(255, 255, 255))


def draw_panel(canvas: Image.Image, draw: ImageDraw.ImageDraw, stage: int, x: int, y: int, w: int, h: int, metrics: dict[str, dict[str, str]]) -> None:
    label = f"stage{stage:02d}"
    row = metrics[label]
    lcr = float(row["primary_largest_component_ratio"])
    box_d = float(row["box_count_dimension_proxy"])
    voxels = int(float(row["occupied_voxels"]))
    draw.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=PANEL, outline=LINE, width=1)
    draw.text((x + 14, y + 12), f"Depth {stage}", font=F_LABEL, fill=INK)
    draw_badge(draw, (x + w - 128, y + 13), "connected", BLUE if lcr > 0.995 else GOLD)

    iso = Image.open(RENDER_DIR / f"{label}_iso.png")
    fit(canvas, iso, (x + 8, y + 46, w - 16, h - 118))

    inset_size = 118
    inset = crop_zoom(iso, stage).resize((inset_size, inset_size), Image.Resampling.LANCZOS)
    inset_x = x + w - inset_size - 14
    inset_y = y + h - inset_size - 68
    draw.rounded_rectangle((inset_x - 4, inset_y - 4, inset_x + inset_size + 4, inset_y + inset_size + 4), radius=6, fill=(255, 255, 255), outline=LINE)
    canvas.paste(inset, (inset_x, inset_y))
    draw.text((inset_x + 8, inset_y + inset_size - 18), "zoom", font=F_TINY, fill=MUTED)

    draw.line((x + 14, y + h - 52, x + w - 14, y + h - 52), fill=LINE, width=1)
    draw.text((x + 14, y + h - 36), f"LCR {lcr:.3f}   box D {box_d:.2f}   occ {voxels:,}", font=F_SMALL, fill=MUTED)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    metrics = load_csv(METRICS)
    margin = 46
    gap = 18
    panel_w = 482
    panel_h = 392
    width = margin * 2 + panel_w * 2 + gap
    height = margin * 2 + 72 + panel_h * 2 + gap
    canvas = Image.new("RGBA", (width, height), BG + (255,))
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, margin - 6), "Pyrite lattice recursion: textured crystal asset sequence", font=F_TITLE, fill=INK)
    draw.text(
        (margin, margin + 34),
        "Same connected lattice grammar, public material guide, Trellis2 texture schedule, and Blender camera across depth.",
        font=F_SUB,
        fill=MUTED,
    )
    y0 = margin + 72
    for idx, stage in enumerate([1, 2, 3, 4]):
        col = idx % 2
        row = idx // 2
        draw_panel(canvas, draw, stage, margin + col * (panel_w + gap), y0 + row * (panel_h + gap), panel_w, panel_h, metrics)
    rgb = Image.new("RGB", canvas.size, BG)
    rgb.paste(canvas, mask=canvas.getchannel("A"))
    rgb.save(OUT_PNG, "PNG", optimize=True)
    rgb.save(OUT_PDF, "PDF", resolution=300.0)
    print(OUT_PNG)
    print(OUT_PDF)


if __name__ == "__main__":
    main()
