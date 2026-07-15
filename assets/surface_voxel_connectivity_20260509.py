#!/usr/bin/env python3
"""Surface-sampled voxel connectivity diagnostics for textured recursive meshes.

Raw GLB face connectivity is a poor paper-facing metric for the current
Trellis2 texture exports because UV/material seams split otherwise touching
surface patches into many triangle islands. This script instead samples mesh
surfaces, voxelizes the samples, optionally dilates the occupied voxels by a
small radius, and reports 6-neighborhood connected components.

The metric is intentionally framed as a renderability/connectivity diagnostic,
not as a watertight-topology proof.
"""

from __future__ import annotations

import csv
import json
from collections import deque
from pathlib import Path
from typing import Iterable

import numpy as np

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - figure output is optional.
    plt = None


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
OUT_DIR = ROOT / "results" / "surface_voxel_connectivity_20260509"
FIG_DIR = ROOT / "paper_siga" / "figures"
OUT_CSV = OUT_DIR / "surface_voxel_connectivity_summary.csv"
OUT_JSON = OUT_DIR / "surface_voxel_connectivity_summary.json"
OUT_PNG = FIG_DIR / "surface_voxel_connectivity_metric_20260509.png"
OUT_PDF = FIG_DIR / "surface_voxel_connectivity_metric_20260509.pdf"


FAMILY_ORDER = ["pyrite_hq_glb", "bismuth_hq_glb", "porous_mineral_glb", "pyrite_source_obj", "bismuth_source_obj", "porous_source_obj"]
FAMILY_LABELS = {
    "pyrite_hq_glb": "Pyrite HQ GLB",
    "bismuth_hq_glb": "Bismuth HQ GLB",
    "porous_mineral_glb": "Porous GLB",
    "pyrite_source_obj": "Pyrite source",
    "bismuth_source_obj": "Bismuth source",
    "porous_source_obj": "Porous source",
}


def load_mesh_points(path: Path, sample_count: int, seed: int) -> tuple[np.ndarray, dict[str, object]]:
    import trimesh

    loaded = trimesh.load(str(path), force=None, process=False)
    meshes = []
    if hasattr(loaded, "geometry"):
        meshes = [m for m in loaded.geometry.values() if hasattr(m, "vertices")]
    elif hasattr(loaded, "vertices"):
        meshes = [loaded]

    rng = np.random.default_rng(seed)
    point_chunks: list[np.ndarray] = []
    total_vertices = 0
    total_faces = 0
    sampled_faces = 0

    valid_meshes = []
    for mesh in meshes:
        vertices = np.asarray(mesh.vertices, dtype=np.float64)
        faces = np.asarray(getattr(mesh, "faces", []), dtype=np.int64)
        if len(vertices) == 0:
            continue
        total_vertices += len(vertices)
        total_faces += len(faces)
        point_chunks.append(vertices)
        if len(faces) > 0:
            valid = faces[(faces >= 0).all(axis=1) & (faces < len(vertices)).all(axis=1)]
            if len(valid) > 0:
                tri = vertices[valid[:, :3]]
                point_chunks.append(tri.mean(axis=1))
                valid_meshes.append(mesh)
                sampled_faces += len(valid)

    if valid_meshes and sample_count > 0:
        # Allocate samples proportional to face count, with a minimum so small
        # scene nodes remain represented.
        face_counts = np.asarray([len(getattr(m, "faces", [])) for m in valid_meshes], dtype=np.float64)
        weights = face_counts / max(float(face_counts.sum()), 1.0)
        for mesh, weight in zip(valid_meshes, weights):
            count = max(512, int(sample_count * float(weight)))
            try:
                # trimesh's sampler uses numpy's global RNG in some versions.
                state = np.random.get_state()
                np.random.seed(int(rng.integers(0, 2**31 - 1)))
                pts, _ = trimesh.sample.sample_surface(mesh, count=count)
                np.random.set_state(state)
                if len(pts):
                    point_chunks.append(np.asarray(pts, dtype=np.float64))
            except Exception:
                # Vertices/centroids still give a deterministic fallback.
                try:
                    np.random.set_state(state)
                except Exception:
                    pass

    points = np.vstack(point_chunks) if point_chunks else np.zeros((0, 3), dtype=np.float64)
    return points, {
        "vertices": int(total_vertices),
        "faces": int(total_faces),
        "surface_face_samples": int(sampled_faces),
        "sample_points": int(len(points)),
        "loader_status": "ok" if len(points) else "empty",
    }


