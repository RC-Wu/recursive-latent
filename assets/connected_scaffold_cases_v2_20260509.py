#!/usr/bin/env python3
"""Generate connected procedural scaffold mesh cases v2 for PS-RSLG roots.

The cases are intentionally occupancy-first: each design is assembled from
overlapping voxels/tubes/boxes, then converted to a triangle mesh. This keeps
the support connected while still producing OBJ meshes suitable for downstream
Trellis2 texturing probes.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from collections import deque
from pathlib import Path

import numpy as np


DEFAULT_OUT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/connected_scaffold_cases_v2_20260509")
DEFAULT_DOC = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/connected_scaffold_cases_v2_zh_20260509.md")
ASSET_DIR = Path(__file__).resolve().parent


def ball_offsets(radius: int) -> np.ndarray:
    rows = []
    r2 = float(radius * radius) + 0.25
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            for z in range(-radius, radius + 1):
                if x * x + y * y + z * z <= r2:
                    rows.append((x, y, z))
    return np.asarray(rows, dtype=np.int16)


def add_ball(points: set[tuple[int, int, int]], center: np.ndarray, radius: int) -> None:
    c = np.rint(center).astype(np.int32)
    for off in ball_offsets(radius):
        p = c + off
        points.add((int(p[0]), int(p[1]), int(p[2])))


def add_tube(points: set[tuple[int, int, int]], start: np.ndarray, end: np.ndarray, radius: int) -> None:
    start = np.asarray(start, dtype=np.float64)
    end = np.asarray(end, dtype=np.float64)
    steps = max(int(np.linalg.norm(end - start) * 1.8), 2)
    for t in np.linspace(0.0, 1.0, steps):
        add_ball(points, start * (1.0 - t) + end * t, radius)


def add_box(points: set[tuple[int, int, int]], lo: tuple[int, int, int], hi: tuple[int, int, int]) -> None:
    for x in range(int(lo[0]), int(hi[0]) + 1):
        for y in range(int(lo[1]), int(hi[1]) + 1):
            for z in range(int(lo[2]), int(hi[2]) + 1):
                points.add((x, y, z))


def remove_ball(points: set[tuple[int, int, int]], center: np.ndarray, radius: int) -> None:
    c = np.rint(center).astype(np.int32)
    for off in ball_offsets(radius):
        p = c + off
        points.discard((int(p[0]), int(p[1]), int(p[2])))


def add_octahedron(points: set[tuple[int, int, int]], center: np.ndarray, radius: int) -> None:
    c = np.rint(center).astype(np.int32)
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            for z in range(-radius, radius + 1):
                if abs(x) + abs(y) + abs(z) <= radius:
                    points.add((int(c[0] + x), int(c[1] + y), int(c[2] + z)))


def coords_array(points: set[tuple[int, int, int]]) -> np.ndarray:
    if not points:
        return np.zeros((0, 3), dtype=np.int32)
    return np.asarray(sorted(points), dtype=np.int32)


def largest_occupancy_component(coords: np.ndarray) -> np.ndarray:
    coords = np.unique(np.asarray(coords, dtype=np.int32), axis=0)
    if len(coords) == 0:
        return coords
    occupied = {tuple(row) for row in coords.tolist()}
    seen: set[tuple[int, int, int]] = set()
    offsets = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    components: list[list[tuple[int, int, int]]] = []
    for start in occupied:
        if start in seen:
            continue
        q: deque[tuple[int, int, int]] = deque([start])
        seen.add(start)
        component: list[tuple[int, int, int]] = []
        while q:
            p = q.popleft()
            component.append(p)
            x, y, z = p
            for dx, dy, dz in offsets:
                nxt = (x + dx, y + dy, z + dz)
                if nxt in occupied and nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        components.append(component)
    largest = max(components, key=len)
    return np.asarray(sorted(largest), dtype=np.int32)


def volumetric_dla_coral_cluster(seed: int = 20260509, quick: bool = False) -> np.ndarray:
    rng = np.random.default_rng(seed)
    points: set[tuple[int, int, int]] = set()
    root = np.array([0.0, 0.0, -18.0])
    add_ball(points, root, 7)
    tips = [root]

    # Three thick seed arms force the DLA/coral scaffold to occupy real volume
    # instead of collapsing into a sheet.
    seed_dirs = [
        np.array([1.0, 0.3, 0.8]),
        np.array([-0.7, 0.9, 0.6]),
        np.array([0.15, -1.0, 1.0]),
        np.array([0.5, 0.65, -0.75]),
    ]
    for d in seed_dirs:
        d = d / np.linalg.norm(d)
        end = root + d * 24.0
        add_tube(points, root, end, 5)
        add_ball(points, end, 6)
        tips.append(end)

    branch_count = 44 if quick else 116
    for i in range(branch_count):
        base = tips[int(rng.integers(0, len(tips)))]
        outward = base - np.array([0.0, 0.0, -8.0])
        direction = outward * 0.55 + rng.normal(0, 10.5, 3)
        direction[2] += rng.uniform(-4.0, 8.0)
        norm = np.linalg.norm(direction)
        direction = direction / norm if norm > 1e-6 else np.array([0.0, 0.0, 1.0])
        length = float(rng.uniform(10.0, 25.0) * max(0.58, 1.0 - 0.0035 * i))
        end = base + direction * max(length, 7.0)
        radius = 4 if i < 18 else (3 if i < 60 else 2)
        add_tube(points, base, end, radius)
        add_ball(points, end, int(rng.integers(3, 7)))
        if i % 5 == 0:
            add_ball(points, base * 0.5 + end * 0.5 + rng.normal(0, 2.2, 3), int(rng.integers(3, 6)))
        for _ in range(1 if quick else 3):
            side = rng.normal(0, 1, 3)
            side = side / max(np.linalg.norm(side), 1e-6)
            twig = end + side * rng.uniform(5, 13)
            add_tube(points, end, twig, 2 if i < 35 else 1)
            add_ball(points, twig, int(rng.integers(2, 5)))
        tips.append(end)
    return coords_array(points)


def add_hopper_square(
    points: set[tuple[int, int, int]],
    center: tuple[int, int, int],
    levels: int,
    outer: int,
    step: int,
    height: int,
) -> None:
    cx, cy, cz = center
    for k in range(levels):
        z0 = cz + k * height
        o = max(outer - k * step, 6)
        inner = max(o - 8, 3)
        thick = 3
        add_box(points, (cx - o, cy - o, z0), (cx + o, cy - inner, z0 + thick))
        add_box(points, (cx - o, cy + inner, z0), (cx + o, cy + o, z0 + thick))
        add_box(points, (cx - o, cy - inner, z0), (cx - inner, cy + inner, z0 + thick))
        add_box(points, (cx + inner, cy - inner, z0), (cx + o, cy + inner, z0 + thick))
        lip = 2
        add_box(points, (cx - inner - lip, cy - inner - lip, z0 + thick + 1), (cx + inner + lip, cy - inner, z0 + thick + 1))
        add_box(points, (cx - inner - lip, cy + inner, z0 + thick + 1), (cx + inner + lip, cy + inner + lip, z0 + thick + 1))
        add_box(points, (cx - inner - lip, cy - inner, z0 + thick + 1), (cx - inner, cy + inner, z0 + thick + 1))
        add_box(points, (cx + inner, cy - inner, z0 + thick + 1), (cx + inner + lip, cy + inner, z0 + thick + 1))
        for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            p0 = np.array([cx + sx * o, cy + sy * o, z0 + 1], dtype=float)
            p1 = np.array([cx + sx * max(o - step, 4), cy + sy * max(o - step, 4), z0 + height + 1], dtype=float)
            add_tube(points, p0, p1, 2)


def bismuth_hopper_cluster(quick: bool = False) -> np.ndarray:
    points: set[tuple[int, int, int]] = set()
    specs = [
        ((-18, -10, -10), 6 if quick else 8, 25, 3, 4),
        ((18, 12, -3), 5 if quick else 7, 20, 3, 4),
        ((-4, 24, 4), 4 if quick else 6, 17, 3, 4),
        ((13, -20, 9), 4 if quick else 6, 16, 2, 4),
    ]
    centers = []
    for center, levels, outer, step, height in specs:
        add_hopper_square(points, center, levels, outer, step, height)
        centers.append(np.array(center, dtype=float))
    for a, b in zip(centers[:-1], centers[1:]):
        add_tube(points, a + np.array([0, 0, 5], dtype=float), b + np.array([0, 0, 5], dtype=float), 4)
        add_tube(points, a + np.array([7, -7, 9], dtype=float), b + np.array([-7, 7, 9], dtype=float), 2)
    add_box(points, (-9, -9, -15), (9, 9, -6))
    return coords_array(points)


def pyrite_crystal_lattice_cluster(quick: bool = False) -> np.ndarray:
    points: set[tuple[int, int, int]] = set()
    span = 2 if quick else 3
    spacing = 16
    nodes = []
    for x in range(-span, span + 1):
        for y in range(-span, span + 1):
            for z in range(-span, span + 1):
                if abs(x) + abs(y) + abs(z) <= span + 1 and (x + 2 * y - z) % 3 != 1:
                    p = np.array([x * spacing, y * spacing, z * spacing], dtype=float)
                    nodes.append((x, y, z, p))
                    d = 5 if (x + y + z) % 2 == 0 else 4
                    add_box(points, (int(p[0] - d), int(p[1] - d), int(p[2] - d)), (int(p[0] + d), int(p[1] + d), int(p[2] + d)))
                    add_octahedron(points, p + np.array([0, 0, d + 3]), 4)
                    add_octahedron(points, p - np.array([0, 0, d + 3]), 4)
                    d = 5
                    add_box(points, (int(p[0] - d), int(p[1] - 1), int(p[2] - 1)), (int(p[0] + d), int(p[1] + 1), int(p[2] + 1)))
                    add_box(points, (int(p[0] - 1), int(p[1] - d), int(p[2] - 1)), (int(p[0] + 1), int(p[1] + d), int(p[2] + 1)))
                    add_box(points, (int(p[0] - 1), int(p[1] - 1), int(p[2] - d)), (int(p[0] + 1), int(p[1] + 1), int(p[2] + d)))
    node_map = {(x, y, z): p for x, y, z, p in nodes}
    for key, p in node_map.items():
        for off in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
            other = (key[0] + off[0], key[1] + off[1], key[2] + off[2])
            if other in node_map:
                add_tube(points, p, node_map[other], 2)
        for off in [(1, 1, 0), (1, 0, 1), (0, 1, 1)]:
            other = (key[0] + off[0], key[1] + off[1], key[2] + off[2])
            if other in node_map:
                add_tube(points, p, node_map[other], 1)
    if (0, 0, 0) in node_map:
        for _key, p in node_map.items():
            add_tube(points, node_map[(0, 0, 0)], p, 1)
    return coords_array(points)


def porous_coral_mineral(seed: int = 20260511, quick: bool = False) -> np.ndarray:
    rng = np.random.default_rng(seed)
    points: set[tuple[int, int, int]] = set()
    anchors = [
        np.array([0.0, 0.0, 0.0]),
        np.array([18.0, -8.0, 9.0]),
        np.array([-16.0, 12.0, -6.0]),
        np.array([8.0, 19.0, 16.0]),
        np.array([-10.0, -18.0, 12.0]),
    ]
    for a, b in zip(anchors[:-1], anchors[1:]):
        add_tube(points, a, b, 7)
    for a in anchors:
        add_ball(points, a, 12 if not quick else 10)
    lump_count = 38 if quick else 82
    for _ in range(lump_count):
        base = anchors[int(rng.integers(0, len(anchors)))]
        offset = rng.normal(0, 10.0, 3)
        p = base + offset
        add_tube(points, base, p, int(rng.integers(2, 5)))
        add_ball(points, p, int(rng.integers(4, 8)))
    pore_count = 16 if quick else 36
    for _ in range(pore_count):
        base = anchors[int(rng.integers(0, len(anchors)))]
        p = base + rng.normal(0, 9.0, 3)
        remove_ball(points, p, int(rng.integers(2, 5)))
    for a, b in zip(anchors[:-1], anchors[1:]):
        add_tube(points, a, b, 4)
    return coords_array(points)


def root_vine_connected_control(seed: int = 20260510, quick: bool = False) -> np.ndarray:
    rng = np.random.default_rng(seed)
    points: set[tuple[int, int, int]] = set()
    trunk = [np.array([0.0, 0.0, -35.0])]
    for i in range(1, 52 if not quick else 32):
        prev = trunk[-1]
        drift = np.array([
            3.2 * math.sin(i * 0.33),
            3.0 * math.cos(i * 0.27),
            2.1,
        ])
        trunk.append(prev + drift)
    for i, (a, b) in enumerate(zip(trunk[:-1], trunk[1:])):
        add_tube(points, a, b, 4 if i < 16 else 3)
        if i % 7 == 0 and i > 4:
            for sign in (-1, 1):
                angle = i * 0.47 + sign * 1.1
                side = np.array([math.cos(angle), math.sin(angle), rng.uniform(-0.15, 0.45)])
                side = side / np.linalg.norm(side)
                tip = b + side * rng.uniform(15, 24)
                add_tube(points, b, tip, 2)
                sub = tip + np.array([-side[1], side[0], 0.35]) * rng.uniform(7, 12)
                add_tube(points, tip, sub, 1)
                add_ball(points, sub, 2)
    for p in trunk[::6]:
        add_ball(points, p, 5)
    return coords_array(points)


def sci_fi_recursive_module(quick: bool = False) -> np.ndarray:
    points: set[tuple[int, int, int]] = set()

    def add_frame(center: np.ndarray, size: int, z_thick: int) -> None:
        cx, cy, cz = np.rint(center).astype(int)
        inner = max(size - 7, 3)
        add_box(points, (cx - size, cy - size, cz - z_thick), (cx + size, cy - inner, cz + z_thick))
        add_box(points, (cx - size, cy + inner, cz - z_thick), (cx + size, cy + size, cz + z_thick))
        add_box(points, (cx - size, cy - inner, cz - z_thick), (cx - inner, cy + inner, cz + z_thick))
        add_box(points, (cx + inner, cy - inner, cz - z_thick), (cx + size, cy + inner, cz + z_thick))
        add_box(points, (cx - 2, cy - 2, cz - size), (cx + 2, cy + 2, cz + size))
        add_box(points, (cx - size, cy - 2, cz - 2), (cx + size, cy + 2, cz + 2))
        add_box(points, (cx - 2, cy - size, cz - 2), (cx + 2, cy + size, cz + 2))

    centers = [np.array([0, 0, 0], dtype=float)]
    add_frame(centers[0], 22, 3)
    offsets = [
        np.array([28, 0, 14], dtype=float),
        np.array([-28, 0, -14], dtype=float),
        np.array([0, 28, -10], dtype=float),
        np.array([0, -28, 10], dtype=float),
    ]
    for off in offsets:
        c = off
        centers.append(c)
        add_frame(c, 13, 2)
        add_tube(points, centers[0], c, 4)
        for side in [np.array([8, 8, 5], dtype=float), np.array([-8, 8, -5], dtype=float)]:
            child = c + side
            add_frame(child, 7, 1)
            add_tube(points, c, child, 2)
    for c in centers:
        add_ball(points, c, 5)
    return coords_array(points)


def occupancy_stats(coords: np.ndarray) -> dict:
    coords = np.unique(np.asarray(coords, dtype=np.int32), axis=0)
    if len(coords) == 0:
        return {"occupied_voxels": 0, "occupancy_component_count_6n": 0, "largest_occupancy_component_ratio_6n": 0.0}
    occupied = {tuple(row) for row in coords.tolist()}
    seen: set[tuple[int, int, int]] = set()
    sizes = []
    offsets = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    for start in occupied:
        if start in seen:
            continue
        q: deque[tuple[int, int, int]] = deque([start])
        seen.add(start)
        n = 0
        while q:
            x, y, z = q.popleft()
            n += 1
            for dx, dy, dz in offsets:
                nxt = (x + dx, y + dy, z + dz)
                if nxt in occupied and nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        sizes.append(n)
    largest = max(sizes) if sizes else 0
    return {
        "occupied_voxels": int(len(coords)),
        "occupancy_component_count_6n": int(len(sizes)),
        "largest_occupancy_component_ratio_6n": float(largest / max(len(coords), 1)),
    }


def coords_to_mesh(coords: np.ndarray):
    import trimesh

    coords = np.unique(np.asarray(coords, dtype=np.int32), axis=0)
    lo = coords.min(axis=0) - 2
    hi = coords.max(axis=0) + 3
    shape = tuple((hi - lo + 1).astype(int).tolist())
    volume = np.zeros(shape, dtype=np.uint8)
    shifted = coords - lo
    volume[shifted[:, 0], shifted[:, 1], shifted[:, 2]] = 1
    try:
        from skimage import measure

        verts, faces, _normals, _values = measure.marching_cubes(volume.astype(np.float32), level=0.5)
        verts = verts + lo.astype(np.float32)
        mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    except Exception:
        pitch = 1.0
        mesh = trimesh.voxel.ops.matrix_to_marching_cubes(volume.astype(bool), pitch=pitch)
        mesh.apply_translation(lo.astype(float))
    center = (mesh.bounds[0] + mesh.bounds[1]) / 2.0
    scale = max(float((mesh.bounds[1] - mesh.bounds[0]).max()), 1e-6)
    mesh.apply_translation(-center)
    mesh.apply_scale(2.0 / scale)
    try:
        mesh.merge_vertices(digits_vertex=5)
        mesh.remove_duplicate_faces()
        mesh.remove_degenerate_faces()
    except Exception:
        pass
    pieces = mesh.split(only_watertight=False)
    if len(pieces) > 1:
        mesh = coords_to_exposed_voxel_mesh(coords)
        center = (mesh.bounds[0] + mesh.bounds[1]) / 2.0
        scale = max(float((mesh.bounds[1] - mesh.bounds[0]).max()), 1e-6)
        mesh.apply_translation(-center)
        mesh.apply_scale(2.0 / scale)
    return mesh


def coords_to_exposed_voxel_mesh(coords: np.ndarray):
    import trimesh

    coords = np.unique(np.asarray(coords, dtype=np.int32), axis=0)
    occupied = {tuple(row) for row in coords.tolist()}
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    vid: dict[tuple[int, int, int], int] = {}

    def vertex_id(p: tuple[int, int, int]) -> int:
        if p not in vid:
            vid[p] = len(vertices)
            vertices.append((float(p[0]), float(p[1]), float(p[2])))
        return vid[p]

    face_defs = [
        ((1, 0, 0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
        ((-1, 0, 0), [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
        ((0, 1, 0), [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]),
        ((0, -1, 0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
        ((0, 0, 1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
        ((0, 0, -1), [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)]),
    ]
    for x, y, z in occupied:
        for normal, corners in face_defs:
            neighbor = (x + normal[0], y + normal[1], z + normal[2])
            if neighbor in occupied:
                continue
            ids = [vertex_id((x + cx, y + cy, z + cz)) for cx, cy, cz in corners]
            faces.append((ids[0], ids[1], ids[2]))
            faces.append((ids[0], ids[2], ids[3]))
    mesh = trimesh.Trimesh(vertices=np.asarray(vertices, dtype=np.float32), faces=np.asarray(faces, dtype=np.int64), process=True)
    try:
        mesh.merge_vertices(digits_vertex=5)
        mesh.remove_duplicate_faces()
        mesh.remove_degenerate_faces()
    except Exception:
        pass
    return mesh


def mesh_stats(mesh) -> dict:
    pieces = mesh.split(only_watertight=False)
    sizes = [len(p.vertices) for p in pieces] or [0]
    bounds = mesh.bounds if len(mesh.vertices) else np.zeros((2, 3))
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


def write_metrics(out_dir: Path, rows: list[dict]) -> None:
    (out_dir / "metrics.json").write_text(json.dumps({"rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    fields = [
        "label",
        "family",
        "obj_path",
        "vertices",
        "faces",
        "mesh_component_count",
        "largest_mesh_component_vertex_ratio",
        "occupied_voxels",
        "occupancy_component_count_6n",
        "largest_occupancy_component_ratio_6n",
        "bbox_diag",
        "surface_area",
        "trellis2_texturing_fit",
        "root_baseline_fit",
    ]
    with (out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fields})


def render_contact_sheet(out_dir: Path, rows: list[dict]) -> Path:
    contact = out_dir / "contact_sheet.png"
    renderer = ASSET_DIR / "render_mesh_contact_sheet.py"
    if renderer.exists():
        cmd = [sys.executable, str(renderer), "--out", str(contact), "--views", "iso", "front", "side", "--max-faces", "90000"]
        for row in rows:
            cmd.extend(["--case", f"{row['label']}={row['obj_path']}"])
        try:
            subprocess.run(cmd, check=True)
            return contact
        except Exception:
            pass
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import trimesh

    fig = plt.figure(figsize=(11, 3 * len(rows)))
    for i, row in enumerate(rows, 1):
        mesh = trimesh.load(row["obj_path"], force="mesh", process=False)
        verts = np.asarray(mesh.vertices)
        faces = np.asarray(mesh.faces)
        if len(faces) > 70000:
            faces = faces[np.linspace(0, len(faces) - 1, 70000).astype(np.int64)]
        ax = fig.add_subplot(len(rows), 1, i, projection="3d")
        center = (verts.min(0) + verts.max(0)) / 2
        scale = max(float((verts.max(0) - verts.min(0)).max()), 1e-6)
        vv = (verts - center) / scale
        tri = vv[faces]
        coll = Poly3DCollection(tri, linewidths=0.0)
        coll.set_facecolor((0.54, 0.68, 0.62, 1.0))
        ax.add_collection3d(coll)
        ax.set_xlim(-0.55, 0.55)
        ax.set_ylim(-0.55, 0.55)
        ax.set_zlim(-0.55, 0.55)
        ax.set_axis_off()
        ax.view_init(22, -45)
        ax.set_title(row["label"], fontsize=9)
    fig.tight_layout()
    fig.savefig(contact, dpi=180)
    plt.close(fig)
    return contact


def write_chinese_doc(doc_path: Path, out_dir: Path, rows: list[dict]) -> None:
    table = "\n".join(
        f"| {r['label']} | {r['family']} | {r['occupancy_component_count_6n']} | "
        f"{r['largest_occupancy_component_ratio_6n']:.4f} | {r['trellis2_texturing_fit']} |"
        for r in rows
    )
    text = f"""# 连通 scaffold mesh cases v2（2026-05-09）

