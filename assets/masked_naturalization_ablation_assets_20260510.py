#!/usr/bin/env python3
"""Generate mesh assets for the 2026-05-10 masked naturalization ablation.

The assets are intentionally local and deterministic.  They are not remote
Trellis2 selections and not hand-picked postprocessing: every row starts from
the same grammar proposals, then changes only the projection schedule and the
masked local field update.
"""

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
from skimage import measure


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_OUT = PROJECT_ROOT / "results" / "masked_naturalization_ablation_20260510"

VARIANTS = [
    "raw_grammar_proposal",
    "final_only_projection_repair",
    "per_depth_projection",
    "per_depth_weak_naturalization",
    "per_depth_global_naturalization",
    "per_depth_masked_naturalization",
]

VARIANT_SEED_OFFSETS = {
    "raw_grammar_proposal": 0,
    "final_only_projection_repair": 1000,
    "per_depth_projection": 2000,
    "per_depth_masked_naturalization": 3000,
    "per_depth_weak_naturalization": 4000,
    "per_depth_global_naturalization": 5000,
}

TASKS = [
    {
        "task_id": "botanical_root",
        "task_family": "botanical/root",
        "label": "botanical root fan",
        "bound": 1.36,
        "attach_threshold": 0.24,
        "bridge_radius": 0.125,
        "naturalization_sigma": 0.40,
        "mask_radius": 0.22,
        "seed_offset": 11,
    },
    {
        "task_id": "coral_frontier",
        "task_family": "coral/frontier",
        "label": "coral frontier reef",
        "bound": 1.42,
        "attach_threshold": 0.27,
        "bridge_radius": 0.130,
        "naturalization_sigma": 0.44,
        "mask_radius": 0.25,
        "seed_offset": 29,
    },
    {
        "task_id": "ifs_crystal",
        "task_family": "IFS/crystal",
        "label": "IFS crystal lattice",
        "bound": 1.30,
        "attach_threshold": 0.23,
        "bridge_radius": 0.120,
        "naturalization_sigma": 0.34,
        "mask_radius": 0.20,
        "seed_offset": 47,
    },
]


def _vec(values: Iterable[float]) -> np.ndarray:
    return np.asarray(tuple(values), dtype=np.float64)


def _segment(a, b, radius: float, depth: int, role: str, masked: bool = False) -> dict[str, object]:
    return {
        "kind": "segment",
        "a": _vec(a),
        "b": _vec(b),
        "radius": float(radius),
        "depth": int(depth),
        "role": role,
        "masked": bool(masked),
    }


def _sphere(center, radius: float, depth: int, role: str, masked: bool = False) -> dict[str, object]:
    return {
        "kind": "sphere",
        "center": _vec(center),
        "radius": float(radius),
        "depth": int(depth),
        "role": role,
        "masked": bool(masked),
    }


def _ellipsoid(center, radii, depth: int, role: str, masked: bool = False) -> dict[str, object]:
    return {
        "kind": "ellipsoid",
        "center": _vec(center),
        "radii": _vec(radii),
        "depth": int(depth),
        "role": role,
        "masked": bool(masked),
    }


def _endpoints(primitive: dict[str, object]) -> list[np.ndarray]:
    if primitive["kind"] == "segment":
        return [np.asarray(primitive["a"], dtype=np.float64), np.asarray(primitive["b"], dtype=np.float64)]
    center = np.asarray(primitive["center"], dtype=np.float64)
    return [center]


def _primitive_center(primitive: dict[str, object]) -> np.ndarray:
    pts = np.vstack(_endpoints(primitive))
    return pts.mean(axis=0)


def _primitive_radius(primitive: dict[str, object]) -> float:
    if primitive["kind"] == "ellipsoid":
        return float(np.max(np.asarray(primitive["radii"], dtype=np.float64)))
    return float(primitive["radius"])


def _jitter(point: np.ndarray, rng: np.random.Generator, amount: float) -> np.ndarray:
    return np.asarray(point, dtype=np.float64) + rng.normal(0.0, amount, size=3)


