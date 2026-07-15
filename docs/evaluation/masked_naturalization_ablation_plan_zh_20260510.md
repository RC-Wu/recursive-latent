# 局部 masked naturalization 主文消融计划 2026-05-10

## 结论先行

`masked local naturalization` 应该作为方法的一小节和主文消融来做，但 claim 必须保守：它不是全局拓扑修复器，而是在 grammar/projection 已经给出可连接编辑区域后，对局部表面、边界和材质做自然化，同时硬约束 anchor/root 不漂移。

因此主文要证明两件事：

1. 和 rule-only/per-depth projection 相比，它提升局部表面观感、减少体素块感或边界硬接痕。
2. 和 global flow/full repair 相比，它不洗掉递归拓扑、不移动 anchor、不引入大量 orphan fragments。

## 推荐消融列

| 列 | 名称 | 目的 | 预期 |
|---|---|---|---|
| A | Rule-only / no-N | grammar + projection，无生成采样 | 拓扑最稳，但表面硬、块感强 |
| B | Weak blend | 只做低强度 feature/material blend，例如 alpha=0.25/0.5 | 轻微改善，但边界自然化有限 |
| C | Masked-N + hard clamp | 主方法：只在可编辑 mask 内采样，anchor/root hard-clamp | 表面更自然，拓扑保持 |
| D | Masked-N no-projection | 分离 masking 和 per-depth projection 的贡献 | 可能局部好但递归状态不稳 |
| E | Global-N / full repair | 负例：整物体 flow/repair | 可能局部漂亮，但拓扑/语义漂移 |
| F | Final-only cleanup + N | 负例：最后清理 | 证明 final-only 无法阻止中间碎片作为下一层 handle |

主文图建议放 A/B/C/E 四列，D/F 放补充或表格。这样图不拥挤，同时保留最关键对照。

## 指标

### 1. 拓扑与连接性

- `occupancy_component_count_6n`
- `largest_occupancy_component_ratio_6n`
- `root_component_ratio`
- `orphan_mass_ratio`
- `path_to_root_rate`
- `orphan_tip_count`
- `component_growth_by_depth`
- `projection_survival_ratio`
- `deleted_mass`
- `bridge_mass_ratio`，仅对 bridge/connectivity completion 变体使用

这些是主 claim 的硬指标。尤其是 `root_component_ratio` 和 `orphan_mass_ratio` 比单纯 component count 更适合解释递归状态污染。

### 2. 局部保持与 mask 泄漏

- `anchor_drift`: hard-clamped anchor 的位置/Chamfer/IoU 变化。
- `mask_leakage`: mask 外发生变化的 token/vertex/voxel 比例。
- `edit_region_change`: mask 内变化强度。
- `handle_survival`: 原有 active handles 是否仍可寻址。
- `tip_survival`: terminal tips 是否消失。

这组指标直接支撑“局部生成模型采样被 grammar 约束住”这一 claim。

### 3. Mesh 质量

- raw face components / LCR。
- welded face components / LCR。
- surface-voxel r0/r1/r2 components / LCR。
- non-manifold edges。
- degenerate faces。
- normal consistency。
- triangle aspect ratio。
- render success / Blender import success。

解释时要分层：occupancy/root-reachability 是结构指标，mesh/face 是资产质量诊断，不能混在一起。

### 4. 自然度/视觉指标

用于支持但不作为唯一 claim：

- 多视角 CLIP score 到类别 prompt，例如 `recursive vine root`, `organic coral cluster`, `pyrite crystal lattice`。
- 多视角 CLIP negative score 或差值，例如和 `blocky voxel cubes`, `broken fragments` 比。
- DINO/CLIP multi-view feature consistency，用于测 zoom 或同一资产不同视角一致性。
- 人工 QA 标签：`naturalized_boundary`, `anchor_preserved`, `washed_out`, `surface_soup`, `fake_bridge`, `blocky_voxel`, `main_paper_candidate`。

不建议把 GPT 评分作为当前主文主指标；可留给补充或内部筛选。

## 推荐 case

### 主文正例

- `vine_d5_projected_compete` / `vine_stage5_warm`：最稳定，视觉也已经可接受。
- `pyrite_lattice_depth` / `pyrite_lattice_hq`：适合 transform/symmetry 叙事。
- `coral_octopus_hq` 或 `volumetric_coral_depth`：非树 stress case，必须先通过连接性和 zoom QA。

### 边界/负例

- `hard_dla`：目前只适合展示 global repair / fake bridge / 碎片边界，不能当主正例。
- `bismuth`：可以作为 pyrite 的对照，说明并非所有晶体/重复结构都适合主 grammar operator。
- aggressive fork/radial/echo：用于 stability-expression boundary。

## 图表设计

### 主文图：Masked Local Naturalization Ablation

- 行：`vine`, `coral`, `pyrite`。
- 列：`rule-only`, `weak blend`, `masked local`, `global repair`。
- 每个 cell：白底 mesh/PBR render + 一个局部 zoom inset。
- 每行右侧或图下方放小指标：
  - `Occ: comp/LCR`
  - `Root: root ratio`
  - `Orphan: orphan mass`
  - `Leak: mask leakage`
  - `Visual: pass/fail`

### 表：自然化指标

| case | variant | occ comp | LCR | root ratio | orphan mass | anchor drift | mask leak | surface r1 comp | CLIP category | verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|

### 补充图

- `alpha x mask_radius` heatmap。
- global-N washout failure。
- masked-N no-projection failure。
- hard-DLA fake bridge failure。

## 可复用文件与脚本

- 旧消融需求：`paper_siga/drafts/strict_revision_section_rewrites_20260509.tex`
- connectivity 方法：`paper_siga/drafts/connectivity_method_section_20260509.tex`
- mesh 指标脚本：`assets/mesh_quality_metrics.py`
- GLB surface 指标：`assets/surface_voxel_connectivity_20260509.py`
- branch/root 指标：`assets/branch_path_metrics_20260509.py`
- 现成 projection zoom 组合图脚本：`scripts/figures/compose_projection_ablation_pure_white_zoom_20260509.py`
- flow/SDE 初步指标：`results/flow_sde_naturalization_metrics_20260510_0008`

## 下一步执行顺序

1. 先在已有结果上构建指标表，不重跑昂贵 Trellis2。
2. 选 `vine`, `pyrite`, `coral` 三个 case 做白底 zoom 消融图。
3. 若已有结果缺少某列，再用 a100-2 GPU 4/5/6/7 补跑对应变体。
4. 将主文 claim 写成：“masked local naturalization improves local realization under hard recursive-state constraints”，不要写成“修复所有碎片”。
