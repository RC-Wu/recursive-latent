#!/usr/bin/env python3
"""Cache/sampler connectivity diagnostics for recursive 3D growth.

This is a fast proxy experiment for the TRELLIS sparse-state line.  It tests
whether cache fusion and local masked sampler ideas reduce disconnected
occupancy islands before committing expensive texture export.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import numpy as np


GRID = 64
NEIGHBORS6 = np.asarray(
    [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)],
    dtype=np.int16,
)


def write_obj(path: Path, vertices, faces) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for v in vertices:
            f.write(f"v {float(v[0]):.6f} {float(v[1]):.6f} {float(v[2]):.6f}\n")
        for a, b, c in faces:
            f.write(f"f {int(a) + 1} {int(b) + 1} {int(c) + 1}\n")


@dataclass
class CaseSpec:
    label: str
    kind: str
    candidates: tuple[str, ...]
    synthetic: str
    stable_control: bool = False


CASES = (
    CaseSpec(
        "hard_dla",
        "hard",
        (
            "visuals/siga_night_20260508/selected_meshes/dla_fork_side_s2_a0p25_d3.obj",
            "visuals/siga_night_20260508/projection_pruning_compete_0550/dla_compete_fork_d4_pruned.obj",
            "results/traditional_baselines/run_20260507_0300/dla_cluster_voxels.obj",
        ),
        "dla",
    ),
    CaseSpec(
        "hard_radial",
        "hard",
        (
            "visuals/siga_night_20260508/selected_meshes/transform_radial4_d3.obj",
            "visuals/non_tree_recursive_20260508/meshes/crown_radial_projected_radial4_stage03.obj",
        ),
        "radial",
    ),
    CaseSpec(
        "hard_scifi",
        "hard",
        (
            "visuals/non_tree_recursive_20260508/meshes/scifi_module_projected_translate_stage03.obj",
            "results/public_guide_textured_glb_metrics_20260508/metrics.json",
        ),
        "scifi",
    ),
    CaseSpec(
        "hard_bismuth",
        "hard",
        (
            "visuals/public_guide_textured_glb_20260509b/porous_container_compete_stage03_bismuth_steps8_tex2048_xformers/textured.glb",
            "visuals/public_guide_textured_glb_20260509d/transform_radial4_bismuth_steps8_tex2048_xformers/textured.glb",
        ),
        "bismuth",
    ),
    CaseSpec(
        "control_vine",
        "control",
        (
            "visuals/siga_night_20260508/siga_vine_projection_pruning_0700/minv_1000/vine_compete_d3/mesh_pruned.obj",
            "visuals/siga_night_20260508/siga_vine_projection_pruning_0700/minv_1000/vine_mask_compete_s1_a025_d3/mesh_pruned.obj",
        ),
        "vine",
        True,
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--case-filter", choices=["all", "hard", "control"], default="all")
    parser.add_argument("--seed", type=int, default=20260509)
    parser.add_argument("--grid", type=int, default=GRID)
    parser.add_argument("--write-previews", action="store_true")
    parser.add_argument("--write-selected-meshes", action="store_true")
    return parser.parse_args()


def read_obj_vertices(path: Path) -> np.ndarray:
    vertices = []
    with path.open("r", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
    return np.asarray(vertices, dtype=np.float32)


def load_vertices(path: Path) -> np.ndarray:
    if path.suffix.lower() == ".obj":
        return read_obj_vertices(path)
    try:
        import trimesh

        loaded = trimesh.load(str(path), force="mesh", process=False)
        if hasattr(loaded, "geometry"):
            meshes = [g for g in loaded.geometry.values() if hasattr(g, "vertices")]
            if not meshes:
                return np.empty((0, 3), dtype=np.float32)
            vertices = np.concatenate([np.asarray(m.vertices) for m in meshes], axis=0)
        else:
            vertices = np.asarray(loaded.vertices)
        return vertices.astype(np.float32)
    except Exception:
        return np.empty((0, 3), dtype=np.float32)


def vertices_to_occ(vertices: np.ndarray, grid: int) -> np.ndarray:
    occ = np.zeros((grid, grid, grid), dtype=bool)
    if len(vertices) == 0:
        return occ
    finite = np.isfinite(vertices).all(axis=1)
    pts = vertices[finite]
    if len(pts) == 0:
        return occ
    lo = pts.min(axis=0)
    hi = pts.max(axis=0)
    span = np.maximum(hi - lo, 1e-6)
    norm = (pts - lo) / span
    idx = np.clip(np.round(norm * (grid - 5) + 2), 0, grid - 1).astype(np.int16)
    occ[idx[:, 0], idx[:, 1], idx[:, 2]] = True
    return dilate(occ, 1)


def synthetic_occ(kind: str, grid: int, rng: random.Random) -> np.ndarray:
    occ = np.zeros((grid, grid, grid), dtype=bool)
    c = np.asarray([grid // 2, grid // 2, grid // 2], dtype=np.int16)
    if kind == "dla":
        occ[tuple(c)] = True
        walkers = 1700
        for _ in range(walkers):
            angle = rng.random() * math.tau
            z = rng.uniform(-0.7, 0.7)
            r = grid * 0.38
            p = c + np.asarray([math.cos(angle) * r, math.sin(angle) * r, z * r], dtype=np.float32)
            p = np.clip(np.round(p), 2, grid - 3).astype(np.int16)
            for _step in range(260):
                near = False
                for d in NEIGHBORS6:
                    q = p + d
                    if occ[tuple(q)]:
                        near = True
                        break
                if near:
                    occ[tuple(p)] = True
                    break
                p += np.asarray(rng.choice(NEIGHBORS6.tolist()), dtype=np.int16)
                p = np.clip(p, 2, grid - 3)
        return dilate(occ, 1)
    if kind == "radial":
        for arm in range(8):
            theta = arm * math.tau / 8
            direction = np.asarray([math.cos(theta), math.sin(theta), 0.22 * math.sin(2 * theta)])
            for t in np.linspace(0, grid * 0.34, 92):
                p = np.round(c + direction * t).astype(np.int16)
                p = np.clip(p, 2, grid - 3)
                occ[tuple(p)] = True
                if int(t) % 8 == 0:
                    occ[tuple(np.clip(p + [0, 0, rng.choice([-1, 1]) * 2], 2, grid - 3))] = True
        return dilate(occ, 2)
    if kind == "bismuth":
        for k in range(8):
            lo = 8 + k * 3
            hi = grid - 8 - k * 3
            z = 10 + k * 4
            occ[lo:hi, lo:lo + 3, z:z + 3] = True
            occ[lo:lo + 3, lo:hi, z:z + 3] = True
            occ[hi - 3:hi, lo:hi, z:z + 3] = True
            occ[lo:hi, hi - 3:hi, z:z + 3] = True
        return dilate(occ, 1)
    if kind == "scifi":
        for x in range(10, grid - 10, 10):
            occ[x:x + 5, 26:38, 26:38] = True
            occ[26:38, x:x + 5, 26:38] = True
        for offset in (-14, 14):
            occ[28:36, 28:36, 28 + offset:36 + offset] = True
        return dilate(occ, 1)
    if kind == "vine":
        p = c.copy()
        for i in range(130):
            p = p + np.asarray([rng.choice([-1, 0, 1]), 1 if i % 2 else 0, rng.choice([-1, 0, 1])], dtype=np.int16)
            p = np.clip(p, 3, grid - 4)
            occ[tuple(p)] = True
            if i % 16 == 0:
                for s in (-1, 1):
                    q = p.copy()
                    for j in range(18):
                        q = q + np.asarray([s, 1 if j % 3 == 0 else 0, rng.choice([-1, 0, 1])], dtype=np.int16)
                        q = np.clip(q, 3, grid - 4)
                        occ[tuple(q)] = True
        return dilate(occ, 2)
    raise ValueError(kind)


def dilate(occ: np.ndarray, steps: int = 1) -> np.ndarray:
    out = occ.copy()
    for _ in range(steps):
        grown = out.copy()
        for dx, dy, dz in NEIGHBORS6:
            src = (
                slice(max(0, -dx), out.shape[0] - max(0, dx)),
                slice(max(0, -dy), out.shape[1] - max(0, dy)),
                slice(max(0, -dz), out.shape[2] - max(0, dz)),
            )
            dst = (
                slice(max(0, dx), out.shape[0] - max(0, -dx)),
                slice(max(0, dy), out.shape[1] - max(0, -dy)),
                slice(max(0, dz), out.shape[2] - max(0, -dz)),
            )
            grown[dst] |= out[src]
        out = grown
    return out


def erode(occ: np.ndarray, steps: int = 1) -> np.ndarray:
    out = occ.copy()
    for _ in range(steps):
        kept = out.copy()
        for dx, dy, dz in NEIGHBORS6:
            shifted = np.zeros_like(out)
            src = (
                slice(max(0, -dx), out.shape[0] - max(0, dx)),
                slice(max(0, -dy), out.shape[1] - max(0, dy)),
                slice(max(0, -dz), out.shape[2] - max(0, dz)),
            )
            dst = (
                slice(max(0, dx), out.shape[0] - max(0, -dx)),
                slice(max(0, dy), out.shape[1] - max(0, -dy)),
                slice(max(0, dz), out.shape[2] - max(0, -dz)),
            )
            shifted[dst] = out[src]
            kept &= shifted
        out = kept
    return out


def close_gaps(occ: np.ndarray, steps: int = 1) -> np.ndarray:
    return erode(dilate(occ, steps), steps)


def downsample_any(occ: np.ndarray, factor: int) -> np.ndarray:
    g = occ.shape[0] // factor
    return occ[: g * factor, : g * factor, : g * factor].reshape(g, factor, g, factor, g, factor).any(axis=(1, 3, 5))


def upsample(occ: np.ndarray, factor: int, grid: int) -> np.ndarray:
    return np.repeat(np.repeat(np.repeat(occ, factor, axis=0), factor, axis=1), factor, axis=2)[:grid, :grid, :grid]


def components(occ: np.ndarray) -> list[np.ndarray]:
    points = np.argwhere(occ)
    if len(points) == 0:
        return []
    seen = np.zeros_like(occ, dtype=bool)
    comps = []
    for start in points:
        st = tuple(int(x) for x in start)
        if seen[st]:
            continue
        q = deque([st])
        seen[st] = True
        comp = []
        while q:
            p = q.popleft()
            comp.append(p)
            arr = np.asarray(p, dtype=np.int16)
            for d in NEIGHBORS6:
                nb = arr + d
                if (nb < 0).any() or (nb >= occ.shape[0]).any():
                    continue
                nt = tuple(int(x) for x in nb)
                if occ[nt] and not seen[nt]:
                    seen[nt] = True
                    q.append(nt)
        comps.append(np.asarray(comp, dtype=np.int16))
    comps.sort(key=len, reverse=True)
    return comps


def metrics(occ: np.ndarray) -> dict:
    comps = components(occ)
    count = int(occ.sum())
    largest = int(len(comps[0])) if comps else 0
    pts = np.argwhere(occ)
    if len(pts):
        extent = pts.max(axis=0) - pts.min(axis=0) + 1
        bbox_volume = int(np.prod(extent))
    else:
        extent = np.zeros(3, dtype=int)
        bbox_volume = 0
    boundary = dilate(occ, 1) & ~erode(occ, 1)
    return {
        "voxels": count,
        "component_count": int(len(comps)),
        "largest_component_voxels": largest,
        "largest_component_ratio": float(largest / max(count, 1)),
        "fragmentation_score": float(1.0 - largest / max(count, 1)),
        "small_components_lt32": int(sum(len(c) < 32 for c in comps)),
        "bbox_volume": bbox_volume,
        "occupancy_density": float(count / max(bbox_volume, 1)),
        "boundary_voxels": int(boundary.sum()),
    }


def translate_occ(occ: np.ndarray, delta: tuple[int, int, int]) -> np.ndarray:
    out = np.zeros_like(occ)
    dx, dy, dz = delta
    src = (
        slice(max(0, -dx), occ.shape[0] - max(0, dx)),
        slice(max(0, -dy), occ.shape[1] - max(0, dy)),
        slice(max(0, -dz), occ.shape[2] - max(0, dz)),
    )
    dst = (
        slice(max(0, dx), occ.shape[0] - max(0, -dx)),
        slice(max(0, dy), occ.shape[1] - max(0, -dy)),
        slice(max(0, dz), occ.shape[2] - max(0, -dz)),
    )
    out[dst] = occ[src]
    return out


def motif_mask(occ: np.ndarray) -> np.ndarray:
    pts = np.argwhere(occ)
    if len(pts) == 0:
        return occ.copy()
    threshold = np.quantile(pts[:, 1], 0.62)
    mask = np.zeros_like(occ)
    selected = pts[pts[:, 1] >= threshold]
    mask[selected[:, 0], selected[:, 1], selected[:, 2]] = True
    return mask


def line_bridge(occ: np.ndarray, a: np.ndarray, b: np.ndarray) -> None:
    steps = int(max(np.abs(b - a).max(), 1))
    for t in range(steps + 1):
        p = np.round(a + (b - a) * (t / steps)).astype(int)
        if (p >= 0).all() and (p < occ.shape[0]).all():
            occ[tuple(p)] = True


def bridge_components(occ: np.ndarray, max_bridges: int = 8) -> np.ndarray:
    out = occ.copy()
    comps = components(out)
    if len(comps) <= 1:
        return out
    main = comps[0]
    main_centroid = main.mean(axis=0)
    for comp in comps[1 : max_bridges + 1]:
        if len(comp) < 8:
            continue
        a = comp[np.argmin(np.linalg.norm(comp - main_centroid, axis=1))]
        b = main[np.argmin(np.linalg.norm(main - a, axis=1))]
        line_bridge(out, a, b)
    return dilate(out, 1)


def naive_transform_copies(base: np.ndarray) -> np.ndarray:
    motif = motif_mask(base)
    return base | translate_occ(motif, (9, 6, -3)) | translate_occ(motif, (-9, 6, 3))


def cached_motif_predecode_fusion(base: np.ndarray) -> np.ndarray:
    fused = naive_transform_copies(base)
    return close_gaps(bridge_components(fused, 10), 1)


def lod_cache_fusion(base: np.ndarray) -> np.ndarray:
    high = naive_transform_copies(base)
    low = upsample(close_gaps(downsample_any(high, 4), 1), 4, high.shape[0])
    return high | (low & dilate(high, 2))


def sliding_window_cache_fusion(base: np.ndarray, window: int = 24, stride: int = 12) -> np.ndarray:
    high = naive_transform_copies(base)
    out = high.copy()
    grid = high.shape[0]
    for x in range(0, grid - window + 1, stride):
        for y in range(0, grid - window + 1, stride):
            for z in range(0, grid - window + 1, stride):
                tile = high[x : x + window, y : y + window, z : z + window]
                comps = components(tile)
                if len(comps) <= 1:
                    continue
                keep = np.zeros_like(tile)
                for comp in comps[:3]:
                    keep[comp[:, 0], comp[:, 1], comp[:, 2]] = True
                out[x : x + window, y : y + window, z : z + window] |= close_gaps(keep, 1)
    return out


def masked_local_sampler(base: np.ndarray) -> np.ndarray:
    growth = naive_transform_copies(base)
    local = dilate(growth ^ base, 2) | (dilate(growth, 1) & ~erode(growth, 1))
    repaired = growth.copy()
    candidate = bridge_components(growth, 10)
    repaired[local] |= candidate[local]
    return close_gaps(repaired, 1)


def score_for_export(row: dict) -> float:
    return (
        20.0 * row["component_count"]
        + 100.0 * row["fragmentation_score"]
        + 0.0002 * row["voxels"]
        - 30.0 * row["largest_component_ratio"]
    )


METHODS = (
    ("naive_transformed_copies", naive_transform_copies),
    ("transform_cache_predecode_fusion", cached_motif_predecode_fusion),
    ("lod_cache_fusion", lod_cache_fusion),
    ("sliding_window_cache_fusion", sliding_window_cache_fusion),
    ("masked_local_sampler_boundary_schedule", masked_local_sampler),
)


def choose_source(root: Path, spec: CaseSpec, grid: int, rng: random.Random) -> tuple[np.ndarray, str]:
    for rel in spec.candidates:
        path = root / rel
        if path.exists() and path.suffix.lower() in {".obj", ".glb", ".ply"}:
            vertices = load_vertices(path)
            occ = vertices_to_occ(vertices, grid)
            if occ.sum() > 0:
                return occ, str(path)
    return synthetic_occ(spec.synthetic, grid, rng), f"synthetic:{spec.synthetic}"


def preview(path: Path, occ: np.ndarray, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pts = np.argwhere(occ)
    fig = plt.figure(figsize=(4, 4))
    ax = fig.add_subplot(111)
    if len(pts):
        ax.scatter(pts[:, 0], pts[:, 1], s=0.12, c=pts[:, 2], cmap="viridis")
    ax.set_title(title, fontsize=8)
    ax.set_aspect("equal")
    ax.set_axis_off()
    fig.tight_layout(pad=0.1)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def write_voxel_surface_obj(path: Path, occ: np.ndarray) -> dict:
    """Write a lightweight boundary-surface OBJ for a voxel occupancy set."""
    path.parent.mkdir(parents=True, exist_ok=True)
    coords = np.argwhere(occ)
    occupied = {tuple(map(int, p)) for p in coords.tolist()}
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    vindex: dict[tuple[int, int, int], int] = {}

    face_defs = (
        ((1, 0, 0), ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))),
        ((-1, 0, 0), ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0))),
        ((0, 1, 0), ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0))),
        ((0, -1, 0), ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))),
        ((0, 0, 1), ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))),
        ((0, 0, -1), ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0))),
    )

    def get_vid(corner: tuple[int, int, int]) -> int:
        if corner not in vindex:
            vindex[corner] = len(vertices)
            scale = max(occ.shape[0] - 1, 1)
            vertices.append(
                (
                    (corner[0] / scale) - 0.5,
                    (corner[1] / scale) - 0.5,
                    (corner[2] / scale) - 0.5,
                )
            )
        return vindex[corner]

    for p in occupied:
        base = np.asarray(p, dtype=np.int64)
        for normal, corners in face_defs:
            nb = tuple(map(int, (base + np.asarray(normal, dtype=np.int64)).tolist()))
            if nb in occupied:
                continue
            vids = [
                get_vid(tuple(map(int, (base + np.asarray(c, dtype=np.int64)).tolist())))
                for c in corners
            ]
            faces.append((vids[0], vids[1], vids[2]))
            faces.append((vids[0], vids[2], vids[3]))
    write_obj(path, vertices, faces)
    return {"mesh_path": str(path), "mesh_vertices": len(vertices), "mesh_faces": len(faces)}


def write_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = sorted({k for row in rows for k in row.keys()})
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    np.random.seed(args.seed % (2**32 - 1))

    selected = [c for c in CASES if args.case_filter == "all" or c.kind == args.case_filter]
    rows: list[dict] = []
    selections: list[dict] = []
    start = time.time()
    for spec in selected:
        case_dir = args.out / spec.label
        case_dir.mkdir(parents=True, exist_ok=True)
        base, source = choose_source(args.root, spec, args.grid, rng)
        base_metrics = metrics(base)
        base_row = {
            "case": spec.label,
            "kind": spec.kind,
            "method": "base_input",
            "source": source,
            "stable_control": spec.stable_control,
            **base_metrics,
            "component_delta_vs_naive": 0,
            "lcr_delta_vs_naive": 0.0,
            "selected_for_texture_export": False,
        }
        rows.append(base_row)
        if args.write_previews:
            preview(case_dir / "base_input_xy.png", base, f"{spec.label} base")

        method_rows = []
        naive_metrics = None
        for method, fn in METHODS:
            occ = fn(base)
            met = metrics(occ)
            if method == "naive_transformed_copies":
                naive_metrics = met
            row = {
                "case": spec.label,
                "kind": spec.kind,
                "method": method,
                "source": source,
                "stable_control": spec.stable_control,
                **met,
                "component_delta_vs_naive": 0,
                "lcr_delta_vs_naive": 0.0,
                "selected_for_texture_export": False,
            }
            method_rows.append(row)
            if args.write_previews:
                preview(case_dir / f"{method}_xy.png", occ, f"{spec.label} {method}")
        assert naive_metrics is not None
        for row in method_rows:
            row["component_delta_vs_naive"] = int(row["component_count"] - naive_metrics["component_count"])
            row["lcr_delta_vs_naive"] = float(row["largest_component_ratio"] - naive_metrics["largest_component_ratio"])
            row["export_score"] = score_for_export(row)
        best = min(method_rows, key=score_for_export)
        best["selected_for_texture_export"] = True
        if args.write_selected_meshes:
            selected_occ = None
            for method, fn in METHODS:
                if method == best["method"]:
                    selected_occ = fn(base)
                    break
            if selected_occ is not None:
                mesh_meta = write_voxel_surface_obj(case_dir / f"{best['method']}_selected_surface.obj", selected_occ)
                best.update(mesh_meta)
        selections.append(
            {
                "case": spec.label,
                "source": source,
                "selected_method": best["method"],
                "component_count": best["component_count"],
                "largest_component_ratio": best["largest_component_ratio"],
                "component_delta_vs_naive": best["component_delta_vs_naive"],
                "lcr_delta_vs_naive": best["lcr_delta_vs_naive"],
                "mesh_path": best.get("mesh_path", ""),
                "mesh_vertices": best.get("mesh_vertices", ""),
                "mesh_faces": best.get("mesh_faces", ""),
            }
        )
        rows.extend(method_rows)

    hard = [r for r in rows if r["kind"] == "hard" and r["method"] != "base_input"]
    best_by_case = [s for s in selections if s["case"].startswith("hard_")]
    mean_lcr_gain = float(np.mean([s["lcr_delta_vs_naive"] for s in best_by_case])) if best_by_case else 0.0
    mean_comp_drop = float(np.mean([-s["component_delta_vs_naive"] for s in best_by_case])) if best_by_case else 0.0
    viable = bool(best_by_case and mean_lcr_gain > 0.05 and mean_comp_drop > 2)
    summary = {
        "kind": "cache_sampler_connectivity_20260509",
        "root": str(args.root),
        "out": str(args.out),
        "grid": args.grid,
        "seed": args.seed,
        "case_filter": args.case_filter,
        "methods": [name for name, _ in METHODS],
        "rows": rows,
        "projection_aware_texture_selection": selections,
        "aggregate": {
            "hard_method_rows": len(hard),
            "hard_cases_selected": len(best_by_case),
            "mean_best_lcr_gain_vs_naive": mean_lcr_gain,
            "mean_best_component_drop_vs_naive": mean_comp_drop,
            "viable_paper_contribution": viable,
            "interpretation": (
                "viable as an ablation/supporting contribution if repeated with true TRELLIS decode"
                if viable
                else "useful diagnostic, but needs stronger true-decode evidence before claiming contribution"
            ),
        },
        "seconds": time.time() - start,
        "env": {
            "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
            "TMPDIR": os.environ.get("TMPDIR", ""),
            "HF_HOME": os.environ.get("HF_HOME", ""),
            "XDG_CACHE_HOME": os.environ.get("XDG_CACHE_HOME", ""),
            "TORCH_HOME": os.environ.get("TORCH_HOME", ""),
            "TRITON_CACHE_DIR": os.environ.get("TRITON_CACHE_DIR", ""),
            "MPLCONFIGDIR": os.environ.get("MPLCONFIGDIR", ""),
        },
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
    write_csv(args.out / "metrics.csv", rows)
    write_csv(args.out / "projection_aware_texture_selection.csv", selections)
    print(json.dumps(summary["aggregate"], indent=2))


if __name__ == "__main__":
    main()
