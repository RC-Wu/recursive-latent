# 最新视觉/指标结果的论文整合建议（2026-05-09）

范围：本文只整合当前已有 AgentDoc plan、QA 文档、baseline/metric 结果与论文叙事建议；不修改 `paper_siga/main.tex`，不启动远端/GPU，不改其他文件。

核心判断：当前论文最稳的主线不是“我们生成了所有类别的拓扑干净 3D asset”，而是：

> 在 generation-model-native 的递归稀疏状态中，projection/connected support 必须放进每一层递归 transition；这样才能把有限深度递归资产的 voxelized 6-neighborhood connected support 变成可报告的不变量。Trellis2 texture/PBR route 是 selected connected scaffold 的资产化兼容性验证，不是拓扑正确性的证明。

这条主线可以成立，但必须把 claim、baseline、metric 和视觉证据拆开写。尤其要避免把 occupancy connected、mesh face connected、PBR renderability、真实物理/算法生长混成一个结论。

## 1. 证据分级总览

### 1.1 应进主文的结果

| 证据 | 推荐主文角色 | 可支持 claim | 必须附带 caveat |
|---|---|---|---|
| `projection_ablation_mesh_contact_20260509`：vine/tree direct vs final-only vs per-depth | 核心方法证据 | projection 放进递归 transition 比 direct/final-only 更稳定；conservative `compete` 是当前主线 | 只覆盖最干净的 vine/tree conservative operator；不代表 fork/radial/DLA 全部解决 |
| vine depth textured stages 1-4 | 主文 selected recursive asset / depth behavior | fixed route 下 depth 展示保持 occupancy connected 与 root reachability proxy | raw textured GLB face components 极高；branch/tip 仍是 mesh-voxel proxy，不是真 skeleton |
| `bismuth_hopper_bismuth_hq` / `connected_pyrite_bismuth` | 主文 non-tree connected scaffold 小 panel 或 teaser 支撑 | 非 tree / crystal-like connected scaffold 可被 Trellis2 PBR 化 | 只能叫 bismuth-like / crystal-like scaffold；不能写真实晶体生长或 topology-clean mesh |
| `pyrite_lattice_pyrite_hq` | 主文小 panel 或强 appendix | crystal-lattice scaffold 在 occupancy support 上连通、视觉语义清楚 | pyrite depth mesh comps 可随 depth 增至 139；应标注 mesh/face diagnostic caveat |
| latest traditional texture rerun `traditional_baseline_texture_20260509_rerun1554` | 主文公平性/诊断 panel，或主文短段 + 补充完整图 | 传统 L-system/space-colonization 也能经同一 texture route 得到可渲染资产；baseline 不是 strawman | 不能用它 claim 我们在连通性上全面优于传统方法；`dla_cluster` 可作为视觉/语义负例 |
| matched structural baseline matrix `tree/root/vine` | 主文一句 sanity check 或 supplement 主表 | 同 root/seed/depth/renderer 下，传统结构基线与 proposed proxy 都能 occupancy-connected | 它反而证明传统 structural baseline 很强；不能说 proposed 在该矩阵中 connectivity 优于传统 |

主文最稳的组合是：方法图 + projection ablation + vine depth/control 展示 + 一张 claim-boundary/metric 表 + 少量 non-tree connected scaffold 视觉 + 传统 baseline 诊断。不要把所有 gallery 资产都塞进主文，否则 claim 宽度会超过证据。

### 1.2 应进 supplement 的结果

| 证据 | Supplement 角色 | 原因 |
|---|---|---|
| 完整 `baseline_matrix_20260509` per-depth CSV、contact sheet、protocol | Matched Structural Baseline Matrix | 主文只需承认传统 baseline 强；完整 36 行、depth/iteration caveat 放补充 |
| `connected_scaffold_v2_textured_glb_qa` 全部 case | Non-tree Connected Scaffold Appendix | bismuth/pyrite 可主文，volumetric DLA/coral 与 porous_coral 更适合补充 |
| `coral_depth_textured_showcase_20260509` | Method-behavior / non-tree depth showcase | stage 2-4 强，stage 1 有极小 island；适合补充或主文一小条，不宜作为 DLA 成功主 claim |
| `coral_stage4_guide_sweep` | Texture guide control | 几何相同、只变材质/guide；不能当几何消融 |
| `coral_density_param_showcase` | Parameter-control supplement | 全部连通，但视觉差异弱、occupied voxels 不单调；不适合主 claim |
| `branch_path_metrics_tree_root_vine` | Metric appendix / screening | 目前 mesh 行是 voxel proxy，不能当真实 branch/tip skeleton metric |
| older matched-guide texture diagnostic | Sensitivity / diagnostic appendix | 它显示同 guide texture route 可严重碎片化，但最新 rerun 已更强，不能单独作为主文传统失败证据 |
| local repair/radial4 QA | Repair appendix / negative-control | 可说明 voxel closure 在 radial4 上有效但面积增长大；不宜包装成主方法 |

