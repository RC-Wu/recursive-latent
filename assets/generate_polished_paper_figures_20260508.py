from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

from paper_plot_style_recursive_growth import (
    DISPLAY_LABELS,
    LINESTYLES,
    MARKERS,
    METHOD_COLORS,
    OPERATOR_COLORS,
    configure_paper_style,
    save_figure,
)


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
FIG_DIR = ROOT / "paper_siga" / "figures"
VIS_DIR = ROOT / "visuals" / "baselines_space_colonization_blender_20260508"


def read_space_rows():
    path = FIG_DIR / "space_competition_depth_curves_20260508.csv"
    rows = []
    with path.open() as f:
        for row in csv.DictReader(f):
            row["depth"] = int(float(row["depth"]))
            for key in ["tokens", "vertices", "faces", "decode_seconds"]:
                row[key] = float(row[key])
            rows.append(row)
    return rows


def draw_space_competition_compact():
    rows = read_space_rows()
    cases = ["Vine", "Tree", "Porous"]
    metrics = [
        ("tokens", "Sparse tokens", 1.0),
        ("vertices", r"Vertices ($10^5$)", 1e5),
        ("faces", r"Faces ($10^6$)", 1e6),
    ]

    fig, axes = plt.subplots(len(metrics), len(cases), figsize=(7.15, 4.85))
    for r, (metric, ylabel, scale) in enumerate(metrics):
        for c, case in enumerate(cases):
            ax = axes[r, c]
            case_rows = [row for row in rows if row["case"] == case]
            operators = []
            for row in case_rows:
                if row["operator"] not in operators:
                    operators.append(row["operator"])
            for op in operators:
                op_rows = sorted(
                    [row for row in case_rows if row["operator"] == op],
                    key=lambda x: x["depth"],
                )
                ax.plot(
                    [row["depth"] for row in op_rows],
                    [row[metric] / scale for row in op_rows],
                    color=OPERATOR_COLORS.get(op, "#555555"),
                    marker=MARKERS.get(op, "o"),
                    linestyle=LINESTYLES.get(op, "-"),
                    linewidth=1.25,
                    markersize=3.4,
                    label=DISPLAY_LABELS.get(op, op),
                )
            if r == 0:
                ax.set_title(case, pad=3.5)
            if c == 0:
                ax.set_ylabel(ylabel)
            if r == len(metrics) - 1:
                ax.set_xlabel("Depth")
            ax.set_xticks(sorted({row["depth"] for row in case_rows}))
            ax.margins(x=0.07, y=0.12)

    handles, labels = [], []
    for ax in axes.flatten():
        h, l = ax.get_legend_handles_labels()
        for handle, label in zip(h, l):
            if label not in labels:
                handles.append(handle)
                labels.append(label)
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.0),
        ncol=5,
        frameon=False,
        handlelength=2.0,
        columnspacing=0.95,
    )
    fig.subplots_adjust(left=0.075, right=0.995, top=0.88, bottom=0.095, wspace=0.32, hspace=0.42)
    save_figure(fig, FIG_DIR / "space_competition_depth_curves_compact_20260508")
    plt.close(fig)


def draw_space_competition_metric(metric: str, ylabel: str, scale: float, out_name: str):
    rows = read_space_rows()
    cases = ["Vine", "Tree", "Porous"]
    fig, axes = plt.subplots(1, len(cases), figsize=(7.15, 1.95), sharey=False)
    for c, case in enumerate(cases):
        ax = axes[c]
        case_rows = [row for row in rows if row["case"] == case]
        operators = []
        for row in case_rows:
            if row["operator"] not in operators:
                operators.append(row["operator"])
        for op in operators:
            op_rows = sorted([row for row in case_rows if row["operator"] == op], key=lambda x: x["depth"])
            ax.plot(
                [row["depth"] for row in op_rows],
                [row[metric] / scale for row in op_rows],
                color=OPERATOR_COLORS.get(op, "#555555"),
                marker=MARKERS.get(op, "o"),
                linestyle=LINESTYLES.get(op, "-"),
                linewidth=1.28,
                markersize=3.5,
                label=DISPLAY_LABELS.get(op, op),
            )
        ax.set_title(case, pad=2.5)
        ax.set_xlabel("Depth")
        if c == 0:
            ax.set_ylabel(ylabel)
        ax.set_xticks(sorted({row["depth"] for row in case_rows}))
        ax.margins(x=0.07, y=0.14)

    handles, labels = [], []
    for ax in axes:
        h, l = ax.get_legend_handles_labels()
        for handle, label in zip(h, l):
            if label not in labels:
                handles.append(handle)
                labels.append(label)
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.0),
        ncol=5,
        frameon=False,
        handlelength=2.0,
        columnspacing=0.85,
    )
    fig.subplots_adjust(left=0.075, right=0.995, top=0.76, bottom=0.25, wspace=0.26)
    save_figure(fig, FIG_DIR / out_name)
    plt.close(fig)


def read_projection_rows():
    path = ROOT / "docs" / "projection_ablation_20260508_1945" / "projection_ablation_table.csv"
    rows = []
    with path.open() as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "case": row["case"],
                    "direct_comps": float(row["direct_components"]),
                    "direct_lcr": float(row["direct_largest_ratio"]),
                    "final_kept": float(row["final_only_kept_components"]),
                    "final_lcr": float(row["final_only_largest_ratio"]),
                    "per_raw": float(row["per_depth_raw_components"]),
                    "per_kept": float(row["per_depth_kept_components"]),
                    "per_lcr": float(row["per_depth_largest_ratio"]),
                }
            )
    return rows


