# 传统方法一对一 baseline 评估计划 2026-05-10

## 目标

用户要求从 `case_gallery_for_user_20260509/06_baselines_metrics_ablation` 中挑选能进入论文对比的传统方法 case，并用我们的 PS-RSLG 生成同类别、可直接比较的结果。最终比较必须是 mesh/GLB/PBR 渲染，不使用点云或 matplotlib 图。

## 选定 baseline 短名单

### 1. L-system：branch/vine/root

传统 baseline：

- Render: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_baseline_texture_matched_guide_20260509/renders/lsystem_branch_iso.png`
- GLB: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_baseline_texture_matched_guide_20260509/lsystem_branch_matched_steps6_tex1024_xformers/textured.glb`

我们的候选：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/standard_pure_white_selected_textured_20260509/renders_flat/vine_stage5_warm_iso.png`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/projection_ablation_blender_mesh_20260509/renders_pure_white_flat_rerun2105/vine_per_depth_front.png`

推荐比较任务：

- `branching / recursive vine`
- `procedural L-system branch` vs `projection-stabilized sparse-latent vine`

注意：L-system 在结构控制上很强，不应当写成弱 baseline。优势应放在 textured/PBR asset readiness、局部自然化、多尺度 zoom 细节和同一 grammar 框架可扩展性。

### 2. Space colonization：tree canopy / root network

传统 baseline 主例：

- Render: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_baseline_texture_20260509_rerun1554/renders/sc_tree_canopy_iso.png`
- GLB: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_baseline_texture_20260509_rerun1554/sc_tree_canopy_steps6_tex1024_xformers/textured.glb`

传统 baseline 辅例：

- `sc_root_vine` in `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_baseline_texture_20260509_rerun1554/`

我们的候选：

- `vine_stage5_warm`
- same-root `proposed_connected/vine` from `results/baseline_matrix_20260509`

推荐比较任务：

- `tree canopy / attractor coverage`
- `root-vine / space competition`

写法：space colonization 的强项是 attractor coverage 和 branch structure，我们的优势是同样能表达 space competition，但额外进入生成模型本地 sparse state、支持 texture/PBR 和 masked naturalization。

### 3. DLA/frontier：coral / porous cluster

传统 baseline：

- Render: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_baseline_texture_20260509_rerun1554/renders/dla_cluster_iso.png`
- GLB: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_baseline_texture_20260509_rerun1554/dla_cluster_steps6_tex1024_xformers/textured.glb`

我们的候选：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/standard_pure_white_selected_textured_20260509/renders_flat/coral_octopus_hq_iso.png`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/coral_depth_texture_showcase_20260509_rerun1640/renders/stage04_iso.png`

推荐比较任务：

- `DLA/coral-inspired frontier accretion`
- `connected coral scaffold`

注意：DLA 是当前压力线，不应过度承诺。可以展示传统 DLA 结构和我们的 coral-inspired connected scaffold，但必须明确：这不是物理 DLA 复现，而是 frontier/attachment rule family 的资产生成对比。

### 4. IFS/fractal/symmetry：transform-copy / lattice

传统 baseline：

- Render: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_baseline_texture_matched_guide_20260509/renders/ifs_branch_tree_iso.png`
- GLB: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_baseline_texture_matched_guide_20260509/ifs_branch_tree_matched_steps6_tex1024_xformers/textured.glb`

我们的候选：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/standard_pure_white_selected_textured_20260509/renders_flat/pyrite_lattice_hq_iso.png`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/texture_latest_occupancy_positive_ralph_20260509_233723/pure_white_render_2348/flat/pyrite_depth4_iso.png`

推荐比较任务：

- `transform-copy lattice`
- `IFS-like recursive motif`

写法：IFS 是 strict transform-copy/self-similarity baseline；pyrite lattice 是我们 transform-copy grammar 的正例，用来说明 transform diagnostics 能指导可接受的 operator family。

## 指标组合

### 硬指标

- `occ_comp_6n`
- `occ_lcr_6n`
- `root_component_ratio`
- `orphan_mass_ratio`
- `path_to_root_rate`
- `orphan_tip_count`
- `tip_count`
- `branch_nodes`
- `mesh_component_count`
- `surface_voxel_r0/r1/r2`
- `nonmanifold_edges`
- `degenerate_faces`
- `vertices/faces/tokens`
- runtime / peak memory / export time

### 类别特定指标

- L-system/space colonization：branch angle distribution, branch length distribution, tip survival, attractor coverage。
- DLA/coral：cavity/porosity proxy, bridge cost, frontier attachment survival, fragment count。
- IFS/pyrite：transform orbit error, symmetry IoU, zoom self-similarity, facet/contact consistency。

### 视觉指标

- 多视角 CLIP category score。
- CLIP negative prompt gap：positive prompt minus `blocky voxel fragments` / `broken floating pieces`。
- DINO/CLIP zoom consistency。
- 人工 QA 标签，不作为主数值指标。

## 五列 protocol 解释

| 列 | 内容 | 论文意义 |
|---|---|---|
| 1 | Classical baseline | 原始传统算法，展示领域标准和结构控制 |
| 2 | Direct sparse grammar | 我们的 rule proposal 不做 projection/naturalization，展示碎片传播失败 |
| 3 | Final-only cleanup/projection | 只在最后清理，证明太晚 |
| 4 | Per-depth projection | 我们的结构核心，递归状态稳定 |
| 5 | Full PS-RSLG | per-depth projection + masked local naturalization + texture/PBR，展示最终资产 |

这五列不是每个任务都必须全进主文图。主文可以选 3-4 列，完整五列放表格或补充。

## 白底多级 zoom 图要求

最终对比图必须重新渲染：

- RGB 255 白底。
- 无平台、无阴影地平线、无 in-image 大标签。
- 固定 orthographic camera，同类别 pair 使用相近尺度和视角。
- overview 图中用矩形框标出 zoom 区域。
- zoom panel 至少包含：
  - root/seed attachment；
  - primary junction/contact；
  - terminal tip/frontier；
  - DLA/IFS/crystal 额外加 facet/cavity/symmetry-contact。

现有渲染用于挑选，不一定满足最终论文格式，需要重渲。

## 推荐进入主文的最小组合

1. L-system branch vs ours vine。
2. Space-colonization tree/root vs ours space-competition vine/root。
3. DLA cluster vs ours coral-inspired connected scaffold。
4. IFS branch/tree vs ours pyrite lattice。

如果页数紧张，DLA 放成边界/压力行，主文正例保留 L-system、space colonization、pyrite。
