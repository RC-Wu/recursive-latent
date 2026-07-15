from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "paper_siga" / "figures"
OUT_PNG = OUT_DIR / "depth_parameter_mesh_showcase_zoom_20260509.png"
OUT_PDF = OUT_DIR / "depth_parameter_mesh_showcase_zoom_20260509.pdf"

BG = (246, 245, 241)
PANEL = (255, 255, 253)
INK = (33, 35, 38)
MUTED = (93, 98, 104)
FAINT = (232, 230, 224)
LINE = (205, 203, 197)
BLUE = (49, 83, 112)
RED = (130, 55, 49)
GREEN = (57, 102, 83)


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


F_TITLE = font(41, True)
F_SUB = font(19)
F_ROW = font(22, True)
F_NOTE = font(16)
F_LABEL = font(20, True)
F_SMALL = font(15)
F_TINY = font(13)


def rr(draw, box, radius=7, fill=PANEL, outline=LINE, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_size(draw, text, fnt):
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def center_text(draw, box, text, fnt, fill=INK):
    x, y, w, h = box
    tw, th = text_size(draw, text, fnt)
    draw.text((x + (w - tw) / 2, y + (h - th) / 2), text, font=fnt, fill=fill)


def wrapped(draw, xy, text, fnt, max_width, fill=MUTED, gap=4):
    x, y = xy
    words = text.split()
    line = ""
    for word in words:
        trial = word if not line else f"{line} {word}"
        if text_size(draw, trial, fnt)[0] <= max_width:
            line = trial
            continue
        if line:
            draw.text((x, y), line, font=fnt, fill=fill)
            y += fnt.size + gap
        line = word
    if line:
        draw.text((x, y), line, font=fnt, fill=fill)


def wrapped_lines(draw, xy, text, fnt, max_width, fill=MUTED, gap=4, max_lines=None):
    x, y = xy
    words = text.split()
    lines = []
    line = ""
    for word in words:
        trial = word if not line else f"{line} {word}"
        if text_size(draw, trial, fnt)[0] <= max_width:
            line = trial
            continue
        if line:
            lines.append(line)
        line = word
    if line:
        lines.append(line)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + gap
    return y


def crop_alpha(im, pad=12):
    im = im.convert("RGBA")
    alpha = im.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return im
    x0, y0, x1, y1 = bbox
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def load(path, crop=True):
    im = Image.open(ROOT / path).convert("RGBA")
    return crop_alpha(im) if crop else im


def cover_crop(im, ratio):
    current = im.width / im.height
    if current > ratio:
        new_w = int(im.height * ratio)
        x0 = (im.width - new_w) // 2
        return im.crop((x0, 0, x0 + new_w, im.height))
    new_h = int(im.width / ratio)
    y0 = (im.height - new_h) // 2
    return im.crop((0, y0, im.width, y0 + new_h))


def fit(canvas, im, box, cover=False):
    x, y, w, h = box
    if cover:
        im = cover_crop(im, w / h)
    scale = max(w / im.width, h / im.height) if cover else min(w / im.width, h / im.height)
    size = (max(1, int(im.width * scale)), max(1, int(im.height * scale)))
    resized = im.resize(size, Image.Resampling.LANCZOS)
    px = x + (w - size[0]) // 2
    py = y + (h - size[1]) // 2
    canvas.alpha_composite(resized, (px, py))


def cell(canvas, draw, x, y, w, h, label, image_path, tag, accent):
    rr(draw, (x, y, x + w, y + h), 7, PANEL, LINE)
    draw.line((x + 1, y + 1, x + w - 1, y + 1), fill=accent, width=3)
    center_text(draw, (x + 8, y + 11, w - 16, 24), label, F_LABEL)
    fit(canvas, load(image_path), (x + 14, y + 38, w - 28, h - 66))
    tw, _ = text_size(draw, tag, F_TINY)
    rr(draw, (x + 12, y + h - 29, x + 24 + tw, y + h - 9), 4, (242, 242, 239), None)
    draw.text((x + 18, y + h - 27), tag, font=F_TINY, fill=MUTED)


def zoom_cell(canvas, draw, x, y, w, h, title, image_path, caption, accent, crop_box=None):
    rr(draw, (x, y, x + w, y + h), 7, PANEL, LINE)
    draw.line((x + 1, y + 1, x + w - 1, y + 1), fill=accent, width=3)
    center_text(draw, (x + 8, y + 10, w - 16, 22), title, F_LABEL)
    im = load(image_path, crop=False).convert("RGBA")
    if crop_box:
        x0, y0, x1, y1 = crop_box
        im = im.crop((x0, y0, x1, y1))
    fit(canvas, im, (x + 14, y + 38, w - 28, h - 86), cover=True)
    draw.rectangle((x + 14, y + h - 43, x + w - 14, y + h - 42), fill=FAINT)
    wrapped(draw, (x + 16, y + h - 35), caption, F_TINY, w - 32, MUTED, gap=2)


def make():
    rows = [
        {
            "letter": "A",
            "title": "Vine recursive depth",
            "note": "Same vine family, Parthenocissus material guide, camera, and renderer; only recursion depth changes.",
            "accent": BLUE,
            "items": [
                ("d=1", "visuals/vine_depth_textured_showcase_20260509/renders/vine_depth1_iso.png", "textured mesh"),
                ("d=2", "visuals/vine_depth_textured_showcase_20260509/renders/vine_depth2_iso.png", "textured mesh"),
                ("d=3", "visuals/vine_depth_textured_showcase_20260509/renders/vine_depth3_iso.png", "textured mesh"),
                ("d=4", "visuals/vine_depth_textured_showcase_20260509/renders/vine_depth4_iso.png", "textured mesh"),
            ],
            "zooms": [
                ("branch zoom", "visuals/vine_zoom_in_multiscale_20260509/B_branch_zoom.png", "branch-level detail"),
                ("tip zoom", "visuals/vine_zoom_in_multiscale_20260509/C_tip_zoom.png", "terminal detail"),
            ],
        },
        {
            "letter": "B",
            "title": "Connected coral scaffold depth",
            "note": "Same connected scaffold and coral guide; depth changes scale and count of attached local modules.",
            "accent": RED,
            "items": [
                ("d=1", "visuals/coral_depth_textured_showcase_20260509/renders/stage01_iso.png", "coral guide"),
                ("d=2", "visuals/coral_depth_textured_showcase_20260509/renders/stage02_iso.png", "coral guide"),
                ("d=3", "visuals/coral_depth_textured_showcase_20260509/renders/stage03_iso.png", "coral guide"),
                ("d=4", "visuals/coral_depth_textured_showcase_20260509/renders/stage04_iso.png", "coral guide"),
            ],
            "zooms": [
                ("d=4 local", "visuals/coral_depth_textured_showcase_20260509/renders/stage04_iso.png", "connected bead-like ends", (250, 250, 900, 900)),
                ("front detail", "visuals/coral_depth_textured_showcase_20260509/renders/stage04_front.png", "same mesh, front view", (245, 210, 900, 865)),
            ],
        },
        {
            "letter": "C",
            "title": "Coral density parameter",
            "note": "Same stage and octopus guide; lambda changes local compactness rather than serving as an ablation.",
            "accent": GREEN,
            "items": [
                ("lambda=0.45", "visuals/coral_density_param_texture_20260509/renders/density_0p45_iso.png", "fixed stage"),
                ("lambda=0.70", "visuals/coral_density_param_texture_20260509/renders/density_0p70_iso.png", "fixed stage"),
                ("lambda=0.95", "visuals/coral_density_param_texture_20260509/renders/density_0p95_iso.png", "fixed stage"),
                ("lambda=1.20", "visuals/coral_density_param_texture_20260509/renders/density_1p20_iso.png", "fixed stage"),
            ],
            "zooms": [
                ("low lambda", "visuals/coral_density_param_texture_20260509/renders/density_0p45_iso.png", "more open local spacing", (310, 300, 1040, 1030)),
                ("high lambda", "visuals/coral_density_param_texture_20260509/renders/density_1p20_iso.png", "more compact local mass", (340, 315, 1085, 1060)),
            ],
        },
    ]

    margin = 48
    label_w = 292
    cell_w = 218
    zoom_w = 178
    row_h = 244
    gap = 16
    zoom_gap = 12
    row_gap = 28
    header_h = 112
    footer_h = 36
    width = margin * 2 + label_w + 4 * cell_w + 3 * gap + gap + 2 * zoom_w + zoom_gap
    height = margin + header_h + len(rows) * row_h + (len(rows) - 1) * row_gap + footer_h

    canvas = Image.new("RGBA", (width, height), BG + (255,))
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, margin - 5), "Recursive growth under matched rendering conditions", font=F_TITLE, fill=INK)
    draw.text(
        (margin, margin + 43),
        "Side-by-side textured mesh renders; each row varies one control while keeping the family, guide/material path, camera, and renderer fixed.",
        font=F_SUB,
        fill=MUTED,
    )
    draw.line((margin, margin + 82, width - margin, margin + 82), fill=LINE, width=2)

    y = margin + header_h
    for row in rows:
        x0 = margin
        draw.text((x0, y + 8), row["letter"], font=F_ROW, fill=row["accent"])
        note_y = wrapped_lines(draw, (x0 + 35, y + 8), row["title"], F_ROW, label_w - 50, INK, gap=2, max_lines=2)
        wrapped(draw, (x0 + 35, note_y + 9), row["note"], F_NOTE, label_w - 48, MUTED, gap=4)
        draw.line((x0 + 35, y + 142, x0 + label_w - 24, y + 142), fill=row["accent"], width=3)
        wrapped(draw, (x0 + 35, y + 154), "Mesh or textured-mesh renders only.", F_SMALL, label_w - 48, MUTED, gap=3)

        x = margin + label_w
        for label, path, tag in row["items"]:
            cell(canvas, draw, x, y, cell_w, row_h, label, path, tag, row["accent"])
            x += cell_w + gap

        x += 2
        for zoom in row["zooms"]:
            title, path, caption, *maybe_crop = zoom
            crop_box = maybe_crop[0] if maybe_crop else None
            zoom_cell(canvas, draw, x, y, zoom_w, row_h, title, path, caption, row["accent"], crop_box)
            x += zoom_w + zoom_gap
        y += row_h + row_gap

    draw.text(
        (margin, height - margin + 3),
        "Qualitative method-behavior visualization, not an ablation study; no point clouds or scatter plots are used.",
        font=F_TINY,
        fill=MUTED,
    )

    rgb = Image.new("RGB", canvas.size, BG)
    rgb.paste(canvas, mask=canvas.getchannel("A"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rgb.save(OUT_PNG, "PNG", optimize=True)
    rgb.save(OUT_PDF, "PDF", resolution=300.0)
    print(OUT_PNG)
    print(OUT_PDF)


if __name__ == "__main__":
    make()
