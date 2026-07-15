---
title: Flow/SDE naturalization grid 初步指标
date: 2026-05-10
project: recursive_3d_generative_growth
status: current
---

# Flow/SDE naturalization grid 初步指标

## 目的

这轮实验针对论文里的 masked/local naturalization 相关 TODO。目标不是证明 Flow/SDE 是主贡献，而是检查冻结 Trellis2 sampler 的 stochastic local realization 是否能替代传统随机生长，或至少作为 recursive grammar 的局部自然化算子。

远端运行：

- `flow_sde_naturalization_grid_ralph_20260510_0002`
- `flow_sde_naturalization_steps1_ralph_20260510_0008`

当前已经完成并拉回的指标：

- `results/flow_sde_naturalization_metrics_20260510_0008/flow_sde_naturalization_grid_ralph_20260510_0002_mesh_metrics.csv`
- `results/flow_sde_naturalization_metrics_20260510_0008/flow_sde_grid_0002_compact.csv`
- `results/flow_sde_naturalization_metrics_20260510_0008/flow_sde_naturalization_steps1_ralph_20260510_0008_mesh_metrics.csv`
- `results/flow_sde_naturalization_metrics_20260510_0008/flow_sde_runtime_stub_grid_ralph_20260509_233429_mesh_metrics.csv`
- `results/flow_sde_naturalization_metrics_20260510_0008/flow_sde_steps_1_2_4_8_compact.csv`
- `results/flow_sde_naturalization_metrics_20260510_0008/flow_sde_depth2_summary.csv`

## 结论先行

当前 steps=1/2/4/8 grid 给出的是**负面/边界证据**：

- Flow/SDE 可以稳定运行并输出 OBJ mesh；
- 但是它不能单独替代 PS-RSLG 的 projection / attachment / occupancy competition；
- vine、coral 在 occupancy-primary 指标上明显碎；
- pyrite depth-2 有高 LCR 但仍有 66 个 occupancy components 和大量 face components；
- bismuth depth-2 在 steps=8 时最接近可用，但仍是 15 个 occupancy components；
- pyrite 在 steps=1/8 时有较高 LCR，但仍是 386 / 66 个 occupancy components；
- 没有一个 sampler-only 配置达到 `occ_comp=1` 且高 LCR 的主正例标准。

因此当前最稳写法是：

> Frozen sampler naturalization can be called inside the sparse-latent executor, but a sampler-only update is not a topology-preserving growth rule. It should remain masked and subordinate to grammar attachment/projection.

不能写：

> Flow/SDE replaces traditional stochastic growth.

## steps=4/8 compact results

| case | steps | depth | vertices | faces | occ comps | occ LCR | face comps | face LCR | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| bismuth | 8 | 2 | 684,262 | 1,335,026 | 15 | 0.9992 | 2,142 | 0.9937 | best sampler-only candidate, but not connected invariant |
| pyrite | 8 | 2 | 887,529 | 1,445,828 | 66 | 0.9970 | 24,518 | 0.2846 | high LCR but many fragments |
| vine | 4 | 2 | 78,523 | 122,420 | 159 | 0.7635 | 4,104 | 0.2227 | not acceptable as topology-preserving growth |
| coral | 4 | 2 | 24,358 | 19,894 | 836 | 0.0380 | 6,543 | 0.0705 | strong negative |

## depth-2 steps 1/2/4/8 summary

| case | steps | vertices | faces | occ comps | occ LCR | face comps | face LCR | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| bismuth | 1 | 470,705 | 1,040,136 | 1,002 | 0.9037 | 10,775 | 0.2726 | negative |
| bismuth | 2 | 31,321 | 72,340 | 6,915 | 0.0074 | 177 | 0.9930 | negative; face LCR misleading |
| bismuth | 8 | 684,262 | 1,335,026 | 15 | 0.9992 | 2,142 | 0.9937 | near-LCR but fragmented |
| coral | 1 | 142,161 | 227,208 | 112 | 0.7904 | 5,180 | 0.1508 | negative |
| coral | 2 | 3,570 | 6,356 | 342 | 0.1409 | 110 | 0.6555 | negative |
| coral | 4 | 24,358 | 19,894 | 836 | 0.0380 | 6,543 | 0.0705 | negative |
| pyrite | 1 | 1,243,477 | 2,735,320 | 386 | 0.9844 | 23,518 | 0.9266 | near-LCR but fragmented |
| pyrite | 2 | 15,992 | 34,262 | 298 | 0.2193 | 196 | 0.9655 | negative; face LCR misleading |
| pyrite | 8 | 887,529 | 1,445,828 | 66 | 0.9970 | 24,518 | 0.2846 | near-LCR but fragmented |
| vine | 1 | 150,748 | 379,466 | 162 | 0.5446 | 5,346 | 0.2318 | negative |
| vine | 2 | 4,045 | 9,030 | 198 | 0.4617 | 146 | 0.4729 | negative |
| vine | 4 | 78,523 | 122,420 | 159 | 0.7635 | 4,104 | 0.2227 | negative |

## 对论文的影响

1. `Flow/SDE` 不应作为主方法正例单独出现。
2. Face LCR 在部分 small-mesh sampler outputs 上会误导，例如 bismuth/pyrite steps=2 face LCR 很高但 occupancy LCR 很低。因此 naturalization ablation 必须以 occupancy-primary 和 surface/mesh diagnostics 分层报告。
3. 它可以作为 `naturalization ablation` 中的 control：
   - rule-only / no naturalization；
   - sampler-only / global or weak local sampler；
   - masked sampler under attachment-preserving projection；
   - PS-RSLG full executor。
3. 当前 negative result 支撑文章主故事：生成模型 sampler 的随机性很有用，但必须被 grammar state、attachment certificate 和 per-depth projection 约束，否则会制造碎片或漂移。

## 仍待补

- 还需要把同一 root/depth 的 no-N / masked-N / global-N / with-projection / without-projection 放入同一表；
- 如果要把 Flow/SDE 写进主文，必须补 surface/occupancy/face 指标和纯白 mesh render，不可用 matplotlib preview。
