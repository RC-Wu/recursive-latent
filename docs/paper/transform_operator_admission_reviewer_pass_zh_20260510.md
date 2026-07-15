# Transform / Operator Admission 与 Algorithm 格式审稿式复查

日期：2026-05-10  
对象：`paper_siga/main.tex`  
写入范围：仅本文档；未修改 `main.tex` 或 figures。  
参考：`docs/paper/transform_operator_admission_story_gap_review_zh_20260510.md`，`literature/arxiv_2604_09132_src/src/Main.tex` 与 `src/4_Method.tex` 的 ACM `algorithm`/`algpseudocode` 用法。

## 1. 总体 verdict

当前版本已经基本闭合用户要求：

1. **Transform 作为 grammar 设计的实证筛选依据**：已成立。`main.tex:287-309` 把 operator admission 写成 scheduler-level decision，并用 semantic/state/compatibility/projection/export gates 定义进入 positive scheduler 的条件；`main.tex:555-560` 明确 transform-copy 结果是 grammar-design evidence，而不是 visual gallery 或 sparse-latent superiority proof。
2. **好/差结果形成算法设计论据**：已成立但仍可再压实。`main.tex:560` 已把 radial/pyrite/bismuth/stair/shared-axis 作为 admit-candidate，把 branch-tree 作为 boundary，把 axis-mismatch 作为 connected negative compatibility control。这里已经能说明算法不是按最终连通性或渲染好看筛选，而是按 grammar contract 筛选。
3. **Algorithm 使用 ACM `algorithm`/`algpseudocode` 而不是 figure**：已成立。`main.tex:8-9` 加载 `algorithm` 和 `algpseudocode`；`main.tex:354-379` 使用 `\begin{algorithm}[t]`、`\begin{algorithmic}[1]`、`\Require`、`\Ensure`、`\State`、`\Function`。这与参考源码 `literature/arxiv_2604_09132_src/src/Main.tex:64-65`、`src/4_Method.tex:39-87` 的用法一致。
4. **语言不冗余**：核心正文已比前一轮紧，但仍有几处可以继续减字或避免防御性重复。主要问题不是 story gap，而是有些段落同时解释 claim、反 claim、边界和 protocol，读者可能觉得谨慎但略显啰嗦。

结论：**不需要主线程再做结构性大改；建议主线程做小幅文字收束**。如果目标是投稿版，还必须清理附录中文工作计划和 visible TODO，但这超出本次 transform/operator admission 与 algorithm 格式复查主题。

## 2. 已闭合点

### 2.1 Operator admission 已从 gallery 变成 grammar contract

- `main.tex:287-288`：已经明确 admission 不是 visually plausible mesh macros，而是 admitted candidate / boundary diagnostic / negative compatibility control 的调度级决策。
- `main.tex:290-304`：五类 gate 完整覆盖 semantic、state、compatibility、projection、export；尤其 `main.tex:304` 明确 export success 不能作为 admission shortcut。
- `main.tex:309`：transform-copy 必须保持 recursive transform schedule、shared/certified support、projection 后的 grammar-readable handles；exact equivariance 被降级为需要专门实验。

审稿判断：这已经回答“transform 为什么是 grammar 设计依据”。读者能看到：operator admission 筛的是下一层规则是否可读，而不是最终图是否好看。

### 2.2 正负例已经服务算法设计

- `main.tex:556-558`：V21 是 strict admission batch；V23/V24 只是 corroboration，不放宽 V21 gates。
- `main.tex:560`：axis-mismatch 连接性通过但被拒绝，这一负例非常关键，说明 compatibility gate 高于 connectivity/renderability。
- `main.tex:566`：表 caption 已把 admit-candidate 限定为 grammar contract 下的 transform-copy evidence，不声称 sparse-latent superiority、exact equivariance、physical crystal growth 或 watertight topology。

审稿判断：这条证据链可用。尤其 axis-mismatch 是最强论据，建议主线程保留。

### 2.3 Algorithm 格式符合 ACM 论文习惯

- `main.tex:354-379` 是独立 algorithm 浮动体，不是 figure。
- 参考 SATO 源码 `src/4_Method.tex:39-87` 同样使用 `algorithm` + `algpseudocode`，包括 caption、label、`algorithmic[1]`、Require/Ensure、State/While/If/Return。

审稿判断：格式要求已闭合。无需改成 figure，也不需要引入 `algorithm2e`。

## 3. 仍建议主线程小改的问题

### 问题 1：`main.tex:555-560` 的 transform screening 段落信息密度过高

风险：当前两段承担了“不是 gallery”“不是 superiority”“certificate chain”“V21/V23/V24 关系”“V21 protocol 细节”“结果解释”“正负例角色”等太多功能。审稿人能读懂，但句子偏长，显得防御性略重。

建议把 `main.tex:556-560` 压成三段，每段只做一件事。可替换文本：

```tex
The transform-copy experiments are operator-admission tests, not a visual gallery. Their purpose is to decide which transform-copy rules are specified well enough to enter the positive scheduler under a fixed grammar contract. They do not by themselves prove that sparse-latent execution outperforms procedural OBJ construction.

For each row, the certificate chain is fixed before rendering: a locked classical transform target, an attached OBJ scaffold with shared or certified support, a declared projection/export policy, post-export surface-voxel diagnostics, and a decision about whether later rules may read the result as transform-copy state. V21 is the strict admission batch; V23 and V24 are used only as visual or metric corroboration for selected rows and do not relax the V21 gates.

The outcomes separate connectivity from admission. Radial, lattice, stepped, stair-loop, and shared-axis affine cases are admitted candidates under the stated contract; branch-tree remains a boundary case; axis-mismatch remains a negative compatibility control even though its OBJ and GLB connectivity diagnostics pass.
```

