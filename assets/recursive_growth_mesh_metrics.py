#!/usr/bin/env python3
"""Lightweight mesh and occupancy metrics for recursive growth outputs.

The script is intentionally dependency-light. OBJ files are parsed directly;
GLB/GLTF/PLY/STL/OFF loading is attempted through trimesh when available. Point
cloud text files are accepted as whitespace- or comma-separated xyz rows.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
from collections import deque
from pathlib import Path
from typing import Iterable

try:
    import numpy as np
except Exception as exc:  # pragma: no cover - numpy is expected, but fail clearly.
    raise SystemExit(f"numpy is required for recursive_growth_mesh_metrics.py: {exc}")


MESH_EXTS = {".obj", ".glb", ".gltf", ".ply", ".stl", ".off"}
POINT_EXTS = {".xyz", ".pts", ".txt", ".csv"}


def parse_obj(path: Path) -> tuple[np.ndarray, np.ndarray]:
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    with path.open("r", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
                    except ValueError:
                        continue
            elif line.startswith("f "):
                raw = line.split()[1:]
                idx: list[int] = []
                for token in raw:
                    head = token.split("/")[0]
                    if not head:
                        continue
                    val = int(head)
                    idx.append(val - 1 if val > 0 else len(vertices) + val)
                if len(idx) >= 3:
                    a = idx[0]
                    for j in range(1, len(idx) - 1):
                        faces.append((a, idx[j], idx[j + 1]))
    return np.asarray(vertices, dtype=np.float64), np.asarray(faces, dtype=np.int64)


def parse_point_text(path: Path) -> tuple[np.ndarray, np.ndarray]:
    points: list[tuple[float, float, float]] = []
    with path.open("r", errors="ignore") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.replace(",", " ").split()
            if len(parts) < 3:
                continue
            try:
                points.append((float(parts[0]), float(parts[1]), float(parts[2])))
            except ValueError:
                continue
    return np.asarray(points, dtype=np.float64), np.zeros((0, 3), dtype=np.int64)


def load_with_trimesh(path: Path) -> tuple[np.ndarray, np.ndarray, str]:
    try:
        import trimesh  # type: ignore
    except Exception as exc:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64), f"trimesh_unavailable:{exc}"
    try:
        loaded = trimesh.load(str(path), force=None, process=False)
        meshes = []
        if hasattr(loaded, "geometry"):
            meshes = [m for m in loaded.geometry.values() if hasattr(m, "vertices")]
        elif hasattr(loaded, "vertices"):
            meshes = [loaded]
        vertices_all = []
        faces_all = []
        offset = 0
        for mesh in meshes:
            verts = np.asarray(mesh.vertices, dtype=np.float64)
            faces = np.asarray(getattr(mesh, "faces", []), dtype=np.int64)
            if len(verts) == 0:
                continue
            vertices_all.append(verts)
            if faces.size:
                faces_all.append(faces[:, :3] + offset)
            offset += len(verts)
        vertices = np.vstack(vertices_all) if vertices_all else np.zeros((0, 3), dtype=np.float64)
        faces = np.vstack(faces_all) if faces_all else np.zeros((0, 3), dtype=np.int64)
        return vertices, faces, "trimesh"
    except Exception as exc:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64), f"trimesh_load_failed:{exc}"


def load_geometry(path: Path) -> tuple[np.ndarray, np.ndarray, str, str]:
    ext = path.suffix.lower()
    if ext == ".obj":
        try:
            vertices, faces = parse_obj(path)
            return vertices, faces, "obj_direct", ""
        except Exception as exc:
            return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64), "obj_direct", f"obj_parse_failed:{exc}"
    if ext in POINT_EXTS:
        vertices, faces = parse_point_text(path)
        return vertices, faces, "point_text", ""
    if ext in MESH_EXTS:
        vertices, faces, status = load_with_trimesh(path)
        error = "" if status == "trimesh" else status
        return vertices, faces, status, error
    return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64), "unsupported", f"unsupported_ext:{ext}"


class UnionFind:
    def __init__(self, n: int):
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


def bbox_stats(vertices: np.ndarray) -> dict:
    if len(vertices) == 0:
        return {
            "bbox_min_x": 0.0,
            "bbox_min_y": 0.0,
            "bbox_min_z": 0.0,
            "bbox_max_x": 0.0,
            "bbox_max_y": 0.0,
            "bbox_max_z": 0.0,
            "bbox_extent_x": 0.0,
            "bbox_extent_y": 0.0,
            "bbox_extent_z": 0.0,
            "bbox_volume": 0.0,
            "bbox_diag": 0.0,
        }
    vmin = vertices.min(axis=0)
    vmax = vertices.max(axis=0)
    extent = vmax - vmin
    return {
        "bbox_min_x": float(vmin[0]),
        "bbox_min_y": float(vmin[1]),
        "bbox_min_z": float(vmin[2]),
        "bbox_max_x": float(vmax[0]),
        "bbox_max_y": float(vmax[1]),
        "bbox_max_z": float(vmax[2]),
        "bbox_extent_x": float(extent[0]),
        "bbox_extent_y": float(extent[1]),
        "bbox_extent_z": float(extent[2]),
        "bbox_volume": float(np.prod(np.maximum(extent, 1e-12))),
        "bbox_diag": float(np.linalg.norm(extent)),
    }


def component_stats(vertices: np.ndarray, faces: np.ndarray) -> dict:
    if len(vertices) == 0:
        return {
            "component_count": 0,
            "largest_component_vertices": 0,
            "largest_component_vertex_ratio": 0.0,
            "small_component_count_lt100": 0,
            "component_status": "empty",
        }
    if len(faces) == 0:
        return {
            "component_count": int(len(vertices)),
            "largest_component_vertices": 1,
            "largest_component_vertex_ratio": float(1.0 / max(len(vertices), 1)),
            "small_component_count_lt100": int(len(vertices)),
            "component_status": "point_proxy_each_vertex",
        }
    valid = faces[(faces >= 0).all(axis=1) & (faces < len(vertices)).all(axis=1)]
    uf = UnionFind(len(vertices))
    for a, b, c in valid:
        uf.union(int(a), int(b))
        uf.union(int(b), int(c))
        uf.union(int(c), int(a))
    roots = np.fromiter((uf.find(i) for i in range(len(vertices))), dtype=np.int64, count=len(vertices))
    _, counts = np.unique(roots, return_counts=True)
    largest = int(counts.max()) if len(counts) else 0
    return {
        "component_count": int(len(counts)),
        "largest_component_vertices": largest,
        "largest_component_vertex_ratio": float(largest / max(len(vertices), 1)),
        "small_component_count_lt100": int(np.sum(counts < 100)),
        "component_status": "face_connectivity",
    }


def quantized_weld_vertices(vertices: np.ndarray, tolerance: float) -> tuple[np.ndarray, np.ndarray, str]:
    if len(vertices) == 0:
        return np.zeros((0, 3), dtype=np.float64), np.zeros((0,), dtype=np.int64), "empty"
    if tolerance <= 0:
        return vertices, np.arange(len(vertices), dtype=np.int64), "disabled"
    keys = np.rint(vertices / float(tolerance)).astype(np.int64)
    _, first_idx, inverse = np.unique(keys, axis=0, return_index=True, return_inverse=True)
    order = np.argsort(first_idx)
    remap = np.empty(len(order), dtype=np.int64)
    remap[order] = np.arange(len(order), dtype=np.int64)
    welded_vertices = vertices[first_idx[order]]
    return welded_vertices, remap[inverse].astype(np.int64), "quantized_vertex_weld"


def welded_component_stats(vertices: np.ndarray, faces: np.ndarray, tolerance: float) -> dict:
    base = {
        "weld_tolerance": float(tolerance),
        "welded_vertices": int(len(vertices)),
        "welded_vertex_reduction": 0,
        "welded_component_count": "",
        "largest_welded_component_vertices": "",
        "largest_welded_component_vertex_ratio": "",
        "small_welded_component_count_lt100": "",
        "welded_component_status": "disabled" if tolerance <= 0 else "empty",
    }
    if len(vertices) == 0:
        return base
    welded_vertices, inverse, status = quantized_weld_vertices(vertices, tolerance)
    base["welded_vertices"] = int(len(welded_vertices))
    base["welded_vertex_reduction"] = int(len(vertices) - len(welded_vertices))
    if tolerance <= 0:
        return base
    if len(faces) == 0:
        base.update(
            {
                "welded_component_count": int(len(welded_vertices)),
                "largest_welded_component_vertices": 1,
                "largest_welded_component_vertex_ratio": float(1.0 / max(len(welded_vertices), 1)),
                "small_welded_component_count_lt100": int(len(welded_vertices)),
                "welded_component_status": "point_proxy_each_welded_vertex",
            }
        )
        return base
    valid = faces[(faces >= 0).all(axis=1) & (faces < len(vertices)).all(axis=1)]
    remapped = inverse[valid] if len(valid) else np.zeros((0, 3), dtype=np.int64)
    nondegenerate = remapped[
        (remapped[:, 0] != remapped[:, 1])
        & (remapped[:, 1] != remapped[:, 2])
        & (remapped[:, 0] != remapped[:, 2])
    ]
    stats = component_stats(welded_vertices, nondegenerate)
    base.update(
        {
            "welded_component_count": stats["component_count"],
            "largest_welded_component_vertices": stats["largest_component_vertices"],
            "largest_welded_component_vertex_ratio": stats["largest_component_vertex_ratio"],
            "small_welded_component_count_lt100": stats["small_component_count_lt100"],
            "welded_component_status": status,
        }
    )
    return base


def occupancy_coords(vertices: np.ndarray, resolution: int) -> tuple[np.ndarray, dict]:
    if len(vertices) == 0 or resolution <= 0:
        return np.zeros((0, 3), dtype=np.int64), {"occupancy_status": "empty"}
    vmin = vertices.min(axis=0)
    vmax = vertices.max(axis=0)
    extent = vmax - vmin
    max_extent = float(np.max(extent))
    if max_extent <= 1e-12:
        return np.zeros((1, 3), dtype=np.int64), {"occupancy_status": "degenerate_bbox"}
    norm = (vertices - vmin) / max_extent
    coords = np.floor(norm * (resolution - 1e-9)).astype(np.int64)
    coords = np.clip(coords, 0, resolution - 1)
    coords = np.unique(coords, axis=0)
    return coords, {"occupancy_status": "vertex_voxelized"}


def occupancy_component_count(coords: np.ndarray) -> tuple[int, int]:
    if len(coords) == 0:
        return 0, 0
    occupied = {tuple(map(int, c)) for c in coords}
    seen: set[tuple[int, int, int]] = set()
    largest = 0
    comps = 0
    dirs = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    for start in occupied:
        if start in seen:
            continue
        comps += 1
        size = 0
        q: deque[tuple[int, int, int]] = deque([start])
        seen.add(start)
        while q:
            cur = q.popleft()
            size += 1
            for d in dirs:
                nxt = (cur[0] + d[0], cur[1] + d[1], cur[2] + d[2])
                if nxt in occupied and nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        largest = max(largest, size)
    return comps, largest


def occupancy_stats(vertices: np.ndarray, resolution: int) -> dict:
    coords, status = occupancy_coords(vertices, resolution)
    comps, largest = occupancy_component_count(coords)
    occupied = int(len(coords))
    total = int(resolution**3) if resolution > 0 else 0
    out = {
        "occupancy_resolution": int(resolution),
        "occupied_voxels": occupied,
        "occupancy_coverage": float(occupied / max(total, 1)),
        "occupancy_component_count_6n": int(comps),
        "largest_occupancy_component_voxels_6n": int(largest),
        "largest_occupancy_component_ratio_6n": float(largest / max(occupied, 1)),
    }
    out.update(status)
    return out


def box_counting_stats(vertices: np.ndarray, resolutions: Iterable[int]) -> dict:
    counts: list[tuple[int, int]] = []
    for res in resolutions:
        coords, _ = occupancy_coords(vertices, int(res))
        if int(res) > 1:
            counts.append((int(res), int(len(coords))))
    out: dict[str, object] = {
        "box_count_resolutions": ";".join(str(r) for r, _ in counts),
        "box_count_occupied": ";".join(str(c) for _, c in counts),
        "box_count_dimension_proxy": "",
        "box_count_status": "insufficient",
    }
    usable = [(r, c) for r, c in counts if c > 0]
    if len(usable) >= 2:
        xs = np.log([r for r, _ in usable])
        ys = np.log([c for _, c in usable])
        slope = float(np.polyfit(xs, ys, 1)[0])
        out["box_count_dimension_proxy"] = slope
        out["box_count_status"] = "vertex_occupancy_proxy"
    return out


def face_area_stats(vertices: np.ndarray, faces: np.ndarray, sample_limit: int) -> dict:
    if len(vertices) == 0 or len(faces) == 0:
        return {"surface_area_est": 0.0, "face_area_mean": 0.0, "face_area_median": 0.0}
    valid = faces[(faces >= 0).all(axis=1) & (faces < len(vertices)).all(axis=1)]
    if len(valid) == 0:
        return {"surface_area_est": 0.0, "face_area_mean": 0.0, "face_area_median": 0.0}
    sample = valid
    scale = 1.0
    if len(sample) > sample_limit:
        idx = np.linspace(0, len(sample) - 1, sample_limit).astype(np.int64)
        sample = sample[idx]
        scale = len(valid) / len(sample)
    tri = vertices[sample]
    areas = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
    return {
        "surface_area_est": float(np.sum(areas) * scale),
        "face_area_mean": float(np.mean(areas)),
        "face_area_median": float(np.median(areas)),
    }


def infer_case_method_depth(path: Path) -> dict:
    parts = path.parts
    depth = ""
    for part in reversed(parts):
        if part.startswith(("depth_", "stage_")):
            tail = part.split("_")[-1]
            if tail.isdigit():
                depth = int(tail)
                break
    return {"case_hint": path.parent.name, "method_hint": path.parent.parent.name if len(parts) >= 2 else "", "depth_hint": depth}


def metric_one(path: Path, label: str, args: argparse.Namespace) -> dict:
    vertices, faces, loader, error = load_geometry(path)
    row: dict[str, object] = {
        "label": label,
        "path": str(path),
        "extension": path.suffix.lower(),
        "loader": loader,
        "load_error": error,
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
    }
    row.update(infer_case_method_depth(path))
    row.update(bbox_stats(vertices))
    row.update(component_stats(vertices, faces))
    row["fragmentation_score"] = float(1.0 - float(row["largest_component_vertex_ratio"]))
    row["vertices_per_bbox_volume"] = float(len(vertices) / max(float(row["bbox_volume"]), 1e-12))
    row.update(face_area_stats(vertices, faces, args.sample_limit))
    row.update(welded_component_stats(vertices, faces, args.weld_tolerance))
    occ = occupancy_stats(vertices, args.occupancy_resolution)
    row.update(occ)
    row.update(box_counting_stats(vertices, args.box_resolutions))
    if args.primary_connectivity == "face":
        row["primary_connectivity_metric"] = "raw_face_vertex_connectivity"
        row["primary_component_count"] = row["component_count"]
        row["primary_largest_component_ratio"] = row["largest_component_vertex_ratio"]
    elif args.primary_connectivity == "welded":
        row["primary_connectivity_metric"] = "quantized_welded_face_connectivity"
        row["primary_component_count"] = row["welded_component_count"]
        row["primary_largest_component_ratio"] = row["largest_welded_component_vertex_ratio"]
    else:
        row["primary_connectivity_metric"] = "occupancy_6n_vertex_voxel"
        row["primary_component_count"] = row["occupancy_component_count_6n"]
        row["primary_largest_component_ratio"] = row["largest_occupancy_component_ratio_6n"]
    return row


def expand_inputs(items: list[str], recursive: bool) -> list[Path]:
    paths: list[Path] = []
    for item in items:
        if any(ch in item for ch in "*?[]"):
            paths.extend(Path(p) for p in glob.glob(item, recursive=recursive))
            continue
        p = Path(item)
        if p.is_dir():
            pattern = "**/*" if recursive else "*"
            for child in p.glob(pattern):
                if child.suffix.lower() in MESH_EXTS | POINT_EXTS:
                    paths.append(child)
        else:
            paths.append(p)
    return sorted(dict.fromkeys(paths))


def parse_case_items(items: list[str]) -> list[tuple[str, Path]]:
    out = []
    for item in items:
        label, raw = item.split("=", 1) if "=" in item else (Path(item).stem, item)
        out.append((label, Path(raw)))
    return out


def default_label(path: Path) -> str:
    parent = path.parent.name
    stem = path.stem
    return f"{parent}_{stem}" if parent else stem


def write_outputs(summary: dict, out_json: Path | None, out_csv: Path | None) -> None:
    if out_json:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    rows = summary["rows"]
    if out_csv and rows:
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = sorted({k for row in rows for k in row if not isinstance(row.get(k), (list, dict))})
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in fieldnames})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", help="Files, directories, or globs.")
    parser.add_argument("--case", action="append", default=[], help="Explicit label=path item. May be repeated.")
    parser.add_argument("--recursive", action="store_true", help="Scan directories recursively and honor recursive globs.")
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-csv", type=Path, default=None)
    parser.add_argument("--occupancy-resolution", type=int, default=64)
    parser.add_argument("--box-resolutions", type=int, nargs="+", default=[8, 16, 32, 64])
    parser.add_argument("--sample-limit", type=int, default=200000)
    parser.add_argument(
        "--weld-tolerance",
        type=float,
        default=0.0,
        help="Optional quantized vertex welding tolerance before face-connectivity stats. 0 disables welding.",
    )
    parser.add_argument(
        "--primary-connectivity",
        choices=["occupancy", "welded", "face"],
        default="occupancy",
        help="Connectivity metric to expose as primary_* fields. Defaults to occupancy for fair OBJ tube comparisons.",
    )
    args = parser.parse_args()

    cases = parse_case_items(args.case)
    for path in expand_inputs(args.inputs, args.recursive):
        cases.append((default_label(path), path))
    rows = []
    missing = []
    for label, path in cases:
        if not path.exists():
            missing.append({"label": label, "path": str(path)})
            continue
        rows.append(metric_one(path, label, args))
    summary = {
        "metric_schema": "recursive_growth_mesh_metrics_v1",
        "rows": rows,
        "missing": missing,
        "notes": [
            "component_count uses face connectivity for meshes and degrades to one component per point when faces are absent.",
            "welded_component_* optionally uses quantized vertex welding before face connectivity; enable with --weld-tolerance.",
            "primary_* defaults to occupancy_6n_vertex_voxel because un-welded procedural tube OBJ segments can inflate raw face components.",
            "occupancy and box-counting are vertex-occupancy proxies normalized by the mesh bounding box.",
            "GLB/GLTF/PLY/STL/OFF require trimesh; failures are recorded per row instead of aborting the batch.",
        ],
    }
    write_outputs(summary, args.out_json, args.out_csv)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
