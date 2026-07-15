#!/usr/bin/env python3
"""Prepare connected per-depth logarithmic-spiral and fern roots for 12o.

12i showed that repeated sparse-latent patch translations create detached dust.
This script moves recursive structure construction back into mesh space, where
every displayed depth is explicitly connected before TRELLIS2 encodes/decodes it.
The remote runner then applies a passthrough SLat decode as naturalization.

12o keeps the user correction that the fiddlehead case must contain no long
support/stem rods.  It thickens the main and child stems, adds local welded
collars, and introduces child-on-child log-spiral growth at depth 4/6.  The
compound fern lane is restored as a long frond candidate with conservative
connected mesh-stage depth changes before remote TRELLIS2/SLat naturalization.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import procedural_baselines as pb
from prepare_fern_root_candidates_20260511 import (
    _add_curved_tube_detail,
    _add_thick_lamina,
    _append_child,
    _counts,
    _dedupe_edges,
    _graph_edges,
    _mesh_stats,
    _node_axis,
    _normalize_nodes,
    _smooth_support_mesh,
    _unit,
)


DEFAULT_OUT = ROOT_DIR / "results" / "fern_depth_roots_20260512o"


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _export_obj(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


def _renormalize(mesh: pb.Mesh, extent: float = 2.95) -> None:
    arr = np.asarray(mesh.vertices, dtype=float)
    center = (arr.min(axis=0) + arr.max(axis=0)) * 0.5
    scale = max(float((arr.max(axis=0) - arr.min(axis=0)).max()), 1e-6)
    arr = (arr - center) * (float(extent) / scale)
    mesh.vertices = [tuple(map(float, v)) for v in arr]


def _add_tube(
    mesh: pb.Mesh,
    centers: List[int],
    nodes: List[np.ndarray],
    idx: int,
    direction: np.ndarray,
    length: float,
    radius: float,
    rng: np.random.Generator,
    curl: float = 0.12,
    segments: int = 6,
    sides: int = 8,
) -> None:
    _add_curved_tube_detail(
        mesh,
        centers[idx],
        nodes[idx],
        _unit(direction),
        float(length),
        float(radius),
        rng,
        segments=int(segments),
        sides=int(sides),
        curl=float(curl),
    )


def _curve_tube_from_points(
    points: List[np.ndarray],
    radii: List[float],
    sides: int = 18,
    ovality: float = 0.04,
) -> Tuple[pb.Mesh, List[int]]:
    if len(points) < 2:
        raise ValueError("curve tube requires at least two points")
    parents = [-1] + list(range(0, len(points) - 1))
    mesh = _smooth_support_mesh(points, _dedupe_edges(_graph_edges(parents)), radii, sides=sides, ovality=ovality)
    centers = list(getattr(mesh, "center_indices"))
    return mesh, centers


def _append_mesh_into(base: pb.Mesh, child: pb.Mesh) -> None:
    offset = len(base.vertices)
    base.vertices.extend(child.vertices)
    base.faces.extend([(a + offset, b + offset, c + offset) for a, b, c in child.faces])


def _append_mesh_into_with_offset(base: pb.Mesh, child: pb.Mesh) -> int:
    offset = len(base.vertices)
    _append_mesh_into(base, child)
    return offset


def _bridge_vertices(mesh: pb.Mesh, a_idx: int, b_idx: int, radius: float) -> None:
    a = np.asarray(mesh.vertices[a_idx - 1], dtype=float)
    b = np.asarray(mesh.vertices[b_idx - 1], dtype=float)
    if float(np.linalg.norm(b - a)) < 1e-8:
        b = a + np.array([0.0, 0.0, 1e-4], dtype=float)
    axis = _unit(b - a)
    u, v, _w = pb.basis_from_axis(axis)
    mid = (a + b) * 0.5
    r = max(float(radius), 1e-5)
    mesh.vertices.append(tuple(mid + u * r))
    p = len(mesh.vertices)
    mesh.vertices.append(tuple(mid - u * r))
    q = len(mesh.vertices)
    mesh.vertices.append(tuple(mid + v * r))
    r_idx = len(mesh.vertices)
    mesh.faces.append((a_idx, p, b_idx))
    mesh.faces.append((a_idx, b_idx, q))
    mesh.faces.append((a_idx, r_idx, b_idx))


def _add_welded_neck(
    mesh: pb.Mesh,
    *,
    anchor_idx: int,
    anchor: np.ndarray,
    target: np.ndarray,
    radius: float,
    rng: np.random.Generator,
    segments: int = 3,
    sides: int = 8,
) -> None:
    direction = _unit(np.asarray(target, dtype=float) - np.asarray(anchor, dtype=float))
    length = max(float(np.linalg.norm(np.asarray(target, dtype=float) - np.asarray(anchor, dtype=float))), 1e-4)
    _add_curved_tube_detail(
        mesh,
        anchor_idx,
        np.asarray(anchor, dtype=float),
        direction,
        length,
        max(float(radius), 0.004),
        rng,
        segments=int(segments),
        sides=int(sides),
        curl=0.0,
    )


def _add_child_on_child_spiral(
    mesh: pb.Mesh,
    child_points: List[np.ndarray],
    child_centers: List[int],
    child_radii: List[float],
    idx: int,
    *,
    depth: int,
    child_rank: int,
    rng: np.random.Generator,
    variant: str,
) -> int:
    if not (2 <= idx < len(child_points) - 4):
        return 0
    tangent, radial, normal = _frame_at(child_points, idx, np.asarray(child_points[0], dtype=float))
    side = -1.0 if child_rank % 2 else 1.0
    scale = (0.078 if variant in ("surface", "open") else 0.070) * (1.0 + 0.015 * depth)
    turns = 0.54 + 0.05 * ((child_rank + depth) % 3)
    steps = 18 if depth < 6 else 20
    r0 = 0.56
    r_min = 0.145
    anchor = np.asarray(child_points[idx], dtype=float)
    clearance = max(child_radii[idx] * 0.42, 0.0048)
    theta_start = side * (0.22 + 0.04 * (child_rank % 3)) + rng.uniform(-0.04, 0.04)
    theta_span = turns * math.tau
    log_b = math.log(r0 / r_min) / max(theta_span, 1e-6)
    start_x = r0 * math.cos(theta_start)
    start_y = r0 * math.sin(theta_start)
    grand_points: List[np.ndarray] = []
    for q in range(steps):
        t = q / float(max(steps - 1, 1))
        theta = theta_start + side * theta_span * t
        r = r0 * math.exp(-log_b * theta_span * t)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        grand_points.append(
            anchor
            + radial * (clearance + scale * (x - start_x) - scale * 0.055 * t)
            + tangent * (side * scale * (y - start_y) + side * scale * 0.030 * t)
            + normal * (scale * 0.014 * math.sin(math.pi * t))
        )
    grand_points[0] = anchor + radial * clearance
    grand_radii = [max(child_radii[idx] * 0.36 * (0.968 ** i), 0.0042) for i in range(len(grand_points))]
    grand_mesh, grand_centers = _curve_tube_from_points(grand_points, grand_radii, sides=7, ovality=0.09)
    offset = _append_mesh_into_with_offset(mesh, grand_mesh)
    grand_centers = [offset + c for c in grand_centers]
    _add_welded_neck(
        mesh,
        anchor_idx=child_centers[idx],
        anchor=anchor,
        target=grand_points[0],
        radius=max(child_radii[idx] * 0.34, 0.0044),
        rng=rng,
        segments=2,
        sides=6,
    )
    _bridge_vertices(mesh, child_centers[idx], grand_centers[0], max(child_radii[idx] * 0.14, 0.0026))
    return 1


def _log_spiral_points(
    *,
    turns: float,
    steps: int,
    r0: float,
    r_min: float,
    theta0: float,
    y_amp: float,
    z_lift: float,
    scale: float,
    center: np.ndarray,
    phase: float = 0.0,
) -> Tuple[List[np.ndarray], List[float], float]:
    theta_span = float(turns) * math.tau
    log_b = math.log(float(r0) / float(r_min)) / max(theta_span, 1e-6)
    points: List[np.ndarray] = []
    arc: List[float] = []
    accum = 0.0
    prev = None
    for i in range(steps):
        t = i / float(max(steps - 1, 1))
        theta_rel = theta_span * t
        theta = theta0 + theta_rel + phase
        r = r0 * math.exp(-log_b * theta_rel)
        p = center + scale * np.array(
            [
                r * math.cos(theta),
                y_amp * math.sin(theta * 0.57 + phase * 0.31),
                r * math.sin(theta) + z_lift * (t - 0.5),
            ],
            dtype=float,
        )
        if prev is not None:
            accum += float(np.linalg.norm(p - prev))
        points.append(p)
        arc.append(accum)
        prev = p
    return points, arc, log_b


def _frame_at(points: List[np.ndarray], idx: int, center_hint: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    i0 = max(0, idx - 2)
    i1 = min(len(points) - 1, idx + 2)
    tangent = _unit(points[i1] - points[i0])
    radial = _unit(points[idx] - center_hint)
    if float(np.linalg.norm(radial)) < 1e-6 or abs(float(np.dot(radial, tangent))) > 0.92:
        radial = _unit(np.cross(tangent, np.array([0.0, 1.0, 0.0])))
    normal = _unit(np.cross(tangent, radial))
    radial = _unit(np.cross(normal, tangent))
    return tangent, radial, normal


def _add_child_log_spiral(
    mesh: pb.Mesh,
    main_points: List[np.ndarray],
    main_centers: List[int],
    main_radii: List[float],
    idx: int,
    *,
    depth: int,
    child_rank: int,
    rng: np.random.Generator,
    center_hint: np.ndarray,
    variant: str,
) -> int:
    tangent, radial, normal = _frame_at(main_points, idx, center_hint)
    side = -1.0 if child_rank % 2 else 1.0
    scale_base = (0.255 if variant in ("surface", "open") else 0.225) * (0.968 ** (child_rank % 5))
    scale = scale_base * (1.0 + 0.035 * min(depth, 6))
    turns = 0.88 + 0.10 * ((child_rank + depth) % 4)
    steps = 34 if depth <= 2 else 40
    r0 = 0.62
    r_min = 0.112
    anchor = np.asarray(main_points[idx], dtype=float)
    clearance = max(main_radii[idx] * 0.34, 0.006)
    theta_start = side * (0.18 + 0.08 * (child_rank % 3)) + rng.uniform(-0.08, 0.08)
    theta_span = float(turns) * math.tau
    log_b = math.log(r0 / r_min) / max(theta_span, 1e-6)
    start_x = r0 * math.cos(theta_start)
    start_y = r0 * math.sin(theta_start)
    child_points: List[np.ndarray] = []
    for q in range(steps):
        t = q / float(max(steps - 1, 1))
        theta_rel = theta_span * t
        theta = theta_start + side * theta_rel
        r = r0 * math.exp(-log_b * theta_rel)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        surface_pull = scale * (0.075 + 0.020 * rng.random()) * t
        child_points.append(
            anchor
            + radial * (clearance + scale * (x - start_x) - surface_pull)
            + tangent * (side * scale * (y - start_y) + side * scale * 0.055 * t)
            + normal * (scale * 0.022 * math.sin(math.pi * t) * math.sin(theta * 0.7))
        )
    child_points[0] = anchor + radial * clearance
    child_radii = [max(main_radii[idx] * 0.42 * (0.970 ** i), 0.0072) for i in range(len(child_points))]
    child_mesh, child_centers = _curve_tube_from_points(child_points, child_radii, sides=10, ovality=0.08)
    child_offset = _append_mesh_into_with_offset(mesh, child_mesh)
    child_centers = [child_offset + c for c in child_centers]
    _add_welded_neck(
        mesh,
        anchor_idx=main_centers[idx],
        anchor=anchor,
        target=child_points[0],
        radius=max(main_radii[idx] * 0.38, 0.006),
        rng=rng,
        segments=3,
        sides=8,
    )
    _bridge_vertices(mesh, main_centers[idx], child_centers[0], max(main_radii[idx] * 0.18, 0.0036))
    added = 1
    if depth >= 4 and child_rank % 2 == 0:
        added += _add_child_on_child_spiral(
            mesh,
            child_points,
            child_centers,
            child_radii,
            max(3, min(len(child_points) - 5, len(child_points) // 2 + (child_rank % 4) - 1)),
            depth=depth,
            child_rank=child_rank,
            rng=rng,
            variant=variant,
        )
    if depth >= 6 and child_rank % 3 == 1:
        added += _add_child_on_child_spiral(
            mesh,
            child_points,
            child_centers,
            child_radii,
            max(4, min(len(child_points) - 5, int(len(child_points) * 0.68))),
            depth=depth,
            child_rank=child_rank + 7,
            rng=rng,
            variant=variant,
        )
    return added


def _build_log_fiddlehead(seed: int, variant: str, depth: int) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed + depth * 97)
    turns = 2.72 if variant in ("surface", "open") else 3.02
    steps = 134 if variant in ("surface", "open") else 152
    radius0 = 1.34 if variant in ("surface", "open") else 1.42
    radius_min = 0.060 if variant in ("surface", "open") else 0.052
    theta0 = -0.18 if variant in ("surface", "open") else 0.10
    center = np.array([0.0, 0.0, 0.0], dtype=float)
    main_points, arc_samples, log_b = _log_spiral_points(
        turns=turns,
        steps=steps,
        r0=radius0,
        r_min=radius_min,
        theta0=theta0,
        y_amp=0.112,
        z_lift=0.075,
        scale=1.0,
        center=center,
    )
    main_radii = [
        max((0.092 if variant in ("surface", "open") else 0.086) * math.exp(-0.66 * (i / max(steps - 1, 1))), 0.020)
        for i in range(steps)
    ]
    mesh, centers = _curve_tube_from_points(main_points, main_radii, sides=18, ovality=0.055)
    counts = _counts()

    base_count = 1 if variant in ("surface", "open") else 2
    detail_count = base_count + int(depth) * (2 if variant in ("surface", "open") else 3)
    arc_arr = np.asarray(arc_samples, dtype=float)
    target_arcs = [] if detail_count <= 0 else np.linspace(arc_arr[20], arc_arr[-22], detail_count)
    selected = []
    for target in target_arcs:
        j = int(np.argmin(np.abs(arc_arr - target)))
        if 18 <= j < len(main_points) - 18 and (not selected or abs(j - selected[-1]) >= 8):
            selected.append(j)

    for k, j in enumerate(selected):
        added = _add_child_log_spiral(
            mesh,
            main_points,
            centers,
            main_radii,
            j,
            depth=depth,
            child_rank=k,
            rng=rng,
            center_hint=center,
            variant=variant,
        )
        counts["tendril_count"] += int(added)

    counts["support_node_count"] = len(main_points)
    _renormalize(mesh, 3.0)
    return mesh, {
        "family": "fiddlehead",
        "variant": f"log_{variant}",
        "depth": depth,
        "seed": seed,
        "spiral_type": "logarithmic",
        "spiral_equation": "r(theta)=r0*exp(-b*theta)",
        "spiral_turns": turns,
        "spiral_decay_b": log_b,
        "root_design": "connected mesh-stage recursion; no long stem rods; main true log spiral plus thicker surface-attached self-similar log spirals and depth-gated child-on-child curls",
        "tendril_count": counts["tendril_count"],
        "support_node_count": counts["support_node_count"],
    }


def _build_compound_fern(seed: int, variant: str, depth: int) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed + depth * 113)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.078 if variant == "broad" else 0.070]
    rachis = [0]
    parent = 0
    n = 28 if variant == "broad" else 30
    for i in range(1, n + 1):
        t = i / float(n)
        direction = np.array(
            [
                0.026 * math.sin(t * math.pi * 0.80),
                0.030 * math.sin(t * math.tau * 0.34),
                0.156 + 0.022 * math.cos(t * math.pi * 0.58),
            ]
        )
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.066 * (0.963**i), 0.017))
        rachis.append(parent)

    anchors: List[Tuple[int, int, float, int]] = []
    stride = 3 if variant == "open" else 2
    for local_i, anchor in enumerate(rachis[2:-2], start=2):
        if local_i % stride != 0:
            continue
        t = local_i / float(n)
        envelope = math.sin(math.pi * t) ** (0.34 if variant == "broad" else 0.42)
        side_len = ((1.56 if variant == "broad" else 1.34) * envelope + 0.28) * (1.0 + 0.060 * min(depth, 6))
        for sign in (-1, 1):
            side_dir = np.array([sign * (1.18 + 0.05 * math.sin(local_i * 0.63)), 0.055 * math.cos(local_i * 0.48), 0.065 - 0.220 * t])
            p0 = _append_child(nodes, parents, radii, anchor, side_dir, side_len * 0.48, max(0.041 * (1.0 - 0.22 * t), 0.014))
            p1 = _append_child(nodes, parents, radii, p0, side_dir + np.array([0.0, 0.030 * sign, -0.10]), side_len * 0.34, max(0.030 * (1.0 - 0.25 * t), 0.0095))
            anchors.extend([(p0, sign, t, 1), (p1, sign, t, 1)])
            if depth >= 2 and 0.16 < t < 0.88:
                branch_count = 1 if variant == "open" or depth < 4 else 2
                for branch_i in range(branch_count):
                    branch_sign = -1 if branch_i == 0 else 1
                    branch_dir = _unit(side_dir + np.array([0.15 * sign, 0.060 * branch_sign, -0.24]))
                    p2 = _append_child(nodes, parents, radii, p1, branch_dir, side_len * (0.27 if depth >= 6 else 0.23), max(0.020 * (1.0 - 0.16 * t), 0.0072))
                    anchors.append((p2, sign, t, 2))
                    if depth >= 6 and variant == "broad" and branch_i == 0 and 0.24 < t < 0.78:
                        p3 = _append_child(
                            nodes,
                            parents,
                            radii,
                            p2,
                            _unit(branch_dir + np.array([0.10 * sign, 0.045 * branch_sign, -0.20])),
                            side_len * 0.15,
                            max(0.012 * (1.0 - 0.12 * t), 0.0054),
                        )
                        anchors.append((p3, sign, t, 3))

    normalized = _normalize_nodes(nodes, 3.08)
    mesh = _smooth_support_mesh(normalized, _dedupe_edges(_graph_edges(parents)), radii, sides=15, ovality=0.07)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    normal_hint = np.array([0.0, 1.0, 0.18], dtype=float)
    for k, (idx, sign, t, order) in enumerate(anchors):
        axis = _node_axis(normalized, parents, idx)
        base = _unit(axis + np.array([0.060 * sign, 0.0, -0.034]) + rng.normal(0.0, 0.008, 3))
        order_scale = 1.0 if order == 1 else (0.78 if order == 2 else 0.58)
        length = float(rng.uniform(0.130, 0.215) * (1.15 - 0.26 * t) * order_scale)
        width = length * float(rng.uniform(0.26, 0.36))
        _add_thick_lamina(mesh, centers[idx], normalized[idx], base, length, width, normal_hint, rows=7, thickness=0.0085, curl=0.038)
        counts["leaflet_count"] += 1
        if depth >= 4 and order == 1 and k % 5 == 2:
            _add_tube(mesh, centers, normalized, idx, _unit(0.72 * base + np.array([0.10 * sign, 0.0, -0.12])), length * 0.48, 0.0075, rng, curl=0.10, segments=4, sides=7)
            counts["tendril_count"] += 1
        if depth >= 6 and order == 2 and k % 4 == 1:
            _add_tube(mesh, centers, normalized, idx, _unit(0.64 * base + np.array([0.08 * sign, 0.0, -0.16])), length * 0.36, 0.0058, rng, curl=0.08, segments=3, sides=6)
            counts["tendril_count"] += 1

    counts["support_node_count"] = len(normalized)
    _renormalize(mesh, 3.04)
    return mesh, {
        "family": "compound_fern",
        "variant": f"mesh_recursive_{variant}",
        "depth": depth,
        "seed": seed,
        "root_design": "connected mesh-stage recursion with thick rachis, primary pinnae, depth-gated secondary/tertiary pinnae, and conservative attached laminae",
        "leaflet_count": counts["leaflet_count"],
        "tendril_count": counts["tendril_count"],
        "support_node_count": counts["support_node_count"],
    }


def _case_specs():
    return [
        ("fiddlehead_log_surface_recursive_s", "fiddlehead", "surface", 202616001),
        ("fiddlehead_log_surface_recursive_t", "fiddlehead", "dense_surface", 202616002),
        ("fern_mesh_frond_m", "fern", "broad", 202616003),
        ("fern_mesh_frond_n", "fern", "open", 202616004),
    ]


def _render_contact(out_dir: Path, rows: List[Dict]) -> Dict:
    out = out_dir / "fern_depth_roots_contact_sheet_20260512o.png"
    cmd = [
        sys.executable,
        str(ASSET_DIR / "render_mesh_contact_sheet.py"),
        "--out",
        str(out),
        "--views",
        "iso",
        "--max-faces",
        "240000",
    ]
    for row in rows:
        cmd.extend(["--case", f"{row['case_id']}_d{row['depth']}={row['mesh_path']}"])
    try:
        result = subprocess.run(cmd, cwd=str(ROOT_DIR), check=True, text=True, capture_output=True)
        return {"status": "ok", "path": str(out), "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except Exception as exc:
        return {"status": "failed", "path": str(out), "error": str(exc)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--depths", nargs="+", type=int, default=[0, 2, 4, 6])
    parser.add_argument("--skip-preview", action="store_true")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    rows: List[Dict] = []
    metrics_rows: List[Dict] = []
    for case_id, family, variant, seed in _case_specs():
        for depth in args.depths:
            if family == "fiddlehead":
                mesh, meta = _build_log_fiddlehead(seed, variant, depth)
            else:
                mesh, meta = _build_compound_fern(seed, variant, depth)
            case_dir = args.out / case_id / f"depth_{depth:02d}"
            mesh_path = case_dir / f"{case_id}_depth_{depth:02d}.obj"
            _export_obj(mesh_path, mesh)
            metrics = _mesh_stats(mesh)
            if float(metrics["largest_mesh_component_vertex_ratio"]) < 0.999:
                raise RuntimeError(f"{case_id} depth {depth} failed connected-root gate: {metrics}")
            meta = {**meta, "case_id": case_id, "mesh_path": str(mesh_path), "metrics": metrics}
            _write_json(case_dir / f"{case_id}_depth_{depth:02d}_metadata.json", meta)
            row = {
                "case_id": case_id,
                "family": meta["family"],
                "variant": meta["variant"],
                "depth": int(depth),
                "mesh_path": str(mesh_path),
                "leaflet_count": meta.get("leaflet_count", 0),
                "tendril_count": meta.get("tendril_count", 0),
                "support_node_count": meta.get("support_node_count", 0),
                "vertices": metrics["vertices"],
                "faces": metrics["faces"],
                "largest_mesh_component_vertex_ratio": metrics["largest_mesh_component_vertex_ratio"],
                "root_design": meta["root_design"],
            }
            rows.append(row)
            metrics_rows.append({"case_id": case_id, "depth": int(depth), **metrics})

    with (args.out / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    _write_json(args.out / "manifest.json", rows)
    _write_json(args.out / "initial_metrics.json", metrics_rows)
    contact = {"status": "skipped", "path": ""}
    if not args.skip_preview:
        contact = _render_contact(args.out, rows)
    summary = {
        "out_dir": str(args.out),
        "case_ids": sorted({row["case_id"] for row in rows}),
        "depths": sorted({row["depth"] for row in rows}),
        "manifest_csv": str(args.out / "manifest.csv"),
        "initial_metrics_json": str(args.out / "initial_metrics.json"),
        "contact_sheet": contact,
        "root_scope": "connected mesh-stage recursive depth roots; final evidence requires remote SLat naturalization",
        "revision": "20260512o thicker/deeper connected log-spiral and compound-fern roots",
    }
    _write_json(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
