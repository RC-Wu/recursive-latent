#!/usr/bin/env python3
"""Render the five-asset R-SLG teaser with transparent alpha and zoom candidates.

Run with Blender:

  /Applications/Blender.app/Contents/MacOS/Blender -b \
    --python scripts/figures/hero_teaser_five_asset_transparent_render_20260512.py -- \
    --manifest scripts/figures/hero_teaser_five_asset_manifest_20260512.json \
    --out-dir visuals/hero_teaser_five_asset_transparent_20260512_v1 \
    --resolution 1400 --samples 64 --engine eevee

The script intentionally preserves RGBA alpha. White previews and the final
composition are produced by compose_hero_teaser_five_asset_20260512.py.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Iterable, Sequence

try:
    import bpy  # type: ignore
    from bpy_extras.object_utils import world_to_camera_view  # type: ignore
    from mathutils import Vector  # type: ignore

    HAS_BLENDER = True
except Exception:
    bpy = None
    world_to_camera_view = None
    Vector = None
    HAS_BLENDER = False


def safe_name(text: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in text).strip("_") or "case"


def quantile(values: Sequence[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    pos = max(0.0, min(1.0, q)) * (len(ordered) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - pos) + ordered[hi] * (pos - lo)


def mean_point(points: Sequence[Sequence[float]]) -> list[float]:
    if not points:
        return [0.0, 0.0, 0.0]
    return [sum(p[i] for p in points) / len(points) for i in range(3)]


def bounds(points: Sequence[Sequence[float]]) -> tuple[list[float], list[float], list[float]]:
    if not points:
        return [-1.0, -1.0, -1.0], [1.0, 1.0, 1.0], [0.0, 0.0, 0.0]
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    center = [(mins[i] + maxs[i]) * 0.5 for i in range(3)]
    return mins, maxs, center


def extent(points: Sequence[Sequence[float]]) -> float:
    mins, maxs, _ = bounds(points)
    return max(maxs[i] - mins[i] for i in range(3)) or 1.0


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_mesh(path: Path):
    before = set(bpy.data.objects)
    suffix = path.suffix.lower()
    if suffix == ".obj":
        if hasattr(bpy.ops.wm, "obj_import"):
            bpy.ops.wm.obj_import(filepath=str(path))
        else:
            bpy.ops.import_scene.obj(filepath=str(path))
    elif suffix in {".glb", ".gltf"}:
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


def normalize_object(obj, target_extent: float = 3.0, rotation_deg: Sequence[float] | None = None) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if rotation_deg:
        obj.rotation_euler = tuple(math.radians(float(v)) for v in rotation_deg)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    bpy.context.view_layer.update()
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    center = sum(corners, Vector()) / 8.0
    obj.location -= center
    bpy.context.view_layer.update()
    dims = obj.dimensions
    scale = target_extent / max(dims.x, dims.y, dims.z, 1e-6)
    obj.scale *= scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.context.view_layer.update()


def setup_world(resolution: int, samples: int, engine: str) -> None:
    scene = bpy.context.scene
    if engine == "cycles":
        scene.render.engine = "CYCLES"
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
        try:
            scene.cycles.max_bounces = 5
        except Exception:
            pass
    elif engine == "workbench":
        scene.render.engine = "BLENDER_WORKBENCH"
    else:
        for engine_name in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            try:
                scene.render.engine = engine_name
                break
            except TypeError:
                continue
        if hasattr(scene, "eevee"):
            try:
                scene.eevee.taa_render_samples = samples
            except Exception:
                pass
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = False
    world.color = (1.0, 1.0, 1.0)


def add_lighting(light_boost: float = 1.0) -> None:
    bpy.ops.object.light_add(type="AREA", location=(-3.2, -4.4, 5.2))
    key = bpy.context.object
    key.name = "hero_large_key_softbox"
    key.data.energy = 720 * light_boost
    key.data.size = 5.8
    bpy.ops.object.light_add(type="AREA", location=(3.6, 2.8, 3.4))
    fill = bpy.context.object
    fill.name = "hero_soft_fill"
    fill.data.energy = 210 * light_boost
    fill.data.size = 4.5
    bpy.ops.object.light_add(type="POINT", location=(0.0, -2.0, 4.6))
    rim = bpy.context.object
    rim.name = "hero_front_sparkle"
    rim.data.energy = 70 * light_boost


def set_bsdf_input(bsdf, name: str, value) -> None:
    if bsdf and name in bsdf.inputs:
        bsdf.inputs[name].default_value = value


def material(name: str, base: Sequence[float], roughness: float, metallic: float = 0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = tuple(base)
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    set_bsdf_input(bsdf, "Base Color", tuple(base))
    set_bsdf_input(bsdf, "Roughness", roughness)
    set_bsdf_input(bsdf, "Metallic", metallic)
    return mat


def assign_single_material(obj, mat, smooth: bool = True, weighted_normals: bool = True) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.material_index = 0
        poly.use_smooth = bool(smooth)
    if weighted_normals:
        mod = obj.modifiers.new("hero_weighted_normals", "WEIGHTED_NORMAL")
        mod.keep_sharp = True


def materialize_tree_canopy(obj) -> None:
    bark = material("hero_bark_warm_brown", (0.24, 0.13, 0.065, 1.0), 0.78, 0.0)
    leaf = material("hero_leaf_deep_green", (0.035, 0.34, 0.055, 1.0), 0.58, 0.0)
    obj.data.materials.clear()
    obj.data.materials.append(bark)
    obj.data.materials.append(leaf)
    areas = [poly.area for poly in obj.data.polygons]
    centers = [obj.matrix_world @ poly.center for poly in obj.data.polygons]
    radii = [math.hypot(c.x, c.y) for c in centers]
    area_cut = quantile(areas, 0.62)
    radial_cut = quantile(radii, 0.38)
    leaf_count = 0
    fallback_cut = quantile(areas, 0.50)
    for poly, center, radius in zip(obj.data.polygons, centers, radii):
        broad_face = poly.area >= area_cut
        outer_face = radius >= radial_cut
        up_face = abs(poly.normal.z) > 0.34
        is_leaf = outer_face and (broad_face or (up_face and poly.area >= fallback_cut))
        poly.material_index = 1 if is_leaf else 0
        poly.use_smooth = not is_leaf
        leaf_count += int(is_leaf)
    if leaf_count < max(24, len(obj.data.polygons) * 0.04):
        for poly, radius in zip(obj.data.polygons, radii):
            if radius >= radial_cut and poly.area >= fallback_cut:
                poly.material_index = 1
                poly.use_smooth = False
    mod = obj.modifiers.new("tree_bark_weighted_normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True


def prepare_materials(obj, mode: str) -> None:
    if mode == "bismuth":
        assign_single_material(obj, material("hero_bismuth_iridescent_lilac", (0.62, 0.52, 0.78, 1.0), 0.30, 0.62), True)
    elif mode == "pyrite":
        assign_single_material(obj, material("hero_pyrite_warm_gold", (0.95, 0.69, 0.26, 1.0), 0.32, 0.82), False, True)
    elif mode == "coral":
        assign_single_material(obj, material("hero_coral_smoothed_red", (0.72, 0.26, 0.16, 1.0), 0.64, 0.0), True, True)
        smooth = obj.modifiers.new("hero_coral_surface_relax", "SMOOTH")
        smooth.factor = 0.38
        smooth.iterations = 4
    elif mode == "bamboo":
        assign_single_material(obj, material("hero_bamboo_bark_warm", (0.48, 0.31, 0.16, 1.0), 0.70, 0.0), True, True)
    elif mode == "tree_canopy":
        materialize_tree_canopy(obj)
    elif mode == "preserve":
        for poly in obj.data.polygons:
            poly.use_smooth = True
        mod = obj.modifiers.new("hero_preserve_weighted_normals", "WEIGHTED_NORMAL")
        mod.keep_sharp = True
    else:
        assign_single_material(obj, material("hero_neutral_clay", (0.54, 0.52, 0.47, 1.0), 0.72, 0.0), True)


def world_vertices(obj, max_vertices: int = 90000) -> list[tuple[float, float, float]]:
    matrix = obj.matrix_world
    vertices = obj.data.vertices
    if len(vertices) <= max_vertices:
        return [tuple(matrix @ vertex.co) for vertex in vertices]
    step = max(1, len(vertices) // max_vertices)
    sampled = [vertices[idx] for idx in range(0, len(vertices), step)]
    if sampled[-1].index != vertices[-1].index:
        sampled.append(vertices[-1])
    return [tuple(matrix @ vertex.co) for vertex in sampled[:max_vertices]]


def camera_direction(raw: Sequence[float]) -> "Vector":
    return Vector((float(raw[0]), float(raw[1]), float(raw[2]))).normalized()


def add_camera(target: Sequence[float], ortho_scale: float, direction_raw: Sequence[float]):
    target_v = Vector(target)
    direction = camera_direction(direction_raw)
    loc = target_v + direction * 7.2
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.rotation_euler = (target_v - loc).to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho_scale
    bpy.context.scene.camera = cam
    return cam


def projected_rect(parent_camera, target: Sequence[float], child_scale: float, resolution: int) -> list[int]:
    scene = bpy.context.scene
    target_v = Vector(target)
    quat = parent_camera.matrix_world.to_quaternion()
    right = quat @ Vector((1.0, 0.0, 0.0))
    up = quat @ Vector((0.0, 1.0, 0.0))
    half = child_scale * 0.5
    corners = [
        target_v - right * half - up * half,
        target_v + right * half - up * half,
        target_v + right * half + up * half,
        target_v - right * half + up * half,
    ]
    coords = [world_to_camera_view(scene, parent_camera, corner) for corner in corners]
    xs = [min(max(coord.x, 0.0), 1.0) * resolution for coord in coords]
    ys = [(1.0 - min(max(coord.y, 0.0), 1.0)) * resolution for coord in coords]
    left = int(max(0, min(xs)))
    top = int(max(0, min(ys)))
    right_px = int(min(resolution, max(xs)))
    bottom = int(min(resolution, max(ys)))
    return [left, top, max(left + 3, right_px), max(top + 3, bottom)]


def choose_zoom_targets(points: Sequence[Sequence[float]], zoom_count: int) -> list[list[float]]:
    mins, maxs, center = bounds(points)
    span = extent(points)
    radii = [math.hypot(p[0] - center[0], p[1] - center[1]) for p in points]
    r_gate = quantile(radii, 0.54)
    z_low = quantile([p[2] for p in points], 0.18)
    filtered = [p for p, r in zip(points, radii) if r >= r_gate and p[2] >= z_low]
    if len(filtered) < 20:
        filtered = list(points)

    targets: list[list[float]] = []
    sector_angles = [-2.45, -1.05, 0.25, 1.55, 2.72]
    for angle in sector_angles:
        scored = []
        for p in filtered:
            theta = math.atan2(p[1] - center[1], p[0] - center[0])
            delta = abs(math.atan2(math.sin(theta - angle), math.cos(theta - angle)))
            radius = math.hypot(p[0] - center[0], p[1] - center[1])
            z_norm = (p[2] - mins[2]) / max(maxs[2] - mins[2], 1e-6)
            score = -delta + 0.33 * radius / max(span, 1e-6) + 0.24 * z_norm
            scored.append((score, p))
        chosen = [p for _, p in sorted(scored, key=lambda item: item[0], reverse=True)[: max(8, min(36, len(scored)))]]
        target = mean_point(chosen)
        if all(math.dist(target, prev) > span * 0.08 for prev in targets):
            targets.append(target)

    while len(targets) < zoom_count:
        q = 0.62 + 0.07 * len(targets)
        z_gate = quantile([p[2] for p in points], min(q, 0.94))
        upper = [p for p in points if p[2] >= z_gate] or list(points)
        targets.append(mean_point(upper[: max(1, min(30, len(upper)))]))
    return targets[:zoom_count]


def render_to(path: Path, camera_obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.camera = camera_obj
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def render_case(case: dict, args: argparse.Namespace) -> dict:
    clear_scene()
    setup_world(args.resolution, args.samples, args.engine)
    add_lighting(float(case.get("light_boost", 1.0)))
    mesh = Path(case["mesh"])
    obj = import_mesh(mesh)
    normalize_object(obj, float(case.get("target_extent", 3.0)), case.get("rotation_deg"))
    prepare_materials(obj, case.get("material_mode", "neutral"))
    vertices = world_vertices(obj)
    _, _, center = bounds(vertices)
    overview_scale = extent(vertices) * float(case.get("overview_scale_factor", 1.18))
    direction = case.get("camera_direction", [4.2, -5.2, 3.0])
    zoom_count = int(case.get("zoom_count", args.zoom_count))
    target_points = case.get("fixed_targets") or choose_zoom_targets(vertices, zoom_count)
    zoom_factors = case.get("zoom_factors") or [0.36, 0.28, 0.22, 0.17, 0.125]

    safe = safe_name(case["id"])
    case_dir = args.out_dir / safe
    overview_path = case_dir / "overview_rgba.png"
    overview_camera = add_camera(center, overview_scale, direction)
    render_to(overview_path, overview_camera)

    plan = {
        "id": case["id"],
        "label": case.get("label", case["id"]),
        "mesh": str(mesh),
        "case_dir": str(case_dir),
        "material_mode": case.get("material_mode", "neutral"),
        "overview": {
            "path": str(overview_path),
            "target": [round(v, 6) for v in center],
            "ortho_scale": round(overview_scale, 6),
            "resolution": [args.resolution, args.resolution],
        },
        "zooms": [],
    }
    for idx, target in enumerate(target_points[:zoom_count], 1):
        factor = float(zoom_factors[min(idx - 1, len(zoom_factors) - 1)])
        scale = overview_scale * factor
        zoom_path = case_dir / f"zoom_{idx:02d}_rgba.png"
        zoom_camera = add_camera(target, scale, direction)
        render_to(zoom_path, zoom_camera)
        plan["zooms"].append(
            {
                "id": f"zoom_{idx:02d}",
                "path": str(zoom_path),
                "target": [round(float(v), 6) for v in target],
                "ortho_scale": round(scale, 6),
                "callout_rect": projected_rect(overview_camera, target, scale, args.resolution),
            }
        )
    if case.get("selected_zoom"):
        plan["selected_zoom"] = case["selected_zoom"]
    return plan


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--resolution", type=int, default=1400)
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--zoom-count", type=int, default=5)
    parser.add_argument("--engine", choices=["eevee", "cycles", "workbench"], default="eevee")
    return parser.parse_args(argv)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = parse_args(argv)
    if not HAS_BLENDER:
        raise SystemExit("This renderer must be run with Blender.")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    cases = payload["cases"] if isinstance(payload, dict) else payload
    plan = {
        "manifest": str(args.manifest),
        "out_dir": str(args.out_dir),
        "render_config": {
            "resolution": args.resolution,
            "samples": args.samples,
            "engine": args.engine,
            "transparent_alpha": True,
            "zoom_candidates_per_asset": args.zoom_count,
        },
        "cases": [],
    }
    for case in cases:
        print(f"[hero-render] {case['id']} <- {case['mesh']}")
        plan["cases"].append(render_case(case, args))
    plan_path = args.out_dir / "hero_teaser_render_plan.json"
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(f"[hero-render] wrote {plan_path}")


if __name__ == "__main__":
    main()
