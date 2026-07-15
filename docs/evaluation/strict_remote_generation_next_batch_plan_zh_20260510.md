# Strict remote generation next batch plan

日期：2026-05-10

范围：只规划，不启动远端任务。目标机器仍是 `a100-2`，只使用 GPU `4,5,6,7`。本文不修改生成脚本、不改 `paper_siga/main.tex`，只给下一批应跑的 case/root/参数和对应论文 claim。

## 0. 执行原则

下一批不应再扩大为“所有漂亮 case 都跑”。应按 strict one-to-one protocol 固定任务，补齐当前最影响论文结论的缺口：

1. 四类传统方法每类至少一个 paper-grade exemplar。
2. 每个 exemplar 至少有 3 个 seed/root/operator setting，记录 selection budget。
3. 每个结果先过硬门槛：`C_r<=2`、`LCR_r>=0.98`、`RAR_r>=0.95`、GLB import/render 成功、metadata 完整。
4. 再过 family metric：L-system branch/root hierarchy、SC attractor coverage、DLA frontier survival/blockiness、IFS orbit/symmetry/contact。
5. 最后做 white overview + root/junction/tip 或 frontier/facet camera zoom + human QA。只有 `paper-grade` 进入主文。

## 1. 下一批推荐队列

### 1.1 GPU 分配总表

| GPU | 优先任务 | 推荐 case/root | 参数/控制 | 主要 claim |
|---|---|---|---|---|
| 4 | L-system pine + SC tree + DLA coral | `v6_lsys_pine_canopy_d5_same_rule_welded_needles`; `v6_sc_tree_crown_260_same_attractor_welded_leaf_shell`; `v12_dla_tapered_staghorn_coral_a`; V8 `v8_dla_coral_lace_reef_branching_a` 对照 | L-system depth=5, branch_nodes=122, attached_needles=324; SC iterations=260, attractor_count=1500, influence_radius=0.24, kill_radius=0.055, step=0.045; DLA active-tip/frontier exclusion, V12 thin_tip_radius_max≈0.027, generated_nodes=144 | L-system tree/canopy strict evidence; SC tree-crown attractor competition; selected DLA coral frontier-attachment asset |
| 5 | L-system root + SC root + DLA coral alternate + IFS radial | `v6_lsys_root_fan_d5_same_rule_welded_hairs`; `v6_sc_root_network_260_same_attractor_welded_rootlets`; `v12_dla_tapered_staghorn_coral_b`; `v6_ifs_radial_ornament_o8_d4_connected_facets` | root depth=5, root_nodes=122, attached_root_hairs=348; SC iterations=260, attractor_count=1500, covered_attractors=1448; DLA generated_nodes=97; IFS order=8, depth=4, bridge_nodes=24, tooth_nodes=32 | Root fan rewriting; SC root network coverage; DLA seed robustness; empirical radial transform-copy |
| 6 | L-system vine backup + SC bush backup + DLA table + IFS lattice | `v6_lsys_climbing_vine_d6_same_curl_attached_leaves`; `v6_sc_bush_shell_220_same_attractor_welded_shell`; `v12_dla_tapered_table_coral_a`; `v6_ifs_fractal_lattice_d4_connected_copy_facets` | vine iterations=6, curl_step=0.82, attached_leaf_cards=6; bush iterations=220, attractor_count=1300, influence_radius=0.23, kill_radius=0.06; DLA table generated_nodes=113; IFS affine_children_per_node=4, depth=4, bridge_edges=90 | Vine only as backup/candidate swap; SC bush supplement; DLA table coral variant; IFS lattice/orbit positive |
| 7 | Missing IFS tree + DLA frontier/crystal boundary | New `ifs_fractal_tree_d5` / `ifs_branch_tree_d6` transform-copy branch asset; `v12_dla_tapered_frontier_plate_a`; `v12_dla_tapered_crystal_a`; optional V8 `v8_dla_frontier_fan_lace_membrane_a` | IFS tree: contractive branch transforms, depth=5 or d6, scale decay, rotate/copy, contact bridges; DLA frontier plate generated_nodes≈frontier mode, thin_tip_radius_max≈0.027; crystal mode with facet/ridge QA | Close IFS tree gap if implemented; DLA frontier sheet appendix/stress; crystal as boundary case, not physical claim |

说明：V6 rows 已有 remote input manifest 和 gallery 图，可作为 L-system/SC/IFS 的下一批复跑/多 seed 基线。V12 是当前 DLA/coral 下一批最稳候选；V8 lace/antler 应保留为 frontier-rich 对照，因为 V12 更 readable 但可能过 smooth。

## 2. Per-family run details

### 2.1 L-system

