#!/usr/bin/env python3
"""Prepare seam-aware junction-collar meshes and PBR guides for remote texturing."""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_SEAM_DIR = PROJECT_ROOT / "results" / "masked_naturalization_seam_optimization_20260510"
DEFAULT_OUT = PROJECT_ROOT / "results" / "seam_aware_texturing_batch_20260510"
REMOTE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]


TASK_GUIDES = {
    "botanical_root": {
        "family": "botanical/root",
        "case_id": "S01_botanical_root_junction_collar_continuous_bark",
        "gpu": 4,
        "seed": 20295610,
        "palette": ((34, 24, 18), [(74, 48, 31), (116, 76, 43), (160, 116, 70), (45, 30, 20)]),
        "motif": "root",
        "guide_notes": "continuous bark/root cambium over junction collars; avoid painted rings and UV material islands",
    },
    "coral_frontier": {
        "family": "coral/frontier",
        "case_id": "S02_coral_frontier_junction_collar_continuous_pores",
        "gpu": 5,
        "seed": 20295611,
        "palette": ((226, 132, 118), [(255, 222, 176), (255, 166, 132), (248, 108, 118), (244, 188, 150)]),
        "motif": "coral",
        "guide_notes": "continuous coral pores and ridges crossing growth junctions; avoid disconnected colored bands",
    },
    "ifs_crystal": {
        "family": "IFS/crystal",
        "case_id": "S03_ifs_crystal_junction_collar_continuous_facets",
        "gpu": 6,
        "seed": 20295612,
        "palette": ((54, 48, 40), [(238, 204, 96), (190, 144, 58), (106, 92, 72), (252, 232, 140)]),
        "motif": "lattice",
        "guide_notes": "continuous pyrite facets across copy bridges; avoid isolated material islands",
    },
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_seed(text: str) -> int:
    total = 0
    for idx, ch in enumerate(text):
        total = (total * 131 + ord(ch) + idx) % (2**32)
    return total


def draw_guide(path: Path, bg: tuple[int, int, int], colors: list[tuple[int, int, int]], motif: str) -> None:
    img = Image.new("RGB", (768, 768), bg)
    draw = ImageDraw.Draw(img)
    rng = np.random.default_rng(stable_seed(path.name))
    # Soft base continuity: broad low-frequency ribbons avoid hard material seams.
    for _ in range(210):
        color = colors[int(rng.integers(0, len(colors)))]
        x = int(rng.integers(-80, 820))
        y = int(rng.integers(-80, 820))
        if motif == "root":
            dx = int(rng.normal(0, 130))
            dy = int(rng.normal(86, 46))
            draw.line((x, y, x + dx, y + dy), fill=color, width=int(rng.integers(5, 14)))
        elif motif == "coral":
            dx = int(rng.normal(0, 128))
            dy = int(rng.normal(0, 112))
            draw.line((x, y, x + dx, y + dy), fill=color, width=int(rng.integers(8, 18)))
            if rng.random() < 0.55:
                r = int(rng.integers(12, 42))
                draw.ellipse((x - r, y - r, x + r, y + r), outline=color, width=3)
        else:
            r = int(rng.integers(18, 58))
            draw.rectangle((x - r, y - r, x + r, y + r), outline=color, width=4)
            if rng.random() < 0.42:
                draw.line((x - r, y, x + r, y), fill=color, width=3)
                draw.line((x, y - r, x, y + r), fill=color, width=3)
    # Seam-aware overlay: long continuous curves crossing the full guide.
    for k in range(18):
        color = colors[k % len(colors)]
        y0 = int(40 + k * 40 + rng.normal(0, 8))
        pts = []
        for i in range(10):
            x = int(i * 86 - 20)
            y = int(y0 + math.sin(i * 0.9 + k) * 26 + rng.normal(0, 9))
            pts.append((x, y))
        draw.line(pts, fill=color, width=3 if motif != "root" else 2)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def _remote_path(local_path: Path, out_dir: Path) -> str:
    rel = local_path.relative_to(out_dir)
    return f"{REMOTE_ROOT}/inputs/seam_aware_texturing_batch_20260510/{rel.as_posix()}"


def prepare_batch(seam_dir: Path = DEFAULT_SEAM_DIR, out_dir: Path = DEFAULT_OUT) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    guide_dir = out_dir / "_guides"
    rows: list[dict[str, Any]] = []
    metrics_path = seam_dir / "masked_naturalization_seam_band_metrics_20260510.json"
    seam_rows = _read_json(metrics_path)
    seam_by_task = {row["task_id"]: row for row in seam_rows}
    for task_id, spec in TASK_GUIDES.items():
        seam = seam_by_task[task_id]
        case_id = spec["case_id"]
        case_dir = out_dir / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        source_mesh = Path(seam["optimized_mesh"])
        local_mesh = case_dir / f"{case_id}.obj"
        shutil.copyfile(source_mesh, local_mesh)
        metadata = _read_json(Path(seam["optimized_metadata"]))
        local_meta = case_dir / f"{case_id}_metadata.json"
        metadata.update(
            {
                "case_id": case_id,
                "remote_texturing_role": "seam_aware_junction_collar_candidate",
                "seam_aware_guide_notes": spec["guide_notes"],
                "source_seam_metric_row": seam,
            }
        )
        local_meta.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
        guide_path = guide_dir / f"{case_id}_seam_aware_pbr_guide.png"
        bg, colors = spec["palette"]
        draw_guide(guide_path, bg, colors, spec["motif"])
        row = {
            "case_id": case_id,
            "task_id": task_id,
            "family": spec["family"],
            "mesh_path": _remote_path(local_mesh, out_dir),
            "guide_image": _remote_path(guide_path, out_dir),
            "metadata_path": _remote_path(local_meta, out_dir),
            "remote_target": REMOTE_TARGET,
            "gpu_group": int(spec["gpu"]),
            "seed": int(spec["seed"]),
            "steps": 8,
            "texture_size": 2048,
            "seam_boundary_jump_delta_deg": seam["seam_boundary_jump_delta_deg"],
            "seam_band_normal_delta_deg": seam["seam_band_normal_delta_deg"],
            "optimized_lcr": seam["optimized_lcr"],
            "junction_collar_count": seam["junction_collar_count"],
            "guide_notes": spec["guide_notes"],
            "claim_scope": "remote texturing candidate for seam visual QA; not a topology proof",
            "selection_policy": "small controlled seam-aware rerun, one case per task plus spare GPU",
        }
        rows.append(row)

    fields = list(rows[0])
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "manifest.json").write_text(json.dumps({"schema": "seam_aware_texturing_batch_20260510", "rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    case_lines = [f"{row['case_id']}|{row['mesh_path']}|{row['guide_image']}|{row['seed']}|{row['gpu_group']}" for row in rows]
    (out_dir / "gpu4567_cases.txt").write_text("\n".join(case_lines) + "\n", encoding="utf-8")
    for gpu in ALLOWED_GPUS:
        selected = [line for line, row in zip(case_lines, rows) if int(row["gpu_group"]) == gpu]
        (out_dir / f"gpu{gpu}_cases.txt").write_text("\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")
    summary = {
        "schema": "seam_aware_texturing_batch_20260510",
        "out_dir": str(out_dir),
        "manifest_csv": str(out_dir / "manifest.csv"),
        "manifest_json": str(out_dir / "manifest.json"),
        "case_count": len(rows),
        "remote_copy_target": f"{REMOTE_ROOT}/inputs/seam_aware_texturing_batch_20260510",
        "allowed_gpus": ALLOWED_GPUS,
        "remote_storage_limit_gb": 200,
        "claim_scope": "texture/PBR rerun inputs for seam visual QA; not paper proof until rendered and scored",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "\n".join(
            [
                "# Seam-aware texturing batch 2026-05-10",
                "",
                "小批量远端 texture/PBR 输入，用于验证 junction collar + 连续材质 guide 是否缓解白底 zoom 接缝。",
                "",
                "运行后只能作为视觉 QA 候选；进入论文前仍需 white-background zoom、seam-band render QA 和 PPTX->PDF 排版。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seam-dir", type=Path, default=DEFAULT_SEAM_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    print(json.dumps(prepare_batch(args.seam_dir, args.out_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
