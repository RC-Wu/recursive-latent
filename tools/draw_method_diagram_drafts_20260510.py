from pathlib import Path
import math

import matplotlib as mpl
mpl.use("Agg")
mpl.rcParams["svg.fonttype"] = "none"
mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["font.family"] = "DejaVu Sans"

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Polygon
from PIL import Image, ImageOps, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
OUT = ROOT / "paper_siga/figures/method_diagram_drafts_20260510"
OUT.mkdir(parents=True, exist_ok=True)


COL = {
    "blue": "#0072B2",
    "green": "#009E73",
    "orange": "#D55E00",
    "gray": "#7B858F",
    "lightgray": "#F6F7F8",
    "dark": "#1F2933",
    "red": "#C85A4A",
    "gold": "#B8860B",
    "purple": "#CC79A7",
    "cyan": "#56B4E9",
    "yellow": "#F0E442",
}


ASSET = {
    "root": ROOT / "visuals/trellis2_mesh_first_reconstruct_20260507_1745/ifs_branch_tree_r512/input_normalized_preview.png",
    "ovoxel": ROOT / "visuals/trellis2_mesh_first_reconstruct_20260507_1745/ifs_branch_tree_r512/ovoxel_roundtrip_preview.png",
    "slat": ROOT / "visuals/trellis2_mesh_first_reconstruct_20260507_1745/ifs_branch_tree_r512/shape_slat_reconstruct_preview.png",
    "vine_strip": ROOT / "paper_siga/figures/vine_depth_textured_strip_20260509_vizworker.png",
    "pyrite": ROOT / "paper_siga/figures/pyrite_hq_depth_textured_showcase_20260509.png",
    "coral": ROOT / "paper_siga/figures/coral_depth_textured_showcase_rerun1640_20260509.png",
    "projection_ablation": ROOT / "paper_siga/figures/projection_ablation_pure_white_flat_contact_rerun2105_20260509.png",
    "latest_texture": ROOT / "paper_siga/figures/texture_latest_occpos_paperstyle_contact_20260509.png",
    "zoom_overview": ROOT / "visuals/matched_camera_zoom_existing_roots_20260510/vine_stage5/overview_raw.png",
    "zoom_1": ROOT / "visuals/matched_camera_zoom_existing_roots_20260510/vine_stage5/zoom_01.png",
    "zoom_2": ROOT / "visuals/matched_camera_zoom_existing_roots_20260510/vine_stage5/zoom_02.png",
    "zoom_comp": ROOT / "visuals/matched_camera_zoom_existing_roots_20260510/vine_stage5/strict_matched_zoom_comparison.png",
}


def exists(key):
    return ASSET[key].exists()


def fig_ax():
    fig, ax = plt.subplots(figsize=(13.6, 7.6), dpi=180)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")
    return fig, ax


def save(fig, name):
    for ext in ("svg", "pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def box(ax, x, y, w, h, text="", fc="white", ec="#333333", lw=1.4, r=0.08,
        color=None, fontsize=9, weight="regular", align="center", alpha=1.0):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.012,rounding_size={min(w, h) * r}",
        fc=fc, ec=ec, lw=lw, alpha=alpha,
    )
    ax.add_patch(patch)
    if text:
        ax.text(
            x + w / 2, y + h / 2, text,
            ha=align, va="center", fontsize=fontsize,
            color=color or COL["dark"], weight=weight, linespacing=1.15,
        )
    return patch


def label(ax, x, y, text, size=9, color=None, weight="regular", ha="left", va="center"):
    ax.text(x, y, text, fontsize=size, color=color or COL["dark"], weight=weight, ha=ha, va=va, linespacing=1.15)


def arrow(ax, x1, y1, x2, y2, color=None, lw=1.8, style="-|>", rad=0.0, mutation=12):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style, mutation_scale=mutation,
        lw=lw, color=color or COL["dark"],
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=2, shrinkB=2,
    ))


