# Reviewer 修改意见应用矩阵

日期：2026-05-09  
项目：Recursive 3D Generative Growth / SIGGRAPH Asia paper revision  
范围：基于 `/Users/fanta/Downloads/论文修改意见与reviewer批评整理.md`、当前 `paper_siga/main.tex`、`current_story_risk_audit_zh_20260509.md`、`ps_rslg_formal_framework_deep_zh_20260509.md`。  
约束：本文只做局部文档支线，不修改 `paper_siga/main.tex`。

## 0. 总体判断

当前 `main.tex` 已经吸收了 reviewer 批评中最核心的一组方法重写建议：引言已从“procedural + generator 互补”转向 “generation-model-native recursive language”；3.2 已用

\[
z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d)
\]

替代旧版八元组；3.3 已用 handle-to-proposal rule template 替代巨大 grammar tuple；3.4 已用 compact recursive transition

\[
z_{d+1}=
\operatorname{Enc}_{\theta}
\left[
\Pi_{\lambda_d}
\left(
\operatorname{Dec}_{\theta}
\left(
\mathcal T_{\theta}(z_d;\mathcal R_d,y)
\right)
\right)
\right]
\]

替代长串联公式，并且已经加入 masked flow naturalization、projection procedure、final-only cleanup 为什么不够、recursive effective resolution、material handles / texture export 等内容。

因此，当前主要问题已经不是“3.2/3.3/3.4 完全没改”，而是：

1. 需要把已经完成的结构性修改在后续 revision 中继续打磨成更正式、更短、更可审稿的论文语言；
2. 部分仍然过宽、过像状态报告或过像系统海报的内容，应转 appendix / supplement；
3. 负面结果、texture/PBR、DLA/crystal、infinite recursion、symmetry/cache 等内容必须保留边界，但要降调；
4. 主文应围绕最稳 claim：per-depth projection stabilizes finite-depth connected sparse-latent recursive assets。

## 1. Reviewer 意见逐条应用矩阵

