# Strict one-to-one matching gap table

日期：2026-05-10

范围：按用户最新纠偏，只审阅当前协议、gallery、V8-V12 结论和已有 manifest/summary，不启动远端任务，不修改 `paper_siga/main.tex`。本文回答：四类传统方法的 strict matched exemplar 当前还缺什么，以及哪些证据不能直接写成论文 claim。

## 0. 总体判断

当前材料已经从“宽泛相似图”推进到 task-level strict matching，但还没有形成四类传统方法都可直接进主文的最终证据包。

- L-system / space-colonization / IFS 的当前主候选主要来自 V6 connectivity 和 V4/V5/V3b gallery。它们已有 case 名、目标任务、控制参数和 zoom comparison，但缺少下一批统一 selection budget、post-GLB 结构指标、family metric 和人工 QA 结论。
- DLA/frontier 是 V8-V12 投入最多的一类。V8 提供了更像 frontier accretion 的候选；V9-V12 已有远端 textured GLB 和 zoom 图，且 summary 多数 `status=ok`。但 DLA 仍缺最终 paper-grade 选择、blockiness/frontier survival/bridge 证书指标，以及明确排除 physical-DLA/crystal claim 的表述。
- `case_gallery_for_user_20260509/06_baselines_metrics_ablation` 当前没有实际文件；2026-05-10 gallery README 已说明本次改从现有 baseline overview、one-to-one baseline、Gen3D baseline clean figures 和相关 manifest 补齐。因此不能把该空目录当成已完成的 baseline/ablation 证据。

## 1. Family gap table

