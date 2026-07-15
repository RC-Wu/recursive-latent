#!/usr/bin/env python3
"""Render clean white-background Experiment 3 geometry panels."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
BASE = ROOT / "results/experiment3_sparse_latent_vs_meshspace_20260511"
OUT = BASE / "visual_matrix_clean"

CASE_ORDER = ["tree_crown", "root_fan", "vine", "spider_rosette", "coral", "pyrite", "bismuth", "radial_ornament"]
METHOD_ORDER = [
    "target",
    "trellis2_oneshot_image",
    "trellis2_root_latentcopy",
    "trellis2_generatedroot_meshcopy",
    "hunyuan_root_meshcopy",
    "ps_rslg",
]

CASE_COLORS = {
    "tree_crown": ((63, 112, 68), (177, 207, 122)),
    "root_fan": ((92, 82, 60), (197, 173, 114)),
    "vine": ((72, 97, 56), (193, 205, 139)),
    "spider_rosette": ((67, 110, 73), (176, 218, 143)),
    "coral": ((142, 47, 42), (230, 111, 88)),
    "pyrite": ((109, 82, 37), (220, 178, 83)),
    "bismuth": ((86, 94, 144), (223, 150, 86)),
    "radial_ornament": ((76, 95, 125), (194, 183, 96)),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def repo_path(path: str) -> Path | None:
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return p if p.exists() else None


def pick_row(rows: list[dict[str, str]], case: str, method: str) -> dict[str, str] | None:
    candidates = [r for r in rows if r.get("case_short") == case and r.get("method_id") == method]
    if not candidates:
        return None

    def score(row: dict[str, str]) -> tuple[int, int, int, int]:
        metrics = row.get("metrics_source", "")
        exp3 = int("experiment3_sparse_latent_vs_meshspace_20260511" in metrics)
        asset = int(bool(mesh_path_for_row(row)))
        status = int(row.get("route_status") in {"ready", "fragmented_copy_paste"})
        ready = {"yes": 3, "needs_visual_qa": 2, "supplement": 1}.get(row.get("ready_for_main", ""), 0)
        return (asset, exp3, status, ready)

    return sorted(candidates, key=score, reverse=True)[0]


def mesh_path_for_row(row: dict[str, str]) -> Path | None:
    for key in ["source_path", "asset_path"]:
        p = repo_path(row.get(key, ""))
        if p and p.suffix.lower() in {".obj", ".glb", ".gltf", ".ply", ".stl"}:
            return p
    return None


def target_mesh_path(rows: list[dict[str, str]], case: str) -> Path | None:
    row = pick_row(rows, case, "ps_rslg")
    return mesh_path_for_row(row) if row else None


def image_fallback_for_row(row: dict[str, str] | None) -> Path | None:
    if not row:
        return None
    for key in ["asset_path", "source_path", "render_path", "preview_path"]:
        p = repo_path(row.get(key, ""))
        if p and p.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            return p
    return None


def load_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(str(path), force="scene", process=False)
    if isinstance(loaded, trimesh.Scene):
        meshes = [g for g in loaded.geometry.values() if isinstance(g, trimesh.Trimesh) and len(g.vertices)]
        if not meshes:
            raise ValueError(f"no mesh geometry in {path}")
        loaded = trimesh.util.concatenate(meshes)
    if not isinstance(loaded, trimesh.Trimesh) or len(loaded.vertices) == 0 or len(loaded.faces) == 0:
        raise ValueError(f"empty mesh: {path}")
    return trimesh.Trimesh(vertices=np.asarray(loaded.vertices), faces=np.asarray(loaded.faces), process=False)


def rot_x(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float64)


def rot_z(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float64)


def render_mesh(path: Path, out: Path, case: str, size: int, max_faces: int) -> None:
    mesh = load_mesh(path)
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(faces) > max_faces:
        faces = faces[np.linspace(0, len(faces) - 1, max_faces, dtype=np.int64)]
    rot = rot_x(math.radians(27.0)) @ rot_z(math.radians(-42.0))
    pts = vertices @ rot.T
    center = (pts.min(axis=0) + pts.max(axis=0)) * 0.5
    span = max(float(np.max(pts.max(axis=0) - pts.min(axis=0))), 1e-9)
    pts = (pts - center) / span
    tri = pts[faces]
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    norm = np.linalg.norm(normals, axis=1)
    valid = norm > 1e-12
    tri = tri[valid]
    normals = normals[valid] / norm[valid, None]
    z = tri[:, :, 2].mean(axis=1)
    order = np.argsort(z)
    z_norm = (z - z.min()) / max(float(z.max() - z.min()), 1e-9)
    low, high = CASE_COLORS.get(case, ((92, 92, 92), (210, 210, 210)))
    low_arr = np.array(low, dtype=np.float64)
    high_arr = np.array(high, dtype=np.float64)
    light = np.array([0.35, -0.45, 0.82], dtype=np.float64)
    light /= np.linalg.norm(light)
    img = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(img)
    scale = size * 0.76
    for idx in order:
        coords = [(float(size * 0.5 + p[0] * scale), float(size * 0.53 - p[1] * scale)) for p in tri[idx, :, :2]]
        base = low_arr * (1.0 - z_norm[idx]) + high_arr * z_norm[idx]
        shade = 0.38 + 0.62 * max(float(normals[idx] @ light), 0.0)
        color = tuple(int(v) for v in np.clip(base * shade, 0, 255))
        draw.polygon(coords, fill=color)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def fit_image(path: Path | None, size: int) -> Image.Image:
    canvas = Image.new("RGB", (size, size), "white")
    if not path or not path.exists():
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((1, 1, size - 2, size - 2), outline=(225, 225, 225))
        return canvas
    img = Image.open(path).convert("RGB")
    img.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas.paste(img, ((size - img.width) // 2, (size - img.height) // 2))
    return canvas


def render_panel(rows: list[dict[str, str]], case: str, method: str, size: int, max_faces: int) -> Path | None:
    panel = OUT / "panels" / f"{case}__{method}.png"
    if method == "target":
        path = target_mesh_path(rows, case)
        if path:
            render_mesh(path, panel, case, size, max_faces)
            return panel
        cond = repo_path(f"results/experiment3_sparse_latent_vs_meshspace_20260511/conditions/{case}/target_guide.png")
        fit_image(cond, size).save(panel)
        return panel
    row = pick_row(rows, case, method)
    path = mesh_path_for_row(row) if row else None
    if path:
        render_mesh(path, panel, case, size, max_faces)
        return panel
    fallback = image_fallback_for_row(row)
    if method == "ps_rslg" and case == "spider_rosette":
        spider = ROOT / "results/botanical_tree_root_recursive_remote_20260511i_pull/blender_qa_20260511i/plant_broad_basal_d4_iso.png"
        fallback = spider if spider.exists() else fallback
    fit_image(fallback, size).save(panel)
    return panel


def draw_centered(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font: ImageFont.ImageFont) -> None:
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
    except Exception:
        w = len(text) * 6
    draw.text((x - w // 2, y), text, fill=(30, 30, 30), font=font)


def compose(rows: list[dict[str, str]], cases: list[str], out: Path, size: int, labels: bool) -> None:
    gap = 10
    label_h = 28 if labels else 0
    cols = len(METHOD_ORDER)
    width = cols * size + (cols + 1) * gap
    height = len(cases) * (size + label_h + gap) + gap
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("Times New Roman.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    for r, case in enumerate(cases):
        y = gap + r * (size + label_h + gap)
        for c, method in enumerate(METHOD_ORDER):
            x = gap + c * (size + gap)
            panel = OUT / "panels" / f"{case}__{method}.png"
            canvas.paste(fit_image(panel, size), (x, y))
            if labels:
                draw_centered(draw, x + size // 2, y + size + 4, f"({chr(97 + c)})", font)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    print(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", nargs="*", default=CASE_ORDER)
    parser.add_argument("--size", type=int, default=320)
    parser.add_argument("--max-faces", type=int, default=65000)
    parser.add_argument("--out", type=Path, default=OUT / "experiment3_clean_matrix_8case_20260511.png")
    parser.add_argument("--no-labels", action="store_true")
    args = parser.parse_args()
    rows = read_csv(BASE / "experiment3_master_manifest.csv")
    for case in args.cases:
        for method in METHOD_ORDER:
            render_panel(rows, case, method, args.size, args.max_faces)
    compose(rows, args.cases, args.out, args.size, not args.no_labels)


if __name__ == "__main__":
    main()
