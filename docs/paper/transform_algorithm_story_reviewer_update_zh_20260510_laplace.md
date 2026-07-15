# Transform / Algorithm Story Reviewer Update

日期：2026-05-10  
范围：只给 `paper_siga/main.tex` 的写作与结构建议，不直接修改论文源码。  
参考：arXiv:2604.09132 SATO, *Strips as Tokens: Artist Mesh Generation with Native UV Segmentation*, ACM Transactions on Graphics / SIGGRAPH 2026；其 arXiv 页面显示为 TOG/SIGGRAPH 2026 稿件，源码使用 `acmart`，并在 Method 中用独立 `algorithm` + `algpseudocode` 浮动体写算法。

## 1. Reviewer 总判断

当前稿件已经把 transform 从“好看的一类结果”改写成了 `Operator Admission and Screening`，这是正确方向。关键还差一步：必须把 transform-copy 明确写成 grammar rule library 的 admission / rejection protocol，而不是写成 Trellis2 具有 transform equivariance、也不是写成 pyrite/radial 视觉图证明所有 IFS 都解决。

建议主线是：

> Transform-copy is a candidate grammar operator family. It enters the positive PS-RSLG scheduler only if it passes semantic-match, state-feasibility, transform-compatibility, projection-behavior, and export-diagnostic gates. Positive pyrite/lattice and radial cases demonstrate screened finite transform-copy operators; branch-tree and axis-mismatch cases are negative controls showing that connectivity/renderability alone does not admit an operator.

这样写的好处是把 transform 变成方法闭环的一部分：rule proposal -> compatibility gate -> projected recursive state -> later-rule-readable handles，而不是额外 gallery。

## 2. 与当前 Method 的闭合方式

当前 `main.tex` 的结构已经具备三块可闭合材料：

1. `Transform-copy proposals`：支持和 feature transport 公式已经出现，说明 transform 是 sparse support / feature / material handle 的 rule-level 操作。
2. `Operator Admission and Screening`：已经有 gate table，强调 admission 不是视觉好看，也不是 GLB export 成功。
3. `Projection-Stabilized Execution`：Algorithm 1 把 proposal、filter、merge、masked local naturalization、decode、projection、re-encode 串起来。

建议把三者的逻辑关系进一步显式化：

- transform-copy 先是 `Prop_R(z_d)` 产生的一类 proposal；
- compatibility gate 检查 affine stack、orbit schedule、axis/scale consistency、mask ownership、copy contact / bridge assumptions；
- projection gate 检查 decode 后是否还能成为 root-attached、handle-readable 的 recursive state；
- 只有通过这些 gate 的 transform family 才允许进入 claim-bearing scheduler；
- 失败但连通的 transform rows 保留为 negative controls，证明 gate 不是 connectivity proxy。

这能回答 reviewer 的一个潜在质疑：为什么 transform 不是一组手工 OBJ / visual macros？答案是：因为 admission 的对象不是最终 mesh，而是能否成为下一层规则可读取的 recursive state。

## 3. Algorithm 排版建议：不要放进 figure

当前稿件已经加载：

```tex
\usepackage{algorithm}
\usepackage{algpseudocode}
```

并且 Algorithm 1 已经是：

```tex
\begin{algorithm}[t]
  \caption{Projection-stabilized recursive sparse-latent execution.}
  \begin{algorithmic}[1]
  ...
  \end{algorithmic}
\end{algorithm}
```

这个方向应保留。不要把算法放进 `figure` / `minipage` / `fbox`。理由：

- ACM/TOG 风格中，算法是独立浮动体，不是图像说明。SATO 源码就是 `acmart` + `algorithm` + `algpseudocode`，并在 Method 中用 `\begin{algorithm}[t] ... \begin{algorithmic}[1]`。
- figure 环境会让 algorithm 被当作视觉图处理，caption、编号、浮动和 accessibility 语义都不对。
- reviewer 会把 figure-boxed algorithm 读成草稿排版或补丁，而不是标准 Method artifact。
- `algpseudocode` 的 `\Require`, `\Ensure`, `\State`, `\For`, `\Return` 能把算法压成可执行 pipeline，正适合 PS-RSLG 的 state-transition claim。

