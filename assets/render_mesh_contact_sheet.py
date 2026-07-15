#!/usr/bin/env python3
"""Render shaded mesh contact sheets for recursive-growth experiments."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np


def normalize_vertices(vertices: np.ndarray) -> np.ndarray:
    vertices = np.asarray(vertices, dtype=np.float32)
    center = (vertices.min(axis=0) + vertices.max(axis=0)) / 2.0
    extent = max(float((vertices.max(axis=0) - vertices.min(axis=0)).max()), 1e-6)
    return (vertices - center) / extent


def sample_faces(faces: np.ndarray, max_faces: int, seed: int = 13) -> np.ndarray:
    if len(faces) <= max_faces:
        return faces
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(faces), size=max_faces, replace=False)
    idx.sort()
    return faces[idx]


def face_shades(vertices: np.ndarray, faces: np.ndarray, light_dir: np.ndarray) -> np.ndarray:
    tri = vertices[faces]
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = normals / np.maximum(norms, 1e-8)
    light_dir = light_dir / np.linalg.norm(light_dir)
    shade = normals @ light_dir
    shade = np.clip(0.28 + 0.72 * np.maximum(shade, 0.0), 0.18, 1.0)
    return shade


def render_mesh(ax, vertices: np.ndarray, faces: np.ndarray, title: str, view: str, max_faces: int) -> None:
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    vertices = normalize_vertices(vertices)
    faces = sample_faces(faces, max_faces)
    tri = vertices[faces]
    z = tri.mean(axis=1)[:, 2]
    z_norm = (z - z.min()) / max(float(z.max() - z.min()), 1e-6)
    base_low = np.array([0.34, 0.49, 0.54])
    base_high = np.array([0.86, 0.78, 0.44])
    base = base_low[None, :] * (1.0 - z_norm[:, None]) + base_high[None, :] * z_norm[:, None]
    shade = face_shades(vertices, faces, np.array([0.35, -0.45, 0.82], dtype=np.float32))
    colors = np.clip(base * shade[:, None], 0, 1)
    colors = np.concatenate([colors, np.full((len(colors), 1), 1.0)], axis=1)

    collection = Poly3DCollection(tri, linewidths=0.0, antialiased=False)
    collection.set_facecolor(colors)
    collection.set_edgecolor((0, 0, 0, 0))
    ax.add_collection3d(collection)
    ax.set_xlim(-0.55, 0.55)
    ax.set_ylim(-0.55, 0.55)
    ax.set_zlim(-0.55, 0.55)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    if view == "front":
        ax.view_init(elev=10, azim=-90)
    elif view == "side":
        ax.view_init(elev=10, azim=0)
    elif view == "top":
        ax.view_init(elev=78, azim=-55)
    else:
        ax.view_init(elev=22, azim=-45)
    ax.set_title(title, fontsize=8, pad=1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", help="label=mesh.obj")
    parser.add_argument("--case-file", type=Path, help="Text file with one label=mesh.obj per line")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--views", nargs="+", default=["iso", "front", "side"])
    parser.add_argument("--max-faces", type=int, default=70000)
    parser.add_argument("--dpi", type=int, default=180)
    args = parser.parse_args()

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import trimesh

    case_items = list(args.case or [])
    if args.case_file:
        for line in args.case_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                case_items.append(line)
    if not case_items:
        raise SystemExit("No cases provided. Use --case or --case-file.")

    cases = []
    for item in case_items:
        label, path = item.split("=", 1)
        mesh = trimesh.load(path, force="mesh", process=False)
        vertices = np.asarray(mesh.vertices, dtype=np.float32)
        faces = np.asarray(mesh.faces, dtype=np.int64)
        cases.append((label, vertices, faces))

    width = max(3.0 * len(args.views), 4.0)
    height = max(2.7 * len(cases), 3.0)
    fig = plt.figure(figsize=(width, height))
    for row, (label, vertices, faces) in enumerate(cases):
        for col, view in enumerate(args.views):
            idx = row * len(args.views) + col + 1
            ax = fig.add_subplot(len(cases), len(args.views), idx, projection="3d")
            title = f"{label} {view}" if col == 0 else view
            render_mesh(ax, vertices, faces, title, view, args.max_faces)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.01, wspace=0.02, hspace=0.05)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=args.dpi)
    plt.close(fig)
    print(args.out)


if __name__ == "__main__":
    main()
