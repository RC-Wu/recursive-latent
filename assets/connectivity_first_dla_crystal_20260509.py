#!/usr/bin/env python3
"""Connectivity-first DLA/crystal recursive growth experiments.

This runner tests concrete anti-fragmentation operators:

1. sparse occupancy closing and bridge-to-main-component before decode;
2. mesh projection that attaches selected islands back to the main component;
3. optional voxel-union smoothing before sample selection/texturing;
4. sample selection by occupancy largest-component ratio and component count.

The GPU-heavy Trellis2 imports are intentionally lazy so the coordinate
operators can be tested locally without the remote runtime.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
import traceback
from collections import deque
from pathlib import Path

import numpy as np


ASSET_DIR = Path(__file__).resolve().parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))


DEFAULT_ROOT = Path("/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507")
RUN_NAME = "connectivity_first_dla_crystal_20260509"


def write_obj(path: Path, vertices, faces) -> None:
    vertices = np.asarray(vertices)
    faces = np.asarray(faces)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for v in vertices:
            f.write(f"v {float(v[0]):.6f} {float(v[1]):.6f} {float(v[2]):.6f}\n")
        for face in faces:
            f.write(f"f {int(face[0]) + 1} {int(face[1]) + 1} {int(face[2]) + 1}\n")


def render_preview(path: Path, vertices, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    vertices = np.asarray(vertices)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")
    if len(vertices):
        step = max(1, len(vertices) // 30000)
        pts = vertices[::step]
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=0.16, c=pts[:, 2], cmap="viridis")
        center = (vertices.min(0) + vertices.max(0)) / 2
        span = max(float((vertices.max(0) - vertices.min(0)).max()), 1e-3)
        ax.set_xlim(center[0] - span / 2, center[0] + span / 2)
        ax.set_ylim(center[1] - span / 2, center[1] + span / 2)
        ax.set_zlim(center[2] - span / 2, center[2] + span / 2)
    ax.set_title(title)
    ax.set_axis_off()
    ax.view_init(24, -42)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def neighbor_offsets(connectivity: int = 6) -> np.ndarray:
    offsets = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if dx == dy == dz == 0:
                    continue
                manhattan = abs(dx) + abs(dy) + abs(dz)
                if connectivity == 6 and manhattan == 1:
                    offsets.append((dx, dy, dz))
                elif connectivity == 18 and manhattan <= 2:
                    offsets.append((dx, dy, dz))
                elif connectivity == 26:
                    offsets.append((dx, dy, dz))
    return np.asarray(offsets, dtype=np.int64)


def connected_components_coords(coords: np.ndarray, connectivity: int = 6) -> list[np.ndarray]:
    coords = np.asarray(coords, dtype=np.int64)
    if len(coords) == 0:
        return []
    unique = np.unique(coords, axis=0)
    occupied = {tuple(map(int, row)) for row in unique.tolist()}
    offsets = neighbor_offsets(connectivity)
    seen: set[tuple[int, int, int]] = set()
    comps: list[np.ndarray] = []
    for start in occupied:
        if start in seen:
            continue
        q: deque[tuple[int, int, int]] = deque([start])
        seen.add(start)
        rows = []
        while q:
            cur = q.popleft()
            rows.append(cur)
            base = np.asarray(cur, dtype=np.int64)
            for off in offsets:
                nxt = tuple(map(int, (base + off).tolist()))
                if nxt in occupied and nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        comps.append(np.asarray(rows, dtype=np.int64))
    comps.sort(key=len, reverse=True)
    return comps


def occupancy_connectivity_stats(coords: np.ndarray, connectivity: int = 6) -> dict:
    comps = connected_components_coords(coords, connectivity=connectivity)
    total = int(len(np.unique(coords, axis=0))) if len(coords) else 0
    largest = int(len(comps[0])) if comps else 0
    return {
        "occupied_voxels": total,
        "component_count": int(len(comps)),
        "largest_component_voxels": largest,
        "largest_component_ratio": float(largest / max(total, 1)),
    }


def _radius_offsets(radius: int, connectivity: int) -> np.ndarray:
    radius = int(max(radius, 0))
    if radius == 0:
        return np.zeros((1, 3), dtype=np.int64)
    offsets = []
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                dist1 = abs(dx) + abs(dy) + abs(dz)
                dist_inf = max(abs(dx), abs(dy), abs(dz))
                if connectivity == 6 and dist1 <= radius:
                    offsets.append((dx, dy, dz))
                elif connectivity == 18 and dist1 <= radius + 1 and dist_inf <= radius:
                    offsets.append((dx, dy, dz))
                elif connectivity == 26 and dist_inf <= radius:
                    offsets.append((dx, dy, dz))
    return np.asarray(offsets, dtype=np.int64)


def _dilate_coords(coords: np.ndarray, radius: int, connectivity: int) -> np.ndarray:
    coords = np.asarray(coords, dtype=np.int64)
    if len(coords) == 0 or radius <= 0:
        return np.unique(coords, axis=0)
    offsets = _radius_offsets(radius, connectivity)
    expanded = (coords[:, None, :] + offsets[None, :, :]).reshape(-1, 3)
    return np.unique(expanded, axis=0)


def _erode_coords(coords: np.ndarray, radius: int, connectivity: int, bounds_min: np.ndarray, bounds_max: np.ndarray) -> np.ndarray:
    coords = np.asarray(coords, dtype=np.int64)
    if len(coords) == 0 or radius <= 0:
        return np.unique(coords, axis=0)
    occupied = {tuple(map(int, row)) for row in coords.tolist()}
    offsets = _radius_offsets(radius, connectivity)
    ranges = [np.arange(bounds_min[i], bounds_max[i] + 1, dtype=np.int64) for i in range(3)]
    kept = []
    for x in ranges[0]:
        for y in ranges[1]:
            for z in ranges[2]:
                base = np.asarray((x, y, z), dtype=np.int64)
                if all(tuple(map(int, (base + off).tolist())) in occupied for off in offsets):
                    kept.append((int(x), int(y), int(z)))
    if not kept:
        return np.zeros((0, 3), dtype=np.int64)
    return np.asarray(kept, dtype=np.int64)


def _fill_axis_aligned_gaps(coords: np.ndarray, max_gap: int) -> np.ndarray:
    coords = np.asarray(coords, dtype=np.int64)
    if len(coords) == 0 or max_gap <= 1:
        return np.unique(coords, axis=0)
    occupied = {tuple(map(int, row)) for row in coords.tolist()}
    added = []
    axes = np.eye(3, dtype=np.int64)
    for row in coords:
        for axis in axes:
            for sign in (-1, 1):
                for dist in range(2, max_gap + 1):
                    other = tuple(map(int, (row + sign * dist * axis).tolist()))
                    if other in occupied:
                        for step in range(1, dist):
                            added.append(tuple(map(int, (row + sign * step * axis).tolist())))
                        break
    if added:
        coords = np.vstack([coords, np.asarray(added, dtype=np.int64)])
    return np.unique(coords, axis=0)


def morphological_close_coords(coords: np.ndarray, radius: int = 1, connectivity: int = 6) -> np.ndarray:
    """Close a sparse occupancy set and fill small axis-aligned gaps."""
    coords = np.asarray(coords, dtype=np.int64)
    if len(coords) == 0 or radius <= 0:
        return np.unique(coords, axis=0)
    bounds_min = coords.min(axis=0) - radius
    bounds_max = coords.max(axis=0) + radius
    dilated = _dilate_coords(coords, radius=radius, connectivity=connectivity)
    eroded = _erode_coords(dilated, radius=radius, connectivity=connectivity, bounds_min=bounds_min, bounds_max=bounds_max)
    closed = np.vstack([coords, eroded]) if len(eroded) else coords
    return _fill_axis_aligned_gaps(closed, max_gap=2 * radius + 1)


def _nearest_pair(a: np.ndarray, b: np.ndarray, sample_limit: int = 2048) -> tuple[np.ndarray, np.ndarray, float]:
    if len(a) > sample_limit:
        a = a[np.linspace(0, len(a) - 1, sample_limit).astype(np.int64)]
    if len(b) > sample_limit:
        b = b[np.linspace(0, len(b) - 1, sample_limit).astype(np.int64)]
    best = (a[0], b[0], float("inf"))
    chunk = 512
    b_float = b.astype(np.float64)
    for i in range(0, len(a), chunk):
        aa = a[i : i + chunk].astype(np.float64)
        d2 = ((aa[:, None, :] - b_float[None, :, :]) ** 2).sum(axis=2)
        flat = int(d2.argmin())
        ai, bi = divmod(flat, d2.shape[1])
        dist = float(math.sqrt(float(d2[ai, bi])))
        if dist < best[2]:
            best = (aa[ai].astype(np.int64), b[bi].astype(np.int64), dist)
    return best


def _line_voxels(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    steps = int(max(np.abs(b - a).max(), 1)) + 1
    pts = np.rint(np.linspace(a, b, steps)).astype(np.int64)
    return np.unique(pts, axis=0)


def bridge_components_to_largest(
    coords: np.ndarray,
    connectivity: int = 6,
    max_components: int = 12,
    min_component_voxels: int = 1,
    max_bridge_length: float | None = None,
) -> tuple[np.ndarray, dict]:
    coords = np.asarray(coords, dtype=np.int64)
    if len(coords) == 0:
        return coords, {"components_before": 0, "components_after": 0, "bridge_voxels_added": 0}
    comps = connected_components_coords(coords, connectivity=connectivity)
    if len(comps) <= 1:
        stats = occupancy_connectivity_stats(coords, connectivity=connectivity)
        return np.unique(coords, axis=0), {
            "components_before": int(len(comps)),
            "components_after": stats["component_count"],
            "bridge_voxels_added": 0,
        }
    main = comps[0]
    all_rows = [coords]
    added_total = 0
    bridged = 0
    for comp in comps[1 : max_components + 1]:
        if len(comp) < min_component_voxels:
            continue
        p_main, p_comp, dist = _nearest_pair(main, comp)
        if max_bridge_length is not None and dist > max_bridge_length:
            continue
        line = _line_voxels(p_main, p_comp)
        all_rows.append(line)
        added_total += int(len(line))
        bridged += 1
    out = np.unique(np.vstack(all_rows), axis=0)
    stats = occupancy_connectivity_stats(out, connectivity=connectivity)
    return out, {
        "components_before": int(len(comps)),
        "components_after": stats["component_count"],
        "bridge_voxels_added": int(max(len(out) - len(np.unique(coords, axis=0)), 0)),
        "bridged_components": int(bridged),
    }


def clip_coords_np(coords: np.ndarray, limit: int) -> np.ndarray:
    coords = np.asarray(coords, dtype=np.int64)
    if len(coords) == 0:
        return coords
    mask = ((coords >= 0) & (coords <= int(limit))).all(axis=1)
    return np.unique(coords[mask], axis=0)


def cap_target_coords(original: np.ndarray, target: np.ndarray, max_tokens: int) -> np.ndarray:
    original = np.unique(original.astype(np.int64), axis=0)
    target = np.unique(target.astype(np.int64), axis=0)
    if len(target) <= max_tokens:
        return target
    original_set = {tuple(row) for row in original.tolist()}
    added = np.asarray([row for row in target.tolist() if tuple(row) not in original_set], dtype=np.int64)
    budget = max(max_tokens - len(original), 0)
    if budget <= 0 or len(added) == 0:
        return original[:max_tokens]
    order = np.lexsort((added[:, 2], added[:, 1], added[:, 0]))
    kept = added[order[:budget]]
    return np.unique(np.vstack([original, kept]), axis=0)


def sparse_with_target_coords(st, target_xyz: np.ndarray):
    import torch
    from trellis2.modules.sparse import SparseTensor

    target_xyz = np.asarray(target_xyz, dtype=np.int64)
    old_xyz = st.coords[:, 1:].detach()
    device = st.coords.device
    target = torch.as_tensor(target_xyz, dtype=st.coords.dtype, device=device)
    if len(target) == 0:
        return st
    old_float = old_xyz.float()
    target_float = target.float()
    nearest = []
    chunk = 2048
    for i in range(0, target.shape[0], chunk):
        d = torch.cdist(target_float[i : i + chunk], old_float)
        nearest.append(torch.argmin(d, dim=1))
    nearest_idx = torch.cat(nearest, dim=0)
    feats = st.feats[nearest_idx].clone()
    batch = torch.zeros((target.shape[0], 1), dtype=st.coords.dtype, device=device)
    coords4 = torch.cat([batch, target], dim=1)
    return SparseTensor(feats=feats, coords=coords4)


def project_sparse_before_decode(st, method: str, limit: int, close_radius: int, max_tokens: int) -> tuple[object, dict]:
    xyz = st.coords[:, 1:].detach().cpu().numpy().astype(np.int64)
    before = occupancy_connectivity_stats(xyz, connectivity=6)
    target = np.unique(xyz, axis=0)
    report = {"sparse_before": before, "method": method}
    if "close" in method:
        target = morphological_close_coords(target, radius=close_radius, connectivity=6)
    if "bridge" in method:
        target, bridge_report = bridge_components_to_largest(target, connectivity=6, max_components=16)
        report["sparse_bridge"] = bridge_report
    target = clip_coords_np(target, limit)
    target = cap_target_coords(xyz, target, max_tokens=max_tokens)
    report["sparse_after"] = occupancy_connectivity_stats(target, connectivity=6)
    report["sparse_tokens_before"] = int(len(np.unique(xyz, axis=0)))
    report["sparse_tokens_after"] = int(len(target))
    return sparse_with_target_coords(st, target), report


def load_mesh_any(path: Path):
    import trimesh

    loaded = trimesh.load(str(path), force=None, process=False)
    if hasattr(loaded, "geometry"):
        meshes = [m for m in loaded.geometry.values() if hasattr(m, "vertices")]
        if not meshes:
            raise ValueError(f"no mesh geometry in {path}")
        return trimesh.util.concatenate(meshes)
    return loaded


def export_mesh(mesh, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(str(path))


def mesh_component_metrics(mesh_path: Path, occupancy_resolution: int = 64) -> dict:
    from recursive_growth_mesh_metrics import load_geometry, component_stats, occupancy_stats

    vertices, faces, loader, error = load_geometry(mesh_path)
    face = component_stats(vertices, faces)
    occ = occupancy_stats(vertices, occupancy_resolution)
    return {
        "path": str(mesh_path),
        "loader": loader,
        "load_error": error,
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
        "face_component_count": int(face["component_count"]),
        "face_largest_component_ratio": float(face["largest_component_vertex_ratio"]),
        "occupancy_component_count": int(occ["occupancy_component_count_6n"]),
        "occupancy_lcr": float(occ["largest_occupancy_component_ratio_6n"]),
        "occupied_voxels": int(occ["occupied_voxels"]),
    }


def _sample_vertices(vertices: np.ndarray, limit: int = 4096) -> np.ndarray:
    vertices = np.asarray(vertices, dtype=np.float64)
    if len(vertices) <= limit:
        return vertices
    return vertices[np.linspace(0, len(vertices) - 1, limit).astype(np.int64)]


def nearest_vertices(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    aa = _sample_vertices(a)
    bb = _sample_vertices(b)
    best = (aa[0], bb[0], float("inf"))
    for i in range(0, len(aa), 512):
        d2 = ((aa[i : i + 512, None, :] - bb[None, :, :]) ** 2).sum(axis=2)
        flat = int(d2.argmin())
        ai, bi = divmod(flat, d2.shape[1])
        dist = float(math.sqrt(float(d2[ai, bi])))
        if dist < best[2]:
            best = (aa[i + ai], bb[bi], dist)
    return best


def make_bridge_mesh(a: np.ndarray, b: np.ndarray, radius: float):
    import trimesh

    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if np.linalg.norm(b - a) < 1e-8:
        return None
    try:
        return trimesh.creation.cylinder(radius=max(float(radius), 1e-5), sections=8, segment=np.vstack([a, b]))
    except Exception:
        mid = (a + b) / 2
        ext = np.maximum(np.abs(b - a), radius)
        box = trimesh.creation.box(extents=ext)
        box.apply_translation(mid)
        return box


def voxel_union_smooth(mesh, pitch_ratio: float):
    if pitch_ratio <= 0 or len(mesh.vertices) == 0:
        return mesh, {"voxel_smoothing": "disabled"}
    diag = float(np.linalg.norm(mesh.bounds[1] - mesh.bounds[0]))
    pitch = max(diag * pitch_ratio, 1e-4)
    try:
        vox = mesh.voxelized(pitch)
        try:
            vox = vox.fill()
        except Exception:
            pass
        smoothed = vox.marching_cubes
        return smoothed, {"voxel_smoothing": "ok", "voxel_pitch": pitch}
    except Exception as exc:
        return mesh, {"voxel_smoothing": "failed", "error": repr(exc), "voxel_pitch": pitch}


def project_mesh_with_bridges(
    mesh_path: Path,
    out_path: Path,
    min_vertices: int,
    bridge_components: int,
    bridge_radius_ratio: float,
    voxel_pitch_ratio: float,
) -> dict:
    import trimesh

    mesh = load_mesh_any(mesh_path)
    pieces = list(mesh.split(only_watertight=False))
    if not pieces:
        export_mesh(mesh, out_path)
        return {"mesh_projection": "no_components", "output": str(out_path)}
    pieces.sort(key=lambda m: len(m.vertices), reverse=True)
    main = pieces[0]
    kept = [main]
    bridges = []
    diag = float(np.linalg.norm(mesh.bounds[1] - mesh.bounds[0]))
    radius = max(diag * bridge_radius_ratio, 1e-4)
    attached = 0
    pruned = 0
    kept_large = 0
    for piece in pieces[1:]:
        if len(piece.vertices) >= min_vertices:
            kept.append(piece)
            kept_large += 1
            if attached < bridge_components:
                a, b, dist = nearest_vertices(np.asarray(main.vertices), np.asarray(piece.vertices))
                bridge = make_bridge_mesh(a, b, radius=radius)
                if bridge is not None:
                    bridges.append(bridge)
                    attached += 1
            continue
        if attached < bridge_components and len(piece.vertices) >= max(8, min_vertices // 20):
            a, b, dist = nearest_vertices(np.asarray(main.vertices), np.asarray(piece.vertices))
            bridge = make_bridge_mesh(a, b, radius=radius)
            if bridge is not None:
                bridges.append(bridge)
                kept.append(piece)
                attached += 1
                continue
        pruned += 1
    merged = trimesh.util.concatenate(kept + bridges)
    try:
        merged.merge_vertices(digits_vertex=5)
    except Exception:
        pass
    merged, smooth_report = voxel_union_smooth(merged, pitch_ratio=voxel_pitch_ratio)
    try:
        merged.merge_vertices(digits_vertex=5)
    except Exception:
        pass
    export_mesh(merged, out_path)
    metrics = mesh_component_metrics(out_path)
    return {
        "input_components": int(len(pieces)),
        "kept_components": int(len(kept)),
        "kept_large_components": int(kept_large),
        "attached_components": int(attached),
        "bridge_meshes_added": int(len(bridges)),
        "pruned_components": int(pruned),
        "bridge_radius": float(radius),
        "output": str(out_path),
        "smooth": smooth_report,
        "metrics": metrics,
    }


def rewrite_model_path(path: str, snapshot: Path) -> str:
    return str(snapshot / path) if path.startswith("ckpts/") else path


def load_trellis_models(args):
    import torch
    from trellis2 import models

    candidate_homes = []
    if os.environ.get("HF_HOME"):
        candidate_homes.append(Path(os.environ["HF_HOME"]))
    candidate_homes.append(args.root / "hf_home")
    candidate_homes.append(args.root / "cache/hf")
    snapshot_root = None
    for hf in candidate_homes:
        root = hf / "hub/models--microsoft--TRELLIS.2-4B/snapshots"
        if root.exists():
            snapshot_root = root
            break
    if snapshot_root is None:
        raise FileNotFoundError(
            "Could not find TRELLIS.2-4B snapshot under "
            + ", ".join(str(p) for p in candidate_homes)
        )
    snapshot = next(snapshot_root.iterdir())
    pipeline_cfg = json.loads((snapshot / "pipeline.json").read_text())["args"]["models"]
    texturing_cfg = json.loads((snapshot / "texturing_pipeline.json").read_text())["args"]["models"]
    encoder = models.from_pretrained(rewrite_model_path(texturing_cfg["shape_slat_encoder"], snapshot)).eval().cuda()
    decoder = models.from_pretrained(rewrite_model_path(pipeline_cfg["shape_slat_decoder"], snapshot)).eval().cuda()
    decoder.set_resolution(args.resolution)
    decoder.low_vram = True
    torch.cuda.empty_cache()
    return encoder, decoder


def encode_mesh(mesh_path: Path, encoder, args):
    import o_voxel
    import torch
    import trimesh
    from trellis2.modules.sparse import SparseTensor

    mesh = trimesh.load(str(mesh_path), force="mesh", process=False)
    vertices_np = np.asarray(mesh.vertices).astype(np.float32)
    faces_np = np.asarray(mesh.faces).astype(np.int64)
    vmin = vertices_np.min(axis=0)
    vmax = vertices_np.max(axis=0)
    center = (vmin + vmax) / 2
    scale = args.fit_scale / max(float((vmax - vmin).max()), 1e-6)
    vertices_np = (vertices_np - center) * scale
    tmp = vertices_np[:, 1].copy()
    vertices_np[:, 1] = -vertices_np[:, 2]
    vertices_np[:, 2] = tmp

    voxel_indices, dual_vertices, intersected = o_voxel.convert.mesh_to_flexible_dual_grid(
        torch.from_numpy(vertices_np).float().cpu(),
        torch.from_numpy(faces_np).long().cpu(),
        grid_size=args.grid_resolution,
        aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
        face_weight=1.0,
        boundary_weight=0.2,
        regularization_weight=1e-2,
        timing=False,
    )
    sparse_vertices = SparseTensor(
        feats=dual_vertices * args.grid_resolution - voxel_indices,
        coords=torch.cat([torch.zeros_like(voxel_indices[:, 0:1]), voxel_indices], dim=-1),
    ).cuda()
    sparse_intersected = sparse_vertices.replace(intersected).cuda()
    with torch.no_grad():
        return encoder(sparse_vertices, sparse_intersected)


def decode_to_obj(st, decoder, out_obj: Path, preview: Path, title: str) -> dict:
    import torch

    with torch.no_grad():
        decoded = decoder(st)[0]
    vertices = decoded.vertices.detach().cpu().numpy()
    faces = decoded.faces.detach().cpu().numpy()
    write_obj(out_obj, vertices, faces)
    render_preview(preview, vertices, title)
    return {"vertices": int(len(vertices)), "faces": int(len(faces))}


def method_options(method: str, args) -> dict:
    return {
        "sparse": False if "raw" in method else ("sparse" in method or "close" in method or "bridge" in method),
        "voxel_pitch_ratio": args.voxel_pitch_ratio if "smooth" in method or "union" in method else 0.0,
        "mesh_bridge_components": args.mesh_bridge_components if "mesh_bridge" in method or "bridge" in method else 0,
    }


def run_candidate(case_label: str, root_mesh: Path, grammar: str, method: str, encoder, decoder, grammar_mod, args) -> dict:
    import torch

    out_root = args.out / case_label / grammar / method
    out_root.mkdir(parents=True, exist_ok=True)
    current_mesh = root_mesh
    limit = args.resolution // 16 - 1
    candidate_summary = {
        "case": case_label,
        "root_mesh": str(root_mesh),
        "grammar": grammar,
        "method": method,
        "stages": [],
    }
    opts = method_options(method, args)
    for stage in range(1, args.stages + 1):
        stage_dir = out_root / f"stage_{stage:02d}"
        raw_dir = stage_dir / "raw"
        sparse_dir = stage_dir / "sparse_connectivity"
        proj_dir = stage_dir / "projected"
        raw_dir.mkdir(parents=True, exist_ok=True)
        sparse_dir.mkdir(parents=True, exist_ok=True)
        proj_dir.mkdir(parents=True, exist_ok=True)

        stage_summary = {"stage": stage, "input_mesh": str(current_mesh)}
        st = encode_mesh(current_mesh, encoder, args)
        stage_summary["input_tokens"] = int(st.coords.shape[0])
        candidate = st
        for op in grammar_mod.GRAMMARS[grammar]:
            candidate = grammar_mod.apply_op(candidate, op, limit)
        stage_summary["proposal_tokens"] = int(candidate.coords.shape[0])
        raw_obj = raw_dir / "proposal_before_connectivity.obj"
        decode_to_obj(candidate, decoder, raw_obj, raw_dir / "proposal_before_connectivity.png", f"{case_label} {grammar} {method} raw s{stage}")
        stage_summary["raw_metrics"] = mesh_component_metrics(raw_obj)

        sparse_report = {"sparse_projection": "disabled"}
        projected_sparse = candidate
        if opts["sparse"]:
            projected_sparse, sparse_report = project_sparse_before_decode(
                candidate,
                method=method,
                limit=limit,
                close_radius=args.close_radius,
                max_tokens=args.max_tokens,
            )
        stage_summary["sparse_report"] = sparse_report
        sparse_obj = sparse_dir / "proposal_after_sparse_connectivity.obj"
        decode_to_obj(projected_sparse, decoder, sparse_obj, sparse_dir / "proposal_after_sparse_connectivity.png", f"{case_label} {method} sparse s{stage}")
        stage_summary["sparse_metrics"] = mesh_component_metrics(sparse_obj)

        projected_obj = proj_dir / "mesh_projected.obj"
        proj_report = project_mesh_with_bridges(
            sparse_obj,
            projected_obj,
            min_vertices=args.min_vertices,
            bridge_components=opts["mesh_bridge_components"],
            bridge_radius_ratio=args.bridge_radius_ratio,
            voxel_pitch_ratio=opts["voxel_pitch_ratio"],
        )
        render_preview(proj_dir / "mesh_projected.png", load_mesh_any(projected_obj).vertices, f"{case_label} {method} projected s{stage}")
        stage_summary["mesh_projection"] = proj_report
        current_mesh = projected_obj
        (out_root / "latest_mesh.txt").write_text(str(current_mesh), encoding="utf-8")
        candidate_summary["stages"].append(stage_summary)
        (out_root / "summary_partial.json").write_text(json.dumps(candidate_summary, indent=2), encoding="utf-8")
        torch.cuda.empty_cache()
    final_metrics = candidate_summary["stages"][-1]["mesh_projection"]["metrics"]
    candidate_summary["final_mesh"] = str(current_mesh)
    candidate_summary["final_metrics"] = final_metrics
    candidate_summary["selection_score"] = float(final_metrics["occupancy_lcr"] - 0.002 * final_metrics["occupancy_component_count"])
    (out_root / "summary.json").write_text(json.dumps(candidate_summary, indent=2), encoding="utf-8")
    return candidate_summary


def parse_cases(items: list[str], root: Path) -> list[tuple[str, Path]]:
    if items:
        out = []
        for item in items:
            label, raw = item.split("=", 1)
            out.append((label, Path(raw)))
        return out
    defaults = [
        ("dla_voxel_root", root / "inputs/procedural_meshes/dla_cluster_voxels.obj"),
        ("porous_bismuth_crystal_proxy", root / "selected_meshes_for_texture_20260508/porous_container_compete_stage03.obj"),
        ("vine_root_control", root / "results/siga_root_quality_sweep/root_quality_gpu6_20260508_0505/example04_vine_curl_steps12_seed910/trellis2_dinov3_min.obj"),
    ]
    return defaults


def texture_selected(candidates: list[dict], args) -> list[dict]:
    if args.texture_top_k <= 0:
        return []
    image_by_case = {
        "dla": args.root / "public_guides_20260508/processed/bismuth_crystal_square.png",
        "porous": args.root / "public_guides_20260508/processed/bismuth_crystal_square.png",
        "crystal": args.root / "public_guides_20260508/processed/bismuth_crystal_square.png",
        "vine": args.root / "public_guides_20260508/processed/spiky_plant_tendril_square.png",
        "tree": args.root / "public_guides_20260508/processed/tree_roots_arlington_square.png",
    }
    dino = args.root / "weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"
    selected = sorted(candidates, key=lambda row: row["selection_score"], reverse=True)[: args.texture_top_k]
    reports = []
    for row in selected:
        case = row["case"].lower()
        image = args.root / "public_guides_20260508/processed/pyrite_cubes_square.png"
        for key, value in image_by_case.items():
            if key in case and value.exists():
                image = value
                break
        out = args.out / row["case"] / row["grammar"] / row["method"] / "selected_texturing"
        cmd = [
            os.environ.get("PYTHON", "python"),
            str(args.root / "assets/trellis2_texturing_latent_smoke.py"),
            "--mesh",
            row["final_mesh"],
            "--image",
            str(image),
            "--dinov3-model",
            str(dino),
            "--out",
            str(out),
            "--steps",
            str(args.texture_steps),
            "--seed",
            str(args.texture_seed),
            "--resolution",
            str(args.resolution),
        ]
        start = time.time()
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        reports.append({
            "case": row["case"],
            "grammar": row["grammar"],
            "method": row["method"],
            "mesh": row["final_mesh"],
            "image": str(image),
            "out": str(out),
            "returncode": proc.returncode,
            "seconds": time.time() - start,
            "log_tail": proc.stdout.splitlines()[-80:],
        })
    return reports


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--case", action="append", default=[], help="label=/path/to/root.obj")
    parser.add_argument("--grammars", nargs="+", default=["compete_fork_attach", "fork_side_attach"])
    parser.add_argument("--methods", nargs="+", default=["sparse_close_bridge", "mesh_bridge_smooth"])
    parser.add_argument("--stages", type=int, default=3)
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--grid-resolution", type=int, default=512)
    parser.add_argument("--fit-scale", type=float, default=0.66)
    parser.add_argument("--max-tokens", type=int, default=14000)
    parser.add_argument("--min-vertices", type=int, default=1800)
    parser.add_argument("--close-radius", type=int, default=1)
    parser.add_argument("--mesh-bridge-components", type=int, default=10)
    parser.add_argument("--bridge-radius-ratio", type=float, default=0.004)
    parser.add_argument("--voxel-pitch-ratio", type=float, default=0.006)
    parser.add_argument("--texture-top-k", type=int, default=0)
    parser.add_argument("--texture-steps", type=int, default=2)
    parser.add_argument("--texture-seed", type=int, default=90509)
    args = parser.parse_args()
    args.out = args.out or (args.root / "results" / RUN_NAME)
    args.out.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    os.environ.setdefault("PYTHON", str(Path(os.sys.executable)))

    summary = {
        "run_name": RUN_NAME,
        "root": str(args.root),
        "out": str(args.out),
        "cases": [],
        "grammars": args.grammars,
        "methods": args.methods,
        "candidates": [],
        "missing_cases": [],
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    (args.out / "run_config.json").write_text(json.dumps(vars(args), indent=2, default=str), encoding="utf-8")
    try:
        from triton_beegfs_cache_patch import apply_triton_beegfs_cache_patch

        apply_triton_beegfs_cache_patch()
        import trellis2_recursive_slat_grammar_workflow as grammar_mod

        encoder, decoder = load_trellis_models(args)
        cases = parse_cases(args.case, args.root)
        for label, mesh in cases:
            if not mesh.exists():
                summary["missing_cases"].append({"label": label, "mesh": str(mesh)})
                continue
            summary["cases"].append({"label": label, "mesh": str(mesh)})
            for grammar in args.grammars:
                if grammar not in grammar_mod.GRAMMARS:
                    summary.setdefault("skipped_grammars", []).append(grammar)
                    continue
                for method in args.methods:
                    try:
                        candidate = run_candidate(label, mesh, grammar, method, encoder, decoder, grammar_mod, args)
                        summary["candidates"].append(candidate)
                        (args.out / "summary_partial.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
                    except Exception as exc:
                        summary.setdefault("candidate_errors", []).append({
                            "case": label,
                            "grammar": grammar,
                            "method": method,
                            "error": repr(exc),
                            "traceback_tail": traceback.format_exc().splitlines()[-80:],
                        })
        ranked = sorted(summary["candidates"], key=lambda row: row["selection_score"], reverse=True)
        summary["selected_candidates"] = [
            {
                "case": row["case"],
                "grammar": row["grammar"],
                "method": row["method"],
                "final_mesh": row["final_mesh"],
                "selection_score": row["selection_score"],
                "final_metrics": row["final_metrics"],
            }
            for row in ranked
        ]
        (args.out / "selected_candidates.json").write_text(json.dumps(summary["selected_candidates"], indent=2), encoding="utf-8")
        summary["texturing_reports"] = texture_selected(ranked, args)
        summary["status"] = "completed"
    except Exception as exc:
        summary["status"] = "failed"
        summary["error"] = repr(exc)
        summary["traceback_tail"] = traceback.format_exc().splitlines()[-120:]
    finally:
        summary["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        (args.out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
