---
title: 最新 occupancy-positive textured GLB 的本地 mesh 指标
date: 2026-05-09
project: recursive_3d_generative_growth
status: current
---

# 最新 occupancy-positive textured GLB 的本地 mesh 指标

## 结论

本次检查对象是 `texture_latest_occupancy_positive_ralph_20260509_233723` 中的三个 Trellis2 textured GLB：bismuth depth-4、pyrite depth-4、coral stage-4。渲染已按纯白背景、无平台、无地面边界完成。

关键结论：

- `bismuth_depth4` 和 `pyrite_depth4` 可以作为当前非树 / 晶体 / 机械结构的主要 textured candidate：二者在 96 分辨率 vertex-voxel occupancy 下都是 1 个 6-neighborhood 连通分量，LCR 为 1.0。
- 这两个 case 的 raw face components 极碎，但 1e-4 quantized welding 后都变成 3 个 welded components，最大 welded component LCR 分别约 0.994 和 0.990。因此论文里必须写成 occupancy-primary connected scaffold，而不能写成 raw mesh topology clean。
- `coral_stage4` 在这次本地 textured GLB 指标中没有维持完全 occupancy-connected：occupancy components = 3，LCR = 0.883；welded face components = 3，LCR = 0.893。它可以保留为视觉/边界候选，但不应作为当前 connectivity 正例。

## 文件路径

- 渲染目录：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/texture_latest_occupancy_positive_ralph_20260509_233723/pure_white_render_2348`
- 临时 QA contact sheet：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/texture_latest_occupancy_positive_ralph_20260509_233723/pure_white_render_2348/texture_latest_occpos_contact_pure_white_20260509.png`
- 论文风格 contact sheet：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/texture_latest_occpos_paperstyle_contact_20260509.png`
- 指标 CSV：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/texture_latest_occpos_mesh_metrics_20260509/texture_latest_occpos_mesh_metrics.csv`
- 指标 JSON：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/texture_latest_occpos_mesh_metrics_20260509/texture_latest_occpos_mesh_metrics.json`

## 指标表

| case | vertices | faces | raw face comps | welded comps | welded LCR | occ comps 6n | occ LCR 6n | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| bismuth depth-4 | 1,058,557 | 1,799,892 | 9,856 | 3 | 0.9938 | 1 | 1.0000 | main non-tree textured candidate, occupancy-primary |
| pyrite depth-4 | 1,605,352 | 2,015,398 | 80,156 | 3 | 0.9897 | 1 | 1.0000 | main crystal/transform-copy textured candidate, occupancy-primary |
| coral stage-4 | 573,444 | 676,808 | 31,154 | 3 | 0.8927 | 3 | 0.8831 | boundary/visual candidate, not current connectivity positive |

## 写进论文时的措辞

建议措辞：

> Selected projected sparse-latent assets can be exported through the frozen Trellis2 texture path and remain connected under occupancy-primary support metrics. Raw face components are reported separately as mesh diagnostics, since GLB export and material seams can fragment triangle connectivity even when the voxelized support is connected.

不要写：

> These cases produce clean watertight meshes.

也不要把 texture/PBR 当作 topology proof。texture/PBR 只说明 asset export compatibility。
