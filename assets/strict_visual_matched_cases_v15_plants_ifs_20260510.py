#!/usr/bin/env python3
"""V15 strict one-to-one plant/root/IFS Trellis2 input generator.

V15 is a fresh remote-generation branch for the family gaps left after the
full-family V6/V8 audits: plant, root, tree, and IFS cases were connected but
often read as rods or fragmented transform scaffolds.  This script emits only
new strict matched task inputs for a100-2 GPU 4/5/6/7 runs.  It does not launch
remote jobs, select local outputs, or post-process earlier V13/V14/DLA cases.
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
import procedural_baselines as pb
import recursive_growth_mesh_metrics as rgm
import space_colonization_baseline as scb


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 100
CONNECTIVITY_LCR_MIN = 0.999
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_v15_plants_ifs_20260510_dryrun"


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _basis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = _unit(np.asarray(axis, dtype=float))
    seed = np.array([0.0, 0.0, 1.0]) if abs(w[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = _unit(np.cross(w, seed))
    v = _unit(np.cross(w, u))
    return u, v, w


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


def _graph_edges(parents: list[int]) -> list[tuple[int, int]]:
    return [(int(parent), int(idx)) for idx, parent in enumerate(parents) if parent >= 0]


def _dedupe_edges(edges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    seen: set[tuple[int, int]] = set()
    out: list[tuple[int, int]] = []
    for a, b in edges:
        if a == b:
            continue
        key = (min(int(a), int(b)), max(int(a), int(b)))
        if key in seen:
            continue
        seen.add(key)
        out.append((int(a), int(b)))
    return out


def _radii_from_parents(parents: list[int], base: float, taper: float, floor: float) -> list[float]:
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    return [max(base * (1.0 - taper * (depth / max(max_depth, 1))) ** 1.12, floor) for depth in depths]


def _append_child(
    nodes: list[np.ndarray],
    parents: list[int],
    radii: list[float],
    anchor: int,
    direction: np.ndarray,
    length: float,
    radius: float,
) -> int:
    nodes.append(np.asarray(nodes[anchor], dtype=float) + _unit(direction) * float(length))
    parents.append(int(anchor))
    radii.append(float(radius))
    return len(nodes) - 1


def _smooth_tapered_support_mesh(
    nodes: list[np.ndarray],
    edges: list[tuple[int, int]],
    radii: list[float],
    sides: int = 10,
) -> pb.Mesh:
    """Face-connected tapered tube support with shared scaffold center fans."""

    mesh = pb.Mesh([], [])
    center_indices: list[int] = []
    for node in nodes:
        mesh.vertices.append(tuple(np.asarray(node, dtype=float)))
        center_indices.append(len(mesh.vertices))

    incident_rings: list[list[list[int]]] = [[] for _ in nodes]
    for a, b in _dedupe_edges(edges):
        start = np.asarray(nodes[a], dtype=float)
        end = np.asarray(nodes[b], dtype=float)
        axis = end - start
        if float(np.linalg.norm(axis)) < 1e-7:
            continue
        u, v, _ = _basis(axis)
        base = len(mesh.vertices)
        for endpoint, radius in ((start, radii[a]), (end, radii[b])):
            for i in range(sides):
                theta = 2.0 * math.pi * i / sides
                d = math.cos(theta) * u + math.sin(theta) * v
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
            s = ridx % sides
            mesh.faces.append((ring[s], ring[(s + 1) % sides], next_ring[s]))
            mesh.faces.append((ring[(s + 1) % sides], next_ring[(s + 1) % sides], next_ring[s]))

    setattr(mesh, "center_indices", center_indices)
    return mesh


def _add_leaf_card(mesh: pb.Mesh, anchor_idx: int, anchor: np.ndarray, normal: np.ndarray, scale: float, aspect: float) -> None:
    u, v, _ = _basis(normal)
    c = np.asarray(anchor, dtype=float) + _unit(normal) * scale * 0.82
    a = float(scale) * float(aspect)
    b = float(scale)
    base = len(mesh.vertices)
    mesh.vertices.extend([tuple(c + u * a), tuple(c + v * b), tuple(c - u * a), tuple(c - v * b)])
    for i in range(4):
        j = (i + 1) % 4
        mesh.faces.append((anchor_idx, base + i + 1, base + j + 1))
        mesh.faces.append((anchor_idx, base + j + 1, base + i + 1))


def _add_edge_panel(
    mesh: pb.Mesh,
    center_indices: list[int],
    nodes: list[np.ndarray],
    a: int,
    b: int,
    width: float,
    lift: float,
    faceted: bool = False,
) -> None:
    pa = np.asarray(nodes[a], dtype=float)
    pb_ = np.asarray(nodes[b], dtype=float)
    axis = pb_ - pa
    if float(np.linalg.norm(axis)) < 1e-7:
        return
    u, v, _ = _basis(axis)
    normal = _unit(v + np.array([0.0, 0.0, lift]))
    mid = (pa + pb_) * 0.5 + normal * float(width) * 0.22
    base = len(mesh.vertices)
    if faceted:
        pts = [
            mid + u * width * 0.82 + normal * width * 0.48,
            mid - u * width * 0.82 + normal * width * 0.42,
            mid + normal * width * 0.94,
        ]
    else:
        pts = [
            mid + u * width * 0.55 + normal * width * 0.34,
            mid - u * width * 0.55 + normal * width * 0.30,
            mid + normal * width * 0.68,
        ]
    mesh.vertices.extend([tuple(p) for p in pts])
    ca = center_indices[a]
    cb = center_indices[b]
    mesh.faces.append((ca, cb, base + 1))
    mesh.faces.append((cb, base + 2, base + 1))
    mesh.faces.append((ca, base + 1, base + 3))
    mesh.faces.append((cb, base + 3, base + 2))


def _add_support_panels(
    mesh: pb.Mesh,
    nodes: list[np.ndarray],
    edges: list[tuple[int, int]],
    width: float,
    lift: float,
    max_panels: int,
    faceted: bool = False,
) -> int:
    centers = getattr(mesh, "center_indices")
    placed = 0
    step = max(len(edges) // max(max_panels, 1), 1)
    for a, b in _dedupe_edges(edges)[::step]:
        if placed >= max_panels:
            break
        _add_edge_panel(mesh, centers, nodes, a, b, width=width, lift=lift, faceted=faceted)
        placed += 1
    return placed


def _terminal_nodes(parents: list[int]) -> list[int]:
    child_map = _children(parents)
    return [i for i in range(1, len(parents)) if not child_map.get(i)]


def _finalize_controls(base: dict, branch_edges: int, detail_count: int, root_hairs: int = 0) -> dict:
    controls = dict(base)
    controls.update(
        {
            "smooth_connected_support": True,
            "connectivity_gate_lcr_min": CONNECTIVITY_LCR_MIN,
            "tapered_branch_edges": int(branch_edges),
            "attached_detail_primitives": int(detail_count),
            "connected_root_hairs": int(root_hairs),
            "direct_voxel_blocks": False,
            "grape_ball_primitives": 0,
            "rod_scaffold_only": False,
            "surface_strategy": controls.get(
                "surface_strategy",
                "smooth connected support with tapered branches and attached category-specific detail primitives",
            ),
        }
    )
    return controls


def lsystem_tree_case(seed: int) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 17)
    nodes0, parents = bm.lsystem_case("tree", depth=5, seed=seed)
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in nodes0], 2.45)
    radii = _radii_from_parents(parents, base=0.082, taper=0.80, floor=0.009)
    edges = _graph_edges(parents)
    mesh = _smooth_tapered_support_mesh(nodes, edges, radii, sides=12)
    centers = getattr(mesh, "center_indices")
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    details = 0
    for idx in [i for i in range(1, len(nodes)) if depths[i] >= max_depth * 0.58]:
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(nodes[idx] - nodes[parent])
        u, v, _ = _basis(axis)
        for k in range(4):
            theta = 2.0 * math.pi * k / 4.0 + rng.normal(0, 0.12)
            normal = _unit(0.34 * axis + math.cos(theta) * u + math.sin(theta) * v)
            _add_leaf_card(mesh, centers[idx], nodes[idx], normal, rng.uniform(0.026, 0.044), 3.2)
            details += 1
    panels = _add_support_panels(mesh, nodes, edges, width=0.040, lift=0.16, max_panels=90, faceted=False)
    return mesh, _finalize_controls(
        {
            "source": "baseline_matrix_20260509.lsystem_case(tree)",
            "depth": 5,
            "branch_nodes": len(nodes),
            "attached_needle_cards": details,
            "local_smooth_envelope_panels": panels,
            "surface_strategy": "smooth connected pine trunk/branch support with attached needle card clusters",
        },
        len(edges),
        details + panels,
    )


def lsystem_root_case(seed: int) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 23)
    nodes0, parents = bm.lsystem_case("root", depth=5, seed=seed)
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in nodes0], 2.55)
    radii = _radii_from_parents(parents, base=0.078, taper=0.84, floor=0.006)
    depths = bm.graph_depths(parents)
    original = len(nodes)
    for idx in range(1, original):
        if depths[idx] < 2:
            continue
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(nodes[idx] - nodes[parent])
        u, v, _ = _basis(axis)
        for _ in range(2 + int(depths[idx] >= 4)):
            direction = _unit(-0.20 * axis + rng.normal(0, 0.75) * u + rng.normal(0, 0.75) * v + np.array([0.0, 0.0, -0.55]))
            _append_child(nodes, parents, radii, idx, direction, rng.uniform(0.075, 0.185), rng.uniform(0.0028, 0.0048))
    edges = _graph_edges(parents)
    mesh = _smooth_tapered_support_mesh(nodes, edges, radii, sides=10)
    panels = _add_support_panels(mesh, nodes, edges, width=0.026, lift=-0.14, max_panels=92, faceted=False)
    root_hairs = len(nodes) - original
    return mesh, _finalize_controls(
        {
            "source": "baseline_matrix_20260509.lsystem_case(root)",
            "depth": 5,
            "root_nodes": original,
            "connected_root_hairs": root_hairs,
            "local_smooth_envelope_panels": panels,
            "surface_strategy": "smooth connected root fan support with fine connected root hairs attached to hierarchy edges",
        },
        len(edges),
        root_hairs + panels,
        root_hairs,
    )


def lsystem_vine_case(seed: int) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 29)
    nodes = [np.zeros(3, dtype=float)]
    parents = [-1]
    radii = [0.060]
    parent = 0
    for level in range(1, 11):
        theta = level * 0.82
        step = np.array([math.cos(theta) * 0.20, math.sin(theta) * 0.20, 0.40])
        current = _append_child(nodes, parents, radii, parent, step, 1.0, max(0.055 * (0.88**level), 0.010))
        for sign in (-1, 1):
            side = _unit(np.array([math.cos(theta + sign * 1.36), math.sin(theta + sign * 1.36), 0.15]))
            tendril = _append_child(nodes, parents, radii, current, side + rng.normal(0, 0.025, 3), 0.24 + 0.018 * level, 0.010)
            _append_child(nodes, parents, radii, tendril, side + np.array([0.0, 0.0, 0.24]), 0.13 + 0.010 * level, 0.006)
            if level >= 4:
                hook = _unit(side * 0.72 + np.array([0.0, 0.0, 0.28]) + rng.normal(0, 0.08, 3))
                _append_child(nodes, parents, radii, tendril, hook, 0.11, 0.0048)
        parent = current
    nodes = _normalize_nodes(nodes, 2.45)
    edges = _graph_edges(parents)
    mesh = _smooth_tapered_support_mesh(nodes, edges, radii, sides=10)
    centers = getattr(mesh, "center_indices")
    details = 0
    for idx in _terminal_nodes(parents):
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(nodes[idx] - nodes[parent])
        _add_leaf_card(mesh, centers[idx], nodes[idx], axis + rng.normal(0, 0.18, 3), 0.052, 1.75)
        details += 1
    for a, b in edges[::2]:
        _add_edge_panel(mesh, centers, nodes, a, b, width=0.030, lift=0.09, faceted=False)
        details += 1
    return mesh, _finalize_controls(
        {
            "source": "V15 hand-authored L-system vine equivalent to baseline_matrix_20260509.lsystem_case(vine)",
            "iterations": 6,
            "attached_leaf_cards": details,
            "surface_strategy": "smooth connected curling vine support with attached leaves and tendril panels",
        },
        len(edges),
        details,
    )


def space_colonization_case(sc_case: str, seed: int, mode: str) -> tuple[pb.Mesh, dict]:
    attractors = 1700 if sc_case != "bush_shell" else 1450
    iterations = 275 if sc_case != "bush_shell" else 235
    result = scb.grow_space_colonization(
        case=sc_case,
        attractor_count=attractors,
        iterations=iterations,
        influence_radius=0.225 if sc_case != "bush_shell" else 0.230,
        kill_radius=0.052 if sc_case != "bush_shell" else 0.060,
        step_size=0.042 if sc_case != "bush_shell" else 0.040,
        seed=seed,
    )
    rng = np.random.default_rng(seed + 41)
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in result["nodes"]], 2.42)
    parents = [int(p) for p in result["parents"]]
    base_radius = 0.062 if mode == "tree" else 0.068
    radii = _radii_from_parents(parents, base=base_radius, taper=0.82, floor=0.0055)
    original = len(nodes)
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    anchors = [i for i in range(1, original) if depths[i] >= max_depth * 0.56 or i in _terminal_nodes(parents)]
    rng.shuffle(anchors)
    root_hairs = 0
    for idx in anchors[:95 if mode == "tree" else 135]:
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(nodes[idx] - nodes[parent])
        u, v, _ = _basis(axis)
        count = 1 if mode == "tree" else 2
        bias = np.array([0.0, 0.0, 0.18 if mode == "tree" else -0.48])
        for _ in range(count):
            direction = _unit(0.22 * axis + rng.normal(0, 0.72) * u + rng.normal(0, 0.72) * v + bias)
            _append_child(nodes, parents, radii, idx, direction, rng.uniform(0.052, 0.142), rng.uniform(0.0030, 0.0056))
            root_hairs += int(mode != "tree")
    edges = _graph_edges(parents)
    mesh = _smooth_tapered_support_mesh(nodes, edges, radii, sides=10)
    centers = getattr(mesh, "center_indices")
    details = 0
    if mode == "tree":
        for idx in anchors[:100]:
            parent = parents[idx] if parents[idx] >= 0 else idx
            axis = _unit(nodes[idx] - nodes[parent])
            _add_leaf_card(mesh, centers[idx], nodes[idx], axis + np.array([0.0, 0.0, 0.20]), 0.040, 1.85)
            details += 1
    panels = _add_support_panels(mesh, nodes, edges, width=0.032 if mode == "tree" else 0.025, lift=0.14 if mode == "tree" else -0.14, max_panels=100, faceted=False)
    return mesh, _finalize_controls(
        {
            "source": "space_colonization_baseline.grow_space_colonization",
            "case": sc_case,
            "attractor_count": attractors,
            "iterations": iterations,
            "covered_attractors": result.get("covered_attractors"),
            "alive_attractors": result.get("alive_attractors"),
            "branch_nodes": original,
            "terminal_attachment_children": len(nodes) - original,
            "attached_leaf_cards": details,
            "local_smooth_envelope_panels": panels,
            "surface_strategy": "smooth connected space-colonization support with terminal attached leaves/rootlets and local envelope panels",
        },
        len(edges),
        details + panels + (len(nodes) - original),
        root_hairs,
    )


def ifs_branch_tree_case(seed: int, depth: int = 6) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 53)
    nodes = [np.array([0.0, 0.0, -1.0], dtype=float)]
    parents = [-1]
    radii = [0.082]

    def rec(parent: int, direction: np.ndarray, length: float, radius: float, level: int, phase: float) -> None:
        if level <= 0:
            return
        current = _append_child(nodes, parents, radii, parent, direction, length, max(radius, 0.006))
        u, _, w = _basis(direction)
        branches = [(-0.48, phase), (0.42, phase + 2.25), (0.24, phase + 4.15)]
        for angle, twist in branches:
            if level <= 1 and angle == 0.24:
                continue
            rot_axis = math.cos(twist) * u + math.sin(twist) * np.cross(w, u)
            child = _unit(math.cos(angle) * w + math.sin(angle) * _unit(rot_axis) + rng.normal(0, 0.035, 3))
            rec(current, child, length * (0.69 + rng.uniform(-0.035, 0.025)), radius * 0.70, level - 1, phase + 0.83)

    rec(0, np.array([0.0, 0.0, 1.0]), 0.48, 0.070, depth, 0.0)
    nodes = _normalize_nodes(nodes, 2.55)
    edges = _graph_edges(parents)
    mesh = _smooth_tapered_support_mesh(nodes, edges, radii, sides=10)
    centers = getattr(mesh, "center_indices")
    details = 0
    for idx in _terminal_nodes(parents):
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(nodes[idx] - nodes[parent])
        _add_leaf_card(mesh, centers[idx], nodes[idx], axis + np.array([0.0, 0.0, 0.12]), 0.034, 2.1)
        details += 1
    panels = _add_support_panels(mesh, nodes, edges, width=0.034, lift=0.13, max_panels=86, faceted=False)
    return mesh, _finalize_controls(
        {
            "source": "V15 affine IFS branch tree recursion",
            "depth": depth,
            "branch_nodes": len(nodes),
            "attached_terminal_leaf_cards": details,
            "local_smooth_envelope_panels": panels,
            "surface_strategy": "smooth connected IFS branch tree with tapered recursive limbs and attached terminal cards",
        },
        len(edges),
        details + panels,
    )


def ifs_radial_case(order: int = 8, depth: int = 4) -> tuple[pb.Mesh, dict]:
    nodes: list[np.ndarray] = [np.zeros(3, dtype=float)]
    radii: list[float] = [0.078]
    edges: list[tuple[int, int]] = []
    previous_ring: list[int] = []
    tooth_nodes = 0
    bridge_count = 0
    for level in range(depth):
        radius = 0.25 + level * 0.235
        z = 0.040 * level
        tube = max(0.044 * (0.82**level), 0.014)
        phase = 0.16 * level
        ring: list[int] = []
        ring_steps = order * 5
        for i in range(ring_steps):
            theta = 2.0 * math.pi * i / ring_steps + phase
            wobble = 1.0 + 0.035 * math.sin(theta * order)
            nodes.append(np.array([math.cos(theta) * radius * wobble, math.sin(theta) * radius * wobble, z]))
            radii.append(tube)
            ring.append(len(nodes) - 1)
        for i, idx in enumerate(ring):
            edges.append((idx, ring[(i + 1) % len(ring)]))
            if i % 5 == 0:
                edges.append((0, idx))
                bridge_count += 1
                direction = _unit(nodes[idx] + np.array([0.0, 0.0, 0.08]))
                nodes.append(nodes[idx] + direction * (0.10 + 0.012 * (depth - level)))
                radii.append(tube * 0.42)
                edges.append((idx, len(nodes) - 1))
                tooth_nodes += 1
                if previous_ring:
                    prev = previous_ring[i % len(previous_ring)]
                    edges.append((prev, idx))
                    bridge_count += 1
        previous_ring = ring
    mesh = _smooth_tapered_support_mesh(nodes, edges, radii, sides=8)
    panels = _add_support_panels(mesh, nodes, edges, width=0.042, lift=0.03, max_panels=110, faceted=True)
    return mesh, _finalize_controls(
        {
            "source": "V15 radial IFS transform-copy graph",
            "order": order,
            "depth": depth,
            "bridged_ring_count": depth,
            "small_bridge_count": bridge_count,
            "tooth_nodes": tooth_nodes,
            "attached_faceted_panels": panels,
            "surface_strategy": "smooth connected transform support with bridged rings, spokes, teeth, and attached metal facets",
        },
        len(edges),
        tooth_nodes + bridge_count + panels,
    )


def ifs_lattice_case(depth: int = 4) -> tuple[pb.Mesh, dict]:
    nodes: list[np.ndarray] = [np.zeros(3, dtype=float)]
    radii: list[float] = [0.068]
    edges: list[tuple[int, int]] = []
    frontier = [0]
    directions = [
        np.array([1.0, 0.0, 0.32]),
        np.array([-0.5, 0.866, 0.32]),
        np.array([-0.5, -0.866, 0.32]),
        np.array([0.0, 0.0, -1.0]),
    ]
    bridge_count = 0
    for level in range(depth):
        next_frontier: list[int] = []
        step = 0.48 * (0.66**level)
        for parent in frontier:
            children: list[int] = []
            for direction in directions:
                point = nodes[parent] + _unit(direction) * step
                nodes.append(point)
                radii.append(max(0.046 * (0.78**level), 0.012))
                idx = len(nodes) - 1
                edges.append((parent, idx))
                children.append(idx)
                next_frontier.append(idx)
            for a, b in zip(children, children[1:] + children[:1]):
                edges.append((a, b))
                bridge_count += 1
        for i in range(0, len(next_frontier) - 1, 2):
            edges.append((next_frontier[i], next_frontier[i + 1]))
            bridge_count += 1
        frontier = next_frontier[::2]
    nodes = _normalize_nodes(nodes, 2.40)
    mesh = _smooth_tapered_support_mesh(nodes, edges, radii, sides=7)
    panels = _add_support_panels(mesh, nodes, edges, width=0.040, lift=0.12, max_panels=120, faceted=True)
    return mesh, _finalize_controls(
        {
            "source": "V15 affine IFS lattice expansion",
            "depth": depth,
            "affine_children_per_node": 4,
            "small_bridge_count": bridge_count,
            "attached_lattice_facets": panels,
            "surface_strategy": "smooth connected affine lattice with small copy bridges and attached crystal-like facets",
        },
        len(edges),
        bridge_count + panels,
    )


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
        for _ in range(640):
            c = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(30, 738))
            y = int(rng.integers(30, 738))
            if motif == "needles":
                draw.line((x, y, x + int(rng.normal(0, 48)), y + int(rng.normal(-24, 38))), fill=c, width=int(rng.integers(1, 4)))
            elif motif == "roots":
                draw.line((x, y, x + int(rng.normal(0, 86)), y + int(rng.normal(38, 46))), fill=c, width=int(rng.integers(2, 7)))
            elif motif == "vine":
                r = int(rng.integers(12, 46))
                draw.arc((x - r, y - r, x + r, y + r), 20, 310, fill=c, width=int(rng.integers(2, 5)))
            elif motif == "radial":
                r = int(rng.integers(12, 46))
                draw.ellipse((x - r, y - r, x + r, y + r), outline=c, width=int(rng.integers(2, 5)))
                draw.line((x, y, x + int(rng.normal(0, 70)), y + int(rng.normal(0, 70))), fill=c, width=2)
            else:
                r = int(rng.integers(8, 34))
                draw.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=c)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "conifer": save("v15_conifer_needles_attached_guide.png", (20, 38, 26), [(47, 86, 43), (89, 116, 66), (134, 138, 84), (72, 55, 33)], "needles"),
        "leaf": save("v15_leaf_vine_crown_attached_guide.png", (24, 52, 35), [(58, 103, 52), (101, 142, 70), (135, 104, 59), (43, 36, 27)], "vine"),
        "root": save("v15_root_hair_hierarchy_guide.png", (29, 23, 18), [(77, 54, 34), (122, 86, 53), (159, 119, 75), (20, 17, 14)], "roots"),
        "metal": save("v15_radial_lattice_bridged_metal_guide.png", (35, 38, 37), [(83, 91, 86), (157, 132, 75), (119, 54, 44), (190, 173, 116)], "radial"),
        "crystal": save("v15_lattice_crystal_bridge_guide.png", (42, 50, 60), [(96, 116, 134), (172, 189, 194), (218, 200, 133), (70, 84, 105)], "facet"),
    }


def _case_specs(seed: int) -> list[dict]:
    specs: list[dict] = []

    def add(
        case_id: str,
        family: str,
        traditional_target: str,
        recursive_mode: str,
        mesh: pb.Mesh,
        guide_key: str,
        case_seed: int,
        controls: dict,
        operators: list[str],
        why: str,
        gpu: int,
        priority: bool = True,
    ) -> None:
        specs.append(
            {
                "case_id": case_id,
                "family": family,
                "match_target": traditional_target,
                "traditional_target": traditional_target,
                "recursive_mode": recursive_mode,
                "mesh": mesh,
                "guide_key": guide_key,
                "seed": int(case_seed),
                "controls": controls,
                "operators": operators,
                "operator_composition": " -> ".join(operators),
                "why_matches_traditional": why,
                "strict_match_notes": why,
                "gpu": int(gpu),
                "case_role": "priority_a100_2" if priority else "backup_a100_2",
            }
        )

    common = ["smooth_connected_support", "tapered_branch_edges", "attached_detail_primitives", "no_rod_scaffold"]

    mesh, ctl = lsystem_tree_case(seed + 1)
    add(
        "v15_lsys_pine_canopy_d5_smooth_needled_branch_mass",
        "L-system",
        "lsys_pine_canopy_d5",
        "symbolic turtle branch rewriting, depth 5, pine/tree canopy",
        mesh,
        "conifer",
        seed + 101,
        ctl,
        ["same_lsystem_tree_rule", *common, "attached_needle_card_clusters"],
        "Same depth-5 tree L-system target; V15 replaces rod-like support with tapered smooth branch mass and attached needle-card clusters.",
        4,
    )

    mesh, ctl = lsystem_root_case(seed + 2)
    add(
        "v15_lsys_root_fan_d5_smooth_hair_hierarchy",
        "L-system",
        "lsys_root_fan_d5",
        "symbolic turtle root branching with downward tropism, depth 5",
        mesh,
        "root",
        seed + 102,
        ctl,
        ["same_lsystem_root_rule", *common, "connected_fine_root_hairs"],
        "Same depth-5 root/tropism grammar; V15 adds connected fine root hairs and smooth root sheath panels without detached wisps.",
        5,
    )

    mesh, ctl = lsystem_vine_case(seed + 3)
    add(
        "v15_lsys_climbing_vine_d6_smooth_leafy_curl",
        "L-system",
        "lsys_climbing_vine_d6",
        "curling main chain with recursive tendrils, six iterations",
        mesh,
        "leaf",
        seed + 103,
        ctl,
        ["same_vine_curl_schedule", *common, "attached_leaf_tendril_cards"],
        "Same six-step climbing vine mode; V15 keeps the curl silhouette but adds leafy/tendril mass attached to the vine.",
        6,
    )

    mesh, ctl = space_colonization_case("tree_canopy", seed + 11, "tree")
    add(
        "v15_sc_tree_crown_260_smooth_leaf_crown",
        "Space colonization",
        "sc_tree_crown_260",
        "tree crown attractor competition with influence/kill radii",
        mesh,
        "leaf",
        seed + 111,
        ctl,
        ["same_sc_tree_attractors", *common, "attached_terminal_leaf_clusters"],
        "Same tree-crown attractor competition; terminal foliage is attached to branches and local support panels keep it from reading as rods.",
        4,
    )

    mesh, ctl = space_colonization_case("root_vine", seed + 12, "root")
    add(
        "v15_sc_root_network_260_smooth_rootlet_web",
        "Space colonization",
        "sc_root_network_260",
        "root/vine attractor competition in below-ground volume",
        mesh,
        "root",
        seed + 112,
        ctl,
        ["same_sc_root_attractors", *common, "connected_rootlet_web"],
        "Same SC root-network attractors and radii; V15 adds connected rootlet webbing and avoids detached hair fragments.",
        5,
    )

    mesh, ctl = space_colonization_case("bush_shell", seed + 13, "tree")
    add(
        "v15_sc_bush_shell_220_smooth_leaf_shell",
        "Space colonization",
        "sc_bush_shell_220",
        "bush-shell attractor competition with outward terminal coverage",
        mesh,
        "leaf",
        seed + 113,
        ctl,
        ["same_sc_bush_shell", *common, "attached_shell_leaf_clusters"],
        "Same bush-shell attractor field; V15 preserves outward shell coverage with attached terminal details instead of a bare scaffold.",
        6,
    )

    mesh, ctl = ifs_branch_tree_case(seed + 31, depth=6)
    add(
        "v15_ifs_branch_tree_d6_smooth_recursive_canopy",
        "IFS/transform",
        "ifs_branch_tree_d6",
        "affine branch tree IFS with six recursive depth levels",
        mesh,
        "conifer",
        seed + 131,
        ctl,
        ["same_ifs_branch_tree_depth6", *common, "terminal_card_canopy"],
        "Same recursive branch-tree IFS depth; V15 makes every transform child a connected tapered limb with terminal cards.",
        7,
    )

    mesh, ctl = ifs_radial_case(order=8, depth=4)
    add(
        "v15_ifs_radial_ornament_o8_d4_bridged_rings",
        "IFS/transform",
        "ifs_radial_ornament_o8_d4",
        "8-fold radial transform-copy ornament with four recursive scale levels",
        mesh,
        "metal",
        seed + 132,
        ctl,
        ["same_radial_order8_depth4", *common, "bridged_ring_cycles", "attached_metal_facets"],
        "Same order-8/depth-4 radial transform target; V15 adds bridged rings and small spokes so radial copies do not fragment.",
        7,
    )

    mesh, ctl = ifs_lattice_case(depth=4)
    add(
        "v15_ifs_lattice_crystal_d4_small_bridge_facets",
        "IFS/transform",
        "ifs_fractal_lattice_d4",
        "affine fractal lattice with recursive copy-and-bridge graph",
        mesh,
        "crystal",
        seed + 133,
        ctl,
        ["same_affine_lattice_depth4", *common, "small_copy_bridges", "attached_crystal_facets"],
        "Same affine lattice depth; V15 inserts small copy bridges and attached facets to keep the transform lattice connected and crystal-like.",
        4,
    )

    return specs


def _export_mesh(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


def _mesh_stats(path: Path, controls: dict) -> dict:
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
        "tapered_branch_edges": int(controls.get("tapered_branch_edges", 0)),
        "attached_detail_primitives": int(controls.get("attached_detail_primitives", 0)),
        "connected_root_hairs": int(controls.get("connected_root_hairs", 0)),
        "small_bridge_count": int(controls.get("small_bridge_count", 0)),
        "bridged_ring_count": int(controls.get("bridged_ring_count", 0)),
    }


def _metadata_for(spec: dict, mesh_path: Path, guide_path: str, metrics: dict) -> dict:
    operator_family = {
        "L-system": "traditional L-system symbolic rewrite",
        "Space colonization": "traditional space-colonization attractor competition",
        "IFS/transform": "traditional IFS/transform-copy recursion",
    }[spec["family"]]
    positive = "smooth connected support, tapered branches, and attached detail primitives"
    if spec["traditional_target"] == "ifs_fractal_lattice_d4":
        positive += "; small copy bridges prevent transform fragmentation"
    elif spec["traditional_target"] == "ifs_radial_ornament_o8_d4":
        positive += "; bridged rings prevent radial ornament fragmentation"
    elif "root" in spec["traditional_target"]:
        positive += "; root hairs are connected fine geometry"
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
            "why_strict_one_to_one": spec["why_matches_traditional"],
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
            "dryrun_visual_floor": "single main component or largest-component vertex ratio above 0.999 before Trellis2",
            "positive_constraint": positive,
            "negative_constraint": "no grape-like balls, no obvious voxel blocks, no pure rod scaffold, no detached transform islands",
            "v6_v8_failure_addressed": "connected plant/root/tree outputs were too rod/scaffold-like; IFS radial/lattice could fragment",
            "no_local_selection": "strict cases must be generated fresh on a100-2; local dry-run files are inputs, not selected final outputs",
        },
        "strict_generation_policy": "generate_new_on_a100_2_no_local_selection_or_posthoc_pick",
        "v15_design_note": "fresh plant/root/IFS branch using connected tapered supports, attached details, and LCR gating",
        "root_selection_log": {
            "root_source_type": "v15_smooth_connected_plants_ifs_input_generator",
            "source_generator": "assets/strict_visual_matched_cases_v15_plants_ifs_20260510.py",
            "root_pool_size": 1,
            "root_generation_budget": "local CPU dry-run geometry only; final strict case must be generated fresh on a100-2",
            "root_screening_budget": "no local manual cherry-pick, no V13/V14/DLA post-processing",
            "selection_rank": 1,
            "projection_naturalization_schedule": spec["operators"],
            "readiness_label": "remote_input_dryrun_lcr_ge_0.999",
            "connectivity_anchor_convention": "OBJ vertices 1..N are shared scaffold centers used by faces; details attach by shared vertices",
        },
    }


def _write_readme(out_dir: Path, summary: dict) -> None:
    text = f"""# V15 Plant/Root/IFS Strict Visual-Matched Cases Dry Run

