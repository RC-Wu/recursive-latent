# Transform/Algorithm Reviewer Iteration 2

日期：2026-05-10  
范围：`paper_siga/main.tex` 中 transform operator admission、Algorithm 1、可见内部计划、claim boundary。  
约束：未修改 baseline / naturalization 脚本；未编译；未 push。

## 1. 本轮发现的问题

### 1.1 Algorithm 1 环境正确，无需改成 figure

当前 `main.tex` 已经使用 ACM-style `algorithm + algpseudocode`：

- `paper_siga/main.tex:8`：`\usepackage{algorithm}`
- `paper_siga/main.tex:9`：`\usepackage{algpseudocode}`
- `paper_siga/main.tex:354`：`\begin{algorithm}[t]`
- `paper_siga/main.tex:357`：`\begin{algorithmic}[1]`
- `paper_siga/main.tex:373`：`\end{algorithmic}`
- `paper_siga/main.tex:374`：`\end{algorithm}`

审查结论：Algorithm 1 是独立 algorithm 浮动体，不在 `figure` 中。这里不需要 patch。若后续扩展算法，建议继续用 `algorithmic` 行号风格，而不是把伪代码塞进 figure/minipage。

### 1.2 Transform operator admission 叙事基本闭合

相关位置：

- `paper_siga/main.tex:287-309`：`Operator Admission and Screening`
- `paper_siga/main.tex:544-570`：`Transform-Copy Operator Screening for Admission` 和 V21 screening table

当前叙事链已经是：

1. operator 不是视觉 mesh macro；
2. positive candidate 必须留下下一层 rule 可读的 recursive state；
3. empirical certificate 包含 intended semantics、root-attached/projectable support、grammar-readable handles/descriptors；
4. transform-copy 需要 transform schedule、shared/certified support、projection 后可读 handles；
5. connected but contract-violating rows 是 negative controls；
6. branch-tree 是 boundary case，axis-mismatch 是 connected/exportable 但 contract fail。

审查结论：本轮无需继续扩写 transform 正文。继续扩写反而可能让主线变防御性过强。

### 1.3 可见中文内部计划仍是投稿风险

发现位置：

- 原状态：`paper_siga/main.tex:753-848` 附近有 `ChinesePlan` 附录，包含中文写作方案、审稿判断、TODO list 和内部修改记录。

风险：即使这是很有用的团队内审稿材料，若默认编进 review PDF，会被 reviewer 视为内部计划泄漏，且中文长段会破坏匿名投稿观感。

### 1.4 过度 claim 当前主要被控制住

当前 transform 相关 claim boundary 较稳：

- `paper_siga/main.tex:309` 明确 exact group equivariance 不成立，orbit/symmetry 只是 screening diagnostics。
- `paper_siga/main.tex:545` 明确 transform-copy 不证明 sparse-latent execution outperforms procedural OBJ construction。
- `paper_siga/main.tex:553` 表 caption 明确 screen-positive 不等于 sparse-latent superiority、exact equivariance、physical crystal growth 或 watertight topology。
- `paper_siga/main.tex:560` branch-tree 已经从 positive 改为 boundary/rejected as positive。
- `paper_siga/main.tex:566` axis-mismatch 已经是 negative compatibility control。

仍需全局注意的非 transform 风险：正文其他段落还有 `TeacherRewriteTODO` 宏调用，但默认 `\showinternalnotesfalse` 时不可见；后续 final draft 应全清，而不是只依赖开关。

## 2. 本轮已做的最小 patch

只修改 `paper_siga/main.tex`，把中文内部计划块放入内部开关：

- `paper_siga/main.tex:753`：新增 `\ifshowinternalnotes`
- `paper_siga/main.tex:754`：保留 `\begin{ChinesePlan}`
- `paper_siga/main.tex:849`：保留 `\end{ChinesePlan}`
- `paper_siga/main.tex:850`：新增 `\fi`

效果：当前 `paper_siga/main.tex:31` 为 `\showinternalnotesfalse`，因此默认编译时不显示中文写作方案与内部审查记录。内容没有删除，便于内部继续追踪。

## 3. 建议改但本轮未改

1. `paper_siga/main.tex:312-313` 有历史 revision trace 注释。LaTeX 注释不会进 PDF，但 final source cleanup 时建议移到内部文档。
2. `TeacherRewriteTODO` / `ExpFigTODO` / `EvidencePending` 宏调用默认不可见，但源码中很多。投稿前建议统一清理或移到 supplement planning doc。
3. Algorithm 1 目前是 execution skeleton。若 reviewer 要求算法更具体，下一步应新增或扩展 `Admissibility Projection` 子算法，写清 connectivity graph、root anchors、component scoring、connector certificates、orphan handle deactivation、handle reattachment、diagnostics。
4. Transform table 仍把 `Pyrite lattice` 标为 `screen-positive with tiny-island/export caveat`。这是可接受的保守正例，但如果主线程后续 surface metrics 更弱，应降为 `near-positive` 或 `screen-positive only after r1 dilation`。

## 4. Reviewer 会怎么批评

强 reviewer 可能会说：

1. “Operator admission gates 是好概念，但 evidence 仍像 post-hoc screening。请证明这些 gates 在 rule scheduling 前已经锁定，而不是看完结果后解释。”
2. “Algorithm 1 太高层，`Filter`、`\Pi`、handle update 是核心，却没有独立伪代码或实现细节。”
3. “Transform-copy rows 主要是 OBJ dry-run 加 Trellis2 export，不能证明 sparse-latent transform execution 优于 mesh-space transform construction。”
4. “Connectivity/LCR 只能证明没有大规模断裂，不能证明 transform hierarchy、orbit consistency 或 later grammar readability。”
5. “中文内部计划、TODO 宏、revision trace 若出现在 PDF 或源码补充中，会显著削弱投稿成熟度。”

## 5. 二次修改后的 claim boundary

本轮后建议主文保持以下边界：

- 可以 claim：PS-RSLG 把 transform-copy 作为 grammar operator admission/screening 问题处理，而不是把视觉结果当作正例。
- 可以 claim：radial、pyrite/lattice、stepped/stair、compatible affine rows 在当前 gates 下提供 screen-positive 或 caveated-positive evidence。
- 可以 claim：branch-tree 和 axis-mismatch 展示 admission 边界；connected/exportable 不等于 operator admissible。
- 不应 claim：strict equivariance、universal IFS/fractal success、physical crystal growth、watertight topology。
- 不应 claim：V21 transform-copy 结果单独证明 sparse-latent execution beats procedural OBJ or mesh-space recursion。
- 不应 claim：Texture/PBR export 是结构正确性的证据；它只能是 asset/export compatibility diagnostic。

## 6. 本轮状态

- 已 patch：`paper_siga/main.tex`
- 已新增审阅文档：`docs/paper/transform_algorithm_reviewer_iteration2_zh_20260510_laplace.md`
- 未编译，按用户要求交由主线程统一验证。
- 未 push。
- 未修改 baseline / naturalization 脚本。
