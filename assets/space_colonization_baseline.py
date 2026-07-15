#!/usr/bin/env python3
"""Traditional space-colonization baselines for recursive growth comparisons."""

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
    return v / n if n > 1e-9 else v


def basis_from_axis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = unit(axis)
    seed = np.array([0.0, 0.0, 1.0]) if abs(w[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = unit(np.cross(w, seed))
    v = unit(np.cross(w, u))
    return u, v, w


def add_cylinder(mesh: Mesh, start: np.ndarray, end: np.ndarray, radius0: float, radius1: float, sides: int = 10) -> None:
    axis = end - start
    if float(np.linalg.norm(axis)) < 1e-9:
        return
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


def write_obj(path: Path, mesh: Mesh) -> None:
    with path.open("w") as f:
        for v in mesh.vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        for a, b, c in mesh.faces:
            f.write(f"f {a} {b} {c}\n")


def sample_attractors(case: str, count: int, rng: np.random.Generator) -> np.ndarray:
    points = []
    while len(points) < count:
        p = rng.uniform(-1.0, 1.0, size=3)
        if case == "tree_canopy":
            q = np.array([p[0] * 0.70, p[1] * 0.70, 0.55 + p[2] * 0.45])
            if ((q[0] / 0.72) ** 2 + (q[1] / 0.72) ** 2 + ((q[2] - 0.55) / 0.48) ** 2) <= 1:
                points.append(q)
        elif case == "root_vine":
            q = np.array([p[0] * 0.85, -0.15 + p[1] * 0.32, p[2] * 0.85])
            if ((q[0] / 0.88) ** 2 + ((q[1] + 0.15) / 0.35) ** 2 + (q[2] / 0.88) ** 2) <= 1:
                points.append(q)
        elif case == "bush_shell":
            q = np.array([p[0] * 0.75, p[1] * 0.75, p[2] * 0.75])
            r = float(np.linalg.norm(q))
            if 0.35 <= r <= 0.78 and q[2] > -0.35:
                points.append(q)
        else:
            raise ValueError(f"unknown case {case}")
    return np.asarray(points, dtype=float)


def initial_nodes(case: str) -> tuple[list[np.ndarray], list[int], list[int]]:
    if case == "tree_canopy":
        pts = [
            np.array([0.0, 0.0, -0.65]),
            np.array([0.0, 0.0, -0.38]),
            np.array([0.0, 0.0, -0.10]),
            np.array([0.0, 0.0, 0.16]),
            np.array([0.0, 0.0, 0.34]),
        ]
    elif case == "root_vine":
        pts = [np.array([0.0, 0.0, 0.0]), np.array([0.0, -0.05, 0.16]), np.array([0.0, -0.08, 0.32])]
    else:
        pts = [np.array([0.0, 0.0, -0.25])]
    parents = [-1] + list(range(len(pts) - 1))
    depths = list(range(len(pts)))
    return pts, parents, depths


def grow_space_colonization(
    case: str,
    attractor_count: int,
    iterations: int,
    influence_radius: float,
    kill_radius: float,
    step_size: float,
    seed: int,
) -> dict:
    rng = np.random.default_rng(seed)
    attractors = sample_attractors(case, attractor_count, rng)
    nodes, parents, depths = initial_nodes(case)
    alive = np.ones(len(attractors), dtype=bool)

    for _ in range(iterations):
        active_attr = np.nonzero(alive)[0]
        if len(active_attr) == 0:
            break
        node_arr = np.asarray(nodes, dtype=float)
        attr_arr = attractors[active_attr]
        dist = np.linalg.norm(attr_arr[:, None, :] - node_arr[None, :, :], axis=2)
        near_any = dist.min(axis=1) <= influence_radius
        kill = dist.min(axis=1) <= kill_radius
        alive[active_attr[kill]] = False
        active_attr = active_attr[near_any & ~kill]
        if len(active_attr) == 0:
            continue
        dist = np.linalg.norm(attractors[active_attr][:, None, :] - node_arr[None, :, :], axis=2)
        nearest = dist.argmin(axis=1)
        proposals: dict[int, list[np.ndarray]] = {}
        for attr_idx, node_idx in zip(active_attr, nearest):
            proposals.setdefault(int(node_idx), []).append(unit(attractors[attr_idx] - nodes[int(node_idx)]))
        existing = np.asarray(nodes, dtype=float)
        for node_idx, dirs in proposals.items():
            direction = unit(np.mean(np.asarray(dirs), axis=0))
            candidate = nodes[node_idx] + direction * step_size
            if np.linalg.norm(existing - candidate, axis=1).min(initial=10.0) < step_size * 0.45:
                continue
            nodes.append(candidate)
            parents.append(node_idx)
            depths.append(depths[node_idx] + 1)

    return {
        "case": case,
        "nodes": [p.tolist() for p in nodes],
        "parents": parents,
        "depths": depths,
        "attractors": attractors.tolist(),
        "alive_attractors": int(alive.sum()),
        "covered_attractors": int((~alive).sum()),
        "params": {
            "attractor_count": attractor_count,
            "iterations": iterations,
            "influence_radius": influence_radius,
            "kill_radius": kill_radius,
            "step_size": step_size,
            "seed": seed,
        },
    }


def skeleton_to_mesh(result: dict, radius: float, taper: float) -> Mesh:
    nodes = [np.asarray(p, dtype=float) for p in result["nodes"]]
    parents = result["parents"]
    depths = result["depths"]
    mesh = Mesh([], [])
    max_depth = max(depths) if depths else 1
    for idx, parent in enumerate(parents):
        if parent < 0:
            continue
        d0 = depths[parent] / max(max_depth, 1)
        d1 = depths[idx] / max(max_depth, 1)
        r0 = radius * (1.0 - taper * d0)
        r1 = radius * (1.0 - taper * d1)
        add_cylinder(mesh, nodes[parent], nodes[idx], max(r0, radius * 0.22), max(r1, radius * 0.16))
    return mesh


def graph_metrics(result: dict, mesh: Mesh) -> dict:
    nodes = np.asarray(result["nodes"], dtype=float)
    parents = np.asarray(result["parents"], dtype=int)
    children = {i: [] for i in range(len(nodes))}
    lengths = []
    for i, p in enumerate(parents):
        if p >= 0:
            children[int(p)].append(i)
            lengths.append(float(np.linalg.norm(nodes[i] - nodes[p])))
    degree = np.asarray([len(children[i]) + (0 if parents[i] < 0 else 1) for i in range(len(nodes))], dtype=int)
    tips = int(np.sum(degree == 1)) if len(nodes) > 1 else 0
    branch_nodes = int(np.sum([len(v) >= 2 for v in children.values()]))
    bbox_min = nodes.min(axis=0).tolist() if len(nodes) else [0, 0, 0]
    bbox_max = nodes.max(axis=0).tolist() if len(nodes) else [0, 0, 0]
    return {
        "nodes": int(len(nodes)),
        "segments": int(max(len(nodes) - 1, 0)),
        "tips": tips,
        "branch_nodes": branch_nodes,
        "max_depth": int(max(result["depths"]) if result["depths"] else 0),
        "total_length": float(np.sum(lengths)),
        "mean_segment_length": float(np.mean(lengths)) if lengths else 0.0,
        "covered_attractors": int(result["covered_attractors"]),
        "alive_attractors": int(result["alive_attractors"]),
        "coverage_ratio": float(result["covered_attractors"] / max(len(result["attractors"]), 1)),
        "mesh_vertices": int(len(mesh.vertices)),
        "mesh_faces": int(len(mesh.faces)),
        "bbox_min": bbox_min,
        "bbox_max": bbox_max,
        "bbox_extent": (np.asarray(bbox_max) - np.asarray(bbox_min)).tolist(),
    }


def render(path: Path, result: dict, mesh: Mesh) -> None:
    nodes = np.asarray(result["nodes"], dtype=float)
    attractors = np.asarray(result["attractors"], dtype=float)
    parents = result["parents"]
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection="3d")
    if len(attractors):
        ax.scatter(attractors[:, 0], attractors[:, 1], attractors[:, 2], s=1.0, c="#bbbbbb", alpha=0.22)
    for i, p in enumerate(parents):
        if p >= 0:
            seg = np.stack([nodes[p], nodes[i]], axis=0)
            ax.plot(seg[:, 0], seg[:, 1], seg[:, 2], color="#2b6c5a", linewidth=0.8)
    if len(nodes):
        ax.scatter(nodes[:, 0], nodes[:, 1], nodes[:, 2], s=3, c="#0c3b2e")
        center = (nodes.min(0) + nodes.max(0)) / 2
        span = max(float((nodes.max(0) - nodes.min(0)).max()), 1e-3)
        ax.set_xlim(center[0] - span / 2, center[0] + span / 2)
        ax.set_ylim(center[1] - span / 2, center[1] + span / 2)
        ax.set_zlim(center[2] - span / 2, center[2] + span / 2)
    ax.set_axis_off()
    ax.view_init(24, -45)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def run_case(args: argparse.Namespace, case: str) -> dict:
    result = grow_space_colonization(
        case=case,
        attractor_count=args.attractors,
        iterations=args.iterations,
        influence_radius=args.influence_radius,
        kill_radius=args.kill_radius,
        step_size=args.step_size,
        seed=args.seed + hash(case) % 10000,
    )
    mesh = skeleton_to_mesh(result, radius=args.radius, taper=args.taper)
    case_dir = args.out / case
    case_dir.mkdir(parents=True, exist_ok=True)
    write_obj(case_dir / "space_colonization.obj", mesh)
    render(case_dir / "space_colonization_preview.png", result, mesh)
    (case_dir / "skeleton.json").write_text(json.dumps(result, indent=2))
    metrics = graph_metrics(result, mesh)
    (case_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    return {"case": case, "mesh": str(case_dir / "space_colonization.obj"), "preview": str(case_dir / "space_colonization_preview.png"), **metrics}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cases", nargs="+", default=["tree_canopy", "root_vine", "bush_shell"])
    parser.add_argument("--attractors", type=int, default=1600)
    parser.add_argument("--iterations", type=int, default=260)
    parser.add_argument("--influence-radius", type=float, default=0.24)
    parser.add_argument("--kill-radius", type=float, default=0.055)
    parser.add_argument("--step-size", type=float, default=0.045)
    parser.add_argument("--radius", type=float, default=0.030)
    parser.add_argument("--taper", type=float, default=0.78)
    parser.add_argument("--seed", type=int, default=1307)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rows = [run_case(args, case) for case in args.cases]
    (args.out / "summary.json").write_text(json.dumps({"rows": rows, "params": vars(args)}, indent=2, default=str))
    print(json.dumps({"rows": rows}, indent=2))


if __name__ == "__main__":
    main()
