from __future__ import annotations

import argparse
import json
import re
import textwrap
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw


COMMONS_API = "https://commons.wikimedia.org/w/api.php"


@dataclass(frozen=True)
class GuideSpec:
    key: str
    title: str
    category: str
    use: str


GUIDES = [
    GuideSpec(
        "tree_roots_arlington",
        "File:Tree roots - Arlington, MA.jpg",
        "plant_root",
        "root branching structure and bark/soil color reference",
    ),
    GuideSpec(
        "spiky_plant_tendril",
        "File:Spiky plant tendril.jpg",
        "vine_tendril",
        "thin spiral tendril and small protrusion reference",
    ),
    GuideSpec(
        "parthenocissus_tendrils",
        "File:Parthenocissus quinquefolia tendrils in summer.jpg",
        "vine_tendril",
        "multi-branch tendril attachment reference",
    ),
    GuideSpec(
        "washington_square_arch",
        "File:Washington Square Arch, New York.jpg",
        "portal_arch",
        "symmetric portal/arch root guide",
    ),
    GuideSpec(
        "pyrite_cubes",
        "File:Pyrite Cubes.JPG",
        "crystal_metal",
        "faceted metallic crystal and cubic growth reference",
    ),
    GuideSpec(
        "bismuth_crystal",
        "File:Bi-crystal.jpg",
        "crystal_iridescent",
        "stepped recursive crystal and iridescent material reference",
    ),
    GuideSpec(
        "gear_train",
        "File:Gear Train.jpg",
        "mechanical",
        "radial gear repetition and metal material reference",
    ),
    GuideSpec(
        "octopus_suckers",
        "File:Suckers of octopus by steve lodefink.jpg",
        "organic_tentacle",
        "repeated suction-cup texture and glossy organic surface reference",
    ),
]


def request_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "recursive-growth-research/0.1"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def download(url: str, path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "recursive-growth-research/0.1"})
    with urllib.request.urlopen(req, timeout=120) as response:
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
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    imageinfo = page.get("imageinfo", [{}])[0]
    meta = imageinfo.get("extmetadata", {})
    return {
        "title": title,
        "pageid": page.get("pageid"),
        "descriptionurl": imageinfo.get("descriptionurl"),
        "url": imageinfo.get("url"),
        "thumburl": imageinfo.get("thumburl"),
        "artist": strip_html(meta.get("Artist", {}).get("value", "")),
        "license_short": strip_html(meta.get("LicenseShortName", {}).get("value", "")),
        "license_url": meta.get("LicenseUrl", {}).get("value", ""),
        "credit": strip_html(meta.get("Credit", {}).get("value", "")),
    }


def strip_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def fit_square(image: Image.Image, size: int = 768) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    crop = image.crop((left, top, left + side, top + side))
    return crop.resize((size, size), Image.Resampling.LANCZOS)


def edge_variant(square: Image.Image) -> Image.Image:
    gray = ImageOps.grayscale(square)
    gray = ImageOps.autocontrast(gray)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.autocontrast(edges)
    edges = ImageEnhance.Contrast(edges).enhance(1.8)
    return ImageOps.colorize(edges, black="#f8f5ed", white="#17212b").convert("RGB")


def warm_contrast_variant(square: Image.Image) -> Image.Image:
    image = ImageEnhance.Color(square).enhance(1.12)
    image = ImageEnhance.Contrast(image).enhance(1.08)
    image = ImageEnhance.Sharpness(image).enhance(1.15)
    return image


def make_contact(rows: list[dict], out_path: Path) -> None:
    tile_w, tile_h = 330, 388
    cols = 4
    rows_n = (len(rows) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tile_w, rows_n * tile_h), "#fbfaf7")
    draw = ImageDraw.Draw(sheet)
    for idx, row in enumerate(rows):
        image = Image.open(row["square_path"]).convert("RGB")
        image.thumbnail((286, 286), Image.Resampling.LANCZOS)
        x0 = (idx % cols) * tile_w
        y0 = (idx // cols) * tile_h
        sheet.paste(image, (x0 + (tile_w - image.width) // 2, y0 + 48))
        draw.text((x0 + 18, y0 + 15), row["key"].replace("_", " "), fill="#20242a")
        draw.text((x0 + 18, y0 + 325), row["category"], fill="#57606a")
        draw.text((x0 + 18, y0 + 346), row.get("license_short", ""), fill="#57606a")
    sheet.save(out_path, quality=95)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--thumb-width", type=int, default=1800)
    parser.add_argument("--size", type=int, default=768)
    args = parser.parse_args()

    raw_dir = args.out / "raw"
    processed_dir = args.out / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for spec in GUIDES:
        info = commons_info(spec.title, args.thumb_width)
        url = info.get("thumburl") or info.get("url")
        if not url:
            raise RuntimeError(f"No image URL found for {spec.title}")
        ext = Path(urllib.parse.urlparse(url).path).suffix.lower() or ".jpg"
        raw_path = raw_dir / f"{spec.key}{ext}"
        download(url, raw_path)

        image = Image.open(raw_path)
        square = fit_square(image, args.size)
        square_path = processed_dir / f"{spec.key}_square.png"
        warm_path = processed_dir / f"{spec.key}_warm.png"
        edge_path = processed_dir / f"{spec.key}_edge.png"
        square.save(square_path)
        warm_contrast_variant(square).save(warm_path)
        edge_variant(square).save(edge_path)
        row = {
            **info,
            "key": spec.key,
            "category": spec.category,
            "use": spec.use,
            "raw_path": str(raw_path),
            "square_path": str(square_path),
            "warm_path": str(warm_path),
            "edge_path": str(edge_path),
        }
        rows.append(row)
        time.sleep(0.3)

    (args.out / "public_guide_manifest.json").write_text(
        json.dumps({"rows": rows}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    make_contact(rows, args.out / "public_guide_contact_sheet.png")
    md_lines = [
        "# Public Guide Image Attribution Table",
        "",
        "| key | category | source | license | local processed guide | intended use |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        md_lines.append(
            "| {key} | {category} | [Commons]({source}) | [{license}]({license_url}) | `{guide}` | {use} |".format(
                key=row["key"],
                category=row["category"],
                source=row.get("descriptionurl") or row.get("url"),
                license=row.get("license_short") or "unknown",
                license_url=row.get("license_url") or row.get("descriptionurl") or row.get("url"),
                guide=row["square_path"],
                use=row["use"],
            )
        )
    (args.out / "public_guide_attribution.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "count": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
