from __future__ import annotations

import math
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[2]
OUT_BASE = ROOT / "paper_siga" / "figures" / "method_system_ps_rslg_tog_draft_20260509"

PROJ_RENDER_DIR = (
    ROOT
    / "visuals"
    / "projection_ablation_blender_mesh_20260509"
    / "renders_pure_white_flat_rerun2105"
)
HQ_RENDER_DIR = (
    ROOT
    / "visuals"
    / "connected_scaffold_v2_textured_glb_hq_20260509"
    / "renders_pure_white_flat_rerun2115"
)

# Replace these paths with final camera-matched mesh renders if stronger cases are selected.
THUMBNAILS = {
    "root": PROJ_RENDER_DIR / "vine_per_depth_iso.png",
    "direct": PROJ_RENDER_DIR / "vine_direct_iso.png",
    "projected": PROJ_RENDER_DIR / "vine_per_depth_iso.png",
    "asset_a": HQ_RENDER_DIR / "bismuth_hopper_iso.png",
    "asset_b": HQ_RENDER_DIR / "pyrite_lattice_iso.png",
    "asset_c": HQ_RENDER_DIR / "volumetric_coral_octopus_iso.png",
}

INK = "#20252B"
MUTED = "#56616D"
HAIR = "#D4DAE0"
LIGHT = "#EDF2F6"
BLUE = "#0072B2"
GREEN = "#009E73"
ORANGE = "#D55E00"
PURPLE = "#7A5195"
GRAY = "#7B858F"
WHITE = "#FFFFFF"


def configure() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 160,
            "savefig.dpi": 320,
            "savefig.facecolor": WHITE,
            "figure.facecolor": WHITE,
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 7.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.grid": False,
        }
    )


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
        zorder=20,
        **kw,
    )


def rounded(ax, x, y, w, h, ec=HAIR, fc=WHITE, lw=0.75, radius=0.018, z=1):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.006,rounding_size={radius}",
        facecolor=fc,
        edgecolor=ec,
        linewidth=lw,
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def arrow(ax, xy1, xy2, color=INK, lw=0.9, rad=0.0, ms=8, z=9):
    patch = FancyArrowPatch(
        xy1,
        xy2,
        arrowstyle="-|>",
        mutation_scale=ms,
        linewidth=lw,
        color=color,
        shrinkA=2.0,
        shrinkB=2.0,
        connectionstyle=f"arc3,rad={rad}",
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def crop_to_content(path: Path, pad: int = 40) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    rgb = np.asarray(im.convert("RGB"))
    alpha = np.asarray(im.getchannel("A"))
    nonwhite = np.any(rgb < 246, axis=2) & (alpha > 5)
    if not np.any(nonwhite):
        return im
    ys, xs = np.where(nonwhite)
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, im.width)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, im.height)
    cropped = im.crop((x0, y0, x1, y1))
    return ImageOps.contain(cropped, (900, 900))


def add_thumb(ax, path: Path, x, y, w, h, zoom=0.16):
    im = crop_to_content(path)
    arr = np.asarray(im)
    oi = OffsetImage(arr, zoom=zoom)
    ab = AnnotationBbox(oi, (x + w / 2, y + h / 2), frameon=False, box_alignment=(0.5, 0.5), zorder=12)
    ax.add_artist(ab)


def node(ax, x, y, w, h, title, subtitle, color, mono=None):
    rounded(ax, x, y, w, h, ec=color, fc=WHITE, lw=1.05, radius=0.016, z=3)
    ax.add_patch(Rectangle((x + 0.012, y + h - 0.016), w - 0.024, 0.006, facecolor=color, edgecolor="none", zorder=4))
    text(ax, x + 0.016, y + h - 0.031, title, size=7.5, weight="bold")
    if subtitle:
        text(ax, x + 0.016, y + h - 0.058, subtitle, size=5.2, color=MUTED)
    if mono:
        text(ax, x + 0.016, y + 0.024, mono, size=5.2, color=color, family="monospace", va="bottom")


def sparse_icon(ax, x, y, w, h):
    pts = [(0.10, 0.25), (0.24, 0.57), (0.41, 0.34), (0.58, 0.67), (0.76, 0.40), (0.88, 0.72)]
    for a, b in zip(pts[:-1], pts[1:]):
        ax.plot([x + a[0] * w, x + b[0] * w], [y + a[1] * h, y + b[1] * h], color="#9AA6B2", lw=0.7, zorder=7)
    for i, (px, py) in enumerate(pts):
        ax.add_patch(
            Circle(
                (x + px * w, y + py * h),
                0.012,
                facecolor=BLUE if i % 2 else GREEN,
                edgecolor=WHITE,
                linewidth=0.6,
                zorder=8,
            )
        )


