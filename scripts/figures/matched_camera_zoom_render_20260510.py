#!/usr/bin/env python3
"""Strict matched overview and camera-zoom renderer for square white figures.

Run with normal Python for ``--plan-only`` validation, or through Blender for
real orthographic zoom renders:

blender -b --python scripts/figures/matched_camera_zoom_render_20260510.py -- ...
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
    from mathutils import Vector  # type: ignore

    HAS_BLENDER = True
except Exception:
    bpy = None
    world_to_camera_view = None
    Vector = None
    HAS_BLENDER = False


WHITE = (255, 255, 255)
INK = (24, 26, 28)
MUTED = (88, 92, 96)
ACCENTS = [(196, 60, 52), (45, 112, 185), (40, 138, 86), (155, 88, 178)]


def _safe_label(label: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in label).strip("_") or "case"


def _quantile(values: Sequence[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    pos = min(max(q, 0.0), 1.0) * (len(ordered) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - pos) + ordered[hi] * (pos - lo)


def _mean(points: Sequence[Sequence[float]]) -> list[float]:
    if not points:
        return [0.0, 0.0, 0.0]
    return [sum(point[idx] for point in points) / len(points) for idx in range(3)]


def _bounds(vertices: Sequence[Sequence[float]]) -> tuple[list[float], list[float], list[float]]:
    if not vertices:
        return [0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [0.0, 0.0, 0.0]
    mins = [min(point[idx] for point in vertices) for idx in range(3)]
    maxs = [max(point[idx] for point in vertices) for idx in range(3)]
    center = [(mins[idx] + maxs[idx]) * 0.5 for idx in range(3)]
    return mins, maxs, center


def _extent(vertices: Sequence[Sequence[float]]) -> float:
    mins, maxs, _ = _bounds(vertices)
    return max(maxs[idx] - mins[idx] for idx in range(3)) or 1.0


def normalize_points(points: Sequence[Sequence[float]], target_extent: float = 3.0) -> list[tuple[float, float, float]]:
    if not points:
        return []
    extent = _extent(points)
    _, _, center = _bounds(points)
    scale = target_extent / max(extent, 1e-6)
    return [
        tuple((point[idx] - center[idx]) * scale for idx in range(3))
        for point in points
    ]


def normalize_points_like(
    points: Sequence[Sequence[float]],
    reference_points: Sequence[Sequence[float]],
    target_extent: float = 3.0,
) -> list[tuple[float, float, float]]:
    """Normalize detail points with the same center/scale as a reference mesh."""
    if not points:
        return []
    reference = reference_points or points
    extent = _extent(reference)
    _, _, center = _bounds(reference)
    scale = target_extent / max(extent, 1e-6)
    return [
        tuple((point[idx] - center[idx]) * scale for idx in range(3))
        for point in points
    ]


def parse_obj_vertices(path: Path) -> list[tuple[float, float, float]]:
    vertices: list[tuple[float, float, float]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
    return vertices


def load_plan_vertices(mesh: Path) -> list[tuple[float, float, float]]:
    if mesh.suffix.lower() == ".obj" and mesh.exists():
        return parse_obj_vertices(mesh)
    return []


def choose_detail_target(
    vertices: Sequence[Sequence[float]],
    level: int,
    previous_target: Sequence[float] | None = None,
) -> list[float]:
    """Pick an informative upper/off-axis target, avoiding central trunks if possible."""
    if not vertices:
        return [0.0, 0.0, 0.0]
    zs = [point[2] for point in vertices]
    lower_z = _quantile(zs, 0.35)
    lower_body = [point for point in vertices if point[2] <= lower_z]
    stem_center = _mean(lower_body or vertices)
    radial = [math.hypot(point[0] - stem_center[0], point[1] - stem_center[1]) for point in vertices]
    z_gate = _quantile(zs, min(0.56 + 0.14 * level, 0.86))
    r_gate = _quantile(radial, 0.56)
    candidates = [
        point
        for point, radius in zip(vertices, radial)
        if point[2] >= z_gate and radius >= r_gate
    ]
    if previous_target is not None:
        span = _extent(vertices) / (2.2 + level)
        nested = [
            point
            for point in candidates
            if math.dist(point, previous_target) <= span and point[2] >= previous_target[2] - 0.08 * _extent(vertices)
        ]
        if nested:
            candidates = nested
    if not candidates:
        candidates = [point for point in vertices if point[2] >= z_gate]
    if not candidates:
        candidates = list(vertices)

    def score(point: Sequence[float]) -> float:
        r = math.hypot(point[0] - stem_center[0], point[1] - stem_center[1])
        nested_bonus = 0.0
        if previous_target is not None:
            nested_bonus = -0.15 * math.dist(point, previous_target) / max(_extent(vertices), 1e-6)
        return 1.4 * point[2] + 0.9 * r + nested_bonus

    top = sorted(candidates, key=score, reverse=True)[: max(2, min(5, len(candidates)))]
    return _mean(top)


def plan_case(
    label: str,
    mesh: str | Path,
    vertices: Sequence[Sequence[float]],
    out_dir: Path,
    resolution: int,
    zoom_levels: int,
    material_mode: str = "preserve",
    detail_vertices: Sequence[Sequence[float]] | None = None,
    fixed_targets: Sequence[Sequence[float]] | None = None,
    target_source: str = "render_mesh",
    zoom_divisor: float = 2.15,
) -> dict:
    safe = _safe_label(label)
    case_dir = out_dir / safe
    extent = _extent(vertices)
    _, _, center = _bounds(vertices)
    overview_scale = round(extent * 1.22, 6)
    overview = {
        "id": "overview",
        "kind": "raw_camera_render",
        "path": str(case_dir / "overview_raw.png"),
        "annotated_path": str(case_dir / "overview_callouts.png"),
        "resolution": [resolution, resolution],
        "target": [round(value, 6) for value in center],
        "ortho_scale": overview_scale,
    }
    zooms = []
    previous_target = None
    previous_id = "overview"
    detail_source = detail_vertices if detail_vertices else vertices
    zoom_divisor = max(float(zoom_divisor), 1.15)
    for level in range(1, zoom_levels + 1):
        if fixed_targets and level - 1 < len(fixed_targets):
            target = [float(value) for value in fixed_targets[level - 1]]
        else:
            target = choose_detail_target(detail_source, level - 1, previous_target)
        scale = round(overview_scale / (zoom_divisor ** level), 6)
        zoom_id = f"zoom_{level:02d}"
        zooms.append(
            {
                "id": zoom_id,
                "kind": "camera_render",
                "path": str(case_dir / f"{zoom_id}.png"),
                "annotated_path": str(case_dir / f"{zoom_id}_callouts.png") if level < zoom_levels else None,
                "resolution": [resolution, resolution],
                "target": [round(value, 6) for value in target],
                "ortho_scale": scale,
                "parent": previous_id,
                "callout_parent": previous_id,
            }
        )
        previous_target = target
        previous_id = zoom_id
    return {
        "label": label,
        "mesh": str(mesh),
        "case_dir": str(case_dir),
        "background": "white",
        "material_mode": material_mode,
        "target_source": target_source,
        "zoom_divisor": zoom_divisor,
        "overview": overview,
        "zooms": zooms,
        "comparison_path": str(case_dir / "strict_matched_zoom_comparison.png"),
    }


def load_cases(args: argparse.Namespace) -> list[dict]:
    cases: list[dict] = []
    if args.manifest:
        payload = json.loads(args.manifest.read_text(encoding="utf-8"))
        raw_cases = payload["cases"] if isinstance(payload, dict) else payload
        for item in raw_cases:
            cases.append(
                {
                    "label": item["label"],
                    "mesh": item["mesh"],
                    "plan_mesh": item.get("plan_mesh", item["mesh"]),
                    "material_mode": item.get("material_mode", args.material_mode),
                    "zoom_levels": int(item.get("zoom_levels", args.zoom_levels)),
                    "detail_targets": item.get("detail_targets"),
                    "fixed_detail_targets": item.get("fixed_detail_targets"),
                    "detail_target_source": item.get("detail_target_source", ""),
                    "zoom_divisor": float(item.get("zoom_divisor", 2.15)),
                    "rotation_deg": item.get("presentation_rotation", item.get("rotation_deg")),
                }
            )
    for item in args.case or []:
        label, mesh = item.split("=", 1)
        cases.append(
            {
                "label": label,
                "mesh": mesh,
                "material_mode": args.material_mode,
                "zoom_levels": args.zoom_levels,
                "zoom_divisor": 2.15,
            }
        )
    if not cases:
        raise SystemExit("Provide at least one --case label=/path/to.obj or --manifest cases.json")
    return cases


def write_plan(plan: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "matched_camera_zoom_plan.json"
    path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return path


def build_plan(args: argparse.Namespace) -> dict:
    planned_cases = []
    for case in load_cases(args):
        mesh = Path(case["mesh"])
        plan_mesh = Path(case.get("plan_mesh", case["mesh"]))
        if args.target_source == "render":
            vertices = load_plan_vertices(mesh)
            target_source = "render_mesh"
        else:
            vertices = load_plan_vertices(plan_mesh)
            target_source = "plan_mesh" if vertices and plan_mesh != mesh else "render_mesh"
        detail_vertices = None
        fixed_targets = None
        if case.get("detail_targets"):
            reference = load_plan_vertices(plan_mesh) or vertices
            detail_vertices = normalize_points_like(case["detail_targets"], reference)
            target_source = case.get("detail_target_source") or "explicit_targets"
        if case.get("fixed_detail_targets"):
            reference = load_plan_vertices(plan_mesh) or vertices
            fixed_targets = normalize_points_like(case["fixed_detail_targets"], reference)
            target_source = case.get("detail_target_source") or "fixed_explicit_targets"
        planned_cases.append(
            plan_case(
                label=case["label"],
                mesh=mesh,
                vertices=vertices,
                out_dir=args.out_dir,
                resolution=args.resolution,
                zoom_levels=case["zoom_levels"],
                material_mode=case["material_mode"],
                detail_vertices=detail_vertices,
                fixed_targets=fixed_targets,
                target_source=target_source,
                zoom_divisor=float(case.get("zoom_divisor", 2.15)),
            )
        )
        planned_cases[-1]["plan_mesh"] = str(plan_mesh)
    return {
        "strict_requirements": {
            "white_background": True,
            "square_overview": True,
            "square_zoom_panels_match_overview_size": True,
            "raw_overview_saved": True,
            "zoom_panels_are_camera_renders": True,
            "nested_multiscale_zoom": True,
            "overview_callouts": True,
            "avoid_uninformative_trunks_when_possible": True,
        },
        "run_config": {
            "resolution": args.resolution,
            "samples": args.samples,
            "camera": args.camera,
            "engine": args.engine,
            "plan_only": args.plan_only,
        },
        "cases": planned_cases,
    }


def _require_blender() -> None:
    if not HAS_BLENDER:
        raise SystemExit(
            "Rendering requires Blender. Use --plan-only with python3, or run:\n"
            "blender -b --python scripts/figures/matched_camera_zoom_render_20260510.py -- <args>"
        )


def clear_scene() -> None:
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
        obj.rotation_euler = tuple(math.radians(float(value)) for value in rotation_deg)
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
    bpy.context.view_layer.update()


def setup_world(resolution: int, samples: int, engine: str = "cycles") -> None:
    scene = bpy.context.scene
    if engine == "eevee":
        for engine_name in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            try:
                scene.render.engine = engine_name
                break
            except TypeError:
                continue
        if hasattr(scene, "eevee"):
            scene.eevee.taa_render_samples = max(1, samples)
    elif engine == "workbench":
        scene.render.engine = "BLENDER_WORKBENCH"
    else:
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
    try:
        scene.display.shading.background_type = "COLOR"
    except TypeError:
        # Blender 5.1 removed/renamed the COLOR background enum; WORLD keeps
        # the same white background behavior for these offline renders.
        scene.display.shading.background_type = "WORLD"
    scene.display.shading.background_color = (1.0, 1.0, 1.0)


def add_lighting() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-2.5, -4.4, 5.2))
    key = bpy.context.object
    key.name = "matched_large_softbox"
    key.data.energy = 520
    key.data.size = 5.5
    bpy.ops.object.light_add(type="AREA", location=(3.4, 2.8, 3.2))
    fill = bpy.context.object
    fill.name = "matched_soft_fill"
    fill.data.energy = 90
    fill.data.size = 4.0


MATERIAL_PRESETS = {
    "neutral": {
        "name": "matched_neutral_matte",
        "base": (0.50, 0.55, 0.47, 1.0),
        "roughness": 0.68,
        "metallic": 0.0,
    },
    "bark": {
        "name": "matched_warm_bark_matte",
        "base": (0.46, 0.30, 0.18, 1.0),
        "roughness": 0.78,
        "metallic": 0.0,
    },
    "cedar": {
        "name": "matched_cedar_green_matte",
        "base": (0.34, 0.43, 0.31, 1.0),
        "roughness": 0.74,
        "metallic": 0.0,
    },
    "metal": {
        "name": "matched_brushed_warm_metal",
        "base": (0.58, 0.60, 0.56, 1.0),
        "roughness": 0.34,
        "metallic": 0.78,
    },
    "stone": {
        "name": "matched_limestone_matte",
        "base": (0.62, 0.59, 0.52, 1.0),
        "roughness": 0.82,
        "metallic": 0.0,
    },
    "ornament": {
        "name": "matched_burnished_ornament",
        "base": (0.66, 0.53, 0.30, 1.0),
        "roughness": 0.42,
        "metallic": 0.58,
    },
}


def make_preset_material(material_mode: str):
    spec = MATERIAL_PRESETS.get(material_mode, MATERIAL_PRESETS["neutral"])
    mat = bpy.data.materials.new(spec["name"])
    mat.diffuse_color = spec["base"]
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = spec["base"]
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = spec["roughness"]
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = spec["metallic"]
    return mat


def prepare_materials(obj, material_mode: str, add_weighted_normals: bool = True) -> None:
    if material_mode != "preserve" or not obj.data.materials:
        obj.data.materials.clear()
        obj.data.materials.append(make_preset_material(material_mode))
    if add_weighted_normals:
        for poly in obj.data.polygons:
            poly.use_smooth = True
        mod = obj.modifiers.new("matched_weighted_normals", "WEIGHTED_NORMAL")
        mod.keep_sharp = True


def world_vertices(obj, max_vertices: int = 60000) -> list[tuple[float, float, float]]:
    matrix = obj.matrix_world
    vertices = obj.data.vertices
    total = len(vertices)
    if total <= max_vertices:
        return [tuple(matrix @ vertex.co) for vertex in vertices]
    step = max(1, total // max_vertices)
    sampled = [vertices[idx] for idx in range(0, total, step)]
    # Always include the last vertex so the sampling remains stable for tails.
    if sampled[-1].index != vertices[-1].index:
        sampled.append(vertices[-1])
    return [tuple(matrix @ vertex.co) for vertex in sampled[: max_vertices + 1]]


def camera_direction(name: str):
    if name == "front":
        return Vector((0.0, -1.0, 0.18)).normalized()
    if name == "side":
        return Vector((1.0, -0.05, 0.18)).normalized()
    return Vector((4.2, -5.2, 3.0)).normalized()


def add_camera(target: Sequence[float], ortho_scale: float, camera: str):
    target_v = Vector(target)
    direction = camera_direction(camera)
    loc = target_v + direction * 7.0
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.rotation_euler = (target_v - loc).to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho_scale
    bpy.context.scene.camera = cam
    return cam


def render_to(path: Path, camera_obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.camera = camera_obj
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    composite_white_background(path)


def composite_white_background(path: Path) -> bool:
    try:
        from PIL import Image
    except Exception:
        return False
    src = Image.open(path).convert("RGBA")
    base = Image.new("RGBA", src.size, WHITE + (255,))
    base.alpha_composite(src)
    base.convert("RGB").save(path)
    return True


def projected_rect(parent_camera, target: Sequence[float], child_scale: float, resolution: int) -> tuple[int, int, int, int]:
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
    return left, top, max(left + 2, right_px), max(top + 2, bottom)


def draw_callouts(
    image_path: Path,
    out_path: Path,
    rects: Sequence[tuple[int, int, int, int]],
    labels: Sequence[str],
    *,
    callout_color: tuple[int, int, int] | None = None,
    show_labels: bool = True,
) -> bool:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        print(f"[warn] PIL unavailable; skipped callouts for {image_path}")
        return False

    src = Image.open(image_path).convert("RGBA")
    im = Image.new("RGBA", src.size, WHITE + (255,))
    im.alpha_composite(src)
    im = im.convert("RGB")
    draw = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", max(18, im.width // 42))
    except Exception:
        font = ImageFont.load_default()
    for idx, rect in enumerate(rects):
        color = callout_color or ACCENTS[idx % len(ACCENTS)]
        draw.rectangle(rect, outline=color, width=max(4, im.width // 220))
        if not show_labels:
            continue
        label = labels[idx]
        tx, ty = rect[0] + 8, max(8, rect[1] - max(22, im.width // 38))
        bbox = draw.textbbox((tx, ty), label, font=font)
        draw.rectangle((bbox[0] - 5, bbox[1] - 3, bbox[2] + 5, bbox[3] + 3), fill=WHITE)
        draw.text((tx, ty), label, font=font, fill=color)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path)
    return True


def compose_case(case_plan: dict) -> bool:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        print(f"[warn] PIL unavailable; skipped comparison sheet for {case_plan.get('label')}")
        return False

    overview_path = Path(case_plan["overview"]["annotated_path"])
    if not overview_path.exists():
        overview_path = Path(case_plan["overview"]["path"])
    panels = [("Overview", overview_path)] + [
        (zoom["id"].replace("_", " ").title(), Path(zoom["path"])) for zoom in case_plan["zooms"]
    ]
    loaded = []
    for _, path in panels:
        src = Image.open(path).convert("RGBA")
        base = Image.new("RGBA", src.size, WHITE + (255,))
        base.alpha_composite(src)
        loaded.append(base.convert("RGB"))
    panel_size = loaded[0].width
    gap = max(36, panel_size // 32)
    label_h = max(58, panel_size // 18)
    margin = max(44, panel_size // 28)
    width = margin * 2 + len(panels) * panel_size + (len(panels) - 1) * gap
    height = margin * 2 + label_h + panel_size
    canvas = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", max(24, panel_size // 34))
    except Exception:
        font = ImageFont.load_default()
    for idx, ((label, _), image) in enumerate(zip(panels, loaded)):
        x = margin + idx * (panel_size + gap)
        y = margin
        canvas.paste(image.resize((panel_size, panel_size), Image.Resampling.LANCZOS), (x, y))
        bbox = draw.textbbox((0, 0), label, font=font)
        draw.text((x + panel_size / 2 - (bbox[2] - bbox[0]) / 2, y + panel_size + 18), label, font=font, fill=INK)
    out = Path(case_plan["comparison_path"])
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    return True


def render_case_with_blender(case_spec: dict, args: argparse.Namespace) -> dict:
    mesh = Path(case_spec["mesh"])
    plan_mesh = Path(case_spec.get("plan_mesh", case_spec["mesh"]))
    clear_scene()
    setup_world(args.resolution, args.samples, args.engine)
    obj = import_mesh(mesh)
    # Some GLB files carry scene/world settings. Re-apply the paper-safe
    # render setup after import so the background stays pure white.
    setup_world(args.resolution, args.samples, args.engine)
    normalize_object(obj, rotation_deg=case_spec.get("rotation_deg"))
    prepare_materials(obj, case_spec["material_mode"], add_weighted_normals=args.engine != "workbench")
    add_lighting()
    vertices = world_vertices(obj)
    detail_vertices = None
    fixed_targets = None
    target_source = "render_mesh"
    if case_spec.get("detail_targets"):
        reference_vertices = parse_obj_vertices(plan_mesh) if plan_mesh.exists() and plan_mesh.suffix.lower() == ".obj" else []
        detail_vertices = normalize_points_like(case_spec["detail_targets"], reference_vertices or case_spec["detail_targets"])
        target_source = case_spec.get("detail_target_source") or "explicit_targets"
    if case_spec.get("fixed_detail_targets"):
        reference_vertices = parse_obj_vertices(plan_mesh) if plan_mesh.exists() and plan_mesh.suffix.lower() == ".obj" else []
        fixed_targets = normalize_points_like(case_spec["fixed_detail_targets"], reference_vertices or case_spec["fixed_detail_targets"])
        target_source = case_spec.get("detail_target_source") or "fixed_explicit_targets"
    elif args.target_source != "render" and plan_mesh.exists() and plan_mesh.suffix.lower() == ".obj":
        detail_vertices = normalize_points(parse_obj_vertices(plan_mesh))
        if detail_vertices:
            target_source = "plan_mesh"
    case_plan = plan_case(
        case_spec["label"],
        mesh,
        vertices,
        args.out_dir,
        args.resolution,
        case_spec["zoom_levels"],
        case_spec["material_mode"],
        detail_vertices=detail_vertices,
        fixed_targets=fixed_targets,
        target_source=target_source,
        zoom_divisor=float(case_spec.get("zoom_divisor", 2.15)),
    )
    case_plan["plan_mesh"] = str(plan_mesh)
    if case_spec.get("rotation_deg"):
        case_plan["rotation_deg"] = case_spec["rotation_deg"]

    cameras = {}
    overview = case_plan["overview"]
    cameras["overview"] = add_camera(overview["target"], overview["ortho_scale"], args.camera)
    if not args.skip_renders:
        render_to(Path(overview["path"]), cameras["overview"])
    for zoom in case_plan["zooms"]:
        cameras[zoom["id"]] = add_camera(zoom["target"], zoom["ortho_scale"], args.camera)
        if not args.skip_renders:
            render_to(Path(zoom["path"]), cameras[zoom["id"]])

    child_by_parent: dict[str, list[dict]] = {}
    for zoom in case_plan["zooms"]:
        child_by_parent.setdefault(zoom["callout_parent"], []).append(zoom)
    case_plan["callouts"] = []
    for parent_id, children in child_by_parent.items():
        if parent_id == "overview":
            parent_path = Path(overview["path"])
            annotated_path = Path(overview["annotated_path"])
        else:
            parent_zoom = next(zoom for zoom in case_plan["zooms"] if zoom["id"] == parent_id)
            parent_path = Path(parent_zoom["path"])
            if parent_zoom["annotated_path"] is None:
                continue
            annotated_path = Path(parent_zoom["annotated_path"])
        rects = [
            projected_rect(cameras[parent_id], child["target"], child["ortho_scale"], args.resolution)
            for child in children
        ]
        labels = [child["id"] for child in children]
        case_plan["callouts"].append(
            {
                "parent_id": parent_id,
                "parent_path": str(parent_path),
                "annotated_path": str(annotated_path),
                "rects": [list(rect) for rect in rects],
                "labels": labels,
            }
        )
        if not args.skip_renders:
            draw_callouts(
                parent_path,
                annotated_path,
                rects,
                labels,
                callout_color=tuple(args.callout_color) if args.callout_color else None,
                show_labels=not args.hide_callout_labels,
            )
    if not args.skip_comparison and not args.skip_renders:
        compose_case(case_plan)
    return case_plan


def render_all_with_blender(args: argparse.Namespace) -> dict:
    _require_blender()
    rendered_cases = [render_case_with_blender(case, args) for case in load_cases(args)]
    return {
        "strict_requirements": build_plan(args)["strict_requirements"],
        "run_config": {
            "resolution": args.resolution,
            "samples": args.samples,
            "camera": args.camera,
            "engine": args.engine,
            "plan_only": False,
        },
        "cases": rendered_cases,
    }


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", help="label=/absolute/path/to.obj|glb")
    parser.add_argument("--manifest", type=Path, help="JSON with cases: [{label, mesh, material_mode?, zoom_levels?}]")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--resolution", type=int, default=1600)
    parser.add_argument("--samples", type=int, default=96)
    parser.add_argument("--zoom-levels", type=int, default=2)
    parser.add_argument("--camera", choices=["iso", "front", "side"], default="iso")
    parser.add_argument("--engine", choices=["cycles", "eevee", "workbench"], default="cycles")
    parser.add_argument(
        "--material-mode",
        choices=["preserve", *MATERIAL_PRESETS.keys()],
        default="preserve",
    )
    parser.add_argument("--target-source", choices=["auto", "render", "plan"], default="auto")
    parser.add_argument(
        "--callout-color",
        nargs=3,
        type=int,
        metavar=("R", "G", "B"),
        help="Override callout rectangle color, e.g. --callout-color 130 130 130 for gray.",
    )
    parser.add_argument("--hide-callout-labels", action="store_true")
    parser.add_argument("--skip-comparison", action="store_true")
    parser.add_argument("--skip-renders", action="store_true")
    parser.add_argument("--plan-only", action="store_true")
    return parser.parse_args(argv)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = parse_args(argv)
    if args.plan_only:
        plan = build_plan(args)
    else:
        plan = render_all_with_blender(args)
    path = write_plan(plan, args.out_dir)
    print(path)
    if not args.plan_only:
        for case in plan["cases"]:
            print(case["comparison_path"])


if __name__ == "__main__":
    main()