输出目录：`{out_dir}`

本批次是 connected scaffold v2，目标是修正 v1 中 DLA/coral 过扁、bismuth 过像单个台阶金字塔的问题。所有 case 都先在体素 occupancy 上生成并检查连通，再导出 OBJ 三角 mesh 和 mesh render contact sheet；不是点云散点。

## 指标摘要

| case | 类型 | occupancy components | largest component ratio | Trellis2 texturing 适配 |
|---|---|---:|---:|---|
{table}

## 可作为 DLA / 晶体路线替代 root 的候选

- `volumetric_dla_coral_cluster`：DLA/coral 主候选。v2 用多条 3D 种子臂和不同高度的瘤状末端强制体积扩展，避免 v1 薄片化。
- `bismuth_hopper_cluster`：bismuth 主候选。它由多个偏移中心的 square hopper/terrace 组成，并用桥接梁连接，不再是单个台阶金字塔。
- `pyrite_crystal_lattice_cluster`：晶格/晶簇候选。节点包含立方 pyrite 块、octahedral facet 暗示和轴向/对角晶棒，faceted/lattice signal 最明确。
- `porous_coral_mineral`：多孔矿物/coral 候选。它有厚骨架、团块和局部孔洞，适合测试 coral/mineral texturing。
- `root_vine_connected_control`：生物根/藤蔓 control baseline，用来对比有明确骨架扫掠的连通结构。
- `sci_fi_recursive_module`：硬表面 recursive module control，用来测试非自然形态的连通 scaffold 和纹理覆盖。