建议算法内容保留简短，不塞解释性长句。Algorithm 1 应只写：

- input / output；
- encode root and initialize handles；
- select rules；
- propose / filter / merge；
- optional masked local naturalization；
- decode；
- project；
- re-encode；
- update handles and deactivate detached descriptors。

解释性文字放在算法前后 paragraph；projection 细节可以另写一个 `AdmissibilityProjection` helper 或 appendix algorithm，但不要把 Algorithm 1 扩成半页公式说明。

## 4. Transform 证据该怎么讲

### 4.1 Positive: pyrite / lattice

Pyrite/lattice 是当前最适合的 transform positive，但措辞必须窄：

- 可写：finite transform-copy lattice / orbit scaffold passes current admission gates.
- 可写：surface-voxel diagnostics show dominant or connected support after export.
- 可写：visual and PBR export are compatible with a crystal-inspired lattice asset.
- 不写：physical pyrite growth is solved.
- 不写：Trellis2 is equivariant to lattice transforms.
- 不写：watertight or mesh-face topology is proven clean.

V21/V23 的 pyrite/lattice 行可以作为 operator screening evidence，尤其适合放在 `Operator Admission` 后或 Experiments 的 transform subsection。它证明某些 group-like / lattice-like transform stacks 在当前 projection/export pipeline 下可以作为 screened positive operators。

### 4.2 Positive / near-positive: radial

Radial ornament 的价值是证明 transform evidence 不只是一种 cubic lattice：

- radial orbit 有明确 order、axis、ring/spoke schedule；
- V21/V23 多个 radial rows 在 surface-voxel metrics 下接近或达到单组件；
- 但它更适合写成 empirical radial transform-copy evidence，而不是 symmetry theorem。

建议加一句限制：

> We measure radial consistency as an empirical orbit-screening diagnostic under voxelized/surface-sampled support; it is not a proof that the codec, sampler, or projection commutes with the rotation group.

### 4.3 Negative: branch-tree

IFS branch-tree 是必须保留的 negative/control，不要硬包装成成功：

- `strict_matched_psrslg_proxy_visual_audit` 已指出 branch-tree visual task 失败：连接性可以为 1，但 self-similar copy orbit、branch fan、scale decay、direction relation 丢失。
- 这正好说明 admission gate 的必要性：connectivity metrics 不能单独决定 transform operator 进入 positive scheduler。
- 可以写成：branch-tree remains an unadmitted transform-copy family until copy hierarchy, scale decay, and orbit/contact metrics pass.

这比单纯说“branch-tree 失败”更有方法论价值：它把失败变成 admission protocol 的反例。

### 4.4 Negative: axis mismatch

Axis-mismatch row 的价值更清楚：它可能 connected、renderable，但仍应 rejected as positive because transform assumptions fail。

建议在表 caption 或正文明确：

> The axis-mismatch row is deliberately connected/renderable but rejected, showing that the gate is a rule-contract gate rather than a visual or connectivity gate.

这句话非常重要，因为它能防 reviewer 说 screening 是 cherry-picking。

## 5. 建议的主文改写位置

### Method 中

在 `Operator Admission and Screening` 开头加强一句：

> The transform experiments below are not used as evidence of exact generator equivariance. They instantiate a rule-library screening protocol: a transform family is admitted only when its copied support, feature/material handles, orbit metadata, and projected decoded state remain readable by the next grammar step.

在 gate table 后补一句：

> We therefore separate `screen-positive` operators from `connected but rejected` controls; both may be renderable, but only the former can enter the claim-bearing scheduler.

### Experiments 中

把 transform 小节从“结果展示”改成“admission evidence”：

