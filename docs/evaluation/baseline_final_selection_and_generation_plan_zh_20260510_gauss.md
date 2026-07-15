# R-SLG baseline / strict one-to-one final selection 与生成计划（Gauss, 2026-05-10）

## 0. 范围与约束

- 本文只服务 baseline/evaluation 线：整理 traditional baseline、ours V23 三 seed pool、strict one-to-one 主文候选与后续生成清单。
- 不修改 `paper_siga/main.tex`，不启动远端长任务，不删除文件。
- 结论优先级：一对一可比性 > 三 seed 稳定性 > root quality / visual QA > 指标漂亮程度。

## 1. 已确认的本地证据

### 1.1 Ours V23 三 seed metrics

三组 V23 全 family strict visual matched texture 的 surface metrics 均已落盘：

| seed pool | metrics |
|---|---|
| first seed V23 | `results/strict_visual_matched_texture_V23_all_family_20260510_remote/surface_metrics_occ64.csv` |
| second seed V23 | `results/strict_visual_matched_texture_V23_all_family_seed20260511_20260510_remote/surface_metrics_occ64.csv` |
| third seed V23 | `results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/surface_metrics_occ64.csv` |

三 seed 汇总文档已有：

- `docs/evaluation/strict_visual_matched_V23_all_family_three_seed_summary_zh_20260510.md`

已知三 seed 稳定性摘要：

| family | case | 三 seed 结论 | min LCR / max components_r0 | 用途建议 |
|---|---|---:|---:|---|
| L-system | `V23_lsys_pine_canopy_d5_multi_root_smooth_needles` | main-stable | 0.999703 / 2 | 主文 L-system 第一候选 |
| L-system | `V23_lsys_root_fan_d5_dense_rootlets_variant` | appendix-stable | 0.997882 / 5 | appendix；root quality 需 QA |
| L-system | `V23_lsys_root_fan_d5_multi_root_smooth_rootlets` | appendix-stable | 0.998854 / 3 | appendix 或补生成 |
| L-system | `V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils` | appendix-stable | 0.998551 / 3 | appendix；避免作为主文唯一 vine 证据 |
| Space colonization | `V23_sc_bush_shell_220_attractor_leaf_shell` | main-stable | 0.999801 / 3 | 主文/appendix 皆可，视觉像 bush shell |
| Space colonization | `V23_sc_tree_crown_260_attractor_leaf_shell` | near-stable | 0.999372 / 7 | SC 一对一主文候选，但需视觉 QA |
| Space colonization | `V23_sc_tree_crown_260_sparse_kill_variant` | near-stable | 0.999683 / 5 | SC 备选/appendix |
| Space colonization | `V23_sc_root_network_260_attractor_rootlets` | appendix-stable | 0.998814 / 13 | root-network claim 需新生成 |
| DLA/frontier | `V23_dla_coral_cluster_900_staghorn_frontier` | main-stable | 1.000000 / 1 | 主文 DLA 第一候选 |
| DLA/frontier | `V23_dla_frontier_sheet_700_open_boundary` | main-stable | 1.000000 / 1 | 主文 DLA 第二候选 |
| DLA/frontier | `V23_dla_crystal_cluster_520_faceted_frontier` | main-stable | 1.000000 / 1 | appendix 或补充 transform/coral 对照 |
| DLA/frontier | `V23_dla_coral_cluster_900_lace_porosity_variant` | near-stable | 0.999150 / 7 | appendix；porosity 视觉需 QA |
| IFS/transform | `V23_ifs_radial_ornament_o8_d4_orbit_spokes` | main-stable | 0.999888 / 2 | 主文 IFS 第一候选 |
| IFS/transform | `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges` | near-stable | 0.999739 / 4 | 主文 IFS 第二候选，和 pyrite baseline 对齐 |
| IFS/transform | `V23_ifs_branch_ornament_d5_contact_facets` | main-stable | 0.999485 / 3 | appendix 或主文小图 |
| IFS/transform | `V23_ifs_fractal_tree_d5_branch_copy` | near-stable | 0.999228 / 4 | appendix；不要作为 IFS tree 正例，除非补生成 |

### 1.2 V23 selected-8 visual 证据

当前应使用新的 render-target 目录，而不是旧的只含两个 L-system case 的 selected8 目录：

