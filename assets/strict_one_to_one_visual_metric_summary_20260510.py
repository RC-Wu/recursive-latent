#!/usr/bin/env python3
"""Summarize strict traditional-vs-PS-RSLG one-to-one visual and metric rows.

The output is an auxiliary paper-selection table.  Image metrics are only
diagnostics for white-background zoom figures; structural claims must still use
the post-GLB surface metrics and the human QA notes.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_OUT = PROJECT_ROOT / "results" / "traditional_vs_ps_rslg_one_to_one_metrics_20260510"

TRAD_DIR = PROJECT_ROOT / "case_gallery_for_user_20260510_remote_matched_candidates" / "01_traditional_targets"
V24_ZOOM_DIR = PROJECT_ROOT / "visuals" / "strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510"
V25_ZOOM_DIR = PROJECT_ROOT / "visuals" / "strict_visual_matched_texture_V25_root_sc_refine_zoom_white_20260510"
V24_COMPARISON = PROJECT_ROOT / "results" / "strict_visual_matched_texture_V24_priority_rerun_seed3_comparison_20260510.csv"
V25_COMPARISON = PROJECT_ROOT / "results" / "strict_visual_matched_texture_V25_root_sc_refine_comparison_20260510.csv"


PAIRINGS = [
    {
        "family": "DLA/frontier",
        "traditional_target": "dla_coral_cluster_900",
        "traditional_image": TRAD_DIR / "strict_matched_traditional_targets_zoom_20260510__dla_coral_cluster_900__strict_matched_zoom_comparison.png",
        "ours_case": "V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA",
        "ours_short": "V24_dla_staghorn_frontier",
        "ours_image": V24_ZOOM_DIR / "V24_dla_staghorn_frontier" / "strict_matched_zoom_comparison.png",
        "comparison_source": "V24-three-seed",
        "paper_use": "main-stable DLA/frontier row; do not claim physical DLA/coral simulation",
    },
    {
        "family": "IFS/transform",
        "traditional_target": "ifs_fractal_lattice_d4",
        "traditional_image": TRAD_DIR / "strict_matched_traditional_targets_zoom_20260510__ifs_fractal_lattice_d4__strict_matched_zoom_comparison.png",
        "ours_case": "V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA",
        "ours_short": "V24_ifs_pyrite_lattice",
        "ours_image": V24_ZOOM_DIR / "V24_ifs_pyrite_lattice" / "strict_matched_zoom_comparison.png",
        "comparison_source": "V24-three-seed",
        "paper_use": "conditional main transform-copy/lattice row; present as operator admission evidence, not strict equivariance",
    },
    {
        "family": "L-system",
        "traditional_target": "lsys_root_fan_d5",
        "traditional_image": TRAD_DIR / "strict_matched_traditional_targets_zoom_20260510__lsys_root_fan_d5__strict_matched_zoom_comparison.png",
        "ours_case": "V25_lsys_root_fan_smooth_anchorD_stable",
        "ours_short": "V25_root_smooth_D",
        "ours_image": V25_ZOOM_DIR / "V25_root_smooth_D" / "strict_matched_zoom_comparison.png",
        "comparison_source": "V25-root-refine",
        "paper_use": "main root row with V25 r0 single-component diagnostic; not a watertight proof",
    },
    {
        "family": "Space colonization",
        "traditional_target": "sc_tree_crown_260",
        "traditional_image": TRAD_DIR / "strict_matched_traditional_targets_zoom_20260510__sc_tree_crown_260__strict_matched_zoom_comparison.png",
        "ours_case": "V25_sc_tree_crown_tapered_B",
        "ours_short": "V25_sc_tapered_B",
        "ours_image": V25_ZOOM_DIR / "V25_sc_tapered_B" / "strict_matched_zoom_comparison.png",
        "comparison_source": "V25-SC-refine",
        "paper_use": "SC crown candidate preserving V24 metric floor; keep visual caveat on natural tree quality",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                fields.append(key)
                seen.add(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in ("", None):
            return default
        return int(float(value))
    except Exception:
        return default


def image_metrics(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "image_exists": False,
            "image_width": "",
            "image_height": "",
            "foreground_ratio": "",
            "edge_density": "",
            "detail_energy": "",
            "colorfulness": "",
            "white_background_ratio": "",
        }
    image = Image.open(path).convert("RGB")
    arr = np.asarray(image, dtype=np.float32) / 255.0
    gray = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
    white = np.all(arr > 0.965, axis=2)
    foreground = ~white
    if arr.shape[0] > 1 and arr.shape[1] > 1:
        gy, gx = np.gradient(gray)
        grad = np.sqrt(gx * gx + gy * gy)
    else:
        grad = np.zeros_like(gray)
    rg = arr[..., 0] - arr[..., 1]
    yb = 0.5 * (arr[..., 0] + arr[..., 1]) - arr[..., 2]
    colorfulness = math.sqrt(float(np.var(rg) + np.var(yb))) + 0.3 * math.sqrt(float(np.mean(rg) ** 2 + np.mean(yb) ** 2))
    fg_grad = grad[foreground] if np.any(foreground) else grad.reshape(-1)
    return {
        "image_exists": True,
        "image_width": int(image.width),
        "image_height": int(image.height),
        "foreground_ratio": float(np.mean(foreground)),
        "edge_density": float(np.mean(fg_grad > 0.055)),
        "detail_energy": float(np.mean(fg_grad)),
        "colorfulness": float(colorfulness),
        "white_background_ratio": float(np.mean(white)),
    }


def v24_index() -> dict[str, dict[str, str]]:
    return {row["case_id"]: row for row in read_csv(V24_COMPARISON)}


def v25_index() -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for row in read_csv(V25_COMPARISON):
        if row.get("replacement_scope") == "root":
            index[row["best_case_id"]] = {
                "case_id": row["best_case_id"],
                "family": "L-system",
                "runs": "1",
                "max_components_r0": row["best_components_r0"],
                "min_lcr_r0": row["best_lcr_r0"],
                "max_components_r1": row["best_components_r1"],
                "min_lcr_r1": row["best_lcr_r1"],
                "stability_grade": row["best_metric_gate"],
                "final_recommendation": row["recommendation"],
                "selection_budget": "V25 root/SC refine screen",
            }
        elif row.get("replacement_scope") == "sc":
            index[row["best_case_id"]] = {
                "case_id": row["best_case_id"],
                "family": "Space colonization",
                "runs": "1",
                "max_components_r0": row["best_components_r0"],
                "min_lcr_r0": row["best_lcr_r0"],
                "max_components_r1": row["best_components_r1"],
                "min_lcr_r1": row["best_lcr_r1"],
                "stability_grade": row["best_metric_gate"],
                "final_recommendation": row["recommendation"],
                "selection_budget": "V25 root/SC refine screen",
            }
    return index


def structural_row(pair: dict[str, Any], v24: dict[str, dict[str, str]], v25: dict[str, dict[str, str]]) -> dict[str, str]:
    if pair["comparison_source"].startswith("V24"):
        return v24.get(str(pair["ours_case"]), {})
    return v25.get(str(pair["ours_case"]), {})


def build_rows() -> list[dict[str, Any]]:
    v24 = v24_index()
    v25 = v25_index()
    rows: list[dict[str, Any]] = []
    for pair in PAIRINGS:
        trad = image_metrics(Path(pair["traditional_image"]))
        ours = image_metrics(Path(pair["ours_image"]))
        structure = structural_row(pair, v24, v25)
        trad_edge = safe_float(trad.get("edge_density"))
        ours_edge = safe_float(ours.get("edge_density"))
        trad_detail = safe_float(trad.get("detail_energy"))
        ours_detail = safe_float(ours.get("detail_energy"))
        edge_ratio = ours_edge / max(trad_edge, 1e-9)
        detail_ratio = ours_detail / max(trad_detail, 1e-9)
        row: dict[str, Any] = {
            "family": pair["family"],
            "traditional_target": pair["traditional_target"],
            "ours_case": pair["ours_case"],
            "ours_short": pair["ours_short"],
            "comparison_source": pair["comparison_source"],
            "traditional_image": str(pair["traditional_image"]),
            "ours_image": str(pair["ours_image"]),
            "traditional_image_exists": trad["image_exists"],
            "ours_image_exists": ours["image_exists"],
            "traditional_foreground_ratio": trad["foreground_ratio"],
            "ours_foreground_ratio": ours["foreground_ratio"],
            "traditional_edge_density": trad["edge_density"],
            "ours_edge_density": ours["edge_density"],
            "ours_vs_traditional_edge_density_ratio": edge_ratio,
            "traditional_detail_energy": trad["detail_energy"],
            "ours_detail_energy": ours["detail_energy"],
            "ours_vs_traditional_detail_energy_ratio": detail_ratio,
            "traditional_colorfulness": trad["colorfulness"],
            "ours_colorfulness": ours["colorfulness"],
            "ours_white_background_ratio": ours["white_background_ratio"],
            "runs": structure.get("runs", ""),
            "max_components_r0": safe_int(structure.get("max_components_r0", "")),
            "min_lcr_r0": safe_float(structure.get("min_lcr_r0", "")),
            "max_components_r1": safe_int(structure.get("max_components_r1", "")),
            "min_lcr_r1": safe_float(structure.get("min_lcr_r1", "")),
            "stability_grade": structure.get("stability_grade", ""),
            "final_recommendation": structure.get("final_recommendation", ""),
            "selection_budget": structure.get("selection_budget", ""),
            "paper_use": pair["paper_use"],
            "metric_boundary": "image metrics are auxiliary white-background diagnostics; structural claims use post-GLB surface metrics and QA notes",
        }
        row["display_priority"] = display_priority(row)
        rows.append(row)
    return rows


def display_priority(row: dict[str, Any]) -> str:
    if safe_float(row.get("min_lcr_r0")) >= 1.0 and safe_int(row.get("max_components_r0")) == 1:
        if row["family"] == "Space colonization":
            return "main-with-visual-caveat"
        return "main"
    if row["family"] == "IFS/transform" and safe_float(row.get("min_lcr_r0")) >= 0.999:
        return "main-caveated-transform-admission"
    return "appendix-or-rerender"


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Strict Traditional vs PS-RSLG One-to-One Metric Summary",
        "",
        "日期：2026-05-10",
        "",
        "本表只用于四族 one-to-one 图的展示决策：传统 target 是结构控制参照，不是弱 baseline；图像指标是白底 zoom 的辅助诊断，不替代人工视觉 QA 或 post-GLB topology diagnostics。",
        "",
        "| family | target | selected ours | priority | r0 comps | r0 LCR | edge ratio | detail ratio | paper use |",
        "|---|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {family} | `{target}` | `{ours}` | {priority} | {comp} | {lcr:.6f} | {edge:.3f} | {detail:.3f} | {use} |".format(
                family=row["family"],
                target=row["traditional_target"],
                ours=row["ours_short"],
                priority=row["display_priority"],
                comp=row["max_components_r0"],
                lcr=safe_float(row["min_lcr_r0"]),
                edge=safe_float(row["ours_vs_traditional_edge_density_ratio"]),
                detail=safe_float(row["ours_vs_traditional_detail_energy_ratio"]),
                use=row["paper_use"],
            )
        )
    lines.extend(
        [
            "",
            "## 展示建议",
            "",
            "- DLA/frontier：可作为 main-stable row，强调 frontier-attachment asset generation，不写物理 DLA/coral simulation。",
            "- IFS/lattice：pyrite lattice 可作为 transform-copy/operator admission 正例，但因 r0 tiny islands 仍需 caveat；radial ornament 是结构更稳的 appendix/main backup。",
            "- L-system/root：V25 root smooth-D 已把 root row 从 V24 visual caveat 升级到 r0 single-component diagnostic，可主文展示。",
            "- Space colonization：V25 SC tapered-B 保持 r0 single-component，但自然树冠视觉仍要谨慎，推荐 main-with-visual-caveat。",
            "",
            "## 指标边界",
            "",
            "- `edge ratio` 和 `detail ratio` 来自白底拼图的 foreground gradient；它们衡量 zoom 图中的细节/轮廓密度，不是 CLIP、人类偏好或 mesh topology。",
            "- `r0 comps/LCR` 来自 post-GLB surface voxel diagnostics；不是 watertight/manifold proof。",
            "- 所有结论必须和 white-background multi-zoom QA 一起使用。",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    rows = build_rows()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "traditional_vs_ps_rslg_one_to_one_metric_rows_20260510.csv", rows)
    (args.out_dir / "traditional_vs_ps_rslg_one_to_one_metric_rows_20260510.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(args.out_dir / "traditional_vs_ps_rslg_one_to_one_metric_summary_zh_20260510.md", rows)
    print(json.dumps({"rows": len(rows), "out_dir": str(args.out_dir)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
