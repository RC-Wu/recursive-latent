# Cache-Selected Texture 复测 QA（2026-05-09 15:30）

## 目的

用户要求继续推进 cache / latent / transform / sampler 相关方向，看看能不能解决 DLA/非树碎块，并增强“使用 Trellis2 稀疏体素/缓存结构”的论文故事。本次复测把四个 cache-selected support 直接送入 Trellis2 texture/PBR export，检查是否能成为可用 textured mesh asset。

## 文件

- 远端结果：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/cache_selected_texture_20260509_rerun1516`
- 本地结果：`visuals/cache_selected_texture_20260509_rerun1516`
- 渲染：`visuals/cache_selected_texture_20260509_rerun1516/renders`
- contact sheet：`visuals/cache_selected_texture_20260509_rerun1516/renders/cache_selected_rerun1516_contact.png`
- vertex occupancy metrics：`visuals/cache_selected_texture_20260509_rerun1516/metrics_occ64.{csv,json}`
- surface metrics：`visuals/cache_selected_texture_20260509_rerun1516/surface_metrics_occ64.{csv,json}`

## 视觉结果

![Cache selected texture smoke](/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/cache_selected_texture_20260509_rerun1516/renders/cache_selected_rerun1516_contact.png)

## 指标解释

普通 vertex-occupancy 指标对这些 textured GLB 明显过于悲观，LCR 都接近 0，因为 GLB 顶点和 seam 结构让 vertex voxelization 变成大量小岛。用 surface-sampled voxel metric 更合理：

| case | surface r0 comps/LCR | surface r1 comps/LCR | 视觉判断 |
|---|---:|---:|---|
| cache DLA masked | `7 / 0.997` | `1 / 1.000` | support 基本可读，但语义弱，像块状柱体 |
| cache radial fusion | `18 / 1.000` | `1 / 1.000` | support 可读，但整体过于块状 |
| cache bismuth fusion | `14 / 0.729` | `4 / 0.701` | 失败，不作为正例 |
| cache scifi connected | `54 / 0.979` | `1 / 1.000` | support 可能可读，但视觉仍偏块状/语义混乱 |

## 结论

- Cache-selected support 并不是完全没希望：DLA/radial/scifi 在 surface metric 下不是严重碎块。
- 但这批视觉太像 blocky monolith，递归语义不清楚，不能作为主文正例。
- Bismuth cache fusion 仍然失败，不能用。
- 当前最稳主线仍然是 grammar-native connected scaffold + Trellis2 texture/PBR，而不是 post-hoc cache repair。

## 论文用法

可以写进 supplement 或方法边界：

- cache/latent support 可以作为未来增强方向；
- 现有 cache-selected repair 能改善部分 support metrics，但还不能稳定带来语义清楚、视觉漂亮的 recursive asset；
- 这反过来支持 PS-RSLG 中 attachment-aware grammar 和 per-depth projection 的必要性。

不建议放主结果图。