def add_img(ax, path, x, y, w, h, ec="#D0D5DA", label_text=None):
    if Path(path).exists():
        img = Image.open(path).convert("RGB")
        img = ImageOps.contain(img, (900, 700))
        ax.imshow(img, extent=(x, x + w, y, y + h), zorder=1)
        ax.add_patch(Rectangle((x, y), w, h, fc="none", ec=ec, lw=1.0, zorder=2))
    else:
        ax.add_patch(Rectangle((x, y), w, h, fc="#F2F2F2", ec=COL["red"], lw=1.2))
        label(ax, x + w/2, y + h/2, "missing\nasset", size=8, color=COL["red"], ha="center")
    if label_text:
        label(ax, x + w / 2, y - 1.4, label_text, size=7.5, color=COL["gray"], ha="center")


def token_cloud(ax, cx, cy, scale=1.0, mode="mixed"):
    pts = [
        (-4, 0), (-2.5, 1.2), (-1.2, 0.4), (0, 1.5), (1.5, 0.2), (2.9, 1.1),
        (-3.1, -1.4), (-1.5, -1.1), (0.2, -1.0), (1.9, -1.5), (3.5, -0.6),
        (4.7, 1.8), (5.8, 0.4), (5.2, -1.0),
    ]
    for i, (px, py) in enumerate(pts):
        if mode == "raw" and i in (10, 11, 12, 13):
            c = COL["red"]
        elif mode == "competition" and i in (5, 9):
            c = COL["orange"]
        else:
            c = COL["green"]
        ax.add_patch(Rectangle((cx + px * scale, cy + py * scale), 0.9 * scale, 0.9 * scale, fc=c, ec="white", lw=0.6))
    ax.add_patch(Circle((cx - 4.7 * scale, cy - 0.4 * scale), 0.9 * scale, fc=COL["blue"], ec="white", lw=0.6))


def mini_rule_icons(ax, x, y):
    names = [("Grow", COL["green"]), ("Attach", COL["blue"]), ("Symmetry", COL["purple"]), ("Refine", COL["gold"])]
    for i, (n, c) in enumerate(names):
        box(ax, x + i * 8.5, y, 7.5, 4.1, n, fc="#FFFFFF", ec=c, lw=1.3, fontsize=7.2, color=c, weight="bold")


