#!/usr/bin/env python3
"""Generate traditional procedural 3D baselines for recursive growth."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class Mesh:
    vertices: list[tuple[float, float, float]]
    faces: list[tuple[int, int, int]]


def unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n < 1e-9:
        return v
    return v / n


def basis_from_axis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = unit(axis)
    seed = np.array([0.0, 0.0, 1.0]) if abs(w[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = unit(np.cross(w, seed))
    v = unit(np.cross(w, u))
    return u, v, w


def add_cylinder(mesh: Mesh, start: np.ndarray, end: np.ndarray, radius0: float, radius1: float, sides: int = 10) -> None:
    axis = end - start
    u, v, _ = basis_from_axis(axis)
    base = len(mesh.vertices)
    for i in range(sides):
        a = 2 * math.pi * i / sides
        d = math.cos(a) * u + math.sin(a) * v
        mesh.vertices.append(tuple(start + radius0 * d))
    for i in range(sides):
        a = 2 * math.pi * i / sides
        d = math.cos(a) * u + math.sin(a) * v
        mesh.vertices.append(tuple(end + radius1 * d))
    for i in range(sides):
        j = (i + 1) % sides
        mesh.faces.append((base + i + 1, base + j + 1, base + sides + i + 1))
        mesh.faces.append((base + j + 1, base + sides + j + 1, base + sides + i + 1))


def rot_axis(axis: np.ndarray, angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    x, y, z = unit(axis)
    return np.array(
        [
            [c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
            [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
            [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)],
        ],
        dtype=float,
    )


def make_ifs_tree(depth: int = 7) -> Mesh:
    mesh = Mesh([], [])

    def rec(pos: np.ndarray, direction: np.ndarray, length: float, radius: float, level: int) -> None:
        end = pos + unit(direction) * length
        add_cylinder(mesh, pos, end, radius, radius * 0.68)
        if level <= 0:
            return
        u, _, w = basis_from_axis(direction)
        angles = [-0.55, 0.42, 0.20]
        twists = [0.0, 2.3, 4.4]
        scales = [0.72, 0.65, 0.50]
        for angle, twist, scale in zip(angles, twists, scales):
            branch_dir = rot_axis(w, twist) @ (rot_axis(u, angle) @ w)
            rec(end, branch_dir, length * scale, radius * 0.72, level - 1)

    rec(np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0]), 1.0, 0.055, depth)
    return mesh


def make_lsystem_branch(iterations: int = 4) -> Mesh:
    axiom = "F"
    rule = "F[+F][-F][&F][^F]F"
    s = axiom
    for _ in range(iterations):
        s = "".join(rule if c == "F" else c for c in s)

    mesh = Mesh([], [])
    pos = np.array([0.0, 0.0, 0.0])
    heading = np.array([0.0, 0.0, 1.0])
    stack: list[tuple[np.ndarray, np.ndarray, float]] = []
    step = 0.16
    radius = 0.025
    angle = 0.48
    for c in s:
        if c == "F":
            new = pos + heading * step
            add_cylinder(mesh, pos, new, radius, radius * 0.96, sides=8)
            pos = new
        elif c == "[":
            stack.append((pos.copy(), heading.copy(), radius))
            radius *= 0.72
        elif c == "]":
            pos, heading, radius = stack.pop()
        elif c == "+":
            heading = rot_axis(np.array([0.0, 1.0, 0.0]), angle) @ heading
        elif c == "-":
            heading = rot_axis(np.array([0.0, 1.0, 0.0]), -angle) @ heading
        elif c == "&":
            heading = rot_axis(np.array([1.0, 0.0, 0.0]), angle) @ heading
        elif c == "^":
            heading = rot_axis(np.array([1.0, 0.0, 0.0]), -angle) @ heading
    return mesh


def make_dla_cluster(n_particles: int = 900, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    occupied = {(0, 0, 0)}
    dirs = np.array(
        [
            [1, 0, 0],
            [-1, 0, 0],
            [0, 1, 0],
            [0, -1, 0],
            [0, 0, 1],
            [0, 0, -1],
        ],
        dtype=int,
    )
    spawn_r = 8
    kill_r = 20
    while len(occupied) < n_particles:
        theta = rng.uniform(0, 2 * math.pi)
        phi = rng.uniform(0.2, math.pi - 0.2)
        p = np.array(
            [
                round(spawn_r * math.sin(phi) * math.cos(theta)),
                round(spawn_r * math.sin(phi) * math.sin(theta)),
                round(spawn_r * math.cos(phi)),
            ],
            dtype=int,
        )
        for _ in range(5000):
            if tuple(p) in occupied:
                break
            if np.linalg.norm(p) > kill_r:
                break
            if any(tuple(p + d) in occupied for d in dirs):
                occupied.add(tuple(p))
                r = int(np.linalg.norm(p)) + 8
                spawn_r = max(spawn_r, min(28, r))
                kill_r = max(kill_r, spawn_r + 12)
                break
            p = p + dirs[rng.integers(0, len(dirs))]
    pts = np.array(sorted(occupied), dtype=float)
    pts = pts / max(float(np.max(np.abs(pts))), 1.0)
    return pts


def points_to_cube_mesh(points: np.ndarray, radius: float = 0.025) -> Mesh:
    mesh = Mesh([], [])
    cube = np.array(
        [
            [-1, -1, -1],
            [1, -1, -1],
            [1, 1, -1],
            [-1, 1, -1],
            [-1, -1, 1],
            [1, -1, 1],
            [1, 1, 1],
            [-1, 1, 1],
        ],
        dtype=float,
    )
    faces = [(1, 2, 3), (1, 3, 4), (5, 8, 7), (5, 7, 6), (1, 5, 6), (1, 6, 2), (2, 6, 7), (2, 7, 3), (3, 7, 8), (3, 8, 4), (4, 8, 5), (4, 5, 1)]
    for p in points:
        base = len(mesh.vertices)
        for v in cube:
            mesh.vertices.append(tuple(p + radius * v))
        for f in faces:
            mesh.faces.append(tuple(base + i for i in f))
    return mesh


def write_obj(path: Path, mesh: Mesh) -> None:
    with path.open("w") as f:
        for v in mesh.vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        for face in mesh.faces:
            f.write(f"f {face[0]} {face[1]} {face[2]}\n")


def write_ply_points(path: Path, points: np.ndarray) -> None:
    with path.open("w") as f:
        f.write("ply\nformat ascii 1.0\n")
        f.write(f"element vertex {len(points)}\n")
        f.write("property float x\nproperty float y\nproperty float z\nend_header\n")
        for p in points:
            f.write(f"{p[0]:.6f} {p[1]:.6f} {p[2]:.6f}\n")


def metrics(mesh: Mesh, points: np.ndarray | None = None) -> dict:
    verts = np.array(mesh.vertices, dtype=float) if mesh.vertices else np.zeros((0, 3))
    if points is None:
        points = verts
    bbox_min = points.min(axis=0).tolist() if len(points) else [0, 0, 0]
    bbox_max = points.max(axis=0).tolist() if len(points) else [0, 0, 0]
    return {
        "vertices": len(mesh.vertices),
        "faces": len(mesh.faces),
        "points": int(len(points)),
        "bbox_min": bbox_min,
        "bbox_max": bbox_max,
        "bbox_extent": (np.array(bbox_max) - np.array(bbox_min)).tolist(),
    }


def render_mesh(path: Path, mesh: Mesh, title: str) -> None:
    verts = np.array(mesh.vertices, dtype=float)
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection="3d")
    if len(verts):
        step = max(1, len(verts) // 9000)
        ax.scatter(verts[::step, 0], verts[::step, 1], verts[::step, 2], s=0.25, c=verts[::step, 2], cmap="viridis")
        center = (verts.min(axis=0) + verts.max(axis=0)) / 2
        span = max((verts.max(axis=0) - verts.min(axis=0)).max(), 1e-3)
        ax.set_xlim(center[0] - span / 2, center[0] + span / 2)
        ax.set_ylim(center[1] - span / 2, center[1] + span / 2)
        ax.set_zlim(center[2] - span / 2, center[2] + span / 2)
    ax.set_title(title)
    ax.set_axis_off()
    ax.view_init(22, -55)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def render_points(path: Path, points: np.ndarray, title: str) -> None:
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=3, c=np.linalg.norm(points, axis=1), cmap="magma")
    ax.set_title(title)
    ax.set_axis_off()
    ax.view_init(25, -45)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    outputs = {}

    tree = make_ifs_tree()
    write_obj(args.out / "ifs_branch_tree.obj", tree)
    render_mesh(args.out / "ifs_branch_tree.png", tree, "IFS recursive branch baseline")
    outputs["ifs_branch_tree"] = metrics(tree)

    lsys = make_lsystem_branch()
    write_obj(args.out / "lsystem_branch.obj", lsys)
    render_mesh(args.out / "lsystem_branch.png", lsys, "L-system branch baseline")
    outputs["lsystem_branch"] = metrics(lsys)

    dla_pts = make_dla_cluster()
    dla_mesh = points_to_cube_mesh(dla_pts)
    write_ply_points(args.out / "dla_cluster_points.ply", dla_pts)
    write_obj(args.out / "dla_cluster_voxels.obj", dla_mesh)
    render_points(args.out / "dla_cluster_points.png", dla_pts, "DLA crystal cluster baseline")
    outputs["dla_cluster"] = metrics(dla_mesh, dla_pts)

    with (args.out / "metrics.json").open("w") as f:
        json.dump(outputs, f, indent=2)
    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()

