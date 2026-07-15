#!/usr/bin/env python3
"""V47 L-system branch shared-neck-yfork naturalization inputs.

V35/V36 improved connectivity, but pure-white zoom QA still read as a large
cut branch tube with small side geometry attached near it.  V38 removed the
largest cap but still failed: the second zoom landed on lobe endpoints and the
small terminal sleeves rendered as isolated wedges.  V40 finally produced a
topology-stable thin branch, but it was too sparse for a main visual comparison.
V41 added density everywhere and produced a denser silhouette, but post-GLB
white zooms became thin fragmented leaves/needles and exact r0 connectivity
dropped.  V47 therefore keeps the same strict branch-with-side-branches target
but moves the fork naturalization into the graph itself:

* two or three low/mid shared-neck Y-fork anchors, far from the terminal, are
  inserted into the main chain and written into the zoom manifest,
* the main continuation and each side branch share a short centerline segment
  before the branch turns out, instead of side branches being attached to the
  outside of an already-complete tube,
* junction-local radius boosts are kept, but external transition lobes are only
  low-relief bark/cambium hints rather than the main fusion geometry,
* no terminal sleeves/bracts, so terminals are solved by thin twig continuation
  rather than by visible cap patches,
* mid-depth shared-neck-yfork zoom targets for local QA,
* no global dense secondary branching and very few free ridges/splits: density
  is local, thick, and wood-dominant so Trellis2 has less incentive to invent
  green needle or leaf shards.

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
import strict_visual_matched_cases_V34_lsystem_branch_naturalization_20260511 as v34


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
DEFAULT_ACTIVE_GPUS = [4, 5]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 200
CONNECTIVITY_LCR_MIN = 0.999
EXTERNAL_SUPPORT_MAX_SEGMENT_GATE = 0.100
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V47_lsystem_branch_shared_neck_yfork_naturalization_20260511_dryrun"

SURFACE_STRATEGY = "v47_lsystem_branch_shared_neck_yfork_sidebranch_naturalization"
GENERATION_POLICY = "generate_new_on_a100_2_no_local_selection_or_postprocessing"
SELECTION_BUDGET = "four_v47_lsystem_branch_candidates_local_qa_then_two_gpu_remote"
MESH_PBR_POLICY = "obj_inputs_lsystem_branch_guides_for_trellis2_glb_export_no_2d_backprojection_claim"
ZOOM_PAIR_MIN_DISTANCE = 0.020
SWEEP_SIDES = 28
JUNCTION_RADIUS_BOOST = 1.46
JUNCTION_NEIGHBOR_RADIUS_BOOST = 1.20


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


def _branch_radii_v47(
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
        if len(child_map.get(idx, [])) <= 1 and t > 0.34:
            # V42 became visually needle-like after GLB. V47 still tapers
            # single-child runs, but keeps enough wood mass for textured export
            # to read as a branch rather than a detached stroke.
            radius *= 1.0 - (1.0 - float(high_depth_shrink)) * min((t - 0.34) / 0.66, 1.0)
        if idx in terminal_lineage and idx not in terminals:
            distance = terminal_lineage[idx]
            radius *= min(1.0, float(tip_parent_shrink) + 0.040 * distance)
        if idx in terminals:
            radius *= float(terminal_shrink)
        radius = max(float(floor), radius)
        radii.append(float(radius))
    return radii


def _append_node(nodes: List[np.ndarray], parents: List[int], parent: int, point: np.ndarray) -> int:
    nodes.append(np.asarray(point, dtype=float))
    parents.append(int(parent))
    return len(nodes) - 1


def _topological_reorder_nodes(nodes: List[np.ndarray], parents: List[int]) -> Tuple[List[np.ndarray], List[int], Dict[int, int]]:
    """Return nodes ordered so every parent appears before its children."""

    child_lists: List[List[int]] = [[] for _ in nodes]
    roots: List[int] = []
    for idx, parent in enumerate(parents):
        parent = int(parent)
        if parent < 0:
            roots.append(idx)
        else:
            child_lists[parent].append(idx)
    order: List[int] = []
    seen: set[int] = set()

    def visit(idx: int) -> None:
        if idx in seen:
            return
        seen.add(idx)
        order.append(idx)
        for child in child_lists[idx]:
            visit(child)

    for root in roots:
        visit(root)
    for idx in range(len(nodes)):
        visit(idx)

    old_to_new = {old: new for new, old in enumerate(order)}
    new_nodes = [np.asarray(nodes[old], dtype=float).copy() for old in order]
    new_parents = [-1 if int(parents[old]) < 0 else int(old_to_new[int(parents[old])]) for old in order]
    return new_nodes, new_parents, old_to_new


def _lsystem_branch_graph_v47(
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
    """Finite L-system branch with a few explicit low/mid shared neck yforks.

    V41 failed by adding side branches everywhere; V42 kept connectivity but
    still rendered as thin strokes with attached blade-like pieces. Here the
    first zoom target is the object-space root of a deliberately placed
    low/mid shared neck yfork. The graph uses fewer free children and thicker
    saddle-neck turns so Trellis2 sees a continuous wooden branch instead of
    many thin tokens.
    """

    rng = np.random.default_rng(seed + 4001)
    nodes: List[np.ndarray] = [np.zeros(3, dtype=float)]
    parents: List[int] = [-1]
    main_axis = v22._unit(np.array([0.82, -0.08, 0.35], dtype=float) + rng.normal(0.0, 0.018, 3))
    u, v, _w = v22._basis(main_axis)
    parent = 0
    main_indices = [0]
    junction_count = 0
    terminal_side_count = 0
    saddle_neck_count = 0
    terminal_fork_count = 0
    raw_yfork_pairs: List[List[List[float]]] = []
    yfork_anchor_indices: List[int] = []
    yfork_branch_count = 0

    for step_i in range(1, int(main_steps) + 1):
        t = step_i / max(float(main_steps), 1.0)
        bend = 0.15 * math.sin(step_i * 0.88 + seed * 0.001)
        direction = v22._unit(main_axis + bend * v + 0.04 * math.cos(step_i * 0.7) * u + rng.normal(0.0, 0.010, 3))
        seg_len = float(rng.uniform(0.30, 0.39)) * (1.0 - 0.07 * max(t - 0.45, 0.0))
        current = _append_node(nodes, parents, parent, np.asarray(nodes[parent], dtype=float) + direction * seg_len)
        main_indices.append(current)
        parent = current

    yfork_steps = [
        max(2, min(int(main_steps) - 2, int(round(main_steps * 0.36)))),
        max(2, min(int(main_steps) - 2, int(round(main_steps * 0.55)))),
        max(2, min(int(main_steps) - 2, int(round(main_steps * 0.70)))),
    ]
    yfork_steps = sorted(set(yfork_steps))
    primary_step = yfork_steps[0]
    primary_sign = -1 if seed % 2 else 1
    shared_neck_by_step: Dict[int, int] = {}

    def shared_neck_for_step(step: int) -> int:
        if step in shared_neck_by_step:
            return shared_neck_by_step[step]
        idx = main_indices[step]
        next_idx = main_indices[min(step + 1, len(main_indices) - 1)]
        anchor = np.asarray(nodes[idx], dtype=float)
        if next_idx == idx:
            axis = v22._node_axis(nodes, parents, idx)
            neck_pos = anchor + axis * 0.080
        else:
            next_pos = np.asarray(nodes[next_idx], dtype=float)
            axis = v22._unit(next_pos - anchor)
            neck_pos = anchor + axis * min(max(float(np.linalg.norm(next_pos - anchor)) * 0.34, 0.070), 0.125)
        neck_idx = _append_node(nodes, parents, idx, neck_pos)
        if next_idx != idx and int(parents[next_idx]) == idx:
            parents[next_idx] = neck_idx
        shared_neck_by_step[step] = neck_idx
        return neck_idx

    def add_chain(parent_idx: int, start_dir: np.ndarray, length0: float, depth: int, spread: float) -> int:
        nonlocal junction_count, terminal_side_count, saddle_neck_count, terminal_fork_count
        parent_axis = v22._node_axis(nodes, parents, parent_idx)
        neck_dir = v22._unit(0.66 * parent_axis + 0.34 * start_dir)
        neck = _append_node(nodes, parents, parent_idx, np.asarray(nodes[parent_idx], dtype=float) + neck_dir * length0 * 0.28)
        saddle_neck_count += 1
        turn_dir = v22._unit(0.34 * parent_axis + 0.66 * start_dir)
        current = _append_node(nodes, parents, neck, np.asarray(nodes[neck], dtype=float) + turn_dir * length0 * 0.64)
        if depth > 0:
            junction_count += 1
            cu, cv, _cw = v22._basis(start_dir)
            child_signs = (-1, 1) if depth >= 2 else (1,)
            for s_i, sign in enumerate(child_signs):
                child_dir = v22._unit(0.76 * start_dir + sign * spread * cu + (0.09 - 0.035 * s_i) * cv + rng.normal(0.0, 0.007, 3))
                child_len = length0 * float(rng.uniform(0.50, 0.66))
                add_chain(current, child_dir, child_len, depth - 1, spread * 0.58)
        else:
            cu, cv, _cw = v22._basis(start_dir)
            twig_dir = v22._unit(0.96 * start_dir + 0.035 * cu + 0.025 * cv)
            _append_node(nodes, parents, current, np.asarray(nodes[current], dtype=float) + twig_dir * length0 * float(rng.uniform(0.26, 0.36)))
            terminal_fork_count += 1
            terminal_side_count += 1
        return current

    primary_child = -1
    for j, step in enumerate(yfork_steps):
        idx = shared_neck_for_step(step)
        axis = v22._node_axis(nodes, parents, idx)
        su, sv, _sw = v22._basis(axis)
        anchor = np.asarray(nodes[idx], dtype=float)
        branch_signs = (primary_sign,) if (not double_sides or j != 1) else (primary_sign, -primary_sign)
        for local_i, sign in enumerate(branch_signs):
            side_dir = v22._unit(
                0.48 * axis
                + sign * (0.56 - 0.04 * local_i) * su
                + (0.13 + 0.020 * j) * sv
                + np.array([0.0, 0.0, 0.055])
                + rng.normal(0.0, 0.006, 3)
            )
            depth = max(1, int(side_depth) - (1 if j > 0 else 0))
            length = float(side_length) * float(rng.uniform(0.50, 0.70)) * (1.0 - 0.04 * j)
            child = add_chain(idx, side_dir, length, depth, 0.26 if j else 0.32)
            if primary_child < 0:
                primary_child = child
            yfork_branch_count += 1
            yfork_anchor_indices.append(int(idx))
            if len(raw_yfork_pairs) < 6:
                raw_yfork_pairs.append(
                    [
                        [float(x) for x in (anchor + side_dir * 0.050)],
                        [float(x) for x in (anchor + side_dir * 0.165)],
                    ]
                )
        primary_sign *= -1

    tip_idx = main_indices[-1]
    tip_pos = np.asarray(nodes[tip_idx], dtype=float)
    tip_axis = v22._node_axis(nodes, parents, tip_idx)
    tip_child = _append_node(nodes, parents, tip_idx, tip_pos + tip_axis * 0.105)
    _append_node(nodes, parents, tip_child, np.asarray(nodes[tip_child], dtype=float) + tip_axis * 0.065)
    terminal_fork_count += 1

    primary_anchor_old = int(shared_neck_by_step.get(primary_step, main_indices[primary_step]))
    nodes, parents, old_to_new = _topological_reorder_nodes(nodes, parents)
    primary_anchor_new = int(old_to_new.get(primary_anchor_old, primary_anchor_old))
    primary_child_new = int(old_to_new.get(primary_child, primary_child)) if primary_child >= 0 else -1
    yfork_anchor_indices = [int(old_to_new.get(idx, idx)) for idx in yfork_anchor_indices]

    raw_nodes = list(nodes)
    nodes = v22._normalize_nodes(nodes, 2.52)
    raw_arr = np.asarray(raw_nodes, dtype=float)
    center = (raw_arr.min(axis=0) + raw_arr.max(axis=0)) * 0.5
    scale = 2.52 / max(float((raw_arr.max(axis=0) - raw_arr.min(axis=0)).max()), 1e-6)
    yfork_pairs = [
        [[float(x) for x in (np.asarray(point, dtype=float) - center) * scale] for point in pair]
        for pair in raw_yfork_pairs
    ]
    return nodes, parents, {
        "source": "custom_finite_lsystem_branch_with_three_local_shared_neck_yforks",
        "grammar_rule": "F -> F[yfork(F)]F with sparse low/mid saddle-neck wood side-branches",
        "recursive_depth": int(side_depth + main_steps),
        "lsystem_branch_depth": int(side_depth),
        "main_branch_steps": int(main_steps),
        "side_branch_every": int(side_every),
        "double_sided_side_branches": bool(double_sides),
        "shared_neck_yfork_anchor_index": int(primary_anchor_new),
        "shared_neck_yfork_child_index": int(primary_child_new),
        "shared_neck_yfork_anchor_indices": sorted(set(yfork_anchor_indices))[:16],
        "shared_neck_yfork_branch_count": int(yfork_branch_count),
        "shared_neck_yfork_zoom_pairs": yfork_pairs[:6],
        "shared_neck_inserted_count": int(len(shared_neck_by_step)),
        "shared_neck_topology": "main branch continuation and side branch share an explicit low/mid centerline neck before splitting",
        "pre_subdivision_junction_count": int(junction_count),
        "pre_subdivision_terminal_side_count": int(terminal_side_count),
        "saddle_neck_count": int(saddle_neck_count),
        "terminal_fork_count": int(terminal_fork_count),
        "target_silhouette": "single woody branch with recursive side branches and no blunt main-axis terminal cap",
    }


def _shared_neck_yfork_target_pairs(
    nodes: List[np.ndarray],
    parents: List[int],
    *,
    count: int,
    pair_count: int = 16,
) -> Tuple[List[int], List[List[List[float]]], List[List[float]]]:
    """Return stable zoom targets at branch roots rather than lobe endpoints."""

    child_map = v22._children(parents)
    anchors = v34._junction_anchor_indices(nodes, parents, max(count, pair_count))
    pairs: List[List[List[float]]] = []
    flat: List[List[float]] = []
    seen: set[int] = set()
    for idx in anchors:
        if idx in seen:
            continue
        seen.add(idx)
        children = child_map.get(idx, [])
        if len(children) < 2:
            continue
        parent_idx = int(parents[idx]) if int(parents[idx]) >= 0 else idx
        anchor = np.asarray(nodes[idx], dtype=float)
        parent_axis = v22._node_axis(nodes, parents, idx) if parent_idx == idx else v22._unit(anchor - np.asarray(nodes[parent_idx], dtype=float))
        child_dirs = []
        for child in children:
            child_pos = np.asarray(nodes[child], dtype=float)
            child_dir = v22._unit(child_pos - anchor)
            branchiness = float(np.linalg.norm(child_dir - 0.72 * parent_axis))
            child_dirs.append((branchiness, child, child_pos, child_dir))
        child_dirs.sort(reverse=True, key=lambda item: item[0])
        if not child_dirs:
            continue
        _score, _child, child_pos, child_dir = child_dirs[0]
        root_target = anchor + child_dir * min(float(np.linalg.norm(child_pos - anchor)) * 0.18, 0.052)
        branch_target = anchor + child_dir * min(float(np.linalg.norm(child_pos - anchor)) * 0.42, 0.105)
        if float(np.linalg.norm(branch_target - root_target)) < ZOOM_PAIR_MIN_DISTANCE * 1.2:
            branch_target = root_target + child_dir * (ZOOM_PAIR_MIN_DISTANCE * 1.2)
        pair = [[float(x) for x in root_target], [float(x) for x in branch_target]]
        pairs.append(pair)
        flat.extend(pair)
        if len(pairs) >= pair_count:
            break
    return list(seen), pairs, flat


def _junction_anchor_indices_for_implicit(nodes: List[np.ndarray], parents: List[int], count: int) -> List[int]:
    child_map = v22._children(parents)
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    candidates = [
        idx
        for idx, children in child_map.items()
        if len(children) >= 2 and 0.12 <= depths[idx] / max(float(max_depth), 1.0) <= 0.78
    ]
    if not candidates:
        candidates = v34._junction_anchor_indices(nodes, parents, count)
    arr = np.asarray(nodes, dtype=float)
    center = arr.mean(axis=0) if len(arr) else np.zeros(3)
    candidates = sorted(
        candidates,
        key=lambda idx: (len(child_map.get(idx, [])), -abs(depths[idx] / max(float(max_depth), 1.0) - 0.45), -float(np.linalg.norm(arr[idx] - center))),
        reverse=True,
    )
    return candidates[: int(count)]


def _shared_neck_yfork_mesh_v47(
    nodes: List[np.ndarray],
    parents: List[int],
    radii: List[float],
    rng: np.random.Generator,
    *,
    fork_count: int,
    ridge_count: int,
    split_count: int,
    detail_radius_scale: float,
    lobe_scale: float,
) -> Tuple[pb.Mesh, DetailCounts, Dict]:
    """Create a continuous swept branch with boosted, sleeve-free Y-forks."""

    edges = v22._graph_edges(parents)
    child_map = v22._children(parents)
    depths = bm.graph_depths(parents)
    terminals = set(v27._terminal_nodes(parents))
    anchors = _junction_anchor_indices_for_implicit(nodes, parents, fork_count)
    anchor_set = set(int(idx) for idx in anchors)
    local_boost_nodes: set[int] = set()
    for idx in anchors:
        local_boost_nodes.add(int(idx))
        parent_idx = int(parents[idx]) if int(parents[idx]) >= 0 else -1
        if parent_idx >= 0:
            local_boost_nodes.add(parent_idx)
        for child in child_map.get(idx, [])[:3]:
            local_boost_nodes.add(int(child))

    boosted_radii = list(float(r) for r in radii)
    for idx in range(len(boosted_radii)):
        boost = 1.0
        if idx in anchor_set:
            boost = JUNCTION_RADIUS_BOOST * float(0.96 + 0.08 * lobe_scale)
        elif idx in local_boost_nodes:
            boost = JUNCTION_NEIGHBOR_RADIUS_BOOST
        if idx in terminals:
            boost *= 1.06
        boosted_radii[idx] = max(float(radii[idx]) * boost, float(radii[idx]) + 0.001)

    mesh = v22._smooth_support_mesh(nodes, edges, boosted_radii, sides=SWEEP_SIDES, ovality=0.26)
    centers = getattr(mesh, "center_indices")

    seam_centers: List[List[float]] = []
    fork_centers: List[List[float]] = []
    saddle_swell_count = 0
    cap_count = 0
    for k, idx in enumerate(anchors):
        children = child_map.get(idx, [])
        if len(children) < 2:
            continue
        anchor = np.asarray(nodes[idx], dtype=float)
        fork_centers.append([float(x) for x in anchor])
        parent_idx = int(parents[idx]) if int(parents[idx]) >= 0 else idx
        parent_axis = v22._unit(anchor - np.asarray(nodes[parent_idx], dtype=float)) if parent_idx != idx else v22._node_axis(nodes, parents, idx)
        child_dirs: List[Tuple[float, np.ndarray, int]] = []
        for child in children:
            child_dir = v22._unit(np.asarray(nodes[child], dtype=float) - anchor)
            score = float(np.linalg.norm(child_dir - 0.64 * parent_axis))
            child_dirs.append((score, child_dir, int(child)))
        child_dirs.sort(reverse=True, key=lambda item: item[0])
        for _score, child_dir, child in child_dirs[:3]:
            blend_dir = v22._unit(0.54 * parent_axis + 0.46 * child_dir)
            side_dir = v22._unit(child_dir - 0.45 * parent_axis)
            if float(np.linalg.norm(side_dir)) < 1e-7:
                side_dir = v22._basis(parent_axis)[0]
            normal = v22._unit(np.cross(blend_dir, side_dir))
            if float(np.linalg.norm(normal)) < 1e-7:
                normal = v22._basis(blend_dir)[1]
            for offset, length, radius, direction in (
                (0.020, 0.070, 0.0048, blend_dir),
                (0.058, 0.082, 0.0038, child_dir),
            ):
                center = v26._add_transition_lobe(
                    mesh,
                    centers[idx],
                    anchor,
                    direction,
                    float(length) * float(0.92 + 0.12 * lobe_scale),
                    float(radius) * float(detail_radius_scale),
                    rng,
                    rings=4,
                    sides=8,
                    curl=float(rng.uniform(0.008, 0.026)),
                )
                seam_centers.append([float(x) for x in center])
                saddle_swell_count += 1

    ridge_sites = sorted(
        [idx for idx in range(1, len(nodes)) if idx not in terminals],
        key=lambda idx: (depths[idx], idx),
        reverse=True,
    )
    ridge_written = 0
    for k, idx in enumerate(ridge_sites[: max(0, int(ridge_count) + int(split_count))]):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx)
        u, v, w = v22._basis(axis)
        lateral = v22._unit(math.cos(k * 1.73) * u + math.sin(k * 1.73) * v)
        v22._add_curved_tube_detail(
            mesh,
            centers[idx],
            anchor + lateral * max(float(boosted_radii[idx]) * 0.45, 0.006),
            v22._unit(0.86 * axis + 0.18 * lateral),
            float(rng.uniform(0.050, 0.085)),
            float(rng.uniform(0.0018, 0.0032)) * float(detail_radius_scale),
            rng,
            segments=4,
            sides=6,
            curl=float(rng.uniform(0.025, 0.070)),
        )
        ridge_written += 1

    for idx in terminals:
        parent_idx = int(parents[idx]) if int(parents[idx]) >= 0 else idx
        axis = v22._unit(np.asarray(nodes[idx], dtype=float) - np.asarray(nodes[parent_idx], dtype=float))
        v22._add_curved_tube_detail(
            mesh,
            centers[idx],
            np.asarray(nodes[idx], dtype=float),
            axis,
            float(rng.uniform(0.040, 0.062)),
            max(float(boosted_radii[idx]) * 0.42, 0.0038),
            rng,
            segments=3,
            sides=8,
            curl=float(rng.uniform(0.004, 0.020)),
        )
        cap_count += 1

    counts = _blank_counts()
    counts["collar_count"] = int(saddle_swell_count + len(anchors))
    counts["flare_count"] = int(saddle_swell_count + len(anchors))
    counts["ridge_count"] = int(ridge_written)
    counts["split_count"] = int(max(0, ridge_written - int(ridge_count)))
    return mesh, counts, {
        "junction_anchor_count": int(len(set(anchors))),
        "junction_collar_count": int(counts["collar_count"]),
        "junction_cambium_lobe_count": 0,
        "seam_mask_center_count": int(len(seam_centers)),
        "seam_mask_centers": seam_centers[:128],
        "shared_neck_yfork_centers": fork_centers[:128],
        "seam_mask_radius": 0.152,
        "shared_neck_support": True,
        "mechanical_sleeve_disabled": True,
        "direct_axis_sleeve_count": 0,
        "junction_shared_neck_count": int(len(set(anchors))),
        "implicit_saddle_swell_count": int(saddle_swell_count),
        "terminal_cap_twig_count": int(cap_count),
        "sweep_sides": int(SWEEP_SIDES),
        "junction_radius_boost": float(JUNCTION_RADIUS_BOOST),
        "junction_neighbor_radius_boost": float(JUNCTION_NEIGHBOR_RADIUS_BOOST),
        "raw_marching_cubes_component_count": 1,
        "largest_component_projection_retained_ratio": 1.0,
        "pre_marching_cubes_primitive_count": int(len(edges) + saddle_swell_count + ridge_written + cap_count),
        "low_relief_lobe_policy": "transition lobes are intentionally small; fusion is carried by graph-shared neck plus radius boost",
    }


def _add_shared_neck_yfork_collars(
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
    shared_neck_yforks: List[List[float]] = []
    for k, idx in enumerate(anchors):
        anchor = np.asarray(nodes[idx], dtype=float)
        shared_neck_yforks.append([float(x) for x in anchor])
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
                    float(rng.uniform(0.045, 0.082)) * float(lobe_scale),
                    float(rng.uniform(0.0065, 0.0125)) * float(radius_scale),
                    rng,
                    rings=5,
                    sides=8,
                    curl=float(rng.uniform(0.015, 0.055)),
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
                    float(rng.uniform(0.105, 0.175)),
                    float(rng.uniform(0.0030, 0.0052)) * float(radius_scale),
                    rng,
                    segments=5,
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
        "shared_neck_yfork_centers": shared_neck_yforks[:128],
        "seam_mask_radius": 0.106,
    }


def _add_broad_shared_neck_yfork_saddles(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    count: int,
    radius_scale: float,
    lobe_scale: float,
) -> Tuple[DetailCounts, Dict]:
    """Add thick, short union collars that read as wood, not as leaves.

    V42's many narrow ridges gave the texturing/export step too many thin
    strokes to reinterpret.  These collars are deliberately fewer, wider, and
    aligned with the parent/child axes around low/mid Y junctions.
    """

    centers = getattr(mesh, "center_indices")
    child_map = v22._children(parents)
    anchors = v34._junction_anchor_indices(nodes, parents, count)
    counts = _blank_counts()
    seam_centers: List[List[float]] = []
    yfork_centers: List[List[float]] = []
    for k, idx in enumerate(anchors):
        children = child_map.get(idx, [])
        if not children:
            continue
        anchor = np.asarray(nodes[idx], dtype=float)
        yfork_centers.append([float(x) for x in anchor])
        parent_idx = int(parents[idx]) if int(parents[idx]) >= 0 else idx
        parent_axis = v22._unit(anchor - np.asarray(nodes[parent_idx], dtype=float)) if parent_idx != idx else v22._node_axis(nodes, parents, idx)
        child_dirs = [
            v22._unit(np.asarray(nodes[ch], dtype=float) - anchor)
            for ch in children[:2]
        ]
        for child_dir in child_dirs:
            for blend in (0.42, 0.68):
                direction = v22._unit((1.0 - blend) * parent_axis + blend * child_dir)
                center = v26._add_transition_lobe(
                    mesh,
                    centers[idx],
                    anchor,
                    direction,
                    float(rng.uniform(0.070, 0.118)) * float(lobe_scale),
                    float(rng.uniform(0.0135, 0.0230)) * float(radius_scale),
                    rng,
                    rings=6,
                    sides=11,
                    curl=float(rng.uniform(0.004, 0.026)),
                )
                seam_centers.append([float(x) for x in center])
                counts["collar_count"] += 1
                counts["flare_count"] += 1
                counts["tendril_count"] += 1
    return counts, {
        "junction_anchor_count": int(len(set(anchors))),
        "junction_collar_count": int(counts["collar_count"]),
        "junction_cambium_lobe_count": 0,
        "seam_mask_center_count": int(len(seam_centers)),
        "seam_mask_centers": seam_centers[:128],
        "shared_neck_yfork_centers": yfork_centers[:128],
        "seam_mask_radius": 0.126,
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
    nodes, parents, lsys_diag = _lsystem_branch_graph_v47(
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
    radii = _branch_radii_v47(
        parents,
        base=base_radius,
        taper=radius_taper,
        floor=radius_floor,
        terminal_shrink=terminal_shrink,
        tip_parent_shrink=tip_parent_shrink,
        high_depth_shrink=high_depth_shrink,
    )
    edges = v22._graph_edges(parents)
    mesh, collar_counts, collar_diag = _shared_neck_yfork_mesh_v47(
        nodes,
        parents,
        radii,
        rng,
        fork_count=collar_count,
        ridge_count=ridge_count,
        split_count=split_count,
        detail_radius_scale=detail_radius_scale,
        lobe_scale=lobe_scale,
    )
    ridge_counts = _blank_counts()
    split_counts = _blank_counts()
    bud_counts = _blank_counts()
    bud_diag = {"terminal_bud_count": 0, "terminal_bud_leaf_count": 0, "terminal_bud_centers": []}
    sleeve_counts = _blank_counts()
    sleeve_diag = {"terminal_sleeve_count": 0, "terminal_sleeve_leaf_count": 0, "terminal_sleeve_centers": []}
    sheath_counts = _blank_counts()
    counts = _merge_counts(collar_counts, ridge_counts, split_counts, bud_counts, sleeve_counts, sheath_counts)
    junction_anchor_indices, junction_zoom_pairs, junction_zoom_centers = _shared_neck_yfork_target_pairs(
        nodes,
        parents,
        count=collar_count,
        pair_count=24,
    )
    primary_pairs = list(lsys_diag.get("shared_neck_yfork_zoom_pairs", []))
    if primary_pairs:
        remaining_pairs = [
            pair
            for pair in junction_zoom_pairs
            if min(float(np.linalg.norm(np.asarray(pair[0]) - np.asarray(primary_pairs[0][0]))), float(np.linalg.norm(np.asarray(pair[1]) - np.asarray(primary_pairs[0][1])))) > 1e-5
        ]
        junction_zoom_pairs = primary_pairs + remaining_pairs
        junction_zoom_centers = [point for pair in junction_zoom_pairs for point in pair]
    seam_centers = junction_zoom_centers + list(collar_diag.get("seam_mask_centers", []))[:48]
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
            "support_cross_section": "broad_oval_shared_neck_yfork_read",
            "support_visibility_policy": "broad tapered wood support remains visible, while side-branch bases leave through thick saddle-neck geometry",
            "main_curve": float(main_curve),
            "side_angle": float(side_angle),
            "side_length": float(side_length),
            "saddle_neck_count": int(lsys_diag.get("saddle_neck_count", 0)),
            "terminal_fork_count": int(lsys_diag.get("terminal_fork_count", 0)),
            "shared_neck_inserted_count": int(lsys_diag.get("shared_neck_inserted_count", 0)),
            "shared_neck_topology": lsys_diag.get("shared_neck_topology", ""),
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
            "v47_lsystem_branch_shared_neck_yfork_naturalization": True,
            "shared_neck_support": bool(collar_diag.get("shared_neck_support", False)),
            "mechanical_sleeve_disabled": bool(collar_diag.get("mechanical_sleeve_disabled", False)),
            "direct_axis_sleeve_count": int(collar_diag.get("direct_axis_sleeve_count", 0)),
            "junction_shared_neck_count": int(collar_diag.get("junction_shared_neck_count", 0)),
            "implicit_saddle_swell_count": int(collar_diag.get("implicit_saddle_swell_count", 0)),
            "sweep_sides": int(collar_diag.get("sweep_sides", 0)),
            "junction_radius_boost": float(collar_diag.get("junction_radius_boost", 0.0)),
            "junction_neighbor_radius_boost": float(collar_diag.get("junction_neighbor_radius_boost", 0.0)),
            "raw_marching_cubes_component_count": int(collar_diag.get("raw_marching_cubes_component_count", 0)),
            "largest_component_projection_retained_ratio": float(collar_diag.get("largest_component_projection_retained_ratio", 0.0)),
            "pre_marching_cubes_primitive_count": int(collar_diag.get("pre_marching_cubes_primitive_count", 0)),
            "v35_failure_addressed": "pure-white zoom still read as a large cut branch tube with side detail attached near it",
            "v36_failure_addressed": "mid-junction zoom still exposed a blunt large main-axis terminal and branch-on-tube attachment",
            "v38_failure_addressed": "object-space zoom targets drifted to collar endpoints, and terminal sleeves still rendered as isolated wedge caps",
            "v40_failure_addressed": "topology-stable slim candidate remained too sparse for a dense branch-with-side-branches main visual",
            "v41_failure_addressed": "global dense secondary branching became needle/leaf fragments after GLB and degraded exact r0 connectivity",
            "v42_failure_addressed": "post-GLB remained connected but read as thin line skeleton plus blade-like buds/needles instead of continuous wood forks",
            "v45_failure_addressed": "whole-branch implicit union removed sleeve seams but collapsed the branch into a coarse blob/root-like object",
            "v46_failure_addressed": "continuous sweep recovered the branch silhouette but zoom still read as hard thin tubes plus small local bumps",
            "masked_local_naturalization_target": "L-system saddle-neck side-branch shared-neck-yfork bands with wood-only tapered terminals",
            "mask_scope": "object_space_side_branch_saddle_shared_neck_yfork_bands_only",
            "seam_mask_space": "object_xyz",
            "seam_mask_selection_rule": "degree>=2 L-system saddle junction root nodes and child-axis midpoints; no global resampling; terminal sleeve anchors excluded",
            "seam_mask_center_count": int(len(seam_centers)),
            "seam_mask_centers": seam_centers[:96],
            "junction_zoom_target_count": int(len(junction_zoom_centers)),
            "junction_zoom_targets": junction_zoom_centers[:48],
            "junction_zoom_pair_count": int(len(junction_zoom_pairs)),
            "junction_zoom_pairs": junction_zoom_pairs[:24],
            "shared_neck_yfork_zoom_pairs": primary_pairs[:4],
            "shared_neck_yfork_zoom_pair_count": int(len(primary_pairs)),
            "shared_neck_yfork_anchor_indices": list(lsys_diag.get("shared_neck_yfork_anchor_indices", []))[:16],
            "shared_neck_yfork_branch_count": int(lsys_diag.get("shared_neck_yfork_branch_count", 0)),
            "shared_neck_inserted_count": int(lsys_diag.get("shared_neck_inserted_count", 0)),
            "shared_neck_topology": lsys_diag.get("shared_neck_topology", ""),
            "junction_zoom_pair_min_distance": float(ZOOM_PAIR_MIN_DISTANCE),
            "seam_mask_radius": float(collar_diag.get("seam_mask_radius", 0.118)),
            "branch_junction_count": int(branch_junction_count),
            "terminal_count": int(terminal_count),
            "saddle_neck_count": int(lsys_diag.get("saddle_neck_count", 0)),
            "terminal_fork_count": int(lsys_diag.get("terminal_fork_count", 0)),
            "junction_anchor_count": int(max(collar_diag.get("junction_anchor_count", 0), len(junction_anchor_indices))),
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
            "material_transition_policy": "continuous bark/cambium/cedar guide; no hard green-brown junction stripe or leaf-colored seam cover",
            "claim_boundary": "grammar-owned local geometry/material candidate; no 2D seam inpaint backprojection claim",
            "hard_tube_cap_mitigation": "generator-native shared neck graph topology with wood-only twig continuation; terminal sleeves and axis sleeve append geometry disabled",
            "shared_neck_yfork_zoom_target_policy": "first manifest pair is the explicit low/mid graph shared neck yfork, not an inferred collar, terminal, or V41-style global dense twig",
        }
    )
    grammar = {
        "grammar_family": "L-system",
        "grammar_symbols": "F,+,-,[,],side_branch,saddle_neck,shared_neck_yfork_mask,cambium_collar,bark_ridge,terminal_twig",
        "target_symbol": "F",
        "operator_to_traditional_mapping": {
            "F": "advance a finite turtle branch segment and create connected swept support",
            "+/-": "yaw side branches from the main branch frame",
            "[]": "push/pop recursive side-branch state",
            "side_branch": "instantiate the same branch-with-side-branches target used by the traditional L-system baseline",
            "saddle_neck": "insert a short shared centerline neck used by both main continuation and side branch before turn-out",
            "shared_neck_yfork_mask": "select side-branch attachment nodes and child-axis midpoints after rewriting",
            "cambium_collar": "locally fuse side-branch bases without global resampling",
            "bark_ridge": "add connected non-round bark relief instead of a smooth tube",
            "terminal_twig": "replace exposed branch caps with connected fine twig continuations",
        },
        "remote_comparison_unit": "one generated OBJ input to one traditional L-system branch-with-side-branches target",
    }
    return mesh, controls, grammar


def _write_guides(out_dir: Path) -> Dict[str, str]:
    guide_dir = out_dir / "_guides"
    guides: Dict[str, str] = {}
    palettes = {
        "cedar": [(62, 43, 25), (86, 57, 30), (112, 75, 40), (126, 92, 55)],
        "cambium": [(72, 48, 27), (98, 64, 34), (130, 88, 48), (150, 112, 70)],
        "olive": [(58, 48, 32), (84, 66, 42), (110, 84, 50), (126, 104, 64)],
        "ridge": [(50, 38, 26), (78, 54, 34), (118, 82, 48), (140, 104, 66)],
    }
    for key, colors in palettes.items():
        path = guide_dir / f"V47_lsystem_branch_{key}_lowcontrast_guide.png"
        rng = np.random.default_rng(v26._stable_seed(path.stem))
        img = Image.new("RGB", (768, 768), (70, 58, 40))
        draw = ImageDraw.Draw(img, "RGBA")
        for _ in range(70):
            color = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(-140, 900))
            y = int(rng.integers(-140, 900))
            r = int(rng.integers(120, 280))
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, int(rng.integers(34, 82))))
        img = img.filter(ImageFilter.GaussianBlur(radius=22))
        draw = ImageDraw.Draw(img, "RGBA")
        for _ in range(36):
            color = colors[int(rng.integers(0, len(colors)))]
            base = np.array([rng.integers(80, 690), rng.integers(120, 670)], dtype=float)
            length = float(rng.uniform(120, 260))
            angle = float(rng.uniform(-2.45, -0.62))
            pts = []
            for t in np.linspace(0.0, 1.0, 8):
                curve = math.sin(t * math.pi) * rng.uniform(-10, 12)
                p = base + np.array([math.cos(angle) * length * t + curve, math.sin(angle) * length * t], dtype=float)
                pts.append((int(p[0]), int(p[1])))
            draw.line(pts, fill=(*color, int(rng.integers(70, 128))), width=int(rng.integers(5, 10)))
            fork = pts[int(rng.integers(2, len(pts) - 2))]
            side_angle = float(angle + rng.choice([-1.0, 1.0]) * rng.uniform(0.50, 0.82))
            end = (
                int(fork[0] + math.cos(side_angle) * length * rng.uniform(0.30, 0.48)),
                int(fork[1] + math.sin(side_angle) * length * rng.uniform(0.30, 0.48)),
            )
            draw.line((fork, end), fill=(*color, int(rng.integers(62, 112))), width=int(rng.integers(3, 7)))
        path.parent.mkdir(parents=True, exist_ok=True)
        img.filter(ImageFilter.SMOOTH_MORE).save(path)
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
        "object_space_side_branch_shared_neck_yfork_mask",
        "shared_vertex_cambium_collars",
        "wood_only_terminal_twigs",
        "broad_shared_vertex_cambium_saddles",
        "minimal_connected_bark_ridges",
        "minimal_structural_branch_splits",
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
            "v47_lsystem_branch_shared_neck_yfork_naturalization": True,
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
        "grammar_guide": "v47_lsystem_branch_lowcontrast_bark_cambium_guide",
        "parameter_variant": parameter_variant,
        "gpu": int(gpu),
        "seed": int(seed),
        "operators": operators,
        "operator_composition": " -> ".join(operators),
        "grammar_mapping": v23._grammar_mapping("L-system", "lsys_branch_side_d5", controls, grammar),
        "family_diagnostics": v23._family_diagnostics("L-system", "lsys_branch_side_d5", controls),
        "why_matches_traditional": reason,
        "strict_match_notes": reason,
            "case_role": "v47_lsystem_branch_shared_neck_yfork_naturalization",
            "qa_priority": "shared_neck_wood_fork_naturalness_no_spherical_collar_mechanical_sleeve_or_leaf_shard_read",
        "rerun_reason": reason,
        "boundary_tag": "",
    }


def _case_specs(seed: int) -> List[Dict]:
    settings = [
        ("V47_lsys_branch_shared_neck_yfork_A", 4, 43001, 7, 2, 2, True, 0.30, 0.60, 0.82, 0.032, 0.782, 0.0060, 0.24, 0.42, 0.52, 0.075, 10, 8, 2, 0, 0, 0, 0, 0, 1.05, 1.06, "cambium", "shared-neck-yfork A: broad low/mid continuous wood saddles, minimal free ridges, no leaf-shard seam cover"),
        ("V47_lsys_branch_shared_neck_yfork_lowfrag_B", 5, 43002, 8, 2, 2, True, 0.26, 0.54, 0.78, 0.030, 0.790, 0.0056, 0.22, 0.40, 0.54, 0.075, 8, 6, 1, 0, 0, 0, 0, 0, 0.98, 1.00, "ridge", "shared-neck-yfork lowfrag B: most conservative connected wood-fork candidate with thick support and very few thin details"),
        ("V47_lsys_branch_shared_neck_yfork_dense_C", 4, 43003, 7, 2, 2, True, 0.34, 0.66, 0.86, 0.034, 0.774, 0.0062, 0.24, 0.44, 0.52, 0.072, 12, 10, 3, 0, 0, 0, 0, 0, 1.10, 1.10, "cedar", "shared-neck-yfork dense C: strongest broad Y-fork silhouette while avoiding V41/V42 needle and blade fragments"),
        ("V47_lsys_branch_shared_neck_yfork_slim_D", 5, 43004, 8, 2, 2, False, 0.22, 0.50, 0.72, 0.028, 0.798, 0.0052, 0.22, 0.38, 0.56, 0.078, 7, 5, 1, 0, 0, 0, 0, 0, 0.94, 0.96, "olive", "shared-neck-yfork slim D: V40-D-like stability but with thicker low/mid saddle fork and no green leaf shards"),
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
                root_variant=case_id.replace("V47_", ""),
                parameter_variant=(
                    f"main{main_steps}_sideD{side_depth}_every{side_every}_double{int(double_sides)}"
                    f"_maxseg{max_segment:.3f}_base{base_radius:.3f}_tip{terminal_shrink:.2f}"
                    f"_parent{tip_parent_shrink:.2f}_woodridge{ridge_count}_woodsleeve{terminal_sleeve_count}"
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
    metadata["root_selection_log"]["root_source_type"] = "V47_lsystem_branch_shared_neck_yfork_naturalization_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V47_lsystem_branch_shared_neck_yfork_naturalization_20260511.py"
    metadata["v47_lsystem_branch_naturalization_contract"] = {
        "target_failure": "V35 remained connected but still read as a cut branch tube with small side geometry attached; V38 removed the large cap but zoomed lobe endpoints and terminal sleeves still read as isolated wedges; V40-D was topology-stable but sparse; V41 became denser but post-GLB zooms fragmented into needle/leaf shards and exact r0 connectivity dropped",
        "geometry_operator": "continuous high-sided swept support with junction-local radius boost and short transition lobes; no appended axis sleeves and no whole-branch marching-cubes blob",
        "seam_mask": {
            "space": "object_xyz",
            "scope": controls.get("mask_scope"),
            "selection_rule": controls.get("seam_mask_selection_rule"),
            "radius": controls.get("seam_mask_radius"),
            "center_count": controls.get("seam_mask_center_count"),
            "centers": controls.get("seam_mask_centers", [])[:96],
        },
        "zoom_targets": {
            "source": "shared-neck-yfork object-space graph node plus child-axis midpoint, using the first broad low/mid y-fork and excluding terminal buds/sleeves, collar endpoints, and V41/V42-style thin twig targets",
            "count": controls.get("junction_zoom_target_count"),
            "centers": controls.get("junction_zoom_targets", [])[:48],
            "pair_count": controls.get("junction_zoom_pair_count"),
            "pairs": controls.get("junction_zoom_pairs", [])[:24],
            "explicit_primary_pair": controls.get("shared_neck_yfork_zoom_pairs", [])[:1],
        },
        "naturalization_regions": ["broad_side_branch_saddle_shared_neck_yfork_band", "wood_only_terminal_twigs", "low_relief_bark_ridges"],
        "shared_neck": {
            "enabled": controls.get("shared_neck_support"),
            "sweep_sides": controls.get("sweep_sides"),
            "junction_radius_boost": controls.get("junction_radius_boost"),
            "junction_neighbor_radius_boost": controls.get("junction_neighbor_radius_boost"),
            "raw_marching_cubes_component_count": controls.get("raw_marching_cubes_component_count"),
            "largest_component_projection_retained_ratio": controls.get("largest_component_projection_retained_ratio"),
            "mechanical_sleeve_disabled": controls.get("mechanical_sleeve_disabled"),
            "direct_axis_sleeve_count": controls.get("direct_axis_sleeve_count"),
            "junction_shared_neck_count": controls.get("junction_shared_neck_count"),
            "implicit_saddle_swell_count": controls.get("implicit_saddle_swell_count"),
            "shared_neck_inserted_count": controls.get("shared_neck_inserted_count"),
            "shared_neck_topology": controls.get("shared_neck_topology"),
        },
        "sdedit_seam_backprojection_available": False,
        "texture_operator": "low-contrast whole-object guide for Trellis2 texturing; no 2D seam inpaint backprojection claim",
        "material_transition_policy": controls.get("material_transition_policy"),
        "claim_boundary": controls.get("claim_boundary"),
        "post_glb_acceptance": "paper candidate only if side-branch saddle zoom no longer reads as a hard inserted tube, terminal endpoint is not a blunt pipe, and r1 LCR remains 1.0; preferred r0 LCR >=0.999",
    }
    metadata["v47_remote_cache_policy"] = {
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
            raise RuntimeError(f"{spec['case_id']} failed V47 connectivity gate: {metrics}")
        if float(spec["controls"].get("external_support_max_segment_after_subdivision", 999.0)) > EXTERNAL_SUPPORT_MAX_SEGMENT_GATE + 1e-6:
            raise RuntimeError(f"{spec['case_id']} failed V47 short-segment gate: {spec['controls']}")
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
            "shared_neck_yfork_branch_count": int(spec["controls"].get("shared_neck_yfork_branch_count", 0)),
            "shared_neck_inserted_count": int(spec["controls"].get("shared_neck_inserted_count", 0)),
            "shared_neck_support": str(bool(spec["controls"].get("shared_neck_support", False))).lower(),
            "mechanical_sleeve_disabled": str(bool(spec["controls"].get("mechanical_sleeve_disabled", False))).lower(),
            "direct_axis_sleeve_count": int(spec["controls"].get("direct_axis_sleeve_count", 0)),
            "junction_shared_neck_count": int(spec["controls"].get("junction_shared_neck_count", 0)),
            "implicit_saddle_swell_count": int(spec["controls"].get("implicit_saddle_swell_count", 0)),
            "raw_marching_cubes_component_count": int(spec["controls"].get("raw_marching_cubes_component_count", 0)),
            "largest_component_projection_retained_ratio": float(spec["controls"].get("largest_component_projection_retained_ratio", 0.0)),
            "pre_marching_cubes_primitive_count": int(spec["controls"].get("pre_marching_cubes_primitive_count", 0)),
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
                "shared_neck_yfork_branch_count": int(spec["controls"].get("shared_neck_yfork_branch_count", 0)),
                "shared_neck_inserted_count": int(spec["controls"].get("shared_neck_inserted_count", 0)),
                "shared_neck_support": str(bool(spec["controls"].get("shared_neck_support", False))).lower(),
                "mechanical_sleeve_disabled": str(bool(spec["controls"].get("mechanical_sleeve_disabled", False))).lower(),
                "direct_axis_sleeve_count": int(spec["controls"].get("direct_axis_sleeve_count", 0)),
                "junction_shared_neck_count": int(spec["controls"].get("junction_shared_neck_count", 0)),
                "implicit_saddle_swell_count": int(spec["controls"].get("implicit_saddle_swell_count", 0)),
                "raw_marching_cubes_component_count": int(spec["controls"].get("raw_marching_cubes_component_count", 0)),
                "largest_component_projection_retained_ratio": float(spec["controls"].get("largest_component_projection_retained_ratio", 0.0)),
                "pre_marching_cubes_primitive_count": int(spec["controls"].get("pre_marching_cubes_primitive_count", 0)),
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
        target_pairs = controls.get("junction_zoom_pairs", [])
        targets = controls.get("junction_zoom_targets", [])[:32] or controls.get("seam_mask_centers", [])[:32]
        fixed_targets = []
        if target_pairs:
            fixed_targets = target_pairs[0][:2]
        elif targets:
            fixed_targets = [targets[0], targets[min(1, len(targets) - 1)]]
        obj_zoom_cases.append(
            {
                "label": row["case_id"] + "_obj_junctiontarget",
                "mesh": str(Path(row["mesh_path"]).resolve()),
                "plan_mesh": str(Path(row["mesh_path"]).resolve()),
                "material_mode": "cedar",
                "zoom_levels": 2,
                "zoom_divisor": 3.2,
                "detail_targets": targets,
                "fixed_detail_targets": fixed_targets,
                "detail_target_source": "v47_lsystem_explicit_shared_neck_yfork_mask",
            }
        )
    (out_dir / "V47_obj_zoom_manifest_junctiontarget_20260511.json").write_text(
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
        "surface_generator": "strict_visual_matched_cases_V47_lsystem_branch_shared_neck_yfork_naturalization",
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
            "mask_scope": "object_space_side_branch_saddle_shared_neck_yfork_bands_only",
            "min_branch_junctions": min(int(row["branch_junction_count"]) for row in rows) if rows else 0,
            "min_saddle_necks": min(int(row["saddle_neck_count"]) for row in rows) if rows else 0,
            "min_terminal_forks": min(int(row["terminal_fork_count"]) for row in rows) if rows else 0,
            "min_shared_neck_yfork_branches": min(int(row["shared_neck_yfork_branch_count"]) for row in rows) if rows else 0,
            "min_shared_neck_inserted": min(int(row["shared_neck_inserted_count"]) for row in rows) if rows else 0,
            "shared_neck_support_required": True,
            "mechanical_sleeve_disabled_required": True,
            "min_junction_shared_necks": min(int(row["junction_shared_neck_count"]) for row in rows) if rows else 0,
            "min_implicit_saddle_swells": min(int(row["implicit_saddle_swell_count"]) for row in rows) if rows else 0,
            "max_direct_axis_sleeves": max(int(row["direct_axis_sleeve_count"]) for row in rows) if rows else 0,
            "max_raw_marching_cubes_components": max(int(row["raw_marching_cubes_component_count"]) for row in rows) if rows else 0,
            "min_largest_component_projection_retained_ratio": min(float(row["largest_component_projection_retained_ratio"]) for row in rows) if rows else 0.0,
            "min_seam_mask_centers": min(int(row["seam_mask_center_count"]) for row in rows) if rows else 0,
            "min_junction_zoom_targets": min(int(row["junction_zoom_target_count"]) for row in rows) if rows else 0,
            "min_junction_collars": min(int(row["junction_collar_count"]) for row in rows) if rows else 0,
            "min_terminal_buds": min(int(row["terminal_bud_count"]) for row in rows) if rows else 0,
            "min_terminal_sleeves": min(int(row["terminal_sleeve_count"]) for row in rows) if rows else 0,
            "terminal_sleeves_required": False,
            "junction_zoom_pair_min_distance": ZOOM_PAIR_MIN_DISTANCE,
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
            "visual_gate": "side-branch saddle zoom must not read as hard inserted tubes; terminal sleeves are disabled and wood-only terminals must stay non-dominant",
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
        "obj_zoom_manifest": str(out_dir / "V47_obj_zoom_manifest_junctiontarget_20260511.json"),
        "do_not_launch_remote_before_local_visual_qa": True,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V47 L-system Branch Junction-Root Naturalization Dry Run\n\n"
        "V47 repairs the V35/V36/V38/V40/V41/V42/V44 visual failure modes: connected metrics but pure-white zoom still read as a tube with attached side detail, "
        "isolated terminal/collar wedges, a topology-stable but too-sparse V40-D, V41-style needle fragmentation, or V42-style thin skeleton plus blade shards. "
        "It replaces V44's tube-plus-sleeve construction and V45's over-blobby whole-field union with a high-sided shared neck, junction-local radius boost, short transition lobes, and bark-ridge primitives. "
        "It keeps paired graph-root zoom targets, wood-only twig terminals, minimal free ridges/splits, and whole-object low-contrast guides. "
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
