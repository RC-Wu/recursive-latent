# Bismuth scaffold + pyrite guide cross-guide QA

时间：2026-05-09 18:04 +08

## 结论

`crystal_depth_hq_bismuth_pyrite_crossguide_20260509_rerun1755` 是一组完整的同几何、换 guide 的材质鲁棒性实验：使用同一套 `bismuth_hopper_depth` connected scaffold，但把 guide 从 bismuth 改成 `pyrite_cubes_warm.png`，steps `8`，texture size `2048`。

本地结果完整：四个 Trellis2 textured GLB 全部拉回，完成 Blender render、surface-voxel 指标和 contact sheet。视觉上相比 `bismuth_depth_textured_showcase_20260509_rerun1729` 更偏暖金色，少了之前明显的绿色偏色，作为“crystal-like / mineral-like recursive scaffold” 展示更稳。

## 视觉证据

- contact sheet: `visuals/crystal_depth_hq_bismuth_pyrite_crossguide_20260509_rerun1755/bismuth_pyrite_crossguide_depth_contact_20260509.png`
- renders: `visuals/crystal_depth_hq_bismuth_pyrite_crossguide_20260509_rerun1755/renders_depth/stage{01,02,03,04}_iso.png`
- paper figure candidate:
  - `paper_siga/figures/bismuth_pyrite_crossguide_depth_rerun1755_20260509.png`
  - `paper_siga/figures/bismuth_pyrite_crossguide_depth_rerun1755_20260509.pdf`

## 指标

来源：`visuals/crystal_depth_hq_bismuth_pyrite_crossguide_20260509_rerun1755/surface_metrics_occ64.csv`

| stage | vertices | faces | occupied @64 | comp r0 | LCR r0 | comp r1 | LCR r1 | comp r2 | LCR r2 | box dim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 01 | 37,696 | 44,592 | 14,300 | 1 | 1.000 | 1 | 1.000 | 1 | 1.000 | 2.037 |
| 02 | 39,679 | 46,980 | 15,117 | 1 | 1.000 | 1 | 1.000 | 1 | 1.000 | 2.038 |
| 03 | 43,399 | 50,436 | 16,297 | 1 | 1.000 | 1 | 1.000 | 1 | 1.000 | 2.032 |
| 04 | 47,055 | 54,036 | 17,460 | 1 | 1.000 | 1 | 1.000 | 1 | 1.000 | 2.029 |

## 解释

这组实验有两个用途：

1. **主文/补充图候选**：它比绿色 bismuth guide 版本更像金属/矿物 recursive asset，可以替代 `bismuth_depth_textured_showcase_20260509_rerun1729` 的 contact sheet。
2. **方法论证据**：同一 connected scaffold 换 guide 后保持相同连通性指标，说明 material guide 主要改变外观，不改变 PS-RSLG 的 connected support claim。

## Caveat

这不是物理晶体生长，也不是严格晶体学模型。应写为 `crystal-like connected recursive scaffold` 或 `mineral-inspired recursive asset`。如果进入论文，caption 中应强调 same scaffold / different material guide / connectivity preserved，而不是“真实黄铁矿或铋晶体生成”。
