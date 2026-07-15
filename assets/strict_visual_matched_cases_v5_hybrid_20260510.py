#!/usr/bin/env python3
"""V5 hybrid strict visual-matched Trellis2 input dry-run generator.

V5 is a small targeted batch for the weak visual cases from V3/V4.  It avoids
global implicit surfacing for plants, roots, DLA, and radial ornaments.  Instead
it builds explicit recursive support graphs and exports connected meshes by
sharing scaffold vertices at every attachment, bridge, spine, and leaf anchor.

The script is local CPU only.  It writes OBJ inputs, guides, manifests,
per-case metadata, and initial mesh metrics.  It does not launch remote jobs.
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
import space_colonization_baseline as scb
from strict_matched_task_targets_20260510 import make_frontier_sheet

REMOTE_TARGET = "a100-2"
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_v5_hybrid_20260510_dryrun"


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _normalize_nodes(nodes: list[np.ndarray], extent: float = 2.35) -> list[np.ndarray]:
    arr = np.asarray(nodes, dtype=float)
    mn, mx = arr.min(axis=0), arr.max(axis=0)
    center = (mn + mx) * 0.5
    scale = max(float((mx - mn).max()), 1e-6)
    return [(np.asarray(n, dtype=float) - center) * (extent / scale) for n in nodes]


def _basis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = _unit(axis)
    seed = np.array([0.0, 0.0, 1.0]) if abs(w[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = _unit(np.cross(w, seed))
    v = _unit(np.cross(w, u))
    return u, v, w


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
        key = (min(a, b), max(a, b))
        if key in seen:
            continue
        seen.add(key)
        out.append((a, b))
    return out


def _radii_from_parents(parents: list[int], base: float, taper: float, floor: float) -> list[float]:
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    return [max(base * (1.0 - taper * (d / max(max_depth, 1))), floor) for d in depths]


def _add_tube_edge(
    mesh: pb.Mesh,
    center_indices: list[int],
    nodes: list[np.ndarray],
    radii: list[float],
    a: int,
    b: int,
    sides: int,
) -> tuple[list[int], list[int]] | None:
    start = np.asarray(nodes[a], dtype=float)
    end = np.asarray(nodes[b], dtype=float)
    axis = end - start
    if float(np.linalg.norm(axis)) < 1e-7:
        return None
    u, v, _ = _basis(axis)
    r0 = float(radii[a])
    r1 = float(radii[b])
    base = len(mesh.vertices)
    for i in range(sides):
        theta = 2.0 * math.pi * i / sides
        d = math.cos(theta) * u + math.sin(theta) * v
        mesh.vertices.append(tuple(start + d * r0))
    for i in range(sides):
        theta = 2.0 * math.pi * i / sides
        d = math.cos(theta) * u + math.sin(theta) * v
        mesh.vertices.append(tuple(end + d * r1))
    for i in range(sides):
        j = (i + 1) % sides
        r0_i = base + i + 1
        r0_j = base + j + 1
        r1_i = base + sides + i + 1
        r1_j = base + sides + j + 1
        mesh.faces.append((r0_i, r0_j, r1_i))
        mesh.faces.append((r0_j, r1_j, r1_i))
    ring0 = [base + i + 1 for i in range(sides)]
    ring1 = [base + sides + i + 1 for i in range(sides)]
    return ring0, ring1


def welded_tube_mesh(nodes: list[np.ndarray], edges: list[tuple[int, int]], radii: list[float], sides: int = 9) -> pb.Mesh:
    mesh = pb.Mesh([], [])
    center_indices: list[int] = []
    for node in nodes:
        mesh.vertices.append(tuple(np.asarray(node, dtype=float)))
        center_indices.append(len(mesh.vertices))
    incident_rings: list[list[list[int]]] = [[] for _ in nodes]
    for a, b in _dedupe_edges(edges):
        rings = _add_tube_edge(mesh, center_indices, nodes, radii, int(a), int(b), sides=sides)
        if rings is None:
            continue
        ring0, ring1 = rings
        incident_rings[int(a)].append(ring0)
        incident_rings[int(b)].append(ring1)
    node_connector_indices: list[int] = []
    for idx, rings in enumerate(incident_rings):
        if not rings:
            node_connector_indices.append(center_indices[idx])
            continue
        node_connector_indices.append(rings[0][0])
        center = center_indices[idx]
        if len(rings) == 1:
            ring = rings[0]
            for i in range(sides):
                j = (i + 1) % sides
                mesh.faces.append((center, ring[i], ring[j]))
            continue
        # Junction bridge ribbons make incident tubes share surface edges.  Each
        # bridge uses a different ring segment where possible, which avoids
        # relying on non-manifold center-only contact.
        used: set[tuple[int, int]] = set()
        for ridx in range(len(rings) - 1):
            ring = rings[ridx]
            next_ring = rings[ridx + 1]
            s = ridx % sides
            for _ in range(sides):
                edge_a = tuple(sorted((ring[s], ring[(s + 1) % sides])))
                edge_b = tuple(sorted((next_ring[s], next_ring[(s + 1) % sides])))
                if edge_a not in used and edge_b not in used:
                    break
                s = (s + 1) % sides
            used.add(tuple(sorted((ring[s], ring[(s + 1) % sides]))))
            used.add(tuple(sorted((next_ring[s], next_ring[(s + 1) % sides]))))
            mesh.faces.append((ring[s], ring[(s + 1) % sides], next_ring[s]))
            mesh.faces.append((ring[(s + 1) % sides], next_ring[(s + 1) % sides], next_ring[s]))
    setattr(mesh, "node_connector_indices", node_connector_indices)
    return mesh


def _append_spur(
    nodes: list[np.ndarray],
    parents: list[int],
    radii: list[float],
    anchor: int,
    direction: np.ndarray,
    length: float,
    radius: float,
) -> int:
    nodes.append(np.asarray(nodes[anchor], dtype=float) + _unit(direction) * float(length))
    parents.append(anchor)
    radii.append(float(radius))
    return len(nodes) - 1


def add_leaf_card(
    mesh: pb.Mesh,
    anchor_vertex_index: int,
    connector_vertex_index: int,
    anchor: np.ndarray,
    normal: np.ndarray,
    scale: float,
    aspect: float,
) -> None:
    u, v, _ = _basis(normal)
    c = np.asarray(anchor, dtype=float) + _unit(normal) * scale * 0.95
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
    # Cards share an existing anchor-connector edge with the branch mesh, so
    # they are connected visual lobes instead of separate leaf-card components.
    for i in range(4):
        j = (i + 1) % 4
        mesh.faces.append((anchor_vertex_index, base + i + 1, base + j + 1))
        mesh.faces.append((anchor_vertex_index, base + j + 1, base + i + 1))
        mesh.faces.append((anchor_vertex_index, connector_vertex_index, base + i + 1))
        mesh.faces.append((anchor_vertex_index, base + i + 1, connector_vertex_index))


def _mesh_center_indices_for_nodes() -> str:
    return "OBJ vertices 1..N are shared scaffold node anchors"


def attach_leaf_cards(mesh: pb.Mesh, nodes: list[np.ndarray], parents: list[int], seed: int, count_limit: int, mode: str) -> int:
    rng = np.random.default_rng(seed)
    child_map = _children(parents)
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    candidates = [i for i in range(1, len(nodes)) if (not child_map.get(i) or depths[i] >= max_depth * 0.55)]
    if not candidates:
        return 0
    rng.shuffle(candidates)
    placed = 0
    for idx in candidates[:count_limit]:
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        u, v, _ = _basis(axis)
        if mode == "pine":
            for k in range(3):
                theta = 2.0 * math.pi * k / 3.0 + rng.normal(0, 0.12)
                normal = _unit(0.35 * axis + math.cos(theta) * u + math.sin(theta) * v)
                connector = getattr(mesh, "node_connector_indices", [idx + 1] * len(nodes))[idx]
                add_leaf_card(mesh, idx + 1, connector, nodes[idx], normal, rng.uniform(0.018, 0.031), aspect=3.1)
                placed += 1
        else:
            normal = _unit(0.35 * axis + rng.normal(0, 0.8) * u + rng.normal(0, 0.8) * v + np.array([0.0, 0.0, 0.10]))
            connector = getattr(mesh, "node_connector_indices", [idx + 1] * len(nodes))[idx]
            add_leaf_card(mesh, idx + 1, connector, nodes[idx], normal, rng.uniform(0.030, 0.052), aspect=rng.uniform(1.5, 2.2))
            placed += 1
    return placed


def graph_from_parents(parents: list[int]) -> list[tuple[int, int]]:
    return [(int(parent), int(idx)) for idx, parent in enumerate(parents) if parent >= 0]


def layered_pine_graph(seed: int) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed)
    nodes = [np.array([0.0, 0.0, -1.05 + i * 0.24], dtype=float) for i in range(9)]
    parents = [-1] + list(range(8))
    radii = [0.060 * (0.91**i) for i in range(9)]
    for level in range(2, 9):
        base = nodes[level]
        radius = 0.58 * (1.0 - 0.074 * level)
        branch_count = 5 if level < 7 else 4
        for k in range(branch_count):
            theta = 2.0 * math.pi * k / branch_count + level * 0.34 + rng.normal(0, 0.035)
            out = _unit(np.array([math.cos(theta), math.sin(theta), 0.08 + 0.024 * level]))
            p1 = base + out * radius
            p2 = p1 + _unit(out + np.array([0.0, 0.0, 0.20])) * radius * 0.42
            i1 = len(nodes)
            nodes.append(p1)
            parents.append(level)
            radii.append(0.026)
            nodes.append(p2)
            parents.append(i1)
            radii.append(0.010)
    branch_node_count = len(nodes)
    child_map = _children(parents)
    tips = [i for i in range(1, branch_node_count) if not child_map.get(i)]
    for idx in tips:
        parent = parents[idx]
        axis = _unit(nodes[idx] - nodes[parent])
        u, v, _ = _basis(axis)
        for k in range(5):
            theta = 2.0 * math.pi * k / 5.0 + rng.normal(0, 0.10)
            direction = _unit(0.45 * axis + math.cos(theta) * u + math.sin(theta) * v + np.array([0.0, 0.0, 0.10]))
            _append_spur(nodes, parents, radii, idx, direction, rng.uniform(0.11, 0.18), rng.uniform(0.0035, 0.0055))
    mesh = welded_tube_mesh(_normalize_nodes(nodes, 2.35), graph_from_parents(parents), radii, sides=8)
    return mesh, {
        "layout": "whorled trunk plus explicit needle spurs",
        "branch_nodes": branch_node_count,
        "attached_needle_spurs": len(nodes) - branch_node_count,
        "attached_leaf_cards": 0,
        "connector_strategy": "shared tube junction ribbons at trunk, whorl, and needle spur attachments",
    }


def lsystem_root_graph(seed: int) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed)
    nodes0, parents = bm.lsystem_case("root", depth=5, seed=seed)
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in nodes0], 2.45)
    radii = _radii_from_parents(parents, base=0.070, taper=0.80, floor=0.006)
    root_node_count = len(nodes)
    depths = bm.graph_depths(parents)
    for idx in range(1, root_node_count):
        if depths[idx] < 2:
            continue
        parent = parents[idx]
        axis = _unit(nodes[idx] - nodes[parent])
        u, v, _ = _basis(axis)
        for _ in range(2 + int(depths[idx] > 4)):
            direction = _unit(-0.25 * axis + rng.normal(0, 0.7) * u + rng.normal(0, 0.7) * v + np.array([0.0, 0.0, -0.40]))
            _append_spur(nodes, parents, radii, idx, direction, rng.uniform(0.08, 0.20), rng.uniform(0.0025, 0.0045))
    mesh = welded_tube_mesh(nodes, graph_from_parents(parents), radii, sides=8)
    return mesh, {
        "depth": 5,
        "layout": "downward fan with thick-to-thin root hierarchy",
        "root_nodes": root_node_count,
        "attached_root_hairs": len(nodes) - root_node_count,
        "connector_strategy": "every hair is a child edge sharing its parent root anchor",
    }


def lsystem_vine_graph(seed: int) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed)
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
        radii.append(max(0.048 * (0.88**level), 0.012))
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
    mesh = welded_tube_mesh(nodes, graph_from_parents(parents), radii, sides=8)
    return mesh, {
        "iterations": 6,
        "curl_step_radians": 0.82,
        "layout": "helical main vine with attached tendrils and welded leaf-like tubelets",
        "attached_leaf_cards": 0,
        "connector_strategy": "tendrils and leaf-like tubelets are child edges of the vine scaffold",
    }


def sc_graph(case: str, seed: int, mode: str) -> tuple[pb.Mesh, dict]:
    result = scb.grow_space_colonization(
        case=case,
        attractor_count=1250 if case != "root_vine" else 1350,
        iterations=215,
        influence_radius=0.24,
        kill_radius=0.055,
        step_size=0.045,
        seed=seed,
    )
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in result["nodes"]], 2.35)
    parents = [int(p) for p in result["parents"]]
    radii = _radii_from_parents(parents, base=0.052 if mode == "leaf" else 0.058, taper=0.82, floor=0.006)
    branch_node_count = len(nodes)
    rng = np.random.default_rng(seed + 71)
    child_map = _children(parents)
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    anchors = [i for i in range(1, branch_node_count) if (not child_map.get(i) or depths[i] >= max_depth * 0.65)]
    rng.shuffle(anchors)
    for idx in anchors[:95 if mode == "leaf" else 115]:
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(nodes[idx] - nodes[parent])
        u, v, _ = _basis(axis)
        direction_bias = np.array([0.0, 0.0, 0.12 if mode == "leaf" else -0.35])
        for _ in range(1 if mode == "leaf" else 2):
            direction = _unit(0.20 * axis + rng.normal(0, 0.75) * u + rng.normal(0, 0.75) * v + direction_bias)
            _append_spur(nodes, parents, radii, idx, direction, rng.uniform(0.055, 0.130), rng.uniform(0.0035, 0.0060))
    mesh = welded_tube_mesh(nodes, graph_from_parents(parents), radii, sides=8)
    controls = {
        "case": case,
        "attractor_count": 1250 if case != "root_vine" else 1350,
        "iterations": 215,
        "influence_radius": 0.24,
        "kill_radius": 0.055,
        "step_size": 0.045,
        "covered_attractors": result.get("covered_attractors"),
        "alive_attractors": result.get("alive_attractors"),
        "branch_nodes": branch_node_count,
        "attached_spurs": len(nodes) - branch_node_count,
        "attached_leaf_cards": 0,
        "connector_strategy": "SC node-parent graph plus terminal children sharing scaffold anchors",
    }
    return mesh, controls


def _nearest_parent_edges(points: np.ndarray, mode: str) -> list[tuple[int, int]]:
    if mode == "frontier_sheet":
        order = np.lexsort((points[:, 2], points[:, 0], points[:, 1]))
    else:
        order = np.argsort(np.linalg.norm(points, axis=1))
    inverse = np.empty(len(order), dtype=int)
    inverse[order] = np.arange(len(order))
    pts = points[order]
    edges: list[tuple[int, int]] = []
    for idx in range(1, len(pts)):
        prev = pts[:idx]
        parent = int(np.argmin(np.linalg.norm(prev - pts[idx], axis=1)))
        edges.append((int(order[parent]), int(order[idx])))
    return edges


def dla_graph(seed: int, mode: str, n_particles: int) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed)
    if mode == "frontier_sheet":
        pts = make_frontier_sheet(seed, particles=n_particles) * np.array([2.05, 1.45, 0.92])
    else:
        pts = pb.make_dla_cluster(n_particles=n_particles, seed=seed % 10000) * np.array([1.12, 1.04, 1.22])
    if len(pts) > n_particles:
        pts = pts[np.linspace(0, len(pts) - 1, n_particles).astype(int)]
    pts = _normalize_nodes([np.asarray(p, dtype=float) for p in pts], 2.35)
    edges = _nearest_parent_edges(np.asarray(pts), mode)
    radii: list[float] = []
    norms = np.linalg.norm(np.asarray(pts), axis=1)
    max_norm = max(float(norms.max()), 1e-6)
    for value in norms:
        frontier = float(value) / max_norm
        radii.append((0.041 if mode == "frontier_sheet" else 0.047) * (1.0 - 0.35 * frontier) + 0.012)
    original_nodes = len(pts)
    parents = [-1 for _ in pts]
    for a, b in edges:
        parents[b] = a
    child_map = _children(parents)
    tips = [i for i in range(original_nodes) if i != 0 and not child_map.get(i)]
    rng.shuffle(tips)
    for idx in tips[:150 if mode == "coral" else 95]:
        parent_candidates = [a for a, b in edges if b == idx]
        parent = parent_candidates[0] if parent_candidates else max(idx - 1, 0)
        axis = _unit(np.asarray(pts[idx]) - np.asarray(pts[parent]))
        u, v, _ = _basis(axis)
        for k in range(2 if mode == "coral" else 1):
            theta = 2.0 * math.pi * (k / 2.0) + rng.normal(0, 0.5)
            direction = _unit(0.45 * axis + math.cos(theta) * u + math.sin(theta) * v + rng.normal(0, 0.08, 3))
            pts.append(np.asarray(pts[idx]) + direction * rng.uniform(0.045, 0.105))
            radii.append(radii[idx] * rng.uniform(0.42, 0.62))
            edges.append((idx, len(pts) - 1))
    mesh = welded_tube_mesh(pts, edges, radii, sides=7)
    controls = {
        "mode": mode,
        "particles": int(n_particles),
        "base_attachment_edges": len(_dedupe_edges(edges[: max(original_nodes - 1, 0)])),
        "attached_frontier_tubelets": len(pts) - original_nodes,
        "surface_strategy": "explicit welded DLA attachment tubes; no global implicit surfacing",
        "connector_strategy": "nearest-parent bridge edge per particle plus attached terminal tubelets",
    }
    return mesh, controls


def radial_orbit_graph(order: int = 8, depth: int = 4) -> tuple[pb.Mesh, dict]:
    nodes: list[np.ndarray] = [np.array([0.0, 0.0, 0.0])]
    radii: list[float] = [0.070]
    edges: list[tuple[int, int]] = []
    previous_ring: list[int] = []
    ring_nodes_total = 0
    tooth_nodes = 0
    bridge_nodes = 0
    for level in range(depth):
        radius = 0.28 + level * 0.245
        z = 0.040 * level
        tube = max(0.035 * (0.84**level), 0.014)
        phase = 0.18 * level
        ring: list[int] = []
        ring_steps = order * 4
        for i in range(ring_steps):
            theta = 2.0 * math.pi * i / ring_steps + phase
            nodes.append(np.array([math.cos(theta) * radius, math.sin(theta) * radius, z]))
            radii.append(tube)
            ring.append(len(nodes) - 1)
        ring_nodes_total += len(ring)
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
    mesh = welded_tube_mesh(nodes, edges, radii, sides=8)
    return mesh, {
        "order": order,
        "depth": depth,
        "ring_nodes": ring_nodes_total,
        "tooth_nodes": tooth_nodes,
        "bridge_nodes": bridge_nodes,
        "connector_strategy": "shared center spine, closed ring cycles, radial teeth, and inter-depth bridge spokes",
    }


def _export_mesh(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


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
        for _ in range(500):
            c = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(0, 768))
            y = int(rng.integers(0, 768))
            if strokes == "needles":
                draw.line((x, y, x + int(rng.normal(0, 58)), y + int(rng.normal(-22, 48))), fill=c, width=int(rng.integers(1, 5)))
            elif strokes == "roots":
                draw.line((x, y, x + int(rng.normal(0, 82)), y + int(rng.normal(34, 44))), fill=c, width=int(rng.integers(2, 8)))
            elif strokes == "coral":
                r = int(rng.integers(5, 20))
                draw.ellipse((x - r, y - r, x + r, y + r), outline=c, width=int(rng.integers(2, 5)))
            elif strokes == "metal":
                r = int(rng.integers(8, 34))
                draw.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=c)
            else:
                draw.line((x, y, x + int(rng.normal(0, 80)), y + int(rng.normal(0, 80))), fill=c, width=5)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "conifer": save("v5_conifer_explicit_needles_guide.png", [(26, 48, 31), (56, 88, 47), (96, 118, 72), (92, 62, 35)], "needles"),
        "leaf": save("v5_leaf_vine_attached_lobes_guide.png", [(36, 72, 37), (86, 126, 57), (126, 96, 55), (53, 42, 28)], "needles"),
        "root": save("v5_root_explicit_hairs_guide.png", [(36, 27, 20), (78, 57, 36), (122, 90, 55), (23, 20, 16)], "roots"),
        "coral": save("v5_coral_tube_porosity_guide.png", [(112, 57, 53), (176, 94, 72), (226, 150, 101), (80, 42, 47)], "coral"),
        "gear": save("v5_radial_dark_metal_guide.png", [(34, 37, 34), (91, 97, 84), (158, 128, 76), (88, 42, 32)], "metal"),
    }


def _case_specs(seed: int) -> list[dict]:
    specs: list[dict] = []

    def add(case_id: str, family: str, target: str, recursive_mode: str, mesh: pb.Mesh, guide_key: str, case_seed: int, controls: dict, operators: list[str], why: str) -> None:
        specs.append(
            {
                "case_id": case_id,
                "family": family,
                "match_target": target,
                "traditional_target": target,
                "recursive_mode": recursive_mode,
                "mesh": mesh,
                "guide_key": guide_key,
                "seed": int(case_seed),
                "controls": controls,
                "operators": operators,
                "operator_composition": " -> ".join(operators),
                "why_matches_traditional": why,
                "strict_match_notes": why,
            }
        )

    mesh, ctl = layered_pine_graph(seed + 1)
    add(
        "v5_lsys_pine_canopy_d5_welded_whorl_needles",
        "L-system",
        "lsys_pine_canopy_d5",
        "symbolic pine rewriting with explicit whorl branches and attached needle scaffold",
        mesh,
        "conifer",
        seed + 101,
        ctl,
        ["symbolic_rewrite", "whorled_spine", "shared_anchor_tubes", "attached_needle_spurs", "anchored_needle_cards"],
        "Matches the traditional L-system pine by keeping depth-5 whorled trunk/branch recursion and replacing disconnected sprays with shared-anchor needle attachments.",
    )

    mesh, ctl = lsystem_root_graph(seed + 2)
    add(
        "v5_lsys_root_fan_d5_welded_hair_hierarchy",
        "L-system",
        "lsys_root_fan_d5",
        "symbolic root rewriting with welded thick-to-thin fan and attached hairs",
        mesh,
        "root",
        seed + 102,
        ctl,
        ["root_rewrite", "fan_spine", "shared_anchor_tubes", "attached_root_hairs"],
        "Matches the traditional L-system root target by preserving depth-5 root fan topology, downward tropism, taper, and connected hair attachment.",
    )

    mesh, ctl = lsystem_vine_graph(seed + 3)
    add(
        "v5_lsys_climbing_vine_d6_welded_leaf_tendrils",
        "L-system",
        "lsys_climbing_vine_d6",
        "curling vine rewrite with welded tendrils and anchored leaf lobes",
        mesh,
        "leaf",
        seed + 103,
        ctl,
        ["curl_rewrite", "main_vine_spine", "shared_anchor_tendrils", "anchored_leaf_lobes"],
        "Matches the traditional climbing vine by keeping the six-step helical main chain and recursive side tendrils while making leaves anchored to the vine scaffold.",
    )

    mesh, ctl = sc_graph("tree_canopy", seed + 11, "leaf")
    add(
        "v5_sc_tree_crown_260_welded_branch_leaf_shell",
        "Space colonization",
        "sc_tree_crown_260",
        "attractor competition crown with explicit branch graph and attached leaf shell",
        mesh,
        "leaf",
        seed + 111,
        ctl,
        ["attractor_competition", "node_parent_branch_spine", "terminal_attachment_scaffold", "anchored_leaf_lobes"],
        "Matches the traditional SC tree crown by using the same attractor competition mode and branch-parent graph, with terminal foliage attached through shared vertices rather than global smoothing.",
    )

    mesh, ctl = sc_graph("root_vine", seed + 12, "root")
    add(
        "v5_sc_root_network_260_welded_root_spurs",
        "Space colonization",
        "sc_root_network_260",
        "attractor competition root network with explicit branch graph and root spurs",
        mesh,
        "root",
        seed + 112,
        ctl,
        ["attractor_competition", "root_network_spine", "shared_anchor_root_spurs", "terminal_root_hairs"],
        "Matches the traditional SC root network by retaining attractor-driven root/vine growth and making every fine root a child of the main root scaffold.",
    )

    mesh, ctl = dla_graph(seed + 21, "coral", 900)
    add(
        "v5_dla_coral_cluster_900_welded_tube_frontier",
        "DLA/frontier",
        "dla_coral_cluster_900",
        "DLA nearest-attachment coral with explicit welded tube frontier",
        mesh,
        "coral",
        seed + 121,
        ctl,
        ["random_walk_support", "nearest_parent_bridge", "welded_coral_tubes", "terminal_tubelets"],
        "Matches the traditional DLA coral category by keeping stochastic accretive attachment order and frontier branches, but surfaces them as readable connected coral tubes.",
    )

    mesh, ctl = dla_graph(seed + 22, "frontier_sheet", 700)
    add(
        "v5_dla_frontier_sheet_700_welded_boundary_reef",
        "DLA/frontier",
        "dla_frontier_sheet_700",
        "line-seeded frontier sheet with explicit boundary bridges",
        mesh,
        "coral",
        seed + 122,
        ctl,
        ["line_seed_frontier", "nearest_parent_bridge", "sheet_spine", "attached_boundary_tubelets"],
        "Matches the traditional frontier sheet by preserving boundary-seeded growth and sheet silhouette while using explicit bridge edges instead of a blobby implicit sheet.",
    )

    mesh, ctl = radial_orbit_graph(8, 4)
    add(
        "v5_ifs_radial_ornament_o8_d4_welded_ring_spokes",
        "IFS/transform",
        "ifs_radial_ornament_o8_d4",
        "8-fold radial transform-copy ornament with welded rings, spokes, and teeth",
        mesh,
        "gear",
        seed + 132,
        ctl,
        ["radial_orbit", "closed_ring_cycles", "shared_center_spine", "inter_depth_bridges", "radial_teeth"],
        "Matches the traditional radial transform ornament by keeping order-8 repeated motifs and depth-4 scale levels, with explicit ring closure and bridge spokes for connectivity.",
    )
    return specs


def _metadata_for(spec: dict, mesh_path: Path, guide_path: str, metrics: dict) -> dict:
    return {
        "case_id": spec["case_id"],
        "family": spec["family"],
        "match_target": spec["match_target"],
        "traditional_target": spec["traditional_target"],
        "recursive_mode": spec["recursive_mode"],
        "remote_target": REMOTE_TARGET,
        "mesh_path": str(mesh_path),
        "guide_image": guide_path,
        "seed": spec["seed"],
        "operators": spec["operators"],
        "operator_composition": spec["operator_composition"],
        "controls": spec["controls"],
        "initial_mesh_metrics": metrics,
        "why_matches_traditional": spec["why_matches_traditional"],
        "strict_match_notes": spec["strict_match_notes"],
        "hybrid_design_note": "explicit recursive graph mesh with shared attachment vertices; no global implicit blob smoothing",
        "root_selection_log": {
            "root_source_type": "proxy_generated_mesh",
            "root_source_provenance": "assets/strict_visual_matched_cases_v5_hybrid_20260510.py local dry-run generator",
            "root_pool_size": 1,
            "root_generation_budget": "local CPU dry-run only; remote Trellis2 regeneration must be run on a100-2",
            "root_screening_budget": "no local manual cherry-pick; all emitted cases are representative V5 hybrid inputs",
            "selection_rank": 1,
            "projection_naturalization_schedule": spec["operators"],
            "readiness_label": "remote_input_dryrun",
            "connectivity_anchor_convention": _mesh_center_indices_for_nodes(),
        },
    }


def _write_readme(out_dir: Path, summary: dict) -> None:
    text = f"""# V5 Hybrid Strict Visual-Matched Cases Dry Run

