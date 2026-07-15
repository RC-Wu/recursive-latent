# V24 strict one-to-one 三 seed QA 推荐

日期：2026-05-10

## 0. 证据文件

- rows: `results/strict_visual_matched_texture_V24_priority_rerun_seed3_rows_20260510.csv`
- comparison: `results/strict_visual_matched_texture_V24_priority_rerun_seed3_comparison_20260510.csv`
- json: `results/strict_visual_matched_texture_V24_priority_rerun_seed3_comparison_20260510.json`
- metrics 输入：V24 priority rerun 的 `seed20260510/20260511/20260512` 三批 `surface_metrics_occ64.csv`。
- seed3 白底 zoom contact sheet：`visuals/strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510/strict_visual_matched_texture_V24_priority_rerun_seed3_contact_sheet.png`

## 1. 总结论

V24 已经形成三 seed strict one-to-one 证据链，但主文要按稳定性分层展示：SC tree A、DLA staghorn、DLA frontier sheet、IFS radial 是三 seed r0 单连通；pyrite lattice 是 transform-copy/lattice 的最佳语义候选，但三 seed r0 有 3--4 个小 component，r1 单连通且 LCR 始终高于 0.9997；L-system/root fan A 视觉上仍有主文潜力，但第三 seed 仍是 2 个 r0 component，不能写成稳定拓扑主证据。

传统方法在本协议中不是失败 baseline。它们是 family target/control；V24 的比较目标是同类别递归形态、可渲染 GLB/PBR、post-GLB surface-connectivity floor 和局部 zoom 可读性。

## 2. 推荐主文/条件主文/附录

### 主文优先

- `V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA`：main-stable，3 seeds max comp r0=1，min LCR r0=1.000000。main。
- `V24_dla_frontier_sheet_700_open_boundary_polish_seedA`：main-stable，3 seeds max comp r0=1，min LCR r0=1.000000。main-or-secondary; strong metric backup for DLA/frontier。
- `V24_sc_tree_crown_260_attractor_clean_seedA`：main-stable，3 seeds max comp r0=1，min LCR r0=1.000000。main。

### 条件主文

- `V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA`：near-stable-high，3 seeds max comp r0=4，min LCR r0=0.999739。conditional-main for transform-copy/lattice if bridge-contact zoom passes。
- `V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA`：near-stable，3 seeds max comp r0=4，min LCR r0=0.998593。conditional-main for root visual only; needs fragment-invisibility zoom QA。

### 附录/鲁棒性

- `V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA`：main-stable，max comp r0=1，min LCR r0=1.000000；main-backup-or-appendix; strongest IFS metric。
- `V24_lsys_root_fan_d5_dense_rootlets_anchorB_seedB`：weak，max comp r0=6，min LCR r0=0.995962；appendix seed/root robustness; not main-stable。
- `V24_lsys_root_fan_d5_smooth_rootlets_anchorA_seedA`：weak，max comp r0=5，min LCR r0=0.997425；appendix fallback。
- `V24_lsys_root_fan_d5_smooth_rootlets_anchorB_seedB`：near-stable，max comp r0=5，min LCR r0=0.997666；appendix fallback。
- `V24_sc_root_network_260_anchorA_seedA`：near-stable，max comp r0=12，min LCR r0=0.998711；appendix root auxiliary; not a tree-canopy replacement。
- `V24_sc_root_network_260_anchorB_seedB`：near-stable，max comp r0=9，min LCR r0=0.998915；appendix root auxiliary; not a tree-canopy replacement。
- `V24_sc_tree_crown_260_attractor_clean_seedB`：near-stable，max comp r0=4，min LCR r0=0.999456；appendix SC robustness。
- `V24_sc_tree_crown_260_sparse_kill_clean_seedA`：near-stable-high，max comp r0=3，min LCR r0=0.999838；appendix SC robustness。
- `V24_sc_tree_crown_260_sparse_kill_clean_seedB`：near-stable-high，max comp r0=4，min LCR r0=0.999703；appendix SC robustness。

### 边界/不进主文

- `V24_dla_coral_cluster_900_lace_porosity_boundary_seedA`：boundary-tagged，max comp r0=10，min LCR r0=0.998634；appendix-boundary-only; do not use as main claim。

## 3. 表格

