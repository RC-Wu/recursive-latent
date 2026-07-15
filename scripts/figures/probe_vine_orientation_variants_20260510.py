#!/usr/bin/env python3
"""Render orientation probes for the selected vine/tree-roots hero case."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy  # type: ignore
from mathutils import Matrix, Vector  # type: ignore


REPO = Path(__file__).resolve().parents[2]
SOURCE = (
    REPO
    / "visuals/vine_stage5_guide_sweep_20260509"
    / "vine_stage5_parthenocissus_warm_steps8_tex2048_xformers/textured.glb"
)
OUT = REPO / "visuals/hero_botanical_variants_20260510/vine_orientation_probe_20260510"


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_joined(path: Path, label: str) -> bpy.types.Object:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
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
    obj.name = label
    return obj


def make_mat(name: str, color: tuple[float, float, float, float], roughness: float) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def recolor_by_height(obj: bpy.types.Object) -> None:
    brown = make_mat("probe_low_brown", (0.35, 0.20, 0.10, 1.0), 0.72)
    green = make_mat("probe_mid_green", (0.18, 0.38, 0.14, 1.0), 0.68)
    light = make_mat("probe_high_leaf_green", (0.26, 0.55, 0.22, 1.0), 0.62)
    obj.data.materials.clear()
    obj.data.materials.append(brown)
    obj.data.materials.append(green)
    obj.data.materials.append(light)
    zs = [v.co.z for v in obj.data.vertices]
    lo, hi = min(zs), max(zs)
    span = max(hi - lo, 1e-6)
    for poly in obj.data.polygons:
        z = sum(obj.data.vertices[i].co.z for i in poly.vertices) / len(poly.vertices)
        t = (z - lo) / span
        poly.material_index = 0 if t < 0.22 else (1 if t < 0.72 else 2)
        poly.use_smooth = True
    mod = obj.modifiers.new("probe_weighted_normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except RuntimeError:
        pass


def transform_obj(obj: bpy.types.Object, variant: str) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if variant == "identity":
        return
    if variant == "rot_x_180":
        obj.rotation_euler[0] += math.pi
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    elif variant == "rot_y_180":
        obj.rotation_euler[1] += math.pi
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    elif variant == "rot_z_180":
        obj.rotation_euler[2] += math.pi
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    elif variant == "mesh_neg_z":
        obj.data.transform(Matrix.Scale(-1.0, 4, Vector((0.0, 0.0, 1.0))))
        obj.data.update()
    elif variant == "mesh_neg_y":
        obj.data.transform(Matrix.Scale(-1.0, 4, Vector((0.0, 1.0, 0.0))))
        obj.data.update()
    elif variant == "mesh_neg_x":
        obj.data.transform(Matrix.Scale(-1.0, 4, Vector((1.0, 0.0, 0.0))))
        obj.data.update()
    else:
        raise ValueError(variant)


def normalize(obj: bpy.types.Object) -> dict[str, float | list[float]]:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    bpy.context.view_layer.update()
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    center = sum(corners, Vector()) / 8.0
    obj.location -= center
    bpy.context.view_layer.update()
    max_dim = max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z, 1e-6)
    obj.scale *= 2.25 / max_dim
    bpy.context.view_layer.update()
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_z = min(c.z for c in corners)
    obj.location.z -= min_z
    bpy.context.view_layer.update()
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(getattr(c, axis) for c in corners) for axis in ("x", "y", "z")]
    maxs = [max(getattr(c, axis) for c in corners) for axis in ("x", "y", "z")]
    return {
        "center_x": (mins[0] + maxs[0]) * 0.5,
        "center_y": (mins[1] + maxs[1]) * 0.5,
        "center_z": (mins[2] + maxs[2]) * 0.5,
        "max_z": maxs[2],
    }


def set_scene(resolution: int = 640) -> None:
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.55
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.image_settings.file_format = "PNG"
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = False
    world.color = (0.91, 0.95, 0.97)
    mat = make_mat("probe_stage_mat", (0.88, 0.93, 0.95, 1.0), 0.74)
    bpy.ops.mesh.primitive_plane_add(size=7.0, location=(0.0, 0.0, 0.0))
    plane = bpy.context.object
    plane.name = "probe_stage"
    plane.data.materials.append(mat)
    bpy.ops.object.light_add(type="AREA", location=(0.0, -4.0, 6.0))
    key = bpy.context.object
    key.data.energy = 900
    key.data.size = 5.5
    bpy.ops.object.light_add(type="AREA", location=(-3.0, 2.5, 4.0))
    fill = bpy.context.object
    fill.data.energy = 380
    fill.data.size = 6.5


def add_camera(bounds: dict[str, float | list[float]]) -> None:
    target = Vector((float(bounds["center_x"]), float(bounds["center_y"]), float(bounds["center_z"])))
    direction = Vector((0.0, -1.0, 0.16)).normalized()
    loc = target + direction * 8.0
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.rotation_euler = (target - loc).to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 2.8
    bpy.context.scene.camera = cam


def export_selected(obj: bpy.types.Object, path: Path, export_yup: bool) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True, export_yup=export_yup)


def render_variant(variant: str, export_yup: bool) -> tuple[Path, Path]:
    clear_scene()
    obj = import_joined(SOURCE, f"{variant}_{'yup' if export_yup else 'native'}")
    transform_obj(obj, variant)
    recolor_by_height(obj)
    glb = OUT / f"{variant}_{'yup' if export_yup else 'native'}.glb"
    export_selected(obj, glb, export_yup)

    clear_scene()
    set_scene()
    obj = import_joined(glb, glb.stem)
    bounds = normalize(obj)
    add_camera(bounds)
    png = OUT / f"{variant}_{'yup' if export_yup else 'native'}.png"
    bpy.context.scene.render.filepath = str(png)
    bpy.ops.render.render(write_still=True)
    return glb, png


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    variants = ["identity", "rot_x_180", "rot_y_180", "rot_z_180", "mesh_neg_z", "mesh_neg_y", "mesh_neg_x"]
    for export_yup in (True, False):
        for variant in variants:
            glb, png = render_variant(variant, export_yup)
            print(glb)
            print(png)


if __name__ == "__main__":
    main()
