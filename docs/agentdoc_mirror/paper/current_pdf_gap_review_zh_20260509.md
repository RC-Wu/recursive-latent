# 当前 PDF gap review（中文，2026-05-09）

审阅对象：`paper_siga/main.pdf` 与其当前源文件 `paper_siga/main.tex`。  
审阅边界：仅做 paper gap review / draft organization；不修改 `paper_siga/main.tex`，不修改 figures。  
总体判断：当前 PDF 已经从“工程状态汇总”推进到“PS-SLG/PS-RSLG 方法论文骨架”，其中 grammar formalism 和 projection-stabilized recursion 的主线已经初步写入主文；但它还没有达到 SIGGRAPH Asia 方法论文的可投稿形态。最主要缺口不是没有材料，而是现有 formal doc、metric protocol、5 月 9 日新图和视频原型还没有被组织成严格的 claim -> mechanism -> evidence 链。

## 1. 证据基线

本 review 依据以下已存在文件：

- 当前论文：`paper_siga/main.tex`，`paper_siga/main.pdf`
- 形式化方法：`docs/method/formal_sparse_latent_grammar_v2_zh_20260509.md`
- 评测协议：`docs/evaluation/space_competition_metric_protocol_zh_20260509.md`
- 当前主文改写计划：`docs/paper/main_tex_rewrite_plan_after_public_guides_zh_20260509.md`
- 新视觉资产：
  - `paper_siga/figures/result_matrix_mesh_20260509.png`，1708 x 2054，36 个现有 mesh render
  - `paper_siga/figures/teaser_candidate_layout_v2_20260509.png`，3200 x 1700，true Trellis2 GLB panels + PBR fallback zoom strip
  - `paper_siga/figures/vine_zoom_in_multiscale_20260509.png`，3900 x 1450，Blender/Cycles mesh zoom-in
  - `visuals/demo_video_20260509/recursive_growth_demo_preview.mp4`，已存在，但按状态文档应视为 prototype

当前 `main.tex` 已引用的主要图仍是：

- `figures/head_figure_textured_non_tree_draft_20260508.png`
- `figures/method_system_grammar_polished_20260508.pdf`
- `figures/projection_depth_curves_20260508.pdf`
- `figures/space_competition_depth_curves_tokens_20260508.pdf`
- `figures/space_colonization_blender_contact_sheet.png`

这意味着 2026-05-09 的 result matrix、teaser candidate、vine zoom-in 和 demo video 还没有进入当前 PDF 的主文叙事。

## 2. 六项需求完成度判定

