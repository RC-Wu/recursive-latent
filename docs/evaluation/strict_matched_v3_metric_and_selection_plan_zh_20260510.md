# strict matched V3 指标与筛选方案（2026-05-10）

本文只准备 V3 评估/指标与选图方案，不修改生成脚本。目标是把 V3 从“结果能否生成”收窄到“每个严格 matched case 是否有足够的硬指标、视觉证据和 root provenance 支撑进入主文”。

## 1. 输入依据

- V1/V2 visual audit：`docs/evaluation/strict_visual_matched_v1_v2_visual_audit_zh_20260510.md`
- 严格一对一论文评估更新：`docs/evaluation/strict_one_to_one_paper_eval_update_zh_20260510.md`
- root quality strict matching strategy：`docs/evaluation/root_quality_strict_matching_strategy_zh_20260510.md`
- V2 visual matched contact sheet：`visuals/strict_visual_matched_texture_v2_zoom_20260510/strict_visual_matched_texture_v2_contact_sheet_20260510.png`
- V2 strict pair contact sheet：`visuals/strict_matched_pair_candidates_v2_20260510/strict_matched_pair_candidates_v2_contact_20260510.png`
- V2 strict pair manifest：`visuals/strict_matched_pair_candidates_v2_20260510/matched_pair_v2_manifest.csv`
- 当前 surface metric 表：`results/matched_high_quality_root_metrics_20260510/surface_metrics_occ64.csv` 与 `results/weak_search_candidate_metrics_20260510/surface_metrics_occ64.csv`

## 2. V3 总准入规则

V3 每个 case 先按 hard gate 筛，再按视觉证据分层，最后决定是否进主文。

### 2.1 hard gate

1. **任务匹配**：traditional task 与 PS-RSLG candidate 必须满足 same-category、same-recursive-mode、same-depth/complexity budget。类别近似但轮廓或模式不一致时，只能进 supplement 或 failure。
2. **mesh/render 可用**：GLB load success、mesh render success、纯白背景 overview、同一 mesh 的 camera zoom 必须齐全。Matplotlib、点云或 2D crop 只能做诊断。
3. **连通与根路径**：至少报告 `components_r0/r1/r2`、`lcr_r0/r1/r2`、`root_component_ratio`、`path_to_root_rate`、`orphan_mass_ratio`。主文正例原则上要求 r0 或 r1 已接近单主成分，并说明 voxel proxy 不能等同真实拓扑证明。
4. **family metric 必须过线**：每类必须有递归族指标。若 shape/mode 指标失败，即使 PBR 很好也不能作为主表胜负行。
5. **root provenance**：主文 row 必须有 `root_selection_log`：root source、candidate pool、selection budget、rejected reasons、metric paths、render paths。高质量 root 可以用，但不能先看最终美图再倒写匹配。
6. **PBR 只证明 asset-readiness**：主文中 neutral render 支撑结构比较，PBR/textured render 只能支撑资产可用性，不能当 topology 或 recursive-mode 证据。

### 2.2 选图分级

| 分级 | 含义 | 放置位置 |
|---|---|---|
| Main-A | 当前可以作为主文正例，但 caption 必须写清楚 caveat 和 provenance | 主文 strict matched figure / main table |
| Main-B | 可进主文边界讨论或小图，不进胜负主表，除非 V3 补齐指标 | 主文 limitation 或 supplement |
| Supp | 任务有诊断价值，但类别、轮廓、模式或视觉语义不足 | supplement contact sheet / failure table |
| Reject-for-main | V3 继续作为生成目标或失败例，不应进入主文正图 | appendix failure / internal screening |

## 3. 通用指标包

### 3.1 结构/拓扑硬指标

- `loader_status`、`vertices`、`faces`、`occupied_voxels`、`bbox/scale`、mesh/GLB export success。
- `occupancy_component_count_6n` at r0/r1/r2。
- `largest_occupancy_component_ratio_6n` at r0/r1/r2。
- `root_component_ratio`、`path_to_root_rate`、`orphan_mass_ratio`、`orphan_handle_rate`。
- `projection_survival_ratio`、`deleted_mass_ratio`、`fake_bridge_count`。
- `face_component_count`、`largest_face_component_ratio`、`nonmanifold_edges`、`boundary_edges`。

### 3.2 视觉/资产指标

- overview、root/seed、primary junction/frontier/lattice contact、terminal tip/facet/cavity 的真实 3D camera zoom。
- neutral render 与 PBR render 分开评分，PBR 只做 asset-readiness。
- 多视角 category prompt margin，例如 `vine - root/coral/tree`、`tree crown - vine/root/coral`、`radial ornament - terrain/crystal`。
- DINO multi-view consistency。
- human QA labels：`wrong_category`、`wrong_mode`、`silhouette_mismatch`、`texture_masks_geometry_failure`、`bead_chunk`、`blocky_terrain`、`thin_sheet_missing`、`fragmented`、`blob`、`dirty_material`。

