#!/usr/bin/env python3
"""Build publication-oriented projection and masked-naturalization matrices.

This runner is intentionally deterministic and local.  It closes the metric
contract for Experiment 2 and Experiment 4 before sending only the strongest
visual candidates to remote Trellis/PBR reruns.
"""

from __future__ import annotations

import argparse
import csv
import importlib
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
ASSETS_DIR = PROJECT_ROOT / "assets"
if str(ASSETS_DIR) not in sys.path:
    sys.path.insert(0, str(ASSETS_DIR))
DEFAULT_OUT = PROJECT_ROOT / "results" / "projection_masked_ablation_matrices_20260511"
DEFAULT_VISUAL = PROJECT_ROOT / "visuals" / "projection_masked_ablation_matrices_20260511"
DEFAULT_DRAFTS = PROJECT_ROOT / "paper_siga" / "drafts"
DEFAULT_FIGURES = PROJECT_ROOT / "paper_siga" / "figures" / "ablation_pptx_20260511"
DEFAULT_DOC = PROJECT_ROOT / "docs" / "evaluation" / "projection_masked_ablation_matrices_zh_20260511.md"

old_assets = importlib.import_module("masked_naturalization_ablation_assets_20260510")
old_eval = importlib.import_module("evaluate_masked_naturalization_ablation_20260510")
old_m3 = importlib.import_module("export_masked_naturalization_m2_m3_20260510")
mesh_metrics = importlib.import_module("recursive_growth_mesh_metrics")


EXTRA_TASKS = [
    {
        "task_id": "vine_trellis",
        "task_family": "vine/branch",
        "label": "vine trellis branch",
        "bound": 1.42,
        "attach_threshold": 0.25,
        "bridge_radius": 0.118,
        "naturalization_sigma": 0.38,
        "mask_radius": 0.23,
        "seed_offset": 71,
    }
]

TASKS = list(old_assets.TASKS) + EXTRA_TASKS
TASK_BY_ID = {str(task["task_id"]): task for task in TASKS}

PROJECTION_VARIANTS = [
    "no_projection",
    "final_only_projection",
    "per_depth_prune_only",
    "per_depth_connector_aware",
    "full_ps_rslg",
]

PROJECTION_LABELS = {
    "no_projection": "no projection",
    "final_only_projection": "final-only",
    "per_depth_prune_only": "per-depth prune-only",
    "per_depth_connector_aware": "per-depth connector-aware",
    "full_ps_rslg": "full PS-RSLG",
}

STABLE_VARIANT_OFFSETS = {
    "no_projection": 1100,
    "final_only_projection": 1200,
    "per_depth_prune_only": 1300,
    "per_depth_connector_aware": 1400,
    "full_ps_rslg": 1500,
    "rule_only": 2100,
    "no_naturalization_no_projection": 2200,
    "weak_blend_no_projection": 2300,
    "masked_local_no_projection": 2400,
    "global_naturalization_no_projection": 2500,
    "no_naturalization_with_projection": 2600,
    "weak_blend_with_projection": 2700,
    "masked_local_with_projection": 2800,
    "global_naturalization_with_projection": 2900,
    "final_only_projection_control": 3000,
}

NATURALIZATION_VARIANTS = [
    "rule_only",
    "no_naturalization_no_projection",
    "weak_blend_no_projection",
    "masked_local_no_projection",
    "global_naturalization_no_projection",
    "no_naturalization_with_projection",
    "weak_blend_with_projection",
    "masked_local_with_projection",
    "global_naturalization_with_projection",
    "final_only_projection_control",
]

NATURALIZATION_LABELS = {
    "rule_only": "rule-only",
    "no_naturalization_no_projection": "no-N/no-proj",
    "weak_blend_no_projection": "weak/no-proj",
    "masked_local_no_projection": "masked/no-proj",
    "global_naturalization_no_projection": "global/no-proj",
    "no_naturalization_with_projection": "no-N/+proj",
    "weak_blend_with_projection": "weak/+proj",
    "masked_local_with_projection": "masked/+proj",
    "global_naturalization_with_projection": "global/+proj",
    "final_only_projection_control": "final-only ctrl",
}

PANEL_COLORS = {
    "no_projection": (130, 95, 88),
    "final_only_projection": (126, 111, 82),
    "per_depth_prune_only": (82, 112, 148),
    "per_depth_connector_aware": (70, 132, 112),
    "full_ps_rslg": (82, 128, 86),
    "rule_only": (130, 95, 88),
    "no_naturalization_no_projection": (130, 95, 88),
    "weak_blend_no_projection": (128, 116, 82),
    "masked_local_no_projection": (90, 128, 105),
    "global_naturalization_no_projection": (126, 88, 134),
    "no_naturalization_with_projection": (82, 112, 148),
    "weak_blend_with_projection": (132, 116, 72),
    "masked_local_with_projection": (78, 132, 92),
    "global_naturalization_with_projection": (128, 80, 128),
    "final_only_projection_control": (126, 111, 82),
}


@dataclass(frozen=True)
class Controls:
    projection_schedule: str
    naturalization_policy: str
    per_depth_projection: bool
    final_projection: bool
    connector_aware: bool
    prune_only: bool
    naturalization_mode: str
    naturalization_strength: float
    proposal_naturalization_strength: float
    old_state_clamped: bool
    global_state_mutable: bool


def _controls_for_variant(variant: str) -> Controls:
    if variant in ("no_projection", "rule_only", "no_naturalization_no_projection"):
        return Controls("disabled", "disabled", False, False, False, False, "disabled", 0.0, 0.0, False, False)
    if variant in ("final_only_projection", "final_only_projection_control"):
        return Controls("after_final_depth_only", "disabled", False, True, True, False, "disabled", 0.0, 0.0, False, False)
    if variant == "per_depth_prune_only":
        return Controls("after_each_depth_before_next_rule", "disabled", True, False, False, True, "disabled", 0.0, 0.0, False, False)
    if variant in ("per_depth_connector_aware", "no_naturalization_with_projection"):
        return Controls("after_each_depth_before_next_rule", "disabled", True, False, True, False, "disabled", 0.0, 0.0, False, False)
    if variant in ("full_ps_rslg", "masked_local_with_projection"):
        return Controls(
            "after_each_depth_before_next_rule",
            "masked_local",
            True,
            False,
            True,
            False,
            "per_depth_edit_mask",
            1.0,
            1.0,
            True,
            False,
        )
    if variant == "weak_blend_with_projection":
        return Controls(
            "after_each_depth_before_next_rule",
            "weak_feature_blend",
            True,
            False,
            True,
            False,
            "weak_masked_blend",
            0.35,
            0.35,
            True,
            False,
        )
    if variant == "global_naturalization_with_projection":
        return Controls(
            "after_each_depth_before_next_rule",
            "global_naturalization",
            True,
            False,
            True,
            False,
            "global_field_smoothing",
            0.9,
            0.65,
            False,
            True,
        )
    if variant == "weak_blend_no_projection":
        return Controls("disabled", "weak_feature_blend", False, False, False, False, "weak_masked_blend", 0.35, 0.35, True, False)
    if variant == "masked_local_no_projection":
        return Controls("disabled", "masked_local", False, False, False, False, "per_depth_edit_mask", 1.0, 1.0, True, False)
    if variant == "global_naturalization_no_projection":
        return Controls("disabled", "global_naturalization", False, False, False, False, "global_field_smoothing", 0.9, 0.65, False, True)
    raise ValueError(f"unknown variant: {variant}")


