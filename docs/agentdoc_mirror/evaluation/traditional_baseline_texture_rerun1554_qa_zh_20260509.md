---
title: Traditional Baseline Texture Rerun QA
date: 2026-05-09
tags:
  - recursive-growth
  - baseline
  - textured-mesh
---

# Traditional Baseline Texture Rerun QA（2026-05-09 16:35）

## 产物

- 远端：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/traditional_baseline_texture_20260509_rerun1554`
- 本地：`visuals/traditional_baseline_texture_20260509_rerun1554`
- 渲染：`visuals/traditional_baseline_texture_20260509_rerun1554/renders`
- contact sheet：`visuals/traditional_baseline_texture_20260509_rerun1554/renders/traditional_baseline_texture_contact_20260509.png`
- surface metrics：`visuals/traditional_baseline_texture_20260509_rerun1554/surface_metrics_occ64.{csv,json}`

## 指标

| baseline | strict comps / LCR | radius-1 comps / LCR | 备注 |
| --- | ---: | ---: | --- |
| `sc_root_vine` | `2 / 0.9999` | `1 / 1.000` | 基本连通，树根结构密集但缺少生成式局部自然化层次。 |
| `sc_tree_canopy` | `1 / 1.000` | `1 / 1.000` | 连通性好，可作为传统 space colonization 正例 baseline。 |
| `lsystem_branch` | `2 / 0.9999` | `1 / 1.000` | 结构明确但风格偏传统枝状，和 PS-RSLG 的纹理/PBR能力可做对比。 |
| `dla_cluster` | `4 / 0.9998` | `1 / 1.000` | 表面近似连通，但视觉是块状簇，难以作为高质量 asset。 |

## 人工视觉判断

- 传统方法经过同一 Trellis2 texture route 后也能得到可渲染 textured mesh，因此 baseline 是公平的：视觉差距主要来自几何 grammar / scaffold，而不是单纯材质。
- `sc_tree_canopy` 和 `lsystem_branch` 是合理 baseline；它们有清楚传统结构，但缺少当前方法希望展示的多尺度体素递归和生成式自然化。
- `dla_cluster` 是很好的负例：虽然 radius-1 surface metric 可连通，但视觉上仍是块状簇，不够自然、不够 asset-ready。

## 论文使用建议

实验部分可以把传统 baseline 和 PS-RSLG 分开讲：

1. 传统 baseline：给出同一 texture/PBR route 下的结果，证明不是只靠上色取胜。
2. PS-RSLG 正例：展示 connected scaffold 下的 crystal/porous/non-tree 结果，强调递归表达与可用 mesh 连通性。
3. 指标：surface-voxel LCR 作为 renderability connectivity；配合视觉图证明传统 DLA 即使 metric 接近连通，也仍在视觉/语义上不足。
