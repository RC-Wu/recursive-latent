#!/usr/bin/env python3
"""V24 priority rerun strict matched case generator.

This generator prepares a small publication-focused rerun batch after the V23
three-seed visual QA.  It prioritizes root quality and SC tree/root reruns, with
small DLA/IFS polish coverage.  It only materializes OBJ inputs, PBR guides,
manifests, and GPU split files; it never launches remote jobs.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import procedural_baselines as pb
import strict_visual_matched_cases_V23_all_family_20260510 as v23


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 200
CONNECTIVITY_LCR_MIN = 0.999
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V24_priority_rerun_20260510_dryrun"

SURFACE_STRATEGY = "v24_priority_root_sc_rerun_with_dla_ifs_polish"
SELECTION_BUDGET = "one_remote_generation_per_manifest_row_no_local_cherry_pick"
GENERATION_POLICY = "generate_new_on_a100_2_no_local_selection_or_postprocessing"
MESH_PBR_POLICY = "obj_inputs_and_pbr_guides_for_trellis2_glb_export"


def _v23_spec(seed: int, case_id: str) -> Dict:
    for spec in v23._case_specs(seed):
        if spec["case_id"] == case_id:
            return deepcopy(spec)
    raise KeyError(case_id)


def _retarget(
    spec: Dict,
    *,
    case_id: str,
    gpu: int,
    seed: int,
    role: str,
    root_variant: str,
    grammar_guide: str,
    parameter_variant: str,
    rerun_reason: str,
    qa_priority: str,
    boundary_tag: str = "",
) -> Dict:
    spec = deepcopy(spec)
    spec["case_id"] = case_id
    spec["gpu"] = int(gpu)
    spec["seed"] = int(seed)
    spec["case_role"] = role
    spec["root_variant"] = root_variant
    spec["grammar_guide"] = grammar_guide
    spec["parameter_variant"] = parameter_variant
    spec["rerun_reason"] = rerun_reason
    spec["qa_priority"] = qa_priority
    spec["boundary_tag"] = boundary_tag
    spec["strict_match_notes"] = rerun_reason
    spec["why_matches_traditional"] = "%s V24 rerun target: %s" % (spec["why_matches_traditional"], rerun_reason)
    spec["operator_composition"] = spec["operator_composition"] + " -> V24_priority_rerun_gate"
    spec["controls"] = dict(spec["controls"])
    spec["controls"].update(
        {
            "v24_priority_rerun": True,
            "v24_qa_priority": qa_priority,
            "v24_rerun_reason": rerun_reason,
            "connectivity_gate_lcr_min": CONNECTIVITY_LCR_MIN,
            "boundary_tag": boundary_tag,
            "support_edge_count": max(20, int(spec["controls"].get("support_edge_count", 0))),
            "semantic_detail_count": max(24, int(spec["controls"].get("semantic_detail_count", 0))),
        }
    )
    spec["grammar_mapping"] = deepcopy(spec["grammar_mapping"])
    spec["grammar_mapping"]["v24_priority_rerun"] = True
    spec["grammar_mapping"]["v24_rerun_reason"] = rerun_reason
    spec["family_diagnostics"] = deepcopy(spec["family_diagnostics"])
    spec["family_diagnostics"]["v24_priority_rerun"] = True
    spec["family_diagnostics"]["v24_qa_priority"] = qa_priority
    spec["family_diagnostics"]["boundary_tag"] = boundary_tag
    return spec


def _case_specs(seed: int) -> List[Dict]:
    rows: List[Dict] = []

    def add(base_seed_offset: int, base_case: str, **kwargs) -> None:
        rows.append(_retarget(_v23_spec(seed + base_seed_offset, base_case), **kwargs))

    add(
        0,
        "V23_lsys_root_fan_d5_dense_rootlets_variant",
        case_id="V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA",
        gpu=4,
        seed=seed + 24001,
        role="priority_root_quality",
        root_variant="dense_rootlets_anchorA",
        grammar_guide="lsystem_root_dense_anchor_guide_A",
        parameter_variant="dense_rootlets_anchor_strength_A",
        rerun_reason="rerun dense root fan to improve rootlet attachment and reduce floating hair-like tips",
        qa_priority="root_quality",
    )
    add(
        17,
        "V23_lsys_root_fan_d5_dense_rootlets_variant",
        case_id="V24_lsys_root_fan_d5_dense_rootlets_anchorB_seedB",
        gpu=5,
        seed=seed + 24002,
        role="priority_root_quality",
        root_variant="dense_rootlets_anchorB",
        grammar_guide="lsystem_root_dense_anchor_guide_B",
        parameter_variant="dense_rootlets_lower_tip_noise",
        rerun_reason="second dense root fan seed for attachment robustness and less visible clipping",
        qa_priority="root_quality",
    )
    add(
        29,
        "V23_lsys_root_fan_d5_multi_root_smooth_rootlets",
        case_id="V24_lsys_root_fan_d5_smooth_rootlets_anchorA_seedA",
        gpu=6,
        seed=seed + 24003,
        role="priority_root_quality",
        root_variant="smooth_rootlets_anchorA",
        grammar_guide="lsystem_root_smooth_anchor_guide_A",
        parameter_variant="smooth_rootlets_attachment_first",
        rerun_reason="rerun smooth root fan as cleaner appendix/main fallback for root quality claim",
        qa_priority="root_quality",
    )
    add(
        43,
        "V23_lsys_root_fan_d5_multi_root_smooth_rootlets",
        case_id="V24_lsys_root_fan_d5_smooth_rootlets_anchorB_seedB",
        gpu=7,
        seed=seed + 24004,
        role="priority_root_quality",
        root_variant="smooth_rootlets_anchorB",
        grammar_guide="lsystem_root_smooth_anchor_guide_B",
        parameter_variant="smooth_rootlets_wider_fan",
        rerun_reason="second smooth root fan seed to screen wider root silhouette without detached rootlets",
        qa_priority="root_quality",
    )

    add(
        53,
        "V23_sc_root_network_260_attractor_rootlets",
        case_id="V24_sc_root_network_260_anchorA_seedA",
        gpu=4,
        seed=seed + 24005,
        role="priority_sc_root_quality",
        root_variant="sc_root_network_anchorA",
        grammar_guide="space_colonization_root_anchor_guide_A",
        parameter_variant="root_network_higher_anchor_lower_orphan",
        rerun_reason="highest priority SC root-network rerun; current V23 root network is not main-text safe",
        qa_priority="root_quality",
    )
    add(
        67,
        "V23_sc_root_network_260_attractor_rootlets",
        case_id="V24_sc_root_network_260_anchorB_seedB",
        gpu=5,
        seed=seed + 24006,
        role="priority_sc_root_quality",
        root_variant="sc_root_network_anchorB",
        grammar_guide="space_colonization_root_anchor_guide_B",
        parameter_variant="root_network_sparse_orphan_suppression",
        rerun_reason="second SC root-network seed for path-to-root and orphan-fragment screening",
        qa_priority="root_quality",
    )
    add(
        79,
        "V23_sc_tree_crown_260_attractor_leaf_shell",
        case_id="V24_sc_tree_crown_260_attractor_clean_seedA",
        gpu=6,
        seed=seed + 24007,
        role="priority_sc_tree_visual_quality",
        root_variant="sc_tree_crown_cleanA",
        grammar_guide="space_colonization_crown_clean_guide_A",
        parameter_variant="tree_crown_less_clipping",
        rerun_reason="SC main-text candidate rerun to reduce visible clipped cylinders and small fragments",
        qa_priority="visual_quality",
    )
    add(
        83,
        "V23_sc_tree_crown_260_attractor_leaf_shell",
        case_id="V24_sc_tree_crown_260_attractor_clean_seedB",
        gpu=7,
        seed=seed + 24008,
        role="priority_sc_tree_visual_quality",
        root_variant="sc_tree_crown_cleanB",
        grammar_guide="space_colonization_crown_clean_guide_B",
        parameter_variant="tree_crown_smoother_local_tips",
        rerun_reason="second SC tree-crown seed to find a cleaner main-text crop",
        qa_priority="visual_quality",
    )
    add(
        97,
        "V23_sc_tree_crown_260_sparse_kill_variant",
        case_id="V24_sc_tree_crown_260_sparse_kill_clean_seedA",
        gpu=4,
        seed=seed + 24009,
        role="priority_sc_tree_backup",
        root_variant="sc_tree_crown_sparse_cleanA",
        grammar_guide="space_colonization_crown_sparse_clean_guide_A",
        parameter_variant="sparse_kill_less_occlusion",
        rerun_reason="SC tree-crown backup if attractor main candidate remains visually crowded",
        qa_priority="visual_quality",
    )
    add(
        101,
        "V23_sc_tree_crown_260_sparse_kill_variant",
        case_id="V24_sc_tree_crown_260_sparse_kill_clean_seedB",
        gpu=5,
        seed=seed + 24010,
        role="priority_sc_tree_backup",
        root_variant="sc_tree_crown_sparse_cleanB",
        grammar_guide="space_colonization_crown_sparse_clean_guide_B",
        parameter_variant="sparse_kill_fragment_suppression",
        rerun_reason="second sparse-kill crown seed for less visible fragment/cap artifacts",
        qa_priority="visual_quality",
    )

    add(
        113,
        "V23_dla_coral_cluster_900_staghorn_frontier",
        case_id="V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA",
        gpu=6,
        seed=seed + 24011,
        role="dla_visual_polish",
        root_variant="dla_staghorn_polishA",
        grammar_guide="dla_staghorn_tip_polish_guide_A",
        parameter_variant="staghorn_tip_cap_softening",
        rerun_reason="small DLA polish rerun to keep LCR=1 while reducing cap/tube artificiality",
        qa_priority="visual_polish",
    )
    add(
        100,
        "V23_dla_frontier_sheet_700_open_boundary",
        case_id="V24_dla_frontier_sheet_700_open_boundary_polish_seedA",
        gpu=7,
        seed=seed + 24012,
        role="dla_visual_polish",
        root_variant="dla_frontier_sheet_polishA",
        grammar_guide="dla_frontier_open_boundary_polish_guide_A",
        parameter_variant="frontier_sheet_branch_thickness_polish",
        rerun_reason="small frontier-sheet polish for branch thickness and less obvious cut ends",
        qa_priority="visual_polish",
    )
    add(
        139,
        "V23_dla_coral_cluster_900_lace_porosity_variant",
        case_id="V24_dla_coral_cluster_900_lace_porosity_boundary_seedA",
        gpu=4,
        seed=seed + 24013,
        role="dla_boundary_polish",
        root_variant="dla_lace_boundaryA",
        grammar_guide="dla_lace_porosity_boundary_guide_A",
        parameter_variant="lace_porosity_boundary_check",
        rerun_reason="boundary-tagged DLA lace rerun; useful only if post-GLB fragments remain invisible",
        qa_priority="boundary_visual_polish",
        boundary_tag="near_stable_v23_components_r0_up_to_7_requires_post_glb_fragment_QA",
    )

    add(
        149,
        "V23_ifs_fractal_lattice_d4_pyrite_copy_bridges",
        case_id="V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA",
        gpu=5,
        seed=seed + 24014,
        role="ifs_visual_polish",
        root_variant="ifs_lattice_pyrite_polishA",
        grammar_guide="ifs_lattice_bridge_polish_guide_A",
        parameter_variant="pyrite_bridge_contact_polish",
        rerun_reason="IFS lattice polish to make bridges read as contact rather than mechanical interpenetration",
        qa_priority="visual_polish",
    )
    add(
        163,
        "V23_ifs_radial_ornament_o8_d4_orbit_spokes",
        case_id="V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA",
        gpu=6,
        seed=seed + 24015,
        role="ifs_visual_polish",
        root_variant="ifs_radial_orbit_polishA",
        grammar_guide="ifs_radial_orbit_polish_guide_A",
        parameter_variant="radial_orbit_contact_polish",
        rerun_reason="small radial/orbit polish as appendix fallback if lattice visual QA fails",
        qa_priority="visual_polish",
    )

    return rows


def _metadata_for(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    metadata = v23._metadata_for(spec, mesh_path, guide_path, metrics)
    metadata["case_id"] = spec["case_id"]
    metadata["strict_generation_policy"] = GENERATION_POLICY
    metadata["selection_budget"] = SELECTION_BUDGET
    metadata["case_role"] = spec["case_role"]
    metadata["rerun_reason"] = spec["rerun_reason"]
    metadata["qa_priority"] = spec["qa_priority"]
    metadata["boundary_tag"] = spec.get("boundary_tag", "")
    metadata["root_selection_log"]["root_source_type"] = "V24_priority_rerun_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V24_priority_rerun_20260510.py"
    metadata["visual_readability_contract"]["post_remote_required"] = (
        "post-GLB surface metrics, root/fragment QA, white overview, zoom panels, and human review are required before paper use"
    )
    metadata["v24_remote_cache_policy"] = {
        "cache_root": REMOTE_STORAGE_ROOT + "/cache",
        "tmpdir": REMOTE_STORAGE_ROOT + "/cache/local_tmp/strict_visual_matched_texture_V24_priority_rerun_20260510",
        "no_system_tmp": True,
    }
    return metadata


def _write_readme(out_dir: Path, summary: Dict) -> None:
    text = """# V24 Priority Rerun Strict Matched Cases Dry Run

