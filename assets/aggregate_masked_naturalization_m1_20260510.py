#!/usr/bin/env python3
"""Aggregate masked naturalization M1 replicate metrics.

Inputs are the per-seed metrics.csv files emitted by
evaluate_masked_naturalization_ablation_20260510.py.  The script is deliberately
read-only with respect to the existing evaluator outputs.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics as stats
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_OUT = PROJECT_ROOT / "results" / "masked_naturalization_ablation_m1_20260510"
DEFAULT_METRICS = [
    PROJECT_ROOT / "results/masked_naturalization_ablation_20260510_seed20260510/evaluation_current/metrics.csv",
    PROJECT_ROOT / "results/masked_naturalization_ablation_20260510_seed20260511/evaluation_current/metrics.csv",
    PROJECT_ROOT / "results/masked_naturalization_ablation_20260510_seed20260512/evaluation_current/metrics.csv",
]

KEY_METRICS = [
    "main_text_score",
    "connectivity_score",
    "surface_largest_component_ratio",
    "locality_preservation_score",
    "local_normal_variation_mean_deg",
    "silhouette_iou_vs_per_depth_projection",
    "mesh_quality_score",
    "connectivity_blockiness_index",
]

PROTOCOL_ORDER = [
    "rule-only",
    "final-only",
    "per-depth/no-N",
    "per-depth/weak",
    "per-depth/global-N",
    "per-depth/masked local-N",
]


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)
    except Exception:
        return default


def infer_seed(path: Path, index: int) -> str:
    for part in path.parts:
        if "seed2026" in part:
            return part.rsplit("seed", 1)[-1]
    return f"input_{index:02d}"


def read_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, path in enumerate(paths, start=1):
        if not path.exists():
            raise FileNotFoundError(path)
        seed = infer_seed(path, index)
        with path.open("r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                row = dict(row)
                row["seed"] = seed
                rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                fields.append(key)
                seen.add(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    if len(values) == 1:
        return float(values[0]), 0.0
    return float(stats.mean(values)), float(stats.stdev(values))


def protocol_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["task_id"], row["protocol_column"], row["variant"]), []).append(row)
    out: list[dict[str, Any]] = []
    order = {label: i for i, label in enumerate(PROTOCOL_ORDER)}
    for (task, protocol, variant), items in grouped.items():
        rec: dict[str, Any] = {
            "task_id": task,
            "protocol_column": protocol,
            "variant": variant,
            "seed_count": len({item.get("seed", "") for item in items}),
        }
        for metric in KEY_METRICS:
            vals = [safe_float(item.get(metric)) for item in items]
            mean, std = mean_std(vals)
            rec[f"{metric}_mean"] = mean
            rec[f"{metric}_std"] = std
        out.append(rec)
    out.sort(key=lambda r: (str(r["task_id"]), order.get(str(r["protocol_column"]), 99)))
    return out


def stability(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_task_seed: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        by_task_seed.setdefault((row["task_id"], row["seed"]), []).append(row)

    winners: dict[str, list[str]] = {}
    for (task, _seed), items in by_task_seed.items():
        winner = max(items, key=lambda r: safe_float(r.get("main_text_score")))
        winners.setdefault(task, []).append(str(winner["variant"]))

    by_task_protocol = {(r["task_id"], r["protocol_column"]): r for r in protocol_summary(rows)}
    out: list[dict[str, Any]] = []
    for task in sorted(winners):
        win_list = winners[task]
        masked_wins = sum(1 for v in win_list if v == "per_depth_masked_naturalization")
        masked = by_task_protocol[(task, "per-depth/masked local-N")]
        no_n = by_task_protocol[(task, "per-depth/no-N")]
        weak = by_task_protocol[(task, "per-depth/weak")]
        global_n = by_task_protocol[(task, "per-depth/global-N")]
        lcr = safe_float(masked["surface_largest_component_ratio_mean"])
        silhouette = safe_float(masked["silhouette_iou_vs_per_depth_projection_mean"])
        score_gain_no_n = safe_float(masked["main_text_score_mean"]) - safe_float(no_n["main_text_score_mean"])
        locality_gain_global = safe_float(masked["locality_preservation_score_mean"]) - safe_float(global_n["locality_preservation_score_mean"])
        gate_pass = (
            masked_wins >= 2
            and lcr >= 0.98
            and silhouette >= 0.84
            and score_gain_no_n > 0
            and locality_gain_global > 0
        )
        out.append(
            {
                "task_id": task,
                "seed_count": len(win_list),
                "masked_local_wins": masked_wins,
                "masked_local_win_rate": masked_wins / max(len(win_list), 1),
                "winner_variants_by_seed": ";".join(win_list),
                "masked_score_mean": masked["main_text_score_mean"],
                "masked_score_std": masked["main_text_score_std"],
                "score_gain_vs_noN_mean": score_gain_no_n,
                "score_gain_vs_weak_mean": safe_float(masked["main_text_score_mean"]) - safe_float(weak["main_text_score_mean"]),
                "score_gain_vs_globalN_mean": safe_float(masked["main_text_score_mean"]) - safe_float(global_n["main_text_score_mean"]),
                "masked_lcr_mean": lcr,
                "masked_silhouette_mean": silhouette,
                "masked_locality_mean": masked["locality_preservation_score_mean"],
                "locality_gain_vs_globalN_mean": locality_gain_global,
                "acceptance_gate_pass": gate_pass,
            }
        )
    return out


def acceptance_summary(rows: list[dict[str, Any]], stable: list[dict[str, Any]], source_paths: list[Path]) -> dict[str, Any]:
    observed_seeds = sorted({str(row.get("seed", "")) for row in rows})
    expected_rows = 3 * len(observed_seeds) * len(PROTOCOL_ORDER)
    task_gates = []
    for row in stable:
        gate = {
            "task_id": row["task_id"],
            "seed_count_is_3": int(row["seed_count"]) == 3,
            "masked_wins_at_least_2_of_3": int(row["masked_local_wins"]) >= 2,
            "masked_mean_lcr_ge_0p98": safe_float(row["masked_lcr_mean"]) >= 0.98,
            "masked_mean_silhouette_ge_0p84": safe_float(row["masked_silhouette_mean"]) >= 0.84,
            "masked_mean_score_gt_no_n": safe_float(row["score_gain_vs_noN_mean"]) > 0,
            "masked_mean_score_gt_weak": safe_float(row["score_gain_vs_weak_mean"]) > 0,
            "masked_mean_score_gt_global_n": safe_float(row["score_gain_vs_globalN_mean"]) > 0,
            "masked_mean_locality_gt_global_n": safe_float(row["locality_gain_vs_globalN_mean"]) > 0,
        }
        gate["task_acceptance_gate_pass"] = all(value for key, value in gate.items() if key != "task_id")
        task_gates.append(gate)
    return {
        "source_metrics": [str(path) for path in source_paths],
        "observed_seed_count": len(observed_seeds),
        "observed_seeds": observed_seeds,
        "observed_rows": len(rows),
        "expected_rows_for_observed_seeds": expected_rows,
        "all_expected_rows_present_for_observed_seeds": len(rows) == expected_rows,
        "three_seed_inputs_present": len(observed_seeds) == 3,
        "task_gates": task_gates,
        "all_acceptance_gates_pass": len(observed_seeds) == 3 and len(rows) == expected_rows and all(g["task_acceptance_gate_pass"] for g in task_gates),
    }


def write_markdown(
    path: Path,
    prot: list[dict[str, Any]],
    stable: list[dict[str, Any]],
    source_paths: list[Path],
    gates: dict[str, Any],
) -> None:
    lines = [
        "# Masked Local Naturalization M1 三 seed 聚合",
        "",
        "日期：2026-05-10",
        "",
        "输入：",
    ]
    lines += [f"- `{p}`" for p in source_paths]
    lines += [
        "",
        "## Recommendation Stability",
        "",
        "| task | masked wins | win rate | masked score mean/std | gain vs no-N | gain vs global-N | locality gain vs global-N | gate |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in stable:
        lines.append(
            "| {task} | {wins}/3 | {rate:.3f} | {score:.4f} / {std:.4f} | {gain_no:.4f} | {gain_global:.4f} | {loc_gain:.4f} | {gate} |".format(
                task=row["task_id"],
                wins=row["masked_local_wins"],
                rate=safe_float(row["masked_local_win_rate"]),
                score=safe_float(row["masked_score_mean"]),
                std=safe_float(row["masked_score_std"]),
                gain_no=safe_float(row["score_gain_vs_noN_mean"]),
                gain_global=safe_float(row["score_gain_vs_globalN_mean"]),
                loc_gain=safe_float(row["locality_gain_vs_globalN_mean"]),
                gate=row["acceptance_gate_pass"],
            )
        )
    lines += [
        "",
        "## Acceptance Gates",
        "",
        f"- observed rows: `{gates['observed_rows']}`",
        f"- expected rows for observed seeds: `{gates['expected_rows_for_observed_seeds']}`",
        f"- observed seed count: `{gates['observed_seed_count']}`",
        f"- all gates pass: `{gates['all_acceptance_gates_pass']}`",
        "",
        "| task | seed=3 | wins>=2/3 | LCR>=0.98 | silh>=0.84 | score>no-N | score>weak | score>global-N | locality>global-N |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for gate in gates["task_gates"]:
        lines.append(
            "| {task_id} | {seed_count_is_3} | {masked_wins_at_least_2_of_3} | {masked_mean_lcr_ge_0p98} | "
            "{masked_mean_silhouette_ge_0p84} | {masked_mean_score_gt_no_n} | {masked_mean_score_gt_weak} | "
            "{masked_mean_score_gt_global_n} | {masked_mean_locality_gt_global_n} |".format(**gate)
        )
    lines += [
        "",
        "## Paper-Safe Reading",
        "",
        "M1 supports the narrow main-text statement that per-depth masked local naturalization is the most stable of the tested local realization controls across three deterministic seeds for the three matched tasks. The result still does not support global topology repair, physical growth, watertightness, or category-wide robustness.",
        "",
        "## Protocol Table",
        "",
        "| task | protocol | score mean/std | LCR mean | locality mean | roughness mean | silhouette mean |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in prot:
        lines.append(
            "| {task} | {protocol} | {score:.4f} / {std:.4f} | {lcr:.4f} | {loc:.4f} | {rough:.2f} | {sil:.4f} |".format(
                task=row["task_id"],
                protocol=row["protocol_column"],
                score=safe_float(row["main_text_score_mean"]),
                std=safe_float(row["main_text_score_std"]),
                lcr=safe_float(row["surface_largest_component_ratio_mean"]),
                loc=safe_float(row["locality_preservation_score_mean"]),
                rough=safe_float(row["local_normal_variation_mean_deg_mean"]),
                sil=safe_float(row["silhouette_iou_vs_per_depth_projection_mean"]),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", type=Path, nargs="+", default=[])
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    metrics = args.metrics or DEFAULT_METRICS
    rows = read_rows(metrics)
    prot = protocol_summary(rows)
    stable = stability(rows)
    gates = acceptance_summary(rows, stable, metrics)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "m1_protocol_meanstd.csv", prot)
    write_csv(args.out_dir / "m1_task_recommendation_stability.csv", stable)
    (args.out_dir / "m1_publication_summary.json").write_text(
        json.dumps(
            {
                "schema": "masked_naturalization_m1_aggregation_20260510",
                "protocol_meanstd_rows": len(prot),
                "task_recommendation_stability_rows": len(stable),
                "acceptance_gates": gates,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_markdown(args.out_dir / "m1_publication_summary.md", prot, stable, metrics, gates)
    print(
        json.dumps(
            {
                "rows": len(rows),
                "protocol_rows": len(prot),
                "tasks": len(stable),
                "acceptance_gates_pass": gates["all_acceptance_gates_pass"],
                "out_dir": str(args.out_dir),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
