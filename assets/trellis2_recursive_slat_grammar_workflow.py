#!/usr/bin/env python3
"""Recursive grammar workflows in Trellis2 mesh-first shape-SLat space."""

from __future__ import annotations

import argparse
import json
import os
import time
import traceback
from pathlib import Path

import numpy as np

from triton_beegfs_cache_patch import apply_triton_beegfs_cache_patch

apply_triton_beegfs_cache_patch()


COMPETE_JITTER = 0.0
COMPETE_GENERATOR = None
GROWTH_AXIS = 1
GROWTH_SIGN = 1


def growth_height(xyz):
    return xyz[:, GROWTH_AXIS].float() * float(GROWTH_SIGN)


def lateral_axes():
    axes = [0, 1, 2]
    axes.remove(GROWTH_AXIS)
    return axes[0], axes[1]


def write_obj(path: Path, vertices, faces) -> None:
    vertices = np.asarray(vertices)
    faces = np.asarray(faces)
    with path.open("w") as f:
        for v in vertices:
            f.write(f"v {float(v[0]):.6f} {float(v[1]):.6f} {float(v[2]):.6f}\n")
        for face in faces:
            f.write(f"f {int(face[0]) + 1} {int(face[1]) + 1} {int(face[2]) + 1}\n")


def restore_output_frame(vertices):
    """Invert the mesh-to-SLat axis conversion before writing OBJ/previews."""

    vertices = np.asarray(vertices).copy()
    restored = vertices.copy()
    restored[:, 0] = vertices[:, 0]
    restored[:, 1] = vertices[:, 2]
    restored[:, 2] = -vertices[:, 1]
    return restored


def maybe_restore_output_frame(vertices, restore: bool):
    if restore:
        return restore_output_frame(vertices)
    return np.asarray(vertices)


def apply_preencode_transform(vertices, transform: str):
    """Apply an explicit root-frame transform before mesh-to-SLat conversion."""

    vertices = np.asarray(vertices).copy()
    if transform == "identity":
        return vertices
    out = vertices.copy()
    x = vertices[:, 0].copy()
    y = vertices[:, 1].copy()
    z = vertices[:, 2].copy()
    if transform == "rot_x_neg90":
        out[:, 0] = x
        out[:, 1] = z
        out[:, 2] = -y
        return out
    if transform == "rot_x_pos90":
        out[:, 0] = x
        out[:, 1] = -z
        out[:, 2] = y
        return out
    if transform == "rot_y_neg90":
        out[:, 0] = -z
        out[:, 1] = y
        out[:, 2] = x
        return out
    if transform == "rot_y_pos90":
        out[:, 0] = z
        out[:, 1] = y
        out[:, 2] = -x
        return out
    raise ValueError(f"unknown preencode transform {transform}")


def render_preview(path: Path, vertices, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    vertices = np.asarray(vertices)
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")
    if len(vertices):
        step = max(1, len(vertices) // 30000)
        pts = vertices[::step]
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=0.18, c=pts[:, 2], cmap="viridis")
        center = (vertices.min(0) + vertices.max(0)) / 2
        span = max(float((vertices.max(0) - vertices.min(0)).max()), 1e-3)
        ax.set_xlim(center[0] - span / 2, center[0] + span / 2)
        ax.set_ylim(center[1] - span / 2, center[1] + span / 2)
        ax.set_zlim(center[2] - span / 2, center[2] + span / 2)
    ax.set_title(title)
    ax.set_axis_off()
    ax.view_init(22, -45)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def rewrite_model_path(path: str, snapshot: Path) -> str:
    return str(snapshot / path) if path.startswith("ckpts/") else path


def sparse_merge(feats, coords):
    import torch
    from trellis2.modules.sparse import SparseTensor

    unique, inverse = torch.unique(coords, dim=0, return_inverse=True)
    out = torch.zeros((unique.shape[0], feats.shape[1]), dtype=feats.dtype, device=feats.device)
    counts = torch.zeros((unique.shape[0], 1), dtype=feats.dtype, device=feats.device)
    out.index_add_(0, inverse, feats)
    counts.index_add_(0, inverse, torch.ones((feats.shape[0], 1), dtype=feats.dtype, device=feats.device))
    return SparseTensor(feats=out / counts.clamp_min(1), coords=unique)


def sparse_with_coords(template, coords):
    from trellis2.modules.sparse import SparseTensor

    return SparseTensor(feats=template.feats.clone(), coords=coords.to(template.coords.device, dtype=template.coords.dtype))


def coord_bounds(st):
    xyz = st.coords[:, 1:]
    return xyz.min(0).values, xyz.max(0).values


def clip_valid(coords, limit):
    return ((coords[:, 1:] >= 0) & (coords[:, 1:] <= limit)).all(dim=1)


def mirror_x(st, limit):
    coords = st.coords.clone()
    coords[:, 1] = limit - coords[:, 1]
    return sparse_with_coords(st, coords)


def tip_continue(st, limit, fraction=0.35, shift_ratio=0.18):
    import torch

    coords = st.coords
    xyz = coords[:, 1:]
    lo, hi = coord_bounds(st)
    threshold = torch.quantile(growth_height(xyz), 1.0 - fraction)
    mask = growth_height(xyz) >= threshold
    copied = coords[mask].clone()
    feats = st.feats[mask].clone()
    extent = (hi - lo).clamp_min(1)
    copied[:, GROWTH_AXIS + 1] += GROWTH_SIGN * max(1, int(extent[GROWTH_AXIS].item() * shift_ratio))
    valid = clip_valid(copied, limit)
    return sparse_merge(torch.cat([st.feats, feats[valid]], dim=0), torch.cat([coords, copied[valid]], dim=0))


def tip_fork(st, limit, fraction=0.30, shift_ratio=0.16):
    import torch

    coords = st.coords
    xyz = coords[:, 1:]
    lo, hi = coord_bounds(st)
    threshold = torch.quantile(growth_height(xyz), 1.0 - fraction)
    mask = growth_height(xyz) >= threshold
    extent = (hi - lo).clamp_min(1)
    ax0, ax1 = lateral_axes()
    dx = max(1, int(extent[ax0].item() * shift_ratio))
    dy = max(1, int(extent[GROWTH_AXIS].item() * shift_ratio))
    dz = max(1, int(extent[ax1].item() * shift_ratio * 0.5))
    all_feats = [st.feats]
    all_coords = [coords]
    for sign in (-1, 1):
        copied = coords[mask].clone()
        copied[:, ax0 + 1] += sign * dx
        copied[:, GROWTH_AXIS + 1] += GROWTH_SIGN * dy
        copied[:, ax1 + 1] += -sign * dz
        valid = clip_valid(copied, limit)
        all_coords.append(copied[valid])
        all_feats.append(st.feats[mask].clone()[valid])
    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def side_branch(st, limit, fraction=0.28, shift_ratio=0.18):
    import torch

    coords = st.coords
    xyz = coords[:, 1:]
    lo, hi = coord_bounds(st)
    threshold = torch.quantile(growth_height(xyz), 1.0 - fraction)
    mask = growth_height(xyz) >= threshold
    extent = (hi - lo).clamp_min(1)
    ax0, _ = lateral_axes()
    copied = coords[mask].clone()
    copied[:, ax0 + 1] += max(1, int(extent[ax0].item() * shift_ratio))
    copied[:, GROWTH_AXIS + 1] += GROWTH_SIGN * max(1, int(extent[GROWTH_AXIS].item() * shift_ratio * 0.5))
    valid = clip_valid(copied, limit)
    return sparse_merge(torch.cat([st.feats, st.feats[mask].clone()[valid]], dim=0), torch.cat([coords, copied[valid]], dim=0))


def attached_copies(st, mask, deltas, limit, bridge_steps=4):
    import torch

    coords = st.coords
    src_coords = coords[mask]
    src_feats = st.feats[mask].clone()
    all_feats = [st.feats]
    all_coords = [coords]
    for delta in deltas:
        delta = delta.to(device=coords.device, dtype=coords.dtype)
        for step_idx in range(1, bridge_steps + 1):
            frac = step_idx / float(bridge_steps)
            step_delta = torch.round(delta.float() * frac).to(coords.dtype)
            if torch.all(step_delta == 0):
                continue
            copied = src_coords.clone()
            copied[:, 1:] += step_delta
            valid = clip_valid(copied, limit)
            if valid.sum() == 0:
                continue
            all_coords.append(copied[valid])
            all_feats.append(src_feats[valid])
    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def tip_fork_attached(st, limit, fraction=0.24, shift_ratio=0.14, bridge_steps=4):
    import torch

    coords = st.coords
    xyz = coords[:, 1:]
    lo, hi = coord_bounds(st)
    threshold = torch.quantile(growth_height(xyz), 1.0 - fraction)
    mask = growth_height(xyz) >= threshold
    extent = (hi - lo).clamp_min(1)
    ax0, ax1 = lateral_axes()
    dx = max(1, int(extent[ax0].item() * shift_ratio))
    dy = max(1, int(extent[GROWTH_AXIS].item() * shift_ratio))
    dz = max(1, int(extent[ax1].item() * shift_ratio * 0.45))
    delta_a = torch.zeros(3, device=coords.device, dtype=torch.long)
    delta_b = torch.zeros(3, device=coords.device, dtype=torch.long)
    delta_a[ax0] = -dx
    delta_a[GROWTH_AXIS] = GROWTH_SIGN * dy
    delta_a[ax1] = dz
    delta_b[ax0] = dx
    delta_b[GROWTH_AXIS] = GROWTH_SIGN * dy
    delta_b[ax1] = -dz
    deltas = [
        delta_a,
        delta_b,
    ]
    return attached_copies(st, mask, deltas, limit, bridge_steps=bridge_steps)


def side_branch_attached(st, limit, fraction=0.22, shift_ratio=0.14, bridge_steps=4):
    import torch

    coords = st.coords
    xyz = coords[:, 1:]
    lo, hi = coord_bounds(st)
    threshold = torch.quantile(growth_height(xyz), 1.0 - fraction)
    mask = growth_height(xyz) >= threshold
    extent = (hi - lo).clamp_min(1)
    ax0, _ = lateral_axes()
    delta = torch.zeros(3, device=coords.device, dtype=torch.long)
    delta[ax0] = max(1, int(extent[ax0].item() * shift_ratio))
    delta[GROWTH_AXIS] = GROWTH_SIGN * max(1, int(extent[GROWTH_AXIS].item() * shift_ratio * 0.5))
    return attached_copies(st, mask, [delta], limit, bridge_steps=bridge_steps)


def crown_bud_attached(st, limit, fraction=0.08, shift_ratio=0.075, bridge_steps=6):
    import torch

    coords = st.coords
    xyz = coords[:, 1:]
    lo, hi = coord_bounds(st)
    height = growth_height(xyz)
    threshold = torch.quantile(height, 1.0 - fraction)
    mask = height >= threshold
    extent = (hi - lo).clamp_min(1)
    delta = torch.zeros(3, device=coords.device, dtype=torch.long)
    delta[GROWTH_AXIS] = GROWTH_SIGN * max(1, int(extent[GROWTH_AXIS].item() * shift_ratio))
    return attached_copies(st, mask, [delta], limit, bridge_steps=bridge_steps)


def crown_micro_fork_attached(st, limit, fraction=0.07, shift_ratio=0.07, bridge_steps=6):
    import torch

    coords = st.coords
    xyz = coords[:, 1:]
    lo, hi = coord_bounds(st)
    height = growth_height(xyz)
    threshold = torch.quantile(height, 1.0 - fraction)
    mask = height >= threshold
    extent = (hi - lo).clamp_min(1)
    ax0, ax1 = lateral_axes()
    lateral0 = max(1, int(extent[ax0].item() * shift_ratio))
    lateral1 = max(1, int(extent[ax1].item() * shift_ratio * 0.35))
    upward = max(1, int(extent[GROWTH_AXIS].item() * shift_ratio * 0.85))
    deltas = []
    for sign in (-1, 1):
        delta = torch.zeros(3, device=coords.device, dtype=torch.long)
        delta[ax0] = sign * lateral0
        delta[ax1] = -sign * lateral1
        delta[GROWTH_AXIS] = GROWTH_SIGN * upward
        deltas.append(delta)
    return attached_copies(st, mask, deltas, limit, bridge_steps=bridge_steps)


def radial_y_clone(st, limit):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    center = (xyz.min(0).values + xyz.max(0).values) / 2
    rel = xyz - center
    rotated = torch.stack([-rel[:, 2], rel[:, 1], rel[:, 0]], dim=1) + center
    copied = torch.cat([coords[:, :1], torch.round(rotated).to(coords.dtype)], dim=1)
    valid = clip_valid(copied, limit)
    return sparse_merge(torch.cat([st.feats, st.feats.clone()[valid]], dim=0), torch.cat([coords, copied[valid]], dim=0))


def shrink_echo(st, limit, scale=0.72):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    center = (xyz.min(0).values + xyz.max(0).values) / 2
    copied_xyz = torch.round((xyz - center) * scale + center).to(coords.dtype)
    copied = torch.cat([coords[:, :1], copied_xyz], dim=1)
    valid = clip_valid(copied, limit)
    return sparse_merge(torch.cat([st.feats, st.feats.clone()[valid]], dim=0), torch.cat([coords, copied[valid]], dim=0))


def translate_clone(st, limit, axis: int, shift_ratio=0.22):
    import torch

    coords = st.coords
    lo, hi = coord_bounds(st)
    extent = (hi - lo).clamp_min(1)
    copied = coords.clone()
    copied[:, axis + 1] += max(1, int(extent[axis].item() * shift_ratio))
    valid = clip_valid(copied, limit)
    return sparse_merge(
        torch.cat([st.feats, st.feats.clone()[valid]], dim=0),
        torch.cat([coords, copied[valid]], dim=0),
    )


def rotate_z_clone(st, limit):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    center = (xyz.min(0).values + xyz.max(0).values) / 2
    rel = xyz - center
    rotated = torch.stack([-rel[:, 1], rel[:, 0], rel[:, 2]], dim=1) + center
    copied = torch.cat([coords[:, :1], torch.round(rotated).to(coords.dtype)], dim=1)
    valid = clip_valid(copied, limit)
    return sparse_merge(
        torch.cat([st.feats, st.feats.clone()[valid]], dim=0),
        torch.cat([coords, copied[valid]], dim=0),
    )


def scale_clone(st, limit, scale=1.18):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    center = (xyz.min(0).values + xyz.max(0).values) / 2
    copied_xyz = torch.round((xyz - center) * scale + center).to(coords.dtype)
    copied = torch.cat([coords[:, :1], copied_xyz], dim=1)
    valid = clip_valid(copied, limit)
    return sparse_merge(
        torch.cat([st.feats, st.feats.clone()[valid]], dim=0),
        torch.cat([coords, copied[valid]], dim=0),
    )


def radial4_y_clone(st, limit):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    center = (xyz.min(0).values + xyz.max(0).values) / 2
    rel = xyz - center
    all_coords = [coords]
    all_feats = [st.feats]
    for k in range(1, 4):
        if k == 1:
            rotated = torch.stack([-rel[:, 2], rel[:, 1], rel[:, 0]], dim=1) + center
        elif k == 2:
            rotated = torch.stack([-rel[:, 0], rel[:, 1], -rel[:, 2]], dim=1) + center
        else:
            rotated = torch.stack([rel[:, 2], rel[:, 1], -rel[:, 0]], dim=1) + center
        copied = torch.cat([coords[:, :1], torch.round(rotated).to(coords.dtype)], dim=1)
        valid = clip_valid(copied, limit)
        all_coords.append(copied[valid])
        all_feats.append(st.feats.clone()[valid])
    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def portal_insert(st, limit, scale=0.58, y_shift_ratio=0.12):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (xyz.min(0).values + xyz.max(0).values) / 2
    extent = (hi - lo).clamp_min(1)
    copied_xyz = torch.round((xyz - center) * scale + center).to(coords.dtype)
    copied = torch.cat([coords[:, :1], copied_xyz], dim=1)
    copied[:, 2] += max(1, int(extent[1].item() * y_shift_ratio))
    valid = clip_valid(copied, limit)
    return sparse_merge(
        torch.cat([st.feats, st.feats.clone()[valid]], dim=0),
        torch.cat([coords, copied[valid]], dim=0),
    )


def attached_transform_copies(st, target_xyz_list, limit, bridge_steps=4):
    """Copy sparse tokens through interpolated transforms so copies stay attached.

    The older radial/portal operators created a transformed duplicate and then
    trusted later projection/pruning to keep a usable component.  Thin crown and
    arch roots fail under that contract: the duplicate intersects or drifts and
    pruning erases the intended recursive motif.  This helper adds a short
    bridge in sparse-coordinate space for every transformed copy, making the
    copy operation itself attachment-aware before decode.
    """

    import torch

    coords = st.coords
    xyz0 = coords[:, 1:].float()
    all_coords = [coords]
    all_feats = [st.feats]
    for target_xyz in target_xyz_list:
        target_xyz = target_xyz.to(device=coords.device, dtype=torch.float32)
        for step in range(1, bridge_steps + 1):
            frac = step / float(bridge_steps)
            interp = torch.round(xyz0 * (1.0 - frac) + target_xyz * frac).to(coords.dtype)
            copied = torch.cat([coords[:, :1], interp], dim=1)
            valid = clip_valid(copied, limit)
            if valid.sum() == 0:
                continue
            all_coords.append(copied[valid])
            all_feats.append(st.feats.clone()[valid])
    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def attached_transform_masked_copies(st, mask, target_xyz_list, limit, bridge_steps=5):
    """Copy only selected frontier tokens through interpolated transforms.

    Whole-root transforms are useful diagnostics but too destructive for thin
    crowns, arches, and mechanical modules: the decoder receives a duplicate
    shell instead of a small recursive child.  The masked variant keeps the root
    intact and grows only from semantic handles selected by the operator.
    """

    import torch

    coords = st.coords
    src_coords = coords[mask]
    src_feats = st.feats[mask].clone()
    if src_coords.shape[0] == 0:
        return st
    xyz0 = src_coords[:, 1:].float()
    all_coords = [coords]
    all_feats = [st.feats]
    for target_xyz in target_xyz_list:
        target_xyz = target_xyz.to(device=coords.device, dtype=torch.float32)
        if target_xyz.shape[0] != xyz0.shape[0]:
            target_xyz = target_xyz[mask]
        for step in range(1, bridge_steps + 1):
            frac = step / float(bridge_steps)
            interp = torch.round(xyz0 * (1.0 - frac) + target_xyz * frac).to(coords.dtype)
            copied = torch.cat([src_coords[:, :1], interp], dim=1)
            valid = clip_valid(copied, limit)
            if valid.sum() == 0:
                continue
            all_coords.append(copied[valid])
            all_feats.append(src_feats[valid])
    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def masked_target_copies_with_tube_support_20260511t(
    st,
    mask,
    target_xyz_list,
    limit,
    support_radius=1.15,
    support_steps=10,
    max_support_tokens=180,
):
    """Attach transformed branch handles with an explicit sparse tube support.

    The s visible-child operator moved a branch handle far enough to be visible,
    but the decoder often interpreted the interpolated sparse mask as a torn
    sheet or point cloud.  This helper keeps only the final transformed handle
    copy and adds a compact cylindrical support path between source and target
    anchors so the decoder receives a continuous branch cue.
    """

    import torch

    coords = st.coords
    src_coords = coords[mask]
    src_feats = st.feats[mask].clone()
    if src_coords.shape[0] == 0:
        return st
    xyz0 = src_coords[:, 1:].float()
    batch = src_coords[:1, :1]
    mean_feat = src_feats.mean(dim=0, keepdim=True)
    all_coords = [coords]
    all_feats = [st.feats]

    radius_i = max(0, int(round(float(support_radius))))
    offsets = []
    for dx in range(-radius_i, radius_i + 1):
        for dy in range(-radius_i, radius_i + 1):
            for dz in range(-radius_i, radius_i + 1):
                if (dx * dx + dy * dy + dz * dz) ** 0.5 <= float(support_radius) + 1e-6:
                    offsets.append([dx, dy, dz])
    if not offsets:
        offsets = [[0, 0, 0]]
    offsets_t = torch.tensor(offsets, device=coords.device, dtype=torch.float32)

    for target_xyz in target_xyz_list:
        target_xyz = target_xyz.to(device=coords.device, dtype=torch.float32)
        if target_xyz.shape[0] != xyz0.shape[0]:
            target_xyz = target_xyz[mask]
        final_xyz = torch.round(target_xyz).to(coords.dtype)
        final_coords = torch.cat([src_coords[:, :1], final_xyz], dim=1)
        valid_final = clip_valid(final_coords, limit)
        if valid_final.sum() > 0:
            all_coords.append(final_coords[valid_final])
            all_feats.append(src_feats[valid_final])

        source_anchor = xyz0.mean(dim=0)
        target_anchor = target_xyz.mean(dim=0)
        support_xyz = []
        for step in range(1, support_steps + 1):
            frac = step / float(support_steps + 1)
            center = source_anchor * (1.0 - frac) + target_anchor * frac
            support_xyz.append(torch.round(center[None, :] + offsets_t))
        if support_xyz:
            support_xyz = torch.cat(support_xyz, dim=0).to(coords.dtype)
            support_coords = torch.cat([batch.expand(support_xyz.shape[0], 1).to(coords.dtype), support_xyz], dim=1)
            support_coords = torch.unique(support_coords, dim=0)
            valid_support = clip_valid(support_coords, limit)
            support_coords = support_coords[valid_support]
            if support_coords.shape[0] > max_support_tokens:
                keep = torch.linspace(
                    0,
                    support_coords.shape[0] - 1,
                    steps=max_support_tokens,
                    device=support_coords.device,
                ).long()
                support_coords = support_coords[keep]
            if support_coords.shape[0] > 0:
                all_coords.append(support_coords)
                all_feats.append(mean_feat.expand(support_coords.shape[0], -1))

    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def connected_patch_mask_20260512i(st, pool, score, max_tokens=24, radius=3.4, min_tokens=8):
    """Select one local handle patch instead of scattered top-k surface tokens."""

    import torch

    idx = torch.nonzero(pool, as_tuple=False).flatten()
    if idx.numel() == 0:
        return None
    seed = idx[torch.argmax(score[idx])]
    xyz = st.coords[:, 1:].float()
    center = xyz[seed]
    dist = torch.linalg.norm(xyz - center[None, :], dim=1)
    patch = pool & (dist <= float(radius))
    if patch.sum() < min_tokens:
        local_idx = idx[torch.topk(-dist[idx], k=min(idx.numel(), max(min_tokens, max_tokens)), largest=True).indices]
        patch = torch.zeros_like(pool)
        patch[local_idx] = True
    return cap_mask_by_score(patch, score, max_tokens)


def masked_target_copies_with_patch_support_20260512i(
    st,
    mask,
    target_xyz_list,
    limit,
    support_radius=1.35,
    support_steps=14,
    max_support_tokens=220,
):
    """Copy one connected patch with both patch-wise and centroid supports."""

    import torch

    coords = st.coords
    src_coords = coords[mask]
    src_feats = st.feats[mask].clone()
    if src_coords.shape[0] == 0:
        return st
    xyz0 = src_coords[:, 1:].float()
    batch = src_coords[:1, :1]
    mean_feat = src_feats.mean(dim=0, keepdim=True)
    all_coords = [coords]
    all_feats = [st.feats]

    radius_i = max(1, int(round(float(support_radius))))
    offsets = []
    for dx in range(-radius_i, radius_i + 1):
        for dy in range(-radius_i, radius_i + 1):
            for dz in range(-radius_i, radius_i + 1):
                if (dx * dx + dy * dy + dz * dz) ** 0.5 <= float(support_radius) + 1e-6:
                    offsets.append([dx, dy, dz])
    offsets_t = torch.tensor(offsets or [[0, 0, 0]], device=coords.device, dtype=torch.float32)

    for target_xyz in target_xyz_list:
        target_xyz = target_xyz.to(device=coords.device, dtype=torch.float32)
        if target_xyz.shape[0] != xyz0.shape[0]:
            target_xyz = target_xyz[mask]
        final_xyz = torch.round(target_xyz).to(coords.dtype)
        final_coords = torch.cat([src_coords[:, :1], final_xyz], dim=1)
        valid_final = clip_valid(final_coords, limit)
        if valid_final.sum() > 0:
            all_coords.append(final_coords[valid_final])
            all_feats.append(src_feats[valid_final])

        support_parts = []
        centroid_src = xyz0.mean(dim=0)
        centroid_dst = target_xyz.mean(dim=0)
        for step in range(1, support_steps + 1):
            frac = step / float(support_steps + 1)
            centroid = torch.round(centroid_src * (1.0 - frac) + centroid_dst * frac)
            support_parts.append(torch.round(centroid[None, :] + offsets_t))

        if xyz0.shape[0] > 0:
            order = torch.linspace(0, xyz0.shape[0] - 1, steps=min(10, xyz0.shape[0]), device=xyz0.device).long()
            src_sample = xyz0[order]
            dst_sample = target_xyz[order]
            for step in range(1, support_steps + 1, 2):
                frac = step / float(support_steps + 1)
                support_parts.append(torch.round(src_sample * (1.0 - frac) + dst_sample * frac))

        if support_parts:
            support_xyz = torch.cat(support_parts, dim=0).to(coords.dtype)
            support_coords = torch.cat([batch.expand(support_xyz.shape[0], 1).to(coords.dtype), support_xyz], dim=1)
            support_coords = torch.unique(support_coords, dim=0)
            valid_support = clip_valid(support_coords, limit)
            support_coords = support_coords[valid_support]
            if support_coords.shape[0] > max_support_tokens:
                keep = torch.linspace(0, support_coords.shape[0] - 1, steps=max_support_tokens, device=support_coords.device).long()
                support_coords = support_coords[keep]
            if support_coords.shape[0] > 0:
                all_coords.append(support_coords)
                all_feats.append(mean_feat.expand(support_coords.shape[0], -1))

    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def radial_frontier_attached_clone(st, limit, fraction=0.18, scale=0.82, bridge_steps=6):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    center = (xyz.min(0).values + xyz.max(0).values) / 2
    rel = xyz - center
    ax0, ax1 = lateral_axes()
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2)
    height = growth_height(xyz)
    frontier = lateral >= torch.quantile(lateral, 1.0 - fraction)
    cap = height >= torch.quantile(height, 0.55)
    mask = frontier & cap
    if mask.sum() < 16:
        mask = frontier
    targets = []
    rel_m = rel[mask]
    for k in range(1, 4):
        target = rel_m.clone()
        if k == 1:
            target[:, ax0], target[:, ax1] = -rel_m[:, ax1], rel_m[:, ax0]
        elif k == 2:
            target[:, ax0], target[:, ax1] = -rel_m[:, ax0], -rel_m[:, ax1]
        else:
            target[:, ax0], target[:, ax1] = rel_m[:, ax1], -rel_m[:, ax0]
        target[:, GROWTH_AXIS] = rel_m[:, GROWTH_AXIS] * 0.92
        targets.append(torch.round(target * scale + center))
    return attached_transform_masked_copies(st, mask, targets, limit, bridge_steps=bridge_steps)


