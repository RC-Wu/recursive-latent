# 严格同任务 Baseline 评估计划

创建时间：2026-05-10

范围：只定义后续评估协议、矩阵、指标和视觉规范；本文档不代表已有结果已经全部完成。所有比较必须是一对一 matched-task comparison，不能用不同任务、不同递归模式或不同类别的结果互相证明胜负。

## 0. 核心原则

严格同任务的定义：

1. **同类别**：baseline 生成什么类别，我们的 PS-RSLG 就必须生成同一类别或同一语义子类。L-system 是 pine/tree canopy，就不能拿 vine/root 代替；DLA 是 crystal/coral，就必须对齐 crystal/coral frontier growth；IFS 是某个 transform/growth pattern，就必须支持同一个 transform/growth pattern。
2. **同递归模式**：branching、frontier accretion、attractor competition、affine transform-copy、radial copy、scale-down portal 等模式不得混用。跨模式只能作为补充讨论，不能进入主表胜负。
3. **同控制变量**：baseline 的角度、长度、分叉率、吸引子、stickiness、邻域、affine transform、depth 等控制量，必须映射到 PS-RSLG 的 analogous controls，并在表格中公开。
4. **同根搜索策略**：若 baseline 从 root/seed/anchor 出发，我们的结果也必须从同类型 root/seed/anchor 出发；如果需要搜索 root，必须预注册搜索池、筛选准则和失败计数。
5. **同输出协议**：所有最终比较使用 mesh/GLB/PBR 或 neutral mesh render；点云、matplotlib scatter、voxel slice 只能用于诊断，不能作为主图证据。
6. **同失败口径**：传统 baseline 的结构强项必须如实报告；我们的失败、非同类替代、过度清理、假桥、碎块和语义偏离必须进入 failure table。

## 1. 任务定义

每个 matched case 必须写成下面的任务记录：

| 字段 | 要求 |
|---|---|
| `case_id` | 唯一编号，如 `lsys_pine_canopy_d5`、`dla_coral_frontier_d4` |
| `family` | L-system、space colonization、DLA/frontier、IFS/transform、shape grammar 等 |
| `target_category` | tree canopy、pine branch、coral、crystal cluster、transform tree、radial lattice 等 |
| `recursive_mode` | branch rewriting、frontier accretion、attractor competition、affine copy、radial copy、scale-down 等 |
| `baseline_controls` | baseline 原始参数和随机种子 |
| `ps_rslg_controls` | 与 baseline 对应的 PS-RSLG handle、operator、projection、naturalization 和 texture 控制 |
| `root_policy` | same-root、matched-root search、category-root search 或 procedural-root |
| `depth_budget` | baseline depth/iterations 与 PS-RSLG depth 的对齐规则 |
| `resource_budget` | token、voxel、vertex、face、sampler steps、runtime、texture export 是否开启 |
| `outputs` | 每层 mesh、最终 GLB、neutral render、textured render、metrics JSON/CSV |
| `pass_fail_rule` | 结构、语义、连通、视觉、资产可用性的硬性通过条件 |

禁止写法：

- `L-system tree vs PS-RSLG vine` 作为主胜负比较。
- `DLA coral vs PS-RSLG generic coral-like asset` 而没有 frontier/attachment controls。
- `IFS branch tree vs PS-RSLG pyrite lattice`，除非任务被重新定义为同一 transform-copy lattice 或同一 branching transform pattern。
- 用传统方法缺少 PBR 材质来证明我们的递归结构更好。
- 用我们的单个漂亮候选去对比 baseline 的平均或未调参结果。

## 2. Root Search 策略

Root search 是严格比较中最容易引入选择偏差的部分，必须单独记录。

### 2.1 Root policy 分级

| 等级 | 名称 | 使用条件 | 说明 |
|---|---|---|---|
| R0 | same-root | baseline 和 PS-RSLG 都可从同一 root anchor 或同一 root mesh 出发 | 最强公平设置，优先使用 |
| R1 | same-category matched-root | baseline root 不可直接复用，但可在同类别池中找相似 root | 需要公开候选池和筛选指标 |
| R2 | generated matched-root | 需要用生成模型生成同类别 root | 必须固定 prompt、seed、步数、筛选预算 |
| R3 | procedural-root proxy | 传统 baseline 或 PS-RSLG 只能使用程序 root proxy | 只能作为结构对齐实验，不能证明最终资产质量 |
| R4 | non-matched-root | 类别或模式不完全一致 | 不得进入主表胜负，只能列为 exploratory/failure |

