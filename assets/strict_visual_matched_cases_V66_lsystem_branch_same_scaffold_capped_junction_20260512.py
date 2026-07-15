#!/usr/bin/env python3
"""V66 same-scaffold capped L-system branch candidates.

V65 matched the traditional L-system depth/density by reconstructing the same
scaffold as an implicit field, but over-fused the branch hierarchy into an
organic mass. V66 keeps the exact same scaffold and instead reconstructs it as
connected capped tubes with small shared junction closures. This preserves the
recursive branch rhythm while removing the traditional baseline's open pipe
ends and hard disconnected caps.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import procedural_baselines as pb
import strict_visual_matched_cases_V22_botanical_smooth_20260510 as v22
import strict_visual_matched_cases_V23_all_family_20260510 as v23
import strict_visual_matched_cases_V65_lsystem_branch_same_scaffold_implicit_naturalization_20260512 as v65


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
DEFAULT_ACTIVE_GPUS = [4, 5]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 200
CONNECTIVITY_LCR_MIN = 0.999
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V66_lsystem_branch_same_scaffold_capped_junction_20260512_dryrun"
BASELINE_OBJ = v65.BASELINE_OBJ

SURFACE_STRATEGY = "v66_lsystem_same_scaffold_capped_junction_depth_density_matched"
SELECTION_BUDGET = "four_v66_same_scaffold_capped_candidates_local_qa_then_priority_bc_two_gpu_remote"
MESH_PBR_POLICY = "same_lsystem_scaffold_reconstructed_as_connected_capped_junction_tubes_for_trellis2_glb_export"
ZOOM_DIVISOR = 2.15


def _cluster_with_inverse(points: np.ndarray, tol: float = 0.010) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    keys = np.rint(points / tol).astype(np.int64)
    unique, inverse = np.unique(keys, axis=0, return_inverse=True)
    centers = np.zeros((len(unique), 3), dtype=np.float64)
    counts = np.zeros(len(unique), dtype=np.int64)
    for idx, cid in enumerate(inverse):
        centers[cid] += points[idx]
        counts[cid] += 1
    centers /= np.maximum(counts[:, None], 1)
    return centers, inverse, counts


def _graph_from_baseline() -> tuple[np.ndarray, list[tuple[int, int, float]], np.ndarray, dict]:
    starts, ends, radii, meta = v65._baseline_segments(BASELINE_OBJ)
    centers, inverse, counts = _cluster_with_inverse(np.vstack([starts, ends]), tol=0.012)
    n = len(starts)
    edges: list[tuple[int, int, float]] = []
    for i in range(n):
        a = int(inverse[i])
        b = int(inverse[n + i])
        if a != b:
            edges.append((a, b, float(radii[i])))
    degree = np.zeros(len(centers), dtype=np.int64)
    for a, b, _r in edges:
        degree[a] += 1
        degree[b] += 1
    meta.update(
        {
            "graph_node_count": int(len(centers)),
            "graph_edge_count": int(len(edges)),
            "junction_node_count": int(np.sum(degree >= 3)),
            "terminal_node_count": int(np.sum(degree == 1)),
        }
    )
    return centers, edges, degree, meta


def _add_connected_capped_segment(
    mesh: pb.Mesh,
    node_vertex_ids: list[int],
    centers: np.ndarray,
    a: int,
    b: int,
    radius: float,
    *,
    sides: int,
    radius_scale: float,
    terminal_scale: float,
    degree: np.ndarray,
    rng: np.random.Generator,
) -> None:
    start = np.asarray(centers[a], dtype=float)
    end = np.asarray(centers[b], dtype=float)
    axis = end - start
    length = float(np.linalg.norm(axis))
    if length < 1e-8:
        return
    u, v, w = v22._basis(axis)
    # Slightly taper terminal ends while preserving baseline density.
    ra = max(radius * radius_scale * (terminal_scale if degree[a] <= 1 else 1.0), 0.0038)
    rb = max(radius * radius_scale * (terminal_scale if degree[b] <= 1 else 1.0), 0.0038)
    start_ring: list[int] = []
    end_ring: list[int] = []
    phase = float(rng.uniform(-0.10, 0.10))
    for i in range(sides):
        theta = 2.0 * math.pi * i / sides
        wobble = 1.0 + 0.025 * math.sin(3.0 * theta + phase)
        d = math.cos(theta) * u + math.sin(theta) * v
        mesh.vertices.append(tuple(start + d * ra * wobble))
        start_ring.append(len(mesh.vertices))
    for i in range(sides):
        theta = 2.0 * math.pi * i / sides
        wobble = 1.0 + 0.025 * math.cos(2.0 * theta + phase)
        d = math.cos(theta) * u + math.sin(theta) * v
        mesh.vertices.append(tuple(end + d * rb * wobble))
        end_ring.append(len(mesh.vertices))
    for i in range(sides):
        j = (i + 1) % sides
        mesh.faces.append((start_ring[i], start_ring[j], end_ring[i]))
        mesh.faces.append((start_ring[j], end_ring[j], end_ring[i]))
        # Cap every segment at the shared graph node center. Shared center
        # vertices make the scaffold face-connected at all L-system junctions.
        mesh.faces.append((node_vertex_ids[a], start_ring[i], start_ring[j]))
        mesh.faces.append((node_vertex_ids[b], end_ring[j], end_ring[i]))


def _add_junction_collar(
    mesh: pb.Mesh,
    node_vertex_ids: list[int],
    centers: np.ndarray,
    idx: int,
    radius: float,
    *,
    sides: int,
    degree: np.ndarray,
) -> None:
    if degree[idx] < 3:
        return
    center = np.asarray(centers[idx], dtype=float)
    # Tiny low-poly closure around high-degree nodes. It is intentionally small:
    # enough to hide hard pipe intersections, not enough to blob out hierarchy.
    axes = [np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0])]
    ring_ids: list[int] = []
    for axis_i, axis in enumerate(axes):
        u, v, _w = v22._basis(axis)
        for k in range(4):
            theta = 0.5 * math.pi * k + 0.32 * axis_i
            p = center + (math.cos(theta) * u + math.sin(theta) * v) * radius
            mesh.vertices.append(tuple(p))
            ring_ids.append(len(mesh.vertices))
    c = node_vertex_ids[idx]
    for i in range(0, len(ring_ids), 2):
        a = ring_ids[i]
        b = ring_ids[(i + 1) % len(ring_ids)]
        mesh.faces.append((c, a, b))


def _make_capped_mesh(
    *,
    radius_scale: float,
    terminal_scale: float,
    collar_scale: float,
    sides: int,
    seed: int,
) -> tuple[pb.Mesh, dict]:
    centers, edges, degree, meta = _graph_from_baseline()
    rng = np.random.default_rng(seed)
    mesh = pb.Mesh([], [])
    node_vertex_ids: list[int] = []
    for center in centers:
        mesh.vertices.append(tuple(map(float, center)))
        node_vertex_ids.append(len(mesh.vertices))
    for a, b, r in edges:
        _add_connected_capped_segment(
            mesh,
            node_vertex_ids,
            centers,
            a,
            b,
            r,
            sides=sides,
            radius_scale=radius_scale,
            terminal_scale=terminal_scale,
            degree=degree,
            rng=rng,
        )
    base_collar_radius = float(np.quantile([edge[2] for edge in edges], 0.72)) * radius_scale * collar_scale
    for idx in range(len(centers)):
        _add_junction_collar(mesh, node_vertex_ids, centers, idx, max(base_collar_radius, 0.0045), sides=sides, degree=degree)
    controls = {
        **meta,
        "surface_strategy": SURFACE_STRATEGY,
        "same_scaffold_as_traditional_baseline": True,
        "connected_shared_junction_vertices": True,
        "open_tube_caps_closed": True,
        "junction_collar_count": int(np.sum(degree >= 3)),
        "terminal_count": int(np.sum(degree == 1)),
        "branch_junction_count": int(np.sum(degree >= 3)),
        "support_edge_count": int(len(edges)),
        "semantic_detail_count": int(np.sum(degree >= 3) + np.sum(degree == 1)),
        "radius_scale": float(radius_scale),
        "terminal_scale": float(terminal_scale),
        "collar_scale": float(collar_scale),
        "sides": int(sides),
        "masked_local_naturalization_target": "same L-system scaffold with capped terminal surfaces and shared junction closures",
        "mask_scope": "object_space_same_scaffold_junction_centers_and_terminal_caps",
        "sdedit_seam_backprojection_available": False,
        "claim_boundary": "object-space same-scaffold capped/junction naturalization; no image-space seam edit",
    }
    return mesh, controls


def _case_specs(out_dir: Path, seed: int) -> list[dict]:
    variants = [
        ("V66_lsys_branch_same_scaffold_capped_A", 4, "olive_bark", 0.92, 0.58, 1.05, 10, "closed same-scaffold tubes, balanced radius"),
        ("V66_lsys_branch_same_scaffold_dense_B", 5, "warm_bark", 1.02, 0.62, 1.10, 10, "priority dense B, closest baseline density with closed caps"),
        ("V66_lsys_branch_same_scaffold_fine_C", 4, "pale_cambium", 0.80, 0.54, 0.92, 12, "priority fine C, thinner recursive twigs and less tube bulk"),
        ("V66_lsys_branch_same_scaffold_soft_D", 5, "matte_cedar", 0.88, 0.56, 1.20, 12, "soft D, stronger junction collars without V65 blob fusion"),
    ]
    specs = []
    for idx, (case_id, gpu, guide_key, radius_scale, terminal_scale, collar_scale, sides, reason) in enumerate(variants):
        mesh, controls = _make_capped_mesh(
            radius_scale=radius_scale,
            terminal_scale=terminal_scale,
            collar_scale=collar_scale,
            sides=sides,
            seed=seed + idx * 97,
        )
        specs.append(
            {
                "case_id": case_id,
                "gpu": gpu,
                "guide_key": guide_key,
                "mesh": mesh,
                "controls": controls,
                "seed": seed + idx * 97,
                "reason": reason,
            }
        )
    return specs


def _zoom_targets() -> tuple[list[list[float]], list[list[float]]]:
    centers, _edges, degree, _meta = _graph_from_baseline()
    candidates = centers[degree >= 3]
    if len(candidates) == 0:
        candidates = centers
    # Upper-side branch region: closer to the baseline detail shown in the
    # traditional zoom, but not a terminal-only target.
    order = np.lexsort((candidates[:, 0], -candidates[:, 2]))
    chosen = candidates[order[:40]]
    targets = [[float(x) for x in p] for p in chosen]
    fixed = targets[:2] if len(targets) >= 2 else targets
    return targets, fixed


def materialize(root: Path, out_dir: Path, seed: int = 20260512, case_limit: Optional[int] = None) -> Dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    guides = v65._write_guides(out_dir)
    specs = _case_specs(out_dir, seed)
    if case_limit is not None:
        specs = specs[: int(case_limit)]
    detail_targets, fixed_targets = _zoom_targets()
    rows = []
    metrics_rows = []
    for spec in specs:
        case_dir = out_dir / spec["case_id"]
        mesh_path = case_dir / f"{spec['case_id']}.obj"
        v23._export_mesh(mesh_path, spec["mesh"])
        metrics = v23._mesh_stats(mesh_path, spec["controls"])
        if metrics["largest_mesh_component_vertex_ratio"] < CONNECTIVITY_LCR_MIN:
            raise RuntimeError(f"{spec['case_id']} failed V66 connectivity gate: {metrics}")
        guide_path = guides[spec["guide_key"]]
        metadata = {
            "case_id": spec["case_id"],
            "source_generator": "assets/strict_visual_matched_cases_V66_lsystem_branch_same_scaffold_capped_junction_20260512.py",
            "root_selection_log": {
                "root_source_type": "traditional_lsystem_branch_same_scaffold_capped_reconstruction",
                "source_obj": str(BASELINE_OBJ),
                "source_segment_count": int(spec["controls"]["source_cylinder_segments"]),
            },
            "controls": spec["controls"],
            "metrics": metrics,
            "guide_image": guide_path,
            "v66_lsystem_branch_naturalization_contract": {
                "target_failure": "V65 preserved density but over-fused hierarchy into an organic mass.",
                "geometry_operator": "same-scaffold connected capped tubes plus shared junction closures.",
                "same_scaffold_as_baseline": True,
                "sdedit_seam_backprojection_available": False,
            },
        }
        metadata_path = case_dir / f"{spec['case_id']}_metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        controls_json = json.dumps(spec["controls"], ensure_ascii=False, sort_keys=True)
        row = {
            "case_id": spec["case_id"],
            "family": "L-system",
            "match_target": "lsys_branch_side_d5",
            "traditional_target": "lsystem_branch.obj",
            "recursive_mode": "same-scaffold capped L-system branch naturalization",
            "mesh_path": str(mesh_path),
            "guide_image": guide_path,
            "metadata_path": str(metadata_path),
            "remote_target": REMOTE_TARGET,
            "gpu_group": int(spec["gpu"]),
            "seed": int(spec["seed"]),
            "operators": json.dumps(["same_scaffold_parse", "connected_capped_tube_reconstruction", "shared_junction_closure"], ensure_ascii=False),
            "operator_composition": "same_scaffold_parse -> connected_capped_tube_reconstruction -> shared_junction_closure",
            "controls": controls_json,
            "why_matches_traditional": "Uses the same L-system branch scaffold/depth/density; caps and junction closures remove baseline open tubes.",
            "strict_match_notes": "same scaffold; visual comparison isolates openness and junction naturalization.",
            "case_role": "v66_lsystem_branch_same_scaffold_capped_junction_naturalization",
            "qa_priority": "publication_grade_depth_density_matched_same_scaffold_closed_caps_readable_branch_hierarchy",
            "rerun_reason": spec["reason"],
            "boundary_tag": "",
            "strict_one_to_one": "true",
            "generation_policy": "same_scaffold_local_materialize_then_two_gpu_remote_if_visual_passes",
            "mesh_input_policy": "obj_mesh_inputs_only",
            "mesh_pbr_policy": MESH_PBR_POLICY,
            "surface_strategy": SURFACE_STRATEGY,
            "block_or_token_stamping": "false",
            "root_variant": spec["case_id"].replace("V66_", ""),
            "grammar_guide": "v66_lsystem_same_scaffold_lowcontrast_bark_guide",
            "parameter_variant": f"sides{spec['controls']['sides']}_r{spec['controls']['radius_scale']}_terminal{spec['controls']['terminal_scale']}_collar{spec['controls']['collar_scale']}",
            "selection_budget": SELECTION_BUDGET,
            "storage_root": REMOTE_STORAGE_ROOT,
            "storage_limit_gb": STORAGE_LIMIT_GB,
            "pre_export_lcr_gate": CONNECTIVITY_LCR_MIN,
            "branch_junction_count": int(spec["controls"]["branch_junction_count"]),
            "terminal_count": int(spec["controls"]["terminal_count"]),
            "sdedit_seam_backprojection_available": "false",
        }
        rows.append(row)
        metrics_rows.append(
            {
                "case_id": spec["case_id"],
                "family": "L-system",
                "match_target": "lsys_branch_side_d5",
                "traditional_target": "lsystem_branch.obj",
                **metrics,
                "branch_junction_count": int(spec["controls"]["branch_junction_count"]),
                "terminal_count": int(spec["controls"]["terminal_count"]),
                "source_segment_count": int(spec["controls"]["source_cylinder_segments"]),
            }
        )

    for name, rows_obj in (("manifest", rows), ("initial_metrics", metrics_rows)):
        (out_dir / f"{name}.json").write_text(json.dumps(rows_obj, indent=2, ensure_ascii=False), encoding="utf-8")
        if rows_obj:
            with (out_dir / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows_obj[0].keys()))
                writer.writeheader()
                writer.writerows(rows_obj)
    obj_zoom_cases = []
    for row in rows:
        obj_zoom_cases.append(
            {
                "label": row["case_id"] + "_obj_same_scaffold_capped_zoom",
                "mesh": str(Path(row["mesh_path"]).resolve()),
                "plan_mesh": str(Path(row["mesh_path"]).resolve()),
                "material_mode": "bark",
                "zoom_levels": 2,
                "zoom_divisor": ZOOM_DIVISOR,
                "detail_targets": detail_targets,
                "fixed_detail_targets": fixed_targets,
                "detail_target_source": "v66_same_scaffold_high_degree_lsystem_junctions",
            }
        )
    zoom_manifest = out_dir / "V66_obj_zoom_manifest_same_scaffold_capped_20260512.json"
    zoom_manifest.write_text(json.dumps({"cases": obj_zoom_cases}, indent=2, ensure_ascii=False), encoding="utf-8")
    case_lines = [f"{row['case_id']}|{row['mesh_path']}|{row['guide_image']}|{row['seed']}|{row['gpu_group']}" for row in rows]
    (out_dir / "a100-2_cases.txt").write_text("\n".join(case_lines) + "\n", encoding="utf-8")
    (out_dir / "gpu45_cases.txt").write_text("\n".join(case_lines) + "\n", encoding="utf-8")
    for gpu in ALLOWED_GPUS:
        selected = [line for line, row in zip(case_lines, rows) if int(row["gpu_group"]) == gpu]
        (out_dir / f"gpu{gpu}_cases.txt").write_text("\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")
    summary = {
        "out_dir": str(out_dir),
        "num_cases": len(rows),
        "remote_target": REMOTE_TARGET,
        "allowed_gpus": ALLOWED_GPUS,
        "default_active_gpus": DEFAULT_ACTIVE_GPUS,
        "max_simultaneous_remote_gpus": 2,
        "storage_root": REMOTE_STORAGE_ROOT,
        "storage_limit_gb": STORAGE_LIMIT_GB,
        "surface_generator": "strict_visual_matched_cases_V66_lsystem_branch_same_scaffold_capped_junction",
        "surface_strategy": SURFACE_STRATEGY,
        "selection_budget": SELECTION_BUDGET,
        "manifest": str(out_dir / "manifest.csv"),
        "initial_metrics": str(out_dir / "initial_metrics.csv"),
        "obj_zoom_manifest": str(zoom_manifest),
        "priority_cases_for_remote_if_obj_qa_passes": [
            "V66_lsys_branch_same_scaffold_dense_B",
            "V66_lsys_branch_same_scaffold_fine_C",
        ],
        "do_not_launch_remote_before_local_visual_qa": True,
        "lsystem_branch_gate": {
            "same_scaffold_as_traditional_baseline": True,
            "source_segment_count": int(rows and json.loads(rows[0]["controls"])["source_cylinder_segments"]),
            "min_branch_junctions": min(int(r["branch_junction_count"]) for r in rows) if rows else 0,
            "min_terminal_count": min(int(r["terminal_count"]) for r in rows) if rows else 0,
            "sdedit_seam_backprojection_available": False,
        },
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V66 Same-Scaffold Capped L-system Naturalization\n\n"
        "V66 preserves the traditional L-system branch scaffold/depth/density but reconstructs it as connected capped tubes with shared junction closures. "
        "It targets the user's latest request: match baseline depth/density while avoiding open tubes and hard seams.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("RGG_ROOT", ROOT_DIR)))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260512)
    parser.add_argument("--case-limit", type=int, default=None)
    args = parser.parse_args()
    materialize(args.root, args.out, seed=args.seed, case_limit=args.case_limit)


if __name__ == "__main__":
    main()