def ornament_crown_buds(st, limit, fraction=0.14, shift_ratio=0.10, bridge_steps=7):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2)
    height = growth_height(xyz)
    mask = (lateral >= torch.quantile(lateral, 1.0 - fraction)) & (
        height >= torch.quantile(height, 0.50)
    )
    if mask.sum() < 16:
        mask = lateral >= torch.quantile(lateral, 1.0 - fraction)
    src_xyz = xyz[mask]
    src_rel = rel[mask]
    radial_norm = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = src_rel[:, ax0] / radial_norm
    radial[:, ax1] = src_rel[:, ax1] / radial_norm
    upward = torch.zeros_like(src_rel)
    upward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    delta = radial * extent * shift_ratio + upward * extent * shift_ratio * 0.45
    targets = [torch.round(src_xyz + delta), torch.round(src_xyz + delta * 0.62)]
    return attached_transform_masked_copies(st, mask, targets, limit, bridge_steps=bridge_steps)


def ornament_rim_micro_buds(st, limit, fraction=0.08, shift_ratio=0.055, bridge_steps=8):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2)
    height = growth_height(xyz)
    rim = lateral >= torch.quantile(lateral, 1.0 - fraction)
    cap = height >= torch.quantile(height, 0.62)
    mask = rim & cap
    if mask.sum() < 16:
        mask = rim
    src_xyz = xyz[mask]
    src_rel = rel[mask]
    radial_norm = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = src_rel[:, ax0] / radial_norm
    radial[:, ax1] = src_rel[:, ax1] / radial_norm
    upward = torch.zeros_like(src_rel)
    upward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    # Narrow, attached beads: enough to read recursive ornament detail without
    # duplicating the entire crown shell.
    delta = radial * extent * shift_ratio + upward * extent * shift_ratio * 0.35
    targets = [torch.round(src_xyz + delta)]
    return attached_transform_masked_copies(st, mask, targets, limit, bridge_steps=bridge_steps)


def arch_keystone_buds(st, limit, fraction=0.18, shift_ratio=0.10, bridge_steps=7):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    lateral_abs = torch.abs(rel[:, ax0])
    depth_abs = torch.abs(rel[:, ax1])
    top = height >= torch.quantile(height, 1.0 - fraction)
    centered = lateral_abs <= torch.quantile(lateral_abs, 0.62)
    readable_depth = depth_abs >= torch.quantile(depth_abs, 0.35)
    mask = top & centered & readable_depth
    if mask.sum() < 16:
        mask = top
    src_xyz = xyz[mask]
    src_rel = rel[mask]
    targets = []
    for sign in (-1, 1):
        delta = torch.zeros_like(src_rel)
        delta[:, ax0] = sign * extent[ax0] * shift_ratio * 0.50
        delta[:, GROWTH_AXIS] = float(GROWTH_SIGN) * extent[GROWTH_AXIS] * shift_ratio
        delta[:, ax1] = torch.sign(src_rel[:, ax1]).clamp(min=-1, max=1) * extent[ax1] * shift_ratio * 0.22
        targets.append(torch.round(src_xyz + delta))
    return attached_transform_masked_copies(st, mask, targets, limit, bridge_steps=bridge_steps)


def socket_translate_attached_clone(st, limit, fraction=0.22, shift_ratio=0.16, bridge_steps=6):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, _ = lateral_axes()
    side = xyz[:, ax0] >= torch.quantile(xyz[:, ax0], 1.0 - fraction)
    high = growth_height(xyz) >= torch.quantile(growth_height(xyz), 0.35)
    mask = side & high
    if mask.sum() < 16:
        mask = side
    target = xyz[mask].clone()
    target[:, ax0] += extent[ax0] * shift_ratio
    target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * extent[GROWTH_AXIS] * shift_ratio * 0.18
    return attached_transform_masked_copies(st, mask, [torch.round(target)], limit, bridge_steps=bridge_steps)


def socket_translate_tight_attached_clone(st, limit, fraction=0.12, shift_ratio=0.10, bridge_steps=8):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    side = xyz[:, ax0] >= torch.quantile(xyz[:, ax0], 1.0 - fraction)
    mid_height = growth_height(xyz) >= torch.quantile(growth_height(xyz), 0.42)
    readable_depth = torch.abs(xyz[:, ax1] - torch.median(xyz[:, ax1])) >= torch.quantile(
        torch.abs(xyz[:, ax1] - torch.median(xyz[:, ax1])), 0.18
    )
    mask = side & mid_height & readable_depth
    if mask.sum() < 16:
        mask = side & mid_height
    if mask.sum() < 16:
        mask = side
    target = xyz[mask].clone()
    target[:, ax0] += extent[ax0] * shift_ratio
    target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * extent[GROWTH_AXIS] * shift_ratio * 0.08
    return attached_transform_masked_copies(st, mask, [torch.round(target)], limit, bridge_steps=bridge_steps)


def crown_rim_gem_array_20260511j(st, limit, fraction=0.055, shift_ratio=0.045, bridge_steps=12):
    """Small repeated rim gems/spikes for crown-like roots.

    The older crown frontier operators could copy too much of the shell.  This
    keeps only a narrow upper rim mask and pushes it radially/upward by a short
    distance, which makes the recursion visible without turning the crown into
    a duplicated disk.
    """

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2).clamp_min(1e-6)
    height = growth_height(xyz)
    rim = lateral >= torch.quantile(lateral, 1.0 - fraction)
    cap = height >= torch.quantile(height, 0.54)
    mask = rim & cap
    if mask.sum() < 16:
        mask = rim
    if mask.sum() < 16:
        return st
    src_xyz = xyz[mask]
    src_rel = rel[mask]
    radial_norm = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = src_rel[:, ax0] / radial_norm
    radial[:, ax1] = src_rel[:, ax1] / radial_norm
    upward = torch.zeros_like(src_rel)
    upward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    targets = [
        torch.round(src_xyz + radial * extent * shift_ratio + upward * extent * shift_ratio * 0.48),
        torch.round(src_xyz + radial * extent * shift_ratio * 0.62 + upward * extent * shift_ratio * 0.82),
    ]
    return attached_transform_masked_copies(st, mask, targets, limit, bridge_steps=bridge_steps)


