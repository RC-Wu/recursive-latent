#!/usr/bin/env python3
"""Aggregate one-shot-vs-recursive effective-resolution metrics."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_OUT = PROJECT_ROOT / "results" / "effective_resolution_metrics_20260510"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def value(row: dict[str, str], *keys: str) -> str:
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


def classify_case(label: str) -> str:
    text = label.lower()
    if any(key in text for key in ("vine", "root", "tree", "canopy", "branch", "lsystem")):
        return "tree/vine"
    if any(key in text for key in ("coral", "crystal", "pyrite", "bismuth", "dla", "ifs")):
        return "crystal/coral"
    return "unknown"


def classify_method(label: str) -> str:
    text = label.lower()
    if text.startswith("ours") or "psrslg" in text or "ps-rslg" in text or "recursive" in text:
        return "recursive"
    if "baseline" in text or "traditional" in text or "one_shot" in text or "one-shot" in text:
        return "one-shot"
    return "unknown"


def glb_size_mb(path_text: str, root: Path) -> str:
    if not path_text:
        return ""
    path = Path(path_text)
    if not path.is_absolute():
        path = root / path
    if path.exists() and path.is_file():
        return f"{path.stat().st_size / (1024 * 1024):.6f}"
    return ""


def metric_row(row: dict[str, str], source: str, root: Path) -> dict[str, object]:
    label = value(row, "label", "case")
    faces = as_float(value(row, "faces", "max_faces_observed"))
    vertices = as_float(value(row, "vertices", "max_vertices_observed"))
    bbox_diag = as_float(value(row, "bbox_diag"), 1.0)
    occupied = as_float(value(row, "occupied_voxels", "occupied", "max_tokens_observed"))
    lcr = as_float(value(row, "primary_largest_component_ratio", "largest_occupancy_component_ratio_6n", "lcr_r1"), 0.0)
    box_dim = as_float(value(row, "box_count_dimension_proxy", "box_dim_32_96"), 0.0)
    feature_scale = bbox_diag / math.sqrt(max(faces, 1.0))
    terminal_detail = occupied if occupied > 0 else max(vertices, faces)
    zoom_retention = lcr * (1.0 + max(box_dim, 0.0) / 3.0)
    path = value(row, "path", "mesh")
    return {
        "row_type": "method_metric",
        "case_group": classify_case(label),
        "label": label,
        "method_class": classify_method(label),
        "status": "available",
        "source_file": source,
        "path": path,
        "glb_size_mb": glb_size_mb(path, root),
        "vertices": f"{vertices:.0f}" if vertices else "",
        "faces": f"{faces:.0f}" if faces else "",
        "bbox_diag": bbox_diag,
        "local_feature_scale_proxy": feature_scale,
        "terminal_detail_count_proxy": terminal_detail,
        "zoom_retention_score": zoom_retention,
        "box_count_dimension_proxy": box_dim,
        "connectivity_lcr": lcr,
        "notes": "local feature scale is bbox_diag / sqrt(face_count); terminal detail uses occupied voxels when available.",
    }


def rows_from_one_to_one(root: Path) -> list[dict[str, object]]:
    rels = [
        Path("results/baseline_one_to_one_metrics_20260510/metrics.csv"),
        Path("results/baseline_one_to_one_surface_metrics_20260510/surface_metrics_occ64.csv"),
    ]
    rows: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for rel in rels:
        for raw in read_csv(root / rel):
            label = value(raw, "label", "case")
            key = (label, str(rel))
            if key in seen:
                continue
            seen.add(key)
            rows.append(metric_row(raw, str(rel), root))
    return rows


def rows_from_depth_showcases(root: Path) -> list[dict[str, object]]:
    rows = []
    for path in sorted((root / "results").glob("*depth_textured_showcase_metrics_20260509/metrics.csv")):
        if not path.exists():
            continue
        rel = path.relative_to(root)
        for raw in read_csv(path):
            m = metric_row(raw, str(rel), root)
            m["method_class"] = "recursive"
            rows.append(m)
    return rows


def runtime_by_case(root: Path) -> dict[str, dict[str, str]]:
    rel = Path("results/runtime_token_growth_aggregate_20260510/runtime_token_growth_case_summary.csv")
    out: dict[str, dict[str, str]] = {}
    for row in read_csv(root / rel):
        case = classify_case(row.get("case", ""))
        current = out.get(case)
        if current is None or as_float(row.get("max_depth_observed")) > as_float(current.get("max_depth_observed")):
            out[case] = row
    return out


def best_by_group(rows: list[dict[str, object]], method_class: str) -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for row in rows:
        if row.get("method_class") != method_class:
            continue
        group = str(row.get("case_group"))
        score = as_float(row.get("zoom_retention_score")) * max(as_float(row.get("terminal_detail_count_proxy")), 1.0)
        current = out.get(group)
        current_score = as_float(current.get("zoom_retention_score")) * max(as_float(current.get("terminal_detail_count_proxy")), 1.0) if current else -1.0
        if current is None or score > current_score:
            out[group] = row
    return out


def comparison_rows(metric_rows: list[dict[str, object]], runtime: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    one = best_by_group(metric_rows, "one-shot")
    rec = best_by_group(metric_rows, "recursive")
    groups = sorted((set(one) | set(rec)) - {"unknown"})
    rows = []
    for group in groups:
        one_row = one.get(group)
        rec_row = rec.get(group)
        if not one_row or not rec_row:
            rows.append(
                {
                    "row_type": "comparison",
                    "case_group": group,
                    "status": "missing",
                    "one_shot_label": "" if not one_row else one_row["label"],
                    "recursive_label": "" if not rec_row else rec_row["label"],
                    "missing_reason": "missing one-shot row" if not one_row else "missing recursive row",
                }
            )
            continue
        one_detail = as_float(one_row.get("terminal_detail_count_proxy"))
        rec_detail = as_float(rec_row.get("terminal_detail_count_proxy"))
        detail_ratio = rec_detail / max(one_detail, 1.0)
        one_feature = as_float(one_row.get("local_feature_scale_proxy"), 1.0)
        rec_feature = as_float(rec_row.get("local_feature_scale_proxy"), 1.0)
        scale_ratio = one_feature / max(rec_feature, 1e-12)
        rt = runtime.get(group, {})
        max_depth = as_float(rt.get("max_depth_observed"), 1.0) or 1.0
        recursive_faces = as_float(rec_row.get("faces"))
        estimated_full = max(recursive_faces, as_float(one_row.get("faces")) * max(scale_ratio, 1.0) ** 2)
        rows.append(
            {
                "row_type": "comparison",
                "case_group": group,
                "status": "available",
                "one_shot_label": one_row["label"],
                "recursive_label": rec_row["label"],
                "one_shot_local_feature_scale_proxy": one_feature,
                "recursive_local_feature_scale_proxy": rec_feature,
                "local_feature_scale_improvement": scale_ratio,
                "one_shot_terminal_detail_count_proxy": one_detail,
                "recursive_terminal_detail_count_proxy": rec_detail,
                "recursive_to_oneshot_terminal_detail_ratio": detail_ratio,
                "one_shot_zoom_retention_score": one_row["zoom_retention_score"],
                "recursive_zoom_retention_score": rec_row["zoom_retention_score"],
                "recursive_depth_observed": max_depth,
                "runtime_base_tokens": value(rt, "base_tokens"),
                "runtime_max_tokens_observed": value(rt, "max_tokens_observed"),
                "one_shot_faces": one_row["faces"],
                "recursive_faces": rec_row["faces"],
                "one_shot_glb_size_mb": one_row["glb_size_mb"],
                "recursive_glb_size_mb": rec_row["glb_size_mb"],
                "estimated_full_object_highres_faces": estimated_full,
                "notes": "estimated_full_object_highres_faces uses one-shot faces scaled by local feature-scale improvement squared, lower-bounded by recursive faces.",
            }
        )
    if not rows:
        rows.append({"row_type": "comparison", "case_group": "global_required", "status": "missing", "missing_reason": "no comparable local one-shot/recursive rows found"})
    return rows


def write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    preferred = [
        "row_type",
        "case_group",
        "status",
        "label",
        "method_class",
        "one_shot_label",
        "recursive_label",
        "local_feature_scale_proxy",
        "terminal_detail_count_proxy",
        "zoom_retention_score",
        "recursive_to_oneshot_terminal_detail_ratio",
        "estimated_full_object_highres_faces",
        "vertices",
        "faces",
        "glb_size_mb",
        "source_file",
        "path",
        "missing_reason",
        "notes",
    ]
    fieldnames = preferred + [f for f in fields if f not in preferred]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def aggregate(project_root: Path = PROJECT_ROOT, out_dir: Path = DEFAULT_OUT) -> dict[str, object]:
    project_root = Path(project_root)
    out_dir = Path(out_dir)
    metric_rows = rows_from_one_to_one(project_root)
    metric_rows.extend(rows_from_depth_showcases(project_root))
    comparisons = comparison_rows(metric_rows, runtime_by_case(project_root))
    write_csv(out_dir / "effective_resolution_metrics.csv", metric_rows + comparisons)
    write_csv(out_dir / "effective_resolution_comparisons.csv", comparisons)
    summary = {
        "schema": "effective_resolution_metrics_20260510",
        "metric_row_count": len(metric_rows),
        "comparison_count": len(comparisons),
        "available_comparison_count": sum(1 for row in comparisons if row.get("status") == "available"),
        "csv": str(out_dir / "effective_resolution_metrics.csv"),
        "comparison_csv": str(out_dir / "effective_resolution_comparisons.csv"),
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
