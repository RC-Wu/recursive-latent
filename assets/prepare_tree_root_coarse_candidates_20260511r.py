#!/usr/bin/env python3
"""Prepare coarse first-split tree-root modules for the 20260511r SLat sweep.

The 20260511q root modules were connected, but their terminal rootlets caused
the recursive SLat operator to produce small islands instead of a clean
thick-to-thin hierarchy.  This script creates input roots with the same explicit
first-split semantics, but suppresses fine root hairs so the next remote sweep
can test coarse branch recursion first.
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
    _append_child,
    _dedupe_edges,
    _mesh_stats,
    _renormalize_mesh,
    _smooth_support_mesh,
)


DEFAULT_OUT = ROOT_DIR / "results" / "tree_root_coarse_candidates_20260511r"
CONNECTIVITY_LCR_MIN = 0.999
SURFACE_STRATEGY = "r_coarse_first_split_swept_taper_no_terminal_rootlet_hairs"


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True, sort_keys=True), encoding="utf-8")


def _graph_edges(parents: List[int]) -> List[Tuple[int, int]]:
    return [(int(parent), int(idx)) for idx, parent in enumerate(parents) if int(parent) >= 0]


def _build_coarse_module(seed: int, variant: str) -> Tuple[pb.Mesh, Dict, Dict]:
    rng = np.random.default_rng(seed)
    downward = variant.endswith("_down")
    sign = -1.0 if downward else 1.0
    asym = "asym" in variant
    swept = "swept" in variant

    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.086 if "thick" in variant else 0.074]

    trunk_steps = 6 if "long" in variant else 5
    trunk = [0]
    parent = 0
    for i in range(1, trunk_steps + 1):
        t = i / float(trunk_steps)
        direction = np.array(
            [
                0.030 * math.sin(t * math.pi * 1.15 + 0.2),
                0.022 * math.sin(t * math.tau + 0.5),
                sign * (0.31 + 0.040 * math.cos(t * math.pi)),
            ],
            dtype=float,
        )
        parent = _append_child(
            nodes,
            parents,
            radii,
            parent,
            direction,
            length=0.94 if "compact" in variant else 1.04,
            radius=max(float(radii[0]) * (1.0 - 0.070 * i), 0.040),
        )
        trunk.append(parent)

    split_anchor = trunk[3 if trunk_steps == 5 else 4]
    child_angles = (-32.0, 30.0) if not asym else (-42.0, 18.0, 38.0)
    branch_records: List[Dict] = []
    for child_i, degrees in enumerate(child_angles):
        theta = math.radians(degrees)
        base_dir = np.array(
            [
                math.sin(theta) * (0.56 + 0.04 * child_i),
                math.cos(theta) * (0.32 + 0.05 * math.sin(child_i + 0.4)),
                sign * (0.68 - 0.045 * child_i),
            ],
            dtype=float,
        )
        first = split_anchor
        branch_nodes: List[int] = []
        branch_steps = 4 if "short" in variant else 5
        for j in range(branch_steps):
            local = j / max(branch_steps - 1, 1)
            bend = np.array(
                [
                    (0.045 if swept else 0.025) * math.sin(local * math.pi + 0.5 * child_i),
                    0.045 * math.cos(local * math.pi * 0.7 + child_i),
                    sign * 0.035 * math.sin(local * math.pi),
                ],
                dtype=float,
            )
            first = _append_child(
                nodes,
                parents,
                radii,
                first,
                base_dir + bend,
                length=(0.62 + 0.035 * child_i) * (0.90 ** j),
                radius=max(0.043 * (0.76 ** j), 0.012),
            )
            branch_nodes.append(first)
        branch_records.append(
            {
                "branch_index": int(child_i),
                "angle_degrees": float(degrees),
                "node_indices": [int(x) for x in branch_nodes],
                "terminal_node": int(branch_nodes[-1]),
            }
        )

    if "stub" in variant:
        for record in branch_records:
            anchor = record["node_indices"][1]
            side = -1.0 if record["branch_index"] % 2 == 0 else 1.0
            _append_child(
                nodes,
                parents,
                radii,
                anchor,
                np.array([side * 0.30, 0.10, sign * 0.62], dtype=float),
                length=0.26,
                radius=0.010,
            )

    mesh = _smooth_support_mesh(
        nodes,
        _dedupe_edges(_graph_edges(parents)),
        radii,
        sides=16 if "smooth" in variant or "thick" in variant else 14,
        ovality=0.09 if "smooth" in variant else 0.13,
    )
    _renormalize_mesh(mesh, extent=2.85)

    terminal_nodes = [int(record["terminal_node"]) for record in branch_records]
    controls = {
        "variant": variant,
        "orientation": "downward_original_z" if downward else "upward_original_z",
        "first_split_anchor_node": int(split_anchor),
        "trunk_node_count": int(len(trunk)),
        "primary_branch_count": int(len(branch_records)),
        "terminal_detail_anchor_nodes": terminal_nodes,
        "support_node_count": int(len(nodes)),
        "support_edge_count": int(len(_dedupe_edges(_graph_edges(parents)))),
        "suggested_trellis_growth_axis": "y",
        "suggested_trellis_growth_sign_primary": 1 if downward else -1,
        "axis_reason": "workflow maps original z to latent -y; downward root tips correspond to y,+1, upward tips to y,-1",
        "branch_records": branch_records,
        "semantic_root_handle": {
            "root_handle": "coarse trunk segment ending at first_split_anchor_node",
            "growth_anchor": "first_split_anchor_node plus primary branch bodies",
            "terminal_detail_anchor_nodes": terminal_nodes,
        },
    }
    grammar = {
        "symbols": "coarse_root_trunk -> first_split(primary_roots) -> coarse_tapering_child_roots",
        "root_module_role": "input handle for remote SLat coarse first-split grammar",
        "manual_semantic_definition": True,
        "terminal_rootlet_suppression": True,
    }
    return mesh, controls, grammar


def _case_specs(seed: int) -> List[Dict]:
    variants = [
        ("coarse_root_down_compact_a", "compact_down", 31),
        ("coarse_root_down_smooth_b", "smooth_down", 32),
        ("coarse_root_down_thick_stub_c", "thick_stub_down", 33),
        ("coarse_root_down_swept_asym_d", "swept_asym_down", 34),
        ("coarse_root_up_compact_e", "compact_up", 41),
        ("coarse_root_up_smooth_f", "smooth_up", 42),
        ("coarse_root_up_thick_stub_g", "thick_stub_up", 43),
        ("coarse_root_up_swept_asym_h", "swept_asym_up", 44),
    ]
    specs: List[Dict] = []
    for case_id, variant, offset in variants:
        mesh, controls, grammar = _build_coarse_module(seed + offset, variant)
        specs.append(
            {
                "case_id": case_id,
                "family": "tree_root_first_split",
                "motif": "coarse_thick_to_thin_first_split_root_module",
                "mesh": mesh,
                "controls": controls,
                "grammar_mapping": grammar,
                "seed": int(seed + offset),
                "case_role": "local_input_root_module_for_remote_slat_recursion",
                "why_candidate": "Connected coarse first-split root handle without terminal rootlet hairs, designed after q rootlet-dust failure.",
                "operators": [
                    "procedural_baselines.pb.Mesh",
                    "r_coarse_first_split_swept_taper_no_terminal_rootlet_hairs",
                    "explicit_first_split_anchor_metadata",
                    "local_input_only",
                ],
            }
        )
    return specs


def _render_contact_sheet(out_dir: Path, rows: List[Dict], max_faces: int) -> Dict:
    script = ASSET_DIR / "render_mesh_contact_sheet.py"
    out_path = out_dir / "tree_root_coarse_candidates_contact_sheet.png"
    cmd = [sys.executable, str(script), "--out", str(out_path), "--views", "iso", "front", "side", "--max-faces", str(max_faces)]
    for row in rows:
        cmd.extend(["--case", f"{row['case_id']}={row['mesh_path']}"])
    try:
        result = subprocess.run(cmd, cwd=str(ROOT_DIR), check=True, text=True, capture_output=True)
        return {"status": "ok", "path": str(out_path), "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except Exception as exc:
        return {"status": "failed", "path": str(out_path), "error": str(exc)}


def materialize(out_dir: Path = DEFAULT_OUT, seed: int = 20260511, render_preview: bool = True, preview_max_faces: int = 120000) -> Dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    specs = _case_specs(seed)
    rows: List[Dict] = []
    metrics_rows: List[Dict] = []

    for spec in specs:
        case_dir = out_dir / spec["case_id"]
        mesh_path = case_dir / f"{spec['case_id']}.obj"
        case_dir.mkdir(parents=True, exist_ok=True)
        pb.write_obj(mesh_path, spec["mesh"])
        metrics = _mesh_stats(spec["mesh"])
        if metrics["largest_mesh_component_vertex_ratio"] < CONNECTIVITY_LCR_MIN:
            raise RuntimeError(f"{spec['case_id']} failed connectivity gate: {metrics}")
        metadata = {
            "case_id": spec["case_id"],
            "family": spec["family"],
            "motif": spec["motif"],
            "mesh_path": str(mesh_path),
            "seed": int(spec["seed"]),
            "case_role": spec["case_role"],
            "operators": spec["operators"],
            "operator_composition": " -> ".join(spec["operators"]),
            "surface_strategy": SURFACE_STRATEGY,
            "controls": spec["controls"],
            "grammar_mapping": spec["grammar_mapping"],
            "why_candidate": spec["why_candidate"],
            "initial_mesh_metrics": metrics,
            "evidence_boundary": {
                "local_generation_only": True,
                "remote_jobs_launched": False,
                "publication_evidence_requires_remote_slat_outputs": True,
                "source_script": "assets/prepare_tree_root_coarse_candidates_20260511r.py",
            },
        }
        metadata_path = case_dir / f"{spec['case_id']}_metadata.json"
        _write_json(metadata_path, metadata)
        row = {
            "case_id": spec["case_id"],
            "family": spec["family"],
            "motif": spec["motif"],
            "mesh_path": str(mesh_path),
            "metadata_path": str(metadata_path),
            "seed": int(spec["seed"]),
            "orientation": spec["controls"]["orientation"],
            "first_split_anchor_node": spec["controls"]["first_split_anchor_node"],
            "primary_branch_count": spec["controls"]["primary_branch_count"],
            "support_node_count": spec["controls"]["support_node_count"],
            "support_edge_count": spec["controls"]["support_edge_count"],
            "rootlet_count": 0,
            "suggested_trellis_growth_axis": spec["controls"]["suggested_trellis_growth_axis"],
            "suggested_trellis_growth_sign_primary": spec["controls"]["suggested_trellis_growth_sign_primary"],
            "why_candidate": spec["why_candidate"],
        }
        rows.append(row)
        metrics_rows.append({"case_id": spec["case_id"], **metrics})

    manifest_csv = out_dir / "manifest.csv"
    with manifest_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    metrics_csv = out_dir / "initial_metrics.csv"
    with metrics_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(metrics_rows[0].keys()))
        writer.writeheader()
        writer.writerows(metrics_rows)
    _write_json(out_dir / "manifest.json", rows)
    _write_json(out_dir / "initial_metrics.json", metrics_rows)

    render_result = _render_contact_sheet(out_dir, rows, preview_max_faces) if render_preview else {"status": "skipped"}
    summary = {
        "status": "ok",
        "out_dir": str(out_dir),
        "case_count": len(rows),
        "manifest_csv": str(manifest_csv),
        "metrics_csv": str(metrics_csv),
        "render_preview": render_result,
        "publication_boundary": "input roots only; remote SLat recursion, metrics, and Blender QA are required before any positive claim",
    }
    _write_json(out_dir / "summary.json", summary)
    readme = out_dir / "README.md"
    readme.write_text(
        "# Tree-Root Coarse Candidates 20260511r\n\n"
        "Coarse first-split root input modules generated after the 20260511q rootlet-dust failure. "
        "These inputs intentionally suppress terminal root hairs. They are not publication evidence until remote SLat recursion, metrics, and Blender QA pass.\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260511)
    parser.add_argument("--no-preview", action="store_true")
    parser.add_argument("--preview-max-faces", type=int, default=120000)
    args = parser.parse_args()
    summary = materialize(args.out, args.seed, not args.no_preview, args.preview_max_faces)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
