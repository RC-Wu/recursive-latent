#!/usr/bin/env python3
"""Prepare 20260512c fern/fiddlehead roots for stronger visual cases.

The 20260512b remote sweep was technically successful, but the fiddlehead stem
was too long relative to the crozier and the fern depth change read too weakly.
This revision uses compact crozier-first roots and broad compound/fractal fern
roots to make recursion visible without relying on aggressive fragmented copies.
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
    _add_lamina,
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


DEFAULT_OUT = ROOT_DIR / "results" / "fern_showcase_roots_20260512c"


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _export_obj(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


def _renormalize(mesh: pb.Mesh, extent: float = 2.85) -> None:
    arr = np.asarray(mesh.vertices, dtype=float)
    center = (arr.min(axis=0) + arr.max(axis=0)) * 0.5
    scale = max(float((arr.max(axis=0) - arr.min(axis=0)).max()), 1e-6)
    arr = (arr - center) * (float(extent) / scale)
    mesh.vertices = [tuple(map(float, v)) for v in arr]


def _compact_fiddlehead(seed: int, variant: str) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.074]

    parent = 0
    stem_steps = 3
    for i in range(1, stem_steps + 1):
        t = i / float(stem_steps)
        direction = np.array([0.18 * math.sin(t * math.pi * 0.65), 0.018 * math.cos(i), 0.18 + 0.025 * t])
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.070 * (0.90**i), 0.040))

    stem_tip = np.asarray(nodes[parent], dtype=float)
    center = stem_tip + np.array([0.24 if variant == "compact_crozier" else 0.12, 0.0, -0.02])
    turns = 2.45 if variant == "compact_crozier" else 1.88
    steps = 58 if variant == "compact_crozier" else 44
    radius0 = 1.05 if variant == "compact_crozier" else 0.88
    phase = 0.10 if variant == "compact_crozier" else -0.55
    prev = stem_tip
    coil_indices: List[int] = []
    for i in range(1, steps + 1):
        t = i / float(steps)
        theta = phase + turns * math.tau * t
        radius = radius0 * ((1.0 - t) ** 0.92) + 0.040
        p = center + np.array(
            [
                radius * math.cos(theta),
                0.035 * math.sin(theta * 0.75),
                radius * math.sin(theta) + 0.060 * t,
            ],
            dtype=float,
        )
        direction = p - prev
        parent = _append_child(
            nodes,
            parents,
            radii,
            parent,
            direction,
            max(float(np.linalg.norm(direction)), 1e-6),
            max(0.040 * (1.0 - 0.58 * t), 0.012),
        )
        coil_indices.append(parent)
        prev = p

    normalized = _normalize_nodes(nodes, 2.90)
    mesh = _smooth_support_mesh(normalized, _dedupe_edges(_graph_edges(parents)), radii, sides=16, ovality=0.09)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    normal_hint = np.array([0.0, 1.0, 0.20], dtype=float)
    coil_anchor = np.asarray(normalized[stem_steps], dtype=float)
    for k, idx in enumerate(coil_indices[3:-2:2]):
        axis = _node_axis(normalized, parents, idx)
        radial = _unit(np.asarray(normalized[idx]) - coil_anchor)
        leaf_dir = _unit(0.25 * axis + 0.92 * radial + rng.normal(0.0, 0.014, 3))
        length = float(rng.uniform(0.105, 0.185) * (1.0 - 0.006 * k))
        _add_thick_lamina(mesh, centers[idx], normalized[idx], leaf_dir, length, length * 0.26, normal_hint, rows=6, thickness=0.0045, curl=0.070)
        counts["leaflet_count"] += 1
        if k % 5 == 2:
            _add_curved_tube_detail(mesh, centers[idx], normalized[idx], _unit(leaf_dir + np.array([0.0, 0.0, -0.12])), length * 0.58, 0.0032, rng, segments=4, sides=6, curl=0.28)
            counts["tendril_count"] += 1

    counts["support_node_count"] = len(normalized)
    counts["support_edge_count"] = len(_dedupe_edges(_graph_edges(parents)))
    _renormalize(mesh, 2.90)
    return mesh, {
        "family": "fiddlehead",
        "variant": variant,
        "seed": seed,
        "target": "compact crozier-dominant fiddlehead with short stem",
        "root_design": "short curved stem with a large multi-turn terminal crozier and attached scales",
        "leaflet_count": counts["leaflet_count"],
        "tendril_count": counts["tendril_count"],
        "support_node_count": counts["support_node_count"],
    }


def _fractal_fern(seed: int, variant: str) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.052]
    rachis = [0]
    parent = 0
    n = 24 if variant == "wide_frond" else 28
    for i in range(1, n + 1):
        t = i / float(n)
        direction = np.array([0.045 * math.sin(t * math.pi * 0.75), 0.020 * math.sin(t * math.tau * 0.5), 0.150 + 0.035 * math.cos(t * math.pi * 0.55)])
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.048 * (0.966**i), 0.011))
        rachis.append(parent)

    anchors: List[Tuple[int, int, float, int]] = []
    for local_i, anchor in enumerate(rachis[2:-2], start=2):
        t = local_i / float(n)
        envelope = math.sin(math.pi * t) ** 0.46
        side_len = (1.12 if variant == "wide_frond" else 0.98) * envelope + 0.22
        for sign in (-1, 1):
            side_dir = np.array([sign * (1.15 + 0.05 * math.sin(local_i)), 0.036 * math.cos(local_i * 0.6), 0.12 - 0.22 * t])
            p0 = _append_child(nodes, parents, radii, anchor, side_dir, side_len * 0.56, max(0.022 * (1.0 - 0.34 * t), 0.007))
            p1 = _append_child(nodes, parents, radii, p0, side_dir + np.array([0.0, 0.018 * sign, -0.08]), side_len * 0.30, max(0.015 * (1.0 - 0.28 * t), 0.005))
            anchors.extend([(p0, sign, t, 1), (p1, sign, t, 1)])
            if 0.16 < t < 0.88:
                for branch_sign in (-1, 1):
                    if variant == "wide_frond" and branch_sign == -1 and local_i % 2:
                        continue
                    branch_dir = _unit(side_dir + np.array([0.18 * sign, 0.045 * branch_sign, -0.22]))
                    p2 = _append_child(nodes, parents, radii, p1, branch_dir, side_len * (0.18 if variant == "wide_frond" else 0.22), max(0.008 * (1.0 - 0.16 * t), 0.0038))
                    anchors.append((p2, sign, t, 2))

    normalized = _normalize_nodes(nodes, 3.05)
    mesh = _smooth_support_mesh(normalized, _dedupe_edges(_graph_edges(parents)), radii, sides=14, ovality=0.10)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    normal_hint = np.array([0.0, 1.0, 0.16], dtype=float)
    for k, (idx, sign, t, order) in enumerate(anchors):
        axis = _node_axis(normalized, parents, idx)
        base = _unit(axis + np.array([0.06 * sign, 0.0, -0.035]) + rng.normal(0.0, 0.012, 3))
        length = float(rng.uniform(0.095, 0.190) * (1.18 - 0.32 * t) * (0.74 if order == 2 else 1.0))
        width = length * float(rng.uniform(0.20, 0.34))
        _add_thick_lamina(mesh, centers[idx], normalized[idx], base, length, width, normal_hint, rows=7, thickness=0.004, curl=0.040)
        counts["leaflet_count"] += 1
        if order == 1 and k % 3 == 1:
            sub = _unit(0.68 * base + np.array([0.08 * sign, 0.0, -0.10]) + rng.normal(0.0, 0.018, 3))
            _add_lamina(mesh, centers[idx], normalized[idx], sub, length * 0.52, width * 0.68, normal_hint, rows=4, curl=0.034, serration=0.12)
            counts["leaflet_count"] += 1

    counts["support_node_count"] = len(normalized)
    counts["support_edge_count"] = len(_dedupe_edges(_graph_edges(parents)))
    _renormalize(mesh, 2.95)
    return mesh, {
        "family": "compound_fern",
        "variant": variant,
        "seed": seed,
        "target": "wide compound fern with visible second-order pinnae hierarchy",
        "root_design": "broad rachis with long pinnae, second-order branchlets, and attached laminae",
        "leaflet_count": counts["leaflet_count"],
        "support_node_count": counts["support_node_count"],
    }


def _cases(seed: int):
    return [
        ("fiddlehead_compact_crozier_e", _compact_fiddlehead(seed + 21, "compact_crozier")),
        ("fiddlehead_hook_crozier_f", _compact_fiddlehead(seed + 22, "hook_crozier")),
        ("fern_wide_frond_e", _fractal_fern(seed + 23, "wide_frond")),
        ("fern_fractal_frond_f", _fractal_fern(seed + 24, "fractal_frond")),
    ]


def _render_contact(out_dir: Path, rows: List[Dict]) -> Dict:
    out = out_dir / "fern_showcase_roots_contact_sheet_20260512c.png"
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
        "180000",
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
        "revision": "20260512c compact fiddlehead and wider hierarchical fern roots",
    }
    _write_json(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
