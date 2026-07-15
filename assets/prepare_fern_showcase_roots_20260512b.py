#!/usr/bin/env python3
"""Prepare stronger publication-targeted fern/fiddlehead root meshes.

This is the 20260512b follow-up to the first fern showcase sweep.  The 12a
roots were connected, but the fiddlehead root read as a straight stem with a
small terminal knot and the fern fronds were too narrow to show strong depth
changes.  These roots make the semantic handles explicit before SLat recursion:
large crozier coils for fiddleheads and broad pinna-bearing fronds for ferns.
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


DEFAULT_OUT = ROOT_DIR / "results" / "fern_showcase_roots_20260512b"


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


def _fiddlehead_macro(seed: int, variant: str) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.070]

    parent = 0
    stem_steps = 5 if variant == "macro_crozier_c" else 4
    for i in range(1, stem_steps + 1):
        t = i / float(stem_steps)
        direction = np.array([0.10 * math.sin(t * math.pi * 0.7), 0.014 * math.cos(i * 1.1), 0.23 + 0.035 * t])
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.064 * (0.91**i), 0.030))

    stem_tip = np.asarray(nodes[parent], dtype=float)
    coil_center = stem_tip + np.array([0.22 if variant == "macro_crozier_c" else 0.12, 0.0, 0.02])
    turns = 2.18 if variant == "macro_crozier_c" else 1.62
    coil_steps = 48 if variant == "macro_crozier_c" else 38
    start_phase = 0.40 if variant == "macro_crozier_c" else -0.22
    radius0 = 0.92 if variant == "macro_crozier_c" else 0.78
    prev = stem_tip
    coil_indices: List[int] = []
    for i in range(1, coil_steps + 1):
        t = i / float(coil_steps)
        theta = start_phase + turns * math.tau * t
        radius = radius0 * ((1.0 - t) ** 0.86) + 0.045
        p = coil_center + np.array(
            [
                radius * math.cos(theta),
                0.055 * math.sin(theta * 0.62),
                radius * math.sin(theta) + 0.095 * t,
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
            max(0.038 * (1.0 - 0.56 * t), 0.010),
        )
        coil_indices.append(parent)
        prev = p

    normalized = _normalize_nodes(nodes, 2.82)
    mesh = _smooth_support_mesh(normalized, _dedupe_edges(_graph_edges(parents)), radii, sides=16, ovality=0.10)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    normal_hint = np.array([0.0, 1.0, 0.25], dtype=float)
    coil_anchor = np.asarray(normalized[stem_steps], dtype=float)

    stride = 2 if variant == "macro_crozier_c" else 3
    for k, idx in enumerate(coil_indices[4:-2:stride]):
        axis = _node_axis(normalized, parents, idx)
        radial = _unit(np.asarray(normalized[idx]) - coil_anchor)
        leaf_dir = _unit(0.32 * axis + 0.88 * radial + rng.normal(0.0, 0.016, 3))
        length = float(rng.uniform(0.115, 0.205) * (1.0 - 0.008 * k))
        _add_thick_lamina(
            mesh,
            centers[idx],
            normalized[idx],
            leaf_dir,
            length,
            length * float(rng.uniform(0.20, 0.31)),
            normal_hint,
            rows=6,
            thickness=0.0045,
            curl=0.075,
        )
        counts["leaflet_count"] += 1
        if k % 4 == 1:
            _add_curved_tube_detail(
                mesh,
                centers[idx],
                normalized[idx],
                _unit(0.50 * leaf_dir + np.array([0.0, 0.0, -0.18])),
                float(rng.uniform(0.080, 0.140)),
                float(rng.uniform(0.0028, 0.0044)),
                rng,
                segments=4,
                sides=6,
                curl=0.26,
            )
            counts["tendril_count"] += 1

    counts["support_node_count"] = len(normalized)
    counts["support_edge_count"] = len(_dedupe_edges(_graph_edges(parents)))
    _renormalize(mesh, 2.90)
    return mesh, {
        "family": "fiddlehead",
        "variant": variant,
        "seed": seed,
        "target": "large readable fern crozier / fiddlehead spiral",
        "root_design": "short support stem plus large shrinking spiral with attached thick scale leaflets",
        "leaflet_count": counts["leaflet_count"],
        "tendril_count": counts["tendril_count"],
        "support_node_count": counts["support_node_count"],
        "root_revision_reason": "20260512a root was visually a straight stem with a small terminal knot",
    }


def _fern_broad(seed: int, variant: str) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.048]
    rachis = [0]
    parent = 0
    n = 22 if variant == "broad_frond_c" else 26
    for i in range(1, n + 1):
        t = i / float(n)
        direction = np.array(
            [
                0.055 * math.sin(t * math.pi * 0.80),
                0.030 * math.sin(t * math.tau * 0.55),
                0.155 + 0.040 * math.cos(t * math.pi * 0.55),
            ],
            dtype=float,
        )
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.045 * (0.965**i), 0.012))
        rachis.append(parent)

    pinna_nodes: List[Tuple[int, int, float, np.ndarray]] = []
    for local_i, anchor in enumerate(rachis[2:-2], start=2):
        t = local_i / float(n)
        envelope = math.sin(math.pi * t) ** 0.52
        side_len = (0.92 if variant == "broad_frond_c" else 0.78) * envelope + 0.18
        for sign in (-1, 1):
            side_dir = np.array([sign * (1.10 + 0.08 * math.sin(local_i * 0.5)), 0.035 * math.cos(local_i * 0.8), 0.16 - 0.24 * t])
            p0 = _append_child(nodes, parents, radii, anchor, side_dir, side_len * 0.62, max(0.020 * (1.0 - 0.36 * t), 0.007))
            p1 = _append_child(nodes, parents, radii, p0, side_dir + np.array([0.0, 0.018 * sign, -0.10]), side_len * 0.34, max(0.014 * (1.0 - 0.30 * t), 0.005))
            pinna_nodes.extend([(p0, sign, t, side_dir), (p1, sign, t, side_dir)])
            if variant == "branching_frond_d" and 0.22 < t < 0.82 and local_i % 3 != 0:
                p2 = _append_child(nodes, parents, radii, p1, side_dir + np.array([0.0, 0.025 * sign, -0.18]), side_len * 0.20, max(0.008 * (1.0 - 0.20 * t), 0.0038))
                pinna_nodes.append((p2, sign, t, side_dir))

    normalized = _normalize_nodes(nodes, 2.92)
    mesh = _smooth_support_mesh(normalized, _dedupe_edges(_graph_edges(parents)), radii, sides=14, ovality=0.12)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    normal_hint = np.array([0.0, 1.0, 0.18], dtype=float)

    for k, (idx, sign, t, _side_dir) in enumerate(pinna_nodes):
        axis = _node_axis(normalized, parents, idx)
        base = _unit(axis + np.array([0.08 * sign, 0.0, -0.035]) + rng.normal(0.0, 0.012, 3))
        length = float(rng.uniform(0.105, 0.205) * (1.20 - 0.34 * t))
        width = length * float(rng.uniform(0.20, 0.34))
        _add_thick_lamina(mesh, centers[idx], normalized[idx], base, length, width, normal_hint, rows=7, thickness=0.0042, curl=0.044)
        counts["leaflet_count"] += 1
        if variant == "branching_frond_d" and k % 2 == 0:
            sub = _unit(0.68 * base + np.array([0.10 * sign, 0.0, -0.10]) + rng.normal(0.0, 0.018, 3))
            _add_lamina(mesh, centers[idx], normalized[idx], sub, length * 0.50, width * 0.62, normal_hint, rows=4, curl=0.034, serration=0.12)
            counts["leaflet_count"] += 1

    counts["support_node_count"] = len(normalized)
    counts["support_edge_count"] = len(_dedupe_edges(_graph_edges(parents)))
    _renormalize(mesh, 2.95)
    return mesh, {
        "family": "compound_fern",
        "variant": variant,
        "seed": seed,
        "target": "broad compound fern frond with visible pinnae hierarchy",
        "root_design": "wide arched rachis with long connected pinnae and thick attached leaflets",
        "leaflet_count": counts["leaflet_count"],
        "support_node_count": counts["support_node_count"],
        "root_revision_reason": "20260512a fern root was clean but narrow, so depth changes read weakly",
    }


def _cases(seed: int):
    return [
        ("fiddlehead_macro_crozier_c", _fiddlehead_macro(seed + 11, "macro_crozier_c")),
        ("fiddlehead_hook_crozier_d", _fiddlehead_macro(seed + 12, "hook_crozier_d")),
        ("fern_broad_frond_c", _fern_broad(seed + 13, "broad_frond_c")),
        ("fern_branching_frond_d", _fern_broad(seed + 14, "branching_frond_d")),
    ]


def _render_contact(out_dir: Path, rows: List[Dict]) -> Dict:
    out = out_dir / "fern_showcase_roots_contact_sheet_20260512b.png"
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
        "160000",
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
        "revision": "20260512b stronger semantic roots after 20260512a visual QA rejection",
    }
    _write_json(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
