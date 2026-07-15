#!/usr/bin/env python3
"""Render the upright 4x4 traditional-vs-PS-RSLE comparison figure.

Run through Blender:

  blender -b --python scripts/figures/render_main_experiment_upright_4x4_zoom_20260512.py --
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Sequence

try:
    import bpy  # type: ignore
    from bpy_extras.object_utils import world_to_camera_view  # type: ignore
    from mathutils import Matrix, Vector  # type: ignore

    HAS_BLENDER = True
except Exception:
    bpy = None
    world_to_camera_view = None
    Matrix = None
    Vector = None
    HAS_BLENDER = False


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
WHITE = (255, 255, 255)
INK = (24, 24, 24)
CALLOUT = (124, 124, 124)


CASES = [
    {
        "row": "Space colonization",
        "traditional": {
            "label": "SC_baseline_tree_canopy",
            "mesh": ROOT / "visuals/traditional_baseline_texture_20260509/sc_tree_canopy_steps6_tex1024_xformers/textured.glb",
            "material_mode": "preserve",
            "rotation_deg": [90, 0, 0],
            "target_quantiles": [0.54, 0.88],
            "zoom_divisor": 4.7,
        },
        "ours": {
            "label": "SC_ours_V32_balanced_canopy_D",
            "mesh": ROOT / "visuals/strict_visual_matched_texture_V32_sc_tree_canopy_veil_naturalization_20260511/V32_sc_tree_balanced_canopy_D_steps8_tex2048_seed20292515_xformers/textured.glb",
            "material_mode": "preserve",
            "rotation_deg": [90, 0, 0],
            "target_quantiles": [0.50, 0.86],
            "zoom_divisor": 4.7,
        },
    },
    {
        "row": "L-system",
        "traditional": {
            "label": "LSystem_baseline_OBJ_neutral_upright",
            "mesh": ROOT / "results/traditional_baselines/run_20260507_0300/lsystem_branch.obj",
            "material_mode": "neutral",
            "target_quantiles": [0.44, 0.72],
            "zoom_divisor": 5.2,
        },
        "ours": {
            "label": "LSystem_ours_V67_tapered_dense_B",
            "mesh": ROOT / "results/strict_visual_matched_texture_V67_lsystem_branch_same_scaffold_tapered_twig_BC_20260512_remote/V67_lsys_branch_tapered_dense_B_steps8_tex2048_seed20260613_xformers/textured.glb",
            "material_mode": "preserve",
            "rotation_deg": [90, 0, 0],
            "target_quantiles": [0.44, 0.72],
            "zoom_divisor": 5.2,
        },
    },
    {
        "row": "DLA",
        "traditional": {
            "label": "DLA_baseline_cluster",
            "mesh": ROOT / "visuals/traditional_baseline_texture_20260509/dla_cluster_steps6_tex1024_xformers/textured.glb",
            "material_mode": "preserve",
            "target_quantiles": [0.46, 0.80],
            "zoom_divisor": 4.8,
        },
        "ours": {
            "label": "DLA_ours_V8_lace_reef_coral_A",
            "mesh": ROOT / "visuals/strict_visual_matched_texture_v8_frontier_refine_20260510/v8_dla_coral_lace_reef_branching_a_steps8_tex2048_seed20260811_xformers/textured.glb",
            "material_mode": "preserve",
            "target_quantiles": [0.46, 0.82],
            "zoom_divisor": 4.8,
        },
    },
    {
        "row": "IFS",
        "traditional": {
            "label": "IFS_baseline_matched_branch_tree",
            "mesh": ROOT / "visuals/traditional_baseline_texture_matched_guide_20260509/ifs_branch_tree_matched_steps6_tex1024_xformers/textured.glb",
            "material_mode": "preserve",
            "rotation_deg": [-90, 0, 0],
            "target_quantiles": [0.50, 0.82],
            "zoom_divisor": 4.9,
        },
        "ours": {
            "label": "IFS_ours_V21_branch_tree_natural_bark",
            "mesh": ROOT / "visuals/strict_visual_matched_texture_V21_ifs_transform_natural_tex4096_seed20292500_20260510/V21_ifs_branch_tree_d6_natural_bark_steps8_tex4096_seed20294601_xformers/textured.glb",
            "material_mode": "preserve",
            "rotation_deg": [-90, 0, 0],
            "target_quantiles": [0.46, 0.78],
            "zoom_divisor": 4.9,
        },
    },
]


IFS_OURS_VARIANTS = {
    "current_v21": {
        "row_label": "IFS",
        "ours": {
            "label": "IFS_ours_V21_branch_tree_natural_bark",
            "mesh": ROOT / "visuals/strict_visual_matched_texture_V21_ifs_transform_natural_tex4096_seed20292500_20260510/V21_ifs_branch_tree_d6_natural_bark_steps8_tex4096_seed20294601_xformers/textured.glb",
            "material_mode": "preserve",
            "rotation_deg": [-90, 0, 0],
            "target_quantiles": [0.46, 0.78],
            "zoom_divisor": 4.9,
        },
        "paper_note": "legacy V21 branch-tree candidate; visually weak recursion in the 4x4 matrix",
    },
    "v23_true_ifs": {
        "row_label": "IFS",
        "ours": {
            "label": "IFS_ours_V23_fractal_tree_branch_copy",
            "mesh": ROOT / "visuals/strict_visual_matched_texture_V23_all_family_seed20260513_20260510/V23_ifs_fractal_tree_d5_branch_copy_steps8_tex2048_seed20262827_xformers/textured.glb",
            "material_mode": "preserve",
            "rotation_deg": [-90, 0, 0],
            "target_quantiles": [0.38, 0.74],
            "zoom_divisor": 5.1,
        },
        "paper_note": "mechanism-matched IFS branch-copy candidate",
    },
    "v59_lowfrag_branch": {
        "row_label": "IFS",
        "ours": {
            "label": "RecursiveBranch_ours_V59_smooth_short_bough_lowfrag_B",
            "mesh": ROOT / "results/strict_visual_matched_texture_V59_lsystem_branch_smooth_short_bough_yfork_BD_smoothpost_20260511/V59_lsys_branch_smooth_short_bough_lowfrag_B_smoothpost/textured.glb",
            "material_mode": "preserve",
            "rotation_deg": [90, 0, 0],
            "target_quantiles": [0.34, 0.82],
            "zoom_divisor": 5.0,
        },
        "paper_note": "visual recursive-branch replacement; generated by the L-system branch grammar, not a formal IFS operator",
    },
    "v59_compact_branch": {
        "row_label": "IFS",
        "ours": {
            "label": "RecursiveBranch_ours_V59_smooth_short_bough_compact_D",
            "mesh": ROOT / "results/strict_visual_matched_texture_V59_lsystem_branch_smooth_short_bough_yfork_BD_smoothpost_20260511/V59_lsys_branch_smooth_short_bough_compact_D_smoothpost/textured.glb",
            "material_mode": "preserve",
            "rotation_deg": [90, 0, 0],
            "target_quantiles": [0.34, 0.82],
            "zoom_divisor": 5.0,
        },
        "paper_note": "visual recursive-branch replacement; generated by the L-system branch grammar, not a formal IFS operator",
    },
    "v59_dense_obj": {
        "row_label": "IFS",
        "ours": {
            "label": "RecursiveBranch_ours_V59_dense_C_OBJ",
            "mesh": ROOT / "results/strict_visual_matched_cases_V59_lsystem_branch_smooth_short_bough_yfork_20260511_dryrun/V59_lsys_branch_smooth_short_bough_dense_C/V59_lsys_branch_smooth_short_bough_dense_C.obj",
            "material_mode": "neutral",
            "rotation_deg": [90, 0, 0],
            "target_quantiles": [0.34, 0.82],
            "zoom_divisor": 5.0,
        },
        "paper_note": "visual recursive-branch replacement from the denser pre-export OBJ; generated by the L-system branch grammar, not a formal IFS operator",
    },
    "v63_distributed_dense_B": {
        "row_label": "IFS",
        "ours": {
            "label": "RecursiveBranch_ours_V63_distributed_dense_B",
            "mesh": ROOT / "results/strict_visual_matched_texture_V63_lsystem_branch_distributed_recursive_bough_BC_20260512_remote/V63_lsys_branch_distributed_dense_B_steps8_tex2048_seed20323513_xformers/textured.glb",
            "material_mode": "preserve",
            "align_major_axis_to_z": True,
            "target_quantiles": [0.24, 0.78],
            "zoom_divisor": 4.3,
        },
        "paper_note": "visual recursive-branch replacement with distributed side-branch depth/density; generated by the L-system branch grammar, not a formal IFS operator",
    },
    "v63_balanced_fan_C": {
        "row_label": "IFS",
        "ours": {
            "label": "RecursiveBranch_ours_V63_balanced_fan_C",
            "mesh": ROOT / "results/strict_visual_matched_texture_V63_lsystem_branch_distributed_recursive_bough_BC_20260512_remote/V63_lsys_branch_balanced_fan_C_steps8_tex2048_seed20323514_xformers/textured.glb",
            "material_mode": "preserve",
            "align_major_axis_to_z": True,
            "post_rotation_deg": [180, 0, 0],
            "target_quantiles": [0.24, 0.78],
            "zoom_divisor": 4.3,
        },
        "paper_note": "visual recursive-branch replacement with distributed side-branch depth/density; generated by the L-system branch grammar, not a formal IFS operator",
    },
}


def apply_ifs_ours_variant(variant: str) -> str:
    selected = IFS_OURS_VARIANTS[variant]
    for row in CASES:
        if row["row"] == "IFS":
            row["row"] = selected["row_label"]
            row["ours"] = dict(selected["ours"])
            return selected["paper_note"]
    raise RuntimeError("IFS row not found in CASES")


def safe_label(label: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in label).strip("_") or "case"


def quantile(values: Sequence[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    pos = min(max(q, 0.0), 1.0) * (len(ordered) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - pos) + ordered[hi] * (pos - lo)


def bounds(points: Sequence[Sequence[float]]) -> tuple[Vector, Vector, Vector]:
    mins = Vector((min(p[i] for p in points) for i in range(3)))
    maxs = Vector((max(p[i] for p in points) for i in range(3)))
    center = (mins + maxs) * 0.5
    return mins, maxs, center


def extent(points: Sequence[Sequence[float]]) -> float:
    mins, maxs, _ = bounds(points)
    dims = maxs - mins
    return max(dims.x, dims.y, dims.z, 1e-6)


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
    obj.name = path.stem
    return obj


def principal_axis(points: Sequence[Vector]) -> Vector:
    if not points:
        return Vector((0.0, 0.0, 1.0))
    mean = sum(points, Vector()) / len(points)
    centered = [point - mean for point in points[:: max(1, len(points) // 50000)]]
    axis = Vector((1.0, 0.0, 0.0))
    for _ in range(18):
        x = sum(vec.x * (vec.dot(axis)) for vec in centered)
        y = sum(vec.y * (vec.dot(axis)) for vec in centered)
        z = sum(vec.z * (vec.dot(axis)) for vec in centered)
        nxt = Vector((x, y, z))
        if nxt.length < 1e-8:
            break
        axis = nxt.normalized()
    if axis.z < 0:
        axis.negate()
    return axis.normalized()


def align_major_axis_to_z(obj) -> None:
    obj.rotation_mode = "XYZ"
    points = [vertex.co.copy() for vertex in obj.data.vertices]
    axis = principal_axis(points)
    if abs(axis.dot(Vector((0.0, 0.0, 1.0)))) > 0.985:
        return
    quat = axis.rotation_difference(Vector((0.0, 0.0, 1.0)))
    obj.rotation_euler = quat.to_euler()
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)


def normalize_object(
    obj,
    target_extent: float = 3.0,
    rotation_deg: Sequence[float] | None = None,
    post_rotation_deg: Sequence[float] | None = None,
    align_to_z: bool = False,
) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    obj.rotation_mode = "XYZ"
    if rotation_deg:
        obj.rotation_euler = tuple(math.radians(float(value)) for value in rotation_deg)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    if align_to_z:
        align_major_axis_to_z(obj)
    if post_rotation_deg:
        obj.rotation_euler = tuple(math.radians(float(value)) for value in post_rotation_deg)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    bpy.context.view_layer.update()
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    center = sum(corners, Vector()) / 8.0
    obj.location -= center
    bpy.context.view_layer.update()
    scale = target_extent / max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z, 1e-6)
    obj.scale *= scale
    bpy.context.view_layer.update()


def setup_world(resolution: int, samples: int) -> None:
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = False
    world.color = (1.0, 1.0, 1.0)


def add_lighting() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-2.8, -5.0, 5.5))
    key = bpy.context.object
    key.name = "upright_large_softbox"
    key.data.energy = 520
    key.data.size = 5.8
    bpy.ops.object.light_add(type="AREA", location=(3.2, 2.6, 3.5))
    fill = bpy.context.object
    fill.name = "upright_soft_fill"
    fill.data.energy = 95
    fill.data.size = 4.2


def make_neutral_material():
    mat = bpy.data.materials.new("upright_neutral_matte")
    mat.diffuse_color = (0.50, 0.54, 0.48, 1.0)
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (0.50, 0.54, 0.48, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.72
    return mat


def prepare_materials(obj, mode: str) -> None:
    if mode != "preserve" or not obj.data.materials:
        obj.data.materials.clear()
        obj.data.materials.append(make_neutral_material())
    for poly in obj.data.polygons:
        poly.use_smooth = True
    mod = obj.modifiers.new("upright_weighted_normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True


def world_vertices(obj, max_vertices: int = 90000) -> list[Vector]:
    matrix = obj.matrix_world
    vertices = obj.data.vertices
    if len(vertices) <= max_vertices:
        return [matrix @ vertex.co for vertex in vertices]
    step = max(1, len(vertices) // max_vertices)
    sampled = [vertices[idx] for idx in range(0, len(vertices), step)]
    return [matrix @ vertex.co for vertex in sampled[:max_vertices]]


def choose_recursive_target(vertices: Sequence[Vector], quantiles: Sequence[float]) -> Vector:
    zs = [v.z for v in vertices]
    z_lo = quantile(zs, quantiles[0])
    z_hi = quantile(zs, quantiles[1])
    mids = [v for v in vertices if z_lo <= v.z <= z_hi] or list(vertices)
    # Pick a dense recursive region rather than the single highest terminal.
    bin_size = extent(vertices) / 9.0
    bins: dict[tuple[int, int, int], list[Vector]] = {}
    for v in mids:
        key = (int(math.floor(v.x / bin_size)), int(math.floor(v.y / bin_size)), int(math.floor(v.z / bin_size)))
        bins.setdefault(key, []).append(v)
    _, cluster = max(bins.items(), key=lambda item: (len(item[1]), sum(v.z for v in item[1]) / len(item[1])))
    center = sum(cluster, Vector()) / len(cluster)
    # Blend with the local high-percentile point in the same cluster so the zoom
    # lands on visible branch/tip detail rather than the interior centroid.
    local = sorted(cluster, key=lambda v: v.z + 0.25 * (abs(v.x - center.x) + abs(v.y - center.y)), reverse=True)
    top = local[: max(4, min(24, len(local)))]
    return sum(top, Vector()) / len(top)


def camera_pose(target: Vector, scale: float):
    # Front-ish orthographic view with global Z locked to screen-up.
    direction = Vector((0.0, -1.0, 0.22)).normalized()
    loc = target + direction * 7.5
    forward = (target - loc).normalized()
    world_up = Vector((0.0, 0.0, 1.0))
    right = forward.cross(world_up).normalized()
    up = right.cross(forward).normalized()
    rot = Matrix(((right.x, up.x, -forward.x), (right.y, up.y, -forward.y), (right.z, up.z, -forward.z))).to_euler()
    bpy.ops.object.camera_add(location=loc, rotation=rot)
    cam = bpy.context.object
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = scale
    bpy.context.scene.camera = cam
    return cam


def composite_white(path: Path) -> None:
    try:
        from PIL import Image
    except Exception:
        return

    src = Image.open(path).convert("RGBA")
    base = Image.new("RGBA", src.size, WHITE + (255,))
    base.alpha_composite(src)
    base.convert("RGB").save(path)


def render_to(path: Path, camera) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.camera = camera
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    composite_white(path)


def projected_rect(camera, target: Vector, child_scale: float, resolution: int) -> tuple[int, int, int, int]:
    scene = bpy.context.scene
    quat = camera.matrix_world.to_quaternion()
    right = quat @ Vector((1.0, 0.0, 0.0))
    up = quat @ Vector((0.0, 1.0, 0.0))
    half = child_scale * 0.5
    corners = [
        target - right * half - up * half,
        target + right * half - up * half,
        target + right * half + up * half,
        target - right * half + up * half,
    ]
    coords = [world_to_camera_view(scene, camera, corner) for corner in corners]
    xs = [min(max(coord.x, 0.0), 1.0) * resolution for coord in coords]
    ys = [(1.0 - min(max(coord.y, 0.0), 1.0)) * resolution for coord in coords]
    left = int(max(0, min(xs)))
    top = int(max(0, min(ys)))
    right_px = int(min(resolution, max(xs)))
    bottom = int(min(resolution, max(ys)))
    return left, top, max(left + 2, right_px), max(top + 2, bottom)


def draw_gray_box(raw_path: Path, out_path: Path, rect: tuple[int, int, int, int]) -> None:
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return

    im = Image.open(raw_path).convert("RGB")
    draw = ImageDraw.Draw(im)
    width = max(3, im.width // 360)
    draw.rectangle(rect, outline=CALLOUT, width=width)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path)


def render_case(case: dict, out_dir: Path, resolution: int, samples: int) -> dict:
    clear_scene()
    setup_world(resolution, samples)
    obj = import_mesh(Path(case["mesh"]))
    normalize_object(
        obj,
        rotation_deg=case.get("rotation_deg"),
        post_rotation_deg=case.get("post_rotation_deg"),
        align_to_z=bool(case.get("align_major_axis_to_z", False)),
    )
    prepare_materials(obj, case["material_mode"])
    add_lighting()
    vertices = world_vertices(obj)
    _, _, center = bounds(vertices)
    overview_scale = extent(vertices) * 1.18
    zoom_target = choose_recursive_target(vertices, case["target_quantiles"])
    zoom_scale = overview_scale / float(case["zoom_divisor"])
    case_dir = out_dir / safe_label(case["label"])
    overview_raw = case_dir / "overview_raw.png"
    overview_box = case_dir / "overview_gray_box.png"
    zoom = case_dir / "zoom.png"
    overview_cam = camera_pose(center, overview_scale)
    render_to(overview_raw, overview_cam)
    zoom_cam = camera_pose(zoom_target, zoom_scale)
    render_to(zoom, zoom_cam)
    rect = projected_rect(overview_cam, zoom_target, zoom_scale, resolution)
    draw_gray_box(overview_raw, overview_box, rect)
    return {
        "label": case["label"],
        "mesh": str(case["mesh"]),
        "material_mode": case["material_mode"],
        "overview_raw": str(overview_raw),
        "overview_gray_box": str(overview_box),
        "zoom": str(zoom),
        "overview_target": list(center),
        "zoom_target": list(zoom_target),
        "overview_scale": overview_scale,
        "zoom_scale": zoom_scale,
        "callout_rect": list(rect),
        "target_quantiles": case["target_quantiles"],
        "zoom_divisor": case["zoom_divisor"],
    }


def fit_square(path: Path, size: int):
    from PIL import Image

    image = Image.open(path).convert("RGB")
    image.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (size, size), WHITE)
    canvas.paste(image, ((size - image.width) // 2, (size - image.height) // 2))
    return canvas


def times_font(size: int):
    from PIL import ImageFont

    for path in [
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
        "/Library/Fonts/Times New Roman Bold.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/Library/Fonts/Times New Roman.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def compose_figure(rows: list[dict], out_path: Path, panel_size: int) -> None:
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return

    label_w = int(panel_size * 0.88)
    gap = int(panel_size * 0.075)
    row_gap = int(panel_size * 0.08)
    margin = int(panel_size * 0.06)
    width = margin * 2 + label_w + gap + 4 * panel_size + 3 * gap
    height = margin * 2 + len(rows) * panel_size + (len(rows) - 1) * row_gap
    canvas = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    font = times_font(max(28, panel_size // 16))

    y = margin
    for row in rows:
        label = row["row"]
        bbox = draw.textbbox((0, 0), label, font=font)
        draw.text((margin, y + panel_size * 0.5 - (bbox[3] - bbox[1]) * 0.5), label, fill=INK, font=font)
        panels = [
            row["traditional"]["overview_gray_box"],
            row["traditional"]["zoom"],
            row["ours"]["overview_gray_box"],
            row["ours"]["zoom"],
        ]
        x = margin + label_w + gap
        for panel in panels:
            canvas.paste(fit_square(Path(panel), panel_size), (x, y))
            x += panel_size + gap
        y += panel_size + row_gap
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=ROOT / "visuals/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512")
    parser.add_argument("--figure-out", type=Path, default=ROOT / "paper_siga/figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.png")
    parser.add_argument("--paper-manifest-out", type=Path, default=ROOT / "paper_siga/figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.json")
    parser.add_argument("--resolution", type=int, default=1600)
    parser.add_argument("--samples", type=int, default=96)
    parser.add_argument("--panel-size", type=int, default=560)
    parser.add_argument(
        "--ifs-ours",
        choices=sorted(IFS_OURS_VARIANTS),
        default="v63_balanced_fan_C",
        help="Candidate used in the IFS-row PS-RSLE/ours column for QA and final figure generation.",
    )
    return parser.parse_args(argv)


def main() -> None:
    if not HAS_BLENDER:
        raise SystemExit("Run this script through Blender, not plain python.")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = parse_args(argv)
    ifs_note = apply_ifs_ours_variant(args.ifs_ours)
    rendered_rows = []
    for row in CASES:
        rendered_rows.append(
            {
                "row": row["row"],
                "traditional": render_case(row["traditional"], args.out_dir, args.resolution, args.samples),
                "ours": render_case(row["ours"], args.out_dir, args.resolution, args.samples),
            }
        )
    compose_figure(rendered_rows, args.figure_out, args.panel_size)
    manifest = {
        "requirements": {
            "layout": "4x4",
            "only_text": "left row labels in Times New Roman",
            "zoom_levels": 1,
            "callout_color": "gray",
            "callout_labels": False,
            "upright_camera": True,
        },
        "ifs_ours_variant": args.ifs_ours,
        "ifs_ours_note": ifs_note,
        "rows": rendered_rows,
        "figure": str(args.figure_out),
    }
    args.paper_manifest_out.parent.mkdir(parents=True, exist_ok=True)
    args.paper_manifest_out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(args.figure_out)
    print(args.paper_manifest_out)


if __name__ == "__main__":
    main()
