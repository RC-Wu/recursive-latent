#!/usr/bin/env python3
"""Run Hunyuan3D shape-only baselines for the R-SLG recursive guide pool.

This script is intended to run on ``a100-2`` from the project root. It supports
sharding so GPUs 4/5/6/7 can process different guide images concurrently while
writing into one shared result directory.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
import traceback
from pathlib import Path

import torch
from PIL import Image
import trimesh


try:
    lib = torch.library.Library("torchvision", "DEF")
    lib.define("nms(Tensor dets, Tensor scores, float iou_threshold) -> Tensor")
except Exception:
    pass

from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline


GUIDE_ROOT = Path("inputs/strict_visual_matched_cases_V24_priority_rerun_20260510/_guides")

CASES = [
    ("vine_lsystem_grammar", "V23_lsystem_vine_grammar_pbr_guide.png", "recursive vine / L-system guide"),
    ("pyrite_lattice", "V23_ifs_lattice_pyrite_pbr_guide.png", "recursive pyrite/lattice guide"),
    ("coral_frontier", "V23_dla_coral_frontier_pbr_guide.png", "recursive coral/frontier guide"),
    ("crystal_frontier", "V23_dla_crystal_frontier_pbr_guide.png", "DLA-inspired crystal frontier guide"),
    ("frontier_sheet", "V23_dla_frontier_sheet_pbr_guide.png", "DLA/frontier sheet guide"),
    ("branch_ornament", "V23_ifs_branch_ornament_pbr_guide.png", "IFS branch ornament guide"),
    ("branch_tree", "V23_ifs_branch_tree_pbr_guide.png", "IFS branch tree guide"),
    ("radial_ornament", "V23_ifs_radial_ornament_pbr_guide.png", "IFS radial ornament guide"),
    ("pine_grammar", "V23_lsystem_pine_grammar_pbr_guide.png", "L-system pine grammar guide"),
    ("root_fan_grammar", "V23_lsystem_root_fan_grammar_pbr_guide.png", "L-system root fan grammar guide"),
    ("bush_shell", "V23_space_colonization_bush_shell_pbr_guide.png", "space-colonization bush shell guide"),
    ("root_network", "V23_space_colonization_root_network_pbr_guide.png", "space-colonization root network guide"),
    ("tree_crown", "V23_space_colonization_tree_crown_pbr_guide.png", "space-colonization tree crown guide"),
]


def row_from_glb(case_id: str, image_path: Path, out_glb: Path, notes: str, settings: dict, seed_used: int) -> dict:
    scene = trimesh.load(out_glb, force="scene")
    vertices = 0
    faces = 0
    for geom in scene.geometry.values():
        if getattr(geom, "vertices", None) is not None:
            vertices += len(geom.vertices)
        if getattr(geom, "faces", None) is not None:
            faces += len(geom.faces)
    return {
        "case_id": case_id,
        "status": "ok",
        "input_image": str(image_path),
        "output_glb": str(out_glb),
        "notes": notes,
        "elapsed_sec": 0.0,
        "vertices": int(vertices),
        "faces": int(faces),
        "file_size_mb": round(out_glb.stat().st_size / 1024 / 1024, 3),
        "geometry_count": len(scene.geometry),
        "bounds": scene.bounds.tolist() if scene.bounds is not None else None,
        **settings,
        "seed_used": seed_used,
        "skipped_existing": True,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    keys = sorted(set().union(*(row.keys() for row in rows)))
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            safe = {}
            for key in keys:
                value = row.get(key, "")
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False)
                safe[key] = value
            writer.writerow(safe)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", type=Path, default=Path("results/publication_hunyuan_recursive_guides_20260510"))
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--octree-resolution", type=int, default=320)
    parser.add_argument("--num-chunks", type=int, default=12000)
    parser.add_argument("--guidance-scale", type=float, default=5.0)
    parser.add_argument("--seed", type=int, default=20260510)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    root = Path.cwd()
    out_root = root / args.out_root
    out_root.mkdir(parents=True, exist_ok=True)
    settings = {
        "num_inference_steps": args.steps,
        "octree_resolution": args.octree_resolution,
        "num_chunks": args.num_chunks,
        "guidance_scale": args.guidance_scale,
        "seed": args.seed,
    }
    selected = [
        item
        for idx, item in enumerate(CASES)
        if idx % max(args.num_shards, 1) == args.shard_index
    ]
    print(
        "ENV",
        {k: os.environ.get(k) for k in ["CUDA_VISIBLE_DEVICES", "HF_HOME", "HF_HUB_CACHE", "HY3DGEN_MODELS", "HF_ENDPOINT"]},
        flush=True,
    )
    print("SHARD", args.shard_index, "/", args.num_shards, [case_id for case_id, _, _ in selected], flush=True)

    pipe = None
    rows: list[dict] = []
    for global_idx, (case_id, image_name, notes) in enumerate(CASES):
        if global_idx % max(args.num_shards, 1) != args.shard_index:
            continue
        image_path = root / GUIDE_ROOT / image_name
        case_dir = out_root / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        out_glb = case_dir / f"{case_id}_hunyuan_steps{args.steps}_oct{args.octree_resolution}.glb"
        seed_used = args.seed + global_idx
        if out_glb.exists() and not args.force:
            print("CASE_SKIP_EXISTING", case_id, out_glb, flush=True)
            try:
                row = row_from_glb(case_id, image_path, out_glb, notes, settings, seed_used)
            except Exception as exc:
                row = {
                    "case_id": case_id,
                    "status": "existing_import_fail",
                    "input_image": str(image_path),
                    "output_glb": str(out_glb),
                    "notes": notes,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    **settings,
                    "seed_used": seed_used,
                    "skipped_existing": True,
                }
            rows.append(row)
            (case_dir / f"{case_id}_metrics.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
            continue

        if pipe is None:
            t0 = time.time()
            pipe = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
                "tencent/Hunyuan3D-2",
                subfolder="hunyuan3d-dit-v2-0",
                variant="fp16",
            )
            print("LOAD_SECONDS", round(time.time() - t0, 2), flush=True)

        print("CASE_START", case_id, image_path, image_path.exists(), flush=True)
        t1 = time.time()
        try:
            image = Image.open(image_path).convert("RGBA")
            generator = torch.manual_seed(seed_used)
            mesh = pipe(
                image=image,
                num_inference_steps=args.steps,
                octree_resolution=args.octree_resolution,
                num_chunks=args.num_chunks,
                guidance_scale=args.guidance_scale,
                generator=generator,
                output_type="trimesh",
                enable_pbar=True,
            )[0]
            if isinstance(mesh, list):
                mesh = mesh[0]
            mesh.export(out_glb)
            scene = trimesh.load(out_glb, force="scene")
            row = {
                "case_id": case_id,
                "status": "ok",
                "input_image": str(image_path),
                "output_glb": str(out_glb),
                "notes": notes,
                "elapsed_sec": round(time.time() - t1, 2),
                "vertices": int(len(mesh.vertices)) if hasattr(mesh, "vertices") else None,
                "faces": int(len(mesh.faces)) if hasattr(mesh, "faces") else None,
                "file_size_mb": round(out_glb.stat().st_size / 1024 / 1024, 3),
                "geometry_count": len(scene.geometry),
                "bounds": scene.bounds.tolist() if scene.bounds is not None else None,
                **settings,
                "seed_used": seed_used,
                "skipped_existing": False,
            }
        except Exception as exc:
            traceback.print_exc()
            row = {
                "case_id": case_id,
                "status": "fail",
                "input_image": str(image_path),
                "notes": notes,
                "elapsed_sec": round(time.time() - t1, 2),
                "error_type": type(exc).__name__,
                "error": str(exc),
                **settings,
                "seed_used": seed_used,
                "skipped_existing": False,
            }
        rows.append(row)
        (case_dir / f"{case_id}_metrics.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
        print("CASE_DONE", json.dumps(row), flush=True)

    shard_json = out_root / f"hunyuan_recursive_guides_batch_metrics_shard{args.shard_index:02d}.json"
    shard_csv = out_root / f"hunyuan_recursive_guides_batch_metrics_shard{args.shard_index:02d}.csv"
    shard_json.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    write_csv(shard_csv, rows)
    print("SHARD_DONE", shard_json, shard_csv, flush=True)


if __name__ == "__main__":
    main()
