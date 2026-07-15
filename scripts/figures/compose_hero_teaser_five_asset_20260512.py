#!/usr/bin/env python3
"""Compose transparent five-asset teaser renders into QA sheets and a 3:2 figure."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw


WHITE = (255, 255, 255, 255)
BOX = (176, 180, 184, 255)


def alpha_to_white(path: Path) -> Image.Image:
    src = Image.open(path).convert("RGBA")
    base = Image.new("RGBA", src.size, WHITE)
    base.alpha_composite(src)
    return base


def content_bbox(im: Image.Image, margin: int = 10) -> tuple[int, int, int, int]:
    alpha = im.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return (0, 0, im.width, im.height)
    left, top, right, bottom = bbox
    return (
        max(0, left - margin),
        max(0, top - margin),
        min(im.width, right + margin),
        min(im.height, bottom + margin),
    )


def crop_to_content_with_bbox(path: Path, pad_ratio: float = 0.09) -> tuple[Image.Image, tuple[int, int, int, int]]:
    im = Image.open(path).convert("RGBA")
    bbox = content_bbox(im, margin=0)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    pad = int(max(w, h) * pad_ratio)
    bbox = (
        max(0, bbox[0] - pad),
        max(0, bbox[1] - pad),
        min(im.width, bbox[2] + pad),
        min(im.height, bbox[3] + pad),
    )
    return im.crop(bbox), bbox


def crop_to_content(path: Path, pad_ratio: float = 0.09) -> Image.Image:
    return crop_to_content_with_bbox(path, pad_ratio)[0]


def resize_contain(im: Image.Image, box: tuple[int, int]) -> Image.Image:
    tw, th = box
    scale = min(tw / im.width, th / im.height)
    nw = max(1, int(im.width * scale))
    nh = max(1, int(im.height * scale))
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def paste_center(canvas: Image.Image, im: Image.Image, box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    x, y, w, h = box
    fitted = resize_contain(im, (w, h))
    px = x + (w - fitted.width) // 2
    py = y + (h - fitted.height) // 2
    canvas.alpha_composite(fitted, (px, py))
    return (px, py, px + fitted.width, py + fitted.height)


def fit_box_inside(box: tuple[int, int, int, int], size: tuple[int, int], pad: int = 0) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0
    max_x0 = max(pad, size[0] - pad - w)
    max_y0 = max(pad, size[1] - pad - h)
    x0 = min(max(x0, pad), max_x0)
    y0 = min(max(y0, pad), max_y0)
    return (x0, y0, x0 + w, y0 + h)


def scaled_rect(
    rect: Sequence[int],
    src_size: int,
    dst_bbox: Sequence[int],
    crop_bbox: Sequence[int] | None = None,
) -> tuple[int, int, int, int]:
    left, top, right, bottom = rect
    if crop_bbox is not None:
        cx0, cy0, cx1, cy1 = crop_bbox
        left = max(cx0, min(cx1, left)) - cx0
        right = max(cx0, min(cx1, right)) - cx0
        top = max(cy0, min(cy1, top)) - cy0
        bottom = max(cy0, min(cy1, bottom)) - cy0
        src_w = max(1, cx1 - cx0)
        src_h = max(1, cy1 - cy0)
    else:
        src_w = src_size
        src_h = src_size
    dx0, dy0, dx1, dy1 = dst_bbox
    sx = (dx1 - dx0) / src_w
    sy = (dy1 - dy0) / src_h
    return (
        int(dx0 + left * sx),
        int(dy0 + top * sy),
        int(dx0 + right * sx),
        int(dy0 + bottom * sy),
    )


def draw_rect(draw: ImageDraw.ImageDraw, rect: Sequence[int], width: int) -> None:
    for i in range(width):
        draw.rectangle((rect[0] - i, rect[1] - i, rect[2] + i, rect[3] + i), outline=BOX)


def write_previews(plan: dict, out_dir: Path) -> None:
    preview_dir = out_dir / "white_previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    for case in plan["cases"]:
        case_preview = preview_dir / case["id"]
        case_preview.mkdir(parents=True, exist_ok=True)
        overview = alpha_to_white(Path(case["overview"]["path"]))
        draw = ImageDraw.Draw(overview)
        for zoom in case["zooms"]:
            draw_rect(draw, zoom["callout_rect"], max(2, overview.width // 360))
        overview.save(case_preview / "overview_all_zoom_boxes.png")
        alpha_to_white(Path(case["overview"]["path"])).save(case_preview / "overview_white.png")
        for zoom in case["zooms"]:
            alpha_to_white(Path(zoom["path"])).save(case_preview / f"{zoom['id']}_white.png")


def compose_contact_sheet(plan: dict, out_path: Path) -> None:
    thumb = 310
    gap = 24
    row_h = thumb
    width = gap + 6 * (thumb + gap)
    height = gap + len(plan["cases"]) * (row_h + gap)
    canvas = Image.new("RGBA", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    for row, case in enumerate(plan["cases"]):
        y = gap + row * (row_h + gap)
        overview = alpha_to_white(Path(case["overview"]["path"]))
        overview_draw = ImageDraw.Draw(overview)
        for zoom in case["zooms"]:
            draw_rect(overview_draw, zoom["callout_rect"], max(2, overview.width // 360))
        paste_center(canvas, overview, (gap, y, thumb, thumb))
        for col, zoom in enumerate(case["zooms"]):
            im = alpha_to_white(Path(zoom["path"]))
            paste_center(canvas, im, (gap + (col + 1) * (thumb + gap), y, thumb, thumb))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out_path)


def compose_teaser(plan: dict, out_path: Path, selections: dict[str, str], size: tuple[int, int]) -> None:
    width, height = size
    canvas = Image.new("RGBA", size, WHITE)
    draw = ImageDraw.Draw(canvas)
    margin_x = int(width * 0.014)
    margin_y = int(height * 0.018)
    gap_x = int(width * 0.010)
    gap_y = int(height * 0.018)
    cell_w = (width - 2 * margin_x - 2 * gap_x) // 3
    cell_h = (height - 2 * margin_y - gap_y) // 2
    positions = [
        (margin_x, margin_y),
        (margin_x + cell_w + gap_x, margin_y),
        (margin_x + 2 * (cell_w + gap_x), margin_y),
        (margin_x + int(cell_w * 0.50), margin_y + cell_h + gap_y),
        (margin_x + int(cell_w * 1.52) + gap_x, margin_y + cell_h + gap_y),
    ]
    overview_box_w = int(cell_w * 0.76)
    zoom_box = int(min(cell_w * 0.41, cell_h * 0.49))
    line_w = max(4, width // 900)

    for idx, case in enumerate(plan["cases"]):
        x, y = positions[idx]
        overview_area = (x, y, overview_box_w, cell_h)
        overview_src, overview_crop = crop_to_content_with_bbox(Path(case["overview"]["path"]), pad_ratio=0.09)
        overview_bbox = paste_center(canvas, overview_src, overview_area)

        selected_id = selections.get(case["id"], case.get("selected_zoom") or "zoom_01")
        selected_zoom = next((z for z in case["zooms"] if z["id"] == selected_id), case["zooms"][0])
        zoom_src = crop_to_content(Path(selected_zoom["path"]), pad_ratio=0.055)

        zoom_x = x + overview_box_w - int(zoom_box * 0.07)
        if idx in {1, 4}:
            zoom_y = y + int(cell_h * 0.06)
        elif idx == 2:
            zoom_y = y + int(cell_h * 0.50)
        else:
            zoom_y = y + int(cell_h * 0.47)
        zoom_area = fit_box_inside((zoom_x, zoom_y, zoom_x + zoom_box, zoom_y + zoom_box), size, int(width * 0.012))
        zoom_bbox = paste_center(canvas, zoom_src, (zoom_area[0], zoom_area[1], zoom_area[2] - zoom_area[0], zoom_area[3] - zoom_area[1]))

        rect = scaled_rect(
            selected_zoom["callout_rect"],
            plan["render_config"]["resolution"],
            overview_bbox,
            overview_crop,
        )
        # Keep the callout square visible even when content crop removes empty alpha.
        rect_w = rect[2] - rect[0]
        rect_h = rect[3] - rect[1]
        side = max(rect_w, rect_h, int(min(overview_bbox[2] - overview_bbox[0], overview_bbox[3] - overview_bbox[1]) * 0.16))
        cx = (rect[0] + rect[2]) // 2
        cy = (rect[1] + rect[3]) // 2
        rect = (cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2)
        rect = fit_box_inside(rect, size, int(width * 0.006))
        draw_rect(draw, rect, line_w)
        draw_rect(draw, zoom_bbox, max(3, line_w - 1))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out_path)
    if out_path.suffix.lower() != ".png":
        canvas.convert("RGB").save(out_path.with_suffix(".png"))


def parse_selection(raw: Sequence[str] | None) -> dict[str, str]:
    selections: dict[str, str] = {}
    for item in raw or []:
        if "=" not in item:
            raise SystemExit(f"Invalid --select entry: {item}")
        key, value = item.split("=", 1)
        selections[key] = value
    return selections


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--select", action="append")
    parser.add_argument("--width", type=int, default=3600)
    parser.add_argument("--height", type=int, default=2400)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    selections = parse_selection(args.select)
    write_previews(plan, args.out_dir)
    compose_contact_sheet(plan, args.out_dir / "hero_teaser_zoom_candidate_contact_sheet.png")
    teaser_path = args.out_dir / "hero_teaser_five_asset_3x2_3600x2400.png"
    compose_teaser(plan, teaser_path, selections, (args.width, args.height))
    (args.out_dir / "selected_zoom_manifest.json").write_text(
        json.dumps({"selections": selections, "source_plan": str(args.plan), "teaser": str(teaser_path)}, indent=2),
        encoding="utf-8",
    )
    print(f"[hero-compose] wrote {teaser_path}")


if __name__ == "__main__":
    main()
