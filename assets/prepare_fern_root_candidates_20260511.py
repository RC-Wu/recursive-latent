#!/usr/bin/env python3
"""Prepare local fern/spider/root OBJ candidates.

This is a local-only root candidate generator.  It does not launch remote jobs
or modify the Trellis workflow.  The meshes follow the V22-style pattern: a
smooth swept support with one shared center vertex per support node, and all
semantic lamina/rootlet details attached back to those center vertices.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import procedural_baselines as pb


DEFAULT_OUT = ROOT_DIR / "results" / "fern_root_candidates_20260511"
CONNECTIVITY_LCR_MIN = 0.999
SURFACE_STRATEGY = "v22_style_shared_center_swept_support_with_attached_lamina_and_rootlets"

COMMON_OPERATORS = [
    "procedural_baselines.pb.Mesh",
    "v22_style_center_anchor_sweep",
    "shared_vertex_semantic_detail_attachment",
    "single_local_obj_candidate",
    "no_remote_launch",
    "no_trellis_workflow_change",
]

DetailCounts = Dict[str, int]


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else np.asarray(v, dtype=float)


def _basis(axis: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = _unit(np.asarray(axis, dtype=float))
    seed = np.array([0.0, 0.0, 1.0]) if abs(float(w[2])) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = _unit(np.cross(w, seed))
    v = _unit(np.cross(w, u))
    return u, v, w


def _counts() -> DetailCounts:
    return {"leaflet_count": 0, "rootlet_count": 0, "tendril_count": 0, "support_node_count": 0}


def _merge_counts(*parts: DetailCounts) -> DetailCounts:
    out = _counts()
    for part in parts:
        for key, value in part.items():
            out[key] = int(out.get(key, 0)) + int(value)
    return out


def _normalize_nodes(nodes: List[np.ndarray], extent: float) -> List[np.ndarray]:
    arr = np.asarray(nodes, dtype=float)
    mn = arr.min(axis=0)
    mx = arr.max(axis=0)
    center = (mn + mx) * 0.5
    scale = max(float((mx - mn).max()), 1e-6)
    return [(np.asarray(n, dtype=float) - center) * (float(extent) / scale) for n in nodes]


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


def _graph_edges(parents: List[int]) -> List[Tuple[int, int]]:
    return [(int(parent), int(idx)) for idx, parent in enumerate(parents) if int(parent) >= 0]


def _dedupe_edges(edges: Iterable[Tuple[int, int]]) -> List[Tuple[int, int]]:
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


def _node_axis(nodes: List[np.ndarray], parents: List[int], idx: int) -> np.ndarray:
    parent = int(parents[idx]) if int(parents[idx]) >= 0 else 0
    axis = _unit(np.asarray(nodes[idx], dtype=float) - np.asarray(nodes[parent], dtype=float))
    if float(np.linalg.norm(axis)) < 1e-8:
        axis = np.array([0.0, 0.0, 1.0], dtype=float)
    return axis


def _smooth_support_mesh(
    nodes: List[np.ndarray],
    edges: List[Tuple[int, int]],
    radii: List[float],
    sides: int = 12,
    ovality: float = 0.14,
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
        twist = 0.17 * math.sin(edge_i * 1.613)
        base = len(mesh.vertices)
        for endpoint, radius in ((start, radii[a]), (end, radii[b])):
            for i in range(sides):
                theta = math.tau * i / sides + twist
                profile = 1.0 + float(ovality) * math.sin(theta * 2.0 + edge_i * 0.31)
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


def _orient_leaf_axes(direction: np.ndarray, normal_hint: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = _unit(np.asarray(direction, dtype=float))
    n = _unit(np.asarray(normal_hint, dtype=float))
    side = _unit(np.cross(w, n))
    if float(np.linalg.norm(side)) < 1e-8:
        side, n, w = _basis(w)
    lift = _unit(np.cross(side, w))
    return side, lift, w


def _add_lamina(
    mesh: pb.Mesh,
    anchor_idx: int,
    anchor: np.ndarray,
    direction: np.ndarray,
    length: float,
    width: float,
    normal_hint: np.ndarray,
    rows: int = 6,
    curl: float = 0.035,
    serration: float = 0.08,
) -> None:
    side, lift, w = _orient_leaf_axes(direction, normal_hint)
    row_indices: List[Tuple[int, int, int]] = []
    for r in range(1, int(rows) + 1):
        t = r / float(rows)
        taper = math.sin(math.pi * t)
        ripple = 1.0 + float(serration) * math.sin(9.0 * math.pi * t)
        center = np.asarray(anchor, dtype=float) + w * float(length) * t + lift * float(length) * float(curl) * math.sin(math.pi * t)
        half_width = float(width) * taper * ripple
        midrib = center + lift * float(width) * 0.035 * math.sin(math.tau * t)
        inds = []
        for p in (center - side * half_width, midrib, center + side * half_width):
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


def _add_thick_lamina(
    mesh: pb.Mesh,
    anchor_idx: int,
    anchor: np.ndarray,
    direction: np.ndarray,
    length: float,
    width: float,
    normal_hint: np.ndarray,
    rows: int = 8,
    thickness: float = 0.010,
    curl: float = 0.045,
    taper_power: float = 0.72,
) -> None:
    """Add a closed, slightly thick strap leaf rather than a zero-thickness card."""

    side, lift, w = _orient_leaf_axes(direction, normal_hint)
    normal = _unit(np.cross(w, side))
    if float(np.linalg.norm(normal)) < 1e-8:
        normal = _unit(normal_hint)

    top_rows: List[Tuple[int, int, int]] = []
    bottom_rows: List[Tuple[int, int, int]] = []
    for r in range(1, int(rows) + 1):
        t = r / float(rows)
        taper = max(math.sin(math.pi * t), 0.0) ** float(taper_power)
        center = np.asarray(anchor, dtype=float) + w * float(length) * t + lift * float(length) * float(curl) * math.sin(math.pi * t)
        half_width = float(width) * taper * (1.0 - 0.10 * t)
        midrib = center + lift * float(width) * 0.020 * math.sin(math.tau * t)
        top = []
        bottom = []
        for p in (center - side * half_width, midrib, center + side * half_width):
            mesh.vertices.append(tuple(p + normal * float(thickness) * 0.5))
            top.append(len(mesh.vertices))
            mesh.vertices.append(tuple(p - normal * float(thickness) * 0.5))
            bottom.append(len(mesh.vertices))
        top_rows.append((top[0], top[1], top[2]))
        bottom_rows.append((bottom[0], bottom[1], bottom[2]))

    first_top = top_rows[0]
    first_bottom = bottom_rows[0]
    for face in ((anchor_idx, first_top[0], first_top[1]), (anchor_idx, first_top[1], first_top[2])):
        mesh.faces.append(face)
    for face in ((anchor_idx, first_bottom[1], first_bottom[0]), (anchor_idx, first_bottom[2], first_bottom[1])):
        mesh.faces.append(face)

    def add_strip(a, b, flip: bool = False) -> None:
        faces = [
            (a[0], b[0], a[1]),
            (a[1], b[0], b[1]),
            (a[1], b[1], a[2]),
            (a[2], b[1], b[2]),
        ]
        for face in faces:
            mesh.faces.append((face[0], face[2], face[1]) if flip else face)

    for a, b in zip(top_rows[:-1], top_rows[1:]):
        add_strip(a, b, flip=False)
    for a, b in zip(bottom_rows[:-1], bottom_rows[1:]):
        add_strip(a, b, flip=True)

    for top_seq, bottom_seq in ((top_rows, bottom_rows),):
        for edge_idx in (0, 2):
            for a_top, b_top, a_bottom, b_bottom in zip(top_seq[:-1], top_seq[1:], bottom_seq[:-1], bottom_seq[1:]):
                at = a_top[edge_idx]
                bt = b_top[edge_idx]
                ab = a_bottom[edge_idx]
                bb = b_bottom[edge_idx]
                mesh.faces.append((at, bt, ab))
                mesh.faces.append((bt, bb, ab))


def _add_curved_tube_detail(
    mesh: pb.Mesh,
    anchor_idx: int,
    anchor: np.ndarray,
    direction: np.ndarray,
    length: float,
    radius: float,
    rng: np.random.Generator,
    segments: int = 4,
    sides: int = 6,
    curl: float = 0.20,
) -> None:
    direction = _unit(np.asarray(direction, dtype=float))
    u, v, w = _basis(direction)
    phase = float(rng.uniform(0.0, math.tau))
    bend = _unit(math.cos(phase) * u + math.sin(phase) * v + 0.18 * w)
    rings: List[List[int]] = []
    prev = np.asarray(anchor, dtype=float)
    for s in range(1, int(segments) + 1):
        t = s / float(segments)
        center = np.asarray(anchor, dtype=float) + direction * float(length) * t + bend * float(length) * float(curl) * math.sin(math.pi * t)
        tangent = _unit(center - prev)
        ru, rv, _rw = _basis(tangent if float(np.linalg.norm(tangent)) > 1e-8 else direction)
        r = float(radius) * (1.0 - 0.70 * t) + float(radius) * 0.15
        ring: List[int] = []
        for i in range(sides):
            theta = math.tau * i / sides + phase * 0.11
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
    tip_center = np.mean(np.asarray([mesh.vertices[i - 1] for i in rings[-1]], dtype=float), axis=0) + direction * float(length) * 0.055
    mesh.vertices.append(tuple(tip_center))
    tip = len(mesh.vertices)
    last = rings[-1]
    for i in range(sides):
        j = (i + 1) % sides
        mesh.faces.append((last[i], tip, last[j]))


def _renormalize_mesh(mesh: pb.Mesh, extent: float = 2.85) -> None:
    if not mesh.vertices:
        return
    arr = np.asarray(mesh.vertices, dtype=float)
    mn = arr.min(axis=0)
    mx = arr.max(axis=0)
    center = (mn + mx) * 0.5
    scale = max(float((mx - mn).max()), 1e-6)
    arr = (arr - center) * (float(extent) / scale)
    mesh.vertices = [tuple(map(float, p)) for p in arr]


def _compound_fern(seed: int, variant: str) -> Tuple[pb.Mesh, Dict, DetailCounts, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.044 if variant == "arched" else 0.038]
    rachis = [0]
    n = 18 if variant == "arched" else 22
    parent = 0
    for i in range(1, n + 1):
        t = i / float(n)
        direction = np.array([0.08 * math.sin(t * math.pi * 0.95), 0.016 * math.sin(t * math.tau), 0.18 + 0.045 * math.cos(t * math.pi)], dtype=float)
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(radii[-1] * 0.955, 0.010))
        rachis.append(parent)

    side_anchors: List[Tuple[int, int, float]] = []
    for local_i, anchor in enumerate(rachis[2:-2], start=2):
        t = local_i / float(n)
        length = (0.64 if variant == "arched" else 0.52) * (math.sin(math.pi * t) ** 0.62) + 0.10
        for sign in (-1, 1):
            if variant == "offset" and (local_i + sign) % 3 == 0:
                continue
            side_dir = np.array([sign * (0.88 + 0.10 * math.sin(local_i)), 0.035 * math.cos(local_i * 0.7), 0.24 - 0.23 * t], dtype=float)
            p0 = _append_child(nodes, parents, radii, anchor, side_dir, length, max(0.015 * (1.0 - 0.42 * t), 0.006))
            p1 = _append_child(nodes, parents, radii, p0, side_dir + np.array([0.0, 0.02 * sign, -0.10]), length * 0.45, max(0.010 * (1.0 - 0.35 * t), 0.0045))
            side_anchors.append((p0, sign, t))
            side_anchors.append((p1, sign, t))

    normalized = _normalize_nodes(nodes, 2.70)
    mesh = _smooth_support_mesh(normalized, _graph_edges(parents), radii, sides=12, ovality=0.18)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    normal_hint = np.array([0.0, 1.0, 0.18], dtype=float)
    for k, (idx, sign, t) in enumerate(side_anchors):
        base_dir = _node_axis(normalized, parents, idx)
        leaflet_dir = _unit(base_dir + np.array([0.12 * sign, 0.0, -0.04]) + rng.normal(0.0, 0.018, 3))
        length = float(rng.uniform(0.145, 0.235) * (1.05 if variant == "arched" else 0.92) * (1.18 - 0.34 * t))
        width = length * float(rng.uniform(0.18, 0.30))
        _add_lamina(mesh, centers[idx], normalized[idx], leaflet_dir, length, width, normal_hint, rows=5, curl=0.055, serration=0.13)
        counts["leaflet_count"] += 1
        if variant == "offset" and k % 3 == 1:
            sub_dir = _unit(0.55 * leaflet_dir + np.array([0.0, 0.0, -0.12]) + rng.normal(0.0, 0.03, 3))
            _add_lamina(mesh, centers[idx], normalized[idx], sub_dir, length * 0.58, width * 0.72, normal_hint, rows=4, curl=0.035, serration=0.10)
            counts["leaflet_count"] += 1

    counts["support_node_count"] = len(normalized)
    controls = _controls(
        motif="compound fern frond",
        source="hand-authored V22-style fern rachis with attached pinnae",
        seed=seed,
        nodes=normalized,
        edges=_graph_edges(parents),
        counts=counts,
        extra={
            "variant": variant,
            "rachis_node_count": len(rachis),
            "pinna_anchor_count": len(side_anchors),
            "target_silhouette": "compound fern frond with attached alternating pinnae",
        },
    )
    grammar = {
        "grammar_family": "procedural fern rachis",
        "symbols": "rachis -> alternating pinnae -> attached leaflets",
        "root_candidate_use": "local clean OBJ root/plant candidate",
    }
    return mesh, controls, counts, grammar


def _fiddlehead(seed: int, variant: str) -> Tuple[pb.Mesh, Dict, DetailCounts, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.044]
    parent = 0

    stem_steps = 8 if variant == "crozier" else 5
    for i in range(1, stem_steps + 1):
        t = i / float(stem_steps)
        direction = np.array([0.11 * math.sin(t * math.pi * 0.65), 0.018 * math.cos(i), 0.20 + 0.04 * t], dtype=float)
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.040 * (0.92**i), 0.012))

    coil_parent = parent
    turns = 1.95 if variant == "crozier" else 2.65
    coil_steps = 24 if variant == "crozier" else 34
    start = np.asarray(nodes[coil_parent], dtype=float)
    center = start + np.array([0.24 if variant == "crozier" else 0.08, 0.0, 0.08], dtype=float)
    prev = start
    for i in range(1, coil_steps + 1):
        t = i / float(coil_steps)
        theta = turns * math.tau * t + (0.28 if variant == "crozier" else 0.0)
        radius = (0.52 if variant == "crozier" else 0.44) * (1.0 - 0.74 * t) + 0.030
        p = center + np.array([radius * math.cos(theta), 0.018 * math.sin(theta * 0.7), radius * math.sin(theta)], dtype=float)
        direction = p - prev
        coil_parent = _append_child(nodes, parents, radii, coil_parent, direction, max(float(np.linalg.norm(direction)), 1e-6), max(0.020 * (1.0 - 0.55 * t), 0.006))
        prev = p

    normalized = _normalize_nodes(nodes, 2.60)
    mesh = _smooth_support_mesh(normalized, _graph_edges(parents), radii, sides=12, ovality=0.21)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    normal_hint = np.array([0.0, 1.0, 0.22], dtype=float)
    first_detail = stem_steps + 3
    for k, idx in enumerate(range(first_detail, len(normalized) - 1, 2 if variant == "crozier" else 3)):
        axis = _node_axis(normalized, parents, idx)
        radial = _unit(np.asarray(normalized[idx], dtype=float) - np.asarray(normalized[stem_steps], dtype=float))
        leaf_dir = _unit(0.42 * axis + 0.75 * radial + rng.normal(0.0, 0.025, 3))
        length = float(rng.uniform(0.075, 0.145) * (1.15 if variant == "crozier" else 0.90))
        _add_lamina(mesh, centers[idx], normalized[idx], leaf_dir, length, length * 0.24, normal_hint, rows=4, curl=0.070, serration=0.10)
        counts["leaflet_count"] += 1
        if variant == "tight_spiral" and k % 4 == 0:
            _add_curved_tube_detail(
                mesh,
                centers[idx],
                normalized[idx],
                _unit(0.45 * leaf_dir + np.array([0.0, 0.0, -0.22])),
                float(rng.uniform(0.070, 0.115)),
                float(rng.uniform(0.0022, 0.0038)),
                rng,
                segments=3,
                sides=5,
                curl=0.32,
            )
            counts["tendril_count"] += 1

    counts["support_node_count"] = len(normalized)
    controls = _controls(
        motif="fiddlehead spiral crozier",
        source="hand-authored spiral fern crozier using shared support centers",
        seed=seed,
        nodes=normalized,
        edges=_graph_edges(parents),
        counts=counts,
        extra={
            "variant": variant,
            "spiral_turns": turns,
            "coil_step_count": coil_steps,
            "target_silhouette": "unfurling fern fiddlehead/crozier",
        },
    )
    grammar = {
        "grammar_family": "fern crozier spiral",
        "symbols": "stem -> shrinking spiral -> folded pinnae",
        "root_candidate_use": "local clean OBJ root/plant candidate",
    }
    return mesh, controls, counts, grammar


def _spider_rosette(seed: int) -> Tuple[pb.Mesh, Dict, DetailCounts, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.050]
    leaf_nodes: List[Tuple[int, np.ndarray, float]] = []
    arms = 13
    for arm in range(arms):
        theta = math.tau * arm / arms + 0.10 * math.sin(arm)
        radial = np.array([math.cos(theta), math.sin(theta), 0.0], dtype=float)
        parent = 0
        arm_len = 0.80 + 0.18 * math.sin(arm * 1.7)
        for s in range(1, 4):
            t = s / 3.0
            lift = np.array([0.0, 0.0, 0.34 * math.sin(math.pi * t) - 0.10 * t], dtype=float)
            direction = radial * (arm_len * (0.36 + 0.08 * s)) + lift
            parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.022 * (1.0 - 0.20 * s), 0.010))
            if s == 1:
                leaf_nodes.append((parent, radial, arm_len))

    for root in range(9):
        theta = math.tau * (root + 0.35) / 9.0
        radial = np.array([math.cos(theta), math.sin(theta), -0.65], dtype=float)
        _append_child(nodes, parents, radii, 0, radial, 0.38 + 0.04 * math.sin(root), 0.0065)

    normalized = _normalize_nodes(nodes, 2.68)
    mesh = _smooth_support_mesh(normalized, _graph_edges(parents), radii, sides=12, ovality=0.17)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    for idx, radial, arm_len in leaf_nodes:
        length = float(0.75 + 0.12 * rng.random()) * arm_len
        _add_lamina(
            mesh,
            centers[0],
            normalized[0],
            _unit(radial + np.array([0.0, 0.0, 0.16])),
            length,
            length * float(rng.uniform(0.070, 0.105)),
            np.array([0.0, 0.0, 1.0]),
            rows=8,
            curl=0.105,
            serration=0.020,
        )
        _add_lamina(
            mesh,
            centers[idx],
            normalized[idx],
            _unit(radial + np.array([0.0, 0.0, -0.04])),
            length * 0.45,
            length * float(rng.uniform(0.030, 0.045)),
            np.array([0.0, 0.0, 1.0]),
            rows=5,
            curl=0.055,
            serration=0.015,
        )
        counts["leaflet_count"] += 2

    for k, idx in enumerate(range(len(normalized) - 9, len(normalized))):
        direction = _unit(np.asarray(normalized[idx], dtype=float) - np.asarray(normalized[0], dtype=float) + rng.normal(0.0, 0.03, 3))
        _add_curved_tube_detail(mesh, centers[0], normalized[0], direction, float(rng.uniform(0.15, 0.25)), 0.0035, rng, segments=4, sides=5, curl=0.20)
        counts["rootlet_count"] += 1

    counts["support_node_count"] = len(normalized)
    controls = _controls(
        motif="spider plant rosette",
        source="radial spider rosette with swept midribs and strap lamina",
        seed=seed,
        nodes=normalized,
        edges=_graph_edges(parents),
        counts=counts,
        extra={
            "variant": "radial_spider_rosette",
            "rosette_arm_count": arms,
            "target_silhouette": "spider plant rosette with attached basal roots",
        },
    )
    grammar = {
        "grammar_family": "radial phyllotaxis rosette",
        "symbols": "hub -> strap leaves + basal roots",
        "root_candidate_use": "local clean OBJ root/plant candidate",
    }
    return mesh, controls, counts, grammar


def _spider_rosette_broad(seed: int, plantlets: bool = False) -> Tuple[pb.Mesh, Dict, DetailCounts, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.066]
    leaf_nodes: List[Tuple[int, np.ndarray, float]] = []
    arms = 17 if not plantlets else 15
    for arm in range(arms):
        theta = math.tau * arm / arms + 0.055 * math.sin(arm * 1.31)
        radial = np.array([math.cos(theta), math.sin(theta), 0.0], dtype=float)
        parent = 0
        arm_len = 0.84 + 0.12 * math.sin(arm * 1.47)
        steps = 4
        for s in range(1, steps + 1):
            t = s / float(steps)
            lift = np.array([0.0, 0.0, 0.28 * math.sin(math.pi * t) - 0.07 * t], dtype=float)
            direction = radial * (arm_len * (0.25 + 0.09 * s)) + lift
            parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.030 * (1.0 - 0.18 * s), 0.012))
            if s in (1, 2):
                leaf_nodes.append((parent, radial, arm_len * (1.0 - 0.12 * (s - 1))))

    root_count = 11
    root_nodes: List[int] = []
    for root in range(root_count):
        theta = math.tau * (root + 0.35) / root_count
        radial = np.array([math.cos(theta), math.sin(theta), -0.72], dtype=float)
        root_nodes.append(_append_child(nodes, parents, radii, 0, radial, 0.34 + 0.035 * math.sin(root), 0.0075))

    plantlet_nodes: List[Tuple[int, np.ndarray, float]] = []
    if plantlets:
        for runner in range(3):
            theta = math.tau * (runner + 0.20) / 3.0
            radial = np.array([math.cos(theta), math.sin(theta), -0.10], dtype=float)
            parent = 0
            for s in range(1, 4):
                t = s / 3.0
                direction = radial * (0.52 + 0.15 * s) + np.array([0.0, 0.0, -0.11 * t], dtype=float)
                parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.018 * (1.0 - 0.20 * s), 0.007))
            for child in range(5):
                angle = theta + math.tau * child / 5.0
                child_radial = np.array([math.cos(angle), math.sin(angle), 0.12], dtype=float)
                child_node = _append_child(nodes, parents, radii, parent, child_radial, 0.20 + 0.025 * rng.random(), 0.0065)
                plantlet_nodes.append((child_node, child_radial, 0.23))

    normalized = _normalize_nodes(nodes, 2.70)
    mesh = _smooth_support_mesh(normalized, _graph_edges(parents), radii, sides=14, ovality=0.12)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    for idx, radial, arm_len in leaf_nodes:
        length = float(0.78 + 0.10 * rng.random()) * arm_len
        _add_thick_lamina(
            mesh,
            centers[idx],
            normalized[idx],
            _unit(radial + np.array([0.0, 0.0, 0.10])),
            length,
            length * float(rng.uniform(0.145, 0.205)),
            np.array([0.0, 0.0, 1.0]),
            rows=10,
            thickness=float(rng.uniform(0.010, 0.016)),
            curl=0.090,
            taper_power=0.55,
        )
        counts["leaflet_count"] += 1

    for idx, radial, arm_len in plantlet_nodes:
        _add_thick_lamina(
            mesh,
            centers[idx],
            normalized[idx],
            _unit(radial + np.array([0.0, 0.0, 0.08])),
            arm_len,
            arm_len * 0.12,
            np.array([0.0, 0.0, 1.0]),
            rows=6,
            thickness=0.007,
            curl=0.060,
            taper_power=0.60,
        )
        counts["leaflet_count"] += 1

    for idx in root_nodes:
        direction = _unit(np.asarray(normalized[idx], dtype=float) - np.asarray(normalized[0], dtype=float) + rng.normal(0.0, 0.025, 3))
        _add_curved_tube_detail(mesh, centers[0], normalized[0], direction, float(rng.uniform(0.12, 0.20)), 0.0040, rng, segments=4, sides=5, curl=0.16)
        counts["rootlet_count"] += 1

    counts["support_node_count"] = len(normalized)
    variant = "broad_strapleaf_plantlets" if plantlets else "broad_strapleaf"
    controls = _controls(
        motif="spider plant broad rosette",
        source="radial spider rosette with thick strap lamina and optional plantlets",
        seed=seed,
        nodes=normalized,
        edges=_graph_edges(parents),
        counts=counts,
        extra={
            "variant": variant,
            "rosette_arm_count": arms,
            "target_silhouette": "spider plant rosette with wider strap leaves and attached basal roots",
            "thick_lamina": True,
            "plantlet_count": len(plantlet_nodes),
        },
    )
    grammar = {
        "grammar_family": "radial phyllotaxis rosette with thick strap leaves",
        "symbols": "hub -> thick strap leaves + basal roots + optional plantlets",
        "root_candidate_use": "local clean OBJ root/plant candidate",
    }
    return mesh, controls, counts, grammar


def _spider_rosette_publication_20260511h(seed: int, plantlets: bool = False) -> Tuple[pb.Mesh, Dict, DetailCounts, Dict]:
    """Cleaner, taller spider/plant-leaf root for axis-corrected SLat sweeps."""

    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.074]
    leaf_nodes: List[Tuple[int, np.ndarray, float, float]] = []
    root_nodes: List[int] = []
    runner_nodes: List[Tuple[int, np.ndarray, float]] = []
    arms = 11 if not plantlets else 9
    for arm in range(arms):
        theta = math.tau * arm / arms + float(rng.normal(0.0, 0.035))
        radial = np.array([math.cos(theta), math.sin(theta), 0.0], dtype=float)
        parent = 0
        arm_len = float(rng.uniform(0.88, 1.04))
        for s in range(1, 5):
            t = s / 4.0
            lift = np.array([0.0, 0.0, 0.34 * math.sin(math.pi * t) + 0.09 * t], dtype=float)
            sway = np.array([-radial[1], radial[0], 0.0], dtype=float) * (0.035 * math.sin(arm * 1.7 + s))
            direction = radial * (arm_len * (0.20 + 0.12 * s)) + lift + sway
            parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.036 * (1.0 - 0.15 * s), 0.014))
            if s in (2, 3):
                leaf_nodes.append((parent, radial, arm_len * (1.0 - 0.10 * (s - 2)), 0.18 if s == 2 else 0.13))

    for root in range(13):
        theta = math.tau * (root + 0.18) / 13.0
        radial = np.array([math.cos(theta), math.sin(theta), -0.95], dtype=float)
        root_nodes.append(_append_child(nodes, parents, radii, 0, radial, float(rng.uniform(0.31, 0.43)), 0.0085))

    if plantlets:
        for runner in range(3):
            theta = math.tau * (runner + 0.12) / 3.0
            radial = np.array([math.cos(theta), math.sin(theta), 0.04], dtype=float)
            parent = 0
            for s in range(1, 5):
                direction = radial * (0.45 + 0.13 * s) + np.array([0.0, 0.0, 0.03 * s], dtype=float)
                parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.016 * (1.0 - 0.18 * s), 0.0065))
            for child in range(4):
                angle = theta + math.tau * child / 4.0 + float(rng.normal(0.0, 0.08))
                child_radial = np.array([math.cos(angle), math.sin(angle), 0.22], dtype=float)
                child_node = _append_child(nodes, parents, radii, parent, child_radial, float(rng.uniform(0.18, 0.25)), 0.006)
                runner_nodes.append((child_node, child_radial, float(rng.uniform(0.20, 0.27))))

    normalized = _normalize_nodes(nodes, 2.82)
    mesh = _smooth_support_mesh(normalized, _graph_edges(parents), radii, sides=16, ovality=0.10)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    for idx, radial, arm_len, width_ratio in leaf_nodes:
        length = float(rng.uniform(0.78, 0.92)) * arm_len
        _add_thick_lamina(
            mesh,
            centers[idx],
            normalized[idx],
            _unit(radial + np.array([0.0, 0.0, 0.18])),
            length,
            length * width_ratio,
            np.array([0.0, 0.0, 1.0]),
            rows=12,
            thickness=float(rng.uniform(0.018, 0.025)),
            curl=0.12,
            taper_power=0.50,
        )
        counts["leaflet_count"] += 1

    for idx, radial, arm_len in runner_nodes:
        _add_thick_lamina(
            mesh,
            centers[idx],
            normalized[idx],
            _unit(radial + np.array([0.0, 0.0, 0.16])),
            arm_len,
            arm_len * 0.15,
            np.array([0.0, 0.0, 1.0]),
            rows=7,
            thickness=0.010,
            curl=0.08,
            taper_power=0.56,
        )
        counts["leaflet_count"] += 1

    for idx in root_nodes:
        direction = _unit(np.asarray(normalized[idx], dtype=float) - np.asarray(normalized[0], dtype=float) + rng.normal(0.0, 0.020, 3))
        _add_curved_tube_detail(mesh, centers[0], normalized[0], direction, float(rng.uniform(0.14, 0.22)), 0.0045, rng, segments=5, sides=6, curl=0.13)
        counts["rootlet_count"] += 1

    counts["support_node_count"] = len(normalized)
    variant = "publication_rosette_runner_20260511h" if plantlets else "publication_rosette_broad_20260511h"
    controls = _controls(
        motif="publication spider/plant-leaf root",
        source="20260511h corrected rosette with explicit basal root indices and thicker leaves",
        seed=seed,
        nodes=normalized,
        edges=_graph_edges(parents),
        counts=counts,
        extra={
            "variant": variant,
            "rosette_arm_count": arms,
            "target_silhouette": "taller spider-plant rosette with clear basal crown and attached roots",
            "thick_lamina": True,
            "plantlet_count": len(runner_nodes),
            "axis_hint_for_trellis2": "original z maps to latent y with sign -1; use --growth-axis y --growth-sign -1 first",
            "root_nodes_tracked_explicitly": True,
        },
    )
    grammar = {
        "grammar_family": "axis-corrected basal rosette with thick leaves",
        "symbols": "hub -> raised strap leaves + explicit basal roots + optional runner plantlets",
        "root_candidate_use": "20260511h primary plant/spider root candidate",
    }
    return mesh, controls, counts, grammar


def _root_vine(seed: int) -> Tuple[pb.Mesh, Dict, DetailCounts, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([-0.95, 0.0, 0.05], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.046]
    main = [0]
    parent = 0
    for i in range(1, 15):
        direction = np.array([0.19, 0.065 * math.sin(i * 0.82), -0.010 + 0.022 * math.sin(i * 0.43)], dtype=float)
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.044 * (0.91**i), 0.010))
        main.append(parent)

    lateral_nodes: List[int] = []
    for i, anchor in enumerate(main[2:-1], start=2):
        for sign in (-1, 1):
            if (i + sign) % 4 == 0:
                continue
            side = np.array([0.05 * math.cos(i), sign * (0.34 + 0.04 * math.sin(i)), -0.18 - 0.02 * i], dtype=float)
            first = _append_child(nodes, parents, radii, anchor, side, 1.0, max(0.012 * (1.0 - 0.035 * i), 0.0048))
            second = _append_child(nodes, parents, radii, first, side + np.array([0.05, 0.02 * sign, -0.08]), 0.62, 0.0042)
            lateral_nodes.extend([first, second])

    normalized = _normalize_nodes(nodes, 2.78)
    mesh = _smooth_support_mesh(normalized, _graph_edges(parents), radii, sides=12, ovality=0.24)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    for k, idx in enumerate(lateral_nodes):
        axis = _node_axis(normalized, parents, idx)
        u, v, _w = _basis(axis)
        lateral = math.cos(k * 1.67) * u + math.sin(k * 1.67) * v
        direction = _unit(0.34 * axis + 0.44 * lateral + np.array([0.0, 0.0, -0.72]) + rng.normal(0.0, 0.055, 3))
        _add_curved_tube_detail(
            mesh,
            centers[idx],
            normalized[idx],
            direction,
            float(rng.uniform(0.085, 0.185)),
            float(rng.uniform(0.0021, 0.0042)),
            rng,
            segments=4,
            sides=5,
            curl=0.26,
        )
        counts["rootlet_count"] += 1

    for k, idx in enumerate(main[3::3]):
        axis = _node_axis(normalized, parents, idx)
        _add_curved_tube_detail(mesh, centers[idx], normalized[idx], _unit(axis + np.array([0.0, 0.18, 0.20])), float(rng.uniform(0.12, 0.22)), 0.0030, rng, segments=5, sides=5, curl=0.45)
        counts["tendril_count"] += 1

    counts["support_node_count"] = len(normalized)
    controls = _controls(
        motif="root-vine fallback",
        source="ground-crawling root-vine support with attached fine roots",
        seed=seed,
        nodes=normalized,
        edges=_graph_edges(parents),
        counts=counts,
        extra={
            "variant": "fallback_root_vine",
            "main_vine_node_count": len(main),
            "lateral_root_node_count": len(lateral_nodes),
            "target_silhouette": "connected root-vine fallback with many fine rootlets",
        },
    )
    grammar = {
        "grammar_family": "root-vine recursive chain",
        "symbols": "main vine -> lateral roots -> fine rootlets/tendrils",
        "root_candidate_use": "local clean OBJ root/plant candidate",
    }
    return mesh, controls, counts, grammar


def _controls(
    motif: str,
    source: str,
    seed: int,
    nodes: List[np.ndarray],
    edges: List[Tuple[int, int]],
    counts: DetailCounts,
    extra: Dict,
) -> Dict:
    controls = {
        "motif": motif,
        "source": source,
        "seed": int(seed),
        "mesh_input_format": "obj",
        "local_generation_only": True,
        "remote_jobs_launched": False,
        "trellis_workflow_changed": False,
        "connected_support": True,
        "connectivity_gate_lcr_min": CONNECTIVITY_LCR_MIN,
        "surface_strategy": SURFACE_STRATEGY,
        "smooth_swept_support": True,
        "shared_vertex_attachment": True,
        "support_node_count": int(len(nodes)),
        "support_edge_count": int(len(_dedupe_edges(edges))),
        "semantic_detail_count": int(counts.get("leaflet_count", 0) + counts.get("rootlet_count", 0) + counts.get("tendril_count", 0)),
        "leaflet_count": int(counts.get("leaflet_count", 0)),
        "rootlet_count": int(counts.get("rootlet_count", 0)),
        "tendril_count": int(counts.get("tendril_count", 0)),
        "detached_chunk_policy": "forbid_by_shared_vertex_faces",
    }
    controls.update(extra)
    return controls


def _case_specs(seed: int) -> List[Dict]:
    cases: List[Dict] = []

    def add(case_id: str, family: str, motif: str, builder, offset: int, why: str) -> None:
        mesh, controls, counts, grammar = builder(seed + offset)
        _renormalize_mesh(mesh, extent=2.85)
        cases.append(
            {
                "case_id": case_id,
                "family": family,
                "motif": motif,
                "mesh": mesh,
                "controls": controls,
                "counts": counts,
                "grammar_mapping": grammar,
                "seed": int(seed + offset),
                "why_candidate": why,
                "operators": list(COMMON_OPERATORS),
                "case_role": "local_root_candidate",
            }
        )

    add(
        "fern_compound_frond_arch_a",
        "fern",
        "compound fern frond",
        lambda s: _compound_fern(s, "arched"),
        11,
        "Clean arched fern frond with a shared swept rachis and attached pinnae/leaflets.",
    )
    add(
        "fern_compound_frond_lacy_b",
        "fern",
        "compound fern frond",
        lambda s: _compound_fern(s, "offset"),
        12,
        "Lacier compound frond variant with denser offset attached leaflets and no detached cards.",
    )
    add(
        "fiddlehead_crozier_open_a",
        "fern",
        "fiddlehead spiral/crozier",
        lambda s: _fiddlehead(s, "crozier"),
        21,
        "Open crozier silhouette with a connected swept stem and folded attached pinnae along the curl.",
    )
    add(
        "fiddlehead_tight_spiral_b",
        "fern",
        "fiddlehead spiral/crozier",
        lambda s: _fiddlehead(s, "tight_spiral"),
        22,
        "Tighter fiddlehead coil with small attached scales/tendrils for a root-token-like local candidate.",
    )
    add(
        "spider_rosette_strapleaf_a",
        "spider plant",
        "spider rosette",
        _spider_rosette,
        31,
        "Radial spider-plant rosette with swept midrib support, strap lamina, and attached basal roots.",
    )
    add(
        "spider_rosette_broadleaf_b",
        "spider plant",
        "spider broad rosette",
        lambda s: _spider_rosette_broad(s, plantlets=False),
        32,
        "Wider, thicker spider-plant rosette root designed to survive SLat decode as leaves rather than rods.",
    )
    add(
        "spider_rosette_runner_plantlets_c",
        "spider plant",
        "spider runner plantlets",
        lambda s: _spider_rosette_broad(s, plantlets=True),
        33,
        "Spider-plant rosette with attached runners and small plantlets for recursive plantlet semantics.",
    )
    add(
        "spider_rosette_publication_broad_20260511h",
        "spider plant",
        "axis-corrected publication broad rosette",
        lambda s: _spider_rosette_publication_20260511h(s, plantlets=False),
        34,
        "20260511h taller broad rosette with explicit basal roots and thicker leaves for corrected y,-1 SLat recursion.",
    )
    add(
        "spider_rosette_publication_runner_20260511h",
        "spider plant",
        "axis-corrected publication runner rosette",
        lambda s: _spider_rosette_publication_20260511h(s, plantlets=True),
        35,
        "20260511h runner/plantlet rosette with basal root indexing fixed and clearer child-plant anchors.",
    )
    add(
        "root_vine_fallback_web_a",
        "root-vine",
        "root-vine fallback",
        _root_vine,
        41,
        "Fallback connected root-vine web with many shared-vertex rootlets for robust local root use.",
    )
    return cases


class _UnionFind:
    def __init__(self, n: int):
        self.parent = np.arange(n, dtype=np.int64)
        self.size = np.ones(n, dtype=np.int64)

    def find(self, x: int) -> int:
        while int(self.parent[x]) != int(x):
            self.parent[x] = self.parent[self.parent[x]]
            x = int(self.parent[x])
        return int(x)

    def union(self, a: int, b: int) -> None:
        ra = self.find(int(a))
        rb = self.find(int(b))
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]


def _mesh_stats(mesh: pb.Mesh) -> Dict:
    vertices = np.asarray(mesh.vertices, dtype=float) if mesh.vertices else np.zeros((0, 3), dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64) - 1 if mesh.faces else np.zeros((0, 3), dtype=np.int64)
    if len(vertices) == 0:
        return {
            "vertices": 0,
            "faces": 0,
            "mesh_component_count": 0,
            "largest_mesh_component_vertex_ratio": 0.0,
            "bbox_min": [0.0, 0.0, 0.0],
            "bbox_max": [0.0, 0.0, 0.0],
            "bbox_extent": [0.0, 0.0, 0.0],
            "bbox_diag": 0.0,
            "surface_area": 0.0,
        }
    uf = _UnionFind(len(vertices))
    for a, b, c in faces:
        uf.union(int(a), int(b))
        uf.union(int(b), int(c))
    roots = np.fromiter((uf.find(i) for i in range(len(vertices))), dtype=np.int64, count=len(vertices))
    _labels, counts = np.unique(roots, return_counts=True)
    largest = int(counts.max()) if len(counts) else 0
    mn = vertices.min(axis=0)
    mx = vertices.max(axis=0)
    extent = mx - mn
    surface_area = 0.0
    if len(faces):
        tri = vertices[faces]
        surface_area = float(np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1).sum() * 0.5)
    return {
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
        "mesh_component_count": int(len(counts)),
        "largest_mesh_component_vertex_ratio": float(largest / max(len(vertices), 1)),
        "bbox_min": [float(x) for x in mn],
        "bbox_max": [float(x) for x in mx],
        "bbox_extent": [float(x) for x in extent],
        "bbox_diag": float(np.linalg.norm(extent)),
        "surface_area": surface_area,
    }


def _export_mesh(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


def _metadata_for(spec: Dict, mesh_path: Path, metrics: Dict) -> Dict:
    controls = dict(spec["controls"])
    return {
        "case_id": spec["case_id"],
        "family": spec["family"],
        "motif": spec["motif"],
        "mesh_path": str(mesh_path),
        "seed": int(spec["seed"]),
        "case_role": spec["case_role"],
        "operators": spec["operators"],
        "operator_composition": " -> ".join(spec["operators"]),
        "controls": controls,
        "grammar_mapping": spec["grammar_mapping"],
        "why_candidate": spec["why_candidate"],
        "semantic_detail_breakdown": {
            "leaflet_count": int(controls.get("leaflet_count", 0)),
            "rootlet_count": int(controls.get("rootlet_count", 0)),
            "tendril_count": int(controls.get("tendril_count", 0)),
            "total": int(controls.get("semantic_detail_count", 0)),
        },
        "initial_mesh_metrics": metrics,
        "local_scope_contract": {
            "local_generation_only": True,
            "remote_jobs_launched": False,
            "trellis_workflow_changed": False,
            "allowed_output_root": "results/fern_root_candidates_20260511",
            "source_script": "assets/prepare_fern_root_candidates_20260511.py",
        },
        "visual_readability_contract": {
            "positive_constraint": "fern/spider/root silhouette from connected swept support with attached visible lamina/rootlets",
            "negative_constraint": "no detached semantic islands, no low-poly block stamping, no mesh-token stamping, no remote selection",
            "connectivity_floor": CONNECTIVITY_LCR_MIN,
        },
    }


def _write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _render_contact_sheet(out_dir: Path, rows: List[Dict], max_faces: int) -> Dict:
    script = ASSET_DIR / "render_mesh_contact_sheet.py"
    out_path = out_dir / "fern_root_candidates_contact_sheet.png"
    cmd = [sys.executable, str(script), "--out", str(out_path), "--views", "iso", "front", "side", "--max-faces", str(max_faces)]
    for row in rows:
        cmd.extend(["--case", f"{row['case_id']}={row['mesh_path']}"])
    try:
        result = subprocess.run(cmd, cwd=str(ROOT_DIR), check=True, text=True, capture_output=True)
        return {"status": "ok", "path": str(out_path), "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except Exception as exc:
        return {"status": "failed", "path": str(out_path), "error": str(exc)}


def _write_readme(out_dir: Path, summary: Dict) -> None:
    text = """# Fern / Spider / Root Local Candidates