### 3.3 root/provenance 指标

- `root_policy`：R0 same-root、R1 same-category matched-root、R2 generated matched-root、R3 procedural proxy、R4 non-matched root。
- `root_source_path`、`source_type`、prompt/guide/seed/steps/texture schedule。
- `candidate_pool_size`、`accepted_count`、`rejected_count`、`selection_rank`、`selection_budget_cap`。
- `pre_texture_selection_metrics`：category、shape、anchor、complexity、recursive mode 先过线，之后才允许 texture/PBR 评分。
- `failure_labels_for_rejected_roots` 与 `rejected_candidate_ids`。

## 4. 每类 case 的 V3 指标与筛选结论

| traditional task | 当前 V2 candidate | V3 必看硬指标 | V3 必看视觉指标 | 主文/补充结论 |
|---|---|---|---|---|
| `lsys_climbing_vine_d6` | `vine_stage5` | L-system branching/tendril 指标：tip count、junction count、branch length/angle distribution、root-to-tip path length；occupancy r0/r1/r2；root path rate；shared root log。当前 `vine_stage5` r0/r1/r2 均单连通。 | overview 应读成 climbing vine；zoom 必须显示卷曲 tendril、主干到侧枝连接、terminal tips；PBR 不得掩盖结构。 | **Main-A**。可进主文正例，但要标注与 `sc_root_network_260` 共享 `vine_stage5`，统计上不能算两个独立 root discovery。 |
| `sc_tree_crown_260` | `tree_compete_s3` | SC attractor coverage、branch density、tip count、nearest-attractor distance、collision/rejection count；occupancy r0=2 comps、LCR=0.993，r2 单连通；root provenance。 | overview 应读成 tree/crown 而不是 generic plant；zoom 看 crown branch junction、leaf/branch cluster、root/attachment。 | **Main-A with caveat**。可进主文，但 caption 必须说明 traditional 是 tube/crown skeleton，ours 是高质量 crown/root 资产；PBR 优势不能写成结构优势。 |
| `sc_root_network_260` | `vine_stage5` | SC root/competition 指标：attractor/root coverage、branch density、path_to_root_rate、terminal root/tip count；occupancy r0/r1/r2；shared root log。 | overview 要读成 root/vine network；zoom 看根基、分叉、末端细根/卷须；不能只像装饰性下垂藤蔓。 | **Main-A with caveat**。可进主文，但必须与 `lsys_climbing_vine_d6` 标注 shared root candidate，避免重复计数。 |
| `ifs_fractal_lattice_d4` | `pyrite_stage4` | IFS/lattice 指标：transform orbit error、copy survival ratio、scale drift、lattice contact graph consistency、facet normal consistency、symmetry IoU；occupancy r0/r1/r2 均单连通。 | overview 与 zoom 应读成 ordered lattice / faceted crystal；zoom 看层级 copy、晶面/接触、局部阶梯，而不是随机 DLA。 | **Main-A**。当前最强非植物正例。论文中只能写 ordered lattice / transform-copy-inspired asset，不能替代 stochastic DLA。 |
| `lsys_pine_canopy_d5` | `tree_compete_s3`；visual V2 needles | L-system pine 指标：主轴可见性、轮生/层级 branch angle、branch length decay、tip/needle bundle count、canopy silhouette coverage；occupancy 与 root path。 | 必须像 conifer/pine：中心主干、分层枝、稀疏针叶束。V2 visual needles 仍偏刺球，pair V2 的 `tree_compete_s3` 更像 broadleaf/palm root，不是 pine。 | **Supp / Reject-for-main**。除非 V3 生成 pine/conifer root 并通过 pine 指标，否则不能进主文正例。 |
| `lsys_root_fan_d5` | `vine_stage5`；visual V2 fibers | L-system root fan 指标：fan silhouette IoU、planarity/flatness、root-to-tip path length、branch angle spread、tip density、single root attachment；occupancy 与 root path。 | overview 必须是 flat root fan 或 downward tropism root，而不是 hanging/climbing vine；zoom 看主根、侧根、末端须根。 | **Supp / needs new root**。`vine_stage5` 资产强但轮廓不匹配，只能补充或用于 root pool 说明。 |
| `sc_bush_shell_220` | `tree_compete_s3` | SC bush 指标：shell coverage、spherical/bushy silhouette coverage、attractor coverage、branch density、uncovered attractor ratio、tip distribution；occupancy。 | overview 要像 bush/shell canopy，而不是 tree trunk with leaves；zoom 看 shell 内外层枝条密度。 | **Supp / needs new root**。当前类别近似但 silhouette 不足，需要 spherical/bushy shell root 后再评估。 |
| `dla_coral_cluster_900` | `coral_density_0p25_octopus`；visual V2 smooth capsules | DLA 指标：frontier attachment survival、effective stickiness、orphan frontier rate、porosity/cavity proxy、surface-to-volume ratio、blockiness、fake_bridge_count、deleted_mass_ratio；当前 candidate r0/r1/r2 单连通。 | overview 要像 coral/frontier cluster，而不是管线骨架或体素珠串；zoom 看分枝端头、孔洞、粗糙表面和 attachment neck。V2 smooth capsules 仍偏管道。 | **Main-B / Supp boundary**。现阶段不进主表正例；可做 naturalization before/after 或 DLA boundary case。 |
| `dla_frontier_sheet_700` | `dla_side_octopus`；visual V2 smooth frontier | DLA frontier sheet 指标：sheet silhouette IoU、frontier attachment survival、thin sheet thickness distribution、fragment count、porosity、blockiness、orphan frontier；当前 `dla_side_octopus` r0 26 comps、LCR=0.966，r2 单连通。 | overview 和 zoom 都要显示 frontier sheet，而不是 generic coral cluster 或碎片云；zoom 看薄片边界、前沿附着、孔洞。 | **Supp / needs new root**。side/frontier mode 更接近，但没有 sheet silhouette，不能进主文。 |
| `dla_aniso_crystal_800` | `bismuth_hopper_pyrite_hq` | 如果保留 DLA 名称：需 stochastic anisotropic DLA 指标，frontier/attachment/anisotropy 同时过线。如果改为 ordered crystal：看 facet normal consistency、anisotropy score、contact graph、step/facet zoom；当前 r0 2 comps、LCR=0.9996，r1 单连通。 | `bismuth_hopper_pyrite_hq` 视觉强，但像 ordered crystal；zoom 看阶梯晶面和接触，不应声称 stochastic DLA。 | **Supp ordered-crystal boundary**。除非任务重定义为 ordered crystal/lattice，否则不能作为 DLA 主文胜负行。 |
| `ifs_branch_tree_d6` | `ifs_transform_copy_proxy`；visual V2 orbit-visible | IFS 指标：transform orbit error、copy survival ratio、scale/rotation hierarchy、level-to-level contact、root attachment、scale drift；occupancy 与 fragmentation。 | zoom 必须看到 copy level、branch hierarchy、tree-like silhouette。当前 proxy 模式严格但像 soft blob 或刺团，visual 不到 paper-grade。 | **Supp mode-matched failure**。适合证明 mode matched 不等于视觉成功；V3 需要真正 transform-copy tree root。 |
| `ifs_radial_ornament_o8_d4` | `cache_radial_transform_fusion`；备选 `transform_radial4_gear`；visual V2 connected gear | radial/IFS 指标：8-fold symmetry/orbit error、copy survival、ring closure、radial thickness consistency、scale decay、component count。当前 `cache_radial_transform_fusion` r0 92 comps、LCR=0.998，r1 单连通；`transform_radial4_gear` r0 845 comps、LCR=0.628，r1 近单连通。 | overview 正视图和斜视图都要读成 radial ornament/gear；zoom 看重复单元、中心/外圈层级和连接，不应像 terrain/crystal block。 | **Supp / needs repair or new root**。V2 radial ring 方向可保留，但当前不能写 radial/transform-copy solved。 |
| visual V2 root / SC root 类 | `v2_lsys_root_fan_d5_fibers`、`v2_sc_root_network_260_fibers` | 根系粗细层级、主根/侧根/末端须根比例、path_to_root_rate、component/LCR、branch angle spread、tip density。 | contact sheet 中 SC root 更像根网，但 lsys root fan 仍像一束刺状根；必须补 root/junction/tip 三类 camera zoom。 | **候选池**。用于 V3 root/root-network 搜索，不直接替代 `vine_stage5` 的主文证据，除非补齐 root fan 或 SC root 指标。 |
| visual V2 pine/crown 类 | `v2_lsys_pine_canopy_d5_needles`、`v2_sc_tree_crown_260_branch_needles` | 主干层级、branch angle/length、tip/needle distribution、canopy/shell coverage、component/LCR。 | 当前 pine/crown 仍偏刺球或灰白团块，缺少 trunk-to-branch hierarchy 和可读 canopy。 | **Reject-for-main**。只能作为 V3 失败诊断或生成方向，不进入主文正图。 |
| visual V2 DLA 类 | `v2_dla_coral_cluster_900_smooth_capsules`、`v2_dla_frontier_sheet_700_smooth` | attachment survival、porosity/cavity、blockiness、tube/capsule over-smoothing rate、fake bridges、deleted mass。 | smooth capsule 改善 voxel 感，但 zoom 像管线骨架；frontier sheet 仍缺薄片轮廓。 | **Supp failure/boundary**。适合展示 naturalization 目标，不作为 DLA solved。 |

