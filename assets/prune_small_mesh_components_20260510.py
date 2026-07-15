#!/usr/bin/env python3
"""Prune tiny disconnected mesh islands from generated OBJ candidates.

This is a conservative postprocess for remote-generated recursive outputs.  It
does not synthesize new geometry; it removes only very small face-connected
islands that read as floating dust in renders.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import trimesh


def load_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(str(path), force="scene", process=False)
    if isinstance(loaded, trimesh.Trimesh):
        mesh = loaded
    elif isinstance(loaded, trimesh.Scene):
        meshes = [g for g in loaded.geometry.values() if isinstance(g, trimesh.Trimesh) and len(g.vertices)]
        if not meshes:
            raise ValueError(f"no mesh geometry in {path}")
        mesh = trimesh.util.concatenate(meshes)
    else:
        raise TypeError(f"unsupported mesh load result for {path}: {type(loaded)!r}")
    mesh = mesh.copy()
    mesh.remove_unreferenced_vertices()
    return mesh


def component_rows(mesh: trimesh.Trimesh) -> list[dict[str, float | int]]:
    comps = mesh.split(only_watertight=False)
    rows: list[dict[str, float | int]] = []
    for idx, comp in enumerate(comps):
        comp.remove_unreferenced_vertices()
        rows.append(
            {
                "index": idx,
                "vertices": int(len(comp.vertices)),
                "faces": int(len(comp.faces)),
                "area": float(comp.area),
            }
        )
    rows.sort(key=lambda row: (float(row["area"]), int(row["faces"]), int(row["vertices"])), reverse=True)
    return rows


def prune(mesh: trimesh.Trimesh, min_faces: int, min_area_ratio: float, keep_top: int) -> tuple[trimesh.Trimesh, dict[str, object]]:
    comps = list(mesh.split(only_watertight=False))
    total_area = float(mesh.area)
    keyed = []
    for idx, comp in enumerate(comps):
        comp.remove_unreferenced_vertices()
        keyed.append((idx, comp, float(comp.area), int(len(comp.faces)), int(len(comp.vertices))))
    keyed.sort(key=lambda item: (item[2], item[3], item[4]), reverse=True)
    keep_indices: set[int] = set()
    for rank, (idx, _comp, area, faces, _vertices) in enumerate(keyed):
        if keep_top and rank < keep_top:
            keep_indices.add(idx)
        elif faces >= min_faces:
            keep_indices.add(idx)
        elif total_area > 0 and area / total_area >= min_area_ratio:
            keep_indices.add(idx)
    kept = [comp for idx, comp, _area, _faces, _vertices in keyed if idx in keep_indices]
    if not kept:
        kept = [keyed[0][1]] if keyed else []
    out = trimesh.util.concatenate(kept) if len(kept) > 1 else kept[0].copy()
    out.remove_unreferenced_vertices()
    summary = {
        "input_vertices": int(len(mesh.vertices)),
        "input_faces": int(len(mesh.faces)),
        "input_components": int(len(comps)),
        "input_area": total_area,
        "output_vertices": int(len(out.vertices)),
        "output_faces": int(len(out.faces)),
        "kept_components": int(len(kept)),
        "removed_components": int(max(0, len(comps) - len(kept))),
        "min_faces": int(min_faces),
        "min_area_ratio": float(min_area_ratio),
        "keep_top": int(keep_top),
        "component_rows_top20": component_rows(mesh)[:20],
    }
    return out, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", default=[], help="label=/path/to/input.obj")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--min-faces", type=int, default=12)
    parser.add_argument("--min-area-ratio", type=float, default=2e-5)
    parser.add_argument("--keep-top", type=int, default=0)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summaries = []
    for item in args.case:
        if "=" not in item:
            raise ValueError(f"--case must be label=path, got {item}")
        label, raw_path = item.split("=", 1)
        path = Path(raw_path)
        mesh = load_mesh(path)
        pruned, summary = prune(mesh, args.min_faces, args.min_area_ratio, args.keep_top)
        out_path = args.out_dir / f"{label}.obj"
        pruned.export(out_path)
        summary.update({"label": label, "input_path": str(path), "output_path": str(out_path)})
        summaries.append(summary)
    (args.out_dir / "prune_summary.json").write_text(json.dumps(summaries, indent=2))
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
