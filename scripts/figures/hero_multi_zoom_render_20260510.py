#!/usr/bin/env python3
"""Pure-white, no-text hero multi-zoom renderer for textured GLB meshes.

Run from the repository root with Blender:

  /Applications/Blender.app/Contents/MacOS/Blender -b \
    --python scripts/figures/hero_multi_zoom_render_20260510.py -- \
    --out-dir visuals/hero_multi_zoom_white_20260510

The output is a publication-safe contact sheet: pure white background, no
ground/platform, no in-image titles, and three nested orthographic camera zooms.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
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


REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = REPO / "visuals" / "hero_multi_zoom_white_20260510"
WHITE = (255, 255, 255)
CALLOUT_COLORS = [
    (38, 96, 170),
    (194, 74, 58),
    (32, 132, 93),
]

DEFAULT_CASES = [
    {
        "label": "bismuth",
        "mesh": REPO
        / "visuals/strict_visual_matched_texture_20260510/"
        / "ifs_bismuth_hopper_d4_terraces_steps8_tex2048_seed20260847_xformers/textured.glb",
        "shade_smooth": False,
    },
    {
        "label": "pyrite",
        "mesh": REPO
        / "visuals/strict_visual_matched_texture_20260510/"
        / "ifs_fractal_lattice_d4_pyrite_steps8_tex2048_seed20260841_xformers/textured.glb",
        "shade_smooth": False,
    },
    {
        "label": "coral",
        "mesh": REPO
        / "visuals/strict_visual_matched_texture_20260510/"
        / "dla_coral_cluster_900_frontier_connected_steps8_tex2048_seed20260711_xformers/textured.glb",
        "shade_smooth": True,
    },
    {
        "label": "root_fan",
        "mesh": REPO
        / "visuals/strict_visual_matched_texture_20260510/"
        / "lsys_root_fan_d5_hair_tokens_steps8_tex2048_seed20260527_xformers/textured.glb",
        "shade_smooth": True,
    },
]


def _safe_label(label: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in label)
    return safe.strip("_") or "case"


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
        return [-1.0, -1.0, -1.0], [1.0, 1.0, 1.0], [0.0, 0.0, 0.0]
    mins = [min(point[idx] for point in vertices) for idx in range(3)]
    maxs = [max(point[idx] for point in vertices) for idx in range(3)]
    center = [(mins[idx] + maxs[idx]) * 0.5 for idx in range(3)]
    return mins, maxs, center


def _extent(vertices: Sequence[Sequence[float]]) -> float:
    mins, maxs, _ = _bounds(vertices)
    return max(maxs[idx] - mins[idx] for idx in range(3)) or 1.0


def choose_detail_target(
    vertices: Sequence[Sequence[float]],
    level: int,
    previous_target: Sequence[float] | None = None,
) -> list[float]:
    """Choose a stable, nested detail point away from the plain object center."""
    if not vertices:
        return [0.0, 0.0, 0.0]

    extent = _extent(vertices)
    _, _, center = _bounds(vertices)
    zs = [point[2] for point in vertices]
    lower_z = _quantile(zs, 0.35)
    lower_body = [point for point in vertices if point[2] <= lower_z]
    stem_center = _mean(lower_body or vertices)
    radial = [
        math.hypot(point[0] - stem_center[0], point[1] - stem_center[1])
        for point in vertices
    ]

    z_gate = _quantile(zs, min(0.52 + 0.10 * level, 0.78))
    r_gate = _quantile(radial, 0.50)
    candidates = [
        point
        for point, radius in zip(vertices, radial)
        if point[2] >= z_gate and radius >= r_gate
    ]

    if previous_target is not None:
        radius = extent / (1.35 + 0.38 * level)
        nested = [
            point
            for point in candidates
            if math.dist(point, previous_target) <= radius
        ]
        if nested:
            candidates = nested

    if not candidates:
        candidates = [point for point in vertices if point[2] >= z_gate]
    if not candidates:
        candidates = list(vertices)

    def score(point: Sequence[float]) -> float:
        r = math.hypot(point[0] - stem_center[0], point[1] - stem_center[1])
        high = (point[2] - center[2]) / max(extent, 1e-6)
        nested_bonus = 0.0
        if previous_target is not None:
            nested_bonus = -0.25 * math.dist(point, previous_target) / max(extent, 1e-6)
        return 0.95 * r / max(extent, 1e-6) + 0.55 * high + nested_bonus

    top = sorted(candidates, key=score, reverse=True)[: max(4, min(18, len(candidates)))]
    return _mean(top)


def load_cases(args: argparse.Namespace) -> list[dict]:
    cases: list[dict] = []
    if args.manifest:
        payload = json.loads(args.manifest.read_text(encoding="utf-8"))
        raw_cases = payload["cases"] if isinstance(payload, dict) else payload
        for item in raw_cases:
            cases.append(
                {
                    "label": item["label"],
                    "mesh": Path(item["mesh"]),
                    "shade_smooth": bool(item.get("shade_smooth", args.shade_smooth)),
                    "material_mode": item.get("material_mode", args.material_mode),
                }
            )
    for item in args.case or []:
        label, mesh = item.split("=", 1)
        cases.append(
            {
                "label": label,
                "mesh": Path(mesh),
                "shade_smooth": args.shade_smooth,
                "material_mode": args.material_mode,
            }
        )
    if not cases:
        cases = [
            {
                **case,
                "material_mode": args.material_mode,
            }
            for case in DEFAULT_CASES
        ]
    for case in cases:
        if not case["mesh"].exists():
            raise SystemExit(f"Missing GLB/mesh for case {case['label']}: {case['mesh']}")
    return cases


def _require_blender() -> None:
    if not HAS_BLENDER:
        raise SystemExit("Rendering requires Blender/bpy. Run this script via blender -b --python ...")


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_mesh(path: Path):
    before = set(bpy.data.objects)
    suffix = path.suffix.lower()
    if suffix in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif suffix == ".obj":
        if hasattr(bpy.ops.wm, "obj_import"):
            bpy.ops.wm.obj_import(filepath=str(path))
        else:
            bpy.ops.import_scene.obj(filepath=str(path))
    else:
        raise ValueError(f"Unsupported mesh format: {path}")

    imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    if not imported:
        raise RuntimeError(f"No mesh objects imported from {path}")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in imported:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = imported[0]
    if len(imported) > 1:
        bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = _safe_label(path.parent.name)
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


def setup_world(resolution: int, samples: int, engine: str) -> None:
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
    else:
        scene.render.engine = "CYCLES"
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
        scene.cycles.max_bounces = 6
        scene.cycles.diffuse_bounces = 3
        scene.cycles.glossy_bounces = 3
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = False
    world.color = (1.0, 1.0, 1.0)
    scene.display.shading.background_type = "COLOR"
    scene.display.shading.background_color = (1.0, 1.0, 1.0)


def add_lighting() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-3.4, -4.7, 5.3))
    key = bpy.context.object
    key.name = "hero_key_softbox"
    key.data.energy = 470
    key.data.size = 5.8

    bpy.ops.object.light_add(type="AREA", location=(4.1, 2.5, 3.3))
    fill = bpy.context.object
    fill.name = "hero_fill_softbox"
    fill.data.energy = 105
    fill.data.size = 4.3

    bpy.ops.object.light_add(type="POINT", location=(0.0, -2.2, 2.6))
    rim = bpy.context.object
    rim.name = "hero_front_pin"
    rim.data.energy = 18
    rim.data.shadow_soft_size = 5.0


def make_fallback_pbr_material():
    mat = bpy.data.materials.new("hero_fallback_pbr")
    mat.diffuse_color = (0.62, 0.58, 0.50, 1.0)
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (0.62, 0.58, 0.50, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.58
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def prepare_materials(obj, material_mode: str, shade_smooth: bool) -> None:
    if material_mode != "preserve" or not obj.data.materials:
        obj.data.materials.clear()
        obj.data.materials.append(make_fallback_pbr_material())
    if shade_smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True
    mod = obj.modifiers.new("hero_weighted_normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True


def world_vertices(obj, max_vertices: int = 70000) -> list[tuple[float, float, float]]:
    matrix = obj.matrix_world
    vertices = obj.data.vertices
    total = len(vertices)
    if total <= max_vertices:
        return [tuple(matrix @ vertex.co) for vertex in vertices]
    step = max(1, total // max_vertices)
    sampled = [vertices[idx] for idx in range(0, total, step)]
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
    return left, top, max(left + 3, right_px), max(top + 3, bottom)


def flatten_to_white(image_path: Path) -> None:
    from PIL import Image

    src = Image.open(image_path).convert("RGBA")
    base = Image.new("RGBA", src.size, WHITE + (255,))
    base.alpha_composite(src)
    im = base.convert("RGB")
    whiten_border_background(im)
    im.save(image_path)


def whiten_border_background(im) -> None:
    """Replace Blender/GLTF gray world pixels with white without touching the mesh."""
    from collections import deque

    w, h = im.size
    px = im.load()
    seen = bytearray(w * h)
    q: deque[tuple[int, int]] = deque()

    def idx(x: int, y: int) -> int:
        return y * w + x

    def is_background(pixel: tuple[int, int, int]) -> bool:
        r, g, b = pixel
        mean = (r + g + b) / 3.0
        return max(pixel) - min(pixel) <= 12 and 35 <= mean <= 130

    def push(x: int, y: int) -> None:
        i = idx(x, y)
        if not seen[i] and is_background(px[x, y]):
            seen[i] = 1
            q.append((x, y))

    for x in range(w):
        push(x, 0)
        push(x, h - 1)
    for y in range(h):
        push(0, y)
        push(w - 1, y)

    while q:
        x, y = q.popleft()
        px[x, y] = WHITE
        if x > 0:
            push(x - 1, y)
        if x + 1 < w:
            push(x + 1, y)
        if y > 0:
            push(x, y - 1)
        if y + 1 < h:
            push(x, y + 1)


def draw_callout(image_path: Path, out_path: Path, rect: tuple[int, int, int, int], level: int) -> None:
    from PIL import Image, ImageDraw

    src = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(src)
    width = max(4, src.width // 230)
    color = CALLOUT_COLORS[level % len(CALLOUT_COLORS)]
    draw.rectangle(rect, outline=color, width=width)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    src.save(out_path)


def compose_sheet(case_plans: Sequence[dict], out_dir: Path) -> Path:
    from PIL import Image

    rows: list[list[Image.Image]] = []
    for case in case_plans:
        paths = [
            Path(case["overview"]["callout_path"]),
            Path(case["zooms"][0]["callout_path"]),
            Path(case["zooms"][1]["callout_path"]),
            Path(case["zooms"][2]["path"]),
        ]
        row = [Image.open(path).convert("RGB") for path in paths]
        rows.append(row)

    panel = rows[0][0].width
    gap = max(22, panel // 44)
    margin = max(28, panel // 36)
    width = margin * 2 + 4 * panel + 3 * gap
    height = margin * 2 + len(rows) * panel + (len(rows) - 1) * gap
    canvas = Image.new("RGB", (width, height), WHITE)
    for r, row in enumerate(rows):
        for c, image in enumerate(row):
            x = margin + c * (panel + gap)
            y = margin + r * (panel + gap)
            canvas.paste(image, (x, y))
    out = out_dir / "hero_multi_zoom_white_20260510.png"
    canvas.save(out)
    return out


def compose_from_manifest(manifest_path: Path) -> Path:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw_paths: list[Path] = []
    for case in payload["cases"]:
        raw_paths.append(Path(case["overview"]["path"]))
        raw_paths.extend(Path(zoom["path"]) for zoom in case["zooms"])
    for path in raw_paths:
        flatten_to_white(path)
    for case in payload["cases"]:
        for idx, callout in enumerate(case.get("callouts", [])):
            draw_callout(
                Path(callout["parent_path"]),
                Path(callout["path"]),
                tuple(callout["rect"]),
                idx,
            )
    sheet_path = compose_sheet(payload["cases"], manifest_path.parent)
    payload["run_config"]["sheet_path"] = str(sheet_path)
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return sheet_path


def run_external_compose(manifest_path: Path) -> Path:
    cmd = [
        "/usr/bin/python3",
        str(Path(__file__).resolve()),
        "--compose-only",
        "--manifest-path",
        str(manifest_path),
    ]
    subprocess.run(cmd, check=True)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    return Path(payload["run_config"]["sheet_path"])


def plan_case(
    case: dict,
    vertices: Sequence[Sequence[float]],
    out_dir: Path,
    resolution: int,
    zoom_levels: int,
    zoom_ratio: float,
) -> dict:
    safe = _safe_label(case["label"])
    case_dir = out_dir / safe
    extent = _extent(vertices)
    _, _, center = _bounds(vertices)
    overview_scale = extent * 1.20
    overview = {
        "id": "overview",
        "path": str(case_dir / "overview_raw.png"),
        "callout_path": str(case_dir / "overview_callout.png"),
        "target": [round(value, 6) for value in center],
        "ortho_scale": round(overview_scale, 6),
    }
    zooms = []
    previous_target = None
    for idx in range(zoom_levels):
        target = choose_detail_target(vertices, idx, previous_target)
        scale = overview_scale / (zoom_ratio ** (idx + 1))
        zoom_id = f"zoom_{idx + 1:02d}"
        zooms.append(
            {
                "id": zoom_id,
                "path": str(case_dir / f"{zoom_id}.png"),
                "callout_path": str(case_dir / f"{zoom_id}_callout.png") if idx + 1 < zoom_levels else None,
                "target": [round(value, 6) for value in target],
                "ortho_scale": round(scale, 6),
                "parent": "overview" if idx == 0 else f"zoom_{idx:02d}",
            }
        )
        previous_target = target
    return {
        "label": case["label"],
        "mesh": str(case["mesh"]),
        "case_dir": str(case_dir),
        "material_mode": case.get("material_mode", "preserve"),
        "shade_smooth": bool(case.get("shade_smooth", False)),
        "overview": overview,
        "zooms": zooms,
    }


def render_case(case: dict, args: argparse.Namespace) -> dict:
    clear_scene()
    setup_world(args.resolution, args.samples, args.engine)
    obj = import_mesh(case["mesh"])
    setup_world(args.resolution, args.samples, args.engine)
    normalize_object(obj, target_extent=3.0)
    prepare_materials(obj, case.get("material_mode", "preserve"), case.get("shade_smooth", False))
    add_lighting()
    vertices = world_vertices(obj)
    case_plan = plan_case(case, vertices, args.out_dir, args.resolution, args.zoom_levels, args.zoom_ratio)

    cameras = {}
    overview = case_plan["overview"]
    cameras["overview"] = add_camera(overview["target"], overview["ortho_scale"], args.camera)
    render_to(Path(overview["path"]), cameras["overview"])

    for zoom in case_plan["zooms"]:
        cameras[zoom["id"]] = add_camera(zoom["target"], zoom["ortho_scale"], args.camera)
        render_to(Path(zoom["path"]), cameras[zoom["id"]])

    for idx, zoom in enumerate(case_plan["zooms"]):
        if idx == 0:
            parent_id = "overview"
            parent_path = Path(overview["path"])
            out_path = Path(overview["callout_path"])
        else:
            parent = case_plan["zooms"][idx - 1]
            parent_id = parent["id"]
            parent_path = Path(parent["path"])
            out_path = Path(parent["callout_path"])
        rect = projected_rect(cameras[parent_id], zoom["target"], zoom["ortho_scale"], args.resolution)
        case_plan.setdefault("callouts", []).append(
            {
                "parent": parent_id,
                "child": zoom["id"],
                "rect": list(rect),
                "parent_path": str(parent_path),
                "path": str(out_path),
            }
        )

    return case_plan


def write_manifest(case_plans: Sequence[dict], out_dir: Path, args: argparse.Namespace, sheet_path: Path | None) -> Path:
    payload = {
        "requirements": {
            "pure_white_background": True,
            "no_ground_plane": True,
            "no_platform": True,
            "no_in_image_text": True,
            "camera_rerendered_zooms_not_2d_crops": True,
            "zoom_levels": args.zoom_levels,
        },
        "run_config": {
            "resolution": args.resolution,
            "samples": args.samples,
            "engine": args.engine,
            "camera": args.camera,
            "zoom_ratio": args.zoom_ratio,
            "out_dir": str(out_dir),
            "sheet_path": str(sheet_path) if sheet_path else None,
        },
        "cases": list(case_plans),
    }
    path = out_dir / "hero_multi_zoom_manifest_20260510.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", help="label=/absolute/path/to.obj|glb")
    parser.add_argument("--manifest", type=Path, help="JSON with cases: [{label, mesh, material_mode?, shade_smooth?}]")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--resolution", type=int, default=1200)
    parser.add_argument("--samples", type=int, default=96)
    parser.add_argument("--zoom-levels", type=int, default=3)
    parser.add_argument("--zoom-ratio", type=float, default=1.88)
    parser.add_argument("--camera", choices=["iso", "front", "side"], default="iso")
    parser.add_argument("--engine", choices=["cycles", "eevee"], default="cycles")
    parser.add_argument("--material-mode", choices=["preserve", "neutral"], default="preserve")
    parser.add_argument("--shade-smooth", action="store_true")
    parser.add_argument("--compose-only", action="store_true")
    parser.add_argument("--manifest-path", type=Path)
    return parser.parse_args(argv)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = parse_args(argv)
    if args.compose_only:
        if not args.manifest_path:
            raise SystemExit("--compose-only requires --manifest-path")
        sheet_path = compose_from_manifest(args.manifest_path)
        print(sheet_path)
        return

    args.out_dir = args.out_dir.resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.zoom_levels != 3:
        raise SystemExit("This hero renderer is fixed to --zoom-levels 3 for the 20260510 output contract.")
    _require_blender()
    case_plans = [render_case(case, args) for case in load_cases(args)]
    manifest_path = write_manifest(case_plans, args.out_dir, args, None)
    sheet_path = run_external_compose(manifest_path)
    print(manifest_path)
    print(sheet_path)
    for case in case_plans:
        print(case["case_dir"])


if __name__ == "__main__":
    main()
