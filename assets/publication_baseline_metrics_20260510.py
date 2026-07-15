#!/usr/bin/env python3
"""Selected-final-only publication baseline metrics aggregator.

This entry point deliberately avoids recursive scans.  It reads a small
manifest, reuses existing gen3d summary rows when available, and only computes
mesh metrics for explicitly listed final assets.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_OUT = PROJECT_ROOT / "results" / "publication_baseline_metrics_20260510"
GEN3D_SUMMARY = PROJECT_ROOT / "results" / "gen3d_baseline_metrics_20260510" / "gen3d_baseline_summary_table_20260510.csv"
CASE_SELECTION_ROOT = PROJECT_ROOT / "visuals" / "case_selection_by_type_20260510"
HUNYUAN_FULLPOOL = PROJECT_ROOT / "results" / "publication_hunyuan_recursive_guides_20260510" / "hunyuan_recursive_guides_fullpool_metrics.csv"
HUNYUAN_TOPOLOGY = PROJECT_ROOT / "results" / "publication_hunyuan_recursive_guides_20260510" / "hunyuan_fullpool_failure_labels_20260510.csv"
CORAL_MESH_SPACE = PROJECT_ROOT / "results" / "publication_coral_mesh_space_20260510" / "coral_mesh_space_metrics.csv"
HUNYUAN_MESH_SPACE = PROJECT_ROOT / "results" / "publication_hunyuan_mesh_space_20260510" / "hunyuan_mesh_space_metrics.csv"


def load_mesh_metrics_module() -> Any:
    path = PROJECT_ROOT / "assets" / "recursive_growth_mesh_metrics.py"
    spec = importlib.util.spec_from_file_location("recursive_growth_mesh_metrics", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load metric module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], preferred: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(preferred or [])
    seen = set(fieldnames)
    for row in rows:
        for key in row:
            if key not in seen:
                fieldnames.append(key)
                seen.add(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def rel(path: str | Path) -> str:
    p = Path(path)
    try:
        if p.is_absolute():
            return str(p.relative_to(PROJECT_ROOT))
    except Exception:
        pass
    return str(p)


def rel_resolved(path: str | Path) -> str:
    p = Path(path).resolve()
    try:
        return str(p.relative_to(PROJECT_ROOT))
    except Exception:
        return str(p)


def first_existing(*items: str) -> str:
    for item in items:
        if item and (PROJECT_ROOT / item).exists():
            return item
        if item and Path(item).exists():
            return item
    for item in items:
        if item:
            return item
    return ""


def baseline_family(method: str) -> str:
    text = method.lower()
    if "ours" in text or "ps-rslg" in text:
        return "ours_psrslg"
    if "latent" in text:
        return "latent_copy"
    if "mesh" in text:
        return "mesh_space"
    if "hunyuan" in text:
        return "hunyuan"
    if "trellis2" in text or "trellis.2" in text:
        return "trellis2_one_shot"
    if "trellis" in text:
        return "trellis1_one_shot"
    return "other"


def case_category(case: str) -> str:
    text = case.lower()
    if any(k in text for k in ("vine", "root", "tree", "plant", "leaf")):
        return "plant_root_tree"
    if any(k in text for k in ("pyrite", "bismuth", "crystal", "coral", "dla", "frontier")):
        return "crystal_coral_dla"
    if any(k in text for k in ("gear", "scifi", "mechanical", "radial", "arch")):
        return "sci_fi_mechanical"
    return "baseline_or_other"


def failure_label(status: str, method: str, missing_reason: str = "") -> str:
    text = f"{status} {method} {missing_reason}".lower()
    if "blocked" in text:
        return "blocked_environment_or_weights"
    if "missing" in text:
        return "missing_local_artifact"
    if "fragment" in text:
        return "fragmented_or_low_lcr"
    if "category mismatch" in text:
        return "category_mismatch"
    if "needs" in text:
        return "needs_visual_qa"
    if "success" in text:
        return ""
    return status


def normalize_gen3d_row(row: dict[str, str]) -> dict[str, Any]:
    method = row.get("method", "")
    status = row.get("status", "")
    asset = first_existing(row.get("asset_path", ""), row.get("source_path", ""))
    return {
        "case_id": row.get("case", ""),
        "category": case_category(row.get("case", "")),
        "method": method,
        "variant": row.get("variant", ""),
        "baseline_family": baseline_family(method),
        "status": status,
        "case_pool_role": "baseline_matrix",
        "recommended_subset": "yes" if row.get("case", "") in {"vine", "pyrite", "coral"} else "",
        "source_path": row.get("source_path", ""),
        "asset_path": asset,
        "vertices": row.get("vertices", ""),
        "faces": row.get("faces", ""),
        "file_size_mb": row.get("file_size_mb", ""),
        "raw_component_count": row.get("mesh_components", ""),
        "welded_component_count": "",
        "occupancy_component_count_6n": row.get("occupancy_components_6n", ""),
        "largest_occupancy_component_ratio_6n": row.get("occupancy_lcr_6n", row.get("LCR", "")),
        "LCR": row.get("LCR", ""),
        "root_reachability": "",
        "orphan_fragment_ratio": "",
        "render_import_success": "present" if asset and (PROJECT_ROOT / asset).exists() else "",
        "visual_qa_status": status,
        "failure_label": failure_label(status, method, row.get("notes", "")),
        "missing_reason": row.get("notes", "") if status in {"missing", "blocked"} else "",
        "notes": row.get("notes", ""),
    }


def blocked_future_rows() -> list[dict[str, Any]]:
    methods = [
        ("TRELLIS image one-shot", "trellis1_one_shot", "blocked: Lane A has not delivered runnable TRELLIS non-2 local outputs"),
        ("Hunyuan3D 2.0 image one-shot", "hunyuan", "blocked: Lane A has not delivered Hunyuan image-to-3D outputs"),
        ("Hunyuan3D 2.0 image+texture", "hunyuan", "blocked: Lane A has not delivered Hunyuan textured outputs"),
        ("Hunyuan3D mesh-space generated-root", "mesh_space", "missing: requires Hunyuan root mesh before local mesh-space copy baseline"),
    ]
    cases = ["vine", "pyrite", "coral"]
    rows: list[dict[str, Any]] = []
    for case in cases:
        for method, family, reason in methods:
            status = "blocked" if reason.startswith("blocked") else "missing"
            rows.append(
                {
                    "case_id": case,
                    "category": case_category(case),
                    "method": method,
                    "variant": "pending_remote_drop",
                    "baseline_family": family,
                    "status": status,
                    "case_pool_role": "future_baseline_slot",
                    "recommended_subset": "yes",
                    "source_path": "",
                    "asset_path": "",
                    "remote_drop_expected": f"incoming/{family}/{case}/final.glb",
                    "render_import_success": "not_run",
                    "visual_qa_status": status,
                    "failure_label": failure_label(status, method, reason),
                    "missing_reason": reason,
                    "notes": "Fill this row by rerunning this script with --input-manifest after Lane A pulls the artifact.",
                }
            )
    return rows


def upsert_rows(rows: list[dict[str, Any]], updates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Replace rows with the same case/method, otherwise append.

    The original manifest intentionally contained future blocked/missing slots.
    Once a baseline lands, the manifest should show the landed evidence instead
    of retaining a contradictory blocked slot for the same case/method.
    """
    by_key: dict[tuple[str, str], dict[str, Any]] = {(str(r.get("case_id", "")), str(r.get("method", ""))): r for r in rows}
    order = [(str(r.get("case_id", "")), str(r.get("method", ""))) for r in rows]
    for update in updates:
        key = (str(update.get("case_id", "")), str(update.get("method", "")))
        if key not in by_key:
            order.append(key)
        by_key[key] = update
    return [by_key[key] for key in order]