def _vine_trellis_proposals(depth: int, rng: np.random.Generator) -> list[dict[str, object]]:
    """A fourth deterministic case so projection and naturalization visuals do not share tasks."""
    segment = old_assets._segment
    sphere = old_assets._sphere
    ellipsoid = old_assets._ellipsoid
    jitter = old_assets._jitter
    vec = old_assets._vec
    if depth == 0:
        return [
            sphere((-0.48, -0.38, -0.16), 0.095, depth, "vine_root_anchor", masked=False),
            segment((-0.48, -0.38, -0.16), (-0.24, -0.08, -0.02), 0.067, depth, "primary_vine_branch", masked=False),
            segment((-0.24, -0.08, -0.02), (0.06, 0.20, 0.12), 0.058, depth, "primary_vine_branch", masked=False),
            segment((0.06, 0.20, 0.12), (0.34, 0.42, 0.24), 0.048, depth, "primary_vine_branch", masked=False),
            ellipsoid((0.08, 0.08, -0.10), (0.18, 0.055, 0.075), depth, "support_leaf_cluster", masked=False),
        ]
    if depth == 1:
        return [
            segment((0.34, 0.42, 0.24), (0.62, 0.62, 0.42), 0.036, depth, "vine_branch_tip", masked=True),
            segment((0.08, 0.20, 0.13), (-0.12, 0.46, 0.34), 0.033, depth, "vine_branch_tip", masked=True),
            segment((0.18, 0.34, 0.19), (0.08, 0.62, 0.48), 0.031, depth, "vine_tendril_branch", masked=True),
            segment((0.42, 0.72, 0.16), (0.66, 0.94, 0.30), 0.028, depth, "raw_gap_vine_branch", masked=True),
        ]
    return [
        segment((0.62, 0.62, 0.42), (0.88, 0.78, 0.56), 0.024, depth, "terminal_vine_tip", masked=True),
        segment((-0.12, 0.46, 0.34), (-0.34, 0.62, 0.52), 0.023, depth, "terminal_vine_tip", masked=True),
        segment((0.08, 0.62, 0.48), (0.00, 0.90, 0.68), 0.022, depth, "terminal_vine_tip", masked=True),
        segment((0.50, 0.48, 0.34), (0.70, 0.38, 0.56), 0.021, depth, "vine_leaf_branch", masked=True),
        segment((-0.62, 0.28, 0.20), (-0.86, 0.42, 0.35), 0.020, depth, "raw_orphan_vine_tip", masked=True),
        sphere(jitter(vec((0.84, 0.76, 0.55)), rng, 0.016), 0.034, depth, "vine_hair_cluster", masked=True),
    ]


def _task_proposals(task_id: str, depth: int, rng: np.random.Generator) -> list[dict[str, object]]:
    if task_id == "vine_trellis":
        return _vine_trellis_proposals(depth, rng)
    return old_assets._task_proposals(task_id, depth, rng)


def _active_handle_indices(primitives: list[dict[str, object]]) -> list[int]:
    return [i for i, primitive in enumerate(primitives) if old_m3._is_active_handle(primitive)]


def _root_reachable_indices(primitives: list[dict[str, object]]) -> set[int]:
    adjacency = old_m3._contact_graph(primitives)
    return old_m3._reachable_from_roots(primitives, adjacency)


def _trace_metric_snapshot(primitives: list[dict[str, object]], proposed_active_count: int | None = None) -> dict[str, float | int]:
    reachable = _root_reachable_indices(primitives)
    active = _active_handle_indices(primitives)
    reachable_active = [i for i in active if i in reachable]
    orphan_active = [i for i in active if i not in reachable]
    frontier = [i for i, primitive in enumerate(primitives) if old_m3._is_frontier_handle(primitive)]
    reachable_frontier = [i for i in frontier if i in reachable]
    masses = np.asarray([old_m3._primitive_mass_proxy(primitive) for primitive in primitives], dtype=np.float64)
    total_mass = float(np.sum(masses)) if len(masses) else 0.0
    reachable_mass = float(np.sum(masses[list(reachable)])) if reachable else 0.0
    denom = proposed_active_count if proposed_active_count is not None else len(active)
    return {
        "active_handle_count_proxy": int(len(active)),
        "root_reachable_active_handles_proxy": int(len(reachable_active)),
        "orphan_active_handles_proxy": int(len(orphan_active)),
        "root_reachability_proxy": float(1.0 if not active else len(reachable_active) / max(len(active), 1)),
        "frontier_reachability_proxy": float(1.0 if not frontier else len(reachable_frontier) / max(len(frontier), 1)),
        "handle_survival_proxy": float(1.0 if not denom else len(reachable_active) / max(int(denom or 0), 1)),
        "root_attached_support_mass_proxy": float(reachable_mass / max(total_mass, 1e-9)),
        "orphan_role_count_proxy": int(sum(1 for primitive in primitives if old_m3._is_orphan_role(primitive))),
    }


def _prune_to_reachable(primitives: list[dict[str, object]]) -> list[dict[str, object]]:
    reachable = _root_reachable_indices(primitives)
    return [primitive for i, primitive in enumerate(primitives) if i in reachable]


def _serialize_state(primitives: list[dict[str, object]]) -> list[dict[str, object]]:
    return [old_assets._serialize_primitive(primitive) for primitive in primitives]


def _mesh_from_state(task: dict[str, object], state: list[dict[str, object]], controls: Controls, resolution: int) -> trimesh.Trimesh:
    mesh = old_assets._mesh_from_primitives(
        state,
        task,
        resolution=int(resolution),
        naturalization_mode=controls.naturalization_mode,
        naturalization_strength=float(controls.naturalization_strength),
    )
    return mesh


