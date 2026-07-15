#!/usr/bin/env python3
"""V6 strict one-to-one visual-matched Trellis2 input dry-run generator.

V6 is a connectivity-first successor to the V5 hybrid batch.  It emits new
case inputs only; it does not launch remote jobs, pick existing local outputs,
or post-process V3/V4/V5 assets.  The generated OBJ inputs are designed for
new strict one-to-one regeneration on a100-2, using only GPU ids 4/5/6/7.

The geometry strategy is intentionally explicit:

* same target category and same recursive mode as the traditional baseline;
* connected skeleton for every case, including DLA/frontier/crystal cases;
* smooth tube support plus anchored sheet/facet envelopes for non-tree cases;
* plant/root/vine cases keep thin hierarchy, leaves, tendrils, and hairs rather
  than a global implicit blob;
* metadata records source/root policy, operator composition, traditional
  target, controls, and why the input matches the comparison target.
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
from strict_matched_task_targets_20260510 import make_frontier_sheet


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 100
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_v6_connectivity_20260510_dryrun"


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


def _graph_edges(parents: list[int]) -> list[tuple[int, int]]:
    return [(int(parent), int(idx)) for idx, parent in enumerate(parents) if parent >= 0]


def _radii_from_parents(parents: list[int], base: float, taper: float, floor: float) -> list[float]:
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    return [max(base * (1.0 - taper * (depth / max(max_depth, 1))), floor) for depth in depths]


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


def welded_skeleton_mesh(nodes: list[np.ndarray], edges: list[tuple[int, int]], radii: list[float], sides: int = 8) -> pb.Mesh:
    """Build a face-connected tube mesh with every scaffold node used in faces."""

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
    c = np.asarray(anchor, dtype=float) + _unit(normal) * scale * 0.92
    a = float(scale) * float(aspect)
    b = float(scale)
    base = len(mesh.vertices)
    mesh.vertices.extend(
        [
            tuple(c + u * a),
            tuple(c + v * b),
            tuple(c - u * a),
            tuple(c - v * b),
        ]
    )
    # Double-sided card, anchored to an existing scaffold center vertex.
    for i in range(4):
        j = (i + 1) % 4
        mesh.faces.append((anchor_idx, base + i + 1, base + j + 1))
        mesh.faces.append((anchor_idx, base + j + 1, base + i + 1))


def _add_smooth_bulb_tip(
    mesh: pb.Mesh,
    anchor_idx: int,
    center: np.ndarray,
    axis: np.ndarray,
    radius: float,
    segments: int = 8,
    rings: int = 3,
) -> None:
    """Attach a small smooth cap to a skeleton node without creating islands."""

    u, v, w = _basis(axis)
    center = np.asarray(center, dtype=float)
    base = len(mesh.vertices)
    ring_indices: list[list[int]] = []
    for r in range(rings):
        t = (r + 1) / rings
        ring_center = center + w * float(radius) * (0.35 + 0.60 * t)
        ring_radius = float(radius) * math.sin(t * math.pi * 0.82) * (1.0 - 0.08 * r)
        ring: list[int] = []
        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            p = ring_center + (math.cos(theta) * u + math.sin(theta) * v) * ring_radius
            mesh.vertices.append(tuple(p))
            ring.append(len(mesh.vertices))
        ring_indices.append(ring)
    tip = center + w * float(radius) * 1.18
    mesh.vertices.append(tuple(tip))
    tip_idx = len(mesh.vertices)
    first = ring_indices[0]
    for i in range(segments):
        j = (i + 1) % segments
        mesh.faces.append((anchor_idx, first[i], first[j]))
    for r in range(len(ring_indices) - 1):
        ring = ring_indices[r]
        next_ring = ring_indices[r + 1]
        for i in range(segments):
            j = (i + 1) % segments
            mesh.faces.append((ring[i], ring[j], next_ring[i]))
            mesh.faces.append((ring[j], next_ring[j], next_ring[i]))
    last = ring_indices[-1]
    for i in range(segments):
        j = (i + 1) % segments
        mesh.faces.append((last[i], last[j], tip_idx))


def _add_edge_sheet(
    mesh: pb.Mesh,
    center_indices: list[int],
    nodes: list[np.ndarray],
    a: int,
    b: int,
    width: float,
    lift: float,
    faceted: bool,
) -> None:
    pa = np.asarray(nodes[a], dtype=float)
    pb_ = np.asarray(nodes[b], dtype=float)
    axis = pb_ - pa
    if float(np.linalg.norm(axis)) < 1e-7:
        return
    u, v, _ = _basis(axis)
    normal = _unit(v + np.array([0.0, 0.0, lift]))
    base = len(mesh.vertices)
    mid = (pa + pb_) * 0.5 + normal * float(width) * 0.35
    if faceted:
        tip1 = mid + u * float(width) * 0.80 + normal * float(width) * 0.55
        tip2 = mid - u * float(width) * 0.80 + normal * float(width) * 0.42
    else:
        tip1 = mid + u * float(width) * 0.55 + normal * float(width) * 0.35
        tip2 = mid - u * float(width) * 0.55 + normal * float(width) * 0.28
    mesh.vertices.extend([tuple(tip1), tuple(tip2)])
    ca = center_indices[a]
    cb = center_indices[b]
    mesh.faces.append((ca, cb, base + 1))
    mesh.faces.append((cb, base + 2, base + 1))
    mesh.faces.append((cb, ca, base + 2))


def _add_local_envelope_panels(
    mesh: pb.Mesh,
    nodes: list[np.ndarray],
    parents: list[int],
    width: float,
    lift: float,
    max_panels: int,
    faceted: bool = False,
) -> int:
    centers = getattr(mesh, "center_indices")
    placed = 0
    for idx, parent in enumerate(parents):
        if parent < 0:
            continue
        if placed >= max_panels:
            break
        if idx % 2 == 0 or placed < max_panels // 3:
            _add_edge_sheet(mesh, centers, nodes, parent, idx, width=width, lift=lift, faceted=faceted)
            placed += 1
    return placed


def _nearest_parent_edges(points: np.ndarray, mode: str = "radial") -> list[tuple[int, int]]:
    if mode == "frontier":
        order = np.lexsort((points[:, 2], points[:, 0], points[:, 1]))
    else:
        order = np.argsort(np.linalg.norm(points, axis=1))
    pts = points[order]
    edges: list[tuple[int, int]] = []
    for idx in range(1, len(pts)):
        prev = pts[:idx]
        parent = int(np.argmin(np.linalg.norm(prev - pts[idx], axis=1)))
        edges.append((int(order[parent]), int(order[idx])))
    return edges


def _parents_from_edges(num_nodes: int, edges: list[tuple[int, int]]) -> list[int]:
    parents = [-1 for _ in range(num_nodes)]
    for a, b in edges:
        if parents[b] < 0 and b != 0:
            parents[b] = a
    return parents


def lsystem_tree_case(seed: int) -> tuple[pb.Mesh, dict]:
    nodes0, parents = bm.lsystem_case("tree", depth=5, seed=seed)
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in nodes0], 2.35)
    radii = _radii_from_parents(parents, base=0.066, taper=0.78, floor=0.006)
    mesh = welded_skeleton_mesh(nodes, _graph_edges(parents), radii, sides=8)
    rng = np.random.default_rng(seed + 17)
    child_map = _children(parents)
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    leaf_count = 0
    for idx in [i for i in range(1, len(nodes)) if not child_map.get(i) or depths[i] >= max_depth * 0.70]:
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        u, v, _ = _basis(axis)
        for k in range(3):
            theta = 2.0 * math.pi * (k / 3.0) + rng.normal(0, 0.12)
            normal = _unit(0.28 * axis + math.cos(theta) * u + math.sin(theta) * v)
            _add_leaf_card(mesh, getattr(mesh, "center_indices")[idx], nodes[idx], normal, rng.uniform(0.022, 0.038), 2.8)
            leaf_count += 1
    envelope_panels = _add_local_envelope_panels(mesh, nodes, parents, width=0.032, lift=0.10, max_panels=64, faceted=False)
    return mesh, {
        "source": "baseline_matrix_20260509.lsystem_case(tree)",
        "depth": 5,
        "branch_nodes": len(nodes),
        "attached_needles": leaf_count,
        "local_smooth_envelope_panels": envelope_panels,
        "surface_strategy": "continuous pine spine plus many oriented needle primitives plus local smooth envelope panels; no implicit canopy blob",
    }


def lsystem_root_case(seed: int) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 23)
    nodes0, parents = bm.lsystem_case("root", depth=5, seed=seed)
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in nodes0], 2.45)
    radii = _radii_from_parents(parents, base=0.070, taper=0.82, floor=0.005)
    root_nodes = len(nodes)
    depths = bm.graph_depths(parents)
    for idx in range(1, root_nodes):
        if depths[idx] < 2:
            continue
        parent = parents[idx]
        axis = _unit(nodes[idx] - nodes[parent])
        u, v, _ = _basis(axis)
        for _ in range(2 + int(depths[idx] > 3)):
            direction = _unit(-0.18 * axis + rng.normal(0, 0.7) * u + rng.normal(0, 0.7) * v + np.array([0.0, 0.0, -0.42]))
            _append_child(nodes, parents, radii, idx, direction, rng.uniform(0.065, 0.18), rng.uniform(0.0026, 0.0045))
    mesh = welded_skeleton_mesh(nodes, _graph_edges(parents), radii, sides=8)
    envelope_panels = _add_local_envelope_panels(mesh, nodes, parents, width=0.026, lift=-0.08, max_panels=72, faceted=False)
    return mesh, {
        "source": "baseline_matrix_20260509.lsystem_case(root)",
        "depth": 5,
        "root_nodes": root_nodes,
        "attached_root_hairs": len(nodes) - root_nodes,
        "local_smooth_envelope_panels": envelope_panels,
        "surface_strategy": "continuous root spine plus many oriented rootlet primitives plus local smooth sheath panels",
    }


def lsystem_vine_case(seed: int) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 29)
    nodes = [np.zeros(3, dtype=float)]
    parents = [-1]
    radii = [0.050]
    parent = 0
    for level in range(1, 7):
        theta = level * 0.82
        step = np.array([math.cos(theta) * 0.22, math.sin(theta) * 0.22, 0.52])
        nodes.append(nodes[parent] + step)
        current = len(nodes) - 1
        parents.append(parent)
        radii.append(max(0.048 * (0.88**level), 0.011))
        for sign in (-1, 1):
            side = _unit(np.array([math.cos(theta + sign * 1.35), math.sin(theta + sign * 1.35), 0.15]))
            tip = nodes[current] + side * (0.29 + 0.034 * level) + rng.normal(0, 0.012, 3)
            nodes.append(tip)
            parents.append(current)
            radii.append(0.012)
            if level >= 3:
                nodes.append(tip + side * 0.16 + np.array([0.0, 0.0, 0.055]))
                parents.append(len(nodes) - 2)
                radii.append(0.0065)
        parent = current
    nodes = _normalize_nodes(nodes, 2.35)
    mesh = welded_skeleton_mesh(nodes, _graph_edges(parents), radii, sides=8)
    child_map = _children(parents)
    leaf_count = 0
    for idx in [i for i in range(1, len(nodes)) if not child_map.get(i)][::2]:
        parent_idx = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(nodes[idx] - nodes[parent_idx])
        _add_leaf_card(mesh, getattr(mesh, "center_indices")[idx], nodes[idx], axis + np.array([0.2, -0.1, 0.1]), 0.045, 1.65)
        leaf_count += 1
    envelope_panels = _add_local_envelope_panels(mesh, nodes, parents, width=0.030, lift=0.07, max_panels=38, faceted=False)
    return mesh, {
        "source": "hand-authored L-system vine equivalent to strict_matched_task_targets lsystem_climbing_vine",
        "iterations": 6,
        "curl_step_radians": 0.82,
        "attached_leaf_cards": leaf_count,
        "local_smooth_envelope_panels": envelope_panels,
        "surface_strategy": "continuous helical vine spine plus oriented leaves/tendrils plus local smooth envelope panels",
    }


def space_colonization_case(sc_case: str, seed: int, mode: str) -> tuple[pb.Mesh, dict]:
    attractors = 1500 if sc_case != "bush_shell" else 1300
    iterations = 260 if sc_case != "bush_shell" else 220
    result = scb.grow_space_colonization(
        case=sc_case,
        attractor_count=attractors,
        iterations=iterations,
        influence_radius=0.24 if sc_case != "bush_shell" else 0.23,
        kill_radius=0.055 if sc_case != "bush_shell" else 0.060,
        step_size=0.045 if sc_case != "bush_shell" else 0.043,
        seed=seed,
    )
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in result["nodes"]], 2.35)
    parents = [int(p) for p in result["parents"]]
    radii = _radii_from_parents(parents, base=0.054 if mode == "tree" else 0.060, taper=0.82, floor=0.0055)
    branch_nodes = len(nodes)
    rng = np.random.default_rng(seed + 41)
    child_map = _children(parents)
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    anchors = [i for i in range(1, branch_nodes) if not child_map.get(i) or depths[i] >= max_depth * 0.62]
    rng.shuffle(anchors)
    for idx in anchors[:90 if mode == "tree" else 125]:
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(nodes[idx] - nodes[parent])
        u, v, _ = _basis(axis)
        count = 1 if mode == "tree" else 2
        bias = np.array([0.0, 0.0, 0.14 if mode == "tree" else -0.38])
        for _ in range(count):
            direction = _unit(0.20 * axis + rng.normal(0, 0.75) * u + rng.normal(0, 0.75) * v + bias)
            _append_child(nodes, parents, radii, idx, direction, rng.uniform(0.055, 0.130), rng.uniform(0.0033, 0.0060))
    mesh = welded_skeleton_mesh(nodes, _graph_edges(parents), radii, sides=8)
    centers = getattr(mesh, "center_indices")
    leaf_cards = 0
    if mode == "tree":
        for idx in anchors[:85]:
            parent = parents[idx] if parents[idx] >= 0 else idx
            axis = _unit(nodes[idx] - nodes[parent])
            _add_leaf_card(mesh, centers[idx], nodes[idx], axis + np.array([0.0, 0.0, 0.18]), 0.035, 1.85)
            leaf_cards += 1
    envelope_panels = _add_local_envelope_panels(mesh, nodes, parents, width=0.030 if mode == "tree" else 0.024, lift=0.09 if mode == "tree" else -0.12, max_panels=80, faceted=False)
    return mesh, {
        "source": "space_colonization_baseline.grow_space_colonization",
        "case": sc_case,
        "attractor_count": attractors,
        "iterations": iterations,
        "influence_radius": 0.24 if sc_case != "bush_shell" else 0.23,
        "kill_radius": 0.055 if sc_case != "bush_shell" else 0.060,
        "step_size": 0.045 if sc_case != "bush_shell" else 0.043,
        "covered_attractors": result.get("covered_attractors"),
        "alive_attractors": result.get("alive_attractors"),
        "branch_nodes": branch_nodes,
        "attached_terminal_children": len(nodes) - branch_nodes,
        "attached_leaf_cards": leaf_cards,
        "local_smooth_envelope_panels": envelope_panels,
        "surface_strategy": "continuous SC spine plus many oriented leaf/rootlet primitives plus local smooth envelope panels",
    }


def dla_coral_case(seed: int, particles: int = 900) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed)
    pts = pb.make_dla_cluster(n_particles=particles, seed=seed % 10000) * np.array([1.08, 1.02, 1.18])
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in pts], 2.35)
    edges = _nearest_parent_edges(np.asarray(nodes), "radial")
    radii = []
    norms = np.linalg.norm(np.asarray(nodes), axis=1)
    max_norm = max(float(norms.max()), 1e-6)
    for value in norms:
        frontier = float(value) / max_norm
        radii.append(0.052 * (1.0 - 0.42 * frontier) + 0.010)
    parents = _parents_from_edges(len(nodes), edges)
    child_map = _children(parents)
    tips = [i for i in range(1, len(nodes)) if not child_map.get(i)]
    rng.shuffle(tips)
    base_count = len(nodes)
    for idx in tips[:155]:
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(nodes[idx] - nodes[parent])
        u, v, _ = _basis(axis)
        for k in range(2):
            theta = math.pi * k + rng.normal(0, 0.45)
            direction = _unit(0.45 * axis + math.cos(theta) * u + math.sin(theta) * v + rng.normal(0, 0.08, 3))
            nodes.append(np.asarray(nodes[idx]) + direction * rng.uniform(0.045, 0.105))
            radii.append(radii[idx] * rng.uniform(0.42, 0.60))
            edges.append((idx, len(nodes) - 1))
    mesh = welded_skeleton_mesh(nodes, edges, radii, sides=7)
    centers = getattr(mesh, "center_indices")
    final_parents = _parents_from_edges(len(nodes), edges)
    final_child_map = _children(final_parents)
    final_tips = [i for i in range(1, len(nodes)) if not final_child_map.get(i)]
    bulb_tips = 0
    for idx in final_tips[:130]:
        parent = final_parents[idx] if final_parents[idx] >= 0 else 0
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        _add_smooth_bulb_tip(mesh, centers[idx], nodes[idx], axis, radius=max(radii[idx] * 1.75, 0.026), segments=8, rings=3)
        bulb_tips += 1
    porous_bridges = 0
    for a, b in edges[:: max(len(edges) // 90, 1)]:
        _add_edge_sheet(mesh, centers, nodes, a, b, width=0.038, lift=0.05, faceted=False)
        porous_bridges += 1
    return mesh, {
        "source": "procedural_baselines.make_dla_cluster",
        "particles": particles,
        "base_attachment_edges": len(_dedupe_edges(edges[: max(base_count - 1, 0)])),
        "attached_frontier_tubelets": len(nodes) - base_count,
        "attached_bulbous_smooth_tips": bulb_tips,
        "attached_porous_bridges": porous_bridges,
        "surface_strategy": "connected DLA branching tubes plus bulbous/smooth tips and attached porous bridges",
        "anti_blob_policy": "no cube voxels and no global implicit blob; every surface lobe is attached to a parent edge",
    }


def dla_frontier_sheet_case(seed: int, particles: int = 700) -> tuple[pb.Mesh, dict]:
    pts = make_frontier_sheet(seed, particles=particles) * np.array([2.08, 1.45, 0.92])
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in pts], 2.35)
    edges = _nearest_parent_edges(np.asarray(nodes), "frontier")
    radii = [0.045 + 0.009 * math.sin(i * 0.23) for i in range(len(nodes))]
    mesh = welded_skeleton_mesh(nodes, edges, radii, sides=7)
    centers = getattr(mesh, "center_indices")
    parents = _parents_from_edges(len(nodes), edges)
    child_map = _children(parents)
    boundary_tips = [i for i in range(1, len(nodes)) if not child_map.get(i)]
    bulb_tips = 0
    for idx in boundary_tips[:110]:
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        _add_smooth_bulb_tip(mesh, centers[idx], nodes[idx], axis, radius=max(radii[idx] * 1.55, 0.024), segments=8, rings=3)
        bulb_tips += 1
    porous_bridges = 0
    order = np.lexsort((np.asarray(nodes)[:, 2], np.asarray(nodes)[:, 0], np.asarray(nodes)[:, 1]))
    for i in range(0, len(order) - 1, max(len(order) // 120, 1)):
        _add_edge_sheet(mesh, centers, nodes, int(order[i]), int(order[i + 1]), width=0.048, lift=0.10, faceted=False)
        porous_bridges += 1
    return mesh, {
        "source": "strict_matched_task_targets_20260510.make_frontier_sheet",
        "particles": particles,
        "base_attachment_edges": len(_dedupe_edges(edges)),
        "attached_bulbous_smooth_tips": bulb_tips,
        "attached_porous_bridges": porous_bridges,
        "surface_strategy": "line-seeded frontier branching tubes plus bulbous/smooth tips and attached porous bridges",
        "anti_blob_policy": "sheet panels are edge-attached and sparse, preserving frontier holes",
    }


def crystal_facet_case(seed: int) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed)
    nodes = [np.zeros(3, dtype=float)]
    radii = [0.055]
    edges: list[tuple[int, int]] = []
    shell_nodes = 0
    for layer in range(1, 5):
        radius = 0.20 + 0.20 * layer
        count = 8 + layer * 4
        z_jitter = 0.035 * layer
        ring: list[int] = []
        for i in range(count):
            theta = 2.0 * math.pi * i / count + 0.17 * layer
            z = ((i % 3) - 1) * z_jitter
            p = np.array([math.cos(theta) * radius, math.sin(theta) * radius, z])
            nodes.append(p)
            radii.append(max(0.045 * (0.86**layer), 0.014))
            ring.append(len(nodes) - 1)
            shell_nodes += 1
        for i, idx in enumerate(ring):
            edges.append((idx, ring[(i + 1) % len(ring)]))
            if layer == 1 or i % 2 == 0:
                edges.append((0, idx))
            else:
                prev = 1 + (i * (8 + (layer - 1) * 4) // count)
                edges.append((max(1, min(prev, len(nodes) - len(ring) - 1)), idx))
            if i % 4 == 0:
                tip = nodes[idx] + _unit(nodes[idx] + rng.normal(0, 0.06, 3)) * (0.10 + 0.025 * layer)
                nodes.append(tip)
                radii.append(0.010)
                edges.append((idx, len(nodes) - 1))
    mesh = welded_skeleton_mesh(nodes, edges, radii, sides=6)
    centers = getattr(mesh, "center_indices")
    for a, b in edges:
        if (a + b) % 5 == 0:
            _add_edge_sheet(mesh, centers, nodes, a, b, width=0.060, lift=0.18, faceted=True)
    return mesh, {
        "source": "V6 bismuth/pyrite stepped faceted attachment graph",
        "layers": 4,
        "shell_nodes": shell_nodes,
        "crystal_style": "bismuth/pyrite stepped lattice facets",
        "facet_policy": "every facet is attached to a skeleton edge using shared scaffold center vertices",
        "surface_strategy": "connected skeleton plus bismuth/pyrite stepped lattice facets and bridge spokes",
    }


def ifs_radial_case(order: int = 8, depth: int = 4) -> tuple[pb.Mesh, dict]:
    nodes: list[np.ndarray] = [np.zeros(3, dtype=float)]
    radii: list[float] = [0.070]
    edges: list[tuple[int, int]] = []
    previous_ring: list[int] = []
    tooth_nodes = 0
    bridge_nodes = 0
    for level in range(depth):
        radius = 0.28 + level * 0.245
        z = 0.040 * level
        tube = max(0.036 * (0.84**level), 0.014)
        phase = 0.18 * level
        ring: list[int] = []
        ring_steps = order * 4
        for i in range(ring_steps):
            theta = 2.0 * math.pi * i / ring_steps + phase
            nodes.append(np.array([math.cos(theta) * radius, math.sin(theta) * radius, z]))
            radii.append(tube)
            ring.append(len(nodes) - 1)
        for i, idx in enumerate(ring):
            edges.append((idx, ring[(i + 1) % len(ring)]))
            if i % 4 == 0:
                edges.append((0, idx))
                theta = 2.0 * math.pi * (i / ring_steps) + phase
                direction = _unit(np.array([math.cos(theta), math.sin(theta), 0.08]))
                nodes.append(nodes[idx] + direction * (0.12 + 0.018 * (depth - level)))
                radii.append(tube * 0.45)
                edges.append((idx, len(nodes) - 1))
                tooth_nodes += 1
                if previous_ring:
                    prev = previous_ring[i % len(previous_ring)]
                    edges.append((prev, idx))
                    bridge_nodes += 1
        previous_ring = ring
    mesh = welded_skeleton_mesh(nodes, edges, radii, sides=8)
    centers = getattr(mesh, "center_indices")
    for a, b in edges[::3]:
        _add_edge_sheet(mesh, centers, nodes, a, b, width=0.040, lift=0.02, faceted=True)
    return mesh, {
        "source": "V6 radial IFS transform-copy graph",
        "order": order,
        "depth": depth,
        "tooth_nodes": tooth_nodes,
        "bridge_nodes": bridge_nodes,
        "surface_strategy": "closed transform rings, shared center spine, inter-depth spokes, and attached metal facets",
    }


def ifs_lattice_case(depth: int = 4) -> tuple[pb.Mesh, dict]:
    nodes: list[np.ndarray] = [np.zeros(3, dtype=float)]
    radii: list[float] = [0.062]
    edges: list[tuple[int, int]] = []
    frontier = [0]
    directions = [
        np.array([1.0, 0.0, 0.34]),
        np.array([-0.5, 0.866, 0.34]),
        np.array([-0.5, -0.866, 0.34]),
        np.array([0.0, 0.0, -1.0]),
    ]
    for level in range(depth):
        next_frontier: list[int] = []
        step = 0.48 * (0.66**level)
        for parent in frontier:
            for direction in directions:
                point = nodes[parent] + _unit(direction) * step
                nodes.append(point)
                radii.append(max(0.042 * (0.78**level), 0.012))
                idx = len(nodes) - 1
                edges.append((parent, idx))
                next_frontier.append(idx)
        for i in range(0, len(next_frontier) - 1, 2):
            edges.append((next_frontier[i], next_frontier[i + 1]))
        frontier = next_frontier[::2]
    nodes = _normalize_nodes(nodes, 2.25)
    mesh = welded_skeleton_mesh(nodes, edges, radii, sides=6)
    centers = getattr(mesh, "center_indices")
    for a, b in edges[::2]:
        _add_edge_sheet(mesh, centers, nodes, a, b, width=0.038, lift=0.12, faceted=True)
    return mesh, {
        "source": "V6 affine IFS lattice expansion",
        "depth": depth,
        "affine_children_per_node": 4,
        "bridge_edges": len(edges),
        "surface_strategy": "recursive affine lattice scaffold with facet plates anchored to copy edges",
    }


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
        for _ in range(560):
            c = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(0, 768))
            y = int(rng.integers(0, 768))
            if strokes == "needles":
                draw.line((x, y, x + int(rng.normal(0, 55)), y + int(rng.normal(-20, 44))), fill=c, width=int(rng.integers(1, 4)))
            elif strokes == "roots":
                draw.line((x, y, x + int(rng.normal(0, 82)), y + int(rng.normal(34, 44))), fill=c, width=int(rng.integers(2, 7)))
            elif strokes == "coral":
                r = int(rng.integers(5, 20))
                draw.ellipse((x - r, y - r, x + r, y + r), outline=c, width=int(rng.integers(2, 5)))
            elif strokes == "facet":
                r = int(rng.integers(8, 34))
                draw.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=c)
            else:
                draw.line((x, y, x + int(rng.normal(0, 80)), y + int(rng.normal(0, 80))), fill=c, width=5)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "conifer": save("v6_conifer_same_lsystem_guide.png", [(25, 49, 30), (55, 89, 46), (99, 119, 72), (88, 61, 36)], "needles"),
        "leaf": save("v6_leaf_vine_attached_guide.png", [(34, 71, 38), (86, 126, 57), (126, 96, 55), (52, 43, 29)], "needles"),
        "root": save("v6_root_hierarchy_guide.png", [(35, 27, 20), (79, 57, 36), (123, 89, 55), (23, 20, 16)], "roots"),
        "coral": save("v6_dla_coral_connected_guide.png", [(112, 57, 53), (176, 94, 72), (226, 150, 101), (80, 42, 47)], "coral"),
        "crystal": save("v6_crystal_facets_connected_guide.png", [(42, 50, 60), (95, 111, 125), (155, 169, 178), (74, 87, 101)], "facet"),
        "metal": save("v6_radial_lattice_metal_guide.png", [(34, 37, 34), (91, 97, 84), (158, 128, 76), (88, 42, 32)], "facet"),
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
        priority: bool,
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

    mesh, ctl = lsystem_tree_case(seed + 1)
    add(
        "v6_lsys_pine_canopy_d5_same_rule_welded_needles",
        "L-system",
        "lsys_pine_canopy_d5",
        "symbolic turtle branch rewriting, depth 5, pine/tree canopy",
        mesh,
        "conifer",
        seed + 101,
        ctl,
        ["same_lsystem_tree_rule", "welded_tapered_skeleton", "shared_junction_fans", "anchored_needle_cards"],
        "Uses the same tree L-system depth and branching family as the traditional pine/canopy target; needles are anchored details, not disconnected sprites or a canopy blob.",
        4,
        True,
    )

    mesh, ctl = lsystem_root_case(seed + 2)
    add(
        "v6_lsys_root_fan_d5_same_rule_welded_hairs",
        "L-system",
        "lsys_root_fan_d5",
        "symbolic turtle root branching with downward tropism, depth 5",
        mesh,
        "root",
        seed + 102,
        ctl,
        ["same_lsystem_root_rule", "welded_root_skeleton", "shared_junction_fans", "child_edge_root_hairs"],
        "Matches the traditional root fan with the same depth-5 root/tropism grammar and explicit attached hairs on the root hierarchy.",
        5,
        True,
    )

    mesh, ctl = lsystem_vine_case(seed + 3)
    add(
        "v6_lsys_climbing_vine_d6_same_curl_attached_leaves",
        "L-system",
        "lsys_climbing_vine_d6",
        "curling main chain with recursive tendrils, six iterations",
        mesh,
        "leaf",
        seed + 103,
        ctl,
        ["same_vine_curl_schedule", "welded_main_vine", "shared_tendril_edges", "anchored_leaf_cards"],
        "Keeps the traditional climbing vine mode: six helical steps, recursive tendrils, and real anchored leaf cards without over-smoothing into a blob.",
        6,
        False,
    )

    mesh, ctl = space_colonization_case("tree_canopy", seed + 11, "tree")
    add(
        "v6_sc_tree_crown_260_same_attractor_welded_leaf_shell",
        "Space colonization",
        "sc_tree_crown_260",
        "tree crown attractor competition with influence/kill radii",
        mesh,
        "leaf",
        seed + 111,
        ctl,
        ["same_sc_tree_attractors", "node_parent_competition_graph", "welded_branch_skeleton", "attached_terminal_leaflets"],
        "Uses the same space-colonization tree-crown task and control radii; terminal foliage remains attached to branch endpoints.",
        4,
        True,
    )

    mesh, ctl = space_colonization_case("root_vine", seed + 12, "root")
    add(
        "v6_sc_root_network_260_same_attractor_welded_rootlets",
        "Space colonization",
        "sc_root_network_260",
        "root/vine attractor competition in below-ground volume",
        mesh,
        "root",
        seed + 112,
        ctl,
        ["same_sc_root_attractors", "node_parent_root_graph", "welded_root_skeleton", "attached_rootlet_edges"],
        "Matches the traditional SC root network through the same attractor-competition mode and explicit below-ground rootlet children.",
        5,
        True,
    )

    mesh, ctl = space_colonization_case("bush_shell", seed + 13, "tree")
    add(
        "v6_sc_bush_shell_220_same_attractor_welded_shell",
        "Space colonization",
        "sc_bush_shell_220",
        "bush-shell attractor competition with outward terminal coverage",
        mesh,
        "leaf",
        seed + 113,
        ctl,
        ["same_sc_bush_shell", "node_parent_shell_graph", "welded_branch_skeleton", "attached_shell_leaflets"],
        "Keeps the SC bush-shell category distinct from tree/root by using the bush-shell attractor field and attached outward terminal details.",
        6,
        False,
    )

    mesh, ctl = dla_coral_case(seed + 21, 900)
    add(
        "v6_dla_coral_cluster_900_connected_tube_sheet",
        "DLA/frontier",
        "dla_coral_cluster_900",
        "stochastic DLA accretion with nearest-parent attachment graph",
        mesh,
        "coral",
        seed + 121,
        ctl,
        ["same_dla_particle_cluster", "nearest_parent_attachment_tree", "smooth_tube_envelope", "attached_porous_sheet_bridges"],
        "Keeps the stochastic DLA/coral accretion target but replaces disconnected voxel chunks with a connected skeleton, tubes, and edge-attached porous sheets.",
        7,
        True,
    )

    mesh, ctl = dla_frontier_sheet_case(seed + 22, 700)
    add(
        "v6_dla_frontier_sheet_700_connected_boundary_sheet",
        "DLA/frontier",
        "dla_frontier_sheet_700",
        "line-seeded frontier sheet growth with boundary accretion",
        mesh,
        "coral",
        seed + 122,
        ctl,
        ["same_frontier_sheet_sampler", "boundary_order_attachment", "smooth_tube_spine", "anchored_sheet_envelope"],
        "Matches the frontier-sheet target with the same line-seeded sampler and boundary silhouette while enforcing connected tubes and anchored sheet panels.",
        7,
        True,
    )

    mesh, ctl = crystal_facet_case(seed + 23)
    add(
        "v6_dla_crystal_facet_cluster_connected_bridges",
        "DLA/frontier",
        "dla_crystal_cluster_520",
        "accretive crystal-like cluster with facet-preserving attachment bridges",
        mesh,
        "crystal",
        seed + 123,
        ctl,
        ["crystal_accretion_shells", "nearest_bridge_spokes", "faceted_edge_envelope", "attachment_bridge_facets"],
        "Targets the non-tree crystal/DLA failure mode directly: facets are preserved as attached plates on a connected skeleton instead of floating shards.",
        4,
        True,
    )

    mesh, ctl = ifs_radial_case(8, 4)
    add(
        "v6_ifs_radial_ornament_o8_d4_connected_facets",
        "IFS/transform",
        "ifs_radial_ornament_o8_d4",
        "8-fold radial transform-copy ornament with four recursive scale levels",
        mesh,
        "metal",
        seed + 132,
        ctl,
        ["same_radial_order8_transform", "closed_ring_cycles", "inter_depth_bridge_spokes", "attached_faceted_teeth"],
        "Keeps the order-8/depth-4 transform-copy target with closed rings, bridge spokes, teeth, and edge-attached facets.",
        5,
        True,
    )

    mesh, ctl = ifs_lattice_case(4)
    add(
        "v6_ifs_fractal_lattice_d4_connected_copy_facets",
        "IFS/transform",
        "ifs_fractal_lattice_d4",
        "affine fractal lattice with recursive copy-and-bridge graph",
        mesh,
        "metal",
        seed + 133,
        ctl,
        ["same_affine_lattice_depth4", "recursive_copy_graph", "contact_bridge_edges", "attached_lattice_facets"],
        "Matches an IFS/fractal lattice target by making each affine copy an attached graph child with contact bridges and non-floating facet plates.",
        6,
        False,
    )

    return specs


def _export_mesh(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


def _mesh_stats(path: Path) -> dict:
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
    }


def _metadata_for(spec: dict, mesh_path: Path, guide_path: str, metrics: dict) -> dict:
    operator_family = {
        "L-system": "traditional L-system symbolic rewrite",
        "Space colonization": "traditional space-colonization attractor competition",
        "DLA/frontier": "traditional DLA/frontier accretive attachment",
        "IFS/transform": "traditional IFS/transform-copy recursion",
    }.get(spec["family"], spec["family"])
    if spec["family"] in {"L-system", "Space colonization"}:
        v5_issue = "V5 was connected but read as bare scaffold; V6 adds oriented leaves/needles/rootlets and local smooth envelope."
        organic_structure = "continuous spine plus many oriented leaf/needle/rootlet primitives plus local smooth envelope"
        non_tree_structure = ""
    elif spec["family"] == "DLA/frontier":
        v5_issue = "V5 DLA/frontier read as dark blocky stone; V6 uses connected branching tubes, bulbous/smooth tips, and porous bridges."
        organic_structure = ""
        non_tree_structure = "connected branching tubes plus bulbous/smooth tips plus porous bridges; crystal variant uses bismuth/pyrite stepped lattice facets"
    else:
        v5_issue = "V5 radial ornament was readable but visually secondary; V6 keeps it as backup with cleaner connected facets."
        organic_structure = ""
        non_tree_structure = "connected transform skeleton with edge-attached lattice facets"
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
            "dryrun_visual_floor": "single-component mesh is only the minimum gate; neutral renders must show the target family before remote results are considered publishable",
            "v5_failure_addressed": v5_issue,
            "organic_structure": organic_structure,
            "non_tree_structure": non_tree_structure,
            "no_local_selection": "strict cases must be generated fresh on a100-2; local dry-run files are inputs, not selected final outputs",
        },
        "strict_generation_policy": "generate_new_on_a100_2_no_local_selection_or_posthoc_pick",
        "v6_design_note": "connected skeleton plus smooth tube/sheet/facet envelope with explicit attachment bridges",
        "root_selection_log": {
            "root_source_type": "v6_connected_case_input_generator",
            "source_generator": "assets/strict_visual_matched_cases_v6_connectivity_20260510.py",
            "root_pool_size": 1,
            "root_generation_budget": "local CPU dry-run geometry only; final strict case must be generated fresh on a100-2",
            "root_screening_budget": "no local manual cherry-pick, no V3/V4/V5 post-processing",
            "selection_rank": 1,
            "projection_naturalization_schedule": spec["operators"],
            "readiness_label": "remote_input_dryrun_single_component",
            "connectivity_anchor_convention": "OBJ vertices 1..N are shared scaffold centers used by faces",
        },
    }


def _write_readme(out_dir: Path, summary: dict) -> None:
    text = f"""# V6 Connectivity Strict Visual-Matched Cases Dry Run

