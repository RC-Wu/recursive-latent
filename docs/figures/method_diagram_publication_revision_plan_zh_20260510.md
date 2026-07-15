# Method Figure Publication Revision Plan（2026-05-10）

本文件是当前方法图任务的上下文压缩恢复点。目标不是继续堆示意图，而是只保留能支撑正文 claim 的发表级图。

## 输入上下文

- 官方 OpenAI Codex 历史已定位并只读解析：`/Users/fanta/.codex/sessions/2026/05/09/rollout-2026-05-09T22-18-20-019e0d1a-7c55-70a1-aa1a-64cf832fcaa4.jsonl`，标题为 `[R-SLG]示意图`。
- 旧草稿目录：`paper_siga/figures/method_diagram_drafts_20260510/`。
- 旧设计文档：`docs/figures/method_diagram_design_plan_zh_20260510.md`。
- AgentDoc 图计划：`/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_method_figures_plan_20260510.md`。

两个只读 reviewer 的共识：

1. Figure A/B 的叙事方向正确，但目前只是结构草稿，仍像 slide/dashboard。
2. Trellis2 必须画成 frozen sparse substrate / codec / local realization prior，不是本文贡献主体。
3. Projection 必须画在 PS-RSLG loop 内部，不应被画成 Trellis2 decoder 的一部分，也不应像最终 cleanup。
4. 真实 mesh/PBR inset 要作为视觉锚点，但 caption 必须声明它们是 selected projected/export examples，不承担拓扑证明。
5. 图内符号必须和正文统一：主状态使用 `z_d=(V_d,F_d,A_d)`，不要混回旧的 `S_d=(V,F,A,M,C)`。

## 主文优先图

### Figure B：Preliminaries / Frozen Trellis2 Sparse Substrate

放置位置：`main.tex` 的 `\subsection{Sparse Generator State}` 末尾，替换现有 sparse voxel / Trellis-style generator pipeline TODO。

输出文件：

- `paper_siga/figures/method_trellis2_substrate_prelim_20260510.pdf`
- `paper_siga/figures/method_trellis2_substrate_prelim_20260510.png`
- `paper_siga/figures/method_trellis2_substrate_prelim_20260510.svg`

必须支撑的 claim：

- 本文使用 frozen sparse generator 暴露的接口：condition/root、O-Voxel support、Shape-SLAT features、masked/local sampler、decoder/re-encoder、optional texture/PBR export。
- 它是 Preliminaries 图，用来解释后文 `Enc_\theta`、`Dec_\theta`、`\mathcal N_\theta`、`Tex_\theta` 和 `z=(V,F)`。

禁止 claim：

- 不声称这是 Trellis2 官方完整架构。
- 不声称 Trellis2 原生保证递归、连通性、handle validity 或 topology preservation。
- 不把 texture/PBR export 写成结构证明。
- 不把 projection 放进 Trellis2 decoder。

### Figure A：Method / PS-RSLG Main Overview

放置位置：替换 `fig:method-overview` 当前旧图。

输出文件：

- `paper_siga/figures/method_ps_rslg_overview_publication_20260510.pdf`
- `paper_siga/figures/method_ps_rslg_overview_publication_20260510.png`
- `paper_siga/figures/method_ps_rslg_overview_publication_20260510.svg`

必须支撑的 claim：

- PS-RSLG 是 grammar-owned recursive state transition。
- Grammar 选择 handles、产生 rules/proposals/masks。
- Frozen Trellis2 substrate 只提供 sparse codec、masked local realization、decode/re-encode 和 selected export。
- Projection 在每个 recursive transition 内部，输出 admissible next state 后才允许下一层规则读取。

禁止 claim：

- 不声称所有 rule family 都稳定。
- 不声称 sparse-latent execution 已全面优于 mesh-space 或 object-latent。
- 不把 transform-copy 写成 strict equivariance。
- 不把 DLA/coral/crystal 写成物理模拟。
- 不把右侧 selected outputs 写成 category-wide success 或 clean topology。

## 当前去留

- 旧 `figure_A_main_method_overview` 和 `figure_A2_two_layer_architecture` 保留为结构草稿，不直接进主文。
- 旧 Figure C projection gate 是必要下一优先级，但要谨慎：当前实现以 conservative prune-only active-state policy 为主，图中不能暗示未完成的 model-proposed connector ablation 已闭合。
- 旧 Figure D/E/F/G 可作为后续 subsection/supplement 的候选，不在本轮强行放入主文。

