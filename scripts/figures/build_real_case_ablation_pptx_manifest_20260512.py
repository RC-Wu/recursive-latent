#!/usr/bin/env python3
"""Build real-case ablation PPTX visual manifests for the 2026-05-12 deck."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_INPUT_MANIFEST = ROOT / "results/real_case_ablation_inputs_20260512/manifest.json"
DEFAULT_ZOOM_PLAN = ROOT / "visuals/real_case_ablation_texture_zoom_20260512/matched_camera_zoom_plan.json"
DEFAULT_OUTPUT_DIR = ROOT / "paper_siga/figures/ablation_pptx_20260512"

SCHEMA = "publication_ablation_visual_manifest_20260512_blender"
PROJECTION_OUTPUT_NAME = "projection_publication_visual_manifest_20260512.json"
NATURALIZATION_OUTPUT_NAME = "masked_naturalization_publication_visual_manifest_20260512.json"

PROJECTION_CASES = ["proj_staghorn_frontier", "proj_pyrite_lattice"]
NATURALIZATION_CASES = ["nat_distributed_bough_B", "nat_balanced_bough_C"]

PROJECTION_VARIANTS = [
    "no_projection",
    "final_only_projection",
    "per_depth_prune_only",
    "per_depth_connector_aware",
    "ours",
]
NATURALIZATION_VARIANTS = [
    "rule_only",
    "no_naturalization_with_projection",
    "weak_blend_with_projection",
    "global_naturalization_with_projection",
    "masked_local_no_projection",
    "ours",
]

LABEL_OVERRIDES = {
    "no_projection": "no projection",
    "final_only_projection": "final-only",
    "per_depth_prune_only": "prune-only",
    "per_depth_connector_aware": "connector-aware",
    "rule_only": "rule-only",
    "no_naturalization_with_projection": "no-N + proj",
    "weak_blend_with_projection": "weak + proj",
    "global_naturalization_with_projection": "global + proj",
    "masked_local_no_projection": "masked / no-proj",
    "ours": "OURS",
}


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def abs_path(path_value: str | None, root: Path = ROOT) -> str | None:
    if not path_value:
        return None
    path = Path(path_value)
    if not path.is_absolute():
        path = root / path
    return str(path)


def index_input_manifest(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str], dict[str, Any]]:
    indexed = {}
    for row in rows:
        key = (row["experiment"], row["case_id"], row["variant"])
        indexed[key] = row
    return indexed


def index_zoom_plan(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {case["label"]: case for case in plan.get("cases", [])}


def zoom_01_path(plan_case: dict[str, Any]) -> str | None:
    for zoom in plan_case.get("zooms", []):
        if zoom.get("id") == "zoom_01":
            return abs_path(zoom.get("path"))
    return None


def panel_paths(plan_case: dict[str, Any]) -> tuple[str | None, str | None]:
    overview = plan_case.get("overview", {})
    overview_path = abs_path(overview.get("annotated_path") or overview.get("path"))
    return overview_path, zoom_01_path(plan_case)


def validate_file(path_value: str | None, context: str, missing: list[str]) -> None:
    if not path_value:
        missing.append(f"{context}: empty path")
        return
    if not Path(path_value).exists():
        missing.append(f"{context}: {path_value}")


def build_experiment_manifest(
    *,
    experiment: str,
    case_ids: list[str],
    variants: list[str],
    input_index: dict[tuple[str, str, str], dict[str, Any]],
    plan_index: dict[str, dict[str, Any]],
    input_manifest_path: Path,
    zoom_plan_path: Path,
) -> tuple[list[dict[str, Any]], list[str]]:
    manifests = []
    missing = []
    labels = [LABEL_OVERRIDES[v] for v in variants]

    for case_id in case_ids:
        rows = []
        panels = []
        case_label = None
        source_cases = []
        for variant in variants:
            row = input_index.get((experiment, case_id, variant))
            if row is None:
                missing.append(f"input manifest row: {experiment}/{case_id}/{variant}")
                continue

            rows.append(row)
            case_label = case_label or row.get("case_label") or case_id
            source_cases.append(row.get("source_case"))
            plan_case = plan_index.get(row["label"])
            if plan_case is None:
                missing.append(f"zoom plan case: {row['label']}")
                continue

            overview_path, zoom_path = panel_paths(plan_case)
            validate_file(overview_path, f"{row['label']} overview_callouts", missing)
            validate_file(zoom_path, f"{row['label']} zoom_01", missing)
            panels.extend(
                [
                    {
                        "variant": variant,
                        "label": LABEL_OVERRIDES[variant],
                        "kind": "overview",
                        "path": overview_path,
                        "source_render": row["label"],
                    },
                    {
                        "variant": variant,
                        "label": LABEL_OVERRIDES[variant],
                        "kind": "zoom",
                        "path": zoom_path,
                        "source_render": row["label"],
                    },
                ]
            )

        manifests.append(
            {
                "schema": SCHEMA,
                "experiment": experiment,
                "case_id": case_id,
                "case_label": case_label or case_id,
                "variants": variants,
                "labels": labels,
                "ours_column": len(variants) - 1,
                "renderer": "Blender orthographic white-background panels from real-case GLB renders",
                "claim_contract": "Real ablation case; OURS is rightmost; overview panels use overview_callouts and zoom panels use zoom_01 camera renders.",
                "panels": panels,
                "summary": {
                    "panel_count": len(panels),
                    "columns": len(variants),
                    "rows": ["overview", "zoom"],
                    "overview_source": "overview.annotated_path, falling back to overview.path",
                    "zoom_source": "zooms[id=zoom_01].path",
                    "ours_rightmost": variants[-1] == "ours",
                    "source_cases": sorted({s for s in source_cases if s}),
                },
                "provenance": {
                    "input_manifest": str(input_manifest_path),
                    "zoom_plan": str(zoom_plan_path),
                    "mesh_labels": [row["label"] for row in rows],
                    "mesh_paths": [row.get("mesh_path") for row in rows],
                    "metadata_paths": [row.get("metadata_path") for row in rows],
                },
            }
        )

    return manifests, missing


def summarize_manifest(manifest: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "case_count": len(manifest),
        "cases": [case["case_id"] for case in manifest],
        "panel_count": sum(len(case["panels"]) for case in manifest),
        "columns": [len(case["variants"]) for case in manifest],
        "ours_columns": [case["ours_column"] for case in manifest],
    }


def build_manifests(
    input_manifest: Path = DEFAULT_INPUT_MANIFEST,
    zoom_plan: Path = DEFAULT_ZOOM_PLAN,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    rows = read_json(input_manifest)
    plan = read_json(zoom_plan)
    input_index = index_input_manifest(rows)
    plan_index = index_zoom_plan(plan)

    projection, projection_missing = build_experiment_manifest(
        experiment="projection",
        case_ids=PROJECTION_CASES,
        variants=PROJECTION_VARIANTS,
        input_index=input_index,
        plan_index=plan_index,
        input_manifest_path=input_manifest,
        zoom_plan_path=zoom_plan,
    )
    naturalization, naturalization_missing = build_experiment_manifest(
        experiment="naturalization",
        case_ids=NATURALIZATION_CASES,
        variants=NATURALIZATION_VARIANTS,
        input_index=input_index,
        plan_index=plan_index,
        input_manifest_path=input_manifest,
        zoom_plan_path=zoom_plan,
    )

    missing = projection_missing + naturalization_missing
    if missing:
        by_prefix: dict[str, int] = defaultdict(int)
        for item in missing:
            by_prefix[item.split(":", 1)[0]] += 1
        raise FileNotFoundError(
            "Cannot build complete publication manifests; missing inputs: "
            + json.dumps({"counts": dict(by_prefix), "first_missing": missing[:20]}, indent=2)
        )

    projection_out = output_dir / PROJECTION_OUTPUT_NAME
    naturalization_out = output_dir / NATURALIZATION_OUTPUT_NAME
    if write:
        write_json(projection_out, projection)
        write_json(naturalization_out, naturalization)

    return {
        "schema": "real_case_ablation_pptx_manifest_builder_20260512",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "would_write": write,
        "input_manifest": str(input_manifest),
        "zoom_plan": str(zoom_plan),
        "outputs": {
            "projection": str(projection_out),
            "naturalization": str(naturalization_out),
        },
        "projection": summarize_manifest(projection),
        "naturalization": summarize_manifest(naturalization),
        "provenance": {
            "script": str(Path(__file__).resolve()),
            "render_case_count": len(plan.get("cases", [])),
            "input_row_count": len(rows),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", type=Path, default=DEFAULT_INPUT_MANIFEST)
    parser.add_argument("--zoom-plan", type=Path, default=DEFAULT_ZOOM_PLAN)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true", help="Validate and print summary without writing outputs.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        summary = build_manifests(
            input_manifest=args.input_manifest,
            zoom_plan=args.zoom_plan,
            output_dir=args.output_dir,
            write=not args.dry_run,
        )
    except FileNotFoundError as exc:
        summary = {
            "ok": False,
            "dry_run": args.dry_run,
            "error": str(exc),
            "input_manifest": str(args.input_manifest),
            "zoom_plan": str(args.zoom_plan),
            "output_dir": str(args.output_dir),
        }
        print(json.dumps(summary, indent=2))
        raise SystemExit(1) from exc
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