def figure_a_main():
    fig, ax = fig_ax()
    label(ax, 2, 57, "A. Projection-Stabilized Recursive Sparse-Latent Grammar", size=14, weight="bold")
    label(ax, 2, 54.5, "Frozen sparse generative substrate + recursive typed grammar + per-depth admissibility projection", size=8.5, color=COL["gray"])

    box(ax, 2, 8, 25, 42, fc="#FFFFFF", ec=COL["blue"], lw=1.8)
    label(ax, 4, 47.5, "Trellis2 sparse substrate", size=10, weight="bold", color=COL["blue"])
    add_img(ax, ASSET["root"], 4, 35, 7, 8, label_text="root/condition")
    add_img(ax, ASSET["ovoxel"], 12.5, 35, 7, 8, label_text="O-Voxel V")
    add_img(ax, ASSET["slat"], 21, 35, 4.5, 8, label_text="Shape-SLAT F")
    arrow(ax, 11.1, 39, 12.4, 39, COL["blue"], lw=1.2)
    arrow(ax, 19.6, 39, 20.9, 39, COL["blue"], lw=1.2)
    box(ax, 5, 24, 19, 6.2, "state interface\nS_d = (V_d, F_d, A_d, M_d, C_d)", fc="#F7FBFE", ec=COL["blue"], fontsize=8)
    box(ax, 5, 15, 19, 5.5, "decoder / re-encoder\nmesh <-> sparse state", fc="#F7FBFE", ec=COL["gray"], fontsize=8, color=COL["gray"])

    # Central loop.
    box(ax, 31, 10, 38, 40, fc="#FFFFFF", ec=COL["green"], lw=1.8)
    label(ax, 33, 47.5, "PS-RSLG recursive transition", size=10, weight="bold", color=COL["green"])
    steps = [
        (35, 38, "select\nhandles", COL["green"]),
        (49, 38, "apply typed\ngrammar rules", COL["green"]),
        (59, 27, "masked local\nsampler", COL["blue"]),
        (49, 16, "decode mesh\nproposal", COL["gray"]),
        (35, 16, "project to\nadmissible state", COL["orange"]),
    ]
    for x, y, t, c in steps:
        box(ax, x, y, 10, 6.5, t, fc="#FFFFFF", ec=c, lw=1.5, fontsize=7.5, color=c, weight="bold")
    arrow(ax, 45, 41.3, 49, 41.3, COL["green"])
    arrow(ax, 59, 38, 61.5, 33.7, COL["blue"], rad=-0.15)
    arrow(ax, 62, 27, 57, 20, COL["gray"], rad=-0.12)
    arrow(ax, 49, 16, 45, 19, COL["orange"], rad=-0.12)
    arrow(ax, 35, 22.5, 35, 38, COL["green"], rad=-0.18)
    token_cloud(ax, 39.5, 29, scale=0.9, mode="raw")
    label(ax, 32.8, 12.5, "S_{d+1}=P_A(E(D(G_theta(R_phi(S_d), xi_d))))", size=7.5, color=COL["dark"])
    mini_rule_icons(ax, 33, 7.2)

    # Right side.
    box(ax, 73, 8, 25, 42, fc="#FFFFFF", ec=COL["gold"], lw=1.8)
    label(ax, 75, 47.5, "Mesh/PBR assets + evidence", size=10, weight="bold", color=COL["gold"])
    add_img(ax, ASSET["vine_strip"], 75, 35.5, 20.5, 7.8, label_text="recursive textured vine")
    add_img(ax, ASSET["pyrite"], 75, 25, 9.8, 7.5, label_text="crystal/symmetry")
    add_img(ax, ASSET["coral"], 86, 25, 9.8, 7.5, label_text="DLA/coral")
    box(ax, 76, 14.5, 18.5, 6.5, "connected support\nmulti-depth control\ntexture/PBR export", fc="#FFFDF6", ec=COL["gold"], fontsize=8, color=COL["dark"])
    arrow(ax, 27, 30, 31, 30, COL["dark"], lw=1.6)
    arrow(ax, 69, 30, 73, 30, COL["dark"], lw=1.6)
    save(fig, "figure_A_main_method_overview")


def figure_b_trellis():
    fig, ax = fig_ax()
    label(ax, 2, 57, "B. Trellis2 as a reusable sparse codec and local realization prior", size=14, weight="bold")
    label(ax, 2, 54.5, "The paper should show the specific model-native interface used by recursion: support, features, masks, decoder, re-encoder, and PBR export.", size=8.3, color=COL["gray"])
    xs = [3, 18, 34, 50, 66, 82]
    labels = [
        ("root / guide", ASSET["root"], COL["gray"]),
        ("O-Voxel\nsupport V", ASSET["ovoxel"], COL["blue"]),
        ("Shape-SLAT\nfeatures F", ASSET["slat"], COL["blue"]),
        ("masked flow\nrealization", None, COL["purple"]),
        ("mesh decoder\n+ projection", ASSET["projection_ablation"], COL["orange"]),
        ("textured GLB\nPBR export", ASSET["latest_texture"], COL["gold"]),
    ]
    for i, (txt, img, c) in enumerate(labels):
        box(ax, xs[i], 34, 12, 7, txt, fc="#FFFFFF", ec=c, lw=1.5, color=c, weight="bold", fontsize=8)
        if img:
            add_img(ax, img, xs[i], 20, 12, 11.5)
        else:
            box(ax, xs[i], 20, 12, 11.5, "", fc="#F8F7FB", ec=c, lw=1.0)
            for k in range(7):
                ax.add_patch(Circle((xs[i] + 2 + k * 1.25, 25 + math.sin(k) * 2), 0.45, fc=c, ec="white", lw=0.6, alpha=0.8))
            label(ax, xs[i] + 6, 17.8, "noise -> constrained local sample", size=7.2, color=COL["gray"], ha="center")
        if i < len(xs) - 1:
            arrow(ax, xs[i] + 12.2, 37.5, xs[i + 1] - 0.4, 37.5, COL["dark"])
    box(ax, 20, 6.2, 60, 6.5, "PS-RSLG reads/writes sparse state and masks; Trellis2 remains frozen but is repeatedly re-entered at each recursive depth.", fc="#F9FAFB", ec="#D1D5DB", fontsize=8.0)
    arrow(ax, 76, 15.5, 40, 15.5, COL["orange"], lw=1.4, rad=-0.18)
    label(ax, 57, 13.0, "re-encode for next depth", size=7.5, color=COL["orange"], ha="center")
    save(fig, "figure_B_trellis_substrate_pipeline")


