#!/usr/bin/env python3
"""Enhanced family-specific metrics for V23 strict matched GLB pools.

This script joins evidence sources without recursive directory scans:

* post-GLB surface-voxel metrics;
* V23 input manifest/metadata controls;
* optional mesh diagnostics loaded from explicitly listed GLB paths.

The resulting metrics are still screening metrics.  They are designed to rank
paper candidates by family before visual QA, not to prove biological, physical,
or exact equivariance claims.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_OUT = PROJECT_ROOT / "results" / "strict_visual_matched_texture_V23_all_family_family_metrics_enhanced_20260510"


RUNS = [
    {
        "run": "seed20262810-25",
        "metrics": PROJECT_ROOT / "results/strict_visual_matched_texture_V23_all_family_20260510_remote/surface_metrics_occ64.csv",
        "inputs": PROJECT_ROOT / "results/strict_visual_matched_texture_V23_all_family_20260510_remote/inputs/manifest.csv",
    },
    {
        "run": "seed20262811-26",
        "metrics": PROJECT_ROOT / "results/strict_visual_matched_texture_V23_all_family_seed20260511_20260510_remote/surface_metrics_occ64.csv",
        "inputs": PROJECT_ROOT / "results/strict_visual_matched_texture_V23_all_family_seed20260511_20260510_remote/inputs/manifest.csv",
    },
    {
        "run": "seed20262812-27",
        "metrics": PROJECT_ROOT / "results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/surface_metrics_occ64.csv",
        "inputs": PROJECT_ROOT / "results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/manifest.csv",
    },
    {
        "run": "seed20262813-28",
        "metrics": PROJECT_ROOT / "results/strict_visual_matched_texture_V23_all_family_seed20260513_20260510_remote/surface_metrics_occ64.csv",
        "inputs": PROJECT_ROOT / "results/strict_visual_matched_texture_V23_all_family_seed20260513_20260510_remote/inputs/manifest.csv",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                fields.append(key)
                seen.add(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in ("", None):
            return default
        return int(float(value))
    except Exception:
        return default


def strip_seed(label: str) -> str:
    for marker in ("_steps", "_tex", "_seed"):
        if marker in label:
            return label.split(marker, 1)[0]
    return label


def rel_to_project(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else PROJECT_ROOT / path


def json_loads(value: str) -> dict[str, Any]:
    if not value:
        return {}
    try:
        obj = json.loads(value)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def mesh_quality_base(status: str) -> dict[str, Any]:
    return {
        "mesh_quality_status": status,
        "mesh_boundary_edges": "",
        "mesh_nonmanifold_edges": "",
        "mesh_degenerate_face_fraction": "",
        "mesh_triangle_aspect_mean": "",
        "mesh_triangle_aspect_p95": "",
        "mesh_face_component_count": "",
        "mesh_is_watertight": "",
        "mesh_normal_coherence": "",
    }


def load_meshes(path: Path):
    try:
        import trimesh  # type: ignore
    except Exception:
        return [], "trimesh_unavailable"
    try:
        loaded = trimesh.load(str(path), force=None, process=False)
        meshes = []
        if hasattr(loaded, "geometry"):
            meshes = [mesh for mesh in loaded.geometry.values() if hasattr(mesh, "vertices")]
        elif hasattr(loaded, "vertices"):
            meshes = [loaded]
        if not meshes:
            return [], "no_mesh"
        return meshes, "ok"
    except Exception as exc:
        return [], f"load_failed:{exc}"


def triangle_aspect_ratios(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    if len(vertices) == 0 or len(faces) == 0:
        return np.zeros((0,), dtype=np.float64)
    tri = vertices[faces[:, :3]]
    e0 = np.linalg.norm(tri[:, 1] - tri[:, 0], axis=1)
    e1 = np.linalg.norm(tri[:, 2] - tri[:, 1], axis=1)
    e2 = np.linalg.norm(tri[:, 0] - tri[:, 2], axis=1)
    longest = np.maximum(np.maximum(e0, e1), e2)
    shortest = np.maximum(np.minimum(np.minimum(e0, e1), e2), 1e-12)
    return longest / shortest


def mesh_quality(path: Path, mode: str) -> dict[str, Any]:
    if mode == "off":
        return mesh_quality_base("skipped")
    meshes, status = load_meshes(path)
    base = mesh_quality_base(status)
    if not meshes:
        return base

    all_aspects: list[np.ndarray] = []
    all_areas: list[np.ndarray] = []
    boundary = 0
    nonmanifold = 0
    normal_num = np.zeros(3, dtype=np.float64)
    normal_den = 0.0
    watertight = True
    nonempty = 0

    for mesh in meshes:
        vertices = np.asarray(mesh.vertices, dtype=np.float64)
        faces = np.asarray(mesh.faces, dtype=np.int64)
        if len(vertices) == 0 or len(faces) == 0:
            continue
        nonempty += 1
        watertight = watertight and bool(getattr(mesh, "is_watertight", False))

        edges = np.sort(np.vstack([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
        counts = Counter(map(tuple, edges.tolist()))
        boundary += sum(1 for count in counts.values() if count == 1)
        nonmanifold += sum(1 for count in counts.values() if count > 2)

        tri = vertices[faces[:, :3]]
        areas = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
        all_areas.append(areas)
        all_aspects.append(triangle_aspect_ratios(vertices, faces))

        normals = np.asarray(getattr(mesh, "face_normals", np.zeros((0, 3))), dtype=np.float64)
        if len(normals) > 2:
            normal_num += normals.mean(axis=0)
            normal_den += float(np.linalg.norm(normals, axis=1).mean())

    if nonempty == 0:
        base["mesh_quality_status"] = "empty"
        return base

    areas = np.concatenate(all_areas) if all_areas else np.zeros((0,), dtype=np.float64)
    aspects = np.concatenate(all_aspects) if all_aspects else np.zeros((0,), dtype=np.float64)
    normal_coherence = ""
    if normal_den > 0:
        normal_coherence = float(np.linalg.norm(normal_num / nonempty) / max(normal_den / nonempty, 1e-12))
    base.update(
        {
            "mesh_quality_status": "ok",
            "mesh_boundary_edges": int(boundary),
            "mesh_nonmanifold_edges": int(nonmanifold),
            "mesh_degenerate_face_fraction": float(np.mean(areas <= 1e-12)),
            "mesh_triangle_aspect_mean": float(np.mean(aspects)) if len(aspects) else "",
            "mesh_triangle_aspect_p95": float(np.quantile(aspects, 0.95)) if len(aspects) else "",
            "mesh_face_component_count": int(nonempty),
            "mesh_is_watertight": bool(watertight),
            "mesh_normal_coherence": normal_coherence,
        }
    )
    return base


def family_metrics(family: str, controls: dict[str, Any], surface: dict[str, str], quality: dict[str, Any]) -> dict[str, Any]:
    lcr0 = safe_float(surface.get("lcr_r0"))
    lcr1 = safe_float(surface.get("lcr_r1"))
    components0 = safe_int(surface.get("components_r0"))
    support_edges = safe_int(controls.get("support_edge_count"))
    semantic = safe_int(controls.get("semantic_detail_count", controls.get("attached_natural_mesh_detail_count")))
    aspect_p95 = safe_float(quality.get("mesh_triangle_aspect_p95"), 0.0)
    boundary_edges = safe_int(quality.get("mesh_boundary_edges"))
    face_components = safe_int(quality.get("mesh_face_component_count"))
    occupied = safe_int(surface.get("occupied"))
    mesh_penalty = min(0.25, math.log1p(boundary_edges) / 80.0 + max(face_components - 1, 0) / 200.0 + max(aspect_p95 - 20.0, 0.0) / 200.0)

    out: dict[str, Any] = {
        "support_edges": support_edges,
        "semantic_details": semantic,
        "detail_density": float(semantic / max(support_edges, 1)),
        "r0_single_component": components0 == 1,
        "r1_single_component": safe_int(surface.get("components_r1")) == 1,
        "root_attachment_proxy": lcr1,
        "mesh_quality_penalty": mesh_penalty,
    }
    if family == "L-system":
        depth = safe_int(controls.get("recursive_depth"))
        terminal_count = safe_int(controls.get("needle_count")) + safe_int(controls.get("rootlet_count")) + safe_int(controls.get("leaf_count")) + safe_int(controls.get("tendril_count"))
        out.update(
            {
                "visible_depth": depth,
                "terminal_detail_count": terminal_count,
                "terminal_detail_density": float(terminal_count / max(support_edges, 1)),
                "branch_depth_score": min(depth / 6.0, 1.0),
                "family_score": 0.35 * lcr0 + 0.25 * lcr1 + 0.20 * min(depth / 6.0, 1.0) + 0.20 * min(terminal_count / max(support_edges, 1), 2.0) / 2.0 - mesh_penalty,
                "family_metric_read": "visible depth, terminal detail density, root-attached surface support",
            }
        )
    elif family == "Space colonization":
        attractors = safe_int(controls.get("attractor_count"))
        covered = safe_int(controls.get("covered_attractors"))
        alive = safe_int(controls.get("alive_attractors"))
        coverage = covered / max(attractors, 1)
        out.update(
            {
                "attractor_count": attractors,
                "covered_attractors": covered,
                "alive_attractors": alive,
                "attractor_coverage": coverage,
                "tip_proxy": support_edges,
                "family_score": 0.30 * lcr0 + 0.20 * lcr1 + 0.30 * coverage + 0.20 * min(semantic / max(support_edges, 1), 0.25) / 0.25 - mesh_penalty,
                "family_metric_read": "attractor coverage, rooted support, terminal semantic attachment",
            }
        )
    elif family == "DLA/frontier":
        events = safe_int(controls.get("frontier_events", controls.get("frontier_event_target")))
        details = safe_int(controls.get("pore_or_facet_detail_count", controls.get("porosity_or_ridge_readability_proxy", semantic)))
        porosity_proxy = occupied / max(events, 1)
        detail_survival = details / max(events, 1)
        out.update(
            {
                "frontier_events": events,
                "pore_or_facet_detail_count": details,
                "frontier_detail_survival_proxy": detail_survival,
                "frontier_occupancy_per_event": porosity_proxy,
                "family_score": 0.40 * lcr0 + 0.20 * lcr1 + 0.20 * min(detail_survival, 0.30) / 0.30 + 0.20 * min(porosity_proxy, 8.0) / 8.0 - mesh_penalty,
                "family_metric_read": "frontier survival proxy, pore/facet detail density, rooted support",
            }
        )
    else:
        radial_order = safe_int(controls.get("radial_order"))
        transform_count = safe_int(controls.get("affine_transform_count"))
        attached = safe_int(controls.get("attached_natural_mesh_detail_count", semantic))
        orbit_strength = max(radial_order, transform_count)
        out.update(
            {
                "radial_order": radial_order,
                "affine_transform_count": transform_count,
                "orbit_strength_proxy": orbit_strength,
                "copy_contact_detail_count": attached,
                "copy_contact_density": float(attached / max(support_edges, 1)),
                "family_score": 0.35 * lcr0 + 0.20 * lcr1 + 0.25 * min(orbit_strength / 8.0, 1.0) + 0.20 * min(attached / max(support_edges, 1), 1.5) / 1.5 - mesh_penalty,
                "family_metric_read": "orbit strength, copy-contact detail density, rooted surface support",
            }
        )
    return out


def joined_rows(runs: list[dict[str, Path]], mesh_quality_mode: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run in runs:
        manifest = {row["case_id"]: row for row in read_csv(run["inputs"])}
        for surf in read_csv(run["metrics"]):
            case = strip_seed(surf.get("label", ""))
            meta = manifest.get(case, {})
            controls = json_loads(meta.get("controls", ""))
            glb_path = rel_to_project(surf.get("path", ""))
            quality = mesh_quality(glb_path, mesh_quality_mode)
            row: dict[str, Any] = {
                "run": run["run"],
                "case": case,
                "family": meta.get("family", ""),
                "match_target": meta.get("match_target", ""),
                "traditional_target": meta.get("traditional_target", ""),
                "glb_path": str(glb_path),
                "surface_components_r0": safe_int(surf.get("components_r0")),
                "surface_lcr_r0": safe_float(surf.get("lcr_r0")),
                "surface_components_r1": safe_int(surf.get("components_r1")),
                "surface_lcr_r1": safe_float(surf.get("lcr_r1")),
                "surface_components_r2": safe_int(surf.get("components_r2")),
                "surface_lcr_r2": safe_float(surf.get("lcr_r2")),
                "occupied": safe_int(surf.get("occupied")),
                "vertices": safe_int(surf.get("vertices")),
                "faces": safe_int(surf.get("faces")),
                "recursive_mode": meta.get("recursive_mode", ""),
                "root_variant": meta.get("root_variant", ""),
                "grammar_guide": meta.get("grammar_guide", ""),
                "parameter_variant": meta.get("parameter_variant", ""),
            }
            row.update(quality)
            row.update(family_metrics(row["family"], controls, surf, quality))
            rows.append(row)
    return rows


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["case"]), []).append(row)
    out: list[dict[str, Any]] = []
    for case, items in sorted(grouped.items()):
        family = items[0].get("family", "")
        scores = [safe_float(item.get("family_score")) for item in items]
        lcrs = [safe_float(item.get("surface_lcr_r0")) for item in items]
        comps = [safe_int(item.get("surface_components_r0")) for item in items]
        penalties = [safe_float(item.get("mesh_quality_penalty")) for item in items]
        verdict = "main-candidate"
        if min(scores or [0]) < 0.70 or min(lcrs or [0]) < 0.999:
            verdict = "appendix-or-rerender"
        if family == "IFS/transform" and "tree" in case.lower():
            verdict = "boundary-control"
        if family == "L-system" and "vine" in case.lower():
            verdict = "appendix-candidate"
        out.append(
            {
                "case": case,
                "family": family,
                "runs": len(items),
                "mean_family_score": float(np.mean(scores)) if scores else "",
                "min_family_score": float(np.min(scores)) if scores else "",
                "min_lcr_r0": float(np.min(lcrs)) if lcrs else "",
                "max_components_r0": int(max(comps)) if comps else "",
                "mean_mesh_quality_penalty": float(np.mean(penalties)) if penalties else "",
                "metric_read": items[0].get("family_metric_read", ""),
                "verdict": verdict,
                "recommended_use": recommend_use(case, family, verdict),
            }
        )
    out.sort(key=lambda r: (str(r["family"]), -safe_float(r["mean_family_score"])))
    return out


def recommend_use(case: str, family: str, verdict: str) -> str:
    if verdict == "boundary-control":
        return "negative/control row for transform admission, not main positive"
    if verdict.startswith("appendix"):
        return "appendix or backup visual unless visual QA is exceptional"
    if family == "DLA/frontier":
        return "main/appendix candidate for frontier-attachment asset comparison"
    if family == "IFS/transform":
        return "main transform-admission candidate if orbit/contact visual QA passes"
    if family == "Space colonization":
        return "main candidate if crown/shell silhouette is visually readable"
    if family == "L-system":
        return "main L-system candidate if terminal details are visible in zoom"
    return "screening candidate"


def write_markdown(path: Path, summary: list[dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# V23 Enhanced Family-Specific Metrics",
        "",
        "日期：2026-05-10",
        "",
        "说明：本表把 V23 GLB surface connectivity、V23 manifest 控制量和可选 mesh quality 诊断合并。它用于候选筛选；最终主文仍需要白底 multi-zoom 视觉 QA。",
        "",
        "| case | family | verdict | runs | mean family score | min LCR r0 | max comp r0 | mean mesh penalty | metric read | recommended use |",
        "|---|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in summary:
        lines.append(
            "| `{case}` | {family} | {verdict} | {runs} | {score:.3f} | {lcr:.6f} | {comp} | {penalty:.3f} | {metric} | {use} |".format(
                case=row["case"],
                family=row["family"],
                verdict=row["verdict"],
                runs=row["runs"],
                score=safe_float(row["mean_family_score"]),
                lcr=safe_float(row["min_lcr_r0"]),
                comp=row["max_components_r0"],
                penalty=safe_float(row["mean_mesh_quality_penalty"]),
                metric=row["metric_read"],
                use=row["recommended_use"],
            )
        )
    lines.extend(
        [
            "",
            "## Metric Notes",
            "",
            "- L-system: visible recursive depth, terminal detail density, and rooted surface support.",
            "- Space colonization: attractor coverage proxy, rooted support, and terminal semantic detail.",
            "- DLA/frontier: frontier event/detail survival proxy, pore/facet detail density, and rooted support.",
            "- IFS/transform: orbit strength proxy, copy-contact detail density, and rooted support.",
            "- Mesh quality penalty combines boundary edges, face components, and extreme triangle aspect ratio; it is a diagnostic for render/mesh readiness, not a topological proof.",
            "",
            "## Current Recommendation",
            "",
            "Use this table to choose the next high-quality Cycles re-render set. Strong structural rows still need human visual QA because several GLBs remain gray or scaffold-like under current guide transfer.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--mesh-quality",
        choices=("off", "full"),
        default="off",
        help="Use off for the publication screening table; full loads each GLB sequentially for heavier mesh diagnostics.",
    )
    args = parser.parse_args()
    rows = joined_rows(RUNS, args.mesh_quality)
    summary = summarize(rows)
    write_csv(args.out_dir / "family_specific_enhanced_rows.csv", rows)
    write_csv(args.out_dir / "family_specific_enhanced_summary.csv", summary)
    (args.out_dir / "family_specific_enhanced_rows.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    (args.out_dir / "family_specific_enhanced_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(args.out_dir / "family_specific_enhanced_summary_zh.md", summary, rows)
    print(json.dumps({"rows": len(rows), "summary": len(summary), "out_dir": str(args.out_dir)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
