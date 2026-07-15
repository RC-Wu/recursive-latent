#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "paper_siga" / "figures"
EVAL_DIR = ROOT / "docs" / "evaluation"

SC_DIR = ROOT / "results" / "traditional_baselines_space_colonization_20260508_v2"
MESH_CSV = ROOT / "results" / "mesh_metric_sweep_20260508" / "mesh_metrics.csv"
PROJ_CSV = ROOT / "docs" / "projection_ablation_20260508_1945" / "projection_ablation_table.csv"


def load_sc_skeleton_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for case in ["tree_canopy", "root_vine", "bush_shell"]:
        path = SC_DIR / case / "metrics.json"
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        rows.append(
            {
                "case": case,
                "method": "Traditional SC",
                "nodes": data["nodes"],
                "segments": data["segments"],
                "tips": data["tips"],
                "branch_nodes": data["branch_nodes"],
                "max_depth": data["max_depth"],
                "coverage_ratio": data["coverage_ratio"],
                "total_length": data["total_length"],
                "mean_segment_length": data["mean_segment_length"],
                "mesh_vertices": data["mesh_vertices"],
                "mesh_faces": data["mesh_faces"],
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def make_mesh_summary(mesh_df: pd.DataFrame) -> pd.DataFrame:
    selected = {
        "tree_canopy_space_colonization": "SC tree",
        "root_vine_space_colonization": "SC root",
        "bush_shell_space_colonization": "SC bush",
        "projection_pruning_compete_0550_tree_compete_d4_pruned": "Ours tree",
        "projection_pruning_compete_0550_tree_compete_fork_d4_pruned": "Fork tree",
        "projection_pruning_compete_0550_dla_compete_d4_pruned": "Ours DLA",
        "meshes_porous_container_compete_stage03": "Ours porous",
    }
    rows = mesh_df[mesh_df["label"].isin(selected)].copy()
    rows["short_label"] = rows["label"].map(selected)
    rows["primary_lcr"] = rows["largest_occupancy_component_ratio_6n"]
    rows["primary_comp"] = rows["occupancy_component_count_6n"]
    rows["frag_proxy"] = 1.0 - rows["primary_lcr"]
    rows = rows[
        [
            "short_label",
            "label",
            "method_hint",
            "vertices",
            "faces",
            "component_count",
            "largest_component_vertex_ratio",
            "primary_comp",
            "primary_lcr",
            "frag_proxy",
            "occupied_voxels",
            "box_count_dimension_proxy",
            "path",
        ]
    ]
    order = list(selected.values())
    rows["order"] = rows["short_label"].apply(order.index)
    return rows.sort_values("order").drop(columns=["order"])


def style_axes(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#e6e6e6", linewidth=0.8)
    ax.set_axisbelow(True)


def draw_figure(sc_df: pd.DataFrame, mesh_summary: pd.DataFrame, proj_df: pd.DataFrame) -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.size": 9.5,
            "axes.titlesize": 10.5,
            "axes.labelsize": 9.5,
            "xtick.labelsize": 8.0,
            "ytick.labelsize": 8.0,
            "legend.fontsize": 8.0,
            "figure.dpi": 160,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
        }
    )

    fig = plt.figure(figsize=(10.8, 3.2))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.22, 1.36], wspace=0.48)

    ax0 = fig.add_subplot(gs[0, 0])
    cases = ["tree_canopy", "root_vine", "bush_shell"]
    labels = ["Tree", "Root", "Bush"]
    coverage = [float(sc_df.loc[sc_df["case"] == c, "coverage_ratio"].iloc[0]) for c in cases]
    tips = [float(sc_df.loc[sc_df["case"] == c, "tips"].iloc[0]) for c in cases]
    bars = ax0.bar(labels, coverage, color="#4C78A8", width=0.58)
    ax0.set_ylim(0, 1.08)
    ax0.set_ylabel("Coverage")
    ax0.set_title("Traditional SC skeleton")
    style_axes(ax0)
    ax0b = ax0.twinx()
    ax0b.plot(labels, tips, color="#F58518", marker="o", linewidth=1.7, label="tips")
    ax0b.set_ylabel("Tips", color="#8a4b08", labelpad=3)
    ax0b.tick_params(axis="y", colors="#8a4b08")
    ax0b.spines["top"].set_visible(False)
    for bar, val in zip(bars, coverage):
        ax0.text(bar.get_x() + bar.get_width() / 2, val + 0.02, f"{val:.2f}", ha="center", va="bottom", fontsize=8)

    ax1 = fig.add_subplot(gs[0, 1])
    mesh_plot = mesh_summary.copy()
    colors = ["#72B7B2" if label.startswith("SC") else "#54A24B" if label.startswith("Ours") else "#E45756" for label in mesh_plot["short_label"]]
    ax1.bar(mesh_plot["short_label"], mesh_plot["primary_lcr"], color=colors, width=0.62)
    ax1.set_ylim(0, 1.08)
    ax1.set_ylabel("LCR (occupancy)")
    ax1.set_title("Primary mesh connectivity proxy")
    ax1.tick_params(axis="x", rotation=32)
    style_axes(ax1)
    for tick in ax1.get_xticklabels():
        tick.set_ha("right")

    ax2 = fig.add_subplot(gs[0, 2])
    x = range(len(proj_df))
    width = 0.34
    ax2.bar([i - width / 2 for i in x], proj_df["direct_components"], width=width, label="Direct raw comps", color="#B279A2")
    ax2.bar([i + width / 2 for i in x], proj_df["per_depth_raw_components"], width=width, label="Per-depth raw comps", color="#59A14F")
    ax2.set_yscale("log")
    ax2.set_ylabel("Component count (log)")
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(["Vine\ncompete", "Tree\ncompete", "Vine\nfork", "Tree\nfork"])
    ax2.set_title("Projection ablation")
    style_axes(ax2)
    ax2b = ax2.twinx()
    ax2b.plot(list(x), proj_df["direct_largest_ratio"], marker="s", color="#8C564B", linewidth=1.3, label="Direct LCR")
    ax2b.plot(list(x), proj_df["per_depth_largest_ratio"], marker="o", color="#2F4B7C", linewidth=1.6, label="Per-depth LCR")
    ax2b.set_ylim(0, 1.08)
    ax2b.set_ylabel("Largest ratio")
    ax2b.spines["top"].set_visible(False)

    handles0, labels0 = ax2.get_legend_handles_labels()
    handles1, labels1 = ax2b.get_legend_handles_labels()
    ax2.legend(handles0 + handles1, labels0 + labels1, frameon=False, loc="upper right", ncol=1)

    fig.suptitle("Space-competition metrics from existing 2026-05-08 runs", y=1.02, fontsize=11)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / "space_competition_metrics_20260509.png"
    fig.savefig(out)
    plt.close(fig)


def main() -> None:
    sc_rows = load_sc_skeleton_rows()
    write_csv(EVAL_DIR / "space_colonization_skeleton_metrics_20260509.csv", sc_rows)
    sc_df = pd.DataFrame(sc_rows)

    mesh_df = pd.read_csv(MESH_CSV)
    mesh_summary = make_mesh_summary(mesh_df)
    mesh_summary.to_csv(EVAL_DIR / "space_competition_mesh_proxy_summary_20260509.csv", index=False)

    proj_df = pd.read_csv(PROJ_CSV)
    proj_df.to_csv(EVAL_DIR / "space_competition_projection_ablation_summary_20260509.csv", index=False)

    draw_figure(sc_df, mesh_summary, proj_df)


if __name__ == "__main__":
    main()