## 后续 Trellis2 texturing 建议

优先送入 Trellis2 texturing 的候选：

1. `bismuth_hopper_cluster`：最值得送 bismuth texturing，台阶方环、多中心 hopper 和棱边足够清楚。
2. `volumetric_dla_coral_cluster`：最值得送 DLA/coral texturing，体积感比 v1 强，末端团簇可承载 coral/mineral 纹理。
3. `pyrite_crystal_lattice_cluster`：适合作为晶体/矿物第三候选，晶棒和 faceted 节点对材质提示更友好。
4. `porous_coral_mineral`：适合做 coral/mineral 扩展候选，视觉上偏岩骨架/孔洞。

`root_vine_connected_control` 和 `sci_fi_recursive_module` 建议保留为 baseline/control：前者验证连通骨架，后者验证硬表面递归模块，不建议作为 DLA/晶体主视觉结果。

## 产物

- metrics JSON：`{out_dir / 'metrics.json'}`
- metrics CSV：`{out_dir / 'metrics.csv'}`
- mesh contact sheet：`{out_dir / 'contact_sheet.png'}`
- OBJ：`{out_dir}/*/*.obj`
"""
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(text, encoding="utf-8")


def generate_all(out_dir: Path, quick: bool = False, write_doc: bool = False, doc_path: Path = DEFAULT_DOC) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    cases = [
        ("volumetric_dla_coral_cluster", "volumetric DLA/coral cluster", volumetric_dla_coral_cluster(quick=quick), "very_high", "high"),
        ("bismuth_hopper_cluster", "bismuth hopper cluster", bismuth_hopper_cluster(quick=quick), "very_high", "high"),
        ("pyrite_crystal_lattice_cluster", "pyrite/crystal lattice cluster", pyrite_crystal_lattice_cluster(quick=quick), "high", "medium_high"),
        ("porous_coral_mineral", "porous coral/mineral", porous_coral_mineral(quick=quick), "high", "medium_high"),
        ("root_vine_connected_control", "root/vine connected control", root_vine_connected_control(quick=quick), "baseline", "very_high"),
        ("sci_fi_recursive_module", "sci-fi recursive module", sci_fi_recursive_module(quick=quick), "control", "medium"),
    ]
    rows = []
    for label, family, coords, texturing_fit, root_fit in cases:
        coords = largest_occupancy_component(coords)
        mesh = coords_to_mesh(coords)
        case_dir = out_dir / label
        case_dir.mkdir(parents=True, exist_ok=True)
        obj_path = case_dir / f"{label}.obj"
        mesh.export(obj_path)
        row = {
            "label": label,
            "family": family,
            "obj_path": str(obj_path),
            "trellis2_texturing_fit": texturing_fit,
            "root_baseline_fit": root_fit,
        }
        row.update(mesh_stats(mesh))
        row.update(occupancy_stats(coords))
        rows.append(row)
    write_metrics(out_dir, rows)
    contact = render_contact_sheet(out_dir, rows)
    if write_doc:
        write_chinese_doc(doc_path, out_dir, rows)
    summary = {"out_dir": str(out_dir), "contact_sheet": str(contact), "rows": rows}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--no-doc", action="store_true")
    args = parser.parse_args()
    summary = generate_all(args.out, quick=args.quick, write_doc=not args.no_doc, doc_path=args.doc)
    print(json.dumps({"out_dir": summary["out_dir"], "contact_sheet": summary["contact_sheet"], "cases": len(summary["rows"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