def hunyuan_shape_only_updates() -> list[dict[str, Any]]:
    case_map = {
        "vine_lsystem_grammar": "vine",
        "pyrite_lattice": "pyrite",
        "coral_frontier": "coral",
    }
    topology = {r.get("case_id", ""): r for r in read_csv(HUNYUAN_TOPOLOGY)}
    rows: list[dict[str, Any]] = []
    for row in read_csv(HUNYUAN_FULLPOOL):
        case = case_map.get(row.get("case_id", ""))
        if not case:
            continue
        topo = topology.get(row.get("case_id", ""), {})
        local_glb = Path(row.get("output_glb", "").replace(
            "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507",
            str(PROJECT_ROOT),
        ))
        case_id = row.get("case_id", "")
        local_render = (
            PROJECT_ROOT
            / "results"
            / "publication_hunyuan_recursive_guides_20260510"
            / "render_qa_fullpool_white_600"
            / "flattened_white"
            / f"{case_id}_iso.png"
        )
        rows.append(
            {
                "case_id": case,
                "category": case_category(case),
                "method": "Hunyuan3D 2.0 image one-shot",
                "variant": f"shape-only {case_id} steps30 oct320",
                "baseline_family": "hunyuan",
                "status": "generated_import_render_QA_pending_topology_metrics",
                "case_pool_role": "baseline_matrix",
                "recommended_subset": "yes",
                "source_path": row.get("input_image", ""),
                "asset_path": rel(local_glb),
                "render_path": rel(local_render),
                "manifest_path": rel(HUNYUAN_FULLPOOL),
                "vertices": row.get("vertices", ""),
                "faces": row.get("faces", ""),
                "file_size_mb": row.get("file_size_mb", ""),
                "raw_component_count": topo.get("raw_component_count", ""),
                "welded_component_count": "",
                "occupancy_component_count_6n": topo.get("occupancy_component_count_6n", ""),
                "largest_occupancy_component_ratio_6n": topo.get("LCR", ""),
                "LCR": topo.get("LCR", ""),
                "root_reachability": "",
                "orphan_fragment_ratio": "",
                "render_import_success": "present",
                "visual_qa_status": "fullpool_white_render_QA_done",
                "failure_label": topo.get("failure_label", "topology_metrics_pending"),
                "missing_reason": "",
                "notes": "Shape-only Hunyuan image-to-3D row. Generated GLB, local trimesh import QA, white render QA, and topology proxy metrics are done; no texture, recursive state, root reachability, or topology correctness claim. "
                + topo.get("visual_note", ""),
            }
        )
    return rows


