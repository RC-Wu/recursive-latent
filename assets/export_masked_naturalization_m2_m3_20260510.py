#!/usr/bin/env python3
"""Export M2 visuals and M3 proxy sidecars for masked local naturalization."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial import cKDTree


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_ASSET_DIR = PROJECT_ROOT / "results" / "masked_naturalization_ablation_20260510"
DEFAULT_VISUAL_DIR = PROJECT_ROOT / "visuals" / "masked_naturalization_m2_m3_20260510"
DEFAULT_RESULT_DIR = PROJECT_ROOT / "results" / "masked_naturalization_m2_m3_20260510"
DEFAULT_STATUS_MD = PROJECT_ROOT / "docs" / "evaluation" / "masked_naturalization_m2_m3_status_zh_20260510.md"

VARIANT_ORDER = [
    "raw_grammar_proposal",
    "final_only_projection_repair",
    "per_depth_projection",
    "per_depth_weak_naturalization",
    "per_depth_global_naturalization",
    "per_depth_masked_naturalization",
]

PROTOCOL_LABELS = {
    "raw_grammar_proposal": "rule-only",
    "final_only_projection_repair": "final-only",
    "per_depth_projection": "per-depth/no-N",
    "per_depth_weak_naturalization": "per-depth/weak",
    "per_depth_global_naturalization": "per-depth/global-N",
    "per_depth_masked_naturalization": "per-depth/masked local-N",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_manifest(asset_dir: Path) -> list[dict[str, object]]:
    payload = _read_json(asset_dir / "manifest.json")
    return list(payload["rows"])


def _load_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(str(path), force="scene", process=False)
    meshes: list[trimesh.Trimesh] = []
    if isinstance(loaded, trimesh.Trimesh):
        meshes = [loaded]
    elif isinstance(loaded, trimesh.Scene):
        for node_name in loaded.graph.nodes_geometry:
            transform, geom_name = loaded.graph[node_name]
            geom = loaded.geometry.get(geom_name)
            if isinstance(geom, trimesh.Trimesh) and len(geom.vertices):
                mesh = geom.copy()
                mesh.apply_transform(transform)
                meshes.append(mesh)
    if not meshes:
        return trimesh.Trimesh(vertices=np.zeros((0, 3)), faces=np.zeros((0, 3), dtype=np.int64), process=False)
    mesh = trimesh.util.concatenate(meshes)
    mesh.remove_unreferenced_vertices()
    return mesh


def _format_float(value: float, digits: int = 4) -> str:
    return f"{float(value):.{digits}f}"


def _safe_font(size: int) -> ImageFont.ImageFont:
    for name in ("Arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def _task_camera(meshes: Iterable[trimesh.Trimesh]) -> dict[str, object]:
    points = [np.asarray(mesh.vertices, dtype=np.float64) for mesh in meshes if len(mesh.vertices)]
    if not points:
        return {"center": [0.0, 0.0, 0.0], "scale": 1.0, "axes": [0, 2], "depth_axis": 1}
    all_points = np.vstack(points)
    vmin = all_points.min(axis=0)
    vmax = all_points.max(axis=0)
    center = (vmin + vmax) * 0.5
    span = float(max((vmax - vmin)[[0, 2]].max(), 1e-6))
    return {"center": [float(x) for x in center.tolist()], "scale": span * 1.16, "axes": [0, 2], "depth_axis": 1}


def _project(points: np.ndarray, camera: dict[str, object], size: int, margin: int) -> np.ndarray:
    if len(points) == 0:
        return np.zeros((0, 2), dtype=np.float64)
    center = np.asarray(camera["center"], dtype=np.float64)
    axes = list(camera["axes"])
    scale = max(float(camera["scale"]), 1e-6)
    xy = (points[:, axes] - center[axes]) / scale
    px = margin + (xy[:, 0] + 0.5) * (size - 2 * margin)
    py = margin + (0.5 - xy[:, 1]) * (size - 2 * margin)
    return np.stack([px, py], axis=1)


def _mesh_panel(
    mesh: trimesh.Trimesh,
    camera: dict[str, object],
    title: str,
    size: int,
    mask_centers: np.ndarray | None = None,
    color: tuple[int, int, int] = (82, 115, 125),
) -> Image.Image:
    image = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(image, "RGBA")
    if len(mesh.vertices) and len(mesh.faces):
        vertices = np.asarray(mesh.vertices, dtype=np.float64)
        faces = np.asarray(mesh.faces, dtype=np.int64)
        max_faces = 9000
        if len(faces) > max_faces:
            idx = np.linspace(0, len(faces) - 1, max_faces).astype(np.int64)
            faces = faces[idx]
        proj = _project(vertices, camera, size, margin=max(20, size // 12))
        depth_axis = int(camera["depth_axis"])
        order = np.argsort(vertices[faces].mean(axis=1)[:, depth_axis])
        tri = vertices[faces]
        normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        norms = np.maximum(np.linalg.norm(normals, axis=1), 1e-8)
        shade = np.clip(0.44 + 0.56 * np.abs(normals[:, 1]) / norms, 0.34, 1.0)
        for face_idx in order:
            pts = [tuple(x) for x in proj[faces[face_idx]]]
            c = tuple(int(min(max(channel * shade[face_idx], 0), 255)) for channel in color)
            draw.polygon(pts, fill=(*c, 235))
    if mask_centers is not None and len(mask_centers):
        projected = _project(mask_centers, camera, size, margin=max(20, size // 12))
        radius = max(4, size // 54)
        for x, y in projected:
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=(215, 61, 48, 220), width=2)
    font = _safe_font(max(10, size // 26))
    draw.rectangle((0, 0, size, max(22, size // 9)), fill=(255, 255, 255, 210))
    draw.text((8, 5), title, font=font, fill=(28, 34, 37, 255))
    return image


def _paste_grid(path: Path, rows: list[list[Image.Image]], labels: list[list[str]] | None = None) -> None:
    if not rows or not rows[0]:
        raise ValueError("empty image grid")
    panel_w, panel_h = rows[0][0].size
    label_h = 0 if labels is None else 26
    gap = 8
    canvas = Image.new(
        "RGB",
        (len(rows[0]) * panel_w + (len(rows[0]) - 1) * gap, len(rows) * (panel_h + label_h) + (len(rows) - 1) * gap),
        "white",
    )
    draw = ImageDraw.Draw(canvas)
    font = _safe_font(13)
    for r, row in enumerate(rows):
        for c, image in enumerate(row):
            x = c * (panel_w + gap)
            y = r * (panel_h + label_h + gap)
            if labels is not None:
                draw.text((x + 4, y + 5), labels[r][c], font=font, fill=(31, 38, 41))
                y += label_h
            canvas.paste(image, (x, y))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def _active_primitives(metadata: dict) -> list[dict]:
    return [p for p in metadata.get("primitive_trace", []) if bool(p.get("masked")) and int(p.get("depth", 0)) > 0]


def _primitive_center(primitive: dict) -> np.ndarray:
    if primitive.get("kind") == "segment":
        return (np.asarray(primitive["a"], dtype=np.float64) + np.asarray(primitive["b"], dtype=np.float64)) * 0.5
    return np.asarray(primitive.get("center", [0.0, 0.0, 0.0]), dtype=np.float64)


def _surface_lcr(mesh: trimesh.Trimesh) -> float:
    if len(mesh.vertices) == 0:
        return 0.0
    if len(mesh.faces) == 0:
        return 1.0 / max(len(mesh.vertices), 1)
    comps = mesh.split(only_watertight=False)
    if not comps:
        return 0.0
    largest = max(len(comp.vertices) for comp in comps)
    return float(largest / max(len(mesh.vertices), 1))


def _nearest_mean_distance(points: np.ndarray, ref_points: np.ndarray) -> float:
    if len(points) == 0 or len(ref_points) == 0:
        return 0.0
    tree = cKDTree(ref_points)
    dist, _idx = tree.query(points, k=1)
    return float(np.mean(dist))


def _primitive_points(primitive: dict) -> list[np.ndarray]:
    if primitive.get("kind") == "segment":
        a = np.asarray(primitive["a"], dtype=np.float64)
        b = np.asarray(primitive["b"], dtype=np.float64)
        return [a, b, (a + b) * 0.5]
    return [np.asarray(primitive.get("center", [0.0, 0.0, 0.0]), dtype=np.float64)]


def _primitive_radius(primitive: dict) -> float:
    if primitive.get("kind") == "ellipsoid":
        return float(np.max(np.asarray(primitive.get("radii", [0.0]), dtype=np.float64)))
    return float(primitive.get("radius", 0.0))


def _primitive_mass_proxy(primitive: dict) -> float:
    kind = primitive.get("kind")
    if kind == "segment":
        a = np.asarray(primitive["a"], dtype=np.float64)
        b = np.asarray(primitive["b"], dtype=np.float64)
        radius = max(float(primitive.get("radius", 0.0)), 1e-6)
        length = float(np.linalg.norm(b - a))
        return float(math.pi * radius * radius * max(length, radius))
    if kind == "ellipsoid":
        radii = np.asarray(primitive.get("radii", [0.0, 0.0, 0.0]), dtype=np.float64)
        radii = np.maximum(radii, 1e-6)
        return float((4.0 / 3.0) * math.pi * radii[0] * radii[1] * radii[2])
    radius = max(float(primitive.get("radius", 0.0)), 1e-6)
    return float((4.0 / 3.0) * math.pi * radius**3)


def _normalized_role(role: str) -> str:
    out = str(role)
    if out.startswith("masked_naturalized_"):
        out = out.removeprefix("masked_naturalized_")
    return out


def _is_active_handle(primitive: dict) -> bool:
    role = str(primitive.get("role", ""))
    if int(primitive.get("depth", 0)) <= 0 or not bool(primitive.get("masked")):
        return False
    if role.startswith("projection_"):
        return False
    if "surface_continuity_kernel" in role:
        return False
    return True


def _is_frontier_handle(primitive: dict) -> bool:
    if not _is_active_handle(primitive):
        return False
    role = _normalized_role(str(primitive.get("role", "")))
    tokens = ("frontier", "terminal", "branch", "rootlet", "copy", "facet", "gap", "polyp", "hair")
    return any(token in role for token in tokens)


def _is_orphan_role(primitive: dict) -> bool:
    role = _normalized_role(str(primitive.get("role", "")))
    return "orphan" in role or "raw_gap" in role


def _contact_graph(primitive_trace: list[dict], contact_scale: float = 1.0) -> list[set[int]]:
    points = [_primitive_points(p) for p in primitive_trace]
    radii = [_primitive_radius(p) for p in primitive_trace]
    adjacency: list[set[int]] = [set() for _ in primitive_trace]
    for i in range(len(primitive_trace)):
        for j in range(i + 1, len(primitive_trace)):
            min_dist = min(float(np.linalg.norm(a - b)) for a in points[i] for b in points[j])
            threshold = max(0.035, float(contact_scale) * (radii[i] + radii[j]))
            if min_dist <= threshold:
                adjacency[i].add(j)
                adjacency[j].add(i)
    return adjacency


def _reachable_from_roots(primitive_trace: list[dict], adjacency: list[set[int]]) -> set[int]:
    roots = [i for i, p in enumerate(primitive_trace) if int(p.get("depth", 0)) == 0 and not bool(p.get("masked"))]
    reachable = set(roots)
    queue = list(roots)
    while queue:
        node = queue.pop(0)
        for nxt in adjacency[node]:
            if nxt not in reachable:
                reachable.add(nxt)
                queue.append(nxt)
    return reachable


def _handle_centers_by_role(metadata: dict) -> dict[tuple[int, str], list[np.ndarray]]:
    buckets: dict[tuple[int, str], list[np.ndarray]] = {}
    for primitive in metadata.get("primitive_trace", []):
        if not _is_active_handle(primitive):
            continue
        key = (int(primitive.get("depth", 0)), _normalized_role(str(primitive.get("role", ""))))
        buckets.setdefault(key, []).append(_primitive_center(primitive))
    return buckets


def _trace_handle_drift(metadata: dict, ref_metadata: dict) -> float:
    current = _handle_centers_by_role(metadata)
    reference = _handle_centers_by_role(ref_metadata)
    distances: list[float] = []
    for key, centers in current.items():
        ref_centers = reference.get(key)
        if not ref_centers:
            continue
        ref_points = np.asarray(ref_centers, dtype=np.float64)
        tree = cKDTree(ref_points)
        dist, _idx = tree.query(np.asarray(centers, dtype=np.float64), k=1)
        distances.extend(float(x) for x in np.atleast_1d(dist))
    return float(np.mean(distances)) if distances else 0.0


def _mask_overlap(metadata: dict, primitive_indices: list[int]) -> float:
    centers = (
        np.asarray(metadata.get("edit_mask_centers", []), dtype=np.float64).reshape((-1, 3))
        if metadata.get("edit_mask_centers")
        else np.zeros((0, 3))
    )
    primitive_trace = list(metadata.get("primitive_trace", []))
    if len(centers) == 0 or not primitive_indices:
        return 0.0
    active_centers = np.asarray([_primitive_center(primitive_trace[i]) for i in primitive_indices], dtype=np.float64)
    tree = cKDTree(centers)
    dist, _idx = tree.query(active_centers, k=1)
    return float(np.mean(dist <= max(float(metadata.get("edit_mask_radius", 0.22)), 1e-6)))


def _trace_graph_row(task_id: str, variant: str, metadata: dict, ref_metadata: dict) -> dict[str, object]:
    primitive_trace = list(metadata.get("primitive_trace", []))
    adjacency = _contact_graph(primitive_trace)
    reachable = _reachable_from_roots(primitive_trace, adjacency)
    active_indices = [i for i, p in enumerate(primitive_trace) if _is_active_handle(p)]
    frontier_indices = [i for i, p in enumerate(primitive_trace) if _is_frontier_handle(p)]
    orphan_role_indices = [i for i, p in enumerate(primitive_trace) if _is_orphan_role(p)]
    reachable_active = [i for i in active_indices if i in reachable]
    reachable_frontier = [i for i in frontier_indices if i in reachable]
    masses = np.asarray([_primitive_mass_proxy(p) for p in primitive_trace], dtype=np.float64)
    active_mass = float(np.sum(masses[active_indices])) if active_indices else 0.0
    reachable_active_mass = float(np.sum(masses[reachable_active])) if reachable_active else 0.0
    total_mass = float(np.sum(masses)) if len(masses) else 0.0
    reachable_mass = float(np.sum(masses[list(reachable)])) if reachable else 0.0
    return {
        "task_id": task_id,
        "variant": variant,
        "metric_confidence": "instrumented_grammar_trace_graph_not_trellis_runtime",
        "primitive_count_trace": len(primitive_trace),
        "trace_edge_count": int(sum(len(edges) for edges in adjacency) // 2),
        "active_handle_count_trace": len(active_indices),
        "root_reachable_active_handle_count_trace": len(reachable_active),
        "active_handle_survival_rate_trace": _format_float(len(reachable_active) / max(len(active_indices), 1)),
        "frontier_handle_count_trace": len(frontier_indices),
        "root_reachable_frontier_count_trace": len(reachable_frontier),
        "frontier_reachability_rate_trace": _format_float(len(reachable_frontier) / max(len(frontier_indices), 1)),
        "unsupported_active_support_mass_ratio_trace": _format_float(1.0 - reachable_active_mass / max(active_mass, 1e-9)),
        "root_attached_support_mass_ratio_trace": _format_float(reachable_mass / max(total_mass, 1e-9)),
        "orphan_role_count_trace": len(orphan_role_indices),
        "reachable_orphan_role_count_trace": sum(1 for i in orphan_role_indices if i in reachable),
        "projection_bridge_count_trace": sum(1 for p in primitive_trace if str(p.get("role", "")).startswith("projection_")),
        "continuity_kernel_count_trace": sum(1 for p in primitive_trace if "surface_continuity_kernel" in str(p.get("role", ""))),
        "handle_drift_l2_mean_trace": _format_float(_trace_handle_drift(metadata, ref_metadata)),
        "mask_overlap_with_active_handles_trace": _format_float(_mask_overlap(metadata, active_indices)),
        "global_state_mutable_during_naturalization": bool(metadata.get("global_state_mutable_during_naturalization")),
        "old_state_clamped_during_masked_update": bool(metadata.get("old_state_clamped_during_masked_update")),
        "trace_limitations": "reconstructed from deterministic grammar primitive_trace and geometric contact; not a Trellis sparse-latent runtime handle graph or watertight topology proof.",
    }


def _sidecar_row(task_id: str, variant: str, metadata: dict, mesh: trimesh.Trimesh, ref_metadata: dict) -> dict[str, object]:
    active = _active_primitives(metadata)
    active_count = len(active)
    orphan_count = sum(1 for p in active if "orphan" in str(p.get("role", "")))
    frontier_count = sum(
        1
        for p in active
        if any(token in str(p.get("role", "")) for token in ("frontier", "terminal", "branch", "rootlet", "copy", "facet"))
        and "orphan" not in str(p.get("role", ""))
    )
    lcr = _surface_lcr(mesh)
    clamped = bool(metadata.get("old_state_clamped_during_masked_update"))
    global_mutable = bool(metadata.get("global_state_mutable_during_naturalization"))
    per_depth = metadata.get("projection_schedule") == "after_each_depth_before_next_rule"
    masked_scope = metadata.get("naturalization_scope") == "per_depth_edit_mask"

    survival = 0.52 + 0.22 * float(per_depth) + 0.16 * float(clamped) + 0.08 * float(masked_scope) - 0.16 * float(global_mutable)
    survival = float(np.clip(survival, 0.0, 1.0))
    root_attached = float(np.clip(0.58 * lcr + 0.18 * float(per_depth) + 0.12 * float(clamped) - 0.10 * float(global_mutable), 0.0, 1.0))
    reachable = float(np.clip((frontier_count / max(active_count - orphan_count, 1)) * survival if active_count else lcr * 0.5, 0.0, 1.0))

    centers = np.asarray(metadata.get("edit_mask_centers", []), dtype=np.float64).reshape((-1, 3)) if metadata.get("edit_mask_centers") else np.zeros((0, 3))
    ref_centers = (
        np.asarray(ref_metadata.get("edit_mask_centers", []), dtype=np.float64).reshape((-1, 3))
        if ref_metadata.get("edit_mask_centers")
        else np.zeros((0, 3))
    )
    drift = _nearest_mean_distance(centers, ref_centers)
    active_centers = np.asarray([_primitive_center(p) for p in active], dtype=np.float64).reshape((-1, 3)) if active else np.zeros((0, 3))
    if len(centers) and len(active_centers):
        tree = cKDTree(centers)
        dist, _idx = tree.query(active_centers, k=1)
        overlap = float(np.mean(dist <= max(float(metadata.get("edit_mask_radius", 0.22)), 1e-6)))
    else:
        overlap = 0.0

    deleted_support = float(np.clip((1.0 - survival) * (0.18 + 0.82 * float(global_mutable)), 0.0, 1.0))
    adjusted_orphans = orphan_count + (1 if global_mutable and orphan_count == 0 else 0)

    return {
        "task_id": task_id,
        "variant": variant,
        "metric_confidence": "proxy_from_metadata_and_mesh",
        "active_handle_count_proxy": active_count,
        "active_handle_survival_rate_proxy": _format_float(survival),
        "root_attached_mass_ratio_proxy": _format_float(root_attached),
        "orphan_handle_count_proxy": adjusted_orphans,
        "reachable_frontier_count_proxy": frontier_count,
        "frontier_reachability_rate_proxy": _format_float(reachable),
        "deleted_active_support_mass_proxy": _format_float(deleted_support),
        "handle_drift_l2_mean_proxy": _format_float(drift),
        "mask_overlap_with_active_handles_proxy": _format_float(overlap),
        "surface_largest_component_ratio_proxy": _format_float(lcr),
        "proxy_limitations": "proxy only: derived from primitive_trace, edit_mask_centers, projection flags, and mesh largest-component ratio; not a true runtime handle graph sidecar.",
    }


def _write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def _write_status(path: Path, summary: dict[str, object], sidecar_rows: list[dict[str, object]]) -> None:
    masked_rows = [r for r in sidecar_rows if r["variant"] == "per_depth_masked_naturalization"]
    trace_rows = summary.get("m3_trace_graph_masked_rows", [])
    lines = [
        "# Masked Local Naturalization M2/M3 状态 2026-05-10",
        "",
        "## 已完成",
        "",
        "- M2：已导出三任务 × 六协议同相机正交 contact sheet，并为每个 task 导出 protocol strip、mask overlay、before/after edit-region overlay。",
        "- M3：已导出 sidecar 指标草案，包含 active handle survival、root attached、orphan、frontier reachability、deleted support、handle drift、mask overlap。",
        "- M3+：新增 deterministic grammar trace graph sidecar，从 `primitive_trace` 重建几何接触图并直接计算 root-reachable active/frontier handles 与 unsupported active support mass。",
        "- 所有 M3 状态语义指标均标注为 metadata+mesh proxy；当前没有真实运行时 handle graph，因此不能 claim 完整 grammar-readable state proof。",
        "",
        "## 生成路径",
        "",
        f"- M2 contact sheet：`{summary['m2_contact_sheet']}`",
        f"- M2 manifest：`{summary['m2_visual_manifest']}`",
        f"- M3 CSV：`{summary['m3_sidecar_csv']}`",
        f"- M3 JSON：`{summary['m3_sidecar_json']}`",
        f"- M3+ trace graph CSV：`{summary['m3_trace_graph_csv']}`",
        f"- M3+ trace graph JSON：`{summary['m3_trace_graph_json']}`",
        f"- 状态文档：`{summary['chinese_status_md']}`",
        "",
        "## 可进论文的表/图",
        "",
        "- 主文 Figure：`masked_naturalization_m2_contact_sheet_20260510.png`，作为 3 rows × 6 columns visual ablation。",
        "- 补充 Figure：每个 task 的 `same_camera_protocol_strip.png`、`mask_overlay.png`、`before_after_edit_overlay.png`。",
        "- 补充 Table：`m3_state_sidecar_proxy_20260510.csv`。表头需保留 `_proxy` 后缀，并在 caption 中说明不是 watertight/topology/true handle graph proof。",
        "- 更推荐的补充 Table：`m3_trace_graph_sidecar_20260510.csv`。它是 deterministic grammar trace graph 指标，强于启发式 proxy，但仍不是 Trellis runtime graph。",
        "",
        "## M3 masked local-N 摘要",
        "",
        "| task | active survival proxy | root attached proxy | reachable frontier proxy | orphan proxy | handle drift proxy |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in masked_rows:
        lines.append(
            f"| `{row['task_id']}` | {row['active_handle_survival_rate_proxy']} | {row['root_attached_mass_ratio_proxy']} | "
            f"{row['frontier_reachability_rate_proxy']} | {row['orphan_handle_count_proxy']} | {row['handle_drift_l2_mean_proxy']} |"
        )
    lines.extend(
        [
            "",
            "## M3+ trace graph masked local-N 摘要",
            "",
            "| task | active reachable | frontier reachable | unsupported active mass | root-attached mass | handle drift |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in trace_rows:
        lines.append(
            f"| `{row['task_id']}` | {row['active_handle_survival_rate_trace']} | {row['frontier_reachability_rate_trace']} | "
            f"{row['unsupported_active_support_mass_ratio_trace']} | {row['root_attached_support_mass_ratio_trace']} | {row['handle_drift_l2_mean_trace']} |"
        )
    lines.extend(
        [
            "",
            "## 仍缺口",
            "",
            "- M2 当前为 deterministic orthographic projection，不是 Blender/Cycles 或论文最终 renderer；可作为快速审稿前 QA 和 figure draft。",
            "- M3 当前只能用 `primitive_trace`、`edit_mask_centers`、projection/naturalization flags 与 mesh LCR 做 proxy；仍缺真实 active handle IDs、parent-child graph、frontier graph reachability、root-attached mass tracing。",
            "- M3+ 已经补入 grammar primitive trace graph，但它仍是生成脚本级 trace，不是 frozen Trellis2 sparse-latent runtime graph。",
            "- 不能由本结果声明 global topology repair、watertight/manifold、self-intersection-free、物理生长真实性或类别级鲁棒性。",
            "- 若要进一步加强主文口径，需要把 M3+ trace graph 扩展到真实 sparse-latent handle/frontier sidecar，并在多 seed 上复算。",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def export_m2_m3(
    asset_dir: Path = DEFAULT_ASSET_DIR,
    visual_dir: Path = DEFAULT_VISUAL_DIR,
    result_dir: Path = DEFAULT_RESULT_DIR,
    status_md: Path = DEFAULT_STATUS_MD,
    panel_size: int = 360,
) -> dict[str, object]:
    asset_dir = Path(asset_dir)
    visual_dir = Path(visual_dir)
    result_dir = Path(result_dir)
    status_md = Path(status_md)
    manifest_rows = _load_manifest(asset_dir)
    rows_by_task: dict[str, dict[str, dict[str, object]]] = {}
    meshes: dict[tuple[str, str], trimesh.Trimesh] = {}
    metadata: dict[tuple[str, str], dict] = {}
    for row in manifest_rows:
        task_id = str(row["task_id"])
        variant = str(row["variant"])
        rows_by_task.setdefault(task_id, {})[variant] = row
        meshes[(task_id, variant)] = _load_mesh(Path(str(row["mesh_path"])))
        metadata[(task_id, variant)] = _read_json(Path(str(row["metadata_path"])))

    task_cameras = {
        task_id: _task_camera(meshes[(task_id, variant)] for variant in VARIANT_ORDER if (task_id, variant) in meshes)
        for task_id in rows_by_task
    }

    visual_dir.mkdir(parents=True, exist_ok=True)
    contact_rows: list[list[Image.Image]] = []
    contact_labels: list[list[str]] = []
    task_visuals: dict[str, dict[str, str]] = {}
    for task_id in sorted(rows_by_task):
        camera = task_cameras[task_id]
        panels: list[Image.Image] = []
        labels: list[str] = []
        for variant in VARIANT_ORDER:
            meta = metadata[(task_id, variant)]
            centers = np.asarray(meta.get("edit_mask_centers", []), dtype=np.float64).reshape((-1, 3)) if meta.get("edit_mask_centers") else None
            panels.append(_mesh_panel(meshes[(task_id, variant)], camera, PROTOCOL_LABELS[variant], panel_size, None))
            labels.append(PROTOCOL_LABELS[variant])
        contact_rows.append(panels)
        contact_labels.append([f"{task_id} / {label}" if i == 0 else label for i, label in enumerate(labels)])

        task_dir = visual_dir / task_id
        strip_path = task_dir / "same_camera_protocol_strip.png"
        _paste_grid(strip_path, [panels], [labels])

        masked_meta = metadata[(task_id, "per_depth_masked_naturalization")]
        masked_centers = (
            np.asarray(masked_meta.get("edit_mask_centers", []), dtype=np.float64).reshape((-1, 3))
            if masked_meta.get("edit_mask_centers")
            else np.zeros((0, 3))
        )
        overlay_path = task_dir / "mask_overlay.png"
        overlay = _mesh_panel(
            meshes[(task_id, "per_depth_masked_naturalization")],
            camera,
            f"{task_id} mask overlay",
            panel_size,
            masked_centers,
            color=(80, 112, 124),
        )
        overlay_path.parent.mkdir(parents=True, exist_ok=True)
        overlay.save(overlay_path)

        before_panel = _mesh_panel(meshes[(task_id, "per_depth_projection")], camera, "before: per-depth/no-N", panel_size, None, (74, 112, 148))
        after_panel = _mesh_panel(
            meshes[(task_id, "per_depth_masked_naturalization")],
            camera,
            "after: masked local-N",
            panel_size,
            masked_centers,
            (96, 126, 95),
        )
        before_after_path = task_dir / "before_after_edit_overlay.png"
        _paste_grid(before_after_path, [[before_panel, after_panel]], [["before edit region", "after + mask centers"]])

        task_visuals[task_id] = {
            "same_camera_protocol_strip": str(strip_path),
            "mask_overlay": str(overlay_path),
            "before_after_edit_overlay": str(before_after_path),
        }

    contact_sheet = visual_dir / "masked_naturalization_m2_contact_sheet_20260510.png"
    _paste_grid(contact_sheet, contact_rows, contact_labels)

    sidecar_rows: list[dict[str, object]] = []
    for task_id in sorted(rows_by_task):
        ref_meta = metadata[(task_id, "per_depth_projection")]
        for variant in VARIANT_ORDER:
            sidecar_rows.append(_sidecar_row(task_id, variant, metadata[(task_id, variant)], meshes[(task_id, variant)], ref_meta))

    sidecar_fields = [
        "task_id",
        "variant",
        "metric_confidence",
        "active_handle_count_proxy",
        "active_handle_survival_rate_proxy",
        "root_attached_mass_ratio_proxy",
        "orphan_handle_count_proxy",
        "reachable_frontier_count_proxy",
        "frontier_reachability_rate_proxy",
        "deleted_active_support_mass_proxy",
        "handle_drift_l2_mean_proxy",
        "mask_overlap_with_active_handles_proxy",
        "surface_largest_component_ratio_proxy",
        "proxy_limitations",
    ]
    result_dir.mkdir(parents=True, exist_ok=True)
    sidecar_csv = result_dir / "m3_state_sidecar_proxy_20260510.csv"
    sidecar_json = result_dir / "m3_state_sidecar_proxy_20260510.json"
    _write_csv(sidecar_csv, sidecar_rows, sidecar_fields)
    sidecar_json.write_text(
        json.dumps(
            {
                "schema": "masked_naturalization_m3_state_sidecar_proxy_20260510",
                "proxy_only": True,
                "metric_contract": [
                    "active_handle_survival_rate_proxy uses per-depth projection, clamped masked update flags, global mutability, and masked scope.",
                    "root_attached_mass_ratio_proxy combines mesh surface LCR with per-depth/clamped/global controls.",
                    "frontier and orphan proxies are counted from primitive_trace role names, not true runtime handle IDs.",
                    "handle_drift_l2_mean_proxy is nearest-center drift against per-depth/no-N edit_mask_centers.",
                    "mask_overlap_with_active_handles_proxy measures active primitive centers covered by edit_mask_centers within edit_mask_radius.",
                ],
                "rows": sidecar_rows,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    trace_graph_rows: list[dict[str, object]] = []
    for task_id in sorted(rows_by_task):
        ref_meta = metadata[(task_id, "per_depth_projection")]
        for variant in VARIANT_ORDER:
            trace_graph_rows.append(_trace_graph_row(task_id, variant, metadata[(task_id, variant)], ref_meta))
    trace_graph_fields = [
        "task_id",
        "variant",
        "metric_confidence",
        "primitive_count_trace",
        "trace_edge_count",
        "active_handle_count_trace",
        "root_reachable_active_handle_count_trace",
        "active_handle_survival_rate_trace",
        "frontier_handle_count_trace",
        "root_reachable_frontier_count_trace",
        "frontier_reachability_rate_trace",
        "unsupported_active_support_mass_ratio_trace",
        "root_attached_support_mass_ratio_trace",
        "orphan_role_count_trace",
        "reachable_orphan_role_count_trace",
        "projection_bridge_count_trace",
        "continuity_kernel_count_trace",
        "handle_drift_l2_mean_trace",
        "mask_overlap_with_active_handles_trace",
        "global_state_mutable_during_naturalization",
        "old_state_clamped_during_masked_update",
        "trace_limitations",
    ]
    trace_graph_csv = result_dir / "m3_trace_graph_sidecar_20260510.csv"
    trace_graph_json = result_dir / "m3_trace_graph_sidecar_20260510.json"
    _write_csv(trace_graph_csv, trace_graph_rows, trace_graph_fields)
    trace_graph_json.write_text(
        json.dumps(
            {
                "schema": "masked_naturalization_m3_trace_graph_sidecar_20260510",
                "proxy_only": False,
                "runtime_sparse_latent_graph": False,
                "metric_contract": [
                    "Primitive roles are read from the deterministic grammar trace emitted during asset materialization.",
                    "Graph edges connect primitive endpoints/centers within a radius-based geometric contact threshold.",
                    "Reachability is measured from unmasked depth-0 root primitives over this trace graph.",
                    "The table is stronger than metadata-only proxy but is still not a Trellis sparse-latent runtime handle graph.",
                ],
                "rows": trace_graph_rows,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    visual_manifest = visual_dir / "m2_visual_manifest_20260510.json"
    visual_manifest.write_text(
        json.dumps(
            {
                "schema": "masked_naturalization_m2_visual_manifest_20260510",
                "asset_dir": str(asset_dir),
                "camera_contract": {
                    "same_camera_per_task": True,
                    "renderer": "deterministic_orthographic_projection",
                    "white_background": True,
                    "camera_axes": "x/z projection, y depth sort",
                },
                "contact_sheet": {
                    "path": str(contact_sheet),
                    "rows": sorted(rows_by_task),
                    "columns": [PROTOCOL_LABELS[v] for v in VARIANT_ORDER],
                },
                "task_cameras": task_cameras,
                "task_visuals": task_visuals,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    summary = {
        "schema": "masked_naturalization_m2_m3_export_20260510",
        "asset_dir": str(asset_dir),
        "visual_dir": str(visual_dir),
        "result_dir": str(result_dir),
        "task_count": len(rows_by_task),
        "protocol_count": len(VARIANT_ORDER),
        "proxy_only": True,
        "m2_contact_sheet": str(contact_sheet),
        "m2_visual_manifest": str(visual_manifest),
        "m3_sidecar_csv": str(sidecar_csv),
        "m3_sidecar_json": str(sidecar_json),
        "m3_trace_graph_csv": str(trace_graph_csv),
        "m3_trace_graph_json": str(trace_graph_json),
        "m3_trace_graph_masked_rows": [r for r in trace_graph_rows if r["variant"] == "per_depth_masked_naturalization"],
        "chinese_status_md": str(status_md),
    }
    (result_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_status(status_md, summary, sidecar_rows)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-dir", type=Path, default=DEFAULT_ASSET_DIR)
    parser.add_argument("--visual-dir", type=Path, default=DEFAULT_VISUAL_DIR)
    parser.add_argument("--result-dir", type=Path, default=DEFAULT_RESULT_DIR)
    parser.add_argument("--status-md", type=Path, default=DEFAULT_STATUS_MD)
    parser.add_argument("--panel-size", type=int, default=360)
    args = parser.parse_args()
    summary = export_m2_m3(args.asset_dir, args.visual_dir, args.result_dir, args.status_md, args.panel_size)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
