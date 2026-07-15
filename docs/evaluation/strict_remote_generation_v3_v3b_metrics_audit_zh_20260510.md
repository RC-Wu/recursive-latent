# V3/V3b 远端 Trellis2 textured GLB 指标审计（2026-05-10）

本文面向最新要求：**必须远端重新生成严格一对一匹配传统方法的 case，不能只是本地挑选或后处理**。本轮审计只读取已经完成的远端 Trellis2 textured GLB 指标与上下文文档，不修改生成器代码，不运行远端命令。

## 输入与证据边界

输入路径：

- V3 GLB：`visuals/strict_visual_matched_texture_v3_20260510`
- V3b GLB：`visuals/strict_visual_matched_texture_v3b_connected_20260510`
- V3 metrics：`results/strict_visual_matched_texture_v3_20260510_remote/surface_metrics_occ64.csv`
- V3b metrics：`results/strict_visual_matched_texture_v3b_connected_20260510_remote/surface_metrics_occ64.csv`
- 上下文：`docs/evaluation/strict_visual_v3_connectivity_risk_and_v3b_plan_zh_20260510.md`、`docs/evaluation/strict_matched_v3_metric_and_selection_plan_zh_20260510.md`、`docs/agentdoc_mirror/plans/recursive_3d_generative_growth_eval_naturalization_plan_20260510.md`

审计边界：

- 下表的 `components_r* / lcr_r* / occupied / box_dim_32_96` 来自远端 textured GLB 的 occ64 surface metrics。
- `components_r0` 是当前最严格的 occupancy 连通代理；`r1/r2` 是膨胀后的宽松 sanity check，不能单独证明原始拓扑。
- `box_dim_32_96` 是 32-96 多尺度 box-count 复杂度估计；数值越高通常表示占用分布更细碎/多尺度，但不是视觉质量或 family 正确性的直接证据。
- 本文没有人工逐张看图，不伪造视觉结论。所有“主文/补充/淘汰”建议只基于指标、manifest 算法描述和既有审计文档；进入论文前仍需 neutral render + camera zoom 人工 QA。

## V3 与 V3b 的算法差异

V3 是 strict visual matched screening run：每个 case 针对传统任务重写了目标控制，例如 pine 的 whorl/trunk/needle、root 的 thick-to-thin hierarchy、DLA 的 frontier-local implicit surface、IFS 的 transform/cache scaffold。V3 的问题是，部分 case 的本地输入网格仍来自很多 tube、card、tip sphere、leaf/root token 的 primitive 级拼接；这些 primitive 在远端 Trellis2 textured GLB 中可能被重建或纹理整合，但不能直接等同于“严格连通生成”。

V3b 是 connected 修复 run：manifest 显示 L-system、SC、IFS branch/radial 等高风险 case 改成 `connected occupancy projection`、`connected root/tendril/orbit projection` 或 `connected ring cache`，目标是在远端生成前就把支撑结构转为单一 connected occupancy/implicit scaffold，而不是事后从本地结果里挑一个看起来连着的版本。

因此，V3b 比 V3 更接近用户要求的“远端重新生成严格一对一匹配 case”。但 V3b 仍需补齐视觉 QA、family metric、root/provenance log；只凭 occ64 单连通不能写成“传统方法全部被解决”。

## Family 级指标摘要

