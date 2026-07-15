#!/usr/bin/env python3
"""Summarize connectivity, depth, and parameter metrics for paper protocol checks.

This is intentionally lightweight: it reads existing local CSV artifacts and
does not run remote jobs, decode meshes, or alter result folders.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUTS = [
    ROOT / "results" / "baseline_matrix_20260509" / "metrics.csv",
    ROOT / "results" / "branch_path_metrics_20260509" / "branch_path_metrics.csv",
    ROOT / "results" / "coral_depth_textured_showcase_metrics_20260509" / "metrics.csv",
    ROOT / "results" / "vine_depth_textured_showcase_metrics_20260509" / "metrics.csv",
]
DEFAULT_OUT_CSV = ROOT / "docs" / "evaluation" / "connectivity_depth_parameter_summary_20260509.csv"
DEFAULT_OUT_JSON = ROOT / "docs" / "evaluation" / "connectivity_depth_parameter_summary_20260509.json"

REQUIRED_PROTOCOL_METHODS = {
    "traditional_structural": {"lsystem", "space_colonization", "ifs", "dla", "shape_grammar"},
    "direct_sparse_grammar": {"direct_sparse_grammar", "direct", "raw_direct"},
    "final_only_projection": {"final_only_projection", "final_only", "final_projection"},
    "proposed_per_depth": {
        "proposed_per_depth",
        "proposed_connected",
        "prune_per_depth",
        "bridge_per_depth",
    },
}


def _clean(value) -> str:
    return "" if value is None else str(value).strip()


def _first(row: dict, keys: Iterable[str], default: str = "") -> str:
    for key in keys:
        value = _clean(row.get(key))
        if value != "":
            return value
    return default


def _to_int(value, default: int | None = None) -> int | None:
    text = _clean(value)
    if text == "":
        return default
    try:
        return int(float(text))
    except ValueError:
        return default


def _to_float(value, default: float | None = None) -> float | None:
    text = _clean(value)
    if text == "":
        return default
    try:
        return float(text)
    except ValueError:
        return default


def _parse_depth(row: dict) -> int | None:
    direct = _to_int(_first(row, ["depth", "depth_hint", "stage", "stage_hint"]))
    if direct is not None:
        return direct
    text = " ".join(_clean(row.get(key)) for key in ("label", "case_hint", "path"))
    for pattern in (r"stage[_-]?0*([0-9]+)", r"depth[_-]?0*([0-9]+)", r"_d0*([0-9]+)"):
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return None


def _infer_case(row: dict) -> str:
    case = _first(row, ["case", "family", "skeleton_case", "case_hint"], "unknown")
    label = _clean(row.get("label"))
    if case == "unknown" and label:
        case = re.sub(r"_(?:stage|depth).*", "", label)
    return re.sub(r"_(?:stage|depth)[_-]?0*[0-9]+.*", "", case)


def _infer_method(row: dict) -> str:
    method = _first(row, ["method", "method_hint", "source_type", "metric_level"], "unknown")
    label = _clean(row.get("label"))
    if method == "unknown" and label:
        if "projected" in label or "proposed" in label:
            return "proposed_per_depth"
        if "direct" in label:
            return "direct_sparse_grammar"
        if "final_only" in label:
            return "final_only_projection"
    return method


def normalize_row(row: dict, source_path: Path) -> dict:
    """Map heterogeneous result CSV rows onto the protocol metric vocabulary."""
    depth = _parse_depth(row)
    occ_components = _to_int(
        _first(row, ["occupancy_component_count_6n", "primary_component_count", "component_count"])
    )
    lcr = _to_float(
        _first(
            row,
            [
                "largest_occupancy_component_ratio_6n",
                "primary_largest_component_ratio",
                "largest_component_ratio",
            ],
        )
    )
    root_ratio = _to_float(_first(row, ["root_component_ratio", "root_reachable_tip_ratio"]), default=None)
    orphan_mass = _to_float(row.get("orphan_mass_ratio"), default=None)
    return {
        "source": str(source_path),
        "case": _infer_case(row),
        "method": _infer_method(row),
        "depth": depth,
        "seed": _first(row, ["same_seed", "seed", "random_seed"]),
        "same_root_anchor": _first(row, ["same_root_anchor", "root_voxel", "root_seed_policy"]),
        "same_max_depth": _to_int(row.get("same_max_depth")),
        "occ_components_6n": occ_components,
        "lcr_occ_6n": lcr,
        "root_component_ratio": root_ratio,
        "orphan_mass_ratio": orphan_mass,
        "surface_fragmentation_score": _to_float(row.get("fragmentation_score"), default=None),
        "mesh_component_count": _to_int(_first(row, ["mesh_component_count", "component_count"])),
        "face_component_count": _to_int(_first(row, ["face_component_count", "component_count"])),
        "vertices": _to_int(row.get("vertices")),
        "faces": _to_int(row.get("faces")),
        "tips": _to_int(_first(row, ["tips", "tip_count_proxy"])),
        "branch_nodes": _to_int(_first(row, ["branch_nodes", "branching_proxy"])),
        "projection_survival_ratio": _to_float(row.get("projection_survival_ratio")),
        "bridge_survival_ratio": _to_float(row.get("bridge_survival_ratio")),
        "path": _first(row, ["obj_path", "path"]),
    }


def load_metric_rows(paths: Iterable[Path | str]) -> list[dict]:
    rows: list[dict] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue
        with path.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                normalized = normalize_row(row, path)
                if normalized["depth"] is not None:
                    rows.append(normalized)
    return rows


def _status(max_components: int | None, min_lcr: float | None, max_orphan: float | None, args) -> str:
    if max_components is None or min_lcr is None:
        return "missing_metrics"
    if max_components > args["max_components"] or min_lcr < args["min_lcr"]:
        return "fail"
    if max_orphan is not None and max_orphan > args["max_orphan_mass"]:
        return "fail"
    return "pass"


def summarize_depth_curves(
    rows: list[dict],
    max_components: int = 1,
    min_lcr: float = 0.98,
    max_orphan_mass: float = 0.02,
) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["case"], row["method"])].append(row)

    summaries: list[dict] = []
    thresholds = {
        "max_components": max_components,
        "min_lcr": min_lcr,
        "max_orphan_mass": max_orphan_mass,
    }
    for (case, method), group in sorted(grouped.items()):
        ordered = sorted(group, key=lambda row: (row["depth"], row["source"]))
        depths = [row["depth"] for row in ordered if row["depth"] is not None]
        comps = [row["occ_components_6n"] for row in ordered if row["occ_components_6n"] is not None]
        lcrs = [row["lcr_occ_6n"] for row in ordered if row["lcr_occ_6n"] is not None]
        orphans = [row["orphan_mass_ratio"] for row in ordered if row["orphan_mass_ratio"] is not None]
        final = ordered[-1]
        first = ordered[0]
        depth_span = max(depths) - min(depths) if depths else 0
        comp_growth = None
        if first["occ_components_6n"] is not None and final["occ_components_6n"] is not None and depth_span > 0:
            comp_growth = (final["occ_components_6n"] - first["occ_components_6n"]) / depth_span

        summaries.append(
            {
                "case": case,
                "method": method,
                "source_count": len({row["source"] for row in ordered}),
                "depth_count": len({row["depth"] for row in ordered}),
                "depth_min": min(depths) if depths else "",
                "depth_max": max(depths) if depths else "",
                "final_depth": final["depth"],
                "final_occ_components_6n": final["occ_components_6n"],
                "max_occ_components_6n": max(comps) if comps else None,
                "final_lcr_occ_6n": final["lcr_occ_6n"],
                "min_lcr_occ_6n": min(lcrs) if lcrs else None,
                "final_root_component_ratio": final["root_component_ratio"],
                "final_orphan_mass_ratio": final["orphan_mass_ratio"],
                "final_surface_fragmentation_score": final["surface_fragmentation_score"],
                "max_orphan_mass_ratio": max(orphans) if orphans else None,
                "component_growth_per_depth": comp_growth,
                "final_vertices": final["vertices"],
                "final_faces": final["faces"],
                "final_tips": final["tips"],
                "tips_delta": (
                    final["tips"] - first["tips"]
                    if final["tips"] is not None and first["tips"] is not None
                    else None
                ),
                "final_projection_survival_ratio": final["projection_survival_ratio"],
                "final_bridge_survival_ratio": final["bridge_survival_ratio"],
                "same_seed_values": ";".join(sorted({_clean(row["seed"]) for row in ordered if _clean(row["seed"])})),
                "same_root_anchor_values": ";".join(
                    sorted({_clean(row["same_root_anchor"]) for row in ordered if _clean(row["same_root_anchor"])})
                ),
                "connectivity_curve_status": _status(
                    max(comps) if comps else None,
                    min(lcrs) if lcrs else None,
                    max(orphans) if orphans else None,
                    thresholds,
                ),
            }
        )
    return summaries


def protocol_gaps(rows: list[dict]) -> list[dict]:
    by_case: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        by_case[row["case"]].add(row["method"])

    gaps = []
    for case, methods in sorted(by_case.items()):
        missing = []
        for slot, aliases in REQUIRED_PROTOCOL_METHODS.items():
            if methods.isdisjoint(aliases):
                missing.append(slot)
        if missing:
            gaps.append(
                {
                    "case": case,
                    "observed_methods": sorted(methods),
                    "missing_required_methods": missing,
                }
            )
    return gaps


def _write_summary_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case",
        "method",
        "source_count",
        "depth_count",
        "depth_min",
        "depth_max",
        "final_depth",
        "final_occ_components_6n",
        "max_occ_components_6n",
        "final_lcr_occ_6n",
        "min_lcr_occ_6n",
        "final_root_component_ratio",
        "final_orphan_mass_ratio",
        "final_surface_fragmentation_score",
        "max_orphan_mass_ratio",
        "component_growth_per_depth",
        "final_vertices",
        "final_faces",
        "final_tips",
        "tips_delta",
        "final_projection_survival_ratio",
        "final_bridge_survival_ratio",
        "same_seed_values",
        "same_root_anchor_values",
        "connectivity_curve_status",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", type=Path, help="Metric CSV path; repeatable.")
    parser.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--max-components", type=int, default=1)
    parser.add_argument("--min-lcr", type=float, default=0.98)
    parser.add_argument("--max-orphan-mass", type=float, default=0.02)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inputs = args.input if args.input else DEFAULT_INPUTS
    rows = load_metric_rows(inputs)
    summaries = summarize_depth_curves(
        rows,
        max_components=args.max_components,
        min_lcr=args.min_lcr,
        max_orphan_mass=args.max_orphan_mass,
    )
    gaps = protocol_gaps(rows)
    _write_summary_csv(args.out_csv, summaries)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_config": {
            "inputs": [str(path) for path in inputs],
            "max_components": args.max_components,
            "min_lcr": args.min_lcr,
            "max_orphan_mass": args.max_orphan_mass,
        },
        "row_count": len(rows),
        "summary_count": len(summaries),
        "protocol_gaps": gaps,
        "summaries": summaries,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {args.out_csv}")
    print(f"wrote {args.out_json}")
    if gaps:
        print(f"protocol gaps: {len(gaps)} case(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
