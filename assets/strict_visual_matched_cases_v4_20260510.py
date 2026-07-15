#!/usr/bin/env python3
"""V4 strict visual-matched Trellis2 input dry-run generator.

This batch is intentionally local CPU only.  It writes geometry, guide images,
metadata, a Trellis2-ready case list, and initial mesh metrics.  It does not
launch remote jobs and does not modify existing launchers.

V4 differs from V3/V3b in the input geometry strategy:

* plant/tree/root cases use continuous implicit trunk/branch/root occupancy
  plus attached needle/leaf/root-hair supports, instead of disconnected cards or
  a single blocky voxel scaffold;
* DLA/coral/frontier cases keep the same attachment/frontier support but
  surface it as connected smooth implicit tubes with mild bump/porosity;
* crystal/lattice/radial/IFS cases preserve recursive transform readability and
  add bridge/ring/spine support to keep components usable for Trellis2.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import baseline_matrix_20260509 as bm
import connected_scaffold_cases_v2_20260509 as scaffold
import procedural_baselines as pb
import space_colonization_baseline as scb
from strict_matched_psrslg_proxy_20260510 import ifs_tree_skeleton
from strict_matched_task_targets_20260510 import make_frontier_sheet

REMOTE_TARGET = "a100-2"
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_v4_20260510_dryrun"


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _normalize_nodes(nodes: list[np.ndarray], extent: float = 2.35) -> list[np.ndarray]:
    arr = np.asarray(nodes, dtype=float)
    mn, mx = arr.min(axis=0), arr.max(axis=0)
    center = (mn + mx) * 0.5
    scale = max(float((mx - mn).max()), 1e-6)
    return [(np.asarray(n, dtype=float) - center) * (extent / scale) for n in nodes]


def _children(parents: list[int]) -> dict[int, list[int]]:
    out: dict[int, list[int]] = {i: [] for i in range(len(parents))}
    for idx, parent in enumerate(parents):
        if parent >= 0:
            out.setdefault(parent, []).append(idx)
    return out


def _basis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = _unit(axis)
    seed = np.array([0.0, 0.0, 1.0]) if abs(w[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = _unit(np.cross(w, seed))
    v = _unit(np.cross(w, u))
    return u, v, w


def _segment_samples(
    start: np.ndarray,
    end: np.ndarray,
    r0: float,
    r1: float,
    spacing: float,
) -> tuple[list[np.ndarray], list[float]]:
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    length = float(np.linalg.norm(end - start))
    count = max(2, int(math.ceil(length / max(spacing, 1e-4))) + 1)
    pts: list[np.ndarray] = []
    radii: list[float] = []
    for i in range(count):
        t = i / max(count - 1, 1)
        pts.append(start * (1.0 - t) + end * t)
        radii.append(float(r0 * (1.0 - t) + r1 * t))
    return pts, radii


def _skeleton_field_samples(
    nodes: list[np.ndarray],
    parents: list[int],
    base_radius: float,
    taper: float,
    min_radius: float,
    spacing_factor: float = 0.68,
) -> tuple[list[np.ndarray], list[float]]:
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    points: list[np.ndarray] = []
    radii: list[float] = []
    for idx, parent in enumerate(parents):
        if parent < 0:
            continue
        f0 = depths[parent] / max(max_depth, 1)
        f1 = depths[idx] / max(max_depth, 1)
        r0 = max(base_radius * (1.0 - taper * f0), min_radius)
        r1 = max(base_radius * (1.0 - taper * f1), min_radius)
        seg_pts, seg_r = _segment_samples(nodes[parent], nodes[idx], r0, r1, min(r0, r1) * spacing_factor)
        points.extend(seg_pts)
        radii.extend(seg_r)
    return points, radii


def _add_tip_sprays(
    points: list[np.ndarray],
    radii: list[float],
    nodes: list[np.ndarray],
    parents: list[int],
    seed: int,
    mode: str,
) -> dict:
    rng = np.random.default_rng(seed)
    child_map = _children(parents)
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    spray_segments = 0
    for idx, node in enumerate(nodes):
        if idx == 0 or child_map.get(idx) or depths[idx] < max_depth * 0.45:
            continue
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(np.asarray(node) - np.asarray(nodes[parent]))
        u, v, _ = _basis(axis)
        if mode == "pine":
            count, length, radius = 5, (0.12, 0.20), (0.010, 0.004)
            lift = np.array([0.0, 0.0, 0.18])
        elif mode == "leaf":
            count, length, radius = 3, (0.10, 0.18), (0.013, 0.006)
            lift = np.array([0.0, 0.0, 0.08])
        else:
            count, length, radius = 2, (0.10, 0.24), (0.008, 0.003)
            lift = np.array([0.0, 0.0, -0.25])
        for k in range(count):
            theta = 2.0 * math.pi * (k / max(count, 1)) + rng.normal(0, 0.16)
            radial = math.cos(theta) * u + math.sin(theta) * v
            direction = _unit(0.55 * radial + 0.45 * axis + lift + rng.normal(0, 0.04, 3))
            start = np.asarray(node) + radial * rng.uniform(0.006, 0.022)
            end = start + direction * rng.uniform(*length)
            seg_pts, seg_r = _segment_samples(start, end, radius[0], radius[1], radius[1] * 0.90)
            points.extend(seg_pts)
            radii.extend(seg_r)
            spray_segments += 1
    return {"attached_spray_segments": spray_segments, "spray_mode": mode}


def _implicit_surface(
    points: list[np.ndarray] | np.ndarray,
    radii: list[float] | np.ndarray,
    grid: int = 76,
    level: float = 0.52,
    pad: float = 0.22,
    faceted: bool = False,
):
    import trimesh
    from skimage import measure

    pts = np.asarray(points, dtype=np.float32)
    rad = np.asarray(radii, dtype=np.float32)
    if len(pts) == 0:
        raise ValueError("cannot build an implicit surface without support points")
    mn = pts.min(axis=0) - float(rad.max()) * 2.8 - pad
    mx = pts.max(axis=0) + float(rad.max()) * 2.8 + pad
    span = mx - mn
    scale = max(float(span.max()), 1e-6)
    mx = mn + scale
    xs = np.linspace(mn[0], mx[0], grid, dtype=np.float32)
    ys = np.linspace(mn[1], mx[1], grid, dtype=np.float32)
    zs = np.linspace(mn[2], mx[2], grid, dtype=np.float32)
    vol = np.zeros((grid, grid, grid), dtype=np.float32)
    for p, rr in zip(pts, rad):
        support = max(float(rr) * 2.7, scale / grid * 1.4)
        lo = np.maximum(np.floor((p - support - mn) / scale * (grid - 1)).astype(int), 0)
        hi = np.minimum(np.ceil((p + support - mn) / scale * (grid - 1)).astype(int) + 1, grid)
        if np.any(hi <= lo):
            continue
        gx, gy, gz = np.meshgrid(xs[lo[0] : hi[0]], ys[lo[1] : hi[1]], zs[lo[2] : hi[2]], indexing="ij")
        d2 = (gx - p[0]) ** 2 + (gy - p[1]) ** 2 + (gz - p[2]) ** 2
        vol[lo[0] : hi[0], lo[1] : hi[1], lo[2] : hi[2]] += np.exp(-d2 / max(2.0 * rr * rr, 1e-6))
    verts, faces, _normals, _values = measure.marching_cubes(vol, level=level)
    verts = verts / float(grid - 1) * scale + mn
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    pieces = mesh.split(only_watertight=False)
    if pieces:
        mesh = max(pieces, key=lambda p: len(p.vertices))
    center = (mesh.bounds[0] + mesh.bounds[1]) * 0.5
    mesh.apply_translation(-center)
    mesh.apply_scale(2.35 / max(float((mesh.bounds[1] - mesh.bounds[0]).max()), 1e-6))
    if faceted:
        mesh.vertices = np.round(mesh.vertices * 42.0) / 42.0
        mesh.merge_vertices(digits_vertex=5)
        pieces = mesh.split(only_watertight=False)
        if pieces:
            mesh = max(pieces, key=lambda p: len(p.vertices))
    return mesh


def _bump_surface(mesh, amplitude: float, frequency: float):
    if amplitude <= 0.0 or len(mesh.vertices) == 0:
        return mesh
    verts = np.asarray(mesh.vertices, dtype=float)
    normals = np.asarray(mesh.vertex_normals, dtype=float)
    signal = (
        np.sin(verts[:, 0] * frequency + verts[:, 1] * 3.1)
        + 0.55 * np.sin(verts[:, 2] * frequency * 1.37 + verts[:, 0] * 5.3)
        + 0.35 * np.cos((verts[:, 0] + verts[:, 1] - verts[:, 2]) * frequency * 0.73)
    )
    mesh.vertices = verts + normals * (amplitude * signal[:, None])
    return mesh


def _mesh_stats(path: Path) -> dict:
    import trimesh

    mesh = trimesh.load(path, force="mesh", process=False)
    pieces = mesh.split(only_watertight=False)
    sizes = [len(p.vertices) for p in pieces] or [0]
    extent = mesh.bounds[1] - mesh.bounds[0] if len(mesh.vertices) else np.zeros(3)
    return {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "mesh_component_count": int(len(pieces)),
        "largest_mesh_component_vertex_ratio": float(max(sizes) / max(len(mesh.vertices), 1)),
        "bbox_extent": [float(x) for x in extent],
        "bbox_diag": float(np.linalg.norm(extent)),
        "surface_area": float(mesh.area),
    }


def _export_mesh(path: Path, mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(mesh, "export"):
        mesh.export(path)
    else:
        pb.write_obj(path, mesh)


def _write_guides(out_dir: Path) -> dict[str, str]:
    from PIL import Image, ImageDraw, ImageFilter

    guide_dir = out_dir / "_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)

    def stable_seed(name: str) -> int:
        return sum((i + 1) * b for i, b in enumerate(name.encode("utf-8"))) % (2**32)

    def save(name: str, colors: list[tuple[int, int, int]], strokes: str) -> str:
        img = Image.new("RGB", (768, 768), colors[0])
        draw = ImageDraw.Draw(img)
        rng = np.random.default_rng(stable_seed(name))
        for _ in range(520):
            c = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(0, 768))
            y = int(rng.integers(0, 768))
            if strokes == "needles":
                draw.line((x, y, x + int(rng.normal(0, 55)), y + int(rng.normal(-22, 48))), fill=c, width=int(rng.integers(2, 5)))
            elif strokes == "roots":
                draw.line((x, y, x + int(rng.normal(0, 82)), y + int(rng.normal(32, 42))), fill=c, width=int(rng.integers(3, 8)))
            elif strokes == "coral":
                r = int(rng.integers(5, 23))
                draw.ellipse((x - r, y - r, x + r, y + r), fill=c)
            elif strokes == "metal":
                r = int(rng.integers(7, 34))
                draw.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=c)
            else:
                draw.line((x, y, x + int(rng.normal(0, 80)), y + int(rng.normal(0, 80))), fill=c, width=5)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "conifer": save("v4_conifer_needles_bark_pbr_guide.png", [(27, 48, 31), (58, 88, 48), (98, 116, 73), (91, 61, 36)], "needles"),
        "leaf": save("v4_leaf_bark_shell_pbr_guide.png", [(38, 72, 36), (88, 124, 58), (126, 96, 55), (53, 42, 28)], "needles"),
        "root": save("v4_root_bark_pbr_guide.png", [(37, 28, 20), (78, 57, 36), (120, 89, 54), (24, 20, 16)], "roots"),
        "coral": save("v4_coral_porous_pbr_guide.png", [(112, 58, 53), (177, 94, 73), (224, 149, 101), (82, 42, 47)], "coral"),
        "pyrite": save("v4_pyrite_faceted_pbr_guide.png", [(99, 81, 35), (177, 144, 57), (222, 195, 101), (72, 64, 52)], "metal"),
        "bismuth": save("v4_bismuth_faceted_pbr_guide.png", [(87, 62, 125), (56, 132, 143), (184, 107, 80), (220, 187, 90)], "metal"),
        "gear": save("v4_dark_radial_gear_pbr_guide.png", [(34, 37, 34), (91, 97, 84), (158, 128, 76), (88, 42, 32)], "metal"),
    }


def layered_pine_nodes(seed: int) -> tuple[list[np.ndarray], list[int]]:
    rng = np.random.default_rng(seed)
    nodes = [np.array([0.0, 0.0, -1.05 + i * 0.24], dtype=float) for i in range(9)]
    parents = [-1] + list(range(8))
    for level in range(2, 9):
        base = nodes[level]
        radius = 0.59 * (1.0 - 0.074 * level)
        branch_count = 5 if level < 7 else 4
        for k in range(branch_count):
            theta = 2.0 * math.pi * k / branch_count + level * 0.34 + rng.normal(0, 0.035)
            out = _unit(np.array([math.cos(theta), math.sin(theta), 0.10 + 0.025 * level]))
            p1 = base + out * radius
            p2 = p1 + _unit(out + np.array([0.0, 0.0, 0.18])) * radius * 0.42
            i1 = len(nodes)
            nodes.append(p1)
            parents.append(level)
            nodes.append(p2)
            parents.append(i1)
    return _normalize_nodes(nodes, 2.35), parents


def lsys_vine_nodes(seed: int) -> tuple[list[np.ndarray], list[int]]:
    rng = np.random.default_rng(seed)
    nodes = [np.zeros(3, dtype=float)]
    parents = [-1]
    parent = 0
    for level in range(1, 7):
        theta = level * 0.82
        step = np.array([math.cos(theta) * 0.22, math.sin(theta) * 0.22, 0.52])
        nodes.append(nodes[parent] + step)
        current = len(nodes) - 1
        parents.append(parent)
        for sign in (-1, 1):
            side = _unit(np.array([math.cos(theta + sign * 1.35), math.sin(theta + sign * 1.35), 0.15]))
            tip = nodes[current] + side * (0.29 + 0.034 * level) + rng.normal(0, 0.012, 3)
            nodes.append(tip)
            parents.append(current)
            if level >= 3:
                nodes.append(tip + side * 0.16 + np.array([0.0, 0.0, 0.055]))
                parents.append(len(nodes) - 2)
        parent = current
    return _normalize_nodes(nodes, 2.35), parents


def sc_nodes(case: str, seed: int) -> tuple[list[np.ndarray], list[int], dict]:
    attractors = 920 if case != "bush_shell" else 800
    iterations = 170 if case != "bush_shell" else 150
    result = scb.grow_space_colonization(
        case=case,
        attractor_count=attractors,
        iterations=iterations,
        influence_radius=0.24,
        kill_radius=0.055 if case != "bush_shell" else 0.060,
        step_size=0.045,
        seed=seed,
    )
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in result["nodes"]], 2.35)
    controls = {
        "case": case,
        "attractor_count": attractors,
        "iterations": iterations,
        "influence_radius": 0.24,
        "kill_radius": 0.055 if case != "bush_shell" else 0.060,
        "step_size": 0.045,
        "covered_attractors": result.get("covered_attractors"),
        "alive_attractors": result.get("alive_attractors"),
    }
    return nodes, [int(p) for p in result["parents"]], controls


def skeleton_case_mesh(
    nodes: list[np.ndarray],
    parents: list[int],
    seed: int,
    garnish: str,
    base_radius: float,
    taper: float,
    min_radius: float,
    grid: int = 76,
) -> tuple[object, dict]:
    points, radii = _skeleton_field_samples(nodes, parents, base_radius=base_radius, taper=taper, min_radius=min_radius)
    spray = _add_tip_sprays(points, radii, nodes, parents, seed, garnish)
    mesh = _implicit_surface(points, radii, grid=grid, level=0.50 if garnish == "root" else 0.52)
    if garnish in {"pine", "leaf", "root"}:
        mesh = _bump_surface(mesh, amplitude=0.006 if garnish != "root" else 0.004, frequency=16.0)
    return mesh, {
        "support_points": len(points),
        "support_strategy": "continuous implicit trunk-branch-root occupancy",
        "garnish": garnish,
        **spray,
    }


def dla_support(seed: int, mode: str, n_particles: int) -> tuple[np.ndarray, dict]:
    rng = np.random.default_rng(seed)
    if mode == "frontier_sheet":
        pts = make_frontier_sheet(seed, particles=n_particles) * np.array([2.15, 1.55, 1.00])
    else:
        pts = pb.make_dla_cluster(n_particles=n_particles, seed=seed % 10000)
        if mode == "aniso_crystal":
            pts = pts * np.array([1.58, 0.72, 1.08])
        else:
            pts = pts * np.array([1.10, 1.02, 1.22])
    pts = np.asarray(pts, dtype=float)
    if len(pts) > n_particles:
        pts = pts[np.linspace(0, len(pts) - 1, n_particles).astype(int)]
    bridges: list[np.ndarray] = []
    for i in range(1, len(pts)):
        prev = pts[:i]
        j = int(np.argmin(np.linalg.norm(prev - pts[i], axis=1)))
        d = float(np.linalg.norm(prev[j] - pts[i]))
        threshold = 0.28 if mode != "frontier_sheet" else 0.36
        if d <= threshold:
            for t in (0.25, 0.50, 0.75):
                bridges.append(prev[j] * (1.0 - t) + pts[i] * t)
        elif rng.random() < (0.020 if mode == "frontier_sheet" else 0.010):
            bridges.append(prev[j] * 0.5 + pts[i] * 0.5)
    all_pts = np.vstack([pts, np.asarray(bridges, dtype=float)]) if bridges else pts
    return all_pts, {"n_particles": int(n_particles), "bridge_points": len(bridges), "support_points": int(len(all_pts))}


def dla_case_mesh(seed: int, mode: str, n_particles: int) -> tuple[object, dict]:
    pts, ctl = dla_support(seed, mode, n_particles)
    norm = np.linalg.norm(pts, axis=1)
    frontier = norm > np.quantile(norm, 0.70)
    if mode == "aniso_crystal":
        radii = np.where(frontier, 0.066, 0.050)
        mesh = _implicit_surface(pts, radii, grid=70, level=0.54, faceted=True)
        mesh = _bump_surface(mesh, amplitude=0.004, frequency=22.0)
        surface = "connected faceted implicit frontier crystal"
    else:
        radii = np.where(frontier, 0.068, 0.052)
        mesh = _implicit_surface(pts, radii, grid=72 if mode == "coral" else 70, level=0.56 if mode == "coral" else 0.52)
        mesh = _bump_surface(mesh, amplitude=0.013 if mode == "coral" else 0.010, frequency=20.0)
        surface = "connected smooth implicit tubes with deterministic surface bump"
    ctl.update({"mode": mode, "surface_strategy": surface, "porosity_proxy": "surface bump plus frontier neck preservation"})
    return mesh, ctl


def radial_orbit_mesh(order: int = 8, depth: int = 4) -> tuple[object, dict]:
    points: list[np.ndarray] = []
    radii: list[float] = []
    points.append(np.zeros(3))
    radii.append(0.105)
    for level in range(depth):
        radius = 0.28 + level * 0.245
        z = 0.035 * level
        tube = max(0.034 * (0.84**level), 0.014)
        phase = 0.18 * level
        ring_steps = max(order * 10, 64)
        ring = [
            np.array([math.cos(2.0 * math.pi * i / ring_steps + phase) * radius, math.sin(2.0 * math.pi * i / ring_steps + phase) * radius, z])
            for i in range(ring_steps)
        ]
        for p in ring:
            points.append(p)
            radii.append(tube)
        for k in range(order):
            a = 2.0 * math.pi * k / order + phase
            p0 = np.array([math.cos(a) * radius, math.sin(a) * radius, z])
            tooth = p0 + _unit(np.array([math.cos(a), math.sin(a), 0.08])) * (0.14 + 0.018 * (depth - level))
            seg_pts, seg_r = _segment_samples(p0, tooth, tube, tube * 0.48, tube * 0.75)
            points.extend(seg_pts)
            radii.extend(seg_r)
            if level > 0:
                prev_r = 0.28 + (level - 1) * 0.245
                prev = np.array([math.cos(a - 0.18) * prev_r, math.sin(a - 0.18) * prev_r, 0.035 * (level - 1)])
                seg_pts, seg_r = _segment_samples(prev, p0, tube * 0.72, tube, tube * 0.80)
                points.extend(seg_pts)
                radii.extend(seg_r)
    mesh = _implicit_surface(points, radii, grid=68, level=0.54, faceted=False)
    mesh = _bump_surface(mesh, amplitude=0.003, frequency=26.0)
    return mesh, {"order": order, "depth": depth, "support_strategy": "rings, radial teeth, and inter-depth bridge spines", "faceting": "deferred to PBR guide to avoid fragmenting ring bridges"}


def lattice_mesh(kind: str):
    if kind == "pyrite":
        coords = scaffold.largest_occupancy_component(scaffold.pyrite_crystal_lattice_cluster(quick=True))
    elif kind == "bismuth":
        coords = scaffold.largest_occupancy_component(scaffold.bismuth_hopper_cluster(quick=True))
    else:
        raise ValueError(kind)
    mesh = scaffold.coords_to_mesh(coords)
    try:
        pieces = mesh.split(only_watertight=False)
        if pieces:
            mesh = max(pieces, key=lambda p: len(p.vertices))
    except Exception:
        pass
    return mesh, {"source": f"connected_scaffold_cases_v2.{kind}", "faceted_lattice": True, "occupancy_voxels": int(len(coords))}


def _case_specs(seed: int) -> list[dict]:
    specs: list[dict] = []

    def add(case_id: str, family: str, target: str, recursive_mode: str, mesh, guide_key: str, case_seed: int, controls: dict, operators: list[str], notes: str) -> None:
        specs.append(
            {
                "case_id": case_id,
                "family": family,
                "match_target": target,
                "recursive_mode": recursive_mode,
                "mesh": mesh,
                "guide_key": guide_key,
                "seed": int(case_seed),
                "controls": controls,
                "operators": operators,
                "strict_match_notes": notes,
            }
        )

    nodes, parents = layered_pine_nodes(seed + 1)
    mesh, ctl = skeleton_case_mesh(nodes, parents, seed + 1, "pine", 0.058, 0.72, 0.010, grid=70)
    ctl.update({"depth": 5, "layout": "whorled conifer trunk and layered branch silhouette"})
    add("v4_lsys_pine_canopy_d5_continuous_conifer", "L-system", "lsys_pine_canopy_d5", "symbolic pine rewriting with continuous whorled trunk-branch occupancy", mesh, "conifer", seed + 101, ctl, ["symbolic_rewrite", "continuous_branch_occupancy", "attached_needle_support", "pbr_guide"], "Same L-system pine/canopy category, whorled silhouette, depth 5, with connected support instead of disconnected needles.")

    nodes, parents = bm.lsystem_case("root", depth=5, seed=seed + 2)
    mesh, ctl = skeleton_case_mesh(_normalize_nodes(nodes, 2.45), parents, seed + 2, "root", 0.066, 0.80, 0.006, grid=68)
    ctl.update({"depth": 5, "layout": "flat-to-downward root fan"})
    add("v4_lsys_root_fan_d5_continuous_hierarchy", "L-system", "lsys_root_fan_d5", "symbolic root rewriting with thick-to-thin fan hierarchy", mesh, "root", seed + 102, ctl, ["root_rewrite", "continuous_root_occupancy", "attached_root_hair_support", "pbr_guide"], "Same root fan task and depth as the traditional L-system target; high-quality root surface is allowed but layout stays fan-like.")

    nodes, parents = lsys_vine_nodes(seed + 3)
    mesh, ctl = skeleton_case_mesh(nodes, parents, seed + 3, "leaf", 0.050, 0.68, 0.007, grid=66)
    ctl.update({"iterations": 6, "curl_step_radians": 0.82})
    add("v4_lsys_climbing_vine_d6_connected_leaf_shell", "L-system", "lsys_climbing_vine_d6", "curling vine rewriting with connected tendril and leaf-shell support", mesh, "leaf", seed + 103, ctl, ["curl_rewrite", "continuous_tendril_occupancy", "leaf_shell_support", "pbr_guide"], "Same climbing vine category, curl pattern, and recursive tendril depth; leaf shell is attached by implicit bridges.")

    for offset, case, target, garnish, guide, label, mode in [
        (11, "tree_canopy", "sc_tree_crown_260", "leaf", "leaf", "tree_crown", "attractor competition crown with branch support and connected leaf shell"),
        (12, "root_vine", "sc_root_network_260", "root", "root", "root_network", "attractor competition root network with connected root hierarchy"),
        (13, "bush_shell", "sc_bush_shell_220", "leaf", "leaf", "bush_shell", "shell attractor competition with connected foliage boundary"),
    ]:
        nodes, parents, ctl0 = sc_nodes(case, seed + offset)
        mesh, ctl = skeleton_case_mesh(nodes, parents, seed + offset, garnish, 0.050 if garnish != "root" else 0.055, 0.82, 0.006, grid=66)
        ctl.update(ctl0)
        add(f"v4_sc_{label}_continuous_{garnish}", "Space colonization", target, mode, mesh, guide, seed + 100 + offset, ctl, ["attractor_competition", "continuous_branch_occupancy", f"attached_{garnish}_support", "pbr_guide"], f"Same SC task ({case}) with matched attractor/competition mode and connected local support.")

    for offset, mode, target, guide, label, particles, notes in [
        (21, "coral", "dla_coral_cluster_900", "coral", "coral_cluster", 620, "Same stochastic DLA/coral category; bridges follow nearest attachment necks and smooth implicit surface removes voxel beads."),
        (22, "frontier_sheet", "dla_frontier_sheet_700", "coral", "frontier_sheet", 560, "Same line-seeded frontier/sheet mode; smooth support keeps sheet-like silhouette instead of loose coral blob."),
        (23, "aniso_crystal", "dla_aniso_crystal_800", "pyrite", "aniso_crystal", 580, "Same anisotropic frontier attachment task; faceted connected surface is allowed for crystal visual quality."),
    ]:
        mesh, ctl = dla_case_mesh(seed + offset, mode, particles)
        add(f"v4_dla_{label}_connected_implicit", "DLA/frontier", target, f"{mode} attachment support with connected implicit tube surface", mesh, guide, seed + 100 + offset, ctl, ["frontier_attachment", "nearest_parent_bridge", "smooth_implicit_surface", "surface_bump_or_faceting", "pbr_guide"], notes)

    nodes, parents = ifs_tree_skeleton(depth=6)
    mesh, ctl = skeleton_case_mesh(_normalize_nodes(nodes, 2.38), parents, seed + 31, "pine", 0.052, 0.78, 0.008, grid=68)
    ctl.update({"depth": 6, "transform_set": "contractive affine branch orbit"})
    add("v4_ifs_branch_tree_d6_continuous_orbit", "IFS/transform", "ifs_branch_tree_d6", "contractive affine branch orbit with connected support spine", mesh, "conifer", seed + 131, ctl, ["transform_copy", "continuous_orbit_spine", "attached_tip_support", "pbr_guide"], "Same IFS branch-tree transform depth and hierarchy; visual root is improved but copy/orbit pattern remains visible.")

    mesh, ctl = radial_orbit_mesh(8, 4)
    add("v4_ifs_radial_ornament_o8_d4_bridged_gear", "IFS/transform", "ifs_radial_ornament_o8_d4", "8-fold radial transform-copy ornament with torus rings and bridge spines", mesh, "gear", seed + 132, ctl, ["radial_orbit", "torus_ring_cache", "bridge_spine", "faceted_projection", "pbr_guide"], "Same 8-fold radial/depth-4 transform task; rings and bridges explicitly prevent fragmented ornament components.")

    mesh, ctl = lattice_mesh("pyrite")
    ctl.update({"depth": 4})
    add("v4_ifs_fractal_lattice_d4_connected_pyrite", "IFS/transform", "ifs_fractal_lattice_d4", "recursive lattice transform-copy with connected pyrite faceted cache", mesh, "pyrite", seed + 133, ctl, ["lattice_orbit", "connected_transform_cache", "faceted_projection", "pbr_guide"], "Same depth-4 transform/lattice task; faceted crystal lattice stays connected and readable.")
    return specs


def _select_representative_specs(specs: list[dict], case_limit: int | None) -> list[dict]:
    if case_limit is None or case_limit >= len(specs):
        return specs
    if case_limit <= 0:
        return []
    families = ["L-system", "Space colonization", "DLA/frontier", "IFS/transform"]
    buckets = {family: [spec for spec in specs if spec["family"] == family] for family in families}
    selected: list[dict] = []
    seen: set[str] = set()
    while len(selected) < case_limit:
        made_progress = False
        for family in families:
            while buckets[family] and buckets[family][0]["case_id"] in seen:
                buckets[family].pop(0)
            if buckets[family] and len(selected) < case_limit:
                spec = buckets[family].pop(0)
                selected.append(spec)
                seen.add(spec["case_id"])
                made_progress = True
        if not made_progress:
            break
    return selected


def _metadata_for(spec: dict, mesh_path: Path, guide_path: str, metrics: dict) -> dict:
    return {
        "case_id": spec["case_id"],
        "family": spec["family"],
        "match_target": spec["match_target"],
        "recursive_mode": spec["recursive_mode"],
        "remote_target": REMOTE_TARGET,
        "mesh_path": str(mesh_path),
        "guide_image": guide_path,
        "seed": spec["seed"],
        "operators": spec["operators"],
        "controls": spec["controls"],
        "initial_mesh_metrics": metrics,
        "strict_match_notes": spec["strict_match_notes"],
        "root_selection_log": {
            "root_source_type": "proxy_generated_mesh",
            "root_source_provenance": "assets/strict_visual_matched_cases_v4_20260510.py local dry-run generator",
            "root_pool_size": 1,
            "root_generation_budget": "local CPU dry-run only; remote Trellis2 regeneration must be run on a100-2",
            "root_screening_budget": "no local manual cherry-pick; all emitted cases are representative V4 inputs",
            "selection_rank": 1,
            "projection_naturalization_schedule": spec["operators"],
            "readiness_label": "remote_input_dryrun",
        },
    }


def _write_readme(out_dir: Path, summary: dict) -> None:
    text = f"""# V4 Strict Visual-Matched Cases Dry Run