def mecha_socket_fin_array_20260511j(st, limit, fraction=0.105, shift_ratio=0.075, bridge_steps=12):
    """Attached hard-surface fins/modules from side sockets.

    This is a visual-first version of the socket grammar.  It selects a tight
    side-panel band and grows two short attached module rows, making mecha/tank
    structures read as repeated manufactured parts instead of random debris.
    """

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    side_high = xyz[:, ax0] >= torch.quantile(xyz[:, ax0], 1.0 - fraction)
    side_low = xyz[:, ax0] <= torch.quantile(xyz[:, ax0], fraction)
    mid_height = growth_height(xyz) >= torch.quantile(growth_height(xyz), 0.28)
    mid_depth = torch.abs(xyz[:, ax1] - torch.median(xyz[:, ax1]))
    readable_depth = mid_depth >= torch.quantile(mid_depth, 0.12)
    masks = []
    for side in (side_high, side_low):
        mask = side & mid_height & readable_depth
        if mask.sum() < 16:
            mask = side & mid_height
        if mask.sum() >= 16:
            masks.append(mask)
    if not masks:
        return st
    all_masks = masks[0]
    for m in masks[1:]:
        all_masks = all_masks | m
    src_xyz = xyz[all_masks]
    rel_side = torch.sign(src_xyz[:, ax0] - torch.median(xyz[:, ax0])).clamp(min=-1, max=1)
    side_vec = torch.zeros_like(src_xyz)
    side_vec[:, ax0] = rel_side
    up_vec = torch.zeros_like(src_xyz)
    up_vec[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    depth_vec = torch.zeros_like(src_xyz)
    depth_vec[:, ax1] = torch.sign(src_xyz[:, ax1] - torch.median(xyz[:, ax1])).clamp(min=-1, max=1)
    targets = [
        torch.round(src_xyz + side_vec * extent * shift_ratio + up_vec * extent * shift_ratio * 0.20),
        torch.round(src_xyz + side_vec * extent * shift_ratio * 0.72 + depth_vec * extent * shift_ratio * 0.44 + up_vec * extent * shift_ratio * 0.10),
    ]
    return attached_transform_masked_copies(st, all_masks, targets, limit, bridge_steps=bridge_steps)


def city_rooftop_tower_array_20260511j(st, limit, fraction=0.18, scale=0.54, bridge_steps=12):
    """Nested rooftop towers for city/LOD roots."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    height = growth_height(xyz)
    top = height >= torch.quantile(height, 1.0 - fraction)
    if top.sum() < 16:
        top = height >= torch.quantile(height, 0.70)
    if top.sum() < 16:
        return st
    src_xyz = xyz[top]
    rel = src_xyz - center
    target = center + rel * scale
    target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * extent[GROWTH_AXIS] * 0.16
    st = attached_transform_masked_copies(st, top, [torch.round(target)], limit, bridge_steps=bridge_steps)
    return rooftop_scale_buds(st, limit, fraction=max(0.10, fraction * 0.75), scale=scale * 0.92, bridge_steps=bridge_steps)


def castle_turret_battlement_20260511j(st, limit, fraction=0.16, shift_ratio=0.075, bridge_steps=12):
    """Top-corner turret/battlement buds for castle/fortress roots."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    top = height >= torch.quantile(height, 1.0 - fraction)
    corner_score = torch.abs(rel[:, ax0]) / extent[ax0].clamp_min(1) + torch.abs(rel[:, ax1]) / extent[ax1].clamp_min(1)
    corners = corner_score >= torch.quantile(corner_score, 0.72)
    mask = top & corners
    if mask.sum() < 16:
        mask = top
    if mask.sum() < 16:
        return st
    src_xyz = xyz[mask]
    src_rel = rel[mask]
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = torch.sign(src_rel[:, ax0]).clamp(min=-1, max=1)
    radial[:, ax1] = torch.sign(src_rel[:, ax1]).clamp(min=-1, max=1)
    upward = torch.zeros_like(src_rel)
    upward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    targets = [
        torch.round(src_xyz + upward * extent * shift_ratio + radial * extent * shift_ratio * 0.30),
        torch.round(src_xyz + upward * extent * shift_ratio * 0.55 + radial * extent * shift_ratio * 0.62),
    ]
    return attached_transform_masked_copies(st, mask, targets, limit, bridge_steps=bridge_steps)


def crown_rim_gem_clean_20260511k(st, limit):
    return crown_rim_gem_array_20260511j(st, limit, fraction=0.030, shift_ratio=0.026, bridge_steps=18)


def mecha_socket_fin_clean_20260511k(st, limit):
    return mecha_socket_fin_array_20260511j(st, limit, fraction=0.052, shift_ratio=0.040, bridge_steps=18)


def city_rooftop_tower_clean_20260511k(st, limit):
    return city_rooftop_tower_array_20260511j(st, limit, fraction=0.095, scale=0.66, bridge_steps=18)


def castle_turret_clean_20260511k(st, limit):
    return castle_turret_battlement_20260511j(st, limit, fraction=0.070, shift_ratio=0.035, bridge_steps=18)


def city_roof_podium_20260511l(st, limit, fraction=0.070, scale=0.42, lift_ratio=0.115, bridge_steps=24):
    """Low-complexity city recursion from a single roof podium.

    The 20260511j/k city operators selected a broad top frontier. On detailed
    building roots that frontier contains facade/window dust, so the decoded
    result is connected but visually mottled. This operator is deliberately
    narrower: it selects the central high roof tokens and grows one compact
    podium/tower upward from that roof.
    """

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    top = height >= torch.quantile(height, 1.0 - fraction)
    lateral = torch.sqrt((rel[:, ax0] / extent[ax0].clamp_min(1)) ** 2 + (rel[:, ax1] / extent[ax1].clamp_min(1)) ** 2)
    central = lateral <= torch.quantile(lateral, 0.42)
    mask = top & central
    if mask.sum() < 18:
        mask = height >= torch.quantile(height, 0.86)
    if mask.sum() < 18:
        return st
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    target_rel = src_rel.clone()
    target_rel[:, ax0] *= scale
    target_rel[:, ax1] *= scale
    target_rel[:, GROWTH_AXIS] *= 0.76
    lift = torch.zeros_like(src_rel)
    lift[:, GROWTH_AXIS] = float(GROWTH_SIGN) * extent[GROWTH_AXIS] * lift_ratio
    target = center + target_rel + lift
    return attached_transform_masked_copies(st, mask, [torch.round(target)], limit, bridge_steps=bridge_steps)


def city_roof_corner_towers_20260511l(st, limit, fraction=0.080, scale=0.50, lift_ratio=0.090, bridge_steps=24):
    """Four-corner rooftop tower handles for clean low-poly city roots."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    top = height >= torch.quantile(height, 1.0 - fraction)
    corner_score = torch.abs(rel[:, ax0]) / extent[ax0].clamp_min(1) + torch.abs(rel[:, ax1]) / extent[ax1].clamp_min(1)
    corners = corner_score >= torch.quantile(corner_score, 0.86)
    mask = top & corners
    if mask.sum() < 18:
        mask = top & (corner_score >= torch.quantile(corner_score, 0.76))
    if mask.sum() < 18:
        return st
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = torch.sign(src_rel[:, ax0]).clamp(min=-1, max=1)
    radial[:, ax1] = torch.sign(src_rel[:, ax1]).clamp(min=-1, max=1)
    target_rel = src_rel.clone()
    target_rel[:, ax0] *= scale
    target_rel[:, ax1] *= scale
    target_rel[:, GROWTH_AXIS] *= 0.82
    lift = torch.zeros_like(src_rel)
    lift[:, GROWTH_AXIS] = float(GROWTH_SIGN) * extent[GROWTH_AXIS] * lift_ratio
    target = center + target_rel + lift + radial * extent * 0.020
    return attached_transform_masked_copies(st, mask, [torch.round(target)], limit, bridge_steps=bridge_steps)


def castle_turret_caps_20260511l(st, limit, fraction=0.060, shift_ratio=0.048, bridge_steps=24):
    """Grow clean recursive turret caps from only the highest corner handles."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    top = height >= torch.quantile(height, 1.0 - fraction)
    corner_score = torch.abs(rel[:, ax0]) / extent[ax0].clamp_min(1) + torch.abs(rel[:, ax1]) / extent[ax1].clamp_min(1)
    corners = corner_score >= torch.quantile(corner_score, 0.82)
    mask = top & corners
    if mask.sum() < 18:
        mask = top
    if mask.sum() < 18:
        return st
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = torch.sign(src_rel[:, ax0]).clamp(min=-1, max=1)
    radial[:, ax1] = torch.sign(src_rel[:, ax1]).clamp(min=-1, max=1)
    upward = torch.zeros_like(src_rel)
    upward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    targets = [
        torch.round(src_xyz + upward * extent * shift_ratio + radial * extent * shift_ratio * 0.24),
        torch.round(src_xyz + upward * extent * shift_ratio * 1.35 + radial * extent * shift_ratio * 0.12),
    ]
    return attached_transform_masked_copies(st, mask, targets, limit, bridge_steps=bridge_steps)


def castle_battlement_strip_20260511l(st, limit, fraction=0.050, shift_ratio=0.034, bridge_steps=24):
    """Small top-strip battlements, excluding most wall/facade sparse tokens."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    top = height >= torch.quantile(height, 1.0 - fraction)
    edge_score = torch.maximum(torch.abs(rel[:, ax0]) / extent[ax0].clamp_min(1), torch.abs(rel[:, ax1]) / extent[ax1].clamp_min(1))
    edge = edge_score >= torch.quantile(edge_score, 0.72)
    mask = top & edge
    if mask.sum() < 18:
        mask = top
    if mask.sum() < 18:
        return st
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    upward = torch.zeros_like(src_rel)
    upward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    target = src_xyz + upward * extent * shift_ratio
    return attached_transform_masked_copies(st, mask, [torch.round(target)], limit, bridge_steps=bridge_steps)


def mecha_socket_pods_20260511l(st, limit):
    """Readable shallow hard-surface modules for visual-first mechanical roots."""

    return mecha_socket_fin_array_20260511j(st, limit, fraction=0.075, shift_ratio=0.058, bridge_steps=22)


def cap_mask_by_score(mask, score, max_tokens):
    """Keep the strongest selected sparse tokens so macro stamps stay bounded."""

    import torch

    idx = torch.nonzero(mask, as_tuple=False).flatten()
    if idx.numel() <= max_tokens:
        return mask
    keep = idx[torch.topk(score[idx], k=max_tokens, largest=True).indices]
    capped = torch.zeros_like(mask)
    capped[keep] = True
    return capped


def city_macro_tower_stack_20260511m(
    st,
    limit,
    scale=0.58,
    lift_ratio=0.20,
    max_source_tokens=96,
    bridge_steps=18,
):
    """Large nested tower body for visual-first city recursion.

    The 11l city operators were clean but frequently collided with the source
    roof, leaving token counts unchanged. This operator copies a bounded upper
    body mask and lifts the child tower far enough to read as a nested module.
    """

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    lateral = torch.sqrt((rel[:, ax0] / extent[ax0].clamp_min(1)) ** 2 + (rel[:, ax1] / extent[ax1].clamp_min(1)) ** 2)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)

    upper_body = (height >= torch.quantile(height, 0.68)) & (height <= torch.quantile(height, 0.985))
    central = lateral <= torch.quantile(lateral, 0.46)
    mask = upper_body & central
    if mask.sum() < 24:
        mask = (height >= torch.quantile(height, 0.78)) & (lateral <= torch.quantile(lateral, 0.60))
    if mask.sum() < 18:
        return st

    score = height_norm - lateral
    mask = cap_mask_by_score(mask, score, max_source_tokens)
    src_xyz = xyz[mask]
    anchor = src_xyz.mean(0, keepdim=True)
    target = anchor + (src_xyz - anchor) * scale
    target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * extent[GROWTH_AXIS] * lift_ratio
    return attached_transform_masked_copies(st, mask, [torch.round(target)], limit, bridge_steps=bridge_steps)


def city_quadrant_tower_stamps_20260511m(
    st,
    limit,
    scale=0.42,
    lift_ratio=0.16,
    max_source_tokens=56,
    bridge_steps=14,
):
    """Stamp one clean upper-city source into four visibly separated quadrants."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    lateral = torch.sqrt((rel[:, ax0] / extent[ax0].clamp_min(1)) ** 2 + (rel[:, ax1] / extent[ax1].clamp_min(1)) ** 2)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)

    mask = (height >= torch.quantile(height, 0.62)) & (lateral <= torch.quantile(lateral, 0.40))
    if mask.sum() < 20:
        mask = (height >= torch.quantile(height, 0.70)) & (lateral <= torch.quantile(lateral, 0.55))
    if mask.sum() < 18:
        return st

    score = height_norm - lateral * 0.7
    mask = cap_mask_by_score(mask, score, max_source_tokens)
    src_xyz = xyz[mask]
    anchor = src_xyz.mean(0, keepdim=True)
    base = anchor + (src_xyz - anchor) * scale
    upward = torch.zeros_like(base)
    upward[:, GROWTH_AXIS] = float(GROWTH_SIGN) * extent[GROWTH_AXIS] * lift_ratio

    targets = []
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            offset = torch.zeros_like(base)
            offset[:, ax0] = sx * extent[ax0] * 0.28
            offset[:, ax1] = sy * extent[ax1] * 0.22
            targets.append(torch.round(base + upward + offset))
    return attached_transform_masked_copies(st, mask, targets, limit, bridge_steps=bridge_steps)


def castle_macro_turret_stack_20260511m(
    st,
    limit,
    scale=0.62,
    lift_ratio=0.18,
    radial_ratio=0.05,
    max_source_tokens=96,
    bridge_steps=18,
):
    """Grow larger recursive turret bodies instead of tiny top-cap strips."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    corner_score = torch.abs(rel[:, ax0]) / extent[ax0].clamp_min(1) + torch.abs(rel[:, ax1]) / extent[ax1].clamp_min(1)

    mask = (height >= torch.quantile(height, 0.58)) & (corner_score >= torch.quantile(corner_score, 0.72))
    if mask.sum() < 20:
        mask = (height >= torch.quantile(height, 0.70)) & (corner_score >= torch.quantile(corner_score, 0.62))
    if mask.sum() < 18:
        return st

    score = height_norm + corner_score
    mask = cap_mask_by_score(mask, score, max_source_tokens)
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    sign0 = torch.sign(src_rel[:, ax0]).clamp(min=-1, max=1)
    sign1 = torch.sign(src_rel[:, ax1]).clamp(min=-1, max=1)
    sign0 = torch.where(sign0 == 0, torch.ones_like(sign0), sign0)
    sign1 = torch.where(sign1 == 0, torch.ones_like(sign1), sign1)

    anchor = center.unsqueeze(0).repeat(src_xyz.shape[0], 1)
    anchor[:, ax0] += sign0 * extent[ax0] * 0.34
    anchor[:, ax1] += sign1 * extent[ax1] * 0.34
    anchor[:, GROWTH_AXIS] = torch.quantile(src_xyz[:, GROWTH_AXIS], 0.45)
    radial = torch.zeros_like(src_xyz)
    radial[:, ax0] = sign0 * extent[ax0] * radial_ratio
    radial[:, ax1] = sign1 * extent[ax1] * radial_ratio
    upward = torch.zeros_like(src_xyz)
    upward[:, GROWTH_AXIS] = float(GROWTH_SIGN) * extent[GROWTH_AXIS] * lift_ratio
    target = anchor + (src_xyz - anchor) * scale + upward + radial
    return attached_transform_masked_copies(st, mask, [torch.round(target)], limit, bridge_steps=bridge_steps)


def castle_battlement_crown_20260511m(
    st,
    limit,
    lift_ratio=0.11,
    radial_ratio=0.035,
    max_source_tokens=120,
    bridge_steps=16,
):
    """Lift a top edge band into a readable recursive battlement crown."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    edge_score = torch.maximum(torch.abs(rel[:, ax0]) / extent[ax0].clamp_min(1), torch.abs(rel[:, ax1]) / extent[ax1].clamp_min(1))
    corner_score = torch.abs(rel[:, ax0]) / extent[ax0].clamp_min(1) + torch.abs(rel[:, ax1]) / extent[ax1].clamp_min(1)

    mask = (height >= torch.quantile(height, 0.74)) & (edge_score >= torch.quantile(edge_score, 0.66)) & (corner_score < torch.quantile(corner_score, 0.92))
    if mask.sum() < 18:
        mask = (height >= torch.quantile(height, 0.72)) & (edge_score >= torch.quantile(edge_score, 0.60))
    if mask.sum() < 18:
        return st

    score = height_norm + edge_score - corner_score * 0.15
    mask = cap_mask_by_score(mask, score, max_source_tokens)
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    radial = torch.zeros_like(src_xyz)
    radial[:, ax0] = torch.sign(src_rel[:, ax0]).clamp(min=-1, max=1) * extent[ax0] * radial_ratio
    radial[:, ax1] = torch.sign(src_rel[:, ax1]).clamp(min=-1, max=1) * extent[ax1] * radial_ratio
    upward = torch.zeros_like(src_xyz)
    upward[:, GROWTH_AXIS] = float(GROWTH_SIGN) * extent[GROWTH_AXIS] * lift_ratio
    target = src_xyz + upward + radial
    return attached_transform_masked_copies(st, mask, [torch.round(target)], limit, bridge_steps=bridge_steps)


def whole_root_nested_stack_20260511n(
    st,
    limit,
    scale=0.45,
    lift_ratio=0.26,
    bridge_steps=4,
):
    """Copy the whole root as one smaller child module.

    11m proved that macroscopic recursion is needed, but local sparse masks
    decoded as thin facade-like sheets. Whole-root transforms preserve a coherent
    latent shape token neighborhood, trading some purity for visual stability.
    """

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    target = center + (xyz - center) * scale
    target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * extent[GROWTH_AXIS] * lift_ratio
    return attached_transform_copies(st, [torch.round(target)], limit, bridge_steps=bridge_steps)


def whole_root_twin_stamps_20260511n(
    st,
    limit,
    scale=0.30,
    lift_ratio=0.20,
    offset_ratio=0.24,
    bridge_steps=3,
):
    """Stamp two smaller whole-root children on opposite lateral anchors."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, _ = lateral_axes()
    base = center + (xyz - center) * scale
    upward = torch.zeros_like(base)
    upward[:, GROWTH_AXIS] = float(GROWTH_SIGN) * extent[GROWTH_AXIS] * lift_ratio
    targets = []
    for sx in (-1.0, 1.0):
        offset = torch.zeros_like(base)
        offset[:, ax0] = sx * extent[ax0] * offset_ratio
        targets.append(torch.round(base + upward + offset))
    return attached_transform_copies(st, targets, limit, bridge_steps=bridge_steps)


def whole_root_single_corner_stamp_20260511n(
    st,
    limit,
    scale=0.34,
    lift_ratio=0.22,
    offset_ratio=0.20,
    bridge_steps=3,
):
    """One whole-root child stamp for a cleaner diagnostic when twins fragment."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    base = center + (xyz - center) * scale
    offset = torch.zeros_like(base)
    offset[:, ax0] = extent[ax0] * offset_ratio
    offset[:, ax1] = extent[ax1] * offset_ratio * 0.45
    offset[:, GROWTH_AXIS] = float(GROWTH_SIGN) * extent[GROWTH_AXIS] * lift_ratio
    return attached_transform_copies(st, [torch.round(base + offset)], limit, bridge_steps=bridge_steps)


def whole_root_rooftop_child_20260511o(
    st,
    limit,
    scale=0.36,
    lift_ratio=0.58,
    bridge_steps=1,
):
    """Place a coherent smaller root on the semantic roof/top side.

    11n copied the whole root but left the child too deeply embedded in the
    parent, which read as a box/shell artifact in controlled renders.  For
    z-up input meshes the launcher should use SLat growth frame y-, and this
    operator offsets the child far enough to sit on the top while preserving a
    small overlap for contact.
    """

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    target = center + (xyz - center) * scale
    target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * extent[GROWTH_AXIS] * lift_ratio
    return attached_transform_copies(st, [torch.round(target)], limit, bridge_steps=bridge_steps)


def whole_root_rooftop_twins_20260511o(
    st,
    limit,
    scale=0.26,
    lift_ratio=0.54,
    offset_ratio=0.23,
    bridge_steps=1,
):
    """Place two coherent child roots on top-side lateral anchors."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, _ = lateral_axes()
    base = center + (xyz - center) * scale
    targets = []
    for sx in (-1.0, 1.0):
        offset = torch.zeros_like(base)
        offset[:, ax0] = sx * extent[ax0] * offset_ratio
        offset[:, GROWTH_AXIS] = float(GROWTH_SIGN) * extent[GROWTH_AXIS] * lift_ratio
        targets.append(torch.round(base + offset))
    return attached_transform_copies(st, targets, limit, bridge_steps=bridge_steps)


def whole_root_rooftop_corner_cluster_20260511o(
    st,
    limit,
    scale=0.22,
    lift_ratio=0.52,
    offset0_ratio=0.24,
    offset1_ratio=0.18,
    bridge_steps=1,
):
    """Place four smaller child modules on top/corner anchors."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    base = center + (xyz - center) * scale
    targets = []
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            offset = torch.zeros_like(base)
            offset[:, ax0] = sx * extent[ax0] * offset0_ratio
            offset[:, ax1] = sy * extent[ax1] * offset1_ratio
            offset[:, GROWTH_AXIS] = float(GROWTH_SIGN) * extent[GROWTH_AXIS] * lift_ratio
            targets.append(torch.round(base + offset))
    return attached_transform_copies(st, targets, limit, bridge_steps=bridge_steps)


def mecha_socket_cluster_20260511o(st, limit):
    """Conservative socket modules for restored-frame mechanical showcase."""

    return mecha_socket_fin_array_20260511j(st, limit, fraction=0.060, shift_ratio=0.050, bridge_steps=14)


def whole_root_rooftop_child_with_support_20260511p(
    st,
    limit,
    scale=0.34,
    lift_ratio=0.46,
    support_scale=0.40,
    support_lift_ratio=0.30,
    max_support_tokens=72,
    support_bridge_steps=8,
):
    """Coherent single child plus narrow support tokens for cleaner visuals.

    11o depth-1 proved that a single coherent rooftop child reads well, but the
    child often floats above a dark roof gap and carries small high-frequency
    fragments.  This 11p operator keeps the whole-root child as one coherent
    sparse copy, then adds only a capped central roof mask as a support band.
    It avoids interpolating the whole root through many bridge steps, which was
    the source of earlier box/sheet artifacts.
    """

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    lateral = torch.sqrt((rel[:, ax0] / extent[ax0].clamp_min(1)) ** 2 + (rel[:, ax1] / extent[ax1].clamp_min(1)) ** 2)

    child_target = center + (xyz - center) * scale
    child_target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * extent[GROWTH_AXIS] * lift_ratio

    support_mask = (height >= torch.quantile(height, 0.78)) & (lateral <= torch.quantile(lateral, 0.36))
    if support_mask.sum() < 18:
        support_mask = (height >= torch.quantile(height, 0.70)) & (lateral <= torch.quantile(lateral, 0.48))
    if support_mask.sum() >= 18:
        support_score = height_norm - lateral
        support_mask = cap_mask_by_score(support_mask, support_score, max_support_tokens)

    all_coords = [coords]
    all_feats = [st.feats]

    child_coords = torch.cat([coords[:, :1], torch.round(child_target).to(coords.dtype)], dim=1)
    child_valid = clip_valid(child_coords, limit)
    if child_valid.sum() > 0:
        all_coords.append(child_coords[child_valid])
        all_feats.append(st.feats.clone()[child_valid])

    if support_mask.sum() >= 18:
        src_coords = coords[support_mask]
        src_feats = st.feats[support_mask].clone()
        src_xyz = src_coords[:, 1:].float()
        support_target = center + (src_xyz - center) * support_scale
        support_target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * extent[GROWTH_AXIS] * support_lift_ratio
        for step in range(1, support_bridge_steps + 1):
            frac = step / float(support_bridge_steps)
            interp = torch.round(src_xyz * (1.0 - frac) + support_target * frac).to(coords.dtype)
            bridge = torch.cat([src_coords[:, :1], interp], dim=1)
            valid = clip_valid(bridge, limit)
            if valid.sum() > 0:
                all_coords.append(bridge[valid])
                all_feats.append(src_feats[valid])

    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def whole_root_rooftop_child_tight_20260511p(st, limit):
    return whole_root_rooftop_child_with_support_20260511p(
        st,
        limit,
        scale=0.30,
        lift_ratio=0.42,
        support_scale=0.34,
        support_lift_ratio=0.25,
        max_support_tokens=56,
        support_bridge_steps=7,
    )


def whole_root_rooftop_child_readable_20260511p(st, limit):
    return whole_root_rooftop_child_with_support_20260511p(
        st,
        limit,
        scale=0.36,
        lift_ratio=0.48,
        support_scale=0.44,
        support_lift_ratio=0.31,
        max_support_tokens=80,
        support_bridge_steps=8,
    )


def whole_root_rooftop_child_aligned_20260511q(
    st,
    limit,
    scale=0.28,
    contact_overlap_ratio=0.045,
    support_scale=0.34,
    support_overlap_ratio=0.030,
    max_support_tokens=112,
    support_bridge_steps=11,
):
    """Bottom-align a compact whole-root child to the parent roof band.

    11p reduced fragmentation but still placed the child by bbox-center plus a
    lift.  For tall city/castle roots that can decode as a side/front graft.
    This operator computes the child bottom in the semantic growth-height
    coordinate and aligns it just inside the parent roof band before adding a
    broader central support mask.
    """

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    lateral = torch.sqrt((rel[:, ax0] / extent[ax0].clamp_min(1)) ** 2 + (rel[:, ax1] / extent[ax1].clamp_min(1)) ** 2)
    top_h = torch.quantile(height, 0.90)

    child_target = center + rel * scale
    child_height = growth_height(child_target)
    child_delta_h = top_h - child_height.min() - extent[GROWTH_AXIS].float() * contact_overlap_ratio
    child_target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * child_delta_h

    support_mask = (height >= torch.quantile(height, 0.84)) & (lateral <= torch.quantile(lateral, 0.52))
    if support_mask.sum() < 24:
        support_mask = (height >= torch.quantile(height, 0.76)) & (lateral <= torch.quantile(lateral, 0.62))
    if support_mask.sum() >= 24:
        support_score = height_norm - 0.55 * lateral
        support_mask = cap_mask_by_score(support_mask, support_score, max_support_tokens)

    all_coords = [coords]
    all_feats = [st.feats]

    child_coords = torch.cat([coords[:, :1], torch.round(child_target).to(coords.dtype)], dim=1)
    child_valid = clip_valid(child_coords, limit)
    if child_valid.sum() > 0:
        all_coords.append(child_coords[child_valid])
        all_feats.append(st.feats.clone()[child_valid])

    if support_mask.sum() >= 24:
        src_coords = coords[support_mask]
        src_feats = st.feats[support_mask].clone()
        src_xyz = src_coords[:, 1:].float()
        src_rel = src_xyz - center
        support_target = center + src_rel * support_scale
        support_height = growth_height(support_target)
        support_delta_h = top_h - support_height.min() - extent[GROWTH_AXIS].float() * support_overlap_ratio
        support_target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * support_delta_h
        for step in range(1, support_bridge_steps + 1):
            frac = step / float(support_bridge_steps)
            interp = torch.round(src_xyz * (1.0 - frac) + support_target * frac).to(coords.dtype)
            bridge = torch.cat([src_coords[:, :1], interp], dim=1)
            valid = clip_valid(bridge, limit)
            if valid.sum() > 0:
                all_coords.append(bridge[valid])
                all_feats.append(src_feats[valid])

    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def whole_root_city_rooftop_stack_aligned_20260511q(st, limit):
    return whole_root_rooftop_child_aligned_20260511q(
        st,
        limit,
        scale=0.28,
        contact_overlap_ratio=0.045,
        support_scale=0.34,
        support_overlap_ratio=0.030,
        max_support_tokens=112,
        support_bridge_steps=11,
    )


def whole_root_castle_rooftop_stack_aligned_20260511q(st, limit):
    return whole_root_rooftop_child_aligned_20260511q(
        st,
        limit,
        scale=0.26,
        contact_overlap_ratio=0.050,
        support_scale=0.32,
        support_overlap_ratio=0.034,
        max_support_tokens=128,
        support_bridge_steps=12,
    )


def whole_root_rooftop_child_protruding_20260511r(
    st,
    limit,
    scale=0.23,
    contact_overlap_ratio=0.018,
    protrude_ratio=0.22,
    support_scale=0.30,
    support_overlap_ratio=0.010,
    max_support_tokens=144,
    support_bridge_steps=14,
):
    """Place a small whole-root child visibly above the roof band.

    11q bottom alignment improved the intended hierarchy in quick views but
    embedded the child too deeply for the controlled camera.  This version keeps
    a small child and explicitly offsets its semantic bottom beyond the roof
    plane so bbox growth and visual protrusion both become auditable.
    """

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    lateral = torch.sqrt((rel[:, ax0] / extent[ax0].clamp_min(1)) ** 2 + (rel[:, ax1] / extent[ax1].clamp_min(1)) ** 2)
    top_h = torch.quantile(height, 0.92)
    protrude = extent[GROWTH_AXIS].float() * protrude_ratio

    child_target = center + rel * scale
    child_height = growth_height(child_target)
    child_delta_h = top_h + protrude - child_height.min() - extent[GROWTH_AXIS].float() * contact_overlap_ratio
    child_target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * child_delta_h

    support_mask = (height >= torch.quantile(height, 0.80)) & (lateral <= torch.quantile(lateral, 0.58))
    if support_mask.sum() < 32:
        support_mask = (height >= torch.quantile(height, 0.70)) & (lateral <= torch.quantile(lateral, 0.70))
    if support_mask.sum() >= 32:
        support_score = height_norm - 0.45 * lateral
        support_mask = cap_mask_by_score(support_mask, support_score, max_support_tokens)

    all_coords = [coords]
    all_feats = [st.feats]

    child_coords = torch.cat([coords[:, :1], torch.round(child_target).to(coords.dtype)], dim=1)
    child_valid = clip_valid(child_coords, limit)
    if child_valid.sum() > 0:
        all_coords.append(child_coords[child_valid])
        all_feats.append(st.feats.clone()[child_valid])

    if support_mask.sum() >= 32:
        src_coords = coords[support_mask]
        src_feats = st.feats[support_mask].clone()
        src_xyz = src_coords[:, 1:].float()
        support_target = center + (src_xyz - center) * support_scale
        support_height = growth_height(support_target)
        support_delta_h = top_h + protrude * 0.52 - support_height.min() - extent[GROWTH_AXIS].float() * support_overlap_ratio
        support_target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * support_delta_h
        for step in range(1, support_bridge_steps + 1):
            frac = step / float(support_bridge_steps)
            interp = torch.round(src_xyz * (1.0 - frac) + support_target * frac).to(coords.dtype)
            bridge = torch.cat([src_coords[:, :1], interp], dim=1)
            valid = clip_valid(bridge, limit)
            if valid.sum() > 0:
                all_coords.append(bridge[valid])
                all_feats.append(src_feats[valid])

    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def whole_root_city_rooftop_stack_protruding_20260511r(st, limit):
    return whole_root_rooftop_child_protruding_20260511r(
        st,
        limit,
        scale=0.23,
        contact_overlap_ratio=0.018,
        protrude_ratio=0.22,
        support_scale=0.30,
        support_overlap_ratio=0.010,
        max_support_tokens=144,
        support_bridge_steps=14,
    )


def city_topbody_protruding_20260511s(
    st,
    limit,
    scale=0.46,
    protrude_ratio=0.14,
    contact_overlap_ratio=0.018,
    max_source_tokens=84,
    support_scale=0.44,
    max_support_tokens=96,
    bridge_steps=8,
):
    """Bounded upper-city module that protrudes above the semantic roof.

    11r showed that whole-root copying can make the top hierarchy visible in a
    quick view but still decode as a side/front graft under controlled cameras.
    This 11s city operator switches to a compact upper-body source mask while
    keeping the explicit roof protrusion and support bridge.
    """

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    lateral = torch.sqrt((rel[:, ax0] / extent[ax0].clamp_min(1)) ** 2 + (rel[:, ax1] / extent[ax1].clamp_min(1)) ** 2)

    top_h = torch.quantile(height, 0.92)
    body = (height >= torch.quantile(height, 0.56)) & (height <= torch.quantile(height, 0.90))
    central = lateral <= torch.quantile(lateral, 0.48)
    mask = body & central
    if mask.sum() < 24:
        mask = (height >= torch.quantile(height, 0.66)) & (lateral <= torch.quantile(lateral, 0.60))
    if mask.sum() < 18:
        return st

    score = height_norm - 0.65 * lateral
    mask = cap_mask_by_score(mask, score, max_source_tokens)
    src_coords = coords[mask]
    src_feats = st.feats[mask].clone()
    src_xyz = src_coords[:, 1:].float()
    target = center + (src_xyz - center) * scale
    target_height = growth_height(target)
    protrude = extent[GROWTH_AXIS].float() * protrude_ratio
    delta_h = top_h + protrude - target_height.min() - extent[GROWTH_AXIS].float() * contact_overlap_ratio
    target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * delta_h

    support_mask = (height >= torch.quantile(height, 0.72)) & (lateral <= torch.quantile(lateral, 0.62))
    if support_mask.sum() >= 24:
        support_mask = cap_mask_by_score(support_mask, height_norm - 0.50 * lateral, max_support_tokens)

    all_coords = [coords]
    all_feats = [st.feats]
    child_coords = torch.cat([src_coords[:, :1], torch.round(target).to(coords.dtype)], dim=1)
    valid = clip_valid(child_coords, limit)
    if valid.sum() > 0:
        all_coords.append(child_coords[valid])
        all_feats.append(src_feats[valid])

    if support_mask.sum() >= 24:
        support_coords = coords[support_mask]
        support_feats = st.feats[support_mask].clone()
        support_xyz = support_coords[:, 1:].float()
        support_target = center + (support_xyz - center) * support_scale
        support_height = growth_height(support_target)
        support_delta_h = top_h + protrude * 0.46 - support_height.min()
        support_target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * support_delta_h
        for step in range(1, bridge_steps + 1):
            frac = step / float(bridge_steps)
            interp = torch.round(support_xyz * (1.0 - frac) + support_target * frac).to(coords.dtype)
            bridge = torch.cat([support_coords[:, :1], interp], dim=1)
            bridge_valid = clip_valid(bridge, limit)
            if bridge_valid.sum() > 0:
                all_coords.append(bridge[bridge_valid])
                all_feats.append(support_feats[bridge_valid])

    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def castle_cap_pair_protruding_20260511s(
    st,
    limit,
    scale=0.52,
    protrude_ratio=0.115,
    radial_ratio=0.015,
    max_source_tokens=80,
    bridge_steps=9,
):
    """Lift clean turret-cap tokens above their caps without side-grafting."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    corner_score = torch.abs(rel[:, ax0]) / extent[ax0].clamp_min(1) + torch.abs(rel[:, ax1]) / extent[ax1].clamp_min(1)
    top_h = torch.quantile(height, 0.92)

    mask = (height >= torch.quantile(height, 0.62)) & (corner_score >= torch.quantile(corner_score, 0.70))
    if mask.sum() < 20:
        mask = (height >= torch.quantile(height, 0.72)) & (corner_score >= torch.quantile(corner_score, 0.56))
    if mask.sum() < 18:
        return st

    score = height_norm + 0.50 * corner_score
    mask = cap_mask_by_score(mask, score, max_source_tokens)
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    sign0 = torch.sign(src_rel[:, ax0])
    sign1 = torch.sign(src_rel[:, ax1])
    sign0 = torch.where(sign0 == 0, torch.ones_like(sign0), sign0)
    sign1 = torch.where(sign1 == 0, torch.ones_like(sign1), sign1)

    anchor = center.unsqueeze(0).repeat(src_xyz.shape[0], 1)
    anchor[:, ax0] += sign0 * extent[ax0] * 0.34
    anchor[:, ax1] += sign1 * extent[ax1] * 0.34
    anchor[:, GROWTH_AXIS] = torch.quantile(src_xyz[:, GROWTH_AXIS], 0.42)
    target = anchor + (src_xyz - anchor) * scale
    radial = torch.zeros_like(target)
    radial[:, ax0] = sign0 * extent[ax0] * radial_ratio
    radial[:, ax1] = sign1 * extent[ax1] * radial_ratio
    target = target + radial
    target_height = growth_height(target)
    protrude = extent[GROWTH_AXIS].float() * protrude_ratio
    delta_h = top_h + protrude - target_height.min()
    target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * delta_h

    return attached_transform_masked_copies(st, mask, [torch.round(target)], limit, bridge_steps=bridge_steps)


def mecha_socket_pods_emphatic_20260511s(st, limit):
    """Slightly stronger attached socket modules for the 11s mechanical branch."""

    return mecha_socket_fin_array_20260511j(st, limit, fraction=0.085, shift_ratio=0.070, bridge_steps=16)


def solid_rooftop_child_20260511u(
    st,
    limit,
    scale=0.34,
    protrude_ratio=0.18,
    support_scale=0.38,
    support_ratio=0.08,
    max_source_tokens=160,
    support_steps=8,
):
    """Low-frequency solid single child for 11u city/castle roots.

    11t proved that pre-encoding root orientation helps the top hierarchy, but
    copied cap/body tokens still decoded as black holes and torn shell ends.
    This operator selects a broad central low-frequency source body and places
    one scaled copy above the roof, then inserts a compact support slab/tube
    from central roof tokens.  It intentionally avoids corner cap masks and
    thin battlement/top details.
    """

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    lateral = torch.sqrt((rel[:, ax0] / extent[ax0]) ** 2 + (rel[:, ax1] / extent[ax1]) ** 2)

    body = (height >= torch.quantile(height, 0.45)) & (height <= torch.quantile(height, 0.88))
    central = lateral <= torch.quantile(lateral, 0.58)
    mask = body & central
    if mask.sum() < 32:
        mask = (height >= torch.quantile(height, 0.35)) & (height <= torch.quantile(height, 0.92)) & (lateral <= torch.quantile(lateral, 0.70))
    if mask.sum() < 24:
        return st
    score = 0.70 * height_norm - 0.45 * lateral
    mask = cap_mask_by_score(mask, score, max_source_tokens)

    src_coords = coords[mask]
    src_feats = st.feats[mask].clone()
    src_xyz = src_coords[:, 1:].float()
    src_center = (src_xyz.min(0).values + src_xyz.max(0).values) / 2
    target = center + (src_xyz - src_center) * scale
    top_h = torch.quantile(height, 0.91)
    target_height = growth_height(target)
    delta_h = top_h + extent[GROWTH_AXIS].float() * protrude_ratio - target_height.min()
    target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * delta_h

    all_coords = [coords]
    all_feats = [st.feats]
    child_coords = torch.cat([src_coords[:, :1], torch.round(target).to(coords.dtype)], dim=1)
    valid = clip_valid(child_coords, limit)
    if valid.sum() > 0:
        all_coords.append(child_coords[valid])
        all_feats.append(src_feats[valid])

    support_mask = (height >= torch.quantile(height, 0.76)) & (lateral <= torch.quantile(lateral, 0.48))
    if support_mask.sum() >= 18:
        support_mask = cap_mask_by_score(support_mask, height_norm - 0.60 * lateral, 96)
        support_coords = coords[support_mask]
        support_feats = st.feats[support_mask].clone()
        support_xyz = support_coords[:, 1:].float()
        support_target = center + (support_xyz - center) * support_scale
        support_height = growth_height(support_target)
        support_delta_h = top_h + extent[GROWTH_AXIS].float() * support_ratio - support_height.min()
        support_target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * support_delta_h
        for step in range(1, support_steps + 1):
            frac = step / float(support_steps)
            interp = torch.round(support_xyz * (1.0 - frac) + support_target * frac).to(coords.dtype)
            bridge = torch.cat([support_coords[:, :1], interp], dim=1)
            bridge_valid = clip_valid(bridge, limit)
            if bridge_valid.sum() > 0:
                all_coords.append(bridge[bridge_valid])
                all_feats.append(support_feats[bridge_valid])

    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def solid_rooftop_child_large_20260511u(st, limit):
    return solid_rooftop_child_20260511u(
        st,
        limit,
        scale=0.38,
        protrude_ratio=0.20,
        support_scale=0.42,
        support_ratio=0.08,
        max_source_tokens=180,
        support_steps=8,
    )


def solid_rooftop_child_clean_20260511u(st, limit):
    return solid_rooftop_child_20260511u(
        st,
        limit,
        scale=0.30,
        protrude_ratio=0.16,
        support_scale=0.34,
        support_ratio=0.06,
        max_source_tokens=128,
        support_steps=6,
    )


def scale_down_attached_clone(st, limit, scale=0.72, bridge_steps=5):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    center = (xyz.min(0).values + xyz.max(0).values) / 2
    target = torch.round((xyz - center) * scale + center)
    return attached_transform_copies(st, [target], limit, bridge_steps=bridge_steps)


def rooftop_scale_buds(st, limit, fraction=0.24, scale=0.62, bridge_steps=7):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    height = growth_height(xyz)
    mask = height >= torch.quantile(height, 1.0 - fraction)
    if mask.sum() < 16:
        mask = height >= torch.quantile(height, 0.70)
    src_xyz = xyz[mask]
    target = (src_xyz - center) * scale + center
    target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * extent[GROWTH_AXIS] * 0.08
    return attached_transform_masked_copies(st, mask, [torch.round(target)], limit, bridge_steps=bridge_steps)


def leaf_basal_fan_attached_clone(
    st,
    limit,
    base_fraction=0.24,
    scale=0.72,
    lateral_ratio=0.15,
    upward_ratio=0.08,
    angle_degrees=26.0,
    bridge_steps=7,
):
    """Grow copied leaf clusters from a low central base anchor.

    The generic crown-tip operators extend the current high frontier, which is
    good for trees but wrong for spider-plant-like rosettes: new leaves should
    read as emerging from the basal crown/root.  This operator copies the whole
    sparse leaf module through a mild lateral fan transform while only bridging
    the low base tokens, so the duplicate remains attached without leaving a
    full-object interpolation trail.
    """

    import math
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    height = growth_height(xyz)
    base_mask = height <= torch.quantile(height, base_fraction)
    ax0, ax1 = lateral_axes()
    center = (lo.float() + hi.float()) / 2
    lateral = torch.sqrt((xyz[:, ax0] - center[ax0]) ** 2 + (xyz[:, ax1] - center[ax1]) ** 2)
    central = lateral <= torch.quantile(lateral, 0.72)
    mask = base_mask & central
    if mask.sum() < 16:
        mask = base_mask
    if mask.sum() < 16:
        return st
    anchor = xyz[mask].mean(dim=0)
    rel = xyz - anchor

    all_coords = [coords]
    all_feats = [st.feats]
    theta = math.radians(float(angle_degrees))
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    for sign in (-1, 1):
        rotated = rel.clone()
        a = rel[:, ax0]
        b = rel[:, ax1]
        rotated[:, ax0] = a * cos_t - sign * b * sin_t
        rotated[:, ax1] = sign * a * sin_t + b * cos_t
        target = anchor + rotated * scale
        target[:, ax0] += sign * extent[ax0] * lateral_ratio
        target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * extent[GROWTH_AXIS] * upward_ratio
        copied = torch.cat([coords[:, :1], torch.round(target).to(coords.dtype)], dim=1)
        valid = clip_valid(copied, limit)
        if valid.sum() > 0:
            all_coords.append(copied[valid])
            all_feats.append(st.feats.clone()[valid])

        src_coords = coords[mask]
        src_feats = st.feats[mask].clone()
        target_base = target[mask]
        xyz0 = src_coords[:, 1:].float()
        for step in range(1, bridge_steps + 1):
            frac = step / float(bridge_steps)
            interp = torch.round(xyz0 * (1.0 - frac) + target_base * frac).to(coords.dtype)
            bridge = torch.cat([src_coords[:, :1], interp], dim=1)
            bridge_valid = clip_valid(bridge, limit)
            if bridge_valid.sum() > 0:
                all_coords.append(bridge[bridge_valid])
                all_feats.append(src_feats[bridge_valid])
    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def leaf_basal_micro_buds(st, limit, base_fraction=0.20, shift_ratio=0.075, bridge_steps=8):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    height = growth_height(xyz)
    base = height <= torch.quantile(height, base_fraction)
    ax0, ax1 = lateral_axes()
    center = (lo.float() + hi.float()) / 2
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2)
    mask = base & (lateral <= torch.quantile(lateral, 0.68))
    if mask.sum() < 16:
        mask = base
    if mask.sum() < 16:
        return st
    src_xyz = xyz[mask]
    src_rel = rel[mask]
    radial_norm = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = src_rel[:, ax0] / radial_norm
    radial[:, ax1] = src_rel[:, ax1] / radial_norm
    upward = torch.zeros_like(src_rel)
    upward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    targets = []
    for sign in (-1, 1):
        side = torch.zeros_like(src_rel)
        side[:, ax0] = sign
        delta = (radial * 0.5 + side * 0.5) * extent * shift_ratio + upward * extent * shift_ratio * 0.75
        targets.append(torch.round(src_xyz + delta))
    return attached_transform_masked_copies(st, mask, targets, limit, bridge_steps=bridge_steps)


def leaf_basal_handle_blades(
    st,
    limit,
    base_fraction=0.28,
    central_quantile=0.42,
    blade_fraction=0.18,
    angle_degrees=34.0,
    child_angles=(-72.0, 0.0, 72.0),
    scale=0.76,
    upward_ratio=0.045,
    bridge_steps=8,
):
    """Copy only a basal handle plus one narrow blade sector.

    Full rosette/leaf-cluster cloning tends to tear thin leaves into floating
    strips after decode.  This operator is intentionally narrower: it finds a
    low central basal anchor, extracts one radial petiole/blade sector, and
    rotates that sector into a few child directions while bridging only the
    basal handle tokens.  The result should read as new leaves emerging from
    the same crown instead of a duplicated plant pasted beside the root.
    """

    import math
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    height = growth_height(xyz)
    ax0, ax1 = lateral_axes()
    center = (lo.float() + hi.float()) / 2
    rel_center = xyz - center
    lateral = torch.sqrt(rel_center[:, ax0] ** 2 + rel_center[:, ax1] ** 2).clamp_min(1e-6)

    base = height <= torch.quantile(height, base_fraction)
    central = lateral <= torch.quantile(lateral, central_quantile)
    base_handle = base & central
    if base_handle.sum() < 12:
        base_handle = base
    if base_handle.sum() < 12:
        return st

    anchor = xyz[base_handle].mean(dim=0)
    rel = xyz - anchor
    lat0 = rel[:, ax0]
    lat1 = rel[:, ax1]
    radial = torch.sqrt(lat0**2 + lat1**2).clamp_min(1e-6)
    h_lo = torch.quantile(height, 0.18)
    h_hi = torch.quantile(height, 0.96)
    radial_floor = torch.quantile(radial, max(0.0, 1.0 - blade_fraction * 2.0))
    blade_pool = (height >= h_lo) & (height <= h_hi) & (radial >= radial_floor)
    if blade_pool.sum() < 12:
        blade_pool = radial >= torch.quantile(radial, 0.60)
    if blade_pool.sum() < 12:
        return st

    score = radial / radial.max().clamp_min(1e-6) + 0.18 * (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    pool_indices = torch.nonzero(blade_pool, as_tuple=False).flatten()
    proto_index = pool_indices[torch.argmax(score[pool_indices])]
    proto = torch.stack([lat0[proto_index], lat1[proto_index]])
    proto = proto / torch.linalg.norm(proto).clamp_min(1e-6)
    proto_perp = torch.stack([-proto[1], proto[0]])

    lateral_vec = torch.stack([lat0, lat1], dim=1)
    cos_to_proto = (lateral_vec @ proto) / radial
    wedge = blade_pool & (cos_to_proto >= math.cos(math.radians(angle_degrees)))
    if wedge.sum() < 12:
        threshold = torch.quantile(cos_to_proto[blade_pool], 0.70)
        wedge = blade_pool & (cos_to_proto >= threshold)
    if wedge.sum() < 12:
        return st

    mask = wedge | base_handle
    src_coords = coords[mask]
    src_feats = st.feats[mask].clone()
    src_xyz = xyz[mask]
    src_rel = src_xyz - anchor
    src_lat = torch.stack([src_rel[:, ax0], src_rel[:, ax1]], dim=1)
    parallel = src_lat @ proto
    perp = src_lat @ proto_perp

    all_coords = [coords]
    all_feats = [st.feats]
    for angle in child_angles:
        theta = math.radians(float(angle))
        target_dir = torch.stack(
            [proto[0] * math.cos(theta) - proto[1] * math.sin(theta), proto[0] * math.sin(theta) + proto[1] * math.cos(theta)]
        )
        target_perp = torch.stack([-target_dir[1], target_dir[0]])
        target_rel = src_rel.clone()
        target_rel[:, ax0] = (parallel * target_dir[0] + perp * target_perp[0]) * scale
        target_rel[:, ax1] = (parallel * target_dir[1] + perp * target_perp[1]) * scale
        target_rel[:, GROWTH_AXIS] = src_rel[:, GROWTH_AXIS] * (0.88 + 0.10 * scale)
        target = anchor + target_rel
        target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * extent[GROWTH_AXIS] * upward_ratio
        copied = torch.cat([src_coords[:, :1], torch.round(target).to(coords.dtype)], dim=1)
        valid = clip_valid(copied, limit)
        if valid.sum() > 0:
            all_coords.append(copied[valid])
            all_feats.append(src_feats[valid])

        base_src_coords = coords[base_handle]
        base_src_feats = st.feats[base_handle].clone()
        bh_xyz = xyz[base_handle]
        bh_rel = bh_xyz - anchor
        bh_lat = torch.stack([bh_rel[:, ax0], bh_rel[:, ax1]], dim=1)
        bh_parallel = bh_lat @ proto
        bh_perp = bh_lat @ proto_perp
        bh_target_rel = bh_rel.clone()
        bh_target_rel[:, ax0] = (bh_parallel * target_dir[0] + bh_perp * target_perp[0]) * scale
        bh_target_rel[:, ax1] = (bh_parallel * target_dir[1] + bh_perp * target_perp[1]) * scale
        bh_target_rel[:, GROWTH_AXIS] = bh_rel[:, GROWTH_AXIS] * (0.88 + 0.10 * scale)
        base_target = anchor + bh_target_rel
        base_target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * extent[GROWTH_AXIS] * upward_ratio
        xyz0 = base_src_coords[:, 1:].float()
        for step in range(1, bridge_steps + 1):
            frac = step / float(bridge_steps)
            interp = torch.round(xyz0 * (1.0 - frac) + base_target * frac).to(coords.dtype)
            bridge = torch.cat([base_src_coords[:, :1], interp], dim=1)
            bridge_valid = clip_valid(bridge, limit)
            if bridge_valid.sum() > 0:
                all_coords.append(bridge[bridge_valid])
                all_feats.append(base_src_feats[bridge_valid])

    return sparse_merge(torch.cat(all_feats, dim=0), torch.cat(all_coords, dim=0))


def fern_frond_tiplets(st, limit, fraction=0.105, lateral_ratio=0.060, upward_ratio=0.070, bridge_steps=8):
    """Tree-crown-style fern growth: only copy terminal frond tips.

    This is deliberately closer to the successful crown-bud operators than to
    the failed leaf-cluster operators.  It copies a small terminal sparse mask
    into alternating side/up directions, so each depth adds visible pinna/frond
    detail without duplicating an entire thin leaf surface.
    """

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    height = growth_height(xyz)
    ax0, ax1 = lateral_axes()
    center = (lo.float() + hi.float()) / 2
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2).clamp_min(1e-6)
    terminal = height >= torch.quantile(height, 1.0 - fraction)
    outer = lateral >= torch.quantile(lateral, 0.45)
    mask = terminal & outer
    if mask.sum() < 16:
        mask = terminal
    if mask.sum() < 16:
        return st

    src_xyz = xyz[mask]
    src_rel = rel[mask]
    radial_norm = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = src_rel[:, ax0] / radial_norm
    radial[:, ax1] = src_rel[:, ax1] / radial_norm
    upward = torch.zeros_like(src_rel)
    upward[:, GROWTH_AXIS] = float(GROWTH_SIGN)

    targets = []
    for sign in (-1, 1):
        side = torch.zeros_like(src_rel)
        side[:, ax0] = float(sign)
        side[:, ax1] = -0.28 * float(sign)
        delta = (
            radial * extent * lateral_ratio * 0.46
            + side * extent * lateral_ratio
            + upward * extent * upward_ratio
        )
        targets.append(torch.round(src_xyz + delta))
    return attached_transform_masked_copies(st, mask, targets, limit, bridge_steps=bridge_steps)


def fern_midrib_pinnae(st, limit, band_fraction=0.34, side_ratio=0.055, bridge_steps=7):
    """Add small alternating pinna-like buds along a frond midrib."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    height = growth_height(xyz)
    ax0, ax1 = lateral_axes()
    center = (lo.float() + hi.float()) / 2
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2).clamp_min(1e-6)
    mid_low = torch.quantile(height, 0.34)
    mid_high = torch.quantile(height, 1.0 - max(0.04, band_fraction * 0.25))
    band = (height >= mid_low) & (height <= mid_high)
    near_midrib = lateral <= torch.quantile(lateral, 0.62)
    mask = band & near_midrib
    if mask.sum() < 20:
        mask = band
    if mask.sum() < 20:
        return st

    src_xyz = xyz[mask]
    src_rel = rel[mask]
    height_norm = (height[mask] - height[mask].min()) / (height[mask].max() - height[mask].min()).clamp_min(1e-6)
    alternating = torch.where(torch.sin(height_norm * torch.pi * 7.0) >= 0, 1.0, -1.0).to(src_xyz.device)
    side = torch.zeros_like(src_rel)
    side[:, ax0] = alternating
    side[:, ax1] = 0.22 * alternating
    upward = torch.zeros_like(src_rel)
    upward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    delta_a = side * extent * side_ratio + upward * extent * side_ratio * 0.38
    delta_b = -side * extent * side_ratio * 0.72 + upward * extent * side_ratio * 0.22
    return attached_transform_masked_copies(
        st,
        mask,
        [torch.round(src_xyz + delta_a), torch.round(src_xyz + delta_b)],
        limit,
        bridge_steps=bridge_steps,
    )


