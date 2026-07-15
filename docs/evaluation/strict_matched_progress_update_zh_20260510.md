# 严格一对一 baseline / ours 匹配进展更新（2026-05-10）

## 1. 已完成的新产物

### 1.1 传统方法任务靶子

新增 CPU-only 传统靶子生成器：

- `assets/strict_matched_task_targets_20260510.py`

输出：

- `results/strict_matched_task_targets_20260510/manifest.csv`
- `results/strict_matched_task_targets_20260510/manifest.json`
- `results/strict_matched_task_targets_20260510/cases.txt`
- 12 个 `traditional_target.obj`

覆盖：

| family | cases |
|---|---|
| L-system | `lsys_pine_canopy_d5`, `lsys_root_fan_d5`, `lsys_climbing_vine_d6` |
| Space colonization | `sc_tree_crown_260`, `sc_root_network_260`, `sc_bush_shell_220` |
| DLA/frontier | `dla_coral_cluster_900`, `dla_aniso_crystal_800`, `dla_frontier_sheet_700` |
| IFS/transform | `ifs_branch_tree_d6`, `ifs_radial_ornament_o8_d4`, `ifs_fractal_lattice_d4` |

白底真实相机 zoom 输出：

- `visuals/strict_matched_traditional_targets_zoom_20260510/strict_matched_traditional_targets_contact_20260510.png`
- 每个 case 的单独图在 `visuals/strict_matched_traditional_targets_zoom_20260510/<case>/strict_matched_zoom_comparison.png`

指标：

- `results/strict_matched_task_targets_metrics_20260510/surface_metrics_occ64.csv`
- `results/strict_matched_task_targets_metrics_20260510/surface_metrics_occ64.json`

观察：

- L-system、space colonization、IFS branch tree 在 surface-voxel 指标上基本连通，所以不能写“传统方法天然不连通”。
- 传统方法的弱点主要是视觉资产质量：管状骨架、无叶片/根须材质、无 PBR 细节、DLA cube aggregate 的块状感。
- `dla_frontier_sheet_700` 和 `ifs_radial_ornament_o8_d4` 在严格 r0 下多 component 明显，但 r1/r2 后趋于连通；这说明指标要同时报告 strict surface proxy 和 seam/alias-tolerant proxy。

### 1.2 高质量 ours root / GLB zoom

修复并加速了真实相机 zoom 脚本：

- `scripts/figures/matched_camera_zoom_render_20260510.py`

修复点：

- 加入 `--engine` 选项；
- 对大网格抽样 world vertices，避免 60 万级顶点逐点计算导致高 GLB 卡死；
- Blender Python 没有 PIL 时先保存 raw render 和 callout 坐标，回到系统 Python 画框和拼图；
- 透明背景统一合成纯白，避免查看器显示黑底。

验证：

- `python3 -m pytest scripts/figures/test_matched_camera_zoom_render_20260510.py -q`
- 结果：`2 passed`

当前高质量 ours 候选：

| ours case | path | surface metric summary | 视觉判断 |
|---|---|---|---|
| `tree_compete_s3` | `visuals/textured_glb_20260508/tree_compete_s3/textured.glb` | r0: 2 comps, LCR 0.993; r2: 1 comp | 植物/树冠线主候选，视觉强 |
| `tree_roots_hq` | `visuals/public_guide_textured_glb_20260509/tree_compete_d4_pruned_tree_roots_steps8_tex2048_xformers/textured.glb` | r0: 2 comps, LCR 0.993; r2: 1 comp | 根/树混合视觉强，但形状偏奇异 |
| `vine_stage5` | `visuals/textured_glb_20260508/vine_d5_compete_s5_inference/textured.glb` | r0/r1/r2: 1 comp, LCR 1.0 | 植物/藤蔓/根系最强候选 |
| `pyrite_stage4` | `visuals/pyrite_depth_hq_warm_showcase_20260509/stage04_textured.glb` | r0/r1/r2: 1 comp, LCR 1.0 | transform/lattice 正候选，但体素块感强 |
| `coral_dla_octopus` | `visuals/connected_scaffold_v2_textured_glb_hq_20260509/volumetric_dla_coral_octopus_hq_steps8_tex2048_xformers/textured.glb` | r0/r1/r2: 1 comp, LCR 1.0 | DLA/coral 候选，但仍有 bead/chunk 感 |

对应 zoom 输出：

- `visuals/matched_camera_zoom_existing_roots_20260510/matched_existing_roots_zoom_contact_20260510.png`
- 每个 case 的单独图在 `visuals/matched_camera_zoom_existing_roots_20260510/<case>/strict_matched_zoom_comparison.png`

指标：

- `results/matched_high_quality_root_metrics_20260510/surface_metrics_occ64.csv`
- `results/matched_high_quality_root_metrics_20260510/surface_metrics_occ64.json`

### 1.3 严格一对一候选配对

第一版以视觉质量优先的候选配对：

- `visuals/strict_matched_pair_candidates_20260510/strict_matched_pair_candidates_contact_20260510.png`
- `visuals/strict_matched_pair_candidates_20260510/matched_pair_manifest.csv`