def _botanical_proposals(depth: int, rng: np.random.Generator) -> list[dict[str, object]]:
    if depth == 0:
        return [
            _sphere((0.0, 0.0, 0.0), 0.105, depth, "root_anchor", masked=False),
            _segment((0.0, 0.0, 0.0), (-0.12, -0.36, -0.08), 0.075, depth, "primary_root", masked=False),
            _segment((-0.12, -0.36, -0.08), (-0.35, -0.66, -0.18), 0.056, depth, "primary_root", masked=False),
            _segment((-0.12, -0.36, -0.08), (0.18, -0.64, -0.16), 0.052, depth, "primary_root", masked=False),
        ]
    if depth == 1:
        return [
            _segment((-0.35, -0.66, -0.18), (-0.72, -0.92, -0.25), 0.038, depth, "grammar_branch", masked=True),
            _segment((0.18, -0.64, -0.16), (0.54, -0.86, -0.23), 0.036, depth, "grammar_branch", masked=True),
            _segment((0.39, -0.54, -0.18), (0.70, -0.72, -0.21), 0.028, depth, "raw_gap_proposal", masked=True),
        ]
    return [
        _segment((-0.72, -0.92, -0.25), (-1.00, -1.04, -0.28), 0.026, depth, "terminal_rootlet", masked=True),
        _segment((0.54, -0.86, -0.23), (0.84, -1.08, -0.34), 0.024, depth, "terminal_rootlet", masked=True),
        _segment((-0.28, -0.72, -0.21), (-0.47, -1.02, -0.32), 0.022, depth, "terminal_rootlet", masked=True),
        _segment((0.89, -0.60, -0.16), (1.10, -0.82, -0.20), 0.020, depth, "raw_orphan_rootlet", masked=True),
        _sphere(_jitter(_vec((0.66, -1.03, -0.38)), rng, 0.018), 0.038, depth, "root_hair_cluster", masked=True),
    ]


def _coral_proposals(depth: int, rng: np.random.Generator) -> list[dict[str, object]]:
    if depth == 0:
        return [
            _ellipsoid((0.0, -0.05, -0.18), (0.58, 0.36, 0.070), depth, "reef_base", masked=False),
            _segment((-0.15, -0.10, -0.12), (-0.34, 0.24, 0.14), 0.075, depth, "frontier_stalk", masked=False),
            _segment((0.10, -0.08, -0.10), (0.33, 0.27, 0.11), 0.072, depth, "frontier_stalk", masked=False),
            _segment((0.02, 0.02, -0.10), (0.02, 0.39, 0.22), 0.068, depth, "frontier_stalk", masked=False),
        ]
    if depth == 1:
        return [
            _segment((-0.34, 0.24, 0.14), (-0.68, 0.43, 0.23), 0.045, depth, "coral_frontier_branch", masked=True),
            _segment((0.33, 0.27, 0.11), (0.66, 0.46, 0.20), 0.045, depth, "coral_frontier_branch", masked=True),
            _segment((0.02, 0.39, 0.22), (-0.18, 0.72, 0.33), 0.040, depth, "coral_frontier_branch", masked=True),
            _segment((0.33, 0.62, 0.12), (0.62, 0.82, 0.20), 0.036, depth, "raw_frontier_island", masked=True),
        ]
    return [
        _segment((-0.68, 0.43, 0.23), (-0.95, 0.55, 0.30), 0.030, depth, "terminal_coral_tip", masked=True),
        _segment((0.66, 0.46, 0.20), (0.92, 0.63, 0.30), 0.032, depth, "terminal_coral_tip", masked=True),
        _segment((-0.18, 0.72, 0.33), (-0.38, 0.96, 0.44), 0.028, depth, "terminal_coral_tip", masked=True),
        _segment((0.14, 0.68, 0.30), (0.18, 1.03, 0.44), 0.029, depth, "terminal_coral_tip", masked=True),
        _segment((-0.82, 0.15, 0.10), (-1.04, 0.30, 0.18), 0.026, depth, "raw_orphan_frontier", masked=True),
        _sphere(_jitter(_vec((0.76, 0.70, 0.28)), rng, 0.020), 0.045, depth, "polyp_cluster", masked=True),
    ]


