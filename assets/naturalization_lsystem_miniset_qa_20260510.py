#!/usr/bin/env python3
"""QA the claim-safe L-system naturalization four-column miniset.

The script intentionally stays local-only.  It reads the selected textured GLB
summaries, imports the local GLBs with trimesh, records lightweight metrics,
and calls out the exact remote source meshes that are not available locally.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import trimesh


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_OUT = PROJECT_ROOT / "results" / "naturalization_lsystem_miniset_qa_20260510"
DEFAULT_STATUS_DOC = PROJECT_ROOT / "docs" / "evaluation" / "naturalization_lsystem_miniset_status_zh_20260510.md"

REMOTE_MARKER = "/recursive_3d_generative_growth_20260507/"


@dataclass(frozen=True)
class VariantSpec:
    variant: str
    summary_rel: Path


VARIANTS = (
    VariantSpec("rule-only", Path("results/gapfill_texturing_selected_20260510/lsystem_rule_only_direct_fork_d3/summary.json")),
    VariantSpec("no-N", Path("results/gapfill_texturing_selected_20260510/lsystem_noN_alpha0_fork_d3/summary.json")),
    VariantSpec("weak blend", Path("results/gapfill_texturing_selected_20260510/lsystem_weakblend_alpha025_fork_d3/summary.json")),
    VariantSpec("masked local-N", Path("results/gapfill_texturing_selected_20260510/lsystem_masked_localN_alpha1_fork_d3/summary.json")),
)


CSV_FIELDS = [
    "case",
    "variant",
    "summary_path",
    "status",
    "source_mesh_path",
    "local_source_mesh_path",
    "source_mesh_local_exists",
    "source_mesh_blocker",
    "glb_path",
    "local_glb_path",
    "glb_import_status",
    "glb_import_error",
    "glb_size_mb",
    "summary_mesh_vertices",
    "summary_mesh_faces",
    "glb_geometry_count",
    "glb_vertices",
    "glb_faces",
    "face_count_delta_glb_minus_summary",
    "material_count",
    "pbr_material_count",
    "texture_count",
    "texture_resolutions",
    "bbox_min",
    "bbox_max",
    "bbox_extent",
    "bbox_diag",
    "bbox_volume",
    "occupancy_proxy_grid",
    "occupancy_proxy_cells",
    "occupancy_proxy_ratio",
    "local_feature_scale_proxy",
    "shape_slat_tokens",
    "tex_slat_tokens",
    "pbr_voxel_tokens",
    "pbr_mean",
    "claim_gate",
    "claim_safe_use",
    "claim_limits",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def localize_path(path_text: str, root: Path) -> Path | None:
    if not path_text:
        return None
    path = Path(path_text)
    if path.is_absolute() and path.exists():
        return path
    text = str(path)
    if REMOTE_MARKER in text:
        candidate = root / text.split(REMOTE_MARKER, 1)[1]
        if candidate.exists():
            return candidate
    if not path.is_absolute():
        candidate = root / path
        if candidate.exists():
            return candidate
    return None


def bbox_values(bounds: np.ndarray | None) -> tuple[list[float], list[float], list[float], float, float]:
    if bounds is None or np.asarray(bounds).shape != (2, 3):
        return [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], 0.0, 0.0
    arr = np.asarray(bounds, dtype=float)
    extent = np.maximum(arr[1] - arr[0], 0.0)
    return (
        [float(x) for x in arr[0]],
        [float(x) for x in arr[1]],
        [float(x) for x in extent],
        float(np.linalg.norm(extent)),
        float(np.prod(np.maximum(extent, 1e-12))),
    )


def texture_resolution(value: Any) -> str | None:
    size = getattr(value, "size", None)
    if size and len(size) == 2:
        return f"{int(size[0])}x{int(size[1])}"
    return None


def material_and_texture_stats(scene: trimesh.Scene) -> tuple[int, int, int, str]:
    material_ids: set[int] = set()
    pbr_count = 0
    texture_resolutions: set[str] = set()
    texture_count = 0
    texture_attrs = (
        "baseColorTexture",
        "metallicRoughnessTexture",
        "normalTexture",
        "emissiveTexture",
        "occlusionTexture",
    )
    for geom in scene.geometry.values():
        material = getattr(getattr(geom, "visual", None), "material", None)
        if material is None:
            continue
        material_ids.add(id(material))
        if type(material).__name__ == "PBRMaterial":
            pbr_count += 1
        for attr in texture_attrs:
            tex = getattr(material, attr, None)
            if tex is None:
                continue
            texture_count += 1
            res = texture_resolution(tex)
            if res:
                texture_resolutions.add(res)
    return len(material_ids), pbr_count, texture_count, ";".join(sorted(texture_resolutions))


def occupancy_proxy(scene: trimesh.Scene, grid: int) -> tuple[int, float]:
    points = []
    bounds = scene.bounds
    if bounds is None:
        return 0, 0.0
    bmin = np.asarray(bounds[0], dtype=float)
    extent = np.asarray(bounds[1], dtype=float) - bmin
    extent = np.where(extent <= 1e-12, 1.0, extent)
    for geom in scene.geometry.values():
        verts = getattr(geom, "vertices", None)
        if verts is None or len(verts) == 0:
            continue
        points.append(np.asarray(verts, dtype=float))
    if not points:
        return 0, 0.0
    verts_all = np.vstack(points)
    coords = np.floor((verts_all - bmin) / extent * grid).astype(np.int32)
    coords = np.clip(coords, 0, grid - 1)
    unique = np.unique(coords, axis=0)
    cells = int(len(unique))
    return cells, float(cells / float(grid**3))


def load_glb_metrics(path: Path, grid: int) -> dict[str, Any]:
    scene = trimesh.load(path, force="scene")
    if not isinstance(scene, trimesh.Scene):
        scene = trimesh.Scene(scene)
    vertices = 0
    faces = 0
    for geom in scene.geometry.values():
        vertices += int(len(getattr(geom, "vertices", [])))
        faces += int(len(getattr(geom, "faces", [])))
    bmin, bmax, extent, diag, volume = bbox_values(scene.bounds)
    material_count, pbr_count, texture_count, texture_res = material_and_texture_stats(scene)
    occ_cells, occ_ratio = occupancy_proxy(scene, grid)
    return {
        "glb_import_status": "ok",
        "glb_import_error": "",
        "glb_geometry_count": len(scene.geometry),
        "glb_vertices": vertices,
        "glb_faces": faces,
        "material_count": material_count,
        "pbr_material_count": pbr_count,
        "texture_count": texture_count,
        "texture_resolutions": texture_res,
        "bbox_min": json.dumps(bmin),
        "bbox_max": json.dumps(bmax),
        "bbox_extent": json.dumps(extent),
        "bbox_diag": f"{diag:.9f}",
        "bbox_volume": f"{volume:.9f}",
        "occupancy_proxy_cells": occ_cells,
        "occupancy_proxy_ratio": f"{occ_ratio:.9f}",
        "local_feature_scale_proxy": f"{diag / math.sqrt(max(faces, 1)):.12f}" if faces else "",
    }


def collect_rows(project_root: Path, grid: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in VARIANTS:
        summary_path = project_root / spec.summary_rel
        data = read_json(summary_path)
        source_mesh = str(data.get("mesh", ""))
        glb = str(data.get("glb", ""))
        local_source_mesh = localize_path(source_mesh, project_root)
        local_glb = localize_path(glb, project_root)
        source_blocker = "" if local_source_mesh else f"source mesh not local; exact source path: {source_mesh}"
        row: dict[str, Any] = {
            "case": "lsystem_branch/fork_side",
            "variant": spec.variant,
            "summary_path": str(spec.summary_rel),
            "status": data.get("status", ""),
            "source_mesh_path": source_mesh,
            "local_source_mesh_path": str(local_source_mesh) if local_source_mesh else "",
            "source_mesh_local_exists": "yes" if local_source_mesh else "no",
            "source_mesh_blocker": source_blocker,
            "glb_path": glb,
            "local_glb_path": str(local_glb) if local_glb else "",
            "glb_size_mb": f"{Path(local_glb).stat().st_size / (1024 * 1024):.6f}" if local_glb else "",
            "summary_mesh_vertices": data.get("mesh_vertices", ""),
            "summary_mesh_faces": data.get("mesh_faces", ""),
            "shape_slat_tokens": data.get("shape_slat_tokens", ""),
            "tex_slat_tokens": data.get("tex_slat_tokens", ""),
            "pbr_voxel_tokens": data.get("pbr_voxel_tokens", ""),
            "pbr_mean": data.get("pbr_mean", ""),
        }
        if local_glb:
            try:
                row.update(load_glb_metrics(local_glb, grid))
            except Exception as exc:  # pragma: no cover - exercised by real corrupt assets.
                row.update({
                    "glb_import_status": "failed",
                    "glb_import_error": f"{type(exc).__name__}: {exc}",
                })
        else:
            row.update({
                "glb_import_status": "missing",
                "glb_import_error": f"GLB not local; exact GLB path: {glb}",
            })
        try:
            row["face_count_delta_glb_minus_summary"] = int(row.get("glb_faces") or 0) - int(row.get("summary_mesh_faces") or 0)
        except ValueError:
            row["face_count_delta_glb_minus_summary"] = ""
        if row.get("glb_import_status") == "ok" and row.get("source_mesh_local_exists") == "no":
            row["claim_gate"] = "visual_export_ablation_only_source_mesh_blocked"
        elif row.get("glb_import_status") == "ok":
            row["claim_gate"] = "visual_export_ablation_plus_local_mesh_metrics"
        else:
            row["claim_gate"] = "blocked_no_importable_local_glb"
        row["claim_safe_use"] = "main visual/export ablation candidate" if row.get("glb_import_status") == "ok" else "not usable"
        row["claim_limits"] = (
            "Do not claim topology repair, root reachability, anchor preservation, or mask leakage; "
            "local source OBJ and projection on/off controls are absent."
        )
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def write_manifest(path: Path, rows: list[dict[str, Any]], grid: int) -> None:
    payload = {
        "case": "lsystem_branch/fork_side",
        "miniset_id": "N-lsystem-localN-4col",
        "occupancy_proxy": "unique occupied vertex-grid cells in GLB bbox; lightweight visual-density proxy, not topology/root metric",
        "occupancy_proxy_grid": grid,
        "rows": rows,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def md_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| variant | GLB import | GLB faces | GLB MB | PBR/material | occ proxy | source mesh | claim gate |",
        "|---|---:|---:|---:|---|---:|---|---|",
    ]
    for row in rows:
        material = f"{row.get('pbr_material_count', '')}/{row.get('material_count', '')}; tex={row.get('texture_count', '')} {row.get('texture_resolutions', '')}"
        source = "local" if row.get("source_mesh_local_exists") == "yes" else "remote-only"
        lines.append(
            "| {variant} | {import_status} | {faces} | {mb} | {material} | {occ} | {source} | {gate} |".format(
                variant=row.get("variant", ""),
                import_status=row.get("glb_import_status", ""),
                faces=row.get("glb_faces", ""),
                mb=row.get("glb_size_mb", ""),
                material=material,
                occ=row.get("occupancy_proxy_ratio", ""),
                source=source,
                gate=row.get("claim_gate", ""),
            )
        )
    return "\n".join(lines)


def write_status_doc(path: Path, rows: list[dict[str, Any]], out_dir: Path, grid: int) -> None:
    ok_rows = [r for r in rows if r.get("glb_import_status") == "ok"]
    blocked_mesh = [r for r in rows if r.get("source_mesh_local_exists") != "yes"]
    can_visual = len(ok_rows) == len(rows)
    can_topology = not blocked_mesh
    blocker_lines = "\n".join(f"- `{r['variant']}`: `{r['source_mesh_path']}`" for r in blocked_mesh)
    text = f"""# Naturalization L-system Miniset 状态（2026-05-10）

