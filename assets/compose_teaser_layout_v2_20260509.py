#!/usr/bin/env python3
"""Compose a SIGGRAPH Asia teaser candidate from existing mesh renders.

The layout intentionally separates true Trellis2 textured GLB renders from
programmatic PBR fallback renders. It does not use matplotlib or point clouds.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper_siga/figures/teaser_candidate_layout_v2_20260509.png"


BG = (245, 243, 236)
INK = (30, 33, 32)
MUTED = (89, 96, 94)
LINE = (198, 200, 194)
TRUE = (45, 112, 83)
PBR = (139, 91, 42)
PAPER = (252, 251, 247)


@dataclass(frozen=True)
class Panel:
    title: str
    source: str
    path: Path
    kind: str
    accent: tuple[int, int, int]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


F_TITLE = font(54, True)
F_SUB = font(25)
F_PANEL = font(28, True)
F_SMALL = font(20)
F_TINY = font(17, True)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def crop_content(img: Image.Image, threshold: int = 247, pad: int = 35) -> Image.Image:
    rgb = img.convert("RGB")
    gray = ImageOps.grayscale(rgb)
    mask = gray.point(lambda p: 255 if p < threshold else 0)
    box = mask.getbbox()
    if box is None:
        return img
    x0, y0, x1, y1 = box
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(img.width, x1 + pad)
    y1 = min(img.height, y1 + pad)
    return img.crop((x0, y0, x1, y1))


def cover(img: Image.Image, size: tuple[int, int], crop: bool = False) -> Image.Image:
    img = img.convert("RGBA")
    if crop:
        img = crop_content(img)
    scale = max(size[0] / img.width, size[1] / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    x = (resized.width - size[0]) // 2
    y = (resized.height - size[1]) // 2
    return resized.crop((x, y, x + size[0], y + size[1]))


def contain(img: Image.Image, size: tuple[int, int], crop: bool = False) -> Image.Image:
    img = img.convert("RGBA")
    if crop:
        img = crop_content(img)
    scale = min(size[0] / img.width, size[1] / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    layer = Image.new("RGBA", size, PAPER + (255,))
    layer.alpha_composite(resized, ((size[0] - resized.width) // 2, (size[1] - resized.height) // 2))
    return layer


def rounded_panel(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    radius: int = 8,
    fill: tuple[int, int, int] = PAPER,
    outline: tuple[int, int, int] = LINE,
) -> Image.Image:
    x0, y0, x1, y1 = box
    mask = Image.new("L", (x1 - x0, y1 - y0), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), radius=radius, fill=255)
    layer = Image.new("RGBA", (x1 - x0, y1 - y0), fill + (255,))
    canvas.paste(layer, (x0, y0), mask)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(box, radius=radius, outline=outline, width=2)
    return canvas


def badge(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, color: tuple[int, int, int]) -> None:
    x, y = xy
    tw, th = text_size(draw, text, F_TINY)
    draw.rounded_rectangle((x, y, x + tw + 26, y + th + 16), radius=6, fill=color)
    draw.text((x + 13, y + 7), text, font=F_TINY, fill=(255, 255, 248))


def draw_panel(
    canvas: Image.Image,
    panel: Panel,
    box: tuple[int, int, int, int],
    *,
    image_mode: str = "cover",
    label_inside: bool = True,
    crop: bool = False,
) -> None:
    x0, y0, x1, y1 = box
    rounded_panel(canvas, box)
    draw = ImageDraw.Draw(canvas)
    pad = 12
    image_box = (x0 + pad, y0 + pad, x1 - pad, y1 - pad)
    image_size = (image_box[2] - image_box[0], image_box[3] - image_box[1])
    img = Image.open(panel.path)
    image = contain(img, image_size, crop=crop) if image_mode == "contain" else cover(img, image_size, crop=crop)
    canvas.alpha_composite(image, (image_box[0], image_box[1]))
    draw.rounded_rectangle(image_box, radius=6, outline=(226, 226, 219), width=1)

    if label_inside:
        label_h = 72
        draw.rounded_rectangle(
            (image_box[0], image_box[3] - label_h, image_box[2], image_box[3]),
            radius=6,
            fill=(250, 249, 244, 238),
        )
        draw.rectangle((image_box[0], image_box[3] - label_h, image_box[0] + 8, image_box[3]), fill=panel.accent)
        draw.text((image_box[0] + 22, image_box[3] - 59), panel.title, font=F_PANEL, fill=INK)
        draw.text((image_box[0] + 22, image_box[3] - 28), panel.source, font=F_SMALL, fill=MUTED)
        badge(draw, (image_box[2] - 310, image_box[3] - 61), panel.kind, panel.accent)
    else:
        draw.rectangle((x0 + 18, y0 + 18, x0 + 26, y0 + 76), fill=panel.accent)
        draw.text((x0 + 42, y0 + 18), panel.title, font=F_PANEL, fill=INK)
        draw.text((x0 + 42, y0 + 50), panel.source, font=F_SMALL, fill=MUTED)
        badge(draw, (x1 - 312, y0 + 22), panel.kind, panel.accent)


def connector(draw: ImageDraw.ImageDraw, a: tuple[int, int], b: tuple[int, int]) -> None:
    draw.line((a, b), fill=(131, 139, 135), width=3)
    x, y = b
    draw.polygon([(x, y), (x - 13, y - 7), (x - 13, y + 7)], fill=(131, 139, 135))


def main() -> None:
    true_dir = ROOT / "visuals/public_guide_textured_glb_20260509/renders"
    pbr_dir = ROOT / "visuals/vine_zoom_in_multiscale_20260509"

    hero = Panel(
        "Recursive Vine",
        "true Trellis2 textured mesh",
        true_dir / "vine_parthenocissus_iso.png",
        "TRUE Trellis2 GLB",
        TRUE,
    )
    panels = [
        Panel("Portal Arch", "true Trellis2 textured mesh", true_dir / "portal_arch_iso.png", "TRUE Trellis2 GLB", TRUE),
        Panel("Tree Roots", "true Trellis2 textured mesh", true_dir / "tree_roots_iso.png", "TRUE Trellis2 GLB", TRUE),
        Panel("Sci-fi Module", "true Trellis2 textured mesh", true_dir / "scifi_gear_iso.png", "TRUE Trellis2 GLB", TRUE),
        Panel("Porous Pyrite", "true Trellis2 textured mesh", true_dir / "porous_pyrite_iso.png", "TRUE Trellis2 GLB", TRUE),
    ]
    zooms = [
        Panel("A overview", "Blender/Cycles mesh render", pbr_dir / "A_overview.png", "PBR fallback", PBR),
        Panel("B branch recursion", "Blender/Cycles mesh render", pbr_dir / "B_branch_zoom.png", "PBR fallback", PBR),
        Panel("C terminal detail", "Blender/Cycles mesh render", pbr_dir / "C_tip_zoom.png", "PBR fallback", PBR),
    ]

    canvas = Image.new("RGBA", (3200, 1700), BG + (255,))
    draw = ImageDraw.Draw(canvas)

    draw.text((82, 56), "Recursive 3D Generative Growth", font=F_TITLE, fill=INK)
    draw.text(
        (84, 122),
        "Teaser candidate v2: textured Trellis2 GLB results, with a PBR fallback zoom strip for local recursion evidence.",
        font=F_SUB,
        fill=MUTED,
    )
    draw.line((82, 172, 3118, 172), fill=(214, 213, 205), width=2)

    draw_panel(canvas, hero, (82, 220, 1536, 1280), image_mode="contain", crop=False)

    right_x = 1580
    cell_w = 748
    cell_h = 520
    gap = 32
    draw_panel(canvas, panels[0], (right_x, 220, right_x + cell_w, 220 + cell_h), image_mode="contain")
    draw_panel(canvas, panels[1], (right_x + cell_w + gap, 220, right_x + 2 * cell_w + gap, 220 + cell_h), image_mode="contain")
    draw_panel(canvas, panels[2], (right_x, 220 + cell_h + gap, right_x + cell_w, 220 + 2 * cell_h + gap), image_mode="contain")
    draw_panel(
        canvas,
        panels[3],
        (right_x + cell_w + gap, 220 + cell_h + gap, right_x + 2 * cell_w + gap, 220 + 2 * cell_h + gap),
        image_mode="contain",
    )

    strip_y = 1322
    strip_h = 300
    strip_x = 82
    strip_w = 3036
    rounded_panel(canvas, (strip_x, strip_y, strip_x + strip_w, strip_y + strip_h), fill=(250, 249, 244))
    draw.text((strip_x + 28, strip_y + 24), "Local geometry evidence", font=F_PANEL, fill=INK)
    draw.text((strip_x + 28, strip_y + 58), "programmatic material; used only as zoom-in evidence", font=F_SMALL, fill=MUTED)
    badge(draw, (strip_x + strip_w - 210, strip_y + 28), "PBR fallback", PBR)

    z_w = 786
    z_h = 210
    z0 = strip_x + 520
    for i, p in enumerate(zooms):
        x0 = z0 + i * (z_w + 38)
        img = Image.open(p.path)
        zimg = cover(img, (z_w, z_h), crop=False)
        canvas.alpha_composite(zimg, (x0, strip_y + 54))
        draw.rounded_rectangle((x0, strip_y + 54, x0 + z_w, strip_y + 54 + z_h), radius=6, outline=(205, 200, 189), width=2)
        draw.rectangle((x0, strip_y + 54 + z_h - 38, x0 + z_w, strip_y + 54 + z_h), fill=(250, 249, 244, 232))
        draw.text((x0 + 14, strip_y + 54 + z_h - 31), p.title, font=F_SMALL, fill=INK)
        if i < 2:
            connector(draw, (x0 + z_w + 10, strip_y + 159), (x0 + z_w + 33, strip_y + 159))

    draw.text((84, 1640), "No matplotlib point-cloud previews are used. All panels are mesh render composites.", font=F_SMALL, fill=MUTED)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUT, quality=95, dpi=(300, 300))
    print(OUT)


if __name__ == "__main__":
    main()
