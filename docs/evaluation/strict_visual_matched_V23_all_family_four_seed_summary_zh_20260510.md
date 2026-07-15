# V23 all-family 四 seed 稳定性摘要

日期：2026-05-10

- 输入 runs：4 个 V23 seed pool。
- 汇总 case：16。

| case | family | runs | min LCR r0 | max comp r0 | all r1 single | verdict |
|---|---|---:|---:|---:|---|---|
| `V23_dla_coral_cluster_900_lace_porosity_variant` | DLA/frontier | 4 | 0.998980 | 8 | True | appendix-stable-4seed |
| `V23_dla_coral_cluster_900_staghorn_frontier` | DLA/frontier | 4 | 1.000000 | 1 | True | main-stable-4seed |
| `V23_dla_crystal_cluster_520_faceted_frontier` | DLA/frontier | 4 | 1.000000 | 1 | True | main-stable-4seed |
| `V23_dla_frontier_sheet_700_open_boundary` | DLA/frontier | 4 | 1.000000 | 1 | True | main-stable-4seed |
| `V23_ifs_branch_ornament_d5_contact_facets` | IFS/transform | 4 | 0.999224 | 4 | True | near-stable-4seed |
| `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges` | IFS/transform | 4 | 0.999739 | 4 | True | near-stable-4seed |
| `V23_ifs_fractal_tree_d5_branch_copy` | IFS/transform | 4 | 0.998948 | 5 | True | boundary-control-4seed |
| `V23_ifs_radial_ornament_o8_d4_orbit_spokes` | IFS/transform | 4 | 0.999888 | 2 | True | main-stable-4seed |
| `V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils` | L-system | 4 | 0.994232 | 3 | True | appendix-stable-4seed |
| `V23_lsys_pine_canopy_d5_multi_root_smooth_needles` | L-system | 4 | 0.999138 | 2 | True | near-stable-4seed |
| `V23_lsys_root_fan_d5_dense_rootlets_variant` | L-system | 4 | 0.995420 | 9 | True | appendix-stable-4seed |
| `V23_lsys_root_fan_d5_multi_root_smooth_rootlets` | L-system | 4 | 0.998596 | 4 | True | appendix-stable-4seed |
| `V23_sc_bush_shell_220_attractor_leaf_shell` | Space colonization | 4 | 0.999801 | 3 | True | main-stable-4seed |
| `V23_sc_root_network_260_attractor_rootlets` | Space colonization | 4 | 0.998360 | 15 | True | appendix-stable-4seed |
| `V23_sc_tree_crown_260_attractor_leaf_shell` | Space colonization | 4 | 0.999372 | 7 | True | near-stable-4seed |
| `V23_sc_tree_crown_260_sparse_kill_variant` | Space colonization | 4 | 0.999637 | 5 | True | near-stable-4seed |

## 主文推荐

- L-system：`V23_lsys_pine_canopy_d5_multi_root_smooth_needles` 仍是主文第一候选。
- Space colonization：`V23_sc_tree_crown_260_attractor_leaf_shell` 最一对一，但视觉需保守；`V23_sc_bush_shell_220_attractor_leaf_shell` 作为稳定 appendix/备选。
- DLA/frontier：`V23_dla_coral_cluster_900_staghorn_frontier` 和 `V23_dla_frontier_sheet_700_open_boundary` 是最稳正例。
- IFS/transform：`V23_ifs_fractal_lattice_d4_pyrite_copy_bridges` 负责 lattice/pyrite 一对一；`V23_ifs_radial_ornament_o8_d4_orbit_spokes` 作为 orbit/radial 备选。

## 口径

四 seed 稳定性仍是筛选证据，不替代白底多级 zoom 的人工 QA；branch-tree 继续作为 transform admission 的 boundary/control，不作为 IFS tree 正例。
