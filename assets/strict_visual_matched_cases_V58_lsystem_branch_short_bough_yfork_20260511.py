#!/usr/bin/env python3
"""V58 L-system short-bough Y-fork naturalization inputs.

V54--V57 kept improving local metrics on the same long, thin branch skeleton,
but pure-white zoom QA still read as tube skeletons, cut ends, and saddle
bulges.  V58 changes the root silhouette instead of applying another local
patch: a compact mid-bough segment with fewer, thicker side branches, explicit
shared-neck Y-forks, and graph-native tapered terminals.  The claim remains
bounded to grammar-owned object-space naturalization; no 2D seam inpaint or
backprojection pipeline is claimed.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import io
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

import strict_visual_matched_cases_V53_lsystem_branch_natural_bough_graph_yfork_20260511 as v53


bm = v53.bm
pb = v53.pb
v22 = v53.v22
v27 = v53.v27

REMOTE_TARGET = v53.REMOTE_TARGET
ALLOWED_GPUS = v53.ALLOWED_GPUS
DEFAULT_ACTIVE_GPUS = v53.DEFAULT_ACTIVE_GPUS
REMOTE_STORAGE_ROOT = v53.REMOTE_STORAGE_ROOT
STORAGE_LIMIT_GB = v53.STORAGE_LIMIT_GB
CONNECTIVITY_LCR_MIN = v53.CONNECTIVITY_LCR_MIN
EXTERNAL_SUPPORT_MAX_SEGMENT_GATE = v53.EXTERNAL_SUPPORT_MAX_SEGMENT_GATE
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V58_lsystem_branch_short_bough_yfork_20260511_dryrun"

SURFACE_STRATEGY = "v58_lsystem_branch_short_bough_yfork_root_silhouette_naturalization"
GENERATION_POLICY = v53.GENERATION_POLICY
SELECTION_BUDGET = "four_v58_lsystem_short_bough_candidates_local_qa_then_two_gpu_remote"
MESH_PBR_POLICY = v53.MESH_PBR_POLICY
ZOOM_DIVISOR = 1.88

_ORIG_GRAPH = v53._lsystem_branch_graph_v53
_ORIG_RADII = v53._branch_radii_v53
_ORIG_CASE_SPECS = v53._case_specs
_ORIG_METADATA_FOR = v53._metadata_for
_ORIG_SPEC = v53._spec
_ORIG_SURFACE_STRATEGY = v53.SURFACE_STRATEGY
_ORIG_SELECTION_BUDGET = v53.SELECTION_BUDGET


def _terminal_lineage(parents: List[int], hops: int = 6) -> Dict[int, int]:
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


def _lsystem_branch_graph_v58(
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
    """Compact L-system branch segment with short, thick side branches.

    The graph deliberately stops chasing a full sparse branch skeleton.  It
    represents the traditional branch-with-side-branches target as a crop-like
    mid-bough: side branches leave through shared centerline necks, while all
    exposed terminals receive graph-native taper chains before implicit field
    construction.
    """

    rng = np.random.default_rng(seed + 5801)
    nodes: List[np.ndarray] = [np.zeros(3, dtype=float)]
    parents: List[int] = [-1]
    main_axis = v22._unit(np.array([0.88, -0.04, 0.24], dtype=float) + rng.normal(0.0, 0.012, 3))
    u, v, _w = v22._basis(main_axis)
    parent = 0
    main_indices = [0]
    junction_count = 0
    terminal_side_count = 0
    saddle_neck_count = 0
    terminal_fork_count = 0
    graph_terminal_taper_count = 0
    raw_yfork_pairs: List[List[List[float]]] = []
    yfork_anchor_indices: List[int] = []
    yfork_branch_count = 0

    for step_i in range(1, int(main_steps) + 1):
        t = step_i / max(float(main_steps), 1.0)
        bend = float(main_curve) * 0.22 * math.sin(step_i * 0.82 + seed * 0.0017)
        direction = v22._unit(main_axis + bend * v + 0.055 * math.cos(step_i * 0.74) * u + rng.normal(0.0, 0.007, 3))
        seg_len = float(rng.uniform(0.22, 0.31)) * (1.0 - 0.08 * max(t - 0.50, 0.0))
        current = v53._append_node(nodes, parents, parent, np.asarray(nodes[parent], dtype=float) + direction * seg_len)
        main_indices.append(current)
        parent = current

    raw_steps = [
        max(1, min(int(main_steps) - 1, int(round(main_steps * 0.30)))),
        max(1, min(int(main_steps) - 1, int(round(main_steps * 0.52)))),
        max(1, min(int(main_steps) - 1, int(round(main_steps * 0.72)))),
    ]
    yfork_steps = sorted(set(raw_steps))
    primary_step = yfork_steps[0]
    primary_sign = -1 if seed % 2 else 1
    implicit_capsule_by_step: Dict[int, int] = {}

    def implicit_capsule_for_step(step: int) -> int:
        if step in implicit_capsule_by_step:
            return implicit_capsule_by_step[step]
        idx = main_indices[step]
        next_idx = main_indices[min(step + 1, len(main_indices) - 1)]
        anchor = np.asarray(nodes[idx], dtype=float)
        if next_idx == idx:
            axis = v22._node_axis(nodes, parents, idx)
            neck_pos = anchor + axis * 0.075
        else:
            next_pos = np.asarray(nodes[next_idx], dtype=float)
            axis = v22._unit(next_pos - anchor)
            neck_pos = anchor + axis * min(max(float(np.linalg.norm(next_pos - anchor)) * 0.40, 0.064), 0.105)
        neck_idx = v53._append_node(nodes, parents, idx, neck_pos)
        if next_idx != idx and int(parents[next_idx]) == idx:
            parents[next_idx] = neck_idx
        implicit_capsule_by_step[step] = neck_idx
        return neck_idx

    def add_short_side(parent_idx: int, start_dir: np.ndarray, length0: float, depth: int, spread: float) -> int:
        nonlocal junction_count, terminal_side_count, saddle_neck_count, terminal_fork_count
        parent_axis = v22._node_axis(nodes, parents, parent_idx)
        neck_dir = v22._unit(0.68 * parent_axis + 0.32 * start_dir)
        neck = v53._append_node(nodes, parents, parent_idx, np.asarray(nodes[parent_idx], dtype=float) + neck_dir * length0 * 0.20)
        saddle_neck_count += 1
        turn_dir = v22._unit(0.38 * parent_axis + 0.62 * start_dir)
        shoulder = v53._append_node(nodes, parents, neck, np.asarray(nodes[neck], dtype=float) + turn_dir * length0 * 0.34)
        current = v53._append_node(nodes, parents, shoulder, np.asarray(nodes[shoulder], dtype=float) + start_dir * length0 * 0.34)
        if depth > 0:
            junction_count += 1
            cu, cv, _cw = v22._basis(start_dir)
            child_count = 2 if depth >= 2 else 1
            for s_i in range(child_count):
                sign = -1 if s_i == 0 else 1
                child_dir = v22._unit(
                    0.78 * start_dir
                    + sign * spread * 0.44 * cu
                    + (0.035 - 0.016 * s_i) * cv
                    + rng.normal(0.0, 0.004, 3)
                )
                child_len = length0 * float(rng.uniform(0.36, 0.50))
                add_short_side(current, child_dir, child_len, depth - 1, spread * 0.40)
        else:
            terminal_side_count += 1
            terminal_fork_count += 1
        return current

    primary_child = -1
    for j, step in enumerate(yfork_steps):
        idx = implicit_capsule_for_step(step)
        axis = v22._node_axis(nodes, parents, idx)
        su, sv, _sw = v22._basis(axis)
        anchor = np.asarray(nodes[idx], dtype=float)
        if double_sides and j == 1:
            branch_signs = (primary_sign, -primary_sign)
        else:
            branch_signs = (primary_sign,)
        for local_i, sign in enumerate(branch_signs):
            side_dir = v22._unit(
                0.50 * axis
                + sign * (0.46 - 0.030 * local_i) * su
                + (0.070 + 0.010 * j) * sv
                + np.array([0.0, 0.0, 0.030])
                + rng.normal(0.0, 0.005, 3)
            )
            depth = max(0, int(side_depth) - (1 if j >= 2 else 0))
            length = float(side_length) * float(rng.uniform(0.44, 0.58)) * (1.0 - 0.060 * j)
            child = add_short_side(idx, side_dir, length, depth, 0.19 if j == 0 else 0.15)
            if primary_child < 0:
                primary_child = child
            yfork_branch_count += 1
            yfork_anchor_indices.append(int(idx))
            if len(raw_yfork_pairs) < 8:
                raw_yfork_pairs.append(
                    [
                        [float(x) for x in (anchor + side_dir * 0.050)],
                        [float(x) for x in (anchor + side_dir * 0.125)],
                    ]
                )
        primary_sign *= -1

    for end_idx, scale in ((main_indices[0], -1.0), (main_indices[-1], 1.0)):
        axis = v22._node_axis(nodes, parents, end_idx) * scale
        pos = np.asarray(nodes[end_idx], dtype=float)
        first = v53._append_node(nodes, parents, end_idx, pos + axis * 0.054)
        v53._append_node(nodes, parents, first, np.asarray(nodes[first], dtype=float) + axis * 0.030)
        terminal_fork_count += 1

    initial_terminals = list(v27._terminal_nodes(parents))
    for terminal in initial_terminals:
        parent_idx = int(parents[terminal]) if int(parents[terminal]) >= 0 else -1
        if parent_idx < 0:
            continue
        tip = np.asarray(nodes[terminal], dtype=float)
        axis = v22._unit(tip - np.asarray(nodes[parent_idx], dtype=float))
        if float(np.linalg.norm(axis)) < 1e-8:
            axis = v22._node_axis(nodes, parents, terminal)
        first = v53._append_node(nodes, parents, terminal, tip + axis * float(rng.uniform(0.040, 0.060)))
        second = v53._append_node(nodes, parents, first, np.asarray(nodes[first], dtype=float) + axis * float(rng.uniform(0.026, 0.042)))
        v53._append_node(nodes, parents, second, np.asarray(nodes[second], dtype=float) + axis * float(rng.uniform(0.017, 0.030)))
        graph_terminal_taper_count += 3

    primary_anchor_old = int(implicit_capsule_by_step.get(primary_step, main_indices[primary_step]))
    nodes, parents, old_to_new = v53._topological_reorder_nodes(nodes, parents)
    primary_anchor_new = int(old_to_new.get(primary_anchor_old, primary_anchor_old))
    primary_child_new = int(old_to_new.get(primary_child, primary_child)) if primary_child >= 0 else -1
    yfork_anchor_indices = [int(old_to_new.get(idx, idx)) for idx in yfork_anchor_indices]

    raw_nodes = list(nodes)
    nodes = v22._normalize_nodes(nodes, 2.06)
    raw_arr = np.asarray(raw_nodes, dtype=float)
    center = (raw_arr.min(axis=0) + raw_arr.max(axis=0)) * 0.5
    scale = 2.06 / max(float((raw_arr.max(axis=0) - raw_arr.min(axis=0)).max()), 1e-6)
    yfork_pairs = [
        [[float(x) for x in (np.asarray(point, dtype=float) - center) * scale] for point in pair]
        for pair in raw_yfork_pairs
    ]
    return nodes, parents, {
        "source": "custom_finite_lsystem_short_bough_with_shared_neck_yforks",
        "grammar_rule": "F -> compact_bough(F[short_side(F)])F with shared-neck Y-forks",
        "recursive_depth": int(side_depth + main_steps),
        "lsystem_branch_depth": int(side_depth),
        "main_branch_steps": int(main_steps),
        "side_branch_every": int(side_every),
        "double_sided_side_branches": bool(double_sides),
        "highres_smooth_yfork_anchor_index": int(primary_anchor_new),
        "highres_smooth_yfork_child_index": int(primary_child_new),
        "highres_smooth_yfork_anchor_indices": sorted(set(yfork_anchor_indices))[:16],
        "highres_smooth_yfork_branch_count": int(yfork_branch_count),
        "highres_smooth_yfork_zoom_pairs": yfork_pairs[:8],
        "implicit_capsule_inserted_count": int(len(implicit_capsule_by_step)),
        "implicit_capsule_topology": "compact bough main continuation and short side branches share explicit necks before turn-out",
        "pre_subdivision_junction_count": int(junction_count),
        "pre_subdivision_terminal_side_count": int(terminal_side_count),
        "saddle_neck_count": int(saddle_neck_count),
        "terminal_fork_count": int(terminal_fork_count),
        "graph_terminal_taper_count": int(graph_terminal_taper_count),
        "target_silhouette": "short thick mid-bough branch segment with few side branches and non-dominant tapered endpoints",
    }


def _branch_radii_v58(
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
        radius = float(base) * (float(taper) ** (depth * 0.50)) * (0.88 + 0.18 * math.sin(math.pi * min(max(t, 0.0), 1.0)))
        if depth == 0:
            radius *= 0.58
        elif depth == 1:
            radius *= 0.82
        if len(child_map.get(idx, [])) >= 2:
            radius *= 1.10
        if len(child_map.get(idx, [])) <= 1 and t > 0.42:
            radius *= 1.0 - (1.0 - float(high_depth_shrink)) * min((t - 0.42) / 0.58, 1.0)
        if idx in terminal_lineage and idx not in terminals:
            distance = terminal_lineage[idx]
            radius *= min(1.0, float(tip_parent_shrink) + 0.030 * distance)
        if idx in terminals:
            radius = max(float(floor) * 0.50, radius * float(terminal_shrink))
        else:
            radius = max(float(floor), radius)
        radii.append(float(radius))
    return radii


def _mutate_controls_for_v58(controls: Dict) -> None:
    controls["surface_strategy"] = SURFACE_STRATEGY
    controls["v53_lsystem_branch_natural_bough_graph_yfork_naturalization"] = False
    controls["v58_lsystem_branch_short_bough_yfork_naturalization"] = True
    controls["masked_local_naturalization_target"] = "L-system compact short-bough Y-fork bands with graph-native tapered endpoints"
    controls["mask_scope"] = "object_space_compact_short_bough_side_yfork_bands_only"
    controls["support_cross_section"] = "compact short-bough oval branch with shared-neck side branches"
    controls["target_silhouette"] = "short thick mid-bough branch segment with few recursive side branches"
    controls["hard_tube_cap_mitigation"] = "V58 changes the root silhouette to a compact mid-bough and keeps all endpoint repairs graph-native; no extra cap balls, terminal sleeves, or 2D seam backprojection"
    controls["v54_v57_failure_addressed"] = "V54-V57 had strong connectivity but pure-white zooms still read as long tube skeletons, crop cuts, or saddle bulges"
    controls["root_silhouette_change"] = "short_bough_root_rewrite_fewer_thicker_side_branches"
    controls["highres_smooth_yfork_zoom_target_policy"] = "explicit short-bough shared-neck Y-fork pair; endpoints excluded from primary zoom"
    controls["sdedit_seam_backprojection_available"] = False


def _build_case_v58(seed: int, **kwargs) -> Tuple[pb.Mesh, Dict, Dict]:
    mesh, controls, grammar = v53._build_lsystem_branch_case(seed, **kwargs)
    _mutate_controls_for_v58(controls)
    grammar["grammar_guide"] = "v58_lsystem_branch_short_bough_lowcontrast_bark_guide"
    grammar["root_silhouette_policy"] = "compact short-bough root, not V54-V57 long thin branch skeleton"
    return mesh, controls, grammar


def _spec_v58(
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
    _mutate_controls_for_v58(controls)
    spec = _ORIG_SPEC(
        case_id=case_id,
        mesh=mesh,
        controls=controls,
        grammar=grammar,
        guide_key=guide_key,
        gpu=gpu,
        seed=seed,
        root_variant=root_variant,
        parameter_variant=parameter_variant,
        reason=reason,
    )
    spec["recursive_mode"] = "finite L-system compact short-bough with recursive side branches and shared-neck Y-forks"
    spec["grammar_guide"] = "v58_lsystem_branch_short_bough_lowcontrast_bark_guide"
    spec["case_role"] = "v58_lsystem_branch_short_bough_yfork_naturalization"
    spec["qa_priority"] = "short_bough_naturalness_no_long_tube_skeleton_no_saddle_bulge_no_cut_endpoint_primary_read"
    spec["operators"] = list(spec["operators"]) + [
        "short_bough_root_silhouette_rewrite",
        "few_thick_side_branch_gate",
        "shared_neck_yfork_crop_avoidance",
    ]
    spec["operator_composition"] = " -> ".join(spec["operators"])
    _mutate_controls_for_v58(spec["controls"])
    return spec


def _case_specs_v58(seed: int) -> List[Dict]:
    settings = [
        ("V58_lsys_branch_short_bough_yfork_A", 4, 58001, 4, 1, 2, False, 0.34, 0.56, 0.76, 0.038, 0.835, 0.0062, 0.13, 0.31, 0.68, 0.062, 6, 1, 0, 0, 0, 0, 0, 0, 0.60, 0.50, "natural_bough", "short-bough A: compact branch segment with one side-Y on each mid-depth step"),
        ("V58_lsys_branch_short_bough_lowfrag_B", 5, 58002, 5, 1, 2, False, 0.28, 0.50, 0.70, 0.036, 0.848, 0.0060, 0.12, 0.29, 0.70, 0.064, 5, 1, 0, 0, 0, 0, 0, 0, 0.54, 0.46, "pale_cambium", "short-bough lowfrag B: safest compact silhouette with pale guide and fewer side branches"),
        ("V58_lsys_branch_short_bough_dense_C", 4, 58003, 4, 2, 2, True, 0.38, 0.60, 0.78, 0.040, 0.828, 0.0064, 0.14, 0.32, 0.66, 0.060, 7, 1, 0, 0, 0, 0, 0, 0, 0.64, 0.54, "warm_cedar", "short-bough dense C: stronger branch-with-side-branches read while keeping side branches thick"),
        ("V58_lsys_branch_short_bough_compact_D", 5, 58004, 5, 1, 3, False, 0.22, 0.48, 0.66, 0.035, 0.858, 0.0058, 0.11, 0.27, 0.72, 0.066, 5, 1, 0, 0, 0, 0, 0, 0, 0.50, 0.42, "pale_cambium", "short-bough compact D: topology-stable fallback with strongest crop avoidance"),
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
        mesh, controls, grammar = _build_case_v58(
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
            _spec_v58(
                case_id=case_id,
                mesh=mesh,
                controls=controls,
                grammar=grammar,
                guide_key=guide_key,
                gpu=gpu,
                seed=seed + offset,
                root_variant=case_id.replace("V58_", ""),
                parameter_variant=(
                    f"main{main_steps}_sideD{side_depth}_every{side_every}_shortbough"
                    f"_base{base_radius:.3f}_tip{terminal_shrink:.2f}_parent{tip_parent_shrink:.2f}"
                ),
                reason=reason,
            )
        )
    return rows


def _metadata_for_v58(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    metadata = _ORIG_METADATA_FOR(spec, mesh_path, guide_path, metrics)
    _mutate_controls_for_v58(metadata["controls"])
    metadata["root_selection_log"]["root_source_type"] = "V58_lsystem_branch_short_bough_yfork_naturalization_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V58_lsystem_branch_short_bough_yfork_20260511.py"
    metadata["case_role"] = "v58_lsystem_branch_short_bough_yfork_naturalization"
    old_contract = metadata.pop("v53_lsystem_branch_naturalization_contract", {})
    metadata["v58_lsystem_branch_naturalization_contract"] = {
        "target_failure": "V54-V57 passed connectivity gates but failed visual QA because the shared root silhouette stayed a long thin tube skeleton with crop-cut endpoints or saddle bulges.",
        "geometry_operator": "compact short-bough root rewrite plus V53 highres smooth Y-fork implicit field and graph-native terminal taper",
        "root_silhouette_change": "fewer, thicker side branches on a shorter bough segment; primary zoom excludes exposed endpoints",
        "carried_v53_evidence": {
            "implicit_capsule": old_contract.get("implicit_capsule", {}),
            "zoom_targets": old_contract.get("zoom_targets", {}),
            "seam_mask": old_contract.get("seam_mask", {}),
        },
        "sdedit_seam_backprojection_available": False,
        "texture_operator": "low-contrast whole-object guide for Trellis2 texturing; no 2D seam inpaint backprojection claim",
        "post_glb_acceptance": "paper candidate only if short-bough overview avoids tube-skeleton read and side-Y zoom reads as continuous wood, with preferred r0 LCR >=0.999 or r1 LCR=1.0.",
    }
    metadata["v58_remote_cache_policy"] = metadata.pop("v53_remote_cache_policy", {})
    return metadata


def _install_v58_overrides() -> None:
    v53._lsystem_branch_graph_v53 = _lsystem_branch_graph_v58
    v53._branch_radii_v53 = _branch_radii_v58
    v53._case_specs = _case_specs_v58
    v53._metadata_for = _metadata_for_v58
    v53.SURFACE_STRATEGY = SURFACE_STRATEGY
    v53.SELECTION_BUDGET = SELECTION_BUDGET


def _restore_v53_overrides() -> None:
    v53._lsystem_branch_graph_v53 = _ORIG_GRAPH
    v53._branch_radii_v53 = _ORIG_RADII
    v53._case_specs = _ORIG_CASE_SPECS
    v53._metadata_for = _ORIG_METADATA_FOR
    v53.SURFACE_STRATEGY = _ORIG_SURFACE_STRATEGY
    v53.SELECTION_BUDGET = _ORIG_SELECTION_BUDGET


def _rewrite_v58_outputs(out_dir: Path, summary: Dict) -> Dict:
    manifest_json = out_dir / "manifest.json"
    manifest_csv = out_dir / "manifest.csv"
    if manifest_json.exists():
        rows = json.loads(manifest_json.read_text(encoding="utf-8"))
        for row in rows:
            controls = json.loads(row["controls"])
            _mutate_controls_for_v58(controls)
            row["controls"] = json.dumps(controls, ensure_ascii=False, sort_keys=True)
            row["case_role"] = "v58_lsystem_branch_short_bough_yfork_naturalization"
            row["grammar_guide"] = "v58_lsystem_branch_short_bough_lowcontrast_bark_guide"
            row["selection_budget"] = SELECTION_BUDGET
            row["surface_strategy"] = SURFACE_STRATEGY
        manifest_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        if manifest_csv.exists() and rows:
            with manifest_csv.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

    old_zoom = out_dir / "V53_obj_zoom_manifest_junctiontarget_20260511.json"
    new_zoom = out_dir / "V58_obj_zoom_manifest_junctiontarget_20260511.json"
    if old_zoom.exists():
        data = json.loads(old_zoom.read_text(encoding="utf-8"))
        for item in data.get("cases", []):
            item["zoom_divisor"] = ZOOM_DIVISOR
            item["detail_target_source"] = "v58_lsystem_explicit_short_bough_yfork_mask"
        new_zoom.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        old_zoom.unlink()

    summary.update(
        {
            "out_dir": str(out_dir),
            "surface_generator": "strict_visual_matched_cases_V58_lsystem_branch_short_bough_yfork_naturalization",
            "surface_strategy": SURFACE_STRATEGY,
            "selection_budget": SELECTION_BUDGET,
            "obj_zoom_manifest": str(new_zoom),
            "do_not_launch_remote_before_local_visual_qa": True,
        }
    )
    summary["lsystem_branch_gate"]["mask_scope"] = "object_space_compact_short_bough_side_yfork_bands_only"
    summary["post_glb_target_floor"]["visual_gate"] = "short-bough overview must avoid tube-skeleton read; side-Y zoom must read as continuous wood without saddle bulge or cut endpoint dominance"
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V58 L-system Short-Bough Y-Fork Dry Run\n\n"
        "V58 records the V54-V57 visual failure and changes the root silhouette: compact mid-bough, fewer thicker side branches, shared-neck Y-forks, and graph-native tapered endpoints. "
        "It must pass local white-background OBJ zoom QA before any a100-2 textured GLB run. "
        "No 2D seam inpaint/backprojection claim is made.\n",
        encoding="utf-8",
    )
    return summary


def materialize(root: Path, out_dir: Path, seed: int = 20260511, case_limit: Optional[int] = None) -> Dict:
    _install_v58_overrides()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            summary = v53.materialize(root, out_dir, seed=seed, case_limit=case_limit)
        summary = _rewrite_v58_outputs(out_dir, summary)
    finally:
        _restore_v53_overrides()
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
