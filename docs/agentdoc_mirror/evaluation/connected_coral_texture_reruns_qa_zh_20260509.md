---
title: Connected / Coral 纹理批量复测 QA
date: 2026-05-09
tags:
  - recursive-growth
  - trellis2
  - mesh-connectivity
  - textured-mesh
---

# Connected / Coral 纹理批量复测 QA（2026-05-09 16:10）

## 本轮结论

这一轮优先回答用户指出的“DLA / crystal / root / non-tree 不允许碎块化，必须能成为可用 asset”的问题。当前最有价值的正例不是 post-hoc bridge，也不是单纯换 guide 的 coral sweep，而是 `connected_best_expansion_texture_20260509_rerun1544` 这组 grammar-native connected scaffold。

## `connected_best_expansion_texture_20260509_rerun1544`

本地路径：

- GLB 与 summary：`visuals/connected_best_expansion_texture_20260509_rerun1544`
- Blender 渲染：`visuals/connected_best_expansion_texture_20260509_rerun1544/renders`
- contact sheet：`visuals/connected_best_expansion_texture_20260509_rerun1544/renders/connected_best_expansion_contact_20260509.png`
- surface 指标：`visuals/connected_best_expansion_texture_20260509_rerun1544/surface_metrics_occ64.{csv,json}`

Surface-voxel 指标（occ64）：

| case | strict comps / LCR | radius-1 comps / LCR | 判断 |
| --- | ---: | ---: | --- |
| `connected_root_vine_parthenocissus` | `1 / 1.000` | `1 / 1.000` | 连通性好，但视觉规模偏小，暂不作为头图正例。 |
| `connected_scifi_gear` | `1 / 1.000` | `1 / 1.000` | 连通性好，机械语义明确度中等，可作非植物对照或补充。 |
| `connected_pyrite_bismuth` | `1 / 1.000` | `1 / 1.000` | 当前最强非植物/晶体正例之一，纹理/PBR 与 cube lattice 结构匹配。 |
| `connected_porous_octopus` | `3 / 0.993` | `1 / 1.000` | 近似连通，视觉可用但 octopus guide 语义偏软，可作 porous/organic 候选。 |

人工视觉判断：

- `connected_pyrite_bismuth` 最适合继续进入论文主结果或拓展应用图；
- `connected_porous_octopus` 比之前碎块 DLA 更可用，但应避免把它解释成严格物理 DLA，只能说是 porous/organic connected scaffold；
- `connected_scifi_gear` 在连通性上好，但画面语言不够“递归优势”，需要更好的 guide 或更显式的多尺度细节；
- `connected_root_vine_parthenocissus` 可作为小规模对照，但不是主视觉。

## `coral_stage4_guide_sweep_20260509_rerun1533`

本地路径：

- GLB 与 summary：`visuals/coral_stage4_guide_sweep_20260509_rerun1533`
- Blender 渲染：`visuals/coral_stage4_guide_sweep_20260509_rerun1533/renders`
- contact sheet：`visuals/coral_stage4_guide_sweep_20260509_rerun1533/renders/coral_stage4_guide_sweep_contact_20260509.png`
- surface 指标：`visuals/coral_stage4_guide_sweep_20260509_rerun1533/surface_metrics_occ64.{csv,json}`

Surface-voxel 指标：四个 guide 版本全为 strict `1 / 1.000`，因为它们共享同一个 connected coral scaffold，只改变 public guide 诱导的纹理/PBR。

人工视觉判断：

- 这是有用的 texture-guide sweep，不是几何正例；
- bismuth/pyrite guide 的材质更可控，octopus guide 的语义偏怪；
- 论文中适合用来说明“同一连通 scaffold 可通过 Trellis2 texture/PBR route 产生不同外观”，不适合作为递归几何贡献主证据。

## 对论文 claim 的影响

可支持的 claim：

1. PS-RSLG 的 connected scaffold route 能把非树、晶体、porous、mechanical 几类结果保持为可渲染连通 mesh。
2. Trellis2 的 texture/PBR export 可以作为生成式自然化模块，而不是只做单色 mesh。
3. surface-voxel connectivity 比 vertex/face island 更适合评价当前 GLB renderability，但不能替代 watertight topology 指标。

需要避免的 claim：

- 不应声称 post-hoc bridge 已解决 DLA 碎块问题；
- 不应声称 coral guide sweep 改变了几何递归；
- 不应把 `porous_octopus` 解释成高保真生物或物理 coral，只能作为 connected organic/porous asset 候选。

## 下一步

1. 拉取并 QA `traditional_baseline_texture_20260509_rerun1554`，形成传统方法同贴图对照。
2. 拉取少量 `vine_stage5_guide_sweep_20260509_rerun1557` 的最优 GLB 或先远端生成低成本截图，避免 100MB 级传输堵塞本地。
3. 对 `connected_pyrite_bismuth` 和 `connected_porous_octopus` 做多尺度 zoom-in 渲染，验证局部细节在论文图中是否站得住。
4. 若后续要写进主文，优先把 `connected_pyrite_bismuth` 和 Pyrite depth HQ 合并为晶体/对称性正例线。