def fern_spiral_echo(st, limit, fraction=0.22, scale=0.72, angle_degrees=42.0, bridge_steps=8):
    """Scaled/rotated terminal echo for fiddlehead-like recursive curls."""

    import math
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    height = growth_height(xyz)
    ax0, ax1 = lateral_axes()
    center = (lo.float() + hi.float()) / 2
    mask = height >= torch.quantile(height, 1.0 - fraction)
    if mask.sum() < 16:
        mask = height >= torch.quantile(height, 0.68)
    if mask.sum() < 16:
        return st
    src_xyz = xyz[mask]
    rel = src_xyz - center
    theta = math.radians(float(angle_degrees))
    rotated = rel.clone()
    a = rel[:, ax0]
    b = rel[:, ax1]
    rotated[:, ax0] = a * math.cos(theta) - b * math.sin(theta)
    rotated[:, ax1] = a * math.sin(theta) + b * math.cos(theta)
    rotated[:, GROWTH_AXIS] = rel[:, GROWTH_AXIS] * 0.88
    target = center + rotated * scale
    target[:, GROWTH_AXIS] += float(GROWTH_SIGN) * extent[GROWTH_AXIS] * 0.11
    return attached_transform_masked_copies(st, mask, [torch.round(target)], limit, bridge_steps=bridge_steps)


def crown_bud_micro_20260511e(st, limit):
    """Conservative short crown bud for the 20260511e botanical repair sweep."""

    return crown_bud_attached(st, limit, fraction=0.055, shift_ratio=0.052, bridge_steps=9)


def crown_scatter_micro_fork_20260511e(st, limit):
    """Tiny attached crown fork; keeps depth difference visible without rail-like rods."""

    st = crown_bud_attached(st, limit, fraction=0.050, shift_ratio=0.048, bridge_steps=10)
    return crown_micro_fork_attached(st, limit, fraction=0.042, shift_ratio=0.046, bridge_steps=10)


def rim_leaflet_micro_20260511e(st, limit):
    """Short scattered rim buds for crown/leaflet-like recursive detail."""

    return ornament_rim_micro_buds(st, limit, fraction=0.055, shift_ratio=0.040, bridge_steps=10)


def tiplet_short_20260511e(st, limit):
    """Short terminal tiplets with lower lateral displacement than the 20260511d default."""

    return fern_frond_tiplets(
        st,
        limit,
        fraction=0.070,
        lateral_ratio=0.040,
        upward_ratio=0.052,
        bridge_steps=10,
    )


def basal_micro_short_20260511e(st, limit):
    """Small basal/root-collar buds for root-fan and rosette candidates."""

    return leaf_basal_micro_buds(st, limit, base_fraction=0.15, shift_ratio=0.050, bridge_steps=10)


def root_crown_micro_conservative_20260511g(st, limit):
    """Conservative spider-plant growth with lower fragmentation than root_rim_tiplet."""

    st = crown_bud_attached(st, limit, fraction=0.040, shift_ratio=0.040, bridge_steps=12)
    return ornament_rim_micro_buds(st, limit, fraction=0.040, shift_ratio=0.030, bridge_steps=12)


def root_plantlet_sprout_20260511g(st, limit):
    """Small attached sprouts for runner/plantlet roots without broad sector copying."""

    st = leaf_basal_micro_buds(st, limit, base_fraction=0.12, shift_ratio=0.035, bridge_steps=12)
    return ornament_rim_micro_buds(st, limit, fraction=0.035, shift_ratio=0.028, bridge_steps=12)


def spider_basal_crown_micro_20260511h(st, limit):
    """Axis-corrected tiny basal buds for spider/rosette roots.

    20260511g used generic crown/rim masks and an often-wrong growth axis.  This
    wrapper is intentionally small and single-purpose so the next sweep can
    diagnose root quality before combining operators.
    """

    return leaf_basal_micro_buds(st, limit, base_fraction=0.10, shift_ratio=0.026, bridge_steps=14)


def spider_leaf_tiplet_micro_20260511h(st, limit):
    """Very short leaf-tip growth for broad strap-leaf roots."""

    return fern_frond_tiplets(
        st,
        limit,
        fraction=0.035,
        lateral_ratio=0.024,
        upward_ratio=0.030,
        bridge_steps=14,
    )


def spider_runner_distal_micro_20260511h(st, limit):
    """Small distal runner/plantlet buds with lower drift than 20260511g."""

    return ornament_rim_micro_buds(st, limit, fraction=0.025, shift_ratio=0.018, bridge_steps=14)


def spider_basal_then_tiplet_20260511h(st, limit):
    """Conservative combined plant growth after single-op diagnostics pass."""

    st = spider_basal_crown_micro_20260511h(st, limit)
    return spider_leaf_tiplet_micro_20260511h(st, limit)


def spider_leaf_handle_visible_20260511j(st, limit):
    """Visible but still local leaf recursion for the 20260511j plant sweep.

    The 20260511i micro operators were metric-clean but almost unchanged across
    depth.  This variant copies one basal handle plus a narrow blade sector,
    so each depth adds readable leaf modules from the crown instead of dust.
    """

    return leaf_basal_handle_blades(
        st,
        limit,
        base_fraction=0.28,
        central_quantile=0.50,
        blade_fraction=0.26,
        angle_degrees=42.0,
        child_angles=(-58.0, 0.0, 58.0),
        scale=0.84,
        upward_ratio=0.055,
        bridge_steps=12,
    )


def spider_leaf_handle_compact_20260511j(st, limit):
    """More conservative visible leaf-copy operator for fragile plant roots."""

    return leaf_basal_handle_blades(
        st,
        limit,
        base_fraction=0.24,
        central_quantile=0.44,
        blade_fraction=0.20,
        angle_degrees=36.0,
        child_angles=(-46.0, 46.0),
        scale=0.78,
        upward_ratio=0.040,
        bridge_steps=14,
    )


def spider_leaf_schedule_20260511j(st, limit):
    """Two-stage plant schedule: visible leaf module followed by tiny buds."""

    st = spider_leaf_handle_visible_20260511j(st, limit)
    return leaf_basal_micro_buds(st, limit, base_fraction=0.11, shift_ratio=0.022, bridge_steps=16)


def root_shrink_fork_20260511h(
    st,
    limit,
    fraction=0.16,
    scale=0.68,
    lateral_ratio=0.060,
    forward_ratio=0.030,
    bridge_steps=14,
):
    """Copy small terminal root masks as attached, shrinking forks.

    This is for the tree_root_leaf root track: copy only terminal sparse tokens,
    shrink them, and bridge them back to the current root.  It should read as
    thick-to-thin recursive root branching rather than whole-object cloning.
    """

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    center = (lo.float() + hi.float()) / 2
    ax0, ax1 = lateral_axes()
    height = growth_height(xyz)
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2).clamp_min(1e-6)
    terminal = height >= torch.quantile(height, 1.0 - fraction)
    outer = lateral >= torch.quantile(lateral, 0.45)
    mask = terminal & outer
    if mask.sum() < 16:
        mask = terminal
    if mask.sum() < 16:
        return st

    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    radial_norm = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = src_rel[:, ax0] / radial_norm
    radial[:, ax1] = src_rel[:, ax1] / radial_norm
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    targets = []
    for sign in (-1, 1):
        side = torch.zeros_like(src_rel)
        side[:, ax0] = float(sign)
        target_rel = src_rel * scale + radial * extent * lateral_ratio + side * extent * lateral_ratio * 0.42
        target = center + target_rel + forward * extent * forward_ratio
        targets.append(torch.round(target))
    return attached_transform_masked_copies(st, mask, targets, limit, bridge_steps=bridge_steps)


def root_shrink_fork_tiplet_20260511h(st, limit):
    """Root fork followed by tiny crown tiplets for tree-root/leaf diagnostics."""

    st = root_shrink_fork_20260511h(st, limit, fraction=0.14, scale=0.66, lateral_ratio=0.052, forward_ratio=0.026, bridge_steps=14)
    return fern_frond_tiplets(st, limit, fraction=0.040, lateral_ratio=0.026, upward_ratio=0.026, bridge_steps=12)


def root_shrink_fork_clean_20260511j(st, limit):
    """Cleaner terminal root fork with fewer copied tips and longer bridges."""

    return root_shrink_fork_20260511h(
        st,
        limit,
        fraction=0.075,
        scale=0.58,
        lateral_ratio=0.036,
        forward_ratio=0.020,
        bridge_steps=22,
    )


def root_wedge_fork_clean_20260511j(st, limit, fraction=0.18, scale=0.64, angle_degrees=32.0, bridge_steps=20):
    """Copy a single coherent terminal root wedge instead of all fine tips.

    20260511i rootfan outputs had the right source semantics but accumulated a
    sprayed terminal cloud.  Selecting one radial wedge keeps the recursive
    child branch coherent enough for naturalization/postprocess to refine.
    """

    import math
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    center = (lo.float() + hi.float()) / 2
    ax0, ax1 = lateral_axes()
    height = growth_height(xyz)
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2).clamp_min(1e-6)
    terminal = height >= torch.quantile(height, 1.0 - fraction)
    outer = lateral >= torch.quantile(lateral, 0.58)
    pool = terminal & outer
    if pool.sum() < 18:
        pool = terminal
    if pool.sum() < 18:
        return st

    pool_idx = torch.nonzero(pool, as_tuple=False).flatten()
    proto_idx = pool_idx[torch.argmax(lateral[pool_idx])]
    proto = torch.stack([rel[proto_idx, ax0], rel[proto_idx, ax1]])
    proto = proto / torch.linalg.norm(proto).clamp_min(1e-6)
    lateral_vec = torch.stack([rel[:, ax0], rel[:, ax1]], dim=1)
    cos_to_proto = (lateral_vec @ proto) / lateral
    wedge = pool & (cos_to_proto >= math.cos(math.radians(angle_degrees)))
    if wedge.sum() < 18:
        threshold = torch.quantile(cos_to_proto[pool], 0.72)
        wedge = pool & (cos_to_proto >= threshold)
    if wedge.sum() < 18:
        return st

    src_xyz = xyz[wedge]
    src_rel = src_xyz - center
    src_lat = torch.stack([src_rel[:, ax0], src_rel[:, ax1]], dim=1)
    perp = torch.stack([-proto[1], proto[0]])
    parallel = src_lat @ proto
    side = src_lat @ perp
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)

    targets = []
    for sign in (-1, 1):
        theta = math.radians(float(sign) * 28.0)
        target_dir = torch.stack(
            [proto[0] * math.cos(theta) - proto[1] * math.sin(theta), proto[0] * math.sin(theta) + proto[1] * math.cos(theta)]
        )
        target_perp = torch.stack([-target_dir[1], target_dir[0]])
        target_rel = src_rel.clone()
        target_rel[:, ax0] = (parallel * target_dir[0] + side * target_perp[0]) * scale
        target_rel[:, ax1] = (parallel * target_dir[1] + side * target_perp[1]) * scale
        target_rel[:, GROWTH_AXIS] = src_rel[:, GROWTH_AXIS] * (0.82 + 0.10 * scale)
        target = center + target_rel + forward * extent * 0.026
        targets.append(torch.round(target))
    return attached_transform_masked_copies(st, wedge, targets, limit, bridge_steps=bridge_steps)


def root_wedge_then_clean_20260511j(st, limit):
    """Coherent wedge child followed by a very small clean terminal fork."""

    st = root_wedge_fork_clean_20260511j(st, limit, fraction=0.16, scale=0.62, angle_degrees=30.0, bridge_steps=20)
    return root_shrink_fork_20260511h(
        st,
        limit,
        fraction=0.055,
        scale=0.56,
        lateral_ratio=0.025,
        forward_ratio=0.014,
        bridge_steps=22,
    )


def spider_terminal_leaflet_visible_20260511k(st, limit):
    """Visible tip-only leaf growth for clean rosette roots.

    The 20260511j basal-handle copy made depth changes visible, but it copied
    too much thin plant geometry and collapsed several leaf clusters.  This
    20260511k operator is deliberately terminal: it lengthens only outer leaf
    tips with long bridges, keeping the basal crown intact.
    """

    return fern_frond_tiplets(
        st,
        limit,
        fraction=0.050,
        lateral_ratio=0.034,
        upward_ratio=0.038,
        bridge_steps=18,
    )


def spider_basal_leaflet_arc_20260511k(st, limit):
    """Narrow basal arc copy for spider/plant leaves.

    This is a smaller version of the 20260511j handle operator: one narrow
    leaf/petiole wedge is copied into two nearby child directions.  It is meant
    for roots that already have a clean shared-vertex rosette, not for fragmented
    presentation GLB cuts.
    """

    return leaf_basal_handle_blades(
        st,
        limit,
        base_fraction=0.18,
        central_quantile=0.34,
        blade_fraction=0.105,
        angle_degrees=24.0,
        child_angles=(-30.0, 30.0),
        scale=0.70,
        upward_ratio=0.024,
        bridge_steps=20,
    )


def spider_balanced_leaflet_20260511k(st, limit):
    """Balanced spider-plant schedule: narrow basal leaves plus tip growth."""

    st = spider_basal_leaflet_arc_20260511k(st, limit)
    return spider_terminal_leaflet_visible_20260511k(st, limit)


def fiddlehead_curl_echo_20260511k(st, limit):
    """Tighter nested curl echo for clean procedural fiddlehead roots."""

    return fern_spiral_echo(st, limit, fraction=0.155, scale=0.66, angle_degrees=58.0, bridge_steps=18)


def fiddlehead_curl_pinnae_20260511k(st, limit):
    """Nested curl echo followed by tiny attached pinnae."""

    st = fiddlehead_curl_echo_20260511k(st, limit)
    return fern_midrib_pinnae(st, limit, band_fraction=0.22, side_ratio=0.030, bridge_steps=16)


def pine_terminal_needles_20260511k(st, limit):
    """Small attached terminal needle/leaf additions for V23 pine sources."""

    st = crown_bud_attached(st, limit, fraction=0.040, shift_ratio=0.034, bridge_steps=18)
    return fern_frond_tiplets(st, limit, fraction=0.030, lateral_ratio=0.020, upward_ratio=0.022, bridge_steps=18)


def root_single_wedge_branch_20260511k(st, limit, fraction=0.115, scale=0.70, angle_degrees=38.0, bridge_steps=26):
    """Single coherent terminal root branch for depth-4 root recursion.

    20260511j two-sided wedge roots were cleaner than earlier all-tip forks but
    still produced weak depth changes and many tiny satellites.  This variant
    copies one terminal wedge into one child branch, using fewer copied tokens
    and a larger but bridged transform.
    """

    import math
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    center = (lo.float() + hi.float()) / 2
    ax0, ax1 = lateral_axes()
    height = growth_height(xyz)
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2).clamp_min(1e-6)
    terminal = height >= torch.quantile(height, 1.0 - fraction)
    outer = lateral >= torch.quantile(lateral, 0.54)
    pool = terminal & outer
    if pool.sum() < 18:
        pool = terminal
    if pool.sum() < 18:
        return st

    pool_idx = torch.nonzero(pool, as_tuple=False).flatten()
    proto_idx = pool_idx[torch.argmax(lateral[pool_idx])]
    proto = torch.stack([rel[proto_idx, ax0], rel[proto_idx, ax1]])
    proto = proto / torch.linalg.norm(proto).clamp_min(1e-6)
    lateral_vec = torch.stack([rel[:, ax0], rel[:, ax1]], dim=1)
    cos_to_proto = (lateral_vec @ proto) / lateral
    wedge = pool & (cos_to_proto >= math.cos(math.radians(26.0)))
    if wedge.sum() < 18:
        threshold = torch.quantile(cos_to_proto[pool], 0.78)
        wedge = pool & (cos_to_proto >= threshold)
    if wedge.sum() < 18:
        return st

    src_xyz = xyz[wedge]
    src_rel = src_xyz - center
    src_lat = torch.stack([src_rel[:, ax0], src_rel[:, ax1]], dim=1)
    perp = torch.stack([-proto[1], proto[0]])
    parallel = src_lat @ proto
    side = src_lat @ perp
    theta = math.radians(float(angle_degrees))
    target_dir = torch.stack(
        [proto[0] * math.cos(theta) - proto[1] * math.sin(theta), proto[0] * math.sin(theta) + proto[1] * math.cos(theta)]
    )
    target_perp = torch.stack([-target_dir[1], target_dir[0]])
    target_rel = src_rel.clone()
    target_rel[:, ax0] = (parallel * target_dir[0] + side * target_perp[0]) * scale
    target_rel[:, ax1] = (parallel * target_dir[1] + side * target_perp[1]) * scale
    target_rel[:, GROWTH_AXIS] = src_rel[:, GROWTH_AXIS] * (0.78 + 0.12 * scale)
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = proto[0]
    radial[:, ax1] = proto[1]
    target = center + target_rel + forward * extent * 0.045 + radial * extent * 0.028
    return attached_transform_masked_copies(st, wedge, [torch.round(target)], limit, bridge_steps=bridge_steps)


def root_single_then_tiplets_20260511k(st, limit):
    """Single root wedge followed by a tiny local terminal fork."""

    st = root_single_wedge_branch_20260511k(st, limit, fraction=0.105, scale=0.68, angle_degrees=34.0, bridge_steps=26)
    return root_shrink_fork_20260511h(
        st,
        limit,
        fraction=0.040,
        scale=0.58,
        lateral_ratio=0.018,
        forward_ratio=0.012,
        bridge_steps=24,
    )


def root_relaxed_wedge_branch_20260511l(
    st,
    limit,
    fraction=0.18,
    scale=0.72,
    angle_degrees=42.0,
    min_tokens=8,
    bridge_steps=30,
):
    """Relaxed single-branch root copy for sparse V23 root-fan masks.

    The 20260511k single-wedge operator often returned an unchanged state on
    rootfan inputs because its terminal wedge required too many sparse tokens.
    This version keeps the same coherent-wedge idea but widens the fallback mask
    and accepts smaller connected token groups, so a depth-4 run can test real
    recursive growth instead of silently no-oping.
    """

    import math
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    center = (lo.float() + hi.float()) / 2
    ax0, ax1 = lateral_axes()
    height = growth_height(xyz)
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2).clamp_min(1e-6)

    terminal = height >= torch.quantile(height, 1.0 - fraction)
    outer = lateral >= torch.quantile(lateral, 0.42)
    pool = terminal & outer
    if pool.sum() < min_tokens:
        pool = height >= torch.quantile(height, max(0.0, 1.0 - fraction * 1.8))
    if pool.sum() < min_tokens:
        return st

    pool_idx = torch.nonzero(pool, as_tuple=False).flatten()
    proto_idx = pool_idx[torch.argmax(lateral[pool_idx])]
    proto = torch.stack([rel[proto_idx, ax0], rel[proto_idx, ax1]])
    proto = proto / torch.linalg.norm(proto).clamp_min(1e-6)
    lateral_vec = torch.stack([rel[:, ax0], rel[:, ax1]], dim=1)
    cos_to_proto = (lateral_vec @ proto) / lateral
    wedge = pool & (cos_to_proto >= math.cos(math.radians(angle_degrees)))
    if wedge.sum() < min_tokens:
        threshold = torch.quantile(cos_to_proto[pool], 0.58)
        wedge = pool & (cos_to_proto >= threshold)
    if wedge.sum() < min_tokens:
        wedge = pool

    src_xyz = xyz[wedge]
    src_rel = src_xyz - center
    src_lat = torch.stack([src_rel[:, ax0], src_rel[:, ax1]], dim=1)
    perp = torch.stack([-proto[1], proto[0]])
    parallel = src_lat @ proto
    side = src_lat @ perp
    theta = math.radians(float(angle_degrees) * 0.56)
    target_dir = torch.stack(
        [proto[0] * math.cos(theta) - proto[1] * math.sin(theta), proto[0] * math.sin(theta) + proto[1] * math.cos(theta)]
    )
    target_perp = torch.stack([-target_dir[1], target_dir[0]])
    target_rel = src_rel.clone()
    target_rel[:, ax0] = (parallel * target_dir[0] + side * target_perp[0]) * scale
    target_rel[:, ax1] = (parallel * target_dir[1] + side * target_perp[1]) * scale
    target_rel[:, GROWTH_AXIS] = src_rel[:, GROWTH_AXIS] * (0.76 + 0.14 * scale)
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = proto[0]
    radial[:, ax1] = proto[1]
    target = center + target_rel + forward * extent * 0.060 + radial * extent * 0.034
    return attached_transform_masked_copies(st, wedge, [torch.round(target)], limit, bridge_steps=bridge_steps)