当前可考虑主文的候选：

| traditional task | ours candidate | 状态 |
|---|---|---|
| `lsys_climbing_vine_d6` | `vine_stage5` | 当前最强 matched plant/root 候选之一 |
| `sc_tree_crown_260` | `tree_compete_s3` | 当前最强 tree/crown 候选，但叶片资产 vs tube skeleton 的表示差异要写清楚 |
| `sc_root_network_260` | `vine_stage5` | 当前最强 root/vine competition 候选 |
| `ifs_fractal_lattice_d4` | `pyrite_stage4` | 当前最强 transform/lattice 候选 |

边界/待替换：

- `dla_coral_cluster_900 -> coral_dla_octopus`：指标连通，但视觉仍 bead/chunk，需要 naturalization 或更好 root。
- `dla_aniso_crystal_800 -> pyrite_stage4`：晶体/格点视觉较好，但不是随机 DLA；只能作为 ordered lattice / symmetry task。
- `ifs_branch_tree_d6 -> tree_compete_s3`：类别像树，但不是 transform-copy tree，需要专门生成。
- `ifs_radial_ornament_o8_d4 -> pyrite_stage4`：不成立，已降级。

### 1.4 mode-matched boundary candidates

为了回应“递归模式要一致”，又渲染了一批更接近算子模式但视觉质量较弱的候选：

- `visuals/matched_camera_zoom_transform_dla_candidates_20260510/transform_dla_candidates_zoom_contact_20260510.png`
- `visuals/strict_matched_pair_candidates_20260510_mode_matched/strict_mode_matched_pair_candidates_contact_20260510.png`

包括：

- `lsystem_fork_spiky`
- `lsystem_fork_side_parthenocissus`
- `transform_radial4_pyrite`
- `transform_radial4_bismuth`
- `dla_fork_side_pyrite`
- `dla_side_bismuth`

指标：

- `results/transform_dla_candidate_metrics_20260510/surface_metrics_occ64.csv`
- `results/transform_dla_candidate_metrics_20260510/surface_metrics_occ64.json`

观察：

- 这些候选更接近 “operator family” 本身，但多数仍然视觉碎、透明片多、surface r0 components 高。
- 它们适合作为 boundary/failure evidence，说明只做 mode-matched transform/fork/DLA 不足以达到资产质量；必须结合 better root、projection、masked naturalization 和严格筛选。
- `transform_radial4_pyrite/bismuth` 的 r0 components 为 845、LCR 约 0.628，但 r1 以后几乎连通；说明它们是高密度碎片/缝隙问题，不是完全散点。若后续做 repair/naturalization，可以作为 radial transform ablation 的压力测试。

## 2. 给用户挑 case 的本地目录

已新增：

- `case_gallery_for_user_20260510_matched_selection/`

子目录：

- `01_lsystem_tree_root/`
- `02_space_colonization_tree_root_bush/`
- `03_dla_coral_crystal_frontier/`
- `04_ifs_transform_lattice/`
- `05_good_roots_and_guides/`
- `06_failed_or_screening_only/`
- `07_strict_matched_new_targets/`
- `08_strict_matched_pair_candidates/`
- `09_high_quality_root_zoom/`
- `10_mode_matched_boundary_candidates/`

其中用户最该优先看的：

1. `08_strict_matched_pair_candidates/strict_matched_pair_candidates_contact_20260510.png`
2. `07_strict_matched_new_targets/strict_matched_traditional_targets_contact_20260510.png`
3. `09_high_quality_root_zoom/matched_existing_roots_zoom_contact_20260510.png`
4. `10_mode_matched_boundary_candidates/strict_mode_matched_pair_candidates_contact_20260510.png`

## 3. 当前严谨结论

1. 传统 baseline 靶子已经从“少量松散 case”推进到 12 个可复现任务，覆盖主要 procedural family。
2. ours 不能再用 loose semantic matching。当前主文候选应只保留：
   - vine/root；
   - tree/crown；
   - root network；
   - lattice/pyrite；
   - coral/DLA 仅作为候选或边界。
3. mode-matched 的 lsystem/radial/DLA 候选说明：仅仅使用对应算子不保证资产质量；更好的 root 和 local naturalization 是必要设计，不是装饰。
4. 论文里应把 “strict matched task” 写成两条并行要求：
   - task/mode/depth/shape 要对齐；
   - root 可以更好，但 root 选择要记录 provenance 和 selection budget。
5. 不能声称所有传统方法在 topology 上差；很多传统方法在 surface sampling 下连通很好。我们更强的 claim 是：在相似递归任务下，PS-RSLG 能把可控递归模式与生成模型外观/PBR资产质量结合，并通过 per-depth projection 抑制深度递归碎片传播。

## 4. 下一步必须继续推进

