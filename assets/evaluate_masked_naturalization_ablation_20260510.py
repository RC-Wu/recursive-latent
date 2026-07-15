#!/usr/bin/env python3
"""Evaluate local masked naturalization ablation assets for PS-RSLG."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
import trimesh
from scipy import ndimage
from scipy.spatial import cKDTree


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_ASSET_DIR = PROJECT_ROOT / "results" / "masked_naturalization_ablation_20260510"
DEFAULT_OUT = DEFAULT_ASSET_DIR / "evaluation"

VARIANT_ORDER = [
    "raw_grammar_proposal",
    "final_only_projection_repair",
    "per_depth_projection",
    "per_depth_weak_naturalization",
    "per_depth_global_naturalization",
    "per_depth_masked_naturalization",
]

PAPER_TABLE_PATH = "paper_table_masked_naturalization_ablation_20260510"
PROTOCOL_SUMMARY_PATH = "protocol_summary_masked_naturalization_ablation_20260510"
MASKED_LOCAL_ADVANTAGE_PATH = "masked_local_advantage_20260510"

PROTOCOL_LABELS = {
    "raw_grammar_proposal": "rule-only",
    "final_only_projection_repair": "final-only",
    "per_depth_projection": "per-depth/no-N",
    "per_depth_weak_naturalization": "per-depth/weak",
    "per_depth_global_naturalization": "per-depth/global-N",
    "per_depth_masked_naturalization": "per-depth/masked local-N",
}


class UnionFind:
    def __init__(self, n: int):
        self.parent = np.arange(n, dtype=np.int64)
        self.size = np.ones(n, dtype=np.int64)

    def find(self, x: int) -> int:
        while int(self.parent[x]) != x:
            self.parent[x] = self.parent[int(self.parent[x])]
            x = int(self.parent[x])
        return int(x)

    def union(self, a: int, b: int) -> None:
        ra = self.find(int(a))
        rb = self.find(int(b))
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]


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


def _surface_component_stats(mesh: trimesh.Trimesh) -> dict[str, object]:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(vertices) == 0:
        return {
            "surface_component_count": 0,
            "surface_largest_component_vertices": 0,
            "surface_largest_component_ratio": 0.0,
            "surface_small_component_count_lt100": 0,
        }
    if len(faces) == 0:
        return {
            "surface_component_count": int(len(vertices)),
            "surface_largest_component_vertices": 1,
            "surface_largest_component_ratio": float(1.0 / max(len(vertices), 1)),
            "surface_small_component_count_lt100": int(len(vertices)),
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
        "surface_component_count": int(len(counts)),
        "surface_largest_component_vertices": largest,
        "surface_largest_component_ratio": float(largest / max(len(vertices), 1)),
        "surface_small_component_count_lt100": int(np.sum(counts < 100)),
    }


def _face_mask_from_centers(mesh: trimesh.Trimesh, metadata: dict) -> np.ndarray | None:
    if len(mesh.faces) == 0:
        return None
    centers = np.asarray(metadata.get("edit_mask_centers", []), dtype=np.float64)
    if centers.size == 0:
        return None
    centers = centers.reshape((-1, 3))
    face_centers = np.asarray(mesh.triangles_center, dtype=np.float64)
    if len(face_centers) == 0:
        return None
    tree = cKDTree(centers)
    dist, _idx = tree.query(face_centers, k=1)
    radius = float(metadata.get("edit_mask_radius", 0.22))
    mask = dist <= max(radius, 1e-6)
    if int(mask.sum()) < 4:
        return None
    return mask


def _normal_variation(mesh: trimesh.Trimesh, face_mask: np.ndarray | None = None) -> float:
    if len(mesh.faces) == 0:
        return 0.0
    adjacency = np.asarray(mesh.face_adjacency, dtype=np.int64)
    if len(adjacency) == 0:
        return 0.0
    if face_mask is not None:
        keep = face_mask[adjacency[:, 0]] & face_mask[adjacency[:, 1]]
        adjacency = adjacency[keep]
    if len(adjacency) == 0:
        return 0.0
    normals = np.asarray(mesh.face_normals, dtype=np.float64)
    dots = np.sum(normals[adjacency[:, 0]] * normals[adjacency[:, 1]], axis=1)
    dots = np.clip(dots, -1.0, 1.0)
    return float(np.degrees(np.arccos(dots)).mean())


def _triangle_quality_stats(mesh: trimesh.Trimesh) -> dict[str, float]:
    if len(mesh.faces) == 0:
        return {
            "mean_triangle_aspect_ratio": 0.0,
            "degenerate_face_fraction": 1.0,
            "mesh_quality_score": 0.0,
        }
    triangles = np.asarray(mesh.triangles, dtype=np.float64)
    edge_lengths = np.stack(
        [
            np.linalg.norm(triangles[:, 1] - triangles[:, 0], axis=1),
            np.linalg.norm(triangles[:, 2] - triangles[:, 1], axis=1),
            np.linalg.norm(triangles[:, 0] - triangles[:, 2], axis=1),
        ],
        axis=1,
    )
    shortest = np.maximum(edge_lengths.min(axis=1), 1e-12)
    longest = edge_lengths.max(axis=1)
    aspect = longest / shortest
    areas = np.asarray(mesh.area_faces, dtype=np.float64)
    positive = areas[areas > 1e-12]
    if len(positive):
        area_floor = max(float(np.median(positive)) * 1e-4, 1e-12)
        degenerate_fraction = float(np.mean(areas <= area_floor))
    else:
        degenerate_fraction = 1.0
    mean_aspect = float(np.mean(np.clip(aspect, 1.0, 20.0))) if len(aspect) else 20.0
    aspect_score = _clamp(1.0 - (mean_aspect - 1.0) / 9.0)
    quality_score = _clamp(0.72 * aspect_score + 0.28 * (1.0 - degenerate_fraction))
    return {
        "mean_triangle_aspect_ratio": mean_aspect,
        "degenerate_face_fraction": degenerate_fraction,
        "mesh_quality_score": quality_score,
    }


def _axis_blockiness(mesh: trimesh.Trimesh) -> dict[str, float]:
    if len(mesh.faces) == 0:
        return {
            "axis_aligned_normal_fraction": 1.0,
            "connectivity_blockiness_index": 1.0,
            "blockiness_score": 0.0,
        }
    normals = np.abs(np.asarray(mesh.face_normals, dtype=np.float64))
    if len(normals) == 0:
        return {
            "axis_aligned_normal_fraction": 1.0,
            "connectivity_blockiness_index": 1.0,
            "blockiness_score": 0.0,
        }
    axis_alignment = float(np.mean(np.max(normals, axis=1)))
    isotropic_floor = float(1.0 / math.sqrt(3.0))
    axis_index = _clamp((axis_alignment - isotropic_floor) / max(1.0 - isotropic_floor, 1e-9))
    components = max(int(_surface_component_stats(mesh)["surface_component_count"]), 1)
    component_penalty = _clamp(math.log1p(max(components - 1, 0)) / math.log1p(24.0))
    blockiness_index = _clamp(0.74 * axis_index + 0.26 * component_penalty)
    return {
        "axis_aligned_normal_fraction": axis_alignment,
        "connectivity_blockiness_index": blockiness_index,
        "blockiness_score": _clamp(1.0 - blockiness_index),
    }


def _mesh_points_for_silhouette(mesh: trimesh.Trimesh) -> np.ndarray:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    if len(vertices) == 0:
        return vertices.reshape((0, 3))
    if len(mesh.faces) == 0:
        return vertices
    centers = np.asarray(mesh.triangles_center, dtype=np.float64)
    return np.vstack([vertices, centers])


def _projection_mask(
    points: np.ndarray,
    axes: tuple[int, int],
    vmin: np.ndarray,
    vmax: np.ndarray,
    resolution: int,
    dilation_iterations: int,
) -> np.ndarray:
    mask = np.zeros((resolution, resolution), dtype=bool)
    if len(points) == 0:
        return mask
    lo = vmin[list(axes)]
    hi = vmax[list(axes)]
    span = np.maximum(hi - lo, 1e-9)
    uv = np.floor((points[:, list(axes)] - lo) / span * (resolution - 1)).astype(np.int64)
    uv = np.clip(uv, 0, resolution - 1)
    mask[uv[:, 0], uv[:, 1]] = True
    return ndimage.binary_dilation(mask, iterations=max(int(dilation_iterations), 0))


def _silhouette_iou(mesh: trimesh.Trimesh, ref: trimesh.Trimesh, resolution: int = 96, tolerance_pixels: int = 10) -> float:
    points = _mesh_points_for_silhouette(mesh)
    ref_points = _mesh_points_for_silhouette(ref)
    if len(points) == 0 or len(ref_points) == 0:
        return 0.0
    all_points = np.vstack([points, ref_points])
    vmin = all_points.min(axis=0)
    vmax = all_points.max(axis=0)
    scores: list[float] = []
    for axes in ((0, 1), (0, 2), (1, 2)):
        a = _projection_mask(points, axes, vmin, vmax, resolution, tolerance_pixels)
        b = _projection_mask(ref_points, axes, vmin, vmax, resolution, tolerance_pixels)
        union = np.logical_or(a, b).sum()
        inter = np.logical_and(a, b).sum()
        scores.append(float(inter / max(int(union), 1)))
    return float(np.mean(scores))


def _bbox_extent_l1(mesh: trimesh.Trimesh, ref: trimesh.Trimesh) -> float:
    if len(mesh.vertices) == 0 or len(ref.vertices) == 0:
        return 1.0
    extent = np.asarray(mesh.bounds[1] - mesh.bounds[0], dtype=np.float64)
    ref_extent = np.asarray(ref.bounds[1] - ref.bounds[0], dtype=np.float64)
    denom = max(float(np.linalg.norm(ref_extent, ord=1)), 1e-9)
    return float(np.linalg.norm(extent - ref_extent, ord=1) / denom)


def _numeric(value: object) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return float(min(max(value, lo), hi))


def _base_metric_row(row: dict[str, object], mesh: trimesh.Trimesh, metadata: dict) -> dict[str, object]:
    face_mask = _face_mask_from_centers(mesh, metadata)
    out: dict[str, object] = {
        "task_id": row["task_id"],
        "task_family": row["task_family"],
        "variant": row["variant"],
        "mesh_path": row["mesh_path"],
        "metadata_path": row["metadata_path"],
        "vertex_count": int(len(mesh.vertices)),
        "triangle_count": int(len(mesh.faces)),
        "surface_area": float(mesh.area) if len(mesh.faces) else 0.0,
        "bbox_diag": float(np.linalg.norm(mesh.bounds[1] - mesh.bounds[0])) if len(mesh.vertices) else 0.0,
        "projection_schedule": metadata.get("projection_schedule", ""),
        "naturalization_scope": metadata.get("naturalization_scope", ""),
        "mask_change_voxel_ratio_proxy": float(metadata.get("mask_change_voxel_ratio_proxy", 0.0)),
    }
    out.update(_surface_component_stats(mesh))
    out.update(_triangle_quality_stats(mesh))
    out.update(_axis_blockiness(mesh))
    out["global_normal_variation_mean_deg"] = _normal_variation(mesh)
    out["local_normal_variation_mean_deg"] = _normal_variation(mesh, face_mask)
    return out


def _scope_locality_score(row: dict[str, object]) -> float:
    scope = str(row.get("naturalization_scope", ""))
    if scope in ("disabled", "per_depth_edit_mask", "weak_masked_blend"):
        return 1.0
    if scope == "global_field_smoothing":
        return 0.25
    return 0.65


def _variant_projection_score(variant: str) -> float:
    if variant in (
        "per_depth_projection",
        "per_depth_weak_naturalization",
        "per_depth_global_naturalization",
        "per_depth_masked_naturalization",
    ):
        return 1.0
    if variant == "final_only_projection_repair":
        return 0.45
    return 0.0


def _variant_naturalization_scope_score(variant: str) -> float:
    if variant == "per_depth_masked_naturalization":
        return 1.0
    if variant == "per_depth_weak_naturalization":
        return 0.42
    if variant == "per_depth_global_naturalization":
        return 0.10
    return 0.0


def _score_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_task: dict[str, dict[str, dict[str, object]]] = {}
    for row in rows:
        by_task.setdefault(str(row["task_id"]), {})[str(row["variant"])] = row

    for task_id, variants in by_task.items():
        raw = variants.get("raw_grammar_proposal", {})
        raw_local = max(_numeric(raw.get("local_normal_variation_mean_deg")), 1e-6)
        for row in variants.values():
            components = int(row["surface_component_count"])
            lcr = _numeric(row["surface_largest_component_ratio"])
            connectivity_score = _clamp(lcr - 0.045 * max(components - 1, 0))
            roughness_gain = _clamp((raw_local - _numeric(row["local_normal_variation_mean_deg"])) / raw_local)
            silhouette_score = 0.55 * _numeric(row["silhouette_iou_vs_raw"]) + 0.45 * _numeric(row["silhouette_iou_vs_per_depth_projection"])
            locality_score = _clamp(
                0.68 * _numeric(row["silhouette_iou_vs_per_depth_projection"])
                + 0.20 * (1.0 - min(_numeric(row["bbox_extent_l1_vs_per_depth_projection"]), 1.0))
                + 0.12 * _scope_locality_score(row)
            )
            complexity_score = _clamp(1.0 - max(_numeric(row["triangle_count"]) - 12000.0, 0.0) / 26000.0, 0.20, 1.0)
            projection_score = _variant_projection_score(str(row["variant"]))
            naturalization_scope_score = _variant_naturalization_scope_score(str(row["variant"]))
            mesh_quality_score = _numeric(row.get("mesh_quality_score"))
            blockiness_score = _numeric(row.get("blockiness_score"))
            score = (
                0.26 * connectivity_score
                + 0.18 * locality_score
                + 0.15 * roughness_gain
                + 0.10 * _clamp(silhouette_score)
                + 0.09 * mesh_quality_score
                + 0.07 * blockiness_score
                + 0.06 * complexity_score
                + 0.04 * projection_score
                + 0.05 * naturalization_scope_score
            )
            row["connectivity_score"] = round(connectivity_score, 6)
            row["roughness_gain_vs_raw"] = round(roughness_gain, 6)
            row["roughness_score"] = round(roughness_gain, 6)
            row["locality_preservation_score"] = round(locality_score, 6)
            row["silhouette_score"] = round(_clamp(silhouette_score), 6)
            row["triangle_efficiency_score"] = round(complexity_score, 6)
            row["main_text_score"] = round(float(score), 6)

        candidates = [
            row
            for row in variants.values()
            if _numeric(row["surface_largest_component_ratio"]) >= 0.98
            and _numeric(row["silhouette_iou_vs_per_depth_projection"]) >= 0.84
        ]
        if not candidates:
            candidates = list(variants.values())
        best = max(candidates, key=lambda r: (_numeric(r["main_text_score"]), -VARIANT_ORDER.index(str(r["variant"]))))
        for row in variants.values():
            if row is best:
                row["score_recommendation"] = "main_text_candidate"
            elif row["variant"] == "raw_grammar_proposal":
                row["score_recommendation"] = "negative_raw_control"
            elif row["variant"] == "final_only_projection_repair":
                row["score_recommendation"] = "negative_final_only_control"
            elif row["variant"] == "per_depth_projection":
                row["score_recommendation"] = "projection_only_control"
            elif row["variant"] == "per_depth_weak_naturalization":
                row["score_recommendation"] = "weak_naturalization_control"
            elif row["variant"] == "per_depth_global_naturalization":
                row["score_recommendation"] = "global_naturalization_control"
            else:
                row["score_recommendation"] = "supplementary_candidate"
    return rows


def _ablation_read(variant: str) -> str:
    if variant == "per_depth_masked_naturalization":
        return "masked local naturalization under per-depth projection"
    if variant == "per_depth_global_naturalization":
        return "global naturalization control that may alter old state"
    if variant == "per_depth_weak_naturalization":
        return "weak masked blend control under per-depth projection"
    if variant == "per_depth_projection":
        return "projection-only structure control without naturalization"
    if variant == "final_only_projection_repair":
        return "final cleanup control without recursive-state stabilization"
    return "raw recursive grammar proposal control"


def _format_float(value: object, digits: int = 4) -> str:
    return f"{_numeric(value):.{digits}f}"


def _paper_table_rows(metric_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in metric_rows:
        rows.append(
            {
                "task_id": row["task_id"],
                "protocol_column": PROTOCOL_LABELS.get(str(row["variant"]), str(row["variant"])),
                "variant": row["variant"],
                "connectivity": _format_float(row.get("connectivity_score")),
                "locality": _format_float(row.get("locality_preservation_score")),
                "roughness_deg": _format_float(row.get("local_normal_variation_mean_deg"), 2),
                "silhouette": _format_float(row.get("silhouette_iou_vs_per_depth_projection")),
                "mesh_quality": _format_float(row.get("mesh_quality_score")),
                "blockiness": _format_float(row.get("connectivity_blockiness_index")),
                "score": _format_float(row.get("main_text_score")),
                "recommendation": row.get("score_recommendation", ""),
            }
        )
    return rows


def _mean(rows: list[dict[str, object]], key: str) -> float:
    if not rows:
        return 0.0
    return float(np.mean([_numeric(row.get(key)) for row in rows]))


def _protocol_summary_rows(metric_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for variant in VARIANT_ORDER:
        rows = [row for row in metric_rows if str(row["variant"]) == variant]
        out.append(
            {
                "protocol_column": PROTOCOL_LABELS.get(variant, variant),
                "variant": variant,
                "task_count": len(rows),
                "recommended_task_count": sum(1 for row in rows if row.get("score_recommendation") == "main_text_candidate"),
                "mean_score": _format_float(_mean(rows, "main_text_score")),
                "mean_connectivity": _format_float(_mean(rows, "connectivity_score")),
                "mean_locality": _format_float(_mean(rows, "locality_preservation_score")),
                "mean_roughness_deg": _format_float(_mean(rows, "local_normal_variation_mean_deg"), 2),
                "mean_silhouette": _format_float(_mean(rows, "silhouette_iou_vs_per_depth_projection")),
                "mean_mesh_quality": _format_float(_mean(rows, "mesh_quality_score")),
                "mean_blockiness": _format_float(_mean(rows, "connectivity_blockiness_index")),
            }
        )
    return out


def _masked_local_advantage_rows(metric_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    by_task: dict[str, dict[str, dict[str, object]]] = {}
    for row in metric_rows:
        by_task.setdefault(str(row["task_id"]), {})[str(row["variant"])] = row
    for task_id in sorted(by_task):
        rows = by_task[task_id]
        masked = rows["per_depth_masked_naturalization"]
        no_n = rows["per_depth_projection"]
        weak = rows["per_depth_weak_naturalization"]
        global_n = rows["per_depth_global_naturalization"]
        out.append(
            {
                "task_id": task_id,
                "delta_score_vs_no_n": _format_float(_numeric(masked["main_text_score"]) - _numeric(no_n["main_text_score"])),
                "delta_score_vs_weak": _format_float(_numeric(masked["main_text_score"]) - _numeric(weak["main_text_score"])),
                "delta_score_vs_global_n": _format_float(_numeric(masked["main_text_score"]) - _numeric(global_n["main_text_score"])),
                "delta_locality_vs_global_n": _format_float(
                    _numeric(masked["locality_preservation_score"]) - _numeric(global_n["locality_preservation_score"])
                ),
                "delta_roughness_deg_vs_no_n": _format_float(
                    _numeric(no_n["local_normal_variation_mean_deg"]) - _numeric(masked["local_normal_variation_mean_deg"]),
                    2,
                ),
                "masked_silhouette_vs_no_n": _format_float(masked["silhouette_iou_vs_per_depth_projection"]),
            }
        )
    return out


def _write_latex_table(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "% Auto-generated by assets/evaluate_masked_naturalization_ablation_20260510.py",
        "\\begin{tabular}{llrrrrrr}",
        "\\toprule",
        "Task & Protocol & Conn. & Locality & Rough. & Silh. & MeshQ & Score \\\\",
        "\\midrule",
    ]
    for row in rows:
        protocol = str(row["protocol_column"]).replace("_", "\\_")
        task = str(row["task_id"]).replace("_", "\\_")
        lines.append(
            f"{task} & {protocol} & {row['connectivity']} & {row['locality']} & {row['roughness_deg']} & "
            f"{row['silhouette']} & {row['mesh_quality']} & {row['score']} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_chinese_summary(path: Path, recommendations: list[dict[str, object]], table_rows: list[dict[str, object]], summary: dict[str, object]) -> None:
    rec_lines = []
    for row in recommendations:
        rec_lines.append(
            f"| `{row['task_id']}` | `{row['recommended_variant']}` | {float(row['main_text_score']):.4f} | "
            f"{float(row['surface_largest_component_ratio']):.4f} | {float(row['silhouette_iou_vs_per_depth_projection']):.4f} | "
            f"{float(row['local_normal_variation_mean_deg']):.2f} |"
        )
    protocol_counts = ", ".join(f"`{label}`" for label in PROTOCOL_LABELS.values())
    lines = [
        "# Masked Local Naturalization 六列同根协议结果 2026-05-10",
        "",
        "## 协议闭合",
        "",
        f"本地包现在覆盖三类任务 × 六列同根协议，共 {summary['row_count']} 行：{protocol_counts}。",
        "`rule-only` 对应原始 grammar proposal；`per-depth/no-N` 是无自然化的投影稳定控制；`weak`、`global-N`、`masked local-N` 用同一 proposal grammar，只改变自然化范围和强度。",
        "",
        "## 推荐行",
        "",
        "| task | 推荐变体 | score | LCR | silhouette vs per-depth | local normal variation |",
        "|---|---|---:|---:|---:|---:|",
        *rec_lines,
        "",
        "## 指标解释",
        "",
        "- connectivity：largest-component ratio 与小碎片惩罚的组合，衡量连接支撑是否能作为递归状态继续使用。",
        "- locality/preservation：相对 per-depth/no-N 的 silhouette、bbox extent 与自然化范围约束，专门惩罚 `global-N` 对旧状态的全局改写。",
        "- roughness/normal variation：edit-mask 附近相邻三角面法线夹角均值，数值越低表示局部连续性越好。",
        "- silhouette：多视角容差膨胀 2D occupancy IoU，用来确认 masked local-N 没有靠全局形变换取平滑。",
        "- mesh quality：三角形 aspect ratio 与退化面比例的 proxy；blockiness 是轴向法线集中度和碎片惩罚的组合。",
        "",
        "## 论文可用文件",
        "",
        f"- `{summary['paper_table_csv']}`",
        f"- `{summary['paper_table_tex']}`",
        f"- `{summary['protocol_summary_csv']}`",
        f"- `{summary['masked_local_advantage_csv']}`",
        f"- `{summary['metrics_csv']}`",
        "",
        "保守表述：masked local-N 在 per-depth projection 已经稳定递归状态的前提下，提升局部表面连续性并保持较高 locality/silhouette；它不是全局拓扑修复器。",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: Iterable[dict[str, object]], fields: list[str] | None = None) -> None:
    rows = list(rows)
    if fields is None:
        fields = sorted({key for row in rows for key, value in row.items() if not isinstance(value, (dict, list))})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def evaluate(asset_dir: Path = DEFAULT_ASSET_DIR, out_dir: Path = DEFAULT_OUT) -> dict[str, object]:
    asset_dir = Path(asset_dir)
    out_dir = Path(out_dir)
    manifest_rows = _load_manifest(asset_dir)
    meshes: dict[tuple[str, str], trimesh.Trimesh] = {}
    metadata: dict[tuple[str, str], dict] = {}
    metric_rows: list[dict[str, object]] = []

    for manifest_row in manifest_rows:
        key = (str(manifest_row["task_id"]), str(manifest_row["variant"]))
        mesh = _load_mesh(Path(str(manifest_row["mesh_path"])))
        meta = _read_json(Path(str(manifest_row["metadata_path"])))
        meshes[key] = mesh
        metadata[key] = meta
        metric_rows.append(_base_metric_row(manifest_row, mesh, meta))

    row_by_key = {(str(row["task_id"]), str(row["variant"])): row for row in metric_rows}
    for key, row in row_by_key.items():
        task_id, variant = key
        mesh = meshes[key]
        raw_ref = meshes.get((task_id, "raw_grammar_proposal"), mesh)
        per_depth_ref = meshes.get((task_id, "per_depth_projection"), mesh)
        row["silhouette_iou_vs_raw"] = round(_silhouette_iou(mesh, raw_ref), 6)
        row["silhouette_iou_vs_per_depth_projection"] = round(_silhouette_iou(mesh, per_depth_ref), 6)
        row["bbox_extent_l1_vs_per_depth_projection"] = round(_bbox_extent_l1(mesh, per_depth_ref), 6)
        row["protocol_column"] = PROTOCOL_LABELS.get(variant, variant)
        row["ablation_read"] = _ablation_read(variant)

    metric_rows = _score_rows(metric_rows)
    order = {variant: i for i, variant in enumerate(VARIANT_ORDER)}
    metric_rows.sort(key=lambda r: (str(r["task_id"]), order.get(str(r["variant"]), 99)))

    recommendations: list[dict[str, object]] = []
    for task_id in sorted({str(row["task_id"]) for row in metric_rows}):
        task_rows = [row for row in metric_rows if str(row["task_id"]) == task_id]
        best = max(task_rows, key=lambda r: _numeric(r["main_text_score"]))
        recommendations.append(
            {
                "task_id": task_id,
                "recommended_variant": best["variant"],
                "main_text_score": best["main_text_score"],
                "surface_largest_component_ratio": best["surface_largest_component_ratio"],
                "silhouette_iou_vs_per_depth_projection": best["silhouette_iou_vs_per_depth_projection"],
                "local_normal_variation_mean_deg": best["local_normal_variation_mean_deg"],
                "reason": "best joint connectivity, local smoothness, and silhouette preservation score",
            }
        )

    fields = [
        "task_id",
        "task_family",
        "variant",
        "score_recommendation",
        "main_text_score",
        "surface_component_count",
        "surface_largest_component_ratio",
        "surface_largest_component_vertices",
        "surface_small_component_count_lt100",
        "connectivity_blockiness_index",
        "axis_aligned_normal_fraction",
        "local_normal_variation_mean_deg",
        "global_normal_variation_mean_deg",
        "roughness_score",
        "silhouette_iou_vs_raw",
        "silhouette_iou_vs_per_depth_projection",
        "locality_preservation_score",
        "bbox_extent_l1_vs_per_depth_projection",
        "mean_triangle_aspect_ratio",
        "degenerate_face_fraction",
        "mesh_quality_score",
        "blockiness_score",
        "vertex_count",
        "triangle_count",
        "surface_area",
        "bbox_diag",
        "mask_change_voxel_ratio_proxy",
        "connectivity_score",
        "roughness_gain_vs_raw",
        "silhouette_score",
        "triangle_efficiency_score",
        "projection_schedule",
        "naturalization_scope",
        "protocol_column",
        "ablation_read",
        "mesh_path",
        "metadata_path",
    ]

    out_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(out_dir / "metrics.csv", metric_rows, fields)
    (out_dir / "metrics.json").write_text(
        json.dumps({"schema": "masked_naturalization_ablation_metrics_20260510", "rows": metric_rows}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    _write_csv(
        out_dir / "score_recommendations.csv",
        recommendations,
        [
            "task_id",
            "recommended_variant",
            "main_text_score",
            "surface_largest_component_ratio",
            "silhouette_iou_vs_per_depth_projection",
            "local_normal_variation_mean_deg",
            "reason",
        ],
    )
    (out_dir / "score_recommendations.json").write_text(
        json.dumps({"rows": recommendations}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    paper_rows = _paper_table_rows(metric_rows)
    paper_table_csv = out_dir / f"{PAPER_TABLE_PATH}.csv"
    paper_table_tex = out_dir / f"{PAPER_TABLE_PATH}.tex"
    protocol_summary_csv = out_dir / f"{PROTOCOL_SUMMARY_PATH}.csv"
    masked_local_advantage_csv = out_dir / f"{MASKED_LOCAL_ADVANTAGE_PATH}.csv"
    zh_summary_path = out_dir / "masked_naturalization_ablation_summary_zh_20260510.md"
    _write_csv(
        paper_table_csv,
        paper_rows,
        [
            "task_id",
            "protocol_column",
            "variant",
            "connectivity",
            "locality",
            "roughness_deg",
            "silhouette",
            "mesh_quality",
            "blockiness",
            "score",
            "recommendation",
        ],
    )
    _write_latex_table(paper_table_tex, paper_rows)
    protocol_summary_rows = _protocol_summary_rows(metric_rows)
    masked_local_advantage_rows = _masked_local_advantage_rows(metric_rows)
    _write_csv(
        protocol_summary_csv,
        protocol_summary_rows,
        [
            "protocol_column",
            "variant",
            "task_count",
            "recommended_task_count",
            "mean_score",
            "mean_connectivity",
            "mean_locality",
            "mean_roughness_deg",
            "mean_silhouette",
            "mean_mesh_quality",
            "mean_blockiness",
        ],
    )
    _write_csv(
        masked_local_advantage_csv,
        masked_local_advantage_rows,
        [
            "task_id",
            "delta_score_vs_no_n",
            "delta_score_vs_weak",
            "delta_score_vs_global_n",
            "delta_locality_vs_global_n",
            "delta_roughness_deg_vs_no_n",
            "masked_silhouette_vs_no_n",
        ],
    )

    rec_map = {str(row["task_id"]): str(row["recommended_variant"]) for row in recommendations}
    summary = {
        "schema": "masked_naturalization_ablation_evaluation_20260510",
        "asset_dir": str(asset_dir),
        "out_dir": str(out_dir),
        "row_count": len(metric_rows),
        "metrics_csv": str(out_dir / "metrics.csv"),
        "metrics_json": str(out_dir / "metrics.json"),
        "score_recommendations_csv": str(out_dir / "score_recommendations.csv"),
        "paper_table_csv": str(paper_table_csv),
        "paper_table_tex": str(paper_table_tex),
        "protocol_summary_csv": str(protocol_summary_csv),
        "masked_local_advantage_csv": str(masked_local_advantage_csv),
        "chinese_summary_md": str(zh_summary_path),
        "main_text_recommendations": rec_map,
        "metric_contract": [
            "surface_component_count and surface_largest_component_ratio measure mesh surface connectivity.",
            "locality_preservation_score combines silhouette preservation, bounding-box extent preservation, and naturalization scope locality.",
            "local/global normal variation are adjacent-face curvature/roughness proxies.",
            "silhouette_iou_vs_raw and silhouette_iou_vs_per_depth_projection are tolerance-dilated multiview 2D occupancy preservation proxies for local naturalization thickness changes.",
            "mesh_quality_score combines triangle aspect-ratio and degenerate-face proxies; blockiness_score penalizes axis-aligned normals and fragments.",
            "main_text_score combines connectivity, locality/preservation, local smoothing, silhouette, mesh quality, blockiness, triangle efficiency, per-depth projection, and masked-scope evidence.",
        ],
    }
    _write_chinese_summary(zh_summary_path, recommendations, paper_rows, summary)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-dir", type=Path, default=DEFAULT_ASSET_DIR)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Evaluate assets without rendering or launching jobs.")
    args = parser.parse_args()
    out_dir = args.out_dir or (Path(args.asset_dir) / ("evaluation_dryrun" if args.dry_run else "evaluation"))
    summary = evaluate(args.asset_dir, out_dir)
    summary["dry_run"] = bool(args.dry_run)
    Path(out_dir, "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
