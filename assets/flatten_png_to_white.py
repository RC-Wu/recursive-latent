#!/usr/bin/env python3
"""Flatten transparent PNG renders onto a pure white RGB background."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def flatten_one(path: Path, out: Path | None = None) -> Path:
    img = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.alpha_composite(img)
    out_path = out or path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bg.convert("RGB").save(out_path)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()

    for path in args.paths:
        if path.is_dir():
            files = sorted(path.glob("*.png"))
        else:
            files = [path]
        for file in files:
            out = args.out_dir / file.name if args.out_dir else None
            print(flatten_one(file, out))


if __name__ == "__main__":
    main()
