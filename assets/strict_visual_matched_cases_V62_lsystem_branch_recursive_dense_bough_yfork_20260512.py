#!/usr/bin/env python3
"""V62 L-system recursive dense-bough Y-fork naturalization inputs.

V61 is clean but still too sparse for the corrected strict L-system
branch-with-side-branches comparison. V62 keeps the V58/V59 compact bough
root family and V61 anti-facet field, then raises recursive branch depth,
side-branch density, and terminal count while preserving shared-neck Y-forks
and graph-native taper.

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
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V62_lsystem_branch_recursive_dense_bough_yfork_20260512_dryrun"

SURFACE_STRATEGY = "v62_lsystem_branch_recursive_dense_bough_yfork_depth_density_plus_antifacet"
SELECTION_BUDGET = "four_v62_recursive_dense_bough_candidates_local_qa_then_priority_bc_two_gpu_remote"
ZOOM_DIVISOR = 1.72

V62_GRID = 288
V62_LEVEL = 0.424
V62_SIGMA = 0.78
V62_JUNCTION_RADIUS_BOOST = 1.18
V62_JUNCTION_NEIGHBOR_RADIUS_BOOST = 1.055


def _write_guides_v62(out_dir: Path) -> Dict[str, str]:
    guide_dir = out_dir / "_guides"
    guides: Dict[str, str] = {}
    palettes = {
        "matte_bark": [(84, 72, 54), (108, 88, 62), (132, 108, 78), (150, 128, 96)],
        "dense_sapwood": [(96, 80, 60), (120, 98, 72), (142, 118, 88), (160, 138, 106)],
        "balanced_cambium": [(90, 76, 58), (114, 94, 70), (136, 112, 84), (154, 132, 102)],
        "lowfrag_cedar": [(82, 68, 50), (104, 84, 60), (126, 104, 76), (144, 122, 92)],
    }
    for key, colors in palettes.items():
        path = guide_dir / f"V62_lsystem_branch_{key}_lowcontrast_guide.png"
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


def _mutate_controls_for_v62(controls: Dict) -> None:
    v59._mutate_controls_for_v59(controls)
    controls["surface_strategy"] = SURFACE_STRATEGY
    controls["v59_lsystem_branch_smooth_short_bough_yfork_naturalization"] = False
    controls["v62_lsystem_branch_recursive_dense_bough_yfork_naturalization"] = True
    controls["masked_local_naturalization_target"] = "L-system recursive dense compact bough Y-fork bands with matched depth and side-branch density"
    controls["v62_failure_addressed"] = "V61 cleaned the bough and restored one layer, but still under-matches the traditional L-system baseline in depth, terminal count, and recursive side-branch density."
    controls["v62_generator_policy"] = "increase generator-side recursive depth/density first, then use fine object-space clean export only after OBJ white-zoom QA"
    controls["v62_priority_cases"] = "B/C are priority for remote textured GLB if local white OBJ zoom passes; A/D bracket density and topology stability."
    controls["target_silhouette"] = "compact woody recursive bough with 12-20 readable terminals, multi-level side forks, and continuous shared-neck Y-forks"
    controls["implicit_grid_resolution"] = V62_GRID
    controls["implicit_field_level"] = V62_LEVEL
    controls["gaussian_sigma"] = V62_SIGMA
    controls["junction_radius_boost"] = V62_JUNCTION_RADIUS_BOOST
    controls["junction_neighbor_radius_boost"] = V62_JUNCTION_NEIGHBOR_RADIUS_BOOST
    controls["sdedit_seam_backprojection_available"] = False


def _build_case_v62(seed: int, **kwargs) -> Tuple[pb.Mesh, Dict, Dict]:
    mesh, controls, grammar = v58._build_case_v58(seed, **kwargs)
    _mutate_controls_for_v62(controls)
    grammar["grammar_guide"] = "v62_lsystem_branch_recursive_dense_bough_lowcontrast_bark_guide"
    grammar["density_policy"] = "side_depth=3 recursive side-branch density; avoid V41/V42 thin needle fragmentation"
    grammar["clean_export_policy"] = "V60/V61-style fine clean export is downstream normalization, not a substitute for branch grammar depth/density"
    return mesh, controls, grammar


def _spec_v62(
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
    _mutate_controls_for_v62(controls)
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
    spec["grammar_guide"] = "v62_lsystem_branch_recursive_dense_bough_lowcontrast_bark_guide"
    spec["case_role"] = "v62_lsystem_branch_recursive_dense_bough_yfork_naturalization"
    spec["qa_priority"] = "publication_grade_branch_with_side_branches_depth_density_no_sparse_v61_no_v41_needles_no_inserted_tube_junction"
    spec["operators"] = list(spec["operators"]) + [
        "recursive_side_branch_depth_density_restore",
        "v61_v60_fine_clean_export_ready_surface",
        "priority_bc_dense_depth_remote_candidate_gate",
    ]
    spec["operator_composition"] = " -> ".join(spec["operators"])
    _mutate_controls_for_v62(spec["controls"])
    return spec


def _case_specs_v62(seed: int) -> List[Dict]:
    settings = [
        ("V62_lsys_branch_recursive_depth_A", 4, 62001, 7, 3, 2, True, 0.31, 0.56, 0.70, 0.0350, 0.856, 0.0062, 0.108, 0.282, 0.700, 0.058, 7, 0, 0, 0, 0, 0, 0, 0, 0.42, 0.34, "matte_bark", "V62 A: side_depth=3 recursive scout with compact bough silhouette and V61 anti-facet field"),
        ("V62_lsys_branch_recursive_dense_B", 5, 62002, 8, 3, 2, True, 0.34, 0.60, 0.74, 0.0356, 0.852, 0.0063, 0.106, 0.282, 0.690, 0.057, 8, 0, 0, 0, 0, 0, 0, 0, 0.43, 0.35, "dense_sapwood", "V62 dense B: priority case, L-system-like depth/density with side_depth=3 and thick readable terminals"),
        ("V62_lsys_branch_balanced_depth_C", 4, 62003, 8, 3, 2, True, 0.29, 0.55, 0.70, 0.0348, 0.858, 0.0062, 0.104, 0.276, 0.710, 0.058, 8, 0, 0, 0, 0, 0, 0, 0, 0.41, 0.33, "balanced_cambium", "V62 balanced C: priority case, dense recursive side-branch rhythm while avoiding long-thin graph return"),
        ("V62_lsys_branch_highdepth_lowfrag_D", 5, 62004, 7, 3, 2, True, 0.24, 0.52, 0.66, 0.0344, 0.866, 0.0061, 0.102, 0.270, 0.730, 0.060, 7, 0, 0, 0, 0, 0, 0, 0, 0.38, 0.30, "lowfrag_cedar", "V62 high-depth lowfrag D: topology fallback that keeps side_depth=3 density without V41/V42 needle read"),
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
        mesh, controls, grammar = _build_case_v62(
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
            _spec_v62(
                case_id=case_id,
                mesh=mesh,
                controls=controls,
                grammar=grammar,
                guide_key=guide_key,
                gpu=gpu,
                seed=seed + offset,
                root_variant=case_id.replace("V62_", ""),
                parameter_variant=(
                    f"main{main_steps}_sideD{side_depth}_every{side_every}_double{int(double_sides)}"
                    f"_recursivedense_grid{V62_GRID}_sigma{V62_SIGMA:.2f}_base{base_radius:.3f}"
                ),
                reason=reason,
            )
        )
    return rows


def _metadata_for_v62(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    metadata = v59._metadata_for_v59(spec, mesh_path, guide_path, metrics)
    _mutate_controls_for_v62(metadata["controls"])
    metadata["root_selection_log"]["root_source_type"] = "V62_lsystem_branch_recursive_dense_bough_yfork_naturalization_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V62_lsystem_branch_recursive_dense_bough_yfork_20260512.py"
    metadata["case_role"] = "v62_lsystem_branch_recursive_dense_bough_yfork_naturalization"
    old_contract = metadata.pop("v59_lsystem_branch_naturalization_contract", {})
    metadata["v62_lsystem_branch_naturalization_contract"] = {
        "target_failure": "V61 fixed cleanliness but remained sparse relative to the traditional L-system branch-with-side-branches baseline; V62 is the depth/density correction.",
        "geometry_operator": "V59/V61 anti-facet compact bough field plus generator-side restoration of side_depth=3 recursive branch hierarchy.",
        "carried_v59_evidence": old_contract,
        "antifacet_constants": {
            "implicit_grid_resolution": V62_GRID,
            "implicit_field_level": V62_LEVEL,
            "gaussian_sigma": V62_SIGMA,
            "junction_radius_boost": V62_JUNCTION_RADIUS_BOOST,
            "junction_neighbor_radius_boost": V62_JUNCTION_NEIGHBOR_RADIUS_BOOST,
        },
        "clean_export_plan": {
            "downstream_script": "assets/postprocess_v62_lsystem_branch_clean_export_20260512.py",
            "voxel_size_target": 0.0065,
            "smooth_iters_target": 3,
            "smooth_factor_target": 0.04,
            "merge_distance_target": 0.00035,
        },
        "sdedit_seam_backprojection_available": False,
        "post_glb_acceptance": "paper candidate only if GLB white zoom keeps clean single support while matching L-system depth/density and preserving natural branch junctions.",
    }
    metadata["v62_remote_cache_policy"] = metadata.pop("v59_remote_cache_policy", {})
    return metadata


def _install_v62_overrides() -> None:
    v59._install_v59_overrides()
    v53.IMPLICIT_GRID_RESOLUTION = V62_GRID
    v53.IMPLICIT_FIELD_LEVEL = V62_LEVEL
    v53.IMPLICIT_GAUSSIAN_SIGMA = V62_SIGMA
    v53.JUNCTION_RADIUS_BOOST = V62_JUNCTION_RADIUS_BOOST
    v53.JUNCTION_NEIGHBOR_RADIUS_BOOST = V62_JUNCTION_NEIGHBOR_RADIUS_BOOST
    v53._write_guides = _write_guides_v62
    v53._case_specs = _case_specs_v62
    v53._metadata_for = _metadata_for_v62
    v53.SURFACE_STRATEGY = SURFACE_STRATEGY
    v53.SELECTION_BUDGET = SELECTION_BUDGET


def _restore_v62_overrides() -> None:
    v59._restore_v59_overrides()


def _rewrite_v62_outputs(out_dir: Path, summary: Dict) -> Dict:
    manifest_json = out_dir / "manifest.json"
    manifest_csv = out_dir / "manifest.csv"
    if manifest_json.exists():
        rows = json.loads(manifest_json.read_text(encoding="utf-8"))
        for row in rows:
            controls = json.loads(row["controls"])
            _mutate_controls_for_v62(controls)
            row["controls"] = json.dumps(controls, ensure_ascii=False, sort_keys=True)
            row["case_role"] = "v62_lsystem_branch_recursive_dense_bough_yfork_naturalization"
            row["grammar_guide"] = "v62_lsystem_branch_recursive_dense_bough_lowcontrast_bark_guide"
            row["selection_budget"] = SELECTION_BUDGET
            row["surface_strategy"] = SURFACE_STRATEGY
        manifest_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        if manifest_csv.exists() and rows:
            with manifest_csv.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

    source_zoom = out_dir / "V53_obj_zoom_manifest_junctiontarget_20260511.json"
    new_zoom = out_dir / "V62_obj_zoom_manifest_junctiontarget_20260512.json"
    if source_zoom.exists():
        data = json.loads(source_zoom.read_text(encoding="utf-8"))
        for item in data.get("cases", []):
            item["zoom_divisor"] = ZOOM_DIVISOR
            item["detail_target_source"] = "v62_lsystem_explicit_recursive_dense_bough_yfork_mask"
        new_zoom.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        source_zoom.unlink()

    summary.update(
        {
            "out_dir": str(out_dir),
            "surface_generator": "strict_visual_matched_cases_V62_lsystem_branch_recursive_dense_bough_yfork_naturalization",
            "surface_strategy": SURFACE_STRATEGY,
            "selection_budget": SELECTION_BUDGET,
            "obj_zoom_manifest": str(new_zoom),
            "priority_cases_for_remote_if_obj_qa_passes": [
                "V62_lsys_branch_recursive_dense_B",
                "V62_lsys_branch_balanced_depth_C",
            ],
            "do_not_launch_remote_before_local_visual_qa": True,
        }
    )
    summary["lsystem_branch_gate"]["mask_scope"] = "object_space_recursive_dense_compact_bough_side_yfork_bands_only_antifacet"
    summary["lsystem_branch_gate"]["min_target_terminals_for_visual_qa"] = 12
    summary["lsystem_branch_gate"]["target_terminal_range"] = "12-20 readable terminals before texturing; prefer 12-16 visually dominant terminals after GLB"
    summary["lsystem_branch_gate"]["target_branch_junctions_min"] = 10
    summary["post_glb_target_floor"]["visual_gate"] = "GLB white zoom must preserve clean single support and restore L-system-like recursive depth/density without V41/V42 needles"
    summary["v62_design"] = {
        "generator_change_required": True,
        "why_not_postprocess_only": "V61's residual failure is insufficient recursive depth/density, not surface noise.",
        "downstream_clean_export": "assets/postprocess_v62_lsystem_branch_clean_export_20260512.py",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V62 L-system Recursive Dense-Bough Y-Fork Dry Run\n\n"
        "V62 is the depth/density counterpart to V61. It restores side_depth=3 recursive branch hierarchy on top of the V58/V59/V61 compact short-bough root, "
        "keeps the V59/V61 anti-facet implicit field, and defers fine clean export until local white-background OBJ zoom passes visual QA. "
        "No 2D seam inpaint/backprojection claim is made.\n",
        encoding="utf-8",
    )
    return summary


def materialize(root: Path, out_dir: Path, seed: int = 20260511, case_limit: Optional[int] = None) -> Dict:
    _install_v62_overrides()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            summary = v53.materialize(root, out_dir, seed=seed, case_limit=case_limit)
        summary = _rewrite_v62_outputs(out_dir, summary)
    finally:
        _restore_v62_overrides()
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