| 编号 | Reviewer / 修改意见 | 当前 `main.tex` 状态 | 推荐处置 | 目标位置 | 优先级 |
|---|---|---|---|---|---|
| 1 | 整体故事线应从 trivial use 失败出发，而不是 procedural 与 generator 互补 | 已大幅完成。摘要和引言已经强调 2D scaffold 失败、direct sparse edit 碎片累积、global flow repair 改写拓扑、final-only cleanup 不足，并提出 generation-model-native recursive language | 继续保留，但进一步压缩旧版注释痕迹；正式投稿前删除 “Previous ... kept for revision trace” 注释 | `Abstract`, `Introduction` | P0 |
| 2 | 3.2/3.3/3.4 要大幅重构，避免大状态、大 tuple、大长公式 | 已完成核心结构。当前 3.2/3.3/3.4 已分别改成最小状态、规则模板、compact transition + execution algorithm | 继续打磨表达，避免重复；把过深证明或泛化内容下沉 | `Method` 主体 | P0 |
| 3 | Typed Sparse-Latent State 不要八元组，拆核心状态和 bookkeeping | 已完成。当前主状态是 `z_d=(V,F,A)`，bookkeeping 被明确排除在主数学状态之外 | 保持。可进一步把 admissible state 定义压短，避免 reader 在 3.2 过早进入全部 violation 项 | 3.2 主文；完整 violation 可进 appendix | P0 |
| 4 | Grammar and Rules 不要写巨大 tuple，改成语言组成对象 + rule template | 已完成。当前 3.3 写成 typed handles、rule templates、realization operators，并给出 rule family table | 保持。后续可以把表格精简成 5-6 个最有证据的 rule families；cache/material 可放补充 | 3.3 主文 + appendix | P0 |
| 5 | Operational semantics 应写成递归算法，而不是算子清单 | 已基本完成。3.4 有 compact transition 和 6 步 executable form | 建议改成正式 `Algorithm 1` 环境或更标准的 enumerated algorithm；把 projection 子步骤拆为 `Algorithm 2` | 3.4 主文 | P0 |
| 6 | Naturalize 应写成 masked flow / SDE sampling，而不是抽象黑箱 | 已完成。当前有 SDE、deterministic flow、masked clamp、sparse feature blend | 保持，但要强调 optional/local；不要让 reviewer 误以为当前实验充分验证了强 flow naturalization | 3.4 主文，细节 appendix | P0 |
| 7 | Classical systems as limits 放后面或附录，避免打断主线 | 当前仍在 Method 主体中作为 3.5 出现 | 建议正文只保留短段和一条公式；IFS/L-system/space-colonization/DLA/CGA 详细推导转 appendix | 3.5 压缩；Appendix A 扩展 | P1 |
| 8 | Symmetry / Cache / Infinite recursion 缺少强贡献 | 当前有 `Symmetry, Cache, and Recursion Scope`，内容谨慎但仍较宽 | 必须降调保留。主文只讲 finite-depth 和 bounded active support；symmetry equivariance 公式、visible-window infinite recursion 放 appendix 或 limitations | `Discussion`, appendix | P1 |
| 9 | 新增分辨率 / recursive refinement 论点 | 已完成。当前有 `Recursive Effective Resolution and Infinite Refinement` | 保留，但改标题避免 “Infinite” 过强。建议主文写 “Effective Resolution under Finite-Depth Refinement” | Method 后半或 Discussion | P1 |
| 10 | 新增材质 / Texture / PBR 方法说明 | 已完成。当前有 `Material Handles and Trellis2 Texture Export` | 保留但降调。必须持续强调 texture export 是 selected projected meshes 的兼容性，不是结构正确性或材质递归一致性证明 | Method + Results texture subsection | P0 |
| 11 | 第四章和第五章实验应合并 | 当前仍是 `Experiments` 后接 `Results`，但内容已经围绕 claims under test 收紧 | 可以继续保留两章，但建议改成一个统一 `Experiments and Results` 或将 Results 小节按 claim 组织 | 实验章节 | P1 |
| 12 | 负面结果不要作为主线展开 | 当前主文仍多次出现 holes、thin sheets、DLA negative、boundary case、weak rows 等 | 需要降调。主文保留最关键 caveat；其他失败图和负面诊断放 appendix/supplement | Results + Appendix | P0 |
| 13 | 图要改成常规论文格式，不要像 PPT | 当前 figure 数量多，result matrix / method overview / gallery 仍偏 poster 或状态总览 | 主文精选 claim-driven figures；大矩阵、density gallery、弱 showcase 放 supplement；图内文字减少，标准 subcaption | Figure plan | P1 |
| 14 | Projection 是核心贡献，但算法要更具体 | 当前已加入 projection 步骤和 objective，但仍写在段落中 | 建议正式拆为 `Algorithm 2: Projection Operator`，明确 mesh/voxel graph、root-attached component、component scoring、handle reattachment | 3.4 主文 | P0 |
| 15 | 实验章节像状态报告，不像围绕 claim 验证 | 当前已有 `Claims under test`，但 Results 仍像综合汇报，图很多 | Results 重排为 claim-based subsections：failure of trivial baselines、projection ablation、operator tradeoff、texture compatibility、diagnostics | Results | P0 |
| 16 | 有些措辞像 draft，不像正式投稿 | 当前仍有 `current draft`、`Draft`、`current paper use`、revision trace comments、candidate 等痕迹 | 正式投稿前必须删除或替换。文档可保留，论文正文不应出现 | 全文清理 | P0 |
| 17 | 指标定义与表格需要更严谨 | 当前 metrics 小节给出 occupancy 6-neighborhood proxy，但 table/figure caption 仍需更明确 | Table 1 caption 标明 component/LCR 口径；raw mesh face components 与 voxel occupancy proxy 分开报告 | Metrics + Tables | P0 |
| 18 | Related Work 和方法定位需要更锋利 | 当前 Related Work 覆盖面足够，但还可以更明确区分 3D editing / structure-controlled generation / procedural / world generation | 保持现有结构，增加每类与本文差异的一句 sharp contrast；不要扩展篇幅 | Related Work | P2 |