| case | root/source | 必保参数 | 需要新增的选择维度 | 对应 claim |
|---|---|---|---|---|
| `v6_lsys_pine_canopy_d5_same_rule_welded_needles` | `baseline_matrix_20260509.lsystem_case(tree)`；V6 guide `v6_conifer_same_lsystem_guide.png` | depth=5, branch_nodes=122, attached_needles=324, welded tapered skeleton, shared junction fans | 至少 3 seeds：原 seed `20260611` + 两个新 seed；可微调 needle density、branch angle jitter、local smooth envelope panels，但不能改成 blob canopy | selected PS-RSLG instantiates a finite-depth L-system pine/canopy task with visible trunk-whorl-needle hierarchy |
| `v6_lsys_root_fan_d5_same_rule_welded_hairs` | `baseline_matrix_20260509.lsystem_case(root)`；V6 root hierarchy guide | depth=5, root_nodes=122, attached_root_hairs=348, downward/root fan grammar | 原 seed `20260612` + 两个新 seed；调 root hair density、root taper、branch angle spread；记录 PTR/RAR | selected PS-RSLG instantiates root-fan rewriting with attached rootlets and generator-native surface |
| `v6_lsys_climbing_vine_d6_same_curl_attached_leaves` | hand-authored L-system vine equivalent | iterations=6, curl_step_radians=0.82, attached_leaf_cards=6 | 仅作为 backup：若跑，增加 leaf/tendril count 与 attachment QA；不要替代 root/pine 主行 | climbing-vine selected evidence only if weak strict vine issue is fixed |

必须补的指标：branch angle distribution、branch length decay、terminal density、PTR、surface-sampled LCR/RAR、root/junction/tip zoom verdict。

### 2.2 Space colonization

| case | root/source | 必保参数 | 需要新增的选择维度 | 对应 claim |
|---|---|---|---|---|
| `v6_sc_tree_crown_260_same_attractor_welded_leaf_shell` | `space_colonization_baseline.grow_space_colonization`, mode `tree_canopy` | iterations=260, attractor_count=1500, influence_radius=0.24, kill_radius=0.055, step_size=0.045, covered_attractors=1460 | 原 seed `20260621` + 两个新 seed；允许调 terminal leaf density、branch taper，但 attractor field 语义不变 | matched attractor-competition tree-crown task with generator-native connected surface/material |
| `v6_sc_root_network_260_same_attractor_welded_rootlets` | same SC baseline, mode `root_vine` | iterations=260, attractor_count=1500, covered_attractors=1448, attached_terminal_children=250 | 原 seed `20260622` + 两个新 seed；调 rootlet density、below-ground spread、projection radius | matched SC root network with root-attached attractor coverage |
| `v6_sc_bush_shell_220_same_attractor_welded_shell` | same SC baseline, mode `bush_shell` | iterations=220, attractor_count=1300, influence_radius=0.23, kill_radius=0.06, covered_attractors=1266 | backup/supplement；重点检查 shell 是否变成实心 blob | SC shell coverage as supplement, not main claim |

必须补的指标：attractor coverage、nearest-attractor distance、alive/covered attractors、terminal path-to-root、shell thickness/blob negative QA。

### 2.3 DLA / frontier

| case | root/source | 必保参数 | 推荐角色 | 对应 claim |
|---|---|---|---|---|
| `v12_dla_tapered_staghorn_coral_a` | `assets/strict_visual_matched_cases_v12_tapered_staghorn_20260510.py`, mode `staghorn` | target `dla_coral_cluster_900`; active-tip frontier expansion; occupancy exclusion; generated_nodes=144; max_depth=5; thin_tip_radius_max≈0.027 | 主候选 1 | selected frontier-attachment coral asset with tapered terminal continuations |
| `v12_dla_tapered_staghorn_coral_b` | same, mode `staghorn` | generated_nodes=97; same controls | seed robustness / alternate | same claim, selection-budget transparency |
| `v12_dla_tapered_table_coral_a` / `b` | same, mode `table` | generated_nodes=113/150; plate-like branches; active-tip frontier | table-coral alternate | selected DLA coral-cluster variant with readable plate-like frontier support |
| `v8_dla_coral_lace_reef_branching_a` | V8 frontier refine | stochastic frontier attachment, occupancy exclusion, porous/lace branching | frontier-rich comparator | V8 retains more accretive lace/pore detail than V12; useful if V12 is too smooth |
| `v8_dla_coral_antler_ridge_branching` | V8 frontier refine | open branching and tip structure | alternate comparator | clearer branch silhouettes under same DLA coral task |
| `v12_dla_tapered_frontier_plate_a` | V12 mode `frontier` | target `dla_frontier_sheet_700`; tapered plate support | appendix/stress | boundary/frontier sheet asset evidence |
| `v12_dla_tapered_crystal_a` | V12 mode `crystal` | target `dla_crystal_cluster_520`; clean tapered branch/facet support | boundary/appendix | accretive crystal-frontier boundary, not physical crystal growth |

不建议再优先投入 V9 全量复跑。V9 两套 seed 已有 24 个 `status=ok` summary，下一步应先筛视觉和指标，而不是继续扩大。V10/V11 可作为 readable fallback；V12 是下一批 DLA 主线，V8 是保留 frontier richness 的对照。

必须补的指标：frontier attachment survival、LCR/RAR、bridge cost、orphan mass、blockiness score、porosity/cavity proxy、tip/neck count、human QA。