def coral_mesh_space_update() -> list[dict[str, Any]]:
    target_variant = "coral_frontier_branch full_srt depth=2 direct merge"
    for row in read_csv(CORAL_MESH_SPACE):
        if row.get("variant") != target_variant:
            continue
        return [
            {
                "case_id": "coral",
                "category": case_category("coral"),
                "method": "Mesh-space generated-root baseline",
                "variant": "full_srt depth=2 direct merge",
                "baseline_family": "mesh_space",
                "status": row.get("status", "fragmented_copy_paste"),
                "case_pool_role": "baseline_matrix",
                "recommended_subset": "yes",
                "source_path": row.get("obj_path", ""),
                "asset_path": row.get("glb_path", ""),
                "render_path": row.get("preview_path", ""),
                "manifest_path": rel(CORAL_MESH_SPACE),
                "vertices": row.get("vertices", ""),
                "faces": row.get("faces", ""),
                "file_size_mb": row.get("file_size_mb", ""),
                "raw_component_count": row.get("raw_component_count", ""),
                "welded_component_count": row.get("welded_component_count", ""),
                "occupancy_component_count_6n": row.get("occupancy_component_count_6n", ""),
                "largest_occupancy_component_ratio_6n": row.get("largest_occupancy_component_ratio_6n", ""),
                "LCR": row.get("LCR", row.get("largest_occupancy_component_ratio_6n", "")),
                "root_reachability": "",
                "orphan_fragment_ratio": "",
                "render_import_success": "present",
                "visual_qa_status": "white_preview_done",
                "failure_label": row.get("failure_label", "fragmented_or_low_lcr"),
                "missing_reason": "",
                "notes": "Coral one-shot root mesh copied by S/R/T and directly concatenated; no generator, no projection, no repair, no weld/boolean/remesh. High occupancy LCR is not a success claim because raw face islands and copy repetition remain the diagnostic.",
            }
        ]
    return []


def hunyuan_mesh_space_updates() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in read_csv(HUNYUAN_MESH_SPACE):
        case = row.get("case", "")
        if case not in {"vine", "pyrite", "coral"}:
            continue
        rows.append(
            {
                "case_id": case,
                "category": case_category(case),
                "method": "Hunyuan3D mesh-space generated-root",
                "variant": row.get("variant", ""),
                "baseline_family": "mesh_space",
                "status": row.get("status", "fragmented_copy_paste"),
                "case_pool_role": "baseline_matrix",
                "recommended_subset": "yes",
                "source_path": row.get("obj_path", ""),
                "asset_path": row.get("glb_path", ""),
                "render_path": row.get("preview_path", ""),
                "manifest_path": rel(HUNYUAN_MESH_SPACE),
                "vertices": row.get("vertices", ""),
                "faces": row.get("faces", ""),
                "file_size_mb": row.get("file_size_mb", ""),
                "raw_component_count": row.get("raw_component_count", ""),
                "welded_component_count": row.get("welded_component_count", ""),
                "occupancy_component_count_6n": row.get("occupancy_component_count_6n", ""),
                "largest_occupancy_component_ratio_6n": row.get("largest_occupancy_component_ratio_6n", ""),
                "LCR": row.get("LCR", row.get("largest_occupancy_component_ratio_6n", "")),
                "root_reachability": "",
                "orphan_fragment_ratio": "",
                "render_import_success": "present",
                "visual_qa_status": "white_preview_done",
                "failure_label": row.get("failure_label", "fragmented_or_copy_repetition"),
                "missing_reason": "",
                "notes": "Hunyuan shape-only one-shot root mesh copied by S/R/T and directly concatenated; no generator call, latent update, projection, weld, boolean, remesh, or repair. This is a mesh-space negative control, not a Hunyuan recursive-state row.",
            }
        )
    return rows


