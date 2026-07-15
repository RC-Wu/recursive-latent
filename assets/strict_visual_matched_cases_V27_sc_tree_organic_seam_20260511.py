#!/usr/bin/env python3
"""V27 organic SC-tree seam refinement inputs.

V26 fixed the branch/crown seam at the mask level, but the white zoom QA still
showed hard support tubes and visible terminal caps.  V27 keeps the same strict
space-colonization target while changing only the grammar-owned local
realization: thinner tapered support, terminal bud caps, and feathered
junction twigs/leaves inside the branch/crown seam band.
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


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 200
CONNECTIVITY_LCR_MIN = 0.999
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V27_sc_tree_organic_seam_20260511_dryrun"

SURFACE_STRATEGY = "v27_sc_tree_terminal_bud_and_junction_feather_masked_naturalization"
GENERATION_POLICY = "generate_new_on_a100_2_no_local_selection_or_postprocessing"
SELECTION_BUDGET = "four_predeclared_sc_tree_organic_seam_candidates_one_per_gpu"
MESH_PBR_POLICY = "obj_inputs_organic_tree_guides_for_trellis2_glb_export_plus_object_space_pbr_qa"

DetailCounts = Dict[str, int]


def _blank_counts() -> DetailCounts:
    return {
        "needle_count": 0,
        "leaf_count": 0,
        "rootlet_count": 0,
        "tendril_count": 0,
        "bud_count": 0,
        "feather_count": 0,
    }


def _merge_counts(*parts: DetailCounts) -> DetailCounts:
    out = _blank_counts()
    for part in parts:
        for key, value in part.items():
            out[key] = int(out.get(key, 0)) + int(value)
    return out


def _children(parents: List[int]) -> Dict[int, List[int]]:
    child_map: Dict[int, List[int]] = {}
    for idx, parent in enumerate(parents):
        child_map.setdefault(int(parent), []).append(idx)
    return child_map


def _terminal_nodes(parents: List[int]) -> List[int]:
    child_map = _children(parents)
    return [idx for idx in range(1, len(parents)) if not child_map.get(idx)]


def _organic_radii(parents: List[int], base: float, taper: float, floor: float, terminal_shrink: float) -> List[float]:
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    terminals = set(_terminal_nodes(parents))
    radii: List[float] = []
    for idx, depth in enumerate(depths):
        t = depth / max(float(max_depth), 1.0)
        radius = max(float(floor), float(base) * (float(taper) ** depth))
        radius *= 1.0 - 0.18 * max(t - 0.35, 0.0)
        if idx in terminals:
            radius *= float(terminal_shrink)
        radii.append(float(max(radius, floor)))
    return radii


def _add_bud_cap(
    mesh: pb.Mesh,
    anchor_idx: int,
    anchor: np.ndarray,
    direction: np.ndarray,
    rng: np.random.Generator,
    *,
    length: float,
    radius: float,
    leaves: int,
) -> DetailCounts:
    counts = _blank_counts()
    direction = v22._unit(np.asarray(direction, dtype=float))
    u, v, _w = v22._basis(direction)
    v22._add_curved_tube_detail(
        mesh,
        anchor_idx,
        anchor,
        direction + rng.normal(0.0, 0.035, 3),
        float(length),
        float(radius),
        rng,
        segments=3,
        sides=6,
        curl=0.10,
    )
    counts["bud_count"] += 1
    for k in range(int(leaves)):
        lateral = math.cos(k * math.tau / max(leaves, 1)) * u + math.sin(k * math.tau / max(leaves, 1)) * v
        leaf_dir = v22._unit(0.46 * direction + 0.72 * lateral + np.array([0.0, 0.0, 0.12]))
        leaf_len = float(length) * float(rng.uniform(0.80, 1.35))
        v22._add_lanceolate_leaf(
            mesh,
            anchor_idx,
            anchor,
            leaf_dir,
            leaf_len,
            leaf_len * float(rng.uniform(0.23, 0.38)),
            rng,
            rows=5,
        )
        counts["leaf_count"] += 1
    return counts


def _add_terminal_bud_field(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    count: int,
    leaves_per_bud: int,
    radius_scale: float,
) -> Tuple[DetailCounts, Dict]:
    centers = getattr(mesh, "center_indices")
    terminals = _terminal_nodes(parents)
    depths = bm.graph_depths(parents)
    ordered = sorted(terminals, key=lambda idx: (depths[idx], idx), reverse=True)
    if not ordered:
        ordered = list(range(1, len(parents))) or [0]
    selected = [ordered[(i * 7) % len(ordered)] for i in range(int(count))]
    counts = _blank_counts()
    bud_centers: List[List[float]] = []
    for k, idx in enumerate(selected):
        axis = v22._node_axis(nodes, parents, idx)
        u, v, _w = v22._basis(axis)
        lateral = math.cos(k * 2.173) * u + math.sin(k * 2.173) * v
        direction = v22._unit(0.80 * axis + 0.22 * lateral + np.array([0.0, 0.0, 0.10]))
        local = _add_bud_cap(
            mesh,
            centers[idx],
            np.asarray(nodes[idx], dtype=float),
            direction,
            rng,
            length=float(rng.uniform(0.045, 0.088)),
            radius=float(rng.uniform(0.0042, 0.0074)) * float(radius_scale),
            leaves=leaves_per_bud,
        )
        counts = _merge_counts(counts, local)
        bud_centers.append([float(x) for x in np.asarray(nodes[idx], dtype=float)])
    return counts, {
        "terminal_bud_count": int(counts["bud_count"]),
        "terminal_bud_leaf_count": int(counts["leaf_count"]),
        "terminal_bud_centers": bud_centers[:80],
    }


def _add_junction_feathers(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    seam_count: int,
    twigs_per_seam: int,
    leaves_per_seam: int,
    twig_radius_scale: float,
    leaf_scale: float,
) -> Tuple[DetailCounts, Dict]:
    centers = getattr(mesh, "center_indices")
    child_map = _children(parents)
    anchors = v26._junction_anchor_indices(nodes, parents, seam_count)
    counts = _blank_counts()
    seam_centers: List[List[float]] = []
    for k, idx in enumerate(anchors):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx)
        u, v, _w = v22._basis(axis)
        child_dirs = [v22._unit(np.asarray(nodes[ch], dtype=float) - anchor) for ch in child_map.get(idx, [])[:3]]
        child_dir = child_dirs[k % len(child_dirs)] if child_dirs else axis
        seam_centers.append([float(x) for x in anchor])
        for t in range(int(twigs_per_seam)):
            phase = (k * 1.917 + t * 2.399) % math.tau
            lateral = math.cos(phase) * u + math.sin(phase) * v
            direction = v22._unit(0.52 * child_dir + 0.32 * axis + 0.42 * lateral + np.array([0.0, 0.0, 0.08]))
            v22._add_curved_tube_detail(
                mesh,
                centers[idx],
                anchor,
                direction,
                float(rng.uniform(0.070, 0.145)),
                float(rng.uniform(0.0024, 0.0051)) * float(twig_radius_scale),
                rng,
                segments=4,
                sides=6,
                curl=float(rng.uniform(0.16, 0.34)),
            )
            counts["feather_count"] += 1
            counts["tendril_count"] += 1
        for leaf_i in range(int(leaves_per_seam)):
            phase = (k * 2.071 + leaf_i * 2.021) % math.tau
            lateral = math.cos(phase) * u + math.sin(phase) * v
            direction = v22._unit(0.36 * axis + 0.72 * lateral + np.array([0.0, 0.0, 0.16]) + rng.normal(0.0, 0.045, 3))
            length = float(rng.uniform(0.052, 0.112)) * float(leaf_scale)
            v22._add_lanceolate_leaf(
                mesh,
                centers[idx],
                anchor,
                direction,
                length,
                length * float(rng.uniform(0.22, 0.42)),
                rng,
                rows=5,
            )
            counts["leaf_count"] += 1
    return counts, {
        "junction_anchor_count": int(len(set(anchors))),
        "junction_feather_count": int(counts["feather_count"]),
        "seam_mask_center_count": int(len(seam_centers)),
        "seam_mask_centers": seam_centers[:80],
        "seam_mask_radius": 0.105,
        "naturalization_style": "terminal_bud_and_junction_feather",
        "mask_scope": "branch_crown_junction_band_and_terminal_caps_only",
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
    seam_count: int,
    twigs_per_seam: int,
    leaves_per_seam: int,
    bud_count: int,
    bud_leaves: int,
    twig_radius_scale: float,
    leaf_scale: float,
) -> Tuple[pb.Mesh, Dict, Dict]:
    rng = np.random.default_rng(seed + 2701)
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
    radii = _organic_radii(parents, base=base_radius, taper=radius_taper, floor=radius_floor, terminal_shrink=terminal_shrink)
    edges = v22._graph_edges(parents)
    mesh = v22._smooth_support_mesh(nodes, edges, radii, sides=14, ovality=0.18)
    base_counts = _merge_counts(
        v22._scatter_needles(mesh, nodes, parents, rng, count=96, length_range=(0.036, 0.082)),
        v22._scatter_leaves(mesh, nodes, parents, rng, count=92, scale=(0.050, 0.115)),
    )
    feather_counts, feather_diag = _add_junction_feathers(
        mesh,
        nodes,
        parents,
        rng,
        seam_count=seam_count,
        twigs_per_seam=twigs_per_seam,
        leaves_per_seam=leaves_per_seam,
        twig_radius_scale=twig_radius_scale,
        leaf_scale=leaf_scale,
    )
    bud_counts, bud_diag = _add_terminal_bud_field(
        mesh,
        nodes,
        parents,
        rng,
        count=bud_count,
        leaves_per_bud=bud_leaves,
        radius_scale=twig_radius_scale,
    )
    counts = _merge_counts(base_counts, feather_counts, bud_counts)
    semantic_detail_count = int(sum(counts.values()))
    controls = v22._finalize_controls(
        {
            "source": "space_colonization_baseline.grow_space_colonization",
            "case": "tree_canopy",
            "semantic_mode": "tree",
            "recursive_depth": int(max(result.get("depths", [0])) if result.get("depths") else 0),
            "target_silhouette": "space-colonization tree crown with organic branch-crown seam and terminal bud naturalization",
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
            "v27_sc_tree_organic_seam": True,
            "masked_local_naturalization_target": "tree branch/crown junction band and terminal caps",
            "naturalization_not_global_resampling": True,
            "low_contrast_guide_required": True,
            "hard_tube_cap_mitigation": "terminal buds plus junction feather twigs/leaves",
            **feather_diag,
            **bud_diag,
            "grammar_rule": "space-colonization growth followed by masked junction-feather and terminal-bud local naturalization",
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
            "feather_count": int(counts["feather_count"]),
        }
    )
    grammar = {
        "grammar_family": "Space colonization",
        "grammar_symbols": "attractor_field,influence_radius,kill_radius,step_size,junction_mask,terminal_mask,junction_feather,terminal_bud",
        "target_symbol": "attractor",
        "operator_to_traditional_mapping": {
            "attractor_field": "keeps the same tree-crown target volume as the traditional SC baseline",
            "grow_tip": "advances support nodes by averaged attractor vectors",
            "terminal_mask": "selects exposed terminal caps that looked like cut tubes in V26 zooms",
            "junction_mask": "selects the branch/crown transition band after growth",
            "masked_local_naturalization": "adds conservative buds, twigs and leaves only inside terminal/junction masks",
        },
        "remote_comparison_unit": "one generated OBJ input to one traditional SC tree-crown target",
    }
    return mesh, controls, grammar


def _draw_organic_tree_guide(path: Path, *, variant: str) -> None:
    rng = np.random.default_rng(v26._stable_seed(path.stem))
    palettes = {
        "bark_leaf_gradient": [(66, 50, 30), (94, 70, 38), (70, 105, 48), (96, 132, 64), (130, 148, 82)],
        "olive_bud": [(58, 52, 32), (85, 78, 45), (64, 112, 54), (100, 142, 72), (142, 154, 91)],
        "moss_bark": [(52, 60, 36), (78, 70, 42), (58, 104, 50), (90, 126, 62), (126, 138, 75)],
        "soft_leaf_bark": [(72, 48, 30), (104, 76, 44), (74, 116, 55), (112, 146, 74), (150, 160, 94)],
    }
    colors = palettes[variant]
    img = Image.new("RGB", (768, 768), (50, 68, 40))
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(120):
        color = colors[int(rng.integers(0, len(colors)))]
        x = int(rng.integers(-150, 920))
        y = int(rng.integers(-150, 920))
        r = int(rng.integers(70, 210))
        alpha = int(rng.integers(54, 112))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, alpha))
    img = img.filter(ImageFilter.GaussianBlur(radius=22))
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(80):
        color = colors[int(rng.integers(0, 2))]
        x0 = int(rng.integers(-30, 800))
        y0 = int(rng.integers(-40, 790))
        pts = []
        phase = float(rng.uniform(0.0, math.tau))
        for t in range(7):
            pts.append((int(x0 + math.sin(t * 0.7 + phase) * rng.uniform(7, 24)), int(y0 + t * 115)))
        draw.line(pts, fill=(*color, int(rng.integers(82, 150))), width=int(rng.integers(2, 5)))
    for _ in range(160):
        color = colors[int(rng.integers(2, len(colors)))]
        x = int(rng.integers(0, 768))
        y = int(rng.integers(0, 768))
        rx = int(rng.integers(8, 26))
        ry = int(rng.integers(4, 16))
        angle = float(rng.uniform(0.0, math.tau))
        pts = []
        for a in np.linspace(0.0, math.tau, 10, endpoint=False):
            pts.append((x + int(math.cos(a) * rx * math.cos(angle) - math.sin(a) * ry * math.sin(angle)), y + int(math.cos(a) * rx * math.sin(angle) + math.sin(a) * ry * math.cos(angle))))
        draw.polygon(pts, fill=(*color, int(rng.integers(46, 96))))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.filter(ImageFilter.SMOOTH_MORE).save(path)


def _write_guides(out_dir: Path) -> Dict[str, str]:
    guide_dir = out_dir / "_guides"
    guides: Dict[str, str] = {}
    for key in ("bark_leaf_gradient", "olive_bud", "moss_bark", "soft_leaf_bark"):
        path = guide_dir / f"V27_sc_tree_{key}_organic_seam_guide.png"
        _draw_organic_tree_guide(path, variant=key)
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
        "terminal_bud_cap_mask",
        "junction_feather_twigs",
        "organic_tree_guide",
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
            "v27_sc_tree_organic_seam": True,
        }
    )
    return {
        "case_id": case_id,
        "family": "Space colonization",
        "match_target": "sc_tree_crown_260",
        "traditional_target": "sc_tree_crown_260",
        "recursive_mode": "tree-crown attractor competition with masked terminal-bud and junction-feather naturalization",
        "mesh": mesh,
        "controls": controls,
        "guide_key": guide_key,
        "root_variant": root_variant,
        "grammar_guide": "v27_space_colonization_organic_tree_seam_guide",
        "parameter_variant": parameter_variant,
        "gpu": int(gpu),
        "seed": int(seed),
        "operators": operators,
        "operator_composition": " -> ".join(operators),
        "grammar_mapping": v23._grammar_mapping("Space colonization", "sc_tree_crown_260", controls, grammar),
        "family_diagnostics": v23._family_diagnostics("Space colonization", "sc_tree_crown_260", controls),
        "why_matches_traditional": reason,
        "strict_match_notes": reason,
        "case_role": "v27_sc_tree_organic_seam_refinement",
        "qa_priority": "branch_crown_seam_and_terminal_cap_visual_quality",
        "rerun_reason": reason,
        "boundary_tag": "",
    }


def _case_specs(seed: int) -> List[Dict]:
    settings = [
        ("V27_sc_tree_organic_feather_A", 4, 27001, 860, 280, 0.205, 0.055, 0.033, 0.12, 0.22, 0.050, 0.78, 0.0036, 0.70, 30, 2, 2, 46, 2, 0.92, 1.00, "bark_leaf_gradient", "organic feather A: thinner support, terminal buds, two feather twigs per seam"),
        ("V27_sc_tree_terminal_bud_B", 5, 27002, 900, 272, 0.198, 0.058, 0.032, 0.10, 0.24, 0.046, 0.76, 0.0032, 0.64, 26, 2, 3, 64, 3, 0.86, 1.08, "olive_bud", "terminal bud B: strongest cap hiding with dense bud leaves and slim crown branches"),
        ("V27_sc_tree_bark_leaf_C", 6, 27003, 800, 288, 0.215, 0.052, 0.034, 0.15, 0.18, 0.052, 0.79, 0.0038, 0.72, 34, 3, 2, 48, 2, 0.96, 1.02, "moss_bark", "bark/leaf C: richer seam feathers while preserving post-GLB metric floor"),
        ("V27_sc_tree_soft_canopy_D", 7, 27004, 940, 270, 0.192, 0.060, 0.031, 0.09, 0.26, 0.044, 0.75, 0.0030, 0.60, 32, 2, 3, 70, 3, 0.82, 1.12, "soft_leaf_bark", "soft canopy D: densest fine twigs/leaves to reduce green pipe read in close zoom"),
    ]
    rows: List[Dict] = []
    for case_id, gpu, offset, attractors, iterations, influence, kill, step, z_gain, shrink, base_radius, taper, floor, terminal_shrink, seam_count, twigs_per_seam, leaves_per_seam, bud_count, bud_leaves, twig_radius_scale, leaf_scale, guide_key, reason in settings:
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
            seam_count=seam_count,
            twigs_per_seam=twigs_per_seam,
            leaves_per_seam=leaves_per_seam,
            bud_count=bud_count,
            bud_leaves=bud_leaves,
            twig_radius_scale=twig_radius_scale,
            leaf_scale=leaf_scale,
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
                root_variant=case_id.replace("V27_", ""),
                parameter_variant=(
                    f"a{attractors}_iter{iterations}_ri{influence:.3f}_rk{kill:.3f}_step{step:.3f}"
                    f"_base{base_radius:.3f}_bud{bud_count}_seam{seam_count}_twig{twigs_per_seam}"
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
    metadata["root_selection_log"]["root_source_type"] = "V27_sc_tree_organic_seam_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V27_sc_tree_organic_seam_20260511.py"
    metadata["v27_organic_seam_contract"] = {
        "target_failure": "V26 reduced seam masks but close zoom still showed hard tubes and cut terminal caps",
        "mask_scope": spec["controls"].get("mask_scope", "branch_crown_junction_band_and_terminal_caps_only"),
        "seam_mask_radius": spec["controls"].get("seam_mask_radius", 0.105),
        "seam_mask_center_count": spec["controls"].get("seam_mask_center_count", 0),
        "terminal_bud_count": spec["controls"].get("terminal_bud_count", 0),
        "junction_feather_count": spec["controls"].get("junction_feather_count", 0),
        "geometry_operator": "thin junction feather twigs/leaves plus terminal bud caps before Trellis2 export",
        "texture_operator": "organic bark/leaf guide; no full-width rings; no global image repaint claim",
        "claim_boundary": "local surface/material realization candidate, not global topology repair",
    }
    metadata["v27_remote_cache_policy"] = {
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
            raise RuntimeError(f"{spec['case_id']} failed V27 connectivity gate: {metrics}")
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
            "junction_feather_count": int(spec["controls"].get("junction_feather_count", 0)),
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
                "junction_feather_count": int(spec["controls"].get("junction_feather_count", 0)),
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
        "surface_generator": "strict_visual_matched_cases_V27_sc_tree_organic_seam",
        "mesh_input_policy": "obj_mesh_inputs_only",
        "mesh_pbr_policy": MESH_PBR_POLICY,
        "surface_strategy": SURFACE_STRATEGY,
        "connectivity_gate": {
            "largest_component_vertex_ratio_min": CONNECTIVITY_LCR_MIN,
            "pre_trellis_required": True,
            "boundary_tag_allowed": False,
        },
        "organic_seam_gate": {
            "mask_scope": "branch_crown_junction_band_and_terminal_caps_only",
            "min_seam_mask_centers": min(int(row["seam_mask_center_count"]) for row in rows) if rows else 0,
            "min_terminal_buds": min(int(row["terminal_bud_count"]) for row in rows) if rows else 0,
            "min_junction_feathers": min(int(row["junction_feather_count"]) for row in rows) if rows else 0,
            "organic_guides": True,
            "object_space_pbr_qa_recommended": True,
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
        "# V27 SC Tree Organic Seam Dry Run\n\n"
        "Predeclared branch/crown seam and terminal-cap naturalization candidates. "
        "This follows V26 and targets the remaining hard-tube visual failure in close zooms.\n",
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
