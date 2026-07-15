#!/usr/bin/env python3
"""Branch/path/root-reachability metrics for tree/root/vine baselines.

The script intentionally separates two evidence levels:

* skeleton_exact_space_colonization: graph metrics from saved skeleton.json.
* mesh_voxel_proxy: root reachability and branch/path proxies from vertex
  occupancy. These are useful for tables and screening, but are not a reliable
  replacement for skeletonization.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable

import numpy as np


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_OUT = PROJECT_ROOT / "results/branch_path_metrics_20260509"
MESH_EXTS = {".obj", ".glb", ".gltf", ".ply", ".stl", ".off"}


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


def load_with_trimesh(path: Path) -> tuple[np.ndarray, np.ndarray, str]:
    try:
        import trimesh  # type: ignore
    except Exception as exc:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64), f"trimesh_unavailable:{exc}"
    try:
        loaded = trimesh.load(str(path), force=None, process=False)
        if hasattr(loaded, "geometry"):
            meshes = [m for m in loaded.geometry.values() if hasattr(m, "vertices")]
        elif hasattr(loaded, "vertices"):
            meshes = [loaded]
        else:
            meshes = []
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
    if ext in MESH_EXTS:
        vertices, faces, status = load_with_trimesh(path)
        return vertices, faces, status, "" if status == "trimesh" else status
    return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64), "unsupported", f"unsupported_ext:{ext}"


def bbox_stats(points: np.ndarray) -> dict[str, object]:
    if len(points) == 0:
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
            "bbox_diag": 0.0,
        }
    vmin = points.min(axis=0)
    vmax = points.max(axis=0)
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
        "bbox_diag": float(np.linalg.norm(extent)),
    }


def infer_family(label: str, path: str = "") -> str:
    text = f"{label} {path}".lower()
    if "space_colonization" in text or "space-colonization" in text:
        return "space_colonization"
    if "vine" in text:
        return "vine"
    if "root" in text:
        return "root"
    if "tree" in text or "lsystem" in text or "ifs_branch" in text:
        return "tree"
    return "unknown"


def graph_components(n: int, adjacency: list[list[int]]) -> tuple[list[int], list[int]]:
    comp_id = [-1] * n
    sizes: list[int] = []
    for start in range(n):
        if comp_id[start] >= 0:
            continue
        cid = len(sizes)
        size = 0
        q: deque[int] = deque([start])
        comp_id[start] = cid
        while q:
            cur = q.popleft()
            size += 1
            for nxt in adjacency[cur]:
                if comp_id[nxt] < 0:
                    comp_id[nxt] = cid
                    q.append(nxt)
        sizes.append(size)
    return comp_id, sizes


def dijkstra_tree_graph(
    nodes: np.ndarray, adjacency: list[list[int]], root: int
) -> tuple[list[float], list[int]]:
    n = len(nodes)
    dist = [math.inf] * n
    hops = [-1] * n
    dist[root] = 0.0
    hops[root] = 0
    # Skeletons here are trees or small sparse graphs; a repeated linear scan is
    # fine and avoids an extra heap import path in the test API.
    visited = [False] * n
    for _ in range(n):
        best = -1
        best_dist = math.inf
        for i, val in enumerate(dist):
            if not visited[i] and val < best_dist:
                best = i
                best_dist = val
        if best < 0:
            break
        visited[best] = True
        for nxt in adjacency[best]:
            edge_len = float(np.linalg.norm(nodes[best] - nodes[nxt]))
            cand = dist[best] + edge_len
            if cand < dist[nxt]:
                dist[nxt] = cand
                hops[nxt] = hops[best] + 1
    return dist, hops


def metric_from_skeleton(
    label: str,
    path: str,
    nodes: Iterable[Iterable[float]],
    edges: Iterable[Iterable[int]] | None = None,
    parents: Iterable[int] | None = None,
) -> dict[str, object]:
    node_arr = np.asarray(list(nodes), dtype=np.float64)
    n = int(len(node_arr))
    adjacency: list[list[int]] = [[] for _ in range(n)]
    root_candidates: list[int] = []
    if parents is not None:
        parent_list = [int(p) for p in parents]
        for i, parent in enumerate(parent_list):
            if parent < 0:
                root_candidates.append(i)
            elif 0 <= parent < n:
                adjacency[i].append(parent)
                adjacency[parent].append(i)
    if edges is not None:
        for edge in edges:
            a, b = [int(x) for x in edge[:2]]
            if 0 <= a < n and 0 <= b < n:
                adjacency[a].append(b)
                adjacency[b].append(a)
    if not root_candidates and n:
        root_candidates = [int(np.argmin(node_arr[:, 2]))]
    root = root_candidates[0] if root_candidates else -1
    degree = [len(set(nei)) for nei in adjacency]
    comp_id, comp_sizes = graph_components(n, adjacency) if n else ([], [])
    root_comp = comp_id[root] if root >= 0 else -1
    root_nodes = comp_sizes[root_comp] if root_comp >= 0 else 0
    dist, hops = dijkstra_tree_graph(node_arr, adjacency, root) if root >= 0 else ([], [])
    reachable = [i for i, d in enumerate(dist) if math.isfinite(d)]
    tips = [i for i, deg in enumerate(degree) if deg <= 1 and i != root]
    root_tips = [i for i in tips if root_comp >= 0 and comp_id[i] == root_comp]
    orphan_tips = [i for i in tips if root_comp < 0 or comp_id[i] != root_comp]
    branch_nodes = [i for i, deg in enumerate(degree) if deg >= 3 and root_comp >= 0 and comp_id[i] == root_comp]
    bbox = bbox_stats(node_arr)
    bbox_diag = float(bbox["bbox_diag"])
    max_dist = max((dist[i] for i in reachable), default=0.0)
    row: dict[str, object] = {
        "label": label,
        "path": path,
        "source_type": "skeleton_json",
        "metric_level": "skeleton_exact_space_colonization",
        "family": infer_family(label, path),
        "loader": "json_skeleton",
        "load_error": "",
        "vertices": n,
        "faces": 0,
        "occupied_voxels": "",
        "occupancy_component_count_6n": "",
        "largest_occupancy_component_ratio_6n": "",
        "root_seed_policy": "parents_negative_else_min_z_node",
        "root_component_ratio": float(root_nodes / max(n, 1)),
        "root_reachable_units": int(root_nodes),
        "total_units": n,
        "orphan_mass_ratio": float(1.0 - root_nodes / max(n, 1)),
        "geodesic_proxy_max_depth": int(max((hops[i] for i in reachable), default=0)),
        "geodesic_proxy_max_length": float(max_dist),
        "bbox_normalized_path_span": float(max_dist / max(bbox_diag, 1e-12)),
        "tip_count_proxy": int(len(root_tips)),
        "branching_proxy": int(len(branch_nodes)),
        "orphan_tip_proxy": int(len(orphan_tips)),
        "root_reachable_tip_ratio": float(len(root_tips) / max(len(tips), 1)),
        "branching_per_tip_proxy": float(len(branch_nodes) / max(len(root_tips), 1)),
        "skeletonization_status": "exact_saved_skeleton",
        "paper_use_tier": "paper_candidate_if_same_root_same_depth_and_render_QA_pass",
        "caveat": "Exact only for the saved procedural skeleton; not directly comparable to textured mesh skeletons without same-root/same-depth control.",
    }
    row.update(bbox)
    return row


def metric_from_skeleton_json(path: Path, label: str | None = None) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    parents = data.get("parents")
    edges = data.get("edges")
    row = metric_from_skeleton(label or str(data.get("case") or path.parent.name), str(path), nodes, edges, parents)
    for key in ["case", "alive_attractors", "covered_attractors"]:
        if key in data:
            row[f"skeleton_{key}"] = data[key]
    return row


def occupancy_coords(vertices: np.ndarray, resolution: int) -> tuple[np.ndarray, dict[str, object]]:
    if len(vertices) == 0:
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
    return coords, {
        "occupancy_status": "vertex_voxelized",
        "voxel_pitch_world": float(max_extent / max(resolution - 1, 1)),
    }


def rasterize_line(a: np.ndarray, b: np.ndarray) -> list[tuple[int, int, int]]:
    delta = b.astype(np.int64) - a.astype(np.int64)
    steps = int(np.max(np.abs(delta)))
    if steps <= 0:
        return [tuple(int(x) for x in a)]
    pts = []
    for i in range(steps + 1):
        t = i / steps
        p = np.rint(a * (1.0 - t) + b * t).astype(np.int64)
        pts.append((int(p[0]), int(p[1]), int(p[2])))
    return pts


def occupancy_coords_from_mesh(
    vertices: np.ndarray,
    faces: np.ndarray,
    resolution: int,
    max_edge_samples: int,
) -> tuple[np.ndarray, dict[str, object]]:
    coords, status = occupancy_coords(vertices, resolution)
    if len(coords) == 0 or len(faces) == 0:
        return coords, status
    valid = faces[(faces >= 0).all(axis=1) & (faces < len(vertices)).all(axis=1)]
    if len(valid) == 0 or len(valid) > max_edge_samples:
        status = dict(status)
        status["edge_voxelization_status"] = "skipped_face_count_limit"
        return coords, status
    vmin = vertices.min(axis=0)
    extent = vertices.max(axis=0) - vmin
    max_extent = float(np.max(extent))
    if max_extent <= 1e-12:
        return coords, status
    q = np.floor(((vertices - vmin) / max_extent) * (resolution - 1e-9)).astype(np.int64)
    q = np.clip(q, 0, resolution - 1)
    occupied = {tuple(map(int, c)) for c in coords}
    for tri in valid:
        qa, qb, qc = q[tri[0]], q[tri[1]], q[tri[2]]
        occupied.update(rasterize_line(qa, qb))
        occupied.update(rasterize_line(qb, qc))
        occupied.update(rasterize_line(qc, qa))
        centroid = np.rint((qa + qb + qc) / 3.0).astype(np.int64)
        occupied.add((int(centroid[0]), int(centroid[1]), int(centroid[2])))
    out = np.asarray(sorted(occupied), dtype=np.int64)
    status = dict(status)
    status["occupancy_status"] = "vertex_edge_voxelized"
    status["edge_voxelization_status"] = "enabled"
    return out, status


def choose_root_voxel(coords: np.ndarray) -> tuple[int, int, int] | None:
    if len(coords) == 0:
        return None
    min_z = int(coords[:, 2].min())
    candidates = coords[coords[:, 2] == min_z]
    xy_center = coords[:, :2].mean(axis=0)
    d2 = np.sum((candidates[:, :2] - xy_center[None, :]) ** 2, axis=1)
    chosen = candidates[int(np.argmin(d2))]
    return (int(chosen[0]), int(chosen[1]), int(chosen[2]))


def occupancy_graph_metrics(coords: np.ndarray, root: tuple[int, int, int] | None) -> dict[str, object]:
    if len(coords) == 0 or root is None:
        return {
            "occupancy_component_count_6n": 0,
            "largest_occupancy_component_ratio_6n": 0.0,
            "root_component_ratio": 0.0,
            "root_reachable_units": 0,
            "orphan_mass_ratio": 0.0,
            "tip_count_proxy": 0,
            "branching_proxy": 0,
            "orphan_tip_proxy": 0,
            "root_reachable_tip_ratio": 0.0,
            "geodesic_proxy_max_depth": 0,
        }
    occupied = {tuple(map(int, c)) for c in coords}
    dirs = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    degree: dict[tuple[int, int, int], int] = {}
    for c in occupied:
        degree[c] = sum((c[0] + d[0], c[1] + d[1], c[2] + d[2]) in occupied for d in dirs)
    seen: set[tuple[int, int, int]] = set()
    comp_sizes: list[int] = []
    comp_of: dict[tuple[int, int, int], int] = {}
    for start in occupied:
        if start in seen:
            continue
        cid = len(comp_sizes)
        q: deque[tuple[int, int, int]] = deque([start])
        seen.add(start)
        size = 0
        while q:
            cur = q.popleft()
            comp_of[cur] = cid
            size += 1
            for d in dirs:
                nxt = (cur[0] + d[0], cur[1] + d[1], cur[2] + d[2])
                if nxt in occupied and nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        comp_sizes.append(size)
    root_comp = comp_of.get(root, -1)
    root_seen: set[tuple[int, int, int]] = set()
    hop_dist: dict[tuple[int, int, int], int] = {}
    if root_comp >= 0:
        q = deque([root])
        root_seen.add(root)
        hop_dist[root] = 0
        while q:
            cur = q.popleft()
            for d in dirs:
                nxt = (cur[0] + d[0], cur[1] + d[1], cur[2] + d[2])
                if nxt in occupied and nxt not in root_seen:
                    root_seen.add(nxt)
                    hop_dist[nxt] = hop_dist[cur] + 1
                    q.append(nxt)
    tips = [c for c, deg in degree.items() if deg <= 1]
    root_tips = [c for c in tips if c in root_seen]
    orphan_tips = [c for c in tips if c not in root_seen]
    branch_voxels = [c for c, deg in degree.items() if deg >= 3 and c in root_seen]
    largest = max(comp_sizes) if comp_sizes else 0
    total = len(occupied)
    return {
        "occupancy_component_count_6n": int(len(comp_sizes)),
        "largest_occupancy_component_ratio_6n": float(largest / max(total, 1)),
        "root_component_ratio": float(len(root_seen) / max(total, 1)),
        "root_reachable_units": int(len(root_seen)),
        "orphan_mass_ratio": float(1.0 - len(root_seen) / max(total, 1)),
        "tip_count_proxy": int(len(root_tips)),
        "branching_proxy": int(len(branch_voxels)),
        "orphan_tip_proxy": int(len(orphan_tips)),
        "root_reachable_tip_ratio": float(len(root_tips) / max(len(tips), 1)),
        "branching_per_tip_proxy": float(len(branch_voxels) / max(len(root_tips), 1)),
        "geodesic_proxy_max_depth": int(max(hop_dist.values(), default=0)),
    }


def metric_from_mesh(path: Path, label: str, resolution: int, max_edge_samples: int) -> dict[str, object]:
    vertices, faces, loader, error = load_geometry(path)
    coords, occ_status = occupancy_coords_from_mesh(vertices, faces, resolution, max_edge_samples)
    root = choose_root_voxel(coords)
    graph = occupancy_graph_metrics(coords, root)
    bbox = bbox_stats(vertices)
    pitch = float(occ_status.get("voxel_pitch_world", 0.0))
    max_len = float(graph["geodesic_proxy_max_depth"]) * pitch
    bbox_diag = float(bbox["bbox_diag"])
    row: dict[str, object] = {
        "label": label,
        "path": str(path),
        "source_type": path.suffix.lower().lstrip("."),
        "metric_level": "mesh_voxel_proxy",
        "family": infer_family(label, str(path)),
        "loader": loader,
        "load_error": error,
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
        "occupancy_resolution": int(resolution),
        "occupied_voxels": int(len(coords)),
        "root_seed_policy": "min_z_voxel_closest_to_xy_centroid",
        "root_voxel": "" if root is None else f"{root[0]},{root[1]},{root[2]}",
        "geodesic_proxy_max_length": max_len,
        "bbox_normalized_path_span": float(max_len / max(bbox_diag, 1e-12)),
        "skeletonization_status": "not_skeletonized_voxel_proxy_only",
        "paper_use_tier": "proxy_screening_or_appendix_only_without_skeleton_or_manual_QA",
        "caveat": "Mesh rows use vertex occupancy 6-neighborhood proxies; tip/branch/path counts are not reliable skeleton metrics.",
    }
    row.update(bbox)
    row.update(occ_status)
    row.update(graph)
    return row


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def default_cases(project_root: Path) -> list[tuple[str, Path, str]]:
    cases: list[tuple[str, Path, str]] = []

    vine_metrics = project_root / "results/vine_depth_textured_showcase_metrics_20260509/metrics.csv"
    for row in read_csv_dicts(vine_metrics):
        p = Path(row.get("path", ""))
        if p.exists():
            cases.append((row.get("label") or p.parent.name, p, "mesh"))

    sc_summary = project_root / "results/traditional_baselines_space_colonization_20260508_v2/summary.json"
    if sc_summary.exists():
        data = json.loads(sc_summary.read_text(encoding="utf-8"))
        for row in data.get("rows", []):
            case = row.get("case") or Path(row.get("mesh", "")).parent.name
            skeleton = Path(row.get("mesh", "")).parent / "skeleton.json"
            mesh = Path(row.get("mesh", ""))
            if skeleton.exists():
                cases.append((f"{case}_skeleton", skeleton, "skeleton"))
            if mesh.exists():
                cases.append((f"{case}_tube_mesh", mesh, "mesh"))

    explicit_meshes = [
        "results/connected_scaffold_cases_v2_20260509/root_vine_connected_control/root_vine_connected_control.obj",
        "results/traditional_baselines/run_20260507_0300/lsystem_branch.obj",
        "results/traditional_baselines/run_20260507_0300/ifs_branch_tree.obj",
        "visuals/siga_night_20260508/projection_pruning_compete_0550/tree_compete_d4_pruned.obj",
        "visuals/siga_night_20260508/projection_pruning_compete_0550/tree_compete_fork_d4_pruned.obj",
        "visuals/siga_night_20260508/projection_pruning_compete_0550/masked_tree_compete_fork_s1_a025_d3_pruned.obj",
        "visuals/public_guide_textured_glb_20260509/tree_compete_d4_pruned_tree_roots_steps8_tex2048_xformers/textured.glb",
        "visuals/public_guide_textured_glb_20260509/vine_compete_stage03_parthenocissus_steps8_tex2048_xformers/textured.glb",
        "visuals/public_guide_textured_glb_20260509/vine_compete_stage03_spiky_tendril_steps8_tex2048_xformers/textured.glb",
    ]
    for rel in explicit_meshes:
        p = project_root / rel
        if p.exists():
            cases.append((p.parent.name if p.name == "textured.glb" else p.stem, p, "mesh"))

    dedup: dict[tuple[str, str], tuple[str, Path, str]] = {}
    for label, path, kind in cases:
        dedup[(label, str(path))] = (label, path, kind)
    return list(dedup.values())


def parse_case_item(item: str) -> tuple[str, Path, str]:
    label, raw = item.split("=", 1) if "=" in item else (Path(item).stem, item)
    path = Path(raw)
    kind = "skeleton" if path.name == "skeleton.json" or path.suffix.lower() == ".json" else "mesh"
    return label, path, kind


def write_outputs(
    rows: list[dict[str, object]],
    missing: list[dict[str, str]],
    out_dir: Path,
    resolution: int,
    max_edge_voxelization_faces: int,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "metric_schema": "branch_path_root_reachability_20260509_v1",
        "occupancy_resolution": resolution,
        "rows": rows,
        "missing": missing,
        "notes": [
            "root_component_ratio is primary for root reachability; mesh rows use min-z root voxel.",
            "space-colonization skeleton rows use saved graph topology and are stronger evidence than mesh proxy rows.",
            "mesh tip_count_proxy, branching_proxy, geodesic_proxy_max_depth, and bbox_normalized_path_span are vertex-occupancy proxies, not reliable skeletonization.",
            "Do not use these tables alone as paper topology proof without same-root/same-depth protocol, neutral render, and zoom-in QA.",
        ],
    }
    (out_dir / "branch_path_metrics.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    if rows:
        fieldnames = sorted({k for row in rows for k in row if not isinstance(row.get(k), (list, dict))})
        with (out_dir / "branch_path_metrics.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in fieldnames})
    compact_fields = [
        "label",
        "family",
        "metric_level",
        "root_component_ratio",
        "geodesic_proxy_max_depth",
        "bbox_normalized_path_span",
        "tip_count_proxy",
        "branching_proxy",
        "orphan_tip_proxy",
        "paper_use_tier",
    ]
    with (out_dir / "branch_path_metrics_compact.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=compact_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in compact_fields})
    config = {
        "project_root": str(PROJECT_ROOT),
        "output_dir": str(out_dir),
        "occupancy_resolution": resolution,
        "max_edge_voxelization_faces": int(max_edge_voxelization_faces),
        "case_count": len(rows),
        "missing_count": len(missing),
    }
    (out_dir / "run_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--occupancy-resolution", type=int, default=64)
    parser.add_argument(
        "--max-edge-voxelization-faces",
        type=int,
        default=120000,
        help="Rasterize triangle edges into occupancy for meshes up to this face count; 0 disables it.",
    )
    parser.add_argument("--case", action="append", default=[], help="label=path, may be repeated")
    args = parser.parse_args()

    cases = [parse_case_item(item) for item in args.case] if args.case else default_cases(args.project_root)
    rows: list[dict[str, object]] = []
    missing: list[dict[str, str]] = []
    for label, path, kind in cases:
        if not path.exists():
            missing.append({"label": label, "path": str(path), "kind": kind})
            continue
        if kind == "skeleton":
            rows.append(metric_from_skeleton_json(path, label))
        else:
            rows.append(metric_from_mesh(path, label, args.occupancy_resolution, args.max_edge_voxelization_faces))
        print(f"done {label}")
    write_outputs(rows, missing, args.out_dir, args.occupancy_resolution, args.max_edge_voxelization_faces)
    print(json.dumps({"rows": len(rows), "missing": len(missing), "out_dir": str(args.out_dir)}, indent=2))


if __name__ == "__main__":
    main()
