# Baseline / Metric Gap Closure Plan 20260509

范围：补齐当前论文实验中 baseline 与 metric 的缺口，重点处理连通性、DLA/晶体/非树碎块、公平 baseline 比较，以及同条件 depth/参数展示如何进入评估协议。

约束：本文档只作为本地评估与论文实验章节写作计划；不修改 `paper_siga/main.tex`，不使用 SSH，不改远端文件。

## 0. 当前结论

当前证据足以支撑一个收窄后的主线：**projection-stabilized recursive execution 需要把 root-attached connected support 作为每层递归状态的不变量，而不是最终 mesh cleanup**。但它还不足以支撑“我们在连通性上击败所有传统方法”或“DLA/晶体生成已解决”。

最关键的 gap 是：

1. 传统 L-system / space-colonization 在公平 tube-occupancy 条件下也能连通，因此传统 baseline 不能被写成连通性失败的 strawman。
2. 当前 matched structural matrix 只有 `lsystem`、`space_colonization`、`proposed_connected`，缺 `direct_sparse_grammar`、`final_only_projection`、`prune_per_depth`、`bridge_per_depth`、完整 `proposed_per_depth`。
3. DLA/coral/crystal/radial/cache-repair 结果有局部改善，但许多仍是 bridge struts、voxel slabs、surface soup 或语义坍缩，必须降级为 stress / negative / supporting。
4. 同条件 depth/参数展示已经有 mesh/textured-mesh 资产基础，但必须写成 method behavior characterization，并绑定固定 root、seed、camera、renderer、material/texture schedule 与逐层指标。

## 1. Baseline / Metric 状态表

| 模块 | 当前状态 | 证据来源 | 论文使用等级 | 仍缺什么 |
|---|---|---|---|---|
| 评估协议文档 | 已完成第一版 | `recursive_growth_baseline_metric_protocol_zh_20260509.md` | 可作为实验协议依据 | 需要把 verdict 标签落实到新 CSV 和 figure caption |
| matched structural baseline matrix: tree/root/vine | 部分完成 | `baseline_matrix_paper_integration_zh_20260509.md` | fairness sanity check | 缺 direct/final-only/prune/bridge/proposed-per-depth 同矩阵 |
| 传统 L-system / space-colonization occupancy 连通性 | 已完成但反直觉 | 同上 | 必须正面承认传统 baseline 强 | 不能用来证明 proposed connectivity 胜出 |
| 传统 baseline texture export diagnostic | 只算诊断 | matched-guide texture 结果在现有文档中总结 | supporting/diagnostic | 不能和 structural matrix 混为一个公平实验 |
| projection ablation: direct vs final-only vs per-depth | 部分完成 | `projection_ablation_table.csv` | conservative compete 可支持主 claim | fork cases 仍失败；缺 mesh/textured-mesh fixed-camera QA |
| conservative compete cases | 已有强数值 | vine direct `2059` comps -> per-depth kept `1`; tree direct `3201` -> per-depth kept `2` | 主方法 ablation 候选 | 需要 same-render mesh strip 和 root/junction/tip zoom |
| expressive fork cases | 诊断/失败边界 | fork direct `11490/12166` comps，per-depth LCR 仍 `0.5758/0.6141` | negative ablation | 不能写成 per-depth projection fully solves expressive recursion |
| connected textured depth showcases | 部分完成 | active plan 中 vine/bismuth/pyrite/coral depth 记录 | method behavior / supplement | 需要统一表格：depth、Comp_6n、LCR、root ratio、render verdict |
| connected_best_expansion texture metrics | 只算候选 QA | `metrics.csv`: root-vine/pyrite `Comp=1,LCR=1.0`; porous/scifi `Comp=3,LCR≈0.993/0.995` | selected supporting | face fragmentation 极高，不能单独证明 mesh topology clean |
| DLA bridge-aware / cache repair | stress / negative | active plan 的 DLA bridge ablation 与 cache repair QA | negative/supporting | 需要 grammar-native connected DLA，而非 post-hoc bridge |
| crystal / pyrite / bismuth | supporting scaffold | bismuth/pyrite depth 与 connected scaffold notes | non-tree/lattice scaffold evidence | 不能写成物理晶体生长或严格 symmetry theorem 已验证 |
| branch/path/root reachability | 部分完成 | branch/path worker 输出被 plan 记录 | supporting metric | 还未完全并入 matched same-root matrix |
| same-condition depth/parameter protocol | 协议明确，证据部分完成 | protocol doc + depth/parameter showcase docs | method behavior | 需要固定条件表、曲线、zoom QA 与 verdict 标签 |
| mesh-level topology metrics | 诊断为主 | raw GLB face components 在多处被证明过敏 | diagnostic only | primary 仍应是 occupancy 6N + visual QA + root reachability |

