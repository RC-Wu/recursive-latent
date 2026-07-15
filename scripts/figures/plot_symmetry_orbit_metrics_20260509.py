from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DATA = ROOT / "results" / "symmetry_orbit_metrics_20260509" / "symmetry_orbit_metrics_stage4.csv"
OUT_PNG = ROOT / "paper_siga" / "figures" / "symmetry_orbit_metrics_20260509.png"
OUT_PDF = ROOT / "paper_siga" / "figures" / "symmetry_orbit_metrics_20260509.pdf"


def main() -> None:
    with DATA.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    labels = ["Pyrite lattice", "Bismuth hopper", "Porous mineral"]
    keys = ["pyrite_stage4", "bismuth_stage4", "porous_stage4"]
    by_label = {row["label"]: row for row in rows}
    mirror = [float(by_label[k]["mirror_mean_iou"]) for k in keys]
    rot = [float(by_label[k]["z_rotation_mean_iou"]) for k in keys]
    overall = [float(by_label[k]["symmetry_mean_iou"]) for k in keys]

    plt.rcParams.update(
        {
            "font.size": 9,
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.dpi": 180,
            "savefig.dpi": 300,
        }
    )
    fig, ax = plt.subplots(figsize=(5.4, 2.55))
    x = np.arange(len(labels))
    width = 0.24
    colors = ["#4B8B6F", "#C89B4A", "#64748B"]
    series = [
        (x - width, mirror, "mirror mean", colors[0]),
        (x, rot, "z-rotation mean", colors[1]),
        (x + width, overall, "overall mean", colors[2]),
    ]
    for xpos, values, label, color in series:
        ax.bar(xpos, values, width, label=label, color=color)
    ax.set_ylim(0, 0.72)
    ax.set_ylabel("voxel IoU")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=0)
    ax.set_title("Stage-4 symmetry/orbit support metric", pad=8)
    ax.grid(axis="y", color="#E6E2DA", linewidth=0.8)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.04))
    for xpos, values, _label, _color in series:
        for xi, val in zip(xpos, values):
            ax.text(xi, val + 0.018, f"{val:.2f}", ha="center", va="bottom", fontsize=7, color="#3A3A3A")
    fig.text(
        0.01,
        -0.03,
        "Screening metric only: voxelized-vertex overlap after simple mirrors/rotations; not a proof of exact equivariance.",
        fontsize=7.5,
        color="#555B63",
    )
    fig.tight_layout(pad=0.8)
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, bbox_inches="tight", pad_inches=0.05)
    fig.savefig(OUT_PDF, bbox_inches="tight", pad_inches=0.05)
    print(OUT_PNG)
    print(OUT_PDF)


if __name__ == "__main__":
    main()