def figure_c_projection():
    fig, ax = fig_ax()
    label(ax, 2, 57, "C. Projection is inside the recursive transition", size=14, weight="bold")
    label(ax, 2, 54.5, "Invalid fragments must be removed or connected before their handles can seed deeper recursion.", size=8.5, color=COL["gray"])
    box(ax, 5, 32, 22, 15, "", fc="#FFFFFF", ec=COL["gray"], lw=1.4)
    label(ax, 16, 45.1, "raw decoded proposal", size=8.5, weight="bold", color=COL["gray"], ha="center")
    token_cloud(ax, 15.5, 38, 1.2, mode="raw")
    label(ax, 10, 31, "red: orphan tokens / invalid handles", size=7.5, color=COL["red"])

    box(ax, 39, 29, 22, 22, "", fc="#FFF8F2", ec=COL["orange"], lw=2.0)
    label(ax, 50, 48.0, "P_A admissibility gate", size=9, weight="bold", color=COL["orange"], ha="center")
    box(ax, 42, 42.5, 16, 3.5, "1 root reachability", fc="white", ec=COL["orange"], fontsize=7.0, color=COL["orange"])
    box(ax, 42, 37.4, 16, 3.5, "2 connect or deactivate", fc="white", ec=COL["orange"], fontsize=7.0, color=COL["orange"])
    box(ax, 42, 32.3, 16, 3.5, "3 re-encode S_{d+1}", fc="white", ec=COL["orange"], fontsize=7.0, color=COL["orange"])
    arrow(ax, 27.5, 39.5, 38.5, 39.5, COL["orange"], lw=2.0)

    box(ax, 73, 32, 22, 15, "", fc="#FFFFFF", ec=COL["green"], lw=1.6)
    label(ax, 84, 45.1, "admissible next state", size=8.5, weight="bold", color=COL["green"], ha="center")
    token_cloud(ax, 83.5, 38, 1.2, mode="clean")
    label(ax, 77, 31, "only attached frontier handles remain active", size=7.5, color=COL["green"])
    arrow(ax, 61.5, 39.5, 72.5, 39.5, COL["orange"], lw=2.0)

    box(ax, 5, 8, 90, 17, fc="#FFFFFF", ec="#D1D5DB", lw=1.0)
    label(ax, 7, 22.2, "Evidence inset: direct vs final-only vs per-depth projection", size=9, weight="bold")
    add_img(ax, ASSET["projection_ablation"], 7, 10, 86, 10.5)
    save(fig, "figure_C_projection_gate")


