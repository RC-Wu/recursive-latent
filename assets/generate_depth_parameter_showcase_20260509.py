#!/usr/bin/env python3
"""Create a mesh-only depth/control showcase figure for the SIGA paper draft."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper_siga/figures/depth_parameter_showcase_20260509.png"


@dataclass(frozen=True)
class Panel:
    label: str
    path: Path


DEPTH_PANELS = [
    Panel(
        "depth 1",
        ROOT
        / "visuals/siga_night_20260508/siga_projected_recursive_loop_0715/vine_d5_projected_compete/stage_01/projected/vine_d5_projected_compete_stage_01/mesh_pruned.obj",
    ),
    Panel(
        "depth 2",
        ROOT
        / "visuals/siga_night_20260508/siga_projected_recursive_loop_0715/vine_d5_projected_compete/stage_02/projected/vine_d5_projected_compete_stage_02/mesh_pruned.obj",
    ),
    Panel(
        "depth 3",
        ROOT
        / "visuals/siga_night_20260508/siga_projected_recursive_loop_0715/vine_d5_projected_compete/stage_03/projected/vine_d5_projected_compete_stage_03/mesh_pruned.obj",
    ),
    Panel(
        "depth 4",
        ROOT
        / "visuals/siga_night_20260508/siga_projected_recursive_loop_0715/vine_d5_projected_compete/stage_04/projected/vine_d5_projected_compete_stage_04/mesh_pruned.obj",
    ),
]

CONTROL_PANELS = [
    Panel(
        "compete",
        ROOT / "visuals/siga_night_20260508/siga_vine_projection_pruning_0700/minv_300/vine_compete_d3/mesh_pruned.obj",
    ),
    Panel(
        "fork-side",
        ROOT / "visuals/siga_night_20260508/siga_vine_projection_pruning_0700/minv_300/vine_fork_side_d3/mesh_pruned.obj",
    ),
    Panel(
        "radial-4",
        ROOT / "visuals/siga_night_20260508/siga_vine_projection_pruning_0700/minv_300/vine_radial4_d3/mesh_pruned.obj",
    ),
    Panel(
        "portal",
        ROOT / "visuals/siga_night_20260508/siga_vine_projection_pruning_0700/minv_300/vine_portal_d3/mesh_pruned.obj",
    ),
]


def normalize_vertices(vertices: np.ndarray) -> np.ndarray:
    center = (vertices.min(axis=0) + vertices.max(axis=0)) / 2.0
    extent = max(float((vertices.max(axis=0) - vertices.min(axis=0)).max()), 1e-6)
    return (vertices - center) / extent


def sample_faces(faces: np.ndarray, max_faces: int, seed: int = 20260509) -> np.ndarray:
    if len(faces) <= max_faces:
        return faces
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(faces), size=max_faces, replace=False)
    idx.sort()
    return faces[idx]


def face_colors(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    tri = vertices[faces]
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-8)
    light = np.array([0.35, -0.45, 0.82], dtype=np.float32)
    light /= np.linalg.norm(light)
    shade = np.clip(0.32 + 0.68 * np.maximum(normals @ light, 0.0), 0.22, 1.0)

    height = tri.mean(axis=1)[:, 2]
    height = (height - height.min()) / max(float(height.max() - height.min()), 1e-6)
    low = np.array([0.38, 0.48, 0.52])
    high = np.array([0.83, 0.76, 0.48])
    base = low[None, :] * (1.0 - height[:, None]) + high[None, :] * height[:, None]
    rgb = np.clip(base * shade[:, None], 0.0, 1.0)
    return np.column_stack([rgb, np.ones(len(rgb))])


def render_panel(ax, panel: Panel, max_faces: int) -> tuple[int, int]:
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import trimesh

    mesh = trimesh.load(panel.path, force="mesh", process=False)
    vertices = normalize_vertices(np.asarray(mesh.vertices, dtype=np.float32))
    faces = sample_faces(np.asarray(mesh.faces, dtype=np.int64), max_faces=max_faces)
    tri = vertices[faces]

    collection = Poly3DCollection(tri, linewidths=0.0, antialiased=False)
    collection.set_facecolor(face_colors(vertices, faces))
    collection.set_edgecolor((0, 0, 0, 0))
    ax.add_collection3d(collection)
    ax.set_xlim(-0.56, 0.56)
    ax.set_ylim(-0.56, 0.56)
    ax.set_zlim(-0.56, 0.56)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=18, azim=-42)
    ax.set_axis_off()
    ax.set_title(panel.label, fontsize=10, pad=0, color="#202020")
    return len(mesh.vertices), len(mesh.faces)


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "text.usetex": False,
        }
    )

    panels = [DEPTH_PANELS, CONTROL_PANELS]
    row_titles = ["fixed case: recursive depth", "fixed depth: control sweep"]
    fig = plt.figure(figsize=(10.8, 4.9), facecolor="white")
    grid = fig.add_gridspec(
        2,
        4,
        left=0.055,
        right=0.995,
        top=0.88,
        bottom=0.075,
        wspace=0.02,
        hspace=0.10,
    )

    stats: list[tuple[str, int, int]] = []
    for row, row_panels in enumerate(panels):
        fig.text(
            0.012,
            0.68 if row == 0 else 0.275,
            row_titles[row],
            rotation=90,
            va="center",
            ha="left",
            fontsize=8.5,
            color="#202020",
        )
        for col, panel in enumerate(row_panels):
            ax = fig.add_subplot(grid[row, col], projection="3d")
            vertices, faces = render_panel(ax, panel, max_faces=60000)
            stats.append((panel.label, vertices, faces))

    fig.text(0.055, 0.955, "mesh-only method-control visualization", ha="left", va="top", fontsize=9, color="#202020")
    fig.text(
        0.995,
        0.025,
        "neutral triangle render; not point cloud",
        ha="right",
        va="bottom",
        fontsize=7.5,
        color="#606060",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor="white", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)

    print(OUT)
    for label, vertices, faces in stats:
        print(f"{label}: {vertices} vertices, {faces} faces")


if __name__ == "__main__":
    main()
