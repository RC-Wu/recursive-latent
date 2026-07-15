#!/usr/bin/env python3
"""V10 readable-coral strict matched DLA/frontier input generator.

V9 removed the block/chunk failure, but early renders read as tangled roots.
V10 keeps the same strict stochastic frontier attachment + occupancy exclusion
protocol while biasing the emitted geometry toward readable staghorn/table
coral and frontier plates: fewer frontier nodes, thicker hierarchical branches,
brighter guide images, fewer free needle details, and more connected ridge/plate
support.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import strict_visual_matched_cases_v9_organic_frontier_20260510 as v9

REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 100
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_v10_readable_coral_frontier_20260510_dryrun"


def _v10_profile_config(profile: str) -> dict:
    """Lower-density, thicker-support profiles for V10."""
    configs = {
        "coral_lace": {
            "nodes": 220,
            "exclusion": 0.056,
            "step": (0.070, 0.145),
            "anisotropy": np.array([1.00, 0.94, 1.28]),
            "up_bias": 0.22,
            "radial_bias": 0.64,
            "noise": np.array([0.34, 0.34, 0.28]),
            "sheet": 0.0,
            "crystal": False,
            "base_radius": 0.070,
            "tip_radius": 0.016,
            "sides": 18,
            "extent": 2.38,
        },
        "coral_table": {
            "nodes": 205,
            "exclusion": 0.060,
            "step": (0.075, 0.150),
            "anisotropy": np.array([1.55, 1.36, 0.52]),
            "up_bias": 0.05,
            "radial_bias": 0.70,
            "noise": np.array([0.36, 0.30, 0.12]),
            "sheet": 0.62,
            "crystal": False,
            "base_radius": 0.066,
            "tip_radius": 0.014,
            "sides": 18,
            "extent": 2.45,
        },
        "frontier_fan": {
            "nodes": 190,
            "exclusion": 0.058,
            "step": (0.078, 0.158),
            "anisotropy": np.array([1.95, 1.22, 0.34]),
            "up_bias": 0.03,
            "radial_bias": 0.72,
            "noise": np.array([0.40, 0.24, 0.08]),
            "sheet": 0.82,
            "crystal": False,
            "base_radius": 0.058,
            "tip_radius": 0.012,
            "sides": 16,
            "extent": 2.46,
        },
        "crystal_blade": {
            "nodes": 210,
            "exclusion": 0.058,
            "step": (0.070, 0.155),
            "anisotropy": np.array([1.16, 1.08, 0.56]),
            "up_bias": 0.00,
            "radial_bias": 0.74,
            "noise": np.array([0.14, 0.14, 0.06]),
            "sheet": 0.25,
            "crystal": True,
            "base_radius": 0.050,
            "tip_radius": 0.012,
            "sides": 10,
            "extent": 2.32,
        },
    }
    return configs[profile]


def _v10_profile_tuning(profile: str) -> dict:
    table = {
        "coral_lace": {
            "source_profile": "coral_lace",
            "curvature": 0.045,
            "radius_scale": 1.04,
            "branchlet_limit": 34,
            "membrane_limit": 28,
            "ridge_limit": 74,
            "tip_limit": 56,
            "rings": 5,
            "sides": 14,
            "crystal": False,
        },
        "coral_plate": {
            "source_profile": "coral_table",
            "curvature": 0.034,
            "radius_scale": 1.02,
            "branchlet_limit": 24,
            "membrane_limit": 44,
            "ridge_limit": 68,
            "tip_limit": 42,
            "rings": 5,
            "sides": 14,
            "crystal": False,
        },
        "frontier_filigree": {
            "source_profile": "frontier_fan",
            "curvature": 0.030,
            "radius_scale": 0.98,
            "branchlet_limit": 22,
            "membrane_limit": 58,
            "ridge_limit": 62,
            "tip_limit": 36,
            "rings": 5,
            "sides": 12,
            "crystal": False,
        },
        "crystal_needle": {
            "source_profile": "crystal_blade",
            "curvature": 0.020,
            "radius_scale": 0.95,
            "branchlet_limit": 28,
            "membrane_limit": 24,
            "ridge_limit": 76,
            "tip_limit": 42,
            "rings": 4,
            "sides": 8,
            "crystal": True,
        },
    }
    return table[profile]


def _v10_write_guides(out_dir: Path) -> dict[str, str]:
    from PIL import Image, ImageDraw, ImageFilter

    guide_dir = out_dir / "_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)

    def save(name: str, bg: tuple[int, int, int], palette: list[tuple[int, int, int]], mode: str) -> str:
        rng = np.random.default_rng(sum((i + 1) * b for i, b in enumerate(name.encode("utf-8"))))
        img = Image.new("RGB", (768, 768), bg)
        draw = ImageDraw.Draw(img)
        for _ in range(520):
            c = palette[int(rng.integers(0, len(palette)))]
            x, y = int(rng.integers(0, 768)), int(rng.integers(0, 768))
            if mode == "crystal":
                r = int(rng.integers(16, 54))
                draw.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], outline=c, fill=None, width=2)
            else:
                width = int(rng.integers(3, 9))
                dx, dy = int(rng.normal(0, 105)), int(rng.normal(0, 70))
                draw.line((x, y, x + dx, y + dy), fill=c, width=width)
                if rng.random() < 0.35:
                    rr = int(rng.integers(10, 32))
                    draw.ellipse((x - rr, y - rr, x + rr, y + rr), outline=c, width=2)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "pink_lace": save(
            "v10_bright_staghorn_coral_guide.png",
            (232, 138, 126),
            [(255, 214, 176), (255, 164, 132), (246, 106, 112), (255, 235, 198), (222, 92, 110)],
            "coral",
        ),
        "ivory_porous": save(
            "v10_ivory_table_coral_guide.png",
            (218, 168, 124),
            [(255, 242, 206), (245, 202, 144), (226, 140, 106), (255, 230, 176), (176, 104, 92)],
            "coral",
        ),
        "fan_lace": save(
            "v10_frontier_plate_coral_guide.png",
            (196, 132, 118),
            [(254, 228, 190), (238, 164, 128), (206, 96, 112), (255, 214, 174), (144, 88, 96)],
            "coral",
        ),
        "crystal_needle": save(
            "v10_blue_gold_crystal_guide.png",
            (56, 68, 82),
            [(106, 142, 168), (176, 204, 210), (230, 214, 160), (76, 92, 116), (196, 172, 112)],
            "crystal",
        ),
    }


def _case_specs_v10(seed: int) -> list[dict]:
    specs: list[dict] = []

    def add(case_id: str, target: str, profile: str, guide_key: str, offset: int, gpu: int, priority: bool, why: str) -> None:
        mesh, controls = v9._organic_frontier_mesh(seed + offset, profile)
        controls["v10_readability_policy"] = "fewer larger frontier nodes, thicker branches, reduced needle budget, brighter coral guide"
        operators = [
            "stochastic_frontier_attachment",
            "occupancy_exclusion",
            "readable_hierarchical_frontier_skeleton",
            "thick_tapered_coral_surface",
            "limited_tip_closure",
            "attached_plate_membranes",
            "connected_ridge_fins",
        ]
        specs.append(
            {
                "case_id": case_id,
                "family": "DLA/frontier",
                "match_target": target,
                "traditional_target": target,
                "recursive_mode": "stochastic frontier attachment with occupancy exclusion and rooted accretive graph growth",
                "mesh": mesh,
                "guide_key": guide_key,
                "seed": int(seed + offset),
                "controls": controls,
                "operators": operators,
                "operator_composition": " -> ".join(operators),
                "why_matches_traditional": why,
                "strict_match_notes": why,
                "gpu": int(gpu),
                "case_role": "priority_a100_2" if priority else "backup_a100_2",
            }
        )

    add("v10_dla_staghorn_coral_branching_a", "dla_coral_cluster_900", "coral_lace", "pink_lace", 411, 4, True, "Same DLA coral-cluster frontier/exclusion task, but V10 uses fewer thicker hierarchical branches and bright coral guidance to avoid V9 root-like tangles.")
    add("v10_dla_staghorn_coral_branching_b", "dla_coral_cluster_900", "coral_lace", "pink_lace", 412, 5, True, "Second strict DLA coral seed with readable staghorn branching; generated fresh on a100-2, not local repair.")
    add("v10_dla_table_coral_plate_a", "dla_coral_cluster_900", "coral_plate", "ivory_porous", 413, 6, True, "Plate-biased DLA/frontier coral cluster with attached membranes and thick support branches.")
    add("v10_dla_table_coral_plate_b", "dla_coral_cluster_900", "coral_plate", "ivory_porous", 414, 7, True, "Backup table-coral DLA cluster seed with same frontier/exclusion control.")
    add("v10_dla_frontier_fan_plate_a", "dla_frontier_sheet_700", "frontier_filigree", "fan_lace", 415, 4, True, "Boundary/frontier sheet task with readable connected plate/ridge support instead of thin rod filigree.")
    add("v10_dla_frontier_fan_plate_b", "dla_frontier_sheet_700", "frontier_filigree", "fan_lace", 416, 5, True, "Second boundary-sheet seed preserving frontier attachment and occupancy exclusion.")
    add("v10_dla_crystal_blue_gold_a", "dla_crystal_cluster_520", "crystal_needle", "crystal_needle", 417, 6, True, "Accretive crystal frontier with fewer but clearer faceted branches and blue/gold PBR guide.")
    add("v10_dla_crystal_blue_gold_b", "dla_crystal_cluster_520", "crystal_needle", "crystal_needle", 418, 7, False, "Backup crystal frontier seed for V10 selection.")
    return specs


def materialize(root: Path, out_dir: Path, seed: int = 20260510, case_limit: int | None = None) -> dict:
    old_profile_config = v9.v8._profile_config
    old_profile_tuning = v9._profile_tuning
    old_write_guides = v9._write_guides
    old_case_specs = v9._case_specs
    try:
        v9.v8._profile_config = _v10_profile_config
        v9._profile_tuning = _v10_profile_tuning
        v9._write_guides = _v10_write_guides
        v9._case_specs = _case_specs_v10
        return v9.materialize(root, out_dir, seed=seed, case_limit=case_limit)
    finally:
        v9.v8._profile_config = old_profile_config
        v9._profile_tuning = old_profile_tuning
        v9._write_guides = old_write_guides
        v9._case_specs = old_case_specs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260510)
    parser.add_argument("--case-limit", type=int, default=None)
    args = parser.parse_args()
    summary = materialize(args.root, args.out, seed=args.seed, case_limit=args.case_limit)
    summary["v10_note"] = "readable coral/frontier branch: lower density, stronger silhouette, brighter PBR guide"
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
