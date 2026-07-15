#!/usr/bin/env python3
"""Generate connected parameter-control scaffold meshes for PS-RSLG demos.

The depth-control strips show recursive stage changes.  This script keeps the
recursive family and stage fixed while changing a grammar parameter.  The
outputs are connected OBJ meshes intended for Trellis2 PBR texturing and
paper/supplement method-control figures.
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


DEFAULT_OUT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/connected_parameter_cases_20260509")


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n < 1e-8:
        return np.array([0.0, 0.0, 1.0])
    return v / n


def coral_density_case(density: float, seed: int = 20260519) -> np.ndarray:
    """Connected coral-like scaffold with fixed stage and varying density.

    The persistent trunk, seed arms, and stabilizing ribs are part of the
    grammar state.  The density parameter changes how many typed growth handles
    are expanded and how strongly they curl, but every new module is attached to
    an existing handle by construction.
    """
    rng = np.random.default_rng(seed)
    points: set[tuple[int, int, int]] = set()
    root = np.array([0.0, 0.0, -25.0])
    base.add_ball(points, root, 8)
    tips = [root]

    seed_dirs = [
        np.array([1.00, 0.22, 0.76]),
        np.array([-0.78, 0.84, 0.58]),
        np.array([0.10, -1.00, 0.92]),
        np.array([0.56, 0.60, -0.52]),
        np.array([-0.46, -0.50, 1.08]),
    ]
    for i, direction in enumerate(seed_dirs):
        d = _unit(direction)
        length = 26.0 + 4.5 * i + 5.0 * density
        end = root + d * length
        radius = 6 if i < 3 else 5
        base.add_tube(points, root, end, radius)
        base.add_ball(points, end, 7)
        tips.append(end)

    branch_count = int(round(56 + 96 * density))
    curl_gain = 0.25 + 0.65 * density
    reach_gain = 0.72 + 0.38 * density
    for i in range(branch_count):
        parent = tips[int(rng.integers(0, len(tips)))]
        outward = _unit(parent - np.array([0.0, 0.0, -7.0]))
        curl = np.array([
            math.sin(0.23 * i + 1.1 * density),
            math.cos(0.29 * i + 0.7 * density),
            math.sin(0.17 * i + 0.3),
        ])
        direction = _unit(0.78 * outward + curl_gain * curl + rng.normal(0, 0.44, 3))
        length = float(rng.uniform(7.0, 20.0) * reach_gain * (1.0 - 0.0019 * i))
        end = parent + direction * max(5.8, length)
        radius = 5 if i < 12 else (4 if i < 36 else (3 if i < 88 else 2))
        base.add_tube(points, parent, end, radius)
        base.add_ball(points, end, int(rng.integers(3, 7)))
        if i % 4 == 0:
            mid = 0.58 * parent + 0.42 * end + rng.normal(0, 1.8, 3)
            base.add_ball(points, mid, int(rng.integers(3, 6)))
        if i % 5 == 1:
            side = _unit(np.cross(direction, rng.normal(0, 1, 3)) + rng.normal(0, 0.25, 3))
            twig = end + side * rng.uniform(4.5, 11.0) * max(0.7, density)
            base.add_tube(points, end, twig, 2)
            base.add_ball(points, twig, int(rng.integers(2, 5)))
        tips.append(end)

    # Root-addressable ribs keep this a single usable asset even at high
    # density; they are thin enough to read as internal scaffold rather than
    # visible post-hoc struts after texturing.
    for idx in range(1, min(len(tips), 12), 2):
        rib_radius = 2 if density < 1.05 else 1
        base.add_tube(points, root + np.array([0, 0, 4], dtype=float), tips[idx], rib_radius)
    return base.coords_array(points)


def write_rows(out_dir: Path, rows: list[dict]) -> None:
    if not rows:
        return
    keys = sorted({key for row in rows for key in row})
    with (out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "metrics.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


def generate(out_dir: Path, family: str, densities: list[float] | None = None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    if family != "coral_density_param":
        raise ValueError(f"unknown family: {family}")
    if densities is None:
        densities = [0.45, 0.70, 0.95, 1.20]
    for density in densities:
        coords = coral_density_case(density)
        coords = base.largest_occupancy_component(coords)
        mesh = base.coords_to_mesh(coords)
        token = f"{density:.2f}".replace(".", "p")
        label = f"{family}_density_{token}"
        case_dir = out_dir / label
        case_dir.mkdir(parents=True, exist_ok=True)
        obj = case_dir / f"{label}.obj"
        mesh.export(obj)
        row = {
            "label": label,
            "family": family,
            "density": density,
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
    parser.add_argument("--family", choices=["coral_density_param"], default="coral_density_param")
    parser.add_argument(
        "--densities",
        type=float,
        nargs="+",
        default=None,
        help="Optional density values for method-behavior endpoint sweeps.",
    )
    args = parser.parse_args()
    summary = generate(args.out / args.family, args.family, args.densities)
    print(json.dumps({"out_dir": summary["out_dir"], "family": summary["family"], "contact_sheet": summary["contact_sheet"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
