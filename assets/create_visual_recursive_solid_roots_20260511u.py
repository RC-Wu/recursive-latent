#!/usr/bin/env python3
"""Create low-frequency solid city/castle roots for 11u visual recursion."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "results" / "visual_recursive_solid_roots_20260511u"


def box(center, extents) -> trimesh.Trimesh:
    mesh = trimesh.creation.box(extents=extents)
    mesh.apply_translation(center)
    return mesh


def cyl(center, radius, height, sections=16, axis="z") -> trimesh.Trimesh:
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    if axis == "x":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    elif axis == "y":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    mesh.apply_translation(center)
    return mesh


def fused_mesh(parts: list[trimesh.Trimesh], pitch: float) -> trimesh.Trimesh:
    merged = trimesh.util.concatenate(parts)
    merged.remove_unreferenced_vertices()
    voxels = merged.voxelized(pitch=pitch).fill()
    mesh = voxels.marching_cubes
    center = (mesh.bounds[0] + mesh.bounds[1]) * 0.5
    scale = max(float((mesh.bounds[1] - mesh.bounds[0]).max()), 1e-8)
    mesh.apply_translation(-center)
    mesh.apply_scale(1.0 / scale)
    mesh.remove_unreferenced_vertices()
    try:
        trimesh.repair.fix_normals(mesh, multibody=True)
    except TypeError:
        trimesh.repair.fix_normals(mesh)
    return mesh


def city_solid_podium_v1() -> tuple[trimesh.Trimesh, dict]:
    parts = [
        box((0, 0, -0.38), (1.35, 0.92, 0.18)),
        box((0, 0, -0.13), (1.05, 0.70, 0.42)),
        box((0, 0, 0.18), (0.78, 0.52, 0.30)),
        box((0, 0, 0.42), (0.52, 0.36, 0.20)),
        box((0, 0, 0.58), (0.30, 0.22, 0.18)),
    ]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(box((sx * 0.43, sy * 0.29, 0.13), (0.16, 0.13, 0.30)))
    mesh = fused_mesh(parts, pitch=0.040)
    return mesh, {
        "case": "city_solid_podium_v1",
        "family": "city",
        "anchors": "single central solid tower body and broad stepped roof support",
        "semantic_growth_frame": "input z+; for 11u preencode rot_x_neg90, use SLat z+",
        "visual_goal": "low-frequency city block with one readable recursive rooftop mass",
    }


def city_solid_keep_v1() -> tuple[trimesh.Trimesh, dict]:
    parts = [
        box((0, 0, -0.42), (1.08, 1.08, 0.16)),
        box((0, 0, -0.08), (0.82, 0.82, 0.70)),
        box((0, 0, 0.37), (0.92, 0.92, 0.12)),
        box((0, 0, 0.56), (0.42, 0.42, 0.30)),
    ]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(box((sx * 0.39, sy * 0.39, 0.30), (0.16, 0.16, 0.26)))
    mesh = fused_mesh(parts, pitch=0.040)
    return mesh, {
        "case": "city_solid_keep_v1",
        "family": "city",
        "anchors": "square roof terrace with compact center tower",
        "semantic_growth_frame": "input z+; for 11u preencode rot_x_neg90, use SLat z+",
        "visual_goal": "city/castle-neutral solid tower hierarchy for recursion stress",
    }


def castle_solid_keep_v1() -> tuple[trimesh.Trimesh, dict]:
    parts = [
        box((0, 0, -0.43), (1.00, 1.00, 0.14)),
        box((0, 0, -0.07), (0.78, 0.78, 0.76)),
        box((0, 0, 0.40), (0.90, 0.90, 0.10)),
        box((0, 0, 0.60), (0.34, 0.34, 0.30)),
    ]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(cyl((sx * 0.42, sy * 0.42, -0.02), 0.13, 0.82, sections=14))
            parts.append(cyl((sx * 0.42, sy * 0.42, 0.44), 0.15, 0.10, sections=14))
    mesh = fused_mesh(parts, pitch=0.038)
    return mesh, {
        "case": "castle_solid_keep_v1",
        "family": "castle",
        "anchors": "four solid corner towers plus central roof mass, no thin battlement strips",
        "semantic_growth_frame": "input z+; for 11u preencode rot_x_neg90, use SLat z+",
        "visual_goal": "solid nested keep/tower recursion without shredded cap details",
    }


def castle_solid_gate_v1() -> tuple[trimesh.Trimesh, dict]:
    parts = [
        box((0, 0, -0.35), (1.16, 0.38, 0.14)),
        box((0, 0, 0.02), (0.76, 0.34, 0.66)),
        box((0, 0, 0.42), (1.02, 0.42, 0.14)),
    ]
    for sx in (-1, 1):
        parts.append(cyl((sx * 0.48, 0, 0.02), 0.17, 0.82, sections=16))
        parts.append(cyl((sx * 0.48, 0, 0.49), 0.19, 0.12, sections=16))
        parts.append(box((sx * 0.48, 0, 0.66), (0.20, 0.20, 0.20)))
    mesh = fused_mesh(parts, pitch=0.038)
    return mesh, {
        "case": "castle_solid_gate_v1",
        "family": "castle",
        "anchors": "two solid tower tops and one central wall slab",
        "semantic_growth_frame": "input z+; for 11u preencode rot_x_neg90, use SLat z+",
        "visual_goal": "gate/turret recursion with fewer thin cap fragments",
    }


CASES = [city_solid_podium_v1, city_solid_keep_v1, castle_solid_keep_v1, castle_solid_gate_v1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    root_dir = args.out / "selected_roots"
    rows = []
    for make_case in CASES:
        mesh, meta = make_case()
        obj = root_dir / f"{meta['case']}.obj"
        obj.parent.mkdir(parents=True, exist_ok=True)
        mesh.export(obj)
        extent = mesh.bounds[1] - mesh.bounds[0]
        row = {
            **meta,
            "obj_path": str(obj),
            "vertices": int(len(mesh.vertices)),
            "faces": int(len(mesh.faces)),
            "bbox_extent": [float(x) for x in extent],
            "bbox_diag": float(np.linalg.norm(extent)),
            "root_source_type": "authored_low_frequency_fused_solid_root",
            "claim_gate": "remote SLat output plus metrics plus controlled render QA required",
        }
        rows.append(row)
        (root_dir / f"{meta['case']}.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
    args.out.mkdir(parents=True, exist_ok=True)
    fields = [
        "case",
        "family",
        "obj_path",
        "vertices",
        "faces",
        "bbox_extent",
        "bbox_diag",
        "root_source_type",
        "semantic_growth_frame",
        "anchors",
        "visual_goal",
        "claim_gate",
    ]
    with (args.out / "selected_roots_manifest_20260511u.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (args.out / "selected_roots_manifest_20260511u.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(args.out), "cases": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