def _generate_state(
    task: dict[str, object],
    variant: str,
    out_dir: Path,
    seed: int,
    resolution: int,
    depth_count: int,
    experiment: str,
) -> dict[str, object]:
    controls = _controls_for_variant(variant)
    seed_offset = STABLE_VARIANT_OFFSETS[variant] + (0 if experiment == "projection" else 50000)
    rng = np.random.default_rng(int(seed) + int(task["seed_offset"]) + seed_offset)
    case_dir = out_dir / experiment / str(task["task_id"]) / f"seed_{int(seed)}" / variant
    case_dir.mkdir(parents=True, exist_ok=True)

    state: list[dict[str, object]] = []
    base_state: list[dict[str, object]] = []
    edit_mask_centers: list[list[float]] = []
    depth_trace: list[dict[str, object]] = []
    before_projection_snapshots: list[dict[str, float | int]] = []
    after_projection_snapshots: list[dict[str, float | int]] = []
    proposed_active_counts: list[int] = []
    deleted_active_counts: list[int] = []

    for depth in range(int(depth_count)):
        proposals = _task_proposals(str(task["task_id"]), depth, rng)
        if depth == 0:
            base_state.extend(proposals)
        if controls.proposal_naturalization_strength > 0.0 and depth > 0:
            proposals = old_assets._naturalize_new_primitives(
                task, proposals, depth, rng, controls.proposal_naturalization_strength
            )
        candidate = state + proposals
        proposed_active = len(_active_handle_indices(candidate))
        bridges: list[dict[str, object]] = []
        before = _trace_metric_snapshot(candidate, proposed_active_count=proposed_active)
        if controls.per_depth_projection and depth > 0:
            if controls.connector_aware:
                bridges = old_assets._bridge_candidates(state, proposals, task, depth)
                candidate = candidate + bridges
            if controls.prune_only:
                candidate = _prune_to_reachable(candidate)
            else:
                candidate = _prune_to_reachable(candidate)
        state = candidate
        after = _trace_metric_snapshot(state, proposed_active_count=proposed_active)
        before_projection_snapshots.append(before)
        after_projection_snapshots.append(after)
        proposed_active_counts.append(proposed_active)
        deleted_active_counts.append(max(int(before["active_handle_count_proxy"]) - int(after["active_handle_count_proxy"]), 0))
        if depth > 0:
            mask_points = [old_assets._primitive_center(p) for p in proposals + bridges if bool(p.get("masked"))]
            edit_mask_centers.extend([[float(x) for x in point.tolist()] for point in mask_points])
        stage_mesh = _mesh_from_state(task, state, controls, resolution)
        stage_path = case_dir / f"depth_{depth + 1:02d}.obj"
        stage_mesh.export(stage_path)
        depth_trace.append(
            {
                "depth": depth + 1,
                "stage_mesh": str(stage_path),
                "proposal_primitive_count": len(proposals),
                "projection_bridge_count": len(bridges),
                "projection_applied": bool(controls.per_depth_projection and depth > 0),
                "active_handles_before_projection_proxy": before["active_handle_count_proxy"],
                "orphan_active_handles_before_projection_proxy": before["orphan_active_handles_proxy"],
                "active_handles_after_projection_proxy": after["active_handle_count_proxy"],
                "orphan_active_handles_after_projection_proxy": after["orphan_active_handles_proxy"],
                "root_reachability_after_projection_proxy": after["root_reachability_proxy"],
                "handle_survival_after_projection_proxy": after["handle_survival_proxy"],
                "stage_vertices": int(len(stage_mesh.vertices)),
                "stage_faces": int(len(stage_mesh.faces)),
            }
        )

    final_projection_bridges: list[dict[str, object]] = []
    recursive_metric_source = after_projection_snapshots
    if controls.final_projection:
        non_base = [primitive for primitive in state if int(primitive.get("depth", 0)) > 0]
        final_projection_bridges = old_assets._bridge_candidates(base_state, non_base, task, int(depth_count))
        state = state + final_projection_bridges
        state = _prune_to_reachable(state)
        edit_mask_centers.extend([[float(x) for x in old_assets._primitive_center(p).tolist()] for p in final_projection_bridges])
        recursive_metric_source = before_projection_snapshots

    final_mesh = _mesh_from_state(task, state, controls, resolution)
    mesh_path = case_dir / "mesh.obj"
    final_mesh.export(mesh_path)

    recursive_metric_source = [
        row for row in recursive_metric_source if int(row.get("active_handle_count_proxy", 0)) > 0
    ]
    recursive_root_reach = float(np.mean([float(row["root_reachability_proxy"]) for row in recursive_metric_source])) if recursive_metric_source else 1.0
    recursive_orphans = float(np.mean([float(row["orphan_active_handles_proxy"]) for row in recursive_metric_source])) if recursive_metric_source else 0.0
    recursive_survival = float(np.mean([float(row["handle_survival_proxy"]) for row in recursive_metric_source])) if recursive_metric_source else 1.0
    final_trace = _trace_metric_snapshot(state)
    metadata = {
        "schema": "projection_masked_ablation_asset_metadata_20260511",
        "experiment": experiment,
        "task_id": task["task_id"],
        "task_family": task["task_family"],
        "variant": variant,
        "seed": int(seed),
        "mesh_path": str(mesh_path),
        "resolution": int(resolution),
        "depth_count": int(depth_count),
        "projection_schedule": controls.projection_schedule,
        "projection_policy": variant if experiment == "projection" else controls.projection_schedule,
        "connector_aware_projection": bool(controls.connector_aware),
        "prune_only_projection": bool(controls.prune_only),
        "naturalization_policy": controls.naturalization_policy,
        "naturalization_mode": controls.naturalization_mode,
        "naturalization_strength": float(controls.naturalization_strength),
        "proposal_naturalization_strength": float(controls.proposal_naturalization_strength),
        "old_state_clamped_during_masked_update": bool(controls.old_state_clamped),
        "global_state_mutable_during_naturalization": bool(controls.global_state_mutable),
        "final_projection_bridge_count": len(final_projection_bridges),
        "edit_mask_radius": float(task["mask_radius"]),
        "edit_mask_centers": edit_mask_centers,
        "depth_trace": depth_trace,
        "primitive_trace": _serialize_state(state),
        "recursive_state_metric_source": "pre_final_intermediate_states" if controls.final_projection else "after_each_depth_state",
        "recursive_root_reachability_proxy": recursive_root_reach,
        "recursive_orphan_active_handles_proxy": recursive_orphans,
        "recursive_handle_survival_proxy": recursive_survival,
        "recursive_deleted_active_handles_mean_proxy": float(np.mean(deleted_active_counts)) if deleted_active_counts else 0.0,
        "final_trace_metrics": final_trace,
        "metric_limitations": "deterministic primitive trace and mesh proxy; not a Trellis sparse-latent runtime graph.",
    }
    metadata_path = case_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    mesh_stats = old_assets._mesh_stats(final_mesh)
    return {
        "experiment": experiment,
        "task_id": task["task_id"],
        "task_family": task["task_family"],
        "variant": variant,
        "seed": int(seed),
        "mesh_path": str(mesh_path),
        "metadata_path": str(metadata_path),
        "vertices": mesh_stats["vertices"],
        "faces": mesh_stats["faces"],
        "bbox_diag": mesh_stats["bbox_diag"],
        "surface_area": mesh_stats["surface_area"],
        "projection_schedule": controls.projection_schedule,
        "naturalization_policy": controls.naturalization_policy,
    }


