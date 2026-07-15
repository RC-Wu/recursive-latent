from __future__ import annotations

import math
import sys
from pathlib import Path
from textwrap import wrap

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, FancyArrowPatch, FancyBboxPatch, Circle, Polygon, Rectangle


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "assets"))

from paper_plot_style_recursive_growth import configure_paper_style, save_figure  # noqa: E402


OUT_BASE = ROOT / "paper_siga" / "figures" / "method_system_grammar_polished_20260508"

BG = "#FBFAF7"
INK = "#1F252B"
MUTED = "#5C6670"
LINE = "#2E3540"
HAIR = "#C9CED3"

COLORS = {
    "state": "#EAF1F7",
    "rules": "#F4ECF8",
    "loop": "#EEF5EF",
    "degen": "#F7F1E6",
    "evidence": "#EEF3F3",
    "accent": "#2F6F73",
    "blue": "#315F8C",
    "orange": "#B66A2A",
    "green": "#4B7F52",
    "pink": "#9B5F7B",
}


def add_text(ax, x, y, text, size=7.0, weight="normal", color=INK, ha="left", va="top", **kwargs):
    kwargs.setdefault("zorder", 8)
    return ax.text(
        x,
        y,
        text,
        fontsize=size,
        fontweight=weight,
        color=color,
        ha=ha,
        va=va,
        linespacing=1.18,
        **kwargs,
    )


def wrapped(ax, x, y, text, width, size=6.35, color=MUTED, leading=0.035, **kwargs):
    lines = []
    for part in text.split("\n"):
        lines.extend(wrap(part, width=width) if part else [""])
    for i, line in enumerate(lines):
        add_text(ax, x, y - i * leading, line, size=size, color=color, **kwargs)
    return y - len(lines) * leading


def box(ax, x, y, w, h, fc="white", ec=LINE, lw=0.9, radius=0.015, z=1):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.008,rounding_size={radius}",
        facecolor=fc,
        edgecolor=ec,
        linewidth=lw,
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def section(ax, x, y, w, h, title, subtitle, fc):
    box(ax, x, y, w, h, fc="#FFFFFF", ec=HAIR, lw=0.65, radius=0.016, z=0)
    ax.add_patch(
        Rectangle((x, y + h - 0.055), w, 0.055, facecolor=fc, edgecolor="none", zorder=1)
    )
    add_text(ax, x + 0.018, y + h - 0.017, title, size=7.4, weight="bold", va="top")
    if subtitle:
        add_text(ax, x + 0.018, y + h - 0.048, subtitle, size=5.6, color=MUTED, va="top")


def arrow(ax, xy1, xy2, color=LINE, lw=0.9, rad=0.0, ms=8):
    arr = FancyArrowPatch(
        xy1,
        xy2,
        arrowstyle="-|>",
        mutation_scale=ms,
        linewidth=lw,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=1.0,
        shrinkB=1.0,
        zorder=3,
    )
    ax.add_patch(arr)
    return arr


def mini_sparse_state(ax, x, y, w, h):
    ax.add_patch(Rectangle((x, y), w, h, facecolor="#F7FAFC", edgecolor=HAIR, linewidth=0.45))
    pts = [
        (0.16, 0.22, 0.012),
        (0.25, 0.36, 0.010),
        (0.35, 0.48, 0.012),
        (0.47, 0.56, 0.011),
        (0.58, 0.49, 0.012),
        (0.67, 0.39, 0.009),
        (0.73, 0.25, 0.010),
        (0.31, 0.18, 0.009),
        (0.50, 0.27, 0.010),
    ]
    for i, (px, py, r) in enumerate(pts):
        color = COLORS["blue"] if i % 3 else COLORS["accent"]
        ax.add_patch(Circle((x + px * w, y + py * h), r, facecolor=color, edgecolor="white", linewidth=0.35))
    for a, b in zip(pts[:-1], pts[1:]):
        ax.plot([x + a[0] * w, x + b[0] * w], [y + a[1] * h, y + b[1] * h], color="#8595A5", lw=0.5)
    add_text(ax, x + 0.02, y + h - 0.018, "C_d, F_d", size=5.6, weight="bold")


