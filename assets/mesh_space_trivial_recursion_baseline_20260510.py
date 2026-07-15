#!/usr/bin/env python3
"""Strict mesh-space recursion negative-control baseline.

The baseline starts from a generated root mesh, applies traditional
scale/rotate/translate instance transforms from two grammars, directly
concatenates the resulting triangle meshes, and writes OBJ/GLB, metrics, and
white-material previews.  It intentionally performs no latent-space update, no
projection repair, no topology welding, and no post-merge cleanup.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT_DIR / "results/mesh_space_trivial_baseline_20260510"
DEFAULT_VINE_ROOT = ROOT_DIR / "inputs/connected_best_expansion_20260509/root_vine_connected_control.obj"
DEFAULT_PYRITE_ROOT = ROOT_DIR / "inputs/connected_best_expansion_20260509/pyrite_crystal_lattice_cluster.obj"


@dataclass(frozen=True)
class CaseSpec:
    grammar: str
    variant: str
    depth: int
    root_path: Path


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = np.arange(n, dtype=np.int64)
        self.size = np.ones(n, dtype=np.int64)

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = int(self.parent[x])
        return x

    def union(self, a: int, b: int) -> None:
        ra = self.find(int(a))
        rb = self.find(int(b))
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]


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


def compact_mesh(vertices: np.ndarray, faces: np.ndarray) -> trimesh.Trimesh:
    used = np.unique(faces.reshape(-1))
    remap = np.full(len(vertices), -1, dtype=np.int64)
    remap[used] = np.arange(len(used), dtype=np.int64)
    return trimesh.Trimesh(vertices=vertices[used], faces=remap[faces], process=False)


def load_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(path, force="mesh", process=False)
    if isinstance(loaded, trimesh.Scene):
        meshes = [g for g in loaded.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not meshes:
            raise ValueError(f"no mesh geometry in {path}")
        loaded = trimesh.util.concatenate(meshes)
    if len(loaded.vertices) == 0 or len(loaded.faces) == 0:
        raise ValueError(f"empty mesh: {path}")
    return trimesh.Trimesh(vertices=np.asarray(loaded.vertices), faces=np.asarray(loaded.faces), process=False)


def deterministic_face_limit(mesh: trimesh.Trimesh, max_faces: int) -> tuple[trimesh.Trimesh, bool]:
    if max_faces <= 0 or len(mesh.faces) <= max_faces:
        return mesh.copy(), False
    idx = np.linspace(0, len(mesh.faces) - 1, max_faces, dtype=np.int64)
    reduced = compact_mesh(np.asarray(mesh.vertices), np.asarray(mesh.faces)[idx])
    return reduced, True


def normalize_root(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    vmin = vertices.min(axis=0)
    vmax = vertices.max(axis=0)
    center = (vmin + vmax) * 0.5
    extent = float(np.max(vmax - vmin))
    vertices = (vertices - center) / max(extent, 1e-9)
    return trimesh.Trimesh(vertices=vertices, faces=np.asarray(mesh.faces), process=False)


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
                local = (
                    translate(np.asarray(offset, dtype=np.float64) * (0.86 ** (level - 1)))
                    @ rot_z(math.radians(yaw_deg) + twist)
                    @ rot_y(math.radians(tilt_deg))
                    @ scale_matrix(local_scale)
                )
                child = parent @ local
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
                yaw = math.radians(22.5 * ((x - y + z) % 8))
                pitch = math.radians(12.0 * ((x + 2 * y) % 5))
                m = translate([x * spacing, y * spacing, z * spacing]) @ rot_z(yaw) @ rot_x(pitch) @ scale_matrix(s)
                transforms.append(m)
    transforms.sort(key=lambda m: (np.linalg.norm(m[:3, 3]), m[0, 3], m[1, 3], m[2, 3]))
    return transforms


def transforms_for(grammar: str, depth: int, variant: str) -> list[np.ndarray]:
    if grammar == "vine_tree":
        return tree_transforms(depth, variant)
    if grammar == "pyrite_lattice":
        return lattice_transforms(depth, variant)
    raise ValueError(grammar)


def instantiate(root: trimesh.Trimesh, transforms: list[np.ndarray]) -> trimesh.Trimesh:
    root_vertices = np.asarray(root.vertices, dtype=np.float64)
    root_faces = np.asarray(root.faces, dtype=np.int64)
    vertices = []
    faces = []
    offset = 0
    ones = np.ones((len(root_vertices), 1), dtype=np.float64)
    homo = np.concatenate([root_vertices, ones], axis=1)
    for matrix in transforms:
        vertices.append((homo @ matrix.T)[:, :3])
        faces.append(root_faces + offset)
        offset += len(root_vertices)
    return trimesh.Trimesh(vertices=np.vstack(vertices), faces=np.vstack(faces), process=False)


def component_stats(vertices: np.ndarray, faces: np.ndarray) -> dict[str, float | int]:
    uf = UnionFind(len(vertices))
    for a, b, c in faces:
        uf.union(int(a), int(b))
        uf.union(int(b), int(c))
        uf.union(int(c), int(a))
    roots = np.fromiter((uf.find(i) for i in range(len(vertices))), dtype=np.int64, count=len(vertices))
    _, counts = np.unique(roots, return_counts=True)
    largest = int(counts.max()) if len(counts) else 0
    return {
        "component_count": int(len(counts)),
        "largest_component_vertices": largest,
        "largest_component_vertex_ratio": float(largest / max(len(vertices), 1)),
        "small_component_count_lt100": int(np.sum(counts < 100)),
    }


def surface_area(vertices: np.ndarray, faces: np.ndarray, sample_limit: int = 250_000) -> float:
    sample = faces
    scale = 1.0
    if len(sample) > sample_limit:
        idx = np.linspace(0, len(sample) - 1, sample_limit, dtype=np.int64)
        sample = sample[idx]
        scale = len(faces) / len(sample)
    tri = vertices[sample]
    areas = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
    return float(np.sum(areas) * scale)


def mesh_metrics(mesh: trimesh.Trimesh, spec: CaseSpec, instance_count: int, root_info: dict) -> dict:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    vmin = vertices.min(axis=0)
    vmax = vertices.max(axis=0)
    extent = vmax - vmin
    row: dict[str, object] = {
        "grammar": spec.grammar,
        "variant": spec.variant,
        "depth": spec.depth,
        "root_path": str(spec.root_path),
        "source_root_vertices": root_info["source_vertices"],
        "source_root_faces": root_info["source_faces"],
        "used_root_vertices": root_info["used_vertices"],
        "used_root_faces": root_info["used_faces"],
        "root_face_limited": root_info["face_limited"],
        "instance_count": instance_count,
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
        "bbox_extent_x": float(extent[0]),
        "bbox_extent_y": float(extent[1]),
        "bbox_extent_z": float(extent[2]),
        "bbox_diag": float(np.linalg.norm(extent)),
        "bbox_volume": float(np.prod(np.maximum(extent, 1e-9))),
        "surface_area_est": surface_area(vertices, faces),
        "watertight_after_merge": bool(mesh.is_watertight),
        "euler_number_after_merge": int(mesh.euler_number),
    }
    row.update(component_stats(vertices, faces))
    row["fragmentation_score"] = float(1.0 - float(row["largest_component_vertex_ratio"]))
    row["copy_repetition_score"] = 1.0
    row["latent_or_mesh_repair_used"] = 0
    return row


def apply_white_material(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    out = mesh.copy()
    try:
        from trimesh.visual.material import PBRMaterial

        out.visual = trimesh.visual.TextureVisuals(
            material=PBRMaterial(
                name="strict_white_pbr_negative_control",
                baseColorFactor=[1.0, 1.0, 1.0, 1.0],
                metallicFactor=0.0,
                roughnessFactor=0.82,
            )
        )
    except Exception:
        out.visual.face_colors = np.tile(np.array([[245, 245, 242, 255]], dtype=np.uint8), (len(out.faces), 1))
    return out


def view_rotation(view: str) -> np.ndarray:
    if view == "front":
        return rot_x(math.radians(0.0))[:3, :3]
    if view == "side":
        return rot_y(math.radians(90.0))[:3, :3]
    if view == "top":
        return rot_x(math.radians(90.0))[:3, :3]
    return (rot_x(math.radians(28.0)) @ rot_z(math.radians(-42.0)))[:3, :3]


def render_white_preview(mesh: trimesh.Trimesh, out: Path, title: str, max_faces: int = 70_000, size: int = 1280) -> None:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(faces) > max_faces:
        faces = faces[np.linspace(0, len(faces) - 1, max_faces, dtype=np.int64)]

    margin = 44
    panel_w = size // 3
    img = Image.new("RGB", (size, int(size * 0.46)), (244, 244, 241))
    draw = ImageDraw.Draw(img)
    views = ["iso", "front", "side"]
    light = np.array([0.25, -0.40, 0.88], dtype=np.float64)
    light = light / np.linalg.norm(light)
    for panel, view in enumerate(views):
        rot = view_rotation(view)
        pts = vertices @ rot.T
        center = (pts.min(axis=0) + pts.max(axis=0)) * 0.5
        span = max(float(np.max(pts.max(axis=0) - pts.min(axis=0))), 1e-9)
        pts = (pts - center) / span
        tri = pts[faces]
        normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        norms = np.linalg.norm(normals, axis=1)
        valid = norms > 1e-10
        tri = tri[valid]
        normals = normals[valid] / norms[valid, None]
        depth = tri[:, :, 2].mean(axis=1)
        order = np.argsort(depth)
        x0 = panel * panel_w
        local_scale = (panel_w - 2 * margin) * 0.88
        y_mid = img.height * 0.52
        for idx in order:
            poly = tri[idx, :, :2]
            coords = [
                (
                    float(x0 + panel_w * 0.5 + p[0] * local_scale),
                    float(y_mid - p[1] * local_scale),
                )
                for p in poly
            ]
            shade = 0.42 + 0.58 * max(float(normals[idx] @ light), 0.0)
            c = int(np.clip(255 * shade, 176, 255))
            draw.polygon(coords, fill=(c, c, c))
        draw.text((x0 + 14, 16), view, fill=(45, 45, 45))
    draw.text((14, img.height - 28), title, fill=(45, 45, 45))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def write_rows_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = sorted({k for row in rows for k in row.keys() if not isinstance(row.get(k), (list, dict))})
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fieldnames})


def run_baseline(args: argparse.Namespace) -> list[dict]:
    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    source_roots = {
        "vine_tree": Path(args.vine_root),
        "pyrite_lattice": Path(args.pyrite_root),
    }
    root_cache: dict[str, tuple[trimesh.Trimesh, dict]] = {}
    for grammar, path in source_roots.items():
        source = load_mesh(path)
        limited, face_limited = deterministic_face_limit(source, args.max_root_faces)
        root = normalize_root(limited)
        root_cache[grammar] = (
            root,
            {
                "source_vertices": int(len(source.vertices)),
                "source_faces": int(len(source.faces)),
                "used_vertices": int(len(root.vertices)),
                "used_faces": int(len(root.faces)),
                "face_limited": bool(face_limited),
            },
        )

    rows: list[dict] = []
    for grammar in ["vine_tree", "pyrite_lattice"]:
        root, root_info = root_cache[grammar]
        for variant in ["full_srt", "no_scale"]:
            for depth in range(args.max_depth + 1):
                spec = CaseSpec(grammar=grammar, variant=variant, depth=depth, root_path=source_roots[grammar])
                transforms = transforms_for(grammar, depth, variant)
                mesh = instantiate(root, transforms)
                case_dir = out_dir / grammar / variant / f"depth_{depth:02d}"
                case_dir.mkdir(parents=True, exist_ok=True)
                obj_path = case_dir / f"{grammar}_{variant}_depth_{depth:02d}.obj"
                glb_path = case_dir / f"{grammar}_{variant}_depth_{depth:02d}_white_pbr.glb"
                png_path = case_dir / f"{grammar}_{variant}_depth_{depth:02d}_white_preview.png"
                mesh.export(obj_path)
                apply_white_material(mesh).export(glb_path)
                render_white_preview(mesh, png_path, f"{grammar} {variant} depth={depth}", args.preview_max_faces)
                row = mesh_metrics(mesh, spec, len(transforms), root_info)
                row.update({"obj_path": str(obj_path), "glb_path": str(glb_path), "preview_path": str(png_path)})
                rows.append(row)
                print(f"wrote {grammar} {variant} depth={depth} instances={len(transforms)}")

    write_rows_csv(out_dir / "mesh_space_trivial_metrics.csv", rows)
    (out_dir / "mesh_space_trivial_metrics.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    summary = {
        "baseline": "mesh_space_trivial_recursion_negative_control",
        "date": "2026-05-10",
        "root_sources": {k: str(v) for k, v in source_roots.items()},
        "max_depth": args.max_depth,
        "max_root_faces": args.max_root_faces,
        "variants": ["full_srt", "no_scale"],
        "negative_control_claim": "mesh-space instance transforms plus direct merge; no generation or repair after root mesh",
        "rows": len(rows),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    return rows


def self_test() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        root = trimesh.creation.box(extents=(1.0, 0.4, 0.6))
        root_path = tmp / "box_root.obj"
        root.export(root_path)
        args = argparse.Namespace(
            out=tmp / "out",
            vine_root=root_path,
            pyrite_root=root_path,
            max_depth=1,
            max_root_faces=0,
            preview_max_faces=10_000,
        )
        rows = run_baseline(args)
        assert len(rows) == 8, len(rows)
        tree_full = [r for r in rows if r["grammar"] == "vine_tree" and r["variant"] == "full_srt" and r["depth"] == 1][0]
        lattice_full = [
            r for r in rows if r["grammar"] == "pyrite_lattice" and r["variant"] == "full_srt" and r["depth"] == 1
        ][0]
        assert tree_full["instance_count"] == 4, tree_full["instance_count"]
        assert lattice_full["instance_count"] == 7, lattice_full["instance_count"]
        assert tree_full["vertices"] == tree_full["used_root_vertices"] * tree_full["instance_count"]
        assert Path(tree_full["obj_path"]).exists()
        assert Path(tree_full["glb_path"]).exists()
        assert Path(tree_full["preview_path"]).exists()
        assert tree_full["latent_or_mesh_repair_used"] == 0
    print("self-test passed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--vine-root", type=Path, default=DEFAULT_VINE_ROOT)
    parser.add_argument("--pyrite-root", type=Path, default=DEFAULT_PYRITE_ROOT)
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--max-root-faces", type=int, default=12_000)
    parser.add_argument("--preview-max-faces", type=int, default=70_000)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return args
    if args.max_depth < 0:
        raise SystemExit("--max-depth must be non-negative")
    return args


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
    else:
        run_baseline(args)


if __name__ == "__main__":
    main()
