#!/usr/bin/env python3
"""Prepare 20260512d fern/fiddlehead roots for publication-targeted recursion.

The 20260512c sweep ran correctly, but local Blender QA rejected it:
fiddlehead rows still produced torn scale sheets, while fern rows were clean but
too close to no-op depth changes.  This revision changes the root design rather
than only increasing grammar strength:

- fiddleheads are tube-dominant croziers with short stems and connected tubular
  buds, avoiding thin lamina cards as the main recursive handle;
- fern fronds are broader triangular compound fronds with explicit thick
  first- and second-order pinna handles so conservative SLat grammars can make
  visible depth changes without large fragmented sidecars.
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


DEFAULT_OUT = ROOT_DIR / "results" / "fern_showcase_roots_20260512d"


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


def _add_tube_bud(
    mesh: pb.Mesh,
    centers: List[int],
    nodes: List[np.ndarray],
    idx: int,
    direction: np.ndarray,
    length: float,
    radius: float,
    rng: np.random.Generator,
    curl: float = 0.16,
) -> None:
    """Add a connected tubular leaflet/bud instead of a fragile thin lamina."""

    _add_curved_tube_detail(
        mesh,
        centers[idx],
        nodes[idx],
        _unit(direction),
        float(length),
        float(radius),
        rng,
        segments=5,
        sides=7,
        curl=float(curl),
    )


def _solid_fiddlehead(seed: int, variant: str) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.085]

    parent = 0
    stem_steps = 2 if variant == "koru_solid" else 3
    for i in range(1, stem_steps + 1):
        t = i / float(stem_steps)
        direction = np.array([0.10 * math.sin(t * math.pi * 0.5), 0.050 * math.cos(i * 0.7), 0.22 + 0.02 * t])
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.078 * (0.90**i), 0.050))

    stem_tip = np.asarray(nodes[parent], dtype=float)
    center = stem_tip + np.array([0.04 if variant == "koru_solid" else 0.18, 0.0, -0.01])
    turns = 2.15 if variant == "koru_solid" else 2.55
    steps = 62 if variant == "koru_solid" else 70
    radius0 = 1.02 if variant == "koru_solid" else 1.14
    phase = -0.36 if variant == "koru_solid" else 0.08
    coil_indices: List[int] = []
    prev = stem_tip
    for i in range(1, steps + 1):
        t = i / float(steps)
        theta = phase + turns * math.tau * t
        r = radius0 * ((1.0 - t) ** 0.82) + 0.065
        p = center + np.array(
            [
                r * math.cos(theta),
                0.115 * math.sin(theta * 0.52),
                r * math.sin(theta) + 0.075 * t,
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
            max(0.055 * (1.0 - 0.50 * t), 0.018),
        )
        coil_indices.append(parent)
        prev = p

    normalized = _normalize_nodes(nodes, 3.0)
    mesh = _smooth_support_mesh(normalized, _dedupe_edges(_graph_edges(parents)), radii, sides=18, ovality=0.07)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    coil_origin = np.asarray(normalized[stem_steps], dtype=float)

    stride = 3 if variant == "koru_solid" else 2
    for k, idx in enumerate(coil_indices[4:-3:stride]):
        axis = _node_axis(normalized, parents, idx)
        radial = _unit(np.asarray(normalized[idx]) - coil_origin)
        tangent = _unit(0.45 * axis + 0.88 * radial + rng.normal(0.0, 0.010, 3))
        length = float(rng.uniform(0.105, 0.180) * (1.0 - 0.004 * k))
        _add_tube_bud(mesh, centers, normalized, idx, tangent, length, float(rng.uniform(0.0065, 0.0105)), rng, curl=0.18)
        counts["tendril_count"] += 1

    counts["support_node_count"] = len(normalized)
    counts["support_edge_count"] = len(_dedupe_edges(_graph_edges(parents)))
    _renormalize(mesh, 3.0)
    return mesh, {
        "family": "fiddlehead",
        "variant": variant,
        "seed": seed,
        "target": "solid tube-dominant fiddlehead crozier with connected recursive buds",
        "root_design": "short stem, large thick crozier coil, and attached tubular buds; no thin sheet scale sidecars",
        "leaflet_count": 0,
        "tendril_count": counts["tendril_count"],
        "support_node_count": counts["support_node_count"],
    }


def _compound_frond(seed: int, variant: str) -> Tuple[pb.Mesh, Dict]:
    rng = np.random.default_rng(seed)
    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.060]
    rachis = [0]
    parent = 0
    n = 26 if variant == "triangular" else 30
    for i in range(1, n + 1):
        t = i / float(n)
        direction = np.array(
            [
                0.030 * math.sin(t * math.pi * 0.9),
                0.035 * math.sin(t * math.tau * 0.45),
                0.145 + 0.025 * math.cos(t * math.pi * 0.5),
            ],
            dtype=float,
        )
        parent = _append_child(nodes, parents, radii, parent, direction, 1.0, max(0.052 * (0.960**i), 0.012))
        rachis.append(parent)

    anchors: List[Tuple[int, int, float, int]] = []
    for local_i, anchor in enumerate(rachis[2:-2], start=2):
        t = local_i / float(n)
        envelope = math.sin(math.pi * t) ** (0.42 if variant == "triangular" else 0.50)
        side_len = (1.28 if variant == "triangular" else 1.10) * envelope + 0.18
        for sign in (-1, 1):
            side_dir = np.array([sign * (1.20 + 0.05 * math.sin(local_i * 0.7)), 0.060 * math.cos(local_i * 0.5), 0.10 - 0.25 * t])
            p0 = _append_child(nodes, parents, radii, anchor, side_dir, side_len * 0.54, max(0.026 * (1.0 - 0.30 * t), 0.008))
            p1 = _append_child(nodes, parents, radii, p0, side_dir + np.array([0.0, 0.022 * sign, -0.10]), side_len * 0.30, max(0.018 * (1.0 - 0.30 * t), 0.0055))
            anchors.extend([(p0, sign, t, 1), (p1, sign, t, 1)])
            if 0.14 < t < 0.90:
                for branch_sign in (-1, 1):
                    if variant == "triangular" and local_i % 2 and branch_sign < 0:
                        continue
                    branch_dir = _unit(side_dir + np.array([0.16 * sign, 0.055 * branch_sign, -0.25]))
                    p2 = _append_child(nodes, parents, radii, p1, branch_dir, side_len * (0.20 if variant == "triangular" else 0.24), max(0.010 * (1.0 - 0.18 * t), 0.0042))
                    anchors.append((p2, sign, t, 2))

    normalized = _normalize_nodes(nodes, 3.08)
    mesh = _smooth_support_mesh(normalized, _dedupe_edges(_graph_edges(parents)), radii, sides=15, ovality=0.08)
    centers = getattr(mesh, "center_indices")
    counts = _counts()
    normal_hint = np.array([0.0, 1.0, 0.18], dtype=float)

    for k, (idx, sign, t, order) in enumerate(anchors):
        axis = _node_axis(normalized, parents, idx)
        base = _unit(axis + np.array([0.050 * sign, 0.0, -0.035]) + rng.normal(0.0, 0.010, 3))
        length = float(rng.uniform(0.105, 0.210) * (1.22 - 0.36 * t) * (0.76 if order == 2 else 1.0))
        width = length * float(rng.uniform(0.22, 0.36))
        _add_thick_lamina(
            mesh,
            centers[idx],
            normalized[idx],
            base,
            length,
            width,
            normal_hint,
            rows=7,
            thickness=0.0050,
            curl=0.045,
        )
        counts["leaflet_count"] += 1
        if order == 1 and k % 4 == 1:
            _add_tube_bud(
                mesh,
                centers,
                normalized,
                idx,
                _unit(0.70 * base + np.array([0.10 * sign, 0.0, -0.12])),
                length * 0.55,
                0.0048,
                rng,
                curl=0.12,
            )
            counts["tendril_count"] += 1

    counts["support_node_count"] = len(normalized)
    counts["support_edge_count"] = len(_dedupe_edges(_graph_edges(parents)))
    _renormalize(mesh, 3.04)
    return mesh, {
        "family": "compound_fern",
        "variant": variant,
        "seed": seed,
        "target": "broad compound fern frond with visible recursive pinnae hierarchy",
        "root_design": "triangular rachis, thick primary/secondary pinnae, attached laminae, and explicit refinement anchors",
        "leaflet_count": counts["leaflet_count"],
        "tendril_count": counts["tendril_count"],
        "support_node_count": counts["support_node_count"],
    }


def _cases(seed: int):
    return [
        ("fiddlehead_solid_koru_g", _solid_fiddlehead(seed + 31, "koru_solid")),
        ("fiddlehead_bud_crozier_h", _solid_fiddlehead(seed + 32, "bud_crozier")),
        ("fern_triangular_frond_g", _compound_frond(seed + 33, "triangular")),
        ("fern_lacy_frond_h", _compound_frond(seed + 34, "lacy")),
    ]


def _render_contact(out_dir: Path, rows: List[Dict]) -> Dict:
    out = out_dir / "fern_showcase_roots_contact_sheet_20260512d.png"
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
        "200000",
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
        "revision": "20260512d solid crozier and visible compound fern refinement roots",
    }
    _write_json(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