### 2.2 必需搜索流程

1. 预先定义候选池：每个 case 至少记录 `N_root_candidates`，包括失败候选。
2. 先用类别和结构指标筛选，再运行最终纹理/PBR；不能先看最终美图再倒选 root。
3. 每个候选保存 root render、root mesh path、root metrics、seed、prompt、生成或选择命令。
4. root 对齐至少检查：bbox aspect、root anchor 位置、主轴方向、terminal handle 数量、初始连通性、类别 prompt score。
5. 若没有找到 matched root，case 记为 `root_match_failed`，不能用邻近类别替代。

### 2.3 Root anchor 与尺度

- 植物、树、根、藤：root anchor 固定在最低点或指定 trunk/root base，主轴 upright。
- DLA/coral/crystal：seed/frontier root 固定为中心 seed、底部 attachment 或指定晶核；必须说明是哪一种。
- IFS/transform：root motif 固定为第 0 层 motif，后续 affine copies 必须可追踪到该 motif。
- 所有 mesh 在指标前归一化到同一 bbox 约束，但指标 JSON 必须保留原始尺度和归一化尺度。

## 3. Per-family Matched Case Matrix

### 3.1 L-system / branch rewriting

| Baseline task | Baseline controls | PS-RSLG matched task | PS-RSLG analogous controls | 可比较指标 | 不能替代为 |
|---|---|---|---|---|---|
| pine branch | axiom、production rules、angle、segment length、depth、taper | PS-RSLG pine branch | branch handle selector、branch angle distribution、length/taper schedule、per-depth projection | branch angle/length distribution、tip survival、path-to-root、rendered pine-branch category | vine、root network、generic tree |
| tree canopy | branching grammar、depth、leaf/tip density、symmetry/randomness | PS-RSLG tree canopy | trunk/root anchor、canopy branching handles、tip density target、collision/competition | canopy coverage、tip count、branch nodes、bbox crown ratio、CLIP/DINO category score | vine scaffold、coral cluster |
| root/vine L-system | turtle branching/curling、depth、turn bias | PS-RSLG root/vine | root/vine handles、curl/tropism controls、attachment projection | root path length、junction count、tip survival、support connectedness | tree canopy unless task is redefined |

Fairness note：如果 baseline 是 L-system pine/tree canopy，则 ours 必须生成 pine/tree canopy；之前的 vine 正例只能作为 root/vine case，不可挪用。

### 3.2 Space colonization / attractor competition

| Baseline task | Baseline controls | PS-RSLG matched task | PS-RSLG analogous controls | 可比较指标 | 失败标签 |
|---|---|---|---|---|---|
| tree canopy attractor coverage | attractor set、kill distance、influence radius、step size、iterations | PS-RSLG tree canopy with space competition | attractor field、handle competition、growth step、projection budget、tip density | attractor coverage、uncovered attractor ratio、branch length、tip count、canopy silhouette IoU | wrong_category_vine |
| root network | attractor field below/around root、collision radius | PS-RSLG root network | root handles、soil/volume attractors、exclusion mask、per-depth projection | path-to-root、coverage、branch density、collision count | canopy_substitution |

Fairness note：space colonization 在结构控制上很强。我们的胜负不能只看连通性，而要看同任务下是否同时保持 recursive-state connectedness、资产渲染质量和可导出性。

### 3.3 DLA / frontier accretion

| Baseline task | Baseline controls | PS-RSLG matched task | PS-RSLG analogous controls | 可比较指标 | 不能替代为 |
|---|---|---|---|---|---|
| coral DLA | walker count、stickiness、seed、neighborhood、kill radius、voxel resolution | PS-RSLG coral frontier growth | frontier handles、stickiness analog、local attachment mask、bridge/prune policy、porosity control | frontier attachment survival、porosity、cavity count、surface smoothness、fragment count、root-connected frontier rate | smooth generic coral asset without DLA/frontier controls |
| crystal DLA | lattice neighborhood、anisotropy、seed、growth bias | PS-RSLG crystal frontier growth | anisotropic frontier selector、facet/contact handles、lattice/radial transform constraints | facet consistency、growth anisotropy、frontier validity、symmetry/contact error | pyrite lattice unless same crystal frontier pattern |
| porous cluster | voxel diffusion growth、threshold、resolution | PS-RSLG porous frontier cluster | occupied support proposal、cavity-preserving projection、local naturalization | Euler proxy、surface/volume, cavity preservation、blockiness | tree/root/canopy |

