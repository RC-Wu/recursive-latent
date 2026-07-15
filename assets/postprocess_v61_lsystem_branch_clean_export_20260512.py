#!/usr/bin/env python3
"""V61 fine clean-export pass for dense L-system branch candidates.

This script reuses the Blender import/remesh/export utilities from V60, but
uses V61 defaults tuned to preserve the restored recursive side-branch density:
fine voxel remesh, low-amplitude smoothing, and no decimation by default.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ASSET_DIR = Path(__file__).resolve().parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import postprocess_v60_lsystem_branch_clean_export_20260511 as v60


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "results" / "strict_visual_matched_texture_V61_lsystem_branch_dense_clean_bough_yfork_BC_20260512_remote"
DEFAULT_OUT = ROOT / "results" / "strict_visual_matched_texture_V61_lsystem_branch_clean_export_fine_20260512"

DEFAULT_CASES = [
    (
        "V61_lsys_branch_clean_dense_B",
        SOURCE_ROOT / "V61_lsys_branch_dense_clean_B_steps8_tex2048_seed20321513_xformers" / "textured.glb",
    ),
    (
        "V61_lsys_branch_clean_balanced_C",
        SOURCE_ROOT / "V61_lsys_branch_balanced_clean_C_steps8_tex2048_seed20321514_xformers" / "textured.glb",
    ),
]


def parse_case(item: str) -> tuple[str, Path]:
    if "=" not in item:
        raise argparse.ArgumentTypeError("--case must be label=/path/to/textured.glb")
    label, path = item.split("=", 1)
    return label, Path(path)


def process_case(
    label: str,
    source: Path,
    out_dir: Path,
    voxel_size: float,
    smooth_iters: int,
    smooth_factor: float,
    merge_distance: float,
    decimate_ratio: float,
) -> dict:
    if not source.exists():
        raise FileNotFoundError(source)
    v60.clear_scene()
    objects = v60.import_glb(source)
    obj = v60.join_objects(objects)
    object_stats = v60.clean_branch_object(
        obj,
        label=label,
        voxel_size=voxel_size,
        smooth_iters=smooth_iters,
        smooth_factor=smooth_factor,
        merge_distance=merge_distance,
        decimate_ratio=decimate_ratio,
    )
    case_dir = out_dir / label
    glb_path = case_dir / "textured.glb"
    v60.export_selected_glb(glb_path, [obj])
    row = {
        "label": label,
        "source_glb": str(source),
        "output_glb": str(glb_path),
        "voxel_size": float(voxel_size),
        "smooth_iters": int(smooth_iters),
        "smooth_factor": float(smooth_factor),
        "merge_distance": float(merge_distance),
        "decimate_ratio": float(decimate_ratio),
        "object_count_before_join": len(objects),
        "objects": [object_stats],
        "postprocess_policy": "V61 fine object-space clean export over V61 dense clean-bough GLBs; source assets preserved",
        "claim_boundary": "Versioned mesh/export normalization candidate, not 2D seam inpaint, SDEdit, UV editing, or backprojection.",
    }
    (case_dir / "v61_clean_export_metadata.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
    print(json.dumps(row, indent=2))
    return row


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", type=parse_case)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--voxel-size", type=float, default=0.0065)
    parser.add_argument("--smooth-iters", type=int, default=3)
    parser.add_argument("--smooth-factor", type=float, default=0.04)
    parser.add_argument("--merge-distance", type=float, default=0.00035)
    parser.add_argument("--decimate-ratio", type=float, default=0.0)
    return parser


def main(argv: list[str] | None = None) -> None:
    v60.require_blender()
    parser = build_parser()
    args = parser.parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    cases = args.case or DEFAULT_CASES
    rows = [
        process_case(
            label,
            path,
            args.out_dir,
            voxel_size=args.voxel_size,
            smooth_iters=args.smooth_iters,
            smooth_factor=args.smooth_factor,
            merge_distance=args.merge_distance,
            decimate_ratio=args.decimate_ratio,
        )
        for label, path in cases
    ]
    manifest = {
        "rows": rows,
        "source": "assets/postprocess_v61_lsystem_branch_clean_export_20260512.py",
        "sdedit_seam_backprojection_available": False,
        "inherits_v60_utility_functions": True,
    }
    (args.out_dir / "v61_clean_export_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    main(argv)