### 2.4 IFS / transform-copy

| case | root/source | 必保参数 | 需要新增的选择维度 | 对应 claim |
|---|---|---|---|---|
| `v6_ifs_radial_ornament_o8_d4_connected_facets` | V6 radial IFS transform-copy graph | order=8, depth=4, bridge_nodes=24, tooth_nodes=32, closed rings, inter-depth spokes | 原 seed `20260642` + 两个新 seed；调 contact threshold/facet size，但必须保留 order-8 orbit | empirical radial transform-copy evidence with connected orbit/contact projection |
| `v6_ifs_fractal_lattice_d4_connected_copy_facets` | V6 affine IFS lattice expansion | affine_children_per_node=4, depth=4, bridge_edges=90 | 原 seed `20260643` + 两个新 seed；调 lattice spacing/contact bridges/facet plates | finite transform-copy lattice/orbit evidence; pyrite allowed only under lattice task |
| New `ifs_fractal_tree_d5` or `ifs_branch_tree_d6` | 新建/启用 transform-copy branch motif root，不能用 pyrite | contractive branch transforms, scale decay, rotate/copy, depth=5 or d6, contact bridges, branch hierarchy | 这是当前最大 IFS 缺口；建议 GPU 7 跑 3 seeds；若来不及实现，则在 gap table 明确 missing，不进主文 | only this can support IFS tree matching; without it, no IFS tree positive claim |

必须补的指标：orbit error、symmetry IoU、self-similarity、contact bridge survival、post-GLB LCR/RAR。文本必须写 empirical consistency，不能写 Trellis2 严格 equivariant。

## 3. 建议最小批次

如果只能跑最小集，建议 12 个：

| family | cases |
|---|---|
| L-system | `v6_lsys_pine_canopy_d5_same_rule_welded_needles` seeds x3；`v6_lsys_root_fan_d5_same_rule_welded_hairs` seeds x3 任选其一进主文 |
| SC | `v6_sc_tree_crown_260_same_attractor_welded_leaf_shell` seeds x3；`v6_sc_root_network_260_same_attractor_welded_rootlets` seeds x3 任选其一进主文 |
| DLA | `v12_dla_tapered_staghorn_coral_a/b` + `v12_dla_tapered_table_coral_a` + V8 `v8_dla_coral_lace_reef_branching_a` 对照 |
| IFS | `v6_ifs_fractal_lattice_d4_connected_copy_facets` seeds x3；`v6_ifs_radial_ornament_o8_d4_connected_facets` seeds x3；若能补新 tree IFS，则替换 radial 的一个 seed |

如果时间更紧，主文四行最小组合应是：

1. `lsys_root_fan_d5` -> `v6_lsys_root_fan_d5_same_rule_welded_hairs` 多 seed 最优。
2. `sc_root_network_260` -> `v6_sc_root_network_260_same_attractor_welded_rootlets` 多 seed 最优。
3. `dla_coral_cluster_900` -> `v12_dla_tapered_staghorn_coral_a/b` 与 V8 lace 对照后选。
4. `ifs_fractal_lattice_d4` -> `v6_ifs_fractal_lattice_d4_connected_copy_facets` 多 seed 最优。

## 4. 输出包要求

每个最终候选必须落成同一证据包：

```text
case_id
traditional_task
root/source provenance
operator_composition
control_parameters
remote_target = a100-2
gpu_group = 4/5/6/7
seed
selection_budget
textured_glb_path
white overview raw
overview callout
camera zoom root/attachment
camera zoom junction/contact/frontier neck
camera zoom terminal tip/pore/facet/orbit
metrics_csv row
human_qa verdict
allowed_claim
disallowed_claim
```

## 5. Claim mapping

| case group | 可支撑 claim | 明确不能支撑 |
|---|---|---|
| L-system pine/root | finite-depth rewriting controls can be instantiated through PS-RSLG roots/operators with connected local naturalization | universal superiority over L-system; infinite recursion; texture-only hierarchy |
| SC tree/root | attractor competition can control generator-native connected tree/root assets while preserving coverage/path-to-root | SC baseline is weak; ordinary branch grammar equals SC |
| DLA coral/frontier | selected frontier-attachment assets can be made connected, readable, and zoomable under strict task controls | physical DLA, real coral growth, real crystallization |
| IFS radial/lattice | finite transform-copy/orbit/lattice tasks can be represented with contact projection and empirical symmetry/orbit diagnostics | Trellis2 strict equivariance; pyrite proves IFS tree |
| New IFS tree | only if generated and QA-passed, supports transform-copy branch/tree matching | cannot be substituted by lattice/pyrite |

## 6. Do-not-run-yet notes

本文是 plan，不是 launch log。执行前还需要：

- 确认 `a100-2` GPU 4/5/6/7 空闲；
- 确认 `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507` 存储余量；
- 为 L-system/SC/IFS 生成或确认多 seed input manifests；
- 决定是否实现新的 `ifs_fractal_tree_d5` / `ifs_branch_tree_d6` case；
- 跑完后再生成统一 metrics + zoom + QA verdict 表。