| 需求 | 当前状态 | 严格判定 | 下一步动作 |
|---|---|---|---|
| 1. 更强 grammar formalism | `main.tex` 已有 problem setting、state tuple、grammar tuple、rule schema、operational semantics、classical limits、projection proposition；支撑文档 `formal_sparse_latent_grammar_v2` 更完整。 | **部分完成，接近主文可用**。形式化已写入，但缺 Algorithm box、coverage table、符号压缩和主文/附录分层。 | 保留中心公式；新增 Algorithm 1；把 IFS/L-system/SC/DLA/finite shape grammar 覆盖写成一张表；长证明移至 appendix。 |
| 2. baseline / metric protocol | `main.tex` 已承认 occupancy 6-neighborhood proxy 比 raw face connectivity 更公平，并已有 projection ablation table；`space_competition_metric_protocol` 给出 skeleton、mesh proxy、projection ablation 三层指标和具体表。 | **部分完成**。协议已经在文档中定型，但当前 PDF 缺 protocol table、SC skeleton metric table、mesh proxy summary table，也未接入 2026-05-09 metric figure。 | 在 Experiments 开头先写 protocol；主表使用 occupancy comps/LCR；SC 用 skeleton coverage/tip/branch 指标；raw face components 降级为 diagnostic。 |
| 3. SDE / flow / cache / infinite recursion | `main.tex` 已把 frozen sampler 写成 masked local prior，包含 SDE/ODE clamp；也写了 cache semantics 和 finite-depth scope；`formal_sparse_latent_grammar_v2` 对 material/cache/visible-window/infinite recursion 更完整。 | **部分完成，但证据不足**。形式语义可写，不能作为实验证明。当前只能主张 finite-depth recursive assets；cache/LOD/infinite recursion 是 extension 或 appendix proposition。 | 主文保留 masked local naturalization 的谨慎表述；cache/LOD 放短段或 appendix；删除任何“真实无限 mesh/world-scale generation”语气。 |
| 4. head figure / teaser | 已有 `teaser_candidate_layout_v2_20260509.png`、`result_matrix_mesh_20260509.png`、`vine_zoom_in_multiscale_20260509.png`；但当前 PDF 仍使用 2026-05-08 旧 head draft。 | **缺失于当前 PDF**。资产已准备，但没有替换进入 paper；teaser 当前含 true GLB 与 PBR fallback，caption 必须明确区分。 | Fig. 1 改用新 teaser 或更克制的 neutral/PBR + true GLB inset；Fig. 5 接入 result matrix；vine zoom-in 可作为局部几何证据或 teaser 底部证据条。 |
| 5. formal paper outline / writing | 当前 PDF 有标准 section skeleton：Introduction、Related Work、Method、Experiments、Results、Discussion；改写计划文档已经给出更清晰的 SIGA 结构。 | **部分完成**。当前主文仍像 draft skeleton，Results 偏状态汇总，Experiments 缺 question-driven protocol，figure/table 顺序不够像正式方法论文。 | 重排为 problem -> method -> protocol -> ablation -> breadth -> texture compatibility -> limitations；每个强句都绑定一个 figure/table。 |
| 6. execution constraints | 本 review 范围要求只写 doc，不改 `main.tex` 或 figures。当前仓库路径下没有 `.git` 元数据，不能依赖 git status 判定他人修改；但文件系统检查显示目标支撑文件存在。 | **本次任务可满足**。需要继续避免覆盖别人对 `main.tex`、figures、assets 的编辑。 | 本轮只输出 `docs/paper/current_pdf_gap_review_zh_20260509.md`；下一轮若改 paper，先重新读取 `main.tex` 和目标图路径。 |

## 3. 当前 PDF 中已经可保留的内容

### 3.1 Method formalism 的主线已经成立

当前 `main.tex` 已经把核心方法从工程流水线提升为 formal grammar system：

- 定义了 finite-depth recursive asset synthesis：`S_{d+1} ~ T_{G,theta,d}`。
- 定义了 typed sparse-latent state：`S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d,K_d)`。
- 定义了 grammar tuple：包含 symbols、transforms、rules、scheduler、constraints、masked naturalization、decoder、encoder、projection、cache、observable、score。
- 写入了中心 transition：
  - proposal
  - masked merge
  - constraints / competition
  - optional masked shape/material naturalization
  - decode
  - projection
  - re-encode
  - cache update
- 已经明确 projection is inside recursion，不是 final cleanup。

这些内容应保留，但需要压缩。当前 Method 占比偏大，正式论文应把部分证明和长符号定义移到 appendix。

### 3.2 关键 claim 的边界比旧稿更安全

当前 PDF 已经避免了几个危险 overclaim：

- 没有把方法称为 universal infinite generator。
- 明确写了 finite-depth recursive assets。
- 承认 global flow repair 会 overwrite recursive scaffold。
- 承认 texture export 技术可行但 material quality category-dependent。
- 对 exact equivariance 使用 approximate metric / bound，而不是保证。

这些边界应继续保持。

### 3.3 Projection ablation 是当前最强实验证据

当前主文 table 已有四行 matched projection ablation：

- `vine compete d3`
- `tree compete d3`
- `vine compete-fork d3`
- `tree compete-fork d3`

其中 conservative `compete` 支持“per-depth projection 能抑制 fragment accumulation 并保持 dominant component”的主张；`compete_fork` 更适合作为 stability-expression boundary，而不是正面成功。

## 4. 当前 PDF 的主要缺口

### 4.1 Abstract 和 contributions 仍偏宽

当前 abstract 写到 “supports depth-5 vine/root growth, and extends to branching, porous, ornamental, architectural, and hard-surface transform-copy programs”。这句话方向可以保留，但需要降级：

- “supports selected depth-5 conservative competition vine/root cases”
- “evaluates branching, porous, ornamental, architectural, and hard-surface programs as breadth and stress tests”
- “success varies by operator and category”

不要让读者误解为所有类别都达到同等质量或同一评测协议。

