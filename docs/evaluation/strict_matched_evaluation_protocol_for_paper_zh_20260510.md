# 严格同任务评估协议：论文主文可用版本

创建时间：2026-05-10  
适用范围：`paper_siga/main.tex` 的 Experiments / Results / Discussion 修订，以及后续同任务 baseline 结果表、主图和 supplement 组织。本文档只定义论文应采用的严格协议和写作边界，不声明所有实验已经完成。

## 0. 一句话原则

本文的比较必须是 **exact matched-task comparison**：传统方法做什么递归任务，PS-RSLG 就必须在同一最终对象类别、同一形状语义、同一复杂度/深度预算、同一递归增长模式下做同一个任务。若根源对象可以搜索或改进，只能在最终类别、形状、复杂度、深度和增长模式都匹配传统任务时进入主表；否则只能作为筛选、诊断或失败材料。

旧的 `L-system/vine`、`IFS/pyrite`、`DLA/crystal-like` 等 loose semantic comparison 只能保留为 screening artifact：它们说明早期搜索空间、失败模式或视觉候选来源，不能作为论文主文的胜负证据。

## 1. 任务定义

每个主文 case 必须定义为一个严格任务记录，而不是一张好看的图。

| 字段 | 主文要求 |
|---|---|
| `case_id` | 唯一任务编号，例如 `lsys_pine_branch_d5`、`sc_tree_canopy_d5`、`dla_coral_frontier_d4`、`ifs_affine_branch_d5` |
| `traditional_family` | L-system、space colonization、DLA/frontier、IFS/transform-copy、shape grammar 等 |
| `target_category` | 最终对象类别，如 pine branch、tree canopy、root/vine、coral cluster、crystal cluster、affine branching tree |
| `target_shape` | 可见形状约束，如 upright trunk+canopy、root network、branch fan、porous cluster、faceted lattice |
| `recursive_mode` | branch rewriting、attractor competition、frontier accretion、affine transform-copy、radial/lattice copy、scale-down recursion |
| `depth_complexity_budget` | 传统 depth/iteration/particle/copy 数与 PS-RSLG depth/token/face/vertex/runtime 的对齐规则 |
| `root_policy` | same-root、same-category matched-root、generated matched-root 或 procedural proxy；必须记录搜索池和失败数 |
| `controls` | 传统控制变量和 PS-RSLG analogous controls 的一一映射 |
| `outputs` | per-depth mesh、final OBJ/GLB、neutral render、textured render、metrics JSON/CSV、失败标签 |
| `pass_fail_rule` | 哪些结构、类别、连通、复杂度、视觉和资产可用条件必须同时满足 |

主文推荐先保留 3-4 个高质量任务，而不是扩大弱矩阵：

1. `tree/root/vine branch or attractor task`：要求分支层级、root path、tip/junction 可见。
2. `space-colonization tree canopy`：要求同一 attractor set、coverage、branch path 和 root-connected support。
3. `DLA/coral frontier cluster`：要求同一 frontier/stickiness/seed policy，并报告 porosity/cavity/fake-bridge。
4. `IFS/transform-copy task`：只有当 transform orbit、copy survival、scale/rotation hierarchy 可见时进入主文；否则作为失败边界。

## 2. Fairness 协议

### 2.1 不允许的替代

- 传统 baseline 是 L-system pine/tree canopy，PS-RSLG 不能用 vine/root 正例替代。
- 传统 baseline 是 DLA coral/crystal，PS-RSLG 不能只用 generic coral-like 或 pyrite-like polished asset 替代；必须保留 frontier/stickiness/seed 或明确写成 `coral-inspired frontier asset`。
- 传统 baseline 是 IFS affine branch tree，PS-RSLG 不能用 pyrite lattice 或 generic radial ornament 替代，除非传统任务也被重新定义为同一 lattice/radial transform-copy。
- 不能用传统 baseline 缺少 PBR 材质证明我们的递归结构更好；材质/GLB 是 asset-readiness 指标，必须与结构指标分列。
- 不能用单个精选 PS-RSLG 候选对比传统 baseline 的未调参或平均失败结果。

