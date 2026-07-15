#!/usr/bin/env python3
"""V14 fine branching implicit coral strict matched DLA input generator.

V13 fixed the cylinder-rod and clipped-terminal failures, but manual review
still found some staghorn/table/frontier cases reading as claw-like shell,
animal-shell, or crystal-sheet chunks. V14 keeps the strict DLA/frontier
contract from V13 - stochastic active frontier attachment, occupancy exclusion,
and one connected implicit projection - while shifting mass from large lobes and
plates into finer antler-like branch hierarchy, smaller pores, and ridged
surface microrelief.
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


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 100
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_v14_branching_coral_20260510_dryrun"


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


def _children_from_edges(count: int, edges: list[tuple[int, int]]) -> dict[int, list[int]]:
    return v13._children_from_edges(count, edges)


def _parents_from_edges(count: int, edges: list[tuple[int, int]]) -> list[int]:
    return v13._parents_from_edges(count, edges)


def _largest_component_mesh(mesh: pb.Mesh) -> tuple[pb.Mesh, int, float]:
    return v13._largest_component_mesh(mesh)


def _mode_config(mode: str) -> dict:
    configs = {
        "staghorn": {
            "target_nodes": 224,
            "max_depth": 9,
            "step": 0.166,
            "branch_prob": 0.86,
            "exclusion": 0.044,
            "anisotropy": np.array([0.92, 0.92, 1.30]),
            "noise": 0.175,
            "up_bias": 0.102,
            "base_radius": 0.064,
            "tip_radius": 0.0105,
            "grid": 76,
            "extent": 2.46,
        },
        "table": {
            "target_nodes": 214,
            "max_depth": 9,
            "step": 0.171,
            "branch_prob": 0.80,
            "exclusion": 0.046,
            "anisotropy": np.array([1.34, 1.24, 0.34]),
            "noise": 0.150,
            "up_bias": 0.018,
            "base_radius": 0.060,
            "tip_radius": 0.0100,
            "grid": 76,
            "extent": 2.50,
        },
        "frontier": {
            "target_nodes": 204,
            "max_depth": 9,
            "step": 0.176,
            "branch_prob": 0.75,
            "exclusion": 0.046,
            "anisotropy": np.array([1.70, 0.98, 0.28]),
            "noise": 0.132,
            "up_bias": 0.008,
            "base_radius": 0.054,
            "tip_radius": 0.0095,
            "grid": 76,
            "extent": 2.52,
        },
        "crystal": {
            "target_nodes": 210,
            "max_depth": 9,
            "step": 0.185,
            "branch_prob": 0.74,
            "exclusion": 0.050,
            "anisotropy": np.array([1.12, 1.02, 0.54]),
            "noise": 0.058,
            "up_bias": 0.000,
            "base_radius": 0.052,
            "tip_radius": 0.0100,
            "grid": 74,
            "extent": 2.40,
        },
    }
    return configs[mode]


def _initial_dirs(mode: str) -> list[np.ndarray]:
    if mode == "table":
        return [_unit(np.array([math.cos(a), math.sin(a), 0.06])) for a in np.linspace(0, 2 * math.pi, 10, endpoint=False)]
    if mode == "frontier":
        xs = np.linspace(-1.0, 1.0, 10)
        return [_unit(np.array([x, 0.30 * math.sin(i * 1.9), 0.045])) for i, x in enumerate(xs)]
    if mode == "crystal":
        return [_unit(np.array([math.cos(a), math.sin(a), 0.16])) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
    return [_unit(np.array([math.cos(a), math.sin(a), 0.64])) for a in np.linspace(0, 2 * math.pi, 9, endpoint=False)]


def _frontier_skeleton(seed: int, mode: str) -> tuple[list[np.ndarray], list[tuple[int, int]], list[int], dict]:
    cfg = _mode_config(mode)
    rng = np.random.default_rng(seed)
    nodes: list[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    edges: list[tuple[int, int]] = []
    depths: list[int] = [0]
    tips: list[tuple[int, np.ndarray, int]] = []
    for direction in _initial_dirs(mode):
        tips.append((0, _unit(direction * cfg["anisotropy"]), 1))

    attempts = 0
    while attempts < 3200 and len(nodes) < int(cfg["target_nodes"]):
        if not tips:
            expandable = [i for i, d in enumerate(depths) if d < int(cfg["max_depth"])]
            if not expandable:
                break
            parent_idx = int(rng.choice(expandable))
            parent_parent = next((a for a, b in edges if b == parent_idx), 0)
            base_dir = _unit(nodes[parent_idx] - nodes[parent_parent])
            if float(np.linalg.norm(base_dir)) < 1e-7:
                base_dir = _unit(rng.normal(0.0, 1.0, 3))
            tips.append((parent_idx, _unit(base_dir + rng.normal(0.0, 0.46, 3)), depths[parent_idx] + 1))
        parent, direction, depth = tips.pop(0)
        attempts += 1
        if depth > int(cfg["max_depth"]):
            continue
        step = float(cfg["step"]) * (0.88 ** (depth - 1)) * rng.uniform(0.82, 1.15)
        bend = rng.normal(0.0, float(cfg["noise"]), 3)
        bend[2] += float(cfg["up_bias"])
        if mode in {"table", "frontier"}:
            bend[2] *= 0.18
        new_dir = _unit((direction + bend) * cfg["anisotropy"])
        p = nodes[parent] + new_dir * step
        exclusion = float(cfg["exclusion"]) * (0.92 ** max(depth - 1, 0))
        if any(float(np.linalg.norm(p - q)) < exclusion for q in nodes):
            continue
        idx = len(nodes)
        nodes.append(p)
        depths.append(depth)
        edges.append((parent, idx))

        if depth < int(cfg["max_depth"]):
            fan = 2 if rng.random() < float(cfg["branch_prob"]) else 1
            if mode == "staghorn" and depth >= 5 and rng.random() < 0.34:
                fan = 3
            if mode in {"table", "frontier"} and depth >= 4 and rng.random() < 0.24:
                fan = 3
            if mode == "crystal" and rng.random() < 0.42:
                fan = 1
            for _ in range(fan):
                rot = rng.normal(0.0, 0.38 if mode != "crystal" else 0.15, 3)
                if mode in {"frontier", "table"}:
                    rot[2] *= 0.16
                if mode == "crystal":
                    rot = np.round(rot * 5.0) / 5.0
                tips.append((idx, _unit(new_dir + rot), depth + 1))

    child_count = {i: 0 for i in range(len(nodes))}
    for a, b in edges:
        child_count[a] = child_count.get(a, 0) + 1
        child_count.setdefault(b, 0)
    terminal_ids = [i for i in range(1, len(nodes)) if child_count.get(i, 0) == 0]
    for i in terminal_ids:
        parent = next((a for a, b in edges if b == i), 0)
        direction = _unit(nodes[i] - nodes[parent])
        extension = 0.070 if mode != "crystal" else 0.058
        nodes.append(nodes[i] + direction * extension)
        depths.append(depths[i] + 1)
        edges.append((i, len(nodes) - 1))

    nodes = v6._normalize_nodes(nodes, float(cfg["extent"]))
    controls = {
        "mode": mode,
        "generated_nodes": len(nodes),
        "skeleton_edges": len(edges),
        "max_depth": int(cfg["max_depth"]),
        "attempts": attempts,
        "occupancy_exclusion_radius": float(cfg["exclusion"]),
        "frontier_attachment_mode": "stochastic active-tip frontier attachment with occupancy exclusion",
        "occupancy_exclusion": "reject candidate frontier nodes inside depth-scaled radius before connected projection",
    }
    return nodes, edges, depths, controls


def _radii_for_depths(depths: list[int], mode: str) -> list[float]:
    cfg = _mode_config(mode)
    max_d = max(depths) if depths else 1
    base = float(cfg["base_radius"])
    tip = float(cfg["tip_radius"])
    power = 1.34 if mode != "crystal" else 1.04
    return [tip + (base - tip) * ((1.0 - d / max(max_d, 1)) ** power) for d in depths]


def _stamp_ball(
    field: np.ndarray,
    coords: np.ndarray,
    center: np.ndarray,
    radius: float,
    strength: float,
    cutoff: float = 2.30,
) -> None:
    v13._stamp_ball(field, coords, center, radius, strength, cutoff=cutoff)


def _stamp_ellipsoid(
    field: np.ndarray,
    coords: np.ndarray,
    center: np.ndarray,
    axes: tuple[np.ndarray, np.ndarray, np.ndarray],
    scales: tuple[float, float, float],
    strength: float,
    cutoff: float = 2.15,
) -> None:
    v13._stamp_ellipsoid(field, coords, center, axes, scales, strength, cutoff=cutoff)


def _implicit_frontier_mesh(seed: int, mode: str) -> tuple[pb.Mesh, dict]:
    nodes, edges, depths, controls = _frontier_skeleton(seed, mode)
    radii = _radii_for_depths(depths, mode)
    cfg = _mode_config(mode)
    rng = np.random.default_rng(seed + 14014)
    resolution = int(cfg["grid"])
    bound = 1.58
    coords = np.linspace(-bound, bound, resolution, dtype=np.float32)
    field = np.zeros((resolution, resolution, resolution), dtype=np.float32)
    children = _children_from_edges(len(nodes), edges)
    parents = _parents_from_edges(len(nodes), edges)
    tips = [i for i in range(1, len(nodes)) if not children.get(i)]

    metaball_samples = 0
    for edge_idx, (a, b) in enumerate(edges):
        pa = np.asarray(nodes[a], dtype=float)
        pb_ = np.asarray(nodes[b], dtype=float)
        axis = pb_ - pa
        length = float(np.linalg.norm(axis))
        if length < 1e-7:
            continue
        u, v, _ = _basis(axis)
        samples = max(6, int(length / 0.025))
        phase = edge_idx * 0.83 + rng.uniform(-0.45, 0.45)
        for s in range(samples + 1):
            t = s / max(samples, 1)
            center = pa * (1.0 - t) + pb_ * t
            wrinkle = 1.0 + 0.095 * math.sin(6.0 * t + phase) + 0.060 * math.sin(17.0 * t + phase * 0.41)
            if mode == "crystal":
                wrinkle = 0.95 + 0.055 * math.sin(4.5 * t + phase)
            radius = (float(radii[a]) * (1.0 - t) + float(radii[b]) * t) * wrinkle
            offset = (u * math.sin(2.0 * math.pi * t + phase) + v * math.cos(math.pi * t + phase)) * radius * 0.14
            _stamp_ball(field, coords, center + offset, radius, 1.14)
            metaball_samples += 1

    rounded_lobes = 0
    large_lobe_scale_max = 0.74
    for idx in tips:
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        for j, scale in enumerate((0.74, 0.52)):
            center = np.asarray(nodes[idx]) + axis * (0.022 * (j + 1))
            _stamp_ball(field, coords, center, max(float(radii[idx]) * scale, 0.010), 0.98)
            metaball_samples += 1
        rounded_lobes += 1

    ridge_lines = 0
    ridge_step = max(len(edges) // 62, 1)
    for k, (a, b) in enumerate(edges[::ridge_step]):
        if ridge_lines >= 76:
            break
        pa = np.asarray(nodes[a], dtype=float)
        pb_ = np.asarray(nodes[b], dtype=float)
        axis = pb_ - pa
        if float(np.linalg.norm(axis)) < 1e-7:
            continue
        u, v, w = _basis(axis)
        side = -1.0 if k % 2 else 1.0
        normal = _unit(v * side + np.array([0.0, 0.0, 0.12 if mode != "crystal" else 0.03]))
        for t in np.linspace(0.18, 0.82, 6):
            center = pa * (1.0 - t) + pb_ * t + normal * (0.014 + float(radii[a]) * 0.30)
            if mode == "crystal":
                _stamp_ellipsoid(field, coords, center, (u, normal, w), (0.048, 0.013, 0.030), 0.28)
            else:
                _stamp_ball(field, coords, center, 0.019, 0.31)
            metaball_samples += 1
        ridge_lines += 1

    micro_branches = 0
    antler_tips = 0
    branch_sites = list(tips)
    if len(branch_sites) < 72:
        high_depth = max(depths) if depths else 0
        branch_sites.extend(i for i in range(1, len(nodes)) if depths[i] >= high_depth - 2 and i not in branch_sites)
    rng.shuffle(branch_sites)
    micro_limit = 72 if mode != "crystal" else 64
    for idx in branch_sites[:micro_limit]:
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        u, v, _ = _basis(axis)
        anchor = np.asarray(nodes[idx])
        _stamp_ball(field, coords, anchor, max(float(radii[idx]) * 1.08, 0.012), 0.96)
        metaball_samples += 1
        prongs = 2 if (mode != "crystal" and rng.random() < 0.62) or (mode == "crystal" and rng.random() < 0.36) else 1
        for prong in range(prongs):
            spread = -1.0 if prong == 0 else 1.0
            direction = _unit(axis * 0.70 + u * rng.normal(0.22 * spread, 0.26) + v * rng.normal(0.0, 0.30))
            length = rng.uniform(0.056, 0.130 if mode != "crystal" else 0.092)
            for s in range(5):
                t = s / 4.0
                radius = max(float(radii[idx]) * (0.76 - 0.49 * t), 0.0085 if mode != "crystal" else 0.0100)
                _stamp_ball(field, coords, anchor + direction * length * t, radius, 0.88)
                metaball_samples += 1
            antler_tips += 1
        micro_branches += 1

    pores = 0
    pore_step = max(len(edges) // 52, 1)
    for k, (a, b) in enumerate(edges[::pore_step]):
        if pores >= 64:
            break
        pa = np.asarray(nodes[a], dtype=float)
        pb_ = np.asarray(nodes[b], dtype=float)
        axis = pb_ - pa
        if float(np.linalg.norm(axis)) < 1e-7:
            continue
        u, v, _ = _basis(axis)
        t = float(rng.uniform(0.20, 0.80))
        side = -1.0 if k % 2 else 1.0
        normal = _unit(v * side + u * rng.uniform(-0.30, 0.30))
        center = pa * (1.0 - t) + pb_ * t + normal * (float(radii[a]) * 0.82 + 0.010)
        pore_radius = 0.028 if mode != "crystal" else 0.025
        _stamp_ball(field, coords, center, pore_radius, -0.43 if mode != "crystal" else -0.34)
        pores += 1

    field = gaussian_filter(field, sigma=0.48 if mode != "crystal" else 0.38)
    level = 0.50 if mode != "crystal" else 0.48
    verts, faces, _normals, _values = marching_cubes(
        field,
        level=level,
        spacing=(float(coords[1] - coords[0]), float(coords[1] - coords[0]), float(coords[1] - coords[0])),
    )
    verts = verts + np.array([coords[0], coords[0], coords[0]], dtype=float)
    mesh = pb.Mesh([tuple(map(float, v)) for v in verts], [tuple(int(i) + 1 for i in f) for f in faces])
    mesh, raw_component_count, retained_ratio = _largest_component_mesh(mesh)
    controls.update(
        {
            "direct_tube_mesh": False,
            "implicit_grid_resolution": resolution,
            "implicit_field_level": level,
            "metaball_sample_count": metaball_samples,
            "rounded_terminal_lobe_count": rounded_lobes,
            "large_lobe_scale_max": large_lobe_scale_max,
            "ridge_line_count": ridge_lines,
            "subtractive_pore_count": pores,
            "micro_branch_count": micro_branches,
            "antler_tip_count": antler_tips,
            "curved_branch_edges": len(edges),
            "perforated_membrane_count": pores,
            "ridge_fin_count": ridge_lines,
            "thin_tip_radius_max": min(radii) if radii else 0.0,
            "raw_marching_cubes_component_count": raw_component_count,
            "largest_component_projection_retained_ratio": retained_ratio,
            "component_projection_policy": "deterministic removal of tiny numerical iso-surface islands after connected skeleton field projection",
            "surface_strategy": "thin branching implicit metaball union with smaller terminal lobes, porous microrelief, and marching cubes continuous coral surface",
            "connected_projection": "all branch, pore, ridge, and antler primitives are sampled from or overlap the single active-frontier skeleton",
            "v14_failure_addressed": "reduces V13 claw-like shell, animal-shell, crystal-sheet, and large blob readings by shifting volume into fine branching coral hierarchy",
            "anti_chunk_policy": "no cube particles, no detached shard primitives, no isolated antler islands, no direct tube/cylinder mesh, no local output selection",
        }
    )
    return mesh, controls


def _write_guides(out_dir: Path) -> dict[str, str]:
    from PIL import Image, ImageDraw, ImageFilter

    guide_dir = out_dir / "_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)

    def save(name: str, bg: tuple[int, int, int], palette: list[tuple[int, int, int]], crystal: bool = False) -> str:
        rng = np.random.default_rng(sum((i + 1) * b for i, b in enumerate(name.encode("utf-8"))) % (2**32))
        img = Image.new("RGB", (768, 768), bg)
        draw = ImageDraw.Draw(img)
        for _ in range(620):
            c = palette[int(rng.integers(0, len(palette)))]
            x, y = int(rng.integers(0, 768)), int(rng.integers(0, 768))
            if crystal:
                r = int(rng.integers(12, 48))
                skew = int(rng.integers(-12, 14))
                draw.polygon([(x, y - r), (x + r + skew, y - r // 5), (x + r // 3, y + r), (x - r + skew, y + r // 6)], outline=c, width=2)
            else:
                width = int(rng.integers(3, 10))
                dx, dy = int(rng.normal(0, 92)), int(rng.normal(0, 82))
                draw.line((x, y, x + dx, y + dy), fill=c, width=width)
                if rng.random() < 0.62:
                    fork = (x + dx * 0.72, y + dy * 0.72)
                    draw.line((fork[0], fork[1], fork[0] + rng.normal(0, 42), fork[1] + rng.normal(0, 38)), fill=c, width=max(2, width // 2))
                if rng.random() < 0.36:
                    rr = int(rng.integers(5, 15))
                    draw.ellipse((x - rr, y - rr, x + rr, y + rr), outline=c, width=2)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "staghorn": save("v14_fine_branching_staghorn_guide.png", (235, 132, 124), [(255, 224, 184), (255, 178, 138), (242, 104, 120), (255, 238, 204), (194, 82, 106)]),
        "table": save("v14_fine_branching_table_coral_guide.png", (222, 160, 118), [(255, 240, 204), (246, 198, 144), (220, 132, 102), (250, 222, 178), (166, 94, 88)]),
        "frontier": save("v14_fine_branching_frontier_coral_guide.png", (206, 126, 116), [(255, 226, 188), (238, 154, 124), (206, 86, 108), (250, 208, 168), (130, 82, 96)]),
        "crystal": save("v14_connected_blue_gold_crystal_branch_guide.png", (58, 70, 84), [(110, 148, 176), (188, 214, 220), (234, 210, 142), (82, 104, 130), (196, 174, 112)], crystal=True),
    }


def _case_specs(seed: int) -> list[dict]:
    specs: list[dict] = []

    def add(case_id: str, target: str, mode: str, guide_key: str, offset: int, gpu: int, priority: bool, why: str) -> None:
        mesh, controls = _implicit_frontier_mesh(seed + offset, mode)
        operators = [
            "stochastic_frontier_attachment",
            "occupancy_exclusion",
            "connected_projection",
            "implicit_metaball_union",
            "smooth_marching_cubes_surface",
            "fine_antler_tip_subbranching",
            "reduced_lobe_volume",
            "porous_ridge_microrelief",
            "no_detached_micro_islands",
        ]
        specs.append(
            {
                "case_id": case_id,
                "family": "DLA/frontier",
                "match_target": target,
                "traditional_target": target,
                "recursive_mode": "stochastic frontier attachment with occupancy exclusion and rooted active-tip accretive growth",
                "mesh": mesh,
                "guide_key": guide_key,
                "seed": int(seed + offset),
                "controls": controls,
                "operators": operators,
                "operator_composition": " -> ".join(operators),
                "why_matches_traditional": why,
                "strict_match_notes": why,
                "gpu": int(gpu),
                "case_role": "priority_a100_2" if priority else "backup_a100_2",
            }
        )

    add("v14_dla_branching_staghorn_a", "dla_coral_cluster_900", "staghorn", "staghorn", 701, 4, True, "Strict DLA coral-cluster frontier/exclusion task; V14 uses finer antler-like implicit branching and reduced large lobes to avoid V13 shell/claw readings.")
    add("v14_dla_branching_staghorn_b", "dla_coral_cluster_900", "staghorn", "staghorn", 702, 5, True, "Second fine staghorn seed with the same stochastic frontier attachment and occupancy exclusion controls.")
    add("v14_dla_branching_table_coral_a", "dla_coral_cluster_900", "table", "table", 703, 6, True, "Table-coral variant using thin connected branches, smaller pores, low mass plates, and continuous implicit surface.")
    add("v14_dla_branching_table_coral_b", "dla_coral_cluster_900", "table", "table", 704, 7, True, "Second table-coral strict input for fresh remote generation, not local selection.")
    add("v14_dla_branching_frontier_sheet_a", "dla_frontier_sheet_700", "frontier", "frontier", 705, 4, True, "Frontier target with branching boundary coral and reduced sheet mass while preserving connected projection.")
    add("v14_dla_branching_frontier_sheet_b", "dla_frontier_sheet_700", "frontier", "frontier", 706, 5, True, "Second frontier seed preserving stochastic attachment, occupancy exclusion, and single implicit component.")
    add("v14_dla_branching_crystal_ridge_a", "dla_crystal_cluster_520", "crystal", "crystal", 707, 6, True, "Crystal/DLA boundary case with less slab mass and connected ridge/branch detail instead of detached block shards.")
    add("v14_dla_branching_crystal_ridge_b", "dla_crystal_cluster_520", "crystal", "crystal", 708, 7, False, "Backup non-blocky crystal frontier seed with connected implicit ridges and small branching terminals.")
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
        "tip_radius_max": float(extra.get("thin_tip_radius_max", 0.0)),
        "perforated_membrane_count": int(extra.get("perforated_membrane_count", 0)),
        "ridge_fin_count": int(extra.get("ridge_fin_count", 0)),
        "curved_branch_edges": int(extra.get("curved_branch_edges", 0)),
        "micro_branch_count": int(extra.get("micro_branch_count", 0)),
        "antler_tip_count": int(extra.get("antler_tip_count", 0)),
    }


def _metadata_for(spec: dict, mesh_path: Path, guide_path: str, metrics: dict) -> dict:
    operator_family = "traditional DLA/frontier accretive attachment"
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
            "same_recursive_mode": spec["recursive_mode"],
            "control_parameters": spec["controls"],
            "why_strict_one_to_one": f"{spec['why_matches_traditional']} This is a fresh on a100-2 strict input, not a local selection.",
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
        "why_matches_traditional": spec["why_matches_traditional"],
        "strict_match_notes": spec["strict_match_notes"],
        "case_role": spec["case_role"],
        "visual_readability_contract": {
            "dryrun_visual_floor": "initial OBJ must be one single component before remote generation; connectivity is a gate, not the final visual claim",
            "v13_failure_addressed": "V14 reduces large blob, claw-shell, animal-shell, and crystal-sheet readings by using thinner hierarchical branches and smaller terminal lobes",
            "frontier_structure": "single active-frontier skeleton projected into an implicit field with fine antler tip subbranches, local pores, and ridge microrelief",
            "negative_constraint": "no cube block particles, no detached micro-branches, no isolated sheet islands, no direct tube/cylinder mesh, no local result selection after generation",
            "no_local_selection": "strict cases must be generated fresh on a100-2; local dry-run files are only root inputs",
        },
        "strict_generation_policy": "generate_new_on_a100_2_no_local_selection_or_posthoc_pick",
        "v14_design_note": "implicit fine-branching DLA/coral/crystal input algorithm, not a cylinder mesh or post-hoc repair pass",
        "root_selection_log": {
            "root_source_type": "v14_implicit_fine_branching_coral_input_generator",
            "source_generator": "assets/strict_visual_matched_cases_v14_branching_coral_20260510.py",
            "root_pool_size": 1,
            "root_generation_budget": "local CPU dry-run geometry only; final strict case must be generated fresh on a100-2",
            "root_screening_budget": "no local manual cherry-pick and no V1-V13 post-processing",
            "selection_rank": 1,
            "projection_naturalization_schedule": spec["operators"],
            "readiness_label": "remote_input_dryrun_implicit_single_component_fine_branching",
            "connectivity_anchor_convention": "all density primitives overlap a single active-frontier skeleton before marching cubes",
        },
    }


def _write_readme(out_dir: Path, summary: dict) -> None:
    text = f"""# V14 Branching Coral Strict Visual-Matched Cases Dry Run

