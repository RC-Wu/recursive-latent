#!/usr/bin/env python3
"""V8 frontier-refined strict matched DLA/coral/crystal input generator.

V8 keeps the traditional DLA/frontier premise: stochastic frontier attachment
with occupancy exclusion.  The change is the local geometry emitted from that
process.  Instead of voxel cubes, detached shards, or large bulb/capsule tips,
each case starts from one continuous center skeleton and adds smooth tapered
tubes, thin ridges/plates, small branchlets, and sparse edge-attached porous
membranes.
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

REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 100
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_v8_frontier_refine_20260510_dryrun"


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


def _profile_config(profile: str) -> dict:
    configs = {
        "coral_lace": {
            "nodes": 470,
            "exclusion": 0.038,
            "step": (0.040, 0.092),
            "anisotropy": np.array([1.06, 0.98, 1.18]),
            "up_bias": 0.10,
            "radial_bias": 0.50,
            "noise": np.array([0.62, 0.62, 0.52]),
            "sheet": 0.0,
            "crystal": False,
            "base_radius": 0.031,
            "tip_radius": 0.0065,
            "sides": 16,
            "extent": 2.38,
        },
        "coral_table": {
            "nodes": 430,
            "exclusion": 0.041,
            "step": (0.045, 0.103),
            "anisotropy": np.array([1.38, 1.22, 0.72]),
            "up_bias": 0.04,
            "radial_bias": 0.56,
            "noise": np.array([0.72, 0.62, 0.30]),
            "sheet": 0.35,
            "crystal": False,
            "base_radius": 0.029,
            "tip_radius": 0.006,
            "sides": 16,
            "extent": 2.42,
        },
        "frontier_fan": {
            "nodes": 390,
            "exclusion": 0.040,
            "step": (0.045, 0.105),
            "anisotropy": np.array([1.92, 1.18, 0.42]),
            "up_bias": 0.02,
            "radial_bias": 0.64,
            "noise": np.array([0.82, 0.46, 0.18]),
            "sheet": 0.75,
            "crystal": False,
            "base_radius": 0.027,
            "tip_radius": 0.0055,
            "sides": 14,
            "extent": 2.44,
        },
        "crystal_blade": {
            "nodes": 310,
            "exclusion": 0.046,
            "step": (0.055, 0.120),
            "anisotropy": np.array([1.12, 1.05, 0.62]),
            "up_bias": 0.00,
            "radial_bias": 0.70,
            "noise": np.array([0.22, 0.22, 0.10]),
            "sheet": 0.20,
            "crystal": True,
            "base_radius": 0.035,
            "tip_radius": 0.010,
            "sides": 8,
            "extent": 2.30,
        },
    }
    return configs[profile]


def _crystal_direction(rng: np.random.Generator, outward: np.ndarray, anisotropy: np.ndarray) -> np.ndarray:
    phi = (1.0 + 5.0**0.5) * 0.5
    dirs = np.array(
        [
            [1.0, phi, 0.0],
            [-1.0, phi, 0.0],
            [1.0, -phi, 0.0],
            [-1.0, -phi, 0.0],
            [0.0, 1.0, phi],
            [0.0, -1.0, phi],
            [0.0, 1.0, -phi],
            [0.0, -1.0, -phi],
            [phi, 0.0, 1.0],
            [-phi, 0.0, 1.0],
            [phi, 0.0, -1.0],
            [-phi, 0.0, -1.0],
        ],
        dtype=float,
    )
    dirs = np.array([_unit(d) for d in dirs])
    weights = np.maximum(dirs @ _unit(outward), -0.15) + 0.22
    base = dirs[int(rng.choice(len(dirs), p=weights / weights.sum()))]
    return _unit((base + rng.normal(0.0, 0.055, 3)) * anisotropy)


def _stochastic_frontier_skeleton(seed: int, profile: str) -> tuple[list[np.ndarray], list[tuple[int, int]], list[float], dict]:
    cfg = _profile_config(profile)
    rng = np.random.default_rng(seed)
    nodes: list[np.ndarray] = [np.zeros(3, dtype=float)]
    edges: list[tuple[int, int]] = []
    parents = [-1]
    frontier = [0]
    attempts = 0
    max_attempts = int(cfg["nodes"] * 28)

    while len(nodes) < int(cfg["nodes"]) and attempts < max_attempts:
        attempts += 1
        if rng.random() < 0.82:
            scores = np.array([0.32 + np.linalg.norm(nodes[i]) for i in frontier], dtype=float)
            parent = int(rng.choice(frontier, p=scores / scores.sum()))
        else:
            parent = int(rng.integers(0, len(nodes)))

        base = np.asarray(nodes[parent], dtype=float)
        parent_vec = _unit(base - nodes[parents[parent]]) if parents[parent] >= 0 else np.array([0.0, 0.0, 1.0])
        outward = _unit(base) if np.linalg.norm(base) > 1e-6 else _unit(rng.normal(0.0, 1.0, 3))
        if cfg["crystal"]:
            direction = _crystal_direction(rng, outward + 0.35 * parent_vec, cfg["anisotropy"])
        else:
            direction = (
                float(cfg["radial_bias"]) * outward
                + 0.28 * parent_vec
                + rng.normal(0.0, 1.0, 3) * cfg["noise"]
                + np.array([0.0, 0.0, float(cfg["up_bias"])])
            )
            if float(cfg["sheet"]) > 0.0:
                direction[2] *= 1.0 - float(cfg["sheet"]) * 0.78
                direction[0] += float(cfg["sheet"]) * 0.22 * np.sign(base[0] + rng.normal(0.0, 0.02))
            direction = _unit(direction * cfg["anisotropy"])

        length = float(rng.uniform(*cfg["step"]))
        point = base + direction * length
        if float(cfg["sheet"]) > 0.0 and not cfg["crystal"]:
            point[2] += rng.normal(0.0, 0.010 + 0.010 * (1.0 - float(cfg["sheet"])))

        exclusion = float(cfg["exclusion"]) * rng.uniform(0.88, 1.16)
        if min(float(np.linalg.norm(point - q)) for q in nodes) < exclusion:
            continue

        idx = len(nodes)
        nodes.append(point)
        edges.append((parent, idx))
        parents.append(parent)
        frontier.append(idx)
        if rng.random() < 0.18 and parent in frontier and parent != 0:
            frontier.remove(parent)
        if len(frontier) > 190:
            frontier = frontier[-155:]

    nodes = v6._normalize_nodes(nodes, float(cfg["extent"]))
    arr = np.asarray(nodes, dtype=float)
    norms = np.linalg.norm(arr, axis=1)
    denom = max(float(norms.max()), 1e-6)
    radii = [
        max(float(cfg["base_radius"]) * (1.0 - 0.62 * (float(norm) / denom)), float(cfg["tip_radius"]))
        for norm in norms
    ]
    return nodes, edges, radii, {
        "profile": profile,
        "nodes_target": int(cfg["nodes"]),
        "generated_nodes": len(nodes),
        "skeleton_edges": len(edges),
        "attempts": attempts,
        "occupancy_exclusion_radius": float(cfg["exclusion"]),
        "frontier_attachment_bias": "weighted active frontier with occasional older-node reseeding",
        "anisotropy": [float(x) for x in cfg["anisotropy"]],
        "smooth_tube_sides": int(cfg["sides"]),
        "center_skeleton_policy": "single rooted attachment tree before any surface detail",
    }


def _add_attached_tapered_tube(
    mesh: pb.Mesh,
    anchor_idx: int,
    anchor: np.ndarray,
    direction: np.ndarray,
    length: float,
    radius0: float,
    radius1: float,
    sides: int,
    rings: int = 3,
) -> None:
    u, v, w = _basis(direction)
    anchor = np.asarray(anchor, dtype=float)
    ring_indices: list[list[int]] = []
    for r in range(rings):
        t = (r + 1) / rings
        center = anchor + w * float(length) * t
        radius = float(radius0) * (1.0 - t) + float(radius1) * t
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
    tip = anchor + w * float(length) * 1.08
    mesh.vertices.append(tuple(tip))
    tip_idx = len(mesh.vertices)
    last = ring_indices[-1]
    for i in range(sides):
        j = (i + 1) % sides
        mesh.faces.append((last[i], last[j], tip_idx))


def _add_ridge_plate(mesh: pb.Mesh, center_indices: list[int], nodes: list[np.ndarray], a: int, b: int, width: float, lift: float) -> None:
    pa = np.asarray(nodes[a], dtype=float)
    pb_ = np.asarray(nodes[b], dtype=float)
    axis = pb_ - pa
    if float(np.linalg.norm(axis)) < 1e-7:
        return
    u, v, _ = _basis(axis)
    normal = _unit(v + np.array([0.0, 0.0, lift]))
    mid = (pa + pb_) * 0.5
    base = len(mesh.vertices)
    mesh.vertices.extend(
        [
            tuple(pa + normal * width * 0.48),
            tuple(mid + normal * width * 1.05 + u * width * 0.35),
            tuple(pb_ + normal * width * 0.48),
        ]
    )
    ca, cb = center_indices[a], center_indices[b]
    mesh.faces.append((ca, base + 1, base + 2))
    mesh.faces.append((ca, base + 2, cb))
    mesh.faces.append((cb, base + 2, base + 3))
    mesh.faces.append((cb, base + 3, ca))


def _decorate_frontier_mesh(
    mesh: pb.Mesh,
    nodes: list[np.ndarray],
    edges: list[tuple[int, int]],
    radii: list[float],
    seed: int,
    profile: str,
) -> dict:
    rng = np.random.default_rng(seed + 3001)
    centers = getattr(mesh, "center_indices")
    parents = [-1 for _ in nodes]
    for a, b in edges:
        if b != 0 and parents[b] < 0:
            parents[b] = a
    child_map = v6._children(parents)
    tips = [i for i in range(1, len(nodes)) if not child_map.get(i)]
    rng.shuffle(tips)

    branchlets = 0
    branchlet_cap = 135 if "crystal" not in profile else 70
    for idx in tips[:branchlet_cap]:
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        u, v, _ = _basis(axis)
        for _ in range(1 if "crystal" in profile else 2):
            direction = _unit(
                0.62 * axis
                + rng.normal(0.0, 0.60) * u
                + rng.normal(0.0, 0.60) * v
                + rng.normal(0.0, 0.05, 3)
            )
            _add_attached_tapered_tube(
                mesh,
                centers[idx],
                nodes[idx],
                direction,
                length=float(rng.uniform(0.050, 0.125)),
                radius0=max(radii[idx] * 0.34, 0.0032),
                radius1=max(radii[idx] * 0.10, 0.0014),
                sides=8 if "crystal" not in profile else 6,
                rings=3,
            )
            branchlets += 1

    ridges = 0
    ridge_stride = max(len(edges) // (120 if "crystal" not in profile else 90), 1)
    for a, b in edges[::ridge_stride]:
        _add_ridge_plate(mesh, centers, nodes, a, b, width=0.026 if "crystal" not in profile else 0.042, lift=0.16 if "crystal" in profile else 0.06)
        ridges += 1

    membranes = 0
    membrane_stride = max(len(edges) // (42 if "frontier" in profile or "table" in profile else 34), 1)
    for a, b in edges[::membrane_stride]:
        if "crystal" in profile and membranes % 2 == 1:
            continue
        v6._add_edge_sheet(
            mesh,
            centers,
            nodes,
            a,
            b,
            width=0.030 if "crystal" not in profile else 0.050,
            lift=0.12 if "frontier" in profile else 0.08,
            faceted="crystal" in profile,
        )
        membranes += 1

    return {
        "attached_small_scale_branchlets": branchlets,
        "attached_thin_plate_ridges": ridges,
        "edge_attached_porous_membranes": membranes,
        "surface_strategy": "continuous center skeleton plus smooth tapered tubes, small branchlets, thin plate/ridge details, and sparse edge-attached porous membranes",
        "anti_block_policy": "no cube voxels, no detached shards, no global implicit blob, and no large terminal capsule field",
    }


def _frontier_refined_mesh(seed: int, profile: str) -> tuple[pb.Mesh, dict]:
    nodes, edges, radii, controls = _stochastic_frontier_skeleton(seed, profile)
    sides = int(_profile_config(profile)["sides"])
    mesh = v6.welded_skeleton_mesh(nodes, edges, radii, sides=sides)
    detail_controls = _decorate_frontier_mesh(mesh, nodes, edges, radii, seed, profile)
    controls.update(detail_controls)
    return mesh, controls


def _mesh_stats(path: Path) -> dict:
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
        for _ in range(720):
            c = palette[int(rng.integers(0, len(palette)))]
            x, y = int(rng.integers(0, 768)), int(rng.integers(0, 768))
            if mode == "crystal":
                r = int(rng.integers(10, 42))
                skew = int(rng.integers(-12, 13))
                draw.polygon([(x, y - r), (x + r + skew, y), (x, y + r), (x - r + skew, y)], outline=c, fill=None)
            else:
                width = int(rng.integers(2, 7))
                dx, dy = int(rng.normal(0, 96)), int(rng.normal(0, 70))
                draw.line((x, y, x + dx, y + dy), fill=c, width=width)
                if rng.random() < 0.42:
                    rr = int(rng.integers(4, 14))
                    draw.ellipse((x - rr, y - rr, x + rr, y + rr), outline=c, width=2)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "warm_coral": save(
            "v8_warm_lace_coral_guide.png",
            (176, 94, 86),
            [(255, 186, 132), (238, 118, 91), (255, 222, 170), (198, 82, 91), (124, 68, 82)],
            "coral",
        ),
        "ivory_reef": save(
            "v8_ivory_porous_reef_guide.png",
            (180, 126, 104),
            [(250, 224, 182), (231, 174, 132), (205, 104, 100), (130, 86, 91), (255, 239, 198)],
            "coral",
        ),
        "frontier_lace": save(
            "v8_frontier_lace_membrane_guide.png",
            (128, 107, 106),
            [(240, 202, 166), (216, 148, 125), (164, 88, 99), (96, 82, 94), (252, 230, 188)],
            "coral",
        ),
        "crystal_blue": save(
            "v8_blue_blade_crystal_guide.png",
            (48, 56, 62),
            [(105, 129, 150), (165, 183, 190), (218, 216, 197), (76, 91, 110), (137, 151, 160)],
            "crystal",
        ),
    }


def _case_specs(seed: int) -> list[dict]:
    specs: list[dict] = []

    def add(
        case_id: str,
        traditional_target: str,
        profile: str,
        guide_key: str,
        case_seed: int,
        gpu: int,
        priority: bool,
        why: str,
    ) -> None:
        mesh, controls = _frontier_refined_mesh(case_seed, profile)
        operators = [
            "stochastic_frontier_attachment",
            "occupancy_exclusion",
            "continuous_center_skeleton",
            "smooth_tube_surface",
            "thin_plate_ridge_details",
            "small_scale_branching",
            "edge_attached_porous_membranes",
        ]
        specs.append(
            {
                "case_id": case_id,
                "family": "DLA/frontier",
                "match_target": traditional_target,
                "traditional_target": traditional_target,
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

    add(
        "v8_dla_coral_lace_reef_branching_a",
        "dla_coral_cluster_900",
        "coral_lace",
        "warm_coral",
        seed + 301,
        4,
        True,
        "Preserves stochastic DLA/coral frontier accretion but replaces blocky particles and V7 capsule tips with a continuous lace-like center skeleton, smooth tapered branches, and attached porous membrane edges for fresh on a100-2 generation.",
    )
    add(
        "v8_dla_coral_antler_ridge_branching",
        "dla_coral_cluster_900",
        "coral_lace",
        "ivory_reef",
        seed + 302,
        5,
        True,
        "Same coral-cluster recursive family as the traditional baseline; small-scale attached branchlets and ridge plates make the root input read as coral/reef rather than isolated rounded blobs when regenerated fresh on a100-2.",
    )
    add(
        "v8_dla_coral_porous_table_reef",
        "dla_coral_cluster_900",
        "coral_table",
        "ivory_reef",
        seed + 303,
        6,
        True,
        "Keeps occupancy-excluded frontier attachment while biasing growth into a porous reef-table scaffold with sparse edge-attached membranes, intended for strict fresh on a100-2 one-to-one comparison.",
    )
    add(
        "v8_dla_frontier_fan_lace_membrane_a",
        "dla_frontier_sheet_700",
        "frontier_fan",
        "frontier_lace",
        seed + 304,
        7,
        True,
        "Matches the line/frontier sheet target through accretive boundary-biased attachment while using thin connected tubes and sparse membranes instead of blocky sheet fragments; final case must be generated fresh on a100-2.",
    )
    add(
        "v8_dla_frontier_terraced_ridge_sheet",
        "dla_frontier_sheet_700",
        "frontier_fan",
        "ivory_reef",
        seed + 305,
        4,
        True,
        "Same DLA/frontier boundary task, with continuous skeleton plus terraced ridge details to reduce chunky rock silhouettes during fresh a100-2 regeneration.",
    )
    add(
        "v8_dla_frontier_open_boundary_seed_b",
        "dla_frontier_sheet_700",
        "frontier_fan",
        "warm_coral",
        seed + 306,
        5,
        False,
        "Backup seed for the same stochastic frontier-sheet comparison; structure remains a rooted occupancy-excluded frontier tree with edge-attached porous membranes for fresh on a100-2 generation.",
    )
    add(
        "v8_dla_crystal_accretive_blade_cluster",
        "dla_crystal_cluster_520",
        "crystal_blade",
        "crystal_blue",
        seed + 307,
        6,
        True,
        "Targets the crystal/DLA boundary with stochastic accretive attachment constrained to crystal-like directions, connected ridges, and faceted plates rather than floating shards; final output must be generated fresh on a100-2.",
    )
    add(
        "v8_dla_crystal_pyrite_ridge_cluster",
        "dla_crystal_cluster_520",
        "crystal_blade",
        "crystal_blue",
        seed + 308,
        7,
        True,
        "Preserves the accretive crystal cluster comparison while forming one connected ridge-and-plate scaffold, reducing V6/V7 block and mushroom artifacts for fresh on a100-2 generation.",
    )
    add(
        "v8_dla_coral_lace_reef_branching_b",
        "dla_coral_cluster_900",
        "coral_table",
        "warm_coral",
        seed + 309,
        4,
        False,
        "Second coral/reef seed for robustness: stochastic frontier attachment plus occupancy exclusion, continuous center skeleton, smooth tubes, and sparse attached membranes for fresh on a100-2 generation.",
    )
    add(
        "v8_dla_crystal_frontier_prism_seed_b",
        "dla_crystal_cluster_520",
        "crystal_blade",
        "crystal_blue",
        seed + 310,
        5,
        False,
        "Backup crystal frontier seed using the same accretive/exclusion rule with connected prism-like ridges and plates, not local post-processing or cherry-picking; intended for fresh on a100-2 generation.",
    )
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
            "why_strict_one_to_one": f"{spec['why_matches_traditional']} Must be generated fresh on a100-2.",
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
            "dryrun_visual_floor": "initial OBJ must be single or near-single component before remote generation; component quality is a gate, not the final visual claim",
            "v7_failure_addressed": "reduce blocky DLA/coral/frontier outputs and avoid V7 capsule or mushroom-like terminal blobs by changing the stochastic input algorithm",
            "frontier_structure": "continuous center skeleton, smooth tapered tubes, thin plates/ridges, small-scale branching, and sparse edge-attached porous membranes",
            "negative_constraint": "no isolated block chunks, no floating membrane islands, no detached crystal shards, no local result selection after generation",
            "no_local_selection": "strict cases must be generated fresh on a100-2; local dry-run files are only root inputs",
        },
        "strict_generation_policy": "generate_new_on_a100_2_no_local_selection_or_posthoc_pick",
        "v8_design_note": "frontier-refined DLA/coral/crystal input algorithm, not a post-hoc mesh selection pass",
        "root_selection_log": {
            "root_source_type": "v8_frontier_refine_input_generator",
            "source_generator": "assets/strict_visual_matched_cases_v8_frontier_refine_20260510.py",
            "root_pool_size": 1,
            "root_generation_budget": "local CPU dry-run geometry only; final strict case must be generated fresh on a100-2",
            "root_screening_budget": "no local manual cherry-pick and no V1-V7 post-processing",
            "selection_rank": 1,
            "projection_naturalization_schedule": spec["operators"],
            "readiness_label": "remote_input_dryrun_frontier_refined_near_single_component",
            "connectivity_anchor_convention": "OBJ vertices 1..N include shared scaffold centers used by faces; all details are face-attached to centers or edges",
        },
    }


def _write_readme(out_dir: Path, summary: dict) -> None:
    text = f"""# V8 Frontier Refine Strict Visual-Matched Cases Dry Run

Generated by `assets/strict_visual_matched_cases_v8_frontier_refine_20260510.py`.

This is a local input dry-run only. It does not launch remote jobs, does not use
SSH, and does not pick or post-process V1-V7 outputs. Strict one-to-one visual
comparison cases must be generated fresh on `{REMOTE_TARGET}` with GPU ids
`{ALLOWED_GPUS}` under:

`{REMOTE_STORAGE_ROOT}`

Storage cap: `{STORAGE_LIMIT_GB}GB`.

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
        metrics = _mesh_stats(mesh_path)
        if metrics["mesh_component_count"] > 2 or metrics["largest_mesh_component_vertex_ratio"] < 0.985:
            raise RuntimeError(f"{spec['case_id']} is not single/near-single component: {metrics}")
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
