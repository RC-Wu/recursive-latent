import argparse
import glob
import json
import math
import re
import sys
from pathlib import Path

import bpy
from mathutils import Vector


DEFAULT_STAGE_GLOB = (
    "visuals/siga_night_20260508/siga_projected_recursive_loop_0715/"
    "vine_d5_projected_compete/stage_*/projected/*/mesh_pruned.obj"
)


def parse_blender_args():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Create a local Blender prototype video for recursive stage-mesh growth."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--stage-glob", default=DEFAULT_STAGE_GLOB)
    parser.add_argument("--out-dir", type=Path, default=Path("visuals/demo_video_20260509"))
    parser.add_argument("--basename", default="recursive_growth_demo")
    parser.add_argument("--resolution", type=int, default=960)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--hold-frames", type=int, default=14)
    parser.add_argument("--transition-frames", type=int, default=10)
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--engine", choices=["eevee", "cycles"], default="eevee")
    parser.add_argument("--save-blend", action="store_true")
    parser.add_argument(
        "--image-sequence",
        action="store_true",
        help="Also render PNG frames to out-dir/frames.",
    )
    return parser.parse_args(argv)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def resolve_stage_paths(repo_root: Path, pattern: str):
    pattern_path = Path(pattern)
    search = pattern if pattern_path.is_absolute() else str(repo_root / pattern)
    paths = [Path(p) for p in glob.glob(search)]
    if not paths:
        raise FileNotFoundError(f"No stage meshes matched: {search}")

    def stage_key(path: Path):
        match = re.search(r"stage_(\d+)", str(path))
        return int(match.group(1)) if match else 9999

    return sorted(paths, key=stage_key)


def import_mesh(path: Path):
    before = set(bpy.data.objects)
    if path.suffix.lower() == ".obj":
        if hasattr(bpy.ops.wm, "obj_import"):
            bpy.ops.wm.obj_import(filepath=str(path))
        else:
            bpy.ops.import_scene.obj(filepath=str(path))
    elif path.suffix.lower() in {".glb", ".gltf"}:
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
    obj.name = stage_label(path)
    return obj


def stage_label(path: Path):
    match = re.search(r"stage_(\d+)", str(path))
    return f"stage_{int(match.group(1)):02d}" if match else path.stem


