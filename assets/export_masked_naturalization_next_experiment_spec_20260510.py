#!/usr/bin/env python3
"""Export next-experiment specs for masked local naturalization.

This is a planning/export helper only. It does not generate meshes, render, or
modify the existing evaluator logic.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_EVAL = PROJECT_ROOT / "results" / "masked_naturalization_ablation_20260510" / "evaluation_current"
DEFAULT_OUT = PROJECT_ROOT / "results" / "masked_naturalization_ablation_20260510" / "next_experiment_spec_hooke2_20260510"

TASKS = ("botanical_root", "coral_frontier", "ifs_crystal")
SEEDS = (20260510, 20260511, 20260512)
VARIANTS = (
    "raw_grammar_proposal",
    "final_only_projection_repair",
    "per_depth_projection",
    "per_depth_weak_naturalization",
    "per_depth_global_naturalization",
    "per_depth_masked_naturalization",
)
VISUAL_VARIANTS = (
    "raw_grammar_proposal",
    "final_only_projection_repair",
    "per_depth_projection",
    "per_depth_weak_naturalization",
    "per_depth_global_naturalization",
    "per_depth_masked_naturalization",
)


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def read_existing_columns(eval_dir: Path) -> list[str]:
    metrics = eval_dir / "metrics.csv"
    if not metrics.exists():
        return []
    with metrics.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        return next(reader, [])


def export(eval_dir: Path, out_dir: Path) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)

    m1_rows = []
    for seed in SEEDS:
        run_dir = f"results/masked_naturalization_ablation_20260510_seed{seed}"
        for task in TASKS:
            for variant in VARIANTS:
                m1_rows.append(
                    {
                        "matrix": "M1",
                        "task_id": task,
                        "seed": seed,
                        "variant": variant,
                        "asset_dir": run_dir,
                        "mesh_path": f"{run_dir}/tasks/{task}/{variant}/mesh.obj",
                        "metadata_path": f"{run_dir}/tasks/{task}/{variant}/metadata.json",
                        "expected_eval_dir": f"{run_dir}/evaluation_current",
                    }
                )
    write_csv(
        out_dir / "m1_minimal_replicate_manifest_20260510.csv",
        m1_rows,
        ["matrix", "task_id", "seed", "variant", "asset_dir", "mesh_path", "metadata_path", "expected_eval_dir"],
    )

    m2_rows = []
    for task in TASKS:
        for variant in VISUAL_VARIANTS:
            m2_rows.append(
                {
                    "matrix": "M2",
                    "task_id": task,
                    "variant": variant,
                    "source_mesh": f"results/masked_naturalization_ablation_20260510/tasks/{task}/{variant}/mesh.obj",
                    "visual_case_label": f"{task}__{variant}",
                    "required_outputs": "overview_raw.png;overview_callouts.png;zoom_01.png;zoom_01_callouts.png;zoom_02.png;strict_matched_zoom_comparison.png",
                    "currently_missing_priority": "yes" if variant in ("per_depth_weak_naturalization", "per_depth_global_naturalization") else "no",
                }
            )
    write_csv(
        out_dir / "m2_visual_closure_manifest_20260510.csv",
        m2_rows,
        ["matrix", "task_id", "variant", "source_mesh", "visual_case_label", "required_outputs", "currently_missing_priority"],
    )

    metric_columns = read_existing_columns(eval_dir)
    m3_fields = {
        "existing_metrics_csv_fields": metric_columns,
        "required_new_handle_state_fields": [
            "active_handle_count_before",
            "active_handle_count_after",
            "active_handle_survival_rate",
            "orphan_handle_count",
            "reachable_frontier_count",
            "frontier_reachability_rate",
            "root_attached_mass_ratio",
            "deleted_active_support_mass",
            "handle_drift_l2_mean",
            "mask_overlap_with_active_handles",
        ],
        "required_metadata_fields": [
            "root_id",
            "seed",
            "operator_family",
            "depth_count",
            "projection_thresholds",
            "naturalization_step_count",
            "mask_schedule",
            "root_source_provenance",
        ],
    }
    (out_dir / "m3_handle_state_metric_schema_20260510.json").write_text(
        json.dumps(m3_fields, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    commands = {
        "m1_generate_assets": [
            f"python3 assets/masked_naturalization_ablation_assets_20260510.py --seed {seed} --depth-count 3 --resolution 56 --out-dir results/masked_naturalization_ablation_20260510_seed{seed}"
            for seed in SEEDS
        ],
        "m1_evaluate": [
            f"python3 assets/evaluate_masked_naturalization_ablation_20260510.py --asset-dir results/masked_naturalization_ablation_20260510_seed{seed} --out-dir results/masked_naturalization_ablation_20260510_seed{seed}/evaluation_current"
            for seed in SEEDS
        ],
        "m2_render_note": "Use the existing matched-camera white zoom renderer on rows in m2_visual_closure_manifest_20260510.csv; prioritize weak/global-N rows.",
        "m3_note": "Requires instrumenting asset metadata or a sidecar collector; do not overload current mesh-only evaluator.",
    }
    (out_dir / "next_experiment_commands_20260510.json").write_text(
        json.dumps(commands, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "schema": "masked_naturalization_next_experiment_spec_hooke2_20260510",
        "out_dir": str(out_dir),
        "m1_rows": len(m1_rows),
        "m2_rows": len(m2_rows),
        "seeds": list(SEEDS),
        "tasks": list(TASKS),
        "variants": list(VARIANTS),
        "files": [
            str(out_dir / "m1_minimal_replicate_manifest_20260510.csv"),
            str(out_dir / "m2_visual_closure_manifest_20260510.csv"),
            str(out_dir / "m3_handle_state_metric_schema_20260510.json"),
            str(out_dir / "next_experiment_commands_20260510.json"),
        ],
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