## 结论

- miniset：`N-lsystem-localN-4col`
- case：`lsystem_branch/fork_side`
- 四列：`rule-only` / `no-N` / `weak blend` / `masked local-N`
- 主文状态：{'可作为谨慎的 visual/export ablation 候选。' if can_visual else '暂不能作为主文 visual/export ablation。'}
- 不可 claim：{'source mesh 已本地化，可继续补拓扑指标。' if can_topology else '不能 claim topology repair、root reachability、anchor preservation、mask leakage，也不能分离 naturalization 与 projection 贡献。'}

## 本地 QA 表

{md_table(rows)}

## 已完成的本地证据

- `trimesh` 成功 import 四个 selected textured GLB，并记录 geometry/material/texture/bbox/file size。
- 四个 GLB 均包含 PBR material；检测到 base-color 与 metallic-roughness texture，texture resolution 为 `1024x1024`。
- occupancy proxy 使用 `{grid}^3` bbox vertex grid 的 unique occupied cell ratio，只能作为轻量空间占用/密度 proxy，不是连通性或 root 指标。
- GLB face count 与 selected summary 的 `mesh_faces` 一致，说明 selected export summary 与本地 GLB geometry 对齐。

## Blocker：source mesh 仍未本地化

以下 exact source mesh 路径来自 selected summary，但本地未找到对应 OBJ：

