#!/usr/bin/env python3
"""Prepare clean first-split tree-root modules for the 20260511q SLat sweep.

This script only creates input root modules.  It does not generate the final
evidence case; publication evidence still comes from the remote
Trellis2/SLat recursive grammar workflow.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
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
    _append_child,
    _dedupe_edges,
    _mesh_stats,
    _renormalize_mesh,
    _smooth_support_mesh,
    _unit,
)


DEFAULT_OUT = ROOT_DIR / "results" / "tree_root_firstsplit_candidates_20260511q"
CONNECTIVITY_LCR_MIN = 0.999
SURFACE_STRATEGY = "q_first_split_shared_center_swept_tapered_roots"


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True, sort_keys=True), encoding="utf-8")


def _graph_edges(parents: List[int]) -> List[Tuple[int, int]]:
    return [(int(parent), int(idx)) for idx, parent in enumerate(parents) if int(parent) >= 0]


def _child_indices(parents: List[int], idx: int) -> List[int]:
    return [i for i, parent in enumerate(parents) if int(parent) == int(idx)]


def _add_rootlet_bundle(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    center_indices: List[int],
    anchors: List[int],
    rng: np.random.Generator,
    scale: float,
    count_per_anchor: int,
    downward_sign: float,
) -> int:
    count = 0
    for anchor in anchors:
        base = np.asarray(nodes[anchor], dtype=float)
        trunk = _unit(base - np.asarray(nodes[max(anchor - 1, 0)], dtype=float))
        for _ in range(count_per_anchor):
            theta = float(rng.uniform(0.0, math.tau))
            radial = np.array([math.cos(theta), math.sin(theta), 0.0], dtype=float)
            root_dir = _unit(0.70 * radial + 0.38 * trunk + np.array([0.0, 0.0, downward_sign * 0.42]))
            _add_curved_tube_detail(
                mesh,
                center_indices[anchor],
                base,
                root_dir,
                length=float(rng.uniform(0.14, 0.28)) * scale,
                radius=float(rng.uniform(0.0035, 0.0065)) * scale,
                rng=rng,
                segments=4,
                sides=6,
                curl=float(rng.uniform(0.08, 0.20)),
            )
            count += 1
    return count


def _build_firstsplit_module(seed: int, variant: str) -> Tuple[pb.Mesh, Dict, Dict]:
    rng = np.random.default_rng(seed)
    downward = variant.endswith("_down")
    sign = -1.0 if downward else 1.0

    nodes: List[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    parents: List[int] = [-1]
    radii: List[float] = [0.070]

    trunk_steps = 6 if "long" in variant else 5
    trunk: List[int] = [0]
    parent = 0
    for i in range(1, trunk_steps + 1):
        t = i / float(trunk_steps)
        direction = np.array(
            [
                0.045 * math.sin(t * math.pi * 1.3),
                0.030 * math.sin(t * math.tau + 0.4),
                sign * (0.28 + 0.055 * math.cos(t * math.pi)),
            ],
            dtype=float,
        )
        parent = _append_child(
            nodes,
            parents,
            radii,
            parent,
            direction,
            length=0.92 if "compact" in variant else 1.0,
            radius=max(0.070 * (1.0 - 0.075 * i), 0.036),
        )
        trunk.append(parent)

    split_anchor = trunk[3 if trunk_steps == 5 else 4]
    branch_records: List[Dict] = []
    child_angles = (-34.0, 28.0) if "asym" not in variant else (-44.0, 18.0, 43.0)
    for child_i, degrees in enumerate(child_angles):
        theta = math.radians(degrees)
        base_dir = np.array(
            [
                math.sin(theta) * (0.55 + 0.08 * child_i),
                math.cos(theta) * (0.38 + 0.05 * math.sin(child_i)),
                sign * (0.70 - 0.07 * child_i),
            ],
            dtype=float,
        )
        first = split_anchor
        branch_nodes: List[int] = []
        branch_steps = 5 if "deep" in variant else 4
        for j in range(branch_steps):
            local = j / max(branch_steps - 1, 1)
            bend = np.array(
                [
                    0.08 * math.sin(local * math.pi + child_i),
                    0.07 * math.cos(local * math.pi * 0.8 + 0.7 * child_i),
                    sign * 0.05 * math.sin(local * math.pi),
                ],
                dtype=float,
            )
            first = _append_child(
                nodes,
                parents,
                radii,
                first,
                base_dir + bend,
                length=(0.58 + 0.05 * child_i) * (0.94 ** j),
                radius=max(0.039 * (0.73 ** j), 0.010),
            )
            branch_nodes.append(first)
        branch_records.append(
            {
                "branch_index": child_i,
                "angle_degrees": float(degrees),
                "node_indices": branch_nodes,
                "terminal_node": int(branch_nodes[-1]),
            }
        )

    secondary_count = 0
    if "sidecar" in variant or "deep" in variant:
        for record in branch_records:
            anchor = record["node_indices"][1]
            side_dir = _unit(np.asarray(nodes[anchor], dtype=float) - np.asarray(nodes[split_anchor], dtype=float))
            for side_sign in (-1.0, 1.0):
                child = _append_child(
                    nodes,
                    parents,
                    radii,
                    anchor,
                    np.array([side_sign * 0.45, 0.22 * math.sin(record["branch_index"] + side_sign), sign * 0.62]) + side_dir * 0.34,
                    length=0.36,
                    radius=0.014,
                )
                _append_child(
                    nodes,
                    parents,
                    radii,
                    child,
                    np.array([side_sign * 0.38, 0.18, sign * 0.74]),
                    length=0.26,
                    radius=0.007,
                )
                secondary_count += 2

    mesh = _smooth_support_mesh(
        nodes,
        _dedupe_edges(_graph_edges(parents)),
        radii,
        sides=14 if "smooth" in variant else 12,
        ovality=0.11 if "smooth" in variant else 0.16,
    )
    center_indices = getattr(mesh, "center_indices")

    terminal_nodes = [int(record["terminal_node"]) for record in branch_records]
    mid_nodes = [int(record["node_indices"][max(1, len(record["node_indices"]) // 2)]) for record in branch_records]
    rootlet_count = _add_rootlet_bundle(
        mesh,
        nodes,
        center_indices,
        anchors=mid_nodes + terminal_nodes,
        rng=rng,
        scale=1.0,
        count_per_anchor=2 if "dense" in variant else 1,
        downward_sign=sign,
    )

    if "root_hairs" in variant:
        hair_anchors = trunk[1:-1] + mid_nodes
        rootlet_count += _add_rootlet_bundle(
            mesh,
            nodes,
            center_indices,
            anchors=hair_anchors,
            rng=rng,
            scale=0.66,
            count_per_anchor=1,
            downward_sign=sign,
        )

    _renormalize_mesh(mesh, extent=2.85)
    controls = {
        "variant": variant,
        "orientation": "downward_original_z" if downward else "upward_original_z",
        "first_split_anchor_node": int(split_anchor),
        "trunk_node_count": int(len(trunk)),
        "primary_branch_count": int(len(branch_records)),
        "secondary_branch_node_count": int(secondary_count),
        "rootlet_count": int(rootlet_count),
        "support_node_count": int(len(nodes)),
        "support_edge_count": int(len(_dedupe_edges(_graph_edges(parents)))),
        "suggested_trellis_growth_axis": "y",
        "suggested_trellis_growth_sign_primary": 1 if downward else -1,
        "axis_reason": "workflow maps original z to latent -y; downward root tips correspond to y,+1, upward tips to y,-1",
        "branch_records": branch_records,
        "semantic_root_handle": {
            "root_handle": "trunk segment ending at first_split_anchor_node",
            "growth_anchor": "first_split_anchor_node plus primary branch mid/terminal nodes",
            "terminal_detail_anchor_nodes": terminal_nodes,
        },
    }
    grammar = {
        "symbols": "root_trunk -> first_split(primary_roots) -> tapering_child_roots -> attached_rootlets",
        "root_module_role": "input handle for remote SLat recursive first-split grammar",
        "manual_semantic_definition": True,
    }
    return mesh, controls, grammar


def _case_specs(seed: int) -> List[Dict]:
    variants = [
        ("first_split_root_down_compact_a", "compact_down", 11),
        ("first_split_root_down_smooth_b", "smooth_down", 12),
        ("first_split_root_down_sidecar_c", "sidecar_down", 13),
        ("first_split_root_down_deep_dense_d", "deep_dense_root_hairs_down", 14),
        ("first_split_root_up_compact_e", "compact_up", 21),
        ("first_split_root_up_smooth_f", "smooth_up", 22),
        ("first_split_root_up_sidecar_g", "sidecar_up", 23),
        ("first_split_root_up_asym_deep_h", "asym_deep_root_hairs_up", 24),
    ]
    specs: List[Dict] = []
    for case_id, variant, offset in variants:
        mesh, controls, grammar = _build_firstsplit_module(seed + offset, variant)
        specs.append(
            {
                "case_id": case_id,
                "family": "tree_root_first_split",
                "motif": "thick_to_thin_first_split_root_module",
                "mesh": mesh,
                "controls": controls,
                "grammar_mapping": grammar,
                "seed": int(seed + offset),
                "case_role": "local_input_root_module_for_remote_slat_recursion",
                "why_candidate": "Clean connected first-split root handle with explicit trunk/split/terminal anchors for q remote grammar sweep.",
                "operators": [
                    "procedural_baselines.pb.Mesh",
                    "q_first_split_shared_center_swept_tapered_roots",
                    "explicit_first_split_anchor_metadata",
                    "attached_curved_tube_rootlets",
                    "local_input_only",
                ],
            }
        )
    return specs


def _render_contact_sheet(out_dir: Path, rows: List[Dict], max_faces: int) -> Dict:
    script = ASSET_DIR / "render_mesh_contact_sheet.py"
    out_path = out_dir / "tree_root_firstsplit_candidates_contact_sheet.png"
    cmd = [sys.executable, str(script), "--out", str(out_path), "--views", "iso", "front", "side", "--max-faces", str(max_faces)]
    for row in rows:
        cmd.extend(["--case", f"{row['case_id']}={row['mesh_path']}"])
    try:
        result = subprocess.run(cmd, cwd=str(ROOT_DIR), check=True, text=True, capture_output=True)
        return {"status": "ok", "path": str(out_path), "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except Exception as exc:
        return {"status": "failed", "path": str(out_path), "error": str(exc)}


def materialize(
    out_dir: Path = DEFAULT_OUT,
    seed: int = 20260511,
    render_preview: bool = True,
    preview_max_faces: int = 120000,
) -> Dict:
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
                "source_script": "assets/prepare_tree_root_firstsplit_candidates_20260511q.py",
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
            "suggested_trellis_growth_axis": spec["controls"]["suggested_trellis_growth_axis"],
            "suggested_trellis_growth_sign_primary": spec["controls"]["suggested_trellis_growth_sign_primary"],
            "first_split_anchor_node": spec["controls"]["first_split_anchor_node"],
            "primary_branch_count": spec["controls"]["primary_branch_count"],
            "rootlet_count": spec["controls"]["rootlet_count"],
            "support_node_count": spec["controls"]["support_node_count"],
            "support_edge_count": spec["controls"]["support_edge_count"],
            "vertices": metrics["vertices"],
            "faces": metrics["faces"],
            "mesh_component_count": metrics["mesh_component_count"],
            "largest_mesh_component_vertex_ratio": metrics["largest_mesh_component_vertex_ratio"],
            "bbox_diag": metrics["bbox_diag"],
            "why_candidate": spec["why_candidate"],
        }
        rows.append(row)
        metrics_rows.append({"case_id": spec["case_id"], **metrics})

    manifest_fields = list(rows[0].keys()) if rows else []
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerows(rows)
    _write_json(out_dir / "manifest.json", rows)

    metric_fields = sorted({key for row in metrics_rows for key in row if not isinstance(row.get(key), (list, dict))})
    with (out_dir / "initial_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        for row in metrics_rows:
            writer.writerow({key: row.get(key) for key in metric_fields})
    _write_json(out_dir / "initial_metrics.json", metrics_rows)

    contact = {"status": "skipped", "path": ""}
    if render_preview:
        contact = _render_contact_sheet(out_dir, rows, preview_max_faces)
    summary = {
        "out_dir": str(out_dir),
        "num_cases": len(rows),
        "case_ids": [row["case_id"] for row in rows],
        "surface_strategy": SURFACE_STRATEGY,
        "connectivity_gate": {
            "largest_component_vertex_ratio_min": CONNECTIVITY_LCR_MIN,
            "all_cases_passed": all(float(row["largest_mesh_component_vertex_ratio"]) >= CONNECTIVITY_LCR_MIN for row in rows),
        },
        "manifest_csv": str(out_dir / "manifest.csv"),
        "manifest_json": str(out_dir / "manifest.json"),
        "initial_metrics_csv": str(out_dir / "initial_metrics.csv"),
        "initial_metrics_json": str(out_dir / "initial_metrics.json"),
        "contact_sheet": contact,
        "evidence_boundary": "input root modules only; final claims require remote SLat recursive outputs plus metrics and Blender QA",
    }
    _write_json(out_dir / "summary.json", summary)
    (out_dir / "README.md").write_text(
        "# Tree Root First-Split Candidates 20260511q\n\n"
        "Local input root modules for the q remote SLat recursion sweep.\n\n"
        "These meshes define explicit trunk, first-split, primary branch, and rootlet anchors. "
        "They are not final evidence by themselves; final evidence must come from remote "
        "Trellis2/SLat recursive outputs, metrics, and Blender QA.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260511)
    parser.add_argument("--no-render-preview", action="store_true")
    parser.add_argument("--preview-max-faces", type=int, default=120000)
    args = parser.parse_args()
    materialize(
        out_dir=args.out,
        seed=args.seed,
        render_preview=not args.no_render_preview,
        preview_max_faces=args.preview_max_faces,
    )


if __name__ == "__main__":
    main()