def mini_rules(ax, x, y, w, h):
    labels = [
        ("Tip -> Tip + Branch", COLORS["green"]),
        ("Portal -> T(Patch)", COLORS["blue"]),
        ("Frontier -> Hit cell", COLORS["orange"]),
    ]
    for i, (label, color) in enumerate(labels):
        yy = y + h - 0.035 - i * 0.052
        box(ax, x + 0.012 * i, yy - 0.028, w - 0.024, 0.036, fc="#FFFFFF", ec=color, lw=0.75, radius=0.008)
        add_text(ax, x + 0.014 + 0.012 * i, yy - 0.002, label, size=5.45, color=INK, va="center")


def mini_loop(ax, cx, cy, r):
    nodes = [
        ("Prop", 90, COLORS["pink"]),
        ("Comp", 18, COLORS["orange"]),
        ("N_theta", -54, COLORS["blue"]),
        ("D/P", -126, COLORS["green"]),
        ("E", 162, COLORS["accent"]),
    ]
    coords = []
    for label, deg, color in nodes:
        th = math.radians(deg)
        px, py = cx + r * math.cos(th), cy + r * math.sin(th)
        coords.append((px, py))
        box(ax, px - 0.034, py - 0.018, 0.068, 0.036, fc="#FFFFFF", ec=color, lw=0.8, radius=0.009, z=3)
        add_text(ax, px, py, label, size=5.3, ha="center", va="center", weight="bold")
    for a, b in zip(coords, coords[1:] + coords[:1]):
        arrow(ax, a, b, color="#66727C", lw=0.75, rad=0.18, ms=6)
    ax.add_patch(Circle((cx, cy), r * 0.45, facecolor="#F8FBF8", edgecolor=HAIR, linewidth=0.5))
    add_text(ax, cx, cy + 0.008, "S_{d+1}", size=5.8, weight="bold", ha="center", va="center")
    add_text(ax, cx, cy - 0.015, "inside recursion", size=4.8, color=MUTED, ha="center", va="center")


def mini_outputs(ax, x, y, w, h):
    ax.add_patch(Rectangle((x, y), w, h, facecolor="#F8FAFA", edgecolor=HAIR, linewidth=0.45))
    for i, height in enumerate([0.032, 0.052, 0.041, 0.066]):
        bx = x + 0.035 + i * 0.039
        ax.add_patch(Rectangle((bx, y + 0.024), 0.022, height, facecolor=COLORS["accent"], alpha=0.75, edgecolor="none"))
    ax.plot([x + 0.03, x + w - 0.025], [y + 0.105, y + 0.035], color=COLORS["orange"], lw=1.0)
    add_text(ax, x + 0.02, y + h - 0.018, "mesh / GLB / metrics", size=5.45, weight="bold")


def bullet(ax, x, y, title, text, accent=COLORS["accent"]):
    ax.add_patch(Circle((x, y - 0.006), 0.0045, facecolor=accent, edgecolor="none"))
    add_text(ax, x + 0.012, y, title, size=5.9, weight="bold")
    return wrapped(ax, x + 0.012, y - 0.026, text, width=30, size=5.35, leading=0.026)


def tag(ax, x, y, text, color=COLORS["accent"], w=None):
    if w is None:
        w = min(0.14, 0.012 + len(text) * 0.0058)
    box(ax, x, y - 0.019, w, 0.028, fc="#FFFFFF", ec=color, lw=0.65, radius=0.007, z=4)
    add_text(ax, x + 0.006, y - 0.005, text, size=4.8, color=INK, va="center")


def row(ax, x, y, key, val, key_color=COLORS["blue"], size=5.1):
    add_text(ax, x, y, key, size=size, weight="bold", color=key_color)
    add_text(ax, x + 0.12, y, val, size=size, color=MUTED)