| case | family | runs | max comp r0 | min LCR r0 | max comp r1 | grade | recommendation |
|---|---|---:|---:|---:|---:|---|---|
| `V24_dla_coral_cluster_900_lace_porosity_boundary_seedA` | DLA/frontier | 3 | 10 | 0.998634 | 1 | boundary | appendix-boundary-only; do not use as main claim |
| `V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA` | DLA/frontier | 3 | 1 | 1.000000 | 1 | main-stable | main |
| `V24_dla_frontier_sheet_700_open_boundary_polish_seedA` | DLA/frontier | 3 | 1 | 1.000000 | 1 | main-stable | main-or-secondary; strong metric backup for DLA/frontier |
| `V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA` | IFS/transform | 3 | 4 | 0.999739 | 1 | near-stable-high | conditional-main for transform-copy/lattice if bridge-contact zoom passes |
| `V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA` | IFS/transform | 3 | 1 | 1.000000 | 1 | main-stable | main-backup-or-appendix; strongest IFS metric |
| `V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA` | L-system | 3 | 4 | 0.998593 | 1 | near-stable | conditional-main for root visual only; needs fragment-invisibility zoom QA |
| `V24_lsys_root_fan_d5_dense_rootlets_anchorB_seedB` | L-system | 3 | 6 | 0.995962 | 1 | weak | appendix seed/root robustness; not main-stable |
| `V24_lsys_root_fan_d5_smooth_rootlets_anchorA_seedA` | L-system | 3 | 5 | 0.997425 | 1 | weak | appendix fallback |
| `V24_lsys_root_fan_d5_smooth_rootlets_anchorB_seedB` | L-system | 3 | 5 | 0.997666 | 1 | near-stable | appendix fallback |
| `V24_sc_root_network_260_anchorA_seedA` | Space colonization | 3 | 12 | 0.998711 | 1 | near-stable | appendix root auxiliary; not a tree-canopy replacement |
| `V24_sc_root_network_260_anchorB_seedB` | Space colonization | 3 | 9 | 0.998915 | 1 | near-stable | appendix root auxiliary; not a tree-canopy replacement |
| `V24_sc_tree_crown_260_attractor_clean_seedA` | Space colonization | 3 | 1 | 1.000000 | 1 | main-stable | main |
| `V24_sc_tree_crown_260_attractor_clean_seedB` | Space colonization | 3 | 4 | 0.999456 | 1 | near-stable | appendix SC robustness |
| `V24_sc_tree_crown_260_sparse_kill_clean_seedA` | Space colonization | 3 | 3 | 0.999838 | 1 | near-stable-high | appendix SC robustness |
| `V24_sc_tree_crown_260_sparse_kill_clean_seedB` | Space colonization | 3 | 4 | 0.999703 | 1 | near-stable-high | appendix SC robustness |

## 4. 论文口径

- 主文四格建议：SC tree A、DLA staghorn、IFS pyrite lattice 条件主文、L-system/root fan A 条件主文；若 root fan zoom 不能遮蔽小碎片，则用 DLA frontier sheet 或 IFS radial 替换 root 主文位。
- Pyrite lattice 的路径：`visuals/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510/V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA_steps8_tex2048_seed20284526_xformers/textured.glb`。早期 V21 pyrite 路径另见 `visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_20260510/`。
- 不写 strict equivariance；写 empirical operator admission/screening。
- 不写 traditional baselines broken；写 controlled family targets。
- Surface voxel metrics 是 post-GLB renderability/connectivity diagnostics，不是 watertight topology proof。

## 5. Seed3 白底 zoom 目视 QA

已完成本地 Blender/Cycles seed3 白底相机 zoom 和系统 Python callout 后处理。每个候选均有 `overview_raw.png`、`overview_callouts.png`、`zoom_01.png`、`zoom_01_callouts.png`、`zoom_02.png`、`strict_matched_zoom_comparison.png`，总图为：

`visuals/strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510/strict_visual_matched_texture_V24_priority_rerun_seed3_contact_sheet.png`

像素 QA：contact sheet 为 `(2600, 7126)`，非白像素约 `0.1715`，各 case comparison 非白像素约 `0.0848--0.2685`，均非空白图。

目视排序：

- `V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA`：视觉最接近 transform-copy / pyrite-lattice 叙事，zoom 中 copy-contact 和 lattice beams 可读；尽管 r0 有 tiny islands，适合条件主文，caption 需写 `r1-connected, tiny r0 islands`。
- `V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA` / `anchorB_seedB`：root/rootlet 视觉比指标更强，细根可读；但 r0 不稳定，不能作为拓扑主证据。若主文需要 root 对比，建议写成 visual family panel + connectivity caveat。
- `V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA` 与 `V24_dla_frontier_sheet_700_open_boundary_polish_seedA`：三 seed 指标最稳，能支撑 DLA/frontier-style asset readiness；但 zoom 中端部和 frontier spikes 偏几何化，不写 natural coral simulation。
- `V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA`：指标最稳、形态干净，但严格 pyrite/lattice story 不如 pyrite 直接；适合 appendix 或 pyrite 主图失败时替换。
- `V24_sc_tree_crown_260_attractor_clean_seedA`：指标主稳，但 zoom 中可见粗黑 trunk / block-like tube，主文使用时应强调 space-colonization crown/control matching，不把它当自然树冠视觉强例。