## 5. V3 主文组合建议

### 5.1 主文正例，只保留四个

1. `lsys_climbing_vine_d6 -> vine_stage5`
2. `sc_tree_crown_260 -> tree_compete_s3`
3. `sc_root_network_260 -> vine_stage5`
4. `ifs_fractal_lattice_d4 -> pyrite_stage4`

主文中四项必须配同一结构：

- traditional neutral overview。
- ours neutral overview。
- ours PBR/asset render，明确标作 asset-readiness。
- 同一 3D mesh 的 root/seed、junction/contact、terminal/facet/cavity camera zoom。
- metric strip：`components/LCR`、family metric、visual QA label 或 category margin、root selection budget。

### 5.2 只能补充或边界讨论

- `dla_coral_cluster_900 -> coral_density_0p25_octopus`：连通性强，但 bead/chunk 与管线感仍明显。放 naturalization boundary。
- `dla_aniso_crystal_800 -> bismuth_hopper_pyrite_hq`：强 ordered crystal 资产，但不是 stochastic DLA。放 ordered-crystal boundary 或改任务后再评估。
- `dla_frontier_sheet_700 -> dla_side_octopus`：frontier 方向相关，但无 sheet silhouette 且碎片多。
- `ifs_branch_tree_d6 -> ifs_transform_copy_proxy`：mode matched 但 visual 低，适合 failure。
- `ifs_radial_ornament_o8_d4 -> cache_radial_transform_fusion / transform_radial4_gear`：一个连通但不像 ornament，一个像 gear 但碎，均不进主表。
- `lsys_pine_canopy_d5 -> tree_compete_s3`：类植物但不等于 pine/conifer。
- `lsys_root_fan_d5 -> vine_stage5`：root/vine 资产强，但不是 flat root fan。
- `sc_bush_shell_220 -> tree_compete_s3`：不是 bush/shell silhouette。

