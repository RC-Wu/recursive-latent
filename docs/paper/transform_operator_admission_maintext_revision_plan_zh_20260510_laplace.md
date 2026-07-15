# Transform Operator Admission 主文修改大纲

日期：2026-05-10  
范围：`paper_siga/main.tex` 的 transform/algorithm story 局部修改计划。  
约束：不修改 baseline / naturalization 脚本；不编译；不 push。

## 1. 当前算法环境审查

`paper_siga/main.tex` 当前已经使用 ACM-style algorithm 环境，且 Algorithm 1 没有放在 `figure` 中：

- `paper_siga/main.tex:8`：`\usepackage{algorithm}`
- `paper_siga/main.tex:9`：`\usepackage{algpseudocode}`
- `paper_siga/main.tex:352`：`\begin{algorithm}[t]`
- `paper_siga/main.tex:355`：`\begin{algorithmic}[1]`
- `paper_siga/main.tex:371`：`\end{algorithmic}`
- `paper_siga/main.tex:372`：`\end{algorithm}`

结论：排版方向正确。建议保留 `algorithm + algpseudocode`，不要改回 `figure/minipage/fbox`。这与 SATO arXiv:2604.09132 的 `acmart + algorithm + algpseudocode` 方法写法一致。

## 2. 主文 transform 故事应闭合的链条

目标链条：

1. **Operator definition**：transform-copy 是 `Copy` rule family 的一种 proposal，不是 mesh macro。
2. **Empirical certificates**：一个 transform operator 要进入 positive scheduler，需要通过 semantic match、state feasibility、transform compatibility、projection behavior、export diagnostics。
3. **Positive evidence**：pyrite/lattice、radial、bismuth/stair/compatible affine stack 可写成 screen-positive 或 near-positive。
4. **Boundary failure**：branch-tree 和 axis-mismatch 不能被包装成正例。branch-tree 是 hierarchy/scale/orbit preservation 边界；axis-mismatch 是 connected/renderable 但 contract fail 的 negative control。
5. **Claim boundary**：这些实验支持 operator admission protocol，不支持 strict equivariance、physical crystal growth、universal IFS success、watertight topology。

## 3. 建议直接改动

### Method: `Operator Admission and Screening`

在现有第一段后加一句：

> We call the supporting evidence an empirical certificate...

目的：把 screening 从“看结果表”变成 method semantics 的一部分。

### Experiment: `Transform-Copy Operator Screening for Admission`

现有段落已经很好，但还需两处收紧：

- 增加 `empirical certificate` 的组成：orbit/axis contract、copy-contact survival、surface connectivity、projection-readable handles。
- 明确 branch-tree 是 boundary / not admitted，而不是 “positive branch-copy”。

### Table: V21 transform admission

建议将第一行从：

`Branch-tree IFS & positive branch-copy ... diagnostic; not the main IFS-tree positive`

改成：

`Branch-tree IFS & boundary branch-copy ... rejected as positive; hierarchy/copy-orbit not certified`

这能避免 reviewer 误读为“我们声称 branch-tree 已 positive，只是没放主图”。

## 4. 正文可写结论

最保守主文口径：

> The transform study is an operator-library screening experiment. Pyrite/lattice and radial rows show that selected finite transform-copy families can pass the current PS-RSLG gates and remain exportable. Branch-tree and axis-mismatch rows show the boundary: connected or renderable outputs are not sufficient when transform hierarchy or compatibility assumptions fail.

## 5. 自我 reviewer 风险

1. **风险：V21/V23 是 OBJ-to-GLB texture export，不足以证明 sparse-latent execution。**  
   应对：正文明确 transform rows 只证明 operator admission protocol；sparse-latent superiority 由 projection/baseline experiments 承担。

2. **风险：pyrite/lattice 被误读为 physical crystal growth。**  
   应对：统一写 `lattice-inspired` / `crystal-inspired scaffold`，不写 physical growth。

3. **风险：radial 被误读为 equivariance。**  
   应对：写 empirical orbit screening，不写 sampler/codec/projection commute。

4. **风险：branch-tree 明明失败，却在表里叫 positive branch-copy。**  
   应对：把 table row 改成 boundary/rejected as positive。

5. **风险：algorithm 太抽象。**  
   应对：当前 Algorithm 1 作为 execution skeleton 足够；projection helper 可后续 appendix 补，不在本轮扩写。

## 6. 本轮实际修改目标

- 新增本 plan。
- 小幅修改 `main.tex` 的 operator admission 段落和 V21 transform screening 表。
- 不动 baseline/naturalization 脚本。
- 不编译、不 push。
