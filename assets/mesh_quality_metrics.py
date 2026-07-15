#!/usr/bin/env python3
"""Mesh quality metrics for recursive Trellis2 growth outputs."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np


def read_obj(path: Path) -> tuple[np.ndarray, np.ndarray]:
    vertices = []
    faces = []
    with path.open("r", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif line.startswith("f "):
                idx = []
                for token in line.split()[1:4]:
                    idx.append(int(token.split("/")[0]) - 1)
                if len(idx) == 3:
                    faces.append(tuple(idx))
    return np.asarray(vertices, dtype=np.float32), np.asarray(faces, dtype=np.int64)


class UnionFind:
    def __init__(self, n: int):
        self.parent = np.arange(n, dtype=np.int64)
        self.size = np.ones(n, dtype=np.int64)

    def find(self, x: int) -> int:
        parent = self.parent
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = int(parent[x])
        return x

    def union(self, a: int, b: int) -> None:
        ra = self.find(int(a))
        rb = self.find(int(b))
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]


def pca_stats(vertices: np.ndarray, sample_limit: int) -> dict:
    if len(vertices) < 3:
        return {"pca_eigenvalues": [0.0, 0.0, 0.0], "pca_linearity": 0.0, "pca_planarity": 0.0}
    pts = vertices
    if len(pts) > sample_limit:
        idx = np.linspace(0, len(pts) - 1, sample_limit).astype(np.int64)
        pts = pts[idx]
    centered = pts - pts.mean(axis=0, keepdims=True)
    cov = centered.T @ centered / max(len(centered) - 1, 1)
    vals = np.linalg.eigvalsh(cov)[::-1]
    vals = np.maximum(vals, 0.0)
    denom = float(vals[0]) + 1e-12
    linearity = float((vals[0] - vals[1]) / denom)
    planarity = float((vals[1] - vals[2]) / denom)
    return {
        "pca_eigenvalues": [float(x) for x in vals],
        "pca_linearity": linearity,
        "pca_planarity": planarity,
    }


def face_area_stats(vertices: np.ndarray, faces: np.ndarray, sample_limit: int) -> dict:
    if len(faces) == 0:
        return {"face_area_mean": 0.0, "face_area_median": 0.0, "face_area_p95": 0.0, "surface_area_est": 0.0}
    sample = faces
    scale = 1.0
    if len(sample) > sample_limit:
        idx = np.linspace(0, len(sample) - 1, sample_limit).astype(np.int64)
        sample = sample[idx]
        scale = len(faces) / len(sample)
    tri = vertices[sample]
    areas = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
    return {
        "face_area_mean": float(np.mean(areas)),
        "face_area_median": float(np.median(areas)),
        "face_area_p95": float(np.quantile(areas, 0.95)),
        "surface_area_est": float(np.sum(areas) * scale),
    }


def component_stats(vertices: np.ndarray, faces: np.ndarray) -> dict:
    if len(vertices) == 0:
        return {
            "component_count": 0,
            "largest_component_vertices": 0,
            "largest_component_vertex_ratio": 0.0,
            "small_component_count_lt100": 0,
        }
    uf = UnionFind(len(vertices))
    for a, b, c in faces:
        uf.union(int(a), int(b))
        uf.union(int(b), int(c))
    roots = np.fromiter((uf.find(i) for i in range(len(vertices))), dtype=np.int64, count=len(vertices))
    _, counts = np.unique(roots, return_counts=True)
    largest = int(counts.max()) if len(counts) else 0
    return {
        "component_count": int(len(counts)),
        "largest_component_vertices": largest,
        "largest_component_vertex_ratio": float(largest / max(len(vertices), 1)),
        "small_component_count_lt100": int(np.sum(counts < 100)),
    }


def metric_one(path: Path, label: str, sample_limit: int) -> dict:
    vertices, faces = read_obj(path)
    out = {
        "label": label,
        "path": str(path),
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
    }
    if len(vertices):
        vmin = vertices.min(axis=0)
        vmax = vertices.max(axis=0)
        extent = vmax - vmin
        out.update({
            "bbox_min": [float(x) for x in vmin],
            "bbox_max": [float(x) for x in vmax],
            "bbox_extent": [float(x) for x in extent],
            "bbox_volume": float(np.prod(np.maximum(extent, 1e-9))),
            "bbox_diag": float(np.linalg.norm(extent)),
        })
    else:
        out.update({"bbox_min": [0, 0, 0], "bbox_max": [0, 0, 0], "bbox_extent": [0, 0, 0], "bbox_volume": 0.0, "bbox_diag": 0.0})
    out.update(component_stats(vertices, faces))
    out.update(pca_stats(vertices, sample_limit))
    out.update(face_area_stats(vertices, faces, sample_limit))
    out["fragmentation_score"] = float(1.0 - out["largest_component_vertex_ratio"])
    out["density_per_bbox_volume"] = float(len(vertices) / max(out["bbox_volume"], 1e-9))
    return out


def default_cases(root: Path) -> list[tuple[str, Path]]:
    return [
        ("direct_lsystem_fork_side_d3", root / "results/trellis2_recursive_slat_grammar/recursive_slat_grammar_gpu0_20260507_1842/lsystem/fork_side/depth_03/mesh.obj"),
        ("masked_lsystem_fork_side_steps2_d3", root / "results/trellis2_recursive_masked_repair/recursive_masked_repair_gpu0_20260507_1804/lsystem_procedural/fork_side/steps_2/depth_03/masked/mesh.obj"),
        ("blend_lsystem_fork_side_a0p25_d3", root / "results/trellis2_recursive_masked_blend/recursive_masked_blend_gpu0_20260507_1824/lsystem_procedural_blend/fork_side/steps_2/alpha_0p25/depth_03/masked/mesh.obj"),
        ("blend_lsystem_fork_side_a0p5_d3", root / "results/trellis2_recursive_masked_blend/recursive_masked_blend_gpu0_20260507_1824/lsystem_procedural_blend/fork_side/steps_2/alpha_0p5/depth_03/masked/mesh.obj"),
        ("blend_lsystem_fork_a0p5_d3", root / "results/trellis2_recursive_masked_blend/recursive_masked_blend_gpu0_20260507_1824/lsystem_procedural_blend/fork/steps_2/alpha_0p5/depth_03/masked/mesh.obj"),
        ("direct_ifs_fork_side_d3", root / "results/trellis2_recursive_slat_grammar/recursive_slat_grammar_gpu0_20260507_1842/ifs/fork_side/depth_03/mesh.obj"),
        ("masked_ifs_fork_side_steps2_d3", root / "results/trellis2_recursive_masked_repair/recursive_masked_repair_gpu0_20260507_1804/ifs_procedural/fork_side/steps_2/depth_03/masked/mesh.obj"),
        ("blend_ifs_fork_side_a0p25_d3", root / "results/trellis2_recursive_masked_blend/recursive_masked_blend_gpu0_20260507_1824/ifs_procedural_blend/fork_side/steps_2/alpha_0p25/depth_03/masked/mesh.obj"),
        ("blend_ifs_fork_a0p5_d3", root / "results/trellis2_recursive_masked_blend/recursive_masked_blend_gpu0_20260507_1824/ifs_procedural_blend/fork/steps_2/alpha_0p5/depth_03/masked/mesh.obj"),
        ("image_lsystem_warm_blend_fork_a0p25_d2", root / "results/trellis2_recursive_masked_blend/recursive_masked_blend_gpu1_20260507_1824/image_lsystem_warm_blend/fork/steps_2/alpha_0p25/depth_02/masked/mesh.obj"),
        ("dla_masked_radial_steps2_d2", root / "results/trellis2_recursive_masked_repair/recursive_masked_repair_gpu1_20260507_1804/dla_procedural/radial/steps_2/depth_02/masked/mesh.obj"),
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sample-limit", type=int, default=100000)
    parser.add_argument("--case", action="append", default=[], help="label=path")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    cases = []
    if args.case:
        for item in args.case:
            label, raw_path = item.split("=", 1)
            cases.append((label, Path(raw_path)))
    else:
        cases = default_cases(args.root)
    rows = []
    missing = []
    for label, path in cases:
        if not path.exists():
            missing.append({"label": label, "path": str(path)})
            continue
        rows.append(metric_one(path, label, args.sample_limit))
        print(f"done {label}")
    summary = {"rows": rows, "missing": missing}
    (args.out / "mesh_quality_metrics.json").write_text(json.dumps(summary, indent=2))
    if rows:
        fieldnames = sorted({k for row in rows for k in row if not isinstance(row.get(k), (list, dict))})
        with (args.out / "mesh_quality_metrics.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k) for k in fieldnames})


if __name__ == "__main__":
    main()
