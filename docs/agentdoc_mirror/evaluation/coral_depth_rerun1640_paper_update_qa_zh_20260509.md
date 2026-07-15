---
title: Coral Depth Rerun 1640 与论文更新 QA
date: 2026-05-09
tags:
  - recursive-growth
  - trellis2
  - coral-depth
  - paper-update
---

# Coral Depth Rerun 1640 与论文更新 QA（2026-05-09 16:55）

## 完成内容

- 远端批次：`coral_depth_texture_showcase_20260509_rerun1640`
- 本地 GLB：`visuals/coral_depth_texture_showcase_20260509_rerun1640`
- Blender preserve-material renders：`visuals/coral_depth_texture_showcase_20260509_rerun1640/renders`
- Surface metrics：`visuals/coral_depth_texture_showcase_20260509_rerun1640/surface_metrics_occ64.{csv,json}`
- 新论文图：
  - `paper_siga/figures/coral_depth_textured_showcase_rerun1640_20260509.{png,pdf}`
  - `paper_siga/figures/traditional_baseline_texture_rerun1554_20260509.{png,pdf}`
  - `paper_siga/figures/connected_best_expansion_texture_rerun1544_20260509.{png,pdf}`

## Surface-voxel 结果

这次 coral depth rerun 比早先版本更干净。四个 stage 在 occ64 strict surface-voxel 诊断下全部为：

| stage | strict components | strict LCR | radius-1 components | radius-1 LCR |
| --- | ---: | ---: | ---: | ---: |
| 1 | 1 | 1.000 | 1 | 1.000 |
| 2 | 1 | 1.000 | 1 | 1.000 |
| 3 | 1 | 1.000 | 1 | 1.000 |
| 4 | 1 | 1.000 | 1 | 1.000 |

## 视觉 QA

- 这组图能够清楚展示 coral / DLA-inspired connected scaffold 随 depth 增长的趋势。
- 语义上仍应称作 `coral/DLA-inspired connected scaffold`，不能写成物理 DLA。
- stage 4 与之前 coral guide sweep 的几何相同，但这组 depth 图更适合主文说明方法行为。

## 论文更新

`paper_siga/main.tex` 已更新：

1. baseline 段落改成更公平的表述：传统方法也能走 Trellis2 texture/PBR route，不再把传统 baseline 写成弱 strawman；
2. 注释掉较旧的 matched-guide texture diagnostic figure block；
3. 将 latest traditional baseline rerun 图接入 `fig:traditional-texture-baseline`；
4. 新增 `fig:connected-best-expansion-textured`；
5. 将 `fig:coral-depth-textured` 替换为 rerun1640 版本，并更新 caption 为四个 stage 全 strict connected；
6. 编译成功：`paper_siga/main.pdf`，当前 25 页。

剩余 LaTeX 警告主要是浮动体拥挤、图片 alt text、ACM metadata/reference style，不是硬错误。仍有一个旧图 `depth_parameter_mesh_showcase_zoom_20260509.pdf` 轻微超页，需要后续压缩或移 supplement。

## 对论文 claim 的影响

这次更新加强了两点：

- non-tree / coral-inspired depth progression 可以作为正面 connected-scaffold 证据，而不只是边界 case；
- traditional baseline 的叙述更严谨，避免 reviewer 认为我们故意选择弱 baseline 或混淆材质优势与几何优势。

下一步应该优先压缩主文 figure 数量，把长 gallery 移 supplement，并将主文 evidence chain 收束为：

1. PS-RSLG formal grammar；
2. per-depth projection ablation；
3. connected scaffold positive cases；
4. same-route traditional baseline；
5. selected Trellis2 textured GLB/PBR asset readiness。
