# 占据连通性优先指标与 Flow/SDE 实验汇总（2026-05-09）

本文档只整理 mesh/GLB/Blender/数值证据，不使用 matplotlib 点云图作为结果证据。写入范围限于本实验汇总支线；未修改 `main.tex`，未操作远端。

## 数据来源

- Method compare 汇总：`docs/remote_results/ralph_method_compare_20260509_221704.md`
- Connectivity/depth/flow 结果：`visuals/connectivity_depth_flow_ralph_20260509_2310/**/summary.json`
- Pyrite close/bridge/flow 网格：`visuals/pyrite_connectivity_flow_grid_ralph_20260509_2340/**/summary.json`
- Projection matrix gap closure：`results/projection_matrix_gap_closure_20260509/projection_matrix_gap_closure.csv`
- Hard-DLA 桥接消融：`visuals/dla_bridge_ablation_20260509/**/summary.json`
- 本轮整理 CSV：
  - `results/occupancy_primary_summary_20260509/connectivity_candidates_20260509.csv`
  - `results/occupancy_primary_summary_20260509/flow_sde_depth_metrics_20260509.csv`

## 指标解释

- `occupancy_component_count` / `occupancy_lcr` 是本文建议的 primary connectivity 指标：先判断体素占据是否连通，再看最大连通块比例。
- `face_component_count` / `face_largest_component_ratio` 是 mesh surface 指标：用于补充说明可渲染 mesh 的碎片残留。
- 主文中不建议只报单一 selection score；至少同时报告 occupancy component、occupancy LCR、face component、face LCR。

## 能支持正文正面 claim

| case | 证据 | 关键数值 | 主文可写法 |
|---|---|---:|---|
| `volumetric_dla_coral / fork_side_attach / sparse_close` depth=3 | `connectivity_depth_flow_ralph_20260509_2310/gpu6_coral_depth3` | occ=1, occ_lcr=1.000, face=1, face_lcr=1.000, verts=110222, faces=200862, occupied_voxels=4140, last input/proposal tokens=502/942 | 最强正面：occupancy-primary 与 mesh surface 都完全连通，可作为主文 connectivity-first 成功例 |
| `volumetric_dla_coral / fork_side_attach / sparse_close_bridge` depth=3 | 同上 | occ=2, occ_lcr=0.999810, face=1, face_lcr=1.000, verts=138932, faces=254012, tokens=628/1128 | 可作为近似正面/补充：surface 完全连通，但 occupancy 仍有 2 个组件，不应写成完全连通 |
| `bismuth_hopper / fork_side_attach / sparse_close` depth=2 | `connectivity_depth_flow_ralph_20260509_2310/gpu4_bismuth_depth2` | occ=1, occ_lcr=1.000, face=6, face_lcr=0.975480, verts=635555, faces=1199870, tokens=2257/3237 | 可支持 occupancy-primary claim，但不能支持 mesh surface 完全连通 claim |
| `bismuth_hopper` method compare | `ralph_method_compare_20260509_221704.md` | raw / mesh_bridge_smooth / sparse_close_bridge 均 occ=1, face=1；sparse_close occ=1, face=2, face_lcr=0.998 | 可作为 bismuth 稳定性的主文或脚注佐证；要注明来自 method compare 窗口 |
| Projection per-depth prune, `vine_compete_d3` | `projection_matrix_gap_closure.csv` | no_projection: comp=2059, LCR=0.9049；final_only: comp=2, LCR=0.9934；per_depth: comp=1, LCR=1.000, verts=188403, faces=429002 | 可支撑“per-depth projection/pruning 比无投影或 final-only cleanup 更稳定”的主文正面 claim |
| Matched structural baseline sanity check | `projection_matrix_gap_closure.csv` | tree/root/vine 的 L-system、space colonization、proposed_connected 均 comp=1, LCR=1.000 | 可用于公平性说明：传统 baseline 本身连通，不能把传统方法当 strawman |