## 2. 传统方法“有利条件下也能连通”的风险与正确比较维度

### 风险

当前 matched structural matrix 的重要事实是：在 same root、same seed、same depth、same renderer、tube-occupancy proxy 下，传统 L-system 和 space-colonization 也能得到 root-attached occupancy-connected support。最终深度上，传统方法与 `proposed_connected` 都可以达到 `occ_comp_6n=1`、`occ_lcr_6n=1.0`、`root_component_ratio=1.0`。

因此论文不能写：

- proposed 在这个矩阵中比 L-system / space-colonization 更连通；
- 传统 procedural baseline 结构失败；
- mesh face components 高就说明传统 baseline 拓扑失败；
- texture export fragmentation 可以反推传统 structural baseline 不连通。

### 更正确的比较维度

论文中的公平比较应改为多轴，而不是单一 connectivity 胜负：

| 比较维度 | 传统方法公平优势 | proposed 应该回答的问题 | 可用指标 |
|---|---|---|---|
| root-attached occupancy support | L-system / space-colonization 强 | proposed 是否也维持每层 root-attached support | `Comp_6n`, `LCR_occ`, `root_component_ratio`, `orphan_mass_ratio` |
| 递归状态稳定性 | 传统规则天然离散稳定 | projection 是否必须放在每层 transition，而不是最终 cleanup | direct/final-only/per-depth 曲线、component growth |
| 结构控制类型 | L-system 规则化，space-colonization coverage 强 | proposed 是否在 sparse latent / generated asset path 中保留控制 | tips、branch nodes、coverage、path-to-root、projection survival |
| asset-readiness | 传统 mesh 可渲染但通常 schematic | proposed 是否能进入 textured GLB / material path 且保持可用几何 | GLB import、fixed-camera render、material validity、visual QA |
| 非树/多尺度行为 | 传统 IFS/shape grammar 有强先验 | proposed 是否能展示 connected non-tree scaffold、depth/parameter behavior | transform/symmetry error、depth strips、parameter grid、zoom crops |
| failure boundary | 传统方法不是同一失败模式 | proposed 在 expressive fork、DLA、crystal 上哪里失败 | negative ablation verdict、bridge artifacts、surface fragmentation |

推荐写法：

> The matched structural matrix is a fairness check rather than a connectivity victory: classical structural baselines are connected under favorable tube-occupancy conditions. The projection claim is evaluated separately by comparing direct recursion, final-only cleanup, and per-depth projection under the same recursive task, while asset-readiness is assessed through fixed-render mesh/textured-mesh QA.

## 3. DLA / crystal / 非树碎块线的严谨处理

### 可以主张

| 方向 | 可主张内容 | 条件 |
|---|---|---|
| DLA/frontier coverage in grammar | PS-RSLG 的规则模板可以表达 frontier attachment、occupancy exclusion、stochastic accretion | 作为理论覆盖或 appendix proof sketch |
| DLA/coral-inspired connected scaffold | 当前 volumetric coral / connected scaffold 可以作为 DLA-inspired stress/control result | 必须写成 inspired scaffold，不写成 faithful DLA physical generator |
| bridge-aware projection | post-hoc bridge 可以改善某些 occupancy 指标，暴露 design tradeoff | 作为 negative/supporting ablation，配 zoom 显示 bridge cost |
| bismuth/pyrite/crystal scaffold | connected lattice / hopper scaffold 能展示非树 recursive asset 和 PBR compatibility | 写成 crystal-inspired/lattice scaffold，不写成严格物理晶体生长 |
| cache/repair selected meshes | 说明 real Trellis2 texture path 可以处理某些 repaired/non-tree inputs | 仅支持 pipeline compatibility |

