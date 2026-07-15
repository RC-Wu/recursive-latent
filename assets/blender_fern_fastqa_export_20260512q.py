#!/usr/bin/env python3
"""Fast GLB export and material-override render QA for 20260512 fern cases.

This is a fast review pass: it exports materialized GLBs and renders Workbench
PNG views. It is not a replacement for final Cycles/PBR renders.
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
    return bpy.context.object


def normalize_object(obj, target_extent: float = 3.0) -> dict:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    bpy.context.view_layer.update()
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    center = sum(corners, Vector()) / 8.0
    obj.location -= center
    bpy.context.view_layer.update()
    dims = obj.dimensions
    extent = max(dims.x, dims.y, dims.z, 1e-6)
    obj.scale *= target_extent / extent
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.context.view_layer.update()
    return {
        "vertices": len(obj.data.vertices),
        "faces": len(obj.data.polygons),
        "normalized_dimensions": [obj.dimensions.x, obj.dimensions.y, obj.dimensions.z],
    }


def set_bsdf(mat, color, roughness: float) -> None:
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness


def assign_material(obj, family: str) -> None:
    if family == "fiddlehead":
        color = (0.42, 0.53, 0.24, 1.0)
        roughness = 0.64
    else:
        color = (0.24, 0.44, 0.24, 1.0)
        roughness = 0.72
    mat = bpy.data.materials.new(f"{family}_qa_green_material")
    mat.diffuse_color = color
    set_bsdf(mat, color, roughness)
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.material_index = 0
        poly.use_smooth = True
    mod = obj.modifiers.new("fastqa_weighted_normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True
    try:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except Exception:
        pass


def add_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-3.0, -4.5, 5.5))
    key = bpy.context.object
    key.data.energy = 600
    key.data.size = 5.0
    bpy.ops.object.light_add(type="AREA", location=(3.5, 3.0, 3.5))
    fill = bpy.context.object
    fill.data.energy = 160
    fill.data.size = 4.0


def setup_render(resolution: int, background: str) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.image_settings.file_format = "PNG"
    if background == "white":
        scene.render.film_transparent = True
        scene.render.image_settings.color_mode = "RGBA"
        world_color = (1.0, 1.0, 1.0)
    else:
        scene.render.film_transparent = False
        scene.render.image_settings.color_mode = "RGB"
        world_color = (0.82, 0.87, 0.91)
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = False
    world.color = world_color
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0


def add_camera(view: str, family: str) -> None:
    locs = {
        "iso": Vector((4.2, -5.0, 3.0)),
        "front": Vector((0.0, -6.2, 1.0)),
        "side": Vector((6.2, 0.0, 1.0)),
        "zoom": Vector((2.6, -3.6, 2.1)),
    }
    loc = locs.get(view, locs["iso"])
    direction = Vector((0.0, 0.0, 0.0)) - loc
    bpy.ops.object.camera_add(location=loc, rotation=direction.to_track_quat("-Z", "Y").to_euler())
    cam = bpy.context.object
    cam.data.type = "ORTHO"
    if view == "zoom":
        cam.data.ortho_scale = 1.35 if family == "fiddlehead" else 1.75
        if family == "fiddlehead":
            cam.location += Vector((-0.42, 0.48, -0.12))
    else:
        cam.data.ortho_scale = 3.7 if family == "fern" else 3.9
    bpy.context.scene.camera = cam


def export_glb(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        export_apply=True,
        export_materials="EXPORT",
        export_normals=True,
    )


def parse_case(text: str) -> dict:
    label, family, depth, path = text.split("|", 3)
    return {"label": label, "family": family, "depth": int(depth), "path": Path(path)}


def process_case(case: dict, out_dir: Path, views: list[str], resolution: int) -> dict:
    label = case["label"]
    family = case["family"]
    obj_path = case["path"]
    manifest = {
        "label": label,
        "family": family,
        "depth": case["depth"],
        "input_obj": str(obj_path),
        "outputs": {},
        "started_at_epoch": time.time(),
    }
    clear_scene()
    obj = import_mesh(obj_path)
    obj.name = label
    manifest.update(normalize_object(obj))
    assign_material(obj, family)
    glb_path = out_dir / "glb" / f"{label}.glb"
    export_glb(glb_path)
    manifest["outputs"]["glb"] = str(glb_path)
    manifest["glb_size_bytes"] = glb_path.stat().st_size if glb_path.exists() else None

    # Render views without re-importing the mesh.
    for background in ["white", "studio"]:
        for view in views:
            for item in [obj for obj in bpy.data.objects if obj.type in {"CAMERA", "LIGHT"}]:
                bpy.data.objects.remove(item, do_unlink=True)
            setup_render(resolution, background)
            add_lights()
            add_camera(view, family)
            out_path = out_dir / "renders" / background / f"{label}_{view}.png"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            bpy.context.scene.render.filepath = str(out_path)
            bpy.ops.render.render(write_still=True)
            manifest["outputs"][f"{background}_{view}"] = str(out_path)
    manifest["finished_at_epoch"] = time.time()
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--views", nargs="+", default=["iso", "front", "zoom"])
    parser.add_argument("--resolution", type=int, default=1100)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = parser.parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    cases = [parse_case(text) for text in args.case]
    manifests = [process_case(case, args.out_dir, args.views, args.resolution) for case in cases]
    manifest_path = args.out_dir / "manifest_20260512q_fastqa.json"
    manifest_path.write_text(json.dumps({"cases": manifests}, indent=2), encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
