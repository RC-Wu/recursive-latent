# V24 strict traditional baseline 一对一评估闭合建议

日期：2026-05-10

## 0. 读取证据

本轮只读并交叉核对以下证据，不使用远端 SSH，不修改 `paper_siga/main.tex`，不触碰 masked naturalization 文件：

- `docs/evaluation/strict_visual_matched_V24_priority_rerun_results_zh_20260510.md`
- `results/strict_visual_matched_texture_V24_priority_rerun_20260510_remote/surface_metrics_occ64.csv`
- `results/strict_visual_matched_texture_V24_priority_rerun_20260510_remote/inputs/manifest.csv`
- `case_gallery_for_user_20260509/06_baselines_metrics_ablation`
- `results/baseline_one_to_one_surface_metrics_20260510/surface_metrics_occ64.csv`
- `results/baseline_one_to_one_clip_metrics_20260510/multiview_clip_prompt_scores.csv`

新增机器可读汇总：

- `results/strict_visual_matched_texture_V24_priority_rerun_20260510_remote/v24_one_to_one_recommendation_metrics_20260510.csv`
- `results/strict_visual_matched_texture_V24_priority_rerun_20260510_remote/v24_one_to_one_recommendation_metrics_20260510.json`

生成脚本：

- `assets/scripts/v24_qa_one_to_one_summary_20260510.py`

## 1. 核心结论

V24 priority rerun 已足够支撑 strict traditional baseline / V24 一对一闭合，但论文展示应采用“受控 family target 对齐”而不是“baseline 失败对照”的叙事。原因是 traditional one-to-one baselines 的 surface-sampled connectivity 很高：`lsystem_branch_baseline` 为 3 / 0.999711，`sc_tree_canopy_baseline` 为 1 / 1.0，`dla_cluster_baseline` 为 3 / 0.999840，`ifs_branch_tree_baseline` 为 1 / 1.0。

因此主 claim 应写成：

> Traditional procedural baselines provide controlled family targets and often remain connected. The comparison asks whether V24 R-SLG outputs preserve the same family-specific recursive morphology after generative texturing/export, while maintaining a comparable connectivity floor.

中文写法：传统方法不是弱连通 baseline；它们是 L-system / SC / DLA-frontier / IFS 的受控目标。V24 的亮点是生成模型输出仍保留对应 family 的递归形态线索，并通过 post-GLB surface connectivity QA。

## 2. 类别级一对一推荐清单

| 类别 | traditional pair | V24 主推荐 | seed2 / backup | appendix | 丢弃或仅边界 | 结论 |
|---|---|---|---|---|---|---|
| L-system/root | `lsystem_branch_baseline` | `V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA` | `V24_lsys_root_fan_d5_dense_rootlets_anchorB_seedB` | `V24_lsys_root_fan_d5_smooth_rootlets_anchorA_seedA`, `V24_lsys_root_fan_d5_smooth_rootlets_anchorB_seedB` | none | 主文用 dense A，dense B 放 seed2 robustness；smooth 两个只做 appendix fallback。 |
| Space colonization tree | `sc_tree_canopy_baseline` | `V24_sc_tree_crown_260_attractor_clean_seedA` | `V24_sc_tree_crown_260_attractor_clean_seedB` | `V24_sc_tree_crown_260_sparse_kill_clean_seedA`, `V24_sc_tree_crown_260_sparse_kill_clean_seedB` | none | 主文用 attractor A；seedB/sparse-kill 证明 rerun family 稳定但不抢主位。 |
| Space colonization root | `sc_tree_canopy_baseline` as SC family control | none for main | `V24_sc_root_network_260_anchorB_seedB` over anchorA if root close-up cleaner | `V24_sc_root_network_260_anchorA_seedA`, `V24_sc_root_network_260_anchorB_seedB` | not main until visible-fragment QA passes | root network 是 V24 缺口补齐，不应替代 SC tree 主文；可在 appendix 作为 root-specific auxiliary。 |
| DLA/frontier | `dla_cluster_baseline` | `V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA` | none | `V24_dla_frontier_sheet_700_open_boundary_polish_seedA` | `V24_dla_coral_cluster_900_lace_porosity_boundary_seedA` only if fragment invisibility QA passes | staghorn polish 是主文 DLA/frontier 正例；frontier sheet 可做小图或 appendix；lace boundary 不进主文。 |
| IFS/pyrite | `ifs_branch_tree_baseline` | `V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA` if bridge-contact zoom passes | none | same case if bridge-contact zoom looks mechanical | none | pyrite lattice 是 strict transform-copy/pyrite 对齐主候选，但必须用 zoom 解释 contact bridges。 |
| IFS/radial | `ifs_branch_tree_baseline` as IFS family control | none by default | `V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA` | `V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA` | none | radial 指标最干净，适合 appendix 或替换式主文备选；不如 pyrite lattice 对 strict pyrite/lattice claim 直接。 |

## 3. 指标表

