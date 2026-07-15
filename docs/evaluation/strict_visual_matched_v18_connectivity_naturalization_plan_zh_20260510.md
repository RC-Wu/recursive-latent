# V18 DLA/Frontier/Crystal 连通自然化生成方案

本文档对应新增生成器：

`assets/strict_visual_matched_cases_v18_connectivity_naturalization_20260510.py`

目标是直接处理用户指出的问题：DLA 与非树结构在远程生成后容易碎成块，或读成杆/管/蘑菇帽/光滑晶体团。V18 不是对本地结果做筛选或后处理，而是在输入几何生成阶段把连通性和语义自然化写入算法。

## 严格匹配原则

- 远程优先：最终结果必须在 `a100-2` 上重新生成，GPU 限定为 `4/5/6/7`。
- 一对一比较：每个 case 都保留 `traditional_target`，用于和对应传统 DLA/frontier/crystal baseline 做严格一对一比较。
- 只交付 mesh/PBR：本地 dry-run 只产出 OBJ 输入、guide PNG、manifest 与初始 mesh 指标；远程 launcher 调用 `trellis2_texturing_export_glb.py` 生成 textured GLB/PBR。
- 禁止本地选择/后处理：metadata 中固定 `generate_new_on_a100_2_no_local_selection_or_postprocessing`，不允许用本地渲染挑选、修复或替代远程新生成。

## V18 算法变化

V18 的核心不是把输出 mesh 修补连通，而是在 marching cubes 前构造一个重叠的隐式场：

- `stochastic_frontier_attachment`：沿用 DLA/frontier 的随机活跃前沿增长。
- `occupancy_exclusion`：候选点在排斥半径内被拒绝，保持 DLA/space-competition 对照属性。
- `rooted_attachment_bridges`：从 root/低半径区域向多条分支加桥，避免主干碎裂。
- `loop_closure_bridges`：在非父子近邻节点之间加 loop bridge，让非树结构成为生成器原生连通支撑。
- `connected_implicit_support`：所有枝、桥、底座、孔洞、ridge、polyp、晶面都先写入同一个 implicit field，再 marching cubes。
- `naturalization_guides` 与 `pbr_material_prompt`：每个 case 有本地 guide image 和材质提示，但只作为远程 fresh PBR 生成输入。

## Case 矩阵

| case_id | traditional_target | motif | GPU |
|---|---:|---|---:|
| `v18_dla_coral_cluster_connected_polyps_a` | `dla_coral_cluster_900` | coral cluster | 4 |
| `v18_dla_coral_cluster_connected_polyps_b` | `dla_coral_cluster_900` | coral cluster | 5 |
| `v18_dla_frontier_sheet_connected_reef_edge` | `dla_frontier_sheet_700` | frontier sheet | 6 |
| `v18_dla_branching_reef_loop_closure_a` | `dla_branching_reef_650` | branching reef | 7 |
| `v18_dla_crystal_lattice_connected_facets` | `dla_crystal_lattice_520` | lattice crystal | 4 |
| `v18_dla_pyrite_orbit_connected_cubes` | `dla_pyrite_orbit_480` | pyrite-like orbit | 5 |
| `v18_dla_bismuth_stepped_connected_crystal` | `dla_bismuth_step_crystal_360` | bismuth-like stepped crystal | 6 |
| `v18_dla_frontier_sheet_seed_b_connected_lace` | `dla_frontier_sheet_700` | frontier sheet backup | 7 |

## Dry-run 指标

本地命令：

```bash
python3 assets/strict_visual_matched_cases_v18_connectivity_naturalization_20260510.py --root /Users/fanta/code/agent/Code/recursive_3d_generative_growth --out results/strict_visual_matched_cases_v18_connectivity_naturalization_20260510_dryrun --seed 20260510
```

结果摘要：

- case 数：8
- 每个 GPU 分配：GPU 4/5/6/7 各 2 个 case
- 所有 dry-run OBJ：`mesh_component_count = 1`
- 所有 dry-run OBJ：`largest_mesh_component_vertex_ratio = 1.0`
- bridge 数：coral/frontier/reef 为 24，其中 loop closure 为 16；crystal/pyrite/bismuth 为 20，其中 loop closure 为 12
- 顶点范围：2538 到 10102
- 面范围：5092 到 20328

## 与 V7/V8/V14/V16 的区别

- V7/V8：主要靠连续 skeleton、smooth tubes、branchlets、membranes 降低块状感；V18 进一步把 root bridge 与非树 loop bridge 写进隐式场，避免非树目标仍碎成 chunks。
- V14：已经是 r0-connected，但视觉上偏 faceted/coarse、容易低多边形粗枝；V18 使用更明确的语义 naturalization primitive，coral 有 pore/ridge/polyp，crystal 有 facet/orbit/step。
- V16：重点是 natural coral，crystal 只有泛化 faceted boundary；V18 扩展到 DLA/frontier/crystal 全组，增加 lattice crystal、pyrite orbit、bismuth stepped crystal，并显式记录 mesh/PBR-only 远程生成契约。

## 远程启动

将新增文件同步到远程根目录后，由调度者手动执行：

```bash
bash /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets/launch_strict_visual_matched_texture_v18_connectivity_naturalization_20260510.sh
```

launcher 约束：

- `ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`
- `RUN=strict_visual_matched_texture_v18_connectivity_naturalization_20260510`
- cache/TMP 全部在 `$ROOT/cache/...`
- worker 使用 `CUDA_VISIBLE_DEVICES="$gpu"`，GPU 为 4/5/6/7
- 已有 `summary.json` 且包含 `"status": "ok"` 时跳过
- 每个 worker 读取对应 `gpu${gpu}_cases.txt`