def material_for_stage(index: int, total: int):
    t = index / max(total - 1, 1)
    base = (0.18 + 0.36 * t, 0.34 + 0.30 * t, 0.20 + 0.12 * t, 1.0)
    accent = (0.74, 0.83, 0.45, 1.0)
    mat = bpy.data.materials.new(f"recursive_growth_stage_{index + 1:02d}")
    mat.use_nodes = True
    mat.diffuse_color = base
    nodes = mat.node_tree.nodes
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = base
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.64
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = 1.0
        noise = nodes.new(type="ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 16.0
        noise.inputs["Detail"].default_value = 7.0
        ramp = nodes.new(type="ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.22
        ramp.color_ramp.elements[0].color = base
        ramp.color_ramp.elements[1].position = 1.0
        ramp.color_ramp.elements[1].color = accent
        mat.node_tree.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        mat.node_tree.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def set_smooth_weighted_normals(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True
    mod = obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True


def normalize_collection(objects):
    bpy.context.view_layer.update()
    mins = Vector((float("inf"), float("inf"), float("inf")))
    maxs = Vector((float("-inf"), float("-inf"), float("-inf")))
    for obj in objects:
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            mins.x = min(mins.x, world.x)
            mins.y = min(mins.y, world.y)
            mins.z = min(mins.z, world.z)
            maxs.x = max(maxs.x, world.x)
            maxs.y = max(maxs.y, world.y)
            maxs.z = max(maxs.z, world.z)
    center = (mins + maxs) * 0.5
    extent = max((maxs - mins).x, (maxs - mins).y, (maxs - mins).z, 1e-6)
    scale = 3.1 / extent
    for obj in objects:
        obj.location = (obj.location - center) * scale
        obj.scale *= scale
    bpy.context.view_layer.update()


def setup_render(args):
    scene = bpy.context.scene
    if args.engine == "cycles":
        scene.render.engine = "CYCLES"
        scene.cycles.samples = args.samples
        scene.cycles.use_denoising = True
    else:
        scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items else "BLENDER_EEVEE"
        if hasattr(scene, "eevee"):
            scene.eevee.taa_render_samples = args.samples
    scene.render.resolution_x = args.resolution
    scene.render.resolution_y = int(args.resolution * 9 / 16)
    scene.render.fps = args.fps
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.render.film_transparent = False
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.color = (0.035, 0.040, 0.042)


def add_lighting_and_camera():
    bpy.ops.object.light_add(type="AREA", location=(0.0, -4.5, 5.0))
    key = bpy.context.object
    key.name = "large_softbox_key"
    key.data.energy = 550
    key.data.size = 5.5
    bpy.ops.object.light_add(type="POINT", location=(-3.3, 3.2, 2.8))
    fill = bpy.context.object
    fill.name = "growth_rim_fill"
    fill.data.energy = 90

    cam_loc = Vector((4.2, -5.2, 3.0))
    direction = Vector((0.0, 0.0, 0.05)) - cam_loc
    bpy.ops.object.camera_add(location=cam_loc, rotation=direction.to_track_quat("-Z", "Y").to_euler())
    cam = bpy.context.object
    cam.name = "growth_demo_camera"
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 4.4
    bpy.context.scene.camera = cam


def add_ground():
    bpy.ops.mesh.primitive_plane_add(size=5.6, location=(0.0, 0.0, -1.62))
    plane = bpy.context.object
    plane.name = "matte_reference_ground"
    mat = bpy.data.materials.new("warm_dark_ground")
    mat.diffuse_color = (0.13, 0.14, 0.13, 1.0)
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (0.13, 0.14, 0.13, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.82
    plane.data.materials.append(mat)


def animate_stages(objects, hold_frames: int, transition_frames: int):
    scene = bpy.context.scene
    segment = hold_frames + transition_frames
    total_frames = segment * len(objects)
    scene.frame_start = 1
    scene.frame_end = total_frames

    for idx, obj in enumerate(objects):
        start = idx * segment + 1
        grow_end = start + transition_frames
        hold_end = start + segment - 1
        obj.rotation_euler[2] = math.radians(-7 + idx * 3)

        for frame, visible, scale_value in [
            (1, False, 0.70),
            (max(start - 1, 1), False, 0.70),
            (start, True, 0.70),
            (grow_end, True, 1.0),
            (hold_end, True, 1.0),
            (min(hold_end + 1, total_frames), False, 1.0),
        ]:
            scene.frame_set(frame)
            obj.hide_viewport = not visible
            obj.hide_render = not visible
            obj.scale = tuple(scale_value * component for component in obj["base_scale"])
            obj.keyframe_insert("hide_viewport", frame=frame)
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("scale", frame=frame)
            obj.keyframe_insert("rotation_euler", frame=frame)

    for obj in objects:
        action = obj.animation_data.action if obj.animation_data else None
        curves = getattr(action, "fcurves", []) if action else []
        for fcurve in curves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = "SINE"
    return total_frames


def ffmpeg_available():
    formats = bpy.context.scene.render.image_settings.bl_rna.properties["file_format"].enum_items
    return any(item.identifier == "FFMPEG" for item in formats)


def render_mp4(out_path: Path):
    if not ffmpeg_available():
        return False
    scene = bpy.context.scene
    scene.render.filepath = str(out_path)
    try:
        scene.render.image_settings.file_format = "FFMPEG"
    except TypeError:
        return False
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    bpy.ops.render.render(animation=True)
    return True


def render_image_sequence(frame_dir: Path):
    scene = bpy.context.scene
    frame_dir.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(frame_dir / "frame_")
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(animation=True)


def main():
    args = parse_blender_args()
    repo_root = args.repo_root.resolve()
    out_dir = (repo_root / args.out_dir).resolve() if not args.out_dir.is_absolute() else args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    clear_scene()
    setup_render(args)
    stage_paths = resolve_stage_paths(repo_root, args.stage_glob)

    objects = []
    for idx, path in enumerate(stage_paths):
        obj = import_mesh(path)
        obj.data.materials.clear()
        obj.data.materials.append(material_for_stage(idx, len(stage_paths)))
        set_smooth_weighted_normals(obj)
        objects.append(obj)

    normalize_collection(objects)
    for obj in objects:
        obj["base_scale"] = tuple(obj.scale)

    add_ground()
    add_lighting_and_camera()
    animate_stages(objects, args.hold_frames, args.transition_frames)

    mp4_path = out_dir / f"{args.basename}.mp4"
    wrote_mp4 = render_mp4(mp4_path)
    wrote_frames = False
    if args.image_sequence or not wrote_mp4:
        render_image_sequence(out_dir / "frames")
        wrote_frames = True
    if args.save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(out_dir / f"{args.basename}.blend"))

    manifest = {
        "prototype": True,
        "stage_glob": args.stage_glob,
        "stage_meshes": [str(path.relative_to(repo_root)) if path.is_relative_to(repo_root) else str(path) for path in stage_paths],
        "frame_start": bpy.context.scene.frame_start,
        "frame_end": bpy.context.scene.frame_end,
        "fps": args.fps,
        "mp4": str(mp4_path.relative_to(repo_root)) if wrote_mp4 and mp4_path.is_relative_to(repo_root) else (str(mp4_path) if wrote_mp4 else None),
        "image_sequence": str((out_dir / "frames").relative_to(repo_root)) if wrote_frames and (out_dir / "frames").is_relative_to(repo_root) else (str(out_dir / "frames") if wrote_frames else None),
    }
    (out_dir / f"{args.basename}_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