def draw():
    configure_paper_style()
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
            "font.size": 5.8,
            "axes.grid": False,
            "figure.facecolor": BG,
            "savefig.facecolor": BG,
        }
    )
    fig, ax = plt.subplots(figsize=(13.8, 7.1))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor(BG)

    add_text(ax, 0.035, 0.958, "Projection-Stabilized Recursive Sparse-Latent Grammar", size=12.2, weight="bold")
    add_text(
        ax,
        0.036,
        0.925,
        "A formal grammar evolves typed sparse 3D latents; Trellis2 contributes local priors, decode/re-encode, projection feedback, and asset export.",
        size=6.3,
        color=MUTED,
    )

    cols = [
        (0.035, 0.57, 0.18, 0.285, "1. Typed sparse-latent state", "grammar-readable O-Voxel / SLAT state", COLORS["state"]),
        (0.232, 0.57, 0.18, 0.285, "2. Grammar rule proposals", "typed stochastic context rules", COLORS["rules"]),
        (0.43, 0.57, 0.25, 0.285, "3. Competition / projection loop", "proposal, sampler, decode, project, re-encode", COLORS["loop"]),
        (0.70, 0.57, 0.135, 0.285, "4. Classical limits", "procedural systems as degeneracies", COLORS["degen"]),
        (0.855, 0.57, 0.11, 0.285, "5. Outputs / evidence", "assets and diagnostics", COLORS["evidence"]),
    ]
    for c in cols:
        section(ax, *c)

    # Column 1: typed state.
    mini_sparse_state(ax, 0.056, 0.708, 0.13, 0.09)
    add_text(ax, 0.057, 0.676, "S_d = (C, F, U, A, B, M, H, K)", size=5.7, weight="bold")
    tag(ax, 0.057, 0.642, "sparse support C_d", COLORS["blue"], 0.115)
    tag(ax, 0.057, 0.606, "typed symbols U_d", COLORS["accent"], 0.112)
    tag(ax, 0.057, 0.570, "masks, history, caches", COLORS["green"], 0.132)

    # Column 2: rule proposals.
    mini_rules(ax, 0.252, 0.714, 0.13, 0.095)
    add_text(ax, 0.253, 0.666, "X(frame, region, level, attrs)", size=5.25, weight="bold")
    add_text(ax, 0.253, 0.632, "proposal kernels", size=4.85, color=MUTED, weight="bold")
    add_text(ax, 0.253, 0.603, "transform-copy   attractor", size=4.75, color=MUTED)
    add_text(ax, 0.253, 0.578, "frontier hit     masked sample", size=4.75, color=MUTED)

    # Column 3: loop.
    mini_loop(ax, 0.555, 0.725, 0.072)
    box(ax, 0.452, 0.591, 0.192, 0.052, fc="#FFFFFF", ec=HAIR, lw=0.55, radius=0.008)
    add_text(ax, 0.548, 0.626, "Prop -> Merge -> Comp -> N_theta", size=4.8, family="monospace", ha="center", va="center")
    add_text(ax, 0.548, 0.605, "Decode -> Project -> Encode", size=4.8, family="monospace", ha="center", va="center")
    add_text(ax, 0.653, 0.618, "inside\nrecursion", size=4.7, color=MUTED, ha="center", va="center")

    # Column 4: degeneracies.
    degeneracies = [
        ("IFS", "N_theta=P=Id"),
        ("L-system", "U_d string / turtle frames"),
        ("Space colonization", "tips compete for attractors"),
        ("DLA / frontier", "exposed boundary hits"),
        ("CGA / shape", "split, extrude, repeat"),
    ]
    yy = 0.795
    for name, desc in degeneracies:
        add_text(ax, 0.718, yy, name, size=5.2, weight="bold", color=COLORS["blue"])
        add_text(ax, 0.718, yy - 0.022, desc, size=4.55, color=MUTED)
        yy -= 0.043

    # Column 5: outputs.
    mini_outputs(ax, 0.872, 0.728, 0.073, 0.078)
    tag(ax, 0.872, 0.684, "mesh / GLB", COLORS["accent"], 0.074)
    tag(ax, 0.872, 0.648, "renders", COLORS["blue"], 0.06)
    tag(ax, 0.872, 0.612, "LCR / comps", COLORS["orange"], 0.085)
    tag(ax, 0.872, 0.576, "token curves", COLORS["green"], 0.088)

    # Main flow arrows.
    arrow(ax, (0.215, 0.715), (0.232, 0.715), color=LINE, ms=9)
    arrow(ax, (0.412, 0.715), (0.43, 0.715), color=LINE, ms=9)
    arrow(ax, (0.68, 0.715), (0.70, 0.715), color=LINE, ms=9)
    arrow(ax, (0.835, 0.715), (0.855, 0.715), color=LINE, ms=9)
    add_text(ax, 0.382, 0.548, "depth feedback: decode -> project -> re-encode -> next grammar step", size=5.0, color=MUTED, ha="center")

    # Bottom evidence panels.
    section(ax, 0.035, 0.305, 0.445, 0.17, "Classical systems are grammar degeneracies", "same operator family with disabled or restricted components", "#F6EFE4")
    left_rows = [
        ("Transform-copy", "contractive maps, symmetry orbits, portal and scale-down programs"),
        ("Symbol rewriting", "L-system strings/graphs interpreted as branch support and local frames"),
        ("Competition growth", "space-colonization attractors plus occupancy, collision, and frontier terms"),
    ]
    yy = 0.405
    for name, desc in left_rows:
        row(ax, 0.06, yy, name, desc, COLORS["blue"], size=5.0)
        yy -= 0.043

    section(ax, 0.52, 0.305, 0.445, 0.17, "Evidence slots in the current paper", "what the overview points to in results and ablations", "#EAF2F2")
    evid = [
        ("Projection ablation", "direct vs final-only vs per-depth projection"),
        ("Depth curves", "components, largest-component ratio, tokens, faces, vertices"),
        ("Asset exports", "mesh renders, GLB smoke tests, texture/PBR compatibility"),
    ]
    yy = 0.405
    for name, desc in evid:
        row(ax, 0.545, yy, name, desc, COLORS["accent"], size=5.0)
        yy -= 0.043

    # Equation band.
    box(ax, 0.035, 0.19, 0.93, 0.075, fc="#FFFFFF", ec=HAIR, lw=0.6, radius=0.012)
    add_text(ax, 0.055, 0.236, "Composed recursive operator", size=5.7, weight="bold", color=INK)
    add_text(
        ax,
        0.055,
        0.207,
        "S_{d+1} = C_{d+1} o E_theta o P_lambda o D_theta o N_theta o Theta_Pi o Merge_B o Prop_R(S_d)",
        size=5.7,
        family="monospace",
        color=INK,
    )
    add_text(
        ax,
        0.632,
        0.207,
        "P_lambda maintains a depth-wise admissible state; it is not final cleanup.",
        size=5.3,
        color=MUTED,
    )

    # Small side legend.
    legend_x, legend_y = 0.035, 0.125
    labels = [("grammar-owned structure", COLORS["pink"]), ("frozen generator prior", COLORS["blue"]), ("projection-stabilized state", COLORS["green"])]
    for i, (label, color) in enumerate(labels):
        x = legend_x + i * 0.19
        ax.add_patch(Circle((x, legend_y), 0.006, facecolor=color, edgecolor="none"))
        add_text(ax, x + 0.012, legend_y + 0.006, label, size=5.0, color=MUTED, va="center")

    # Decorative but semantic mini scaffold.
    base_x, base_y = 0.80, 0.112
    ax.plot([base_x, base_x + 0.12], [base_y, base_y + 0.045], color="#6F7D87", lw=0.8)
    ax.plot([base_x + 0.04, base_x + 0.07], [base_y + 0.015, base_y + 0.058], color="#6F7D87", lw=0.8)
    ax.plot([base_x + 0.075, base_x + 0.105], [base_y + 0.028, base_y + 0.075], color="#6F7D87", lw=0.8)
    for px, py, color in [
        (base_x, base_y, COLORS["accent"]),
        (base_x + 0.04, base_y + 0.015, COLORS["blue"]),
        (base_x + 0.07, base_y + 0.058, COLORS["orange"]),
        (base_x + 0.12, base_y + 0.045, COLORS["green"]),
        (base_x + 0.105, base_y + 0.075, COLORS["pink"]),
    ]:
        ax.add_patch(Circle((px, py), 0.008, facecolor=color, edgecolor="white", linewidth=0.4))
    add_text(ax, 0.91, 0.132, "finite-depth recursive asset", size=5.0, color=MUTED, ha="center")

    save_figure(fig, OUT_BASE)
    plt.close(fig)


if __name__ == "__main__":
    draw()
    print(f"saved {OUT_BASE.with_suffix('.png')}")
    print(f"saved {OUT_BASE.with_suffix('.pdf')}")
