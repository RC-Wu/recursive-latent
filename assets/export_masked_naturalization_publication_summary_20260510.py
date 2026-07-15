#!/usr/bin/env python3
"""Export paper-ready masked-naturalization publication summaries.

This script is intentionally read-only with respect to the existing evaluator:
it consumes the current evaluation CSV files and writes compact derived tables.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_EVAL = PROJECT_ROOT / "results" / "masked_naturalization_ablation_20260510" / "evaluation_current"
DEFAULT_OUT = DEFAULT_EVAL / "publication_summary_hooke_20260510"

TASK_ORDER = ("botanical_root", "coral_frontier", "ifs_crystal")
VARIANT_ORDER = (
    "raw_grammar_proposal",
    "final_only_projection_repair",
    "per_depth_projection",
    "per_depth_weak_naturalization",
    "per_depth_global_naturalization",
    "per_depth_masked_naturalization",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def f(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, "0"))
    except Exception:
        return 0.0


def fmt(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}"


def build_summary(eval_dir: Path) -> dict[str, object]:
    paper_rows = read_csv(eval_dir / "paper_table_masked_naturalization_ablation_20260510.csv")
    metrics_rows = read_csv(eval_dir / "metrics.csv")
    by_task_variant = {(row["task_id"], row["variant"]): row for row in paper_rows}
    metrics_by_task_variant = {(row["task_id"], row["variant"]): row for row in metrics_rows}

    compact_rows: list[dict[str, object]] = []
    contrast_rows: list[dict[str, object]] = []
    for task in TASK_ORDER:
        masked = by_task_variant[(task, "per_depth_masked_naturalization")]
        no_n = by_task_variant[(task, "per_depth_projection")]
        weak = by_task_variant[(task, "per_depth_weak_naturalization")]
        global_n = by_task_variant[(task, "per_depth_global_naturalization")]
        raw = by_task_variant[(task, "raw_grammar_proposal")]
        masked_metrics = metrics_by_task_variant[(task, "per_depth_masked_naturalization")]

        compact_rows.append(
            {
                "task_id": task,
                "recommended_protocol": masked["protocol_column"],
                "score": masked["score"],
                "surface_lcr": masked_metrics["surface_largest_component_ratio"],
                "locality": masked["locality"],
                "roughness_deg": masked["roughness_deg"],
                "silhouette_vs_no_n": masked["silhouette"],
                "mesh_quality": masked["mesh_quality"],
                "score_gain_vs_no_n": fmt(f(masked, "score") - f(no_n, "score")),
                "score_gain_vs_weak": fmt(f(masked, "score") - f(weak, "score")),
                "score_gain_vs_global_n": fmt(f(masked, "score") - f(global_n, "score")),
                "roughness_reduction_deg_vs_no_n": fmt(f(no_n, "roughness_deg") - f(masked, "roughness_deg"), 2),
                "roughness_reduction_deg_vs_raw": fmt(f(raw, "roughness_deg") - f(masked, "roughness_deg"), 2),
                "locality_gain_vs_global_n": fmt(f(masked, "locality") - f(global_n, "locality")),
            }
        )

        contrast_rows.extend(
            [
                {
                    "task_id": task,
                    "contrast": "masked_vs_no_n",
                    "score_delta": fmt(f(masked, "score") - f(no_n, "score")),
                    "locality_delta": fmt(f(masked, "locality") - f(no_n, "locality")),
                    "roughness_delta_deg": fmt(f(masked, "roughness_deg") - f(no_n, "roughness_deg"), 2),
                    "silhouette_delta": fmt(f(masked, "silhouette") - f(no_n, "silhouette")),
                    "interpretation": "adds local continuity while preserving high shape agreement",
                },
                {
                    "task_id": task,
                    "contrast": "masked_vs_global_n",
                    "score_delta": fmt(f(masked, "score") - f(global_n, "score")),
                    "locality_delta": fmt(f(masked, "locality") - f(global_n, "locality")),
                    "roughness_delta_deg": fmt(f(masked, "roughness_deg") - f(global_n, "roughness_deg"), 2),
                    "silhouette_delta": fmt(f(masked, "silhouette") - f(global_n, "silhouette")),
                    "interpretation": "keeps locality better than global smoothing",
                },
                {
                    "task_id": task,
                    "contrast": "masked_vs_weak",
                    "score_delta": fmt(f(masked, "score") - f(weak, "score")),
                    "locality_delta": fmt(f(masked, "locality") - f(weak, "locality")),
                    "roughness_delta_deg": fmt(f(masked, "roughness_deg") - f(weak, "roughness_deg"), 2),
                    "silhouette_delta": fmt(f(masked, "silhouette") - f(weak, "silhouette")),
                    "interpretation": "slightly stronger joint score than weak masked blend",
                },
            ]
        )

    protocol_summary = read_csv(eval_dir / "protocol_summary_masked_naturalization_ablation_20260510.csv")
    protocol_discrimination = []
    for row in protocol_summary:
        protocol_discrimination.append(
            {
                "protocol": row["protocol_column"],
                "mean_score": row["mean_score"],
                "mean_connectivity": row["mean_connectivity"],
                "mean_locality": row["mean_locality"],
                "mean_roughness_deg": row["mean_roughness_deg"],
                "mean_silhouette": row["mean_silhouette"],
                "recommended_task_count": row["recommended_task_count"],
            }
        )

    return {
        "compact_rows": compact_rows,
        "contrast_rows": contrast_rows,
        "protocol_discrimination": protocol_discrimination,
    }


def write_tex(path: Path, compact_rows: list[dict[str, object]]) -> None:
    lines = [
        "% Auto-generated by assets/export_masked_naturalization_publication_summary_20260510.py",
        "\\begin{tabular}{lrrrrrr}",
        "\\toprule",
        "Task & Score & LCR & Locality & Rough. & Silh. & $\\Delta$Score/no-N \\\\",
        "\\midrule",
    ]
    for row in compact_rows:
        task = str(row["task_id"]).replace("_", "\\_")
        lines.append(
            f"{task} & {row['score']} & {float(row['surface_lcr']):.4f} & {row['locality']} & "
            f"{row['roughness_deg']} & {row['silhouette_vs_no_n']} & {row['score_gain_vs_no_n']} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def export(eval_dir: Path, out_dir: Path) -> dict[str, object]:
    summary = build_summary(eval_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    compact_fields = [
        "task_id",
        "recommended_protocol",
        "score",
        "surface_lcr",
        "locality",
        "roughness_deg",
        "silhouette_vs_no_n",
        "mesh_quality",
        "score_gain_vs_no_n",
        "score_gain_vs_weak",
        "score_gain_vs_global_n",
        "roughness_reduction_deg_vs_no_n",
        "roughness_reduction_deg_vs_raw",
        "locality_gain_vs_global_n",
    ]
    contrast_fields = ["task_id", "contrast", "score_delta", "locality_delta", "roughness_delta_deg", "silhouette_delta", "interpretation"]
    protocol_fields = [
        "protocol",
        "mean_score",
        "mean_connectivity",
        "mean_locality",
        "mean_roughness_deg",
        "mean_silhouette",
        "recommended_task_count",
    ]

    compact_csv = out_dir / "masked_local_n_publication_compact_summary_20260510.csv"
    contrast_csv = out_dir / "masked_local_n_publication_contrast_summary_20260510.csv"
    protocol_csv = out_dir / "masked_local_n_protocol_discrimination_20260510.csv"
    compact_tex = out_dir / "masked_local_n_publication_compact_summary_20260510.tex"
    claim_json = out_dir / "masked_local_n_claim_boundaries_20260510.json"

    write_csv(compact_csv, summary["compact_rows"], compact_fields)
    write_csv(contrast_csv, summary["contrast_rows"], contrast_fields)
    write_csv(protocol_csv, summary["protocol_discrimination"], protocol_fields)
    write_tex(compact_tex, summary["compact_rows"])
    claim_json.write_text(
        json.dumps(
            {
                "supported_claims": [
                    "masked local naturalization is a local surface-continuity operator under per-depth projection",
                    "the tested masked-local rows preserve surface LCR=1.0 across three tasks",
                    "masked local naturalization improves the joint score over no-N, weak blend, and global-N in the current three-task matrix",
                    "global-N is a smoothing control and is penalized for lower locality preservation",
                ],
                "unsupported_claims": [
                    "global topology repair",
                    "connectivity guaranteed by naturalization alone",
                    "watertight or clean manifold topology",
                    "category-wide robustness across seeds and roots",
                    "physical DLA, coral, or crystal simulation validity",
                ],
                "missing_for_publication_strength": [
                    "seed/root mean-std",
                    "depth/root/operator metadata completeness",
                    "weak/global-N matched zoom visualizations",
                    "score weight sensitivity",
                    "handle-level recursive-state metrics",
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    manifest = {
        "schema": "masked_local_n_publication_summary_hooke_20260510",
        "source_eval_dir": str(eval_dir),
        "compact_csv": str(compact_csv),
        "contrast_csv": str(contrast_csv),
        "protocol_discrimination_csv": str(protocol_csv),
        "compact_tex": str(compact_tex),
        "claim_boundaries_json": str(claim_json),
        "row_count_compact": len(summary["compact_rows"]),
        "row_count_contrast": len(summary["contrast_rows"]),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-dir", type=Path, default=DEFAULT_EVAL)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    print(json.dumps(export(args.eval_dir, args.out_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
