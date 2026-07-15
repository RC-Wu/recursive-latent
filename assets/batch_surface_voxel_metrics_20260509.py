#!/usr/bin/env python3
"""Batch surface-voxel connectivity metrics for textured GLB result folders."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
sys.path.insert(0, str(ROOT / "assets"))

from surface_voxel_connectivity_20260509 import (  # noqa: E402
    box_dimension,
    component_stats,
    dilate,
    load_mesh_points,
    voxelize,
)


def metric_for_mesh(path: Path, label: str, resolution: int, sample_count: int, seed: int) -> dict[str, object]:
    points, meta = load_mesh_points(path, sample_count=sample_count, seed=seed)
    coords = voxelize(points, resolution)
    row: dict[str, object] = {
        "label": label,
        "path": str(path),
        "resolution": resolution,
        "occupied": int(len(coords)),
        **meta,
    }
    for radius in (0, 1, 2):
        dilated = dilate(coords, resolution, radius)
        comps, largest, lcr = component_stats(dilated)
        row[f"components_r{radius}"] = int(comps)
        row[f"largest_r{radius}"] = int(largest)
        row[f"lcr_r{radius}"] = float(lcr)
        row[f"occupied_r{radius}"] = int(len(dilated))
    coords_by_res = {res: voxelize(points, res) for res in (32, 48, 64, 96)}
    row["box_dim_32_96"] = box_dimension(coords_by_res)
    return row


def find_glbs(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("textured.glb") if path.is_file())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out-prefix", type=Path, required=True)
    parser.add_argument("--resolution", type=int, default=64)
    parser.add_argument("--sample-count", type=int, default=60000)
    parser.add_argument("--seed", type=int, default=90509)
    args = parser.parse_args()

    rows = []
    for path in find_glbs(args.root):
        label = path.parent.name
        print(f"[metric] {label}", flush=True)
        rows.append(metric_for_mesh(path, label, args.resolution, args.sample_count, args.seed))

    args.out_prefix.parent.mkdir(parents=True, exist_ok=True)
    csv_path = args.out_prefix.with_suffix(".csv")
    json_path = args.out_prefix.with_suffix(".json")
    if rows:
        fieldnames = list(rows[0].keys())
        with csv_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    else:
        csv_path.write_text("")
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"[done] {csv_path}")
    print(f"[done] {json_path}")


if __name__ == "__main__":
    main()