| category | V24 case | baseline pair | baseline comp/LCR r0 | V24 comp/LCR r0 | V24 comp/LCR r1 | grade | 推荐 |
|---|---|---|---:|---:|---:|---|---|
| L-system/root | `V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA` | `lsystem_branch_baseline` | 3 / 0.999711 | 1 / 1.000000 | 1 / 1.000000 | strong | main |
| L-system/root | `V24_lsys_root_fan_d5_dense_rootlets_anchorB_seedB` | `lsystem_branch_baseline` | 3 / 0.999711 | 1 / 1.000000 | 1 / 1.000000 | strong | appendix / seed2 robustness |
| L-system/root | `V24_lsys_root_fan_d5_smooth_rootlets_anchorA_seedA` | `lsystem_branch_baseline` | 3 / 0.999711 | 4 / 0.997951 | 1 / 1.000000 | near-stable | appendix fallback |
| L-system/root | `V24_lsys_root_fan_d5_smooth_rootlets_anchorB_seedB` | `lsystem_branch_baseline` | 3 / 0.999711 | 5 / 0.997666 | 1 / 1.000000 | near-stable | appendix fallback |
| SC/root | `V24_sc_root_network_260_anchorA_seedA` | `sc_tree_canopy_baseline` | 1 / 1.000000 | 8 / 0.998895 | 1 / 1.000000 | near-stable | appendix/root auxiliary |
| SC/root | `V24_sc_root_network_260_anchorB_seedB` | `sc_tree_canopy_baseline` | 1 / 1.000000 | 9 / 0.998915 | 1 / 1.000000 | near-stable | appendix/root auxiliary; prefer if visual crop cleaner |
| SC/tree | `V24_sc_tree_crown_260_attractor_clean_seedA` | `sc_tree_canopy_baseline` | 1 / 1.000000 | 1 / 1.000000 | 1 / 1.000000 | strong | main |
| SC/tree | `V24_sc_tree_crown_260_attractor_clean_seedB` | `sc_tree_canopy_baseline` | 1 / 1.000000 | 3 / 0.999838 | 1 / 1.000000 | near-stable | appendix / seed2 robustness |
| SC/tree | `V24_sc_tree_crown_260_sparse_kill_clean_seedA` | `sc_tree_canopy_baseline` | 1 / 1.000000 | 2 / 0.999919 | 1 / 1.000000 | near-stable | appendix backup |
| SC/tree | `V24_sc_tree_crown_260_sparse_kill_clean_seedB` | `sc_tree_canopy_baseline` | 1 / 1.000000 | 4 / 0.999703 | 1 / 1.000000 | near-stable | appendix backup |
| DLA/frontier | `V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA` | `dla_cluster_baseline` | 3 / 0.999840 | 1 / 1.000000 | 1 / 1.000000 | strong | main |
| DLA/frontier | `V24_dla_frontier_sheet_700_open_boundary_polish_seedA` | `dla_cluster_baseline` | 3 / 0.999840 | 1 / 1.000000 | 1 / 1.000000 | strong | appendix or small secondary panel |
| DLA/frontier | `V24_dla_coral_cluster_900_lace_porosity_boundary_seedA` | `dla_cluster_baseline` | 3 / 0.999840 | 10 / 0.998634 | 1 / 1.000000 | boundary | discard main; appendix only after fragment invisibility QA |
| IFS/pyrite | `V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA` | `ifs_branch_tree_baseline` | 1 / 1.000000 | 4 / 0.999739 | 1 / 1.000000 | near-stable | main if bridge-contact zoom passes; otherwise appendix |
| IFS/radial | `V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA` | `ifs_branch_tree_baseline` | 1 / 1.000000 | 1 / 1.000000 | 1 / 1.000000 | strong | appendix / IFS radial backup |

## 4. 论文展示策略

主文建议采用 4+2 结构：

1. 四个主文 family panel：
   - L-system/root：`dense_rootlets_anchorA_seedA`
   - SC/tree：`sc_tree_crown_260_attractor_clean_seedA`
   - DLA/frontier：`staghorn_frontier_polish_seedA`
   - IFS/pyrite：`pyrite_copy_bridges_polish_seedA`，前提是 bridge-contact zoom 通过人工 QA。
2. 两个 appendix/secondary panel：
   - `dense_rootlets_anchorB_seedB` 作为 seed2 robustness。
   - `ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA` 或 `dla_frontier_sheet_700_open_boundary_polish_seedA` 作为 family diversity / backup。

图像组织建议：

- 每个主 panel 放 traditional baseline overview + V24 overview + V24 local zoom。
- 不把 connectivity 当作唯一胜点；每个 caption 都写 family-specific morphology：rootlet attachment、attractor crown、frontier branch tip、transform-copy bridge。
- SC root network 不进主文四格；它适合 appendix 的 root-specific close-up，并明确不是 strict tree-canopy replacement。
- DLA lace boundary 不进主文。若 appendix 使用，caption 必须标 `boundary-tagged candidate`，且只在白底 zoom 中不可见碎片时使用。
- IFS radial 指标很干净，但与 pyrite/lattice claim 不如 lattice 直接；最佳位置是 appendix 或 pyrite zoom 失败时的替补。

## 5. 可写与不可写

可写：

- V24 priority rerun closes the strict one-to-one evaluation set for L-system/root, SC tree/root, DLA/frontier, and IFS transform variants.
- V24 outputs keep a comparable post-GLB surface connectivity floor while preserving family-specific recursive morphology.
- Boundary-tagged cases are separated from main claims.

不可写：

- 不说 traditional baselines are broken or fragmented。
- 不说 DLA 是物理扩散模拟；用 DLA/frontier-style 或 frontier-attachment asset generation。
- 不把 occ64 surface metric 写成拓扑证明；它是 post-GLB 渲染资产 QA。
- 不把 SC root network 当作 tree canopy baseline 的直接主文替代。
