#!/usr/bin/env python3
"""Export smoothed V49 L-system branch GLB candidates.

This script is intentionally a local, versioned post-export QA pass. It keeps
the original remote Trellis2 GLBs untouched and writes derivative assets with
metadata so we can decide whether the V49 blocker is mainly surface/export
faceting or still a grammar-shape issue.

Run through Blender:

  /Applications/Blender.app/Contents/MacOS/Blender -b --python \
    assets/postprocess_v49_lsystem_branch_smooth_export_20260511.py -- \
    --out-dir results/strict_visual_matched_texture_V49_lsystem_branch_highres_smooth_yfork_smoothpost_20260511
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

try:
    import bpy  # type: ignore
except Exception as exc:  # pragma: no cover - run inside Blender
    raise SystemExit("This script must run inside Blender") from exc


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "results" / "strict_visual_matched_texture_V49_lsystem_branch_highres_smooth_yfork_naturalization_20260511_remote"
DEFAULT_OUT = ROOT / "results" / "strict_visual_matched_texture_V49_lsystem_branch_highres_smooth_yfork_smoothpost_20260511"

DEFAULT_CASES = [
    (
        "V49_lsys_branch_highres_smooth_yfork_lowfrag_B_smoothpost",
        SOURCE_ROOT / "V49_lsys_branch_highres_smooth_yfork_lowfrag_B_steps8_tex2048_seed20303513_xformers" / "textured.glb",
    ),
    (
        "V49_lsys_branch_highres_smooth_yfork_slim_D_smoothpost",
        SOURCE_ROOT / "V49_lsys_branch_highres_smooth_yfork_slim_D_steps8_tex2048_seed20303515_xformers" / "textured.glb",
    ),
]


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def mesh_objects() -> list:
    return [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]


def import_glb(path: Path) -> list:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objects = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    if not objects:
        raise RuntimeError(f"No mesh objects imported from {path}")
    return objects


def apply_modifier(obj, modifier_name: str) -> bool:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    try:
        bpy.ops.object.modifier_apply(modifier=modifier_name)
        return True
    except Exception as exc:
        print(f"[warn] could not apply {modifier_name} on {obj.name}: {exc}")
        return False


def smooth_object(obj, subdiv_levels: int, smooth_factor: float, smooth_iters: int) -> dict:
    stats = {
        "name": obj.name,
        "vertices_before": int(len(obj.data.vertices)),
        "faces_before": int(len(obj.data.polygons)),
        "subdivision_applied": False,
        "laplacian_smooth_applied": False,
        "weighted_normals_applied": False,
    }

    for poly in obj.data.polygons:
        poly.use_smooth = True

    if subdiv_levels > 0:
        mod = obj.modifiers.new("v49_surface_subdivision", "SUBSURF")
        mod.levels = int(subdiv_levels)
        mod.render_levels = int(subdiv_levels)
        mod.subdivision_type = "CATMULL_CLARK"
        stats["subdivision_applied"] = apply_modifier(obj, mod.name)

    if smooth_iters > 0 and smooth_factor > 0:
        mod = obj.modifiers.new("v49_low_amplitude_laplacian", "LAPLACIANSMOOTH")
        mod.iterations = int(smooth_iters)
        mod.lambda_factor = float(smooth_factor)
        mod.use_x = True
        mod.use_y = True
        mod.use_z = True
        try:
            mod.preserve_volume = True
        except Exception:
            pass
        stats["laplacian_smooth_applied"] = apply_modifier(obj, mod.name)

    for poly in obj.data.polygons:
        poly.use_smooth = True
    mod = obj.modifiers.new("v49_weighted_normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = False
    stats["weighted_normals_applied"] = apply_modifier(obj, mod.name)

    stats["vertices_after"] = int(len(obj.data.vertices))
    stats["faces_after"] = int(len(obj.data.polygons))
    return stats


def export_selected_glb(path: Path, objects: Iterable) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    selected = list(objects)
    for obj in selected:
        obj.select_set(True)
    if selected:
        bpy.context.view_layer.objects.active = selected[0]
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
    )


def process_case(label: str, source: Path, out_dir: Path, subdiv_levels: int, smooth_factor: float, smooth_iters: int) -> dict:
    if not source.exists():
        raise FileNotFoundError(source)
    clear_scene()
    objects = import_glb(source)
    object_stats = [smooth_object(obj, subdiv_levels, smooth_factor, smooth_iters) for obj in objects]
    case_dir = out_dir / label
    glb_path = case_dir / "textured.glb"
    export_selected_glb(glb_path, objects)
    row = {
        "label": label,
        "source_glb": str(source),
        "output_glb": str(glb_path),
        "subdiv_levels": int(subdiv_levels),
        "smooth_factor": float(smooth_factor),
        "smooth_iters": int(smooth_iters),
        "object_count": len(objects),
        "objects": object_stats,
        "postprocess_policy": "local derivative V49 export smoothing; original Trellis2 GLB preserved",
        "claim_boundary": "QA/export-surface smoothing candidate, not a new remote generation and not 2D seam inpaint backprojection",
    }
    (case_dir / "smoothpost_metadata.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
    print(json.dumps(row, indent=2))
    return row


def parse_case(item: str) -> tuple[str, Path]:
    if "=" not in item:
        raise argparse.ArgumentTypeError("--case must be label=/path/to/textured.glb")
    label, path = item.split("=", 1)
    return label, Path(path)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", type=parse_case)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--subdiv-levels", type=int, default=1)
    parser.add_argument("--smooth-factor", type=float, default=0.18)
    parser.add_argument("--smooth-iters", type=int, default=2)
    args = parser.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    cases = args.case or DEFAULT_CASES
    rows = [
        process_case(label, path, args.out_dir, args.subdiv_levels, args.smooth_factor, args.smooth_iters)
        for label, path in cases
    ]
    manifest = {
        "rows": rows,
        "source": "assets/postprocess_v49_lsystem_branch_smooth_export_20260511.py",
    }
    (args.out_dir / "smoothpost_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    main(argv)
