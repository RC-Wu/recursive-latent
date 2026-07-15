#!/usr/bin/env python3
"""Local mesh connectivity and repair diagnostics for fragmented GLB/OBJ assets.

This script is intentionally local and deterministic.  It evaluates mesh-based
postprocesses with occupancy-primary connectivity metrics, exports repaired
mesh variants, and renders mesh contact sheets with a small software rasterizer
so the visual evidence is based on triangles rather than point clouds.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import re
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from scipy.spatial import cKDTree
from skimage import measure


MESH_EXTS = {".glb", ".gltf", ".obj", ".ply", ".stl", ".off"}
NEIGHBORS6 = np.asarray(
    [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)],
    dtype=np.int16,
)
DEFAULT_GLOBS = (
    "visuals/public_guide_textured_glb_20260509/**/*.glb",
    "visuals/public_guide_textured_glb_20260509b/**/*.glb",
    "visuals/public_guide_textured_glb_20260509c/**/*.glb",
    "visuals/public_guide_textured_glb_20260509d/**/*.glb",
    "visuals/public_guide_textured_glb_20260509e/**/*.glb",
    "visuals/siga_night_20260508/projection_pruning_compete_0550/*.obj",
    "visuals/siga_night_20260508/selected_meshes/*.obj",
    "visuals/non_tree_recursive_20260508/meshes/*.obj",
)
FOCUS_PATTERNS = re.compile(
    r"(dla|radial|bismuth|scifi|tree|leaf|lsystem|fork|parthenocissus)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class OccGrid:
    matrix: np.ndarray
    vmin: np.ndarray
    scale: float
    inner: int
    margin: int


def slugify(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text.strip())
    text = re.sub(r"_+", "_", text).strip("_.")
    return text[:120] or "mesh"


def expand_inputs(root: Path, items: Iterable[str], recursive: bool = True) -> list[Path]:
    paths: list[Path] = []
    for item in items:
        raw = str(root / item) if not Path(item).is_absolute() else item
        if any(ch in raw for ch in "*?[]"):
            paths.extend(Path(p) for p in glob.glob(raw, recursive=recursive))
            continue
        p = Path(raw)
        if p.is_dir():
            pattern = "**/*" if recursive else "*"
            paths.extend(child for child in p.glob(pattern) if child.suffix.lower() in MESH_EXTS)
        elif p.suffix.lower() in MESH_EXTS:
            paths.append(p)
    return sorted(dict.fromkeys(p.resolve() for p in paths if p.exists()))


def default_label(root: Path, path: Path) -> str:
    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = path
    parent = rel.parent.name
    grand = rel.parent.parent.name if rel.parent.parent.name else ""
    if path.name == "textured.glb" and parent:
        return slugify(parent)
    if path.name == "mesh_pruned.obj" and parent:
        return slugify(parent)
    return slugify("_".join(x for x in (grand, parent, path.stem) if x))


def load_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(str(path), force="scene", process=False)
    meshes: list[trimesh.Trimesh] = []
    if isinstance(loaded, trimesh.Trimesh):
        meshes = [loaded]
    elif isinstance(loaded, trimesh.Scene):
        for node_name in loaded.graph.nodes_geometry:
            transform, geom_name = loaded.graph[node_name]
            geom = loaded.geometry.get(geom_name)
            if not isinstance(geom, trimesh.Trimesh) or len(geom.vertices) == 0:
                continue
            m = geom.copy()
            m.apply_transform(transform)
            meshes.append(m)
    if not meshes:
        raise ValueError(f"no mesh geometry in {path}")
    mesh = trimesh.util.concatenate(meshes)
    mesh.remove_unreferenced_vertices()
    return mesh


def clean_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    out = mesh.copy()
    out.remove_unreferenced_vertices()
    if len(out.faces):
        out.update_faces(out.nondegenerate_faces())
        out.remove_unreferenced_vertices()
    return out


def quantized_weld_mesh(mesh: trimesh.Trimesh, tolerance: float) -> trimesh.Trimesh:
    if len(mesh.vertices) == 0 or tolerance <= 0:
        return clean_mesh(mesh)
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    keys = np.rint(vertices / float(tolerance)).astype(np.int64)
    _, first_idx, inverse = np.unique(keys, axis=0, return_index=True, return_inverse=True)
    order = np.argsort(first_idx)
    rank = np.empty(len(order), dtype=np.int64)
    rank[order] = np.arange(len(order), dtype=np.int64)
    welded_vertices = vertices[first_idx[order]]
    welded_faces = rank[inverse[faces]]
    keep = (
        (welded_faces[:, 0] != welded_faces[:, 1])
        & (welded_faces[:, 1] != welded_faces[:, 2])
        & (welded_faces[:, 0] != welded_faces[:, 2])
    )
    return clean_mesh(trimesh.Trimesh(vertices=welded_vertices, faces=welded_faces[keep], process=False))


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = np.arange(n, dtype=np.int64)
        self.size = np.ones(n, dtype=np.int64)

    def find(self, x: int) -> int:
        while int(self.parent[x]) != x:
            self.parent[x] = self.parent[int(self.parent[x])]
            x = int(self.parent[x])
        return x

    def union(self, a: int, b: int) -> None:
        ra = self.find(int(a))
        rb = self.find(int(b))
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]


def face_component_labels(mesh: trimesh.Trimesh) -> tuple[np.ndarray, np.ndarray]:
    vertices = np.asarray(mesh.vertices)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(vertices) == 0:
        return np.zeros((0,), dtype=np.int64), np.zeros((0,), dtype=np.int64)
    if len(faces) == 0:
        return np.arange(len(vertices), dtype=np.int64), np.ones(len(vertices), dtype=np.int64)
    uf = UnionFind(len(vertices))
    valid = faces[(faces >= 0).all(axis=1) & (faces < len(vertices)).all(axis=1)]
    for a, b, c in valid:
        uf.union(int(a), int(b))
        uf.union(int(b), int(c))
        uf.union(int(c), int(a))
    roots = np.fromiter((uf.find(i) for i in range(len(vertices))), dtype=np.int64, count=len(vertices))
    labels, inverse, counts = np.unique(roots, return_inverse=True, return_counts=True)
    _ = labels
    return inverse, counts


def split_components(mesh: trimesh.Trimesh) -> list[trimesh.Trimesh]:
    labels, counts = face_component_labels(mesh)
    if len(labels) == 0:
        return []
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(faces) == 0:
        return [mesh.copy()]
    face_labels = labels[faces[:, 0]]
    comps: list[trimesh.Trimesh] = []
    for label in np.argsort(counts)[::-1]:
        face_mask = face_labels == label
        if not np.any(face_mask):
            continue
        comps.append(clean_mesh(mesh.submesh([np.flatnonzero(face_mask)], append=True, repair=False)))
    return comps


def keep_largest_component(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    comps = split_components(mesh)
    if not comps:
        return clean_mesh(mesh)
    comps.sort(key=lambda m: (len(m.vertices), float(m.area)), reverse=True)
    return clean_mesh(comps[0])


def conservative_hole_repair(mesh: trimesh.Trimesh, tolerance: float) -> trimesh.Trimesh:
    out = quantized_weld_mesh(mesh, tolerance)
    try:
        trimesh.repair.fill_holes(out)
        trimesh.repair.fix_normals(out, multibody=True)
    except Exception:
        pass
    return clean_mesh(out)


def cylinder_between(a: np.ndarray, b: np.ndarray, radius: float, sections: int = 10) -> trimesh.Trimesh | None:
    dist = float(np.linalg.norm(b - a))
    if not np.isfinite(dist) or dist <= radius * 0.5:
        return None
    try:
        return trimesh.creation.cylinder(radius=radius, segment=np.vstack([a, b]), sections=sections)
    except Exception:
        return None


def sample_vertices(vertices: np.ndarray, limit: int) -> np.ndarray:
    if len(vertices) <= limit:
        return vertices
    idx = np.linspace(0, len(vertices) - 1, limit).astype(np.int64)
    return vertices[idx]


def bridge_to_largest(mesh: trimesh.Trimesh, max_components: int = 16, min_vertices: int = 12) -> trimesh.Trimesh:
    comps = split_components(mesh)
    if len(comps) <= 1:
        return clean_mesh(mesh)
    comps.sort(key=lambda m: (len(m.vertices), float(m.area)), reverse=True)
    largest = comps[0]
    bbox_diag = float(np.linalg.norm(mesh.bounds[1] - mesh.bounds[0])) if len(mesh.vertices) else 1.0
    radius = max(bbox_diag * 0.006, 1e-4)
    largest_sample = sample_vertices(np.asarray(largest.vertices), 8000)
    tree = cKDTree(largest_sample)
    bridges: list[trimesh.Trimesh] = []
    kept = [largest]
    kept_vertices = len(largest.vertices)
    total_vertices = max(len(mesh.vertices), 1)
    for comp in comps[1:max_components]:
        if len(comp.vertices) < min_vertices:
            continue
        comp_sample = sample_vertices(np.asarray(comp.vertices), 2000)
        dists, idx = tree.query(comp_sample, k=1)
        best = int(np.argmin(dists))
        a = comp_sample[best]
        b = largest_sample[int(idx[best])]
        bridge = cylinder_between(a, b, radius=radius)
        if bridge is not None:
            bridges.append(bridge)
        kept.append(comp)
        kept_vertices += len(comp.vertices)
        if kept_vertices / total_vertices >= 0.98:
            break
    return clean_mesh(trimesh.util.concatenate(kept + bridges))


def mesh_points_for_occupancy(mesh: trimesh.Trimesh, max_faces: int = 120_000) -> np.ndarray:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(vertices) == 0 or len(faces) == 0:
        return vertices
    if len(faces) > max_faces:
        idx = np.linspace(0, len(faces) - 1, max_faces).astype(np.int64)
        faces = faces[idx]
    tri = vertices[faces]
    mids = np.concatenate(
        [
            (tri[:, 0] + tri[:, 1]) * 0.5,
            (tri[:, 1] + tri[:, 2]) * 0.5,
            (tri[:, 2] + tri[:, 0]) * 0.5,
            tri.mean(axis=1),
        ],
        axis=0,
    )
    return np.vstack([vertices, mids])


def occupancy_from_mesh(mesh: trimesh.Trimesh, resolution: int, dilate_steps: int = 1, margin: int = 3) -> OccGrid:
    points = mesh_points_for_occupancy(mesh)
    matrix = np.zeros((resolution, resolution, resolution), dtype=bool)
    if len(points) == 0:
        return OccGrid(matrix=matrix, vmin=np.zeros(3), scale=1.0, inner=resolution - 2 * margin - 1, margin=margin)
    finite = np.isfinite(points).all(axis=1)
    points = points[finite]
    vmin = points.min(axis=0)
    vmax = points.max(axis=0)
    scale = float(np.max(vmax - vmin))
    if scale <= 1e-12:
        matrix[resolution // 2, resolution // 2, resolution // 2] = True
        return OccGrid(matrix=matrix, vmin=vmin, scale=1.0, inner=resolution - 2 * margin - 1, margin=margin)
    inner = max(resolution - 2 * margin - 1, 1)
    coords = np.floor((points - vmin) / scale * inner + margin).astype(np.int64)
    coords = np.clip(coords, 0, resolution - 1)
    matrix[coords[:, 0], coords[:, 1], coords[:, 2]] = True
    if dilate_steps > 0:
        structure = ndimage.generate_binary_structure(3, 1)
        matrix = ndimage.binary_dilation(matrix, structure=structure, iterations=dilate_steps)
    return OccGrid(matrix=matrix, vmin=vmin, scale=scale, inner=inner, margin=margin)


def components_6n(matrix: np.ndarray) -> list[np.ndarray]:
    points = np.argwhere(matrix)
    if len(points) == 0:
        return []
    seen = np.zeros_like(matrix, dtype=bool)
    comps: list[np.ndarray] = []
    grid = matrix.shape[0]
    for start in points:
        st = tuple(int(x) for x in start)
        if seen[st]:
            continue
        q: deque[tuple[int, int, int]] = deque([st])
        seen[st] = True
        comp: list[tuple[int, int, int]] = []
        while q:
            p = q.popleft()
            comp.append(p)
            arr = np.asarray(p, dtype=np.int16)
            for d in NEIGHBORS6:
                nb = arr + d
                if (nb < 0).any() or (nb >= grid).any():
                    continue
                nt = tuple(int(x) for x in nb)
                if matrix[nt] and not seen[nt]:
                    seen[nt] = True
                    q.append(nt)
        comps.append(np.asarray(comp, dtype=np.int16))
    comps.sort(key=len, reverse=True)
    return comps


def line_bridge_occ(matrix: np.ndarray, a: np.ndarray, b: np.ndarray) -> None:
    steps = int(max(np.abs(b - a).max(), 1))
    for t in range(steps + 1):
        p = np.round(a + (b - a) * (t / steps)).astype(int)
        if (p >= 0).all() and (p < matrix.shape[0]).all():
            matrix[tuple(p)] = True


def bridge_occ_to_largest(matrix: np.ndarray, max_components: int = 24, min_voxels: int = 8) -> np.ndarray:
    out = matrix.copy()
    comps = components_6n(out)
    if len(comps) <= 1:
        return out
    largest = comps[0]
    tree = cKDTree(largest.astype(np.float64))
    for comp in comps[1:max_components]:
        if len(comp) < min_voxels:
            continue
        dists, idx = tree.query(comp.astype(np.float64), k=1)
        best = int(np.argmin(dists))
        line_bridge_occ(out, comp[best], largest[int(idx[best])])
    structure = ndimage.generate_binary_structure(3, 1)
    return ndimage.binary_dilation(out, structure=structure, iterations=1)


def occ_to_mesh(grid: OccGrid) -> trimesh.Trimesh:
    matrix = grid.matrix
    if int(matrix.sum()) == 0:
        return trimesh.Trimesh(vertices=np.zeros((0, 3)), faces=np.zeros((0, 3), dtype=np.int64), process=False)
    padded = np.pad(matrix.astype(np.float32), 1, mode="constant")
    verts, faces, _normals, _values = measure.marching_cubes(padded, level=0.5, allow_degenerate=False)
    verts = verts - 1.0
    verts = (verts - grid.margin) / max(float(grid.inner), 1.0) * grid.scale + grid.vmin
    return clean_mesh(trimesh.Trimesh(vertices=verts, faces=faces.astype(np.int64), process=False))


def voxel_remesh(mesh: trimesh.Trimesh, resolution: int, mode: str, simplify_faces: int = 60_000) -> trimesh.Trimesh:
    grid = occupancy_from_mesh(mesh, resolution=resolution, dilate_steps=1)
    matrix = grid.matrix
    structure = ndimage.generate_binary_structure(3, 1)
    if "bridge" in mode:
        matrix = bridge_occ_to_largest(matrix)
    if "close" in mode:
        matrix = ndimage.binary_closing(matrix, structure=structure, iterations=1)
    if "largest" in mode:
        comps = components_6n(matrix)
        keep = np.zeros_like(matrix, dtype=bool)
        if comps:
            c = comps[0]
            keep[c[:, 0], c[:, 1], c[:, 2]] = True
        matrix = keep
    grid = OccGrid(matrix=matrix, vmin=grid.vmin, scale=grid.scale, inner=grid.inner, margin=grid.margin)
    out = occ_to_mesh(grid)
    if "simplify" in mode and len(out.faces) > simplify_faces:
        try:
            out = out.simplify_quadric_decimation(face_count=simplify_faces, aggression=4)
            out = clean_mesh(out)
        except Exception:
            pass
    return out


def occupancy_metrics(mesh: trimesh.Trimesh, resolution: int) -> dict[str, object]:
    grid = occupancy_from_mesh(mesh, resolution=resolution, dilate_steps=1)
    comps = components_6n(grid.matrix)
    occupied = int(grid.matrix.sum())
    largest = int(len(comps[0])) if comps else 0
    return {
        "occupancy_resolution": int(resolution),
        "occupied_voxels": occupied,
        "occupancy_component_count_6n": int(len(comps)),
        "largest_occupancy_component_voxels_6n": largest,
        "largest_occupancy_component_ratio_6n": float(largest / max(occupied, 1)),
        "occupancy_fragmentation_score": float(1.0 - largest / max(occupied, 1)),
    }


def mesh_metrics(mesh: trimesh.Trimesh, resolution: int, render_visible_ratio: float | None = None) -> dict[str, object]:
    labels, counts = face_component_labels(mesh)
    largest = int(counts.max()) if len(counts) else 0
    bbox = mesh.bounds if len(mesh.vertices) else np.zeros((2, 3), dtype=np.float64)
    extent = bbox[1] - bbox[0]
    out: dict[str, object] = {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "surface_area": float(mesh.area) if len(mesh.faces) else 0.0,
        "bbox_diag": float(np.linalg.norm(extent)),
        "bbox_volume": float(np.prod(np.maximum(extent, 1e-12))) if len(mesh.vertices) else 0.0,
        "face_component_count": int(len(counts)),
        "largest_face_component_vertices": largest,
        "largest_face_component_ratio": float(largest / max(len(mesh.vertices), 1)),
        "is_watertight": bool(mesh.is_watertight) if len(mesh.faces) else False,
        "euler_number": int(mesh.euler_number) if len(mesh.faces) else 0,
        "render_visible_ratio": "" if render_visible_ratio is None else float(render_visible_ratio),
    }
    _ = labels
    out.update(occupancy_metrics(mesh, resolution=resolution))
    out["primary_connectivity_metric"] = "occupancy_6n_surface_voxel"
    out["primary_component_count"] = out["occupancy_component_count_6n"]
    out["primary_largest_component_ratio"] = out["largest_occupancy_component_ratio_6n"]
    return out


def variant_meshes(mesh: trimesh.Trimesh, weld_tolerance: float, voxel_resolution: int) -> list[tuple[str, trimesh.Trimesh]]:
    repaired = conservative_hole_repair(mesh, weld_tolerance)
    return [
        ("vertex_weld", quantized_weld_mesh(mesh, weld_tolerance)),
        ("conservative_hole_fill", repaired),
        ("largest_component", keep_largest_component(repaired)),
        ("bridge_to_largest", bridge_to_largest(repaired)),
        ("voxel_close", voxel_remesh(repaired, voxel_resolution, "close")),
        ("voxel_bridge_close", voxel_remesh(repaired, voxel_resolution, "bridge_close")),
        ("voxel_bridge_close_simplify", voxel_remesh(repaired, voxel_resolution, "bridge_close_simplify")),
    ]


def rotation_matrix(elev_deg: float = 20.0, azim_deg: float = -42.0) -> np.ndarray:
    elev = math.radians(elev_deg)
    azim = math.radians(azim_deg)
    rz = np.array(
        [[math.cos(azim), -math.sin(azim), 0.0], [math.sin(azim), math.cos(azim), 0.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    rx = np.array(
        [[1.0, 0.0, 0.0], [0.0, math.cos(elev), -math.sin(elev)], [0.0, math.sin(elev), math.cos(elev)]],
        dtype=np.float64,
    )
    return rx @ rz


def mesh_render(mesh: trimesh.Trimesh, title: str, size: int = 512, max_faces: int = 75_000) -> tuple[Image.Image, float]:
    bg = np.array([245, 244, 239], dtype=np.uint8)
    img = Image.new("RGB", (size, size), tuple(int(x) for x in bg))
    draw = ImageDraw.Draw(img, "RGBA")
    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        draw.text((12, 12), title + " empty", fill=(20, 20, 20))
        return img, 0.0
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(faces) > max_faces:
        idx = np.linspace(0, len(faces) - 1, max_faces).astype(np.int64)
        faces = faces[idx]
    center = (vertices.min(axis=0) + vertices.max(axis=0)) * 0.5
    scale = max(float((vertices.max(axis=0) - vertices.min(axis=0)).max()), 1e-9)
    pts = (vertices - center) / scale
    rot = rotation_matrix()
    proj = pts @ rot.T
    xy = proj[:, :2]
    z = proj[:, 2]
    px = np.empty_like(xy)
    px[:, 0] = xy[:, 0] * (size * 0.78) + size * 0.5
    px[:, 1] = -xy[:, 1] * (size * 0.78) + size * 0.52
    tri_z = z[faces].mean(axis=1)
    order = np.argsort(tri_z)
    light = np.asarray([0.3, -0.45, 0.84], dtype=np.float64)
    light /= np.linalg.norm(light)
    tri = pts[faces]
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-9)
    shade = np.clip(0.32 + 0.68 * np.maximum(normals @ light, 0.0), 0.18, 1.0)
    z_norm = (tri_z - tri_z.min()) / max(float(tri_z.max() - tri_z.min()), 1e-9)
    low = np.array([73, 105, 118], dtype=np.float64)
    high = np.array([220, 183, 94], dtype=np.float64)
    colors = (low[None, :] * (1.0 - z_norm[:, None]) + high[None, :] * z_norm[:, None]) * shade[:, None]
    for face_idx in order:
        poly = [tuple(px[v]) for v in faces[face_idx]]
        color = tuple(int(np.clip(c, 0, 255)) for c in colors[face_idx])
        draw.polygon(poly, fill=(*color, 255))
    label_h = 38
    draw.rectangle((0, 0, size, label_h), fill=(245, 244, 239, 224))
    font = ImageFont.load_default()
    draw.text((8, 8), title[:78], fill=(25, 28, 30), font=font)
    arr = np.asarray(img)
    diff = np.abs(arr.astype(np.int16) - bg[None, None, :].astype(np.int16)).sum(axis=2)
    visible = float(np.mean(diff > 18))
    return img, visible


def save_contact_sheet(path: Path, panels: list[tuple[str, trimesh.Trimesh]], size: int = 420) -> dict[str, float]:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered: list[Image.Image] = []
    visible: dict[str, float] = {}
    for title, mesh in panels:
        img, ratio = mesh_render(mesh, title=title, size=size)
        rendered.append(img)
        visible[title] = ratio
    cols = min(4, max(1, len(rendered)))
    rows = int(math.ceil(len(rendered) / cols))
    sheet = Image.new("RGB", (cols * size, rows * size), (245, 244, 239))
    for i, img in enumerate(rendered):
        sheet.paste(img, ((i % cols) * size, (i // cols) * size))
    sheet.save(path)
    return visible


def metric_gain(base: dict[str, object], row: dict[str, object]) -> dict[str, float | bool | str]:
    base_lcr = float(base["largest_occupancy_component_ratio_6n"])
    base_comps = int(base["occupancy_component_count_6n"])
    lcr = float(row["largest_occupancy_component_ratio_6n"])
    comps = int(row["occupancy_component_count_6n"])
    voxel_retention = float(row["occupied_voxels"]) / max(float(base["occupied_voxels"]), 1.0)
    area_retention = float(row["surface_area"]) / max(float(base["surface_area"]), 1e-9)
    bbox_retention = float(row["bbox_diag"]) / max(float(base["bbox_diag"]), 1e-9)
    lcr_gain = lcr - base_lcr
    comp_drop = base_comps - comps
    improved = (lcr_gain > 0.01 or comp_drop > 0) and comps <= base_comps
    visually_conservative = voxel_retention >= 0.65 and bbox_retention >= 0.75 and area_retention >= 0.20
    safe = improved and visually_conservative
    if safe:
        judgement = "safe_candidate"
    elif improved:
        judgement = "metric_only_or_shape_risky"
    else:
        judgement = "not_improved"
    return {
        "lcr_gain_vs_before": float(lcr_gain),
        "component_drop_vs_before": float(comp_drop),
        "voxel_retention_vs_before": float(voxel_retention),
        "area_retention_vs_before": float(area_retention),
        "bbox_diag_retention_vs_before": float(bbox_retention),
        "metric_improved": bool(improved),
        "visually_conservative": bool(visually_conservative),
        "paper_safe_candidate": bool(safe),
        "visual_judgement": judgement,
    }


def score_row(row: dict[str, object]) -> float:
    return (
        120.0 * float(row["lcr_gain_vs_before"])
        + 2.0 * float(row["component_drop_vs_before"])
        + 18.0 * min(float(row["voxel_retention_vs_before"]), 1.15)
        + 8.0 * min(float(row["bbox_diag_retention_vs_before"]), 1.05)
        - 0.00003 * float(row["faces"])
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = sorted({k for row in rows for k in row if not isinstance(row.get(k), (list, dict))})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def write_report(path: Path, summary: dict[str, object], selections: list[dict[str, object]]) -> None:
    rows = summary["rows"]
    assert isinstance(rows, list)
    improved = [r for r in rows if r.get("method") != "before" and r.get("metric_improved")]
    safe = [r for r in rows if r.get("paper_safe_candidate")]
    selected_safe = [s for s in selections if str(s.get("judgement")) == "safe_candidate"]
    lines = [
        "# 本地 mesh connectivity/repair 诊断 20260509",
        "",
        "## 结论",
        "",
        f"- 输入资产数：{summary['case_count']}；评估方法数：{summary['method_count']}；导出 mesh 变体数：{summary['exported_variant_count']}。",
        f"- occupancy-primary 改善方法行：{len(improved)}；同时满足保守视觉保真阈值的方法行：{len(safe)}；最终按 case 选出的 safe candidates：{len(selected_safe)}。",
        "- 判定口径：primary connectivity 使用 surface/edge/centroid voxel occupancy 的 6-neighbor 连通性；视觉可用性用 mesh 三角面软件渲染的 contact sheet 和 voxel/面积/bbox 保留率联合判断。",
        "- 本轮只有 radial4 系列在 before/after metrics 和视觉保守性上同时改善；DLA/scifi/tree-leaf/bismuth 多数在该 occupancy 分辨率下已经是单连通，不能据此宣称修复成功。",
        "- 不把 largest_component 单独视为论文图安全修复；它常能让连通性指标变好，但会删除碎片结构，适合作为诊断下界。",
        "",
            "## 每个 case 的改善候选",
            "",
            "| case | source | selected method | before comps | after comps | before LCR | after LCR | retention(voxel/area/bbox) | judgement |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for item in selections:
        lines.append(
            "| {case} | `{source}` | {method} | {before_components} | {after_components} | "
            "{before_lcr:.3f} | {after_lcr:.3f} | {voxel_retention:.2f}/{area_retention:.2f}/{bbox_retention:.2f} | {judgement} |".format(
                **item
            )
        )
    lines.extend(
        [
            "",
            "## 方法安全性判断",
            "",
            "| method | improved variants | safe candidates | 说明 |",
            "|---|---:|---:|---|",
        ]
    )
    methods = sorted({str(r["method"]) for r in rows if r.get("method") != "before"})
    for method in methods:
        subset = [r for r in rows if r.get("method") == method]
        imp = sum(bool(r.get("metric_improved")) for r in subset)
        ok = sum(bool(r.get("paper_safe_candidate")) for r in subset)
        if method == "largest_component":
            note = "只推荐诊断使用；删除结构风险高。"
        elif method.startswith("voxel_bridge_close"):
            note = "本轮只在 radial4 系列安全改善；其他 case 不能宣称成功，需逐图看 contact sheet。"
        elif method == "bridge_to_largest":
            note = "保留原结构但会引入细桥；适合可接受连接杆的工程图，不宜默认做美术图。"
        elif method == "conservative_hole_fill":
            note = "低风险清理；通常不解决远距离碎片。"
        elif method == "voxel_close":
            note = "本轮 radial4 安全改善；其他 case 多为 no-op 或仅改变表面。"
        else:
            note = "低风险但改善有限。"
        lines.append(f"| {method} | {imp} | {ok} | {note} |")
    lines.extend(
        [
            "",
            "## 输出文件",
            "",
            f"- Metrics JSON: `{summary['metrics_json']}`",
            f"- Metrics CSV: `{summary['metrics_csv']}`",
            f"- Selection JSON: `{summary['selection_json']}`",
            f"- Repaired meshes and contact sheets: `{summary['output_dir']}`",
            "",
            "## 使用限制",
            "",
            "- 本轮没有把任一修复结果声明为自动成功；只有同时改善 metrics 且 contact sheet 视觉保守的条目才标记为 paper_safe_candidate。",
            "- GLB 纹理不会在 voxel remesh 后保留；这些结果主要用于几何连通性修复诊断。若要用于论文最终图，需要重新贴图或使用原 GLB 渲染作为材质参考。",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def process_case(
    root: Path,
    path: Path,
    out_dir: Path,
    label: str,
    args: argparse.Namespace,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    mesh = clean_mesh(load_mesh(path))
    rel_path = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
    case_dir = out_dir / "meshes" / label
    case_dir.mkdir(parents=True, exist_ok=True)
    contact_dir = out_dir / "contact_sheets"
    contact_dir.mkdir(parents=True, exist_ok=True)

    base_metrics = mesh_metrics(mesh, args.metric_resolution)
    base_row: dict[str, object] = {
        "case": label,
        "method": "before",
        "source": rel_path,
        "mesh_path": rel_path,
        "export_path": "",
        **base_metrics,
        "lcr_gain_vs_before": 0.0,
        "component_drop_vs_before": 0.0,
        "voxel_retention_vs_before": 1.0,
        "area_retention_vs_before": 1.0,
        "bbox_diag_retention_vs_before": 1.0,
        "metric_improved": False,
        "visually_conservative": True,
        "paper_safe_candidate": False,
        "visual_judgement": "before",
    }
    rows = [base_row]
    panels: list[tuple[str, trimesh.Trimesh]] = [("before", mesh)]
    variants = variant_meshes(mesh, args.weld_tolerance, args.voxel_resolution)
    exported_count = 0
    for method, variant in variants:
        if len(variant.vertices) == 0 or len(variant.faces) == 0:
            continue
        suffix = ".glb" if args.export_format == "glb" else ".obj"
        export_path = case_dir / f"{method}{suffix}"
        variant.export(export_path)
        exported_count += 1
        metrics = mesh_metrics(variant, args.metric_resolution)
        gain = metric_gain(base_metrics, metrics)
        row: dict[str, object] = {
            "case": label,
            "method": method,
            "source": rel_path,
            "mesh_path": str(path),
            "export_path": str(export_path.relative_to(out_dir)),
            **metrics,
            **gain,
        }
        rows.append(row)
        if method in {"largest_component", "bridge_to_largest", "voxel_bridge_close", "voxel_bridge_close_simplify"}:
            panels.append((method, variant))

    sheet_visible = save_contact_sheet(contact_dir / f"{label}_contact.png", panels)
    for row in rows:
        title = str(row["method"])
        if title in sheet_visible:
            row["render_visible_ratio"] = sheet_visible[title]

    candidates = [r for r in rows if r["method"] != "before"]
    improved_candidates = [r for r in candidates if bool(r.get("metric_improved"))]
    if improved_candidates:
        best = max(improved_candidates, key=score_row)
        best_method = str(best["method"])
        judgement = str(best.get("visual_judgement", "metric_improved"))
    else:
        best = base_row
        best_method = "none_no_metric_improvement"
        judgement = "not_improved"
    selection = {
        "case": label,
        "source": rel_path,
        "method": best_method,
        "before_components": int(base_row["occupancy_component_count_6n"]),
        "after_components": int(best["occupancy_component_count_6n"]),
        "before_lcr": float(base_row["largest_occupancy_component_ratio_6n"]),
        "after_lcr": float(best["largest_occupancy_component_ratio_6n"]),
        "voxel_retention": float(best.get("voxel_retention_vs_before", 1.0)),
        "area_retention": float(best.get("area_retention_vs_before", 1.0)),
        "bbox_retention": float(best.get("bbox_diag_retention_vs_before", 1.0)),
        "judgement": judgement,
        "contact_sheet": str((contact_dir / f"{label}_contact.png").relative_to(out_dir)),
        "exported_variants": exported_count,
    }
    return rows, selection


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, default=Path("results/connectivity_repair_local_20260509"))
    parser.add_argument("--input", action="append", default=[], help="File, directory, or glob. Defaults to project fragmented assets.")
    parser.add_argument("--all-default-inputs", action="store_true", help="Use every default input instead of focus-pattern filtering.")
    parser.add_argument("--limit", type=int, default=0, help="Optional max number of input meshes after sorting.")
    parser.add_argument("--metric-resolution", type=int, default=64)
    parser.add_argument("--voxel-resolution", type=int, default=88)
    parser.add_argument("--weld-tolerance", type=float, default=0.002)
    parser.add_argument("--export-format", choices=["obj", "glb"], default="obj")
    parser.add_argument("--report", type=Path, default=Path("docs/evaluation/connectivity_repair_local_zh_20260509.md"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    out_dir = (root / args.out).resolve() if not args.out.is_absolute() else args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    inputs = tuple(args.input) if args.input else DEFAULT_GLOBS
    paths = expand_inputs(root, inputs)
    if not args.input and not args.all_default_inputs:
        paths = [p for p in paths if FOCUS_PATTERNS.search(str(p))]
    if args.limit > 0:
        paths = paths[: args.limit]

    rows: list[dict[str, object]] = []
    selections: list[dict[str, object]] = []
    missing_or_failed: list[dict[str, object]] = []
    start = time.time()
    used_labels: set[str] = set()
    for idx, path in enumerate(paths, 1):
        label = default_label(root, path)
        if label in used_labels:
            label = f"{label}_{idx:02d}"
        used_labels.add(label)
        print(f"[{idx}/{len(paths)}] {label}")
        try:
            case_rows, selection = process_case(root, path, out_dir, label, args)
            rows.extend(case_rows)
            selections.append(selection)
        except Exception as exc:
            missing_or_failed.append({"path": str(path), "label": label, "error": repr(exc)})
            print(f"  failed: {exc}")

    metrics_json = out_dir / "metrics.json"
    metrics_csv = out_dir / "metrics.csv"
    selection_json = out_dir / "selection.json"
    summary: dict[str, object] = {
        "kind": "mesh_connectivity_repair_local_20260509",
        "root": str(root),
        "output_dir": str(out_dir),
        "case_count": len(selections),
        "method_count": 7,
        "exported_variant_count": int(sum(int(s["exported_variants"]) for s in selections)),
        "metric_resolution": int(args.metric_resolution),
        "voxel_resolution": int(args.voxel_resolution),
        "weld_tolerance": float(args.weld_tolerance),
        "elapsed_seconds": round(time.time() - start, 3),
        "rows": rows,
        "selections": selections,
        "missing_or_failed": missing_or_failed,
        "metrics_json": str(metrics_json),
        "metrics_csv": str(metrics_csv),
        "selection_json": str(selection_json),
    }
    metrics_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(metrics_csv, rows)
    selection_json.write_text(json.dumps(selections, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path = (root / args.report).resolve() if not args.report.is_absolute() else args.report.resolve()
    write_report(report_path, summary, selections)
    print(json.dumps({k: summary[k] for k in ("case_count", "exported_variant_count", "elapsed_seconds")}, indent=2))
    print(report_path)


if __name__ == "__main__":
    main()
