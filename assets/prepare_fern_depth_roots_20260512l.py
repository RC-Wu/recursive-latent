#!/usr/bin/env python3
"""Prepare connected per-depth fern/fiddlehead roots for 12k SLat naturalization.

12i showed that repeated sparse-latent patch translations create detached dust.
This script moves recursive structure construction back into mesh space, where
every displayed depth is explicitly connected before TRELLIS2 encodes/decodes it.
The remote runner then applies a passthrough SLat decode as naturalization.

12k incorporates the user correction that the logarithmic spiral case must not
contain the two long support/stem rods from 12j. The fiddlehead root is only a
main logarithmic spiral tube plus self-similar logarithmic spiral child tubes
attached along it.
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


DEFAULT_OUT = ROOT_DIR / "results" / "fern_depth_roots_20260512l"


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
) -> None:
    tangent, radial, normal = _frame_at(main_points, idx, center_hint)
    side = -1.0 if child_rank % 2 else 1.0
    scale_base = (0.33 if variant == "open" else 0.285) * (0.92 ** (child_rank % 5))
    scale = scale_base * (1.0 + 0.045 * depth)
    turns = 1.18 + 0.16 * ((child_rank + depth) % 3)
    steps = 34 if depth <= 1 else 40
    r0 = 0.54
    r_min = 0.095
    anchor = np.asarray(main_points[idx], dtype=float)
    clearance = max(main_radii[idx] * 2.25, 0.034)
    child_center = anchor + radial * (clearance + 0.18 * scale) + normal * (side * 0.10 * scale)
    theta0 = math.atan2(float(anchor[2] - center_hint[2]), float(anchor[0] - center_hint[0])) + side * 0.65
    child_points, _, _ = _log_spiral_points(
        turns=turns,
        steps=steps,
        r0=r0,
        r_min=r_min,
        theta0=theta0,
        y_amp=0.035,
        z_lift=0.060,
        scale=scale,
        center=child_center,
        phase=side * 0.42 + 0.13 * child_rank,
    )
    # Rotate the child curve's rough plane into the main tangent/radial frame.
    child_arr = np.asarray(child_points, dtype=float)
    local_center = child_arr.mean(axis=0)
    local = child_arr - local_center
    transformed = []
    for p in local:
        transformed.append(child_center + radial * p[0] + normal * p[1] + tangent * p[2])
    child_points = transformed
    child_points[0] = anchor + radial * clearance
    child_radii = [max(main_radii[idx] * 0.34 * (0.985 ** i), 0.0065) for i in range(len(child_points))]
    child_mesh, child_centers = _curve_tube_from_points(child_points, child_radii, sides=10, ovality=0.05)
    child_offset = _append_mesh_into_with_offset(mesh, child_mesh)
    child_centers = [child_offset + c for c in child_centers]
    # Short welded neck only; this is a local attachment, not a visible long rod.
    _add_curved_tube_detail(
        mesh,
        main_centers[idx],
        anchor,
        _unit(child_points[0] - anchor),
        max(float(np.linalg.norm(child_points[0] - anchor)), 1e-4),
        max(main_radii[idx] * 0.42, 0.0065),
        rng,
        segments=2,
        sides=8,
        curl=0.0,
    )
    _bridge_vertices(mesh, main_centers[idx], child_centers[0], max(main_radii[idx] * 0.16, 0.0038))
    if depth >= 4 and child_rank % 3 == 1:
        sub_idx = min(len(child_points) - 5, max(4, len(child_points) // 2))
        sub_anchor = np.asarray(child_points[sub_idx], dtype=float)
        sub_tangent, sub_radial, sub_normal = _frame_at(child_points, sub_idx, child_center)
        sub_scale = scale * 0.43
        sub_center = sub_anchor + sub_radial * (child_radii[sub_idx] * 2.2 + 0.08 * sub_scale)
        sub_points, _, _ = _log_spiral_points(
            turns=0.95,
            steps=24,
            r0=0.48,
            r_min=0.11,
            theta0=theta0 + 0.72,
            y_amp=0.025,
            z_lift=0.040,
            scale=sub_scale,
            center=sub_center,
            phase=-side * 0.37,
        )
        sub_arr = np.asarray(sub_points, dtype=float)
        sub_local = sub_arr - sub_arr.mean(axis=0)
        sub_points = [sub_center + sub_radial * p[0] + sub_normal * p[1] + sub_tangent * p[2] for p in sub_local]
        sub_points[0] = sub_anchor + sub_radial * max(child_radii[sub_idx] * 2.1, 0.018)
        sub_radii = [max(child_radii[sub_idx] * 0.36 * (0.982 ** i), 0.0048) for i in range(len(sub_points))]
        sub_mesh, sub_centers = _curve_tube_from_points(sub_points, sub_radii, sides=8, ovality=0.05)
        sub_offset = _append_mesh_into_with_offset(mesh, sub_mesh)
        sub_centers = [sub_offset + c for c in sub_centers]
        _add_curved_tube_detail(
            mesh,
            child_centers[sub_idx],
            sub_anchor,
            _unit(sub_points[0] - sub_anchor),
            max(float(np.linalg.norm(sub_points[0] - sub_anchor)), 1e-4),
            max(child_radii[sub_idx] * 0.38, 0.0048),
            rng,
            segments=2,
            sides=7,
            curl=0.0,
        )
        _bridge_vertices(mesh, child_centers[sub_idx], sub_centers[0], max(child_radii[sub_idx] * 0.14, 0.0028))


def _build_log_fiddlehead(seed: int, variant: str, depth: int) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed + depth * 97)
    turns = 2.70 if variant == "open" else 3.05
    steps = 122 if variant == "open" else 142
    radius0 = 1.34 if variant == "open" else 1.43
    radius_min = 0.060 if variant == "open" else 0.052
    theta0 = -0.18 if variant == "open" else 0.12
    center = np.array([0.0, 0.0, 0.0], dtype=float)
    main_points, arc_samples, log_b = _log_spiral_points(
        turns=turns,
        steps=steps,
        r0=radius0,
        r_min=radius_min,
        theta0=theta0,
        y_amp=0.105,
        z_lift=0.070,
        scale=1.0,
        center=center,
    )
    main_radii = [
        max((0.078 if variant == "open" else 0.074) * math.exp(-0.78 * (i / max(steps - 1, 1))), 0.017)
        for i in range(steps)
    ]
    mesh, centers = _curve_tube_from_points(main_points, main_radii, sides=18, ovality=0.055)
    counts = _counts()

    base_count = 3 if variant == "open" else 4
    detail_count = base_count + int(depth) * (2 if variant == "open" else 3)
    arc_arr = np.asarray(arc_samples, dtype=float)
    target_arcs = np.linspace(arc_arr[12], arc_arr[-13], detail_count)
    selected = []
    for target in target_arcs:
        j = int(np.argmin(np.abs(arc_arr - target)))
        if 10 <= j < len(main_points) - 10 and (not selected or abs(j - selected[-1]) >= 7):
            selected.append(j)

    for k, j in enumerate(selected):
        _add_child_log_spiral(
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
        counts["tendril_count"] += 1

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
        "root_design": "connected mesh-stage recursion; no long stem rods; main true log spiral plus attached self-similar log spirals",
        "tendril_count": counts["tendril_count"],
        "support_node_count": counts["support_node_count"],
    }


def _build_compound_fern(seed: int, variant: str, depth: int) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed + depth * 113)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.068 if variant == "broad" else 0.060]
    rachis = [0]
    parent = 0
    n = 24 if variant == "broad" else 26
    for i in range(1, n + 1):
        t = i / float(n)
        direction = np.array([0.030 * math.sin(t * math.pi * 0.80), 0.022 * math.sin(t * math.tau * 0.38), 0.156 + 0.020 * math.cos(t * math.pi * 0.60)])
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.058 * (0.958**i), 0.014))
        rachis.append(parent)

    anchors: List[Tuple[int, int, float, int]] = []
    stride = 3 if variant == "open" else 2
    for local_i, anchor in enumerate(rachis[2:-2], start=2):
        if local_i % stride != 0:
            continue
        t = local_i / float(n)
        envelope = math.sin(math.pi * t) ** (0.34 if variant == "broad" else 0.42)
        side_len = ((1.48 if variant == "broad" else 1.28) * envelope + 0.24) * (1.0 + 0.055 * depth)
        for sign in (-1, 1):
            side_dir = np.array([sign * (1.18 + 0.05 * math.sin(local_i * 0.63)), 0.050 * math.cos(local_i * 0.48), 0.075 - 0.230 * t])
            p0 = _append_child(nodes, parents, radii, anchor, side_dir, side_len * 0.48, max(0.034 * (1.0 - 0.24 * t), 0.011))
            p1 = _append_child(nodes, parents, radii, p0, side_dir + np.array([0.0, 0.022 * sign, -0.10]), side_len * 0.32, max(0.024 * (1.0 - 0.26 * t), 0.007))
            anchors.extend([(p0, sign, t, 1), (p1, sign, t, 1)])
            if depth >= 2 and 0.16 < t < 0.88:
                branch_count = 1 if variant == "open" or depth < 4 else 2
                for branch_i in range(branch_count):
                    branch_sign = -1 if branch_i == 0 else 1
                    branch_dir = _unit(side_dir + np.array([0.15 * sign, 0.060 * branch_sign, -0.24]))
                    p2 = _append_child(nodes, parents, radii, p1, branch_dir, side_len * 0.24, max(0.015 * (1.0 - 0.18 * t), 0.0052))
                    anchors.append((p2, sign, t, 2))

    normalized = _normalize_nodes(nodes, 3.08)
    mesh = _smooth_support_mesh(normalized, _dedupe_edges(_graph_edges(parents)), radii, sides=15, ovality=0.07)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    normal_hint = np.array([0.0, 1.0, 0.18], dtype=float)
    for k, (idx, sign, t, order) in enumerate(anchors):
        axis = _node_axis(normalized, parents, idx)
        base = _unit(axis + np.array([0.060 * sign, 0.0, -0.034]) + rng.normal(0.0, 0.008, 3))
        length = float(rng.uniform(0.110, 0.190) * (1.15 - 0.28 * t) * (0.72 if order == 2 else 1.0))
        width = length * float(rng.uniform(0.22, 0.32))
        _add_thick_lamina(mesh, centers[idx], normalized[idx], base, length, width, normal_hint, rows=6, thickness=0.0065, curl=0.034)
        counts["leaflet_count"] += 1
        if depth >= 4 and order == 1 and k % 5 == 2:
            _add_tube(mesh, centers, normalized, idx, _unit(0.72 * base + np.array([0.10 * sign, 0.0, -0.12])), length * 0.44, 0.0058, rng, curl=0.10, segments=4, sides=6)
            counts["tendril_count"] += 1

    counts["support_node_count"] = len(normalized)
    _renormalize(mesh, 3.04)
    return mesh, {
        "family": "compound_fern",
        "variant": f"mesh_recursive_{variant}",
        "depth": depth,
        "seed": seed,
        "root_design": "connected mesh-stage recursion with rachis, primary pinnae, and depth-gated secondary pinnae",
        "leaflet_count": counts["leaflet_count"],
        "tendril_count": counts["tendril_count"],
        "support_node_count": counts["support_node_count"],
    }


def _case_specs():
    return [
        ("fiddlehead_log_crozier_pure_m", "fiddlehead", "open", 202613001),
        ("fiddlehead_log_crozier_pure_n", "fiddlehead", "dense", 202613002),
        ("fern_mesh_frond_k", "fern", "broad", 202613003),
        ("fern_mesh_frond_l", "fern", "open", 202613004),
    ]


def _render_contact(out_dir: Path, rows: List[Dict]) -> Dict:
    out = out_dir / "fern_depth_roots_contact_sheet_20260512l.png"
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
    parser.add_argument("--depths", nargs="+", type=int, default=[0, 2, 4])
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
        "revision": "20260512l per-depth connected roots",
    }
    _write_json(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
