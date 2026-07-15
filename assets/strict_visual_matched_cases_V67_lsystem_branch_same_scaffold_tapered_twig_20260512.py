#!/usr/bin/env python3
"""V67 same-scaffold tapered-twig L-system branch candidates.

V66 matched the traditional L-system baseline depth/density but still read as
hard capped tubes in close-up. V67 keeps the exact same parsed scaffold, removes
flat terminal caps, and turns terminal nodes into graph-native tapered twig
continuations. Junctions remain shared-vertex connected, with only small
low-amplitude collars to soften pipe intersections.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path
from typing import Dict, Optional

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import procedural_baselines as pb
import strict_visual_matched_cases_V22_botanical_smooth_20260510 as v22
import strict_visual_matched_cases_V23_all_family_20260510 as v23
import strict_visual_matched_cases_V65_lsystem_branch_same_scaffold_implicit_naturalization_20260512 as v65
import strict_visual_matched_cases_V66_lsystem_branch_same_scaffold_capped_junction_20260512 as v66


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
DEFAULT_ACTIVE_GPUS = [4, 5]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 200
CONNECTIVITY_LCR_MIN = 0.999
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V67_lsystem_branch_same_scaffold_tapered_twig_20260512_dryrun"
BASELINE_OBJ = v65.BASELINE_OBJ

SURFACE_STRATEGY = "v67_lsystem_same_scaffold_tapered_twig_depth_density_matched"
SELECTION_BUDGET = "four_v67_same_scaffold_tapered_twig_candidates_local_qa_then_priority_bc_two_gpu_remote"
MESH_PBR_POLICY = "same_lsystem_scaffold_reconstructed_as_tapered_twig_connected_branch_support_for_trellis2_glb_export"
ZOOM_DIVISOR = 2.15


def _incident_edges(edges: list[tuple[int, int, float]], node_count: int) -> list[list[tuple[int, float]]]:
    out: list[list[tuple[int, float]]] = [[] for _ in range(node_count)]
    for a, b, r in edges:
        out[a].append((b, float(r)))
        out[b].append((a, float(r)))
    return out


def _node_vertex_ids(mesh: pb.Mesh, centers: np.ndarray, degree: np.ndarray) -> list[Optional[int]]:
    ids: list[Optional[int]] = []
    for idx, center in enumerate(centers):
        if int(degree[idx]) <= 1:
            ids.append(None)
            continue
        mesh.vertices.append(tuple(map(float, center)))
        ids.append(len(mesh.vertices))
    return ids


def _add_ring(
    mesh: pb.Mesh,
    center: np.ndarray,
    axis: np.ndarray,
    radius: float,
    *,
    sides: int,
    phase: float,
    wobble: float,
) -> list[int]:
    u, v, _w = v22._basis(axis)
    ring: list[int] = []
    for i in range(sides):
        theta = 2.0 * math.pi * i / sides
        # Very small deterministic asymmetry makes twig sections less synthetic
        # without creating leaf-like free detail.
        local = 1.0 + wobble * math.sin(3.0 * theta + phase) + 0.012 * math.cos(5.0 * theta - phase)
        d = math.cos(theta) * u + math.sin(theta) * v
        mesh.vertices.append(tuple(map(float, center + d * radius * local)))
        ring.append(len(mesh.vertices))
    return ring


def _connect_rings(mesh: pb.Mesh, ring_a: list[int], ring_b: list[int]) -> None:
    n = min(len(ring_a), len(ring_b))
    for i in range(n):
        j = (i + 1) % n
        mesh.faces.append((ring_a[i], ring_a[j], ring_b[i]))
        mesh.faces.append((ring_a[j], ring_b[j], ring_b[i]))


def _cap_to_shared_node(mesh: pb.Mesh, node_id: Optional[int], ring: list[int], *, reverse: bool = False) -> None:
    if node_id is None:
        return
    for i in range(len(ring)):
        j = (i + 1) % len(ring)
        if reverse:
            mesh.faces.append((node_id, ring[j], ring[i]))
        else:
            mesh.faces.append((node_id, ring[i], ring[j]))


def _add_taper_tip(mesh: pb.Mesh, ring: list[int], center: np.ndarray, outward: np.ndarray, length: float) -> int:
    tip = center + v22._unit(outward) * float(length)
    mesh.vertices.append(tuple(map(float, tip)))
    tip_id = len(mesh.vertices)
    for i in range(len(ring)):
        j = (i + 1) % len(ring)
        mesh.faces.append((ring[i], ring[j], tip_id))
    return tip_id


def _add_soft_node_collar(
    mesh: pb.Mesh,
    node_vertex_ids: list[Optional[int]],
    centers: np.ndarray,
    incident: list[list[tuple[int, float]]],
    idx: int,
    *,
    collar_scale: float,
    degree: np.ndarray,
) -> int:
    c = node_vertex_ids[idx]
    if c is None or int(degree[idx]) < 2:
        return 0
    center = np.asarray(centers[idx], dtype=float)
    neighbors = incident[idx]
    if not neighbors:
        return 0
    mean_r = float(np.mean([r for _nb, r in neighbors]))
    radius = max(mean_r * collar_scale, 0.0048)
    # Use incident directions rather than a full sphere: it softens shared
    # junctions while preserving branch hierarchy and avoiding V65-style fusion.
    added = 0
    for local_i, (nb, _r) in enumerate(neighbors[:4]):
        axis = v22._unit(np.asarray(centers[nb], dtype=float) - center)
        u, v, _w = v22._basis(axis)
        p1 = center + axis * radius * 0.85 + u * radius * 0.70
        p2 = center + axis * radius * 0.85 - u * radius * 0.70
        p3 = center + axis * radius * 1.45 + v * radius * 0.46
        mesh.vertices.extend([tuple(map(float, p1)), tuple(map(float, p2)), tuple(map(float, p3))])
        a, b, d = len(mesh.vertices) - 2, len(mesh.vertices) - 1, len(mesh.vertices)
        if local_i % 2:
            mesh.faces.append((c, b, a))
            mesh.faces.append((a, b, d))
        else:
            mesh.faces.append((c, a, b))
            mesh.faces.append((a, d, b))
        added += 2
    return added


def _make_tapered_twig_mesh(
    *,
    radius_scale: float,
    terminal_scale: float,
    tip_length_scale: float,
    collar_scale: float,
    sides: int,
    seed: int,
) -> tuple[pb.Mesh, dict]:
    centers, edges, degree, meta = v66._graph_from_baseline()
    incident = _incident_edges(edges, len(centers))
    rng = np.random.default_rng(seed)
    mesh = pb.Mesh([], [])
    center_ids = _node_vertex_ids(mesh, centers, degree)
    terminal_tip_count = 0

    for edge_i, (a, b, r) in enumerate(edges):
        start = np.asarray(centers[a], dtype=float)
        end = np.asarray(centers[b], dtype=float)
        axis = end - start
        length = float(np.linalg.norm(axis))
        if length < 1e-8:
            continue
        w = axis / length
        phase = float(rng.uniform(-0.25, 0.25) + edge_i * 0.173)
        ra = max(float(r) * radius_scale * (terminal_scale if degree[a] <= 1 else 1.0), 0.0028)
        rb = max(float(r) * radius_scale * (terminal_scale if degree[b] <= 1 else 1.0), 0.0028)
        ring_a = _add_ring(mesh, start, axis, ra, sides=sides, phase=phase, wobble=0.020)
        ring_b = _add_ring(mesh, end, axis, rb, sides=sides, phase=phase + 0.73, wobble=0.020)
        _connect_rings(mesh, ring_a, ring_b)

        if int(degree[a]) <= 1:
            terminal_tip_count += 1
            _add_taper_tip(mesh, ring_a, start, -w, max(float(r) * radius_scale * tip_length_scale, 0.012))
        else:
            _cap_to_shared_node(mesh, center_ids[a], ring_a, reverse=True)
        if int(degree[b]) <= 1:
            terminal_tip_count += 1
            _add_taper_tip(mesh, ring_b, end, w, max(float(r) * radius_scale * tip_length_scale, 0.012))
        else:
            _cap_to_shared_node(mesh, center_ids[b], ring_b, reverse=False)

    collar_faces = 0
    for idx in range(len(centers)):
        collar_faces += _add_soft_node_collar(
            mesh,
            center_ids,
            centers,
            incident,
            idx,
            collar_scale=collar_scale,
            degree=degree,
        )

    controls = {
        **meta,
        "surface_strategy": SURFACE_STRATEGY,
        "same_scaffold_as_traditional_baseline": True,
        "source_scaffold_preserved": True,
        "connected_shared_junction_vertices": True,
        "flat_terminal_caps_disabled": True,
        "graph_native_tapered_terminal_tips": True,
        "terminal_tip_count": int(terminal_tip_count),
        "terminal_count": int(np.sum(degree == 1)),
        "branch_junction_count": int(np.sum(degree >= 3)),
        "support_edge_count": int(len(edges)),
        "semantic_detail_count": int(np.sum(degree >= 3) + np.sum(degree == 1)),
        "soft_node_collar_face_count": int(collar_faces),
        "junction_collar_count": int(np.sum(degree >= 2)),
        "radius_scale": float(radius_scale),
        "terminal_scale": float(terminal_scale),
        "tip_length_scale": float(tip_length_scale),
        "collar_scale": float(collar_scale),
        "sides": int(sides),
        "v66_failure_addressed": "V66 matched depth/density but used hard flat terminal caps and pipe-like junction fans.",
        "masked_local_naturalization_target": "same L-system scaffold terminal tips and shared junction necks",
        "mask_scope": "object_space_same_scaffold_terminal_nodes_and_junction_centers",
        "sdedit_seam_backprojection_available": False,
        "claim_boundary": "object-space same-scaffold tapered-tip/junction naturalization; no image-space seam edit",
    }
    return mesh, controls


def _case_specs(out_dir: Path, seed: int) -> list[dict]:
    variants = [
        ("V67_lsys_branch_tapered_twig_A", 4, "olive_bark", 0.90, 0.26, 6.0, 0.74, 14, "balanced same-scaffold tapered-twig A"),
        ("V67_lsys_branch_tapered_dense_B", 5, "warm_bark", 0.98, 0.30, 6.5, 0.82, 14, "priority B: dense same-scaffold, tapered terminals"),
        ("V67_lsys_branch_tapered_fine_C", 4, "pale_cambium", 0.78, 0.24, 7.4, 0.68, 16, "priority C: finer twigs, less pipe bulk"),
        ("V67_lsys_branch_tapered_soft_D", 5, "matte_cedar", 0.86, 0.27, 6.8, 0.92, 16, "soft D: small shared-neck collars, no flat caps"),
    ]
    specs = []
    for idx, (case_id, gpu, guide_key, radius_scale, terminal_scale, tip_length_scale, collar_scale, sides, reason) in enumerate(variants):
        mesh, controls = _make_tapered_twig_mesh(
            radius_scale=radius_scale,
            terminal_scale=terminal_scale,
            tip_length_scale=tip_length_scale,
            collar_scale=collar_scale,
            sides=sides,
            seed=seed + idx * 101,
        )
        specs.append(
            {
                "case_id": case_id,
                "gpu": gpu,
                "guide_key": guide_key,
                "mesh": mesh,
                "controls": controls,
                "seed": seed + idx * 101,
                "reason": reason,
            }
        )
    return specs


def _zoom_targets() -> tuple[list[list[float]], list[list[float]]]:
    centers, _edges, degree, _meta = v66._graph_from_baseline()
    candidates = centers[degree >= 3]
    if len(candidates) == 0:
        candidates = centers
    # Pick upper but still dense side-branch regions so zoom reflects the user's
    # depth/density target rather than isolated terminal tips.
    z = candidates[:, 2]
    y = candidates[:, 1]
    x = candidates[:, 0]
    order = np.lexsort((np.abs(x), np.abs(y), -z))
    chosen = candidates[order[:56]]
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
            raise RuntimeError(f"{spec['case_id']} failed V67 connectivity gate: {metrics}")
        guide_path = guides[spec["guide_key"]]
        metadata = {
            "case_id": spec["case_id"],
            "source_generator": "assets/strict_visual_matched_cases_V67_lsystem_branch_same_scaffold_tapered_twig_20260512.py",
            "root_selection_log": {
                "root_source_type": "traditional_lsystem_branch_same_scaffold_tapered_twig_reconstruction",
                "source_obj": str(BASELINE_OBJ),
                "source_segment_count": int(spec["controls"]["source_cylinder_segments"]),
            },
            "controls": spec["controls"],
            "metrics": metrics,
            "guide_image": guide_path,
            "v67_lsystem_branch_naturalization_contract": {
                "target_failure": "V66 preserved density but retained flat capped pipe-like terminals in zoom.",
                "geometry_operator": "same-scaffold tapered terminal continuation plus small shared-neck junction collars.",
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
            "recursive_mode": "same-scaffold tapered-twig L-system branch naturalization",
            "mesh_path": str(mesh_path),
            "guide_image": guide_path,
            "metadata_path": str(metadata_path),
            "remote_target": REMOTE_TARGET,
            "gpu_group": int(spec["gpu"]),
            "seed": int(spec["seed"]),
            "operators": json.dumps(["same_scaffold_parse", "tapered_terminal_twig_continuation", "shared_junction_neck_closure"], ensure_ascii=False),
            "operator_composition": "same_scaffold_parse -> tapered_terminal_twig_continuation -> shared_junction_neck_closure",
            "controls": controls_json,
            "why_matches_traditional": "Uses the same L-system branch scaffold/depth/density while replacing open/flat pipe ends with tapered twig tips.",
            "strict_match_notes": "same scaffold; visual comparison isolates terminal/junction naturalization under equal recursive density.",
            "case_role": "v67_lsystem_branch_same_scaffold_tapered_twig_naturalization",
            "qa_priority": "publication_grade_depth_density_matched_same_scaffold_tapered_twig_no_flat_caps",
            "rerun_reason": spec["reason"],
            "boundary_tag": "",
            "strict_one_to_one": "true",
            "generation_policy": "same_scaffold_local_materialize_then_two_gpu_remote_if_visual_passes",
            "mesh_input_policy": "obj_mesh_inputs_only",
            "mesh_pbr_policy": MESH_PBR_POLICY,
            "surface_strategy": SURFACE_STRATEGY,
            "block_or_token_stamping": "false",
            "root_variant": spec["case_id"].replace("V67_", ""),
            "grammar_guide": "v67_lsystem_same_scaffold_lowcontrast_bark_guide",
            "parameter_variant": f"sides{spec['controls']['sides']}_r{spec['controls']['radius_scale']}_terminal{spec['controls']['terminal_scale']}_tip{spec['controls']['tip_length_scale']}_collar{spec['controls']['collar_scale']}",
            "selection_budget": SELECTION_BUDGET,
            "storage_root": REMOTE_STORAGE_ROOT,
            "storage_limit_gb": STORAGE_LIMIT_GB,
            "pre_export_lcr_gate": CONNECTIVITY_LCR_MIN,
            "branch_junction_count": int(spec["controls"]["branch_junction_count"]),
            "terminal_count": int(spec["controls"]["terminal_count"]),
            "terminal_tip_count": int(spec["controls"]["terminal_tip_count"]),
            "flat_terminal_caps_disabled": "true",
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
                "terminal_tip_count": int(spec["controls"]["terminal_tip_count"]),
                "source_segment_count": int(spec["controls"]["source_cylinder_segments"]),
                "flat_terminal_caps_disabled": True,
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
                "label": row["case_id"] + "_obj_same_scaffold_tapered_twig_zoom",
                "mesh": str(Path(row["mesh_path"]).resolve()),
                "plan_mesh": str(Path(row["mesh_path"]).resolve()),
                "material_mode": "bark",
                "zoom_levels": 2,
                "zoom_divisor": ZOOM_DIVISOR,
                "detail_targets": detail_targets,
                "fixed_detail_targets": fixed_targets,
                "detail_target_source": "v67_same_scaffold_high_degree_lsystem_junctions_no_terminal_caps",
            }
        )
    zoom_manifest = out_dir / "V67_obj_zoom_manifest_same_scaffold_tapered_twig_20260512.json"
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
        "surface_generator": "strict_visual_matched_cases_V67_lsystem_branch_same_scaffold_tapered_twig",
        "surface_strategy": SURFACE_STRATEGY,
        "selection_budget": SELECTION_BUDGET,
        "manifest": str(out_dir / "manifest.csv"),
        "initial_metrics": str(out_dir / "initial_metrics.csv"),
        "obj_zoom_manifest": str(zoom_manifest),
        "priority_cases_for_remote_if_obj_qa_passes": [
            "V67_lsys_branch_tapered_dense_B",
            "V67_lsys_branch_tapered_fine_C",
        ],
        "do_not_launch_remote_before_local_visual_qa": True,
        "lsystem_branch_gate": {
            "same_scaffold_as_traditional_baseline": True,
            "source_segment_count": int(rows and json.loads(rows[0]["controls"])["source_cylinder_segments"]),
            "min_branch_junctions": min(int(r["branch_junction_count"]) for r in rows) if rows else 0,
            "min_terminal_count": min(int(r["terminal_count"]) for r in rows) if rows else 0,
            "min_terminal_tip_count": min(int(r["terminal_tip_count"]) for r in rows) if rows else 0,
            "flat_terminal_caps_disabled": True,
            "sdedit_seam_backprojection_available": False,
        },
        "v67_design": {
            "v66_not_remote_reason": "same-scaffold density matched, but white zoom still showed hard pipe bundles and flat terminal caps",
            "generator_change_required": True,
            "teaser_claim_boundary": "same-scaffold object-space naturalization only",
        },
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V67 Same-Scaffold Tapered-Twig L-system Naturalization\n\n"
        "V67 preserves the traditional L-system branch scaffold/depth/density, disables flat terminal caps, "
        "and adds graph-native tapered twig continuations plus small shared junction necks. It is a local "
        "geometry/naturalization candidate and must pass white OBJ zoom before any remote textured GLB launch.\n",
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