def _load_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(str(path), force="scene", process=False)
    if isinstance(loaded, trimesh.Trimesh):
        mesh = loaded
    else:
        meshes = []
        for node_name in loaded.graph.nodes_geometry:
            transform, geom_name = loaded.graph[node_name]
            geom = loaded.geometry.get(geom_name)
            if isinstance(geom, trimesh.Trimesh) and len(geom.vertices):
                copied = geom.copy()
                copied.apply_transform(transform)
                meshes.append(copied)
        mesh = trimesh.util.concatenate(meshes) if meshes else trimesh.Trimesh(process=False)
    mesh.remove_unreferenced_vertices()
    return mesh


def _surface_dilated_occupancy_stats(
    mesh: trimesh.Trimesh,
    resolution: int = 64,
    dilation_iterations: int = 2,
) -> dict[str, object]:
    """Surface-sampled occupancy LCR for marching-cubes and GLB-style meshes.

    Vertex-only occupancy underestimates connectedness for smooth extracted
    surfaces because adjacent faces may not share adjacent quantized vertices at
    high resolution.  We use vertices, triangle centers, and edge midpoints,
    then apply a small 6-neighborhood dilation before component counting.
    """
    if len(mesh.vertices) == 0:
        return {
            "occupancy_resolution": int(resolution),
            "occupied_voxels": 0,
            "occupancy_component_count_6n": 0,
            "largest_occupancy_component_voxels_6n": 0,
            "largest_occupancy_component_ratio_6n": 0.0,
            "occupancy_status": "empty",
            "occupancy_sampling": "surface_vertices_centers_edges_dilated",
            "occupancy_dilation_iterations": int(dilation_iterations),
        }
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    samples = [vertices]
    if len(mesh.faces):
        faces = np.asarray(mesh.faces, dtype=np.int64)
        valid = faces[(faces >= 0).all(axis=1) & (faces < len(vertices)).all(axis=1)]
        if len(valid):
            tri = vertices[valid]
            samples.extend(
                [
                    tri.mean(axis=1),
                    (tri[:, 0] + tri[:, 1]) * 0.5,
                    (tri[:, 1] + tri[:, 2]) * 0.5,
                    (tri[:, 2] + tri[:, 0]) * 0.5,
                ]
            )
    points = np.vstack(samples)
    vmin = points.min(axis=0)
    vmax = points.max(axis=0)
    extent = float(np.max(vmax - vmin))
    if extent <= 1e-12:
        return {
            "occupancy_resolution": int(resolution),
            "occupied_voxels": 1,
            "occupancy_component_count_6n": 1,
            "largest_occupancy_component_voxels_6n": 1,
            "largest_occupancy_component_ratio_6n": 1.0,
            "occupancy_status": "degenerate_bbox",
            "occupancy_sampling": "surface_vertices_centers_edges_dilated",
            "occupancy_dilation_iterations": int(dilation_iterations),
        }
    coords = np.floor((points - vmin) / extent * (int(resolution) - 1e-9)).astype(np.int64)
    coords = np.clip(coords, 0, int(resolution) - 1)
    coords = np.unique(coords, axis=0)
    grid = np.zeros((int(resolution), int(resolution), int(resolution)), dtype=bool)
    grid[coords[:, 0], coords[:, 1], coords[:, 2]] = True
    structure = ndimage.generate_binary_structure(3, 1)
    if int(dilation_iterations) > 0:
        grid = ndimage.binary_dilation(grid, structure=structure, iterations=int(dilation_iterations))
    labels, comp_count = ndimage.label(grid, structure=structure)
    counts = np.bincount(labels.ravel())[1:]
    largest = int(counts.max()) if len(counts) else 0
    occupied = int(counts.sum()) if len(counts) else 0
    return {
        "occupancy_resolution": int(resolution),
        "occupied_voxels": occupied,
        "occupancy_component_count_6n": int(comp_count),
        "largest_occupancy_component_voxels_6n": largest,
        "largest_occupancy_component_ratio_6n": float(largest / max(occupied, 1)),
        "occupancy_status": "surface_sampled_dilated",
        "occupancy_sampling": "surface_vertices_centers_edges_dilated",
        "occupancy_dilation_iterations": int(dilation_iterations),
    }


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _mesh_metric_row(manifest_row: dict[str, object], mesh: trimesh.Trimesh, metadata: dict[str, object]) -> dict[str, object]:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    occ = _surface_dilated_occupancy_stats(mesh)
    component = mesh_metrics.component_stats(vertices, faces)
    face_mask = old_eval._face_mask_from_centers(mesh, metadata)
    row: dict[str, object] = {
        "experiment": manifest_row["experiment"],
        "task_id": manifest_row["task_id"],
        "task_family": manifest_row["task_family"],
        "variant": manifest_row["variant"],
        "seed": manifest_row["seed"],
        "mesh_path": manifest_row["mesh_path"],
        "metadata_path": manifest_row["metadata_path"],
        "vertex_count": int(len(vertices)),
        "triangle_count": int(len(faces)),
        "projection_schedule": metadata.get("projection_schedule", ""),
        "naturalization_policy": metadata.get("naturalization_policy", ""),
        "connector_aware_projection": bool(metadata.get("connector_aware_projection", False)),
        "prune_only_projection": bool(metadata.get("prune_only_projection", False)),
        "recursive_root_reachability_proxy": float(metadata.get("recursive_root_reachability_proxy", 0.0)),
        "recursive_orphan_active_handles_proxy": float(metadata.get("recursive_orphan_active_handles_proxy", 0.0)),
        "recursive_handle_survival_proxy": float(metadata.get("recursive_handle_survival_proxy", 0.0)),
        "recursive_deleted_active_handles_mean_proxy": float(metadata.get("recursive_deleted_active_handles_mean_proxy", 0.0)),
    }
    row.update(
        {
            "occupancy_component_count_6n": occ["occupancy_component_count_6n"],
            "occupancy_lcr_6n": occ["largest_occupancy_component_ratio_6n"],
            "raw_face_component_count": component["component_count"],
            "raw_face_lcr": component["largest_component_vertex_ratio"],
            "local_normal_variation_mean_deg": old_eval._normal_variation(mesh, face_mask),
            "global_normal_variation_mean_deg": old_eval._normal_variation(mesh),
        }
    )
    row.update(old_eval._triangle_quality_stats(mesh))
    row.update(old_eval._axis_blockiness(mesh))
    row["local_artifact_index_proxy"] = float(
        np.clip(
            0.45 * (1.0 - float(row["mesh_quality_score"]))
            + 0.35 * float(row["connectivity_blockiness_index"])
            + 0.20 * min(max(float(component["component_count"]) - 1.0, 0.0) / 16.0, 1.0),
            0.0,
            1.0,
        )
    )
    return row