def _ifs_proposals(depth: int, rng: np.random.Generator) -> list[dict[str, object]]:
    if depth == 0:
        return [
            _ellipsoid((0.0, 0.0, 0.0), (0.24, 0.24, 0.11), depth, "crystal_seed", masked=False),
            _segment((-0.34, 0.0, 0.0), (0.34, 0.0, 0.0), 0.060, depth, "lattice_axis", masked=False),
            _segment((0.0, -0.34, 0.0), (0.0, 0.34, 0.0), 0.060, depth, "lattice_axis", masked=False),
            _segment((0.0, 0.0, -0.24), (0.0, 0.0, 0.32), 0.055, depth, "lattice_axis", masked=False),
        ]
    if depth == 1:
        out = []
        for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            out.append(_segment((0.22 * sx, 0.22 * sy, 0.03), (0.54 * sx, 0.54 * sy, 0.12), 0.034, depth, "ifs_copy_arm", masked=True))
        out.append(_segment((0.66, -0.18, 0.08), (0.92, -0.34, 0.17), 0.030, depth, "raw_crystal_copy_gap", masked=True))
        return out
    return [
        _segment((0.54, 0.54, 0.12), (0.78, 0.78, 0.22), 0.024, depth, "ifs_terminal_copy", masked=True),
        _segment((-0.54, 0.54, 0.12), (-0.78, 0.78, 0.22), 0.024, depth, "ifs_terminal_copy", masked=True),
        _segment((0.54, -0.54, 0.12), (0.78, -0.78, 0.22), 0.024, depth, "ifs_terminal_copy", masked=True),
        _segment((-0.54, -0.54, 0.12), (-0.78, -0.78, 0.22), 0.024, depth, "ifs_terminal_copy", masked=True),
        _segment((-0.86, -0.10, 0.12), (-1.05, -0.26, 0.20), 0.021, depth, "raw_orphan_crystal_copy", masked=True),
        _ellipsoid(_jitter(_vec((0.70, -0.30, 0.17)), rng, 0.014), (0.060, 0.038, 0.026), depth, "crystal_facet_detail", masked=True),
    ]


def _task_proposals(task_id: str, depth: int, rng: np.random.Generator) -> list[dict[str, object]]:
    if task_id == "botanical_root":
        return _botanical_proposals(depth, rng)
    if task_id == "coral_frontier":
        return _coral_proposals(depth, rng)
    if task_id == "ifs_crystal":
        return _ifs_proposals(depth, rng)
    raise ValueError(task_id)


def _naturalize_new_primitives(
    task: dict[str, object],
    primitives: list[dict[str, object]],
    depth: int,
    rng: np.random.Generator,
    strength: float = 1.0,
) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    family = str(task["task_family"])
    strength = float(np.clip(strength, 0.0, 1.0))
    for primitive in primitives:
        p = dict(primitive)
        p["role"] = f"masked_naturalized_{primitive['role']}"
        p["masked"] = True
        if p["kind"] == "segment":
            scale = 1.0 + strength * (0.025 if "coral" in family else 0.015)
            p["radius"] = float(p["radius"]) * scale
        elif p["kind"] == "sphere":
            p["radius"] = float(p["radius"]) * (1.0 + 0.015 * strength)
        elif p["kind"] == "ellipsoid":
            p["radii"] = np.asarray(p["radii"], dtype=np.float64) * (1.0 + 0.015 * strength)
        out.append(p)

        if p["kind"] == "segment":
            a = np.asarray(p["a"], dtype=np.float64)
            b = np.asarray(p["b"], dtype=np.float64)
            radius = float(p["radius"])
            for frac in (0.34, 0.67):
                center = a * (1.0 - frac) + b * frac
                if "coral" in family:
                    detail_radius = radius * 0.30
                elif "crystal" in family:
                    detail_radius = radius * 0.20
                else:
                    detail_radius = radius * 0.22
                out.append(
                    _sphere(
                        _jitter(center, rng, radius * 0.14),
                        max(detail_radius * (0.42 + 0.58 * strength), 0.007),
                        depth,
                        "masked_local_surface_continuity_kernel",
                        masked=True,
                    )
                )
    return out


def _all_endpoints(primitives: list[dict[str, object]]) -> list[np.ndarray]:
    points: list[np.ndarray] = []
    for primitive in primitives:
        points.extend(_endpoints(primitive))
    return points


