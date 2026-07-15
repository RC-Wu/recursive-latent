#!/usr/bin/env python3
"""V13b implicit-surface DLA/coral/crystal strict matched input generator.

V12 proved the connectivity objective but failed visually: the generated assets
were still cylinders with visible cut ends.  V13b keeps the same strict
DLA/frontier formulation, but changes the *surface generator* from tube meshes
to a connected implicit field decoded with marching cubes.  The classical part
is still an active-frontier stochastic attachment process with occupancy
exclusion; the implicit field only turns that graph into an organic mesh.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from skimage import measure

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import procedural_baselines as pb
import recursive_growth_mesh_metrics as rgm
import strict_visual_matched_cases_v6_connectivity_20260510 as v6

REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 100
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_v13b_implicit_coral_20260510_dryrun"


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _basis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return v6._basis(axis)


def _smoothstep(t: np.ndarray) -> np.ndarray:
    return t * t * (3.0 - 2.0 * t)


def _normalize(nodes: list[np.ndarray], extent: float = 2.35) -> list[np.ndarray]:
    return v6._normalize_nodes(nodes, extent)


def _frontier_graph(seed: int, mode: str) -> tuple[list[np.ndarray], list[tuple[int, int]], list[int], dict]:
    rng = np.random.default_rng(seed)
    nodes: list[np.ndarray] = [np.zeros(3, dtype=float)]
    edges: list[tuple[int, int]] = []
    depths = [0]
    tips: list[tuple[int, np.ndarray, int]] = []

    if mode == "table":
        dirs = [_unit(np.array([math.cos(a), math.sin(a), 0.08])) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
        max_depth, step0, branch_prob = 5, 0.27, 0.70
        aniso = np.array([1.28, 1.28, 0.34])
    elif mode == "frontier":
        dirs = [_unit(np.array([x, 0.42 * math.sin(i * 0.9), 0.03])) for i, x in enumerate(np.linspace(-1.0, 1.0, 9))]
        max_depth, step0, branch_prob = 5, 0.25, 0.64
        aniso = np.array([1.55, 0.92, 0.27])
    elif mode == "crystal":
        dirs = [_unit(np.array([math.cos(a), math.sin(a), 0.35])) for a in np.linspace(0, 2 * math.pi, 7, endpoint=False)]
        max_depth, step0, branch_prob = 4, 0.28, 0.55
        aniso = np.array([1.00, 1.00, 0.72])
    else:
        dirs = [_unit(np.array([math.cos(a), math.sin(a), 0.48])) for a in np.linspace(0, 2 * math.pi, 7, endpoint=False)]
        max_depth, step0, branch_prob = 5, 0.25, 0.76
        aniso = np.array([0.98, 0.98, 1.05])
    for d in dirs:
        tips.append((0, _unit(d * aniso), 1))

    attempts = 0
    while tips and attempts < 1200 and len(nodes) < (145 if mode != "crystal" else 105):
        parent, direction, depth = tips.pop(0)
        attempts += 1
        if depth > max_depth:
            continue
        bend = rng.normal(0.0, 0.18 if mode != "crystal" else 0.05, 3)
        if mode == "table":
            bend[2] *= 0.20
        if mode == "staghorn":
            bend[2] += 0.08
        new_dir = _unit((direction + bend) * aniso)
        step = step0 * (0.84 ** (depth - 1)) * rng.uniform(0.78, 1.12)
        p = nodes[parent] + new_dir * step
        reject_radius = 0.075 * (0.90 ** depth)
        if any(float(np.linalg.norm(p - q)) < reject_radius for q in nodes):
            continue
        idx = len(nodes)
        nodes.append(p)
        depths.append(depth)
        edges.append((parent, idx))
        fan = 2 if rng.random() < branch_prob else 1
        if depth < max_depth:
            for _ in range(fan):
                tips.append((idx, _unit(new_dir + rng.normal(0.0, 0.38, 3)), depth + 1))

    # Tapered terminal continuations remove V12's flat terminal cuts.
    child = {i: 0 for i in range(len(nodes))}
    parent_of = {0: -1}
    for a, b in edges:
        child[a] += 1
        child.setdefault(b, 0)
        parent_of[b] = a
    for i in [i for i in range(1, len(nodes)) if child.get(i, 0) == 0]:
        p = parent_of.get(i, 0)
        d = _unit(nodes[i] - nodes[p])
        nodes.append(nodes[i] + d * (0.10 if mode != "crystal" else 0.075))
        depths.append(depths[i] + 1)
        edges.append((i, len(nodes) - 1))

    nodes = _normalize(nodes, 2.45)
    return nodes, edges, depths, {
        "mode": mode,
        "frontier_nodes": len(nodes),
        "frontier_edges": len(edges),
        "max_depth": max(depths),
        "attempts": attempts,
        "frontier_attachment_mode": "active-tip stochastic attachment",
        "occupancy_exclusion": "reject candidate frontier nodes inside a depth-scaled exclusion radius",
    }


def _implicit_mesh(
    nodes: list[np.ndarray],
    edges: list[tuple[int, int]],
    depths: list[int],
    seed: int,
    mode: str,
    grid: int = 78,
) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 1337)
    pts = np.asarray(nodes, dtype=np.float32)
    margin = 0.28
    mn = pts.min(axis=0) - margin
    mx = pts.max(axis=0) + margin
    extent = mx - mn
    xs = np.linspace(mn[0], mx[0], grid, dtype=np.float32)
    ys = np.linspace(mn[1], mx[1], grid, dtype=np.float32)
    zs = np.linspace(mn[2], mx[2], grid, dtype=np.float32)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    P = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    field = np.full(P.shape[0], 1e6, dtype=np.float32)
    max_depth = max(depths) if depths else 1

    def add_capsule(a: int, b: int, radius_scale: float = 1.0) -> None:
        nonlocal field
        pa = pts[a]
        pb_ = pts[b]
        ab = pb_ - pa
        denom = float(np.dot(ab, ab)) + 1e-8
        t = np.clip(((P - pa) @ ab) / denom, 0.0, 1.0)
        q = pa + t[:, None] * ab
        depth = depths[b] if b < len(depths) else max_depth
        base = (0.085 * (1.0 - 0.70 * depth / max_depth) + 0.014) * radius_scale
        if mode == "crystal":
            base *= 0.78
        # Soft radius modulation produces organic coral ridges while preserving one field.
        wrinkle = 1.0 + 0.10 * np.sin(7.0 * t + seed * 0.001) + 0.05 * np.sin(19.0 * t + a)
        d = np.linalg.norm(P - q, axis=1) - base * wrinkle
        field = np.minimum(field, d.astype(np.float32))

    for a, b in edges:
        add_capsule(a, b, 1.00)

    # Attach lobes and porous ridges to existing skeleton vertices. They are
    # deliberately anchored, never free-floating particles.
    child_count = {i: 0 for i in range(len(nodes))}
    parent_of = {0: -1}
    for a, b in edges:
        child_count[a] = child_count.get(a, 0) + 1
        child_count.setdefault(b, 0)
        parent_of[b] = a
    tips = [i for i in range(1, len(nodes)) if child_count.get(i, 0) == 0]
    rng.shuffle(tips)

    lobe_count = 0
    for i in tips[:72 if mode != "crystal" else 38]:
        p = parent_of.get(i, 0)
        d = _unit(pts[i] - pts[p])
        c = pts[i] + d * rng.uniform(0.010, 0.035)
        if mode == "crystal":
            axes = np.array([0.060, 0.040, 0.026], dtype=np.float32) * rng.uniform(0.75, 1.05)
        else:
            axes = np.array([0.070, 0.052, 0.040], dtype=np.float32) * rng.uniform(0.70, 1.12)
        # Use a sphere-like lobe in the global coordinates; this is not exact
        # ellipsoid distance but is stable and attached through overlap.
        dist = np.sqrt(((P - c) / axes)[:, 0] ** 2 + ((P - c) / axes)[:, 1] ** 2 + ((P - c) / axes)[:, 2] ** 2)
        field = np.minimum(field, ((dist - 1.0) * float(axes.min())).astype(np.float32))
        lobe_count += 1

    plate_count = 0
    if mode in {"table", "frontier", "staghorn"}:
        for a, b in edges[:: max(1, len(edges) // 52)]:
            pa, pb_ = pts[a], pts[b]
            mid = (pa + pb_) * 0.5
            axis = pb_ - pa
            u, v, _ = _basis(axis)
            c = mid + (u * rng.normal(0.0, 0.025) + v * rng.normal(0.0, 0.025)).astype(np.float32)
            axes = np.array([0.150, 0.052, 0.020], dtype=np.float32) * rng.uniform(0.75, 1.10)
            rel = P - c
            q0 = rel @ u
            q1 = rel @ v
            q2 = rel @ _unit(axis)
            dist = np.sqrt((q0 / axes[0]) ** 2 + (q1 / axes[1]) ** 2 + (q2 / axes[2]) ** 2)
            field = np.minimum(field, ((dist - 1.0) * float(axes.min())).astype(np.float32))
            plate_count += 1

    if mode == "crystal":
        # Mild faceting: move the level set toward an octahedral metric.
        field += (0.010 * (np.sin(P[:, 0] * 19.0) + np.sin(P[:, 1] * 17.0) + np.sin(P[:, 2] * 13.0))).astype(np.float32)
    else:
        # Tiny deterministic naturalization, not enough to detach components.
        field += (0.006 * np.sin(P[:, 0] * 13.0 + seed) * np.sin(P[:, 1] * 11.0) * np.sin(P[:, 2] * 7.0)).astype(np.float32)

    vol = field.reshape((grid, grid, grid))
    verts, faces, _, _ = measure.marching_cubes(vol, level=0.0, spacing=(extent[0] / (grid - 1), extent[1] / (grid - 1), extent[2] / (grid - 1)))
    verts = verts + mn[None, :]
    mesh = pb.Mesh([tuple(map(float, v)) for v in verts], [tuple(int(i) + 1 for i in f) for f in faces])
    return mesh, {
        "implicit_grid": grid,
        "implicit_surface": "union of connected capsules plus anchored lobes/plates decoded by marching cubes",
        "attached_lobes": lobe_count,
        "attached_plates": plate_count,
        "no_free_particles": True,
    }


def _write_guides(out_dir: Path) -> dict[str, str]:
    from PIL import Image, ImageDraw, ImageFilter

    guide_dir = out_dir / "_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)

    def save(name: str, bg: tuple[int, int, int], palette: list[tuple[int, int, int]], lines: int = 280) -> str:
        rng = np.random.default_rng(sum((i + 3) * b for i, b in enumerate(name.encode("utf-8"))))
        img = Image.new("RGB", (768, 768), bg)
        draw = ImageDraw.Draw(img)
        for _ in range(lines):
            color = palette[int(rng.integers(0, len(palette)))]
            x, y = int(rng.integers(0, 768)), int(rng.integers(0, 768))
            dx, dy = int(rng.normal(0, 120)), int(rng.normal(0, 100))
            width = int(rng.integers(4, 13))
            draw.line((x, y, x + dx, y + dy), fill=color, width=width)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "pink": save("v13b_soft_pink_coral_guide.png", (238, 126, 116), [(255, 224, 184), (250, 146, 126), (216, 88, 104), (255, 188, 148)]),
        "ivory": save("v13b_ivory_table_coral_guide.png", (230, 176, 128), [(255, 238, 192), (238, 194, 132), (210, 128, 92), (250, 220, 166)]),
        "frontier": save("v13b_red_frontier_sheet_guide.png", (184, 98, 92), [(250, 194, 152), (218, 118, 104), (136, 62, 78), (242, 164, 126)]),
        "crystal": save("v13b_blue_black_crystal_guide.png", (54, 64, 82), [(88, 124, 164), (184, 208, 222), (226, 198, 126), (42, 52, 68)]),
    }


def _case_specs(seed: int) -> list[dict]:
    specs: list[dict] = []

    def add(case_id: str, target: str, mode: str, guide_key: str, offset: int, gpu: int) -> None:
        nodes, edges, depths, graph_ctl = _frontier_graph(seed + offset, mode)
        mesh, surf_ctl = _implicit_mesh(nodes, edges, depths, seed + offset, mode, grid=76 if mode != "crystal" else 72)
        controls = {**graph_ctl, **surf_ctl}
        operators = [
            "stochastic_frontier_attachment",
            "occupancy_exclusion",
            "connected_implicit_field_projection",
            "anchored_lobe_plate_naturalization",
            "marching_cubes_mesh_decode",
        ]
        specs.append(
            {
                "case_id": case_id,
                "family": "DLA/frontier",
                "match_target": target,
                "traditional_target": target,
                "recursive_mode": "stochastic frontier attachment with occupancy exclusion, followed by connected implicit surface projection",
                "mesh": mesh,
                "guide_key": guide_key,
                "seed": int(seed + offset),
                "gpu": int(gpu),
                "controls": controls,
                "operators": operators,
                "operator_composition": " -> ".join(operators),
                "why_matches_traditional": "Same DLA/frontier accretive growth mode as the classical target; only the root/token surface is upgraded into a connected implicit organic asset.",
                "strict_match_notes": "Fresh a100-2 case input; not local postprocessing of a prior GLB.",
                "case_role": "priority_a100_2",
            }
        )

    add("v13b_implicit_staghorn_coral_a", "dla_coral_cluster_900", "staghorn", "pink", 901, 4)
    add("v13b_implicit_staghorn_coral_b", "dla_coral_cluster_900", "staghorn", "pink", 902, 5)
    add("v13b_implicit_table_coral_a", "dla_coral_cluster_900", "table", "ivory", 903, 6)
    add("v13b_implicit_table_coral_b", "dla_coral_cluster_900", "table", "ivory", 904, 7)
    add("v13b_implicit_frontier_sheet_a", "dla_frontier_sheet_700", "frontier", "frontier", 905, 4)
    add("v13b_implicit_frontier_sheet_b", "dla_frontier_sheet_700", "frontier", "frontier", 906, 5)
    add("v13b_implicit_crystal_cluster_a", "dla_crystal_cluster_520", "crystal", "crystal", 907, 6)
    add("v13b_implicit_crystal_cluster_b", "dla_crystal_cluster_520", "crystal", "crystal", 908, 7)
    return specs


def _mesh_stats(path: Path) -> dict:
    vertices, faces = rgm.parse_obj(path)
    comp = rgm.component_stats(vertices, faces)
    bbox = rgm.bbox_stats(vertices)
    surface_area = 0.0
    if len(vertices) and len(faces):
        tri = vertices[faces]
        surface_area = float(np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1).sum() * 0.5)
    return {
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
        "mesh_component_count": int(comp["component_count"]),
        "largest_mesh_component_vertex_ratio": float(comp["largest_component_vertex_ratio"]),
        "bbox_extent": [float(bbox["bbox_extent_x"]), float(bbox["bbox_extent_y"]), float(bbox["bbox_extent_z"])],
        "bbox_diag": float(bbox["bbox_diag"]),
        "surface_area": surface_area,
    }


def materialize(root: Path, out_dir: Path, seed: int, case_limit: int | None = None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    guides = _write_guides(out_dir)
    specs = _case_specs(seed)
    if case_limit is not None:
        specs = specs[: int(case_limit)]
    rows: list[dict] = []
    metrics_rows: list[dict] = []
    for spec in specs:
        case_dir = out_dir / spec["case_id"]
        case_dir.mkdir(parents=True, exist_ok=True)
        mesh_path = case_dir / f"{spec['case_id']}.obj"
        pb.write_obj(mesh_path, spec["mesh"])
        metrics = _mesh_stats(mesh_path)
        if metrics["mesh_component_count"] != 1:
            raise RuntimeError(f"{spec['case_id']} has {metrics['mesh_component_count']} components: {metrics}")
        meta = {
            **{k: spec[k] for k in ["case_id", "family", "match_target", "traditional_target", "recursive_mode", "seed", "controls", "operators", "operator_composition", "why_matches_traditional", "strict_match_notes", "case_role"]},
            "remote_target": REMOTE_TARGET,
            "allowed_gpus": ALLOWED_GPUS,
            "mesh_path": str(mesh_path),
            "guide_image": guides[spec["guide_key"]],
            "initial_mesh_metrics": metrics,
            "v13b_design_note": "implicit/metaball-like connected surface projection avoids V12 cylinder cut-end failure while preserving DLA/frontier operator provenance",
        }
        metadata_path = case_dir / f"{spec['case_id']}_metadata.json"
        metadata_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        row = {
            "case_id": spec["case_id"],
            "family": spec["family"],
            "match_target": spec["match_target"],
            "traditional_target": spec["traditional_target"],
            "recursive_mode": spec["recursive_mode"],
            "mesh_path": str(mesh_path),
            "guide_image": guides[spec["guide_key"]],
            "metadata_path": str(metadata_path),
            "remote_target": REMOTE_TARGET,
            "gpu_group": spec["gpu"],
            "seed": spec["seed"],
            "operators": json.dumps(spec["operators"], ensure_ascii=False),
            "operator_composition": spec["operator_composition"],
            "controls": json.dumps(spec["controls"], ensure_ascii=False, sort_keys=True),
            "why_matches_traditional": spec["why_matches_traditional"],
            "strict_match_notes": spec["strict_match_notes"],
            "case_role": spec["case_role"],
            "strict_one_to_one": "true",
            "generation_policy": "generate_new_on_a100_2_no_local_cherrypick",
            "storage_root": REMOTE_STORAGE_ROOT,
            "storage_limit_gb": STORAGE_LIMIT_GB,
        }
        rows.append(row)
        metrics_rows.append({"case_id": spec["case_id"], **metrics})

    manifest_fields = list(rows[0].keys()) if rows else []
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    metric_fields = list(metrics_rows[0].keys()) if metrics_rows else []
    with (out_dir / "initial_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        writer.writerows(metrics_rows)
    (out_dir / "initial_metrics.json").write_text(json.dumps(metrics_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [f"{r['case_id']}|{r['mesh_path']}|{r['guide_image']}|{r['seed']}|{r['gpu_group']}" for r in rows]
    (out_dir / "a100-2_cases.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    for gpu in ALLOWED_GPUS:
        gpu_lines = [line for line, row in zip(lines, rows) if int(row["gpu_group"]) == gpu]
        (out_dir / f"gpu{gpu}_cases.txt").write_text("\n".join(gpu_lines) + ("\n" if gpu_lines else ""), encoding="utf-8")
    (out_dir / "gpu4567_cases.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    summary = {
        "out_dir": str(out_dir),
        "num_cases": len(rows),
        "remote_target": REMOTE_TARGET,
        "allowed_gpus": ALLOWED_GPUS,
        "manifest": str(out_dir / "manifest.csv"),
        "initial_metrics": str(out_dir / "initial_metrics.csv"),
        "v13b_note": "implicit connected DLA/frontier inputs replacing tube mesh surface",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260510)
    parser.add_argument("--case-limit", type=int, default=None)
    args = parser.parse_args()
    print(json.dumps(materialize(args.root, args.out, args.seed, args.case_limit), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
