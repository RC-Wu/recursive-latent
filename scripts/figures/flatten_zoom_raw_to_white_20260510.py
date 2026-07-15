#!/usr/bin/env python3
"""Flatten transparent Blender zoom PNGs onto a true white background."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


WHITE = (255, 255, 255, 255)


def flatten_png(src: Path, dst: Path) -> None:
    image = Image.open(src).convert("RGBA")
    base = Image.new("RGBA", image.size, WHITE)
    base.alpha_composite(image)
    dst.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(dst)


def flatten_plan(plan_path: Path, suffix: str = "_white") -> dict[str, object]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    outputs: list[str] = []
    for case in plan.get("cases", []):
        panels = [case.get("overview", {})] + list(case.get("zooms", []))
        for panel in panels:
            src_text = panel.get("path")
            if not src_text:
                continue
            src = Path(src_text)
            dst = src.with_name(f"{src.stem}{suffix}{src.suffix}")
            flatten_png(src, dst)
            panel["white_path"] = str(dst)
            outputs.append(str(dst))
    out_plan = plan_path.with_name(f"{plan_path.stem}_white{plan_path.suffix}")
    out_plan.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return {"plan": str(out_plan), "outputs": outputs, "count": len(outputs)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(flatten_plan(args.plan), indent=2))


if __name__ == "__main__":
    main()
