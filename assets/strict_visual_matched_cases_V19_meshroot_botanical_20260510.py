#!/usr/bin/env python3
"""V19 strict matched botanical/root generator using real GLB mesh tokens.

V19 keeps the same traditional control sources as the L-system and
space-colonization baselines, but the visible botanical detail is composed from
real project GLB meshes.  The dry run exports OBJ inputs plus guide images for
fresh Trellis2 texturing on a100-2 GPUs 4/5/6/7.
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

import baseline_matrix_20260509 as bm
import procedural_baselines as pb
import recursive_growth_mesh_metrics as rgm
import space_colonization_baseline as scb
import strict_visual_matched_cases_v17_plants_roots_20260510 as v17


REMOTE_TARGET = "a100-2"
ALLOWED_GPUS = [4, 5, 6, 7]
REMOTE_STORAGE_ROOT = "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
STORAGE_LIMIT_GB = 100
CONNECTIVITY_LCR_MIN = 0.999
DEFAULT_OUT = ROOT_DIR / "results" / "strict_visual_matched_cases_V19_meshroot_botanical_20260510_dryrun"

TOKEN_SOURCES = {
    "tree": "visuals/textured_glb_20260508/tree_compete_s3/textured.glb",
    "vine": "visuals/textured_glb_20260508/vine_d5_compete_s5_inference/textured.glb",
    "root": "visuals/public_guide_textured_glb_20260509/tree_compete_d4_pruned_tree_roots_steps8_tex2048_xformers/textured.glb",
    "meshroot_vine": "visuals/gen3d_baseline_texture_fairness_20260510/meshspace_genroot_vine_d2/textured.glb",
}
TOKEN_FACE_BUDGET = 180


class MeshToken:
    def __init__(
        self,
        name: str,
        source: str,
        vertices: np.ndarray,
        faces: np.ndarray,
        original_vertices: int,
        original_faces: int,
        fallback_used: bool,
    ) -> None:
        self.name = name
        self.source = source
        self.vertices = vertices
        self.faces = faces
        self.original_vertices = int(original_vertices)
        self.original_faces = int(original_faces)
        self.fallback_used = bool(fallback_used)


def _load_scene_mesh(path: Path) -> tuple[np.ndarray, np.ndarray]:
    import trimesh

    loaded = trimesh.load(str(path), force="scene", process=False)
    meshes = []
    if isinstance(loaded, trimesh.Trimesh):
        meshes = [loaded]
    elif isinstance(loaded, trimesh.Scene):
        for geom in loaded.geometry.values():
            if isinstance(geom, trimesh.Trimesh) and len(geom.vertices) and len(geom.faces):
                meshes.append(geom)
    if not meshes:
        raise RuntimeError(f"no mesh geometry found in {path}")
    vertices_all = []
    faces_all = []
    offset = 0
    for mesh in meshes:
        verts = np.asarray(mesh.vertices, dtype=float)
        faces = np.asarray(mesh.faces[:, :3], dtype=np.int64)
        vertices_all.append(verts)
        faces_all.append(faces + offset)
        offset += len(verts)
    return np.vstack(vertices_all), np.vstack(faces_all)


def _tiny_fallback_token(name: str) -> MeshToken:
    mesh = pb.Mesh([], [])
    pb.add_cylinder(mesh, np.array([0.0, 0.0, -0.5]), np.array([0.0, 0.0, 0.5]), 0.18, 0.08, sides=12)
    base = len(mesh.vertices)
    for z, r in ((-0.30, 0.22), (0.05, 0.16), (0.34, 0.10)):
        for i in range(12):
            theta = math.tau * i / 12
            mesh.vertices.append((math.cos(theta) * r, math.sin(theta) * r, z))
        ring = [base + 12 * list((( -0.30, 0.22), (0.05, 0.16), (0.34, 0.10))).index((z, r)) + i + 1 for i in range(12)]
        for i in range(12):
            mesh.faces.append((1, ring[i], ring[(i + 1) % 12]))
    verts = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64) - 1
    return MeshToken(name, "tiny_procedural_fallback", verts, faces, len(verts), len(faces), True)


def _normalize_token(name: str, source: str, vertices: np.ndarray, faces: np.ndarray, seed: int) -> MeshToken:
    original_vertices = int(len(vertices))
    original_faces = int(len(faces))
    if len(vertices) == 0 or len(faces) == 0:
        return _tiny_fallback_token(name)
    stride = max(int(len(faces) // TOKEN_FACE_BUDGET), 1)
    offset = seed % stride
    chosen = faces[offset::stride][:TOKEN_FACE_BUDGET]
    if len(chosen) < min(80, len(faces)):
        chosen = faces[: min(TOKEN_FACE_BUDGET, len(faces))]
    used, inverse = np.unique(chosen.reshape(-1), return_inverse=True)
    verts = np.asarray(vertices[used], dtype=float)
    selected_faces = inverse.reshape((-1, 3)).astype(np.int64)
    center = (verts.min(axis=0) + verts.max(axis=0)) * 0.5
    extent = max(float((verts.max(axis=0) - verts.min(axis=0)).max()), 1e-6)
    verts = (verts - center) / extent
    return MeshToken(name, source, verts, selected_faces, original_vertices, original_faces, False)


def load_token_library(root: Path, seed: int = 20260510, use_tiny_fallback: bool = False) -> dict[str, MeshToken]:
    tokens: dict[str, MeshToken] = {}
    for i, (name, rel) in enumerate(TOKEN_SOURCES.items()):
        path = root / rel
        if use_tiny_fallback:
            tokens[name] = _tiny_fallback_token(name)
            continue
        try:
            vertices, faces = _load_scene_mesh(path)
            tokens[name] = _normalize_token(name, rel, vertices, faces, seed + i * 97)
        except Exception:
            tokens[name] = _tiny_fallback_token(name)
    return tokens


def _append_token_stamp(
    mesh: pb.Mesh,
    token: MeshToken,
    center_index: int,
    anchor: np.ndarray,
    direction: np.ndarray,
    scale: float,
    roll: float,
) -> int:
    u, v, w = v17._basis(direction)
    c = np.asarray(anchor, dtype=float)
    base = len(mesh.vertices)
    ca, sa = math.cos(roll), math.sin(roll)
    for x, y, z in token.vertices:
        xr = ca * x - sa * y
        yr = sa * x + ca * y
        p = c + (u * xr + v * yr + w * z) * float(scale)
        mesh.vertices.append(tuple(p))
    bridge_count = 0
    for face in token.faces:
        a, b, cidx = (int(face[0]) + base + 1, int(face[1]) + base + 1, int(face[2]) + base + 1)
        if a == b or b == cidx or a == cidx:
            continue
        mesh.faces.append((a, b, cidx))
        mesh.faces.append((center_index, a, b))
        bridge_count += 1
    return bridge_count


def _select_anchors(nodes: list[np.ndarray], parents: list[int], count: int, prefer_terminal: bool) -> list[int]:
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    child_map = v17._children(parents)
    if prefer_terminal:
        candidates = [i for i in range(1, len(nodes)) if not child_map.get(i)]
    else:
        candidates = [i for i in range(1, len(nodes)) if depths[i] >= max_depth * 0.45]
    if not candidates:
        candidates = list(range(1, len(nodes)))
    candidates = sorted(candidates, key=lambda i: (depths[i], i), reverse=True)
    if len(candidates) >= count:
        step = max(len(candidates) // count, 1)
        return candidates[::step][:count]
    return candidates


def _stamp_botanical_tokens(
    mesh: pb.Mesh,
    nodes: list[np.ndarray],
    parents: list[int],
    token: MeshToken,
    rng: np.random.Generator,
    count: int,
    scale_range: tuple[float, float],
    prefer_terminal: bool,
) -> dict:
    centers = getattr(mesh, "center_indices")
    anchors = _select_anchors(nodes, parents, count=count, prefer_terminal=prefer_terminal)
    bridges = 0
    stamps = 0
    for n_i in anchors:
        parent = parents[n_i] if parents[n_i] >= 0 else 0
        direction = v17._unit(np.asarray(nodes[n_i], dtype=float) - np.asarray(nodes[parent], dtype=float))
        if float(np.linalg.norm(direction)) < 1e-8:
            direction = np.array([0.0, 0.0, 1.0])
        scale = float(rng.uniform(*scale_range))
        bridges += _append_token_stamp(mesh, token, centers[n_i], nodes[n_i], direction, scale, float(rng.uniform(0, math.tau)))
        stamps += 1
    return {
        "token_stamp_count": stamps,
        "support_bridge_count": bridges,
        "token_faces_per_stamp": int(len(token.faces)),
    }


def _case_controls(base: dict, token_stats: dict, edges: int, root_hairs: int = 0, root_anchors: int = 0) -> dict:
    controls = dict(base)
    controls.update(
        {
            "same_classical_task_mode": True,
            "real_glb_mesh_token_library": True,
            "oriented_mesh_token_stamping": True,
            "connected_botanical_support_sweep": True,
            "shared_vertex_support_bridge": True,
            "mesh_pbr_output_only": True,
            "procedural_rods_only": False,
            "local_selection_or_postprocess": False,
            "tapered_branch_edges": int(edges),
            "root_hair_count": int(root_hairs),
            "root_token_anchor_count": int(root_anchors),
            **token_stats,
        }
    )
    return controls


def _build_lsystem_pine(seed: int, token: MeshToken) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 1901)
    nodes0, parents = bm.lsystem_case("tree", depth=5, seed=seed)
    nodes = v17._normalize_nodes([np.asarray(p, dtype=float) for p in nodes0], 2.55)
    radii = v17._radii_from_parents(parents, base=0.092, taper=0.76, floor=0.012)
    edges = v17._graph_edges(parents)
    mesh = v17._swept_botanical_support_mesh(nodes, edges, radii, sides=14, ovality=0.25)
    token_stats = _stamp_botanical_tokens(mesh, nodes, parents, token, rng, 24, (0.095, 0.155), True)
    return mesh, _case_controls(
        {
            "source": "baseline_matrix_20260509.lsystem_case(tree)",
            "depth": 5,
            "target_silhouette": "conifer/canopy crown",
        },
        token_stats,
        len(edges),
    )


def _build_lsystem_root(seed: int, token: MeshToken) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 1902)
    nodes0, parents = bm.lsystem_case("root", depth=5, seed=seed)
    nodes = v17._normalize_nodes([np.asarray(p, dtype=float) for p in nodes0], 2.65)
    radii = v17._radii_from_parents(parents, base=0.085, taper=0.84, floor=0.0058)
    depths = bm.graph_depths(parents)
    original = len(nodes)
    for idx in [i for i in range(1, original) if depths[i] >= 2]:
        parent = parents[idx] if parents[idx] >= 0 else 0
        axis = v17._unit(nodes[idx] - nodes[parent])
        u, v, _ = v17._basis(axis)
        for _ in range(3 + int(depths[idx] >= 4)):
            direction = v17._unit(-0.25 * axis + rng.normal(0, 0.85) * u + rng.normal(0, 0.85) * v + np.array([0.0, 0.0, -0.62]))
            v17._append_child(nodes, parents, radii, idx, direction, rng.uniform(0.060, 0.175), rng.uniform(0.0026, 0.0048))
    edges = v17._graph_edges(parents)
    mesh = v17._swept_botanical_support_mesh(nodes, edges, radii, sides=12, ovality=0.36)
    token_stats = _stamp_botanical_tokens(mesh, nodes, parents, token, rng, 30, (0.090, 0.165), True)
    root_hairs = len(nodes) - original
    return mesh, _case_controls(
        {
            "source": "baseline_matrix_20260509.lsystem_case(root)",
            "depth": 5,
            "target_silhouette": "root fan",
        },
        token_stats,
        len(edges),
        root_hairs=root_hairs,
        root_anchors=8,
    )


def _build_lsystem_vine(seed: int, token: MeshToken) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 1903)
    nodes: list[np.ndarray] = [np.zeros(3, dtype=float)]
    parents: list[int] = [-1]
    radii: list[float] = [0.060]
    parent = 0
    for level in range(1, 13):
        theta = level * 0.74
        current = v17._append_child(nodes, parents, radii, parent, np.array([math.cos(theta) * 0.20, math.sin(theta) * 0.20, 0.34]), 1.0, max(0.054 * (0.88**level), 0.009))
        for sign in (-1, 1):
            side = v17._unit(np.array([math.cos(theta + sign * 1.28), math.sin(theta + sign * 1.28), 0.10]))
            tendril = v17._append_child(nodes, parents, radii, current, side + rng.normal(0, 0.035, 3), 0.24 + 0.012 * level, 0.009)
            curl_parent = tendril
            for curl in range(2):
                curl_parent = v17._append_child(nodes, parents, radii, curl_parent, side * (0.55 - 0.12 * curl) + np.array([0.0, 0.0, 0.22]) + rng.normal(0, 0.10, 3), 0.10 + 0.012 * curl, 0.005)
        parent = current
    nodes = v17._normalize_nodes(nodes, 2.45)
    edges = v17._graph_edges(parents)
    mesh = v17._swept_botanical_support_mesh(nodes, edges, radii, sides=12, ovality=0.30)
    token_stats = _stamp_botanical_tokens(mesh, nodes, parents, token, rng, 20, (0.085, 0.140), False)
    return mesh, _case_controls(
        {
            "source": "hand-authored L-system vine equivalent to baseline_matrix_20260509.lsystem_case(vine)",
            "iterations": 6,
            "target_silhouette": "climbing vine",
        },
        token_stats,
        len(edges),
    )


def _build_space_colonization(sc_case: str, seed: int, mode: str, token: MeshToken) -> tuple[pb.Mesh, dict]:
    rng = np.random.default_rng(seed + 1904)
    attractors = 1600 if sc_case != "bush_shell" else 1400
    iterations = 260 if sc_case != "bush_shell" else 230
    result = scb.grow_space_colonization(
        case=sc_case,
        attractor_count=attractors,
        iterations=iterations,
        influence_radius=0.220 if sc_case != "bush_shell" else 0.235,
        kill_radius=0.052 if sc_case != "bush_shell" else 0.060,
        step_size=0.041 if sc_case != "bush_shell" else 0.040,
        seed=seed,
    )
    nodes = v17._normalize_nodes([np.asarray(p, dtype=float) for p in result["nodes"]], 2.48)
    parents = [int(p) for p in result["parents"]]
    radii = v17._radii_from_parents(parents, base=0.080 if mode != "root" else 0.084, taper=0.82, floor=0.0056)
    original = len(nodes)
    depths = bm.graph_depths(parents)
    max_depth = max(depths) if depths else 1
    anchors = [i for i in range(1, original) if depths[i] >= max_depth * 0.50 or i in v17._terminal_nodes(parents)]
    rng.shuffle(anchors)
    root_hairs = 0
    if mode == "root":
        for idx in anchors[:130]:
            parent = parents[idx] if parents[idx] >= 0 else idx
            axis = v17._unit(nodes[idx] - nodes[parent])
            u, v, _ = v17._basis(axis)
            for _ in range(2):
                direction = v17._unit(-0.16 * axis + rng.normal(0, 0.80) * u + rng.normal(0, 0.80) * v + np.array([0.0, 0.0, -0.54]))
                v17._append_child(nodes, parents, radii, idx, direction, rng.uniform(0.054, 0.135), rng.uniform(0.0028, 0.0050))
                root_hairs += 1
    elif mode == "tree":
        for idx in anchors[:80]:
            parent = parents[idx] if parents[idx] >= 0 else idx
            axis = v17._unit(nodes[idx] - nodes[parent])
            v17._append_child(nodes, parents, radii, idx, axis + np.array([0.0, 0.0, 0.20]) + rng.normal(0, 0.20, 3), rng.uniform(0.035, 0.075), 0.006)
    edges = v17._graph_edges(parents)
    mesh = v17._swept_botanical_support_mesh(nodes, edges, radii, sides=12, ovality=0.30)
    token_stats = _stamp_botanical_tokens(mesh, nodes, parents, token, rng, 28 if mode != "root" else 34, (0.075, 0.145), mode != "root")
    return mesh, _case_controls(
        {
            "source": "space_colonization_baseline.grow_space_colonization",
            "case": sc_case,
            "attractor_count": attractors,
            "iterations": iterations,
            "covered_attractors": result.get("covered_attractors"),
            "alive_attractors": result.get("alive_attractors"),
            "target_silhouette": "attractor-driven root/crown/bush shell",
        },
        token_stats,
        len(edges),
        root_hairs=root_hairs,
        root_anchors=7 if mode == "root" else 0,
    )


def _write_guides(out_dir: Path) -> dict[str, str]:
    from PIL import Image, ImageDraw, ImageFilter

    guide_dir = out_dir / "_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)

    def save(name: str, bg: tuple[int, int, int], colors: list[tuple[int, int, int]], motif: str) -> str:
        img = Image.new("RGB", (768, 768), bg)
        draw = ImageDraw.Draw(img)
        rng = np.random.default_rng(sum(name.encode("utf-8")))
        for _ in range(900):
            c = colors[int(rng.integers(0, len(colors)))]
            x, y = int(rng.integers(30, 738)), int(rng.integers(30, 738))
            if motif == "root":
                draw.line((x, y, x + int(rng.normal(0, 95)), y + int(rng.normal(46, 42))), fill=c, width=int(rng.integers(2, 7)))
            elif motif == "vine":
                r = int(rng.integers(14, 58))
                draw.arc((x - r, y - r, x + r, y + r), 10, 330, fill=c, width=int(rng.integers(2, 5)))
            else:
                draw.line((x, y, x + int(rng.normal(0, 58)), y + int(rng.normal(-28, 34))), fill=c, width=int(rng.integers(1, 4)))
                if rng.random() < 0.32:
                    rr = int(rng.integers(4, 16))
                    draw.ellipse((x - rr, y - rr, x + rr, y + rr), fill=c)
        path = guide_dir / name
        img.filter(ImageFilter.SMOOTH_MORE).save(path)
        return str(path)

    return {
        "tree": save("v19_real_mesh_token_pine_crown_pbr_guide.png", (18, 34, 24), [(42, 84, 43), (92, 128, 66), (134, 116, 70), (76, 49, 30)], "tree"),
        "root": save("v19_real_mesh_token_root_pbr_guide.png", (29, 22, 17), [(72, 49, 31), (123, 82, 48), (166, 119, 74), (24, 17, 13)], "root"),
        "vine": save("v19_real_mesh_token_vine_pbr_guide.png", (20, 44, 31), [(45, 96, 48), (93, 136, 68), (136, 104, 52), (55, 36, 24)], "vine"),
    }


def _case_specs(seed: int, tokens: dict[str, MeshToken]) -> list[dict]:
    specs: list[dict] = []

    def add(case_id: str, family: str, target: str, mode: str, mesh: pb.Mesh, controls: dict, token: MeshToken, guide: str, why: str, gpu: int) -> None:
        operators = [
            "same_classical_recursive_mode",
            "real_glb_mesh_token_library",
            "grammar_skeleton_or_attractor_field",
            "oriented_mesh_token_stamping",
            "shared_vertex_support_bridge",
            "connected_botanical_support_sweep",
            "pbr_guide_output_for_trellis2",
            "no_local_selection",
        ]
        specs.append(
            {
                "case_id": case_id,
                "family": family,
                "traditional_target": target,
                "match_target": target,
                "recursive_mode": mode,
                "mesh": mesh,
                "controls": controls,
                "token": token,
                "guide_key": guide,
                "why_matches_traditional": why,
                "strict_match_notes": why,
                "gpu": int(gpu),
                "seed": int(seed + len(specs) + 301),
                "operators": operators,
                "operator_composition": " -> ".join(operators),
                "case_role": "priority_a100_2",
            }
        )

    mesh, controls = _build_lsystem_pine(seed + 1, tokens["tree"])
    add("v19_lsys_pine_canopy_d5_real_meshroot_token_crown", "L-system", "lsys_pine_canopy_d5", "symbolic turtle branch rewriting, depth 5, pine/tree canopy", mesh, controls, tokens["tree"], "tree", "Same depth-5 tree L-system target; V19 stamps real tree GLB mesh tokens onto the grammar skeleton while keeping the conifer/crown silhouette.", 4)

    mesh, controls = _build_lsystem_root(seed + 2, tokens["root"])
    add("v19_lsys_root_fan_d5_real_meshroot_token_fan", "L-system", "lsys_root_fan_d5", "symbolic turtle root branching with downward tropism, depth 5", mesh, controls, tokens["root"], "root", "Same depth-5 root/tropism grammar; V19 uses real pruned-root GLB mesh tokens plus connected rootlet support, not rods/cards only.", 5)

    mesh, controls = _build_lsystem_vine(seed + 3, tokens["vine"])
    add("v19_lsys_climbing_vine_d6_real_meshroot_token_curl", "L-system", "lsys_climbing_vine_d6", "curling main chain with recursive tendrils, six iterations", mesh, controls, tokens["vine"], "vine", "Same six-step climbing vine mode; V19 composes real vine GLB mesh tokens along tendril/curl anchors.", 6)

    mesh, controls = _build_space_colonization("tree_canopy", seed + 11, "tree", tokens["tree"])
    add("v19_sc_tree_crown_260_real_meshroot_token_attractor_crown", "Space colonization", "sc_tree_crown_260", "tree crown attractor competition with influence/kill radii", mesh, controls, tokens["tree"], "tree", "Same SC tree-crown attractor mode; V19 stamps real tree GLB token surfaces onto attractor-driven branches.", 4)

    mesh, controls = _build_space_colonization("root_vine", seed + 12, "root", tokens["meshroot_vine"])
    add("v19_sc_root_network_260_real_meshroot_token_root_web", "Space colonization", "sc_root_network_260", "root/vine attractor competition in below-ground volume", mesh, controls, tokens["meshroot_vine"], "root", "Same SC root-network attractor field; V19 uses the meshspace genroot vine GLB token for high-quality root-web surface detail.", 5)

    mesh, controls = _build_space_colonization("bush_shell", seed + 13, "tree", tokens["tree"])
    add("v19_sc_bush_shell_220_real_meshroot_token_leaf_shell", "Space colonization", "sc_bush_shell_220", "bush-shell attractor competition with outward terminal coverage", mesh, controls, tokens["tree"], "tree", "Same SC bush-shell attractor coverage; V19 preserves the shell silhouette and stamps real tree/canopy mesh tokens.", 7)
    return specs


def _export_mesh(path: Path, mesh: pb.Mesh) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pb.write_obj(path, mesh)


def _mesh_stats(path: Path, controls: dict) -> dict:
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
        "token_stamp_count": int(controls.get("token_stamp_count", 0)),
        "support_bridge_count": int(controls.get("support_bridge_count", 0)),
        "token_faces_per_stamp": int(controls.get("token_faces_per_stamp", 0)),
        "root_hair_count": int(controls.get("root_hair_count", 0)),
        "root_token_anchor_count": int(controls.get("root_token_anchor_count", 0)),
    }


def _metadata_for(spec: dict, mesh_path: Path, guide_path: str, metrics: dict, tokens: dict[str, MeshToken]) -> dict:
    token = spec["token"]
    source_glbs = [t.source for t in tokens.values()]
    positive = "real GLB mesh tokens on a connected botanical support while preserving the classical silhouette"
    if "root" in spec["traditional_target"]:
        positive += " and root fan/root-web behavior"
    return {
        "case_id": spec["case_id"],
        "family": spec["family"],
        "match_target": spec["match_target"],
        "traditional_target": spec["traditional_target"],
        "traditional_alignment": {
            "traditional_target": spec["traditional_target"],
            "same_category": True,
            "same_recursive_mode": spec["recursive_mode"],
            "strict_one_to_one_comparison": True,
            "control_parameters": spec["controls"],
            "why_strict_one_to_one": spec["why_matches_traditional"],
        },
        "recursive_mode": spec["recursive_mode"],
        "remote_target": REMOTE_TARGET,
        "remote_constraints": {
            "machine": REMOTE_TARGET,
            "allowed_gpus": ALLOWED_GPUS,
            "storage_root": REMOTE_STORAGE_ROOT,
            "storage_limit_gb": STORAGE_LIMIT_GB,
        },
        "mesh_path": str(mesh_path),
        "guide_image": guide_path,
        "seed": spec["seed"],
        "operators": spec["operators"],
        "operator_composition": spec["operator_composition"],
        "controls": spec["controls"],
        "initial_mesh_metrics": metrics,
        "why_matches_traditional": spec["why_matches_traditional"],
        "strict_match_notes": spec["strict_match_notes"],
        "case_role": spec["case_role"],
        "strict_generation_policy": "generate_new_on_a100_2_no_local_selection_or_postprocessing",
        "mesh_pbr_contract": {
            "obj_input_required": True,
            "pbr_guide_required": True,
            "pbr_textured_glb_required": True,
            "forbidden_outputs": ["local_selected_render", "2d_only_image", "procedural_rods_only"],
        },
        "mesh_token_provenance": {
            "source_type": "tiny_procedural_fallback" if token.fallback_used else "real_project_glb",
            "fallback_used": bool(token.fallback_used),
            "active_token": token.name,
            "active_token_source": token.source,
            "source_glbs": source_glbs,
            "token_original_vertices": token.original_vertices,
            "token_original_faces": token.original_faces,
            "token_faces_per_stamp": int(len(token.faces)),
            "composition_rule": "normalize real GLB token, orient local z-axis to grammar edge, stamp at skeleton/attractor anchors, bridge every token face to a shared support vertex",
        },
        "root_selection_log": {
            "root_source_type": "v19_real_glb_mesh_token_botanical_generator",
            "source_generator": "assets/strict_visual_matched_cases_V19_meshroot_botanical_20260510.py",
            "source_glbs": source_glbs,
            "root_screening_budget": "no local manual cherry-pick and no posthoc repair selection; final outputs generated fresh on a100-2",
        },
        "visual_readability_contract": {
            "dryrun_visual_floor": "single main component or largest-component vertex ratio above 0.999 before Trellis2",
            "positive_constraint": positive,
            "negative_constraint": "no rod/card-only mesh, no loose semantic replacement, no local postprocess substitution, no detached token islands",
            "failure_addressed": "V17 improved connectivity but still relied heavily on procedural rods/cards; V19 composes actual high-quality project GLB mesh tokens.",
            "no_local_selection": "strict cases must be generated fresh on a100-2; local dry-run files are inputs, not selected final outputs",
        },
    }


def _write_readme(out_dir: Path, summary: dict) -> None:
    text = f"""# V19 Meshroot Botanical Strict Visual-Matched Cases Dry Run

