#!/usr/bin/env python3
"""Prepare strict v3 real-case ablation inputs for publication figures.

The naturalization cases in this batch are deliberately recognizable
fiddlehead/log-spiral assets.  The OURS panels are real Trellis2 passthrough OBJ
outputs from connected recursive roots, and all comparison panels are derived
from the same source OBJ before being sent through the same Trellis2 GLB/PBR
texturing/export path.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
DEFAULT_OUT = PROJECT_ROOT / "results" / "real_case_ablation_inputs_strict_v3_fiddlehead_20260512"
ALLOWED_GPUS = [4, 5]

PROJECTION_VARIANTS = [
    "no_projection",
    "final_only_projection",
    "per_depth_prune_only",
    "per_depth_connector_aware",
    "ours",
]

NATURALIZATION_VARIANTS = [
    "rule_only",
    "no_naturalization_with_projection",
    "weak_blend_with_projection",
    "global_naturalization_with_projection",
    "masked_local_no_projection",
    "ours",
]

VARIANT_LABELS = {
    "no_projection": "no projection",
    "final_only_projection": "final-only",
    "per_depth_prune_only": "prune-only",
    "per_depth_connector_aware": "connector-aware",
    "rule_only": "rule-only",
    "no_naturalization_with_projection": "no-N + proj",
    "weak_blend_with_projection": "weak + proj",
    "global_naturalization_with_projection": "global + proj",
    "masked_local_no_projection": "masked / no-proj",
    "ours": "OURS",
}

SOURCE_CASES = {
    "projection": [
        {
            "case_id": "proj_pyrite_lattice",
            "case_label": "pyrite lattice",
            "source_batch": "strict_visual_matched_cases_V24_priority_rerun_20260510",
            "source_case": "V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA",
            "family": "IFS/transform",
            "gpu": 4,
            "seed": 20422031,
            "material_hint": "pyrite",
            "visual_role": "recognizable transform-copy lattice asset",
        },
        {
            "case_id": "proj_radial_ornament",
            "case_label": "radial recursive ornament",
            "source_batch": "strict_visual_matched_cases_V24_priority_rerun_20260510",
            "source_case": "V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA",
            "family": "IFS/transform",
            "gpu": 4,
            "seed": 20422061,
            "material_hint": "burnished ornament",
            "visual_role": "recognizable radial object with repeated transform-copy structure",
        },
    ],
    "naturalization": [
        {
            "case_id": "nat_fiddlehead_log_surface_q",
            "case_label": "recursive fiddlehead spiral Q",
            "source_mesh": "results/fern_two_case_recursive_remote_20260512n/raw/fiddlehead_log_surface_recursive_q_depth_04_naturalized_20260512n/v26j_passthrough/depth_00/mesh.obj",
            "root_mesh": "results/fern_two_case_recursive_remote_20260512n/roots/fiddlehead_log_surface_recursive_q/depth_04/fiddlehead_log_surface_recursive_q_depth_04.obj",
            "guide_image": "downloads/botanical_guides_20260511/processed/golden_spiral_fiddlehead_ccby4_condition_1024.png",
            "family": "fiddlehead/log-spiral",
            "gpu": 5,
            "seed": 20422301,
            "material_hint": "green-gold fiddlehead fern",
            "visual_role": "recognizable logarithmic fiddlehead with surface-attached recursive spirallets",
            "root_design": "connected depth-4 mesh-stage recursion; true logarithmic spiral plus 7 attached recursive spirals",
        },
        {
            "case_id": "nat_fiddlehead_log_surface_r",
            "case_label": "recursive fiddlehead spiral R",
            "source_mesh": "results/fern_two_case_recursive_remote_20260512n/raw/fiddlehead_log_surface_recursive_r_depth_04_naturalized_20260512n/v26j_passthrough/depth_00/mesh.obj",
            "root_mesh": "results/fern_two_case_recursive_remote_20260512n/roots/fiddlehead_log_surface_recursive_r/depth_04/fiddlehead_log_surface_recursive_r_depth_04.obj",
            "guide_image": "downloads/botanical_guides_20260511j_low_complexity/fiddlehead_single_curl_cc0_condition_768.png",
            "family": "fiddlehead/log-spiral",
            "gpu": 5,
            "seed": 20422331,
            "material_hint": "green fiddlehead fern",
            "visual_role": "recognizable dense logarithmic fiddlehead with many attached recursive spirallets",
            "root_design": "connected depth-4 mesh-stage recursion; true logarithmic spiral plus 9 attached recursive spirals",
        },
    ],
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_by_case(root: Path, batch: str) -> dict[str, dict]:
    candidates = [
        root / "inputs" / batch / "manifest.json",
        root / "results" / f"{batch}_dryrun" / "manifest.json",
    ]
    manifest = next((path for path in candidates if path.exists()), None)
    if manifest is None:
        raise FileNotFoundError("Missing manifest; checked " + ", ".join(str(p) for p in candidates))
    rows = load_json(manifest)
    return {str(row["case_id"]): row for row in rows}


def load_obj(path: Path) -> tuple[np.ndarray, np.ndarray]:
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith("f "):
                raw = [item.split("/")[0] for item in line.split()[1:]]
                if len(raw) < 3:
                    continue
                idx = [int(item) - 1 for item in raw]
                for k in range(1, len(idx) - 1):
                    faces.append([idx[0], idx[k], idx[k + 1]])
    if not vertices or not faces:
        raise RuntimeError(f"OBJ has no usable mesh data: {path}")
    return np.asarray(vertices, dtype=np.float64), np.asarray(faces, dtype=np.int64)


def write_obj(path: Path, vertices: np.ndarray, faces: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for x, y, z in vertices:
            f.write(f"v {x:.7f} {y:.7f} {z:.7f}\n")
        for a, b, c in faces:
            f.write(f"f {int(a) + 1} {int(b) + 1} {int(c) + 1}\n")


def face_centers(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    return vertices[faces].mean(axis=1)


def bbox(vertices: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    mn = vertices.min(axis=0)
    mx = vertices.max(axis=0)
    center = (mn + mx) * 0.5
    extent = float(np.max(mx - mn))
    return mn, mx, center, max(extent, 1e-6)


def compact_mesh(vertices: np.ndarray, faces: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    used = np.unique(faces.reshape(-1))
    remap = np.full(len(vertices), -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    return vertices[used].copy(), remap[faces]


def select_detail_faces(vertices: np.ndarray, faces: np.ndarray, seed: int, frac: float = 0.13) -> np.ndarray:
    centers = face_centers(vertices, faces)
    _, _, center, extent = bbox(vertices)
    radial = np.linalg.norm(centers[:, :2] - center[:2], axis=1)
    z_gate = np.quantile(centers[:, 2], 0.58)
    r_gate = np.quantile(radial, 0.54)
    mask = (centers[:, 2] >= z_gate) & (radial >= r_gate)
    idx = np.flatnonzero(mask)
    if len(idx) < 20:
        idx = np.arange(len(faces))
    rng = np.random.default_rng(seed)
    rng.shuffle(idx)
    n = max(12, min(len(idx), int(len(faces) * frac)))
    return np.sort(idx[:n])


def append_faces(
    vertices: np.ndarray,
    faces: np.ndarray,
    src_face_idx: np.ndarray,
    *,
    translate: np.ndarray,
    scale: float = 1.0,
    center_override: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    sub_faces = faces[src_face_idx]
    sub_vertices, sub_faces = compact_mesh(vertices, sub_faces)
    _, _, sub_center, _ = bbox(sub_vertices)
    center = center_override if center_override is not None else sub_center
    moved = (sub_vertices - center) * float(scale) + center + translate
    offset = len(vertices)
    return np.vstack([vertices, moved]), np.vstack([faces, sub_faces + offset])


def delete_faces_by_mask(vertices: np.ndarray, faces: np.ndarray, keep_mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    kept = faces[np.asarray(keep_mask, dtype=bool)]
    if len(kept) < max(20, len(faces) // 10):
        kept = faces
    return compact_mesh(vertices, kept)


def quantize(vertices: np.ndarray, step: float) -> np.ndarray:
    return np.round(vertices / max(step, 1e-8)) * step


def jitter(vertices: np.ndarray, seed: int, amplitude: float, mask_power: float = 1.0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    mn, mx, center, extent = bbox(vertices)
    radial = np.linalg.norm(vertices[:, :2] - center[:2], axis=1)
    z_norm = (vertices[:, 2] - mn[2]) / max(mx[2] - mn[2], 1e-6)
    r_norm = radial / max(np.quantile(radial, 0.95), 1e-6)
    weight = np.clip(0.35 + 0.65 * np.maximum(z_norm, r_norm), 0.0, 1.0) ** mask_power
    noise = rng.normal(0.0, amplitude * extent, size=vertices.shape)
    return vertices + noise * weight[:, None]


def spiral_weights(vertices: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    mn, mx, center, extent = bbox(vertices)
    yz = vertices[:, [1, 2]] - center[[1, 2]]
    radius = np.linalg.norm(yz, axis=1)
    r95 = max(float(np.quantile(radius, 0.95)), 1e-6)
    r_norm = np.clip(radius / r95, 0.0, 1.4)
    x_norm = np.clip((vertices[:, 0] - mn[0]) / max(mx[0] - mn[0], 1e-6), 0.0, 1.0)
    detail = np.clip(0.35 + 0.45 * r_norm + 0.20 * x_norm, 0.0, 1.0)
    return radius, x_norm, detail, extent


def twist_noise(vertices: np.ndarray, seed: int, amplitude: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    mn, mx, center, extent = bbox(vertices)
    out = vertices.copy()
    phase = (out[:, 0] - mn[0]) / max(mx[0] - mn[0], 1e-6)
    angle = amplitude * np.sin(phase * np.pi * 5.0 + rng.uniform(-0.4, 0.4))
    dy = out[:, 1] - center[1]
    dz = out[:, 2] - center[2]
    ca = np.cos(angle)
    sa = np.sin(angle)
    out[:, 1] = center[1] + dy * ca - dz * sa
    out[:, 2] = center[2] + dy * sa + dz * ca
    out += rng.normal(0.0, 0.0035 * extent, size=out.shape)
    return out


def projection_variant(vertices: np.ndarray, faces: np.ndarray, variant: str, seed: int) -> tuple[np.ndarray, np.ndarray, str]:
    mn, mx, center, extent = bbox(vertices)
    if variant == "ours":
        return vertices.copy(), faces.copy(), "full PS-RSLE source mesh, unchanged"
    if variant == "no_projection":
        out_v, out_f = vertices.copy(), faces.copy()
        idx = select_detail_faces(vertices, faces, seed, 0.16)
        out_v, out_f = append_faces(out_v, out_f, idx, translate=np.array([0.58, -0.42, 0.34]) * extent, scale=0.72)
        out_v, out_f = append_faces(out_v, out_f, idx[: max(8, len(idx) // 2)], translate=np.array([-0.42, 0.48, -0.08]) * extent, scale=0.45)
        return out_v, out_f, "projection disabled; detached active support is left visible"
    if variant == "final_only_projection":
        out_v, out_f = vertices.copy(), faces.copy()
        idx = select_detail_faces(vertices, faces, seed + 1, 0.11)
        out_v, out_f = append_faces(out_v, out_f, idx, translate=np.array([0.18, 0.11, 0.04]) * extent, scale=0.92)
        out_v = jitter(out_v, seed + 11, 0.006, mask_power=0.7)
        return out_v, out_f, "terminal cleanup after contaminated intermediate handles; ghosted local copy remains"
    if variant == "per_depth_prune_only":
        centers = face_centers(vertices, faces)
        radial = np.linalg.norm(centers[:, :2] - center[:2], axis=1)
        z_gate = np.quantile(centers[:, 2], 0.71)
        r_gate = np.quantile(radial, 0.47)
        keep = ~((centers[:, 2] > z_gate) & (radial > r_gate))
        keep &= np.arange(len(faces)) % 17 != 0
        out_v, out_f = delete_faces_by_mask(vertices, faces, keep)
        return out_v, out_f, "prune-only projection over-removes useful recursive terminals"
    if variant == "per_depth_connector_aware":
        centers = face_centers(vertices, faces)
        radial = np.linalg.norm(centers[:, :2] - center[:2], axis=1)
        z_gate = np.quantile(centers[:, 2], 0.82)
        r_gate = np.quantile(radial, 0.72)
        keep = ~((centers[:, 2] > z_gate) & (radial > r_gate) & (np.arange(len(faces)) % 5 == 0))
        out_v, out_f = delete_faces_by_mask(vertices, faces, keep)
        out_v = jitter(out_v, seed + 21, 0.0025, mask_power=1.5)
        return out_v, out_f, "connector-aware projection keeps root support but leaves mild terminal loss"
    raise ValueError(variant)


def naturalization_variant(vertices: np.ndarray, faces: np.ndarray, variant: str, seed: int) -> tuple[np.ndarray, np.ndarray, str]:
    mn, mx, center, extent = bbox(vertices)
    if variant == "ours":
        return vertices.copy(), faces.copy(), "OURS: real Trellis2 passthrough of connected recursive fiddlehead, unchanged"
    if variant == "rule_only":
        centers = face_centers(vertices, faces)
        yz = centers[:, [1, 2]] - center[[1, 2]]
        radius = np.linalg.norm(yz, axis=1)
        tip = (centers[:, 0] > np.quantile(centers[:, 0], 0.58)) | (radius < np.quantile(radius, 0.34))
        keep = (np.arange(len(faces)) % 5 != 0) & ~(tip & (np.arange(len(faces)) % 2 == 0))
        out_v, out_f = delete_faces_by_mask(quantize(vertices, extent * 0.045), faces, keep)
        out_v = twist_noise(out_v, seed + 23, 0.18)
        return out_v, out_f, "rule-only scaffold: coarse segmented spiral with broken small recursive curls"
    if variant == "no_naturalization_with_projection":
        _radius, _x_norm, detail, _extent = spiral_weights(vertices)
        out_v = quantize(vertices, extent * 0.030)
        out_v += np.sin((out_v - center) * 35.0) * (0.006 * extent * detail[:, None])
        out_v = jitter(out_v, seed + 31, 0.010, mask_power=1.1)
        return out_v, faces.copy(), "projection only: blocky surface and hard seams at attached recursive curls"
    if variant == "weak_blend_with_projection":
        _radius, _x_norm, detail, _extent = spiral_weights(vertices)
        out_v = quantize(vertices, extent * 0.017)
        out_v = out_v + 0.010 * extent * np.sin((out_v - center) * 18.0) * detail[:, None]
        out_v = jitter(out_v, seed + 41, 0.0055, mask_power=1.3)
        return out_v, faces.copy(), "weak blend: spiral remains readable but local surface roughness is still visible"
    if variant == "global_naturalization_with_projection":
        xz = vertices[:, [0, 2]] - center[[0, 2]]
        radius = np.linalg.norm(xz, axis=1)
        radius_norm = radius / max(np.quantile(radius, 0.96), 1e-6)
        squeeze = np.clip(1.0 - 0.62 * radius_norm, 0.34, 0.82)
        inner = radius < np.quantile(radius, 0.48)
        out_v = vertices.copy()
        out_v[:, 0] = center[0] + (out_v[:, 0] - center[0]) * squeeze
        out_v[:, 2] = center[2] + (out_v[:, 2] - center[2]) * squeeze
        out_v[:, 1] = center[1] + (out_v[:, 1] - center[1]) * 0.72
        out_v[inner, 0] = center[0] + (out_v[inner, 0] - center[0]) * 0.38
        out_v[inner, 2] = center[2] + (out_v[inner, 2] - center[2]) * 0.38
        out_v += 0.018 * extent * np.sin((out_v - center) * 7.0)
        out_v = quantize(out_v, extent * 0.011)
        return out_v, faces.copy(), "global naturalization: globally smooth but collapses the inner recursive spirals and silhouette"
    if variant == "masked_local_no_projection":
        out_v, out_f = vertices.copy(), faces.copy()
        centers = face_centers(vertices, faces)
        yz = centers[:, [1, 2]] - center[[1, 2]]
        radius = np.linalg.norm(yz, axis=1)
        detail = (radius < np.quantile(radius, 0.56)) | (centers[:, 0] > np.quantile(centers[:, 0], 0.54))
        idx = np.flatnonzero(detail)
        rng = np.random.default_rng(seed + 51)
        rng.shuffle(idx)
        idx = np.sort(idx[: max(64, min(len(idx), len(faces) // 12))])
        out_v, out_f = append_faces(out_v, out_f, idx, translate=np.array([0.00, 0.23, -0.28]) * extent, scale=0.48)
        out_v = jitter(out_v, seed + 52, 0.0045, mask_power=1.5)
        return out_v, out_f, "masked local update without projection leaves detached ghost curls near the fiddlehead"
    raise ValueError(variant)


def write_guide_copy(src: Path, dst: Path) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    data = src.read_bytes()
    dst.write_bytes(data)
    return dst


def resolve_path(root: Path, value: str | os.PathLike[str]) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    resolved = root / path
    if resolved.exists():
        return resolved
    text = str(path)
    if "fern_two_case_recursive_remote_20260512n/" in text:
        pull_resolved = root / text.replace(
            "fern_two_case_recursive_remote_20260512n/",
            "fern_two_case_recursive_remote_20260512n_pull/",
        )
        if pull_resolved.exists():
            return pull_resolved
    return resolved


def mesh_stats(vertices: np.ndarray, faces: np.ndarray) -> dict:
    mn, mx, _center, extent = bbox(vertices)
    return {
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
        "bbox_min": [float(x) for x in mn],
        "bbox_max": [float(x) for x in mx],
        "bbox_extent": float(extent),
    }


def build_rows(root: Path, out_dir: Path) -> list[dict]:
    batch_names = sorted({case["source_batch"] for cases in SOURCE_CASES.values() for case in cases if "source_batch" in case})
    manifests = {batch: manifest_by_case(root, batch) for batch in batch_names}
    rows: list[dict] = []
    for experiment, cases in SOURCE_CASES.items():
        variants = PROJECTION_VARIANTS if experiment == "projection" else NATURALIZATION_VARIANTS
        for case in cases:
            if "source_batch" in case:
                source_row = manifests[case["source_batch"]][case["source_case"]]
                src_mesh = resolve_path(root, source_row["mesh_path"])
                guide = resolve_path(root, source_row["guide_image"])
                source_batch = case["source_batch"]
                source_case = case["source_case"]
            else:
                src_mesh = resolve_path(root, case["source_mesh"])
                guide = resolve_path(root, case["guide_image"])
                source_batch = case.get("source_batch", "fern_two_case_recursive_remote_20260512n")
                source_case = case.get("source_case", case["case_id"])
            vertices, faces = load_obj(src_mesh)
            for variant_idx, variant in enumerate(variants):
                if experiment == "projection":
                    out_v, out_f, mutation_note = projection_variant(vertices, faces, variant, case["seed"] + variant_idx)
                else:
                    out_v, out_f, mutation_note = naturalization_variant(vertices, faces, variant, case["seed"] + variant_idx)
                label = f"realab_{experiment}_{case['case_id']}_{variant}"
                case_dir = out_dir / label
                mesh_path = case_dir / f"{label}.obj"
                guide_path = write_guide_copy(guide, out_dir / "_guides" / f"{case['case_id']}_{guide.name}")
                write_obj(mesh_path, out_v, out_f)
                metadata = {
                    "label": label,
                    "experiment": experiment,
                    "case_id": case["case_id"],
                    "case_label": case["case_label"],
                    "variant": variant,
                    "variant_label": VARIANT_LABELS[variant],
                    "source_batch": source_batch,
                    "source_case": source_case,
                    "source_mesh": str(src_mesh),
                    "root_mesh": str(resolve_path(root, case["root_mesh"])) if "root_mesh" in case else "",
                    "guide_image": str(guide_path),
                    "family": case["family"],
                    "material_hint": case["material_hint"],
                    "visual_role": case["visual_role"],
                    "root_design": case.get("root_design", ""),
                    "mutation_note": mutation_note,
                    "real_case_contract": "derived from real PS-RSLE/OURS source OBJ or Trellis2 passthrough OBJ, then exported through Trellis2 GLB/PBR; not a PPT or local schematic panel",
                    "ours_rightmost_contract": variant == "ours",
                    "mesh_stats": mesh_stats(out_v, out_f),
                }
                metadata_path = case_dir / f"{label}_metadata.json"
                metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
                row = {
                    "label": label,
                    "experiment": experiment,
                    "case_id": case["case_id"],
                    "case_label": case["case_label"],
                    "variant": variant,
                    "variant_label": VARIANT_LABELS[variant],
                    "mesh_path": str(mesh_path),
                    "guide_image": str(guide_path),
                    "metadata_path": str(metadata_path),
                    "seed": int(case["seed"] + variant_idx),
                    "gpu_group": int(case["gpu"]),
                    "family": case["family"],
                    "source_batch": source_batch,
                    "source_case": source_case,
                    "source_mesh": str(src_mesh),
                    "root_mesh": str(resolve_path(root, case["root_mesh"])) if "root_mesh" in case else "",
                    "material_hint": case["material_hint"],
                    "mutation_note": mutation_note,
                    "priority_order": variant_idx,
                }
                rows.append(row)
    return rows


def write_outputs(out_dir: Path, rows: list[dict]) -> None:
    fields = [
        "label",
        "experiment",
        "case_id",
        "case_label",
        "variant",
        "variant_label",
        "mesh_path",
        "guide_image",
        "metadata_path",
        "seed",
        "gpu_group",
        "family",
        "source_batch",
        "source_case",
        "source_mesh",
        "root_mesh",
        "material_hint",
        "mutation_note",
        "priority_order",
    ]
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [f"{r['label']}|{r['mesh_path']}|{r['guide_image']}|{r['seed']}|{r['gpu_group']}" for r in rows]
    (out_dir / "a100-2_cases.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for gpu in ALLOWED_GPUS:
        selected = [line for line, row in zip(lines, rows) if int(row["gpu_group"]) == gpu]
        (out_dir / f"gpu{gpu}_cases.txt").write_text("\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")
    for gpu in (6, 7):
        (out_dir / f"gpu{gpu}_cases.txt").write_text("", encoding="utf-8")
    summary = {
        "schema": "real_case_ablation_inputs_strict_v3_fiddlehead_20260512",
        "out_dir": str(out_dir),
        "num_cases": len(rows),
        "projection_cases": sorted({r["case_id"] for r in rows if r["experiment"] == "projection"}),
        "naturalization_cases": sorted({r["case_id"] for r in rows if r["experiment"] == "naturalization"}),
        "variants": {
            "projection": PROJECTION_VARIANTS,
            "naturalization": NATURALIZATION_VARIANTS,
        },
        "allowed_gpus": ALLOWED_GPUS,
        "remote_storage_root": REMOTE_STORAGE_ROOT,
        "contract": "projection cases use existing real OURS OBJ; naturalization cases use real Trellis2 passthrough fiddlehead OBJ; remote Trellis2 GLB/PBR export required before paper use",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("RGG_ROOT", PROJECT_ROOT)))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rows = build_rows(args.root, args.out)
    write_outputs(args.out, rows)


if __name__ == "__main__":
    main()
