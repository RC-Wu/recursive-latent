#!/usr/bin/env python3
"""Compose teaser layout v3 from existing mesh render PNGs.

This script uses only local mesh-based render assets. It separates true
Trellis2 textured GLB renders from programmatic PBR fallback zoom renders and
does not use matplotlib or point-cloud previews.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper_siga/figures/teaser_candidate_layout_v3_20260509.png"

BG = (244, 241, 233)
PANEL_BG = (252, 251, 247)
PANEL_BG_ALT = (248, 246, 239)
INK = (29, 32, 31)
MUTED = (83, 91, 88)
HAIRLINE = (198, 198, 188)
SOFT_LINE = (224, 223, 214)
TRUE = (38, 111, 82)
PBR = (146, 94, 43)
SHADOW = (217, 214, 204)


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


F_KICKER = font(20, True)
F_HERO = font(33, True)
F_PANEL = font(25, True)
F_BODY = font(19)
F_SMALL = font(16)
F_BADGE = font(16, True)
F_TINY = font(14)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def load_image(path: Path) -> Image.Image:
    if not path.exists():
        raise FileNotFoundError(path)
    return Image.open(path).convert("RGBA")


def rounded_rect_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def paste_rounded(
    canvas: Image.Image,
    image: Image.Image,
    box: tuple[int, int, int, int],
    radius: int,
) -> None:
    x0, y0, x1, y1 = box
    mask = rounded_rect_mask((x1 - x0, y1 - y0), radius)
    canvas.paste(image, (x0, y0), mask)


def fit_cover(
    image: Image.Image,
    size: tuple[int, int],
    *,
    anchor: tuple[float, float] = (0.5, 0.5),
    source_crop: tuple[int, int, int, int] | None = None,
) -> Image.Image:
    image = image.convert("RGBA")
    if source_crop is not None:
        image = image.crop(source_crop)
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    max_x = resized.width - size[0]
    max_y = resized.height - size[1]
    x = round(max_x * anchor[0]) if max_x > 0 else 0
    y = round(max_y * anchor[1]) if max_y > 0 else 0
    return resized.crop((x, y, x + size[0], y + size[1]))


def fit_contain(image: Image.Image, size: tuple[int, int], bg: tuple[int, int, int] = PANEL_BG) -> Image.Image:
    image = image.convert("RGBA")
    scale = min(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    layer = Image.new("RGBA", size, bg + (255,))
    layer.alpha_composite(resized, ((size[0] - resized.width) // 2, (size[1] - resized.height) // 2))
    return layer


def draw_badge(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    label: str,
    color: tuple[int, int, int],
) -> None:
    x, y = xy
    tw, th = text_size(draw, label, F_BADGE)
    draw.rounded_rectangle((x, y, x + tw + 24, y + th + 14), radius=6, fill=color)
    draw.text((x + 12, y + 6), label, font=F_BADGE, fill=(255, 255, 247))


def draw_panel_shell(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    *,
    fill: tuple[int, int, int] = PANEL_BG,
    accent: tuple[int, int, int] | None = None,
) -> None:
    x0, y0, x1, y1 = box
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((x0 + 4, y0 + 4, x1 + 4, y1 + 4), radius=8, fill=SHADOW)
    draw.rounded_rectangle(box, radius=8, fill=fill, outline=HAIRLINE, width=2)
    if accent:
        draw.rectangle((x0, y0 + 12, x0 + 8, y1 - 12), fill=accent)


def draw_labeled_panel(
    canvas: Image.Image,
    panel: Panel,
    box: tuple[int, int, int, int],
    *,
    mode: str = "contain",
    anchor: tuple[float, float] = (0.5, 0.5),
    label_h: int = 72,
    source_crop: tuple[int, int, int, int] | None = None,
    hero: bool = False,
) -> None:
    draw_panel_shell(canvas, box, accent=panel.accent)
    draw = ImageDraw.Draw(canvas)
    x0, y0, x1, y1 = box
    pad = 13
    image_box = (x0 + pad, y0 + pad, x1 - pad, y1 - pad)
    image_size = (image_box[2] - image_box[0], image_box[3] - image_box[1])
    image = load_image(panel.path)
    fitted = (
        fit_cover(image, image_size, anchor=anchor, source_crop=source_crop)
        if mode == "cover"
        else fit_contain(image, image_size)
    )
    paste_rounded(canvas, fitted, image_box, 5)
    draw.rounded_rectangle(image_box, radius=5, outline=SOFT_LINE, width=1)

    label_y0 = image_box[3] - label_h
    draw.rounded_rectangle(
        (image_box[0], label_y0, image_box[2], image_box[3]),
        radius=5,
        fill=(252, 251, 247, 238),
    )
    draw.rectangle((image_box[0], label_y0, image_box[0] + 8, image_box[3]), fill=panel.accent)
    title_font = F_HERO if hero else F_PANEL
    draw.text((image_box[0] + 22, label_y0 + 13), panel.title, font=title_font, fill=INK)
    draw.text((image_box[0] + 22, label_y0 + 44), panel.source, font=F_BODY, fill=MUTED)
    badge_x = image_box[2] - (248 if panel.kind.startswith("TRUE") else 178)
    draw_badge(draw, (badge_x, label_y0 + 16), panel.kind, panel.accent)


def draw_zoom_strip(canvas: Image.Image, zooms: list[Panel], box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    draw_panel_shell(canvas, box, fill=PANEL_BG_ALT, accent=PBR)
    draw = ImageDraw.Draw(canvas)
    draw.text((x0 + 32, y0 + 28), "Zoom-in mesh evidence", font=F_PANEL, fill=INK)
    draw.text((x0 + 32, y0 + 60), "programmatic PBR material, not Trellis2 texture", font=F_BODY, fill=MUTED)
    draw_badge(draw, (x0 + 32, y0 + 98), "PBR fallback", PBR)

    z_gap = 34
    z_w = 784
    z_h = 286
    z_x = x0 + 500
    z_y = y0 + 42
    for idx, panel in enumerate(zooms):
        zx = z_x + idx * (z_w + z_gap)
        image = fit_cover(load_image(panel.path), (z_w, z_h), anchor=(0.5, 0.5))
        paste_rounded(canvas, image, (zx, z_y, zx + z_w, z_y + z_h), 5)
        draw.rounded_rectangle((zx, z_y, zx + z_w, z_y + z_h), radius=5, outline=(198, 190, 176), width=2)
        draw.rectangle((zx, z_y + z_h - 42, zx + z_w, z_y + z_h), fill=(252, 251, 247, 232))
        draw.text((zx + 16, z_y + z_h - 32), panel.title, font=F_BODY, fill=INK)
        if idx < len(zooms) - 1:
            ax = zx + z_w + 9
            ay = z_y + z_h // 2
            draw.line((ax, ay, ax + 18, ay), fill=(126, 132, 127), width=3)
            draw.polygon([(ax + 24, ay), (ax + 12, ay - 7), (ax + 12, ay + 7)], fill=(126, 132, 127))


def main() -> None:
    true_a = ROOT / "visuals/public_guide_textured_glb_20260509/renders"
    true_c = ROOT / "visuals/public_guide_textured_glb_20260509c/renders"
    true_d = ROOT / "visuals/public_guide_textured_glb_20260509d/renders"
    zoom_dir = ROOT / "visuals/vine_zoom_in_multiscale_20260509"

    hero = Panel(
        "Recursive Vine",
        "true Trellis2 textured GLB render",
        true_a / "vine_parthenocissus_iso.png",
        "TRUE Trellis2 GLB",
        TRUE,
    )
    true_panels = [
        Panel("Tree Roots", "true Trellis2 textured GLB render", true_a / "tree_roots_iso.png", "TRUE Trellis2 GLB", TRUE),
        Panel("L-system Fork", "true Trellis2 textured GLB render", true_c / "lsystem_parthenocissus_iso.png", "TRUE Trellis2 GLB", TRUE),
        Panel("Radial Copy", "true Trellis2 textured GLB render", true_c / "radial_pyrite_iso.png", "TRUE Trellis2 GLB", TRUE),
        Panel("Portal Gear", "true Trellis2 textured GLB render", true_c / "portal_gear_iso.png", "TRUE Trellis2 GLB", TRUE),
        Panel("DLA Branch", "true Trellis2 textured GLB render", true_d / "dla_fork_pyrite_iso.png", "TRUE Trellis2 GLB", TRUE),
        Panel("Sci-fi Module", "true Trellis2 textured GLB render", true_a / "scifi_gear_iso.png", "TRUE Trellis2 GLB", TRUE),
    ]
    zooms = [
        Panel("A overview", "Blender/Cycles mesh render", zoom_dir / "A_overview.png", "PBR fallback", PBR),
        Panel("B branch recursion", "Blender/Cycles mesh render", zoom_dir / "B_branch_zoom.png", "PBR fallback", PBR),
        Panel("C terminal detail", "Blender/Cycles mesh render", zoom_dir / "C_tip_zoom.png", "PBR fallback", PBR),
    ]

    canvas = Image.new("RGBA", (3200, 1700), BG + (255,))
    draw = ImageDraw.Draw(canvas)

    draw.text((72, 38), "MESH-BASED TEASER CANDIDATE V3", font=F_KICKER, fill=TRUE)
    draw.text((72, 66), "True textured GLB results dominate the layout; PBR renders are isolated as geometry zoom evidence.", font=F_BODY, fill=MUTED)
    draw_badge(draw, (2520, 45), "TRUE Trellis2 GLB", TRUE)
    draw_badge(draw, (2795, 45), "PBR fallback", PBR)
    draw.line((72, 112, 3128, 112), fill=(211, 209, 199), width=2)

    draw_labeled_panel(
        canvas,
        hero,
        (72, 145, 1150, 1220),
        mode="cover",
        anchor=(0.5, 0.47),
        label_h=82,
        hero=True,
    )

    grid_x = 1188
    grid_y = 145
    cell_w = 628
    cell_h = 522
    gap_x = 30
    gap_y = 30
    for idx, panel in enumerate(true_panels):
        col = idx % 3
        row = idx // 3
        x0 = grid_x + col * (cell_w + gap_x)
        y0 = grid_y + row * (cell_h + gap_y)
        draw_labeled_panel(
            canvas,
            panel,
            (x0, y0, x0 + cell_w, y0 + cell_h),
            mode="cover",
            anchor=(0.5, 0.55),
            label_h=68,
        )

    draw_zoom_strip(canvas, zooms, (72, 1262, 3128, 1620))
    draw.text(
        (74, 1650),
        "All panels are mesh render composites from existing local assets. No matplotlib point-cloud previews are used.",
        font=F_SMALL,
        fill=MUTED,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUT, quality=95, dpi=(300, 300))
    print(OUT)


if __name__ == "__main__":
    main()
