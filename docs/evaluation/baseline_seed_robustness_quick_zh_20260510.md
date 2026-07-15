---
title: Baseline seed robustness quick matrix
date: 2026-05-10
project: recursive_3d_generative_growth
status: current
---

# Baseline seed robustness quick matrix

## 目的

这轮本地 CPU 快速实验补 `main.tex` 中 seed variation / mean-std 的一小部分缺口。它不是最终完整 baseline，只覆盖 tree/root/vine 三类传统结构和三种结构生成方式：

- `lsystem`
- `space_colonization`
- `proposed_connected`

运行了四个 seed：`20260509`、`20260510`、`20260511`、`20260512`，最大深度 `4`，quick 模式。

## 输出路径

- 原始 seed runs：
  - `results/baseline_matrix_20260509`
  - `results/baseline_matrix_seed_20260510`
  - `results/baseline_matrix_seed_20260511`
  - `results/baseline_matrix_seed_20260512`
- 聚合：
  - `results/baseline_matrix_seed_aggregate_20260510/baseline_matrix_seed_depth4_rows.csv`
  - `results/baseline_matrix_seed_aggregate_20260510/baseline_matrix_seed_depth4_aggregate.csv`

## 结论

这个 quick matrix 给出的最重要结论不是“我们在 connectivity 上击败传统方法”，而恰恰相反：

- 在公平 tube/occupancy 结构协议下，L-system、space colonization、proposed_connected 在 tree/root/vine 上都能达到 `occupancy_component_count_6n=1`、`occupancy LCR=1.0`、`path_to_root_rate=1.0`、`orphan_tip_count=0`。
- 这说明 occupancy connectedness 对传统干净程序化结构没有区分力；它适合证明我们避免碎片传播，但不能单独证明方法优于传统 procedural baseline。
- 后续主文 baseline 必须比较传统方法缺失的维度：generator-native surface/material naturalization、texture/PBR export compatibility、latent transform-copy/cache/addressability、effective resolution、mesh-space vs sparse-latent execution、以及同一 root 下的视觉/语义质量。

## depth-4 聚合摘要

所有 case/method 的 occupancy connectivity 和 root reachability 都是满分：

| family | method | n seeds | occ comps mean | occ LCR mean | path-to-root mean | orphan tips mean |
|---|---|---:|---:|---:|---:|---:|
| root | lsystem | 4 | 1.0 | 1.0 | 1.0 | 0.0 |
| root | proposed_connected | 4 | 1.0 | 1.0 | 1.0 | 0.0 |
| root | space_colonization | 4 | 1.0 | 1.0 | 1.0 | 0.0 |
| tree | lsystem | 4 | 1.0 | 1.0 | 1.0 | 0.0 |
| tree | proposed_connected | 4 | 1.0 | 1.0 | 1.0 | 0.0 |
| tree | space_colonization | 4 | 1.0 | 1.0 | 1.0 | 0.0 |
| vine | lsystem | 4 | 1.0 | 1.0 | 1.0 | 0.0 |
| vine | proposed_connected | 4 | 1.0 | 1.0 | 1.0 | 0.0 |
| vine | space_colonization | 4 | 1.0 | 1.0 | 1.0 | 0.0 |

## 写论文时的使用方式

可写：

> Classical procedural systems easily satisfy connectivity on clean authored scaffolds; therefore our evaluation separates structural stability from asset-readiness and generator-native execution.

不可写：

> Our method improves occupancy connectivity over L-systems or space colonization on clean procedural scaffolds.

这轮结果应作为 baseline/metric 章节的警示：必须加入 latent-vs-mesh、texture/export、effective-resolution、surface/mesh quality 和 semantic branching metrics，否则 occupancy-only table 会被 reviewer 认为没有区分力。