def figure_d_competition():
    fig, ax = fig_ax()
    label(ax, 2, 57, "D. Sparse-native operator scheduling and space competition", size=14, weight="bold")
    label(ax, 2, 54.5, "Multiple grammar handles propose tokens on one occupancy lattice; ownership is resolved before decoding.", size=8.5, color=COL["gray"])
    box(ax, 5, 13, 25, 35, fc="#FFFFFF", ec=COL["green"], lw=1.5)
    label(ax, 7, 45.5, "active handles", size=10, weight="bold", color=COL["green"])
    for i, (x, y, c) in enumerate([(13, 34, COL["blue"]), (20, 27, COL["green"]), (15, 20, COL["purple"])]):
        ax.add_patch(Circle((x, y), 1.2, fc=c, ec="white", lw=1.0))
        label(ax, x + 2, y, f"a_{i+1}", size=8, color=c)
        for k in range(5):
            ax.add_patch(Rectangle((x + 2 + k * 1.2, y + (k % 2) * 1.1 - 1.1), 0.8, 0.8, fc="#E8F3EE", ec=COL["green"], lw=0.5))

    box(ax, 38, 13, 25, 35, fc="#FFFFFF", ec=COL["orange"], lw=1.5)
    label(ax, 40, 45.5, "frontier ownership map", size=10, weight="bold", color=COL["orange"])
    for ix in range(8):
        for iy in range(7):
            c = "#ECEFF1"
            if (ix + iy) % 5 == 0:
                c = COL["green"]
            if (ix, iy) in [(4, 3), (5, 3), (4, 4)]:
                c = COL["red"]
            if (ix, iy) in [(2, 2), (2, 3), (3, 2)]:
                c = COL["orange"]
            ax.add_patch(Rectangle((42 + ix * 2, 22 + iy * 2), 1.5, 1.5, fc=c, ec="white", lw=0.45))
    label(ax, 42, 18.2, "green accepted; red rejected collisions; gray occupied", size=7, color=COL["gray"])
    arrow(ax, 30.5, 30.5, 37.5, 30.5, COL["dark"])

    box(ax, 72, 13, 23, 35, fc="#FFFFFF", ec=COL["blue"], lw=1.5)
    label(ax, 74, 45.5, "connected next support", size=10, weight="bold", color=COL["blue"])
    token_cloud(ax, 82, 33, 1.6, mode="competition")
    box(ax, 75, 17, 17, 7.5, "metrics\nLCR, coverage,\ncollision reject rate", fc="#F7FBFE", ec=COL["blue"], fontsize=7.6, color=COL["blue"])
    arrow(ax, 63.5, 30.5, 71.5, 30.5, COL["dark"])
    save(fig, "figure_D_operator_competition")


def figure_e_naturalization():
    fig, ax = fig_ax()
    label(ax, 2, 57, "E. Masked local naturalization uses the generative sampler without losing grammar constraints", size=13.2, weight="bold")
    label(ax, 2, 54.5, "Hard sparse scaffold and anchors define the editable region; the sampler fills local detail and material; projection closes the loop.", size=8.5, color=COL["gray"])
    box(ax, 5, 18, 24, 27, "", fc="#FFFFFF", ec=COL["green"], lw=1.5)
    label(ax, 17, 42.8, "rule scaffold", size=9, weight="bold", color=COL["green"], ha="center")
    token_cloud(ax, 16, 31, 1.5, mode="clean")
    ax.add_patch(Rectangle((11, 25), 12, 10, fc="none", ec=COL["purple"], lw=2.0, ls="--"))
    label(ax, 11, 22.5, "editable mask + clamped anchors", size=7.5, color=COL["purple"])

    box(ax, 39, 18, 24, 27, "", fc="#FBF8FE", ec=COL["purple"], lw=1.5)
    label(ax, 51, 42.8, "masked flow sampler", size=9, weight="bold", color=COL["purple"], ha="center")
    for k in range(9):
        x = 43 + k * 1.7
        y = 32 + math.sin(k * 0.8) * 4
        ax.add_patch(Circle((x, y), 0.55 + k * 0.035, fc=COL["purple"], ec="white", alpha=0.25 + 0.06 * k))
    arrow(ax, 43, 27, 59, 27, COL["purple"], lw=1.6)
    label(ax, 51, 24, "noise schedule inside mask", size=7.5, color=COL["purple"], ha="center")
    arrow(ax, 29.5, 31.5, 38.5, 31.5, COL["dark"])

    box(ax, 73, 18, 22, 27, "", fc="#FFFFFF", ec=COL["gold"], lw=1.5)
    label(ax, 84, 42.8, "naturalized mesh/PBR", size=9, weight="bold", color=COL["gold"], ha="center")
    add_img(ax, ASSET["latest_texture"], 75, 23, 18, 13)
    arrow(ax, 63.5, 31.5, 72.5, 31.5, COL["dark"])
    box(ax, 18, 7.5, 64, 5.8, "Ablation story: rule-only preserves structure but looks schematic; global repair drifts; masked local repair improves visual quality while keeping support admissible.", fc="#FAFAFA", ec="#D1D5DB", fontsize=7.4)
    save(fig, "figure_E_masked_naturalization")