Texture/GLB 侧的正面证据可作为“选中 mesh 可以走 Trellis2 texture path”的资产可导出证明，但不是 connectivity 主证据：bismuth textured best 为 shape/tex tokens=5269/5269、mesh=635555 verts / 1199870 faces、GLB 约 39.98 MB；coral textured best 为 tokens=942/942、mesh=110222 verts / 200862 faces、GLB 约 9.89 MB；coral sparse_bridge textured 为 tokens=1314/1314、mesh=152604 verts / 276798 faces、GLB 约 12.71 MB。

## 适合 appendix 负例或边界

| case | 证据 | 关键数值 | 归类依据 |
|---|---|---:|---|
| `volumetric_dla_coral / compete_fork_attach / *` depth=3 | `gpu6_coral_depth3` | sparse_close: occ=7, occ_lcr=0.806643, face=11, face_lcr=0.642755；sparse_close_bridge: occ=6, occ_lcr=0.908133, face=3, face_lcr=0.970283；mesh_bridge_smooth: occ=8, occ_lcr=0.929714, face=1, face_lcr=1.000 | 强边界：mesh 可被修成 surface 连通，但 occupancy 仍碎，说明 grammar choice 与 repair method 有交互 |
| `pyrite_lattice` method compare | `ralph_method_compare_20260509_221704.md` | raw: occ=1, face=3, face_lcr=0.993；sparse_close: occ=1, face=5, face_lcr=0.974；sparse_close_bridge: occ=1, face=4, face_lcr=0.994 | 可作“occupancy solved, surface imperfect”的边界例 |
| `pyrite_lattice` depth=2 / close grid | `gpu5_pyrite_depth2` 与 `pyrite_connectivity_flow_grid_ralph_20260509_2340` | depth2 best around compete+sparse_close_bridge: occ=4, occ_lcr=0.989154, face=6, face_lcr=0.977435；close2 bridge 可出现 occ=43, occ_lcr=0.998476, face=1；close5 bridge 可退化到 occ=80-99 | Pyrite 不能作为强主文正面。它适合说明参数敏感、occupancy 与 face 指标不等价 |
| `dla_voxel_root` method compare | `ralph_method_compare_20260509_221704.md` | raw: occ=3, occ_lcr=0.999353, face=1；sparse_close/sparse_close_bridge: occ=11, occ_lcr≈0.887-0.888, face=12/8 | 边界/负例：sparse repair 非单调，bridge 改善 face 但不解决 occupancy |
| `hard_dla` | `dla_bridge_ablation_20260509` | raw: occ=4, occ_lcr=0.387223, face=5, face_lcr=0.300680；raw_bridge_smooth: occ=6, occ_lcr=0.670490, face=1；sparse_close_bridge: occ=4, occ_lcr=0.738181, face=3；mesh_bridge_smooth: occ=6, occ_lcr=0.615000, face=3 | 明确负例：最多能改善 surface，不能支持 occupancy-primary 正向 claim |
| Projection fork variants | `projection_matrix_gap_closure.csv` | `vine_compete_fork_d3`: no_projection comp=11490/LCR=0.5178, final_only comp=11/LCR=0.6863, per_depth comp=24/LCR=0.5758；`tree_compete_fork_d3`: no_projection comp=12166/LCR=0.5869, final_only comp=20/LCR=0.6937, per_depth comp=53/LCR=0.6141 | 不能放成正面 projection 结果；适合 appendix 说明 fork grammar 下 per-depth prune 仍可能失败 |

## Flow/SDE 结果判断

Flow/SDE summary 目前只有 depth-level `input_tokens`、`repaired_tokens`、`vertices`、`faces`、seconds，没有 `occupancy_component_count`、`occupancy_lcr`、`face_component_count`、`face_largest_component_ratio`。因此它不能支撑正文 connectivity claim。