1. 为 `ifs_branch_tree_d6` 生成真正 transform-copy tree-like ours，不再用 `tree_compete_s3` 顶替。
2. 为 `ifs_radial_ornament_o8_d4` 生成干净的 radial ornament/hard-surface candidate；当前 `transform_radial4_*` 太碎。
3. 为 `dla_coral_cluster_900` / `dla_frontier_sheet_700` 继续做 masked naturalization 或 better root，使 bead/cube/chunk 感明显降低。
4. 对 `tree_compete_s3` / `vine_stage5` 做更高采样、白底、相机对齐的最终候选渲染。
5. 把以上 strict matched protocol 写入 `paper_siga/main.tex` 的 task/evaluation/results caption，避免旧 loose comparison 误导审稿人。

## 5. 追加：弱项候选搜索与 V2 配对（2026-05-10 05:25）

弱项搜索文档：

- `docs/evaluation/weak_matched_tasks_candidate_search_zh_20260510.md`
- `results/weak_matched_tasks_candidate_search_20260510/candidate_mapping.csv`

新增弱项候选 zoom：

- `visuals/matched_camera_zoom_weak_search_candidates_20260510/weak_search_candidates_zoom_contact_20260510.png`

指标：

- `results/weak_search_candidate_metrics_20260510/surface_metrics_occ64.csv`
- `results/weak_search_candidate_metrics_20260510/ifs_transform_copy_surface_metrics_occ64.csv`

关键观察：

- `ifs_transform_copy_proxy` 是当前最严格的 IFS branch/tree 语义候选，因为它确实来自 transform-copy branch grammar；但视觉像软 blob，不能进主文正例。指标上 r0 有 94 components，LCR 0.976，r1 后单连通。
- `cache_radial_transform_fusion` 比 `transform_radial4_pyrite/bismuth/gear` 更连通，r0 LCR 0.998，但视觉更像体素地形/晶体块，不像干净 radial ornament。
- `coral_density_0p25_octopus` 是当前 DLA/coral 线最好的替代候选：r0/r1/r2 均单连通，视觉比高密度 coral 更开阔，但仍有 voxel/bead 感。
- `bismuth_hopper_pyrite_hq` 是最好的晶体/ordered-growth 候选：r0 两个 component、LCR 0.9996，r1 单连通；适合作 ordered crystal/lattice，不适合作 stochastic DLA。
- `dla_side_octopus` 更接近 frontier-side mode，但视觉碎片明显，仍只能是 boundary。

V2 配对图：

- `visuals/strict_matched_pair_candidates_v2_20260510/strict_matched_pair_candidates_v2_contact_20260510.png`
- `visuals/strict_matched_pair_candidates_v2_20260510/matched_pair_v2_manifest.csv`

V2 的主文候选判断：

| task | current best | status |
|---|---|---|
| `lsys_climbing_vine_d6` | `vine_stage5` | paper candidate |
| `sc_tree_crown_260` | `tree_compete_s3` | paper candidate |
| `sc_root_network_260` | `vine_stage5` | paper candidate |
| `ifs_fractal_lattice_d4` | `pyrite_stage4` | paper candidate |
| `dla_coral_cluster_900` | `coral_density_0p25_octopus` | connected but visual boundary |
| `dla_aniso_crystal_800` | `bismuth_hopper_pyrite_hq` | ordered crystal boundary |
| `ifs_branch_tree_d6` | `ifs_transform_copy_proxy` | mode-matched but low visual quality |
| `ifs_radial_ornament_o8_d4` | `cache_radial_transform_fusion` | more connected, but not clean ornament |

## 6. 追加：blocky naturalization / repair pilot

CPU pilot：

- `assets/naturalize_blocky_mesh_pilot_20260510.py`
- `tests/test_naturalize_blocky_mesh_pilot_20260510.py`
- `docs/evaluation/naturalize_blocky_mesh_pilot_zh_20260510.md`
- `visuals/naturalize_blocky_mesh_pilot_20260510/before_after_contact_sheet.png`

结论：

- 该 pilot 对 radial/transform fragmentation 有诊断价值，例如 `transform_radial4_pyrite` 的 occupancy components 从 118 降到 8，但表面积膨胀到 6.23x，视觉上像被厚壳填满，不能作为主文正例。
- 对 DLA/coral，许多输入在 dilation 后已经单连通，所以它更多是平滑/重建，不是 connectivity repair 证据。
- 后续如果纳入方法，应改成 masked/local，而不是全局 closing：只处理小组件、接触缝、低置信边界，并加入面积/体积/骨架保护阈值。

验证：

- `python3 -m pytest tests/test_naturalize_blocky_mesh_pilot_20260510.py -q` -> `2 passed`
- `python3 -m pytest scripts/figures/test_matched_camera_zoom_render_20260510.py -q` -> `2 passed`

## 7. Paper / Overleaf 同步状态

已将旧 loose screening 图替换为 strict matched V2 candidate 图，并保留 mode-matched boundary 图：

- `paper_siga/figures/strict_matched_pair_candidates_v2_20260510.png`
- `paper_siga/figures/strict_mode_matched_boundary_candidates_20260510.png`

Overleaf 已更新：

- commit `5c3de24 Update strict matched candidates to v2`
- push target: `overleaf master`

注意：当前 shell 仍找不到 `latexmk/pdflatex/tectonic`，因此本地没有编译 PDF；已做 `git diff --check` 与相关脚本测试。
