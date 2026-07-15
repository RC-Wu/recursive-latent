#!/usr/bin/env python3
"""Create root-stamped strict-matching plans for PS-RSLG candidates.

The generated JSON keeps the traditional procedural skeleton/point process as
the control source, while allowing the PS-RSLG candidate to instantiate higher
quality root tokens at anchors.  This follows the user's latest clarification:
the recursive task, category, coarse silhouette, depth, and growth mode must
match, but the root asset may be better than the primitive used by the
traditional baseline as long as provenance is logged.
"""

from __future__ import annotations

import argparse
import json
import math
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
from strict_matched_psrslg_proxy_20260510 import ifs_tree_skeleton
from strict_matched_task_targets_20260510 import fractal_lattice, make_frontier_sheet, radial_ornament


def _children(parents: list[int]) -> dict[int, list[int]]:
    out = {i: [] for i in range(len(parents))}
    for i, p in enumerate(parents):
        if p >= 0:
            out[p].append(i)
    return out


def _depths(parents: list[int]) -> list[int]:
    return bm.graph_depths(parents)


def _bbox_center_scale(nodes: list[np.ndarray]) -> tuple[np.ndarray, float]:
    arr = np.asarray(nodes, dtype=float)
    mn = arr.min(axis=0)
    mx = arr.max(axis=0)
    center = (mn + mx) * 0.5
    scale = float(np.max(mx - mn))
    return center, max(scale, 1e-6)


def _normalize_nodes(nodes: list[np.ndarray], target_extent: float = 8.0) -> list[np.ndarray]:
    center, scale = _bbox_center_scale(nodes)
    return [(np.asarray(n, dtype=float) - center) * (target_extent / scale) for n in nodes]


def _edge_records(nodes: list[np.ndarray], parents: list[int], base_radius: float, taper: float) -> list[dict]:
    depths = _depths(parents)
    max_depth = max(depths) if depths else 1
    edges = []
    for idx, parent in enumerate(parents):
        if parent < 0:
            continue
        f0 = depths[parent] / max(max_depth, 1)
        f1 = depths[idx] / max(max_depth, 1)
        r0 = max(base_radius * (1.0 - taper * f0), base_radius * 0.14)
        r1 = max(base_radius * (1.0 - taper * f1), base_radius * 0.10)
        edges.append(
            {
                "parent": parent,
                "child": idx,
                "start": np.asarray(nodes[parent], dtype=float).round(5).tolist(),
                "end": np.asarray(nodes[idx], dtype=float).round(5).tolist(),
                "radius0": round(float(r0), 5),
                "radius1": round(float(r1), 5),
            }
        )
    return edges


def _anchors_from_skeleton(
    nodes: list[np.ndarray],
    parents: list[int],
    max_tips: int,
    max_junctions: int,
    token_scale: float,
    token_kind: str,
) -> list[dict]:
    child_map = _children(parents)
    depths = _depths(parents)
    max_depth = max(depths) if depths else 1
    tips = [i for i in range(1, len(nodes)) if not child_map.get(i)]
    tips = sorted(tips, key=lambda i: depths[i], reverse=True)[:max_tips]
    junctions = [i for i in range(1, len(nodes)) if len(child_map.get(i, [])) >= 2]
    junctions = sorted(junctions, key=lambda i: (depths[i], len(child_map.get(i, []))), reverse=True)[:max_junctions]
    anchors: list[dict] = []
    for i in tips:
        parent = parents[i] if parents[i] >= 0 else i
        direction = np.asarray(nodes[i], dtype=float) - np.asarray(nodes[parent], dtype=float)
        norm = float(np.linalg.norm(direction)) or 1.0
        anchors.append(
            {
                "node": i,
                "role": "terminal_tip",
                "position": np.asarray(nodes[i], dtype=float).round(5).tolist(),
                "direction": (direction / norm).round(5).tolist(),
                "scale": round(token_scale * (0.75 + 0.35 * depths[i] / max(max_depth, 1)), 5),
                "token_kind": token_kind,
            }
        )
    for i in junctions:
        parent = parents[i] if parents[i] >= 0 else i
        direction = np.asarray(nodes[i], dtype=float) - np.asarray(nodes[parent], dtype=float)
        norm = float(np.linalg.norm(direction)) or 1.0
        anchors.append(
            {
                "node": i,
                "role": "junction",
                "position": np.asarray(nodes[i], dtype=float).round(5).tolist(),
                "direction": (direction / norm).round(5).tolist(),
                "scale": round(token_scale * 0.65, 5),
                "token_kind": token_kind,
            }
        )
    return anchors