def short_case(name: str) -> str:
    return (
        name.replace("_", " ")
        .replace("vine compete fork d3", "vine fork")
        .replace("tree compete fork d3", "tree fork")
        .replace("vine compete d3", "vine compete")
        .replace("tree compete d3", "tree compete")
    )


def draw_projection_ablation_polished():
    rows = read_projection_rows()
    cases = [short_case(row["case"]) for row in rows]
    x = np.arange(len(rows))
    width = 0.24

    fig, axes = plt.subplots(1, 2, figsize=(7.15, 2.35))
    ax = axes[0]
    lcrs = [
        [row["direct_lcr"] for row in rows],
        [row["final_lcr"] for row in rows],
        [row["per_lcr"] for row in rows],
    ]
    methods = ["Direct", "Final-only", "Per-depth"]
    for i, method in enumerate(methods):
        ax.bar(
            x + (i - 1) * width,
            lcrs[i],
            width,
            color=METHOD_COLORS[method],
            label=method,
            edgecolor="white",
            linewidth=0.4,
        )
    ax.set_ylim(0, 1.06)
    ax.set_ylabel("Largest component ratio")
    ax.set_xticks(x)
    ax.set_xticklabels(cases, rotation=18, ha="right")
    ax.set_title("(a) Connected mass", loc="left")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", padding=1.5, fontsize=5.8)

    ax = axes[1]
    comp_values = [
        [row["direct_comps"] for row in rows],
        [row["final_kept"] for row in rows],
        [row["per_kept"] for row in rows],
    ]
    for i, method in enumerate(methods):
        ax.bar(
            x + (i - 1) * width,
            comp_values[i],
            width,
            color=METHOD_COLORS[method],
            edgecolor="white",
            linewidth=0.4,
        )
    ax.set_yscale("log")
    ax.set_ylabel("Connected components")
    ax.set_xticks(x)
    ax.set_xticklabels(cases, rotation=18, ha="right")
    ax.set_title("(b) Fragment count", loc="left")
    for container in ax.containers:
        labels = []
        for bar in container:
            value = bar.get_height()
            if value >= 1000:
                labels.append(f"{value/1000:.1f}k")
            else:
                labels.append(f"{value:.0f}")
        ax.bar_label(container, labels=labels, padding=1.5, fontsize=5.8)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False)
    fig.subplots_adjust(left=0.075, right=0.995, top=0.78, bottom=0.26, wspace=0.28)
    save_figure(fig, FIG_DIR / "projection_ablation_lcr_components_20260508")
    plt.close(fig)


def crop_render(path: Path, margin: int = 18) -> Image.Image:
    im = Image.open(path).convert("RGB")
    # Crop the uniform white paper margins from contact-sheet inputs; keep Blender frame intact.
    arr = np.asarray(im)
    mask = np.any(arr < 245, axis=2)
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return im
    left = max(xs.min() - margin, 0)
    right = min(xs.max() + margin, im.width - 1)
    top = max(ys.min() - margin, 0)
    bottom = min(ys.max() + margin, im.height - 1)
    return im.crop((left, top, right + 1, bottom + 1))


def draw_mesh_status_strip():
    items = [
        ("Traditional tree", VIS_DIR / "sc_tree_iso.png"),
        ("Traditional root", VIS_DIR / "sc_root_iso.png"),
        ("Traditional bush", VIS_DIR / "sc_bush_iso.png"),
        (
            "Ours tree mesh",
            ROOT / "visuals" / "paper_quality_renders_20260508" / "blender_tiles" / "tree_compete_iso.png",
        ),
        (
            "Ours vine textured",
            ROOT
            / "visuals"
            / "paper_quality_renders_20260508"
            / "textured_glb_preview"
            / "vine_d5_compete_tex_iso.png",
        ),
        (
            "Ours tree textured",
            ROOT
            / "visuals"
            / "paper_quality_renders_20260508"
            / "textured_glb_preview"
            / "tree_compete_tex_iso.png",
        ),
    ]
    cell_w, cell_h = 520, 380
    title_h = 38
    bg = (250, 249, 246)
    sheet = Image.new("RGB", (cell_w * 3, (cell_h + title_h) * 2), bg)
    draw = ImageDraw.Draw(sheet)
    for idx, (title, path) in enumerate(items):
        im = crop_render(path)
        im.thumbnail((cell_w - 24, cell_h - 18), Image.LANCZOS)
        col, row = idx % 3, idx // 3
        x0, y0 = col * cell_w, row * (cell_h + title_h)
        draw.rounded_rectangle(
            (x0 + 8, y0 + 8, x0 + cell_w - 8, y0 + cell_h + title_h - 8),
            radius=8,
            fill=(255, 255, 255),
            outline=(224, 224, 220),
            width=1,
        )
        draw.text((x0 + 22, y0 + 17), title, fill=(40, 40, 40))
        px = x0 + (cell_w - im.width) // 2
        py = y0 + title_h + (cell_h - im.height) // 2
        sheet.paste(im, (px, py))
    out = VIS_DIR / "mesh_based_visual_status_contact_sheet_refined.png"
    sheet.save(out, quality=95)
    (FIG_DIR / out.name).write_bytes(out.read_bytes())


def main():
    configure_paper_style()
    draw_space_competition_compact()
    draw_space_competition_metric("tokens", "Sparse tokens", 1.0, "space_competition_depth_curves_tokens_20260508")
    draw_space_competition_metric("vertices", r"Vertices ($10^5$)", 1e5, "space_competition_depth_curves_vertices_20260508")
    draw_space_competition_metric("faces", r"Faces ($10^6$)", 1e6, "space_competition_depth_curves_faces_20260508")
    draw_projection_ablation_polished()
    draw_mesh_status_strip()
    print("polished figures written to", FIG_DIR)


if __name__ == "__main__":
    main()
