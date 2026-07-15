---
title: 可视化补充 VineD5 与 Crystal Guide Sweep
date: 2026-05-09
tags:
  - recursive-3d-growth
  - trellis2
  - visualization
  - paper
---

# 可视化补充：Vine D5 与 Crystal Guide Sweep

## Vine D5

本轮补齐了一个重要缺口：之前指标经常引用 `vine_d5_projected_compete`，但主文较清晰的 textured depth strip 只有 `d=1..4`。现在对同一个 depth-5 projected vine mesh 做了 4 个 public guide 的 Trellis2 textured GLB export。

最重要结论：

- 四个结果都在 occupancy-primary proxy 下单连通：`Comp=1, LCR=1.000`。
- `parthenocissus_square` 和 `parthenocissus_warm` 视觉最稳，可作为 depth-5 textured closure。
- `parthenocissus_edge` 偏绿，适合展示外观 guide 敏感性。
- `tree_roots_square` 是材质备选，不是新几何 case。

对应文件：

- QA 图：`paper_siga/figures/vine_stage5_guide_sweep_20260509.png`
- 指标：`results/vine_stage5_guide_sweep_metrics_20260509/metrics.csv`
- 详细 QA：`docs/visuals/vine_stage5_guide_sweep_qa_zh_20260509.md`

论文中必须保守写：这是 depth-5 visual/export closure，不是 ablation，也不是 raw mesh topology clean proof。

## Crystal Guide Sweep

本轮也测试了两个已连通的 crystal-inspired stage-4 scaffold：bismuth hopper 与 pyrite lattice。

最重要结论：

- 四个结果在 occupancy-primary proxy 下都是 `Comp=1, LCR=1.000`。
- `bismuth_warm` 视觉最好，可作为非树/晶体启发 scaffold 的 supporting candidate。
- `bismuth_edge` 太白，像白模。
- `pyrite_warm` 可放 supplement；`pyrite_edge` 偏灰，主图价值不高。

对应文件：

- QA 图：`paper_siga/figures/crystal_stage4_guide_sweep_20260509.png`
- 指标：`results/crystal_stage4_guide_sweep_metrics_20260509/metrics.csv`
- 详细 QA：`docs/visuals/crystal_stage4_guide_sweep_qa_zh_20260509.md`

论文中必须保守写：这些是 crystal-inspired connected scaffolds，不是物理晶体生长模拟，也不是 raw GLB face topology clean proof。

## 总体判断

这两批补充的实际价值：

1. Vine D5 是主线正向补强，值得进入 supplement，甚至可在主文短提。
2. Bismuth warm 是非树类 supporting positive，可以帮助扩展“只会做树/藤蔓”的风险。
3. Pyrite 仍偏 supporting/gallery，不建议主文核心。
4. 所有结果继续遵守当前论文边界：结构主张基于 occupancy-connected projected support；texture/PBR 主张基于 selected GLB export compatibility。
