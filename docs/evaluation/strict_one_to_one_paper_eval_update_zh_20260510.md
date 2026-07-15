# 严格一对一论文评估更新建议（2026-05-10）

本文只给 `paper_siga/main.tex` 后续实验、图表和措辞修订提供建议，不声明所有结果已经最终完成。核心原则是：主文比较必须是 **same-category / same-recursive-mode / same-depth-budget** 的严格任务比较；高质量 mesh 或 PBR root 可以使用，但必须记录来源、搜索池、筛选顺序和失败候选，不能事后用好看的资产替代不匹配的递归任务。

## 1. 现在建议进入主文的 exemplar tasks

优先只放 4 个主文正例，宁可少而严格，不扩展弱矩阵。

| 优先级 | traditional task | ours candidate | 进入主文建议 | 论文角色 |
|---|---|---|---|---|
| P1 | `lsys_climbing_vine_d6` | `vine_stage5` | 进主文 | L-system / climbing vine 类别和卷曲 tendril 递归模式目前最接近。`vine_stage5` 在 high-quality root 指标中 r0/r1/r2 均为单 occupancy component，视觉/PBR 也最强。 |
| P1 | `sc_tree_crown_260` | `tree_compete_s3` | 进主文，但加 caveat | Space-colonization tree/crown 的当前最佳树冠资产候选。r0 有 2 个 occupancy components、LCR 0.993，r2 后单连通。必须写清楚传统 baseline 是 tube/crown skeleton，而 ours 有叶片/材质资产差异；不能把 PBR 优势写成结构优势。 |
| P1 | `sc_root_network_260` | `vine_stage5` | 进主文，但避免重复计数 | root/vine competition 的当前最佳正例。若与 `lsys_climbing_vine_d6` 共享同一个 `vine_stage5` root，应在表中标注 shared root candidate，并在统计上不要当作两个独立 root-search 成功。 |
| P2 | `ifs_fractal_lattice_d4` | `pyrite_stage4` | 进主文的非植物正例 | transform/lattice 当前最强候选，`pyrite_stage4` r0/r1/r2 均单连通，视觉 coherent。必须限定为 ordered lattice / transform-copy-inspired asset，不能替代 stochastic DLA 或 radial ornament。 |

可放入 supplement 或 main-text 边界讨论但不放主表胜负行：

- `lsys_pine_canopy_d5 -> tree_compete_s3`：同为植物/树冠，但 pine canopy 的符号分支形态未严格对齐。可作为候选图，不建议作为主表正例。
- `lsys_root_fan_d5 -> vine_stage5`：root/vine 资产强，但 ours 是垂挂/卷曲藤蔓，不是平面 root fan。需要新 root 或新相机/控制任务。
- `dla_coral_cluster_900 -> coral_density_0p25_octopus`：连通性好，r0/r1/r2 单连通，但仍有 voxel/bead/chunk 感。现阶段适合 boundary 或 naturalization 前后对比。
- `dla_aniso_crystal_800 -> bismuth_hopper_pyrite_hq`：资产质量强，r0 LCR 0.9996、r1 单连通，但这是 ordered crystal，不是 stochastic DLA。除非把任务重定义为 ordered anisotropic crystal growth，否则不要写成 DLA 胜负。
- `ifs_branch_tree_d6 -> ifs_transform_copy_proxy`：递归模式最严格，但视觉像 soft blob，不能作为主文正例；适合作 mode-matched failure。
- `ifs_radial_ornament_o8_d4 -> cache_radial_transform_fusion`：r0 LCR 0.998、r1 单连通，但外观像 blocky terrain/crystal，不是干净 radial ornament。不要进主表。

## 2. 需要继续生成或重跑的 rows

必须继续生成，直到能满足 same-category 与 same-recursive-mode：