### 1.3 应作为负面/边界呈现的结果

| 边界结果 | 应如何写 | 不应如何写 |
|---|---|---|
| DLA bridge ablation | post-hoc bridge / sparse closing 的负例或 stress-test；fake bridge、over-closing 说明 metric 改善不等于语义正确 | 不写成 DLA 已解决 |
| `hard_dla` / cache smoke over-closing | 说明 hard connectivity mask 可能牺牲 DLA 语义 | 不写成 cache/SDE 成功 |
| `volumetric_dla_coral` | DLA/coral-inspired connected scaffold，证明 grammar-native connected support 更稳 | 不写真实 DLA physics、random-walk hitting distribution 或 frontier process 已复现 |
| `porous_coral` / `connected_porous_octopus` | porous/organic asset 候选，适合补充 | 不作为主文高保真生物/coral 成功图 |
| pyrite depth mesh component growth | occupancy connected 与 face/mesh diagnostic 不一致的典型 caveat | 不忽略 mesh comps 增长，也不写 clean crystal topology |
| textured GLB raw face fragmentation | PBR/export surface splitting caveat；单独报告 face diagnostics | 不用 textured beauty render 替代 topology proof |
| `largest_component` / aggressive bridge repair | diagnostic lower bound 或 negative ablation | 不作为主图修复方法 |

## 2. 主文 claim 的推荐写法

### 2.1 核心 claim

建议主文只写以下强度：

> We treat connected voxelized support as a per-depth invariant of recursive sparse-latent generation. On selected vine/tree conservative growth cases, placing projection inside the recursive transition yields substantially cleaner connected-support diagnostics than direct recursion or final-only cleanup.

中文解释：这个 claim 对应 projection ablation，目标是说“每层 projection 是必要设计”，不是说所有输出 mesh 拓扑干净。

### 2.2 视觉/资产化 claim

建议写：

> Trellis2 texture/PBR export can be applied to selected connected scaffolds, producing renderable textured GLB assets for vine and non-tree scaffold candidates such as bismuth-like hopper and pyrite-like lattice examples.

必须跟一句 caveat：

> We report mesh/face diagnostics separately because GLB material and face islands do not imply topology-clean surfaces.

### 2.3 传统 baseline claim

最新 QA 后，传统 baseline 必须写得更公平：

> Classical L-system and space-colonization baselines are strong structural controls: under a fair tube-occupancy structural protocol, they are also root-attached and occupancy-connected. We therefore use them as sanity baselines rather than strawman failures, and evaluate our design claim through direct/final-only/per-depth projection ablations.

Texture baseline 可以另写：

> Passing traditional scaffolds through the same texture route tests whether appearance transfer alone solves asset readiness. The latest rerun shows several traditional baselines are renderable and near-connected, while DLA-like clusters remain visually blocky; thus texture export is necessary but not sufficient, and geometry/scaffold semantics must be evaluated separately.

不要再用“传统方法经 texture 后都碎，所以我们胜出”作为主文逻辑。早先 matched-guide texture diagnostic 可以放 supplement，作为 texture-route sensitivity，而不是最终 baseline closure。

### 2.4 Non-tree / DLA / crystal claim

推荐写法：

> For non-tree cases, connected scaffold construction provides stress-test assets for crystal-like and porous/DLA-inspired families. These examples demonstrate scaffold connectivity and PBR compatibility, not physical crystallization or true DLA growth.

主文若空间有限，non-tree 只选 `bismuth_hopper_bismuth_hq` 和 `pyrite_lattice_pyrite_hq`。`volumetric_dla_coral_octopus_hq` 更适合 appendix/stress-test，除非补齐 frontier/porosity/zoom QA。

## 3. 图表组织建议

### Figure 1：Teaser / result strip

目的：展示方法能生成可渲染递归资产，但不要让 teaser 暗示所有类别都已严格解决。

建议内容：