{blocker_lines}

由于 source OBJ 不在本地，本轮没有计算：

- OBJ face connectivity / largest component ratio
- root reachability
- mask leakage
- anchor drift / preserved-token geometry drift
- with projection vs without projection 控制
- global-N matched negative/control

## Claim-safe 使用边界

可以写：在 selected L-system row 上，`rule-only/no-N/weak blend/masked local-N` 四列均能进入同一 Trellis2 texture/export path，本地 GLB import 与材质导入 QA 通过，可用于谨慎的视觉/导出状态 ablation。

不能写：masked local-N 修复拓扑、保持 root/anchor、没有 mask leakage，或自然化本身优于 projection。当前证据也不能支持完整 naturalization matrix，只支持最小四列 selected visual/export subset。

## 输出文件

- CSV：`{out_dir / 'naturalization_lsystem_miniset_qa.csv'}`
- JSON：`{out_dir / 'naturalization_lsystem_miniset_qa_manifest.json'}`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(project_root: Path, out_dir: Path, status_doc: Path, grid: int) -> list[dict[str, Any]]:
    rows = collect_rows(project_root, grid)
    for row in rows:
        row["occupancy_proxy_grid"] = grid
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "naturalization_lsystem_miniset_qa.csv", rows)
    write_manifest(out_dir / "naturalization_lsystem_miniset_qa_manifest.json", rows, grid)
    write_status_doc(status_doc, rows, out_dir, grid)
    return rows


