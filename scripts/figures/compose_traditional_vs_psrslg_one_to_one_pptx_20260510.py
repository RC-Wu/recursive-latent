#!/usr/bin/env python3
"""Orchestrate PPTX-first one-to-one figure generation and export."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
NODE = Path("/Users/fanta/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node")
NODE_MODULES = Path("/Users/fanta/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules")
JS_SCRIPT = ROOT / "scripts" / "figures" / "compose_traditional_vs_psrslg_one_to_one_pptx_20260510.js"
KEYNOTE_EXPORT = ROOT / "scripts" / "figures" / "export_pptx_with_keynote_20260510.py"
OUT_DIR = ROOT / "paper_siga" / "figures" / "traditional_vs_psrslg_one_to_one_pptx_20260510"
PPTX = OUT_DIR / "traditional_vs_psrslg_one_to_one_20260510.pptx"
PDF = OUT_DIR / "traditional_vs_psrslg_one_to_one_20260510.pdf"
PREVIEW = OUT_DIR / "traditional_vs_psrslg_one_to_one_20260510_preview.png"
SOURCE_COMPOSITE = ROOT / "visuals" / "traditional_vs_v24_one_to_one_zoom_20260510" / "traditional_vs_v24_one_to_one_zoom_20260510.png"


def make_preview() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.open(SOURCE_COMPOSITE).convert("RGB")
    image.thumbnail((2400, 1500), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (2400, 1500), "white")
    x = (canvas.width - image.width) // 2
    y = (canvas.height - image.height) // 2
    canvas.paste(image, (x, y))
    canvas.save(PREVIEW)
    return PREVIEW


def run_node() -> None:
    env = {"NODE_PATH": str(NODE_MODULES)}
    subprocess.run([str(NODE), str(JS_SCRIPT)], check=True, cwd=str(ROOT), env={**env})
    if not PPTX.exists() or PPTX.stat().st_size == 0:
        raise RuntimeError(f"PPTX was not written: {PPTX}")


def run_keynote_export(skip_pdf: bool) -> str:
    if skip_pdf:
        return "skipped"
    subprocess.run(["python3", str(KEYNOTE_EXPORT), str(PPTX), str(PDF)], check=True, cwd=str(ROOT))
    return "ok"


def build(skip_pdf: bool = False) -> dict[str, object]:
    run_node()
    preview = make_preview()
    export_status = run_keynote_export(skip_pdf=skip_pdf)
    summary = {
        "schema": "traditional_vs_psrslg_one_to_one_pptx_20260510",
        "pptx": str(PPTX),
        "pdf": str(PDF) if PDF.exists() else "",
        "preview_png": str(preview),
        "pdf_export": export_status,
        "source_composite": str(SOURCE_COMPOSITE),
        "workflow_contract": "paper figures must be arranged in PPTX first, then exported to PDF",
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-pdf", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build(skip_pdf=args.skip_pdf), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