Hard rule：如果 baseline 是 DLA crystal/coral，ours 必须保留 DLA/frontier structure 的 controls。只能把非物理、资产化的 coral 写成 `coral-inspired frontier asset`，不能声称复现真实 DLA。

### 3.4 IFS / transform-copy growth

| Baseline task | Baseline controls | PS-RSLG matched task | PS-RSLG analogous controls | 可比较指标 | 不能替代为 |
|---|---|---|---|---|---|
| IFS branch tree | affine maps、probabilities、depth、scale、rotation | PS-RSLG affine branch tree | transform-copy operator、branch handles、scale/rotation schedule、projection | transform orbit error、branch topology、self-similarity, path-to-root | crystal lattice unless IFS target is lattice |
| radial transform motif | group order、rotation axis、scale、depth | PS-RSLG radial motif | radial copy operator、axis lock、contact/admissibility projection | radial symmetry error、copy survival、contact consistency | branch tree |
| scale-down growth / portal | contraction maps、visible window、depth | PS-RSLG scale-down recursive motif | local transform frame、LOD/cache descriptor、visible-window projection | zoom consistency、feature survival、transform drift、token growth | one-shot texture detail |
| lattice transform | affine lattice basis、depth、pruning | PS-RSLG lattice transform | lattice transform operator、facet/contact projection、mask naturalization | lattice contact, orbit error, symmetry IoU, component count | IFS tree unless target is tree |

Hard rule：IFS 不是一个可随意替换的视觉类别。baseline 的具体 affine pattern 必须被 PS-RSLG 的 transform operator 支持，否则报告为 `operator_not_supported`。

## 4. Operator Composition

每个 PS-RSLG matched task 必须公开 operator stack，而不是只给最终 mesh。

### 4.1 通用组合

```text
root state
-> typed handle/frontier selection
-> rule proposal with matched controls
-> local transform and mask construction
-> occupancy competition / collision filtering
-> per-depth admissibility projection
-> optional masked local naturalization
-> decode / render / re-encode / cache update
```

### 4.2 与传统方法的映射

| 传统控制 | PS-RSLG 对应项 | 必须记录 |
|---|---|---|
| L-system production rule | typed branch rule proposal | rule id、handle type、branch count |
| turtle angle / length | local transform schedule | angle mean/std、length/taper schedule |
| space colonization attractor | external field / competition target | attractor set、coverage、rejection |
| DLA stickiness | frontier attachment probability / mask acceptance | attach rate、rejected frontier、orphan frontier |
| DLA lattice neighborhood | frontier neighbor stencil | neighborhood type、anisotropy |
| IFS affine map | transform-copy operator | matrix、probability、scale、rotation |
| pruning / collision | admissibility projection | deleted mass、survived handles |
| texture/material step | appearance export | must be separate from structure metrics |

### 4.3 Projection variants

每个主 case 至少保留这些列：

| 列 | 目的 | 是否主表必需 |
|---|---|---|
| Traditional baseline | 传统结构控制上限 | 是 |
| Direct sparse grammar | 暴露 naive recursion 碎片传播 | 是 |
| Final-only projection | 证明最后清理不足 | 是 |
| Per-depth prune projection | 当前保守 PS-RSLG 核心 | 是 |
| Per-depth bridge-aware projection | DLA/crystal/frontier 必需压力列 | DLA/晶体必须 |
| Full PS-RSLG with masked naturalization | 最终资产候选 | 有 true mesh/GLB 证据才进 |

## 5. Metrics

### 5.1 通用结构和连通指标

- `occupancy_component_count_6n`
- `largest_occupancy_component_ratio_6n`
- `root_component_ratio`
- `orphan_mass_ratio`
- `path_to_root_rate`
- `frontier_validity`
- `orphan_handle_rate`
- `projection_survival_ratio`
- `deleted_mass_ratio`
- `component_growth_rate_by_depth`
- `vertices / faces / occupied_voxels / bbox`
- `face_component_count`
- `largest_face_component_ratio`
- `nonmanifold_edges / degenerate_faces / boundary_edges`
- mesh load success、GLB export success、render success

