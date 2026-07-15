#!/usr/bin/env python3
"""Prepare 20260512i fern/fiddlehead roots for publication-targeted recursion.

This revision follows the 12h failure analysis: the SLat grammar should not be
asked to invent fern children from scattered surface tokens.  The root already
contains connected secondary handles, and the recursive operators only extend
or emphasize those handles with low-amplitude local moves.
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


DEFAULT_OUT = ROOT_DIR / "results" / "fern_showcase_roots_20260512i"


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _export_obj(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


def _renormalize(mesh: pb.Mesh, extent: float = 2.90) -> None:
    arr = np.asarray(mesh.vertices, dtype=float)
    center = (arr.min(axis=0) + arr.max(axis=0)) * 0.5
    scale = max(float((arr.max(axis=0) - arr.min(axis=0)).max()), 1e-6)
    arr = (arr - center) * (float(extent) / scale)
    mesh.vertices = [tuple(map(float, v)) for v in arr]


def _add_handle_tube(
    mesh: pb.Mesh,
    centers: List[int],
    nodes: List[np.ndarray],
    idx: int,
    direction: np.ndarray,
    length: float,
    radius: float,
    rng: np.random.Generator,
    curl: float = 0.14,
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


def _log_spiral_handle_fiddlehead(seed: int, variant: str) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.088]

    parent = 0
    stem_steps = 2 if variant == "open" else 3
    for i in range(1, stem_steps + 1):
        t = i / float(stem_steps)
        direction = np.array([0.075 * math.sin(t * math.pi * 0.55), 0.035 * math.cos(i * 0.83), 0.210 + 0.018 * t])
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.080 * (0.91**i), 0.052))

    stem_tip = np.asarray(nodes[parent], dtype=float)
    center = stem_tip + np.array([0.24 if variant == "open" else 0.31, 0.0, -0.035])
    turns = 2.75 if variant == "open" else 3.25
    steps = 118 if variant == "open" else 138
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
        p = center + np.array(
            [
                r * math.cos(theta),
                0.115 * math.sin(theta * 0.50),
                r * math.sin(theta) + 0.050 * t,
            ],
            dtype=float,
        )
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

    detail_count = 12 if variant == "open" else 15
    arc_arr = np.asarray(arc_samples, dtype=float)
    target_arcs = np.linspace(arc_arr[8], arc_arr[-8], detail_count)
    selected = []
    for target in target_arcs:
        j = int(np.argmin(np.abs(arc_arr - target)))
        if 6 <= j < len(coil_indices) - 6 and (not selected or abs(j - selected[-1]) >= 5):
            selected.append(j)
    for k, j in enumerate(selected):
        idx = coil_indices[j]
        axis = _node_axis(normalized, parents, idx)
        radial = _unit(np.asarray(normalized[idx]) - coil_origin)
        tangent = _unit(0.22 * axis + 0.94 * radial + rng.normal(0.0, 0.008, 3))
        scale = max(0.42, 0.90**k)
        length = float(rng.uniform(0.205, 0.330) * scale)
        radius = float(rng.uniform(0.010, 0.016) * max(0.70, scale))
        _add_handle_tube(mesh, centers, normalized, idx, tangent, length, radius, rng, curl=0.16, segments=7, sides=8)
        if k % 3 == 1:
            child_dir = _unit(0.60 * tangent + 0.35 * axis + rng.normal(0.0, 0.012, 3))
            _add_handle_tube(mesh, centers, normalized, idx, child_dir, length * 0.54, radius * 0.58, rng, curl=0.26, segments=5, sides=7)
        counts["tendril_count"] += 1

    counts["support_node_count"] = len(normalized)
    counts["support_edge_count"] = len(_dedupe_edges(_graph_edges(parents)))
    _renormalize(mesh, 3.0)
    return mesh, {
        "family": "fiddlehead",
        "variant": f"log_handle_{variant}",
        "seed": seed,
        "target": "logarithmic fern fiddlehead crozier with connected recursive handles",
        "root_design": "true logarithmic spiral r(theta)=r0*exp(-b*theta), equal-arc-length connected side handles, and pre-attached secondary buds",
        "spiral_type": "logarithmic",
        "spiral_equation": "r(theta)=r0*exp(-b*theta)",
        "spiral_turns": turns,
        "spiral_decay_b": log_b,
        "bud_spacing": "approximately equal arc length along logarithmic spiral",
        "leaflet_count": 0,
        "tendril_count": counts["tendril_count"],
        "support_node_count": counts["support_node_count"],
    }


def _handle_compound_frond(seed: int, variant: str) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.066 if variant == "broad" else 0.060]
    rachis = [0]
    parent = 0
    n = 22 if variant == "broad" else 26
    for i in range(1, n + 1):
        t = i / float(n)
        direction = np.array(
            [
                0.032 * math.sin(t * math.pi * 0.82),
                0.026 * math.sin(t * math.tau * 0.38),
                0.158 + 0.022 * math.cos(t * math.pi * 0.62),
            ],
            dtype=float,
        )
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.058 * (0.958**i), 0.014))
        rachis.append(parent)

    anchors: List[Tuple[int, int, float, int]] = []
    for local_i, anchor in enumerate(rachis[2:-2], start=2):
        t = local_i / float(n)
        if variant == "open" and local_i % 2 == 0:
            continue
        envelope = math.sin(math.pi * t) ** (0.34 if variant == "broad" else 0.42)
        side_len = (1.55 if variant == "broad" else 1.34) * envelope + 0.24
        for sign in (-1, 1):
            side_dir = np.array(
                [sign * (1.18 + 0.06 * math.sin(local_i * 0.63)), 0.052 * math.cos(local_i * 0.48), 0.075 - 0.230 * t],
                dtype=float,
            )
            p0 = _append_child(nodes, parents, radii, anchor, side_dir, side_len * 0.48, max(0.033 * (1.0 - 0.24 * t), 0.011))
            p1 = _append_child(nodes, parents, radii, p0, side_dir + np.array([0.0, 0.025 * sign, -0.10]), side_len * 0.32, max(0.024 * (1.0 - 0.26 * t), 0.007))
            anchors.extend([(p0, sign, t, 1), (p1, sign, t, 1)])
            if 0.16 < t < 0.88:
                branch_count = 1 if variant == "open" else 2
                for branch_i in range(branch_count):
                    branch_sign = -1 if branch_i == 0 else 1
                    branch_dir = _unit(side_dir + np.array([0.15 * sign, 0.060 * branch_sign, -0.24]))
                    p2 = _append_child(nodes, parents, radii, p1, branch_dir, side_len * (0.24 if variant == "broad" else 0.29), max(0.015 * (1.0 - 0.18 * t), 0.0052))
                    anchors.append((p2, sign, t, 2))

    normalized = _normalize_nodes(nodes, 3.08)
    mesh = _smooth_support_mesh(normalized, _dedupe_edges(_graph_edges(parents)), radii, sides=15, ovality=0.07)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    normal_hint = np.array([0.0, 1.0, 0.18], dtype=float)

    for k, (idx, sign, t, order) in enumerate(anchors):
        axis = _node_axis(normalized, parents, idx)
        base = _unit(axis + np.array([0.060 * sign, 0.0, -0.034]) + rng.normal(0.0, 0.008, 3))
        length = float(rng.uniform(0.105, 0.195) * (1.16 - 0.30 * t) * (0.74 if order == 2 else 1.0))
        width = length * float(rng.uniform(0.21, 0.32))
        _add_thick_lamina(
            mesh,
            centers[idx],
            normalized[idx],
            base,
            length,
            width,
            normal_hint,
            rows=6,
            thickness=0.0062,
            curl=0.038,
        )
        counts["leaflet_count"] += 1
        if order == 1 and k % 5 == 2:
            _add_handle_tube(
                mesh,
                centers,
                normalized,
                idx,
                _unit(0.72 * base + np.array([0.10 * sign, 0.0, -0.12])),
                length * 0.56,
                0.0058,
                rng,
                curl=0.11,
                segments=4,
                sides=6,
            )
            counts["tendril_count"] += 1

    counts["support_node_count"] = len(normalized)
    counts["support_edge_count"] = len(_dedupe_edges(_graph_edges(parents)))
    _renormalize(mesh, 3.04)
    return mesh, {
        "family": "compound_fern",
        "variant": f"handle_{variant}",
        "seed": seed,
        "target": "compound fern frond with connected recursive rachis-pinna handles",
        "root_design": "connected thick rachis, primary pinnae, secondary pinnae, attached laminae, and explicit handle tips for low-amplitude SLat recursion",
        "leaflet_count": counts["leaflet_count"],
        "tendril_count": counts["tendril_count"],
        "support_node_count": counts["support_node_count"],
    }


def _cases(seed: int):
    return [
        ("fiddlehead_log_handle_k", _log_spiral_handle_fiddlehead(seed + 61, "open")),
        ("fiddlehead_log_handle_l", _log_spiral_handle_fiddlehead(seed + 62, "dense")),
        ("fern_handle_frond_k", _handle_compound_frond(seed + 63, "broad")),
        ("fern_handle_frond_l", _handle_compound_frond(seed + 64, "open")),
    ]


def _render_contact(out_dir: Path, rows: List[Dict]) -> Dict:
    out = out_dir / "fern_showcase_roots_contact_sheet_20260512i.png"
    cmd = [
        sys.executable,
        str(ASSET_DIR / "render_mesh_contact_sheet.py"),
        "--out",
        str(out),
        "--views",
        "iso",
        "front",
        "side",
        "--max-faces",
        "220000",
    ]
    for row in rows:
        cmd.extend(["--case", f"{row['case_id']}={row['mesh_path']}"])
    try:
        result = subprocess.run(cmd, cwd=str(ROOT_DIR), check=True, text=True, capture_output=True)
        return {"status": "ok", "path": str(out), "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except Exception as exc:
        return {"status": "failed", "path": str(out), "error": str(exc)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260512)
    parser.add_argument("--skip-preview", action="store_true")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    rows: List[Dict] = []
    metrics_rows: List[Dict] = []
    for case_id, (mesh, meta) in _cases(args.seed):
        case_dir = args.out / case_id
        mesh_path = case_dir / f"{case_id}.obj"
        _export_obj(mesh_path, mesh)
        metrics = _mesh_stats(mesh)
        if float(metrics["largest_mesh_component_vertex_ratio"]) < 0.999:
            raise RuntimeError(f"{case_id} failed connected-root gate: {metrics}")
        meta = {**meta, "case_id": case_id, "mesh_path": str(mesh_path), "metrics": metrics}
        _write_json(case_dir / f"{case_id}_metadata.json", meta)
        rows.append(
            {
                "case_id": case_id,
                "family": meta["family"],
                "variant": meta["variant"],
                "mesh_path": str(mesh_path),
                "leaflet_count": meta.get("leaflet_count", 0),
                "tendril_count": meta.get("tendril_count", 0),
                "support_node_count": meta.get("support_node_count", 0),
                "vertices": metrics["vertices"],
                "faces": metrics["faces"],
                "largest_mesh_component_vertex_ratio": metrics["largest_mesh_component_vertex_ratio"],
                "target": meta["target"],
            }
        )
        metrics_rows.append({"case_id": case_id, **metrics})

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
        "case_ids": [row["case_id"] for row in rows],
        "manifest_csv": str(args.out / "manifest.csv"),
        "initial_metrics_json": str(args.out / "initial_metrics.json"),
        "contact_sheet": contact,
        "root_scope": "root candidates only; final evidence requires remote SLat recursion",
        "revision": "20260512i connected secondary handles for low-amplitude recursion",
    }
    _write_json(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
