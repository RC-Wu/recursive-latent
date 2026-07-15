#!/usr/bin/env python3
"""V16 native natural-coral DLA/frontier strict visual-matched input generator.

V16 is a remote-generation branch after V14. It keeps the strict DLA/frontier
contract - stochastic active frontier attachment, occupancy exclusion, bridge
root connectivity, and a single connected support - while making the input
geometry more coral/reef-native before Trellis2 texturing. This is not a local
repair pass over textured outputs.
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
import strict_visual_matched_cases_v14_branching_coral_20260510 as v14


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 100
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_v16_natural_coral_20260510_dryrun"


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


def _parents_from_edges(count: int, edges: list[tuple[int, int]]) -> list[int]:
    return v13._parents_from_edges(count, edges)


def _children_from_edges(count: int, edges: list[tuple[int, int]]) -> dict[int, list[int]]:
    return v13._children_from_edges(count, edges)


def _largest_component_mesh(mesh: pb.Mesh) -> tuple[pb.Mesh, int, float]:
    return v13._largest_component_mesh(mesh)


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


def _motif_params(motif: str) -> dict:
    params = {
        "staghorn": {
            "base_mode": "staghorn",
            "grid": 86,
            "level": 0.49,
            "branch_scale": 0.92,
            "base_scale": (0.62, 0.62, 0.10),
            "polyps": 118,
            "pores": 58,
            "ridges": 88,
            "tip_bonus": 0.020,
        },
        "branching_elkhorn": {
            "base_mode": "table",
            "grid": 86,
            "level": 0.50,
            "branch_scale": 1.07,
            "base_scale": (0.78, 0.68, 0.095),
            "polyps": 112,
            "pores": 62,
            "ridges": 92,
            "tip_bonus": 0.026,
        },
        "table_coral": {
            "base_mode": "table",
            "grid": 86,
            "level": 0.50,
            "branch_scale": 0.98,
            "base_scale": (0.90, 0.78, 0.080),
            "polyps": 104,
            "pores": 66,
            "ridges": 86,
            "tip_bonus": 0.018,
        },
        "porous_reef_plate": {
            "base_mode": "frontier",
            "grid": 86,
            "level": 0.50,
            "branch_scale": 0.95,
            "base_scale": (0.96, 0.62, 0.075),
            "polyps": 100,
            "pores": 78,
            "ridges": 84,
            "tip_bonus": 0.018,
        },
        "frontier_sheet": {
            "base_mode": "frontier",
            "grid": 88,
            "level": 0.49,
            "branch_scale": 0.90,
            "base_scale": (0.98, 0.48, 0.070),
            "polyps": 96,
            "pores": 60,
            "ridges": 82,
            "tip_bonus": 0.016,
        },
        "faceted_crystal_boundary": {
            "base_mode": "crystal",
            "grid": 84,
            "level": 0.48,
            "branch_scale": 0.88,
            "base_scale": (0.58, 0.54, 0.075),
            "polyps": 76,
            "pores": 42,
            "ridges": 74,
            "tip_bonus": 0.014,
        },
    }
    return params[motif]


def _taubin_smooth(mesh: pb.Mesh, iterations: int = 10, lam: float = 0.33, mu: float = -0.35) -> pb.Mesh:
    if not mesh.vertices or not mesh.faces:
        return mesh
    vertices = np.asarray(mesh.vertices, dtype=float)
    adjacency: list[set[int]] = [set() for _ in range(len(vertices))]
    for face in mesh.faces:
        ids = [int(i) - 1 for i in face]
        for a, b in ((ids[0], ids[1]), (ids[1], ids[2]), (ids[2], ids[0])):
            adjacency[a].add(b)
            adjacency[b].add(a)

    def step(points: np.ndarray, amount: float) -> np.ndarray:
        out = points.copy()
        for i, nbrs in enumerate(adjacency):
            if not nbrs:
                continue
            avg = points[list(nbrs)].mean(axis=0)
            out[i] = points[i] + amount * (avg - points[i])
        return out

    for _ in range(iterations):
        vertices = step(vertices, lam)
        vertices = step(vertices, mu)
    return pb.Mesh([tuple(map(float, p)) for p in vertices], mesh.faces)


def _natural_coral_mesh(seed: int, motif: str) -> tuple[pb.Mesh, dict]:
    p = _motif_params(motif)
    nodes, edges, depths, controls = v14._frontier_skeleton(seed, p["base_mode"])
    radii = v14._radii_for_depths(depths, p["base_mode"])
    rng = np.random.default_rng(seed + 16016)
    resolution = int(p["grid"])
    bound = 1.62
    coords = np.linspace(-bound, bound, resolution, dtype=np.float32)
    field = np.zeros((resolution, resolution, resolution), dtype=np.float32)
    children = _children_from_edges(len(nodes), edges)
    parents = _parents_from_edges(len(nodes), edges)
    tips = [i for i in range(1, len(nodes)) if not children.get(i)]

    metaball_samples = 0
    section_min = 14
    for edge_idx, (a, b) in enumerate(edges):
        pa = np.asarray(nodes[a], dtype=float)
        pb_ = np.asarray(nodes[b], dtype=float)
        axis = pb_ - pa
        length = float(np.linalg.norm(axis))
        if length < 1e-7:
            continue
        u, v, w = _basis(axis)
        samples = max(section_min, int(length / 0.018))
        phase = edge_idx * 0.71 + rng.uniform(-0.35, 0.35)
        for s in range(samples + 1):
            t = s / max(samples, 1)
            center = pa * (1.0 - t) + pb_ * t
            undulate = 1.0 + 0.070 * math.sin(7.0 * t + phase) + 0.040 * math.sin(19.0 * t + phase * 0.53)
            if motif == "faceted_crystal_boundary":
                undulate = 0.98 + 0.035 * math.sin(5.0 * t + phase)
            radius = (float(radii[a]) * (1.0 - t) + float(radii[b]) * t) * float(p["branch_scale"]) * undulate
            helical = (u * math.sin(2.0 * math.pi * t + phase) + v * math.cos(2.0 * math.pi * t + phase)) * radius * 0.11
            _stamp_ball(field, coords, center + helical, max(radius, 0.009), 1.12)
            metaball_samples += 1
            if motif in {"branching_elkhorn", "table_coral", "porous_reef_plate", "frontier_sheet"} and s % 5 == 0:
                sheet_normal = _unit(np.array([0.0, 0.0, 1.0]) + 0.18 * v)
                _stamp_ellipsoid(field, coords, center + sheet_normal * radius * 0.25, (u, v, w), (radius * 1.9, radius * 0.62, radius * 0.40), 0.20)
                metaball_samples += 1

    rounded_tips = 0
    for idx in tips:
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        for j, scale in enumerate((0.82, 0.58, 0.34)):
            center = np.asarray(nodes[idx]) + axis * (float(p["tip_bonus"]) * (j + 1))
            _stamp_ball(field, coords, center, max(float(radii[idx]) * scale, 0.010), 0.96)
            metaball_samples += 1
        rounded_tips += 1

    base_axes = (np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0]))
    _stamp_ellipsoid(field, coords, np.array([0.0, 0.0, -0.045]), base_axes, p["base_scale"], 0.44, cutoff=2.0)
    _stamp_ball(field, coords, np.array([0.0, 0.0, -0.018]), 0.18, 0.62)
    metaball_samples += 2

    ridge_count = 0
    ridge_edges = list(edges)
    rng.shuffle(ridge_edges)
    for a, b in ridge_edges:
        if ridge_count >= int(p["ridges"]):
            break
        pa = np.asarray(nodes[a], dtype=float)
        pb_ = np.asarray(nodes[b], dtype=float)
        axis = pb_ - pa
        if float(np.linalg.norm(axis)) < 1e-7:
            continue
        u, v, w = _basis(axis)
        t = float(rng.uniform(0.14, 0.88))
        side = -1.0 if ridge_count % 2 else 1.0
        normal = _unit(v * side + u * rng.uniform(-0.24, 0.24) + np.array([0.0, 0.0, 0.08]))
        center = pa * (1.0 - t) + pb_ * t + normal * (float(radii[a]) * 0.55 + 0.009)
        if motif == "faceted_crystal_boundary":
            _stamp_ellipsoid(field, coords, center, (u, normal, w), (0.050, 0.012, 0.030), 0.28)
        else:
            _stamp_ellipsoid(field, coords, center, (u, normal, w), (0.040, 0.012, 0.022), 0.25)
        ridge_count += 1
        metaball_samples += 1

    branch_sites = list(range(1, len(nodes)))
    rng.shuffle(branch_sites)
    polyp_count = 0
    for idx in branch_sites:
        if polyp_count >= int(p["polyps"]):
            break
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        u, v, _ = _basis(axis)
        angle = float(rng.uniform(0.0, 2.0 * math.pi))
        normal = _unit(math.cos(angle) * u + math.sin(angle) * v + 0.08 * axis)
        anchor = np.asarray(nodes[idx]) + normal * (float(radii[idx]) * 0.70 + 0.006)
        _stamp_ball(field, coords, anchor, rng.uniform(0.0085, 0.0145), 0.44)
        polyp_count += 1
        metaball_samples += 1

    pore_count = 0
    pore_edges = list(edges)
    rng.shuffle(pore_edges)
    for a, b in pore_edges:
        if pore_count >= int(p["pores"]):
            break
        pa = np.asarray(nodes[a], dtype=float)
        pb_ = np.asarray(nodes[b], dtype=float)
        axis = pb_ - pa
        if float(np.linalg.norm(axis)) < 1e-7:
            continue
        u, v, _ = _basis(axis)
        t = float(rng.uniform(0.20, 0.82))
        normal = _unit(v * (1.0 if pore_count % 2 else -1.0) + u * rng.uniform(-0.28, 0.28))
        center = pa * (1.0 - t) + pb_ * t + normal * (float(radii[a]) * 0.72 + 0.010)
        _stamp_ball(field, coords, center, rng.uniform(0.022, 0.034), -0.35)
        pore_count += 1

    sigma = 0.46 if motif != "faceted_crystal_boundary" else 0.34
    field = gaussian_filter(field, sigma=sigma)
    verts, faces, _normals, _values = marching_cubes(
        field,
        level=float(p["level"]),
        spacing=(float(coords[1] - coords[0]), float(coords[1] - coords[0]), float(coords[1] - coords[0])),
    )
    verts = verts + np.array([coords[0], coords[0], coords[0]], dtype=float)
    mesh = pb.Mesh([tuple(map(float, v)) for v in verts], [tuple(int(i) + 1 for i in f) for f in faces])
    mesh, raw_component_count, retained_ratio = _largest_component_mesh(mesh)
    smoothing_iterations = 10 if motif != "faceted_crystal_boundary" else 8
    mesh = _taubin_smooth(mesh, iterations=smoothing_iterations)

    controls.update(
        {
            "natural_coral_motif": motif,
            "bridge_root_connectivity": True,
            "continuous_base": True,
            "direct_voxel_blocks": False,
            "direct_straight_rods": False,
            "flat_terminal_cuts": False,
            "huge_shell_blob": False,
            "direct_tube_mesh": False,
            "implicit_grid_resolution": resolution,
            "implicit_field_level": float(p["level"]),
            "section_samples_per_edge": section_min,
            "metaball_sample_count": int(metaball_samples),
            "rounded_terminal_tip_count": int(rounded_tips),
            "attached_polyp_count": int(polyp_count),
            "subtle_pore_depression_count": int(pore_count),
            "surface_ridge_count": int(ridge_count),
            "taubin_smoothing_iterations": int(smoothing_iterations),
            "normal_shape_smoothing": "gaussian implicit field smoothing plus Taubin mesh smoothing before remote input export",
            "largest_component_vertex_ratio_min": 0.999,
            "raw_marching_cubes_component_count": int(raw_component_count),
            "largest_component_projection_retained_ratio": float(retained_ratio),
            "component_projection_policy": "drop only tiny numerical iso-surface islands from the generator's connected implicit support",
            "surface_strategy": "generator-native high-resolution implicit SDF/metaball coral field with rounded tips, attached polyps, shallow pores, ridges, continuous base, and smoothing",
            "v16_naturalization_policy": "generator-native naturalization in root input geometry, not local repair or post-hoc textured output postprocessing",
            "frontier_attachment_mode": "stochastic active-tip frontier attachment with occupancy exclusion and bridge/root connected projection",
            "occupancy_exclusion": "candidate frontier nodes are rejected inside depth-scaled exclusion radius before the implicit connected support is sampled",
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
            x = int(rng.integers(28, 740))
            y = int(rng.integers(28, 740))
            if motif == "crystal":
                r = int(rng.integers(12, 52))
                skew = int(rng.integers(-16, 17))
                draw.polygon([(x, y - r), (x + r + skew, y - r // 4), (x + r // 2, y + r), (x - r + skew, y + r // 5)], outline=c, width=2)
            elif motif in {"plate", "frontier"}:
                rx = int(rng.integers(20, 72))
                ry = int(rng.integers(6, 24))
                draw.ellipse((x - rx, y - ry, x + rx, y + ry), outline=c, width=int(rng.integers(2, 5)))
                if rng.random() < 0.62:
                    draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=c)
            else:
                width = int(rng.integers(3, 9))
                dx = int(rng.normal(0, 86))
                dy = int(rng.normal(-16, 76))
                draw.line((x, y, x + dx, y + dy), fill=c, width=width)
                if rng.random() < 0.70:
                    fork = (x + dx * 0.70, y + dy * 0.70)
                    draw.line((fork[0], fork[1], fork[0] + rng.normal(0, 48), fork[1] + rng.normal(-12, 44)), fill=c, width=max(2, width // 2))
                if rng.random() < 0.48:
                    rr = int(rng.integers(4, 12))
                    draw.ellipse((x - rr, y - rr, x + rr, y + rr), fill=c)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "staghorn": save("v16_pink_ivory_staghorn_pbr_guide.png", (226, 128, 122), [(255, 231, 204), (252, 179, 142), (230, 88, 116), (255, 244, 224), (176, 82, 98)], "branch"),
        "elkhorn": save("v16_warm_branching_elkhorn_pbr_guide.png", (218, 154, 118), [(255, 236, 196), (244, 194, 136), (218, 124, 92), (164, 88, 78), (255, 220, 174)], "branch"),
        "table": save("v16_layered_table_coral_pbr_guide.png", (210, 142, 112), [(255, 234, 190), (235, 174, 122), (200, 94, 104), (250, 216, 172), (128, 82, 86)], "plate"),
        "reef": save("v16_porous_reef_plate_polyps_pbr_guide.png", (192, 122, 112), [(248, 220, 184), (226, 150, 118), (176, 84, 100), (255, 238, 210), (130, 92, 92)], "plate"),
        "frontier": save("v16_frontier_sheet_reef_edge_pbr_guide.png", (204, 128, 116), [(255, 230, 188), (238, 158, 124), (202, 84, 108), (248, 208, 166), (114, 78, 92)], "frontier"),
        "crystal": save("v16_blue_gold_faceted_crystal_boundary_pbr_guide.png", (52, 64, 82), [(104, 144, 176), (184, 210, 220), (236, 210, 136), (78, 98, 128), (196, 172, 104)], "crystal"),
    }


def _case_specs(seed: int) -> list[dict]:
    specs: list[dict] = []

    def add(case_id: str, target: str, motif: str, guide_key: str, offset: int, gpu: int, priority: bool, why: str) -> None:
        mesh, controls = _natural_coral_mesh(seed + offset, motif)
        operators = [
            "stochastic_frontier_attachment",
            "occupancy_exclusion",
            "bridge_root_connectivity",
            "implicit_sdf_union",
            "high_resolution_marching_cubes",
            "taubin_laplacian_shape_smoothing",
            "rounded_tapered_terminal_tips",
            "subtle_pore_depressions",
            "attached_polyp_buds",
            "surface_ridge_microrelief",
            "continuous_reef_base",
            "natural_coral_semantics",
        ]
        specs.append(
            {
                "case_id": case_id,
                "family": "DLA/frontier",
                "match_target": target,
                "traditional_target": target,
                "recursive_mode": "stochastic frontier attachment with occupancy exclusion, bridge/root connectivity, and rooted accretive growth",
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

    add("v16_dla_natural_staghorn_a", "dla_coral_cluster_900", "staghorn", "staghorn", 801, 4, True, "Strict DLA coral-cluster frontier/exclusion case with native staghorn coral branching, rounded tips, attached polyps, and continuous reef base.")
    add("v16_dla_natural_staghorn_b", "dla_coral_cluster_900", "staghorn", "staghorn", 802, 5, True, "Second staghorn seed preserving the same frontier attachment and occupancy exclusion controls for fresh a100-2 generation.")
    add("v16_dla_natural_elkhorn_a", "dla_coral_cluster_900", "branching_elkhorn", "elkhorn", 803, 6, True, "Branching elkhorn variant: broader forked coral surfaces without straight rods or disconnected lobes.")
    add("v16_dla_natural_table_coral_a", "dla_coral_cluster_900", "table_coral", "table", 804, 7, True, "Table-coral variant with smooth connected plate-like branch envelopes, pores, ridges, and tapered terminal edges.")
    add("v16_dla_natural_porous_reef_plate_a", "dla_frontier_sheet_700", "porous_reef_plate", "reef", 805, 4, True, "Porous reef-plate frontier case preserving boundary growth while making the connected plate read as coral reef rather than a flat slab.")
    add("v16_dla_natural_frontier_sheet_a", "dla_frontier_sheet_700", "frontier_sheet", "frontier", 806, 5, True, "Frontier sheet edge with accretive DLA attachment, continuous base bridges, shallow pores, and natural coral edge texture.")
    add("v16_dla_natural_crystal_boundary_a", "dla_crystal_cluster_520", "faceted_crystal_boundary", "crystal", 807, 6, True, "Faceted DLA/crystal boundary case with connected branch ridges rather than detached block shards.")
    add("v16_dla_natural_crystal_boundary_b", "dla_crystal_cluster_520", "faceted_crystal_boundary", "crystal", 808, 7, False, "Backup faceted crystal-boundary seed with high-resolution connected implicit support and no voxel blocks.")
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
        "rounded_terminal_tip_count": int(extra.get("rounded_terminal_tip_count", 0)),
        "attached_polyp_count": int(extra.get("attached_polyp_count", 0)),
        "subtle_pore_depression_count": int(extra.get("subtle_pore_depression_count", 0)),
        "surface_ridge_count": int(extra.get("surface_ridge_count", 0)),
        "taubin_smoothing_iterations": int(extra.get("taubin_smoothing_iterations", 0)),
        "implicit_grid_resolution": int(extra.get("implicit_grid_resolution", 0)),
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
            "dryrun_visual_floor": "initial OBJ must be one single main component or LCR >= 0.999 before remote generation",
            "v14_failure_addressed": "V16 targets V14 faceted/low-poly coarse branches and weak coral semantics with high-resolution implicit surfaces, smoothing, polyps, pores, ridges, and rounded tips",
            "positive_constraint": "must read as coral/reef growth: staghorn, elkhorn, table coral, porous reef plate, frontier sheet, or connected faceted crystal boundary",
            "negative_constraint": "no voxel blocks, no straight rods, no flat terminal cuts, no fragmented islands, no huge shell/blob, and no local textured-output cherry-pick",
            "no_local_selection": "strict cases must be generated fresh on a100-2; local dry-run files are only root inputs",
        },
        "strict_generation_policy": "generate_new_on_a100_2_no_local_selection_or_posthoc_pick",
        "v16_design_note": "native high-resolution implicit natural coral input branch after V14; not output repair",
        "root_selection_log": {
            "root_source_type": "v16_native_natural_coral_input_generator",
            "source_generator": "assets/strict_visual_matched_cases_v16_natural_coral_20260510.py",
            "root_pool_size": 1,
            "root_generation_budget": "local CPU dry-run geometry only; final strict cases must be generated fresh on a100-2 GPUs 4-7",
            "root_screening_budget": "no local manual cherry-pick and no V1-V15 textured-output postprocessing",
            "selection_rank": 1,
            "projection_naturalization_schedule": spec["operators"],
            "readiness_label": "remote_input_dryrun_native_natural_coral_single_component",
            "connectivity_anchor_convention": "all density, pore, ridge, polyp, and base primitives overlap one active-frontier skeleton before marching cubes",
        },
    }


def _write_readme(out_dir: Path, summary: dict) -> None:
    text = f"""# V16 Natural Coral Strict Visual-Matched Cases Dry Run

