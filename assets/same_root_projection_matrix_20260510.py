#!/usr/bin/env python3
"""Aggregate same-root projection ablation evidence into a fixed matrix.

This is an aggregator, not a runner. It consumes local CSV/JSON summaries when
they exist and writes explicit missing rows for required variants that have no
matched local evidence yet.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_OUT = PROJECT_ROOT / "results" / "same_root_projection_matrix_20260510"
VARIANTS = ("traditional", "direct", "final-only", "prune", "bridge", "proposed")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def number(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        val = row.get(key, "")
        if val not in ("", None):
            return str(val)
    return ""


def infer_depth(row: dict[str, str]) -> str:
    for key in ("depth", "depth_hint", "same_max_depth", "stage_count"):
        val = row.get(key, "")
        if str(val).strip():
            return str(val)
    label = " ".join(str(v) for v in row.values())
    for token in label.replace("-", "_").split("_"):
        if token.startswith("d") and token[1:].isdigit():
            return token[1:]
    return ""


def normalize_variant(raw: str, method: str = "") -> str:
    text = f"{raw} {method}".lower().replace("_", "-")
    if "traditional" in text or "lsystem" in text or "space-colonization" in text:
        return "traditional"
    if "proposed" in text or "ours" in text or "psrslg" in text or "ps-rslg" in text:
        return "proposed"
    if "final-only" in text or "final-only-projection" in text:
        return "final-only"
    if "bridge" in text:
        return "bridge"
    if "prune" in text or "per-depth" in text or "sparse-close" in text:
        return "prune"
    if "no-projection" in text or "direct" in text or raw == "raw":
        return "direct"
    return raw or "unknown"


def case_family(case: str, fallback: str = "") -> str:
    text = f"{case} {fallback}".lower()
    if any(key in text for key in ("vine", "tree", "root", "pine", "canopy")):
        return "tree/root/vine"
    if any(key in text for key in ("coral", "crystal", "pyrite", "bismuth", "dla", "ifs")):
        return "crystal/coral/lattice"
    return fallback or "unknown"


def file_size_mb(path_text: str, root: Path) -> str:
    if not path_text:
        return ""
    path = Path(path_text)
    if not path.is_absolute():
        path = root / path
    if not path.exists() or not path.is_file():
        return ""
    return f"{path.stat().st_size / (1024 * 1024):.6f}"


def base_row(
    *,
    case: str,
    variant: str,
    source: str,
    status: str,
    row: dict[str, str] | None = None,
    root: Path,
    missing_reason: str = "",
) -> dict[str, object]:
    row = row or {}
    mesh_path = number(row, "mesh_path", "obj_path", "path", "final_mesh")
    method = number(row, "method", "variant", "source_method")
    family = number(row, "family") or case_family(case, method)
    return {
        "case": case,
        "family": family,
        "projection_variant": variant,
        "root_source": number(row, "root_source", "same_root_anchor") or "same local root if source row reports it",
        "grammar_operator": number(row, "grammar", "method", "operators", "recursive_mode", "variant"),
        "depth": infer_depth(row),
        "status": status,
        "evidence_status": number(row, "evidence_status", "status") or status,
        "source_file": source,
        "source_method": method,
        "mesh_path": mesh_path,
        "glb_size_mb": file_size_mb(mesh_path, root) if mesh_path.lower().endswith(".glb") else "",
        "vertices": number(row, "vertices"),
        "faces": number(row, "faces"),
        "component_count": number(row, "component_count", "mesh_component_count", "face_component_count", "occupancy_component_count"),
        "largest_component_ratio": number(
            row,
            "largest_component_ratio",
            "largest_mesh_component_vertex_ratio",
            "face_largest_component_ratio",
            "occupancy_lcr",
            "largest_occupancy_component_ratio_6n",
        ),
        "root_reachability": number(row, "root_component_ratio", "path_to_root_rate"),
        "orphan_tip_ratio": number(row, "orphan_tip_ratio", "orphan_mass_ratio"),
        "attachment_success": number(row, "root_component_ratio", "path_to_root_rate"),
        "render_qa": number(row, "render_QA", "main_text_ready", "paper_use_tier"),
        "paper_placement": number(row, "paper_placement", "main_text_ready", "paper_use_tier"),
        "notes": number(row, "notes", "fairness_note", "caveat"),
        "missing_reason": missing_reason,
    }


def rows_from_projection_gap(root: Path) -> list[dict[str, object]]:
    rel = Path("results/projection_matrix_gap_closure_20260509/projection_matrix_gap_closure.csv")
    rows = []
    for row in read_csv(root / rel):
        variant = normalize_variant(row.get("variant", ""))
        status = "missing" if "missing" in row.get("evidence_status", "").lower() else "available"
        rows.append(
            base_row(
                case=row.get("case", "projection_gap_case"),
                variant=variant,
                source=str(rel),
                status=status,
                row=row,
                root=root,
                missing_reason="" if status == "available" else row.get("notes", "source row reports missing evidence"),
            )
        )
    return rows


def rows_from_baseline_matrix(root: Path) -> list[dict[str, object]]:
    candidates = [
        Path("results/strict_matched_baseline_matrix_20260510_seed310_depth5/metrics.csv"),
        Path("results/baseline_matrix_seed_20260510/metrics.csv"),
        Path("results/baseline_matrix_20260509/metrics.csv"),
    ]
    out = []
    for rel in candidates:
        for row in read_csv(root / rel):
            if row.get("render_group") not in ("", "final_depth_contact_sheet"):
                continue
            method = row.get("method", "")
            variant = "proposed" if method == "proposed_connected" else "traditional"
            out.append(base_row(case=row.get("case", "baseline_case"), variant=variant, source=str(rel), status="available", row=row, root=root))
    return out


def rows_from_proxy_manifest(root: Path) -> list[dict[str, object]]:
    candidates = [
        Path("results/strict_matched_psrslg_proxy_20260510_seed310_v2/manifest.csv"),
        Path("results/strict_matched_psrslg_proxy_20260510_seed310/manifest.csv"),
    ]
    out = []
    for rel in candidates:
        for row in read_csv(root / rel):
            variant = normalize_variant("", row.get("method", ""))
            out.append(base_row(case=row.get("task", "strict_matched_proxy"), variant=variant, source=str(rel), status="available", row=row, root=root))
        if out:
            break
    return out


def rows_from_projection_variant_summary(root: Path) -> list[dict[str, object]]:
    rel = Path("results/projection_variant_connectivity_ralph_20260510_0018_summary/projection_variant_final_metrics_available_20260510.csv")
    out = []
    for row in read_csv(root / rel):
        variant = normalize_variant(row.get("method", ""))
        out.append(base_row(case=row.get("case", "projection_variant_case"), variant=variant, source=str(rel), status="available", row=row, root=root))
    return out


def add_missing_required(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    observed_cases = sorted({str(row["case"]) for row in rows}) or ["global_required"]
    have = {(str(row["case"]), str(row["projection_variant"])) for row in rows}
    for case in observed_cases:
        for variant in VARIANTS:
            if (case, variant) not in have:
                rows.append(
                    base_row(
                        case=case,
                        variant=variant,
                        source="required_matrix_schema",
                        status="missing",
                        row={},
                        root=PROJECT_ROOT,
                        missing_reason=f"no local same-root {variant} row observed for case",
                    )
                )
    return rows


def write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "case",
        "family",
        "projection_variant",
        "root_source",
        "grammar_operator",
        "depth",
        "status",
        "evidence_status",
        "source_file",
        "source_method",
        "mesh_path",
        "glb_size_mb",
        "vertices",
        "faces",
        "component_count",
        "largest_component_ratio",
        "root_reachability",
        "orphan_tip_ratio",
        "attachment_success",
        "render_qa",
        "paper_placement",
        "notes",
        "missing_reason",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def aggregate(project_root: Path = PROJECT_ROOT, out_dir: Path = DEFAULT_OUT) -> dict[str, object]:
    project_root = Path(project_root)
    out_dir = Path(out_dir)
    rows: list[dict[str, object]] = []
    rows.extend(rows_from_projection_gap(project_root))
    rows.extend(rows_from_baseline_matrix(project_root))
    rows.extend(rows_from_proxy_manifest(project_root))
    rows.extend(rows_from_projection_variant_summary(project_root))
    rows = add_missing_required(rows)
    rows.sort(key=lambda r: (str(r["case"]), VARIANTS.index(str(r["projection_variant"])) if str(r["projection_variant"]) in VARIANTS else 99, str(r["source_file"])))

    available = [row for row in rows if row["status"] == "available"]
    missing = [row for row in rows if row["status"] == "missing"]
    write_csv(out_dir / "same_root_projection_matrix.csv", rows)
    write_csv(out_dir / "same_root_projection_missing.csv", missing)
    summary = {
        "schema": "same_root_projection_matrix_20260510",
        "row_count": len(rows),
        "available_count": len(available),
        "missing_count": len(missing),
        "csv": str(out_dir / "same_root_projection_matrix.csv"),
        "missing_csv": str(out_dir / "same_root_projection_missing.csv"),
        "required_variants": list(VARIANTS),
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
