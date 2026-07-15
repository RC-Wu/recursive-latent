#!/usr/bin/env python3
"""CPU pilot for local naturalization of blocky mesh support.

This is an engineering diagnostic, not a paper claim.  It converts OBJ/GLB
surface support to a voxel occupancy grid, applies conservative morphology and
optional shortest voxel bridges to preserve connected support, then reconstructs
an OBJ with marching cubes.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import re
from collections import deque
from pathlib import Path
from typing import Iterable, NamedTuple

import numpy as np
import trimesh
from scipy import ndimage
from scipy.spatial import cKDTree
from skimage import measure


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
MESH_EXTS = {".obj", ".glb", ".gltf", ".ply", ".stl", ".off"}
NEIGHBORS6 = np.asarray(
    [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)],
    dtype=np.int16,
)


class OccGrid(NamedTuple):
    matrix: np.ndarray
    vmin: np.ndarray
    scale: float
    inner: int
    margin: int


class NaturalizeResult(NamedTuple):
    mesh: trimesh.Trimesh
    grid: OccGrid
    before: dict[str, object]
    after: dict[str, object]


def slugify(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text.strip())
    return re.sub(r"_+", "_", text).strip("_.")[:140] or "mesh"


def expand_inputs(root: Path, items: Iterable[str]) -> list[Path]:
    paths: list[Path] = []
    for item in items:
        raw = str(root / item) if not Path(item).is_absolute() else item
        if any(ch in raw for ch in "*?[]"):
            paths.extend(Path(p) for p in glob.glob(raw, recursive=True))
            continue
        path = Path(raw)
        if path.is_dir():
            paths.extend(p for p in path.glob("**/*") if p.suffix.lower() in MESH_EXTS)
        elif path.suffix.lower() in MESH_EXTS:
            paths.append(path)
    return sorted(dict.fromkeys(p.resolve() for p in paths if p.exists()))


def default_label(root: Path, path: Path) -> str:
    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = path
    if path.name == "textured.glb" and rel.parent.name:
        return slugify(rel.parent.name)
    if path.name == "traditional_target.obj" and rel.parent.name:
        return slugify(rel.parent.name)
    return slugify("_".join([rel.parent.name, path.stem]))


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
            mesh = geom.copy()
            mesh.apply_transform(transform)
            meshes.append(mesh)
    if not meshes:
        raise ValueError(f"no mesh geometry found in {path}")
    out = trimesh.util.concatenate(meshes)
    out.remove_unreferenced_vertices()
    return out


def clean_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    out = mesh.copy()
    out.remove_unreferenced_vertices()
    if len(out.faces):
        out.update_faces(out.nondegenerate_faces())
        out.remove_unreferenced_vertices()
        try:
            trimesh.repair.fix_normals(out, multibody=True)
        except Exception:
            pass
    return out


def mesh_support_points(mesh: trimesh.Trimesh, sample_count: int, seed: int) -> np.ndarray:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    chunks: list[np.ndarray] = []
    if len(vertices):
        chunks.append(vertices)
    if len(vertices) and len(faces):
        valid = faces[(faces >= 0).all(axis=1) & (faces < len(vertices)).all(axis=1)]
        if len(valid):
            tri = vertices[valid[:, :3]]
            chunks.extend(
                [
                    tri.mean(axis=1),
                    (tri[:, 0] + tri[:, 1]) * 0.5,
                    (tri[:, 1] + tri[:, 2]) * 0.5,
                    (tri[:, 2] + tri[:, 0]) * 0.5,
                ]
            )
            if sample_count > 0:
                state = np.random.get_state()
                np.random.seed(seed)
                try:
                    pts, _ = trimesh.sample.sample_surface(mesh, count=sample_count)
                    if len(pts):
                        chunks.append(np.asarray(pts, dtype=np.float64))
                finally:
                    np.random.set_state(state)
    points = np.vstack(chunks) if chunks else np.zeros((0, 3), dtype=np.float64)
    return points[np.isfinite(points).all(axis=1)]


def occupancy_from_points(points: np.ndarray, resolution: int, margin: int) -> OccGrid:
    matrix = np.zeros((resolution, resolution, resolution), dtype=bool)
    if len(points) == 0:
        return OccGrid(matrix, np.zeros(3, dtype=np.float64), 1.0, max(resolution - 2 * margin - 1, 1), margin)
    vmin = points.min(axis=0)
    vmax = points.max(axis=0)
    scale = float(np.max(vmax - vmin))
    inner = max(resolution - 2 * margin - 1, 1)
    if scale <= 1e-12:
        matrix[resolution // 2, resolution // 2, resolution // 2] = True
        return OccGrid(matrix, vmin, 1.0, inner, margin)
    coords = np.floor((points - vmin) / scale * inner + margin).astype(np.int64)
    coords = np.clip(coords, 0, resolution - 1)
    matrix[coords[:, 0], coords[:, 1], coords[:, 2]] = True
    return OccGrid(matrix, vmin, scale, inner, margin)


def component_arrays_6n(matrix: np.ndarray) -> list[np.ndarray]:
    points = np.argwhere(matrix)
    if len(points) == 0:
        return []
    seen = np.zeros_like(matrix, dtype=bool)
    comps: list[np.ndarray] = []
    shape = np.asarray(matrix.shape, dtype=np.int16)
    for start in points:
        st = tuple(int(x) for x in start)
        if seen[st]:
            continue
        q: deque[tuple[int, int, int]] = deque([st])
        seen[st] = True
        comp: list[tuple[int, int, int]] = []
        while q:
            cur = q.popleft()
            comp.append(cur)
            arr = np.asarray(cur, dtype=np.int16)
            for delta in NEIGHBORS6:
                nb = arr + delta
                if (nb < 0).any() or (nb >= shape).any():
                    continue
                nt = tuple(int(x) for x in nb)
                if matrix[nt] and not seen[nt]:
                    seen[nt] = True
                    q.append(nt)
        comps.append(np.asarray(comp, dtype=np.int16))
    comps.sort(key=len, reverse=True)
    return comps


def component_stats_6n(matrix: np.ndarray) -> dict[str, object]:
    comps = component_arrays_6n(matrix)
    occupied = int(matrix.sum())
    largest = int(len(comps[0])) if comps else 0
    return {
        "occupied_voxels": occupied,
        "component_count": int(len(comps)),
        "largest_component_voxels": largest,
        "largest_component_ratio": float(largest / max(occupied, 1)),
    }


def draw_voxel_line(matrix: np.ndarray, a: np.ndarray, b: np.ndarray, radius: int) -> None:
    steps = int(max(np.abs(b - a).max(), 1))
    rr = max(int(radius), 0)
    for step in range(steps + 1):
        p = np.round(a + (b - a) * (step / steps)).astype(int)
        for dx in range(-rr, rr + 1):
            for dy in range(-rr, rr + 1):
                for dz in range(-rr, rr + 1):
                    q = p + np.asarray([dx, dy, dz])
                    if (q >= 0).all() and (q < np.asarray(matrix.shape)).all():
                        matrix[tuple(int(x) for x in q)] = True


def bridge_components_to_largest(
    matrix: np.ndarray,
    max_components: int = 32,
    min_voxels: int = 4,
    bridge_radius: int = 1,
) -> np.ndarray:
    out = matrix.copy()
    comps = component_arrays_6n(out)
    if len(comps) <= 1:
        return out
    largest = comps[0]
    tree = cKDTree(largest.astype(np.float64))
    for comp in comps[1:max_components]:
        if len(comp) < min_voxels:
            continue
        dists, idx = tree.query(comp.astype(np.float64), k=1)
        best = int(np.argmin(dists))
        draw_voxel_line(out, comp[best], largest[int(idx[best])], bridge_radius)
    return out


def naturalized_occupancy(
    grid: OccGrid,
    initial_dilate: int,
    close_iterations: int,
    smooth_sigma: float,
    bridge: bool,
    bridge_radius: int,
) -> tuple[OccGrid, dict[str, object], dict[str, object]]:
    structure = ndimage.generate_binary_structure(3, 1)
    matrix = grid.matrix.copy()
    if initial_dilate > 0:
        matrix = ndimage.binary_dilation(matrix, structure=structure, iterations=initial_dilate)
    before = component_stats_6n(matrix)
    if bridge:
        matrix = bridge_components_to_largest(matrix, bridge_radius=bridge_radius)
    if close_iterations > 0:
        matrix = ndimage.binary_closing(matrix, structure=structure, iterations=close_iterations)
        matrix = ndimage.binary_dilation(matrix, structure=structure, iterations=1)
    if smooth_sigma > 0:
        field = ndimage.gaussian_filter(matrix.astype(np.float32), sigma=float(smooth_sigma))
        matrix = np.logical_or(field >= 0.30, matrix)
    after = component_stats_6n(matrix)
    return OccGrid(matrix, grid.vmin, grid.scale, grid.inner, grid.margin), before, after


def mesh_from_occupancy(grid: OccGrid) -> trimesh.Trimesh:
    if int(grid.matrix.sum()) == 0:
        return trimesh.Trimesh(vertices=np.zeros((0, 3)), faces=np.zeros((0, 3), dtype=np.int64), process=False)
    padded = np.pad(grid.matrix.astype(np.float32), 1, mode="constant")
    verts, faces, _normals, _values = measure.marching_cubes(padded, level=0.5, allow_degenerate=False)
    verts = verts - 1.0
    verts = (verts - grid.margin) / max(float(grid.inner), 1.0) * grid.scale + grid.vmin
    return clean_mesh(trimesh.Trimesh(vertices=verts, faces=faces.astype(np.int64), process=False))


def naturalize_mesh(
    mesh: trimesh.Trimesh,
    resolution: int = 96,
    sample_count: int = 100_000,
    seed: int = 20260510,
    margin: int = 4,
    initial_dilate: int = 1,
    close_iterations: int = 1,
    smooth_sigma: float = 0.45,
    bridge: bool = True,
    bridge_radius: int = 1,
    simplify_faces: int = 80_000,
) -> NaturalizeResult:
    points = mesh_support_points(mesh, sample_count=sample_count, seed=seed)
    grid = occupancy_from_points(points, resolution=resolution, margin=margin)
    out_grid, before, after = naturalized_occupancy(
        grid,
        initial_dilate=initial_dilate,
        close_iterations=close_iterations,
        smooth_sigma=smooth_sigma,
        bridge=bridge,
        bridge_radius=bridge_radius,
    )
    out_mesh = mesh_from_occupancy(out_grid)
    if simplify_faces > 0 and len(out_mesh.faces) > simplify_faces:
        try:
            out_mesh = out_mesh.simplify_quadric_decimation(face_count=simplify_faces, aggression=4)
            out_mesh = clean_mesh(out_mesh)
        except Exception:
            pass
    return NaturalizeResult(out_mesh, out_grid, before, after)


def mesh_summary(mesh: trimesh.Trimesh) -> dict[str, object]:
    bounds = mesh.bounds if len(mesh.vertices) else np.zeros((2, 3), dtype=np.float64)
    extent = bounds[1] - bounds[0]
    return {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "surface_area": float(mesh.area) if len(mesh.faces) else 0.0,
        "bbox_diag": float(np.linalg.norm(extent)),
        "is_watertight": bool(mesh.is_watertight) if len(mesh.faces) else False,
        "euler_number": int(mesh.euler_number) if len(mesh.faces) else 0,
    }


def process_one(path: Path, label: str, out_dir: Path, args: argparse.Namespace) -> dict[str, object]:
    mesh = load_mesh(path)
    result = naturalize_mesh(
        mesh,
        resolution=args.resolution,
        sample_count=args.sample_count,
        seed=args.seed,
        margin=args.margin,
        initial_dilate=args.initial_dilate,
        close_iterations=args.close_iterations,
        smooth_sigma=args.smooth_sigma,
        bridge=not args.no_bridge,
        bridge_radius=args.bridge_radius,
        simplify_faces=args.simplify_faces,
    )
    out_path = out_dir / f"{label}_naturalized.obj"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.mesh.export(out_path)
    base = mesh_summary(mesh)
    out = mesh_summary(result.mesh)
    row: dict[str, object] = {
        "label": label,
        "source": str(path),
        "output_obj": str(out_path),
        "resolution": int(args.resolution),
        "sample_count": int(args.sample_count),
        "initial_dilate": int(args.initial_dilate),
        "close_iterations": int(args.close_iterations),
        "smooth_sigma": float(args.smooth_sigma),
        "bridge": not args.no_bridge,
        "bridge_radius": int(args.bridge_radius),
    }
    row.update({f"before_{k}": v for k, v in base.items()})
    row.update({f"after_{k}": v for k, v in out.items()})
    row.update({f"occ_before_{k}": v for k, v in result.before.items()})
    row.update({f"occ_after_{k}": v for k, v in result.after.items()})
    row["component_drop"] = int(result.before["component_count"]) - int(result.after["component_count"])
    row["lcr_gain"] = float(result.after["largest_component_ratio"]) - float(result.before["largest_component_ratio"])
    row["area_retention"] = float(out["surface_area"]) / max(float(base["surface_area"]), 1e-9)
    row["bbox_diag_retention"] = float(out["bbox_diag"]) / max(float(base["bbox_diag"]), 1e-9)
    return row


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = sorted({k for row in rows for k, v in row.items() if not isinstance(v, (dict, list))})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", required=True, help="Mesh path, directory, or glob. Can be repeated.")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results" / "naturalize_blocky_mesh_pilot_20260510")
    parser.add_argument("--resolution", type=int, default=96)
    parser.add_argument("--sample-count", type=int, default=120_000)
    parser.add_argument("--seed", type=int, default=20260510)
    parser.add_argument("--margin", type=int, default=4)
    parser.add_argument("--initial-dilate", type=int, default=1)
    parser.add_argument("--close-iterations", type=int, default=1)
    parser.add_argument("--smooth-sigma", type=float, default=0.45)
    parser.add_argument("--bridge-radius", type=int, default=1)
    parser.add_argument("--no-bridge", action="store_true")
    parser.add_argument("--simplify-faces", type=int, default=80_000)
    args = parser.parse_args()

    paths = expand_inputs(ROOT, args.input)
    if not paths:
        raise SystemExit("no input meshes found")
    rows = []
    for path in paths:
        label = default_label(ROOT, path)
        print(f"[naturalize] {label}: {path}")
        rows.append(process_one(path, label, args.out_dir, args))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "summary.csv", rows)
    (args.out_dir / "summary.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[naturalize] wrote {len(rows)} OBJ files and summary to {args.out_dir}")


if __name__ == "__main__":
    main()
