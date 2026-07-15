#!/usr/bin/env python3
"""Selected-final-only publication ablation aggregation.

This script is intentionally conservative: it reads only named CSV/JSON
summaries and selected final GLB summaries. It does not recurse through large
result trees or recompute mesh metrics.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_OUT = PROJECT_ROOT / "results" / "publication_ablation_metrics_20260510"

SAME_ROOT_VARIANTS = ("traditional", "direct", "final-only", "prune", "bridge", "proposed")
NATURALIZATION_VARIANTS = (
    "rule-only",
    "no-N",
    "weak blend",
    "masked local-N",
    "global-N",
    "with projection",
    "without projection",
    "post-hoc repair baseline",
)

SELECTED_TEXTURING_SUMMARIES = (
    Path("results/gapfill_texturing_selected_20260510/lsystem_rule_only_direct_fork_d3/summary.json"),
    Path("results/gapfill_texturing_selected_20260510/lsystem_noN_alpha0_fork_d3/summary.json"),
    Path("results/gapfill_texturing_selected_20260510/lsystem_weakblend_alpha025_fork_d3/summary.json"),
    Path("results/gapfill_texturing_selected_20260510/lsystem_masked_localN_alpha1_fork_d3/summary.json"),
    Path("results/gapfill_non_tree_texturing_selected_20260510/coral_weakblend_alpha025_fork_d2/summary.json"),
    Path("results/gapfill_non_tree_texturing_selected_20260510/coral_masked_localN_alpha1_fork_d2/summary.json"),
    Path("results/gapfill_non_tree_texturing_selected_20260510/pyrite_weakblend_alpha025_fork_d2/summary.json"),
    Path("results/gapfill_non_tree_texturing_selected_20260510/pyrite_masked_localN_alpha1_fork_d2/summary.json"),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def value(row: dict[str, object], *keys: str) -> str:
    for key in keys:
        val = row.get(key, "")
        if val not in ("", None):
            return str(val)
    return ""


def as_float(val: object, default: float = 0.0) -> float:
    try:
        if val in ("", None):
            return default
        return float(val)
    except Exception:
        return default


def localize_remote_path(path_text: str, root: Path) -> Path | None:
    if not path_text:
        return None
    path = Path(path_text)
    if path.is_absolute() and path.exists():
        return path
    text = str(path)
    marker = "/recursive_3d_generative_growth_20260507/"
    if marker in text:
        rel = text.split(marker, 1)[1]
        candidate = root / rel
        if candidate.exists():
            return candidate
    if not path.is_absolute():
        candidate = root / path
        if candidate.exists():
            return candidate
    return None


def file_size_mb(path: Path | None) -> str:
    if path and path.exists() and path.is_file():
        return f"{path.stat().st_size / (1024 * 1024):.6f}"
    return ""


def mesh_asset_status(mesh_path: str, glb_path: str, root: Path) -> tuple[str, str, str, str]:
    local_mesh = localize_remote_path(mesh_path, root)
    local_glb = localize_remote_path(glb_path, root)
    mesh_exists = "yes" if local_mesh else "no"
    glb_exists = "yes" if local_glb else "no"
    if local_mesh and local_glb:
        status = "final_mesh_and_glb_local"
    elif local_glb:
        status = "final_glb_local_mesh_remote_or_unresolved"
    elif local_mesh:
        status = "final_mesh_local_no_glb"
    elif mesh_path or glb_path:
        status = "metrics_or_summary_only_asset_not_local"
    else:
        status = "missing_asset_path"
    return status, mesh_exists, glb_exists, file_size_mb(local_glb or local_mesh)


def metric_completeness(row: dict[str, str], kind: str) -> str:
    if kind == "same_root":
        required = ("faces", "component_count", "largest_component_ratio")
    elif kind == "naturalization":
        required = ("faces",)
    else:
        required = ("faces", "local_feature_scale_proxy", "terminal_detail_count_proxy", "zoom_retention_score")
    present = sum(1 for key in required if value(row, key))
    return f"{present}/{len(required)}"


def claim_gate(status: str, asset_status: str, completeness: str, notes: str = "") -> str:
    if status != "available":
        return "appendix_missing_or_gap"
    if completeness.startswith("0/"):
        return "asset_or_status_only_needs_metrics"
    if "remote_or_unresolved" in asset_status or "not_local" in asset_status:
        return "metrics_snapshot_needs_local_final_asset"
    if "negative" in notes.lower() or "diagnostic" in notes.lower():
        return "appendix_diagnostic"
    return "appendix_candidate_claim_gated"


def same_root_rows(root: Path) -> list[dict[str, object]]:
    rel = Path("results/same_root_projection_matrix_20260510/same_root_projection_matrix.csv")
    out: list[dict[str, object]] = []
    for row in read_csv(root / rel):
        variant = row.get("projection_variant", "")
        if variant not in SAME_ROOT_VARIANTS:
            continue
        mesh_path = value(row, "mesh_path")
        asset_status, mesh_exists, glb_exists, size = mesh_asset_status(mesh_path, "", root)
        complete = metric_completeness(row, "same_root")
        status = row.get("status", "")
        out.append(
            {
                "matrix": "same-root",
                "case": row.get("case", ""),
                "variant": variant,
                "status": status,
                "asset_status": asset_status if status == "available" else "missing_required_row",
                "final_mesh_path": mesh_path,
                "final_glb_path": "",
                "local_mesh_exists": mesh_exists,
                "local_glb_exists": glb_exists,
                "metric_completeness": complete,
                "vertices": row.get("vertices", ""),
                "faces": row.get("faces", ""),
                "component_count": row.get("component_count", ""),
                "largest_component_ratio": row.get("largest_component_ratio", ""),
                "glb_or_mesh_size_mb": size,
                "source_file": str(rel),
                "claim_gate": claim_gate(status, asset_status, complete, row.get("notes", "")),
                "missing_reason": row.get("missing_reason", ""),
                "notes": row.get("notes", ""),
            }
        )
    return out


def selected_glb_by_variant(root: Path) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    for rel in SELECTED_TEXTURING_SUMMARIES:
        data = read_json(root / rel)
        if not data:
            continue
        label = rel.parent.name
        if "rule_only" in label:
            case, variant = "lsystem_branch/fork_side", "rule-only"
        elif "noN" in label:
            case, variant = "lsystem_branch/fork_side", "no-N"
        elif "lsystem_weakblend" in label:
            case, variant = "lsystem_branch/fork_side", "weak blend"
        elif "lsystem_masked" in label:
            case, variant = "lsystem_branch/fork_side", "masked local-N"
        elif label.startswith("coral_weakblend"):
            case, variant = "coral_v3b/fork_side", "weak blend"
        elif label.startswith("coral_masked"):
            case, variant = "coral_v3b/fork_side", "masked local-N"
        elif label.startswith("pyrite_weakblend"):
            case, variant = "pyrite_v3b/fork_side", "weak blend"
        elif label.startswith("pyrite_masked"):
            case, variant = "pyrite_v3b/fork_side", "masked local-N"
        else:
            case, variant = label, "unknown"
        out[(case, variant)] = {
            "summary": str(rel),
            "mesh": str(data.get("mesh", "")),
            "glb": str(data.get("glb", "")),
            "vertices": str(data.get("mesh_vertices", "")),
            "faces": str(data.get("mesh_faces", "")),
            "glb_bytes": str(data.get("glb_bytes", "")),
            "status": str(data.get("status", "")),
            "notes": f"selected Trellis2 texture/export GLB; shape_slat_tokens={data.get('shape_slat_tokens', '')}; pbr_voxel_tokens={data.get('pbr_voxel_tokens', '')}",
        }
    return out


def naturalization_rows(root: Path) -> list[dict[str, object]]:
    rel = Path("results/naturalization_projection_ablation_20260510/naturalization_projection_ablation.csv")
    glbs = selected_glb_by_variant(root)
    out: list[dict[str, object]] = []
    for row in read_csv(root / rel):
        variant = row.get("ablation_variant", "")
        if variant not in NATURALIZATION_VARIANTS:
            continue
        case = row.get("case", "")
        selected = glbs.get((case, variant), {})
        mesh_path = selected.get("mesh") or row.get("mesh_path", "")
        glb_path = selected.get("glb", "")
        asset_status, mesh_exists, glb_exists, size = mesh_asset_status(mesh_path, glb_path, root)
        complete = metric_completeness(row, "naturalization")
        status = row.get("status", "")
        faces = selected.get("faces") or row.get("faces", "")
        vertices = selected.get("vertices") or row.get("vertices", "")
        out.append(
            {
                "matrix": "naturalization",
                "case": case,
                "variant": variant,
                "status": status,
                "asset_status": asset_status if status == "available" else "missing_required_row",
                "final_mesh_path": mesh_path,
                "final_glb_path": glb_path,
                "local_mesh_exists": mesh_exists,
                "local_glb_exists": glb_exists,
                "metric_completeness": complete,
                "vertices": vertices,
                "faces": faces,
                "component_count": row.get("after_components", ""),
                "largest_component_ratio": row.get("after_largest_component_ratio", ""),
                "glb_or_mesh_size_mb": size or (f"{as_float(selected.get('glb_bytes')) / (1024 * 1024):.6f}" if selected.get("glb_bytes") else ""),
                "source_file": selected.get("summary") or str(rel),
                "claim_gate": claim_gate(status, asset_status, complete, row.get("verdict", "") + " " + row.get("notes", "")),
                "missing_reason": row.get("missing_reason", ""),
                "notes": selected.get("notes") or row.get("notes", ""),
            }
        )
    return out


def effective_rows(root: Path) -> list[dict[str, object]]:
    rel = Path("results/effective_resolution_metrics_20260510/effective_resolution_metrics.csv")
    out: list[dict[str, object]] = []
    for row in read_csv(root / rel):
        if row.get("row_type") != "method_metric":
            continue
        mesh_path = row.get("path", "")
        asset_status, mesh_exists, glb_exists, size = mesh_asset_status(mesh_path, mesh_path if mesh_path.endswith(".glb") else "", root)
        complete = metric_completeness(row, "effective")
        faces = as_float(row.get("faces"))
        feature = as_float(row.get("local_feature_scale_proxy"))
        highres = faces / max(feature * feature, 1e-12) if faces and feature else 0.0
        out.append(
            {
                "matrix": "effective-resolution",
                "case": row.get("case_group", ""),
                "variant": row.get("label", ""),
                "status": row.get("status", ""),
                "asset_status": asset_status,
                "final_mesh_path": mesh_path,
                "final_glb_path": mesh_path if mesh_path.endswith(".glb") else "",
                "local_mesh_exists": mesh_exists,
                "local_glb_exists": glb_exists,
                "metric_completeness": complete,
                "vertices": row.get("vertices", ""),
                "faces": row.get("faces", ""),
                "local_feature_scale_proxy": row.get("local_feature_scale_proxy", ""),
                "terminal_detail_count_proxy": row.get("terminal_detail_count_proxy", ""),
                "zoom_retention_score": row.get("zoom_retention_score", ""),
                "estimated_full_object_highres_faces": f"{highres:.0f}" if highres else "",
                "glb_or_mesh_size_mb": size or row.get("glb_size_mb", ""),
                "source_file": str(rel),
                "claim_gate": claim_gate(row.get("status", ""), asset_status, complete),
                "missing_reason": row.get("missing_reason", ""),
                "notes": row.get("notes", ""),
            }
        )
    return out


def coverage_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row.get("matrix", "")), str(row.get("variant", ""))), []).append(row)
    out = []
    for (matrix, variant), group in sorted(grouped.items()):
        available = [r for r in group if r.get("status") == "available"]
        with_local_glb = [r for r in available if r.get("local_glb_exists") == "yes"]
        with_local_mesh = [r for r in available if r.get("local_mesh_exists") == "yes"]
        metrics_nonempty = [r for r in available if not str(r.get("metric_completeness", "")).startswith("0/")]
        out.append(
            {
                "matrix": matrix,
                "variant": variant,
                "available_rows": len(available),
                "missing_rows": len(group) - len(available),
                "available_with_local_mesh": len(with_local_mesh),
                "available_with_local_glb": len(with_local_glb),
                "available_with_any_metrics": len(metrics_nonempty),
            }
        )
    return out


def schema_rows() -> list[dict[str, str]]:
    return [
        {"column": "case_id", "required": "yes", "definition": "Stable case/group identifier, e.g. lsystem_branch/fork_side or crystal/coral."},
        {"column": "method_class", "required": "yes", "definition": "one-shot, recursive, same-root variant, or naturalization variant."},
        {"column": "final_mesh_path", "required": "yes", "definition": "Selected final OBJ/GLB mesh path; remote paths are allowed only when local asset is absent and status says so."},
        {"column": "local_feature_scale", "required": "yes", "definition": "bbox diagonal divided by sqrt(face count); smaller means finer local triangle scale at fixed object extent."},
        {"column": "terminal_detail_count", "required": "yes", "definition": "Preferred occupied surface/voxel/token count at terminal depth; fallback is vertices/faces when occupancy is absent."},
        {"column": "zoom_retention", "required": "yes", "definition": "connectivity_lcr * (1 + box_count_dimension_proxy / 3); proxy for retained local structure under zoom."},
        {"column": "faces", "required": "yes", "definition": "Triangle count for final selected asset."},
        {"column": "glb_size_mb", "required": "if_glb", "definition": "Local selected GLB size in MB when GLB exists."},
        {"column": "full_object_highres_blowup_estimate_faces", "required": "yes", "definition": "One-shot face count scaled by local-feature-scale improvement squared, lower-bounded by recursive faces in comparison rows."},
        {"column": "claim_gate", "required": "yes", "definition": "main_candidate, appendix_candidate, diagnostic, missing, or needs_local_final_asset."},
    ]


def write_csv(path: Path, rows: Iterable[dict[str, object]], preferred: list[str] | None = None) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    if preferred:
        fieldnames = preferred + [field for field in fields if field not in preferred]
    else:
        fieldnames = fields
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def aggregate(project_root: Path = PROJECT_ROOT, out_dir: Path = DEFAULT_OUT) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    rows.extend(same_root_rows(project_root))
    rows.extend(naturalization_rows(project_root))
    rows.extend(effective_rows(project_root))
    preferred = [
        "matrix",
        "case",
        "variant",
        "status",
        "asset_status",
        "claim_gate",
        "local_mesh_exists",
        "local_glb_exists",
        "metric_completeness",
        "vertices",
        "faces",
        "component_count",
        "largest_component_ratio",
        "local_feature_scale_proxy",
        "terminal_detail_count_proxy",
        "zoom_retention_score",
        "estimated_full_object_highres_faces",
        "glb_or_mesh_size_mb",
        "final_mesh_path",
        "final_glb_path",
        "source_file",
        "missing_reason",
        "notes",
    ]
    write_csv(out_dir / "manifest_selected_final_rows.csv", rows, preferred)
    write_csv(out_dir / "matrix_coverage_summary.csv", coverage_rows(rows))
    write_csv(out_dir / "effective_resolution_schema.csv", schema_rows(), ["column", "required", "definition"])
    summary = {
        "schema": "publication_ablation_metrics_20260510",
        "row_count": len(rows),
        "available_count": sum(1 for row in rows if row.get("status") == "available"),
        "missing_count": sum(1 for row in rows if row.get("status") != "available"),
        "manifest_csv": str(out_dir / "manifest_selected_final_rows.csv"),
        "coverage_csv": str(out_dir / "matrix_coverage_summary.csv"),
        "effective_resolution_schema_csv": str(out_dir / "effective_resolution_schema.csv"),
        "selected_final_only": True,
        "no_recursive_directory_scan": True,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.project_root, args.out_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