| task | 当前问题 | 下一步生成目标 | 进入主文门槛 |
|---|---|---|---|
| `ifs_branch_tree_d6` | `ifs_transform_copy_proxy` 模式严格但视觉弱；`tree_compete_s3` 视觉强但不是 transform-copy tree。 | 生成真正 affine transform-copy branch tree 的 ours，保留 copy survival、scale/rotation hierarchy 和 root attachment。 | 中性 render 可读、camera zoom 中能看到 level-to-level copy，r0 或 r1 近连通，失败候选有记录。 |
| `ifs_radial_ornament_o8_d4` | 当前 radial 候选碎、块、像地形；`pyrite_stage4` 不是 radial ornament。 | 生成干净的 radial ornament / hard-surface transform-copy candidate，最好有 8-fold symmetry、scale decay 和中心/外圈层级。 | symmetry/orbit metric 与 zoom consistency 通过；不能只靠 PBR 掩盖形状不匹配。 |
| `dla_coral_cluster_900` | `coral_density_0p25_octopus` 连通但 bead/chunk 感明显。 | masked/local naturalization 或更好 coral root；只处理小组件、接触缝和低置信边界，避免全局 closing 填死孔洞。 | porosity/cavity、frontier attachment、blockiness、deleted mass 同时报告；视觉上不再主要由体素珠串构成。 |
| `dla_frontier_sheet_700` | `dla_side_octopus` 更接近 side/frontier，但碎片明显且没有 sheet silhouette。 | 生成 sheet-like frontier accretion asset，保持边界生长、薄片轮廓和附着证书。 | overview 与 zoom 都显示 frontier sheet，而不是 generic coral cluster。 |
| `dla_aniso_crystal_800` | `bismuth_hopper_pyrite_hq` 是 ordered crystal，不是随机 DLA。 | 二选一：重定义为 ordered crystal task；或生成 stochastic anisotropic DLA crystal candidate。 | 任务名、baseline family、caption 三者一致；不能把 ordered lattice 当 DLA。 |
| `sc_bush_shell_220` | `tree_compete_s3` 不是 shell/bush silhouette。 | 搜索 bush/shell same-category matched-root。 | canopy shell coverage、branch density、neutral/PBR render 都与 bush task 对齐。 |
| `lsys_pine_canopy_d5` | `tree_compete_s3` 是 tree/crown，但 pine/turtle branch morphology 不够严格。 | 生成 pine/conifer canopy root 或把任务重命名为 generic tree canopy。 | 若保留 pine，需有 pine-like branch/tip/canopy 指标；否则降为 supplement。 |
| `lsys_root_fan_d5` | `vine_stage5` 形态偏 hanging vine。 | 生成 flat root fan / downward tropism root candidate。 | root fan silhouette 和 branching/tip metrics 对齐。 |

## 3. 主图布局：overview + 真相机 zoom callouts

建议主文只做一个严格 matched figure，而不是大拼盘。每个 case 占一列或一个小 block；每个 block 内固定如下结构：

| 层级 | 内容 | 规则 |
|---|---|---|
| Overview | traditional neutral render、ours neutral render、ours PBR/rendered asset | 同一 orthographic camera、纯白背景、同尺度归一化；PBR 只作为 asset-readiness panel。 |
| Callout 1 | root / seed attachment zoom | 必须是同一 3D mesh 的第二个 camera render，不使用 2D crop 当最终证据。overview 上画 callout 框和编号。 |
| Callout 2 | primary junction / attractor competition / lattice contact / frontier contact | baseline 与 ours 的 zoom 类型一致；如果 ours 缺少该结构，标 failure，不换更好看的局部。 |
| Callout 3 | terminal tip / tendril / canopy leaf cluster / facet / cavity / transform-copy level | 展示递归末端是否仍可检查。IFS/scale-down 任务必须加 level-to-level zoom。 |
| Metric strip | structural、shape、visual、root-budget 小条 | 放最少指标：occ comps/LCR、family metric、CLIP/DINO category margin 或 failure label、root search budget。 |

图件组织建议：

1. Main Figure A：4 个主文正例：`lsys_climbing_vine_d6`、`sc_tree_crown_260`、`sc_root_network_260`、`ifs_fractal_lattice_d4`。
2. Main Figure B：同 root / 同 operator / 同 depth 的 projection ablation：`direct -> final-only -> per-depth projection -> bridge-aware/full`。
3. Supplement Figure S1：全部 V2 strict matched pair candidate contact sheet。
4. Supplement Figure S2：mode-matched boundary/failure rows，包括 `ifs_transform_copy_proxy`、`transform_radial4_*`、`dla_side_octopus`、naturalization pilot before/after。