def root_primary_branch_cut_20260511l(
    st,
    limit,
    fraction=0.34,
    scale=0.64,
    angle_degrees=46.0,
    min_tokens=10,
    bridge_steps=28,
):
    """Copy a thicker primary branch band before adding fine rootlets.

    Terminal rootlet masks are too small for the desired hero case.  This
    operator selects a mid-to-terminal radial branch band, then creates two
    shrunken attached child branches.  It is intentionally root-first: the goal
    is a visible thick-to-thin hierarchy before any small terminal details.
    """

    import math
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    center = (lo.float() + hi.float()) / 2
    ax0, ax1 = lateral_axes()
    height = growth_height(xyz)
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2).clamp_min(1e-6)
    h_low = torch.quantile(height, 0.42)
    h_high = torch.quantile(height, 1.0 - max(0.04, fraction * 0.18))
    band = (height >= h_low) & (height <= h_high)
    outer = lateral >= torch.quantile(lateral, 0.38)
    pool = band & outer
    if pool.sum() < min_tokens:
        pool = height >= torch.quantile(height, 0.36)
    if pool.sum() < min_tokens:
        return st

    score = lateral / lateral.max().clamp_min(1e-6) + 0.22 * (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    pool_idx = torch.nonzero(pool, as_tuple=False).flatten()
    proto_idx = pool_idx[torch.argmax(score[pool_idx])]
    proto = torch.stack([rel[proto_idx, ax0], rel[proto_idx, ax1]])
    proto = proto / torch.linalg.norm(proto).clamp_min(1e-6)
    lateral_vec = torch.stack([rel[:, ax0], rel[:, ax1]], dim=1)
    cos_to_proto = (lateral_vec @ proto) / lateral
    wedge = pool & (cos_to_proto >= math.cos(math.radians(angle_degrees)))
    if wedge.sum() < min_tokens:
        threshold = torch.quantile(cos_to_proto[pool], 0.55)
        wedge = pool & (cos_to_proto >= threshold)
    if wedge.sum() < min_tokens:
        wedge = pool

    src_xyz = xyz[wedge]
    src_rel = src_xyz - center
    src_lat = torch.stack([src_rel[:, ax0], src_rel[:, ax1]], dim=1)
    perp = torch.stack([-proto[1], proto[0]])
    parallel = src_lat @ proto
    side = src_lat @ perp
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    targets = []
    for sign in (-1, 1):
        theta = math.radians(float(sign) * 22.0)
        target_dir = torch.stack(
            [proto[0] * math.cos(theta) - proto[1] * math.sin(theta), proto[0] * math.sin(theta) + proto[1] * math.cos(theta)]
        )
        target_perp = torch.stack([-target_dir[1], target_dir[0]])
        target_rel = src_rel.clone()
        target_rel[:, ax0] = (parallel * target_dir[0] + side * target_perp[0]) * scale
        target_rel[:, ax1] = (parallel * target_dir[1] + side * target_perp[1]) * scale
        target_rel[:, GROWTH_AXIS] = src_rel[:, GROWTH_AXIS] * (0.80 + 0.08 * scale)
        targets.append(torch.round(center + target_rel + forward * extent * 0.046))
    return attached_transform_masked_copies(st, wedge, targets, limit, bridge_steps=bridge_steps)


def root_two_phase_hierarchy_20260511l(st, limit):
    """Primary root branch growth followed by a relaxed terminal child."""

    st = root_primary_branch_cut_20260511l(st, limit, fraction=0.30, scale=0.62, angle_degrees=44.0, min_tokens=10, bridge_steps=30)
    return root_relaxed_wedge_branch_20260511l(
        st,
        limit,
        fraction=0.11,
        scale=0.66,
        angle_degrees=40.0,
        min_tokens=8,
        bridge_steps=30,
    )


def root_two_phase_late_rootlets_20260511l(st, limit):
    """Hierarchy-first root growth with very small rootlets as the final step."""

    st = root_two_phase_hierarchy_20260511l(st, limit)
    return root_shrink_fork_20260511h(
        st,
        limit,
        fraction=0.030,
        scale=0.58,
        lateral_ratio=0.014,
        forward_ratio=0.010,
        bridge_steps=26,
    )


def spider_leaf_cluster_compact_20260511l(st, limit):
    """Compact basal leaf-cluster recursion for fragile plant-leaf roots."""

    st = leaf_basal_handle_blades(
        st,
        limit,
        base_fraction=0.18,
        central_quantile=0.34,
        blade_fraction=0.13,
        angle_degrees=26.0,
        child_angles=(-34.0, 34.0),
        scale=0.72,
        upward_ratio=0.026,
        bridge_steps=24,
    )
    return fern_frond_tiplets(st, limit, fraction=0.026, lateral_ratio=0.016, upward_ratio=0.020, bridge_steps=24)


def spider_leaf_treecrown_schedule_20260511l(st, limit):
    """Tree-crown-like plant recursion: local crown buds, then leaf-tip growth."""

    st = leaf_basal_micro_buds(st, limit, base_fraction=0.085, shift_ratio=0.018, bridge_steps=24)
    return fern_frond_tiplets(st, limit, fraction=0.040, lateral_ratio=0.026, upward_ratio=0.030, bridge_steps=24)


def spider_leaf_tip_clean_20260511l(st, limit):
    """Tip-only spider/leaf growth with long bridges and low lateral drift."""

    return fern_frond_tiplets(st, limit, fraction=0.034, lateral_ratio=0.020, upward_ratio=0.024, bridge_steps=28)


def fiddlehead_guarded_curl_20260511l(st, limit):
    """Small, guarded curl echo for fiddleheads after 20260511k fragmentation."""

    return fern_spiral_echo(st, limit, fraction=0.105, scale=0.78, angle_degrees=30.0, bridge_steps=30)


def pine_leaf_cluster_clean_20260511l(st, limit):
    """Conservative V23 pine leaf frontier growth with fewer terminal islands."""

    st = crown_bud_attached(st, limit, fraction=0.030, shift_ratio=0.024, bridge_steps=28)
    return fern_frond_tiplets(st, limit, fraction=0.022, lateral_ratio=0.014, upward_ratio=0.016, bridge_steps=28)


def pine_branch_tip_cluster_20260511l(st, limit):
    """Slightly larger pine branch-tip cluster before tiny terminal needles."""

    st = crown_bud_attached(st, limit, fraction=0.052, shift_ratio=0.030, bridge_steps=26)
    return pine_leaf_cluster_clean_20260511l(st, limit)


def plant_basal_midrib_leaflet_20260511n(st, limit):
    """Visible basal/petiole leaflet growth for fragile plant roots.

    20260511l showed that tip-only plant operators can become token no-ops,
    while full cluster copying tears thin leaves.  This operator explicitly
    copies a narrow basal handle plus one midrib-like blade sector into two
    smaller child leaves.  It is meant for depth-1/2 gated sweeps, not blind
    depth-4 expansion.
    """

    return leaf_basal_handle_blades(
        st,
        limit,
        base_fraction=0.30,
        central_quantile=0.36,
        blade_fraction=0.10,
        angle_degrees=22.0,
        child_angles=(-32.0, 32.0),
        scale=0.68,
        upward_ratio=0.034,
        bridge_steps=30,
    )


def plant_basal_crown_leaflets_20260511n(st, limit):
    """Small crown leaflets after a basal handle, with bounded token growth."""

    st = leaf_basal_micro_buds(st, limit, base_fraction=0.075, shift_ratio=0.014, bridge_steps=28)
    return plant_basal_midrib_leaflet_20260511n(st, limit)


def spider_runner_leaflet_gated_20260511n(st, limit):
    """Early-depth spider-plant runner growth that avoids late-depth clutter."""

    return leaf_basal_handle_blades(
        st,
        limit,
        base_fraction=0.22,
        central_quantile=0.32,
        blade_fraction=0.12,
        angle_degrees=24.0,
        child_angles=(-42.0, 42.0),
        scale=0.72,
        upward_ratio=0.026,
        bridge_steps=26,
    )


def fern_pinnae_sparse_attach_20260511n(st, limit):
    """Fewer, shorter fern pinnae for depth-1 visual QA."""

    st = fern_midrib_pinnae(st, limit, band_fraction=0.22, side_ratio=0.030, bridge_steps=16)
    return fern_frond_tiplets(st, limit, fraction=0.020, lateral_ratio=0.012, upward_ratio=0.014, bridge_steps=18)


def fiddlehead_thick_curl_20260511n(st, limit):
    """Thicker, less aggressive curl echo than the fragmented 20260511l row."""

    return fern_spiral_echo(st, limit, fraction=0.075, scale=0.86, angle_degrees=18.0, bridge_steps=34)


def root_short_terminal_rootlets_20260511n(st, limit):
    """Extend a few terminal rootlets without trying to replace the branch body."""

    return root_shrink_fork_20260511h(
        st,
        limit,
        fraction=0.026,
        scale=0.76,
        lateral_ratio=0.010,
        forward_ratio=0.018,
        bridge_steps=32,
    )


def root_first_split_taper_20260511n(st, limit):
    """Coherent first-split style taper for V23 rootfan early-depth QA."""

    st = root_relaxed_wedge_branch_20260511l(
        st,
        limit,
        fraction=0.10,
        scale=0.78,
        angle_degrees=48.0,
        min_tokens=6,
        bridge_steps=34,
    )
    return root_short_terminal_rootlets_20260511n(st, limit)


def pine_leaf_gated_20260511n(st, limit):
    """Single early-depth pine frontier growth with lower component pressure."""

    st = crown_bud_attached(st, limit, fraction=0.024, shift_ratio=0.020, bridge_steps=32)
    return fern_frond_tiplets(st, limit, fraction=0.016, lateral_ratio=0.010, upward_ratio=0.012, bridge_steps=32)


def spider_runner_visible_chain_20260511p(st, limit):
    """Stronger spider-runner leaflet growth for depth-visible QA.

    The 20260511o runner rows were clean but nearly identical across depths.
    This keeps the successful terminal-leaflet contract, but increases the
    terminal mask and bridge length enough that d0..d4 should read as a growing
    runner/leaflet chain instead of only token-density change.
    """

    st = fern_frond_tiplets(st, limit, fraction=0.064, lateral_ratio=0.040, upward_ratio=0.038, bridge_steps=30)
    return leaf_basal_micro_buds(st, limit, base_fraction=0.070, shift_ratio=0.014, bridge_steps=28)


def spider_rosette_crown_fan_20260511p(st, limit):
    """Visible basal crown fan without copying a whole thin leaf cluster."""

    st = leaf_basal_handle_blades(
        st,
        limit,
        base_fraction=0.22,
        central_quantile=0.36,
        blade_fraction=0.095,
        angle_degrees=24.0,
        child_angles=(-46.0, 46.0),
        scale=0.72,
        upward_ratio=0.034,
        bridge_steps=30,
    )
    return fern_frond_tiplets(st, limit, fraction=0.026, lateral_ratio=0.016, upward_ratio=0.020, bridge_steps=30)


def potted_petiole_leaf_fan_20260511p(st, limit):
    """Broad-leaf petiole fan for the CC0 Poly Haven potted leaves root."""

    st = leaf_basal_handle_blades(
        st,
        limit,
        base_fraction=0.26,
        central_quantile=0.40,
        blade_fraction=0.080,
        angle_degrees=20.0,
        child_angles=(-34.0, 0.0, 34.0),
        scale=0.70,
        upward_ratio=0.026,
        bridge_steps=34,
    )
    return leaf_basal_micro_buds(st, limit, base_fraction=0.060, shift_ratio=0.010, bridge_steps=30)


def fern_midrib_pinnae_handles_20260511p(st, limit):
    """Low-drift fern pinnae handles for the clean single-frond Poly Haven cut."""

    st = fern_midrib_pinnae(st, limit, band_fraction=0.18, side_ratio=0.022, bridge_steps=24)
    return fern_frond_tiplets(st, limit, fraction=0.018, lateral_ratio=0.010, upward_ratio=0.012, bridge_steps=24)


def fiddlehead_nested_curl_20260512a(st, limit):
    """Publication-targeted nested curl for crozier roots.

    Prior fiddlehead rows either fragmented under aggressive curl copies or
    became visually static. This schedule uses a small spiral echo followed by
    short attached tiplets so depth changes are visible without copying the
    whole thin leaf surface.
    """

    st = fern_spiral_echo(st, limit, fraction=0.090, scale=0.82, angle_degrees=24.0, bridge_steps=36)
    return fern_frond_tiplets(st, limit, fraction=0.018, lateral_ratio=0.010, upward_ratio=0.012, bridge_steps=34)


def fiddlehead_visible_curl_20260512a(st, limit):
    """Stronger crozier curl echo for visual-depth stress testing."""

    return fern_spiral_echo(st, limit, fraction=0.125, scale=0.76, angle_degrees=34.0, bridge_steps=34)


def fern_showcase_pinnae_20260512a(st, limit):
    """Low-drift midrib and pinnae expansion for compound fern roots."""

    st = fern_midrib_pinnae(st, limit, band_fraction=0.20, side_ratio=0.026, bridge_steps=26)
    return fern_frond_tiplets(st, limit, fraction=0.020, lateral_ratio=0.012, upward_ratio=0.014, bridge_steps=28)


def fern_showcase_dense_pinnae_20260512a(st, limit):
    """Denser compound fern expansion for visible recursive leaflet growth."""

    st = fern_midrib_pinnae(st, limit, band_fraction=0.28, side_ratio=0.034, bridge_steps=24)
    st = fern_frond_tiplets(st, limit, fraction=0.030, lateral_ratio=0.018, upward_ratio=0.020, bridge_steps=28)
    return crown_bud_attached(st, limit, fraction=0.014, shift_ratio=0.010, bridge_steps=30)


def fiddlehead_macro_curl_20260512b(st, limit):
    """Larger crozier echo for the 20260512b macro fiddlehead roots."""

    st = fern_spiral_echo(st, limit, fraction=0.155, scale=0.78, angle_degrees=44.0, bridge_steps=36)
    return fern_spiral_echo(st, limit, fraction=0.070, scale=0.84, angle_degrees=22.0, bridge_steps=38)


def fiddlehead_scale_buds_20260512b(st, limit):
    """Attached scale/leaflet buds on a fiddlehead coil without whole-root copy."""

    st = fern_frond_tiplets(st, limit, fraction=0.045, lateral_ratio=0.020, upward_ratio=0.018, bridge_steps=34)
    return crown_bud_attached(st, limit, fraction=0.020, shift_ratio=0.014, bridge_steps=36)


def fern_broad_pinnae_20260512b(st, limit):
    """Visible but bounded broad-pinnae expansion for the wider 20260512b fronds."""

    st = fern_midrib_pinnae(st, limit, band_fraction=0.34, side_ratio=0.045, bridge_steps=24)
    return fern_frond_tiplets(st, limit, fraction=0.040, lateral_ratio=0.024, upward_ratio=0.022, bridge_steps=28)


def fern_branchlet_pinnae_20260512b(st, limit):
    """Second-order fern branchlets for clear depth changes on compound fronds."""

    st = fern_midrib_pinnae(st, limit, band_fraction=0.42, side_ratio=0.058, bridge_steps=24)
    st = fern_frond_tiplets(st, limit, fraction=0.055, lateral_ratio=0.030, upward_ratio=0.026, bridge_steps=28)
    return crown_bud_attached(st, limit, fraction=0.022, shift_ratio=0.014, bridge_steps=30)


def _sidecar_mask_and_targets_20260512c(
    st,
    fraction=0.16,
    lateral_ratio=0.10,
    forward_ratio=0.06,
    scale=0.74,
    min_tokens=12,
    max_source_tokens=220,
):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2).clamp_min(1e-6)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    lateral_norm = lateral / lateral.max().clamp_min(1e-6)

    band = height >= torch.quantile(height, 1.0 - fraction)
    outer = lateral >= torch.quantile(lateral, 0.35)
    pool = band & outer
    if pool.sum() < min_tokens:
        pool = height >= torch.quantile(height, max(0.50, 1.0 - fraction * 1.8))
    if pool.sum() < min_tokens:
        return None, []

    score = height_norm + 0.45 * lateral_norm
    pool_idx = torch.nonzero(pool, as_tuple=False).flatten()
    if pool_idx.shape[0] > max_source_tokens:
        chosen = pool_idx[torch.topk(score[pool_idx], k=max_source_tokens).indices]
        mask = torch.zeros_like(pool)
        mask[chosen] = True
    else:
        mask = pool

    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    radial = torch.zeros_like(src_rel)
    src_lat = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial[:, ax0] = src_rel[:, ax0] / src_lat
    radial[:, ax1] = src_rel[:, ax1] / src_lat
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    targets = []
    for sign in (-1.0, 1.0):
        side = torch.zeros_like(src_rel)
        side[:, ax0] = sign
        side[:, ax1] = -0.28 * sign
        target = center + src_rel * scale + radial * extent * lateral_ratio + side * extent * lateral_ratio * 0.46 + forward * extent * forward_ratio
        targets.append(torch.round(target))
    return mask, targets


def fiddlehead_supported_scales_20260512c(st, limit):
    """Supported scale sidecars for compact crozier roots."""

    mask, targets = _sidecar_mask_and_targets_20260512c(
        st,
        fraction=0.18,
        lateral_ratio=0.055,
        forward_ratio=0.030,
        scale=0.82,
        max_source_tokens=160,
    )
    if mask is None:
        return st
    return masked_target_copies_with_tube_support_20260511t(
        st,
        mask,
        targets,
        limit,
        support_radius=1.0,
        support_steps=12,
        max_support_tokens=180,
    )


def fiddlehead_compact_echo_20260512c(st, limit):
    """Small terminal echo for compact fiddlehead depth without rod-like copies."""

    st = fern_spiral_echo(st, limit, fraction=0.055, scale=0.88, angle_degrees=18.0, bridge_steps=38)
    return fern_frond_tiplets(st, limit, fraction=0.020, lateral_ratio=0.010, upward_ratio=0.010, bridge_steps=36)


def fern_visible_sidecars_20260512c(st, limit):
    """Visible supported sidecars on fern pinnae with bounded source tokens."""

    mask, targets = _sidecar_mask_and_targets_20260512c(
        st,
        fraction=0.22,
        lateral_ratio=0.075,
        forward_ratio=0.030,
        scale=0.76,
        max_source_tokens=190,
    )
    if mask is None:
        return st
    return masked_target_copies_with_tube_support_20260511t(
        st,
        mask,
        targets,
        limit,
        support_radius=1.0,
        support_steps=12,
        max_support_tokens=220,
    )


def fern_fractal_sidecars_20260512c(st, limit):
    """Second-order supported fern sidecars for stronger depth change."""

    st = fern_midrib_pinnae(st, limit, band_fraction=0.46, side_ratio=0.048, bridge_steps=26)
    mask, targets = _sidecar_mask_and_targets_20260512c(
        st,
        fraction=0.28,
        lateral_ratio=0.092,
        forward_ratio=0.036,
        scale=0.72,
        max_source_tokens=210,
    )
    if mask is None:
        return st
    return masked_target_copies_with_tube_support_20260511t(
        st,
        mask,
        targets,
        limit,
        support_radius=1.0,
        support_steps=14,
        max_support_tokens=260,
    )


def _cap_outer_height_mask_20260512d(st, fraction=0.12, min_tokens=20, max_tokens=96):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    lateral = torch.sqrt((rel[:, ax0] / extent[ax0].clamp_min(1)) ** 2 + (rel[:, ax1] / extent[ax1].clamp_min(1)) ** 2)
    pool = (height >= torch.quantile(height, 1.0 - fraction)) & (lateral >= torch.quantile(lateral, 0.42))
    if pool.sum() < min_tokens:
        pool = height >= torch.quantile(height, max(0.45, 1.0 - fraction * 1.65))
    if pool.sum() < min_tokens:
        return None
    score = height_norm + 0.38 * lateral
    return cap_mask_by_score(pool, score, max_tokens)


def fiddlehead_inner_buds_20260512d(st, limit):
    """Small attached bud growth for solid 12d croziers.

    This deliberately avoids the 12c supported-sidecar route, which decoded as
    torn sheets.  It adds only compact tip/rim buds so depth changes are visible
    while keeping the crozier silhouette dominant.
    """

    st = crown_bud_attached(st, limit, fraction=0.050, shift_ratio=0.025, bridge_steps=34)
    return ornament_rim_micro_buds(st, limit, fraction=0.055, shift_ratio=0.020, bridge_steps=32)


def fiddlehead_solid_echo_20260512d(st, limit):
    """Very small crozier echo plus compact buds for the solid 12d roots."""

    st = fern_spiral_echo(st, limit, fraction=0.040, scale=0.93, angle_degrees=12.0, bridge_steps=44)
    return fiddlehead_inner_buds_20260512d(st, limit)


def fern_visible_refinement_20260512d(st, limit):
    """Visible but conservative refinement for broad compound fern roots."""

    st = fern_midrib_pinnae(st, limit, band_fraction=0.50, side_ratio=0.050, bridge_steps=28)
    return fern_frond_tiplets(st, limit, fraction=0.045, lateral_ratio=0.024, upward_ratio=0.020, bridge_steps=30)


def fern_bounded_sidelets_20260512d(st, limit):
    """Bounded second-order sidelet copies for 12d fronds.

    Uses fewer source tokens and shorter support than 12c.  The purpose is to
    show depth progression without the many disconnected sidecar islands seen
    in v26c_fern_*.
    """

    import torch

    mask = _cap_outer_height_mask_20260512d(st, fraction=0.18, min_tokens=24, max_tokens=84)
    if mask is None:
        return st
    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    radial = torch.zeros_like(src_rel)
    lat = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial[:, ax0] = src_rel[:, ax0] / lat
    radial[:, ax1] = src_rel[:, ax1] / lat
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    targets = []
    for sign in (-1.0, 1.0):
        side = torch.zeros_like(src_rel)
        side[:, ax0] = sign
        side[:, ax1] = -0.18 * sign
        target = src_xyz + radial * extent * 0.020 + side * extent * 0.026 + forward * extent * 0.016
        targets.append(torch.round(target))
    return masked_target_copies_with_tube_support_20260511t(
        st,
        mask,
        targets,
        limit,
        support_radius=0.65,
        support_steps=10,
        max_support_tokens=120,
    )


def fern_refinement_then_sidelets_20260512d(st, limit):
    st = fern_visible_refinement_20260512d(st, limit)
    return fern_bounded_sidelets_20260512d(st, limit)


def _surface_band_mask_20260512e(st, lower_q=0.10, upper_q=0.90, lateral_q=0.62, max_tokens=96, min_tokens=18):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    h0 = torch.quantile(height, lower_q)
    h1 = torch.quantile(height, upper_q)
    lateral = torch.sqrt((rel[:, ax0] / extent[ax0].clamp_min(1)) ** 2 + (rel[:, ax1] / extent[ax1].clamp_min(1)) ** 2)
    band = (height >= h0) & (height <= h1)
    surface = lateral >= torch.quantile(lateral, lateral_q)
    pool = band & surface
    if pool.sum() < min_tokens:
        pool = surface
    if pool.sum() < min_tokens:
        return None
    angle = torch.atan2(rel[:, ax1], rel[:, ax0])
    h_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    score = lateral + 0.10 * torch.sin(angle * 5.0) + 0.06 * torch.cos(h_norm * torch.pi * 4.0)
    return cap_mask_by_score(pool, score, max_tokens)


def fiddlehead_surface_microbuds_20260512e(st, limit):
    """Surface-distributed crozier buds without the 12d underside rung band."""

    import torch

    mask = _surface_band_mask_20260512e(st, lower_q=0.12, upper_q=0.92, lateral_q=0.66, max_tokens=92)
    if mask is None:
        return st
    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    radial_norm = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = src_rel[:, ax0] / radial_norm
    radial[:, ax1] = src_rel[:, ax1] / radial_norm
    tangent = torch.zeros_like(src_rel)
    tangent[:, ax0] = -radial[:, ax1]
    tangent[:, ax1] = radial[:, ax0]
    height = growth_height(src_xyz)
    h_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    phase = torch.where(torch.sin(h_norm * torch.pi * 7.0) >= 0, 1.0, -1.0).to(src_xyz.device)
    target_a = src_xyz + radial * extent * 0.020 + tangent * phase[:, None] * extent * 0.010
    target_b = src_xyz + radial * extent * 0.012 - tangent * phase[:, None] * extent * 0.007
    return attached_transform_masked_copies(st, mask, [torch.round(target_a), torch.round(target_b)], limit, bridge_steps=34)


def fiddlehead_tiny_coil_echo_20260512e(st, limit):
    """Very small coil echo, then surface buds; no terminal tiplet operator."""

    st = fern_spiral_echo(st, limit, fraction=0.030, scale=0.955, angle_degrees=8.0, bridge_steps=48)
    return fiddlehead_surface_microbuds_20260512e(st, limit)


def fiddlehead_surface_then_echo_20260512e(st, limit):
    st = fiddlehead_surface_microbuds_20260512e(st, limit)
    return fern_spiral_echo(st, limit, fraction=0.026, scale=0.965, angle_degrees=6.0, bridge_steps=48)


def fern_outer_pinnae_refinement_20260512e(st, limit):
    """Make compound frond depth changes visible by extending existing pinna tips."""

    import torch

    mask = _surface_band_mask_20260512e(st, lower_q=0.08, upper_q=0.94, lateral_q=0.58, max_tokens=128, min_tokens=24)
    if mask is None:
        return st
    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    radial_norm = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = src_rel[:, ax0] / radial_norm
    radial[:, ax1] = src_rel[:, ax1] / radial_norm
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    height = growth_height(src_xyz)
    h_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    alternate = torch.where(torch.sin(h_norm * torch.pi * 9.0) >= 0, 1.0, -1.0).to(src_xyz.device)
    side = torch.zeros_like(src_rel)
    side[:, ax0] = alternate
    side[:, ax1] = -0.16 * alternate
    target_a = src_xyz + radial * extent * 0.034 + side * extent * 0.018 + forward * extent * 0.012
    target_b = src_xyz + radial * extent * 0.020 - side * extent * 0.011 + forward * extent * 0.008
    return attached_transform_masked_copies(st, mask, [torch.round(target_a), torch.round(target_b)], limit, bridge_steps=30)


def fern_hierarchical_visible_20260512e(st, limit):
    st = fern_midrib_pinnae(st, limit, band_fraction=0.52, side_ratio=0.062, bridge_steps=30)
    return fern_outer_pinnae_refinement_20260512e(st, limit)


def fern_hierarchical_then_tiplets_20260512e(st, limit):
    st = fern_hierarchical_visible_20260512e(st, limit)
    return fern_frond_tiplets(st, limit, fraction=0.040, lateral_ratio=0.026, upward_ratio=0.014, bridge_steps=32)


def fiddlehead_macro_surface_buds_20260512f(st, limit):
    """Depth-visible crozier surface buds with cell-scale displacement.

    The 12e microbud operator often rounded back into existing sparse cells, so
    the decoded mesh was clean but close to no-op. This version deliberately
    moves a smaller surface mask by multiple sparse cells and attaches each copy
    through short interpolated paths.
    """

    import torch

    mask = _surface_band_mask_20260512e(st, lower_q=0.10, upper_q=0.94, lateral_q=0.68, max_tokens=54, min_tokens=14)
    if mask is None:
        return st
    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    radial_norm = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = src_rel[:, ax0] / radial_norm
    radial[:, ax1] = src_rel[:, ax1] / radial_norm
    tangent = torch.zeros_like(src_rel)
    tangent[:, ax0] = -radial[:, ax1]
    tangent[:, ax1] = radial[:, ax0]
    height = growth_height(src_xyz)
    h_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    phase = torch.where(torch.sin(h_norm * torch.pi * 5.0) >= 0, 1.0, -1.0).to(src_xyz.device)
    radial_shift = torch.clamp(extent.max() * 0.135, min=2.0, max=3.4)
    tangent_shift = torch.clamp(extent.max() * 0.055, min=1.0, max=1.7)
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    target_a = src_xyz + radial * radial_shift + tangent * phase[:, None] * tangent_shift + forward * 0.6
    target_b = src_xyz + radial * (radial_shift * 0.58) - tangent * phase[:, None] * (tangent_shift * 0.55)
    return attached_transform_masked_copies(st, mask, [torch.round(target_a), torch.round(target_b)], limit, bridge_steps=12)


def fiddlehead_macro_buds_then_micro_20260512f(st, limit):
    st = fiddlehead_macro_surface_buds_20260512f(st, limit)
    return fiddlehead_surface_microbuds_20260512e(st, limit)


def fiddlehead_macro_buds_light_echo_20260512f(st, limit):
    st = fiddlehead_macro_surface_buds_20260512f(st, limit)
    return fern_spiral_echo(st, limit, fraction=0.022, scale=0.975, angle_degrees=4.0, bridge_steps=50)


