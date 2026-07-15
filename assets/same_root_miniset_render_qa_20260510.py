#!/usr/bin/env python3
"""Export and render-QA the same-root claim-safe miniset.

This script is intentionally narrow: it reads the selected-final manifest,
uses only the local final OBJ rows for vine/tree compete depth-3 projection
variants, exports GLB copies, and creates deterministic white-background
software render previews plus CSV/JSON manifests.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import trimesh
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "results/publication_ablation_metrics_20260510/manifest_selected_final_rows.csv"
DEFAULT_OUT = ROOT / "results/same_root_miniset_render_qa_20260510"
DEFAULT_DOC = ROOT / "docs/evaluation/same_root_miniset_render_qa_status_zh_20260510.md"
TARGET_VARIANTS = ("direct", "final-only", "prune")
CASE_ORDER = ("vine_compete_d3", "tree_compete_d3")


@dataclass
class RowResult:
    case: str
    variant: str
    status: str
    final_mesh_path: str
    final_glb_path: str
    render_iso_path: str
    render_front_path: str
    render_sheet_path: str
    obj_exists: bool
    glb_export_ok: bool
    glb_import_ok: bool
    render_ok: bool
    vertices_manifest: str
    faces_manifest: str
    components_manifest: str
    lcr_manifest: str
    vertices_loaded: int | str
    faces_loaded: int | str
    glb_size_mb: float | str
    obj_size_mb: float | str
    iso_nonwhite_ratio: float | str
    front_nonwhite_ratio: float | str
    iso_corner_white: bool | str
    front_corner_white: bool | str
    blocker: str
    notes: str


def rel(path: Path | str) -> str:
    p = Path(path)
    try:
        return str(p.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def load_selected_rows(manifest: Path, include_tree: bool) -> list[dict[str, str]]:
    wanted_cases = {"vine_compete_d3"}
    if include_tree:
        wanted_cases.add("tree_compete_d3")
    with manifest.open(newline="") as f:
        rows = list(csv.DictReader(f))
    selected = [
        r
        for r in rows
        if r.get("matrix") == "same-root"
        and r.get("case") in wanted_cases
        and r.get("variant") in TARGET_VARIANTS
    ]
    order = {case: i for i, case in enumerate(CASE_ORDER)}
    variant_order = {variant: i for i, variant in enumerate(TARGET_VARIANTS)}
    selected.sort(key=lambda r: (order.get(r["case"], 99), variant_order.get(r["variant"], 99)))
    return selected


def load_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(str(path), force="scene", process=False)
    if isinstance(loaded, trimesh.Trimesh):
        return loaded
    if isinstance(loaded, trimesh.Scene):
        meshes = [g for g in loaded.geometry.values() if isinstance(g, trimesh.Trimesh) and len(g.vertices) > 0]
        if not meshes:
            raise ValueError(f"scene contains no mesh geometry: {path}")
        return trimesh.util.concatenate(meshes)
    raise TypeError(f"unsupported mesh type for {path}: {type(loaded).__name__}")


def normalize_vertices(vertices: np.ndarray, view: str) -> tuple[np.ndarray, np.ndarray]:
    angles = {
        "front": (0.0, 0.0, 0.0),
        "iso": (math.radians(18), math.radians(-34), math.radians(0)),
    }[view]
    rx, ry, rz = angles
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    mx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]], dtype=np.float64)
    my = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=np.float64)
    mz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]], dtype=np.float64)
    rot = mz @ my @ mx
    pts = vertices @ rot.T
    center = (pts.min(axis=0) + pts.max(axis=0)) * 0.5
    span = max(float(np.max(pts.max(axis=0) - pts.min(axis=0))), 1e-9)
    return (pts - center) / span, rot


def render_mesh_white(
    mesh: trimesh.Trimesh,
    out: Path,
    view: str,
    size: int = 1400,
    max_faces: int = 120_000,
) -> dict[str, object]:
    bg = np.array([255, 255, 255], dtype=np.uint8)
    img = Image.new("RGB", (size, size), tuple(int(x) for x in bg))
    draw = ImageDraw.Draw(img, "RGBA")
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(vertices) == 0 or len(faces) == 0:
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)
        return {"nonwhite_ratio": 0.0, "corner_white": True, "blocker": "empty mesh"}
    if len(faces) > max_faces:
        faces = faces[np.linspace(0, len(faces) - 1, max_faces, dtype=np.int64)]
    pts, _rot = normalize_vertices(vertices, view)
    tri = pts[faces]
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    norm = np.linalg.norm(normals, axis=1)
    valid = norm > 1e-12
    tri = tri[valid]
    normals = normals[valid] / norm[valid, None]
    if len(tri) == 0:
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)
        return {"nonwhite_ratio": 0.0, "corner_white": True, "blocker": "all sampled triangles degenerate"}
    light = np.array([0.35, -0.42, 0.84], dtype=np.float64)
    light /= np.linalg.norm(light)
    z = tri[:, :, 2].mean(axis=1)
    order = np.argsort(z)
    z_norm = (z - z.min()) / max(float(z.max() - z.min()), 1e-9)
    scale = size * 0.74
    x_mid = size * 0.5
    y_mid = size * 0.52
    base = np.array([86, 114, 111], dtype=np.float64)
    high = np.array([206, 171, 87], dtype=np.float64)
    for idx in order:
        poly = [(float(x_mid + p[0] * scale), float(y_mid - p[1] * scale)) for p in tri[idx, :, :2]]
        shade = 0.36 + 0.64 * max(float(normals[idx] @ light), 0.0)
        tone = base * (1.0 - z_norm[idx]) + high * z_norm[idx]
        color = tuple(int(np.clip(c * shade, 0, 246)) for c in tone)
        draw.polygon(poly, fill=(*color, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    arr = np.asarray(img)
    diff = np.abs(arr.astype(np.int16) - bg[None, None, :].astype(np.int16)).sum(axis=2)
    corner = np.concatenate(
        [
            arr[:40, :40].reshape(-1, 3),
            arr[:40, -40:].reshape(-1, 3),
            arr[-40:, :40].reshape(-1, 3),
            arr[-40:, -40:].reshape(-1, 3),
        ],
        axis=0,
    )
    return {
        "nonwhite_ratio": float(np.mean(diff > 20)),
        "corner_white": bool(np.all(corner > 248)),
        "blocker": "",
    }


def save_sheet(paths: Iterable[Path], out: Path) -> None:
    images = [Image.open(p).convert("RGB") for p in paths]
    if not images:
        return
    w, h = images[0].size
    sheet = Image.new("RGB", (w * len(images), h), (255, 255, 255))
    for i, img in enumerate(images):
        sheet.paste(img, (i * w, 0))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)


def qa_row(row: dict[str, str], out_dir: Path) -> RowResult:
    case = row["case"]
    variant = row["variant"]
    mesh_path = Path(row["final_mesh_path"])
    if not mesh_path.is_absolute():
        mesh_path = ROOT / mesh_path
    stem = f"{case}__{variant.replace('-', '_')}"
    mesh_copy = out_dir / "meshes" / f"{stem}.obj"
    glb_path = out_dir / "glb" / f"{stem}.glb"
    render_iso = out_dir / "renders" / f"{stem}__iso_white.png"
    render_front = out_dir / "renders" / f"{stem}__front_white.png"
    render_sheet = out_dir / "contact_sheets" / f"{stem}__white_qa_sheet.png"

    obj_exists = mesh_path.exists()
    blocker = ""
    glb_export_ok = False
    glb_import_ok = False
    render_ok = False
    vertices_loaded: int | str = ""
    faces_loaded: int | str = ""
    glb_size_mb: float | str = ""
    obj_size_mb: float | str = ""
    iso_nonwhite: float | str = ""
    front_nonwhite: float | str = ""
    iso_corner: bool | str = ""
    front_corner: bool | str = ""
    final_glb = ""

    if not obj_exists:
        blocker = f"local final OBJ missing: {mesh_path}"
    else:
        try:
            mesh = load_mesh(mesh_path)
            vertices_loaded = int(len(mesh.vertices))
            faces_loaded = int(len(mesh.faces))
            obj_size_mb = round(mesh_path.stat().st_size / 1_000_000, 6)
            mesh_copy.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(mesh_path, mesh_copy)
            glb_path.parent.mkdir(parents=True, exist_ok=True)
            mesh.export(str(glb_path), file_type="glb")
            glb_export_ok = glb_path.exists() and glb_path.stat().st_size > 0
            if glb_export_ok:
                glb_size_mb = round(glb_path.stat().st_size / 1_000_000, 6)
                imported = load_mesh(glb_path)
                glb_import_ok = len(imported.vertices) > 0 and len(imported.faces) > 0
                final_glb = rel(glb_path)
            iso = render_mesh_white(mesh, render_iso, "iso")
            front = render_mesh_white(mesh, render_front, "front")
            save_sheet([render_iso, render_front], render_sheet)
            iso_nonwhite = round(float(iso["nonwhite_ratio"]), 6)
            front_nonwhite = round(float(front["nonwhite_ratio"]), 6)
            iso_corner = bool(iso["corner_white"])
            front_corner = bool(front["corner_white"])
            render_ok = (
                not iso["blocker"]
                and not front["blocker"]
                and iso_nonwhite > 0.01
                and front_nonwhite > 0.01
                and bool(iso_corner)
                and bool(front_corner)
            )
            blockers = [str(iso["blocker"]), str(front["blocker"])]
            blocker = "; ".join(b for b in blockers if b)
        except Exception as exc:
            blocker = f"{type(exc).__name__}: {exc}"

    status = "complete" if obj_exists and glb_export_ok and glb_import_ok and render_ok else "blocked"
    return RowResult(
        case=case,
        variant=variant,
        status=status,
        final_mesh_path=rel(mesh_path),
        final_glb_path=final_glb,
        render_iso_path=rel(render_iso) if render_iso.exists() else "",
        render_front_path=rel(render_front) if render_front.exists() else "",
        render_sheet_path=rel(render_sheet) if render_sheet.exists() else "",
        obj_exists=obj_exists,
        glb_export_ok=glb_export_ok,
        glb_import_ok=glb_import_ok,
        render_ok=render_ok,
        vertices_manifest=row.get("vertices", ""),
        faces_manifest=row.get("faces", ""),
        components_manifest=row.get("component_count", ""),
        lcr_manifest=row.get("largest_component_ratio", ""),
        vertices_loaded=vertices_loaded,
        faces_loaded=faces_loaded,
        glb_size_mb=glb_size_mb,
        obj_size_mb=obj_size_mb,
        iso_nonwhite_ratio=iso_nonwhite,
        front_nonwhite_ratio=front_nonwhite,
        iso_corner_white=iso_corner,
        front_corner_white=front_corner,
        blocker=blocker,
        notes=row.get("notes", ""),
    )


def write_csv(path: Path, rows: list[RowResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(RowResult.__dataclass_fields__.keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_markdown(path: Path, rows: list[RowResult], include_tree: bool) -> None:
    vine = [r for r in rows if r.case == "vine_compete_d3"]
    tree = [r for r in rows if r.case == "tree_compete_d3"]
    completed = [r for r in rows if r.status == "complete"]
    blocked = [r for r in rows if r.status != "complete"]
    lines = [
        "# Same-root miniset GLB/render QA status（2026-05-10）",
        "",
        "## 范围",
        "",
        "- 主目标：`vine_compete_d3` 的 `direct` / `final-only` / `prune` 三列。",
        f"- 备选纳入：{'是，包含 tree_compete_d3 三列。' if include_tree else '否。'}",
        "- 本轮仅验证已有本地 final OBJ，导出本地 GLB，并生成固定白底软件 render QA；未 SSH，未修改 `paper_siga/main.tex`。",
        "",
        "## 行状态",
        "",
        "| case | variant | status | OBJ | GLB | render QA | components | LCR | blocker |",
        "|---|---|---|---|---|---|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| `{r.case}` | `{r.variant}` | {r.status} | {'yes' if r.obj_exists else 'no'} | "
            f"{'yes' if r.glb_export_ok and r.glb_import_ok else 'no'} | {'yes' if r.render_ok else 'no'} | "
            f"{r.components_manifest} | {r.lcr_manifest} | {r.blocker or ''} |"
        )
    lines += [
        "",
        "## 输出文件",
        "",
        "- metrics: `results/same_root_miniset_render_qa_20260510/metrics/same_root_miniset_render_qa_metrics.csv`",
        "- manifest: `results/same_root_miniset_render_qa_20260510/manifest/same_root_miniset_render_qa_manifest.json`",
        "- GLB: `results/same_root_miniset_render_qa_20260510/glb/`",
        "- renders: `results/same_root_miniset_render_qa_20260510/renders/` 与 `contact_sheets/`",
        "",
        "## 可写进主文的保守结论",
        "",
    ]
    if len(vine) == 3 and all(r.status == "complete" for r in vine):
        lines.append(
            "- 在 matched `vine_compete_d3` depth-3 projection 子集上，三列已有本地 final OBJ，且本轮 GLB import 与固定白底 render QA 均通过。指标支持保守写法：direct recursion 高碎片化（2059 components, LCR=0.9049），final-only 明显降低碎片（2 components, LCR=0.9934），per-depth prune/projection 达到单连通主结果（1 component, LCR=1.0）。"
        )
    else:
        lines.append(
            "- `vine_compete_d3` 三列尚不能全部作为主文 QA 闭合行；只能引用已完成行，并保留 blocker。"
        )
    if include_tree and len(tree) == 3 and all(r.status == "complete" for r in tree):
        lines.append(
            "- `tree_compete_d3` 可作为备选或 appendix 支撑同向趋势：direct 为 3201 components/LCR=0.9169，final-only 为 4 components/LCR=0.9842，prune 为 2 components/LCR=0.9949；仍不是完整 six-row same-root matrix。"
        )
    lines += [
        "- 不能写 same-root matrix 已闭合；同一 case 的 `traditional` / `bridge` / `proposed` 仍缺。",
        "",
        "## 验证摘要",
        "",
        f"- complete rows: {len(completed)}",
        f"- blocked rows: {len(blocked)}",
        "- 渲染方式：纯 Python/Pillow 三角面软件投影，白底、无文字标签；不是 Blender/PBR 最终图。",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--status-doc", type=Path, default=DEFAULT_DOC)
    parser.add_argument("--include-tree", action="store_true", help="Also QA tree_compete_d3 backup rows.")
    args = parser.parse_args()

    rows = load_selected_rows(args.manifest, include_tree=args.include_tree)
    results = [qa_row(row, args.out_dir) for row in rows]
    metrics_path = args.out_dir / "metrics/same_root_miniset_render_qa_metrics.csv"
    manifest_path = args.out_dir / "manifest/same_root_miniset_render_qa_manifest.json"
    write_csv(metrics_path, results)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "kind": "same_root_miniset_render_qa",
                "date": "2026-05-10",
                "input_manifest": rel(args.manifest),
                "include_tree": args.include_tree,
                "target_variants": list(TARGET_VARIANTS),
                "rows": [r.__dict__ for r in results],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    write_markdown(args.status_doc, results, include_tree=args.include_tree)
    complete = sum(1 for r in results if r.status == "complete")
    print(f"wrote {metrics_path}")
    print(f"wrote {manifest_path}")
    print(f"wrote {args.status_doc}")
    print(f"complete_rows={complete}/{len(results)}")
    for r in results:
        print(f"{r.case}/{r.variant}: {r.status} glb={r.glb_export_ok and r.glb_import_ok} render={r.render_ok} blocker={r.blocker}")


if __name__ == "__main__":
    main()