| 传统方法 | strict exemplar | 当前可用候选 | 当前缺口 | 下一步证据门槛 | 论文中可写 / 不可写 |
|---|---|---|---|---|---|
| L-system | `lsys_pine_canopy_d5` | V6 `v6_lsys_pine_canopy_d5_same_rule_welded_needles`; gallery 中还有 V5/V4/V3b 对照图。 | 还缺统一下一批 a100-2 多 seed 选择；缺 post-GLB `LCR/RAR/PTR`、branch angle/length distribution；缺明确证明 trunk-whorl-needle 层级不是纹理噪声的 camera zoom QA。 | 至少 3 个 seed/root/operator setting；保留 depth=5、branch nodes、attached needles、junction zoom；通过 `LCR>=0.98`、`RAR>=0.95`、needle/tip attachment QA。 | 可写 selected finite-depth L-system pine task；不可写 PS-RSLG 普遍优于 L-system，或仅凭针叶纹理证明重写层级。 |
| L-system | `lsys_root_fan_d5` | V6 `v6_lsys_root_fan_d5_same_rule_welded_hairs`; V5 root fan 可作备选。 | 缺 rootlet 全部 attached 的 post-decode 指标；缺 root fan 方向性、主根到细根层级的 family metric；旧 `ours_vine` 弱行不能替代 root fan 正例。 | 统计 root depth、terminal density、PTR、root-attached ratio；zoom 覆盖 root base、junction、terminal hair。 | 可写 selected root-fan rewriting with attached rootlets；不可把 loose vine/root 或 stage5 reference 未经 strict mapping 直接写成 L-system root 证据。 |
| L-system | `lsys_climbing_vine_d6` | V6 `v6_lsys_climbing_vine_d6_same_curl_attached_leaves`; existing `ours_vine_stage5` 更强但不是完整 strict mapping。 | 当前 strict vine 仍有弱行风险；缺 helical main chain、tendril/leaf token、attachment 的 post-GLB QA；缺与 stronger stage5 reference 的替换理由表。 | 三 seed 重跑或至少明确 candidate swap；指标包含 curl step、leaf/tendril attachment、PTR、visible depth=6。 | 只能写 selected climbing-vine task if QA passes；不能用 weak strict vine row 支撑正向 claim。 |
| Space colonization | `sc_tree_crown_260` | V6 `v6_sc_tree_crown_260_same_attractor_welded_leaf_shell`; V5/V4/V3b 有中间图。 | 缺 attractor coverage / nearest-attractor distance 的最终表；缺 post-GLB leaf shell 是否仍 attached；缺证明不是普通 branch grammar 冒充 SC 的 operator log。 | 保留 attractor count、iterations=260、influence radius、kill radius、step size；报告 coverage、alive attractors、terminal path-to-root、crown envelope zoom。 | 可写 matched attractor-competition tree crown；不可否定传统 SC 的结构能力。 |
| Space colonization | `sc_root_network_260` | V6 `v6_sc_root_network_260_same_attractor_welded_rootlets`; V5 root network 备选。 | 缺 root field attractor coverage 与 path-to-root；缺 post-decode rootlet orphan mass；缺与 L-system root fan 的边界说明。 | 指标包含 coverage、RAR、PTR、rootlet density、nearest-attractor distance；zoom 覆盖主根、竞争分叉、细根。 | 可写 PS-RSLG 将 SC controls 接入 generator-native root surface；不可写“SC baseline 结构失败”。 |
| Space colonization | `sc_bush_shell_220` | V6 `v6_sc_bush_shell_220_same_attractor_welded_shell`; V4/V3b 有 shell 图。 | 缺 shell attractor coverage 和 shell-vs-blob QA；缺 leaf shell attachment、interior solidity/blockiness 指标；主文优先级低于 tree/root。 | 报告 attractor_count=1300、iterations=220、kill/influence radii、coverage、shell thickness、blob negative QA。 | 可作为 supplement 或 backup；主文应优先 SC tree/root。 |
| DLA/frontier | `dla_coral_cluster_900` | V8 `v8_dla_coral_lace_reef_branching_a`、`v8_dla_coral_antler_ridge_branching`; V10/V11/V12 staghorn/table coral; V9 organic frontier seed sweeps。 | 当前最强，但缺最终 V8-V12 横向选择表；缺 blockiness、frontier attachment survival、bridge cost、porosity/tip/neck count；V11/V12 更可读但可能牺牲 porous/ridge 细节，V9 有机但可能 root-like tangle。 | 在 V12 tapered staghorn/table 与 V8 lace/antler 中选主候选；统一 pure-white overview + 3 camera zoom；报告 LCR/RAR、frontier survival、blockiness、porosity、tip/neck。 | 可写 frontier-attachment asset generation for selected coral cases；不可写物理 DLA 或真实珊瑚生长仿真。 |
| DLA/frontier | `dla_frontier_sheet_700` | V8 `v8_dla_frontier_fan_lace_membrane_a`、`v8_dla_frontier_open_boundary_seed_b`; V10/V11/V12 frontier plate; V9 frontier fan/ripple/open boundary。 | V8 sheet 有可读 frontier 但偏平膜；V11/V12 plate 更干净但可能过度简化为 smooth plate；缺 open boundary、membrane、neck survival 指标。 | 保留 boundary sheet target=700 events；至少比较 V8 lace membrane、V12 tapered frontier plate、V9 perforated/ripple；报告 open-boundary continuity、floating sheet OMR、bridge cost。 | 可写 boundary/frontier sheet stress evidence；不宜作为唯一 DLA/coral 主正例。 |
| DLA/frontier | `dla_crystal_cluster_520` | V8 `v8_dla_crystal_accretive_blade_cluster`; V10 blue-gold crystal; V11/V12 clean/tapered crystal; V9 crystal needles/blades。 | 缺 facet direction / ridge 指标；部分 V8 material dark，V11/V12 crystal mesh较小且可能像 stylized ornament；不能 claim physical crystallization。 | 报告 facet/ridge readability、connected shard ratio、axis/blockiness、LCR/RAR；优先作为 appendix/boundary unless main paper needs crystal row。 | 可写 accretive crystal-frontier boundary case；不可写真实晶体生长。 |
| IFS/transform | `ifs_fractal_tree_d5` / current gallery `ifs_branch_tree_d6` | V3b/V4 有 `ifs_branch_tree_d6` 图；协议要求 tree IFS 不能用 pyrite 代替。 | 当前缺可主文的 transform-copy tree/branch asset；缺 depth=5/d6 的 copy hierarchy、self-similarity 和 contact metrics；pyrite/lattice 不能补这个缺口。 | 下一批必须单独生成 branch/tree IFS：contractive branch transforms、scale/rotate/copy、contact bridges；报告 orbit/copy tree hierarchy、self-similarity、PTR。 | 当前不可写 IFS tree positive claim。 |
| IFS/transform | `ifs_radial_ornament_o8_d4` | V6 `v6_ifs_radial_ornament_o8_d4_connected_facets`; V5/V4/V3b radial ornament。 | 缺 orbit error、8-fold symmetry IoU、contact bridge survival；需要确认 Trellis2/PBR 没破坏 spokes/teeth/ring order。 | 三 seed 或至少两个 root/operator variants；报告 order=8、depth=4、bridge nodes、tooth nodes、symmetry IoU、orbit error。 | 可写 empirical radial transform-copy evidence；不可写 sampler 严格 equivariant。 |
| IFS/transform | `ifs_fractal_lattice_d4` | V6 `v6_ifs_fractal_lattice_d4_connected_copy_facets`; pyrite/lattice Gen3D comparison rows。 | 这是 IFS 中最接近正例的行，但缺 orbit/contact metrics、lattice symmetry consistency、post-GLB LCR/RAR；需要把 task 名限定为 lattice/orbit。 | 报告 affine_children_per_node=4、depth=4、bridge_edges、symmetry IoU、orbit error、contact bridge survival。 | 可写 finite transform-copy lattice/orbit selected evidence；不可写 pyrite proves IFS tree matching。 |

