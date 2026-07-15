#!/usr/bin/env python3
"""Generate repair candidates for collapsed recursive-3D visual cases.

This batch is intentionally grammar-first rather than a post-hoc cleanup of the
failed 2026-05-08 projected-loop assets.  The old radial/portal cases collapsed
because whole latent/mesh copies were rotated or inserted without stable
attachment handles.  These candidates use explicit handles, bridge geometry and
category-specific scaffolds before any optional neural texturing pass.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "results/publication_repair_candidates_20260510"


def unit(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    n = float(np.linalg.norm(v))
    if n < 1e-9:
        return np.array([0.0, 0.0, 1.0])
    return v / n


def basis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = unit(axis)
    seed = np.array([0.0, 0.0, 1.0]) if abs(w[2]) < 0.86 else np.array([1.0, 0.0, 0.0])
    u = unit(np.cross(w, seed))
    v = unit(np.cross(w, u))
    return u, v, w


@dataclass(frozen=True)
class Mat:
    name: str
    color: tuple[int, int, int, int]


class MeshBuilder:
    def __init__(self, materials: list[Mat]):
        self.vertices: list[np.ndarray] = []
        self.faces: list[list[int]] = []
        self.mats: list[int] = []
        self.materials = materials

    def add_vertex(self, p: np.ndarray) -> int:
        self.vertices.append(np.asarray(p, dtype=float))
        return len(self.vertices) - 1

    def add_face(self, a: int, b: int, c: int, mat: int) -> None:
        self.faces.append([int(a), int(b), int(c)])
        self.mats.append(int(mat))

    def add_frustum(
        self,
        p0: np.ndarray,
        p1: np.ndarray,
        r0: float,
        r1: float,
        mat: int,
        sides: int = 12,
        phase: float = 0.0,
        cap: bool = True,
    ) -> None:
        p0 = np.asarray(p0, dtype=float)
        p1 = np.asarray(p1, dtype=float)
        u, v, _w = basis(p1 - p0)
        ring0: list[int] = []
        ring1: list[int] = []
        for i in range(sides):
            theta = 2.0 * math.pi * i / sides + phase
            d = math.cos(theta) * u + math.sin(theta) * v
            ring0.append(self.add_vertex(p0 + d * r0))
            ring1.append(self.add_vertex(p1 + d * r1))
        c0 = self.add_vertex(p0)
        c1 = self.add_vertex(p1)
        for i in range(sides):
            j = (i + 1) % sides
            self.add_face(ring0[i], ring0[j], ring1[j], mat)
            self.add_face(ring0[i], ring1[j], ring1[i], mat)
            if cap:
                self.add_face(c0, ring0[j], ring0[i], mat)
                self.add_face(c1, ring1[i], ring1[j], mat)

    def add_box(self, center: np.ndarray, extents: np.ndarray, mat: int, rot: np.ndarray | None = None) -> None:
        center = np.asarray(center, dtype=float)
        extents = np.asarray(extents, dtype=float)
        rot = np.eye(3) if rot is None else np.asarray(rot, dtype=float)
        corners = []
        for sx in (-0.5, 0.5):
            for sy in (-0.5, 0.5):
                for sz in (-0.5, 0.5):
                    local = np.array([sx * extents[0], sy * extents[1], sz * extents[2]])
                    corners.append(self.add_vertex(center + rot @ local))
        # index helper: x,y,z with bits 0/1 in the order above.
        def idx(x: int, y: int, z: int) -> int:
            return corners[x * 4 + y * 2 + z]

        quads = [
            (idx(0, 0, 0), idx(0, 1, 0), idx(0, 1, 1), idx(0, 0, 1)),
            (idx(1, 0, 0), idx(1, 0, 1), idx(1, 1, 1), idx(1, 1, 0)),
            (idx(0, 0, 0), idx(1, 0, 0), idx(1, 0, 1), idx(0, 0, 1)),
            (idx(0, 1, 0), idx(0, 1, 1), idx(1, 1, 1), idx(1, 1, 0)),
            (idx(0, 0, 0), idx(0, 1, 0), idx(1, 1, 0), idx(1, 0, 0)),
            (idx(0, 0, 1), idx(1, 0, 1), idx(1, 1, 1), idx(0, 1, 1)),
        ]
        for a, b, c, d in quads:
            self.add_face(a, b, c, mat)
            self.add_face(a, c, d, mat)

    def add_ellipsoid(
        self,
        center: np.ndarray,
        radii: tuple[float, float, float],
        mat: int,
        seg: int = 18,
        rings: int = 9,
        rot: np.ndarray | None = None,
    ) -> None:
        center = np.asarray(center, dtype=float)
        rot = np.eye(3) if rot is None else np.asarray(rot, dtype=float)
        rx, ry, rz = radii
        grid: list[list[int]] = []
        for a in range(rings + 1):
            phi = -math.pi / 2.0 + math.pi * a / rings
            row: list[int] = []
            for b in range(seg):
                th = 2.0 * math.pi * b / seg
                local = np.array([rx * math.cos(phi) * math.cos(th), ry * math.cos(phi) * math.sin(th), rz * math.sin(phi)])
                row.append(self.add_vertex(center + rot @ local))
            grid.append(row)
        for a in range(rings):
            for b in range(seg):
                nb = (b + 1) % seg
                self.add_face(grid[a][b], grid[a][nb], grid[a + 1][nb], mat)
                self.add_face(grid[a][b], grid[a + 1][nb], grid[a + 1][b], mat)

    def add_ring_tube(
        self,
        center: np.ndarray,
        radius: float,
        tube: float,
        mat: int,
        major: int = 96,
        minor: int = 10,
        z_scale: float = 1.0,
        phase0: float = 0.0,
    ) -> None:
        center = np.asarray(center, dtype=float)
        rings: list[list[int]] = []
        for i in range(major):
            th = 2.0 * math.pi * i / major + phase0
            radial = np.array([math.cos(th), math.sin(th), 0.0])
            tangent = np.array([-math.sin(th), math.cos(th), 0.0])
            normal = np.array([0.0, 0.0, 1.0])
            ring: list[int] = []
            for j in range(minor):
                ph = 2.0 * math.pi * j / minor
                p = center + radial * (radius + tube * math.cos(ph)) + normal * (tube * z_scale * math.sin(ph))
                # a little tangent wobble makes metal hand-worked rather than CAD flat.
                p += tangent * (0.004 * math.sin(3 * th + ph))
                ring.append(self.add_vertex(p))
            rings.append(ring)
        for i in range(major):
            ni = (i + 1) % major
            for j in range(minor):
                nj = (j + 1) % minor
                self.add_face(rings[i][j], rings[ni][j], rings[ni][nj], mat)
                self.add_face(rings[i][j], rings[ni][nj], rings[i][nj], mat)

    def add_tri_fin(self, anchor: np.ndarray, axis: np.ndarray, width: float, length: float, mat: int, lift: float = 0.0) -> None:
        anchor = np.asarray(anchor, dtype=float)
        u, v, w = basis(axis)
        tip = anchor + w * length + v * lift
        left = anchor + u * width
        right = anchor - u * width
        ia, il, ir, it = self.add_vertex(anchor), self.add_vertex(left), self.add_vertex(right), self.add_vertex(tip)
        self.add_face(ia, il, it, mat)
        self.add_face(ia, it, ir, mat)
        self.add_face(ia, it, il, mat)
        self.add_face(ia, ir, it, mat)

    def add_leaf_disc(
        self,
        center: np.ndarray,
        axis: np.ndarray,
        radius: float,
        thickness: float,
        mat: int,
        seg: int = 12,
        squash: float = 0.56,
    ) -> None:
        u, v, w = basis(axis)
        center = np.asarray(center, dtype=float)
        top = self.add_vertex(center + w * thickness)
        bottom = self.add_vertex(center - w * thickness)
        ring_top: list[int] = []
        ring_bottom: list[int] = []
        for i in range(seg):
            th = 2.0 * math.pi * i / seg
            p = center + u * (math.cos(th) * radius) + v * (math.sin(th) * radius * squash)
            ring_top.append(self.add_vertex(p + w * thickness))
            ring_bottom.append(self.add_vertex(p - w * thickness))
        for i in range(seg):
            j = (i + 1) % seg
            self.add_face(top, ring_top[i], ring_top[j], mat)
            self.add_face(bottom, ring_bottom[j], ring_bottom[i], mat)
            self.add_face(ring_top[i], ring_bottom[i], ring_bottom[j], mat)
            self.add_face(ring_top[i], ring_bottom[j], ring_top[j], mat)

    def mesh(self) -> trimesh.Trimesh:
        mesh = trimesh.Trimesh(vertices=np.asarray(self.vertices, dtype=np.float32), faces=np.asarray(self.faces, dtype=np.int64), process=False)
        return mesh

    def normalize(self, target_extent: float = 3.0, ground: bool = True) -> None:
        arr = np.asarray(self.vertices, dtype=float)
        mn = arr.min(axis=0)
        mx = arr.max(axis=0)
        arr[:, :2] -= (mn[:2] + mx[:2]) * 0.5
        if ground:
            arr[:, 2] -= mn[2]
        else:
            arr -= (mn + mx) * 0.5
        scale = target_extent / max(float((arr.max(axis=0) - arr.min(axis=0)).max()), 1e-6)
        arr *= scale
        self.vertices = [p for p in arr]

    def export(self, obj_path: Path, glb_path: Path) -> dict[str, object]:
        obj_path.parent.mkdir(parents=True, exist_ok=True)
        glb_path.parent.mkdir(parents=True, exist_ok=True)
        mesh = self.mesh()
        mesh.export(obj_path)
        scene = trimesh.Scene()
        mats_np = np.asarray(self.mats, dtype=np.int64)
        for mi, material in enumerate(self.materials):
            idx = np.where(mats_np == mi)[0]
            if len(idx) == 0:
                continue
            sub = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces[idx], process=False)
            color = np.asarray(material.color, dtype=np.uint8)
            sub.visual = trimesh.visual.ColorVisuals(sub, face_colors=np.tile(color[None, :], (len(sub.faces), 1)))
            scene.add_geometry(sub, geom_name=material.name, node_name=material.name)
        scene.export(glb_path)
        comps = mesh.split(only_watertight=False)
        total_area = float(mesh.area) if mesh.area else 0.0
        largest_area = max((float(c.area) for c in comps), default=0.0)
        return {
            "obj": str(obj_path),
            "glb": str(glb_path),
            "vertices": int(len(mesh.vertices)),
            "faces": int(len(mesh.faces)),
            "face_components": int(len(comps)),
            "largest_component_area_ratio": float(largest_area / total_area) if total_area > 0 else 0.0,
            "bbox": (mesh.bounds[1] - mesh.bounds[0]).round(4).tolist(),
        }


TREE_MATS = [
    Mat("cedar_trunk_warm_brown", (106, 63, 34, 255)),
    Mat("deep_cedar_needles", (22, 72, 42, 255)),
    Mat("snow_lit_cedar_tips", (184, 184, 164, 255)),
    Mat("pale_exposed_roots", (141, 117, 104, 255)),
]

CROWN_MATS = [
    Mat("aged_gold_filagree", (180, 125, 58, 255)),
    Mat("dark_bronze_recess", (74, 48, 32, 255)),
    Mat("sapphire_glass_inlays", (33, 54, 112, 255)),
    Mat("warm_highlight_gold", (235, 184, 86, 255)),
]

SCIFI_MATS = [
    Mat("graphite_shell", (46, 51, 54, 255)),
    Mat("brushed_steel_edges", (132, 141, 140, 255)),
    Mat("blue_energy_ports", (38, 96, 162, 255)),
    Mat("dark_panel_gaps", (16, 18, 19, 255)),
]

ARCH_MATS = [
    Mat("limestone_blocks", (168, 162, 148, 255)),
    Mat("cool_shadow_stone", (98, 101, 102, 255)),
    Mat("moss_patina", (70, 92, 66, 255)),
    Mat("pale_edge_wear", (215, 207, 188, 255)),
]


def build_tree_root(seed: int) -> MeshBuilder:
    rng = np.random.default_rng(seed)
    b = MeshBuilder(TREE_MATS)

    def module(base: np.ndarray, axis: np.ndarray, scale: float, depth: int, yaw: float) -> None:
        axis = unit(axis)
        u, v, w = basis(axis)
        top = base + w * 1.20 * scale
        b.add_frustum(base, top, 0.070 * scale, 0.025 * scale, 0, sides=14)
        handles: list[tuple[np.ndarray, np.ndarray]] = []
        whorls = [(0.18, 0.50, 8), (0.33, 0.42, 7), (0.49, 0.34, 6), (0.64, 0.26, 5), (0.78, 0.19, 4), (0.91, 0.12, 3)]
        for wi, (h, spread, n) in enumerate(whorls):
            center = base + w * (h * 1.12 * scale)
            for k in range(n):
                th = yaw + 2.0 * math.pi * k / n + wi * 0.17 + rng.normal(0.0, 0.025)
                radial = math.cos(th) * u + math.sin(th) * v
                branch_tip = center + radial * (spread * scale) + w * (0.05 + 0.11 * h) * scale
                b.add_frustum(center, branch_tip, 0.020 * scale * (1.0 - 0.45 * h), 0.006 * scale, 0, sides=8)
                leaf_axis = unit(radial * 0.72 + w * (0.30 + 0.18 * h))
                # Dense cedar pads: a short bridge plus overlapping flattened
                # discs reads much closer to the good snow-cedar texture than
                # long straight needles.
                pad_count = 5 if scale > 0.24 else 3
                for f in range(pad_count):
                    t = (f + 0.35) / pad_count
                    side_angle = th + (f - (pad_count - 1) * 0.5) * 0.12 + rng.normal(0.0, 0.025)
                    side = math.cos(side_angle) * u + math.sin(side_angle) * v
                    pad_center = center * (1.0 - t) + branch_tip * t + side * (0.030 * scale) + w * (0.014 * scale * f)
                    bridge0 = pad_center - leaf_axis * (0.032 * scale)
                    b.add_frustum(branch_tip if f == 0 else pad_center - leaf_axis * (0.045 * scale), bridge0, 0.006 * scale, 0.004 * scale, 1, sides=5)
                    radius = (0.050 + 0.025 * (1.0 - h)) * scale * (1.0 - 0.08 * f)
                    b.add_leaf_disc(pad_center, unit(leaf_axis * 0.85 + side * 0.25), radius, 0.006 * scale, 1, seg=12, squash=0.50)
                    if (wi + k + f) % 4 == 0:
                        b.add_leaf_disc(pad_center + w * 0.012 * scale, unit(leaf_axis * 0.80 + side * 0.18), radius * 0.70, 0.004 * scale, 2, seg=10, squash=0.52)
                if scale > 0.18 and wi in {1, 2, 3} and k % max(1, n // 3) == 0:
                    handles.append((branch_tip, unit(radial * 0.82 + w * 0.70)))
        b.add_ellipsoid(top + w * 0.055 * scale, (0.055 * scale, 0.055 * scale, 0.16 * scale), 2, seg=14, rings=7)
        for k in range(10 if scale > 0.22 else 5):
            th = yaw + 2.0 * math.pi * k / (10 if scale > 0.22 else 5)
            radial = math.cos(th) * u + math.sin(th) * v
            b.add_tri_fin(top - w * 0.05 * scale + radial * 0.015 * scale, unit(w * 1.05 + radial * 0.35), 0.030 * scale, 0.18 * scale, 1 if k % 3 else 2)
        if depth <= 0:
            return
        rng.shuffle(handles)
        for i, (hp, hd) in enumerate(handles[:4 if depth > 1 else 3]):
            child_axis = unit(hd + w * 0.45 + rng.normal(0.0, 0.030, 3))
            child_scale = scale * (0.43 if depth > 1 else 0.36) * rng.uniform(0.93, 1.05)
            child_base = hp + child_axis * (0.030 * scale)
            b.add_frustum(hp, child_base, 0.014 * scale, 0.030 * child_scale, 0, sides=8)
            module(child_base, child_axis, child_scale, depth - 1, yaw + 0.55 * i + rng.normal(0.0, 0.06))

    module(np.array([0.0, 0.0, 0.05]), np.array([0.0, 0.0, 1.0]), 1.0, 3, 0.12)
    for k in range(11):
        th = 2.0 * math.pi * k / 11.0 + rng.normal(0.0, 0.05)
        radial = np.array([math.cos(th), math.sin(th), -0.20])
        p0 = np.array([0.0, 0.0, 0.08])
        p1 = p0 + unit(radial) * rng.uniform(0.34, 0.62)
        b.add_frustum(p0, p1, 0.025, 0.008, 3, sides=7)
        for _ in range(2):
            side = unit(radial + rng.normal(0.0, 0.16, 3) + np.array([0.0, 0.0, -0.15]))
            b.add_frustum(p1, p1 + side * rng.uniform(0.12, 0.24), 0.008, 0.003, 3, sides=6)
    b.normalize(3.0, ground=True)
    return b


def build_crown_ornament(seed: int) -> MeshBuilder:
    rng = np.random.default_rng(seed)
    b = MeshBuilder(CROWN_MATS)
    b.add_ring_tube(np.zeros(3), 0.96, 0.046, 0, major=144, minor=12, z_scale=0.55)
    b.add_ring_tube(np.array([0.0, 0.0, 0.13]), 0.77, 0.027, 0, major=120, minor=8, z_scale=0.46, phase0=0.08)
    b.add_ring_tube(np.array([0.0, 0.0, -0.13]), 0.64, 0.022, 1, major=96, minor=8, z_scale=0.42, phase0=-0.08)
    # Attached radial handles: each prong is bridged to the ring and hosts a smaller contracted motif.
    for k in range(12):
        th = 2.0 * math.pi * k / 12.0
        radial = np.array([math.cos(th), math.sin(th), 0.0])
        tangent = np.array([-math.sin(th), math.cos(th), 0.0])
        root = radial * 0.88
        high = radial * 0.90 + np.array([0.0, 0.0, 0.28 + 0.04 * (k % 2)])
        tip = radial * 1.04 + np.array([0.0, 0.0, 0.42 + 0.06 * (k % 3 == 0)])
        b.add_frustum(root, high, 0.026, 0.020, 0, sides=8)
        b.add_frustum(high, tip, 0.020, 0.014, 3, sides=8)
        b.add_frustum(high, high + tangent * 0.16 - radial * 0.04 + np.array([0.0, 0.0, 0.08]), 0.013, 0.007, 0, sides=6)
        b.add_frustum(high, high - tangent * 0.16 - radial * 0.04 + np.array([0.0, 0.0, 0.08]), 0.013, 0.007, 0, sides=6)
        if k % 2 == 0:
            b.add_ellipsoid(radial * 0.84 + np.array([0.0, 0.0, 0.16]), (0.075, 0.050, 0.035), 2, seg=16, rings=7, rot=np.column_stack([radial, tangent, np.array([0, 0, 1])]))
        # Small recursive child crown motif, contracted and attached by a spoke.
        if k % 3 == 0:
            child_center = radial * 0.48 + np.array([0.0, 0.0, 0.20])
            b.add_frustum(radial * 0.68 + np.array([0.0, 0.0, 0.12]), child_center, 0.012, 0.018, 0, sides=6)
            b.add_ring_tube(child_center, 0.112, 0.010, 3, major=36, minor=6, z_scale=0.45, phase0=th)
            for q in range(4):
                aq = th + 2.0 * math.pi * q / 4.0
                rr = np.array([math.cos(aq), math.sin(aq), 0.0])
                b.add_frustum(child_center + rr * 0.10, child_center + rr * 0.12 + np.array([0.0, 0.0, 0.06]), 0.006, 0.003, 3, sides=5)
    for k in range(24):
        th = 2.0 * math.pi * k / 24.0 + 0.06
        radial = np.array([math.cos(th), math.sin(th), 0.0])
        tangent = np.array([-math.sin(th), math.cos(th), 0.0])
        p0 = radial * 0.72 + np.array([0.0, 0.0, -0.02])
        p1 = radial * 0.86 + tangent * (0.055 * (-1 if k % 2 else 1)) + np.array([0.0, 0.0, 0.19])
        b.add_frustum(p0, p1, 0.007, 0.005, 3 if k % 4 == 0 else 0, sides=5)
    # Inner bridges suppress the old central floating debris by making center structure intentional.
    for k in range(8):
        th = 2.0 * math.pi * k / 8.0 + 0.18
        radial = np.array([math.cos(th), math.sin(th), 0.0])
        b.add_frustum(radial * 0.22 + np.array([0, 0, -0.05]), radial * 0.62 + np.array([0, 0, 0.12]), 0.012, 0.010, 1, sides=6)
    b.add_ellipsoid(np.array([0.0, 0.0, 0.03]), (0.115, 0.115, 0.050), 2, seg=20, rings=8)
    b.normalize(3.0, ground=False)
    return b


def build_scifi_module(seed: int) -> MeshBuilder:
    rng = np.random.default_rng(seed)
    b = MeshBuilder(SCIFI_MATS)
    b.add_box(np.array([0.0, 0.0, 0.35]), np.array([1.05, 0.72, 0.70]), 0)
    b.add_box(np.array([0.0, 0.0, 0.76]), np.array([0.88, 0.56, 0.08]), 1)
    b.add_box(np.array([0.0, 0.0, -0.02]), np.array([0.96, 0.62, 0.10]), 1)
    b.add_box(np.array([0.0, -0.43, 0.35]), np.array([1.16, 0.08, 0.80]), 1)
    b.add_box(np.array([0.0, 0.43, 0.35]), np.array([1.16, 0.08, 0.80]), 1)
    b.add_box(np.array([-0.58, 0.0, 0.35]), np.array([0.08, 0.80, 0.72]), 1)
    b.add_box(np.array([0.58, 0.0, 0.35]), np.array([0.08, 0.80, 0.72]), 1)
    # Recursive attached pods on all four sides.
    for side in range(4):
        th = side * math.pi / 2.0
        radial = np.array([math.cos(th), math.sin(th), 0.0])
        tangent = np.array([-math.sin(th), math.cos(th), 0.0])
        base = radial * 0.66 + np.array([0.0, 0.0, 0.35])
        b.add_frustum(base - radial * 0.10, base + radial * 0.18, 0.055, 0.050, 1, sides=12)
        pod_center = base + radial * 0.34
        rot = np.column_stack([radial, tangent, np.array([0.0, 0.0, 1.0])])
        b.add_box(pod_center, np.array([0.36, 0.28, 0.42]), 0, rot=rot)
        b.add_ellipsoid(pod_center + radial * 0.20, (0.055, 0.055, 0.070), 2, seg=14, rings=7, rot=rot)
        for level in range(2):
            offset = pod_center + radial * (0.18 + 0.18 * level) + np.array([0.0, 0.0, 0.25 - 0.12 * level])
            b.add_box(offset, np.array([0.20, 0.06, 0.08]), 1, rot=rot)
        # A smaller attached child module makes the transform-copy recursion
        # visible without turning into a noisy heap.
        child = pod_center + radial * 0.42 + tangent * (0.16 if side % 2 == 0 else -0.16) + np.array([0.0, 0.0, 0.08])
        b.add_frustum(pod_center + radial * 0.21, child - radial * 0.10, 0.020, 0.018, 1, sides=6)
        b.add_box(child, np.array([0.18, 0.14, 0.18]), 0, rot=rot)
        b.add_ellipsoid(child + radial * 0.11, (0.032, 0.032, 0.040), 2, seg=10, rings=5, rot=rot)
        for sign in (-1, 1):
            strut0 = base + tangent * sign * 0.24 + np.array([0.0, 0.0, -0.24])
            strut1 = pod_center + tangent * sign * 0.17 + np.array([0.0, 0.0, -0.24])
            b.add_frustum(strut0, strut1, 0.025, 0.018, 1, sides=8)
    # Clean panel grooves and antenna towers: no black collapsed heap.
    for x in np.linspace(-0.34, 0.34, 3):
        b.add_box(np.array([x, -0.472, 0.35]), np.array([0.055, 0.030, 0.52]), 3)
        b.add_box(np.array([x, 0.472, 0.35]), np.array([0.055, 0.030, 0.52]), 3)
    for x, y in [(-0.38, -0.25), (0.38, -0.25), (-0.38, 0.25), (0.38, 0.25)]:
        b.add_frustum(np.array([x, y, 0.72]), np.array([x, y, 1.28 + rng.uniform(-0.05, 0.05)]), 0.050, 0.040, 1, sides=14)
        b.add_ellipsoid(np.array([x, y, 1.33]), (0.065, 0.065, 0.045), 2, seg=14, rings=7)
    b.normalize(3.0, ground=True)
    return b


def build_arch_portal(seed: int) -> MeshBuilder:
    _rng = np.random.default_rng(seed)
    b = MeshBuilder(ARCH_MATS)
    # Grounded columns.
    for x in (-0.72, 0.72):
        b.add_box(np.array([x, 0.0, 0.45]), np.array([0.26, 0.36, 0.90]), 0)
        b.add_box(np.array([x, 0.0, 0.08]), np.array([0.42, 0.48, 0.16]), 1)
        b.add_box(np.array([x, 0.0, 0.94]), np.array([0.36, 0.44, 0.14]), 3)
    # Voussoir blocks along arch.
    center = np.array([0.0, 0.0, 0.88])
    for i in range(17):
        t = math.pi - i * math.pi / 16.0
        pos = center + np.array([math.cos(t) * 0.72, 0.0, math.sin(t) * 0.72])
        tangent = np.array([-math.sin(t), 0.0, math.cos(t)])
        radial = unit(pos - center)
        yaxis = np.array([0.0, 1.0, 0.0])
        rot = np.column_stack([tangent, yaxis, radial])
        b.add_box(pos, np.array([0.18, 0.36, 0.24]), 0 if i % 3 else 3, rot=rot)
        if i % 4 == 0 and 0 < i < 16:
            # Nested attached mini-arch ornaments, explicitly bridged.
            child = pos - radial * 0.20 + np.array([0.0, 0.0, -0.10])
            b.add_frustum(pos - radial * 0.06, child, 0.018, 0.016, 1, sides=6)
            for j in range(5):
                a = math.pi - j * math.pi / 4.0
                cpos = child + np.array([math.cos(a) * 0.12, -0.21, math.sin(a) * 0.12])
                b.add_box(cpos, np.array([0.040, 0.050, 0.070]), 3)
    # Thin stone tracery hugging the inner arch: more recursive detail, less
    # block-collapse impression.
    for i in range(13):
        t = math.pi - i * math.pi / 12.0
        p = center + np.array([math.cos(t) * 0.50, -0.23, math.sin(t) * 0.50])
        q = center + np.array([math.cos(t) * 0.61, -0.23, math.sin(t) * 0.61])
        b.add_frustum(p, q, 0.012, 0.010, 3, sides=6)
    # Back/side ribs make it volumetric, not a flat collapsed silhouette.
    for y in (-0.20, 0.20):
        b.add_frustum(np.array([-0.72, y, 0.92]), np.array([0.72, y, 0.92]), 0.030, 0.030, 1, sides=8)
        b.add_frustum(np.array([-0.86, y, 0.08]), np.array([0.86, y, 0.08]), 0.025, 0.025, 1, sides=8)
    # Soft stone wear/moss patches.
    for x in (-0.72, 0.72):
        b.add_box(np.array([x, -0.19, 0.55]), np.array([0.18, 0.018, 0.22]), 2)
    b.normalize(3.0, ground=True)
    return b


def render_preview(mesh: trimesh.Trimesh, mats: np.ndarray, materials: list[Mat], out: Path, elev: float = 18.0, azim: float = -48.0) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    out.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(8, 8), dpi=180)
    ax = fig.add_subplot(111, projection="3d")
    bg = "#dbe3ea"
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    faces = mesh.faces
    if len(faces) > 100000:
        idx = np.linspace(0, len(faces) - 1, 100000).astype(int)
        faces = faces[idx]
        mats = mats[idx]
    tri = mesh.vertices[faces]
    palette = np.asarray([[c / 255.0 for c in m.color] for m in materials], dtype=float)
    colors = palette[np.clip(mats, 0, len(palette) - 1)]
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-9)
    light = unit(np.array([-0.35, -0.45, 0.85]))
    shade = 0.52 + 0.48 * np.clip(normals @ light, 0.0, 1.0)
    colors = colors.copy()
    colors[:, :3] *= shade[:, None]
    ax.add_collection3d(Poly3DCollection(tri, facecolors=colors, linewidths=0.0))
    bounds = mesh.bounds
    z0 = bounds[0, 2] - 0.01
    sx = max(abs(bounds[0, 0]), abs(bounds[1, 0])) + 0.45
    sy = max(abs(bounds[0, 1]), abs(bounds[1, 1])) + 0.45
    platform = np.array([[-sx, -sy, z0], [sx, -sy, z0], [sx, sy, z0], [-sx, sy, z0]])
    ax.add_collection3d(Poly3DCollection([platform], facecolors=(0.82, 0.86, 0.86, 1.0), linewidths=0.0))
    center = (bounds[0] + bounds[1]) * 0.5
    extent = max(float((bounds[1] - bounds[0]).max()), 1e-3) * 0.68
    ax.set_xlim(center[0] - extent, center[0] + extent)
    ax.set_ylim(center[1] - extent, center[1] + extent)
    ax.set_zlim(z0, bounds[1, 2] + extent * 0.08)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_proj_type("persp")
    plt.subplots_adjust(0, 0, 1, 1)
    fig.savefig(out, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def build_all(seed: int) -> dict[str, MeshBuilder]:
    return {
        "lsystem_tree_root_cedar_grammar_v3": build_tree_root(seed + 1),
        "crown_ornament_attached_portal_v1": build_crown_ornament(seed + 2),
        "scifi_module_clean_recursive_v1": build_scifi_module(seed + 3),
        "architectural_arch_portal_bridge_v1": build_arch_portal(seed + 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260510)
    parser.add_argument("--no-preview", action="store_true")
    args = parser.parse_args()

    rows: dict[str, dict[str, object]] = {}
    for name, builder in build_all(args.seed).items():
        case_dir = args.out / name
        info = builder.export(case_dir / f"{name}.obj", case_dir / f"{name}.glb")
        if not args.no_preview:
            mesh = builder.mesh()
            mats = np.asarray(builder.mats, dtype=np.int64)
            render_preview(mesh, mats, builder.materials, case_dir / f"{name}_preview_iso.png")
            render_preview(mesh, mats, builder.materials, case_dir / f"{name}_preview_front.png", elev=10.0, azim=-90.0)
            info["preview_iso"] = str(case_dir / f"{name}_preview_iso.png")
            info["preview_front"] = str(case_dir / f"{name}_preview_front.png")
        info["materials"] = [m.name for m in builder.materials]
        rows[name] = info
    summary = {
        "kind": "publication_repair_candidates_20260510",
        "seed": args.seed,
        "status": "generated",
        "cases": rows,
        "old_failure_root_cause": {
            "tree_root": "root/crown local frame and child attachment handles were inconsistent",
            "crown_radial4": "unattached four-way rotated sparse/mesh copies amplified disconnected fragments under projection/pruning",
            "scifi": "mostly material/camera/dirty root asset rather than topology collapse",
            "snow_arch": "portal insertion survived only partially; disconnected/blocky masses made the arch read collapsed",
        },
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
