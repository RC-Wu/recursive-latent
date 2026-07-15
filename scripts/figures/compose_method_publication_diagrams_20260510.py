from __future__ import annotations

import math
import shutil
from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, PathPatch, Rectangle
from matplotlib.path import Path as MplPath
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "paper_siga" / "figures"
OUT_DIR = FIG_DIR
QA_DIR = FIG_DIR / "method_diagram_drafts_20260510"

ASSETS = {
    "root": ROOT / "visuals/trellis2_mesh_first_reconstruct_20260507_1745/ifs_branch_tree_r512/input_normalized_preview.png",
    "ovoxel": ROOT / "visuals/trellis2_mesh_first_reconstruct_20260507_1745/ifs_branch_tree_r512/ovoxel_roundtrip_preview.png",
    "slat": ROOT / "visuals/trellis2_mesh_first_reconstruct_20260507_1745/ifs_branch_tree_r512/shape_slat_reconstruct_preview.png",
    "mesh_export": FIG_DIR / "texture_latest_occpos_paperstyle_contact_20260509.png",
    "pyrite": FIG_DIR / "pyrite_hq_depth_textured_showcase_20260509.png",
    "vine": FIG_DIR / "vine_depth_textured_showcase_20260509.png",
    "coral": FIG_DIR / "texture_latest_occpos_paperstyle_contact_20260509.png",
    "masked_raw": ROOT / "visuals/masked_naturalization_ablation_zoom_20260510/botanical_root__raw_grammar_proposal/zoom_01.png",
    "masked_projection": ROOT / "visuals/masked_naturalization_ablation_zoom_20260510/botanical_root__per_depth_projection/zoom_01.png",
    "masked_local": ROOT / "visuals/masked_naturalization_ablation_zoom_20260510/botanical_root__per_depth_masked_naturalization/zoom_01.png",
}

INK = "#1F2328"
MUTED = "#5C6670"
LIGHT = "#F5F7F8"
HAIR = "#D4DCE3"
BLUE = "#0072B2"
GREEN = "#009E73"
ORANGE = "#D55E00"
PURPLE = "#8C5AA9"
PINK = "#CC79A7"
GOLD = "#B8860B"
GRAY = "#7B858F"
RED = "#C85A4A"
WHITE = "#FFFFFF"


@dataclass(frozen=True)
class CropSpec:
    path: Path
    box: tuple[int, int, int, int] | None = None
    threshold: int = 246
    pad: int = 24
    max_size: tuple[int, int] = (900, 900)


def configure() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 160,
            "savefig.dpi": 360,
            "savefig.facecolor": WHITE,
            "figure.facecolor": WHITE,
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 7.6,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.grid": False,
            "text.usetex": False,
        }
    )