### 5.2 Family-specific metrics

| Family | 必报指标 |
|---|---|
| L-system / branch | branch angle distribution、branch length distribution、tip count、branch node count、tip survival、trunk/root path length、canopy silhouette coverage |
| Space colonization | attractor coverage、uncovered attractor ratio、influence radius sensitivity、branch density、collision/rejection count |
| DLA / frontier | frontier attachment survival、stickiness effective rate、porosity/cavity count、surface-to-volume proxy、Euler proxy、blockiness、fake bridge count |
| Crystal / lattice | symmetry IoU、facet normal consistency、contact graph consistency、anisotropy score、lattice orbit error |
| IFS / transform | transform orbit error、copy survival ratio、self-similarity score、zoom consistency、scale drift、radial/lattice symmetry error |
| Asset readiness | GLB import/export, PBR channel completeness, texture seam diagnostics, file size, render warnings |

### 5.3 Visual and semantic metrics

- 多视角 category prompt score 只能作为辅助指标。
- DINO/CLIP zoom consistency 只能辅助说明视觉一致性，不能替代结构指标。
- 人工 QA 标签必须与硬指标分列，包括：`wrong_category`、`wrong_recursive_mode`、`floating_shards`、`fake_bridge`、`over_pruned`、`over_smoothed`、`texture_masks_geometry_failure`、`root_mismatch`。

## 6. Visual Protocol

最终主图必须重渲，不直接使用筛选图。

### 6.1 Upright square pure-white overview

- 画布为正方形，建议 `1800 x 1800` 或更高。
- 背景必须为纯白 `RGB(255,255,255)`；不得有平台、地面、地平线、灰色渐变、卡片边框或接触阴影边界。
- 使用 orthographic camera；同一 matched pair 使用相同视角、相同尺度规则和相近填充比例。
- 物体 upright：树、根、藤类 root/base 在下方；晶体/DLA/coral 按预定义 seed/base 或主轴竖直；IFS/transform 按第 0 层 motif 主轴固定。
- 物体在正方形内填充约 82% 到 92%，不得裁切 terminal tips 或 callout 区域。
- 图内不放解释性文字；只保留必要的子图编号，说明放 caption。

### 6.2 Nested callouts

每个 case 至少提供 overview + 三个 nested zoom：

1. root/seed attachment zoom；
2. primary junction/contact/frontier zoom；
3. terminal tip、facet、cavity 或 transform-copy zoom。

DLA/coral/crystal 额外需要 cavity/frontier/facet callout。IFS/transform 额外需要 level-to-level self-similarity callout。

Callout 规则：

- overview 中用细矩形框标出 zoom 区域，矩形不得遮挡关键结构。
- zoom 必须来自同一个 3D mesh 的相机级放大或重新渲染；2D crop 只能作为草图，不作为最终主图。
- nested callout 需要保持方向一致：overview、zoom-1、zoom-2 的上方向相同。
- 同一行 baseline 与 ours 的 callout 类型必须一致，例如都看 root attachment、都看 branch junction、都看 terminal tip。
- 如果 ours 没有对应结构，必须空缺并标记 failure，不得换一个更好看的局部。

### 6.3 Figure layout

推荐主图布局：

| 行 | 内容 |
|---|---|
| Row 1 | Traditional baseline overview + nested callouts |
| Row 2 | Direct sparse grammar or final-only projection failure |
| Row 3 | Proposed per-depth projection / Full PS-RSLG |
| Row 4 | 指标小表或附图编号引用，不把大量文字放入图内 |

如果版面不足，主文保留 baseline vs proposed + 关键 failure 列；完整 operator columns 放 supplement。

## 7. Reporting Wins and Failures

### 7.1 胜利的最低条件

一个 case 只有同时满足下面条件，才允许写成 PS-RSLG 在该 matched task 上胜出：

1. `target_category` 与 baseline 一致。
2. `recursive_mode` 与 baseline 一致。
3. baseline controls 有 PS-RSLG analogous controls，并公开参数。
4. root policy 为 R0、R1 或 R2；R3 只能支撑 structure proxy，R4 不能判胜。
5. 结构指标不劣于 baseline 的关键结构强项，或明确说明 tradeoff。
6. 连通和 frontier 指标通过预设阈值。
7. upright square pure-white overview 与 nested callouts 通过人工 QA。
8. 若报告 PBR/GLB 优势，必须先通过 neutral geometry render 和 mesh metrics。

