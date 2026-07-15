# Traditional baselines + same Trellis2 texture path 对比

更新时间：2026-05-09 08:15 +08

## 为什么做这组

用户要求 baseline/metric 不只停留在传统单色 mesh，也要考虑纹理/PBR。这里把传统 procedural baseline 的 OBJ 也送入同一个 Trellis2 texturing/export path，用来回答一个关键问题：

> 如果传统 L-system / space-colonization / DLA 也获得 Trellis2 纹理，是否就能成为可用 textured recursive asset？

这不是最终公平基线矩阵，但它是一个很有价值的诊断：固定 texture/export 能力之后，传统 scaffold 的结构问题是否仍然存在。

## 输入与输出

输入：

- `space_colonization root_vine`
- `space_colonization tree_canopy`
- `lsystem_branch`
- `dla_cluster_voxels`

远端输出：

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/traditional_baseline_texture_20260509`

本地输出：

- GLB：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_baseline_texture_20260509`
- Blender renders：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_baseline_texture_20260509/renders`
- Metrics：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/traditional_baseline_texture_metrics_20260509/metrics.csv`
- Figure：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/traditional_baseline_texture_20260509.png`

## 定量结果

| case | occ comps | LCR | occupied voxels | 视觉判断 |
|---|---:|---:|---:|---|
| Space colonization root | 218 | 0.524 | 9,185 | 纹理可导出，但结构像一团管束，断裂明显 |
| Space colonization tree | 278 | 0.364 | 7,989 | 更像白色枝条团，局部可看但整体不够 asset-ready |
| L-system branch | 315 | 0.115 | 2,622 | 形态清楚，但 Trellis2 GLB 后 occupancy fragment 严重 |
| Voxel DLA cluster | 2,511 | 0.002 | 3,272 | 作为 textured asset 失败，几乎是碎块集合 |

## 结论

这组结果非常支持目前论文故事：

1. Trellis2 texture/PBR export 不是万能后处理。传统 scaffold 直接送入 texture path 后可以生成 GLB，但结构连通性指标很差。
2. 这说明本文主张的 projection-aware recursive execution 有必要性：问题不是“缺材质”，而是递归状态在每一步必须保持 connected / projectable / reusable。
3. 传统 baselines 仍然是结构控制和 branch/path 指标的重要对照，但不能直接作为高质量 textured recursive asset 的上限。

严格 caveat：

- 这组不是最终 matched same-root baseline matrix；输入类别、root 和 guide 还没有完全统一。
- 指标仍使用 GLB vertex-occupancy proxy；raw face components 由于 Trellis2/GLB material island 会更碎。
- 可以在论文中作为 “texture alone is insufficient” 的辅助证据，而不是主对比表的唯一证据。
