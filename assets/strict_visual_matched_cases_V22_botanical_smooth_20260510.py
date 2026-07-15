#!/usr/bin/env python3
"""V22 strict smooth botanical/root matched input generator.

V22 fixes the V17/V19 failure mode by keeping the same L-system and
space-colonization comparison targets while removing block-like surfaces and
mesh token stamping.  Every dry-run case is an OBJ input with a face-connected
smooth swept support and many attached semantic leaves, needles, tendrils, or
rootlets before mesh export.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import baseline_matrix_20260509 as bm
import procedural_baselines as pb
import recursive_growth_mesh_metrics as rgm
import space_colonization_baseline as scb


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 100
CONNECTIVITY_LCR_MIN = 0.999
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V22_botanical_smooth_20260510_dryrun"

SURFACE_STRATEGY = "smooth_implicit_swept_connected_support_with_attached_semantic_details"
COMMON_OPERATORS = [
    "same_classical_recursive_mode",
    "lsystem_or_space_colonization_control",
    "smooth_implicit_radius_field",
    "swept_connected_support",
    "shared_vertex_semantic_detail_attachment",
    "pre_export_leaf_needle_rootlet_details",
    "obj_mesh_input_only",
    "pbr_guide_output_for_trellis2",
    "largest_component_gate",
]


DetailCounts = Dict[str, int]


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _basis(axis: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = _unit(np.asarray(axis, dtype=float))
    seed = np.array([0.0, 0.0, 1.0]) if abs(float(w[2])) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = _unit(np.cross(w, seed))
    v = _unit(np.cross(w, u))
    return u, v, w


def _normalize_nodes(nodes: List[np.ndarray], extent: float = 2.55) -> List[np.ndarray]:
    arr = np.asarray(nodes, dtype=float)
    mn = arr.min(axis=0)
    mx = arr.max(axis=0)
    center = (mn + mx) * 0.5
    scale = max(float((mx - mn).max()), 1e-6)
    return [(np.asarray(n, dtype=float) - center) * (extent / scale) for n in nodes]


def _children(parents: List[int]) -> Dict[int, List[int]]:
    out: Dict[int, List[int]] = {i: [] for i in range(len(parents))}
    for idx, parent in enumerate(parents):
        if int(parent) >= 0:
            out.setdefault(int(parent), []).append(int(idx))
    return out


def _terminal_nodes(parents: List[int]) -> List[int]:
    child_map = _children(parents)
    return [idx for idx in range(1, len(parents)) if not child_map.get(idx)]


def _graph_edges(parents: List[int]) -> List[Tuple[int, int]]:
    return [(int(parent), int(idx)) for idx, parent in enumerate(parents) if int(parent) >= 0]


def _dedupe_edges(edges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    seen = set()
    out: List[Tuple[int, int]] = []
    for a, b in edges:
        if int(a) == int(b):
            continue
        key = (min(int(a), int(b)), max(int(a), int(b)))
        if key in seen:
            continue
        seen.add(key)
        out.append((int(a), int(b)))
    return out


def _radii_from_parents(parents: List[int], base: float, taper: float, floor: float) -> List[float]:
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    radii = []
    for depth in depths:
        t = depth / max(float(max_depth), 1.0)
        radii.append(max(float(base) * max(1.0 - float(taper) * t, 0.08) ** 1.12, float(floor)))
    return radii


def _append_child(
    nodes: List[np.ndarray],
    parents: List[int],
    radii: List[float],
    anchor: int,
    direction: np.ndarray,
    length: float,
    radius: float,
) -> int:
    nodes.append(np.asarray(nodes[anchor], dtype=float) + _unit(direction) * float(length))
    parents.append(int(anchor))
    radii.append(float(radius))
    return len(nodes) - 1


def _node_axis(nodes: List[np.ndarray], parents: List[int], idx: int) -> np.ndarray:
    parent = int(parents[idx]) if int(parents[idx]) >= 0 else 0
    axis = _unit(np.asarray(nodes[idx], dtype=float) - np.asarray(nodes[parent], dtype=float))
    if float(np.linalg.norm(axis)) < 1e-8:
        axis = np.array([0.0, 0.0, 1.0], dtype=float)
    return axis


def _repeat_anchor_indices(parents: List[int], count: int, prefer_terminal: bool = True, min_depth_fraction: float = 0.42) -> List[int]:
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    terminals = _terminal_nodes(parents)
    if prefer_terminal and terminals:
        base = terminals
    else:
        base = [idx for idx in range(1, len(parents)) if depths[idx] >= max_depth * min_depth_fraction]
    if not base:
        base = list(range(1, len(parents))) or [0]
    base = sorted(base, key=lambda idx: (depths[idx], idx), reverse=True)
    return [base[(i * 7) % len(base)] for i in range(int(count))]


def _blank_counts() -> DetailCounts:
    return {"needle_count": 0, "leaf_count": 0, "rootlet_count": 0, "tendril_count": 0}


def _total_details(counts: DetailCounts) -> int:
    return int(sum(counts.values()))


def _smooth_support_mesh(
    nodes: List[np.ndarray],
    edges: List[Tuple[int, int]],
    radii: List[float],
    sides: int = 14,
    ovality: float = 0.16,
) -> pb.Mesh:
    """Face-connected tapered sweep with one shared scaffold vertex per node."""

    mesh = pb.Mesh([], [])
    center_indices: List[int] = []
    for node in nodes:
        mesh.vertices.append(tuple(np.asarray(node, dtype=float)))
        center_indices.append(len(mesh.vertices))

    incident_rings: List[List[List[int]]] = [[] for _ in nodes]
    for edge_i, (a, b) in enumerate(_dedupe_edges(edges)):
        start = np.asarray(nodes[a], dtype=float)
        end = np.asarray(nodes[b], dtype=float)
        axis = end - start
        if float(np.linalg.norm(axis)) < 1e-8:
            continue
        u, v, _w = _basis(axis)
        twist = 0.18 * math.sin(edge_i * 1.37)
        base = len(mesh.vertices)
        for endpoint, radius in ((start, radii[a]), (end, radii[b])):
            for i in range(sides):
                theta = math.tau * i / sides + twist
                profile = 1.0 + float(ovality) * math.sin(theta * 2.0 + edge_i * 0.29)
                d = math.cos(theta) * u * profile + math.sin(theta) * v * (2.0 - profile)
                mesh.vertices.append(tuple(endpoint + d * float(radius)))
        ring0 = [base + i + 1 for i in range(sides)]
        ring1 = [base + sides + i + 1 for i in range(sides)]
        for i in range(sides):
            j = (i + 1) % sides
            mesh.faces.append((ring0[i], ring0[j], ring1[i]))
            mesh.faces.append((ring0[j], ring1[j], ring1[i]))
        incident_rings[a].append(ring0)
        incident_rings[b].append(ring1)

    for node_idx, rings in enumerate(incident_rings):
        center = center_indices[node_idx]
        for ring in rings:
            for i in range(sides):
                j = (i + 1) % sides
                mesh.faces.append((center, ring[i], ring[j]))
        for ridx in range(len(rings) - 1):
            ring = rings[ridx]
            next_ring = rings[ridx + 1]
            slot = ridx % sides
            mesh.faces.append((ring[slot], ring[(slot + 1) % sides], next_ring[slot]))
            mesh.faces.append((ring[(slot + 1) % sides], next_ring[(slot + 1) % sides], next_ring[slot]))

    setattr(mesh, "center_indices", center_indices)
    return mesh


def _add_curved_tube_detail(
    mesh: pb.Mesh,
    anchor_idx: int,
    anchor: np.ndarray,
    direction: np.ndarray,
    length: float,
    radius: float,
    rng: np.random.Generator,
    segments: int = 4,
    sides: int = 7,
    curl: float = 0.16,
) -> None:
    direction = _unit(np.asarray(direction, dtype=float))
    u, v, w = _basis(direction)
    phase = float(rng.uniform(0.0, math.tau))
    bend = _unit(math.cos(phase) * u + math.sin(phase) * v + 0.25 * rng.normal(0.0, 1.0) * w)
    rings: List[List[int]] = []
    prev = np.asarray(anchor, dtype=float)
    for s in range(1, int(segments) + 1):
        t = s / float(segments)
        center = np.asarray(anchor, dtype=float) + direction * float(length) * t + bend * float(length) * float(curl) * math.sin(math.pi * t)
        tangent = _unit(center - prev)
        ru, rv, _rw = _basis(tangent if float(np.linalg.norm(tangent)) > 1e-8 else direction)
        r = float(radius) * (1.0 - 0.72 * t) + float(radius) * 0.16
        ring: List[int] = []
        for i in range(sides):
            theta = math.tau * i / sides + phase * 0.13
            p = center + (math.cos(theta) * ru + math.sin(theta) * rv) * r
            mesh.vertices.append(tuple(p))
            ring.append(len(mesh.vertices))
        rings.append(ring)
        prev = center
    first = rings[0]
    for i in range(sides):
        j = (i + 1) % sides
        mesh.faces.append((anchor_idx, first[i], first[j]))
    for a, b in zip(rings[:-1], rings[1:]):
        for i in range(sides):
            j = (i + 1) % sides
            mesh.faces.append((a[i], a[j], b[i]))
            mesh.faces.append((a[j], b[j], b[i]))
    tip_center = np.mean(np.asarray([mesh.vertices[i - 1] for i in rings[-1]], dtype=float), axis=0) + direction * float(length) * 0.075
    mesh.vertices.append(tuple(tip_center))
    tip = len(mesh.vertices)
    last = rings[-1]
    for i in range(sides):
        j = (i + 1) % sides
        mesh.faces.append((last[i], tip, last[j]))


def _add_lanceolate_leaf(
    mesh: pb.Mesh,
    anchor_idx: int,
    anchor: np.ndarray,
    direction: np.ndarray,
    length: float,
    width: float,
    rng: np.random.Generator,
    rows: int = 6,
) -> None:
    direction = _unit(np.asarray(direction, dtype=float))
    u, v, w = _basis(direction)
    side = _unit(u + 0.18 * rng.normal(0.0, 1.0) * v)
    lift = _unit(np.cross(side, w))
    row_indices: List[Tuple[int, int, int]] = []
    for r in range(1, int(rows) + 1):
        t = r / float(rows)
        center = np.asarray(anchor, dtype=float) + w * float(length) * t + lift * float(length) * 0.09 * math.sin(math.pi * t)
        half_width = float(width) * math.sin(math.pi * t) * (0.78 + 0.10 * math.sin(5.0 * t))
        midrib_offset = lift * float(width) * 0.05 * math.sin(math.tau * t)
        points = [center - side * half_width, center + midrib_offset, center + side * half_width]
        inds = []
        for p in points:
            mesh.vertices.append(tuple(p))
            inds.append(len(mesh.vertices))
        row_indices.append((inds[0], inds[1], inds[2]))
    first = row_indices[0]
    for face in ((anchor_idx, first[0], first[1]), (anchor_idx, first[1], first[2])):
        mesh.faces.append(face)
        mesh.faces.append((face[0], face[2], face[1]))
    for row_a, row_b in zip(row_indices[:-1], row_indices[1:]):
        strips = [
            (row_a[0], row_b[0], row_a[1]),
            (row_a[1], row_b[0], row_b[1]),
            (row_a[1], row_b[1], row_a[2]),
            (row_a[2], row_b[1], row_b[2]),
        ]
        for face in strips:
            mesh.faces.append(face)
            mesh.faces.append((face[0], face[2], face[1]))


def _scatter_needles(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    count: int,
    length_range: Tuple[float, float],
) -> DetailCounts:
    centers = getattr(mesh, "center_indices")
    counts = _blank_counts()
    for k, idx in enumerate(_repeat_anchor_indices(parents, count=count, prefer_terminal=True)):
        axis = _node_axis(nodes, parents, idx)
        u, v, _w = _basis(axis)
        lateral = math.cos(k * 2.399) * u + math.sin(k * 2.399) * v
        direction = _unit(0.62 * axis + 0.50 * lateral + np.array([0.0, 0.0, 0.18]) + rng.normal(0.0, 0.055, 3))
        _add_curved_tube_detail(
            mesh,
            centers[idx],
            nodes[idx],
            direction,
            float(rng.uniform(*length_range)),
            float(rng.uniform(0.0026, 0.0058)),
            rng,
            segments=3,
            sides=7,
            curl=0.06,
        )
        counts["needle_count"] += 1
    return counts


def _scatter_rootlets(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    count: int,
    downward: float = 0.58,
) -> DetailCounts:
    centers = getattr(mesh, "center_indices")
    counts = _blank_counts()
    for k, idx in enumerate(_repeat_anchor_indices(parents, count=count, prefer_terminal=False, min_depth_fraction=0.26)):
        axis = _node_axis(nodes, parents, idx)
        u, v, _w = _basis(axis)
        lateral = math.cos(k * 1.733) * u + math.sin(k * 1.733) * v
        direction = _unit(-0.12 * axis + 0.54 * lateral + np.array([0.0, 0.0, -float(downward)]) + rng.normal(0.0, 0.08, 3))
        _add_curved_tube_detail(
            mesh,
            centers[idx],
            nodes[idx],
            direction,
            float(rng.uniform(0.070, 0.175)),
            float(rng.uniform(0.0022, 0.0048)),
            rng,
            segments=4,
            sides=6,
            curl=0.20,
        )
        counts["rootlet_count"] += 1
    return counts


def _scatter_leaves(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    count: int,
    scale: Tuple[float, float],
) -> DetailCounts:
    centers = getattr(mesh, "center_indices")
    counts = _blank_counts()
    for k, idx in enumerate(_repeat_anchor_indices(parents, count=count, prefer_terminal=False, min_depth_fraction=0.40)):
        axis = _node_axis(nodes, parents, idx)
        u, v, _w = _basis(axis)
        lateral = math.cos(k * 2.077) * u + math.sin(k * 2.077) * v
        direction = _unit(0.42 * axis + 0.68 * lateral + np.array([0.0, 0.0, 0.12]) + rng.normal(0.0, 0.06, 3))
        length = float(rng.uniform(*scale))
        _add_lanceolate_leaf(mesh, centers[idx], nodes[idx], direction, length, length * float(rng.uniform(0.20, 0.36)), rng, rows=6)
        counts["leaf_count"] += 1
    return counts


def _scatter_tendrils(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    count: int,
) -> DetailCounts:
    centers = getattr(mesh, "center_indices")
    counts = _blank_counts()
    for k, idx in enumerate(_repeat_anchor_indices(parents, count=count, prefer_terminal=False, min_depth_fraction=0.28)):
        axis = _node_axis(nodes, parents, idx)
        u, v, _w = _basis(axis)
        lateral = math.cos(k * 1.177) * u + math.sin(k * 1.177) * v
        direction = _unit(0.28 * axis + lateral + np.array([0.0, 0.0, 0.12]) + rng.normal(0.0, 0.05, 3))
        _add_curved_tube_detail(
            mesh,
            centers[idx],
            nodes[idx],
            direction,
            float(rng.uniform(0.105, 0.235)),
            float(rng.uniform(0.0026, 0.0052)),
            rng,
            segments=5,
            sides=6,
            curl=0.46,
        )
        counts["tendril_count"] += 1
    return counts


def _merge_counts(*parts: DetailCounts) -> DetailCounts:
    out = _blank_counts()
    for part in parts:
        for key, value in part.items():
            out[key] += int(value)
    return out


def _finalize_controls(base: Dict, nodes: List[np.ndarray], edges: List[Tuple[int, int]], counts: DetailCounts) -> Dict:
    controls = dict(base)
    controls.update(
        {
            "mesh_input_format": "obj",
            "same_classical_task_mode": True,
            "connected_support": True,
            "connectivity_gate_lcr_min": CONNECTIVITY_LCR_MIN,
            "low_poly_block_stamping": False,
            "mesh_token_stamping": False,
            "procedural_block_tokens": False,
            "smooth_implicit_support": True,
            "swept_support": True,
            "shared_vertex_attachment": True,
            "support_edge_count": int(len(_dedupe_edges(edges))),
            "shared_vertex_anchor_count": int(len(nodes)),
            "semantic_detail_count": _total_details(counts),
            "needle_count": int(counts["needle_count"]),
            "leaf_count": int(counts["leaf_count"]),
            "rootlet_count": int(counts["rootlet_count"]),
            "tendril_count": int(counts["tendril_count"]),
            "direct_voxel_blocks": False,
            "detached_chunk_policy": "forbid_detached_detail_islands_by_shared_vertex_faces",
            "surface_strategy": SURFACE_STRATEGY,
        }
    )
    return controls


def _build_lsystem_pine(seed: int, depth: int = 5) -> Tuple[pb.Mesh, Dict, DetailCounts, Dict]:
    rng = np.random.default_rng(seed + 2201 + depth)
    nodes0, parents = bm.lsystem_case("tree", depth=depth, seed=seed)
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in nodes0], 2.72 if depth >= 6 else 2.58)
    radii = _radii_from_parents(parents, base=0.094 if depth <= 5 else 0.088, taper=0.78, floor=0.010)
    edges = _graph_edges(parents)
    mesh = _smooth_support_mesh(nodes, edges, radii, sides=14, ovality=0.14)
    counts = _merge_counts(
        _scatter_needles(mesh, nodes, parents, rng, count=190 if depth >= 6 else 158, length_range=(0.055, 0.122)),
        _scatter_leaves(mesh, nodes, parents, rng, count=24 if depth >= 6 else 18, scale=(0.060, 0.115)),
    )
    controls = _finalize_controls(
        {
            "source": "baseline_matrix_20260509.lsystem_case(tree)",
            "recursive_depth": int(depth),
            "target_silhouette": "conifer pine canopy",
            "grammar_rule": "F -> F[+F][-F][&F][^F]F with decreasing radii and terminal needle clusters",
            "depth_sweep_variant": bool(depth >= 6),
        },
        nodes,
        edges,
        counts,
    )
    grammar = {
        "grammar_family": "L-system",
        "grammar_symbols": "F,+,-,[,],&,^,terminal needle and leaf attachments",
        "target_symbol": "F",
        "operator_to_traditional_mapping": {
            "F": "advance the turtle and create a swept branch segment",
            "+/-": "yaw the branch around the spread axis",
            "&/^": "pitch the branch for canopy volume",
            "[]": "push/pop recursive branch state",
        },
        "remote_comparison_unit": "one generated OBJ input to one traditional target",
    }
    return mesh, controls, counts, grammar


def _build_lsystem_root(seed: int, depth: int = 5) -> Tuple[pb.Mesh, Dict, DetailCounts, Dict]:
    rng = np.random.default_rng(seed + 2202)
    nodes0, parents = bm.lsystem_case("root", depth=depth, seed=seed)
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in nodes0], 2.70)
    radii = _radii_from_parents(parents, base=0.086, taper=0.83, floor=0.0058)
    edges = _graph_edges(parents)
    mesh = _smooth_support_mesh(nodes, edges, radii, sides=12, ovality=0.24)
    counts = _scatter_rootlets(mesh, nodes, parents, rng, count=190, downward=0.72)
    controls = _finalize_controls(
        {
            "source": "baseline_matrix_20260509.lsystem_case(root)",
            "recursive_depth": int(depth),
            "target_silhouette": "root fan",
            "grammar_rule": "F -> F[+F][-F]F with downward tropism and dense pre-export rootlets",
            "root_tropism": "negative_z_bias",
        },
        nodes,
        edges,
        counts,
    )
    grammar = {
        "grammar_family": "L-system",
        "grammar_symbols": "F,+,-,[,],root_tropism,rootlet attachments",
        "target_symbol": "F",
        "operator_to_traditional_mapping": {
            "F": "advance root segment and taper the implicit radius",
            "+/-": "fan roots laterally",
            "[]": "branch root state without changing the target category",
            "root_tropism": "bias recursive growth downward",
        },
        "remote_comparison_unit": "one generated OBJ input to one traditional target",
    }
    return mesh, controls, counts, grammar


def _build_lsystem_vine(seed: int) -> Tuple[pb.Mesh, Dict, DetailCounts, Dict]:
    rng = np.random.default_rng(seed + 2203)
    nodes: List[np.ndarray] = [np.zeros(3, dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.060]
    parent = 0
    for level in range(1, 14):
        theta = level * 0.72
        main_dir = np.array([math.cos(theta) * 0.26, math.sin(theta) * 0.26, 0.42])
        current = _append_child(nodes, parents, radii, parent, main_dir, 1.0, max(0.055 * (0.88**level), 0.008))
        for sign in (-1, 1):
            side = _unit(np.array([math.cos(theta + sign * 1.26), math.sin(theta + sign * 1.26), 0.10]))
            tendril = _append_child(nodes, parents, radii, current, side + rng.normal(0.0, 0.035, 3), 0.26 + 0.010 * level, 0.009)
            curl_parent = tendril
            for curl in range(2):
                curl_parent = _append_child(
                    nodes,
                    parents,
                    radii,
                    curl_parent,
                    side * (0.58 - 0.12 * curl) + np.array([0.0, 0.0, 0.20]) + rng.normal(0.0, 0.09, 3),
                    0.105 + 0.011 * curl,
                    0.005,
                )
        parent = current
    nodes = _normalize_nodes(nodes, 2.52)
    edges = _graph_edges(parents)
    mesh = _smooth_support_mesh(nodes, edges, radii, sides=12, ovality=0.22)
    counts = _merge_counts(
        _scatter_leaves(mesh, nodes, parents, rng, count=96, scale=(0.055, 0.118)),
        _scatter_tendrils(mesh, nodes, parents, rng, count=70),
    )
    controls = _finalize_controls(
        {
            "source": "hand-authored L-system vine equivalent to baseline_matrix_20260509.lsystem_case(vine)",
            "recursive_depth": 6,
            "iterations": 6,
            "target_silhouette": "climbing vine",
            "grammar_rule": "F -> F curl(F) leaf(F) with recursive tendril side branches",
        },
        nodes,
        edges,
        counts,
    )
    grammar = {
        "grammar_family": "L-system",
        "grammar_symbols": "F,+,-,[,],curl,tendril,leaf",
        "target_symbol": "F",
        "operator_to_traditional_mapping": {
            "F": "extend the climbing main vine",
            "curl": "rotate recursive side growth around the support axis",
            "tendril": "create smooth curling attachment organs",
            "leaf": "attach small curved leaf blades before mesh export",
        },
        "remote_comparison_unit": "one generated OBJ input to one traditional target",
    }
    return mesh, controls, counts, grammar


def _build_space_colonization(
    sc_case: str,
    seed: int,
    mode: str,
    attractor_count: int,
    iterations: int,
    influence_radius: float,
    kill_radius: float,
    step_size: float,
    dense_variant: bool = False,
) -> Tuple[pb.Mesh, Dict, DetailCounts, Dict]:
    rng = np.random.default_rng(seed + 2204)
    result = scb.grow_space_colonization(
        case=sc_case,
        attractor_count=attractor_count,
        iterations=iterations,
        influence_radius=influence_radius,
        kill_radius=kill_radius,
        step_size=step_size,
        seed=seed,
    )
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in result["nodes"]], 2.58)
    parents = [int(p) for p in result["parents"]]
    radii = _radii_from_parents(parents, base=0.080 if mode != "root" else 0.082, taper=0.82, floor=0.0055)
    edges = _graph_edges(parents)
    mesh = _smooth_support_mesh(nodes, edges, radii, sides=12, ovality=0.22 if mode == "root" else 0.17)
    if mode == "root":
        counts = _scatter_rootlets(mesh, nodes, parents, rng, count=220 if dense_variant else 174, downward=0.66)
    elif sc_case == "bush_shell":
        counts = _merge_counts(
            _scatter_leaves(mesh, nodes, parents, rng, count=180, scale=(0.050, 0.110)),
            _scatter_needles(mesh, nodes, parents, rng, count=28, length_range=(0.042, 0.086)),
        )
    else:
        counts = _merge_counts(
            _scatter_needles(mesh, nodes, parents, rng, count=130, length_range=(0.052, 0.112)),
            _scatter_leaves(mesh, nodes, parents, rng, count=52, scale=(0.052, 0.104)),
        )
    controls = _finalize_controls(
        {
            "source": "space_colonization_baseline.grow_space_colonization",
            "case": sc_case,
            "semantic_mode": mode,
            "recursive_depth": int(max(result.get("depths", [0])) if result.get("depths") else 0),
            "target_silhouette": "attractor-driven crown/root/bush shell",
            "attractor_count": int(attractor_count),
            "iterations": int(iterations),
            "influence_radius": float(influence_radius),
            "kill_radius": float(kill_radius),
            "step_size": float(step_size),
            "covered_attractors": int(result.get("covered_attractors", 0)),
            "alive_attractors": int(result.get("alive_attractors", 0)),
            "parameter_sweep_variant": bool(dense_variant),
            "grammar_rule": "attractor vectors accumulate at nearest nodes; surviving nodes extend by the averaged direction field",
        },
        nodes,
        edges,
        counts,
    )
    grammar = {
        "grammar_family": "Space colonization",
        "grammar_symbols": "attractor_field,influence_radius,kill_radius,step_size,coverage_update",
        "target_symbol": "attractor",
        "operator_to_traditional_mapping": {
            "attractor_field": "defines the same target crown/root/shell volume",
            "influence_radius": "selects which attractors contribute to a growth node",
            "kill_radius": "removes covered attractors",
            "step_size": "advances a swept support node in the averaged direction",
        },
        "remote_comparison_unit": "one generated OBJ input to one traditional target",
    }
    return mesh, controls, counts, grammar


def _write_guides(out_dir: Path) -> Dict[str, str]:
    from PIL import Image, ImageDraw, ImageFilter

    guide_dir = out_dir / "_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)

    def stable_seed(name: str) -> int:
        return sum((i + 1) * b for i, b in enumerate(name.encode("utf-8"))) % (2**32)

    def save(name: str, bg: Tuple[int, int, int], colors: List[Tuple[int, int, int]], motif: str) -> str:
        img = Image.new("RGB", (768, 768), bg)
        draw = ImageDraw.Draw(img)
        rng = np.random.default_rng(stable_seed(name))
        for _ in range(960):
            c = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(28, 740))
            y = int(rng.integers(28, 740))
            if motif == "root":
                draw.line((x, y, x + int(rng.normal(0, 88)), y + int(rng.normal(52, 44))), fill=c, width=int(rng.integers(1, 5)))
                if rng.random() < 0.34:
                    draw.line((x, y, x + int(rng.normal(42, 30)), y + int(rng.normal(18, 26))), fill=c, width=1)
            elif motif == "vine":
                r = int(rng.integers(14, 58))
                draw.arc((x - r, y - r, x + r, y + r), int(rng.integers(0, 80)), int(rng.integers(210, 360)), fill=c, width=int(rng.integers(2, 5)))
                if rng.random() < 0.42:
                    draw.ellipse((x - r // 3, y - r // 6, x + r // 2, y + r // 4), outline=c, width=2)
            elif motif == "bush":
                r = int(rng.integers(4, 16))
                draw.ellipse((x - r, y - r // 2, x + r, y + r // 2), fill=c)
            else:
                draw.line((x, y, x + int(rng.normal(0, 50)), y + int(rng.normal(-36, 32))), fill=c, width=int(rng.integers(1, 4)))
                if rng.random() < 0.42:
                    rr = int(rng.integers(3, 9))
                    draw.line((x - rr, y, x + rr, y), fill=c, width=1)
                    draw.line((x, y - rr, x, y + rr), fill=c, width=1)
        path = guide_dir / name
        img.filter(ImageFilter.SMOOTH_MORE).save(path)
        return str(path)

    return {
        "pine": save("V22_smooth_pine_needles_bark_pbr_guide.png", (18, 34, 24), [(36, 82, 43), (86, 124, 62), (126, 102, 62), (70, 45, 28)], "pine"),
        "root": save("V22_smooth_rootlets_soil_pbr_guide.png", (30, 22, 17), [(72, 49, 32), (126, 84, 48), (166, 119, 74), (22, 16, 12)], "root"),
        "vine": save("V22_smooth_vine_leaf_tendril_pbr_guide.png", (20, 45, 32), [(44, 96, 50), (98, 136, 68), (148, 116, 56), (52, 34, 24)], "vine"),
        "bush": save("V22_smooth_bush_shell_leaf_pbr_guide.png", (24, 42, 28), [(50, 102, 50), (104, 146, 76), (158, 138, 78), (82, 54, 32)], "bush"),
    }


def _case_specs(seed: int) -> List[Dict]:
    specs: List[Dict] = []

    def add(
        case_id: str,
        family: str,
        target: str,
        mode: str,
        mesh: pb.Mesh,
        controls: Dict,
        counts: DetailCounts,
        grammar: Dict,
        guide: str,
        why: str,
        gpu: int,
    ) -> None:
        specs.append(
            {
                "case_id": case_id,
                "family": family,
                "traditional_target": target,
                "match_target": target,
                "recursive_mode": mode,
                "mesh": mesh,
                "controls": controls,
                "counts": counts,
                "grammar_mapping": grammar,
                "guide_key": guide,
                "why_matches_traditional": why,
                "strict_match_notes": why,
                "gpu": int(gpu),
                "seed": int(seed + len(specs) + 220),
                "operators": list(COMMON_OPERATORS),
                "operator_composition": " -> ".join(COMMON_OPERATORS),
                "case_role": "priority_a100_2",
            }
        )

    mesh, controls, counts, grammar = _build_lsystem_pine(seed + 1, depth=5)
    add(
        "V22_lsys_pine_canopy_d5_smooth_needles",
        "L-system",
        "lsys_pine_canopy_d5",
        "symbolic turtle branch rewriting, depth 5, pine canopy",
        mesh,
        controls,
        counts,
        grammar,
        "pine",
        "Same depth-5 tree L-system target; V22 keeps the branch grammar and adds smooth swept pine needles and leaf-scale detail before OBJ export.",
        4,
    )

    mesh, controls, counts, grammar = _build_lsystem_root(seed + 2, depth=5)
    add(
        "V22_lsys_root_fan_d5_smooth_rootlets",
        "L-system",
        "lsys_root_fan_d5",
        "symbolic turtle root branching with downward tropism, depth 5",
        mesh,
        controls,
        counts,
        grammar,
        "root",
        "Same depth-5 root fan grammar; V22 uses smooth swept roots and many attached rootlets rather than blocky or stamped substitutes.",
        5,
    )

    mesh, controls, counts, grammar = _build_lsystem_vine(seed + 3)
    add(
        "V22_lsys_climbing_vine_d6_smooth_leaf_tendrils",
        "L-system",
        "lsys_climbing_vine_d6",
        "curling main chain with recursive tendrils, six iterations",
        mesh,
        controls,
        counts,
        grammar,
        "vine",
        "Same six-iteration climbing vine comparison; V22 represents tendrils and leaves as connected curved geometry before mesh export.",
        6,
    )

    mesh, controls, counts, grammar = _build_space_colonization("tree_canopy", seed + 11, "tree", 900, 260, 0.220, 0.052, 0.041)
    add(
        "V22_sc_tree_crown_260_smooth_needled_crown",
        "Space colonization",
        "sc_tree_crown_260",
        "tree crown attractor competition with influence/kill radii",
        mesh,
        controls,
        counts,
        grammar,
        "pine",
        "Same SC tree-crown attractor target; V22 preserves attractor competition and adds connected fine canopy semantics.",
        7,
    )

    mesh, controls, counts, grammar = _build_space_colonization("root_vine", seed + 12, "root", 980, 260, 0.220, 0.052, 0.041)
    add(
        "V22_sc_root_network_260_smooth_rootlet_web",
        "Space colonization",
        "sc_root_network_260",
        "root/vine attractor competition in below-ground volume",
        mesh,
        controls,
        counts,
        grammar,
        "root",
        "Same SC root-network attractor field; V22 keeps the web target and grows attached smooth rootlets from support anchors.",
        4,
    )

    mesh, controls, counts, grammar = _build_space_colonization("bush_shell", seed + 13, "tree", 850, 220, 0.235, 0.060, 0.040)
    add(
        "V22_sc_bush_shell_220_smooth_leaf_shell",
        "Space colonization",
        "sc_bush_shell_220",
        "bush-shell attractor competition with outward terminal coverage",
        mesh,
        controls,
        counts,
        grammar,
        "bush",
        "Same SC bush-shell coverage target; V22 keeps the shell and attaches curved leaf-scale detail to the connected support.",
        5,
    )

    mesh, controls, counts, grammar = _build_lsystem_pine(seed + 21, depth=6)
    add(
        "V22_lsys_pine_canopy_depth_sweep_d6_smooth_needles",
        "L-system",
        "lsys_pine_canopy_depth_sweep_d6",
        "depth sweep variant of the symbolic pine/tree L-system",
        mesh,
        controls,
        counts,
        grammar,
        "pine",
        "Depth-sweep variant of the same pine L-system target; only grammar depth changes while smooth support and semantic detail policy stay fixed.",
        6,
    )

    mesh, controls, counts, grammar = _build_space_colonization("root_vine", seed + 22, "root", 1250, 320, 0.205, 0.044, 0.036, dense_variant=True)
    add(
        "V22_sc_root_network_parameter_sweep_dense_smooth_rootlets",
        "Space colonization",
        "sc_root_network_parameter_sweep_dense",
        "dense parameter sweep of root-network attractor competition",
        mesh,
        controls,
        counts,
        grammar,
        "root",
        "Parameter-sweep variant of the same SC root-network target; smaller kill radius and denser attractors create a finer connected root web.",
        7,
    )
    return specs


def _export_mesh(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


def _mesh_stats(path: Path, controls: Dict) -> Dict:
    vertices, faces = rgm.parse_obj(path)
    comp = rgm.component_stats(vertices, faces)
    bbox = rgm.bbox_stats(vertices)
    surface_area = 0.0
    if len(vertices) and len(faces):
        tri = vertices[faces]
        surface_area = float(np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1).sum() * 0.5)
    return {
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
        "mesh_component_count": int(comp["component_count"]),
        "largest_mesh_component_vertex_ratio": float(comp["largest_component_vertex_ratio"]),
        "bbox_extent": [float(bbox["bbox_extent_x"]), float(bbox["bbox_extent_y"]), float(bbox["bbox_extent_z"])],
        "bbox_diag": float(bbox["bbox_diag"]),
        "surface_area": surface_area,
        "semantic_detail_count": int(controls.get("semantic_detail_count", 0)),
        "needle_count": int(controls.get("needle_count", 0)),
        "leaf_count": int(controls.get("leaf_count", 0)),
        "rootlet_count": int(controls.get("rootlet_count", 0)),
        "tendril_count": int(controls.get("tendril_count", 0)),
        "support_edge_count": int(controls.get("support_edge_count", 0)),
        "low_poly_block_stamping": bool(controls.get("low_poly_block_stamping", False)),
        "mesh_token_stamping": bool(controls.get("mesh_token_stamping", False)),
    }


def _metadata_for(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    controls = spec["controls"]
    positive = "smooth swept botanical/root support with visible leaf, needle, tendril, and rootlet semantics before OBJ export"
    return {
        "case_id": spec["case_id"],
        "family": spec["family"],
        "match_target": spec["match_target"],
        "traditional_target": spec["traditional_target"],
        "traditional_alignment": {
            "traditional_target": spec["traditional_target"],
            "same_category": True,
            "same_recursive_mode": spec["recursive_mode"],
            "strict_one_to_one_comparison": True,
            "control_parameters": controls,
            "why_strict_one_to_one": spec["why_matches_traditional"],
        },
        "grammar_mapping": spec["grammar_mapping"],
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
        "controls": controls,
        "semantic_detail_breakdown": {
            "needle_count": int(controls.get("needle_count", 0)),
            "leaf_count": int(controls.get("leaf_count", 0)),
            "rootlet_count": int(controls.get("rootlet_count", 0)),
            "tendril_count": int(controls.get("tendril_count", 0)),
            "total": int(controls.get("semantic_detail_count", 0)),
        },
        "initial_mesh_metrics": metrics,
        "why_matches_traditional": spec["why_matches_traditional"],
        "strict_match_notes": spec["strict_match_notes"],
        "case_role": spec["case_role"],
        "strict_generation_policy": "generate_new_on_a100_2_no_local_selection_or_postprocessing",
        "mesh_pbr_contract": {
            "input_mesh_format": "obj",
            "obj_mesh_inputs_only": True,
            "pbr_guide_required": True,
            "pbr_textured_glb_required": True,
            "mesh_outputs_only": True,
            "forbidden_outputs": [
                "local_selected_render",
                "2d_only_image",
                "posthoc_repair_mesh",
                "non_obj_mesh_input",
                "low_poly_block_stamp",
                "mesh_token_stamp",
            ],
        },
        "root_selection_log": {
            "root_source_type": "V22_strict_smooth_botanical_input_generator",
            "source_generator": "assets/strict_visual_matched_cases_V22_botanical_smooth_20260510.py",
            "root_screening_budget": "no local manual cherry-pick and no posthoc repair selection; final outputs generated fresh on a100-2",
        },
        "visual_readability_contract": {
            "dryrun_visual_floor": "OBJ mesh must pass largest-component vertex ratio >= 0.999 before Trellis2",
            "positive_constraint": positive,
            "negative_constraint": "no low-poly block surfaces, no token stamping, no detached semantic islands, no local selected result substitution",
            "failure_addressed": "V17 relied on procedural rod/card simplifications; V19 improved source quality with mesh tokens but still used token stamping. V22 makes the visible semantics as smooth attached geometry.",
            "no_local_selection": "strict cases must be generated fresh on a100-2; local dry-run files are inputs, not selected final outputs",
        },
    }


def _write_readme(out_dir: Path, summary: Dict) -> None:
    text = """# V22 Smooth Botanical Strict Visual-Matched Cases Dry Run

