#!/usr/bin/env python3
"""V36 L-system branch woody-junction naturalization inputs.

V35 improved post-GLB connectivity, but the first pure-white zoom QA still read
as a large cut branch tube with small side geometry attached near it. V36 keeps
the same strict branch-with-side-branches target and changes the local
realization toward a woodier continuous fork:

* thinner and more curved high-depth support with stronger terminal taper,
* broad cambium collars at actual side-branch junctions,
* fewer free leaves/bracts so the geometry reads as fused wood rather than
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
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V36_lsystem_branch_woody_junction_naturalization_20260511_dryrun"

SURFACE_STRATEGY = "v36_lsystem_branch_woody_junction_sidebranch_naturalization"
GENERATION_POLICY = "generate_new_on_a100_2_no_local_selection_or_postprocessing"
SELECTION_BUDGET = "four_v36_lsystem_branch_candidates_local_qa_then_two_gpu_remote"
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


def _branch_radii_v36(
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
    terminal_lineage = _terminal_lineage(parents, hops=3)
    radii: List[float] = []
    for idx, depth in enumerate(depths):
        t = depth / max(float(max_depth), 1.0)
        radius = float(base) * (float(taper) ** (depth * 0.66))
        if len(child_map.get(idx, [])) >= 2:
            radius *= 1.04
        if len(child_map.get(idx, [])) <= 1 and t > 0.50:
            # Shrink single-child upper branch runs so the side view stops
            # reading as a rectangular pipe.
            radius *= 1.0 - (1.0 - float(high_depth_shrink)) * min((t - 0.50) / 0.50, 1.0)
        if idx in terminal_lineage and idx not in terminals:
            distance = terminal_lineage[idx]
            radius *= min(1.0, float(tip_parent_shrink) + 0.16 * distance)
        if idx in terminals:
            radius *= float(terminal_shrink)
        radius = max(float(floor) * 0.55, radius)
        radii.append(float(radius))
    return radii


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
            float(rng.uniform(0.052, 0.090)),
            float(rng.uniform(0.010, 0.017)) * float(radius_scale),
            rng,
            rings=5,
            sides=10,
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
    lo = float(np.quantile(z, 0.18))
    hi = float(np.quantile(z, 0.72))
    center = arr.mean(axis=0)
    candidates: List[Tuple[float, List[float]]] = []
    for point in arr:
        if not (lo <= float(point[2]) <= hi):
            continue
        radial = float(np.linalg.norm(point[:2] - center[:2]))
        mid_bonus = -abs(float(point[2]) - float(np.median(z)))
        score = 1.3 * radial + 0.4 * mid_bonus
        candidates.append((score, [float(x) for x in point]))
    if not candidates:
        candidates = [(0.0, [float(x) for x in point]) for point in arr]
    return [point for _score, point in sorted(candidates, reverse=True)[:limit]]


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
    rng = np.random.default_rng(seed + 3502)
    nodes, parents, lsys_diag = v34._lsystem_branch_graph(
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
    radii = _branch_radii_v36(
        parents,
        base=base_radius,
        taper=radius_taper,
        floor=radius_floor,
        terminal_shrink=terminal_shrink,
        tip_parent_shrink=tip_parent_shrink,
        high_depth_shrink=high_depth_shrink,
    )
    edges = v22._graph_edges(parents)
    mesh = v22._smooth_support_mesh(nodes, edges, radii, sides=15, ovality=0.34)
    collar_counts, collar_diag = v34._add_junction_collars(
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
        scale=(0.024, 0.052),
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
            "support_visibility_policy": "main support remains visible but side-branch junctions are fused with broad cambium collars",
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
            "v36_lsystem_branch_woody_junction_naturalization": True,
            "v35_failure_addressed": "pure-white zoom still read as a large cut branch tube with side detail attached near it",
            "masked_local_naturalization_target": "L-system side-branch junction bands plus low-leaf terminal sleeves",
            "mask_scope": "object_space_side_branch_junction_bands_and_terminal_caps_only",
            "seam_mask_space": "object_xyz",
            "seam_mask_selection_rule": "degree>=2 L-system junction nodes plus terminal sleeve anchors; no global resampling; zoom targets filtered to mid-depth junctions",
            "seam_mask_center_count": int(len(seam_centers)),
            "seam_mask_centers": seam_centers[:96],
            "junction_zoom_target_count": int(len(junction_zoom_centers)),
            "junction_zoom_targets": junction_zoom_centers[:48],
            "seam_mask_radius": float(collar_diag.get("seam_mask_radius", 0.118)),
            "branch_junction_count": int(branch_junction_count),
            "terminal_count": int(terminal_count),
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
            "hard_tube_cap_mitigation": "thin high-depth support, stronger parent-of-terminal taper, low-leaf terminal sleeves, bark ridges, and broad junction collars",
        }
    )
    grammar = {
        "grammar_family": "L-system",
        "grammar_symbols": "F,+,-,[,],side_branch,junction_mask,cambium_collar,bark_ridge,terminal_sleeve,terminal_cap",
        "target_symbol": "F",
        "operator_to_traditional_mapping": {
            "F": "advance a finite turtle branch segment and create connected swept support",
            "+/-": "yaw side branches from the main branch frame",
            "[]": "push/pop recursive side-branch state",
            "side_branch": "instantiate the same branch-with-side-branches target used by the traditional L-system baseline",
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
        path = guide_dir / f"V36_lsystem_branch_{key}_lowcontrast_guide.png"
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
            "v36_lsystem_branch_woody_junction_naturalization": True,
        }
    )
    return {
        "case_id": case_id,
        "family": "L-system",
        "match_target": "lsys_branch_side_d5",
        "traditional_target": "lsys_branch_side_d5",
        "recursive_mode": "finite L-system branch with recursive side branches and woody fused junctions",
        "mesh": mesh,
        "controls": controls,
        "guide_key": guide_key,
        "root_variant": root_variant,
        "grammar_guide": "v36_lsystem_branch_lowcontrast_bark_cambium_guide",
        "parameter_variant": parameter_variant,
        "gpu": int(gpu),
        "seed": int(seed),
        "operators": operators,
        "operator_composition": " -> ".join(operators),
        "grammar_mapping": v23._grammar_mapping("L-system", "lsys_branch_side_d5", controls, grammar),
        "family_diagnostics": v23._family_diagnostics("L-system", "lsys_branch_side_d5", controls),
        "why_matches_traditional": reason,
        "strict_match_notes": reason,
        "case_role": "v36_lsystem_branch_woody_junction_naturalization",
        "qa_priority": "woody_side_branch_junction_naturalness_terminal_taper_and_non_seam_read",
        "rerun_reason": reason,
        "boundary_tag": "",
    }


def _case_specs(seed: int) -> List[Dict]:
    settings = [
        ("V36_lsys_branch_woody_junction_A", 4, 36001, 9, 3, 2, True, 0.24, 0.72, 0.70, 0.042, 0.812, 0.0028, 0.17, 0.34, 0.48, 0.088, 34, 62, 18, 8, 20, 0, 0, 2, 1.28, 1.26, "cambium", "woody junction A: broad cambium collars, minimal bracts, and stronger tip taper for branch-on-branch continuity"),
        ("V36_lsys_branch_woody_sleeve_B", 5, 36002, 10, 2, 2, False, 0.20, 0.64, 0.64, 0.040, 0.820, 0.0028, 0.16, 0.32, 0.46, 0.086, 30, 72, 14, 6, 24, 0, 0, 0, 1.20, 1.16, "ridge", "woody sleeve B: low-fragment wood-only backup with ridges and terminal sleeves instead of leaf clutter"),
        ("V36_lsys_branch_fused_fork_C", 4, 36003, 8, 3, 2, True, 0.27, 0.78, 0.74, 0.038, 0.805, 0.0026, 0.18, 0.34, 0.50, 0.088, 36, 56, 20, 6, 18, 0, 0, 4, 1.34, 1.30, "olive", "fused fork C: strongest side-branch hierarchy with large collars and a small tapered main tip"),
        ("V36_lsys_branch_lowfrag_taper_D", 5, 36004, 9, 2, 3, False, 0.16, 0.60, 0.58, 0.036, 0.828, 0.0028, 0.15, 0.30, 0.44, 0.084, 24, 52, 10, 4, 18, 0, 0, 0, 1.12, 1.06, "cedar", "lowfrag taper D: conservative wood-only candidate with the best chance of post-GLB r0 stability"),
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
                root_variant=case_id.replace("V36_", ""),
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
    metadata["root_selection_log"]["root_source_type"] = "V36_lsystem_branch_woody_junction_naturalization_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V36_lsystem_branch_woody_junction_naturalization_20260511.py"
    metadata["v36_lsystem_branch_naturalization_contract"] = {
        "target_failure": "V35 remained connected but still read as a cut branch tube with small side geometry attached in pure-white zoom QA",
        "geometry_operator": "strong tip-parent taper, low-leaf terminal sleeves, short segmented swept support, broad object-space junction collars, bark ridges, and branch splits",
        "seam_mask": {
            "space": "object_xyz",
            "scope": controls.get("mask_scope"),
            "selection_rule": controls.get("seam_mask_selection_rule"),
            "radius": controls.get("seam_mask_radius"),
            "center_count": controls.get("seam_mask_center_count"),
            "centers": controls.get("seam_mask_centers", [])[:96],
        },
        "zoom_targets": {
            "source": "junction-only object-space collar centers, excluding terminal buds/sleeves",
            "count": controls.get("junction_zoom_target_count"),
            "centers": controls.get("junction_zoom_targets", [])[:48],
        },
        "naturalization_regions": ["side_branch_junction_band", "terminal_sleeves", "bark_ridge_relief"],
        "sdedit_seam_backprojection_available": False,
        "texture_operator": "low-contrast whole-object guide for Trellis2 texturing; no 2D seam inpaint backprojection claim",
        "material_transition_policy": controls.get("material_transition_policy"),
        "claim_boundary": controls.get("claim_boundary"),
        "post_glb_acceptance": "paper candidate only if side-branch junction zoom no longer reads as a hard inserted tube, terminal endpoint is not a blunt pipe, and r1 LCR remains 1.0; preferred r0 LCR >=0.999",
    }
    metadata["v36_remote_cache_policy"] = {
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
            raise RuntimeError(f"{spec['case_id']} failed V36 connectivity gate: {metrics}")
        if float(spec["controls"].get("external_support_max_segment_after_subdivision", 999.0)) > EXTERNAL_SUPPORT_MAX_SEGMENT_GATE + 1e-6:
            raise RuntimeError(f"{spec['case_id']} failed V36 short-segment gate: {spec['controls']}")
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
                "detail_target_source": "v36_lsystem_object_space_junction_mask",
            }
        )
    (out_dir / "V36_obj_zoom_manifest_junctiontarget_20260511.json").write_text(
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
        "surface_generator": "strict_visual_matched_cases_V36_lsystem_branch_woody_junction_naturalization",
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
            "visual_gate": "side-branch junction zoom must not read as hard inserted tubes; terminal caps must be closed by sleeves/buds",
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
        "obj_zoom_manifest": str(out_dir / "V36_obj_zoom_manifest_junctiontarget_20260511.json"),
        "do_not_launch_remote_before_local_visual_qa": True,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V36 L-system Branch Tapered Naturalization Dry Run\n\n"
        "V36 repairs the V35 visual failure mode: connected metrics but pure-white zoom still read as a tube with attached side detail. "
        "It uses stronger high-depth support taper, broad junction collars, low-leaf terminal sleeves, mid-depth junction-only zoom targets, "
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
