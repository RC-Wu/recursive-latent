#!/usr/bin/env python3
"""Prepare low-complexity botanical condition images for the 20260511j loop."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


@dataclass(frozen=True)
class CropSpec:
    key: str
    source: Path
    box_frac: tuple[float, float, float, float]
    category: str
    license_note: str
    purpose: str


def crop_to_square(image: Image.Image, box_frac: tuple[float, float, float, float], size: int) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    w, h = image.size
    l, t, r, b = box_frac
    crop = image.crop((int(l * w), int(t * h), int(r * w), int(b * h)))
    cw, ch = crop.size
    side = max(cw, ch)
    canvas = Image.new("RGB", (side, side), "#f8f8f2")
    canvas.paste(crop, ((side - cw) // 2, (side - ch) // 2))
    canvas = canvas.resize((size, size), Image.Resampling.LANCZOS)
    canvas = ImageEnhance.Color(canvas).enhance(1.08)
    canvas = ImageEnhance.Contrast(canvas).enhance(1.16)
    canvas = ImageEnhance.Sharpness(canvas).enhance(1.08)
    return canvas


def soften_condition(image: Image.Image) -> Image.Image:
    image = image.filter(ImageFilter.MedianFilter(size=3))
    image = ImageEnhance.Contrast(image).enhance(1.05)
    return image


def edge_condition(image: Image.Image) -> Image.Image:
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.autocontrast(edges)
    edges = ImageEnhance.Contrast(edges).enhance(1.25)
    return ImageOps.colorize(edges, black="#fafaf6", white="#203022").convert("RGB")


def make_contact(rows: list[dict], out: Path) -> None:
    cols = 4
    tw, th = 280, 342
    sheet = Image.new("RGB", (cols * tw, ((len(rows) + cols - 1) // cols) * th), "white")
    draw = ImageDraw.Draw(sheet)
    for i, row in enumerate(rows):
        image = Image.open(row["condition_image"]).convert("RGB")
        image.thumbnail((240, 240), Image.Resampling.LANCZOS)
        x = (i % cols) * tw
        y = (i // cols) * th
        sheet.paste(image, (x + (tw - image.width) // 2, y + 32))
        draw.text((x + 12, y + 8), row["key"], fill="#1d251e")
        draw.text((x + 12, y + 276), row["category"], fill="#566052")
        draw.text((x + 12, y + 298), row["license_note"], fill="#566052")
    sheet.save(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--size", type=int, default=768)
    parser.add_argument("--out", type=Path, default=Path("downloads/botanical_guides_20260511j_low_complexity"))
    args = parser.parse_args()

    source_root = args.root / "downloads/botanical_guides_20260511/raw"
    specs = [
        CropSpec(
            "spider_photo_rosette_cc0",
            source_root / "spider_plants_cc0_photo.jpg",
            (0.12, 0.16, 0.86, 0.90),
            "spider_plant",
            "CC0",
            "natural spider plant photo rosette crop",
        ),
        CropSpec(
            "spider_rosette_single_pd",
            source_root / "spider_plant_commons_pd.png",
            (0.48, 0.02, 0.98, 0.46),
            "spider_plant",
            "Public domain",
            "single rosette/plantlet condition, not full hanging plant",
        ),
        CropSpec(
            "spider_runner_child_pd",
            source_root / "spider_plant_commons_pd.png",
            (0.00, 0.48, 0.50, 0.98),
            "spider_plant",
            "Public domain",
            "small runner plantlet condition",
        ),
        CropSpec(
            "rubber_fig_3_7_roots_cc0",
            source_root / "rubber_fig_aerial_roots_cc0.jpg",
            (0.25, 0.06, 0.70, 0.88),
            "aerial_roots",
            "CC0",
            "3-7 aerial roots with trunk contact",
        ),
        CropSpec(
            "rubber_fig_trunk_contact_cc0",
            source_root / "rubber_fig_aerial_roots_cc0.jpg",
            (0.08, 0.00, 0.52, 0.76),
            "aerial_roots",
            "CC0",
            "low-complexity trunk/root attachment",
        ),
        CropSpec(
            "beech_aerial_root_strip_pd",
            source_root / "beech_aerial_roots_pd.jpg",
            (0.05, 0.00, 0.58, 0.86),
            "aerial_roots",
            "Public domain",
            "thin root strip on trunk",
        ),
        CropSpec(
            "fiddlehead_single_curl_cc0",
            source_root / "fiddlehead_ferns_cc0.jpg",
            (0.02, 0.06, 0.58, 0.78),
            "fern_crozier",
            "CC0",
            "single fiddlehead curl",
        ),
    ]

    out = args.root / args.out
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for spec in specs:
        if not spec.source.exists():
            raise FileNotFoundError(spec.source)
        condition = soften_condition(crop_to_square(Image.open(spec.source), spec.box_frac, args.size))
        edge = edge_condition(condition)
        condition_path = out / f"{spec.key}_condition_{args.size}.png"
        edge_path = out / f"{spec.key}_edge_{args.size}.png"
        condition.save(condition_path)
        edge.save(edge_path)
        rows.append(
            {
                "key": spec.key,
                "source": str(spec.source),
                "condition_image": str(condition_path),
                "edge_image": str(edge_path),
                "box_frac": spec.box_frac,
                "category": spec.category,
                "license_note": spec.license_note,
                "purpose": spec.purpose,
            }
        )
    (out / "manifest_botanical_low_complexity_20260511j.json").write_text(
        json.dumps({"created_for": "R-SLG 20260511j low-complexity image roots", "rows": rows}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    make_contact(rows, out / "botanical_low_complexity_contact_20260511j.png")
    print(json.dumps({"out": str(out), "count": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