def ensure_assets() -> None:
    missing = [name for name, path in ASSETS.items() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing assets: " + ", ".join(f"{name}={ASSETS[name]}" for name in missing))


def text(ax, x, y, s, size=7.0, weight="normal", color=INK, ha="left", va="top", **kw):
    return ax.text(
        x,
        y,
        s,
        fontsize=size,
        fontweight=weight,
        color=color,
        ha=ha,
        va=va,
        linespacing=1.08,
        zorder=30,
        **kw,
    )


def rounded(ax, x, y, w, h, ec=HAIR, fc=WHITE, lw=0.8, radius=0.012, z=1):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.004,rounding_size={radius}",
        facecolor=fc,
        edgecolor=ec,
        linewidth=lw,
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def arrow(ax, xy1, xy2, color=INK, lw=0.9, rad=0.0, ms=8, z=20):
    patch = FancyArrowPatch(
        xy1,
        xy2,
        arrowstyle="-|>",
        mutation_scale=ms,
        linewidth=lw,
        color=color,
        shrinkA=2,
        shrinkB=2,
        connectionstyle=f"arc3,rad={rad}",
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def brace_arrow(ax, pts: list[tuple[float, float]], color=BLUE, lw=1.0, z=17):
    codes = [MplPath.MOVETO] + [MplPath.CURVE3] * (len(pts) - 1)
    path = MplPath(pts, codes)
    patch = FancyArrowPatch(
        path=path,
        arrowstyle="-|>",
        mutation_scale=9,
        linewidth=lw,
        color=color,
        shrinkA=0,
        shrinkB=0,
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def crop_image(spec: CropSpec) -> Image.Image:
    im = Image.open(spec.path).convert("RGBA")
    if spec.box is not None:
        im = im.crop(spec.box)
    rgb = np.asarray(im.convert("RGB"))
    alpha = np.asarray(im.getchannel("A"))
    non_bg = np.any(rgb < spec.threshold, axis=2) & (alpha > 8)
    if np.any(non_bg):
        ys, xs = np.where(non_bg)
        x0 = max(int(xs.min()) - spec.pad, 0)
        y0 = max(int(ys.min()) - spec.pad, 0)
        x1 = min(int(xs.max()) + spec.pad + 1, im.width)
        y1 = min(int(ys.max()) + spec.pad + 1, im.height)
        im = im.crop((x0, y0, x1, y1))
    return ImageOps.contain(im, spec.max_size, Image.Resampling.LANCZOS)


def add_image(ax, spec: CropSpec, x, y, w, h, z=12):
    im = crop_image(spec)
    arr = np.asarray(im)
    iw, ih = max(im.width, 1), max(im.height, 1)
    image_ar = iw / ih
    box_ar = w / h
    if image_ar >= box_ar:
        dw = w
        dh = w / image_ar
    else:
        dh = h
        dw = h * image_ar
    x0 = x + (w - dw) / 2
    y0 = y + (h - dh) / 2
    ax.imshow(arr, extent=(x0, x0 + dw, y0, y0 + dh), zorder=z, interpolation="lanczos", aspect="auto")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return None


def panel_label(ax, x, y, label, color):
    rounded(ax, x, y, 0.032, 0.028, ec=color, fc=WHITE, lw=0.9, radius=0.006, z=5)
    text(ax, x + 0.016, y + 0.014, label, size=7.0, weight="bold", color=color, ha="center", va="center")


def figure_heading(ax, title, subtitle, color=INK):
    text(ax, 0.035, 0.948, title, size=8.2, weight="bold", color=color)
    if subtitle:
        text(ax, 0.035, 0.908, subtitle, size=5.4, color=MUTED)


def node(ax, x, y, w, h, title, subtitle, color, mono=None, fc=WHITE):
    rounded(ax, x, y, w, h, ec=color, fc=fc, lw=1.0, radius=0.012, z=4)
    ax.add_patch(Rectangle((x + 0.010, y + h - 0.012), w - 0.020, 0.004, facecolor=color, edgecolor="none", zorder=5))
    text(ax, x + 0.014, y + h - 0.025, title, size=7.4, weight="bold", color=INK)
    if subtitle:
        text(ax, x + 0.014, y + h - 0.050, subtitle, size=5.1, color=MUTED)
    if mono:
        text(ax, x + 0.014, y + 0.018, mono, size=4.6, color=color, family="monospace", va="bottom")


def compact_node(ax, x, y, w, h, title, subtitle, color, mono=None, fc=WHITE):
    rounded(ax, x, y, w, h, ec=color, fc=fc, lw=1.0, radius=0.012, z=4)
    ax.add_patch(Rectangle((x + 0.010, y + h - 0.012), w - 0.020, 0.004, facecolor=color, edgecolor="none", zorder=5))
    text(ax, x + 0.014, y + h - 0.030, title, size=6.7, weight="bold", color=INK)
    if subtitle:
        text(ax, x + 0.014, y + h - 0.058, subtitle, size=4.7, color=MUTED)
    if mono:
        text(ax, x + 0.014, y + 0.018, mono, size=4.4, color=color, family="monospace", va="bottom")


def mini_tokens(ax, x, y, w, h, mode="support"):
    rng = np.random.default_rng(11 if mode == "support" else 17)
    pts = []
    if mode == "support":
        pts = [(0.12, 0.30), (0.25, 0.46), (0.40, 0.36), (0.54, 0.60), (0.68, 0.49), (0.84, 0.66)]
        for (a, b) in zip(pts[:-1], pts[1:]):
            ax.plot([x + a[0] * w, x + b[0] * w], [y + a[1] * h, y + b[1] * h], color="#A8B2BC", lw=0.55, zorder=9)
        for i, (px, py) in enumerate(pts):
            ax.add_patch(Circle((x + px * w, y + py * h), 0.0085, facecolor=BLUE if i % 2 else GREEN, edgecolor=WHITE, lw=0.4, zorder=10))
    else:
        for j in range(4):
            for i in range(7):
                c = "#E9EEF2"
                if rng.random() < 0.33:
                    c = GREEN
                if rng.random() < 0.08:
                    c = ORANGE
                ax.add_patch(Rectangle((x + i * w / 7, y + j * h / 4), 0.009, 0.009, facecolor=c, edgecolor="#C7D0D8", lw=0.2, zorder=10))


def sampler_mask(ax, x, y, w, h, show_label=True):
    rounded(ax, x, y, w, h, ec=PINK, fc="#FFF8FC", lw=0.8, radius=0.010, z=7)
    ax.add_patch(Rectangle((x + 0.020, y + 0.028), w * 0.42, h * 0.46, fill=False, edgecolor=PINK, linewidth=0.8, linestyle=(0, (3, 2)), zorder=11))
    for px, py in [(0.22, 0.35), (0.30, 0.44), (0.38, 0.30), (0.58, 0.48), (0.68, 0.40), (0.76, 0.54)]:
        ax.add_patch(Circle((x + px * w, y + py * h), 0.007, facecolor=PINK, edgecolor=WHITE, lw=0.3, zorder=12, alpha=0.78))
    for px, py in [(0.16, 0.70), (0.26, 0.73), (0.36, 0.68)]:
        ax.add_patch(Rectangle((x + px * w, y + py * h), 0.012, 0.012, facecolor=GREEN, edgecolor=WHITE, lw=0.3, zorder=12))
    if show_label:
        text(ax, x + 0.014, y + h - 0.022, "sampler", size=4.7, color=PINK, weight="bold")
    text(ax, x + 0.014, y + 0.015, "anchors clamped", size=4.2, color=MUTED)


def pipeline_node(ax, x, y, w, h, title, subtitle, color, fc=WHITE):
    rounded(ax, x, y, w, h, ec=color, fc=fc, lw=1.0, radius=0.012, z=4)
    ax.add_patch(Rectangle((x + 0.010, y + h - 0.012), w - 0.020, 0.004, facecolor=color, edgecolor="none", zorder=5))
    text(ax, x + 0.014, y + h - 0.034, title, size=6.9, weight="bold", color=INK)
    if subtitle:
        text(ax, x + 0.014, y + h - 0.066, subtitle, size=4.8, color=MUTED)


def projection_gate(ax, x, y, w, h, compact=False):
    rounded(ax, x, y, w, h, ec=ORANGE, fc="#FFF9F5", lw=1.15, radius=0.014, z=8)
    text(ax, x + 0.014, y + h - 0.023, "project to admissible state", size=6.6 if not compact else 5.6, weight="bold", color=ORANGE)
    items = ["root reachability", "deactivate/prune", "re-encode"]
    for i, item in enumerate(items):
        yy = y + h - 0.055 - i * (0.026 if not compact else 0.022)
        rounded(ax, x + 0.016, yy - 0.014, w - 0.032, 0.020 if not compact else 0.017, ec="#F1B37E", fc=WHITE, lw=0.55, radius=0.005, z=10)
        text(ax, x + 0.026, yy - 0.004, item, size=4.9 if not compact else 4.2, color=INK, va="center")


def support_scene(ax, x, y, w, h, projected=False):
    rounded(ax, x, y, w, h, ec=HAIR, fc=WHITE, lw=0.75, radius=0.010, z=4)
    trunk = [(0.18, 0.20), (0.27, 0.34), (0.36, 0.46), (0.48, 0.58), (0.61, 0.70)]
    branch = [(0.36, 0.46), (0.51, 0.45), (0.68, 0.54), (0.80, 0.62)]
    root_pts = trunk + branch[1:]
    for pts in (trunk, branch):
        for a, b in zip(pts[:-1], pts[1:]):
            ax.plot([x + a[0] * w, x + b[0] * w], [y + a[1] * h, y + b[1] * h], color="#9BA6AF", lw=0.75, zorder=8)
    for i, (px, py) in enumerate(root_pts):
        color = GREEN if i < len(trunk) else BLUE
        ax.add_patch(Circle((x + px * w, y + py * h), 0.010, facecolor=color, edgecolor=WHITE, lw=0.45, zorder=10))
    for px, py in [(0.61, 0.70), (0.80, 0.62)]:
        ax.add_patch(Rectangle((x + px * w - 0.011, y + py * h + 0.014), 0.022, 0.020, facecolor="#F6FFFB", edgecolor=GREEN, lw=0.65, zorder=11))
    if not projected:
        orphan = [(0.77, 0.23), (0.86, 0.31), (0.73, 0.36), (0.91, 0.43)]
        for a, b in zip(orphan[:-1], orphan[1:]):
            ax.plot([x + a[0] * w, x + b[0] * w], [y + a[1] * h, y + b[1] * h], color="#E8A09A", lw=0.7, zorder=8)
        for px, py in orphan:
            ax.add_patch(Circle((x + px * w, y + py * h), 0.010, facecolor=RED, edgecolor=WHITE, lw=0.45, zorder=10))
        ax.add_patch(Rectangle((x + 0.695 * w, y + 0.175 * h), 0.245 * w, 0.315 * h, fill=False, edgecolor=RED, linewidth=0.8, linestyle=(0, (3, 2)), zorder=12))
        text(ax, x + 0.705 * w, y + 0.160 * h, "orphan active support", size=4.5, color=RED, va="top")
    else:
        text(ax, x + 0.200 * w, y + 0.120 * h, "active support only", size=4.6, color=GREEN)
        text(ax, x + 0.590 * w, y + 0.850 * h, "surviving handles", size=4.4, color=GREEN, ha="center")


def draw_projection_admissibility() -> Path:
    configure()
    out = OUT_DIR / "method_projection_admissibility_gate_20260510"
    fig, ax = plt.subplots(figsize=(10.8, 3.9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    figure_heading(ax, "Projection as active-state selection", "Only the projected sparse state is visible to the next derivation depth.", ORANGE)

    # Transition rail.
    rail_y = 0.815
    rail_nodes = [
        (0.060, r"$z_d$", "active state", GREEN),
        (0.185, "rules", "proposal", GREEN),
        (0.305, r"$\mathrm{Dec}_\theta$", "candidate", GRAY),
        (0.580, r"$\Pi_{\lambda_d}$", "gate", ORANGE),
        (0.825, r"$\mathrm{Enc}_\theta$", "next state", BLUE),
    ]
    for i, (cx, title, sub, color) in enumerate(rail_nodes):
        rounded(ax, cx - 0.042, rail_y - 0.027, 0.084, 0.054, ec=color, fc=WHITE, lw=0.85, radius=0.007, z=5)
        text(ax, cx, rail_y + 0.008, title, size=6.3, weight="bold", color=color, ha="center", va="center")
        text(ax, cx, rail_y - 0.013, sub, size=4.5, color=MUTED, ha="center", va="center")
        if i < len(rail_nodes) - 1:
            arrow(ax, (cx + 0.046, rail_y), (rail_nodes[i + 1][0] - 0.046, rail_y), color=INK, lw=0.75, ms=7)

    # Candidate state.
    node(ax, 0.065, 0.455, 0.220, 0.245, "decoded candidate", "attached support plus orphans", GRAY)
    support_scene(ax, 0.090, 0.480, 0.170, 0.150, projected=False)
    text(ax, 0.095, 0.450, "Unprojected orphans would remain executable.", size=4.7, color=MUTED)

    # Gate.
    rounded(ax, 0.355, 0.400, 0.265, 0.315, ec=ORANGE, fc="#FFF9F5", lw=1.05, radius=0.016, z=3)
    text(ax, 0.375, 0.685, "admissibility gate", size=7.4, weight="bold", color=ORANGE)
    checks = [
        ("root reachability", "keep attached support"),
        ("orphan handles", "deactivate or prune"),
        ("budget / renderability", "reject invalid state"),
    ]
    for i, (title, sub) in enumerate(checks):
        yy = 0.625 - i * 0.070
        rounded(ax, 0.380, yy - 0.024, 0.215, 0.045, ec="#F1B37E", fc=WHITE, lw=0.60, radius=0.006, z=6)
        ax.add_patch(Circle((0.397, yy - 0.002), 0.008, facecolor=ORANGE, edgecolor=WHITE, lw=0.35, zorder=8))
        text(ax, 0.413, yy + 0.009, title, size=5.6, weight="bold", color=INK, va="center")
        text(ax, 0.413, yy - 0.011, sub, size=4.5, color=MUTED, va="center")
    text(ax, 0.488, 0.425, "conservative prune-only policy", size=4.8, color=ORANGE, ha="center")

    # Orphan branch.
    rounded(ax, 0.345, 0.165, 0.210, 0.115, ec=RED, fc="#FFF8F7", lw=0.85, radius=0.010, z=3)
    text(ax, 0.365, 0.250, "inactive descriptor / deleted", size=6.0, weight="bold", color=RED)
    text(ax, 0.365, 0.224, "cannot become a parent,\nfrontier, or cached motif", size=4.8, color=MUTED)
    arrow(ax, (0.450, 0.400), (0.450, 0.286), color=RED, lw=0.80, ms=7)

    # Optional connector branch.
    rounded(ax, 0.600, 0.165, 0.225, 0.115, ec=PINK, fc="#FFF8FC", lw=0.85, radius=0.010, z=3)
    text(ax, 0.620, 0.250, "optional connector mask", size=5.8, weight="bold", color=PINK)
    text(ax, 0.620, 0.224, "rule-proposed and certified;\nnot the default repair path", size=4.6, color=MUTED)
    arrow(ax, (0.570, 0.400), (0.690, 0.286), color=PINK, lw=0.75, ms=7, rad=0.08)

    # Projected next state.
    node(ax, 0.710, 0.455, 0.225, 0.245, "projected active state", r"projected $z_{d+1}$", BLUE)
    support_scene(ax, 0.735, 0.480, 0.170, 0.150, projected=True)
    text(ax, 0.820, 0.432, "later rules read this state only", size=4.3, color=MUTED, ha="center", va="bottom")

    arrow(ax, (0.285, 0.577), (0.355, 0.577), color=INK, lw=0.85, ms=8)
    arrow(ax, (0.620, 0.577), (0.710, 0.577), color=ORANGE, lw=0.85, ms=8)

    # Loop back to the next depth.
    ax.plot([0.820, 0.820, 0.110, 0.110], [0.455, 0.330, 0.330, 0.455], color=GREEN, lw=0.90, zorder=16)
    arrow(ax, (0.110, 0.455), (0.110, 0.505), color=GREEN, lw=0.90, ms=8)
    text(ax, 0.458, 0.314, r"next rule selection reads $z_{d+1}$", size=5.2, color=GREEN, ha="center", va="top")

    rounded(ax, 0.065, 0.065, 0.870, 0.050, ec=HAIR, fc=WHITE, lw=0.60, radius=0.008, z=2)
    text(
        ax,
        0.500,
        0.090,
        r"$z_{d+1}=\mathrm{Enc}_{\theta}\!\left(\Pi_{\theta,\lambda_d}\!\left(\mathrm{Dec}_{\theta}(\bar{z}_{d+1}),\mathcal{A}_d\right)\right)$",
        size=7.2,
        color=INK,
        ha="center",
        va="center",
    )

    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out.with_suffix(".png"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return out


def draw_substrate() -> Path:
    configure()
    ensure_assets()
    out = OUT_DIR / "method_trellis2_substrate_prelim_20260510"
    fig, ax = plt.subplots(figsize=(10.0, 3.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    figure_heading(ax, "Frozen Trellis2 sparse substrate", "Reusable sparse codec and local prior; grammar owns handles, scheduling, and projection.", BLUE)

    preview_box = (0, 100, 1020, 1020)
    steps = [
        ("condition", "root / guide", BLUE, CropSpec(ASSETS["root"], box=preview_box, max_size=(700, 700))),
        ("O-Voxel", r"$V_d$", BLUE, CropSpec(ASSETS["ovoxel"], box=preview_box, max_size=(700, 700))),
        ("Shape-SLAT", r"$F_d$", BLUE, CropSpec(ASSETS["slat"], box=preview_box, max_size=(700, 700))),
        ("local prior", r"$\mathcal{N}_\theta(z;m)$", PINK, None),
        ("codec", r"$\mathrm{Dec}_\theta / \mathrm{Enc}_\theta$", GRAY, CropSpec(ASSETS["vine"], box=(0, 90, 805, 854), threshold=120, pad=4, max_size=(800, 760))),
        ("asset export", "optional GLB/PBR", GOLD, CropSpec(ASSETS["mesh_export"], box=(770, 585, 1458, 1225), threshold=248, pad=6, max_size=(820, 720))),
    ]
    x0, y0, bw, bh, gap = 0.050, 0.405, 0.122, 0.325, 0.032
    centers = []
    for i, (title, sub, color, spec) in enumerate(steps):
        x = x0 + i * (bw + gap)
        centers.append((x + bw / 2, y0 + bh / 2))
        pipeline_node(ax, x, y0, bw, bh, title, sub, color, fc=WHITE)
        if spec is not None:
            add_image(ax, spec, x + 0.018, y0 + 0.035, bw - 0.036, bh - 0.112, z=13)
        else:
            sampler_mask(ax, x + 0.018, y0 + 0.050, bw - 0.036, bh - 0.130, show_label=False)
        if i < len(steps) - 1:
            arrow(ax, (x + bw + 0.006, y0 + bh / 2), (x + bw + gap - 0.006, y0 + bh / 2), color=INK, lw=0.9, ms=8)

    # Grammar boundary and projection outside Trellis2.
    rounded(ax, 0.305, 0.160, 0.390, 0.090, ec=GREEN, fc=WHITE, lw=0.85, radius=0.012, z=2)
    text(ax, 0.500, 0.222, "grammar-visible interface", size=6.3, weight="bold", color=GREEN, ha="center")
    text(ax, 0.500, 0.193, r"handles + masks + sparse proposals; projection is outside the frozen generator", size=5.35, color=MUTED, ha="center")
    brace_arrow(ax, [(0.498, 0.405), (0.452, 0.315), (0.372, 0.253)], color=GREEN, lw=0.90)
    brace_arrow(ax, [(0.648, 0.405), (0.622, 0.315), (0.612, 0.253)], color=GREEN, lw=0.90)

    # Re-entry loop.
    ax.plot([0.710, 0.205], [0.315, 0.315], color=BLUE, lw=0.90, zorder=12)
    arrow(ax, (0.205, 0.315), (0.205, 0.397), color=BLUE, lw=0.90, ms=8)
    text(ax, 0.457, 0.328, "re-encode and re-enter", size=5.3, color=BLUE, ha="center", va="bottom")

    # Small claim boundary.
    text(ax, 0.050, 0.082, "Interface figure only: the frozen substrate does not enforce recursion, handle validity, or topology preservation.", size=5.3, color=MUTED)

    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out.with_suffix(".png"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return out


def draw_overview() -> Path:
    configure()
    ensure_assets()
    out = OUT_DIR / "method_ps_rslg_overview_publication_20260510"
    fig, ax = plt.subplots(figsize=(11.0, 4.45))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    figure_heading(ax, "PS-RSLG over a frozen sparse substrate", "Rules own recursive state; the frozen generator realizes masked local edits and re-encodes projected states.", GREEN)

    # Frozen substrate strip.
    rounded(ax, 0.055, 0.735, 0.870, 0.118, ec=BLUE, fc=WHITE, lw=0.90, radius=0.010, z=1)
    text(ax, 0.074, 0.832, "(a) frozen Trellis2 substrate", size=7.0, weight="bold", color=BLUE)
    strip_nodes = [
        (0.245, r"$\mathrm{Enc}_\theta$", r"$x_d \mapsto z_d$"),
        (0.365, "O-Voxel", r"$V_d$"),
        (0.485, "Shape-SLAT", r"$F_d$"),
        (0.615, r"$\mathrm{Dec}_\theta/\mathrm{Enc}_\theta$", "round trip"),
        (0.755, "GLB/PBR", "optional export"),
    ]
    for i, (cx, t, s) in enumerate(strip_nodes):
        color = BLUE if i < 3 else GRAY if i == 3 else GOLD
        rounded(ax, cx - 0.052, 0.772, 0.104, 0.043, ec=color, fc=WHITE, lw=0.75, radius=0.006, z=4)
        text(ax, cx, 0.800, t, size=5.35, weight="bold", color=color, ha="center", va="center")
        text(ax, cx, 0.781, s, size=4.35, color=MUTED, ha="center", va="center")
        if i < len(strip_nodes) - 1:
            arrow(ax, (cx + 0.058, 0.793), (strip_nodes[i + 1][0] - 0.058, 0.793), color="#57606A", lw=0.75, ms=7)

    add_image(ax, CropSpec(ASSETS["ovoxel"], box=(0, 100, 1020, 1020), max_size=(640, 640)), 0.078, 0.770, 0.070, 0.065, z=13)

    # Main grammar loop background.
    rounded(ax, 0.075, 0.205, 0.675, 0.440, ec=GREEN, fc=WHITE, lw=1.0, radius=0.014, z=1)
    text(ax, 0.096, 0.620, "(b) grammar-owned recursive transition", size=7.5, weight="bold", color=GREEN)
    text(ax, 0.096, 0.590, r"state $z_d=(V_d,F_d,\mathcal{A}_d)$ is read only after projection", size=5.2, color=GREEN)

    # Loop nodes.
    y = 0.442
    loop = [
        (0.115, 0.105, "handles", r"$\mathcal{A}_d$", GREEN, "support"),
        (0.265, 0.112, "rules", r"$\mathcal{R}_d$", GREEN, "rules"),
        (0.420, 0.120, "local prior", r"$\mathcal{N}_\theta$", PINK, "mask_icon"),
        (0.590, 0.118, "decode", r"$\bar{x}_{d+1}$", GRAY, "decode"),
    ]
    prev_right = None
    for x, w, title, sub, color, icon in loop:
        node(ax, x, y, w, 0.115, title, sub, color)
        if icon == "support":
            mini_tokens(ax, x + 0.022, y + 0.032, w - 0.044, 0.034, mode="support")
        elif icon == "rules":
            colors = [GREEN, BLUE, PURPLE, GOLD]
            for j, c in enumerate(colors):
                ax.add_patch(Rectangle((x + 0.024 + j * 0.018, y + 0.042), 0.012, 0.030, facecolor=c, edgecolor=WHITE, lw=0.35, zorder=11))
            text(ax, x + w / 2, y + 0.026, "typed rule bank", size=4.45, color=MUTED, ha="center", va="bottom")
        elif icon == "mask_icon":
            ax.add_patch(Rectangle((x + 0.030, y + 0.030), w * 0.28, 0.034, fill=False, edgecolor=PINK, linewidth=0.75, linestyle=(0, (3, 2)), zorder=11))
            mini_tokens(ax, x + 0.062, y + 0.033, w - 0.078, 0.033, mode="proposal")
            text(ax, x + w / 2, y + 0.023, "mask + anchors", size=4.35, color=MUTED, ha="center", va="bottom")
        elif icon == "decode":
            mini_tokens(ax, x + 0.022, y + 0.032, w - 0.044, 0.040, mode="proposal")
        if prev_right is not None:
            arrow(ax, (prev_right, y + 0.057), (x - 0.010, y + 0.057), color=INK, lw=0.85, ms=8)
        prev_right = x + w

    projection_gate(ax, 0.535, 0.285, 0.165, 0.112, compact=True)
    arrow(ax, (0.650, y), (0.617, 0.405), color=ORANGE, lw=0.9, ms=8, rad=0.12)
    node(ax, 0.292, 0.300, 0.150, 0.086, "next state", r"$z_{d+1}$", BLUE)
    arrow(ax, (0.535, 0.340), (0.450, 0.340), color=ORANGE, lw=0.9, ms=8)
    ax.plot([0.367, 0.145], [0.292, 0.292], color=GREEN, lw=0.95, zorder=16)
    arrow(ax, (0.145, 0.292), (0.145, 0.420), color=GREEN, lw=0.95, ms=8)
    text(ax, 0.258, 0.274, "next rules read projected state", size=5.2, color=GREEN, ha="center")

    # Formula.
    rounded(ax, 0.190, 0.151, 0.430, 0.047, ec=HAIR, fc=WHITE, lw=0.60, radius=0.007, z=3)
    text(
        ax,
        0.405,
        0.175,
        r"$z_{d+1}=\mathrm{Enc}_{\theta}\!\left[\Pi_{\theta,\lambda_d}\!\left(\mathrm{Dec}_{\theta}(\bar z_{d+1}),\mathcal{A}_d\right)\right]$",
        size=6.4,
        color=INK,
        ha="center",
        va="center",
    )

    # Connections to frozen substrate.
    arrow(ax, (0.405, 0.735), (0.405, 0.645), color=BLUE, lw=0.85, ms=8)
    text(ax, 0.414, 0.694, r"read $z_d$", size=5.0, color=BLUE)
    arrow(ax, (0.642, 0.442), (0.615, 0.735), color=BLUE, lw=0.85, ms=8, rad=-0.08)
    text(ax, 0.662, 0.650, "codec path", size=5.0, color=BLUE, ha="left", va="center")

    # Evidence panel.
    rounded(ax, 0.785, 0.250, 0.150, 0.335, ec=GOLD, fc=WHITE, lw=0.85, radius=0.012, z=1)
    text(ax, 0.802, 0.560, "(c) selected asset view", size=6.2, weight="bold", color=GOLD)
    add_image(ax, CropSpec(ASSETS["mesh_export"], box=(770, 585, 1458, 1225), threshold=248, pad=6, max_size=(820, 720)), 0.805, 0.365, 0.110, 0.135, z=13)
    text(ax, 0.860, 0.335, "finite-depth\nvisual anchor", size=5.2, weight="bold", color=INK, ha="center")
    text(ax, 0.860, 0.292, "metrics and matched\nablations carry claims", size=4.5, color=MUTED, ha="center")

    text(ax, 0.115, 0.105, "Projection is execution semantics, not final mesh cleanup.", size=5.55, color=ORANGE)

    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out.with_suffix(".png"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return out


def draw_masked_naturalization_mechanism() -> Path:
    configure()
    ensure_assets()
    out = OUT_DIR / "method_masked_local_naturalization_mechanism_20260510"
    fig, ax = plt.subplots(figsize=(10.2, 3.15))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    figure_heading(ax, "Masked Local Naturalization", "The grammar fixes anchors and the edit mask; the frozen prior realizes only the masked region before projection.", PINK)

    # Main mechanism strip.
    y, h = 0.535, 0.255
    xs = [0.060, 0.315, 0.570, 0.800]
    ws = [0.170, 0.190, 0.170, 0.145]
    labels = [
        ("rule scaffold", "anchors + editable mask", GREEN),
        ("masked prior", r"$m_d$-local sampling", PINK),
        ("project", "attached active state", ORANGE),
        ("re-encode", r"$z_{d+1}$", BLUE),
    ]
    for i, (x, w) in enumerate(zip(xs, ws)):
        title, sub, color = labels[i]
        compact_node(ax, x, y, w, h, title, sub, color)
        if i == 0:
            # Root scaffold with clamped anchors and an editable mask.
            for px, py in [(0.18, 0.30), (0.30, 0.42), (0.43, 0.48), (0.56, 0.54), (0.68, 0.58), (0.80, 0.60)]:
                ax.add_patch(Rectangle((x + px * w, y + py * h), 0.012, 0.012, facecolor=GREEN, edgecolor=WHITE, lw=0.25, zorder=12))
            for px, py in [(0.15, 0.28), (0.25, 0.40)]:
                ax.add_patch(Circle((x + px * w, y + py * h), 0.009, facecolor=BLUE, edgecolor=WHITE, lw=0.35, zorder=13))
            ax.add_patch(Rectangle((x + 0.36 * w, y + 0.30 * h), 0.48 * w, 0.38 * h, fill=False, edgecolor=PINK, linewidth=0.9, linestyle=(0, (3, 2)), zorder=14))
            text(ax, x + 0.60 * w, y + 0.250 * h, "editable", size=4.3, color=PINK, ha="center")
        elif i == 1:
            sampler_mask(ax, x + 0.032, y + 0.052, w - 0.064, h - 0.142, show_label=False)
        elif i == 2:
            support_scene(ax, x + 0.022, y + 0.040, w - 0.044, h - 0.112, projected=True)
        else:
            mini_tokens(ax, x + 0.025, y + 0.060, w - 0.050, h - 0.130, mode="support")
        if i < len(xs) - 1:
            arrow(ax, (x + w + 0.010, y + h * 0.52), (xs[i + 1] - 0.010, y + h * 0.52), color=INK, lw=0.85, ms=8)

    # Anchor clamp rail.
    ax.plot([0.085, 0.405], [0.485, 0.485], color=BLUE, lw=0.85, zorder=10)
    arrow(ax, (0.405, 0.485), (0.405, 0.535), color=BLUE, lw=0.85, ms=7)
    text(ax, 0.245, 0.469, "anchor tokens remain clamped", size=5.25, color=BLUE, ha="center")

    # Compact equation and claim boundary.
    rounded(ax, 0.188, 0.368, 0.620, 0.056, ec=HAIR, fc=WHITE, lw=0.60, radius=0.007, z=3)
    text(ax, 0.498, 0.396, r"$u_{t-\Delta t}=(1-m_d)\odot z_{\rm anchor}+m_d\odot\Phi_{\theta,t}(u_t,y)$", size=7.0, color=INK, ha="center", va="center")
    text(ax, 0.500, 0.330, r"$m_d$ is the sparse editable mask. Local realization only: topology and active handles remain grammar/projection decisions.", size=5.55, color=ORANGE, ha="center")

    # Claim-boundary cards. These replace the older evidence strip so the figure
    # stays a method mechanism rather than a result claim.
    cards = [
        (0.105, "mask fixed by grammar", "feasibility clips editable support", GREEN),
        (0.365, "sampler inside mask", "surface/material continuity only", PINK),
        (0.625, "projection owns state", "selects active next handles", ORANGE),
    ]
    for x, title, body, color in cards:
        rounded(ax, x, 0.145, 0.220, 0.115, ec=color, fc=WHITE, lw=0.80, radius=0.009, z=4)
        ax.add_patch(Rectangle((x + 0.012, 0.238), 0.028, 0.005, facecolor=color, edgecolor="none", zorder=6))
        text(ax, x + 0.052, 0.232, title, size=5.55, weight="bold", color=color)
        text(ax, x + 0.052, 0.201, body, size=4.75, color=MUTED)

    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out.with_suffix(".png"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return out


def make_contact(outputs: list[Path]) -> Path:
    imgs = [Image.open(path.with_suffix(".png")).convert("RGB") for path in outputs]
    labels = [path.name for path in outputs]
    thumbs = []
    for im in imgs:
        thumbs.append(ImageOps.contain(im, (1600, 650), Image.Resampling.LANCZOS))
    width = max(t.width for t in thumbs)
    height = sum(t.height + 58 for t in thumbs) + 20
    sheet = Image.new("RGB", (width + 60, height), WHITE)
    y = 20
    for label, im in zip(labels, thumbs):
        sheet.paste(im, (30, y))
        y += im.height + 6
        # Simple label.
        import PIL.ImageDraw as ImageDraw
        import PIL.ImageFont as ImageFont

        draw = ImageDraw.Draw(sheet)
        try:
            font = ImageFont.truetype("Arial.ttf", 20)
        except OSError:
            font = ImageFont.load_default()
        draw.text((30, y), label, fill=INK, font=font)
        y += 52
    out = QA_DIR / "method_publication_abc_contact_sheet_20260510.png"
    QA_DIR.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def copy_to_drafts(outputs: list[Path]) -> None:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    for path in outputs:
        for ext in (".pdf", ".png", ".svg"):
            src = path.with_suffix(ext)
            if src.exists():
                shutil.copy2(src, QA_DIR / src.name)


def main() -> None:
    outputs = [draw_substrate(), draw_overview(), draw_projection_admissibility(), draw_masked_naturalization_mechanism()]
    copy_to_drafts(outputs)
    contact = make_contact(outputs)
    print("Generated:")
    for path in outputs:
        print(path.with_suffix(".pdf"))
        print(path.with_suffix(".png"))
        print(path.with_suffix(".svg"))
    print(contact)


if __name__ == "__main__":
    main()
