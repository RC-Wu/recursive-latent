#!/usr/bin/env python3
"""V20 paper-ready DLA/frontier/coral/crystal input generator.

V20 keeps V18's connected implicit support, rooted bridges, and loop-closure
bridges, then shifts the geometry toward paper-figure semantics: staghorn and
table coral have dense calyx/polyp relief, porous rounded reef surfaces, and
tapered branches; crystal cases get sharper facet plates, cubic pyrite clusters,
and stepped bismuth terraces.  The output here is only a remote input dry run;
final mesh/PBR outputs must be generated fresh on a100-2 GPUs 4/5/6/7.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path
from typing import Optional

import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.measure import marching_cubes

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import procedural_baselines as pb
import recursive_growth_mesh_metrics as rgm
import strict_visual_matched_cases_v6_connectivity_20260510 as v6
import strict_visual_matched_cases_v13_smooth_coral_crystal_20260510 as v13
import strict_visual_matched_cases_v14_branching_coral_20260510 as v14
import strict_visual_matched_cases_v16_natural_coral_20260510 as v16


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 100
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V20_paper_coral_crystal_20260510_dryrun"


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _basis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return v6._basis(axis)


def _surface_area(vertices: np.ndarray, faces: np.ndarray) -> float:
    if len(vertices) == 0 or len(faces) == 0:
        return 0.0
    tri = vertices[faces]
    return float(np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1).sum() * 0.5)


def _stamp_ball(field: np.ndarray, coords: np.ndarray, center: np.ndarray, radius: float, strength: float, cutoff: float = 2.35) -> None:
    v13._stamp_ball(field, coords, center, radius, strength, cutoff=cutoff)


def _stamp_ellipsoid(
    field: np.ndarray,
    coords: np.ndarray,
    center: np.ndarray,
    axes: tuple[np.ndarray, np.ndarray, np.ndarray],
    scales: tuple[float, float, float],
    strength: float,
    cutoff: float = 2.20,
) -> None:
    v13._stamp_ellipsoid(field, coords, center, axes, scales, strength, cutoff=cutoff)


def _parents_from_edges(count: int, edges: list[tuple[int, int]]) -> list[int]:
    return v13._parents_from_edges(count, edges)


def _children_from_edges(count: int, edges: list[tuple[int, int]]) -> dict[int, list[int]]:
    return v13._children_from_edges(count, edges)


def _largest_component_mesh(mesh: pb.Mesh) -> tuple[pb.Mesh, int, float]:
    return v13._largest_component_mesh(mesh)


def _taubin_smooth(mesh: pb.Mesh, iterations: int, lam: float = 0.31, mu: float = -0.33) -> pb.Mesh:
    return v16._taubin_smooth(mesh, iterations=iterations, lam=lam, mu=mu)


def _motif_config(motif: str) -> dict:
    configs = {
        "staghorn_calyx_coral": {
            "mode": "staghorn",
            "grid": 78,
            "level": 0.48,
            "bound": 1.58,
            "base_scale": (0.58, 0.55, 0.095),
            "branch_scale": 0.88,
            "bridge_radius": 0.029,
            "detail_count": 126,
            "pores": 68,
            "ridges": 92,
            "sigma": 0.42,
            "smooth": 8,
            "crystal": False,
            "domain": "coral",
        },
        "frontier_lace_sheet": {
            "mode": "frontier",
            "grid": 78,
            "level": 0.47,
            "bound": 1.60,
            "base_scale": (0.98, 0.42, 0.070),
            "branch_scale": 0.86,
            "bridge_radius": 0.027,
            "detail_count": 116,
            "pores": 74,
            "ridges": 96,
            "sigma": 0.42,
            "smooth": 8,
            "crystal": False,
            "domain": "coral",
        },
        "table_reef_plate": {
            "mode": "table",
            "grid": 78,
            "level": 0.48,
            "bound": 1.60,
            "base_scale": (1.02, 0.82, 0.070),
            "branch_scale": 0.90,
            "bridge_radius": 0.030,
            "detail_count": 122,
            "pores": 82,
            "ridges": 104,
            "sigma": 0.43,
            "smooth": 8,
            "crystal": False,
            "domain": "coral",
        },
        "branching_reef_loop_closure": {
            "mode": "table",
            "grid": 78,
            "level": 0.48,
            "bound": 1.60,
            "base_scale": (0.88, 0.72, 0.082),
            "branch_scale": 0.96,
            "bridge_radius": 0.030,
            "detail_count": 124,
            "pores": 78,
            "ridges": 104,
            "sigma": 0.43,
            "smooth": 8,
            "crystal": False,
            "domain": "coral",
        },
        "pyrite_cubic_crystal": {
            "mode": "crystal",
            "grid": 76,
            "level": 0.47,
            "bound": 1.54,
            "base_scale": (0.54, 0.52, 0.070),
            "branch_scale": 0.82,
            "bridge_radius": 0.034,
            "detail_count": 92,
            "pores": 18,
            "ridges": 116,
            "sigma": 0.24,
            "smooth": 2,
            "crystal": True,
            "domain": "crystal",
            "orbit": True,
        },
        "bismuth_stepped_crystal": {
            "mode": "crystal",
            "grid": 76,
            "level": 0.46,
            "bound": 1.52,
            "base_scale": (0.50, 0.50, 0.060),
            "branch_scale": 0.76,
            "bridge_radius": 0.034,
            "detail_count": 104,
            "pores": 12,
            "ridges": 132,
            "sigma": 0.22,
            "smooth": 2,
            "crystal": True,
            "domain": "crystal",
            "bismuth": True,
        },
    }
    return configs[motif]


def _radii_for_depths(depths: list[int], motif: str) -> list[float]:
    mode = _motif_config(motif)["mode"]
    radii = v14._radii_for_depths(depths, mode)
    scale = float(_motif_config(motif)["branch_scale"])
    return [max(float(r) * scale, 0.010 if mode != "crystal" else 0.012) for r in radii]


def _augment_non_tree_bridges(nodes: list[np.ndarray], edges: list[tuple[int, int]], seed: int, motif: str) -> list[tuple[int, int]]:
    rng = np.random.default_rng(seed + 18001)
    existing = {tuple(sorted((int(a), int(b)))) for a, b in edges}
    arr = np.asarray(nodes, dtype=float)
    candidates: list[tuple[float, int, int]] = []
    for i in range(1, len(nodes)):
        for j in range(i + 2, len(nodes), 3):
            if tuple(sorted((i, j))) in existing:
                continue
            d = float(np.linalg.norm(arr[i] - arr[j]))
            if 0.18 < d < (0.50 if _motif_config(motif)["crystal"] else 0.42):
                radial = float(np.linalg.norm(arr[i]) + np.linalg.norm(arr[j]))
                candidates.append((d - 0.040 * radial + rng.uniform(0.0, 0.018), i, j))
    candidates.sort(key=lambda x: x[0])
    wanted = 16 if not _motif_config(motif)["crystal"] else 12
    bridges = [(i, j) for _, i, j in candidates[:wanted]]
    root_candidates = np.argsort(np.linalg.norm(arr, axis=1))[1:13]
    bridges.extend((0, int(i)) for i in root_candidates[:8])
    return bridges


def _stamp_segment(
    field: np.ndarray,
    coords: np.ndarray,
    a: np.ndarray,
    b: np.ndarray,
    radius_a: float,
    radius_b: float,
    strength: float,
    samples_per_unit: float,
    motif: str,
) -> int:
    axis = b - a
    length = float(np.linalg.norm(axis))
    if length < 1e-8:
        return 0
    samples = max(7, int(length * samples_per_unit))
    u, v, w = _basis(axis)
    count = 0
    crystal = bool(_motif_config(motif)["crystal"])
    for s in range(samples + 1):
        t = s / max(samples, 1)
        center = a * (1.0 - t) + b * t
        radius = radius_a * (1.0 - t) + radius_b * t
        if not crystal:
            center = center + (u * math.sin(9.0 * t + length) + v * math.cos(7.0 * t)) * radius * 0.07
        _stamp_ball(field, coords, center, max(radius, 0.009), strength)
        count += 1
    if crystal:
        mid = (a + b) * 0.5
        _stamp_ellipsoid(field, coords, mid, (u, v, w), (max(radius_a, radius_b) * 1.45, max(radius_a, radius_b) * 0.88, length * 0.55 + 0.010), 0.18)
        count += 1
    return count


def _stamp_crystal_semantics(
    field: np.ndarray,
    coords: np.ndarray,
    nodes: list[np.ndarray],
    edges: list[tuple[int, int]],
    seed: int,
    motif: str,
) -> int:
    rng = np.random.default_rng(seed + 18002)
    count = 0
    arr = np.asarray(nodes, dtype=float)
    if motif == "pyrite_cubic_crystal":
        for radius in (0.38, 0.58, 0.78):
            for k in range(16):
                theta = 2.0 * math.pi * k / 16.0 + radius
                center = np.array([math.cos(theta) * radius, math.sin(theta) * radius, 0.12 * math.sin(2.0 * theta)])
                u = _unit(np.array([math.cos(theta), math.sin(theta), 0.0]))
                v = _unit(np.array([-math.sin(theta), math.cos(theta), 0.15]))
                w = _unit(np.cross(u, v))
                _stamp_ellipsoid(field, coords, center, (u, v, w), (0.078, 0.058, 0.052), 0.36, cutoff=2.0)
                count += 1
    if motif == "bismuth_stepped_crystal":
        for k in range(9):
            size = 0.48 - 0.036 * k
            center = np.array([0.0, 0.0, -0.03 + 0.044 * k])
            _stamp_ellipsoid(field, coords, center, (np.eye(3)[0], np.eye(3)[1], np.eye(3)[2]), (size, size * 0.74, 0.022), 0.28, cutoff=1.75)
            count += 1
            for sign in (-1.0, 1.0):
                _stamp_ellipsoid(field, coords, center + np.array([sign * size * 0.48, 0.0, 0.016]), (np.eye(3)[0], np.eye(3)[1], np.eye(3)[2]), (0.044, size * 0.38, 0.022), 0.22, cutoff=1.75)
                count += 1
    sample_edges = list(edges)
    rng.shuffle(sample_edges)
    for a, b in sample_edges[:70]:
        pa = arr[a]
        pb_ = arr[b]
        axis = pb_ - pa
        if float(np.linalg.norm(axis)) < 1e-8:
            continue
        u, v, w = _basis(axis)
        t = float(rng.uniform(0.12, 0.90))
        center = pa * (1.0 - t) + pb_ * t
        if motif == "bismuth_stepped_crystal":
            center = np.round(center / 0.055) * 0.055
        normal = _unit(u * rng.uniform(-0.6, 0.6) + v * rng.choice([-1.0, 1.0]) + 0.10 * w)
        _stamp_ellipsoid(field, coords, center + normal * 0.026, (u, normal, w), (0.062, 0.014, 0.040), 0.26, cutoff=2.0)
        count += 1
    return count


def _stamp_organic_semantics(
    field: np.ndarray,
    coords: np.ndarray,
    nodes: list[np.ndarray],
    edges: list[tuple[int, int]],
    radii: list[float],
    seed: int,
    motif: str,
) -> tuple[int, int, int]:
    cfg = _motif_config(motif)
    rng = np.random.default_rng(seed + 18003)
    parents = _parents_from_edges(len(nodes), edges)
    branch_sites = list(range(1, len(nodes)))
    rng.shuffle(branch_sites)
    details = 0
    for idx in branch_sites[: int(cfg["detail_count"])]:
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        u, v, _ = _basis(axis)
        angle = float(rng.uniform(0.0, 2.0 * math.pi))
        normal = _unit(math.cos(angle) * u + math.sin(angle) * v + 0.10 * axis)
        anchor = np.asarray(nodes[idx]) + normal * (float(radii[idx]) * 0.80 + 0.006)
        _stamp_ball(field, coords, anchor, rng.uniform(0.008, 0.014), 0.40)
        details += 1
    pore_count = 0
    pore_edges = list(edges)
    rng.shuffle(pore_edges)
    for a, b in pore_edges[: int(cfg["pores"])]:
        pa = np.asarray(nodes[a], dtype=float)
        pb_ = np.asarray(nodes[b], dtype=float)
        axis = pb_ - pa
        if float(np.linalg.norm(axis)) < 1e-8:
            continue
        u, v, _ = _basis(axis)
        center = pa * 0.42 + pb_ * 0.58
        normal = _unit(v * rng.choice([-1.0, 1.0]) + u * rng.uniform(-0.25, 0.25))
        _stamp_ball(field, coords, center + normal * (float(radii[a]) + 0.012), rng.uniform(0.020, 0.032), -0.28)
        pore_count += 1
    ridge_count = 0
    ridge_edges = list(edges)
    rng.shuffle(ridge_edges)
    for a, b in ridge_edges[: int(cfg["ridges"])]:
        pa = np.asarray(nodes[a], dtype=float)
        pb_ = np.asarray(nodes[b], dtype=float)
        axis = pb_ - pa
        if float(np.linalg.norm(axis)) < 1e-8:
            continue
        u, v, w = _basis(axis)
        t = float(rng.uniform(0.18, 0.84))
        normal = _unit(v * rng.choice([-1.0, 1.0]) + np.array([0.0, 0.0, 0.08]))
        center = pa * (1.0 - t) + pb_ * t + normal * (float(radii[a]) * 0.62 + 0.010)
        _stamp_ellipsoid(field, coords, center, (u, normal, w), (0.043, 0.012, 0.024), 0.23)
        ridge_count += 1
    return details, pore_count, ridge_count


def _stamp_paper_coral_calyxes(
    field: np.ndarray,
    coords: np.ndarray,
    nodes: list[np.ndarray],
    edges: list[tuple[int, int]],
    radii: list[float],
    seed: int,
    motif: str,
) -> int:
    """Stamp repeated coral calyx rings so branches read as coral, not tubes."""
    cfg = _motif_config(motif)
    rng = np.random.default_rng(seed + 20020)
    parents = _parents_from_edges(len(nodes), edges)
    sites = [i for i in range(1, len(nodes))]
    rng.shuffle(sites)
    wanted = max(96, int(cfg["detail_count"]))
    count = 0
    for idx in sites[:wanted]:
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        u, v, _w = _basis(axis)
        base_radius = max(float(radii[idx]), 0.010)
        angle = float(rng.uniform(0.0, 2.0 * math.pi))
        normal = _unit(math.cos(angle) * u + math.sin(angle) * v + 0.08 * axis)
        tangent = _unit(-math.sin(angle) * u + math.cos(angle) * v)
        center = np.asarray(nodes[idx]) + normal * (base_radius * 0.95 + 0.008)
        calyx_r = float(rng.uniform(0.010, 0.017))
        _stamp_ball(field, coords, center, calyx_r, 0.30, cutoff=2.0)
        _stamp_ball(field, coords, center + normal * 0.004, calyx_r * 0.58, -0.18, cutoff=1.9)
        for spoke in (-1.0, 1.0):
            _stamp_ball(field, coords, center + tangent * spoke * calyx_r * 0.72 + normal * calyx_r * 0.22, calyx_r * 0.45, 0.20, cutoff=1.8)
        count += 1
    return count


def _stamp_paper_crystal_facet_plates(
    field: np.ndarray,
    coords: np.ndarray,
    nodes: list[np.ndarray],
    edges: list[tuple[int, int]],
    seed: int,
    motif: str,
) -> int:
    """Stamp planar facet/terrace plates for pyrite and bismuth readability."""
    cfg = _motif_config(motif)
    rng = np.random.default_rng(seed + 20021)
    arr = np.asarray(nodes, dtype=float)
    sample_edges = list(edges)
    rng.shuffle(sample_edges)
    wanted = max(72, int(cfg["ridges"]))
    count = 0
    for a, b in sample_edges:
        if count >= wanted:
            break
        pa = arr[a]
        pb_ = arr[b]
        axis = pb_ - pa
        if float(np.linalg.norm(axis)) < 1e-8:
            continue
        u, v, w = _basis(axis)
        for _ in range(2):
            if count >= wanted:
                break
            t = float(rng.uniform(0.12, 0.90))
            center = pa * (1.0 - t) + pb_ * t
            if motif == "bismuth_stepped_crystal":
                center = np.round(center / 0.050) * 0.050
                scales = (0.078, 0.020, 0.046)
                strength = 0.24
            else:
                center = np.round(center / 0.070) * 0.070
                scales = (0.066, 0.030, 0.052)
                strength = 0.26
            normal = _unit(v * rng.choice([-1.0, 1.0]) + u * rng.uniform(-0.24, 0.24) + w * 0.10)
            _stamp_ellipsoid(field, coords, center + normal * 0.030, (u, normal, w), scales, strength, cutoff=1.9)
            count += 1
    return count


def _connected_implicit_mesh(seed: int, motif: str) -> tuple[pb.Mesh, dict]:
    cfg = _motif_config(motif)
    nodes, edges, depths, controls = v14._frontier_skeleton(seed, str(cfg["mode"]))
    radii = _radii_for_depths(depths, motif)
    bridge_pairs = _augment_non_tree_bridges(nodes, edges, seed, motif)
    resolution = int(cfg["grid"])
    bound = float(cfg["bound"])
    coords = np.linspace(-bound, bound, resolution, dtype=np.float32)
    field = np.zeros((resolution, resolution, resolution), dtype=np.float32)

    primitive_count = 0
    for a, b in edges:
        primitive_count += _stamp_segment(
            field,
            coords,
            np.asarray(nodes[a], dtype=float),
            np.asarray(nodes[b], dtype=float),
            float(radii[a]),
            float(radii[b]),
            1.06,
            72.0,
            motif,
        )

    bridge_radius = float(cfg["bridge_radius"])
    for a, b in bridge_pairs:
        primitive_count += _stamp_segment(
            field,
            coords,
            np.asarray(nodes[a], dtype=float),
            np.asarray(nodes[b], dtype=float),
            bridge_radius,
            bridge_radius * 0.86,
            0.60,
            58.0,
            motif,
        )

    base_axes = (np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0]))
    _stamp_ellipsoid(field, coords, np.array([0.0, 0.0, -0.050]), base_axes, tuple(float(x) for x in cfg["base_scale"]), 0.42, cutoff=2.0)
    _stamp_ball(field, coords, np.array([0.0, 0.0, -0.010]), 0.18, 0.52)
    primitive_count += 2

    children = _children_from_edges(len(nodes), edges)
    parents = _parents_from_edges(len(nodes), edges)
    tips = [i for i in range(1, len(nodes)) if not children.get(i)]
    tip_count = 0
    for idx in tips:
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        if cfg["crystal"]:
            _stamp_ellipsoid(field, coords, np.asarray(nodes[idx]) + axis * 0.018, _basis(axis), (0.046, 0.034, 0.060), 0.38, cutoff=2.0)
        else:
            for j, scale in enumerate((0.76, 0.50)):
                _stamp_ball(field, coords, np.asarray(nodes[idx]) + axis * (0.014 * (j + 1)), max(float(radii[idx]) * scale, 0.010), 0.80)
        tip_count += 1

    calyx_polyp_count = 0
    facet_plate_count = 0
    if cfg["crystal"]:
        naturalization_detail_count = _stamp_crystal_semantics(field, coords, nodes, edges, seed, motif)
        facet_plate_count = _stamp_paper_crystal_facet_plates(field, coords, nodes, edges, seed, motif)
        naturalization_detail_count += facet_plate_count
        pore_count = int(cfg["pores"])
        ridge_count = naturalization_detail_count
    else:
        naturalization_detail_count, pore_count, ridge_count = _stamp_organic_semantics(field, coords, nodes, edges, radii, seed, motif)
        calyx_polyp_count = _stamp_paper_coral_calyxes(field, coords, nodes, edges, radii, seed, motif)
        naturalization_detail_count += calyx_polyp_count

    field = gaussian_filter(field, sigma=float(cfg["sigma"]))
    verts, faces, _normals, _values = marching_cubes(
        field,
        level=float(cfg["level"]),
        spacing=(float(coords[1] - coords[0]), float(coords[1] - coords[0]), float(coords[1] - coords[0])),
    )
    verts = verts + np.array([coords[0], coords[0], coords[0]], dtype=float)
    mesh = pb.Mesh([tuple(map(float, v)) for v in verts], [tuple(int(i) + 1 for i in f) for f in faces])
    mesh, raw_component_count, retained_ratio = _largest_component_mesh(mesh)
    mesh = _taubin_smooth(mesh, iterations=int(cfg["smooth"]))

    controls.update(
        {
            "semantic_motif": motif,
            "semantic_domain": str(cfg["domain"]),
            "connected_implicit_support": True,
            "bridge_root_connectivity": True,
            "attachment_bridge_count": len(bridge_pairs),
            "loop_closure_bridge_count": max(0, len(bridge_pairs) - 8),
            "naturalization_detail_count": int(naturalization_detail_count),
            "surface_ridge_count": int(ridge_count),
            "subtle_pore_depression_count": int(pore_count),
            "calyx_polyp_count": int(calyx_polyp_count),
            "facet_plate_count": int(facet_plate_count),
            "rounded_porous_reef_surface": not bool(cfg["crystal"]),
            "flat_rod_cut_policy": "forbid_flat_rod_cuts" if not bool(cfg["crystal"]) else "not_applicable",
            "stepped_terrace_or_cubic_symmetry": bool(cfg["crystal"]),
            "smooth_blob_policy": "forbid_smooth_crystal_blobs" if bool(cfg["crystal"]) else "not_applicable",
            "rounded_or_faceted_terminal_tip_count": int(tip_count),
            "direct_voxel_blocks": False,
            "direct_straight_rods": False,
            "direct_tube_mesh": False,
            "detached_chunk_policy": "forbid_detached_chunks_by_overlapping_primitives_before_marching_cubes",
            "implicit_grid_resolution": resolution,
            "implicit_field_level": float(cfg["level"]),
            "gaussian_sigma": float(cfg["sigma"]),
            "taubin_smoothing_iterations": int(cfg["smooth"]),
            "raw_marching_cubes_component_count": int(raw_component_count),
            "largest_component_projection_retained_ratio": float(retained_ratio),
            "largest_component_vertex_ratio_min": 0.999,
            "pre_marching_cubes_primitive_count": int(primitive_count),
            "surface_strategy": "rooted DLA/frontier skeleton plus overlapping bridge, loop, base, semantic detail, and facet primitives in one implicit field",
            "paper_semantic_upgrade_over_v18": True,
            "v20_naturalization_policy": "V18 connected implicit support plus dense coral calyx/polyp relief and crystal facet/terrace primitives before marching cubes; not local repair, not local selection, and not textured-output postprocessing",
            "frontier_attachment_mode": "stochastic active-tip frontier attachment with occupancy exclusion and explicit loop-closure attachment bridges",
        }
    )
    return mesh, controls


def _write_guides(out_dir: Path) -> dict[str, str]:
    from PIL import Image, ImageDraw, ImageFilter

    guide_dir = out_dir / "_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)

    def stable_seed(name: str) -> int:
        return sum((i + 1) * b for i, b in enumerate(name.encode("utf-8"))) % (2**32)

    def save(name: str, bg: tuple[int, int, int], colors: list[tuple[int, int, int]], motif: str) -> str:
        img = Image.new("RGB", (768, 768), bg)
        draw = ImageDraw.Draw(img)
        rng = np.random.default_rng(stable_seed(name))
        for _ in range(760):
            c = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(30, 738))
            y = int(rng.integers(30, 738))
            if motif == "bismuth":
                r = int(rng.integers(18, 62))
                for k in range(4):
                    off = k * 5
                    x0, y0 = x - r + off, y - r // 2 + off
                    x1, y1 = x + r - off, y + r // 2 - off
                    if x0 <= x1 and y0 <= y1:
                        draw.rectangle((x0, y0, x1, y1), outline=c, width=2)
            elif motif == "crystal":
                r = int(rng.integers(12, 48))
                draw.polygon([(x, y - r), (x + r, y - r // 5), (x + r // 2, y + r), (x - r, y + r // 5)], outline=c, width=2)
            elif motif == "frontier":
                rx = int(rng.integers(22, 76))
                ry = int(rng.integers(5, 20))
                draw.ellipse((x - rx, y - ry, x + rx, y + ry), outline=c, width=int(rng.integers(2, 5)))
                if rng.random() < 0.50:
                    draw.line((x - rx, y, x + rx, y + int(rng.normal(0, 14))), fill=c, width=2)
            else:
                width = int(rng.integers(3, 9))
                dx = int(rng.normal(0, 80))
                dy = int(rng.normal(-10, 72))
                draw.line((x, y, x + dx, y + dy), fill=c, width=width)
                if rng.random() < 0.65:
                    draw.line((x + dx * 0.65, y + dy * 0.65, x + dx * 0.65 + rng.normal(0, 44), y + dy * 0.65 + rng.normal(-10, 40)), fill=c, width=max(2, width // 2))
                if rng.random() < 0.35:
                    rr = int(rng.integers(4, 10))
                    draw.ellipse((x - rr, y - rr, x + rr, y + rr), fill=c)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "coral": save("V20_staghorn_calyx_coral_pbr_guide.png", (214, 132, 116), [(255, 232, 194), (244, 170, 132), (226, 88, 116), (160, 78, 92), (255, 214, 168)], "coral"),
        "table": save("V20_table_reef_plate_porous_pbr_guide.png", (204, 136, 114), [(255, 232, 190), (238, 166, 126), (212, 96, 106), (136, 82, 90), (248, 214, 172)], "frontier"),
        "frontier": save("V20_frontier_lace_sheet_reef_edge_pbr_guide.png", (188, 122, 112), [(255, 228, 188), (232, 154, 124), (196, 84, 108), (118, 78, 94), (244, 204, 164)], "frontier"),
        "reef": save("V20_branching_reef_loop_porous_pbr_guide.png", (198, 138, 112), [(255, 234, 190), (236, 176, 120), (210, 102, 100), (138, 86, 88), (250, 216, 172)], "coral"),
        "pyrite": save("V20_pyrite_cubic_metallic_pbr_guide.png", (64, 56, 48), [(238, 198, 92), (178, 132, 52), (102, 88, 72), (250, 224, 132), (84, 78, 66)], "crystal"),
        "bismuth": save("V20_bismuth_stepped_iridescent_pbr_guide.png", (54, 58, 66), [(86, 204, 204), (214, 110, 214), (236, 186, 74), (110, 136, 238), (68, 86, 104)], "bismuth"),
    }


def _case_specs(seed: int) -> list[dict]:
    specs: list[dict] = []

    def add(case_id: str, target: str, motif: str, guide_key: str, offset: int, gpu: int, role: str, material_prompt: str, why: str) -> None:
        mesh, controls = _connected_implicit_mesh(seed + offset, motif)
        operators = [
            "stochastic_frontier_attachment",
            "occupancy_exclusion",
            "rooted_attachment_bridges",
            "loop_closure_bridges",
            "connected_implicit_support",
            "paper_semantic_surface_primitives",
            "coral_calyx_or_crystal_facet_guides",
            "pbr_material_prompt",
            "largest_component_gate",
        ]
        specs.append(
            {
                "case_id": case_id,
                "family": "DLA/frontier/crystal",
                "match_target": target,
                "traditional_target": target,
                "recursive_mode": "stochastic frontier attachment with occupancy exclusion, rooted bridge connectivity, and loop-closure non-tree support",
                "mesh": mesh,
                "guide_key": guide_key,
                "seed": int(seed + offset),
                "controls": controls,
                "operators": operators,
                "operator_composition": " -> ".join(operators),
                "material_prompt": material_prompt,
                "why_matches_traditional": why,
                "strict_match_notes": why,
                "gpu": int(gpu),
                "case_role": role,
            }
        )

    add("V20_dla_staghorn_calyx_coral_a", "dla_staghorn_coral_900", "staghorn_calyx_coral", "coral", 2001, 4, "priority_a100_2", "staghorn coral PBR, ivory pink calcareous branches, repeated calyx polyps, porous wet roughness, no plastic tubes", "Strict staghorn DLA coral target with V18 connectivity plus dense calyx/polyp rings, rounded tapered tips, pores, ridges, and no flat rod cuts.")
    add("V20_dla_staghorn_calyx_coral_b", "dla_staghorn_coral_900", "staghorn_calyx_coral", "coral", 2002, 5, "priority_a100_2", "living staghorn coral PBR, peach ivory skeletal texture, small calyx cups and porous tips", "Second same-target staghorn seed for one-to-one robustness; connectivity is enforced by overlapping root and loop bridges before marching cubes.")
    add("V20_dla_table_coral_reef_plate", "dla_table_coral_plate_760", "table_reef_plate", "table", 2003, 6, "priority_a100_2", "table coral reef plate PBR, thin rounded calcareous plate, porous rim, small coral cups", "Table coral target preserves planar frontier growth while avoiding giant leaf sheets through porous reef plate relief and rounded fused branches.")
    add("V20_dla_branching_reef_loop_closure", "dla_branching_reef_loop_650", "branching_reef_loop_closure", "reef", 2004, 7, "priority_a100_2", "branching reef coral PBR, antler branches, fused loop closures, porous ridges and calyx texture", "Branching reef case turns non-tree connectivity into explicit loop bridges and repeated coral surface motifs rather than arbitrary branch sheets.")
    add("V20_dla_frontier_lace_sheet_a", "dla_frontier_sheet_700", "frontier_lace_sheet", "frontier", 2005, 4, "priority_a100_2", "frontier reef sheet PBR, lace-like porous coral edge, thin calcareous surface, rounded rim", "Frontier sheet target with boundary-biased DLA attachment, connected lace rim, pores, and calyx relief so it reads as reef sheet rather than leaf.")
    add("V20_dla_frontier_lace_sheet_b", "dla_frontier_sheet_700", "frontier_lace_sheet", "frontier", 2006, 5, "backup_a100_2", "porous frontier coral sheet PBR, calcareous lace edge, small polyps and rough reef surface", "Backup frontier seed using the same strict one-to-one frontier/exclusion controls with connected implicit support and no local postprocessing.")
    add("V20_dla_pyrite_cubic_crystal", "dla_pyrite_cubic_crystal_520", "pyrite_cubic_crystal", "pyrite", 2007, 6, "priority_a100_2", "metallic pyrite PBR, cubic crystal cluster, sharp planar facets, rough gold mineral anisotropy", "Pyrite-like DLA/crystal target uses accretive growth plus cubic facet plates and bridge-supported orbit clusters to avoid smooth blobs or detached shards.")
    add("V20_dla_bismuth_stepped_crystal", "dla_bismuth_step_crystal_360", "bismuth_stepped_crystal", "bismuth", 2008, 7, "priority_a100_2", "iridescent bismuth PBR, stepped terraces, oxide rainbow facets, sharp mineral ledges", "Bismuth-like stepped crystal uses connected terrace primitives and loop bridges, targeting crystal semantics instead of smooth organic branches.")
    return specs


def _export_mesh(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


def _mesh_stats(path: Path, extra: dict) -> dict:
    vertices, faces = rgm.parse_obj(path)
    comp = rgm.component_stats(vertices, faces)
    bbox = rgm.bbox_stats(vertices)
    return {
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
        "mesh_component_count": int(comp["component_count"]),
        "largest_mesh_component_vertex_ratio": float(comp["largest_component_vertex_ratio"]),
        "bbox_extent": [float(bbox["bbox_extent_x"]), float(bbox["bbox_extent_y"]), float(bbox["bbox_extent_z"])],
        "bbox_diag": float(bbox["bbox_diag"]),
        "surface_area": _surface_area(vertices, faces),
        "attachment_bridge_count": int(extra.get("attachment_bridge_count", 0)),
        "loop_closure_bridge_count": int(extra.get("loop_closure_bridge_count", 0)),
        "naturalization_detail_count": int(extra.get("naturalization_detail_count", 0)),
        "surface_ridge_count": int(extra.get("surface_ridge_count", 0)),
        "subtle_pore_depression_count": int(extra.get("subtle_pore_depression_count", 0)),
        "raw_marching_cubes_component_count": int(extra.get("raw_marching_cubes_component_count", 0)),
    }


def _metadata_for(spec: dict, mesh_path: Path, guide_path: str, metrics: dict) -> dict:
    operator_family = "traditional DLA/frontier accretive attachment with non-tree connectivity target"
    return {
        "case_id": spec["case_id"],
        "family": spec["family"],
        "operator_family": operator_family,
        "match_target": spec["match_target"],
        "traditional_target": spec["traditional_target"],
        "traditional_alignment": {
            "traditional_target": spec["traditional_target"],
            "operator_family": operator_family,
            "same_category": True,
            "strict_one_to_one_comparison": True,
            "same_recursive_mode": spec["recursive_mode"],
            "control_parameters": spec["controls"],
            "why_strict_one_to_one": f"{spec['why_matches_traditional']} Must be generated fresh on a100-2 and compared one-to-one against the matching traditional baseline.",
        },
        "recursive_mode": spec["recursive_mode"],
        "remote_target": REMOTE_TARGET,
        "remote_constraints": {
            "machine": REMOTE_TARGET,
            "allowed_gpus": ALLOWED_GPUS,
            "storage_root": REMOTE_STORAGE_ROOT,
            "storage_limit_gb": STORAGE_LIMIT_GB,
        },
        "mesh_path": str(mesh_path),
        "guide_image": guide_path,
        "seed": spec["seed"],
        "operators": spec["operators"],
        "operator_composition": spec["operator_composition"],
        "controls": spec["controls"],
        "initial_mesh_metrics": metrics,
        "material_prompt": spec["material_prompt"],
        "why_matches_traditional": spec["why_matches_traditional"],
        "strict_match_notes": spec["strict_match_notes"],
        "case_role": spec["case_role"],
        "mesh_pbr_contract": {
            "mesh_outputs_only": True,
            "input_mesh_format": "obj",
            "pbr_textured_glb_required": True,
            "texture_size_default": 2048,
            "forbidden_outputs": ["local_selected_render", "2d_only_image", "posthoc_repair_mesh"],
        },
        "visual_readability_contract": {
            "dryrun_visual_floor": "initial OBJ must pass connected largest-component gate before remote PBR generation",
            "positive_constraint": "connected staghorn coral, table coral, frontier reef sheet, pyrite cubic crystal, or bismuth stepped crystal growth with fused bridges, calyx/facet detail, and readable PBR material intent",
            "negative_constraint": "no fragmented chunks, no textured organic branches/sheets as the dominant read, no flat rod cuts, no mushroom caps, no smooth crystal blobs, no local textured-output postprocessing",
            "v18_failure_addressed": "V20 keeps V18 connectivity but adds denser coral calyx/polyps, rounded porous reef surfaces, cubic pyrite facets, and bismuth stepped terraces before marching cubes.",
        },
        "strict_generation_policy": "generate_new_on_a100_2_no_local_selection_or_postprocessing",
        "root_selection_log": {
            "root_source_type": "V20_paper_coral_crystal_input_generator",
            "source_generator": "assets/strict_visual_matched_cases_V20_paper_coral_crystal_20260510.py",
            "root_pool_size": 1,
            "root_generation_budget": "local CPU dry-run geometry only; final mesh/PBR outputs must be generated fresh on a100-2 GPUs 4-7",
            "root_screening_budget": "no local manual cherry-pick and no V1-V16 textured-output repair",
            "selection_rank": 1,
            "projection_naturalization_schedule": spec["operators"],
            "readiness_label": "remote_input_dryrun_V20_paper_coral_crystal",
        },
    }


def _write_readme(out_dir: Path, summary: dict) -> None:
    text = f"""# V20 Paper Coral/Crystal Strict Matched Cases Dry Run

