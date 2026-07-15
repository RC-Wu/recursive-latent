#!/usr/bin/env python3
"""Apply audited presentation-frame transforms to OBJ/GLB meshes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import trimesh


def as_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(loaded, trimesh.Scene):
        parts = []
        for geom in loaded.geometry.values():
            if isinstance(geom, trimesh.Trimesh) and len(geom.vertices):
                parts.append(geom)
        if not parts:
            raise RuntimeError(f"No mesh geometry found in {path}")
        loaded = trimesh.util.concatenate(parts)
    if not isinstance(loaded, trimesh.Trimesh) or len(loaded.vertices) == 0:
        raise RuntimeError(f"No mesh vertices found in {path}")
    return loaded


def rot_x_neg90_then_center_floor(vertices: np.ndarray) -> np.ndarray:
    """Rotate decoder-frame coordinates for upright presentation, then center/floor."""
    out = vertices.copy().astype(np.float64)
    x = out[:, 0].copy()
    y = out[:, 1].copy()
    z = out[:, 2].copy()
    out[:, 0] = x
    out[:, 1] = z
    out[:, 2] = -y
    bounds = np.array([out.min(axis=0), out.max(axis=0)], dtype=np.float64)
    xy_center = (bounds[0, :2] + bounds[1, :2]) * 0.5
    out[:, 0] -= xy_center[0]
    out[:, 1] -= xy_center[1]
    out[:, 2] -= bounds[0, 2]
    return out


def identity_center_floor(vertices: np.ndarray) -> np.ndarray:
    out = vertices.copy().astype(np.float64)
    bounds = np.array([out.min(axis=0), out.max(axis=0)], dtype=np.float64)
    xy_center = (bounds[0, :2] + bounds[1, :2]) * 0.5
    out[:, 0] -= xy_center[0]
    out[:, 1] -= xy_center[1]
    out[:, 2] -= bounds[0, 2]
    return out


def rot_x_pos90_then_center_floor(vertices: np.ndarray) -> np.ndarray:
    out = vertices.copy().astype(np.float64)
    x = out[:, 0].copy()
    y = out[:, 1].copy()
    z = out[:, 2].copy()
    out[:, 0] = x
    out[:, 1] = -z
    out[:, 2] = y
    return identity_center_floor(out)


def rot_y_neg90_then_center_floor(vertices: np.ndarray) -> np.ndarray:
    out = vertices.copy().astype(np.float64)
    x = out[:, 0].copy()
    y = out[:, 1].copy()
    z = out[:, 2].copy()
    out[:, 0] = -z
    out[:, 1] = y
    out[:, 2] = x
    return identity_center_floor(out)


def rot_y_pos90_then_center_floor(vertices: np.ndarray) -> np.ndarray:
    out = vertices.copy().astype(np.float64)
    x = out[:, 0].copy()
    y = out[:, 1].copy()
    z = out[:, 2].copy()
    out[:, 0] = z
    out[:, 1] = y
    out[:, 2] = -x
    return identity_center_floor(out)


def decoder_frame_inverse_restore_then_center_floor(vertices: np.ndarray) -> np.ndarray:
    """Diagnostic inverse of the mesh-to-SLat frame map, then center/floor."""
    out = vertices.copy().astype(np.float64)
    x = out[:, 0].copy()
    y = out[:, 1].copy()
    z = out[:, 2].copy()
    out[:, 0] = x
    out[:, 1] = z
    out[:, 2] = -y
    return identity_center_floor(out)


TRANSFORMS = {
    "identity_center_floor": identity_center_floor,
    "decoder_frame_inverse_restore_then_center_floor": decoder_frame_inverse_restore_then_center_floor,
    "rot_x_neg90_then_center_floor": rot_x_neg90_then_center_floor,
    "rot_x_pos90_then_center_floor": rot_x_pos90_then_center_floor,
    "rot_y_neg90_then_center_floor": rot_y_neg90_then_center_floor,
    "rot_y_pos90_then_center_floor": rot_y_pos90_then_center_floor,
}


def mesh_stats(mesh: trimesh.Trimesh, path: Path, label: str) -> dict:
    bounds = np.array(mesh.bounds, dtype=float)
    return {
        "label": label,
        "path": str(path),
        "bounds": bounds.tolist(),
        "extent": (bounds[1] - bounds[0]).tolist(),
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
    }


def parse_case(item: str) -> tuple[str, Path]:
    label, path = item.split("=", 1)
    return label, Path(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", help="label=/absolute/path/to/input.obj")
    parser.add_argument("--case-file", type=Path, help="Text file with label=/absolute/path per line")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--transform", choices=sorted(TRANSFORMS), default="rot_x_neg90_then_center_floor")
    parser.add_argument("--suffix", default="")
    parser.add_argument("--write-case-file", type=Path, help="Optional output label=path case file")
    parser.add_argument("--manifest", type=Path, help="Optional output JSON manifest")
    args = parser.parse_args()

    cases = list(args.case or [])
    if args.case_file:
        for line in args.case_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                cases.append(line)
    if not cases:
        raise SystemExit("No cases provided")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    transform_fn = TRANSFORMS[args.transform]
    manifest = []
    case_lines = []
    for item in cases:
        label, src = parse_case(item)
        mesh = as_mesh(src)
        mesh.vertices = transform_fn(np.asarray(mesh.vertices, dtype=np.float64))
        stem = f"{label}{args.suffix}" if args.suffix else label
        out_path = args.out_dir / f"{stem}.obj"
        mesh.export(out_path)
        row = mesh_stats(mesh, out_path, stem)
        row.update(
            {
                "source_path": str(src),
                "presentation_transform": args.transform,
                "semantic_frame_note": "Presentation-only transform; do not infer sparse-latent growth frame from this OBJ orientation.",
            }
        )
        manifest.append(row)
        case_lines.append(f"{stem}={out_path}")

    manifest_path = args.manifest or (args.out_dir / "manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if args.write_case_file:
        args.write_case_file.parent.mkdir(parents=True, exist_ok=True)
        args.write_case_file.write_text("\n".join(case_lines) + "\n", encoding="utf-8")
    print(json.dumps({"out_dir": str(args.out_dir), "manifest": str(manifest_path), "count": len(manifest)}, indent=2))


if __name__ == "__main__":
    main()