## 4. 指标分组

主文表不要混合“结构更好”和“PBR 更好”。建议 Table 2 分成四组列：

### 4.1 Structural / topology diagnostics

- `occupancy_component_count_6n` at r0/r1/r2。
- `largest_occupancy_component_ratio_6n` at r0/r1/r2。
- `root_component_ratio`、`path_to_root_rate`。
- `orphan_mass_ratio`、`orphan_handle_rate`。
- `projection_survival_ratio`、`deleted_mass_ratio`、`fake_bridge_count`。
- `face_component_count`、`largest_face_component_ratio`、`nonmanifold_edges`、`boundary_edges`。
- `vertices`、`faces`、`occupied_voxels`、`bbox/scale`、mesh/GLB load success。

写法必须带 proxy 名称，例如 “r0 occupancy proxy reports one component”，不要泛称 “topology is solved”。

### 4.2 Shape-matching / recursive-mode metrics

- L-system / branching：branch angle distribution、branch length distribution、tip count、junction count、root-to-tip path length、canopy silhouette coverage。
- Space colonization：attractor coverage、uncovered attractor ratio、nearest-attractor distance、branch density、tip count、collision/rejection count。
- DLA / frontier：frontier attachment survival、effective stickiness、orphan frontier rate、porosity/cavity proxy、surface-to-volume proxy、blockiness、fake bridge count。
- Crystal / lattice：facet normal consistency、contact graph consistency、anisotropy score、symmetry IoU、lattice orbit error。
- IFS / transform-copy：transform orbit error、copy survival ratio、scale drift、radial/lattice symmetry error、zoom consistency。

这些指标决定是否 same-recursive-mode。若这一组失败，即使 visual/PBR 很强也不能进主表胜负行。

### 4.3 Visual / PBR asset-readiness metrics

- 多视角 category prompt margin：目标类别相对邻近错误类别的 margin，例如 `tree canopy - vine/root/coral`。
- DINO multi-view consistency。
- neutral render 与 PBR render 的 human QA failure labels：`wrong_category`、`texture_masks_geometry_failure`、`dirty_material`、`holes`、`thin_sheet`、`bead_chunk`。
- GLB export success、PBR token count、render success、guide/source image provenance。
- camera zoom visual consistency：overview、root、junction/frontier、terminal tip/facet/cavity 是否仍属同一类别和结构。

PBR 只能支持 asset-readiness，不能作为结构或递归忠实度证据。

### 4.4 Root-selection budget / provenance metrics

每个 ours 主文 row 必须加 root log，最低字段：

- `root_policy`：R0 same-root、R1 same-category matched-root、R2 generated matched-root、R3 procedural proxy、R4 non-matched root。
- `root_source_path`：例如 `visuals/textured_glb_20260508/vine_d5_compete_s5_inference/textured.glb`。
- `source_type`：generated mesh、public-guide textured GLB、procedural proxy、manual selected mesh。
- `prompt/guide/seed/steps/texture_schedule`：若使用生成或 public guide。
- `candidate_pool_size`、`accepted_count`、`rejected_count`。
- `pre_texture_selection_metrics`：类别、形状、anchor、复杂度先通过后才允许 texture/PBR 评估。
- `failure_labels_for_rejected_roots`：wrong category、wrong mode、fragmented、blob、over-pruned、bad PBR 等。
- `selection_budget_cap`：每个 task 最多允许多少 seeds/roots/texture guides，避免无限 cherry-picking。

允许高质量 root 的前提是：先按 category / shape / anchor / complexity / recursive mode 筛选，再看 texture/PBR。不能先看最终美图再倒写任务匹配。

## 5. 推荐写入论文的精确措辞

### 5.1 Abstract / intro 可用句

> We evaluate selected finite-depth recursive assets under exact matched-task protocols that control object category, recursive mode, root policy, depth/complexity budget, camera, and rendering setup.

