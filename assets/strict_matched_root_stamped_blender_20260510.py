#!/usr/bin/env python3
"""Materialize root-stamped strict-matching candidates in Blender.

Run with Blender:

  /Applications/Blender.app/Contents/MacOS/Blender -b --python \
    assets/strict_matched_root_stamped_blender_20260510.py -- \
    --plan results/strict_matched_root_stamped_20260510/anchor_plan.json \
    --out visuals/strict_matched_root_stamped_20260510
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


def parse_args() -> argparse.Namespace:
    import sys

    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--max-token-objects", type=int, default=8)
    parser.add_argument("--max-instances", type=int, default=34)
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def ensure_mat(name: str, color: tuple[float, float, float, float], roughness: float = 0.58, metallic: float = 0.0) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        try:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = roughness
            bsdf.inputs["Metallic"].default_value = metallic
        except Exception:
            pass
    return mat


def material_for_preset(preset: str) -> dict[str, bpy.types.Material]:
    if preset in {"bark_leaf", "vine_leaf"}:
        return {
            "support": ensure_mat("warm_branch_bark", (0.30, 0.17, 0.09, 1), 0.72, 0.0),
            "accent": ensure_mat("leaf_accent", (0.18, 0.43, 0.16, 1), 0.46, 0.0),
        }
    if preset == "root_bark":
        return {
            "support": ensure_mat("root_bark", (0.42, 0.27, 0.14, 1), 0.78, 0.0),
            "accent": ensure_mat("fine_root_tips", (0.50, 0.36, 0.21, 1), 0.70, 0.0),
        }
    if preset == "coral_octopus":
        return {
            "support": ensure_mat("coral_support", (0.72, 0.36, 0.29, 1), 0.55, 0.0),
            "accent": ensure_mat("coral_tip", (0.95, 0.58, 0.45, 1), 0.42, 0.0),
        }
    return {
        "support": ensure_mat("pyrite_support", (0.92, 0.72, 0.30, 1), 0.34, 0.45),
        "accent": ensure_mat("pyrite_dark_edges", (0.34, 0.26, 0.14, 1), 0.42, 0.35),
    }


def frustum_mesh(name: str, start: Vector, end: Vector, r0: float, r1: float, sides: int = 12) -> bpy.types.Mesh:
    axis = end - start
    if axis.length < 1e-7:
        axis = Vector((0, 0, 1))
    w = axis.normalized()
    seed = Vector((0, 0, 1)) if abs(w.z) < 0.88 else Vector((1, 0, 0))
    u = w.cross(seed).normalized()
    v = w.cross(u).normalized()
    verts = []
    faces = []
    for i in range(sides):
        a = 2.0 * math.pi * i / sides
        d = math.cos(a) * u + math.sin(a) * v
        verts.append(start + d * r0)
    for i in range(sides):
        a = 2.0 * math.pi * i / sides
        d = math.cos(a) * u + math.sin(a) * v
        verts.append(end + d * r1)
    for i in range(sides):
        j = (i + 1) % sides
        faces.append((i, j, sides + i))
        faces.append((j, sides + j, sides + i))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in verts], [], faces)
    mesh.update()
    return mesh


def add_support_edges(case: dict, mats: dict[str, bpy.types.Material]) -> None:
    for e_idx, edge in enumerate(case.get("edges", [])):
        start = Vector(edge["start"])
        end = Vector(edge["end"])
        mesh = frustum_mesh(f"{case['case_id']}_edge_{e_idx:04d}", start, end, float(edge["radius0"]), float(edge["radius1"]), sides=12)
        obj = bpy.data.objects.new(mesh.name, mesh)
        obj.data.materials.append(mats["support"])
        bpy.context.collection.objects.link(obj)
    # Add small accent bulbs to anchor points so the local generated token is
    # still visible even if an imported GLB root is too heavy or malformed.
    for a_idx, anchor in enumerate(case.get("anchors", [])[:48]):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=float(anchor.get("scale", 0.08)) * 0.55, location=anchor["position"])
        obj = bpy.context.object
        obj.name = f"{case['case_id']}_accent_{a_idx:03d}"
        obj.data.materials.append(mats["accent"])


def import_asset(root: Path, rel: str | None, max_objects: int) -> tuple[list[bpy.types.Object], Vector, float]:
    if not rel:
        return [], Vector((0, 0, 0)), 1.0
    path = (root / rel).resolve()
    if not path.exists():
        print(f"[warn] root asset missing: {path}")
        return [], Vector((0, 0, 0)), 1.0
    before = set(bpy.data.objects)
    try:
        bpy.ops.import_scene.gltf(filepath=str(path))
    except Exception as exc:
        print(f"[warn] failed to import root asset {path}: {exc}")
        return [], Vector((0, 0, 0)), 1.0
    imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    imported = sorted(imported, key=lambda o: len(o.data.vertices), reverse=True)[:max_objects]
    if not imported:
        return [], Vector((0, 0, 0)), 1.0
    pts = []
    for obj in imported:
        for corner in obj.bound_box:
            pts.append(obj.matrix_world @ Vector(corner))
        obj.hide_render = True
        obj.hide_viewport = True
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center = (mn + mx) * 0.5
    extent = max(mx.x - mn.x, mx.y - mn.y, mx.z - mn.z, 1e-6)
    return imported, center, 1.0 / extent


def rotation_from_z(direction: Vector) -> Matrix:
    if direction.length < 1e-8:
        direction = Vector((0, 0, 1))
    try:
        q = Vector((0, 0, 1)).rotation_difference(direction.normalized())
        return q.to_matrix().to_4x4()
    except Exception:
        return Matrix.Identity(4)


def add_token_instances(case: dict, root: Path, max_objects: int, max_instances: int) -> int:
    source, center, norm_scale = import_asset(root, case.get("root_asset"), max_objects=max_objects)
    if not source:
        return 0
    count = 0
    for anchor in case.get("anchors", [])[:max_instances]:
        pos = Vector(anchor["position"])
        direction = Vector(anchor.get("direction", [0, 0, 1]))
        scale = float(anchor.get("scale", 0.1))
        transform = Matrix.Translation(pos) @ rotation_from_z(direction) @ Matrix.Scale(scale * norm_scale, 4) @ Matrix.Translation(-center)
        for obj in source:
            dup = obj.copy()
            dup.data = obj.data
            dup.animation_data_clear()
            dup.matrix_world = transform @ obj.matrix_world
            dup.hide_render = False
            dup.hide_viewport = False
            dup.name = f"{case['case_id']}_token_{count:03d}_{obj.name[:24]}"
            bpy.context.collection.objects.link(dup)
        count += 1
    return count


def add_lights_and_camera() -> None:
    bpy.ops.object.light_add(type="AREA", location=(0, -5, 8))
    light = bpy.context.object
    light.name = "softbox_key"
    light.data.energy = 450
    light.data.size = 5.0
    bpy.ops.object.camera_add(location=(7.5, -8.0, 6.2), rotation=(math.radians(62), 0, math.radians(43)))
    bpy.context.scene.camera = bpy.context.object


def export_case(case: dict, out_dir: Path, root: Path, max_objects: int, max_instances: int) -> dict:
    clear_scene()
    mats = material_for_preset(str(case.get("material_preset", "bark_leaf")))
    add_support_edges(case, mats)
    token_count = add_token_instances(case, root, max_objects=max_objects, max_instances=max_instances)
    add_lights_and_camera()
    case_dir = out_dir / case["case_id"]
    case_dir.mkdir(parents=True, exist_ok=True)
    glb_path = case_dir / "root_stamped_candidate.glb"
    bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format="GLB")
    meta = {
        "case_id": case["case_id"],
        "matched_traditional_case": case.get("matched_traditional_case"),
        "family": case.get("family"),
        "target_category": case.get("target_category"),
        "recursive_mode": case.get("recursive_mode"),
        "root_asset": case.get("root_asset"),
        "root_asset_policy": case.get("root_asset_policy"),
        "material_preset": case.get("material_preset"),
        "edges": len(case.get("edges", [])),
        "anchors": len(case.get("anchors", [])),
        "token_instances": token_count,
        "glb_path": str(glb_path),
        "controls": case.get("controls", {}),
        "selection_budget": case.get("selection_budget", {}),
    }
    (case_dir / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta


def main() -> None:
    args = parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)
    rows = []
    for case in plan["cases"]:
        print(f"[root-stamp] {case['case_id']}")
        rows.append(export_case(case, args.out, args.root, args.max_token_objects, args.max_instances))
    fields = [
        "case_id",
        "matched_traditional_case",
        "family",
        "target_category",
        "recursive_mode",
        "root_asset",
        "material_preset",
        "edges",
        "anchors",
        "token_instances",
        "glb_path",
    ]
    with (args.out / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    (args.out / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    cases_txt = "\n".join(f"{row['case_id']}={row['glb_path']}" for row in rows) + "\n"
    (args.out / "cases.txt").write_text(cases_txt, encoding="utf-8")
    print(json.dumps({"out": str(args.out), "cases": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