| 版本 | family | case 数 | 平均 occupied | r0 最大组件数 | r0 最低 LCR | 平均 box-count dim | 指标解读 |
|---|---:|---:|---:|---:|---:|---:|---|
| V3 | DLA/frontier | 3 | 10,949 | 1 | 1.0000 | 1.912 | 远端 GLB 的 occ64 r0 已单连通，主要风险转为视觉/family 是否真像 coral/frontier/aniso DLA。 |
| V3 | IFS/transform | 4 | 15,134 | 9 | 0.9453 | 2.108 | lattice/bismuth 稳，branch/radial 有轻到中等 r0 fragmentation；radial r0 LCR 最弱。 |
| V3 | L-system | 3 | 2,991 | 130 | 0.8879 | 1.804 | pine/root fan 仍有严格 r0 碎裂；vine 占用量很低，需警惕结构过瘦或弱证据。 |
| V3 | Space colonization | 3 | 38,061 | 602 | 0.9644 | 2.041 | SC 远端体量大、复杂度高，但 root network r0 碎裂最多。 |
| V3b | DLA/frontier | 2 | 11,079 | 1 | 1.0000 | 1.926 | coral/frontier 保持单连通，未包含 aniso crystal。 |
| V3b | IFS/transform | 3 | 16,893 | 1 | 1.0000 | 2.117 | branch、radial、lattice 全部 r0 单连通；radial occupied 明显提升。 |
| V3b | L-system | 3 | 9,020 | 1 | 1.0000 | 2.088 | pine/root/vine 均从 V3 的碎裂或低占用转为 r0 单连通。 |
| V3b | Space colonization | 3 | 40,478 | 1 | 1.0000 | 2.281 | SC 三例全部 r0 单连通，复杂度最高；需视觉确认是否变成厚 blob。 |

## V3 case 审计

| case | traditional target | occupied | r0 components / LCR | r1/r2 | box dim | 指标判定 |
|---|---|---:|---:|---|---:|---|
| `v3_dla_coral_cluster_900_implicit_organic` | `dla_coral_cluster_900` | 13,255 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 1.912 | 可作为 V3 DLA coral 候选，但只基于指标；还需看是否 porous coral 而非 smooth blob/tube skeleton。 |
| `v3_dla_frontier_sheet_700_implicit_reef` | `dla_frontier_sheet_700` | 8,969 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 1.920 | 连通指标好；主风险是 frontier sheet silhouette 和薄片/前沿语义是否成立。 |
| `v3_dla_aniso_crystal_800_faceted_frontier` | `dla_aniso_crystal_800` | 10,624 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 1.905 | 远端 GLB occ64 已单连通，优于本地 dryrun 风险；但 ordered crystal 与 stochastic DLA 的概念边界仍需谨慎。 |
| `v3_ifs_bismuth_hopper_d4_terraced_lattice` | `ifs_bismuth_hopper_d4` | 18,354 | 2 / 0.9996 | 1 / 1.0000；1 / 1.0000 | 2.009 | 近单连通，碎片质量极小；可进补充或 ordered lattice/bismuth boundary，主文需视觉和 transform 指标。 |
| `v3_ifs_branch_tree_d6_clean_orbit` | `ifs_branch_tree_d6` | 9,871 | 9 / 0.9989 | 1 / 1.0000；1 / 1.0000 | 2.362 | box dim 最高，说明多尺度占用强；r0 仍非单连通，适合对比 V3b 修复，不宜直接主张 connected branch tree。 |
| `v3_ifs_fractal_lattice_d4_pyrite_scaffold` | `ifs_fractal_lattice_d4` | 29,147 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 2.153 | V3 最强结构候选之一；occupied、复杂度、连通性都强，需确认 lattice/copy/facet 视觉。 |
| `v3_ifs_radial_ornament_o8_d4_solid_gear` | `ifs_radial_ornament_o8_d4` | 3,164 | 2 / 0.9453 | 1 / 1.0000；1 / 1.0000 | 1.908 | r0 LCR 最低；只能作为 V3 radial repair target，不宜进主文。 |
| `v3_lsys_climbing_vine_d6_leaf_cards` | `lsys_climbing_vine_d6` | 938 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 1.917 | 单连通但 occupied 很低，可能是瘦结构；需视觉确认 vine/tendril/leaf 是否清楚。指标上可进候选池，不足以主文定稿。 |
| `v3_lsys_pine_canopy_d5_layered_conifer` | `lsys_pine_canopy_d5` | 4,631 | 130 / 0.8879 | 1 / 1.0000；1 / 1.0000 | 1.453 | V3 最弱之一：r0 碎裂严重且 box dim 低。应淘汰主文，作为 V3b 的关键修复对照。 |
| `v3_lsys_root_fan_d5_hierarchy` | `lsys_root_fan_d5` | 3,404 | 29 / 0.9897 | 1 / 1.0000；1 / 1.0000 | 2.042 | 有多尺度 root 信号，但 r0 多组件；只适合补充/修复池。 |
| `v3_sc_bush_shell_220_leaf_shell` | `sc_bush_shell_220` | 46,944 | 122 / 0.9973 | 1 / 1.0000；1 / 1.0000 | 1.997 | 体量大、LCR 高但碎片多；不能主张严格 connected bush。 |
| `v3_sc_root_network_260_root_hierarchy` | `sc_root_network_260` | 22,928 | 602 / 0.9644 | 1 / 1.0000；1 / 1.0000 | 1.892 | V3 SC 中 r0 风险最大；应淘汰主文，优先看 V3b。 |
| `v3_sc_tree_crown_260_leaf_clusters` | `sc_tree_crown_260` | 44,312 | 59 / 0.9971 | 1 / 1.0000；1 / 1.0000 | 2.234 | 复杂度高且 LCR 高，但严格 r0 非单连通；可作补充/修复对照，不直接进主文。 |