### 2.2 Root search

Root source 可以改进，但必须预注册：

| 等级 | 名称 | 是否可进主文胜负表 | 条件 |
|---|---|---|---|
| R0 | same-root | 是，优先 | 同一 root anchor 或同一 root mesh |
| R1 | same-category matched-root | 是 | 同类别候选池、筛选指标、失败候选全部记录 |
| R2 | generated matched-root | 谨慎 | prompt/seed/steps/search budget 固定，先筛 root 再看 texture |
| R3 | procedural proxy root | 仅结构表 | 只能证明结构对齐，不能证明最终资产质量 |
| R4 | non-matched root | 否 | 只能作为 screening/failure |

筛选顺序必须是：类别/形状/anchor/复杂度指标通过后，才进入 texture/PBR 或主图候选；不得先看最终美图再倒选 root。

### 2.3 输出公平性

- 同一 matched pair 使用相同相机、尺度归一化、背景、渲染器和图像分辨率。
- 中性 mesh render 与 textured/PBR render 分开。中性 render 用于结构判断；PBR render 用于资产可用性。
- 传统方法如果输出 skeleton，应允许公平 tube/mesh 化，不能用未焊接 cylinder face components 惩罚它。
- PS-RSLG 如果用 projection 删除碎片，必须报告 deleted mass、survived handles、orphan/fake bridge，而不能只展示清理后结果。

## 3. Baseline 列设计

每个主表 case 至少需要这些列：

| 列 | 作用 | 主文状态 |
|---|---|---|
| Traditional matched baseline | 传统结构控制强项 | 必需 |
| Direct sparse/proxy grammar | 暴露 naive recursion 碎片传播或 blob 化 | 必需 |
| Final-only projection | 证明最后清理不足 | 必需 |
| Per-depth prune projection | 当前 PS-RSLG 核心执行语义 | 必需 |
| Bridge-aware / connector projection | DLA、coral、crystal/frontier 压力任务 | 对 frontier 必需 |
| Masked local naturalization | 资产化候选 | 有真实 mesh/GLB 和结构指标时进主文 |

旧的宽松图可以放 supplement 的 `Screening and Failure Artifacts` 小节，并明确标注：

- `L-system/vine loose comparison`：不同类别，不能进主表。
- `IFS/pyrite loose comparison`：不同 transform target，不能进主表。
- `DLA/pyrite or bismuth loose comparison`：若无 frontier/facet/stickiness 对齐，只能说明候选视觉和导出能力。

## 4. Metrics

### 4.1 硬拓扑与 mesh 指标

这些是主文结构 claim 的基础：

- `occupancy_component_count_6n`
- `largest_occupancy_component_ratio_6n`
- `root_component_ratio`
- `path_to_root_rate`
- `orphan_mass_ratio`
- `orphan_handle_rate`
- `frontier_validity`
- `projection_survival_ratio`
- `deleted_mass_ratio`
- `fake_bridge_count`
- `component_growth_rate_by_depth`
- `vertices / faces / occupied_voxels / bbox`
- `face_component_count`
- `largest_face_component_ratio`
- `nonmanifold_edges / degenerate_faces / boundary_edges`
- mesh load success、GLB export success、render success

主文措辞：连通性必须写成 “occupancy proxy / mesh diagnostic / GLB face diagnostic” 的具体版本，不能泛称 topology solved。

### 4.2 Family-specific 指标

| Family | 必报指标 |
|---|---|
| L-system / branching | branch angle distribution、branch length distribution、tip count、branch node count、tip survival、trunk/root path length、canopy silhouette coverage |
| Space colonization | attractor coverage、uncovered attractor ratio、nearest-attractor distance、branch density、collision/rejection count、tip count |
| DLA / frontier | frontier attachment survival、effective stickiness、orphan frontier rate、porosity/cavity proxy、surface-to-volume proxy、Euler proxy、blockiness、fake bridge count |
| Crystal / lattice | facet normal consistency、contact graph consistency、anisotropy score、symmetry IoU、lattice orbit error |
| IFS / transform | transform orbit error、copy survival ratio、self-similarity score、scale drift、radial/lattice symmetry error、zoom consistency |

