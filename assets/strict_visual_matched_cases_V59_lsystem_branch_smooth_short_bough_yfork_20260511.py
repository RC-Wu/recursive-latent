#!/usr/bin/env python3
"""V59 L-system smooth short-bough Y-fork naturalization inputs.

V58 proved the root/silhouette switch was the right move: post-GLB connectivity
was perfect and the overview no longer read as a long tube skeleton.  Its GLB
zoom still exposed faceted striping and over-saturated plastic wood texture.
V59 keeps the V58 compact short-bough graph, but increases the implicit field
resolution and smoothing, removes free bark ridges from the OBJ scaffold, and
uses a desaturated low-contrast whole-object guide.
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


pb = v58.pb

REMOTE_TARGET = v58.REMOTE_TARGET
ALLOWED_GPUS = v58.ALLOWED_GPUS
DEFAULT_ACTIVE_GPUS = v58.DEFAULT_ACTIVE_GPUS
REMOTE_STORAGE_ROOT = v58.REMOTE_STORAGE_ROOT
STORAGE_LIMIT_GB = v58.STORAGE_LIMIT_GB
CONNECTIVITY_LCR_MIN = v58.CONNECTIVITY_LCR_MIN
EXTERNAL_SUPPORT_MAX_SEGMENT_GATE = v58.EXTERNAL_SUPPORT_MAX_SEGMENT_GATE
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V59_lsystem_branch_smooth_short_bough_yfork_20260511_dryrun"

SURFACE_STRATEGY = "v59_lsystem_branch_smooth_short_bough_yfork_antifacet_naturalization"
SELECTION_BUDGET = "four_v59_smooth_short_bough_candidates_local_qa_then_two_gpu_remote"
ZOOM_DIVISOR = 1.82

_ORIG_WRITE_GUIDES = v53._write_guides
_ORIG_GRID = v53.IMPLICIT_GRID_RESOLUTION
_ORIG_LEVEL = v53.IMPLICIT_FIELD_LEVEL
_ORIG_SIGMA = v53.IMPLICIT_GAUSSIAN_SIGMA
_ORIG_JUNCTION_RADIUS_BOOST = v53.JUNCTION_RADIUS_BOOST
_ORIG_JUNCTION_NEIGHBOR_RADIUS_BOOST = v53.JUNCTION_NEIGHBOR_RADIUS_BOOST

V59_GRID = 288
V59_LEVEL = 0.424
V59_SIGMA = 0.78
V59_JUNCTION_RADIUS_BOOST = 1.18
V59_JUNCTION_NEIGHBOR_RADIUS_BOOST = 1.055


def _write_guides_v59(out_dir: Path) -> Dict[str, str]:
    guide_dir = out_dir / "_guides"
    guides: Dict[str, str] = {}
    palettes = {
        "soft_bark": [(92, 78, 58), (112, 92, 66), (132, 110, 80), (150, 128, 96)],
        "matte_sapwood": [(104, 88, 66), (126, 104, 76), (144, 122, 92), (160, 138, 108)],
        "lowcontrast_cambium": [(96, 82, 62), (118, 98, 72), (136, 114, 84), (152, 132, 102)],
        "muted_cedar": [(88, 74, 54), (108, 88, 62), (128, 106, 78), (146, 124, 94)],
    }
    for key, colors in palettes.items():
        path = guide_dir / f"V59_lsystem_branch_{key}_lowcontrast_guide.png"
        rng = np.random.default_rng(v53.v26._stable_seed(path.stem))
        img = v53.Image.new("RGB", (768, 768), (118, 100, 78))
        draw = v53.ImageDraw.Draw(img, "RGBA")
        for _ in range(72):
            color = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(-120, 888))
            y = int(rng.integers(-120, 888))
            r = int(rng.integers(130, 310))
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, int(rng.integers(12, 34))))
        img = img.filter(v53.ImageFilter.GaussianBlur(radius=28))
        draw = v53.ImageDraw.Draw(img, "RGBA")
        for _ in range(18):
            color = colors[int(rng.integers(0, len(colors)))]
            base = np.array([rng.integers(80, 690), rng.integers(120, 660)], dtype=float)
            length = float(rng.uniform(130, 260))
            angle = float(rng.uniform(-2.35, -0.70))
            pts = []
            for t in np.linspace(0.0, 1.0, 9):
                curve = math.sin(t * math.pi) * rng.uniform(-8, 9)
                p = base + np.array([math.cos(angle) * length * t + curve, math.sin(angle) * length * t], dtype=float)
                pts.append((int(p[0]), int(p[1])))
            draw.line(pts, fill=(*color, int(rng.integers(24, 46))), width=int(rng.integers(5, 9)))
        path.parent.mkdir(parents=True, exist_ok=True)
        img.filter(v53.ImageFilter.SMOOTH_MORE).save(path)
        guides[key] = str(path)
    return guides


def _mutate_controls_for_v59(controls: Dict) -> None:
    v58._mutate_controls_for_v58(controls)
    controls["surface_strategy"] = SURFACE_STRATEGY
    controls["v58_lsystem_branch_short_bough_yfork_naturalization"] = False
    controls["v59_lsystem_branch_smooth_short_bough_yfork_naturalization"] = True
    controls["masked_local_naturalization_target"] = "L-system smooth compact short-bough Y-fork bands with anti-facet implicit field"
    controls["v58_failure_addressed"] = "V58 post-GLB connectivity was perfect, but GLB zoom exposed faceted striping, over-saturated plastic wood texture, and occasional dark endpoint read."
    controls["implicit_antifacet_policy"] = "higher-resolution smoother implicit field, lower junction radius boost, no free ridge scaffold, and desaturated low-contrast guide"
    controls["hard_tube_cap_mitigation"] = "V59 preserves V58 short-bough root while using smoother field and muted guide to avoid faceted strips and dark terminal drops"
    controls["texture_guide_policy"] = "desaturated low-contrast whole-object bark guide; no strong orange/woodgrain stripe target"
    controls["implicit_grid_resolution"] = V59_GRID
    controls["implicit_field_level"] = V59_LEVEL
    controls["gaussian_sigma"] = V59_SIGMA
    controls["junction_radius_boost"] = V59_JUNCTION_RADIUS_BOOST
    controls["junction_neighbor_radius_boost"] = V59_JUNCTION_NEIGHBOR_RADIUS_BOOST
    controls["sdedit_seam_backprojection_available"] = False


def _build_case_v59(seed: int, **kwargs) -> Tuple[pb.Mesh, Dict, Dict]:
    mesh, controls, grammar = v58._build_case_v58(seed, **kwargs)
    _mutate_controls_for_v59(controls)
    grammar["grammar_guide"] = "v59_lsystem_branch_smooth_short_bough_lowcontrast_bark_guide"
    grammar["antifacet_policy"] = "higher resolution smooth implicit field plus desaturated guide"
    return mesh, controls, grammar


def _spec_v59(
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
    _mutate_controls_for_v59(controls)
    spec = v58._spec_v58(
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
    spec["recursive_mode"] = "finite L-system smooth compact short-bough with recursive side branches and anti-facet shared-neck Y-forks"
    spec["grammar_guide"] = "v59_lsystem_branch_smooth_short_bough_lowcontrast_bark_guide"
    spec["case_role"] = "v59_lsystem_branch_smooth_short_bough_yfork_naturalization"
    spec["qa_priority"] = "post_glb_antifacet_short_bough_no_zigzag_strip_no_plastic_wood_no_dark_terminal_drop"
    spec["operators"] = list(spec["operators"]) + [
        "high_resolution_implicit_antifacet_field",
        "desaturated_low_contrast_bark_guide",
        "free_ridge_suppression",
    ]
    spec["operator_composition"] = " -> ".join(spec["operators"])
    _mutate_controls_for_v59(spec["controls"])
    return spec


def _case_specs_v59(seed: int) -> List[Dict]:
    settings = [
        ("V59_lsys_branch_smooth_short_bough_soft_A", 4, 59001, 4, 1, 2, False, 0.32, 0.54, 0.74, 0.0355, 0.852, 0.0064, 0.115, 0.285, 0.72, 0.058, 6, 0, 0, 0, 0, 0, 0, 0, 0.42, 0.34, "soft_bark", "V59 soft A: V58 short-bough with smoother field and muted bark guide"),
        ("V59_lsys_branch_smooth_short_bough_lowfrag_B", 5, 59002, 5, 1, 2, False, 0.27, 0.49, 0.68, 0.0345, 0.862, 0.0063, 0.105, 0.270, 0.74, 0.060, 5, 0, 0, 0, 0, 0, 0, 0, 0.38, 0.30, "matte_sapwood", "V59 lowfrag B: safest anti-facet version of V58 lowfrag_B"),
        ("V59_lsys_branch_smooth_short_bough_dense_C", 4, 59003, 4, 2, 2, True, 0.36, 0.58, 0.76, 0.0365, 0.846, 0.0066, 0.120, 0.300, 0.70, 0.058, 7, 0, 0, 0, 0, 0, 0, 0, 0.44, 0.36, "lowcontrast_cambium", "V59 dense C: stronger branch read with ridge suppression and smooth guide"),
        ("V59_lsys_branch_smooth_short_bough_compact_D", 5, 59004, 5, 1, 3, False, 0.21, 0.47, 0.64, 0.0340, 0.868, 0.0062, 0.100, 0.260, 0.76, 0.062, 5, 0, 0, 0, 0, 0, 0, 0, 0.36, 0.28, "matte_sapwood", "V59 compact D: anti-facet version of V58 compact_D with muted endpoint read"),
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
        mesh, controls, grammar = _build_case_v59(
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
            _spec_v59(
                case_id=case_id,
                mesh=mesh,
                controls=controls,
                grammar=grammar,
                guide_key=guide_key,
                gpu=gpu,
                seed=seed + offset,
                root_variant=case_id.replace("V59_", ""),
                parameter_variant=(
                    f"main{main_steps}_sideD{side_depth}_smoothshortbough"
                    f"_grid{V59_GRID}_sigma{V59_SIGMA:.2f}_base{base_radius:.3f}_ridge0"
                ),
                reason=reason,
            )
        )
    return rows


def _metadata_for_v59(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    metadata = v58._metadata_for_v58(spec, mesh_path, guide_path, metrics)
    _mutate_controls_for_v59(metadata["controls"])
    metadata["root_selection_log"]["root_source_type"] = "V59_lsystem_branch_smooth_short_bough_yfork_naturalization_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V59_lsystem_branch_smooth_short_bough_yfork_20260511.py"
    metadata["case_role"] = "v59_lsystem_branch_smooth_short_bough_yfork_naturalization"
    old_contract = metadata.pop("v58_lsystem_branch_naturalization_contract", {})
    metadata["v59_lsystem_branch_naturalization_contract"] = {
        "target_failure": "V58 post-GLB metrics were clean, but white zoom exposed faceted striping, plastic orange wood texture, and occasional dark endpoint read.",
        "geometry_operator": "V58 compact short-bough root plus higher-resolution smoother implicit field, lower junction boost, free-ridge suppression, and desaturated guide",
        "carried_v58_evidence": old_contract,
        "antifacet_constants": {
            "implicit_grid_resolution": V59_GRID,
            "implicit_field_level": V59_LEVEL,
            "gaussian_sigma": V59_SIGMA,
            "junction_radius_boost": V59_JUNCTION_RADIUS_BOOST,
            "junction_neighbor_radius_boost": V59_JUNCTION_NEIGHBOR_RADIUS_BOOST,
        },
        "sdedit_seam_backprojection_available": False,
        "post_glb_acceptance": "candidate only if GLB white zoom no longer shows zigzag strips, dark terminal drops, or plastic high-saturation wood as the dominant read.",
    }
    metadata["v59_remote_cache_policy"] = metadata.pop("v58_remote_cache_policy", {})
    return metadata


def _install_v59_overrides() -> None:
    v58._install_v58_overrides()
    v53.IMPLICIT_GRID_RESOLUTION = V59_GRID
    v53.IMPLICIT_FIELD_LEVEL = V59_LEVEL
    v53.IMPLICIT_GAUSSIAN_SIGMA = V59_SIGMA
    v53.JUNCTION_RADIUS_BOOST = V59_JUNCTION_RADIUS_BOOST
    v53.JUNCTION_NEIGHBOR_RADIUS_BOOST = V59_JUNCTION_NEIGHBOR_RADIUS_BOOST
    v53._write_guides = _write_guides_v59
    v53._case_specs = _case_specs_v59
    v53._metadata_for = _metadata_for_v59
    v53.SURFACE_STRATEGY = SURFACE_STRATEGY
    v53.SELECTION_BUDGET = SELECTION_BUDGET


def _restore_v59_overrides() -> None:
    v58._restore_v53_overrides()
    v53._write_guides = _ORIG_WRITE_GUIDES
    v53.IMPLICIT_GRID_RESOLUTION = _ORIG_GRID
    v53.IMPLICIT_FIELD_LEVEL = _ORIG_LEVEL
    v53.IMPLICIT_GAUSSIAN_SIGMA = _ORIG_SIGMA
    v53.JUNCTION_RADIUS_BOOST = _ORIG_JUNCTION_RADIUS_BOOST
    v53.JUNCTION_NEIGHBOR_RADIUS_BOOST = _ORIG_JUNCTION_NEIGHBOR_RADIUS_BOOST


def _rewrite_v59_outputs(out_dir: Path, summary: Dict) -> Dict:
    manifest_json = out_dir / "manifest.json"
    manifest_csv = out_dir / "manifest.csv"
    if manifest_json.exists():
        rows = json.loads(manifest_json.read_text(encoding="utf-8"))
        for row in rows:
            controls = json.loads(row["controls"])
            _mutate_controls_for_v59(controls)
            row["controls"] = json.dumps(controls, ensure_ascii=False, sort_keys=True)
            row["case_role"] = "v59_lsystem_branch_smooth_short_bough_yfork_naturalization"
            row["grammar_guide"] = "v59_lsystem_branch_smooth_short_bough_lowcontrast_bark_guide"
            row["selection_budget"] = SELECTION_BUDGET
            row["surface_strategy"] = SURFACE_STRATEGY
        manifest_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        if manifest_csv.exists() and rows:
            with manifest_csv.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

    old_zoom = out_dir / "V53_obj_zoom_manifest_junctiontarget_20260511.json"
    v58_zoom = out_dir / "V58_obj_zoom_manifest_junctiontarget_20260511.json"
    new_zoom = out_dir / "V59_obj_zoom_manifest_junctiontarget_20260511.json"
    source_zoom = v58_zoom if v58_zoom.exists() else old_zoom
    if source_zoom.exists():
        data = json.loads(source_zoom.read_text(encoding="utf-8"))
        for item in data.get("cases", []):
            item["zoom_divisor"] = ZOOM_DIVISOR
            item["detail_target_source"] = "v59_lsystem_explicit_smooth_short_bough_yfork_antifacet_mask"
        new_zoom.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        source_zoom.unlink()
    if old_zoom.exists():
        old_zoom.unlink()

    summary.update(
        {
            "out_dir": str(out_dir),
            "surface_generator": "strict_visual_matched_cases_V59_lsystem_branch_smooth_short_bough_yfork_naturalization",
            "surface_strategy": SURFACE_STRATEGY,
            "selection_budget": SELECTION_BUDGET,
            "obj_zoom_manifest": str(new_zoom),
            "do_not_launch_remote_before_local_visual_qa": True,
        }
    )
    summary["lsystem_branch_gate"]["mask_scope"] = "object_space_compact_short_bough_side_yfork_bands_only_antifacet"
    summary["post_glb_target_floor"]["visual_gate"] = "GLB white zoom must avoid zigzag/faceted strips, plastic saturated wood, and dark terminal drops"
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V59 L-system Smooth Short-Bough Y-Fork Dry Run\n\n"
        "V59 keeps V58's short-bough root rewrite but targets the post-GLB failure mode: faceted/zigzag strips, saturated plastic wood, and dark endpoints. "
        "It uses a higher-resolution smoother implicit field, suppresses free ridges, and switches to desaturated whole-object guides. "
        "No 2D seam inpaint/backprojection claim is made.\n",
        encoding="utf-8",
    )
    return summary


def materialize(root: Path, out_dir: Path, seed: int = 20260511, case_limit: Optional[int] = None) -> Dict:
    _install_v59_overrides()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            summary = v53.materialize(root, out_dir, seed=seed, case_limit=case_limit)
        summary = _rewrite_v59_outputs(out_dir, summary)
    finally:
        _restore_v59_overrides()
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