This directory was produced locally by `assets/strict_visual_matched_cases_v5_hybrid_20260510.py`.

It is a dry-run input batch only. It does not contain remote Trellis2 outputs and it did not launch a job. The strict comparison regeneration target is `{REMOTE_TARGET}`.

V5 targets the weakest visual/connectivity cases with explicit shared-anchor graph meshes instead of global implicit blob smoothing.

Files:

- `manifest.csv` / `manifest.json`: case-level Trellis2 input manifest.
- `a100-2_cases.txt`: remote-ready lines in `case_id|mesh_path|guide_image|seed` format.
- `gpu2_cases.txt`: compatibility alias for scripts that consume GPU-group case lists.
- `initial_metrics.csv` / `initial_metrics.json`: pre-texture mesh metrics.
- each case folder: OBJ plus per-case metadata JSON.

Run locally:

```bash
python3 assets/strict_visual_matched_cases_v5_hybrid_20260510.py
```

Case count: {summary["num_cases"]}
"""
    (out_dir / "README.md").write_text(text, encoding="utf-8")


def materialize(root: Path, out_dir: Path, seed: int = 20260510) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    guides = _write_guides(out_dir)
    specs = _case_specs(seed)
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
            "traditional_target": spec["traditional_target"],
            "recursive_mode": spec["recursive_mode"],
            "mesh_path": str(mesh_path),
            "guide_image": guide_path,
            "metadata_path": str(metadata_path),
            "remote_target": REMOTE_TARGET,
            "gpu_group": 2,
            "seed": spec["seed"],
            "operators": json.dumps(spec["operators"], ensure_ascii=False),
            "operator_composition": spec["operator_composition"],
            "controls": json.dumps(spec["controls"], ensure_ascii=False, sort_keys=True),
            "why_matches_traditional": spec["why_matches_traditional"],
            "strict_match_notes": spec["strict_match_notes"],
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
    args = parser.parse_args()
    materialize(args.root, args.out or DEFAULT_OUT, seed=args.seed)


if __name__ == "__main__":
    main()
