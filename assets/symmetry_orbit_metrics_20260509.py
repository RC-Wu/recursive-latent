#!/usr/bin/env python3
"""Approximate voxel symmetry/orbit metrics for recursive scaffold meshes.

The metric is intentionally lightweight: it voxelizes mesh vertices in a
normalized cube and measures occupancy overlap after simple group transforms.
It is not a proof of exact equivariance. It is a screening metric for
crystal/lattice cases and a paper supplement diagnostic.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


def load_vertices(path: Path) -> np.ndarray:
    if path.suffix.lower() == ".obj":
        verts = []
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("v "):
                    parts = line.split()
                    if len(parts) >= 4:
                        verts.append([float(parts[1]), float(parts[2]), float(parts[3])])
        return np.asarray(verts, dtype=np.float64)
    import trimesh

    obj = trimesh.load(path, force="mesh", process=False)
    return np.asarray(obj.vertices, dtype=np.float64)


def normalize_vertices(vertices: np.ndarray) -> np.ndarray:
    if len(vertices) == 0:
        return vertices
    lo = vertices.min(axis=0)
    hi = vertices.max(axis=0)
    center = (lo + hi) / 2.0
    scale = max(float((hi - lo).max()), 1e-8)
    return (vertices - center) / scale


def voxelize(vertices: np.ndarray, resolution: int) -> set[tuple[int, int, int]]:
    if len(vertices) == 0:
        return set()
    v = np.clip(normalize_vertices(vertices), -0.5, 0.5)
    ijk = np.floor((v + 0.5) * (resolution - 1) + 0.5).astype(np.int32)
    return {tuple(row) for row in ijk.tolist()}


def transform_voxels(voxels: set[tuple[int, int, int]], resolution: int, transform: str) -> set[tuple[int, int, int]]:
    max_i = resolution - 1
    out = set()
    for x, y, z in voxels:
        if transform == "mirror_x":
            out.add((max_i - x, y, z))
        elif transform == "mirror_y":
            out.add((x, max_i - y, z))
        elif transform == "mirror_z":
            out.add((x, y, max_i - z))
        elif transform == "rot90_z":
            out.add((max_i - y, x, z))
        elif transform == "rot180_z":
            out.add((max_i - x, max_i - y, z))
        elif transform == "rot270_z":
            out.add((y, max_i - x, z))
        else:
            raise ValueError(transform)
    return out


def overlap(voxels: set[tuple[int, int, int]], other: set[tuple[int, int, int]]) -> float:
    if not voxels and not other:
        return 1.0
    union = len(voxels | other)
    if union == 0:
        return 0.0
    return len(voxels & other) / union


def metric_one(path: Path, label: str, resolution: int) -> dict:
    verts = load_vertices(path)
    voxels = voxelize(verts, resolution)
    transforms = ["mirror_x", "mirror_y", "mirror_z", "rot90_z", "rot180_z", "rot270_z"]
    scores = {f"{name}_iou": overlap(voxels, transform_voxels(voxels, resolution, name)) for name in transforms}
    mirror_scores = [scores["mirror_x_iou"], scores["mirror_y_iou"], scores["mirror_z_iou"]]
    rot_scores = [scores["rot90_z_iou"], scores["rot180_z_iou"], scores["rot270_z_iou"]]
    return {
        "label": label,
        "path": str(path),
        "vertices": int(len(verts)),
        "resolution": int(resolution),
        "occupied_voxels": int(len(voxels)),
        **scores,
        "mirror_mean_iou": float(np.mean(mirror_scores)),
        "z_rotation_mean_iou": float(np.mean(rot_scores)),
        "symmetry_mean_iou": float(np.mean(mirror_scores + rot_scores)),
    }


def parse_case(item: str) -> tuple[str, Path]:
    if "=" in item:
        label, path = item.split("=", 1)
        return label, Path(path)
    path = Path(item)
    return path.stem, path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", default=[], help="label=path item. May be repeated.")
    parser.add_argument("--resolution", type=int, default=64)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-csv", type=Path, required=True)
    args = parser.parse_args()

    rows = []
    missing = []
    for item in args.case:
        label, path = parse_case(item)
        if not path.exists():
            missing.append({"label": label, "path": str(path)})
            continue
        rows.append(metric_one(path, label, args.resolution))

    summary = {
        "metric_schema": "symmetry_orbit_metrics_20260509",
        "notes": [
            "Voxelized-vertex overlap metric after normalized-centroid alignment.",
            "Use as a screening/supplement diagnostic, not as a proof of exact equivariance.",
        ],
        "rows": rows,
        "missing": missing,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if rows:
        fields = sorted({k for row in rows for k in row})
        args.out_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.out_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
