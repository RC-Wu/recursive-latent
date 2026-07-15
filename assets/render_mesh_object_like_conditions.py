#!/usr/bin/env python3
"""Render procedural meshes as object-like alpha-masked image conditions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh


def normalize_vertices(vertices: np.ndarray, fit_scale: float) -> np.ndarray:
    vmin = vertices.min(axis=0)
    vmax = vertices.max(axis=0)
    center = (vmin + vmax) / 2
    scale = fit_scale / max(float((vmax - vmin).max()), 1e-6)
    return (vertices - center) * scale


def render(path: Path, vertices: np.ndarray, mode: str, elev: float, azim: float, title: str, size: int = 768) -> None:
    fig = plt.figure(figsize=(size / 120, size / 120), dpi=120)
    fig.patch.set_alpha(0)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor((0, 0, 0, 0))
    step = max(1, len(vertices) // 35000)
    pts = vertices[::step]
    if mode == "solid_depth":
        colors = pts[:, 2]
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=2.8, c=colors, cmap="viridis", alpha=0.98, linewidths=0)
    elif mode == "warm_silhouette":
        colors = np.linalg.norm(pts[:, :2], axis=1)
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=3.4, c=colors, cmap="copper", alpha=0.98, linewidths=0)
    elif mode == "ink_mass":
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=4.0, c="#1c8f6f", alpha=0.92, linewidths=0)
    else:
        raise ValueError(mode)
    center = (vertices.min(0) + vertices.max(0)) / 2
    span = max(float((vertices.max(0) - vertices.min(0)).max()), 1e-3)
    pad = span * 0.18
    ax.set_xlim(center[0] - span / 2 - pad, center[0] + span / 2 + pad)
    ax.set_ylim(center[1] - span / 2 - pad, center[1] + span / 2 + pad)
    ax.set_zlim(center[2] - span / 2 - pad, center[2] + span / 2 + pad)
    ax.view_init(elev, azim)
    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    fig.savefig(path, transparent=True)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--case-name", default=None)
    parser.add_argument("--fit-scale", type=float, default=0.88)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    case = args.case_name or args.mesh.stem
    mesh = trimesh.load(str(args.mesh), force="mesh", process=False)
    vertices = normalize_vertices(np.asarray(mesh.vertices, dtype=np.float32), args.fit_scale)
    configs = [
        ("solid_depth_front", "solid_depth", 18, -45),
        ("solid_depth_side", "solid_depth", 22, 25),
        ("warm_silhouette", "warm_silhouette", 18, -55),
        ("ink_mass", "ink_mass", 28, -35),
    ]
    outputs = []
    for name, mode, elev, azim in configs:
        path = args.out / f"{case}_{name}.png"
        render(path, vertices, mode, elev, azim, f"{case} {name}")
        outputs.append(str(path))
    summary = {
        "kind": "object_like_mesh_condition_renders",
        "mesh": str(args.mesh),
        "case": case,
        "fit_scale": args.fit_scale,
        "outputs": outputs,
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