Produced by `assets/prepare_fern_root_candidates_20260511.py`.

Scope: local OBJ candidate generation only.  This script does not launch remote
jobs and does not modify the Trellis workflow.

Meshes use `procedural_baselines.pb.Mesh` plus a V22-style shared-center swept
support.  Semantic details are attached by shared-vertex faces.

Candidate count: {count}
Connectivity floor: largest-component vertex ratio >= {lcr}
Contact sheet: `{sheet}`
""".format(
        count=summary["num_cases"],
        lcr=CONNECTIVITY_LCR_MIN,
        sheet=summary.get("contact_sheet", {}).get("path", ""),
    )
    (out_dir / "README.md").write_text(text, encoding="utf-8")


def materialize(
    root: Path = ROOT_DIR,
    out_dir: Path = DEFAULT_OUT,
    seed: int = 20260511,
    case_limit: Optional[int] = None,
    render_preview: bool = True,
    preview_max_faces: int = 90000,
) -> Dict:
    root = Path(root)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    specs = _case_specs(seed)
    if case_limit is not None:
        specs = specs[: int(case_limit)]

    rows: List[Dict] = []
    metrics_rows: List[Dict] = []
    for spec in specs:
        case_dir = out_dir / spec["case_id"]
        mesh_path = case_dir / f"{spec['case_id']}.obj"
        _export_mesh(mesh_path, spec["mesh"])
        metrics = _mesh_stats(spec["mesh"])
        controls = dict(spec["controls"])
        metrics.update(
            {
                "semantic_detail_count": int(controls.get("semantic_detail_count", 0)),
                "leaflet_count": int(controls.get("leaflet_count", 0)),
                "rootlet_count": int(controls.get("rootlet_count", 0)),
                "tendril_count": int(controls.get("tendril_count", 0)),
                "support_node_count": int(controls.get("support_node_count", 0)),
                "support_edge_count": int(controls.get("support_edge_count", 0)),
            }
        )
        if metrics["largest_mesh_component_vertex_ratio"] < CONNECTIVITY_LCR_MIN:
            raise RuntimeError(f"{spec['case_id']} failed connectivity gate: {metrics}")
        metadata = _metadata_for(spec, mesh_path, metrics)
        metadata_path = case_dir / f"{spec['case_id']}_metadata.json"
        _write_json(metadata_path, metadata)

        row = {
            "case_id": spec["case_id"],
            "family": spec["family"],
            "motif": spec["motif"],
            "mesh_path": str(mesh_path),
            "metadata_path": str(metadata_path),
            "seed": int(spec["seed"]),
            "case_role": spec["case_role"],
            "operators": json.dumps(spec["operators"], ensure_ascii=False),
            "operator_composition": " -> ".join(spec["operators"]),
            "surface_strategy": SURFACE_STRATEGY,
            "local_generation_only": "true",
            "remote_jobs_launched": "false",
            "trellis_workflow_changed": "false",
            "shared_vertex_attachment": "true",
            "largest_mesh_component_vertex_ratio": metrics["largest_mesh_component_vertex_ratio"],
            "mesh_component_count": metrics["mesh_component_count"],
            "vertices": metrics["vertices"],
            "faces": metrics["faces"],
            "semantic_detail_count": metrics["semantic_detail_count"],
            "leaflet_count": metrics["leaflet_count"],
            "rootlet_count": metrics["rootlet_count"],
            "tendril_count": metrics["tendril_count"],
            "support_node_count": metrics["support_node_count"],
            "support_edge_count": metrics["support_edge_count"],
            "why_candidate": spec["why_candidate"],
        }
        rows.append(row)
        metrics_rows.append({"case_id": spec["case_id"], "family": spec["family"], "motif": spec["motif"], **metrics})

    manifest_fields = [
        "case_id",
        "family",
        "motif",
        "mesh_path",
        "metadata_path",
        "seed",
        "case_role",
        "operators",
        "operator_composition",
        "surface_strategy",
        "local_generation_only",
        "remote_jobs_launched",
        "trellis_workflow_changed",
        "shared_vertex_attachment",
        "largest_mesh_component_vertex_ratio",
        "mesh_component_count",
        "vertices",
        "faces",
        "semantic_detail_count",
        "leaflet_count",
        "rootlet_count",
        "tendril_count",
        "support_node_count",
        "support_edge_count",
        "why_candidate",
    ]
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerows(rows)
    _write_json(out_dir / "manifest.json", rows)

    metric_fields = sorted({key for row in metrics_rows for key in row.keys() if not isinstance(row.get(key), (list, dict))})
    with (out_dir / "initial_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        for row in metrics_rows:
            writer.writerow({key: row.get(key) for key in metric_fields})
    _write_json(out_dir / "initial_metrics.json", metrics_rows)

    contact = {"status": "skipped", "path": ""}
    if render_preview and rows:
        contact = _render_contact_sheet(out_dir, rows, max_faces=preview_max_faces)

    summary = {
        "out_dir": str(out_dir),
        "num_cases": len(rows),
        "source_script": str(ASSET_DIR / "prepare_fern_root_candidates_20260511.py"),
        "surface_strategy": SURFACE_STRATEGY,
        "mesh_format": "obj",
        "local_generation_only": True,
        "remote_jobs_launched": False,
        "trellis_workflow_changed": False,
        "connectivity_gate": {
            "largest_component_vertex_ratio_min": CONNECTIVITY_LCR_MIN,
            "all_cases_passed": all(float(row["largest_mesh_component_vertex_ratio"]) >= CONNECTIVITY_LCR_MIN for row in rows),
        },
        "families": sorted({row["family"] for row in rows}),
        "motifs": sorted({row["motif"] for row in rows}),
        "manifest_csv": str(out_dir / "manifest.csv"),
        "manifest_json": str(out_dir / "manifest.json"),
        "initial_metrics_csv": str(out_dir / "initial_metrics.csv"),
        "initial_metrics_json": str(out_dir / "initial_metrics.json"),
        "contact_sheet": contact,
        "case_ids": [row["case_id"] for row in rows],
    }
    _write_json(out_dir / "summary.json", summary)
    _write_readme(out_dir, summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("RGG_ROOT", ROOT_DIR)))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260511)
    parser.add_argument("--case-limit", type=int, default=None)
    parser.add_argument("--skip-preview", action="store_true")
    parser.add_argument("--preview-max-faces", type=int, default=90000)
    args = parser.parse_args()
    materialize(
        root=args.root,
        out_dir=args.out,
        seed=args.seed,
        case_limit=args.case_limit,
        render_preview=not args.skip_preview,
        preview_max_faces=args.preview_max_faces,
    )


if __name__ == "__main__":
    main()