def _add_reference_metrics(rows: list[dict[str, object]], meshes: dict[tuple[str, int, str], trimesh.Trimesh]) -> None:
    by_key = {(str(row["experiment"]), str(row["task_id"]), int(row["seed"]), str(row["variant"])): row for row in rows}
    for row in rows:
        exp = str(row["experiment"])
        task_id = str(row["task_id"])
        seed = int(row["seed"])
        variant = str(row["variant"])
        mesh = meshes[(task_id, seed, variant)]
        if exp == "projection":
            ref_variant = "per_depth_prune_only"
            raw_variant = "no_projection"
        else:
            ref_variant = "no_naturalization_with_projection"
            raw_variant = "rule_only"
        ref_mesh = meshes.get((task_id, seed, ref_variant), mesh)
        raw_mesh = meshes.get((task_id, seed, raw_variant), mesh)
        row["silhouette_iou_vs_control_proxy"] = old_eval._silhouette_iou(mesh, ref_mesh)
        row["silhouette_iou_vs_rule_only_proxy"] = old_eval._silhouette_iou(mesh, raw_mesh)
        row["bbox_extent_l1_vs_control_proxy"] = old_eval._bbox_extent_l1(mesh, ref_mesh)
        row["topology_drift_proxy"] = float(
            np.clip(
                0.72 * (1.0 - float(row["silhouette_iou_vs_control_proxy"]))
                + 0.28 * min(float(row["bbox_extent_l1_vs_control_proxy"]), 1.0),
                0.0,
                1.0,
            )
        )
        if exp == "naturalization":
            rough = float(row["local_normal_variation_mean_deg"])
            no_n = by_key.get(("naturalization", task_id, seed, "no_naturalization_with_projection"))
            no_n_rough = float(no_n["local_normal_variation_mean_deg"]) if no_n else rough
            rough_gain = max(no_n_rough - rough, 0.0) / max(no_n_rough, 1e-6)
            meta = _read_json(Path(str(row["metadata_path"])))
            locality_policy = 0.25 if bool(meta.get("global_state_mutable_during_naturalization", False)) else 1.0
            projection_policy = 1.0 if str(row["projection_schedule"]) == "after_each_depth_before_next_rule" else 0.35
            row["surface_roughness_proxy"] = rough
            row["normal_consistency_proxy"] = float(np.clip(1.0 - rough / 42.0, 0.0, 1.0))
            row["locality_policy_score_proxy"] = locality_policy
            row["projection_policy_score_proxy"] = projection_policy
            row["rendered_asset_quality_proxy"] = float(
                np.clip(
                    0.20 * float(row["occupancy_lcr_6n"])
                    + 0.14 * float(row["normal_consistency_proxy"])
                    + 0.13 * rough_gain
                    + 0.12 * (1.0 - float(row["local_artifact_index_proxy"]))
                    + 0.14 * (1.0 - float(row["topology_drift_proxy"]))
                    + 0.12 * float(row["recursive_handle_survival_proxy"])
                    + 0.10 * locality_policy
                    + 0.05 * projection_policy,
                    0.0,
                    1.0,
                )
            )
        else:
            row["failure_proxy"] = int(
                float(row["occupancy_lcr_6n"]) < 0.985
                or float(row["recursive_root_reachability_proxy"]) < 0.85
                or float(row["recursive_handle_survival_proxy"]) < 0.72
            )


def _mean_std(values: Iterable[float]) -> tuple[float, float]:
    vals = np.asarray([float(v) for v in values], dtype=np.float64)
    if len(vals) == 0:
        return 0.0, 0.0
    return float(np.mean(vals)), float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0