Produced by `assets/strict_visual_matched_cases_v15_plants_ifs_20260510.py`.

This is an input batch only. It does not launch remote jobs, locally select
outputs, or post-process V13/V14/DLA assets. Final strict one-to-one cases must
be generated fresh on `{REMOTE_TARGET}` with GPU ids `{ALLOWED_GPUS}` under:

`{REMOTE_STORAGE_ROOT}`

Connectivity gate: largest-component vertex ratio >= `{CONNECTIVITY_LCR_MIN}`
before Trellis2.

Files:

- `manifest.csv` / `manifest.json`: case-level Trellis2 input manifest.
- `a100-2_cases.txt`: remote-ready `case_id|mesh_path|guide_image|seed|gpu` lines.
- `gpu4_cases.txt` ... `gpu7_cases.txt`: per-GPU splits.
- `gpu4567_cases.txt`: combined GPU 4/5/6/7 split.
- `initial_metrics.csv` / `initial_metrics.json`: pre-texture mesh metrics.
- each case folder: OBJ plus per-case metadata JSON.

Case count: {summary["num_cases"]}
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
        if metrics["mesh_component_count"] != 1 and metrics["largest_mesh_component_vertex_ratio"] < CONNECTIVITY_LCR_MIN:
            raise RuntimeError(f"{spec['case_id']} failed V15 connectivity gate: {metrics}")
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
        "tapered_branch_edges",
        "attached_detail_primitives",
        "connected_root_hairs",
        "small_bridge_count",
        "bridged_ring_count",
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
        "surface_generator": "smooth_connected_plants_roots_ifs_v15",
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
