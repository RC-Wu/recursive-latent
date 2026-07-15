from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
RENDER_DIR = ROOT / "visuals" / "porous_mineral_depth_textured_showcase_20260509" / "renders"
GLB_METRICS = (
    ROOT
    / "visuals"
    / "porous_mineral_depth_textured_showcase_20260509"
    / "porous_mineral_depth_textured_glb_metrics_occ64.csv"
)
SRC_METRICS = (
    ROOT
    / "results"
    / "connected_coral_depth_cases_20260509"
    / "porous_mineral_depth"
    / "source_metrics_occ64.csv"
)
FIG_DIR = ROOT / "paper_siga" / "figures"
OUT_PNG = FIG_DIR / "porous_mineral_depth_textured_showcase_20260509.png"
OUT_PDF = FIG_DIR / "porous_mineral_depth_textured_showcase_20260509.pdf"

BG = (248, 247, 244)
PANEL = (255, 255, 255)
INK = (34, 36, 39)
MUTED = (94, 100, 106)
LINE = (219, 218, 212)
ACCENT = (58, 116, 93)
WARN = (174, 128, 52)


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


F_TITLE = font(30, True)
F_SUB = font(18)
F_LABEL = font(21, True)
F_SMALL = font(16)
F_TINY = font(13)


def load_csv(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {row["label"]: row for row in rows}


def source_label(stage: int) -> str:
    prefix = f"porous_mineral_depth_stage_{stage:02d}_"
    for key in SRC_ROWS:
        if key.startswith(prefix):
            return key
    raise KeyError(prefix)


def fit(canvas: Image.Image, im: Image.Image, box: tuple[int, int, int, int]) -> None:
    x, y, w, h = box
    im = im.convert("RGBA")
    scale = min(w / im.width, h / im.height)
    size = (max(1, int(im.width * scale)), max(1, int(im.height * scale)))
    resized = im.resize(size, Image.Resampling.LANCZOS)
    canvas.alpha_composite(resized, (x + (w - size[0]) // 2, y + (h - size[1]) // 2))


def center_zoom(im: Image.Image) -> Image.Image:
    w, h = im.size
    side = int(min(w, h) * 0.45)
    cx, cy = int(w * 0.52), int(h * 0.50)
    return im.crop((max(0, cx - side // 2), max(0, cy - side // 2), min(w, cx + side // 2), min(h, cy + side // 2)))


def draw_badge(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, color: tuple[int, int, int]) -> None:
    pad_x, pad_y = 10, 5
    bbox = draw.textbbox((0, 0), text, font=F_TINY)
    w = bbox[2] - bbox[0] + pad_x * 2
    h = bbox[3] - bbox[1] + pad_y * 2
    draw.rounded_rectangle((x, y, x + w, y + h), radius=6, fill=color)
    draw.text((x + pad_x, y + pad_y - 1), text, font=F_TINY, fill=(255, 255, 255))


def draw_panel(canvas: Image.Image, draw: ImageDraw.ImageDraw, stage: int, x: int, y: int, w: int, h: int) -> None:
    label = f"stage{stage:02d}"
    glb = GLB_ROWS[label]
    src = SRC_ROWS[source_label(stage)]
    draw.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=PANEL, outline=LINE, width=1)
    draw.text((x + 18, y + 14), f"Depth {stage}", font=F_LABEL, fill=INK)
    occ_lcr = float(glb["primary_largest_component_ratio"])
    badge = "connected support" if occ_lcr >= 0.97 else "needs inspection"
    draw_badge(draw, x + w - 158, y + 15, badge, ACCENT if occ_lcr >= 0.97 else WARN)

    im = Image.open(RENDER_DIR / f"{label}_iso.png")
    fit(canvas, im, (x + 10, y + 54, w - 20, h - 142))

    inset_side = 132
    inset = center_zoom(im).resize((inset_side, inset_side), Image.Resampling.LANCZOS)
    inset_x = x + w - inset_side - 22
    inset_y = y + h - inset_side - 78
    draw.rounded_rectangle((inset_x - 4, inset_y - 4, inset_x + inset_side + 4, inset_y + inset_side + 4), radius=6, fill=(255, 255, 255), outline=LINE)
    canvas.paste(inset, (inset_x, inset_y))

    draw.line((x + 18, y + h - 62, x + w - 18, y + h - 62), fill=LINE, width=1)
    metric = (
        f"GLB occ LCR {occ_lcr:.3f}  |  "
        f"source face LCR {float(src['largest_component_vertex_ratio']):.3f}  |  "
        f"box D {float(glb['box_count_dimension_proxy']):.2f}"
    )
    draw.text((x + 18, y + h - 44), metric, font=F_SMALL, fill=MUTED)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    margin = 50
    gap = 22
    panel_w = 505
    panel_h = 455
    width = margin * 2 + panel_w * 2 + gap
    height = margin * 2 + 86 + panel_h * 2 + gap
    canvas = Image.new("RGBA", (width, height), BG + (255,))
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, margin - 6), "Porous mineral recursion: connected textured GLB sequence", font=F_TITLE, fill=INK)
    draw.text(
        (margin, margin + 40),
        "Same grammar and guide across depths. This is a non-tree scaffold positive case, not a final bismuth/crystal head figure.",
        font=F_SUB,
        fill=MUTED,
    )
    y0 = margin + 84
    for idx, stage in enumerate([1, 2, 3, 4]):
        col = idx % 2
        row = idx // 2
        draw_panel(canvas, draw, stage, margin + col * (panel_w + gap), y0 + row * (panel_h + gap), panel_w, panel_h)
    rgb = Image.new("RGB", canvas.size, BG)
    rgb.paste(canvas, mask=canvas.getchannel("A"))
    rgb.save(OUT_PNG, "PNG", optimize=True)
    rgb.save(OUT_PDF, "PDF", resolution=300.0)
    print(OUT_PNG)
    print(OUT_PDF)


GLB_ROWS = load_csv(GLB_METRICS)
SRC_ROWS = load_csv(SRC_METRICS)


if __name__ == "__main__":
    main()
