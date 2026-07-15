#!/usr/bin/env python3
"""V33 SC-tree fused-veil seam naturalization inputs.

V28 recovered the post-GLB connectivity floor, but the rendered asset still
read as one long support rod inserted into a crown.  V29 removed that rod with
hidden multi-stem hubs, and V30 shortened the exterior support segments, but
the resulting GLB still reads as a sparse branch lattice with small fragments.
V32 improved the branch/crown read with many leaf-mass clusters, but Trellis2
post-GLB r0 connectivity regressed because thin leaves and rods survived as
small islands.  V33 keeps the hidden short-hub support and replaces most thin
leaf clusters with fewer, thicker fused lobes attached to shared support
vertices.

This is intentionally claim-bounded.  The image guide is a whole-object
Trellis2 texture guide; there is no 2D seam-inpaint backprojection claim.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ASSET_DIR = Path(__file__).resolve().parent
ROOT_DIR = ASSET_DIR.parent
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import baseline_matrix_20260509 as bm
import procedural_baselines as pb
import space_colonization_baseline as scb
import strict_visual_matched_cases_V22_botanical_smooth_20260510 as v22
import strict_visual_matched_cases_V23_all_family_20260510 as v23
import strict_visual_matched_cases_V26_sc_tree_seam_naturalization_20260511 as v26
import strict_visual_matched_cases_V27_sc_tree_organic_seam_20260511 as v27
import strict_visual_matched_cases_V28_sc_tree_flare_bark_naturalization_20260511 as v28


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 200
CONNECTIVITY_LCR_MIN = 0.999
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V33_sc_tree_fused_veil_naturalization_20260511_dryrun"

SURFACE_STRATEGY = "v33_sc_tree_fused_veil_masked_naturalization"
GENERATION_POLICY = "generate_new_on_a100_2_no_local_selection_or_postprocessing"
SELECTION_BUDGET = "four_predeclared_sc_tree_fused_veil_candidates_one_per_gpu"
MESH_PBR_POLICY = "obj_inputs_fused_veil_transition_guides_for_trellis2_glb_export_no_2d_backprojection_claim"
EXTERNAL_SUPPORT_MAX_SEGMENT_GATE = 0.145


DetailCounts = Dict[str, int]


def _blank_counts() -> DetailCounts:
    return {
        "needle_count": 0,
        "leaf_count": 0,
        "rootlet_count": 0,
        "tendril_count": 0,
        "bud_count": 0,
        "flare_count": 0,
        "ridge_count": 0,
        "split_count": 0,
        "entry_sheath_count": 0,
    }


def _merge_counts(*parts: DetailCounts) -> DetailCounts:
    out = _blank_counts()
    for part in parts:
        for key, value in part.items():
            out[key] = int(out.get(key, 0)) + int(value)
    return out


def _graph_depths(parents: List[int]) -> List[int]:
    return bm.graph_depths(parents)


def _angle_bucket(point: np.ndarray, center: np.ndarray, buckets: int) -> int:
    angle = math.atan2(float(point[1] - center[1]), float(point[0] - center[0]))
    bucket = int(math.floor(((angle + math.pi) / math.tau) * buckets)) % buckets
    return bucket


def _subdivide_long_support_edges(
    nodes: List[np.ndarray],
    parents: List[int],
    *,
    max_segment: float,
) -> Tuple[List[np.ndarray], List[int], Dict]:
    """Insert shared-vertex intermediate nodes so low-level supports stay short."""

    new_nodes: List[np.ndarray] = []
    new_parents: List[int] = []
    old_to_new: Dict[int, int] = {}
    inserted = 0
    for old_idx, point in enumerate(nodes):
        parent = int(parents[old_idx])
        if parent < 0:
            old_to_new[old_idx] = len(new_nodes)
            new_nodes.append(np.asarray(point, dtype=float).copy())
            new_parents.append(-1)
            continue
        parent_new = old_to_new[parent]
        parent_pos = np.asarray(new_nodes[parent_new], dtype=float)
        child_pos = np.asarray(point, dtype=float)
        dist = float(np.linalg.norm(child_pos - parent_pos))
        segments = max(1, int(math.ceil(dist / max(float(max_segment), 1e-6))))
        last_parent = parent_new
        for s in range(1, segments):
            t = s / float(segments)
            interp = parent_pos * (1.0 - t) + child_pos * t
            new_nodes.append(interp)
            new_parents.append(last_parent)
            last_parent = len(new_nodes) - 1
            inserted += 1
        old_to_new[old_idx] = len(new_nodes)
        new_nodes.append(child_pos.copy())
        new_parents.append(last_parent)

    seg_lengths = [
        float(np.linalg.norm(new_nodes[idx] - new_nodes[parent]))
        for idx, parent in enumerate(new_parents)
        if parent >= 0
    ]
    return new_nodes, new_parents, {
        "short_hub_subdivision_enabled": True,
        "short_hub_max_segment_gate": float(max_segment),
        "short_hub_inserted_support_nodes": int(inserted),
        "external_support_max_segment_after_subdivision": float(max(seg_lengths) if seg_lengths else 0.0),
        "external_support_mean_segment_after_subdivision": float(np.mean(seg_lengths) if seg_lengths else 0.0),
    }


def _reroot_as_hidden_multistem(
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    cut_depth: int,
    hub_count: int,
    fork_spread: float,
    entry_lift: float,
) -> Tuple[List[np.ndarray], List[int], Dict]:
    """Remove the visible low-depth rod and replace it with short hidden hubs."""

    depths = _graph_depths(parents)
    keep = [idx for idx, depth in enumerate(depths) if depth >= int(cut_depth)]
    if not keep:
        return nodes, parents, {
            "hidden_trunk_cut_depth": int(cut_depth),
            "hidden_trunk_hub_count": 0,
            "entry_frontier_count": 0,
            "external_support_max_segment": 0.0,
            "external_support_mean_segment": 0.0,
        }

    frontier = [idx for idx in keep if int(parents[idx]) < 0 or depths[int(parents[idx])] < int(cut_depth)]
    arr = np.asarray([nodes[idx] for idx in keep], dtype=float)
    frontier_arr = np.asarray([nodes[idx] for idx in frontier], dtype=float) if frontier else arr
    center_xy = frontier_arr[:, :2].mean(axis=0)
    z_low = float(np.quantile(arr[:, 2], 0.13))
    root = np.array([float(center_xy[0]), float(center_xy[1]), z_low - 0.018], dtype=float)

    new_nodes: List[np.ndarray] = [root]
    new_parents: List[int] = [-1]
    hub_indices: List[int] = []
    for hub in range(int(hub_count)):
        angle = math.tau * hub / max(int(hub_count), 1) + float(rng.uniform(-0.20, 0.20))
        radial = float(fork_spread) * float(rng.uniform(0.72, 1.16))
        z = float(entry_lift) * float(rng.uniform(0.72, 1.18))
        pos = root + np.array([math.cos(angle) * radial, math.sin(angle) * radial, z], dtype=float)
        new_nodes.append(pos)
        new_parents.append(0)
        hub_indices.append(len(new_nodes) - 1)

    old_to_new: Dict[int, int] = {}
    ordered_keep = sorted(keep, key=lambda idx: (depths[idx], idx))
    for old_idx in ordered_keep:
        old = np.asarray(nodes[old_idx], dtype=float).copy()
        if old_idx in frontier:
            bucket = _angle_bucket(old, root, max(int(hub_count), 1))
            parent = hub_indices[bucket % len(hub_indices)]
            hub_pos = new_nodes[parent]
            # Pull the first retained nodes slightly inward so the entry is a
            # forked crown base rather than a long exterior support.
            old = hub_pos * 0.23 + old * 0.77
            old[2] += float(rng.uniform(-0.012, 0.028))
        else:
            old_parent = int(parents[old_idx])
            parent = old_to_new.get(old_parent)
            if parent is None:
                bucket = _angle_bucket(old, root, max(int(hub_count), 1))
                parent = hub_indices[bucket % len(hub_indices)]
        if depths[old_idx] <= int(cut_depth) + 3:
            # Mild nonuniform bend for the formerly straight low-level chain.
            u = np.asarray(old, dtype=float) - root
            side = np.array([-u[1], u[0], 0.0], dtype=float)
            side_norm = float(np.linalg.norm(side))
            if side_norm > 1e-8:
                old += side / side_norm * float(rng.uniform(-0.025, 0.025))
        old_to_new[old_idx] = len(new_nodes)
        new_nodes.append(old)
        new_parents.append(int(parent))

    segments = []
    for idx, parent in enumerate(new_parents):
        if parent >= 0:
            segments.append(float(np.linalg.norm(new_nodes[idx] - new_nodes[parent])))
    diagnostics = {
        "hidden_trunk_cut_depth": int(cut_depth),
        "hidden_trunk_hub_count": int(hub_count),
        "entry_frontier_count": int(len(frontier)),
        "external_support_strategy": "low_depth_trunk_rerooted_into_short_occluded_multistem_hubs",
        "external_support_max_segment": float(max(segments) if segments else 0.0),
        "external_support_mean_segment": float(np.mean(segments) if segments else 0.0),
        "removed_visible_low_depth_rod": True,
    }
    return new_nodes, new_parents, diagnostics


def _organic_radii(
    parents: List[int],
    *,
    base: float,
    taper: float,
    floor: float,
    terminal_shrink: float,
    hub_count: int,
) -> List[float]:
    depths = _graph_depths(parents)
    max_depth = max(depths) if depths else 1
    terminals = set(v27._terminal_nodes(parents))
    radii: List[float] = []
    for idx, depth in enumerate(depths):
        t = depth / max(float(max_depth), 1.0)
        radius = max(float(floor), float(base) * (float(taper) ** (depth * 0.72)))
        radius *= 1.0 - 0.28 * max(t - 0.22, 0.0)
        if idx == 0:
            radius *= 0.84
        elif 1 <= idx <= int(hub_count):
            radius *= 0.78
        if idx in terminals:
            radius *= float(terminal_shrink)
        radii.append(float(max(radius, floor)))
    return radii


def _entry_anchor_indices(parents: List[int], count: int, hub_count: int) -> List[int]:
    child_map = v22._children(parents)
    candidates: List[int] = []
    for hub_idx in range(1, int(hub_count) + 1):
        candidates.append(hub_idx)
        candidates.extend(child_map.get(hub_idx, [])[:8])
    if not candidates:
        candidates = v28._junction_anchor_indices([], parents, count)
    candidates = [idx for idx in candidates if 0 <= idx < len(parents)]
    if not candidates:
        candidates = list(range(1, min(len(parents), int(count) + 1))) or [0]
    return [candidates[(i * 3) % len(candidates)] for i in range(int(count))]


def _add_entry_sheaths(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    count: int,
    hub_count: int,
    radius_scale: float,
    bracts_per_anchor: int,
) -> Tuple[DetailCounts, Dict]:
    centers = getattr(mesh, "center_indices")
    anchors = _entry_anchor_indices(parents, count, hub_count)
    counts = _blank_counts()
    seam_centers: List[List[float]] = []
    for k, idx in enumerate(anchors):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx) if idx > 0 else np.array([0.0, 0.0, 1.0])
        u, v, _w = v22._basis(axis)
        lateral = math.cos(k * 2.237) * u + math.sin(k * 2.237) * v
        direction = v22._unit(0.34 * axis + 0.56 * lateral + np.array([0.0, 0.0, 0.11]) + rng.normal(0.0, 0.028, 3))
        center = v26._add_transition_lobe(
            mesh,
            centers[idx],
            anchor,
            direction,
            float(rng.uniform(0.070, 0.132)),
            float(rng.uniform(0.010, 0.019)) * float(radius_scale),
            rng,
            rings=4,
            sides=10,
            curl=float(rng.uniform(0.08, 0.18)),
        )
        counts["entry_sheath_count"] += 1
        counts["tendril_count"] += 1
        seam_centers.append([float(x) for x in center])
        for b in range(int(bracts_per_anchor)):
            phase = k * 1.917 + b * math.tau / max(int(bracts_per_anchor), 1)
            side = math.cos(phase) * u + math.sin(phase) * v
            leaf_dir = v22._unit(0.32 * direction + 0.74 * side + np.array([0.0, 0.0, 0.08]))
            length = float(rng.uniform(0.034, 0.070))
            v22._add_lanceolate_leaf(
                mesh,
                centers[idx],
                anchor,
                leaf_dir,
                length,
                length * float(rng.uniform(0.22, 0.38)),
                rng,
                rows=5,
            )
            counts["leaf_count"] += 1
    return counts, {
        "entry_sheath_count": int(counts["entry_sheath_count"]),
        "entry_sheath_leaf_count": int(counts["leaf_count"]),
        "entry_mask_anchor_count": int(len(set(anchors))),
        "entry_mask_centers": seam_centers[:80],
    }


def _add_occlusion_shell(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    count: int,
    hub_count: int,
    radius_scale: float,
) -> Tuple[DetailCounts, Dict]:
    """Attach broad, low-detail volumetric lobes around the hub/crown transition."""

    centers = getattr(mesh, "center_indices")
    anchors = _entry_anchor_indices(parents, count, hub_count)
    counts = _blank_counts()
    shell_centers: List[List[float]] = []
    for k, idx in enumerate(anchors):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx) if idx > 0 else np.array([0.0, 0.0, 1.0])
        u, v, _w = v22._basis(axis)
        phase = k * 2.399
        side = math.cos(phase) * u + math.sin(phase) * v
        direction = v22._unit(0.18 * axis + 0.84 * side + np.array([0.0, 0.0, 0.10]) + rng.normal(0.0, 0.022, 3))
        length = float(rng.uniform(0.070, 0.118)) * float(radius_scale)
        radius_lobe = length * float(rng.uniform(0.18, 0.32))
        center = v26._add_transition_lobe(
            mesh,
            centers[idx],
            anchor,
            direction,
            length,
            radius_lobe,
            rng,
            rings=4,
            sides=12,
            curl=float(rng.uniform(0.04, 0.11)),
        )
        counts["flare_count"] += 1
        counts["tendril_count"] += 1
        shell_centers.append([float(x) for x in center])
        if k % 3 == 0:
            lobe_dir = v22._unit(0.40 * direction + 0.32 * axis + rng.normal(0.0, 0.016, 3))
            extra_center = v26._add_transition_lobe(
                mesh,
                centers[idx],
                anchor,
                lobe_dir,
                float(rng.uniform(0.052, 0.086)) * float(radius_scale),
                float(rng.uniform(0.014, 0.024)) * float(radius_scale),
                rng,
                rings=4,
                sides=10,
                curl=float(rng.uniform(0.05, 0.12)),
            )
            counts["flare_count"] += 1
            counts["tendril_count"] += 1
            shell_centers.append([float(x) for x in extra_center])
    return counts, {
        "occlusion_shell_lobe_count": int(counts["flare_count"]),
        "occlusion_shell_anchor_count": int(len(set(anchors))),
        "occlusion_shell_centers": shell_centers[:80],
    }


def _support_visibility_indices(parents: List[int], hub_count: int) -> set[int]:
    depths = _graph_depths(parents)
    max_depth = max(depths) if depths else 1
    terminals = set(v27._terminal_nodes(parents))
    visible: set[int] = set(range(0, min(len(parents), int(hub_count) + 1)))
    for idx in range(1, len(parents)):
        t = depths[idx] / max(float(max_depth), 1.0)
        if t <= 0.58 and idx not in terminals:
            visible.add(idx)
        elif t <= 0.44:
            visible.add(idx)
    return visible


def _fused_veil_radii(
    parents: List[int],
    *,
    base: float,
    taper: float,
    floor: float,
    terminal_shrink: float,
    hub_count: int,
    support_visibility_fraction: float,
) -> List[float]:
    radii = _organic_radii(
        parents,
        base=base,
        taper=taper,
        floor=floor,
        terminal_shrink=terminal_shrink,
        hub_count=hub_count,
    )
    depths = _graph_depths(parents)
    max_depth = max(depths) if depths else 1
    terminals = set(v27._terminal_nodes(parents))
    for idx in range(len(radii)):
        t = depths[idx] / max(float(max_depth), 1.0)
        if idx in terminals or t >= 0.62:
            radii[idx] = max(float(floor) * 0.42, radii[idx] * float(support_visibility_fraction))
        elif t >= 0.48:
            fade = (t - 0.48) / max(0.62 - 0.48, 1e-6)
            radii[idx] = max(float(floor) * 0.55, radii[idx] * (1.0 - fade * (1.0 - support_visibility_fraction)))
    return [float(r) for r in radii]


def _canopy_anchor_indices(nodes: List[np.ndarray], parents: List[int], count: int, hub_count: int) -> List[int]:
    depths = _graph_depths(parents)
    max_depth = max(depths) if depths else 1
    child_map = v22._children(parents)
    scored: List[Tuple[float, int]] = []
    for idx in range(1, len(parents)):
        t = depths[idx] / max(float(max_depth), 1.0)
        if t < 0.26 or t > 0.84:
            continue
        degree = len(child_map.get(idx, []))
        xy = math.hypot(float(nodes[idx][0]), float(nodes[idx][1]))
        score = 1.8 * (1.0 - abs(t - 0.56)) + 0.45 * degree + 0.14 * xy + 0.0007 * idx
        if idx <= int(hub_count):
            score += 0.65
        scored.append((score, idx))
    if not scored:
        return _entry_anchor_indices(parents, count, hub_count)
    ordered = [idx for _score, idx in sorted(scored, reverse=True)]
    return [ordered[(i * 5) % len(ordered)] for i in range(int(count))]


def _add_fused_lobe_cluster(
    mesh: pb.Mesh,
    anchor_idx: int,
    anchor: np.ndarray,
    axis: np.ndarray,
    rng: np.random.Generator,
    *,
    radius: float,
    lobes: int,
    length_range: Tuple[float, float],
    width_scale: Tuple[float, float],
) -> Tuple[int, List[List[float]]]:
    u, v, _w = v22._basis(axis)
    centers: List[List[float]] = []
    for lobe_i in range(int(lobes)):
        phase = float(rng.uniform(0.0, math.tau)) + lobe_i * math.tau / max(int(lobes), 1)
        side = math.cos(phase) * u + math.sin(phase) * v
        lift = np.array([0.0, 0.0, float(rng.uniform(0.05, 0.22))])
        base = np.asarray(anchor, dtype=float) + side * float(radius) * float(rng.uniform(0.25, 0.82)) + lift * float(radius)
        direction = v22._unit(0.24 * axis + 0.84 * side + np.array([0.0, 0.0, 0.24]) + rng.normal(0.0, 0.040, 3))
        length = float(rng.uniform(*length_range))
        radius_lobe = length * float(rng.uniform(*width_scale))
        center = v26._add_transition_lobe(
            mesh,
            anchor_idx,
            base,
            direction,
            length,
            radius_lobe,
            rng,
            rings=4,
            sides=12,
            curl=float(rng.uniform(0.04, 0.11)),
        )
        centers.append([float(x) for x in center])
        centers.append([float(x) for x in base])
    return int(lobes), centers


def _add_fused_veil_pads(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    count: int,
    hub_count: int,
    radius_scale: float,
) -> Tuple[DetailCounts, Dict]:
    """Add thick, attached crown pads and fused lobes over visible entry supports."""

    centers = getattr(mesh, "center_indices")
    anchors = _entry_anchor_indices(parents, count, hub_count)
    counts = _blank_counts()
    pad_centers: List[List[float]] = []
    for k, idx in enumerate(anchors):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx) if idx > 0 else np.array([0.0, 0.0, 1.0])
        u, v, _w = v22._basis(axis)
        phase = k * 2.017
        side = math.cos(phase) * u + math.sin(phase) * v
        outward = v22._unit(0.28 * axis + 0.76 * side + np.array([0.0, 0.0, 0.12]) + rng.normal(0.0, 0.018, 3))
        center = v26._add_transition_lobe(
            mesh,
            centers[idx],
            anchor,
            outward,
            float(rng.uniform(0.092, 0.154)),
            float(rng.uniform(0.024, 0.042)) * float(radius_scale),
            rng,
            rings=6,
            sides=14,
            curl=float(rng.uniform(0.04, 0.10)),
        )
        counts["flare_count"] += 1
        counts["tendril_count"] += 1
        pad_centers.append([float(x) for x in center])
        lobe_count, lobe_centers = _add_fused_lobe_cluster(
            mesh,
            centers[idx],
            anchor,
            outward,
            rng,
            radius=float(rng.uniform(0.034, 0.060)) * float(radius_scale),
            lobes=1 + int(k % 4 == 0),
            length_range=(0.082 * float(radius_scale), 0.142 * float(radius_scale)),
            width_scale=(0.18, 0.30),
        )
        counts["bud_count"] += lobe_count
        counts["tendril_count"] += lobe_count
        pad_centers.extend(lobe_centers)
    return counts, {
        "fused_veil_pad_count": int(counts["flare_count"]),
        "fused_veil_pad_lobe_count": int(counts["bud_count"]),
        "fused_veil_pad_anchor_count": int(len(set(anchors))),
        "fused_veil_pad_centers": pad_centers[:80],
    }


def _add_mid_fused_veil(
    mesh: pb.Mesh,
    nodes: List[np.ndarray],
    parents: List[int],
    rng: np.random.Generator,
    *,
    count: int,
    hub_count: int,
    radius_scale: float,
) -> Tuple[DetailCounts, Dict]:
    centers = getattr(mesh, "center_indices")
    anchors = _canopy_anchor_indices(nodes, parents, count, hub_count)
    counts = _blank_counts()
    veil_centers: List[List[float]] = []
    for k, idx in enumerate(anchors):
        anchor = np.asarray(nodes[idx], dtype=float)
        axis = v22._node_axis(nodes, parents, idx)
        u, v, _w = v22._basis(axis)
        side = math.cos(k * 2.271) * u + math.sin(k * 2.271) * v
        outward = v22._unit(0.12 * axis + 0.88 * side + np.array([0.0, 0.0, 0.18]) + rng.normal(0.0, 0.026, 3))
        lobe_center = v26._add_transition_lobe(
            mesh,
            centers[idx],
            anchor,
            outward,
            float(rng.uniform(0.072, 0.126)) * float(radius_scale),
            float(rng.uniform(0.016, 0.028)) * float(radius_scale),
            rng,
            rings=4,
            sides=12,
            curl=float(rng.uniform(0.06, 0.14)),
        )
        counts["flare_count"] += 1
        counts["tendril_count"] += 1
        veil_centers.append([float(x) for x in lobe_center])
        lobe_count, lobe_centers = _add_fused_lobe_cluster(
            mesh,
            centers[idx],
            anchor,
            outward,
            rng,
            radius=float(rng.uniform(0.030, 0.052)) * float(radius_scale),
            lobes=1 + int(k % 5 == 0),
            length_range=(0.066 * float(radius_scale), 0.122 * float(radius_scale)),
            width_scale=(0.16, 0.28),
        )
        counts["bud_count"] += lobe_count
        counts["tendril_count"] += lobe_count
        veil_centers.extend(lobe_centers)
    return counts, {
        "mid_fused_veil_count": int(counts["flare_count"]),
        "mid_fused_veil_lobe_count": int(counts["bud_count"]),
        "mid_fused_veil_anchor_count": int(len(set(anchors))),
        "mid_fused_veil_centers": veil_centers[:96],
    }


def _draw_hidden_tree_guide(path: Path, *, variant: str) -> None:
    rng = np.random.default_rng(v26._stable_seed(path.stem))
    palettes = {
        "multistem": [(58, 48, 32), (84, 66, 42), (102, 94, 54), (62, 108, 54), (92, 132, 70)],
        "occlusion": [(54, 45, 30), (84, 68, 42), (76, 116, 58), (110, 144, 78), (146, 154, 90)],
        "braided": [(48, 38, 25), (74, 54, 34), (112, 82, 48), (70, 102, 48), (110, 132, 72)],
        "softleaf": [(60, 50, 34), (92, 70, 44), (66, 114, 56), (118, 152, 82), (156, 164, 98)],
    }
    colors = palettes[variant]
    img = Image.new("RGB", (768, 768), (46, 58, 38))
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(112):
        color = colors[int(rng.integers(0, len(colors)))]
        x = int(rng.integers(-140, 900))
        y = int(rng.integers(-140, 900))
        r = int(rng.integers(80, 230))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, int(rng.integers(48, 98))))
    img = img.filter(ImageFilter.GaussianBlur(radius=19))
    draw = ImageDraw.Draw(img, "RGBA")
    # Short forked bark strokes, deliberately without a single long straight rod.
    for _ in range(92):
        base = np.array([rng.integers(70, 700), rng.integers(130, 690)], dtype=float)
        color = colors[int(rng.integers(0, 3))]
        branch_len = float(rng.uniform(36, 118))
        angle = float(rng.uniform(-2.55, -0.58))
        pts = []
        for t in np.linspace(0.0, 1.0, 5):
            curve = math.sin(t * math.pi) * rng.uniform(-18, 18)
            p = base + np.array([math.cos(angle) * branch_len * t + curve, math.sin(angle) * branch_len * t], dtype=float)
            pts.append((int(p[0]), int(p[1])))
        draw.line(pts, fill=(*color, int(rng.integers(78, 145))), width=int(rng.integers(2, 5)))
        if rng.random() < 0.42:
            fork = pts[int(rng.integers(1, len(pts)))]
            side = float(angle + rng.choice([-1.0, 1.0]) * rng.uniform(0.45, 0.95))
            end = (int(fork[0] + math.cos(side) * branch_len * 0.38), int(fork[1] + math.sin(side) * branch_len * 0.38))
            draw.line((fork, end), fill=(*color, int(rng.integers(70, 130))), width=int(rng.integers(1, 4)))
    for _ in range(160):
        color = colors[int(rng.integers(3, len(colors)))]
        x = int(rng.integers(35, 735))
        y = int(rng.integers(35, 735))
        rx = int(rng.integers(6, 20))
        ry = int(rng.integers(4, 13))
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(*color, int(rng.integers(34, 76))))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.filter(ImageFilter.SMOOTH_MORE).save(path)


def _write_guides(out_dir: Path) -> Dict[str, str]:
    guide_dir = out_dir / "_guides"
    guides: Dict[str, str] = {}
    for key in ("multistem", "occlusion", "braided", "softleaf"):
        path = guide_dir / f"V33_sc_tree_{key}_fused_veil_lowcontrast_guide.png"
        _draw_hidden_tree_guide(path, variant=key)
        guides[key] = str(path)
    return guides


def _build_sc_tree_case(
    seed: int,
    *,
    attractors: int,
    iterations: int,
    influence: float,
    kill: float,
    step: float,
    z_gain: float,
    shrink: float,
    cut_depth: int,
    hub_count: int,
    fork_spread: float,
    entry_lift: float,
    base_radius: float,
    radius_taper: float,
    radius_floor: float,
    terminal_shrink: float,
    max_segment: float,
    entry_sheath_count: int,
    bracts_per_anchor: int,
    occlusion_shell_count: int,
    compact_pad_count: int,
    mid_veil_count: int,
    flare_count: int,
    ridge_count: int,
    split_count: int,
    bud_count: int,
    bracts_per_bud: int,
    scatter_leaf_count: int,
    scatter_needle_count: int,
    detail_radius_scale: float,
    flare_length_scale: float,
    support_visibility_fraction: float,
) -> Tuple[pb.Mesh, Dict, Dict]:
    rng = np.random.default_rng(seed + 2901)
    result = scb.grow_space_colonization(
        case="tree_canopy",
        attractor_count=attractors,
        iterations=iterations,
        influence_radius=influence,
        kill_radius=kill,
        step_size=step,
        seed=seed,
    )
    raw_nodes = v22._normalize_nodes([np.asarray(p, dtype=float) for p in result["nodes"]], 2.62)
    raw_nodes = v26._scale_nodes_for_crown(raw_nodes, z_gain=z_gain, radial_shrink_top=shrink)
    raw_parents = [int(p) for p in result["parents"]]
    nodes, parents, reroot_diag = _reroot_as_hidden_multistem(
        raw_nodes,
        raw_parents,
        rng,
        cut_depth=cut_depth,
        hub_count=hub_count,
        fork_spread=fork_spread,
        entry_lift=entry_lift,
    )
    nodes, parents, subdiv_diag = _subdivide_long_support_edges(
        nodes,
        parents,
        max_segment=max_segment,
    )
    radii = _fused_veil_radii(
        parents,
        base=base_radius,
        taper=radius_taper,
        floor=radius_floor,
        terminal_shrink=terminal_shrink,
        hub_count=hub_count,
        support_visibility_fraction=support_visibility_fraction,
    )
    edges = v22._graph_edges(parents)
    mesh = v22._smooth_support_mesh(nodes, edges, radii, sides=15, ovality=0.43)
    base_counts = _merge_counts(
        v22._scatter_needles(mesh, nodes, parents, rng, count=scatter_needle_count, length_range=(0.032, 0.064)),
        v22._scatter_leaves(mesh, nodes, parents, rng, count=scatter_leaf_count, scale=(0.036, 0.076)),
    )
    entry_counts, entry_diag = _add_entry_sheaths(
        mesh,
        nodes,
        parents,
        rng,
        count=entry_sheath_count,
        hub_count=hub_count,
        radius_scale=detail_radius_scale,
        bracts_per_anchor=bracts_per_anchor,
    )
    shell_counts, shell_diag = _add_occlusion_shell(
        mesh,
        nodes,
        parents,
        rng,
        count=occlusion_shell_count,
        hub_count=hub_count,
        radius_scale=detail_radius_scale,
    )
    pad_counts, pad_diag = _add_fused_veil_pads(
        mesh,
        nodes,
        parents,
        rng,
        count=compact_pad_count,
        hub_count=hub_count,
        radius_scale=detail_radius_scale,
    )
    veil_counts, veil_diag = _add_mid_fused_veil(
        mesh,
        nodes,
        parents,
        rng,
        count=mid_veil_count,
        hub_count=hub_count,
        radius_scale=detail_radius_scale,
    )
    flare_counts, flare_diag = v28._add_flare_sleeves(
        mesh,
        nodes,
        parents,
        rng,
        count=flare_count,
        radius_scale=detail_radius_scale,
        length_scale=flare_length_scale,
    )
    ridge_counts = v28._add_bark_ridges(mesh, nodes, parents, rng, count=ridge_count, radius_scale=detail_radius_scale)
    split_counts = v28._add_structural_splits(mesh, nodes, parents, rng, count=split_count, radius_scale=detail_radius_scale)
    bud_counts, bud_diag = v28._add_compact_terminal_buds(
        mesh,
        nodes,
        parents,
        rng,
        count=bud_count,
        bracts_per_bud=bracts_per_bud,
        radius_scale=detail_radius_scale,
    )
    counts = _merge_counts(base_counts, entry_counts, shell_counts, pad_counts, veil_counts, flare_counts, ridge_counts, split_counts, bud_counts)
    seam_centers = (
        list(entry_diag.get("entry_mask_centers", []))
        + list(shell_diag.get("occlusion_shell_centers", []))
        + list(pad_diag.get("fused_veil_pad_centers", []))
        + list(veil_diag.get("mid_fused_veil_centers", []))
        + list(flare_diag.get("seam_mask_centers", []))
    )
    semantic_detail_count = int(
        counts["needle_count"]
        + counts["leaf_count"]
        + counts["bud_count"]
        + counts["flare_count"]
        + counts["ridge_count"]
        + counts["split_count"]
        + counts["entry_sheath_count"]
    )
    controls = v22._finalize_controls(
        {
            "source": "space_colonization_baseline.grow_space_colonization",
            "case": "tree_canopy",
            "semantic_mode": "tree",
            "recursive_depth": int(max(result.get("depths", [0])) if result.get("depths") else 0),
            "target_silhouette": "space-colonization tree crown with compact crown-entry mass",
            "attractor_count": int(attractors),
            "iterations": int(iterations),
            "influence_radius": float(influence),
            "kill_radius": float(kill),
            "step_size": float(step),
            "covered_attractors": int(result.get("covered_attractors", 0)),
            "alive_attractors": int(result.get("alive_attractors", 0)),
            "z_gain": float(z_gain),
            "radial_shrink_top": float(shrink),
            "support_base_radius": float(base_radius),
            "support_radius_taper": float(radius_taper),
            "support_radius_floor": float(radius_floor),
            "terminal_radius_shrink": float(terminal_shrink),
            "support_visibility_fraction": float(support_visibility_fraction),
            "support_visibility_policy": "thin outer support below fused volumetric veil while keeping shared-vertex support graph",
            "support_cross_section": "thin_outer_support_plus_attached_fused_veil",
            "grammar_rule": "space-colonization growth rerooted as hidden crown-entry support, then masked fused veil naturalization",
            **reroot_diag,
            **subdiv_diag,
        },
        nodes,
        edges,
        {
            "needle_count": int(counts["needle_count"]),
            "leaf_count": int(counts["leaf_count"]),
            "rootlet_count": 0,
            "tendril_count": int(counts["tendril_count"]),
        },
    )
    controls.update(
        {
            "surface_strategy": SURFACE_STRATEGY,
            "semantic_detail_count": semantic_detail_count,
            "v33_sc_tree_fused_veil_naturalization": True,
            "v24_v31_failure_addressed": "visible branch/crown seam, smooth inserted rod, hard terminal cap, sparse branch lattice read, and post-GLB tiny fragments",
            "v33_base_from_v31": "V31 metric-improved compact-crown skeleton with outer support visually demoted under attached fused veils",
            "masked_local_naturalization_target": "fused veil branch/crown entry mass and terminal caps",
            "mask_scope": "object_space_fused_veil_entry_band_and_terminal_caps_only",
            "seam_mask_space": "object_xyz",
            "seam_mask_selection_rule": "short entry hubs plus fused veil pads, mid-canopy volumetric lobes, occlusion shell, and branch/crown junction flares; terminal caps tracked separately",
            "seam_mask_center_count": int(len(seam_centers)),
            "seam_mask_centers": seam_centers[:96],
            "seam_mask_radius": 0.126,
            "naturalization_regions": [
                "junction_band",
                "terminal_caps",
                "primary_branch_flare",
                "canopy_occlusion_shell",
            ],
            "entry_sheath_count": int(counts["entry_sheath_count"]),
            "occlusion_shell_lobe_count": int(shell_diag.get("occlusion_shell_lobe_count", 0)),
            "fused_veil_pad_count": int(pad_diag.get("fused_veil_pad_count", 0)),
            "fused_veil_pad_lobe_count": int(pad_diag.get("fused_veil_pad_lobe_count", 0)),
            "mid_fused_veil_count": int(veil_diag.get("mid_fused_veil_count", 0)),
            "mid_fused_veil_lobe_count": int(veil_diag.get("mid_fused_veil_lobe_count", 0)),
            "fused_veil_total_lobe_count": int(
                pad_diag.get("fused_veil_pad_lobe_count", 0)
                + veil_diag.get("mid_fused_veil_lobe_count", 0)
            ),
            "terminal_bud_count": int(bud_diag.get("terminal_bud_count", 0)),
            "junction_flare_count": int(counts["flare_count"]),
            "ridge_count": int(counts["ridge_count"]),
            "structural_split_count": int(counts["split_count"]),
            "external_support_max_segment_gate": float(EXTERNAL_SUPPORT_MAX_SEGMENT_GATE),
            "short_hub_gate_pass": bool(
                float(subdiv_diag.get("external_support_max_segment_after_subdivision", 999.0))
                <= EXTERNAL_SUPPORT_MAX_SEGMENT_GATE + 1e-6
            ),
            "naturalization_not_global_resampling": True,
            "image_generation_considered": True,
            "optional_seam_guide_source": "whole_object_lowcontrast_image_guide_or_sd35_reference_for_trellis2_texturing",
            "sdedit_seam_backprojection_available": False,
            "claim_boundary": "grammar-owned local geometry/material candidate; no 2D seam inpaint backprojection claim",
            "low_contrast_guide_required": True,
            "material_transition_policy": "object-space bark-to-olive fused lobe transition; Trellis guide remains whole-object low-contrast",
            "hard_tube_cap_mitigation": "fused veil entry mass, visually demoted outer support, attached volumetric lobes, entry sheaths, bark ridges, structural splits, and compact terminal buds",
        }
    )
    grammar = {
        "grammar_family": "Space colonization",
        "grammar_symbols": "attractor_field,influence_radius,kill_radius,step_size,hidden_entry_hub,junction_mask,fused_veil,volumetric_lobe,bark_ridge,terminal_bud",
        "target_symbol": "attractor",
        "operator_to_traditional_mapping": {
            "attractor_field": "keeps the same tree-crown target volume as the traditional SC baseline",
            "grow_tip": "advances support nodes by averaged attractor vectors",
            "hidden_entry_hub": "compresses the low-depth trunk into short multi-stem crown-entry hubs",
            "short_hub_subdivision_gate": "inserts shared-vertex intermediate supports so no exterior segment reads as one long rod",
            "junction_mask": "selects only the branch/crown transition band after growth",
            "entry_sheath": "locally covers hub/crown transitions without global resampling",
            "canopy_occlusion_shell": "adds broad attached volumetric lobes around the entry to hide hard material and branch seams",
            "fused_veil_entry_pad": "uses thick shared-vertex pads and volumetric lobes to read as crown mass instead of a sparse branch lattice",
            "mid_fused_veil": "turns the outer SC skeleton into attached volumetric crown mass while preserving the support graph underneath",
            "bark_ridge": "adds connected non-round surface relief instead of repainting the whole object",
            "terminal_bud": "turns exposed caps into compact connected buds rather than detached leaves",
        },
        "remote_comparison_unit": "one generated OBJ input to one traditional SC tree-crown target",
    }
    return mesh, controls, grammar


def _spec(
    *,
    case_id: str,
    mesh: pb.Mesh,
    controls: Dict,
    grammar: Dict,
    guide_key: str,
    gpu: int,
    seed: int,
    root_variant: str,
    parameter_variant: str,
    reason: str,
) -> Dict:
    operators = list(v23.OPERATORS_BY_FAMILY["Space colonization"]) + [
        "hidden_multistem_entry_hub",
        "short_hub_subdivision_gate",
        "entry_junction_mask",
        "compact_entry_sheaths",
        "attached_canopy_occlusion_shell",
        "fused_veil_entry_pads",
        "mid_canopy_fused_lobes",
        "connected_bark_ridges",
        "structural_canopy_splits",
        "compact_terminal_buds",
        "low_contrast_whole_object_guide",
    ]
    controls = dict(controls)
    controls.update(
        {
            "mesh_input_format": "obj",
            "same_classical_task_mode": True,
            "connected_support": True,
            "connectivity_gate_lcr_min": CONNECTIVITY_LCR_MIN,
            "low_poly_block_stamping": False,
            "mesh_token_stamping": False,
            "v33_sc_tree_fused_veil_naturalization": True,
        }
    )
    return {
        "case_id": case_id,
        "family": "Space colonization",
        "match_target": "sc_tree_crown_260",
        "traditional_target": "sc_tree_crown_260",
        "recursive_mode": "tree-crown attractor competition with hidden support and masked fused-veil naturalization",
        "mesh": mesh,
        "controls": controls,
        "guide_key": guide_key,
        "root_variant": root_variant,
        "grammar_guide": "v33_space_colonization_fused_veil_lowcontrast_tree_guide",
        "parameter_variant": parameter_variant,
        "gpu": int(gpu),
        "seed": int(seed),
        "operators": operators,
        "operator_composition": " -> ".join(operators),
        "grammar_mapping": v23._grammar_mapping("Space colonization", "sc_tree_crown_260", controls, grammar),
        "family_diagnostics": v23._family_diagnostics("Space colonization", "sc_tree_crown_260", controls),
        "why_matches_traditional": reason,
        "strict_match_notes": reason,
        "case_role": "v33_sc_tree_fused_veil_naturalization",
        "qa_priority": "remove_smooth_inserted_rod_while_preserving_sc_tree_crown",
        "rerun_reason": reason,
        "boundary_tag": "",
    }


def _case_specs(seed: int) -> List[Dict]:
    settings = [
        ("V33_sc_tree_fused_lobe_A", 4, 33001, 620, 218, 0.222, 0.074, 0.033, 0.072, 0.49, 7, 5, 0.106, 0.054, 0.040, 0.858, 0.0086, 0.90, 0.136, 8, 0, 22, 18, 24, 6, 3, 3, 2, 0, 0, 0, 1.18, 0.82, 0.40, "occlusion", "fused lobe A: V32-style occlusion with fewer thin leaves and thicker attached volumetric lobes"),
        ("V33_sc_tree_cambium_shell_B", 5, 33002, 640, 220, 0.226, 0.076, 0.033, 0.074, 0.50, 7, 6, 0.108, 0.052, 0.041, 0.856, 0.0088, 0.90, 0.134, 8, 0, 24, 20, 28, 6, 4, 3, 2, 0, 0, 0, 1.20, 0.80, 0.38, "softleaf", "cambium shell B: denser fused sleeves with no free scatter leaves, targeting lower post-GLB fragment count"),
        ("V33_sc_tree_lowfrag_lobe_C", 6, 33003, 590, 206, 0.230, 0.078, 0.032, 0.068, 0.52, 8, 5, 0.096, 0.048, 0.042, 0.858, 0.0092, 0.92, 0.130, 6, 0, 22, 22, 30, 4, 3, 2, 1, 0, 0, 0, 1.24, 0.78, 0.36, "occlusion", "lowfrag lobe C: most conservative V33 candidate with high cut depth, thick support floor, and fused lobes instead of thin leaves"),
        ("V33_sc_tree_balanced_fused_D", 7, 33004, 660, 226, 0.220, 0.074, 0.033, 0.078, 0.47, 7, 6, 0.112, 0.056, 0.040, 0.860, 0.0084, 0.90, 0.138, 8, 0, 24, 20, 26, 7, 4, 4, 2, 0, 0, 0, 1.16, 0.84, 0.42, "softleaf", "balanced fused D: keeps some support readability while replacing leaf islands with connected lobe sleeves"),
    ]
    rows: List[Dict] = []
    for (
        case_id,
        gpu,
        offset,
        attractors,
        iterations,
        influence,
        kill,
        step,
        z_gain,
        shrink,
        cut_depth,
        hub_count,
        fork_spread,
        entry_lift,
        base_radius,
        taper,
        floor,
        terminal_shrink,
        max_segment,
        entry_sheath_count,
        bracts_per_anchor,
        occlusion_shell_count,
        compact_pad_count,
        mid_veil_count,
        flare_count,
        ridge_count,
        split_count,
        bud_count,
        bracts_per_bud,
        scatter_leaf_count,
        scatter_needle_count,
        detail_radius_scale,
        flare_length_scale,
        support_visibility_fraction,
        guide_key,
        reason,
    ) in settings:
        mesh, controls, grammar = _build_sc_tree_case(
            seed + offset,
            attractors=attractors,
            iterations=iterations,
            influence=influence,
            kill=kill,
            step=step,
            z_gain=z_gain,
            shrink=shrink,
            cut_depth=cut_depth,
            hub_count=hub_count,
            fork_spread=fork_spread,
            entry_lift=entry_lift,
            base_radius=base_radius,
            radius_taper=taper,
            radius_floor=floor,
            terminal_shrink=terminal_shrink,
            max_segment=max_segment,
            entry_sheath_count=entry_sheath_count,
            bracts_per_anchor=bracts_per_anchor,
            occlusion_shell_count=occlusion_shell_count,
            compact_pad_count=compact_pad_count,
            mid_veil_count=mid_veil_count,
            flare_count=flare_count,
            ridge_count=ridge_count,
            split_count=split_count,
            bud_count=bud_count,
            bracts_per_bud=bracts_per_bud,
            scatter_leaf_count=scatter_leaf_count,
            scatter_needle_count=scatter_needle_count,
            detail_radius_scale=detail_radius_scale,
            flare_length_scale=flare_length_scale,
            support_visibility_fraction=support_visibility_fraction,
        )
        rows.append(
            _spec(
                case_id=case_id,
                mesh=mesh,
                controls=controls,
                grammar=grammar,
                guide_key=guide_key,
                gpu=gpu,
                seed=seed + offset,
                root_variant=case_id.replace("V33_", ""),
                parameter_variant=(
                    f"a{attractors}_iter{iterations}_ri{influence:.3f}_rk{kill:.3f}_step{step:.3f}"
                    f"_cut{cut_depth}_hub{hub_count}_maxseg{max_segment:.3f}_base{base_radius:.3f}"
                    f"_entry{entry_sheath_count}_shell{occlusion_shell_count}_pad{compact_pad_count}"
                    f"_veil{mid_veil_count}_vis{support_visibility_fraction:.2f}_ridge{ridge_count}"
                ),
                reason=reason,
            )
        )
    return rows


def _metadata_for(spec: Dict, mesh_path: Path, guide_path: str, metrics: Dict) -> Dict:
    metadata = v23._metadata_for(spec, mesh_path, guide_path, metrics)
    controls = spec["controls"]
    metadata["strict_generation_policy"] = GENERATION_POLICY
    metadata["selection_budget"] = SELECTION_BUDGET
    metadata["case_role"] = spec["case_role"]
    metadata["rerun_reason"] = spec["rerun_reason"]
    metadata["qa_priority"] = spec["qa_priority"]
    metadata["root_selection_log"]["root_source_type"] = "V33_sc_tree_fused_veil_input_generator"
    metadata["root_selection_log"]["source_generator"] = "assets/strict_visual_matched_cases_V33_sc_tree_fused_veil_naturalization_20260511.py"
    metadata["v33_seam_naturalization_contract"] = {
        "target_failure": "V24/V26/V27/V28 branch-crown seam remains visually hard; V31 improves short-hub metrics but still reads as a sparse branch lattice",
        "geometry_operator": "hidden short-hub support plus shared-vertex subdivision, visually demoted outer support, fused veil pads, attached volumetric lobes, compact entry sheaths, occlusion shell, bark ridges, splits, and terminal buds",
        "base_evidence": "V33 uses V31-C's low-fragment metric direction but replaces the sparse branch-lattice read with attached fused veil geometry",
        "seam_mask": {
            "space": "object_xyz",
            "scope": controls.get("mask_scope"),
            "selection_rule": controls.get("seam_mask_selection_rule"),
            "radius": controls.get("seam_mask_radius"),
            "center_count": controls.get("seam_mask_center_count"),
            "centers": controls.get("seam_mask_centers", [])[:96],
        },
        "naturalization_regions": controls.get("naturalization_regions", []),
        "optional_seam_guide_source": controls.get("optional_seam_guide_source"),
        "sdedit_seam_backprojection_available": False,
        "texture_operator": "low-contrast whole-object guide for Trellis2 texturing; no 2D seam inpaint backprojection claim",
        "material_transition_policy": controls.get("material_transition_policy"),
        "claim_boundary": controls.get("claim_boundary"),
        "post_glb_acceptance": "paper candidate only if GLB zoom no longer reads as one inserted rod and r0 LCR remains >=0.999 preferred",
    }
    metadata["v33_remote_cache_policy"] = {
        "cache_root": REMOTE_STORAGE_ROOT + "/cache",
        "no_system_tmp": True,
    }
    return metadata


def materialize(root: Path, out_dir: Path, seed: int = 20260511, case_limit: Optional[int] = None) -> Dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    guides = _write_guides(out_dir)
    specs = _case_specs(seed)
    if case_limit is not None:
        specs = specs[: int(case_limit)]

    rows: List[Dict] = []
    metrics_rows: List[Dict] = []
    for spec in specs:
        case_dir = out_dir / spec["case_id"]
        mesh_path = case_dir / f"{spec['case_id']}.obj"
        v23._export_mesh(mesh_path, spec["mesh"])
        guide_path = guides[spec["guide_key"]]
        metrics = v23._mesh_stats(mesh_path, spec["controls"])
        if metrics["largest_mesh_component_vertex_ratio"] < CONNECTIVITY_LCR_MIN:
            raise RuntimeError(f"{spec['case_id']} failed V33 connectivity gate: {metrics}")
        if float(spec["controls"].get("external_support_max_segment_after_subdivision", 999.0)) > EXTERNAL_SUPPORT_MAX_SEGMENT_GATE + 1e-6:
            raise RuntimeError(f"{spec['case_id']} failed V33 short-hub segment gate: {spec['controls']}")
        metadata = _metadata_for(spec, mesh_path, guide_path, metrics)
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
            "gpu_group": int(spec["gpu"]),
            "seed": int(spec["seed"]),
            "operators": json.dumps(spec["operators"], ensure_ascii=False),
            "operator_composition": spec["operator_composition"],
            "controls": json.dumps(spec["controls"], ensure_ascii=False, sort_keys=True),
            "why_matches_traditional": spec["why_matches_traditional"],
            "strict_match_notes": spec["strict_match_notes"],
            "case_role": spec["case_role"],
            "qa_priority": spec["qa_priority"],
            "rerun_reason": spec["rerun_reason"],
            "boundary_tag": "",
            "strict_one_to_one": "true",
            "generation_policy": GENERATION_POLICY,
            "mesh_input_policy": "obj_mesh_inputs_only",
            "mesh_pbr_policy": MESH_PBR_POLICY,
            "surface_strategy": SURFACE_STRATEGY,
            "block_or_token_stamping": "false",
            "root_variant": spec["root_variant"],
            "grammar_guide": spec["grammar_guide"],
            "parameter_variant": spec["parameter_variant"],
            "selection_budget": SELECTION_BUDGET,
            "storage_root": REMOTE_STORAGE_ROOT,
            "storage_limit_gb": STORAGE_LIMIT_GB,
            "pre_export_lcr_gate": CONNECTIVITY_LCR_MIN,
            "pre_export_gate_or_boundary": "lcr>=0.999",
            "seam_mask_center_count": int(spec["controls"].get("seam_mask_center_count", 0)),
            "entry_sheath_count": int(spec["controls"].get("entry_sheath_count", 0)),
            "terminal_bud_count": int(spec["controls"].get("terminal_bud_count", 0)),
            "junction_flare_count": int(spec["controls"].get("junction_flare_count", 0)),
            "ridge_count": int(spec["controls"].get("ridge_count", 0)),
            "structural_split_count": int(spec["controls"].get("structural_split_count", 0)),
            "hidden_trunk_hub_count": int(spec["controls"].get("hidden_trunk_hub_count", 0)),
            "occlusion_shell_lobe_count": int(spec["controls"].get("occlusion_shell_lobe_count", 0)),
            "fused_veil_pad_count": int(spec["controls"].get("fused_veil_pad_count", 0)),
            "fused_veil_pad_lobe_count": int(spec["controls"].get("fused_veil_pad_lobe_count", 0)),
            "mid_fused_veil_count": int(spec["controls"].get("mid_fused_veil_count", 0)),
            "mid_fused_veil_lobe_count": int(spec["controls"].get("mid_fused_veil_lobe_count", 0)),
            "fused_veil_total_lobe_count": int(spec["controls"].get("fused_veil_total_lobe_count", 0)),
            "support_visibility_fraction": float(spec["controls"].get("support_visibility_fraction", 1.0)),
            "external_support_max_segment_after_subdivision": float(
                spec["controls"].get("external_support_max_segment_after_subdivision", 0.0)
            ),
            "sdedit_seam_backprojection_available": str(bool(spec["controls"].get("sdedit_seam_backprojection_available", False))).lower(),
        }
        rows.append(row)
        metrics_rows.append(
            {
                "case_id": spec["case_id"],
                "family": spec["family"],
                "match_target": spec["match_target"],
                "traditional_target": spec["traditional_target"],
                **metrics,
                "qa_priority": spec["qa_priority"],
                "boundary_tag": "",
                "seam_mask_center_count": int(spec["controls"].get("seam_mask_center_count", 0)),
                "entry_sheath_count": int(spec["controls"].get("entry_sheath_count", 0)),
                "terminal_bud_count": int(spec["controls"].get("terminal_bud_count", 0)),
                "junction_flare_count": int(spec["controls"].get("junction_flare_count", 0)),
                "ridge_count": int(spec["controls"].get("ridge_count", 0)),
                "hidden_trunk_hub_count": int(spec["controls"].get("hidden_trunk_hub_count", 0)),
                "external_support_max_segment": float(spec["controls"].get("external_support_max_segment", 0.0)),
                "external_support_max_segment_after_subdivision": float(
                    spec["controls"].get("external_support_max_segment_after_subdivision", 0.0)
                ),
                "occlusion_shell_lobe_count": int(spec["controls"].get("occlusion_shell_lobe_count", 0)),
                "fused_veil_pad_count": int(spec["controls"].get("fused_veil_pad_count", 0)),
                "fused_veil_pad_lobe_count": int(spec["controls"].get("fused_veil_pad_lobe_count", 0)),
                "mid_fused_veil_count": int(spec["controls"].get("mid_fused_veil_count", 0)),
                "mid_fused_veil_lobe_count": int(spec["controls"].get("mid_fused_veil_lobe_count", 0)),
                "fused_veil_total_lobe_count": int(spec["controls"].get("fused_veil_total_lobe_count", 0)),
                "support_visibility_fraction": float(spec["controls"].get("support_visibility_fraction", 1.0)),
            }
        )

    manifest_fields = list(rows[0].keys()) if rows else []
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    obj_zoom_cases = []
    for row in rows:
        controls = json.loads(row["controls"])
        targets = controls.get("seam_mask_centers", [])[:36]
        obj_zoom_cases.append(
            {
                "label": row["case_id"] + "_obj_seamtarget",
                "mesh": str(Path(row["mesh_path"]).resolve()),
                "plan_mesh": str(Path(row["mesh_path"]).resolve()),
                "material_mode": "cedar",
                "zoom_levels": 2,
                "detail_targets": targets,
                "detail_target_source": "v33_object_space_seam_mask",
            }
        )
    (out_dir / "V33_obj_zoom_manifest_seamtarget_20260511.json").write_text(
        json.dumps({"cases": obj_zoom_cases}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    metric_fields = list(metrics_rows[0].keys()) if metrics_rows else []
    with (out_dir / "initial_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        writer.writerows(metrics_rows)
    (out_dir / "initial_metrics.json").write_text(json.dumps(metrics_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    case_lines = [f"{row['case_id']}|{row['mesh_path']}|{row['guide_image']}|{row['seed']}|{row['gpu_group']}" for row in rows]
    (out_dir / "a100-2_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    (out_dir / "gpu4567_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    gpu_case_counts: Dict[str, int] = {}
    for gpu in ALLOWED_GPUS:
        selected = [line for line, row in zip(case_lines, rows) if int(row["gpu_group"]) == gpu]
        gpu_case_counts[str(gpu)] = len(selected)
        (out_dir / f"gpu{gpu}_cases.txt").write_text("\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")

    summary = {
        "out_dir": str(out_dir),
        "num_cases": len(rows),
        "remote_target": REMOTE_TARGET,
        "allowed_gpus": ALLOWED_GPUS,
        "storage_root": REMOTE_STORAGE_ROOT,
        "storage_limit_gb": STORAGE_LIMIT_GB,
        "surface_generator": "strict_visual_matched_cases_V33_sc_tree_fused_veil_naturalization",
        "mesh_input_policy": "obj_mesh_inputs_only",
        "mesh_pbr_policy": MESH_PBR_POLICY,
        "surface_strategy": SURFACE_STRATEGY,
        "connectivity_gate": {
            "largest_component_vertex_ratio_min": CONNECTIVITY_LCR_MIN,
            "pre_trellis_required": True,
            "boundary_tag_allowed": False,
        },
        "fused_veil_gate": {
            "mask_scope": "object_space_fused_veil_entry_band_and_terminal_caps_only",
            "min_seam_mask_centers": min(int(row["seam_mask_center_count"]) for row in rows) if rows else 0,
            "min_entry_sheaths": min(int(row["entry_sheath_count"]) for row in rows) if rows else 0,
            "min_hidden_hubs": min(int(row["hidden_trunk_hub_count"]) for row in rows) if rows else 0,
            "min_fused_veil_pads": min(int(row["fused_veil_pad_count"]) for row in rows) if rows else 0,
            "min_mid_fused_veils": min(int(row["mid_fused_veil_count"]) for row in rows) if rows else 0,
            "min_fused_veil_lobes": min(int(row["fused_veil_total_lobe_count"]) for row in rows) if rows else 0,
            "max_support_visibility_fraction": max(float(row["support_visibility_fraction"]) for row in rows) if rows else 1.0,
            "max_external_support_segment_after_subdivision": max(
                float(row["external_support_max_segment_after_subdivision"]) for row in rows
            ) if rows else 0.0,
            "external_support_max_segment_gate": EXTERNAL_SUPPORT_MAX_SEGMENT_GATE,
            "sdedit_seam_backprojection_available": False,
            "image_generation_considered": True,
        },
        "post_glb_target_floor": {
            "preferred_r0_lcr_min": 0.999,
            "fallback_r1_lcr_min": 1.0,
            "visual_gate": "no single long inserted rod at branch/crown seam in overview or seam-target zoom",
        },
        "storage_risk": {
            "expected_upper_bound_gb": 24,
            "risk_level": "low",
            "notes": "4 Trellis2 mesh/PBR exports; cache must remain inside project root.",
        },
        "gpu_case_counts": gpu_case_counts,
        "priority_cases": [row["case_id"] for row in rows],
        "manifest": str(out_dir / "manifest.csv"),
        "initial_metrics": str(out_dir / "initial_metrics.csv"),
        "obj_zoom_manifest": str(out_dir / "V33_obj_zoom_manifest_seamtarget_20260511.json"),
        "do_not_launch_remote": True,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# V33 SC Tree Fused-Veil Naturalization Dry Run\n\n"
        "Predeclared fused-veil branch/crown seam candidates. V33 uses "
        "a short-hub subdivision gate, visually demoted outer support, attached canopy occlusion shell, and "
        "object-space transition metadata while explicitly avoiding any claim of "
        "a 2D seam-inpaint backprojection pipeline.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("RGG_ROOT", ROOT_DIR)))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260511)
    parser.add_argument("--case-limit", type=int, default=None)
    args = parser.parse_args()
    materialize(args.root, args.out, seed=args.seed, case_limit=args.case_limit)


if __name__ == "__main__":
    main()