Produced by `assets/strict_visual_matched_cases_V19_meshroot_botanical_20260510.py`.

This is an input batch only. It does not launch remote jobs, locally select
outputs, or post-process prior assets. Final strict one-to-one cases must be
generated fresh on `{REMOTE_TARGET}` with GPU ids `{ALLOWED_GPUS}` under:

`{REMOTE_STORAGE_ROOT}`

Connectivity gate: largest-component vertex ratio >= `{CONNECTIVITY_LCR_MIN}`
before Trellis2.

Case count: {summary["num_cases"]}
"""
    (out_dir / "README.md").write_text(text, encoding="utf-8")


def materialize(root: Path, out_dir: Path, seed: int = 20260510, case_limit: int | None = None, use_tiny_fallback: bool = False) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    tokens = load_token_library(root, seed=seed, use_tiny_fallback=use_tiny_fallback)
    guides = _write_guides(out_dir)
    specs = _case_specs(seed, tokens)
    if case_limit is not None:
        specs = specs[: int(case_limit)]

    rows: list[dict] = []
    metrics_rows: list[dict] = []
    for spec in specs:
        case_dir = out_dir / spec["case_id"]
        mesh_path = case_dir / f"{spec['case_id']}.obj"
        _export_mesh(mesh_path, spec["mesh"])
        guide_path = guides[spec["guide_key"]]
        metrics = _mesh_stats(mesh_path, spec["controls"])
        if metrics["mesh_component_count"] != 1 and metrics["largest_mesh_component_vertex_ratio"] < CONNECTIVITY_LCR_MIN:
            raise RuntimeError(f"{spec['case_id']} failed V19 connectivity gate: {metrics}")
        metadata = _metadata_for(spec, mesh_path, guide_path, metrics, tokens)
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
            "gpu_group": spec["gpu"],
            "seed": spec["seed"],
            "operators": json.dumps(spec["operators"], ensure_ascii=False),
            "operator_composition": spec["operator_composition"],
            "controls": json.dumps(spec["controls"], ensure_ascii=False, sort_keys=True),
            "why_matches_traditional": spec["why_matches_traditional"],
            "strict_match_notes": spec["strict_match_notes"],
            "case_role": spec["case_role"],
            "strict_one_to_one": "true",
            "generation_policy": "generate_new_on_a100_2_no_local_selection_or_postprocessing",
            "mesh_token_source": "tiny_procedural_fallback" if spec["token"].fallback_used else "real_project_glb",
            "storage_root": REMOTE_STORAGE_ROOT,
            "storage_limit_gb": STORAGE_LIMIT_GB,
        }
        rows.append(row)
        metrics_rows.append({"case_id": spec["case_id"], "match_target": spec["match_target"], "traditional_target": spec["traditional_target"], **metrics})

    manifest_fields = [
        "case_id",
        "family",
        "match_target",
        "traditional_target",
        "recursive_mode",
        "mesh_path",
        "guide_image",
        "metadata_path",
        "remote_target",
        "gpu_group",
        "seed",
        "operators",
        "operator_composition",
        "controls",
        "why_matches_traditional",
        "strict_match_notes",
        "case_role",
        "strict_one_to_one",
        "generation_policy",
        "mesh_token_source",
        "storage_root",
        "storage_limit_gb",
    ]
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    metric_fields = [
        "case_id",
        "match_target",
        "traditional_target",
        "vertices",
        "faces",
        "mesh_component_count",
        "largest_mesh_component_vertex_ratio",
        "bbox_extent",
        "bbox_diag",
        "surface_area",
        "token_stamp_count",
        "support_bridge_count",
        "token_faces_per_stamp",
        "root_hair_count",
        "root_token_anchor_count",
    ]
    with (out_dir / "initial_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        writer.writerows(metrics_rows)
    (out_dir / "initial_metrics.json").write_text(json.dumps(metrics_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    case_lines = [f"{row['case_id']}|{row['mesh_path']}|{row['guide_image']}|{row['seed']}|{row['gpu_group']}" for row in rows]
    (out_dir / "a100-2_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    (out_dir / "gpu4567_cases.txt").write_text("\n".join(case_lines) + ("\n" if case_lines else ""), encoding="utf-8")
    for gpu in ALLOWED_GPUS:
        selected = [line for line, row in zip(case_lines, rows) if int(row["gpu_group"]) == gpu]
        (out_dir / f"gpu{gpu}_cases.txt").write_text("\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")

    summary = {
        "out_dir": str(out_dir),
        "num_cases": len(rows),
        "remote_target": REMOTE_TARGET,
        "allowed_gpus": ALLOWED_GPUS,
        "storage_root": REMOTE_STORAGE_ROOT,
        "storage_limit_gb": STORAGE_LIMIT_GB,
        "surface_generator": "real_glb_mesh_token_botanical_grammar_v19",
        "mesh_token_policy": "production_real_project_glbs_with_explicit_tiny_fallback",
        "mesh_pbr_policy": "obj_inputs_and_pbr_guides_for_trellis2_glb_export",
        "connectivity_gate": {
            "largest_component_vertex_ratio_min": CONNECTIVITY_LCR_MIN,
            "pre_trellis_required": True,
        },
        "manifest": str(out_dir / "manifest.csv"),
        "initial_metrics": str(out_dir / "initial_metrics.csv"),
        "priority_cases": [row["case_id"] for row in rows if row["case_role"] == "priority_a100_2"],
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_readme(out_dir, summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("RGG_ROOT", ROOT_DIR)))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20260510)
    parser.add_argument("--case-limit", type=int, default=None)
    parser.add_argument("--use-tiny-fallback", action="store_true")
    args = parser.parse_args()
    materialize(args.root, args.out, seed=args.seed, case_limit=args.case_limit, use_tiny_fallback=args.use_tiny_fallback)


if __name__ == "__main__":
    main()