## 2. 3.2 / 3.3 / 3.4 方法部分推荐新结构

### 2.1 3.2 Core State and Handles：主状态继续简化

当前方向是正确的：主文只让读者记住三件事。

\[
z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d)
\]

推荐正式写法：

1. \(\mathcal V_d\)：active sparse token support。只承担“当前可递归操作的稀疏支撑”。
2. \(\mathbf F_d\)：generator-native latent features。只说明它是每个 token 上的 shape/material/auxiliary feature，不展开实现细项。
3. \(\mathcal A_d\)：grammar-readable anchors。包括 handles、frontiers、attachment graph、ownership、material handles。

handle 保持：

\[
h_i=(\sigma_i,T_i,\Omega_i,\alpha_i)
\]

其中 \(\sigma_i\) 是类型，\(T_i\) 是 local frame，\(\Omega_i\) 是支持区域或 ownership region，\(\alpha_i\) 是半径、年龄、优先级、材质意图等局部属性。

建议删减或下沉：

- `masks, random seeds, rule traces, diagnostic scores, projection schedules, cached motifs, texture-export metadata` 不进主状态；
- admissible state 中的全部 violation 项不要在 3.2 一次性展开太多；
- `V_mat`, `V_sym`, token budget、renderability 等可作为 executor constraints 或 appendix 完整定义。

推荐主文重点句：

> The recursive state is a sparse latent support with features and grammar-readable anchors; all other masks, traces, caches, and texture metadata are executor bookkeeping.

### 2.2 3.3 Rule Templates：用规则模板替代大 tuple

当前大 tuple 已被替换，这是最重要的完成项之一。推荐保持三层：

第一层：语言对象

\[
\mathcal L=(\text{typed handles},\text{rule templates},\text{realization operators})
\]

第二层：核心 rule template

\[
\rho:\ h_i\mapsto
\{(\sigma_j,\tau_j,\Omega_j,m_j,\kappa_j,\pi_j,\eta_j)\}_{j=1}^{k}
\]

第三层：rule family 表。

建议主文表格只保留最能支撑论文 claim 的规则族：

| Rule family | 是否主文保留 | 理由 |
|---|---|---|
| grow | 保留 | vine/root/tree conservative evidence 最强 |
| branch | 保留 | tree/bush recursion 的核心 |
| attach | 保留但降调 | DLA/porous 是 stress test，证据不稳 |
| copy | 保留 | portal/ornament/hard-surface breadth |
| refine | 保留 | 支撑 effective resolution |
| material | 可保留一行 | 只作 metadata/export compatibility |
| cache | 转 appendix | 当前没有足够主实验支撑 |
| split/extrude | 可转 appendix | architecture/shape grammar breadth，不是核心证据 |

rule template 后应立即解释 semantic difference：

> A proposal is not active because it is locally plausible; it becomes active only if it remains projectable and attached for the next recursion step.

这句话比列更多 rule family 更重要。

### 2.3 3.4 Projection-Stabilized Execution：主公式压缩，细节下沉

主公式应保持当前简洁形式：

\[
z_{d+1}=
\operatorname{Enc}_{\theta}
\left[
\Pi_{\lambda_d}
\left(
\operatorname{Dec}_{\theta}
\left(
\mathcal T_{\theta}(z_d;\mathcal R_d,y)
\right)
\right)
\right].
\]

其中：

\[
\mathcal R_d=\operatorname{SelectRules}(z_d,\mathcal G)
\]

\[
\tilde z_{d+1}=\mathcal M(z_d,\operatorname{Prop}_{\mathcal R_d}(z_d))
\]

\[
\bar z_{d+1}=\mathcal N_\theta(\tilde z_{d+1};m_d,y)
\]

\[
x_{d+1}=\operatorname{Dec}_\theta(\bar z_{d+1})
\]

\[
x_{d+1}^{\star}=\Pi_{\lambda_d}(x_{d+1},\mathcal A_d)
\]

\[
z_{d+1}=\operatorname{Enc}_\theta(x_{d+1}^{\star})
\]