This directory was produced locally by `assets/strict_visual_matched_cases_v6_connectivity_20260510.py`.

It is a dry-run input batch only.  It does not contain remote Trellis2 outputs,
does not launch jobs, and does not locally select/post-process existing V3/V4/V5
results.  Strict one-to-one visual comparison cases must be generated fresh on
`{REMOTE_TARGET}` with GPU ids `{ALLOWED_GPUS}` and outputs under:

`{REMOTE_STORAGE_ROOT}`

Storage cap: `{STORAGE_LIMIT_GB}GB`.

Files:

- `manifest.csv` / `manifest.json`: case-level Trellis2 input manifest.
- `a100-2_cases.txt`: remote-ready lines in `case_id|mesh_path|guide_image|seed|gpu` format.
- `gpu4567_cases.txt`: same lines, explicitly scoped to GPUs 4/5/6/7.
- `initial_metrics.csv` / `initial_metrics.json`: pre-texture mesh metrics; every V6 input is required to be one component.
- each case folder: OBJ plus per-case metadata JSON.

Run locally:

```bash
python3 assets/strict_visual_matched_cases_v6_connectivity_20260510.py
```

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
        metrics = _mesh_stats(mesh_path)
        if metrics["mesh_component_count"] != 1:
            raise RuntimeError(f"{spec['case_id']} is not single-component: {metrics}")
        guide_path = guides[spec["guide_key"]]
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
    ]
    with (out_dir / "initial_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        writer.writerows(metrics_rows)
    (out_dir / "initial_metrics.json").write_text(json.dumps(metrics_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    case_lines = [f"{row['case_id']}|{row['mesh_path']}|{row['guide_image']}|{row['seed']}|{row['gpu_group']}" for row in rows]
    (out_dir / "a100-2_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    (out_dir / "gpu4567_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")

    summary = {
        "out_dir": str(out_dir),
        "num_cases": len(rows),
        "remote_target": REMOTE_TARGET,
        "allowed_gpus": ALLOWED_GPUS,
        "storage_root": REMOTE_STORAGE_ROOT,
        "storage_limit_gb": STORAGE_LIMIT_GB,
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
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=20260510)
    parser.add_argument("--case-limit", type=int, default=None)
    args = parser.parse_args()
    materialize(args.root, args.out or DEFAULT_OUT, seed=args.seed, case_limit=args.case_limit)


if __name__ == "__main__":
    main()
