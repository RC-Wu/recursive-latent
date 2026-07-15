#!/usr/bin/env python3
"""Trellis2 generated-root mesh-space recursion for Experiment 3.

Input roots are Trellis2 root-guide identity meshes.  The baseline then applies
deterministic S/R/T copy schedules and directly concatenates triangles.  This is
a mesh-space negative control, not PS-RSLG and not a latent update.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "results/experiment3_sparse_latent_vs_meshspace_20260511"


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


def normalize_root(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    vmin = vertices.min(axis=0)
    vmax = vertices.max(axis=0)
    center = (vmin + vmax) * 0.5
    extent = max(float(np.max(vmax - vmin)), 1e-9)
    vertices = (vertices - center) / extent
    return trimesh.Trimesh(vertices=vertices, faces=np.asarray(mesh.faces), process=False)


def tree_branching_transforms(depth: int) -> list[np.ndarray]:
    transforms = [np.eye(4, dtype=np.float64)]
    frontier = [np.eye(4, dtype=np.float64)]
    child_specs = [
        (-36.0, 24.0, 0.70, [-0.23, 0.00, 0.58]),
        (0.0, 31.0, 0.66, [0.00, 0.05, 0.67]),
        (36.0, 24.0, 0.70, [0.23, 0.00, 0.58]),
    ]
    for level in range(1, depth + 1):
        next_frontier: list[np.ndarray] = []
        for parent_i, parent in enumerate(frontier):
            twist = (parent_i % 3 - 1) * math.radians(9.0)
            for yaw_deg, tilt_deg, scale, offset in child_specs:
                child = parent @ (
                    translate(np.asarray(offset, dtype=np.float64) * (0.86 ** (level - 1)))
                    @ rot_z(math.radians(yaw_deg) + twist)
                    @ rot_y(math.radians(tilt_deg))
                    @ scale_matrix(scale)
                )
                transforms.append(child)
                next_frontier.append(child)
        frontier = next_frontier
    return transforms


def pyrite_lattice_transforms(depth: int) -> list[np.ndarray]:
    transforms: list[np.ndarray] = []
    spacing = 0.83
    for x in range(-depth, depth + 1):
        for y in range(-depth, depth + 1):
            for z in range(-depth, depth + 1):
                shell = abs(x) + abs(y) + abs(z)
                if shell > depth:
                    continue
                scale = max(0.42, 0.82 ** shell)
                transforms.append(
                    translate([x * spacing, y * spacing, z * spacing])
                    @ rot_z(math.radians(22.5 * ((x - y + z) % 8)))
                    @ rot_x(math.radians(12.0 * ((x + 2 * y) % 5)))
                    @ scale_matrix(scale)
                )
    transforms.sort(key=lambda m: (np.linalg.norm(m[:3, 3]), m[0, 3], m[1, 3], m[2, 3]))
    return transforms


def coral_frontier_transforms(depth: int) -> list[np.ndarray]:
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
        for parent_i, parent in enumerate(frontier):
            roll = math.radians((parent_i % 5 - 2) * 10.0)
            for yaw_deg, pitch_deg, scale, offset in child_specs:
                child = parent @ (
                    translate(np.asarray(offset, dtype=np.float64) * (0.84 ** (level - 1)))
                    @ rot_z(math.radians(yaw_deg) + roll)
                    @ rot_y(math.radians(pitch_deg))
                    @ rot_x(math.radians(8.0 * level))
                    @ scale_matrix(scale)
                )
                transforms.append(child)
                next_frontier.append(child)
        frontier = next_frontier
    return transforms


def transforms_for(grammar: str, depth: int) -> list[np.ndarray]:
    if grammar == "tree_branching":
        return tree_branching_transforms(depth)
    if grammar == "pyrite_lattice":
        return pyrite_lattice_transforms(depth)
    if grammar == "coral_frontier":
        return coral_frontier_transforms(depth)
    raise ValueError(grammar)


def instantiate(root: trimesh.Trimesh, transforms: list[np.ndarray]) -> trimesh.Trimesh:
    vertices = np.asarray(root.vertices, dtype=np.float64)
    faces = np.asarray(root.faces, dtype=np.int64)
    homo = np.concatenate([vertices, np.ones((len(vertices), 1), dtype=np.float64)], axis=1)
    out_vertices: list[np.ndarray] = []
    out_faces: list[np.ndarray] = []
    offset = 0
    for matrix in transforms:
        out_vertices.append((homo @ matrix.T)[:, :3])
        out_faces.append(faces + offset)
        offset += len(vertices)
    return trimesh.Trimesh(vertices=np.vstack(out_vertices), faces=np.vstack(out_faces), process=False)


def apply_material(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    out = mesh.copy()
    out.visual.face_colors = np.tile(np.array([[245, 245, 242, 255]], dtype=np.uint8), (len(out.faces), 1))
    return out


def render_preview(mesh: trimesh.Trimesh, out: Path, title: str, max_faces: int = 80_000) -> None:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(faces) > max_faces:
        faces = faces[np.linspace(0, len(faces) - 1, max_faces, dtype=np.int64)]
    width, height = 1280, 590
    img = Image.new("RGB", (width, height), (244, 244, 241))
    draw = ImageDraw.Draw(img)
    views = [("iso", rot_x(math.radians(28.0)) @ rot_z(math.radians(-42.0))), ("front", np.eye(4)), ("side", rot_y(math.radians(90.0)))]
    light = np.array([0.25, -0.40, 0.88], dtype=np.float64)
    light = light / np.linalg.norm(light)
    panel_w = width // 3
    for panel, (name, matrix) in enumerate(views):
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
        scale = panel_w * 0.38
        for idx in order:
            coords = [
                (float(x0 + panel_w * 0.5 + p[0] * scale), float(height * 0.52 - p[1] * scale))
                for p in tri[idx, :, :2]
            ]
            shade = 0.43 + 0.57 * max(float(normals[idx] @ light), 0.0)
            color = int(np.clip(255 * shade, 174, 255))
            draw.polygon(coords, fill=(color, color, color))
        draw.text((x0 + 14, 16), name, fill=(45, 45, 45))
    draw.text((14, height - 28), title, fill=(45, 45, 45))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def load_metrics_module() -> Any:
    path = ROOT / "assets/recursive_growth_mesh_metrics.py"
    spec = importlib.util.spec_from_file_location("recursive_growth_mesh_metrics", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def metric_one(path: Path, label: str, module: Any) -> dict[str, Any]:
    args = argparse.Namespace(
        occupancy_resolution=64,
        box_resolutions=[8, 16, 32, 64],
        sample_limit=200_000,
        weld_tolerance=0.0,
        primary_connectivity="occupancy",
    )
    row = module.metric_one(path, label, args)
    row["file_size_mb"] = round(path.stat().st_size / (1024 * 1024), 6)
    return row


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = sorted({k for row in rows for k in row if not isinstance(row.get(k), (list, dict))})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--condition-manifest", type=Path, default=DEFAULT_BASE / "conditions/condition_manifest.csv")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_BASE / "trellis2_generatedroot_meshcopy")
    parser.add_argument("--cases", nargs="*", default=[])
    parser.add_argument("--max-root-faces", type=int, default=12_000)
    args = parser.parse_args()

    metric_module = load_metrics_module()
    wanted = set(args.cases)
    rows: list[dict[str, Any]] = []
    for case in read_manifest(args.condition_manifest):
        case_short = case["case_short"]
        if wanted and case_short not in wanted:
            continue
        root_mesh = args.base_dir / "trellis2_latentcopy" / f"{case_short}_root_seed2026061201" / "identity" / "mesh.obj"
        if not root_mesh.exists():
            rows.append({"case_short": case_short, "status": "missing_root", "root_mesh": str(root_mesh)})
            continue
        source = load_mesh(root_mesh)
        limited, face_limited = deterministic_face_limit(source, args.max_root_faces)
        root = normalize_root(limited)
        transforms = transforms_for(case["grammar"], int(case["depth"]))
        mesh = instantiate(root, transforms)
        out = args.out_dir / case_short / f"{case_short}_{case['grammar']}_depth{int(case['depth']):02d}_direct"
        out.mkdir(parents=True, exist_ok=True)
        obj = out / "mesh.obj"
        glb = out / "mesh_white.glb"
        png = out / "preview.png"
        mesh.export(obj)
        apply_material(mesh).export(glb)
        render_preview(mesh, png, f"{case_short} generated-root mesh-copy")
        metric = metric_one(obj, f"trellis2_generatedroot_meshcopy__{case_short}", metric_module)
        metric.update(
            {
                "case_short": case_short,
                "case_id": case["case_id"],
                "method": "Trellis2 generated-root mesh-space recursion",
                "variant": "identity_root_full_srt_depth02_direct",
                "status": "fragmented_copy_paste",
                "grammar": case["grammar"],
                "depth": int(case["depth"]),
                "root_mesh": str(root_mesh),
                "obj_path": str(obj),
                "glb_path": str(glb),
                "preview_path": str(png),
                "source_root_vertices": int(len(source.vertices)),
                "source_root_faces": int(len(source.faces)),
                "used_root_vertices": int(len(root.vertices)),
                "used_root_faces": int(len(root.faces)),
                "root_face_limited": bool(face_limited),
                "instance_count": len(transforms),
                "copy_repetition_score": 1.0,
                "projection_used": 0,
                "latent_update_used": 0,
                "generator_calls_after_root": 0,
                "weld_boolean_or_remesh_used": 0,
                "post_copy_smoothing_iterations": 0,
                "failure_label": "generated_root_mesh_copy_without_recursive_state",
            }
        )
        rows.append(metric)
        print(f"wrote {case_short} instances={len(transforms)} faces={len(mesh.faces)}")
    write_csv(args.out_dir / "trellis2_generatedroot_meshcopy_metrics.csv", rows)
    (args.out_dir / "trellis2_generatedroot_meshcopy_metrics.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "out": str(args.out_dir)}, indent=2))


if __name__ == "__main__":
    main()