def voxelize(points: np.ndarray, resolution: int) -> np.ndarray:
    if len(points) == 0:
        return np.zeros((0, 3), dtype=np.int16)
    vmin = points.min(axis=0)
    vmax = points.max(axis=0)
    extent = vmax - vmin
    max_extent = float(np.max(extent))
    if max_extent <= 1e-12:
        return np.zeros((1, 3), dtype=np.int16)
    norm = (points - vmin) / max_extent
    coords = np.floor(norm * (resolution - 1e-9)).astype(np.int16)
    coords = np.clip(coords, 0, resolution - 1)
    return np.unique(coords, axis=0)


def dilation_offsets(radius: int) -> list[tuple[int, int, int]]:
    offsets = []
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                if max(abs(dx), abs(dy), abs(dz)) <= radius:
                    offsets.append((dx, dy, dz))
    return offsets


def dilate(coords: np.ndarray, resolution: int, radius: int) -> np.ndarray:
    if radius <= 0 or len(coords) == 0:
        return coords
    occupied = set()
    for x, y, z in coords.astype(np.int32):
        for dx, dy, dz in dilation_offsets(radius):
            nx, ny, nz = int(x + dx), int(y + dy), int(z + dz)
            if 0 <= nx < resolution and 0 <= ny < resolution and 0 <= nz < resolution:
                occupied.add((nx, ny, nz))
    return np.asarray(sorted(occupied), dtype=np.int16)


def component_stats(coords: np.ndarray) -> tuple[int, int, float]:
    if len(coords) == 0:
        return 0, 0, 0.0
    occupied = {tuple(map(int, c)) for c in coords}
    seen: set[tuple[int, int, int]] = set()
    dirs = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    components = 0
    largest = 0
    for start in occupied:
        if start in seen:
            continue
        components += 1
        count = 0
        q: deque[tuple[int, int, int]] = deque([start])
        seen.add(start)
        while q:
            cur = q.popleft()
            count += 1
            for dx, dy, dz in dirs:
                nxt = (cur[0] + dx, cur[1] + dy, cur[2] + dz)
                if nxt in occupied and nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        largest = max(largest, count)
    return components, largest, float(largest / max(len(coords), 1))


def box_dimension(coords_by_res: dict[int, np.ndarray]) -> float | str:
    usable = [(res, len(coords)) for res, coords in coords_by_res.items() if res > 1 and len(coords) > 0]
    if len(usable) < 2:
        return ""
    xs = np.log([r for r, _ in usable])
    ys = np.log([c for _, c in usable])
    return float(np.polyfit(xs, ys, 1)[0])


def default_cases() -> list[tuple[str, str, int, Path]]:
    cases: list[tuple[str, str, int, Path]] = []
    pyrite_glb = ROOT / "visuals" / "pyrite_depth_hq_warm_showcase_20260509"
    bismuth_glb = ROOT / "visuals" / "bismuth_depth_hq_warm_showcase_20260509"
    porous_glb = ROOT / "visuals" / "porous_mineral_depth_textured_showcase_20260509"
    for stage in range(1, 5):
        cases.append((f"pyrite_hq_stage{stage:02d}", "pyrite_hq_glb", stage, pyrite_glb / f"stage{stage:02d}_textured.glb"))
        cases.append((f"bismuth_hq_stage{stage:02d}", "bismuth_hq_glb", stage, bismuth_glb / f"stage{stage:02d}_textured.glb"))
        cases.append(
            (
                f"porous_mineral_stage{stage:02d}",
                "porous_mineral_glb",
                stage,
                porous_glb / f"porous_mineral_depth_stage_{stage:02d}_coral_steps6_tex1024_xformers" / "textured.glb",
            )
        )
        cases.append(
            (
                f"pyrite_source_stage{stage:02d}",
                "pyrite_source_obj",
                stage,
                ROOT
                / "results"
                / "connected_scaffold_depth_cases_20260509"
                / "pyrite_lattice_depth"
                / f"pyrite_lattice_depth_stage_{stage:02d}"
                / f"pyrite_lattice_depth_stage_{stage:02d}.obj",
            )
        )
        cases.append(
            (
                f"bismuth_source_stage{stage:02d}",
                "bismuth_source_obj",
                stage,
                ROOT
                / "results"
                / "connected_scaffold_depth_cases_20260509"
                / "bismuth_hopper_depth"
                / f"bismuth_hopper_depth_stage_{stage:02d}"
                / f"bismuth_hopper_depth_stage_{stage:02d}.obj",
            )
        )
        cases.append(
            (
                f"porous_source_stage{stage:02d}",
                "porous_source_obj",
                stage,
                ROOT
                / "results"
                / "connected_coral_depth_cases_20260509"
                / "porous_mineral_depth"
                / f"porous_mineral_depth_stage_{stage:02d}"
                / f"porous_mineral_depth_stage_{stage:02d}.obj",
            )
        )
    return cases


