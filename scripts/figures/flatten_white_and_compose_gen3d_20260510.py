#!/usr/bin/env python3
"""Flatten transparent render PNGs onto real white and compose clean grids.

The Blender renderers intentionally avoid ground planes.  Older runs emitted
RGBA PNGs with transparent background, which looks black in some viewers.  This
script produces RGB white-background copies and paper-safe grids with only
Times New Roman subfigure labels below panels.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WHITE = (255, 255, 255)
INK = (20, 20, 20)


def times(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/Library/Fonts/Times New Roman.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def flood_white_background(im: Image.Image, tolerance: int = 10) -> Image.Image:
    """Replace the connected corner background with white.

    Blender EEVEE can render a constant gray background even when the world is
    set to white.  We only modify pixels connected to the image boundary whose
    color is close to the corner colors, which preserves dark geometry inside
    the object.
    """
    rgb = im.convert("RGB")
    w, h = rgb.size
    pix = rgb.load()
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    seed_colors = [pix[x, y] for x, y in seeds]

    def close_to_bg(color: tuple[int, int, int]) -> bool:
        return any(max(abs(color[i] - bg[i]) for i in range(3)) <= tolerance for bg in seed_colors)

    stack = list(seeds)
    seen: set[tuple[int, int]] = set()
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or x < 0 or y < 0 or x >= w or y >= h:
            continue
        seen.add((x, y))
        if not close_to_bg(pix[x, y]):
            continue
        pix[x, y] = WHITE
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return rgb


def flatten_image(src: Path, dst: Path, flood_white: bool = False, tolerance: int = 10) -> None:
    im = Image.open(src)
    if im.mode in {"RGBA", "LA"} or ("transparency" in im.info):
        rgba = im.convert("RGBA")
        base = Image.new("RGBA", rgba.size, (*WHITE, 255))
        base.alpha_composite(rgba)
        out = base.convert("RGB")
    else:
        out = im.convert("RGB")
    if flood_white:
        out = flood_white_background(out, tolerance=tolerance)
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst)


def flatten_tree(src_dir: Path, dst_dir: Path, flood_white: bool = False, tolerance: int = 10) -> list[dict]:
    records: list[dict] = []
    for src in sorted(src_dir.rglob("*.png")):
        rel = src.relative_to(src_dir)
        dst = dst_dir / rel
        flatten_image(src, dst, flood_white=flood_white, tolerance=tolerance)
        records.append({"src": str(src), "dst": str(dst)})
    return records


def center_crop(im: Image.Image) -> Image.Image:
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return im.crop((left, top, left + side, top + side))


def pad_fit(im: Image.Image, size: int) -> Image.Image:
    im = center_crop(im).resize((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (size, size), WHITE)
    canvas.paste(im, (0, 0))
    return canvas


def compose_grid(
    cells: list[list[Path | None]],
    out: Path,
    panel_size: int,
    label_prefix: str = "",
) -> None:
    label_font = times(max(24, panel_size // 14))
    gap = max(22, panel_size // 28)
    label_h = max(42, panel_size // 12)
    rows = len(cells)
    cols = max(len(row) for row in cells)
    width = cols * panel_size + (cols - 1) * gap
    height = rows * (panel_size + label_h) + (rows - 1) * gap
    canvas = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    idx = 0
    for r, row in enumerate(cells):
        y = r * (panel_size + label_h + gap)
        for c in range(cols):
            x = c * (panel_size + gap)
            path = row[c] if c < len(row) else None
            if path is not None and path.exists():
                panel = pad_fit(Image.open(path).convert("RGB"), panel_size)
                canvas.paste(panel, (x, y))
            label = f"({chr(ord('a') + idx)})"
            if label_prefix:
                label = f"{label_prefix}{label}"
            bbox = draw.textbbox((0, 0), label, font=label_font)
            draw.text((x + (panel_size - (bbox[2] - bbox[0])) / 2, y + panel_size + 6), label, font=label_font, fill=INK)
            idx += 1
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def compose_from_manifest(manifest: Path, out: Path, panel_size: int) -> None:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    rows: list[list[Path | None]] = []
    base = manifest.parent
    for row in payload["rows"]:
        rows.append([base / cell if cell else None for cell in row])
    compose_grid(rows, out, panel_size=panel_size)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src-dir", type=Path, required=True)
    parser.add_argument("--dst-dir", type=Path, required=True)
    parser.add_argument("--grid-manifest", type=Path)
    parser.add_argument("--grid-out", type=Path)
    parser.add_argument("--panel-size", type=int, default=760)
    parser.add_argument("--flood-white", action="store_true")
    parser.add_argument("--tolerance", type=int, default=10)
    args = parser.parse_args()

    records = flatten_tree(args.src_dir, args.dst_dir, flood_white=args.flood_white, tolerance=args.tolerance)
    (args.dst_dir / "flatten_manifest.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    if args.grid_manifest and args.grid_out:
        compose_from_manifest(args.grid_manifest, args.grid_out, args.panel_size)
    print(json.dumps({"flattened": len(records), "dst_dir": str(args.dst_dir)}, indent=2))


if __name__ == "__main__":
    main()
