#!/usr/bin/env python3
"""V57 L-system branch tapered-midbough Y-fork naturalization inputs.

V56 showed that adding basal continuation alone is not enough: the radius model
still creates exposed club-like ends. V57 changes the branch into a tapered
mid-bough segment by shrinking both low-depth and terminal exposed nodes while
keeping V55's elongated Y-fork saddle field. The goal is a visually continuous
wood branch, not a tube with a repaired endpoint.
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

import strict_visual_matched_cases_V55_lsystem_branch_elongated_saddle_yfork_20260511 as v55


v54 = v55.v54

REMOTE_TARGET = v55.REMOTE_TARGET
ALLOWED_GPUS = v55.ALLOWED_GPUS
DEFAULT_ACTIVE_GPUS = v55.DEFAULT_ACTIVE_GPUS
REMOTE_STORAGE_ROOT = v55.REMOTE_STORAGE_ROOT
STORAGE_LIMIT_GB = v55.STORAGE_LIMIT_GB
CONNECTIVITY_LCR_MIN = v55.CONNECTIVITY_LCR_MIN
EXTERNAL_SUPPORT_MAX_SEGMENT_GATE = v55.EXTERNAL_SUPPORT_MAX_SEGMENT_GATE
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V57_lsystem_branch_tapered_midbough_yfork_20260511_dryrun"

SURFACE_STRATEGY = "v57_lsystem_branch_tapered_midbough_yfork_naturalization"
SELECTION_BUDGET = "four_v57_lsystem_branch_candidates_local_qa_then_two_gpu_remote"
ZOOM_DIVISOR = 1.92

_ORIGINAL_BRANCH_RADII = v54._branch_radii_v54


def _branch_radii_v57(
    parents: List[int],
    *,
    base: float,
    taper: float,
    floor: float,
    terminal_shrink: float,
    tip_parent_shrink: float,
    high_depth_shrink: float,
) -> List[float]:
    depths = v54.bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    child_map = v54.v22._children(parents)
    terminals = set(v54.v27._terminal_nodes(parents))
    terminal_lineage = v54._terminal_lineage(parents, hops=6)
    radii: List[float] = []
    for idx, depth in enumerate(depths):
        t = depth / max(float(max_depth), 1.0)
        mid_mass = 0.76 + 0.24 * math.sin(math.pi * min(max(t, 0.0), 1.0))
        radius = float(base) * mid_mass * (float(taper) ** (depth * 0.34))
        if depth == 0:
            radius *= 0.34
        elif depth == 1:
            radius *= 0.48
        elif depth == 2:
            radius *= 0.64
        if len(child_map.get(idx, [])) >= 2 and depth > 1:
            radius *= 1.06
        if len(child_map.get(idx, [])) <= 1 and t > 0.30:
            radius *= 1.0 - (1.0 - float(high_depth_shrink)) * min((t - 0.30) / 0.70, 1.0)
        if idx in terminal_lineage and idx not in terminals:
            distance = terminal_lineage[idx]
            radius *= min(1.0, float(tip_parent_shrink) + 0.024 * distance)
        if idx in terminals:
            radius = max(float(floor) * 0.38, radius * float(terminal_shrink))
        else:
            radius = max(float(floor), radius)
        radii.append(float(radius))
    return radii


def _mutate_controls_for_v57(controls: Dict) -> None:
    v55._mutate_controls_for_v55(controls)
    controls["surface_strategy"] = SURFACE_STRATEGY
    controls["v55_lsystem_branch_elongated_saddle_yfork_naturalization"] = False
    controls["v57_lsystem_branch_tapered_midbough_yfork_naturalization"] = True
    controls["masked_local_naturalization_target"] = "L-system tapered mid-bough branch with elongated side-Y saddle bands"
    controls["support_cross_section"] = "two-ended tapered mid-bough with side-branch saddles"
    controls["hard_tube_cap_mitigation"] = "V57 replaces endpoint repair with a two-ended tapered mid-bough radius model: low-depth and terminal exposed nodes are both small, while mid-bough Y-forks retain wood mass"
    controls["v56_failure_addressed"] = "V56 basal continuation still left visible club-like end mass because the radius model was root-heavy"
    controls["highres_smooth_yfork_zoom_target_policy"] = "explicit side-branch Y-fork pair with wider V57 zoom; endpoints excluded"


def _build_case_v57(seed: int, **kwargs) -> Tuple[v54.pb.Mesh, Dict, Dict]:
    mesh, controls, grammar = v54._build_lsystem_branch_case(seed, **kwargs)
    _mutate_controls_for_v57(controls)
    grammar["grammar_guide"] = "v57_lsystem_branch_lowcontrast_bark_tapered_midbough_guide"
    return mesh, controls, grammar


def _case_specs_v57(seed: int) -> List[Dict]:
    settings = [
        ("V57_lsys_branch_tapered_midbough_yfork_A", 4, 57001, 7, 2, 2, False, 0.30, 0.57, 0.74, 0.0230, 0.812, 0.0039, 0.070, 0.215, 0.62, 0.062, 8, 2, 0, 0, 0, 0, 0, 0, 0.34, 0.27, "pale_cambium", "tapered-midbough A: balanced strict branch without club endpoints"),
        ("V57_lsys_branch_tapered_midbough_yfork_lowfrag_B", 5, 57002, 8, 2, 2, False, 0.25, 0.51, 0.69, 0.0220, 0.820, 0.0037, 0.064, 0.205, 0.68, 0.062, 8, 2, 0, 0, 0, 0, 0, 0, 0.30, 0.24, "pale_cambium", "tapered-midbough lowfrag B: thinnest conservative branch"),
        ("V57_lsys_branch_tapered_midbough_yfork_dense_C", 4, 57003, 7, 2, 2, False, 0.34, 0.60, 0.78, 0.0235, 0.806, 0.0040, 0.074, 0.225, 0.61, 0.060, 9, 2, 0, 0, 0, 0, 0, 0, 0.36, 0.29, "centered_bough", "tapered-midbough dense C: stronger side branches with endpoint taper"),
        ("V57_lsys_branch_tapered_midbough_yfork_slim_D", 5, 57004, 8, 2, 2, False, 0.22, 0.49, 0.66, 0.0214, 0.826, 0.0035, 0.060, 0.195, 0.72, 0.064, 7, 2, 0, 0, 0, 0, 0, 0, 0.28, 0.22, "pale_cambium", "tapered-midbough slim D: safest no-club topology fallback"),
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
        mesh, controls, grammar = _build_case_v57(
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
            v54._spec(
                case_id=case_id,
                mesh=mesh,
                controls=controls,
                grammar=grammar,
                guide_key=guide_key,
                gpu=gpu,
                seed=seed + offset,
                root_variant=case_id.replace("V57_", ""),
                parameter_variant=(
                    f"main{main_steps}_sideD{side_depth}_every{side_every}_midbough"
                    f"_base{base_radius:.3f}_tip{terminal_shrink:.2f}_parent{tip_parent_shrink:.2f}"
                ),
                reason=reason,
            )
        )
    return rows


def _metadata_for_v57(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    metadata = v55._metadata_for_v55(spec, mesh_path, guide_path, metrics)
    _mutate_controls_for_v57(metadata["controls"])
    metadata["root_selection_log"]["root_source_type"] = "V57_lsystem_branch_tapered_midbough_yfork_naturalization_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V57_lsystem_branch_tapered_midbough_yfork_20260511.py"
    contract = metadata.pop("v55_lsystem_branch_naturalization_contract", {})
    contract["target_failure"] = "V56/V55 retained exposed club-like ends because the radius model stayed root-heavy."
    contract["geometry_operator"] = "V55 elongated saddle field plus V57 tapered two-ended mid-bough radius model"
    contract["v57_visual_gate"] = "overview and zoom must read as a natural branch segment: no club endpoint, hard tube insertion, or crop-edge cut as the primary feature."
    metadata["v57_lsystem_branch_naturalization_contract"] = contract
    metadata["v57_remote_cache_policy"] = metadata.pop("v55_remote_cache_policy", {})
    return metadata


def _install_v57_overrides() -> None:
    v55._install_v55_overrides()
    v54._branch_radii_v54 = _branch_radii_v57
    v54._case_specs = _case_specs_v57
    v54._metadata_for = _metadata_for_v57


def _rewrite_v57_outputs(out_dir: Path, summary: Dict) -> Dict:
    manifest_json = out_dir / "manifest.json"
    manifest_csv = out_dir / "manifest.csv"
    if manifest_json.exists():
        rows = json.loads(manifest_json.read_text(encoding="utf-8"))
        for row in rows:
            controls = json.loads(row["controls"])
            _mutate_controls_for_v57(controls)
            row["controls"] = json.dumps(controls, ensure_ascii=False, sort_keys=True)
            row["case_role"] = "v57_lsystem_branch_tapered_midbough_yfork_naturalization"
            row["grammar_guide"] = "v57_lsystem_branch_lowcontrast_bark_tapered_midbough_guide"
            row["selection_budget"] = SELECTION_BUDGET
            row["surface_strategy"] = SURFACE_STRATEGY
        manifest_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        if manifest_csv.exists() and rows:
            with manifest_csv.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

    old_zoom = out_dir / "V54_obj_zoom_manifest_junctiontarget_20260511.json"
    v55_zoom = out_dir / "V55_obj_zoom_manifest_junctiontarget_20260511.json"
    new_zoom = out_dir / "V57_obj_zoom_manifest_junctiontarget_20260511.json"
    source_zoom = v55_zoom if v55_zoom.exists() else old_zoom
    if source_zoom.exists():
        data = json.loads(source_zoom.read_text(encoding="utf-8"))
        for item in data.get("cases", []):
            item["zoom_divisor"] = ZOOM_DIVISOR
            item["detail_target_source"] = "v57_lsystem_explicit_side_yfork_tapered_midbough"
        new_zoom.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        source_zoom.unlink()
    if old_zoom.exists():
        old_zoom.unlink()

    summary.update(
        {
            "out_dir": str(out_dir),
            "surface_generator": "strict_visual_matched_cases_V57_lsystem_branch_tapered_midbough_yfork_naturalization",
            "surface_strategy": SURFACE_STRATEGY,
            "selection_budget": SELECTION_BUDGET,
            "obj_zoom_manifest": str(new_zoom),
        }
    )
    summary["lsystem_branch_gate"]["mask_scope"] = "object_space_tapered_midbough_side_yfork_bands_only"
    summary["post_glb_target_floor"]["visual_gate"] = "natural branch segment with tapered endpoints and continuous side-Y saddle"
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V57 L-system Branch Tapered-Midbough Y-Fork Dry Run\n\n"
        "V57 targets the remaining V55/V56 visual failure: exposed club-like endpoints. "
        "It reuses the elongated saddle field but replaces the root-heavy radius schedule with a two-ended tapered mid-bough radius model. "
        "No terminal sleeves, no 2D seam backprojection, and no remote launch before local white-background QA.\n",
        encoding="utf-8",
    )
    return summary


def materialize(root: Path, out_dir: Path, seed: int = 20260511, case_limit: Optional[int] = None) -> Dict:
    _install_v57_overrides()
    with contextlib.redirect_stdout(io.StringIO()):
        summary = v54.materialize(root, out_dir, seed=seed, case_limit=case_limit)
    summary = _rewrite_v57_outputs(out_dir, summary)
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