def metric_case(label: str, family: str, stage: int, path: Path, resolutions: Iterable[int], dilation_radii: Iterable[int]) -> dict[str, object]:
    row: dict[str, object] = {
        "label": label,
        "family": family,
        "stage": stage,
        "path": str(path),
        "exists": path.exists(),
    }
    if not path.exists():
        row["loader_status"] = "missing"
        return row

    points, meta = load_mesh_points(path, sample_count=120000, seed=stage + len(family))
    row.update(meta)
    coords_by_res = {int(res): voxelize(points, int(res)) for res in resolutions}
    row["surface_box_count_dimension_proxy"] = box_dimension(coords_by_res)
    for res, coords in coords_by_res.items():
        row[f"surface_occ{res}_voxels_r0"] = int(len(coords))
        for radius in dilation_radii:
            dcoords = dilate(coords, res, int(radius))
            comps, largest, lcr = component_stats(dcoords)
            row[f"surface_occ{res}_r{radius}_components_6n"] = comps
            row[f"surface_occ{res}_r{radius}_largest_voxels_6n"] = largest
            row[f"surface_occ{res}_r{radius}_lcr_6n"] = lcr
            row[f"surface_occ{res}_r{radius}_occupied_voxels"] = int(len(dcoords))
    return row


def write_outputs(rows: list[dict[str, object]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "metric_schema": "surface_voxel_connectivity_20260509",
        "rows": rows,
        "notes": [
            "Surface samples include vertices, triangle centroids, and stochastic surface samples.",
            "Connectivity uses 6-neighborhood voxel components after optional Chebyshev dilation.",
            "Use radius 0 as a strict sampled-surface proxy and radius 1 as a seam/alias-tolerant renderability proxy.",
            "This is not a proof of watertight topology or physical growth correctness.",
        ],
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    fields = sorted({key for row in rows for key in row.keys()})
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def draw_figure(rows: list[dict[str, object]]) -> None:
    if plt is None:
        return
    plot_rows = [r for r in rows if r.get("exists") and str(r.get("family", "")).endswith("_glb")]
    colors = {"pyrite_hq_glb": "#4B6F8F", "bismuth_hq_glb": "#95835F", "porous_mineral_glb": "#5F8D77"}
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.25), sharex=True)
    for ax, radius in zip(axes, [0, 1]):
        for family in ["pyrite_hq_glb", "bismuth_hq_glb", "porous_mineral_glb"]:
            fam_rows = sorted([r for r in plot_rows if r.get("family") == family], key=lambda x: int(x["stage"]))
            xs = [int(r["stage"]) for r in fam_rows]
            ys = [float(r.get(f"surface_occ64_r{radius}_lcr_6n", 0.0)) for r in fam_rows]
            comps = [int(r.get(f"surface_occ64_r{radius}_components_6n", 0)) for r in fam_rows]
            ax.plot(xs, ys, marker="o", linewidth=2.0, markersize=4.5, color=colors[family], label=FAMILY_LABELS[family])
            for x, y, c in zip(xs, ys, comps):
                ax.text(x, min(1.01, y + 0.018), str(c), ha="center", va="bottom", fontsize=7, color=colors[family])
        ax.set_title(f"surface occupancy, radius {radius}", fontsize=10)
        ax.set_xlabel("recursive depth")
        ax.set_ylim(0.0, 1.05)
        ax.set_xticks([1, 2, 3, 4])
        ax.grid(True, color="#E7E2D9", linewidth=0.8)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("largest component ratio")
    axes[1].legend(frameon=False, fontsize=8, loc="lower right")
    fig.suptitle("Surface-voxel connectivity diagnostic for textured GLB exports", fontsize=11, y=1.02)
    fig.text(
        0.5,
        -0.03,
        "Numbers above markers are component counts. Radius 1 is seam/alias-tolerant and should be read as renderability evidence, not a topology proof.",
        ha="center",
        va="top",
        fontsize=8,
        color="#555555",
    )
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight", pad_inches=0.08)
    fig.savefig(OUT_PDF, bbox_inches="tight", pad_inches=0.08)


def main() -> None:
    rows = []
    for label, family, stage, path in default_cases():
        print(f"[surface-metric] {label}: {path}")
        rows.append(metric_case(label, family, stage, path, resolutions=[32, 64, 96], dilation_radii=[0, 1]))
    write_outputs(rows)
    draw_figure(rows)
    print(OUT_CSV)
    print(OUT_JSON)
    print(OUT_PNG)
    print(OUT_PDF)


if __name__ == "__main__":
    main()
