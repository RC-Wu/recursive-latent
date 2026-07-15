#!/usr/bin/env python3
"""Render seam-aware candidates with object-space procedural PBR materials.

This is a visual QA path for cases where Trellis UV/material export introduces
visible islands.  Geometry still comes from the grammar/junction-collar batch;
the material is a continuous object-space shader, so it does not create UV
seams at recursive junctions.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
sys.path.insert(0, str(SCRIPT_DIR))

import matched_camera_zoom_render_20260510 as zoom  # noqa: E402

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover - exercised only by Blender
    bpy = None


DEFAULT_CASES = [
    {
        "label": "S01a_root_procedural_bark_pbr",
        "mesh": str(
            PROJECT_ROOT
            / "results/seam_aware_texturing_batch_v2_20260510_remote"
            / "S01a_root_continuous_bark_grain_lowcontrast_steps8_tex2048_seed20295710_xformers/textured.glb"
        ),
        "material": "root_bark",
    },
    {
        "label": "S02c_coral_procedural_ivory_pbr",
        "mesh": str(
            PROJECT_ROOT
            / "results/seam_aware_texturing_batch_v2_20260510_remote"
            / "S02c_coral_bone_ridge_plain_steps8_tex2048_seed20295716_xformers/textured.glb"
        ),
        "material": "coral_ivory",
    },
    {
        "label": "S03a_pyrite_procedural_facets_pbr",
        "mesh": str(
            PROJECT_ROOT
            / "results/seam_aware_texturing_batch_v2_20260510_remote"
            / "S03a_pyrite_brushed_facets_lowcontrast_steps8_tex2048_seed20295714_xformers/textured.glb"
        ),
        "material": "pyrite_facets",
    },
]


def _set_input(node, name: str, value) -> None:
    if name in node.inputs:
        node.inputs[name].default_value = value


def _hex_color(rgb: tuple[int, int, int], alpha: float = 1.0) -> tuple[float, float, float, float]:
    return (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0, alpha)


def make_object_noise_material(
    name: str,
    dark: tuple[int, int, int],
    mid: tuple[int, int, int],
    light: tuple[int, int, int],
    *,
    scale: float,
    detail: float,
    roughness: float,
    metallic: float,
    bump_strength: float,
    bump_distance: float,
):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return mat

    tex_coord = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    ramp = nodes.new("ShaderNodeValToRGB")
    bump_noise = nodes.new("ShaderNodeTexNoise")
    bump = nodes.new("ShaderNodeBump")

    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = detail
    noise.inputs["Roughness"].default_value = 0.58
    bump_noise.inputs["Scale"].default_value = scale * 1.9
    bump_noise.inputs["Detail"].default_value = min(detail + 2.0, 15.0)
    bump_noise.inputs["Roughness"].default_value = 0.62

    ramp.color_ramp.elements[0].position = 0.18
    ramp.color_ramp.elements[0].color = _hex_color(dark)
    ramp.color_ramp.elements[1].position = 0.92
    ramp.color_ramp.elements[1].color = _hex_color(light)
    middle = ramp.color_ramp.elements.new(0.55)
    middle.color = _hex_color(mid)

    links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tex_coord.outputs["Object"], bump_noise.inputs["Vector"])
    links.new(bump_noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    _set_input(bsdf, "Roughness", roughness)
    _set_input(bsdf, "Metallic", metallic)
    _set_input(bump, "Strength", bump_strength)
    _set_input(bump, "Distance", bump_distance)
    return mat


def material_for(kind: str):
    if kind == "coral_ivory":
        return make_object_noise_material(
            "object_space_coral_ivory_pbr",
            (160, 126, 94),
            (210, 182, 142),
            (238, 220, 185),
            scale=32.0,
            detail=11.0,
            roughness=0.82,
            metallic=0.0,
            bump_strength=0.17,
            bump_distance=0.045,
        )
    if kind == "pyrite_facets":
        return make_object_noise_material(
            "object_space_pyrite_facets_pbr",
            (82, 68, 42),
            (144, 113, 58),
            (213, 174, 84),
            scale=18.0,
            detail=6.0,
            roughness=0.36,
            metallic=0.78,
            bump_strength=0.07,
            bump_distance=0.025,
        )
    return make_object_noise_material(
        "object_space_root_bark_pbr",
        (72, 45, 28),
        (128, 82, 43),
        (176, 124, 70),
        scale=24.0,
        detail=12.0,
        roughness=0.76,
        metallic=0.0,
        bump_strength=0.12,
        bump_distance=0.035,
    )


def apply_material(obj, kind: str) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(material_for(kind))
    smooth = kind != "pyrite_facets"
    for poly in obj.data.polygons:
        poly.use_smooth = smooth
    if smooth:
        mod = obj.modifiers.new("procedural_pbr_weighted_normals", "WEIGHTED_NORMAL")
        mod.keep_sharp = True


def load_cases(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return DEFAULT_CASES
    payload = json.loads(path.read_text(encoding="utf-8"))
    return list(payload["cases"] if isinstance(payload, dict) else payload)


def render_case(case: dict[str, str], args: argparse.Namespace) -> dict:
    mesh = Path(case["mesh"])
    zoom.clear_scene()
    zoom.setup_world(args.resolution, args.samples, args.engine)
    obj = zoom.import_mesh(mesh)
    zoom.normalize_object(obj)
    apply_material(obj, case.get("material", "root_bark"))
    zoom.add_lighting()
    vertices = zoom.world_vertices(obj)
    case_plan = zoom.plan_case(
        label=case["label"],
        mesh=mesh,
        vertices=vertices,
        out_dir=args.out_dir,
        resolution=args.resolution,
        zoom_levels=args.zoom_levels,
        material_mode=f"procedural:{case.get('material', 'root_bark')}",
        target_source="render_mesh",
    )

    cameras = {}
    overview = case_plan["overview"]
    cameras["overview"] = zoom.add_camera(overview["target"], overview["ortho_scale"], args.camera)
    zoom.render_to(Path(overview["path"]), cameras["overview"])
    for panel in case_plan["zooms"]:
        cameras[panel["id"]] = zoom.add_camera(panel["target"], panel["ortho_scale"], args.camera)
        zoom.render_to(Path(panel["path"]), cameras[panel["id"]])

    child_by_parent: dict[str, list[dict]] = {}
    for panel in case_plan["zooms"]:
        child_by_parent.setdefault(panel["callout_parent"], []).append(panel)
    case_plan["callouts"] = []
    for parent_id, children in child_by_parent.items():
        if parent_id == "overview":
            parent_path = Path(overview["path"])
            annotated_path = Path(overview["annotated_path"])
        else:
            parent_zoom = next(panel for panel in case_plan["zooms"] if panel["id"] == parent_id)
            parent_path = Path(parent_zoom["path"])
            if parent_zoom["annotated_path"] is None:
                continue
            annotated_path = Path(parent_zoom["annotated_path"])
        rects = [
            zoom.projected_rect(cameras[parent_id], child["target"], child["ortho_scale"], args.resolution)
            for child in children
        ]
        case_plan["callouts"].append(
            {
                "parent_id": parent_id,
                "parent_path": str(parent_path),
                "annotated_path": str(annotated_path),
                "rects": [list(rect) for rect in rects],
                "labels": [child["id"] for child in children],
            }
        )
    return case_plan


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--resolution", type=int, default=1400)
    parser.add_argument("--samples", type=int, default=96)
    parser.add_argument("--zoom-levels", type=int, default=2)
    parser.add_argument("--camera", choices=["iso", "front", "side"], default="iso")
    parser.add_argument("--engine", choices=["cycles", "eevee", "workbench"], default="cycles")
    return parser.parse_args(argv)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = parse_args(argv)
    if not zoom.HAS_BLENDER:
        raise SystemExit("Run this script with Blender.")
    cases = [render_case(case, args) for case in load_cases(args.manifest)]
    plan = {
        "strict_requirements": {
            "white_background": True,
            "square_overview": True,
            "object_space_procedural_pbr": True,
            "uv_material_islands_avoided_by_design": True,
            "claim_scope": "visual QA / paper candidate; material field is procedural PBR, not Trellis UV texture proof",
        },
        "run_config": {
            "resolution": args.resolution,
            "samples": args.samples,
            "camera": args.camera,
            "engine": args.engine,
        },
        "cases": cases,
    }
    path = zoom.write_plan(plan, args.out_dir)
    print(path)
    for case in cases:
        print(case["comparison_path"])


if __name__ == "__main__":
    main()
