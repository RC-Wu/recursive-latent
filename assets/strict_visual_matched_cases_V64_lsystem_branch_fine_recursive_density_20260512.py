#!/usr/bin/env python3
"""V64 fine-recursive L-system branch candidates.

V63 closed the post-GLB connectivity metrics, but its white renders still read
as a sparse branch with large terminal bulbs. V64 keeps the distributed V63
graph family and anti-facet implicit field, then makes the publication target
more explicit: finer recursive depth/density, smaller terminal caps, and zoom
targets at interior Y-forks rather than exposed ends.

The claim remains object-space grammar-owned naturalization. No 2D SDEdit,
inpaint, UV seam patch, or backprojection pipeline is claimed.
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

import strict_visual_matched_cases_V63_lsystem_branch_distributed_recursive_bough_20260512 as v63


v53 = v63.v53
v58 = v63.v58
v59 = v63.v59
pb = v63.pb

REMOTE_TARGET = v63.REMOTE_TARGET
ALLOWED_GPUS = v63.ALLOWED_GPUS
DEFAULT_ACTIVE_GPUS = v63.DEFAULT_ACTIVE_GPUS
REMOTE_STORAGE_ROOT = v63.REMOTE_STORAGE_ROOT
STORAGE_LIMIT_GB = v63.STORAGE_LIMIT_GB
CONNECTIVITY_LCR_MIN = v63.CONNECTIVITY_LCR_MIN
EXTERNAL_SUPPORT_MAX_SEGMENT_GATE = v63.EXTERNAL_SUPPORT_MAX_SEGMENT_GATE
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V64_lsystem_branch_fine_recursive_density_20260512_dryrun"

SURFACE_STRATEGY = "v64_lsystem_branch_fine_recursive_density_small_terminal_antiblob"
SELECTION_BUDGET = "four_v64_fine_recursive_density_candidates_local_qa_then_priority_bc_two_gpu_remote"
ZOOM_DIVISOR = 2.24

V64_GRID = 304
V64_LEVEL = 0.428
V64_SIGMA = 0.82
V64_JUNCTION_RADIUS_BOOST = 1.11
V64_JUNCTION_NEIGHBOR_RADIUS_BOOST = 1.032


def _mutate_controls_for_v64(controls: Dict) -> None:
    v63._mutate_controls_for_v63(controls)
    controls["surface_strategy"] = SURFACE_STRATEGY
    controls["v63_lsystem_branch_distributed_recursive_bough_naturalization"] = False
    controls["v64_lsystem_branch_fine_recursive_density_naturalization"] = True
    controls["masked_local_naturalization_target"] = "L-system fine recursive density with small terminals and interior Y-fork zooms"
    controls["v64_failure_addressed"] = (
        "V63 had clean connectivity and acceptable saddle continuity, but GLB white zoom was dominated by sparse branches "
        "and large pear-shaped terminal bulbs rather than L-system-like recursive depth/density."
    )
    controls["v64_generator_policy"] = "increase visible branch depth/density while shrinking terminal caps and keeping distributed side-branch layout"
    controls["v64_priority_cases"] = "B/C are priority for remote textured GLB only if local OBJ overview shows dense recursive side branches without terminal blobs."
    controls["target_silhouette"] = "dense recursive L-system side-branch family with many fine terminals and non-dominant small tapered tips"
    controls["implicit_grid_resolution"] = V64_GRID
    controls["implicit_field_level"] = V64_LEVEL
    controls["gaussian_sigma"] = V64_SIGMA
    controls["junction_radius_boost"] = V64_JUNCTION_RADIUS_BOOST
    controls["junction_neighbor_radius_boost"] = V64_JUNCTION_NEIGHBOR_RADIUS_BOOST
    controls["sdedit_seam_backprojection_available"] = False


def _branch_radii_v64(
    parents: List[int],
    *,
    base: float,
    taper: float,
    floor: float,
    terminal_shrink: float,
    tip_parent_shrink: float,
    high_depth_shrink: float,
) -> List[float]:
    """Thin terminal neighborhoods more aggressively than V53/V63."""
    radii = v58._ORIG_RADII(
        parents,
        base=base,
        taper=taper,
        floor=floor,
        terminal_shrink=terminal_shrink,
        tip_parent_shrink=tip_parent_shrink,
        high_depth_shrink=high_depth_shrink,
    )
    child_map = v53.v22._children(parents)
    terminals = set(v53.v27._terminal_nodes(parents))
    lineage = v53._terminal_lineage(parents, hops=8)
    depths = v53.bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    out: List[float] = []
    for idx, radius in enumerate(radii):
        t = depths[idx] / max(float(max_depth), 1.0)
        value = float(radius)
        if idx in terminals:
            value = max(float(floor) * 0.34, value * 0.58)
        elif idx in lineage:
            dist = int(lineage[idx])
            value *= min(1.0, 0.62 + 0.045 * dist)
        if len(child_map.get(idx, [])) <= 1 and t > 0.50:
            value *= 0.80
        out.append(max(float(floor) * 0.30, value))
    return out


def _build_case_v64(seed: int, **kwargs) -> Tuple[pb.Mesh, Dict, Dict]:
    mesh, controls, grammar = v63._build_case_v63(seed, **kwargs)
    _mutate_controls_for_v64(controls)
    grammar["grammar_guide"] = "v64_lsystem_branch_fine_recursive_density_lowcontrast_bark_guide"
    grammar["density_policy"] = "increase readable recursive depth/density and terminal count while shrinking exposed terminal bulbs"
    grammar["zoom_policy"] = "interior Y-fork targets only; terminal caps are excluded from primary zoom evidence"
    return mesh, controls, grammar


def _spec_v64(
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
    _mutate_controls_for_v64(controls)
    spec = v63._spec_v63(
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
    spec["recursive_mode"] = "finite L-system fine recursive branch with dense side-branch hierarchy and small graph-native terminals"
    spec["grammar_guide"] = "v64_lsystem_branch_fine_recursive_density_lowcontrast_bark_guide"
    spec["case_role"] = "v64_lsystem_branch_fine_recursive_density_naturalization"
    spec["qa_priority"] = "publication_grade_lsystem_depth_density_small_terminals_no_v63_pear_bulb_no_baseline_open_tubes"
    spec["operators"] = list(spec["operators"]) + [
        "fine_recursive_density_restore",
        "small_terminal_antiblob_radius_gate",
        "interior_yfork_zoom_target_gate",
    ]
    spec["operator_composition"] = " -> ".join(spec["operators"])
    _mutate_controls_for_v64(spec["controls"])
    return spec


def _case_specs_v64(seed: int) -> List[Dict]:
    settings = [
        ("V64_lsys_branch_fine_recursive_A", 4, 64001, 10, 4, 2, True, 0.29, 0.67, 0.78, 0.0238, 0.812, 0.0044, 0.062, 0.198, 0.555, 0.052, 11, 0, 0, 0, 0, 0, 0, 0, 0.36, 0.31, "soft_bark", "V64 A: finer recursion scout, lower terminal radius and more interior Y-forks"),
        ("V64_lsys_branch_dense_feather_B", 5, 64002, 11, 4, 2, True, 0.32, 0.70, 0.82, 0.0242, 0.806, 0.0043, 0.058, 0.190, 0.540, 0.050, 12, 0, 0, 0, 0, 0, 0, 0, 0.38, 0.33, "lowcontrast_cambium", "V64 dense B: priority, highest visible recursive density without terminal bulbs"),
        ("V64_lsys_branch_balanced_fine_C", 4, 64003, 10, 4, 2, True, 0.26, 0.72, 0.86, 0.0232, 0.818, 0.0042, 0.056, 0.188, 0.560, 0.050, 12, 0, 0, 0, 0, 0, 0, 0, 0.36, 0.31, "muted_cedar", "V64 balanced C: priority, wider recursive side-branch fan and small terminals"),
        ("V64_lsys_branch_lowfrag_fine_D", 5, 64004, 10, 3, 2, True, 0.24, 0.66, 0.78, 0.0228, 0.824, 0.0042, 0.054, 0.184, 0.575, 0.052, 10, 0, 0, 0, 0, 0, 0, 0, 0.34, 0.29, "matte_sapwood", "V64 lowfrag D: topology fallback with fine terminals but milder side depth"),
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
        mesh, controls, grammar = _build_case_v64(
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
            _spec_v64(
                case_id=case_id,
                mesh=mesh,
                controls=controls,
                grammar=grammar,
                guide_key=guide_key,
                gpu=gpu,
                seed=seed + offset,
                root_variant=case_id.replace("V64_", ""),
                parameter_variant=(
                    f"main{main_steps}_sideD{side_depth}_every{side_every}_double{int(double_sides)}"
                    f"_fine_grid{V64_GRID}_sigma{V64_SIGMA:.2f}_tip{terminal_shrink:.3f}"
                ),
                reason=reason,
            )
        )
    return rows


def _metadata_for_v64(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    metadata = v63._metadata_for_v63(spec, mesh_path, guide_path, metrics)
    _mutate_controls_for_v64(metadata["controls"])
    metadata["root_selection_log"]["root_source_type"] = "V64_lsystem_branch_fine_recursive_density_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V64_lsystem_branch_fine_recursive_density_20260512.py"
    metadata["case_role"] = "v64_lsystem_branch_fine_recursive_density_naturalization"
    old_contract = metadata.pop("v63_lsystem_branch_naturalization_contract", {})
    metadata["v64_lsystem_branch_naturalization_contract"] = {
        "target_failure": "V63 was connected and clean but still too sparse, with large pear-shaped terminal bulbs in white zoom.",
        "geometry_operator": "V63 distributed graph plus deeper side recursion, smaller terminal radius gate, and interior Y-fork zoom targets.",
        "carried_v63_evidence": old_contract,
        "antifacet_constants": {
            "implicit_grid_resolution": V64_GRID,
            "implicit_field_level": V64_LEVEL,
            "gaussian_sigma": V64_SIGMA,
            "junction_radius_boost": V64_JUNCTION_RADIUS_BOOST,
            "junction_neighbor_radius_boost": V64_JUNCTION_NEIGHBOR_RADIUS_BOOST,
        },
        "sdedit_seam_backprojection_available": False,
        "post_glb_acceptance": "paper candidate only if GLB white overview approaches baseline recursion density while zooms avoid open tubes and terminal bulbs.",
    }
    return metadata


def _install_v64_overrides() -> None:
    v63._install_v63_overrides()
    v53._branch_radii_v53 = _branch_radii_v64
    v53.IMPLICIT_GRID_RESOLUTION = V64_GRID
    v53.IMPLICIT_FIELD_LEVEL = V64_LEVEL
    v53.IMPLICIT_GAUSSIAN_SIGMA = V64_SIGMA
    v53.JUNCTION_RADIUS_BOOST = V64_JUNCTION_RADIUS_BOOST
    v53.JUNCTION_NEIGHBOR_RADIUS_BOOST = V64_JUNCTION_NEIGHBOR_RADIUS_BOOST
    v53._case_specs = _case_specs_v64
    v53._metadata_for = _metadata_for_v64
    v53.SURFACE_STRATEGY = SURFACE_STRATEGY
    v53.SELECTION_BUDGET = SELECTION_BUDGET


def _restore_v64_overrides() -> None:
    v63._restore_v63_overrides()


def _rewrite_v64_outputs(out_dir: Path, summary: Dict) -> Dict:
    manifest_json = out_dir / "manifest.json"
    manifest_csv = out_dir / "manifest.csv"
    if manifest_json.exists():
        rows = json.loads(manifest_json.read_text(encoding="utf-8"))
        for row in rows:
            controls = json.loads(row["controls"])
            _mutate_controls_for_v64(controls)
            row["controls"] = json.dumps(controls, ensure_ascii=False, sort_keys=True)
            row["case_role"] = "v64_lsystem_branch_fine_recursive_density_naturalization"
            row["grammar_guide"] = "v64_lsystem_branch_fine_recursive_density_lowcontrast_bark_guide"
            row["selection_budget"] = SELECTION_BUDGET
            row["surface_strategy"] = SURFACE_STRATEGY
        manifest_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        if manifest_csv.exists() and rows:
            with manifest_csv.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

    source_zoom = out_dir / "V53_obj_zoom_manifest_junctiontarget_20260511.json"
    inherited_zoom = out_dir / "V63_obj_zoom_manifest_junctiontarget_20260512.json"
    new_zoom = out_dir / "V64_obj_zoom_manifest_junctiontarget_20260512.json"
    if inherited_zoom.exists():
        source_zoom = inherited_zoom
    if source_zoom.exists():
        data = json.loads(source_zoom.read_text(encoding="utf-8"))
        for item in data.get("cases", []):
            item["zoom_divisor"] = ZOOM_DIVISOR
            item["detail_target_source"] = "v64_lsystem_explicit_fine_recursive_interior_yfork_mask"
            if item.get("fixed_detail_targets") and len(item["fixed_detail_targets"]) >= 2:
                item["fixed_detail_targets"] = item["fixed_detail_targets"][:2]
        new_zoom.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        if source_zoom != new_zoom:
            source_zoom.unlink()

    summary.update(
        {
            "out_dir": str(out_dir),
            "surface_generator": "strict_visual_matched_cases_V64_lsystem_branch_fine_recursive_density_naturalization",
            "surface_strategy": SURFACE_STRATEGY,
            "selection_budget": SELECTION_BUDGET,
            "obj_zoom_manifest": str(new_zoom),
            "priority_cases_for_remote_if_obj_qa_passes": [
                "V64_lsys_branch_dense_feather_B",
                "V64_lsys_branch_balanced_fine_C",
            ],
            "do_not_launch_remote_before_local_visual_qa": True,
        }
    )
    summary["lsystem_branch_gate"]["mask_scope"] = "object_space_fine_recursive_side_yfork_bands_small_terminal_antiblob"
    summary["lsystem_branch_gate"]["min_target_terminals_for_visual_qa"] = 18
    summary["lsystem_branch_gate"]["target_terminal_range"] = "18-32 readable fine terminals before texturing; prefer distributed visible terminals after GLB"
    summary["lsystem_branch_gate"]["target_branch_junctions_min"] = 14
    summary["post_glb_target_floor"]["visual_gate"] = "GLB white overview must show L-system-like recursive density; zooms must avoid open tubes, terminal bulbs, and hard inserted side branches"
    summary["v64_design"] = {
        "generator_change_required": True,
        "why_not_v63": "V63's metrics were clean but visual density remained below the traditional L-system baseline and terminal bulbs dominated zooms.",
        "remote_launch_gate": "Only B/C launch after OBJ contact sheet shows denser recursive hierarchy without terminal blob clusters.",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V64 L-system Fine Recursive Density Dry Run\n\n"
        "V64 keeps V63's distributed branch family but shifts toward the user's latest target: depth/density comparable to the traditional L-system baseline, "
        "small terminals, and interior Y-fork zoom evidence. No 2D seam inpaint/backprojection claim is made.\n",
        encoding="utf-8",
    )
    return summary


def materialize(root: Path, out_dir: Path, seed: int = 20260512, case_limit: Optional[int] = None) -> Dict:
    _install_v64_overrides()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            summary = v53.materialize(root, out_dir, seed=seed, case_limit=case_limit)
        summary = _rewrite_v64_outputs(out_dir, summary)
    finally:
        _restore_v64_overrides()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("RGG_ROOT", ROOT_DIR)))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260512)
    parser.add_argument("--case-limit", type=int, default=None)
    args = parser.parse_args()
    materialize(args.root, args.out, seed=args.seed, case_limit=args.case_limit)


if __name__ == "__main__":
    main()