- Positive screened rows: pyrite/lattice, radial ornament, maybe bismuth/affine stack if visual and metrics pass.
- Negative controls: branch-tree task mismatch, axis mismatch, over-smoothed / blob-like transform results.
- Metrics: r0/r1 surface components, LCR, orbit/contact survival, copy hierarchy preservation, approximate symmetry/orbit error, renderability.
- Claim: screened transform-copy operators are feasible under PS-RSLG gates.
- Not claim: exact equivariance, physical crystal growth, universal IFS success.

### Caption 中

将 caption 里的 “strict transform-copy screening” 保留，但把 admission 状态改成更保守词：

- `screen-positive`
- `screen-positive with caveat`
- `connected negative`
- `rejected as positive`
- `appendix diagnostic`

避免 `admit` / `solved` / `equivariant` 这类过强词。

## 6. 建议表格结构

建议 transform screening 表采用如下列：

| Row | Target family | Transform contract | Surface comp / LCR | Orbit/contact diagnostic | Screening decision | Claim allowed |
|---|---|---|---|---|---|---|
| pyrite lattice | finite lattice copy | affine/lattice stack, contact bridges | report r0/r1 | lattice/contact readable | screen-positive with caveat | lattice-inspired transform-copy asset |
| radial ornament | radial orbit | order, axis, spoke/ring closure | report r0/r1 | radial orbit readable | screen-positive / near-positive | empirical radial transform evidence |
| branch tree | contractive branch-copy | copy hierarchy + scale decay | may be connected | hierarchy not preserved | rejected as positive | negative admission control |
| axis mismatch | incompatible stack | intentionally mismatched axes | may be connected | contract fails | connected negative | gate is not visual/connectivity-only |

这个表格比 gallery 更有 reviewer 说服力，因为每一行都回答“为什么这个 operator 可以或不可以进入 grammar library”。

## 7. 与 SATO 的可借鉴点

SATO 对本项目的启发不是内容相似，而是写法相似：

- 先定义表示/执行单位：SATO 是 strips-as-tokens；PS-RSLG 是 typed sparse state + handles + grammar proposals。
- 再给标准算法：SATO 用独立 algorithm 浮动体说明 sequence construction；PS-RSLG 应用独立 algorithm 浮动体说明 recursive execution。
- 实验围绕表示选择是否带来结构收益，而不是只展示漂亮图。PS-RSLG 也应围绕 operator admission、projection inside transition、negative controls 和 matched tasks 组织。

因此，算法排版和 transform story 的共同目标是让 reviewer 看到一个可执行的 method，而不是一个视觉 pipeline。

## 8. 最保守可写结论

建议最终主文只写以下强度：

> Transform-copy rules are treated as screened grammar operators. Lattice/pyrite and radial rows show that selected finite transform families can pass the current PS-RSLG gates and remain exportable as textured assets. Branch-tree and axis-mismatch rows show the boundary: connected or renderable outputs are not sufficient when transform hierarchy or compatibility assumptions fail. We therefore use transform experiments to justify operator admission and failure screening, not to claim exact equivariance or universal IFS generation.

这句话和当前数据最匹配，也能把 positive / negative / algorithm 三条线闭合。

## 9. 立即行动清单

1. 保留当前 `algorithm` + `algpseudocode` 环境；不要回退到 figure/minipage。
2. 将 Algorithm 1 控制在 state-transition skeleton，复杂 projection 细节另写 helper 或 appendix。
3. 在 Method 中明确 transform evidence 是 operator-library screening，不是 generator equivariance proof。
4. 将 V21/V23 transform rows 的状态统一为 `screen-positive`, `near-positive`, `connected negative`, `rejected as positive`, `appendix diagnostic`。
5. 主文 positive 优先 pyrite/lattice + radial；branch-tree 作为 negative admission control；axis-mismatch 作为 gate-not-connectivity-only control。
6. 所有 pyrite/crystal 文字限定为 `crystal-inspired` / `lattice-inspired` / `finite transform-copy scaffold`。
7. 不用 GLB/PBR 成功替代 transform hierarchy、copy contact、orbit consistency 和 projection survival 指标。
