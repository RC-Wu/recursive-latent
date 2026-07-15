from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt


# Colorblind-safe categorical palette based on Okabe-Ito / Paul Tol style choices.
# Use redundant markers and line styles so the figure remains interpretable in grayscale.
OPERATOR_COLORS = {
    "compete": "#009E73",
    "compete_fork": "#CC79A7",
    "fork_side": "#E69F00",
    "portal": "#56B4E9",
    "scale_down": "#6B5B95",
}

METHOD_COLORS = {
    "Direct": "#9AA0A6",
    "Final-only": "#D55E00",
    "Per-depth": "#0072B2",
}

DISPLAY_LABELS = {
    "compete": "Competition",
    "compete_fork": "Competition+Fork",
    "fork_side": "Side Fork",
    "portal": "Portal Copy",
    "scale_down": "Scale Copy",
}

MARKERS = {
    "compete": "o",
    "compete_fork": "s",
    "fork_side": "^",
    "portal": "D",
    "scale_down": "P",
}

LINESTYLES = {
    "compete": "-",
    "compete_fork": "--",
    "fork_side": "-.",
    "portal": ":",
    "scale_down": (0, (3, 1, 1, 1)),
}


def configure_paper_style() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif"],
            "font.size": 7.0,
            "axes.labelsize": 7.1,
            "axes.titlesize": 7.2,
            "xtick.labelsize": 6.4,
            "ytick.labelsize": 6.4,
            "legend.fontsize": 6.4,
            "axes.linewidth": 0.65,
            "xtick.major.width": 0.55,
            "ytick.major.width": 0.55,
            "xtick.major.size": 2.5,
            "ytick.major.size": 2.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.18,
            "grid.linewidth": 0.45,
            "mathtext.fontset": "stix",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save_figure(fig: plt.Figure, out_base: Path) -> None:
    out_base.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_base.with_suffix(".pdf"))
    fig.savefig(out_base.with_suffix(".png"))
