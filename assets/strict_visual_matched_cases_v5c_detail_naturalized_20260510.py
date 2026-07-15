#!/usr/bin/env python3
"""V5c detail-naturalized strict matched Trellis2 input generator.

This is an input-generation experiment, not a postprocess of rendered results.
It starts from the V5 hybrid strict matched graphs, then adds attached local
detail primitives before remote Trellis2 texturing: needle/leaf/rootlet fans for
plant tasks and rounded attached lobes for DLA/frontier tasks.  The goal is to
test whether local grammar-token naturalization can improve visual category
readability without losing the V5 connected support graph.
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
import strict_visual_matched_cases_v5_hybrid_20260510 as v5

REMOTE_TARGET = "a100-2"
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_v5c_detail_naturalized_20260510_dryrun"


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _basis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = _unit(axis)
    seed = np.array([0.0, 0.0, 1.0]) if abs(w[2]) < 0.92 else np.array([1.0, 0.0, 0.0])
    u = _unit(np.cross(w, seed))
    v = _unit(np.cross(w, u))
    return u, v, w


def _vertices(mesh: pb.Mesh) -> np.ndarray:
    return np.asarray(mesh.vertices, dtype=float) if mesh.vertices else np.zeros((0, 3), dtype=float)


def _add_tapered_card(mesh: pb.Mesh, anchor0: int, direction: np.ndarray, length: float, width: float, skew: float = 0.25) -> None:
    verts = _vertices(mesh)
    if len(verts) == 0:
        return
    anchor = verts[int(anchor0)]
    u, vdir, w = _basis(direction)
    c0 = anchor + w * length * 0.26
    c1 = anchor + w * length
    base = len(mesh.vertices)
    mesh.vertices.extend(
        [
            tuple(c0 + u * width),
            tuple(c0 - u * width),
            tuple(c1 + u * width * skew + vdir * width * 0.20),
            tuple(c1 - u * width * skew - vdir * width * 0.20),
        ]
    )
    a = anchor0 + 1
    b = _edge_neighbor(mesh, anchor0)
    mesh.faces.extend(
        [
            (a, b, base + 1),
            (b, base + 2, base + 1),
            (a, base + 1, base + 2),
            (base + 1, base + 3, base + 2),
            (base + 2, base + 3, base + 4),
            (a, base + 2, base + 4),
        ]
    )


def _add_leaf_disk(mesh: pb.Mesh, anchor0: int, direction: np.ndarray, radius: float, aspect: float, sides: int = 8) -> None:
    verts = _vertices(mesh)
    if len(verts) == 0:
        return
    anchor = verts[int(anchor0)]
    u, vdir, w = _basis(direction)
    center = anchor + w * radius * 1.2
    base = len(mesh.vertices)
    for i in range(sides):
        theta = 2.0 * math.pi * i / sides
        p = center + math.cos(theta) * u * radius * aspect + math.sin(theta) * vdir * radius
        mesh.vertices.append(tuple(p))
    a = anchor0 + 1
    b = _edge_neighbor(mesh, anchor0)
    mesh.faces.append((a, b, base + 1))
    mesh.faces.append((b, base + 2, base + 1))
    for i in range(sides):
        j = (i + 1) % sides
        mesh.faces.append((a, base + i + 1, base + j + 1))


def _add_lobed_cap(mesh: pb.Mesh, anchor0: int, direction: np.ndarray, radius: float, rings: int = 2, sides: int = 10) -> None:
    verts = _vertices(mesh)
    if len(verts) == 0:
        return
    anchor = verts[int(anchor0)]
    u, vdir, w = _basis(direction)
    center = anchor + w * radius * 0.9
    base = len(mesh.vertices)
    ring_ids: list[list[int]] = []
    for r in range(1, rings + 1):
        phi = (math.pi * 0.46) * r / (rings + 1)
        ring: list[int] = []
        for i in range(sides):
            theta = 2.0 * math.pi * i / sides
            p = center + w * (radius * math.cos(phi)) + (math.cos(theta) * u + math.sin(theta) * vdir) * (radius * math.sin(phi))
            mesh.vertices.append(tuple(p))
            ring.append(base + len(ring_ids) * sides + i + 1)
        ring_ids.append(ring)
    tip = len(mesh.vertices) + 1
    mesh.vertices.append(tuple(center + w * radius * 1.15))
    a = anchor0 + 1
    b = _edge_neighbor(mesh, anchor0)
    first = ring_ids[0]
    mesh.faces.append((a, b, first[0]))
    mesh.faces.append((b, first[1], first[0]))
    for i in range(sides):
        j = (i + 1) % sides
        mesh.faces.append((a, first[j], first[i]))
    for ridx in range(len(ring_ids) - 1):
        ring0, ring1 = ring_ids[ridx], ring_ids[ridx + 1]
        for i in range(sides):
            j = (i + 1) % sides
            mesh.faces.append((ring0[i], ring0[j], ring1[i]))
            mesh.faces.append((ring0[j], ring1[j], ring1[i]))
    last = ring_ids[-1]
    for i in range(sides):
        j = (i + 1) % sides
        mesh.faces.append((last[i], last[j], tip))


def _edge_neighbor(mesh: pb.Mesh, anchor0: int) -> int:
    """Return a 1-based vertex id sharing a face edge with anchor0 when possible."""
    a = int(anchor0) + 1
    for face in mesh.faces:
        if a not in face:
            continue
        for vid in face:
            if vid != a:
                return int(vid)
    return a


def _candidate_indices(mesh: pb.Mesh, seed: int, n: int, mode: str) -> list[int]:
    verts = _vertices(mesh)
    if len(verts) == 0:
        return []
    rng = np.random.default_rng(seed)
    centered = verts - verts.mean(axis=0, keepdims=True)
    radius = np.linalg.norm(centered[:, :2], axis=1)
    score = radius + 0.18 * centered[:, 2]
    if mode in {"root", "coral"}:
        score = radius - 0.10 * centered[:, 2]
    order = np.argsort(score)[::-1]
    keep = order[: max(n * 8, n)]
    rng.shuffle(keep)
    return [int(i) for i in keep[:n]]


def _naturalize_mesh(mesh: pb.Mesh, case_id: str, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    verts = _vertices(mesh)
    if len(verts) == 0:
        return {"local_detail_primitives": 0}
    center = verts.mean(axis=0)
    added = 0
    if "pine" in case_id:
        for idx in _candidate_indices(mesh, seed, 150, "pine"):
            direction = _unit((verts[idx] - center) + np.array([0.0, 0.0, 0.24]) + rng.normal(0, 0.09, 3))
            _add_tapered_card(mesh, idx, direction, rng.uniform(0.050, 0.115), rng.uniform(0.0045, 0.0090), skew=0.08)
            added += 1
    elif "vine" in case_id or "crown" in case_id:
        count = 120 if "crown" in case_id else 70
        for idx in _candidate_indices(mesh, seed, count, "leaf"):
            direction = _unit((verts[idx] - center) + np.array([0.0, 0.0, 0.18]) + rng.normal(0, 0.10, 3))
            _add_leaf_disk(mesh, idx, direction, rng.uniform(0.025, 0.052), rng.uniform(1.5, 2.4), sides=8)
            added += 1
    elif "root" in case_id:
        for idx in _candidate_indices(mesh, seed, 125, "root"):
            direction = _unit((verts[idx] - center) + np.array([0.0, 0.0, -0.35]) + rng.normal(0, 0.13, 3))
            _add_tapered_card(mesh, idx, direction, rng.uniform(0.055, 0.140), rng.uniform(0.003, 0.006), skew=0.05)
            added += 1
    elif "coral" in case_id or "frontier" in case_id:
        for idx in _candidate_indices(mesh, seed, 120, "coral"):
            direction = _unit((verts[idx] - center) + rng.normal(0, 0.08, 3))
            _add_lobed_cap(mesh, idx, direction, rng.uniform(0.030, 0.060), rings=2, sides=10)
            added += 1
    elif "radial" in case_id:
        for idx in _candidate_indices(mesh, seed, 28, "radial"):
            direction = _unit((verts[idx] - center) + np.array([0.0, 0.0, 0.06]))
            _add_lobed_cap(mesh, idx, direction, rng.uniform(0.026, 0.045), rings=1, sides=8)
            added += 1
    return {
        "local_detail_primitives": added,
        "detail_strategy": "attached grammar-token local naturalization before remote Trellis2 texturing",
    }


def _write_guides(out_dir: Path) -> dict[str, str]:
    from PIL import Image, ImageDraw, ImageFilter

    guide_dir = out_dir / "_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)

    def save(name: str, bg: tuple[int, int, int], palette: list[tuple[int, int, int]], mode: str) -> str:
        rng = np.random.default_rng(sum((i + 1) * b for i, b in enumerate(name.encode("utf-8"))) % (2**32))
        img = Image.new("RGB", (768, 768), bg)
        draw = ImageDraw.Draw(img)
        for _ in range(850):
            c = palette[int(rng.integers(0, len(palette)))]
            x, y = int(rng.integers(0, 768)), int(rng.integers(0, 768))
            if mode == "leaf":
                r = int(rng.integers(7, 24))
                draw.ellipse((x - r * 2, y - r, x + r * 2, y + r), fill=c)
            elif mode == "needle":
                draw.line((x, y, x + int(rng.normal(0, 88)), y + int(rng.normal(-24, 58))), fill=c, width=int(rng.integers(2, 5)))
            elif mode == "root":
                draw.line((x, y, x + int(rng.normal(0, 110)), y + int(rng.normal(42, 52))), fill=c, width=int(rng.integers(2, 7)))
            elif mode == "coral":
                r = int(rng.integers(8, 26))
                draw.ellipse((x - r, y - r, x + r, y + r), outline=c, width=int(rng.integers(3, 7)))
                if rng.random() < 0.55:
                    draw.line((x, y, x + int(rng.normal(0, 70)), y + int(rng.normal(0, 70))), fill=c, width=int(rng.integers(3, 8)))
            else:
                r = int(rng.integers(8, 36))
                draw.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=c)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        path = guide_dir / name
        img.save(path)
        return str(path)

    return {
        "conifer": save("v5c_conifer_needles_guide.png", (27, 44, 27), [(35, 74, 39), (58, 102, 52), (112, 128, 78), (79, 57, 35)], "needle"),
        "leaf": save("v5c_leaf_crown_vine_guide.png", (34, 64, 35), [(42, 100, 44), (82, 140, 62), (118, 154, 77), (65, 47, 30)], "leaf"),
        "root": save("v5c_root_fiber_guide.png", (34, 27, 22), [(59, 39, 27), (102, 72, 45), (151, 112, 69), (29, 22, 18)], "root"),
        "coral": save("v5c_warm_coral_guide.png", (100, 58, 63), [(219, 107, 93), (240, 154, 119), (255, 192, 143), (139, 62, 72)], "coral"),
        "gear": save("v5c_brushed_metal_radial_guide.png", (44, 43, 39), [(74, 75, 68), (140, 130, 101), (186, 151, 83), (80, 43, 35)], "metal"),
    }


def _mesh_stats(path: Path) -> dict:
    return v5._mesh_stats(path)


def materialize(root: Path, out_dir: Path, seed: int) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    guides = _write_guides(out_dir)
    specs = v5._case_specs(seed)
    rows: list[dict] = []
    metric_rows: list[dict] = []
    for spec in specs:
        old_id = spec["case_id"]
        spec["case_id"] = old_id.replace("v5_", "v5c_")
        detail = _naturalize_mesh(spec["mesh"], spec["case_id"], int(spec["seed"]) + 700)
        spec["operators"] = [*spec["operators"], "attached_local_detail_naturalization"]
        spec["operator_composition"] = " -> ".join(spec["operators"])
        spec["controls"] = {**spec["controls"], **detail, "v5c_source_case": old_id}
        spec["strict_match_notes"] = spec["why_matches_traditional"] + " V5c additionally attaches local grammar-token detail before remote texturing; this is not local repair of the output."
        if "coral" in spec["case_id"] or "frontier" in spec["case_id"]:
            spec["guide_key"] = "coral"
        elif "pine" in spec["case_id"]:
            spec["guide_key"] = "conifer"
        elif "root" in spec["case_id"]:
            spec["guide_key"] = "root"
        elif "radial" in spec["case_id"]:
            spec["guide_key"] = "gear"
        else:
            spec["guide_key"] = "leaf"

        case_dir = out_dir / spec["case_id"]
        mesh_path = case_dir / f"{spec['case_id']}.obj"
        case_dir.mkdir(parents=True, exist_ok=True)
        pb.write_obj(mesh_path, spec["mesh"])
        metrics = _mesh_stats(mesh_path)
        guide_path = guides[spec["guide_key"]]
        metadata = {
            "case_id": spec["case_id"],
            "family": spec["family"],
            "traditional_target": spec["traditional_target"],
            "match_target": spec["match_target"],
            "recursive_mode": spec["recursive_mode"],
            "remote_target": REMOTE_TARGET,
            "mesh_path": str(mesh_path),
            "guide_image": guide_path,
            "seed": int(spec["seed"]),
            "operators": spec["operators"],
            "operator_composition": spec["operator_composition"],
            "controls": spec["controls"],
            "initial_mesh_metrics": metrics,
            "why_matches_traditional": spec["why_matches_traditional"],
            "strict_match_notes": spec["strict_match_notes"],
            "root_selection_log": {
                "root_source_type": "algorithmically_generated_proxy_mesh",
                "root_source_provenance": "V5 hybrid graph plus V5c attached local detail naturalization",
                "remote_generation_required": True,
                "local_postprocess_of_remote_output": False,
            },
        }
        metadata_path = case_dir / f"{spec['case_id']}_metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        row = {
            "case_id": spec["case_id"],
            "family": spec["family"],
            "match_target": spec["match_target"],
            "traditional_target": spec["traditional_target"],
            "recursive_mode": spec["recursive_mode"],
            "mesh_path": str(mesh_path),
            "guide_image": guide_path,
            "metadata_path": str(metadata_path),
            "remote_target": REMOTE_TARGET,
            "gpu_group": 2,
            "seed": int(spec["seed"]),
            "operator_composition": spec["operator_composition"],
            "controls": json.dumps(spec["controls"], ensure_ascii=False, sort_keys=True),
            "strict_match_notes": spec["strict_match_notes"],
        }
        rows.append(row)
        metric_rows.append({"case_id": spec["case_id"], "traditional_target": spec["traditional_target"], **metrics})

    fields = list(rows[0].keys()) if rows else []
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    metric_fields = list(metric_rows[0].keys()) if metric_rows else []
    with (out_dir / "initial_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        writer.writerows(metric_rows)
    (out_dir / "initial_metrics.json").write_text(json.dumps(metric_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [f"{r['case_id']}|{r['mesh_path']}|{r['guide_image']}|{r['seed']}" for r in rows]
    (out_dir / "a100-2_cases.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    (out_dir / "gpu2_cases.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
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