## 2. V8-V12 DLA/frontier conclusion boundary

| 批次 | 当前定位 | 已解决 | 仍缺 |
|---|---|---|---|
| V8 / V8-thin | DLA/frontier refine 主候选池。`v8_dla_coral_lace_reef_branching_a`、`v8_dla_coral_antler_ridge_branching`、`v8_dla_crystal_accretive_blade_cluster` 当前最值得保留。 | 从 V6 的块状/杆状风险转向更像 accretive branching / porous membrane / frontier sheet。V8-thin 改善 terminal tip。 | 部分 sheet 偏平膜，部分 crystal material 偏暗；V8-thin 曾被标注 comparison panel 不完整，但当前 zoom 目录已有部分 comparison，仍需统一 paper figure QA。 |
| V9 | organic frontier DLA/coral/crystal input algorithm。两套远端 seed 目录均有 12 个 `status=ok` summary。 | 曲线边、细针 tip、ridge fin、attached perforated membrane，针对 V8 smooth tube/rod 视觉问题。 | 可能读成 root-like tangle 或过密 filigree；需要人工从 24 个远端结果筛 paper-grade，不可只按 `status=ok` 晋级。 |
| V10 | readable coral/frontier：更少、更粗、更亮 guide，8 个 case，另有 seed20266900 复跑。 | 增强 staghorn/table/frontier plate 的可读轮廓，降低 V9 过密感。 | 可能牺牲 DLA porous/frontier 细节；需要 blockiness 与 frontier survival 指标证明不是普通枝状珊瑚。 |
| V11 | clean staghorn/table support：更干净的 smooth welded branch，三个 seed 目录各 8 个 summary `ok`。 | 可读性最稳，适合作为 clean coral fallback。 | 过度 smooth，perforated/ridge 细节为 0；更像 readable asset，不是最强 frontier-attachment 证据。 |
| V12 | tapered staghorn/table：V11 的细端头修正，8 个远端 summary `ok` 且 zoom comparison 完整。 | 明确 tapered terminal continuations，适合作为下一批 DLA/coral 主候选和 V11 替代。 | 当前主要覆盖 DLA/coral/frontier/crystal，不能补 L-system/SC/IFS 缺口；仍缺最终指标表和人工 verdict。 |

## 3. 主文优先级

建议主文只提升四个最稳任务：

1. L-system：`lsys_root_fan_d5` 或 `lsys_pine_canopy_d5`，从 V6 重新按多 seed/QA 选。
2. Space colonization：`sc_root_network_260` 或 `sc_tree_crown_260`，必须带 attractor coverage。
3. DLA/frontier：`dla_coral_cluster_900`，优先 V12 tapered staghorn/table 与 V8 lace/antler 横比。
4. IFS/transform：`ifs_fractal_lattice_d4` 或 `ifs_radial_ornament_o8_d4`，不要用 pyrite 证明 IFS tree。

不建议主文现在写：`ifs_fractal_tree_d5/d6`、`dla_crystal_cluster_520`、`sc_bush_shell_220`、weak strict vine。它们可以作为 appendix、screening 或下一批补缺目标。
