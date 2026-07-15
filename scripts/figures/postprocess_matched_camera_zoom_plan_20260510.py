#!/usr/bin/env python3
"""Postprocess Blender camera-zoom renders with callouts and contact sheets.

Blender's bundled Python may not have PIL, so `matched_camera_zoom_render_20260510.py`
can render raw PNGs but skip callouts/comparison sheets.  Run this script with
the system Python after Blender finishes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WHITE = (255, 255, 255)
INK = (24, 26, 28)
ACCENTS = [(196, 60, 52), (45, 112, 185), (40, 138, 86), (155, 88, 178)]


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
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


def draw_callout(parent_path: Path, out_path: Path, rects: list[list[int]], labels: list[str]) -> None:
    im = flatten(parent_path)
    draw = ImageDraw.Draw(im)
    f = font(max(18, im.width // 42), bold=True)
    for idx, rect in enumerate(rects):
        color = ACCENTS[idx % len(ACCENTS)]
        xy = tuple(int(v) for v in rect)
        draw.rectangle(xy, outline=color, width=max(4, im.width // 220))
        label = labels[idx] if idx < len(labels) else f"zoom_{idx+1:02d}"
        tx, ty = xy[0] + 8, max(8, xy[1] - max(22, im.width // 38))
        bbox = draw.textbbox((tx, ty), label, font=f)
        draw.rectangle((bbox[0] - 5, bbox[1] - 3, bbox[2] + 5, bbox[3] + 3), fill=WHITE)
        draw.text((tx, ty), label, font=f, fill=color)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path)


def compose_case(case: dict) -> Path:
    overview = case["overview"]
    overview_path = Path(overview.get("annotated_path") or overview["path"])
    if not overview_path.exists():
        overview_path = Path(overview["path"])
    panels = [("overview", overview_path)]
    for zoom in case.get("zooms", []):
        panels.append((zoom["id"], Path(zoom["path"])))
    images = [flatten(path) for _, path in panels]
    panel = images[0].width
    gap = max(28, panel // 32)
    label_h = max(50, panel // 18)
    margin = max(36, panel // 28)
    out = Image.new("RGB", (margin * 2 + len(images) * panel + (len(images) - 1) * gap, margin * 2 + panel + label_h), WHITE)
    draw = ImageDraw.Draw(out)
    f = font(max(20, panel // 36), bold=True)
    for i, ((label, _), image) in enumerate(zip(panels, images)):
        x = margin + i * (panel + gap)
        y = margin
        out.paste(image.resize((panel, panel), Image.Resampling.LANCZOS), (x, y))
        bbox = draw.textbbox((0, 0), label, font=f)
        draw.text((x + panel / 2 - (bbox[2] - bbox[0]) / 2, y + panel + 16), label, font=f, fill=INK)
    path = Path(case["comparison_path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    return path


def make_contact_sheet(cases: list[dict], out_path: Path, max_width: int = 2600) -> None:
    rows = []
    for case in cases:
        comp = Path(case["comparison_path"])
        if comp.exists():
            rows.append((case["label"], flatten(comp)))
    if not rows:
        return
    target_w = max_width
    resized = []
    for label, im in rows:
        scale = target_w / im.width
        resized.append((label, im.resize((target_w, int(im.height * scale)), Image.Resampling.LANCZOS)))
    title_h = 52
    gap = 28
    total_h = sum(im.height + title_h for _, im in resized) + gap * (len(resized) + 1)
    canvas = Image.new("RGB", (target_w, total_h), WHITE)
    draw = ImageDraw.Draw(canvas)
    f = font(28, bold=True)
    y = gap
    for label, im in resized:
        draw.text((18, y), label, font=f, fill=INK)
        y += title_h
        canvas.paste(im, (0, y))
        y += im.height + gap
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--contact", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    for case in plan.get("cases", []):
        for callout in case.get("callouts", []):
            draw_callout(Path(callout["parent_path"]), Path(callout["annotated_path"]), callout["rects"], callout["labels"])
        compose_case(case)
    make_contact_sheet(plan.get("cases", []), args.contact)
    print(json.dumps({"cases": len(plan.get("cases", [])), "contact": str(args.contact)}, indent=2))


if __name__ == "__main__":
    main()