## 本轮实现计划

1. 写新脚本 `scripts/figures/compose_method_publication_diagrams_20260510.py`，只生成 A/B 两张发表级候选和 contact sheet。
2. A/B 都输出 SVG/PDF/PNG；图形框、箭头、文字为 vector，真实 mesh inset 为 raster。
3. 更新 `paper_siga/main.tex`：
   - 在 Preliminaries 的 `Sparse Generator State` 插入 Figure B；
   - Method 开头替换 Figure A；
   - caption 明确 frozen substrate / selected export 的 claim boundary。
4. 编译 LaTeX，确认无 undefined refs/cites。
5. 将 `paper_siga` 中实际引用的新图和 `main.tex` commit/push 到 Overleaf。

## 进度

- 2026-05-10 16:33 CST：完成官方历史抽取和 main.tex 图位审查；确认 Figure B 插在 `Sparse Generator State`，Figure A 替换 `fig:method-overview`。开始生成 publication 版 A/B。
- 2026-05-10 18:22 CST：A/B 已生成并插入正文，`paper_siga` 已编译通过并与 Overleaf `master` 持平。下一优先级切到 Figure C：`Model-Native Projection` 机制图。

## Figure C：Projection / Admissibility Gate

放置位置：`paper_siga/main.tex` 的 `Model-Native Projection` 小节内，紧跟 projection argmin 定义与 conservative prune-only active-state policy 解释之后，放在 `Why final-only cleanup is insufficient` 之前。

输出文件：

- `paper_siga/figures/method_projection_admissibility_gate_20260510.pdf`
- `paper_siga/figures/method_projection_admissibility_gate_20260510.png`
- `paper_siga/figures/method_projection_admissibility_gate_20260510.svg`

必须支撑的 claim：

- Projection 是 recursive transition 内部的 admissibility-constrained state selection，不是终端 mesh cleanup。
- 当前主实现是 conservative prune-only active-state policy：root-attached decoded support 和 certified connector regions 才能 re-encode 为 active state。
- Detached/orphan components 被删除或降为 inactive descriptors，不能成为下一层 parent/frontier/cache motif。
- 输出符号统一为 `z_{d+1}=(V,F,A)`，并通过 `Enc_\theta(projected asset)` 回到下一层 rule selection。

图内元素：

1. 左侧：`decoded candidate at depth d`，显示 root-attached active support、active handles/frontiers、红色 detached/orphan support。
2. 中间：`admissibility projection gate`，三项检查为 root reachability、orphan handle deactivation/pruning、token/budget/renderability admissibility。
3. 中下：`inactive descriptor / deleted` 分支，说明 detached components cannot fire later rules。
4. 弱化可选分支：`certified connector mask`，标注为 optional rule-proposed mask, not default repair。
5. 右侧：`z_{d+1}=Enc_\theta(x^\star)`，只保留 root-attached active state 和 surviving handles，并回流到 `next rule selection`。

Caption 边界：

- 不写 topology repair / mesh fix / geometry restoration。
- 不暗示 model-proposed connector ablation 已完成。
- 不把 projection 画成或写成 Trellis2 decoder 的一部分。
- 不声称 guarantee all rule families；aggressive fork/radial/DLA-like 仍属于 stability-expression boundary。

## 2026-05-10 19:00 CST 更新：A/B/C/E 正文方法图状态

本轮继续接手 `[R-SLG]示意图` 官方 Codex 历史之后，对方法图做了两次 Overleaf 同步：

1. `40d7f74 Add masked naturalization mechanism figure`
   - 新增 `paper_siga/figures/method_masked_local_naturalization_mechanism_20260510.pdf`。
   - 插入 `main.tex` 的 `Masked Local Naturalization` 小节，label 为 `fig:method-masked-naturalization`。
   - 同时将 algorithm 里过长的 comment 缩为 `admission gates`，避免 ACM 单栏 algorithm 过宽。
2. `9aed2ef Tighten method figure typography`
   - 对 A/B/C/E 四张方法图统一降低图内大标题视觉重量，减少 slide/poster 感。
   - 本地编译通过并已 push 到 Overleaf；`overleaf/master...HEAD = 0 0`。

当前正文方法图：