This directory was produced locally by `assets/strict_visual_matched_cases_v4_20260510.py`.

It is a dry-run input batch only.  It does not contain remote Trellis2 outputs and it did not launch a job.  The strict comparison regeneration target is `{REMOTE_TARGET}`.

Files:

- `manifest.csv` / `manifest.json`: case-level Trellis2 input manifest.
- `a100-2_cases.txt`: remote-ready lines in `case_id|mesh_path|guide_image|seed` format.
- `gpu2_cases.txt`: compatibility alias for scripts that consume GPU-group case lists.
- `initial_metrics.csv` / `initial_metrics.json`: pre-texture mesh metrics.
- each case folder: OBJ plus per-case metadata JSON.

Run locally:

```bash
python3 assets/strict_visual_matched_cases_v4_20260510.py
```

Case count: {summary["num_cases"]}
"""
    (out_dir / "README.md").write_text(text, encoding="utf-8")


def materialize(root: Path, out_dir: Path, seed: int = 20260510, case_limit: int | None = None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    guides = _write_guides(out_dir)
    specs = _case_specs(seed)
    specs = _select_representative_specs(specs, case_limit)
    rows: list[dict] = []
    metrics_rows: list[dict] = []
    for spec in specs:
        case_dir = out_dir / spec["case_id"]
        mesh_path = case_dir / f"{spec['case_id']}.obj"
        _export_mesh(mesh_path, spec["mesh"])
        metrics = _mesh_stats(mesh_path)
        guide_path = guides[spec["guide_key"]]
        metadata = _metadata_for(spec, mesh_path, guide_path, metrics)
        metadata_path = case_dir / f"{spec['case_id']}_metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        row = {
            "case_id": spec["case_id"],
            "family": spec["family"],
            "match_target": spec["match_target"],
            "recursive_mode": spec["recursive_mode"],
            "mesh_path": str(mesh_path),
            "guide_image": guide_path,
            "metadata_path": str(metadata_path),
            "remote_target": REMOTE_TARGET,
            "gpu_group": 2,
            "seed": spec["seed"],
            "operators": json.dumps(spec["operators"], ensure_ascii=False),
            "controls": json.dumps(spec["controls"], ensure_ascii=False, sort_keys=True),
            "strict_match_notes": spec["strict_match_notes"],
        }
        rows.append(row)
        metrics_rows.append({"case_id": spec["case_id"], "match_target": spec["match_target"], **metrics})

    manifest_fields = [
        "case_id",
        "family",
        "match_target",
        "recursive_mode",
        "mesh_path",
        "guide_image",
        "metadata_path",
        "remote_target",
        "gpu_group",
        "seed",
        "operators",
        "controls",
        "strict_match_notes",
    ]
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    metric_fields = [
        "case_id",
        "match_target",
        "vertices",
        "faces",
        "mesh_component_count",
        "largest_mesh_component_vertex_ratio",
        "bbox_extent",
        "bbox_diag",
        "surface_area",
    ]
    with (out_dir / "initial_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        writer.writerows(metrics_rows)
    (out_dir / "initial_metrics.json").write_text(json.dumps(metrics_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    case_lines = [f"{row['case_id']}|{row['mesh_path']}|{row['guide_image']}|{row['seed']}" for row in rows]
    (out_dir / "a100-2_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    (out_dir / "gpu2_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    summary = {
        "out_dir": str(out_dir),
        "num_cases": len(rows),
        "remote_target": REMOTE_TARGET,
        "manifest": str(out_dir / "manifest.csv"),
        "initial_metrics": str(out_dir / "initial_metrics.csv"),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_readme(out_dir, summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("RGG_ROOT", ROOT_DIR)))
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=20260510)
    parser.add_argument("--case-limit", type=int, default=None)
    args = parser.parse_args()
    materialize(args.root, args.out or DEFAULT_OUT, seed=args.seed, case_limit=args.case_limit)


if __name__ == "__main__":
    main()
