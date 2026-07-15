#!/usr/bin/env python3
"""Aggregate naturalization/projection ablations without conflating them."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_OUT = PROJECT_ROOT / "results" / "naturalization_projection_ablation_20260510"
REQUIRED_VARIANTS = (
    "rule-only",
    "no-N",
    "weak blend",
    "masked local-N",
    "global-N",
    "with projection",
    "without projection",
)


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


def family_for(label: str) -> str:
    text = label.lower()
    if any(key in text for key in ("vine", "tree", "root", "pine", "canopy")):
        return "tree/root/vine"
    if any(key in text for key in ("coral", "crystal", "pyrite", "bismuth", "dla", "ifs")):
        return "crystal/coral/lattice"
    return "unknown"


def row_base(
    *,
    case: str,
    variant: str,
    status: str,
    source: str,
    row: dict[str, str] | None = None,
    naturalization_role: str = "",
    projection_role: str = "",
    missing_reason: str = "",
) -> dict[str, object]:
    row = row or {}
    before_components = value(row, "occ_before_component_count", "before_component_count", "component_count")
    after_components = value(
        row,
        "occ_after_component_count",
        "occ_comp",
        "occupancy_component_count",
        "occupancy_component_count_6n",
        "primary_component_count",
    )
    before_lcr = value(row, "occ_before_largest_component_ratio", "before_lcr")
    after_lcr = value(row, "occ_after_largest_component_ratio", "occ_lcr", "largest_occupancy_component_ratio_6n", "primary_largest_component_ratio")
    return {
        "case": case,
        "family": family_for(case),
        "ablation_variant": variant,
        "status": status,
        "source_file": source,
        "naturalization_role": naturalization_role,
        "projection_role": projection_role,
        "projection_applied": "yes" if projection_role in ("recursive_state_projection", "explicit_projection") else "no",
        "mesh_path": value(row, "output_obj", "path", "mesh_path", "final_mesh"),
        "source_mesh_path": value(row, "source"),
        "vertices": value(row, "after_vertices", "vertices"),
        "faces": value(row, "after_faces", "faces"),
        "before_components": before_components,
        "after_components": after_components,
        "before_largest_component_ratio": before_lcr,
        "after_largest_component_ratio": after_lcr,
        "component_delta": numeric_delta(before_components, after_components),
        "lcr_delta": numeric_delta(before_lcr, after_lcr),
        "verdict": value(row, "verdict", "paper_gate", "claim_gate"),
        "notes": value(row, "notes", "recursive_mode", "recipe"),
        "missing_reason": missing_reason,
    }


def numeric_delta(before: str, after: str) -> str:
    try:
        return f"{float(after) - float(before):.12g}"
    except Exception:
        return ""


def rows_from_naturalize_pilot(root: Path) -> list[dict[str, object]]:
    rel = Path("results/naturalize_blocky_mesh_pilot_20260510/summary.csv")
    out = []
    for row in read_csv(root / rel):
        case = row.get("label", "naturalize_pilot")
        out.append(
            row_base(
                case=case,
                variant="post-hoc repair baseline",
                status="available",
                source=str(rel),
                row=row,
                naturalization_role="mesh_space_surface_naturalization",
                projection_role="post_hoc_mesh_repair_not_projection",
            )
        )
    return out


def rows_from_flow_sde(root: Path) -> list[dict[str, object]]:
    rel = Path("results/flow_sde_naturalization_metrics_20260510_0008/flow_sde_depth2_summary.csv")
    out = []
    for row in read_csv(root / rel):
        out.append(
            row_base(
                case=row.get("case", "flow_sde_case"),
                variant="global-N",
                status="available",
                source=str(rel),
                row=row,
                naturalization_role=f"global_flow_sde_steps_{row.get('steps', '')}",
                projection_role="none_or_not_reported",
            )
        )
    return out


def rows_from_strict_proxy(root: Path) -> list[dict[str, object]]:
    candidates = [
        Path("results/strict_matched_psrslg_proxy_20260510_seed310_v2/manifest.csv"),
        Path("results/strict_matched_psrslg_proxy_20260510_seed310/manifest.csv"),
        Path("results/strict_visual_matched_cases_20260510_dryrun/manifest.csv"),
    ]
    out = []
    for rel in candidates:
        for row in read_csv(root / rel):
            text = f"{row.get('method', '')} {row.get('operators', '')} {row.get('recipe', '')} {row.get('recursive_mode', '')}".lower()
            if "naturalization" in text or "tip_kernel" in text or "junction_kernel" in text:
                projection = "recursive_state_projection" if "projection" in text or "root_projection" in text else "none_or_not_reported"
                out.append(
                    row_base(
                        case=row.get("task", row.get("case", row.get("label", "strict_proxy"))),
                        variant="masked local-N",
                        status="available",
                        source=str(rel),
                        row=row,
                        naturalization_role="frontier_or_masked_local_naturalization",
                        projection_role=projection,
                    )
                )
            if "root_projection" in text or "projection" in text:
                out.append(
                    row_base(
                        case=row.get("task", row.get("case", row.get("label", "strict_proxy"))),
                        variant="with projection",
                        status="available",
                        source=str(rel),
                        row=row,
                        naturalization_role="reported_separately_in_variant_row",
                        projection_role="recursive_state_projection",
                    )
                )
    return out


def rows_from_projection_gap(root: Path) -> list[dict[str, object]]:
    rel = Path("results/projection_matrix_gap_closure_20260509/projection_matrix_gap_closure.csv")
    out = []
    for row in read_csv(root / rel):
        variant_raw = row.get("variant", "").lower()
        if "no_projection" in variant_raw or "no-projection" in variant_raw:
            out.append(
                row_base(
                    case=row.get("case", "projection_gap"),
                    variant="without projection",
                    status="available",
                    source=str(rel),
                    row=row,
                    naturalization_role="unchanged_or_not_reported",
                    projection_role="projection_disabled",
                )
            )
        if "per_depth" in variant_raw or "prune" in variant_raw or "projection" in variant_raw:
            out.append(
                row_base(
                    case=row.get("case", "projection_gap"),
                    variant="with projection",
                    status="available",
                    source=str(rel),
                    row=row,
                    naturalization_role="unchanged_or_not_reported",
                    projection_role="explicit_projection",
                )
            )
    return out


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def final_metric_by_path(root: Path, rel: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in read_csv(root / rel):
        path = row.get("path", "")
        if path:
            out[path] = row
            out[str(Path(path))] = row
    return out


def gapfill_masked_mesh_path(run_name: str, label: str, grammar: str, steps: str, alpha: str, depth: int) -> str:
    return (
        f"results/{run_name}/{label}_masked_alpha_grid/"
        f"{grammar}/steps_{steps}/{alpha}/depth_{depth:02d}/masked/mesh.obj"
    )


def gapfill_rule_mesh_path(run_name: str, label: str, grammar: str, depth: int) -> str:
    return f"results/{run_name}/{label}_rule_only_direct/{grammar}/depth_{depth:02d}/mesh.obj"


def rows_from_gapfill(root: Path) -> list[dict[str, object]]:
    """Read same-root masked-naturalization gap-fill runs.

    These rows are intentionally labeled as partial evidence: alpha=0.0 is a
    candidate/no-N control inside the masked repair executor, alpha=0.25 is a
    weak blend, and alpha=1.0 is full masked local naturalization on new tokens
    with old tokens preserved.
    """

    run_name = "masked_naturalization_gapfill_20260510"
    rel_root = Path("results") / run_name
    metrics = final_metric_by_path(root, rel_root / "mesh_metrics.csv")
    out: list[dict[str, object]] = []

    alpha_to_variant = {
        "alpha_0p0": ("no-N", "masked_executor_candidate_only_alpha_0"),
        "alpha_0p25": ("weak blend", "masked_executor_weak_blend_alpha_0.25"),
        "alpha_1p0": ("masked local-N", "masked_executor_local_naturalization_alpha_1.0"),
    }

    for summary_path in sorted((root / rel_root).glob("*_masked_alpha_grid/summary.json")):
        data = read_json(summary_path)
        label = str(data.get("case", summary_path.parent.name.replace("_masked_alpha_grid", "")))
        for grammar, grammar_data in data.get("grammars", {}).items():
            steps_map = grammar_data.get("steps", {})
            for steps, alpha_map in steps_map.items():
                for alpha, depths in alpha_map.items():
                    if not depths:
                        continue
                    variant, role = alpha_to_variant.get(alpha, (alpha, f"masked_executor_{alpha}"))
                    final = depths[-1]
                    depth = int(final.get("depth", len(depths) - 1))
                    mesh_path = gapfill_masked_mesh_path(run_name, label, grammar, str(steps), alpha, depth)
                    metric_row = metrics.get(mesh_path, {})
                    merged = {
                        **{k: str(v) for k, v in final.items()},
                        **metric_row,
                        "mesh_path": mesh_path,
                        "notes": f"{grammar}; steps={steps}; {role}; preserved old tokens before next recursion",
                    }
                    out.append(
                        row_base(
                            case=f"{label}/{grammar}",
                            variant=variant,
                            status="available",
                            source=str(summary_path.relative_to(root)),
                            row=merged,
                            naturalization_role=role,
                            projection_role="masked_local_state_preservation_not_full_projection",
                        )
                    )

    for summary_path in sorted((root / rel_root).glob("*_rule_only_direct/summary.json")):
        data = read_json(summary_path)
        label = str(data.get("case", summary_path.parent.name.replace("_rule_only_direct", "")))
        for grammar, grammar_data in data.get("grammars", {}).items():
            depths = grammar_data.get("depths", [])
            if not depths:
                continue
            final = depths[-1]
            depth = int(final.get("depth", len(depths) - 1))
            mesh_path = gapfill_rule_mesh_path(run_name, label, grammar, depth)
            metric_row = metrics.get(mesh_path, {})
            merged = {
                **{k: str(v) for k, v in final.items()},
                **metric_row,
                "mesh_path": mesh_path,
                "notes": f"{grammar}; rule-only direct sparse grammar; no flow/N sampling",
            }
            out.append(
                row_base(
                    case=f"{label}/{grammar}",
                    variant="rule-only",
                    status="available",
                    source=str(summary_path.relative_to(root)),
                    row=merged,
                    naturalization_role="deterministic_rule_only_no_generator_sampling",
                    projection_role="none_or_not_reported",
                )
            )
    return out


def add_missing(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    observed_cases = sorted({str(row["case"]) for row in rows}) or ["global_required"]
    have = {(str(row["case"]), str(row["ablation_variant"])) for row in rows}
    for case in observed_cases:
        for variant in REQUIRED_VARIANTS:
            if (case, variant) not in have:
                rows.append(
                    row_base(
                        case=case,
                        variant=variant,
                        status="missing",
                        source="required_naturalization_projection_schema",
                        missing_reason=f"no local {variant} row observed for case",
                        naturalization_role="required_but_missing" if variant not in ("with projection", "without projection") else "separate_from_projection",
                        projection_role="required_but_missing" if variant in ("with projection", "without projection") else "not_the_tested_axis",
                    )
                )
    return rows


def write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "case",
        "family",
        "ablation_variant",
        "status",
        "source_file",
        "naturalization_role",
        "projection_role",
        "projection_applied",
        "mesh_path",
        "source_mesh_path",
        "vertices",
        "faces",
        "before_components",
        "after_components",
        "before_largest_component_ratio",
        "after_largest_component_ratio",
        "component_delta",
        "lcr_delta",
        "verdict",
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
    rows.extend(rows_from_naturalize_pilot(project_root))
    rows.extend(rows_from_flow_sde(project_root))
    rows.extend(rows_from_strict_proxy(project_root))
    rows.extend(rows_from_projection_gap(project_root))
    rows.extend(rows_from_gapfill(project_root))
    rows = add_missing(rows)
    order = {name: i for i, name in enumerate(REQUIRED_VARIANTS + ("post-hoc repair baseline",))}
    rows.sort(key=lambda r: (str(r["case"]), order.get(str(r["ablation_variant"]), 99), str(r["source_file"])))

    missing = [row for row in rows if row["status"] == "missing"]
    write_csv(out_dir / "naturalization_projection_ablation.csv", rows)
    write_csv(out_dir / "naturalization_projection_missing.csv", missing)
    summary = {
        "schema": "naturalization_projection_ablation_20260510",
        "row_count": len(rows),
        "available_count": len(rows) - len(missing),
        "missing_count": len(missing),
        "csv": str(out_dir / "naturalization_projection_ablation.csv"),
        "missing_csv": str(out_dir / "naturalization_projection_missing.csv"),
        "required_variants": list(REQUIRED_VARIANTS),
        "note": "post-hoc repair baseline is reported separately when local mesh repair evidence is present.",
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
