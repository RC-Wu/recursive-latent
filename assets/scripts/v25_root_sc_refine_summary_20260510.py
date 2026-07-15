#!/usr/bin/env python3
"""Summarize V25 root/SC refinement candidates against V24 replacement gates."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

V25_DIR = ROOT / "results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote"
V25_METRICS = V25_DIR / "surface_metrics_occ64.csv"
V25_MANIFEST = V25_DIR / "inputs/manifest.csv"
V24_COMPARISON = ROOT / "results/strict_visual_matched_texture_V24_priority_rerun_seed3_comparison_20260510.csv"

OUT_ROWS = ROOT / "results/strict_visual_matched_texture_V25_root_sc_refine_rows_20260510.csv"
OUT_COMPARISON = ROOT / "results/strict_visual_matched_texture_V25_root_sc_refine_comparison_20260510.csv"
OUT_JSON = ROOT / "results/strict_visual_matched_texture_V25_root_sc_refine_comparison_20260510.json"
OUT_MD = ROOT / "docs/evaluation/strict_visual_matched_V25_root_sc_refine_QA_recommendation_zh_20260510.md"


V24_REFERENCE_CASES = {
    "root": "V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA",
    "sc": "V24_sc_tree_crown_260_attractor_clean_seedA",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def short_case_id(label: str) -> str:
    return label.split("_steps", 1)[0]


def family_gate(case_id: str, family: str, components_r0: int, lcr_r0: float, components_r1: int) -> tuple[str, str]:
    if family == "L-system":
        if components_r0 == 1 and lcr_r0 >= 0.999999:
            return "replace-metric-eligible", "root row can upgrade from visual panel to topology/main-stable candidate, pending zoom QA"
        if components_r1 == 1 and lcr_r0 >= 0.9995:
            return "visual-only-candidate", "root row remains visual-family evidence; tiny r0 islands must be invisible in zoom"
        return "reject-main", "root row is weaker than the V24 caveated baseline"
    if family == "Space colonization":
        if components_r0 == 1 and lcr_r0 >= 0.999999:
            return "replace-metric-eligible", "SC row preserves V24 metric floor; replacement depends on visibly better trunk/cap zoom"
        if components_r1 == 1 and lcr_r0 >= 0.9995:
            return "appendix-only", "SC visual may improve but metric regresses from V24 SC A"
        return "reject-main", "SC row loses the V24 connectivity floor"
    return "unknown", f"unexpected family for {case_id}"


def load_v24_reference() -> dict[str, dict[str, str]]:
    if not V24_COMPARISON.exists():
        return {}
    by_case = {row["case_id"]: row for row in read_csv(V24_COMPARISON)}
    return {key: by_case.get(case_id, {}) for key, case_id in V24_REFERENCE_CASES.items()}


def build_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    manifest = {row["case_id"]: row for row in read_csv(V25_MANIFEST)}
    v24_ref = load_v24_reference()
    rows: list[dict[str, str]] = []
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)

    for metric in read_csv(V25_METRICS):
        case_id = short_case_id(metric["label"])
        meta = manifest.get(case_id, {})
        family = meta.get("family", "")
        components_r0 = int(metric["components_r0"])
        lcr_r0 = float(metric["lcr_r0"])
        components_r1 = int(metric["components_r1"])
        grade, recommendation = family_gate(case_id, family, components_r0, lcr_r0, components_r1)
        row = {
            "case_id": case_id,
            "label": metric["label"],
            "family": family,
            "match_target": meta.get("match_target", ""),
            "traditional_target": meta.get("traditional_target", ""),
            "components_r0": metric["components_r0"],
            "lcr_r0": f"{lcr_r0:.6f}",
            "components_r1": metric["components_r1"],
            "lcr_r1": f'{float(metric["lcr_r1"]):.6f}',
            "components_r2": metric["components_r2"],
            "lcr_r2": f'{float(metric["lcr_r2"]):.6f}',
            "vertices": metric["vertices"],
            "faces": metric["faces"],
            "occupied": metric.get("occupied", ""),
            "box_dim_32_96": metric.get("box_dim_32_96", ""),
            "glb_path": metric["path"],
            "qa_priority": meta.get("qa_priority", ""),
            "root_variant": meta.get("root_variant", ""),
            "parameter_variant": meta.get("parameter_variant", ""),
            "metric_gate": grade,
            "recommendation": recommendation,
            "replacement_scope": "root" if family == "L-system" else "sc" if family == "Space colonization" else "",
            "selection_budget": meta.get("selection_budget", ""),
        }
        rows.append(row)
        grouped[row["replacement_scope"]].append(row)

    comparisons: list[dict[str, str]] = []
    for scope, items in grouped.items():
        if not scope:
            continue
        reference = v24_ref.get(scope, {})
        eligible = [row for row in items if row["metric_gate"] == "replace-metric-eligible"]
        visual_only = [row for row in items if row["metric_gate"] == "visual-only-candidate"]
        best_pool = eligible or visual_only or items
        best = sorted(
            best_pool,
            key=lambda row: (
                row["metric_gate"] != "replace-metric-eligible",
                -float(row["lcr_r0"]),
                int(row["components_r0"]),
                row["case_id"],
            ),
        )[0]
        comparisons.append(
            {
                "replacement_scope": scope,
                "best_case_id": best["case_id"],
                "best_metric_gate": best["metric_gate"],
                "best_components_r0": best["components_r0"],
                "best_lcr_r0": best["lcr_r0"],
                "best_components_r1": best["components_r1"],
                "best_lcr_r1": best["lcr_r1"],
                "v24_reference_case": V24_REFERENCE_CASES.get(scope, ""),
                "v24_max_components_r0": reference.get("max_components_r0", ""),
                "v24_min_lcr_r0": reference.get("min_lcr_r0", ""),
                "v24_max_components_r1": reference.get("max_components_r1", ""),
                "num_v25_candidates": str(len(items)),
                "num_replace_metric_eligible": str(len(eligible)),
                "num_visual_only": str(len(visual_only)),
                "recommendation": best["recommendation"],
            }
        )
    return rows, comparisons


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(rows: list[dict[str, str]], comparisons: list[dict[str, str]]) -> None:
    lines = [
        "# V25 root/SC refine QA recommendation",
        "",
        "日期：2026-05-10",
        "",
        "## 0. Evidence files",
        "",
        f"- rows: `{OUT_ROWS.relative_to(ROOT)}`",
        f"- comparison: `{OUT_COMPARISON.relative_to(ROOT)}`",
        f"- json: `{OUT_JSON.relative_to(ROOT)}`",
        f"- surface metrics: `{V25_METRICS.relative_to(ROOT)}`",
        f"- manifest: `{V25_MANIFEST.relative_to(ROOT)}`",
        "",
        "## 1. Replacement decision",
        "",
        "V25 is a root/SC refinement screen. It can replace the current V24 one-to-one rows only after both metric gates and white-background zoom QA pass.",
        "",
    ]
    for comp in comparisons:
        lines.append(
            f"- `{comp['replacement_scope']}` best: `{comp['best_case_id']}` ({comp['best_metric_gate']}), "
            f"r0={comp['best_components_r0']} / LCR {comp['best_lcr_r0']}; "
            f"V24 reference `{comp['v24_reference_case']}` had max r0={comp['v24_max_components_r0']}, min LCR={comp['v24_min_lcr_r0']}. "
            f"{comp['recommendation']}"
        )
    lines.extend(["", "## 2. Candidate table", ""])
    lines.append("| case | family | r0 comps | r0 LCR | r1 comps | gate | recommendation |")
    lines.append("|---|---:|---:|---:|---:|---|---|")
    for row in sorted(rows, key=lambda item: (item["family"], item["case_id"])):
        lines.append(
            f"| `{row['case_id']}` | {row['family']} | {row['components_r0']} | {row['lcr_r0']} | "
            f"{row['components_r1']} | {row['metric_gate']} | {row['recommendation']} |"
        )
    lines.extend(
        [
            "",
            "## 3. Claim boundary",
            "",
            "- Root candidates with r0 islands remain visual-family evidence only, even if r1 is connected.",
            "- SC candidates must not regress below the V24 SC A metric floor; otherwise they can only be appendix visual variants.",
            "- Surface metrics are post-GLB renderability/connectivity diagnostics, not watertight topology proofs.",
        ]
    )
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows, comparisons = build_rows()
    write_csv(OUT_ROWS, rows)
    write_csv(OUT_COMPARISON, comparisons)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(comparisons, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(rows, comparisons)
    print(OUT_ROWS)
    print(OUT_COMPARISON)
    print(OUT_JSON)
    print(OUT_MD)


if __name__ == "__main__":
    main()
