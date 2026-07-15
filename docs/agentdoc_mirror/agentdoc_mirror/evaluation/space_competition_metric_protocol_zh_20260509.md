# Space Competition Metric Protocol - 2026-05-09

本文整理 2026-05-08 已有本地结果，不跑远端，不修改 `paper_siga/main.tex`。目标是把空间竞争实验固定成可复现、可公平解释的 baseline/metric 协议，并给出当前可用的定量表和论文风格图。

## 1. 数据来源与产物

已读取的主要输入：

- `results/traditional_baselines_space_colonization_20260508_v2/*/metrics.json`
- `results/mesh_metric_sweep_20260508/mesh_metrics.csv`
- `results/mesh_metric_welded_update_20260508/*`
- `docs/evaluation/baseline_metric_eval_plan_zh_20260508.md`
- `docs/evaluation/space_competition_metric_protocol_v2_zh_20260508.md`
- `docs/evaluation/mesh_metric_sweep_status_zh_20260508.md`
- `docs/evaluation/mesh_metric_welded_update_zh_20260508.md`
- `docs/projection_ablation_20260508_1945/projection_ablation_table.csv`
- `paper_siga/figures/space_competition_depth_curves_20260508.csv`

本轮新增产物：

- `paper_siga/figures/space_competition_metrics_20260509.png`
- `docs/evaluation/space_colonization_skeleton_metrics_20260509.csv`
- `docs/evaluation/space_competition_mesh_proxy_summary_20260509.csv`
- `docs/evaluation/space_competition_projection_ablation_summary_20260509.csv`
- `assets/generate_space_competition_metrics_20260509.py`

## 2. 固定算法流程

空间竞争实验的主流程应固定为：

```text
root asset / root scaffold
-> grammar proposals at depth d
-> spatial competition among proposals
-> sparse merge into current occupied state
-> optional masked weak naturalization
-> per-depth projection / pruning
-> re-encode projected state
-> continue to depth d+1
-> export OBJ / GLB / render / metrics for every depth
```

公平比较的关键是每个方法都必须保留 `d=0..D` 的中间状态。只给 final mesh 的方法不能证明递归过程稳定，只能证明最后一步有 repair 能力。

当前已有结果支持三类证据：

1. traditional space-colonization 能给出高 coverage 的显式 skeleton scaffold。
2. conservative `compete` 在 projection ablation 中显著减少 raw component explosion，并保持 dominant component。
3. `compete_fork` 仍然碎片化，应写成 expression-stability boundary，而不是失败后删掉。

## 3. 可比 baseline 固定

主实验至少四列：

| Method | 当前状态 | 公平口径 | 备注 |
| --- | --- | --- | --- |
| Traditional space colonization | 已有 skeleton JSON、tube OBJ、preview/render、metrics | skeleton 指标为主，occupancy proxy 为辅 | raw face components 不公平，因为 tube segment 未共享顶点 |
| Direct sparse grammar | projection ablation 表已有 direct components/LCR | raw component count、largest ratio | 表征 naive recursive edit 的碎片积累 |
| Final-only projection | projection ablation 表已有 final-only kept components/LCR | final projected LCR 和 kept components | 只能说明最终清理，不说明中间状态可用 |
| Proposed per-depth projection + competition | projection ablation 表和 mesh sweep 已有部分结果 | per-depth raw/kept components、primary occupancy LCR | conservative `compete` 是主证据，fork 是边界案例 |

可选 baseline：

- L-system / turtle：可补 branch/tip/angle upper bound。
- DLA / voxel frontier：适合 porous/fracture stress，不适合作为主植物 case。
- IFS / transform-copy：适合 scale-down/portal，不应和 branch competition 混成一个指标。
- One-shot 3D generation / image-entry recursion：适合证明视觉资产质量与递归 trace 是不同问题。

## 4. Metric 定义

主文建议指标分三层。

### 4.1 Traditional skeleton metrics

对 space-colonization 和 L-system 直接从 graph/trace 统计：

- `nodes`
- `segments`
- `tips`
- `branch_nodes`
- `max_depth`
- `coverage_ratio = covered_attractors / total_attractors`
- `total_length`
- `mean_segment_length`

这组指标是 traditional baseline 的公平主指标，因为它输出的是显式 skeleton/tube scaffold。

### 4.2 Mesh / occupancy proxy metrics

统一 mesh 指标来自 `assets/recursive_growth_mesh_metrics.py`：

- `vertices`, `faces`
- raw `component_count`, raw `largest_component_vertex_ratio`
- `occupancy_component_count_6n`
- `largest_occupancy_component_ratio_6n`
- `fragmentation_score = 1 - largest_component_vertex_ratio`
- `occupied_voxels`
- `occupancy_coverage`
- `box_count_dimension_proxy`
- bbox extent / volume / diag

论文主表应使用 `largest_occupancy_component_ratio_6n` 和 `occupancy_component_count_6n` 作为 primary mesh connectivity proxy。原因是 traditional tube OBJ、textured GLB、部分 generated mesh 都可能导出为不共享顶点的三角片，raw face connectivity 会把视觉上相邻的片段误报成大量 components。

