#!/usr/bin/env python3
"""Build a corrected L-system tree-root case with an upward crown frame.

The failed public-guide case stamped repeated tree/root chunks in a mismatched
local frame, so several children float or point sideways.  This script creates a
diagnostic replacement mesh where the root module is normalized to +Z, children
attach through explicit crown handles, and every recursive copy is bridged to
its parent before export.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "results/lsystem_tree_root_orientation_fix_20260510"


def unit(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    if n <= 1e-9:
        return np.array([0.0, 0.0, 1.0], dtype=float)
    return v / n


def basis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = unit(axis)
    ref = np.array([0.0, 0.0, 1.0]) if abs(w[2]) < 0.82 else np.array([1.0, 0.0, 0.0])
    u = unit(np.cross(w, ref))
    v = unit(np.cross(w, u))
    return u, v, w


def add_frustum(
    verts: list[np.ndarray],
    faces: list[list[int]],
    mats: list[int],
    p0: np.ndarray,
    p1: np.ndarray,
    r0: float,
    r1: float,
    sides: int,
    mat: int,
    phase: float = 0.0,
) -> None:
    p0 = np.asarray(p0, dtype=float)
    p1 = np.asarray(p1, dtype=float)
    u, v, _w = basis(p1 - p0)
    base = len(verts)
    for i in range(sides):
        th = 2.0 * math.pi * i / sides + phase
        verts.append(p0 + r0 * (math.cos(th) * u + math.sin(th) * v))
    for i in range(sides):
        th = 2.0 * math.pi * i / sides + phase
        verts.append(p1 + r1 * (math.cos(th) * u + math.sin(th) * v))
    c0 = len(verts)
    verts.append(p0)
    c1 = len(verts)
    verts.append(p1)
    for i in range(sides):
        j = (i + 1) % sides
        faces.append([base + i, base + j, base + sides + j])
        mats.append(mat)
        faces.append([base + i, base + sides + j, base + sides + i])
        mats.append(mat)
        faces.append([c0, base + j, base + i])
        mats.append(mat)
        faces.append([c1, base + sides + i, base + sides + j])
        mats.append(mat)


def add_ellipsoid(
    verts: list[np.ndarray],
    faces: list[list[int]],
    mats: list[int],
    center: np.ndarray,
    radii: tuple[float, float, float],
    mat: int,
    seg: int = 16,
    rings: int = 8,
) -> None:
    center = np.asarray(center, dtype=float)
    rx, ry, rz = radii
    base = len(verts)
    for a in range(rings + 1):
        phi = -math.pi / 2.0 + math.pi * a / rings
        cp = math.cos(phi)
        sp = math.sin(phi)
        for b in range(seg):
            th = 2.0 * math.pi * b / seg
            verts.append(center + np.array([rx * cp * math.cos(th), ry * cp * math.sin(th), rz * sp]))
    for a in range(rings):
        for b in range(seg):
            nb = (b + 1) % seg
            i0 = base + a * seg + b
            i1 = base + a * seg + nb
            i2 = base + (a + 1) * seg + nb
            i3 = base + (a + 1) * seg + b
            faces.append([i0, i1, i2])
            mats.append(mat)
            faces.append([i0, i2, i3])
            mats.append(mat)


def add_needles(
    verts: list[np.ndarray],
    faces: list[list[int]],
    mats: list[int],
    rng: np.random.Generator,
    origin: np.ndarray,
    axis: np.ndarray,
    length: float,
    radius: float,
    count: int,
    mat: int = 1,
) -> None:
    axis = unit(axis)
    u, v, w = basis(axis)
    for k in range(count):
        th = 2.0 * math.pi * (k / count) + rng.normal(0.0, 0.06)
        z = rng.uniform(-0.36, 0.36)
        shell_r = radius * (1.0 - 0.55 * max(z, 0.0)) * rng.uniform(0.74, 1.05)
        anchor = np.asarray(origin) + w * (z * length * 0.38) + (math.cos(th) * u + math.sin(th) * v) * shell_r * 0.32
        direction = unit(w * 0.38 + (math.cos(th) * u + math.sin(th) * v) * 1.15 + rng.normal(0.0, 0.045, 3))
        tip = anchor + direction * rng.uniform(length * 0.18, length * 0.34)
        add_frustum(verts, faces, mats, anchor, tip, radius * 0.046, radius * 0.012, sides=5, mat=mat, phase=rng.uniform(0.0, 1.0))


def add_pine_module(
    verts: list[np.ndarray],
    faces: list[list[int]],
    mats: list[int],
    rng: np.random.Generator,
    base: np.ndarray,
    axis: np.ndarray,
    scale: float,
    depth: int,
    yaw: float,
) -> None:
    axis = unit(axis)
    u, v, w = basis(axis)
    base = np.asarray(base, dtype=float)
    top = base + w * (1.12 * scale)
    add_frustum(verts, faces, mats, base, top, 0.075 * scale, 0.026 * scale, sides=14, mat=0)

    handles: list[tuple[np.ndarray, np.ndarray]] = []
    whorls = [(0.20, 0.46, 7), (0.39, 0.37, 6), (0.57, 0.28, 5), (0.73, 0.20, 4), (0.88, 0.13, 3)]
    for wi, (h, spread, n) in enumerate(whorls):
        center = base + w * (h * 1.12 * scale)
        for k in range(n):
            th = yaw + 2.0 * math.pi * k / n + wi * 0.23 + rng.normal(0.0, 0.035)
            radial = math.cos(th) * u + math.sin(th) * v
            p1 = center + radial * (spread * scale) + w * ((0.10 + 0.18 * h) * scale)
            add_frustum(verts, faces, mats, center, p1, 0.021 * scale * (1.0 - h * 0.45), 0.007 * scale, sides=8, mat=0)
            needle_count = 13 if scale > 0.42 else (9 if scale > 0.20 else 5)
            add_needles(verts, faces, mats, rng, center * 0.30 + p1 * 0.70, radial + 0.35 * w, 0.45 * scale * (1.0 - h * 0.22), 0.145 * scale, needle_count)
            if scale > 0.20:
                puff_scale = (0.075 + 0.035 * (1.0 - h)) * scale
                add_ellipsoid(verts, faces, mats, p1 - radial * 0.035 * scale, (puff_scale * 1.25, puff_scale * 0.82, puff_scale * 0.58), mat=1, seg=12, rings=6)
                if (wi + k) % 3 == 0:
                    add_ellipsoid(verts, faces, mats, p1 + w * 0.018 * scale, (puff_scale * 0.95, puff_scale * 0.58, puff_scale * 0.42), mat=2, seg=10, rings=5)
            if wi in {1, 2, 3} and k % max(1, n // 3) == 0:
                handles.append((p1, unit(radial * 0.82 + w * 0.62)))

    add_ellipsoid(verts, faces, mats, top + w * 0.045 * scale, (0.085 * scale, 0.085 * scale, 0.18 * scale), mat=2)
    add_needles(verts, faces, mats, rng, top - w * 0.08 * scale, w, 0.56 * scale, 0.18 * scale, 24 if scale > 0.25 else 10)

    if depth <= 0:
        return
    rng.shuffle(handles)
    for i, (hpos, hdir) in enumerate(handles[: 4 if depth > 1 else 3]):
        child_scale = scale * (0.43 if depth > 1 else 0.38) * rng.uniform(0.90, 1.08)
        child_axis = unit(hdir + np.array([0.0, 0.0, 0.55]) + rng.normal(0.0, 0.035, 3))
        child_base = hpos + child_axis * (0.035 * scale)
        add_frustum(verts, faces, mats, hpos, child_base, 0.015 * scale, 0.035 * child_scale, sides=8, mat=0)
        add_pine_module(verts, faces, mats, rng, child_base, child_axis, child_scale, depth - 1, yaw + i * 0.65 + rng.normal(0.0, 0.05))


def build_mesh(seed: int, depth: int) -> tuple[trimesh.Trimesh, np.ndarray]:
    rng = np.random.default_rng(seed)
    verts: list[np.ndarray] = []
    faces: list[list[int]] = []
    mats: list[int] = []

    add_pine_module(verts, faces, mats, rng, np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0]), 1.0, depth=depth, yaw=0.15)
    for k in range(9):
        th = 2.0 * math.pi * k / 9.0 + rng.normal(0.0, 0.06)
        radial = np.array([math.cos(th), math.sin(th), -0.18])
        p0 = np.array([0.0, 0.0, 0.06])
        p1 = p0 + unit(radial) * rng.uniform(0.34, 0.58)
        add_frustum(verts, faces, mats, p0, p1, 0.030, 0.010, sides=8, mat=3)
        for _ in range(2):
            side = unit(radial + rng.normal(0.0, 0.20, 3) + np.array([0.0, 0.0, -0.18]))
            add_frustum(verts, faces, mats, p1, p1 + side * rng.uniform(0.10, 0.21), 0.010, 0.004, sides=6, mat=3)

    vertices = np.asarray(verts, dtype=np.float32)
    faces_np = np.asarray(faces, dtype=np.int64)
    bounds = np.vstack([vertices.min(axis=0), vertices.max(axis=0)])
    vertices[:, :2] -= (bounds[0, :2] + bounds[1, :2]) / 2.0
    vertices[:, 2] -= bounds[0, 2]
    scale = 2.85 / max(1e-6, float((vertices.max(axis=0) - vertices.min(axis=0)).max()))
    vertices *= scale
    return trimesh.Trimesh(vertices=vertices, faces=faces_np, process=False), np.asarray(mats, dtype=np.int64)


def export_glb(mesh: trimesh.Trimesh, mats: np.ndarray, path: Path) -> None:
    colors = [
        ("warm brown trunk", [0.42, 0.25, 0.14, 1.0]),
        ("snow cedar needles", [0.13, 0.33, 0.20, 1.0]),
        ("pale new crown growth", [0.68, 0.62, 0.52, 1.0]),
        ("pale root wood", [0.55, 0.45, 0.40, 1.0]),
    ]
    scene = trimesh.Scene()
    for mi, (name, color) in enumerate(colors):
        idx = np.where(mats == mi)[0]
        if len(idx) == 0:
            continue
        sub = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces[idx], process=False)
        sub.visual = trimesh.visual.ColorVisuals(sub, face_colors=np.tile(np.asarray(color) * 255.0, (len(sub.faces), 1)).astype(np.uint8))
        scene.add_geometry(sub, geom_name=name, node_name=name)
    scene.export(path)


def render_preview(mesh: trimesh.Trimesh, mats: np.ndarray, path: Path, elev: float, azim: float, bg: str = "#d9e1e8") -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(8, 8), dpi=180)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor(bg)
    fig.patch.set_facecolor(bg)

    faces = mesh.faces
    max_faces = 90000
    if len(faces) > max_faces:
        sel = np.linspace(0, len(faces) - 1, max_faces).astype(int)
        faces = faces[sel]
        mats = mats[sel]

    tri = mesh.vertices[faces]
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    normals = normals / np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-9)
    light = unit(np.array([-0.25, -0.45, 0.85]))
    shade = 0.50 + 0.50 * np.clip(normals.dot(light), 0.0, 1.0)
    palette = np.array(
        [
            [0.42, 0.25, 0.14, 1.0],
            [0.13, 0.33, 0.20, 1.0],
            [0.68, 0.62, 0.52, 1.0],
            [0.55, 0.45, 0.40, 1.0],
        ]
    )
    colors = palette[mats].copy()
    colors[:, :3] *= shade[:, None]
    ax.add_collection3d(Poly3DCollection(tri, facecolors=colors, linewidths=0.0, alpha=1.0))

    bounds = mesh.bounds
    pad = 0.38
    z0 = bounds[0, 2] - 0.01
    sx = max(abs(bounds[0, 0]), abs(bounds[1, 0])) + pad
    sy = max(abs(bounds[0, 1]), abs(bounds[1, 1])) + pad
    platform = np.array([[-sx, -sy, z0], [sx, -sy, z0], [sx, sy, z0], [-sx, sy, z0]])
    ax.add_collection3d(Poly3DCollection([platform], facecolors=(0.84, 0.87, 0.87, 1.0), linewidths=0.0, alpha=1.0))

    center = (bounds[0] + bounds[1]) / 2.0
    extent = (bounds[1] - bounds[0]).max() * 0.68
    ax.set_xlim(center[0] - extent, center[0] + extent)
    ax.set_ylim(center[1] - extent, center[1] + extent)
    ax.set_zlim(z0, bounds[1, 2] + 0.10)
    ax.view_init(elev=elev, azim=azim)
    ax.set_proj_type("persp")
    ax.set_axis_off()
    plt.subplots_adjust(0, 0, 1, 1)
    fig.savefig(path, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260510)
    parser.add_argument("--depth", type=int, default=2)
    args = parser.parse_args()

    out = args.out
    mesh_dir = out / "mesh"
    glb_dir = out / "glb"
    render_dir = out / "renders"
    for directory in [mesh_dir, glb_dir, render_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    mesh, mats = build_mesh(args.seed, args.depth)
    obj_path = mesh_dir / "lsystem_tree_root_upward_crown_handles_fix.obj"
    glb_path = glb_dir / "lsystem_tree_root_upward_crown_handles_fix.glb"
    iso_path = render_dir / "lsystem_tree_root_upward_crown_handles_fix_iso.png"
    front_path = render_dir / "lsystem_tree_root_upward_crown_handles_fix_front.png"
    mesh.export(obj_path)
    export_glb(mesh, mats, glb_path)
    render_preview(mesh, mats, iso_path, elev=18, azim=-48)
    render_preview(mesh, mats, front_path, elev=11, azim=-90)

    components = mesh.split(only_watertight=False)
    total_area = float(mesh.area) if mesh.area else 0.0
    largest_area = max((float(component.area) for component in components), default=0.0)
    summary = {
        "kind": "lsystem_tree_root_orientation_fix",
        "diagnosis_old_case": "old case has wrong root/crown local frame plus detached stamp-style child chunks",
        "fix": "normalize original module to +Z crown frame; attach children through upper crown handles; add explicit bridge geometry before recursive copies",
        "seed": args.seed,
        "depth": args.depth,
        "obj": str(obj_path),
        "glb": str(glb_path),
        "iso_render": str(iso_path),
        "front_render": str(front_path),
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "surface_components": int(len(components)),
        "largest_component_area_ratio": largest_area / total_area if total_area > 0.0 else 0.0,
        "bbox": (mesh.bounds[1] - mesh.bounds[0]).round(4).tolist(),
        "status": "geometry_preview_ok",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