> Classical procedural systems are treated as strong structural baselines. Our comparison separates structural diagnostics, recursive-mode matching, visual/category alignment, and asset-readiness.

> Selected projected meshes can be exported through a frozen texture/PBR path, but export success is reported separately from structural correctness.

> High-quality matched roots are allowed only when their provenance, candidate pool, selection order, and failure budget are logged before texture/PBR evaluation.

### 5.2 Results / caption 可用句

> In this panel, the neutral renders support the structural comparison; the textured render reports asset-readiness for the same selected mesh and is not used as topology evidence.

> Zoom panels are rendered by moving the 3D camera to the marked root, junction/frontier, and terminal regions of the same mesh, rather than by cropping the overview image.

> The occupancy proxy reports connected support at the stated voxel tolerance; it does not by itself certify correct branching, physical DLA dynamics, watertight topology, or transform-copy fidelity.

> The lattice row is evaluated as an ordered transform/lattice task. It is not used as a substitute for stochastic DLA.

> The vine/root row and root-network row share the same current high-quality root candidate; we therefore report them as two task views over a shared root-search success rather than as independent root discoveries.

### 5.3 Discussion / limitation 可用句

> Current positive evidence is strongest for vine/root, tree/crown, root-network, and ordered lattice tasks. DLA/frontier sheet, radial ornament, and strict transform-copy branch-tree rows remain generation targets or boundary cases.

> Mode-matched failures are included because they show that using the correct recursive operator is not sufficient; the root, projection policy, and local naturalization must also preserve asset readability.

> The method should be read as a finite-depth projection-stabilized recursive asset framework, not as an infinite-growth model or a physical simulator.

## 6. 必须避免的 overclaim

不要写：

- “PS-RSLG beats L-systems / DLA / IFS.”
- “PBR texture proves better topology.”
- “Connected occupancy proves correct branching or DLA physics.”
- “Pyrite or bismuth results solve DLA.”
- “A good vine asset substitutes for a pine, root fan, or IFS branch-tree task.”
- “Radial/transform-copy is solved” while current radial candidates are still blocky or fragmented.
- “Depth progression proves controllability” unless 只改变一个控制变量并报告相应 family metric。

建议替换为：

- “On selected matched tasks, per-depth projection improves the stability of finite-depth recursive states under the reported occupancy and mesh diagnostics.”
- “The current DLA/coral row is a connected frontier-inspired asset candidate and remains a naturalization target.”
- “The pyrite/lattice row supports ordered lattice/transform-copy-inspired recursion, not stochastic DLA.”
- “Texture/PBR export demonstrates asset-path compatibility for selected projected meshes; structural fidelity is evaluated by separate neutral-render and metric panels.”
- “Traditional baselines remain strong structural controls; the paper's claim is about combining recursive control with generated-asset realization under logged root budgets.”

## 7. Main paper recommendation summary

Main paper now:

1. `lsys_climbing_vine_d6 -> vine_stage5`
2. `sc_tree_crown_260 -> tree_compete_s3`
3. `sc_root_network_260 -> vine_stage5`
4. `ifs_fractal_lattice_d4 -> pyrite_stage4`

不进主表，只作 boundary/failure 或 supplement:

1. `dla_coral_cluster_900 -> coral_density_0p25_octopus`
2. `dla_aniso_crystal_800 -> bismuth_hopper_pyrite_hq`
3. `dla_frontier_sheet_700 -> dla_side_octopus`
4. `ifs_branch_tree_d6 -> ifs_transform_copy_proxy`
5. `ifs_radial_ornament_o8_d4 -> cache_radial_transform_fusion`
6. `lsys_pine_canopy_d5 -> tree_compete_s3`
7. `lsys_root_fan_d5 -> vine_stage5`
8. `sc_bush_shell_220 -> tree_compete_s3`

最重要的修订方向是把 “好看/连通” 改成 “严格任务匹配 + 指标分组 + root provenance”。这样可以允许高质量 mesh/PBR root 进入论文，同时避免审稿人认为 baseline 是 loose similar-looking comparison 或 cherry-picking。
