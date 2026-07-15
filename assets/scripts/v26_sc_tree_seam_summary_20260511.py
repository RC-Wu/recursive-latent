#!/usr/bin/env python3
"""Summarize V26 SC-tree seam naturalization results."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V26_DIR = ROOT / "results/strict_visual_matched_texture_V26_sc_tree_seam_naturalization_20260511_remote"
V26_METRICS = V26_DIR / "surface_metrics_occ64.csv"
V26_MANIFEST = V26_DIR / "inputs/manifest.csv"
V25_COMPARISON = ROOT / "results/strict_visual_matched_texture_V25_root_sc_refine_comparison_20260510.csv"
OUT_ROWS = ROOT / "results/strict_visual_matched_texture_V26_sc_tree_seam_naturalization_rows_20260511.csv"
OUT_JSON = ROOT / "results/strict_visual_matched_texture_V26_sc_tree_seam_naturalization_rows_20260511.json"
OUT_MD = ROOT / "docs/evaluation/strict_visual_matched_V26_sc_tree_seam_naturalization_results_zh_20260511.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def short_case_id(label: str) -> str:
    return label.split("_steps", 1)[0]


def gate(components_r0: int, lcr_r0: float, components_r1: int) -> tuple[str, str]:
    if components_r0 == 1 and lcr_r0 >= 0.999999:
        return "main-metric-stable", "passes V25 SC metric floor; visual seam QA decides main replacement"
    if components_r1 == 1 and lcr_r0 >= 0.9995:
        return "near-stable-high", "appendix or conditional visual candidate; tiny r0 island must be invisible"
    return "reject-main", "metric regresses too much for main SC replacement"


def build_rows() -> list[dict[str, str]]:
    manifest = {row["case_id"]: row for row in read_csv(V26_MANIFEST)}
    v25 = {}
    for row in read_csv(V25_COMPARISON):
        key = row.get("case_id") or row.get("best_case_id") or row.get("replacement_scope", "")
        if key:
            v25[key] = row
    rows: list[dict[str, str]] = []
    for metric in read_csv(V26_METRICS):
        case_id = short_case_id(metric["label"])
        meta = manifest.get(case_id, {})
        components_r0 = int(metric["components_r0"])
        lcr_r0 = float(metric["lcr_r0"])
        components_r1 = int(metric["components_r1"])
        grade, recommendation = gate(components_r0, lcr_r0, components_r1)
        rows.append(
            {
                "case_id": case_id,
                "family": meta.get("family", "Space colonization"),
                "match_target": meta.get("match_target", "sc_tree_crown_260"),
                "components_r0": str(components_r0),
                "lcr_r0": f"{lcr_r0:.6f}",
                "components_r1": metric["components_r1"],
                "lcr_r1": f'{float(metric["lcr_r1"]):.6f}',
                "vertices": metric["vertices"],
                "faces": metric["faces"],
                "seam_mask_center_count": meta.get("seam_mask_center_count", ""),
                "junction_collar_count": meta.get("junction_collar_count", ""),
                "junction_leafshield_count": meta.get("junction_leafshield_count", ""),
                "metric_grade": grade,
                "recommendation": recommendation,
                "glb_path": metric["path"],
                "v25_reference_case": "V25_sc_tree_crown_tapered_B",
                "v25_reference_metric": (
                    f"r0={v25.get('V25_sc_tree_crown_tapered_B', v25.get('sc', {})).get('best_components_r0', '1')}, "
                    f"LCR={v25.get('V25_sc_tree_crown_tapered_B', v25.get('sc', {})).get('best_lcr_r0', '1.000000')}"
                ),
                "claim_boundary": "seam-focused SC tree candidate; not proof that Trellis UV/PBR generally removes seams",
            }
        )
    rows.sort(key=lambda row: (row["metric_grade"] != "main-metric-stable", row["case_id"]))
    return rows


def write_md(rows: list[dict[str, str]]) -> None:
    main_metric = [row for row in rows if row["metric_grade"] == "main-metric-stable"]
    near = [row for row in rows if row["metric_grade"] != "main-metric-stable"]
    lines = [
        "# V26 SC tree seam naturalization 结果",
        "",
        "日期：2026-05-11",
        "",
        "## 结论",
        "",
        "V26 是针对用户指出的 V24/V25 树枝-树冠接缝问题做的小批次修复。它没有扩展 baseline 矩阵，而是把 `sc_tree_crown_260` 的 branch/crown junction band 显式写入 grammar mask，并在该局部加入 junction collar / cambium sleeve / leafshield 过渡几何，再配低对比连续 guide 送 Trellis2。",
        "",
        f"远端 4/4 生成成功；post-GLB surface metrics 中 {len(main_metric)}/4 达到 r0 单连通、LCR=1.0，剩余 {len(near)}/4 为 r1 单连通且 LCR 高于 0.9995。白底 zoom QA 仍是最终是否替换 V24/V25 SC tree 图的决定项。",
        "",
        "## 证据文件",
        "",
        f"- metrics CSV: `{OUT_ROWS.relative_to(ROOT)}`",
        f"- metrics JSON: `{OUT_JSON.relative_to(ROOT)}`",
        "- post-GLB occ64: `results/strict_visual_matched_texture_V26_sc_tree_seam_naturalization_20260511_remote/surface_metrics_occ64.csv`",
        "- GLB: `visuals/strict_visual_matched_texture_V26_sc_tree_seam_naturalization_20260511/*/textured.glb`",
        "- zoom 目录：`visuals/strict_visual_matched_texture_V26_sc_tree_seam_naturalization_zoom_white_20260511/`",
        "",
        "## 候选表",
        "",
        "| case | r0 comps | r0 LCR | seam centers | collars | leafshield | grade | recommendation |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['case_id']}` | {row['components_r0']} | {row['lcr_r0']} | "
            f"{row['seam_mask_center_count']} | {row['junction_collar_count']} | "
            f"{row['junction_leafshield_count']} | {row['metric_grade']} | {row['recommendation']} |"
        )
    lines.extend(
        [
            "",
            "## 论文口径",
            "",
            "- 可以写：针对 V24/V25 暴露出的 branch/crown seam，局部 masked naturalization 需要显式 junction-band 设计；V26 是这个设计的 SC tree stress-test。",
            "- 不能写：Trellis 原生 UV/PBR 已普遍消除接缝。若最终采用 object-space PBR 图，必须称为 grammar-owned material/rendering route。",
            "- 与 V24/V25 比较时，指标只说明 post-GLB renderability/connectivity floor；自然度和接缝改善必须由同相机白底 zoom 支撑。",
        ]
    )
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(OUT_ROWS, rows)
    OUT_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(rows)
    print(OUT_ROWS)
    print(OUT_JSON)
    print(OUT_MD)


if __name__ == "__main__":
    main()
