---
title: Projection Matrix Gap Closure 2026-05-09
date: 2026-05-09
tags:
  - recursive-3d-growth
  - projection-ablation
  - baseline-metric
status: active
---

# Projection Matrix Gap Closure 2026-05-09

## 本地输出

- CSV: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/projection_matrix_gap_closure_20260509/projection_matrix_gap_closure.csv`
- Markdown: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/projection_matrix_gap_closure_20260509/projection_matrix_gap_closure.md`

## 结论先行

当前已有证据不足以声称完整的 same-case projection matrix 已闭合。现有 matched projection 事实表只可靠覆盖三列：`no_projection/direct`、`final_only_projection`、`per_depth_prune_only`。`model_bridge` 和 `traditional_repair` 在同一 case 上仍缺结果；已有 DLA bridge / repair_local 结果只能作为 negative/control inventory，不能替代 matched case。

最强的主文候选是 `vine_compete_d3`：direct 有 `2059` 个 mesh components、LCR=`0.9049`；final-only 变为 `2` 个 components、LCR=`0.9934`；per-depth prune/projection 变为 `1` 个 component、LCR=`1.0`。这支持“per-depth projection can prevent fragment propagation in selected simple compete cases”，但进入主文前仍需要 fixed-camera mesh strip 和 root/junction/tip zoom。

`tree_compete_d3` 支持同一趋势，但 per-depth 仍为 `2` 个 components、LCR=`0.9949`，更适合 supporting 或 appendix，而不是写成严格单连通成功。两个 fork case 是清晰失败边界：per-depth 后仍有 `24` / `53` 个 kept components，LCR 只有 `0.5758` / `0.6141`，只能作为 limitation/negative ablation。

## 每个 variant 的状态

| variant | 当前状态 | mesh-based evidence | 可进主文 | 是否缺 rerun |
|---|---|---:|---|---|
| `no_projection/direct` | 已有 `vine/tree/fork` ablation metric 和 OBJ mesh metric | 是 | 可作负例/对照 | 不缺，但缺同屏 render QA |
| `final_only_projection` | 已有 `vine/tree/fork` ablation metric 和 simple case OBJ mesh metric | 是 | 可作对照，不能单独支持方法 | 不缺，但缺同屏 render QA |
| `per_depth_prune_only` | 已有 `vine/tree/fork` ablation metric 和 simple case OBJ mesh metric | 是 | `vine_compete_d3` 可作正向候选；`tree_compete_d3` supporting；fork 为负例 | 不缺数值，缺主文级 zoom QA |
| `model_bridge` | 没有同一 case matched 结果 | 否 | 否 | 是 |
| `traditional_repair` | 有跨 case repair inventory，但没有同一 case matched 结果 | 非 matched | 否 | 是 |
| `traditional_lsystem/space_colonization` | baseline matrix 已有 tree/root/vine final-depth connected support | 是 | fairness sanity check | 不缺 |

## 对论文写法的约束

1. 可以写：在 selected simple compete case 中，per-depth projection 比 direct recursion 和 final-only cleanup 更能抑制 fragment propagation。
2. 必须写：fork/high-branch variants 仍失败，projection 不是通用拓扑保证。
3. 不要写：已经完成 `no projection / final-only / per-depth prune-only / model-bridge / traditional repair` 的完整 same-case 矩阵。
4. 不要把 DLA bridge 或 repair_local 的跨 case 结果并入 matched projection matrix；它们只能作为 stress/negative/control。
5. 传统 structural baseline 在 favorable tube-occupancy 条件下是连通的，应作为 fairness check，而不是 strawman。

## 下一步最小补缺

优先补 `vine_compete_d3` 与 `tree_compete_d3` 的固定相机 render strip 和 root/junction/tip zoom；这比重跑 Trellis2 更直接。若要真正闭合矩阵，再对同一 case 本地生成 `model_bridge` 与 `traditional_repair` 的 mesh-level matched variants，并用相同 occupancy/mesh metric 脚本评价。当前不建议新增 Trellis2/GPU 实验。

## Evidence 文件

- `docs/projection_ablation_20260508_1945/projection_ablation_table.csv`
- `results/projection_ablation_blender_mesh_metrics_20260509/mesh_quality_metrics.csv`
- `results/baseline_matrix_20260509/metrics.csv`
- `results/connectivity_repair_local_20260509/metrics.csv`
- `docs/evaluation/baseline_metric_gap_closure_plan_zh_20260509.md`
