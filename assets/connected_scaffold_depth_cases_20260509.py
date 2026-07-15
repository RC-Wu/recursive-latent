#!/usr/bin/env python3
"""Generate connected non-tree scaffold depth/parameter stages.

This script makes fixed-condition non-tree stages for paper visualization:
the support is connected by construction, while the number of recursive
hopper/lattice modules increases with stage. The output OBJ meshes are meant
for downstream Trellis2 texturing, not matplotlib/point-cloud figures.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import connected_scaffold_cases_v2_20260509 as base


DEFAULT_OUT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/connected_scaffold_depth_cases_20260509")


def bismuth_hopper_stage(stage: int) -> np.ndarray:
    points: set[tuple[int, int, int]] = set()
    specs = [
        ((-15, -8, -10), 3 + stage, 23, 3, 4),
        ((16, 10, -5), 2 + stage, 19, 3, 4),
        ((-2, 23, 1), 1 + stage, 16, 3, 4),
        ((12, -20, 8), max(2, stage), 15, 2, 4),
    ]
    centers: list[np.ndarray] = []
    for center, levels, outer, step, height in specs:
        base.add_hopper_square(points, center, levels, outer, step, height)
        centers.append(np.asarray(center, dtype=float))
    # A persistent connected backbone is part of the grammar state, not a
    # post-hoc bridge; all stages share it so topology remains comparable.
    for a, b in zip(centers[:-1], centers[1:]):
        base.add_tube(points, a + np.array([0, 0, 5], dtype=float), b + np.array([0, 0, 5], dtype=float), 4)
        base.add_tube(points, a + np.array([7, -7, 9], dtype=float), b + np.array([-7, 7, 9], dtype=float), 2)
    base.add_box(points, (-9, -9, -15), (9, 9, -6))
    if stage >= 3:
        base.add_tube(points, centers[0] + np.array([0, 12, 12], dtype=float), centers[-1] + np.array([0, -12, 12], dtype=float), 2)
    if stage >= 4:
        base.add_tube(points, centers[1] + np.array([-9, 0, 18], dtype=float), centers[2] + np.array([9, 0, 18], dtype=float), 2)
    return base.coords_array(points)


def pyrite_lattice_stage(stage: int) -> np.ndarray:
    points: set[tuple[int, int, int]] = set()
    span = 1 + min(stage, 3)
    spacing = 17
    nodes = []
    for x in range(-span, span + 1):
        for y in range(-span, span + 1):
            for z in range(-span, span + 1):
                if abs(x) + abs(y) + abs(z) <= span + 1 and (x + 2 * y - z + stage) % 3 != 1:
                    p = np.array([x * spacing, y * spacing, z * spacing], dtype=float)
                    nodes.append((x, y, z, p))
                    d = 5 if (x + y + z) % 2 == 0 else 4
                    base.add_box(points, (int(p[0] - d), int(p[1] - d), int(p[2] - d)), (int(p[0] + d), int(p[1] + d), int(p[2] + d)))
                    base.add_octahedron(points, p + np.array([0, 0, d + 3]), 4)
                    base.add_octahedron(points, p - np.array([0, 0, d + 3]), 4)
    node_map = {(x, y, z): p for x, y, z, p in nodes}
    origin = np.array([0.0, 0.0, 0.0])
    if (0, 0, 0) in node_map:
        origin = node_map[(0, 0, 0)]
    for key, p in node_map.items():
        for off in [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)]:
            other = (key[0] + off[0], key[1] + off[1], key[2] + off[2])
            if other in node_map:
                base.add_tube(points, p, node_map[other], 2 if sum(abs(v) for v in off) == 1 else 1)
        if stage >= 2:
            base.add_tube(points, origin, p, 1)
    return base.coords_array(points)


def write_rows(out_dir: Path, rows: list[dict]) -> None:
    if not rows:
        return
    keys = sorted({k for r in rows for k in r})
    with (out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "metrics.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


def generate(out_dir: Path, family: str) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for stage in range(1, 5):
        if family == "bismuth_hopper_depth":
            coords = bismuth_hopper_stage(stage)
        elif family == "pyrite_lattice_depth":
            coords = pyrite_lattice_stage(stage)
        else:
            raise ValueError(f"unknown family: {family}")
        coords = base.largest_occupancy_component(coords)
        mesh = base.coords_to_mesh(coords)
        label = f"{family}_stage_{stage:02d}"
        case_dir = out_dir / label
        case_dir.mkdir(parents=True, exist_ok=True)
        obj = case_dir / f"{label}.obj"
        mesh.export(obj)
        row = {
            "label": label,
            "family": family,
            "stage": stage,
            "obj_path": str(obj),
        }
        row.update(base.mesh_stats(mesh))
        row.update(base.occupancy_stats(coords))
        rows.append(row)
    write_rows(out_dir, rows)
    contact = base.render_contact_sheet(out_dir, rows)
    summary = {"out_dir": str(out_dir), "family": family, "contact_sheet": str(contact), "rows": rows}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--family", choices=["bismuth_hopper_depth", "pyrite_lattice_depth"], default="bismuth_hopper_depth")
    args = parser.parse_args()
    summary = generate(args.out, args.family)
    print(json.dumps({"out_dir": summary["out_dir"], "family": summary["family"], "contact_sheet": summary["contact_sheet"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

