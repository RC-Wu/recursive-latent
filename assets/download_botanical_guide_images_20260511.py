#!/usr/bin/env python3
"""Download license-tracked botanical guide images for the 20260511 loop."""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw


COMMONS_API = "https://commons.wikimedia.org/w/api.php"


@dataclass(frozen=True)
class CommonsGuide:
    key: str
    title: str
    category: str
    use: str
    preferred_crop: str = "center"


GUIDES = [
    CommonsGuide(
        "spider_plant_commons_pd",
        "File:Chlorophytum comosum.png",
        "spider_plant",
        "public-domain spider plant rosette/root silhouette seed",
    ),
    CommonsGuide(
        "spider_plants_cc0_photo",
        "File:Spider plants (Chlorophytum comosum).jpg",
        "spider_plant",
        "CC0 spider-plant rosette photo seed with natural leaf mass",
    ),
    CommonsGuide(
        "fiddlehead_ferns_cc0",
        "File:Fiddlehead-ferns.jpg",
        "fern_crozier",
        "CC0 fiddlehead/crozier seed for recursive curl roots",
    ),
    CommonsGuide(
        "rubber_fig_aerial_roots_cc0",
        "File:Rubber fig (Ficus elastica) aerial roots.jpg",
        "aerial_roots",
        "CC0 aerial-root seed for thick-to-thin dangling root recursion",
        "vertical",
    ),
    CommonsGuide(
        "beech_aerial_roots_pd",
        "File:Beech Aerial Roots.JPG",
        "aerial_roots",
        "public-domain aerial roots on trunk contact seed",
        "vertical",
    ),
    CommonsGuide(
        "root_bound_spider_plant_ccby2",
        "File:Root-bound Chlorophytum comosum.jpg",
        "spider_roots",
        "CC-BY exposed spider-plant root mass seed; attribution required",
    ),
    CommonsGuide(
        "golden_spiral_fiddlehead_ccby4",
        "File:Golden spiral in a fiddlehead fern.jpg",
        "fern_crozier",
        "CC-BY 4.0 high-semantic spiral fiddlehead seed; attribution required",
    ),
]


def strip_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", value).strip()


def request_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "r-slg-botanical-guides/0.1"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def download(url: str, path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "r-slg-botanical-guides/0.1"})
    with urllib.request.urlopen(req, timeout=180) as response:
        path.write_bytes(response.read())


def commons_info(title: str, thumb_width: int) -> dict:
    params = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "titles": title,
        "iiprop": "url|extmetadata",
        "iiurlwidth": str(thumb_width),
    }
    data = request_json(COMMONS_API + "?" + urllib.parse.urlencode(params))
    page = next(iter(data["query"]["pages"].values()))
    if "missing" in page:
        raise RuntimeError(f"Commons file not found: {title}")
    imageinfo = page.get("imageinfo", [{}])[0]
    meta = imageinfo.get("extmetadata", {})
    return {
        "title": title,
        "descriptionurl": imageinfo.get("descriptionurl"),
        "url": imageinfo.get("url"),
        "thumburl": imageinfo.get("thumburl"),
        "artist": strip_html(meta.get("Artist", {}).get("value", "")),
        "license_short": strip_html(meta.get("LicenseShortName", {}).get("value", "")),
        "license_url": meta.get("LicenseUrl", {}).get("value", ""),
        "credit": strip_html(meta.get("Credit", {}).get("value", "")),
    }


def condition_square(image: Image.Image, size: int, crop_mode: str) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    width, height = image.size
    if crop_mode == "vertical" and height > width:
        side = width
        left = 0
        top = max(0, int((height - side) * 0.18))
    else:
        side = min(width, height)
        left = (width - side) // 2
        top = (height - side) // 2
    crop = image.crop((left, top, left + side, top + side))
    crop = crop.resize((size, size), Image.Resampling.LANCZOS)
    crop = ImageEnhance.Color(crop).enhance(1.08)
    crop = ImageEnhance.Contrast(crop).enhance(1.10)
    crop = ImageEnhance.Sharpness(crop).enhance(1.12)
    return crop


def edge_condition(square: Image.Image) -> Image.Image:
    gray = ImageOps.grayscale(square)
    gray = ImageOps.autocontrast(gray)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.autocontrast(edges)
    edges = ImageEnhance.Contrast(edges).enhance(1.7)
    return ImageOps.colorize(edges, black="#f8faf8", white="#18231b").convert("RGB")


def make_contact(rows: list[dict], path: Path) -> None:
    tile_w, tile_h = 344, 408
    cols = 3
    sheet = Image.new("RGB", (tile_w * cols, tile_h * ((len(rows) + cols - 1) // cols)), "#fbfcfb")
    draw = ImageDraw.Draw(sheet)
    for idx, row in enumerate(rows):
        image = Image.open(row["condition_image"]).convert("RGB")
        image.thumbnail((300, 300), Image.Resampling.LANCZOS)
        x = (idx % cols) * tile_w
        y = (idx // cols) * tile_h
        sheet.paste(image, (x + (tile_w - image.width) // 2, y + 48))
        draw.text((x + 18, y + 14), row["key"], fill="#1f2620")
        draw.text((x + 18, y + 330), row["category"], fill="#5b655c")
        draw.text((x + 18, y + 352), row["license_short"] or "unknown", fill="#5b655c")
    sheet.save(path, quality=95)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("downloads/botanical_guides_20260511"))
    parser.add_argument("--thumb-width", type=int, default=2200)
    parser.add_argument("--size", type=int, default=1024)
    args = parser.parse_args()

    raw_dir = args.out / "raw"
    processed_dir = args.out / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for guide in GUIDES:
        info = commons_info(guide.title, args.thumb_width)
        url = info.get("thumburl") or info.get("url")
        if not url:
            raise RuntimeError(f"No image URL for {guide.title}")
        ext = Path(urllib.parse.urlparse(url).path).suffix or ".jpg"
        raw_path = raw_dir / f"{guide.key}{ext.lower()}"
        download(url, raw_path)
        image = Image.open(raw_path)
        condition = condition_square(image, args.size, guide.preferred_crop)
        condition_path = processed_dir / f"{guide.key}_condition_{args.size}.png"
        edge_path = processed_dir / f"{guide.key}_edge_{args.size}.png"
        condition.save(condition_path)
        edge_condition(condition).save(edge_path)
        row = {
            **info,
            "key": guide.key,
            "category": guide.category,
            "use": guide.use,
            "raw_path": str(raw_path),
            "condition_image": str(condition_path),
            "edge_image": str(edge_path),
            "crop_mode": guide.preferred_crop,
        }
        rows.append(row)
        time.sleep(0.25)

    manifest = {"created_for": "R-SLG botanical/tree-root recursion 20260511", "rows": rows}
    (args.out / "manifest_botanical_guides_20260511.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    make_contact(rows, args.out / "botanical_guide_contact_sheet_20260511.png")
    print(json.dumps({"out": str(args.out), "count": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