Produced by `assets/strict_visual_matched_cases_V22_botanical_smooth_20260510.py`.

This is an input batch only. It does not launch remote jobs, locally select
outputs, or post-process prior assets. Final strict one-to-one cases must be
generated fresh on `{remote}` with GPU ids `{gpus}` under:

`{storage}`

Connectivity gate: largest-component vertex ratio >= `{lcr}` before Trellis2.
Mesh policy: OBJ inputs plus PBR guide images only.

Case count: {count}
""".format(
        remote=REMOTE_TARGET,
        gpus=ALLOWED_GPUS,
        storage=REMOTE_STORAGE_ROOT,
        lcr=CONNECTIVITY_LCR_MIN,
        count=summary["num_cases"],
    )
    (out_dir / "README.md").write_text(text, encoding="utf-8")


def materialize(root: Path, out_dir: Path, seed: int = 20260510, case_limit: Optional[int] = None) -> Dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    guides = _write_guides(out_dir)
    specs = _case_specs(seed)
    if case_limit is not None:
        specs = specs[: int(case_limit)]

    rows: List[Dict] = []
    metrics_rows: List[Dict] = []
    for spec in specs:
        case_dir = out_dir / spec["case_id"]
        mesh_path = case_dir / ("%s.obj" % spec["case_id"])
        _export_mesh(mesh_path, spec["mesh"])
        guide_path = guides[spec["guide_key"]]
        metrics = _mesh_stats(mesh_path, spec["controls"])
        if metrics["largest_mesh_component_vertex_ratio"] < CONNECTIVITY_LCR_MIN:
            raise RuntimeError("%s failed V22 connectivity gate: %s" % (spec["case_id"], metrics))
        metadata = _metadata_for(spec, mesh_path, guide_path, metrics)
        metadata_path = case_dir / ("%s_metadata.json" % spec["case_id"])
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
            "gpu_group": int(spec["gpu"]),
            "seed": int(spec["seed"]),
            "operators": json.dumps(spec["operators"], ensure_ascii=False),
            "operator_composition": spec["operator_composition"],
            "controls": json.dumps(spec["controls"], ensure_ascii=False, sort_keys=True),
            "why_matches_traditional": spec["why_matches_traditional"],
            "strict_match_notes": spec["strict_match_notes"],
            "case_role": spec["case_role"],
            "strict_one_to_one": "true",
            "generation_policy": "generate_new_on_a100_2_no_local_selection_or_postprocessing",
            "mesh_input_policy": "obj_mesh_inputs_only",
            "surface_strategy": SURFACE_STRATEGY,
            "block_or_token_stamping": "false",
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
        "mesh_input_policy",
        "surface_strategy",
        "block_or_token_stamping",
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
        "semantic_detail_count",
        "needle_count",
        "leaf_count",
        "rootlet_count",
        "tendril_count",
        "support_edge_count",
        "low_poly_block_stamping",
        "mesh_token_stamping",
    ]
    with (out_dir / "initial_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        writer.writerows(metrics_rows)
    (out_dir / "initial_metrics.json").write_text(json.dumps(metrics_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    case_lines = ["%s|%s|%s|%s|%s" % (row["case_id"], row["mesh_path"], row["guide_image"], row["seed"], row["gpu_group"]) for row in rows]
    (out_dir / "a100-2_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    (out_dir / "gpu4567_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    for gpu in ALLOWED_GPUS:
        selected = [line for line, row in zip(case_lines, rows) if int(row["gpu_group"]) == gpu]
        (out_dir / ("gpu%s_cases.txt" % gpu)).write_text("\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")

    summary = {
        "out_dir": str(out_dir),
        "num_cases": len(rows),
        "remote_target": REMOTE_TARGET,
        "allowed_gpus": ALLOWED_GPUS,
        "storage_root": REMOTE_STORAGE_ROOT,
        "storage_limit_gb": STORAGE_LIMIT_GB,
        "surface_generator": "strict_lsystem_space_colonization_smooth_botanical_v22",
        "mesh_input_policy": "obj_mesh_inputs_only",
        "mesh_pbr_policy": "obj_inputs_and_pbr_guides_for_trellis2_glb_export",
        "v22_fix_focus": "smooth connected botanical semantics without low_poly_block_or_token_stamping",
        "connectivity_gate": {
            "largest_component_vertex_ratio_min": CONNECTIVITY_LCR_MIN,
            "pre_trellis_required": True,
        },
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