Produced by `assets/strict_visual_matched_cases_V24_priority_rerun_20260510.py`.

This is an input batch only. It does not launch remote jobs, locally select
outputs, delete old files, or touch paper sources.

Priority: root quality and SC tree/root rerun; small DLA/IFS polish.
Remote: `{remote}`. GPUs: `{gpus}` only.
Cache/storage root: `{storage}`.
Connectivity gate: largest-component vertex ratio >= `{lcr}` before Trellis2,
unless a row has an explicit boundary tag requiring post-GLB QA.
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
    guides = v23._write_guides(out_dir)
    specs = _case_specs(seed)
    if case_limit is not None:
        specs = specs[: int(case_limit)]

    rows: List[Dict] = []
    metrics_rows: List[Dict] = []
    for spec in specs:
        case_dir = out_dir / spec["case_id"]
        mesh_path = case_dir / ("%s.obj" % spec["case_id"])
        v23._export_mesh(mesh_path, spec["mesh"])
        guide_path = guides[spec["guide_key"]]
        metrics = v23._mesh_stats(mesh_path, spec["controls"])
        if metrics["largest_mesh_component_vertex_ratio"] < CONNECTIVITY_LCR_MIN and not spec.get("boundary_tag"):
            raise RuntimeError("%s failed V24 connectivity gate: %s" % (spec["case_id"], metrics))
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
            "qa_priority": spec["qa_priority"],
            "rerun_reason": spec["rerun_reason"],
            "boundary_tag": spec.get("boundary_tag", ""),
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
            "pre_export_gate_or_boundary": "boundary_tag" if spec.get("boundary_tag") else "lcr>=0.999",
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
                "boundary_tag": spec.get("boundary_tag", ""),
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
        "qa_priority",
        "rerun_reason",
        "boundary_tag",
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
        "pre_export_lcr_gate",
        "pre_export_gate_or_boundary",
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
        "qa_priority",
        "boundary_tag",
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
        "surface_generator": "strict_visual_matched_cases_V24_priority_rerun",
        "mesh_input_policy": "obj_mesh_inputs_only",
        "mesh_pbr_policy": MESH_PBR_POLICY,
        "connectivity_gate": {
            "largest_component_vertex_ratio_min": CONNECTIVITY_LCR_MIN,
            "pre_trellis_required": True,
            "boundary_tag_allowed": True,
        },
        "storage_risk": {
            "expected_upper_bound_gb": 64,
            "risk_level": "medium",
            "notes": "15 Trellis2 mesh/PBR exports at 2048 texture size should remain inside the project cache/storage root; do not use system /tmp or /dev/shm.",
        },
        "manifest": str(out_dir / "manifest.csv"),
        "initial_metrics": str(out_dir / "initial_metrics.csv"),
        "priority_cases": [row["case_id"] for row in rows],
        "do_not_launch_remote": True,
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
