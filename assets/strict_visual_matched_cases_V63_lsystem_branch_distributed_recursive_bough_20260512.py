#!/usr/bin/env python3
"""V63 distributed L-system branch depth/density candidates.

V62 passed the numeric depth/density gates, but its compact short-bough graph
packed the recursive branches into a few thick terminal clusters.  V63 restores
the V53 distributed main-axis side-branch graph, keeps the V59/V61 anti-facet
implicit field, and retains the V62 publication gates for junction/terminal
count.  The claim remains object-space grammar-owned naturalization; no 2D
seam inpaint, SDEdit/backprojection, or UV patching pipeline is claimed.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import io
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import strict_visual_matched_cases_V58_lsystem_branch_short_bough_yfork_20260511 as v58
import strict_visual_matched_cases_V59_lsystem_branch_smooth_short_bough_yfork_20260511 as v59
import strict_visual_matched_cases_V62_lsystem_branch_recursive_dense_bough_yfork_20260512 as v62


v53 = v62.v53
pb = v62.pb

REMOTE_TARGET = v62.REMOTE_TARGET
ALLOWED_GPUS = v62.ALLOWED_GPUS
DEFAULT_ACTIVE_GPUS = v62.DEFAULT_ACTIVE_GPUS
REMOTE_STORAGE_ROOT = v62.REMOTE_STORAGE_ROOT
STORAGE_LIMIT_GB = v62.STORAGE_LIMIT_GB
CONNECTIVITY_LCR_MIN = v62.CONNECTIVITY_LCR_MIN
EXTERNAL_SUPPORT_MAX_SEGMENT_GATE = v62.EXTERNAL_SUPPORT_MAX_SEGMENT_GATE
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V63_lsystem_branch_distributed_recursive_bough_20260512_dryrun"

SURFACE_STRATEGY = "v63_lsystem_branch_distributed_recursive_bough_depth_density_antifacet"
SELECTION_BUDGET = "four_v63_distributed_recursive_bough_candidates_local_qa_then_priority_bc_two_gpu_remote"
ZOOM_DIVISOR = 2.10

V63_GRID = 288
V63_LEVEL = 0.424
V63_SIGMA = 0.78
V63_JUNCTION_RADIUS_BOOST = 1.16
V63_JUNCTION_NEIGHBOR_RADIUS_BOOST = 1.045


def _mutate_controls_for_v63(controls: Dict) -> None:
    v59._mutate_controls_for_v59(controls)
    controls["surface_strategy"] = SURFACE_STRATEGY
    controls["v59_lsystem_branch_smooth_short_bough_yfork_naturalization"] = False
    controls["v63_lsystem_branch_distributed_recursive_bough_naturalization"] = True
    controls["masked_local_naturalization_target"] = "L-system distributed recursive bough with matched depth, density, and side-branch rhythm"
    controls["v63_failure_addressed"] = "V62 raised terminal/junction counts but compressed the hierarchy into thick terminal blobs; V63 distributes recursive side branches along the main axis."
    controls["v63_generator_policy"] = "restore distributed main-axis L-system branch layout while keeping anti-facet implicit field and graph-native taper"
    controls["v63_priority_cases"] = "B/C are priority for remote textured GLB if local white OBJ zoom shows visible recursive depth without hard inserted tubes."
    controls["target_silhouette"] = "single woody L-system branch with distributed recursive side branches, 12-20 readable terminals, and continuous saddle-neck Y-forks"
    controls["implicit_grid_resolution"] = V63_GRID
    controls["implicit_field_level"] = V63_LEVEL
    controls["gaussian_sigma"] = V63_SIGMA
    controls["junction_radius_boost"] = V63_JUNCTION_RADIUS_BOOST
    controls["junction_neighbor_radius_boost"] = V63_JUNCTION_NEIGHBOR_RADIUS_BOOST
    controls["sdedit_seam_backprojection_available"] = False


def _build_case_v63(seed: int, **kwargs) -> Tuple[pb.Mesh, Dict, Dict]:
    mesh, controls, grammar = v53._build_lsystem_branch_case(seed, **kwargs)
    _mutate_controls_for_v63(controls)
    grammar["grammar_guide"] = "v63_lsystem_branch_distributed_recursive_bough_lowcontrast_bark_guide"
    grammar["density_policy"] = "distributed main-axis side_depth=3 recursion; avoid compact terminal blob clusters and V41/V42 needle fragmentation"
    grammar["clean_export_policy"] = "fine clean export is downstream normalization, not a substitute for distributed branch grammar depth/density"
    return mesh, controls, grammar


def _spec_v63(
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
    _mutate_controls_for_v63(controls)
    spec = v59._spec_v59(
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
    spec["recursive_mode"] = "finite L-system distributed recursive bough with side branches and anti-facet shared-neck Y-forks"
    spec["grammar_guide"] = "v63_lsystem_branch_distributed_recursive_bough_lowcontrast_bark_guide"
    spec["case_role"] = "v63_lsystem_branch_distributed_recursive_bough_naturalization"
    spec["qa_priority"] = "publication_grade_lsystem_depth_density_distributed_sidebranches_no_sparse_v61_no_blobbed_v62_no_inserted_tube"
    spec["operators"] = list(spec["operators"]) + [
        "distributed_main_axis_side_branch_restore",
        "recursive_depth_density_restore",
        "anti_blob_terminal_cluster_gate",
        "priority_bc_distributed_remote_candidate_gate",
    ]
    spec["operator_composition"] = " -> ".join(spec["operators"])
    _mutate_controls_for_v63(spec["controls"])
    return spec


def _case_specs_v63(seed: int) -> List[Dict]:
    settings = [
        ("V63_lsys_branch_distributed_depth_A", 4, 63001, 8, 3, 2, True, 0.28, 0.56, 0.78, 0.0288, 0.802, 0.0056, 0.118, 0.280, 0.640, 0.064, 8, 0, 0, 0, 0, 0, 0, 0, 0.46, 0.38, "soft_bark", "V63 A: distributed graph scout with side_depth=3 and anti-facet field"),
        ("V63_lsys_branch_distributed_dense_B", 5, 63002, 9, 3, 2, True, 0.31, 0.60, 0.82, 0.0292, 0.798, 0.0057, 0.116, 0.282, 0.630, 0.063, 8, 0, 0, 0, 0, 0, 0, 0, 0.48, 0.40, "lowcontrast_cambium", "V63 dense B: priority case, distributed recursive depth/density closest to the traditional L-system branch rhythm"),
        ("V63_lsys_branch_balanced_fan_C", 4, 63003, 8, 3, 2, True, 0.24, 0.64, 0.86, 0.0284, 0.808, 0.0055, 0.112, 0.276, 0.650, 0.064, 8, 0, 0, 0, 0, 0, 0, 0, 0.46, 0.38, "muted_cedar", "V63 balanced C: priority case, wider side-branch spread for clearer visible recursive structure"),
        ("V63_lsys_branch_lowfrag_depth_D", 5, 63004, 9, 2, 2, True, 0.22, 0.54, 0.76, 0.0280, 0.812, 0.0054, 0.110, 0.270, 0.660, 0.066, 7, 0, 0, 0, 0, 0, 0, 0, 0.42, 0.34, "matte_sapwood", "V63 lowfrag D: topology/texture fallback with distributed graph but milder side depth"),
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
        mesh, controls, grammar = _build_case_v63(
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
            _spec_v63(
                case_id=case_id,
                mesh=mesh,
                controls=controls,
                grammar=grammar,
                guide_key=guide_key,
                gpu=gpu,
                seed=seed + offset,
                root_variant=case_id.replace("V63_", ""),
                parameter_variant=(
                    f"main{main_steps}_sideD{side_depth}_every{side_every}_double{int(double_sides)}"
                    f"_distributed_grid{V63_GRID}_sigma{V63_SIGMA:.2f}_base{base_radius:.3f}"
                ),
                reason=reason,
            )
        )
    return rows


def _metadata_for_v63(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    metadata = v59._metadata_for_v59(spec, mesh_path, guide_path, metrics)
    _mutate_controls_for_v63(metadata["controls"])
    metadata["root_selection_log"]["root_source_type"] = "V63_lsystem_branch_distributed_recursive_bough_naturalization_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V63_lsystem_branch_distributed_recursive_bough_20260512.py"
    metadata["case_role"] = "v63_lsystem_branch_distributed_recursive_bough_naturalization"
    old_contract = metadata.pop("v59_lsystem_branch_naturalization_contract", {})
    metadata["v63_lsystem_branch_naturalization_contract"] = {
        "target_failure": "V62 had strong junction/terminal counts but its compact short-bough graph packed recursive side branches into terminal blobs.",
        "geometry_operator": "V53 distributed side-branch graph plus V59 anti-facet implicit field and V62 depth/density gates.",
        "carried_v59_evidence": old_contract,
        "antifacet_constants": {
            "implicit_grid_resolution": V63_GRID,
            "implicit_field_level": V63_LEVEL,
            "gaussian_sigma": V63_SIGMA,
            "junction_radius_boost": V63_JUNCTION_RADIUS_BOOST,
            "junction_neighbor_radius_boost": V63_JUNCTION_NEIGHBOR_RADIUS_BOOST,
        },
        "clean_export_plan": {
            "downstream_script": "assets/postprocess_v62_lsystem_branch_clean_export_20260512.py or V63 clone after remote textured GLB",
            "voxel_size_target": 0.0060,
            "smooth_iters_target": 2,
            "smooth_factor_target": 0.035,
            "merge_distance_target": 0.00030,
        },
        "sdedit_seam_backprojection_available": False,
        "post_glb_acceptance": "paper candidate only if GLB white zoom keeps distributed L-system depth/density without hard junction tubes or V62 terminal blobs.",
    }
    metadata["v63_remote_cache_policy"] = metadata.pop("v59_remote_cache_policy", {})
    return metadata


def _install_v63_overrides() -> None:
    v59._install_v59_overrides()
    # V59 installs the compact V58 graph.  V63 intentionally restores V53's
    # distributed main-axis graph, while retaining the V59 anti-facet field.
    v53._lsystem_branch_graph_v53 = v58._ORIG_GRAPH
    v53._branch_radii_v53 = v58._ORIG_RADII
    v53.IMPLICIT_GRID_RESOLUTION = V63_GRID
    v53.IMPLICIT_FIELD_LEVEL = V63_LEVEL
    v53.IMPLICIT_GAUSSIAN_SIGMA = V63_SIGMA
    v53.JUNCTION_RADIUS_BOOST = V63_JUNCTION_RADIUS_BOOST
    v53.JUNCTION_NEIGHBOR_RADIUS_BOOST = V63_JUNCTION_NEIGHBOR_RADIUS_BOOST
    v53._write_guides = v59._write_guides_v59
    v53._case_specs = _case_specs_v63
    v53._metadata_for = _metadata_for_v63
    v53.SURFACE_STRATEGY = SURFACE_STRATEGY
    v53.SELECTION_BUDGET = SELECTION_BUDGET


def _restore_v63_overrides() -> None:
    v59._restore_v59_overrides()


def _rewrite_v63_outputs(out_dir: Path, summary: Dict) -> Dict:
    manifest_json = out_dir / "manifest.json"
    manifest_csv = out_dir / "manifest.csv"
    if manifest_json.exists():
        rows = json.loads(manifest_json.read_text(encoding="utf-8"))
        for row in rows:
            controls = json.loads(row["controls"])
            _mutate_controls_for_v63(controls)
            row["controls"] = json.dumps(controls, ensure_ascii=False, sort_keys=True)
            row["case_role"] = "v63_lsystem_branch_distributed_recursive_bough_naturalization"
            row["grammar_guide"] = "v63_lsystem_branch_distributed_recursive_bough_lowcontrast_bark_guide"
            row["selection_budget"] = SELECTION_BUDGET
            row["surface_strategy"] = SURFACE_STRATEGY
        manifest_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        if manifest_csv.exists() and rows:
            with manifest_csv.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

    source_zoom = out_dir / "V53_obj_zoom_manifest_junctiontarget_20260511.json"
    new_zoom = out_dir / "V63_obj_zoom_manifest_junctiontarget_20260512.json"
    if source_zoom.exists():
        data = json.loads(source_zoom.read_text(encoding="utf-8"))
        for item in data.get("cases", []):
            item["zoom_divisor"] = ZOOM_DIVISOR
            item["detail_target_source"] = "v63_lsystem_explicit_distributed_recursive_bough_mask"
        new_zoom.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        source_zoom.unlink()

    summary.update(
        {
            "out_dir": str(out_dir),
            "surface_generator": "strict_visual_matched_cases_V63_lsystem_branch_distributed_recursive_bough_naturalization",
            "surface_strategy": SURFACE_STRATEGY,
            "selection_budget": SELECTION_BUDGET,
            "obj_zoom_manifest": str(new_zoom),
            "priority_cases_for_remote_if_obj_qa_passes": [
                "V63_lsys_branch_distributed_dense_B",
                "V63_lsys_branch_balanced_fan_C",
            ],
            "do_not_launch_remote_before_local_visual_qa": True,
        }
    )
    summary["lsystem_branch_gate"]["mask_scope"] = "object_space_distributed_recursive_bough_side_yfork_bands_only_antifacet"
    summary["lsystem_branch_gate"]["min_target_terminals_for_visual_qa"] = 12
    summary["lsystem_branch_gate"]["target_terminal_range"] = "12-20 readable terminals before texturing; prefer distributed visible terminals after GLB"
    summary["lsystem_branch_gate"]["target_branch_junctions_min"] = 10
    summary["post_glb_target_floor"]["visual_gate"] = "GLB white zoom must preserve clean support and show distributed L-system recursive depth/density without V62 terminal blobs"
    summary["v63_design"] = {
        "generator_change_required": True,
        "why_not_postprocess_only": "V62's residual failure is graph layout compaction; postprocess cannot unfold terminal clusters into distributed recursion.",
        "downstream_clean_export": "assets/postprocess_v62_lsystem_branch_clean_export_20260512.py or versioned V63 clone after remote GLB",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V63 L-system Distributed Recursive-Bough Dry Run\n\n"
        "V63 restores the distributed V53 L-system graph while retaining the V59 anti-facet implicit field. "
        "It is the visual-layout correction to V62: same depth/density target, but branches are spread along the main axis instead of packed into terminal blobs. "
        "No 2D seam inpaint/backprojection claim is made.\n",
        encoding="utf-8",
    )
    return summary


def materialize(root: Path, out_dir: Path, seed: int = 20260511, case_limit: Optional[int] = None) -> Dict:
    _install_v63_overrides()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            summary = v53.materialize(root, out_dir, seed=seed, case_limit=case_limit)
        summary = _rewrite_v63_outputs(out_dir, summary)
    finally:
        _restore_v63_overrides()
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
