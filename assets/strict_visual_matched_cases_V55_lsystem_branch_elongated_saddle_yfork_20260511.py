#!/usr/bin/env python3
"""V55 L-system branch elongated-saddle Y-fork naturalization inputs.

V54 passed the hard local metrics, but white zoom QA still read as rounded
branch tubes with cut-off crop edges and local bulb-like saddles. V55 keeps the
same strict branch-with-side-branches grammar target, but makes the local
naturalization more object-space and wood-like:

* terminal radii are allowed to taper below the V54 field floor,
* junction fusion is carried by elongated parent-child saddle fields instead of
  round anchor balls,
* branch relief is limited to shallow longitudinal bark ridges,
* zoom is widened slightly so the second level does not cut through the branch
  as the dominant visual feature.

This is still grammar-owned local geometry plus whole-object low-contrast guide
texturing. It does not claim a 2D seam-inpaint/backprojection pipeline.
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

import strict_visual_matched_cases_V54_lsystem_branch_centered_bough_yfork_20260511 as v54


REMOTE_TARGET = v54.REMOTE_TARGET
ALLOWED_GPUS = v54.ALLOWED_GPUS
DEFAULT_ACTIVE_GPUS = v54.DEFAULT_ACTIVE_GPUS
REMOTE_STORAGE_ROOT = v54.REMOTE_STORAGE_ROOT
STORAGE_LIMIT_GB = v54.STORAGE_LIMIT_GB
CONNECTIVITY_LCR_MIN = v54.CONNECTIVITY_LCR_MIN
EXTERNAL_SUPPORT_MAX_SEGMENT_GATE = v54.EXTERNAL_SUPPORT_MAX_SEGMENT_GATE
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V55_lsystem_branch_elongated_saddle_yfork_20260511_dryrun"

SURFACE_STRATEGY = "v55_lsystem_branch_elongated_saddle_yfork_naturalization"
SELECTION_BUDGET = "four_v55_lsystem_branch_candidates_local_qa_then_two_gpu_remote"
MESH_PBR_POLICY = v54.MESH_PBR_POLICY
ZOOM_PAIR_MIN_DISTANCE = v54.ZOOM_PAIR_MIN_DISTANCE
IMPLICIT_GRID_RESOLUTION = 224
IMPLICIT_FIELD_BOUND = 1.70
IMPLICIT_FIELD_LEVEL = 0.425
IMPLICIT_GAUSSIAN_SIGMA = 0.56
ZOOM_DIVISOR = 2.22


_ORIGINAL_CASE_SPECS = v54._case_specs
_ORIGINAL_CAPSULE_FIELD_MESH = v54._capsule_field_mesh
_ORIGINAL_METADATA_FOR = v54._metadata_for


def _capsule_field_mesh_v55(
    nodes: List[np.ndarray],
    parents: List[int],
    radii: List[float],
    rng: np.random.Generator,
    *,
    anchors: List[int],
    ridge_count: int,
    split_count: int,
    detail_radius_scale: float,
    lobe_scale: float,
) -> Tuple[v54.pb.Mesh, v54.DetailCounts, Dict]:
    """Implicit branch field with elongated saddles and slimmer terminals."""

    resolution = IMPLICIT_GRID_RESOLUTION
    bound = IMPLICIT_FIELD_BOUND
    coords = np.linspace(-bound, bound, resolution, dtype=np.float32)
    field = np.zeros((resolution, resolution, resolution), dtype=np.float32)
    edges = v54.v22._graph_edges(parents)
    child_map = v54.v22._children(parents)
    depths = v54.bm.graph_depths(parents)
    terminals = set(v54.v27._terminal_nodes(parents))
    anchor_set = set(int(idx) for idx in anchors)

    local_boost_nodes: set[int] = set()
    for idx in anchors:
        local_boost_nodes.add(int(idx))
        parent_idx = int(parents[idx]) if int(parents[idx]) >= 0 else -1
        if parent_idx >= 0:
            local_boost_nodes.add(parent_idx)
        for child in child_map.get(idx, [])[:3]:
            local_boost_nodes.add(int(child))

    boosted_radii = [float(r) for r in radii]
    for idx in range(len(boosted_radii)):
        if idx in anchor_set:
            boosted_radii[idx] = max(boosted_radii[idx] * (1.045 + 0.012 * lobe_scale), boosted_radii[idx] + 0.0008)
        elif idx in local_boost_nodes:
            boosted_radii[idx] = max(boosted_radii[idx] * 1.018, boosted_radii[idx] + 0.0004)
        if idx in terminals:
            boosted_radii[idx] = max(boosted_radii[idx] * 0.52, 0.0029)

    primitive_count = 0
    for edge_i, (a, b) in enumerate(edges):
        a_terminal = int(a) in terminals
        b_terminal = int(b) in terminals
        ra_floor = 0.0032 if a_terminal else 0.0064
        rb_floor = 0.0030 if b_terminal else 0.0062
        primitive_count += v54.v45._stamp_wood_segment(
            field,
            coords,
            np.asarray(nodes[a], dtype=float),
            np.asarray(nodes[b], dtype=float),
            max(boosted_radii[a], ra_floor),
            max(boosted_radii[b], rb_floor),
            strength=1.035,
            samples_per_unit=190.0,
            rng=rng,
            phase=edge_i * 0.83 + rng.uniform(-0.12, 0.12),
        )

    seam_centers: List[List[float]] = []
    fork_centers: List[List[float]] = []
    saddle_swell_count = 0
    for k, idx in enumerate(anchors):
        children = child_map.get(idx, [])
        if len(children) < 2:
            continue
        anchor = np.asarray(nodes[idx], dtype=float)
        fork_centers.append([float(x) for x in anchor])
        parent_idx = int(parents[idx]) if int(parents[idx]) >= 0 else idx
        parent_axis = (
            v54.v22._unit(anchor - np.asarray(nodes[parent_idx], dtype=float))
            if parent_idx != idx
            else v54.v22._node_axis(nodes, parents, idx)
        )
        child_dirs: List[Tuple[float, np.ndarray, int]] = []
        for child in children:
            child_dir = v54.v22._unit(np.asarray(nodes[child], dtype=float) - anchor)
            score = float(np.linalg.norm(child_dir - 0.62 * parent_axis))
            child_dirs.append((score, child_dir, int(child)))
        child_dirs.sort(reverse=True, key=lambda item: item[0])

        # A very weak anchor keeps the implicit field watertight without reading
        # as a spherical collar in close-up.
        v54.v45._stamp_ball(
            field,
            coords,
            anchor,
            max(float(boosted_radii[idx]) * 0.56, 0.0105),
            0.075,
            cutoff=1.42,
        )
        primitive_count += 1

        for _score, child_dir, _child in child_dirs[:3]:
            side_dir = v54.v22._unit(child_dir - 0.36 * parent_axis)
            if float(np.linalg.norm(side_dir)) < 1e-7:
                side_dir = v54.v22._basis(parent_axis)[0]
            blend_dir = v54.v22._unit(0.66 * parent_axis + 0.34 * child_dir)
            normal = v54.v22._unit(np.cross(blend_dir, side_dir))
            if float(np.linalg.norm(normal)) < 1e-7:
                normal = v54.v22._basis(blend_dir)[1]

            upstream = anchor - parent_axis * 0.034 + blend_dir * 0.030
            v54.v45._stamp_ellipsoid(
                field,
                coords,
                upstream,
                (side_dir, normal, blend_dir),
                (
                    float(0.0095 + 0.0022 * detail_radius_scale),
                    float(0.0085 + 0.0018 * detail_radius_scale),
                    float(0.082 + 0.020 * lobe_scale),
                ),
                0.058,
                cutoff=1.34,
            )
            mid = anchor + blend_dir * 0.072
            v54.v45._stamp_ellipsoid(
                field,
                coords,
                mid,
                (side_dir, normal, blend_dir),
                (
                    float(0.0100 + 0.0024 * detail_radius_scale),
                    float(0.0088 + 0.0019 * detail_radius_scale),
                    float(0.104 + 0.022 * lobe_scale),
                ),
                0.070,
                cutoff=1.34,
            )
            root = anchor + child_dir * 0.102
            v54.v45._stamp_ellipsoid(
                field,
                coords,
                root,
                (normal, side_dir, child_dir),
                (
                    float(0.0085 + 0.0018 * detail_radius_scale),
                    float(0.0102 + 0.0022 * detail_radius_scale),
                    float(0.083 + 0.018 * lobe_scale),
                ),
                0.056,
                cutoff=1.32,
            )
            seam_centers.extend([[float(x) for x in upstream], [float(x) for x in mid], [float(x) for x in root]])
            saddle_swell_count += 3
            primitive_count += 3

    ridge_sites = sorted(
        [idx for idx in range(1, len(nodes)) if idx not in terminals],
        key=lambda idx: (depths[idx], idx),
        reverse=True,
    )
    ridge_written = 0
    for k, idx in enumerate(ridge_sites[: max(0, int(ridge_count) + int(split_count))]):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v54.v22._node_axis(nodes, parents, idx)
        u, v, w = v54.v22._basis(axis)
        lateral = v54.v22._unit(math.cos(k * 2.11) * u + math.sin(k * 2.11) * v)
        center = anchor + lateral * max(float(boosted_radii[idx]) * 0.50, 0.0055) + axis * 0.026
        v54.v45._stamp_ellipsoid(
            field,
            coords,
            center,
            (lateral, v54.v22._unit(np.cross(w, lateral)), w),
            (
                float(0.0018 + 0.0005 * detail_radius_scale),
                float(0.0032 + 0.0007 * detail_radius_scale),
                float(0.040 + 0.008 * rng.random()),
            ),
            0.033,
            cutoff=1.18,
        )
        ridge_written += 1
        primitive_count += 1

    field_terminal_taper_count = 0
    field = v54.v45.gaussian_filter(field, sigma=IMPLICIT_GAUSSIAN_SIGMA)
    verts, faces, _normals, _values = v54.v45.marching_cubes(
        field,
        level=IMPLICIT_FIELD_LEVEL,
        spacing=(float(coords[1] - coords[0]), float(coords[1] - coords[0]), float(coords[1] - coords[0])),
        allow_degenerate=False,
    )
    verts = verts + np.array([coords[0], coords[0], coords[0]], dtype=float)
    mesh = v54.pb.Mesh([tuple(map(float, v)) for v in verts], [tuple(int(i) + 1 for i in f) for f in faces])
    mesh, raw_component_count, retained_ratio = v54.v45._largest_component_mesh(mesh)
    mesh = v54.v45._taubin_smooth(mesh, iterations=10, lam=0.26, mu=-0.29)

    counts = v54._blank_counts()
    counts["collar_count"] = int(saddle_swell_count + len(anchors))
    counts["flare_count"] = int(saddle_swell_count + len(anchors))
    counts["ridge_count"] = int(ridge_written)
    counts["split_count"] = int(max(0, ridge_written - int(ridge_count)))
    return mesh, counts, {
        "junction_anchor_count": int(len(set(anchors))),
        "junction_collar_count": int(counts["collar_count"]),
        "junction_cambium_lobe_count": 0,
        "seam_mask_center_count": int(len(seam_centers)),
        "seam_mask_centers": seam_centers[:128],
        "highres_smooth_yfork_centers": fork_centers[:128],
        "seam_mask_radius": 0.132,
        "implicit_capsule_support": True,
        "mechanical_sleeve_disabled": True,
        "direct_axis_sleeve_count": 0,
        "junction_implicit_capsule_count": int(len(set(anchors))),
        "implicit_saddle_swell_count": int(saddle_swell_count),
        "terminal_taper_count": int(field_terminal_taper_count),
        "field_terminal_taper_count": int(field_terminal_taper_count),
        "terminal_taper_source": "graph_native_three_step_taper_segments_with_v55_low_terminal_field_floor",
        "sweep_sides": 0,
        "junction_radius_boost": 1.045,
        "junction_neighbor_radius_boost": 1.018,
        "raw_marching_cubes_component_count": int(raw_component_count),
        "largest_component_projection_retained_ratio": float(retained_ratio),
        "pre_marching_cubes_primitive_count": int(primitive_count),
        "implicit_grid_resolution": int(resolution),
        "implicit_field_bound": float(bound),
        "implicit_field_level": float(IMPLICIT_FIELD_LEVEL),
        "gaussian_sigma": float(IMPLICIT_GAUSSIAN_SIGMA),
        "low_relief_lobe_policy": "elongated low-strength parent-child saddle fields; no spherical collars, terminal sleeves, or cap stamps",
    }


def _mutate_controls_for_v55(controls: Dict) -> None:
    controls["surface_strategy"] = SURFACE_STRATEGY
    controls["v54_lsystem_branch_centered_bough_yfork_naturalization"] = False
    controls["v55_lsystem_branch_elongated_saddle_yfork_naturalization"] = True
    controls["masked_local_naturalization_target"] = "L-system elongated parent-child saddle bands with low-floor graph-native terminal tapers"
    controls["mask_scope"] = "object_space_elongated_saddle_yfork_bands_only"
    controls["seam_mask_selection_rule"] = "degree>=2 L-system saddle junctions plus elongated parent-child blend centers; terminal sleeves excluded"
    controls["support_cross_section"] = "slim_elliptic_branch_with_elongated_saddle_yforks"
    controls["support_visibility_policy"] = "main and side branches remain visible as one woody bough; local field saddles are elongated along branch axes"
    controls["hard_tube_cap_mitigation"] = "V55 lowers terminal field floors, raises the implicit level, widens zoom, and replaces round collars with elongated low-strength saddle fields"
    controls["highres_smooth_yfork_zoom_target_policy"] = "explicit graph Y-fork pair with wider V55 zoom; terminal and crop-edge targets excluded"
    controls["v54_failure_addressed"] = "V54 metric-passed but white zoom still read as round tubes with crop-edge cuts and bulb-like saddle collars"
    controls["claim_boundary"] = "grammar-owned local geometry/material candidate; no 2D seam inpaint backprojection claim"


def _build_case_v55(seed: int, **kwargs) -> Tuple[v54.pb.Mesh, Dict, Dict]:
    mesh, controls, grammar = v54._build_lsystem_branch_case(seed, **kwargs)
    _mutate_controls_for_v55(controls)
    grammar["grammar_guide"] = "v55_lsystem_branch_lowcontrast_bark_elongated_saddle_guide"
    return mesh, controls, grammar


def _case_specs_v55(seed: int) -> List[Dict]:
    settings = [
        ("V55_lsys_branch_elongated_saddle_yfork_A", 4, 55001, 7, 2, 2, False, 0.30, 0.58, 0.76, 0.0265, 0.788, 0.0048, 0.085, 0.245, 0.58, 0.066, 8, 2, 0, 0, 0, 0, 0, 0, 0.42, 0.34, "pale_cambium", "elongated-saddle A: lower terminal field floor, wider zoom, and non-spherical Y-fork saddle"),
        ("V55_lsys_branch_elongated_saddle_yfork_lowfrag_B", 5, 55002, 8, 2, 2, False, 0.25, 0.52, 0.72, 0.0255, 0.798, 0.0045, 0.080, 0.235, 0.62, 0.066, 8, 2, 0, 0, 0, 0, 0, 0, 0.38, 0.30, "pale_cambium", "elongated-saddle lowfrag B: conservative slender bough with least collar mass"),
        ("V55_lsys_branch_elongated_saddle_yfork_dense_C", 4, 55003, 7, 2, 2, False, 0.34, 0.62, 0.80, 0.0270, 0.782, 0.0049, 0.090, 0.255, 0.57, 0.064, 9, 2, 0, 0, 0, 0, 0, 0, 0.44, 0.36, "centered_bough", "elongated-saddle dense C: stronger branch silhouette without V54 round saddle balls"),
        ("V55_lsys_branch_elongated_saddle_yfork_slim_D", 5, 55004, 8, 2, 2, False, 0.22, 0.50, 0.68, 0.0248, 0.806, 0.0043, 0.075, 0.225, 0.66, 0.068, 7, 2, 0, 0, 0, 0, 0, 0, 0.36, 0.28, "pale_cambium", "elongated-saddle slim D: widest visual margin against cut-pipe terminals"),
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
        mesh, controls, grammar = _build_case_v55(
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
                root_variant=case_id.replace("V55_", ""),
                parameter_variant=(
                    f"main{main_steps}_sideD{side_depth}_every{side_every}_double{int(double_sides)}"
                    f"_maxseg{max_segment:.3f}_base{base_radius:.3f}_tip{terminal_shrink:.2f}"
                    f"_parent{tip_parent_shrink:.2f}_elongatedsaddle_ridge{ridge_count}"
                ),
                reason=reason,
            )
        )
    return rows


def _metadata_for_v55(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    metadata = _ORIGINAL_METADATA_FOR(spec, mesh_path, guide_path, metrics)
    _mutate_controls_for_v55(metadata["controls"])
    metadata["root_selection_log"]["root_source_type"] = "V55_lsystem_branch_elongated_saddle_yfork_naturalization_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V55_lsystem_branch_elongated_saddle_yfork_20260511.py"
    contract = metadata.pop("v54_lsystem_branch_naturalization_contract", {})
    contract["target_failure"] = "V54 passed connectivity and object-space mask metrics but white zoom still read as round tubes, bulb collars, and crop-edge cuts."
    contract["geometry_operator"] = "continuous implicit wood field with low terminal floors and elongated parent-child saddle ellipsoids"
    contract["v55_visual_gate"] = "overview must remain branch-with-side-branches; zoom_01/zoom_02 must show continuous wood saddle without hard tube insertion, round collar bulb, or dominant crop cut"
    metadata["v55_lsystem_branch_naturalization_contract"] = contract
    metadata["v55_remote_cache_policy"] = metadata.pop("v54_remote_cache_policy", {})
    return metadata


def _install_v55_overrides() -> None:
    v54.SURFACE_STRATEGY = SURFACE_STRATEGY
    v54.SELECTION_BUDGET = SELECTION_BUDGET
    v54.IMPLICIT_FIELD_LEVEL = IMPLICIT_FIELD_LEVEL
    v54.IMPLICIT_GAUSSIAN_SIGMA = IMPLICIT_GAUSSIAN_SIGMA
    v54._capsule_field_mesh = _capsule_field_mesh_v55
    v54._case_specs = _case_specs_v55
    v54._metadata_for = _metadata_for_v55


def _rewrite_v55_outputs(out_dir: Path, summary: Dict) -> Dict:
    manifest_json = out_dir / "manifest.json"
    manifest_csv = out_dir / "manifest.csv"
    if manifest_json.exists():
        rows = json.loads(manifest_json.read_text(encoding="utf-8"))
        for row in rows:
            controls = json.loads(row["controls"])
            _mutate_controls_for_v55(controls)
            row["controls"] = json.dumps(controls, ensure_ascii=False, sort_keys=True)
            row["case_role"] = "v55_lsystem_branch_elongated_saddle_yfork_naturalization"
            row["grammar_guide"] = "v55_lsystem_branch_lowcontrast_bark_elongated_saddle_guide"
            row["selection_budget"] = SELECTION_BUDGET
            row["surface_strategy"] = SURFACE_STRATEGY
        manifest_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        if manifest_csv.exists() and rows:
            with manifest_csv.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

    old_zoom = out_dir / "V54_obj_zoom_manifest_junctiontarget_20260511.json"
    new_zoom = out_dir / "V55_obj_zoom_manifest_junctiontarget_20260511.json"
    if old_zoom.exists():
        data = json.loads(old_zoom.read_text(encoding="utf-8"))
        for item in data.get("cases", []):
            item["zoom_divisor"] = ZOOM_DIVISOR
            item["detail_target_source"] = "v55_lsystem_explicit_elongated_saddle_yfork_mask"
        new_zoom.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        old_zoom.unlink()

    summary.update(
        {
            "out_dir": str(out_dir),
            "surface_generator": "strict_visual_matched_cases_V55_lsystem_branch_elongated_saddle_yfork_naturalization",
            "surface_strategy": SURFACE_STRATEGY,
            "selection_budget": SELECTION_BUDGET,
            "obj_zoom_manifest": str(new_zoom),
        }
    )
    summary["lsystem_branch_gate"]["mask_scope"] = "object_space_elongated_saddle_yfork_bands_only"
    summary["post_glb_target_floor"]["visual_gate"] = (
        "side-branch saddle zoom must read as a continuous elongated wood fork, "
        "not a hard inserted tube, round collar bulb, or crop-edge cut"
    )
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V55 L-system Branch Elongated-Saddle Y-Fork Dry Run\n\n"
        "V55 follows the failed V54 visual QA: strong connectivity was not enough because the white zoom still read as "
        "round tubes, bulb-like saddles, and crop-edge cuts. This batch lowers terminal field floors, raises the implicit "
        "surface level, replaces spherical collars with elongated low-strength saddle ellipsoids, keeps shallow bark ridges, "
        "and widens the matched zoom before any remote textured GLB launch. It remains claim-bounded: no 2D seam inpaint "
        "or backprojection pipeline is claimed.\n",
        encoding="utf-8",
    )
    return summary


def materialize(root: Path, out_dir: Path, seed: int = 20260511, case_limit: Optional[int] = None) -> Dict:
    _install_v55_overrides()
    with contextlib.redirect_stdout(io.StringIO()):
        summary = v54.materialize(root, out_dir, seed=seed, case_limit=case_limit)
    summary = _rewrite_v55_outputs(out_dir, summary)
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