## 6. V3 具体筛选流程

1. **先锁任务定义**：每个 row 固定 traditional task、family、depth/complexity budget、target silhouette 和 expected zoom 类型。不能在选图后改任务名。
2. **先跑硬指标表**：mesh load、component/LCR、root path、family metric、projection/fake bridge、mesh quality。硬指标不达标的结果只能进入 failure 或 repair pool。
3. **再做 neutral render QA**：在白底同相机下检查 category、silhouette、recursive mode、root/junction/tip。neutral render 失败时，PBR 再好也不能晋级。
4. **最后看 PBR/asset-readiness**：texture 只决定是否适合 paper-facing render，不决定结构胜负。
5. **记录 root_selection_log**：每个主文 row 写清 root pool、筛选顺序、失败候选、metric paths、render paths 和 budget cap。
6. **生成 final figure 前复核 overclaim**：DLA、radial、pine/root-fan/bush 这些当前弱项不得因为有好看的 asset 被写成 solved。

## 7. V3 文案边界

可以写：

> Selected strict matched rows show that finite-depth recursive assets can preserve task-level structure while using logged high-quality roots and a frozen PBR export path.

> The neutral renders and family metrics support the structural comparison; textured renders report asset-readiness for the same selected meshes.

> DLA/frontier, radial ornament, pine canopy, root fan, and bush shell remain boundary or generation targets unless their family metrics and zoom evidence pass the V3 gates.

不要写：

- “PS-RSLG beats L-systems / DLA / IFS”。
- “PBR 证明 topology 更好”。
- “connected occupancy 证明 DLA physics 或 branching 正确”。
- “bismuth/pyrite 解决 DLA”。
- “vine_stage5 可以同时替代 vine、root fan、SC root 而不标 shared root 和 silhouette caveat”。
- “radial/transform-copy 已解决”。

## 8. 当前结论

V3 的主文策略应保守：只把 `vine_stage5` 对 climbing vine、`tree_compete_s3` 对 SC crown、`vine_stage5` 对 SC root network、`pyrite_stage4` 对 IFS/lattice 放进主文正例，并在表中明确 shared root、root provenance 和 PBR caveat。DLA/coral、frontier sheet、anisotropic crystal、IFS branch tree、radial ornament、pine canopy、root fan、bush shell 都应先进入 supplement、boundary 或 failure pool，除非 V3 用对应的 family metric、真实 camera zoom 和 root log 证明它们完成了 strict matching。