是否必须改：**建议改，但非阻塞**。当前版本已闭合要求；这是可读性优化。

### 问题 2：`main.tex:560` 与 Table caption `main.tex:566` 对 admit-candidate 的 caveat 有重复

风险：正文和 caption 都说“不是 superiority / equivariance / watertight / physical”，谨慎是对的，但连续阅读会略显重复。

建议：正文保留具体 case 解释，caption 保留最短边界。可把 `main.tex:566` caption 末句压缩为：

```tex
``Admit-candidate'' denotes positive evidence under this grammar contract; export connectivity is diagnostic and does not imply exact equivariance, watertight topology, or physical crystal growth.
```

是否必须改：**可选**。如果页数紧，建议改。

### 问题 3：`main.tex:575` pyrite lattice 的 admission wording 已正确但仍可能被误读为 clean positive

风险：表格里 `positive lattice copy` + `admit-candidate` 的视觉印象很强，虽然后面有 caveat，但审稿人快速扫表时可能把 pyrite 当作 clean topology positive。

建议把 `main.tex:575` 的 Transform role 改为：

```tex
screened lattice copy
```

或把 Admission decision 改为：

```tex
admit-candidate; r0 tiny-island caveat
```

是否必须改：**建议改**。这能更精确地延续 gap review 里“screen-positive 语义要更窄”的要求。

### 问题 4：`main.tex:585` pyrite showcase 句子较长，且“deeper stages increase ... while remaining ...” 可能被读成过强 depth proof

风险：虽然 `main.tex:585` 后半句已经降级 exact symmetry/topology/physical claim，但前半句“deeper stages increase occupied support and local crystal facets”仍像一个深度规律 claim。若该图只是 selected showcase，建议降低为 visual line。

建议替换文本：

```tex
The pyrite depth showcase in Figure~\ref{fig:pyrite-hq-depth-textured} is used only as selected visual corroboration for the admitted lattice-copy row. Across the shown stages, occupied support and local faceted motifs remain readable under the fixed render protocol, while raw faceted GLB surface diagnostics can still fragment. The symmetry/orbit score is a voxelized-vertex overlap diagnostic under normalized mirror and rotation transforms. We therefore treat pyrite and radial rows as connected lattice/orbit scaffold evidence and export compatibility, not as exact symmetry, clean surface topology, watertightness, or physical crystallization.
```

是否必须改：**可选但推荐**。它让 showcase 与 admission evidence 的层级更清楚。

### 问题 5：`main.tex:718` effective-resolution caption 最后一句略强

风险：`PS-RSLG preserves recursive motifs at selected attached regions` 比前文的 case-specific caveat 稍强，容易被读成普遍 effective-resolution 结论。虽然 `main.tex:704` 已经降级，但 caption 单独看仍偏强。

建议替换 caption 末句：

```tex
The PS-RSLG panels show selected attached regions where recursive motifs remain readable under the current protocol.
```

是否必须改：**建议改**。这属于语言降级，不影响结构。

### 问题 6：Algorithm 语义已足够，但 `main.tex:364` 的 `Admit` 和 `main.tex:372-377` 的 `ProjectAdmissible` 可以更显式连到五类 gate

风险：审稿人看 Algorithm 时可能问：Admission gates 在算法里具体在哪里发生？正文 `main.tex:287-309` 已解释，但 Algorithm 中 `Admit` 只是一行。

建议在 `main.tex:364` 之后加一行短注释式 State，或替换该行：

```tex
\State $(\widehat{\mathcal P}_d,m_d) \gets \operatorname{Admit}(\mathcal P_d,\mathcal A_d,\lambda_d)$ \Comment{semantic, state, compatibility, and projection-policy gates}
```

是否必须改：**可选**。格式要求已经通过；这是让算法和 admission 表更紧密。

## 4. 不建议再改的点

1. 不建议把 Algorithm 改回 figure。当前写法符合 ACM + SATO 参考源码。
2. 不建议继续堆 V23/V24 结果到主文 transform section。`main.tex:558` 已正确限定 V23/V24 只是 corroboration；更多视觉候选应留在 appendix/status。
3. 不建议把 axis-mismatch 写成失败案例。它应该是“connected negative compatibility control”，这是 admission 叙事的核心正资产。
4. 不建议把 export/PBR 成功与 operator admission 合并。`main.tex:304`、`main.tex:525`、`main.tex:749` 的分离是必要防线。

## 5. 是否需要主线程再改

**需要，但只需要小改。**

优先级建议：

1. 必做/高收益：压缩 `main.tex:556-560` 的 transform screening 叙事，减少防御性重复。
2. 高收益：收窄 `main.tex:575` pyrite wording，避免 clean positive 误读。
3. 中收益：降级 `main.tex:718` caption 的 effective-resolution 句子。
4. 可选：给 `main.tex:364` 的 `Admit` 加 gate comment，让 Algorithm 与 admission table 显式相连。

如果主线程只做一轮最小修订，建议只改上述 1、2、3。Algorithm 格式本身无需再动。