def figure_f_zoom():
    fig, ax = fig_ax()
    label(ax, 2, 57, "F. Recursive zoom and effective local resolution", size=14, weight="bold")
    label(ax, 2, 54.5, "The same grammar can re-enter the sparse codec at deeper handles instead of allocating one global high-resolution scene.", size=8.5, color=COL["gray"])

    box(ax, 4, 12, 32, 38, fc="#FFFFFF", ec=COL["green"], lw=1.4)
    label(ax, 6, 47.3, "same asset, nested views", size=10, weight="bold", color=COL["green"])
    add_img(ax, ASSET["zoom_overview"], 7, 20, 25, 21)
    ax.add_patch(Rectangle((15, 27), 9, 7, fc="none", ec=COL["orange"], lw=1.8))
    ax.add_patch(Rectangle((19, 30), 4, 3, fc="none", ec=COL["purple"], lw=1.5))

    box(ax, 42, 12, 22, 38, fc="#FFFFFF", ec=COL["blue"], lw=1.4)
    label(ax, 44, 47.3, "recursive call tree", size=10, weight="bold", color=COL["blue"])
    nodes = [(53, 40, "root"), (47, 30, "branch"), (59, 30, "branch"), (44, 20, "terminal"), (51, 20, "terminal"), (62, 20, "terminal")]
    for x, y, t in nodes:
        ax.add_patch(Circle((x, y), 2.3, fc="#F7FBFE", ec=COL["blue"], lw=1.2))
        label(ax, x, y, t, size=6.6, color=COL["blue"], ha="center")
    for a, b in [((53, 38), (47, 32.5)), ((53, 38), (59, 32.5)), ((47, 27.5), (44, 22.4)), ((47, 27.5), (51, 22.4)), ((59, 27.5), (62, 22.4))]:
        arrow(ax, *a, *b, COL["blue"], lw=1.1, mutation=8)
    label(ax, 53, 15.5, "decode -> project -> re-encode\nat selected handles", size=7, color=COL["gray"], ha="center")

    box(ax, 70, 12, 26, 38, fc="#FFFFFF", ec=COL["orange"], lw=1.4)
    label(ax, 72, 47.3, "zoom evidence panels", size=10, weight="bold", color=COL["orange"])
    add_img(ax, ASSET["zoom_1"], 73, 33, 20, 10, label_text="level 1")
    add_img(ax, ASSET["zoom_2"], 73, 20, 20, 10, label_text="level 2")
    box(ax, 73, 13.2, 20, 3.8, "depth parameter controls local detail budget", fc="#FFF8F2", ec=COL["orange"], fontsize=7.1, color=COL["orange"])
    save(fig, "figure_F_recursive_zoom")


