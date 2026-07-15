#!/usr/bin/env python3
"""Create low-complexity anchored roots for visual recursive case sweep 20260511l.

These meshes are root inputs only. Publication evidence still has to come from
the remote SLat/grammar decode, metrics, and controlled render QA.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "results" / "visual_recursive_lowpoly_roots_20260511l"


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


def merge(parts: list[trimesh.Trimesh]) -> trimesh.Trimesh:
    mesh = trimesh.util.concatenate(parts)
    mesh.remove_unreferenced_vertices()
    try:
        trimesh.repair.fix_normals(mesh, multibody=True)
    except TypeError:
        trimesh.repair.fix_normals(mesh)
    return mesh


def fused_mesh(parts: list[trimesh.Trimesh], pitch: float = 0.035) -> trimesh.Trimesh:
    """Voxel-fuse overlapping primitives into one watertight root surface."""

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


def city_block_lowpoly_roof_anchor_v1() -> tuple[trimesh.Trimesh, dict]:
    parts = [
        box((0.0, 0.0, 0.0), (1.25, 0.76, 0.86)),
        box((0.0, 0.0, 0.47), (1.36, 0.86, 0.08)),
        box((0.0, 0.37, 0.55), (1.36, 0.06, 0.20)),
        box((0.0, -0.37, 0.55), (1.36, 0.06, 0.20)),
        box((0.62, 0.0, 0.55), (0.06, 0.86, 0.20)),
        box((-0.62, 0.0, 0.55), (0.06, 0.86, 0.20)),
        box((0.0, 0.0, 0.68), (0.42, 0.30, 0.34)),
        box((0.0, 0.0, 0.88), (0.52, 0.40, 0.06)),
        box((0.0, 0.0, 1.02), (0.24, 0.18, 0.24)),
        box((-0.38, -0.23, 0.64), (0.18, 0.16, 0.22)),
        box((0.38, 0.23, 0.64), (0.18, 0.16, 0.22)),
    ]
    mesh = fused_mesh(parts, pitch=0.035)
    meta = {
        "case": "city_block_lowpoly_roof_anchor_v1",
        "family": "city",
        "semantic_up": "z+ in mesh frame; run y+ and z+ SLat growth-frame checks",
        "anchors": "flat roof slab, central rooftop podium, four parapet strips",
        "intended_grammar": "v25l_city_roof_podium / v25l_city_roof_corners",
    }
    return mesh, meta


def city_courtyard_tower_anchor_v1() -> tuple[trimesh.Trimesh, dict]:
    parts = [
        box((-0.45, 0.0, 0.0), (0.42, 1.00, 0.70)),
        box((0.45, 0.0, 0.0), (0.42, 1.00, 0.70)),
        box((0.0, -0.42, 0.0), (1.25, 0.22, 0.68)),
        box((0.0, 0.42, 0.0), (1.25, 0.22, 0.68)),
        box((0.0, 0.0, 0.12), (1.10, 0.16, 0.18)),
        box((0.0, 0.0, 0.12), (0.16, 0.92, 0.18)),
        box((0.0, 0.0, 0.40), (0.34, 0.34, 0.86)),
        box((0.0, 0.0, 0.88), (0.44, 0.44, 0.08)),
        box((0.0, 0.0, 1.08), (0.22, 0.22, 0.28)),
    ]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(box((sx * 0.55, sy * 0.43, 0.47), (0.20, 0.16, 0.30)))
            parts.append(box((sx * 0.55, sy * 0.43, 0.66), (0.26, 0.22, 0.05)))
    mesh = fused_mesh(parts, pitch=0.035)
    meta = {
        "case": "city_courtyard_tower_anchor_v1",
        "family": "city",
        "semantic_up": "z+ in mesh frame; run y+ and z+ SLat growth-frame checks",
        "anchors": "central tower roof and four courtyard corner roofs",
        "intended_grammar": "v25l_city_roof_podium / v25l_city_roof_corners",
    }
    return mesh, meta


def castle_gate_lowpoly_turret_anchor_v1() -> tuple[trimesh.Trimesh, dict]:
    parts = [
        box((-0.34, 0.0, 0.05), (0.24, 0.32, 0.70)),
        box((0.34, 0.0, 0.05), (0.24, 0.32, 0.70)),
        box((0.0, 0.0, 0.38), (0.90, 0.26, 0.26)),
        box((0.0, 0.0, -0.18), (0.90, 0.24, 0.18)),
        box((0.0, 0.0, 0.60), (1.00, 0.30, 0.24)),
        cyl((-0.54, 0.0, 0.06), 0.17, 0.82, sections=16),
        cyl((0.54, 0.0, 0.06), 0.17, 0.82, sections=16),
        cyl((-0.54, 0.0, 0.52), 0.20, 0.08, sections=16),
        cyl((0.54, 0.0, 0.52), 0.20, 0.08, sections=16),
    ]
    for sx in (-1, 1):
        for k in (-1, 0, 1):
            parts.append(box((sx * 0.54 + k * 0.055, 0.0, 0.70), (0.045, 0.28, 0.18)))
    for x in np.linspace(-0.33, 0.33, 5):
        parts.append(box((float(x), 0.0, 0.73), (0.06, 0.26, 0.20)))
    mesh = fused_mesh(parts, pitch=0.030)
    meta = {
        "case": "castle_gate_lowpoly_turret_anchor_v1",
        "family": "castle",
        "semantic_up": "z+ in mesh frame; run y+ and z+ SLat growth-frame checks",
        "anchors": "two turret caps plus a top battlement strip over the gate",
        "intended_grammar": "v25l_castle_turret_caps / v25l_castle_battlement_strip",
    }
    return mesh, meta


def castle_keep_battlement_anchor_v1() -> tuple[trimesh.Trimesh, dict]:
    parts = [
        box((0.0, 0.0, 0.0), (0.88, 0.88, 0.90)),
        box((0.0, 0.0, 0.50), (0.98, 0.98, 0.08)),
        box((0.0, 0.50, 0.62), (0.98, 0.12, 0.24)),
        box((0.0, -0.50, 0.62), (0.98, 0.12, 0.24)),
        box((0.50, 0.0, 0.62), (0.12, 0.98, 0.24)),
        box((-0.50, 0.0, 0.62), (0.12, 0.98, 0.24)),
        box((0.0, 0.0, -0.50), (1.10, 1.10, 0.12)),
    ]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(cyl((sx * 0.46, sy * 0.46, 0.10), 0.16, 1.08, sections=14))
            parts.append(cyl((sx * 0.46, sy * 0.46, 0.70), 0.19, 0.08, sections=14))
            parts.append(box((sx * 0.46, sy * 0.46, 0.86), (0.13, 0.13, 0.18)))
    for x in np.linspace(-0.36, 0.36, 5):
        parts.append(box((float(x), 0.50, 0.72), (0.07, 0.10, 0.22)))
        parts.append(box((float(x), -0.50, 0.72), (0.07, 0.10, 0.22)))
    for y in np.linspace(-0.36, 0.36, 5):
        parts.append(box((0.50, float(y), 0.72), (0.10, 0.07, 0.22)))
        parts.append(box((-0.50, float(y), 0.72), (0.10, 0.07, 0.22)))
    mesh = fused_mesh(parts, pitch=0.035)
    meta = {
        "case": "castle_keep_battlement_anchor_v1",
        "family": "castle",
        "semantic_up": "z+ in mesh frame; run y+ and z+ SLat growth-frame checks",
        "anchors": "four turret caps and clean battlement strips",
        "intended_grammar": "v25l_castle_turret_caps / v25l_castle_battlement_strip",
    }
    return mesh, meta


def mech_socket_frame_lowpoly_v1() -> tuple[trimesh.Trimesh, dict]:
    parts = [
        box((0.0, 0.0, 0.0), (0.72, 0.50, 0.46)),
        box((0.0, 0.0, 0.33), (0.45, 0.32, 0.20)),
        box((0.0, 0.0, -0.33), (0.45, 0.32, 0.20)),
    ]
    for sx in (-1, 1):
        parts.append(box((sx * 0.48, 0.0, 0.0), (0.26, 0.32, 0.28)))
        parts.append(box((sx * 0.66, 0.0, 0.0), (0.18, 0.22, 0.18)))
        parts.append(cyl((sx * 0.78, 0.0, 0.0), 0.065, 0.24, sections=12, axis="x"))
        parts.append(box((sx * 0.36, 0.34, 0.0), (0.16, 0.26, 0.08)))
        parts.append(box((sx * 0.36, -0.34, 0.0), (0.16, 0.26, 0.08)))
    for z in (-0.18, 0.18):
        parts.append(cyl((0.0, 0.36, z), 0.055, 0.25, sections=12, axis="y"))
        parts.append(cyl((0.0, -0.36, z), 0.055, 0.25, sections=12, axis="y"))
    mesh = fused_mesh(parts, pitch=0.032)
    meta = {
        "case": "mech_socket_frame_lowpoly_v1",
        "family": "mechanical",
        "semantic_up": "z+ for presentation; SLat side-socket grammar should use y+ or z+ checks",
        "anchors": "bilateral side sockets, four fin pads, front/back ports",
        "intended_grammar": "v25l_mecha_socket_pods",
    }
    return mesh, meta


CASES = [
    city_block_lowpoly_roof_anchor_v1,
    city_courtyard_tower_anchor_v1,
    castle_gate_lowpoly_turret_anchor_v1,
    castle_keep_battlement_anchor_v1,
    mech_socket_frame_lowpoly_v1,
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    out_dir = args.out
    root_dir = out_dir / "selected_roots"
    rows = []
    for make_case in CASES:
        mesh, meta = make_case()
        obj_path = root_dir / f"{meta['case']}.obj"
        save_mesh(mesh, obj_path)
        bounds = mesh.bounds
        extent = bounds[1] - bounds[0]
        row = {
            **meta,
            "obj_path": str(obj_path),
            "vertices": int(len(mesh.vertices)),
            "faces": int(len(mesh.faces)),
            "bbox_extent": [float(x) for x in extent],
            "bbox_diag": float(np.linalg.norm(extent)),
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
        "semantic_up",
        "anchors",
        "intended_grammar",
    ]
    with (out_dir / "selected_roots_manifest_20260511l.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "selected_roots_manifest_20260511l.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps({"out_dir": str(out_dir), "cases": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
