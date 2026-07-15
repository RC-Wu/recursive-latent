#!/usr/bin/env python3
"""V26 SC-tree seam naturalization input generator.

This is a small, predeclared follow-up to the V24/V25 space-colonization tree
crown cases.  The goal is not a broader baseline sweep.  It targets the visible
branch/crown junction failure with grammar-owned transition geometry, a
seam-band mask recorded in metadata, and low-contrast continuous guides before
remote Trellis2 texturing.
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


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 200
CONNECTIVITY_LCR_MIN = 0.999
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V26_sc_tree_seam_naturalization_20260511_dryrun"

SURFACE_STRATEGY = "v26_sc_tree_junction_collar_masked_local_naturalization"
GENERATION_POLICY = "generate_new_on_a100_2_no_local_selection_or_postprocessing"
SELECTION_BUDGET = "four_predeclared_sc_tree_seam_candidates_one_per_gpu"
MESH_PBR_POLICY = "obj_inputs_lowcontrast_guides_for_trellis2_glb_export_plus_object_space_pbr_qa"


DetailCounts = Dict[str, int]


def _stable_seed(text: str) -> int:
    value = 23
    for idx, ch in enumerate(text):
        value = (value * 181 + ord(ch) + idx * 17) % (2**32)
    return value


def _scale_nodes_for_crown(nodes: List[np.ndarray], z_gain: float, radial_shrink_top: float) -> List[np.ndarray]:
    arr = np.asarray(nodes, dtype=float)
    z_min = float(arr[:, 2].min())
    z_max = float(arr[:, 2].max())
    span = max(z_max - z_min, 1e-6)
    center_xy = arr[:, :2].mean(axis=0)
    out: List[np.ndarray] = []
    for node in arr:
        v = np.asarray(node, dtype=float).copy()
        t = (float(v[2]) - z_min) / span
        v[2] = z_min + (float(v[2]) - z_min) * (1.0 + float(z_gain) * t)
        shrink = 1.0 - float(radial_shrink_top) * max(t - 0.35, 0.0)
        v[:2] = center_xy + (v[:2] - center_xy) * max(shrink, 0.72)
        out.append(v)
    return out


def _blank_counts() -> DetailCounts:
    return {"needle_count": 0, "leaf_count": 0, "rootlet_count": 0, "tendril_count": 0}


def _merge_counts(*parts: DetailCounts) -> DetailCounts:
    out = _blank_counts()
    for part in parts:
        for key, value in part.items():
            out[key] = int(out.get(key, 0)) + int(value)
    return out


def _add_transition_lobe(
    mesh: pb.Mesh,
    anchor_idx: int,
    anchor: np.ndarray,
    direction: np.ndarray,
    length: float,
    radius: float,
    rng: np.random.Generator,
    *,
    rings: int = 5,
    sides: int = 10,
    curl: float = 0.10,
) -> np.ndarray:
    direction = v22._unit(np.asarray(direction, dtype=float))
    u, v, w = v22._basis(direction)
    phase = float(rng.uniform(0.0, math.tau))
    bend = v22._unit(math.cos(phase) * u + math.sin(phase) * v + 0.18 * w)
    ring_ids: List[List[int]] = []
    centers: List[np.ndarray] = []
    for ring_i in range(1, int(rings) + 1):
        t = ring_i / float(rings)
        center = (
            np.asarray(anchor, dtype=float)
            + direction * float(length) * t
            + bend * float(length) * float(curl) * math.sin(math.pi * t)
        )
        centers.append(center)
        ru, rv, _rw = v22._basis(direction + bend * 0.12)
        # Bulged at the root, then gently tapering.  This reads as a cambium
        # sleeve rather than a hard cap on the branch.
        profile = 0.34 + 0.82 * math.sin(math.pi * min(t, 0.92)) * (1.0 - 0.38 * t)
        ring: List[int] = []
        for side_i in range(sides):
            theta = math.tau * side_i / sides + phase * 0.11
            oval = 1.0 + 0.15 * math.sin(2.0 * theta + phase)
            pos = center + (math.cos(theta) * ru * oval + math.sin(theta) * rv * (2.0 - oval)) * float(radius) * profile
            mesh.vertices.append(tuple(pos))
            ring.append(len(mesh.vertices))
        ring_ids.append(ring)
    first = ring_ids[0]
    for side_i in range(sides):
        j = (side_i + 1) % sides
        mesh.faces.append((anchor_idx, first[side_i], first[j]))
    for a_ring, b_ring in zip(ring_ids[:-1], ring_ids[1:]):
        for side_i in range(sides):
            j = (side_i + 1) % sides
            mesh.faces.append((a_ring[side_i], a_ring[j], b_ring[side_i]))
            mesh.faces.append((a_ring[j], b_ring[j], b_ring[side_i]))
    tip_center = centers[-1] + direction * float(length) * 0.06
    mesh.vertices.append(tuple(tip_center))
    tip = len(mesh.vertices)
    last = ring_ids[-1]
    for side_i in range(sides):
        j = (side_i + 1) % sides
        mesh.faces.append((last[side_i], tip, last[j]))
    return np.mean(np.asarray(centers, dtype=float), axis=0)


def _junction_anchor_indices(nodes: List[np.ndarray], parents: List[int], count: int) -> List[int]:
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    child_map = v22._children(parents)
    scored: List[Tuple[float, int]] = []
    for idx in range(1, len(parents)):
        t = depths[idx] / max(float(max_depth), 1.0)
        if t < 0.18 or t > 0.68:
            continue
        degree = len(child_map.get(idx, []))
        if degree == 0 and t < 0.45:
            continue
        # Prefer the mid-crown branch/trunk junctions that caused the visual
        # seam, but still sample some terminal transition anchors.
        score = degree * 2.0 + (1.0 - abs(t - 0.42)) + 0.001 * idx
        scored.append((score, idx))
    if not scored:
        return v22._repeat_anchor_indices(parents, count=count, prefer_terminal=False, min_depth_fraction=0.25)
    ordered = [idx for _score, idx in sorted(scored, reverse=True)]
    return [ordered[(i * 5) % len(ordered)] for i in range(int(count))]


def _add_junction_naturalization(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    style: str,
    collar_count: int,
    leaf_count: int,
) -> Tuple[DetailCounts, Dict]:
    centers = getattr(mesh, "center_indices")
    anchors = _junction_anchor_indices(nodes, parents, collar_count)
    seam_centers: List[List[float]] = []
    counts = _blank_counts()
    child_map = v22._children(parents)
    for k, idx in enumerate(anchors):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx)
        u, v, _w = v22._basis(axis)
        lateral = math.cos(k * 2.117) * u + math.sin(k * 2.117) * v
        child_dirs = []
        for child in child_map.get(idx, [])[:3]:
            child_dirs.append(v22._unit(np.asarray(nodes[child], dtype=float) - anchor))
        child_dir = child_dirs[k % len(child_dirs)] if child_dirs else axis
        direction = v22._unit(0.48 * axis + 0.38 * child_dir + 0.28 * lateral + np.array([0.0, 0.0, 0.10]))
        if style == "leafshield":
            radius = float(rng.uniform(0.020, 0.030))
            length = float(rng.uniform(0.125, 0.215))
            curl = 0.16
        elif style == "cambium":
            radius = float(rng.uniform(0.024, 0.036))
            length = float(rng.uniform(0.105, 0.180))
            curl = 0.10
        else:
            radius = float(rng.uniform(0.018, 0.028))
            length = float(rng.uniform(0.140, 0.245))
            curl = 0.08
        center = _add_transition_lobe(mesh, centers[idx], anchor, direction, length, radius, rng, rings=5, sides=10, curl=curl)
        seam_centers.append([float(x) for x in center])
        counts["tendril_count"] += 1
        if k % 2 == 0:
            v22._add_curved_tube_detail(
                mesh,
                centers[idx],
                anchor,
                v22._unit(0.50 * direction + 0.46 * lateral + rng.normal(0.0, 0.035, 3)),
                float(rng.uniform(0.080, 0.145)),
                float(rng.uniform(0.0045, 0.0080)),
                rng,
                segments=4,
                sides=7,
                curl=0.24,
            )
            counts["needle_count"] += 1
    leaf_anchors = _junction_anchor_indices(nodes, parents, leaf_count)
    for k, idx in enumerate(leaf_anchors):
        axis = v22._node_axis(nodes, parents, idx)
        u, v, _w = v22._basis(axis)
        lateral = math.cos(k * 2.399) * u + math.sin(k * 2.399) * v
        direction = v22._unit(0.28 * axis + 0.78 * lateral + np.array([0.0, 0.0, 0.18]) + rng.normal(0.0, 0.05, 3))
        length = float(rng.uniform(0.065, 0.128)) if style == "leafshield" else float(rng.uniform(0.045, 0.092))
        width = length * float(rng.uniform(0.22, 0.39))
        v22._add_lanceolate_leaf(mesh, centers[idx], nodes[idx], direction, length, width, rng, rows=6)
        counts["leaf_count"] += 1
    diagnostics = {
        "junction_anchor_count": int(len(set(anchors))),
        "junction_collar_count": int(collar_count),
        "junction_leafshield_count": int(leaf_count),
        "seam_mask_center_count": int(len(seam_centers)),
        "seam_mask_centers": seam_centers[:64],
        "seam_mask_radius": 0.145 if style == "leafshield" else 0.125,
        "naturalization_style": style,
        "mask_scope": "branch_crown_junction_band_only",
    }
    return counts, diagnostics


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
    style: str,
    collar_count: int,
    leaf_count: int,
    base_radius: float,
) -> Tuple[pb.Mesh, Dict, Dict]:
    rng = np.random.default_rng(seed + 2601)
    result = scb.grow_space_colonization(
        case="tree_canopy",
        attractor_count=attractors,
        iterations=iterations,
        influence_radius=influence,
        kill_radius=kill,
        step_size=step,
        seed=seed,
    )
    nodes = v22._normalize_nodes([np.asarray(p, dtype=float) for p in result["nodes"]], 2.60)
    nodes = _scale_nodes_for_crown(nodes, z_gain=z_gain, radial_shrink_top=shrink)
    parents = [int(p) for p in result["parents"]]
    radii = v22._radii_from_parents(parents, base=base_radius, taper=0.86, floor=0.0048)
    edges = v22._graph_edges(parents)
    mesh = v22._smooth_support_mesh(nodes, edges, radii, sides=16, ovality=0.12)
    base_counts = _merge_counts(
        v22._scatter_needles(mesh, nodes, parents, rng, count=118, length_range=(0.044, 0.096)),
        v22._scatter_leaves(mesh, nodes, parents, rng, count=68, scale=(0.048, 0.102)),
    )
    seam_counts, seam_diag = _add_junction_naturalization(
        mesh,
        nodes,
        parents,
        rng,
        style=style,
        collar_count=collar_count,
        leaf_count=leaf_count,
    )
    counts = _merge_counts(base_counts, seam_counts)
    controls = v22._finalize_controls(
        {
            "source": "space_colonization_baseline.grow_space_colonization",
            "case": "tree_canopy",
            "semantic_mode": "tree",
            "recursive_depth": int(max(result.get("depths", [0])) if result.get("depths") else 0),
            "target_silhouette": "space-colonization tree crown with branch-crown seam naturalization",
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
            "v26_sc_tree_seam_naturalization": True,
            "masked_local_naturalization_target": "tree branch/crown junction band",
            "naturalization_not_global_resampling": True,
            "low_contrast_guide_required": True,
            **seam_diag,
            "grammar_rule": "space-colonization growth followed by masked junction-collar local naturalization at branch/crown seams",
        },
        nodes,
        edges,
        counts,
    )
    controls["surface_strategy"] = SURFACE_STRATEGY
    grammar = {
        "grammar_family": "Space colonization",
        "grammar_symbols": "attractor_field,influence_radius,kill_radius,step_size,junction_mask,junction_collar,leafshield",
        "target_symbol": "attractor",
        "operator_to_traditional_mapping": {
            "attractor_field": "keeps the same tree-crown target volume as the traditional SC baseline",
            "grow_tip": "advances support nodes by averaged attractor vectors",
            "junction_mask": "selects the branch/crown transition band after growth",
            "masked_local_naturalization": "adds conservative collar and leafshield geometry only in the seam band",
        },
        "remote_comparison_unit": "one generated OBJ input to one traditional SC tree-crown target",
    }
    return mesh, controls, grammar


def _draw_lowcontrast_sc_tree_guide(path: Path, *, variant: str) -> None:
    rng = np.random.default_rng(_stable_seed(path.stem))
    palettes = {
        "bark_leaf": {
            "bg": (43, 67, 36),
            "colors": [(60, 88, 43), (74, 103, 50), (92, 112, 58), (86, 70, 40), (112, 88, 49)],
        },
        "moss_cambium": {
            "bg": (46, 72, 40),
            "colors": [(62, 93, 48), (88, 118, 61), (105, 123, 68), (98, 86, 50), (124, 103, 61)],
        },
        "matte_greenwood": {
            "bg": (50, 78, 42),
            "colors": [(70, 102, 52), (94, 126, 67), (118, 132, 74), (92, 82, 48), (130, 110, 67)],
        },
        "soft_canopy": {
            "bg": (48, 76, 41),
            "colors": [(66, 98, 50), (90, 121, 65), (111, 132, 75), (84, 75, 46), (122, 105, 65)],
        },
    }
    palette = palettes[variant]
    img = Image.new("RGB", (768, 768), palette["bg"])
    draw = ImageDraw.Draw(img, "RGBA")
    colors = palette["colors"]
    for _ in range(100):
        color = colors[int(rng.integers(0, len(colors)))]
        x = int(rng.integers(-180, 920))
        y = int(rng.integers(-180, 920))
        r = int(rng.integers(90, 235))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, int(rng.integers(70, 120))))
    img = img.filter(ImageFilter.GaussianBlur(radius=24))
    draw = ImageDraw.Draw(img, "RGBA")
    # Fine, mostly longitudinal fibers.  Full-width rings were the visible
    # failure mode in the seam-aware v1 run.
    for _ in range(180):
        color = colors[int(rng.integers(0, len(colors)))]
        x0 = int(rng.integers(-70, 838))
        y0 = int(rng.integers(-60, 808))
        pts = []
        phase = float(rng.uniform(0.0, math.tau))
        for t in range(8):
            y = y0 + t * 112
            x = x0 + math.sin(t * 0.72 + phase) * float(rng.uniform(9, 28)) + t * float(rng.normal(0.0, 5.0))
            pts.append((int(x), int(y)))
        draw.line(pts, fill=(*color, int(rng.integers(72, 145))), width=int(rng.integers(2, 6)))
    for _ in range(180):
        color = colors[int(rng.integers(0, 3))]
        x = int(rng.integers(-20, 788))
        y = int(rng.integers(-20, 788))
        rx = int(rng.integers(5, 18))
        ry = int(rng.integers(3, 12))
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(*color, int(rng.integers(48, 92))))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.filter(ImageFilter.SMOOTH_MORE).save(path)


def _write_guides(out_dir: Path) -> Dict[str, str]:
    guide_dir = out_dir / "_guides"
    guides: Dict[str, str] = {}
    for key in ("bark_leaf", "moss_cambium", "matte_greenwood", "soft_canopy"):
        path = guide_dir / f"V26_sc_tree_{key}_lowcontrast_seam_guide.png"
        _draw_lowcontrast_sc_tree_guide(path, variant=key)
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
        "masked_junction_collar",
        "seam_band_lowcontrast_material_guide",
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
            "v26_sc_tree_seam_naturalization": True,
        }
    )
    return {
        "case_id": case_id,
        "family": "Space colonization",
        "match_target": "sc_tree_crown_260",
        "traditional_target": "sc_tree_crown_260",
        "recursive_mode": "tree-crown attractor competition with masked branch/crown junction naturalization",
        "mesh": mesh,
        "controls": controls,
        "guide_key": guide_key,
        "root_variant": root_variant,
        "grammar_guide": "v26_space_colonization_seam_band_lowcontrast_guide",
        "parameter_variant": parameter_variant,
        "gpu": int(gpu),
        "seed": int(seed),
        "operators": operators,
        "operator_composition": " -> ".join(operators),
        "grammar_mapping": v23._grammar_mapping("Space colonization", "sc_tree_crown_260", controls, grammar),
        "family_diagnostics": v23._family_diagnostics("Space colonization", "sc_tree_crown_260", controls),
        "why_matches_traditional": reason,
        "strict_match_notes": reason,
        "case_role": "v26_sc_tree_seam_naturalization",
        "qa_priority": "branch_crown_seam_visual_quality",
        "rerun_reason": reason,
        "boundary_tag": "",
    }


def _case_specs(seed: int) -> List[Dict]:
    settings = [
        (
            "V26_sc_tree_crown_junction_collar_A_lowcontrast",
            4,
            26001,
            820,
            276,
            0.212,
            0.052,
            0.035,
            0.13,
            0.18,
            "cambium",
            28,
            42,
            0.064,
            "bark_leaf",
            "junction collar A with low-contrast bark/leaf transition guide",
        ),
        (
            "V26_sc_tree_crown_leafshield_B_lowcontrast",
            5,
            26002,
            880,
            272,
            0.205,
            0.055,
            0.034,
            0.12,
            0.21,
            "leafshield",
            24,
            68,
            0.060,
            "moss_cambium",
            "leaf-shield B covers visible branch/crown caps while preserving SC attractor crown",
        ),
        (
            "V26_sc_tree_crown_cambium_sleeve_C_lowcontrast",
            6,
            26003,
            760,
            284,
            0.222,
            0.050,
            0.036,
            0.16,
            0.16,
            "cambium",
            34,
            36,
            0.068,
            "matte_greenwood",
            "cambium sleeve C thickens only the junction band to remove hard tube seams",
        ),
        (
            "V26_sc_tree_crown_soft_canopy_D_lowcontrast",
            7,
            26004,
            920,
            268,
            0.198,
            0.058,
            0.033,
            0.10,
            0.23,
            "soft",
            30,
            56,
            0.058,
            "soft_canopy",
            "soft canopy D reduces trunk/crown contrast and adds transition lobes in the seam mask",
        ),
    ]
    rows: List[Dict] = []
    for case_id, gpu, offset, attractors, iterations, influence, kill, step, z_gain, shrink, style, collar_count, leaf_count, base_radius, guide_key, reason in settings:
        mesh, controls, grammar = _build_sc_tree_case(
            seed + offset,
            attractors=attractors,
            iterations=iterations,
            influence=influence,
            kill=kill,
            step=step,
            z_gain=z_gain,
            shrink=shrink,
            style=style,
            collar_count=collar_count,
            leaf_count=leaf_count,
            base_radius=base_radius,
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
                root_variant=case_id.replace("V26_", ""),
                parameter_variant=f"a{attractors}_iter{iterations}_ri{influence:.3f}_rk{kill:.3f}_step{step:.3f}_{style}_collar{collar_count}_leaf{leaf_count}",
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
    metadata["root_selection_log"]["root_source_type"] = "V26_sc_tree_seam_naturalization_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V26_sc_tree_seam_naturalization_20260511.py"
    metadata["v26_seam_naturalization_contract"] = {
        "target_failure": "visible branch/crown seam in V24/V25 SC tree zoom",
        "mask_scope": spec["controls"].get("mask_scope", "branch_crown_junction_band_only"),
        "seam_mask_radius": spec["controls"].get("seam_mask_radius", 0.125),
        "seam_mask_center_count": spec["controls"].get("seam_mask_center_count", 0),
        "geometry_operator": "junction collar / leafshield before Trellis2 export",
        "texture_operator": "low-contrast continuous guide; no full-width dark rings",
        "claim_boundary": "geometry and material seam QA candidate, not proof that Trellis UV export always removes seams",
    }
    metadata["v26_remote_cache_policy"] = {
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
            raise RuntimeError(f"{spec['case_id']} failed V26 connectivity gate: {metrics}")
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
            "junction_collar_count": int(spec["controls"].get("junction_collar_count", 0)),
            "junction_leafshield_count": int(spec["controls"].get("junction_leafshield_count", 0)),
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
                "junction_collar_count": int(spec["controls"].get("junction_collar_count", 0)),
                "junction_leafshield_count": int(spec["controls"].get("junction_leafshield_count", 0)),
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
        "surface_generator": "strict_visual_matched_cases_V26_sc_tree_seam_naturalization",
        "mesh_input_policy": "obj_mesh_inputs_only",
        "mesh_pbr_policy": MESH_PBR_POLICY,
        "surface_strategy": SURFACE_STRATEGY,
        "connectivity_gate": {
            "largest_component_vertex_ratio_min": CONNECTIVITY_LCR_MIN,
            "pre_trellis_required": True,
            "boundary_tag_allowed": False,
        },
        "seam_naturalization_gate": {
            "mask_scope": "branch_crown_junction_band_only",
            "min_seam_mask_centers": min(int(row["seam_mask_center_count"]) for row in rows) if rows else 0,
            "low_contrast_guides": True,
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
        "# V26 SC Tree Seam Naturalization Dry Run\n\n"
        "Predeclared branch/crown seam naturalization candidates for the V24/V25 "
        "space-colonization tree-crown visual weak point.  Generate only; remote "
        "Trellis2 launch is separate.\n",
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