Generated by `assets/strict_visual_matched_cases_v16_natural_coral_20260510.py`.

This is a local input dry-run only. It does not launch remote jobs and does not
repair or select local textured outputs. Strict visual cases must be generated
fresh on `{REMOTE_TARGET}` with GPU ids `{ALLOWED_GPUS}` under:

`{REMOTE_STORAGE_ROOT}`

V16 focus:

- DLA/frontier/coral/crystal only.
- Same frontier attachment, occupancy exclusion, and rooted bridge connectivity.
- High-resolution implicit SDF/metaball fields with marching cubes.
- Generator-side Gaussian and Taubin/Laplacian smoothing.
- Rounded/tapered terminal tips, attached polyps, shallow pore depressions,
  surface ridges, and continuous reef bases.
- No voxel blocks, straight rods, flat cuts, fragmented components, or huge
  shell/blob inputs.

Files:

- `manifest.csv` / `manifest.json`: case-level Trellis2 input manifest.
- `a100-2_cases.txt`: remote-ready `case_id|mesh_path|guide_image|seed|gpu` lines.
- `gpu4_cases.txt` ... `gpu7_cases.txt`: two cases per GPU split.
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
        if metrics["mesh_component_count"] != 1 and metrics["largest_mesh_component_vertex_ratio"] < 0.999:
            raise RuntimeError(f"{spec['case_id']} failed V16 connectivity gate: {metrics}")
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
        "rounded_terminal_tip_count",
        "attached_polyp_count",
        "subtle_pore_depression_count",
        "surface_ridge_count",
        "taubin_smoothing_iterations",
        "implicit_grid_resolution",
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
        "surface_generator": "implicit_sdf_taubin_natural_coral_v16",
        "connectivity_gate": {"largest_component_vertex_ratio_min": 0.999},
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