### 4.3 Projection / competition metrics

有 trace 或 ablation 表时报告：

- direct raw component count
- direct largest ratio
- final-only kept components
- final-only largest ratio
- per-depth raw components
- per-depth kept components
- per-depth largest ratio
- accepted proposal ratio、collision violation rate、projection survival ratio：当前缺 trace 数据，主表先填 `n/a`

## 5. 当前定量表

### 5.1 Traditional space-colonization skeleton

| case | nodes | segments | tips | branch_nodes | max_depth | coverage_ratio | total_length | mean_segment_length |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| tree_canopy | 1586 | 1585 | 435 | 371 | 26 | 0.970 | 72.14 | 0.0455 |
| root_vine | 1628 | 1627 | 456 | 392 | 24 | 0.971 | 73.46 | 0.0451 |
| bush_shell | 1922 | 1921 | 500 | 440 | 36 | 0.971 | 86.45 | 0.0450 |

解释：traditional SC 的 attractor coverage 稳定接近 0.97，说明它是强结构 scaffold baseline；但它不提供 learned local geometry/PBR material。

### 5.2 Mesh occupancy proxy summary

| label | vertices | faces | occ comps | occ LCR | occupied voxels | box dim proxy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SC tree | 31700 | 31700 | 278 | 0.364 | 7989 | 1.83 |
| SC root | 32540 | 32540 | 218 | 0.524 | 9185 | 1.87 |
| SC bush | 38420 | 38420 | 528 | 0.154 | 11993 | 1.79 |
| Ours tree | 298054 | 608554 | 3 | 0.993 | 11414 | 1.93 |
| Fork tree | 441435 | 872846 | 8 | 0.967 | 11224 | 1.97 |
| Ours DLA | 320516 | 674284 | 1 | 1.000 | 12994 | 2.13 |
| Ours porous | 430538 | 904688 | 1 | 1.000 | 24296 | 2.33 |

解释：这个表只能作为 mesh/occupancy proxy 横向参考，不能把 SC 的低 occupancy LCR 写成结构失败。SC 的主结构指标应看 skeleton coverage/tips/branches；generated mesh 的主资产指标才适合看 occupancy LCR。

### 5.3 Projection ablation

| case | direct comps | direct LCR | final-only kept | final-only LCR | per-depth raw comps | per-depth kept | per-depth LCR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vine_compete_d3 | 2059 | 0.9049 | 2 | 0.9934 | 819 | 1 | 1.0000 |
| tree_compete_d3 | 3201 | 0.9169 | 4 | 0.9842 | 835 | 2 | 0.9949 |
| vine_compete_fork_d3 | 11490 | 0.5178 | 11 | 0.6863 | 2581 | 24 | 0.5758 |
| tree_compete_fork_d3 | 12166 | 0.5869 | 20 | 0.6937 | 5538 | 53 | 0.6141 |

解释：conservative `compete` 支持“每深度投影稳定递归状态”的主张；`compete_fork` 降低 raw component explosion 但保留碎片，适合写成稳定性和表达性的边界。

## 6. 图表产物

本轮生成的论文风格图：

```text
paper_siga/figures/space_competition_metrics_20260509.png
```

图包含三个 panel：

1. traditional SC skeleton coverage 与 tips；
2. selected mesh 的 primary occupancy LCR；
3. direct vs per-depth projection ablation 的 component count 与 LCR。

生成命令：

```bash
python3 assets/generate_space_competition_metrics_20260509.py
```

该脚本只读取已有本地 CSV/JSON，不跑远端实验。

## 7. 数据不足与论文写法限制

当前还不足以声称完整四列主实验已经完成。缺口如下：

- traditional SC、direct sparse grammar、final-only projection、proposed per-depth projection 还没有完全同 root、同 depth、同相机、同 renderer 的四列主表。
- trace 层 `accepted proposal ratio`、`collision violation rate`、`projection survival ratio` 缺失。
- GLB import/PBR material channel success table 还没有接入 space competition 主实验。
- traditional SC tube OBJ 的 raw face connectivity 不公平，不能直接进主表。
- `box_count_dimension_proxy` 是 vertex occupancy proxy，不是严格 fractal dimension。
- 当前图是 metric figure，可用于论文定量图或 appendix；最终 visual main figure 仍应使用统一 Blender/Cycles render。

推荐论文表述：

```text
For mesh-level connectivity, we report a voxel-occupancy 6-neighborhood proxy as the primary metric. This avoids penalizing procedural tube baselines and textured GLB exports whose adjacent geometric pieces may not share vertices. For traditional space-colonization, skeleton-level coverage, tip, and branch metrics are the fair structural comparison.
```

中文口径：

```text
传统 space-colonization 是强结构 baseline，而不是强资产质量 baseline。它的 skeleton coverage/tip/branch 指标可用于证明显式空间竞争的结构控制上限；其 tube OBJ 的 face component 数只作为导出诊断，不能作为主文公平比较指标。
```