### 4.3 Render-based CLIP/DINO 指标

CLIP/DINO 只能作为类别和视觉一致性的辅助证据，不能替代结构指标。

建议报告：

- 多视角 category prompt score：对象类别是否仍是 tree/coral/crystal/root/vine。
- matched prompt margin：目标 prompt 分数减去邻近错误类别 prompt 分数，例如 tree canopy vs vine/root/coral。
- DINO multi-view consistency：同一 mesh 多视角特征稳定性。
- zoom consistency：overview、junction、tip/cavity/facet zoom 是否保持同一类别/结构。
- failure labels：`wrong_category`、`wrong_recursive_mode`、`blob_naturalization`、`orbit_lost`、`fake_bridge`、`over_pruned`、`texture_masks_geometry_failure`。

这些指标只能支持 “visual/category alignment improves or fails under the matched task”；不能写成 “CLIP proves recursive fidelity”。

### 4.4 复杂度、深度与 zoom 指标

深度/复杂度必须以 per-depth 形式报告：

- depth 或 iteration 对齐规则；
- token/voxel/vertex/face 增长曲线；
- branch/tip/frontier/copy 数量随深度变化；
- deleted mass 与 projection survival 随深度变化；
- runtime 和 GPU memory 随深度变化；
- zoom panel 中 root、junction/frontier、terminal tip/facet/cavity 的可见结构是否保留。

允许 claim：per-depth projection 在有限深度下维持 root-attached admissible state，并暴露稳定性-表达力 tradeoff。  
不允许 claim：无限递归、物理生长精确模拟、超越基础模型分辨率，除非另有专门实验。

### 4.5 Runtime / controllability

主文或 supplement 至少提供：

- 每深度 rule proposal、masked naturalization、decode、projection、re-encode、texture export 时间；
- peak GPU memory；
- token/face/vertex 增长；
- 控制变量 sweep：branch angle、density、stickiness、attractor count、transform scale/rotation；
- 失败率和 seed robustness。

Controllability 只能由固定其余变量、单独改变一个控制量的 row 支撑。宽松 guide sweep 只能说明外观敏感性，不能证明结构控制。

## 5. Figure / Table 设计

### 5.1 主文 Figure A：严格 matched task panel

推荐布局：

| 行 | 内容 |
|---|---|
| Row 1 | Traditional matched baseline neutral render + root/junction/tip zoom |
| Row 2 | Direct or final-only failure render + 对应 zoom |
| Row 3 | Per-depth projection / full PS-RSLG neutral render + 对应 zoom |
| Row 4 | 同 case 的小指标条：components、root ratio、family metric、failure label |

规则：

- 所有 overview 为正方形纯白背景、orthographic camera、同尺度。
- zoom 必须是同一 3D mesh 的 camera-level zoom，不用 2D crop 作为最终证据。
- baseline 与 ours 的 zoom 类型必须一致。若 ours 缺少 terminal tip/facet/copy，就标 failure，不换一个好看的局部。

### 5.2 主文 Figure B：projection ablation

使用同根、同深度、同 operator：

`direct -> final-only -> per-depth prune -> bridge-aware/full`

Caption 必须说明：

- direct/final-only 让无效 component 在中间层成为 parent/frontier/cached motif 的风险；
- per-depth projection 是 recursive transition 的一部分；
- mesh face components 和 occupancy components 是不同诊断。

### 5.3 主文 Figure C：multi-scale zoom panels

每个正例至少给：

1. overview；
2. root/seed attachment；
3. primary junction/contact/frontier；
4. terminal tip、facet、cavity 或 transform-copy level；
5. 若是 IFS/scale-down，必须有 level-to-level zoom consistency。

这个图的 claim 是 “结构可检查且多尺度细节未完全丢失”，不是 “无限 zoom”。

### 5.4 主文 Table 1：claim map

