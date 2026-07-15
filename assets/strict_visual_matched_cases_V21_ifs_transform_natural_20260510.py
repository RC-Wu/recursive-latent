#!/usr/bin/env python3
"""V21 strict IFS/transform/radial/lattice remote input generator.

V21 is a fresh strict matched branch for transform grammar cases that were not
covered cleanly by coral/crystal-focused V20.  It emits OBJ mesh inputs only,
plus PBR guide images and metadata for remote Trellis2 mesh/PBR generation on
a100-2 GPU 4/5/6/7.  The local dry run is only an input and connectivity gate:
no remote jobs are launched here, no local textured result is selected, and no
generated mesh is post-processed.
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

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import procedural_baselines as pb
import recursive_growth_mesh_metrics as rgm


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 100
CONNECTIVITY_LCR_MIN = 0.999
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V21_ifs_transform_natural_20260510_dryrun"

COMMON_OPERATORS = [
    "affine_transform_grammar",
    "recursive_copy_depth_schedule",
    "strict_traditional_target_mapping",
    "shared_vertex_connected_support",
    "attached_natural_mesh_detail",
    "obj_mesh_input_only",
    "pbr_material_prompt",
    "largest_component_gate",
]


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _basis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = _unit(np.asarray(axis, dtype=float))
    seed = np.array([0.0, 0.0, 1.0]) if abs(float(w[2])) < 0.90 else np.array([1.0, 0.0, 0.0])
    u = _unit(np.cross(w, seed))
    v = _unit(np.cross(w, u))
    return u, v, w


def _rot_axis(axis: np.ndarray, angle: float) -> np.ndarray:
    c = math.cos(angle)
    s = math.sin(angle)
    x, y, z = _unit(axis)
    return np.array(
        [
            [c + x * x * (1.0 - c), x * y * (1.0 - c) - z * s, x * z * (1.0 - c) + y * s],
            [y * x * (1.0 - c) + z * s, c + y * y * (1.0 - c), y * z * (1.0 - c) - x * s],
            [z * x * (1.0 - c) - y * s, z * y * (1.0 - c) + x * s, c + z * z * (1.0 - c)],
        ],
        dtype=float,
    )


def _normalize_nodes(nodes: list[np.ndarray], extent: float = 2.60) -> list[np.ndarray]:
    arr = np.asarray(nodes, dtype=float)
    mn = arr.min(axis=0)
    mx = arr.max(axis=0)
    center = (mn + mx) * 0.5
    scale = max(float((mx - mn).max()), 1e-6)
    return [(np.asarray(n, dtype=float) - center) * (extent / scale) for n in nodes]


def _dedupe_edges(edges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    seen: set[tuple[int, int]] = set()
    out: list[tuple[int, int]] = []
    for a, b in edges:
        if int(a) == int(b):
            continue
        key = (min(int(a), int(b)), max(int(a), int(b)))
        if key in seen:
            continue
        seen.add(key)
        out.append((int(a), int(b)))
    return out


def _append_node(
    nodes: list[np.ndarray],
    parents: list[int],
    radii: list[float],
    parent: int,
    direction: np.ndarray,
    length: float,
    radius: float,
) -> int:
    nodes.append(np.asarray(nodes[parent], dtype=float) + _unit(direction) * float(length))
    parents.append(int(parent))
    radii.append(float(radius))
    return len(nodes) - 1


def _edges_from_parents(parents: list[int]) -> list[tuple[int, int]]:
    return [(int(parent), int(idx)) for idx, parent in enumerate(parents) if int(parent) >= 0]


def _terminal_nodes(parents: list[int]) -> list[int]:
    children: dict[int, list[int]] = {i: [] for i in range(len(parents))}
    for idx, parent in enumerate(parents):
        if parent >= 0:
            children.setdefault(int(parent), []).append(int(idx))
    return [i for i in range(1, len(parents)) if not children.get(i)]


def _connected_support_mesh(nodes: list[np.ndarray], edges: list[tuple[int, int]], radii: list[float], sides: int = 10) -> pb.Mesh:
    """Create a face-connected support by sharing one scaffold vertex per node."""

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
        if float(np.linalg.norm(axis)) < 1e-8:
            continue
        u, v, _w = _basis(axis)
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
            slot = ridx % sides
            mesh.faces.append((ring[slot], ring[(slot + 1) % sides], next_ring[slot]))
            mesh.faces.append((ring[(slot + 1) % sides], next_ring[(slot + 1) % sides], next_ring[slot]))

    setattr(mesh, "center_indices", center_indices)
    return mesh


def _add_card(mesh: pb.Mesh, anchor_idx: int, anchor: np.ndarray, normal: np.ndarray, scale: float, aspect: float) -> None:
    u, v, _w = _basis(normal)
    c = np.asarray(anchor, dtype=float) + _unit(normal) * float(scale) * 0.82
    a = float(scale) * float(aspect)
    b = float(scale)
    base = len(mesh.vertices)
    mesh.vertices.extend([tuple(c + u * a), tuple(c + v * b), tuple(c - u * a), tuple(c - v * b)])
    for i in range(4):
        j = (i + 1) % 4
        mesh.faces.append((anchor_idx, base + i + 1, base + j + 1))
        mesh.faces.append((anchor_idx, base + j + 1, base + i + 1))


def _add_plate(
    mesh: pb.Mesh,
    anchor_idx: int,
    center: np.ndarray,
    normal: np.ndarray,
    radius: float,
    thickness: float,
    sides: int = 6,
) -> None:
    u, v, w = _basis(normal)
    center = np.asarray(center, dtype=float)
    base = len(mesh.vertices)
    top: list[int] = []
    bottom: list[int] = []
    for layer, offset in ((top, thickness * 0.5), (bottom, -thickness * 0.5)):
        for i in range(sides):
            theta = 2.0 * math.pi * i / sides
            r = float(radius) * (0.82 if i % 2 else 1.0)
            p = center + u * math.cos(theta) * r + v * math.sin(theta) * r + w * offset
            mesh.vertices.append(tuple(p))
            layer.append(len(mesh.vertices))
    top_center = len(mesh.vertices) + 1
    bottom_center = len(mesh.vertices) + 2
    mesh.vertices.append(tuple(center + w * thickness * 0.5))
    mesh.vertices.append(tuple(center - w * thickness * 0.5))
    for i in range(sides):
        j = (i + 1) % sides
        mesh.faces.append((top_center, top[i], top[j]))
        mesh.faces.append((bottom_center, bottom[j], bottom[i]))
        mesh.faces.append((top[i], bottom[i], top[j]))
        mesh.faces.append((top[j], bottom[i], bottom[j]))
    mesh.faces.append((anchor_idx, base + 1, base + 2))
    mesh.faces.append((anchor_idx, base + 2, top_center))


def _add_box(
    mesh: pb.Mesh,
    anchor_idx: int,
    center: np.ndarray,
    axes: tuple[np.ndarray, np.ndarray, np.ndarray],
    half_extents: tuple[float, float, float],
) -> None:
    u, v, w = (_unit(np.asarray(a, dtype=float)) for a in axes)
    hx, hy, hz = (float(x) for x in half_extents)
    center = np.asarray(center, dtype=float)
    corners = [
        center + sx * u * hx + sy * v * hy + sz * w * hz
        for sx, sy, sz in (
            (-1, -1, -1),
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, 1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, 1, 1),
        )
    ]
    base = len(mesh.vertices)
    mesh.vertices.extend([tuple(p) for p in corners])
    faces = [
        (1, 2, 3),
        (1, 3, 4),
        (5, 8, 7),
        (5, 7, 6),
        (1, 5, 6),
        (1, 6, 2),
        (2, 6, 7),
        (2, 7, 3),
        (3, 7, 8),
        (3, 8, 4),
        (4, 8, 5),
        (4, 5, 1),
    ]
    for f in faces:
        mesh.faces.append(tuple(base + i for i in f))
    mesh.faces.append((anchor_idx, base + 1, base + 2))
    mesh.faces.append((anchor_idx, base + 2, base + 6))
    mesh.faces.append((anchor_idx, base + 6, base + 5))


def _add_edge_panels(
    mesh: pb.Mesh,
    nodes: list[np.ndarray],
    edges: list[tuple[int, int]],
    max_panels: int,
    width: float,
    lift: float,
    faceted: bool,
) -> int:
    centers = getattr(mesh, "center_indices")
    placed = 0
    sample = _dedupe_edges(edges)
    step = max(len(sample) // max(max_panels, 1), 1)
    for a, b in sample[::step]:
        if placed >= max_panels:
            break
        pa = np.asarray(nodes[a], dtype=float)
        pb_ = np.asarray(nodes[b], dtype=float)
        axis = pb_ - pa
        if float(np.linalg.norm(axis)) < 1e-8:
            continue
        u, v, w = _basis(axis)
        normal = _unit(v + np.array([0.0, 0.0, lift]))
        center = pa * 0.45 + pb_ * 0.55 + normal * float(width) * 0.55
        if faceted:
            _add_plate(mesh, centers[a], center, normal, radius=width, thickness=width * 0.20, sides=6)
        else:
            _add_card(mesh, centers[a], center, normal + 0.25 * w, scale=width * 0.72, aspect=2.2)
        placed += 1
    return placed


def _surface_area(vertices: np.ndarray, faces: np.ndarray) -> float:
    if len(vertices) == 0 or len(faces) == 0:
        return 0.0
    tri = vertices[faces]
    return float(np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1).sum() * 0.5)


def _finalize_controls(base: dict, nodes: list[np.ndarray], edges: list[tuple[int, int]], detail_count: int) -> dict:
    controls = dict(base)
    controls.update(
        {
            "mesh_input_format": "obj",
            "connected_support": True,
            "connectivity_gate_lcr_min": CONNECTIVITY_LCR_MIN,
            "shared_vertex_anchor_count": int(len(nodes)),
            "support_edge_count": int(len(_dedupe_edges(edges))),
            "attached_natural_mesh_detail_count": int(detail_count),
            "direct_voxel_blocks": False,
            "detached_chunk_policy": "forbid_detached_transform_islands_by_shared_support_faces",
        }
    )
    return controls


def ifs_branch_tree_case(seed: int, depth: int = 6) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 211)
    nodes = [np.array([0.0, 0.0, -1.0], dtype=float)]
    parents = [-1]
    radii = [0.086]

    def rec(parent: int, direction: np.ndarray, length: float, radius: float, level: int, phase: float) -> None:
        current = _append_node(nodes, parents, radii, parent, direction, length, max(radius, 0.007))
        if level <= 1:
            return
        u, _v, w = _basis(direction)
        transforms = [(-0.52, phase), (0.42, phase + 2.18), (0.24, phase + 4.35)]
        scales = [0.70, 0.66, 0.54]
        for (angle, twist), scale in zip(transforms, scales):
            twist_axis = math.cos(twist) * u + math.sin(twist) * np.cross(w, u)
            child = _unit(math.cos(angle) * w + math.sin(angle) * _unit(twist_axis) + rng.normal(0.0, 0.022, 3))
            rec(current, child, length * (scale + rng.uniform(-0.018, 0.018)), radius * 0.70, level - 1, phase + 0.79)

    rec(0, np.array([0.0, 0.0, 1.0]), 0.46, 0.074, depth, 0.0)
    nodes = _normalize_nodes(nodes, 2.70)
    edges = _edges_from_parents(parents)
    mesh = _connected_support_mesh(nodes, edges, radii, sides=11)
    centers = getattr(mesh, "center_indices")
    details = 0
    for idx in _terminal_nodes(parents):
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(nodes[idx] - nodes[parent])
        _add_card(mesh, centers[idx], nodes[idx], axis + np.array([0.0, 0.0, 0.16]), scale=0.034, aspect=2.6)
        details += 1
    details += _add_edge_panels(mesh, nodes, edges, max_panels=96, width=0.044, lift=0.18, faceted=False)
    controls = _finalize_controls(
        {
            "semantic_motif": "fractal_branch_ifs_tree",
            "recursive_depth": depth,
            "affine_transform_count": 3,
            "transform_compatibility_label": "positive",
            "compatible_transform_stack": True,
            "ifs_rule": "T0 trunk; {scale, rotate, translate}^d with three contracted branch maps",
            "surface_strategy": "tapered shared-support IFS branch tree with attached terminal cards and bark-like panels",
        },
        nodes,
        edges,
        details,
    )
    return mesh, controls


def radial_ornament_case(order: int = 12, depth: int = 5) -> tuple[pb.Mesh, dict]:
    nodes: list[np.ndarray] = [np.zeros(3, dtype=float)]
    radii: list[float] = [0.076]
    edges: list[tuple[int, int]] = []
    previous_ring: list[int] = []
    detail_nodes = 0
    bridge_count = 0
    ring_steps = order * 6
    for level in range(depth):
        radius = 0.24 + level * 0.185
        z = 0.035 * math.sin(level * 0.9)
        tube = max(0.044 * (0.84**level), 0.012)
        phase = level * math.pi / order
        ring: list[int] = []
        for i in range(ring_steps):
            theta = 2.0 * math.pi * i / ring_steps + phase
            scallop = 1.0 + 0.055 * math.cos(theta * order)
            nodes.append(np.array([math.cos(theta) * radius * scallop, math.sin(theta) * radius * scallop, z]))
            radii.append(tube)
            ring.append(len(nodes) - 1)
        for i, idx in enumerate(ring):
            edges.append((idx, ring[(i + 1) % len(ring)]))
            if i % 6 == 0:
                edges.append((0, idx))
                bridge_count += 1
                direction = _unit(nodes[idx] + np.array([0.0, 0.0, 0.12]))
                nodes.append(nodes[idx] + direction * (0.095 + 0.010 * (depth - level)))
                radii.append(tube * 0.46)
                edges.append((idx, len(nodes) - 1))
                detail_nodes += 1
                if previous_ring:
                    edges.append((previous_ring[i % len(previous_ring)], idx))
                    bridge_count += 1
        previous_ring = ring
    mesh = _connected_support_mesh(nodes, edges, radii, sides=8)
    details = detail_nodes + bridge_count
    details += _add_edge_panels(mesh, nodes, edges, max_panels=132, width=0.044, lift=0.06, faceted=True)
    controls = _finalize_controls(
        {
            "semantic_motif": "radial_ornament",
            "recursive_depth": depth,
            "affine_transform_count": order,
            "radial_order": order,
            "bridged_ring_count": depth,
            "small_bridge_count": bridge_count,
            "transform_compatibility_label": "positive",
            "compatible_transform_stack": True,
            "ifs_rule": "R_k radial rotations with contracted ring copies and spoke bridges for each recursion level",
            "surface_strategy": "connected radial IFS ornament with recursive rings, spokes, teeth, and metallic facet plates",
        },
        nodes,
        edges,
        details,
    )
    return mesh, controls


def pyrite_lattice_case(depth: int = 4) -> tuple[pb.Mesh, dict]:
    nodes: list[np.ndarray] = [np.zeros(3, dtype=float)]
    radii: list[float] = [0.070]
    edges: list[tuple[int, int]] = []
    frontier = [0]
    directions = [
        np.array([1.0, 0.0, 0.22]),
        np.array([-1.0, 0.0, 0.22]),
        np.array([0.0, 1.0, 0.22]),
        np.array([0.0, -1.0, 0.22]),
        np.array([0.0, 0.0, 1.0]),
        np.array([0.0, 0.0, -0.86]),
    ]
    bridge_count = 0
    for level in range(depth):
        next_frontier: list[int] = []
        step = 0.50 * (0.66**level)
        for parent in frontier:
            children: list[int] = []
            for direction in directions:
                point = np.asarray(nodes[parent], dtype=float) + _unit(direction) * step
                nodes.append(point)
                radii.append(max(0.048 * (0.78**level), 0.012))
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
    nodes = _normalize_nodes(nodes, 2.48)
    mesh = _connected_support_mesh(nodes, edges, radii, sides=7)
    centers = getattr(mesh, "center_indices")
    details = bridge_count
    sample = list(range(1, len(nodes), max(len(nodes) // 96, 1)))
    for idx in sample[:96]:
        anchor = nodes[idx]
        u, v, w = _basis(anchor if np.linalg.norm(anchor) > 1e-8 else np.array([0.0, 0.0, 1.0]))
        snapped = np.round(np.asarray(anchor, dtype=float) / 0.085) * 0.085
        _add_box(mesh, centers[idx], snapped, (u, v, w), (0.040, 0.040, 0.032))
        details += 1
    details += _add_edge_panels(mesh, nodes, edges, max_panels=90, width=0.040, lift=0.12, faceted=True)
    controls = _finalize_controls(
        {
            "semantic_motif": "pyrite_lattice_transform",
            "recursive_depth": depth,
            "affine_transform_count": 6,
            "small_bridge_count": bridge_count,
            "facet_cube_count": len(sample[:96]),
            "transform_compatibility_label": "positive",
            "compatible_transform_stack": True,
            "ifs_rule": "six signed-axis affine copies with scale contraction and local copy bridges",
            "surface_strategy": "pyrite-like connected lattice with snapped cubic facets and recursive copy bridges",
        },
        nodes,
        edges,
        details,
    )
    return mesh, controls


def bismuth_stepped_case(depth: int = 5) -> tuple[pb.Mesh, dict]:
    nodes: list[np.ndarray] = []
    radii: list[float] = []
    edges: list[tuple[int, int]] = []
    previous_loop: list[int] = []
    segments = 9
    for level in range(depth):
        scale = 1.12 * (0.80**level)
        z = -0.20 + level * 0.105
        loop: list[int] = []
        for side in range(4):
            start = np.array(
                [
                    math.cos(side * math.pi / 2.0) * scale + math.cos((side + 1) * math.pi / 2.0) * scale,
                    math.sin(side * math.pi / 2.0) * scale + math.sin((side + 1) * math.pi / 2.0) * scale,
                    z,
                ],
                dtype=float,
            )
            end = np.array(
                [
                    math.cos((side + 1) * math.pi / 2.0) * scale + math.cos((side + 2) * math.pi / 2.0) * scale,
                    math.sin((side + 1) * math.pi / 2.0) * scale + math.sin((side + 2) * math.pi / 2.0) * scale,
                    z,
                ],
                dtype=float,
            )
            for j in range(segments):
                t = j / float(segments)
                nodes.append(start * (1.0 - t) + end * t)
                radii.append(max(0.046 * (0.83**level), 0.014))
                loop.append(len(nodes) - 1)
        for i, idx in enumerate(loop):
            edges.append((idx, loop[(i + 1) % len(loop)]))
            if previous_loop and i % 3 == 0:
                edges.append((idx, previous_loop[i % len(previous_loop)]))
        previous_loop = loop
    nodes = _normalize_nodes(nodes, 2.58)
    mesh = _connected_support_mesh(nodes, edges, radii, sides=8)
    centers = getattr(mesh, "center_indices")
    details = 0
    for idx in range(0, len(nodes), 2):
        anchor = nodes[idx]
        z_axis = np.array([0.0, 0.0, 1.0])
        tangent = _unit(np.array([-anchor[1], anchor[0], 0.0]))
        radial = _unit(np.array([anchor[0], anchor[1], 0.12]))
        _add_box(mesh, centers[idx], np.asarray(anchor) + z_axis * 0.018, (tangent, radial, z_axis), (0.058, 0.034, 0.011))
        details += 1
    details += _add_edge_panels(mesh, nodes, edges, max_panels=88, width=0.038, lift=0.18, faceted=True)
    controls = _finalize_controls(
        {
            "semantic_motif": "bismuth_stepped_transform",
            "recursive_depth": depth,
            "affine_transform_count": 4,
            "terrace_level_count": depth,
            "stepped_slab_count": details,
            "transform_compatibility_label": "positive",
            "compatible_transform_stack": True,
            "ifs_rule": "four square-loop affine copies with contracted scale and upward terrace translation",
            "surface_strategy": "connected bismuth transform terraces with iridescent slab facets and loop bridges",
        },
        nodes,
        edges,
        details,
    )
    return mesh, controls


def escher_stair_loop_case(depth: int = 4) -> tuple[pb.Mesh, dict]:
    nodes: list[np.ndarray] = []
    radii: list[float] = []
    edges: list[tuple[int, int]] = []
    loops: list[list[int]] = []
    steps_per_side = 8
    for level in range(depth):
        scale = 1.12 * (0.76**level)
        z0 = -0.36 + level * 0.11
        loop: list[int] = []
        corners = [
            np.array([-scale, -scale, z0]),
            np.array([scale, -scale, z0 + 0.18]),
            np.array([scale, scale, z0 + 0.36]),
            np.array([-scale, scale, z0 + 0.54]),
        ]
        for side in range(4):
            start = corners[side]
            end = corners[(side + 1) % 4]
            if side == 3:
                end = np.array([-scale, -scale, z0 + 0.72])
            for j in range(steps_per_side):
                t = j / float(steps_per_side)
                p = start * (1.0 - t) + end * t
                nodes.append(p)
                radii.append(max(0.042 * (0.82**level), 0.012))
                loop.append(len(nodes) - 1)
        for i, idx in enumerate(loop):
            edges.append((idx, loop[(i + 1) % len(loop)]))
            if level > 0 and i % 4 == 0:
                edges.append((idx, loops[level - 1][i % len(loops[level - 1])]))
        loops.append(loop)
    nodes = _normalize_nodes(nodes, 2.66)
    mesh = _connected_support_mesh(nodes, edges, radii, sides=8)
    centers = getattr(mesh, "center_indices")
    details = 0
    for loop in loops:
        for idx in loop[::2]:
            anchor = nodes[idx]
            tangent = _unit(nodes[loop[(loop.index(idx) + 1) % len(loop)]] - nodes[idx])
            side = _unit(np.cross(tangent, np.array([0.0, 0.0, 1.0])))
            normal = _unit(np.cross(side, tangent))
            _add_box(mesh, centers[idx], np.asarray(anchor) + normal * 0.020, (tangent, side, normal), (0.070, 0.045, 0.012))
            details += 1
    details += _add_edge_panels(mesh, nodes, edges, max_panels=68, width=0.036, lift=0.20, faceted=True)
    controls = _finalize_controls(
        {
            "semantic_motif": "escher_recursive_stair_loop",
            "recursive_depth": depth,
            "affine_transform_count": 4,
            "stair_loop_count": depth,
            "view_dependent_impossible_loop": True,
            "transform_compatibility_label": "positive",
            "compatible_transform_stack": True,
            "ifs_rule": "four contracted stair-loop transforms with vertical phase offset and recursive inner loops",
            "surface_strategy": "connected recursive stair loop; impossible-loop read is view-dependent while mesh remains physically connected",
        },
        nodes,
        edges,
        details,
    )
    return mesh, controls


def transform_compat_case(seed: int, compatible: bool, depth: int = 4) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + (401 if compatible else 499))
    nodes = [np.array([0.0, 0.0, -0.95], dtype=float)]
    parents = [-1]
    radii = [0.074]
    frontier = [0]
    transforms = 3 if compatible else 4
    for level in range(depth):
        next_frontier: list[int] = []
        scale = 0.42 * (0.72**level)
        for parent in frontier:
            base_axis = _unit(np.asarray(nodes[parent]) + np.array([0.0, 0.0, 1.30]))
            u, v, w = _basis(base_axis)
            for k in range(transforms):
                if compatible:
                    angle = 2.0 * math.pi * k / transforms + 0.12 * level
                    direction = _unit(0.58 * w + math.cos(angle) * u + math.sin(angle) * v)
                    radius = max(0.045 * (0.80**level), 0.011)
                else:
                    angle = (k * 1.37 + level * 0.51) % (2.0 * math.pi)
                    shear = np.array([0.24 * math.sin(level + k), -0.18 * math.cos(2.0 * k), 0.16 * (-1) ** k])
                    direction = _unit((math.cos(angle) * u + math.sin(angle) * v) * (1.0 + 0.16 * k) + 0.36 * w + shear)
                    radius = max(0.044 * (0.76**level) * (1.0 + 0.05 * ((k + level) % 2)), 0.010)
                child = _append_node(nodes, parents, radii, parent, direction + rng.normal(0.0, 0.014, 3), scale, radius)
                next_frontier.append(child)
        frontier = next_frontier if compatible else next_frontier[1::2] or next_frontier
    nodes = _normalize_nodes(nodes, 2.48)
    edges = _edges_from_parents(parents)
    if not compatible:
        for i in range(2, len(nodes), 5):
            edges.append((i - 1, i))
    mesh = _connected_support_mesh(nodes, edges, radii, sides=9 if compatible else 8)
    centers = getattr(mesh, "center_indices")
    details = 0
    for idx in range(1, len(nodes), 3 if compatible else 2):
        axis = _unit(nodes[idx] - nodes[parents[idx]]) if parents[idx] >= 0 else np.array([0.0, 0.0, 1.0])
        if compatible:
            _add_plate(mesh, centers[idx], np.asarray(nodes[idx]) + axis * 0.022, axis, radius=0.038, thickness=0.010, sides=6)
        else:
            u, v, w = _basis(axis + np.array([0.14, -0.21, 0.08]))
            _add_box(mesh, centers[idx], np.asarray(nodes[idx]) + w * 0.024, (u, v, w), (0.043, 0.028, 0.017))
        details += 1
    details += _add_edge_panels(mesh, nodes, edges, max_panels=76, width=0.038, lift=0.12, faceted=True)
    label = "transform_compat_positive" if compatible else "transform_compat_negative"
    controls = _finalize_controls(
        {
            "semantic_motif": label,
            "recursive_depth": depth,
            "affine_transform_count": transforms,
            "transform_compatibility_label": "positive" if compatible else "negative",
            "compatible_transform_stack": bool(compatible),
            "axis_mismatch_control": not bool(compatible),
            "ifs_rule": (
                "commuting rotation-scale affine stack with shared source and target axes"
                if compatible
                else "non-commuting anisotropic rotation-scale stack; intentionally mismatched axes for negative compatibility control"
            ),
            "surface_strategy": (
                "compatible transform stack with aligned repeated copy plates"
                if compatible
                else "negative transform compatibility control with connected but axis-mismatched copy modules"
            ),
        },
        nodes,
        edges,
        details,
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
        for _ in range(780):
            c = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(34, 734))
            y = int(rng.integers(34, 734))
            if motif == "branch":
                width = int(rng.integers(2, 7))
                draw.line((x, y, x + int(rng.normal(0, 72)), y + int(rng.normal(-34, 68))), fill=c, width=width)
                if rng.random() < 0.55:
                    rr = int(rng.integers(4, 10))
                    draw.ellipse((x - rr, y - rr, x + rr, y + rr), outline=c, width=2)
            elif motif == "radial":
                r = int(rng.integers(16, 70))
                draw.ellipse((x - r, y - r, x + r, y + r), outline=c, width=int(rng.integers(2, 5)))
                for k in range(3):
                    a = 2.0 * math.pi * (k / 3.0 + rng.random())
                    draw.line((x, y, x + int(math.cos(a) * r), y + int(math.sin(a) * r)), fill=c, width=2)
            elif motif == "pyrite":
                r = int(rng.integers(12, 42))
                draw.rectangle((x - r, y - r, x + r, y + r), outline=c, width=int(rng.integers(2, 5)))
                draw.line((x - r, y, x + r, y), fill=c, width=1)
                draw.line((x, y - r, x, y + r), fill=c, width=1)
            elif motif == "bismuth":
                r = int(rng.integers(18, 62))
                for k in range(5):
                    off = k * 5
                    if x - r + off <= x + r - off and y - r + off <= y + r - off:
                        draw.rectangle((x - r + off, y - r + off, x + r - off, y + r - off), outline=c, width=2)
            elif motif == "stairs":
                r = int(rng.integers(12, 40))
                draw.line((x - r, y - r, x + r, y - r, x + r, y + r, x - r, y + r, x - r, y - r), fill=c, width=3)
                draw.line((x - r, y, x, y, x, y + r), fill=c, width=2)
            else:
                r = int(rng.integers(8, 36))
                pts = [(x, y - r), (x + r, y - r // 4), (x + r // 2, y + r), (x - r, y + r // 5)]
                draw.polygon(pts, outline=c)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "branch": save("V21_ifs_branch_tree_bark_pbr_guide.png", (36, 38, 30), [(104, 78, 48), (154, 112, 68), (72, 108, 58), (196, 170, 110)], "branch"),
        "radial": save("V21_radial_ornament_burnished_pbr_guide.png", (38, 40, 42), [(196, 166, 92), (124, 132, 142), (96, 68, 58), (224, 210, 154)], "radial"),
        "pyrite": save("V21_pyrite_lattice_faceted_pbr_guide.png", (52, 48, 42), [(238, 204, 96), (180, 132, 54), (92, 82, 68), (252, 232, 140)], "pyrite"),
        "bismuth": save("V21_bismuth_stepped_iridescent_pbr_guide.png", (50, 56, 66), [(86, 206, 210), (220, 112, 214), (236, 190, 72), (116, 136, 238)], "bismuth"),
        "stairs": save("V21_escher_recursive_stairs_stone_pbr_guide.png", (48, 47, 43), [(156, 146, 126), (98, 94, 86), (204, 190, 162), (74, 78, 84)], "stairs"),
        "compat": save("V21_transform_compat_aligned_pbr_guide.png", (38, 44, 46), [(98, 150, 162), (184, 190, 142), (76, 88, 96), (214, 216, 172)], "compat"),
        "mismatch": save("V21_transform_compat_negative_mismatch_pbr_guide.png", (44, 40, 46), [(176, 86, 104), (86, 122, 164), (210, 180, 90), (92, 76, 94)], "compat"),
    }


def _case_specs(seed: int) -> list[dict]:
    specs: list[dict] = []

    def add(
        case_id: str,
        traditional_target: str,
        mesh: pb.Mesh,
        guide_key: str,
        case_seed: int,
        controls: dict,
        grammar_target_symbol: str,
        grammar_mapping: dict,
        material_prompt: str,
        why: str,
        gpu: int,
        role: str = "priority_a100_2",
    ) -> None:
        operators = list(COMMON_OPERATORS)
        if controls.get("transform_compatibility_label") == "negative":
            operators.append("negative_transform_compatibility_control")
        specs.append(
            {
                "case_id": case_id,
                "family": "IFS/transform",
                "match_target": traditional_target,
                "traditional_target": traditional_target,
                "recursive_mode": controls["ifs_rule"],
                "mesh": mesh,
                "guide_key": guide_key,
                "seed": int(case_seed),
                "controls": controls,
                "operators": operators,
                "operator_composition": " -> ".join(operators),
                "grammar_target_symbol": grammar_target_symbol,
                "grammar_mapping": grammar_mapping,
                "material_prompt": material_prompt,
                "why_matches_traditional": why,
                "strict_match_notes": why,
                "gpu": int(gpu),
                "case_role": role,
            }
        )

    mesh, controls = ifs_branch_tree_case(seed + 1, depth=6)
    add(
        "V21_ifs_branch_tree_d6_natural_bark",
        "ifs_branch_tree_d6",
        mesh,
        "branch",
        seed + 2101,
        controls,
        "F -> T_branch(F)^3",
        {
            "copy_operator": "three contracted branch maps",
            "traditional_parameter_lock": "depth=6, three branch transforms, taper schedule preserved",
            "surface_upgrade": "natural bark/leaf details attached to the same IFS skeleton",
        },
        "natural fractal branch IFS PBR, bark ridges, tapered recursive limbs, restrained terminal foliage",
        "Strict branch-tree IFS target: same depth-6 affine branch copies, upgraded to connected natural mesh detail without rod-only supports.",
        4,
    )

    mesh, controls = radial_ornament_case(order=12, depth=5)
    add(
        "V21_ifs_radial_ornament_o12_d5_burnished",
        "ifs_radial_ornament_o12_d5",
        mesh,
        "radial",
        seed + 2102,
        controls,
        "O -> union_k R_k S(O)",
        {
            "copy_operator": "12-fold radial rotations with scale-contracted rings",
            "traditional_parameter_lock": "order=12, depth=5, spokes and ring bridges",
            "surface_upgrade": "burnished ornamental metal facets attached to rings",
        },
        "radial ornament PBR, burnished metal, carved recursive rings, small facet inlays",
        "Strict radial transform target: order-12/depth-5 ring copies and spokes remain one-to-one while bridge faces prevent fragmented radial islands.",
        5,
    )

    mesh, controls = pyrite_lattice_case(depth=4)
    add(
        "V21_ifs_pyrite_lattice_transform_d4_faceted",
        "ifs_pyrite_lattice_transform_d4",
        mesh,
        "pyrite",
        seed + 2103,
        controls,
        "L -> union_axis T_axis S(L)",
        {
            "copy_operator": "six signed-axis lattice copies with scale contraction",
            "traditional_parameter_lock": "depth=4, signed-axis transform set, copy bridges",
            "surface_upgrade": "snapped pyrite cube facets attached to lattice anchors",
        },
        "metallic pyrite PBR, cubic lattice, sharp gold facets, rough mineral anisotropy",
        "Strict lattice/pyrite transform target: affine lattice copies are connected by copy bridges and carry pyrite-like cubic facets.",
        6,
    )

    mesh, controls = bismuth_stepped_case(depth=5)
    add(
        "V21_ifs_bismuth_stepped_transform_d5_iridescent",
        "ifs_bismuth_stepped_transform_d5",
        mesh,
        "bismuth",
        seed + 2104,
        controls,
        "B -> T_z S(square_loop(B))",
        {
            "copy_operator": "contracted square-loop transforms with upward terrace translation",
            "traditional_parameter_lock": "depth=5, four loop maps, terrace scale schedule",
            "surface_upgrade": "iridescent bismuth slabs attached to the loop support",
        },
        "iridescent bismuth PBR, stepped square terraces, oxide rainbow edges, sharp ledges",
        "Strict bismuth stepped transform target: recursive square-loop terraces are preserved and upgraded with connected slab facets.",
        7,
    )

    mesh, controls = escher_stair_loop_case(depth=4)
    add(
        "V21_ifs_escher_recursive_stair_loop_d4_viewlocked",
        "ifs_escher_recursive_stair_loop_d4",
        mesh,
        "stairs",
        seed + 2105,
        controls,
        "E -> stair_loop(E) with contracted inner copies",
        {
            "copy_operator": "four stair-loop transforms with vertical phase offset",
            "traditional_parameter_lock": "depth=4 nested stair loops and loop closure",
            "surface_upgrade": "stone stair treads attached to a connected support",
            "feasibility_note": "impossible-loop read is view-dependent; the actual OBJ remains physically connected",
        },
        "Escher-like recursive stair loop PBR, matte stone treads, view-dependent impossible staircase, connected mesh",
        "Strict recursive-stairs transform target when feasible: preserves nested stair-loop grammar and documents the view-dependent impossible-loop assumption.",
        4,
    )

    mesh, controls = transform_compat_case(seed + 6, compatible=True, depth=4)
    add(
        "V21_transform_compat_positive_affine_stack_d4",
        "transform_compat_positive_affine_stack_d4",
        mesh,
        "compat",
        seed + 2106,
        controls,
        "C+ -> commuting affine stack",
        {
            "copy_operator": "commuting rotation-scale maps with shared axes",
            "traditional_parameter_lock": "depth=4 compatible transform stack",
            "surface_upgrade": "aligned copy plates show transform compatibility",
        },
        "aligned transform stack PBR, satin ceramic-metal facets, coherent repeated affine modules",
        "Positive transform-compatibility target: source and target axes share a commuting affine stack, so the generated mesh should remain grammar-compatible.",
        5,
    )

    mesh, controls = transform_compat_case(seed + 7, compatible=False, depth=4)
    add(
        "V21_transform_compat_negative_axis_mismatch_d4",
        "transform_compat_negative_axis_mismatch_d4",
        mesh,
        "mismatch",
        seed + 2107,
        controls,
        "C- -> noncommuting mismatched affine stack",
        {
            "copy_operator": "non-commuting anisotropic scale and axis-mismatched rotations",
            "traditional_parameter_lock": "depth=4 negative compatibility control",
            "surface_upgrade": "mismatched modules remain connected but are not claimed as compatible",
        },
        "negative transform compatibility control PBR, connected mismatched modules, anisotropic facets, no detached shards",
        "Negative transform-compatibility control: still an OBJ mesh/PBR input, but metadata marks the axis mismatch so it is not counted as a positive grammar match.",
        6,
        role="negative_control_a100_2",
    )

    return specs


def _export_mesh(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


def _mesh_stats(path: Path, controls: dict) -> dict:
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
        "attached_natural_mesh_detail_count": int(controls.get("attached_natural_mesh_detail_count", 0)),
        "shared_vertex_anchor_count": int(controls.get("shared_vertex_anchor_count", 0)),
        "support_edge_count": int(controls.get("support_edge_count", 0)),
        "recursive_depth": int(controls.get("recursive_depth", 0)),
        "affine_transform_count": int(controls.get("affine_transform_count", 0)),
    }


def _grammar_mapping_for(spec: dict) -> dict:
    mapping = dict(spec["grammar_mapping"])
    return {
        "grammar_family": "IFS/transform grammar",
        "target_symbol": spec["grammar_target_symbol"],
        "operator_to_traditional_mapping": mapping,
        "controls": {
            "recursive_depth": spec["controls"].get("recursive_depth"),
            "affine_transform_count": spec["controls"].get("affine_transform_count"),
            "semantic_motif": spec["controls"].get("semantic_motif"),
        },
        "remote_comparison_unit": "one generated OBJ input to one traditional target",
        "strictness_note": "same target category and transform grammar are recorded per case; negative compatibility control is explicitly labeled.",
    }


def _metadata_for(spec: dict, mesh_path: Path, guide_path: str, metrics: dict) -> dict:
    operator_family = "traditional IFS/radial/lattice affine transform-copy recursion"
    expected_compatible = bool(spec["controls"].get("compatible_transform_stack", True))
    comparison_role = "positive transform compatibility case" if expected_compatible else "negative control for transform compatibility axis mismatch"
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
            "why_strict_one_to_one": f"{spec['why_matches_traditional']} Final result must be generated fresh on a100-2 and compared against this exact traditional transform target.",
        },
        "grammar_mapping": _grammar_mapping_for(spec),
        "transform_compatibility": {
            "expected_compatible": expected_compatible,
            "comparison_role": comparison_role,
            "positive_negative_pair_id": "V21_transform_compat_affine_stack_pair_d4",
            "compatibility_basis": spec["controls"].get("ifs_rule"),
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
            "obj_mesh_inputs_only": True,
            "pbr_textured_glb_required": True,
            "texture_size_default": 2048,
            "forbidden_outputs": ["local_selected_render", "2d_only_image", "posthoc_repair_mesh", "non_obj_mesh_input"],
        },
        "visual_readability_contract": {
            "dryrun_visual_floor": "OBJ input mesh must pass LCR >= 0.999 before remote mesh/PBR generation",
            "positive_constraint": "IFS transform cases must read as branch tree, radial ornament, lattice/pyrite, bismuth terrace, Escher recursive stairs, or explicit transform compatibility module with connected natural mesh detail",
            "negative_constraint": "no detached transform islands, no non-OBJ mesh input, no local selected renders, no pure rod scaffold, no loose 2D-only ornament",
            "v21_failure_addressed": "prior IFS/radial/lattice inputs could be connected but too schematic; V21 keeps one-to-one transform grammar while adding attached natural mesh/PBR detail.",
        },
        "strict_generation_policy": "generate_new_on_a100_2_no_local_selection_or_postprocessing",
        "root_selection_log": {
            "root_source_type": "V21_strict_ifs_transform_natural_input_generator",
            "source_generator": "assets/strict_visual_matched_cases_V21_ifs_transform_natural_20260510.py",
            "root_pool_size": 1,
            "root_generation_budget": "local CPU dry-run OBJ geometry only; final mesh/PBR outputs must be generated fresh on a100-2 GPUs 4-7",
            "root_screening_budget": "no local manual cherry-pick and no textured-output repair",
            "selection_rank": 1,
            "projection_naturalization_schedule": spec["operators"],
            "readiness_label": "remote_input_dryrun_V21_ifs_transform_lcr_ge_0.999",
            "connectivity_anchor_convention": "shared scaffold center vertices and support faces keep transform copies in one mesh component",
        },
    }


def _write_readme(out_dir: Path, summary: dict) -> None:
    text = f"""# V21 Strict IFS/Transform Natural Mesh Cases Dry Run