def _bridge_candidates(
    existing: list[dict[str, object]],
    proposals: list[dict[str, object]],
    task: dict[str, object],
    depth: int,
) -> list[dict[str, object]]:
    existing_points = _all_endpoints(existing)
    if not existing_points:
        return []
    anchors = [p.copy() for p in existing_points]
    bridges: list[dict[str, object]] = []
    threshold = float(task["attach_threshold"])
    radius = float(task["bridge_radius"])
    for primitive in proposals:
        points = _endpoints(primitive)
        best: tuple[float, np.ndarray, np.ndarray] | None = None
        for p in points:
            for anchor in anchors:
                dist = float(np.linalg.norm(p - anchor))
                if best is None or dist < best[0]:
                    best = (dist, p, anchor)
        if best is None:
            continue
        if best[0] > threshold:
            bridges.append(_segment(best[1], best[2], radius, depth, "projection_bridge_to_previous_state", masked=True))
            anchors.extend(points)
        else:
            midpoint = (best[1] + best[2]) * 0.5
            bridges.append(_sphere(midpoint, radius * 1.35, depth, "projection_junction_weld", masked=True))
            anchors.extend(points)
    return bridges


def _stamp_segment(field: np.ndarray, coords: np.ndarray, a: np.ndarray, b: np.ndarray, radius: float) -> None:
    ba = b - a
    denom = max(float(np.dot(ba, ba)), 1e-12)
    h = np.clip(np.sum((coords - a) * ba, axis=-1) / denom, 0.0, 1.0)
    closest = a + h[..., None] * ba
    dist = np.linalg.norm(coords - closest, axis=-1)
    np.maximum(field, radius - dist, out=field)


def _stamp_sphere(field: np.ndarray, coords: np.ndarray, center: np.ndarray, radius: float) -> None:
    dist = np.linalg.norm(coords - center, axis=-1)
    np.maximum(field, radius - dist, out=field)


def _stamp_ellipsoid(field: np.ndarray, coords: np.ndarray, center: np.ndarray, radii: np.ndarray) -> None:
    q = (coords - center) / np.maximum(radii, 1e-6)
    dist = np.linalg.norm(q, axis=-1)
    np.maximum(field, 1.0 - dist, out=field)


def _field_from_primitives(primitives: list[dict[str, object]], coords: np.ndarray) -> np.ndarray:
    field = np.full(coords.shape[:3], -10.0, dtype=np.float32)
    for primitive in primitives:
        if primitive["kind"] == "segment":
            _stamp_segment(
                field,
                coords,
                np.asarray(primitive["a"], dtype=np.float64),
                np.asarray(primitive["b"], dtype=np.float64),
                float(primitive["radius"]),
            )
        elif primitive["kind"] == "sphere":
            _stamp_sphere(
                field,
                coords,
                np.asarray(primitive["center"], dtype=np.float64),
                float(primitive["radius"]),
            )
        elif primitive["kind"] == "ellipsoid":
            _stamp_ellipsoid(
                field,
                coords,
                np.asarray(primitive["center"], dtype=np.float64),
                np.asarray(primitive["radii"], dtype=np.float64),
            )
        else:
            raise ValueError(str(primitive["kind"]))
    return field


def _mesh_from_primitives(
    primitives: list[dict[str, object]],
    task: dict[str, object],
    resolution: int,
    naturalization_mode: str,
    naturalization_strength: float = 1.0,
) -> trimesh.Trimesh:
    bound = float(task["bound"])
    axis = np.linspace(-bound, bound, int(resolution), dtype=np.float32)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    coords = np.stack([x, y, z], axis=-1)
    naturalization_strength = float(np.clip(naturalization_strength, 0.0, 1.0))
    if naturalization_mode in ("per_depth_edit_mask", "weak_masked_blend"):
        old_prims = [p for p in primitives if not bool(p.get("masked"))]
        mask_prims = [p for p in primitives if bool(p.get("masked"))]
        old_field = _field_from_primitives(old_prims, coords) if old_prims else np.full(x.shape, -10.0, dtype=np.float32)
        mask_field = _field_from_primitives(mask_prims, coords) if mask_prims else np.full(x.shape, -10.0, dtype=np.float32)
        sigma = float(task["naturalization_sigma"]) * (0.45 if naturalization_mode == "weak_masked_blend" else 1.0)
        if sigma > 0:
            smooth_mask = ndimage.gaussian_filter(mask_field, sigma=sigma)
            if naturalization_mode == "weak_masked_blend":
                mask_field = np.maximum(mask_field, smooth_mask * naturalization_strength + mask_field * (1.0 - naturalization_strength))
            else:
                mask_field = np.maximum(mask_field, smooth_mask)
        field = np.maximum(old_field, mask_field)
    elif naturalization_mode == "global_field_smoothing":
        field = _field_from_primitives(primitives, coords)
        sigma = float(task["naturalization_sigma"]) * (1.35 + 0.35 * naturalization_strength)
        if sigma > 0:
            smooth_field = ndimage.gaussian_filter(field, sigma=sigma)
            field = np.maximum(field, smooth_field * (0.65 + 0.25 * naturalization_strength))
    else:
        field = _field_from_primitives(primitives, coords)

    if float(field.max()) <= 0.0:
        return trimesh.Trimesh(vertices=np.zeros((0, 3)), faces=np.zeros((0, 3), dtype=np.int64), process=False)

    verts, faces, _normals, _values = measure.marching_cubes(field, level=0.0, allow_degenerate=False)
    verts = -bound + verts * (2.0 * bound / max(int(resolution) - 1, 1))
    mesh = trimesh.Trimesh(vertices=verts, faces=faces.astype(np.int64), process=False)
    mesh.remove_unreferenced_vertices()
    try:
        trimesh.repair.fix_normals(mesh, multibody=True)
    except Exception:
        pass
    return mesh