| case | steps | depth 0/1/2 tokens | depth 0/1/2 verts | depth 0/1/2 faces | 判断 |
|---|---:|---:|---:|---:|---|
| bismuth continue | 1 | 21/34/47 | 17781/18114/25350 | 53156/69508/71252 | 有可导出 mesh 数值，但无连通性指标 |
| bismuth continue | 4 | 21/34/47 | 18500/13452/15709 | 45644/26332/30996 | 无法支持正面 claim |
| bismuth continue | 8 | 21/34/47 | 11693/11193/17587 | 24672/23368/35324 | 无法支持正面 claim |
| coral continue | 1/4/8 | 15/21/27 | steps=8 时 1784/2684/4179 | steps=8 时 3014/4608/7428 | 规模偏小，且无连通性指标 |
| vine fork | 1/4/8 | 14/22/30 | steps=4 时 80/345/481；steps=8 时 462/525/794 | steps=4 时 22/196/294；steps=8 时 408/498/690 | 更像负例：mesh 过小，不能体现递归增长质量 |
| pyrite fork | 4 | 32/54/74 | 8331/15520/20411 | 16576/30436/39958 | 只有一个 steps=4 版本，无连通性指标 |

建议写入 appendix/limitation：global flow/SDE repair 在当前证据中尚未形成可量化 connectivity 改善；它更适合作为“模型先验修复不等同于递归结构保持”的负/边界结果。不要把 flow/SDE 作为主文正面 baseline。

## 特别判断：能否写进主文

- `coral`：可以写进主文，但只用 `fork_side_attach + sparse_close` 的 depth=3 正面结果。依据是 occ=1、occ_lcr=1、face=1、face_lcr=1，且已有 textured GLB 数值。`compete_fork_attach` 同 case 必须作为 appendix 边界或 discussion。
- `bismuth`：可以写进主文的 occupancy-primary 正面，尤其 method compare 中有全连通结果；但 depth=2 新结果中 `sparse_close` 是 occ=1、face=6，`sparse_close_bridge` 是 occ=5、face=2，所以正文不能笼统写“bismuth always fully connected at mesh and occupancy levels”。
- `pyrite`：不建议作为主文正面核心。method compare 可作边界正面，但 depth=2 与 close grid 显示 occ component 仍为 3-99，参数敏感明显。适合 appendix 展示“occupancy 与 face 不等价、bridge 参数非单调”。
- `hard-DLA`：不能写主文正面。raw occ_lcr≈0.38，best sparse_close_bridge occ_lcr≈0.738 且 occ=4；只适合 appendix 负例。
- `flow/SDE`：不能写主文正面。当前没有 connectivity component 指标，且 vine/coral mesh 规模偏小；适合 appendix 负例或“仍需补跑”。

## 论文实验表格建议

1. 主文 Table 1：Occupancy-primary connectivity table。列：case、grammar、method、depth、occ comp、occ LCR、face comp、face LCR、verts/faces。行只放 coral fork+sparse_close、bismuth selected positive、projection vine per-depth、以及对应 no-projection/final-only controls。
2. 主文 Table 2 或 compact ablation：Projection variants。列：case、variant、component_count、LCR、verts/faces、main_text_ready。重点放 `vine_compete_d3` 的 no_projection / final_only / per_depth；fork variants 放 appendix。
3. Appendix Table A：Boundary/failure matrix。放 pyrite grid、hard-DLA、DLA voxel root、coral compete_fork_attach、flow/SDE。
4. Figure-only pages：只放 GLB/Blender fixed-camera strip，不放 matplotlib 点云。建议用 coral positive、bismuth occupancy-positive、projection vine ablation 三组。

## 下一轮最小补实验清单

1. 对 `coral fork_side_attach sparse_close` 和 `bismuth selected positive` 做 fixed-camera Blender/GLB strip，确保主文视觉和表格一一对应。
2. 补一个 matched `model_bridge` 或 `traditional_repair` projection matrix case，至少在 `vine_compete_d3` 同 case 上跑，避免 projection 表里 repair baseline 为空。
3. 对 flow/SDE 输出补同一套 mesh/occupancy connectivity evaluator；如果仍无改善，就作为负例闭环。
4. Pyrite 只需最小补一轮参数确认：固定 depth=2，比较 close2/close5 与 bridge radius；若仍非单调，停止追正面，转 appendix。
5. Hard-DLA 不建议继续投入主文补跑；除非需要专门 limitation figure，否则现有负例数值已足够。
