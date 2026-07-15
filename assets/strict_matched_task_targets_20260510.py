#!/usr/bin/env python3
"""Emit strict matched-task traditional baseline OBJ targets.

This script is intentionally local CPU only.  It writes traditional baseline
meshes plus manifest files for exact matched-task PS-RSLG comparisons; it does
not render, texture, or call any GPU pipeline.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import baseline_matrix_20260509 as bm
import procedural_baselines as pb
import space_colonization_baseline as scb


@dataclass(frozen=True)
class Target:
    case_id: str
    family: str
    target_category: str
    recursive_mode: str
    mesh: pb.Mesh
    controls: dict


def add_uv_sphere(mesh: pb.Mesh, center: np.ndarray, radius: float, segments: int = 10, rings: int = 6) -> None:
    base = len(mesh.vertices)
    center = np.asarray(center, dtype=float)
    for r in range(rings + 1):
        phi = math.pi * r / rings
        for s in range(segments):
            theta = 2.0 * math.pi * s / segments
            point = center + radius * np.array(
                [math.sin(phi) * math.cos(theta), math.sin(phi) * math.sin(theta), math.cos(phi)],
                dtype=float,
            )
            mesh.vertices.append(tuple(point))
    for r in range(rings):
        for s in range(segments):
            a = base + r * segments + s
            b = base + r * segments + (s + 1) % segments
            c = base + (r + 1) * segments + s
            d = base + (r + 1) * segments + (s + 1) % segments
            mesh.faces.append((a + 1, c + 1, b + 1))
            mesh.faces.append((b + 1, c + 1, d + 1))


def children_from_parents(parents: list[int]) -> dict[int, list[int]]:
    children = {i: [] for i in range(len(parents))}
    for idx, parent in enumerate(parents):
        if parent >= 0:
            children[parent].append(idx)
    return children


def skeleton_to_tube_mesh(
    nodes: list[np.ndarray],
    parents: list[int],
    base_radius: float,
    taper: float,
    sides: int = 10,
    tip_spheres: bool = False,
) -> pb.Mesh:
    mesh = pb.Mesh([], [])
    depths = bm.graph_depths(parents)
    child_map = children_from_parents(parents)
    max_depth = max(depths) if depths else 1
    for idx, parent in enumerate(parents):
        if parent < 0:
            continue
        f0 = depths[parent] / max(max_depth, 1)
        f1 = depths[idx] / max(max_depth, 1)
        r0 = max(base_radius * (1.0 - taper * f0), base_radius * 0.18)
        r1 = max(base_radius * (1.0 - taper * f1), base_radius * 0.12)
        pb.add_cylinder(mesh, np.asarray(nodes[parent]), np.asarray(nodes[idx]), r0, r1, sides=sides)
    if tip_spheres:
        for idx, node in enumerate(nodes):
            if idx != 0 and not child_map[idx]:
                add_uv_sphere(mesh, np.asarray(node), base_radius * 1.15, segments=9, rings=5)
    return mesh


def mesh_stats(mesh: pb.Mesh) -> dict:
    verts = np.asarray(mesh.vertices, dtype=float) if mesh.vertices else np.zeros((0, 3), dtype=float)
    bbox_min = verts.min(axis=0).tolist() if len(verts) else [0.0, 0.0, 0.0]
    bbox_max = verts.max(axis=0).tolist() if len(verts) else [0.0, 0.0, 0.0]
    extent = (np.asarray(bbox_max) - np.asarray(bbox_min)).tolist()
    return {
        "vertices": len(mesh.vertices),
        "faces": len(mesh.faces),
        "bbox_min": bbox_min,
        "bbox_max": bbox_max,
        "bbox_extent": extent,
    }


def transform_mesh(mesh: pb.Mesh, scale: np.ndarray, translate: np.ndarray | None = None) -> pb.Mesh:
    translate = np.zeros(3, dtype=float) if translate is None else np.asarray(translate, dtype=float)
    out = pb.Mesh([], list(mesh.faces))
    for vertex in mesh.vertices:
        out.vertices.append(tuple(np.asarray(vertex, dtype=float) * scale + translate))
    return out


def merge_meshes(meshes: list[pb.Mesh]) -> pb.Mesh:
    out = pb.Mesh([], [])
    for mesh in meshes:
        offset = len(out.vertices)
        out.vertices.extend(mesh.vertices)
        for a, b, c in mesh.faces:
            out.faces.append((a + offset, b + offset, c + offset))
    return out


def lsystem_climbing_vine(iterations: int = 6, seed: int = 20260510) -> pb.Mesh:
    rng = np.random.default_rng(seed)
    nodes = [np.zeros(3, dtype=float)]
    parents = [-1]
    parent = 0
    for level in range(1, iterations + 1):
        theta = level * 0.82
        step = np.array([math.cos(theta) * 2.2, math.sin(theta) * 2.2, 5.2])
        nodes.append(nodes[parent] + step)
        current = len(nodes) - 1
        parents.append(parent)
        for sign in (-1, 1):
            side = pb.unit(np.array([math.cos(theta + sign * 1.35), math.sin(theta + sign * 1.35), 0.15]))
            tip = nodes[current] + side * (2.8 + 0.35 * level) + rng.normal(0, 0.12, 3)
            nodes.append(tip)
            parents.append(current)
            if level >= 3:
                nodes.append(tip + side * 1.35 + np.array([0.0, 0.0, 0.55]))
                parents.append(len(nodes) - 2)
        parent = current
    return skeleton_to_tube_mesh(nodes, parents, base_radius=0.45, taper=0.62, sides=10, tip_spheres=True)


def make_lsystem_targets(seed: int) -> list[Target]:
    tree_nodes, tree_parents = bm.lsystem_case("tree", depth=5, seed=seed)
    root_nodes, root_parents = bm.lsystem_case("root", depth=5, seed=seed + 17)
    return [
        Target(
            "lsys_pine_canopy_d5",
            "L-system",
            "pine/tree canopy",
            "symbolic turtle branch rewriting",
            skeleton_to_tube_mesh(tree_nodes, tree_parents, base_radius=0.95, taper=0.76, sides=10, tip_spheres=True),
            {"depth": 5, "source": "baseline_matrix_20260509.lsystem_case(tree)"},
        ),
        Target(
            "lsys_root_fan_d5",
            "L-system",
            "root fan",
            "symbolic turtle root branching with downward tropism",
            skeleton_to_tube_mesh(root_nodes, root_parents, base_radius=0.82, taper=0.70, sides=10, tip_spheres=True),
            {"depth": 5, "source": "baseline_matrix_20260509.lsystem_case(root)"},
        ),
        Target(
            "lsys_climbing_vine_d6",
            "L-system",
            "climbing vine",
            "curling main chain with recursive tendrils",
            lsystem_climbing_vine(iterations=6, seed=seed + 29),
            {"iterations": 6, "curl_step_radians": 0.82, "seed": seed + 29},
        ),
    ]


def make_space_targets(seed: int) -> list[Target]:
    specs = [
        ("sc_tree_crown_260", "tree_canopy", "tree crown", 1600, 260, 0.24, 0.055, 0.045, 0.030),
        ("sc_root_network_260", "root_vine", "root network", 1600, 260, 0.24, 0.055, 0.045, 0.030),
        ("sc_bush_shell_220", "bush_shell", "bush shell", 1400, 220, 0.23, 0.060, 0.043, 0.028),
    ]
    rows: list[Target] = []
    for idx, (case_id, sc_case, category, attractors, iterations, influence, kill, step, radius) in enumerate(specs):
        result = scb.grow_space_colonization(
            case=sc_case,
            attractor_count=attractors,
            iterations=iterations,
            influence_radius=influence,
            kill_radius=kill,
            step_size=step,
            seed=seed + 100 + idx * 41,
        )
        rows.append(
            Target(
                case_id,
                "Space colonization",
                category,
                "attractor competition with influence/kill radii",
                scb.skeleton_to_mesh(result, radius=radius, taper=0.78),
                {
                    "case": sc_case,
                    "attractors": attractors,
                    "iterations": iterations,
                    "influence_radius": influence,
                    "kill_radius": kill,
                    "step_size": step,
                    "seed": seed + 100 + idx * 41,
                    "covered_attractors": result["covered_attractors"],
                },
            )
        )
    return rows


def cube_mesh_from_points(points: np.ndarray, radius: float = 0.035) -> pb.Mesh:
    return pb.points_to_cube_mesh(points, radius=radius)


def make_frontier_sheet(seed: int, particles: int = 700) -> np.ndarray:
    rng = np.random.default_rng(seed)
    occupied = {(x, 0, 0) for x in range(-8, 9)}
    dirs = np.asarray([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], dtype=int)
    while len(occupied) < particles:
        p = np.array([rng.integers(-16, 17), rng.integers(10, 24), rng.integers(-4, 5)], dtype=int)
        for _ in range(900):
            if any(tuple(p + d) in occupied for d in dirs):
                occupied.add(tuple(p))
                break
            bias = np.array([0, -1, 0]) if rng.random() < 0.42 else dirs[rng.integers(0, len(dirs))]
            p = p + bias
            if abs(p[0]) > 28 or p[1] < -4 or p[1] > 30 or abs(p[2]) > 9:
                break
    pts = np.asarray(sorted(occupied), dtype=float)
    pts[:, 0] /= 28.0
    pts[:, 1] = pts[:, 1] / 24.0 - 0.15
    pts[:, 2] /= 10.0
    return pts


def make_dla_targets(seed: int) -> list[Target]:
    coral = pb.make_dla_cluster(n_particles=900, seed=seed % 10000)
    crystal = pb.make_dla_cluster(n_particles=800, seed=(seed + 313) % 10000)
    crystal = crystal * np.array([1.35, 0.70, 1.05])
    frontier = make_frontier_sheet(seed + 719, particles=700)
    return [
        Target(
            "dla_coral_cluster_900",
            "DLA/frontier",
            "coral porous cluster",
            "random-walk accretive particle attachment",
            cube_mesh_from_points(coral, radius=0.026),
            {"particles": 900, "seed": seed % 10000, "neighborhood": "6n", "surfacing": "cube_per_hit"},
        ),
        Target(
            "dla_aniso_crystal_800",
            "DLA/frontier",
            "anisotropic crystal dendrite",
            "biased accretive particle attachment with anisotropic scaling",
            cube_mesh_from_points(crystal, radius=0.025),
            {"particles": 800, "seed": (seed + 313) % 10000, "anisotropic_scale": [1.35, 0.70, 1.05]},
        ),
        Target(
            "dla_frontier_sheet_700",
            "DLA/frontier",
            "frontier sheet dendrite",
            "boundary-seeded accretive frontier growth",
            cube_mesh_from_points(frontier, radius=0.030),
            {"particles": 700, "seed": seed + 719, "seed_shape": "line_strip", "growth_bias": "toward boundary"},
        ),
    ]


def radial_ornament(order: int = 8, depth: int = 4) -> pb.Mesh:
    meshes: list[pb.Mesh] = []
    motif = pb.Mesh([], [])
    pb.add_cylinder(motif, np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0]), 0.05, 0.025, sides=8)
    add_uv_sphere(motif, np.array([1.0, 0.0, 0.0]), 0.09, segments=8, rings=4)
    for level in range(depth):
        scale = 1.0 / (1.0 + 0.55 * level)
        radius = 1.2 * level
        for k in range(order):
            theta = 2.0 * math.pi * k / order + 0.22 * level
            c, s = math.cos(theta), math.sin(theta)
            rot = np.asarray([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]], dtype=float)
            copy = pb.Mesh([], list(motif.faces))
            offset = np.array([math.cos(theta) * radius, math.sin(theta) * radius, level * 0.10])
            for vertex in motif.vertices:
                copy.vertices.append(tuple(rot @ (np.asarray(vertex) * scale) + offset))
            meshes.append(copy)
    return merge_meshes(meshes)


def fractal_lattice(depth: int = 4) -> pb.Mesh:
    meshes: list[pb.Mesh] = []
    base = pb.Mesh([], [])
    pb.add_cylinder(base, np.array([-0.5, 0.0, 0.0]), np.array([0.5, 0.0, 0.0]), 0.045, 0.045, sides=8)
    pb.add_cylinder(base, np.array([0.0, -0.5, 0.0]), np.array([0.0, 0.5, 0.0]), 0.045, 0.045, sides=8)
    pb.add_cylinder(base, np.array([0.0, 0.0, -0.5]), np.array([0.0, 0.0, 0.5]), 0.045, 0.045, sides=8)
    offsets = [np.array([0.0, 0.0, 0.0])]
    for level in range(depth):
        new_offsets = []
        scale = 0.72**level
        for off in offsets:
            meshes.append(transform_mesh(base, np.array([scale, scale, scale]), off))
            step = 1.1 * scale
            for axis in np.eye(3):
                new_offsets.append(off + axis * step)
                new_offsets.append(off - axis * step)
        offsets = new_offsets[: 6 * (level + 1)]
    return merge_meshes(meshes)


def make_ifs_targets(seed: int) -> list[Target]:
    del seed
    branch = pb.make_ifs_tree(depth=6)
    return [
        Target(
            "ifs_branch_tree_d6",
            "IFS/transform",
            "recursive branch tree",
            "contractive affine transform-copy branching",
            branch,
            {"depth": 6, "transforms": "make_ifs_tree default 3-map branch system"},
        ),
        Target(
            "ifs_radial_ornament_o8_d4",
            "IFS/transform",
            "radial fractal ornament",
            "radial transform-copy with scale decay",
            radial_ornament(order=8, depth=4),
            {"order": 8, "depth": 4, "scale_decay": "1/(1+0.55*level)"},
        ),
        Target(
            "ifs_fractal_lattice_d4",
            "IFS/transform",
            "fractal lattice ornament",
            "affine lattice transform-copy with recursive basis offsets",
            fractal_lattice(depth=4),
            {"depth": 4, "basis": "axis-aligned 3D cross motif"},
        ),
    ]


def build_targets(seed: int) -> list[Target]:
    return make_lsystem_targets(seed) + make_space_targets(seed) + make_dla_targets(seed) + make_ifs_targets(seed)


def materialize(targets: list[Target], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    case_lines = []
    for target in targets:
        case_dir = out / target.case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        mesh_path = case_dir / "traditional_target.obj"
        pb.write_obj(mesh_path, target.mesh)
        stats = mesh_stats(target.mesh)
        row = {
            "case_id": target.case_id,
            "family": target.family,
            "target_category": target.target_category,
            "recursive_mode": target.recursive_mode,
            "obj_path": str(mesh_path),
            "vertices": stats["vertices"],
            "faces": stats["faces"],
            "bbox_extent": json.dumps(stats["bbox_extent"]),
            "controls": json.dumps(target.controls, ensure_ascii=False, sort_keys=True),
        }
        rows.append(row)
        case_lines.append(f"{target.case_id}={mesh_path}")

    fields = ["case_id", "family", "target_category", "recursive_mode", "obj_path", "vertices", "faces", "bbox_extent", "controls"]
    with (out / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (out / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "cases.txt").write_text("\n".join(case_lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out), "targets": len(rows), "manifest": str(out / "manifest.csv"), "cases": str(out / "cases.txt")}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT_DIR / "results" / "strict_matched_task_targets_20260510")
    parser.add_argument("--seed", type=int, default=20260510)
    args = parser.parse_args()
    materialize(build_targets(args.seed), args.out)


if __name__ == "__main__":
    main()
