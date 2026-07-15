#!/usr/bin/env python3
"""Prepare publication-hero botanical GLB variants.

This is intentionally a Blender-side deterministic postprocess: it keeps the
source geometry provenance, but creates head-figure presentation variants for
the two botanical cases the user selected on 2026-05-10.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

try:
    import bpy  # type: ignore
    from mathutils import Matrix, Vector  # type: ignore
except Exception as exc:  # pragma: no cover - Blender-only script
    raise SystemExit("This script must be run with Blender's Python.") from exc


REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "visuals" / "hero_botanical_variants_20260510"

TREE_SOURCE = REPO / "visuals/textured_glb_20260508/tree_compete_s3/textured.glb"
VINE_SOURCE = (
    REPO
    / "visuals/vine_stage5_guide_sweep_20260509"
    / "vine_stage5_parthenocissus_warm_steps8_tex2048_xformers/textured.glb"
)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_principled(name: str, color: tuple[float, float, float, float], roughness: float) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
    return mat


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
    obj.data.name = f"{label}_mesh"
    return obj


def apply_weighted_normals(obj: bpy.types.Object) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    mod = obj.modifiers.new("publication_weighted_normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except RuntimeError:
        pass


def local_z_bounds(obj: bpy.types.Object) -> tuple[float, float]:
    zs = [vertex.co.z for vertex in obj.data.vertices]
    return min(zs), max(zs)


def assign_by_height(
    obj: bpy.types.Object,
    low_material: bpy.types.Material,
    high_material: bpy.types.Material,
    split_fraction: float,
    middle_material: bpy.types.Material | None = None,
) -> dict[str, float | int]:
    obj.data.materials.clear()
    obj.data.materials.append(low_material)
    if middle_material is not None:
        obj.data.materials.append(middle_material)
    obj.data.materials.append(high_material)
    high_index = len(obj.data.materials) - 1
    middle_index = 1 if middle_material is not None else high_index
    low_z, high_z = local_z_bounds(obj)
    span = max(high_z - low_z, 1e-6)
    split = low_z + span * split_fraction
    middle_split = low_z + span * min(split_fraction + 0.12, 0.82)
    low_count = middle_count = high_count = 0
    for poly in obj.data.polygons:
        z = sum(obj.data.vertices[idx].co.z for idx in poly.vertices) / max(len(poly.vertices), 1)
        if z < split:
            poly.material_index = 0
            low_count += 1
        elif middle_material is not None and z < middle_split:
            poly.material_index = middle_index
            middle_count += 1
        else:
            poly.material_index = high_index
            high_count += 1
    return {
        "min_z": float(low_z),
        "max_z": float(high_z),
        "split_z": float(split),
        "low_faces": low_count,
        "middle_faces": middle_count,
        "high_faces": high_count,
    }


def export_selected(obj: bpy.types.Object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
    )


def normalize_for_preview(obj: bpy.types.Object) -> dict[str, list[float] | float]:
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
    min_z = min(corner.z for corner in corners)
    obj.location.z -= min_z
    bpy.context.view_layer.update()
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(getattr(corner, axis) for corner in corners) for axis in ("x", "y", "z")]
    maxs = [max(getattr(corner, axis) for corner in corners) for axis in ("x", "y", "z")]
    return {
        "min": [float(v) for v in mins],
        "max": [float(v) for v in maxs],
        "extent": float(max(maxs[i] - mins[i] for i in range(3))),
    }


def set_preview_scene(resolution: int, samples: int) -> None:
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.45
    scene.view_settings.gamma = 1.0
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.image_settings.file_format = "PNG"
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = False
    world.color = (0.91, 0.95, 0.97)


def add_preview_stage() -> None:
    mat = make_principled("preview_light_blue_gray_stage", (0.88, 0.93, 0.95, 1.0), 0.74)
    bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0.0, 0.0, 0.0))
    plane = bpy.context.object
    plane.name = "preview_stage"
    plane.data.materials.append(mat)
    bpy.ops.object.light_add(type="AREA", location=(0.0, -3.5, 5.8))
    key = bpy.context.object
    key.name = "preview_key_softbox"
    key.data.energy = 760
    key.data.size = 5.5
    bpy.ops.object.light_add(type="AREA", location=(-2.4, 2.2, 4.2))
    fill = bpy.context.object
    fill.name = "preview_fill_softbox"
    fill.data.energy = 360
    fill.data.size = 6.0


def add_preview_camera(target: tuple[float, float, float], ortho_scale: float) -> bpy.types.Object:
    target_v = Vector(target)
    direction = Vector((4.8, -6.0, 3.4)).normalized()
    loc = target_v + direction * 9.0
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.rotation_euler = (target_v - loc).to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho_scale
    return cam


def render_preview(glb: Path, out_path: Path, resolution: int, samples: int) -> dict:
    clear_scene()
    set_preview_scene(resolution, samples)
    obj = import_joined(glb, glb.stem)
    bounds = normalize_for_preview(obj)
    add_preview_stage()
    center = (
        (bounds["min"][0] + bounds["max"][0]) * 0.5,
        (bounds["min"][1] + bounds["max"][1]) * 0.5,
        (bounds["min"][2] + bounds["max"][2]) * 0.5,
    )
    cam = add_preview_camera(center, 3.0)
    bpy.context.scene.camera = cam
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)
    return bounds


def build_tree_variant(out_dir: Path) -> dict:
    clear_scene()
    obj = import_joined(TREE_SOURCE, "tree_compete_s3_green_leaf_brown_root")
    root_mat = make_principled("brown_root_and_trunk_pbr", (0.34, 0.20, 0.11, 1.0), 0.70)
    branch_mat = make_principled("olive_transition_branch_pbr", (0.28, 0.30, 0.14, 1.0), 0.68)
    leaf_mat = make_principled("deep_green_leaf_pbr", (0.13, 0.36, 0.18, 1.0), 0.62)
    split_stats = assign_by_height(obj, root_mat, leaf_mat, split_fraction=0.46, middle_material=branch_mat)
    apply_weighted_normals(obj)
    glb = out_dir / "tree_compete_s3_green_leaf_brown_root.glb"
    export_selected(obj, glb)
    preview = out_dir / "tree_compete_s3_green_leaf_brown_root_preview.png"
    preview_bounds = render_preview(glb, preview, 900, 64)
    return {
        "label": "tree_compete_s3_green_leaf_brown_root",
        "source_glb": str(TREE_SOURCE),
        "output_glb": str(glb),
        "preview": str(preview),
        "operation": "height-split recolor: lower/root geometry brown, upper/crown geometry green, middle band olive",
        "split_stats": split_stats,
        "preview_bounds": preview_bounds,
    }


def build_vine_variant(out_dir: Path) -> dict:
    clear_scene()
    obj = import_joined(VINE_SOURCE, "vine_stage5_upright_green_leaf_brown_base")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    obj.data.transform(Matrix.Scale(-1.0, 4, Vector((0.0, 0.0, 1.0))))
    obj.data.update()
    base_mat = make_principled("brown_pot_base_and_stems_pbr", (0.34, 0.19, 0.10, 1.0), 0.72)
    vine_mat = make_principled("green_vine_leaf_pbr", (0.16, 0.34, 0.13, 1.0), 0.66)
    leaf_mat = make_principled("fresh_green_leaf_tip_pbr", (0.21, 0.46, 0.18, 1.0), 0.64)
    split_stats = assign_by_height(obj, base_mat, leaf_mat, split_fraction=0.24, middle_material=vine_mat)
    apply_weighted_normals(obj)
    glb = out_dir / "vine_stage5_parthenocissus_warm_upright_green_leaf_brown_base.glb"
    export_selected(obj, glb)
    preview = out_dir / "vine_stage5_parthenocissus_warm_upright_green_leaf_brown_base_preview.png"
    preview_bounds = render_preview(glb, preview, 900, 64)
    return {
        "label": "vine_stage5_parthenocissus_warm_upright_green_leaf_brown_base",
        "source_glb": str(VINE_SOURCE),
        "same_geometry_as": str(
            REPO
            / "visuals/vine_stage5_guide_sweep_20260509"
            / "vine_stage5_tree_roots_square_steps8_tex2048_xformers/textured.glb"
        ),
        "output_glb": str(glb),
        "preview": str(preview),
        "operation": "use greener same-stage Parthenocissus PBR source, mirror local Z for the visual vertical flip that places the base at the bottom, then height-split recolor brown base / green upper growth",
        "split_stats": split_stats,
        "preview_bounds": preview_bounds,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    return parser.parse_args(argv)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = parse_args(argv)
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    variants = [build_tree_variant(out_dir), build_vine_variant(out_dir)]
    manifest = {
        "created_for": "R-SLG five-case hero botanical replacement variants",
        "notes": [
            "No source geometry is overwritten.",
            "The vine variant uses the greener same-stage Parthenocissus texture source because it shares the vine_d5_projected_compete stage-05 mesh with tree_roots_square.",
            "A 2026-05-10 orientation probe selected the local-Z mirror variant because it is the only tested orientation with the brown base down and green growth upward.",
            "The final hero script points to these derived GLBs for clearer publication rendering.",
        ],
        "variants": variants,
    }
    manifest_path = out_dir / "hero_botanical_variants_manifest_20260510.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(manifest_path)
    for item in variants:
        print(item["output_glb"])
        print(item["preview"])


if __name__ == "__main__":
    main()
