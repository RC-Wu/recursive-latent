#!/usr/bin/env python3
"""Prepare v2 seam-aware low-contrast texturing candidates.

The first seam-aware batch proved the junction-collar meshes are structurally
sound, but the high-contrast guides created visible material/UV islands in
zoom renders.  This v2 batch keeps the same grammar/collar meshes and changes
only the texture guide policy: low-frequency, continuous material fields with
multiple seeds per family.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


PROJECT_ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_V1_DIR = PROJECT_ROOT / "results" / "seam_aware_texturing_batch_20260510"
DEFAULT_OUT = PROJECT_ROOT / "results" / "seam_aware_texturing_batch_v2_20260510"
REMOTE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
REMOTE_TARGET = "a100-2"
INPUT_NAME = "seam_aware_texturing_batch_v2_20260510"
ALLOWED_GPUS = [4, 5, 6, 7]


CASES = [
    {
        "source_case": "S01_botanical_root_junction_collar_continuous_bark",
        "case_id": "S01a_root_continuous_bark_grain_lowcontrast",
        "task_id": "botanical_root",
        "family": "botanical/root",
        "gpu": 4,
        "seed": 20295710,
        "motif": "root",
        "variant": "longitudinal_lowcontrast",
        "base": (106, 66, 38),
        "colors": [(128, 78, 42), (92, 54, 32), (145, 93, 54), (116, 74, 48)],
        "guide_notes": "low-contrast longitudinal bark grain; no dark ring bands; continuous material across collars",
    },
    {
        "source_case": "S01_botanical_root_junction_collar_continuous_bark",
        "case_id": "S01b_root_warm_cambium_soft_grain",
        "task_id": "botanical_root",
        "family": "botanical/root",
        "gpu": 5,
        "seed": 20295711,
        "motif": "root",
        "variant": "warm_soft_grain",
        "base": (126, 78, 44),
        "colors": [(147, 92, 50), (109, 66, 39), (160, 106, 64), (119, 82, 58)],
        "guide_notes": "soft warm cambium grain; avoid annular seams and isolated dark patches",
    },
    {
        "source_case": "S02_coral_frontier_junction_collar_continuous_pores",
        "case_id": "S02a_coral_ivory_pores_continuous",
        "task_id": "coral_frontier",
        "family": "coral/frontier",
        "gpu": 6,
        "seed": 20295712,
        "motif": "coral",
        "variant": "ivory_pores",
        "base": (222, 190, 142),
        "colors": [(236, 206, 156), (205, 165, 120), (231, 179, 138), (213, 188, 151)],
        "guide_notes": "ivory coral pores and ridges; low hue contrast; no red/yellow material islands",
    },
    {
        "source_case": "S02_coral_frontier_junction_collar_continuous_pores",
        "case_id": "S02b_coral_peach_micro_pores",
        "task_id": "coral_frontier",
        "family": "coral/frontier",
        "gpu": 7,
        "seed": 20295713,
        "motif": "coral",
        "variant": "peach_micro_pores",
        "base": (224, 156, 128),
        "colors": [(238, 174, 139), (209, 136, 116), (231, 193, 154), (198, 151, 124)],
        "guide_notes": "continuous peach coral micro-pores; avoid high-contrast camouflage bands",
    },
    {
        "source_case": "S03_ifs_crystal_junction_collar_continuous_facets",
        "case_id": "S03a_pyrite_brushed_facets_lowcontrast",
        "task_id": "ifs_crystal",
        "family": "IFS/crystal",
        "gpu": 4,
        "seed": 20295714,
        "motif": "pyrite",
        "variant": "brushed_lowcontrast",
        "base": (122, 101, 65),
        "colors": [(148, 122, 75), (102, 88, 63), (171, 142, 82), (132, 117, 86)],
        "guide_notes": "low-contrast pyrite facets; brushed mineral anisotropy; avoid zebra stripes",
    },
    {
        "source_case": "S03_ifs_crystal_junction_collar_continuous_facets",
        "case_id": "S03b_mineral_facets_smoke_gold",
        "task_id": "ifs_crystal",
        "family": "IFS/crystal",
        "gpu": 5,
        "seed": 20295715,
        "motif": "pyrite",
        "variant": "smoke_gold_facets",
        "base": (87, 78, 62),
        "colors": [(118, 100, 68), (73, 66, 55), (154, 126, 76), (102, 92, 74)],
        "guide_notes": "smoky gold mineral facets; coherent facet patches; no isolated white/black stripes",
    },
    {
        "source_case": "S02_coral_frontier_junction_collar_continuous_pores",
        "case_id": "S02c_coral_bone_ridge_plain",
        "task_id": "coral_frontier",
        "family": "coral/frontier",
        "gpu": 6,
        "seed": 20295716,
        "motif": "coral",
        "variant": "bone_ridge_plain",
        "base": (214, 190, 160),
        "colors": [(228, 207, 174), (191, 163, 133), (236, 216, 185), (204, 181, 150)],
        "guide_notes": "near-monochrome bone coral ridges; best for seam visibility QA",
    },
    {
        "source_case": "S01_botanical_root_junction_collar_continuous_bark",
        "case_id": "S01c_root_matte_earth_plain",
        "task_id": "botanical_root",
        "family": "botanical/root",
        "gpu": 7,
        "seed": 20295717,
        "motif": "root",
        "variant": "matte_earth_plain",
        "base": (113, 77, 54),
        "colors": [(126, 85, 57), (98, 66, 48), (140, 99, 70), (119, 82, 60)],
        "guide_notes": "near-monochrome matte earth bark; diagnostic low-texture root seam candidate",
    },
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_seed(text: str) -> int:
    value = 17
    for idx, ch in enumerate(text):
        value = (value * 167 + ord(ch) + idx * 13) % (2**32)
    return value


def draw_root(draw: ImageDraw.ImageDraw, rng: np.random.Generator, colors: list[tuple[int, int, int]]) -> None:
    # Mostly vertical, gently drifting fibers.  This avoids artificial annular
    # bands that read as recursive seams on cylindrical root forms.
    for _ in range(170):
        color = colors[int(rng.integers(0, len(colors)))]
        x0 = int(rng.integers(-80, 848))
        y0 = int(rng.integers(-60, 808))
        pts = []
        phase = float(rng.uniform(0.0, math.tau))
        drift = float(rng.normal(0.0, 24.0))
        for t in range(9):
            y = y0 + t * 108
            x = x0 + drift * t / 8.0 + math.sin(t * 0.85 + phase) * rng.uniform(8, 22)
            pts.append((int(x), int(y)))
        draw.line(pts, fill=color, width=int(rng.integers(2, 7)))
    for _ in range(45):
        color = colors[int(rng.integers(0, len(colors)))]
        x0 = int(rng.integers(-40, 808))
        y0 = int(rng.integers(-20, 788))
        draw.line(
            (x0, y0, int(x0 + rng.normal(40, 60)), int(y0 + rng.normal(110, 55))),
            fill=color,
            width=1,
        )


def draw_coral(draw: ImageDraw.ImageDraw, rng: np.random.Generator, colors: list[tuple[int, int, int]]) -> None:
    for _ in range(155):
        color = colors[int(rng.integers(0, len(colors)))]
        x = int(rng.integers(-40, 808))
        y = int(rng.integers(-40, 808))
        dx = int(rng.normal(0, 80))
        dy = int(rng.normal(0, 72))
        draw.line((x, y, x + dx, y + dy), fill=color, width=int(rng.integers(4, 11)))
    # Fine pores are drawn as subtle tonal rings, not hue-separated islands.
    for _ in range(260):
        color = colors[int(rng.integers(0, len(colors)))]
        x = int(rng.integers(-20, 788))
        y = int(rng.integers(-20, 788))
        r = int(rng.integers(5, 21))
        draw.ellipse((x - r, y - r, x + r, y + r), outline=color, width=1)
    for _ in range(32):
        color = colors[int(rng.integers(0, len(colors)))]
        y0 = int(rng.integers(0, 768))
        pts = []
        for t in range(12):
            x = int(t * 74 - 60)
            y = int(y0 + math.sin(t * 0.65 + rng.uniform(0, math.tau)) * 20)
            pts.append((x, y))
        draw.line(pts, fill=color, width=2)


def draw_pyrite(draw: ImageDraw.ImageDraw, rng: np.random.Generator, colors: list[tuple[int, int, int]]) -> None:
    # Large, low-contrast facet patches.  No full-width stripes: those were the
    # main visual failure in the first IFS seam-aware render.
    for _ in range(190):
        color = colors[int(rng.integers(0, len(colors)))]
        cx = int(rng.integers(-60, 828))
        cy = int(rng.integers(-60, 828))
        r = int(rng.integers(18, 68))
        skew = int(rng.integers(-18, 18))
        pts = [
            (cx - r, cy - r // 2 + skew),
            (cx - r // 4, cy - r),
            (cx + r, cy - r // 3 - skew),
            (cx + r // 2, cy + r),
            (cx - r // 2, cy + r // 2),
        ]
        draw.polygon(pts, fill=color)
    for _ in range(85):
        color = colors[int(rng.integers(0, len(colors)))]
        x = int(rng.integers(-30, 798))
        y = int(rng.integers(-30, 798))
        length = int(rng.integers(35, 130))
        angle = float(rng.choice([0.0, math.pi / 2, math.pi / 4, -math.pi / 4]) + rng.normal(0, 0.08))
        draw.line((x, y, int(x + math.cos(angle) * length), int(y + math.sin(angle) * length)), fill=color, width=1)


def draw_guide(path: Path, base: tuple[int, int, int], colors: list[tuple[int, int, int]], motif: str) -> None:
    rng = np.random.default_rng(stable_seed(path.stem))
    img = Image.new("RGB", (768, 768), base)
    draw = ImageDraw.Draw(img)
    # Soft low-frequency variation first; all later detail lives close to the
    # base palette so Trellis does not invent high-contrast material islands.
    for _ in range(90):
        color = colors[int(rng.integers(0, len(colors)))]
        x = int(rng.integers(-160, 900))
        y = int(rng.integers(-160, 900))
        r = int(rng.integers(80, 220))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)
    img = img.filter(ImageFilter.GaussianBlur(radius=26))
    draw = ImageDraw.Draw(img)
    if motif == "root":
        draw_root(draw, rng, colors)
    elif motif == "coral":
        draw_coral(draw, rng, colors)
    else:
        draw_pyrite(draw, rng, colors)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.35))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def _remote_path(local_path: Path, out_dir: Path) -> str:
    rel = local_path.relative_to(out_dir)
    return f"{REMOTE_ROOT}/inputs/{INPUT_NAME}/{rel.as_posix()}"


def prepare_batch(v1_dir: Path = DEFAULT_V1_DIR, out_dir: Path = DEFAULT_OUT) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    guide_dir = out_dir / "_guides"
    rows: list[dict[str, Any]] = []
    for spec in CASES:
        source_dir = v1_dir / spec["source_case"]
        source_mesh = source_dir / f"{spec['source_case']}.obj"
        source_meta = source_dir / f"{spec['source_case']}_metadata.json"
        case_id = spec["case_id"]
        case_dir = out_dir / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        local_mesh = case_dir / f"{case_id}.obj"
        local_meta = case_dir / f"{case_id}_metadata.json"
        shutil.copyfile(source_mesh, local_mesh)
        metadata = _read_json(source_meta)
        metadata.update(
            {
                "case_id": case_id,
                "remote_texturing_role": "seam_aware_v2_low_contrast_texture_candidate",
                "v2_variant": spec["variant"],
                "seam_aware_guide_notes": spec["guide_notes"],
                "source_case": spec["source_case"],
                "paper_claim_scope": "visual seam/PBR QA candidate only; not topology or watertight proof",
            }
        )
        local_meta.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
        guide_path = guide_dir / f"{case_id}_pbr_guide_v2.png"
        draw_guide(guide_path, spec["base"], spec["colors"], spec["motif"])
        row = {
            "case_id": case_id,
            "task_id": spec["task_id"],
            "family": spec["family"],
            "variant": spec["variant"],
            "mesh_path": _remote_path(local_mesh, out_dir),
            "guide_image": _remote_path(guide_path, out_dir),
            "metadata_path": _remote_path(local_meta, out_dir),
            "remote_target": REMOTE_TARGET,
            "gpu_group": int(spec["gpu"]),
            "seed": int(spec["seed"]),
            "steps": 8,
            "texture_size": 2048,
            "guide_notes": spec["guide_notes"],
            "claim_scope": "low-contrast seam/PBR visual QA candidate; not a topology proof",
            "selection_policy": "v2 keeps geometry fixed and varies only texture guide/seed for seam visual selection",
        }
        rows.append(row)

    fields = list(rows[0])
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "manifest.json").write_text(
        json.dumps({"schema": "seam_aware_texturing_batch_v2_20260510", "input_name": INPUT_NAME, "rows": rows}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    case_lines = [f"{row['case_id']}|{row['mesh_path']}|{row['guide_image']}|{row['seed']}|{row['gpu_group']}" for row in rows]
    (out_dir / "gpu4567_cases.txt").write_text("\n".join(case_lines) + "\n", encoding="utf-8")
    for gpu in ALLOWED_GPUS:
        selected = [line for line, row in zip(case_lines, rows) if int(row["gpu_group"]) == gpu]
        (out_dir / f"gpu{gpu}_cases.txt").write_text("\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")
    summary = {
        "schema": "seam_aware_texturing_batch_v2_20260510",
        "out_dir": str(out_dir),
        "manifest_csv": str(out_dir / "manifest.csv"),
        "manifest_json": str(out_dir / "manifest.json"),
        "case_count": len(rows),
        "remote_copy_target": f"{REMOTE_ROOT}/inputs/{INPUT_NAME}",
        "remote_run": "seam_aware_texturing_batch_v2_20260510_remote",
        "allowed_gpus": ALLOWED_GPUS,
        "remote_storage_limit_gb": 200,
        "claim_scope": "second texture/PBR selection batch for seam visual QA; v1 remains negative guide evidence",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "\n".join(
            [
                "# Seam-aware texturing batch v2 2026-05-10",
                "",
                "第二批 seam-aware texture/PBR 输入。几何保持 v1 junction-collar OBJ 不变，只换低对比连续材质 guide 和 seed。",
                "",
                "目标是减少 root 环状深色纹理、coral 红黄材质岛、IFS 高对比条纹导致的可见接缝。",
                "",
                "进入论文前仍必须完成 white-background zoom QA，并通过 PPTX 排版后导出 PDF。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v1-dir", type=Path, default=DEFAULT_V1_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    print(json.dumps(prepare_batch(args.v1_dir, args.out_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
