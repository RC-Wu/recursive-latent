#!/usr/bin/env python3
"""Build claim-aligned metric summary artifacts from existing local results."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "results" / "claim_aligned_metric_summary_20260509"
FIG_DIR = ROOT / "paper_siga" / "figures"


def read_csv(rel: str) -> pd.DataFrame:
    return pd.read_csv(ROOT / rel)


def fmt_range(values, digits=3) -> str:
    vals = [float(v) for v in values if pd.notna(v)]
    if not vals:
        return "n/a"
    lo, hi = min(vals), max(vals)
    if abs(lo - hi) < 10 ** (-(digits + 1)):
        return f"{lo:.{digits}f}"
    return f"{lo:.{digits}f}-{hi:.{digits}f}"


def fmt_int_range(values) -> str:
    vals = [int(v) for v in values if pd.notna(v)]
    if not vals:
        return "n/a"
    lo, hi = min(vals), max(vals)
    if lo == hi:
        return str(lo)
    return f"{lo}-{hi}"


def add_source_depth_rows(rows: list[dict]) -> None:
    specs = [
        (
            "bismuth",
            "bismuth_hopper_depth",
            "results/connected_scaffold_depth_cases_20260509/bismuth_hopper_depth/metrics.csv",
            "connected scaffold depth source; not physical crystal growth",
        ),
        (
            "pyrite",
            "pyrite_lattice_depth",
            "results/connected_scaffold_depth_cases_20260509/pyrite_lattice_depth/metrics.csv",
            "connected crystal-lattice scaffold source; mesh components grow with depth",
        ),
        (
            "DLA/coral",
            "volumetric_coral_depth",
            "results/connected_coral_depth_cases_20260509/volumetric_coral_depth/metrics.csv",
            "grammar-native connected coral/DLA-inspired scaffold; not true DLA growth",
        ),
    ]
    for family, case, rel, note in specs:
        df = read_csv(rel)
        for _, r in df.iterrows():
            rows.append(
                {
                    "family": family,
                    "case": case,
                    "evidence_class": "source_depth_scaffold",
                    "stage_or_method": int(r["stage"]),
                    "occ_comp_6n": int(r["occupancy_component_count_6n"]),
                    "occ_lcr_6n": float(r["largest_occupancy_component_ratio_6n"]),
                    "mesh_or_face_components": int(r["mesh_component_count"]),
                    "mesh_or_face_lcr": float(r["largest_mesh_component_vertex_ratio"]),
                    "vertices": int(r["vertices"]),
                    "faces": int(r["faces"]),
                    "effective_resolution_proxy": f"occupied_voxels={int(r['occupied_voxels'])}",
                    "branch_path_proxy": "not measured",
                    "visual_verdict": "pending neutral/zoom QA",
                    "claim_verdict": note,
                    "source_file": rel,
                }
            )


def add_vine_rows(rows: list[dict]) -> None:
    metrics = read_csv("results/vine_depth_textured_showcase_metrics_20260509/metrics.csv")
    branch = read_csv("results/branch_path_metrics_20260509/branch_path_metrics_compact.csv")
    branch_map = {r["label"]: r for _, r in branch.iterrows()}
    for _, r in metrics.iterrows():
        label = r["label"]
        stage = int(str(label).split("_stage_")[1][:2])
        b = branch_map.get(label)
        if b is not None:
            branch_proxy = (
                f"root_ratio={float(b['root_component_ratio']):.3f}; "
                f"path_span={float(b['bbox_normalized_path_span']):.3f}; "
                f"orphan_tip_proxy={int(b['orphan_tip_proxy'])}"
            )
        else:
            branch_proxy = "not measured"
        rows.append(
            {
                "family": "vine/root/tree",
                "case": "vine_d5_projected_compete",
                "evidence_class": "textured_depth_glb",
                "stage_or_method": stage,
                "occ_comp_6n": int(r["occupancy_component_count_6n"]),
                "occ_lcr_6n": float(r["largest_occupancy_component_ratio_6n"]),
                "mesh_or_face_components": int(r["component_count"]),
                "mesh_or_face_lcr": float(r["largest_component_vertex_ratio"]),
                "vertices": int(r["vertices"]),
                "faces": int(r["faces"]),
                "effective_resolution_proxy": (
                    f"occ64={int(r['occupied_voxels'])}; "
                    f"box_count={r['box_count_occupied']}"
                ),
                "branch_path_proxy": branch_proxy,
                "visual_verdict": "textured asset exists; neutral/zoom QA missing",
                "claim_verdict": "supports per-depth occupancy-connected vine showcase only",
                "source_file": "results/vine_depth_textured_showcase_metrics_20260509/metrics.csv",
            }
        )


def add_bridge_negative_rows(rows: list[dict]) -> None:
    # Copied from local mesh-only QA doc so the negative claim remains explicit in the table.
    records = [
        ("hard_dla", "raw", 5, 0.301, 4, 0.387, "fail: fragmented"),
        ("hard_dla", "raw_bridge_smooth", 1, 1.000, 6, 0.670, "fail: face connected but occupancy fragmented"),
        ("hard_dla", "sparse_close_bridge", 3, 0.931, 4, 0.738, "fail: fake bridge / over-closing"),
        ("hard_dla", "mesh_bridge_smooth", 3, 0.916, 6, 0.615, "fail: still unusable"),
        ("volumetric_dla", "raw", 8, 0.447, 8, 0.408, "fail: natural-looking but fragmented"),
        ("volumetric_dla", "raw_bridge_smooth", 2, 0.984, 9, 0.416, "fail: face improved, occupancy not"),
        ("volumetric_dla", "mesh_bridge_smooth", 1, 1.000, 4, 0.961, "partial: best bridge but not singly connected"),
        ("volumetric_dla", "sparse_close_bridge", 4, 0.935, 5, 0.482, "fail: over-closing traces"),
    ]
    for case, method, face_c, face_lcr, occ_c, occ_lcr, verdict in records:
        rows.append(
            {
                "family": "DLA/coral",
                "case": f"dla_bridge_ablation/{case}",
                "evidence_class": "posthoc_bridge_ablation",
                "stage_or_method": method,
                "occ_comp_6n": occ_c,
                "occ_lcr_6n": occ_lcr,
                "mesh_or_face_components": face_c,
                "mesh_or_face_lcr": face_lcr,
                "vertices": None,
                "faces": None,
                "effective_resolution_proxy": "mesh-only QA summary",
                "branch_path_proxy": "not measured; needs frontier/porosity metrics",
                "visual_verdict": verdict,
                "claim_verdict": "negative ablation: post-hoc bridge is not sufficient evidence",
                "source_file": "docs/evaluation/dla_bridge_ablation_mesh_qa_zh_20260509.md",
            }
        )


def build_summary(long_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    specs = [
        (
            "vine/root/tree",
            "vine_d5_projected_compete",
            "positive",
            "Per-depth 6N occupancy support is connected for textured vine stages.",
            "Raw textured face components are extremely fragmented; branch/path values are mesh-voxel proxies.",
            "Matched L-system/space-colonization/direct/final-only/prune/bridge matrix; explicit skeleton/root anchor; neutral junction/tip/root zoom QA.",
            "Projection-stabilized vine showcase keeps voxelized 6N occupancy support connected across displayed depths.",
            "Tree/root/vine assets are fully topology-clean or systematically beat traditional baselines.",
        ),
        (
            "bismuth",
            "bismuth_hopper_depth",
            "positive_with_caveat",
            "Source depth stages are occupancy-connected and mesh LCR remains high.",
            "This is a bismuth-like scaffold, not physical bismuth crystal growth; facet/contact QA is absent.",
            "Same-root IFS/lattice baseline; facet/contact metrics; neutral facet/cavity zoom; PBR winner QA.",
            "Bismuth-like non-tree scaffold can be kept occupancy-connected across depth.",
            "Bismuth crystallization or physical growth is solved.",
        ),
        (
            "pyrite",
            "pyrite_lattice_depth",
            "mixed",
            "Source depth stages keep occupancy comp=1 and LCR=1.0.",
            "Mesh component count rises from 1 to 139 with depth; raw GLB face fragmentation remains a topology caveat.",
            "Same-root lattice/IFS baseline; symmetry/contact/facet metrics; mesh fragmentation explanation; neutral zoom QA.",
            "Pyrite-like lattice scaffold maintains connected voxel support across depth.",
            "Crystal generation/topology is solved at mesh-face level.",
        ),
        (
            "DLA/coral",
            "volumetric_coral_depth",
            "stress_positive_with_negative_ablation",
            "Grammar-native coral/DLA-inspired source stages are occupancy-connected.",
            "Post-hoc DLA bridge ablation often improves one metric while failing occupancy or visual QA.",
            "True DLA/frontier baseline; direct/final-only/prune/bridge matrix; branch openness, frontier attachment, porosity/cavity, bridge survival, over-closing labels.",
            "DLA/coral is a stress test motivating grammar-native connected support.",
            "True DLA growth/frontier process is solved.",
        ),
    ]
    for family, case, verdict, pos, neg, missing, allowed, not_allowed in specs:
        subset = long_df[(long_df["family"] == family) & (long_df["case"] == case)]
        rows.append(
            {
                "family": family,
                "case": case,
                "evidence_verdict": verdict,
                "stages_or_methods": ",".join(map(str, subset["stage_or_method"].tolist())),
                "occ_comp_6n_range": fmt_int_range(subset["occ_comp_6n"]),
                "occ_lcr_6n_range": fmt_range(subset["occ_lcr_6n"], 3),
                "mesh_or_face_component_range": fmt_int_range(subset["mesh_or_face_components"]),
                "mesh_or_face_lcr_range": fmt_range(subset["mesh_or_face_lcr"], 3),
                "effective_resolution_or_proxy": " | ".join(subset["effective_resolution_proxy"].head(2).astype(str)),
                "branch_path_proxy": " | ".join(subset["branch_path_proxy"].head(2).astype(str)),
                "visual_pass_fail": " | ".join(subset["visual_verdict"].drop_duplicates().head(3).astype(str)),
                "positive_evidence": pos,
                "negative_or_caveat": neg,
                "missing_quant_experiments": missing,
                "allowed_claim_now": allowed,
                "not_allowed_claim": not_allowed,
            }
        )
    bridge = long_df[long_df["evidence_class"] == "posthoc_bridge_ablation"]
    rows.append(
        {
            "family": "DLA/coral",
            "case": "dla_bridge_ablation",
            "evidence_verdict": "negative",
            "stages_or_methods": ",".join(map(str, bridge["stage_or_method"].tolist())),
            "occ_comp_6n_range": fmt_int_range(bridge["occ_comp_6n"]),
            "occ_lcr_6n_range": fmt_range(bridge["occ_lcr_6n"], 3),
            "mesh_or_face_component_range": fmt_int_range(bridge["mesh_or_face_components"]),
            "mesh_or_face_lcr_range": fmt_range(bridge["mesh_or_face_lcr"], 3),
            "effective_resolution_or_proxy": "mesh-only QA summary",
            "branch_path_proxy": "frontier/porosity/branch openness not measured",
            "visual_pass_fail": "mostly fail; best bridge remains occ_comp=4",
            "positive_evidence": "Shows why face connectivity or LCR alone is insufficient.",
            "negative_or_caveat": "Visual over-closing/fake bridges invalidate it as a positive DLA result.",
            "missing_quant_experiments": "Bridge survival labels, fake-bridge labels, porosity/cavity, true DLA baseline.",
            "allowed_claim_now": "Negative ablation for post-hoc bridge repair.",
            "not_allowed_claim": "DLA bridge repair solves connected generation.",
        }
    )
    return pd.DataFrame(rows)


def write_latex_table(summary: pd.DataFrame) -> None:
    cols = [
        "family",
        "case",
        "occ_comp_6n_range",
        "occ_lcr_6n_range",
        "mesh_or_face_component_range",
        "mesh_or_face_lcr_range",
        "visual_pass_fail",
    ]
    table = summary[cols].rename(
        columns={
            "family": "Family",
            "case": "Case",
            "occ_comp_6n_range": "Occ. comp.",
            "occ_lcr_6n_range": "Occ. LCR",
            "mesh_or_face_component_range": "Mesh/face comp.",
            "mesh_or_face_lcr_range": "Mesh/face LCR",
            "visual_pass_fail": "Visual / QA status",
        }
    )
    latex = table.to_latex(index=False, escape=True, column_format="llccclp{0.25\\linewidth}")
    (FIG_DIR / "claim_aligned_metric_summary_table_20260509.tex").write_text(latex)


def to_markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in df.iterrows():
        values = [str(row[col]).replace("\n", " ").replace("|", "\\|") for col in cols]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"


def make_plot(long_df: pd.DataFrame) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.dpi": 160,
            "savefig.dpi": 300,
        }
    )
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.1), constrained_layout=True)

    depth_cases = long_df[long_df["evidence_class"].isin(["textured_depth_glb", "source_depth_scaffold"])]
    color_map = {
        "vine_d5_projected_compete": "#2ca02c",
        "bismuth_hopper_depth": "#1f77b4",
        "pyrite_lattice_depth": "#9467bd",
        "volumetric_coral_depth": "#ff7f0e",
    }
    for case, df in depth_cases.groupby("case"):
        x = pd.to_numeric(df["stage_or_method"])
        c = color_map.get(case, None)
        axes[0].plot(x, df["occ_comp_6n"], marker="o", label=case.replace("_depth", ""), color=c)
        axes[1].plot(x, df["mesh_or_face_components"], marker="o", label=case.replace("_depth", ""), color=c)

    bridge = long_df[long_df["evidence_class"] == "posthoc_bridge_ablation"].copy()
    bridge["x"] = range(1, len(bridge) + 1)
    axes[0].scatter(bridge["x"] / 2, bridge["occ_comp_6n"], marker="x", color="#d62728", label="DLA bridge ablation")
    axes[1].scatter(bridge["x"] / 2, bridge["mesh_or_face_components"], marker="x", color="#d62728", label="DLA bridge ablation")

    axes[0].set_title("Occupancy connectedness")
    axes[0].set_xlabel("Depth / ablation index")
    axes[0].set_ylabel("6N component count")
    axes[0].set_ylim(0.5, max(10, bridge["occ_comp_6n"].max() + 1))

    axes[1].set_title("Mesh or raw face caveat")
    axes[1].set_xlabel("Depth / ablation index")
    axes[1].set_ylabel("component count (log)")
    axes[1].set_yscale("log")

    branch = read_csv("results/branch_path_metrics_20260509/branch_path_metrics_compact.csv")
    branch = branch[
        branch["label"].isin(
            [
                "vine_d5_projected_compete_stage_01_parthenocissus_steps4_tex1024_xformers_textured",
                "vine_d5_projected_compete_stage_02_parthenocissus_steps4_tex1024_xformers_textured",
                "vine_d5_projected_compete_stage_03_parthenocissus_steps4_tex1024_xformers_textured",
                "vine_d5_projected_compete_stage_04_parthenocissus_steps4_tex1024_xformers_textured",
                "root_vine_skeleton",
                "tree_canopy_skeleton",
                "bush_shell_skeleton",
                "tree_compete_d4_pruned",
                "masked_tree_compete_fork_s1_a025_d3_pruned",
            ]
        )
    ].copy()
    short_map = {
        "vine_d5_projected_compete_stage_01_parthenocissus_steps4_tex1024_xformers_textured": "vine d1",
        "vine_d5_projected_compete_stage_02_parthenocissus_steps4_tex1024_xformers_textured": "vine d2",
        "vine_d5_projected_compete_stage_03_parthenocissus_steps4_tex1024_xformers_textured": "vine d3",
        "vine_d5_projected_compete_stage_04_parthenocissus_steps4_tex1024_xformers_textured": "vine d4",
        "root_vine_skeleton": "SC root",
        "tree_canopy_skeleton": "SC tree",
        "bush_shell_skeleton": "SC bush",
        "tree_compete_d4_pruned": "tree pruned",
        "masked_tree_compete_fork_s1_a025_d3_pruned": "masked fork",
    }
    branch["short"] = branch["label"].map(short_map)
    axes[2].bar(branch["short"], branch["root_component_ratio"], color="#7f7f7f")
    axes[2].set_ylim(0.84, 1.01)
    axes[2].set_title("Root reachability proxy")
    axes[2].set_ylabel("root component ratio")
    axes[2].tick_params(axis="x", rotation=45)
    axes[2].axhline(1.0, color="black", linewidth=0.8, linestyle=":")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.08))
    for ext in ("pdf", "png"):
        fig.savefig(FIG_DIR / f"claim_aligned_metric_summary_20260509.{ext}", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    add_vine_rows(rows)
    add_source_depth_rows(rows)
    add_bridge_negative_rows(rows)

    long_df = pd.DataFrame(rows)
    summary = build_summary(long_df)

    long_df.to_csv(RESULT_DIR / "claim_aligned_metric_long.csv", index=False)
    summary.to_csv(RESULT_DIR / "claim_aligned_metric_summary.csv", index=False)
    (RESULT_DIR / "claim_aligned_metric_summary.json").write_text(
        json.dumps(summary.to_dict(orient="records"), indent=2, ensure_ascii=False)
    )
    (RESULT_DIR / "claim_aligned_metric_summary.md").write_text(to_markdown_table(summary))

    write_latex_table(summary)
    make_plot(long_df)

    print(f"Wrote {RESULT_DIR}")
    print(f"Wrote {FIG_DIR / 'claim_aligned_metric_summary_20260509.pdf'}")


if __name__ == "__main__":
    main()