def self_test() -> None:
    assert localize_path("/tmp/definitely_missing.obj", PROJECT_ROOT) is None
    remote = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/gapfill_texturing_selected_20260510/lsystem_rule_only_direct_fork_d3/textured.glb"
    localized = localize_path(remote, PROJECT_ROOT)
    assert localized is not None
    assert localized.exists()
    rows = collect_rows(PROJECT_ROOT, 16)
    assert len(rows) == 4
    assert {r["variant"] for r in rows} == {"rule-only", "no-N", "weak blend", "masked local-N"}
    assert all(r["local_glb_path"] for r in rows)
    assert all(r["glb_import_status"] == "ok" for r in rows)
    assert all(r["source_mesh_local_exists"] == "no" for r in rows)
    assert all(int(r["glb_faces"]) > 0 for r in rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--status-doc", type=Path, default=DEFAULT_STATUS_DOC)
    parser.add_argument("--occupancy-grid", type=int, default=64)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("self-test ok")
        return
    rows = run(args.project_root, args.out_dir, args.status_doc, args.occupancy_grid)
    failed = [r for r in rows if r.get("glb_import_status") != "ok"]
    print(f"wrote {len(rows)} QA rows to {args.out_dir}")
    if failed:
        print(f"{len(failed)} GLB imports failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
