#!/usr/bin/env python3
"""V12 tapered staghorn/table-coral strict matched DLA input generator.

V9 was non-blocky but too root-like; V10 was connected but too lumpy. V11 keeps
the same frontier-growth/exclusion story but emits a cleaner hierarchical coral
support: fewer branches, larger radii, smooth welded tubes, and bright guide
images. V12 adds explicit tapered continuation nodes at every terminal branch so
close zooms do not show the flat cylinder cuts seen in V11.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import procedural_baselines as pb
import strict_visual_matched_cases_v6_connectivity_20260510 as v6
import strict_visual_matched_cases_v9_organic_frontier_20260510 as v9

REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 100
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_v12_tapered_staghorn_20260510_dryrun"


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _smooth_frontier_tree(seed: int, mode: str) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed)
    nodes: list[np.ndarray] = [np.array([0.0, 0.0, 0.0], dtype=float)]
    edges: list[tuple[int, int]] = []
    depths = [0]
    tips: list[tuple[int, np.ndarray, int]] = []

    if mode == "table":
        main_dirs = [
            _unit(np.array([math.cos(a), math.sin(a), 0.10])) for a in np.linspace(0, 2 * math.pi, 7, endpoint=False)
        ]
        max_depth, step0, branch_prob = 5, 0.26, 0.72
        anisotropy = np.array([1.20, 1.20, 0.38])
    elif mode == "frontier":
        main_dirs = [_unit(np.array([x, 0.30 * math.sin(i), 0.06])) for i, x in enumerate(np.linspace(-1.0, 1.0, 7))]
        max_depth, step0, branch_prob = 5, 0.25, 0.62
        anisotropy = np.array([1.55, 0.86, 0.28])
    elif mode == "crystal":
        main_dirs = [_unit(np.array([math.cos(a), math.sin(a), 0.28])) for a in np.linspace(0, 2 * math.pi, 6, endpoint=False)]
        max_depth, step0, branch_prob = 4, 0.27, 0.50
        anisotropy = np.array([1.0, 1.0, 0.70])
    else:
        main_dirs = [_unit(np.array([math.cos(a), math.sin(a), 0.55])) for a in np.linspace(0, 2 * math.pi, 6, endpoint=False)]
        max_depth, step0, branch_prob = 5, 0.24, 0.74
        anisotropy = np.array([0.95, 0.95, 1.15])

    for direction in main_dirs:
        tips.append((0, _unit(direction * anisotropy), 1))

    attempts = 0
    while tips and attempts < 900 and len(nodes) < 240:
        parent, direction, depth = tips.pop(0)
        attempts += 1
        if depth > max_depth:
            continue
        step = step0 * (0.86 ** (depth - 1)) * rng.uniform(0.82, 1.12)
        bend = rng.normal(0.0, 0.12 if mode != "crystal" else 0.045, 3)
        if mode == "staghorn":
            bend[2] += 0.08
        if mode == "table":
            bend[2] *= 0.25
        new_dir = _unit((direction + bend) * anisotropy)
        p = nodes[parent] + new_dir * step
        exclusion = 0.065 * (0.90 ** depth)
        if any(float(np.linalg.norm(p - q)) < exclusion for q in nodes):
            continue
        idx = len(nodes)
        nodes.append(p)
        depths.append(depth)
        edges.append((parent, idx))

        fan = 2 if rng.random() < branch_prob else 1
        if depth < max_depth and (mode == "table" or rng.random() < 0.92):
            for j in range(fan):
                rot = rng.normal(0.0, 0.34, 3)
                if mode == "frontier":
                    rot[2] *= 0.15
                child_dir = _unit(new_dir + rot)
                tips.append((idx, child_dir, depth + 1))

    child_count = {i: 0 for i in range(len(nodes))}
    for a, b in edges:
        child_count[a] = child_count.get(a, 0) + 1
        child_count.setdefault(b, 0)
    terminal_ids = [i for i in range(1, len(nodes)) if child_count.get(i, 0) == 0]
    for i in terminal_ids:
        parent = next((a for a, b in edges if b == i), 0)
        direction = _unit(nodes[i] - nodes[parent])
        extension = 0.085 if mode != "crystal" else 0.070
        nodes.append(nodes[i] + direction * extension)
        depths.append(depths[i] + 1)
        edges.append((i, len(nodes) - 1))

    nodes = v6._normalize_nodes(nodes, 2.45)
    max_d = max(depths) if depths else 1
    if mode == "crystal":
        radii = [0.060 * (1.0 - 0.65 * d / max_d) + 0.004 for d in depths]
        sides = 8
    elif mode == "frontier":
        radii = [0.070 * (1.0 - 0.70 * d / max_d) + 0.004 for d in depths]
        sides = 18
    else:
        radii = [0.082 * (1.0 - 0.72 * d / max_d) + 0.004 for d in depths]
        sides = 20
    mesh = v6.welded_skeleton_mesh(nodes, edges, radii, sides=sides)
    return mesh, {
        "mode": mode,
        "generated_nodes": len(nodes),
        "skeleton_edges": len(edges),
        "max_depth": max_depth,
        "attempts": attempts,
        "frontier_attachment_mode": "active-tip frontier expansion with occupancy exclusion",
        "occupancy_exclusion": "reject candidate nodes inside depth-scaled radius",
        "v12_policy": "smooth readable welded staghorn/table support with explicit tapered terminal continuations",
        "curved_branch_edges": len(edges),
        "perforated_membrane_count": 0,
        "ridge_fin_count": 0,
        "thin_tip_radius_max": min(radii) if radii else 0.0,
    }


def _write_guides(out_dir: Path) -> dict[str, str]:
    from PIL import Image, ImageDraw, ImageFilter

    guide_dir = out_dir / "_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)

    def save(name: str, bg: tuple[int, int, int], palette: list[tuple[int, int, int]], crystal: bool = False) -> str:
        rng = np.random.default_rng(sum((i + 1) * b for i, b in enumerate(name.encode("utf-8"))))
        img = Image.new("RGB", (768, 768), bg)
        draw = ImageDraw.Draw(img)
        for _ in range(360):
            c = palette[int(rng.integers(0, len(palette)))]
            x, y = int(rng.integers(0, 768)), int(rng.integers(0, 768))
            if crystal:
                r = int(rng.integers(18, 64))
                draw.polygon([(x, y-r), (x+r, y), (x, y+r), (x-r, y)], outline=c, width=3)
            else:
                width = int(rng.integers(5, 14))
                dx, dy = int(rng.normal(0, 110)), int(rng.normal(0, 95))
                draw.line((x, y, x + dx, y + dy), fill=c, width=width)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "staghorn": save("v11_bright_pink_staghorn_coral_guide.png", (244, 146, 130), [(255, 222, 176), (255, 166, 132), (250, 112, 120), (238, 92, 112)]),
        "table": save("v11_warm_ivory_table_coral_guide.png", (230, 176, 126), [(255, 240, 196), (246, 198, 134), (226, 142, 100), (252, 224, 172)]),
        "frontier": save("v11_frontier_plate_coral_guide.png", (216, 142, 124), [(255, 224, 184), (236, 152, 124), (206, 92, 110), (250, 204, 160)]),
        "crystal": save("v11_blue_gold_crystal_guide.png", (64, 78, 92), [(104, 142, 172), (188, 212, 218), (230, 202, 132), (82, 104, 128)], crystal=True),
    }


def _case_specs_v11(seed: int) -> list[dict]:
    specs: list[dict] = []

    def add(case_id: str, target: str, mode: str, guide_key: str, offset: int, gpu: int, priority: bool, why: str) -> None:
        mesh, controls = _smooth_frontier_tree(seed + offset, mode)
        operators = [
            "stochastic_frontier_attachment",
            "occupancy_exclusion",
            "active_tip_growth",
            "smooth_welded_staghorn_surface",
            "connected_branch_projection",
        ]
        specs.append(
            {
                "case_id": case_id,
                "family": "DLA/frontier",
                "match_target": target,
                "traditional_target": target,
                "recursive_mode": "stochastic frontier attachment with occupancy exclusion and rooted active-tip accretive growth",
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

    add("v12_dla_tapered_staghorn_coral_a", "dla_coral_cluster_900", "staghorn", "staghorn", 501, 4, True, "Strict DLA coral-cluster task with active frontier tips, occupancy exclusion, readable smooth staghorn branches, and tapered terminals.")
    add("v12_dla_tapered_staghorn_coral_b", "dla_coral_cluster_900", "staghorn", "staghorn", 502, 5, True, "Second tapered staghorn seed for the same frontier/exclusion coral target.")
    add("v12_dla_tapered_table_coral_a", "dla_coral_cluster_900", "table", "table", 503, 6, True, "Table-coral variant preserving frontier expansion while producing readable tapered plate-like branches.")
    add("v12_dla_tapered_table_coral_b", "dla_coral_cluster_900", "table", "table", 504, 7, True, "Second tapered table-coral seed for selection.")
    add("v12_dla_tapered_frontier_plate_a", "dla_frontier_sheet_700", "frontier", "frontier", 505, 4, True, "Frontier sheet task with connected smooth tapered plate support.")
    add("v12_dla_tapered_frontier_plate_b", "dla_frontier_sheet_700", "frontier", "frontier", 506, 5, True, "Second tapered frontier sheet seed.")
    add("v12_dla_tapered_crystal_a", "dla_crystal_cluster_520", "crystal", "crystal", 507, 6, True, "Crystal frontier boundary case with cleaner tapered branch/facet support.")
    add("v12_dla_tapered_crystal_b", "dla_crystal_cluster_520", "crystal", "crystal", 508, 7, False, "Backup tapered crystal seed.")
    return specs


def materialize(root: Path, out_dir: Path, seed: int = 20260510, case_limit: int | None = None) -> dict:
    old_write_guides = v9._write_guides
    old_case_specs = v9._case_specs
    try:
        v9._write_guides = _write_guides
        v9._case_specs = _case_specs_v11
        return v9.materialize(root, out_dir, seed=seed, case_limit=case_limit)
    finally:
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
    summary["v12_note"] = "V11 clean support plus tapered terminal continuations to remove flat cylinder cuts"
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
