#!/usr/bin/env python3
"""V60 clean-export pass for the L-system short-bough branch candidates.

V59 fixed the topology metrics but the GLB zoom still showed black micro
triangles, scalloped edges, and faceted strips.  This pass is a versioned mesh
export-normalization candidate: it preserves the V59 short-bough silhouette,
remeshes the object-space branch surface into one clean support, smooths
normals, and writes derivative GLBs with explicit metadata.

Run through Blender:

  /Applications/Blender.app/Contents/MacOS/Blender -b --python \
    assets/postprocess_v60_lsystem_branch_clean_export_20260511.py -- \
    --out-dir results/strict_visual_matched_texture_V60_lsystem_branch_clean_export_20260511
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

try:
    import bpy  # type: ignore

    HAS_BLENDER = True
except Exception:  # pragma: no cover - normal Python import path
    bpy = None
    HAS_BLENDER = False


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = (
    ROOT
    / "results"
    / "strict_visual_matched_texture_V59_lsystem_branch_smooth_short_bough_yfork_BD_smoothpost_20260511"
)
DEFAULT_OUT = ROOT / "results" / "strict_visual_matched_texture_V60_lsystem_branch_clean_export_20260511"

DEFAULT_CASES = [
    (
        "V60_lsys_branch_clean_short_bough_lowfrag_B",
        SOURCE_ROOT / "V59_lsys_branch_smooth_short_bough_lowfrag_B_smoothpost" / "textured.glb",
    ),
    (
        "V60_lsys_branch_clean_short_bough_compact_D",
        SOURCE_ROOT / "V59_lsys_branch_smooth_short_bough_compact_D_smoothpost" / "textured.glb",
    ),
]


def require_blender() -> None:
    if not HAS_BLENDER:
        raise SystemExit("This script must be run inside Blender for GLB import/export.")


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_glb(path: Path) -> list:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objects = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    if not objects:
        raise RuntimeError(f"No mesh objects imported from {path}")
    return objects


def join_objects(objects: Iterable):
    objects = list(objects)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    if len(objects) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = "v60_clean_branch_surface"
    return obj


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


def mesh_cleanup_ops(obj, merge_distance: float) -> dict:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    try:
        bpy.ops.mesh.remove_doubles(threshold=float(merge_distance))
        removed = True
    except Exception as exc:
        print(f"[warn] remove_doubles failed: {exc}")
        removed = False
    try:
        bpy.ops.mesh.normals_make_consistent(inside=False)
        normals = True
    except Exception as exc:
        print(f"[warn] normals_make_consistent failed: {exc}")
        normals = False
    bpy.ops.object.mode_set(mode="OBJECT")
    return {"remove_doubles": removed, "normals_consistent": normals}


def make_bark_material(label: str):
    mat = bpy.data.materials.new(f"{label}_matte_bark")
    mat.diffuse_color = (0.47, 0.35, 0.23, 1.0)
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (0.47, 0.35, 0.23, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.82
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def clean_branch_object(
    obj,
    label: str,
    voxel_size: float,
    smooth_iters: int,
    smooth_factor: float,
    merge_distance: float,
    decimate_ratio: float,
) -> dict:
    stats = {
        "object": obj.name,
        "vertices_before": int(len(obj.data.vertices)),
        "faces_before": int(len(obj.data.polygons)),
        "voxel_remesh_applied": False,
        "smooth_applied": False,
        "weighted_normals_applied": False,
        "decimate_applied": False,
    }

    mesh_cleanup_ops(obj, merge_distance=merge_distance)

    remesh = obj.modifiers.new("v60_object_space_voxel_remesh", "REMESH")
    remesh.mode = "VOXEL"
    remesh.voxel_size = float(voxel_size)
    try:
        remesh.adaptivity = 0.0
    except Exception:
        pass
    try:
        remesh.use_smooth_shade = True
    except Exception:
        pass
    stats["voxel_remesh_applied"] = apply_modifier(obj, remesh.name)

    mesh_cleanup = mesh_cleanup_ops(obj, merge_distance=merge_distance)
    stats["mesh_cleanup_after_remesh"] = mesh_cleanup

    if smooth_iters > 0 and smooth_factor > 0:
        smooth = obj.modifiers.new("v60_low_amplitude_laplacian", "LAPLACIANSMOOTH")
        smooth.iterations = int(smooth_iters)
        smooth.lambda_factor = float(smooth_factor)
        smooth.use_x = True
        smooth.use_y = True
        smooth.use_z = True
        try:
            smooth.preserve_volume = True
        except Exception:
            pass
        stats["smooth_applied"] = apply_modifier(obj, smooth.name)

    if 0.0 < decimate_ratio < 1.0:
        decimate = obj.modifiers.new("v60_publication_face_budget_decimate", "DECIMATE")
        decimate.ratio = float(decimate_ratio)
        decimate.use_collapse_triangulate = True
        stats["decimate_applied"] = apply_modifier(obj, decimate.name)

    for poly in obj.data.polygons:
        poly.use_smooth = True
    normals = obj.modifiers.new("v60_weighted_normals", "WEIGHTED_NORMAL")
    normals.keep_sharp = False
    stats["weighted_normals_applied"] = apply_modifier(obj, normals.name)

    obj.data.materials.clear()
    obj.data.materials.append(make_bark_material(label))
    stats["vertices_after"] = int(len(obj.data.vertices))
    stats["faces_after"] = int(len(obj.data.polygons))
    return stats


def export_selected_glb(path: Path, objects: Iterable) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    selected = list(objects)
    bpy.ops.object.select_all(action="DESELECT")
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


def process_case(
    label: str,
    source: Path,
    out_dir: Path,
    voxel_size: float,
    smooth_iters: int,
    smooth_factor: float,
    merge_distance: float,
    decimate_ratio: float,
) -> dict:
    if not source.exists():
        raise FileNotFoundError(source)
    clear_scene()
    objects = import_glb(source)
    obj = join_objects(objects)
    object_stats = clean_branch_object(
        obj,
        label=label,
        voxel_size=voxel_size,
        smooth_iters=smooth_iters,
        smooth_factor=smooth_factor,
        merge_distance=merge_distance,
        decimate_ratio=decimate_ratio,
    )
    case_dir = out_dir / label
    glb_path = case_dir / "textured.glb"
    export_selected_glb(glb_path, [obj])
    row = {
        "label": label,
        "source_glb": str(source),
        "output_glb": str(glb_path),
        "voxel_size": float(voxel_size),
        "smooth_iters": int(smooth_iters),
        "smooth_factor": float(smooth_factor),
        "merge_distance": float(merge_distance),
        "decimate_ratio": float(decimate_ratio),
        "object_count_before_join": len(objects),
        "objects": [object_stats],
        "postprocess_policy": "V60 local object-space mesh export normalization over V59 short-bough GLB; source assets preserved",
        "claim_boundary": "Versioned mesh/export normalization candidate, not 2D seam inpaint or UV backprojection.",
    }
    (case_dir / "v60_clean_export_metadata.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
    print(json.dumps(row, indent=2))
    return row


def parse_case(item: str) -> tuple[str, Path]:
    if "=" not in item:
        raise argparse.ArgumentTypeError("--case must be label=/path/to/textured.glb")
    label, path = item.split("=", 1)
    return label, Path(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", type=parse_case)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--voxel-size", type=float, default=0.0175)
    parser.add_argument("--smooth-iters", type=int, default=5)
    parser.add_argument("--smooth-factor", type=float, default=0.10)
    parser.add_argument("--merge-distance", type=float, default=0.0008)
    parser.add_argument("--decimate-ratio", type=float, default=0.0)
    return parser


def main(argv: list[str] | None = None) -> None:
    require_blender()
    parser = build_parser()
    args = parser.parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    cases = args.case or DEFAULT_CASES
    rows = [
        process_case(
            label,
            path,
            args.out_dir,
            voxel_size=args.voxel_size,
            smooth_iters=args.smooth_iters,
            smooth_factor=args.smooth_factor,
            merge_distance=args.merge_distance,
            decimate_ratio=args.decimate_ratio,
        )
        for label, path in cases
    ]
    manifest = {
        "rows": rows,
        "source": "assets/postprocess_v60_lsystem_branch_clean_export_20260511.py",
        "sdedit_seam_backprojection_available": False,
    }
    (args.out_dir / "v60_clean_export_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    main(argv)