def compute_metric_for_path(path_text: str, label: str, metrics_module: Any, args: argparse.Namespace) -> dict[str, Any]:
    if not path_text:
        return {}
    path = Path(path_text)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if not path.exists():
        return {}
    metric_args = argparse.Namespace(
        occupancy_resolution=args.occupancy_resolution,
        box_resolutions=args.box_resolutions,
        sample_limit=args.sample_limit,
        weld_tolerance=args.weld_tolerance,
        primary_connectivity="occupancy",
    )
    row = metrics_module.metric_one(path, label, metric_args)
    row["file_size_mb"] = round(path.stat().st_size / (1024 * 1024), 6)
    return row


def normalize_manifest_row(row: dict[str, str], metrics_module: Any, args: argparse.Namespace) -> dict[str, Any]:
    case = row.get("case_id") or row.get("case") or "unknown_case"
    method = row.get("method", "unknown_method")
    status = row.get("status", "")
    asset = first_existing(row.get("asset_path", ""), row.get("source_path", ""), row.get("mesh_path", ""))
    metric = compute_metric_for_path(asset, f"{case}_{method}", metrics_module, args)
    if not status:
        status = "success" if metric else "missing"
    missing_reason = row.get("missing_reason", "")
    if status == "missing" and not missing_reason:
        missing_reason = f"explicit manifest asset not found: {asset}"
    return {
        "case_id": case,
        "category": row.get("category", case_category(case)),
        "method": method,
        "variant": row.get("variant", ""),
        "baseline_family": row.get("baseline_family", baseline_family(method)),
        "status": status,
        "case_pool_role": row.get("case_pool_role", "external_manifest"),
        "recommended_subset": row.get("recommended_subset", ""),
        "input_target_path": row.get("input_target_path", ""),
        "source_path": row.get("source_path", ""),
        "asset_path": asset,
        "render_path": row.get("render_path", ""),
        "manifest_path": row.get("manifest_path", ""),
        "vertices": metric.get("vertices", row.get("vertices", "")),
        "faces": metric.get("faces", row.get("faces", "")),
        "file_size_mb": metric.get("file_size_mb", row.get("file_size_mb", "")),
        "raw_component_count": metric.get("component_count", row.get("raw_component_count", "")),
        "welded_component_count": metric.get("welded_component_count", row.get("welded_component_count", "")),
        "occupancy_component_count_6n": metric.get("occupancy_component_count_6n", row.get("occupancy_component_count_6n", "")),
        "largest_occupancy_component_ratio_6n": metric.get(
            "largest_occupancy_component_ratio_6n", row.get("largest_occupancy_component_ratio_6n", "")
        ),
        "LCR": metric.get("primary_largest_component_ratio", row.get("LCR", "")),
        "root_reachability": row.get("root_reachability", ""),
        "orphan_fragment_ratio": row.get("orphan_fragment_ratio", ""),
        "render_import_success": row.get("render_import_success", "present" if metric else "not_verified"),
        "visual_qa_status": row.get("visual_qa_status", status),
        "failure_label": row.get("failure_label", failure_label(status, method, missing_reason)),
        "missing_reason": missing_reason,
        "notes": row.get("notes", ""),
    }


def case_pool_rows() -> list[dict[str, Any]]:
    recommended = {
        "plant_root_tree": {"001", "002", "005", "007", "009"},
        "crystal_coral_dla": {"001", "002", "003", "004", "005", "006"},
        "gen3d_baselines": {"001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012"},
        "ablation_depth": {"001", "002", "009", "010", "011", "012", "013"},
        "sci_fi_mechanical": {"001", "004", "006"},
    }
    rows: list[dict[str, Any]] = []
    for category_dir in sorted(p for p in CASE_SELECTION_ROOT.iterdir() if p.is_dir()):
        files = sorted(p for p in category_dir.iterdir() if p.is_file() or p.is_symlink())
        for p in files:
            prefix = p.name.split("_", 1)[0]
            rows.append(
                {
                    "category": category_dir.name,
                    "case_candidate": p.stem,
                    "candidate_path": rel(p),
                    "source_path": rel_resolved(p) if p.is_symlink() else rel(p),
                    "recommended": "yes" if prefix in recommended.get(category_dir.name, set()) else "",
                    "status": "available",
                    "notes": "",
                }
            )
        if len(files) < 10:
            rows.append(
                {
                    "category": category_dir.name,
                    "case_candidate": "__category_gap__",
                    "candidate_path": "",
                    "source_path": "",
                    "recommended": "",
                    "status": "gap",
                    "notes": f"Only {len(files)} local candidates; needs {10 - len(files)} more to reach the Lane B target of 10.",
                }
            )
    return rows