### 必须降级

| 情况 | 降级标签 | 原因 |
|---|---|---|
| DLA bridge 后处理出现人工 struts | `negative_ablation` | 指标改善不等于自然连通资产 |
| hard-DLA / radial / cache repair 读成 capped blocks 或 voxel slabs | `stress_only` | surface occupancy 可能连通，但视觉语义失败 |
| porous/crystal textured GLB face islands 极多 | `surface_fragmentation_diagnostic` | raw GLB face components 被 UV/material islands 干扰，只能诊断 |
| bismuth/pyrite 外观像矿物但生成规则不是物理晶体 | `supporting_scaffold` | 不能 claim physical crystal growth |
| DLA/coral stage 1 有小岛但 LCR 很高 | `conditional_candidate` | 可省略 stage 1 或明确 tiny proxy island caveat |

### 不能主张

- DLA / crystal / radial fragmentation 已解决。
- Post-hoc closing / bridge 是通用拓扑修复方法。
- Trellis2 texture export 证明几何连通。
- raw face component count 可以直接作为跨 OBJ/GLB/UV/material 的主指标。
- connected scaffold 等价于物理 DLA 或真实晶体生长过程。

## 4. 同条件 depth / 参数展示进入评估协议的方式

同条件 depth/参数图不是普通 ablation，也不是只为好看。它们应作为 **method behavior characterization** 进入实验章节，回答递归系统在固定规则和资源预算下如何随 depth 或控制参数变化。

每个 depth/parameter row 必须记录：

| 字段 | 要求 |
|---|---|
| fixed condition | root、seed schedule、grammar family、renderer、camera、material/texture schedule、resolution |
| varied variable | depth 或单一参数，如 density、bridge budget、projection threshold、mask radius、sampler alpha |
| per-stage metric | `Comp_6n`, `LCR_occ`, `root_component_ratio`, `orphan_mass_ratio`, vertices/faces/tokens |
| render evidence | neutral mesh 或 textured-mesh fixed-camera strip |
| local QA | root/junction/tip/bridge/facet/cavity zoom，至少对主 claim case 提供 |
| verdict | `method_behavior`, `paper_safe_candidate`, `diagnostic_only`, `negative_ablation`, `do_not_claim` |

推荐图注原则：

> Depth and parameter rows characterize the behavior of the recursive transition under fixed conditions. They should not be interpreted as unrelated ablations or as proof of a monotonic control law unless the sweep isolates one variable and reports the corresponding curves.

当前可优先整理的展示：

| 展示 | 当前判断 | 放置建议 |
|---|---|---|
| vine textured depth | 最稳，stage 均 occupancy-connected | 主文或主文精简 + supplement |
| bismuth hopper depth | 非树 connected scaffold，PBR 兼容 | 主文 supporting 或 supplement |
| pyrite lattice depth | lattice/symmetry scaffold 强，但 stage 1 caveat | supplement 或主文选 stage 2-4 |
| coral depth | DLA/coral-inspired connected scaffold，仍需谨慎 | supplement/control evidence |
| coral density/parameter | qualitative control，不是强 calibrated law | supplement 或 method behavior panel |
| cache repair / DLA bridge | negative/supporting | appendix failure analysis |

## 5. 下一批最小必要实验清单

所有实验必须输出 mesh 或 textured-mesh 可验证资产；matplotlib/point-cloud 只能做内部诊断。

### P0. Tree/root/vine projection-stability matched matrix

目标：补上论文最核心方法 claim：projection inside recursive transition 优于 direct recursion 与 final-only cleanup。

设置：

