#!/usr/bin/env python3
"""Compute selected-case metrics for the main traditional-vs-ours comparison."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "assets"))

from batch_surface_voxel_metrics_20260509 import metric_for_mesh  # noqa: E402
from recursive_growth_mesh_metrics import metric_one  # noqa: E402


def read_cases(manifest: Path) -> list[dict]:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    return payload["cases"] if isinstance(payload, dict) else payload


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--resolution", type=int, default=64)
    parser.add_argument("--sample-count", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=20260511)
    parser.add_argument("--weld-tolerance", type=float, default=0.002)
    args = parser.parse_args()

    mesh_args = SimpleNamespace(
        sample_limit=200000,
        weld_tolerance=args.weld_tolerance,
        occupancy_resolution=args.resolution,
        box_resolutions=[8, 16, 32, 64],
        primary_connectivity="occupancy",
    )
    surface_rows = []
    mesh_rows = []
    for case in read_cases(args.manifest):
        label = case["label"]
        path = Path(case["mesh"])
        if not path.exists():
            raise FileNotFoundError(path)
        print(f"[selected-metric] {label}", flush=True)
        row = metric_for_mesh(path, label, args.resolution, args.sample_count, args.seed)
        row["family"] = case.get("family", "")
        row["role"] = "ours" if "_ours_" in label else "traditional"
        surface_rows.append(row)
        mesh_row = metric_one(path, label, mesh_args)
        mesh_row["family"] = case.get("family", "")
        mesh_row["role"] = "ours" if "_ours_" in label else "traditional"
        mesh_rows.append(mesh_row)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "main_experiment_selected_surface_metrics_occ64.json").write_text(
        json.dumps(surface_rows, indent=2),
        encoding="utf-8",
    )
    (args.out_dir / "main_experiment_selected_recursive_mesh_metrics.json").write_text(
        json.dumps({"rows": mesh_rows}, indent=2),
        encoding="utf-8",
    )
    write_csv(args.out_dir / "main_experiment_selected_surface_metrics_occ64.csv", surface_rows)
    write_csv(args.out_dir / "main_experiment_selected_recursive_mesh_metrics.csv", mesh_rows)
    print(args.out_dir)


if __name__ == "__main__":
    main()