## V3b case 审计

| case | traditional target | occupied | r0 components / LCR | r1/r2 | box dim | 指标判定 |
|---|---|---:|---:|---|---:|---|
| `v3b_dla_coral_cluster_900_implicit_single` | `dla_coral_cluster_900` | 13,405 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 1.918 | 结构上可作为 coral 主文候选；需视觉确认 porous/frontier attachment，而非只靠 smooth implicit surface。 |
| `v3b_dla_frontier_sheet_700_implicit_single` | `dla_frontier_sheet_700` | 8,753 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 1.934 | 结构稳定；是否进主文取决于 sheet/frontier silhouette 和 thin sheet zoom。 |
| `v3b_ifs_branch_tree_d6_connected_orbit` | `ifs_branch_tree_d6` | 12,758 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 2.125 | 相比 V3 branch 的 9 个 r0 component 已解决连通性；主文仍需 transform-copy hierarchy 可视化。 |
| `v3b_ifs_fractal_lattice_d4_pyrite_connected` | `ifs_fractal_lattice_d4` | 29,147 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 2.153 | 继续是最稳的非植物候选；可优先进入主文或强补充。 |
| `v3b_ifs_radial_ornament_o8_d4_connected_gear` | `ifs_radial_ornament_o8_d4` | 8,774 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 2.071 | 相比 V3 radial 的低 LCR 有实质修复；若 8-fold/ring 视觉成立，可作为 V3b 证明点。 |
| `v3b_lsys_climbing_vine_d6_connected_leafy` | `lsys_climbing_vine_d6` | 4,374 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 1.998 | 比 V3 vine occupied 提升约 4.7x 且保持单连通；可作为候选，但要看是否仍像 climbing vine。 |
| `v3b_lsys_pine_canopy_d5_connected_conifer` | `lsys_pine_canopy_d5` | 16,654 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 1.996 | 从 V3 pine 的 130 个 r0 component 修复为单连通，且复杂度提升；是 V3b 最需要视觉 QA 的主文候选。 |
| `v3b_lsys_root_fan_d5_connected_hierarchy` | `lsys_root_fan_d5` | 6,031 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 2.270 | root fan 指标显著改善；若 flat/root-fan silhouette 成立，可进主文或强补充。 |
| `v3b_sc_bush_shell_connected_leaf` | `sc_bush_shell_220` | 54,986 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 2.262 | 体量和复杂度最高之一；需要排查是否 thick blob/leaf shell，而不是真正 bush/shell branch support。 |
| `v3b_sc_root_network_connected_root` | `sc_root_network_260` | 32,926 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 2.361 | V3b 中复杂度最高，且解决 V3 root network 602 组件问题；主文潜力高，但需 path-to-root 和 root zoom。 |
| `v3b_sc_tree_crown_connected_leaf` | `sc_tree_crown_260` | 33,521 | 1 / 1.0000 | 1 / 1.0000；1 / 1.0000 | 2.218 | 从 V3 的 r0 59 组件变成单连通；可作为 SC crown 候选，需 crown silhouette 和 branch/leaf anchor QA。 |

