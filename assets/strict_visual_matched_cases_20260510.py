#!/usr/bin/env python3
"""Generate strict matched PS-RSLG visual candidates for remote Trellis2 texturing.

This script is intentionally different from the earlier local screening
scripts: each output mesh is regenerated from the same procedural family as a
specific traditional baseline task.  The geometry is still CPU generated, but
the target use is GPU Trellis2 texturing/PBR export on a100-2.

The matching contract is:

* preserve the traditional task category and recursive/growth mode;
* keep a readable branch/frontier/transform structure instead of collapsing it
  into a generic blob;
* use connected sparse support before texturing, so the downstream GLB is
  asset-like rather than a fragmented point/cube cloud;
* record the operator composition and root/guide policy for paper evaluation.
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
from strict_matched_task_targets_20260510 import (
    add_uv_sphere,
    fractal_lattice,
    lsystem_climbing_vine,
    make_frontier_sheet,
    radial_ornament,
    skeleton_to_tube_mesh,
)


@dataclass
class Case:
    case_id: str
    family: str
    match_target: str
    recursive_mode: str
    variant: str
    mesh_path: str
    guide_image: str
    gpu_group: int
    seed: int
    controls: dict
    operators: list[str]
    claim_gate: str


def _children(parents: list[int]) -> dict[int, list[int]]:
    children = {i: [] for i in range(len(parents))}
    for idx, parent in enumerate(parents):
        if parent >= 0:
            children.setdefault(parent, []).append(idx)
    return children


def _normalize_nodes(nodes: list[np.ndarray], extent: float = 2.0) -> list[np.ndarray]:
    arr = np.asarray(nodes, dtype=float)
    mn = arr.min(axis=0)
    mx = arr.max(axis=0)
    center = (mn + mx) * 0.5
    scale = max(float((mx - mn).max()), 1e-6)
    return [(np.asarray(n, dtype=float) - center) * (extent / scale) for n in nodes]


def _copy_mesh(mesh: pb.Mesh) -> pb.Mesh:
    return pb.Mesh(list(mesh.vertices), list(mesh.faces))


def _scale_mesh(mesh: pb.Mesh, scale: float | np.ndarray, translate: np.ndarray | None = None) -> pb.Mesh:
    s = np.asarray(scale if not np.isscalar(scale) else [scale, scale, scale], dtype=float)
    t = np.zeros(3, dtype=float) if translate is None else np.asarray(translate, dtype=float)
    out = pb.Mesh([], list(mesh.faces))
    for v in mesh.vertices:
        out.vertices.append(tuple(np.asarray(v, dtype=float) * s + t))
    return out


def _merge_meshes(meshes: list[pb.Mesh]) -> pb.Mesh:
    out = pb.Mesh([], [])
    for mesh in meshes:
        offset = len(out.vertices)
        out.vertices.extend(mesh.vertices)
        for a, b, c in mesh.faces:
            out.faces.append((a + offset, b + offset, c + offset))
    return out


def _add_leaf_ellipsoids(mesh: pb.Mesh, nodes: list[np.ndarray], parents: list[int], radius: float, every: int = 1) -> None:
    child_map = _children(parents)
    tips = [i for i in range(1, len(nodes)) if len(child_map.get(i, [])) == 0]
    for rank, idx in enumerate(tips):
        if rank % max(every, 1) != 0:
            continue
        parent = parents[idx] if parents[idx] >= 0 else idx
        direction = np.asarray(nodes[idx]) - np.asarray(nodes[parent])
        direction = direction / max(float(np.linalg.norm(direction)), 1e-6)
        p = np.asarray(nodes[idx], dtype=float) + direction * radius * 0.35
        add_uv_sphere(mesh, p, radius, segments=12, rings=6)


def _write_pb_mesh(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


def _write_trimesh(path: Path, mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(path)


def _mesh_stats(path: Path) -> dict:
    import trimesh

    mesh = trimesh.load(path, force="mesh", process=False)
    pieces = mesh.split(only_watertight=False)
    sizes = [len(p.vertices) for p in pieces] or [0]
    bounds = mesh.bounds if len(mesh.vertices) else np.zeros((2, 3), dtype=float)
    extent = bounds[1] - bounds[0]
    return {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "mesh_component_count": int(len(pieces)),
        "largest_mesh_component_vertex_ratio": float(max(sizes) / max(len(mesh.vertices), 1)),
        "bbox_extent": [float(x) for x in extent],
        "bbox_diag": float(np.linalg.norm(extent)),
        "surface_area": float(getattr(mesh, "area", 0.0)),
    }


def _guide(root: Path, name: str) -> str:
    return str(root / "public_guides_20260508" / "processed" / name)


def _lsystem_pine(seed: int, depth: int, leaf_scale: float, visible: bool) -> pb.Mesh:
    nodes, parents = bm.lsystem_case("tree", depth=depth, seed=seed)
    nodes = _normalize_nodes(nodes, extent=2.3)
    mesh = skeleton_to_tube_mesh(
        nodes,
        parents,
        base_radius=0.075 if visible else 0.062,
        taper=0.74,
        sides=12,
        tip_spheres=True,
    )
    _add_leaf_ellipsoids(mesh, nodes, parents, radius=leaf_scale, every=1 if visible else 2)
    return mesh


def _lsystem_root_fan(seed: int, depth: int, hairs: bool) -> pb.Mesh:
    rng = np.random.default_rng(seed + 913)
    nodes, parents = bm.lsystem_case("root", depth=depth, seed=seed)
    nodes = _normalize_nodes(nodes, extent=2.2)
    mesh = skeleton_to_tube_mesh(nodes, parents, base_radius=0.068, taper=0.80, sides=12, tip_spheres=True)
    if hairs:
        child_map = _children(parents)
        depths = bm.graph_depths(parents)
        for idx, node in enumerate(nodes):
            if idx == 0 or depths[idx] < 2:
                continue
            if len(child_map.get(idx, [])) == 0 or rng.random() < 0.38:
                base = np.asarray(node, dtype=float)
                for _ in range(2):
                    d = rng.normal(0, 1, 3)
                    d[2] -= 0.7
                    d /= max(float(np.linalg.norm(d)), 1e-6)
                    pb.add_cylinder(mesh, base, base + d * rng.uniform(0.10, 0.22), 0.010, 0.004, sides=6)
    return mesh


def _space_colonization_mesh(case: str, seed: int, tip_radius: float, shell: bool = False) -> tuple[pb.Mesh, dict]:
    result = scb.grow_space_colonization(
        case=case,
        attractor_count=1800 if case != "bush_shell" else 1500,
        iterations=280 if case != "bush_shell" else 240,
        influence_radius=0.24,
        kill_radius=0.055 if case != "bush_shell" else 0.060,
        step_size=0.045,
        seed=seed,
    )
    nodes = [np.asarray(p, dtype=float) for p in result["nodes"]]
    parents = [int(p) for p in result["parents"]]
    nodes = _normalize_nodes(nodes, extent=2.25 if case != "root_vine" else 2.35)
    mesh = skeleton_to_tube_mesh(nodes, parents, base_radius=0.052, taper=0.82, sides=10, tip_spheres=True)
    if shell:
        _add_leaf_ellipsoids(mesh, nodes, parents, radius=tip_radius, every=2)
    else:
        _add_leaf_ellipsoids(mesh, nodes, parents, radius=tip_radius, every=3 if case == "tree_canopy" else 2)
    controls = {
        "case": case,
        "attractor_count": 1800 if case != "bush_shell" else 1500,
        "iterations": 280 if case != "bush_shell" else 240,
        "influence_radius": 0.24,
        "kill_radius": 0.055 if case != "bush_shell" else 0.060,
        "step_size": 0.045,
        "covered_attractors": result.get("covered_attractors"),
    }
    return mesh, controls


def _connected_dla_like(seed: int, mode: str, particles: int = 900) -> tuple[object, dict]:
    rng = np.random.default_rng(seed)
    if mode == "frontier_sheet":
        pts = make_frontier_sheet(seed, particles=760) * np.array([2.1, 1.8, 1.6])
    else:
        pts = pb.make_dla_cluster(n_particles=particles, seed=seed % 10000)
        if mode == "aniso_crystal":
            pts = pts * np.array([1.55, 0.72, 1.08])
        elif mode == "coral_branch":
            pts = pts * np.array([1.10, 1.05, 1.25])
    coords = np.rint(pts * 42.0).astype(np.int32)
    coords = np.unique(coords, axis=0)
    if len(coords) > 1500:
        idx = np.linspace(0, len(coords) - 1, 1500).astype(np.int64)
        coords = coords[idx]
    points: set[tuple[int, int, int]] = set()
    # Frontier-local masked naturalization: each hit gets a compact local token,
    # then a nearest-parent bridge preserves accretive structure without turning
    # the cluster into isolated cubes.
    for i, p in enumerate(coords):
        r = 2 if i % 3 else 3
        if mode == "aniso_crystal":
            scaffold.add_octahedron(points, p, r + 1)
        else:
            scaffold.add_ball(points, p + rng.normal(0, 0.18, 3), r)
        if i > 0:
            prev = coords[:i]
            j = int(np.argmin(np.linalg.norm(prev - p, axis=1)))
            d = float(np.linalg.norm(prev[j] - p))
            if d <= (10.0 if mode != "frontier_sheet" else 14.0):
                scaffold.add_tube(points, prev[j], p, 1 if d > 5.5 else 2)
    arr = scaffold.largest_occupancy_component(scaffold.coords_array(points))
    mesh = scaffold.coords_to_mesh(arr)
    controls = {
        "mode": mode,
        "particles": int(particles),
        "seed": int(seed),
        "frontier_policy": "nearest previous support bridge plus local masked token",
        "naturalization": "ball/octahedron local kernels before Trellis2 texturing",
    }
    return mesh, controls


def _ifs_branch(seed: int, depth: int) -> pb.Mesh:
    del seed
    nodes, parents = ifs_tree_skeleton(depth=depth)
    nodes = _normalize_nodes(nodes, extent=2.25)
    mesh = skeleton_to_tube_mesh(nodes, parents, base_radius=0.055, taper=0.75, sides=10, tip_spheres=True)
    _add_leaf_ellipsoids(mesh, nodes, parents, radius=0.030, every=2)
    return mesh


def _pyrite_lattice(quick: bool = False):
    coords = scaffold.pyrite_crystal_lattice_cluster(quick=quick)
    return scaffold.coords_to_mesh(scaffold.largest_occupancy_component(coords))


def _bismuth_hopper(quick: bool = False):
    coords = scaffold.bismuth_hopper_cluster(quick=quick)
    return scaffold.coords_to_mesh(scaffold.largest_occupancy_component(coords))


def _radial_gear_variant(order: int, depth: int) -> pb.Mesh:
    base = radial_ornament(order=order, depth=depth)
    hub = pb.Mesh([], [])
    add_uv_sphere(hub, np.array([0.0, 0.0, 0.0]), 0.18, segments=18, rings=8)
    ring = pb.Mesh([], [])
    for k in range(order):
        theta = 2.0 * math.pi * k / order
        p0 = np.array([math.cos(theta) * 0.28, math.sin(theta) * 0.28, 0.0])
        p1 = np.array([math.cos(theta) * 1.15, math.sin(theta) * 1.15, 0.0])
        pb.add_cylinder(ring, p0, p1, 0.035, 0.020, sides=8)
    return _merge_meshes([_scale_mesh(base, 0.60), hub, ring])


def build_cases(remote_root: Path, out_dir: Path, seed: int) -> list[Case]:
    rows: list[Case] = []

    def add_case(
        case_id: str,
        family: str,
        match_target: str,
        recursive_mode: str,
        variant: str,
        mesh_obj,
        guide: str,
        gpu: int,
        local_seed: int,
        controls: dict,
        operators: list[str],
        claim_gate: str,
    ) -> None:
        case_dir = out_dir / case_id
        path = case_dir / f"{case_id}.obj"
        if isinstance(mesh_obj, pb.Mesh):
            _write_pb_mesh(path, mesh_obj)
        else:
            _write_trimesh(path, mesh_obj)
        stats = _mesh_stats(path)
        controls = dict(controls)
        controls.update({"mesh_stats": stats})
        rows.append(
            Case(
                case_id=case_id,
                family=family,
                match_target=match_target,
                recursive_mode=recursive_mode,
                variant=variant,
                mesh_path=str(path),
                guide_image=_guide(remote_root, guide),
                gpu_group=gpu,
                seed=local_seed,
                controls=controls,
                operators=operators,
                claim_gate=claim_gate,
            )
        )

    add_case(
        "lsys_pine_canopy_d5_branch_visible",
        "L-system",
        "lsys_pine_canopy_d5",
        "symbolic turtle branch rewriting with visible trunk/branch/tip hierarchy",
        "branch_visible_tip_tokens",
        _lsystem_pine(seed + 11, depth=5, leaf_scale=0.034, visible=True),
        "spiky_plant_tendril_square.png",
        4,
        seed + 11,
        {"depth": 5, "branching_source": "baseline_matrix.lsystem_case(tree)"},
        ["typed_symbol_rewrite", "skeleton_tube_interpretation", "tip_leaf_tokens", "root_projection"],
        "positive candidate if branch hierarchy survives Trellis2 texture",
    )
    add_case(
        "lsys_pine_canopy_d6_dense_needles",
        "L-system",
        "lsys_pine_canopy_d5",
        "deeper symbolic turtle branch rewriting with denser terminal tokens",
        "depth6_dense_needles",
        _lsystem_pine(seed + 12, depth=6, leaf_scale=0.024, visible=False),
        "tree_roots_arlington_square.png",
        4,
        seed + 12,
        {"depth": 6, "branching_source": "baseline_matrix.lsystem_case(tree)"},
        ["typed_symbol_rewrite", "depth_schedule", "terminal_token_sweep", "root_projection"],
        "screen for depth/zoom, not final if too dense",
    )
    add_case(
        "lsys_root_fan_d5_hair_tokens",
        "L-system",
        "lsys_root_fan_d5",
        "symbolic root branching with downward tropism and root-hair tokens",
        "root_fan_hair_tokens",
        _lsystem_root_fan(seed + 17, depth=5, hairs=True),
        "tree_roots_arlington_square.png",
        4,
        seed + 17,
        {"depth": 5, "source": "baseline_matrix.lsystem_case(root)"},
        ["symbolic_root_rewrite", "downward_tropism", "hair_token_instancing", "root_projection"],
        "strong plant/root candidate if texture reads as roots",
    )
    add_case(
        "lsys_climbing_vine_d6_tendrils",
        "L-system",
        "lsys_climbing_vine_d6",
        "curling main chain with recursive tendril side branches",
        "tendril_visible",
        _scale_mesh(lsystem_climbing_vine(iterations=6, seed=seed + 29), 0.078),
        "parthenocissus_tendrils_square.png",
        4,
        seed + 29,
        {"iterations": 6, "curl_step_radians": 0.82},
        ["curling_lsystem_rewrite", "side_tendril_tokens", "masked_tip_naturalization"],
        "current likely paper-grade vine/root visual if zoom remains clean",
    )

    for case_id, sc_case, target, variant, guide, tip, shell, gpu, local_seed in [
        ("sc_tree_crown_260_visible_tips", "tree_canopy", "sc_tree_crown_260", "visible_competition_tips", "spiky_plant_tendril_square.png", 0.030, False, 5, seed + 101),
        ("sc_tree_crown_260_leafy_shell", "tree_canopy", "sc_tree_crown_260", "leafy_crown_shell", "tree_roots_arlington_square.png", 0.038, True, 5, seed + 102),
        ("sc_root_network_260_tube_roots", "root_vine", "sc_root_network_260", "root_network_tubes", "tree_roots_arlington_square.png", 0.028, False, 5, seed + 143),
        ("sc_bush_shell_220_compete", "bush_shell", "sc_bush_shell_220", "bush_shell_compete", "spiky_plant_tendril_warm.png", 0.034, True, 5, seed + 177),
    ]:
        mesh, controls = _space_colonization_mesh(sc_case, local_seed, tip_radius=tip, shell=shell)
        add_case(
            case_id,
            "Space colonization",
            target,
            "attractor competition with influence/kill radii and occupancy exclusion",
            variant,
            mesh,
            guide,
            gpu,
            local_seed,
            controls,
            ["attractor_competition", "occupancy_exclusion", "tip_token_schedule", "per_depth_projection"],
            "positive candidate only if attractor-driven silhouette and root paths remain visible",
        )

    for case_id, mode, target, variant, guide, gpu, local_seed, particles in [
        ("dla_coral_cluster_900_frontier_connected", "coral_branch", "dla_coral_cluster_900", "connected_frontier_coral", "octopus_suckers_square.png", 6, seed + 201, 940),
        ("dla_coral_cluster_900_mineral_connected", "coral_branch", "dla_coral_cluster_900", "mineral_texture_variant", "bismuth_crystal_square.png", 6, seed + 202, 940),
        ("dla_frontier_sheet_700_connected", "frontier_sheet", "dla_frontier_sheet_700", "line_seed_frontier_sheet", "octopus_suckers_warm.png", 6, seed + 219, 760),
        ("dla_aniso_crystal_800_faceted", "aniso_crystal", "dla_aniso_crystal_800", "anisotropic_faceted_frontier", "bismuth_crystal_warm.png", 6, seed + 231, 820),
    ]:
        mesh, controls = _connected_dla_like(local_seed, mode=mode, particles=particles)
        add_case(
            case_id,
            "DLA/frontier",
            target,
            "random-walk/frontier attachment with local masked naturalization and root-connected support",
            variant,
            mesh,
            guide,
            gpu,
            local_seed,
            controls,
            ["frontier_attachment", "occupancy_exclusion", "nearest_previous_bridge", "masked_local_naturalization"],
            "stress/positive only if porosity remains and fake bridges are not visually dominant",
        )

    add_case(
        "ifs_branch_tree_d6_transform_visible",
        "IFS/transform",
        "ifs_branch_tree_d6",
        "contractive affine transform-copy branching tree with visible copy hierarchy",
        "transform_copy_tree",
        _ifs_branch(seed + 301, depth=6),
        "spiky_plant_tendril_square.png",
        7,
        seed + 301,
        {"depth": 6, "transform_family": "3-map branch copy with scale decay"},
        ["transform_copy", "scale_decay", "orbit_preserving_projection", "weak_tip_naturalization"],
        "must preserve transform-copy orbit; otherwise use as failure boundary",
    )
    add_case(
        "ifs_radial_ornament_o8_d4_gear",
        "IFS/transform",
        "ifs_radial_ornament_o8_d4",
        "radial transform-copy ornament with depth-dependent rotation",
        "gear_radial_orbit",
        _radial_gear_variant(order=8, depth=4),
        "gear_train_square.png",
        7,
        seed + 317,
        {"order": 8, "depth": 4, "scale_decay": "1/(1+0.55*level)"},
        ["radial_transform_orbit", "transform_cache_candidate", "orbit_projection"],
        "positive if radial orbit remains legible after texture",
    )
    add_case(
        "ifs_fractal_lattice_d4_pyrite",
        "IFS/transform",
        "ifs_fractal_lattice_d4",
        "axis-aligned recursive lattice transform-copy with group-like motifs",
        "pyrite_lattice",
        _pyrite_lattice(quick=False),
        "pyrite_cubes_square.png",
        7,
        seed + 331,
        {"depth": 4, "basis": "axis-aligned 3D cross/cube lattice"},
        ["group_like_transform_copy", "lattice_cache", "orbit_projection", "crystal_material_guide"],
        "current best non-tree transform/symmetry candidate",
    )
    add_case(
        "ifs_bismuth_hopper_d4_terraces",
        "IFS/transform",
        "ifs_fractal_lattice_d4",
        "recursive stepped terrace/lattice transform family for bismuth-like crystal asset",
        "bismuth_terrace_lattice",
        _bismuth_hopper(quick=False),
        "bismuth_crystal_square.png",
        7,
        seed + 337,
        {"depth": 4, "motif": "stepped square hopper cluster with connecting beams"},
        ["stepped_transform_copy", "terrace_projection", "crystal_material_guide"],
        "visual showcase candidate, but do not claim physical crystal growth without facet metrics",
    )
    return rows


def materialize(remote_root: Path, out_dir: Path, seed: int) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    cases = build_cases(remote_root, out_dir, seed)
    rows = []
    for case in cases:
        row = {
            "case_id": case.case_id,
            "family": case.family,
            "match_target": case.match_target,
            "recursive_mode": case.recursive_mode,
            "variant": case.variant,
            "mesh_path": case.mesh_path,
            "guide_image": case.guide_image,
            "gpu_group": case.gpu_group,
            "seed": case.seed,
            "operators": json.dumps(case.operators, ensure_ascii=False),
            "controls": json.dumps(case.controls, ensure_ascii=False, sort_keys=True),
            "claim_gate": case.claim_gate,
        }
        rows.append(row)
    fields = [
        "case_id",
        "family",
        "match_target",
        "recursive_mode",
        "variant",
        "mesh_path",
        "guide_image",
        "gpu_group",
        "seed",
        "operators",
        "controls",
        "claim_gate",
    ]
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    for gpu in sorted({case.gpu_group for case in cases}):
        lines = []
        for case in cases:
            if case.gpu_group != gpu:
                continue
            lines.append(f"{case.case_id}|{case.mesh_path}|{case.guide_image}|{case.seed}")
        (out_dir / f"gpu{gpu}_cases.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# Strict visual matched PS-RSLG cases 2026-05-10\n\n"
        "These OBJ inputs are generated from the same recursive families as the "
        "traditional baseline targets.  They are meant for remote Trellis2 "
        "texturing/PBR export, not for local post-hoc selection only.\n",
        encoding="utf-8",
    )
    summary = {"out_dir": str(out_dir), "num_cases": len(cases), "manifest": str(out_dir / "manifest.csv")}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("RGG_ROOT", ROOT_DIR)))
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=20260510)
    args = parser.parse_args()
    out_dir = args.out or (args.root / "inputs" / "strict_visual_matched_cases_20260510")
    materialize(args.root, out_dir, args.seed)


if __name__ == "__main__":
    main()