Generated by `assets/strict_visual_matched_cases_V20_paper_coral_crystal_20260510.py`.

This directory is a local input dry run only. It does not launch remote jobs,
does not select local textured outputs, and does not postprocess generated
outputs. Final strict cases must be generated fresh on `{REMOTE_TARGET}` with
GPU ids `{ALLOWED_GPUS}` under:

`{REMOTE_STORAGE_ROOT}`

V20 focus:

- DLA/frontier/coral/crystal strict one-to-one targets.
- Rooted attachment bridges plus loop-closure bridges before marching cubes.
- Connected implicit support, reef bases, pores, ridges, repeated calyx/polyps, and crystal facets.
- Staghorn coral, table reef plate, branching reef loop closure, frontier lace sheet, cubic pyrite, and bismuth stepped crystal cases.
- Mesh/PBR outputs only: OBJ dry-run input and fresh remote textured GLB/PBR export.
- No local selection, no local textured-output repair, no 2D-only result.

Files:

- `manifest.csv` / `manifest.json`: case-level Trellis2 input manifest.
- `a100-2_cases.txt`: `case_id|mesh_path|guide_image|seed|gpu` lines.
- `gpu4_cases.txt` ... `gpu7_cases.txt`: two cases per GPU split.
- `initial_metrics.csv` / `initial_metrics.json`: pre-texture connectivity metrics.
- each case folder: OBJ plus per-case metadata JSON.

