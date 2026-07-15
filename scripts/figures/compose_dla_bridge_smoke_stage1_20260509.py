from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
FIG_DIR = ROOT / "paper_siga" / "figures"
OUT_PNG = FIG_DIR / "dla_bridge_smoke_stage1_qa_20260509.png"
OUT_PDF = FIG_DIR / "dla_bridge_smoke_stage1_qa_20260509.pdf"

BG = (248, 247, 244)
PANEL = (255, 255, 255)
INK = (34, 36, 39)
MUTED = (94, 100, 106)
LINE = (220, 218, 212)
NEG = (168, 72, 62)
WARN = (194, 142, 45)
OK = (64, 118, 92)


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


F_TITLE = font(38, True)
F_SUB = font(19)
F_LABEL = font(22, True)
F_SMALL = font(17)
F_TINY = font(14)


CASES = [
    {
        "title": "Hard DLA / raw",
        "img": "visuals/dla_bridge_smoke_stage1_20260509/renders/hard_raw_iso.png",
        "status": "fragmented",
        "color": NEG,
        "metrics": "occ 4 / LCR .357; face 4 / .356",
    },
    {
        "title": "Hard DLA / sparse bridge",
        "img": "visuals/dla_bridge_smoke_stage1_20260509/renders/hard_sparse_bridge_iso.png",
        "status": "fake bridges",
        "color": NEG,
        "metrics": "occ 4 / LCR .642; face 4 / .742",
    },
    {
        "title": "Volumetric DLA / raw",
        "img": "visuals/dla_bridge_smoke_stage1_20260509/renders/volumetric_raw_iso.png",
        "status": "connected support",
        "color": OK,
        "metrics": "occ 1 / LCR 1.000; face 3 / .520",
    },
    {
        "title": "Volumetric DLA / bridge",
        "img": "visuals/dla_bridge_smoke_stage1_20260509/renders/volumetric_sparse_bridge_iso.png",
        "status": "support worsens",
        "color": WARN,
        "metrics": "occ 7 / LCR .870; face 1 / 1.000",
    },
]


def crop(im: Image.Image, pad: int = 8) -> Image.Image:
    im = im.convert("RGBA")
    # Keep square renders mostly intact; crop only fully transparent if present.
    alpha = im.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return im
    if bbox == (0, 0, im.width, im.height):
        return im
    x0, y0, x1, y1 = bbox
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def fit(canvas: Image.Image, im: Image.Image, box: tuple[int, int, int, int]) -> None:
    x, y, w, h = box
    scale = min(w / im.width, h / im.height)
    size = (max(1, int(im.width * scale)), max(1, int(im.height * scale)))
    resized = im.resize(size, Image.Resampling.LANCZOS)
    px = x + (w - size[0]) // 2
    py = y + (h - size[1]) // 2
    canvas.alpha_composite(resized, (px, py))


def draw_panel(canvas: Image.Image, draw: ImageDraw.ImageDraw, case: dict, x: int, y: int, w: int, h: int) -> None:
    draw.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=PANEL, outline=LINE, width=1)
    draw.text((x + 20, y + 16), case["title"], font=F_LABEL, fill=INK)
    badge = case["status"]
    tw = draw.textbbox((0, 0), badge, font=F_TINY)[2]
    draw.rounded_rectangle((x + w - tw - 34, y + 17, x + w - 18, y + 43), radius=6, fill=case["color"])
    draw.text((x + w - tw - 26, y + 22), badge, font=F_TINY, fill=(255, 255, 255))
    im = crop(Image.open(ROOT / case["img"]))
    fit(canvas, im, (x + 16, y + 56, w - 32, h - 118))
    draw.line((x + 18, y + h - 50, x + w - 18, y + h - 50), fill=LINE, width=1)
    draw.text((x + 20, y + h - 38), case["metrics"], font=F_SMALL, fill=MUTED)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    margin = 54
    gap = 22
    panel_w = 500
    panel_h = 440
    width = margin * 2 + panel_w * 2 + gap
    height = margin * 2 + 82 + panel_h * 2 + gap
    canvas = Image.new("RGBA", (width, height), BG + (255,))
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, margin - 6), "DLA bridge smoke: post-hoc repair is not enough", font=F_TITLE, fill=INK)
    draw.text(
        (margin, margin + 42),
        "Stage-1 mesh renders; texture off. Occupancy is primary; raw face components are diagnostics.",
        font=F_SUB,
        fill=MUTED,
    )
    y0 = margin + 88
    positions = [
        (margin, y0),
        (margin + panel_w + gap, y0),
        (margin, y0 + panel_h + gap),
        (margin + panel_w + gap, y0 + panel_h + gap),
    ]
    for case, (x, y) in zip(CASES, positions):
        draw_panel(canvas, draw, case, x, y, panel_w, panel_h)
    rgb = Image.new("RGB", canvas.size, BG)
    rgb.paste(canvas, mask=canvas.getchannel("A"))
    rgb.save(OUT_PNG, "PNG", optimize=True)
    rgb.save(OUT_PDF, "PDF", resolution=300.0)
    print(OUT_PNG)
    print(OUT_PDF)


if __name__ == "__main__":
    main()
