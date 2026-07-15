#!/usr/bin/env python3
"""Generate connected volumetric coral/DLA depth-control scaffold meshes.

These cases are intentionally grammar-native connected scaffolds rather than
post-hoc bridged DLA fragments.  They are used to test whether a coral/DLA-like
non-tree family can pass the same-condition depth visualization gate before
Trellis2 texturing.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import connected_scaffold_cases_v2_20260509 as base


DEFAULT_OUT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/connected_coral_depth_cases_20260509")


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n < 1e-8:
        return np.array([0.0, 0.0, 1.0])
    return v / n


def volumetric_coral_stage(stage: int, seed: int = 20260509) -> np.ndarray:
    """Connected stage sequence with a persistent trunk and growing nodules."""
    rng = np.random.default_rng(seed)
    points: set[tuple[int, int, int]] = set()
    root = np.array([0.0, 0.0, -24.0])
    base.add_ball(points, root, 8)
    tips = [root]

    seed_dirs = [
        np.array([1.00, 0.24, 0.82]),
        np.array([-0.72, 0.88, 0.58]),
        np.array([0.12, -1.00, 0.96]),
        np.array([0.58, 0.62, -0.55]),
        np.array([-0.42, -0.52, 1.05]),
    ]
    active_seed_dirs = seed_dirs[: 2 + min(stage, 3)]
    for i, d in enumerate(active_seed_dirs):
        d = _unit(d)
        end = root + d * (22.0 + 4.0 * stage + 2.0 * i)
        base.add_tube(points, root, end, 6 if i < 3 else 5)
        base.add_ball(points, end, 7)
        tips.append(end)

    branch_count = [0, 22, 56, 96, 138][stage]
    for i in range(branch_count):
        parent = tips[int(rng.integers(0, len(tips)))]
        outward = _unit(parent - np.array([0.0, 0.0, -8.0]))
        curl = np.array([
            math.sin(0.27 * i + 0.8 * stage),
            math.cos(0.31 * i + 0.5 * stage),
            math.sin(0.19 * i),
        ])
        direction = _unit(0.85 * outward + 0.42 * curl + rng.normal(0, 0.55, 3))
        length = float(rng.uniform(8.0, 21.0) * (1.0 - 0.0022 * i))
        end = parent + direction * max(6.5, length)
        radius = 5 if i < 14 else (4 if i < 44 else (3 if i < 90 else 2))
        base.add_tube(points, parent, end, radius)
        base.add_ball(points, end, int(rng.integers(4, 8)))
        if i % 4 == 0:
            mid = 0.55 * parent + 0.45 * end + rng.normal(0, 1.7, 3)
            base.add_ball(points, mid, int(rng.integers(3, 6)))
        if stage >= 3 and i % 5 == 1:
            side = _unit(np.cross(direction, rng.normal(0, 1, 3)) + rng.normal(0, 0.2, 3))
            twig = end + side * rng.uniform(5.0, 12.0)
            base.add_tube(points, end, twig, 2)
            base.add_ball(points, twig, int(rng.integers(2, 5)))
        tips.append(end)

    if stage >= 2:
        # Small stabilizing ribs are part of the grammar scaffold; they should
        # not be visually dominant, but they keep deep stages root-addressable.
        for idx in range(1, min(len(tips), 9), 2):
            base.add_tube(points, root + np.array([0, 0, 4], dtype=float), tips[idx], 2)

    return base.coords_array(points)


def porous_mineral_stage(stage: int, seed: int = 20260517) -> np.ndarray:
    """Connected porous mineral/coral stage sequence with conservative pores."""
    rng = np.random.default_rng(seed)
    points: set[tuple[int, int, int]] = set()
    anchors = [
        np.array([0.0, 0.0, 0.0]),
        np.array([20.0, -7.0, 8.0]),
        np.array([-18.0, 12.0, -5.0]),
        np.array([8.0, 20.0, 15.0]),
        np.array([-10.0, -18.0, 13.0]),
        np.array([stage * 4.0, 4.0 - stage, 22.0]),
    ]
    for a, b in zip(anchors[:-1], anchors[1:]):
        base.add_tube(points, a, b, 7)
    for a in anchors[: 3 + stage]:
        base.add_ball(points, a, 10 + stage)

    for i in range([0, 18, 40, 68, 92][stage]):
        a = anchors[int(rng.integers(0, min(len(anchors), 3 + stage)))]
        p = a + rng.normal(0, 8.0 + stage, 3)
        base.add_tube(points, a, p, int(rng.integers(3, 6)))
        base.add_ball(points, p, int(rng.integers(4, 8)))

    for i in range([0, 5, 11, 18, 26][stage]):
        a = anchors[int(rng.integers(0, min(len(anchors), 3 + stage)))]
        p = a + rng.normal(0, 8.0, 3)
        base.remove_ball(points, p, int(rng.integers(2, 5)))

    # Repaint the main beams after pore subtraction so that the root scaffold
    # remains connected even when local holes are introduced.
    for a, b in zip(anchors[:-1], anchors[1:]):
        base.add_tube(points, a, b, 4)
    return base.coords_array(points)


def write_rows(out_dir: Path, rows: list[dict]) -> None:
    if not rows:
        return
    keys = sorted({k for row in rows for k in row})
    with (out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "metrics.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


def generate(out_dir: Path, family: str) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for stage in range(1, 5):
        if family == "volumetric_coral_depth":
            coords = volumetric_coral_stage(stage)
        elif family == "porous_mineral_depth":
            coords = porous_mineral_stage(stage)
        else:
            raise ValueError(f"unknown family: {family}")
        coords = base.largest_occupancy_component(coords)
        mesh = base.coords_to_mesh(coords)
        label = f"{family}_stage_{stage:02d}"
        case_dir = out_dir / label
        case_dir.mkdir(parents=True, exist_ok=True)
        obj = case_dir / f"{label}.obj"
        mesh.export(obj)
        row = {"label": label, "family": family, "stage": stage, "obj_path": str(obj)}
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
    parser.add_argument("--family", choices=["volumetric_coral_depth", "porous_mineral_depth"], default="volumetric_coral_depth")
    args = parser.parse_args()
    summary = generate(args.out, args.family)
    print(json.dumps({"out_dir": summary["out_dir"], "family": summary["family"], "contact_sheet": summary["contact_sheet"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
