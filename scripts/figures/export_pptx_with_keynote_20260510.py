#!/usr/bin/env python3
"""Export a PPTX to PDF with Keynote on macOS.

The paper workflow for qualitative figures is PPTX-first.  This helper keeps
the export reproducible on machines where Keynote is installed and LibreOffice
is not available.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import time
from pathlib import Path


def export_with_keynote(pptx: Path, pdf: Path, timeout_seconds: int = 1800) -> None:
    pptx = pptx.resolve()
    pdf = pdf.resolve()
    if not pptx.exists():
        raise FileNotFoundError(pptx)
    pdf.parent.mkdir(parents=True, exist_ok=True)
    script = f'''
set inputFile to POSIX file "{pptx}" as alias
set outputFile to POSIX file "{pdf}"
with timeout of {int(timeout_seconds)} seconds
    tell application id "com.apple.iWork.Keynote"
        launch
        delay 3
        set theDoc to open inputFile
        delay 1
        export theDoc to outputFile as PDF
        close theDoc saving no
    end tell
end timeout
'''
    with tempfile.NamedTemporaryFile("w", suffix=".applescript", encoding="utf-8", delete=False) as f:
        f.write(script)
        script_path = Path(f.name)
    try:
        subprocess.run(["osascript", str(script_path)], check=True, timeout=timeout_seconds + 30)
    finally:
        script_path.unlink(missing_ok=True)
    if not pdf.exists() or pdf.stat().st_size == 0:
        raise RuntimeError(f"Keynote export did not create a non-empty PDF: {pdf}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    start = time.time()
    export_with_keynote(args.pptx, args.pdf, timeout_seconds=args.timeout_seconds)
    if args.summary:
        payload = {
            "source_pptx": str(args.pptx.resolve()),
            "pdf": str(args.pdf.resolve()),
            "exporter": "Keynote AppleScript",
            "workflow_contract": "PPTX-first figure; PDF exported from Keynote",
            "timeout_seconds": int(args.timeout_seconds),
            "export_seconds": time.time() - start,
            "pdf_bytes": int(args.pdf.stat().st_size),
        }
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(args.pdf)


if __name__ == "__main__":
    main()
