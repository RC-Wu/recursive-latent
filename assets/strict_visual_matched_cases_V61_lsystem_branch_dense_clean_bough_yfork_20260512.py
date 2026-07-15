#!/usr/bin/env python3
"""V61 L-system dense clean-bough Y-fork naturalization inputs.

V60 is the cleanest export fallback, but it is too sparse for the strict
branch-with-side-branches comparison.  V61 keeps the V58/V59 compact bough
root family and V59 anti-facet implicit field, then restores one controlled
layer of recursive side-branch density before the V60-style clean export pass.

The claim remains object-space and grammar-owned: no 2D seam inpaint,
SDEdit/backprojection, or UV patching pipeline is claimed.
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

import strict_visual_matched_cases_V53_lsystem_branch_natural_bough_graph_yfork_20260511 as v53
import strict_visual_matched_cases_V58_lsystem_branch_short_bough_yfork_20260511 as v58
import strict_visual_matched_cases_V59_lsystem_branch_smooth_short_bough_yfork_20260511 as v59


pb = v58.pb

REMOTE_TARGET = v59.REMOTE_TARGET
ALLOWED_GPUS = v59.ALLOWED_GPUS
DEFAULT_ACTIVE_GPUS = v59.DEFAULT_ACTIVE_GPUS
REMOTE_STORAGE_ROOT = v59.REMOTE_STORAGE_ROOT
STORAGE_LIMIT_GB = v59.STORAGE_LIMIT_GB
CONNECTIVITY_LCR_MIN = v59.CONNECTIVITY_LCR_MIN
EXTERNAL_SUPPORT_MAX_SEGMENT_GATE = v59.EXTERNAL_SUPPORT_MAX_SEGMENT_GATE
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V61_lsystem_branch_dense_clean_bough_yfork_20260512_dryrun"

SURFACE_STRATEGY = "v61_lsystem_branch_dense_clean_bough_yfork_generator_density_plus_antifacet"
SELECTION_BUDGET = "four_v61_dense_clean_bough_candidates_local_qa_then_priority_bc_two_gpu_remote"
ZOOM_DIVISOR = 1.72

V61_GRID = 288
V61_LEVEL = 0.424
V61_SIGMA = 0.78
V61_JUNCTION_RADIUS_BOOST = 1.18
V61_JUNCTION_NEIGHBOR_RADIUS_BOOST = 1.055


def _write_guides_v61(out_dir: Path) -> Dict[str, str]:
    guide_dir = out_dir / "_guides"
    guides: Dict[str, str] = {}
    palettes = {
        "matte_bark": [(84, 72, 54), (108, 88, 62), (132, 108, 78), (150, 128, 96)],
        "dense_sapwood": [(96, 80, 60), (120, 98, 72), (142, 118, 88), (160, 138, 106)],
        "balanced_cambium": [(90, 76, 58), (114, 94, 70), (136, 112, 84), (154, 132, 102)],
        "lowfrag_cedar": [(82, 68, 50), (104, 84, 60), (126, 104, 76), (144, 122, 92)],
    }
    for key, colors in palettes.items():
        path = guide_dir / f"V61_lsystem_branch_{key}_lowcontrast_guide.png"
        rng = np.random.default_rng(v53.v26._stable_seed(path.stem))
        img = v53.Image.new("RGB", (768, 768), (112, 94, 72))
        draw = v53.ImageDraw.Draw(img, "RGBA")
        for _ in range(80):
            color = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(-130, 898))
            y = int(rng.integers(-130, 898))
            r = int(rng.integers(125, 300))
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, int(rng.integers(12, 32))))
        img = img.filter(v53.ImageFilter.GaussianBlur(radius=30))
        draw = v53.ImageDraw.Draw(img, "RGBA")
        for _ in range(22):
            color = colors[int(rng.integers(0, len(colors)))]
            base = np.array([rng.integers(70, 700), rng.integers(115, 665)], dtype=float)
            length = float(rng.uniform(140, 285))
            angle = float(rng.uniform(-2.35, -0.66))
            pts = []
            for t in np.linspace(0.0, 1.0, 10):
                curve = math.sin(t * math.pi) * rng.uniform(-9, 10)
                p = base + np.array([math.cos(angle) * length * t + curve, math.sin(angle) * length * t], dtype=float)
                pts.append((int(p[0]), int(p[1])))
            draw.line(pts, fill=(*color, int(rng.integers(22, 44))), width=int(rng.integers(4, 8)))
            if rng.random() < 0.64:
                fork = pts[int(rng.integers(3, len(pts) - 2))]
                side_angle = float(angle + rng.choice([-1.0, 1.0]) * rng.uniform(0.46, 0.78))
                end = (
                    int(fork[0] + math.cos(side_angle) * length * rng.uniform(0.22, 0.38)),
                    int(fork[1] + math.sin(side_angle) * length * rng.uniform(0.22, 0.38)),
                )
                draw.line((fork, end), fill=(*color, int(rng.integers(18, 38))), width=int(rng.integers(2, 5)))
        path.parent.mkdir(parents=True, exist_ok=True)
        img.filter(v53.ImageFilter.SMOOTH_MORE).save(path)
        guides[key] = str(path)
    return guides


def _mutate_controls_for_v61(controls: Dict) -> None:
    v59._mutate_controls_for_v59(controls)
    controls["surface_strategy"] = SURFACE_STRATEGY
    controls["v59_lsystem_branch_smooth_short_bough_yfork_naturalization"] = False
    controls["v61_lsystem_branch_dense_clean_bough_yfork_naturalization"] = True
    controls["masked_local_naturalization_target"] = "L-system dense compact bough Y-fork bands with restored recursive side-branch density"
    controls["v60_failure_addressed"] = "V60 clean export removed micro artifacts and kept connectivity, but over-smoothed the input into a sparse smooth bough with insufficient recursive side-branch semantics."
    controls["v61_generator_policy"] = "restore one controlled recursive side-branch layer in the generator, then use fine object-space clean export only after OBJ white-zoom QA"
    controls["v61_priority_cases"] = "B/C are priority for remote textured GLB if local white OBJ zoom passes; D is topology-stable fallback."
    controls["target_silhouette"] = "compact woody bough with 6-9 readable side terminals and continuous shared-neck Y-forks"
    controls["implicit_grid_resolution"] = V61_GRID
    controls["implicit_field_level"] = V61_LEVEL
    controls["gaussian_sigma"] = V61_SIGMA
    controls["junction_radius_boost"] = V61_JUNCTION_RADIUS_BOOST
    controls["junction_neighbor_radius_boost"] = V61_JUNCTION_NEIGHBOR_RADIUS_BOOST
    controls["sdedit_seam_backprojection_available"] = False


def _build_case_v61(seed: int, **kwargs) -> Tuple[pb.Mesh, Dict, Dict]:
    mesh, controls, grammar = v58._build_case_v58(seed, **kwargs)
    _mutate_controls_for_v61(controls)
    grammar["grammar_guide"] = "v61_lsystem_branch_dense_clean_bough_lowcontrast_bark_guide"
    grammar["density_policy"] = "one controlled recursive side-branch layer; avoid V41/V42 thin needle fragmentation"
    grammar["clean_export_policy"] = "V60-style fine clean export is downstream normalization, not a substitute for branch grammar density"
    return mesh, controls, grammar


def _spec_v61(
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
    _mutate_controls_for_v61(controls)
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
    spec["recursive_mode"] = "finite L-system dense compact clean-bough with restored recursive side branches and shared-neck Y-forks"
    spec["grammar_guide"] = "v61_lsystem_branch_dense_clean_bough_lowcontrast_bark_guide"
    spec["case_role"] = "v61_lsystem_branch_dense_clean_bough_yfork_naturalization"
    spec["qa_priority"] = "publication_grade_branch_with_side_branches_no_sparse_v60_no_v41_needles_no_inserted_tube_junction"
    spec["operators"] = list(spec["operators"]) + [
        "controlled_recursive_side_branch_density_restore",
        "v60_fine_clean_export_ready_surface",
        "priority_bc_remote_candidate_gate",
    ]
    spec["operator_composition"] = " -> ".join(spec["operators"])
    _mutate_controls_for_v61(spec["controls"])
    return spec


def _case_specs_v61(seed: int) -> List[Dict]:
    settings = [
        ("V61_lsys_branch_asym_clean_A", 4, 61001, 6, 2, 2, True, 0.31, 0.54, 0.66, 0.0350, 0.856, 0.0062, 0.112, 0.280, 0.700, 0.058, 6, 0, 0, 0, 0, 0, 0, 0, 0.40, 0.32, "matte_bark", "V61 A: asymmetric dense clean-bough scout with one restored recursive side-branch layer"),
        ("V61_lsys_branch_dense_clean_B", 5, 61002, 6, 2, 2, True, 0.34, 0.58, 0.70, 0.0358, 0.850, 0.0063, 0.110, 0.280, 0.700, 0.058, 7, 0, 0, 0, 0, 0, 0, 0, 0.42, 0.34, "dense_sapwood", "V61 dense B: priority case, stronger side-branch read while preserving V59 anti-facet field and thick terminals"),
        ("V61_lsys_branch_balanced_clean_C", 4, 61003, 7, 2, 2, True, 0.29, 0.54, 0.66, 0.0346, 0.858, 0.0061, 0.108, 0.276, 0.710, 0.058, 7, 0, 0, 0, 0, 0, 0, 0, 0.40, 0.32, "balanced_cambium", "V61 balanced C: priority case, one extra main step for side-branch rhythm without returning to long-thin graph"),
        ("V61_lsys_branch_lowfrag_clean_D", 5, 61004, 6, 2, 3, True, 0.24, 0.50, 0.62, 0.0342, 0.866, 0.0060, 0.104, 0.270, 0.730, 0.060, 5, 0, 0, 0, 0, 0, 0, 0, 0.37, 0.29, "lowfrag_cedar", "V61 lowfrag D: topology fallback with one mirrored mid-step exit to keep terminal density above the visual gate"),
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
        mesh, controls, grammar = _build_case_v61(
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
            _spec_v61(
                case_id=case_id,
                mesh=mesh,
                controls=controls,
                grammar=grammar,
                guide_key=guide_key,
                gpu=gpu,
                seed=seed + offset,
                root_variant=case_id.replace("V61_", ""),
                parameter_variant=(
                    f"main{main_steps}_sideD{side_depth}_every{side_every}_double{int(double_sides)}"
                    f"_denseclean_grid{V61_GRID}_sigma{V61_SIGMA:.2f}_base{base_radius:.3f}"
                ),
                reason=reason,
            )
        )
    return rows


def _metadata_for_v61(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    metadata = v59._metadata_for_v59(spec, mesh_path, guide_path, metrics)
    _mutate_controls_for_v61(metadata["controls"])
    metadata["root_selection_log"]["root_source_type"] = "V61_lsystem_branch_dense_clean_bough_yfork_naturalization_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V61_lsystem_branch_dense_clean_bough_yfork_20260512.py"
    metadata["case_role"] = "v61_lsystem_branch_dense_clean_bough_yfork_naturalization"
    old_contract = metadata.pop("v59_lsystem_branch_naturalization_contract", {})
    metadata["v61_lsystem_branch_naturalization_contract"] = {
        "target_failure": "V60 clean export fixed surface artifacts but over-smoothed the candidate into a sparse branch with weak L-system side-branch semantics.",
        "geometry_operator": "V59 anti-facet compact bough field plus generator-side restoration of one controlled recursive side-branch layer.",
        "carried_v59_evidence": old_contract,
        "antifacet_constants": {
            "implicit_grid_resolution": V61_GRID,
            "implicit_field_level": V61_LEVEL,
            "gaussian_sigma": V61_SIGMA,
            "junction_radius_boost": V61_JUNCTION_RADIUS_BOOST,
            "junction_neighbor_radius_boost": V61_JUNCTION_NEIGHBOR_RADIUS_BOOST,
        },
        "clean_export_plan": {
            "downstream_script": "assets/postprocess_v61_lsystem_branch_clean_export_20260512.py",
            "voxel_size_target": 0.0065,
            "smooth_iters_target": 3,
            "smooth_factor_target": 0.04,
            "merge_distance_target": 0.00035,
        },
        "sdedit_seam_backprojection_available": False,
        "post_glb_acceptance": "paper candidate only if GLB white zoom keeps V60's clean single support while restoring branch-with-side-branches density.",
    }
    metadata["v61_remote_cache_policy"] = metadata.pop("v59_remote_cache_policy", {})
    return metadata


def _install_v61_overrides() -> None:
    v59._install_v59_overrides()
    v53.IMPLICIT_GRID_RESOLUTION = V61_GRID
    v53.IMPLICIT_FIELD_LEVEL = V61_LEVEL
    v53.IMPLICIT_GAUSSIAN_SIGMA = V61_SIGMA
    v53.JUNCTION_RADIUS_BOOST = V61_JUNCTION_RADIUS_BOOST
    v53.JUNCTION_NEIGHBOR_RADIUS_BOOST = V61_JUNCTION_NEIGHBOR_RADIUS_BOOST
    v53._write_guides = _write_guides_v61
    v53._case_specs = _case_specs_v61
    v53._metadata_for = _metadata_for_v61
    v53.SURFACE_STRATEGY = SURFACE_STRATEGY
    v53.SELECTION_BUDGET = SELECTION_BUDGET


def _restore_v61_overrides() -> None:
    v59._restore_v59_overrides()


def _rewrite_v61_outputs(out_dir: Path, summary: Dict) -> Dict:
    manifest_json = out_dir / "manifest.json"
    manifest_csv = out_dir / "manifest.csv"
    if manifest_json.exists():
        rows = json.loads(manifest_json.read_text(encoding="utf-8"))
        for row in rows:
            controls = json.loads(row["controls"])
            _mutate_controls_for_v61(controls)
            row["controls"] = json.dumps(controls, ensure_ascii=False, sort_keys=True)
            row["case_role"] = "v61_lsystem_branch_dense_clean_bough_yfork_naturalization"
            row["grammar_guide"] = "v61_lsystem_branch_dense_clean_bough_lowcontrast_bark_guide"
            row["selection_budget"] = SELECTION_BUDGET
            row["surface_strategy"] = SURFACE_STRATEGY
        manifest_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        if manifest_csv.exists() and rows:
            with manifest_csv.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

    source_zoom = out_dir / "V53_obj_zoom_manifest_junctiontarget_20260511.json"
    new_zoom = out_dir / "V61_obj_zoom_manifest_junctiontarget_20260512.json"
    if source_zoom.exists():
        data = json.loads(source_zoom.read_text(encoding="utf-8"))
        for item in data.get("cases", []):
            item["zoom_divisor"] = ZOOM_DIVISOR
            item["detail_target_source"] = "v61_lsystem_explicit_dense_clean_bough_yfork_mask"
        new_zoom.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        source_zoom.unlink()

    summary.update(
        {
            "out_dir": str(out_dir),
            "surface_generator": "strict_visual_matched_cases_V61_lsystem_branch_dense_clean_bough_yfork_naturalization",
            "surface_strategy": SURFACE_STRATEGY,
            "selection_budget": SELECTION_BUDGET,
            "obj_zoom_manifest": str(new_zoom),
            "priority_cases_for_remote_if_obj_qa_passes": [
                "V61_lsys_branch_dense_clean_B",
                "V61_lsys_branch_balanced_clean_C",
            ],
            "do_not_launch_remote_before_local_visual_qa": True,
        }
    )
    summary["lsystem_branch_gate"]["mask_scope"] = "object_space_dense_compact_bough_side_yfork_bands_only_antifacet"
    summary["lsystem_branch_gate"]["min_target_terminals_for_visual_qa"] = 8
    summary["post_glb_target_floor"]["visual_gate"] = "GLB white zoom must preserve clean single support and restore readable L-system side-branch density without V41/V42 needles"
    summary["v61_design"] = {
        "generator_change_required": True,
        "why_not_postprocess_only": "V60's residual failure is missing recursive branch semantics, not merely surface noise.",
        "downstream_clean_export": "assets/postprocess_v61_lsystem_branch_clean_export_20260512.py",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V61 L-system Dense Clean-Bough Y-Fork Dry Run\n\n"
        "V61 is the generator-density counterpart to V60 clean export. It restores one controlled recursive side-branch layer on top of the V58/V59 compact short-bough root, "
        "keeps the V59 anti-facet implicit field, and defers V60-style fine clean export until local white-background OBJ zoom passes visual QA. "
        "No 2D seam inpaint/backprojection claim is made.\n",
        encoding="utf-8",
    )
    return summary


def materialize(root: Path, out_dir: Path, seed: int = 20260511, case_limit: Optional[int] = None) -> Dict:
    _install_v61_overrides()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            summary = v53.materialize(root, out_dir, seed=seed, case_limit=case_limit)
        summary = _rewrite_v61_outputs(out_dir, summary)
    finally:
        _restore_v61_overrides()
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
