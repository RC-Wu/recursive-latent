# Projection ablation mesh-render QA（2026-05-09）

## 目的

补齐 reviewer/用户反复指出的证据缺口：projection ablation 不能只用旧的 preview/contact sheet 或点云式可视化，必须有真实 mesh render 支撑主文 claim。

本轮只选择最干净的 conservative `compete` 线，不把 `compete_fork` 的失败边界混入主图：

- `vine_compete_d3`: direct / final-only / per-depth
- `tree_compete_d3`: direct / final-only / per-depth

## 资产路径

- 本地 mesh：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/projection_ablation_blender_mesh_20260509/meshes`
- Blender renders：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/projection_ablation_blender_mesh_20260509/renders`
- 指标：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/projection_ablation_blender_mesh_metrics_20260509/mesh_quality_metrics.csv`
- 论文图：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/projection_ablation_mesh_contact_20260509.png`
- 论文 PDF：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.pdf`

## 关键指标

| case | raw mesh comps | raw LCR | judgement |
|---|---:|---:|---|
| vine direct | 2059 | 0.9049 | fragments visually obvious |
| vine final-only | 2 | 0.9934 | strong cleanup, but only after fragments already existed during recursion |
| vine per-depth | 1 | 1.0000 | strongest conservative case |
| tree direct | 3201 | 0.9169 | fragments visually obvious |
| tree final-only | 4 | 0.9842 | improved but still multi-component |
| tree per-depth | 2 | 0.9949 | strongest conservative tree case |

## 严格解释

这张图可以支持：

- projection 必须放进递归 transition 内，而不是仅仅做 final cleanup；
- conservative competition + per-depth projection 是当前最稳的主线；
- direct recursion 会让碎片在递归过程中作为潜在 handle/frontier/cache 污染后续状态。

这张图不能支持：

- 所有 rule family 都已经解决；
- GLB/material export 的 raw topology 是干净的；
- fork/radial/DLA 等高表达性 operator 已经单连通。

## 论文处理

已把图插入 `main.tex`，caption 明确：

- 这是真 mesh / Blender render，不是 point-cloud preview；
- 表格中的 raw component 是 mesh face-connectivity diagnostic；
- 其他地方的 occupancy-primary connectivity proxy 与 raw mesh component 是两个不同口径。
