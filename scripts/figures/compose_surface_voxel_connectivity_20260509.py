from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
CSV = ROOT / "results" / "surface_voxel_connectivity_20260509" / "surface_voxel_connectivity_summary.csv"
FIG_DIR = ROOT / "paper_siga" / "figures"
OUT_PNG = FIG_DIR / "surface_voxel_connectivity_metric_20260509.png"
OUT_PDF = FIG_DIR / "surface_voxel_connectivity_metric_20260509.pdf"

COLORS = {
    "pyrite_hq_glb": "#3E6385",
    "bismuth_hq_glb": "#947F56",
    "porous_mineral_glb": "#5E8B72",
}
LABELS = {
    "pyrite_hq_glb": "Pyrite HQ GLB",
    "bismuth_hq_glb": "Bismuth HQ GLB",
    "porous_mineral_glb": "Porous GLB",
}


def load_rows() -> list[dict[str, str]]:
    with CSV.open("r", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row["family"].endswith("_glb")]


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    plt.rcParams.update(
        {
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 7,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.45))
    for family in ["pyrite_hq_glb", "bismuth_hq_glb", "porous_mineral_glb"]:
        fam = sorted([r for r in rows if r["family"] == family], key=lambda r: int(r["stage"]))
        xs = [int(r["stage"]) for r in fam]
        lcr = [float(r["surface_occ64_r0_lcr_6n"]) for r in fam]
        comps = [int(r["surface_occ64_r0_components_6n"]) for r in fam]
        axes[0].plot(xs, lcr, marker="o", linewidth=1.8, markersize=3.8, color=COLORS[family], label=LABELS[family])
        axes[1].plot(xs, comps, marker="o", linewidth=1.8, markersize=3.8, color=COLORS[family], label=LABELS[family])

    axes[0].set_title("Strict surface-voxel LCR")
    axes[0].set_ylabel("largest component ratio")
    axes[0].set_ylim(0.965, 1.004)
    axes[0].set_yticks([0.97, 0.98, 0.99, 1.00])
    axes[1].set_title("Strict component count")
    axes[1].set_ylabel("components")
    axes[1].set_ylim(0.75, 4.25)
    axes[1].set_yticks([1, 2, 3, 4])
    for ax in axes:
        ax.set_xlabel("depth")
        ax.set_xticks([1, 2, 3, 4])
        ax.grid(True, color="#E4E1D9", linewidth=0.7)

    axes[1].legend(frameon=False, loc="upper right")
    fig.suptitle("Surface-sampled GLB connectivity diagnostic", y=1.04, fontsize=10)
    fig.text(
        0.5,
        -0.05,
        "Radius-1 seam/alias-tolerant surface occupancy gives LCR=1.000 and one component for all shown rows; strict radius-0 exposes small porous seam fragments.",
        ha="center",
        va="top",
        fontsize=7,
        color="#555555",
    )
    fig.tight_layout(w_pad=2.2)
    fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight", pad_inches=0.05)
    fig.savefig(OUT_PDF, bbox_inches="tight", pad_inches=0.05)
    print(OUT_PNG)
    print(OUT_PDF)


if __name__ == "__main__":
    main()
