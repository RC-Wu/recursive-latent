#!/usr/bin/env python3
"""Create restored-frame visual roots for 20260511o remote recursive sweep.

These are authored root inputs for visual showcase only.  The publication gate
still requires remote SLat/grammar outputs, metrics, and controlled render QA.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "results" / "visual_recursive_roots_20260511o"


def box(center, extents) -> trimesh.Trimesh:
    mesh = trimesh.creation.box(extents=extents)
    mesh.apply_translation(center)
    return mesh


def cyl(center, radius, height, sections=18, axis="z") -> trimesh.Trimesh:
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    if axis == "x":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    elif axis == "y":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    mesh.apply_translation(center)
    return mesh


def cone(center, r1, r2, height, sections=18, axis="z") -> trimesh.Trimesh:
    mesh = trimesh.creation.cone(radius=r1, radius_top=r2, height=height, sections=sections)
    if axis == "x":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    elif axis == "y":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    mesh.apply_translation(center)
    return mesh


def torus(center, major, minor, sections=36) -> trimesh.Trimesh:
    mesh = trimesh.creation.torus(major_radius=major, minor_radius=minor, major_sections=sections, minor_sections=10)
    mesh.apply_translation(center)
    return mesh


def merge(parts: list[trimesh.Trimesh]) -> trimesh.Trimesh:
    mesh = trimesh.util.concatenate(parts)
    mesh.remove_unreferenced_vertices()
    try:
        trimesh.repair.fix_normals(mesh, multibody=True)
    except TypeError:
        trimesh.repair.fix_normals(mesh)
    return mesh


def fused_mesh(parts: list[trimesh.Trimesh], pitch: float) -> trimesh.Trimesh:
    merged = merge(parts)
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


def save_mesh(mesh: trimesh.Trimesh, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(out)


def city_tower_cluster_socket_v2() -> tuple[trimesh.Trimesh, dict]:
    parts = [
        box((0, 0, -0.42), (1.55, 1.10, 0.14)),
        box((0, 0, -0.22), (1.24, 0.84, 0.38)),
        box((0, 0, 0.12), (0.72, 0.52, 0.88)),
        box((0, 0, 0.61), (0.84, 0.62, 0.10)),
        box((0, 0, 0.82), (0.38, 0.30, 0.34)),
    ]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(box((sx * 0.47, sy * 0.32, 0.02), (0.23, 0.18, 0.56)))
            parts.append(box((sx * 0.47, sy * 0.32, 0.34), (0.30, 0.24, 0.08)))
    for x in np.linspace(-0.48, 0.48, 5):
        parts.append(box((float(x), -0.48, -0.02), (0.055, 0.10, 0.38)))
        parts.append(box((float(x), 0.48, -0.02), (0.055, 0.10, 0.38)))
    mesh = fused_mesh(parts, pitch=0.026)
    return mesh, {
        "case": "city_tower_cluster_socket_v2",
        "family": "city",
        "semantic_growth_frame": "input z+ is semantic up; after workflow mesh-to-SLat mapping use growth_axis=y,growth_sign=-1",
        "render_frame": "restored input z-up frame; no semantic inference from old flipped contact sheets",
        "anchors": "central rooftop tower plus four clean corner roof sockets",
        "visual_goal": "small city/tower cluster on top of a larger city block with obvious recursive hierarchy",
    }


def city_stepped_arcology_v1() -> tuple[trimesh.Trimesh, dict]:
    parts = [
        box((0, 0, -0.46), (1.50, 0.92, 0.14)),
        box((0, 0, -0.25), (1.12, 0.72, 0.40)),
        box((0, 0, 0.06), (0.86, 0.54, 0.42)),
        box((0, 0, 0.36), (0.60, 0.38, 0.32)),
        box((0, 0, 0.61), (0.34, 0.24, 0.26)),
    ]
    for sx in (-1, 1):
        parts.append(box((sx * 0.58, 0, -0.02), (0.22, 0.58, 0.54)))
        parts.append(box((sx * 0.58, 0, 0.31), (0.30, 0.66, 0.08)))
    for sy in (-1, 1):
        parts.append(box((0, sy * 0.38, 0.00), (0.92, 0.15, 0.44)))
    mesh = fused_mesh(parts, pitch=0.026)
    return mesh, {
        "case": "city_stepped_arcology_v1",
        "family": "city",
        "semantic_growth_frame": "input z+; SLat y-",
        "render_frame": "restored z-up",
        "anchors": "stepped roof terraces and side towers",
        "visual_goal": "arcology-like recursive terraces, less box-like than 11n city",
    }


def castle_tower_gate_socket_v2() -> tuple[trimesh.Trimesh, dict]:
    parts = [
        box((0, 0, -0.45), (1.30, 0.42, 0.18)),
        box((0, 0, -0.08), (0.72, 0.34, 0.56)),
        box((0, 0, 0.30), (1.02, 0.38, 0.22)),
    ]
    for sx in (-1, 1):
        parts.append(cyl((sx * 0.54, 0, -0.04), 0.18, 0.92, sections=20))
        parts.append(cyl((sx * 0.54, 0, 0.48), 0.22, 0.12, sections=20))
        parts.append(cone((sx * 0.54, 0, 0.73), 0.22, 0.06, 0.36, sections=20))
    for x in np.linspace(-0.36, 0.36, 5):
        parts.append(box((float(x), 0, 0.53), (0.065, 0.36, 0.20)))
    mesh = fused_mesh(parts, pitch=0.024)
    return mesh, {
        "case": "castle_tower_gate_socket_v2",
        "family": "castle",
        "semantic_growth_frame": "input z+; SLat y-",
        "render_frame": "restored z-up",
        "anchors": "two tower caps and central battlement strip",
        "visual_goal": "recursive castle towers visibly perched on parent towers/gate",
    }


def castle_keep_spire_socket_v2() -> tuple[trimesh.Trimesh, dict]:
    parts = [
        box((0, 0, -0.36), (1.02, 1.02, 0.16)),
        box((0, 0, 0.02), (0.74, 0.74, 0.82)),
        box((0, 0, 0.48), (0.90, 0.90, 0.10)),
        box((0, 0, 0.66), (0.38, 0.38, 0.22)),
    ]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(cyl((sx * 0.42, sy * 0.42, 0.05), 0.14, 0.90, sections=16))
            parts.append(cone((sx * 0.42, sy * 0.42, 0.62), 0.16, 0.05, 0.24, sections=16))
    for x in np.linspace(-0.28, 0.28, 4):
        parts.append(box((float(x), 0.46, 0.62), (0.065, 0.10, 0.18)))
        parts.append(box((float(x), -0.46, 0.62), (0.065, 0.10, 0.18)))
    mesh = fused_mesh(parts, pitch=0.024)
    return mesh, {
        "case": "castle_keep_spire_socket_v2",
        "family": "castle",
        "semantic_growth_frame": "input z+; SLat y-",
        "render_frame": "restored z-up",
        "anchors": "four corner spires plus top keep socket",
        "visual_goal": "nested castle keep/spire recursion without 11n facade holes",
    }


def mecha_socket_cruciform_v2() -> tuple[trimesh.Trimesh, dict]:
    parts = [
        box((0, 0, 0), (0.72, 0.46, 0.44)),
        box((0, 0, 0.36), (0.48, 0.32, 0.20)),
        box((0, 0, -0.36), (0.48, 0.32, 0.20)),
    ]
    for sx in (-1, 1):
        parts.append(box((sx * 0.50, 0, 0), (0.26, 0.34, 0.28)))
        parts.append(cyl((sx * 0.70, 0, 0), 0.08, 0.22, sections=14, axis="x"))
    for sy in (-1, 1):
        parts.append(box((0, sy * 0.42, 0.00), (0.34, 0.22, 0.24)))
        parts.append(cyl((0, sy * 0.58, 0), 0.065, 0.20, sections=14, axis="y"))
    mesh = fused_mesh(parts, pitch=0.026)
    return mesh, {
        "case": "mecha_socket_cruciform_v2",
        "family": "mechanical",
        "semantic_growth_frame": "input z+ for presentation; side sockets are lateral anchors, SLat y- for top variants",
        "render_frame": "restored z-up",
        "anchors": "left/right/front/back mechanical sockets",
        "visual_goal": "clear repeated hard-surface modules with controlled metal material",
    }


def crown_spire_ring_socket_v2() -> tuple[trimesh.Trimesh, dict]:
    parts = [torus((0, 0, -0.02), 0.40, 0.055, sections=40)]
    for i in range(12):
        a = i * np.pi * 2 / 12
        x = 0.40 * np.cos(a)
        y = 0.40 * np.sin(a)
        parts.append(cone((x, y, 0.18), 0.055, 0.018, 0.34, sections=10))
        parts.append(cyl((x, y, 0.02), 0.035, 0.12, sections=10))
    parts.append(cyl((0, 0, 0.06), 0.18, 0.12, sections=24))
    mesh = fused_mesh(parts, pitch=0.020)
    return mesh, {
        "case": "crown_spire_ring_socket_v2",
        "family": "crown",
        "semantic_growth_frame": "input z+; rim recursion can use SLat y- or radial operators",
        "render_frame": "restored z-up",
        "anchors": "circular rim spires and center cap",
        "visual_goal": "ornamental crown/tiara ring with obvious recursive spire beads",
    }


CASES = [
    city_tower_cluster_socket_v2,
    city_stepped_arcology_v1,
    castle_tower_gate_socket_v2,
    castle_keep_spire_socket_v2,
    mecha_socket_cruciform_v2,
    crown_spire_ring_socket_v2,
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    root_dir = args.out / "selected_roots"
    rows = []
    for make_case in CASES:
        mesh, meta = make_case()
        out_path = root_dir / f"{meta['case']}.obj"
        save_mesh(mesh, out_path)
        extent = mesh.bounds[1] - mesh.bounds[0]
        row = {
            **meta,
            "obj_path": str(out_path),
            "vertices": int(len(mesh.vertices)),
            "faces": int(len(mesh.faces)),
            "bbox_extent": [float(x) for x in extent],
            "bbox_diag": float(np.linalg.norm(extent)),
            "root_source_type": "authored_fused_lowpoly_visual_root",
            "claim_gate": "remote SLat output plus metrics plus controlled render QA required",
        }
        rows.append(row)
        (root_dir / f"{meta['case']}.json").write_text(json.dumps(row, indent=2), encoding="utf-8")

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
        "render_frame",
        "anchors",
        "visual_goal",
        "claim_gate",
    ]
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "selected_roots_manifest_20260511o.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (args.out / "selected_roots_manifest_20260511o.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(args.out), "cases": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