def _case_from_skeleton(
    case_id: str,
    target_case: str,
    family: str,
    category: str,
    recursive_mode: str,
    controls: dict,
    nodes: list[np.ndarray],
    parents: list[int],
    root_asset: str | None,
    token_kind: str,
    token_scale: float,
    material_preset: str,
    max_tips: int = 24,
    max_junctions: int = 10,
    base_radius: float = 0.055,
    taper: float = 0.76,
) -> dict:
    nodes = _normalize_nodes(nodes)
    anchors = _anchors_from_skeleton(nodes, parents, max_tips=max_tips, max_junctions=max_junctions, token_scale=token_scale, token_kind=token_kind)
    return {
        "case_id": case_id,
        "matched_traditional_case": target_case,
        "family": family,
        "target_category": category,
        "recursive_mode": recursive_mode,
        "controls": controls,
        "root_asset": root_asset,
        "root_asset_policy": "higher-quality project/Trellis2 token allowed; final silhouette and recursive mode remain controlled by the traditional skeleton",
        "material_preset": material_preset,
        "nodes": [np.asarray(n, dtype=float).round(5).tolist() for n in nodes],
        "parents": parents,
        "edges": _edge_records(nodes, parents, base_radius=base_radius, taper=taper),
        "anchors": anchors,
        "selection_budget": {
            "current_candidate_index": 1,
            "planned_variants": ["token scale sweep", "tip-only vs tip+junction tokens", "root material preset sweep"],
            "paper_gate": "must match category/silhouette/depth and pass mesh/PBR visual zoom inspection",
        },
    }


def _dla_neighbor_edges(points: np.ndarray, max_edges: int = 1800) -> list[dict]:
    """Build a conservative connected support graph for DLA points."""
    pts = np.asarray(points, dtype=float)
    edges = []
    if len(pts) < 2:
        return edges
    # Connect each point to its nearest previous point.  This preserves the
    # accretive-tree spirit and is robust even when the original DLA order is
    # not available in the point set returned by the baseline helper.
    for idx in range(1, min(len(pts), max_edges)):
        prev = pts[:idx]
        j = int(np.argmin(np.linalg.norm(prev - pts[idx], axis=1)))
        dist = float(np.linalg.norm(prev[j] - pts[idx]))
        radius = max(0.018, min(0.050, dist * 0.045))
        edges.append(
            {
                "parent": j,
                "child": idx,
                "start": pts[j].round(5).tolist(),
                "end": pts[idx].round(5).tolist(),
                "radius0": round(radius, 5),
                "radius1": round(radius * 0.92, 5),
            }
        )
    return edges


def _case_from_points(
    case_id: str,
    target_case: str,
    family: str,
    category: str,
    recursive_mode: str,
    controls: dict,
    points: np.ndarray,
    root_asset: str | None,
    material_preset: str,
    max_anchors: int = 34,
) -> dict:
    pts = np.asarray(points, dtype=float)
    center = (pts.min(axis=0) + pts.max(axis=0)) * 0.5
    extent = max(float(np.max(pts.max(axis=0) - pts.min(axis=0))), 1e-6)
    pts = (pts - center) * (8.0 / extent)
    norms = np.linalg.norm(pts, axis=1)
    chosen = np.argsort(norms)[-max_anchors:][::-1]
    anchors = [
        {
            "node": int(i),
            "role": "frontier_particle",
            "position": pts[i].round(5).tolist(),
            "direction": (pts[i] / (float(np.linalg.norm(pts[i])) or 1.0)).round(5).tolist(),
            "scale": round(0.20 + 0.10 * (k % 3), 5),
            "token_kind": "coral_or_crystal_token",
        }
        for k, i in enumerate(chosen)
    ]
    return {
        "case_id": case_id,
        "matched_traditional_case": target_case,
        "family": family,
        "target_category": category,
        "recursive_mode": recursive_mode,
        "controls": controls,
        "root_asset": root_asset,
        "root_asset_policy": "frontier point set controls shape; root token adds local generated material/surface detail",
        "material_preset": material_preset,
        "nodes": pts.round(5).tolist(),
        "parents": [],
        "edges": _dla_neighbor_edges(pts),
        "anchors": anchors,
        "selection_budget": {
            "current_candidate_index": 1,
            "planned_variants": ["frontier token density", "bridge radius", "coral vs crystal token material"],
            "paper_gate": "DLA line remains boundary until blockiness and bead artifacts are reduced in zoom renders",
        },
    }