Generated by `assets/strict_visual_matched_cases_V21_ifs_transform_natural_20260510.py`.

This directory is a local input dry run only. It does not launch remote jobs,
does not select local textured outputs, and does not postprocess generated
outputs. Final strict cases must be generated fresh on `{REMOTE_TARGET}` with
GPU ids `{ALLOWED_GPUS}` under:

`{REMOTE_STORAGE_ROOT}`

V21 focus:

- IFS/transform/radial/lattice strict one-to-one targets.
- OBJ mesh inputs only; no GLB/PLY/STL mesh inputs.
- LCR gate before remote generation: largest-component vertex ratio >= `{CONNECTIVITY_LCR_MIN}`.
- Branch-tree IFS, radial ornament, pyrite lattice transform, bismuth stepped transform, Escher-like recursive stairs, and positive/negative transform compatibility pair.
- Mesh/PBR outputs only: local OBJ input plus fresh remote textured GLB/PBR export.
- No local selection, no local textured-output repair, no 2D-only result.

Files:

- `manifest.csv` / `manifest.json`: case-level Trellis2 input manifest.
- `a100-2_cases.txt`: `case_id|mesh_path|guide_image|seed|gpu` lines.
- `gpu4_cases.txt` ... `gpu7_cases.txt`: per-GPU splits.
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
        if metrics["mesh_component_count"] != 1 and metrics["largest_mesh_component_vertex_ratio"] < CONNECTIVITY_LCR_MIN:
            raise RuntimeError(f"{spec['case_id']} failed V21 connectivity gate: {metrics}")
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
            "mesh_input_policy": "obj_mesh_inputs_only",
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
        "mesh_input_policy",
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
        "attached_natural_mesh_detail_count",
        "shared_vertex_anchor_count",
        "support_edge_count",
        "recursive_depth",
        "affine_transform_count",
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
        "surface_generator": "strict_ifs_transform_natural_mesh_v21",
        "mesh_input_policy": "obj_mesh_inputs_only",
        "mesh_pbr_policy": "mesh_and_pbr_outputs_only",
        "connectivity_gate": {"largest_component_vertex_ratio_min": CONNECTIVITY_LCR_MIN},
        "v21_focus": "IFS transform radial lattice strict one-to-one natural mesh branch",
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
