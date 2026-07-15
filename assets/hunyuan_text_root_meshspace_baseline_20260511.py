#!/usr/bin/env python3
"""Fair Hunyuan text-root mesh-space recursion baseline.

This baseline follows the mesh-space route the paper needs to compare:

1. Use a short text prompt to generate one reusable root primitive image.
2. Use Hunyuan3D shape generation to convert that root image into one root mesh.
3. Copy/rotate/scale/translate the root mesh with a simple grammar.
4. Directly concatenate meshes, with an optional light smoothing upper-bound row.

It intentionally does not condition Hunyuan on a full recursive guide image.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import tempfile
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
import trimesh
from PIL import Image, ImageDraw


try:
    lib = torch.library.Library("torchvision", "DEF")
    lib.define("nms(Tensor dets, Tensor scores, float iou_threshold) -> Tensor")
except Exception:
    pass


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT_DIR / "results/publication_hunyuan_text_root_meshspace_20260511"


@dataclass(frozen=True)
class TextRootCase:
    case_id: str
    family: str
    prompt: str
    grammar: str
    depth: int
    seed: int


CASES = [
    TextRootCase(
        case_id="tree_trunk_branch",
        family="L-system tree",
        prompt="single upright cedar tree trunk with one forked branch segment, isolated 3D object",
        grammar="tree_branching",
        depth=2,
        seed=2026051101,
    ),
    TextRootCase(
        case_id="pyrite_crystal_root",
        family="IFS crystal",
        prompt="single faceted pyrite crystal block, isolated 3D object",
        grammar="pyrite_lattice",
        depth=2,
        seed=2026051102,
    ),
    TextRootCase(
        case_id="coral_branch_root",
        family="DLA coral",
        prompt="single smooth branching coral stem segment, isolated 3D object",
        grammar="coral_frontier",
        depth=2,
        seed=2026051103,
    ),
    TextRootCase(
        case_id="bismuth_crystal_root",
        family="Terraced bismuth crystal",
        prompt="single stepped bismuth crystal block with terraced square facets, isolated 3D object",
        grammar="bismuth_terrace",
        depth=2,
        seed=2026051104,
    ),
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT_DIR))
    except Exception:
        return str(path)


def rot_x(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], dtype=np.float64)


def rot_y(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], dtype=np.float64)


def rot_z(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=np.float64)


def translate(v: list[float] | np.ndarray) -> np.ndarray:
    out = np.eye(4, dtype=np.float64)
    out[:3, 3] = np.asarray(v, dtype=np.float64)
    return out


def scale_matrix(s: float) -> np.ndarray:
    out = np.eye(4, dtype=np.float64)
    out[0, 0] = out[1, 1] = out[2, 2] = float(s)
    return out


def load_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(path, force="scene", process=False)
    if isinstance(loaded, trimesh.Scene):
        meshes = [g for g in loaded.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not meshes:
            raise ValueError(f"no mesh geometry in {path}")
        loaded = trimesh.util.concatenate(meshes)
    if len(loaded.vertices) == 0 or len(loaded.faces) == 0:
        raise ValueError(f"empty mesh: {path}")
    return trimesh.Trimesh(vertices=np.asarray(loaded.vertices), faces=np.asarray(loaded.faces), process=False)


def compact_mesh(vertices: np.ndarray, faces: np.ndarray) -> trimesh.Trimesh:
    used = np.unique(faces.reshape(-1))
    remap = np.full(len(vertices), -1, dtype=np.int64)
    remap[used] = np.arange(len(used), dtype=np.int64)
    return trimesh.Trimesh(vertices=vertices[used], faces=remap[faces], process=False)


def deterministic_face_limit(mesh: trimesh.Trimesh, max_faces: int) -> tuple[trimesh.Trimesh, bool]:
    if max_faces <= 0 or len(mesh.faces) <= max_faces:
        return mesh.copy(), False
    idx = np.linspace(0, len(mesh.faces) - 1, max_faces, dtype=np.int64)
    return compact_mesh(np.asarray(mesh.vertices), np.asarray(mesh.faces)[idx]), True


def rotation_between(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = a / max(np.linalg.norm(a), 1e-12)
    b = b / max(np.linalg.norm(b), 1e-12)
    v = np.cross(a, b)
    c = float(np.clip(np.dot(a, b), -1.0, 1.0))
    if np.linalg.norm(v) < 1e-10:
        if c > 0:
            return np.eye(3, dtype=np.float64)
        return rot_x(math.pi)[:3, :3]
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]], dtype=np.float64)
    return np.eye(3, dtype=np.float64) + vx + vx @ vx * ((1 - c) / max(np.dot(v, v), 1e-12))


def normalize_root(mesh: trimesh.Trimesh, align_long_axis_to_z: bool = True) -> trimesh.Trimesh:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    vertices = vertices - vertices.mean(axis=0, keepdims=True)
    if align_long_axis_to_z and len(vertices) >= 3:
        cov = np.cov(vertices.T)
        vals, vecs = np.linalg.eigh(cov)
        axis = vecs[:, int(np.argmax(vals))]
        if axis[2] < 0:
            axis = -axis
        vertices = vertices @ rotation_between(axis, np.array([0.0, 0.0, 1.0])).T
    vmin = vertices.min(axis=0)
    vmax = vertices.max(axis=0)
    center_xy = (vmin[:2] + vmax[:2]) * 0.5
    vertices[:, 0] -= center_xy[0]
    vertices[:, 1] -= center_xy[1]
    vertices[:, 2] -= vmin[2]
    height = max(float(vertices[:, 2].max()), 1e-9)
    vertices = vertices / height
    return trimesh.Trimesh(vertices=vertices, faces=np.asarray(mesh.faces), process=False)


def tree_branching_transforms(depth: int, variant: str) -> list[np.ndarray]:
    transforms = [np.eye(4, dtype=np.float64)]
    frontier = [np.eye(4, dtype=np.float64)]
    child_specs = [
        (-38.0, 31.0, 0.70, [-0.25, 0.02, 0.78]),
        (0.0, 20.0, 0.72, [0.00, 0.00, 0.86]),
        (38.0, 31.0, 0.70, [0.25, -0.02, 0.78]),
    ]
    for level in range(1, depth + 1):
        next_frontier: list[np.ndarray] = []
        decay = 0.82 ** (level - 1)
        for parent_i, parent in enumerate(frontier):
            twist = math.radians((parent_i % 3 - 1) * 8.0)
            for yaw_deg, tilt_deg, scale, offset in child_specs:
                s = 1.0 if variant == "no_scale" else scale
                child = parent @ (
                    translate(np.asarray(offset, dtype=np.float64) * decay)
                    @ rot_z(math.radians(yaw_deg) + twist)
                    @ rot_y(math.radians(tilt_deg))
                    @ scale_matrix(s)
                )
                transforms.append(child)
                next_frontier.append(child)
        frontier = next_frontier
    return transforms


def pyrite_lattice_transforms(depth: int, variant: str) -> list[np.ndarray]:
    transforms: list[np.ndarray] = []
    spacing = 0.78
    for x in range(-depth, depth + 1):
        for y in range(-depth, depth + 1):
            for z in range(-depth, depth + 1):
                shell = abs(x) + abs(y) + abs(z)
                if shell > depth:
                    continue
                s = 1.0 if variant == "no_scale" else max(0.46, 0.82 ** shell)
                transforms.append(
                    translate([x * spacing, y * spacing, z * spacing])
                    @ rot_z(math.radians(22.5 * ((x - y + z) % 8)))
                    @ rot_x(math.radians(12.0 * ((x + 2 * y) % 5)))
                    @ scale_matrix(s)
                )
    transforms.sort(key=lambda m: (np.linalg.norm(m[:3, 3]), m[0, 3], m[1, 3], m[2, 3]))
    return transforms


def coral_frontier_transforms(depth: int, variant: str) -> list[np.ndarray]:
    transforms = [np.eye(4, dtype=np.float64)]
    frontier = [np.eye(4, dtype=np.float64)]
    child_specs = [
        (-42.0, 18.0, 0.70, [-0.34, -0.04, 0.40]),
        (-18.0, -11.0, 0.64, [-0.18, 0.24, 0.34]),
        (21.0, 14.0, 0.67, [0.21, -0.20, 0.36]),
        (47.0, -17.0, 0.58, [0.37, 0.11, 0.28]),
    ]
    for level in range(1, depth + 1):
        next_frontier: list[np.ndarray] = []
        decay = 0.84 ** (level - 1)
        for parent_i, parent in enumerate(frontier):
            roll = math.radians((parent_i % 5 - 2) * 10.0)
            for yaw_deg, pitch_deg, scale, offset in child_specs:
                s = 1.0 if variant == "no_scale" else scale
                child = parent @ (
                    translate(np.asarray(offset, dtype=np.float64) * decay)
                    @ rot_z(math.radians(yaw_deg) + roll)
                    @ rot_y(math.radians(pitch_deg))
                    @ rot_x(math.radians(8.0 * level))
                    @ scale_matrix(s)
                )
                transforms.append(child)
                next_frontier.append(child)
        frontier = next_frontier
    return transforms


def bismuth_terrace_transforms(depth: int, variant: str) -> list[np.ndarray]:
    transforms: list[np.ndarray] = [np.eye(4, dtype=np.float64)]
    spacing = 0.58
    for level in range(1, depth + 1):
        radius = level
        z = 0.38 * level
        scale = 1.0 if variant == "no_scale" else max(0.44, 0.78 ** level)
        coords: list[tuple[int, int]] = []
        for x in range(-radius, radius + 1):
            coords.append((x, -radius))
            coords.append((x, radius))
        for y in range(-radius + 1, radius):
            coords.append((-radius, y))
            coords.append((radius, y))
        for i, (x, y) in enumerate(coords):
            yaw = math.radians(90.0 * ((i + level) % 4))
            transforms.append(
                translate([x * spacing * (0.86 ** level), y * spacing * (0.86 ** level), z])
                @ rot_z(yaw)
                @ rot_x(math.radians(6.0 * ((x - y) % 3 - 1)))
                @ scale_matrix(scale)
            )
    transforms.sort(key=lambda m: (m[2, 3], abs(m[0, 3]) + abs(m[1, 3]), m[0, 3], m[1, 3]))
    return transforms


def transforms_for(grammar: str, depth: int, variant: str) -> list[np.ndarray]:
    if grammar == "tree_branching":
        return tree_branching_transforms(depth, variant)
    if grammar == "pyrite_lattice":
        return pyrite_lattice_transforms(depth, variant)
    if grammar == "coral_frontier":
        return coral_frontier_transforms(depth, variant)
    if grammar == "bismuth_terrace":
        return bismuth_terrace_transforms(depth, variant)
    raise ValueError(grammar)


def instantiate(root: trimesh.Trimesh, transforms: list[np.ndarray]) -> trimesh.Trimesh:
    root_vertices = np.asarray(root.vertices, dtype=np.float64)
    root_faces = np.asarray(root.faces, dtype=np.int64)
    homo = np.concatenate([root_vertices, np.ones((len(root_vertices), 1), dtype=np.float64)], axis=1)
    vertices: list[np.ndarray] = []
    faces: list[np.ndarray] = []
    offset = 0
    for matrix in transforms:
        vertices.append((homo @ matrix.T)[:, :3])
        faces.append(root_faces + offset)
        offset += len(root_vertices)
    return trimesh.Trimesh(vertices=np.vstack(vertices), faces=np.vstack(faces), process=False)


def smooth_mesh(mesh: trimesh.Trimesh, iterations: int) -> trimesh.Trimesh:
    out = mesh.copy()
    if iterations <= 0:
        return out
    try:
        trimesh.smoothing.filter_laplacian(out, lamb=0.18, iterations=iterations)
    except Exception:
        pass
    return out


def apply_material(mesh: trimesh.Trimesh, color: tuple[int, int, int, int]) -> trimesh.Trimesh:
    out = mesh.copy()
    try:
        from trimesh.visual.material import PBRMaterial

        rgba = [c / 255.0 for c in color]
        out.visual = trimesh.visual.TextureVisuals(
            material=PBRMaterial(
                name="hunyuan_text_root_meshspace_white_pbr",
                baseColorFactor=rgba,
                metallicFactor=0.0,
                roughnessFactor=0.82,
            )
        )
    except Exception:
        out.visual.face_colors = np.tile(np.array([color], dtype=np.uint8), (len(out.faces), 1))
    return out


def render_preview(mesh: trimesh.Trimesh, out: Path, title: str, max_faces: int = 90_000, size: int = 1280) -> None:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(faces) > max_faces:
        faces = faces[np.linspace(0, len(faces) - 1, max_faces, dtype=np.int64)]
    img = Image.new("RGB", (size, int(size * 0.50)), (246, 247, 248))
    draw = ImageDraw.Draw(img)
    rotations = [
        ("iso", rot_x(math.radians(28.0)) @ rot_z(math.radians(-42.0))),
        ("front", np.eye(4, dtype=np.float64)),
        ("side", rot_y(math.radians(90.0))),
    ]
    light = np.array([0.25, -0.45, 0.86], dtype=np.float64)
    light = light / np.linalg.norm(light)
    panel_w = size // 3
    for panel, (name, matrix) in enumerate(rotations):
        pts = vertices @ matrix[:3, :3].T
        center = (pts.min(axis=0) + pts.max(axis=0)) * 0.5
        span = max(float(np.max(pts.max(axis=0) - pts.min(axis=0))), 1e-9)
        pts = (pts - center) / span
        tri = pts[faces]
        normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        norms = np.linalg.norm(normals, axis=1)
        valid = norms > 1e-10
        tri = tri[valid]
        normals = normals[valid] / norms[valid, None]
        order = np.argsort(tri[:, :, 2].mean(axis=1))
        x0 = panel * panel_w
        local_scale = panel_w * 0.38
        y_mid = img.height * 0.53
        for idx in order:
            coords = [
                (float(x0 + panel_w * 0.5 + p[0] * local_scale), float(y_mid - p[1] * local_scale))
                for p in tri[idx, :, :2]
            ]
            shade = 0.45 + 0.55 * max(float(normals[idx] @ light), 0.0)
            c = int(np.clip(255 * shade, 172, 255))
            draw.polygon(coords, fill=(c, c, c))
        draw.text((x0 + 16, 16), name, fill=(44, 48, 52))
    draw.text((16, img.height - 30), title, fill=(44, 48, 52))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def load_metric_module() -> Any:
    path = ROOT_DIR / "assets/recursive_growth_mesh_metrics.py"
    spec = importlib.util.spec_from_file_location("recursive_growth_mesh_metrics", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load metric module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def metric_one(path: Path, label: str, metric_module: Any, args: argparse.Namespace) -> dict[str, Any]:
    metric_args = argparse.Namespace(
        occupancy_resolution=args.occupancy_resolution,
        box_resolutions=[8, 16, 32, args.occupancy_resolution],
        sample_limit=200_000,
        weld_tolerance=args.weld_tolerance,
        primary_connectivity="occupancy",
    )
    row = metric_module.metric_one(path, label, metric_args)
    row["file_size_mb"] = round(path.stat().st_size / (1024 * 1024), 6)
    return row


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = sorted({k for row in rows for k in row.keys() if not isinstance(row.get(k), (list, dict))})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def generate_root_assets(args: argparse.Namespace, cases: list[TextRootCase]) -> list[dict[str, Any]]:
    from hy3dgen.rembg import BackgroundRemover
    from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
    from hy3dgen.text2image import HunyuanDiTPipeline

    t2i = None
    shape_pipe = None
    remover = None
    root_rows: list[dict[str, Any]] = []
    for case in cases:
        case_dir = args.out / case.case_id
        root_image = case_dir / "text_root_image.png"
        root_glb = case_dir / "hunyuan_text_root.glb"
        root_row_path = case_dir / "root_generation.json"
        case_dir.mkdir(parents=True, exist_ok=True)
        row: dict[str, Any] = {
            "case_id": case.case_id,
            "family": case.family,
            "prompt": case.prompt,
            "grammar": case.grammar,
            "depth": case.depth,
            "seed": case.seed,
            "root_image": rel(root_image),
            "root_glb": rel(root_glb),
            "status": "pending",
        }
        if root_glb.exists() and root_image.exists() and not args.force_roots:
            row["status"] = "existing"
            root_rows.append(row)
            root_row_path.write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")
            continue
        try:
            if t2i is None:
                t0 = time.time()
                t2i = HunyuanDiTPipeline(args.t2i_model, device=args.device)
                row["t2i_load_sec"] = round(time.time() - t0, 2)
            if shape_pipe is None:
                t0 = time.time()
                shape_pipe = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
                    args.shape_model,
                    subfolder=args.shape_subfolder,
                    variant=args.shape_variant,
                )
                row["shape_load_sec"] = round(time.time() - t0, 2)
            if remover is None:
                remover = BackgroundRemover()

            t0 = time.time()
            image = t2i(case.prompt, seed=case.seed)
            image.save(root_image)
            row["t2i_sec"] = round(time.time() - t0, 2)

            t0 = time.time()
            image_for_shape = remover(Image.open(root_image).convert("RGBA"))
            generator = torch.manual_seed(case.seed + 1000)
            mesh = shape_pipe(
                image=image_for_shape,
                num_inference_steps=args.steps,
                octree_resolution=args.octree_resolution,
                num_chunks=args.num_chunks,
                guidance_scale=args.guidance_scale,
                generator=generator,
                output_type="trimesh",
                enable_pbar=True,
            )[0]
            if isinstance(mesh, list):
                mesh = mesh[0]
            mesh.export(root_glb)
            row.update(
                {
                    "status": "ok",
                    "shape_sec": round(time.time() - t0, 2),
                    "root_vertices": int(len(mesh.vertices)) if hasattr(mesh, "vertices") else "",
                    "root_faces": int(len(mesh.faces)) if hasattr(mesh, "faces") else "",
                    "root_glb_mb": round(root_glb.stat().st_size / 1024 / 1024, 6),
                }
            )
        except Exception as exc:
            traceback.print_exc()
            row.update({"status": "fail", "error_type": type(exc).__name__, "error": str(exc)})
        root_rows.append(row)
        root_row_path.write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")
        print("ROOT_DONE", json.dumps(row, ensure_ascii=False), flush=True)
    write_csv(args.out / "text_root_generation_manifest.csv", root_rows)
    (args.out / "text_root_generation_manifest.json").write_text(json.dumps(root_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    return root_rows


def build_meshspace(args: argparse.Namespace, cases: list[TextRootCase]) -> list[dict[str, Any]]:
    metric_module = load_metric_module()
    rows: list[dict[str, Any]] = []
    for case in cases:
        root_glb = args.out / case.case_id / "hunyuan_text_root.glb"
        if not root_glb.exists():
            rows.append(
                {
                    "case_id": case.case_id,
                    "status": "missing_root",
                    "prompt": case.prompt,
                    "root_glb": rel(root_glb),
                    "notes": "No Hunyuan text-root GLB was available, so mesh-space copy was not run.",
                }
            )
            continue
        source = load_mesh(root_glb)
        limited, face_limited = deterministic_face_limit(source, args.max_root_faces)
        root = normalize_root(
            limited,
            align_long_axis_to_z=case.grammar in {"tree_branching", "coral_frontier", "bismuth_terrace"},
        )
        transforms = transforms_for(case.grammar, case.depth, args.variant)
        direct = instantiate(root, transforms)
        for smooth_iter in [0, args.smooth_iterations]:
            if smooth_iter == 0:
                variant_name = f"{case.grammar}_{args.variant}_depth{case.depth:02d}_direct"
                mesh = direct
                repair_used = 0
                status = "fragmented_copy_paste"
            else:
                variant_name = f"{case.grammar}_{args.variant}_depth{case.depth:02d}_laplacian{smooth_iter}"
                mesh = smooth_mesh(direct, smooth_iter)
                repair_used = 1
                status = "smoothed_copy_paste"
            case_dir = args.out / case.case_id / variant_name
            case_dir.mkdir(parents=True, exist_ok=True)
            obj_path = case_dir / f"{variant_name}.obj"
            glb_path = case_dir / f"{variant_name}_white_pbr.glb"
            preview_path = case_dir / f"{variant_name}_preview.png"
            mesh.export(obj_path)
            apply_material(mesh, (246, 246, 244, 255)).export(glb_path)
            render_preview(mesh, preview_path, f"{case.case_id} Hunyuan text-root mesh copy {variant_name}", args.preview_max_faces)
            metric = metric_one(obj_path, variant_name, metric_module, args)
            row: dict[str, Any] = {
                "case_id": case.case_id,
                "family": case.family,
                "method": "Hunyuan text-root mesh-space recursion",
                "variant": variant_name,
                "prompt": case.prompt,
                "grammar": case.grammar,
                "depth": case.depth,
                "instance_count": len(transforms),
                "root_glb": rel(root_glb),
                "source_root_vertices": int(len(source.vertices)),
                "source_root_faces": int(len(source.faces)),
                "used_root_vertices": int(len(root.vertices)),
                "used_root_faces": int(len(root.faces)),
                "root_face_limited": bool(face_limited),
                "obj_path": rel(obj_path),
                "glb_path": rel(glb_path),
                "preview_path": rel(preview_path),
                "copy_repetition_score": 1.0,
                "projection_used": 0,
                "generator_calls_after_root": 0,
                "weld_boolean_or_remesh_used": 0,
                "latent_update_used": 0,
                "post_copy_smoothing_iterations": smooth_iter,
                "latent_or_mesh_repair_used": repair_used,
                "status": status,
                "failure_label": "copy_repetition_without_recursive_state",
                "notes": "Text-generated Hunyuan root primitive copied by S/R/T and directly concatenated; smoothing row is only a mesh-route upper-bound, not learned recursion.",
            }
            row.update(
                {
                    "vertices": metric.get("vertices", ""),
                    "faces": metric.get("faces", ""),
                    "file_size_mb": metric.get("file_size_mb", ""),
                    "raw_component_count": metric.get("component_count", ""),
                    "largest_component_vertex_ratio": metric.get("largest_component_vertex_ratio", ""),
                    "welded_component_count": metric.get("welded_component_count", ""),
                    "largest_welded_component_vertex_ratio": metric.get("largest_welded_component_vertex_ratio", ""),
                    "occupancy_component_count_6n": metric.get("occupancy_component_count_6n", ""),
                    "largest_occupancy_component_ratio_6n": metric.get("largest_occupancy_component_ratio_6n", ""),
                    "LCR": metric.get("primary_largest_component_ratio", ""),
                    "bbox_diag": metric.get("bbox_diag", ""),
                    "bbox_extent_x": metric.get("bbox_extent_x", ""),
                    "bbox_extent_y": metric.get("bbox_extent_y", ""),
                    "bbox_extent_z": metric.get("bbox_extent_z", ""),
                    "surface_area_est": metric.get("surface_area_est", ""),
                }
            )
            rows.append(row)
            print("MESHSPACE_DONE", json.dumps(row, ensure_ascii=False), flush=True)
    write_csv(args.out / "hunyuan_text_root_meshspace_metrics.csv", rows)
    (args.out / "hunyuan_text_root_meshspace_metrics.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = {
        "date": "2026-05-11",
        "baseline": "fair_hunyuan_text_root_meshspace_recursion",
        "rows": len(rows),
        "definition": "text prompt -> HunyuanDiT root image -> Hunyuan3D root shape -> S/R/T root copy -> direct mesh concat, optional smoothing reported separately",
        "not_used": ["full recursive guide image", "latent update", "projection", "boolean union", "weld", "remesh", "post-root generator calls"],
        "outputs": {
            "root_manifest": rel(args.out / "text_root_generation_manifest.csv"),
            "metrics": rel(args.out / "hunyuan_text_root_meshspace_metrics.csv"),
        },
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return rows


def selected_cases(args: argparse.Namespace) -> list[TextRootCase]:
    if args.case == "all":
        return CASES
    return [case for case in CASES if case.case_id == args.case]


def self_test() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        case = CASES[0]
        case_dir = tmp / case.case_id
        case_dir.mkdir(parents=True)
        root = trimesh.creation.cylinder(radius=0.08, height=1.0, sections=10)
        root.export(case_dir / "hunyuan_text_root.glb")
        args = argparse.Namespace(
            out=tmp,
            variant="full_srt",
            max_root_faces=0,
            smooth_iterations=1,
            preview_max_faces=5000,
            occupancy_resolution=32,
            weld_tolerance=0.0,
        )
        rows = build_meshspace(args, [case])
        assert len(rows) == 2
        assert rows[0]["copy_repetition_score"] == 1.0
        assert (tmp / "hunyuan_text_root_meshspace_metrics.csv").exists()
    print("self-test passed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--case", choices=["all"] + [case.case_id for case in CASES], default="all")
    parser.add_argument("--mode", choices=["all", "roots", "meshspace", "self-test"], default="all")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--t2i-model", default="Tencent-Hunyuan/HunyuanDiT-v1.1-Diffusers-Distilled")
    parser.add_argument("--shape-model", default="tencent/Hunyuan3D-2")
    parser.add_argument("--shape-subfolder", default="hunyuan3d-dit-v2-0")
    parser.add_argument("--shape-variant", default="fp16")
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--octree-resolution", type=int, default=320)
    parser.add_argument("--num-chunks", type=int, default=12000)
    parser.add_argument("--guidance-scale", type=float, default=5.0)
    parser.add_argument("--variant", choices=["full_srt", "no_scale"], default="full_srt")
    parser.add_argument("--max-root-faces", type=int, default=12000)
    parser.add_argument("--smooth-iterations", type=int, default=3)
    parser.add_argument("--preview-max-faces", type=int, default=90_000)
    parser.add_argument("--occupancy-resolution", type=int, default=64)
    parser.add_argument("--weld-tolerance", type=float, default=0.0)
    parser.add_argument("--force-roots", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    cases = selected_cases(args)
    if args.mode == "self-test":
        self_test()
        return
    if args.mode in {"all", "roots"}:
        generate_root_assets(args, cases)
    if args.mode in {"all", "meshspace"}:
        build_meshspace(args, cases)


if __name__ == "__main__":
    main()
