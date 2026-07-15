#!/usr/bin/env python3
"""V3 strict matched PS-RSLG candidates for remote Trellis2 texturing.

V1/V2 showed that the remote Trellis2 path works, but also that the weak
geometry choices were causing grape-like crowns, tube-skeleton DLA/coral, and
sparse radial cases.  V3 keeps the same strict one-to-one procedural families,
but changes the generated inputs themselves before GPU texturing:

* conifer / crown cases use readable trunk, whorl branches, and flattened
  foliage/needle clusters rather than all-direction spikes;
* root cases use explicit thick-to-thin root hierarchy;
* DLA/frontier cases use local implicit-surface naturalization over the same
  frontier/support process, so they are connected continuous meshes instead of
  cubes or straight capsules;
* IFS/radial/lattice cases use solid transform orbits with enough thickness to
  survive Trellis2 projection and paper zooms.
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
from strict_matched_task_targets_20260510 import add_uv_sphere, lsystem_climbing_vine, make_frontier_sheet, skeleton_to_tube_mesh


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
    mn = arr.min(axis=0)
    mx = arr.max(axis=0)
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


def _write_obj(path: Path, mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(mesh, "export"):
        mesh.export(path)
    else:
        pb.write_obj(path, mesh)


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


def _basis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = _unit(axis)
    seed = np.array([0.0, 0.0, 1.0]) if abs(w[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = _unit(np.cross(w, seed))
    v = _unit(np.cross(w, u))
    return u, v, w


def add_leaf_card(mesh: pb.Mesh, center: np.ndarray, normal: np.ndarray, scale: float, aspect: float = 2.8) -> None:
    u, v, _ = _basis(normal)
    c = np.asarray(center, dtype=float)
    a = scale * aspect
    b = scale
    base = len(mesh.vertices)
    mesh.vertices.extend(
        [
            tuple(c + u * a),
            tuple(c + v * b),
            tuple(c - u * a),
            tuple(c - v * b),
            tuple(c + normal * scale * 0.15),
        ]
    )
    # Two-sided diamond card plus tiny raised center. OBJ face indices are 1-based.
    faces = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (1, 0, 4), (2, 1, 4), (3, 2, 4), (0, 3, 4)]
    for a0, b0, c0 in faces:
        mesh.faces.append((base + a0 + 1, base + b0 + 1, base + c0 + 1))


def add_foliage_sprays(mesh: pb.Mesh, nodes: list[np.ndarray], parents: list[int], seed: int, mode: str) -> None:
    rng = np.random.default_rng(seed)
    children = _children(parents)
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    for idx, node in enumerate(nodes):
        if idx == 0 or depths[idx] < max_depth * 0.48:
            continue
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(np.asarray(node) - np.asarray(nodes[parent]))
        u, v, _ = _basis(axis)
        is_tip = not children.get(idx)
        count = 5 if mode == "pine" else 7
        if is_tip:
            count += 3
        for k in range(count):
            theta = 2.0 * math.pi * k / max(count, 1) + rng.normal(0, 0.10)
            radial = math.cos(theta) * u + math.sin(theta) * v
            normal = _unit(0.45 * axis + 0.80 * radial + rng.normal(0, 0.04, 3))
            loc = np.asarray(node) + radial * rng.uniform(0.030, 0.075) + axis * rng.uniform(-0.015, 0.055)
            if mode == "pine":
                pb.add_cylinder(mesh, loc, loc + normal * rng.uniform(0.11, 0.17), 0.0040, 0.0014, sides=5)
            else:
                add_leaf_card(mesh, loc + normal * 0.035, normal, rng.uniform(0.022, 0.040), aspect=rng.uniform(1.5, 2.3))


def add_root_hairs(mesh: pb.Mesh, nodes: list[np.ndarray], parents: list[int], seed: int, density: int = 2) -> None:
    rng = np.random.default_rng(seed)
    depths = bm.graph_depths(parents)
    for idx, node in enumerate(nodes):
        if idx == 0 or depths[idx] < 2:
            continue
        parent = parents[idx] if parents[idx] >= 0 else idx
        axis = _unit(np.asarray(node) - np.asarray(nodes[parent]))
        u, v, _ = _basis(axis)
        count = density + (1 if depths[idx] > 4 else 0)
        for _ in range(count):
            d = _unit(-0.15 * axis + rng.normal(0, 0.7) * u + rng.normal(0, 0.7) * v + np.array([0.0, 0.0, -0.20]))
            p0 = np.asarray(node) + rng.normal(0, 0.010, 3)
            p1 = p0 + d * rng.uniform(0.09, 0.22)
            pb.add_cylinder(mesh, p0, p1, 0.0038, 0.0012, sides=5)


def lsys_layered_pine(seed: int, depth: int = 5) -> pb.Mesh:
    rng = np.random.default_rng(seed)
    mesh = pb.Mesh([], [])
    trunk = [np.array([0.0, 0.0, -1.15 + i * 0.27]) for i in range(9)]
    for i, (a, b) in enumerate(zip(trunk[:-1], trunk[1:])):
        pb.add_cylinder(mesh, a, b, 0.055 * (0.90 ** i), 0.050 * (0.90 ** i), sides=12)
    nodes = list(trunk)
    parents = [-1] + list(range(len(trunk) - 1))
    for level in range(2, 9):
        base = trunk[level]
        radius = 0.60 * (1.0 - 0.080 * level)
        branch_count = 5 if level < 7 else 4
        for k in range(branch_count):
            theta = 2.0 * math.pi * k / branch_count + level * 0.35 + rng.normal(0, 0.05)
            outward = np.array([math.cos(theta), math.sin(theta), 0.25 - 0.05 * level])
            outward = _unit(outward)
            p1 = base + outward * radius
            p2 = p1 + _unit(outward + np.array([0, 0, 0.22])) * radius * 0.38
            i1 = len(nodes)
            nodes.append(p1)
            parents.append(level)
            i2 = len(nodes)
            nodes.append(p2)
            parents.append(i1)
            pb.add_cylinder(mesh, base, p1, 0.030, 0.016, sides=10)
            pb.add_cylinder(mesh, p1, p2, 0.016, 0.007, sides=8)
    add_foliage_sprays(mesh, nodes, parents, seed + 71, "pine")
    return mesh


def lsys_root_hierarchy(seed: int, depth: int = 5) -> pb.Mesh:
    nodes, parents = bm.lsystem_case("root", depth=depth, seed=seed)
    nodes = _normalize_nodes(nodes, 2.55)
    mesh = skeleton_to_tube_mesh(nodes, parents, base_radius=0.070, taper=0.80, sides=12, tip_spheres=False)
    add_root_hairs(mesh, nodes, parents, seed + 19, density=2)
    return mesh


def lsys_leafy_vine(seed: int) -> pb.Mesh:
    mesh = lsystem_climbing_vine(iterations=6, seed=seed)
    # Add a small set of non-spherical leaf cards so the matched vine remains a
    # recursive vine instead of collapsing into a twig-only control.
    rng = np.random.default_rng(seed + 29)
    verts = np.asarray(mesh.vertices, dtype=float)
    if len(verts) == 0:
        return mesh
    indices = rng.choice(len(verts), size=min(42, len(verts)), replace=False)
    for idx in indices:
        c = verts[idx]
        normal = _unit(np.array([math.sin(c[2] * 2.4), math.cos(c[2] * 2.1), 0.35]) + rng.normal(0, 0.15, 3))
        add_leaf_card(mesh, c + normal * 0.035, normal, rng.uniform(0.018, 0.035), aspect=1.9)
    return mesh


def sc_crown_leaf_clusters(seed: int, case: str, mode: str) -> tuple[pb.Mesh, dict]:
    result = scb.grow_space_colonization(
        case=case,
        attractor_count=1800 if case != "bush_shell" else 1500,
        iterations=285 if case != "bush_shell" else 245,
        influence_radius=0.24,
        kill_radius=0.055 if case != "bush_shell" else 0.060,
        step_size=0.045,
        seed=seed,
    )
    nodes = _normalize_nodes([np.asarray(p, dtype=float) for p in result["nodes"]], 2.45)
    parents = [int(p) for p in result["parents"]]
    if mode == "root":
        mesh = skeleton_to_tube_mesh(nodes, parents, base_radius=0.052, taper=0.83, sides=10, tip_spheres=False)
        add_root_hairs(mesh, nodes, parents, seed + 5, density=2)
    else:
        mesh = skeleton_to_tube_mesh(nodes, parents, base_radius=0.046, taper=0.80, sides=10, tip_spheres=False)
        add_foliage_sprays(mesh, nodes, parents, seed + 5, "leaf")
    controls = {
        "case": case,
        "attractor_count": 1800 if case != "bush_shell" else 1500,
        "iterations": 285 if case != "bush_shell" else 245,
        "influence_radius": 0.24,
        "kill_radius": 0.055 if case != "bush_shell" else 0.060,
        "step_size": 0.045,
        "covered_attractors": result.get("covered_attractors"),
        "alive_attractors": result.get("alive_attractors"),
    }
    return mesh, controls


def _implicit_surface(points: np.ndarray, radii: np.ndarray, grid: int = 112, pad: float = 0.30, level: float = 0.56):
    import trimesh
    from skimage import measure

    pts = np.asarray(points, dtype=np.float32)
    r = np.asarray(radii, dtype=np.float32)
    mn = pts.min(axis=0) - float(r.max()) - pad
    mx = pts.max(axis=0) + float(r.max()) + pad
    span = mx - mn
    scale = max(float(span.max()), 1e-6)
    mx = mn + scale
    xs = np.linspace(mn[0], mx[0], grid, dtype=np.float32)
    ys = np.linspace(mn[1], mx[1], grid, dtype=np.float32)
    zs = np.linspace(mn[2], mx[2], grid, dtype=np.float32)
    vol = np.zeros((grid, grid, grid), dtype=np.float32)
    for p, rr in zip(pts, r):
        lo = np.maximum(np.floor((p - rr * 2.8 - mn) / scale * (grid - 1)).astype(int), 0)
        hi = np.minimum(np.ceil((p + rr * 2.8 - mn) / scale * (grid - 1)).astype(int) + 1, grid)
        if np.any(hi <= lo):
            continue
        gx, gy, gz = np.meshgrid(xs[lo[0] : hi[0]], ys[lo[1] : hi[1]], zs[lo[2] : hi[2]], indexing="ij")
        d2 = (gx - p[0]) ** 2 + (gy - p[1]) ** 2 + (gz - p[2]) ** 2
        vol[lo[0] : hi[0], lo[1] : hi[1], lo[2] : hi[2]] += np.exp(-d2 / max(2.0 * rr * rr, 1e-6))
    verts, faces, _normals, _values = measure.marching_cubes(vol, level=level)
    verts = verts / float(grid - 1) * scale + mn
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    pieces = mesh.split(only_watertight=False)
    if pieces:
        mesh = max(pieces, key=lambda p: len(p.vertices))
    center = (mesh.bounds[0] + mesh.bounds[1]) * 0.5
    mesh.apply_translation(-center)
    mesh.apply_scale(2.35 / max(float((mesh.bounds[1] - mesh.bounds[0]).max()), 1e-6))
    return mesh


def implicit_dla(seed: int, mode: str, n_particles: int = 900):
    rng = np.random.default_rng(seed)
    if mode == "frontier_sheet":
        pts = make_frontier_sheet(seed, particles=n_particles) * np.array([2.15, 1.60, 1.05])
    else:
        pts = pb.make_dla_cluster(n_particles=n_particles, seed=seed % 10000)
        if mode == "aniso_crystal":
            pts = pts * np.array([1.55, 0.72, 1.08])
        else:
            pts = pts * np.array([1.15, 1.05, 1.24])
    pts = np.asarray(pts, dtype=np.float32)
    if len(pts) > n_particles:
        pts = pts[np.linspace(0, len(pts) - 1, n_particles).astype(int)]
    # Parent bridges keep the DLA attachment path connected, while the implicit
    # field gives the local masked naturalization needed for non-voxel surfaces.
    extra = []
    for i in range(1, len(pts)):
        prev = pts[:i]
        j = int(np.argmin(np.linalg.norm(prev - pts[i], axis=1)))
        d = float(np.linalg.norm(prev[j] - pts[i]))
        if d <= (0.28 if mode != "frontier_sheet" else 0.36):
            for t in (0.33, 0.66):
                extra.append(prev[j] * (1 - t) + pts[i] * t)
        elif rng.random() < (0.012 if mode == "coral" else 0.020):
            extra.append(prev[j] * 0.5 + pts[i] * 0.5)
    if extra:
        pts = np.vstack([pts, np.asarray(extra, dtype=np.float32)])
    norm = np.linalg.norm(pts, axis=1)
    frontier = norm > np.quantile(norm, 0.72)
    if mode == "aniso_crystal":
        radii = np.where(frontier, 0.070, 0.050)
        mesh = _implicit_surface(pts, radii, grid=104, level=0.56)
        try:
            # Give crystals a mild faceted bias after the connected implicit
            # surface, instead of a voxel-block look.
            mesh.vertices = np.round(mesh.vertices * 38.0) / 38.0
            mesh.merge_vertices(digits_vertex=5)
        except Exception:
            pass
    else:
        radii = np.where(frontier, 0.070, 0.052)
        mesh = _implicit_surface(pts, radii, grid=112, level=0.58 if mode == "coral" else 0.54)
    return mesh, {
        "mode": mode,
        "n_particles": int(n_particles),
        "implicit_points": int(len(pts)),
        "naturalization": "frontier-local implicit surface over same DLA support",
        "seed": int(seed),
    }


def ifs_clean_branch(seed: int, depth: int = 6) -> pb.Mesh:
    del seed
    nodes, parents = ifs_tree_skeleton(depth=depth)
    nodes = _normalize_nodes(nodes, 2.45)
    return skeleton_to_tube_mesh(nodes, parents, base_radius=0.055, taper=0.78, sides=12, tip_spheres=True)


def radial_solid_gear(order: int = 8, depth: int = 4) -> pb.Mesh:
    mesh = pb.Mesh([], [])
    for level in range(depth):
        radius = 0.28 + level * 0.24
        z = 0.040 * level
        tube = 0.028 * (0.88 ** level)
        phase = 0.18 * level
        for k in range(order):
            a0 = 2 * math.pi * k / order + phase
            a1 = 2 * math.pi * (k + 1) / order + phase
            p0 = np.array([math.cos(a0) * radius, math.sin(a0) * radius, z])
            p1 = np.array([math.cos(a1) * radius, math.sin(a1) * radius, z])
            pb.add_cylinder(mesh, p0, p1, tube, tube, sides=10)
            d = _unit(np.array([math.cos(a0), math.sin(a0), 0.10]))
            pb.add_cylinder(mesh, p0, p0 + d * (0.11 + 0.02 * (depth - level)), tube * 0.92, tube * 0.45, sides=10)
            if level > 0 and k % 2 == 0:
                rprev = 0.28 + (level - 1) * 0.24
                pp = np.array([math.cos(a0 - 0.18) * rprev, math.sin(a0 - 0.18) * rprev, 0.040 * (level - 1)])
                pb.add_cylinder(mesh, pp, p0, tube * 0.70, tube * 0.78, sides=8)
    add_uv_sphere(mesh, np.zeros(3), 0.11, segments=16, rings=8)
    return mesh


def lattice_from_scaffold(kind: str):
    if kind == "pyrite":
        return scaffold.coords_to_mesh(scaffold.largest_occupancy_component(scaffold.pyrite_crystal_lattice_cluster(quick=False)))
    if kind == "bismuth":
        return scaffold.coords_to_mesh(scaffold.largest_occupancy_component(scaffold.bismuth_hopper_cluster(quick=False)))
    raise ValueError(kind)


def _write_guides(out_dir: Path) -> dict[str, str]:
    from PIL import Image, ImageDraw, ImageFilter

    guide_dir = out_dir / "_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)

    def save(name: str, colors: list[tuple[int, int, int]], strokes: str) -> str:
        img = Image.new("RGB", (768, 768), colors[0])
        draw = ImageDraw.Draw(img)
        rng = np.random.default_rng(abs(hash(name)) % (2**32))
        for _ in range(420):
            c = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(0, 768))
            y = int(rng.integers(0, 768))
            if strokes == "needles":
                dx = int(rng.normal(0, 55))
                dy = int(rng.normal(-20, 55))
                draw.line((x, y, x + dx, y + dy), fill=c, width=int(rng.integers(2, 6)))
            elif strokes == "roots":
                dx = int(rng.normal(0, 70))
                dy = int(rng.normal(30, 40))
                draw.line((x, y, x + dx, y + dy), fill=c, width=int(rng.integers(3, 9)))
            elif strokes == "coral":
                r = int(rng.integers(8, 32))
                draw.ellipse((x - r, y - r, x + r, y + r), fill=c)
            elif strokes == "metal":
                r = int(rng.integers(8, 38))
                draw.rectangle((x - r, y - r, x + r, y + r), fill=c)
            else:
                draw.line((x, y, x + int(rng.normal(0, 80)), y + int(rng.normal(0, 80))), fill=c, width=5)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "conifer": save("v3_conifer_needles_guide.png", [(33, 54, 35), (58, 86, 48), (95, 116, 72), (91, 61, 35)], "needles"),
        "leaf": save("v3_leaf_bark_guide.png", [(42, 73, 36), (82, 121, 58), (118, 94, 55), (55, 42, 26)], "needles"),
        "root": save("v3_root_bark_guide.png", [(43, 31, 21), (83, 62, 39), (116, 90, 58), (30, 24, 17)], "roots"),
        "coral": save("v3_coral_porosity_guide.png", [(126, 67, 52), (182, 104, 76), (218, 151, 104), (83, 44, 48)], "coral"),
        "pyrite": save("v3_pyrite_facets_guide.png", [(108, 87, 36), (176, 144, 58), (221, 193, 101), (70, 64, 54)], "metal"),
        "bismuth": save("v3_bismuth_iridescent_guide.png", [(88, 65, 127), (58, 130, 142), (185, 108, 80), (220, 186, 89)], "metal"),
        "gear": save("v3_dark_metal_gear_guide.png", [(36, 38, 35), (89, 96, 84), (155, 127, 78), (87, 42, 31)], "metal"),
    }


def build_cases(root: Path, out_dir: Path, seed: int) -> list[Case]:
    rows: list[Case] = []
    guides = _write_guides(out_dir)

    def add(
        case_id: str,
        family: str,
        target: str,
        mode: str,
        mesh,
        guide_key: str,
        gpu: int,
        s: int,
        controls: dict,
        operators: list[str],
        gate: str,
    ) -> None:
        path = out_dir / case_id / f"{case_id}.obj"
        _write_obj(path, mesh)
        controls = dict(controls)
        controls["mesh_stats"] = _mesh_stats(path)
        rows.append(Case(case_id, family, target, mode, str(path), guides[guide_key], gpu, s, controls, operators, gate))

    add("v3_lsys_pine_canopy_d5_layered_conifer", "L-system", "lsys_pine_canopy_d5", "symbolic pine rewriting with whorled trunk branches and local conifer sprays", lsys_layered_pine(seed + 1, 5), "conifer", 4, seed + 1, {"depth": 5, "layout": "whorled conifer"}, ["symbolic_rewrite", "whorl_branch_operator", "masked_tip_foliage", "per_depth_projection"], "candidate only if trunk, whorls, and conifer silhouette are readable")
    add("v3_lsys_root_fan_d5_hierarchy", "L-system", "lsys_root_fan_d5", "downward symbolic root rewriting with thick-to-thin root hierarchy", lsys_root_hierarchy(seed + 2, 5), "root", 4, seed + 2, {"depth": 5}, ["root_rewrite", "root_hair_token", "root_component_projection"], "candidate if main root and side root fan are readable")
    add("v3_lsys_climbing_vine_d6_leaf_cards", "L-system", "lsys_climbing_vine_d6", "curling vine rewriting with tendril and leaf-card tokens", lsys_leafy_vine(seed + 3), "leaf", 4, seed + 3, {"iterations": 6}, ["curl_rewrite", "tendril_token", "leaf_card_naturalization"], "candidate if helix vine and tendrils remain visible")

    mesh, ctl = sc_crown_leaf_clusters(seed + 11, "tree_canopy", "leaf")
    add("v3_sc_tree_crown_260_leaf_clusters", "Space colonization", "sc_tree_crown_260", "attractor competition crown with branch support and local leaf clusters", mesh, "leaf", 5, seed + 11, ctl, ["attractor_competition", "occupancy_exclusion", "masked_leaf_cluster"], "candidate if SC crown shape and branches are readable")
    mesh, ctl = sc_crown_leaf_clusters(seed + 12, "root_vine", "root")
    add("v3_sc_root_network_260_root_hierarchy", "Space colonization", "sc_root_network_260", "attractor competition root network with root hierarchy", mesh, "root", 5, seed + 12, ctl, ["attractor_competition", "root_projection", "root_hair_token"], "candidate if root network is readable and connected")
    mesh, ctl = sc_crown_leaf_clusters(seed + 13, "bush_shell", "leaf")
    add("v3_sc_bush_shell_220_leaf_shell", "Space colonization", "sc_bush_shell_220", "shell attractor competition with local foliage clusters", mesh, "leaf", 5, seed + 13, ctl, ["shell_attractor_competition", "masked_leaf_cluster", "component_projection"], "candidate if bush shell is not a gray spike ball")

    mesh, ctl = implicit_dla(seed + 21, "coral", 920)
    add("v3_dla_coral_cluster_900_implicit_organic", "DLA/frontier", "dla_coral_cluster_900", "DLA support with frontier-local implicit-surface naturalization", mesh, "coral", 6, seed + 21, ctl, ["frontier_attachment", "nearest_parent_bridge", "local_implicit_naturalization"], "candidate if coral is continuous, porous, and not tube skeleton")
    mesh, ctl = implicit_dla(seed + 22, "frontier_sheet", 760)
    add("v3_dla_frontier_sheet_700_implicit_reef", "DLA/frontier", "dla_frontier_sheet_700", "line-seeded frontier sheet with implicit reef naturalization", mesh, "coral", 6, seed + 22, ctl, ["frontier_sheet_seed", "occupancy_exclusion", "local_implicit_naturalization"], "candidate if sheet/frontier silhouette survives")
    mesh, ctl = implicit_dla(seed + 23, "aniso_crystal", 780)
    add("v3_dla_aniso_crystal_800_faceted_frontier", "DLA/frontier", "dla_aniso_crystal_800", "anisotropic frontier accretion with connected faceted naturalization", mesh, "pyrite", 6, seed + 23, ctl, ["anisotropic_frontier_attachment", "faceted_projection", "local_implicit_naturalization"], "candidate if frontier crystal remains connected and faceted")

    add("v3_ifs_branch_tree_d6_clean_orbit", "IFS/transform", "ifs_branch_tree_d6", "contractive affine branch orbit with clean tapered support", ifs_clean_branch(seed + 31, 6), "conifer", 7, seed + 31, {"depth": 6}, ["transform_copy", "orbit_branch_support", "tip_projection"], "candidate if transform branch hierarchy is readable")
    add("v3_ifs_radial_ornament_o8_d4_solid_gear", "IFS/transform", "ifs_radial_ornament_o8_d4", "8-fold radial transform-copy gear with connected ring cache", radial_solid_gear(8, 4), "gear", 7, seed + 32, {"order": 8, "depth": 4}, ["radial_orbit", "connected_ring_cache", "gear_tooth_token"], "candidate if radial order and local repeated units are clear")
    add("v3_ifs_fractal_lattice_d4_pyrite_scaffold", "IFS/transform", "ifs_fractal_lattice_d4", "recursive lattice transform-copy with pyrite-like scaffold cache", lattice_from_scaffold("pyrite"), "pyrite", 7, seed + 33, {"depth": 4, "source": "connected_scaffold_cases_v2.pyrite_crystal_lattice_cluster"}, ["lattice_orbit", "transform_cache", "faceted_projection"], "candidate if lattice self-similarity and crystal facets are clear")
    add("v3_ifs_bismuth_hopper_d4_terraced_lattice", "IFS/transform", "ifs_bismuth_hopper_d4", "terraced square-hopper transform-cache candidate", lattice_from_scaffold("bismuth"), "bismuth", 7, seed + 34, {"depth": 4, "source": "connected_scaffold_cases_v2.bismuth_hopper_cluster"}, ["terrace_transform", "lod_cache", "faceted_projection"], "candidate if bismuth terrace signal is strong")
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
    materialize(args.root, args.out or (args.root / "inputs" / "strict_visual_matched_cases_v3_20260510"), args.seed)


if __name__ == "__main__":
    main()
