#!/usr/bin/env python3
"""Connectivity-first strict matched candidates for remote Trellis2 texturing.

This V3b batch is a direct response to the V3 pre-texture component audit.
V3 explores richer plant/crown detail, but several cases are assembled from
many independent tube/card surfaces.  V3b keeps the same strict target families
and controls, but converts plant/root/transform structures through a connected
occupancy scaffold before marching cubes.  The output meshes therefore pass a
single-component pre-texture gate before Trellis2 is allowed to texture them.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import baseline_matrix_20260509 as bm
import connected_scaffold_cases_v2_20260509 as scaffold
import procedural_baselines as pb
import space_colonization_baseline as scb
from strict_matched_psrslg_proxy_20260510 import ifs_tree_skeleton
from strict_visual_matched_cases_v3_20260510 import _mesh_stats, _write_guides, implicit_dla, lattice_from_scaffold


@dataclass
class Case:
    case_id: str
    family: str
    match_target: str
    recursive_mode: str
    mesh_path: str
    guide_image: str
    gpu_group: int
    seed: int
    controls: dict
    operators: list[str]
    claim_gate: str


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _normalize_nodes(nodes: list[np.ndarray], extent: float = 2.3) -> list[np.ndarray]:
    arr = np.asarray(nodes, dtype=float)
    mn, mx = arr.min(axis=0), arr.max(axis=0)
    center = (mn + mx) * 0.5
    scale = max(float((mx - mn).max()), 1e-6)
    return [(np.asarray(n, dtype=float) - center) * (extent / scale) for n in nodes]


def _children(parents: list[int]) -> dict[int, list[int]]:
    out = {i: [] for i in range(len(parents))}
    for i, p in enumerate(parents):
        if p >= 0:
            out.setdefault(p, []).append(i)
    return out


def _to_grid(p: np.ndarray, scale: float = 42.0) -> np.ndarray:
    return np.asarray(p, dtype=float) * scale


def _coords_to_single_mesh(points: set[tuple[int, int, int]]):
    coords = scaffold.largest_occupancy_component(scaffold.coords_array(points))
    mesh = scaffold.coords_to_mesh(coords)
    try:
        pieces = mesh.split(only_watertight=False)
        if pieces:
            mesh = max(pieces, key=lambda p: len(p.vertices))
    except Exception:
        pass
    return mesh, scaffold.occupancy_stats(coords)


def _skeleton_scaffold(
    nodes: list[np.ndarray],
    parents: list[int],
    base_radius: int,
    min_radius: int,
    taper: float,
    seed: int,
    garnish: str,
) -> tuple[object, dict]:
    rng = np.random.default_rng(seed)
    points: set[tuple[int, int, int]] = set()
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    children = _children(parents)
    grid_nodes = [_to_grid(np.asarray(n), 42.0) for n in nodes]
    for i, p in enumerate(parents):
        if p < 0:
            continue
        f = depths[i] / max(max_depth, 1)
        radius = max(int(round(base_radius * (1.0 - taper * f))), min_radius)
        scaffold.add_tube(points, grid_nodes[p], grid_nodes[i], radius)
        if len(children.get(i, [])) >= 2:
            scaffold.add_ball(points, grid_nodes[i], max(radius + 1, min_radius + 1))
    tips = [i for i in range(1, len(nodes)) if not children.get(i)]
    for idx in tips:
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        base = grid_nodes[idx]
        f = depths[idx] / max(max_depth, 1)
        if garnish == "pine":
            scaffold.add_ball(points, base, max(min_radius + 2, 4))
            for k in range(5):
                theta = 2 * math.pi * k / 5.0 + rng.normal(0, 0.12)
                side = np.array([math.cos(theta), math.sin(theta), rng.uniform(-0.15, 0.45)])
                side = _unit(0.5 * axis + side)
                end = base + side * rng.uniform(6.0, 10.0)
                scaffold.add_tube(points, base, end, max(min_radius, 1))
                scaffold.add_ball(points, end, max(min_radius, 2))
        elif garnish == "leaf":
            scaffold.add_ball(points, base, max(min_radius + 3, 4))
            for _ in range(3):
                side = _unit(rng.normal(0, 1, 3) + axis * 0.4)
                end = base + side * rng.uniform(5.0, 9.0)
                scaffold.add_tube(points, base, end, max(min_radius, 1))
                scaffold.add_ball(points, end, max(min_radius + 1, 3))
        elif garnish == "root":
            for _ in range(2):
                side = _unit(rng.normal(0, 1, 3) + np.array([0.0, 0.0, -0.45]) - 0.2 * axis)
                end = base + side * rng.uniform(6.0, 12.0) * (1.0 + 0.25 * f)
                scaffold.add_tube(points, base, end, max(min_radius, 1))
                scaffold.add_ball(points, end, max(min_radius, 2))
        else:
            scaffold.add_ball(points, base, max(min_radius + 1, 3))
    mesh, occ = _coords_to_single_mesh(points)
    return mesh, {"occupancy": occ, "node_count": len(nodes), "segment_count": max(len(nodes) - 1, 0), "garnish": garnish}


def layered_pine_nodes(seed: int) -> tuple[list[np.ndarray], list[int]]:
    rng = np.random.default_rng(seed)
    nodes = [np.array([0.0, 0.0, -1.05 + i * 0.24], dtype=float) for i in range(9)]
    parents = [-1] + list(range(8))
    for level in range(2, 9):
        base = nodes[level]
        radius = 0.58 * (1.0 - 0.075 * level)
        branch_count = 5 if level < 7 else 4
        for k in range(branch_count):
            theta = 2 * math.pi * k / branch_count + level * 0.35 + rng.normal(0, 0.04)
            out = _unit(np.array([math.cos(theta), math.sin(theta), 0.10 + 0.025 * level]))
            p1 = base + out * radius
            p2 = p1 + _unit(out + np.array([0, 0, 0.18])) * radius * 0.42
            i1 = len(nodes)
            nodes.append(p1)
            parents.append(level)
            nodes.append(p2)
            parents.append(i1)
    return nodes, parents


def lsys_vine_nodes(seed: int) -> tuple[list[np.ndarray], list[int]]:
    rng = np.random.default_rng(seed)
    nodes = [np.zeros(3, dtype=float)]
    parents = [-1]
    parent = 0
    for level in range(1, 7):
        theta = level * 0.82
        step = np.array([math.cos(theta) * 0.22, math.sin(theta) * 0.22, 0.52])
        nodes.append(nodes[parent] + step)
        current = len(nodes) - 1
        parents.append(parent)
        for sign in (-1, 1):
            side = _unit(np.array([math.cos(theta + sign * 1.35), math.sin(theta + sign * 1.35), 0.15]))
            tip = nodes[current] + side * (0.28 + 0.035 * level) + rng.normal(0, 0.012, 3)
            nodes.append(tip)
            parents.append(current)
            if level >= 3:
                nodes.append(tip + side * 0.16 + np.array([0.0, 0.0, 0.055]))
                parents.append(len(nodes) - 2)
        parent = current
    return _normalize_nodes(nodes, 2.45), parents


def sc_nodes(case: str, seed: int) -> tuple[list[np.ndarray], list[int], dict]:
    result = scb.grow_space_colonization(
        case=case,
        attractor_count=1700 if case != "bush_shell" else 1450,
        iterations=270 if case != "bush_shell" else 230,
        influence_radius=0.24,
        kill_radius=0.055 if case != "bush_shell" else 0.060,
        step_size=0.045,
        seed=seed,
    )
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in result["nodes"]], 2.35)
    parents = [int(p) for p in result["parents"]]
    controls = {
        "case": case,
        "attractor_count": 1700 if case != "bush_shell" else 1450,
        "iterations": 270 if case != "bush_shell" else 230,
        "covered_attractors": result.get("covered_attractors"),
        "alive_attractors": result.get("alive_attractors"),
    }
    return nodes, parents, controls


def radial_connected_gear(order: int = 8, depth: int = 4):
    points: set[tuple[int, int, int]] = set()
    center = np.zeros(3)
    scaffold.add_ball(points, center, 5)
    for level in range(depth):
        radius = 12 + level * 10
        z = level * 2
        phase = 0.18 * level
        for k in range(order):
            a0 = 2 * math.pi * k / order + phase
            a1 = 2 * math.pi * (k + 1) / order + phase
            p0 = np.array([math.cos(a0) * radius, math.sin(a0) * radius, z])
            p1 = np.array([math.cos(a1) * radius, math.sin(a1) * radius, z])
            scaffold.add_tube(points, p0, p1, max(2, 4 - level // 2))
            tooth = p0 + _unit(np.array([math.cos(a0), math.sin(a0), 0.12])) * (8 - level)
            scaffold.add_tube(points, p0, tooth, max(2, 3 - level // 2))
            if level > 0:
                pp = np.array([math.cos(a0 - 0.18) * (12 + (level - 1) * 10), math.sin(a0 - 0.18) * (12 + (level - 1) * 10), (level - 1) * 2])
                scaffold.add_tube(points, pp, p0, 2)
    mesh, occ = _coords_to_single_mesh(points)
    return mesh, {"occupancy": occ, "order": order, "depth": depth}


def export_mesh(path: Path, mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(path)


def build_cases(root: Path, out_dir: Path, seed: int) -> list[Case]:
    guides = _write_guides(out_dir)
    rows: list[Case] = []

    def add(case_id: str, family: str, target: str, mode: str, mesh, guide_key: str, gpu: int, s: int, controls: dict, operators: list[str], gate: str) -> None:
        path = out_dir / case_id / f"{case_id}.obj"
        export_mesh(path, mesh)
        controls = dict(controls)
        controls["mesh_stats"] = _mesh_stats(path)
        rows.append(Case(case_id, family, target, mode, str(path), guides[guide_key], gpu, s, controls, operators, gate))

    nodes, parents = layered_pine_nodes(seed + 1)
    mesh, ctl = _skeleton_scaffold(nodes, parents, 5, 2, 0.72, seed + 1, "pine")
    add("v3b_lsys_pine_canopy_d5_connected_conifer", "L-system", "lsys_pine_canopy_d5", "connected occupancy conifer rewriting with whorled branches", mesh, "conifer", 4, seed + 101, ctl, ["symbolic_rewrite", "connected_occupancy_projection", "masked_foliage_kernel"], "pre-texture single-component conifer candidate")

    nodes, parents = bm.lsystem_case("root", depth=5, seed=seed + 2)
    mesh, ctl = _skeleton_scaffold(_normalize_nodes(nodes, 2.55), parents, 5, 1, 0.80, seed + 2, "root")
    add("v3b_lsys_root_fan_d5_connected_hierarchy", "L-system", "lsys_root_fan_d5", "connected occupancy root fan rewriting", mesh, "root", 4, seed + 102, ctl, ["root_rewrite", "connected_root_projection", "root_hair_kernel"], "pre-texture single-component root fan candidate")

    nodes, parents = lsys_vine_nodes(seed + 3)
    mesh, ctl = _skeleton_scaffold(nodes, parents, 5, 2, 0.65, seed + 3, "leaf")
    add("v3b_lsys_climbing_vine_d6_connected_leafy", "L-system", "lsys_climbing_vine_d6", "connected curling vine rewrite with attached leaf kernels", mesh, "leaf", 4, seed + 103, ctl, ["curl_rewrite", "connected_tendril_projection", "leaf_kernel"], "pre-texture single-component vine candidate")

    for idx, (case, target, garnish, guide, gpu, label) in enumerate(
        [
            ("tree_canopy", "sc_tree_crown_260", "leaf", "leaf", 5, "tree_crown"),
            ("root_vine", "sc_root_network_260", "root", "root", 5, "root_network"),
            ("bush_shell", "sc_bush_shell_220", "leaf", "leaf", 5, "bush_shell"),
        ]
    ):
        nodes, parents, ctl0 = sc_nodes(case, seed + 11 + idx)
        mesh, ctl = _skeleton_scaffold(nodes, parents, 4, 1, 0.82, seed + 11 + idx, garnish)
        ctl.update(ctl0)
        add(f"v3b_sc_{label}_connected_{garnish}", "Space colonization", target, f"connected occupancy {case} attractor competition", mesh, guide, gpu, seed + 111 + idx, ctl, ["attractor_competition", "connected_occupancy_projection", f"{garnish}_kernel"], "pre-texture single-component SC candidate")

    mesh, ctl = implicit_dla(seed + 21, "coral", 900)
    add("v3b_dla_coral_cluster_900_implicit_single", "DLA/frontier", "dla_coral_cluster_900", "frontier-local implicit naturalization over DLA support", mesh, "coral", 6, seed + 121, ctl, ["frontier_attachment", "implicit_local_naturalization", "component_gate"], "DLA coral must stay continuous and porous")
    mesh, ctl = implicit_dla(seed + 22, "frontier_sheet", 740)
    add("v3b_dla_frontier_sheet_700_implicit_single", "DLA/frontier", "dla_frontier_sheet_700", "line-seeded frontier sheet implicit naturalization", mesh, "coral", 6, seed + 122, ctl, ["frontier_sheet_seed", "implicit_local_naturalization", "component_gate"], "frontier sheet must keep sheet silhouette")

    nodes, parents = ifs_tree_skeleton(depth=6)
    mesh, ctl = _skeleton_scaffold(_normalize_nodes(nodes, 2.45), parents, 5, 2, 0.78, seed + 31, "pine")
    add("v3b_ifs_branch_tree_d6_connected_orbit", "IFS/transform", "ifs_branch_tree_d6", "connected transform-copy branch orbit", mesh, "conifer", 7, seed + 131, ctl, ["transform_copy", "connected_orbit_projection", "tip_kernel"], "IFS branch must show transform hierarchy")
    mesh, ctl = radial_connected_gear(8, 4)
    add("v3b_ifs_radial_ornament_o8_d4_connected_gear", "IFS/transform", "ifs_radial_ornament_o8_d4", "connected radial transform-copy gear orbit", mesh, "gear", 7, seed + 132, ctl, ["radial_orbit", "connected_ring_cache", "symmetry_gate"], "radial order must remain visible")
    add("v3b_ifs_fractal_lattice_d4_pyrite_connected", "IFS/transform", "ifs_fractal_lattice_d4", "connected pyrite lattice transform cache", lattice_from_scaffold("pyrite"), "pyrite", 7, seed + 133, {"source": "pyrite_crystal_lattice_cluster"}, ["lattice_orbit", "transform_cache", "faceted_projection"], "lattice must remain readable and connected")
    return rows


def materialize(root: Path, out_dir: Path, seed: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    cases = build_cases(root, out_dir, seed)
    fields = ["case_id", "family", "match_target", "recursive_mode", "mesh_path", "guide_image", "gpu_group", "seed", "operators", "controls", "claim_gate"]
    rows = []
    for c in cases:
        rows.append(
            {
                "case_id": c.case_id,
                "family": c.family,
                "match_target": c.match_target,
                "recursive_mode": c.recursive_mode,
                "mesh_path": c.mesh_path,
                "guide_image": c.guide_image,
                "gpu_group": c.gpu_group,
                "seed": c.seed,
                "operators": json.dumps(c.operators, ensure_ascii=False),
                "controls": json.dumps(c.controls, ensure_ascii=False, sort_keys=True),
                "claim_gate": c.claim_gate,
            }
        )
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    (out_dir / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    for gpu in sorted({c.gpu_group for c in cases}):
        lines = [f"{c.case_id}|{c.mesh_path}|{c.guide_image}|{c.seed}" for c in cases if c.gpu_group == gpu]
        (out_dir / f"gpu{gpu}_cases.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary = {"out_dir": str(out_dir), "num_cases": len(cases), "manifest": str(out_dir / "manifest.csv")}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("RGG_ROOT", ROOT_DIR)))
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=20260510)
    args = parser.parse_args()
    materialize(args.root, args.out or (args.root / "inputs" / "strict_visual_matched_cases_v3b_connected_20260510"), args.seed)


if __name__ == "__main__":
    main()