def figure_a2_two_layer():
    fig, ax = fig_ax()
    label(ax, 2, 57, "A2. Two-layer view: PS-RSLG writes a sparse program over a frozen Trellis2 substrate", size=13.5, weight="bold")
    label(ax, 2, 54.5, "Use this variant if the paper needs a clearer architectural separation between model prior and grammar system.", size=8.5, color=COL["gray"])
    box(ax, 7, 34, 86, 14, fc="#F7FBFE", ec=COL["blue"], lw=1.6)
    label(ax, 9, 45.8, "Frozen Trellis2 substrate", size=10.5, weight="bold", color=COL["blue"])
    for i, t in enumerate(["encode", "O-Voxel V", "Shape-SLAT F", "masked sampler", "decode mesh", "texture/PBR"]):
        x = 12 + i * 13.2
        c = COL["blue"] if i < 3 else (COL["purple"] if i == 3 else COL["gray"])
        box(ax, x, 37.6, 10.5, 5.2, t, fc="white", ec=c, lw=1.2, fontsize=7.2, color=c, weight="bold")
        if i < 5:
            arrow(ax, x + 10.7, 40.2, x + 12.8, 40.2, COL["dark"], lw=1.0, mutation=8)

    box(ax, 7, 11, 86, 17, fc="#F8FFFB", ec=COL["green"], lw=1.8)
    label(ax, 9, 25.7, "Projection-Stabilized Recursive Sparse-Latent Grammar", size=10.5, weight="bold", color=COL["green"])
    grammar_steps = [
        ("symbols\nSigma", COL["green"]),
        ("typed handles\nA_d", COL["green"]),
        ("rule families\nrho", COL["green"]),
        ("support proposal\nDelta V, Delta F", COL["blue"]),
        ("projection\nP_A", COL["orange"]),
        ("next state\nS_{d+1}", COL["green"]),
    ]
    for i, (t, c) in enumerate(grammar_steps):
        x = 11 + i * 13.5
        box(ax, x, 15, 11, 6, t, fc="white", ec=c, lw=1.2, fontsize=7.2, color=c, weight="bold")
        if i < len(grammar_steps) - 1:
            arrow(ax, x + 11.2, 18, x + 13.2, 18, COL["dark"], lw=1.0, mutation=8)
    arrow(ax, 30, 28.2, 30, 34, COL["blue"], lw=1.3)
    label(ax, 32, 31.2, "read/write sparse state", size=7.5, color=COL["blue"])
    arrow(ax, 66, 34, 66, 28.2, COL["orange"], lw=1.3)
    label(ax, 68, 31.2, "re-enter after projection", size=7.5, color=COL["orange"])
    add_img(ax, ASSET["vine_strip"], 14, 3.5, 30, 5.8, label_text="selected output")
    add_img(ax, ASSET["pyrite"], 55, 3.5, 25, 5.8, label_text="non-tree output")
    save(fig, "figure_A2_two_layer_architecture")


def figure_g_classical_coverage():
    fig, ax = fig_ax()
    label(ax, 2, 57, "G. Classical procedural systems as restricted PS-RSLG programs", size=14, weight="bold")
    label(ax, 2, 54.5, "This optional method figure supports the formal framework claim; it should be paired with equations in the method section or supplement.", size=8.3, color=COL["gray"])
    systems = [
        ("IFS", "contractive transforms\nfixed symbol rewrite", "copy / transform rules", COL["purple"]),
        ("L-system", "string symbols + turtle\nbranch rewrite", "typed handle expansion", COL["green"]),
        ("Space colonization", "attractor competition\noccupied space", "frontier ownership map", COL["blue"]),
        ("DLA / frontier", "stochastic walkers\nboundary attachment", "masked stochastic growth", COL["orange"]),
        ("Symmetry / tiling", "group action G\norbit replication", "equivariant transform family", COL["gold"]),
    ]
    x0, y0, w, h = 5, 39, 18, 10
    for i, (name, classical, ours, c) in enumerate(systems):
        x = x0 + i * 18.5
        box(ax, x, y0, w - 1.5, h, name, fc="white", ec=c, lw=1.5, fontsize=10, color=c, weight="bold")
        box(ax, x, y0 - 12, w - 1.5, 8.5, classical, fc="#FAFAFA", ec="#CDD3DA", lw=1.0, fontsize=7.0, color=COL["gray"])
        box(ax, x, y0 - 24, w - 1.5, 8.5, ours, fc="#F8FFFB", ec=c, lw=1.1, fontsize=7.0, color=c)
        arrow(ax, x + (w - 1.5)/2, y0 - 3.0, x + (w - 1.5)/2, y0 - 11.5, COL["dark"], lw=0.9, mutation=7)
        arrow(ax, x + (w - 1.5)/2, y0 - 15.2, x + (w - 1.5)/2, y0 - 23.5, COL["dark"], lw=0.9, mutation=7)
    box(ax, 18, 6.2, 64, 6.5, "Unifying state: S_d=(V_d,F_d,A_d,M_d,C_d). A classical method fixes or removes the generative sampler, projection, or feature field; PS-RSLG keeps them active.", fc="#F9FAFB", ec="#D1D5DB", fontsize=8.0)
    save(fig, "figure_G_classical_system_coverage")