推荐主文写成两个算法框：

**Algorithm 1: Recursive Sparse-Latent Program Execution**

1. initialize \(z_0\) and root handles;
2. select active handles and rules;
3. instantiate sparse proposals;
4. reject proposals outside projectable domain unless bridge-certified;
5. masked merge support/features/material handles;
6. optional masked local naturalization;
7. decode, project, re-encode;
8. update handles, frontiers, caches, diagnostics.

**Algorithm 2: Projection Operator**

1. build mesh / voxel / occupancy connectivity graph;
2. identify root-attached components;
3. score components by mass, distance, bridge cost, renderability, material seam, rule ownership;
4. keep root-attached and accepted bridge-certified components;
5. prune or inactivate orphan components and orphan handles;
6. optionally weld / close gaps / remesh / insert bridges;
7. validate token budget and frontier connectedness;
8. return \(x^\star\), updated anchors, and diagnostics for re-encoding.

主文不应把所有细节放在一个长公式里；长公式现在已经解决，后续风险是“解释段落又变得太长”。建议把 projection objective、bridge path set、stability sketch 放进 appendix 或压成短段。

## 3. 哪些已经完成

### 3.1 已完成且应保留的核心修改

- 摘要与引言已经转向 generation-model-native recursive language。
- 引言已经形成 failure-driven motivation：2D scaffold、direct sparse edit、global flow repair、final-only cleanup。
- 3.2 已用最小 sparse-latent state 替代八元组。
- 3.3 已用 rule template 替代 grammar tuple。
- 3.4 已压缩主递归公式。
- masked flow naturalization 已具体化。
- projection 已被放进 recursive transition，而不是 post-hoc cleanup。
- material / texture export 已在方法中解释为 selected projected meshes 的导出兼容性。
- recursive effective resolution 已出现。
- experiments 已开始用 claims under test 收束，不再完全是日志式结果堆叠。

### 3.2 已完成但仍需语言打磨

- 旧版本注释仍保留在 `main.tex` 中，正式稿必须删除。
- `current draft`、`current paper use`、`Draft Trellis2...`、`candidate`、`bug fixed`、`smoke` 等措辞要替换成正式论文语言。
- Figure caption 中仍有较多“当前状态说明”，需要变成 claim-driven caption。
- Results 中 caveat 过多，需区分主文 caveat 与 appendix diagnostics。

## 4. 哪些需要继续改 `main.tex`

下列项建议后续真正修改正文，而不是只放文档：

1. **正式化算法框**  
   将当前 3.4 的 enumerate 改为 Algorithm 1；projection 步骤拆成 Algorithm 2。

2. **清理 revision trace 注释**  
   当前 `main.tex` 保留大量 “Previous ... kept for revision trace”。这些对内部协作有用，但不能进入投稿稿。

3. **重排 Results 为 claim-based subsections**  
   建议结构：
   - 5.1 Trivial generator use fails to preserve recursive topology
   - 5.2 Per-depth projection stabilizes conservative recursive growth
   - 5.3 Rule families reveal a stability-expression tradeoff
   - 5.4 Selected projected meshes support Trellis2 texture/PBR export
   - 5.5 Diagnostics and failure boundaries

4. **指标口径写清楚**  
   每张表和关键图都明确：component 是 voxel occupancy 6N proxy、raw mesh face connectivity、welded mesh component，还是 GLB import/render diagnostic。

5. **精简主图**  
   主文只保留服务核心 claim 的图；大 gallery 和弱 showcase 转 supplement。

6. **降调 finite/infinite 递归措辞**  
   标题或小节名不要暗示已经实现无限 mesh。建议把 `Recursive Effective Resolution and Infinite Refinement` 改成 `Recursive Effective Resolution under Finite-Depth Refinement`。

7. **texture/PBR 边界更明确**  
   Table 2 和文字都要说 texture export success 不等于 topology clean，也不等于 material recursion solved。

## 5. 哪些适合转 Appendix / Supplement

