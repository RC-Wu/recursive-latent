#!/usr/bin/env python3
"""Summarize V24 strict matched reruns across three texture/export seeds."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

RUNS = [
    (
        "seed20260510",
        ROOT / "results/strict_visual_matched_texture_V24_priority_rerun_20260510_remote",
    ),
    (
        "seed20260511",
        ROOT / "results/strict_visual_matched_texture_V24_priority_rerun_seed20260511_20260510_remote",
    ),
    (
        "seed20260512",
        ROOT / "results/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510_remote",
    ),
]

OUT_ROWS = ROOT / "results/strict_visual_matched_texture_V24_priority_rerun_seed3_rows_20260510.csv"
OUT_COMPARISON = ROOT / "results/strict_visual_matched_texture_V24_priority_rerun_seed3_comparison_20260510.csv"
OUT_JSON = ROOT / "results/strict_visual_matched_texture_V24_priority_rerun_seed3_comparison_20260510.json"
OUT_MD = ROOT / "docs/evaluation/strict_visual_matched_V24_three_seed_QA_recommendation_zh_20260510.md"


BASELINE_PAIR = {
    "lsys_root_fan_d5_dense_rootlets": "lsystem_branch_baseline",
    "lsys_root_fan_d5": "lsystem_branch_baseline",
    "sc_tree_crown_260": "sc_tree_canopy_baseline",
    "sc_tree_crown_260_sparse_kill": "sc_tree_canopy_baseline",
    "sc_root_network_260": "sc_tree_canopy_baseline",
    "dla_coral_cluster_900_staghorn_frontier": "dla_cluster_baseline",
    "dla_coral_cluster_900": "dla_cluster_baseline",
    "dla_frontier_sheet_700": "dla_cluster_baseline",
    "dla_coral_cluster_900_lace_porosity": "dla_cluster_baseline",
    "ifs_fractal_lattice_d4": "ifs_branch_tree_baseline",
    "ifs_radial_ornament_o8_d4": "ifs_branch_tree_baseline",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def short_case_id(label: str) -> str:
    return label.split("_steps", 1)[0]


def stability_grade(max_components_r0: int, min_lcr_r0: float, max_components_r1: int, boundary_tag: str) -> str:
    if boundary_tag:
        return "boundary"
    if max_components_r0 == 1 and min_lcr_r0 >= 0.999999:
        return "main-stable"
    if max_components_r1 == 1 and min_lcr_r0 >= 0.9995:
        return "near-stable-high"
    if max_components_r1 == 1 and min_lcr_r0 >= 0.9975:
        return "near-stable"
    return "weak"


def final_recommendation(case_id: str, grade: str) -> str:
    if "lace_porosity_boundary" in case_id:
        return "appendix-boundary-only; do not use as main claim"
    if case_id == "V24_sc_tree_crown_260_attractor_clean_seedA":
        return "main"
    if case_id == "V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA":
        return "main"
    if case_id == "V24_dla_frontier_sheet_700_open_boundary_polish_seedA":
        return "main-or-secondary; strong metric backup for DLA/frontier"
    if case_id == "V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA":
        return "main-backup-or-appendix; strongest IFS metric"
    if case_id == "V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA":
        return "conditional-main for transform-copy/lattice if bridge-contact zoom passes"
    if case_id == "V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA":
        return "conditional-main for root visual only; needs fragment-invisibility zoom QA"
    if case_id == "V24_lsys_root_fan_d5_dense_rootlets_anchorB_seedB":
        return "appendix seed/root robustness; not main-stable"
    if "smooth_rootlets" in case_id:
        return "appendix fallback"
    if "sc_tree_crown_260_attractor_clean_seedB" in case_id or "sparse_kill" in case_id:
        return "appendix SC robustness"
    if "sc_root_network" in case_id:
        return "appendix root auxiliary; not a tree-canopy replacement"
    if grade.startswith("main"):
        return "main candidate after visual QA"
    if grade.startswith("near"):
        return "appendix or conditional visual candidate"
    return "discard unless diagnostic"


def load_manifest_metadata() -> dict[str, dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    for _, run_dir in RUNS:
        manifest = run_dir / "inputs/manifest.csv"
        for row in read_csv(manifest):
            merged.setdefault(row["case_id"], row)
    return merged


def build_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    manifest = load_manifest_metadata()
    metric_rows: list[dict[str, str]] = []
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for run_seed, run_dir in RUNS:
        for row in read_csv(run_dir / "surface_metrics_occ64.csv"):
            case_id = short_case_id(row["label"])
            meta = manifest.get(case_id, {})
            out = {
                "run_seed": run_seed,
                "case_id": case_id,
                "label": row["label"],
                "family": meta.get("family", ""),
                "match_target": meta.get("match_target", ""),
                "traditional_target": meta.get("traditional_target", ""),
                "baseline_pair": BASELINE_PAIR.get(meta.get("match_target", ""), ""),
                "boundary_tag": meta.get("boundary_tag", ""),
                "components_r0": row["components_r0"],
                "lcr_r0": f'{float(row["lcr_r0"]):.6f}',
                "components_r1": row["components_r1"],
                "lcr_r1": f'{float(row["lcr_r1"]):.6f}',
                "components_r2": row["components_r2"],
                "lcr_r2": f'{float(row["lcr_r2"]):.6f}',
                "vertices": row["vertices"],
                "faces": row["faces"],
                "glb_path": row["path"],
                "selection_budget": meta.get("selection_budget", ""),
                "rerun_reason": meta.get("rerun_reason", ""),
            }
            metric_rows.append(out)
            grouped[case_id].append(out)

    comparisons: list[dict[str, str]] = []
    for case_id in sorted(grouped):
        rows = grouped[case_id]
        first = rows[0]
        max_components_r0 = max(int(row["components_r0"]) for row in rows)
        min_lcr_r0 = min(float(row["lcr_r0"]) for row in rows)
        max_components_r1 = max(int(row["components_r1"]) for row in rows)
        min_lcr_r1 = min(float(row["lcr_r1"]) for row in rows)
        grade = stability_grade(max_components_r0, min_lcr_r0, max_components_r1, first["boundary_tag"])
        comparisons.append(
            {
                "case_id": case_id,
                "family": first["family"],
                "match_target": first["match_target"],
                "baseline_pair": first["baseline_pair"],
                "runs": str(len(rows)),
                "max_components_r0": str(max_components_r0),
                "min_lcr_r0": f"{min_lcr_r0:.6f}",
                "max_components_r1": str(max_components_r1),
                "min_lcr_r1": f"{min_lcr_r1:.6f}",
                "boundary_tag": first["boundary_tag"],
                "stability_grade": grade,
                "final_recommendation": final_recommendation(case_id, grade),
                "traditional_target": first["traditional_target"],
                "selection_budget": first["selection_budget"],
            }
        )
    return metric_rows, comparisons


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(comparisons: list[dict[str, str]]) -> None:
    main_rows = [r for r in comparisons if r["final_recommendation"] in {"main", "main-or-secondary; strong metric backup for DLA/frontier"}]
    conditional = [r for r in comparisons if r["final_recommendation"].startswith("conditional-main")]
    appendix = [
        r
        for r in comparisons
        if r not in main_rows and r not in conditional and not r["final_recommendation"].startswith("appendix-boundary")
    ]
    boundary = [r for r in comparisons if r["final_recommendation"].startswith("appendix-boundary")]

    lines = [
        "# V24 strict one-to-one 三 seed QA 推荐",
        "",
        "日期：2026-05-10",
        "",
        "## 0. 证据文件",
        "",
        f"- rows: `{OUT_ROWS.relative_to(ROOT)}`",
        f"- comparison: `{OUT_COMPARISON.relative_to(ROOT)}`",
        f"- json: `{OUT_JSON.relative_to(ROOT)}`",
        "- metrics 输入：V24 priority rerun 的 `seed20260510/20260511/20260512` 三批 `surface_metrics_occ64.csv`。",
        "",
        "## 1. 总结论",
        "",
        "V24 已经形成三 seed strict one-to-one 证据链，但主文要按稳定性分层展示：SC tree A、DLA staghorn、DLA frontier sheet、IFS radial 是三 seed r0 单连通；pyrite lattice 是 transform-copy/lattice 的最佳语义候选，但三 seed r0 有 3--4 个小 component，r1 单连通且 LCR 始终高于 0.9997；L-system/root fan A 视觉上仍有主文潜力，但第三 seed 仍是 2 个 r0 component，不能写成稳定拓扑主证据。",
        "",
        "传统方法在本协议中不是失败 baseline。它们是 family target/control；V24 的比较目标是同类别递归形态、可渲染 GLB/PBR、post-GLB surface-connectivity floor 和局部 zoom 可读性。",
        "",
        "## 2. 推荐主文/条件主文/附录",
        "",
        "### 主文优先",
        "",
    ]
    for row in main_rows:
        lines.append(
            f"- `{row['case_id']}`：{row['stability_grade']}，3 seeds max comp r0={row['max_components_r0']}，min LCR r0={row['min_lcr_r0']}。{row['final_recommendation']}。"
        )
    lines.extend(["", "### 条件主文", ""])
    for row in conditional:
        lines.append(
            f"- `{row['case_id']}`：{row['stability_grade']}，3 seeds max comp r0={row['max_components_r0']}，min LCR r0={row['min_lcr_r0']}。{row['final_recommendation']}。"
        )
    lines.extend(["", "### 附录/鲁棒性", ""])
    for row in appendix:
        lines.append(
            f"- `{row['case_id']}`：{row['stability_grade']}，max comp r0={row['max_components_r0']}，min LCR r0={row['min_lcr_r0']}；{row['final_recommendation']}。"
        )
    lines.extend(["", "### 边界/不进主文", ""])
    for row in boundary:
        lines.append(
            f"- `{row['case_id']}`：boundary-tagged，max comp r0={row['max_components_r0']}，min LCR r0={row['min_lcr_r0']}；{row['final_recommendation']}。"
        )
    lines.extend(
        [
            "",
            "## 3. 表格",
            "",
            "| case | family | runs | max comp r0 | min LCR r0 | max comp r1 | grade | recommendation |",
            "|---|---|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in comparisons:
        lines.append(
            f"| `{row['case_id']}` | {row['family']} | {row['runs']} | {row['max_components_r0']} | {row['min_lcr_r0']} | {row['max_components_r1']} | {row['stability_grade']} | {row['final_recommendation']} |"
        )
    lines.extend(
        [
            "",
            "## 4. 论文口径",
            "",
            "- 主文四格建议：SC tree A、DLA staghorn、IFS pyrite lattice 条件主文、L-system/root fan A 条件主文；若 root fan zoom 不能遮蔽小碎片，则用 DLA frontier sheet 或 IFS radial 替换 root 主文位。",
            "- Pyrite lattice 的路径：`visuals/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510/V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA_steps8_tex2048_seed20284526_xformers/textured.glb`。早期 V21 pyrite 路径另见 `visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_20260510/`。",
            "- 不写 strict equivariance；写 empirical operator admission/screening。",
            "- 不写 traditional baselines broken；写 controlled family targets。",
            "- Surface voxel metrics 是 post-GLB renderability/connectivity diagnostics，不是 watertight topology proof。",
        ]
    )
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows, comparisons = build_rows()
    write_csv(OUT_ROWS, rows)
    write_csv(OUT_COMPARISON, comparisons)
    OUT_JSON.write_text(json.dumps(comparisons, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(comparisons)
    print(OUT_ROWS)
    print(OUT_COMPARISON)
    print(OUT_JSON)
    print(OUT_MD)


if __name__ == "__main__":
    main()
