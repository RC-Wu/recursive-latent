# V23 All-Family Three-Seed Stability Summary
日期：2026-05-10 17:08 CST
输入：三个 V23 strict matched all-family Trellis2 GLB/PBR seed sweeps。指标为 surface-sampled occupancy voxel connectivity at resolution 64。
## 总结
- `main-stable`: 7 cases：`V23_dla_coral_cluster_900_staghorn_frontier`, `V23_dla_crystal_cluster_520_faceted_frontier`, `V23_dla_frontier_sheet_700_open_boundary`, `V23_ifs_branch_ornament_d5_contact_facets`, `V23_ifs_radial_ornament_o8_d4_orbit_spokes`, `V23_lsys_pine_canopy_d5_multi_root_smooth_needles`, `V23_sc_bush_shell_220_attractor_leaf_shell`
- `near-stable`: 5 cases：`V23_dla_coral_cluster_900_lace_porosity_variant`, `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges`, `V23_ifs_fractal_tree_d5_branch_copy`, `V23_sc_tree_crown_260_attractor_leaf_shell`, `V23_sc_tree_crown_260_sparse_kill_variant`
- `appendix-stable`: 4 cases：`V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils`, `V23_lsys_root_fan_d5_dense_rootlets_variant`, `V23_lsys_root_fan_d5_multi_root_smooth_rootlets`, `V23_sc_root_network_260_attractor_rootlets`

## 三 seed 汇总表
| case | family | seeds | min LCR r0 | mean LCR r0 | max comp r0 | all r1 single | mean occupied | mean vertices | mean faces | verdict |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| `V23_dla_coral_cluster_900_staghorn_frontier` | DLA/frontier | 3 | 1.000000 | 1.000000 | 1 | True | 5868.7 | 13992.0 | 11137.3 | main-stable |
| `V23_dla_crystal_cluster_520_faceted_frontier` | DLA/frontier | 3 | 1.000000 | 1.000000 | 1 | True | 2780.0 | 6280.7 | 3479.7 | main-stable |
| `V23_dla_frontier_sheet_700_open_boundary` | DLA/frontier | 3 | 1.000000 | 1.000000 | 1 | True | 2292.0 | 9689.0 | 7073.0 | main-stable |
| `V23_dla_coral_cluster_900_lace_porosity_variant` | DLA/frontier | 3 | 0.999150 | 0.999362 | 7 | True | 6551.0 | 16079.7 | 11214.3 | near-stable |
| `V23_ifs_branch_ornament_d5_contact_facets` | IFS/transform | 3 | 0.999485 | 0.999652 | 3 | True | 3818.7 | 11636.0 | 6980.0 | main-stable |
| `V23_ifs_radial_ornament_o8_d4_orbit_spokes` | IFS/transform | 3 | 0.999888 | 0.999963 | 2 | True | 9040.3 | 18554.0 | 13053.0 | main-stable |
| `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges` | IFS/transform | 3 | 0.999739 | 0.999742 | 4 | True | 11631.3 | 28641.0 | 18618.0 | near-stable |
| `V23_ifs_fractal_tree_d5_branch_copy` | IFS/transform | 3 | 0.999228 | 0.999568 | 4 | True | 3838.7 | 11630.0 | 6980.0 | near-stable |
| `V23_lsys_pine_canopy_d5_multi_root_smooth_needles` | L-system | 3 | 0.999703 | 0.999810 | 2 | True | 3526.7 | 21678.7 | 14372.0 | main-stable |
| `V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils` | L-system | 3 | 0.998551 | 0.998783 | 3 | True | 1362.3 | 23620.0 | 12588.0 | appendix-stable |
| `V23_lsys_root_fan_d5_dense_rootlets_variant` | L-system | 3 | 0.997882 | 0.999187 | 5 | True | 3009.0 | 21784.0 | 15168.0 | appendix-stable |
| `V23_lsys_root_fan_d5_multi_root_smooth_rootlets` | L-system | 3 | 0.998854 | 0.999397 | 3 | True | 2883.3 | 21821.3 | 15168.0 | appendix-stable |
| `V23_sc_bush_shell_220_attractor_leaf_shell` | Space colonization | 3 | 0.999801 | 0.999911 | 3 | True | 15263.3 | 109571.3 | 76024.0 | main-stable |
| `V23_sc_tree_crown_260_attractor_leaf_shell` | Space colonization | 3 | 0.999372 | 0.999739 | 7 | True | 12782.3 | 96484.0 | 71804.7 | near-stable |
| `V23_sc_tree_crown_260_sparse_kill_variant` | Space colonization | 3 | 0.999683 | 0.999790 | 5 | True | 12771.3 | 101178.0 | 75521.3 | near-stable |
| `V23_sc_root_network_260_attractor_rootlets` | Space colonization | 3 | 0.998814 | 0.999227 | 13 | True | 16180.7 | 102367.0 | 78716.7 | appendix-stable |

## 推荐主文/附录使用
- 主文结构稳定池：DLA staghorn/frontier/crystal、L-system pine、IFS radial、SC bush。它们仍需人工视觉 QA 和 family-specific metrics，不能只靠 LCR 入主文。
- near-stable 但叙事价值高：pyrite lattice、IFS branch-tree、SC tree crown/sparse-kill。pyrite/radial 适合 transform admission；branch-tree 适合作为 boundary/negative，不宜硬写成功。
- appendix-stable：root fan、vine、SC root-network。它们可以支撑 robustness/status，但若想入主文需要更好的 root/guide 或 family-specific orphan/rootlet metrics。

## 下一步指标
- L-system：visible depth、terminal/tip survival、needle/rootlet attachment、path-to-root。
- Space colonization：attractor coverage、nearest-attractor distance、alive/killed attractors、terminal root reachability。
- DLA/frontier：frontier/tip survival、neck/porosity、blockiness、bridge/contact survival。
- IFS/transform：orbit error、symmetry IoU、copy-contact survival、lattice/radial contract readability。