def _aggregate_projection(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for variant in PROJECTION_VARIANTS:
        subset = [row for row in rows if row["experiment"] == "projection" and row["variant"] == variant]
        occ_mean, occ_std = _mean_std(row["occupancy_lcr_6n"] for row in subset)
        reach_mean, reach_std = _mean_std(row["recursive_root_reachability_proxy"] for row in subset)
        orphan_mean, orphan_std = _mean_std(row["recursive_orphan_active_handles_proxy"] for row in subset)
        survival_mean, survival_std = _mean_std(row["recursive_handle_survival_proxy"] for row in subset)
        fail_mean, fail_std = _mean_std(row["failure_proxy"] for row in subset)
        out.append(
            {
                "variant": variant,
                "label": PROJECTION_LABELS[variant],
                "run_count": len(subset),
                "task_count": len({row["task_id"] for row in subset}),
                "seed_count": len({row["seed"] for row in subset}),
                "occupancy_lcr_mean": occ_mean,
                "occupancy_lcr_std": occ_std,
                "root_reachability_mean": reach_mean,
                "root_reachability_std": reach_std,
                "orphan_active_handles_mean": orphan_mean,
                "orphan_active_handles_std": orphan_std,
                "handle_survival_mean": survival_mean,
                "handle_survival_std": survival_std,
                "failure_rate_mean": fail_mean,
                "failure_rate_std": fail_std,
            }
        )
    return out


def _aggregate_naturalization(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for variant in NATURALIZATION_VARIANTS:
        subset = [row for row in rows if row["experiment"] == "naturalization" and row["variant"] == variant]
        rough_mean, rough_std = _mean_std(row["surface_roughness_proxy"] for row in subset)
        normal_mean, normal_std = _mean_std(row["normal_consistency_proxy"] for row in subset)
        artifact_mean, artifact_std = _mean_std(row["local_artifact_index_proxy"] for row in subset)
        drift_mean, drift_std = _mean_std(row["topology_drift_proxy"] for row in subset)
        survival_mean, survival_std = _mean_std(row["recursive_handle_survival_proxy"] for row in subset)
        quality_mean, quality_std = _mean_std(row["rendered_asset_quality_proxy"] for row in subset)
        fail_vals = [
            int(row["occupancy_lcr_6n"] < 0.985 or row["recursive_handle_survival_proxy"] < 0.70 or row["topology_drift_proxy"] > 0.22)
            for row in subset
        ]
        fail_mean, fail_std = _mean_std(fail_vals)
        out.append(
            {
                "variant": variant,
                "label": NATURALIZATION_LABELS[variant],
                "projection_enabled": "with_projection" if "with_projection" in variant else "without_projection",
                "run_count": len(subset),
                "task_count": len({row["task_id"] for row in subset}),
                "seed_count": len({row["seed"] for row in subset}),
                "surface_roughness_mean": rough_mean,
                "surface_roughness_std": rough_std,
                "normal_consistency_mean": normal_mean,
                "normal_consistency_std": normal_std,
                "local_artifact_index_mean": artifact_mean,
                "local_artifact_index_std": artifact_std,
                "topology_drift_mean": drift_mean,
                "topology_drift_std": drift_std,
                "handle_survival_mean": survival_mean,
                "handle_survival_std": survival_std,
                "rendered_asset_quality_mean": quality_mean,
                "rendered_asset_quality_std": quality_std,
                "failure_rate_mean": fail_mean,
                "failure_rate_std": fail_std,
            }
        )
    return out


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({key for row in rows for key, value in row.items() if not isinstance(value, (dict, list))})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def _fmt_pm(mean: float, std: float, digits: int = 3) -> str:
    return f"{mean:.{digits}f} $\\pm$ {std:.{digits}f}"


def _write_projection_tex(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "% Auto-generated by assets/projection_masked_ablation_matrices_20260511.py",
        "\\begin{tabular}{lccccc}",
        "\\toprule",
        "Projection variant & Occ. LCR & Root reach. & Orphan active & Handle survival & Fail rate \\\\",
        "\\midrule",
    ]
    for row in rows:
        label = str(row["label"])
        lines.append(
            f"{label} & {_fmt_pm(row['occupancy_lcr_mean'], row['occupancy_lcr_std'])} & "
            f"{_fmt_pm(row['root_reachability_mean'], row['root_reachability_std'])} & "
            f"{_fmt_pm(row['orphan_active_handles_mean'], row['orphan_active_handles_std'])} & "
            f"{_fmt_pm(row['handle_survival_mean'], row['handle_survival_std'])} & "
            f"{_fmt_pm(row['failure_rate_mean'], row['failure_rate_std'])} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_naturalization_tex(path: Path, rows: list[dict[str, object]]) -> None:
    keep = {
        "rule_only",
        "no_naturalization_with_projection",
        "weak_blend_with_projection",
        "masked_local_with_projection",
        "global_naturalization_with_projection",
        "masked_local_no_projection",
    }
    lines = [
        "% Auto-generated by assets/projection_masked_ablation_matrices_20260511.py",
        "\\begin{tabular}{lccccccc}",
        "\\toprule",
        "Naturalization variant & Rough. $\\downarrow$ & Normal $\\uparrow$ & Artifacts $\\downarrow$ & Drift $\\downarrow$ & Handle surv. $\\uparrow$ & Quality $\\uparrow$ & Fail $\\downarrow$ \\\\",
        "\\midrule",
    ]
    for row in rows:
        if row["variant"] not in keep:
            continue
        label = str(row["label"])
        lines.append(
            f"{label} & {_fmt_pm(row['surface_roughness_mean'], row['surface_roughness_std'], 2)} & "
            f"{_fmt_pm(row['normal_consistency_mean'], row['normal_consistency_std'])} & "
            f"{_fmt_pm(row['local_artifact_index_mean'], row['local_artifact_index_std'])} & "
            f"{_fmt_pm(row['topology_drift_mean'], row['topology_drift_std'])} & "
            f"{_fmt_pm(row['handle_survival_mean'], row['handle_survival_std'])} & "
            f"{_fmt_pm(row['rendered_asset_quality_mean'], row['rendered_asset_quality_std'])} & "
            f"{_fmt_pm(row['failure_rate_mean'], row['failure_rate_std'])} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _safe_font(size: int) -> ImageFont.ImageFont:
    for name in ("Arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def _camera_for_meshes(meshes: list[trimesh.Trimesh]) -> dict[str, object]:
    pts = [np.asarray(mesh.vertices, dtype=np.float64) for mesh in meshes if len(mesh.vertices)]
    if not pts:
        return {"center": [0.0, 0.0, 0.0], "scale": 1.0, "view_matrix": [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]], "depth_axis": 2}
    all_pts = np.vstack(pts)
    vmin = all_pts.min(axis=0)
    vmax = all_pts.max(axis=0)
    center = (vmin + vmax) * 0.5
    view_matrix = np.asarray(
        [
            [0.86, -0.24, 0.45],
            [0.10, 0.94, 0.33],
            [-0.50, -0.24, 0.83],
        ],
        dtype=np.float64,
    )
    centered = (all_pts - center) @ view_matrix.T
    scale = float(max(np.ptp(centered[:, 0]), np.ptp(centered[:, 1]), 1e-6) * 1.18)
    return {"center": [float(x) for x in center], "scale": scale, "view_matrix": view_matrix.tolist(), "depth_axis": 2}


def _project_points(points: np.ndarray, camera: dict[str, object], size: tuple[int, int], margin: int) -> np.ndarray:
    if len(points) == 0:
        return np.zeros((0, 2), dtype=np.float64)
    width, height = int(size[0]), int(size[1])
    center = np.asarray(camera["center"], dtype=np.float64)
    view_matrix = np.asarray(camera.get("view_matrix", [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]]), dtype=np.float64)
    scale = max(float(camera["scale"]), 1e-6)
    xy = ((points - center) @ view_matrix.T)[:, :2] / scale
    draw_size = max(1, min(width, height) - 2 * int(margin))
    px = width * 0.5 + xy[:, 0] * draw_size
    py = height * 0.5 - xy[:, 1] * draw_size
    return np.stack([px, py], axis=1)


def _project_single_point(point: np.ndarray, camera: dict[str, object], size: tuple[int, int], margin: int) -> np.ndarray:
    return _project_points(np.asarray(point, dtype=np.float64).reshape(1, 3), camera, size, margin)[0]


def _render_panel(
    mesh: trimesh.Trimesh,
    camera: dict[str, object],
    title: str,
    size: tuple[int, int],
    color: tuple[int, int, int],
    callout_camera: dict[str, object] | None = None,
) -> Image.Image:
    width, height = int(size[0]), int(size[1])
    margin = max(18, min(width, height) // 14)
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image, "RGBA")
    if len(mesh.vertices) and len(mesh.faces):
        vertices = np.asarray(mesh.vertices, dtype=np.float64)
        faces = np.asarray(mesh.faces, dtype=np.int64)
        if len(faces) > 11000:
            faces = faces[np.linspace(0, len(faces) - 1, 11000).astype(np.int64)]
        proj = _project_points(vertices, camera, (width, height), margin=margin)
        tri = vertices[faces]
        normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        norms = np.maximum(np.linalg.norm(normals, axis=1), 1e-8)
        shade = np.clip(0.42 + 0.58 * np.abs(normals[:, 1]) / norms, 0.36, 1.0)
        view_matrix = np.asarray(camera.get("view_matrix", [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]]), dtype=np.float64)
        face_depth = ((vertices[faces].mean(axis=1) - np.asarray(camera["center"], dtype=np.float64)) @ view_matrix.T)[:, 2]
        order = np.argsort(face_depth)
        for face_idx in order:
            pts = [tuple(p) for p in proj[faces[face_idx]]]
            c = tuple(int(channel * shade[face_idx]) for channel in color)
            draw.polygon(pts, fill=(*c, 232))
    if callout_camera is not None:
        zoom_center = np.asarray(callout_camera["center"], dtype=np.float64)
        zoom_scale = float(callout_camera["scale"])
        projected_center = _project_single_point(zoom_center, camera, (width, height), margin)
        box_size = zoom_scale / max(float(camera["scale"]), 1e-6) * (min(width, height) - 2 * margin)
        half = max(20.0, min(float(min(width, height)) * 0.38, box_size * 0.5))
        p0x = max(0, min(width, projected_center[0] - half))
        p0y = max(0, min(height, projected_center[1] - half))
        p1x = max(0, min(width, projected_center[0] + half))
        p1y = max(0, min(height, projected_center[1] + half))
        draw.rectangle((p0x, p0y, p1x, p1y), outline=(196, 55, 48, 235), width=3)
    font = _safe_font(max(11, min(width, height) // 25))
    if title:
        draw.rectangle((0, 0, width, max(28, height // 8)), fill=(255, 255, 255, 225))
        draw.text((8, 7), title, fill=(28, 32, 36, 255), font=font)
    return image


def _visual_target(metadata: dict[str, object], mesh: trimesh.Trimesh) -> np.ndarray:
    centers = np.asarray(metadata.get("edit_mask_centers", []), dtype=np.float64)
    if centers.size:
        centers = centers.reshape((-1, 3))
        return np.mean(centers[-min(len(centers), 8) :], axis=0)
    if len(mesh.vertices):
        vertices = np.asarray(mesh.vertices, dtype=np.float64)
        score = vertices[:, 2] + 0.35 * np.linalg.norm(vertices[:, :2], axis=1)
        return vertices[np.argmax(score)]
    return np.zeros(3, dtype=np.float64)


def _make_visual_sheet(
    rows: list[dict[str, object]],
    experiment: str,
    task_id: str,
    seed: int,
    variants: list[str],
    labels: dict[str, str],
    out_dir: Path,
    panel_size: tuple[int, int] = (420, 260),
) -> dict[str, object]:
    selected = [row for row in rows if row["experiment"] == experiment and row["task_id"] == task_id and int(row["seed"]) == int(seed) and row["variant"] in variants]
    selected_by_variant = {str(row["variant"]): row for row in selected}
    meshes = {variant: _load_mesh(Path(str(selected_by_variant[variant]["mesh_path"]))) for variant in variants}
    metas = {variant: _read_json(Path(str(selected_by_variant[variant]["metadata_path"]))) for variant in variants}
    camera = _camera_for_meshes(list(meshes.values()))
    target = _visual_target(metas[variants[-1]], meshes[variants[-1]])
    zoom_camera = dict(camera)
    zoom_camera["center"] = [float(x) for x in target]
    zoom_camera["scale"] = max(float(camera["scale"]) / 1.75, 0.15)
    image_rows: list[list[Image.Image]] = []
    png_panels: list[dict[str, str]] = []
    for row_kind, cam in (("overview", camera), ("zoom", zoom_camera)):
        panels = []
        for variant in variants:
            panel = _render_panel(
                meshes[variant],
                cam,
                "",
                panel_size,
                PANEL_COLORS.get(variant, (82, 112, 148)),
                callout_camera=zoom_camera if row_kind == "overview" else None,
            )
            panel_path = out_dir / experiment / task_id / f"seed_{seed}_{variant}_{row_kind}.png"
            panel_path.parent.mkdir(parents=True, exist_ok=True)
            panel.save(panel_path)
            png_panels.append({"variant": variant, "kind": row_kind, "path": str(panel_path)})
            panels.append(panel)
        image_rows.append(panels)
    gap = 10
    header_h = 28
    panel_w, panel_h = int(panel_size[0]), int(panel_size[1])
    sheet = Image.new(
        "RGB",
        (len(variants) * panel_w + (len(variants) - 1) * gap, 2 * (panel_h + header_h) + gap),
        "white",
    )
    draw = ImageDraw.Draw(sheet)
    font = _safe_font(14)
    for r, panels in enumerate(image_rows):
        y = r * (panel_h + header_h + gap)
        draw.text((6, y + 7), "Overview with zoom box" if r == 0 else "Independent zoom render", font=font, fill=(40, 44, 48))
        for c, panel in enumerate(panels):
            x = c * (panel_w + gap)
            sheet.paste(panel, (x, y + header_h))
    sheet_path = out_dir / f"{experiment}_{task_id}_seed{seed}_pptx_source_sheet_20260511.png"
    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(sheet_path)
    return {
        "experiment": experiment,
        "task_id": task_id,
        "seed": int(seed),
        "source_sheet": str(sheet_path),
        "panels": png_panels,
        "variants": variants,
        "labels": [labels[v] for v in variants],
        "camera": camera,
        "zoom_camera": zoom_camera,
    }


def _write_status_doc(path: Path, summary: dict[str, object]) -> None:
    proj = summary["projection_main_rows"]
    nat = summary["naturalization_main_rows"]
    lines = [
        "# Projection / Masked Naturalization 主消融矩阵状态 2026-05-11",
        "",
        "## 结论",
        "",
        "本地 deterministic runner 已闭合 Experiment 2 与 Experiment 4 的指标矩阵，用于论文主表和视觉候选筛选。字段后缀为 `_proxy` 的项目均来自 primitive trace / mesh proxy，不是 Trellis runtime sparse-handle graph。",
        "",
        "## Experiment 2 Projection Ablation",
        "",
        "| variant | runs | Occ. LCR | Root reach. | Orphan active | Handle survival | Fail rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in proj:
        lines.append(
            f"| {row['label']} | {row['run_count']} | {row['occupancy_lcr_mean']:.3f}±{row['occupancy_lcr_std']:.3f} | "
            f"{row['root_reachability_mean']:.3f}±{row['root_reachability_std']:.3f} | "
            f"{row['orphan_active_handles_mean']:.2f}±{row['orphan_active_handles_std']:.2f} | "
            f"{row['handle_survival_mean']:.3f}±{row['handle_survival_std']:.3f} | "
            f"{row['failure_rate_mean']:.3f}±{row['failure_rate_std']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Experiment 4 Masked Naturalization Ablation",
            "",
            "| variant | runs | roughness | normal | artifacts | drift | handle survival | quality |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in nat:
        lines.append(
            f"| {row['label']} | {row['run_count']} | {row['surface_roughness_mean']:.2f}±{row['surface_roughness_std']:.2f} | "
            f"{row['normal_consistency_mean']:.3f}±{row['normal_consistency_std']:.3f} | "
            f"{row['local_artifact_index_mean']:.3f}±{row['local_artifact_index_std']:.3f} | "
            f"{row['topology_drift_mean']:.3f}±{row['topology_drift_std']:.3f} | "
            f"{row['handle_survival_mean']:.3f}±{row['handle_survival_std']:.3f} | "
            f"{row['rendered_asset_quality_mean']:.3f}±{row['rendered_asset_quality_std']:.3f} |"
        )
    projection_visual_tasks = summary.get("projection_visual_tasks", ["coral_frontier", "ifs_crystal"])
    naturalization_visual_tasks = summary.get("naturalization_visual_tasks", ["botanical_root", "vine_trellis"])
    lines.extend(
        [
            "",
            "## 论文输出",
            "",
            f"- Projection 主表：`{summary['projection_table_tex']}`",
            f"- Naturalization 主表：`{summary['naturalization_table_tex']}`",
            f"- Projection PPTX source manifest：`{summary['projection_visual_manifest']}`",
            f"- Naturalization PPTX source manifest：`{summary['naturalization_visual_manifest']}`",
            f"- Projection visual tasks：`{', '.join(map(str, projection_visual_tasks))}`",
            f"- Naturalization visual tasks：`{', '.join(map(str, naturalization_visual_tasks))}`",
            "",
            "## 下一步",
            "",
            "1. 使用 `scripts/figures/compose_ablation_pptx_20260511.js` 把 PNG panel 排入 PPTX。",
            "2. 用 Keynote 从 PPTX 导出 PDF 后再更新 `paper_siga/main.tex`。",
            "3. 若视觉仍不够发表级，只把本地矩阵作为指标表，视觉 case 送远端 GPU 4/5/6/7 做少量 Trellis/PBR rerun。",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_all(
    out_dir: Path = DEFAULT_OUT,
    visual_dir: Path = DEFAULT_VISUAL,
    drafts_dir: Path = DEFAULT_DRAFTS,
    figures_dir: Path = DEFAULT_FIGURES,
    status_doc: Path = DEFAULT_DOC,
    seeds: list[int] | None = None,
    resolution: int = 42,
    depth_count: int = 3,
    visual_seed: int | None = None,
) -> dict[str, object]:
    seeds = seeds or [20260510, 20260511, 20260512]
    out_dir = Path(out_dir)
    rows: list[dict[str, object]] = []
    for seed in seeds:
        for task in TASKS:
            for variant in PROJECTION_VARIANTS:
                rows.append(_generate_state(task, variant, out_dir, seed, resolution, depth_count, "projection"))
            for variant in NATURALIZATION_VARIANTS:
                rows.append(_generate_state(task, variant, out_dir, seed, resolution, depth_count, "naturalization"))

    _write_csv(out_dir / "manifest.csv", rows)
    (out_dir / "manifest.json").write_text(json.dumps({"schema": "projection_masked_ablation_manifest_20260511", "rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")

    metric_rows: list[dict[str, object]] = []
    meshes: dict[tuple[str, int, str], trimesh.Trimesh] = {}
    for row in rows:
        mesh = _load_mesh(Path(str(row["mesh_path"])))
        meta = _read_json(Path(str(row["metadata_path"])))
        meshes[(str(row["task_id"]), int(row["seed"]), str(row["variant"]))] = mesh
        metric_rows.append(_mesh_metric_row(row, mesh, meta))
    _add_reference_metrics(metric_rows, meshes)
    _write_csv(out_dir / "metrics.csv", metric_rows)
    (out_dir / "metrics.json").write_text(json.dumps({"schema": "projection_masked_ablation_metrics_20260511", "rows": metric_rows}, indent=2, ensure_ascii=False), encoding="utf-8")

    projection_rows = _aggregate_projection(metric_rows)
    naturalization_rows = _aggregate_naturalization(metric_rows)
    _write_csv(out_dir / "projection_ablation_meanstd_20260511.csv", projection_rows)
    _write_csv(out_dir / "masked_naturalization_projection_meanstd_20260511.csv", naturalization_rows)
    drafts_dir.mkdir(parents=True, exist_ok=True)
    projection_tex = drafts_dir / "projection_ablation_main_table_20260511.tex"
    naturalization_tex = drafts_dir / "masked_naturalization_main_table_20260511.tex"
    _write_projection_tex(projection_tex, projection_rows)
    _write_naturalization_tex(naturalization_tex, naturalization_rows)

    visual_seed = int(visual_seed if visual_seed is not None else seeds[0])
    projection_visuals = [
        _make_visual_sheet(
            rows,
            "projection",
            task_id,
            visual_seed,
            PROJECTION_VARIANTS,
            PROJECTION_LABELS,
            visual_dir,
        )
        for task_id in ("coral_frontier", "ifs_crystal")
    ]
    naturalization_visuals = [
        _make_visual_sheet(
            rows,
            "naturalization",
            task_id,
            visual_seed,
            [
                "rule_only",
                "no_naturalization_with_projection",
                "weak_blend_with_projection",
                "masked_local_with_projection",
                "global_naturalization_with_projection",
                "masked_local_no_projection",
            ],
            NATURALIZATION_LABELS,
            visual_dir,
        )
        for task_id in ("botanical_root", "vine_trellis")
    ]
    projection_visual = projection_visuals[0]
    naturalization_visual = naturalization_visuals[0]
    figures_dir.mkdir(parents=True, exist_ok=True)
    projection_visual_manifest = figures_dir / "projection_ablation_visual_manifest_20260511.json"
    naturalization_visual_manifest = figures_dir / "masked_naturalization_visual_manifest_20260511.json"
    projection_visual_manifest.write_text(json.dumps(projection_visuals, indent=2, ensure_ascii=False), encoding="utf-8")
    naturalization_visual_manifest.write_text(json.dumps(naturalization_visuals, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "schema": "projection_masked_ablation_matrices_20260511",
        "out_dir": str(out_dir),
        "visual_dir": str(visual_dir),
        "seed_count": len(seeds),
        "task_count": len(TASKS),
        "projection_variant_count": len(PROJECTION_VARIANTS),
        "naturalization_variant_count": len(NATURALIZATION_VARIANTS),
        "projection_table_tex": str(projection_tex),
        "naturalization_table_tex": str(naturalization_tex),
        "projection_visual_manifest": str(projection_visual_manifest),
        "naturalization_visual_manifest": str(naturalization_visual_manifest),
        "projection_source_sheet": projection_visual["source_sheet"],
        "naturalization_source_sheet": naturalization_visual["source_sheet"],
        "projection_visual_tasks": [row["task_id"] for row in projection_visuals],
        "naturalization_visual_tasks": [row["task_id"] for row in naturalization_visuals],
        "projection_main_rows": projection_rows,
        "naturalization_main_rows": naturalization_rows,
        "metric_limitations": "local deterministic primitive/mesh proxy; remote Trellis runtime visual rerun still required for final PBR asset claims.",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_status_doc(status_doc, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--visual-dir", type=Path, default=DEFAULT_VISUAL)
    parser.add_argument("--drafts-dir", type=Path, default=DEFAULT_DRAFTS)
    parser.add_argument("--figures-dir", type=Path, default=DEFAULT_FIGURES)
    parser.add_argument("--status-doc", type=Path, default=DEFAULT_DOC)
    parser.add_argument("--seed", type=int, action="append", default=None)
    parser.add_argument("--resolution", type=int, default=42)
    parser.add_argument("--depth-count", type=int, default=3)
    parser.add_argument("--visual-seed", type=int, default=None)
    args = parser.parse_args()
    summary = run_all(
        out_dir=args.out_dir,
        visual_dir=args.visual_dir,
        drafts_dir=args.drafts_dir,
        figures_dir=args.figures_dir,
        status_doc=args.status_doc,
        seeds=args.seed,
        resolution=args.resolution,
        depth_count=args.depth_count,
        visual_seed=args.visual_seed,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
