#!/usr/bin/env python3
"""Render a compact front-view placeholder for the five-case hero combo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import bpy  # type: ignore
    from mathutils import Vector  # type: ignore
except Exception as exc:  # pragma: no cover
    raise SystemExit("Run with Blender Python.") from exc


REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "visuals" / "hero_combo_publication_20260510_placeholder_front_compact"


CASES = [
    {
        "label": "bismuth",
        "mesh": REPO
        / "visuals/connected_scaffold_v2_textured_glb_hq_20260509"
        / "bismuth_hopper_bismuth_hq_steps8_tex2048_xformers/textured.glb",
        "scale": 2.62,
        "loc": (-2.42, 0.28, 0.0),
    },
    {
        "label": "pyrite",
        "mesh": REPO
        / "visuals/connected_scaffold_v2_textured_glb_hq_20260509"
        / "pyrite_lattice_pyrite_hq_steps8_tex2048_xformers/textured.glb",
        "scale": 2.50,
        "loc": (-1.18, 0.12, 0.0),
    },
    {
        "label": "coral",
        "mesh": REPO
        / "visuals/connected_scaffold_v2_textured_glb_hq_20260509"
        / "volumetric_dla_coral_octopus_hq_steps8_tex2048_xformers/textured.glb",
        "scale": 2.22,
        "loc": (0.05, -0.04, 0.0),
    },
    {
        "label": "tree_compete",
        "mesh": REPO / "visuals/hero_botanical_variants_20260510/tree_compete_s3_green_leaf_brown_root.glb",
        "scale": 2.36,
        "loc": (1.21, 0.08, 0.0),
    },
    {
        "label": "vine_stage5",
        "mesh": REPO
        / "visuals/hero_botanical_variants_20260510"
        / "vine_stage5_parthenocissus_warm_upright_green_leaf_brown_base.glb",
        "scale": 1.92,
        "loc": (2.50, -0.12, 0.0),
    },
]


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def set_scene(resolution: int, samples: int) -> None:
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 5
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.65
    scene.view_settings.gamma = 1.0
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = False
    world.color = (0.91, 0.95, 0.97)


def import_glb(path: Path, label: str) -> bpy.types.Object:
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


def bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    lo = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    hi = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    return lo, hi


def normalize_place(obj: bpy.types.Object, target_extent: float, loc: tuple[float, float, float]) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    bpy.context.view_layer.update()
    lo, hi = bounds(obj)
    center = (lo + hi) * 0.5
    obj.location -= center
    bpy.context.view_layer.update()
    max_dim = max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z, 1e-6)
    obj.scale *= target_extent / max_dim
    bpy.context.view_layer.update()
    lo, _ = bounds(obj)
    obj.location.x += loc[0]
    obj.location.y += loc[1]
    obj.location.z += loc[2] - lo.z
    bpy.context.view_layer.update()


def prepare_mesh(obj: bpy.types.Object, smooth: bool = True) -> None:
    if smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True
    mod = obj.modifiers.new("placeholder_weighted_normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True


def make_material(name: str, color: tuple[float, float, float, float], roughness: float = 0.72) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
    return mat


def add_stage() -> None:
    mat = make_material("placeholder_blue_gray_stage", (0.88, 0.93, 0.95, 1.0), 0.74)
    bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0.0, -0.15, 0.0))
    plane = bpy.context.object
    plane.name = "placeholder_stage"
    plane.data.materials.append(mat)


def add_lighting() -> None:
    bpy.ops.object.light_add(type="AREA", location=(0.0, -4.2, 6.2))
    key = bpy.context.object
    key.data.energy = 1250
    key.data.size = 7.5
    bpy.ops.object.light_add(type="AREA", location=(-3.0, -1.0, 4.2))
    fill = bpy.context.object
    fill.data.energy = 420
    fill.data.size = 8.0
    bpy.ops.object.light_add(type="AREA", location=(3.0, 2.5, 4.0))
    rim = bpy.context.object
    rim.data.energy = 260
    rim.data.size = 6.0


def add_camera(ortho_scale: float) -> bpy.types.Object:
    target = Vector((0.0, 0.0, 1.25))
    loc = Vector((0.0, -9.5, 1.55))
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.rotation_euler = (target - loc).to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho_scale
    return cam


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--resolution", type=int, default=1600)
    parser.add_argument("--samples", type=int, default=48)
    parser.add_argument("--ortho-scale", type=float, default=5.9)
    return parser.parse_args(argv)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = parse_args(argv)
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    clear_scene()
    set_scene(args.resolution, args.samples)
    objects = []
    for case in CASES:
        obj = import_glb(case["mesh"], case["label"])
        normalize_place(obj, case["scale"], case["loc"])
        prepare_mesh(obj, smooth=True)
        objects.append(obj)
    add_stage()
    add_lighting()
    cam = add_camera(args.ortho_scale)
    bpy.context.scene.camera = cam
    path = out_dir / "overview_front_compact_raw.png"
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print(path)


if __name__ == "__main__":
    main()
