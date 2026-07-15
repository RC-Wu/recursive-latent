import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_mesh(path: Path):
    before = set(bpy.data.objects)
    suffix = path.suffix.lower()
    if suffix == ".obj":
        bpy.ops.wm.obj_import(filepath=str(path))
    elif suffix in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    else:
        raise ValueError(f"Unsupported mesh format: {path}")
    imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    if not imported:
        raise RuntimeError(f"No mesh imported from {path}")
    for obj in imported:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = imported[0]
    if len(imported) > 1:
        bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = path.stem
    return obj


def normalize_object(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    bpy.context.view_layer.update()
    center = sum((Vector(corner) for corner in obj.bound_box), Vector()) / 8.0
    obj.location -= obj.matrix_world @ center
    bpy.context.view_layer.update()
    dims = obj.dimensions
    scale = max(dims.x, dims.y, dims.z, 1e-6)
    obj.scale *= 3.0 / scale
    bpy.context.view_layer.update()


def _set_bsdf_value(bsdf, key: str, value):
    if bsdf is not None and key in bsdf.inputs:
        bsdf.inputs[key].default_value = value


def _make_principled_material(name: str, base, secondary=None, roughness=0.62, metallic=0.0, noise=False):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    _set_bsdf_value(bsdf, "Metallic", metallic)
    _set_bsdf_value(bsdf, "Roughness", roughness)
    _set_bsdf_value(bsdf, "Base Color", base)
    mat.diffuse_color = base
    if noise and bsdf is not None and secondary is not None and "Base Color" in bsdf.inputs:
        noise_node = nodes.new(type="ShaderNodeTexNoise")
        noise_node.inputs["Scale"].default_value = 18.0
        noise_node.inputs["Detail"].default_value = 9.0
        noise_node.inputs["Roughness"].default_value = 0.58
        ramp = nodes.new(type="ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.18
        ramp.color_ramp.elements[0].color = secondary
        ramp.color_ramp.elements[1].position = 1.0
        ramp.color_ramp.elements[1].color = base
        mat.node_tree.links.new(noise_node.outputs["Fac"], ramp.inputs["Fac"])
        mat.node_tree.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def _material_preset(name: str, material_mode: str):
    lowered = name.lower()
    mode = material_mode
    if mode == "auto":
        if any(key in lowered for key in ["tree", "root", "vine", "plant"]):
            mode = "botanical"
        elif any(key in lowered for key in ["portal", "arch", "ruin", "stone", "city"]):
            mode = "stone"
        elif any(key in lowered for key in ["crystal", "dla", "porous"]):
            mode = "crystal"
        elif any(key in lowered for key in ["scifi", "gear", "metal", "module"]):
            mode = "metal"
        else:
            mode = "neutral"
    if mode == "botanical":
        return _make_principled_material(f"{name}_botanical_pbr", (0.24, 0.36, 0.22, 1.0), (0.50, 0.60, 0.42, 1.0), 0.66, 0.0, True)
    if mode == "bark":
        return _make_principled_material(f"{name}_bark_pbr", (0.40, 0.26, 0.15, 1.0), (0.18, 0.11, 0.06, 1.0), 0.78, 0.0, True)
    if mode == "stone":
        return _make_principled_material(f"{name}_stone_pbr", (0.58, 0.56, 0.52, 1.0), (0.30, 0.32, 0.33, 1.0), 0.82, 0.0, True)
    if mode == "metal":
        return _make_principled_material(f"{name}_brushed_metal_pbr", (0.62, 0.64, 0.60, 1.0), (0.30, 0.34, 0.35, 1.0), 0.32, 0.85, True)
    if mode == "crystal":
        return _make_principled_material(f"{name}_green_crystal_pbr", (0.10, 0.42, 0.20, 1.0), (0.70, 0.88, 0.58, 1.0), 0.18, 0.05, True)
    return _make_principled_material(f"{name}_teal_gold_clay", (0.46, 0.54, 0.40, 1.0), None, 0.62, 0.0, False)


def assign_material(obj, name: str, material_mode: str = "neutral"):
    mat = _material_preset(name, material_mode)
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    mod = obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True


def preserve_materials(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True
    mod = obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True


def setup_world(samples: int, resolution: int, background: str):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.film_transparent = background == "white"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA" if background == "white" else "RGB"
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = False
    if background == "white":
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"
        scene.view_settings.exposure = 0.0
        scene.view_settings.gamma = 1.0
        world.color = (1.0, 1.0, 1.0)
    else:
        world.color = (0.96, 0.96, 0.94)


def add_lighting():
    bpy.ops.object.light_add(type="AREA", location=(0.0, -4.5, 5.5))
    key = bpy.context.object
    key.name = "large_softbox"
    key.data.energy = 450
    key.data.size = 5.0
    bpy.ops.object.light_add(type="POINT", location=(-3.5, 3.0, 3.0))
    fill = bpy.context.object
    fill.name = "small_fill"
    fill.data.energy = 60


def add_camera(view: str):
    if view == "front":
        loc = (0.0, -6.0, 1.0)
        rot = (math.radians(80), 0.0, 0.0)
    elif view == "side":
        loc = (6.0, -0.2, 1.0)
        rot = (math.radians(80), 0.0, math.radians(88))
    else:
        loc = (4.2, -5.2, 3.0)
        direction = Vector((0, 0, 0)) - Vector(loc)
        rot = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.camera_add(location=loc, rotation=rot)
    cam = bpy.context.object
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 4.2
    bpy.context.scene.camera = cam


def add_ground(background: str):
    plane_size = 200.0 if background == "white" else 5.2
    bpy.ops.mesh.primitive_plane_add(size=plane_size, location=(0, 0, -1.45))
    plane = bpy.context.object
    plane.name = "matte_ground"
    if background == "white":
        ground_color = (1.0, 1.0, 1.0, 1)
        ground_name = "white_ground"
    else:
        ground_color = (0.84, 0.84, 0.80, 1)
        ground_name = "warm_gray_ground"
    mat = bpy.data.materials.new(name=ground_name)
    mat.diffuse_color = ground_color
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = ground_color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.8
    plane.data.materials.append(mat)
    if background == "white":
        if hasattr(plane, "is_shadow_catcher"):
            plane.is_shadow_catcher = True
        elif hasattr(plane, "cycles") and hasattr(plane.cycles, "is_shadow_catcher"):
            plane.cycles.is_shadow_catcher = True


def render_case(
    mesh_path: Path,
    out_path: Path,
    label: str,
    view: str,
    samples: int,
    resolution: int,
    save_blend: bool,
    material_mode: str,
    background: str,
):
    clear_scene()
    setup_world(samples, resolution, background)
    obj = import_mesh(mesh_path)
    normalize_object(obj)
    if material_mode == "preserve":
        preserve_materials(obj)
    else:
        assign_material(obj, label, material_mode)
    if background != "white":
        add_ground(background)
    add_lighting()
    add_camera(view)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.render.filepath = str(out_path)
    if save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(out_path.with_suffix(".blend")))
    bpy.ops.render.render(write_still=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", help="label=/abs/path.obj")
    parser.add_argument("--case-file", type=Path, help="Text file with one label=/abs/path mesh per line")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--views", nargs="+", default=["iso"])
    parser.add_argument("--samples", type=int, default=96)
    parser.add_argument("--resolution", type=int, default=1800)
    parser.add_argument("--save-blend", action="store_true")
    parser.add_argument("--material-mode", choices=["neutral", "preserve", "auto", "botanical", "bark", "stone", "metal", "crystal"], default="neutral")
    parser.add_argument(
        "--background",
        choices=["white", "studio-gray"],
        default="white",
        help="Render background. Default 'white' is the paper-safe mode: pure white world, transparent PNG, no ground plane/platform/horizon.",
    )
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = parser.parse_args(argv)

    cases = list(args.case or [])
    if args.case_file:
        for line in args.case_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                cases.append(line)

    for item in cases:
        label, path = item.split("=", 1)
        for view in args.views:
            render_case(
                Path(path),
                args.out_dir / f"{label}_{view}.png",
                label,
                view,
                args.samples,
                args.resolution,
                args.save_blend,
                args.material_mode,
                args.background,
            )


if __name__ == "__main__":
    main()
