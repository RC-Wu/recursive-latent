#!/usr/bin/env python3
"""Render clean 2D condition images for the pure logarithmic spiral case."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import List, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def log_spiral(turns: float, steps: int, r0: float, r_min: float, theta0: float) -> np.ndarray:
    theta_span = float(turns) * math.tau
    b = math.log(float(r0) / float(r_min)) / max(theta_span, 1e-6)
    pts: List[Tuple[float, float]] = []
    for i in range(steps):
        t = i / float(max(steps - 1, 1))
        theta_rel = theta_span * t
        theta = theta0 + theta_rel
        r = r0 * math.exp(-b * theta_rel)
        pts.append((r * math.cos(theta), r * math.sin(theta)))
    return np.asarray(pts, dtype=float)


def arc_lengths(points: np.ndarray) -> np.ndarray:
    seg = np.linalg.norm(np.diff(points, axis=0), axis=1)
    return np.concatenate([[0.0], np.cumsum(seg)])


def tangent_normal(points: np.ndarray, idx: int) -> Tuple[np.ndarray, np.ndarray]:
    i0 = max(0, idx - 2)
    i1 = min(len(points) - 1, idx + 2)
    t = points[i1] - points[i0]
    t = t / max(float(np.linalg.norm(t)), 1e-8)
    n = np.array([-t[1], t[0]], dtype=float)
    return t, n


def child_curve(anchor: np.ndarray, tangent: np.ndarray, normal: np.ndarray, rank: int, dense: bool) -> np.ndarray:
    side = -1.0 if rank % 2 else 1.0
    scale = (0.170 if dense else 0.205) * (0.93 ** (rank % 5))
    base = log_spiral(0.88 + 0.10 * (rank % 3), 96, 0.66, 0.105, side * (0.16 + 0.05 * rank))
    base = base - base[0]
    pts = []
    for i, p in enumerate(base):
        u = i / float(max(len(base) - 1, 1))
        pts.append(anchor + normal * (0.030 + scale * p[0] - 0.025 * scale * u) + tangent * (side * scale * p[1] + side * 0.030 * scale * u))
    return np.asarray(pts, dtype=float)


def draw_case(path: Path, depth: int, dense: bool, ink: bool, size: int) -> None:
    main = log_spiral(3.02 if dense else 2.72, 520, 1.0, 0.045, 0.10 if dense else -0.18)
    arcs = arc_lengths(main)
    count = depth * (3 if dense else 2)
    children: List[np.ndarray] = []
    if count:
        for rank, target in enumerate(np.linspace(arcs[80], arcs[-88], count)):
            idx = int(np.argmin(np.abs(arcs - target)))
            tangent, normal = tangent_normal(main, idx)
            if np.dot(normal, main[idx]) < 0:
                normal = -normal
            children.append(child_curve(main[idx], tangent, normal, rank, dense))

    fig = plt.figure(figsize=(size / 120, size / 120), dpi=120)
    ax = fig.add_subplot(111)
    ax.set_aspect("equal")
    ax.axis("off")
    color_main = "#256f57" if ink else "#2d7f62"
    color_child = "#5aa36f" if ink else "#66b982"
    ax.plot(main[:, 0], main[:, 1], color=color_main, linewidth=18 if ink else 20, solid_capstyle="round")
    ax.plot(main[:, 0], main[:, 1], color="#d5d77d", linewidth=9 if ink else 10, alpha=0.62, solid_capstyle="round")
    for child in children:
        ax.plot(child[:, 0], child[:, 1], color=color_child, linewidth=9 if ink else 10, solid_capstyle="round")
        ax.plot(child[:, 0], child[:, 1], color="#d7dc8a", linewidth=4, alpha=0.58, solid_capstyle="round")
    all_pts = np.concatenate([main] + children, axis=0) if children else main
    mn = all_pts.min(axis=0)
    mx = all_pts.max(axis=0)
    center = (mn + mx) * 0.5
    span = max(float((mx - mn).max()), 1e-6) * 1.28
    ax.set_xlim(center[0] - span / 2, center[0] + span / 2)
    ax.set_ylim(center[1] - span / 2, center[1] + span / 2)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/log_spiral_conditions_20260512n"))
    parser.add_argument("--size", type=int, default=1024)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    outputs = []
    for dense in (False, True):
        variant = "surface" if not dense else "dense_surface"
        for depth in (2, 4):
            for ink in (False, True):
                style = "ink" if ink else "soft"
                path = args.out / f"log_spiral_{variant}_d{depth}_{style}_condition.png"
                draw_case(path, depth=depth, dense=dense, ink=ink, size=args.size)
                outputs.append(str(path))
    (args.out / "summary.json").write_text(
        json.dumps(
            {
                "kind": "pure_logarithmic_spiral_recursive_condition_images",
                "constraint": "no rods; main r(theta)=r0*exp(-b*theta); child spirals attach along main spiral",
                "outputs": outputs,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"out": str(args.out), "outputs": outputs}, indent=2))


if __name__ == "__main__":
    main()