def make_contact_sheet():
    pngs = [
        OUT / "figure_A_main_method_overview.png",
        OUT / "figure_A2_two_layer_architecture.png",
        OUT / "figure_B_trellis_substrate_pipeline.png",
        OUT / "figure_C_projection_gate.png",
        OUT / "figure_D_operator_competition.png",
        OUT / "figure_E_masked_naturalization.png",
        OUT / "figure_F_recursive_zoom.png",
        OUT / "figure_G_classical_system_coverage.png",
    ]
    thumbs = []
    for p in pngs:
        img = Image.open(p).convert("RGB")
        img.thumbnail((640, 360))
        canvas = Image.new("RGB", (680, 420), "white")
        canvas.paste(img, ((680 - img.width) // 2, 18))
        d = ImageDraw.Draw(canvas)
        d.rectangle((0, 0, 679, 419), outline=(205, 210, 216), width=2)
        d.text((18, 385), p.stem, fill=(31, 41, 51))
        thumbs.append(canvas)
    rows = math.ceil(len(thumbs) / 2)
    sheet = Image.new("RGB", (1360, 420 * rows), "white")
    for i, im in enumerate(thumbs):
        x = (i % 2) * 680
        y = (i // 2) * 420
        sheet.paste(im, (x, y))
    sheet.save(OUT / "method_diagram_drafts_contact_sheet.png")


def write_manifest():
    missing = [k for k, p in ASSET.items() if not p.exists()]
    text = "# Method diagram draft asset manifest\n\n"
    text += "Generated six SVG/PDF/PNG draft figures from local assets only.\n\n"
    text += "## Source assets\n\n"
    for k, p in ASSET.items():
        text += f"- `{k}`: `{p}` {'OK' if p.exists() else 'MISSING'}\n"
    text += "\n## Missing assets\n\n"
    text += "None.\n" if not missing else "\n".join(f"- {m}" for m in missing) + "\n"
    text += "\n## Outputs\n\n"
    for name in [
        "figure_A_main_method_overview",
        "figure_A2_two_layer_architecture",
        "figure_B_trellis_substrate_pipeline",
        "figure_C_projection_gate",
        "figure_D_operator_competition",
        "figure_E_masked_naturalization",
        "figure_F_recursive_zoom",
        "figure_G_classical_system_coverage",
        "method_diagram_drafts_contact_sheet",
    ]:
        text += f"- `{OUT / (name + ('.png' if name.startswith('method') else '.svg'))}`\n"
    (OUT / "asset_manifest.md").write_text(text, encoding="utf-8")


def main():
    figure_a_main()
    figure_b_trellis()
    figure_c_projection()
    figure_d_competition()
    figure_e_naturalization()
    figure_f_zoom()
    figure_a2_two_layer()
    figure_g_classical_coverage()
    make_contact_sheet()
    write_manifest()
    print(f"Wrote drafts to {OUT}")


if __name__ == "__main__":
    main()
