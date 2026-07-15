#!/usr/bin/env python3
"""Controlled Blender render/export pass for the 20260512 fern cases.

This script is intentionally self-contained and only consumes selected OBJ
outputs from the remote 12p run. It does not generate new geometry.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_mesh(path: Path):
    before = set(bpy.data.objects)
    if path.suffix.lower() == ".obj":
        bpy.ops.wm.obj_import(filepath=str(path))
    elif path.suffix.lower() in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    else:
        raise ValueError(f"Unsupported mesh format: {path}")
    imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    if not imported:
        raise RuntimeError(f"No mesh imported from {path}")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in imported:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = imported[0]
    if len(imported) > 1:
        bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = path.parent.parent.parent.name
    return obj


def normalize_object(obj, target_extent: float = 3.0) -> dict:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    bpy.context.view_layer.update()
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    low = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    high = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    center = (low + high) * 0.5
    extent_vec = high - low
    extent = max(extent_vec.x, extent_vec.y, extent_vec.z, 1e-6)
    obj.location -= center
    obj.scale *= target_extent / extent
    bpy.context.view_layer.update()
    corners2 = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    low2 = Vector((min(c.x for c in corners2), min(c.y for c in corners2), min(c.z for c in corners2)))
    high2 = Vector((max(c.x for c in corners2), max(c.y for c in corners2), max(c.z for c in corners2)))
    return {
        "normalized_bbox_min": [low2.x, low2.y, low2.z],
        "normalized_bbox_max": [high2.x, high2.y, high2.z],
        "normalized_extent": max((high2 - low2).x, (high2 - low2).y, (high2 - low2).z),
    }


def set_bsdf_value(bsdf, key: str, value) -> None:
    if bsdf is not None and key in bsdf.inputs:
        bsdf.inputs[key].default_value = value


def make_material(name: str, base, secondary, roughness: float = 0.68):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    set_bsdf_value(bsdf, "Base Color", base)
    set_bsdf_value(bsdf, "Roughness", roughness)
    set_bsdf_value(bsdf, "Metallic", 0.0)
    mat.diffuse_color = base
    if bsdf is not None and "Base Color" in bsdf.inputs:
        noise = nodes.new(type="ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 28.0
        noise.inputs["Detail"].default_value = 12.0
        noise.inputs["Roughness"].default_value = 0.62
        ramp = nodes.new(type="ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.18
        ramp.color_ramp.elements[0].color = secondary
        ramp.color_ramp.elements[1].position = 1.0
        ramp.color_ramp.elements[1].color = base
        mat.node_tree.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        mat.node_tree.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def assign_material(obj, family: str) -> None:
    if family == "fiddlehead":
        mat = make_material(
            "fiddlehead_wet_green_pbr_override",
            (0.54, 0.62, 0.30, 1.0),
            (0.08, 0.23, 0.20, 1.0),
            0.64,
        )
    else:
        mat = make_material(
            "fern_frond_green_pbr_override",
            (0.33, 0.48, 0.22, 1.0),
            (0.05, 0.22, 0.23, 1.0),
            0.72,
        )
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    mod = obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True
    try:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except Exception:
        pass


def setup_world(background: str, resolution: int, samples: int) -> None:
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = 0.15
    scene.view_settings.gamma = 1.0
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = False
    if background == "white":
        scene.render.film_transparent = True
        scene.render.image_settings.color_mode = "RGBA"
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"
        world.color = (1.0, 1.0, 1.0)
    else:
        scene.render.film_transparent = False
        scene.render.image_settings.color_mode = "RGB"
        world.color = (0.82, 0.87, 0.91)


def add_ground(background: str) -> None:
    if background == "white":
        return
    bpy.ops.mesh.primitive_plane_add(size=220.0, location=(0, 0, -1.55))
    plane = bpy.context.object
    plane.name = "continuous_blue_gray_ground"
    mat = bpy.data.materials.new(name="blue_gray_matte_ground")
    mat.diffuse_color = (0.82, 0.87, 0.91, 1.0)
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    set_bsdf_value(bsdf, "Base Color", (0.82, 0.87, 0.91, 1.0))
    set_bsdf_value(bsdf, "Roughness", 0.84)
    plane.data.materials.append(mat)


def add_lighting() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-3.0, -4.5, 6.0))
    key = bpy.context.object
    key.name = "large_softbox_key"
    key.data.energy = 720
    key.data.size = 5.6
    bpy.ops.object.light_add(type="AREA", location=(3.5, 3.0, 3.5))
    fill = bpy.context.object
    fill.name = "large_softbox_fill"
    fill.data.energy = 110
    fill.data.size = 6.0


def camera_pose(view: str):
    if view == "front":
        loc = Vector((0.0, -6.2, 1.0))
    elif view == "side":
        loc = Vector((6.2, -0.2, 1.1))
    elif view == "top":
        loc = Vector((0.1, -1.3, 7.0))
    elif view == "zoom":
        loc = Vector((2.8, -3.8, 2.4))
    else:
        loc = Vector((4.4, -5.2, 3.1))
    direction = Vector((0.0, 0.0, 0.0)) - loc
    return loc, direction.to_track_quat("-Z", "Y").to_euler()


def add_camera(view: str, family: str) -> None:
    loc, rot = camera_pose(view)
    bpy.ops.object.camera_add(location=loc, rotation=rot)
    cam = bpy.context.object
    cam.name = f"camera_{view}"
    cam.data.type = "ORTHO"
    if view == "zoom":
        cam.data.ortho_scale = 1.45 if family == "fiddlehead" else 1.9
        if family == "fiddlehead":
            cam.location += Vector((-0.45, 0.58, -0.15))
        else:
            cam.location += Vector((0.0, 0.18, -0.04))
    elif family == "fern":
        cam.data.ortho_scale = 3.7
    else:
        cam.data.ortho_scale = 3.9
    bpy.context.scene.camera = cam


def export_glb(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(out_path),
        export_format="GLB",
        export_apply=True,
        export_materials="EXPORT",
        export_texcoords=True,
        export_normals=True,
    )


def render_png(out_path: Path, background: str, view: str, family: str, resolution: int, samples: int) -> None:
    setup_world(background, resolution, samples)
    add_ground(background)
    add_lighting()
    add_camera(view, family)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)


def parse_case(item: str) -> dict:
    # label|family|depth|/path/to/mesh.obj
    label, family, depth, path = item.split("|", 3)
    return {"label": label, "family": family, "depth": int(depth), "path": Path(path)}


def process_case(case: dict, out_dir: Path, views: list[str], samples: int, resolution: int) -> dict:
    label = case["label"]
    family = case["family"]
    mesh_path = case["path"]
    manifest = {
        "label": label,
        "family": family,
        "depth": case["depth"],
        "input_obj": str(mesh_path),
        "outputs": {},
        "started_at_epoch": time.time(),
    }
    clear_scene()
    obj = import_mesh(mesh_path)
    mesh_stats = {
        "vertices": len(obj.data.vertices),
        "faces": len(obj.data.polygons),
    }
    mesh_stats.update(normalize_object(obj))
    assign_material(obj, family)
    glb_path = out_dir / "glb" / f"{label}.glb"
    export_glb(glb_path)
    manifest["outputs"]["glb"] = str(glb_path)
    manifest["glb_size_bytes"] = glb_path.stat().st_size if glb_path.exists() else None
    manifest.update(mesh_stats)
    for background in ["white", "studio"]:
        for view in views:
            clear_scene()
            obj = import_mesh(mesh_path)
            normalize_object(obj)
            assign_material(obj, family)
            png_path = out_dir / "renders" / background / f"{label}_{view}.png"
            render_png(png_path, background, view, family, resolution, samples)
            manifest["outputs"][f"{background}_{view}"] = str(png_path)
    manifest["finished_at_epoch"] = time.time()
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", required=True, help="label|family|depth|/path/to/mesh.obj")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--views", nargs="+", default=["iso", "front", "zoom"])
    parser.add_argument("--samples", type=int, default=128)
    parser.add_argument("--resolution", type=int, default=1600)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = parser.parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifests = []
    for item in args.case:
        manifests.append(process_case(parse_case(item), args.out_dir, args.views, args.samples, args.resolution))
    manifest_path = args.out_dir / "manifest_20260512q.json"
    manifest_path.write_text(json.dumps({"cases": manifests}, indent=2), encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