- contact sheet: `visuals/strict_visual_matched_texture_V23_all_family_selected8_zoom_render_target_20260510/strict_visual_matched_texture_V23_all_family_selected8_render_target_contact_sheet_20260510.png`
- per-case zoom/comparison: `visuals/strict_visual_matched_texture_V23_all_family_selected8_zoom_render_target_20260510/<case>/strict_matched_zoom_comparison.png`
- 该目录包含：pine、root fan dense、SC tree crown、DLA staghorn、DLA frontier sheet、DLA crystal、IFS lattice、IFS radial 等。

### 1.3 Traditional baseline / one-to-one baseline 证据

用户点名的传统 baseline 目录：

- `case_gallery_for_user_20260509/06_baselines_metrics_ablation`

本地检查时该目录没有可用文件，因此不能作为当前主证据。当前可用 evidence 应转向以下路径：

| evidence | path | 备注 |
|---|---|---|
| matched selection manifest | `case_gallery_for_user_20260510_matched_selection/manifest.csv` | 含 baseline 与 strict matched proxy/gallery symlink |
| publication baseline matrix | `results/publication_baseline_metrics_20260510/publication_baseline_master_manifest_20260510.csv` | Trellis2 one-shot、latent copy、mesh-space generated-root、ours/PS-RSLG、blocked future slots |
| one-to-one geometry metrics | `results/baseline_one_to_one_metrics_20260510/metrics.csv` | baseline 一对一 mesh 指标 |
| one-to-one surface metrics | `results/baseline_one_to_one_surface_metrics_20260510/surface_metrics_occ64.csv` | `dla_cluster_baseline`、`ifs_branch_tree_baseline`、`lsystem_branch_baseline`、`sc_tree_canopy_baseline` 等 |
| one-to-one renders/assets | `visuals/baseline_one_to_one_white_20260510/` | baseline front/iso/glb cases |
| remote matched candidates | `case_gallery_for_user_20260510_remote_matched_candidates/` | 含传统目标、baseline overview、strict matched v3b/v4/v5/v6/V8/V10-V13、Gen3D baseline ablation |

## 2. Strict one-to-one final 候选表

### 2.1 L-system

| role | case / baseline | evidence | 决策 |
|---|---|---|---|
| traditional baseline | `lsystem_branch_baseline` | `results/baseline_one_to_one_surface_metrics_20260510/surface_metrics_occ64.csv`; `visuals/baseline_one_to_one_white_20260510/` | 可作为一对一 baseline 行 |
| ours primary | `V23_lsys_pine_canopy_d5_multi_root_smooth_needles` | 三 seed stable；selected-8 有 zoom render | **进主文**。最稳的 L-system positive case，指标和视觉证据均齐。 |
| ours secondary | `V23_lsys_root_fan_d5_dense_rootlets_variant` | selected-8 有 render；三 seed appendix-stable | **appendix / 补生成候选**。适合 root claim，但 rootlet 附着和根部自然度需人工 QA。 |
| ours backup | `V23_lsys_root_fan_d5_multi_root_smooth_rootlets` | 三 seed appendix-stable | **appendix**。若 dense rootlets 显得毛刺/过密，可作为更干净备选。 |
| ours reject-for-main | `V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils` | 三 seed appendix-stable | **不建议主文**。可放 appendix，避免承担主 claim。 |

L-system 推荐：主文放 pine；appendix 放 root fan dense/smooth。若主文需要“root quality”强证据，应补一批 root fan rerun。

### 2.2 Space colonization (SC)

| role | case / baseline | evidence | 决策 |
|---|---|---|---|
| traditional baseline | `sc_tree_canopy_baseline` | `results/baseline_one_to_one_surface_metrics_20260510/surface_metrics_occ64.csv`; `visuals/baseline_one_to_one_white_20260510/` | 可作为 SC 一对一 baseline 行 |
| ours primary one-to-one | `V23_sc_tree_crown_260_attractor_leaf_shell` | selected-8 有 render；三 seed near-stable | **主文候选**。与 tree canopy baseline 最对齐，但 max components_r0 到 7，需要人工确认碎片不可见。 |
| ours stable visual | `V23_sc_bush_shell_220_attractor_leaf_shell` | 三 seed main-stable | **主文备选 / appendix**。稳定性最好，但和 `sc_tree_canopy_baseline` 的一对一语义略弱。 |
| ours backup | `V23_sc_tree_crown_260_sparse_kill_variant` | 三 seed near-stable | **appendix/备选**。若 primary 视觉太密，可替换。 |
| ours root-network | `V23_sc_root_network_260_attractor_rootlets` | 三 seed appendix-stable；components_r0 可到 13 | **不建议主文，需新生成**。root network 是重要 claim，但当前 fragment/root QA 风险高。 |