### 4.2 当前 PDF 没有显式 Algorithm 1

Method 有中心公式，但正式图形学论文需要一个可读 algorithm box。建议加入：

**Algorithm 1: Projection-Stabilized Sparse-Latent Recursive Grammar**

输入：root mesh `x0`、frozen generator `theta`、grammar `G`、depth `D`、projection schedule `lambda_d`、optional condition `y`。  
步骤：

1. Encode root mesh into sparse state `S0`。
2. For each depth：
   - schedule active rules
   - propose sparse patches
   - masked merge
   - apply competition / occupancy / attachment / token constraints
   - optional masked local naturalization
   - decode candidate mesh
   - project to admissible state
   - re-encode
   - update cache/history/diagnostics
3. Export neutral renders、metrics、optional textured GLB。

这样可以把长公式变成可执行流程，降低审稿人理解成本。

### 4.3 Classical systems as limits 缺主文表

当前主文有一段文字覆盖 IFS、L-system、space colonization、DLA、finite shape grammar，但缺少表格。建议新增 Table 1：

| Classical system | PS-SLG restriction | State/rule mapping | 当前用途 |
|---|---|---|---|
| L-system | `U_d in Sigma*`，同步重写 | symbol string -> turtle/frame support | branching motivation / baseline |
| IFS | transform-copy + union merge，identity sampler/projection | `C_{d+1}=union_i T_i(C_d)` | portal / scale-down / self-similar stress |
| Space colonization | tips + attractors + occupancy exclusion | attractor assignment -> averaged direction | main conservative growth / structural baseline |
| DLA/frontier | frontier hitting kernel | cluster union with exposed cell | porous / coral stress |
| Finite shape/CGA grammar | typed face/tile/portal + split/extrude/repeat | local symbol graph rewrite | architecture / portal / ornament |

必加 caveat：coverage 是 finite-step operational equivalence 或 quantized approximation，不是 visual superiority，也不是覆盖所有 shape grammar。

### 4.4 Baseline protocol 尚未成为论文结构

当前 `main.tex` 的 Experiments 只有 Tasks/Baselines/Metrics 三个短小段落，缺少正式 protocol。应把 `docs/evaluation/space_competition_metric_protocol_zh_20260509.md` 中的内容合并成主文：

- traditional SC 的公平主指标是 skeleton coverage、tips、branch nodes、total length。
- generated mesh 的公平主指标是 occupancy 6-neighborhood component count 和 largest occupancy component ratio。
- raw face connectivity 和 welded components 是 diagnostics。
- `accepted proposal ratio`、`collision violation rate`、`projection survival ratio` 当前缺 trace，不应写成已完成主结果。

当前最安全主表：

1. SC skeleton metrics table。
2. Mesh occupancy proxy summary。
3. Projection ablation table。

### 4.5 新图没有进入当前 PDF

当前 PDF 最大视觉风险是 Fig. 1 仍使用旧 `head_figure_textured_non_tree_draft_20260508.png`。5 月 9 日已有更清晰资产：

- `teaser_candidate_layout_v2_20260509.png`：更像 head figure，但包含 true Trellis2 GLB 和 PBR fallback 两类证据，caption 必须显式说明。
- `result_matrix_mesh_20260509.png`：可作为 qualitative breadth matrix，但不能写成 “36 Trellis2 textured results”；应写 “36 existing mesh renders, separated by protocol”。
- `vine_zoom_in_multiscale_20260509.png`：可支撑 local recursive geometry，但不是 Trellis2 texture result。

推荐改法：

- Fig. 1：新 teaser 或经过重排的 neutral/PBR hero + true GLB inset。
- Fig. 5：result matrix，caption 明确 green/blue/gray 协议。
- Fig. 6 或 appendix：vine zoom-in，用作 local geometry evidence。

### 4.6 Texture/PBR 还只能做 compatibility，不是主贡献

当前材料中 true Trellis2 GLB route 已经存在，且 matrix 里有约 15 个 true textured GLB render。但视觉 QA 明确指出 holes、thin sheets、white speckles、semantic mismatch、dirty material 等问题。

主文写法应是：

- selected projected meshes can be passed through Trellis2 textured GLB export
- texture/PBR compatibility is evaluated separately
- material quality remains category-dependent

