#!/usr/bin/env python3
"""Prepare publication-targeted fern and fiddlehead root meshes.

The meshes are root candidates for the remote TRELLIS2/SLat recursive executor.
They are generated as connected OBJ supports with attached semantic leaflets so
that recursion starts from biologically meaningful handles.
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


DEFAULT_OUT = ROOT_DIR / "results" / "fern_showcase_roots_20260512a"


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


def _fiddlehead_showcase(seed: int, variant: str) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.060]

    parent = 0
    stem_steps = 9 if variant == "curl_a" else 7
    for i in range(1, stem_steps + 1):
        t = i / float(stem_steps)
        direction = np.array([0.04 * math.sin(t * math.pi), 0.018 * math.sin(i * 0.8), 0.20 + 0.06 * t])
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.058 * (0.94**i), 0.026))

    stem_tip = np.asarray(nodes[parent], dtype=float)
    coil_center = stem_tip + np.array([0.34 if variant == "curl_a" else 0.22, 0.0, 0.06])
    turns = 1.82 if variant == "curl_a" else 2.28
    coil_steps = 32 if variant == "curl_a" else 42
    prev = stem_tip
    coil_indices: List[int] = []
    for i in range(1, coil_steps + 1):
        t = i / float(coil_steps)
        theta = turns * math.tau * t + (0.72 if variant == "curl_a" else 0.20)
        radius = (0.62 if variant == "curl_a" else 0.54) * ((1.0 - t) ** 0.78) + 0.035
        p = coil_center + np.array(
            [
                radius * math.cos(theta),
                0.030 * math.sin(theta * 0.55),
                radius * math.sin(theta) + 0.035 * t,
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
            max(0.034 * (1.0 - 0.58 * t), 0.008),
        )
        coil_indices.append(parent)
        prev = p

    normalized = _normalize_nodes(nodes, 2.72)
    mesh = _smooth_support_mesh(normalized, _dedupe_edges(_graph_edges(parents)), radii, sides=14, ovality=0.12)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    normal_hint = np.array([0.0, 1.0, 0.20], dtype=float)

    detail_stride = 3 if variant == "curl_a" else 4
    for k, idx in enumerate(coil_indices[3:-2:detail_stride]):
        axis = _node_axis(normalized, parents, idx)
        radial = _unit(np.asarray(normalized[idx]) - np.asarray(normalized[stem_steps]))
        leaf_dir = _unit(0.38 * axis + 0.76 * radial + rng.normal(0.0, 0.018, 3))
        length = float(rng.uniform(0.105, 0.185) * (1.05 if variant == "curl_a" else 0.88))
        _add_lamina(mesh, centers[idx], normalized[idx], leaf_dir, length, length * 0.22, normal_hint, rows=5, curl=0.060, serration=0.11)
        counts["leaflet_count"] += 1
        if k % 3 == 0:
            _add_curved_tube_detail(
                mesh,
                centers[idx],
                normalized[idx],
                _unit(0.42 * leaf_dir + np.array([0.0, 0.0, -0.18])),
                float(rng.uniform(0.080, 0.130)),
                float(rng.uniform(0.0030, 0.0046)),
                rng,
                segments=4,
                sides=6,
                curl=0.38,
            )
            counts["tendril_count"] += 1

    counts["support_node_count"] = len(normalized)
    counts["support_edge_count"] = len(_dedupe_edges(_graph_edges(parents)))
    _renormalize(mesh, 2.80)
    meta = {
        "family": "fiddlehead",
        "variant": variant,
        "seed": seed,
        "target": "green fern crozier / fiddlehead spiral",
        "root_design": "connected swept stem plus shrinking spiral with attached scale leaflets",
        "leaflet_count": counts["leaflet_count"],
        "tendril_count": counts["tendril_count"],
        "support_node_count": counts["support_node_count"],
    }
    return mesh, meta


def _fern_showcase(seed: int, variant: str) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.040]
    rachis = [0]
    parent = 0
    n = 25 if variant == "compound_a" else 30
    for i in range(1, n + 1):
        t = i / float(n)
        direction = np.array(
            [
                0.035 * math.sin(t * math.pi * 0.90),
                0.020 * math.sin(t * math.tau * 0.75),
                0.155 + 0.046 * math.cos(t * math.pi * 0.72),
            ],
            dtype=float,
        )
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.040 * (0.972**i), 0.010))
        rachis.append(parent)

    pinna_nodes: List[Tuple[int, int, float, np.ndarray]] = []
    for local_i, anchor in enumerate(rachis[2:-2], start=2):
        t = local_i / float(n)
        side_len = (0.78 if variant == "compound_a" else 0.70) * (math.sin(math.pi * t) ** 0.58) + 0.12
        if variant == "lacy_b" and local_i % 5 == 0:
            side_len *= 0.82
        for sign in (-1, 1):
            side_dir = np.array([sign * (0.94 + 0.10 * math.sin(local_i * 0.7)), 0.028 * math.cos(local_i), 0.18 - 0.24 * t])
            p0 = _append_child(nodes, parents, radii, anchor, side_dir, side_len * 0.55, max(0.017 * (1.0 - 0.36 * t), 0.006))
            p1 = _append_child(nodes, parents, radii, p0, side_dir + np.array([0.0, 0.016 * sign, -0.10]), side_len * 0.32, max(0.012 * (1.0 - 0.30 * t), 0.0045))
            p2 = _append_child(nodes, parents, radii, p1, side_dir + np.array([0.0, 0.012 * sign, -0.16]), side_len * 0.20, max(0.008 * (1.0 - 0.25 * t), 0.0035))
            pinna_nodes.extend([(p0, sign, t, side_dir), (p1, sign, t, side_dir), (p2, sign, t, side_dir)])

    normalized = _normalize_nodes(nodes, 2.82)
    mesh = _smooth_support_mesh(normalized, _dedupe_edges(_graph_edges(parents)), radii, sides=12, ovality=0.16)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    normal_hint = np.array([0.0, 1.0, 0.15], dtype=float)

    for k, (idx, sign, t, side_dir) in enumerate(pinna_nodes):
        axis = _node_axis(normalized, parents, idx)
        base = _unit(axis + np.array([0.10 * sign, 0.0, -0.03]) + rng.normal(0.0, 0.014, 3))
        length = float(rng.uniform(0.090, 0.180) * (1.16 - 0.32 * t))
        width = length * float(rng.uniform(0.18, 0.28))
        if variant == "lacy_b":
            _add_lamina(mesh, centers[idx], normalized[idx], base, length, width, normal_hint, rows=5, curl=0.050, serration=0.16)
        else:
            _add_thick_lamina(mesh, centers[idx], normalized[idx], base, length, width, normal_hint, rows=6, thickness=0.004, curl=0.042)
        counts["leaflet_count"] += 1
        if variant == "lacy_b" and k % 3 == 0:
            sub = _unit(0.66 * base + np.array([0.08 * sign, 0.0, -0.08]) + rng.normal(0.0, 0.020, 3))
            _add_lamina(mesh, centers[idx], normalized[idx], sub, length * 0.55, width * 0.70, normal_hint, rows=4, curl=0.035, serration=0.12)
            counts["leaflet_count"] += 1

    counts["support_node_count"] = len(normalized)
    counts["support_edge_count"] = len(_dedupe_edges(_graph_edges(parents)))
    _renormalize(mesh, 2.90)
    meta = {
        "family": "compound_fern",
        "variant": variant,
        "seed": seed,
        "target": "compound fern frond with rachis, pinnae, and fine leaflet repetition",
        "root_design": "connected arched rachis with attached alternating pinnae and secondary leaflets",
        "leaflet_count": counts["leaflet_count"],
        "support_node_count": counts["support_node_count"],
    }
    return mesh, meta


def _cases(seed: int):
    return [
        ("fiddlehead_showcase_curl_a", _fiddlehead_showcase(seed + 1, "curl_a")),
        ("fiddlehead_nested_curl_b", _fiddlehead_showcase(seed + 2, "nested_b")),
        ("fern_showcase_compound_a", _fern_showcase(seed + 3, "compound_a")),
        ("fern_showcase_lacy_b", _fern_showcase(seed + 4, "lacy_b")),
    ]


def _render_contact(out_dir: Path, rows: List[Dict]) -> Dict:
    out = out_dir / "fern_showcase_roots_contact_sheet_20260512a.png"
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
        "120000",
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
    }
    _write_json(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

