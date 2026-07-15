# IFS / DLA 主实验候选定稿记录

日期：2026-05-11  
状态：active selection；等待 L-system V35 远端 GLB 完成后合并四类统一图和表。

## IFS / Pyrite

**主推：`pyrite_depth_hq_warm_showcase stage04`**

- GLB：`visuals/pyrite_depth_hq_warm_showcase_20260509/stage04_textured.glb`
- 白底渲染：`visuals/pyrite_depth_hq_warm_showcase_20260509/renders/stage04_iso.png`
- contact：`visuals/pyrite_depth_hq_warm_showcase_20260509/renders/pyrite_hq_warm_render_contact.png`
- metrics：`visuals/pyrite_depth_hq_warm_showcase_20260509/metrics_occ64.json`
- stage04 mesh scale：`660309` vertices、`482348` faces、`30807` occupied voxels。
- 推荐理由：这是用户头图中认可的 HQ pyrite lattice 线，晶格/矿物读感比 V24 strict pyrite 更适合主视觉。
- caveat：该 metrics schema 目前不含 r0/r1 LCR 字段；正文写成 ordered lattice / transform-family visual asset，不写成拓扑最强或物理晶体生长。

**指标/strict 备份：V24 pyrite lattice**

- GLB：`visuals/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510/V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA_steps8_tex2048_seed20284526_xformers/textured.glb`
- 证据文档：`docs/evaluation/strict_visual_matched_V24_three_seed_QA_recommendation_zh_20260510.md`
- 口径：三 seed r0 有 tiny islands，但 r1-connected 且 LCR 高；作为 transform-copy/lattice strict evidence。

## DLA / Coral

**主推：`v14_dla_branching_table_coral_b`**

- GLB：`visuals/strict_visual_matched_texture_v14_branching_coral_seed20279100_20260510/v14_dla_branching_table_coral_b_steps8_tex2048_seed20279804_xformers/textured.glb`
- 白底 zoom：`visuals/strict_visual_matched_texture_v14_branching_coral_seed20279100_zoom_20260510/v14_dla_branching_table_coral_b/strict_matched_zoom_comparison.png`
- metrics：`results/strict_visual_matched_texture_v14_branching_coral_seed20279100_20260510_remote/surface_metrics_occ64.json`
- 指标：r0/r1/r2 均 1 component，LCR `1.0`；occupied `6367`，box_dim_32_96 `1.9431226435170017`。
- 推荐理由：与头图 coral 不重复；比 V24 staghorn/frontier 更少“硬管/体素块”读感，整体更像薄片/分支珊瑚。
- caveat：近景仍有低多边形切面，红白纹理较强，可能偏 stylized；最终主图应选择最干净视角和 zoom。

**指标备份：V24 DLA staghorn/frontier**

- `V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA`
- `V24_dla_frontier_sheet_700_open_boundary_polish_seedA`
- 证据：三 seed r0 单连通，适合 metric backup；视觉上端部/frontier spike 偏几何化，不宜作为唯一自然视觉正例。

## 进入最终四类主实验的当前建议

- SC：`V32_sc_tree_balanced_canopy_D`，备选 `V32_sc_tree_leafmass_shell_B` / `V29_sc_tree_softleaf_entry_D`。
- L-system：等待 V35 textured GLB；本地预览优先 `V35_lsys_branch_tapered_bud_A` 和 `V35_lsys_branch_fused_fork_C`，`B/D` 作为低碎片备份。
- IFS：`pyrite_depth_hq_warm_showcase stage04`。
- DLA：`v14_dla_branching_table_coral_b`。

