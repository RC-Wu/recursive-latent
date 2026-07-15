#!/usr/bin/env python3
"""Build the Experiment 3 route-normalized manifest.

This script is intentionally selected-final-only.  It does not recursively scan
the repository; it combines explicitly named evidence files and an 8-case
claim-gated queue for the sparse-latent-vs-mesh-space novelty experiment.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_OUT = ROOT / "results" / "experiment3_sparse_latent_vs_meshspace_20260511"
BASELINE_MASTER = ROOT / "results/publication_baseline_metrics_20260510/publication_baseline_master_manifest_20260510.csv"
HUNYUAN_TEXT_ROOT = ROOT / "results/remote_pull_hunyuan_text_root_meshspace_20260511/hunyuan_text_root_meshspace_metrics.csv"
TRELLIS2_EXP3_METRICS = ROOT / "results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_trellis2_baseline_metrics.csv"
TRELLIS2_GENERATEDROOT_METRICS = (
    ROOT
    / "results/experiment3_sparse_latent_vs_meshspace_20260511/trellis2_generatedroot_meshcopy/trellis2_generatedroot_meshcopy_metrics.csv"
)
PS_RSLG_EXP3_METRICS = ROOT / "results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_ps_rslg_metric_rows_20260511.csv"


METHOD_ROWS = [
    "classical_proc",
    "classical_smooth",
    "proc_trellis2_texture",
    "hunyuan_root_meshcopy",
    "hunyuan_root_meshcopy_smooth",
    "trellis2_oneshot_image",
    "trellis2_root_latentcopy",
    "trellis2_generatedroot_meshcopy",
    "ps_rslg",
]


CASES: list[dict[str, str]] = [
    {
        "case_id": "V25_sc_tree_crown_tapered_B",
        "case_short": "tree_crown",
        "category": "botanical_tree",
        "family": "space_colonization_tree_crown",
        "root_or_source": "results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/inputs/V25_sc_tree_crown_tapered_B/V25_sc_tree_crown_tapered_B.obj",
        "ps_asset": "visuals/strict_visual_matched_texture_V25_root_sc_refine_20260510/V25_sc_tree_crown_tapered_B_steps8_tex2048_seed20285522_xformers/textured.glb",
        "preview": "visuals/strict_visual_matched_texture_V25_root_sc_refine_zoom_white_20260510/V25_root_sc_refine_contact_sheet_20260510.png",
        "priority_note": "P0 Trellis2 one-shot and latent-copy; P1 Hunyuan text-root meshcopy.",
    },
    {
        "case_id": "V25_lsys_root_fan_smooth_anchorD_stable",
        "case_short": "root_fan",
        "category": "botanical_tree",
        "family": "lsystem_root_fan",
        "root_or_source": "results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/inputs/V25_lsys_root_fan_smooth_anchorD_stable/V25_lsys_root_fan_smooth_anchorD_stable.obj",
        "ps_asset": "visuals/strict_visual_matched_texture_V25_root_sc_refine_20260510/V25_lsys_root_fan_smooth_anchorD_stable_steps8_tex2048_seed20285514_xformers/textured.glb",
        "preview": "visuals/strict_visual_matched_texture_V25_root_sc_refine_zoom_white_20260510/V25_root_sc_refine_contact_sheet_20260510.png",
        "priority_note": "P0 Trellis2 one-shot and latent-copy; P1 Hunyuan text-root meshcopy.",
    },
    {
        "case_id": "v15_lsys_climbing_vine_d6_smooth_leafy_curl",
        "case_short": "vine",
        "category": "botanical_tree",
        "family": "lsystem_vine",
        "root_or_source": "results/strict_visual_matched_texture_v15_plants_ifs_seed20278100_20260510_remote/inputs/v15_lsys_climbing_vine_d6_smooth_leafy_curl/v15_lsys_climbing_vine_d6_smooth_leafy_curl.obj",
        "ps_asset": "visuals/strict_visual_matched_texture_v15_plants_ifs_seed20278100_20260510/v15_lsys_climbing_vine_d6_smooth_leafy_curl_steps8_tex2048_seed20278203_xformers/textured.glb",
        "preview": "visuals/strict_visual_matched_texture_v15_plants_ifs_zoom_20260510/v15_lsys_climbing_vine_d6_smooth_leafy_curl/strict_matched_zoom_comparison.png",
        "priority_note": "Existing baseline rows map to short case vine; synchronize strict vs selected labels.",
    },
    {
        "case_id": "spider_rosette_publication_broad_20260511h",
        "case_short": "spider_rosette",
        "category": "botanical_tree",
        "family": "spider_rosette_plant",
        "root_or_source": "results/fern_root_candidates_20260511h/spider_rosette_publication_broad_20260511h/spider_rosette_publication_broad_20260511h.obj",
        "ps_asset": "results/botanical_tree_root_recursive_remote_20260511i_pull/raw/plant_broad_yneg_20260511i",
        "preview": "results/fern_root_candidates_20260511h/fern_root_candidates_contact_sheet.png",
        "priority_note": "P0 QA-gated; run Trellis2 one-shot after selected recursive output passes Blender QA.",
    },
    {
        "case_id": "V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA",
        "case_short": "coral",
        "category": "non_tree",
        "family": "dla_coral_frontier",
        "root_or_source": "results/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510_remote/inputs/V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA/V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA.obj",
        "ps_asset": "visuals/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510/V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA_steps8_tex2048_seed20284523_xformers/textured.glb",
        "preview": "visuals/strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510/strict_visual_matched_texture_V24_priority_rerun_seed3_contact_sheet.png",
        "priority_note": "Core rows exist under short case coral; add fair Hunyuan text-root row and updated failure labels.",
    },
    {
        "case_id": "V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA",
        "case_short": "pyrite",
        "category": "non_tree",
        "family": "ifs_pyrite_lattice",
        "root_or_source": "results/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510_remote/inputs/V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA/V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA.obj",
        "ps_asset": "visuals/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510/V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA_steps8_tex2048_seed20284526_xformers/textured.glb",
        "preview": "visuals/strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510/strict_visual_matched_texture_V24_priority_rerun_seed3_contact_sheet.png",
        "priority_note": "Core rows exist under short case pyrite; add fair Hunyuan text-root row and updated failure labels.",
    },
    {
        "case_id": "V21_ifs_bismuth_stepped_transform_d5_iridescent",
        "case_short": "bismuth",
        "category": "non_tree",
        "family": "ifs_bismuth_terraced",
        "root_or_source": "results/strict_visual_matched_texture_V21_ifs_transform_natural_seed20291700_20260510_remote/inputs/V21_ifs_bismuth_stepped_transform_d5_iridescent/V21_ifs_bismuth_stepped_transform_d5_iridescent.obj",
        "ps_asset": "visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20291700_20260510/V21_ifs_bismuth_stepped_transform_d5_iridescent_steps8_tex2048_seed20293804_xformers/textured.glb",
        "preview": "visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_zoom_20260510/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_contact_sheet_20260510.png",
        "priority_note": "P0 Trellis2 one-shot and generated-root/latent-copy baselines; P1 Hunyuan text-root meshcopy.",
    },
    {
        "case_id": "V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA",
        "case_short": "radial_ornament",
        "category": "non_tree",
        "family": "ifs_radial_ornament",
        "root_or_source": "results/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510_remote/inputs/V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA/V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA.obj",
        "ps_asset": "visuals/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510/V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA_steps8_tex2048_seed20284527_xformers/textured.glb",
        "preview": "visuals/strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510/strict_visual_matched_texture_V24_priority_rerun_seed3_contact_sheet.png",
        "priority_note": "P0 Trellis2 one-shot and generated-root/latent-copy baselines; P1 Hunyuan text-root meshcopy.",
    },
]


SHORT_CASE_ALIASES = {
    "vine": "v15_lsys_climbing_vine_d6_smooth_leafy_curl",
    "pyrite": "V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA",
    "coral": "V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA",
    "tree_trunk_branch": "V25_sc_tree_crown_tapered_B",
    "pyrite_crystal_root": "V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA",
    "coral_branch_root": "V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA",
    "bismuth_crystal_root": "V21_ifs_bismuth_stepped_transform_d5_iridescent",
}


METHOD_ALIASES = {
    "Trellis2 one-shot": "trellis2_oneshot_image",
    "Trellis2 trivial latent": "trellis2_root_latentcopy",
    "mesh-space generated-root": "trellis2_generatedroot_meshcopy",
    "Hunyuan text-root mesh-space recursion": "hunyuan_root_meshcopy",
    "PS-RSLG (ours)": "ps_rslg",
    "PS-RSLG (ours, strict protocol)": "ps_rslg",
    "PS-RSLG (ours, selected)": "ps_rslg",
}


P0_BY_CASE_METHOD = {
    ("V25_sc_tree_crown_tapered_B", "trellis2_oneshot_image"),
    ("V25_sc_tree_crown_tapered_B", "trellis2_root_latentcopy"),
    ("V25_sc_tree_crown_tapered_B", "trellis2_generatedroot_meshcopy"),
    ("V25_lsys_root_fan_smooth_anchorD_stable", "trellis2_oneshot_image"),
    ("V25_lsys_root_fan_smooth_anchorD_stable", "trellis2_root_latentcopy"),
    ("V25_lsys_root_fan_smooth_anchorD_stable", "trellis2_generatedroot_meshcopy"),
    ("spider_rosette_publication_broad_20260511h", "trellis2_oneshot_image"),
    ("spider_rosette_publication_broad_20260511h", "trellis2_root_latentcopy"),
    ("V21_ifs_bismuth_stepped_transform_d5_iridescent", "trellis2_oneshot_image"),
    ("V21_ifs_bismuth_stepped_transform_d5_iridescent", "trellis2_root_latentcopy"),
    ("V21_ifs_bismuth_stepped_transform_d5_iridescent", "trellis2_generatedroot_meshcopy"),
    ("V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA", "trellis2_oneshot_image"),
    ("V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA", "trellis2_root_latentcopy"),
    ("V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA", "trellis2_generatedroot_meshcopy"),
}


FIELDS = [
    "case_id",
    "case_short",
    "category",
    "family",
    "method_id",
    "method",
    "variant",
    "route_status",
    "priority",
    "claim_role",
    "ready_for_main",
    "root_or_source",
    "condition_image",
    "asset_path",
    "source_path",
    "render_path",
    "preview_path",
    "metrics_source",
    "vertices",
    "faces",
    "file_size_mb",
    "raw_component_count",
    "welded_component_count",
    "occupancy_component_count_6n",
    "largest_occupancy_component_ratio_6n",
    "LCR",
    "copy_repetition_score",
    "projection_used",
    "latent_update_used",
    "generator_calls_after_root",
    "weld_boolean_or_remesh_used",
    "post_copy_smoothing_iterations",
    "render_import_success",
    "visual_qa_status",
    "failure_label",
    "missing_reason",
    "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    extra = [k for row in rows for k in row if k not in FIELDS]
    fieldnames = FIELDS + sorted(set(extra))
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def rel_exists(path: str) -> bool:
    if not path:
        return False
    p = Path(path)
    return p.exists() if p.is_absolute() else (ROOT / p).exists()


def case_by_id() -> dict[str, dict[str, str]]:
    return {case["case_id"]: case for case in CASES}


def method_id_from_label(label: str, variant: str = "") -> str:
    if label in METHOD_ALIASES:
        mid = METHOD_ALIASES[label]
    elif "Hunyuan text-root" in label:
        mid = "hunyuan_root_meshcopy_smooth" if "laplacian" in variant else "hunyuan_root_meshcopy"
    elif "latent" in label.lower():
        mid = "trellis2_root_latentcopy"
    elif "one-shot" in label.lower():
        mid = "trellis2_oneshot_image"
    elif "mesh" in label.lower():
        mid = "trellis2_generatedroot_meshcopy"
    elif "ours" in label.lower() or "ps-rslg" in label.lower():
        mid = "ps_rslg"
    else:
        mid = "other"
    if mid == "hunyuan_root_meshcopy" and "laplacian" in variant:
        return "hunyuan_root_meshcopy_smooth"
    return mid


def base_grid() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in CASES:
        for method_id in METHOD_ROWS:
            priority = "P0" if (case["case_id"], method_id) in P0_BY_CASE_METHOD else "P1"
            if method_id in {"classical_proc", "classical_smooth", "proc_trellis2_texture"}:
                priority = "P1"
            if method_id == "hunyuan_root_meshcopy_smooth":
                priority = "P2"
            route_status = "needs_remote" if method_id.startswith(("hunyuan", "trellis2")) else "needs_local"
            if method_id == "ps_rslg":
                route_status = "ready" if rel_exists(case["ps_asset"]) else "needs_visual_qa"
                priority = "P0" if route_status != "ready" else "P1"
            rows.append(
                {
                    "case_id": case["case_id"],
                    "case_short": case["case_short"],
                    "category": case["category"],
                    "family": case["family"],
                    "method_id": method_id,
                    "method": method_id,
                    "variant": "",
                    "route_status": route_status,
                    "priority": priority,
                    "claim_role": "positive" if method_id == "ps_rslg" else "baseline",
                    "ready_for_main": "no",
                    "root_or_source": case["root_or_source"],
                    "asset_path": case["ps_asset"] if method_id == "ps_rslg" else "",
                    "preview_path": case["preview"],
                    "missing_reason": "" if method_id == "ps_rslg" and rel_exists(case["ps_asset"]) else "route not yet generated or not yet mapped",
                    "notes": case["priority_note"],
                }
            )
    return rows


def key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (str(row.get("case_id", "")), str(row.get("method_id", "")), str(row.get("variant", "")))


def upsert(rows: list[dict[str, Any]], new_row: dict[str, Any]) -> None:
    new_key = key(new_row)
    for i, old in enumerate(rows):
        if key(old) == new_key:
            merged = old.copy()
            merged.update({k: v for k, v in new_row.items() if v not in ("", None)})
            rows[i] = merged
            return
    rows.append(new_row)


def normalize_existing_baseline(row: dict[str, str]) -> dict[str, Any] | None:
    short_case = row.get("case_id") or row.get("case") or ""
    case_id = SHORT_CASE_ALIASES.get(short_case)
    if not case_id:
        return None
    cases = case_by_id()
    case = cases[case_id]
    method_label = row.get("method", "")
    variant = row.get("variant", "")
    method_id = method_id_from_label(method_label, variant)
    if method_id == "other":
        return None
    status = row.get("status", "")
    route_status = "ready" if status in {"success", "fragmented", "fragmented_copy_paste", "smoothed_copy_paste"} else status or "mapped"
    if "blocked" in route_status or "missing" in route_status:
        ready = "no"
    else:
        ready = "yes" if method_id != "ps_rslg" or status == "success" else "needs_label"
    return {
        "case_id": case_id,
        "case_short": case["case_short"],
        "category": case["category"],
        "family": case["family"],
        "method_id": method_id,
        "method": method_label or method_id,
        "variant": variant,
        "route_status": route_status,
        "priority": "P0" if (case_id, method_id) in P0_BY_CASE_METHOD else "P1",
        "claim_role": "positive" if method_id == "ps_rslg" else "baseline",
        "ready_for_main": ready,
        "root_or_source": case["root_or_source"],
        "asset_path": row.get("asset_path") or row.get("glb_path") or "",
        "source_path": row.get("source_path") or row.get("obj_path") or "",
        "render_path": row.get("render_path") or row.get("preview_path") or "",
        "preview_path": row.get("preview_path") or case["preview"],
        "metrics_source": str(BASELINE_MASTER.relative_to(ROOT)),
        "vertices": row.get("vertices", ""),
        "faces": row.get("faces", ""),
        "file_size_mb": row.get("file_size_mb", ""),
        "raw_component_count": row.get("raw_component_count", ""),
        "welded_component_count": row.get("welded_component_count", ""),
        "occupancy_component_count_6n": row.get("occupancy_component_count_6n", ""),
        "largest_occupancy_component_ratio_6n": row.get("largest_occupancy_component_ratio_6n", ""),
        "LCR": row.get("LCR", ""),
        "copy_repetition_score": row.get("copy_repetition_score", ""),
        "projection_used": row.get("projection_used", ""),
        "latent_update_used": row.get("latent_update_used", ""),
        "generator_calls_after_root": row.get("generator_calls_after_root", ""),
        "weld_boolean_or_remesh_used": row.get("weld_boolean_or_remesh_used", ""),
        "post_copy_smoothing_iterations": row.get("post_copy_smoothing_iterations", ""),
        "render_import_success": row.get("render_import_success", ""),
        "visual_qa_status": row.get("visual_qa_status") or status,
        "failure_label": row.get("failure_label", ""),
        "missing_reason": row.get("missing_reason", ""),
        "notes": row.get("notes", ""),
    }


def normalize_hunyuan_text_root(row: dict[str, str]) -> dict[str, Any] | None:
    case_id = SHORT_CASE_ALIASES.get(row.get("case_id", ""))
    if not case_id:
        return None
    cases = case_by_id()
    case = cases[case_id]
    variant = row.get("variant", "")
    method_id = "hunyuan_root_meshcopy_smooth" if row.get("post_copy_smoothing_iterations", "0") not in {"", "0"} else "hunyuan_root_meshcopy"
    return {
        "case_id": case_id,
        "case_short": case["case_short"],
        "category": case["category"],
        "family": case["family"],
        "method_id": method_id,
        "method": "Hunyuan text-root mesh-space recursion",
        "variant": variant,
        "route_status": "ready",
        "priority": "P0" if method_id == "hunyuan_root_meshcopy" else "P2",
        "claim_role": "mesh_based_baseline",
        "ready_for_main": "yes" if method_id == "hunyuan_root_meshcopy" else "supplement",
        "root_or_source": row.get("root_glb") or case["root_or_source"],
        "asset_path": row.get("glb_path", ""),
        "source_path": row.get("obj_path", ""),
        "render_path": row.get("preview_path", ""),
        "preview_path": row.get("preview_path") or case["preview"],
        "metrics_source": str(HUNYUAN_TEXT_ROOT.relative_to(ROOT)),
        "vertices": row.get("vertices", ""),
        "faces": row.get("faces", ""),
        "file_size_mb": row.get("file_size_mb", ""),
        "raw_component_count": row.get("raw_component_count", ""),
        "occupancy_component_count_6n": row.get("occupancy_component_count_6n", ""),
        "largest_occupancy_component_ratio_6n": row.get("largest_occupancy_component_ratio_6n", row.get("LCR", "")),
        "LCR": row.get("LCR", ""),
        "copy_repetition_score": row.get("copy_repetition_score", ""),
        "projection_used": row.get("projection_used", "0"),
        "latent_update_used": row.get("latent_update_used", "0"),
        "generator_calls_after_root": row.get("generator_calls_after_root", "0"),
        "weld_boolean_or_remesh_used": row.get("weld_boolean_or_remesh_used", "0"),
        "post_copy_smoothing_iterations": row.get("post_copy_smoothing_iterations", ""),
        "render_import_success": "present" if rel_exists(row.get("glb_path", "")) else "remote_only_or_missing_local",
        "visual_qa_status": row.get("status", ""),
        "failure_label": row.get("failure_label", "copy_repetition_without_recursive_state"),
        "missing_reason": "",
        "notes": row.get("notes", ""),
    }


def normalize_exp3_trellis2_metric(row: dict[str, str]) -> dict[str, Any] | None:
    label = row.get("label", "")
    case_short = ""
    method_id = ""
    variant = ""
    if label.startswith("trellis2_oneshot__"):
        tail = label.removeprefix("trellis2_oneshot__")
        case_short = tail.split("_target_seed", 1)[0]
        method_id = "trellis2_oneshot_image"
        variant = "target_guide_seed2026061101"
    elif label.startswith("trellis2_latentcopy__"):
        tail = label.removeprefix("trellis2_latentcopy__")
        case_short = tail.split("_root_seed", 1)[0]
        method_id = "trellis2_root_latentcopy"
        variant = "root_guide_copy_shift_upper_z_seed2026061201"
    else:
        return None
    case_id = None
    for candidate in CASES:
        if candidate["case_short"] == case_short:
            case_id = candidate["case_id"]
            case = candidate
            break
    if not case_id:
        return None
    lcr = row.get("largest_occupancy_component_ratio_6n", "")
    try:
        lcr_f = float(lcr)
        status = "success" if lcr_f >= 0.98 and method_id == "trellis2_oneshot_image" else "fragmented_or_uncontrolled"
    except Exception:
        status = "metrics_ready_visual_pending"
    return {
        "case_id": case_id,
        "case_short": case["case_short"],
        "category": case["category"],
        "family": case["family"],
        "method_id": method_id,
        "method": "Trellis2 one-shot image-conditioned" if method_id == "trellis2_oneshot_image" else "Trellis2 trivial latent copy",
        "variant": variant,
        "route_status": "ready",
        "priority": "P0" if (case_id, method_id) in P0_BY_CASE_METHOD else "P1",
        "claim_role": "baseline",
        "ready_for_main": "needs_visual_qa",
        "root_or_source": case["root_or_source"],
        "asset_path": row.get("path", ""),
        "source_path": row.get("path", ""),
        "render_path": "",
        "preview_path": case["preview"],
        "metrics_source": str(TRELLIS2_EXP3_METRICS.relative_to(ROOT)),
        "vertices": row.get("vertices", ""),
        "faces": row.get("faces", ""),
        "file_size_mb": "",
        "raw_component_count": row.get("component_count", ""),
        "welded_component_count": row.get("welded_component_count", ""),
        "occupancy_component_count_6n": row.get("occupancy_component_count_6n", ""),
        "largest_occupancy_component_ratio_6n": row.get("largest_occupancy_component_ratio_6n", ""),
        "LCR": row.get("largest_occupancy_component_ratio_6n", ""),
        "copy_repetition_score": "1.0" if method_id == "trellis2_root_latentcopy" else "0.0",
        "projection_used": "0",
        "latent_update_used": "0" if method_id == "trellis2_root_latentcopy" else "N/A",
        "generator_calls_after_root": "0" if method_id == "trellis2_root_latentcopy" else "1",
        "weld_boolean_or_remesh_used": "0",
        "post_copy_smoothing_iterations": "0",
        "render_import_success": "present" if rel_exists(row.get("path", "")) else "remote_only_or_missing_local",
        "visual_qa_status": status,
        "failure_label": "one_shot_no_recursive_state" if method_id == "trellis2_oneshot_image" else "trivial_latent_copy_without_projection",
        "missing_reason": "",
        "notes": "Experiment 3 P0 Trellis2 baseline from explicit root/target guide.",
    }


def normalize_exp3_trellis2_generatedroot(row: dict[str, str]) -> dict[str, Any] | None:
    case_short = row.get("case_short", "")
    if not case_short:
        label = row.get("label", "")
        if label.startswith("trellis2_generatedroot_meshcopy__"):
            case_short = label.removeprefix("trellis2_generatedroot_meshcopy__")
    case = None
    case_id = None
    for candidate in CASES:
        if candidate["case_short"] == case_short:
            case = candidate
            case_id = candidate["case_id"]
            break
    if not case or not case_id:
        return None
    obj_path = row.get("obj_path") or row.get("path", "")
    glb_path = row.get("glb_path", "")
    preview_path = row.get("preview_path", "")
    return {
        "case_id": case_id,
        "case_short": case["case_short"],
        "category": case["category"],
        "family": case["family"],
        "method_id": "trellis2_generatedroot_meshcopy",
        "method": "Trellis2 generated-root mesh-space recursion",
        "variant": row.get("variant", "identity_root_full_srt_depth02_direct"),
        "route_status": row.get("status", "ready") or "ready",
        "priority": "P0" if (case_id, "trellis2_generatedroot_meshcopy") in P0_BY_CASE_METHOD else "P1",
        "claim_role": "mesh_based_baseline",
        "ready_for_main": "needs_visual_qa",
        "root_or_source": row.get("root_mesh") or case["root_or_source"],
        "asset_path": glb_path or obj_path,
        "source_path": obj_path,
        "render_path": preview_path,
        "preview_path": preview_path or case["preview"],
        "metrics_source": str(TRELLIS2_GENERATEDROOT_METRICS.relative_to(ROOT)),
        "vertices": row.get("vertices", ""),
        "faces": row.get("faces", ""),
        "file_size_mb": row.get("file_size_mb", ""),
        "raw_component_count": row.get("component_count", row.get("raw_component_count", "")),
        "welded_component_count": row.get("welded_component_count", ""),
        "occupancy_component_count_6n": row.get("occupancy_component_count_6n", ""),
        "largest_occupancy_component_ratio_6n": row.get("largest_occupancy_component_ratio_6n", ""),
        "LCR": row.get("largest_occupancy_component_ratio_6n", row.get("LCR", "")),
        "copy_repetition_score": row.get("copy_repetition_score", "1.0"),
        "projection_used": row.get("projection_used", "0"),
        "latent_update_used": row.get("latent_update_used", "0"),
        "generator_calls_after_root": row.get("generator_calls_after_root", "0"),
        "weld_boolean_or_remesh_used": row.get("weld_boolean_or_remesh_used", "0"),
        "post_copy_smoothing_iterations": row.get("post_copy_smoothing_iterations", "0"),
        "render_import_success": "present" if rel_exists(glb_path or obj_path) else "remote_only_or_missing_local",
        "visual_qa_status": row.get("status", "fragmented_copy_paste"),
        "failure_label": row.get("failure_label", "generated_root_mesh_copy_without_recursive_state"),
        "missing_reason": "",
        "notes": "Trellis2 root-guide identity mesh copied by deterministic S/R/T in mesh space; no projection, handles, or recursive latent update.",
    }


def normalize_exp3_ps_rslg_metric(row: dict[str, str]) -> dict[str, Any] | None:
    case_short = row.get("case_short", "")
    case = None
    case_id = None
    for candidate in CASES:
        if candidate["case_short"] == case_short:
            case = candidate
            case_id = candidate["case_id"]
            break
    if not case or not case_id:
        return None
    status = row.get("status", "")
    return {
        "case_id": case_id,
        "case_short": case["case_short"],
        "category": case["category"],
        "family": case["family"],
        "method_id": "ps_rslg",
        "method": "PS-RSLG",
        "variant": row.get("label", "experiment3_selected_positive"),
        "route_status": "ready",
        "priority": "P0" if status == "qa_gated_depth_sequence" else "P1",
        "claim_role": "positive",
        "ready_for_main": "needs_visual_qa" if status == "qa_gated_depth_sequence" else "yes",
        "root_or_source": case["root_or_source"],
        "asset_path": row.get("path", "") or case["ps_asset"],
        "source_path": row.get("path", ""),
        "render_path": "",
        "preview_path": case["preview"],
        "metrics_source": str(PS_RSLG_EXP3_METRICS.relative_to(ROOT)),
        "vertices": row.get("vertices", ""),
        "faces": row.get("faces", ""),
        "file_size_mb": "",
        "raw_component_count": row.get("raw_component_count", ""),
        "occupancy_component_count_6n": row.get("occupancy_component_count_6n", ""),
        "largest_occupancy_component_ratio_6n": row.get("LCR", ""),
        "LCR": row.get("LCR", ""),
        "copy_repetition_score": "0.0",
        "projection_used": "yes",
        "latent_update_used": "yes",
        "generator_calls_after_root": "",
        "weld_boolean_or_remesh_used": "0",
        "post_copy_smoothing_iterations": "0",
        "render_import_success": "present" if rel_exists(row.get("path", "")) else "preview_or_metric_only",
        "visual_qa_status": status or "selected_positive",
        "failure_label": "",
        "missing_reason": "",
        "notes": row.get("notes", ""),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    method_counts: dict[str, int] = {}
    for row in rows:
        status_counts[str(row.get("route_status", ""))] = status_counts.get(str(row.get("route_status", "")), 0) + 1
        priority_counts[str(row.get("priority", ""))] = priority_counts.get(str(row.get("priority", "")), 0) + 1
        method_counts[str(row.get("method_id", ""))] = method_counts.get(str(row.get("method_id", "")), 0) + 1
    return {
        "schema": "experiment3_sparse_latent_vs_meshspace_manifest_v1",
        "row_count": len(rows),
        "case_count": len({row.get("case_id") for row in rows}),
        "method_rows": METHOD_ROWS,
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "method_counts": method_counts,
        "sources": {
            "baseline_master": str(BASELINE_MASTER),
            "hunyuan_text_root": str(HUNYUAN_TEXT_ROOT),
            "trellis2_exp3_metrics": str(TRELLIS2_EXP3_METRICS),
            "trellis2_generatedroot_metrics": str(TRELLIS2_GENERATEDROOT_METRICS),
            "ps_rslg_exp3_metrics": str(PS_RSLG_EXP3_METRICS),
        },
        "notes": [
            "This manifest is selected-final-only and does not recursively scan the repository.",
            "Hunyuan full recursive guide rows are not treated as fair mesh-space recursion.",
            "Occupancy LCR must be interpreted with raw components and route flags.",
            "Rows marked ready still need unified render/zoom QA before final paper use.",
        ],
    }


def prune_shadowed_placeholders(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop base-grid placeholders once a concrete variant exists.

    The base grid is useful as a to-do list, but it should not survive beside a
    concrete metric row for the same case and method. Otherwise downstream table
    builders see both "needs_remote" and "ready" for a completed baseline.
    """

    concrete: set[tuple[str, str]] = set()
    for row in rows:
        has_variant = bool(str(row.get("variant", "")).strip())
        has_metrics = bool(str(row.get("metrics_source", "")).strip())
        has_asset = bool(str(row.get("asset_path", "")).strip() or str(row.get("source_path", "")).strip())
        status = str(row.get("route_status", ""))
        if (has_variant or has_metrics or has_asset) and status not in {"needs_remote", "needs_local"}:
            concrete.add((str(row.get("case_id", "")), str(row.get("method_id", ""))))

    pruned: list[dict[str, Any]] = []
    for row in rows:
        pair = (str(row.get("case_id", "")), str(row.get("method_id", "")))
        is_placeholder = (
            pair in concrete
            and not str(row.get("variant", "")).strip()
            and str(row.get("route_status", "")) in {"needs_remote", "needs_local"}
            and str(row.get("missing_reason", "")).startswith("route not yet generated")
        )
        if not is_placeholder:
            pruned.append(row)
    return pruned


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    rows = base_grid()
    for existing in read_csv(BASELINE_MASTER):
        normalized = normalize_existing_baseline(existing)
        if normalized:
            upsert(rows, normalized)
    for existing in read_csv(HUNYUAN_TEXT_ROOT):
        normalized = normalize_hunyuan_text_root(existing)
        if normalized:
            upsert(rows, normalized)
    for existing in read_csv(TRELLIS2_EXP3_METRICS):
        normalized = normalize_exp3_trellis2_metric(existing)
        if normalized:
            upsert(rows, normalized)
    for existing in read_csv(TRELLIS2_GENERATEDROOT_METRICS):
        normalized = normalize_exp3_trellis2_generatedroot(existing)
        if normalized:
            upsert(rows, normalized)
    for existing in read_csv(PS_RSLG_EXP3_METRICS):
        normalized = normalize_exp3_ps_rslg_metric(existing)
        if normalized:
            upsert(rows, normalized)

    rows = prune_shadowed_placeholders(rows)
    rows.sort(key=lambda r: (str(r.get("case_id", "")), str(r.get("priority", "")), str(r.get("method_id", "")), str(r.get("variant", ""))))
    out_csv = args.out_dir / "experiment3_master_manifest.csv"
    write_csv(out_csv, rows)
    summary = summarize(rows)
    summary["outputs"] = {"master_manifest_csv": str(out_csv)}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
