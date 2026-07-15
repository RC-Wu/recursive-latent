# Ralph connectivity-first method compare 远端状态

采样时间：2026-05-09 22:21:51、22:22:21、22:22:51 CST。  
远端 runroot：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/connectivity_first_method_compare_ralph_20260509_221704`  
远端 logs：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/connectivity_first_method_compare_ralph_20260509_221704`

本地拉取目录：`docs/remote_results/connectivity_first_method_compare_ralph_20260509_221704_pull/`

## 监控状态

- 已拉取完成的 `summary.json` / `selected_candidates.json` 共 18 个文件，包括 16 个 method-level `summary.json`、`gpu4_dla_voxel_root/summary.json`、`gpu4_dla_voxel_root/selected_candidates.json`。
- 三次采样期间，`gpu5_pyrite_lattice`、`gpu6_volumetric_dla_coral`、`gpu7_bismuth_hopper` 的 `summary_partial.json` 仍在增长或新增 method summary，说明采样窗口内 run 仍在推进；只有 `gpu4_dla_voxel_root.log` 明确显示 `status: completed`，完成时间为 `2026-05-09T22:20:11+0800`。
- 进程检查命令在远端返回 `ps: user name does not exist`，因此本轮没有可靠进程表；状态判断主要来自结果文件新增、partial 文件增长和 log tail。

## 指标表

`occ_comp` 是 `occupancy_component_count`；`occ_lcr` 是 `occupancy_lcr`；`face_comp` 是 `face_component_count`；`face_lcr` 是 `face_largest_component_ratio`。

| case | grammar | method | score | occ_comp | occ_lcr | face_comp | face_lcr | 判断 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| bismuth_hopper | fork_side_attach | raw | 0.998 | 1 | 1.000 | 1 | 1.000 | 正面：occupancy 和 face 均完全连通 |
| bismuth_hopper | fork_side_attach | mesh_bridge_smooth | 0.998 | 1 | 1.000 | 1 | 1.000 | 正面：与 raw 同样完全连通 |
| bismuth_hopper | fork_side_attach | sparse_close | 0.998 | 1 | 1.000 | 2 | 0.998 | 边界正面：体素连通，mesh face 仍有 2 个组件 |
| bismuth_hopper | fork_side_attach | sparse_close_bridge | 0.998 | 1 | 1.000 | 1 | 1.000 | 正面：体素和 face 均连通 |
| dla_voxel_root | compete_fork_attach | raw | 0.993 | 3 | 0.999 | 1 | 1.000 | 边界正面：mesh 连通，occupancy 仍有 3 组件但 LCR 极高 |
| dla_voxel_root | compete_fork_attach | mesh_bridge_smooth | 0.976 | 4 | 0.984 | 1 | 1.000 | 边界：mesh 连通，但 occupancy 组件更多且 LCR 下降 |
| dla_voxel_root | compete_fork_attach | sparse_close | 0.866 | 11 | 0.888 | 12 | 0.869 | 负面：体素和 face 均明显碎裂 |
| dla_voxel_root | compete_fork_attach | sparse_close_bridge | 0.865 | 11 | 0.887 | 8 | 0.943 | 负面：bridge 改善 face LCR，但 occupancy 仍碎裂 |
| pyrite_lattice | fork_side_attach | raw | 0.998 | 1 | 1.000 | 3 | 0.993 | 边界正面：体素连通，mesh face 有少量残余组件 |
| pyrite_lattice | fork_side_attach | sparse_close | 0.998 | 1 | 1.000 | 5 | 0.974 | 边界/负面：体素连通，但 face 碎片增加 |
| pyrite_lattice | fork_side_attach | sparse_close_bridge | 0.998 | 1 | 1.000 | 4 | 0.994 | 边界正面：face LCR 恢复到接近 raw，但组件数仍未清零 |
| volumetric_dla_coral | compete_fork_attach | raw | 0.669 | 9 | 0.687 | 10 | 0.739 | 负面：严重碎裂 |
| volumetric_dla_coral | compete_fork_attach | sparse_close | 0.731 | 7 | 0.745 | 9 | 0.751 | 负面但有改善：occupancy 组件和 LCR 好于 raw |
| volumetric_dla_coral | compete_fork_attach | mesh_bridge_smooth | 0.796 | 9 | 0.814 | 5 | 0.938 | 边界/部分正面：face 明显改善，occupancy 仍有 9 组件 |
| volumetric_dla_coral | fork_side_attach | raw | 0.942 | 4 | 0.950 | 5 | 0.948 | 边界：比 compete_fork_attach 明显好，但仍非完全连通 |
| volumetric_dla_coral | fork_side_attach | sparse_close | 0.998 | 1 | 1.000 | 2 | 0.987 | 正面候选：occupancy 完全连通，face 仅剩 2 组件 |