Generated by `assets/strict_visual_matched_cases_v14_branching_coral_20260510.py`.

This is a local input dry-run only. It does not launch remote jobs, does not use
SSH, and does not pick or post-process V1-V13 outputs. Strict one-to-one visual
comparison cases must be generated fresh on `{REMOTE_TARGET}` with GPU ids
`{ALLOWED_GPUS}` under:

`{REMOTE_STORAGE_ROOT}`

Storage cap: `{STORAGE_LIMIT_GB}GB`.

V14 focus:

- DLA/coral/frontier/crystal only.
- Same stochastic frontier attachment and occupancy-exclusion mode.
- Initial OBJ inputs are gated to one mesh component.
- Surface is implicit metaball density plus marching cubes, not a welded tube or
  cylinder mesh.
- Smaller terminal lobes, finer antler/tip subbranches, shallow pores, and
  ridged microrelief target the V13 claw-shell / animal-shell / crystal-sheet
  visual failure.

Files:

- `manifest.csv` / `manifest.json`: case-level Trellis2 input manifest.
- `a100-2_cases.txt`: remote-ready `case_id|mesh_path|guide_image|seed|gpu` lines.
- `gpu4_cases.txt` ... `gpu7_cases.txt`: per-GPU splits.
- `gpu4567_cases.txt`: combined GPU 4/5/6/7 split.
- `initial_metrics.csv` / `initial_metrics.json`: pre-texture mesh metrics.
- each case folder: OBJ plus per-case metadata JSON.

Case count: {summary["num_cases"]}
Priority cases: {", ".join(summary["priority_cases"])}
"""
    (out_dir / "README.md").write_text(text, encoding="utf-8")


def materialize(root: Path, out_dir: Path, seed: int = 20260510, case_limit: int | None = None) -> dict:
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
        if metrics["mesh_component_count"] != 1 or metrics["largest_mesh_component_vertex_ratio"] < 1.0:
            raise RuntimeError(f"{spec['case_id']} is not single component: {metrics}")
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
            "why_matches_traditional": spec["why_matches_traditional"],
            "strict_match_notes": spec["strict_match_notes"],
            "case_role": spec["case_role"],
            "strict_one_to_one": "true",
            "generation_policy": "generate_new_on_a100_2_no_local_cherrypick",
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
        "why_matches_traditional",
        "strict_match_notes",
        "case_role",
        "strict_one_to_one",
        "generation_policy",
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
        "tip_radius_max",
        "perforated_membrane_count",
        "ridge_fin_count",
        "curved_branch_edges",
        "micro_branch_count",
        "antler_tip_count",
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
        "surface_generator": "implicit_metaball_marching_cubes_branching_coral_v14",
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
