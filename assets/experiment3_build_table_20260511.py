#!/usr/bin/env python3
"""Build compact Experiment 3 novelty-gate tables from the route manifest."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_BASE = ROOT / "results/experiment3_sparse_latent_vs_meshspace_20260511"
DEFAULT_TEX = ROOT / "paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex"

CASE_ORDER = [
    "tree_crown",
    "root_fan",
    "vine",
    "spider_rosette",
    "coral",
    "pyrite",
    "bismuth",
    "radial_ornament",
]

MAIN_CASE_ORDER = [
    "tree_crown",
    "bismuth",
    "coral",
    "pyrite",
]

DIAGNOSTIC_CASES = {
    "root_fan",
    "vine",
    "spider_rosette",
    "radial_ornament",
}

METHOD_ORDER = [
    "trellis2_oneshot_image",
    "trellis2_root_latentcopy",
    "trellis2_generatedroot_meshcopy",
    "hunyuan_root_meshcopy",
    "ps_rslg",
]

METHOD_LABELS = {
    "trellis2_oneshot_image": "Trellis2 one-shot",
    "trellis2_root_latentcopy": "Trellis2 latent-copy",
    "trellis2_generatedroot_meshcopy": "Trellis2 root+mesh-copy",
    "hunyuan_root_meshcopy": "Hunyuan root+mesh-copy",
    "ps_rslg": "PS-RSLG",
}

CASE_LABELS = {
    "tree_crown": "tree crown",
    "root_fan": "root fan",
    "vine": "vine",
    "spider_rosette": "spider rosette",
    "coral": "coral",
    "pyrite": "pyrite",
    "bismuth": "bismuth",
    "radial_ornament": "radial ornament",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "case",
        "method",
        "state_update",
        "projection",
        "copy_rep",
        "raw_components",
        "occ_components",
        "LCR",
        "status",
        "failure_label",
        "asset_path",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def pick_best(rows: list[dict[str, str]], case: str, method: str) -> dict[str, str] | None:
    candidates = [r for r in rows if r.get("case_short") == case and r.get("method_id") == method]
    if not candidates:
        return None

    def score(row: dict[str, str]) -> tuple[int, int, int, int]:
        status = row.get("route_status", "")
        ready = row.get("ready_for_main", "")
        has_metrics = int(bool(row.get("metrics_source")))
        has_asset = int(bool(row.get("asset_path") or row.get("source_path")))
        metrics_source = row.get("metrics_source", "")
        status_score = {
            "ready": 5,
            "fragmented_copy_paste": 5,
            "success": 5,
            "generated_import_render_QA_pending_topology_metrics": 3,
            "blocked": 1,
            "needs_remote": 0,
            "needs_local": 0,
        }.get(status, 2)
        ready_score = {"yes": 4, "needs_visual_qa": 3, "supplement": 2, "needs_label": 1, "no": 0}.get(ready, 0)
        variant_score = int(bool(row.get("variant")))
        exp3_score = int(
            method.startswith("trellis2_")
            and "experiment3_sparse_latent_vs_meshspace_20260511" in metrics_source
        )
        return (exp3_score, status_score, ready_score, has_metrics + has_asset + variant_score)

    return sorted(candidates, key=score, reverse=True)[0]


def fmt_int(value: str) -> str:
    if value in {"", "N/A"}:
        return "--"
    try:
        return str(int(float(value)))
    except Exception:
        return value


def fmt_float(value: str) -> str:
    if value in {"", "N/A"}:
        return "--"
    try:
        return f"{float(value):.3f}"
    except Exception:
        return value


def status_short(row: dict[str, str] | None) -> str:
    if row is None:
        return "missing"
    status = row.get("route_status", "")
    failure = row.get("failure_label", "")
    if status in {"needs_remote", "needs_local"}:
        return status.replace("_", " ")
    if row.get("method_id") == "ps_rslg":
        if row.get("ready_for_main") != "yes":
            return "QA-gated positive"
        try:
            raw_components = int(float(row.get("raw_component_count") or row.get("component_count") or "1"))
        except Exception:
            raw_components = 1
        try:
            occ_components = int(float(row.get("occupancy_component_count_6n") or "1"))
        except Exception:
            occ_components = 1
        if raw_components > 1 or occ_components > 1:
            return "proxy-positive+caveat"
        return "selected positive"
    if "copy" in failure:
        return "copy-state control"
    if "one_shot" in failure:
        return "one-shot control"
    return status.replace("_", " ") or row.get("visual_qa_status", "")


def compact_rows(manifest_rows: list[dict[str, str]], case_order: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for case in case_order:
        for method in METHOD_ORDER:
            row = pick_best(manifest_rows, case, method)
            if row is None:
                continue
            if method == "hunyuan_root_meshcopy" and row.get("route_status") in {"needs_remote", "needs_local"}:
                continue
            if method == "ps_rslg" and row.get("route_status") in {"needs_remote", "needs_local"}:
                continue
            out.append(
                {
                    "case": CASE_LABELS.get(case, case),
                    "method": METHOD_LABELS.get(method, method),
                    "state_update": row.get("latent_update_used") or ("yes" if method == "ps_rslg" else "0"),
                    "projection": row.get("projection_used") or ("yes" if method == "ps_rslg" else "0"),
                    "copy_rep": fmt_float(row.get("copy_repetition_score", "")),
                    "raw_components": fmt_int(row.get("raw_component_count") or row.get("component_count", "")),
                    "occ_components": fmt_int(row.get("occupancy_component_count_6n", "")),
                    "LCR": fmt_float(row.get("LCR") or row.get("largest_occupancy_component_ratio_6n", "")),
                    "status": status_short(row),
                    "failure_label": row.get("failure_label", ""),
                    "asset_path": row.get("asset_path") or row.get("source_path", ""),
                }
            )
    return out


def esc_tex(text: Any) -> str:
    s = str(text)
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in s)


def write_tex(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "% Auto-generated by assets/experiment3_build_table_20260511.py",
        "% Source: results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_master_manifest.csv",
        r"\begin{table*}[t]",
        r"\centering",
        r"\small",
        r"\setlength{\tabcolsep}{3.0pt}",
        r"\begin{tabular}{llcccrrrl}",
        r"\toprule",
        r"Case & Method & State & Proj. & Copy & Raw comp. & Occ. comp. & LCR & Status \\",
        r"\midrule",
    ]
    last_case = None
    for row in rows:
        if last_case is not None and row["case"] != last_case:
            lines.append(r"\midrule")
        last_case = row["case"]
        lines.append(
            " & ".join(
                [
                    esc_tex(row["case"]),
                    esc_tex(row["method"]),
                    esc_tex(row["state_update"]),
                    esc_tex(row["projection"]),
                    esc_tex(row["copy_rep"]),
                    esc_tex(row["raw_components"]),
                    esc_tex(row["occ_components"]),
                    esc_tex(row["LCR"]),
                    esc_tex(row["status"]),
                ]
            )
            + r" \\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        (
            r"\caption{Quality-gated Experiment 3 novelty comparison between ordinary one-shot generation, "
            r"trivial latent or mesh-copy controls, representative Hunyuan text-root mesh-space "
            r"baselines, and PS-RSLG. State indicates whether the row performs a recursive latent-state "
            r"update after the root; Proj. indicates per-depth admissibility projection; Copy marks "
            r"direct root reuse. Raw components are face-connectivity islands, while Occ. comp. and "
            r"LCR are 64-resolution vertex-occupancy diagnostics. LCR is not used alone as topology "
            r"proof: high occupancy LCR can coexist with thousands of raw mesh islands in one-shot "
            r"or copy baselines. The main table keeps only visually strong claim-bearing cases: tree "
            r"crown, bismuth, coral, and a caveated pyrite/lattice row. Hunyuan rows are text-root "
            r"representative mesh-space baselines, not universal coverage.}"
        ),
        r"\label{tab:experiment3-sparse-latent-vs-mesh-space}",
        r"\end{table*}",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_supplement_tex(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "% Auto-generated by assets/experiment3_build_table_20260511.py",
        "% Supplement/diagnostic full eight-case coverage.",
        r"\begin{table*}[t]",
        r"\centering",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2.4pt}",
        r"\begin{tabular}{llcccrrrl}",
        r"\toprule",
        r"Case & Method & State & Proj. & Copy & Raw comp. & Occ. comp. & LCR & Status \\",
        r"\midrule",
    ]
    last_case = None
    for row in rows:
        if last_case is not None and row["case"] != last_case:
            lines.append(r"\midrule")
        last_case = row["case"]
        status = str(row["status"])
        short = next((k for k, v in CASE_LABELS.items() if v == row["case"]), "")
        if short in DIAGNOSTIC_CASES and row["method"] == METHOD_LABELS["ps_rslg"]:
            status = f"supplement/diagnostic: {status}"
        lines.append(
            " & ".join(
                [
                    esc_tex(row["case"]),
                    esc_tex(row["method"]),
                    esc_tex(row["state_update"]),
                    esc_tex(row["projection"]),
                    esc_tex(row["copy_rep"]),
                    esc_tex(row["raw_components"]),
                    esc_tex(row["occ_components"]),
                    esc_tex(row["LCR"]),
                    esc_tex(status),
                ]
            )
            + r" \\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        (
            r"\caption{Supplementary diagnostic Experiment 3 table with all eight candidate targets. "
            r"Rows outside the quality-gated main subset are retained to document coverage and failure "
            r"modes, not as primary positive evidence.}"
        ),
        r"\label{tab:experiment3-sparse-latent-vs-mesh-space-supplement}",
        r"\end{table*}",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_BASE / "experiment3_master_manifest.csv")
    parser.add_argument("--out-csv", type=Path, default=DEFAULT_BASE / "experiment3_compact_table_20260511.csv")
    parser.add_argument("--out-json", type=Path, default=DEFAULT_BASE / "experiment3_compact_table_20260511.json")
    parser.add_argument("--out-tex", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--out-supp-tex",
        type=Path,
        default=ROOT / "paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_supplement_20260511.tex",
    )
    args = parser.parse_args()

    manifest_rows = read_csv(args.manifest)
    main_rows = compact_rows(manifest_rows, MAIN_CASE_ORDER)
    all_rows = compact_rows(manifest_rows, CASE_ORDER)
    write_csv(args.out_csv, main_rows)
    args.out_json.write_text(json.dumps(main_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    write_tex(args.out_tex, main_rows)
    supp_csv = args.out_csv.with_name("experiment3_compact_table_supplement_8case_20260511.csv")
    supp_json = args.out_json.with_name("experiment3_compact_table_supplement_8case_20260511.json")
    write_csv(supp_csv, all_rows)
    supp_json.write_text(json.dumps(all_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    write_supplement_tex(args.out_supp_tex, all_rows)
    print(
        json.dumps(
            {
                "main_rows": len(main_rows),
                "supplement_rows": len(all_rows),
                "csv": str(args.out_csv),
                "tex": str(args.out_tex),
                "supplement_tex": str(args.out_supp_tex),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