def rule_icon(ax, x, y, w, h):
    labels = [("grow", GREEN), ("attach", GREEN), ("copy", PURPLE)]
    for i, (label, color) in enumerate(labels):
        yy = y + h - 0.018 - i * 0.028
        rounded(ax, x, yy - 0.014, w, 0.021, ec=color, fc=WHITE, lw=0.65, radius=0.006, z=7)
        text(ax, x + w / 2, yy - 0.004, label, size=5.5, ha="center", va="center")


def sampler_icon(ax, x, y, w, h):
    rng = np.random.default_rng(7)
    cols, rows = 6, 4
    cell = min(w / cols, h / rows) * 0.68
    for j in range(rows):
        for i in range(cols):
            fc = GREEN if rng.random() < 0.27 else "#ECF1F3"
            ax.add_patch(
                Rectangle(
                    (x + i * w / cols, y + j * h / rows),
                    cell,
                    cell,
                    facecolor=fc,
                    edgecolor="#C9D1D8",
                    linewidth=0.25,
                    zorder=7,
                )
            )


def decode_icon(ax, x, y, w, h):
    p = np.array([[0.15, 0.28], [0.48, 0.78], [0.86, 0.34], [0.46, 0.13]]) * [w, h] + [x, y]
    ax.plot([p[0, 0], p[1, 0], p[2, 0], p[3, 0], p[0, 0]], [p[0, 1], p[1, 1], p[2, 1], p[3, 1], p[0, 1]], color=BLUE, lw=0.85, zorder=7)
    ax.plot([p[0, 0], p[2, 0]], [p[0, 1], p[2, 1]], color="#9AA6B2", lw=0.55, zorder=7)
    ax.plot([p[1, 0], p[3, 0]], [p[1, 1], p[3, 1]], color="#9AA6B2", lw=0.55, zorder=7)


def projection_icon(ax, x, y, w, h):
    ax.add_patch(Circle((x + 0.16 * w, y + 0.58 * h), 0.019, facecolor=BLUE, edgecolor=WHITE, lw=0.4, zorder=8))
    ax.add_patch(Circle((x + 0.28 * w, y + 0.28 * h), 0.012, facecolor=BLUE, edgecolor=WHITE, lw=0.4, zorder=8))
    ax.plot([x + 0.16 * w, x + 0.28 * w], [y + 0.58 * h, y + 0.28 * h], color="#8C98A4", lw=0.7, zorder=7)
    text(ax, x + 0.44 * w, y + 0.44 * h, "x", size=16, weight="bold", color=ORANGE, ha="center", va="center")
    arrow(ax, (x + 0.54 * w, y + 0.45 * h), (x + 0.66 * w, y + 0.45 * h), color=ORANGE, lw=0.9, ms=7)
    for px, py in [(0.79, 0.62), (0.70, 0.35), (0.92, 0.56)]:
        ax.add_patch(Circle((x + px * w, y + py * h), 0.017, facecolor=GREEN, edgecolor=WHITE, lw=0.4, zorder=8))
    ax.plot([x + 0.70 * w, x + 0.79 * w, x + 0.92 * w], [y + 0.35 * h, y + 0.62 * h, y + 0.56 * h], color="#8C98A4", lw=0.7, zorder=7)


