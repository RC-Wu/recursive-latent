from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
RENDER_DIR = ROOT / "visuals" / "dla_bridge_smoke_stage1_20260509_rerun1455" / "renders"
FIG_DIR = ROOT / "paper_siga" / "figures"
OUT_PNG = FIG_DIR / "dla_bridge_smoke_stage1_rerun1455_20260509.png"
OUT_PDF = FIG_DIR / "dla_bridge_smoke_stage1_rerun1455_20260509.pdf"

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


F_TITLE = font(31, True)
F_SUB = font(17)
F_LABEL = font(21, True)
F_SMALL = font(15)
F_TINY = font(12)


CASES = [
    {
        "title": "Hard DLA / raw",
        "img": "hard_raw_iso.png",
        "inset": "hard_raw_front.png",
        "status": "fragmented",
        "color": NEG,
        "metrics": "final occ 4 / LCR .380; face 4 / .378",
        "note": "post-projection keeps disconnected chunks",
    },
    {
        "title": "Hard DLA / sparse bridge",
        "img": "hard_bridge_iso.png",
        "inset": "hard_bridge_front.png",
        "status": "not enough",
        "color": NEG,
        "metrics": "final occ 5 / LCR .591; face 3 / .811",
        "note": "face improves, occupancy remains fragmented",
    },
    {
        "title": "Volumetric DLA / raw",
        "img": "volumetric_raw_iso.png",
        "inset": "volumetric_raw_front.png",
        "status": "connected",
        "color": OK,
        "metrics": "final occ 1 / LCR 1.000; face 3 / .521",
        "note": "grammar-native support is strongest",
    },
    {
        "title": "Volumetric DLA / sparse bridge",
        "img": "volumetric_bridge_iso.png",
        "inset": "volumetric_bridge_front.png",
        "status": "over-bridge",
        "color": WARN,
        "metrics": "final occ 7 / LCR .873; face 2 / .990",
        "note": "face metric improves while support worsens",
    },
]


def fit(canvas: Image.Image, im: Image.Image, box: tuple[int, int, int, int]) -> None:
    x, y, w, h = box
    im = im.convert("RGBA")
    scale = min(w / im.width, h / im.height)
    size = (max(1, int(im.width * scale)), max(1, int(im.height * scale)))
    resized = im.resize(size, Image.Resampling.LANCZOS)
    canvas.alpha_composite(resized, (x + (w - size[0]) // 2, y + (h - size[1]) // 2))


def draw_badge(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, color: tuple[int, int, int]) -> None:
    bbox = draw.textbbox((0, 0), text, font=F_TINY)
    w = bbox[2] - bbox[0] + 18
    h = bbox[3] - bbox[1] + 8
    draw.rounded_rectangle((x, y, x + w, y + h), radius=5, fill=color)
    draw.text((x + 9, y + 3), text, font=F_TINY, fill=(255, 255, 255))


def draw_panel(canvas: Image.Image, draw: ImageDraw.ImageDraw, case: dict, x: int, y: int, w: int, h: int) -> None:
    draw.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=PANEL, outline=LINE, width=1)
    draw.text((x + 16, y + 14), case["title"], font=F_LABEL, fill=INK)
    badge_w = draw.textbbox((0, 0), case["status"], font=F_TINY)[2] + 18
    draw_badge(draw, x + w - badge_w - 16, y + 16, case["status"], case["color"])
    fit(canvas, Image.open(RENDER_DIR / case["img"]), (x + 10, y + 52, w - 20, h - 130))

    inset = Image.open(RENDER_DIR / case["inset"]).resize((124, 124), Image.Resampling.LANCZOS)
    inset_x = x + w - 142
    inset_y = y + h - 174
    draw.rounded_rectangle((inset_x - 4, inset_y - 4, inset_x + 128, inset_y + 128), radius=6, fill=(255, 255, 255), outline=LINE)
    canvas.paste(inset, (inset_x, inset_y))

    draw.line((x + 16, y + h - 62, x + w - 16, y + h - 62), fill=LINE, width=1)
    draw.text((x + 16, y + h - 44), case["metrics"], font=F_SMALL, fill=MUTED)
    draw.text((x + 16, y + h - 24), case["note"], font=F_SMALL, fill=case["color"])


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    margin = 48
    gap = 20
    panel_w = 508
    panel_h = 405
    width = margin * 2 + panel_w * 2 + gap
    height = margin * 2 + 82 + panel_h * 2 + gap
    canvas = Image.new("RGBA", (width, height), BG + (255,))
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, margin - 6), "DLA connectivity smoke: bridge repair is not the main route", font=F_TITLE, fill=INK)
    draw.text(
        (margin, margin + 38),
        "Blender mesh renders. Occupancy support is primary; face components can improve while visible/support connectivity worsens.",
        font=F_SUB,
        fill=MUTED,
    )
    y0 = margin + 84
    for idx, case in enumerate(CASES):
        col = idx % 2
        row = idx // 2
        draw_panel(canvas, draw, case, margin + col * (panel_w + gap), y0 + row * (panel_h + gap), panel_w, panel_h)
    rgb = Image.new("RGB", canvas.size, BG)
    rgb.paste(canvas, mask=canvas.getchannel("A"))
    rgb.save(OUT_PNG, "PNG", optimize=True)
    rgb.save(OUT_PDF, "PDF", resolution=300.0)
    print(OUT_PNG)
    print(OUT_PDF)


if __name__ == "__main__":
    main()
