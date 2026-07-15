#!/usr/bin/env python3
"""Hunyuan-root mesh-space generated-root negative-control baseline.

This starts from Hunyuan3D shape-only one-shot meshes, applies deterministic
grammar S/R/T instance transforms, directly concatenates triangles, and records
metrics. It intentionally performs no generation, latent update, projection,
welding, boolean union, remeshing, or post-hoc repair.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw


ROOT_DIR = Path(__file__).resolve().parents[1]
HUNYUAN_ROOT = ROOT_DIR / "results/publication_hunyuan_recursive_guides_20260510"
DEFAULT_OUT = ROOT_DIR / "results/publication_hunyuan_mesh_space_20260510"


@dataclass(frozen=True)
class RootSpec:
    case: str
    grammar: str
    variant: str
    depth: int
    root_path: Path


def rot_x(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], dtype=np.float64)


def rot_y(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], dtype=np.float64)


def rot_z(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=np.float64)


def translate(v: np.ndarray | list[float]) -> np.ndarray:
    out = np.eye(4, dtype=np.float64)
    out[:3, 3] = np.asarray(v, dtype=np.float64)
    return out


def scale_matrix(s: float) -> np.ndarray:
    out = np.eye(4, dtype=np.float64)
    out[0, 0] = out[1, 1] = out[2, 2] = float(s)
    return out


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT_DIR))
    except Exception:
        return str(path)


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
    scale = max(float(np.max(vmax - vmin)), 1e-9)
    return trimesh.Trimesh(vertices=(vertices - center) / scale, faces=np.asarray(mesh.faces), process=False)


def tree_transforms(depth: int, variant: str) -> list[np.ndarray]:
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
            for yaw_deg, tilt_deg, s, offset in child_specs:
                local_scale = 1.0 if variant == "no_scale" else s
                child = parent @ (
                    translate(np.asarray(offset, dtype=np.float64) * (0.86 ** (level - 1)))
                    @ rot_z(math.radians(yaw_deg) + twist)
                    @ rot_y(math.radians(tilt_deg))
                    @ scale_matrix(local_scale)
                )
                transforms.append(child)
                next_frontier.append(child)
        frontier = next_frontier
    return transforms


def lattice_transforms(depth: int, variant: str) -> list[np.ndarray]:
    transforms: list[np.ndarray] = []
    spacing = 0.83
    for x in range(-depth, depth + 1):
        for y in range(-depth, depth + 1):
            for z in range(-depth, depth + 1):
                shell = abs(x) + abs(y) + abs(z)
                if shell > depth:
                    continue
                s = 1.0 if variant == "no_scale" else max(0.42, 0.82 ** shell)
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
        (-42.0, 18.0, 0.70, [-0.36, -0.04, 0.34]),
        (-18.0, -11.0, 0.64, [-0.18, 0.25, 0.28]),
        (21.0, 14.0, 0.67, [0.21, -0.20, 0.31]),
        (47.0, -17.0, 0.58, [0.39, 0.11, 0.23]),
    ]
    for level in range(1, depth + 1):
        next_frontier: list[np.ndarray] = []
        level_decay = 0.84 ** (level - 1)
        for parent_i, parent in enumerate(frontier):
            roll = math.radians((parent_i % 5 - 2) * 10.0)
            for yaw_deg, pitch_deg, s, offset in child_specs:
                local_scale = 1.0 if variant == "no_scale" else s
                child = parent @ (
                    translate(np.asarray(offset, dtype=np.float64) * level_decay)
                    @ rot_z(math.radians(yaw_deg) + roll)
                    @ rot_y(math.radians(pitch_deg))
                    @ rot_x(math.radians(9.0 * level))
                    @ scale_matrix(local_scale)
                )
                transforms.append(child)
                next_frontier.append(child)
        frontier = next_frontier
    return transforms


def transforms_for(grammar: str, depth: int, variant: str) -> list[np.ndarray]:
    if grammar == "vine_tree":
        return tree_transforms(depth, variant)
    if grammar == "pyrite_lattice":
        return lattice_transforms(depth, variant)
    if grammar == "coral_frontier_branch":
        return coral_frontier_transforms(depth, variant)
    raise ValueError(grammar)


def instantiate(root: trimesh.Trimesh, transforms: list[np.ndarray]) -> trimesh.Trimesh:
    root_vertices = np.asarray(root.vertices, dtype=np.float64)
    root_faces = np.asarray(root.faces, dtype=np.int64)
    vertices: list[np.ndarray] = []
    faces: list[np.ndarray] = []
    offset = 0
    homo = np.concatenate([root_vertices, np.ones((len(root_vertices), 1), dtype=np.float64)], axis=1)
    for matrix in transforms:
        vertices.append((homo @ matrix.T)[:, :3])
        faces.append(root_faces + offset)
        offset += len(root_vertices)
    return trimesh.Trimesh(vertices=np.vstack(vertices), faces=np.vstack(faces), process=False)


def apply_white_material(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    out = mesh.copy()
    try:
        from trimesh.visual.material import PBRMaterial

        out.visual = trimesh.visual.TextureVisuals(
            material=PBRMaterial(
                name="white_pbr_hunyuan_mesh_space_negative_control",
                baseColorFactor=[1.0, 1.0, 1.0, 1.0],
                metallicFactor=0.0,
                roughnessFactor=0.86,
            )
        )
    except Exception:
        out.visual.face_colors = np.tile(np.array([[246, 246, 244, 255]], dtype=np.uint8), (len(out.faces), 1))
    return out


def render_white_preview(mesh: trimesh.Trimesh, out: Path, title: str, max_faces: int = 80_000, size: int = 1280) -> None:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(faces) > max_faces:
        faces = faces[np.linspace(0, len(faces) - 1, max_faces, dtype=np.int64)]
    img = Image.new("RGB", (size, int(size * 0.46)), (244, 244, 241))
    draw = ImageDraw.Draw(img)
    rotations = [
        ("iso", rot_x(math.radians(28.0)) @ rot_z(math.radians(-42.0))),
        ("front", np.eye(4, dtype=np.float64)),
        ("side", rot_y(math.radians(90.0))),
    ]
    light = np.array([0.25, -0.40, 0.88], dtype=np.float64)
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
        y_mid = img.height * 0.52
        for idx in order:
            coords = [
                (float(x0 + panel_w * 0.5 + p[0] * local_scale), float(y_mid - p[1] * local_scale))
                for p in tri[idx, :, :2]
            ]
            shade = 0.42 + 0.58 * max(float(normals[idx] @ light), 0.0)
            c = int(np.clip(255 * shade, 176, 255))
            draw.polygon(coords, fill=(c, c, c))
        draw.text((x0 + 14, 16), name, fill=(45, 45, 45))
    draw.text((14, img.height - 28), title, fill=(45, 45, 45))
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


def write_rows_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = sorted({k for row in rows for k in row.keys() if not isinstance(row.get(k), (list, dict))})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def default_specs(depth: int, variant: str) -> list[RootSpec]:
    return [
        RootSpec("vine", "vine_tree", variant, depth, HUNYUAN_ROOT / "vine_lsystem_grammar/vine_lsystem_grammar_hunyuan_steps30_oct320.glb"),
        RootSpec("pyrite", "pyrite_lattice", variant, depth, HUNYUAN_ROOT / "pyrite_lattice/pyrite_lattice_hunyuan_steps30_oct320.glb"),
        RootSpec("coral", "coral_frontier_branch", variant, depth, HUNYUAN_ROOT / "coral_frontier/coral_frontier_hunyuan_steps30_oct320.glb"),
    ]


def run(args: argparse.Namespace) -> list[dict[str, Any]]:
    metric_module = load_metric_module()
    rows: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    for spec in default_specs(args.depth, args.variant):
        source = load_mesh(spec.root_path)
        limited, face_limited = deterministic_face_limit(source, args.max_root_faces)
        root = normalize_root(limited)
        transforms = transforms_for(spec.grammar, spec.depth, spec.variant)
        mesh = instantiate(root, transforms)
        case_dir = args.out / spec.case / spec.grammar / spec.variant / f"depth_{spec.depth:02d}"
        case_dir.mkdir(parents=True, exist_ok=True)
        stem = f"{spec.case}_{spec.grammar}_{spec.variant}_depth_{spec.depth:02d}"
        obj_path = case_dir / f"{stem}.obj"
        glb_path = case_dir / f"{stem}_white_pbr.glb"
        preview_path = case_dir / f"{stem}_white_preview.png"
        mesh.export(obj_path)
        apply_white_material(mesh).export(glb_path)
        render_white_preview(mesh, preview_path, f"{spec.case} Hunyuan root mesh-space depth={spec.depth}", args.preview_max_faces)
        metric = metric_one(obj_path, stem, metric_module, args)
        row = {
            "case": spec.case,
            "method": "Hunyuan3D mesh-space generated-root",
            "variant": f"{spec.grammar} {spec.variant} depth={spec.depth} direct merge",
            "grammar": spec.grammar,
            "srt_variant": spec.variant,
            "depth": spec.depth,
            "instance_count": len(transforms),
            "copy_repetition_score": 1.0,
            "latent_or_mesh_repair_used": 0,
            "projection_used": 0,
            "weld_boolean_or_remesh_used": 0,
            "root_path": rel(spec.root_path),
            "source_root_vertices": int(len(source.vertices)),
            "source_root_faces": int(len(source.faces)),
            "used_root_vertices": int(len(root.vertices)),
            "used_root_faces": int(len(root.faces)),
            "root_face_limited": bool(face_limited),
            "obj_path": rel(obj_path),
            "glb_path": rel(glb_path),
            "preview_path": rel(preview_path),
            "status": "fragmented_copy_paste",
            "failure_label": "fragmented_or_copy_repetition",
            "notes": "Hunyuan shape-only one-shot root mesh copied by S/R/T and directly concatenated; no generator, projection, weld, boolean, remesh, or repair.",
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
                "fragmentation_score": 1.0 - float(metric.get("primary_largest_component_ratio", 0.0)),
                "bbox_diag": metric.get("bbox_diag", ""),
                "bbox_extent_x": metric.get("bbox_extent_x", ""),
                "bbox_extent_y": metric.get("bbox_extent_y", ""),
                "bbox_extent_z": metric.get("bbox_extent_z", ""),
                "surface_area_est": metric.get("surface_area_est", ""),
            }
        )
        rows.append(row)
        manifest_rows.append(
            {
                "case": spec.case,
                "method": row["method"],
                "variant": row["variant"],
                "status": row["status"],
                "asset_path": row["glb_path"],
                "source_path": row["obj_path"],
                "render_path": row["preview_path"],
                "manifest_path": rel(args.out / "manifest.csv"),
                "notes": row["notes"],
            }
        )
        print(f"wrote {spec.case} instances={len(transforms)} faces={row['faces']}")

    write_rows_csv(args.out / "hunyuan_mesh_space_metrics.csv", rows)
    write_rows_csv(args.out / "manifest.csv", manifest_rows)
    (args.out / "hunyuan_mesh_space_metrics.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = {
        "baseline": "hunyuan_mesh_space_generated_root_negative_control",
        "date": "2026-05-10",
        "rows": len(rows),
        "depth": args.depth,
        "variant": args.variant,
        "max_root_faces": args.max_root_faces,
        "negative_control_claim": "Hunyuan root mesh plus traditional S/R/T copy and direct concat only; no learned recursion or projection.",
        "outputs": {
            "metrics_csv": rel(args.out / "hunyuan_mesh_space_metrics.csv"),
            "manifest_csv": rel(args.out / "manifest.csv"),
        },
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return rows


def self_test() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        root = trimesh.creation.icosphere(subdivisions=1, radius=0.5)
        root_path = tmp / "root.glb"
        root.export(root_path)
        global HUNYUAN_ROOT
        old = HUNYUAN_ROOT
        HUNYUAN_ROOT = tmp
        for case_dir, name in [
            ("vine_lsystem_grammar", "vine_lsystem_grammar_hunyuan_steps30_oct320.glb"),
            ("pyrite_lattice", "pyrite_lattice_hunyuan_steps30_oct320.glb"),
            ("coral_frontier", "coral_frontier_hunyuan_steps30_oct320.glb"),
        ]:
            (tmp / case_dir).mkdir(parents=True, exist_ok=True)
            root.export(tmp / case_dir / name)
        args = argparse.Namespace(out=tmp / "out", depth=1, variant="full_srt", max_root_faces=0, preview_max_faces=5000, occupancy_resolution=32, weld_tolerance=0.0)
        rows = run(args)
        HUNYUAN_ROOT = old
        assert len(rows) == 3
        assert rows[0]["projection_used"] == 0
        assert (tmp / "out/manifest.csv").exists()
    print("self-test passed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--variant", choices=["full_srt", "no_scale"], default="full_srt")
    parser.add_argument("--max-root-faces", type=int, default=8_000)
    parser.add_argument("--preview-max-faces", type=int, default=80_000)
    parser.add_argument("--occupancy-resolution", type=int, default=64)
    parser.add_argument("--weld-tolerance", type=float, default=0.0)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
    else:
        run(args)


if __name__ == "__main__":
    main()