| 项 | 最小要求 |
|---|---|
| cases | `tree`, `root`, `vine` |
| methods | `traditional_lsystem`, `traditional_space_colonization`, `direct_sparse_grammar`, `final_only_projection`, `prune_per_depth`, `bridge_per_depth`, `proposed_per_depth` |
| fixed conditions | same root anchor, seed schedule, max depth 1-4, occupancy resolution, renderer, camera |
| outputs | per-depth OBJ/GLB, neutral mesh strip, optional textured GLB for final candidates |
| metrics | `Comp_6n`, `LCR_occ`, `root_component_ratio`, `orphan_mass_ratio`, `path_to_root_rate`, `orphan_tip_count`, `tips`, `branch_nodes`, `projection_survival_ratio`, `bridge_mass_ratio`, `mesh_component_count` diagnostic |
| pass condition | proposed per-depth 每层 root-attached；direct/final-only 的失败模式可见；traditional 被公平展示为 strong structural baseline |

### P0. Fixed-camera zoom QA for the same matrix

目标：避免 overview contact sheet 掩盖假桥、碎片、端点断裂或 surface soup。

最小视图：

| 视图 | 用途 |
|---|---|
| overview iso/front/side | 比较整体结构 |
| root attachment zoom | 验证 root-connected |
| primary junction zoom | 验证分叉或 bridge 自然性 |
| terminal tip zoom | 验证递归末端不是碎片 |
| failure zoom | direct/final-only/bridge 的 orphan、fake bridge、surface soup |

### P0. DLA/coral bridge-aware stress matrix

目标：把 DLA 从“看起来碎”变成严谨 negative/stress 分析，并定义何时能晋升。

设置：

| 项 | 最小要求 |
|---|---|
| cases | `hard_dla`, `volumetric_coral`, optional `porous_scaffold` |
| methods | direct frontier, final-only cleanup, prune-per-depth, bridge-per-depth, grammar-native connected scaffold |
| outputs | neutral mesh stages + bridge zoom; textured GLB 只作为 optional |
| metrics | component growth, root ratio, bridge added voxels, bridge length distribution, bridge survival, face/surface fragmentation diagnostic |
| claim boundary | 若有 bridge struts 或 blocky slabs，一律 negative/supporting；只有 mesh zoom 通过才可升为 main |

### P1. Crystal/lattice fairness and symmetry closure

目标：把 pyrite/bismuth 从“好看候选”变成可评估的 non-tree scaffold result。

设置：

| 项 | 最小要求 |
|---|---|
| cases | bismuth hopper, pyrite lattice, radial/IFS transform-copy |
| baselines | IFS/crystal lattice/radial transform-copy, direct sparse, final-only, proposed scaffold |
| metrics | `Comp_6n`, `LCR_occ`, transform/symmetry error, lattice contact/facet diagnostic, render verdict |
| outputs | fixed-camera mesh/textured-mesh depth strip, facet zoom |
| claim boundary | lattice/scaffold/PBR compatibility；不写 physical crystal growth solved |

### P1. Matched texture/export compatibility after structural closure

目标：连接 structural matrix 与 texture/PBR，但不混淆二者。

设置：

| 项 | 最小要求 |
|---|---|
| inputs | 从 P0 matrix 中选择传统和 proposed final-depth mesh |
| guide | same guide per case family |
| methods | same Trellis2 texture/PBR schedule |
| metrics | GLB import/render status, material validity, occupancy proxy after export, raw face components diagnostic, visual QA |
| paper use | 说明 texture path 兼容 selected projected meshes；texture alone 不是 topology repair |

### P2. Space-colonization / branch-path fairness metrics

目标：承认传统方法的强项，避免 baseline section 被审稿人认为挑指标。

指标：

| 指标 | 用途 |
|---|---|
| attractor coverage | space-colonization 强项 |
| nearest-attractor distance | coverage quality |
| tips / occupied volume | branching density |
| branch length / angle distribution | morphology comparison |
| collision/self-intersection proxy | structure quality |
| skeleton path-to-root | root reachability |

## 6. 论文实验章节中文小节草稿大纲

### 6.1 实验设置与公平协议

我们将实验分为三类：结构优先的递归增长、同条件 depth/参数行为展示，以及 texture/PBR asset-readiness。所有结构比较优先使用 neutral mesh render 和 occupancy 6-neighborhood connectivity；textured GLB 结果只用于外观与导出兼容性，不作为几何正确性的单独证据。传统 L-system、space-colonization、IFS/晶格和 DLA/frontier 方法在各自有利的结构条件下作为强 baseline，而不是失败样本。