- 一列 vine depth 或 vine final textured asset，承接 tree/root/vine 主线；
- 一个 bismuth-like connected scaffold HQ；
- 一个 pyrite-like lattice HQ；
- 可选一个 coral/DLA-inspired connected scaffold，但 caption 必须写 stress-test / inspired scaffold。

Caption 必须包含三点：selected connected scaffolds、true textured GLB render、topology diagnostics reported separately。

### Figure 2：Method overview

目的：把论文从“procedural + generator 拼接”改成“递归稀疏状态语言”。

建议结构：

`typed grammar handle -> proposal support/features -> competition/projection -> masked Trellis2 naturalization -> decode/render/export -> cache/update`

图中突出 per-depth projection 是 transition 的一部分，而不是最终 cleanup。不要把所有 classical coverage 证明塞进主图，可把 IFS/L-system/space-colonization/DLA/shape grammar coverage 做成小 taxonomy 或 appendix table。

### Figure 3：Projection ablation 主证据

主文必须保留。推荐结构：

| case | direct | final-only | per-depth projection |
|---|---|---|---|
| vine compete | render + comps/LCR | render + comps/LCR | render + comps/LCR |
| tree compete | render + comps/LCR | render + comps/LCR | render + comps/LCR |

数值口径：

- vine direct：raw mesh comps 2059，LCR 0.9049；
- vine final-only：2，LCR 0.9934；
- vine per-depth：1，LCR 1.0000；
- tree direct：3201，LCR 0.9169；
- tree final-only：4，LCR 0.9842；
- tree per-depth：2，LCR 0.9949。

Caption 写法：这是 conservative `compete` 线的 mesh-render diagnostic，证明 projection-in-transition 的必要性。不要声称 fork/DLA/radial 全部通过。

### Figure 4：Connected support vs depth / claim-boundary table

建议做成主文 table 或 compact plot：

列：

`family | case | depths | primary occupancy evidence | mesh/face caveat | allowed claim`

推荐行：

- vine depth：stage 1-4 `occ_comp_6n=1`, `occ_lcr_6n=1.0`，root ratio 1.0；caveat 是 raw face comps 极高；
- bismuth hopper depth：stage 1-4 occupancy connected，mesh comps 2-4；caveat 是 bismuth-like scaffold；
- pyrite lattice depth：occupancy connected，mesh comps 可增至 139；caveat 是 lattice scaffold；
- volumetric coral depth：stage 2-4 GLB connected，stage 1 有极小 island；caveat 是 DLA/coral-inspired stress。

这张表的价值是主动约束 claim，避免审稿人认为作者隐藏失败。

### Figure 5：Baseline organization

建议拆成两部分，不要混在一个 conclusion 中。

**5A. Matched structural sanity check**  
主文短表或 supplement 主表：L-system、space-colonization、proposed_connected 在 tree/root/vine 的最终 depth 全部 `occ_comp_6n=1`, `occ_lcr_6n=1.0`, `root_component_ratio=1.0`。解释为“传统 baseline 是强结构控制”，不是“proposed connectivity 更强”。

**5B. Texture/export diagnostic**  
使用最新 `traditional_baseline_texture_20260509_rerun1554`：

- `sc_tree_canopy` strict `1 / 1.000`，可作为传统正例；
- `sc_root_vine` strict `2 / 0.9999`，radius-1 `1 / 1.000`；
- `lsystem_branch` strict `2 / 0.9999`，radius-1 `1 / 1.000`；
- `dla_cluster` strict `4 / 0.9998`，radius-1 `1 / 1.000`，但视觉块状、语义不足。

这张图说明 texture route 公平地给了传统方法机会，并且传统方法有强结果；我们的比较焦点应放在递归 projection semantics、生成式自然化和多尺度/非树 scaffold 表达上。

旧 matched-guide texture diagnostic（218/278/315/62 comps）不建议主文单独使用。若保留，放 supplement 并解释协议差异，避免与最新 rerun 冲突。

### Figure 6：Method-behavior controls

主文可选，supplement 更稳。

优先级：

1. vine depth strip：最贴近主线；
2. coral depth strip：stage 2-4 好，stage 1 caveat；
3. coral density parameter：全部连通，但视觉差异弱，放 supplement；
4. guide sweep：只说明 material guide control，不说明 geometry。

Caption 中统一使用 `method-behavior visualization`，不要写成 causal ablation，除非实验真正只隔离了一个因素。

## 4. Baseline/metric 章节建议结构