| 内容 | 推荐去向 | 原因 |
|---|---|---|
| IFS / L-system / space-colonization / DLA / CGA 的完整限制实例推导 | Appendix | 有定位价值，但打断方法主线；过宽会引发 reviewer 追问 |
| Symmetry approximate equivariance 公式 | Appendix 或 Discussion | 当前没有强实验验证，不适合当主贡献 |
| Cache / visible-window infinite recursion | Appendix / Future Work | 当前属于语义扩展，不是实验证明 |
| Projection objective 的完整优化形式与 bridge path set | Appendix | 主文保留算法，细节推导下沉 |
| `result_matrix_mesh_20260509.png` 大矩阵 | Supplement | 像状态总览，不适合作主 claim 图 |
| `depth_parameter_mesh_showcase_20260509.png` | Supplement | 控制 gallery，有用但不集中 |
| `coral_density_param_showcase_20260509.png` | Supplement | 连通性好但参数效应弱，不适合作主图 |
| DLA radial / echo / bridge-ablation 弱结果 | Failure appendix / diagnostics | 重要边界，但不应冲淡主贡献 |
| pyrite mesh component caveat、raw face fragmentation 细表 | Appendix diagnostics | 必须透明，但主文只需短 caveat |
| traditional baseline texture diagnostic 完整图组 | 主文小图 + Supplement 完整版 | 主文用来说明 texture alone is insufficient；完整协议放补充 |

## 6. 哪些必须保留但要降调

### 6.1 Texture / PBR

必须保留，因为 reviewer 明确要求说明材质管线，且 Table 2 / textured strips 是资产导出能力的重要证据。

但要降调为：

> Trellis2 texture/PBR export is compatible with selected projected meshes.

不能写成：

> The method solves recursive material generation.

应持续区分：

- geometry recursion；
- material handle metadata；
- selected projected mesh texture export；
- GLB import/render success；
- raw mesh / face topology caveat。

### 6.2 DLA / Coral / Porous

必须保留为 stress test 和边界案例，因为它说明 projection/bridge 的困难，也支持“不是所有 rule family 都已解决”的诚实边界。

但主文不能把它写成 solved DLA。推荐措辞：

> DLA-inspired and coral-like frontier programs serve as stress tests for attachment and bridge policies; conservative connected scaffold variants are positive, while bridge-ablation variants remain partial or negative.

### 6.3 Crystal / Bismuth / Pyrite

可以保留为 non-tree breadth，但必须避免物理晶体生长 claim。

推荐：

> bismuth-like connected scaffold

避免：

> physical crystallization, facet-accurate growth, face-welded topology proof

### 6.4 Effective Resolution

必须保留，因为它是比“稳定递归”更强的潜在贡献点。

但要写成 finite-depth / active-window / local refinement，不要写成已经实现无限分辨率或无限 mesh。

### 6.5 Classical Systems as Limits

必须保留一点，因为它帮助 reviewer 理解 PS-RSLG 与传统 procedural systems 的关系。

但主文只保留一句：

> Several classical procedural systems are recovered as restricted rule families when learned naturalization, projection, or generator-native features are disabled.

详细推导转 appendix。

## 7. 最重要的结论

1. `main.tex` 已经完成 reviewer 对 3.2/3.3/3.4 的核心结构性要求：最小状态、规则模板、简洁递归公式、masked flow、per-depth projection 都已经在正文中出现。
2. 下一轮正文修改的关键不是再发明新方法，而是把现有方法表述正式化：Algorithm 1/2、claim-based Results、指标定义、图表精简、删除 draft 痕迹。
3. 主文最稳 claim 只能是：per-depth projection stabilizes finite-depth recursive sparse-latent programs under voxelized connected-support metrics。
4. Texture/PBR、DLA/coral、crystal、symmetry/cache、infinite recursion 都有价值，但必须作为 selected compatibility、stress test、inspired scaffold、appendix semantics 或 future extension 降调处理。
5. 如果要让论文从“有说服力的研究状态报告”变成“可审稿论文”，最缺的是 matched same-root tree/root/vine baseline matrix，以及更标准的 claim-driven figure/table organization。

