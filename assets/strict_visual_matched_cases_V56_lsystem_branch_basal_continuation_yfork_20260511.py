#!/usr/bin/env python3
"""V56 L-system branch basal-continuation Y-fork naturalization inputs.

V55 made the junction saddles less spherical, but the branch still failed the
white-background visual gate because the main branch start read as a visible
club-like endpoint. V56 keeps V55's elongated saddle field and changes only the
object-space grammar geometry: the branch is treated as a mid-bough segment by
adding a slim backward basal continuation before meshing. This keeps the
branch-with-side-branches target while preventing the rendered object from
being dominated by an artificial start cap.
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
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V56_lsystem_branch_basal_continuation_yfork_20260511_dryrun"

SURFACE_STRATEGY = "v56_lsystem_branch_basal_continuation_yfork_naturalization"
SELECTION_BUDGET = "four_v56_lsystem_branch_candidates_local_qa_then_two_gpu_remote"
ZOOM_DIVISOR = 2.05

_ORIGINAL_GRAPH = v54._lsystem_branch_graph_v54


def _lsystem_branch_graph_v56(seed: int, **kwargs) -> Tuple[List[np.ndarray], List[int], Dict]:
    nodes, parents, diag = _ORIGINAL_GRAPH(seed, **kwargs)
    child_map = v54.v22._children(parents)
    root_children = child_map.get(0, [])
    if root_children:
        main_child = max(
            root_children,
            key=lambda child: float(np.linalg.norm(np.asarray(nodes[child], dtype=float) - np.asarray(nodes[0], dtype=float))),
        )
        root = np.asarray(nodes[0], dtype=float)
        axis = v54.v22._unit(np.asarray(nodes[main_child], dtype=float) - root)
        if float(np.linalg.norm(axis)) < 1e-7:
            axis = np.array([1.0, 0.0, 0.0], dtype=float)
        u, _v, _w = v54.v22._basis(axis)
        direction = v54.v22._unit(-0.94 * axis + 0.045 * u)
        first = v54._append_node(nodes, parents, 0, root + direction * 0.130)
        second = v54._append_node(nodes, parents, first, np.asarray(nodes[first], dtype=float) + direction * 0.105)
        third = v54._append_node(nodes, parents, second, np.asarray(nodes[second], dtype=float) + direction * 0.075)
        diag["basal_continuation_node_count"] = 3
        diag["basal_continuation_policy"] = "slim backward mid-bough continuation hides artificial root cap"
        diag["graph_terminal_taper_count"] = int(diag.get("graph_terminal_taper_count", 0)) + 3
    else:
        diag["basal_continuation_node_count"] = 0
    diag["source"] = "custom_finite_lsystem_branch_with_basal_continuation_yforks"
    diag["target_silhouette"] = "mid-bough woody branch with recursive side branches and no exposed club-like start cap"
    return nodes, parents, diag


def _mutate_controls_for_v56(controls: Dict) -> None:
    v55._mutate_controls_for_v55(controls)
    controls["surface_strategy"] = SURFACE_STRATEGY
    controls["v55_lsystem_branch_elongated_saddle_yfork_naturalization"] = False
    controls["v56_lsystem_branch_basal_continuation_yfork_naturalization"] = True
    controls["masked_local_naturalization_target"] = "L-system basal-continuation branch segment with elongated Y-fork saddle bands"
    controls["hard_tube_cap_mitigation"] = "V56 adds a slim backward basal continuation so the branch root is no longer a visible club-like terminal; elongated saddle field remains local"
    controls["v55_failure_addressed"] = "V55 reduced round collars but still showed a large club-like branch start and crop-edge-dominated closeups"
    controls["highres_smooth_yfork_zoom_target_policy"] = "explicit side-branch Y-fork pair with wider V56 zoom; basal continuation and terminal caps excluded"


def _build_case_v56(seed: int, **kwargs) -> Tuple[v54.pb.Mesh, Dict, Dict]:
    mesh, controls, grammar = v54._build_lsystem_branch_case(seed, **kwargs)
    _mutate_controls_for_v56(controls)
    grammar["grammar_guide"] = "v56_lsystem_branch_lowcontrast_bark_basal_continuation_guide"
    return mesh, controls, grammar


def _case_specs_v56(seed: int) -> List[Dict]:
    settings = [
        ("V56_lsys_branch_basal_continuation_yfork_A", 4, 56001, 7, 2, 2, False, 0.30, 0.57, 0.74, 0.0245, 0.790, 0.0044, 0.078, 0.225, 0.60, 0.064, 8, 2, 0, 0, 0, 0, 0, 0, 0.38, 0.30, "pale_cambium", "basal-continuation A: no exposed root cap, balanced side-branch silhouette"),
        ("V56_lsys_branch_basal_continuation_yfork_lowfrag_B", 5, 56002, 8, 2, 2, False, 0.25, 0.51, 0.70, 0.0238, 0.802, 0.0042, 0.072, 0.215, 0.66, 0.064, 8, 2, 0, 0, 0, 0, 0, 0, 0.34, 0.27, "pale_cambium", "basal-continuation lowfrag B: thinnest cap-safe branch"),
        ("V56_lsys_branch_basal_continuation_yfork_dense_C", 4, 56003, 7, 2, 2, False, 0.34, 0.60, 0.78, 0.0250, 0.785, 0.0045, 0.082, 0.235, 0.59, 0.062, 9, 2, 0, 0, 0, 0, 0, 0, 0.40, 0.32, "centered_bough", "basal-continuation dense C: stronger strict branch read without root club"),
        ("V56_lsys_branch_basal_continuation_yfork_slim_D", 5, 56004, 8, 2, 2, False, 0.22, 0.49, 0.66, 0.0232, 0.810, 0.0040, 0.068, 0.205, 0.70, 0.066, 7, 2, 0, 0, 0, 0, 0, 0, 0.32, 0.25, "pale_cambium", "basal-continuation slim D: conservative fallback against tube/cap artifacts"),
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
        mesh, controls, grammar = _build_case_v56(
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
                root_variant=case_id.replace("V56_", ""),
                parameter_variant=(
                    f"main{main_steps}_sideD{side_depth}_every{side_every}_basalcont"
                    f"_base{base_radius:.3f}_tip{terminal_shrink:.2f}_parent{tip_parent_shrink:.2f}"
                ),
                reason=reason,
            )
        )
    return rows


def _metadata_for_v56(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    metadata = v55._metadata_for_v55(spec, mesh_path, guide_path, metrics)
    _mutate_controls_for_v56(metadata["controls"])
    metadata["root_selection_log"]["root_source_type"] = "V56_lsystem_branch_basal_continuation_yfork_naturalization_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V56_lsystem_branch_basal_continuation_yfork_20260511.py"
    contract = metadata.pop("v55_lsystem_branch_naturalization_contract", {})
    contract["target_failure"] = "V55 reduced collar bulbs but retained a visible club-like start cap."
    contract["geometry_operator"] = "V55 elongated saddle field plus V56 graph-native backward basal continuation"
    contract["v56_visual_gate"] = "overview and zoom must not be dominated by an exposed root club, hard tube insertion, or crop-edge cut."
    metadata["v56_lsystem_branch_naturalization_contract"] = contract
    metadata["v56_remote_cache_policy"] = metadata.pop("v55_remote_cache_policy", {})
    return metadata


def _install_v56_overrides() -> None:
    v55._install_v55_overrides()
    v54._lsystem_branch_graph_v54 = _lsystem_branch_graph_v56
    v54._case_specs = _case_specs_v56
    v54._metadata_for = _metadata_for_v56


def _rewrite_v56_outputs(out_dir: Path, summary: Dict) -> Dict:
    manifest_json = out_dir / "manifest.json"
    manifest_csv = out_dir / "manifest.csv"
    if manifest_json.exists():
        rows = json.loads(manifest_json.read_text(encoding="utf-8"))
        for row in rows:
            controls = json.loads(row["controls"])
            _mutate_controls_for_v56(controls)
            row["controls"] = json.dumps(controls, ensure_ascii=False, sort_keys=True)
            row["case_role"] = "v56_lsystem_branch_basal_continuation_yfork_naturalization"
            row["grammar_guide"] = "v56_lsystem_branch_lowcontrast_bark_basal_continuation_guide"
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
    new_zoom = out_dir / "V56_obj_zoom_manifest_junctiontarget_20260511.json"
    source_zoom = v55_zoom if v55_zoom.exists() else old_zoom
    if source_zoom.exists():
        data = json.loads(source_zoom.read_text(encoding="utf-8"))
        for item in data.get("cases", []):
            item["zoom_divisor"] = ZOOM_DIVISOR
            item["detail_target_source"] = "v56_lsystem_explicit_side_yfork_basal_continuation_excluded"
        new_zoom.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        source_zoom.unlink()
    if old_zoom.exists():
        old_zoom.unlink()

    summary.update(
        {
            "out_dir": str(out_dir),
            "surface_generator": "strict_visual_matched_cases_V56_lsystem_branch_basal_continuation_yfork_naturalization",
            "surface_strategy": SURFACE_STRATEGY,
            "selection_budget": SELECTION_BUDGET,
            "obj_zoom_manifest": str(new_zoom),
        }
    )
    summary["lsystem_branch_gate"]["mask_scope"] = "object_space_basal_continuation_side_yfork_bands_only"
    summary["post_glb_target_floor"]["visual_gate"] = (
        "side-branch saddle zoom must read as continuous wood, with no exposed "
        "root club, round collar bulb, or crop-edge cut as the dominant feature"
    )
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V56 L-system Branch Basal-Continuation Y-Fork Dry Run\n\n"
        "V56 targets the remaining V55 visual failure: a club-like visible branch start. "
        "It adds a graph-native backward basal continuation before the V55 elongated saddle field, "
        "keeps terminal sleeves and 2D seam backprojection disabled, and widens local zoom before any remote GLB launch.\n",
        encoding="utf-8",
    )
    return summary


def materialize(root: Path, out_dir: Path, seed: int = 20260511, case_limit: Optional[int] = None) -> Dict:
    _install_v56_overrides()
    with contextlib.redirect_stdout(io.StringIO()):
        summary = v54.materialize(root, out_dir, seed=seed, case_limit=case_limit)
    summary = _rewrite_v56_outputs(out_dir, summary)
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