### 4.1 Baseline 小节

建议按任务分三类写：

1. **Structural baselines**：L-system、space-colonization、IFS/lattice。评价 root-attached connected support、tips、branch nodes、path/root reachability。强调它们是强基线。
2. **Ablation baselines**：direct recursion、final-only cleanup、prune-per-depth、bridge-per-depth、proposed per-depth projection。这里才是方法优势的主证据。
3. **Texture/export diagnostics**：同一 Trellis2 texture/PBR route 下传统/proposed selected scaffolds 的 renderability。该部分不替代 geometry baseline。

这个拆法可以化解当前结果之间的表面矛盾：传统方法在 structural tube-occupancy 上强，早先 texture diagnostic 有碎片，最新 texture rerun 又有 near-connected 强例。它们回答的是不同问题，不能互相覆盖。

### 4.2 Metric 小节

建议明确三层指标：

**Primary support metric**  
`occupancy_component_count_6n` 和 `largest_occupancy_component_ratio_6n`。主文 positive result 至少应逐 depth 报告，而不是只报 final。

**Root / recursion metric**  
`root_component_ratio`、`path_to_root_rate`、`orphan_mass_ratio`、`orphan_tip_proxy`。当前 vine 和部分 tree/root 只有 proxy，必须标注 `mesh_voxel_proxy`；space-colonization skeleton 指标较强，但尚未与 proposed 完全 matched。

**Diagnostics**  
raw/welded mesh components、face component count、largest face/vertex ratio、non-manifold/watertight、occupied voxels、token/vertex/face growth。它们不能替代 primary occupancy，但必须报告以暴露 GLB/face fragmentation。

Family-specific 指标建议：

- tree/root/vine：tips、branch nodes、path length/span、junction/root/tip zoom；
- bismuth/pyrite：facet size、contact area、symmetry/contact error、cavity/facet zoom；
- DLA/coral：frontier attachment、branch openness、porosity/cavity、fake bridge / over-closing label。

### 4.3 Claim gate

建议给每个进入主文图的 case 加一个小 gate：

| gate | 主文正例最低要求 |
|---|---|
| support | per-depth `occ_comp_6n=1` 或明确解释极小 island |
| root | root ratio / path-to-root proxy 接近 1，orphan proxy 低 |
| diagnostic | mesh/face fragmentation 已报告，不隐藏 |
| visual | fixed-camera neutral render 或 mesh render；texture render 只补资产化 |
| semantic | 图像在 neutral render 下能读出对应 family 结构 |

没过所有 gate 的结果不进主文正例，只进 supplement/negative。

## 5. 各结果的具体去向

### 5.1 Vine / tree / root

主文：

- projection ablation 的 vine/tree conservative `compete`；
- vine textured depth strip；
- claim-boundary 表中的 vine connected support 和 raw face caveat。

Supplement：

- branch/path/root reachability proxy 全表；
- tree/root/vine matched structural baseline matrix；
- public guide texture GLB 表。

写法边界：

- 可以写 finite-depth recursive vine/tree supports；
- 不能写 tree/root/vine topology 完全解决；
- 不能把 mesh proxy 的 tip count 当真实 branch skeleton。

### 5.2 Bismuth / pyrite / crystal-like

主文：

- `bismuth_hopper_bismuth_hq` 作为 non-tree connected scaffold star candidate；
- `pyrite_lattice_pyrite_hq` 作为 crystal-lattice scaffold candidate，若篇幅允许。

Supplement：

- connected scaffold v2 全表；
- bismuth/pyrite depth metrics；
- facet/contact/symmetry 指标缺口说明。

写法边界：

- 可以写 bismuth-like / pyrite-like lattice scaffold；
- 不能写真实 crystal growth、nucleation、facet physics；
- pyrite mesh component growth 必须写成 caveat。

### 5.3 Coral / DLA-inspired

主文：

- 只有在需要展示非树广度时，选一张 `volumetric_coral_depth` 或 `volumetric_dla_coral_octopus_hq`，并明确为 inspired connected scaffold/stress test。

Supplement：

- coral depth stage 1-4；
- coral density parameter control；
- guide sweep；
- DLA bridge ablation failure；
- traditional `dla_cluster` texture rerun。

写法边界：

- 可以写 grammar-native connected coral/DLA-inspired scaffold 比 post-hoc bridge 更可用；
- 不能写 true DLA process、frontier distribution 或 physical coral growth；
- stage 1 small island、fake bridge、over-closing 都应保留。