### 7.2 公平失败报告

必须按 case 报告失败，不得只隐藏失败候选：

| Failure label | 含义 | 报告方式 |
|---|---|---|
| `wrong_category` | 类别不匹配，如 tree canopy 被 vine 替代 | 不能进入主胜负表 |
| `wrong_recursive_mode` | 递归模式不一致，如 DLA 被 smooth coral 替代 | 标为 exploratory |
| `root_match_failed` | root search 未找到合格同类 root | 报候选数和失败原因 |
| `operator_not_supported` | PS-RSLG 无法表达 baseline pattern | 作为方法边界 |
| `floating_shards` | 出现漂浮碎片或孤立 component | 报 component/orphan 指标 |
| `fake_bridge` | 连接是粗糙、视觉不可信或非 grammar-proposed | 进入 negative ablation |
| `over_pruned` | 为连通性牺牲主要结构 | 报 deleted mass 和 tip loss |
| `over_smoothed` | naturalization 洗掉递归结构 | 报 branch/tip/frontier preservation |
| `texture_masks_geometry_failure` | 纹理好看但几何失败 | 分离 appearance 与 structure |

### 7.3 表述模板

可以写：

> 在 `DLA coral frontier` matched task 中，PS-RSLG 使用 frontier attachment operator、stickiness analog 和 per-depth admissibility projection，与传统 DLA 的 coral/frontier controls 对齐。该 case 在 root-connected frontier、surface renderability 和 nested callout QA 上通过，但不声称复现物理 DLA。

不应写：

> 我们的 coral 比 DLA 好。

可以写：

> 在 `IFS radial motif` matched task 中，PS-RSLG 的 transform-copy operator 支持相同 radial group order，并报告 transform orbit error 与 copy survival。

不应写：

> pyrite lattice 证明我们优于 IFS tree。

## 8. 主表建议

主表每行对应一个严格 matched case：

| case_id | family | target category | recursive mode | baseline | PS-RSLG operator stack | root policy | depth | primary pass | wins | failures |
|---|---|---|---|---|---|---|---:|---|---|---|
| `lsys_pine_branch` | L-system | pine branch | branch rewriting | L-system pine | branch handles + angle/length/taper + per-depth projection | R0/R1 | D | pending | pending | pending |
| `sc_tree_canopy` | Space colonization | tree canopy | attractor competition | SC canopy | attractor field + handle competition + projection | R0/R1 | D | pending | pending | pending |
| `dla_coral_frontier` | DLA | coral | frontier accretion | DLA coral | frontier attach + stickiness analog + bridge/prune projection | R0/R1/R2 | D | pending | pending | pending |
| `dla_crystal_frontier` | DLA | crystal | frontier/lattice accretion | DLA crystal | anisotropic frontier + facet/contact projection | R0/R1/R2 | D | pending | pending | pending |
| `ifs_affine_tree` | IFS | affine branch tree | transform-copy branching | IFS tree | affine copy + branch handles + projection | R0/R1 | D | pending | pending | pending |
| `ifs_radial_lattice` | IFS | radial/lattice motif | transform-copy lattice | IFS lattice | radial/lattice copy + contact projection | R0/R1 | D | pending | pending | pending |

现有非严格候选可以保留在 appendix 或 screening table，但主文胜负表必须只使用上面这种同类别、同模式、同控制的 matched cases。

## 9. 最小执行清单

1. 为每个 baseline 先锁定 `target_category` 和 `recursive_mode`。
2. 建立 root candidate pool，并按 R0/R1/R2/R3/R4 记录 root policy。
3. 为 PS-RSLG 写出 analogous controls，不支持就标 `operator_not_supported`。
4. 跑 baseline、direct sparse、final-only、per-depth projection、必要的 bridge-aware/full PS-RSLG。
5. 每层保存 mesh 和 metrics；最终保存 neutral render、textured render、GLB/PBR。
6. 用 upright square pure-white camera protocol 重渲 overview。
7. 对 root/junction/tip/frontier/facet/transform 做 nested callouts。
8. 生成 case-level table：wins、failures、tradeoffs、不可比较项。
9. 论文中只声明通过 strict matched-task 的结果；不通过的结果进入 failure/limitation。