不要写：

- texture quality solved
- 36 textured Trellis2 results
- porous/crystal/animal categories are fully successful

### 4.7 Demo video 是 prototype，不能作为论文核心证据

`visuals/demo_video_20260509/recursive_growth_demo_preview.mp4` 存在；`docs/visuals/blender_demo_video_status_zh_20260509.md` 说明它复用已有 projected/pruned stage mesh，当前定位是 prototype。可在 supplementary planning 中提及，但当前不应作为主文 claim：

- 它证明“可以视频化呈现递归生长过程”。
- 它不证明连续局部增长、空间竞争可视化、projection pruning 可视化或最终展示级视频质量。

## 5. 下一版论文组织建议

### 5.1 Section outline

建议下一版 `main.tex` 按以下结构重写：

1. **Abstract**
   - 7 句以内：problem、gap、method、projection mechanism、main quantitative result、breadth/stress tests、texture compatibility caveat。

2. **Introduction**
   - P1：recursive assets 的图形学动机。
   - P2：native sparse 3D generator 的机会与 mismatch。
   - P3：naive bridges 的失败模式和设计原则。
   - P4：PS-SLG/PS-RSLG 方法概述。
   - P5：contributions + evidence boundaries。

3. **Related Work**
   - Classical recursive procedural modeling。
   - Neural 3D generation and sparse latent states。
   - Training-free 3D editing。
   - Structure control and world-scale composition。
   - Evaluation of recursive assets。

4. **Method**
   - Problem setting。
   - Typed sparse-latent state。
   - Grammar tuple and rule schema。
   - Algorithm 1。
   - Classical systems as restricted instances。
   - Sparse competition and masked local naturalization。
   - Projection-stabilized recursion proposition。
   - Cache / symmetry / finite-depth scope as extension paragraph。

5. **Experimental Protocol**
   - Asset families and operators。
   - Baselines。
   - Metrics。
   - Rendering / texture protocol separation。

6. **Results**
   - Projection ablation first。
   - Stability-expression tradeoff。
   - Traditional SC comparison。
   - Qualitative mesh matrix。
   - Texture/PBR compatibility。

7. **Discussion and Limitations**
   - Finite-depth only。
   - No topology-preserving flow guarantee。
   - Texture quality category-dependent。
   - Cache/LOD/infinite recursion not experimentally complete。
   - Trace metrics missing。

8. **Appendix**
   - Coverage proof sketches。
   - Symmetry/cache bounds。
   - Raw/welded/occupancy metric diagnostics。
   - Additional visual QA and failed cases。

### 5.2 Figure and table list

| Order | Item | Source candidate | Role | Required caveat |
|---|---|---|---|---|
| Fig. 1 | Teaser / head figure | `teaser_candidate_layout_v2_20260509.png` or revised version | First visual signal | distinguish true Trellis2 GLB vs PBR fallback |
| Fig. 2 | Method overview | `method_system_grammar_polished_20260508.pdf` | Formal pipeline | caption should match Algorithm 1 |
| Table 1 | Classical systems coverage | new table from formal doc | Theory bridge | finite-step restricted instances only |
| Fig. 3 | Projection depth curves | `projection_depth_curves_20260508.pdf` | Stability evidence | specify exact connectivity metric |
| Table 2 | Projection ablation | current table + protocol wording | Main quantitative evidence | compete rows are strong; fork rows are boundary |
| Fig. 4 | Operator growth curves | `space_competition_depth_curves_tokens_20260508.pdf` | Stability-expression tradeoff | token growth is not visual quality |
| Fig. 5 | Result matrix | `result_matrix_mesh_20260509.png` | Qualitative breadth | not all true textured GLB |
| Fig. 6 | Traditional SC baseline | `space_colonization_blender_contact_sheet.png` | Structural baseline | SC judged by skeleton metrics, not raw face comps |
| Fig. 7 / appendix | Vine zoom-in | `vine_zoom_in_multiscale_20260509.png` | Local geometry evidence | programmatic PBR mesh render, not Trellis2 texture |
| Table 3 | SC skeleton metrics | from metric protocol CSV/table | Baseline fairness | coverage/tips/branches only |
| Table 4 | Mesh proxy metrics | from metric protocol | Mesh connectivity | occupancy 6n proxy, not topology proof |
| Table 5 | Texture/PBR QA | current texture QA rows | Export compatibility | category-dependent material quality |

