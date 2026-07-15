#!/usr/bin/env python3
"""Generate strict matched procedural-vs-PS-RSLG proxy tasks.

This is a local CPU scaffold generator for evaluation design.  Each proposed
case inherits the corresponding traditional recursive mode, then applies a
PS-RSLG-like connected sparse-support interpretation: thicker support, local
tip/junction naturalization kernels, root-attached projection, and explicit
operator metadata.  It is not a replacement for Trellis2 texture/PBR export.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
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


def children_from_parents(parents: list[int]) -> dict[int, list[int]]:
    children: dict[int, list[int]] = {i: [] for i in range(len(parents))}
    for idx, parent in enumerate(parents):
        if parent >= 0:
            children.setdefault(parent, []).append(idx)
    return children


def naturalized_skeleton_coords(
    nodes: list[np.ndarray],
    parents: list[int],
    case: str,
    radius: int,
    tip_radius: int,
    jitter_seed: int,
) -> np.ndarray:
    """Interpret a recursive skeleton as a connected sparse support."""
    rng = np.random.default_rng(jitter_seed)
    points: set[tuple[int, int, int]] = set()
    child_map = children_from_parents(parents)
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    scaffold.add_ball(points, np.zeros(3, dtype=float), radius + 2)
    for idx, parent in enumerate(parents):
        if parent < 0:
            continue
        frac = depths[idx] / max(max_depth, 1)
        local_radius = max(1, int(round(radius * (1.0 - 0.45 * frac))))
        if case in {"sc_tree_canopy", "lsystem_pine"} and frac > 0.58:
            local_radius = max(local_radius, 2)
        start = np.asarray(nodes[parent], dtype=float)
        end = np.asarray(nodes[idx], dtype=float)
        scaffold.add_tube(points, start, end, local_radius)
        if len(child_map.get(idx, [])) >= 2:
            scaffold.add_ball(points, end, max(local_radius + 1, 3))
        if len(child_map.get(idx, [])) == 0:
            tr = tip_radius
            if case in {"sc_tree_canopy", "lsystem_pine"}:
                tr += int(rng.integers(0, 2))
            scaffold.add_ball(points, end + rng.normal(0, 0.7, 3), tr)
    return scaffold.largest_occupancy_component(scaffold.coords_array(points))


def write_mesh(path: Path, coords: np.ndarray) -> dict:
    mesh = scaffold.coords_to_mesh(coords)
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(path)
    return stats_from_coords_mesh(coords, mesh)


def stats_from_coords_mesh(coords: np.ndarray, mesh) -> dict:
    stats = scaffold.mesh_stats(mesh)
    stats.update(bm.occupancy_with_root_stats(coords, np.zeros(3)))
    return stats


def write_pb_mesh(path: Path, mesh: pb.Mesh, coords_for_metrics: np.ndarray | None = None) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)
    verts = np.asarray(mesh.vertices, dtype=float) if mesh.vertices else np.zeros((0, 3))
    if coords_for_metrics is None:
        coords_for_metrics = np.rint(verts * 48.0).astype(np.int32) if len(verts) else np.zeros((0, 3), dtype=np.int32)
    return stats_from_pb_mesh(mesh, coords_for_metrics)


def stats_from_pb_mesh(mesh: pb.Mesh, coords_for_metrics: np.ndarray | None = None) -> dict:
    verts = np.asarray(mesh.vertices, dtype=float) if mesh.vertices else np.zeros((0, 3))
    if coords_for_metrics is None:
        coords_for_metrics = np.rint(verts * 48.0).astype(np.int32) if len(verts) else np.zeros((0, 3), dtype=np.int32)
    stats = {
        "vertices": len(mesh.vertices),
        "faces": len(mesh.faces),
        "mesh_component_count": "",
        "largest_mesh_component_vertex_ratio": "",
    }
    stats.update(bm.occupancy_with_root_stats(coords_for_metrics, np.zeros(3)))
    return stats


def scale_nodes(nodes: list[np.ndarray], scale: float) -> list[np.ndarray]:
    return [np.asarray(n, dtype=float) * scale for n in nodes]


def add_uv_sphere(mesh: pb.Mesh, center: np.ndarray, radius: float, segments: int = 10, rings: int = 6) -> None:
    base = len(mesh.vertices)
    center = np.asarray(center, dtype=float)
    for r in range(rings + 1):
        phi = math.pi * r / rings
        for s in range(segments):
            theta = 2.0 * math.pi * s / segments
            p = center + radius * np.array(
                [math.sin(phi) * math.cos(theta), math.sin(phi) * math.sin(theta), math.cos(phi)],
                dtype=float,
            )
            mesh.vertices.append(tuple(p))
    for r in range(rings):
        for s in range(segments):
            a = base + r * segments + s
            b = base + r * segments + (s + 1) % segments
            c = base + (r + 1) * segments + s
            d = base + (r + 1) * segments + (s + 1) % segments
            mesh.faces.append((a + 1, c + 1, b + 1))
            mesh.faces.append((b + 1, c + 1, d + 1))


def skeleton_to_tube_mesh(
    nodes: list[np.ndarray],
    parents: list[int],
    base_radius: float,
    taper: float,
    sides: int = 10,
    tip_spheres: bool = False,
    junction_spheres: bool = False,
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
        r1 = max(base_radius * (1.0 - taper * f1), base_radius * 0.14)
        pb.add_cylinder(mesh, np.asarray(nodes[parent], dtype=float), np.asarray(nodes[idx], dtype=float), r0, r1, sides=sides)
    if junction_spheres or tip_spheres:
        for idx, node in enumerate(nodes):
            children = child_map.get(idx, [])
            if junction_spheres and len(children) >= 2:
                add_uv_sphere(mesh, np.asarray(node, dtype=float), base_radius * 1.10, segments=9, rings=5)
            if tip_spheres and idx != 0 and len(children) == 0:
                add_uv_sphere(mesh, np.asarray(node, dtype=float), base_radius * 1.35, segments=9, rings=5)
    return mesh


def ifs_tree_skeleton(depth: int = 6) -> tuple[list[np.ndarray], list[int]]:
    nodes = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents = [-1]

    def rec(parent: int, direction: np.ndarray, length: float, level: int) -> None:
        end = nodes[parent] + pb.unit(direction) * length
        nodes.append(end)
        current = len(nodes) - 1
        parents.append(parent)
        if level <= 0:
            return
        u, _, w = pb.basis_from_axis(direction)
        angles = [-0.55, 0.42, 0.20]
        twists = [0.0, 2.3, 4.4]
        scales = [0.72, 0.65, 0.50]
        for angle, twist, scale in zip(angles, twists, scales):
            branch_dir = pb.rot_axis(w, twist) @ (pb.rot_axis(u, angle) @ w)
            rec(current, branch_dir, length * scale, level - 1)

    rec(0, np.array([0.0, 0.0, 1.0]), 9.0, depth)
    return nodes, parents


def sc_result_to_nodes(result: dict, scale: float = 84.0) -> tuple[list[np.ndarray], list[int]]:
    nodes = [np.asarray(p, dtype=float) * scale for p in result["nodes"]]
    parents = [int(p) for p in result["parents"]]
    return nodes, parents


def build_cases(seed: int) -> list[dict]:
    rows: list[dict] = []

    def add_row(task: str, method: str, family: str, mode: str, path: Path, stats: dict, recipe: dict) -> None:
        rows.append(
            {
                "task": task,
                "method": method,
                "family": family,
                "recursive_mode": mode,
                "path": str(path),
                "vertices": stats.get("vertices", ""),
                "faces": stats.get("faces", ""),
                "occ_comp_6n": stats.get("occupancy_component_count_6n", ""),
                "occ_lcr_6n": stats.get("largest_occupancy_component_ratio_6n", ""),
                "root_ratio": stats.get("root_component_ratio", ""),
                "recipe": json.dumps(recipe, ensure_ascii=False, sort_keys=True),
            }
        )

    # L-system pine/canopy: same symbolic branching mode, proposed uses the same
    # skeleton but interprets it as connected sparse latent support.
    nodes, parents = bm.lsystem_case("tree", depth=5, seed=seed)
    trad_lsys_mesh = skeleton_to_tube_mesh(nodes, parents, base_radius=1.05, taper=0.78, sides=10)
    ours_lsys_mesh = skeleton_to_tube_mesh(
        nodes,
        parents,
        base_radius=1.18,
        taper=0.72,
        sides=12,
        tip_spheres=True,
        junction_spheres=True,
    )
    add_row(
        "lsystem_pine_canopy",
        "traditional_lsystem",
        "L-system",
        "symbolic turtle branching: F -> F[+F][-F][&F][^F]F-like tree canopy",
        Path("lsystem_pine_canopy/traditional_lsystem.obj"),
        stats_from_pb_mesh(trad_lsys_mesh),
        {"source": "baseline_matrix.lsystem_case(tree, depth=5)", "projection": "none"},
    )
    rows[-1]["_mesh"] = trad_lsys_mesh
    rows[-1]["_path_rel"] = "lsystem_pine_canopy/traditional_lsystem.obj"
    add_row(
        "lsystem_pine_canopy",
        "ours_psrslg_lsystem_mode",
        "PS-RSLG",
        "same L-system skeleton interpreted with connected sparse support + local tip/junction naturalization + root projection",
        Path("lsystem_pine_canopy/ours_psrslg_lsystem_mode.obj"),
        stats_from_pb_mesh(ours_lsys_mesh),
        {"root": "same L-system skeleton", "operators": ["typed_anchor_rewrite", "tube_support_interpretation", "junction_kernel", "tip_kernel", "root_projection"]},
    )
    rows[-1]["_mesh"] = ours_lsys_mesh
    rows[-1]["_path_rel"] = "lsystem_pine_canopy/ours_psrslg_lsystem_mode.obj"

    # Space colonization tree canopy: same attractor distribution and growth
    # mode, proposed uses connected sparse support over the same skeleton.
    sc_tree = scb.grow_space_colonization(
        case="tree_canopy",
        attractor_count=1600,
        iterations=260,
        influence_radius=0.24,
        kill_radius=0.055,
        step_size=0.045,
        seed=seed + 101,
    )
    sc_mesh = scb.skeleton_to_mesh(sc_tree, radius=0.03, taper=0.78)
    sc_nodes, sc_parents = sc_result_to_nodes(sc_tree, scale=84.0)
    sc_coords = naturalized_skeleton_coords(sc_nodes, sc_parents, "sc_tree_canopy", radius=2, tip_radius=2, jitter_seed=seed + 12)
    sc_trad_stats = stats_from_pb_mesh(sc_mesh, np.rint(np.asarray(sc_tree["nodes"], dtype=float) * 84.0).astype(np.int32))
    add_row(
        "space_colonization_tree_canopy",
        "traditional_space_colonization",
        "Space colonization",
        "attractor-field crown growth with influence/kill radii",
        Path("space_colonization_tree_canopy/traditional_space_colonization.obj"),
        sc_trad_stats,
        {"case": "tree_canopy", "attractors": 1600, "iterations": 260, "influence_radius": 0.24, "kill_radius": 0.055},
    )
    rows[-1]["_mesh"] = sc_mesh
    rows[-1]["_path_rel"] = "space_colonization_tree_canopy/traditional_space_colonization.obj"
    add_row(
        "space_colonization_tree_canopy",
        "ours_psrslg_attractor_compete",
        "PS-RSLG",
        "same attractor-driven competition skeleton with connected sparse interpretation and local naturalization",
        Path("space_colonization_tree_canopy/ours_psrslg_attractor_compete.obj"),
        stats_from_coords_mesh(sc_coords, scaffold.coords_to_mesh(sc_coords)),
        {"root": "same SC skeleton", "operators": ["attractor_compete", "occupancy_exclusion", "junction_kernel", "tip_kernel", "root_projection"]},
    )
    rows[-1]["_coords"] = sc_coords
    rows[-1]["_path_rel"] = "space_colonization_tree_canopy/ours_psrslg_attractor_compete.obj"

    # DLA crystal/coral: traditional cubes from DLA hits; proposed keeps the
    # same DLA hit set but uses local balls/tubes as masked naturalization proxy.
    pts = pb.make_dla_cluster(n_particles=900, seed=seed % 10000)
    trad_dla = pb.points_to_cube_mesh(pts, radius=0.025)
    pts_i = np.rint(pts * 64.0).astype(np.int32)
    points: set[tuple[int, int, int]] = set()
    occupied = {tuple(row) for row in pts_i.tolist()}
    offsets = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    for p in pts_i:
        scaffold.add_ball(points, p, 2)
        for off in offsets:
            q = tuple((p + np.asarray(off)).tolist())
            if q in occupied:
                scaffold.add_tube(points, p, np.asarray(q), 1)
    ours_dla_coords = scaffold.largest_occupancy_component(scaffold.coords_array(points))
    add_row(
        "dla_crystal_cluster",
        "traditional_dla_voxel_cluster",
        "DLA",
        "random-walk hitting and accretive particle attachment",
        Path("dla_crystal_cluster/traditional_dla_voxel_cluster.obj"),
        stats_from_pb_mesh(trad_dla, pts_i),
        {"n_particles": 900, "seed": seed % 10000, "surfacing": "cube per DLA hit"},
    )
    rows[-1]["_mesh"] = trad_dla
    rows[-1]["_path_rel"] = "dla_crystal_cluster/traditional_dla_voxel_cluster.obj"
    add_row(
        "dla_crystal_cluster",
        "ours_psrslg_frontier_naturalized",
        "PS-RSLG",
        "same DLA hit set with frontier-local masked naturalization and root-attached projection",
        Path("dla_crystal_cluster/ours_psrslg_frontier_naturalized.obj"),
        stats_from_coords_mesh(ours_dla_coords, scaffold.coords_to_mesh(ours_dla_coords)),
        {"root": "same DLA hits", "operators": ["frontier_attachment", "masked_local_naturalization", "neighbor_bridge", "largest_root_projection"]},
    )
    rows[-1]["_coords"] = ours_dla_coords
    rows[-1]["_path_rel"] = "dla_crystal_cluster/ours_psrslg_frontier_naturalized.obj"

    # IFS recursive branching: keep traditional transform tree and use a
    # connected transform-copy sparse interpretation as ours.
    ifs_mesh = pb.make_ifs_tree(depth=6)
    ifs_nodes, ifs_parents = ifs_tree_skeleton(depth=6)
    ifs_ours_mesh = skeleton_to_tube_mesh(
        ifs_nodes,
        ifs_parents,
        base_radius=0.62,
        taper=0.70,
        sides=10,
        tip_spheres=True,
        junction_spheres=True,
    )
    add_row(
        "ifs_transform_branching_tree",
        "traditional_ifs_tree",
        "IFS",
        "recursive contractive transform-copy branching tree",
        Path("ifs_transform_branching_tree/traditional_ifs_tree.obj"),
        stats_from_pb_mesh(ifs_mesh),
        {"transforms": "procedural_baselines.make_ifs_tree(depth=6)", "projection": "none"},
    )
    rows[-1]["_mesh"] = ifs_mesh
    rows[-1]["_path_rel"] = "ifs_transform_branching_tree/traditional_ifs_tree.obj"
    add_row(
        "ifs_transform_branching_tree",
        "ours_psrslg_transform_copy",
        "PS-RSLG",
        "transform-copy anchor grammar with connected sparse projection and local tip kernels",
        Path("ifs_transform_branching_tree/ours_psrslg_transform_copy.obj"),
        stats_from_pb_mesh(ifs_ours_mesh),
        {"operators": ["transform_copy", "scale_decay", "typed_anchor_rewrite", "root_projection", "tip_kernel"]},
    )
    rows[-1]["_mesh"] = ifs_ours_mesh
    rows[-1]["_path_rel"] = "ifs_transform_branching_tree/ours_psrslg_transform_copy.obj"

    return rows


def materialize(rows: list[dict], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    clean_rows = []
    for row in rows:
        path = out / row.pop("_path_rel")
        if "_coords" in row:
            coords = row.pop("_coords")
            stats = write_mesh(path, coords)
        else:
            mesh = row.pop("_mesh")
            stats = write_pb_mesh(path, mesh)
        row["path"] = str(path)
        row["vertices"] = stats.get("vertices", row.get("vertices", ""))
        row["faces"] = stats.get("faces", row.get("faces", ""))
        row["occ_comp_6n"] = stats.get("occupancy_component_count_6n", row.get("occ_comp_6n", ""))
        row["occ_lcr_6n"] = stats.get("largest_occupancy_component_ratio_6n", row.get("occ_lcr_6n", ""))
        row["root_ratio"] = stats.get("root_component_ratio", row.get("root_ratio", ""))
        clean_rows.append(row)

    fields = ["task", "method", "family", "recursive_mode", "path", "vertices", "faces", "occ_comp_6n", "occ_lcr_6n", "root_ratio", "recipe"]
    with (out / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(clean_rows)
    (out / "manifest.json").write_text(json.dumps(clean_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    case_file = out / "cases.txt"
    lines = []
    for row in clean_rows:
        label = f"{row['task']}__{row['method']}"
        lines.append(f"{label}={row['path']}")
    case_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    doc = out / "README.md"
    doc.write_text(
        "# Strict matched PS-RSLG proxy tasks 2026-05-10\n\n"
        "This folder is a local CPU scaffold starting point for exact matched-task evaluation. "
        "Each proposed case follows the same recursive family as its traditional counterpart, "
        "then applies PS-RSLG-style connected sparse support, local naturalization kernels, and root projection.\n\n"
        "Important: these are structure proxies, not final Trellis2 textured/PBR outputs.\n",
        encoding="utf-8",
    )
    print(json.dumps({"out": str(out), "manifest": str(out / "manifest.csv"), "case_file": str(case_file), "rows": len(clean_rows)}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT_DIR / "results" / "strict_matched_psrslg_proxy_20260510")
    parser.add_argument("--seed", type=int, default=20260510)
    args = parser.parse_args()
    materialize(build_cases(args.seed), args.out)


if __name__ == "__main__":
    main()
