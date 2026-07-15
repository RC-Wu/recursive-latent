#!/usr/bin/env python3
"""Local same-root/same-depth baseline matrix for tree/root/vine cases."""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from collections import deque
from pathlib import Path

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import connected_scaffold_cases_v2_20260509 as scaffold


DEFAULT_OUT = ROOT_DIR / "results" / "baseline_matrix_20260509"
DEFAULT_DOC = ROOT_DIR / "docs" / "evaluation" / "baseline_matrix_zh_20260509.md"
CASES = ("tree", "root", "vine")
METHODS = ("lsystem", "space_colonization", "proposed_connected")
CASE_SEED_OFFSETS = {"tree": 101, "root": 211, "vine": 307}
METHOD_SEED_OFFSETS = {"lsystem": 11, "space_colonization": 23, "proposed_connected": 37}


def unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def rotation_matrix(axis: np.ndarray, angle: float) -> np.ndarray:
    axis = unit(np.asarray(axis, dtype=float))
    x, y, z = axis
    c, s = math.cos(angle), math.sin(angle)
    return np.asarray(
        [
            [c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
            [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
            [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)],
        ],
        dtype=float,
    )


def stable_rng(seed: int, case: str, method: str) -> np.random.Generator:
    return np.random.default_rng(seed + CASE_SEED_OFFSETS[case] + METHOD_SEED_OFFSETS[method])


def append_node(nodes: list[np.ndarray], parents: list[int], parent: int, point: np.ndarray) -> int:
    nodes.append(np.asarray(point, dtype=float))
    parents.append(int(parent))
    return len(nodes) - 1


def graph_depths(parents: list[int]) -> list[int]:
    depths = [0] * len(parents)
    for idx, parent in enumerate(parents):
        if parent >= 0:
            depths[idx] = depths[parent] + 1
    return depths


def child_counts(parents: list[int]) -> list[int]:
    counts = [0] * len(parents)
    for parent in parents:
        if parent >= 0:
            counts[parent] += 1
    return counts


def lsystem_case(case: str, depth: int, seed: int) -> tuple[list[np.ndarray], list[int]]:
    rng = stable_rng(seed, case, "lsystem")
    nodes = [np.zeros(3, dtype=float)]
    parents = [-1]

    if case == "tree":
        base_dir = np.array([0.0, 0.0, 1.0])
        segment = 8.0
        spread_axis = np.array([0.0, 1.0, 0.0])
    elif case == "root":
        base_dir = np.array([0.08, 0.0, -1.0])
        segment = 7.0
        spread_axis = np.array([0.0, 1.0, 0.0])
    else:
        base_dir = np.array([0.45, 0.08, 0.88])
        segment = 7.2
        spread_axis = np.array([1.0, 0.0, 0.0])

    def rec(parent: int, direction: np.ndarray, length: float, level: int, phase: float) -> None:
        if level <= 0:
            return
        direction = unit(direction)
        end = nodes[parent] + direction * length
        current = append_node(nodes, parents, parent, end)
        if case == "vine":
            twist = phase + 0.92 * level
            side = unit(np.array([math.cos(twist), math.sin(twist), 0.18]))
            tendril = append_node(nodes, parents, current, end + side * length * 0.55)
            if level > 1:
                append_node(nodes, parents, tendril, nodes[tendril] + side * length * 0.25 + np.array([0, 0, 1.4]))
            next_dir = unit(rotation_matrix(np.array([0, 0, 1.0]), 0.45) @ direction + np.array([0.12, 0.0, 0.18]))
            rec(current, next_dir, length * 0.92, level - 1, phase + 0.73)
            return

        angle = 0.42 if case == "tree" else 0.34
        for sign in (-1, 1):
            jitter = float(rng.normal(0.0, 0.045))
            turn = rotation_matrix(spread_axis, sign * (angle + jitter))
            twist = rotation_matrix(base_dir, phase + sign * 1.75)
            child_dir = unit(twist @ (turn @ direction))
            rec(current, child_dir, length * 0.68, level - 1, phase + sign * 0.71)
        if level > 1:
            rec(current, direction + rng.normal(0, 0.06, 3), length * 0.82, level - 1, phase + 0.31)

    rec(0, base_dir, segment, depth, 0.0)
    return nodes, parents


def sample_attractors(case: str, count: int, rng: np.random.Generator) -> np.ndarray:
    pts: list[np.ndarray] = []
    while len(pts) < count:
        p = rng.uniform(-1.0, 1.0, size=3)
        if case == "tree":
            q = np.array([p[0] * 23.0, p[1] * 23.0, 22.0 + p[2] * 18.0])
            ok = (q[0] / 24.0) ** 2 + (q[1] / 24.0) ** 2 + ((q[2] - 22.0) / 18.0) ** 2 <= 1.0
        elif case == "root":
            q = np.array([p[0] * 31.0, p[1] * 18.0, -24.0 + p[2] * 15.0])
            ok = (q[0] / 31.0) ** 2 + (q[1] / 18.0) ** 2 + ((q[2] + 24.0) / 15.0) ** 2 <= 1.0
        else:
            z = rng.uniform(5.0, 42.0)
            theta = 0.27 * z + rng.normal(0, 0.45)
            r = rng.uniform(9.0, 18.0)
            q = np.array([math.cos(theta) * r, math.sin(theta) * r, z]) + rng.normal(0, 2.2, 3)
            ok = True
        if ok:
            pts.append(q)
    return np.asarray(pts, dtype=float)


def initial_space_nodes(case: str) -> tuple[list[np.ndarray], list[int]]:
    nodes = [np.zeros(3, dtype=float)]
    parents = [-1]
    if case == "tree":
        append_node(nodes, parents, 0, np.array([0.0, 0.0, 7.0]))
        append_node(nodes, parents, 1, np.array([0.0, 0.0, 14.0]))
    elif case == "root":
        append_node(nodes, parents, 0, np.array([0.0, 0.0, -6.0]))
        append_node(nodes, parents, 1, np.array([1.5, 0.0, -12.0]))
    else:
        append_node(nodes, parents, 0, np.array([3.5, 1.0, 6.0]))
        append_node(nodes, parents, 1, np.array([6.5, 2.5, 12.0]))
    return nodes, parents


def space_colonization_case(case: str, depth: int, seed: int, quick: bool) -> tuple[list[np.ndarray], list[int]]:
    rng = stable_rng(seed, case, "space_colonization")
    attractor_count = (80 if quick else 220) + depth * (20 if quick else 60)
    iterations = depth * (18 if quick else 36)
    influence_radius = 12.0
    kill_radius = 3.0
    step = 4.2
    attractors = sample_attractors(case, attractor_count, rng)
    alive = np.ones(len(attractors), dtype=bool)
    nodes, parents = initial_space_nodes(case)

    for _ in range(iterations):
        active = np.nonzero(alive)[0]
        if len(active) == 0:
            break
        node_arr = np.asarray(nodes, dtype=float)
        attr = attractors[active]
        dist = np.linalg.norm(attr[:, None, :] - node_arr[None, :, :], axis=2)
        nearest_dist = dist.min(axis=1)
        alive[active[nearest_dist <= kill_radius]] = False
        active = active[(nearest_dist <= influence_radius) & (nearest_dist > kill_radius)]
        if len(active) == 0:
            continue
        dist = np.linalg.norm(attractors[active][:, None, :] - node_arr[None, :, :], axis=2)
        nearest = dist.argmin(axis=1)
        proposals: dict[int, list[np.ndarray]] = {}
        for attr_idx, node_idx in zip(active, nearest):
            proposals.setdefault(int(node_idx), []).append(unit(attractors[int(attr_idx)] - nodes[int(node_idx)]))
        existing = np.asarray(nodes, dtype=float)
        for node_idx, dirs in proposals.items():
            direction = unit(np.mean(np.asarray(dirs), axis=0) + rng.normal(0, 0.04, 3))
            candidate = nodes[node_idx] + direction * step
            if len(existing) and float(np.linalg.norm(existing - candidate, axis=1).min()) < step * 0.42:
                continue
            append_node(nodes, parents, node_idx, candidate)
    return nodes, parents


def proposed_case(case: str, depth: int, seed: int) -> tuple[list[np.ndarray], list[int], np.ndarray, float]:
    rng = stable_rng(seed, case, "proposed_connected")
    nodes = [np.zeros(3, dtype=float)]
    parents = [-1]

    if case == "tree":
        frontier = [(0, np.array([0.0, 0.0, 1.0]), 8.0)]
        for stage in range(1, depth + 1):
            new_frontier = []
            for parent, direction, length in frontier:
                end = nodes[parent] + unit(direction) * length
                node = append_node(nodes, parents, parent, end)
                new_frontier.append((node, direction + rng.normal(0, 0.04, 3), length * 0.82))
                if stage >= 2:
                    for sign in (-1, 1):
                        side = rotation_matrix(np.array([0.0, 1.0, 0.0]), sign * 0.48) @ unit(direction)
                        side = rotation_matrix(direction, sign * (0.9 + 0.2 * stage)) @ side
                        new_frontier.append((node, side, length * 0.58))
            frontier = new_frontier[: max(2, 3 * stage)]
    elif case == "root":
        frontier = [(0, np.array([0.1, 0.0, -1.0]), 7.5)]
        for stage in range(1, depth + 1):
            new_frontier = []
            for parent, direction, length in frontier:
                end = nodes[parent] + unit(direction) * length
                node = append_node(nodes, parents, parent, end)
                new_frontier.append((node, direction + np.array([0.04, 0.0, -0.08]) + rng.normal(0, 0.05, 3), length * 0.86))
                if stage >= 2:
                    for sign in (-1, 1):
                        side = unit(np.array([sign * 0.95, 0.28 * math.sin(stage + sign), -0.42]))
                        new_frontier.append((node, side, length * 0.54))
            frontier = new_frontier[: max(2, 2 * stage + 1)]
    else:
        parent = 0
        direction = np.array([0.45, 0.0, 0.88])
        for stage in range(1, depth + 1):
            theta = stage * 0.78
            helix = np.array([math.cos(theta) * 3.5, math.sin(theta) * 3.5, 7.0])
            node = append_node(nodes, parents, parent, nodes[parent] + helix)
            side = unit(np.array([math.cos(theta + 1.4), math.sin(theta + 1.4), 0.2]))
            tendril = append_node(nodes, parents, node, nodes[node] + side * (5.5 + stage))
            if stage >= 2:
                append_node(nodes, parents, tendril, nodes[tendril] + side * 2.5 + np.array([0, 0, 1.5]))
            if stage % 2 == 0:
                other = unit(np.array([math.cos(theta - 1.3), math.sin(theta - 1.3), -0.1]))
                append_node(nodes, parents, node, nodes[node] + other * 4.5)
            parent = node
            direction = unit(direction + helix * 0.02)

    raw_coords = skeleton_to_coords(nodes, parents, case, method="proposed_connected")
    for _ in range(depth):
        orphan = rng.uniform(-45.0, 45.0, size=3)
        if np.linalg.norm(orphan) > 16.0:
            scaffold.add_ball(set_proxy := set(map(tuple, raw_coords.tolist())), orphan, 2)
            raw_coords = scaffold.coords_array(set_proxy)
    projected = root_component_coords(raw_coords, np.zeros(3, dtype=float))
    survival = float(len(projected) / max(len(raw_coords), 1))
    return nodes, parents, projected, survival


def skeleton_to_coords(nodes: list[np.ndarray], parents: list[int], case: str, method: str) -> np.ndarray:
    points: set[tuple[int, int, int]] = set()
    depths = graph_depths(parents)
    max_depth = max(depths) if depths else 1
    base_radius = 3 if method == "proposed_connected" else 2
    scaffold.add_ball(points, np.zeros(3, dtype=float), base_radius + 1)
    for idx, parent in enumerate(parents):
        if parent < 0:
            continue
        frac = depths[idx] / max(max_depth, 1)
        radius = max(1, int(round(base_radius * (1.0 - 0.55 * frac))))
        if case == "root" and idx < 4:
            radius = max(radius, 2)
        scaffold.add_tube(points, nodes[parent], nodes[idx], radius)
        if method == "proposed_connected" and idx % 3 == 0:
            scaffold.add_ball(points, nodes[idx], max(radius, 2))
    return scaffold.coords_array(points)


def component_sizes(coords: np.ndarray) -> list[list[tuple[int, int, int]]]:
    coords = np.unique(np.asarray(coords, dtype=np.int32), axis=0)
    occupied = {tuple(row) for row in coords.tolist()}
    seen: set[tuple[int, int, int]] = set()
    comps: list[list[tuple[int, int, int]]] = []
    offsets = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    for start in occupied:
        if start in seen:
            continue
        q: deque[tuple[int, int, int]] = deque([start])
        seen.add(start)
        comp: list[tuple[int, int, int]] = []
        while q:
            p = q.popleft()
            comp.append(p)
            x, y, z = p
            for dx, dy, dz in offsets:
                nxt = (x + dx, y + dy, z + dz)
                if nxt in occupied and nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        comps.append(comp)
    return comps


def root_component_coords(coords: np.ndarray, root: np.ndarray) -> np.ndarray:
    coords = np.unique(np.asarray(coords, dtype=np.int32), axis=0)
    if len(coords) == 0:
        return coords
    root_int = tuple(np.rint(root).astype(int).tolist())
    comps = component_sizes(coords)
    if root_int not in {tuple(row) for row in coords.tolist()}:
        nearest = coords[np.linalg.norm(coords - np.rint(root).astype(int), axis=1).argmin()]
        root_int = tuple(nearest.tolist())
    for comp in comps:
        if root_int in comp:
            return np.asarray(sorted(comp), dtype=np.int32)
    largest = max(comps, key=len)
    return np.asarray(sorted(largest), dtype=np.int32)


def occupancy_with_root_stats(coords: np.ndarray, root: np.ndarray) -> dict:
    coords = np.unique(np.asarray(coords, dtype=np.int32), axis=0)
    if len(coords) == 0:
        return {
            "occupied_voxels": 0,
            "occupancy_component_count_6n": 0,
            "largest_occupancy_component_ratio_6n": 0.0,
            "root_component_ratio": 0.0,
            "orphan_mass_ratio": 0.0,
        }
    comps = component_sizes(coords)
    sizes = [len(c) for c in comps]
    root_comp = root_component_coords(coords, root)
    root_ratio = float(len(root_comp) / max(len(coords), 1))
    return {
        "occupied_voxels": int(len(coords)),
        "occupancy_component_count_6n": int(len(comps)),
        "largest_occupancy_component_ratio_6n": float(max(sizes) / max(len(coords), 1)),
        "root_component_ratio": root_ratio,
        "orphan_mass_ratio": float(1.0 - root_ratio),
    }


def graph_metrics(nodes: list[np.ndarray], parents: list[int]) -> dict:
    depths = graph_depths(parents)
    children = child_counts(parents)
    lengths = [float(np.linalg.norm(nodes[i] - nodes[p])) for i, p in enumerate(parents) if p >= 0]
    reachable = set()
    q = deque([0])
    child_map: dict[int, list[int]] = {i: [] for i in range(len(nodes))}
    for i, parent in enumerate(parents):
        if parent >= 0:
            child_map[parent].append(i)
    while q:
        node = q.popleft()
        if node in reachable:
            continue
        reachable.add(node)
        q.extend(child_map[node])
    tips = sum(1 for idx, count in enumerate(children) if idx != 0 and count == 0)
    orphan_tips = sum(1 for idx, count in enumerate(children) if idx not in reachable and count == 0)
    return {
        "nodes": int(len(nodes)),
        "segments": int(max(len(nodes) - 1, 0)),
        "tips": int(tips),
        "branch_nodes": int(sum(1 for c in children if c >= 2)),
        "graph_max_depth": int(max(depths) if depths else 0),
        "total_length": float(np.sum(lengths)) if lengths else 0.0,
        "mean_segment_length": float(np.mean(lengths)) if lengths else 0.0,
        "path_to_root_rate": float(len(reachable) / max(len(nodes), 1)),
        "orphan_tip_count": int(orphan_tips),
    }


def build_case_method(case: str, method: str, depth: int, seed: int, quick: bool) -> tuple[list[np.ndarray], list[int], np.ndarray, float]:
    if method == "lsystem":
        nodes, parents = lsystem_case(case, depth, seed)
        return nodes, parents, skeleton_to_coords(nodes, parents, case, method), 1.0
    if method == "space_colonization":
        nodes, parents = space_colonization_case(case, depth, seed, quick)
        return nodes, parents, skeleton_to_coords(nodes, parents, case, method), 1.0
    if method == "proposed_connected":
        return proposed_case(case, depth, seed)
    raise ValueError(f"unknown method: {method}")


def write_rows(out_dir: Path, rows: list[dict]) -> None:
    fields = [
        "case",
        "method",
        "depth",
        "same_root_anchor",
        "same_seed",
        "same_max_depth",
        "obj_path",
        "render_group",
        "vertices",
        "faces",
        "mesh_component_count",
        "largest_mesh_component_vertex_ratio",
        "occupied_voxels",
        "occupancy_component_count_6n",
        "largest_occupancy_component_ratio_6n",
        "root_component_ratio",
        "orphan_mass_ratio",
        "nodes",
        "segments",
        "tips",
        "branch_nodes",
        "graph_max_depth",
        "total_length",
        "mean_segment_length",
        "path_to_root_rate",
        "orphan_tip_count",
        "projection_survival_ratio",
        "fairness_note",
    ]
    with (out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})
    (out_dir / "metrics.json").write_text(json.dumps({"rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")


def render_final_contact_sheet(out_dir: Path, final_rows: list[dict]) -> Path:
    contact = out_dir / "contact_sheet_final_depth.png"
    renderer = ASSET_DIR / "render_mesh_contact_sheet.py"
    cmd = [
        sys.executable,
        str(renderer),
        "--out",
        str(contact),
        "--views",
        "iso",
        "front",
        "side",
        "--max-faces",
        "65000",
    ]
    for row in final_rows:
        label = f"{row['case']}_{row['method']}"
        cmd.extend(["--case", f"{label}={row['obj_path']}"])
    subprocess.run(cmd, check=True)
    return contact


def write_doc(doc_path: Path, out_dir: Path, rows: list[dict], final_rows: list[dict], contact: Path, seed: int, max_depth: int) -> None:
    final_table = "\n".join(
        "| {case} | {method} | {occ} | {lcr:.4f} | {root:.4f} | {tips} | {branches} | {mesh} |".format(
            case=r["case"],
            method=r["method"],
            occ=int(r["occupancy_component_count_6n"]),
            lcr=float(r["largest_occupancy_component_ratio_6n"]),
            root=float(r["root_component_ratio"]),
            tips=int(r["tips"]),
            branches=int(r["branch_nodes"]),
            mesh=int(r["mesh_component_count"]),
        )
        for r in final_rows
    )
    proposed = [r for r in final_rows if r["method"] == "proposed_connected"]
    trad = [r for r in final_rows if r["method"] in {"lsystem", "space_colonization"}]
    prop_occ = ", ".join(f"{r['case']}={int(r['occupancy_component_count_6n'])}/{float(r['root_component_ratio']):.3f}" for r in proposed)
    trad_occ = ", ".join(f"{r['case']}:{r['method']}={int(r['occupancy_component_count_6n'])}/{float(r['root_component_ratio']):.3f}" for r in trad)
    text = f"""# Same-root / same-depth baseline matrix 20260509

范围：本地 CPU 第一版；没有 SSH、远端或 GPU；没有修改 `paper_siga/main.tex`。

输出目录：`{out_dir}`

Contact sheet：`{contact}`

## 协议

- Cases：`tree`, `root`, `vine`。
- Methods：传统 `lsystem`、传统 `space_colonization`、`proposed_connected` projection-positive scaffold。
- Same-root：每个 case/method/depth 都从 `(0, 0, 0)` root anchor 出发。
- Same-seed：`{seed}`，脚本内部只加固定 case/method offset，避免 Python hash 随进程漂移。
- Same-depth：`1..{max_depth}`；CSV 每行都记录 `same_max_depth={max_depth}`。
- Same renderer：最终深度全部用同一个 mesh renderer 生成 `contact_sheet_final_depth.png`，不是点云 scatter。

## 最终深度指标

| case | method | occ comp 6N | occ LCR | root ratio | tips | branch nodes | mesh comps |
|---|---|---:|---:|---:|---:|---:|---:|
{final_table}

## 第一版结论

- `proposed_connected` 在三个 case 的最终深度保持 root-attached occupancy：{prop_occ}。
- 传统 L-system 和 space-colonization 这版也通过 skeleton-to-voxel tube 输出 mesh，因此不应用连通性指标把它们简单判负：{trad_occ}。
- 当前最有信息量的差异不是“是否连通”，而是结构复杂度和控制方式：L-system 给出规则化分叉，space-colonization 给出吸引子覆盖，proposed_connected 给出每层 projection-positive 的 root-attached 支撑。

## Fairness 限制

1. 这是 structure-first CPU mesh matrix，不经过 Trellis2 texture/GLB，因此不能回答材质一致性或生成模型外观质量。
2. 传统 baseline 由 skeleton 转 occupancy tube mesh，避免用未焊接 cylinder face components 不公平惩罚传统方法；相应地，它们的连通性会偏乐观。
3. `proposed_connected` 是本地 connected scaffold/projection-positive 代理，不是完整 sparse latent decode-project-encode 管线。
4. Space-colonization 的递归 depth 用 iteration budget 对齐，不等同于 grammar derivation depth；CSV 同时报 `graph_max_depth` 以暴露这个不完全公平点。
5. 本版 contact sheet 只渲染最终深度；每层 OBJ 和 metrics 已保存，后续需要补 front/top/zoom QA。

## 下一步缺口

- 加入 direct sparse grammar、final-only projection、prune-per-depth、bridge-per-depth 列，形成文档中要求的四列/六列闭环。
- 对 tree/root/vine 增加 root attachment、junction、tip zoom 的 Blender/Cycles 或同等 mesh render。
- 增加 proposed 的真实 sparse latent/Trellis2 本地可复现实验入口；当前只是 scaffold/projection-positive proxy。
- 补 coverage/collision metrics，让 space-colonization 的传统优势能被公平记录。
"""
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(text, encoding="utf-8")


def generate_matrix(
    out_dir: Path,
    max_depth: int = 4,
    seed: int = 20260509,
    quick: bool = False,
    doc_path: Path | None = None,
) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    root_anchor = np.zeros(3, dtype=float)
    for case in CASES:
        for method in METHODS:
            for depth in range(1, max_depth + 1):
                nodes, parents, coords, survival = build_case_method(case, method, depth, seed, quick)
                mesh = scaffold.coords_to_mesh(coords)
                case_dir = out_dir / case / method / f"depth_{depth:02d}"
                case_dir.mkdir(parents=True, exist_ok=True)
                obj_path = case_dir / f"{case}_{method}_depth_{depth:02d}.obj"
                mesh.export(obj_path)
                row = {
                    "case": case,
                    "method": method,
                    "depth": int(depth),
                    "same_root_anchor": "0,0,0",
                    "same_seed": int(seed),
                    "same_max_depth": int(max_depth),
                    "obj_path": str(obj_path),
                    "render_group": "final_depth_contact_sheet" if depth == max_depth else "per_depth_mesh_saved",
                    "projection_survival_ratio": float(survival),
                    "fairness_note": "same root/depth/seed; SC depth is iteration-budget matched; proposed is connected scaffold proxy",
                }
                row.update(scaffold.mesh_stats(mesh))
                row.update(occupancy_with_root_stats(coords, root_anchor))
                row.update(graph_metrics(nodes, parents))
                rows.append(row)
    write_rows(out_dir, rows)
    final_rows = [r for r in rows if int(r["depth"]) == max_depth]
    contact = render_final_contact_sheet(out_dir, final_rows)
    summary = {
        "out_dir": str(out_dir),
        "metrics_csv": str(out_dir / "metrics.csv"),
        "metrics_json": str(out_dir / "metrics.json"),
        "contact_sheet": str(contact),
        "seed": seed,
        "max_depth": max_depth,
        "quick": quick,
        "rows": rows,
        "final_rows": final_rows,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    if doc_path is not None:
        write_doc(doc_path, out_dir, rows, final_rows, contact, seed, max_depth)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260509)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    args = parser.parse_args()
    summary = generate_matrix(args.out, max_depth=args.max_depth, seed=args.seed, quick=args.quick, doc_path=args.doc)
    print(
        json.dumps(
            {
                "out_dir": summary["out_dir"],
                "metrics_csv": summary["metrics_csv"],
                "contact_sheet": summary["contact_sheet"],
                "doc": str(args.doc),
                "rows": len(summary["rows"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
