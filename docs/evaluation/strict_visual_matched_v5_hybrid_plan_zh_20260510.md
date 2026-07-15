# Strict Visual Matched V5 Hybrid 计划（2026-05-10）

入口脚本：`assets/strict_visual_matched_cases_v5_hybrid_20260510.py`

dry-run 输出：`results/strict_visual_matched_cases_v5_hybrid_20260510_dryrun`

本批次只做本地输入生成和连通性初测，不启动远端任务。后续正式 Trellis2 生成目标仍是 `a100-2`，manifest、metadata 和 `a100-2_cases.txt` 已按这个目标写出。

## 目标

V5 只针对当前最弱的 8 个 case 重做输入，不覆盖全量 12 个 case：

- L-system：pine、root、vine。
- Space colonization：tree crown、root network。
- DLA/frontier：coral cluster、frontier sheet。
- IFS/transform：radial ornament。

V4 的主要问题是用连续 implicit support 解决了组件数，但容易把植物、根、DLA、frontier 和 radial 全局抹成 blob/blocky。V5 改为 hybrid explicit scaffold：先保留传统方法的递归/吸引/附着/变换图，再用共享边的 connector、bridge、spine、attachment tubelet 导出 OBJ。

## 生成原则

- 不使用全局 marching-cubes implicit 去包住整棵树或整团 DLA。
- 每个 parent-child edge 导出显式 tube。
- junction 处用 surface bridge ribbon 连接入射 tube，避免只共享空间接触或只共享顶点。
- needle、root hair、tendril、frontier tubelet 都作为主 scaffold 的 child edge，不再输出离散 card/sphere。
- radial ornament 用 closed ring cycles、shared center spine、inter-depth bridge spokes 和 teeth，保留 8-fold/depth-4 transform 读法。
- 每个 metadata 记录 `traditional_target`、`operator_composition`、`why_matches_traditional` 和 local dry-run provenance。

## dry-run 初测

8 个 case 均完成 OBJ、guide、manifest、metadata、initial_metrics 输出。初始 mesh 指标：

| case | target | components | LCR |
|---|---|---:|---:|
| `v5_lsys_pine_canopy_d5_welded_whorl_needles` | `lsys_pine_canopy_d5` | 1 | 1.000000 |
| `v5_lsys_root_fan_d5_welded_hair_hierarchy` | `lsys_root_fan_d5` | 1 | 1.000000 |
| `v5_lsys_climbing_vine_d6_welded_leaf_tendrils` | `lsys_climbing_vine_d6` | 1 | 1.000000 |
| `v5_sc_tree_crown_260_welded_branch_leaf_shell` | `sc_tree_crown_260` | 1 | 1.000000 |
| `v5_sc_root_network_260_welded_root_spurs` | `sc_root_network_260` | 1 | 1.000000 |
| `v5_dla_coral_cluster_900_welded_tube_frontier` | `dla_coral_cluster_900` | 1 | 1.000000 |
| `v5_dla_frontier_sheet_700_welded_boundary_reef` | `dla_frontier_sheet_700` | 1 | 1.000000 |
| `v5_ifs_radial_ornament_o8_d4_welded_ring_spokes` | `ifs_radial_ornament_o8_d4` | 1 | 1.000000 |

## 使用边界

V5 是 remote input dry-run，不是本地挑选结果，也不是远端 textured GLB。下一步应把脚本和 `a100-2_cases.txt` 同步到 `a100-2` 后重新运行 Trellis2，视觉判断重点看：

- pine 是否保留 whorl trunk、branch layer、needle 读法。
- root/SC root 是否有主根到细根的层级，而不是线团。
- vine 是否保留 helix main chain 和 tendril。
- SC crown 是否像 crown，而不是球形 blob。
- DLA coral/frontier 是否保留 accretive tube/frontier，而不是平滑团块。
- radial 是否保留 order-8 ring/teeth/depth structure。