## V3 与 V3b 对应改进

| target | V3 指标问题 | V3b 改进 | 当前建议 |
|---|---|---|---|
| `lsys_pine_canopy_d5` | r0 130 comps，LCR 0.8879，box 1.453 | r0 1 comp，LCR 1.0000，occupied 16,654，box 1.996 | 优先看图；若有 trunk/whorl/conifer silhouette，可进主文候选。 |
| `lsys_root_fan_d5` | r0 29 comps | r0 1 comp，box 2.270 | 强补充/主文候选，取决于 flat root fan 和 root-to-tip zoom。 |
| `lsys_climbing_vine_d6` | 已单连通但 occupied 938 太低 | occupied 4,374，box 1.998，仍单连通 | 可替代 V3 vine 候选。 |
| `sc_tree_crown_260` | r0 59 comps | r0 1 comp，box 2.218 | V3b 明显更符合严格远端生成要求。 |
| `sc_root_network_260` | r0 602 comps，LCR 0.9644 | r0 1 comp，box 2.361 | V3b 重点候选；必须补 path-to-root/zoom。 |
| `sc_bush_shell_220` | r0 122 comps | r0 1 comp，box 2.262 | 指标可用；视觉若像 shell/bush 才能进入论文。 |
| `dla_coral_cluster_900` | V3 已单连通 | V3b 仍单连通，occupied 接近 | 二者都可候选；选图必须由 coral/frontier 视觉和 family metric 决定。 |
| `dla_frontier_sheet_700` | V3 已单连通 | V3b 仍单连通，box 略升 | 不是连通问题，关键是 sheet silhouette。 |
| `dla_aniso_crystal_800` | V3 单连通，但 family 边界风险 | V3b 未包含 | 暂不进主文严格一对一；若保留，应 V4 重新生成。 |
| `ifs_branch_tree_d6` | r0 9 comps | r0 1 comp，occupied 提升 | V3b 可作为 connected transform branch 候选。 |
| `ifs_radial_ornament_o8_d4` | r0 LCR 0.9453 | r0 1 comp，occupied 8,774，box 2.071 | V3b 是实质修复；优先检查 8-fold/ring closure。 |
| `ifs_fractal_lattice_d4` | V3 已强 | V3b 保持强 | 主文最稳非植物候选。 |
| `ifs_bismuth_hopper_d4` | V3 近单连通 | V3b 未包含 | 可作补充 ordered-transform boundary；V4 可补远端 connected 版本。 |

## 主文、补充、淘汰建议

### 可优先进入主文候选池

这些 case 的远端 GLB 指标满足 r0 单连通，且与传统 target 的一对一关系在 manifest 中较清楚；进入主文前仍需 neutral render、同 mesh camera zoom、family metric 与 root/provenance log。

- `v3b_lsys_pine_canopy_d5_connected_conifer`
- `v3b_lsys_root_fan_d5_connected_hierarchy`
- `v3b_sc_root_network_connected_root`
- `v3b_sc_tree_crown_connected_leaf`
- `v3b_ifs_fractal_lattice_d4_pyrite_connected`
- `v3b_ifs_radial_ornament_o8_d4_connected_gear`

### 强补充或边界讨论

这些 case 指标可用，但容易被质疑视觉/family 语义，适合补充图、失败边界或 ablation 对照。

