#!/usr/bin/env python3
"""Collect PS-RSLG metric rows for Experiment 3 from validated diagnostics."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
OUT = ROOT / "results/experiment3_sparse_latent_vs_meshspace_20260511"

SURFACE_SOURCES = [
    ROOT / "results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/surface_metrics_occ64.csv",
    ROOT / "results/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510_remote/surface_metrics_occ64.csv",
    ROOT / "results/strict_visual_matched_texture_V21_ifs_transform_natural_seed20291700_20260510_remote/surface_metrics_occ64.csv",
]

LABEL_TO_CASE = {
    "V25_sc_tree_crown_tapered_B_steps8_tex2048_seed20285522_xformers": "tree_crown",
    "V25_lsys_root_fan_smooth_anchorD_stable_steps8_tex2048_seed20285514_xformers": "root_fan",
    "V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA_steps8_tex2048_seed20284523_xformers": "coral",
    "V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA_steps8_tex2048_seed20284526_xformers": "pyrite",
    "V21_ifs_bismuth_stepped_transform_d5_iridescent_steps8_tex2048_seed20293804_xformers": "bismuth",
    "V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA_steps8_tex2048_seed20284527_xformers": "radial_ornament",
}

EXTRA_ROWS = [
    {
        "case_short": "vine",
        "label": "vine_stage5_parthenocissus_warm_steps8_tex2048_xformers",
        "path": "visuals/vine_stage5_guide_sweep_20260509/vine_stage5_parthenocissus_warm_steps8_tex2048_xformers/textured.glb",
        "vertices": "647958",
        "faces": "455964",
        "raw_component_count": "113957",
        "occupancy_component_count_6n": "4",
        "LCR": "0.999",
        "status": "selected_visual_candidate",
        "notes": "Existing publication baseline metric; selected visual candidate, not strict same-root proof.",
    },
    {
        "case_short": "spider_rosette",
        "label": "plant_broad_yneg_20260511i__v25h_spider_basal_crown_micro__depth_04",
        "path": "results/botanical_tree_root_recursive_remote_20260511i_pull/raw/plant_broad_yneg_20260511i/v25h_spider_basal_crown_micro/depth_04/preview.png",
        "vertices": "113467",
        "faces": "246348",
        "raw_component_count": "289",
        "occupancy_component_count_6n": "1",
        "LCR": "1.0",
        "status": "qa_gated_depth_sequence",
        "notes": "Best 20260511i spider-rosette metric row; visual QA still required before main-paper positive claim.",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def surface_row_to_exp3(row: dict[str, str], case_short: str, source: Path) -> dict[str, Any]:
    return {
        "case_short": case_short,
        "label": row.get("label", ""),
        "path": row.get("path", ""),
        "vertices": row.get("vertices", ""),
        "faces": row.get("faces", ""),
        "raw_component_count": row.get("components_r0", ""),
        "occupancy_component_count_6n": row.get("components_r0", ""),
        "LCR": row.get("lcr_r0", ""),
        "components_r1": row.get("components_r1", ""),
        "lcr_r1": row.get("lcr_r1", ""),
        "components_r2": row.get("components_r2", ""),
        "lcr_r2": row.get("lcr_r2", ""),
        "status": "surface_metrics_occ64",
        "metrics_source": str(source.relative_to(ROOT)),
        "notes": "Validated surface-occupancy diagnostic for textured PS-RSLG export; use with caption caveat.",
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "case_short",
        "label",
        "path",
        "vertices",
        "faces",
        "raw_component_count",
        "occupancy_component_count_6n",
        "LCR",
        "components_r1",
        "lcr_r1",
        "components_r2",
        "lcr_r2",
        "status",
        "metrics_source",
        "notes",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def main() -> None:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in SURFACE_SOURCES:
        for row in read_csv(source):
            case_short = LABEL_TO_CASE.get(row.get("label", ""))
            if not case_short or case_short in seen:
                continue
            rows.append(surface_row_to_exp3(row, case_short, source))
            seen.add(case_short)
    for row in EXTRA_ROWS:
        if row["case_short"] not in seen:
            rows.append(row)
            seen.add(row["case_short"])
    out_csv = OUT / "experiment3_ps_rslg_metric_rows_20260511.csv"
    out_json = OUT / "experiment3_ps_rslg_metric_rows_20260511.json"
    write_csv(out_csv, rows)
    out_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "csv": str(out_csv), "missing": sorted(set(LABEL_TO_CASE.values()) - seen)}, indent=2))


if __name__ == "__main__":
    main()
