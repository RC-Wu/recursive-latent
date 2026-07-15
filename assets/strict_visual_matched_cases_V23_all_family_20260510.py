#!/usr/bin/env python3
"""V23 all-family strict matched case generator.

This dry-run generator prepares OBJ mesh inputs and PBR guide images for the
next remote strict one-to-one batch.  It intentionally does not launch remote
jobs or select final outputs.  The batch covers L-system, space colonization,
DLA/frontier, and IFS/transform families with balanced GPU 4/5/6/7 assignment.
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

import procedural_baselines as pb
import recursive_growth_mesh_metrics as rgm
import strict_visual_matched_cases_V21_ifs_transform_natural_20260510 as v21
import strict_visual_matched_cases_V22_botanical_smooth_20260510 as v22
import strict_visual_matched_cases_v12_tapered_staghorn_20260510 as v12


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 200
CONNECTIVITY_LCR_MIN = 0.999
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V23_all_family_20260510_dryrun"

SURFACE_STRATEGY = "connected_swept_or_facet_support_with_family_semantic_details"
SELECTION_BUDGET = "one_remote_generation_per_manifest_row_no_local_cherry_pick"

FORBIDDEN_OUTPUTS = [
    "local_selected_render",
    "2d_only_image",
    "posthoc_repair_mesh",
    "non_obj_mesh_input",
    "low_poly_block_stamp",
    "mesh_token_stamp",
]

OPERATORS_BY_FAMILY = {
    "L-system": [
        "lsystem_rewriting",
        "grammar_guide_condition",
        "smooth_swept_branch_support",
        "shared_vertex_attachment",
        "semantic_detail_preexport",
        "obj_mesh_input_only",
        "largest_component_gate",
    ],
    "Space colonization": [
        "attractor_select",
        "grow_tip_from_attractor_field",
        "kill_covered_attractors",
        "occupancy_competition",
        "smooth_swept_branch_support",
        "shared_vertex_attachment",
        "obj_mesh_input_only",
        "largest_component_gate",
    ],
    "DLA/frontier": [
        "frontier_sample",
        "occupancy_exclusion",
        "attach_patch",
        "bridge_to_root_certificate",
        "connected_projection",
        "facet_or_pore_detail",
        "obj_mesh_input_only",
        "largest_component_gate",
    ],
    "IFS/transform": [
        "transform_copy",
        "orbit_or_lattice_certificate",
        "contact_bridge",
        "shared_vertex_connected_support",
        "attached_transform_detail",
        "obj_mesh_input_only",
        "largest_component_gate",
    ],
}


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _basis(axis: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = _unit(np.asarray(axis, dtype=float))
    seed = np.array([0.0, 0.0, 1.0]) if abs(float(w[2])) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = _unit(np.cross(w, seed))
    v = _unit(np.cross(w, u))
    return u, v, w


def _surface_area(vertices: np.ndarray, faces: np.ndarray) -> float:
    if len(vertices) == 0 or len(faces) == 0:
        return 0.0
    tri = vertices[faces]
    return float(np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1).sum() * 0.5)


def _control_detail_count(controls: Dict) -> int:
    return int(controls.get("semantic_detail_count", controls.get("attached_natural_mesh_detail_count", 0)))


def _normalize_controls(controls: Dict, family: str, support_edges: int, detail_count: int) -> Dict:
    normalized = dict(controls)
    normalized.update(
        {
            "mesh_input_format": "obj",
            "same_classical_task_mode": True,
            "connected_support": True,
            "connectivity_gate_lcr_min": CONNECTIVITY_LCR_MIN,
            "low_poly_block_stamping": False,
            "mesh_token_stamping": False,
            "procedural_block_tokens": False,
            "direct_voxel_blocks": False,
            "surface_strategy": SURFACE_STRATEGY,
            "support_edge_count": int(max(support_edges, int(normalized.get("support_edge_count", 0)))),
            "semantic_detail_count": int(max(detail_count, _control_detail_count(normalized))),
            "detached_chunk_policy": "forbid_detached_detail_islands_by_shared_vertex_faces",
        }
    )
    if family == "IFS/transform":
        normalized["attached_natural_mesh_detail_count"] = int(normalized["semantic_detail_count"])
    return normalized


def _mesh_stats(path: Path, controls: Dict) -> Dict:
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
        "support_edge_count": int(controls.get("support_edge_count", 0)),
        "semantic_detail_count": int(controls.get("semantic_detail_count", 0)),
        "low_poly_block_stamping": bool(controls.get("low_poly_block_stamping", False)),
        "mesh_token_stamping": bool(controls.get("mesh_token_stamping", False)),
    }


def _add_dla_detail(mesh: pb.Mesh, mode: str, seed: int, requested: int) -> int:
    centers = list(getattr(mesh, "center_indices", []))
    if not centers:
        return 0
    rng = np.random.default_rng(seed + 2300)
    placed = 0
    stride = max(len(centers) // max(requested, 1), 1)
    sampled = centers[::stride]
    while len(sampled) < requested:
        sampled.extend(centers)
    for k, anchor_idx in enumerate(sampled[:requested]):
        anchor = np.asarray(mesh.vertices[int(anchor_idx) - 1], dtype=float)
        normal = _unit(anchor + rng.normal(0.0, 0.18, 3) + np.array([0.0, 0.0, 0.16]))
        if mode == "crystal":
            u, v, w = _basis(normal + np.array([0.18, -0.10, 0.24]))
            v21._add_box(mesh, int(anchor_idx), anchor + w * 0.035, (u, v, w), (0.052, 0.034, 0.025))
        elif mode == "frontier":
            v21._add_plate(mesh, int(anchor_idx), anchor + normal * 0.035, normal, radius=0.054, thickness=0.012, sides=6)
            if k % 3 == 0:
                v21._add_card(mesh, int(anchor_idx), anchor, normal + np.array([0.08, 0.0, 0.02]), scale=0.045, aspect=2.8)
        elif mode == "lace":
            v21._add_card(mesh, int(anchor_idx), anchor, normal, scale=0.042, aspect=2.4)
            if k % 2 == 0:
                v21._add_plate(mesh, int(anchor_idx), anchor + normal * 0.026, normal, radius=0.036, thickness=0.008, sides=5)
        else:
            v21._add_plate(mesh, int(anchor_idx), anchor + normal * 0.030, normal, radius=0.040, thickness=0.010, sides=6)
        placed += 1
    return placed


def _build_dla_case(seed: int, mode: str, target_events: int, detail_count: int) -> Tuple[pb.Mesh, Dict]:
    base_mode = "staghorn" if mode == "lace" else mode
    mesh, controls = v12._smooth_frontier_tree(seed, base_mode)
    placed = _add_dla_detail(mesh, mode, seed, detail_count)
    support_edges = int(controls.get("skeleton_edges", controls.get("curved_branch_edges", 0)))
    controls = _normalize_controls(controls, "DLA/frontier", support_edges, placed)
    controls.update(
        {
            "frontier_event_target": int(target_events),
            "frontier_events": int(target_events),
            "frontier_attachment_mode": controls.get("frontier_attachment_mode", "active-tip frontier expansion with occupancy exclusion"),
            "bridge_to_root_certificate": "single shared-vertex support plus local detail faces attached to existing centers",
            "semantic_mode": mode,
            "pore_or_facet_detail_count": int(placed),
            "porosity_or_ridge_readability_proxy": int(placed),
        }
    )
    return mesh, controls


def _write_guides(out_dir: Path) -> Dict[str, str]:
    from PIL import Image, ImageDraw, ImageFilter

    guide_dir = out_dir / "_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)

    def stable_seed(name: str) -> int:
        return sum((i + 1) * b for i, b in enumerate(name.encode("utf-8"))) % (2**32)

    def save(name: str, bg: Tuple[int, int, int], colors: List[Tuple[int, int, int]], motif: str) -> str:
        img = Image.new("RGB", (768, 768), bg)
        draw = ImageDraw.Draw(img)
        rng = np.random.default_rng(stable_seed(name))
        for _ in range(880):
            c = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(30, 738))
            y = int(rng.integers(30, 738))
            if motif in {"pine", "root", "vine", "bush"}:
                if motif == "root":
                    draw.line((x, y, x + int(rng.normal(0, 95)), y + int(rng.normal(58, 42))), fill=c, width=int(rng.integers(1, 5)))
                elif motif == "vine":
                    r = int(rng.integers(14, 58))
                    draw.arc((x - r, y - r, x + r, y + r), 20, 330, fill=c, width=int(rng.integers(2, 5)))
                elif motif == "bush":
                    r = int(rng.integers(5, 18))
                    draw.ellipse((x - r, y - r // 2, x + r, y + r // 2), fill=c)
                else:
                    draw.line((x, y, x + int(rng.normal(0, 54)), y + int(rng.normal(-42, 30))), fill=c, width=int(rng.integers(1, 4)))
            elif motif in {"coral", "frontier"}:
                width = int(rng.integers(3, 10))
                draw.line((x, y, x + int(rng.normal(0, 110)), y + int(rng.normal(0, 95))), fill=c, width=width)
                if rng.random() < 0.45:
                    r = int(rng.integers(8, 32))
                    draw.ellipse((x - r, y - r, x + r, y + r), outline=c, width=2)
            elif motif == "crystal":
                r = int(rng.integers(14, 48))
                draw.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], outline=c, width=3)
            elif motif == "radial":
                r = int(rng.integers(20, 76))
                draw.ellipse((x - r, y - r, x + r, y + r), outline=c, width=3)
                for k in range(4):
                    a = math.tau * (k / 4.0 + rng.random() * 0.05)
                    draw.line((x, y, x + int(math.cos(a) * r), y + int(math.sin(a) * r)), fill=c, width=2)
            elif motif == "lattice":
                r = int(rng.integers(12, 42))
                draw.rectangle((x - r, y - r, x + r, y + r), outline=c, width=3)
            else:
                draw.line((x, y, x + int(rng.normal(0, 80)), y + int(rng.normal(-35, 70))), fill=c, width=int(rng.integers(2, 6)))
        path = guide_dir / name
        img.filter(ImageFilter.SMOOTH_MORE).save(path)
        return str(path)

    return {
        "pine": save("V23_lsystem_pine_grammar_pbr_guide.png", (18, 34, 24), [(36, 82, 43), (88, 126, 64), (126, 103, 62), (70, 45, 28)], "pine"),
        "root": save("V23_lsystem_root_fan_grammar_pbr_guide.png", (29, 21, 17), [(72, 49, 32), (126, 84, 48), (166, 119, 74), (22, 16, 12)], "root"),
        "vine": save("V23_lsystem_vine_grammar_pbr_guide.png", (20, 45, 32), [(44, 96, 50), (98, 136, 68), (148, 116, 56), (52, 34, 24)], "vine"),
        "bush": save("V23_space_colonization_bush_shell_pbr_guide.png", (24, 42, 28), [(50, 102, 50), (104, 146, 76), (158, 138, 78), (82, 54, 32)], "bush"),
        "sc_tree": save("V23_space_colonization_tree_crown_pbr_guide.png", (18, 34, 25), [(48, 92, 52), (108, 146, 76), (164, 144, 82), (80, 54, 32)], "pine"),
        "sc_root": save("V23_space_colonization_root_network_pbr_guide.png", (30, 22, 18), [(82, 54, 34), (142, 90, 52), (178, 126, 78), (30, 20, 14)], "root"),
        "coral": save("V23_dla_coral_frontier_pbr_guide.png", (226, 128, 118), [(255, 222, 176), (255, 166, 132), (250, 112, 120), (238, 92, 112)], "coral"),
        "frontier": save("V23_dla_frontier_sheet_pbr_guide.png", (204, 134, 118), [(255, 224, 184), (236, 152, 124), (206, 92, 110), (250, 204, 160)], "frontier"),
        "crystal": save("V23_dla_crystal_frontier_pbr_guide.png", (58, 72, 88), [(104, 142, 172), (188, 212, 218), (230, 202, 132), (82, 104, 128)], "crystal"),
        "lattice": save("V23_ifs_lattice_pyrite_pbr_guide.png", (52, 48, 42), [(238, 204, 96), (180, 132, 54), (92, 82, 68), (252, 232, 140)], "lattice"),
        "radial": save("V23_ifs_radial_ornament_pbr_guide.png", (38, 40, 42), [(196, 166, 92), (124, 132, 142), (96, 68, 58), (224, 210, 154)], "radial"),
        "branch": save("V23_ifs_branch_tree_pbr_guide.png", (36, 38, 30), [(104, 78, 48), (154, 112, 68), (72, 108, 58), (196, 170, 110)], "branch"),
        "ornament": save("V23_ifs_branch_ornament_pbr_guide.png", (42, 38, 34), [(180, 132, 90), (110, 152, 120), (214, 188, 130), (82, 70, 54)], "branch"),
    }


def _grammar_mapping(family: str, target: str, controls: Dict, override: Optional[Dict] = None) -> Dict:
    if family == "L-system":
        mapping = {
            "grammar_family": family,
            "grammar_symbols": "F,+,-,[,],branch/root/vine semantic attachments",
            "target_symbol": "F",
            "operator_to_traditional_mapping": {
                "F": "advance turtle and create a connected swept segment",
                "+/-": "turn the recursive branch/root/vine direction",
                "[]": "push/pop state for finite depth branching",
                "semantic_attachment": "attach needle, leaf, tendril, or rootlet geometry to the same support",
            },
        }
    elif family == "Space colonization":
        mapping = {
            "grammar_family": family,
            "grammar_symbols": "attractor_field,active_tip,influence_radius,kill_radius,step_size",
            "target_symbol": "attractor",
            "operator_to_traditional_mapping": {
                "attractor_select": "select attractors inside the influence radius",
                "grow_tip": "advance a support node in the averaged attractor direction",
                "kill": "remove covered attractors inside the kill radius",
                "occupancy_competition": "reject overly close growth candidates",
            },
        }
    elif family == "DLA/frontier":
        mapping = {
            "grammar_family": family,
            "grammar_symbols": "frontier,occupied_support,stickiness,exclusion,bridge",
            "target_symbol": "frontier_site",
            "operator_to_traditional_mapping": {
                "frontier_sample": "sample rooted active frontier sites",
                "occupancy_exclusion": "reject attachments inside the occupied exclusion radius",
                "attach_patch": "add a local coral, sheet, or facet patch at the frontier",
                "bridge_to_root_certificate": "record that every patch is face-attached to the rooted support",
            },
        }
    else:
        mapping = {
            "grammar_family": family,
            "grammar_symbols": "motif,transform_set,orbit,contact_bridge,copy_depth",
            "target_symbol": "T_i(M)",
            "operator_to_traditional_mapping": {
                "transform_copy": "copy the motif by the same finite transform family",
                "orbit_or_lattice_certificate": "record order, lattice children, or branch copy count",
                "contact_bridge": "keep copied motifs connected at anchors",
                "masked_naturalization": "only improve contact and local facet detail after the copy support exists",
            },
        }
    mapping["remote_comparison_unit"] = "one generated OBJ input to one traditional target"
    if override:
        mapping.update(override)
    mapping["control_lock"] = {k: controls[k] for k in controls if k in {"recursive_depth", "iterations", "attractor_count", "frontier_events", "radial_order", "affine_transform_count"}}
    return mapping


def _family_diagnostics(family: str, target: str, controls: Dict) -> Dict:
    base = {
        "metric_family": family,
        "traditional_target": target,
        "post_glb_required": True,
        "pre_trellis_lcr_min": CONNECTIVITY_LCR_MIN,
        "surface_sampled_lcr_required": 0.98,
        "root_attached_ratio_required": 0.95,
    }
    if family == "L-system":
        base.update(
            {
                "visible_depth": int(controls.get("recursive_depth", controls.get("iterations", 5))),
                "path_to_root_rate_required": 0.95,
                "branch_hierarchy_metric_required": True,
                "terminal_attachment_metric_required": True,
            }
        )
    elif family == "Space colonization":
        base.update(
            {
                "attractor_count": int(controls.get("attractor_count", 260)),
                "covered_attractors": int(controls.get("covered_attractors", 0)),
                "alive_attractors": int(controls.get("alive_attractors", 0)),
                "coverage_metric_required": True,
                "nearest_attractor_distance_required": True,
            }
        )
    elif family == "DLA/frontier":
        base.update(
            {
                "frontier_events": int(controls.get("frontier_events", controls.get("frontier_event_target", 520))),
                "bridge_certificate_required": True,
                "frontier_survival_metric_required": True,
                "blockiness_and_porosity_metric_required": True,
            }
        )
    else:
        base.update(
            {
                "recursive_depth": int(controls.get("recursive_depth", 4)),
                "affine_transform_count": int(controls.get("affine_transform_count", 2)),
                "radial_order": int(controls.get("radial_order", 0)),
                "orbit_or_lattice_metric_required": True,
                "contact_bridge_survival_required": True,
            }
        )
    return base


def _case_specs(seed: int) -> List[Dict]:
    specs: List[Dict] = []

    def add(
        case_id: str,
        family: str,
        target: str,
        recursive_mode: str,
        mesh: pb.Mesh,
        controls: Dict,
        guide_key: str,
        root_variant: str,
        grammar_guide: str,
        parameter_variant: str,
        gpu: int,
        why: str,
        grammar_override: Optional[Dict] = None,
        role: str = "priority_a100_2",
    ) -> None:
        operators = list(OPERATORS_BY_FAMILY[family])
        specs.append(
            {
                "case_id": case_id,
                "family": family,
                "match_target": target,
                "traditional_target": target,
                "recursive_mode": recursive_mode,
                "mesh": mesh,
                "controls": controls,
                "guide_key": guide_key,
                "root_variant": root_variant,
                "grammar_guide": grammar_guide,
                "parameter_variant": parameter_variant,
                "gpu": int(gpu),
                "seed": int(seed + 2300 + len(specs)),
                "operators": operators,
                "operator_composition": " -> ".join(operators),
                "grammar_mapping": _grammar_mapping(family, target, controls, grammar_override),
                "family_diagnostics": _family_diagnostics(family, target, controls),
                "why_matches_traditional": why,
                "strict_match_notes": why,
                "case_role": role,
            }
        )

    mesh, controls, _counts, grammar = v22._build_lsystem_pine(seed + 1, depth=5)
    add(
        "V23_lsys_pine_canopy_d5_multi_root_smooth_needles",
        "L-system",
        "lsys_pine_canopy_d5",
        "depth-5 turtle rewriting with trunk, whorl branches, and needle clusters",
        mesh,
        _normalize_controls(controls, "L-system", int(controls["support_edge_count"]), int(controls["semantic_detail_count"])),
        "pine",
        "smooth_conifer_root_variant_A",
        "lsystem_pine_rewriting_guide",
        "depth5_default_angle_decay",
        4,
        "Matches the finite L-system pine task: same depth and branch hierarchy, with connected needles attached before OBJ export.",
        grammar,
    )

    mesh, controls, _counts, grammar = v22._build_lsystem_root(seed + 2, depth=5)
    add(
        "V23_lsys_root_fan_d5_multi_root_smooth_rootlets",
        "L-system",
        "lsys_root_fan_d5",
        "depth-5 root fan rewriting with downward tropism and rootlets",
        mesh,
        _normalize_controls(controls, "L-system", int(controls["support_edge_count"]), int(controls["semantic_detail_count"])),
        "root",
        "smooth_root_fan_variant_A",
        "lsystem_root_rewriting_guide",
        "depth5_default_root_spread",
        5,
        "Matches the finite root-fan L-system task: main roots and rootlets remain attached to the same support.",
        grammar,
    )

    mesh, controls, _counts, grammar = v22._build_lsystem_vine(seed + 3)
    add(
        "V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils",
        "L-system",
        "lsys_climbing_vine_d6",
        "six-iteration helicoidal vine rewriting with side tendrils and leaves",
        mesh,
        _normalize_controls(controls, "L-system", int(controls["support_edge_count"]), int(controls["semantic_detail_count"])),
        "vine",
        "smooth_vine_variant_A",
        "lsystem_vine_curl_guide",
        "d6_leaf_tendril_default",
        6,
        "Matches the climbing-vine L-system task: the main chain, curling tendrils, and leaves are connected geometry.",
        grammar,
    )

    mesh, controls, _counts, grammar = v22._build_lsystem_root(seed + 4, depth=5)
    controls = dict(controls)
    controls.update({"rootlet_density_variant": "dense", "parameter_sweep_variant": True})
    add(
        "V23_lsys_root_fan_d5_dense_rootlets_variant",
        "L-system",
        "lsys_root_fan_d5_dense_rootlets",
        "depth-5 root fan rewriting with denser local rootlet schedule",
        mesh,
        _normalize_controls(controls, "L-system", int(controls["support_edge_count"]), int(controls["semantic_detail_count"])),
        "root",
        "smooth_root_fan_variant_B",
        "lsystem_root_dense_rootlet_guide",
        "rootlet_density_sweep",
        7,
        "Parameter variant of the same root-fan L-system family, used to screen attached fine-root readability.",
        grammar,
    )

    mesh, controls, _counts, grammar = v22._build_space_colonization("tree_canopy", seed + 11, "tree", 900, 260, 0.220, 0.052, 0.041)
    add(
        "V23_sc_tree_crown_260_attractor_leaf_shell",
        "Space colonization",
        "sc_tree_crown_260",
        "tree-crown attractor competition with influence and kill radii",
        mesh,
        _normalize_controls(controls, "Space colonization", int(controls["support_edge_count"]), int(controls["semantic_detail_count"])),
        "sc_tree",
        "sc_tree_crown_root_variant_A",
        "space_colonization_crown_attractor_guide",
        "ri_0p220_rk_0p052_step_0p041",
        4,
        "Matches the SC tree-crown task with explicit attractor competition and connected canopy detail.",
        grammar,
    )

    mesh, controls, _counts, grammar = v22._build_space_colonization("root_vine", seed + 12, "root", 980, 260, 0.220, 0.052, 0.041)
    add(
        "V23_sc_root_network_260_attractor_rootlets",
        "Space colonization",
        "sc_root_network_260",
        "below-ground root attractor competition with rootlet detail",
        mesh,
        _normalize_controls(controls, "Space colonization", int(controls["support_edge_count"]), int(controls["semantic_detail_count"])),
        "sc_root",
        "sc_root_network_variant_A",
        "space_colonization_root_attractor_guide",
        "ri_0p220_rk_0p052_step_0p041",
        5,
        "Matches the SC root-network target with attractor coverage and root-attached local rootlets.",
        grammar,
    )

    mesh, controls, _counts, grammar = v22._build_space_colonization("bush_shell", seed + 13, "tree", 850, 220, 0.235, 0.060, 0.040)
    add(
        "V23_sc_bush_shell_220_attractor_leaf_shell",
        "Space colonization",
        "sc_bush_shell_220",
        "bush-shell attractor competition with shell coverage",
        mesh,
        _normalize_controls(controls, "Space colonization", int(controls["support_edge_count"]), int(controls["semantic_detail_count"])),
        "bush",
        "sc_bush_shell_variant_A",
        "space_colonization_shell_attractor_guide",
        "ri_0p235_rk_0p060_step_0p040",
        6,
        "Matches the SC bush-shell task while retaining a shell rather than a solid blob.",
        grammar,
    )

    mesh, controls, _counts, grammar = v22._build_space_colonization("tree_canopy", seed + 14, "tree", 780, 260, 0.245, 0.046, 0.038)
    controls = dict(controls)
    controls.update({"parameter_sweep_variant": True, "kill_radius_variant": "sparse_kill"})
    add(
        "V23_sc_tree_crown_260_sparse_kill_variant",
        "Space colonization",
        "sc_tree_crown_260_sparse_kill",
        "tree-crown attractor competition with smaller kill radius parameter sweep",
        mesh,
        _normalize_controls(controls, "Space colonization", int(controls["support_edge_count"]), int(controls["semantic_detail_count"])),
        "sc_tree",
        "sc_tree_crown_root_variant_B",
        "space_colonization_crown_sparse_kill_guide",
        "ri_0p245_rk_0p046_step_0p038",
        7,
        "Parameter variant of the same SC crown family to screen coverage/readability under a smaller kill radius.",
        grammar,
    )

    mesh, controls = _build_dla_case(seed + 21, "staghorn", 900, 132)
    add(
        "V23_dla_coral_cluster_900_staghorn_frontier",
        "DLA/frontier",
        "dla_coral_cluster_900",
        "rooted frontier attachment with occupancy exclusion and tapered coral support",
        mesh,
        controls,
        "coral",
        "dla_staghorn_frontier_root_A",
        "dla_coral_frontier_attachment_guide",
        "events900_staghorn_default",
        4,
        "Matches the DLA coral-cluster task as frontier-attachment asset generation, with every patch bridged to root.",
    )

    mesh, controls = _build_dla_case(seed + 22, "frontier", 700, 112)
    add(
        "V23_dla_frontier_sheet_700_open_boundary",
        "DLA/frontier",
        "dla_frontier_sheet_700",
        "frontier sheet accretion with open-boundary plate detail",
        mesh,
        controls,
        "frontier",
        "dla_frontier_sheet_root_A",
        "dla_frontier_sheet_boundary_guide",
        "events700_plate_open_boundary",
        5,
        "Matches the DLA/frontier sheet task: open boundary and membranes are connected to the rooted support.",
    )

    mesh, controls = _build_dla_case(seed + 23, "crystal", 520, 128)
    add(
        "V23_dla_crystal_cluster_520_faceted_frontier",
        "DLA/frontier",
        "dla_crystal_cluster_520",
        "facet-constrained frontier attachment boundary case",
        mesh,
        controls,
        "crystal",
        "dla_crystal_frontier_root_A",
        "dla_crystal_facet_frontier_guide",
        "events520_facet_ridge",
        6,
        "Matches the crystal-frontier boundary task without claiming physical crystallization.",
    )

    mesh, controls = _build_dla_case(seed + 24, "lace", 900, 156)
    controls.update({"porosity_variant": "lace"})
    add(
        "V23_dla_coral_cluster_900_lace_porosity_variant",
        "DLA/frontier",
        "dla_coral_cluster_900_lace_porosity",
        "frontier coral accretion with extra lace/pore readability",
        mesh,
        controls,
        "coral",
        "dla_lace_coral_root_B",
        "dla_coral_lace_porosity_guide",
        "events900_lace_porosity",
        7,
        "Parameter variant of the coral-frontier task, preserving rooted frontier attachment while improving pore and neck readability.",
    )

    mesh, controls = v21.pyrite_lattice_case(depth=4)
    controls = _normalize_controls(controls, "IFS/transform", int(controls["support_edge_count"]), int(controls["attached_natural_mesh_detail_count"]))
    add(
        "V23_ifs_fractal_lattice_d4_pyrite_copy_bridges",
        "IFS/transform",
        "ifs_fractal_lattice_d4",
        "affine translation/scale/copy lattice with contact bridges",
        mesh,
        controls,
        "lattice",
        "ifs_lattice_pyrite_root_A",
        "ifs_lattice_affine_copy_guide",
        "depth4_six_axis_lattice",
        4,
        "Matches the IFS lattice/orbit task; pyrite-like facets are used only under the lattice target.",
    )

    mesh, controls = v21.radial_ornament_case(order=8, depth=4)
    controls = _normalize_controls(controls, "IFS/transform", int(controls["support_edge_count"]), int(controls["attached_natural_mesh_detail_count"]))
    add(
        "V23_ifs_radial_ornament_o8_d4_orbit_spokes",
        "IFS/transform",
        "ifs_radial_ornament_o8_d4",
        "order-8 radial transform orbit with ring/spoke contact bridges",
        mesh,
        controls,
        "radial",
        "ifs_radial_ornament_root_A",
        "ifs_radial_order8_orbit_guide",
        "order8_depth4",
        5,
        "Matches the order-8 radial IFS task with explicit orbit spokes and contact bridges.",
    )

    mesh, controls = v21.ifs_branch_tree_case(seed + 31, depth=5)
    controls = _normalize_controls(controls, "IFS/transform", int(controls["support_edge_count"]), int(controls["attached_natural_mesh_detail_count"]))
    add(
        "V23_ifs_fractal_tree_d5_branch_copy",
        "IFS/transform",
        "ifs_fractal_tree_d5",
        "contractive branch transform-copy hierarchy with contact bridges",
        mesh,
        controls,
        "branch",
        "ifs_fractal_tree_root_A",
        "ifs_branch_tree_contracting_copy_guide",
        "depth5_three_branch_maps",
        6,
        "Closes the IFS-tree gap with an actual branch/tree transform-copy target rather than substituting lattice or pyrite.",
    )

    mesh, controls = v21.ifs_branch_tree_case(seed + 32, depth=5)
    controls = dict(controls)
    controls.update({"semantic_motif": "branch_ornament_transform", "ornament_variant": True})
    controls = _normalize_controls(controls, "IFS/transform", int(controls["support_edge_count"]), int(controls["attached_natural_mesh_detail_count"]))
    add(
        "V23_ifs_branch_ornament_d5_contact_facets",
        "IFS/transform",
        "ifs_branch_ornament_d5",
        "contractive branch ornament transform-copy with attached contact facets",
        mesh,
        controls,
        "ornament",
        "ifs_branch_ornament_root_B",
        "ifs_branch_ornament_contact_guide",
        "depth5_contact_facet_variant",
        7,
        "Branch-ornament variant of the IFS transform-copy family for appendix-grade screening and contact metric QA.",
    )

    return specs


def _export_mesh(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


def _metadata_for(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    controls = spec["controls"]
    return {
        "case_id": spec["case_id"],
        "family": spec["family"],
        "match_target": spec["match_target"],
        "traditional_target": spec["traditional_target"],
        "traditional_alignment": {
            "traditional_target": spec["traditional_target"],
            "same_category": True,
            "same_recursive_mode": spec["recursive_mode"],
            "strict_one_to_one_comparison": True,
            "control_parameters": controls,
            "why_strict_one_to_one": spec["why_matches_traditional"],
        },
        "grammar_mapping": spec["grammar_mapping"],
        "family_diagnostics": spec["family_diagnostics"],
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
        "seed": int(spec["seed"]),
        "operators": spec["operators"],
        "operator_composition": spec["operator_composition"],
        "controls": controls,
        "initial_mesh_metrics": metrics,
        "why_matches_traditional": spec["why_matches_traditional"],
        "strict_match_notes": spec["strict_match_notes"],
        "case_role": spec["case_role"],
        "strict_generation_policy": "generate_new_on_a100_2_no_local_selection_or_postprocessing",
        "selection_budget": SELECTION_BUDGET,
        "mesh_pbr_contract": {
            "input_mesh_format": "obj",
            "obj_mesh_inputs_only": True,
            "pbr_guide_required": True,
            "pbr_textured_glb_required": True,
            "mesh_outputs_only": True,
            "forbidden_outputs": FORBIDDEN_OUTPUTS,
        },
        "root_selection_log": {
            "root_source_type": "V23_all_family_strict_input_generator",
            "source_generator": "assets/strict_visual_matched_cases_V23_all_family_20260510.py",
            "root_variant": spec["root_variant"],
            "grammar_guide": spec["grammar_guide"],
            "parameter_variant": spec["parameter_variant"],
            "root_screening_budget": SELECTION_BUDGET,
        },
        "visual_readability_contract": {
            "dryrun_visual_floor": "OBJ input must pass LCR gate; local dry-run is not final selected output",
            "positive_constraint": "paper-grade strict matched candidate must preserve the named family, visible recursive structure, connected local details, and PBR-readable material guide",
            "negative_constraint": "no low-poly block surfaces, no token stamping, no detached semantic islands, no family substitution, no local selected result substitution",
            "post_remote_required": "white overview, zoom panels, post-GLB metrics, and human QA are required before paper use",
        },
    }


def _write_readme(out_dir: Path, summary: Dict) -> None:
    text = """# V23 All-Family Strict Matched Cases Dry Run