def draw() -> None:
    configure()
    fig, ax = plt.subplots(figsize=(14.2, 5.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor(WHITE)

    text(ax, 0.034, 0.958, "Projection-Stabilized Recursive Sparse-Latent Grammar", size=13.6, weight="bold")
    text(
        ax,
        0.034,
        0.918,
        "Grammar controls recursive topology; the frozen 3D generator supplies masked local realization, codec, and export.",
        size=7.1,
        color=MUTED,
    )

    rounded(ax, 0.03, 0.21, 0.94, 0.64, ec="#BCC7D0", fc=WHITE, lw=0.85, radius=0.018, z=0)
    ax.add_patch(Rectangle((0.052, 0.797), 0.825, 0.018, facecolor=LIGHT, edgecolor="none", zorder=1))
    text(ax, 0.055, 0.805, "per-depth transition  d -> d+1", size=7.8, weight="bold", va="center")
    text(ax, 0.842, 0.805, "export at selected finite depth", size=7.3, color=MUTED, ha="right", va="center")

    # Root condition.
    rounded(ax, 0.055, 0.36, 0.13, 0.35, ec=HAIR, fc=WHITE, lw=0.75, radius=0.014, z=2)
    text(ax, 0.067, 0.682, "root condition", size=8.0, weight="bold")
    add_thumb(ax, THUMBNAILS["root"], 0.07, 0.43, 0.10, 0.16, zoom=0.105)
    text(ax, 0.067, 0.405, "x0, y", size=6.0, color=BLUE, family="monospace")
    text(ax, 0.067, 0.375, "mesh / image / text", size=5.3, color=MUTED)

    # Main nodes.
    xs = [0.22, 0.345, 0.485, 0.625, 0.745]
    y, w, h = 0.56, 0.105, 0.145
    node(ax, xs[0], y, w, h, "sparse state", "", BLUE, "z_d, F_d, A_d")
    sparse_icon(ax, xs[0] + 0.024, y + 0.055, 0.060, 0.045)
    node(ax, xs[1], y, w, h, "grammar", "", GREEN)
    rule_icon(ax, xs[1] + 0.022, y + 0.030, 0.062, 0.074)
    node(ax, xs[2], y, w, h, "masked prior", "", GREEN)
    sampler_icon(ax, xs[2] + 0.022, y + 0.045, 0.062, 0.050)
    node(ax, xs[3], y, 0.085, h, "decode", "", GRAY)
    decode_icon(ax, xs[3] + 0.025, y + 0.035, 0.045, 0.060)
    node(ax, xs[4], y - 0.005, 0.125, h + 0.010, "projection", "inside every recursion step", ORANGE, "Pi_lambda")
    projection_icon(ax, xs[4] + 0.017, y + 0.023, 0.088, 0.070)

    for x1, x2 in [(0.185, xs[0]), (xs[0] + w, xs[1]), (xs[1] + w, xs[2]), (xs[2] + w, xs[3]), (xs[3] + 0.085, xs[4])]:
        arrow(ax, (x1, y + h / 2), (x2, y + h / 2), lw=0.95, ms=9)

    # Re-encode and feedback loop.
    node(ax, 0.590, 0.315, 0.165, 0.105, "re-encode", "sparse tokens, anchors", BLUE, "z_{d+1}")
    node(ax, 0.365, 0.315, 0.155, 0.105, "update memory", "valid frontiers and caches", GREEN)
    arrow(ax, (0.805, 0.555), (0.672, 0.420), color=ORANGE, lw=1.0, rad=-0.10, ms=9)
    arrow(ax, (0.590, 0.368), (0.520, 0.368), color=INK, lw=0.9, ms=8)
    arrow(ax, (0.365, 0.368), (0.270, 0.560), color=INK, lw=0.9, rad=-0.36, ms=8)
    text(ax, 0.438, 0.258, "projection prevents invalid fragments from becoming next-depth handles", size=6.4, color=MUTED, ha="center")

    # Output thumbnails.
    rounded(ax, 0.895, 0.36, 0.055, 0.35, ec=HAIR, fc=WHITE, lw=0.75, radius=0.014, z=2)
    text(ax, 0.923, 0.682, "assets", size=8.0, weight="bold", ha="center")
    for i, key in enumerate(["asset_a", "asset_b", "asset_c"]):
        add_thumb(ax, THUMBNAILS[key], 0.904, 0.565 - i * 0.082, 0.037, 0.055, zoom=0.044)
    text(ax, 0.923, 0.375, "GLB + PBR", size=5.8, color=BLUE, ha="center")
    arrow(ax, (0.870, y + h / 2), (0.895, y + h / 2), lw=0.95, ms=9)

    # Compact equation and legend.
    rounded(ax, 0.235, 0.165, 0.55, 0.035, ec=HAIR, fc=WHITE, lw=0.55, radius=0.008, z=2)
    text(
        ax,
        0.510,
        0.183,
        "z(d+1) = Enc[ Pi_lambda( Dec( masked_sample( rules(z(d), y) ) ) ) ]",
        size=5.4,
        family="monospace",
        color=INK,
        ha="center",
        va="center",
    )

    legend = [("grammar", GREEN), ("sparse codec", BLUE), ("projection", ORANGE), ("frozen prior", GRAY)]
    lx = 0.055
    for label, color in legend:
        ax.add_patch(Circle((lx, 0.125), 0.006, facecolor=color, edgecolor="none", zorder=10))
        text(ax, lx + 0.012, 0.126, label, size=6.1, color=MUTED, va="center")
        lx += 0.118

    OUT_BASE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_BASE.with_suffix(".png"), bbox_inches="tight", pad_inches=0.02, facecolor=WHITE)
    fig.savefig(OUT_BASE.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02, facecolor=WHITE)
    plt.close(fig)


if __name__ == "__main__":
    missing = [str(p) for p in THUMBNAILS.values() if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing thumbnail renders:\n" + "\n".join(missing))
    draw()
    print(OUT_BASE.with_suffix(".png"))
    print(OUT_BASE.with_suffix(".pdf"))
