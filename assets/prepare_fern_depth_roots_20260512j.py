#!/usr/bin/env python3
"""Prepare connected per-depth fern/fiddlehead roots for 12j SLat naturalization.

12i showed that repeated sparse-latent patch translations create detached dust.
This script moves recursive structure construction back into mesh space, where
every displayed depth is explicitly connected before TRELLIS2 encodes/decodes it.
The remote runner then applies a passthrough SLat decode as naturalization.
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


DEFAULT_OUT = ROOT_DIR / "results" / "fern_depth_roots_20260512j"


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


def _build_log_fiddlehead(seed: int, variant: str, depth: int) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed + depth * 97)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.090]
    parent = 0
    stem_steps = 3
    for i in range(1, stem_steps + 1):
        t = i / float(stem_steps)
        direction = np.array([0.075 * math.sin(t * math.pi * 0.52), 0.030 * math.cos(i * 0.7), 0.210 + 0.016 * t])
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.082 * (0.91**i), 0.052))

    stem_tip = np.asarray(nodes[parent], dtype=float)
    center = stem_tip + np.array([0.25 if variant == "open" else 0.32, 0.0, -0.035])
    turns = 2.75 if variant == "open" else 3.20
    steps = 116 if variant == "open" else 136
    theta0 = -0.34 if variant == "open" else 0.08
    theta_span = turns * math.tau
    radius0 = 1.33 if variant == "open" else 1.42
    radius_min = 0.055 if variant == "open" else 0.047
    log_b = math.log(radius0 / radius_min) / max(theta_span, 1e-6)
    coil_indices: List[int] = []
    arc_samples: List[float] = []
    prev = stem_tip
    arc_len = 0.0
    for i in range(1, steps + 1):
        t = i / float(steps)
        theta_rel = theta_span * t
        theta = theta0 + theta_rel
        r = radius0 * math.exp(-log_b * theta_rel)
        p = center + np.array([r * math.cos(theta), 0.112 * math.sin(theta * 0.50), r * math.sin(theta) + 0.050 * t])
        direction = p - prev
        arc_len += float(np.linalg.norm(direction))
        parent = _append_child(
            nodes,
            parents,
            radii,
            parent,
            direction,
            max(float(np.linalg.norm(direction)), 1e-6),
            max(0.070 * math.exp(-0.64 * theta_rel / theta_span), 0.019),
        )
        coil_indices.append(parent)
        arc_samples.append(arc_len)
        prev = p

    normalized = _normalize_nodes(nodes, 3.0)
    mesh = _smooth_support_mesh(normalized, _dedupe_edges(_graph_edges(parents)), radii, sides=18, ovality=0.06)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    coil_origin = np.asarray(normalized[stem_steps], dtype=float)

    base_count = 8 if variant == "open" else 10
    detail_count = base_count + int(depth) * (3 if variant == "open" else 4)
    arc_arr = np.asarray(arc_samples, dtype=float)
    target_arcs = np.linspace(arc_arr[9], arc_arr[-9], detail_count)
    selected = []
    for target in target_arcs:
        j = int(np.argmin(np.abs(arc_arr - target)))
        if 7 <= j < len(coil_indices) - 7 and (not selected or abs(j - selected[-1]) >= 4):
            selected.append(j)

    for k, j in enumerate(selected):
        idx = coil_indices[j]
        axis = _node_axis(normalized, parents, idx)
        radial = _unit(np.asarray(normalized[idx]) - coil_origin)
        tangent = _unit(0.22 * axis + 0.94 * radial + rng.normal(0.0, 0.006, 3))
        depth_scale = 1.0 + 0.055 * depth
        scale = max(0.40, 0.91**k)
        length = float(rng.uniform(0.205, 0.320) * scale * depth_scale)
        radius = float(rng.uniform(0.011, 0.017) * max(0.72, scale))
        _add_tube(mesh, centers, normalized, idx, tangent, length, radius, rng, curl=0.15, segments=7, sides=8)
        if depth >= 2 and k % 3 == 1:
            child_dir = _unit(0.62 * tangent + 0.34 * axis + rng.normal(0.0, 0.010, 3))
            _add_tube(mesh, centers, normalized, idx, child_dir, length * 0.50, radius * 0.58, rng, curl=0.22, segments=5, sides=7)
        if depth >= 4 and k % 5 == 2:
            child_dir = _unit(0.46 * tangent + 0.52 * radial + rng.normal(0.0, 0.012, 3))
            _add_tube(mesh, centers, normalized, idx, child_dir, length * 0.36, radius * 0.48, rng, curl=0.28, segments=4, sides=6)
        counts["tendril_count"] += 1

    counts["support_node_count"] = len(normalized)
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
        "root_design": "connected mesh-stage recursion; equal-arc-length side handles on a true log spiral",
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
        ("fiddlehead_log_mesh_k", "fiddlehead", "open", 202611001),
        ("fiddlehead_log_mesh_l", "fiddlehead", "dense", 202611002),
        ("fern_mesh_frond_k", "fern", "broad", 202611003),
        ("fern_mesh_frond_l", "fern", "open", 202611004),
    ]


def _render_contact(out_dir: Path, rows: List[Dict]) -> Dict:
    out = out_dir / "fern_depth_roots_contact_sheet_20260512j.png"
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
        "revision": "20260512j per-depth connected roots",
    }
    _write_json(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