### 5.3 Claim-evidence matrix

| Claim | Mechanism | Current evidence | Status | Safe wording |
|---|---|---|---|---|
| PS-SLG defines recursive asset generation over sparse native 3D states. | Typed state, grammar tuple, rule schema, central transition. | `main.tex` Method + `formal_sparse_latent_grammar_v2_zh_20260509.md` | **Strong formal claim** | “We formulate...” |
| Classical procedural systems are included as restricted instances. | Disable or restrict learned sampler/projection/material terms; choose interpretation map. | Formal doc proof sketches; current main text paragraph. | **Formal but needs table** | “Finite-step instances can be recovered under restrictions.” |
| Per-depth projection is stronger than final-only cleanup for conservative competition cases. | Decode/project/re-encode before next rule; prevents fragments entering frontier/history/cache. | Projection ablation table: vine/tree compete rows. | **Strongest empirical claim** | “On matched conservative competition cases...” |
| Fork/side/radial operators increase expression but reduce stability. | More aggressive proposals consume support and create fragments. | Fork ablation rows and operator curves. | **Supported as boundary** | “These expose the stability-expression boundary.” |
| Traditional space colonization is a strong structural baseline. | Explicit tips/attractors/skeleton coverage. | Metric protocol: coverage near 0.97; SC render contact sheet. | **Supported** | “SC is a structural scaffold baseline, not an asset-quality baseline.” |
| Occupancy 6n LCR is the primary mesh connectivity proxy. | Voxelized vertex occupancy avoids unfair raw face connectivity. | Metric protocol and current Metrics section. | **Supported with caveat** | “We report a voxel-occupancy proxy, not topological connectivity.” |
| Texture export is compatible with selected projected meshes. | Trellis2 textured GLB export/import/render route. | Texture QA table, result matrix green panels, teaser v2 panels. | **Compatibility only** | “Selected projected meshes can be exported as textured GLBs.” |
| Material recursion is solved per depth. | Would require material state update at every recursive step. | Formal semantics only; current experiments mostly final texture export. | **Missing** | Do not claim; call future extension. |
| Infinite recursion / zoom is supported. | Would require contractive proof or visible-window cache/LOD streaming evidence. | Formal discussion and cache/LOD prototype references only. | **Missing as result** | “Logical extension under bounded visible-window/cache assumptions.” |
| Demo video proves recursive growth dynamics. | Blender imports stages and animates appearance/scale. | `recursive_growth_demo_preview.mp4` prototype. | **Partial prototype** | “A supplementary visualization prototype exists.” |

## 6. Action list for next draft

1. Replace or demote the current old head figure; use the 2026-05-09 teaser only with strict caption labels.
2. Add Algorithm 1 immediately after the central transition formula.
3. Add Table 1 for classical procedural systems as restricted PS-SLG instances.
4. Rewrite Experiments into a protocol-first section.
5. Add SC skeleton metric table and mesh occupancy proxy table from the metric protocol.
6. Recaption projection figures with the exact metric names used.
7. Add `result_matrix_mesh_20260509.png` as qualitative breadth, not as all-textured success.
8. Add texture/PBR QA table with `paper use` labels: head candidate, matrix, appendix, diagnostic.
9. Move cache/LOD/infinite recursion to limitations/appendix unless new evidence is added.
10. Keep claims tightly scoped to finite-depth, training-free recursive asset generation.

## 7. Bottom-line recommendation

下一版不要再扩大 claim。论文最稳的主张应是：

> PS-SLG / PS-RSLG is a training-free formal grammar interface over frozen sparse native-3D states. Its strongest demonstrated mechanism is per-depth decode/project/re-encode, which stabilizes selected conservative recursive growth cases better than direct recursion or final-only cleanup. Classical procedural systems provide the restricted formal baseline; texture/PBR export and cache/LOD recursion are compatible extensions, not yet primary solved results.

如果下一版严格围绕这个 claim 写，当前材料已经足够形成一篇清晰的 method-paper draft。若继续把 head figure、texture、infinite recursion、cache、SDE repair、all-category breadth 同时写成主贡献，审稿风险会显著上升。