- `v3b_lsys_climbing_vine_d6_connected_leafy`：连通和占用改善明显，但需要确认 climbing vine/tendril 是否可读。
- `v3b_sc_bush_shell_connected_leaf`：指标很强，但必须防止“复杂厚壳”替代 bush/shell。
- `v3b_dla_coral_cluster_900_implicit_single`：结构可用，需证明 DLA/frontier coral 语义。
- `v3b_dla_frontier_sheet_700_implicit_single`：结构可用，需证明 sheet/frontier，而不是 generic reef。
- `v3b_ifs_branch_tree_d6_connected_orbit`：结构可用，需证明 transform-copy branch hierarchy。
- `v3_ifs_bismuth_hopper_d4_terraced_lattice`：V3 近单连通，但 V3b 未远端 connected 重跑，建议只作 ordered-transform 补充。

### 不建议进主文，除非 V4 重跑

- `v3_lsys_pine_canopy_d5_layered_conifer`
- `v3_lsys_root_fan_d5_hierarchy`
- `v3_sc_root_network_260_root_hierarchy`
- `v3_sc_tree_crown_260_leaf_clusters`
- `v3_sc_bush_shell_220_leaf_shell`
- `v3_ifs_radial_ornament_o8_d4_solid_gear`

原因不是它们没有视觉价值，而是严格 r0 组件数或 LCR 仍不足，不能支撑“远端重新生成、严格一对一、connected asset”的主张。

## 下一步 V4 优先解决的问题

1. **先补视觉 QA，不要只看 PBR 美图**
   - 对每个 V3b 主文候选生成/整理 pure-white neutral overview、root/seed、junction/contact、terminal/facet/cavity 的真实 camera zoom。
   - QA 标签必须包括 `wrong_category`、`wrong_mode`、`silhouette_mismatch`、`texture_masks_geometry_failure`、`blob`、`fragmented`、`tube_skeleton`。

2. **补 family metric 和 root/path metric**
   - L-system：depth token survival、branch order consistency、branch length decay、tip/needle/root attachment。
   - SC：attractor coverage、path-to-root、leaf/root anchor rate、orphan mass。
   - DLA/frontier：frontier attachment survival、porosity/cavity、surface-to-volume、fake bridge/deleted mass。
   - IFS/transform：orbit error、copy survival、symmetry IoU、contact graph consistency。

3. **V4 必须继续远端重生成缺口 case**
   - `dla_aniso_crystal_800`：V3b 没有 connected 版本；若要保留 DLA 名义，必须重跑并区分 stochastic anisotropic DLA 与 ordered crystal。
   - `ifs_bismuth_hopper_d4`：V3 近单连通但 V3b 缺失；若要进主文，应补 V4 connected 远端生成。
   - 对 V3b 视觉失败的 pine/root/SC/radial，不应本地挑图修 caption，而应按同一 target 远端重跑多 seed/controls，并记录 selection budget。

4. **建立“远端重生成”证据链**
   - 每个最终 case 写入：traditional target、operator composition、seed、guide、mesh input、remote textured GLB path、metrics path、render path、rejected candidate count。
   - caption 中区分：occupancy connected、mesh export connected、visual category matched、PBR asset-ready；不要把一个证据写成另一个证据。

5. **主文策略收窄**
   - 主文只放 4-6 个最稳 case，宁可少放，也不要把 V3 的碎裂候选或未看图候选写成 solved。
   - 当前最值得先投入主文 QA 的组合是：V3b pine、V3b root fan、V3b SC root、V3b SC crown、V3b pyrite lattice、V3b radial gear。

## 当前结论

V3 的远端 GLB 指标说明：DLA/frontier 和 pyrite lattice 等 case 已有可用结构信号，但 L-system pine/root、SC root/crown/bush、radial ornament 仍不能作为严格 connected 主文证据。

V3b 的远端 GLB 指标说明：connected occupancy/implicit scaffold 的方向有效，11 个 case 全部达到 occ64 r0 单连通、LCR 1.0000；这比“本地挑选/后处理”更符合用户要求。下一步不是继续包装 V3，而是用 V3b/V4 的远端重生成结果补齐视觉 QA、family metrics 和 provenance，再决定主文/补充。