### 5.4 Traditional baselines

主文：

- matched structural matrix 作为一句 fairness check；
- latest traditional texture rerun 作为 baseline diagnostic，展示传统方法也可渲染、但 DLA-like cluster 仍语义不足。

Supplement：

- full matrix；
- old matched-guide sensitivity；
- neutral zoom 需求清单。

写法边界：

- 承认传统 structural baselines 很强；
- 方法优势不能写成“传统不连通”，而应写成“我们的递归 transition 把 projection/connected support 纳入生成语义，并在 direct/final-only ablation 中显示必要性”。

## 6. 论文叙事的推荐顺序

1. **Problem**：递归 3D generation 的失败不是缺一个最后修补，而是碎片/无效 handle 会进入下一层状态。
2. **Method**：定义 sparse-latent recursive grammar；projection、competition、masked naturalization 是 transition semantics。
3. **Primary evidence**：direct/final-only/per-depth projection ablation，说明 projection-in-transition 的必要性。
4. **Depth behavior**：vine/coral/bismuth/pyrite 的 connected support vs depth，展示方法行为，但限制 claim。
5. **Baselines**：传统方法作为强结构控制；matched structural matrix 不判传统失败；texture rerun 说明 appearance route 公平且不是唯一问题。
6. **Asset compatibility**：selected connected scaffolds 通过 Trellis2 texture/PBR 导出 GLB。
7. **Limitations**：DLA/coral physics、crystal growth、raw face fragmentation、mesh skeleton metrics、material coherence 都未完全解决。

## 7. 需要补但不应阻塞当前整合的实验

P0：真正的 tree/root/vine ablation matrix。

- Methods：L-system、space-colonization、direct sparse grammar、final-only、prune-per-depth、bridge-per-depth、proposed；
- Controls：同 root、同 seed、同 depth、同 camera/renderer；
- Metrics：occupancy comps/LCR、root reachability、path-to-root、orphan mass/tips、tips、branch nodes、mesh diagnostics；
- QA：neutral front/side/top/iso，root/junction/tip zoom。

P1：bismuth/pyrite semantic metrics。

- facet/contact/symmetry/cavity；
- neutral facet/contact zoom；
- 不依赖材质暗示类别。

P1：DLA/coral stress closure。

- true voxel DLA/frontier baseline；
- frontier attachment、porosity/cavity、branch openness；
- fake bridge / over-closing labels。

P2：texture/material consistency。

- 同几何多 guide 与同 guide 多几何分开；
- PBR channel completeness、same-camera render、texture masking failure labels。

## 8. 可直接给主文/图注使用的短句

可用：

> We report connected support using voxelized 6-neighborhood components and largest-component ratio, and separately report mesh/face diagnostics because textured GLB exports may contain many material or face islands.

可用：

> The matched structural baseline matrix shows that classical procedures are strong connected-support baselines under fair tube-occupancy protocols; our method claim is therefore evaluated against direct/final-only/per-depth projection ablations rather than by treating classical baselines as disconnected failures.

可用：

> Non-tree examples are presented as connected scaffold and PBR-compatibility results, not as physical crystallization or true DLA growth models.

不要用：

> Our method solves DLA/crystal/tree topology.

不要用：

> Textured GLB render proves mesh topology is clean.

不要用：

> Traditional baselines fail connectivity.

不要用：

> Coral density demonstrates monotonic parameter control.

## 9. 本文依据的主要本地文档

- `/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_system_grammar_plan_20260508.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/claim_aligned_metric_summary_zh_20260509.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/baseline_matrix_paper_integration_zh_20260509.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/baseline_metric_reviewer_closure_zh_20260509.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/projection_ablation_mesh_render_qa_zh_20260509.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/baseline_matrix_zh_20260509.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/branch_path_metrics_tree_root_vine_zh_20260509.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/connected_coral_texture_reruns_qa_zh_20260509.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/traditional_baseline_texture_rerun1554_qa_zh_20260509.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/traditional_matched_guide_texture_baseline_zh_20260509.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/connectivity_visual_qa_next_actions_zh_20260509.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/connected_scaffold_v2_textured_glb_qa_zh_20260509.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/connected_scaffold_cases_v2_zh_20260509.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/coral_depth_textured_showcase_zh_20260509.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/coral_density_parameter_control_zh_20260509.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/paper/current_story_risk_audit_zh_20260509.md`