报告字段包括 `Comp_6n`、`LCR_occ`、`root_component_ratio`、`orphan_mass_ratio`、branch/path metrics、vertices/faces/tokens、projection survival 和 bridge cost。raw face components 保留为 GLB/UV/material fragmentation diagnostic。

### 6.2 Matched Structural Baseline Matrix

在 tree/root/vine 上，我们首先运行 matched structural-control matrix。该矩阵固定 root、seed、depth 和 mesh renderer，用于确认比较协议没有把传统方法设成 strawman。结果应明确指出：L-system 与 space-colonization 在 tube-occupancy proxy 下也能生成 root-attached connected supports。因此，该矩阵是 fairness check，不是 proposed 在 connectivity 上击败传统方法的证据。

### 6.3 Projection-Stability Ablation

核心方法 claim 由 direct recursion、final-only cleanup、prune-per-depth、bridge-per-depth 和 proposed per-depth projection 的同条件比较支撑。已有 projection ablation 显示，保守 `compete` cases 中 direct recursion 会产生数千碎块，final-only cleanup 只能修最终状态，而 per-depth projection 能显著降低 fragment propagation。expressive fork cases 则作为失败边界：projection 能降低爆炸但不能保证复杂表达下的单连通资产。

### 6.4 同条件 Depth 与参数行为展示

Depth/parameter panels 展示递归 transition 在固定 root、guide、camera、renderer 和 texture schedule 下的行为，而不是简单 ablation。vine depth 可作为主 positive；bismuth/pyrite/coral depth 可作为 non-tree/lattice/coral-inspired supporting panels。每个 panel 应配套 per-stage connectivity metrics 和局部 zoom，参数 sweep 只声明 controllability 与 failure boundary，不声明未校准的单调控制律。

### 6.5 DLA / Crystal / Non-tree Stress Results

DLA、crystal、radial 和 cache-repair 结果单独成节，避免污染主 claim。DLA/frontier growth 可作为 grammar coverage claim，但当前 bridge/postprocess 结果只支持 stress/negative 分析：人工桥、块状封闭或 surface soup 不能升为主结果。bismuth/pyrite 目前更适合写成 connected crystal-inspired scaffold 和 PBR compatibility，而不是物理晶体生长。

### 6.6 Texture/PBR Export Compatibility

Texture/PBR 章节回答 asset-readiness，而非 topology proof。传统 baseline 与 proposed meshes 都应在同 guide 或 matched guide 条件下测试 Trellis2 texture export。若传统 scaffolds texture 后仍出现大量 occupancy fragments，这只能说明 texture export alone 不能自动修复结构；若 proposed projected meshes 成功导出 textured GLB，则说明 projection-stabilized geometry 可以进入外观合成路径。

### 6.7 Verdict 与 Claim Boundary

最终实验表应为每个 case/method 标注 `paper_safe_candidate`、`matched_structural_sanity`、`method_behavior`、`diagnostic_only`、`negative_ablation`、`surface_fragmentation_diagnostic` 或 `do_not_claim`。论文主文只使用前两三类；diagnostic 与 negative 进入 supplement 或 failure analysis。

## 7. 直接可贴入论文的保守表述

> We do not treat classical procedural methods as weak connectivity baselines. Under favorable matched tube-occupancy conditions, L-systems and space-colonization can produce root-attached connected supports. Our projection claim is therefore evaluated on a different axis: whether recursive generated states remain admissible at every depth, and whether direct or final-only cleanup allows fragment errors to propagate through subsequent recursive steps.

> DLA- and crystal-like examples are reported as stress cases unless they pass both occupancy connectivity and fixed-camera mesh QA. Bridge-based repair can improve scalar connectivity but may introduce visible artificial struts or blocky closures; such cases are used to delimit the method rather than to claim solved physical growth.

> Same-condition depth and parameter panels characterize recursive behavior under fixed roots, cameras, renderers, and material schedules. They are included to show stability, control, and failure boundaries, not as unrelated visual ablations.
