#!/usr/bin/env python3
"""Compose textured-mesh guide-sweep contact sheets for paper QA."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


TITLE = font(46, True)
SUBTITLE = font(21)
H2 = font(27, True)
BODY = font(20)
SMALL = font(16)
TINY = font(14)

BG = (244, 242, 238)
TEXT = (31, 34, 36)
MUTED = (88, 93, 97)
GREEN = (43, 126, 90)
BROWN = (151, 104, 45)
BLUE = (47, 88, 124)
RED = (143, 58, 55)
LINE = (204, 199, 190)
WHITE = (252, 251, 248)


def read_metrics(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as f:
        return {row["label"]: row for row in csv.DictReader(f)}


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt, width: int, fill=TEXT, gap=4) -> int:
    x, y = xy
    lines: list[str] = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
        words = para.split()
        cur = ""
        for word in words:
            test = word if not cur else f"{cur} {word}"
            if draw.textbbox((0, 0), test, font=fnt)[2] <= width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + gap
    return y


def fit_image(path: Path, box: tuple[int, int], crop: bool = True) -> Image.Image:
    if not path.exists():
        img = Image.new("RGB", box, (226, 223, 216))
        d = ImageDraw.Draw(img)
        d.text((20, box[1] // 2 - 12), "missing render", fill=RED, font=BODY)
        return img
    img = Image.open(path).convert("RGB")
    bw, bh = box
    iw, ih = img.size
    scale = max(bw / iw, bh / ih) if crop else min(bw / iw, bh / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max((nw - bw) // 2, 0)
    top = max((nh - bh) // 2, 0)
    return img.crop((left, top, left + bw, top + bh))


def metric_line(row: dict[str, str]) -> tuple[str, tuple[int, int, int]]:
    if not row:
        return "metrics pending", RED
    comp = row.get("primary_component_count") or row.get("occupancy_component_count_6n") or "?"
    lcr = row.get("primary_largest_component_ratio") or row.get("largest_occupancy_component_ratio_6n") or "?"
    face = row.get("component_count") or "?"
    try:
        lcr_text = f"{float(lcr):.3f}"
    except Exception:
        lcr_text = str(lcr)
    color = GREEN if str(comp) == "1" and lcr_text.startswith("1.000") else BROWN
    return f"Occ comp {comp} / LCR {lcr_text}; raw face comps {face}", color


def compose(
    title: str,
    subtitle: str,
    cases: list[dict],
    metrics: dict[str, dict[str, str]],
    out_png: Path,
    footer: str,
) -> None:
    w, h = 2200, 1450
    margin = 74
    card_gap = 26
    card_w = (w - 2 * margin - card_gap * (len(cases) - 1)) // len(cases)
    card_h = 1065
    image_h = 360
    image_w = card_w - 54
    im = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(im)
    draw.text((margin, 48), title, font=TITLE, fill=TEXT)
    draw_wrapped(draw, (margin, 112), subtitle, SUBTITLE, w - 2 * margin, MUTED, 5)
    draw.line((margin, 160, w - margin, 160), fill=LINE, width=2)

    y0 = 210
    for idx, case in enumerate(cases):
        x0 = margin + idx * (card_w + card_gap)
        accent = case.get("accent", BLUE)
        draw.rounded_rectangle((x0, y0, x0 + card_w, y0 + card_h), radius=10, fill=WHITE, outline=LINE, width=1)
        draw.rectangle((x0, y0, x0 + 8, y0 + card_h), fill=accent)
        draw.text((x0 + 26, y0 + 26), case["title"], font=H2, fill=TEXT)
        metric, metric_color = metric_line(metrics.get(case["metric"], {}))
        draw_wrapped(draw, (x0 + 26, y0 + 64), metric, BODY, card_w - 52, metric_color, 3)
        draw_wrapped(draw, (x0 + 26, y0 + 116), case["note"], SMALL, card_w - 54, MUTED, 3)

        iso = fit_image(ROOT / case["iso"], (image_w, image_h))
        front = fit_image(ROOT / case["front"], (image_w, image_h))
        im.paste(iso, (x0 + 27, y0 + 210))
        draw.text((x0 + 31, y0 + 210), "iso", font=TINY, fill=(235, 234, 230))
        im.paste(front, (x0 + 27, y0 + 594))
        draw.text((x0 + 31, y0 + 594), "front", font=TINY, fill=(235, 234, 230))
        draw_wrapped(draw, (x0 + 26, y0 + 985), case["verdict"], SMALL, card_w - 54, accent, 3)

    draw_wrapped(draw, (margin, h - 112), footer, SUBTITLE, w - 2 * margin, MUTED, 4)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_png)
    im.save(out_png.with_suffix(".pdf"), "PDF", resolution=300.0)
    print(out_png)


def crystal() -> None:
    metrics = read_metrics(ROOT / "results/crystal_stage4_guide_sweep_metrics_20260509/metrics.csv")
    cases = [
        {
            "title": "Bismuth edge",
            "metric": "bismuth_edge",
            "iso": "visuals/crystal_stage4_guide_sweep_20260509/renders/bismuth_edge_iso.png",
            "front": "visuals/crystal_stage4_guide_sweep_20260509/renders/bismuth_edge_front.png",
            "note": "Same connected stage-4 hopper scaffold; edge-processed bismuth guide.",
            "verdict": "candidate if visual edge texture reads cleaner",
            "accent": GREEN,
        },
        {
            "title": "Bismuth warm",
            "metric": "bismuth_warm",
            "iso": "visuals/crystal_stage4_guide_sweep_20260509/renders/bismuth_warm_iso.png",
            "front": "visuals/crystal_stage4_guide_sweep_20260509/renders/bismuth_warm_front.png",
            "note": "Same geometry and schedule; warmer mineral color guide.",
            "verdict": "candidate if material contrast improves",
            "accent": GREEN,
        },
        {
            "title": "Pyrite edge",
            "metric": "pyrite_edge",
            "iso": "visuals/crystal_stage4_guide_sweep_20260509/renders/pyrite_edge_iso.png",
            "front": "visuals/crystal_stage4_guide_sweep_20260509/renders/pyrite_edge_front.png",
            "note": "Same connected stage-4 lattice scaffold; edge-processed pyrite guide.",
            "verdict": "supporting only; dense lattice remains visually busy",
            "accent": BROWN,
        },
        {
            "title": "Pyrite warm",
            "metric": "pyrite_warm",
            "iso": "visuals/crystal_stage4_guide_sweep_20260509/renders/pyrite_warm_iso.png",
            "front": "visuals/crystal_stage4_guide_sweep_20260509/renders/pyrite_warm_front.png",
            "note": "Same geometry and schedule; warm pyrite guide.",
            "verdict": "supporting only unless zoom clarifies lattice",
            "accent": BROWN,
        },
    ]
    compose(
        "Crystal-inspired stage-4 guide sweep",
        "All panels use connected scaffold meshes and true Trellis2 textured GLB exports; only the material guide changes within each scaffold family.",
        cases,
        metrics,
        ROOT / "paper_siga/figures/crystal_stage4_guide_sweep_20260509.png",
        "Strict reading: these are crystal-inspired connected scaffolds, not physical crystal-growth simulations or clean raw-face topology proofs.",
    )


def vine_stage5() -> None:
    metrics = read_metrics(ROOT / "results/vine_stage5_guide_sweep_metrics_20260509/metrics.csv")
    cases = [
        {
            "title": "Parthenocissus square",
            "metric": "parthenocissus_square",
            "iso": "visuals/vine_stage5_guide_sweep_20260509/renders/parthenocissus_square_iso.png",
            "front": "visuals/vine_stage5_guide_sweep_20260509/renders/parthenocissus_square_front.png",
            "note": "Depth-5 vine mesh, same projection state; square tendril guide.",
            "verdict": "primary candidate if readable after zoom",
            "accent": GREEN,
        },
        {
            "title": "Parthenocissus warm",
            "metric": "parthenocissus_warm",
            "iso": "visuals/vine_stage5_guide_sweep_20260509/renders/parthenocissus_warm_iso.png",
            "front": "visuals/vine_stage5_guide_sweep_20260509/renders/parthenocissus_warm_front.png",
            "note": "Same mesh and schedule; warmer tendril guide.",
            "verdict": "candidate if material is less noisy",
            "accent": GREEN,
        },
        {
            "title": "Parthenocissus edge",
            "metric": "parthenocissus_edge",
            "iso": "visuals/vine_stage5_guide_sweep_20260509/renders/parthenocissus_edge_iso.png",
            "front": "visuals/vine_stage5_guide_sweep_20260509/renders/parthenocissus_edge_front.png",
            "note": "Same mesh and schedule; edge guide tests texture crispness.",
            "verdict": "candidate if tendrils remain visible",
            "accent": GREEN,
        },
        {
            "title": "Tree roots guide",
            "metric": "tree_roots_square",
            "iso": "visuals/vine_stage5_guide_sweep_20260509/renders/tree_roots_square_iso.png",
            "front": "visuals/vine_stage5_guide_sweep_20260509/renders/tree_roots_square_front.png",
            "note": "Same depth-5 geometry with a root/bark appearance guide.",
            "verdict": "material alternative, not a new geometry case",
            "accent": BROWN,
        },
    ]
    compose(
        "Depth-5 vine guide sweep",
        "Same stage-5 projected vine mesh, same Trellis2 schedule, and fixed Blender camera; only the guide image changes.",
        cases,
        metrics,
        ROOT / "paper_siga/figures/vine_stage5_guide_sweep_20260509.png",
        "Strict reading: this closes the depth-5 visual/export gap for the vine metric claim, but it is a guide sweep, not an ablation.",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--which", choices=["crystal", "vine-stage5", "all"], default="all")
    args = parser.parse_args()
    if args.which in {"crystal", "all"}:
        crystal()
    if args.which in {"vine-stage5", "all"}:
        vine_stage5()


if __name__ == "__main__":
    main()
