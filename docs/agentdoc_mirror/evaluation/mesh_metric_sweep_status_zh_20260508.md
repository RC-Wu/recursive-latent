# Mesh Metric Sweep 状态 - 2026-05-08 21:55

本文记录第一版统一 mesh 指标脚本的实际运行结果和重要注意事项。它不是最终实验表，而是把 baseline/metric 从文档推进到可执行状态。

## 1. 输入与输出

脚本：

```text
/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/recursive_growth_mesh_metrics.py
```

输出：

```text
/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/mesh_metric_sweep_20260508/mesh_metrics.json
/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/mesh_metric_sweep_20260508/mesh_metrics.csv
```

覆盖数据：

- traditional space-colonization v2 的 `tree/root/bush` OBJ；
- non-tree recursive meshes；
- projection pruning compete/fork candidates。

## 2. 关键结果摘要

| case | vertices | faces | face comps | face LCR | occ comps | occ LCR | box-dim proxy |
|---|---:|---:|---:|---:|---:|---:|---:|
| bush shell SC | 38,420 | 38,420 | 1,921 | 0.001 | 528 | 0.154 | 1.79 |
| root vine SC | 32,540 | 32,540 | 1,627 | 0.001 | 218 | 0.524 | 1.87 |
| tree canopy SC | 31,700 | 31,700 | 1,585 | 0.001 | 278 | 0.364 | 1.83 |
| island city scale-down | 419,096 | 921,140 | 2 | 0.975 | 3 | 0.998 | 2.19 |
| ornate chair portal | 148,144 | 411,470 | 1 | 1.000 | 1 | 1.000 | 2.03 |
| porous container compete | 430,538 | 904,688 | 1 | 1.000 | 1 | 1.000 | 2.33 |
| ruin arch portal | 207,163 | 474,636 | 1 | 1.000 | 1 | 1.000 | 2.14 |
| crown portal | 314,504 | 727,348 | 5 | 0.946 | 5 | 0.918 | 2.08 |
| crown radial4 | 17,357 | 33,012 | 5 | 0.248 | 7 | 0.257 | 1.87 |
| scifi translate | 453,050 | 879,950 | 1 | 1.000 | 2 | 1.000 | 2.25 |
| snow arch portal | 318,537 | 645,682 | 2 | 0.924 | 3 | 0.920 | 2.16 |
| DLA compete d4 pruned | 320,516 | 674,284 | 1 | 1.000 | 1 | 1.000 | 2.13 |
| DLA compete-fork d4 pruned | 715,506 | 1,429,990 | 11 | 0.948 | 5 | 0.984 | 2.10 |
| tree compete d4 pruned | 298,054 | 608,554 | 2 | 0.995 | 3 | 0.993 | 1.93 |
| tree compete-fork d4 pruned | 441,435 | 872,846 | 16 | 0.702 | 8 | 0.967 | 1.97 |

## 3. 重要解释

传统 space-colonization 的 tube OBJ 在 face-connectivity 指标下显示数千组件，但这不是结构失败的直接证据。原因是当前 tube mesh 是按 segment 生成的，很多相邻 tube 没有共享焊接顶点，因此 face graph 会把每段 tube 当成独立组件。

后续主实验应这样处理：

1. 对 traditional space-colonization，主结构指标使用 skeleton JSON 的 `coverage/tips/branches/length/angle`，而不是 face LCR。
2. 若要统一 mesh 指标，使用 occupancy component proxy 或先做 weld/boolean union/remesh。
3. 在论文表格中不能把 traditional tube face-component 直接作为对比项，否则不公平。

## 4. 对主故事的支持

有用的正结果：

- `porous_container_compete`、`ruin_arch_portal`、`ornate_chair_portal`、`DLA compete d4` 在 face 和 occupancy proxy 上都显示强连通或近强连通，说明非树/晶体/portal 类别不是完全不可用。
- `tree_compete_d4_pruned` 的 face LCR 为 `0.995`、occupancy LCR 为 `0.993`，支持 conservative competition + projection 的稳定性。
- `compete_fork` 一类更 expressive，但 face LCR 明显下降，适合作为 stability-expression boundary 的消融。

风险：

- `crown_radial4` 的 LCR 很低，不适合放主图，只能作为失败/边界或需要重做的 symmetry case。
- `snow_arch_portal`、`crown_portal` 有一定碎片，但仍比 radial4 更可写。
- 指标现在仍是 proxy，不能声称 topology 完整；Euler/genus/watertight volume 还没实现。

## 5. 下一步

1. 给 traditional baselines 增加 skeleton-level metric table。
2. 对 selected proposed meshes 运行 Blender/PBR import QA，形成 `GLB import/material channel` 表。
3. 对 traditional tube OBJ 做 weld/remesh 或直接从 skeleton 生成 welded branch mesh，避免 face-connectivity 指标误导。
4. 把 `tree_compete_d4_pruned`、`porous_container_compete`、`ruin_arch_portal`、`scifi_translate` 作为下一批高质量 mesh/textured render 候选。
