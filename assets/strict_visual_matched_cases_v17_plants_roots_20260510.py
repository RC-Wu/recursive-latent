#!/usr/bin/env python3
"""V17 strict visual-matched plant/root Trellis2 input generator.

V17 is a fresh generator for the plant/tree/root cases where V6/V15 stayed too
rod-like. It keeps the same classical task modes as the traditional baselines:
L-system tree/root/vine and space-colonization tree/root/bush. The output is
mesh input plus PBR guide images only; final results must be generated fresh on
a100-2 GPU ids 4/5/6/7.
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
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_v17_plants_roots_20260510_dryrun"

HIGH_QUALITY_SOURCE_REFERENCES = [
    "visuals/textured_glb_20260508/tree_compete_s3/textured.glb",
    "visuals/textured_glb_20260508/vine_d5_compete_s5_inference/textured.glb",
    "visuals/public_guide_textured_glb_20260509/tree_compete_d4_pruned_tree_roots_steps8_tex2048_xformers/textured.glb",
    "visuals/programmatic_pbr_renders_20260508/tree_auto_iso.png",
    "visuals/programmatic_pbr_renders_20260508/vine_auto_iso.png",
]


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _basis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = _unit(np.asarray(axis, dtype=float))
    seed = np.array([0.0, 0.0, 1.0]) if abs(w[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = _unit(np.cross(w, seed))
    v = _unit(np.cross(w, u))
    return u, v, w


def _normalize_nodes(nodes: list[np.ndarray], extent: float = 2.40) -> list[np.ndarray]:
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


def _terminal_nodes(parents: list[int]) -> list[int]:
    child_map = _children(parents)
    return [idx for idx in range(1, len(parents)) if not child_map.get(idx)]


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
    return [max(base * (1.0 - taper * (depth / max(max_depth, 1))) ** 1.08, floor) for depth in depths]


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


def _swept_botanical_support_mesh(
    nodes: list[np.ndarray],
    edges: list[tuple[int, int]],
    radii: list[float],
    sides: int = 14,
    ovality: float = 0.22,
) -> pb.Mesh:
    """Connected tapered sweep mesh with scaffold centers welded into faces."""

    mesh = pb.Mesh([], [])
    center_indices: list[int] = []
    for node in nodes:
        mesh.vertices.append(tuple(np.asarray(node, dtype=float)))
        center_indices.append(len(mesh.vertices))

    incident_rings: list[list[list[int]]] = [[] for _ in nodes]
    for edge_i, (a, b) in enumerate(_dedupe_edges(edges)):
        start = np.asarray(nodes[a], dtype=float)
        end = np.asarray(nodes[b], dtype=float)
        axis = end - start
        if float(np.linalg.norm(axis)) < 1e-7:
            continue
        u, v, _ = _basis(axis)
        twist = 0.35 * math.sin(edge_i * 1.73)
        base = len(mesh.vertices)
        for endpoint, radius in ((start, radii[a]), (end, radii[b])):
            for i in range(sides):
                theta = 2.0 * math.pi * i / sides + twist
                profile = 1.0 + ovality * math.sin(theta * 2.0 + edge_i * 0.37)
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
            s = ridx % sides
            mesh.faces.append((ring[s], ring[(s + 1) % sides], next_ring[s]))
            mesh.faces.append((ring[(s + 1) % sides], next_ring[(s + 1) % sides], next_ring[s]))

    setattr(mesh, "center_indices", center_indices)
    return mesh


def _add_edge_sleeve(
    mesh: pb.Mesh,
    center_indices: list[int],
    nodes: list[np.ndarray],
    a: int,
    b: int,
    width: float,
    lift: float,
    phase: float,
) -> None:
    pa = np.asarray(nodes[a], dtype=float)
    pb_ = np.asarray(nodes[b], dtype=float)
    axis = pb_ - pa
    if float(np.linalg.norm(axis)) < 1e-7:
        return
    u, v, _ = _basis(axis)
    normal = _unit(math.cos(phase) * u + math.sin(phase) * v + np.array([0.0, 0.0, lift]))
    tangent = _unit(np.cross(normal, _unit(axis)))
    mid = (pa + pb_) * 0.5 + normal * width * 0.52
    base = len(mesh.vertices)
    pts = [
        pa * 0.72 + pb_ * 0.28 + normal * width * 0.36 + tangent * width * 0.34,
        mid + normal * width * 0.56 + tangent * width * 0.62,
        pb_ * 0.72 + pa * 0.28 + normal * width * 0.38 - tangent * width * 0.30,
        mid + normal * width * 0.92 - tangent * width * 0.58,
    ]
    mesh.vertices.extend([tuple(p) for p in pts])
    ca = center_indices[a]
    cb = center_indices[b]
    mesh.faces.append((ca, base + 1, base + 2))
    mesh.faces.append((ca, base + 2, cb))
    mesh.faces.append((cb, base + 3, base + 4))
    mesh.faces.append((cb, base + 4, ca))
    mesh.faces.append((base + 1, base + 3, base + 2))
    mesh.faces.append((base + 3, base + 4, base + 2))


def _add_leaf_lamina(mesh: pb.Mesh, anchor_idx: int, anchor: np.ndarray, normal: np.ndarray, scale: float, aspect: float) -> None:
    u, v, w = _basis(normal)
    c = np.asarray(anchor, dtype=float) + w * scale * 0.72
    base = len(mesh.vertices)
    pts = [
        c + v * scale * aspect,
        c + u * scale * 0.42,
        c - v * scale * aspect * 0.82,
        c - u * scale * 0.42,
        c + w * scale * 0.24,
    ]
    mesh.vertices.extend([tuple(p) for p in pts])
    mesh.faces.append((anchor_idx, base + 1, base + 2))
    mesh.faces.append((anchor_idx, base + 2, base + 3))
    mesh.faces.append((anchor_idx, base + 3, base + 4))
    mesh.faces.append((anchor_idx, base + 4, base + 1))
    for i in range(4):
        j = (i + 1) % 4
        mesh.faces.append((base + i + 1, base + j + 1, base + 5))


def _add_root_plate(mesh: pb.Mesh, anchor_idx: int, anchor: np.ndarray, normal: np.ndarray, scale: float) -> None:
    u, v, w = _basis(normal)
    c = np.asarray(anchor, dtype=float) + w * scale * 0.35
    base = len(mesh.vertices)
    pts = [
        c + u * scale * 1.10,
        c + v * scale * 0.55,
        c - u * scale * 0.90,
        c - v * scale * 0.48,
        c + w * scale * 0.34,
    ]
    mesh.vertices.extend([tuple(p) for p in pts])
    mesh.faces.append((anchor_idx, base + 1, base + 2))
    mesh.faces.append((anchor_idx, base + 2, base + 3))
    mesh.faces.append((anchor_idx, base + 3, base + 4))
    mesh.faces.append((anchor_idx, base + 4, base + 1))
    mesh.faces.append((base + 1, base + 2, base + 5))
    mesh.faces.append((base + 2, base + 3, base + 5))
    mesh.faces.append((base + 3, base + 4, base + 5))
    mesh.faces.append((base + 4, base + 1, base + 5))


def _add_terminal_bud(mesh: pb.Mesh, anchor_idx: int, center: np.ndarray, direction: np.ndarray, radius: float, rings: int = 3, sides: int = 8) -> None:
    u, v, w = _basis(direction)
    base_rings: list[list[int]] = []
    for r in range(rings):
        t = (r + 1) / rings
        ring_center = np.asarray(center, dtype=float) + w * radius * (0.42 + 0.64 * t)
        ring_radius = radius * math.sin(t * math.pi * 0.86) * (1.02 - 0.12 * r)
        ring: list[int] = []
        for i in range(sides):
            theta = 2.0 * math.pi * i / sides
            mesh.vertices.append(tuple(ring_center + (math.cos(theta) * u + math.sin(theta) * v) * ring_radius))
            ring.append(len(mesh.vertices))
        base_rings.append(ring)
    tip = np.asarray(center, dtype=float) + w * radius * 1.36
    mesh.vertices.append(tuple(tip))
    tip_idx = len(mesh.vertices)
    first = base_rings[0]
    for i in range(sides):
        mesh.faces.append((anchor_idx, first[i], first[(i + 1) % sides]))
    for ring, next_ring in zip(base_rings, base_rings[1:]):
        for i in range(sides):
            j = (i + 1) % sides
            mesh.faces.append((ring[i], ring[j], next_ring[i]))
            mesh.faces.append((ring[j], next_ring[j], next_ring[i]))
    last = base_rings[-1]
    for i in range(sides):
        mesh.faces.append((last[i], last[(i + 1) % sides], tip_idx))


def _decorate_botanical_surface(
    mesh: pb.Mesh,
    nodes: list[np.ndarray],
    parents: list[int],
    edges: list[tuple[int, int]],
    rng: np.random.Generator,
    kind: str,
) -> dict:
    centers = getattr(mesh, "center_indices")
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    sleeves = 0
    pbr_regions = 0

    unique_edges = _dedupe_edges(edges)
    step = max(len(unique_edges) // 120, 1)
    for e_i, (a, b) in enumerate(unique_edges[::step]):
        if sleeves >= 140:
            break
        lift = -0.22 if kind == "root" else 0.18
        width = 0.025 if kind == "root" else 0.035
        _add_edge_sleeve(mesh, centers, nodes, a, b, width=width, lift=lift, phase=e_i * 0.83)
        sleeves += 1
        pbr_regions += 1

    terminal = _terminal_nodes(parents)
    if kind in {"pine", "crown", "bush"}:
        anchors = [i for i in range(1, len(nodes)) if depths[i] >= max_depth * 0.58]
        rng.shuffle(anchors)
        for idx in anchors[:150 if kind != "bush" else 190]:
            parent = parents[idx] if parents[idx] >= 0 else idx
            axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
            repeats = 2 if kind == "pine" else 1
            for _ in range(repeats):
                normal = axis + np.array([0.0, 0.0, 0.28]) + rng.normal(0, 0.18, 3)
                _add_leaf_lamina(mesh, centers[idx], nodes[idx], normal, rng.uniform(0.028, 0.052), 2.4 if kind == "pine" else 1.35)
                pbr_regions += 1
        for idx in terminal[:80]:
            parent = parents[idx] if parents[idx] >= 0 else idx
            axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
            _add_terminal_bud(mesh, centers[idx], nodes[idx], axis + np.array([0.0, 0.0, 0.14]), 0.020 if kind == "pine" else 0.025)
            pbr_regions += 1
    elif kind == "vine":
        for idx in terminal[:110]:
            parent = parents[idx] if parents[idx] >= 0 else idx
            axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
            _add_leaf_lamina(mesh, centers[idx], nodes[idx], axis + rng.normal(0, 0.22, 3), 0.060, 1.65)
            pbr_regions += 1
        for a, b in unique_edges[::2][:100]:
            _add_edge_sleeve(mesh, centers, nodes, a, b, width=0.030, lift=0.10, phase=rng.uniform(0, math.tau))
            sleeves += 1
            pbr_regions += 1
    elif kind == "root":
        for idx in terminal[:190]:
            parent = parents[idx] if parents[idx] >= 0 else idx
            axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
            _add_root_plate(mesh, centers[idx], nodes[idx], -axis + np.array([0.0, 0.0, -0.30]), rng.uniform(0.020, 0.038))
            pbr_regions += 1

    return {"fused_branch_sleeve_count": sleeves, "pbr_surface_region_count": pbr_regions}


def _finalize_controls(base: dict, branch_edges: int, decorations: dict, root_hairs: int = 0) -> dict:
    controls = dict(base)
    controls.update(
        {
            "same_classical_task_mode": True,
            "connected_swept_botanical_surface": True,
            "reference_seeded_root_source_strategy": True,
            "mesh_pbr_output_only": True,
            "connectivity_gate_lcr_min": CONNECTIVITY_LCR_MIN,
            "tapered_branch_edges": int(branch_edges),
            "connected_root_hairs": int(root_hairs),
            "fused_branch_sleeve_count": int(decorations.get("fused_branch_sleeve_count", 0)),
            "pbr_surface_region_count": int(decorations.get("pbr_surface_region_count", 0)),
            "direct_voxel_blocks": False,
            "grape_ball_primitives": 0,
            "rod_scaffold_only": False,
            "local_selection_or_postprocess": False,
            "surface_strategy": controls.get(
                "surface_strategy",
                "reference-seeded connected botanical swept surface with fused sleeves and attached PBR regions",
            ),
        }
    )
    return controls


def lsystem_pine_case(seed: int) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 17)
    nodes0, parents = bm.lsystem_case("tree", depth=5, seed=seed)
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in nodes0], 2.48)
    radii = _radii_from_parents(parents, base=0.102, taper=0.76, floor=0.014)
    edges = _graph_edges(parents)
    mesh = _swept_botanical_support_mesh(nodes, edges, radii, sides=16, ovality=0.27)
    decorations = _decorate_botanical_surface(mesh, nodes, parents, edges, rng, "pine")
    controls = _finalize_controls(
        {
            "source": "baseline_matrix_20260509.lsystem_case(tree)",
            "depth": 5,
            "root_source_anchor_count": 3,
            "reference_profile": "tree_compete_s3 trunk/canopy root-source distribution plus tree_auto_iso PBR tonal guide",
            "surface_strategy": "reference-seeded connected pine canopy with oval trunk sweeps, fused branch sleeves, buds, and needle laminae",
        },
        len(edges),
        decorations,
    )
    return mesh, controls


def lsystem_root_case(seed: int) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 23)
    nodes0, parents = bm.lsystem_case("root", depth=5, seed=seed)
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in nodes0], 2.58)
    radii = _radii_from_parents(parents, base=0.092, taper=0.84, floor=0.0065)
    depths = bm.graph_depths(parents)
    original = len(nodes)
    anchors = [idx for idx in range(1, original) if depths[idx] >= 2]
    for idx in anchors:
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(nodes[idx] - nodes[parent])
        u, v, _ = _basis(axis)
        for _ in range(3 + int(depths[idx] >= 4)):
            direction = _unit(-0.25 * axis + rng.normal(0, 0.85) * u + rng.normal(0, 0.85) * v + np.array([0.0, 0.0, -0.62]))
            _append_child(nodes, parents, radii, idx, direction, rng.uniform(0.060, 0.175), rng.uniform(0.0026, 0.0048))
    edges = _graph_edges(parents)
    mesh = _swept_botanical_support_mesh(nodes, edges, radii, sides=12, ovality=0.34)
    decorations = _decorate_botanical_surface(mesh, nodes, parents, edges, rng, "root")
    root_hairs = len(nodes) - original
    controls = _finalize_controls(
        {
            "source": "baseline_matrix_20260509.lsystem_case(root)",
            "depth": 5,
            "root_source_anchor_count": 6,
            "reference_profile": "public pruned tree roots GLB root plate spread plus tree_auto_iso bark/root PBR guide",
            "surface_strategy": "reference-seeded connected root fan with flattened root plates, fused rhizome sleeves, and dense connected rootlets",
        },
        len(edges),
        decorations,
        root_hairs,
    )
    return mesh, controls


def lsystem_vine_case(seed: int) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 29)
    nodes: list[np.ndarray] = [np.zeros(3, dtype=float)]
    parents: list[int] = [-1]
    radii: list[float] = [0.066]
    parent = 0
    for level in range(1, 13):
        theta = level * 0.74
        step = np.array([math.cos(theta) * 0.20, math.sin(theta) * 0.20, 0.34])
        current = _append_child(nodes, parents, radii, parent, step, 1.0, max(0.060 * (0.88**level), 0.010))
        for sign in (-1, 1):
            side = _unit(np.array([math.cos(theta + sign * 1.28), math.sin(theta + sign * 1.28), 0.10]))
            tendril = _append_child(nodes, parents, radii, current, side + rng.normal(0, 0.035, 3), 0.24 + 0.012 * level, 0.010)
            curl_parent = tendril
            for curl in range(2):
                curl_dir = _unit(side * (0.55 - 0.12 * curl) + np.array([0.0, 0.0, 0.22]) + rng.normal(0, 0.10, 3))
                curl_parent = _append_child(nodes, parents, radii, curl_parent, curl_dir, 0.10 + 0.012 * curl, 0.0055)
        parent = current
    nodes = _normalize_nodes(nodes, 2.45)
    edges = _graph_edges(parents)
    mesh = _swept_botanical_support_mesh(nodes, edges, radii, sides=12, ovality=0.30)
    decorations = _decorate_botanical_surface(mesh, nodes, parents, edges, rng, "vine")
    controls = _finalize_controls(
        {
            "source": "V17 hand-authored L-system vine equivalent to baseline_matrix_20260509.lsystem_case(vine)",
            "iterations": 6,
            "root_source_anchor_count": 4,
            "reference_profile": "vine_d5_compete_s5_inference GLB curl/source placement plus vine_auto_iso PBR guide",
            "surface_strategy": "reference-seeded connected climbing vine with swept curls, fused tendril sleeves, and attached leaf laminae",
        },
        len(edges),
        decorations,
    )
    return mesh, controls


def space_colonization_case(sc_case: str, seed: int, mode: str) -> tuple[pb.Mesh, dict]:
    attractors = 1600 if sc_case != "bush_shell" else 1400
    iterations = 260 if sc_case != "bush_shell" else 230
    result = scb.grow_space_colonization(
        case=sc_case,
        attractor_count=attractors,
        iterations=iterations,
        influence_radius=0.220 if sc_case != "bush_shell" else 0.235,
        kill_radius=0.052 if sc_case != "bush_shell" else 0.060,
        step_size=0.041 if sc_case != "bush_shell" else 0.040,
        seed=seed,
    )
    rng = np.random.default_rng(seed + 41)
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in result["nodes"]], 2.44)
    parents = [int(p) for p in result["parents"]]
    base_radius = 0.084 if mode == "tree" else 0.088
    radii = _radii_from_parents(parents, base=base_radius, taper=0.83, floor=0.0058)
    original = len(nodes)
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    anchors = [i for i in range(1, original) if depths[i] >= max_depth * 0.50 or i in _terminal_nodes(parents)]
    rng.shuffle(anchors)
    root_hairs = 0
    if mode == "root":
        for idx in anchors[:130]:
            parent = parents[idx] if parents[idx] >= 0 else idx
            axis = _unit(nodes[idx] - nodes[parent])
            u, v, _ = _basis(axis)
            for _ in range(2):
                direction = _unit(-0.16 * axis + rng.normal(0, 0.80) * u + rng.normal(0, 0.80) * v + np.array([0.0, 0.0, -0.54]))
                _append_child(nodes, parents, radii, idx, direction, rng.uniform(0.054, 0.135), rng.uniform(0.0028, 0.0050))
                root_hairs += 1
    elif mode == "tree":
        for idx in anchors[:95]:
            parent = parents[idx] if parents[idx] >= 0 else idx
            axis = _unit(nodes[idx] - nodes[parent])
            _append_child(nodes, parents, radii, idx, axis + np.array([0.0, 0.0, 0.20]) + rng.normal(0, 0.20, 3), rng.uniform(0.035, 0.075), 0.006)
    edges = _graph_edges(parents)
    mesh = _swept_botanical_support_mesh(nodes, edges, radii, sides=12, ovality=0.29)
    kind = "root" if mode == "root" else ("bush" if sc_case == "bush_shell" else "crown")
    decorations = _decorate_botanical_surface(mesh, nodes, parents, edges, rng, kind)
    controls = _finalize_controls(
        {
            "source": "space_colonization_baseline.grow_space_colonization",
            "case": sc_case,
            "attractor_count": attractors,
            "iterations": iterations,
            "covered_attractors": result.get("covered_attractors"),
            "alive_attractors": result.get("alive_attractors"),
            "branch_nodes": original,
            "terminal_attachment_children": len(nodes) - original,
            "root_source_anchor_count": 5 if mode == "root" else 3,
            "reference_profile": (
                "public pruned tree roots GLB source fan"
                if mode == "root"
                else "tree_compete_s3 GLB crown/source placement and tree_auto_iso PBR guide"
            ),
            "surface_strategy": (
                "reference-seeded connected SC root network with fused rhizome sleeves and root plates"
                if mode == "root"
                else "reference-seeded connected SC crown/bush with fused branch sleeves and attached leaf/bud PBR regions"
            ),
        },
        len(edges),
        decorations,
        root_hairs,
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
        for _ in range(820):
            c = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(28, 740))
            y = int(rng.integers(28, 740))
            if motif == "pine":
                draw.line((x, y, x + int(rng.normal(0, 54)), y + int(rng.normal(-28, 34))), fill=c, width=int(rng.integers(1, 4)))
            elif motif == "root":
                draw.line((x, y, x + int(rng.normal(0, 96)), y + int(rng.normal(42, 48))), fill=c, width=int(rng.integers(2, 8)))
                if rng.random() < 0.28:
                    draw.ellipse((x - 3, y - 2, x + 8, y + 5), fill=c)
            elif motif == "vine":
                r = int(rng.integers(12, 54))
                draw.arc((x - r, y - r, x + r, y + r), 10, 330, fill=c, width=int(rng.integers(2, 5)))
            else:
                r = int(rng.integers(7, 26))
                draw.ellipse((x - r, y - r, x + r, y + r), fill=c)
                draw.line((x, y, x + int(rng.normal(0, 40)), y + int(rng.normal(-28, 28))), fill=c, width=2)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "pine": save("v17_reference_seeded_pine_pbr_guide.png", (18, 36, 24), [(40, 83, 42), (92, 124, 66), (138, 132, 78), (82, 52, 31)], "pine"),
        "root": save("v17_reference_seeded_root_pbr_guide.png", (28, 22, 17), [(72, 49, 31), (123, 82, 48), (164, 119, 74), (23, 17, 13)], "root"),
        "vine": save("v17_reference_seeded_vine_pbr_guide.png", (21, 45, 31), [(48, 95, 49), (96, 139, 68), (139, 102, 52), (56, 36, 25)], "vine"),
        "leaf": save("v17_reference_seeded_leaf_crown_pbr_guide.png", (24, 51, 34), [(54, 105, 53), (106, 144, 72), (150, 121, 64), (41, 34, 26)], "leaf"),
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
        why: str,
        gpu: int,
    ) -> None:
        operators = [
            "same_classical_recursive_mode",
            "reference_seeded_root_source_strategy",
            "connected_swept_botanical_surface",
            "fused_branch_sleeve_envelope",
            "attached_pbr_surface_regions",
            "mesh_pbr_output_only",
            "no_local_selection",
        ]
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
                "case_role": "priority_a100_2",
            }
        )

    mesh, ctl = lsystem_pine_case(seed + 1)
    add(
        "v17_lsys_pine_canopy_d5_reference_sleeved_needled_mass",
        "L-system",
        "lsys_pine_canopy_d5",
        "symbolic turtle branch rewriting, depth 5, pine/tree canopy",
        mesh,
        "pine",
        seed + 101,
        ctl,
        "Same depth-5 tree L-system target; V17 changes only the source/surface strategy to reference-seeded connected botanical sleeves and needle mass, generated fresh on a100-2.",
        4,
    )

    mesh, ctl = lsystem_root_case(seed + 2)
    add(
        "v17_lsys_root_fan_d5_reference_rhizome_plate_network",
        "L-system",
        "lsys_root_fan_d5",
        "symbolic turtle root branching with downward tropism, depth 5",
        mesh,
        "root",
        seed + 102,
        ctl,
        "Same depth-5 root/tropism grammar; V17 uses a higher-quality root/source fan with connected rootlets and root plates instead of rod/card proxies.",
        5,
    )

    mesh, ctl = lsystem_vine_case(seed + 3)
    add(
        "v17_lsys_climbing_vine_d6_reference_leafy_swept_curl",
        "L-system",
        "lsys_climbing_vine_d6",
        "curling main chain with recursive tendrils, six iterations",
        mesh,
        "vine",
        seed + 103,
        ctl,
        "Same six-step climbing vine mode; V17 uses the vine GLB/PBR source style for connected curled tendrils and attached leaf surface regions.",
        6,
    )

    mesh, ctl = space_colonization_case("tree_canopy", seed + 11, "tree")
    add(
        "v17_sc_tree_crown_260_reference_leaf_bud_crown",
        "Space colonization",
        "sc_tree_crown_260",
        "tree crown attractor competition with influence/kill radii",
        mesh,
        "leaf",
        seed + 111,
        ctl,
        "Same space-colonization tree-crown attractor mode; V17 keeps the attractor competition and adds connected botanical surface sleeves and leaf/bud PBR regions.",
        4,
    )

    mesh, ctl = space_colonization_case("root_vine", seed + 12, "root")
    add(
        "v17_sc_root_network_260_reference_connected_root_source_web",
        "Space colonization",
        "sc_root_network_260",
        "root/vine attractor competition in below-ground volume",
        mesh,
        "root",
        seed + 112,
        ctl,
        "Same SC root-network attractor field; V17 uses reference-seeded connected root source placement with dense rootlets and fused rhizome sleeves.",
        5,
    )

    mesh, ctl = space_colonization_case("bush_shell", seed + 13, "tree")
    add(
        "v17_sc_bush_shell_220_reference_connected_leaf_shell",
        "Space colonization",
        "sc_bush_shell_220",
        "bush-shell attractor competition with outward terminal coverage",
        mesh,
        "leaf",
        seed + 113,
        ctl,
        "Same SC bush-shell outward attractor coverage; V17 replaces bare shell rods with connected swept sleeves and attached leaf/bud PBR regions.",
        7,
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
        "connected_root_hairs": int(controls.get("connected_root_hairs", 0)),
        "fused_branch_sleeve_count": int(controls.get("fused_branch_sleeve_count", 0)),
        "pbr_surface_region_count": int(controls.get("pbr_surface_region_count", 0)),
        "root_source_anchor_count": int(controls.get("root_source_anchor_count", 0)),
    }


def _metadata_for(spec: dict, mesh_path: Path, guide_path: str, metrics: dict) -> dict:
    operator_family = {
        "L-system": "traditional L-system symbolic rewrite",
        "Space colonization": "traditional space-colonization attractor competition",
    }[spec["family"]]
    positive = "reference-seeded connected botanical mesh/PBR surface with fused branch sleeves"
    if "root" in spec["traditional_target"]:
        positive += " and connected root source fan/rootlet geometry"
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
            "negative_constraint": "no detached proxy cards, no pure rod scaffold, no grape-like primitive balls, no voxel blocks, no local repair/postprocess substitution",
            "failure_addressed": "V15/V6 plant, tree, vine, and root cases were connected but still read as rod/proxy geometry; V17 uses higher-quality reference-seeded root/source placement and botanical mesh surfaces.",
            "no_local_selection": "strict cases must be generated fresh on a100-2; local dry-run files are inputs, not selected final outputs",
        },
        "strict_generation_policy": "generate_new_on_a100_2_no_local_selection_or_posthoc_pick",
        "v17_design_note": "fresh plant/root branch using high-quality visual references for root/source strategy while preserving the classical recursive comparison target",
        "root_selection_log": {
            "root_source_type": "v17_reference_seeded_botanical_input_generator",
            "source_generator": "assets/strict_visual_matched_cases_v17_plants_roots_20260510.py",
            "high_quality_source_references": HIGH_QUALITY_SOURCE_REFERENCES,
            "root_pool_size": 1,
            "root_generation_budget": "local CPU dry-run geometry only; final strict case must be generated fresh on a100-2",
            "root_screening_budget": "no local manual cherry-pick, no V6/V15 post-processing, no selection of existing textured outputs",
            "selection_rank": 1,
            "projection_naturalization_schedule": spec["operators"],
            "readiness_label": "remote_input_dryrun_lcr_ge_0.999_visual_reference_seeded",
            "connectivity_anchor_convention": "OBJ vertices 1..N are shared scaffold centers used by faces; sleeves, laminae, root plates, and buds attach by shared vertices",
        },
    }


def _write_readme(out_dir: Path, summary: dict) -> None:
    text = f"""# V17 Plant/Root Strict Visual-Matched Cases Dry Run

Produced by `assets/strict_visual_matched_cases_v17_plants_roots_20260510.py`.

This is an input batch only. It does not launch remote jobs, locally select
outputs, or post-process V6/V15 assets. Final strict one-to-one cases must be
generated fresh on `{REMOTE_TARGET}` with GPU ids `{ALLOWED_GPUS}` under:

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
            raise RuntimeError(f"{spec['case_id']} failed V17 connectivity gate: {metrics}")
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
        metrics_rows.append({"case_id": spec["case_id"], "match_target": spec["match_target"], "traditional_target": spec["traditional_target"], **metrics})

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
        "connected_root_hairs",
        "fused_branch_sleeve_count",
        "pbr_surface_region_count",
        "root_source_anchor_count",
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
        "surface_generator": "visual_reference_seeded_connected_botanical_v17",
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