def build_plan(seed: int) -> dict:
    tree_root = "visuals/textured_glb_20260508/tree_compete_s3/textured.glb"
    vine_root = "visuals/textured_glb_20260508/vine_d5_compete_s5_inference/textured.glb"
    tree_roots_root = "visuals/public_guide_textured_glb_20260509/tree_compete_d4_pruned_tree_roots_steps8_tex2048_xformers/textured.glb"
    pyrite_root = "visuals/pyrite_depth_hq_warm_showcase_20260509/stage04_textured.glb"
    coral_root = "visuals/coral_density_extreme_texture_20260509/coral_density_param_density_0p25_octopus_steps8_tex2048_xformers/textured.glb"

    cases: list[dict] = []
    nodes, parents = bm.lsystem_case("tree", depth=5, seed=seed)
    cases.append(
        _case_from_skeleton(
            "lsys_pine_canopy_d5__rootstamped_tree_compete",
            "lsys_pine_canopy_d5",
            "L-system",
            "pine/tree canopy",
            "symbolic turtle branch rewriting; same branch depth and branching family as traditional target",
            {"depth": 5, "seed": seed, "branch_source": "baseline_matrix_20260509.lsystem_case(tree)"},
            nodes,
            parents,
            tree_root,
            "leafy_tree_token",
            0.115,
            "bark_leaf",
            max_tips=18,
            max_junctions=8,
            base_radius=0.080,
        )
    )

    nodes, parents = bm.lsystem_case("root", depth=5, seed=seed + 17)
    cases.append(
        _case_from_skeleton(
            "lsys_root_fan_d5__rootstamped_vine_roots",
            "lsys_root_fan_d5",
            "L-system",
            "root fan",
            "symbolic turtle root branching with downward tropism; same root fan topology",
            {"depth": 5, "seed": seed + 17, "branch_source": "baseline_matrix_20260509.lsystem_case(root)"},
            nodes,
            parents,
            tree_roots_root,
            "root_vine_token",
            0.110,
            "root_bark",
            max_tips=22,
            max_junctions=9,
            base_radius=0.070,
        )
    )

    # Reuse the explicit climbing-vine target generator by reconstructing its
    # centerline in the same style; this gives a better visual candidate than
    # the previous loose vine-stage substitution.
    vine_nodes = [np.zeros(3, dtype=float)]
    vine_parents = [-1]
    parent = 0
    rng = np.random.default_rng(seed + 29)
    for level in range(1, 7):
        theta = level * 0.82
        step = np.array([math.cos(theta) * 2.2, math.sin(theta) * 2.2, 5.2])
        vine_nodes.append(vine_nodes[parent] + step)
        current = len(vine_nodes) - 1
        vine_parents.append(parent)
        for sign in (-1, 1):
            side = pb.unit(np.array([math.cos(theta + sign * 1.35), math.sin(theta + sign * 1.35), 0.15]))
            tip = vine_nodes[current] + side * (2.8 + 0.35 * level) + rng.normal(0, 0.12, 3)
            vine_nodes.append(tip)
            vine_parents.append(current)
            if level >= 3:
                vine_nodes.append(tip + side * 1.35 + np.array([0.0, 0.0, 0.55]))
                vine_parents.append(len(vine_nodes) - 2)
        parent = current
    cases.append(
        _case_from_skeleton(
            "lsys_climbing_vine_d6__rootstamped_vine_stage5",
            "lsys_climbing_vine_d6",
            "L-system",
            "climbing vine",
            "curling main chain with recursive tendrils; same helix/tendril recursion",
            {"iterations": 6, "seed": seed + 29, "curl_step_radians": 0.82},
            vine_nodes,
            vine_parents,
            vine_root,
            "vine_leaf_token",
            0.100,
            "vine_leaf",
            max_tips=20,
            max_junctions=8,
            base_radius=0.050,
            taper=0.60,
        )
    )

    for sc_case, target_id, category, root_asset, token_kind, mat, max_tips in [
        ("tree_canopy", "sc_tree_crown_260", "tree crown", tree_root, "leafy_tree_token", "bark_leaf", 24),
        ("root_vine", "sc_root_network_260", "root network", vine_root, "root_vine_token", "root_bark", 24),
        ("bush_shell", "sc_bush_shell_220", "bush shell", tree_root, "leafy_bush_token", "bark_leaf", 28),
    ]:
        result = scb.grow_space_colonization(
            case=sc_case,
            attractor_count=1600 if sc_case != "bush_shell" else 1400,
            iterations=260 if sc_case != "bush_shell" else 220,
            influence_radius=0.24 if sc_case != "bush_shell" else 0.23,
            kill_radius=0.055 if sc_case != "bush_shell" else 0.060,
            step_size=0.045 if sc_case != "bush_shell" else 0.043,
            seed=seed + 100 + len(cases) * 41,
        )
        nodes = [np.asarray(p, dtype=float) * 84.0 for p in result["nodes"]]
        parents = [int(p) for p in result["parents"]]
        cases.append(
            _case_from_skeleton(
                f"{target_id}__rootstamped_{sc_case}",
                target_id,
                "Space colonization",
                category,
                "attractor competition with influence/kill radii; same attractor-growth task family",
                {
                    "case": sc_case,
                    "attractors": 1600 if sc_case != "bush_shell" else 1400,
                    "iterations": 260 if sc_case != "bush_shell" else 220,
                    "influence_radius": 0.24 if sc_case != "bush_shell" else 0.23,
                    "kill_radius": 0.055 if sc_case != "bush_shell" else 0.060,
                    "covered_attractors": result.get("covered_attractors", None),
                },
                nodes,
                parents,
                root_asset,
                token_kind,
                0.075 if sc_case == "tree_canopy" else 0.085,
                mat,
                max_tips=max_tips,
                max_junctions=10,
                base_radius=0.045,
            )
        )

    ifs_nodes, ifs_parents = ifs_tree_skeleton(depth=6)
    cases.append(
        _case_from_skeleton(
            "ifs_branch_tree_d6__rootstamped_transform_tree",
            "ifs_branch_tree_d6",
            "IFS/transform",
            "recursive branch tree",
            "contractive affine transform-copy branching; same 3-map transform tree family",
            {"depth": 6, "transforms": "strict_matched_task_targets.ifs_tree_skeleton"},
            ifs_nodes,
            ifs_parents,
            tree_root,
            "leafy_tree_token",
            0.090,
            "bark_leaf",
            max_tips=24,
            max_junctions=8,
            base_radius=0.045,
            taper=0.70,
        )
    )

    coral = pb.make_dla_cluster(n_particles=900, seed=seed % 10000)
    cases.append(
        _case_from_points(
            "dla_coral_cluster_900__rootstamped_coral_token",
            "dla_coral_cluster_900",
            "DLA/frontier",
            "coral porous cluster",
            "random-walk accretive particle attachment; frontier particles preserved as anchors",
            {"particles": 900, "seed": seed % 10000, "neighborhood": "6n"},
            coral,
            coral_root,
            "coral_octopus",
            max_anchors=26,
        )
    )

    frontier = make_frontier_sheet(seed + 719, particles=700)
    cases.append(
        _case_from_points(
            "dla_frontier_sheet_700__rootstamped_coral_frontier",
            "dla_frontier_sheet_700",
            "DLA/frontier",
            "frontier sheet dendrite",
            "boundary-seeded accretive frontier growth; sheet frontier controls silhouette",
            {"particles": 700, "seed": seed + 719, "seed_shape": "line_strip"},
            frontier,
            coral_root,
            "coral_octopus",
            max_anchors=30,
        )
    )

    # For lattice/radial tasks, use pyrite/bismuth root tokens but keep the
    # transform-generated node positions from the classical task.
    lattice_mesh = fractal_lattice(depth=4)
    lattice_nodes = [np.asarray(v, dtype=float) for v in lattice_mesh.vertices[:: max(1, len(lattice_mesh.vertices) // 120)]]
    cases.append(
        _case_from_points(
            "ifs_fractal_lattice_d4__rootstamped_pyrite_lattice",
            "ifs_fractal_lattice_d4",
            "IFS/transform",
            "fractal lattice ornament",
            "affine lattice transform-copy with recursive basis offsets",
            {"depth": 4, "basis": "axis-aligned 3D cross motif"},
            np.asarray(lattice_nodes, dtype=float),
            pyrite_root,
            "pyrite_gold",
            max_anchors=24,
        )
    )

    radial_mesh = radial_ornament(order=8, depth=4)
    radial_nodes = [np.asarray(v, dtype=float) for v in radial_mesh.vertices[:: max(1, len(radial_mesh.vertices) // 96)]]
    cases.append(
        _case_from_points(
            "ifs_radial_ornament_o8_d4__rootstamped_pyrite_radial",
            "ifs_radial_ornament_o8_d4",
            "IFS/transform",
            "radial fractal ornament",
            "radial transform-copy with scale decay; order-8 orbit preserved",
            {"order": 8, "depth": 4, "scale_decay": "1/(1+0.55*level)"},
            np.asarray(radial_nodes, dtype=float),
            pyrite_root,
            "pyrite_gold",
            max_anchors=28,
        )
    )

    return {
        "created_by": "strict_matched_root_stamped_plan_20260510.py",
        "seed": seed,
        "matching_rule": "same procedural task/mode/category/depth/coarse silhouette; better root tokens allowed with provenance and selection budget",
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT_DIR / "results" / "strict_matched_root_stamped_20260510" / "anchor_plan.json")
    parser.add_argument("--seed", type=int, default=20260510)
    args = parser.parse_args()
    plan = build_plan(args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"out": str(args.out), "cases": len(plan["cases"])}, indent=2))


if __name__ == "__main__":
    main()
