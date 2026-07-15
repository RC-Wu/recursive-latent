#!/usr/bin/env python3
"""V38 L-system branch tipless-saddle naturalization inputs.

V35/V36 improved connectivity, but pure-white zoom QA still read as a large
cut branch tube with small side geometry attached near it. V38 keeps the same
strict branch-with-side-branches target and changes the local realization
toward a tipless saddle fork:

* shorter, thinner main-axis terminals so the branch end is not the visual
  protagonist in overview/zoom,
* side branches leave through a short saddle-neck segment instead of an abrupt
  tube insertion,
* broad cambium collars and elongated bark ridges at actual side-branch
  junctions,
* very few free leaves/bracts so the geometry reads as fused wood rather than
  foliage pasted on a tube,
* mid-depth junction-only zoom targets for local QA.

This remains claim-bounded: the guide is whole-object low-contrast guidance;
there is no 2D seam-inpaint backprojection pipeline.
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
import strict_visual_matched_cases_V34_lsystem_branch_naturalization_20260511 as v34


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
DEFAULT_ACTIVE_GPUS = [4, 5]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 200
CONNECTIVITY_LCR_MIN = 0.999
EXTERNAL_SUPPORT_MAX_SEGMENT_GATE = 0.100
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V38_lsystem_branch_tipless_saddle_naturalization_20260511_dryrun"

SURFACE_STRATEGY = "v38_lsystem_branch_tipless_sidebranch_saddle_naturalization"
GENERATION_POLICY = "generate_new_on_a100_2_no_local_selection_or_postprocessing"
SELECTION_BUDGET = "four_v38_lsystem_branch_candidates_local_qa_then_two_gpu_remote"
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
        "terminal_sleeve_count": 0,
    }


def _merge_counts(*parts: DetailCounts) -> DetailCounts:
    out = _blank_counts()
    for part in parts:
        for key, value in part.items():
            out[key] = int(out.get(key, 0)) + int(value)
    return out


def _terminal_lineage(parents: List[int], hops: int = 2) -> Dict[int, int]:
    terminals = v27._terminal_nodes(parents)
    lineage: Dict[int, int] = {}
    for terminal in terminals:
        current = terminal
        for distance in range(hops + 1):
            if current < 0:
                break
            lineage[current] = min(distance, lineage.get(current, distance))
            current = int(parents[current]) if current < len(parents) else -1
    return lineage


def _branch_radii_v38(
    parents: List[int],
    *,
    base: float,
    taper: float,
    floor: float,
    terminal_shrink: float,
    tip_parent_shrink: float,
    high_depth_shrink: float,
) -> List[float]:
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    child_map = v22._children(parents)
    terminals = set(v27._terminal_nodes(parents))
    terminal_lineage = _terminal_lineage(parents, hops=6)
    radii: List[float] = []
    for idx, depth in enumerate(depths):
        t = depth / max(float(max_depth), 1.0)
        radius = float(base) * (float(taper) ** (depth * 0.86))
        if len(child_map.get(idx, [])) >= 2:
            radius *= 1.02
        if len(child_map.get(idx, [])) <= 1 and t > 0.28:
            # Shrink single-child upper branch runs so the side view stops
            # reading as a rectangular pipe.
            radius *= 1.0 - (1.0 - float(high_depth_shrink)) * min((t - 0.28) / 0.72, 1.0)
        if idx in terminal_lineage and idx not in terminals:
            distance = terminal_lineage[idx]
            radius *= min(1.0, float(tip_parent_shrink) + 0.055 * distance)
        if idx in terminals:
            radius *= float(terminal_shrink)
        radius = max(float(floor) * 0.55, radius)
        radii.append(float(radius))
    return radii


def _append_node(nodes: List[np.ndarray], parents: List[int], parent: int, point: np.ndarray) -> int:
    nodes.append(np.asarray(point, dtype=float))
    parents.append(int(parent))
    return len(nodes) - 1


def _lsystem_branch_graph_v38(
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
    """Finite L-system branch with explicit saddle-neck side-branch bases.

    V36 used the same tree topology as V34/V35, so the renderer often saw a
    long main tube and then separate attached detail.  This graph keeps the
    same L-system family but inserts one short, forward-leaning neck before
    each side recursion.  The side branch therefore shares the local main-axis
    direction before it turns away, which makes the swept mesh read more like a
    natural fork.
    """

    rng = np.random.default_rng(seed + 3801)
    nodes: List[np.ndarray] = [np.zeros(3, dtype=float)]
    parents: List[int] = [-1]
    direction = v22._unit(np.array([0.42, -0.04, 0.90], dtype=float))
    length = 0.92
    parent = 0
    junction_count = 0
    terminal_side_count = 0
    saddle_neck_count = 0
    terminal_fork_count = 0

    def add_recursive_side(parent_idx: int, parent_axis: np.ndarray, target_dir: np.ndarray, length0: float, depth: int) -> None:
        nonlocal junction_count, terminal_side_count, saddle_neck_count
        if depth <= 0:
            terminal_side_count += 1
            return
        parent_pos = np.asarray(nodes[parent_idx], dtype=float)
        parent_axis = v22._unit(parent_axis)
        target_dir = v22._unit(target_dir + rng.normal(0.0, 0.020, 3))
        neck_dir = v22._unit(0.54 * parent_axis + 0.46 * target_dir)
        neck_len = float(length0) * float(rng.uniform(0.22, 0.31))
        neck = _append_node(nodes, parents, parent_idx, parent_pos + neck_dir * neck_len)
        saddle_neck_count += 1
        branch_len = float(length0) * float(rng.uniform(0.66, 0.78))
        end = np.asarray(nodes[neck], dtype=float) + target_dir * branch_len
        child = _append_node(nodes, parents, neck, end)
        if depth >= 2:
            junction_count += 1
            u, v, w = v22._basis(target_dir)
            signs = (-1, 1) if depth > 2 else ((1,) if rng.random() > 0.45 else (-1,))
            for local_i, sign in enumerate(signs):
                turn_axis = v22._unit(0.34 * u + sign * 0.54 * v + 0.16 * w)
                child_dir = v22._unit(v34._rot(turn_axis, sign * (0.38 + 0.04 * rng.normal())) @ target_dir)
                child_dir = v22._unit(0.76 * child_dir + sign * 0.26 * v + np.array([0.0, 0.0, 0.035]))
                add_recursive_side(child, target_dir, child_dir, branch_len * float(rng.uniform(0.54, 0.66)), depth - 1)
        else:
            # Depth-1 side branches get a tiny fork so visible endings read as
            # fine twigs instead of capped tubes.
            if length0 > 0.055:
                u, v, w = v22._basis(target_dir)
                for sign in (-1, 1):
                    twig_dir = v22._unit(0.72 * target_dir + sign * 0.24 * u + 0.10 * v)
                    _append_node(nodes, parents, child, np.asarray(nodes[child], dtype=float) + twig_dir * length0 * float(rng.uniform(0.18, 0.26)))
                    terminal_side_count += 1
            else:
                terminal_side_count += 1

    for step_i in range(1, int(main_steps) + 1):
        t = step_i / max(float(main_steps), 1.0)
        twist = float(main_curve) * math.sin(step_i * 0.83)
        direction = v22._unit(v34._rot(np.array([0.0, 0.0, 1.0]), twist) @ direction + rng.normal(0.0, 0.016, 3))
        step_len = length * float(rng.uniform(0.84, 0.98))
        if t > 0.60:
            step_len *= 0.46
            direction = v22._unit(0.88 * direction + 0.14 * np.array([-0.22, 0.10, 0.10]) + rng.normal(0.0, 0.012, 3))
        end = np.asarray(nodes[parent], dtype=float) + direction * step_len
        current = _append_node(nodes, parents, parent, end)
        should_branch = step_i >= 2 and (step_i % int(side_every) == 0 or step_i in {3, max(3, main_steps - 2)})
        if should_branch:
            u, v, w = v22._basis(direction)
            if double_sides:
                signs = (-1, 1)
            else:
                signs = ((-1,) if step_i % 2 else (1,))
            for sign in signs:
                yaw = sign * (float(side_angle) + float(rng.normal(0.0, 0.045)))
                pitch = float(rng.uniform(0.12, 0.26))
                side_dir = v22._unit(v34._rot(w, yaw) @ (v34._rot(v, pitch) @ direction))
                side_dir = v22._unit(0.58 * side_dir + sign * 0.50 * u + 0.16 * direction + np.array([0.0, 0.0, 0.035]))
                add_recursive_side(
                    current,
                    direction,
                    side_dir,
                    length * float(side_length) * float(rng.uniform(0.82, 1.02)) * (1.0 - 0.14 * t),
                    int(side_depth),
                )
                junction_count += 1
        parent = current
        length *= float(rng.uniform(0.74, 0.84))

    # Convert the main-axis endpoint into a fine terminal fork.  This is the
    # main V38 change: the visible main branch no longer ends in a thick capped
    # tube, but continues into two small off-axis twigs.
    if parent > 0:
        tip_pos = np.asarray(nodes[parent], dtype=float)
        parent_axis = v22._node_axis(nodes, parents, parent)
        u, v, _w = v22._basis(parent_axis)
        for sign in (-1, 1):
            fork_dir = v22._unit(0.70 * parent_axis + sign * 0.30 * u + 0.12 * v + rng.normal(0.0, 0.018, 3))
            child = _append_node(nodes, parents, parent, tip_pos + fork_dir * max(length * 0.48, 0.045))
            terminal_fork_count += 1
            # Add a second tiny segment to turn the silhouette into a tapering
            # twig rather than a short V-shaped cap.
            child_pos = np.asarray(nodes[child], dtype=float)
            _append_node(nodes, parents, child, child_pos + v22._unit(0.82 * fork_dir + sign * 0.12 * v) * max(length * 0.22, 0.025))
            terminal_fork_count += 1

    nodes = v22._normalize_nodes(nodes, 2.52)
    return nodes, parents, {
        "source": "custom_finite_lsystem_branch_with_saddle_neck_side_branches",
        "grammar_rule": "F -> F[+sF][-sF]F with saddle-neck side-branch bases and tapered terminal continuation",
        "recursive_depth": int(side_depth + main_steps),
        "lsystem_branch_depth": int(side_depth),
        "main_branch_steps": int(main_steps),
        "side_branch_every": int(side_every),
        "double_sided_side_branches": bool(double_sides),
        "pre_subdivision_junction_count": int(junction_count),
        "pre_subdivision_terminal_side_count": int(terminal_side_count),
        "saddle_neck_count": int(saddle_neck_count),
        "terminal_fork_count": int(terminal_fork_count),
        "target_silhouette": "single woody branch with recursive side branches and no blunt main-axis terminal cap",
    }


def _add_terminal_sleeves(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    count: int,
    bracts_per_sleeve: int,
    radius_scale: float,
) -> Tuple[DetailCounts, Dict]:
    centers = getattr(mesh, "center_indices")
    anchors = v34._terminal_anchor_indices(parents, count)
    counts = _blank_counts()
    sleeve_centers: List[List[float]] = []
    for k, idx in enumerate(anchors):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx)
        u, v, _w = v22._basis(axis)
        lateral = math.cos(k * 2.311) * u + math.sin(k * 2.311) * v
        direction = v22._unit(0.90 * axis + 0.12 * lateral + np.array([0.0, 0.0, 0.035]))
        center = v26._add_transition_lobe(
            mesh,
            centers[idx],
            anchor,
            direction,
            float(rng.uniform(0.030, 0.060)),
            float(rng.uniform(0.006, 0.011)) * float(radius_scale),
            rng,
            rings=4,
            sides=8,
            curl=float(rng.uniform(0.03, 0.09)),
        )
        sleeve_centers.append([float(x) for x in center])
        counts["terminal_sleeve_count"] += 1
        counts["bud_count"] += 1
        counts["tendril_count"] += 1
        for bract in range(int(bracts_per_sleeve)):
            phase = k * 1.719 + bract * math.tau / max(int(bracts_per_sleeve), 1)
            side = math.cos(phase) * u + math.sin(phase) * v
            leaf_dir = v22._unit(0.36 * direction + 0.70 * side + np.array([0.0, 0.0, 0.06]))
            length = float(rng.uniform(0.026, 0.050))
            v22._add_lanceolate_leaf(
                mesh,
                centers[idx],
                anchor,
                leaf_dir,
                length,
                length * float(rng.uniform(0.16, 0.26)),
                rng,
                rows=4,
            )
            counts["leaf_count"] += 1
    return counts, {
        "terminal_sleeve_count": int(counts["terminal_sleeve_count"]),
        "terminal_sleeve_leaf_count": int(counts["leaf_count"]),
        "terminal_sleeve_centers": sleeve_centers[:96],
    }


def _mid_junction_targets(points: List[List[float]], limit: int = 48) -> List[List[float]]:
    """Keep zoom targets on readable mid-depth side-branch junctions.

    The matched zoom renderer scores high-Z points strongly; feeding it all
    collar centers makes it choose terminal-near collars.  For this figure we
    want the first zoom to land on the side-branch insertion region, so the
    manifest stores the mid-band collar centers only.
    """
    if not points:
        return []
    arr = np.asarray(points, dtype=float)
    z = arr[:, 2]
    lo = float(np.quantile(z, 0.12))
    hi = float(np.quantile(z, 0.54))
    center = arr.mean(axis=0)
    candidates: List[Tuple[float, List[float]]] = []
    for point in arr:
        if not (lo <= float(point[2]) <= hi):
            continue
        radial = float(np.linalg.norm(point[:2] - center[:2]))
        mid_bonus = -abs(float(point[2]) - float(np.median(z)))
        score = 1.4 * radial + 0.9 * mid_bonus - 0.55 * max(float(point[2]) - float(np.median(z)), 0.0)
        candidates.append((score, [float(x) for x in point]))
    if not candidates:
        candidates = [(0.0, [float(x) for x in point]) for point in arr]
    return [point for _score, point in sorted(candidates, reverse=True)[:limit]]


def _add_tipless_saddle_collars(
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
    anchors = v34._junction_anchor_indices(nodes, parents, count)
    counts = _blank_counts()
    seam_centers: List[List[float]] = []
    for k, idx in enumerate(anchors):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx)
        parent_idx = int(parents[idx]) if int(parents[idx]) >= 0 else idx
        parent_axis = v22._unit(anchor - np.asarray(nodes[parent_idx], dtype=float)) if parent_idx != idx else axis
        children = child_map.get(idx, [])
        if not children:
            continue
        child_dirs = [v22._unit(np.asarray(nodes[ch], dtype=float) - anchor) for ch in children[:3]]
        u, v, _w = v22._basis(axis)
        for local_i, child_dir in enumerate(child_dirs[:2]):
            side = v22._unit(child_dir - 0.55 * parent_axis)
            if float(np.linalg.norm(side)) < 1e-8:
                side = math.cos(k * 1.91) * u + math.sin(k * 1.91) * v
            for sleeve_i, direction in enumerate(
                (
                    v22._unit(0.34 * parent_axis + 0.66 * child_dir),
                    v22._unit(-0.18 * parent_axis + 0.74 * child_dir + 0.18 * side),
                )
            ):
                center = v26._add_transition_lobe(
                    mesh,
                    centers[idx],
                    anchor,
                    direction,
                    float(rng.uniform(0.070, 0.122)) * float(lobe_scale),
                    float(rng.uniform(0.010, 0.018)) * float(radius_scale),
                    rng,
                    rings=5,
                    sides=10,
                    curl=float(rng.uniform(0.02, 0.075)),
                )
                seam_centers.append([float(x) for x in center])
                counts["collar_count"] += 1
                counts["flare_count"] += 1
                counts["tendril_count"] += 1
            if local_i == 0 and k % 2 == 0:
                ridge_dir = v22._unit(0.50 * axis + 0.38 * child_dir + 0.24 * side)
                v22._add_curved_tube_detail(
                    mesh,
                    centers[idx],
                    anchor,
                    ridge_dir,
                    float(rng.uniform(0.085, 0.150)),
                    float(rng.uniform(0.0038, 0.0062)) * float(radius_scale),
                    rng,
                    segments=4,
                    sides=6,
                    curl=float(rng.uniform(0.05, 0.14)),
                )
                counts["ridge_count"] += 1
                counts["tendril_count"] += 1
    return counts, {
        "junction_anchor_count": int(len(set(anchors))),
        "junction_collar_count": int(counts["collar_count"]),
        "junction_cambium_lobe_count": int(counts["cambium_lobe_count"]),
        "seam_mask_center_count": int(len(seam_centers)),
        "seam_mask_centers": seam_centers[:128],
        "seam_mask_radius": 0.106,
    }


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
    tip_parent_shrink: float,
    high_depth_shrink: float,
    max_segment: float,
    collar_count: int,
    ridge_count: int,
    split_count: int,
    bud_count: int,
    terminal_sleeve_count: int,
    bracts_per_bud: int,
    bracts_per_sleeve: int,
    leaf_sheath_count: int,
    detail_radius_scale: float,
    lobe_scale: float,
) -> Tuple[pb.Mesh, Dict, Dict]:
    rng = np.random.default_rng(seed + 3802)
    nodes, parents, lsys_diag = _lsystem_branch_graph_v38(
        seed,
        main_steps=main_steps,
        side_depth=side_depth,
        side_every=side_every,
        double_sides=double_sides,
        main_curve=main_curve,
        side_angle=side_angle,
        side_length=side_length,
    )
    nodes, parents, subdiv_diag = v34._subdivide_long_edges(nodes, parents, max_segment=max_segment)
    radii = _branch_radii_v38(
        parents,
        base=base_radius,
        taper=radius_taper,
        floor=radius_floor,
        terminal_shrink=terminal_shrink,
        tip_parent_shrink=tip_parent_shrink,
        high_depth_shrink=high_depth_shrink,
    )
    edges = v22._graph_edges(parents)
    mesh = v22._smooth_support_mesh(nodes, edges, radii, sides=14, ovality=0.30)
    collar_counts, collar_diag = _add_tipless_saddle_collars(
        mesh,
        nodes,
        parents,
        rng,
        count=collar_count,
        radius_scale=detail_radius_scale,
        lobe_scale=lobe_scale,
    )
    ridge_counts = v34._add_branch_bark_ridges(mesh, nodes, parents, rng, count=ridge_count, radius_scale=detail_radius_scale)
    split_counts = v34._add_structural_splits(mesh, nodes, parents, rng, count=split_count, radius_scale=detail_radius_scale)
    bud_counts, bud_diag = v34._add_terminal_buds(
        mesh,
        nodes,
        parents,
        rng,
        count=bud_count,
        bracts_per_bud=bracts_per_bud,
        radius_scale=detail_radius_scale,
    )
    sleeve_counts, sleeve_diag = _add_terminal_sleeves(
        mesh,
        nodes,
        parents,
        rng,
        count=terminal_sleeve_count,
        bracts_per_sleeve=bracts_per_sleeve,
        radius_scale=detail_radius_scale,
    )
    sheath_counts = v34._scatter_attached_leaf_sheaths(
        mesh,
        nodes,
        parents,
        rng,
        count=leaf_sheath_count,
        scale=(0.016, 0.034),
    )
    counts = _merge_counts(collar_counts, ridge_counts, split_counts, bud_counts, sleeve_counts, sheath_counts)
    junction_zoom_centers = _mid_junction_targets(list(collar_diag.get("seam_mask_centers", [])), limit=48)
    seam_centers = junction_zoom_centers + list(bud_diag.get("terminal_bud_centers", []))[:18] + list(
        sleeve_diag.get("terminal_sleeve_centers", [])
    )[:18]
    semantic_detail_count = int(
        counts["leaf_count"]
        + counts["bud_count"]
        + counts["flare_count"]
        + counts["ridge_count"]
        + counts["split_count"]
        + counts["collar_count"]
        + counts["cambium_lobe_count"]
        + counts["terminal_sleeve_count"]
    )
    controls = v22._finalize_controls(
        {
            **lsys_diag,
            **subdiv_diag,
            "semantic_mode": "single_tree_branch",
            "target_silhouette": "woody naturalized L-system branch with fused recursive side branches",
            "support_base_radius": float(base_radius),
            "support_radius_taper": float(radius_taper),
            "support_radius_floor": float(radius_floor),
            "terminal_radius_shrink": float(terminal_shrink),
            "tip_parent_radius_shrink": float(tip_parent_shrink),
            "high_depth_single_child_shrink": float(high_depth_shrink),
            "support_cross_section": "thin_oval_nonround_bark_read",
            "support_visibility_policy": "short tapered main support remains visible, while side-branch bases leave through saddle-neck geometry",
            "main_curve": float(main_curve),
            "side_angle": float(side_angle),
            "side_length": float(side_length),
            "saddle_neck_count": int(lsys_diag.get("saddle_neck_count", 0)),
            "terminal_fork_count": int(lsys_diag.get("terminal_fork_count", 0)),
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
            "v38_lsystem_branch_tipless_saddle_naturalization": True,
            "v35_failure_addressed": "pure-white zoom still read as a large cut branch tube with side detail attached near it",
            "v36_failure_addressed": "mid-junction zoom still exposed a blunt large main-axis terminal and branch-on-tube attachment",
            "masked_local_naturalization_target": "L-system saddle-neck side-branch junction bands plus tiny terminal sleeves",
            "mask_scope": "object_space_side_branch_saddle_junction_bands_and_tiny_terminal_caps_only",
            "seam_mask_space": "object_xyz",
            "seam_mask_selection_rule": "degree>=2 L-system saddle junction nodes plus tiny terminal sleeve anchors; no global resampling; zoom targets filtered to mid-depth side-branch necks",
            "seam_mask_center_count": int(len(seam_centers)),
            "seam_mask_centers": seam_centers[:96],
            "junction_zoom_target_count": int(len(junction_zoom_centers)),
            "junction_zoom_targets": junction_zoom_centers[:48],
            "seam_mask_radius": float(collar_diag.get("seam_mask_radius", 0.118)),
            "branch_junction_count": int(branch_junction_count),
            "terminal_count": int(terminal_count),
            "saddle_neck_count": int(lsys_diag.get("saddle_neck_count", 0)),
            "terminal_fork_count": int(lsys_diag.get("terminal_fork_count", 0)),
            "junction_anchor_count": int(collar_diag.get("junction_anchor_count", 0)),
            "junction_collar_count": int(collar_diag.get("junction_collar_count", 0)),
            "junction_cambium_lobe_count": int(collar_diag.get("junction_cambium_lobe_count", 0)),
            "terminal_bud_count": int(bud_diag.get("terminal_bud_count", 0)),
            "terminal_bud_leaf_count": int(bud_diag.get("terminal_bud_leaf_count", 0)),
            "terminal_sleeve_count": int(sleeve_diag.get("terminal_sleeve_count", 0)),
            "terminal_sleeve_leaf_count": int(sleeve_diag.get("terminal_sleeve_leaf_count", 0)),
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
            "hard_tube_cap_mitigation": "tipless main-axis fork, shorter high-depth support, explicit saddle-neck side-branch bases, stronger parent-of-terminal taper, tiny terminal sleeves, and elongated bark ridges",
        }
    )
    grammar = {
        "grammar_family": "L-system",
        "grammar_symbols": "F,+,-,[,],side_branch,saddle_neck,junction_mask,cambium_collar,bark_ridge,terminal_sleeve,terminal_cap",
        "target_symbol": "F",
        "operator_to_traditional_mapping": {
            "F": "advance a finite turtle branch segment and create connected swept support",
            "+/-": "yaw side branches from the main branch frame",
            "[]": "push/pop recursive side-branch state",
            "side_branch": "instantiate the same branch-with-side-branches target used by the traditional L-system baseline",
            "saddle_neck": "insert a short shared-direction neck before side-branch turn-out so the fork is continuous",
            "junction_mask": "select side-branch attachment nodes after rewriting",
            "cambium_collar": "locally fuse side-branch bases without global resampling",
            "bark_ridge": "add connected non-round bark relief instead of a smooth tube",
            "terminal_sleeve": "cover exposed branch cuts with connected sleeves",
            "terminal_cap": "turn terminal cuts into small connected sleeves rather than large visible caps",
        },
        "remote_comparison_unit": "one generated OBJ input to one traditional L-system branch-with-side-branches target",
    }
    return mesh, controls, grammar


def _write_guides(out_dir: Path) -> Dict[str, str]:
    guide_dir = out_dir / "_guides"
    guides: Dict[str, str] = {}
    for key in ("cedar", "cambium", "olive", "ridge"):
        path = guide_dir / f"V38_lsystem_branch_{key}_lowcontrast_guide.png"
        v34._draw_branch_guide(path, variant=key)
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
        "high_depth_tip_parent_taper",
        "saddle_neck_side_branch_base",
        "object_space_side_branch_junction_mask",
        "shared_vertex_cambium_collars",
        "terminal_sleeve_caps",
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
            "v38_lsystem_branch_tipless_saddle_naturalization": True,
        }
    )
    return {
        "case_id": case_id,
        "family": "L-system",
        "match_target": "lsys_branch_side_d5",
        "traditional_target": "lsys_branch_side_d5",
            "recursive_mode": "finite L-system branch with recursive side branches and continuous saddle-neck junctions",
        "mesh": mesh,
        "controls": controls,
        "guide_key": guide_key,
        "root_variant": root_variant,
        "grammar_guide": "v38_lsystem_branch_lowcontrast_bark_cambium_guide",
        "parameter_variant": parameter_variant,
        "gpu": int(gpu),
        "seed": int(seed),
        "operators": operators,
        "operator_composition": " -> ".join(operators),
        "grammar_mapping": v23._grammar_mapping("L-system", "lsys_branch_side_d5", controls, grammar),
        "family_diagnostics": v23._family_diagnostics("L-system", "lsys_branch_side_d5", controls),
        "why_matches_traditional": reason,
        "strict_match_notes": reason,
            "case_role": "v38_lsystem_branch_tipless_saddle_naturalization",
            "qa_priority": "continuous_side_branch_saddle_naturalness_terminal_taper_and_non_seam_read",
        "rerun_reason": reason,
        "boundary_tag": "",
    }


def _case_specs(seed: int) -> List[Dict]:
    settings = [
        ("V38_lsys_branch_tipless_saddle_A", 4, 38001, 6, 3, 2, True, 0.34, 0.70, 0.76, 0.024, 0.710, 0.0016, 0.055, 0.120, 0.225, 0.070, 24, 64, 10, 0, 4, 0, 0, 0, 0.82, 0.92, "cambium", "tipless saddle A: main axis resolves into fine twigs; saddle necks carry the side-branch comparison"),
        ("V38_lsys_branch_tipless_midfork_B", 5, 38002, 7, 2, 2, False, 0.30, 0.62, 0.70, 0.023, 0.725, 0.0016, 0.050, 0.115, 0.215, 0.070, 22, 68, 8, 0, 4, 0, 0, 0, 0.78, 0.88, "ridge", "tipless midfork B: low-fragment wood-only backup with no dominant branch cap"),
        ("V38_lsys_branch_tipless_densefork_C", 4, 38003, 6, 3, 2, True, 0.38, 0.76, 0.80, 0.024, 0.705, 0.0015, 0.055, 0.120, 0.215, 0.068, 28, 60, 12, 0, 4, 0, 0, 0, 0.84, 0.96, "olive", "tipless densefork C: strongest recursive side-branch hierarchy while suppressing blunt terminal geometry"),
        ("V38_lsys_branch_tipless_slim_D", 5, 38004, 7, 2, 2, False, 0.24, 0.58, 0.64, 0.021, 0.730, 0.0015, 0.045, 0.105, 0.205, 0.068, 18, 58, 6, 0, 4, 0, 0, 0, 0.72, 0.82, "cedar", "tipless slim D: conservative thin-branch candidate with the least terminal mass"),
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
        tip_parent_shrink,
        high_depth_shrink,
        max_segment,
        collar_count,
        ridge_count,
        split_count,
        bud_count,
        terminal_sleeve_count,
        bracts_per_bud,
        bracts_per_sleeve,
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
            tip_parent_shrink=tip_parent_shrink,
            high_depth_shrink=high_depth_shrink,
            max_segment=max_segment,
            collar_count=collar_count,
            ridge_count=ridge_count,
            split_count=split_count,
            bud_count=bud_count,
            terminal_sleeve_count=terminal_sleeve_count,
            bracts_per_bud=bracts_per_bud,
            bracts_per_sleeve=bracts_per_sleeve,
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
                root_variant=case_id.replace("V38_", ""),
                parameter_variant=(
                    f"main{main_steps}_sideD{side_depth}_every{side_every}_double{int(double_sides)}"
                    f"_maxseg{max_segment:.3f}_base{base_radius:.3f}_tip{terminal_shrink:.2f}"
                    f"_parent{tip_parent_shrink:.2f}_woodridge{ridge_count}_sleeve{terminal_sleeve_count}"
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
    metadata["root_selection_log"]["root_source_type"] = "V38_lsystem_branch_tipless_saddle_naturalization_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V38_lsystem_branch_tipless_saddle_naturalization_20260511.py"
    metadata["v38_lsystem_branch_naturalization_contract"] = {
        "target_failure": "V35 remained connected but still read as a cut branch tube with small side geometry attached in pure-white zoom QA",
        "geometry_operator": "explicit saddle-neck side-branch bases, stronger tip-parent taper, tiny terminal sleeves, short segmented swept support, broad object-space junction collars, bark ridges, and branch splits",
        "seam_mask": {
            "space": "object_xyz",
            "scope": controls.get("mask_scope"),
            "selection_rule": controls.get("seam_mask_selection_rule"),
            "radius": controls.get("seam_mask_radius"),
            "center_count": controls.get("seam_mask_center_count"),
            "centers": controls.get("seam_mask_centers", [])[:96],
        },
        "zoom_targets": {
            "source": "junction-only object-space saddle-neck collar centers, excluding terminal buds/sleeves",
            "count": controls.get("junction_zoom_target_count"),
            "centers": controls.get("junction_zoom_targets", [])[:48],
        },
        "naturalization_regions": ["side_branch_saddle_junction_band", "tiny_terminal_sleeves", "bark_ridge_relief"],
        "sdedit_seam_backprojection_available": False,
        "texture_operator": "low-contrast whole-object guide for Trellis2 texturing; no 2D seam inpaint backprojection claim",
        "material_transition_policy": controls.get("material_transition_policy"),
        "claim_boundary": controls.get("claim_boundary"),
        "post_glb_acceptance": "paper candidate only if side-branch saddle zoom no longer reads as a hard inserted tube, terminal endpoint is not a blunt pipe, and r1 LCR remains 1.0; preferred r0 LCR >=0.999",
    }
    metadata["v38_remote_cache_policy"] = {
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
            raise RuntimeError(f"{spec['case_id']} failed V38 connectivity gate: {metrics}")
        if float(spec["controls"].get("external_support_max_segment_after_subdivision", 999.0)) > EXTERNAL_SUPPORT_MAX_SEGMENT_GATE + 1e-6:
            raise RuntimeError(f"{spec['case_id']} failed V38 short-segment gate: {spec['controls']}")
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
            "saddle_neck_count": int(spec["controls"].get("saddle_neck_count", 0)),
            "terminal_fork_count": int(spec["controls"].get("terminal_fork_count", 0)),
            "seam_mask_center_count": int(spec["controls"].get("seam_mask_center_count", 0)),
            "junction_zoom_target_count": int(spec["controls"].get("junction_zoom_target_count", 0)),
            "junction_collar_count": int(spec["controls"].get("junction_collar_count", 0)),
            "junction_cambium_lobe_count": int(spec["controls"].get("junction_cambium_lobe_count", 0)),
            "terminal_bud_count": int(spec["controls"].get("terminal_bud_count", 0)),
            "terminal_sleeve_count": int(spec["controls"].get("terminal_sleeve_count", 0)),
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
                "saddle_neck_count": int(spec["controls"].get("saddle_neck_count", 0)),
                "terminal_fork_count": int(spec["controls"].get("terminal_fork_count", 0)),
                "seam_mask_center_count": int(spec["controls"].get("seam_mask_center_count", 0)),
                "junction_zoom_target_count": int(spec["controls"].get("junction_zoom_target_count", 0)),
                "junction_collar_count": int(spec["controls"].get("junction_collar_count", 0)),
                "junction_cambium_lobe_count": int(spec["controls"].get("junction_cambium_lobe_count", 0)),
                "terminal_bud_count": int(spec["controls"].get("terminal_bud_count", 0)),
                "terminal_sleeve_count": int(spec["controls"].get("terminal_sleeve_count", 0)),
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
        targets = controls.get("junction_zoom_targets", [])[:32] or controls.get("seam_mask_centers", [])[:32]
        fixed_targets = []
        if targets:
            fixed_targets = [targets[0], targets[min(1, len(targets) - 1)]]
        obj_zoom_cases.append(
            {
                "label": row["case_id"] + "_obj_junctiontarget",
                "mesh": str(Path(row["mesh_path"]).resolve()),
                "plan_mesh": str(Path(row["mesh_path"]).resolve()),
                "material_mode": "cedar",
                "zoom_levels": 2,
                "detail_targets": targets,
                "fixed_detail_targets": fixed_targets,
                "detail_target_source": "v38_lsystem_object_space_junction_mask",
            }
        )
    (out_dir / "V38_obj_zoom_manifest_junctiontarget_20260511.json").write_text(
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
        "surface_generator": "strict_visual_matched_cases_V38_lsystem_branch_tipless_saddle_naturalization",
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
                "mask_scope": "object_space_side_branch_saddle_junction_bands_and_tiny_terminal_caps_only",
            "min_branch_junctions": min(int(row["branch_junction_count"]) for row in rows) if rows else 0,
            "min_saddle_necks": min(int(row["saddle_neck_count"]) for row in rows) if rows else 0,
            "min_terminal_forks": min(int(row["terminal_fork_count"]) for row in rows) if rows else 0,
            "min_seam_mask_centers": min(int(row["seam_mask_center_count"]) for row in rows) if rows else 0,
            "min_junction_zoom_targets": min(int(row["junction_zoom_target_count"]) for row in rows) if rows else 0,
            "min_junction_collars": min(int(row["junction_collar_count"]) for row in rows) if rows else 0,
            "min_terminal_buds": min(int(row["terminal_bud_count"]) for row in rows) if rows else 0,
            "min_terminal_sleeves": min(int(row["terminal_sleeve_count"]) for row in rows) if rows else 0,
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
            "visual_gate": "side-branch saddle zoom must not read as hard inserted tubes; terminal caps must be tiny and non-dominant",
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
        "obj_zoom_manifest": str(out_dir / "V38_obj_zoom_manifest_junctiontarget_20260511.json"),
        "do_not_launch_remote_before_local_visual_qa": True,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V38 L-system Branch Tapered Naturalization Dry Run\n\n"
        "V38 repairs the V35/V36 visual failure mode: connected metrics but pure-white zoom still read as a tube with attached side detail. "
        "It uses explicit saddle-neck side-branch bases, stronger high-depth support taper, broad junction collars, tiny terminal sleeves, mid-depth junction-only zoom targets, "
        "bark ridges, structural splits, and whole-object low-contrast guides. "
        "It explicitly does not claim a 2D seam-inpaint backprojection pipeline.\n",
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
