#!/usr/bin/env python3
"""CPU mesh diagnostics for recursive 3D growth paper assets.

The script prefers installed geometry libraries when available, but keeps
minimal OBJ/PLY readers so OBJ/ASCII-PLY metrics remain reproducible on a
plain CPU Python environment. GLB/GLTF is loaded only when trimesh can handle it.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

try:
    import numpy as np
except Exception as exc:  # pragma: no cover - numpy is expected in this repo
    raise SystemExit(f"numpy is required for mesh metrics: {exc}")

try:
    import trimesh  # type: ignore
except Exception:  # pragma: no cover - fallback parsers cover OBJ/PLY
    trimesh = None


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "results" / "metric_enrichment_20260513"
SUPPORTED_EXTENSIONS = {".obj", ".ply", ".glb", ".gltf"}
DEFAULT_PRIORITY_CSVS = [
    ROOT / "results" / "experiment3_sparse_latent_vs_meshspace_20260511" / "experiment3_master_manifest.csv",
    ROOT / "results" / "experiment3_sparse_latent_vs_meshspace_20260511" / "experiment3_ps_rslg_metrics.csv",
    ROOT / "results" / "experiment3_sparse_latent_vs_meshspace_20260511" / "experiment3_trellis2_baseline_metrics.csv",
    ROOT / "results" / "experiment3_sparse_latent_vs_meshspace_20260511" / "experiment3_ps_rslg_metric_rows_20260511.csv",
    ROOT / "results" / "publication_hunyuan_text_root_meshspace_20260511" / "hunyuan_text_root_meshspace_metrics.csv",
    ROOT / "results" / "strict_visual_matched_cases_V24_priority_rerun_20260510_dryrun" / "manifest.csv",
    ROOT / "results" / "real_case_ablation_inputs_20260512" / "manifest.csv",
    ROOT / "results" / "masked_naturalization_ablation_20260510_seed20260512" / "manifest.csv",
]
DEFAULT_PRIORITY_DIRS = [
    ROOT / "results" / "experiment3_sparse_latent_vs_meshspace_20260511",
    ROOT / "results" / "publication_hunyuan_text_root_meshspace_20260511",
    ROOT / "results" / "strict_visual_matched_cases_V24_priority_rerun_20260510_dryrun",
    ROOT / "results" / "real_case_ablation_inputs_20260512",
    ROOT / "results" / "masked_naturalization_ablation_20260510_seed20260512",
]


def parse_obj(path: Path) -> tuple[np.ndarray, np.ndarray]:
    vertices: list[list[float]] = []
    triangles: list[list[int]] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if parts[0] == "v" and len(parts) >= 4:
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif parts[0] == "f" and len(parts) >= 4:
                face: list[int] = []
                for token in parts[1:]:
                    raw = token.split("/")[0]
                    if not raw:
                        continue
                    idx = int(raw)
                    face.append(idx - 1 if idx > 0 else len(vertices) + idx)
                for i in range(1, len(face) - 1):
                    triangles.append([face[0], face[i], face[i + 1]])
    return np.asarray(vertices, dtype=np.float64), np.asarray(triangles, dtype=np.int64)


def parse_ascii_ply(path: Path) -> tuple[np.ndarray, np.ndarray]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        if handle.readline().strip() != "ply":
            raise ValueError("not a PLY file")
        vertex_count = 0
        face_count = 0
        fmt = ""
        for line in handle:
            line = line.strip()
            if line.startswith("format "):
                fmt = line
            elif line.startswith("element vertex "):
                vertex_count = int(line.split()[-1])
            elif line.startswith("element face "):
                face_count = int(line.split()[-1])
            elif line == "end_header":
                break
        if "ascii" not in fmt:
            raise ValueError("fallback PLY parser supports ASCII PLY only")
        vertices = []
        for _ in range(vertex_count):
            parts = handle.readline().split()
            vertices.append([float(parts[0]), float(parts[1]), float(parts[2])])
        triangles = []
        for _ in range(face_count):
            parts = handle.readline().split()
            n = int(parts[0])
            face = [int(v) for v in parts[1 : 1 + n]]
            for i in range(1, len(face) - 1):
                triangles.append([face[0], face[i], face[i + 1]])
    return np.asarray(vertices, dtype=np.float64), np.asarray(triangles, dtype=np.int64)


def load_mesh_arrays(path: Path) -> tuple[np.ndarray, np.ndarray, str]:
    ext = path.suffix.lower()
    if trimesh is not None:
        try:
            loaded = trimesh.load(path, force="mesh", process=False)
            if hasattr(loaded, "geometry"):
                parts = [g for g in loaded.geometry.values() if len(g.vertices) and len(g.faces)]
                loaded = trimesh.util.concatenate(parts) if parts else loaded
            vertices = np.asarray(loaded.vertices, dtype=np.float64)
            faces = np.asarray(loaded.faces, dtype=np.int64)
            if faces.ndim == 2 and faces.shape[1] == 3:
                return vertices, faces, "trimesh"
        except Exception:
            if ext in {".glb", ".gltf"}:
                raise
    if ext == ".obj":
        vertices, faces = parse_obj(path)
        return vertices, faces, "fallback_obj"
    if ext == ".ply":
        vertices, faces = parse_ascii_ply(path)
        return vertices, faces, "fallback_ascii_ply"
    raise ValueError(f"no CPU loader available for {ext}")


def cheap_mesh_size(path: Path) -> tuple[int | None, int | None]:
    ext = path.suffix.lower()
    if ext == ".obj":
        vertices = 0
        faces = 0
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if line.startswith("v "):
                    vertices += 1
                elif line.startswith("f "):
                    n = max(len(line.split()) - 1, 0)
                    faces += max(n - 2, 0)
        return vertices, faces
    return None, None


def valid_face_mask(vertices: np.ndarray, faces: np.ndarray, area_eps: float = 1e-14) -> np.ndarray:
    if len(faces) == 0:
        return np.zeros((0,), dtype=bool)
    in_range = (faces >= 0).all(axis=1) & (faces < len(vertices)).all(axis=1)
    unique = (faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2]) & (faces[:, 0] != faces[:, 2])
    mask = in_range & unique
    areas = np.zeros(len(faces), dtype=np.float64)
    if mask.any():
        tri = vertices[faces[mask]]
        areas[mask] = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
    return mask & (areas > area_eps)


def edge_counter(faces: np.ndarray) -> Counter[tuple[int, int]]:
    counts: Counter[tuple[int, int]] = Counter()
    for a, b, c in faces.tolist():
        for u, v in ((a, b), (b, c), (c, a)):
            counts[(u, v) if u < v else (v, u)] += 1
    return counts


def face_component_sizes(faces: np.ndarray) -> list[int]:
    if len(faces) == 0:
        return []
    by_edge: dict[tuple[int, int], list[int]] = defaultdict(list)
    for idx, (a, b, c) in enumerate(faces.tolist()):
        for u, v in ((a, b), (b, c), (c, a)):
            by_edge[(u, v) if u < v else (v, u)].append(idx)
    neighbors: list[list[int]] = [[] for _ in range(len(faces))]
    for incident in by_edge.values():
        if len(incident) < 2:
            continue
        for face_idx in incident:
            neighbors[face_idx].extend(j for j in incident if j != face_idx)
    seen = np.zeros(len(faces), dtype=bool)
    sizes: list[int] = []
    for start in range(len(faces)):
        if seen[start]:
            continue
        queue: deque[int] = deque([start])
        seen[start] = True
        size = 0
        while queue:
            cur = queue.popleft()
            size += 1
            for nxt in neighbors[cur]:
                if not seen[nxt]:
                    seen[nxt] = True
                    queue.append(nxt)
        sizes.append(size)
    return sorted(sizes, reverse=True)


def quantized_weld(vertices: np.ndarray, faces: np.ndarray, tolerance: float) -> tuple[np.ndarray, np.ndarray, int]:
    if len(vertices) == 0 or tolerance <= 0:
        return vertices.copy(), faces.copy(), 0
    keys = np.round(vertices / tolerance).astype(np.int64)
    remap: dict[tuple[int, int, int], int] = {}
    new_vertices: list[np.ndarray] = []
    inverse = np.empty(len(vertices), dtype=np.int64)
    for idx, key_arr in enumerate(keys):
        key = tuple(int(x) for x in key_arr)
        if key not in remap:
            remap[key] = len(new_vertices)
            new_vertices.append(vertices[idx])
        inverse[idx] = remap[key]
    new_faces = inverse[faces] if len(faces) else faces.copy()
    welded_vertices = np.asarray(new_vertices, dtype=np.float64)
    mask = valid_face_mask(welded_vertices, new_faces)
    return welded_vertices, new_faces[mask], int(len(vertices) - len(welded_vertices))


def triangle_stats(vertices: np.ndarray, faces: np.ndarray) -> dict[str, Any]:
    if len(faces) == 0:
        return {
            "face_area_mean": 0.0,
            "face_area_median": 0.0,
            "triangle_aspect_mean": "",
            "triangle_aspect_p95": "",
            "triangle_aspect_max": "",
            "triangle_quality_mean": "",
            "triangle_quality_min": "",
        }
    tri = vertices[faces]
    e0 = np.linalg.norm(tri[:, 1] - tri[:, 0], axis=1)
    e1 = np.linalg.norm(tri[:, 2] - tri[:, 1], axis=1)
    e2 = np.linalg.norm(tri[:, 0] - tri[:, 2], axis=1)
    cross = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    area = 0.5 * np.linalg.norm(cross, axis=1)
    longest = np.maximum.reduce([e0, e1, e2])
    altitude = np.divide(2.0 * area, longest, out=np.full_like(area, np.nan), where=longest > 0)
    aspect = np.divide(longest, altitude, out=np.full_like(area, np.nan), where=altitude > 0)
    denom = e0 * e0 + e1 * e1 + e2 * e2
    quality = np.divide(4.0 * math.sqrt(3.0) * area, denom, out=np.zeros_like(area), where=denom > 0)
    aspect_finite = aspect[np.isfinite(aspect)]
    return {
        "face_area_mean": float(np.mean(area)),
        "face_area_median": float(np.median(area)),
        "triangle_aspect_mean": float(np.mean(aspect_finite)) if len(aspect_finite) else "",
        "triangle_aspect_p95": float(np.percentile(aspect_finite, 95)) if len(aspect_finite) else "",
        "triangle_aspect_max": float(np.max(aspect_finite)) if len(aspect_finite) else "",
        "triangle_quality_mean": float(np.mean(quality)) if len(quality) else "",
        "triangle_quality_min": float(np.min(quality)) if len(quality) else "",
    }


def signed_volume(vertices: np.ndarray, faces: np.ndarray) -> float:
    if len(faces) == 0:
        return 0.0
    tri = vertices[faces]
    vols = np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])) / 6.0
    return float(abs(np.sum(vols)))


def base_metrics(path: Path, vertices: np.ndarray, faces_in: np.ndarray, loader: str, weld_tolerance: float) -> dict[str, Any]:
    finite_vertices = bool(np.isfinite(vertices).all()) if len(vertices) else True
    in_range = (faces_in >= 0).all(axis=1) & (faces_in < len(vertices)).all(axis=1) if len(faces_in) else np.zeros(0, dtype=bool)
    raw_degenerate = int(len(faces_in) - int(valid_face_mask(vertices, faces_in).sum()))
    faces = faces_in[valid_face_mask(vertices, faces_in)]
    edge_counts = edge_counter(faces)
    boundary_edges = sum(1 for count in edge_counts.values() if count == 1)
    nonmanifold_edges = sum(1 for count in edge_counts.values() if count > 2)
    component_sizes = face_component_sizes(faces)
    used_vertices = int(len(set(faces.reshape(-1).tolist()))) if len(faces) else 0
    bbox_min = vertices.min(axis=0) if len(vertices) else np.zeros(3)
    bbox_max = vertices.max(axis=0) if len(vertices) else np.zeros(3)
    extent = bbox_max - bbox_min
    area_stats = triangle_stats(vertices, faces)
    surface_area = float(area_stats["face_area_mean"] * len(faces)) if len(faces) else 0.0
    is_watertight = bool(len(faces) > 0 and boundary_edges == 0 and nonmanifold_edges == 0)
    volume = signed_volume(vertices, faces) if is_watertight else ""
    compactness = ""
    if is_watertight and surface_area > 0 and volume != "":
        compactness = float((math.pi ** (1.0 / 3.0)) * ((6.0 * float(volume)) ** (2.0 / 3.0)) / surface_area)
    welded_vertices, welded_faces, welded_reduction = quantized_weld(vertices, faces, weld_tolerance)
    welded_components = face_component_sizes(welded_faces)
    result: dict[str, Any] = {
        "label": path.stem,
        "path": str(path),
        "extension": path.suffix.lower(),
        "status": "ok",
        "loader": loader,
        "load_error": "",
        "vertices": int(len(vertices)),
        "triangles": int(len(faces)),
        "raw_faces_in_file": int(len(faces_in)),
        "invalid_or_degenerate_faces": raw_degenerate,
        "finite_vertices": finite_vertices,
        "used_vertices": used_vertices,
        "isolated_vertex_count": int(max(len(vertices) - used_vertices, 0)),
        "bbox_min_x": float(bbox_min[0]),
        "bbox_min_y": float(bbox_min[1]),
        "bbox_min_z": float(bbox_min[2]),
        "bbox_max_x": float(bbox_max[0]),
        "bbox_max_y": float(bbox_max[1]),
        "bbox_max_z": float(bbox_max[2]),
        "bbox_extent_x": float(extent[0]),
        "bbox_extent_y": float(extent[1]),
        "bbox_extent_z": float(extent[2]),
        "bbox_diag": float(np.linalg.norm(extent)),
        "bbox_volume": float(np.prod(extent)) if len(vertices) else 0.0,
        "raw_component_count": int(len(component_sizes)),
        "largest_raw_component_faces": int(component_sizes[0]) if component_sizes else 0,
        "largest_raw_component_face_ratio": float(component_sizes[0] / len(faces)) if component_sizes and len(faces) else "",
        "small_raw_component_count_lt10_faces": int(sum(1 for size in component_sizes if size < 10)),
        "weld_tolerance": float(weld_tolerance),
        "welded_vertices": int(len(welded_vertices)),
        "welded_vertex_reduction": welded_reduction,
        "welded_triangles": int(len(welded_faces)),
        "welded_component_count": int(len(welded_components)),
        "largest_welded_component_faces": int(welded_components[0]) if welded_components else 0,
        "largest_welded_component_face_ratio": float(welded_components[0] / len(welded_faces))
        if welded_components and len(welded_faces)
        else "",
        "boundary_edge_count": int(boundary_edges),
        "nonmanifold_edge_count": int(nonmanifold_edges),
        "unique_edge_count": int(len(edge_counts)),
        "is_watertight": is_watertight,
        "surface_area": surface_area,
        "signed_volume": volume,
        "compactness_sphericity": compactness,
        "renderability_proxy_available": bool(len(faces) > 0 and finite_vertices),
        "renderability_proxy_reason": "triangular mesh with finite vertices" if len(faces) > 0 and finite_vertices else "no valid triangles",
        "primary_connectivity_metric": "raw face-edge components plus quantized vertex weld",
    }
    result.update(area_stats)
    return result


def measure_mesh(path: Path | str, weld_tolerance: float = 0.002) -> dict[str, Any]:
    path = Path(path)
    try:
        vertices, faces, loader = load_mesh_arrays(path)
        return base_metrics(path, vertices, faces, loader, weld_tolerance)
    except Exception as exc:
        return {
            "label": path.stem,
            "path": str(path),
            "extension": path.suffix.lower(),
            "status": "skipped",
            "loader": "",
            "load_error": str(exc),
            "renderability_proxy_available": False,
        }


def measure_mesh_guarded(
    path: Path | str,
    weld_tolerance: float = 0.002,
    max_faces: int | None = None,
) -> dict[str, Any]:
    path = Path(path)
    cheap_vertices, cheap_faces = cheap_mesh_size(path)
    if max_faces is not None and cheap_faces is not None and cheap_faces > max_faces:
        return {
            "label": path.stem,
            "path": str(path),
            "extension": path.suffix.lower(),
            "status": "skipped",
            "loader": "cheap_obj_counter",
            "load_error": f"face_count_above_limit:{cheap_faces}>{max_faces}",
            "vertices": cheap_vertices,
            "raw_faces_in_file": cheap_faces,
            "renderability_proxy_available": False,
        }
    return measure_mesh(path, weld_tolerance=weld_tolerance)


def discover_inputs(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            found.append(path)
        elif path.is_dir():
            found.extend(p for p in path.rglob("*") if p.suffix.lower() in SUPPORTED_EXTENSIONS)
    return sorted(dict.fromkeys(found), key=lambda p: str(p))


def resolve_path(raw: str, csv_path: Path) -> Path | None:
    raw = (raw or "").strip()
    if not raw or raw.upper() == "N/A":
        return None
    path = Path(raw)
    candidates = [path] if path.is_absolute() else [ROOT / path, csv_path.parent / path]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    if path.suffix.lower() in SUPPORTED_EXTENSIONS:
        return candidates[0]
    return None


def candidate_mesh_columns(row: dict[str, str]) -> list[str]:
    preferred = [
        "asset_path",
        "mesh_path",
        "source_path",
        "path",
        "source_mesh",
        "root_or_source",
        "render_path",
        "preview_path",
    ]
    cols = [col for col in preferred if col in row]
    cols.extend(col for col in row if col not in cols and ("mesh" in col.lower() or "asset" in col.lower() or col.lower().endswith("path")))
    return cols


def rows_from_csv(csv_path: Path) -> list[tuple[Path, dict[str, Any]]]:
    if not csv_path.exists():
        return []
    out: list[tuple[Path, dict[str, Any]]] = []
    with csv_path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, row in enumerate(reader):
            chosen: Path | None = None
            source_col = ""
            for col in candidate_mesh_columns(row):
                candidate = resolve_path(row.get(col, ""), csv_path)
                if candidate is not None and candidate.suffix.lower() in SUPPORTED_EXTENSIONS:
                    chosen = candidate
                    source_col = col
                    break
            if chosen is None:
                continue
            metadata = {
                "source_csv": str(csv_path),
                "source_csv_row": idx,
                "source_csv_mesh_column": source_col,
            }
            for key in (
                "label",
                "case_id",
                "case_short",
                "category",
                "family",
                "method",
                "method_id",
                "variant",
                "variant_label",
                "experiment",
                "task_id",
                "task_family",
                "priority",
                "claim_role",
                "ready_for_main",
                "route_status",
                "visual_qa_status",
                "failure_label",
                "projection_schedule",
                "naturalization_scope",
            ):
                if key in row:
                    metadata[f"manifest_{key}"] = row.get(key, "")
            out.append((chosen, metadata))
    return out


def priority_manifest_inputs(csv_paths: list[Path]) -> list[tuple[Path, dict[str, Any]]]:
    pairs: list[tuple[Path, dict[str, Any]]] = []
    for csv_path in csv_paths:
        pairs.extend(rows_from_csv(csv_path))
    dedup: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path, meta in pairs:
        key = str(path)
        if key not in dedup:
            dedup[key] = (path, meta)
        else:
            dedup[key][1].update({k: v for k, v in meta.items() if k.startswith("manifest_") and v})
    return list(dedup.values())


def measure_with_metadata(
    path: Path,
    metadata: dict[str, Any],
    weld_tolerance: float,
    max_faces: int | None = None,
) -> dict[str, Any]:
    row = measure_mesh_guarded(path, weld_tolerance=weld_tolerance, max_faces=max_faces)
    for key, value in metadata.items():
        row.setdefault(key, value)
    if metadata.get("manifest_label"):
        row["label"] = metadata["manifest_label"]
    elif metadata.get("manifest_case_id") and metadata.get("manifest_variant"):
        row["label"] = f"{metadata['manifest_case_id']}::{metadata['manifest_variant']}"
    elif metadata.get("manifest_case_id"):
        row["label"] = metadata["manifest_case_id"]
    return row


def write_outputs(rows: list[dict[str, Any]], out_dir: Path, prefix: str) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{prefix}.json"
    csv_path = out_dir / f"{prefix}.csv"
    json_path.write_text(json.dumps({"rows": rows}, indent=2), encoding="utf-8")
    fields = sorted({key for row in rows for key in row.keys()})
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return json_path, csv_path


def write_readme(rows: list[dict[str, Any]], out_dir: Path, prefix: str, inputs: list[Path]) -> Path:
    ok = [r for r in rows if r.get("status") == "ok"]
    skipped = [r for r in rows if r.get("status") != "ok"]
    one_component = [r for r in ok if r.get("welded_component_count") == 1]
    watertight = [r for r in ok if r.get("is_watertight") is True]
    text = [
        "# Metric Enrichment 20260513",
        "",
        "CPU-only mesh diagnostics generated by `assets/mesh_metric_enrichment_20260513.py`.",
        "",
        f"- Inputs requested: {len(inputs)}",
        f"- Meshes measured: {len(ok)}",
        f"- Skipped/unloaded: {len(skipped)}",
        f"- Welded single-component meshes: {len(one_component)}",
        f"- Watertight meshes with volume/compactness: {len(watertight)}",
        "",
        "Outputs:",
        f"- `{prefix}.csv`: flat table for paper/result aggregation.",
        f"- `{prefix}.json`: full rows including skipped loader errors.",
        "",
        "Metrics include raw face-edge components, tolerance-welded components, boundary/non-manifold edges, degenerate faces, surface area, volume when watertight, bounding box extents, sphericity compactness, triangle aspect/quality, and renderability proxy availability.",
    ]
    readme = out_dir / "README.md"
    readme.write_text("\n".join(text) + "\n", encoding="utf-8")
    return readme


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", type=Path, help="mesh files or directories to scan")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--prefix", default="mesh_metric_enrichment_20260513")
    parser.add_argument("--weld-tolerance", type=float, default=0.002)
    parser.add_argument("--manifest-csv", action="append", type=Path, default=[], help="manifest/metrics CSV containing mesh paths")
    parser.add_argument("--priority-defaults", action="store_true", help="use the paper-priority manifest and metric CSVs")
    parser.add_argument("--scan-priority-dirs", action="store_true", help="also scan priority result directories for mesh files")
    parser.add_argument("--limit", type=int, default=0, help="measure only the first N resolved meshes")
    parser.add_argument("--max-faces", type=int, default=750000, help="skip OBJ files above this triangle count; 0 disables")
    args = parser.parse_args()
    csv_paths = list(args.manifest_csv)
    if args.priority_defaults or (not args.inputs and not csv_paths):
        csv_paths.extend(DEFAULT_PRIORITY_CSVS)
    manifest_pairs = priority_manifest_inputs(csv_paths)
    manifest_paths = {str(path) for path, _meta in manifest_pairs}
    input_roots = list(args.inputs)
    if args.scan_priority_dirs or (not args.inputs and not csv_paths):
        input_roots.extend(DEFAULT_PRIORITY_DIRS)
    direct_paths = [path for path in discover_inputs(input_roots) if str(path.resolve()) not in manifest_paths]
    max_faces = args.max_faces if args.max_faces > 0 else None
    jobs = [("manifest", path, meta) for path, meta in manifest_pairs]
    jobs.extend(("direct", path, {}) for path in direct_paths)
    if args.limit > 0:
        jobs = jobs[: args.limit]
    rows = []
    for idx, (kind, path, meta) in enumerate(jobs, start=1):
        print(f"[{idx}/{len(jobs)}] {kind} {path}", flush=True)
        if kind == "manifest":
            rows.append(measure_with_metadata(path, meta, args.weld_tolerance, max_faces=max_faces))
        else:
            rows.append(measure_mesh_guarded(path, weld_tolerance=args.weld_tolerance, max_faces=max_faces))
    paths = [path for _kind, path, _meta in jobs]
    json_path, csv_path = write_outputs(rows, args.out_dir, args.prefix)
    readme = write_readme(rows, args.out_dir, args.prefix, paths)
    print(f"measured={sum(1 for r in rows if r.get('status') == 'ok')} skipped={sum(1 for r in rows if r.get('status') != 'ok')}")
    print(f"json={json_path}")
    print(f"csv={csv_path}")
    print(f"readme={readme}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
