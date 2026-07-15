#!/usr/bin/env python3
"""V25 small refinement batch for root-fan and SC-crown visual weak points."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import baseline_matrix_20260509 as bm
import procedural_baselines as pb
import strict_visual_matched_cases_V22_botanical_smooth_20260510 as v22
import strict_visual_matched_cases_V23_all_family_20260510 as v23


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 200
CONNECTIVITY_LCR_MIN = 0.999
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V25_root_sc_refine_20260510_dryrun"

SURFACE_STRATEGY = "v25_root_sc_refine_tapered_support_and_attached_detail"
GENERATION_POLICY = "generate_new_on_a100_2_no_local_selection_or_postprocessing"
SELECTION_BUDGET = "small_refinement_batch_8_manifest_rows_predeclared"
MESH_PBR_POLICY = "obj_inputs_and_pbr_guides_for_trellis2_glb_export"


def _scale_support_radii(mesh: pb.Mesh, factor: float) -> None:
    centers = getattr(mesh, "center_indices", [])
    center_set = set(int(i) - 1 for i in centers)
    if not centers:
        return
    arr = np.asarray([mesh.vertices[int(i) - 1] for i in centers], dtype=float)
    tree = arr
    verts = [np.asarray(v, dtype=float) for v in mesh.vertices]
    for idx, v in enumerate(verts):
        if idx in center_set:
            continue
        distances = np.linalg.norm(tree - v[None, :], axis=1)
        anchor = tree[int(np.argmin(distances))]
        verts[idx] = anchor + (v - anchor) * float(factor)
    mesh.vertices = [tuple(v) for v in verts]


def _raise_and_taper_tree(mesh: pb.Mesh, z_gain: float, radial_shrink_top: float) -> None:
    verts = np.asarray(mesh.vertices, dtype=float)
    if len(verts) == 0:
        return
    z_min = float(verts[:, 2].min())
    z_max = float(verts[:, 2].max())
    span = max(z_max - z_min, 1e-6)
    center_xy = verts[:, :2].mean(axis=0)
    for idx, v in enumerate(verts):
        t = (float(v[2]) - z_min) / span
        v[2] = z_min + (float(v[2]) - z_min) * (1.0 + float(z_gain) * t)
        shrink = 1.0 - float(radial_shrink_top) * max(t - 0.35, 0.0)
        v[:2] = center_xy + (v[:2] - center_xy) * max(shrink, 0.72)
        verts[idx] = v
    mesh.vertices = [tuple(v) for v in verts]


def _build_root_case(seed: int, *, density: int, support_scale: float, downward: float) -> tuple[pb.Mesh, Dict, Dict]:
    rng = np.random.default_rng(seed + 2501)
    nodes0, parents = bm.lsystem_case("root", depth=5, seed=seed)
    nodes = v22._normalize_nodes([np.asarray(p, dtype=float) for p in nodes0], 2.70)
    mesh, controls, _counts, grammar = v22._build_lsystem_root(seed, depth=5)
    _scale_support_radii(mesh, support_scale)
    counts = v22._scatter_rootlets(mesh, nodes, parents, rng, count=density, downward=downward)
    controls = dict(controls)
    controls.update(
        {
            "v25_refine": True,
            "v25_refine_goal": "root_fan_r0_stability_and_rootlet_attachment",
            "support_radius_scale": float(support_scale),
            "extra_rootlet_count": int(counts["rootlet_count"]),
            "rootlet_density": int(density),
            "rootlet_downward_bias": float(downward),
            "semantic_detail_count": int(controls.get("semantic_detail_count", 0)) + int(counts["rootlet_count"]),
            "rootlet_count": int(controls.get("rootlet_count", 0)) + int(counts["rootlet_count"]),
        }
    )
    return mesh, controls, grammar


def _build_sc_case(
    seed: int,
    *,
    attractors: int,
    iterations: int,
    influence: float,
    kill: float,
    step: float,
    z_gain: float,
    shrink: float,
) -> tuple[pb.Mesh, Dict, Dict]:
    mesh, controls, _counts, grammar = v22._build_space_colonization(
        "tree_canopy", seed, "tree", attractors, iterations, influence, kill, step
    )
    _scale_support_radii(mesh, 0.82)
    _raise_and_taper_tree(mesh, z_gain, shrink)
    controls = dict(controls)
    controls.update(
        {
            "v25_refine": True,
            "v25_refine_goal": "space_colonization_crown_trunk_cap_visual_quality",
            "support_radius_scale": 0.82,
            "z_gain": float(z_gain),
            "radial_shrink_top": float(shrink),
            "attractor_count": int(attractors),
            "iterations": int(iterations),
            "influence_radius": float(influence),
            "kill_radius": float(kill),
            "step_size": float(step),
        }
    )
    return mesh, controls, grammar


def _spec(
    *,
    case_id: str,
    family: str,
    target: str,
    mode: str,
    mesh: pb.Mesh,
    controls: Dict,
    guide_key: str,
    root_variant: str,
    grammar_guide: str,
    parameter_variant: str,
    gpu: int,
    seed: int,
    reason: str,
    grammar: Dict,
) -> Dict:
    controls = dict(controls)
    controls.update(
        {
            "mesh_input_format": "obj",
            "same_classical_task_mode": True,
            "connected_support": True,
            "connectivity_gate_lcr_min": CONNECTIVITY_LCR_MIN,
            "low_poly_block_stamping": False,
            "mesh_token_stamping": False,
            "v25_root_sc_refine": True,
        }
    )
    operators = list(v23.OPERATORS_BY_FAMILY[family])
    return {
        "case_id": case_id,
        "family": family,
        "match_target": target,
        "traditional_target": target,
        "recursive_mode": mode,
        "mesh": mesh,
        "controls": controls,
        "guide_key": guide_key,
        "root_variant": root_variant,
        "grammar_guide": grammar_guide,
        "parameter_variant": parameter_variant,
        "gpu": int(gpu),
        "seed": int(seed),
        "operators": operators,
        "operator_composition": " -> ".join(operators + ["V25_refinement_gate"]),
        "grammar_mapping": v23._grammar_mapping(family, target, controls, grammar),
        "family_diagnostics": v23._family_diagnostics(family, target, controls),
        "why_matches_traditional": reason,
        "strict_match_notes": reason,
        "case_role": "v25_root_sc_refinement",
        "qa_priority": "root_stability" if family == "L-system" else "sc_visual_quality",
        "rerun_reason": reason,
        "boundary_tag": "",
    }


def _case_specs(seed: int) -> List[Dict]:
    rows: List[Dict] = []
    root_settings = [
        ("V25_lsys_root_fan_dense_anchorC_stable", 4, 25001, 260, 0.92, 0.80, "root fan dense anchor C with thicker shared support"),
        ("V25_lsys_root_fan_dense_anchorD_stable", 5, 25002, 300, 0.88, 0.76, "root fan dense anchor D with extra attached fine roots"),
        ("V25_lsys_root_fan_smooth_anchorC_stable", 6, 25003, 230, 0.96, 0.68, "smooth root fan C for cleaner silhouette and fewer islands"),
        ("V25_lsys_root_fan_smooth_anchorD_stable", 7, 25004, 250, 0.90, 0.72, "smooth root fan D with stronger rootlet attachment"),
    ]
    for case_id, gpu, offset, density, support_scale, downward, reason in root_settings:
        mesh, controls, grammar = _build_root_case(seed + offset, density=density, support_scale=support_scale, downward=downward)
        rows.append(
            _spec(
                case_id=case_id,
                family="L-system",
                target="lsys_root_fan_d5",
                mode="depth-5 root fan rewriting with attached rootlets",
                mesh=mesh,
                controls=controls,
                guide_key="root",
                root_variant=case_id.replace("V25_", ""),
                grammar_guide="v25_lsystem_root_attachment_guide",
                parameter_variant=f"density{density}_support{support_scale:.2f}_down{downward:.2f}",
                gpu=gpu,
                seed=seed + offset,
                reason=reason,
                grammar=grammar,
            )
        )

    sc_settings = [
        ("V25_sc_tree_crown_tapered_A", 4, 25011, 780, 260, 0.225, 0.050, 0.037, 0.18, 0.16, "tapered SC crown A to reduce blocky trunk/cap artifacts"),
        ("V25_sc_tree_crown_tapered_B", 5, 25012, 840, 260, 0.215, 0.054, 0.036, 0.14, 0.18, "tapered SC crown B with denser canopy but slimmer exported tubes"),
        ("V25_sc_tree_crown_leafshield_A", 6, 25013, 720, 260, 0.235, 0.048, 0.038, 0.20, 0.12, "leaf-shield SC crown A to hide cut caps while preserving attractor crown"),
        ("V25_sc_tree_crown_leafshield_B", 7, 25014, 900, 260, 0.205, 0.056, 0.035, 0.12, 0.20, "leaf-shield SC crown B for cleaner local zoom and less massive trunk"),
    ]
    for case_id, gpu, offset, attractors, iterations, influence, kill, step, z_gain, shrink, reason in sc_settings:
        mesh, controls, grammar = _build_sc_case(
            seed + offset,
            attractors=attractors,
            iterations=iterations,
            influence=influence,
            kill=kill,
            step=step,
            z_gain=z_gain,
            shrink=shrink,
        )
        rows.append(
            _spec(
                case_id=case_id,
                family="Space colonization",
                target="sc_tree_crown_260",
                mode="tree-crown attractor competition with tapered connected support",
                mesh=mesh,
                controls=controls,
                guide_key="sc_tree",
                root_variant=case_id.replace("V25_", ""),
                grammar_guide="v25_space_colonization_crown_visual_guide",
                parameter_variant=f"a{attractors}_ri{influence:.3f}_rk{kill:.3f}_step{step:.3f}_zg{z_gain:.2f}",
                gpu=gpu,
                seed=seed + offset,
                reason=reason,
                grammar=grammar,
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
    metadata["root_selection_log"]["root_source_type"] = "V25_root_sc_refine_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V25_root_sc_refine_20260510.py"
    metadata["v25_remote_cache_policy"] = {
        "cache_root": REMOTE_STORAGE_ROOT + "/cache",
        "no_system_tmp": True,
    }
    return metadata


def materialize(root: Path, out_dir: Path, seed: int = 20260510, case_limit: Optional[int] = None) -> Dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    guides = v23._write_guides(out_dir)
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
            raise RuntimeError(f"{spec['case_id']} failed V25 connectivity gate: {metrics}")
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
        "surface_generator": "strict_visual_matched_cases_V25_root_sc_refine",
        "mesh_input_policy": "obj_mesh_inputs_only",
        "mesh_pbr_policy": MESH_PBR_POLICY,
        "connectivity_gate": {
            "largest_component_vertex_ratio_min": CONNECTIVITY_LCR_MIN,
            "pre_trellis_required": True,
            "boundary_tag_allowed": False,
        },
        "storage_risk": {
            "expected_upper_bound_gb": 40,
            "risk_level": "low-medium",
            "notes": "8 Trellis2 mesh/PBR exports; cache must remain inside project root.",
        },
        "gpu_case_counts": gpu_case_counts,
        "priority_cases": [row["case_id"] for row in rows],
        "manifest": str(out_dir / "manifest.csv"),
        "initial_metrics": str(out_dir / "initial_metrics.csv"),
        "do_not_launch_remote": True,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V25 Root/SC Refinement Dry Run\n\n"
        "Small predeclared refinement batch for L-system root-fan r0 stability and "
        "space-colonization crown trunk/cap visual quality. Generate only; remote launch is separate.\n",
        encoding="utf-8",
    )
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
