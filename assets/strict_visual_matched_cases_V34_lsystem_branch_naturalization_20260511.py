#!/usr/bin/env python3
"""V34 L-system branch-with-side-branches naturalization inputs.

The V24/V23 L-system branch candidates remained too schematic: side branches
read as smooth tubes inserted into a main branch, terminal caps were exposed,
and Trellis2 texturing could amplify the junction seams.  V34 keeps the strict
L-system target -- a finite branch with recursive side branches -- but changes
the grammar-owned local realization before export: short segmented support,
object-space junction collars, fused cambium lobes, bark ridges, structural
splits, compact terminal buds, and a low-contrast whole-object guide.

This is intentionally claim-bounded.  The image guide is a whole-object
Trellis2 texture guide; there is no 2D seam-inpaint backprojection claim.
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
from PIL import Image, ImageDraw, ImageFilter

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import baseline_matrix_20260509 as bm
import procedural_baselines as pb
import strict_visual_matched_cases_V22_botanical_smooth_20260510 as v22
import strict_visual_matched_cases_V23_all_family_20260510 as v23
import strict_visual_matched_cases_V26_sc_tree_seam_naturalization_20260511 as v26
import strict_visual_matched_cases_V27_sc_tree_organic_seam_20260511 as v27
import strict_visual_matched_cases_V28_sc_tree_flare_bark_naturalization_20260511 as v28


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
DEFAULT_ACTIVE_GPUS = [4, 5]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 200
CONNECTIVITY_LCR_MIN = 0.999
EXTERNAL_SUPPORT_MAX_SEGMENT_GATE = 0.125
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V34_lsystem_branch_naturalization_20260511_dryrun"

SURFACE_STRATEGY = "v34_lsystem_branch_sidebranch_masked_naturalization"
GENERATION_POLICY = "generate_new_on_a100_2_no_local_selection_or_postprocessing"
SELECTION_BUDGET = "four_predeclared_lsystem_branch_candidates_local_qa_then_two_gpu_remote"
MESH_PBR_POLICY = "obj_inputs_lsystem_branch_guides_for_trellis2_glb_export_no_2d_backprojection_claim"


DetailCounts = Dict[str, int]


def _blank_counts() -> DetailCounts:
    return {
        "needle_count": 0,
        "leaf_count": 0,
        "rootlet_count": 0,
        "tendril_count": 0,
        "bud_count": 0,
        "flare_count": 0,
        "ridge_count": 0,
        "split_count": 0,
        "collar_count": 0,
        "cambium_lobe_count": 0,
    }


def _merge_counts(*parts: DetailCounts) -> DetailCounts:
    out = _blank_counts()
    for part in parts:
        for key, value in part.items():
            out[key] = int(out.get(key, 0)) + int(value)
    return out


def _append_node(nodes: List[np.ndarray], parents: List[int], parent: int, point: np.ndarray) -> int:
    nodes.append(np.asarray(point, dtype=float))
    parents.append(int(parent))
    return len(nodes) - 1


def _depths(parents: List[int]) -> List[int]:
    return bm.graph_depths(parents)


def _rot(axis: np.ndarray, angle: float) -> np.ndarray:
    return bm.rotation_matrix(np.asarray(axis, dtype=float), float(angle))


def _subdivide_long_edges(
    nodes: List[np.ndarray],
    parents: List[int],
    *,
    max_segment: float,
) -> Tuple[List[np.ndarray], List[int], Dict]:
    new_nodes: List[np.ndarray] = []
    new_parents: List[int] = []
    old_to_new: Dict[int, int] = {}
    inserted = 0
    for old_idx, point in enumerate(nodes):
        parent = int(parents[old_idx])
        if parent < 0:
            old_to_new[old_idx] = len(new_nodes)
            new_nodes.append(np.asarray(point, dtype=float).copy())
            new_parents.append(-1)
            continue
        parent_new = old_to_new[parent]
        parent_pos = np.asarray(new_nodes[parent_new], dtype=float)
        child_pos = np.asarray(point, dtype=float)
        dist = float(np.linalg.norm(child_pos - parent_pos))
        segments = max(1, int(math.ceil(dist / max(float(max_segment), 1e-6))))
        last_parent = parent_new
        for s in range(1, segments):
            t = s / float(segments)
            interp = parent_pos * (1.0 - t) + child_pos * t
            new_nodes.append(interp)
            new_parents.append(last_parent)
            last_parent = len(new_nodes) - 1
            inserted += 1
        old_to_new[old_idx] = len(new_nodes)
        new_nodes.append(child_pos.copy())
        new_parents.append(last_parent)

    lengths = [
        float(np.linalg.norm(new_nodes[idx] - new_nodes[parent]))
        for idx, parent in enumerate(new_parents)
        if parent >= 0
    ]
    return new_nodes, new_parents, {
        "short_segment_subdivision_enabled": True,
        "short_segment_max_gate": float(max_segment),
        "short_segment_inserted_nodes": int(inserted),
        "external_support_max_segment_after_subdivision": float(max(lengths) if lengths else 0.0),
        "external_support_mean_segment_after_subdivision": float(np.mean(lengths) if lengths else 0.0),
    }


def _lsystem_branch_graph(
    seed: int,
    *,
    main_steps: int,
    side_depth: int,
    side_every: int,
    double_sides: bool,
    main_curve: float,
    side_angle: float,
    side_length: float,
) -> Tuple[List[np.ndarray], List[int], Dict]:
    """Create a finite L-system-style branch with recursive side branches."""

    rng = np.random.default_rng(seed + 3401)
    nodes: List[np.ndarray] = [np.zeros(3, dtype=float)]
    parents: List[int] = [-1]
    main_indices = [0]
    direction = v22._unit(np.array([0.34, 0.04, 0.94], dtype=float))
    length = 1.0
    parent = 0
    junction_count = 0
    terminal_side_count = 0

    def add_recursive_side(parent_idx: int, base_dir: np.ndarray, length0: float, depth: int, phase: float) -> None:
        nonlocal junction_count, terminal_side_count
        if depth <= 0:
            terminal_side_count += 1
            return
        parent_pos = np.asarray(nodes[parent_idx], dtype=float)
        axis = v22._unit(base_dir + rng.normal(0.0, 0.028, 3))
        end = parent_pos + axis * float(length0)
        child = _append_node(nodes, parents, parent_idx, end)
        if depth >= 2:
            junction_count += 1
            u, v, w = v22._basis(axis)
            for sign in (-1, 1):
                if depth == 2 and not double_sides and sign < 0:
                    continue
                turn_axis = v22._unit(0.55 * u + sign * 0.35 * v + 0.18 * w)
                child_dir = v22._unit(_rot(turn_axis, sign * (0.34 + 0.05 * rng.normal())) @ axis)
                child_dir = v22._unit(child_dir + sign * 0.20 * v + np.array([0.0, 0.0, 0.05]))
                add_recursive_side(child, child_dir, length0 * float(rng.uniform(0.58, 0.72)), depth - 1, phase + sign * 0.73)
        else:
            terminal_side_count += 1

    for step_i in range(1, int(main_steps) + 1):
        twist = main_curve * math.sin(step_i * 0.74)
        direction = v22._unit(_rot(np.array([0.0, 0.0, 1.0]), twist) @ direction + rng.normal(0.0, 0.018, 3))
        end = np.asarray(nodes[parent], dtype=float) + direction * length * float(rng.uniform(0.86, 1.04))
        current = _append_node(nodes, parents, parent, end)
        main_indices.append(current)
        if step_i >= 2 and (step_i % int(side_every) == 0 or step_i in {3, main_steps - 1}):
            u, v, w = v22._basis(direction)
            signs = (-1, 1) if double_sides or step_i % 3 == 0 else ((-1,) if step_i % 2 else (1,))
            for sign in signs:
                yaw = sign * (float(side_angle) + float(rng.normal(0.0, 0.06)))
                pitch = float(rng.uniform(0.16, 0.34))
                side_dir = v22._unit(_rot(w, yaw) @ (_rot(v, pitch) @ direction))
                side_dir = v22._unit(0.70 * side_dir + sign * 0.45 * u + np.array([0.0, 0.0, 0.05]))
                add_recursive_side(
                    current,
                    side_dir,
                    length * float(side_length) * float(rng.uniform(0.86, 1.10)),
                    int(side_depth),
                    step_i * 0.31,
                )
                junction_count += 1
        parent = current
        length *= float(rng.uniform(0.87, 0.94))

    nodes = v22._normalize_nodes(nodes, 2.72)
    return nodes, parents, {
        "source": "custom_finite_lsystem_branch_with_side_branches",
        "grammar_rule": "F -> F[+F][-F]F with explicit side-branch recursion and terminal bud handles",
        "recursive_depth": int(side_depth + main_steps),
        "lsystem_branch_depth": int(side_depth),
        "main_branch_steps": int(main_steps),
        "side_branch_every": int(side_every),
        "double_sided_side_branches": bool(double_sides),
        "pre_subdivision_junction_count": int(junction_count),
        "pre_subdivision_terminal_side_count": int(terminal_side_count),
        "target_silhouette": "single main branch with recursive side branches",
    }


def _branch_radii(
    parents: List[int],
    *,
    base: float,
    taper: float,
    floor: float,
    terminal_shrink: float,
) -> List[float]:
    depths = _depths(parents)
    max_depth = max(depths) if depths else 1
    terminals = set(v27._terminal_nodes(parents))
    child_map = v22._children(parents)
    radii: List[float] = []
    for idx, depth in enumerate(depths):
        t = depth / max(float(max_depth), 1.0)
        radius = max(float(floor), float(base) * (float(taper) ** (depth * 0.58)))
        if len(child_map.get(idx, [])) > 1:
            radius *= 1.10
        if idx in terminals:
            radius *= float(terminal_shrink)
        if t > 0.64:
            radius *= 1.0 - 0.24 * min((t - 0.64) / 0.36, 1.0)
        radii.append(float(max(radius, floor)))
    return radii


def _junction_anchor_indices(nodes: List[np.ndarray], parents: List[int], count: int) -> List[int]:
    depths = _depths(parents)
    max_depth = max(depths) if depths else 1
    child_map = v22._children(parents)
    scored: List[Tuple[float, int]] = []
    for idx in range(1, len(parents)):
        degree = len(child_map.get(idx, []))
        if degree < 2:
            continue
        t = depths[idx] / max(float(max_depth), 1.0)
        radial = float(np.linalg.norm(np.asarray(nodes[idx], dtype=float)[:2]))
        score = 2.8 * degree + 1.2 * (1.0 - abs(t - 0.44)) + 0.18 * radial + 0.0009 * idx
        scored.append((score, idx))
    if not scored:
        return v28._junction_anchor_indices(nodes, parents, count)
    ordered = [idx for _score, idx in sorted(scored, reverse=True)]
    return [ordered[(i * 5) % len(ordered)] for i in range(int(count))]


def _terminal_anchor_indices(parents: List[int], count: int) -> List[int]:
    depths = _depths(parents)
    terminals = v27._terminal_nodes(parents)
    ordered = sorted(terminals, key=lambda idx: (depths[idx], idx), reverse=True) if terminals else list(range(1, len(parents)))
    if not ordered:
        ordered = [0]
    return [ordered[(i * 7) % len(ordered)] for i in range(int(count))]


def _add_junction_collars(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    count: int,
    radius_scale: float,
    lobe_scale: float,
) -> Tuple[DetailCounts, Dict]:
    centers = getattr(mesh, "center_indices")
    child_map = v22._children(parents)
    anchors = _junction_anchor_indices(nodes, parents, count)
    counts = _blank_counts()
    seam_centers: List[List[float]] = []
    for k, idx in enumerate(anchors):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx)
        children = child_map.get(idx, [])
        child_dirs = [v22._unit(np.asarray(nodes[ch], dtype=float) - anchor) for ch in children[:4]]
        if not child_dirs:
            child_dirs = [axis]
        u, v, _w = v22._basis(axis)
        for local_i, child_dir in enumerate(child_dirs[:2]):
            lateral = math.cos((k + local_i) * 2.113) * u + math.sin((k + local_i) * 2.113) * v
            direction = v22._unit(0.44 * axis + 0.48 * child_dir + 0.18 * lateral + rng.normal(0.0, 0.018, 3))
            center = v26._add_transition_lobe(
                mesh,
                centers[idx],
                anchor,
                direction,
                float(rng.uniform(0.082, 0.148)) * float(lobe_scale),
                float(rng.uniform(0.014, 0.026)) * float(radius_scale),
                rng,
                rings=5,
                sides=12,
                curl=float(rng.uniform(0.04, 0.13)),
            )
            seam_centers.append([float(x) for x in center])
            counts["collar_count"] += 1
            counts["flare_count"] += 1
            counts["tendril_count"] += 1
        if k % 2 == 0:
            side = v22._unit(math.cos(k * 1.71) * u + math.sin(k * 1.71) * v)
            center = v26._add_transition_lobe(
                mesh,
                centers[idx],
                anchor,
                v22._unit(0.30 * axis + 0.70 * side + np.array([0.0, 0.0, 0.04])),
                float(rng.uniform(0.052, 0.092)) * float(lobe_scale),
                float(rng.uniform(0.011, 0.020)) * float(radius_scale),
                rng,
                rings=4,
                sides=10,
                curl=float(rng.uniform(0.04, 0.10)),
            )
            seam_centers.append([float(x) for x in center])
            counts["cambium_lobe_count"] += 1
            counts["bud_count"] += 1
            counts["tendril_count"] += 1
    return counts, {
        "junction_anchor_count": int(len(set(anchors))),
        "junction_collar_count": int(counts["collar_count"]),
        "junction_cambium_lobe_count": int(counts["cambium_lobe_count"]),
        "seam_mask_center_count": int(len(seam_centers)),
        "seam_mask_centers": seam_centers[:96],
        "seam_mask_radius": 0.118,
    }


def _add_branch_bark_ridges(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    count: int,
    radius_scale: float,
) -> DetailCounts:
    centers = getattr(mesh, "center_indices")
    depths = _depths(parents)
    max_depth = max(depths) if depths else 1
    candidates = [
        idx
        for idx in range(1, len(parents))
        if 0.08 <= depths[idx] / max(float(max_depth), 1.0) <= 0.82
    ]
    if not candidates:
        candidates = list(range(1, len(parents))) or [0]
    candidates = sorted(candidates, key=lambda idx: (depths[idx], idx), reverse=True)
    counts = _blank_counts()
    for k in range(int(count)):
        idx = candidates[(k * 11) % len(candidates)]
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx)
        u, v, _w = v22._basis(axis)
        lateral = math.cos(k * 1.731) * u + math.sin(k * 1.731) * v
        direction = v22._unit(0.80 * axis + 0.24 * lateral + rng.normal(0.0, 0.024, 3))
        v22._add_curved_tube_detail(
            mesh,
            centers[idx],
            anchor,
            direction,
            float(rng.uniform(0.074, 0.154)),
            float(rng.uniform(0.0048, 0.0080)) * float(radius_scale),
            rng,
            segments=4,
            sides=7,
            curl=float(rng.uniform(0.04, 0.12)),
        )
        counts["ridge_count"] += 1
        counts["tendril_count"] += 1
    return counts


def _add_structural_splits(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    count: int,
    radius_scale: float,
) -> DetailCounts:
    centers = getattr(mesh, "center_indices")
    child_map = v22._children(parents)
    anchors = _junction_anchor_indices(nodes, parents, count)
    counts = _blank_counts()
    for k, idx in enumerate(anchors):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx)
        child_dirs = [v22._unit(np.asarray(nodes[ch], dtype=float) - anchor) for ch in child_map.get(idx, [])[:3]]
        child_dir = child_dirs[k % len(child_dirs)] if child_dirs else axis
        u, v, _w = v22._basis(axis)
        lateral = math.cos(k * 2.377) * u + math.sin(k * 2.377) * v
        direction = v22._unit(0.62 * child_dir + 0.20 * axis + 0.28 * lateral + np.array([0.0, 0.0, 0.05]))
        v22._add_curved_tube_detail(
            mesh,
            centers[idx],
            anchor,
            direction,
            float(rng.uniform(0.072, 0.138)),
            float(rng.uniform(0.0048, 0.0086)) * float(radius_scale),
            rng,
            segments=4,
            sides=7,
            curl=float(rng.uniform(0.10, 0.22)),
        )
        counts["split_count"] += 1
        counts["tendril_count"] += 1
    return counts


def _add_terminal_buds(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    count: int,
    bracts_per_bud: int,
    radius_scale: float,
) -> Tuple[DetailCounts, Dict]:
    centers = getattr(mesh, "center_indices")
    anchors = _terminal_anchor_indices(parents, count)
    counts = _blank_counts()
    bud_centers: List[List[float]] = []
    for k, idx in enumerate(anchors):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx)
        u, v, _w = v22._basis(axis)
        lateral = math.cos(k * 2.071) * u + math.sin(k * 2.071) * v
        direction = v22._unit(0.86 * axis + 0.16 * lateral + np.array([0.0, 0.0, 0.04]) + rng.normal(0.0, 0.018, 3))
        center = v26._add_transition_lobe(
            mesh,
            centers[idx],
            anchor,
            direction,
            float(rng.uniform(0.044, 0.078)),
            float(rng.uniform(0.0085, 0.0145)) * float(radius_scale),
            rng,
            rings=4,
            sides=9,
            curl=float(rng.uniform(0.04, 0.11)),
        )
        counts["bud_count"] += 1
        counts["tendril_count"] += 1
        bud_centers.append([float(x) for x in center])
        for b in range(int(bracts_per_bud)):
            phase = k * 1.881 + b * math.tau / max(int(bracts_per_bud), 1)
            side = math.cos(phase) * u + math.sin(phase) * v
            leaf_dir = v22._unit(0.46 * direction + 0.58 * side + np.array([0.0, 0.0, 0.08]))
            length = float(rng.uniform(0.028, 0.056))
            v22._add_lanceolate_leaf(
                mesh,
                centers[idx],
                anchor,
                leaf_dir,
                length,
                length * float(rng.uniform(0.18, 0.30)),
                rng,
                rows=4,
            )
            counts["leaf_count"] += 1
    return counts, {
        "terminal_bud_count": int(counts["bud_count"]),
        "terminal_bud_leaf_count": int(counts["leaf_count"]),
        "terminal_bud_centers": bud_centers[:96],
    }


def _scatter_attached_leaf_sheaths(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    count: int,
    scale: Tuple[float, float],
) -> DetailCounts:
    centers = getattr(mesh, "center_indices")
    anchors = _junction_anchor_indices(nodes, parents, max(count, 1))
    counts = _blank_counts()
    for k in range(int(count)):
        idx = anchors[(k * 3) % len(anchors)]
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx)
        u, v, _w = v22._basis(axis)
        side = math.cos(k * 2.077) * u + math.sin(k * 2.077) * v
        direction = v22._unit(0.44 * axis + 0.62 * side + np.array([0.0, 0.0, 0.08]) + rng.normal(0.0, 0.040, 3))
        length = float(rng.uniform(*scale))
        v22._add_lanceolate_leaf(
            mesh,
            centers[idx],
            anchor,
            direction,
            length,
            length * float(rng.uniform(0.18, 0.32)),
            rng,
            rows=5,
        )
        counts["leaf_count"] += 1
    return counts


def _build_lsystem_branch_case(
    seed: int,
    *,
    main_steps: int,
    side_depth: int,
    side_every: int,
    double_sides: bool,
    main_curve: float,
    side_angle: float,
    side_length: float,
    base_radius: float,
    radius_taper: float,
    radius_floor: float,
    terminal_shrink: float,
    max_segment: float,
    collar_count: int,
    ridge_count: int,
    split_count: int,
    bud_count: int,
    bracts_per_bud: int,
    leaf_sheath_count: int,
    detail_radius_scale: float,
    lobe_scale: float,
) -> Tuple[pb.Mesh, Dict, Dict]:
    rng = np.random.default_rng(seed + 3402)
    nodes, parents, lsys_diag = _lsystem_branch_graph(
        seed,
        main_steps=main_steps,
        side_depth=side_depth,
        side_every=side_every,
        double_sides=double_sides,
        main_curve=main_curve,
        side_angle=side_angle,
        side_length=side_length,
    )
    nodes, parents, subdiv_diag = _subdivide_long_edges(nodes, parents, max_segment=max_segment)
    radii = _branch_radii(
        parents,
        base=base_radius,
        taper=radius_taper,
        floor=radius_floor,
        terminal_shrink=terminal_shrink,
    )
    edges = v22._graph_edges(parents)
    mesh = v22._smooth_support_mesh(nodes, edges, radii, sides=15, ovality=0.38)
    collar_counts, collar_diag = _add_junction_collars(
        mesh,
        nodes,
        parents,
        rng,
        count=collar_count,
        radius_scale=detail_radius_scale,
        lobe_scale=lobe_scale,
    )
    ridge_counts = _add_branch_bark_ridges(mesh, nodes, parents, rng, count=ridge_count, radius_scale=detail_radius_scale)
    split_counts = _add_structural_splits(mesh, nodes, parents, rng, count=split_count, radius_scale=detail_radius_scale)
    bud_counts, bud_diag = _add_terminal_buds(
        mesh,
        nodes,
        parents,
        rng,
        count=bud_count,
        bracts_per_bud=bracts_per_bud,
        radius_scale=detail_radius_scale,
    )
    sheath_counts = _scatter_attached_leaf_sheaths(
        mesh,
        nodes,
        parents,
        rng,
        count=leaf_sheath_count,
        scale=(0.030, 0.062),
    )
    counts = _merge_counts(collar_counts, ridge_counts, split_counts, bud_counts, sheath_counts)
    seam_centers = list(collar_diag.get("seam_mask_centers", [])) + list(bud_diag.get("terminal_bud_centers", []))[:24]
    semantic_detail_count = int(
        counts["leaf_count"]
        + counts["bud_count"]
        + counts["flare_count"]
        + counts["ridge_count"]
        + counts["split_count"]
        + counts["collar_count"]
        + counts["cambium_lobe_count"]
    )
    controls = v22._finalize_controls(
        {
            **lsys_diag,
            **subdiv_diag,
            "semantic_mode": "single_tree_branch",
            "target_silhouette": "naturalized L-system branch with recursive side branches",
            "support_base_radius": float(base_radius),
            "support_radius_taper": float(radius_taper),
            "support_radius_floor": float(radius_floor),
            "terminal_radius_shrink": float(terminal_shrink),
            "support_cross_section": "oval_nonround_bark_read",
            "support_visibility_policy": "all support remains visible but side-branch junctions receive object-space collars",
            "main_curve": float(main_curve),
            "side_angle": float(side_angle),
            "side_length": float(side_length),
        },
        nodes,
        edges,
        {
            "needle_count": 0,
            "leaf_count": int(counts["leaf_count"]),
            "rootlet_count": 0,
            "tendril_count": int(counts["tendril_count"]),
        },
    )
    child_map = v22._children(parents)
    terminal_count = len(v27._terminal_nodes(parents))
    branch_junction_count = sum(1 for children in child_map.values() if len(children) >= 2)
    controls.update(
        {
            "surface_strategy": SURFACE_STRATEGY,
            "semantic_detail_count": semantic_detail_count,
            "v34_lsystem_branch_naturalization": True,
            "v24_failure_addressed": "side-branch insertion seams, smooth tube read, exposed terminal caps, low naturalness, and post-GLB material islands",
            "masked_local_naturalization_target": "L-system side-branch junction bands and terminal caps",
            "mask_scope": "object_space_side_branch_junction_bands_and_terminal_caps_only",
            "seam_mask_space": "object_xyz",
            "seam_mask_selection_rule": "L-system nodes with degree >= 2 plus terminal bud anchors; no global resampling",
            "seam_mask_center_count": int(len(seam_centers)),
            "seam_mask_centers": seam_centers[:96],
            "seam_mask_radius": float(collar_diag.get("seam_mask_radius", 0.118)),
            "branch_junction_count": int(branch_junction_count),
            "terminal_count": int(terminal_count),
            "junction_anchor_count": int(collar_diag.get("junction_anchor_count", 0)),
            "junction_collar_count": int(collar_diag.get("junction_collar_count", 0)),
            "junction_cambium_lobe_count": int(collar_diag.get("junction_cambium_lobe_count", 0)),
            "terminal_bud_count": int(bud_diag.get("terminal_bud_count", 0)),
            "terminal_bud_leaf_count": int(bud_diag.get("terminal_bud_leaf_count", 0)),
            "leaf_sheath_count": int(sheath_counts.get("leaf_count", 0)),
            "ridge_count": int(counts["ridge_count"]),
            "structural_split_count": int(counts["split_count"]),
            "junction_flare_count": int(counts["flare_count"]),
            "external_support_max_segment_gate": float(EXTERNAL_SUPPORT_MAX_SEGMENT_GATE),
            "short_segment_gate_pass": bool(
                float(subdiv_diag.get("external_support_max_segment_after_subdivision", 999.0))
                <= EXTERNAL_SUPPORT_MAX_SEGMENT_GATE + 1e-6
            ),
            "naturalization_not_global_resampling": True,
            "image_generation_considered": True,
            "optional_seam_guide_source": "whole_object_lowcontrast_bark_olive_image_guide_or_reference_for_trellis2_texturing",
            "sdedit_seam_backprojection_available": False,
            "low_contrast_guide_required": True,
            "material_transition_policy": "continuous bark/cambium/olive guide; no hard green-brown junction stripe",
            "claim_boundary": "grammar-owned local geometry/material candidate; no 2D seam inpaint backprojection claim",
            "hard_tube_cap_mitigation": "shared-vertex junction collars, cambium lobes, bark ridges, structural splits, and compact terminal buds",
        }
    )
    grammar = {
        "grammar_family": "L-system",
        "grammar_symbols": "F,+,-,[,],side_branch,junction_mask,cambium_collar,bark_ridge,terminal_bud",
        "target_symbol": "F",
        "operator_to_traditional_mapping": {
            "F": "advance a finite turtle branch segment and create connected swept support",
            "+/-": "yaw side branches from the main branch frame",
            "[]": "push/pop recursive side-branch state",
            "side_branch": "instantiate the same branch-with-side-branches target used by the traditional L-system baseline",
            "junction_mask": "select side-branch attachment nodes after rewriting",
            "cambium_collar": "locally fuse side-branch bases without global resampling",
            "bark_ridge": "add connected non-round bark relief instead of a smooth tube",
            "terminal_bud": "turn exposed caps into compact connected buds",
        },
        "remote_comparison_unit": "one generated OBJ input to one traditional L-system branch-with-side-branches target",
    }
    return mesh, controls, grammar


def _draw_branch_guide(path: Path, *, variant: str) -> None:
    rng = np.random.default_rng(v26._stable_seed(path.stem))
    palettes = {
        "cedar": [(50, 36, 22), (78, 52, 30), (116, 78, 44), (76, 94, 46), (116, 126, 70)],
        "cambium": [(58, 44, 28), (92, 66, 38), (134, 92, 50), (86, 112, 58), (136, 144, 84)],
        "olive": [(48, 40, 28), (82, 64, 38), (106, 84, 52), (70, 102, 50), (108, 134, 78)],
        "ridge": [(44, 34, 24), (74, 54, 34), (120, 84, 48), (80, 104, 52), (132, 138, 78)],
    }
    colors = palettes[variant]
    img = Image.new("RGB", (768, 768), (48, 52, 36))
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(86):
        color = colors[int(rng.integers(0, len(colors)))]
        x = int(rng.integers(-120, 880))
        y = int(rng.integers(-120, 880))
        r = int(rng.integers(90, 240))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, int(rng.integers(42, 92))))
    img = img.filter(ImageFilter.GaussianBlur(radius=18))
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(78):
        base = np.array([rng.integers(20, 720), rng.integers(110, 700)], dtype=float)
        color = colors[int(rng.integers(0, 3))]
        branch_len = float(rng.uniform(68, 170))
        angle = float(rng.uniform(-2.78, -0.38))
        pts = []
        for t in np.linspace(0.0, 1.0, 7):
            curve = math.sin(t * math.pi) * rng.uniform(-14, 18)
            p = base + np.array([math.cos(angle) * branch_len * t + curve, math.sin(angle) * branch_len * t], dtype=float)
            pts.append((int(p[0]), int(p[1])))
        draw.line(pts, fill=(*color, int(rng.integers(86, 150))), width=int(rng.integers(2, 6)))
        for _side in range(int(rng.integers(1, 3))):
            fork = pts[int(rng.integers(1, len(pts) - 1))]
            side_angle = float(angle + rng.choice([-1.0, 1.0]) * rng.uniform(0.55, 1.05))
            end = (
                int(fork[0] + math.cos(side_angle) * branch_len * rng.uniform(0.24, 0.48)),
                int(fork[1] + math.sin(side_angle) * branch_len * rng.uniform(0.24, 0.48)),
            )
            draw.line((fork, end), fill=(*color, int(rng.integers(72, 132))), width=int(rng.integers(1, 4)))
    for _ in range(120):
        color = colors[int(rng.integers(3, len(colors)))]
        x = int(rng.integers(30, 738))
        y = int(rng.integers(30, 738))
        rx = int(rng.integers(5, 16))
        ry = int(rng.integers(3, 10))
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(*color, int(rng.integers(28, 62))))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.filter(ImageFilter.SMOOTH_MORE).save(path)


def _write_guides(out_dir: Path) -> Dict[str, str]:
    guide_dir = out_dir / "_guides"
    guides: Dict[str, str] = {}
    for key in ("cedar", "cambium", "olive", "ridge"):
        path = guide_dir / f"V34_lsystem_branch_{key}_lowcontrast_guide.png"
        _draw_branch_guide(path, variant=key)
        guides[key] = str(path)
    return guides


def _spec(
    *,
    case_id: str,
    mesh: pb.Mesh,
    controls: Dict,
    grammar: Dict,
    guide_key: str,
    gpu: int,
    seed: int,
    root_variant: str,
    parameter_variant: str,
    reason: str,
) -> Dict:
    operators = list(v23.OPERATORS_BY_FAMILY["L-system"]) + [
        "short_segment_subdivision_gate",
        "object_space_side_branch_junction_mask",
        "shared_vertex_cambium_collars",
        "attached_cambium_lobes",
        "connected_bark_ridges",
        "structural_branch_splits",
        "compact_terminal_buds",
        "low_contrast_whole_object_guide",
    ]
    controls = dict(controls)
    controls.update(
        {
            "mesh_input_format": "obj",
            "same_classical_task_mode": True,
            "connected_support": True,
            "connectivity_gate_lcr_min": CONNECTIVITY_LCR_MIN,
            "low_poly_block_stamping": False,
            "mesh_token_stamping": False,
            "v34_lsystem_branch_naturalization": True,
        }
    )
    return {
        "case_id": case_id,
        "family": "L-system",
        "match_target": "lsys_branch_side_d5",
        "traditional_target": "lsys_branch_side_d5",
        "recursive_mode": "finite L-system branch with recursive side branches and terminal buds",
        "mesh": mesh,
        "controls": controls,
        "guide_key": guide_key,
        "root_variant": root_variant,
        "grammar_guide": "v34_lsystem_branch_lowcontrast_bark_cambium_guide",
        "parameter_variant": parameter_variant,
        "gpu": int(gpu),
        "seed": int(seed),
        "operators": operators,
        "operator_composition": " -> ".join(operators),
        "grammar_mapping": v23._grammar_mapping("L-system", "lsys_branch_side_d5", controls, grammar),
        "family_diagnostics": v23._family_diagnostics("L-system", "lsys_branch_side_d5", controls),
        "why_matches_traditional": reason,
        "strict_match_notes": reason,
        "case_role": "v34_lsystem_branch_naturalization",
        "qa_priority": "side_branch_junction_naturalness_and_non_seam_read",
        "rerun_reason": reason,
        "boundary_tag": "",
    }


def _case_specs(seed: int) -> List[Dict]:
    settings = [
        ("V34_lsys_branch_cambium_collar_A", 4, 34001, 9, 3, 2, True, 0.16, 0.72, 0.70, 0.066, 0.856, 0.0068, 0.86, 0.118, 22, 34, 14, 26, 1, 28, 1.08, 0.92, "cambium", "cambium collar A: dense shared-vertex collars at all major side-branch bases with low-contrast bark/olive guide"),
        ("V34_lsys_branch_ridge_bud_B", 5, 34002, 10, 2, 2, False, 0.13, 0.66, 0.64, 0.070, 0.862, 0.0072, 0.88, 0.116, 20, 42, 16, 30, 1, 18, 1.04, 0.86, "ridge", "ridge-bud B: fewer leaves, stronger bark ridges and compact terminal buds for low-fragment GLB export"),
        ("V34_lsys_branch_fused_side_C", 4, 34003, 8, 3, 2, True, 0.19, 0.78, 0.74, 0.064, 0.850, 0.0070, 0.84, 0.120, 20, 28, 16, 22, 1, 20, 1.14, 0.94, "olive", "fused side C: broader cambium lobes around paired side branches to hide insertion seams while preserving L-system hierarchy, with reduced free leaf detail for post-GLB stability"),
        ("V34_lsys_branch_lowfrag_D", 5, 34004, 9, 2, 3, False, 0.11, 0.62, 0.60, 0.072, 0.868, 0.0076, 0.90, 0.112, 18, 28, 12, 22, 0, 10, 0.98, 0.82, "cedar", "lowfrag D: conservative two-GPU candidate with thick support floor, short segments, minimal free leaves, and strong terminal cap closure"),
    ]
    rows: List[Dict] = []
    for (
        case_id,
        gpu,
        offset,
        main_steps,
        side_depth,
        side_every,
        double_sides,
        main_curve,
        side_angle,
        side_length,
        base_radius,
        radius_taper,
        radius_floor,
        terminal_shrink,
        max_segment,
        collar_count,
        ridge_count,
        split_count,
        bud_count,
        bracts_per_bud,
        leaf_sheath_count,
        detail_radius_scale,
        lobe_scale,
        guide_key,
        reason,
    ) in settings:
        mesh, controls, grammar = _build_lsystem_branch_case(
            seed + offset,
            main_steps=main_steps,
            side_depth=side_depth,
            side_every=side_every,
            double_sides=double_sides,
            main_curve=main_curve,
            side_angle=side_angle,
            side_length=side_length,
            base_radius=base_radius,
            radius_taper=radius_taper,
            radius_floor=radius_floor,
            terminal_shrink=terminal_shrink,
            max_segment=max_segment,
            collar_count=collar_count,
            ridge_count=ridge_count,
            split_count=split_count,
            bud_count=bud_count,
            bracts_per_bud=bracts_per_bud,
            leaf_sheath_count=leaf_sheath_count,
            detail_radius_scale=detail_radius_scale,
            lobe_scale=lobe_scale,
        )
        rows.append(
            _spec(
                case_id=case_id,
                mesh=mesh,
                controls=controls,
                grammar=grammar,
                guide_key=guide_key,
                gpu=gpu,
                seed=seed + offset,
                root_variant=case_id.replace("V34_", ""),
                parameter_variant=(
                    f"main{main_steps}_sideD{side_depth}_every{side_every}_double{int(double_sides)}"
                    f"_maxseg{max_segment:.3f}_base{base_radius:.3f}_collar{collar_count}"
                    f"_ridge{ridge_count}_bud{bud_count}_leaf{leaf_sheath_count}"
                ),
                reason=reason,
            )
        )
    return rows


def _metadata_for(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    metadata = v23._metadata_for(spec, mesh_path, guide_path, metrics)
    controls = spec["controls"]
    metadata["strict_generation_policy"] = GENERATION_POLICY
    metadata["selection_budget"] = SELECTION_BUDGET
    metadata["case_role"] = spec["case_role"]
    metadata["rerun_reason"] = spec["rerun_reason"]
    metadata["qa_priority"] = spec["qa_priority"]
    metadata["root_selection_log"]["root_source_type"] = "V34_lsystem_branch_naturalization_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V34_lsystem_branch_naturalization_20260511.py"
    metadata["v34_lsystem_branch_naturalization_contract"] = {
        "target_failure": "V24/V23 L-system branch-with-side-branches remains tube-like, visibly inserted at junctions, and has exposed terminal caps",
        "geometry_operator": "short segmented swept support plus object-space junction collars, cambium lobes, bark ridges, branch splits, and compact terminal buds",
        "seam_mask": {
            "space": "object_xyz",
            "scope": controls.get("mask_scope"),
            "selection_rule": controls.get("seam_mask_selection_rule"),
            "radius": controls.get("seam_mask_radius"),
            "center_count": controls.get("seam_mask_center_count"),
            "centers": controls.get("seam_mask_centers", [])[:96],
        },
        "naturalization_regions": ["side_branch_junction_band", "terminal_caps", "bark_ridge_relief"],
        "optional_seam_guide_source": controls.get("optional_seam_guide_source"),
        "sdedit_seam_backprojection_available": False,
        "texture_operator": "low-contrast whole-object guide for Trellis2 texturing; no 2D seam inpaint backprojection claim",
        "material_transition_policy": controls.get("material_transition_policy"),
        "claim_boundary": controls.get("claim_boundary"),
        "post_glb_acceptance": "paper candidate only if side-branch junction zoom no longer reads as a hard inserted tube and r1 LCR remains 1.0; preferred r0 LCR >=0.999",
    }
    metadata["v34_remote_cache_policy"] = {
        "cache_root": REMOTE_STORAGE_ROOT + "/cache",
        "no_system_tmp": True,
        "max_simultaneous_gpus": 2,
        "allowed_gpu_pool": ALLOWED_GPUS,
    }
    return metadata


def materialize(root: Path, out_dir: Path, seed: int = 20260511, case_limit: Optional[int] = None) -> Dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    guides = _write_guides(out_dir)
    specs = _case_specs(seed)
    if case_limit is not None:
        specs = specs[: int(case_limit)]

    rows: List[Dict] = []
    metrics_rows: List[Dict] = []
    for spec in specs:
        case_dir = out_dir / spec["case_id"]
        mesh_path = case_dir / f"{spec['case_id']}.obj"
        v23._export_mesh(mesh_path, spec["mesh"])
        guide_path = guides[spec["guide_key"]]
        metrics = v23._mesh_stats(mesh_path, spec["controls"])
        if metrics["largest_mesh_component_vertex_ratio"] < CONNECTIVITY_LCR_MIN:
            raise RuntimeError(f"{spec['case_id']} failed V34 connectivity gate: {metrics}")
        if float(spec["controls"].get("external_support_max_segment_after_subdivision", 999.0)) > EXTERNAL_SUPPORT_MAX_SEGMENT_GATE + 1e-6:
            raise RuntimeError(f"{spec['case_id']} failed V34 short-segment gate: {spec['controls']}")
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
            "gpu_group": int(spec["gpu"]),
            "seed": int(spec["seed"]),
            "operators": json.dumps(spec["operators"], ensure_ascii=False),
            "operator_composition": spec["operator_composition"],
            "controls": json.dumps(spec["controls"], ensure_ascii=False, sort_keys=True),
            "why_matches_traditional": spec["why_matches_traditional"],
            "strict_match_notes": spec["strict_match_notes"],
            "case_role": spec["case_role"],
            "qa_priority": spec["qa_priority"],
            "rerun_reason": spec["rerun_reason"],
            "boundary_tag": "",
            "strict_one_to_one": "true",
            "generation_policy": GENERATION_POLICY,
            "mesh_input_policy": "obj_mesh_inputs_only",
            "mesh_pbr_policy": MESH_PBR_POLICY,
            "surface_strategy": SURFACE_STRATEGY,
            "block_or_token_stamping": "false",
            "root_variant": spec["root_variant"],
            "grammar_guide": spec["grammar_guide"],
            "parameter_variant": spec["parameter_variant"],
            "selection_budget": SELECTION_BUDGET,
            "storage_root": REMOTE_STORAGE_ROOT,
            "storage_limit_gb": STORAGE_LIMIT_GB,
            "pre_export_lcr_gate": CONNECTIVITY_LCR_MIN,
            "pre_export_gate_or_boundary": "lcr>=0.999",
            "branch_junction_count": int(spec["controls"].get("branch_junction_count", 0)),
            "terminal_count": int(spec["controls"].get("terminal_count", 0)),
            "seam_mask_center_count": int(spec["controls"].get("seam_mask_center_count", 0)),
            "junction_collar_count": int(spec["controls"].get("junction_collar_count", 0)),
            "junction_cambium_lobe_count": int(spec["controls"].get("junction_cambium_lobe_count", 0)),
            "terminal_bud_count": int(spec["controls"].get("terminal_bud_count", 0)),
            "leaf_sheath_count": int(spec["controls"].get("leaf_sheath_count", 0)),
            "junction_flare_count": int(spec["controls"].get("junction_flare_count", 0)),
            "ridge_count": int(spec["controls"].get("ridge_count", 0)),
            "structural_split_count": int(spec["controls"].get("structural_split_count", 0)),
            "external_support_max_segment_after_subdivision": float(
                spec["controls"].get("external_support_max_segment_after_subdivision", 0.0)
            ),
            "sdedit_seam_backprojection_available": str(bool(spec["controls"].get("sdedit_seam_backprojection_available", False))).lower(),
        }
        rows.append(row)
        metrics_rows.append(
            {
                "case_id": spec["case_id"],
                "family": spec["family"],
                "match_target": spec["match_target"],
                "traditional_target": spec["traditional_target"],
                **metrics,
                "qa_priority": spec["qa_priority"],
                "boundary_tag": "",
                "branch_junction_count": int(spec["controls"].get("branch_junction_count", 0)),
                "terminal_count": int(spec["controls"].get("terminal_count", 0)),
                "seam_mask_center_count": int(spec["controls"].get("seam_mask_center_count", 0)),
                "junction_collar_count": int(spec["controls"].get("junction_collar_count", 0)),
                "junction_cambium_lobe_count": int(spec["controls"].get("junction_cambium_lobe_count", 0)),
                "terminal_bud_count": int(spec["controls"].get("terminal_bud_count", 0)),
                "leaf_sheath_count": int(spec["controls"].get("leaf_sheath_count", 0)),
                "junction_flare_count": int(spec["controls"].get("junction_flare_count", 0)),
                "ridge_count": int(spec["controls"].get("ridge_count", 0)),
                "structural_split_count": int(spec["controls"].get("structural_split_count", 0)),
                "external_support_max_segment_after_subdivision": float(
                    spec["controls"].get("external_support_max_segment_after_subdivision", 0.0)
                ),
            }
        )

    manifest_fields = list(rows[0].keys()) if rows else []
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    obj_zoom_cases = []
    for row in rows:
        controls = json.loads(row["controls"])
        targets = controls.get("seam_mask_centers", [])[:36]
        obj_zoom_cases.append(
            {
                "label": row["case_id"] + "_obj_junctiontarget",
                "mesh": str(Path(row["mesh_path"]).resolve()),
                "plan_mesh": str(Path(row["mesh_path"]).resolve()),
                "material_mode": "cedar",
                "zoom_levels": 2,
                "detail_targets": targets,
                "detail_target_source": "v34_lsystem_object_space_junction_mask",
            }
        )
    (out_dir / "V34_obj_zoom_manifest_junctiontarget_20260511.json").write_text(
        json.dumps({"cases": obj_zoom_cases}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    metric_fields = list(metrics_rows[0].keys()) if metrics_rows else []
    with (out_dir / "initial_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        writer.writerows(metrics_rows)
    (out_dir / "initial_metrics.json").write_text(json.dumps(metrics_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    case_lines = [f"{row['case_id']}|{row['mesh_path']}|{row['guide_image']}|{row['seed']}|{row['gpu_group']}" for row in rows]
    (out_dir / "a100-2_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    (out_dir / "gpu45_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    gpu_case_counts: Dict[str, int] = {}
    for gpu in ALLOWED_GPUS:
        selected = [line for line, row in zip(case_lines, rows) if int(row["gpu_group"]) == gpu]
        gpu_case_counts[str(gpu)] = len(selected)
        (out_dir / f"gpu{gpu}_cases.txt").write_text("\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")

    summary = {
        "out_dir": str(out_dir),
        "num_cases": len(rows),
        "remote_target": REMOTE_TARGET,
        "allowed_gpus": ALLOWED_GPUS,
        "default_active_gpus": DEFAULT_ACTIVE_GPUS,
        "max_simultaneous_remote_gpus": 2,
        "storage_root": REMOTE_STORAGE_ROOT,
        "storage_limit_gb": STORAGE_LIMIT_GB,
        "surface_generator": "strict_visual_matched_cases_V34_lsystem_branch_naturalization",
        "mesh_input_policy": "obj_mesh_inputs_only",
        "mesh_pbr_policy": MESH_PBR_POLICY,
        "surface_strategy": SURFACE_STRATEGY,
        "connectivity_gate": {
            "largest_component_vertex_ratio_min": CONNECTIVITY_LCR_MIN,
            "pre_trellis_required": True,
            "boundary_tag_allowed": False,
        },
        "lsystem_branch_gate": {
            "match_target": "lsys_branch_side_d5",
            "mask_scope": "object_space_side_branch_junction_bands_and_terminal_caps_only",
            "min_branch_junctions": min(int(row["branch_junction_count"]) for row in rows) if rows else 0,
            "min_seam_mask_centers": min(int(row["seam_mask_center_count"]) for row in rows) if rows else 0,
            "min_junction_collars": min(int(row["junction_collar_count"]) for row in rows) if rows else 0,
            "min_terminal_buds": min(int(row["terminal_bud_count"]) for row in rows) if rows else 0,
            "min_ridges": min(int(row["ridge_count"]) for row in rows) if rows else 0,
            "max_external_support_segment_after_subdivision": max(
                float(row["external_support_max_segment_after_subdivision"]) for row in rows
            ) if rows else 0.0,
            "external_support_max_segment_gate": EXTERNAL_SUPPORT_MAX_SEGMENT_GATE,
            "sdedit_seam_backprojection_available": False,
            "image_generation_considered": True,
        },
        "post_glb_target_floor": {
            "preferred_r0_lcr_min": 0.999,
            "fallback_r1_lcr_min": 1.0,
            "visual_gate": "side-branch junction zoom must not read as hard inserted tubes; terminal caps must be closed by buds/cambium",
        },
        "storage_risk": {
            "expected_upper_bound_gb": 24,
            "risk_level": "low",
            "notes": "4 OBJ candidates; remote launch defaults to two GPUs only.",
        },
        "gpu_case_counts": gpu_case_counts,
        "priority_cases": [row["case_id"] for row in rows],
        "manifest": str(out_dir / "manifest.csv"),
        "initial_metrics": str(out_dir / "initial_metrics.csv"),
        "obj_zoom_manifest": str(out_dir / "V34_obj_zoom_manifest_junctiontarget_20260511.json"),
        "do_not_launch_remote_before_local_visual_qa": True,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V34 L-system Branch Naturalization Dry Run\n\n"
        "Predeclared branch-with-side-branches candidates. V34 uses short segmented support, "
        "object-space side-branch junction masks, shared-vertex cambium collars, bark ridges, "
        "structural splits, compact terminal buds, and whole-object low-contrast guides. It explicitly "
        "does not claim a 2D seam-inpaint backprojection pipeline.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("RGG_ROOT", ROOT_DIR)))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260511)
    parser.add_argument("--case-limit", type=int, default=None)
    args = parser.parse_args()
    materialize(args.root, args.out, seed=args.seed, case_limit=args.case_limit)


if __name__ == "__main__":
    main()
