#!/usr/bin/env python3
"""Build and render the five-case publication hero combo GLB.

Run from the repository root:

  /Applications/Blender.app/Contents/MacOS/Blender -b \
    --python scripts/figures/hero_combo_publication_20260510.py -- \
    --out-dir visuals/hero_combo_publication_20260510 \
    --resolution 1200 --samples 96

Use --plan-only with system Python to write the manifest without requiring bpy.
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
    from mathutils import Vector  # type: ignore

    HAS_BLENDER = True
except Exception:
    bpy = None
    Vector = None
    HAS_BLENDER = False


REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = REPO / "visuals" / "hero_combo_publication_20260510"
BG_COLOR = (0.91, 0.95, 0.97, 1.0)
PLATFORM_COLOR = (0.88, 0.93, 0.95, 1.0)


def default_cases() -> list[dict]:
    return [
        {
            "label": "bismuth_terraced_hopper",
            "display": "bismuth crystal / terraced pyramid",
            "category": "bismuth",
            "mesh": REPO
            / "visuals/connected_scaffold_v2_textured_glb_hq_20260509"
            / "bismuth_hopper_bismuth_hq_steps8_tex2048_xformers/textured.glb",
            "smooth": False,
            "scale_boost": 1.08,
            "recommended_rank": 1,
            "reason": "HQ scaffold manifest identifies this as the strongest bismuth hopper candidate.",
        },
        {
            "label": "pyrite_lattice_crystal",
            "display": "pyrite crystal",
            "category": "pyrite",
            "mesh": REPO
            / "visuals/connected_scaffold_v2_textured_glb_hq_20260509"
            / "pyrite_lattice_pyrite_hq_steps8_tex2048_xformers/textured.glb",
            "smooth": False,
            "scale_boost": 1.04,
            "recommended_rank": 1,
            "reason": "HQ scaffold pyrite lattice, already selected in the user gallery manifest.",
        },
        {
            "label": "coral_branching",
            "display": "coral",
            "category": "coral",
            "mesh": REPO
            / "visuals/connected_scaffold_v2_textured_glb_hq_20260509"
            / "volumetric_dla_coral_octopus_hq_steps8_tex2048_xformers/textured.glb",
            "smooth": True,
            "scale_boost": 1.12,
            "recommended_rank": 1,
            "reason": "HQ volumetric coral; apply optional smoothing/weighted normals for the hero render.",
        },
        {
            "label": "tree_root_leaf",
            "display": "tree-root / tree-leaf case",
            "category": "tree-root/tree-leaf",
            "mesh": REPO
            / "visuals/hero_botanical_variants_20260510/tree_compete_s3_green_leaf_brown_root.glb",
            "smooth": True,
            "scale_boost": 1.24,
            "botanical_contrast": "preserve",
            "zoom_scale": 2.15,
            "recommended_rank": 1,
            "reason": "Presentation variant of the user-selected tree_compete_iso case: green leaf/crown surfaces with brown root/trunk surfaces.",
        },
        {
            "label": "plant_leaf_with_base",
            "display": "plant leaf case with base",
            "category": "plant-leaf/base",
            "mesh": REPO
            / "visuals/hero_botanical_variants_20260510"
            / "vine_stage5_parthenocissus_warm_upright_green_leaf_brown_base.glb",
            "smooth": True,
            "scale_boost": 1.34,
            "botanical_contrast": "preserve",
            "zoom_scale": 2.05,
            "recommended_rank": 1,
            "reason": "Presentation variant of the user-selected tree_roots_square_front same-stage vine geometry: local-Z mirror makes the base sit down, with green upper growth and brown base.",
        },
    ]


def _safe_label(label: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in label)
    return safe.strip("_") or "case"


def load_cases(args: argparse.Namespace) -> list[dict]:
    if args.manifest:
        payload = json.loads(args.manifest.read_text(encoding="utf-8"))
        raw_cases = payload["cases"] if isinstance(payload, dict) else payload
        cases = []
        for idx, item in enumerate(raw_cases):
            cases.append(
                {
                    "label": item["label"],
                    "display": item.get("display", item["label"]),
                    "category": item.get("category", "custom"),
                    "mesh": Path(item["mesh"]).resolve(),
                    "smooth": bool(item.get("smooth", False)),
                    "recommended_rank": int(item.get("recommended_rank", idx + 1)),
                    "reason": item.get("reason", "custom manifest case"),
                }
            )
    else:
        cases = [{**case, "mesh": Path(case["mesh"]).resolve()} for case in default_cases()]

    if len(cases) != 5:
        raise SystemExit(f"Expected exactly five hero cases, got {len(cases)}")
    missing = [str(case["mesh"]) for case in cases if not Path(case["mesh"]).exists()]
    if missing:
        raise SystemExit("Missing mesh files:\n" + "\n".join(missing))
    return cases


def case_x_positions(count: int, spacing: float) -> list[float]:
    start = -0.5 * spacing * (count - 1)
    return [start + idx * spacing for idx in range(count)]


def build_manifest(cases: Sequence[dict], out_dir: Path, args: argparse.Namespace) -> dict:
    positions = case_x_positions(len(cases), args.spacing)
    planned_cases = []
    for idx, case in enumerate(cases):
        safe = _safe_label(case["label"])
        planned_cases.append(
            {
                "label": case["label"],
                "display": case.get("display", case["label"]),
                "category": case.get("category", ""),
                "source_glb": str(case["mesh"]),
                "recommended_rank": case.get("recommended_rank", idx + 1),
                "selection_reason": case.get("reason", ""),
                "smooth": bool(case.get("smooth", False)),
                "placement": {
                    "index": idx,
                    "location": [round(positions[idx], 6), 0.0, 0.0],
                    "target_extent": args.target_extent,
                    "scale_boost": float(case.get("scale_boost", 1.0)),
                    "grounded_on_platform": True,
                },
                "zoom": {
                    "kind": "camera_render",
                    "path": str(out_dir / safe / "zoom.png"),
                    "camera": f"camera_zoom_{safe}",
                    "ortho_scale": float(case.get("zoom_scale", args.zoom_scale)),
                },
                "botanical_contrast": case.get("botanical_contrast", "preserve"),
            }
        )

    return {
        "created_for": "R-SLG Lane C five-case publication hero combo",
        "requirements": {
            "combined_glb": True,
            "overview_is_camera_render": True,
            "zooms_are_camera_renders_not_2d_crops": True,
            "light_blue_gray_background_and_platform": True,
            "no_visible_horizon_line_target": True,
            "brighter_lighting_and_exposure": True,
            "coral_optional_smoothing": True,
        },
        "environment": {
            "background_family": "light blue-gray seamless",
            "world_color_rgba": list(BG_COLOR),
            "platform_color_rgba": list(PLATFORM_COLOR),
            "platform_shape": "large seamless rectangular matte stage, matching world color",
        },
        "render_config": {
            "engine": args.engine,
            "resolution": [args.resolution, args.resolution],
            "samples": args.samples,
            "exposure": args.exposure,
            "camera": args.camera,
            "target_extent": args.target_extent,
            "spacing": args.spacing,
            "overview_ortho_scale": args.overview_scale,
            "zoom_ortho_scale": args.zoom_scale,
        },
        "outputs": {
            "combined_glb": str(out_dir / "hero_combo_publication_20260510.glb"),
            "combined_glb_exported": not args.skip_glb_export,
            "overview": str(out_dir / "overview.png"),
            "manifest": str(out_dir / "hero_combo_publication_manifest_20260510.json"),
        },
        "cases": planned_cases,
        "qa": {
            "expected": [
                "Combined GLB imports in Blender.",
                "Overview and zooms are direct camera renders.",
                "Background/platform are light blue-gray and no in-image text is present.",
                "Contact shadows are visible but not heavy.",
            ],
            "status": "plan-only" if args.plan_only else "pending_render",
        },
    }


def write_manifest(payload: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "hero_combo_publication_manifest_20260510.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _require_blender() -> None:
    if not HAS_BLENDER:
        raise SystemExit("Blender/bpy is required unless --plan-only is used.")


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def set_scene(args: argparse.Namespace) -> None:
    scene = bpy.context.scene
    if args.engine == "eevee":
        for engine_name in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            try:
                scene.render.engine = engine_name
                break
            except TypeError:
                continue
        if hasattr(scene, "eevee"):
            scene.eevee.taa_render_samples = max(1, args.samples)
    else:
        scene.render.engine = "CYCLES"
        scene.cycles.samples = args.samples
        scene.cycles.use_denoising = True
        scene.cycles.max_bounces = 6
    # Use display-referred color management for this figure. Filmic makes the
    # requested light blue-gray studio background render much darker than the
    # chosen color, which hurt the head-figure read.
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = args.exposure
    scene.view_settings.gamma = 1.0
    scene.render.resolution_x = args.resolution
    scene.render.resolution_y = args.resolution
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = False
    world.color = BG_COLOR[:3]


def import_glb(path: Path, label: str):
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
    obj.name = _safe_label(label)
    return obj


def normalize_and_place(obj, x: float, target_extent: float, scale_boost: float = 1.0) -> dict:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    bpy.context.view_layer.update()
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    center = sum(corners, Vector()) / 8.0
    obj.location -= center
    bpy.context.view_layer.update()
    max_dim = max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z, 1e-6)
    obj.scale *= (target_extent * scale_boost) / max_dim
    bpy.context.view_layer.update()
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_z = min(corner.z for corner in corners)
    obj.location.x += x
    obj.location.z -= min_z
    bpy.context.view_layer.update()
    return object_bounds(obj)


def object_bounds(obj) -> dict:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(getattr(corner, axis) for corner in corners) for axis in ("x", "y", "z")]
    maxs = [max(getattr(corner, axis) for corner in corners) for axis in ("x", "y", "z")]
    center = [(mins[idx] + maxs[idx]) * 0.5 for idx in range(3)]
    extent = max(maxs[idx] - mins[idx] for idx in range(3))
    return {"min": mins, "max": maxs, "center": center, "extent": extent}


def prepare_mesh(obj, smooth: bool) -> None:
    if smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True
    mod = obj.modifiers.new("hero_weighted_normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True


def _set_principled_color(mat, color: tuple[float, float, float, float], roughness: float = 0.68) -> None:
    mat.diffuse_color = color
    if not mat.use_nodes:
        mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return
    if "Base Color" in bsdf.inputs:
        bsdf.inputs["Base Color"].default_value = color
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = roughness


def enhance_botanical_contrast(obj, mode: str) -> None:
    """Keep the GLB identity but make pale plant scaffolds readable in the hero overview."""
    if mode == "preserve":
        return
    palette = {
        "leaf_bark": [
            (0.24, 0.42, 0.20, 1.0),
            (0.34, 0.24, 0.16, 1.0),
            (0.50, 0.63, 0.37, 1.0),
        ],
        "base_stem": [
            (0.30, 0.43, 0.24, 1.0),
            (0.42, 0.30, 0.20, 1.0),
            (0.56, 0.47, 0.34, 1.0),
        ],
    }.get(mode)
    if not palette:
        return
    for idx, mat in enumerate(obj.data.materials):
        if mat is None:
            continue
        color = palette[idx % len(palette)]
        # Only override very pale/low-contrast materials or objects with tiny
        # material sets. The existing green/brown texture remains visible when
        # it already carries semantic color.
        diffuse = tuple(mat.diffuse_color) if mat.diffuse_color else (1, 1, 1, 1)
        rgb = diffuse[:3]
        pale = sum(rgb) / 3.0 > 0.78 and max(rgb) - min(rgb) < 0.22
        if pale or len(obj.data.materials) <= 2:
            _set_principled_color(mat, color)


def make_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float = 0.72,
    emission_strength: float = 0.0,
):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if emission_strength > 0.0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = color
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def add_platform(width: float) -> None:
    mat = make_material("light_blue_gray_platform", PLATFORM_COLOR, emission_strength=0.22)
    # Use a single plane instead of a thick cube; the camera angle otherwise
    # sees the far side wall as a dark diagonal band.
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, 0.0, 0.0))
    platform = bpy.context.object
    platform.name = "seamless_light_blue_gray_stage"
    platform.dimensions = (width * 8.0, width * 6.0, 1.0)
    platform.location.y = -0.8
    bpy.context.view_layer.update()
    platform.data.materials.append(mat)
    platform.modifiers.new("platform_weighted_normals", "WEIGHTED_NORMAL")


def add_lighting(width: float) -> None:
    bpy.ops.object.light_add(type="AREA", location=(0.0, -0.5, 7.6))
    top = bpy.context.object
    top.name = "hero_combo_large_top_softbox"
    top.data.energy = 1350
    top.data.size = 10.5

    bpy.ops.object.light_add(type="AREA", location=(-width * 0.34, -5.0, 6.2))
    key = bpy.context.object
    key.name = "hero_combo_key_softbox"
    key.data.energy = 980
    key.data.size = 7.0

    bpy.ops.object.light_add(type="AREA", location=(width * 0.28, 2.6, 4.2))
    fill = bpy.context.object
    fill.name = "hero_combo_fill_softbox"
    fill.data.energy = 520
    fill.data.size = 8.0

    bpy.ops.object.light_add(type="POINT", location=(0.0, -3.0, 2.2))
    front = bpy.context.object
    front.name = "hero_combo_front_lift"
    front.data.energy = 120
    front.data.shadow_soft_size = 5.0


def camera_direction(kind: str):
    if kind == "front":
        return Vector((0.0, -1.0, 0.20)).normalized()
    return Vector((5.5, -6.8, 3.8)).normalized()


def add_camera(name: str, target: Sequence[float], ortho_scale: float, kind: str):
    target_v = Vector(target)
    direction = camera_direction(kind)
    loc = target_v + direction * 12.0
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.name = name
    cam.rotation_euler = (target_v - loc).to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho_scale
    return cam


def render(path: Path, camera_obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.camera = camera_obj
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def export_glb(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB")


def render_scene(cases: Sequence[dict], out_dir: Path, args: argparse.Namespace, manifest: dict) -> dict:
    _require_blender()
    clear_scene()
    set_scene(args)

    positions = case_x_positions(len(cases), args.spacing)
    objects = []
    bounds = []
    for idx, case in enumerate(cases):
        obj = import_glb(Path(case["mesh"]), case["label"])
        b = normalize_and_place(obj, positions[idx], args.target_extent, float(case.get("scale_boost", 1.0)))
        prepare_mesh(obj, bool(case.get("smooth", False)))
        enhance_botanical_contrast(obj, case.get("botanical_contrast", "preserve"))
        objects.append(obj)
        bounds.append(b)
        manifest["cases"][idx]["bounds_after_transform"] = b

    width = args.spacing * (len(cases) - 1) + args.target_extent * 2.0
    add_platform(width)
    add_lighting(width)

    if args.export_only and args.skip_glb_export:
        raise SystemExit("--export-only requires GLB export; remove --skip-glb-export.")

    if not args.skip_glb_export:
        export_glb(Path(manifest["outputs"]["combined_glb"]))

    if args.export_only:
        manifest["qa"]["status"] = "glb_exported"
        manifest["qa"]["actual_outputs"] = [manifest["outputs"]["combined_glb"]]
        return manifest

    overview_target = [0.0, 0.0, args.target_extent * 0.48]
    overview_cam = add_camera("camera_overview_combo", overview_target, args.overview_scale, args.camera)
    render(Path(manifest["outputs"]["overview"]), overview_cam)

    for idx, obj in enumerate(objects):
        b = bounds[idx]
        target = [b["center"][0], b["center"][1], b["center"][2]]
        zoom_scale = float(cases[idx].get("zoom_scale", args.zoom_scale))
        cam = add_camera(f"camera_zoom_{_safe_label(cases[idx]['label'])}", target, zoom_scale, args.camera)
        render(Path(manifest["cases"][idx]["zoom"]["path"]), cam)

    manifest["qa"]["status"] = "rendered"
    manifest["qa"]["actual_outputs"] = [
        manifest["outputs"]["combined_glb"],
        manifest["outputs"]["overview"],
        *[case["zoom"]["path"] for case in manifest["cases"]],
    ]
    return manifest


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, help="Optional five-case JSON manifest.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--resolution", type=int, default=1200)
    parser.add_argument("--samples", type=int, default=96)
    parser.add_argument("--engine", choices=["cycles", "eevee"], default="cycles")
    parser.add_argument("--camera", choices=["iso", "front"], default="iso")
    parser.add_argument("--target-extent", type=float, default=2.25)
    parser.add_argument("--spacing", type=float, default=2.72)
    parser.add_argument("--overview-scale", type=float, default=9.45)
    parser.add_argument("--zoom-scale", type=float, default=2.45)
    parser.add_argument("--exposure", type=float, default=0.55)
    parser.add_argument(
        "--skip-glb-export",
        action="store_true",
        help="Render PNGs without writing another large combined GLB.",
    )
    parser.add_argument(
        "--export-only",
        action="store_true",
        help="Build the combined scene and export GLB, then skip PNG rendering.",
    )
    parser.add_argument("--plan-only", action="store_true")
    return parser.parse_args(argv)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = parse_args(argv)
    args.out_dir = args.out_dir.resolve()
    cases = load_cases(args)
    manifest = build_manifest(cases, args.out_dir, args)
    if not args.plan_only:
        manifest = render_scene(cases, args.out_dir, args, manifest)
    manifest_path = write_manifest(manifest, args.out_dir)
    print(manifest_path)
    print(manifest["outputs"]["combined_glb"])
    print(manifest["outputs"]["overview"])


if __name__ == "__main__":
    main()