SC 推荐：若主文强调 strict one-to-one，用 `sc_tree_crown_260_attractor_leaf_shell`；若主文强调稳定性，用 `sc_bush_shell_220_attractor_leaf_shell`。root-network 需补生成后再进入主文。

### 2.3 DLA / frontier

| role | case / baseline | evidence | 决策 |
|---|---|---|---|
| traditional baseline | `dla_cluster_baseline` | `results/baseline_one_to_one_surface_metrics_20260510/surface_metrics_occ64.csv`; `visuals/baseline_one_to_one_white_20260510/` | 可作为 DLA baseline 行 |
| ours primary | `V23_dla_coral_cluster_900_staghorn_frontier` | 三 seed main-stable；selected-8 有 render | **进主文**。LCR=1.0、components=1，最强 DLA/frontier 正例。 |
| ours secondary | `V23_dla_frontier_sheet_700_open_boundary` | 三 seed main-stable；selected-8 有 render | **进主文或主文小图**。展示 open boundary/frontier 的互补形态。 |
| ours appendix | `V23_dla_crystal_cluster_520_faceted_frontier` | 三 seed main-stable；selected-8 有 render | **appendix/补充**。形态偏 crystal，适合说明 DLA/frontier 泛化。 |
| ours appendix-risk | `V23_dla_coral_cluster_900_lace_porosity_variant` | 三 seed near-stable | **appendix**。porosity 视觉如通过 QA 可保留；不作为主文核心。 |

DLA 推荐：主文至少放 staghorn frontier；若版面允许，frontier sheet 作为第二个 DLA family positive。无需立即补指标，主要缺视觉 QA。

### 2.4 IFS / transform

| role | case / baseline | evidence | 决策 |
|---|---|---|---|
| traditional baseline | `ifs_branch_tree_baseline` | `results/baseline_one_to_one_surface_metrics_20260510/surface_metrics_occ64.csv`; `visuals/baseline_one_to_one_white_20260510/` | 可作为 transform/branch baseline 行 |
| ours primary | `V23_ifs_radial_ornament_o8_d4_orbit_spokes` | 三 seed main-stable；selected-8 有 render | **进主文**。稳定，结构清晰，适合代表 transform/orbit copy。 |
| ours one-to-one pyrite | `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges` | 三 seed near-stable；selected-8 有 render；publication baseline matrix 有 pyrite baseline | **主文候选**。和 pyrite/crystal baseline 对齐更好，但需确认 bridges 视觉自然度。 |
| ours appendix | `V23_ifs_branch_ornament_d5_contact_facets` | 三 seed main-stable | **appendix 或主文小图**。稳定但 family claim 不如 radial/lattice 清楚。 |
| ours reject-for-main | `V23_ifs_fractal_tree_d5_branch_copy` | 三 seed near-stable | **暂不主文**。除非补生成出更强 branch tree，否则避免把 IFS tree 作为正例。 |

IFS 推荐：主文 radial ornament + lattice pyrite 二选一或都放；branch tree 暂不承担主文 claim。

## 3. 发布级主文候选排序

### 3.1 最小主文四 family 组合

| rank | family | primary case | baseline pair | reason |
|---:|---|---|---|---|
| 1 | DLA/frontier | `V23_dla_coral_cluster_900_staghorn_frontier` | `dla_cluster_baseline` | 三 seed 完全连通，视觉目录已齐，是最硬 positive。 |
| 2 | L-system | `V23_lsys_pine_canopy_d5_multi_root_smooth_needles` | `lsystem_branch_baseline` | 三 seed stable，能代表 grammar/recursive branching。 |
| 3 | IFS/transform | `V23_ifs_radial_ornament_o8_d4_orbit_spokes` | `ifs_branch_tree_baseline` 或 pyrite rows | 三 seed stable，结构辨识度强。 |
| 4 | SC | `V23_sc_tree_crown_260_attractor_leaf_shell` | `sc_tree_canopy_baseline` | 一对一语义最对齐，但需要视觉 QA 与 fragment 可见性检查。 |

### 3.2 扩展主文 / appendix 组合