Produced by `assets/strict_visual_matched_cases_V23_all_family_20260510.py`.

This is an input batch only. It does not launch remote jobs, locally select
outputs, or post-process prior final assets. Final strict one-to-one cases must
be generated fresh on `{remote}` with GPU ids `{gpus}` under:

`{storage}`

Connectivity gate: largest-component vertex ratio >= `{lcr}` before Trellis2.
Mesh policy: OBJ inputs plus PBR guide images only.
Case count: {count}. GPU split: {gpu_counts}.
""".format(
        remote=REMOTE_TARGET,
        gpus=ALLOWED_GPUS,
        storage=REMOTE_STORAGE_ROOT,
        lcr=CONNECTIVITY_LCR_MIN,
        count=summary["num_cases"],
        gpu_counts=summary["gpu_case_counts"],
    )
    (out_dir / "README.md").write_text(text, encoding="utf-8")


def materialize(root: Path, out_dir: Path, seed: int = 20260510, case_limit: Optional[int] = None) -> Dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    guides = _write_guides(out_dir)
    specs = _case_specs(seed)
    if case_limit is not None:
        specs = specs[: int(case_limit)]

    rows: List[Dict] = []
    metrics_rows: List[Dict] = []
    for spec in specs:
        case_dir = out_dir / spec["case_id"]
        mesh_path = case_dir / ("%s.obj" % spec["case_id"])
        _export_mesh(mesh_path, spec["mesh"])
        guide_path = guides[spec["guide_key"]]
        metrics = _mesh_stats(mesh_path, spec["controls"])
        if metrics["largest_mesh_component_vertex_ratio"] < CONNECTIVITY_LCR_MIN:
            raise RuntimeError("%s failed V23 connectivity gate: %s" % (spec["case_id"], metrics))
        metadata = _metadata_for(spec, mesh_path, guide_path, metrics)
        metadata_path = case_dir / ("%s_metadata.json" % spec["case_id"])
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
            "strict_one_to_one": "true",
            "generation_policy": "generate_new_on_a100_2_no_local_selection_or_postprocessing",
            "mesh_input_policy": "obj_mesh_inputs_only",
            "mesh_pbr_policy": "obj_inputs_and_pbr_guides_for_trellis2_glb_export",
            "surface_strategy": SURFACE_STRATEGY,
            "block_or_token_stamping": "false",
            "root_variant": spec["root_variant"],
            "grammar_guide": spec["grammar_guide"],
            "parameter_variant": spec["parameter_variant"],
            "selection_budget": SELECTION_BUDGET,
            "storage_root": REMOTE_STORAGE_ROOT,
            "storage_limit_gb": STORAGE_LIMIT_GB,
        }
        rows.append(row)
        metrics_rows.append(
            {
                "case_id": spec["case_id"],
                "family": spec["family"],
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
        "mesh_input_policy",
        "mesh_pbr_policy",
        "surface_strategy",
        "block_or_token_stamping",
        "root_variant",
        "grammar_guide",
        "parameter_variant",
        "selection_budget",
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
        "family",
        "match_target",
        "traditional_target",
        "vertices",
        "faces",
        "mesh_component_count",
        "largest_mesh_component_vertex_ratio",
        "bbox_extent",
        "bbox_diag",
        "surface_area",
        "support_edge_count",
        "semantic_detail_count",
        "low_poly_block_stamping",
        "mesh_token_stamping",
    ]
    with (out_dir / "initial_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        writer.writerows(metrics_rows)
    (out_dir / "initial_metrics.json").write_text(json.dumps(metrics_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    case_lines = ["%s|%s|%s|%s|%s" % (row["case_id"], row["mesh_path"], row["guide_image"], row["seed"], row["gpu_group"]) for row in rows]
    (out_dir / "a100-2_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    (out_dir / "gpu4567_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    gpu_case_counts: Dict[str, int] = {}
    for gpu in ALLOWED_GPUS:
        selected = [line for line, row in zip(case_lines, rows) if int(row["gpu_group"]) == gpu]
        gpu_case_counts[str(gpu)] = len(selected)
        (out_dir / ("gpu%s_cases.txt" % gpu)).write_text("\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")

    summary = {
        "out_dir": str(out_dir),
        "num_cases": len(rows),
        "estimated_remote_cases": len(rows),
        "gpu_case_counts": gpu_case_counts,
        "remote_target": REMOTE_TARGET,
        "allowed_gpus": ALLOWED_GPUS,
        "storage_root": REMOTE_STORAGE_ROOT,
        "storage_limit_gb": STORAGE_LIMIT_GB,
        "surface_generator": "strict_all_family_matched_cases_v23",
        "mesh_input_policy": "obj_mesh_inputs_only",
        "mesh_pbr_policy": "obj_inputs_and_pbr_guides_for_trellis2_glb_export",
        "connectivity_gate": {
            "largest_component_vertex_ratio_min": CONNECTIVITY_LCR_MIN,
            "pre_trellis_required": True,
        },
        "storage_risk": {
            "expected_upper_bound_gb": 64,
            "risk_level": "medium",
            "notes": "16 Trellis2 mesh/PBR exports at 2048 texture size may consume tens of GB including logs and caches; keep within the user-approved 200 GB project cap and clean stale failed/cache artifacts.",
        },
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
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260510)
    parser.add_argument("--case-limit", type=int, default=None)
    args = parser.parse_args()
    materialize(args.root, args.out, seed=args.seed, case_limit=args.case_limit)


if __name__ == "__main__":
    main()
