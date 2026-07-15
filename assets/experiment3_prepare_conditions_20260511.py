#!/usr/bin/env python3
"""Prepare explicit condition images for Experiment 3 baselines.

For every main case, write:

* target_guide.png: a generous full-object PS-RSLG guide for one-shot methods.
* root_guide.png: a root/source mesh render for root-first latent-copy methods.

The script uses only explicit paths from the Experiment 3 manifest.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_OUT = ROOT / "results/experiment3_sparse_latent_vs_meshspace_20260511/conditions"


CASES: list[dict[str, str]] = [
    {
        "case_id": "V25_sc_tree_crown_tapered_B",
        "case_short": "tree_crown",
        "root_mesh": "results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/inputs/V25_sc_tree_crown_tapered_B/V25_sc_tree_crown_tapered_B.obj",
        "target_guide": "visuals/strict_visual_matched_texture_V25_root_sc_refine_zoom_white_20260510/V25_sc_tapered_B/overview_raw.png",
        "prompt": "recursive space colonization tree crown with branching canopy, connected trunk and fine terminal branches",
        "grammar": "tree_branching",
        "depth": "2",
    },
    {
        "case_id": "V25_lsys_root_fan_smooth_anchorD_stable",
        "case_short": "root_fan",
        "root_mesh": "results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/inputs/V25_lsys_root_fan_smooth_anchorD_stable/V25_lsys_root_fan_smooth_anchorD_stable.obj",
        "target_guide": "visuals/strict_visual_matched_texture_V25_root_sc_refine_zoom_white_20260510/V25_root_smooth_D/overview_raw.png",
        "prompt": "recursive root fan with many connected branching rootlets and tapering roots",
        "grammar": "tree_branching",
        "depth": "2",
    },
    {
        "case_id": "v15_lsys_climbing_vine_d6_smooth_leafy_curl",
        "case_short": "vine",
        "root_mesh": "results/strict_visual_matched_texture_v15_plants_ifs_seed20278100_20260510_remote/inputs/v15_lsys_climbing_vine_d6_smooth_leafy_curl/v15_lsys_climbing_vine_d6_smooth_leafy_curl.obj",
        "target_guide": "visuals/strict_visual_matched_texture_v15_plants_ifs_zoom_20260510/v15_lsys_climbing_vine_d6_smooth_leafy_curl/overview_raw.png",
        "prompt": "recursive climbing vine with curling stems, tendrils, and attached leaves",
        "grammar": "tree_branching",
        "depth": "2",
    },
    {
        "case_id": "spider_rosette_publication_broad_20260511h",
        "case_short": "spider_rosette",
        "root_mesh": "results/fern_root_candidates_20260511h/spider_rosette_publication_broad_20260511h/spider_rosette_publication_broad_20260511h.obj",
        "target_guide": "results/botanical_tree_root_recursive_remote_20260511i_pull/blender_qa_20260511i/plant_broad_basal_d4_iso.png",
        "prompt": "recursive spider plant rosette with connected basal crown and repeated strap leaves",
        "grammar": "tree_branching",
        "depth": "2",
    },
    {
        "case_id": "V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA",
        "case_short": "coral",
        "root_mesh": "results/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510_remote/inputs/V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA/V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA.obj",
        "target_guide": "visuals/strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510/V24_dla_staghorn_frontier/overview_raw.png",
        "prompt": "recursive staghorn coral frontier with branching porous tips and connected base",
        "grammar": "coral_frontier",
        "depth": "2",
    },
    {
        "case_id": "V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA",
        "case_short": "pyrite",
        "root_mesh": "results/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510_remote/inputs/V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA/V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA.obj",
        "target_guide": "visuals/strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510/V24_ifs_pyrite_lattice/overview_raw.png",
        "prompt": "recursive pyrite crystal lattice with faceted cubic blocks and connected bridges",
        "grammar": "pyrite_lattice",
        "depth": "2",
    },
    {
        "case_id": "V21_ifs_bismuth_stepped_transform_d5_iridescent",
        "case_short": "bismuth",
        "root_mesh": "results/strict_visual_matched_texture_V21_ifs_transform_natural_seed20291700_20260510_remote/inputs/V21_ifs_bismuth_stepped_transform_d5_iridescent/V21_ifs_bismuth_stepped_transform_d5_iridescent.obj",
        "target_guide": "visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_zoom_20260510/V21_ifs_bismuth_stepped_transform_d5_iridescent_steps8_tex2048_seed20295804_xformers/overview_raw.png",
        "prompt": "recursive bismuth crystal with stepped terraced square hopper geometry and iridescent facets",
        "grammar": "pyrite_lattice",
        "depth": "2",
    },
    {
        "case_id": "V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA",
        "case_short": "radial_ornament",
        "root_mesh": "results/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510_remote/inputs/V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA/V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA.obj",
        "target_guide": "visuals/strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510/V24_ifs_radial_ornament/overview_raw.png",
        "prompt": "recursive radial ornament with orbiting spokes, repeated rings, and connected symmetric structure",
        "grammar": "pyrite_lattice",
        "depth": "2",
    },
]


def rot_x(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float64)


def rot_z(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float64)


def load_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(path, force="scene", process=False)
    if isinstance(loaded, trimesh.Scene):
        meshes = [m for m in loaded.geometry.values() if isinstance(m, trimesh.Trimesh)]
        if not meshes:
            raise ValueError(f"no mesh in {path}")
        loaded = trimesh.util.concatenate(meshes)
    return trimesh.Trimesh(vertices=np.asarray(loaded.vertices), faces=np.asarray(loaded.faces), process=False)


def render_mesh(mesh_path: Path, out: Path, title: str, size: int = 1024, max_faces: int = 90_000) -> None:
    mesh = load_mesh(mesh_path)
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(faces) > max_faces:
        faces = faces[np.linspace(0, len(faces) - 1, max_faces, dtype=np.int64)]
    img = Image.new("RGB", (size, size), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    rot = rot_x(math.radians(27.0)) @ rot_z(math.radians(-42.0))
    pts = vertices @ rot.T
    center = (pts.min(axis=0) + pts.max(axis=0)) * 0.5
    span = max(float((pts.max(axis=0) - pts.min(axis=0)).max()), 1e-9)
    pts = (pts - center) / span
    tri = pts[faces]
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    norms = np.linalg.norm(normals, axis=1)
    valid = norms > 1e-10
    tri = tri[valid]
    normals = normals[valid] / norms[valid, None]
    light = np.array([0.35, -0.45, 0.82], dtype=np.float64)
    light = light / np.linalg.norm(light)
    order = np.argsort(tri[:, :, 2].mean(axis=1))
    scale = size * 0.74
    for idx in order:
        coords = [
            (float(size * 0.5 + p[0] * scale), float(size * 0.53 - p[1] * scale))
            for p in tri[idx, :, :2]
        ]
        shade = 0.44 + 0.56 * max(float(normals[idx] @ light), 0.0)
        val = int(np.clip(255 * shade, 162, 255))
        draw.polygon(coords, fill=(val, val, val))
    draw.text((18, size - 34), title, fill=(35, 35, 35))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def copy_image(src: Path, dst: Path) -> None:
    img = Image.open(src).convert("RGB")
    img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (1024, 1024), (255, 255, 255))
    x = (1024 - img.width) // 2
    y = (1024 - img.height) // 2
    canvas.paste(img, (x, y))
    dst.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dst)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = sorted({k for row in rows for k in row})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    if not args.out_dir.is_absolute():
        args.out_dir = (ROOT / args.out_dir).resolve()

    rows: list[dict[str, Any]] = []
    for case in CASES:
        case_dir = args.out_dir / case["case_short"]
        root_mesh = ROOT / case["root_mesh"]
        target_src = ROOT / case["target_guide"]
        root_guide = case_dir / "root_guide.png"
        target_guide = case_dir / "target_guide.png"
        render_mesh(root_mesh, root_guide, f"{case['case_short']} root")
        copy_image(target_src, target_guide)
        row = {
            **case,
            "root_mesh_abs": str(root_mesh),
            "target_guide_source_abs": str(target_src),
            "root_guide_abs": str(root_guide),
            "target_guide_abs": str(target_guide),
            "root_guide": str(root_guide.resolve().relative_to(ROOT)),
            "target_guide": str(target_guide.resolve().relative_to(ROOT)),
            "status": "ok",
        }
        rows.append(row)
    write_csv(args.out_dir / "condition_manifest.csv", rows)
    (args.out_dir / "condition_manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "out": str(args.out_dir)}, indent=2))


if __name__ == "__main__":
    main()
