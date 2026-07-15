# Mesh Metric Welded Update - 2026-05-08

本文记录 baseline/metric 支线对 mesh 连通性指标的修正。目标是避免 traditional space-colonization OBJ 因管段逐段导出、相邻段未共享顶点而在 `face connectivity` 下出现虚高 component count，并给出论文可用指标口径。

## 1. 脚本更新

修改脚本：

```text
/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/recursive_growth_mesh_metrics.py
```

新增输出字段：

- `welded_component_*`：可选的 quantized vertex welding 后 face-connectivity 统计。
- `weld_tolerance`、`welded_vertices`、`welded_vertex_reduction`：记录焊接容差与顶点合并量。
- `primary_connectivity_metric`、`primary_component_count`、`primary_largest_component_ratio`：显式标出主连通性指标。默认主指标为 `occupancy_6n_vertex_voxel`。

新增命令行参数：

```text
--weld-tolerance FLOAT
--primary-connectivity {occupancy,welded,face}
```

兼容性：

- 原有 `component_count`、`largest_component_vertex_ratio`、`occupancy_component_count_6n` 等字段保持不变。
- 默认 `--weld-tolerance 0.0` 时不改变旧 face-connectivity 口径，只新增空/disabled 的 welded 字段。
- 默认 `--primary-connectivity occupancy`，用于防止后续汇总表继续误用 raw face components。

## 2. 本地小规模验证

验证输出：

```text
results/mesh_metric_welded_update_20260508/mesh_metrics_welded_small.json
results/mesh_metric_welded_update_20260508/mesh_metrics_welded_small.csv
results/mesh_metric_welded_update_20260508/mesh_metrics_welded_tol1e-2_small.json
results/mesh_metric_welded_update_20260508/mesh_metrics_welded_tol1e-2_small.csv
```

覆盖 case：

- `sc_root_vine`
- `sc_bush_shell`
- `sc_tree_canopy`
- `proposed_tree_compete`
- `proposed_porous_container`

### 2.1 小容差焊接：`--weld-tolerance 1e-6`

| case | raw face comps | welded comps | welded LCR | occ comps | occ LCR |
|---|---:|---:|---:|---:|---:|
| sc_root_vine | 1627 | 1581 | 0.001 | 218 | 0.524 |
| sc_bush_shell | 1921 | 1847 | 0.001 | 528 | 0.154 |
| sc_tree_canopy | 1585 | 1545 | 0.002 | 278 | 0.364 |
| proposed_tree_compete | 2 | 2 | 0.995 | 3 | 0.993 |
| proposed_porous_container | 1 | 1 | 1.000 | 1 | 1.000 |

结论：`1e-6` 只合并少量完全或近似重合顶点，不能修正 traditional SC tube OBJ 的虚高 face components。说明当前 traditional OBJ 不是简单的重复索引问题，而是逐管段 mesh 之间存在真实几何间隙、截面不共享、或浮点位置不完全一致。

### 2.2 大容差焊接：`--weld-tolerance 1e-2`

| case | raw face comps | welded comps | welded LCR | occ comps | occ LCR |
|---|---:|---:|---:|---:|---:|
| sc_root_vine | 1627 | 31 | 0.810 | 218 | 0.524 |
| sc_bush_shell | 1921 | 25 | 0.314 | 528 | 0.154 |
| sc_tree_canopy | 1585 | 17 | 0.904 | 278 | 0.364 |
| proposed_tree_compete | 2 | 341 | 0.874 | 3 | 0.993 |
| proposed_porous_container | 1 | 35 | 0.997 | 1 | 1.000 |

结论：`1e-2` 可以显著降低 traditional SC 的 face components，但它是尺度相关的近邻合并，会扰动 proposed mesh 的 face connectivity。例如 `proposed_tree_compete` 从 2 个 raw face components 变成 341 个 welded components，说明过大容差会折叠局部三角形、制造退化面或断开连接。

## 3. 哪些指标可进论文

可进主表：

- `occupancy_component_count_6n`
- `largest_occupancy_component_ratio_6n`
- `primary_component_count`
- `primary_largest_component_ratio`
- `box_count_dimension_proxy`，但需标注为 vertex occupancy proxy，不等价于严格 fractal dimension。
- traditional space-colonization 的 skeleton-level 指标，例如 coverage、tips、branches、length、angle。该类指标比 tube OBJ face connectivity 更公平。

可进附录或诊断表：

- `welded_component_count`
- `largest_welded_component_vertex_ratio`
- `welded_vertex_reduction`
- 不同 `weld_tolerance` 的敏感性分析。

不应进主表或不应作为公平对比依据：

- traditional SC tube OBJ 的 raw `component_count` / `largest_component_vertex_ratio`。
- 单一固定大容差下的 welded face components，除非对所有类别先做统一尺度归一化和几何 QA。
- `surface_area_est` 作为类别间质量比较，因为不同生成器三角化密度和管径设置不同。

## 4. 论文写法建议

推荐表述：

```text
For connectivity, we report a voxel-occupancy 6-neighborhood proxy as the primary mesh-level metric, because procedural tube baselines may export adjacent branch segments without shared vertices. Raw face-component counts are retained only as a diagnostic signal. For traditional space-colonization baselines, skeleton-level metrics are the fair structural comparison.
```

中文解释：

传统 space-colonization 的 OBJ 是逐段 tube mesh，不保证相邻管段共享顶点或形成 watertight union。因此 raw face components 会把许多视觉上相连的枝段统计为独立组件。occupancy connectivity 更接近“空间上是否连续”的问题，但仍是 proxy；最终论文中应把它称为 voxel/occupancy proxy，而不是严格拓扑连通性。