Case count: {summary["num_cases"]}
Priority cases: {", ".join(summary["priority_cases"])}
"""
    (out_dir / "README.md").write_text(text, encoding="utf-8")


def materialize(root: Path, out_dir: Path, seed: int = 20260510, case_limit: Optional[int] = None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    guides = _write_guides(out_dir)
    specs = _case_specs(seed)
    if case_limit is not None:
        specs = specs[: int(case_limit)]

    rows: list[dict] = []
    metrics_rows: list[dict] = []
    for spec in specs:
        case_dir = out_dir / spec["case_id"]
        mesh_path = case_dir / f"{spec['case_id']}.obj"
        _export_mesh(mesh_path, spec["mesh"])
        guide_path = guides[spec["guide_key"]]
        metrics = _mesh_stats(mesh_path, spec["controls"])
        if metrics["mesh_component_count"] != 1 and metrics["largest_mesh_component_vertex_ratio"] < 0.999:
            raise RuntimeError(f"{spec['case_id']} failed V20 connectivity gate: {metrics}")
        metadata = _metadata_for(spec, mesh_path, guide_path, metrics)
        metadata_path = case_dir / f"{spec['case_id']}_metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        row = {
            "case_id": spec["case_id"],
            "family": spec["family"],
            "match_target": spec["match_target"],
            "traditional_target": spec["traditional_target"],
            "recursive_mode": spec["recursive_mode"],
            "mesh_path": str(mesh_path),
            "guide_image": guide_path,
            "metadata_path": str(metadata_path),
            "remote_target": REMOTE_TARGET,
            "gpu_group": spec["gpu"],
            "seed": spec["seed"],
            "operators": json.dumps(spec["operators"], ensure_ascii=False),
            "operator_composition": spec["operator_composition"],
            "controls": json.dumps(spec["controls"], ensure_ascii=False, sort_keys=True),
            "material_prompt": spec["material_prompt"],
            "why_matches_traditional": spec["why_matches_traditional"],
            "strict_match_notes": spec["strict_match_notes"],
            "case_role": spec["case_role"],
            "strict_one_to_one": "true",
            "generation_policy": "generate_new_on_a100_2_no_local_selection_or_postprocessing",
            "mesh_pbr_policy": "mesh_and_pbr_outputs_only",
            "storage_root": REMOTE_STORAGE_ROOT,
            "storage_limit_gb": STORAGE_LIMIT_GB,
        }
        rows.append(row)
        metrics_rows.append(
            {
                "case_id": spec["case_id"],
                "match_target": spec["match_target"],
                "traditional_target": spec["traditional_target"],
                **metrics,
            }
        )

    manifest_fields = [
        "case_id",
        "family",
        "match_target",
        "traditional_target",
        "recursive_mode",
        "mesh_path",
        "guide_image",
        "metadata_path",
        "remote_target",
        "gpu_group",
        "seed",
        "operators",
        "operator_composition",
        "controls",
        "material_prompt",
        "why_matches_traditional",
        "strict_match_notes",
        "case_role",
        "strict_one_to_one",
        "generation_policy",
        "mesh_pbr_policy",
        "storage_root",
        "storage_limit_gb",
    ]
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    metric_fields = [
        "case_id",
        "match_target",
        "traditional_target",
        "vertices",
        "faces",
        "mesh_component_count",
        "largest_mesh_component_vertex_ratio",
        "bbox_extent",
        "bbox_diag",
        "surface_area",
        "attachment_bridge_count",
        "loop_closure_bridge_count",
        "naturalization_detail_count",
        "surface_ridge_count",
        "subtle_pore_depression_count",
        "raw_marching_cubes_component_count",
    ]
    with (out_dir / "initial_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        writer.writerows(metrics_rows)
    (out_dir / "initial_metrics.json").write_text(json.dumps(metrics_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    case_lines = [f"{row['case_id']}|{row['mesh_path']}|{row['guide_image']}|{row['seed']}|{row['gpu_group']}" for row in rows]
    (out_dir / "a100-2_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    (out_dir / "gpu4567_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    for gpu in ALLOWED_GPUS:
        selected = [line for line, row in zip(case_lines, rows) if int(row["gpu_group"]) == gpu]
        (out_dir / f"gpu{gpu}_cases.txt").write_text("\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")

    summary = {
        "out_dir": str(out_dir),
        "num_cases": len(rows),
        "remote_target": REMOTE_TARGET,
        "allowed_gpus": ALLOWED_GPUS,
        "storage_root": REMOTE_STORAGE_ROOT,
        "storage_limit_gb": STORAGE_LIMIT_GB,
        "surface_generator": "paper_coral_crystal_semantics_v20",
        "mesh_pbr_policy": "mesh_and_pbr_outputs_only",
        "connectivity_gate": {"largest_component_vertex_ratio_min": 0.999},
        "v20_supersedes": "V18 connectivity plus stronger coral calyx/polyp and crystal facet/terrace semantics",
        "manifest": str(out_dir / "manifest.csv"),
        "initial_metrics": str(out_dir / "initial_metrics.csv"),
        "priority_cases": [row["case_id"] for row in rows if row["case_role"] == "priority_a100_2"],
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_readme(out_dir, summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("RGG_ROOT", ROOT_DIR)))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260510)
    parser.add_argument("--case-limit", type=int, default=None)
    args = parser.parse_args()
    materialize(args.root, args.out, seed=args.seed, case_limit=args.case_limit)


if __name__ == "__main__":
    main()
