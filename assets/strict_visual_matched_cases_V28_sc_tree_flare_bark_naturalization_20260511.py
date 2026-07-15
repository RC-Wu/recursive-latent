#!/usr/bin/env python3
"""V28 SC-tree branch/crown seam refinement inputs.

V27 made the seam target explicit, but post-GLB QA showed two remaining
failure modes: the main support still read as a smooth inserted rod, and many
fine leaves/twigs became tiny disconnected fragments after Trellis export.
V28 keeps the same strict `sc_tree_crown_260` target and changes only the
grammar-owned local realization: compact junction flares, bark ridges, thicker
secondary splits, and fewer leaf/bud details.
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
import space_colonization_baseline as scb
import strict_visual_matched_cases_V22_botanical_smooth_20260510 as v22
import strict_visual_matched_cases_V23_all_family_20260510 as v23
import strict_visual_matched_cases_V26_sc_tree_seam_naturalization_20260511 as v26
import strict_visual_matched_cases_V27_sc_tree_organic_seam_20260511 as v27


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 200
CONNECTIVITY_LCR_MIN = 0.999
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V28_sc_tree_flare_bark_naturalization_20260511_dryrun"

SURFACE_STRATEGY = "v28_sc_tree_compact_flare_bark_ridge_masked_naturalization"
GENERATION_POLICY = "generate_new_on_a100_2_no_local_selection_or_postprocessing"
SELECTION_BUDGET = "four_predeclared_sc_tree_flare_bark_candidates_one_per_gpu"
MESH_PBR_POLICY = "obj_inputs_compact_flare_tree_guides_for_trellis2_glb_export_plus_object_space_pbr_qa"


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
    }


def _merge_counts(*parts: DetailCounts) -> DetailCounts:
    out = _blank_counts()
    for part in parts:
        for key, value in part.items():
            out[key] = int(out.get(key, 0)) + int(value)
    return out


def _node_depths(parents: List[int]) -> List[int]:
    return bm.graph_depths(parents)


def _junction_anchor_indices(nodes: List[np.ndarray], parents: List[int], count: int) -> List[int]:
    depths = _node_depths(parents)
    max_depth = max(depths) if depths else 1
    child_map = v22._children(parents)
    scored: List[Tuple[float, int]] = []
    for idx in range(1, len(parents)):
        t = depths[idx] / max(float(max_depth), 1.0)
        degree = len(child_map.get(idx, []))
        if t < 0.16 or t > 0.70:
            continue
        if degree == 0 and t < 0.50:
            continue
        radial = float(np.linalg.norm(np.asarray(nodes[idx], dtype=float)[:2]))
        score = 2.4 * degree + 1.2 * (1.0 - abs(t - 0.42)) + 0.25 * radial + 0.001 * idx
        scored.append((score, idx))
    if not scored:
        return v22._repeat_anchor_indices(parents, count=count, prefer_terminal=False, min_depth_fraction=0.25)
    ordered = [idx for _score, idx in sorted(scored, reverse=True)]
    return [ordered[(i * 5) % len(ordered)] for i in range(int(count))]


def _terminal_anchor_indices(parents: List[int], count: int) -> List[int]:
    depths = _node_depths(parents)
    terminals = v27._terminal_nodes(parents)
    if not terminals:
        return v22._repeat_anchor_indices(parents, count=count, prefer_terminal=True)
    ordered = sorted(terminals, key=lambda idx: (depths[idx], idx), reverse=True)
    return [ordered[(i * 7) % len(ordered)] for i in range(int(count))]


def _organic_radii(parents: List[int], *, base: float, taper: float, floor: float, terminal_shrink: float) -> List[float]:
    depths = _node_depths(parents)
    max_depth = max(depths) if depths else 1
    terminals = set(v27._terminal_nodes(parents))
    radii: List[float] = []
    for idx, depth in enumerate(depths):
        t = depth / max(float(max_depth), 1.0)
        radius = max(float(floor), float(base) * (float(taper) ** (depth * 0.82)))
        radius *= 1.0 - 0.22 * max(t - 0.30, 0.0)
        if idx in terminals:
            radius *= float(terminal_shrink)
        radii.append(float(max(radius, floor)))
    return radii


def _add_flare_sleeves(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    count: int,
    radius_scale: float,
    length_scale: float,
) -> Tuple[DetailCounts, Dict]:
    centers = getattr(mesh, "center_indices")
    child_map = v22._children(parents)
    anchors = _junction_anchor_indices(nodes, parents, count)
    counts = _blank_counts()
    seam_centers: List[List[float]] = []
    for k, idx in enumerate(anchors):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx)
        u, v, _w = v22._basis(axis)
        child_dirs = [v22._unit(np.asarray(nodes[ch], dtype=float) - anchor) for ch in child_map.get(idx, [])[:4]]
        child_dir = child_dirs[k % len(child_dirs)] if child_dirs else axis
        lateral = math.cos(k * 2.113) * u + math.sin(k * 2.113) * v
        direction = v22._unit(0.46 * axis + 0.44 * child_dir + 0.22 * lateral + np.array([0.0, 0.0, 0.06]))
        center = v26._add_transition_lobe(
            mesh,
            centers[idx],
            anchor,
            direction,
            float(rng.uniform(0.105, 0.185)) * float(length_scale),
            float(rng.uniform(0.014, 0.026)) * float(radius_scale),
            rng,
            rings=5,
            sides=12,
            curl=float(rng.uniform(0.05, 0.13)),
        )
        seam_centers.append([float(x) for x in center])
        counts["flare_count"] += 1
        counts["tendril_count"] += 1
    return counts, {
        "junction_anchor_count": int(len(set(anchors))),
        "junction_flare_count": int(counts["flare_count"]),
        "seam_mask_center_count": int(len(seam_centers)),
        "seam_mask_centers": seam_centers[:80],
        "seam_mask_radius": 0.132,
    }


def _add_bark_ridges(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    count: int,
    radius_scale: float,
) -> DetailCounts:
    centers = getattr(mesh, "center_indices")
    anchors = _junction_anchor_indices(nodes, parents, count)
    counts = _blank_counts()
    for k, idx in enumerate(anchors):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx)
        u, v, _w = v22._basis(axis)
        lateral = math.cos(k * 1.731) * u + math.sin(k * 1.731) * v
        direction = v22._unit(0.78 * axis + 0.26 * lateral + rng.normal(0.0, 0.025, 3))
        v22._add_curved_tube_detail(
            mesh,
            centers[idx],
            anchor,
            direction,
            float(rng.uniform(0.095, 0.185)),
            float(rng.uniform(0.0048, 0.0084)) * float(radius_scale),
            rng,
            segments=4,
            sides=7,
            curl=float(rng.uniform(0.04, 0.11)),
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
        u, v, _w = v22._basis(axis)
        child_dirs = [v22._unit(np.asarray(nodes[ch], dtype=float) - anchor) for ch in child_map.get(idx, [])[:3]]
        child_dir = child_dirs[k % len(child_dirs)] if child_dirs else axis
        lateral = math.cos(k * 2.377) * u + math.sin(k * 2.377) * v
        direction = v22._unit(0.58 * child_dir + 0.22 * axis + 0.36 * lateral + np.array([0.0, 0.0, 0.07]))
        v22._add_curved_tube_detail(
            mesh,
            centers[idx],
            anchor,
            direction,
            float(rng.uniform(0.085, 0.155)),
            float(rng.uniform(0.0046, 0.0080)) * float(radius_scale),
            rng,
            segments=4,
            sides=7,
            curl=float(rng.uniform(0.12, 0.25)),
        )
        counts["split_count"] += 1
        counts["tendril_count"] += 1
    return counts


def _add_compact_terminal_buds(
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
        direction = v22._unit(0.84 * axis + 0.18 * lateral + np.array([0.0, 0.0, 0.06]) + rng.normal(0.0, 0.025, 3))
        v26._add_transition_lobe(
            mesh,
            centers[idx],
            anchor,
            direction,
            float(rng.uniform(0.046, 0.078)),
            float(rng.uniform(0.0085, 0.0145)) * float(radius_scale),
            rng,
            rings=4,
            sides=9,
            curl=float(rng.uniform(0.05, 0.12)),
        )
        counts["bud_count"] += 1
        counts["tendril_count"] += 1
        bud_centers.append([float(x) for x in anchor])
        for b in range(int(bracts_per_bud)):
            phase = k * 1.881 + b * math.tau / max(bracts_per_bud, 1)
            side = math.cos(phase) * u + math.sin(phase) * v
            leaf_dir = v22._unit(0.45 * direction + 0.64 * side + np.array([0.0, 0.0, 0.10]))
            length = float(rng.uniform(0.034, 0.064))
            v22._add_lanceolate_leaf(
                mesh,
                centers[idx],
                anchor,
                leaf_dir,
                length,
                length * float(rng.uniform(0.20, 0.31)),
                rng,
                rows=4,
            )
            counts["leaf_count"] += 1
    return counts, {
        "terminal_bud_count": int(counts["bud_count"]),
        "terminal_bud_leaf_count": int(counts["leaf_count"]),
        "terminal_bud_centers": bud_centers[:80],
    }


def _build_sc_tree_case(
    seed: int,
    *,
    attractors: int,
    iterations: int,
    influence: float,
    kill: float,
    step: float,
    z_gain: float,
    shrink: float,
    base_radius: float,
    radius_taper: float,
    radius_floor: float,
    terminal_shrink: float,
    flare_count: int,
    ridge_count: int,
    split_count: int,
    bud_count: int,
    bracts_per_bud: int,
    scatter_leaf_count: int,
    scatter_needle_count: int,
    detail_radius_scale: float,
    flare_length_scale: float,
) -> Tuple[pb.Mesh, Dict, Dict]:
    rng = np.random.default_rng(seed + 2801)
    result = scb.grow_space_colonization(
        case="tree_canopy",
        attractor_count=attractors,
        iterations=iterations,
        influence_radius=influence,
        kill_radius=kill,
        step_size=step,
        seed=seed,
    )
    nodes = v22._normalize_nodes([np.asarray(p, dtype=float) for p in result["nodes"]], 2.62)
    nodes = v26._scale_nodes_for_crown(nodes, z_gain=z_gain, radial_shrink_top=shrink)
    parents = [int(p) for p in result["parents"]]
    radii = _organic_radii(
        parents,
        base=base_radius,
        taper=radius_taper,
        floor=radius_floor,
        terminal_shrink=terminal_shrink,
    )
    edges = v22._graph_edges(parents)
    mesh = v22._smooth_support_mesh(nodes, edges, radii, sides=15, ovality=0.34)
    base_counts = _merge_counts(
        v22._scatter_needles(mesh, nodes, parents, rng, count=scatter_needle_count, length_range=(0.036, 0.074)),
        v22._scatter_leaves(mesh, nodes, parents, rng, count=scatter_leaf_count, scale=(0.044, 0.088)),
    )
    flare_counts, flare_diag = _add_flare_sleeves(
        mesh,
        nodes,
        parents,
        rng,
        count=flare_count,
        radius_scale=detail_radius_scale,
        length_scale=flare_length_scale,
    )
    ridge_counts = _add_bark_ridges(mesh, nodes, parents, rng, count=ridge_count, radius_scale=detail_radius_scale)
    split_counts = _add_structural_splits(mesh, nodes, parents, rng, count=split_count, radius_scale=detail_radius_scale)
    bud_counts, bud_diag = _add_compact_terminal_buds(
        mesh,
        nodes,
        parents,
        rng,
        count=bud_count,
        bracts_per_bud=bracts_per_bud,
        radius_scale=detail_radius_scale,
    )
    counts = _merge_counts(base_counts, flare_counts, ridge_counts, split_counts, bud_counts)
    semantic_detail_count = int(
        counts["needle_count"]
        + counts["leaf_count"]
        + counts["bud_count"]
        + counts["flare_count"]
        + counts["ridge_count"]
        + counts["split_count"]
    )
    controls = v22._finalize_controls(
        {
            "source": "space_colonization_baseline.grow_space_colonization",
            "case": "tree_canopy",
            "semantic_mode": "tree",
            "recursive_depth": int(max(result.get("depths", [0])) if result.get("depths") else 0),
            "target_silhouette": "space-colonization tree crown with compact branch flare and bark-ridge seam naturalization",
            "attractor_count": int(attractors),
            "iterations": int(iterations),
            "influence_radius": float(influence),
            "kill_radius": float(kill),
            "step_size": float(step),
            "covered_attractors": int(result.get("covered_attractors", 0)),
            "alive_attractors": int(result.get("alive_attractors", 0)),
            "z_gain": float(z_gain),
            "radial_shrink_top": float(shrink),
            "support_base_radius": float(base_radius),
            "support_radius_taper": float(radius_taper),
            "support_radius_floor": float(radius_floor),
            "terminal_radius_shrink": float(terminal_shrink),
            "support_cross_section": "oval_nonround_bark_read",
            "v28_sc_tree_flare_bark_naturalization": True,
            "masked_local_naturalization_target": "tree branch/crown junction band and terminal caps",
            "naturalization_not_global_resampling": True,
            "low_contrast_guide_required": True,
            "hard_tube_cap_mitigation": "compact flare sleeves, bark ridges, structural splits, and connected terminal buds",
            **flare_diag,
            **bud_diag,
            "grammar_rule": "space-colonization growth followed by compact masked junction flares, bark ridges, and terminal buds",
        },
        nodes,
        edges,
        {
            "needle_count": int(counts["needle_count"]),
            "leaf_count": int(counts["leaf_count"]),
            "rootlet_count": 0,
            "tendril_count": int(counts["tendril_count"]),
        },
    )
    controls.update(
        {
            "surface_strategy": SURFACE_STRATEGY,
            "semantic_detail_count": semantic_detail_count,
            "bud_count": int(counts["bud_count"]),
            "flare_count": int(counts["flare_count"]),
            "ridge_count": int(counts["ridge_count"]),
            "structural_split_count": int(counts["split_count"]),
            "v27_failure_addressed": "reduce smooth inserted rod read while avoiding V27 tiny leaf/twig post-GLB fragments",
        }
    )
    grammar = {
        "grammar_family": "Space colonization",
        "grammar_symbols": "attractor_field,influence_radius,kill_radius,step_size,junction_mask,flare_sleeve,bark_ridge,terminal_bud",
        "target_symbol": "attractor",
        "operator_to_traditional_mapping": {
            "attractor_field": "keeps the same tree-crown target volume as the traditional SC baseline",
            "grow_tip": "advances support nodes by averaged attractor vectors",
            "junction_mask": "selects the branch/crown transition band after growth",
            "flare_sleeve": "locally thickens branching bases to avoid hard insertion seams",
            "bark_ridge": "adds connected non-round surface relief instead of global repainting",
            "terminal_bud": "turns exposed caps into compact connected buds rather than many detached leaves",
        },
        "remote_comparison_unit": "one generated OBJ input to one traditional SC tree-crown target",
    }
    return mesh, controls, grammar


def _draw_flare_tree_guide(path: Path, *, variant: str) -> None:
    rng = np.random.default_rng(v26._stable_seed(path.stem))
    palettes = {
        "flare_bark": [(56, 42, 26), (88, 60, 34), (116, 86, 48), (58, 94, 42), (92, 126, 60)],
        "bark_ridge": [(48, 38, 26), (80, 58, 38), (128, 92, 54), (64, 96, 44), (98, 132, 66)],
        "split_canopy": [(58, 46, 28), (100, 72, 42), (76, 116, 52), (108, 146, 72), (144, 152, 84)],
        "hybrid_bud": [(54, 44, 30), (92, 66, 42), (70, 112, 52), (118, 146, 76), (154, 162, 94)],
    }
    colors = palettes[variant]
    img = Image.new("RGB", (768, 768), (46, 62, 38))
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(96):
        color = colors[int(rng.integers(0, len(colors)))]
        x = int(rng.integers(-140, 900))
        y = int(rng.integers(-140, 900))
        r = int(rng.integers(80, 230))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, int(rng.integers(54, 105))))
    img = img.filter(ImageFilter.GaussianBlur(radius=21))
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(105):
        color = colors[int(rng.integers(0, 3))]
        x0 = int(rng.integers(-40, 800))
        y0 = int(rng.integers(-60, 790))
        pts = []
        phase = float(rng.uniform(0.0, math.tau))
        for t in range(7):
            pts.append((int(x0 + math.sin(t * 0.8 + phase) * rng.uniform(8, 22)), int(y0 + t * 116)))
        draw.line(pts, fill=(*color, int(rng.integers(92, 156))), width=int(rng.integers(2, 5)))
    for _ in range(90):
        color = colors[int(rng.integers(3, len(colors)))]
        x = int(rng.integers(0, 768))
        y = int(rng.integers(0, 768))
        rx = int(rng.integers(7, 22))
        ry = int(rng.integers(4, 13))
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(*color, int(rng.integers(38, 78))))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.filter(ImageFilter.SMOOTH_MORE).save(path)


def _write_guides(out_dir: Path) -> Dict[str, str]:
    guide_dir = out_dir / "_guides"
    guides: Dict[str, str] = {}
    for key in ("flare_bark", "bark_ridge", "split_canopy", "hybrid_bud"):
        path = guide_dir / f"V28_sc_tree_{key}_compact_flare_guide.png"
        _draw_flare_tree_guide(path, variant=key)
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
    operators = list(v23.OPERATORS_BY_FAMILY["Space colonization"]) + [
        "compact_junction_flare_mask",
        "connected_bark_ridges",
        "structural_canopy_splits",
        "compact_terminal_buds",
        "low_fragment_tree_guide",
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
            "v28_sc_tree_flare_bark_naturalization": True,
        }
    )
    return {
        "case_id": case_id,
        "family": "Space colonization",
        "match_target": "sc_tree_crown_260",
        "traditional_target": "sc_tree_crown_260",
        "recursive_mode": "tree-crown attractor competition with compact flare, bark-ridge, and terminal-bud masked naturalization",
        "mesh": mesh,
        "controls": controls,
        "guide_key": guide_key,
        "root_variant": root_variant,
        "grammar_guide": "v28_space_colonization_compact_flare_bark_tree_guide",
        "parameter_variant": parameter_variant,
        "gpu": int(gpu),
        "seed": int(seed),
        "operators": operators,
        "operator_composition": " -> ".join(operators),
        "grammar_mapping": v23._grammar_mapping("Space colonization", "sc_tree_crown_260", controls, grammar),
        "family_diagnostics": v23._family_diagnostics("Space colonization", "sc_tree_crown_260", controls),
        "why_matches_traditional": reason,
        "strict_match_notes": reason,
        "case_role": "v28_sc_tree_flare_bark_naturalization",
        "qa_priority": "branch_crown_seam_rod_read_and_post_glb_fragment_floor",
        "rerun_reason": reason,
        "boundary_tag": "",
    }


def _case_specs(seed: int) -> List[Dict]:
    settings = [
        ("V28_sc_tree_branch_flare_A", 4, 28001, 800, 292, 0.210, 0.054, 0.031, 0.13, 0.20, 0.043, 0.82, 0.0045, 0.72, 34, 24, 18, 28, 1, 40, 36, 0.98, 1.06, "flare_bark", "branch flare A: compact flares break the hard rod/crown insertion with fewer tiny details than V27"),
        ("V28_sc_tree_bark_ridge_B", 5, 28002, 780, 300, 0.216, 0.052, 0.030, 0.15, 0.17, 0.040, 0.83, 0.0044, 0.74, 28, 42, 14, 24, 1, 34, 30, 1.04, 0.96, "bark_ridge", "bark ridge B: emphasizes non-round bark relief on the support while keeping leaf count low for post-GLB stability"),
        ("V28_sc_tree_multiscale_canopy_C", 6, 28003, 900, 288, 0.198, 0.058, 0.029, 0.10, 0.25, 0.038, 0.81, 0.0042, 0.68, 28, 20, 24, 24, 1, 36, 34, 0.92, 1.00, "split_canopy", "multiscale canopy C: uses thicker structural splits and compact buds to hide terminal cuts without V27's leaf fragment load"),
        ("V28_sc_tree_hybrid_flare_bud_D", 7, 28004, 860, 296, 0.204, 0.056, 0.030, 0.12, 0.22, 0.041, 0.82, 0.0043, 0.70, 30, 24, 20, 26, 1, 38, 34, 0.96, 1.02, "hybrid_bud", "hybrid flare-bud D: balances flares, bark ridges, and compact buds for final visual selection"),
    ]
    rows: List[Dict] = []
    for case_id, gpu, offset, attractors, iterations, influence, kill, step, z_gain, shrink, base_radius, taper, floor, terminal_shrink, flare_count, ridge_count, split_count, bud_count, bracts_per_bud, scatter_leaf_count, scatter_needle_count, detail_radius_scale, flare_length_scale, guide_key, reason in settings:
        mesh, controls, grammar = _build_sc_tree_case(
            seed + offset,
            attractors=attractors,
            iterations=iterations,
            influence=influence,
            kill=kill,
            step=step,
            z_gain=z_gain,
            shrink=shrink,
            base_radius=base_radius,
            radius_taper=taper,
            radius_floor=floor,
            terminal_shrink=terminal_shrink,
            flare_count=flare_count,
            ridge_count=ridge_count,
            split_count=split_count,
            bud_count=bud_count,
            bracts_per_bud=bracts_per_bud,
            scatter_leaf_count=scatter_leaf_count,
            scatter_needle_count=scatter_needle_count,
            detail_radius_scale=detail_radius_scale,
            flare_length_scale=flare_length_scale,
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
                root_variant=case_id.replace("V28_", ""),
                parameter_variant=(
                    f"a{attractors}_iter{iterations}_ri{influence:.3f}_rk{kill:.3f}_step{step:.3f}"
                    f"_base{base_radius:.3f}_flare{flare_count}_ridge{ridge_count}_split{split_count}_bud{bud_count}"
                ),
                reason=reason,
            )
        )
    return rows


def _metadata_for(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    metadata = v23._metadata_for(spec, mesh_path, guide_path, metrics)
    metadata["strict_generation_policy"] = GENERATION_POLICY
    metadata["selection_budget"] = SELECTION_BUDGET
    metadata["case_role"] = spec["case_role"]
    metadata["rerun_reason"] = spec["rerun_reason"]
    metadata["qa_priority"] = spec["qa_priority"]
    metadata["root_selection_log"]["root_source_type"] = "V28_sc_tree_flare_bark_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V28_sc_tree_flare_bark_naturalization_20260511.py"
    metadata["v28_flare_bark_contract"] = {
        "target_failure": "V27 GLB still reads as a smooth rod through the crown and adds post-GLB tiny fragments",
        "mask_scope": spec["controls"].get("mask_scope", "branch_crown_junction_band_and_terminal_caps_only"),
        "seam_mask_radius": spec["controls"].get("seam_mask_radius", 0.132),
        "seam_mask_center_count": spec["controls"].get("seam_mask_center_count", 0),
        "terminal_bud_count": spec["controls"].get("terminal_bud_count", 0),
        "junction_flare_count": spec["controls"].get("junction_flare_count", 0),
        "ridge_count": spec["controls"].get("ridge_count", 0),
        "structural_split_count": spec["controls"].get("structural_split_count", 0),
        "geometry_operator": "compact flares + connected bark ridges + thicker structural splits + terminal buds",
        "texture_operator": "low-fragment bark/leaf guide; no seam-only 2D SDEdit claim",
        "claim_boundary": "local surface/material realization candidate, not global topology repair",
    }
    metadata["v28_remote_cache_policy"] = {
        "cache_root": REMOTE_STORAGE_ROOT + "/cache",
        "no_system_tmp": True,
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
            raise RuntimeError(f"{spec['case_id']} failed V28 connectivity gate: {metrics}")
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
            "seam_mask_center_count": int(spec["controls"].get("seam_mask_center_count", 0)),
            "terminal_bud_count": int(spec["controls"].get("terminal_bud_count", 0)),
            "junction_flare_count": int(spec["controls"].get("junction_flare_count", 0)),
            "ridge_count": int(spec["controls"].get("ridge_count", 0)),
            "structural_split_count": int(spec["controls"].get("structural_split_count", 0)),
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
                "seam_mask_center_count": int(spec["controls"].get("seam_mask_center_count", 0)),
                "terminal_bud_count": int(spec["controls"].get("terminal_bud_count", 0)),
                "junction_flare_count": int(spec["controls"].get("junction_flare_count", 0)),
                "ridge_count": int(spec["controls"].get("ridge_count", 0)),
                "structural_split_count": int(spec["controls"].get("structural_split_count", 0)),
            }
        )

    manifest_fields = list(rows[0].keys()) if rows else []
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    metric_fields = list(metrics_rows[0].keys()) if metrics_rows else []
    with (out_dir / "initial_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        writer.writerows(metrics_rows)
    (out_dir / "initial_metrics.json").write_text(json.dumps(metrics_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    case_lines = [f"{row['case_id']}|{row['mesh_path']}|{row['guide_image']}|{row['seed']}|{row['gpu_group']}" for row in rows]
    (out_dir / "a100-2_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    (out_dir / "gpu4567_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
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
        "storage_root": REMOTE_STORAGE_ROOT,
        "storage_limit_gb": STORAGE_LIMIT_GB,
        "surface_generator": "strict_visual_matched_cases_V28_sc_tree_flare_bark_naturalization",
        "mesh_input_policy": "obj_mesh_inputs_only",
        "mesh_pbr_policy": MESH_PBR_POLICY,
        "surface_strategy": SURFACE_STRATEGY,
        "connectivity_gate": {
            "largest_component_vertex_ratio_min": CONNECTIVITY_LCR_MIN,
            "pre_trellis_required": True,
            "boundary_tag_allowed": False,
        },
        "flare_bark_gate": {
            "mask_scope": "branch_crown_junction_band_and_terminal_caps_only",
            "min_seam_mask_centers": min(int(row["seam_mask_center_count"]) for row in rows) if rows else 0,
            "min_terminal_buds": min(int(row["terminal_bud_count"]) for row in rows) if rows else 0,
            "min_junction_flares": min(int(row["junction_flare_count"]) for row in rows) if rows else 0,
            "min_bark_ridges": min(int(row["ridge_count"]) for row in rows) if rows else 0,
            "compact_guides": True,
            "object_space_pbr_qa_recommended": True,
        },
        "post_glb_target_floor": {
            "preferred_r0_lcr_min": 0.999,
            "fallback_r1_lcr_min": 1.0,
            "reason": "V27 B/C/D fragmented at r0 after GLB; V28 must recover V26-like connectivity while improving seam visual quality.",
        },
        "storage_risk": {
            "expected_upper_bound_gb": 24,
            "risk_level": "low",
            "notes": "4 Trellis2 mesh/PBR exports; cache must remain inside project root.",
        },
        "gpu_case_counts": gpu_case_counts,
        "priority_cases": [row["case_id"] for row in rows],
        "manifest": str(out_dir / "manifest.csv"),
        "initial_metrics": str(out_dir / "initial_metrics.csv"),
        "do_not_launch_remote": True,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V28 SC Tree Flare/Bark Naturalization Dry Run\n\n"
        "Predeclared compact branch/crown seam candidates. V28 directly addresses "
        "the V27 hard-rod read and post-GLB tiny-fragment failure by using fewer, "
        "thicker connected local details.\n",
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