- Figure B / Preliminaries：`method_trellis2_substrate_prelim_20260510.pdf`，PDF 文本抽取位于 page 4。
- Figure A / Method overview：`method_ps_rslg_overview_publication_20260510.pdf`，PDF 文本抽取位于 page 4。
- Figure E / Masked local naturalization mechanism：`method_masked_local_naturalization_mechanism_20260510.pdf`，PDF 文本抽取位于 page 8。
- Figure C / Projection gate：`method_projection_admissibility_gate_20260510.pdf`，PDF 文本抽取位于 page 9。

重要决策：

- 旧 `method_masked_local_naturalization_20260510.*` 含 same-root evidence crop、`\Delta normals 2--3^\circ`、`wins 3/3 seeds`，不再作为正文方法图使用。它最多作为 supplement/内部结果候选，除非 sampling schedule、mask rule、三任务三 seed protocol 在同页闭合。
- 正文 E 图只保留机制：rule scaffold fixes anchors/mask -> frozen local prior changes masked tokens -> projection selects active state -> re-encode。caption 明确它不是 global topology repair 或 operator-admission shortcut。
- A/B/C/E 的 caption 边界目前比图内文字更重要：图内只做结构短标签，claim 解释交给 caption 和正文。

当前仍未解决的图形风险：

- A/B/C/E 仍有流程图感，虽然比旧稿收敛；如果后续还有时间，应该继续减少圆角框/大标题，改成更像 ACM/TOG 方法图的 panel labels + sparse symbols + 少量真实 inset。
- `main.tex` 仍包含中文写作方案 appendix，导致 CJK/font warnings 和明显 submission 风险；这是全稿清理任务，不属于本轮方法图提交。
- appendix/figures-only 中仍有过大的 candidate/contact-sheet 图，latexmk 报 float too large；正式投稿前必须隐藏、拆分或移出正文编译流。

## 2026-05-10 19:32 CST 更新：二轮 reviewer 后的降噪版

本轮只读 reviewer 指出：`method_projection_admissibility_gate_20260510` 和 `method_trellis2_substrate_prelim_20260510` 已基本可用；`method_masked_local_naturalization_mechanism_20260510` 需要小修文字贴边；`method_ps_rslg_overview_publication_20260510` 信息密度过高，缩到 ACM 全宽后仍像内部系统图。

已执行的脚本级修改：

- `configure()` 字体基准从 `7.0` 提到 `7.6`，并保持 `pdf.fonttype=42`。
- 新增 `pipeline_node()`，让 Trellis2 prelim 的节点标题和 subtitle 间距更稳定，避免 condition/O-Voxel/Shape-SLAT/PBR 节点缩放后贴字。
- Overview A 从多节点+三条 visual anchors 的 dashboard 版降噪为三块：
  - `(a) frozen Trellis2 substrate`：只保留 `Enc_\theta`、O-Voxel `$V_d$`、Shape-SLAT `$F_d$`、Dec/Enc round trip、optional GLB/PBR。
  - `(b) grammar-owned recursive transition`：handles `$\\mathcal A_d$`、rules `$\\mathcal R_d$`、local prior `$\\mathcal N_\\theta$`、decode、projection、next state `$z_{d+1}$` 形成主 loop。
  - `(c) selected asset view`：只保留一个视觉锚点，并写明 metrics/matched ablations carry claims。
- Overview 删除旋转文字，统一为水平 `codec path`；公式统一到 `\\Pi_{\\theta,\\lambda_d}` 并带 `\\mathcal A_d`。
- Masked local naturalization E 标题缩短为 `Masked Local Naturalization`，图内补充 `$m_d$ is the sparse editable mask`，底部三张卡片改成关键词式：`mask fixed by grammar`、`sampler inside mask`、`projection owns state`。
- `sampler_mask()` 支持隐藏内部重复 label；在 B/E 中均隐藏 `sampler` 内部标签，只保留 anchors clamped 和外部节点标题，避免小图中文字打架。

最新 QA 图：

- `paper_siga/figures/method_diagram_drafts_20260510/method_publication_abc_contact_sheet_20260510.png`

当前判断：

- A 图不再是最终 camera-ready，但已经从“内部系统图”提升到可进入论文草稿的主方法图；后续若追求更高审美，应交给 Illustrator/Keynote 手排，并使用同一三块结构。
- B/C/E 可作为主文机制图继续保留；旧 evidence-heavy `method_masked_local_naturalization_20260510.*` 仍应视为 obsolete/supplement candidate，不进入主文引用链。
