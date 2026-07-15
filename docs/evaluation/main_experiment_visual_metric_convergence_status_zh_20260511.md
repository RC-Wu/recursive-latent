# 主实验视觉与指标收束状态

日期：2026-05-11  
状态：active / evidence generated / TeX not patched yet

## 本轮新增产物

### 四类 traditional-vs-ours 白底 comparison

- 渲染 manifest：`results/main_experiment_case_metrics_20260511/main_experiment_traditional_vs_ours_manifest_20260511.json`
- 单 case raw / callout / zoom：`visuals/main_experiment_traditional_vs_ours_white_zoom_20260511/`
- QA contact sheet：`visuals/main_experiment_traditional_vs_ours_white_zoom_20260511/main_experiment_traditional_vs_ours_contact_sheet_20260511.png`
- 论文矩阵草稿：`paper_siga/figures/main_experiment_traditional_vs_ours_white_zoom_matrix_20260511.png`

当前矩阵行：

| Family | Traditional | Ours |
|---|---|---|
| Space colonization | `sc_tree_canopy_steps6_tex1024_xformers` | `V32_sc_tree_balanced_canopy_D` |
| L-system | `lsystem_branch_matched_steps6_tex1024_xformers` | `V40_lsys_branch_primary_fork_slim_D` |
| DLA / frontier | `dla_cluster_steps6_tex1024_xformers` | `v14_dla_branching_table_coral_b` |
| IFS / transform | `ifs_branch_tree_matched_steps6_tex1024_xformers` | `pyrite_depth_hq_warm_showcase/stage04_textured.glb` |

### 统一指标

- Surface-voxel metrics：`results/main_experiment_case_metrics_20260511/main_experiment_selected_surface_metrics_occ64.csv`
- Recursive mesh metrics：`results/main_experiment_case_metrics_20260511/main_experiment_selected_recursive_mesh_metrics.csv`
- LaTeX table draft：`paper_siga/figures/main_experiment_selected_metrics_table_20260511.tex`

关键数值（surface protocol）：

| Family | Method | `components_r0` | `lcr_r0` | `components_r1` | box dim | faces |
|---|---|---:|---:|---:|---:|---:|
| SC | traditional | 1 | 1.000 | 1 | 1.797 | 31,700 |
| SC | ours V32-D | 10 | 0.996 | 1 | 1.727 | 84,062 |
| L-system | traditional matched | 5 | 0.999 | 1 | 1.961 | 20,736 |
| L-system | ours V40-D | 1 | 1.000 | 1 | 1.401 | 16,192 |
| DLA | traditional cluster | 6 | 1.000 | 1 | 1.987 | 10,800 |
| DLA | ours V14 table coral B | 1 | 1.000 | 1 | 1.941 | 11,996 |
| IFS | traditional matched branch tree | 1 | 1.000 | 1 | 1.994 | 65,600 |
| IFS | ours pyrite HQ stage04 | 1 | 1.000 | 1 | 2.195 | 482,348 |

## QA 判断

### Space colonization

- `V32_sc_tree_balanced_canopy_D` 在 overview 上比传统 baseline 更像有冠层质量的可读树冠，材质/叶团效果明显。
- caveat：post-GLB exact r0 有 tiny components，`components_r0=10`，但 r1 connected。正文应写 visual/export readiness + near-connected support，不写成拓扑最强。
- 备选：`V29_sc_tree_softleaf_entry_D` 是用户认可上色候选；如要减少 V32 的材质岛风险，可把 V29 作为补充或备选行。

### L-system

