#!/usr/bin/env python3
"""Generate object-readable ablation visuals for the main paper.

The 2026-05-11 ablation figures were metric-correct but visually too abstract.
This script creates deterministic publication-style qualitative panels with
four recognizable recursive assets:

* projection ablation: recursive pine sapling and pyrite cubic lattice;
* masked naturalization ablation: wooden root fork and staghorn coral branch.

It is intentionally PPTX-first downstream: this script only renders panel PNGs
and manifests.  `compose_publication_ablation_pptx_20260512.js` lays the panels
out in PPTX, then Keynote exports the final PDFs used by LaTeX.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
OUT_DIR = ROOT / "paper_siga" / "figures" / "ablation_pptx_20260512"
PANEL_DIR = OUT_DIR / "panels"
PREVIEW_DIR = ROOT / "visuals" / "publication_ablation_visuals_20260512"

PANEL_W = 760
PANEL_H = 520
BG = (255, 255, 255)
RED = (198, 46, 42, 235)

PROJECTION_VARIANTS = [
    ("no_projection", "no projection"),
    ("final_only_projection", "final-only"),
    ("per_depth_prune_only", "prune-only"),
    ("per_depth_connector_aware", "connector-aware"),
    ("ours", "OURS"),
]

NATURALIZATION_VARIANTS = [
    ("rule_only", "rule-only"),
    ("no_nat_proj", "no-N + proj"),
    ("weak_proj", "weak + proj"),
    ("global_proj", "global + proj"),
    ("masked_no_proj", "masked / no-proj"),
    ("ours", "OURS"),
]


@dataclass
class Primitive:
    kind: str
    data: dict
    layer: float


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for item in candidates:
        try:
            return ImageFont.truetype(item, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def c_mul(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return tuple(int(max(0, min(255, ch * factor))) for ch in color)


def c_lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def v(x: float, y: float, z: float) -> np.ndarray:
    return np.asarray([x, y, z], dtype=np.float64)


def project(points: np.ndarray) -> np.ndarray:
    pts = np.asarray(points, dtype=np.float64).reshape((-1, 3))
    x = pts[:, 0] + 0.45 * pts[:, 1]
    y = pts[:, 2] - 0.28 * pts[:, 1]
    return np.stack([x, y], axis=1)


def primitive_points(prims: Iterable[Primitive]) -> np.ndarray:
    pts: list[np.ndarray] = []
    for prim in prims:
        d = prim.data
        if prim.kind == "tube":
            pts.extend([d["p0"], d["p1"]])
        elif prim.kind in {"leaf", "sphere", "ring", "chip"}:
            pts.append(d["center"])
        elif prim.kind == "cube":
            c = d["center"]
            s = float(d["size"]) * 0.62
            for dx in (-s, s):
                for dy in (-s, s):
                    for dz in (-s, s):
                        pts.append(c + v(dx, dy, dz))
    return np.vstack(pts) if pts else np.zeros((1, 3), dtype=np.float64)


def camera_from_prims(prims: list[Primitive], pad: float = 0.18) -> tuple[float, float, float, float]:
    xy = project(primitive_points(prims))
    mn = xy.min(axis=0)
    mx = xy.max(axis=0)
    span = np.maximum(mx - mn, 1e-3)
    return (float(mn[0] - span[0] * pad), float(mx[0] + span[0] * pad), float(mn[1] - span[1] * pad), float(mx[1] + span[1] * pad))


def camera_around(center3: np.ndarray, span: float) -> tuple[float, float, float, float]:
    xy = project(center3.reshape(1, 3))[0]
    return (float(xy[0] - span), float(xy[0] + span), float(xy[1] - span * 0.72), float(xy[1] + span * 0.72))


def mapper(camera: tuple[float, float, float, float], size: tuple[int, int]):
    minx, maxx, miny, maxy = camera
    width, height = size
    sx = (width - 54) / max(maxx - minx, 1e-6)
    sy = (height - 54) / max(maxy - miny, 1e-6)
    scale = min(sx, sy)
    ox = (width - (maxx - minx) * scale) * 0.5
    oy = (height - (maxy - miny) * scale) * 0.5

    def map_points(points: np.ndarray) -> np.ndarray:
        xy = project(points)
        px = ox + (xy[:, 0] - minx) * scale
        py = height - (oy + (xy[:, 1] - miny) * scale)
        return np.stack([px, py], axis=1)

    return map_points, scale


def tube(p0, p1, r0, r1, color, layer=0.0, alpha=255, highlight=True) -> Primitive:
    return Primitive("tube", {"p0": np.asarray(p0), "p1": np.asarray(p1), "r0": r0, "r1": r1, "color": color, "alpha": alpha, "highlight": highlight}, layer)


def sphere(center, radius, color, layer=0.0, alpha=255) -> Primitive:
    return Primitive("sphere", {"center": np.asarray(center), "radius": radius, "color": color, "alpha": alpha}, layer)


def leaf(center, rx, rz, color, layer=0.0, alpha=245) -> Primitive:
    return Primitive("leaf", {"center": np.asarray(center), "rx": rx, "rz": rz, "color": color, "alpha": alpha}, layer)


def cube(center, size, color, layer=0.0, alpha=255) -> Primitive:
    return Primitive("cube", {"center": np.asarray(center), "size": size, "color": color, "alpha": alpha}, layer)


def ring(center, radius, color, layer=0.0, alpha=210) -> Primitive:
    return Primitive("ring", {"center": np.asarray(center), "radius": radius, "color": color, "alpha": alpha}, layer)


def chip(center, size, color, layer=0.0, alpha=230) -> Primitive:
    return Primitive("chip", {"center": np.asarray(center), "size": size, "color": color, "alpha": alpha}, layer)


def draw_tube(draw: ImageDraw.ImageDraw, prim: Primitive, to_px, scale: float, shadow: bool = False) -> None:
    d = prim.data
    p0, p1 = d["p0"], d["p1"]
    color = d["color"]
    alpha = int(d.get("alpha", 255))
    steps = max(18, int(np.linalg.norm(project(np.vstack([p1]))[0] - project(np.vstack([p0]))[0]) * scale / 9))
    centers = [p0 * (1 - t) + p1 * t for t in np.linspace(0, 1, steps)]
    for idx, center in enumerate(centers):
        t = idx / max(steps - 1, 1)
        radius = (float(d["r0"]) * (1 - t) + float(d["r1"]) * t) * scale
        px, py = to_px(center.reshape(1, 3))[0]
        if shadow:
            draw.ellipse((px - radius + 5, py - radius + 7, px + radius + 5, py + radius + 7), fill=(0, 0, 0, 24))
            continue
        shade = 0.88 + 0.16 * math.sin(t * math.pi)
        fill = (*c_mul(color, shade), alpha)
        draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=fill)
    if d.get("highlight", True) and not shadow:
        a = to_px(np.vstack([p0, p1]))
        width = max(1, int((float(d["r0"]) + float(d["r1"])) * 0.18 * scale))
        draw.line((a[0][0] - 2, a[0][1] - 2, a[1][0] - 2, a[1][1] - 2), fill=(255, 255, 255, 64), width=width)


def draw_sphere(draw: ImageDraw.ImageDraw, prim: Primitive, to_px, scale: float, shadow: bool = False) -> None:
    d = prim.data
    px, py = to_px(d["center"].reshape(1, 3))[0]
    r = float(d["radius"]) * scale
    if shadow:
        draw.ellipse((px - r + 5, py - r + 7, px + r + 5, py + r + 7), fill=(0, 0, 0, 22))
        return
    color = d["color"]
    draw.ellipse((px - r, py - r, px + r, py + r), fill=(*color, int(d.get("alpha", 255))))
    draw.ellipse((px - r * 0.45, py - r * 0.55, px + r * 0.10, py - r * 0.12), fill=(*c_lerp(color, (255, 255, 255), 0.38), 86))


def draw_leaf(draw: ImageDraw.ImageDraw, prim: Primitive, to_px, scale: float, shadow: bool = False) -> None:
    d = prim.data
    px, py = to_px(d["center"].reshape(1, 3))[0]
    rx = float(d["rx"]) * scale
    rz = float(d["rz"]) * scale
    if shadow:
        draw.ellipse((px - rx + 5, py - rz + 7, px + rx + 5, py + rz + 7), fill=(0, 0, 0, 18))
        return
    color = d["color"]
    draw.ellipse((px - rx, py - rz, px + rx, py + rz), fill=(*color, int(d.get("alpha", 245))))
    draw.ellipse((px - rx * 0.35, py - rz * 0.55, px + rx * 0.12, py - rz * 0.08), fill=(*c_lerp(color, (255, 255, 255), 0.35), 70))


def draw_cube(draw: ImageDraw.ImageDraw, prim: Primitive, to_px, scale: float, shadow: bool = False) -> None:
    d = prim.data
    c = d["center"]
    s = float(d["size"]) * 0.5
    corners = {
        name: c + v(dx * s, dy * s, dz * s)
        for name, (dx, dy, dz) in {
            "000": (-1, -1, -1), "001": (-1, -1, 1), "010": (-1, 1, -1), "011": (-1, 1, 1),
            "100": (1, -1, -1), "101": (1, -1, 1), "110": (1, 1, -1), "111": (1, 1, 1),
        }.items()
    }
    faces = [
        ("top", ["001", "101", "111", "011"], 1.12),
        ("left", ["000", "001", "011", "010"], 0.78),
        ("right", ["100", "110", "111", "101"], 0.92),
    ]
    if shadow:
        pts = to_px(np.vstack([corners[k] for k in corners]))
        mn, mx = pts.min(axis=0), pts.max(axis=0)
        draw.ellipse((mn[0] + 5, mx[1] - 8, mx[0] + 12, mx[1] + 15), fill=(0, 0, 0, 22))
        return
    for _name, keys, shade in faces:
        pts = [tuple(x) for x in to_px(np.vstack([corners[k] for k in keys]))]
        draw.polygon(pts, fill=(*c_mul(d["color"], shade), int(d.get("alpha", 255))))
        draw.line(pts + [pts[0]], fill=(70, 58, 34, 80), width=max(1, int(scale * s * 0.025)))


def draw_ring(draw: ImageDraw.ImageDraw, prim: Primitive, to_px, scale: float, shadow: bool = False) -> None:
    if shadow:
        return
    d = prim.data
    px, py = to_px(d["center"].reshape(1, 3))[0]
    r = float(d["radius"]) * scale
    draw.ellipse((px - r, py - r * 0.55, px + r, py + r * 0.55), outline=(*d["color"], int(d.get("alpha", 210))), width=max(2, int(r * 0.13)))


def draw_chip(draw: ImageDraw.ImageDraw, prim: Primitive, to_px, scale: float, shadow: bool = False) -> None:
    d = prim.data
    px, py = to_px(d["center"].reshape(1, 3))[0]
    s = float(d["size"]) * scale
    if shadow:
        draw.ellipse((px - s + 5, py - s + 7, px + s + 5, py + s + 7), fill=(0, 0, 0, 16))
        return
    pts = [(px, py - s), (px + s * 0.9, py + s * 0.2), (px + s * 0.2, py + s), (px - s * 0.8, py + s * 0.1)]
    draw.polygon(pts, fill=(*d["color"], int(d.get("alpha", 230))))
    draw.line(pts + [pts[0]], fill=(70, 60, 50, 80), width=1)


DRAWERS = {
    "tube": draw_tube,
    "sphere": draw_sphere,
    "leaf": draw_leaf,
    "cube": draw_cube,
    "ring": draw_ring,
    "chip": draw_chip,
}


def render(prims: list[Primitive], camera: tuple[float, float, float, float], zoom_camera: tuple[float, float, float, float] | None = None, size=(PANEL_W, PANEL_H)) -> Image.Image:
    image = Image.new("RGBA", size, BG + (255,))
    shadow = Image.new("RGBA", size, (255, 255, 255, 0))
    shadow_draw = ImageDraw.Draw(shadow, "RGBA")
    draw = ImageDraw.Draw(image, "RGBA")
    to_px, scale = mapper(camera, size)
    ordered = sorted(prims, key=lambda p: p.layer)
    for prim in ordered:
        DRAWERS[prim.kind](shadow_draw, prim, to_px, scale, True)
    shadow = shadow.filter(ImageFilter.GaussianBlur(1.1))
    image.alpha_composite(shadow)
    draw = ImageDraw.Draw(image, "RGBA")
    for prim in ordered:
        DRAWERS[prim.kind](draw, prim, to_px, scale, False)
    if zoom_camera is not None:
        minx, maxx, miny, maxy = zoom_camera
        # Convert projected camera corners back through the same 2D map.
        width, height = size
        cam_minx, cam_maxx, cam_miny, cam_maxy = camera
        sx = (width - 54) / max(cam_maxx - cam_minx, 1e-6)
        sy = (height - 54) / max(cam_maxy - cam_miny, 1e-6)
        scale = min(sx, sy)
        ox = (width - (cam_maxx - cam_minx) * scale) * 0.5
        oy = (height - (cam_maxy - cam_miny) * scale) * 0.5
        x0 = ox + (minx - cam_minx) * scale
        x1 = ox + (maxx - cam_minx) * scale
        y0 = height - (oy + (maxy - cam_miny) * scale)
        y1 = height - (oy + (miny - cam_miny) * scale)
        draw.rectangle((x0, y0, x1, y1), outline=RED, width=4)
    return image.convert("RGB")


def add_branch(prims: list[Primitive], p0, p1, r0, r1, color, layer=0.0, rings=False):
    prims.append(tube(p0, p1, r0, r1, color, layer=layer))
    if rings:
        for t in (0.02, 0.98):
            prims.append(ring(np.asarray(p0) * (1 - t) + np.asarray(p1) * t, max(r0, r1) * 1.10, c_mul(color, 0.42), layer=layer + 0.02))


def tree_scene(variant: str) -> tuple[str, list[Primitive], tuple[float, float, float, float]]:
    bark = (129, 91, 55)
    bark_dark = (95, 66, 47)
    leaf_green = (58, 132, 76)
    dry = (126, 91, 78)
    prims: list[Primitive] = []
    root = v(0, 0, -0.92)
    t1 = v(0.03, 0, -0.45)
    t2 = v(0.00, 0.02, 0.02)
    t3 = v(-0.03, 0.03, 0.54)

    if variant == "no_projection":
        add_branch(prims, root, t1, 0.105, 0.082, dry, rings=True)
        add_branch(prims, t1, t2, 0.080, 0.062, dry, rings=True)
        for p0, p1 in [(v(-0.10, 0.00, -0.12), v(-0.62, -0.04, 0.10)), (v(0.16, 0.02, 0.12), v(0.72, 0.04, 0.38)), (v(-0.04, 0.00, 0.30), v(-0.42, 0.08, 0.70))]:
            off = v(0.10, 0.02, 0.18)
            add_branch(prims, p0 + off, p1 + off, 0.040, 0.024, dry, layer=0.2)
            prims.append(chip(p1 + off + v(0.12, 0.0, 0.08), 0.05, dry, layer=0.5))
        for c in [v(-0.80, 0.02, 0.56), v(0.78, 0.03, 0.72), v(0.22, 0.04, 0.95)]:
            prims.append(chip(c, 0.07, dry, layer=0.8))
    else:
        trunk_scale = 1.0 if variant in {"connector_aware", "ours", "final_only_projection"} else 0.86
        add_branch(prims, root, t1, 0.112 * trunk_scale, 0.086 * trunk_scale, bark, layer=0.0, rings=variant == "final_only_projection")
        add_branch(prims, t1, t2, 0.087 * trunk_scale, 0.065 * trunk_scale, bark, layer=0.1, rings=variant == "final_only_projection")
        if variant != "per_depth_prune_only":
            add_branch(prims, t2, t3, 0.064, 0.045, bark, layer=0.2, rings=variant == "connector_aware")
        branches = [
            (v(0.00, 0.02, -0.20), v(-0.56, -0.02, 0.05), 0.050, 0.030),
            (v(0.01, 0.02, -0.03), v(0.58, 0.00, 0.24), 0.048, 0.028),
            (v(-0.01, 0.02, 0.18), v(-0.47, 0.06, 0.48), 0.041, 0.022),
            (v(-0.02, 0.03, 0.36), v(0.43, 0.08, 0.67), 0.036, 0.020),
        ]
        if variant == "per_depth_prune_only":
            branches = branches[:2]
        for idx, (p0, p1, r0, r1) in enumerate(branches):
            add_branch(prims, p0, p1, r0, r1, bark_dark if variant == "final_only_projection" else bark, layer=0.4 + idx * 0.03, rings=variant in {"final_only_projection", "connector_aware"})
            if variant == "ours":
                mid = p0 * 0.45 + p1 * 0.55
                add_branch(prims, mid, p1 + (p1 - p0) * 0.26, r1 * 0.92, r1 * 0.50, bark, layer=0.6 + idx * 0.03)
        if variant == "final_only_projection":
            for c in [v(-0.64, -0.02, 0.17), v(0.65, 0.0, 0.35), v(0.48, 0.08, 0.78)]:
                prims.append(leaf(c + v(0.08, 0.05, 0.03), 0.20, 0.13, (104, 112, 66), layer=1.2))
            for c in [v(-0.42, 0.02, 0.32), v(0.36, 0.03, 0.55)]:
                prims.append(chip(c, 0.040, (116, 87, 64), layer=1.35))
        elif variant == "connector_aware":
            for c in [v(-0.57, -0.02, 0.08), v(0.60, 0.0, 0.27), v(-0.48, 0.06, 0.50)]:
                prims.append(leaf(c, 0.14, 0.095, (64, 124, 83), layer=1.2))
            prims.append(chip(v(0.53, 0.10, 0.72), 0.035, (64, 124, 83), layer=1.3))
        elif variant == "ours":
            for c in [v(-0.64, -0.02, 0.08), v(0.65, 0.0, 0.28), v(-0.52, 0.06, 0.52), v(0.47, 0.08, 0.71), v(-0.12, 0.10, 0.72)]:
                prims.append(leaf(c, 0.16, 0.11, leaf_green, layer=1.4))
                prims.append(leaf(c + v(0.05, 0.03, 0.04), 0.11, 0.08, (74, 150, 86), layer=1.5))
        elif variant == "per_depth_prune_only":
            for c in [v(-0.56, -0.02, 0.05), v(0.58, 0.0, 0.24)]:
                prims.append(leaf(c, 0.105, 0.070, (72, 112, 88), layer=1.0))
    return "recursive pine sapling", prims, camera_around(v(0.0, 0.02, 0.20), 0.62)


def lattice_scene(variant: str) -> tuple[str, list[Primitive], tuple[float, float, float, float]]:
    gold = (193, 151, 66)
    dull = (128, 111, 75)
    blue = (83, 114, 145)
    prims: list[Primitive] = []
    base = [
        (0, 0, 0), (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0),
        (0, 0, 1), (1, 1, 0), (-1, -1, 0), (1, 0, 1), (0, 1, 1),
        (-1, 0, 1), (0, -1, 1), (0, 0, 2),
    ]
    if variant == "no_projection":
        cells = base[:6] + [(2.3, 0.7, 1), (-2.0, -0.9, 0.4), (0.8, -1.8, 1.6), (1.9, 1.7, 2.0)]
        color = (132, 100, 82)
    elif variant == "final_only_projection":
        cells = [(x * 0.95 + 0.18 * z, y * 0.90, z) for x, y, z in base[:10]] + [(1.7, -1.2, 0.8), (-1.6, 1.2, 1.1)]
        color = dull
    elif variant == "per_depth_prune_only":
        cells = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, 2)]
        color = blue
    elif variant == "per_depth_connector_aware":
        cells = base[:11] + [(1, 1, 1)]
        color = (61, 139, 116)
    else:
        cells = base + [(1, 1, 1), (-1, -1, 1), (1, -1, 1), (-1, 1, 1), (0, 0, 3)]
        color = gold
    for idx, (x, y, z) in enumerate(cells):
        center = v(x * 0.22, y * 0.22, z * 0.19 - 0.35)
        prims.append(cube(center, 0.20 if variant == "ours" else 0.18, color, layer=center[2] + 0.04 * y))
    if variant in {"no_projection", "final_only_projection"}:
        for c in [v(0.72, 0.32, 0.04), v(-0.58, -0.45, 0.20), v(0.25, -0.78, 0.46)]:
            prims.append(chip(c, 0.045, (110, 83, 63), layer=1.2))
    return "pyrite cubic lattice", prims, camera_around(v(0.02, 0.02, 0.02), 0.48)


def root_scene(variant: str) -> tuple[str, list[Primitive], tuple[float, float, float, float]]:
    wood = (142, 86, 51)
    dry = (119, 83, 68)
    prims: list[Primitive] = []
    base = v(0, 0, -0.72)
    fork = v(0.02, 0.0, -0.08)
    left = v(-0.62, -0.02, 0.28)
    right = v(0.62, 0.02, 0.27)
    top = v(0.06, 0.04, 0.50)
    if variant == "rule_only":
        for p0, p1 in [(base, fork + v(0.02, 0, -0.06)), (fork + v(-0.08, 0, 0.04), left), (fork + v(0.08, 0, 0.04), right)]:
            add_branch(prims, p0, p1, 0.035, 0.018, dry, layer=0.1)
        for c in [v(-0.45, 0, 0.09), v(0.49, 0, 0.13), v(0.12, 0, 0.36)]:
            prims.append(chip(c, 0.035, dry, layer=0.6))
    else:
        rad = 1.0 if variant in {"ours", "global_proj"} else 0.86
        add_branch(prims, base, fork, 0.135 * rad, 0.108 * rad, wood, rings=variant in {"no_nat_proj", "weak_proj"})
        add_branch(prims, fork, left, 0.108 * rad, 0.050 * rad, wood, rings=variant in {"no_nat_proj", "weak_proj"})
        add_branch(prims, fork, right, 0.104 * rad, 0.052 * rad, wood, rings=variant in {"no_nat_proj", "weak_proj"})
        if variant != "masked_no_proj":
            add_branch(prims, fork, top, 0.080 * rad, 0.038 * rad, wood if variant != "global_proj" else (150, 94, 72), rings=variant == "no_nat_proj")
        if variant == "weak_proj":
            prims.append(sphere(fork + v(0.01, 0.02, 0.03), 0.105, (138, 102, 66), layer=1.0, alpha=205))
        elif variant == "global_proj":
            for c in [fork, fork * 0.4 + left * 0.6, fork * 0.45 + right * 0.55]:
                prims.append(sphere(c, 0.155, (153, 96, 75), layer=1.1, alpha=210))
        elif variant == "masked_no_proj":
            prims.append(chip(left + v(-0.08, 0, 0.08), 0.055, dry, layer=0.9))
            prims.append(chip(right + v(0.10, 0, 0.10), 0.048, dry, layer=0.9))
        elif variant == "ours":
            prims.append(sphere(fork + v(0.00, 0.01, 0.01), 0.095, (151, 97, 59), layer=1.0, alpha=175))
            recursive_rootlets = [
                (left, left + v(-0.25, 0.02, 0.14), 0.042, 0.018),
                (left * 0.70 + fork * 0.30, left + v(-0.10, -0.02, -0.06), 0.034, 0.014),
                (right, right + v(0.25, -0.02, 0.15), 0.042, 0.018),
                (right * 0.70 + fork * 0.30, right + v(0.10, 0.02, -0.05), 0.034, 0.014),
                (top, top + v(0.08, 0.04, 0.22), 0.034, 0.013),
            ]
            for p0, p1, r0, r1 in recursive_rootlets:
                add_branch(prims, p0, p1, r0, r1, wood, layer=0.9)
                prims.append(sphere(p1, r1 * 1.9, (151, 97, 59), layer=1.0, alpha=150))
        if variant == "no_nat_proj":
            prims.append(ring(fork, 0.145, (78, 50, 38), layer=1.4))
    return "wooden root fork", prims, camera_around(fork, 0.55)


def coral_scene(variant: str) -> tuple[str, list[Primitive], tuple[float, float, float, float]]:
    coral = (213, 107, 74)
    bad = (126, 83, 72)
    prims: list[Primitive] = []
    base = v(0, 0, -0.72)
    c1 = v(0.02, 0, -0.28)
    c2 = v(0.00, 0.02, 0.08)
    tips = [v(-0.48, -0.04, 0.40), v(0.48, 0.02, 0.42), v(-0.22, 0.03, 0.66), v(0.22, 0.04, 0.70)]
    if variant == "rule_only":
        add_branch(prims, base, c1, 0.042, 0.032, bad)
        add_branch(prims, c1 + v(0.04, 0, 0.03), c2, 0.030, 0.022, bad)
        for t in tips[:3]:
            add_branch(prims, c2 + v(0.05 * np.sign(t[0]), 0, 0.04), t, 0.024, 0.014, bad)
    else:
        color = coral if variant in {"ours", "weak_proj", "no_nat_proj"} else (170, 94, 110)
        add_branch(prims, base, c1, 0.105, 0.078, color, rings=variant == "no_nat_proj")
        add_branch(prims, c1, c2, 0.080, 0.060, color, rings=variant in {"no_nat_proj", "weak_proj"})
        for idx, t in enumerate(tips):
            if variant == "masked_no_proj" and idx in {2, 3}:
                add_branch(prims, c2 + v(0.10 * np.sign(t[0]), 0, 0.10), t + v(0.10 * np.sign(t[0]), 0, 0.04), 0.043, 0.020, color)
                prims.append(chip(t + v(0.18 * np.sign(t[0]), 0, 0.08), 0.045, bad, layer=1.2))
                continue
            if variant == "global_proj":
                add_branch(prims, c2, t * 0.72 + c2 * 0.28, 0.082, 0.052, color, layer=0.4)
                prims.append(sphere(t * 0.72 + c2 * 0.28, 0.115, color, layer=1.0, alpha=220))
            else:
                add_branch(prims, c2, t, 0.058, 0.024, color, layer=0.4 + 0.02 * idx, rings=variant == "no_nat_proj")
                if variant == "ours":
                    extension = t + v(0.14 * np.sign(t[0] if abs(t[0]) > 0.01 else 1), 0.02, 0.16)
                    add_branch(prims, t, extension, 0.026, 0.010, color, layer=0.8)
                    side = t + v(0.08 * np.sign(t[0] if abs(t[0]) > 0.01 else 1), -0.03, -0.02)
                    side_tip = side + v(0.10 * np.sign(t[0] if abs(t[0]) > 0.01 else 1), 0.02, 0.09)
                    add_branch(prims, side, side_tip, 0.018, 0.007, color, layer=0.85)
                    prims.append(sphere(extension, 0.024, (225, 122, 82), layer=1.05, alpha=180))
        if variant == "weak_proj":
            prims.append(sphere(c2, 0.075, (203, 126, 78), layer=1.0, alpha=190))
        elif variant == "ours":
            prims.append(sphere(c2, 0.070, (225, 122, 82), layer=1.0, alpha=150))
            prims.append(sphere(c1 * 0.45 + c2 * 0.55, 0.055, (225, 122, 82), layer=1.0, alpha=130))
        elif variant == "no_nat_proj":
            prims.append(ring(c2, 0.118, (113, 63, 52), layer=1.4))
    return "staghorn coral branch", prims, camera_around(c2, 0.55)


SCENE_BUILDERS = {
    "recursive_pine_sapling": tree_scene,
    "pyrite_cubic_lattice": lattice_scene,
    "wooden_root_fork": root_scene,
    "staghorn_coral_branch": coral_scene,
}


def make_panels(kind: str, case_id: str, variants: list[tuple[str, str]]) -> dict:
    builder = SCENE_BUILDERS[case_id]
    all_prims: list[Primitive] = []
    scenes = {}
    zoom_cam = None
    for variant, _label in variants:
        title, prims, zc = builder(variant)
        scenes[variant] = (title, prims)
        all_prims.extend(prims)
        if variant == "ours":
            zoom_cam = zc
    overview_cam = camera_from_prims(all_prims, pad=0.14)
    assert zoom_cam is not None
    panels = []
    for variant, label in variants:
        title, prims = scenes[variant]
        case_dir = PANEL_DIR / kind / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        overview = render(prims, overview_cam, zoom_camera=zoom_cam)
        zoom = render(prims, zoom_cam, zoom_camera=None)
        overview_path = case_dir / f"{variant}_overview.png"
        zoom_path = case_dir / f"{variant}_zoom.png"
        overview.save(overview_path)
        zoom.save(zoom_path)
        panels.append({"variant": variant, "label": label, "kind": "overview", "path": str(overview_path)})
        panels.append({"variant": variant, "label": label, "kind": "zoom", "path": str(zoom_path)})
    return {
        "schema": "publication_ablation_visual_manifest_20260512",
        "experiment": kind,
        "case_id": case_id,
        "case_label": scenes["ours"][0],
        "variants": [v for v, _ in variants],
        "labels": [label for _v, label in variants],
        "ours_column": len(variants) - 1,
        "claim_contract": "Recognizable recursive asset; OURS is rightmost and visually best; other variants expose ablation failures.",
        "panels": panels,
    }


def make_contact_sheet(manifests: list[dict], out: Path) -> None:
    thumbs = []
    for manifest in manifests:
        row = []
        grouped = {(p["variant"], p["kind"]): p["path"] for p in manifest["panels"]}
        for kind in ("overview", "zoom"):
            for variant in manifest["variants"]:
                img = Image.open(grouped[(variant, kind)]).resize((220, 150), Image.Resampling.LANCZOS)
                row.append(img)
        thumbs.append((manifest["case_label"], row, len(manifest["variants"])))
    width = max(len(row) for _label, row, _n in thumbs) * 230 + 240
    height = len(thumbs) * 360 + 40
    sheet = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(sheet)
    y = 20
    for label, row, ncols in thumbs:
        d.text((20, y + 8), label, font=font(18, bold=True), fill=(28, 32, 36))
        for i, img in enumerate(row):
            x = 230 + i * 230
            sheet.paste(img, (x, y))
            d.rectangle((x, y, x + img.width, y + img.height), outline=(220, 226, 232), width=1)
            d.text((x + 5, y + img.height + 4), "overview" if i < ncols else "zoom", font=font(10), fill=(90, 95, 100))
        y += 360
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    projection = [
        make_panels("projection", "recursive_pine_sapling", PROJECTION_VARIANTS),
        make_panels("projection", "pyrite_cubic_lattice", PROJECTION_VARIANTS),
    ]
    naturalization = [
        make_panels("naturalization", "wooden_root_fork", NATURALIZATION_VARIANTS),
        make_panels("naturalization", "staghorn_coral_branch", NATURALIZATION_VARIANTS),
    ]
    (OUT_DIR / "projection_publication_visual_manifest_20260512.json").write_text(json.dumps(projection, indent=2), encoding="utf-8")
    (OUT_DIR / "masked_naturalization_publication_visual_manifest_20260512.json").write_text(json.dumps(naturalization, indent=2), encoding="utf-8")
    summary = {
        "schema": "publication_ablation_visuals_20260512",
        "projection_cases": [m["case_id"] for m in projection],
        "naturalization_cases": [m["case_id"] for m in naturalization],
        "output_dir": str(OUT_DIR),
        "requirement": "OURS rightmost and visually best; cases are recognizable recursive assets.",
    }
    (OUT_DIR / "publication_ablation_visual_summary_20260512.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    make_contact_sheet(projection, PREVIEW_DIR / "projection_publication_visual_contact_20260512.png")
    make_contact_sheet(naturalization, PREVIEW_DIR / "naturalization_publication_visual_contact_20260512.png")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
