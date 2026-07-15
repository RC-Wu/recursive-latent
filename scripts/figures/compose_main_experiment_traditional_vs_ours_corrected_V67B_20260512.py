#!/usr/bin/env python3
"""Compose the corrected V67B traditional-vs-ours zoom matrix."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WHITE = (255, 255, 255)
INK = (26, 28, 30)
MUTED = (92, 96, 100)
RULE = (212, 216, 220)


FAMILIES = [
    ("Space colonization", "SC_baseline_tree_canopy", "SC_ours_V32_balanced_canopy_D"),
    ("L-system", "LSystem_baseline_OBJ_neutral_upright", "LSystem_ours_V67_tapered_dense_B"),
    ("DLA / frontier", "DLA_baseline_cluster", "DLA_ours_V8_lace_reef_coral_A"),
    ("IFS / transform", "IFS_baseline_matched_branch_tree", "IFS_ours_V21_branch_tree_natural_bark"),
]


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def flatten(path: Path) -> Image.Image:
    src = Image.open(path).convert("RGBA")
    base = Image.new("RGBA", src.size, WHITE + (255,))
    base.alpha_composite(src)
    return base.convert("RGB")


def crop_content(image: Image.Image, pad_ratio: float = 0.045) -> Image.Image:
    gray = image.convert("L")
    mask = gray.point(lambda px: 255 if px < 248 else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return image
    pad = max(10, int(max(image.size) * pad_ratio))
    left = max(0, bbox[0] - pad)
    top = max(0, bbox[1] - pad)
    right = min(image.width, bbox[2] + pad)
    bottom = min(image.height, bbox[3] + pad)
    return image.crop((left, top, right, bottom))


def fit_panel(image: Image.Image, size: int, crop: bool) -> Image.Image:
    if crop:
        image = crop_content(image)
    image.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (size, size), WHITE)
    canvas.paste(image, ((size - image.width) // 2, (size - image.height) // 2))
    return canvas


def panel_paths(root: Path, case: str) -> list[Path]:
    case_dir = root / case
    return [
        case_dir / "overview_callouts.png",
        case_dir / "zoom_01_callouts.png",
        case_dir / "zoom_02.png",
    ]


def load_case_panels(root: Path, case: str, panel_size: int, crop: bool) -> list[Image.Image]:
    images: list[Image.Image] = []
    for path in panel_paths(root, case):
        if not path.exists() and path.name == "overview_callouts.png":
            path = path.with_name("overview_raw.png")
        if not path.exists() and path.name == "zoom_01_callouts.png":
            path = path.with_name("zoom_01.png")
        if not path.exists():
            raise FileNotFoundError(path)
        images.append(fit_panel(flatten(path), panel_size, crop))
    return images


def draw_centered(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt, fill=INK) -> None:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0] - (bbox[2] - bbox[0]) / 2, xy[1]), text, font=fnt, fill=fill)


def compose(root: Path, out: Path, panel_size: int, crop_panels: bool) -> None:
    gap = max(20, panel_size // 24)
    family_w = max(230, panel_size // 2)
    margin = max(42, panel_size // 10)
    header_h = max(76, panel_size // 8)
    method_h = max(16, panel_size // 34)
    row_gap = max(30, panel_size // 16)
    cols = 6

    content_w = family_w + gap + cols * panel_size + (cols - 1) * gap
    row_h = method_h + panel_size
    width = margin * 2 + content_w
    height = margin * 2 + header_h + len(FAMILIES) * row_h + (len(FAMILIES) - 1) * row_gap
    canvas = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)

    family_font = font(max(24, panel_size // 25), bold=True)
    method_font = font(max(21, panel_size // 30), bold=True)
    small_font = font(max(17, panel_size // 38))

    x0 = margin + family_w + gap
    for label, start, end in [("Traditional", 0, 3), ("PS-RSLE", 3, 6)]:
        left = x0 + start * (panel_size + gap)
        right = x0 + (end - 1) * (panel_size + gap) + panel_size
        draw_centered(draw, ((left + right) // 2, margin), label, method_font)
    for idx, label in enumerate(["overview", "zoom 1", "zoom 2"] * 2):
        x = x0 + idx * (panel_size + gap)
        draw_centered(draw, (x + panel_size // 2, margin + max(34, panel_size // 20)), label, small_font, fill=MUTED)

    y = margin + header_h
    for row_idx, (family, baseline, ours) in enumerate(FAMILIES):
        if row_idx:
            draw.line((margin, y - row_gap // 2, width - margin, y - row_gap // 2), fill=RULE, width=1)
        draw.text((margin, y + method_h + int(panel_size * 0.37)), family, font=family_font, fill=INK)
        images = load_case_panels(root, baseline, panel_size, crop_panels) + load_case_panels(root, ours, panel_size, crop_panels)
        for idx, image in enumerate(images):
            x = x0 + idx * (panel_size + gap)
            canvas.paste(image, (x, y + method_h))
        y += row_h + row_gap

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--panel-size", type=int, default=390)
    parser.add_argument("--no-crop", action="store_true")
    args = parser.parse_args()
    compose(args.root, args.out, args.panel_size, not args.no_crop)
    print(args.out)
    print(args.out.stat().st_size)


if __name__ == "__main__":
    main()