- V40-D 是当前指标最稳：`components_r0=1, LCR=1.0`，材质比 V40-B 稳定。
- 视觉仍未完全发表级：overview 太稀疏，和传统 branch-with-side-branches 的密集结构不是同等视觉强度；自动 zoom 也没有稳定命中最佳 primary fork。
- V40-A 视觉分叉读感更自然，但 r0 被分成 4 个 surface components，`LCR=0.486`，只能作为视觉备选。
- V40-B 指标接近单连通，`components_r0=2, LCR=0.998`，但红/绿材质分裂严重，不建议主文正例。
- V41 远端已完成但失败：密度增加后白底近景碎成细针/叶片，post-GLB exact r0 连通也变差，不建议主文使用。
- V42 远端已完成，`lowfrag_B` 与 `dense_C` 指标最强，surface `components_r0=1, LCR=1.0`，但视觉仍不够发表级：zoom 中仍像细线骨架上贴了扁叶/芽片/长针，连续木质 Y-fork 读感不足。因此 V42 只能作为“V41 后进步但未最终收束”的备选证据。
- V43 本地 OBJ 已完成，pre-export 指标单连通且去掉了 V42 的细针/叶片碎片，但白底 zoom 变成“管子 + 圆鼓包 saddle/collar”，自然木质连续感仍不足，不应上远端。
- 当前建议：如果必须马上收束，V40-D 仍是 topology-stable fallback；若按用户要求追发表级主视觉，应继续 V44：把 V43 的圆鼓包改成沿主枝拉长的低起伏 cambium saddle，让侧枝从融合带自然转出，本地白底 zoom 过关后再上远端。
- 2026-05-11 late update：V54--V57 已证明同一长细 graph 的局部微调不足以发表级收束。四轮都做到 pre-export single component / LCR 1.0，但 contact sheet 仍被细管骨架、裁切边、club-like 端部或 saddle 鼓包主导；因此 V54--V57 都不应上远端，也不能替换主实验。
- V58 已切换为 compact short-bough root/silhouette：
  - dry-run：`results/strict_visual_matched_cases_V58_lsystem_branch_short_bough_yfork_20260511_dryrun/`
  - contact：`visuals/strict_visual_matched_cases_V58_lsystem_branch_obj_zoom_short_bough_20260511/V58_lsystem_branch_short_bough_obj_contact_sheet_20260511.png`
  - metrics：四候选 OBJ 均 `mesh_component_count=1`、`LCR=1.0`、`raw_marching_cubes_component_count=1`、`retained_ratio=1.0`；faces 约 `11.8k--16.1k`。
  - visual QA：V58 明显摆脱 V54--V57 的长细管局部最小值，`lowfrag_B` 与 `compact_D` 当前最干净，允许进入远端 textured GLB 验证。
  - claim boundary：这只是 OBJ 视觉门槛通过；post-GLB 仍需确认没有暗 terminal drop、纹理分裂、塑料感或插接管回归。未通过前不 patch `paper_siga/main.tex`。
- V58 B/D post-GLB 已完成：
  - GLB 白底 contact：`visuals/strict_visual_matched_texture_V58_lsystem_branch_short_bough_yfork_BD_zoom_white_20260511/V58_lsystem_branch_short_bough_BD_glb_contact_sheet_20260511.png`
  - surface metrics：`results/main_experiment_case_metrics_20260511/v58_lsystem_bd_postglb_surface_metrics_occ64.csv`
  - selected metrics：`results/main_experiment_case_metrics_20260511/v58_lsystem_bd_postglb_metrics/`
  - 两个候选 r0/r1/r2 全部 `components=1, LCR=1.0`，是目前 L-system 线最干净的 post-GLB connectivity 结果之一。
  - 视觉仍未最终发表级：GLB zoom 中有明显 faceted/锯齿 strip 和偏塑料的木纹，`compact_D` 局部端部过暗。V58 可作为重要进步/fallback，但暂不替换主实验最终图；下一步应做 V59 high-res smoother short-bough，而不是回退到长细 graph。

### DLA / frontier

- `v14_dla_branching_table_coral_b` 相比传统 DLA cluster 明显减少体素块读感，并且 r0/r1 均单连通。
- caveat：近景仍有低多边形切面和红白 stylized texture，最好把它写成 frontier/coral-like connected asset，而不是 natural coral 的最终审美上限。

### IFS / transform

- `pyrite_depth_hq_warm_showcase/stage04` 是当前最强 pyrite HQ 视觉，晶格/transform-copy 读感强，指标也单连通。
- caveat：传统 baseline 目前是 `ifs_branch_tree_matched`，不是 pyrite 同类；这个行适合作为 “IFS/transform family contrast” 或 “pyrite positive case”，不适合写成完全严格的 pyrite-vs-pyrite one-to-one baseline。

## 论文接入建议

1. 主文可使用矩阵图和指标表，但 caption 必须把 L-system 和 IFS 的 claim boundary 写清楚。
2. L-system 如果还有实验预算，优先继续 V41/V42，而不是直接把 V40-D 当最终胜利图。
3. DLA 和 SC 可以作为当前主实验视觉支撑，但都要保留 caveat：传统 baseline 不是 strawman，connectivity 指标不是唯一视觉质量指标。
4. `paper_siga/main.tex` 仍未 patch，避免覆盖用户保留中文；证据闭环和用户确认后再局部替换 includegraphics / input table。