建议保留现有 claim-map 的思想，但更新为严格协议：

| Claim | Required evidence | Allowed wording | Forbidden wording |
|---|---|---|---|
| finite-depth sparse-latent recursion | per-depth states, handles, projection trace | finite-depth admissible growth | infinite recursion solved |
| matched structural improvement | same task, same root/depth, direct/final/per-depth columns | stabilizes selected matched tasks | beats all procedural systems |
| asset export compatibility | GLB/PBR import/render on projected meshes | selected projected meshes export | texture proves topology |
| classical baselines are strong | fair tube/mesh/metric protocol | structure and asset readiness are separate | procedural baselines are strawmen |

### 5.5 主文 Table 2：strict matched metrics

列建议：

`case, family, target, method, depth, occ comps, occ LCR, root ratio, family metric 1/2, CLIP/DINO category margin, runtime, failure label`

只把通过 task matching 的 case 放入主表。Screening artifacts 单独放 supplement。

## 6. 允许与禁止的论文 claim

### 6.1 允许

- “We evaluate under exact matched tasks: category, recursive mode, root policy, depth/complexity budget, and rendering protocol are matched per case.”
- “Per-depth projection stabilizes finite-depth recursive state by preventing detached support from becoming later handles.”
- “Classical procedural baselines remain strong structural baselines; our evaluation separates structural fidelity, category alignment, and asset-readiness.”
- “Selected projected meshes can be exported through the frozen texture/PBR path, but export success is not used as topology evidence.”
- “Loose earlier L-system/vine and IFS/pyrite comparisons are retained only as screening artifacts and failure diagnostics.”

### 6.2 禁止

- “PS-RSLG beats L-systems / DLA / IFS” without strict same-task, multi-row, multi-metric evidence.
- “Connected occupancy proves correct branching, DLA physics, crystal growth, or transform-copy recursion.”
- “Trellis2 texture export proves structural correctness.”
- “A pyrite/coral/vine visual candidate substitutes for an unmatched L-system or IFS task.”
- “Depth rows prove monotonic controllability” unless the variable is isolated and measured.

## 7. `paper_siga/main.tex` patch plan

本轮没有直接修改 `paper_siga/main.tex`，因为主线程负责最终 Overleaf 集成。建议按以下顺序最小修改。

### 7.1 Abstract

位置：abstract 末尾已有 `\EvidencePending{Fill final quantitative improvement numbers...}`。

建议：

- 把 “relative to direct sparse editing and final-only cleanup” 限定为 “under strict matched tasks where category, recursive mode, root policy, and depth/complexity budget are controlled”。
- 加一句负责任边界：older loose semantic comparisons are screening artifacts, not final evidence。

### 7.2 Introduction / Contributions

位置：Introduction contributions 第 4 条。

建议：

- 把 “across branching, frontier-growth, and transform-copy families” 改成 “under exact matched task protocols for selected branching/frontier/transform families”。
- 明确 classical baselines 不是 strawman：传统系统提供强结构控制，本文比较的是 strict matched task 下的 recursive-state stability、asset readiness 和局部生成先验。

### 7.3 Related Work / Evaluation paragraph

位置：`\subsection{Generative Control, Editing, and Evaluation}` 末尾。

建议：

- 加一句 “object-level render metrics are auxiliary; matched recursive fidelity requires topology, family-specific control metrics, and zoom-panel inspection.”
- 避免把 CLIP/DINO 写成核心结构指标。

### 7.4 Experiments opening

位置：`\section{Experiments and Results}` 后 `Claims under test`。

建议替换主线为：

```tex
% TODO(strict-matched): Rewrite this paragraph so every quantitative comparison is gated by exact matched task criteria: same final category/shape, same recursive mode, matched root policy, matched depth/complexity budget, and same render/metric protocol. Loose L-system/vine and IFS/pyrite comparisons should be named only as screening artifacts or failure diagnostics.
```

正文建议写：

- “We separate strict matched evaluations from exploratory screening artifacts.”
- “A case enters the main table only if category, recursive mode, root policy, depth/complexity budget, and output protocol match.”
- “Older loose comparisons are moved to supplement/failure diagnostics.”

