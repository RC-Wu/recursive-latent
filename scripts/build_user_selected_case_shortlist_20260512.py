#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
OUT = ROOT / "docs" / "evaluation" / "user_selected_case_shortlist_20260512"
REMOTE_LIST = ROOT / "docs" / "evaluation" / "case_inventory_v1_v60_20260512" / "remote_a1002_v1_v60_files.txt"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
GEOM_EXTS = {".glb", ".obj"}
SPEC_EXTS = {".json", ".md", ".py", ".sh", ".yaml", ".yml", ".csv"}


@dataclass
class CaseSpec:
    key: str
    title: str
    version: str
    family: str
    user_note: str
    image_rel: str
    case_ids: list[str]
    kind: str = "single"
    sheet_target: str = ""
    status: str = "candidate"
    extra_notes: list[str] = field(default_factory=list)


CASES: list[CaseSpec] = [
    CaseSpec(
        "v8_dla_frontier_open_boundary_seed_b",
        "V8 DLA frontier open boundary seed B",
        "V8",
        "DLA / coral",
        "作为珊瑚的case似乎还不错。",
        "visuals/strict_visual_matched_texture_v8_frontier_refine_zoom_20260510/v8_dla_frontier_open_boundary_seed_b/strict_matched_zoom_comparison.png",
        ["v8_dla_frontier_open_boundary_seed_b"],
    ),
    CaseSpec(
        "v9_dla_coral_porous_table_ridge",
        "V9 DLA coral porous table ridge",
        "V9",
        "DLA / seaweed-like coral",
        "作为海草的case还可以。",
        "visuals/strict_visual_matched_texture_v9_organic_frontier_zoom_20260510/v9_dla_coral_porous_table_ridge/zoom_01.png",
        ["v9_dla_coral_porous_table_ridge"],
    ),
    CaseSpec(
        "v10_dla_staghorn_coral_branching_b",
        "V10 DLA staghorn coral branching B",
        "V10",
        "DLA / staghorn coral",
        "对应的case也留下来备选。",
        "visuals/strict_visual_matched_texture_v10_readable_coral_frontier_zoom_20260510/v10_dla_staghorn_coral_branching_b/overview_raw.png",
        ["v10_dla_staghorn_coral_branching_b"],
    ),
    CaseSpec(
        "v13_dla_smooth_coral_staghorn_b",
        "V13 DLA smooth coral staghorn B",
        "V13",
        "DLA / staghorn coral",
        "感觉还行。",
        "visuals/strict_visual_matched_texture_v13_smooth_coral_crystal_zoom_20260510/v13_dla_smooth_coral_staghorn_b/strict_matched_zoom_comparison.png",
        ["v13_dla_smooth_coral_staghorn_b"],
    ),
    CaseSpec(
        "v13_dla_smooth_table_coral_b",
        "V13 DLA smooth table coral B",
        "V13",
        "DLA / table coral",
        "感觉还行。",
        "visuals/strict_visual_matched_texture_v13_smooth_coral_crystal_zoom_20260510/v13_dla_smooth_table_coral_b/strict_matched_zoom_comparison.png",
        ["v13_dla_smooth_table_coral_b"],
    ),
    CaseSpec(
        "v14_dla_branching_staghorn_a",
        "V14 DLA branching staghorn A",
        "V14",
        "DLA / staghorn coral",
        "感觉也还可以。",
        "visuals/strict_visual_matched_texture_v14_branching_coral_zoom_20260510/v14_dla_branching_staghorn_a/strict_matched_zoom_comparison.png",
        ["v14_dla_branching_staghorn_a"],
    ),
    CaseSpec(
        "v15_ifs_lattice_crystal_d4_small_bridge_facets",
        "V15 IFS lattice crystal d4 small bridge facets",
        "V15",
        "IFS / lattice crystal",
        "这张图还不错。",
        "visuals/strict_visual_matched_texture_v15_plants_ifs_seed20281700_zoom_20260510/v15_ifs_lattice_crystal_d4_small_bridge_facets/strict_matched_zoom_comparison.png",
        ["v15_ifs_lattice_crystal_d4_small_bridge_facets"],
    ),
    CaseSpec(
        "v15_lsys_climbing_vine_d6_smooth_leafy_curl",
        "V15 L-system climbing vine d6 smooth leafy curl",
        "V15",
        "L-system / vine",
        "代表图里 main 第四行这个 case 还不错。",
        "docs/evaluation/case_inventory_v1_v60_20260512/representative_images/V15_strict_visual_matched_texture_v15_plants_ifs_zoom_20260510.png",
        ["v15_lsys_climbing_vine_d6_smooth_leafy_curl"],
        kind="sheet-row",
        sheet_target="Sheet 第四行: v15_lsys_climbing_vine_d6_smooth_leafy_curl",
    ),
    CaseSpec(
        "v16_dla_natural_staghorn_b",
        "V16 DLA natural staghorn B",
        "V16",
        "DLA / staghorn coral",
        "这张图还可以。",
        "visuals/strict_visual_matched_texture_v16_natural_coral_seed20280300_zoom_20260510/v16_dla_natural_staghorn_b/strict_matched_zoom_comparison.png",
        ["v16_dla_natural_staghorn_b"],
    ),
    CaseSpec(
        "v19_lsys_root_fan_d5_real_meshroot_token_fan",
        "V19 L-system root fan real meshroot token fan",
        "V19",
        "L-system / root fan",
        "勉强还行。",
        "visuals/strict_visual_matched_texture_V19_meshroot_botanical_zoom_20260510/v19_lsys_root_fan_d5_real_meshroot_token_fan/zoom_02.png",
        ["v19_lsys_root_fan_d5_real_meshroot_token_fan"],
    ),
    CaseSpec(
        "v21_ifs_radial_ornament_o12_d5_burnished",
        "V21 IFS radial ornament o12 d5 burnished",
        "V21",
        "IFS / radial ornament",
        "这张图还可以。",
        "visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_zoom_20260510/V21_ifs_radial_ornament_o12_d5_burnished_steps8_tex2048_seed20295802_xformers/strict_matched_zoom_comparison.png",
        ["V21_ifs_radial_ornament_o12_d5_burnished", "V21_ifs_radial_ornament_o12_d5_burnished_steps8_tex2048_seed20295802_xformers"],
    ),
    CaseSpec(
        "v24_dla_staghorn_frontier_seed3_sheet_row2",
        "V24 DLA staghorn frontier, seed3 sheet row 2",
        "V24",
        "DLA / staghorn frontier",
        "contact sheet 第二行这个 case 还行。",
        "visuals/strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510/strict_visual_matched_texture_V24_priority_rerun_seed3_contact_sheet.png",
        ["V24_dla_staghorn_frontier", "V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA"],
        kind="sheet-row",
        sheet_target="Sheet 第二行: V24_dla_staghorn_frontier",
        extra_notes=["短标签 `V24_dla_staghorn_frontier` 对应真实 case id `V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA`。"],
    ),
    CaseSpec(
        "tree_v25_bud_d1_spiky_controlled_cedar",
        "V25 controlled cedar bud d1 spiky",
        "V25",
        "Space colonization / tree crown",
        "待定，或许表面能修或者能 naturalized。",
        "visuals/publication_repair_20260510f_controlled_zoom_1200/tree_v25_bud_d1_spiky_controlled_cedar/strict_matched_zoom_comparison.png",
        ["tree_v25_bud_d1_spiky_controlled_cedar", "tree_v25_bud_d1_spiky_pruned"],
        status="pending repair",
        extra_notes=["展示标签 controlled_cedar 的渲染 plan 指向真实 GLB case `tree_v25_bud_d1_spiky_pruned_steps8_tex2048_seed202605601_xformers`。"],
    ),
    CaseSpec(
        "v26_sc_tree_seam_naturalization_dryrun_sheet",
        "V26 SC tree seam naturalization dryrun sheet",
        "V26",
        "Space colonization / tree crown",
        "待定。",
        "visuals/strict_visual_matched_cases_V26_sc_tree_seam_naturalization_20260511_dryrun_contact.png",
        [
            "V26_sc_tree_crown_junction_collar_A_lowcontrast",
            "V26_sc_tree_crown_leafshield_B_lowcontrast",
            "V26_sc_tree_crown_cambium_sleeve_C_lowcontrast",
            "V26_sc_tree_crown_soft_canopy_D_lowcontrast",
        ],
        kind="sheet",
        status="pending",
    ),
    CaseSpec(
        "v26_sc_tree_seam_naturalization_object_pbr_sheet",
        "V26 SC tree seam naturalization object PBR sheet",
        "V26",
        "Space colonization / tree crown",
        "待定。",
        "visuals/strict_visual_matched_texture_V26_sc_tree_seam_naturalization_object_pbr_20260511/V26_sc_tree_seam_naturalization_object_pbr_contact_sheet_20260511.png",
        [
            "V26_sc_tree_crown_junction_collar_A_lowcontrast",
            "V26_sc_tree_crown_leafshield_B_lowcontrast",
            "V26_sc_tree_crown_cambium_sleeve_C_lowcontrast",
            "V26_sc_tree_crown_soft_canopy_D_lowcontrast",
        ],
        kind="sheet",
        status="pending",
    ),
    CaseSpec(
        "v27_sc_tree_organic_seam_sheet",
        "V27 SC tree organic seam sheet",
        "V27",
        "Space colonization / tree crown",
        "这个 case 质量非常好，进入头图候选。",
        "visuals/strict_visual_matched_cases_V27_sc_tree_organic_seam_obj_zoom_seamtarget_20260511/V27_sc_tree_organic_seam_obj_seamtarget_contact_sheet_20260511.png",
        [
            "V27_sc_tree_organic_feather_A",
            "V27_sc_tree_terminal_bud_B",
            "V27_sc_tree_bark_leaf_C",
            "V27_sc_tree_soft_canopy_D",
        ],
        kind="sheet",
        status="hero candidate",
    ),
    CaseSpec(
        "v29_glb_softleaf_entry_d",
        "V29 GLB softleaf entry D seamtarget",
        "V29",
        "Space colonization / tree crown texture",
        "着色方案可能比较不错。",
        "visuals/strict_visual_matched_texture_V29_sc_tree_hidden_trunk_naturalization_zoom_white_seamtarget_20260511/V29_glb_softleaf_entry_D_seamtarget/strict_matched_zoom_comparison.png",
        ["V29_glb_softleaf_entry_D", "V29_sc_tree_hidden_trunk_naturalization"],
    ),
    CaseSpec(
        "v35_lsystem_branch_tapered_naturalization_sheet",
        "V35 L-system branch tapered naturalization sheet",
        "V35",
        "L-system / branch",
        "可能可以作为补充视觉材料；需要说明几个不同 case 控制了什么变量或超参数。",
        "visuals/strict_visual_matched_texture_V35_lsystem_branch_tapered_naturalization_zoom_white_junctiontarget_20260511/V35_lsystem_branch_tapered_naturalization_contact_sheet_20260511.png",
        [
            "V35_lsys_branch_tapered_bud_A",
            "V35_lsys_branch_bark_sleeve_B",
            "V35_lsys_branch_fused_fork_C",
            "V35_lsys_branch_lowfrag_taper_D",
        ],
        kind="sheet",
    ),
    CaseSpec(
        "v37_lsystem_branch_continuous_saddle_sheet",
        "V37 L-system branch continuous saddle sheet",
        "V37",
        "L-system / branch",
        "这组 case 也是，需要说明变量或超参数。",
        "docs/evaluation/case_inventory_v1_v60_20260512/representative_images/V37_strict_visual_matched_cases_V37_lsystem_branch_obj_zoom_junctiontarget_20260511.png",
        [
            "V37_lsys_branch_saddle_fork_A",
            "V37_lsys_branch_midfork_B",
            "V37_lsys_branch_densefork_C",
            "V37_lsys_branch_slim_taper_D",
        ],
        kind="sheet",
    ),
    CaseSpec(
        "v40_lsystem_branch_primary_fork_sheet",
        "V40 L-system branch primary fork sheet",
        "V40",
        "L-system / branch",
        "这组相当不错，可以用来和传统方法比较。",
        "docs/evaluation/case_inventory_v1_v60_20260512/representative_images/V40_strict_visual_matched_texture_V40_lsystem_branch_primary_fork_zoom_white_2026051.png",
        [
            "V40_lsys_branch_primary_fork_A",
            "V40_lsys_branch_primary_fork_lowfrag_B",
            "V40_lsys_branch_primary_fork_dense_C",
            "V40_lsys_branch_primary_fork_slim_D",
        ],
        kind="sheet",
    ),
    CaseSpec(
        "v41_lsys_branch_dense_fork_lowfrag_b",
        "V41 L-system branch dense fork lowfrag B",
        "V41",
        "L-system / branch",
        "更密集些，可能更适合比较。",
        "visuals/strict_visual_matched_texture_V41_lsystem_branch_dense_fork_zoom_white_20260511/V41_lsys_branch_dense_fork_lowfrag_B_glb_junctiontarget/overview_raw.png",
        ["V41_lsys_branch_dense_fork_lowfrag_B"],
    ),
    CaseSpec(
        "v47_lsys_branch_shared_neck_yfork_dense_c",
        "V47 L-system shared-neck Y-fork dense C",
        "V47",
        "L-system / branch",
        "质量很不错；问题是还能多分叉吗？现在 depth 有点太少。",
        "visuals/strict_visual_matched_cases_V47_lsystem_branch_obj_zoom_sharedneckyfork_20260511/V47_lsys_branch_shared_neck_yfork_dense_C_obj_junctiontarget/strict_matched_zoom_comparison.png",
        ["V47_lsys_branch_shared_neck_yfork_dense_C"],
        status="needs higher depth/density",
    ),
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_remote_lines() -> list[str]:
    if REMOTE_LIST.exists():
        return REMOTE_LIST.read_text(errors="ignore").splitlines()
    return []


def all_files() -> list[Path]:
    roots = ["results", "visuals", "assets", "tests", "docs"]
    out: list[Path] = []
    for r in roots:
        root = ROOT / r
        if not root.exists():
            continue
        out.extend([p for p in root.rglob("*") if p.is_file()])
    return out


def score_path(path: Path) -> tuple[int, int, str]:
    s = str(path).lower()
    score = 0
    if path.suffix.lower() == ".glb":
        score += 500
    if path.suffix.lower() == ".obj":
        score += 250
    if "textured.glb" in s:
        score += 400
    if "summary.json" in s:
        score += 350
    if "pipeline.json" in s:
        score += 320
    if "manifest.json" in s:
        score += 280
    if "metadata.json" in s:
        score += 260
    if "dryrun" in s:
        score += 20
    if "traditional" in s or "baseline" in s:
        score -= 600
    if "remote" in s:
        score += 10
    return (-score, len(str(path)), str(path))


def find_hits(files: list[Path], case_ids: list[str]) -> list[Path]:
    hits: list[Path] = []
    lows = [c.lower() for c in case_ids]
    for p in files:
        s = str(p).lower()
        if any(c in s for c in lows):
            hits.append(p)
    return sorted(dict.fromkeys(hits), key=score_path)


def find_remote(remote_lines: list[str], case_ids: list[str]) -> list[str]:
    lows = [c.lower() for c in case_ids]
    return sorted({line for line in remote_lines if any(c in line.lower() for c in lows)})


def is_ours(files: list[Path], spec: CaseSpec, local_hits: list[Path]) -> tuple[bool, str]:
    s = "\n".join(str(p).lower() for p in local_hits)
    if "traditional" in s or "baseline" in s:
        return False, "包含 traditional/baseline 命中，需要人工复核。"
    if (
        "strict_visual_matched" in s
        or "publication_repair" in s
        or "recursive" in s
        or any(cid.lower().startswith(("v", "tree_v25")) for cid in spec.case_ids)
    ):
        return True, "命中 strict_visual_matched/publication_repair/recursive 结果，未命中 traditional/baseline 路径。"
    return False, "未找到足够方法侧元数据，需人工复核。"


def summarize_metadata(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    controls = data.get("controls") if isinstance(data.get("controls"), dict) else {}
    root_log = data.get("root_selection_log") if isinstance(data.get("root_selection_log"), dict) else {}
    grammar = data.get("grammar_mapping") if isinstance(data.get("grammar_mapping"), dict) else {}
    metrics = data.get("initial_mesh_metrics") if isinstance(data.get("initial_mesh_metrics"), dict) else {}
    return {
        "family": data.get("family"),
        "recursive_mode": data.get("recursive_mode"),
        "match_target": data.get("match_target"),
        "seed": data.get("seed"),
        "mesh_path": data.get("mesh_path"),
        "guide_image": data.get("guide_image"),
        "source_generator": root_log.get("source_generator"),
        "root_variant": root_log.get("root_variant"),
        "parameter_variant": root_log.get("parameter_variant"),
        "recursive_depth": (grammar.get("control_lock") or {}).get("recursive_depth"),
        "visible_depth": (data.get("family_diagnostics") or {}).get("visible_depth") if isinstance(data.get("family_diagnostics"), dict) else None,
        "branch_junction_count": controls.get("branch_junction_count"),
        "junction_anchor_count": controls.get("junction_anchor_count"),
        "junction_collar_count": controls.get("junction_collar_count"),
        "terminal_sleeve_count": controls.get("terminal_sleeve_count"),
        "ridge_count": controls.get("ridge_count"),
        "double_sided_side_branches": controls.get("double_sided_side_branches"),
        "mesh_component_count": metrics.get("mesh_component_count"),
        "largest_component_vertex_ratio": metrics.get("largest_mesh_component_vertex_ratio"),
        "operator_composition": data.get("operator_composition"),
        "rerun_reason": data.get("rerun_reason"),
    }


def variant_notes(record: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    key = record["key"]
    if key.startswith("v35_"):
        notes.append("V35 variants control side-branch naturalization under the same L-system branch target: A=tapered bud/cambium guide, B=bark sleeve/ridge guide with fewer side branches, C=fused fork/olive guide with dense recursive junctions, D=low-fragment taper/conservative terminal treatment.")
    if key.startswith("v37_"):
        notes.append("V37 variants replace abrupt tube insertion with continuous saddle-neck junctions: A=saddle fork, B=midfork, C=densefork, D=slim taper. Main controls include side depth, double-sided side branches, max segment length, terminal shrink, collar/ridge/sleeve counts, and guide image.")
    if key.startswith("v40_"):
        notes.append("V40 is the primary-fork naturalization family; A/B/C/D trade density and fragmentation, with dense_C usually the strongest structural comparison candidate and lowfrag_B safer visually.")
    if key.startswith("v47_"):
        notes.append("V47 dense_C uses visible_depth=9 and branch_junction_count=4 in metadata. It can be made more branched by increasing side_depth/main shared-neck anchors and branch_junction_count, but this risks reintroducing V41/V42-style thin fragmented leaf/needle artifacts after GLB texturing.")
    return notes


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    thumb_dir = OUT / "images"
    if thumb_dir.exists():
        shutil.rmtree(thumb_dir)
    thumb_dir.mkdir(parents=True, exist_ok=True)

    files = all_files()
    remote = load_remote_lines()
    records: list[dict[str, Any]] = []
    for idx, spec in enumerate(CASES, start=1):
        image_abs = ROOT / spec.image_rel
        local_hits = find_hits(files, spec.case_ids)
        remote_hits = find_remote(remote, spec.case_ids)
        geometry = [rel(p) for p in local_hits if p.suffix.lower() in GEOM_EXTS]
        glbs = [p for p in geometry if p.lower().endswith(".glb")]
        objs = [p for p in geometry if p.lower().endswith(".obj")]
        metadata_paths = [p for p in local_hits if p.name.endswith("_metadata.json")]
        spec_paths = [rel(p) for p in local_hits if p.suffix.lower() in SPEC_EXTS and p.suffix.lower() not in {".obj", ".glb"}]
        image_hits = [rel(p) for p in local_hits if p.suffix.lower() in IMAGE_EXTS]
        copied_image = ""
        if image_abs.exists() and image_abs.suffix.lower() in IMAGE_EXTS:
            dst = thumb_dir / f"{idx:02d}_{spec.key}{image_abs.suffix.lower()}"
            shutil.copy2(image_abs, dst)
            copied_image = str(dst)
        ours, ours_reason = is_ours(files, spec, local_hits)
        metadata_summaries = [summarize_metadata(p) for p in metadata_paths[:8]]
        record = {
            "index": idx,
            "key": spec.key,
            "title": spec.title,
            "version": spec.version,
            "family": spec.family,
            "kind": spec.kind,
            "status": spec.status,
            "sheet_target": spec.sheet_target,
            "user_note": spec.user_note,
            "image_rel": spec.image_rel,
            "image_abs": str(image_abs),
            "image_exists": image_abs.exists(),
            "copied_image": copied_image,
            "case_ids": spec.case_ids,
            "local_hit_count": len(local_hits),
            "remote_hit_count": len(remote_hits),
            "is_ours_method": ours,
            "ours_reason": ours_reason,
            "has_local_glb": bool(glbs),
            "has_local_obj": bool(objs),
            "local_glb_paths": glbs[:20],
            "local_obj_paths": objs[:20],
            "metadata_paths": [rel(p) for p in metadata_paths[:20]],
            "metadata_summaries": metadata_summaries,
            "spec_or_repro_paths": spec_paths[:40],
            "image_hit_paths": image_hits[:30],
            "remote_paths": remote_hits[:40],
            "notes": spec.extra_notes + variant_notes({"key": spec.key}),
        }
        if not glbs:
            record["notes"].append("本地未找到 textured GLB；若只有 OBJ，则需要后续 texturing/export 或去远端确认是否已生成。")
        if not geometry:
            record["notes"].append("本地未找到 GLB/OBJ 几何路径。")
        if not spec_paths and not metadata_paths:
            record["notes"].append("本地未找到 manifest/summary/metadata/script 复现信息。")
        records.append(record)

    (OUT / "user_selected_case_shortlist_20260512.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    md: list[str] = []
    md.append("# User selected case shortlist 20260512\n\n")
    md.append("本清单整理用户在 V1-V60 gallery 中点名的候选 case，保留原始批注，并定位本地图像、GLB/OBJ、metadata/manifest/summary/pipeline/脚本、远端 a100-2 路径样本。`is_ours_method` 只基于路径和元数据判定；未发现 traditional/baseline 命中时标记为 ours。\n\n")
    md.append(f"- HTML: `{OUT / 'user_selected_case_shortlist_20260512.html'}`\n")
    md.append(f"- JSON: `{OUT / 'user_selected_case_shortlist_20260512.json'}`\n")
    md.append(f"- 图片副本: `{thumb_dir}`\n\n")
    for r in records:
        md.append(f"## {r['index']:02d}. {r['title']}\n\n")
        if r["copied_image"]:
            md.append(f"![{r['key']}]({r['copied_image']})\n\n")
        md.append(f"- 用户批注: {r['user_note']}\n")
        if r["sheet_target"]:
            md.append(f"- Sheet 指定区域: {r['sheet_target']}\n")
        md.append(f"- 方法归属: {'ours' if r['is_ours_method'] else 'needs review'}; {r['ours_reason']}\n")
        md.append(f"- 本地 GLB: {len(r['local_glb_paths'])}; 本地 OBJ: {len(r['local_obj_paths'])}; metadata/spec: {len(r['spec_or_repro_paths'])}; remote hits: {r['remote_hit_count']}\n")
        if r["local_glb_paths"]:
            md.append("- GLB:\n")
            for p in r["local_glb_paths"][:8]:
                md.append(f"  - `{p}`\n")
        if r["local_obj_paths"]:
            md.append("- OBJ:\n")
            for p in r["local_obj_paths"][:8]:
                md.append(f"  - `{p}`\n")
        if r["metadata_paths"]:
            md.append("- Metadata:\n")
            for p in r["metadata_paths"][:8]:
                md.append(f"  - `{p}`\n")
        if r["spec_or_repro_paths"]:
            md.append("- Spec/repro:\n")
            for p in r["spec_or_repro_paths"][:10]:
                md.append(f"  - `{p}`\n")
        if r["notes"]:
            md.append("- Notes:\n")
            for n in r["notes"]:
                md.append(f"  - {n}\n")
        md.append("\n")
    (OUT / "user_selected_case_shortlist_20260512.md").write_text("".join(md), encoding="utf-8")

    css = """
    body{font-family:Arial,sans-serif;margin:20px;color:#111;background:#fafafa}
    nav{position:sticky;top:0;background:#fff;border-bottom:1px solid #ddd;padding:10px;z-index:1}
    a{color:#0645ad}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(520px,1fr));gap:18px}
    .card{background:#fff;border:1px solid #ddd;border-radius:6px;padding:14px;box-shadow:0 1px 2px #ddd}
    .hero{width:100%;max-height:500px;object-fit:contain;background:white;border:1px solid #eee}
    .meta{font-size:13px;color:#444}.path{font-family:Menlo,Consolas,monospace;font-size:11px;word-break:break-all;color:#222}
    .ok{color:#0a6b2b;font-weight:bold}.warn{color:#a15c00;font-weight:bold}.bad{color:#a00000;font-weight:bold}
    details{margin-top:8px}.note{background:#fff7df;border-left:4px solid #d79b00;padding:6px 8px;margin:6px 0}
    h1{margin-bottom:6px}h2{margin-bottom:4px}
    """
    html_parts: list[str] = []
    html_parts.append("<!doctype html><meta charset='utf-8'><title>User selected case shortlist 20260512</title>")
    html_parts.append(f"<style>{css}</style>")
    html_parts.append("<h1>User selected case shortlist 20260512</h1>")
    html_parts.append("<p class='meta'>用户点名候选 case 的可用性、GLB/OBJ、复现元数据与原始批注。图片为本地副本，路径区保留原始位置。</p>")
    html_parts.append("<nav>")
    for r in records:
        html_parts.append(f"<a href='#case{r['index']:02d}'>{r['index']:02d}-{html.escape(r['version'])}</a> ")
    html_parts.append("</nav><div class='grid'>")
    for r in records:
        html_parts.append(f"<section class='card' id='case{r['index']:02d}'>")
        html_parts.append(f"<h2>{r['index']:02d}. {html.escape(r['title'])}</h2>")
        html_parts.append(f"<div class='meta'>{html.escape(r['version'])} | {html.escape(r['family'])} | {html.escape(r['kind'])} | status: {html.escape(r['status'])}</div>")
        if r["copied_image"]:
            html_parts.append(f"<a href='{html.escape(r['copied_image'])}'><img class='hero' src='{html.escape(r['copied_image'])}'></a>")
        else:
            html_parts.append("<div class='hero'>Image missing</div>")
        html_parts.append(f"<p><b>用户批注:</b> {html.escape(r['user_note'])}</p>")
        if r["sheet_target"]:
            html_parts.append(f"<p><b>Sheet 指定:</b> {html.escape(r['sheet_target'])}</p>")
        html_parts.append(f"<p><b>方法归属:</b> <span class='{'ok' if r['is_ours_method'] else 'bad'}'>{'ours' if r['is_ours_method'] else 'needs review'}</span> - {html.escape(r['ours_reason'])}</p>")
        html_parts.append(
            f"<p><b>资产状态:</b> GLB <span class='{'ok' if r['has_local_glb'] else 'warn'}'>{len(r['local_glb_paths'])}</span>, "
            f"OBJ <span class='{'ok' if r['has_local_obj'] else 'warn'}'>{len(r['local_obj_paths'])}</span>, "
            f"metadata/spec {len(r['spec_or_repro_paths'])}, remote {r['remote_hit_count']}</p>"
        )
        if r["notes"]:
            for n in r["notes"]:
                html_parts.append(f"<div class='note'>{html.escape(n)}</div>")
        for title, key, limit in [
            ("Local GLB", "local_glb_paths", 8),
            ("Local OBJ", "local_obj_paths", 8),
            ("Metadata", "metadata_paths", 8),
            ("Spec / repro / scripts", "spec_or_repro_paths", 12),
            ("Remote a100-2 hits", "remote_paths", 10),
        ]:
            vals = r[key][:limit]
            if not vals:
                continue
            html_parts.append(f"<details><summary>{title} ({len(r[key])})</summary>")
            for p in vals:
                html_parts.append(f"<div class='path'>{html.escape(p)}</div>")
            html_parts.append("</details>")
        summaries = [s for s in r["metadata_summaries"] if s]
        if summaries:
            html_parts.append("<details><summary>Metadata summaries</summary>")
            for s in summaries[:4]:
                fields = [f"{k}: {v}" for k, v in s.items() if v not in (None, "", [], {})]
                html_parts.append(f"<div class='path'>{html.escape(' | '.join(fields)[:2400])}</div><hr>")
            html_parts.append("</details>")
        html_parts.append(f"<details><summary>Image paths</summary><div class='path'>{html.escape(r['image_rel'])}</div>")
        for p in r["image_hit_paths"][:20]:
            html_parts.append(f"<div class='path'>{html.escape(p)}</div>")
        html_parts.append("</details>")
        html_parts.append("</section>")
    html_parts.append("</div>")
    (OUT / "user_selected_case_shortlist_20260512.html").write_text("".join(html_parts), encoding="utf-8")


if __name__ == "__main__":
    build()
