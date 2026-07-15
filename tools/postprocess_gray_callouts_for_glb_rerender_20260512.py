#!/usr/bin/env python3
"""Flatten rerendered PNGs to white and create unlabeled gray callouts."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw


PLAN = Path(
    "/Users/fanta/code/agent/Code/recursive_3d_generative_growth/"
    "docs/evaluation/user_selected_case_glb_rerender_20260512/"
    "rendered_glb_white_1200_v2/matched_camera_zoom_plan.json"
)
GRAY = (130, 130, 130)


def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    flattened = 0
    for case in plan.get("cases", []):
        paths = [Path(case["overview"]["path"])]
        paths.extend(Path(zoom["path"]) for zoom in case.get("zooms", []))
        for path in paths:
            if not path.is_file():
                continue
            src = Image.open(path).convert("RGBA")
            base = Image.new("RGBA", src.size, (255, 255, 255, 255))
            base.alpha_composite(src)
            base.convert("RGB").save(path)
            flattened += 1
    written = 0
    missing = []
    for case in plan.get("cases", []):
        for callout in case.get("callouts", []):
            if callout.get("parent_id") != "overview":
                continue
            parent = Path(callout["parent_path"])
            out = parent.with_name("overview_gray_callout.png")
            if not parent.is_file():
                missing.append(str(parent))
                continue
            im = Image.open(parent).convert("RGB")
            draw = ImageDraw.Draw(im)
            width = max(4, im.width // 220)
            for rect in callout.get("rects", []):
                draw.rectangle(tuple(rect), outline=GRAY, width=width)
            im.save(out)
            written += 1
    print(f"WHITE_FLATTENED={flattened}")
    print(f"GRAY_CALLOUTS={written}")
    if missing:
        print("MISSING_PARENTS=" + json.dumps(missing, ensure_ascii=False))


if __name__ == "__main__":
    main()