| bucket | cases |
|---|---|
| 主文可加 | `V23_dla_frontier_sheet_700_open_boundary`, `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges` |
| appendix 强 | `V23_sc_bush_shell_220_attractor_leaf_shell`, `V23_dla_crystal_cluster_520_faceted_frontier`, `V23_ifs_branch_ornament_d5_contact_facets` |
| appendix 或 rerun 后上主文 | `V23_lsys_root_fan_d5_dense_rootlets_variant`, `V23_lsys_root_fan_d5_multi_root_smooth_rootlets`, `V23_sc_root_network_260_attractor_rootlets` |
| 暂不主文 | `V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils`, `V23_ifs_fractal_tree_d5_branch_copy`, `V23_dla_coral_cluster_900_lace_porosity_variant` |

## 4. 需要新生成的 case 与优先级

### Priority A: root quality / root claim

1. L-system root fan rerun：
   - base cases: `V23_lsys_root_fan_d5_dense_rootlets_variant`, `V23_lsys_root_fan_d5_multi_root_smooth_rootlets`
   - 目标：更清晰主根、rootlet 附着、减少毛刺/漂浮末端。
   - 建议：3-4 seeds；保留当前 dense/smooth 两种 guide；增加 root guide 强度 sweep。

2. SC root network rerun：
   - base case: `V23_sc_root_network_260_attractor_rootlets`
   - 目标：降低 components_r0，提升 visible root reachability，减少孤立 root fragments。
   - 建议：3-4 seeds；提高 root anchor/kill radius 约束；额外导出 path-to-root/orphan fragment 指标。

### Priority B: visual quality for main positives

3. SC tree crown QA/rerun：
   - base case: `V23_sc_tree_crown_260_attractor_leaf_shell`
   - 目标：确认 components_r0<=7 的小碎片是否可见；若可见，则 rerun sparse/attractor guide。

4. DLA staghorn/frontier sheet visual sweep：
   - base cases: `V23_dla_coral_cluster_900_staghorn_frontier`, `V23_dla_frontier_sheet_700_open_boundary`
   - 目标：保持 LCR=1.0，同时优化 branch thickness、frontier roughness、texture naturalization。

### Priority C: transform/IFS 兜底

5. IFS lattice/radial visual QA：
   - base cases: `V23_ifs_radial_ornament_o8_d4_orbit_spokes`, `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges`
   - 目标：确认 copy bridges/contact facets 不是过度机械重复；若失败，仅补 lattice 2-3 seeds。

6. IFS branch tree rerun（可选）：
   - base case: `V23_ifs_fractal_tree_d5_branch_copy`
   - 只在论文必须展示 IFS tree 时执行；否则放弃主文。

## 5. 指标展示建议

### 5.1 主表指标

每个 family 分开报告，避免把 plant/root 与 crystal/coral 形态混成一个排名：

| family | recommended metrics |
|---|---|
| L-system | `components_r0`, `lcr_r0`, `occupied`, root/branch visual QA；root fan 额外报告 root reachability/orphan ratio |
| SC | `components_r0`, `lcr_r0`, `occupied`, crown/root shell visual QA；root network 额外报告 path-to-root |
| DLA/frontier | `components_r0`, `lcr_r0`, `occupied`, frontier continuity, branch thickness QA |
| IFS/transform | `components_r0`, `lcr_r0`, `occupied`, copy contact/bridge visibility QA |

### 5.2 Baseline rows

主文 baseline matrix 可分两层：

1. Traditional one-to-one baseline rows：
   - `lsystem_branch_baseline`
   - `sc_tree_canopy_baseline`
   - `dla_cluster_baseline`
   - `ifs_branch_tree_baseline`

2. Gen3D publication baseline rows：
   - Trellis2 one-shot
   - Trellis2 trivial latent copy
   - Mesh-space generated-root baseline
   - Ours / PS-RSLG
   - TRELLIS1 / Hunyuan rows 目前保持 blocked/future slot，除非 Lane A 交付可评估 artifact。

## 6. 候选评分脚本/命令建议

为避免和其他 agent 修改脚本冲突，当前建议先用一次性命令生成 CSV，而不是改已有 pipeline。若需要落盘，可写到新的 `results/baseline_final_selection_gauss_20260510/`。

建议命令：

