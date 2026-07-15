#!/usr/bin/env python3
"""V9 organic frontier strict matched DLA/coral/crystal input generator.

V9 is a fresh input-generation algorithm for the DLA/frontier/crystal rows. It
keeps the strict classical mode: stochastic frontier attachment with occupancy
exclusion. The geometry emitted from that mode is changed to address the V8
failure where results still read as smooth tubes or rods. V9 uses curved
multi-ring edges, sinusoidal radius modulation, asymmetric ridge fins, attached
perforated membranes, and many needle-like terminal tips while preserving one
connected mesh component before any remote Trellis2 generation.
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

import procedural_baselines as pb
import recursive_growth_mesh_metrics as rgm
import strict_visual_matched_cases_v6_connectivity_20260510 as v6
import strict_visual_matched_cases_v8_frontier_refine_20260510 as v8


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 100
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_v9_organic_frontier_20260510_dryrun"


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
    children: dict[int, list[int]] = {i: [] for i in range(count)}
    for a, b in edges:
        children.setdefault(int(a), []).append(int(b))
    return children


def _parents_from_edges(count: int, edges: list[tuple[int, int]]) -> list[int]:
    parents = [-1 for _ in range(count)]
    for a, b in edges:
        if b != 0 and parents[b] < 0:
            parents[b] = int(a)
    return parents


def _profile_tuning(profile: str) -> dict:
    table = {
        "coral_lace": {
            "source_profile": "coral_lace",
            "curvature": 0.070,
            "radius_scale": 0.58,
            "branchlet_limit": 190,
            "membrane_limit": 52,
            "ridge_limit": 135,
            "tip_limit": 170,
            "rings": 5,
            "sides": 10,
            "crystal": False,
        },
        "coral_plate": {
            "source_profile": "coral_table",
            "curvature": 0.052,
            "radius_scale": 0.54,
            "branchlet_limit": 160,
            "membrane_limit": 74,
            "ridge_limit": 125,
            "tip_limit": 145,
            "rings": 5,
            "sides": 10,
            "crystal": False,
        },
        "frontier_filigree": {
            "source_profile": "frontier_fan",
            "curvature": 0.045,
            "radius_scale": 0.50,
            "branchlet_limit": 150,
            "membrane_limit": 88,
            "ridge_limit": 120,
            "tip_limit": 135,
            "rings": 5,
            "sides": 9,
            "crystal": False,
        },
        "crystal_needle": {
            "source_profile": "crystal_blade",
            "curvature": 0.025,
            "radius_scale": 0.62,
            "branchlet_limit": 92,
            "membrane_limit": 34,
            "ridge_limit": 112,
            "tip_limit": 96,
            "rings": 4,
            "sides": 7,
            "crystal": True,
        },
    }
    return table[profile]


def _edge_curve(start: np.ndarray, end: np.ndarray, edge_index: int, curvature: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    axis = end - start
    u, v, _ = _basis(axis)
    phase = 0.73 * edge_index + rng.uniform(-0.45, 0.45)
    amp1 = curvature * rng.uniform(0.45, 1.15)
    amp2 = curvature * rng.uniform(-0.55, 0.75)
    return u * amp1 * math.cos(phase) + v * amp1 * math.sin(phase), v * amp2


def _curved_skeleton_mesh(
    nodes: list[np.ndarray],
    edges: list[tuple[int, int]],
    radii: list[float],
    seed: int,
    profile: str,
) -> tuple[pb.Mesh, dict]:
    tuning = _profile_tuning(profile)
    rng = np.random.default_rng(seed + 9101)
    mesh = pb.Mesh([], [])
    centers: list[int] = []
    for node in nodes:
        mesh.vertices.append(tuple(np.asarray(node, dtype=float)))
        centers.append(len(mesh.vertices))

    curved_edges = 0
    sides = int(tuning["sides"])
    rings = int(tuning["rings"])
    for edge_index, (a, b) in enumerate(v6._dedupe_edges(edges)):
        start = np.asarray(nodes[a], dtype=float)
        end = np.asarray(nodes[b], dtype=float)
        axis = end - start
        if float(np.linalg.norm(axis)) < 1e-7:
            continue
        u, v, _ = _basis(axis)
        bend1, bend2 = _edge_curve(start, end, edge_index, float(tuning["curvature"]), rng)
        ring_indices: list[list[int]] = []
        for r in range(1, rings + 1):
            t = r / (rings + 1)
            center = start * (1.0 - t) + end * t + math.sin(math.pi * t) * bend1 + math.sin(2.0 * math.pi * t) * bend2 * 0.45
            base_radius = (float(radii[a]) * (1.0 - t) + float(radii[b]) * t) * float(tuning["radius_scale"])
            ring: list[int] = []
            for i in range(sides):
                theta = 2.0 * math.pi * i / sides
                wrinkle = 1.0 + 0.18 * math.sin(3.0 * theta + edge_index * 0.71) + 0.08 * math.sin(7.0 * theta + r)
                radial = (math.cos(theta) * u + math.sin(theta) * v) * base_radius * wrinkle
                p = center + radial
                mesh.vertices.append(tuple(p))
                ring.append(len(mesh.vertices))
            ring_indices.append(ring)
        first = ring_indices[0]
        last = ring_indices[-1]
        ca, cb = centers[a], centers[b]
        for i in range(sides):
            j = (i + 1) % sides
            mesh.faces.append((ca, first[i], first[j]))
        for r in range(len(ring_indices) - 1):
            ring = ring_indices[r]
            next_ring = ring_indices[r + 1]
            for i in range(sides):
                j = (i + 1) % sides
                mesh.faces.append((ring[i], ring[j], next_ring[i]))
                mesh.faces.append((ring[j], next_ring[j], next_ring[i]))
        for i in range(sides):
            j = (i + 1) % sides
            mesh.faces.append((last[i], cb, last[j]))
        curved_edges += 1

    setattr(mesh, "center_indices", centers)
    return mesh, {
        "curved_branch_edges": curved_edges,
        "organic_surface_rings_per_edge": rings,
        "organic_surface_sides": sides,
        "straight_tube_suppression": "curved multi-ring edges with sinusoidal radius modulation",
    }


def _add_needle_tip(mesh: pb.Mesh, anchor_idx: int, anchor: np.ndarray, direction: np.ndarray, radius: float, length: float, sides: int) -> None:
    u, v, w = _basis(direction)
    radius = min(float(radius), 0.0062)
    anchor = np.asarray(anchor, dtype=float)
    base = len(mesh.vertices)
    ring: list[int] = []
    for i in range(sides):
        theta = 2.0 * math.pi * i / sides
        p = anchor + w * (length * 0.18) + (math.cos(theta) * u + math.sin(theta) * v) * radius
        mesh.vertices.append(tuple(p))
        ring.append(len(mesh.vertices))
    tip = anchor + w * float(length)
    mesh.vertices.append(tuple(tip))
    tip_idx = len(mesh.vertices)
    for i in range(sides):
        j = (i + 1) % sides
        mesh.faces.append((anchor_idx, ring[i], ring[j]))
        mesh.faces.append((ring[i], tip_idx, ring[j]))


def _add_curved_branchlet(
    mesh: pb.Mesh,
    anchor_idx: int,
    anchor: np.ndarray,
    direction: np.ndarray,
    seed_offset: int,
    length: float,
    radius0: float,
    radius1: float,
    sides: int,
) -> None:
    rng = np.random.default_rng(seed_offset)
    u, v, w = _basis(direction)
    bend = (u * rng.uniform(-0.050, 0.050) + v * rng.uniform(-0.050, 0.050))
    rings = 3
    ring_indices: list[list[int]] = []
    for r in range(1, rings + 1):
        t = r / (rings + 1)
        center = np.asarray(anchor, dtype=float) + w * length * t + math.sin(math.pi * t) * bend
        radius = (radius0 * (1.0 - t) + radius1 * t) * (1.0 + 0.12 * math.sin(seed_offset + t * 5.0))
        ring: list[int] = []
        for i in range(sides):
            theta = 2.0 * math.pi * i / sides
            p = center + (math.cos(theta) * u + math.sin(theta) * v) * radius
            mesh.vertices.append(tuple(p))
            ring.append(len(mesh.vertices))
        ring_indices.append(ring)
    first = ring_indices[0]
    for i in range(sides):
        j = (i + 1) % sides
        mesh.faces.append((anchor_idx, first[i], first[j]))
    for r in range(len(ring_indices) - 1):
        ring = ring_indices[r]
        next_ring = ring_indices[r + 1]
        for i in range(sides):
            j = (i + 1) % sides
            mesh.faces.append((ring[i], ring[j], next_ring[i]))
            mesh.faces.append((ring[j], next_ring[j], next_ring[i]))
    _add_needle_tip(mesh, ring_indices[-1][0], np.asarray(anchor, dtype=float) + w * length + bend * 0.15, w + bend, radius1, length * 0.28, sides)


def _add_ridge_fin(mesh: pb.Mesh, centers: list[int], nodes: list[np.ndarray], a: int, b: int, width: float, lift: float, side: float) -> None:
    pa = np.asarray(nodes[a], dtype=float)
    pb_ = np.asarray(nodes[b], dtype=float)
    axis = pb_ - pa
    if float(np.linalg.norm(axis)) < 1e-7:
        return
    u, v, _ = _basis(axis)
    normal = _unit(v * side + np.array([0.0, 0.0, lift]))
    mid = (pa + pb_) * 0.5
    base = len(mesh.vertices)
    mesh.vertices.extend(
        [
            tuple(pa + normal * width * 0.42),
            tuple(mid + normal * width * 1.35 + u * width * 0.18 * side),
            tuple(pb_ + normal * width * 0.42),
        ]
    )
    ca, cb = centers[a], centers[b]
    mesh.faces.append((ca, base + 1, base + 2))
    mesh.faces.append((ca, base + 2, cb))
    mesh.faces.append((cb, base + 2, base + 3))
    mesh.faces.append((cb, base + 3, ca))


def _add_perforated_membrane(
    mesh: pb.Mesh,
    centers: list[int],
    nodes: list[np.ndarray],
    a: int,
    b: int,
    width: float,
    lift: float,
    sides: int,
    seed_offset: int,
    faceted: bool,
) -> None:
    pa = np.asarray(nodes[a], dtype=float)
    pb_ = np.asarray(nodes[b], dtype=float)
    axis = pb_ - pa
    if float(np.linalg.norm(axis)) < 1e-7:
        return
    rng = np.random.default_rng(seed_offset)
    u, v, _ = _basis(axis)
    mid = (pa + pb_) * 0.5
    normal = _unit(v + np.array([0.0, 0.0, lift]))
    center = mid + normal * width * 0.82
    major = max(float(np.linalg.norm(axis)) * 0.42, width * 1.15)
    minor = width * (0.66 if faceted else 0.86)
    outer: list[int] = []
    inner: list[int] = []
    for i in range(sides):
        theta = 2.0 * math.pi * i / sides
        wobble = 1.0 if faceted else 1.0 + 0.14 * math.sin(3.0 * theta + seed_offset)
        ou = math.cos(theta) * major * wobble
        ov = math.sin(theta) * minor * (1.0 + rng.uniform(-0.06, 0.06))
        inn = 0.36 + 0.07 * math.sin(2.0 * theta + seed_offset)
        mesh.vertices.append(tuple(center + u * ou + normal * ov))
        outer.append(len(mesh.vertices))
        mesh.vertices.append(tuple(center + u * ou * inn + normal * ov * inn))
        inner.append(len(mesh.vertices))
    for i in range(sides):
        j = (i + 1) % sides
        mesh.faces.append((outer[i], outer[j], inner[i]))
        mesh.faces.append((outer[j], inner[j], inner[i]))
    mesh.faces.append((centers[a], outer[0], outer[1]))
    mesh.faces.append((centers[b], outer[sides // 2], outer[(sides // 2 + 1) % sides]))


def _decorate_organic_frontier(
    mesh: pb.Mesh,
    nodes: list[np.ndarray],
    edges: list[tuple[int, int]],
    radii: list[float],
    seed: int,
    profile: str,
) -> dict:
    tuning = _profile_tuning(profile)
    rng = np.random.default_rng(seed + 4201)
    centers = getattr(mesh, "center_indices")
    children = _children_from_edges(len(nodes), edges)
    parents = _parents_from_edges(len(nodes), edges)
    tips = [i for i in range(1, len(nodes)) if not children.get(i)]
    rng.shuffle(tips)

    branchlets = 0
    for idx in tips[: int(tuning["branchlet_limit"])]:
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        u, v, _ = _basis(axis)
        count = 1 if tuning["crystal"] else 2
        for k in range(count):
            direction = _unit(0.58 * axis + rng.normal(0.0, 0.72) * u + rng.normal(0.0, 0.72) * v + rng.normal(0.0, 0.045, 3))
            _add_curved_branchlet(
                mesh,
                centers[idx],
                nodes[idx],
                direction,
                seed + idx * 17 + k,
                length=float(rng.uniform(0.060, 0.150 if not tuning["crystal"] else 0.105)),
                radius0=max(float(radii[idx]) * 0.20, 0.0032),
                radius1=0.0034 if not tuning["crystal"] else 0.0046,
                sides=6 if not tuning["crystal"] else 5,
            )
            branchlets += 1

    needle_tips = 0
    for idx in tips[: int(tuning["tip_limit"])]:
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        _add_needle_tip(
            mesh,
            centers[idx],
            nodes[idx],
            axis,
            radius=0.0048 if not tuning["crystal"] else 0.0060,
            length=float(rng.uniform(0.050, 0.115 if not tuning["crystal"] else 0.090)),
            sides=6 if not tuning["crystal"] else 5,
        )
        needle_tips += 1

    ridges = 0
    ridge_step = max(len(edges) // int(tuning["ridge_limit"]), 1)
    for k, (a, b) in enumerate(edges[::ridge_step]):
        if ridges >= int(tuning["ridge_limit"]):
            break
        _add_ridge_fin(
            mesh,
            centers,
            nodes,
            a,
            b,
            width=0.020 if not tuning["crystal"] else 0.038,
            lift=0.08 if not tuning["crystal"] else 0.18,
            side=-1.0 if k % 2 else 1.0,
        )
        ridges += 1

    membranes = 0
    membrane_step = max(len(edges) // int(tuning["membrane_limit"]), 1)
    for k, (a, b) in enumerate(edges[::membrane_step]):
        if membranes >= int(tuning["membrane_limit"]):
            break
        if tuning["crystal"] and k % 3 == 1:
            continue
        _add_perforated_membrane(
            mesh,
            centers,
            nodes,
            a,
            b,
            width=0.032 if not tuning["crystal"] else 0.055,
            lift=0.11 if "frontier" in profile else 0.06,
            sides=8 if not tuning["crystal"] else 6,
            seed_offset=seed + k * 31,
            faceted=bool(tuning["crystal"]),
        )
        membranes += 1

    return {
        "attached_curved_branchlets": branchlets,
        "needle_tip_count": needle_tips + branchlets,
        "perforated_membrane_count": membranes,
        "ridge_fin_count": ridges,
        "thin_tip_radius_max": 0.0062,
        "surface_strategy": "single connected curved frontier skeleton with wrinkled tube sections, asymmetric ridge fins, perforated attached membranes, and needle-like terminal tips",
        "anti_rod_policy": "reduce smooth tube or straight rod reading through curve offsets, radius modulation, non-planar membranes, ridge fins, and many fine tips",
        "hole_policy": "membranes are annular face loops attached to scaffold centers, leaving explicit central holes while preserving component connectivity",
    }


def _organic_frontier_mesh(seed: int, profile: str) -> tuple[pb.Mesh, dict]:
    tuning = _profile_tuning(profile)
    nodes, edges, radii, controls = v8._stochastic_frontier_skeleton(seed, str(tuning["source_profile"]))
    radii = [float(r) * float(tuning["radius_scale"]) for r in radii]
    mesh, mesh_controls = _curved_skeleton_mesh(nodes, edges, radii, seed, profile)
    detail_controls = _decorate_organic_frontier(mesh, nodes, edges, radii, seed, profile)
    controls.update(mesh_controls)
    controls.update(detail_controls)
    controls["v9_profile"] = profile
    controls["source_frontier_profile"] = tuning["source_profile"]
    return mesh, controls


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
    }


def _write_guides(out_dir: Path) -> dict[str, str]:
    from PIL import Image, ImageDraw, ImageFilter

    guide_dir = out_dir / "_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)

    def stable_seed(name: str) -> int:
        return sum((i + 1) * b for i, b in enumerate(name.encode("utf-8"))) % (2**32)

    def save(name: str, bg: tuple[int, int, int], palette: list[tuple[int, int, int]], mode: str) -> str:
        rng = np.random.default_rng(stable_seed(name))
        img = Image.new("RGB", (768, 768), bg)
        draw = ImageDraw.Draw(img)
        for _ in range(980):
            c = palette[int(rng.integers(0, len(palette)))]
            x, y = int(rng.integers(0, 768)), int(rng.integers(0, 768))
            if mode == "crystal":
                r = int(rng.integers(9, 34))
                draw.polygon([(x, y - r), (x + r, y - r // 5), (x + r // 4, y + r), (x - r, y + r // 6)], outline=c, fill=None)
            else:
                width = int(rng.integers(1, 5))
                dx, dy = int(rng.normal(0, 110)), int(rng.normal(0, 82))
                draw.arc((x - 48, y - 32, x + 48, y + 32), start=int(rng.integers(0, 180)), end=int(rng.integers(181, 360)), fill=c, width=width)
                draw.line((x, y, x + dx, y + dy), fill=c, width=width)
                if rng.random() < 0.58:
                    rr = int(rng.integers(3, 13))
                    draw.ellipse((x - rr, y - rr, x + rr, y + rr), outline=c, width=1)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "pink_lace": save(
            "v9_pink_branching_lace_coral_guide.png",
            (188, 112, 112),
            [(255, 204, 168), (244, 132, 118), (255, 226, 190), (194, 80, 105), (118, 72, 86)],
            "coral",
        ),
        "ivory_porous": save(
            "v9_ivory_perforated_reef_guide.png",
            (188, 142, 116),
            [(255, 235, 198), (232, 180, 134), (205, 112, 103), (142, 88, 86), (255, 244, 214)],
            "coral",
        ),
        "fan_lace": save(
            "v9_frontier_fan_lace_guide.png",
            (132, 104, 102),
            [(246, 206, 166), (220, 150, 124), (172, 86, 96), (96, 76, 88), (250, 228, 188)],
            "coral",
        ),
        "crystal_needle": save(
            "v9_blue_needle_crystal_guide.png",
            (42, 50, 58),
            [(104, 132, 156), (164, 188, 198), (224, 222, 202), (74, 90, 110), (138, 154, 166)],
            "crystal",
        ),
    }


def _case_specs(seed: int) -> list[dict]:
    specs: list[dict] = []

    def add(case_id: str, target: str, profile: str, guide_key: str, case_seed: int, gpu: int, priority: bool, why: str) -> None:
        mesh, controls = _organic_frontier_mesh(case_seed, profile)
        operators = [
            "stochastic_frontier_attachment",
            "occupancy_exclusion",
            "curved_frontier_skeleton",
            "organic_tapered_surface",
            "needle_tip_closure",
            "perforated_attached_membranes",
            "asymmetric_ridge_fins",
        ]
        specs.append(
            {
                "case_id": case_id,
                "family": "DLA/frontier",
                "match_target": target,
                "traditional_target": target,
                "recursive_mode": "stochastic frontier attachment with occupancy exclusion and rooted accretive graph growth",
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

    add("v9_dla_coral_lace_branching_curve_a", "dla_coral_cluster_900", "coral_lace", "pink_lace", seed + 901, 4, True, "Same DLA coral cluster task and occupancy-excluded frontier mode; V9 changes the emitted root to curved branching, fine tips, porous holes, and ridge fins to avoid the V8 smooth tube or rod appearance. Must be generated fresh on a100-2.")
    add("v9_dla_coral_antler_filigree_tips", "dla_coral_cluster_900", "coral_lace", "ivory_porous", seed + 902, 5, True, "Strict coral/frontier accretion case with many thin antler-like terminal tips and attached perforated membranes while preserving a single rooted component for fresh a100-2 generation.")
    add("v9_dla_coral_open_reef_lace_b", "dla_coral_cluster_900", "coral_plate", "pink_lace", seed + 903, 6, True, "Matches DLA coral cluster through stochastic frontier attachment and occupancy exclusion, adding non-planar reef plates and holes rather than smooth capsules or block particles. Must be generated fresh on a100-2.")
    add("v9_dla_coral_porous_table_ridge", "dla_coral_cluster_900", "coral_plate", "ivory_porous", seed + 904, 7, True, "Same coral-cluster target with plate-biased accretion, curved branch supports, perforated sheets, and ridge fins to test whether V9 reduces V8 rod-like close zooms on a100-2.")
    add("v9_dla_frontier_fan_perforated_a", "dla_frontier_sheet_700", "frontier_filigree", "fan_lace", seed + 905, 4, True, "Same DLA frontier sheet target; the mesh remains one rooted accretive graph but uses fan-like curved supports plus hole-bearing membranes for a fresh a100-2 run.")
    add("v9_dla_frontier_ripple_lace_sheet", "dla_frontier_sheet_700", "frontier_filigree", "ivory_porous", seed + 906, 5, True, "Strict frontier-sheet comparison with boundary-biased accretion, rippled surfaces, attached holes, thin tips, and asymmetric ridge fins instead of smooth rods. Must be generated fresh on a100-2.")
    add("v9_dla_frontier_open_boundary_needles", "dla_frontier_sheet_700", "frontier_filigree", "pink_lace", seed + 907, 6, True, "Backup frontier sheet seed under the same stochastic attachment/exclusion rule, emphasizing open boundary lace and fine needle tips while keeping single-component input connectivity.")
    add("v9_dla_frontier_plate_ridge_seed_b", "dla_frontier_sheet_700", "coral_plate", "fan_lace", seed + 908, 7, False, "Backup frontier/reef plate seed with the same strict DLA frontier mode; intended to broaden remote selection without local post-hoc picking.")
    add("v9_dla_crystal_accretive_needles_a", "dla_crystal_cluster_520", "crystal_needle", "crystal_needle", seed + 909, 4, True, "Crystal/DLA boundary case using accretive attachment constrained by crystal-like directions, connected needle tips, and faceted ridge plates rather than floating shards. Must be generated fresh on a100-2.")
    add("v9_dla_crystal_frosted_blade_cluster", "dla_crystal_cluster_520", "crystal_needle", "crystal_needle", seed + 910, 5, True, "Same accretive crystal cluster task; V9 keeps one connected root while adding blade-like ridges and fine terminal points to avoid blocky mineral chunks.")
    add("v9_dla_crystal_ridge_fan_seed_b", "dla_crystal_cluster_520", "crystal_needle", "crystal_needle", seed + 911, 6, False, "Backup crystal frontier seed with connected faceted membranes, ridge fins, and needle tips under the same DLA/frontier rule for fresh a100-2 generation.")
    add("v9_dla_crystal_branching_prism_seed_c", "dla_crystal_cluster_520", "crystal_needle", "crystal_needle", seed + 912, 7, False, "Additional strict crystal accretion seed to test whether the V9 organic frontier geometry transfers to the crystal boundary case without detached shard components.")
    return specs


def _export_mesh(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


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
            "v8_failure_addressed": "V9 directly targets the V8/V8-thin smooth tube or rod failure by using curved branches, fine tips, holes, ridge fins, and non-flat local surfaces",
            "frontier_structure": "curved branches generated from stochastic frontier attachment, occupancy exclusion, attached perforated membranes, asymmetric ridges, and needle tips",
            "negative_constraint": "no cube block particles, no detached shards, no isolated sheet islands, no thick capsule/mushroom terminal fields, no local result selection after generation",
            "no_local_selection": "strict cases must be generated fresh on a100-2; local dry-run files are only root inputs",
        },
        "strict_generation_policy": "generate_new_on_a100_2_no_local_selection_or_posthoc_pick",
        "v9_design_note": "organic-frontier DLA/coral/crystal input algorithm, not a post-hoc mesh repair pass",
        "root_selection_log": {
            "root_source_type": "v9_organic_frontier_input_generator",
            "source_generator": "assets/strict_visual_matched_cases_v9_organic_frontier_20260510.py",
            "root_pool_size": 1,
            "root_generation_budget": "local CPU dry-run geometry only; final strict case must be generated fresh on a100-2",
            "root_screening_budget": "no local manual cherry-pick and no V1-V8 post-processing",
            "selection_rank": 1,
            "projection_naturalization_schedule": spec["operators"],
            "readiness_label": "remote_input_dryrun_organic_frontier_single_component",
            "connectivity_anchor_convention": "OBJ center vertices are shared by all curved edges, tips, ridge fins, and perforated membranes",
        },
    }


def _write_readme(out_dir: Path, summary: dict) -> None:
    text = f"""# V9 Organic Frontier Strict Visual-Matched Cases Dry Run

Generated by `assets/strict_visual_matched_cases_v9_organic_frontier_20260510.py`.

This is a local input dry-run only. It does not launch remote jobs, does not use
SSH, and does not pick or post-process V1-V8 outputs. Strict one-to-one visual
comparison cases must be generated fresh on `{REMOTE_TARGET}` with GPU ids
`{ALLOWED_GPUS}` under:

`{REMOTE_STORAGE_ROOT}`

Storage cap: `{STORAGE_LIMIT_GB}GB`.

V9 focus:

- DLA/coral/frontier/crystal only.
- Same stochastic frontier attachment and occupancy-exclusion mode.
- Initial OBJ inputs are gated to one mesh component.
- Geometry intentionally includes curved branches, fine tips, non-flat surfaces,
  perforated attached membranes, and asymmetric ridge fins.

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