def fern_macro_pinnae_20260512f(st, limit):
    """Cell-scale alternating branchlets for visible compound-fern recursion."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    lateral = torch.sqrt((rel[:, ax0] / extent[ax0].clamp_min(1)) ** 2 + (rel[:, ax1] / extent[ax1].clamp_min(1)) ** 2)
    band = (height >= torch.quantile(height, 0.10)) & (height <= torch.quantile(height, 0.92))
    outer = lateral >= torch.quantile(lateral, 0.50)
    pool = band & outer
    if pool.sum() < 18:
        pool = outer
    if pool.sum() < 18:
        return st
    score = lateral + 0.12 * torch.cos((height - height.min()) / (height.max() - height.min()).clamp_min(1e-6) * torch.pi * 8.0)
    mask = cap_mask_by_score(pool, score, 72)
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    radial_norm = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = src_rel[:, ax0] / radial_norm
    radial[:, ax1] = src_rel[:, ax1] / radial_norm
    height_m = growth_height(src_xyz)
    h_norm = (height_m - height_m.min()) / (height_m.max() - height_m.min()).clamp_min(1e-6)
    alternate = torch.where(torch.sin(h_norm * torch.pi * 9.0) >= 0, 1.0, -1.0).to(src_xyz.device)
    side = torch.zeros_like(src_rel)
    side[:, ax0] = alternate
    side[:, ax1] = -0.30 * alternate
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    base_shift = torch.clamp(extent.max() * 0.115, min=2.1, max=3.6)
    side_shift = torch.clamp(extent.max() * 0.075, min=1.3, max=2.4)
    target_a = src_xyz + radial * base_shift + side * side_shift + forward * 1.2
    target_b = src_xyz + radial * (base_shift * 0.62) - side * (side_shift * 0.45) + forward * 0.7
    return attached_transform_masked_copies(st, mask, [torch.round(target_a), torch.round(target_b)], limit, bridge_steps=14)


def fern_macro_then_branchlets_20260512f(st, limit):
    st = fern_macro_pinnae_20260512f(st, limit)
    return fern_branchlet_pinnae_20260512b(st, limit)


def fern_macro_dense_20260512f(st, limit):
    st = fern_macro_pinnae_20260512f(st, limit)
    return fern_macro_pinnae_20260512f(st, limit)


def fiddlehead_attached_surface_buds_20260512h(st, limit):
    """Sparse tube-supported crozier buds for the 12h log-spiral pass.

    The 12g/v26f rows made depth changes visible, but they decoded as detached
    leaf clouds.  This version keeps one small target per pass and gives the
    decoder a compact tube cue from the source surface to the child handle.
    """

    import torch

    mask = _surface_band_mask_20260512e(st, lower_q=0.16, upper_q=0.82, lateral_q=0.72, max_tokens=28, min_tokens=10)
    if mask is None:
        return st
    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    radial_norm = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = src_rel[:, ax0] / radial_norm
    radial[:, ax1] = src_rel[:, ax1] / radial_norm
    tangent = torch.zeros_like(src_rel)
    tangent[:, ax0] = -radial[:, ax1]
    tangent[:, ax1] = radial[:, ax0]
    height = growth_height(src_xyz)
    h_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    phase = torch.where(torch.sin(h_norm * torch.pi * 4.0) >= 0, 1.0, -1.0).to(src_xyz.device)
    radial_shift = torch.clamp(extent.max() * 0.060, min=1.1, max=1.8)
    tangent_shift = torch.clamp(extent.max() * 0.025, min=0.4, max=0.8)
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    target = src_xyz + radial * radial_shift + tangent * phase[:, None] * tangent_shift + forward * 0.4
    return masked_target_copies_with_tube_support_20260511t(
        st,
        mask,
        [torch.round(target)],
        limit,
        support_radius=0.85,
        support_steps=9,
        max_support_tokens=120,
    )


def fiddlehead_attached_buds_then_micro_20260512h(st, limit):
    st = fiddlehead_attached_surface_buds_20260512h(st, limit)
    return fiddlehead_surface_microbuds_20260512e(st, limit)


def fern_attached_pinnae_20260512h(st, limit):
    """Low-count tube-supported child pinnae for compound fern fronds."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    lateral = torch.sqrt((rel[:, ax0] / extent[ax0].clamp_min(1)) ** 2 + (rel[:, ax1] / extent[ax1].clamp_min(1)) ** 2)
    band = (height_norm >= 0.18) & (height_norm <= 0.86)
    outer = lateral >= torch.quantile(lateral, 0.64)
    pool = band & outer
    if pool.sum() < 12:
        pool = band & (lateral >= torch.quantile(lateral, 0.56))
    if pool.sum() < 12:
        return st
    score = lateral + 0.10 * torch.cos(height_norm * torch.pi * 7.0)
    mask = cap_mask_by_score(pool, score, 34)
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    radial_norm = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = src_rel[:, ax0] / radial_norm
    radial[:, ax1] = src_rel[:, ax1] / radial_norm
    height_m = growth_height(src_xyz)
    h_norm = (height_m - height_m.min()) / (height_m.max() - height_m.min()).clamp_min(1e-6)
    alternate = torch.where(torch.sin(h_norm * torch.pi * 6.0) >= 0, 1.0, -1.0).to(src_xyz.device)
    side = torch.zeros_like(src_rel)
    side[:, ax0] = alternate
    side[:, ax1] = -0.22 * alternate
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    base_shift = torch.clamp(extent.max() * 0.055, min=1.2, max=2.0)
    side_shift = torch.clamp(extent.max() * 0.035, min=0.7, max=1.2)
    target = src_xyz + radial * base_shift + side * side_shift + forward * 0.55
    return masked_target_copies_with_tube_support_20260511t(
        st,
        mask,
        [torch.round(target)],
        limit,
        support_radius=0.75,
        support_steps=9,
        max_support_tokens=150,
    )


def fern_attached_pinnae_then_tiplets_20260512h(st, limit):
    st = fern_attached_pinnae_20260512h(st, limit)
    return fern_frond_tiplets(st, limit, fraction=0.022, lateral_ratio=0.012, upward_ratio=0.012, bridge_steps=34)


