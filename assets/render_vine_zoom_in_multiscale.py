#!/usr/bin/env python3
"""Render multi-scale Blender zoom-in panels for the strongest vine mesh."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_obj(path: Path):
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=str(path))
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
    obj.name = "vine_d5_projected_compete_stage_05"
    return obj


def normalize_object(obj, target_extent: float = 3.0) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    bpy.context.view_layer.update()
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    center = sum(corners, Vector()) / 8.0
    obj.location -= center
    bpy.context.view_layer.update()
    dims = obj.dimensions
    scale = target_extent / max(dims.x, dims.y, dims.z, 1e-6)
    obj.scale *= scale
    bpy.context.view_layer.update()


def make_vine_material():
    mat = bpy.data.materials.new("botanical_bark_pbr")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return mat
    if "Base Color" in bsdf.inputs:
        bsdf.inputs["Base Color"].default_value = (0.30, 0.25, 0.16, 1.0)
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = 0.74
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = 0.0

    noise = nodes.new(type="ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 24.0
    noise.inputs["Detail"].default_value = 12.0
    noise.inputs["Roughness"].default_value = 0.58
    ramp = nodes.new(type="ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.13, 0.11, 0.07, 1.0)
    ramp.color_ramp.elements[1].position = 1.00
    ramp.color_ramp.elements[1].color = (0.46, 0.41, 0.25, 1.0)
    mat.node_tree.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    mat.node_tree.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    mat.diffuse_color = (0.30, 0.25, 0.16, 1.0)
    return mat


def assign_material(obj) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(make_vine_material())
    for poly in obj.data.polygons:
        poly.use_smooth = True
    mod = obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True


def setup_render(resolution: int, samples: int) -> None:
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.color = (0.965, 0.958, 0.938)


def add_lighting() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-1.4, -4.8, 5.2))
    key = bpy.context.object
    key.name = "large_softbox_key"
    key.data.energy = 520
    key.data.size = 5.0

    bpy.ops.object.light_add(type="AREA", location=(3.6, 2.4, 2.2))
    rim = bpy.context.object
    rim.name = "warm_rim"
    rim.data.energy = 90
    rim.data.size = 3.0


def add_ground(z: float = -1.47) -> None:
    bpy.ops.mesh.primitive_plane_add(size=6.0, location=(0, 0, z))
    plane = bpy.context.object
    plane.name = "matte_warm_ground"
    mat = bpy.data.materials.new("matte_warm_ground")
    mat.diffuse_color = (0.82, 0.82, 0.78, 1.0)
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (0.82, 0.82, 0.78, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.86
    plane.data.materials.append(mat)


def world_vertices(obj):
    matrix = obj.matrix_world
    return [matrix @ v.co for v in obj.data.vertices]


def quantile(values, q: float) -> float:
    values = sorted(values)
    if not values:
        return 0.0
    pos = min(max(q, 0.0), 1.0) * (len(values) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - pos) + values[hi] * (pos - lo)


def masked_mean(vertices, predicate, fallback: Vector) -> Vector:
    selected = [v for v in vertices if predicate(v)]
    if not selected:
        return fallback.copy()
    return sum(selected, Vector()) / len(selected)


def panel_targets(obj):
    verts = world_vertices(obj)
    xs = [v.x for v in verts]
    ys = [v.y for v in verts]
    zs = [v.z for v in verts]
    center = Vector(
        (
            (min(xs) + max(xs)) * 0.5,
            (min(ys) + max(ys)) * 0.5,
            (min(zs) + max(zs)) * 0.5,
        )
    )
    y72 = quantile(ys, 0.72)
    y88 = quantile(ys, 0.88)
    z55 = quantile(zs, 0.55)
    z70 = quantile(zs, 0.70)
    x62 = quantile(xs, 0.62)
    branch = masked_mean(verts, lambda v: v.y >= y72 and v.z >= z55, center)
    tip = masked_mean(verts, lambda v: v.y >= y88 and v.z >= z70 and v.x >= x62, branch)
    return [
        ("A_overview", "overview", center, 3.60, 70.0),
        ("B_branch_zoom", "branch-level recursion", branch + Vector((0.00, 0.03, 0.04)), 1.35, 95.0),
        ("C_tip_zoom", "terminal detail", tip + Vector((0.03, 0.02, 0.02)), 0.62, 115.0),
    ]


def add_camera(target: Vector, ortho_scale: float, lens_label: float) -> None:
    direction = Vector((4.2, -5.0, 3.1)).normalized()
    loc = target + direction * 5.5
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.name = f"camera_{int(lens_label)}mm_equiv"
    cam.rotation_euler = (target - loc).to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho_scale
    bpy.context.scene.camera = cam


def add_target_marker(target: Vector, scale: float) -> None:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=scale, location=target)
    marker = bpy.context.object
    marker.name = "subtle_zoom_target_marker"
    mat = bpy.data.materials.new("target_marker_muted_gold")
    mat.diffuse_color = (0.95, 0.72, 0.22, 1.0)
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (0.95, 0.72, 0.22, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.48
    marker.data.materials.append(mat)


def render_panel(mesh_path: Path, out_path: Path, panel, resolution: int, samples: int) -> None:
    clear_scene()
    setup_render(resolution, samples)
    obj = import_obj(mesh_path)
    normalize_object(obj)
    assign_material(obj)
    add_ground()
    add_lighting()
    _, _, target, ortho_scale, lens_label = panel
    add_camera(target, ortho_scale, lens_label)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)


def make_emission_image_material(name: str, image_path: Path):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    image = nodes.new(type="ShaderNodeTexImage")
    image.image = bpy.data.images.load(str(image_path))
    emission = nodes.new(type="ShaderNodeEmission")
    output = nodes.new(type="ShaderNodeOutputMaterial")
    mat.node_tree.links.new(image.outputs["Color"], emission.inputs["Color"])
    mat.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return mat


def add_text(label: str, location, size: float, align: str = "CENTER") -> None:
    bpy.ops.object.text_add(location=location, rotation=(0, 0, 0))
    text = bpy.context.object
    text.name = f"text_{label[:12]}"
    text.data.body = label
    text.data.align_x = align
    text.data.align_y = "CENTER"
    text.data.size = size
    text.data.font = text.data.font
    mat = bpy.data.materials.new(f"text_mat_{label[:12]}")
    mat.diffuse_color = (0.10, 0.10, 0.09, 1.0)
    text.data.materials.append(mat)


def composite_panels(panel_paths, labels, final_path: Path, width: int, height: int) -> None:
    clear_scene()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.color = (0.96, 0.955, 0.935)

    panel_size = 2.0
    gap = 0.18
    start_x = -(panel_size + gap)
    for idx, (path, label) in enumerate(zip(panel_paths, labels)):
        x = start_x + idx * (panel_size + gap)
        bpy.ops.mesh.primitive_plane_add(size=panel_size, location=(x, 0.08, 0))
        plane = bpy.context.object
        plane.name = f"panel_{idx + 1}"
        plane.data.materials.append(make_emission_image_material(f"panel_mat_{idx + 1}", path))
        add_text(label, (x, -1.12, 0.02), 0.085)

    add_text("Recursive vine mesh: multi-scale Blender zoom-in", (0, 1.25, 0.02), 0.105)

    bpy.ops.object.camera_add(location=(0, 0, 5.0), rotation=(0, 0, 0))
    cam = bpy.context.object
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 3.05
    scene.camera = cam
    final_path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(final_path)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--resolution", type=int, default=1400)
    parser.add_argument("--samples", type=int, default=80)
    parser.add_argument("--final-width", type=int, default=4200)
    parser.add_argument("--final-height", type=int, default=1550)
    parser.add_argument("--reuse-panels", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = parser.parse_args(argv)

    args.work_dir.mkdir(parents=True, exist_ok=True)
    clear_scene()
    obj = import_obj(args.mesh)
    normalize_object(obj)
    panels = panel_targets(obj)
    labels = [f"{name.split('_', 1)[0]}  {label}" for name, label, *_ in panels]
    panel_paths = [args.work_dir / f"{name}.png" for name, *_ in panels]

    for panel, path in zip(panels, panel_paths):
        if args.reuse_panels and path.exists():
            continue
        render_panel(args.mesh, path, panel, args.resolution, args.samples)

    composite_panels(panel_paths, labels, args.out, args.final_width, args.final_height)
    print(args.out)


if __name__ == "__main__":
    main()
