#!/usr/bin/env python3
"""Create simple smoothed mesh variants for voxel-like recursive outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--iterations", nargs="+", type=int, default=[4, 12, 24])
    parser.add_argument("--lambda", dest="lamb", type=float, default=0.35)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    import numpy as np
    import trimesh
    from trimesh.smoothing import filter_laplacian

    base = trimesh.load(args.mesh, force="mesh", process=False)
    rows = []
    for iters in args.iterations:
        mesh = base.copy()
        filter_laplacian(mesh, lamb=args.lamb, iterations=iters, volume_constraint=True)
        out_path = args.out / f"smoothed_l{str(args.lamb).replace('.', 'p')}_i{iters}.obj"
        mesh.export(out_path)
        verts = np.asarray(mesh.vertices)
        faces = np.asarray(mesh.faces)
        rows.append(
            {
                "iterations": int(iters),
                "lambda": float(args.lamb),
                "out": str(out_path),
                "vertices": int(len(verts)),
                "faces": int(len(faces)),
                "bbox_min": verts.min(axis=0).tolist() if len(verts) else [0, 0, 0],
                "bbox_max": verts.max(axis=0).tolist() if len(verts) else [0, 0, 0],
            }
        )
    (args.out / "summary.json").write_text(json.dumps({"source": str(args.mesh), "rows": rows}, indent=2))
    print(json.dumps({"source": str(args.mesh), "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
