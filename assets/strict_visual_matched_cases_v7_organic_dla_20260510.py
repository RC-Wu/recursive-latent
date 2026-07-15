#!/usr/bin/env python3
"""V7 focused organic DLA/frontier strict matched input generator.

V7 is a narrow remote-generation experiment after V6.  V6 improved connected
support but DLA/coral still rendered as dark blocky mineral chunks.  V7 changes
the input algorithm itself: stochastic frontier trees are surfaced with
high-section smooth tubes, rounded bulb tips, and sparse edge-attached porous
panels, while preserving the same DLA/frontier comparison target family.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import procedural_baselines as pb
import recursive_growth_mesh_metrics as rgm
import strict_visual_matched_cases_v6_connectivity_20260510 as v6

REMOTE_TARGET = "a100-2"
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_v7_organic_dla_20260510_dryrun"


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _stochastic_frontier_tree(seed: int, nodes_target: int, anisotropy: np.ndarray, sheet: bool = False) -> tuple[list[np.ndarray], list[tuple[int, int]], list[float], dict]:
    rng = np.random.default_rng(seed)
    nodes = [np.zeros(3, dtype=float)]
    edges: list[tuple[int, int]] = []
    frontier = [0]
    radii = [0.070]
    attempts = 0
    while len(nodes) < nodes_target and attempts < nodes_target * 12:
        attempts += 1
        parent = int(rng.choice(frontier if rng.random() < 0.78 else range(len(nodes))))
        base = np.asarray(nodes[parent], dtype=float)
        if sheet:
            direction = np.array([rng.normal(0, 1.0), rng.normal(0, 0.55), rng.normal(0, 0.15)])
            direction[0] += 0.38 * np.sign(base[0] + 1e-4)
        else:
            direction = base + rng.normal(0, 0.55, 3)
            direction[2] += rng.normal(0.10, 0.16)
        direction = _unit(direction * anisotropy)
        length = float(rng.uniform(0.035, 0.085) * (1.0 + 0.7 * rng.random()))
        point = base + direction * length
        # Enforce occupancy-like exclusion, matching DLA/space competition.
        if min(np.linalg.norm(point - np.asarray(q)) for q in nodes) < (0.030 if sheet else 0.034):
            continue
        nodes.append(point)
        idx = len(nodes) - 1
        edges.append((parent, idx))
        depth_proxy = min(1.0, np.linalg.norm(point) / 1.2)
        radii.append(0.040 * (1.0 - 0.45 * depth_proxy) + rng.uniform(0.010, 0.018))
        frontier.append(idx)
        if len(frontier) > 180:
            frontier = frontier[-140:]
    nodes = v6._normalize_nodes(nodes, 2.35)
    return nodes, edges, radii, {
        "nodes_target": nodes_target,
        "generated_nodes": len(nodes),
        "attempts": attempts,
        "sheet_mode": sheet,
        "anisotropy": [float(x) for x in anisotropy],
        "occupancy_exclusion_radius": 0.030 if sheet else 0.034,
    }


def _organic_coral_mesh(seed: int, variant: str) -> tuple[pb.Mesh, dict]:
    sheet = variant == "frontier_sheet"
    anisotropy = np.array([1.7, 1.0, 0.55]) if sheet else np.array([1.0, 0.92, 1.22])
    nodes, edges, radii, ctl = _stochastic_frontier_tree(seed, 430 if sheet else 520, anisotropy, sheet=sheet)
    mesh = v6.welded_skeleton_mesh(nodes, edges, radii, sides=14)
    centers = getattr(mesh, "center_indices")
    parents = [-1 for _ in nodes]
    for a, b in edges:
        if parents[b] < 0 and b != 0:
            parents[b] = a
    child_map = v6._children(parents)
    tips = [i for i in range(1, len(nodes)) if not child_map.get(i)]
    rng = np.random.default_rng(seed + 99)
    rng.shuffle(tips)
    bulb_count = 0
    for idx in tips[:190 if not sheet else 135]:
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = _unit(np.asarray(nodes[idx]) - np.asarray(nodes[parent]))
        v6._add_smooth_bulb_tip(mesh, centers[idx], nodes[idx], axis, radius=max(radii[idx] * 2.1, 0.035), segments=14, rings=4)
        bulb_count += 1
    panel_count = 0
    stride = max(len(edges) // (75 if sheet else 100), 1)
    for a, b in edges[::stride]:
        v6._add_edge_sheet(mesh, centers, nodes, a, b, width=0.026 if not sheet else 0.038, lift=0.09, faceted=False)
        panel_count += 1
    ctl.update(
        {
            "variant": variant,
            "attached_smooth_bulb_tips": bulb_count,
            "attached_sparse_porous_panels": panel_count,
            "surface_strategy": "high-section connected tubes plus rounded bulb tips and sparse edge-attached porous panels",
            "why_v7": "V6 DLA rendered as dark blocky mineral chunks; V7 uses smoother open organic frontier support before remote Trellis2 generation.",
        }
    )
    return mesh, ctl


def _crystal_mesh(seed: int, variant: str) -> tuple[pb.Mesh, dict]:
    mesh, ctl = v6.crystal_facet_case(seed)
    ctl = {**ctl, "variant": variant, "why_v7": "retain crystal/lattice as positive non-organic transform/DLA boundary candidate"}
    return mesh, ctl


def _mesh_stats(path: Path) -> dict:
    vertices, faces = rgm.parse_obj(path)
    comp = rgm.component_stats(vertices, faces)
    bbox = rgm.bbox_stats(vertices)
    return {
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
        "mesh_component_count": int(comp["component_count"]),
        "largest_mesh_component_vertex_ratio": float(comp["largest_component_vertex_ratio"]),
        "bbox_extent": [float(bbox["bbox_extent_x"]), float(bbox["bbox_extent_y"]), float(bbox["bbox_extent_z"])],
        "bbox_diag": float(bbox["bbox_diag"]),
    }


def _write_guides(out_dir: Path) -> dict[str, str]:
    from PIL import Image, ImageDraw, ImageFilter

    guide_dir = out_dir / "_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)

    def save(name: str, bg: tuple[int, int, int], palette: list[tuple[int, int, int]], mode: str) -> str:
        rng = np.random.default_rng(sum((i + 1) * b for i, b in enumerate(name.encode("utf-8"))) % (2**32))
        img = Image.new("RGB", (768, 768), bg)
        draw = ImageDraw.Draw(img)
        for _ in range(980):
            c = palette[int(rng.integers(0, len(palette)))]
            x, y = int(rng.integers(0, 768)), int(rng.integers(0, 768))
            if mode == "coral":
                r = int(rng.integers(7, 24))
                draw.ellipse((x - r, y - r, x + r, y + r), outline=c, width=int(rng.integers(2, 7)))
                if rng.random() < 0.65:
                    draw.line((x, y, x + int(rng.normal(0, 82)), y + int(rng.normal(0, 82))), fill=c, width=int(rng.integers(3, 9)))
            else:
                r = int(rng.integers(10, 38))
                draw.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=c)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "coral_warm": save("v7_bright_branching_coral_guide.png", (210, 124, 104), [(252, 184, 132), (238, 102, 86), (255, 219, 160), (177, 74, 85), (248, 148, 107)], "coral"),
        "coral_ivory": save("v7_ivory_reef_coral_guide.png", (192, 126, 102), [(246, 211, 170), (228, 154, 116), (174, 92, 91), (255, 235, 190)], "coral"),
        "crystal": save("v7_cool_pyrite_crystal_guide.png", (45, 52, 58), [(91, 110, 126), (146, 164, 178), (205, 210, 202), (75, 88, 105)], "facet"),
    }


def _case_specs(seed: int) -> list[dict]:
    cases: list[dict] = []

    def add(case_id: str, target: str, mesh: pb.Mesh, guide_key: str, case_seed: int, controls: dict, gpu: int) -> None:
        cases.append(
            {
                "case_id": case_id,
                "family": "DLA/frontier",
                "traditional_target": target,
                "match_target": target,
                "recursive_mode": "stochastic accretive frontier attachment with occupancy exclusion",
                "mesh": mesh,
                "guide_key": guide_key,
                "seed": int(case_seed),
                "gpu_group": int(gpu),
                "operators": ["stochastic_frontier_attachment", "occupancy_exclusion", "smooth_tube_support", "bulbous_tip_naturalization", "edge_attached_porous_panels"],
                "operator_composition": "stochastic_frontier_attachment -> occupancy_exclusion -> smooth_tube_support -> bulbous_tip_naturalization -> edge_attached_porous_panels",
                "controls": controls,
                "why_matches_traditional": "Starts from the same DLA/frontier task family and preserves stochastic accretive attachment plus exclusion; V7 changes only the asset-quality surface instantiation.",
            }
        )

    mesh, ctl = _organic_coral_mesh(seed + 1, "open_branching_coral")
    add("v7_dla_coral_open_branching_smooth_tips", "dla_coral_cluster_900", mesh, "coral_warm", seed + 201, ctl, 4)
    mesh, ctl = _organic_coral_mesh(seed + 2, "dense_porous_coral")
    add("v7_dla_coral_dense_porous_smooth_tips", "dla_coral_cluster_900", mesh, "coral_ivory", seed + 202, ctl, 5)
    mesh, ctl = _organic_coral_mesh(seed + 3, "frontier_sheet")
    add("v7_dla_frontier_open_reef_boundary", "dla_frontier_sheet_700", mesh, "coral_warm", seed + 203, ctl, 6)
    mesh, ctl = _organic_coral_mesh(seed + 4, "frontier_sheet")
    add("v7_dla_frontier_ivory_reef_boundary", "dla_frontier_sheet_700", mesh, "coral_ivory", seed + 204, ctl, 7)
    mesh, ctl = _crystal_mesh(seed + 5, "pyrite_boundary")
    add("v7_dla_crystal_faceted_pyrite_boundary", "dla_crystal_cluster_520", mesh, "crystal", seed + 205, ctl, 4)
    mesh, ctl = _organic_coral_mesh(seed + 6, "open_branching_coral")
    add("v7_dla_coral_open_branching_seed_b", "dla_coral_cluster_900", mesh, "coral_warm", seed + 206, ctl, 5)
    mesh, ctl = _organic_coral_mesh(seed + 7, "frontier_sheet")
    add("v7_dla_frontier_open_reef_seed_b", "dla_frontier_sheet_700", mesh, "coral_ivory", seed + 207, ctl, 6)
    mesh, ctl = _crystal_mesh(seed + 8, "blue_crystal_boundary")
    add("v7_dla_crystal_connected_blue_facets", "dla_crystal_cluster_520", mesh, "crystal", seed + 208, ctl, 7)
    return cases


def materialize(root: Path, out_dir: Path, seed: int = 20260510) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    guides = _write_guides(out_dir)
    rows: list[dict] = []
    metrics_rows: list[dict] = []
    for spec in _case_specs(seed):
        case_dir = out_dir / spec["case_id"]
        case_dir.mkdir(parents=True, exist_ok=True)
        mesh_path = case_dir / f"{spec['case_id']}.obj"
        pb.write_obj(mesh_path, spec["mesh"])
        metrics = _mesh_stats(mesh_path)
        guide = guides[spec["guide_key"]]
        meta = {k: v for k, v in spec.items() if k not in {"mesh", "guide_key"}}
        meta.update({"remote_target": REMOTE_TARGET, "mesh_path": str(mesh_path), "guide_image": guide, "initial_mesh_metrics": metrics})
        metadata_path = case_dir / f"{spec['case_id']}_metadata.json"
        metadata_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        rows.append(
            {
                "case_id": spec["case_id"],
                "family": spec["family"],
                "traditional_target": spec["traditional_target"],
                "match_target": spec["match_target"],
                "mesh_path": str(mesh_path),
                "guide_image": guide,
                "metadata_path": str(metadata_path),
                "remote_target": REMOTE_TARGET,
                "gpu_group": spec["gpu_group"],
                "seed": spec["seed"],
                "operator_composition": spec["operator_composition"],
                "why_matches_traditional": spec["why_matches_traditional"],
            }
        )
        metrics_rows.append({"case_id": spec["case_id"], "traditional_target": spec["traditional_target"], **metrics})
    fields = list(rows[0].keys())
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    metric_fields = list(metrics_rows[0].keys())
    with (out_dir / "initial_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        writer.writerows(metrics_rows)
    (out_dir / "initial_metrics.json").write_text(json.dumps(metrics_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    for gpu in (4, 5, 6, 7):
        selected = [r for r in rows if int(r["gpu_group"]) == gpu]
        lines = [f"{r['case_id']}|{r['mesh_path']}|{r['guide_image']}|{r['seed']}|{r['gpu_group']}" for r in selected]
        (out_dir / f"gpu{gpu}_cases.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    lines = [f"{r['case_id']}|{r['mesh_path']}|{r['guide_image']}|{r['seed']}|{r['gpu_group']}" for r in rows]
    (out_dir / "gpu4567_cases.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary = {"out_dir": str(out_dir), "num_cases": len(rows), "remote_target": REMOTE_TARGET, "manifest": str(out_dir / "manifest.csv")}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("RGG_ROOT", ROOT_DIR)))
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=20260510)
    args = parser.parse_args()
    materialize(args.root, args.out or DEFAULT_OUT, args.seed)


if __name__ == "__main__":
    main()
