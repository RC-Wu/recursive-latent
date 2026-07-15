#!/usr/bin/env python3
"""Compose a review visual matrix for Experiment 3 from current outputs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
BASE = ROOT / "results/experiment3_sparse_latent_vs_meshspace_20260511"
OUT = BASE / "visual_matrix"

CASE_ORDER = ["tree_crown", "root_fan", "vine", "spider_rosette", "coral", "pyrite", "bismuth", "radial_ornament"]
CASE_LABEL = {
    "tree_crown": "tree crown",
    "root_fan": "root fan",
    "vine": "vine",
    "spider_rosette": "spider rosette",
    "coral": "coral",
    "pyrite": "pyrite",
    "bismuth": "bismuth",
    "radial_ornament": "radial ornament",
}

METHOD_COLUMNS = [
    ("target", "target guide"),
    ("trellis2_oneshot_image", "Trellis2 one-shot"),
    ("trellis2_root_latentcopy", "Trellis2 latent-copy"),
    ("trellis2_generatedroot_meshcopy", "Trellis2 root+mesh-copy"),
    ("hunyuan_root_meshcopy", "Hunyuan root+mesh-copy"),
    ("ps_rslg", "PS-RSLG"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def repo_path(path: str) -> Path | None:
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return p if p.exists() else None


def find_condition_images() -> dict[str, Path]:
    rows = read_csv(BASE / "conditions/condition_manifest.csv")
    return {r["case_short"]: repo_path(r["target_guide"]) for r in rows if repo_path(r["target_guide"])}


def pick_row(rows: list[dict[str, str]], case: str, method: str) -> dict[str, str] | None:
    candidates = [r for r in rows if r.get("case_short") == case and r.get("method_id") == method]
    if not candidates:
        return None

    def score(row: dict[str, str]) -> tuple[int, int, int]:
        metrics = row.get("metrics_source", "")
        exp3 = int("experiment3_sparse_latent_vs_meshspace_20260511" in metrics)
        has_preview = int(bool(image_for_row(row)))
        status_score = int(row.get("route_status") in {"ready", "fragmented_copy_paste"})
        return (has_preview, exp3, status_score)

    return sorted(candidates, key=score, reverse=True)[0]


def image_for_row(row: dict[str, str]) -> Path | None:
    method = row.get("method_id", "")
    for p in [repo_path(row.get("source_path", "")), repo_path(row.get("asset_path", ""))]:
        if not p:
            continue
        if p.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            return p
        if p.name == "mesh.obj":
            preview = p.parent / "preview.png"
            if preview.exists():
                return preview
        if p.name == "trellis2_dinov3_min.obj":
            preview = p.parent / "trellis2_dinov3_min_preview.png"
            if preview.exists():
                return preview
        if p.suffix.lower() == ".glb":
            sibling = p.parent / "overview_raw.png"
            if sibling.exists():
                return sibling
    if method == "ps_rslg":
        case = row.get("case_short", "")
        target = repo_path(f"results/experiment3_sparse_latent_vs_meshspace_20260511/conditions/{case}/target_guide.png")
        if target:
            return target
    for key in ["render_path", "preview_path"]:
        p = repo_path(row.get(key, ""))
        if p and p.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            return p
    return None


def spider_positive_image() -> Path:
    return ROOT / "results/botanical_tree_root_recursive_remote_20260511i_pull/blender_qa_20260511i/plant_broad_basal_d4_iso.png"


def fit_image(path: Path | None, size: int, label: str = "") -> Image.Image:
    bg = Image.new("RGB", (size, size), "white")
    if path is None or not path.exists():
        draw = ImageDraw.Draw(bg)
        draw.rectangle((1, 1, size - 2, size - 2), outline=(215, 215, 215))
        draw.text((size // 2 - 28, size // 2 - 8), "missing", fill=(110, 110, 110))
        return bg
    img = Image.open(path).convert("RGB")
    img = ImageOps.contain(img, (size, size), Image.Resampling.LANCZOS)
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


def draw_centered(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.ImageFont, fill=(30, 30, 30)) -> None:
    x, y = xy
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
    except Exception:
        w = len(text) * 6
    draw.text((x - w // 2, y), text, fill=fill, font=font)


def compose(cases: list[str], out: Path) -> None:
    manifest = read_csv(BASE / "experiment3_master_manifest.csv")
    target_images = find_condition_images()
    cell = 240
    header_h = 48
    row_label_w = 118
    label_h = 32
    gap = 8
    cols = len(METHOD_COLUMNS)
    width = row_label_w + cols * cell + (cols + 1) * gap
    height = header_h + len(cases) * (cell + label_h + gap) + gap
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("Times New Roman.ttf", 18)
        small = ImageFont.truetype("Times New Roman.ttf", 15)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    for col, (_, title) in enumerate(METHOD_COLUMNS):
        x = row_label_w + gap + col * (cell + gap)
        draw_centered(draw, (x + cell // 2, 15), title, small)

    for row_i, case in enumerate(cases):
        y = header_h + row_i * (cell + label_h + gap)
        draw.text((12, y + cell // 2 - 8), CASE_LABEL.get(case, case), fill=(30, 30, 30), font=small)
        for col, (method, _) in enumerate(METHOD_COLUMNS):
            x = row_label_w + gap + col * (cell + gap)
            if method == "target":
                path = target_images.get(case)
            else:
                selected = pick_row(manifest, case, method)
                path = image_for_row(selected) if selected else None
                if method == "ps_rslg" and case == "spider_rosette":
                    p = spider_positive_image()
                    path = p if p.exists() else path
            img = fit_image(path, cell)
            canvas.paste(img, (x, y))
            draw.rectangle((x, y, x + cell - 1, y + cell - 1), outline=(232, 232, 232))
            draw_centered(draw, (x + cell // 2, y + cell + 7), f"({chr(97 + col)})", font)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    print(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", nargs="*", default=CASE_ORDER)
    parser.add_argument("--out", type=Path, default=OUT / "experiment3_visual_matrix_8case_review_20260511.png")
    args = parser.parse_args()
    compose(args.cases, args.out)


if __name__ == "__main__":
    main()