```bash
mkdir -p results/baseline_final_selection_gauss_20260510
python - <<'PY'
import csv, os, re
from collections import defaultdict

metric_paths = [
    "results/strict_visual_matched_texture_V23_all_family_20260510_remote/surface_metrics_occ64.csv",
    "results/strict_visual_matched_texture_V23_all_family_seed20260511_20260510_remote/surface_metrics_occ64.csv",
    "results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/surface_metrics_occ64.csv",
]
render_root = "visuals/strict_visual_matched_texture_V23_all_family_selected8_zoom_render_target_20260510"

def case_base(label):
    return re.sub(r"_steps\\d+_tex\\d+_seed\\d+_xformers$", "", label)

def family(case):
    if "_lsys_" in case: return "L-system"
    if "_sc_" in case: return "Space colonization"
    if "_dla_" in case: return "DLA/frontier"
    if "_ifs_" in case: return "IFS/transform"
    return "unknown"

rows = defaultdict(list)
for seed_i, path in enumerate(metric_paths, 1):
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            b = case_base(r["label"])
            rows[b].append({
                "seed_i": seed_i,
                "lcr_r0": float(r["lcr_r0"]),
                "components_r0": int(r["components_r0"]),
                "occupied": int(r["occupied"]),
            })

out = "results/baseline_final_selection_gauss_20260510/v23_three_seed_candidate_scores.csv"
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=[
        "family","case","seed_count","min_lcr_r0","mean_lcr_r0",
        "max_components_r0","mean_occupied","has_selected8_render","render_path"
    ])
    w.writeheader()
    for case, vals in sorted(rows.items(), key=lambda kv: (family(kv[0]), kv[0])):
        lcrs = [v["lcr_r0"] for v in vals]
        comps = [v["components_r0"] for v in vals]
        occs = [v["occupied"] for v in vals]
        render_path = os.path.join(render_root, case, "strict_matched_zoom_comparison.png")
        w.writerow({
            "family": family(case),
            "case": case,
            "seed_count": len(vals),
            "min_lcr_r0": f"{min(lcrs):.6f}",
            "mean_lcr_r0": f"{sum(lcrs)/len(lcrs):.6f}",
            "max_components_r0": max(comps),
            "mean_occupied": f"{sum(occs)/len(occs):.1f}",
            "has_selected8_render": os.path.exists(render_path),
            "render_path": render_path if os.path.exists(render_path) else "",
        })
print(out)
PY
```

候选排序规则建议：

1. family 内先筛 `seed_count=3`。
2. 主文候选优先 `min_lcr_r0 >= 0.999` 且 `max_components_r0 <= 7`。
3. root-family 或 root-claim case 即使 LCR 高，也必须人工检查 root attachment、floating tips、orphan fragments。
4. selected-8 render 不存在的 case 不进入主文，只进 appendix 或 rerun queue。

## 7. 下一步远端批量生成建议

不在本地启动。建议远端按小批次提交，避免 SSH/长任务冲突：

| batch | cases | seeds | purpose | priority |
|---|---|---:|---|---|
| A-root | L-system root fan dense/smooth + SC root network | 3-4 each | root quality / root reachability | 最高 |
| B-SC | SC tree crown attractor/sparse guide | 2-3 each | 主文 SC one-to-one 兜底 | 高 |
| C-DLA | staghorn + frontier sheet guide sweep | 2-3 each | 主文视觉 polish | 中 |
| D-IFS | lattice/radial polish; branch-tree optional | 2-3 each | transform family 兜底 | 中低 |

建议资源纪律：最多 3 个 SSH shell；优先 GPU 4-7；每批先出 low-step/preview contact sheet，再扩到 full tex2048；所有新结果落到新的 dated `results/` 与 `visuals/` 子目录，不覆盖当前 V23 evidence。

## 8. 当前结论

- 已可进主文的最小候选：`V23_dla_coral_cluster_900_staghorn_frontier`、`V23_lsys_pine_canopy_d5_multi_root_smooth_needles`、`V23_ifs_radial_ornament_o8_d4_orbit_spokes`、`V23_sc_tree_crown_260_attractor_leaf_shell`。
- 最值得补生成的缺口：L-system root fan 与 SC root network，因为它们最直接支撑 root-quality claim，但当前更适合 appendix。
- 当前最需要人工视觉 QA：SC tree crown 小碎片是否可见、root fan/root network 的 root attachment、IFS lattice bridges 是否机械、DLA frontier 的 texture/branch thickness 是否论文级。
