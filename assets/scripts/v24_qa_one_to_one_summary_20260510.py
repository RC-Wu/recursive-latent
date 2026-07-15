#!/usr/bin/env python3
"""Build V24 strict one-to-one QA recommendation tables."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V24_METRICS = ROOT / "results/strict_visual_matched_texture_V24_priority_rerun_20260510_remote/surface_metrics_occ64.csv"
V24_MANIFEST = ROOT / "results/strict_visual_matched_texture_V24_priority_rerun_20260510_remote/inputs/manifest.csv"
BASELINE_METRICS = ROOT / "results/baseline_one_to_one_surface_metrics_20260510/surface_metrics_occ64.csv"
BASELINE_CLIP = ROOT / "results/baseline_one_to_one_clip_metrics_20260510/multiview_clip_prompt_scores.csv"
OUT_DIR = ROOT / "results/strict_visual_matched_texture_V24_priority_rerun_20260510_remote"


PAIR_POLICY = {
    "lsys_root_fan_d5_dense_rootlets": {
        "category": "L-system/root",
        "baseline_pair": "lsystem_branch_baseline",
        "paper_target": "root-fan/rootlet variant of the L-system branch target",
    },
    "lsys_root_fan_d5": {
        "category": "L-system/root",
        "baseline_pair": "lsystem_branch_baseline",
        "paper_target": "clean root-fan fallback for the L-system branch target",
    },
    "sc_tree_crown_260": {
        "category": "space-colonization tree",
        "baseline_pair": "sc_tree_canopy_baseline",
        "paper_target": "tree canopy/crown one-to-one target",
    },
    "sc_tree_crown_260_sparse_kill": {
        "category": "space-colonization tree",
        "baseline_pair": "sc_tree_canopy_baseline",
        "paper_target": "sparse-kill tree canopy/crown backup target",
    },
    "sc_root_network_260": {
        "category": "space-colonization root",
        "baseline_pair": "sc_tree_canopy_baseline",
        "paper_target": "root-network auxiliary target; not a strict tree-canopy visual replacement",
    },
    "dla_coral_cluster_900_staghorn_frontier": {
        "category": "DLA/frontier",
        "baseline_pair": "dla_cluster_baseline",
        "paper_target": "staghorn frontier/coral cluster target",
    },
    "dla_coral_cluster_900": {
        "category": "DLA/frontier",
        "baseline_pair": "dla_cluster_baseline",
        "paper_target": "coral cluster polish target",
    },
    "dla_frontier_sheet_700": {
        "category": "DLA/frontier",
        "baseline_pair": "dla_cluster_baseline",
        "paper_target": "frontier sheet/open-boundary auxiliary target",
    },
    "dla_coral_cluster_900_lace_porosity": {
        "category": "DLA/frontier",
        "baseline_pair": "dla_cluster_baseline",
        "paper_target": "boundary-tagged lace porosity variant",
    },
    "ifs_fractal_lattice_d4": {
        "category": "IFS/pyrite",
        "baseline_pair": "ifs_branch_tree_baseline",
        "paper_target": "pyrite-like transform-copy lattice target",
    },
    "ifs_radial_ornament_o8_d4": {
        "category": "IFS/radial",
        "baseline_pair": "ifs_branch_tree_baseline",
        "paper_target": "radial orbit/spoke transform target",
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def short_case_id(label: str) -> str:
    marker = "_steps"
    return label.split(marker, 1)[0] if marker in label else label


def metric_grade(row: dict[str, str], boundary_tag: str) -> str:
    components_r0 = int(row["components_r0"])
    lcr_r0 = float(row["lcr_r0"])
    components_r1 = int(row["components_r1"])
    if boundary_tag:
        return "boundary"
    if components_r0 == 1 and lcr_r0 == 1.0:
        return "strong"
    if components_r1 == 1 and lcr_r0 >= 0.9975:
        return "near-stable"
    return "weak"


def recommendation(case_id: str, grade: str, target: str) -> str:
    if "lace_porosity_boundary" in case_id:
        return "discard-main; appendix only after fragment invisibility QA"
    if case_id.endswith("dense_rootlets_anchorA_seedA"):
        return "main"
    if case_id.endswith("dense_rootlets_anchorB_seedB"):
        return "appendix/seed2 robustness"
    if "smooth_rootlets" in case_id:
        return "appendix fallback"
    if "sc_tree_crown_260_attractor_clean_seedA" in case_id:
        return "main"
    if "sc_tree_crown_260_attractor_clean_seedB" in case_id:
        return "appendix/seed2 robustness"
    if "sc_tree_crown_260_sparse_kill" in case_id:
        return "appendix backup"
    if "sc_root_network" in case_id:
        return "appendix/root auxiliary; not main until visual fragment QA passes"
    if "staghorn_frontier_polish" in case_id:
        return "main"
    if "frontier_sheet" in case_id:
        return "appendix or small secondary panel"
    if "pyrite_copy_bridges" in case_id:
        return "main if bridge-contact zoom passes; otherwise appendix"
    if "radial_ornament" in case_id:
        return "appendix/IFS radial backup"
    if grade == "strong" and "tree" in target:
        return "main"
    return "appendix"


def main() -> None:
    metrics = {short_case_id(row["label"]): row for row in read_csv(V24_METRICS)}
    manifest = {row["case_id"]: row for row in read_csv(V24_MANIFEST)}
    baseline = {row["label"]: row for row in read_csv(BASELINE_METRICS)}
    clip = {row["label"]: row for row in read_csv(BASELINE_CLIP)}

    rows: list[dict[str, str]] = []
    for case_id, manifest_row in manifest.items():
        metric_row = metrics[case_id]
        target = manifest_row["match_target"]
        policy = PAIR_POLICY[target]
        baseline_label = policy["baseline_pair"]
        baseline_row = baseline[baseline_label]
        grade = metric_grade(metric_row, manifest_row["boundary_tag"])
        rows.append(
            {
                "category": policy["category"],
                "case_id": case_id,
                "match_target": target,
                "baseline_pair": baseline_label,
                "baseline_components_r0": baseline_row["components_r0"],
                "baseline_lcr_r0": f'{float(baseline_row["lcr_r0"]):.6f}',
                "baseline_components_r1": baseline_row["components_r1"],
                "baseline_clip_mean": f'{float(clip.get(baseline_label, {}).get("mean_clip_cosine", "nan")):.6f}',
                "v24_components_r0": metric_row["components_r0"],
                "v24_lcr_r0": f'{float(metric_row["lcr_r0"]):.6f}',
                "v24_components_r1": metric_row["components_r1"],
                "v24_lcr_r1": f'{float(metric_row["lcr_r1"]):.6f}',
                "vertices": metric_row["vertices"],
                "faces": metric_row["faces"],
                "boundary_tag": manifest_row["boundary_tag"],
                "metric_grade": grade,
                "recommendation": recommendation(case_id, grade, target),
                "paper_target": policy["paper_target"],
                "rerun_reason": manifest_row["rerun_reason"],
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / "v24_one_to_one_recommendation_metrics_20260510.csv"
    json_path = OUT_DIR / "v24_one_to_one_recommendation_metrics_20260510.json"
    fieldnames = list(rows[0].keys())
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    with json_path.open("w") as handle:
        json.dump(rows, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(csv_path)
    print(json_path)


if __name__ == "__main__":
    main()
