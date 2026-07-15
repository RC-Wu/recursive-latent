#!/usr/bin/env python3
"""Seam-band QA and junction-collar proposal for masked naturalization.

This script is intentionally claim-bounded.  It does not say Trellis2 already
solves the visible seam problem.  It measures the seam band around recursive
junctions, then exports a conservative grammar-compatible junction-collar mesh
proposal that can be used for render QA or as the next remote generation input.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial import cKDTree


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_ASSET_DIR = PROJECT_ROOT / "results" / "masked_naturalization_ablation_20260510"
DEFAULT_OUT_DIR = PROJECT_ROOT / "results" / "masked_naturalization_seam_optimization_20260510"
DEFAULT_VISUAL_DIR = PROJECT_ROOT / "visuals" / "masked_naturalization_seam_optimization_20260510"
DEFAULT_STATUS_MD = PROJECT_ROOT / "docs" / "evaluation" / "masked_naturalization_seam_optimization_status_zh_20260510.md"

ASSET_SCRIPT = PROJECT_ROOT / "assets" / "masked_naturalization_ablation_assets_20260510.py"
SOURCE_VARIANT = "per_depth_masked_naturalization"


def _load_asset_module():
    spec = importlib.util.spec_from_file_location("masked_naturalization_ablation_assets_20260510", ASSET_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "task_id",
        "source_variant",
        "optimized_variant",
        "junction_collar_count",
        "source_vertices",
        "source_faces",
        "optimized_vertices",
        "optimized_faces",
        "source_component_count",
        "source_lcr",
        "optimized_component_count",
        "optimized_lcr",
        "source_seam_band_face_fraction",
        "optimized_seam_band_face_fraction",
        "source_seam_band_normal_variation_deg",
        "optimized_seam_band_normal_variation_deg",
        "source_seam_boundary_jump_deg",
        "optimized_seam_boundary_jump_deg",
        "source_seam_axis_alignment",
        "optimized_seam_axis_alignment",
        "seam_boundary_jump_delta_deg",
        "seam_band_normal_delta_deg",
        "lcr_delta",
        "claim_scope",
        "source_mesh",
        "optimized_mesh",
        "optimized_metadata",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def _as_array(value: Any) -> np.ndarray:
    return np.asarray(value, dtype=np.float64)


def _deserialize_primitive(primitive: dict[str, Any]) -> dict[str, Any]:
    out = dict(primitive)
    for key in ("a", "b", "center", "radii"):
        if key in out:
            out[key] = _as_array(out[key])
    return out


def _primitive_center(primitive: dict[str, Any]) -> np.ndarray:
    if primitive.get("kind") == "segment":
        return (_as_array(primitive["a"]) + _as_array(primitive["b"])) * 0.5
    return _as_array(primitive.get("center", [0.0, 0.0, 0.0]))


def _primitive_radius(primitive: dict[str, Any]) -> float:
    if primitive.get("kind") == "ellipsoid":
        return float(np.max(_as_array(primitive.get("radii", [0.0, 0.0, 0.0]))))
    return float(primitive.get("radius", 0.0))


def _primitive_endpoints(primitive: dict[str, Any]) -> list[np.ndarray]:
    if primitive.get("kind") == "segment":
        return [_as_array(primitive["a"]), _as_array(primitive["b"])]
    return [_primitive_center(primitive)]


def _closest_point_on_primitive(point: np.ndarray, primitive: dict[str, Any]) -> tuple[float, np.ndarray, float]:
    kind = primitive.get("kind")
    if kind == "segment":
        a = _as_array(primitive["a"])
        b = _as_array(primitive["b"])
        ab = b - a
        denom = max(float(np.dot(ab, ab)), 1e-12)
        t = float(np.clip(np.dot(point - a, ab) / denom, 0.0, 1.0))
        closest = a + ab * t
    else:
        closest = _primitive_center(primitive)
    radius = max(_primitive_radius(primitive), 1e-6)
    return float(np.linalg.norm(point - closest)), closest, radius


def _nearest_previous_primitive(
    point: np.ndarray,
    primitive: dict[str, Any],
    primitives: list[dict[str, Any]],
) -> tuple[float, np.ndarray, float, dict[str, Any]] | None:
    depth = int(primitive.get("depth", 0))
    best: tuple[float, np.ndarray, float, dict[str, Any]] | None = None
    for candidate in primitives:
        if candidate is primitive:
            continue
        if int(candidate.get("depth", 0)) >= depth:
            continue
        dist, closest, radius = _closest_point_on_primitive(point, candidate)
        if best is None or dist < best[0]:
            best = (dist, closest, radius, candidate)
    return best


def _sphere(center: np.ndarray, radius: float, depth: int, role: str) -> dict[str, Any]:
    return {
        "kind": "sphere",
        "center": np.asarray(center, dtype=np.float64),
        "radius": float(radius),
        "depth": int(depth),
        "role": role,
        "masked": True,
    }


def _junction_collars(primitives: list[dict[str, Any]], mask_radius: float) -> list[dict[str, Any]]:
    collars: list[dict[str, Any]] = []
    for primitive in primitives:
        if not bool(primitive.get("masked")) or int(primitive.get("depth", 0)) <= 0:
            continue
        if primitive.get("kind") != "segment":
            continue
        role = str(primitive.get("role", ""))
        if "orphan" in role and "projection_bridge" not in role:
            continue
        a = _as_array(primitive["a"])
        b = _as_array(primitive["b"])
        axis = b - a
        axis_len = max(float(np.linalg.norm(axis)), 1e-8)
        axis_unit = axis / axis_len
        seg_radius = max(float(primitive.get("radius", 0.0)), 1e-6)
        for endpoint, sign in ((a, 1.0), (b, -1.0)):
            nearest = _nearest_previous_primitive(endpoint, primitive, primitives)
            if nearest is None:
                continue
            dist, closest, old_radius, _candidate = nearest
            if dist > max(mask_radius * 1.85, seg_radius * 5.0):
                continue
            collar_radius = max(seg_radius * 1.75, min(old_radius * 0.72, mask_radius * 0.42))
            center = endpoint * 0.72 + closest * 0.28
            collars.append(
                _sphere(center, collar_radius, int(primitive.get("depth", 0)), "seam_feather_junction_collar")
            )
            inner = endpoint + axis_unit * sign * min(axis_len * 0.16, max(seg_radius * 2.8, mask_radius * 0.20))
            collars.append(
                _sphere(inner, collar_radius * 0.72, int(primitive.get("depth", 0)), "seam_feather_transition_lobe")
            )
    # Deduplicate near-identical collars; several primitives share exact nodes.
    unique: list[dict[str, Any]] = []
    centers: list[np.ndarray] = []
    min_sep = max(mask_radius * 0.12, 1e-4)
    for collar in collars:
        center = _as_array(collar["center"])
        if any(float(np.linalg.norm(center - old)) < min_sep for old in centers):
            continue
        unique.append(collar)
        centers.append(center)
    return unique


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


def _component_stats(mesh: trimesh.Trimesh) -> tuple[int, float]:
    if len(mesh.vertices) == 0:
        return 0, 0.0
    comps = mesh.split(only_watertight=False)
    if not comps:
        return 0, 0.0
    largest = max(len(comp.vertices) for comp in comps)
    return int(len(comps)), float(largest / max(len(mesh.vertices), 1))


def _face_band(mesh: trimesh.Trimesh, centers: np.ndarray, radius: float) -> np.ndarray:
    if len(mesh.faces) == 0 or len(centers) == 0:
        return np.zeros((len(mesh.faces),), dtype=bool)
    face_centers = np.asarray(mesh.triangles_center, dtype=np.float64)
    tree = cKDTree(centers)
    dist, _idx = tree.query(face_centers, k=1)
    band = dist <= max(float(radius), 1e-6)
    if int(band.sum()) < 4:
        q = min(max(12, len(face_centers) // 20), len(face_centers))
        nearest = np.argsort(dist)[:q]
        band = np.zeros((len(face_centers),), dtype=bool)
        band[nearest] = True
    return band


def _normal_angle_stats(mesh: trimesh.Trimesh, band: np.ndarray) -> tuple[float, float]:
    if len(mesh.faces) == 0:
        return 0.0, 0.0
    adjacency = np.asarray(mesh.face_adjacency, dtype=np.int64)
    if len(adjacency) == 0:
        return 0.0, 0.0
    normals = np.asarray(mesh.face_normals, dtype=np.float64)
    dots = np.sum(normals[adjacency[:, 0]] * normals[adjacency[:, 1]], axis=1)
    angles = np.degrees(np.arccos(np.clip(dots, -1.0, 1.0)))
    band_pair = band[adjacency[:, 0]] & band[adjacency[:, 1]]
    boundary_pair = band[adjacency[:, 0]] ^ band[adjacency[:, 1]]
    band_mean = float(np.mean(angles[band_pair])) if int(band_pair.sum()) else 0.0
    boundary_mean = float(np.mean(angles[boundary_pair])) if int(boundary_pair.sum()) else band_mean
    return band_mean, boundary_mean


def _axis_alignment(mesh: trimesh.Trimesh, band: np.ndarray) -> float:
    if len(mesh.faces) == 0 or int(band.sum()) == 0:
        return 0.0
    normals = np.abs(np.asarray(mesh.face_normals, dtype=np.float64)[band])
    return float(np.mean(np.max(normals, axis=1))) if len(normals) else 0.0


def _seam_metrics(mesh: trimesh.Trimesh, seam_centers: np.ndarray, radius: float) -> dict[str, Any]:
    comps, lcr = _component_stats(mesh)
    band = _face_band(mesh, seam_centers, radius)
    band_normal, boundary_jump = _normal_angle_stats(mesh, band)
    return {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "component_count": comps,
        "lcr": lcr,
        "seam_band_face_fraction": float(np.mean(band)) if len(band) else 0.0,
        "seam_band_normal_variation_deg": band_normal,
        "seam_boundary_jump_deg": boundary_jump,
        "seam_axis_alignment": _axis_alignment(mesh, band),
    }


def _safe_font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _camera_for_meshes(meshes: Iterable[trimesh.Trimesh]) -> dict[str, Any]:
    points = [np.asarray(mesh.vertices, dtype=np.float64) for mesh in meshes if len(mesh.vertices)]
    if not points:
        return {"center": np.zeros(3), "scale": 1.0, "axes": (0, 2)}
    pts = np.vstack(points)
    vmin = pts.min(axis=0)
    vmax = pts.max(axis=0)
    center = (vmin + vmax) * 0.5
    scale = float(max((vmax - vmin)[[0, 2]].max(), 1e-6)) * 1.16
    return {"center": center, "scale": scale, "axes": (0, 2)}


def _project(points: np.ndarray, camera: dict[str, Any], size: int, margin: int) -> np.ndarray:
    center = np.asarray(camera["center"], dtype=np.float64)
    axes = tuple(camera["axes"])
    scale = max(float(camera["scale"]), 1e-6)
    xy = (points[:, axes] - center[list(axes)]) / scale
    px = margin + (xy[:, 0] + 0.5) * (size - 2 * margin)
    py = margin + (0.5 - xy[:, 1]) * (size - 2 * margin)
    return np.stack([px, py], axis=1)


def _mesh_panel(
    mesh: trimesh.Trimesh,
    camera: dict[str, Any],
    title: str,
    size: int,
    seam_centers: np.ndarray | None = None,
) -> Image.Image:
    image = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(image, "RGBA")
    if len(mesh.vertices) and len(mesh.faces):
        vertices = np.asarray(mesh.vertices, dtype=np.float64)
        faces = np.asarray(mesh.faces, dtype=np.int64)
        if len(faces) > 9500:
            faces = faces[np.linspace(0, len(faces) - 1, 9500).astype(np.int64)]
        proj = _project(vertices, camera, size, max(20, size // 13))
        tri = vertices[faces]
        normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        norms = np.maximum(np.linalg.norm(normals, axis=1), 1e-8)
        shade = np.clip(0.46 + 0.54 * np.abs(normals[:, 1]) / norms, 0.35, 1.0)
        order = np.argsort(tri.mean(axis=1)[:, 1])
        base = (94, 118, 105)
        for face_idx in order:
            pts = [tuple(x) for x in proj[faces[face_idx]]]
            color = tuple(int(channel * shade[face_idx]) for channel in base)
            draw.polygon(pts, fill=(*color, 238))
    if seam_centers is not None and len(seam_centers):
        projected = _project(seam_centers, camera, size, max(20, size // 13))
        radius = max(4, size // 60)
        for x, y in projected:
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=(204, 55, 45, 220), width=2)
    font = _safe_font(max(12, size // 28))
    draw.rectangle((0, 0, size, max(26, size // 9)), fill=(255, 255, 255, 220))
    draw.text((8, 6), title, font=font, fill=(24, 28, 30, 255))
    return image


def _write_contact_sheet(path: Path, rows: list[dict[str, Any]], panel_size: int = 320) -> None:
    if not rows:
        return
    gap = 10
    label_w = 210
    cols = 3
    width = label_w + cols * panel_size + cols * gap
    height = len(rows) * panel_size + (len(rows) - 1) * gap
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    title_font = _safe_font(18)
    small_font = _safe_font(13)
    for idx, row in enumerate(rows):
        y = idx * (panel_size + gap)
        source_mesh = _load_mesh(Path(row["source_mesh"]))
        optimized_mesh = _load_mesh(Path(row["optimized_mesh"]))
        seam_centers = np.asarray(row["_seam_centers"], dtype=np.float64).reshape((-1, 3))
        camera = _camera_for_meshes([source_mesh, optimized_mesh])
        draw.text((8, y + 18), str(row["task_id"]), font=title_font, fill=(20, 24, 26))
        draw.text((8, y + 48), "masked local-N", font=small_font, fill=(75, 80, 84))
        draw.text((8, y + 70), "seam collar proposal", font=small_font, fill=(75, 80, 84))
        x = label_w
        canvas.paste(_mesh_panel(source_mesh, camera, "source", panel_size), (x, y))
        x += panel_size + gap
        canvas.paste(_mesh_panel(optimized_mesh, camera, "junction collar", panel_size), (x, y))
        x += panel_size + gap
        canvas.paste(_mesh_panel(optimized_mesh, camera, "seam centers", panel_size, seam_centers=seam_centers), (x, y))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def _write_status(path: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Masked naturalization seam optimization status",
        "",
        "日期：2026-05-10",
        "",
        "## 本轮结论",
        "",
        "用户指出白底 zoom 中接缝仍明显是成立的：已有 masked local-N 证据主要覆盖 projection/trace/local surface proxy，尚未把 junction band 和最终材质/UV seam 作为一等目标。",
        "",
        "本轮新增一个 claim-bounded 的 seam-band QA 和 `junction collar` 方案：在 grammar trace 中对新旧递归状态交界处加入保守过渡壳/transition lobe，再重建 mesh，用来筛选下一轮远端 Trellis2 texture/PBR 输入。它是下一轮算法候选，不是把现有 Trellis textured GLB 追认为无接缝。",
        "",
        "## 输出",
        "",
        f"- summary: `{summary['summary_json']}`",
        f"- CSV: `{summary['metrics_csv']}`",
        f"- JSON: `{summary['metrics_json']}`",
        f"- contact sheet: `{summary['contact_sheet']}`",
        "",
        "## 指标表",
        "",
        "| task | collars | LCR before | LCR after | boundary jump delta | band normal delta |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {task} | {collars} | {l0:.6f} | {l1:.6f} | {dj:.3f} | {dn:.3f} |".format(
                task=row["task_id"],
                collars=int(row["junction_collar_count"]),
                l0=float(row["source_lcr"]),
                l1=float(row["optimized_lcr"]),
                dj=float(row["seam_boundary_jump_delta_deg"]),
                dn=float(row["seam_band_normal_delta_deg"]),
            )
        )
    lines.extend(
        [
            "",
            "## 论文口径",
            "",
            "- 可以写：接缝问题需要显式 junction-band 约束；我们用 seam-band metrics 作为下一轮筛选门槛。",
            "- 不能写：现有 masked local-N 已经在最终 PBR/UV textured GLB 中完全消除接缝，或证明 watertight/manifold。",
            "- 视觉图进入论文前仍需走 PPTX 排版再导出 PDF，并优先使用无 callout 原图做接缝 QA。",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_seam_qa(
    asset_dir: Path = DEFAULT_ASSET_DIR,
    out_dir: Path = DEFAULT_OUT_DIR,
    visual_dir: Path = DEFAULT_VISUAL_DIR,
    status_md: Path = DEFAULT_STATUS_MD,
) -> dict[str, Any]:
    asset_mod = _load_asset_module()
    task_by_id = {str(task["task_id"]): task for task in asset_mod.TASKS}
    manifest = _read_json(asset_dir / "manifest.json")
    rows: list[dict[str, Any]] = []
    visual_rows: list[dict[str, Any]] = []
    for item in manifest["rows"]:
        if item["variant"] != SOURCE_VARIANT:
            continue
        task_id = str(item["task_id"])
        task = task_by_id[task_id]
        metadata_path = Path(item["metadata_path"])
        if not metadata_path.is_absolute():
            metadata_path = PROJECT_ROOT / metadata_path
        metadata = _read_json(metadata_path)
        primitives = [_deserialize_primitive(p) for p in metadata.get("primitive_trace", [])]
        mask_radius = float(metadata.get("edit_mask_radius", task.get("mask_radius", 0.22)))
        collars = _junction_collars(primitives, mask_radius)
        optimized_primitives = primitives + collars
        optimized_mesh = asset_mod._mesh_from_primitives(
            optimized_primitives,
            task,
            resolution=int(metadata.get("resolution", 56)),
            naturalization_mode="per_depth_edit_mask",
            naturalization_strength=1.0,
        )
        case_dir = out_dir / "tasks" / task_id / "per_depth_masked_junction_collar"
        case_dir.mkdir(parents=True, exist_ok=True)
        optimized_mesh_path = case_dir / "mesh.obj"
        optimized_mesh.export(optimized_mesh_path)
        optimized_metadata_path = case_dir / "metadata.json"
        optimized_metadata = dict(metadata)
        optimized_metadata.update(
            {
                "schema": "masked_naturalization_junction_collar_metadata_20260510",
                "source_variant": SOURCE_VARIANT,
                "variant": "per_depth_masked_junction_collar",
                "mesh_path": str(optimized_mesh_path),
                "junction_collar_count": len(collars),
                "junction_collar_primitives": [asset_mod._serialize_primitive(p) for p in collars],
                "claim_scope": "seam-band grammar proposal and render QA; not Trellis runtime topology proof",
            }
        )
        optimized_metadata["primitive_trace"] = [asset_mod._serialize_primitive(p) for p in optimized_primitives]
        optimized_metadata_path.write_text(json.dumps(optimized_metadata, indent=2, ensure_ascii=False), encoding="utf-8")

        source_mesh_path = Path(item["mesh_path"])
        if not source_mesh_path.is_absolute():
            source_mesh_path = PROJECT_ROOT / source_mesh_path
        source_mesh = _load_mesh(source_mesh_path)
        seam_centers = np.asarray(
            [p["center"] for p in collars if p.get("kind") == "sphere"]
            or metadata.get("edit_mask_centers", []),
            dtype=np.float64,
        ).reshape((-1, 3))
        source_metrics = _seam_metrics(source_mesh, seam_centers, mask_radius * 1.18)
        opt_metrics = _seam_metrics(optimized_mesh, seam_centers, mask_radius * 1.18)
        row = {
            "task_id": task_id,
            "source_variant": SOURCE_VARIANT,
            "optimized_variant": "per_depth_masked_junction_collar",
            "junction_collar_count": int(len(collars)),
            "source_vertices": source_metrics["vertices"],
            "source_faces": source_metrics["faces"],
            "optimized_vertices": opt_metrics["vertices"],
            "optimized_faces": opt_metrics["faces"],
            "source_component_count": source_metrics["component_count"],
            "source_lcr": source_metrics["lcr"],
            "optimized_component_count": opt_metrics["component_count"],
            "optimized_lcr": opt_metrics["lcr"],
            "source_seam_band_face_fraction": source_metrics["seam_band_face_fraction"],
            "optimized_seam_band_face_fraction": opt_metrics["seam_band_face_fraction"],
            "source_seam_band_normal_variation_deg": source_metrics["seam_band_normal_variation_deg"],
            "optimized_seam_band_normal_variation_deg": opt_metrics["seam_band_normal_variation_deg"],
            "source_seam_boundary_jump_deg": source_metrics["seam_boundary_jump_deg"],
            "optimized_seam_boundary_jump_deg": opt_metrics["seam_boundary_jump_deg"],
            "source_seam_axis_alignment": source_metrics["seam_axis_alignment"],
            "optimized_seam_axis_alignment": opt_metrics["seam_axis_alignment"],
            "seam_boundary_jump_delta_deg": float(source_metrics["seam_boundary_jump_deg"] - opt_metrics["seam_boundary_jump_deg"]),
            "seam_band_normal_delta_deg": float(source_metrics["seam_band_normal_variation_deg"] - opt_metrics["seam_band_normal_variation_deg"]),
            "lcr_delta": float(opt_metrics["lcr"] - source_metrics["lcr"]),
            "claim_scope": "seam-band diagnostic and junction-collar proposal; not watertight topology or final PBR proof",
            "source_mesh": str(source_mesh_path),
            "optimized_mesh": str(optimized_mesh_path),
            "optimized_metadata": str(optimized_metadata_path),
            "_seam_centers": seam_centers.tolist(),
        }
        rows.append(row)
        visual_rows.append(row)

    metrics_csv = out_dir / "masked_naturalization_seam_band_metrics_20260510.csv"
    metrics_json = out_dir / "masked_naturalization_seam_band_metrics_20260510.json"
    summary_json = out_dir / "summary.json"
    contact_sheet = visual_dir / "masked_naturalization_seam_optimization_contact_sheet_20260510.png"
    _write_csv(metrics_csv, rows)
    metrics_json.write_text(json.dumps([{k: v for k, v in row.items() if not k.startswith("_")} for row in rows], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_contact_sheet(contact_sheet, visual_rows)
    summary = {
        "schema": "masked_naturalization_seam_band_qa_20260510",
        "asset_dir": str(asset_dir),
        "out_dir": str(out_dir),
        "visual_dir": str(visual_dir),
        "metrics_csv": str(metrics_csv),
        "metrics_json": str(metrics_json),
        "contact_sheet": str(contact_sheet),
        "status_md": str(status_md),
        "task_count": len(rows),
        "claim_scope": "junction-band QA/proposal, not Trellis runtime topology proof",
    }
    summary["summary_json"] = str(summary_json)
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_status(status_md, summary, rows)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-dir", type=Path, default=DEFAULT_ASSET_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--visual-dir", type=Path, default=DEFAULT_VISUAL_DIR)
    parser.add_argument("--status-md", type=Path, default=DEFAULT_STATUS_MD)
    args = parser.parse_args()
    summary = build_seam_qa(args.asset_dir, args.out_dir, args.visual_dir, args.status_md)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
