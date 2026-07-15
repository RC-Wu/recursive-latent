#!/usr/bin/env python3
"""Second strict-matched visual candidates with smoother, more readable geometry.

V1 proved that the remote Trellis2 path works, but visual audit exposed three
algorithmic failures: grape-like leaf balls, blocky DLA/coral voxels, and sparse
radial/IFS motifs.  V2 keeps the same procedural families but changes the
grammar token geometry before Trellis2 texturing:

* L-system / SC use visible branch tubes plus needle/leaflet strokes, not balls.
* DLA/frontier uses smooth capsule/sphere accretion support, not voxel cubes.
* IFS/radial uses connected transform orbits and larger motifs.
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
import procedural_baselines as pb
import space_colonization_baseline as scb
from strict_matched_psrslg_proxy_20260510 import ifs_tree_skeleton
from strict_matched_task_targets_20260510 import add_uv_sphere, make_frontier_sheet, skeleton_to_tube_mesh


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


def _normalize_nodes(nodes: list[np.ndarray], extent: float = 2.4) -> list[np.ndarray]:
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


def _merge(meshes: list[pb.Mesh]) -> pb.Mesh:
    out = pb.Mesh([], [])
    for mesh in meshes:
        offset = len(out.vertices)
        out.vertices.extend(mesh.vertices)
        for a, b, c in mesh.faces:
            out.faces.append((a + offset, b + offset, c + offset))
    return out


def _scale_mesh(mesh: pb.Mesh, scale: float) -> pb.Mesh:
    out = pb.Mesh([], list(mesh.faces))
    for v in mesh.vertices:
        out.vertices.append(tuple(np.asarray(v, dtype=float) * scale))
    return out


def _write_obj(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


def _guide(root: Path, name: str) -> str:
    return str(root / "public_guides_20260508" / "processed" / name)


def _mesh_stats(path: Path) -> dict:
    import trimesh

    mesh = trimesh.load(path, force="mesh", process=False)
    pieces = mesh.split(only_watertight=False)
    sizes = [len(p.vertices) for p in pieces] or [0]
    extent = mesh.bounds[1] - mesh.bounds[0] if len(mesh.vertices) else np.zeros(3)
    return {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "mesh_component_count": int(len(pieces)),
        "largest_mesh_component_vertex_ratio": float(max(sizes) / max(len(mesh.vertices), 1)),
        "bbox_extent": [float(x) for x in extent],
        "bbox_diag": float(np.linalg.norm(extent)),
        "surface_area": float(mesh.area),
    }


def add_needles(mesh: pb.Mesh, nodes: list[np.ndarray], parents: list[int], seed: int, density: int = 4, length: float = 0.13) -> None:
    rng = np.random.default_rng(seed)
    child = _children(parents)
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    for idx, node in enumerate(nodes):
        if idx == 0 or depths[idx] < max_depth * 0.45:
            continue
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(np.asarray(node) - np.asarray(nodes[parent]))
        u, v, _ = pb.basis_from_axis(axis)
        is_tip = not child.get(idx)
        count = density + (2 if is_tip else 0)
        for k in range(count):
            theta = 2 * math.pi * (k / max(count, 1)) + rng.normal(0, 0.12)
            d = _unit(0.55 * axis + math.cos(theta) * u + math.sin(theta) * v + rng.normal(0, 0.10, 3))
            p0 = np.asarray(node) + d * 0.015
            p1 = p0 + d * length * (1.0 + 0.35 * rng.random())
            pb.add_cylinder(mesh, p0, p1, 0.0065, 0.0018, sides=5)


def add_rootlets(mesh: pb.Mesh, nodes: list[np.ndarray], parents: list[int], seed: int) -> None:
    rng = np.random.default_rng(seed)
    depths = bm.graph_depths(parents)
    for idx, node in enumerate(nodes):
        if idx == 0 or depths[idx] < 2:
            continue
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(np.asarray(node) - np.asarray(nodes[parent]))
        u, v, _ = pb.basis_from_axis(axis)
        for _ in range(2 if depths[idx] > 3 else 1):
            d = _unit(-0.2 * axis + rng.normal(0, 0.65, 1)[0] * u + rng.normal(0, 0.65, 1)[0] * v + np.array([0, 0, -0.15]))
            p0 = np.asarray(node)
            p1 = p0 + d * rng.uniform(0.10, 0.25)
            pb.add_cylinder(mesh, p0, p1, 0.0045, 0.0015, sides=5)


def lsys_pine_needles(seed: int, depth: int = 5) -> pb.Mesh:
    nodes, parents = bm.lsystem_case("tree", depth=depth, seed=seed)
    nodes = _normalize_nodes(nodes, 2.55)
    mesh = skeleton_to_tube_mesh(nodes, parents, base_radius=0.060, taper=0.78, sides=12, tip_spheres=False)
    add_needles(mesh, nodes, parents, seed + 31, density=5, length=0.15)
    return mesh


def lsys_root_fan_fibers(seed: int, depth: int = 5) -> pb.Mesh:
    nodes, parents = bm.lsystem_case("root", depth=depth, seed=seed)
    nodes = _normalize_nodes(nodes, 2.45)
    mesh = skeleton_to_tube_mesh(nodes, parents, base_radius=0.055, taper=0.82, sides=10, tip_spheres=False)
    add_rootlets(mesh, nodes, parents, seed + 71)
    return mesh


def sc_visible_tree(case: str, seed: int, leaf_mode: str) -> tuple[pb.Mesh, dict]:
    result = scb.grow_space_colonization(
        case=case,
        attractor_count=1700 if case != "bush_shell" else 1400,
        iterations=270 if case != "bush_shell" else 230,
        influence_radius=0.24,
        kill_radius=0.055 if case != "bush_shell" else 0.060,
        step_size=0.045,
        seed=seed,
    )
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in result["nodes"]], 2.45)
    parents = [int(p) for p in result["parents"]]
    mesh = skeleton_to_tube_mesh(nodes, parents, base_radius=0.040, taper=0.82, sides=10, tip_spheres=False)
    if leaf_mode == "needles":
        add_needles(mesh, nodes, parents, seed + 11, density=3, length=0.11)
    elif leaf_mode == "rootlets":
        add_rootlets(mesh, nodes, parents, seed + 11)
    else:
        add_needles(mesh, nodes, parents, seed + 11, density=2, length=0.09)
    return mesh, {
        "case": case,
        "attractor_count": 1700 if case != "bush_shell" else 1400,
        "iterations": 270 if case != "bush_shell" else 230,
        "covered_attractors": result.get("covered_attractors"),
    }


def smooth_dla_capsules(seed: int, mode: str, n_particles: int = 720) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed)
    if mode == "frontier_sheet":
        pts = make_frontier_sheet(seed, particles=n_particles) * np.array([2.2, 1.7, 1.2])
    else:
        pts = pb.make_dla_cluster(n_particles=n_particles, seed=seed % 10000)
        if mode == "aniso":
            pts = pts * np.array([1.55, 0.72, 1.05])
        else:
            pts = pts * np.array([1.20, 1.05, 1.25])
    pts = np.asarray(pts, dtype=float)
    # Keep a deterministic subset for mesh size, biased toward outer/frontier points.
    if len(pts) > n_particles:
        norms = np.linalg.norm(pts, axis=1)
        keep = np.argsort(norms)[-n_particles:]
        pts = pts[sorted(keep)]
    mesh = pb.Mesh([], [])
    for idx, p in enumerate(pts):
        radius = 0.020 if mode != "aniso" else 0.024
        if idx % 5 == 0 or idx < 24:
            add_uv_sphere(mesh, p, radius * (1.8 if mode != "frontier_sheet" else 1.45), segments=8, rings=4)
        if idx > 0:
            prev = pts[:idx]
            j = int(np.argmin(np.linalg.norm(prev - p, axis=1)))
            dist = float(np.linalg.norm(prev[j] - p))
            max_dist = 0.19 if mode != "frontier_sheet" else 0.24
            if dist <= max_dist:
                r0 = 0.018 if mode != "aniso" else 0.020
                pb.add_cylinder(mesh, prev[j], p, r0, r0 * 0.74, sides=8)
            elif rng.random() < 0.018:
                # Deliberately rare bridge: enough to preserve asset connectivity,
                # sparse enough not to erase DLA porosity.
                pb.add_cylinder(mesh, prev[j], p, 0.006, 0.004, sides=6)
    return mesh, {
        "mode": mode,
        "n_particles": n_particles,
        "seed": seed,
        "support": "smooth capsule DLA/frontier tokenization",
    }


def radial_orbit_gear(order: int = 8, depth: int = 4) -> pb.Mesh:
    mesh = pb.Mesh([], [])
    # Connected rings make the orbit readable and avoid the V1 sparse-stick look.
    for level in range(depth):
        radius = 0.32 + level * 0.22
        z = 0.045 * level
        tooth_len = 0.10 * (0.92 ** level)
        for k in range(order):
            a0 = 2 * math.pi * k / order + level * 0.19
            a1 = 2 * math.pi * (k + 1) / order + level * 0.19
            p0 = np.array([math.cos(a0) * radius, math.sin(a0) * radius, z])
            p1 = np.array([math.cos(a1) * radius, math.sin(a1) * radius, z])
            pb.add_cylinder(mesh, p0, p1, 0.018, 0.018, sides=8)
            d = _unit(np.array([math.cos(a0), math.sin(a0), 0.08]))
            pb.add_cylinder(mesh, p0, p0 + d * tooth_len, 0.016, 0.007, sides=8)
    hub = pb.Mesh([], [])
    add_uv_sphere(hub, np.zeros(3), 0.09, segments=14, rings=6)
    return _merge([mesh, hub])


def ifs_branch_orbit(seed: int, depth: int = 6) -> pb.Mesh:
    del seed
    nodes, parents = ifs_tree_skeleton(depth=depth)
    nodes = _normalize_nodes(nodes, 2.5)
    mesh = skeleton_to_tube_mesh(nodes, parents, base_radius=0.040, taper=0.80, sides=10, tip_spheres=False)
    add_needles(mesh, nodes, parents, 917, density=1, length=0.07)
    return mesh


def build_cases(root: Path, out_dir: Path, seed: int) -> list[Case]:
    rows: list[Case] = []

    def add(case_id: str, family: str, target: str, mode: str, mesh: pb.Mesh, guide: str, gpu: int, s: int, controls: dict, operators: list[str], gate: str) -> None:
        path = out_dir / case_id / f"{case_id}.obj"
        _write_obj(path, mesh)
        controls = dict(controls)
        controls["mesh_stats"] = _mesh_stats(path)
        rows.append(Case(case_id, family, target, mode, str(path), _guide(root, guide), gpu, s, controls, operators, gate))

    add("v2_lsys_pine_canopy_d5_needles", "L-system", "lsys_pine_canopy_d5", "symbolic turtle branch rewriting with explicit pine-needle strokes", lsys_pine_needles(seed + 1, 5), "spiky_plant_tendril_square.png", 4, seed + 1, {"depth": 5}, ["symbolic_rewrite", "branch_tube", "needle_token", "weak_texture_naturalization"], "candidate if it reads as branches/needles rather than grape balls")
    add("v2_lsys_root_fan_d5_fibers", "L-system", "lsys_root_fan_d5", "downward root rewriting with fine rootlets", lsys_root_fan_fibers(seed + 2, 5), "tree_roots_arlington_square.png", 4, seed + 2, {"depth": 5}, ["root_rewrite", "fiber_token", "root_projection"], "candidate if root fan remains readable")
    mesh, ctl = sc_visible_tree("tree_canopy", seed + 11, "needles")
    add("v2_sc_tree_crown_260_branch_needles", "Space colonization", "sc_tree_crown_260", "attractor competition crown with visible branches and terminal needles", mesh, "spiky_plant_tendril_square.png", 5, seed + 11, ctl, ["attractor_competition", "branch_tube", "terminal_needle_token"], "candidate if attractor crown is readable and not a berry cluster")
    mesh, ctl = sc_visible_tree("root_vine", seed + 12, "rootlets")
    add("v2_sc_root_network_260_fibers", "Space colonization", "sc_root_network_260", "attractor competition root network with fine fibers", mesh, "tree_roots_arlington_square.png", 5, seed + 12, ctl, ["attractor_competition", "root_fiber_token", "occupancy_exclusion"], "candidate if root network is readable")
    mesh, ctl = smooth_dla_capsules(seed + 21, "coral", 760)
    add("v2_dla_coral_cluster_900_smooth_capsules", "DLA/frontier", "dla_coral_cluster_900", "random-walk accretion with smooth capsule frontier support", mesh, "octopus_suckers_square.png", 6, seed + 21, ctl, ["frontier_attachment", "smooth_capsule_token", "sparse_bridge"], "candidate if porous coral is smooth and not voxel blocky")
    mesh, ctl = smooth_dla_capsules(seed + 22, "frontier_sheet", 720)
    add("v2_dla_frontier_sheet_700_smooth", "DLA/frontier", "dla_frontier_sheet_700", "line-seeded frontier sheet with smooth capsule support", mesh, "octopus_suckers_warm.png", 6, seed + 22, ctl, ["frontier_sheet_seed", "smooth_capsule_token", "sparse_bridge"], "candidate if sheet silhouette and porosity survive")
    add("v2_ifs_branch_tree_d6_orbit_visible", "IFS/transform", "ifs_branch_tree_d6", "contractive affine branch orbit with weak tip tokenization", ifs_branch_orbit(seed + 31, 6), "spiky_plant_tendril_square.png", 7, seed + 31, {"depth": 6}, ["transform_copy", "orbit_preserving_branch_tube", "weak_tip_token"], "candidate if transform branch orbit remains readable")
    add("v2_ifs_radial_ornament_o8_d4_connected_gear", "IFS/transform", "ifs_radial_ornament_o8_d4", "radial transform-copy gear orbit with connected rings and teeth", radial_orbit_gear(8, 4), "gear_train_square.png", 7, seed + 32, {"order": 8, "depth": 4}, ["radial_orbit", "connected_ring_cache", "gear_tooth_token"], "candidate if radial order is visible")
    return rows


def materialize(root: Path, out_dir: Path, seed: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    cases = build_cases(root, out_dir, seed)
    fields = ["case_id", "family", "match_target", "recursive_mode", "mesh_path", "guide_image", "gpu_group", "seed", "operators", "controls", "claim_gate"]
    rows = []
    for c in cases:
        rows.append({
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
        })
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
    materialize(args.root, args.out or (args.root / "inputs" / "strict_visual_matched_cases_v2_20260510"), args.seed)


if __name__ == "__main__":
    main()