## 分 case 结论

### `gpu4_dla_voxel_root`

`selected_candidates.json` 选择了 `raw`，其 final metrics 为：`occupancy_component_count=3`、`occupancy_lcr=0.999353`、`face_component_count=1`、`face_largest_component_ratio=1.0`、`selection_score=0.993353`。这是一个重要的边界正面结果：mesh surface 已完全连通，但 occupancy 仍保留极少数小组件。  

`sparse_close` 和 `sparse_close_bridge` 在这个 case 上是负面结果：两者都把 final occupancy component count 推到 11，LCR 降到约 0.887-0.888；`sparse_close_bridge` 虽然把 face component 从 12 降到 8，并把 face LCR 提高到 0.943，但没有解决 occupancy 破碎问题。论文中适合用作 counterexample：稀疏闭合不应被描述为单调改进，应强调 case-dependent failure。

### `gpu5_pyrite_lattice`

已完成 3 个 method-level summary：`raw`、`sparse_close`、`sparse_close_bridge`。三者 occupancy 都完全连通；区别主要在 face components。`raw` 为 3 个 face components，`sparse_close` 增加到 5 且 face LCR 降至 0.974，`sparse_close_bridge` 回到 4 且 face LCR 约 0.994。  

论文中可作为“voxel connectivity can be solved while surface connectivity remains imperfect”的例子；`sparse_close_bridge` 可作为缓解 face fragmentation 的弱正面，但不是完全解决。

### `gpu6_volumetric_dla_coral`

这个 case 分化最明显。`compete_fork_attach` grammar 下所有 method 都没有完全解决 occupancy connectivity：`raw` 是 9 个 occupancy 组件、LCR 0.687；`sparse_close` 改善到 7 个组件、LCR 0.745；`mesh_bridge_smooth` face 侧改善明显，face components 从 10 降到 5、face LCR 提高到 0.938，但 occupancy 仍有 9 个组件。  

同一 case 的 `fork_side_attach` grammar 明显更好：`raw` 为 4 个 occupancy 组件、LCR 0.950；`sparse_close` 达到 occupancy 完全连通，face 仅剩 2 个组件、face LCR 0.987。论文中最适合用它证明 grammar choice 与 connectivity correction method 有交互效应：换 grammar 比单独补 connectivity 更关键。

### `gpu7_bismuth_hopper`

四个 method 都达到 occupancy 完全连通。`raw`、`mesh_bridge_smooth`、`sparse_close_bridge` 的 face 也完全连通；`sparse_close` 仅剩 2 个 face components，face LCR 0.998。  

论文中可作为正面稳定 case，说明在某些结构上 connectivity-first pipeline 不需要复杂修复也能稳定工作；`sparse_close_bridge` 可作为不破坏连通性的保守增强。

## 论文使用建议

- 主表建议按 `case / grammar / method` 报告 `occupancy_component_count`、`occupancy_lcr`、`face_component_count`、`face_largest_component_ratio` 和 `selection_score`，不要只报单一 score。
- 正面例子：`bismuth_hopper/fork_side_attach` 全部 method 基本稳定；`volumetric_dla_coral/fork_side_attach/sparse_close` 是最强的修复型正面例子。
- 边界例子：`dla_voxel_root/raw`、`pyrite_lattice/raw`、`pyrite_lattice/sparse_close_bridge`，用于说明 occupancy 与 face connectivity 的评价不完全等价。
- 负面例子：`dla_voxel_root/sparse_close*` 和 `volumetric_dla_coral/compete_fork_attach/*`，用于讨论 sparse repair 的非单调性、grammar-method interaction，以及为什么论文需要同时报告 voxel 和 mesh-level components。
- 后续如果主 agent 需要补拉结果，应优先补 `gpu5_pyrite_lattice/selected_candidates.json`、`gpu6_volumetric_dla_coral/summary.json`、`gpu6_volumetric_dla_coral/selected_candidates.json`、`gpu7_bismuth_hopper/summary.json`、`gpu7_bismuth_hopper/selected_candidates.json`，因为本轮采样时这些 root-level 文件尚未完成或未出现在拉取集合中。