def fiddlehead_log_attached_patch_20260512i(st, limit):
    """One connected crozier-handle patch per pass; preserves the log spiral."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    h_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    lateral = torch.sqrt((rel[:, ax0] / extent[ax0].clamp_min(1)) ** 2 + (rel[:, ax1] / extent[ax1].clamp_min(1)) ** 2)
    pool = (h_norm >= 0.16) & (h_norm <= 0.84) & (lateral >= torch.quantile(lateral, 0.66))
    if pool.sum() < 8:
        pool = lateral >= torch.quantile(lateral, 0.70)
    score = lateral + 0.14 * torch.cos(h_norm * torch.pi * 5.0)
    mask = connected_patch_mask_20260512i(st, pool, score, max_tokens=22, radius=3.8, min_tokens=8)
    if mask is None:
        return st
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    radial_norm = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = src_rel[:, ax0] / radial_norm
    radial[:, ax1] = src_rel[:, ax1] / radial_norm
    tangent = torch.zeros_like(src_rel)
    tangent[:, ax0] = -radial[:, ax1]
    tangent[:, ax1] = radial[:, ax0]
    height_m = growth_height(src_xyz)
    h_m = (height_m - height_m.min()) / (height_m.max() - height_m.min()).clamp_min(1e-6)
    phase = torch.where(torch.sin(h_m * torch.pi * 3.0) >= 0, 1.0, -1.0).to(src_xyz.device)
    radial_shift = torch.clamp(extent.max() * 0.070, min=1.25, max=2.05)
    tangent_shift = torch.clamp(extent.max() * 0.030, min=0.55, max=0.95)
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    target = src_xyz + radial * radial_shift + tangent * phase[:, None] * tangent_shift + forward * 0.36
    return masked_target_copies_with_patch_support_20260512i(
        st,
        mask,
        [torch.round(target)],
        limit,
        support_radius=1.35,
        support_steps=14,
        max_support_tokens=220,
    )


def fiddlehead_log_attached_patch_double_20260512i(st, limit):
    st = fiddlehead_log_attached_patch_20260512i(st, limit)
    return fiddlehead_log_attached_patch_20260512i(st, limit)


def fern_handle_pinnae_20260512i(st, limit):
    """Grow from a connected pinna-handle patch, not from scattered leaf surfaces."""

    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    ax0, ax1 = lateral_axes()
    rel = xyz - center
    height = growth_height(xyz)
    h_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    lateral = torch.sqrt((rel[:, ax0] / extent[ax0].clamp_min(1)) ** 2 + (rel[:, ax1] / extent[ax1].clamp_min(1)) ** 2)
    mid_outer = (h_norm >= 0.20) & (h_norm <= 0.82) & (lateral >= torch.quantile(lateral, 0.50))
    if mid_outer.sum() < 10:
        mid_outer = (h_norm >= 0.18) & (h_norm <= 0.88)
    score = lateral + 0.10 * torch.cos(h_norm * torch.pi * 6.0)
    mask = connected_patch_mask_20260512i(st, mid_outer, score, max_tokens=26, radius=4.2, min_tokens=10)
    if mask is None:
        return st
    src_xyz = xyz[mask]
    src_rel = src_xyz - center
    radial_norm = torch.sqrt(src_rel[:, ax0] ** 2 + src_rel[:, ax1] ** 2).clamp_min(1e-6)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = src_rel[:, ax0] / radial_norm
    radial[:, ax1] = src_rel[:, ax1] / radial_norm
    height_m = growth_height(src_xyz)
    h_m = (height_m - height_m.min()) / (height_m.max() - height_m.min()).clamp_min(1e-6)
    alternate = torch.where(torch.sin(h_m * torch.pi * 4.0) >= 0, 1.0, -1.0).to(src_xyz.device)
    side = torch.zeros_like(src_rel)
    side[:, ax0] = alternate
    side[:, ax1] = -0.18 * alternate
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    base_shift = torch.clamp(extent.max() * 0.060, min=1.35, max=2.15)
    side_shift = torch.clamp(extent.max() * 0.034, min=0.72, max=1.22)
    target = src_xyz + radial * base_shift + side * side_shift + forward * 0.48
    return masked_target_copies_with_patch_support_20260512i(
        st,
        mask,
        [torch.round(target)],
        limit,
        support_radius=1.35,
        support_steps=14,
        max_support_tokens=240,
    )


def fern_handle_tiplets_20260512i(st, limit):
    return fern_frond_tiplets(st, limit, fraction=0.016, lateral_ratio=0.010, upward_ratio=0.010, bridge_steps=36)


def fern_handle_pinnae_light_tiplets_20260512i(st, limit):
    st = fern_handle_pinnae_20260512i(st, limit)
    return fern_handle_tiplets_20260512i(st, limit)


def pine_branch_frontier_needle_whorl_20260511p(st, limit):
    """More readable V23 pine leaf-side frontier than the 20260511o no-op-ish row."""

    st = crown_bud_attached(st, limit, fraction=0.045, shift_ratio=0.030, bridge_steps=34)
    st = fern_frond_tiplets(st, limit, fraction=0.026, lateral_ratio=0.016, upward_ratio=0.020, bridge_steps=34)
    return crown_bud_attached(st, limit, fraction=0.018, shift_ratio=0.014, bridge_steps=34)


def root_first_split_sidecar_handles_20260511p(
    st,
    limit,
    fraction=0.38,
    scale=0.72,
    angle_degrees=54.0,
    radial_ratio=0.105,
    forward_ratio=0.115,
    max_source_tokens=220,
    min_tokens=8,
    bridge_steps=36,
):
    """Copy a thicker first-split root handle into attached sidecar branches.

    The 20260511o rootfan rows selected plausible root regions but transformed
    them mostly inside the original bbox.  This variant chooses a mid-to-outer
    branch band, caps the source tokens, and adds explicit radial plus growth
    displacement so the depth sequence can fail or pass visually, not as a
    silent no-op.
    """

    import math
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    center = (lo.float() + hi.float()) / 2
    ax0, ax1 = lateral_axes()
    height = growth_height(xyz)
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2).clamp_min(1e-6)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    lateral_norm = lateral / lateral.max().clamp_min(1e-6)

    h_low = torch.quantile(height, 0.24)
    h_high = torch.quantile(height, 1.0 - max(0.035, fraction * 0.12))
    band = (height >= h_low) & (height <= h_high)
    outer = lateral >= torch.quantile(lateral, 0.34)
    pool = band & outer
    if pool.sum() < min_tokens:
        pool = (height >= torch.quantile(height, 0.18)) & (lateral >= torch.quantile(lateral, 0.26))
    if pool.sum() < min_tokens:
        return st

    score = lateral_norm + 0.35 * height_norm
    pool_idx = torch.nonzero(pool, as_tuple=False).flatten()
    proto_idx = pool_idx[torch.argmax(score[pool_idx])]
    proto = torch.stack([rel[proto_idx, ax0], rel[proto_idx, ax1]])
    proto = proto / torch.linalg.norm(proto).clamp_min(1e-6)
    lateral_vec = torch.stack([rel[:, ax0], rel[:, ax1]], dim=1)
    cos_to_proto = (lateral_vec @ proto) / lateral
    wedge = pool & (cos_to_proto >= math.cos(math.radians(angle_degrees)))
    if wedge.sum() < min_tokens:
        threshold = torch.quantile(cos_to_proto[pool], 0.50)
        wedge = pool & (cos_to_proto >= threshold)
    if wedge.sum() < min_tokens:
        wedge = pool
    wedge = cap_mask_by_score(wedge, score, max_source_tokens)

    src_xyz = xyz[wedge]
    src_rel = src_xyz - center
    src_lat = torch.stack([src_rel[:, ax0], src_rel[:, ax1]], dim=1)
    proto_perp = torch.stack([-proto[1], proto[0]])
    parallel = src_lat @ proto
    side = src_lat @ proto_perp
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = proto[0]
    radial[:, ax1] = proto[1]

    targets = []
    for sign in (-1, 1):
        theta = math.radians(float(sign) * 28.0)
        target_dir = torch.stack(
            [proto[0] * math.cos(theta) - proto[1] * math.sin(theta), proto[0] * math.sin(theta) + proto[1] * math.cos(theta)]
        )
        target_perp = torch.stack([-target_dir[1], target_dir[0]])
        target_rel = src_rel.clone()
        target_rel[:, ax0] = (parallel * target_dir[0] + side * target_perp[0]) * scale
        target_rel[:, ax1] = (parallel * target_dir[1] + side * target_perp[1]) * scale
        target_rel[:, GROWTH_AXIS] = src_rel[:, GROWTH_AXIS] * (0.72 + 0.10 * scale)
        target = center + target_rel + radial * extent * radial_ratio + forward * extent * forward_ratio
        targets.append(torch.round(target))
    return attached_transform_masked_copies(st, wedge, targets, limit, bridge_steps=bridge_steps)


def root_first_split_then_rootlets_20260511p(st, limit):
    """Depth-visible root branch handles followed by only tiny late rootlets."""

    st = root_first_split_sidecar_handles_20260511p(
        st,
        limit,
        fraction=0.34,
        scale=0.74,
        angle_degrees=58.0,
        radial_ratio=0.120,
        forward_ratio=0.125,
        max_source_tokens=180,
        min_tokens=8,
        bridge_steps=38,
    )
    return root_shrink_fork_20260511h(
        st,
        limit,
        fraction=0.024,
        scale=0.70,
        lateral_ratio=0.012,
        forward_ratio=0.016,
        bridge_steps=34,
    )


def root_module_sidecar_20260511q(st, limit):
    """First-split sidecar tuned for clean q root modules.

    Unlike the p rows, q inputs are already compact first-split modules with
    explicit trunk/branch handles.  Use a narrower mask and fewer source tokens
    so the child root reads as a smaller attached branch instead of a whole-root
    clone.
    """

    return root_first_split_sidecar_handles_20260511p(
        st,
        limit,
        fraction=0.24,
        scale=0.66,
        angle_degrees=42.0,
        radial_ratio=0.075,
        forward_ratio=0.095,
        max_source_tokens=92,
        min_tokens=5,
        bridge_steps=44,
    )


def root_module_chain_20260511q(st, limit):
    """Hierarchy-first q schedule: attached first split, then tiny taper fork."""

    st = root_module_sidecar_20260511q(st, limit)
    return root_shrink_fork_20260511h(
        st,
        limit,
        fraction=0.018,
        scale=0.62,
        lateral_ratio=0.010,
        forward_ratio=0.014,
        bridge_steps=38,
    )


def root_module_dense_rootlets_20260511q(st, limit):
    """Conservative q variant for denser rootlet input modules."""

    st = root_first_split_sidecar_handles_20260511p(
        st,
        limit,
        fraction=0.18,
        scale=0.62,
        angle_degrees=36.0,
        radial_ratio=0.060,
        forward_ratio=0.080,
        max_source_tokens=64,
        min_tokens=5,
        bridge_steps=48,
    )
    return root_shrink_fork_20260511h(
        st,
        limit,
        fraction=0.012,
        scale=0.58,
        lateral_ratio=0.008,
        forward_ratio=0.010,
        bridge_steps=42,
    )


def root_module_coarse_branch_20260511r(
    st,
    limit,
    fraction=0.22,
    scale=0.62,
    angle_degrees=30.0,
    radial_ratio=0.080,
    forward_ratio=0.090,
    max_source_tokens=54,
    min_tokens=4,
    bridge_steps=56,
    pair=False,
):
    """Coarse first-split branch growth after the q rootlet-dust failure.

    q proved that copying terminal/rootlet-heavy sparse regions makes small
    islands instead of a publication-grade thick-to-thin root hierarchy.  r
    selects a thicker mid-branch band, caps it aggressively, and moves one
    coherent side branch with long bridges.  Fine rootlets are intentionally
    excluded from the primary operator.
    """

    import math
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    center = (lo.float() + hi.float()) / 2
    ax0, ax1 = lateral_axes()
    height = growth_height(xyz)
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2).clamp_min(1e-6)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    lateral_norm = lateral / lateral.max().clamp_min(1e-6)

    h_low = torch.quantile(height, 0.24)
    h_high = torch.quantile(height, 1.0 - max(0.08, fraction * 0.20))
    band = (height >= h_low) & (height <= h_high)
    outer = lateral >= torch.quantile(lateral, 0.30)
    pool = band & outer
    if pool.sum() < min_tokens:
        pool = (height >= torch.quantile(height, 0.18)) & (height <= torch.quantile(height, 0.88))
    if pool.sum() < min_tokens:
        return st

    score = lateral_norm + 0.18 * height_norm
    pool_idx = torch.nonzero(pool, as_tuple=False).flatten()
    proto_idx = pool_idx[torch.argmax(score[pool_idx])]
    proto = torch.stack([rel[proto_idx, ax0], rel[proto_idx, ax1]])
    proto = proto / torch.linalg.norm(proto).clamp_min(1e-6)
    lateral_vec = torch.stack([rel[:, ax0], rel[:, ax1]], dim=1)
    cos_to_proto = (lateral_vec @ proto) / lateral
    wedge = pool & (cos_to_proto >= math.cos(math.radians(angle_degrees)))
    if wedge.sum() < min_tokens:
        threshold = torch.quantile(cos_to_proto[pool], 0.62)
        wedge = pool & (cos_to_proto >= threshold)
    if wedge.sum() < min_tokens:
        wedge = pool
    wedge = cap_mask_by_score(wedge, score, max_source_tokens)

    src_xyz = xyz[wedge]
    src_rel = src_xyz - center
    src_lat = torch.stack([src_rel[:, ax0], src_rel[:, ax1]], dim=1)
    proto_perp = torch.stack([-proto[1], proto[0]])
    parallel = src_lat @ proto
    side = src_lat @ proto_perp
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = proto[0]
    radial[:, ax1] = proto[1]

    signs = (-1, 1) if pair else (1,)
    targets = []
    for sign in signs:
        theta = math.radians(float(sign) * 24.0)
        target_dir = torch.stack(
            [proto[0] * math.cos(theta) - proto[1] * math.sin(theta), proto[0] * math.sin(theta) + proto[1] * math.cos(theta)]
        )
        target_perp = torch.stack([-target_dir[1], target_dir[0]])
        target_rel = src_rel.clone()
        target_rel[:, ax0] = (parallel * target_dir[0] + side * target_perp[0]) * scale
        target_rel[:, ax1] = (parallel * target_dir[1] + side * target_perp[1]) * scale
        target_rel[:, GROWTH_AXIS] = src_rel[:, GROWTH_AXIS] * (0.70 + 0.12 * scale)
        target = center + target_rel + radial * extent * radial_ratio + forward * extent * forward_ratio
        targets.append(torch.round(target))
    return attached_transform_masked_copies(st, wedge, targets, limit, bridge_steps=bridge_steps)


def root_module_coarse_pair_20260511r(st, limit):
    """Two coarse child branches, no fine rootlets."""

    return root_module_coarse_branch_20260511r(
        st,
        limit,
        fraction=0.24,
        scale=0.60,
        angle_degrees=34.0,
        radial_ratio=0.072,
        forward_ratio=0.082,
        max_source_tokens=44,
        min_tokens=4,
        bridge_steps=58,
        pair=True,
    )


def root_module_coarse_visible_20260511r(st, limit):
    """Single more visible coarse side branch for depth-change QA."""

    return root_module_coarse_branch_20260511r(
        st,
        limit,
        fraction=0.20,
        scale=0.58,
        angle_degrees=28.0,
        radial_ratio=0.100,
        forward_ratio=0.118,
        max_source_tokens=48,
        min_tokens=4,
        bridge_steps=64,
        pair=False,
    )


def root_module_coarse_then_hairline_20260511r(st, limit):
    """Coarse branch first, then a very small late terminal detail diagnostic."""

    st = root_module_coarse_visible_20260511r(st, limit)
    return root_shrink_fork_20260511h(
        st,
        limit,
        fraction=0.008,
        scale=0.66,
        lateral_ratio=0.006,
        forward_ratio=0.008,
        bridge_steps=44,
    )


def root_module_visible_child_20260511s(
    st,
    limit,
    fraction=0.36,
    scale=0.72,
    angle_degrees=18.0,
    radial_ratio=0.18,
    forward_ratio=0.22,
    max_source_tokens=96,
    min_tokens=6,
    bridge_steps=30,
    pair=False,
):
    """Grow a visibly displaced coarse child branch for the s repair batch.

    The r operators preserved connectivity but usually decoded as almost the
    same root with a few terminal specks.  This variant deliberately selects a
    mid-body branch handle, not the fragile terminal tips, then moves that
    handle several sparse cells outward and along the root growth direction.
    That makes the d0..d4 sequence fail or pass visually instead of hiding as a
    metric-clean near-no-op.
    """

    import math
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    center = (lo.float() + hi.float()) / 2
    ax0, ax1 = lateral_axes()
    height = growth_height(xyz)
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2).clamp_min(1e-6)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    lateral_norm = lateral / lateral.max().clamp_min(1e-6)

    h_low = torch.quantile(height, 0.18)
    h_high = torch.quantile(height, min(0.86, 1.0 - max(0.08, fraction * 0.16)))
    band = (height >= h_low) & (height <= h_high)
    outer = lateral >= torch.quantile(lateral, 0.24)
    pool = band & outer
    if pool.sum() < min_tokens:
        pool = (height >= torch.quantile(height, 0.12)) & (height <= torch.quantile(height, 0.90))
    if pool.sum() < min_tokens:
        return st

    score = lateral_norm + 0.14 * height_norm
    pool_idx = torch.nonzero(pool, as_tuple=False).flatten()
    proto_idx = pool_idx[torch.argmax(score[pool_idx])]
    proto = torch.stack([rel[proto_idx, ax0], rel[proto_idx, ax1]])
    proto = proto / torch.linalg.norm(proto).clamp_min(1e-6)
    lateral_vec = torch.stack([rel[:, ax0], rel[:, ax1]], dim=1)
    cos_to_proto = (lateral_vec @ proto) / lateral
    wedge = pool & (cos_to_proto >= math.cos(math.radians(42.0)))
    if wedge.sum() < min_tokens:
        threshold = torch.quantile(cos_to_proto[pool], 0.54)
        wedge = pool & (cos_to_proto >= threshold)
    if wedge.sum() < min_tokens:
        wedge = pool
    wedge = cap_mask_by_score(wedge, score, max_source_tokens)

    src_xyz = xyz[wedge]
    src_rel = src_xyz - center
    src_lat = torch.stack([src_rel[:, ax0], src_rel[:, ax1]], dim=1)
    proto_perp = torch.stack([-proto[1], proto[0]])
    parallel = src_lat @ proto
    side = src_lat @ proto_perp
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = proto[0]
    radial[:, ax1] = proto[1]

    signs = (-1, 1) if pair else (1,)
    targets = []
    for sign in signs:
        theta = math.radians(float(sign) * angle_degrees)
        target_dir = torch.stack(
            [proto[0] * math.cos(theta) - proto[1] * math.sin(theta), proto[0] * math.sin(theta) + proto[1] * math.cos(theta)]
        )
        target_perp = torch.stack([-target_dir[1], target_dir[0]])
        target_rel = src_rel.clone()
        target_rel[:, ax0] = (parallel * target_dir[0] + side * target_perp[0]) * scale
        target_rel[:, ax1] = (parallel * target_dir[1] + side * target_perp[1]) * scale
        target_rel[:, GROWTH_AXIS] = src_rel[:, GROWTH_AXIS] * (0.74 + 0.10 * scale)
        target = center + target_rel + radial * extent * radial_ratio + forward * extent * forward_ratio
        targets.append(torch.round(target))
    return attached_transform_masked_copies(st, wedge, targets, limit, bridge_steps=bridge_steps)


def root_module_visible_child_far_20260511s(st, limit):
    """Single coarse child with stronger displacement for visual gate testing."""

    return root_module_visible_child_20260511s(
        st,
        limit,
        fraction=0.38,
        scale=0.70,
        angle_degrees=14.0,
        radial_ratio=0.22,
        forward_ratio=0.26,
        max_source_tokens=88,
        min_tokens=6,
        bridge_steps=28,
        pair=False,
    )


def root_module_visible_child_pair_20260511s(st, limit):
    """Two attached coarse children; higher risk but should expose depth change."""

    return root_module_visible_child_20260511s(
        st,
        limit,
        fraction=0.34,
        scale=0.68,
        angle_degrees=24.0,
        radial_ratio=0.16,
        forward_ratio=0.20,
        max_source_tokens=72,
        min_tokens=6,
        bridge_steps=30,
        pair=True,
    )


def root_module_visible_child_late_taper_20260511s(st, limit):
    """Coarse visible child plus a tiny taper diagnostic, not a main positive."""

    st = root_module_visible_child_far_20260511s(st, limit)
    return root_shrink_fork_20260511h(
        st,
        limit,
        fraction=0.006,
        scale=0.72,
        lateral_ratio=0.004,
        forward_ratio=0.006,
        bridge_steps=36,
    )


def root_module_supported_child_20260511t(
    st,
    limit,
    fraction=0.30,
    scale=0.74,
    angle_degrees=16.0,
    radial_ratio=0.13,
    forward_ratio=0.17,
    max_source_tokens=56,
    min_tokens=5,
    support_radius=1.10,
    support_steps=9,
    pair=False,
):
    """Coarse first-split child with explicit tube support for t.

    s showed that a visible sparse-latent displacement alone decodes as torn
    bark fragments.  t keeps the moved branch handle smaller and adds a direct
    sparse tube between source and target anchors, aiming for a continuous
    thick child root before any fine rootlet detail is allowed.
    """

    import math
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi.float() - lo.float()).clamp_min(1)
    center = (lo.float() + hi.float()) / 2
    ax0, ax1 = lateral_axes()
    height = growth_height(xyz)
    rel = xyz - center
    lateral = torch.sqrt(rel[:, ax0] ** 2 + rel[:, ax1] ** 2).clamp_min(1e-6)
    height_norm = (height - height.min()) / (height.max() - height.min()).clamp_min(1e-6)
    lateral_norm = lateral / lateral.max().clamp_min(1e-6)

    h_low = torch.quantile(height, 0.16)
    h_high = torch.quantile(height, 0.78)
    band = (height >= h_low) & (height <= h_high)
    outer = lateral >= torch.quantile(lateral, 0.22)
    pool = band & outer
    if pool.sum() < min_tokens:
        pool = (height >= torch.quantile(height, 0.10)) & (height <= torch.quantile(height, 0.86))
    if pool.sum() < min_tokens:
        return st

    score = lateral_norm + 0.12 * height_norm
    pool_idx = torch.nonzero(pool, as_tuple=False).flatten()
    proto_idx = pool_idx[torch.argmax(score[pool_idx])]
    proto = torch.stack([rel[proto_idx, ax0], rel[proto_idx, ax1]])
    proto = proto / torch.linalg.norm(proto).clamp_min(1e-6)
    lateral_vec = torch.stack([rel[:, ax0], rel[:, ax1]], dim=1)
    cos_to_proto = (lateral_vec @ proto) / lateral
    wedge = pool & (cos_to_proto >= math.cos(math.radians(36.0)))
    if wedge.sum() < min_tokens:
        threshold = torch.quantile(cos_to_proto[pool], 0.58)
        wedge = pool & (cos_to_proto >= threshold)
    if wedge.sum() < min_tokens:
        wedge = pool
    wedge = cap_mask_by_score(wedge, score, max_source_tokens)

    src_xyz = xyz[wedge]
    src_rel = src_xyz - center
    src_lat = torch.stack([src_rel[:, ax0], src_rel[:, ax1]], dim=1)
    proto_perp = torch.stack([-proto[1], proto[0]])
    parallel = src_lat @ proto
    side = src_lat @ proto_perp
    forward = torch.zeros_like(src_rel)
    forward[:, GROWTH_AXIS] = float(GROWTH_SIGN)
    radial = torch.zeros_like(src_rel)
    radial[:, ax0] = proto[0]
    radial[:, ax1] = proto[1]

    signs = (-1, 1) if pair else (1,)
    targets = []
    for sign in signs:
        theta = math.radians(float(sign) * angle_degrees)
        target_dir = torch.stack(
            [proto[0] * math.cos(theta) - proto[1] * math.sin(theta), proto[0] * math.sin(theta) + proto[1] * math.cos(theta)]
        )
        target_perp = torch.stack([-target_dir[1], target_dir[0]])
        target_rel = src_rel.clone()
        target_rel[:, ax0] = (parallel * target_dir[0] + side * target_perp[0]) * scale
        target_rel[:, ax1] = (parallel * target_dir[1] + side * target_perp[1]) * scale
        target_rel[:, GROWTH_AXIS] = src_rel[:, GROWTH_AXIS] * (0.78 + 0.08 * scale)
        target = center + target_rel + radial * extent * radial_ratio + forward * extent * forward_ratio
        targets.append(torch.round(target))

    return masked_target_copies_with_tube_support_20260511t(
        st,
        wedge,
        targets,
        limit,
        support_radius=support_radius,
        support_steps=support_steps,
        max_support_tokens=220,
    )


def root_module_supported_child_single_20260511t(st, limit):
    """Single supported child branch; the primary t candidate."""

    return root_module_supported_child_20260511t(
        st,
        limit,
        fraction=0.30,
        scale=0.76,
        angle_degrees=12.0,
        radial_ratio=0.12,
        forward_ratio=0.16,
        max_source_tokens=48,
        min_tokens=5,
        support_radius=1.15,
        support_steps=10,
        pair=False,
    )


def root_module_supported_child_pair_20260511t(st, limit):
    """Two supported child branches, used as a stress/backup candidate."""

    return root_module_supported_child_20260511t(
        st,
        limit,
        fraction=0.28,
        scale=0.72,
        angle_degrees=20.0,
        radial_ratio=0.10,
        forward_ratio=0.14,
        max_source_tokens=42,
        min_tokens=5,
        support_radius=1.05,
        support_steps=9,
        pair=True,
    )


def root_module_supported_child_micro_20260511t(st, limit):
    """Conservative t variant for metrics-first sanity checking."""

    return root_module_supported_child_20260511t(
        st,
        limit,
        fraction=0.24,
        scale=0.82,
        angle_degrees=8.0,
        radial_ratio=0.075,
        forward_ratio=0.105,
        max_source_tokens=32,
        min_tokens=5,
        support_radius=1.0,
        support_steps=8,
        pair=False,
    )


def portal_attached_insert(st, limit, scale=0.58, y_shift_ratio=0.12, bridge_steps=4):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (xyz.min(0).values + xyz.max(0).values) / 2
    extent = (hi - lo).clamp_min(1)
    copied_xyz = torch.round((xyz - center) * scale + center)
    copied_xyz[:, GROWTH_AXIS] += GROWTH_SIGN * max(1, int(extent[GROWTH_AXIS].item() * y_shift_ratio))
    return attached_transform_copies(st, [copied_xyz], limit, bridge_steps=bridge_steps)


def radial4_y_attached_clone(st, limit, scale=0.72, bridge_steps=3):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    center = (xyz.min(0).values + xyz.max(0).values) / 2
    rel = xyz - center
    targets = []
    for k in range(1, 4):
        if k == 1:
            rotated = torch.stack([-rel[:, 2], rel[:, 1], rel[:, 0]], dim=1)
        elif k == 2:
            rotated = torch.stack([-rel[:, 0], rel[:, 1], -rel[:, 2]], dim=1)
        else:
            rotated = torch.stack([rel[:, 2], rel[:, 1], -rel[:, 0]], dim=1)
        targets.append(torch.round(rotated * scale + center))
    return attached_transform_copies(st, targets, limit, bridge_steps=bridge_steps)


def translate_attached_clone(st, limit, axis: int, shift_ratio=0.20, bridge_steps=4):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    extent = (hi - lo).clamp_min(1)
    target = xyz.clone()
    target[:, axis] += max(1, int(extent[axis].item() * shift_ratio))
    return attached_transform_copies(st, [target], limit, bridge_steps=bridge_steps)


def compete_grow(st, limit, tip_fraction=0.32, attractor_count=96, step_ratio=0.10):
    import torch

    coords = st.coords
    xyz = coords[:, 1:].float()
    lo, hi = coord_bounds(st)
    center = (lo.float() + hi.float()) / 2
    extent = (hi.float() - lo.float()).clamp_min(1)
    y_threshold = torch.quantile(growth_height(xyz), 1.0 - tip_fraction)
    radius = torch.linalg.norm((xyz - center) / extent.clamp_min(1), dim=1)
    radius_threshold = torch.quantile(radius, 0.62)
    tip_mask = (growth_height(xyz) >= y_threshold) | (radius >= radius_threshold)
    tip_indices = torch.nonzero(tip_mask, as_tuple=False).flatten()
    if tip_indices.numel() == 0:
        return st

    angles = torch.linspace(0, 2 * torch.pi, attractor_count + 1, device=xyz.device)[:-1]
    bands = torch.arange(attractor_count, device=xyz.device) % 4
    band_height = 0.20 + 0.13 * bands.float()
    ax0, ax1 = lateral_axes()
    shell = torch.zeros((attractor_count, 3), device=xyz.device, dtype=xyz.dtype)
    shell[:, ax0] = torch.cos(angles) * extent[ax0] * 0.52
    shell[:, GROWTH_AXIS] = GROWTH_SIGN * extent[GROWTH_AXIS] * band_height
    shell[:, ax1] = torch.sin(angles) * extent[ax1] * 0.52
    if COMPETE_JITTER > 0 and COMPETE_GENERATOR is not None:
        shell_noise = torch.randn(
            shell.shape,
            generator=COMPETE_GENERATOR,
            device=shell.device,
            dtype=shell.dtype,
        )
        shell = shell + shell_noise * extent * COMPETE_JITTER
    attractors = center + shell
    tip_xyz = xyz[tip_indices]
    nearest = torch.cdist(attractors, tip_xyz).argmin(dim=1)
    selected = torch.unique(nearest)

    new_coords = []
    new_feats = []
    step = torch.clamp(torch.round(extent * step_ratio), min=1)
    for local_idx in selected.tolist():
        assigned = attractors[nearest == local_idx]
        direction = assigned.mean(dim=0) - tip_xyz[local_idx]
        norm = torch.linalg.norm(direction).clamp_min(1e-6)
        delta = torch.round(direction / norm * step).to(coords.dtype)
        if torch.all(delta == 0):
            delta[GROWTH_AXIS] = GROWTH_SIGN
        src_idx = tip_indices[local_idx]
        copied = coords[src_idx].clone()
        copied[1:] = copied[1:] + delta
        new_coords.append(copied[None, :])
        new_feats.append(st.feats[src_idx : src_idx + 1].clone())
    if not new_coords:
        return st
    copied_coords = torch.cat(new_coords, dim=0)
    copied_feats = torch.cat(new_feats, dim=0)
    valid = clip_valid(copied_coords, limit)
    if valid.sum() == 0:
        return st
    return sparse_merge(
        torch.cat([st.feats, copied_feats[valid]], dim=0),
        torch.cat([coords, copied_coords[valid]], dim=0),
    )


GRAMMARS = {
    "continue": ["tip_continue"],
    "fork": ["tip_fork"],
    "side": ["side_branch"],
    "fork_side": ["tip_fork", "side_branch"],
    "radial": ["radial_y_clone"],
    "echo": ["shrink_echo", "tip_continue"],
    "mirror": ["mirror_x"],
    "mirror_fork": ["mirror_x", "tip_fork"],
    "translate_x": ["translate_x_clone"],
    "translate_y": ["translate_y_clone"],
    "rotate_z": ["rotate_z_clone"],
    "scale_up": ["scale_up_clone"],
    "scale_down": ["shrink_echo"],
    "radial4": ["radial4_y_clone"],
    "portal": ["portal_insert"],
    "radial4_attach": ["radial4_y_attached_clone"],
    "portal_attach": ["portal_attached_insert"],
    "translate_x_attach": ["translate_x_attached_clone"],
    "ornament_portal_attach": ["portal_attached_insert", "radial4_y_attached_clone"],
    "arch_portal_attach": ["portal_attached_insert", "shrink_echo"],
    "radial_frontier_attach": ["radial_frontier_attached_clone"],
    "ornament_bud_attach": ["ornament_crown_buds"],
    "ornament_rim_micro_attach": ["ornament_rim_micro_buds"],
    "ornament_frontier_attach": ["radial_frontier_attached_clone", "ornament_crown_buds"],
    "arch_keystone_attach": ["arch_keystone_buds"],
    "socket_translate_attach": ["socket_translate_attached_clone"],
    "socket_tight_attach": ["socket_translate_tight_attached_clone"],
    "scale_down_attach": ["scale_down_attached_clone"],
    "city_rooftop_scale_attach": ["rooftop_scale_buds", "scale_down_attached_clone"],
    "leaf_basal_fan_attach": ["leaf_basal_fan_attached_clone"],
    "leaf_basal_micro_attach": ["leaf_basal_micro_buds"],
    "leaf_basal_fan_micro_attach": ["leaf_basal_fan_attached_clone", "leaf_basal_micro_buds"],
    "leaf_basal_handle_attach": ["leaf_basal_handle_blades"],
    "leaf_basal_handle_micro_attach": ["leaf_basal_handle_blades", "leaf_basal_micro_buds"],
    "fern_frond_tip_attach": ["fern_frond_tiplets"],
    "fern_frond_pinnae_attach": ["fern_midrib_pinnae", "fern_frond_tiplets"],
    "fern_spiral_echo_attach": ["fern_spiral_echo"],
    "fern_recursive_frond_attach": ["fern_midrib_pinnae", "fern_frond_tiplets", "crown_bud_attached"],
    "v25e_crown_bud_micro": ["crown_bud_micro_20260511e"],
    "v25e_crown_scatter_fork": ["crown_scatter_micro_fork_20260511e"],
    "v25e_rim_leaflet_micro": ["rim_leaflet_micro_20260511e"],
    "v25e_crown_tiplet_short": ["crown_bud_micro_20260511e", "tiplet_short_20260511e"],
    "v25e_root_basal_micro": ["basal_micro_short_20260511e"],
    "v25e_root_rim_tiplet": ["rim_leaflet_micro_20260511e", "tiplet_short_20260511e"],
    "v25e_root_crown_micro": ["crown_bud_micro_20260511e", "rim_leaflet_micro_20260511e"],
    "v25g_root_crown_conservative": ["root_crown_micro_conservative_20260511g"],
    "v25g_root_plantlet_sprout": ["root_plantlet_sprout_20260511g"],
    "v25g_root_crown_then_sprout": ["root_crown_micro_conservative_20260511g", "root_plantlet_sprout_20260511g"],
    "v25h_spider_basal_crown_micro": ["spider_basal_crown_micro_20260511h"],
    "v25h_spider_leaf_tiplet_micro": ["spider_leaf_tiplet_micro_20260511h"],
    "v25h_spider_runner_distal_micro": ["spider_runner_distal_micro_20260511h"],
    "v25h_spider_basal_then_tiplet": ["spider_basal_then_tiplet_20260511h"],
    "v25h_tree_root_shrink_fork": ["root_shrink_fork_20260511h"],
    "v25h_tree_root_fork_tiplet": ["root_shrink_fork_tiplet_20260511h"],
    "v25j_spider_leaf_handle_visible": ["spider_leaf_handle_visible_20260511j"],
    "v25j_spider_leaf_handle_compact": ["spider_leaf_handle_compact_20260511j"],
    "v25j_spider_leaf_schedule": ["spider_leaf_schedule_20260511j"],
    "v25j_tree_root_clean_fork": ["root_shrink_fork_clean_20260511j"],
    "v25j_tree_root_wedge_fork": ["root_wedge_fork_clean_20260511j"],
    "v25j_tree_root_wedge_then_clean": ["root_wedge_then_clean_20260511j"],
    "v25j_crown_rim_gem": ["crown_rim_gem_array_20260511j"],
    "v25j_crown_rim_gem_bud": ["crown_rim_gem_array_20260511j", "ornament_rim_micro_buds"],
    "v25j_mecha_socket_fin": ["mecha_socket_fin_array_20260511j"],
    "v25j_mecha_socket_tight_fin": ["socket_translate_tight_attached_clone", "mecha_socket_fin_array_20260511j"],
    "v25j_city_rooftop_tower": ["city_rooftop_tower_array_20260511j"],
    "v25j_city_nested_scale": ["city_rooftop_tower_array_20260511j", "scale_down_attached_clone"],
    "v25j_castle_turret": ["castle_turret_battlement_20260511j"],
    "v25j_castle_turret_keystone": ["castle_turret_battlement_20260511j", "arch_keystone_buds"],
    "v25k_spider_terminal_leaflet": ["spider_terminal_leaflet_visible_20260511k"],
    "v25k_spider_basal_leaflet_arc": ["spider_basal_leaflet_arc_20260511k"],
    "v25k_spider_balanced_leaflet": ["spider_balanced_leaflet_20260511k"],
    "v25k_fiddlehead_curl_echo": ["fiddlehead_curl_echo_20260511k"],
    "v25k_fiddlehead_curl_pinnae": ["fiddlehead_curl_pinnae_20260511k"],
    "v25k_pine_terminal_needles": ["pine_terminal_needles_20260511k"],
    "v25k_root_single_wedge": ["root_single_wedge_branch_20260511k"],
    "v25k_root_single_then_tiplets": ["root_single_then_tiplets_20260511k"],
    "v25k_crown_clean_gem": ["crown_rim_gem_clean_20260511k"],
    "v25k_mecha_clean_fin": ["mecha_socket_fin_clean_20260511k"],
    "v25k_city_clean_tower": ["city_rooftop_tower_clean_20260511k"],
    "v25k_castle_clean_turret": ["castle_turret_clean_20260511k"],
    "v25l_root_relaxed_wedge": ["root_relaxed_wedge_branch_20260511l"],
    "v25l_root_primary_branch": ["root_primary_branch_cut_20260511l"],
    "v25l_root_two_phase": ["root_two_phase_hierarchy_20260511l"],
    "v25l_root_two_phase_rootlets": ["root_two_phase_late_rootlets_20260511l"],
    "v25l_spider_leaf_cluster_compact": ["spider_leaf_cluster_compact_20260511l"],
    "v25l_spider_leaf_treecrown": ["spider_leaf_treecrown_schedule_20260511l"],
    "v25l_spider_leaf_tip_clean": ["spider_leaf_tip_clean_20260511l"],
    "v25l_fiddlehead_guarded_curl": ["fiddlehead_guarded_curl_20260511l"],
    "v25l_pine_leaf_cluster_clean": ["pine_leaf_cluster_clean_20260511l"],
    "v25l_pine_branch_tip_cluster": ["pine_branch_tip_cluster_20260511l"],
    "v25n_plant_basal_midrib_leaflet": ["plant_basal_midrib_leaflet_20260511n"],
    "v25n_plant_basal_crown_leaflets": ["plant_basal_crown_leaflets_20260511n"],
    "v25n_spider_runner_leaflet_gated": ["spider_runner_leaflet_gated_20260511n"],
    "v25n_fern_pinnae_sparse": ["fern_pinnae_sparse_attach_20260511n"],
    "v25n_fiddlehead_thick_curl": ["fiddlehead_thick_curl_20260511n"],
    "v25n_root_short_terminal_rootlets": ["root_short_terminal_rootlets_20260511n"],
    "v25n_root_first_split_taper": ["root_first_split_taper_20260511n"],
    "v25n_pine_leaf_gated": ["pine_leaf_gated_20260511n"],
    "v25l_city_roof_podium": ["city_roof_podium_20260511l"],
    "v25l_city_roof_corners": ["city_roof_corner_towers_20260511l"],
    "v25l_city_podium_then_corners": ["city_roof_podium_20260511l", "city_roof_corner_towers_20260511l"],
    "v25l_castle_turret_caps": ["castle_turret_caps_20260511l"],
    "v25l_castle_battlement_strip": ["castle_battlement_strip_20260511l"],
    "v25l_castle_turret_then_battlement": ["castle_turret_caps_20260511l", "castle_battlement_strip_20260511l"],
    "v25l_mecha_socket_pods": ["mecha_socket_pods_20260511l"],
    "v25m_city_macro_stack": ["city_macro_tower_stack_20260511m"],
    "v25m_city_quadrant_stamps": ["city_quadrant_tower_stamps_20260511m"],
    "v25m_city_stack_then_quadrants": ["city_macro_tower_stack_20260511m", "city_quadrant_tower_stamps_20260511m"],
    "v25m_castle_macro_turret_stack": ["castle_macro_turret_stack_20260511m"],
    "v25m_castle_battlement_crown": ["castle_battlement_crown_20260511m"],
    "v25m_castle_turret_then_crown": ["castle_macro_turret_stack_20260511m", "castle_battlement_crown_20260511m"],
    "v25n_whole_root_stack": ["whole_root_nested_stack_20260511n"],
    "v25n_whole_root_twin": ["whole_root_twin_stamps_20260511n"],
    "v25n_whole_root_corner": ["whole_root_single_corner_stamp_20260511n"],
    "v25n_whole_root_stack_then_twin": ["whole_root_nested_stack_20260511n", "whole_root_twin_stamps_20260511n"],
    "v25o_rooftop_child": ["whole_root_rooftop_child_20260511o"],
    "v25o_rooftop_twins": ["whole_root_rooftop_twins_20260511o"],
    "v25o_rooftop_corner_cluster": ["whole_root_rooftop_corner_cluster_20260511o"],
    "v25o_rooftop_child_then_twins": ["whole_root_rooftop_child_20260511o", "whole_root_rooftop_twins_20260511o"],
    "v25o_mecha_socket_cluster": ["mecha_socket_cluster_20260511o"],
    "v25p_rooftop_child_tight": ["whole_root_rooftop_child_tight_20260511p"],
    "v25p_rooftop_child_readable": ["whole_root_rooftop_child_readable_20260511p"],
    "v25q_city_rooftop_stack_aligned": ["whole_root_city_rooftop_stack_aligned_20260511q"],
    "v25q_castle_rooftop_stack_aligned": ["whole_root_castle_rooftop_stack_aligned_20260511q"],
    "v25r_city_rooftop_stack_protruding": ["whole_root_city_rooftop_stack_protruding_20260511r"],
    "v25s_city_topbody_protruding": ["city_topbody_protruding_20260511s"],
    "v25s_castle_cap_pair_protruding": ["castle_cap_pair_protruding_20260511s"],
    "v25s_mecha_socket_pods_emphatic": ["mecha_socket_pods_emphatic_20260511s"],
    "v25u_solid_rooftop_child_large": ["solid_rooftop_child_large_20260511u"],
    "v25u_solid_rooftop_child_clean": ["solid_rooftop_child_clean_20260511u"],
    "v25p_spider_runner_visible_chain": ["spider_runner_visible_chain_20260511p"],
    "v25p_spider_rosette_crown_fan": ["spider_rosette_crown_fan_20260511p"],
    "v25p_potted_petiole_leaf_fan": ["potted_petiole_leaf_fan_20260511p"],
    "v25p_fern_midrib_pinnae_handles": ["fern_midrib_pinnae_handles_20260511p"],
    "v26a_fiddlehead_nested_curl": ["fiddlehead_nested_curl_20260512a"],
    "v26a_fiddlehead_visible_curl": ["fiddlehead_visible_curl_20260512a"],
    "v26a_fern_showcase_pinnae": ["fern_showcase_pinnae_20260512a"],
    "v26a_fern_showcase_dense_pinnae": ["fern_showcase_dense_pinnae_20260512a"],
    "v26b_fiddlehead_macro_curl": ["fiddlehead_macro_curl_20260512b"],
    "v26b_fiddlehead_scale_buds": ["fiddlehead_scale_buds_20260512b"],
    "v26b_fiddlehead_macro_then_buds": ["fiddlehead_macro_curl_20260512b", "fiddlehead_scale_buds_20260512b"],
    "v26b_fern_broad_pinnae": ["fern_broad_pinnae_20260512b"],
    "v26b_fern_branchlet_pinnae": ["fern_branchlet_pinnae_20260512b"],
    "v26b_fern_broad_then_branchlet": ["fern_broad_pinnae_20260512b", "fern_branchlet_pinnae_20260512b"],
    "v26c_fiddlehead_supported_scales": ["fiddlehead_supported_scales_20260512c"],
    "v26c_fiddlehead_compact_echo": ["fiddlehead_compact_echo_20260512c"],
    "v26c_fiddlehead_scales_then_echo": ["fiddlehead_supported_scales_20260512c", "fiddlehead_compact_echo_20260512c"],
    "v26c_fern_visible_sidecars": ["fern_visible_sidecars_20260512c"],
    "v26c_fern_fractal_sidecars": ["fern_fractal_sidecars_20260512c"],
    "v26c_fern_sidecars_then_fractal": ["fern_visible_sidecars_20260512c", "fern_fractal_sidecars_20260512c"],
    "v26d_fiddlehead_inner_buds": ["fiddlehead_inner_buds_20260512d"],
    "v26d_fiddlehead_solid_echo": ["fiddlehead_solid_echo_20260512d"],
    "v26d_fiddlehead_echo_then_buds": ["fiddlehead_solid_echo_20260512d", "fiddlehead_inner_buds_20260512d"],
    "v26d_fern_visible_refinement": ["fern_visible_refinement_20260512d"],
    "v26d_fern_bounded_sidelets": ["fern_bounded_sidelets_20260512d"],
    "v26d_fern_refinement_then_sidelets": ["fern_refinement_then_sidelets_20260512d"],
    "v26e_fiddlehead_surface_microbuds": ["fiddlehead_surface_microbuds_20260512e"],
    "v26e_fiddlehead_tiny_coil_echo": ["fiddlehead_tiny_coil_echo_20260512e"],
    "v26e_fiddlehead_surface_then_echo": ["fiddlehead_surface_then_echo_20260512e"],
    "v26e_fern_outer_pinnae_refinement": ["fern_outer_pinnae_refinement_20260512e"],
    "v26e_fern_hierarchical_visible": ["fern_hierarchical_visible_20260512e"],
    "v26e_fern_hierarchical_then_tiplets": ["fern_hierarchical_then_tiplets_20260512e"],
    "v26f_fiddlehead_macro_surface_buds": ["fiddlehead_macro_surface_buds_20260512f"],
    "v26f_fiddlehead_macro_buds_then_micro": ["fiddlehead_macro_buds_then_micro_20260512f"],
    "v26f_fiddlehead_macro_buds_light_echo": ["fiddlehead_macro_buds_light_echo_20260512f"],
    "v26f_fern_macro_pinnae": ["fern_macro_pinnae_20260512f"],
    "v26f_fern_macro_then_branchlets": ["fern_macro_then_branchlets_20260512f"],
    "v26f_fern_macro_dense": ["fern_macro_dense_20260512f"],
    "v26h_fiddlehead_attached_surface_buds": ["fiddlehead_attached_surface_buds_20260512h"],
    "v26h_fiddlehead_attached_buds_then_micro": ["fiddlehead_attached_buds_then_micro_20260512h"],
    "v26h_fern_attached_pinnae": ["fern_attached_pinnae_20260512h"],
    "v26h_fern_attached_pinnae_then_tiplets": ["fern_attached_pinnae_then_tiplets_20260512h"],
    "v26i_fiddlehead_log_attached_patch": ["fiddlehead_log_attached_patch_20260512i"],
    "v26i_fiddlehead_log_attached_patch_double": ["fiddlehead_log_attached_patch_double_20260512i"],
    "v26i_fern_handle_pinnae": ["fern_handle_pinnae_20260512i"],
    "v26i_fern_handle_pinnae_light_tiplets": ["fern_handle_pinnae_light_tiplets_20260512i"],
    "v26j_passthrough": [],
    "v25p_pine_branch_frontier_needle_whorl": ["pine_branch_frontier_needle_whorl_20260511p"],
    "v25p_root_first_split_sidecar": ["root_first_split_sidecar_handles_20260511p"],
    "v25p_root_first_split_then_rootlets": ["root_first_split_then_rootlets_20260511p"],
    "v25q_root_module_sidecar": ["root_module_sidecar_20260511q"],
    "v25q_root_module_chain": ["root_module_chain_20260511q"],
    "v25q_root_module_dense_rootlets": ["root_module_dense_rootlets_20260511q"],
    "v25r_root_coarse_pair": ["root_module_coarse_pair_20260511r"],
    "v25r_root_coarse_visible": ["root_module_coarse_visible_20260511r"],
    "v25r_root_coarse_then_hairline": ["root_module_coarse_then_hairline_20260511r"],
    "v25s_root_visible_child_far": ["root_module_visible_child_far_20260511s"],
    "v25s_root_visible_child_pair": ["root_module_visible_child_pair_20260511s"],
    "v25s_root_visible_child_late_taper": ["root_module_visible_child_late_taper_20260511s"],
    "v25t_root_supported_child_single": ["root_module_supported_child_single_20260511t"],
    "v25t_root_supported_child_pair": ["root_module_supported_child_pair_20260511t"],
    "v25t_root_supported_child_micro": ["root_module_supported_child_micro_20260511t"],
    "compete": ["compete_grow"],
    "compete_fork": ["compete_grow", "tip_fork"],
    "compete_fork_attach": ["compete_grow", "tip_fork_attached"],
    "fork_side_attach": ["tip_fork_attached", "side_branch_attached"],
    "crown_bud_attach": ["crown_bud_attached"],
    "crown_micro_fork_attach": ["crown_bud_attached", "crown_micro_fork_attached"],
}


def apply_op(st, op, limit):
    if op == "tip_continue":
        return tip_continue(st, limit)
    if op == "tip_fork":
        return tip_fork(st, limit)
    if op == "side_branch":
        return side_branch(st, limit)
    if op == "tip_fork_attached":
        return tip_fork_attached(st, limit)
    if op == "side_branch_attached":
        return side_branch_attached(st, limit)
    if op == "crown_bud_attached":
        return crown_bud_attached(st, limit)
    if op == "crown_micro_fork_attached":
        return crown_micro_fork_attached(st, limit)
    if op == "radial_y_clone":
        return radial_y_clone(st, limit)
    if op == "shrink_echo":
        return shrink_echo(st, limit)
    if op == "mirror_x":
        return mirror_x(st, limit)
    if op == "translate_x_clone":
        return translate_clone(st, limit, axis=0)
    if op == "translate_y_clone":
        return translate_clone(st, limit, axis=1)
    if op == "rotate_z_clone":
        return rotate_z_clone(st, limit)
    if op == "scale_up_clone":
        return scale_clone(st, limit, scale=1.18)
    if op == "radial4_y_clone":
        return radial4_y_clone(st, limit)
    if op == "radial4_y_attached_clone":
        return radial4_y_attached_clone(st, limit)
    if op == "portal_insert":
        return portal_insert(st, limit)
    if op == "portal_attached_insert":
        return portal_attached_insert(st, limit)
    if op == "radial_frontier_attached_clone":
        return radial_frontier_attached_clone(st, limit)
    if op == "ornament_crown_buds":
        return ornament_crown_buds(st, limit)
    if op == "ornament_rim_micro_buds":
        return ornament_rim_micro_buds(st, limit)
    if op == "arch_keystone_buds":
        return arch_keystone_buds(st, limit)
    if op == "socket_translate_attached_clone":
        return socket_translate_attached_clone(st, limit)
    if op == "socket_translate_tight_attached_clone":
        return socket_translate_tight_attached_clone(st, limit)
    if op == "scale_down_attached_clone":
        return scale_down_attached_clone(st, limit)
    if op == "rooftop_scale_buds":
        return rooftop_scale_buds(st, limit)
    if op == "leaf_basal_fan_attached_clone":
        return leaf_basal_fan_attached_clone(st, limit)
    if op == "leaf_basal_micro_buds":
        return leaf_basal_micro_buds(st, limit)
    if op == "leaf_basal_handle_blades":
        return leaf_basal_handle_blades(st, limit)
    if op == "fern_frond_tiplets":
        return fern_frond_tiplets(st, limit)
    if op == "fern_midrib_pinnae":
        return fern_midrib_pinnae(st, limit)
    if op == "fern_spiral_echo":
        return fern_spiral_echo(st, limit)
    if op == "crown_bud_micro_20260511e":
        return crown_bud_micro_20260511e(st, limit)
    if op == "crown_scatter_micro_fork_20260511e":
        return crown_scatter_micro_fork_20260511e(st, limit)
    if op == "rim_leaflet_micro_20260511e":
        return rim_leaflet_micro_20260511e(st, limit)
    if op == "tiplet_short_20260511e":
        return tiplet_short_20260511e(st, limit)
    if op == "basal_micro_short_20260511e":
        return basal_micro_short_20260511e(st, limit)
    if op == "root_crown_micro_conservative_20260511g":
        return root_crown_micro_conservative_20260511g(st, limit)
    if op == "root_plantlet_sprout_20260511g":
        return root_plantlet_sprout_20260511g(st, limit)
    if op == "spider_basal_crown_micro_20260511h":
        return spider_basal_crown_micro_20260511h(st, limit)
    if op == "spider_leaf_tiplet_micro_20260511h":
        return spider_leaf_tiplet_micro_20260511h(st, limit)
    if op == "spider_runner_distal_micro_20260511h":
        return spider_runner_distal_micro_20260511h(st, limit)
    if op == "spider_basal_then_tiplet_20260511h":
        return spider_basal_then_tiplet_20260511h(st, limit)
    if op == "root_shrink_fork_20260511h":
        return root_shrink_fork_20260511h(st, limit)
    if op == "root_shrink_fork_tiplet_20260511h":
        return root_shrink_fork_tiplet_20260511h(st, limit)
    if op == "spider_leaf_handle_visible_20260511j":
        return spider_leaf_handle_visible_20260511j(st, limit)
    if op == "spider_leaf_handle_compact_20260511j":
        return spider_leaf_handle_compact_20260511j(st, limit)
    if op == "spider_leaf_schedule_20260511j":
        return spider_leaf_schedule_20260511j(st, limit)
    if op == "root_shrink_fork_clean_20260511j":
        return root_shrink_fork_clean_20260511j(st, limit)
    if op == "root_wedge_fork_clean_20260511j":
        return root_wedge_fork_clean_20260511j(st, limit)
    if op == "root_wedge_then_clean_20260511j":
        return root_wedge_then_clean_20260511j(st, limit)
    if op == "crown_rim_gem_array_20260511j":
        return crown_rim_gem_array_20260511j(st, limit)
    if op == "mecha_socket_fin_array_20260511j":
        return mecha_socket_fin_array_20260511j(st, limit)
    if op == "city_rooftop_tower_array_20260511j":
        return city_rooftop_tower_array_20260511j(st, limit)
    if op == "castle_turret_battlement_20260511j":
        return castle_turret_battlement_20260511j(st, limit)
    if op == "spider_terminal_leaflet_visible_20260511k":
        return spider_terminal_leaflet_visible_20260511k(st, limit)
    if op == "spider_basal_leaflet_arc_20260511k":
        return spider_basal_leaflet_arc_20260511k(st, limit)
    if op == "spider_balanced_leaflet_20260511k":
        return spider_balanced_leaflet_20260511k(st, limit)
    if op == "fiddlehead_curl_echo_20260511k":
        return fiddlehead_curl_echo_20260511k(st, limit)
    if op == "fiddlehead_curl_pinnae_20260511k":
        return fiddlehead_curl_pinnae_20260511k(st, limit)
    if op == "pine_terminal_needles_20260511k":
        return pine_terminal_needles_20260511k(st, limit)
    if op == "root_single_wedge_branch_20260511k":
        return root_single_wedge_branch_20260511k(st, limit)
    if op == "root_single_then_tiplets_20260511k":
        return root_single_then_tiplets_20260511k(st, limit)
    if op == "crown_rim_gem_clean_20260511k":
        return crown_rim_gem_clean_20260511k(st, limit)
    if op == "mecha_socket_fin_clean_20260511k":
        return mecha_socket_fin_clean_20260511k(st, limit)
    if op == "city_rooftop_tower_clean_20260511k":
        return city_rooftop_tower_clean_20260511k(st, limit)
    if op == "castle_turret_clean_20260511k":
        return castle_turret_clean_20260511k(st, limit)
    if op == "root_relaxed_wedge_branch_20260511l":
        return root_relaxed_wedge_branch_20260511l(st, limit)
    if op == "root_primary_branch_cut_20260511l":
        return root_primary_branch_cut_20260511l(st, limit)
    if op == "root_two_phase_hierarchy_20260511l":
        return root_two_phase_hierarchy_20260511l(st, limit)
    if op == "root_two_phase_late_rootlets_20260511l":
        return root_two_phase_late_rootlets_20260511l(st, limit)
    if op == "spider_leaf_cluster_compact_20260511l":
        return spider_leaf_cluster_compact_20260511l(st, limit)
    if op == "spider_leaf_treecrown_schedule_20260511l":
        return spider_leaf_treecrown_schedule_20260511l(st, limit)
    if op == "spider_leaf_tip_clean_20260511l":
        return spider_leaf_tip_clean_20260511l(st, limit)
    if op == "fiddlehead_guarded_curl_20260511l":
        return fiddlehead_guarded_curl_20260511l(st, limit)
    if op == "pine_leaf_cluster_clean_20260511l":
        return pine_leaf_cluster_clean_20260511l(st, limit)
    if op == "pine_branch_tip_cluster_20260511l":
        return pine_branch_tip_cluster_20260511l(st, limit)
    if op == "plant_basal_midrib_leaflet_20260511n":
        return plant_basal_midrib_leaflet_20260511n(st, limit)
    if op == "plant_basal_crown_leaflets_20260511n":
        return plant_basal_crown_leaflets_20260511n(st, limit)
    if op == "spider_runner_leaflet_gated_20260511n":
        return spider_runner_leaflet_gated_20260511n(st, limit)
    if op == "fern_pinnae_sparse_attach_20260511n":
        return fern_pinnae_sparse_attach_20260511n(st, limit)
    if op == "fiddlehead_thick_curl_20260511n":
        return fiddlehead_thick_curl_20260511n(st, limit)
    if op == "root_short_terminal_rootlets_20260511n":
        return root_short_terminal_rootlets_20260511n(st, limit)
    if op == "root_first_split_taper_20260511n":
        return root_first_split_taper_20260511n(st, limit)
    if op == "pine_leaf_gated_20260511n":
        return pine_leaf_gated_20260511n(st, limit)
    if op == "city_roof_podium_20260511l":
        return city_roof_podium_20260511l(st, limit)
    if op == "city_roof_corner_towers_20260511l":
        return city_roof_corner_towers_20260511l(st, limit)
    if op == "castle_turret_caps_20260511l":
        return castle_turret_caps_20260511l(st, limit)
    if op == "castle_battlement_strip_20260511l":
        return castle_battlement_strip_20260511l(st, limit)
    if op == "mecha_socket_pods_20260511l":
        return mecha_socket_pods_20260511l(st, limit)
    if op == "city_macro_tower_stack_20260511m":
        return city_macro_tower_stack_20260511m(st, limit)
    if op == "city_quadrant_tower_stamps_20260511m":
        return city_quadrant_tower_stamps_20260511m(st, limit)
    if op == "castle_macro_turret_stack_20260511m":
        return castle_macro_turret_stack_20260511m(st, limit)
    if op == "castle_battlement_crown_20260511m":
        return castle_battlement_crown_20260511m(st, limit)
    if op == "whole_root_nested_stack_20260511n":
        return whole_root_nested_stack_20260511n(st, limit)
    if op == "whole_root_twin_stamps_20260511n":
        return whole_root_twin_stamps_20260511n(st, limit)
    if op == "whole_root_single_corner_stamp_20260511n":
        return whole_root_single_corner_stamp_20260511n(st, limit)
    if op == "whole_root_rooftop_child_20260511o":
        return whole_root_rooftop_child_20260511o(st, limit)
    if op == "whole_root_rooftop_twins_20260511o":
        return whole_root_rooftop_twins_20260511o(st, limit)
    if op == "whole_root_rooftop_corner_cluster_20260511o":
        return whole_root_rooftop_corner_cluster_20260511o(st, limit)
    if op == "mecha_socket_cluster_20260511o":
        return mecha_socket_cluster_20260511o(st, limit)
    if op == "whole_root_rooftop_child_tight_20260511p":
        return whole_root_rooftop_child_tight_20260511p(st, limit)
    if op == "whole_root_rooftop_child_readable_20260511p":
        return whole_root_rooftop_child_readable_20260511p(st, limit)
    if op == "whole_root_city_rooftop_stack_aligned_20260511q":
        return whole_root_city_rooftop_stack_aligned_20260511q(st, limit)
    if op == "whole_root_castle_rooftop_stack_aligned_20260511q":
        return whole_root_castle_rooftop_stack_aligned_20260511q(st, limit)
    if op == "whole_root_city_rooftop_stack_protruding_20260511r":
        return whole_root_city_rooftop_stack_protruding_20260511r(st, limit)
    if op == "city_topbody_protruding_20260511s":
        return city_topbody_protruding_20260511s(st, limit)
    if op == "castle_cap_pair_protruding_20260511s":
        return castle_cap_pair_protruding_20260511s(st, limit)
    if op == "mecha_socket_pods_emphatic_20260511s":
        return mecha_socket_pods_emphatic_20260511s(st, limit)
    if op == "solid_rooftop_child_large_20260511u":
        return solid_rooftop_child_large_20260511u(st, limit)
    if op == "solid_rooftop_child_clean_20260511u":
        return solid_rooftop_child_clean_20260511u(st, limit)
    if op == "spider_runner_visible_chain_20260511p":
        return spider_runner_visible_chain_20260511p(st, limit)
    if op == "spider_rosette_crown_fan_20260511p":
        return spider_rosette_crown_fan_20260511p(st, limit)
    if op == "potted_petiole_leaf_fan_20260511p":
        return potted_petiole_leaf_fan_20260511p(st, limit)
    if op == "fern_midrib_pinnae_handles_20260511p":
        return fern_midrib_pinnae_handles_20260511p(st, limit)
    if op == "fiddlehead_nested_curl_20260512a":
        return fiddlehead_nested_curl_20260512a(st, limit)
    if op == "fiddlehead_visible_curl_20260512a":
        return fiddlehead_visible_curl_20260512a(st, limit)
    if op == "fern_showcase_pinnae_20260512a":
        return fern_showcase_pinnae_20260512a(st, limit)
    if op == "fern_showcase_dense_pinnae_20260512a":
        return fern_showcase_dense_pinnae_20260512a(st, limit)
    if op == "fiddlehead_macro_curl_20260512b":
        return fiddlehead_macro_curl_20260512b(st, limit)
    if op == "fiddlehead_scale_buds_20260512b":
        return fiddlehead_scale_buds_20260512b(st, limit)
    if op == "fern_broad_pinnae_20260512b":
        return fern_broad_pinnae_20260512b(st, limit)
    if op == "fern_branchlet_pinnae_20260512b":
        return fern_branchlet_pinnae_20260512b(st, limit)
    if op == "fiddlehead_supported_scales_20260512c":
        return fiddlehead_supported_scales_20260512c(st, limit)
    if op == "fiddlehead_compact_echo_20260512c":
        return fiddlehead_compact_echo_20260512c(st, limit)
    if op == "fern_visible_sidecars_20260512c":
        return fern_visible_sidecars_20260512c(st, limit)
    if op == "fern_fractal_sidecars_20260512c":
        return fern_fractal_sidecars_20260512c(st, limit)
    if op == "fiddlehead_inner_buds_20260512d":
        return fiddlehead_inner_buds_20260512d(st, limit)
    if op == "fiddlehead_solid_echo_20260512d":
        return fiddlehead_solid_echo_20260512d(st, limit)
    if op == "fern_visible_refinement_20260512d":
        return fern_visible_refinement_20260512d(st, limit)
    if op == "fern_bounded_sidelets_20260512d":
        return fern_bounded_sidelets_20260512d(st, limit)
    if op == "fern_refinement_then_sidelets_20260512d":
        return fern_refinement_then_sidelets_20260512d(st, limit)
    if op == "fiddlehead_surface_microbuds_20260512e":
        return fiddlehead_surface_microbuds_20260512e(st, limit)
    if op == "fiddlehead_tiny_coil_echo_20260512e":
        return fiddlehead_tiny_coil_echo_20260512e(st, limit)
    if op == "fiddlehead_surface_then_echo_20260512e":
        return fiddlehead_surface_then_echo_20260512e(st, limit)
    if op == "fern_outer_pinnae_refinement_20260512e":
        return fern_outer_pinnae_refinement_20260512e(st, limit)
    if op == "fern_hierarchical_visible_20260512e":
        return fern_hierarchical_visible_20260512e(st, limit)
    if op == "fern_hierarchical_then_tiplets_20260512e":
        return fern_hierarchical_then_tiplets_20260512e(st, limit)
    if op == "fiddlehead_macro_surface_buds_20260512f":
        return fiddlehead_macro_surface_buds_20260512f(st, limit)
    if op == "fiddlehead_macro_buds_then_micro_20260512f":
        return fiddlehead_macro_buds_then_micro_20260512f(st, limit)
    if op == "fiddlehead_macro_buds_light_echo_20260512f":
        return fiddlehead_macro_buds_light_echo_20260512f(st, limit)
    if op == "fern_macro_pinnae_20260512f":
        return fern_macro_pinnae_20260512f(st, limit)
    if op == "fern_macro_then_branchlets_20260512f":
        return fern_macro_then_branchlets_20260512f(st, limit)
    if op == "fern_macro_dense_20260512f":
        return fern_macro_dense_20260512f(st, limit)
    if op == "fiddlehead_attached_surface_buds_20260512h":
        return fiddlehead_attached_surface_buds_20260512h(st, limit)
    if op == "fiddlehead_attached_buds_then_micro_20260512h":
        return fiddlehead_attached_buds_then_micro_20260512h(st, limit)
    if op == "fern_attached_pinnae_20260512h":
        return fern_attached_pinnae_20260512h(st, limit)
    if op == "fern_attached_pinnae_then_tiplets_20260512h":
        return fern_attached_pinnae_then_tiplets_20260512h(st, limit)
    if op == "fiddlehead_log_attached_patch_20260512i":
        return fiddlehead_log_attached_patch_20260512i(st, limit)
    if op == "fiddlehead_log_attached_patch_double_20260512i":
        return fiddlehead_log_attached_patch_double_20260512i(st, limit)
    if op == "fern_handle_pinnae_20260512i":
        return fern_handle_pinnae_20260512i(st, limit)
    if op == "fern_handle_pinnae_light_tiplets_20260512i":
        return fern_handle_pinnae_light_tiplets_20260512i(st, limit)
    if op == "pine_branch_frontier_needle_whorl_20260511p":
        return pine_branch_frontier_needle_whorl_20260511p(st, limit)
    if op == "root_first_split_sidecar_handles_20260511p":
        return root_first_split_sidecar_handles_20260511p(st, limit)
    if op == "root_first_split_then_rootlets_20260511p":
        return root_first_split_then_rootlets_20260511p(st, limit)
    if op == "root_module_sidecar_20260511q":
        return root_module_sidecar_20260511q(st, limit)
    if op == "root_module_chain_20260511q":
        return root_module_chain_20260511q(st, limit)
    if op == "root_module_dense_rootlets_20260511q":
        return root_module_dense_rootlets_20260511q(st, limit)
    if op == "root_module_coarse_pair_20260511r":
        return root_module_coarse_pair_20260511r(st, limit)
    if op == "root_module_coarse_visible_20260511r":
        return root_module_coarse_visible_20260511r(st, limit)
    if op == "root_module_coarse_then_hairline_20260511r":
        return root_module_coarse_then_hairline_20260511r(st, limit)
    if op == "root_module_visible_child_far_20260511s":
        return root_module_visible_child_far_20260511s(st, limit)
    if op == "root_module_visible_child_pair_20260511s":
        return root_module_visible_child_pair_20260511s(st, limit)
    if op == "root_module_visible_child_late_taper_20260511s":
        return root_module_visible_child_late_taper_20260511s(st, limit)
    if op == "root_module_supported_child_single_20260511t":
        return root_module_supported_child_single_20260511t(st, limit)
    if op == "root_module_supported_child_pair_20260511t":
        return root_module_supported_child_pair_20260511t(st, limit)
    if op == "root_module_supported_child_micro_20260511t":
        return root_module_supported_child_micro_20260511t(st, limit)
    if op == "translate_x_attached_clone":
        return translate_attached_clone(st, limit, axis=0)
    if op == "compete_grow":
        return compete_grow(st, limit)
    raise ValueError(f"unknown op {op}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--case-name", default=None)
    parser.add_argument("--grammars", nargs="+", default=["continue", "fork", "fork_side", "radial", "echo"])
    parser.add_argument("--depths", type=int, default=3)
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--grid-resolution", type=int, default=512)
    parser.add_argument("--fit-scale", type=float, default=0.68)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--seed", type=int, default=None, help="Seed for stochastic grammar diagnostics.")
    parser.add_argument(
        "--growth-axis",
        choices=["x", "y", "z"],
        default="y",
        help="Latent coordinate axis used for tip/crown selection and upward grammar shifts.",
    )
    parser.add_argument(
        "--growth-sign",
        type=int,
        choices=[-1, 1],
        default=1,
        help="Direction on the growth axis treated as crown/tip side.",
    )
    parser.add_argument(
        "--compete-jitter",
        type=float,
        default=0.0,
        help="Relative attractor jitter for compete_grow; default 0 preserves deterministic behavior.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Decode and time each state but do not write OBJ/PNG assets; useful near storage caps.",
    )
    parser.add_argument(
        "--restore-output-frame",
        action="store_true",
        help="Diagnostic mode: write decoded vertices after inverting the input mesh-to-SLat axis conversion. Default keeps the decoder frame used by prior runs.",
    )
    parser.add_argument(
        "--preencode-transform",
        choices=["identity", "rot_x_neg90", "rot_x_pos90", "rot_y_neg90", "rot_y_pos90"],
        default="identity",
        help="Optional root-frame transform applied before centering/scaling and the fixed mesh-to-SLat conversion.",
    )
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

    case = args.case_name or args.mesh.stem
    summary = {
        "kind": "trellis2_recursive_slat_grammar_workflow",
        "mesh": str(args.mesh),
        "case": case,
        "resolution": args.resolution,
        "grid_resolution": args.grid_resolution,
        "fit_scale": args.fit_scale,
        "max_tokens": args.max_tokens,
        "growth_axis": args.growth_axis,
        "growth_sign": args.growth_sign,
        "preencode_transform": args.preencode_transform,
        "restore_output_frame": bool(args.restore_output_frame),
        "summary_only": bool(args.summary_only),
        "grammars": {},
    }

    try:
        import torch
        import trimesh
        import o_voxel
        from trellis2 import models
        from trellis2.modules.sparse import SparseTensor

        global COMPETE_GENERATOR, COMPETE_JITTER, GROWTH_AXIS, GROWTH_SIGN
        GROWTH_AXIS = {"x": 0, "y": 1, "z": 2}[args.growth_axis]
        GROWTH_SIGN = int(args.growth_sign)
        COMPETE_JITTER = float(args.compete_jitter)
        if args.seed is not None:
            np.random.seed(args.seed)
            torch.manual_seed(args.seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(args.seed)
            COMPETE_GENERATOR = torch.Generator(device="cuda" if torch.cuda.is_available() else "cpu")
            COMPETE_GENERATOR.manual_seed(args.seed)
        summary["seed"] = args.seed
        summary["compete_jitter"] = COMPETE_JITTER

        hf = Path(os.environ["HF_HOME"])
        snapshot = next((hf / "hub/models--microsoft--TRELLIS.2-4B/snapshots").iterdir())
        pipeline_cfg = json.loads((snapshot / "pipeline.json").read_text())["args"]["models"]
        texturing_cfg = json.loads((snapshot / "texturing_pipeline.json").read_text())["args"]["models"]
        load_start = time.time()
        encoder = models.from_pretrained(rewrite_model_path(texturing_cfg["shape_slat_encoder"], snapshot)).eval().cuda()
        decoder = models.from_pretrained(rewrite_model_path(pipeline_cfg["shape_slat_decoder"], snapshot)).eval().cuda()
        decoder.set_resolution(args.resolution)
        decoder.low_vram = True
        summary["load_seconds"] = time.time() - load_start

        mesh = trimesh.load(str(args.mesh), force="mesh", process=False)
        vertices_np = np.asarray(mesh.vertices).astype(np.float32)
        faces_np = np.asarray(mesh.faces).astype(np.int64)
        vertices_np = apply_preencode_transform(vertices_np, args.preencode_transform).astype(np.float32)
        vmin = vertices_np.min(axis=0)
        vmax = vertices_np.max(axis=0)
        center = (vmin + vmax) / 2
        scale = args.fit_scale / max(float((vmax - vmin).max()), 1e-6)
        vertices_np = (vertices_np - center) * scale
        tmp = vertices_np[:, 1].copy()
        vertices_np[:, 1] = -vertices_np[:, 2]
        vertices_np[:, 2] = tmp

        fdg_start = time.time()
        voxel_indices, dual_vertices, intersected = o_voxel.convert.mesh_to_flexible_dual_grid(
            torch.from_numpy(vertices_np).float().cpu(),
            torch.from_numpy(faces_np).long().cpu(),
            grid_size=args.grid_resolution,
            aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
            face_weight=1.0,
            boundary_weight=0.2,
            regularization_weight=1e-2,
            timing=True,
        )
        summary["fdg_seconds"] = time.time() - fdg_start
        summary["fdg_voxels"] = int(voxel_indices.shape[0])
        sparse_vertices = SparseTensor(
            feats=dual_vertices * args.grid_resolution - voxel_indices,
            coords=torch.cat([torch.zeros_like(voxel_indices[:, 0:1]), voxel_indices], dim=-1),
        ).cuda()
        sparse_intersected = sparse_vertices.replace(intersected).cuda()
        with torch.no_grad():
            encode_start = time.time()
            base_slat = encoder(sparse_vertices, sparse_intersected)
            summary["encode_seconds"] = time.time() - encode_start
            summary["base_tokens"] = int(base_slat.coords.shape[0])
            summary["base_coord_min"] = base_slat.coords[:, 1:].min(0).values.detach().cpu().tolist()
            summary["base_coord_max"] = base_slat.coords[:, 1:].max(0).values.detach().cpu().tolist()
            limit = args.resolution // 16 - 1
            summary["latent_coord_limit"] = int(limit)

            for grammar_name in args.grammars:
                ops = GRAMMARS[grammar_name]
                grammar_dir = args.out / grammar_name
                if not args.summary_only:
                    grammar_dir.mkdir(parents=True, exist_ok=True)
                st = base_slat
                grammar_summary = {"ops": ops, "depths": []}
                for depth in range(args.depths + 1):
                    depth_dir = grammar_dir / f"depth_{depth:02d}"
                    if not args.summary_only:
                        depth_dir.mkdir(parents=True, exist_ok=True)
                    decode_start = time.time()
                    decoded = decoder(st)[0]
                    vertices_slat = decoded.vertices.detach().cpu().numpy()
                    vertices = maybe_restore_output_frame(vertices_slat, args.restore_output_frame)
                    faces = decoded.faces.detach().cpu().numpy()
                    decode_seconds = time.time() - decode_start
                    if not args.summary_only:
                        write_obj(depth_dir / "mesh.obj", vertices, faces)
                        render_preview(depth_dir / "preview.png", vertices, f"{case} {grammar_name} d{depth}")
                    grammar_summary["depths"].append({
                        "depth": depth,
                        "tokens": int(st.coords.shape[0]),
                        "vertices": int(len(vertices)),
                        "faces": int(len(faces)),
                        "bbox_min": vertices.min(0).tolist() if len(vertices) else [0, 0, 0],
                        "bbox_max": vertices.max(0).tolist() if len(vertices) else [0, 0, 0],
                        "decode_seconds": decode_seconds,
                    })
                    if depth == args.depths:
                        break
                    op_start = time.time()
                    for op in ops:
                        st = apply_op(st, op, limit)
                    grammar_summary["depths"][-1]["op_seconds_to_next"] = time.time() - op_start
                    grammar_summary["depths"][-1]["next_tokens"] = int(st.coords.shape[0])
                    if st.coords.shape[0] > args.max_tokens:
                        grammar_summary["stopped_at_depth"] = depth
                        grammar_summary["stop_reason"] = f"tokens {int(st.coords.shape[0])} > max_tokens {args.max_tokens}"
                        break
                summary["grammars"][grammar_name] = grammar_summary
        summary["cuda_memory_allocated"] = int(torch.cuda.memory_allocated())
        summary["cuda_memory_reserved"] = int(torch.cuda.memory_reserved())
    except Exception as exc:
        summary["status"] = "failed"
        summary["error"] = repr(exc)
        summary["traceback_tail"] = traceback.format_exc().splitlines()[-100:]
    finally:
        (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