### 7.5 Tasks subsection

位置：`\subsection{Tasks}`。

建议：

- 增加 task record 表：case_id、family、target_category、recursive_mode、root_policy、depth_complexity_budget、controls、outputs、pass_fail。
- 把当前 tree/root/vine/pyrite/coral/bismuth 等视觉组重新分成 `strict matched main cases` 与 `screening artifacts`。
- 明确 L-system pine/tree 只能对 PS-RSLG pine/tree；vine 只能对 root/vine task。

### 7.6 Baselines subsection

位置：`\subsection{Baselines}`。

建议：

- 增加列：traditional matched baseline、direct sparse/proxy grammar、final-only projection、per-depth prune、bridge-aware/full。
- 说明 traditional skeleton/tube mesh 需要公平 voxel/tube 化；不能用 mesh face fragmentation 当作唯一传统失败。
- 把 `traditional_baseline_texture_rerun1554` 写成 texture/export diagnostic，而不是 structural win。

### 7.7 Metrics subsection

位置：`\subsection{Metrics}`。

建议：

- 分为四组：hard topology/mesh、family-specific、render-based category/CLIP-DINO、runtime/control。
- 明确 occupancy connectivity、raw mesh face components、GLB export diagnostics 的区别。
- 加 failure labels：wrong_category、wrong_recursive_mode、blob_naturalization、orbit_lost、fake_bridge、over_pruned、texture_masks_geometry_failure。

### 7.8 Result subsections

位置：`Per-Depth Projection...` 到 `Current Boundaries`。

建议：

- `Per-Depth Projection Stabilizes...` 只引用 strict matched cases 和 projection ablation，不混入 loose visual wins。
- `Baselines Separate Structural Control...` 明确传统方法在 fair tube/occupancy 下通常也可连通，差异不应简化为 “ours connected, baseline fragmented”。
- `Selected Projected Meshes...` 明确 GLB/PBR 是 export compatibility，不是 topology proof。
- `Depth and Parameter Control...` 保持 “method-behavior evidence”，不要写 calibrated monotonic control。
- `Current Boundaries` 显式列出 L-system blob、IFS orbit lost、DLA fake bridge/over-bridging 风险。

### 7.9 Figures and captions

建议修改 caption 的三类风险：

- 含 `traditional_baseline_texture` 的图：标注为 texture/export diagnostic，不作为 strict structural comparison。
- 含 `result_matrix` 的图：标注为 qualitative screening overview，不能作为 main evidence figure。
- 含 pyrite/bismuth/coral guide sweep 的图：除非同任务 controls 完整，否则只支持 selected export/candidate visual evidence。

### 7.10 Discussion / Limitations

位置：`\section{Discussion and Limitations}`。

建议新增限制：

- Strict matched tasks sharply reduce what can be claimed from earlier broad visual matrices.
- Connectivity can be achieved while losing branch semantics or transform orbit; therefore family-specific metrics and zoom inspection are required.
- Texture/PBR export is valuable but orthogonal to topology and recursive fidelity.

## 8. 立即执行建议

1. 主文先建立 `strict matched task protocol` 小段和表格，再决定哪些现有结果能进入主证据链。
2. 把 `L-system/vine`、`IFS/pyrite` 旧比较移动到 supplement/failure artifacts。
3. 对 tree/root/vine 的已有 same-root/same-depth CPU matrix，只写成 structure-first sanity check，不写成 outperform。
4. 优先补 Space Colonization 和 DLA/frontier 的 strict rows，因为现有 proxy 审计中它们最接近 matched-mode 正例。
5. IFS/transform-copy 在 transform orbit、copy survival、scale drift 未通过前不要进主文正例。
6. 每个正例都补 root/junction/tip 或 seed/frontier/cavity 的 camera-level zoom panel。
7. 把最终 claim 从 “视觉相似/类别相近” 改成 “同任务下 finite-depth recursive state stability + selected asset export compatibility”。