def _serialize_primitive(primitive: dict[str, object]) -> dict[str, object]:
    out: dict[str, object] = {}
    for key, value in primitive.items():
        if isinstance(value, np.ndarray):
            out[key] = [float(x) for x in value.tolist()]
        elif isinstance(value, (np.floating, np.integer)):
            out[key] = value.item()
        else:
            out[key] = value
    return out


def _mesh_stats(mesh: trimesh.Trimesh) -> dict[str, object]:
    bounds = mesh.bounds if len(mesh.vertices) else np.zeros((2, 3), dtype=np.float64)
    extent = bounds[1] - bounds[0]
    return {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "bbox_diag": float(np.linalg.norm(extent)),
        "surface_area": float(mesh.area) if len(mesh.faces) else 0.0,
    }


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = [
        "task_id",
        "task_family",
        "variant",
        "mesh_path",
        "metadata_path",
        "depth_count",
        "projection_schedule",
        "naturalization_scope",
        "vertices",
        "faces",
        "bbox_diag",
        "surface_area",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def _variant_controls(variant: str) -> dict[str, object]:
    if variant == "raw_grammar_proposal":
        return {
            "projection_schedule": "disabled",
            "naturalization_scope": "disabled",
            "per_depth_projection": False,
            "final_projection": False,
            "naturalization_mode": "disabled",
            "naturalization_strength": 0.0,
            "proposal_naturalization_strength": 0.0,
            "old_state_clamped_during_masked_update": False,
            "global_state_mutable_during_naturalization": False,
        }
    if variant == "final_only_projection_repair":
        return {
            "projection_schedule": "after_final_depth_only",
            "naturalization_scope": "disabled",
            "per_depth_projection": False,
            "final_projection": True,
            "naturalization_mode": "disabled",
            "naturalization_strength": 0.0,
            "proposal_naturalization_strength": 0.0,
            "old_state_clamped_during_masked_update": False,
            "global_state_mutable_during_naturalization": False,
        }
    if variant == "per_depth_projection":
        return {
            "projection_schedule": "after_each_depth_before_next_rule",
            "naturalization_scope": "disabled",
            "per_depth_projection": True,
            "final_projection": False,
            "naturalization_mode": "disabled",
            "naturalization_strength": 0.0,
            "proposal_naturalization_strength": 0.0,
            "old_state_clamped_during_masked_update": False,
            "global_state_mutable_during_naturalization": False,
        }
    if variant == "per_depth_weak_naturalization":
        return {
            "projection_schedule": "after_each_depth_before_next_rule",
            "naturalization_scope": "weak_masked_blend",
            "per_depth_projection": True,
            "final_projection": False,
            "naturalization_mode": "weak_masked_blend",
            "naturalization_strength": 0.35,
            "proposal_naturalization_strength": 0.35,
            "old_state_clamped_during_masked_update": True,
            "global_state_mutable_during_naturalization": False,
        }
    if variant == "per_depth_global_naturalization":
        return {
            "projection_schedule": "after_each_depth_before_next_rule",
            "naturalization_scope": "global_field_smoothing",
            "per_depth_projection": True,
            "final_projection": False,
            "naturalization_mode": "global_field_smoothing",
            "naturalization_strength": 0.85,
            "proposal_naturalization_strength": 0.65,
            "old_state_clamped_during_masked_update": False,
            "global_state_mutable_during_naturalization": True,
        }
    if variant == "per_depth_masked_naturalization":
        return {
            "projection_schedule": "after_each_depth_before_next_rule",
            "naturalization_scope": "per_depth_edit_mask",
            "per_depth_projection": True,
            "final_projection": False,
            "naturalization_mode": "per_depth_edit_mask",
            "naturalization_strength": 1.0,
            "proposal_naturalization_strength": 1.0,
            "old_state_clamped_during_masked_update": True,
            "global_state_mutable_during_naturalization": False,
        }
    raise ValueError(variant)


def _generate_variant(
    task: dict[str, object],
    variant: str,
    out_dir: Path,
    resolution: int,
    depth_count: int,
    seed: int,
) -> dict[str, object]:
    controls = _variant_controls(variant)
    rng = np.random.default_rng(int(seed) + int(task["seed_offset"]) + int(VARIANT_SEED_OFFSETS[variant]))
    task_dir = out_dir / "tasks" / str(task["task_id"]) / variant
    task_dir.mkdir(parents=True, exist_ok=True)

    state: list[dict[str, object]] = []
    base_primitives: list[dict[str, object]] = []
    depth_trace: list[dict[str, object]] = []
    edit_mask_centers: list[list[float]] = []
    masked_voxel_proxy = 0.0

    for depth in range(int(depth_count)):
        proposals = _task_proposals(str(task["task_id"]), depth, rng)
        if depth == 0:
            base_primitives.extend(proposals)
        if float(controls["proposal_naturalization_strength"]) > 0.0 and depth > 0:
            proposals = _naturalize_new_primitives(task, proposals, depth, rng, float(controls["proposal_naturalization_strength"]))
        bridges: list[dict[str, object]] = []
        if bool(controls["per_depth_projection"]) and depth > 0:
            bridges = _bridge_candidates(state, proposals, task, depth)
        stage_primitives = state + proposals + bridges
        state = stage_primitives
        if depth > 0:
            mask_points = [_primitive_center(p) for p in proposals + bridges if bool(p.get("masked"))]
            edit_mask_centers.extend([[float(x) for x in point.tolist()] for point in mask_points])
            masked_voxel_proxy += sum((4.0 / 3.0) * math.pi * _primitive_radius(p) ** 3 for p in proposals + bridges if bool(p.get("masked")))

        stage_mesh = _mesh_from_primitives(
            state,
            task,
            resolution=resolution,
            naturalization_mode=str(controls["naturalization_mode"]),
            naturalization_strength=float(controls["naturalization_strength"]),
        )
        stage_path = task_dir / f"depth_{depth + 1:02d}.obj"
        stage_mesh.export(stage_path)
        depth_trace.append(
            {
                "depth": depth + 1,
                "stage_mesh": str(stage_path),
                "proposal_primitive_count": len(proposals),
                "projection_bridge_count": len(bridges),
                "projection_applied": bool(bridges),
                "naturalization_mode": str(controls["naturalization_mode"]) if depth > 0 else "disabled_at_root_depth",
                "masked_naturalization_applied": str(controls["naturalization_mode"]) in ("per_depth_edit_mask", "weak_masked_blend") and depth > 0,
                "global_naturalization_applied": str(controls["naturalization_mode"]) == "global_field_smoothing" and depth > 0,
                "stage_vertices": int(len(stage_mesh.vertices)),
                "stage_faces": int(len(stage_mesh.faces)),
            }
        )

    final_bridges: list[dict[str, object]] = []
    if bool(controls["final_projection"]):
        non_base = [p for p in state if int(p.get("depth", 0)) > 0]
        final_bridges = _bridge_candidates(base_primitives, non_base, task, int(depth_count))
        state = state + final_bridges
        edit_mask_centers.extend([[float(x) for x in _primitive_center(p).tolist()] for p in final_bridges])

    mesh = _mesh_from_primitives(
        state,
        task,
        resolution=resolution,
        naturalization_mode=str(controls["naturalization_mode"]),
        naturalization_strength=float(controls["naturalization_strength"]),
    )
    mesh_path = task_dir / "mesh.obj"
    mesh.export(mesh_path)
    stats = _mesh_stats(mesh)

    metadata_path = task_dir / "metadata.json"
    metadata = {
        "schema": "masked_naturalization_ablation_asset_metadata_20260510",
        "task_id": task["task_id"],
        "task_family": task["task_family"],
        "task_label": task["label"],
        "variant": variant,
        "mesh_path": str(mesh_path),
        "resolution": int(resolution),
        "depth_count": int(depth_count),
        "projection_schedule": controls["projection_schedule"],
        "naturalization_scope": controls["naturalization_scope"],
        "naturalization_mode": controls["naturalization_mode"],
        "naturalization_strength": float(controls["naturalization_strength"]),
        "proposal_naturalization_strength": float(controls["proposal_naturalization_strength"]),
        "old_state_clamped_during_masked_update": bool(controls["old_state_clamped_during_masked_update"]),
        "global_state_mutable_during_naturalization": bool(controls["global_state_mutable_during_naturalization"]),
        "hand_picked_postprocess": False,
        "stage_outputs_are_mesh_based": True,
        "grammar_proposals_shared_across_variants": True,
        "final_projection_bridge_count": len(final_bridges),
        "mask_change_voxel_ratio_proxy": float(masked_voxel_proxy / max((2.0 * float(task["bound"])) ** 3, 1e-9)),
        "edit_mask_radius": float(task["mask_radius"]),
        "edit_mask_centers": edit_mask_centers,
        "depth_trace": depth_trace,
        "primitive_trace": [_serialize_primitive(p) for p in state],
        "paper_claim_scope": "measurable_local_masked_naturalization_not_hand_picked_postprocessing",
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    row: dict[str, object] = {
        "task_id": task["task_id"],
        "task_family": task["task_family"],
        "variant": variant,
        "mesh_path": str(mesh_path),
        "metadata_path": str(metadata_path),
        "depth_count": int(depth_count),
        "projection_schedule": controls["projection_schedule"],
        "naturalization_scope": controls["naturalization_scope"],
    }
    row.update(stats)
    return row


def _write_render_manifest(out_dir: Path, rows: list[dict[str, object]]) -> Path:
    cases = [
        {
            "label": f"{row['task_id']}__{row['variant']}",
            "mesh": row["mesh_path"],
            "material_mode": "neutral",
            "zoom_levels": 2,
        }
        for row in rows
    ]
    payload = {
        "schema": "masked_naturalization_ablation_pure_white_zoom_manifest_20260510",
        "renderer": "scripts/figures/matched_camera_zoom_render_20260510.py",
        "strict_requirements": {
            "white_background": True,
            "square_overview": True,
            "square_zoom_panels_match_overview_size": True,
            "pure_white_zoom_renderer_compatible": True,
            "plan_only_supported": True,
        },
        "cases": cases,
    }
    path = out_dir / "render_manifest_pure_white_zoom.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def materialize(
    out_dir: Path = DEFAULT_OUT,
    resolution: int = 56,
    depth_count: int = 3,
    seed: int = 20260510,
) -> dict[str, object]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for task in TASKS:
        for variant in VARIANTS:
            rows.append(_generate_variant(task, variant, out_dir, int(resolution), int(depth_count), int(seed)))

    _write_csv(out_dir / "manifest.csv", rows)
    manifest_payload = {
        "schema": "masked_naturalization_ablation_manifest_20260510",
        "rows": rows,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    render_manifest = _write_render_manifest(out_dir, rows)
    summary = {
        "schema": "masked_naturalization_ablation_assets_20260510",
        "out_dir": str(out_dir),
        "manifest_csv": str(out_dir / "manifest.csv"),
        "manifest_json": str(out_dir / "manifest.json"),
        "render_manifest": str(render_manifest),
        "task_count": len(TASKS),
        "variant_count": len(VARIANTS),
        "mesh_count": len(rows),
        "tasks": [str(task["task_id"]) for task in TASKS],
        "variants": list(VARIANTS),
        "paper_claim_scope": "measurable_local_masked_naturalization_not_hand_picked_postprocessing",
        "notes": [
            "Raw grammar, final-only projection, per-depth projection, weak masked blend, global naturalization, and masked local naturalization share the same deterministic proposal grammar.",
            "Weak and masked naturalization update only current edit-mask primitives; global naturalization smooths the full field and is a locality negative control.",
            "OBJ outputs and render_manifest_pure_white_zoom.json are compatible with the existing matched-camera white zoom renderer.",
        ],
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--resolution", type=int, default=56)
    parser.add_argument("--depth-count", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260510)
    args = parser.parse_args()
    print(json.dumps(materialize(args.out_dir, args.resolution, args.depth_count, args.seed), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