def latex_table(rows: list[dict[str, Any]]) -> str:
    selected = [r for r in rows if r.get("recommended_subset") == "yes" and r.get("case_id") in {"vine", "pyrite", "coral"}]
    header = [
        "% Auto-generated draft. Check visual QA before paper use.",
        "\\begin{tabular}{llllrrrl}",
        "\\toprule",
        "Case & Method & Status & Variant & Vertices & Faces & LCR & Failure \\\\",
        "\\midrule",
    ]
    body = []
    for r in selected:
        body.append(
            f"{r.get('case_id','')} & {r.get('method','')} & {r.get('status','')} & "
            f"{r.get('variant','')} & {r.get('vertices','')} & {r.get('faces','')} & "
            f"{r.get('LCR') or r.get('largest_occupancy_component_ratio_6n','')} & {r.get('failure_label','')} \\\\"
        )
    footer = ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(header + body + footer)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", type=Path, default=None, help="Optional explicit CSV of future pulled rows.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--occupancy-resolution", type=int, default=64)
    parser.add_argument("--box-resolutions", type=int, nargs="+", default=[8, 16, 32, 64])
    parser.add_argument("--sample-limit", type=int, default=200000)
    parser.add_argument("--weld-tolerance", type=float, default=0.0)
    args = parser.parse_args()

    metrics_module = load_mesh_metrics_module()
    rows: list[dict[str, Any]] = [normalize_gen3d_row(r) for r in read_csv(GEN3D_SUMMARY)]
    rows.extend(blocked_future_rows())
    rows = upsert_rows(rows, coral_mesh_space_update())
    rows = upsert_rows(rows, hunyuan_shape_only_updates())
    rows = upsert_rows(rows, hunyuan_mesh_space_updates())
    if args.input_manifest:
        rows = upsert_rows(
            rows,
            [normalize_manifest_row(row, metrics_module, args) for row in read_csv(args.input_manifest)],
        )

    pool = case_pool_rows()
    preferred = [
        "case_id",
        "category",
        "method",
        "variant",
        "baseline_family",
        "status",
        "recommended_subset",
        "source_path",
        "asset_path",
        "render_path",
        "manifest_path",
        "remote_drop_expected",
        "vertices",
        "faces",
        "file_size_mb",
        "raw_component_count",
        "welded_component_count",
        "occupancy_component_count_6n",
        "largest_occupancy_component_ratio_6n",
        "LCR",
        "root_reachability",
        "orphan_fragment_ratio",
        "render_import_success",
        "visual_qa_status",
        "failure_label",
        "missing_reason",
        "notes",
    ]
    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "publication_baseline_master_manifest_20260510.csv", rows, preferred)
    write_csv(args.out / "publication_case_pool_candidates_20260510.csv", pool)
    (args.out / "publication_baseline_table_draft_20260510.tex").write_text(latex_table(rows), encoding="utf-8")
    summary = {
        "schema": "publication_baseline_metrics_selected_final_only_v1",
        "input_manifest": str(args.input_manifest) if args.input_manifest else "",
        "row_count": len(rows),
        "case_pool_row_count": len(pool),
        "status_counts": {status: sum(1 for r in rows if r.get("status") == status) for status in sorted({str(r.get("status", "")) for r in rows})},
        "outputs": {
            "master_manifest_csv": str(args.out / "publication_baseline_master_manifest_20260510.csv"),
            "case_pool_csv": str(args.out / "publication_case_pool_candidates_20260510.csv"),
            "latex_table_draft": str(args.out / "publication_baseline_table_draft_20260510.tex"),
        },
        "notes": [
            "No directory recursion is used; every measured file is listed in an input CSV or the built-in selected manifest.",
            "Blocked/missing rows are intentionally retained for Lane A TRELLIS/Hunyuan drops.",
            "Hunyuan shape-only one-shot rows are generated/import/render-QA rows, not texture or recursive-state proof.",
            "Coral mesh-space generated-root is a direct copy-paste negative control with no projection/repair.",
            "Hunyuan mesh-space generated-root rows copy Hunyuan one-shot root meshes in mesh space; they are negative controls, not Hunyuan recursive-state generation.",
        ],
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
