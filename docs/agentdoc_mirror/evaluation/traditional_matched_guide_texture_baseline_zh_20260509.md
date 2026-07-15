# Traditional baselines matched-guide texture diagnostic

更新时间：2026-05-09 08:33 +08

## 目的

上一组 traditional baseline texture diagnostic 使用了不同 guide，因此只能说明“texture path 可用但仍碎”。这一组更严格：四个传统 baseline 都使用同一个 `parthenocissus_tendrils_square.png` guide、相同 Trellis2 texturing schedule、相同 Blender render protocol。

这仍然不是完整 same-root/same-depth/same-seed 矩阵，但已经去掉了 guide choice 这个混杂因素。

## 文件

- 远端：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/traditional_baseline_texture_matched_guide_20260509`
- 本地 GLB/renders：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_baseline_texture_matched_guide_20260509`
- 指标：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/traditional_baseline_texture_matched_guide_metrics_20260509/metrics.csv`
- 图：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/traditional_baseline_texture_matched_guide_20260509.png`

## 结果

| baseline | guide | occ comps | LCR | occupied voxels | 判断 |
|---|---|---:|---:|---:|---|
| Space colonization root | same vine guide | 218 | 0.524 | 9,185 | 仍明显 fragment；结构像管束 |
| Space colonization tree | same vine guide | 278 | 0.364 | 7,989 | 仍明显 fragment；整体 asset-ready 不足 |
| L-system branch | same vine guide | 315 | 0.115 | 2,622 | 结构清楚但导出后连通 proxy 很差 |
| IFS branch tree | same vine guide | 62 | 0.920 | 3,282 | 传统 baseline 中最强，但仍非单连通 |

## 严格结论

这组比上一组更适合写进论文或补充材料：

- 正面用途：证明在同一 appearance guide 下，传统 procedural baseline 经过 Trellis2 texture/PBR export 后仍不能自动成为单连通 asset。
- 对我们有利的点：proposed 的 vine/coral/bismuth 等 selected cases 能达到 `occ_comp=1, LCR=1.0`，传统 baseline 即使纹理化也没有达到。
- caveat：IFS `LCR=0.92` 说明传统 transform-copy 结构并非完全失败，它是强 baseline；我们必须在论文中承认它是下一轮 matched same-root matrix 中最值得认真比较的传统方法。

下一步：

1. 做 same-root/same-depth/same-seed 的 tree/root/vine 矩阵；
2. 给 IFS/L-system/space-colonization 也生成 neutral zoom-in，比较 junction、tip、root attachment；
3. 如果主文放这张图，caption 必须写成 diagnostic evidence，不能说是最终 baseline closure。
