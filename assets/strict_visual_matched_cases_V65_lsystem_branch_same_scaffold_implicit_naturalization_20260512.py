#!/usr/bin/env python3
"""V65 same-scaffold L-system implicit naturalization.

The previous V61--V64 line improved continuity but did not match the traditional
L-system baseline's recursive depth and density. V65 therefore uses the
traditional branch OBJ as the scaffold itself: each 8-sided cylinder segment is
converted back into a centerline segment, then reconstructed as a fused implicit
wood surface with closed terminals and junction-local fusion.

This is still grammar-owned/object-space naturalization: no 2D inpaint,
SDEdit/backprojection, UV seam patching, or post-hoc image edit is claimed.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import procedural_baselines as pb
import strict_visual_matched_cases_V22_botanical_smooth_20260510 as v22
import strict_visual_matched_cases_V23_all_family_20260510 as v23
import strict_visual_matched_cases_V45_lsystem_branch_implicit_wood_fork_naturalization_20260511 as v45
import strict_visual_matched_cases_v13_smooth_coral_crystal_20260510 as v13
import strict_visual_matched_cases_v16_natural_coral_20260510 as v16


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
DEFAULT_ACTIVE_GPUS = [4, 5]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 200
CONNECTIVITY_LCR_MIN = 0.995
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V65_lsystem_branch_same_scaffold_implicit_naturalization_20260512_dryrun"
BASELINE_OBJ = ROOT_DIR / "results" / "traditional_baselines" / "run_20260507_0300" / "lsystem_branch.obj"

SURFACE_STRATEGY = "v65_lsystem_same_scaffold_implicit_naturalization_depth_density_matched"
SELECTION_BUDGET = "four_v65_same_scaffold_candidates_local_qa_then_priority_bc_two_gpu_remote"
MESH_PBR_POLICY = "same_lsystem_scaffold_obj_reconstructed_as_fused_implicit_wood_for_trellis2_glb_export"
ZOOM_DIVISOR = 2.15


def _parse_obj_vertices(path: Path) -> np.ndarray:
    vertices: list[tuple[float, float, float]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
    return np.asarray(vertices, dtype=np.float64)


def _baseline_segments(path: Path, target_extent: float = 2.72) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    verts = _parse_obj_vertices(path)
    if len(verts) % 16 != 0:
        raise RuntimeError(f"Expected 16 vertices per L-system cylinder, got {len(verts)} vertices")
    mins = verts.min(axis=0)
    maxs = verts.max(axis=0)
    center = (mins + maxs) * 0.5
    scale = target_extent / max(float((maxs - mins).max()), 1e-6)
    starts: list[np.ndarray] = []
    ends: list[np.ndarray] = []
    radii: list[float] = []
    for offset in range(0, len(verts), 16):
        ring0 = (verts[offset : offset + 8] - center) * scale
        ring1 = (verts[offset + 8 : offset + 16] - center) * scale
        a = ring0.mean(axis=0)
        b = ring1.mean(axis=0)
        if float(np.linalg.norm(b - a)) < 1e-8:
            continue
        r0 = float(np.linalg.norm(ring0 - a, axis=1).mean())
        r1 = float(np.linalg.norm(ring1 - b, axis=1).mean())
        starts.append(a)
        ends.append(b)
        radii.append(max((r0 + r1) * 0.5, 0.004))
    meta = {
        "source_obj": str(path),
        "source_vertices": int(len(verts)),
        "source_cylinder_segments": int(len(starts)),
        "source_bbox_extent": [float(x) for x in (maxs - mins)],
        "normalization_target_extent": float(target_extent),
        "normalization_scale": float(scale),
    }
    return np.asarray(starts), np.asarray(ends), np.asarray(radii), meta


def _cluster_points(points: np.ndarray, tol: float = 0.010) -> tuple[np.ndarray, np.ndarray]:
    keys = np.rint(points / tol).astype(np.int64)
    unique, inverse = np.unique(keys, axis=0, return_inverse=True)
    centers = np.zeros((len(unique), 3), dtype=np.float64)
    counts = np.zeros(len(unique), dtype=np.int64)
    for idx, cid in enumerate(inverse):
        centers[cid] += points[idx]
        counts[cid] += 1
    centers /= np.maximum(counts[:, None], 1)
    return centers, counts


def _write_guides(out_dir: Path) -> Dict[str, str]:
    guide_dir = out_dir / "_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)
    palettes = {
        "olive_bark": [(82, 76, 51), (112, 98, 64), (140, 120, 82), (96, 112, 74)],
        "warm_bark": [(98, 72, 48), (128, 94, 66), (158, 122, 86), (116, 94, 62)],
        "pale_cambium": [(116, 98, 74), (144, 120, 88), (166, 142, 108), (104, 118, 88)],
        "matte_cedar": [(78, 68, 48), (104, 84, 58), (132, 106, 72), (150, 128, 92)],
    }
    out: Dict[str, str] = {}
    for key, colors in palettes.items():
        path = guide_dir / f"V65_lsystem_same_scaffold_{key}_lowcontrast_guide.png"
        rng = np.random.default_rng(abs(hash(path.stem)) % (2**31 - 1))
        img = Image.new("RGB", (768, 768), colors[1])
        draw = ImageDraw.Draw(img, "RGBA")
        for _ in range(95):
            color = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(-160, 928))
            y = int(rng.integers(-160, 928))
            r = int(rng.integers(110, 320))
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, int(rng.integers(10, 28))))
        img = img.filter(ImageFilter.GaussianBlur(radius=28))
        draw = ImageDraw.Draw(img, "RGBA")
        for _ in range(34):
            color = colors[int(rng.integers(0, len(colors)))]
            x = int(rng.integers(20, 748))
            y = int(rng.integers(40, 728))
            length = int(rng.integers(120, 330))
            angle = float(rng.uniform(-2.4, -0.5))
            pts = [
                (
                    int(x + math.cos(angle) * length * t + math.sin(t * math.pi) * rng.uniform(-7, 7)),
                    int(y + math.sin(angle) * length * t),
                )
                for t in np.linspace(0, 1, 8)
            ]
            draw.line(pts, fill=(*color, int(rng.integers(20, 42))), width=int(rng.integers(3, 7)))
        img.filter(ImageFilter.SMOOTH_MORE).save(path)
        out[key] = str(path)
    return out


def _stamp_same_scaffold(
    starts: np.ndarray,
    ends: np.ndarray,
    radii: np.ndarray,
    *,
    radius_scale: float,
    junction_boost: float,
    sigma: float,
    level: float,
    grid: int,
    bound: float,
    sample_scale: float,
    seed: int,
) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed)
    coords = np.linspace(-bound, bound, grid, dtype=np.float32)
    field = np.zeros((grid, grid, grid), dtype=np.float32)
    all_endpoints = np.vstack([starts, ends])
    junction_centers, endpoint_counts = _cluster_points(all_endpoints, tol=0.012)
    junctions = junction_centers[endpoint_counts >= 3]
    terminals = junction_centers[endpoint_counts == 1]
    primitive_count = 0
    for i, (a, b, r) in enumerate(zip(starts, ends, radii)):
        ra = max(float(r) * radius_scale, 0.0052)
        rb = max(float(r) * radius_scale, 0.0048)
        primitive_count += v45._stamp_wood_segment(
            field,
            coords,
            a,
            b,
            ra,
            rb,
            strength=1.02,
            samples_per_unit=sample_scale,
            rng=rng,
            phase=i * 0.37 + rng.uniform(-0.2, 0.2),
        )
    for j, center in enumerate(junctions):
        # Junction-local balls fuse coincident cylinder endpoints without making
        # the whole object a single smooth blob.
        local_r = float(np.quantile(radii, 0.72)) * radius_scale * junction_boost
        v45._stamp_ball(field, coords, center, max(local_r, 0.012), 0.36, cutoff=1.95)
        primitive_count += 1
        if j % 5 == 0:
            axis = v22._unit(center + rng.normal(0.0, 0.08, 3))
            u, v, w = v22._basis(axis)
            v45._stamp_ellipsoid(
                field,
                coords,
                center + axis * 0.010,
                (u, v, w),
                (max(local_r * 0.42, 0.006), max(local_r * 0.30, 0.005), max(local_r * 1.55, 0.018)),
                0.045,
                cutoff=1.5,
            )
            primitive_count += 1
    for center in terminals[:: max(1, len(terminals) // 96)]:
        v45._stamp_ball(field, coords, center, max(float(np.quantile(radii, 0.38)) * radius_scale * 0.70, 0.006), 0.09, cutoff=1.55)
        primitive_count += 1
    field = v45.gaussian_filter(field, sigma=float(sigma))
    verts, faces, _normals, _values = v45.marching_cubes(
        field,
        level=float(level),
        spacing=(float(coords[1] - coords[0]),) * 3,
        allow_degenerate=False,
    )
    verts = verts + np.array([coords[0], coords[0], coords[0]], dtype=float)
    mesh = pb.Mesh([tuple(map(float, v)) for v in verts], [tuple(int(i) + 1 for i in f) for f in faces])
    mesh, raw_components, retained_ratio = v13._largest_component_mesh(mesh)
    mesh = v16._taubin_smooth(mesh, iterations=6, lam=0.28, mu=-0.31)
    diag = {
        "source_segment_count": int(len(starts)),
        "junction_cluster_count": int(len(junctions)),
        "terminal_cluster_count": int(len(terminals)),
        "pre_marching_cubes_primitive_count": int(primitive_count),
        "raw_marching_cubes_component_count": int(raw_components),
        "largest_component_projection_retained_ratio": float(retained_ratio),
        "implicit_grid_resolution": int(grid),
        "implicit_field_bound": float(bound),
        "implicit_field_level": float(level),
        "gaussian_sigma": float(sigma),
        "same_scaffold_reconstruction": True,
    }
    return mesh, diag


def _case_specs(root: Path, out_dir: Path, seed: int) -> list[dict]:
    starts, ends, radii, source_meta = _baseline_segments(BASELINE_OBJ)
    variants = [
        ("V65_lsys_branch_same_scaffold_smooth_A", 4, "olive_bark", 0.82, 1.08, 0.64, 0.42, 184, 1.62, 138.0, "smooth fused same-scaffold naturalization"),
        ("V65_lsys_branch_same_scaffold_dense_B", 5, "warm_bark", 0.92, 1.14, 0.70, 0.43, 192, 1.62, 146.0, "priority dense B: best depth/density match while closing open tubes"),
        ("V65_lsys_branch_same_scaffold_fine_C", 4, "pale_cambium", 0.74, 1.04, 0.58, 0.40, 192, 1.62, 150.0, "priority fine C: thinner naturalized branch forest, less blob risk"),
        ("V65_lsys_branch_same_scaffold_lowfrag_D", 5, "matte_cedar", 0.98, 1.18, 0.74, 0.45, 176, 1.62, 134.0, "low-fragment fallback with stronger junction closure"),
    ]
    specs = []
    for idx, (case_id, gpu, guide_key, radius_scale, junction_boost, sigma, level, grid, bound, sample_scale, reason) in enumerate(variants):
        mesh, diag = _stamp_same_scaffold(
            starts,
            ends,
            radii,
            radius_scale=radius_scale,
            junction_boost=junction_boost,
            sigma=sigma,
            level=level,
            grid=grid,
            bound=bound,
            sample_scale=sample_scale,
            seed=seed + idx * 101,
        )
        controls = {
            **source_meta,
            **diag,
            "surface_strategy": SURFACE_STRATEGY,
            "family": "L-system",
            "match_target": "lsys_branch_side_d5",
            "traditional_target": "lsystem_branch.obj",
            "branch_junction_count": int(diag["junction_cluster_count"]),
            "terminal_count": int(diag["terminal_cluster_count"]),
            "saddle_neck_count": int(diag["junction_cluster_count"]),
            "terminal_fork_count": int(diag["terminal_cluster_count"]),
            "support_edge_count": int(diag["source_segment_count"]),
            "semantic_detail_count": int(diag["junction_cluster_count"] + diag["terminal_cluster_count"]),
            "masked_local_naturalization_target": "same L-system scaffold reconstructed as fused continuous wood surface",
            "mask_scope": "object_space_same_scaffold_junction_clusters_and_segment_union",
            "seam_mask_space": "object_xyz",
            "same_scaffold_as_traditional_baseline": True,
            "open_tube_cap_removed_by_implicit_union": True,
            "hard_inserted_tube_replaced_by_junction_fusion": True,
            "sdedit_seam_backprojection_available": False,
            "claim_boundary": "object-space same-scaffold implicit naturalization; no image-space seam edit",
            "radius_scale": float(radius_scale),
            "junction_boost": float(junction_boost),
        }
        specs.append(
            {
                "case_id": case_id,
                "gpu": gpu,
                "guide_key": guide_key,
                "mesh": mesh,
                "controls": controls,
                "seed": seed + idx * 101,
                "reason": reason,
            }
        )
    return specs


def _zoom_targets_from_baseline() -> tuple[list[list[float]], list[list[float]]]:
    starts, ends, _radii, _meta = _baseline_segments(BASELINE_OBJ)
    centers, counts = _cluster_points(np.vstack([starts, ends]), tol=0.012)
    junctions = centers[counts >= 3]
    if len(junctions) == 0:
        junctions = centers
    order = np.argsort(junctions[:, 2])[::-1]
    selected = junctions[order[:32]]
    targets = [[float(x) for x in p] for p in selected]
    fixed = targets[:2] if len(targets) >= 2 else targets
    return targets, fixed


def materialize(root: Path, out_dir: Path, seed: int = 20260512, case_limit: Optional[int] = None) -> Dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    guides = _write_guides(out_dir)
    specs = _case_specs(root, out_dir, seed)
    if case_limit is not None:
        specs = specs[: int(case_limit)]
    detail_targets, fixed_targets = _zoom_targets_from_baseline()
    rows = []
    metrics_rows = []
    for spec in specs:
        case_dir = out_dir / spec["case_id"]
        mesh_path = case_dir / f"{spec['case_id']}.obj"
        v23._export_mesh(mesh_path, spec["mesh"])
        metrics = v23._mesh_stats(mesh_path, spec["controls"])
        if metrics["largest_mesh_component_vertex_ratio"] < CONNECTIVITY_LCR_MIN:
            raise RuntimeError(f"{spec['case_id']} failed V65 connectivity gate: {metrics}")
        guide_path = guides[spec["guide_key"]]
        metadata = {
            "case_id": spec["case_id"],
            "source_generator": "assets/strict_visual_matched_cases_V65_lsystem_branch_same_scaffold_implicit_naturalization_20260512.py",
            "root_selection_log": {
                "root_source_type": "traditional_lsystem_branch_same_scaffold",
                "source_obj": str(BASELINE_OBJ),
                "source_segment_count": int(spec["controls"]["source_segment_count"]),
            },
            "controls": spec["controls"],
            "metrics": metrics,
            "guide_image": guide_path,
            "v65_lsystem_branch_naturalization_contract": {
                "target_failure": "V61-V64 could be clean but did not match the baseline branch depth/density.",
                "geometry_operator": "parse traditional L-system cylinder scaffold and reconstruct it as fused implicit wood with local junction closure.",
                "same_scaffold_as_baseline": True,
                "sdedit_seam_backprojection_available": False,
            },
        }
        metadata_path = case_dir / f"{spec['case_id']}_metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        row = {
            "case_id": spec["case_id"],
            "family": "L-system",
            "match_target": "lsys_branch_side_d5",
            "traditional_target": "lsystem_branch.obj",
            "recursive_mode": "same-scaffold L-system implicit wood naturalization",
            "mesh_path": str(mesh_path),
            "guide_image": guide_path,
            "metadata_path": str(metadata_path),
            "remote_target": REMOTE_TARGET,
            "gpu_group": int(spec["gpu"]),
            "seed": int(spec["seed"]),
            "operators": json.dumps(["same_scaffold_parse", "implicit_segment_union", "junction_cluster_fusion", "closed_terminal_surface"], ensure_ascii=False),
            "operator_composition": "same_scaffold_parse -> implicit_segment_union -> junction_cluster_fusion -> closed_terminal_surface",
            "controls": json.dumps(spec["controls"], ensure_ascii=False, sort_keys=True),
            "why_matches_traditional": "Uses the same traditional L-system branch cylinder scaffold, but reconstructs it as our continuous naturalized implicit mesh.",
            "strict_match_notes": "same scaffold/depth/density; comparison isolates tube-openings and junction naturalization.",
            "case_role": "v65_lsystem_branch_same_scaffold_implicit_naturalization",
            "qa_priority": "publication_grade_depth_density_matched_same_scaffold_no_open_tube_no_hard_insert",
            "rerun_reason": spec["reason"],
            "boundary_tag": "",
            "strict_one_to_one": "true",
            "generation_policy": "same_scaffold_local_materialize_then_two_gpu_remote_if_visual_passes",
            "mesh_input_policy": "obj_mesh_inputs_only",
            "mesh_pbr_policy": MESH_PBR_POLICY,
            "surface_strategy": SURFACE_STRATEGY,
            "block_or_token_stamping": "false",
            "root_variant": spec["case_id"].replace("V65_", ""),
            "grammar_guide": "v65_lsystem_same_scaffold_lowcontrast_bark_guide",
            "parameter_variant": f"grid{spec['controls']['implicit_grid_resolution']}_sigma{spec['controls']['gaussian_sigma']}_level{spec['controls']['implicit_field_level']}_r{spec['controls']['radius_scale']}",
            "selection_budget": SELECTION_BUDGET,
            "storage_root": REMOTE_STORAGE_ROOT,
            "storage_limit_gb": STORAGE_LIMIT_GB,
            "pre_export_lcr_gate": CONNECTIVITY_LCR_MIN,
            "branch_junction_count": int(spec["controls"]["branch_junction_count"]),
            "terminal_count": int(spec["controls"]["terminal_count"]),
            "raw_marching_cubes_component_count": int(spec["controls"]["raw_marching_cubes_component_count"]),
            "largest_component_projection_retained_ratio": float(spec["controls"]["largest_component_projection_retained_ratio"]),
            "pre_marching_cubes_primitive_count": int(spec["controls"]["pre_marching_cubes_primitive_count"]),
            "sdedit_seam_backprojection_available": "false",
        }
        rows.append(row)
        metrics_rows.append(
            {
                "case_id": spec["case_id"],
                "family": "L-system",
                "match_target": "lsys_branch_side_d5",
                "traditional_target": "lsystem_branch.obj",
                **metrics,
                "branch_junction_count": int(spec["controls"]["branch_junction_count"]),
                "terminal_count": int(spec["controls"]["terminal_count"]),
                "raw_marching_cubes_component_count": int(spec["controls"]["raw_marching_cubes_component_count"]),
                "largest_component_projection_retained_ratio": float(spec["controls"]["largest_component_projection_retained_ratio"]),
            }
        )

    for name, rows_obj in (("manifest", rows), ("initial_metrics", metrics_rows)):
        csv_path = out_dir / f"{name}.csv"
        json_path = out_dir / f"{name}.json"
        json_path.write_text(json.dumps(rows_obj, indent=2, ensure_ascii=False), encoding="utf-8")
        if rows_obj:
            with csv_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows_obj[0].keys()))
                writer.writeheader()
                writer.writerows(rows_obj)
    obj_zoom_cases = []
    for row in rows:
        obj_zoom_cases.append(
            {
                "label": row["case_id"] + "_obj_same_scaffold_zoom",
                "mesh": str(Path(row["mesh_path"]).resolve()),
                "plan_mesh": str(Path(row["mesh_path"]).resolve()),
                "material_mode": "bark",
                "zoom_levels": 2,
                "zoom_divisor": ZOOM_DIVISOR,
                "detail_targets": detail_targets,
                "fixed_detail_targets": fixed_targets,
                "detail_target_source": "v65_same_scaffold_high_degree_lsystem_junctions",
            }
        )
    zoom_manifest = out_dir / "V65_obj_zoom_manifest_same_scaffold_20260512.json"
    zoom_manifest.write_text(json.dumps({"cases": obj_zoom_cases}, indent=2, ensure_ascii=False), encoding="utf-8")
    case_lines = [f"{row['case_id']}|{row['mesh_path']}|{row['guide_image']}|{row['seed']}|{row['gpu_group']}" for row in rows]
    (out_dir / "a100-2_cases.txt").write_text("\n".join(case_lines) + "\n", encoding="utf-8")
    (out_dir / "gpu45_cases.txt").write_text("\n".join(case_lines) + "\n", encoding="utf-8")
    for gpu in ALLOWED_GPUS:
        selected = [line for line, row in zip(case_lines, rows) if int(row["gpu_group"]) == gpu]
        (out_dir / f"gpu{gpu}_cases.txt").write_text("\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")
    summary = {
        "out_dir": str(out_dir),
        "num_cases": len(rows),
        "remote_target": REMOTE_TARGET,
        "allowed_gpus": ALLOWED_GPUS,
        "default_active_gpus": DEFAULT_ACTIVE_GPUS,
        "max_simultaneous_remote_gpus": 2,
        "storage_root": REMOTE_STORAGE_ROOT,
        "storage_limit_gb": STORAGE_LIMIT_GB,
        "surface_generator": "strict_visual_matched_cases_V65_lsystem_branch_same_scaffold_implicit_naturalization",
        "surface_strategy": SURFACE_STRATEGY,
        "selection_budget": SELECTION_BUDGET,
        "manifest": str(out_dir / "manifest.csv"),
        "initial_metrics": str(out_dir / "initial_metrics.csv"),
        "obj_zoom_manifest": str(zoom_manifest),
        "priority_cases_for_remote_if_obj_qa_passes": [
            "V65_lsys_branch_same_scaffold_dense_B",
            "V65_lsys_branch_same_scaffold_fine_C",
        ],
        "do_not_launch_remote_before_local_visual_qa": True,
        "lsystem_branch_gate": {
            "same_scaffold_as_traditional_baseline": True,
            "source_segment_count": int(rows and json.loads(rows[0]["controls"])["source_segment_count"]),
            "min_branch_junctions": min(int(r["branch_junction_count"]) for r in rows) if rows else 0,
            "min_terminal_count": min(int(r["terminal_count"]) for r in rows) if rows else 0,
            "min_largest_component_projection_retained_ratio": min(float(r["largest_component_projection_retained_ratio"]) for r in rows) if rows else 0,
            "sdedit_seam_backprojection_available": False,
        },
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V65 Same-Scaffold L-system Naturalization\n\n"
        "V65 parses the traditional L-system branch OBJ into cylinder centerlines and reconstructs the same scaffold as a fused implicit wood surface. "
        "It is designed to match depth/density while replacing open tubes and hard junctions. No image-space seam edit is claimed.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("RGG_ROOT", ROOT_DIR)))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260512)
    parser.add_argument("--case-limit", type=int, default=None)
    args = parser.parse_args()
    materialize(args.root, args.out, seed=args.seed, case_limit=args.case_limit)


if __name__ == "__main__":
    main()
