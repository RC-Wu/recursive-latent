# Method / Theory Insertions for PS-RSLG（中文整合建议）

创建时间：2026-05-09  
目标文件：`paper_siga/main.tex`（本文件只给插入建议，不直接修改）  
写作目标：把 Method 从“系统模块串联”升级为 grammar calculus，同时保留 current paper 已经较好的 compact-state 写法。

## 0. 总体改法

建议不要把完整深版理论文档塞进主文。SIGGRAPH Asia 主文应采用“短公式 + 算法语义 + coverage table + projection invariant sketch”的结构。核心替换策略：

1. 保留当前 `Problem Setting` 的方向，但把第一句话改成“recursive program over sparse native state”，避免“pipeline”措辞。
2. 保留当前 `Core State and Handles` 的最小状态 \(z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d)\)，不要退回 8 元组。
3. 在 `Rule Templates as a Recursive Language` 中加入更明确的 rule template、feasibility/projectable condition 和 rule family table。
4. 在 `Projection-Stabilized Execution` 中加入 Algorithm-style paragraph，并把 masked flow/SDE naturalization 单独作为一个 paragraph。
5. 在 projection paragraph 后加入一个短 theorem/proof sketch，解释 per-depth projection 为什么比 final-only cleanup 更有理论意义。
6. 将 `Classical Systems as Limits` 扩展为一段 concise coverage proof sketches，或者放成表格。
7. 将 `Recursive Effective Resolution and Infinite Refinement` 改成更谨慎的 finite-depth + LOD/window recursion 表述。

## 1. Abstract / Introduction 可加的精炼 claim

### Abstract 中替换或补一句

建议在摘要中 “The key execution principle is projection inside the recursive transition” 后加：

```latex
This makes the learned sampler a masked local naturalizer rather than a global topology repair model, and gives connected support the status of a recursive state invariant.
```

中文意图：生成器不是全局修复器；connected support 是递归不变量。

### Introduction 中可加一句 reviewer-facing motivation

建议在 “The direct version of this idea fails for a specific reason.” 段后加：

```latex
The failure mode is semantic rather than merely geometric: once an orphan component becomes a frontier, motif source, sampler condition, or cache entry, later recursion has already consumed the error before final mesh cleanup can remove it.
```

这句把 projection 放进递归转移的必要性讲清楚。

## 2. Method 开头建议：Problem Setting

位置：`Method` 下 `Problem Setting` subsection 开头。  
建议把当前第一段替换为更强版本：

```latex
We formulate recursive 3D asset synthesis as execution of a grammar program over the native sparse state of a frozen 3D generator. Let \(x_0\) be a root mesh or generated root asset, \(y\) be an optional image, text, category, or material condition, and \(D\) be a finite recursion depth. The goal is to produce a renderable asset
\[
x_D=\mathcal{O}(z_D),\qquad
z_{d+1}\sim
\mathsf{T}_{\mathcal{G},\theta,d}(\cdot\mid z_d,y,\xi_d),
\quad d=0,\ldots,D-1,
\]
where \(\mathcal{G}\) is a recursive grammar, \(\theta\) is a frozen native 3D generator, and \(\xi_d\) includes stochasticity from rule choice, frontier sampling, local generative sampling, or sample selection. The grammar owns global structure: typed handles, transforms, attachment, frontiers, constraints, projection parameters, and caches. The frozen generator supplies the sparse native representation, masked local shape/material priors, decoding, re-encoding, and optional asset export.
```

保留一句命名：

```latex
We call the resulting formalism a Projection-Stabilized Recursive Sparse-Latent Grammar (PS-RSLG).
```

## 3. State subsection 建议：保留最小状态，压缩 admissible set

位置：当前 `Core State and Handles`。  
建议保留当前 \(z_d\) 形式，但把 invariant 更明确。可插入：

```latex
The minimal state deliberately separates recursive semantics from bookkeeping:
\[
z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d).
\]
\(\mathcal V_d\subset h\mathbb Z^3\) is the active sparse token support, \(\mathbf F_d:\mathcal V_d\rightarrow\mathbb R^q\) stores generator-native latent features, and \(\mathcal A_d\) is the grammar-readable anchor structure. A handle is
\[
h_i=(\sigma_i,T_i,\Omega_i,\alpha_i),
\]
with type \(\sigma_i\), local frame \(T_i\), owned or target support \(\Omega_i\), and attributes \(\alpha_i\). Masks, caches, seeds, rule traces, projection schedules, and export metadata are auxiliary executor state; they are important for implementation but are not the mathematical object the reader must track.
```

然后把 connected support invariant 放紧：

```latex
Let \(R_d\subset\mathcal V_d\) denote root anchors and let \(G_\eta(\mathcal V_d)\) be the sparse-token adjacency graph. The attached support is
\[
\mathcal V_{\mathrm{att}}(z_d)=
\{v\in\mathcal V_d:\ v\leadsto R_d\ \mathrm{in}\ G_\eta(\mathcal V_d)\}.
\]
We measure disconnected recursive mass by
\[
V_{\mathrm{conn}}(z_d)=
1-\frac{\operatorname{mass}(\mathcal V_{\mathrm{att}}(z_d))}
{\operatorname{mass}(\mathcal V_d)+\epsilon}.
\]
An admissible state has bounded connectivity, occupancy, material, and budget violations, and no active orphan frontier:
\[
\mathcal Z_{\mathrm{adm}}(\lambda)=
\{z:\ V_{\mathrm{conn}}(z)\le\epsilon_c,\;
V_{\mathrm{frontier}}(z)=0,\;
V_{\mathrm{occ}}(z)\le\epsilon_o,\;
V_{\mathrm{mat}}(z)\le\epsilon_m,\;
|\mathcal V(z)|\le T_{\max}\}.
\]
```

## 4. Rule subsection 建议：替换为 handle-to-proposal calculus

位置：当前 `Rule Templates as a Recursive Language`。  
建议主公式改为：

```latex
A rule is a local rewrite template over handles,
\[
\rho:\ h_i\mapsto
\{(\sigma_j,\tau_j,\Omega_j,m_j,\kappa_j,\pi_j,\eta_j)\}_{j=1}^{k}.
\]
Each emitted item creates or updates a handle of type \(\sigma_j\), local transform \(\tau_j\), target or ownership region \(\Omega_j\), edit mask \(m_j\), feasibility condition \(\kappa_j\), proposal kernel \(\pi_j\), and optional sampler or material schedule \(\eta_j\). The proposal kernel may instantiate frontier growth, branch splitting, stochastic attachment, transform-copy, local refinement, material transport, or cache lookup.
```

建议紧接 feasibility：

```latex
Rules are executable only when their materialized proposal is projectable. For a proposed support \(\Delta\mathcal V\), we require
\[
\Delta\mathcal V\subset
\mathcal R_{\mathrm{proj}}(z_d;b_d,r_d),
\]
or a valid bridge certificate
\[
\exists B:\quad
\Delta\mathcal V\cup B\in\mathcal Z_{\mathrm{adm}}(\lambda_d),
\qquad
\operatorname{cost}(B)\le b_d.
\]
Thus a patch is not active merely because it is locally plausible; it must remain usable by the next recursive step.
```

建议 table（可替换当前表或追加一列）：

```latex
\begin{table}[t]
  \centering
  \caption{Rule families share the same handle-to-proposal template but differ in proposal kernels and feasibility conditions.}
  \label{tab:rule-families}
  \begin{tabular}{lll}
    \toprule
    Family & Proposal kernel & Typical use \\
    \midrule
    grow & attached frontier extension & vines, roots \\
    branch & handle split & trees, bushes \\
    attach & frontier hit with bridge certificate & porous/DLA-like growth \\
    copy & connected motif transform & ornaments, portals \\
    split/extrude & local frame decomposition & architecture \\
    refine & terminal densification & zoom/detail \\
    material & handle transport/blend & PBR export continuity \\
    cache & motif/LOD descriptor lookup & finite-memory recursion \\
    \bottomrule
  \end{tabular}
\end{table}
```

## 5. Operational semantics 建议：主公式 + algorithm paragraph

位置：当前 `Projection-Stabilized Execution`。  
建议保留 compact transition，略微改成：

```latex
The recursive transition is
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
\(\mathcal T_\theta\) contains rule selection, sparse proposal, masked merge, competition, feasibility filtering, and optional local naturalization. Projection is inside the recursive map, not a final mesh cleanup pass.
```

Algorithm paragraph：

```latex
Execution proceeds as follows. First, active handles are selected from \(\mathcal A_d\), and applicable rules \(\mathcal R_d\) are chosen by type, priority, budget, frontier state, and optional symmetry orbit. Second, the rules instantiate sparse proposals, which are rejected or deferred when they fall outside the projectable domain. Third, accepted proposals are merged with masks and blend kernels, then filtered by occupancy competition and attachment constraints. Fourth, edited regions may be locally naturalized by the frozen masked sampler while anchor regions are hard-clamped. Finally, the state is decoded, projected to an admissible connected asset, re-encoded, and all handles, frontiers, material metadata, diagnostics, and caches are updated before the next depth.
```

## 6. Flow/SDE naturalization 建议：单独 paragraph

位置：`Projection-Stabilized Execution` 内或其后。  
建议替换/扩展当前 `Masked flow naturalization`：

```latex
\paragraph{Masked sampler naturalization.}
The frozen generator is used as a local naturalization prior, not as a global repair model. In SDE form,
\[
dZ_t=f_\theta(Z_t,t,y)\,dt+g(t)\,dW_t,
\]
or, for a deterministic flow,
\[
\frac{dZ_t}{dt}=v_\theta(Z_t,t,y).
\]
Let \(m_d\) be the rule edit mask clipped by projectability and attachment constraints. A reverse step is hard-clamped outside the mask:
\[
Z_{t-\Delta t}=
(1-m_d)\odot Z_{\mathrm{anchor}}
+m_d\odot\Phi_{\theta,t}(Z_t,y).
\]
For sparse features this corresponds to
\[
\mathbf f_i'=
(1-\alpha_i)\mathbf f_i^{\mathrm{rule}}
+\alpha_i\mathbf f_i^{\theta},
\qquad i\in m_d.
\]
The sampler therefore improves local shape or material realization while the grammar preserves global recursive topology.
```

必须避免的句子：`the flow repairs topology`。  
建议用：`the sampler naturalizes local realization under a hard grammar mask`。

## 7. Projection invariant 建议：短 theorem/proof sketch

位置：Projection paragraph 后，`Why final-only cleanup is insufficient` 可升级成 theorem-style。

```latex
\paragraph{Projection invariant.}
Let \(e(z)\) combine connectivity, orphan-frontier, occupancy, material, renderability, and budget violations. Suppose projection satisfies
\[
e(\Pi_{\lambda_d}(x))\le\epsilon_P
\]
and the decode/re-encode round trip contributes at most \(\epsilon_E\):
\[
e(\operatorname{Enc}_\theta(\Pi_{\lambda_d}(x)))
\le e(\Pi_{\lambda_d}(x))+\epsilon_E.
\]
Then every executed recursive state satisfies
\[
e(z_d)\le\epsilon_P+\epsilon_E,\qquad d=1,\ldots,D.
\]
This follows directly from the transition \(z_{d+1}=\operatorname{Enc}_\theta(\Pi_{\lambda_d}(\operatorname{Dec}_\theta(\bar z_{d+1})))\). Final-only cleanup lacks this invariant because an invalid component can already have been selected as a parent, frontier, motif source, sampler condition, material source, or cache entry before the final mesh is cleaned.
```

这段是最重要的 theory response。它解释了为什么 projection 是 grammar semantics，不是后处理。

## 8. Classical systems coverage 建议：压成一段 + table

位置：当前 `Classical Systems as Limits`。  
建议保留数学短句，但增强为 proof sketch：

```latex
\paragraph{Classical systems as limits.}
IFS is recovered by a single patch handle, transform-copy rules, union merge, identity sampler, and identity projection:
\[
\mathcal V_{d+1}=\bigcup_i Q_h(\tau_i(\mathcal V_d)).
\]
L-systems are recovered when \(\mathcal A_d\) is an ordered symbol string or turtle-frame graph and the scheduler applies synchronous rewriting before geometric interpretation. Space colonization is recovered by tip and attractor handles, nearest-attractor assignment, occupancy exclusion, and growth along averaged attraction directions. DLA-like accretion is recovered when the proposal kernel samples exposed frontier cells from a hitting distribution and accepts only attached or bridge-certified sites. Finite shape grammars and CGA-style programs are recovered by typed face, tile, and portal handles with split, extrude, repeat, replacement, and transform-copy rules. Symmetry and crystal-like programs are recovered by closing the rule set and scheduler under a group or lattice action.
```

然后加 caveat：

```latex
These are expressivity statements, not quality claims: they show that classical procedural rules are degenerate PS-RSLG transitions obtained by disabling or restricting learned naturalization, projection, or sparse generative features.
```

如果加表：

```latex
\begin{table}[t]
  \centering
  \caption{Classical procedural systems as restricted PS-RSLG programs.}
  \label{tab:classical-limits}
  \begin{tabular}{lll}
    \toprule
    System & Restriction & Learned component \\
    \midrule
    IFS & contractive transform-copy union & identity \\
    L-system & ordered synchronous handle rewrite & optional realization only \\
    Space colonization & tip-attractor grow rules & identity/local mask \\
    DLA & stochastic frontier attachment & identity/local mask \\
    Shape grammar & typed split/extrude/replace & optional local prior \\
    Symmetry & group-closed rule orbits & approximate postprocess \\
    \bottomrule
  \end{tabular}
\end{table}
```

## 9. Symmetry/crystal 建议：谨慎等变表述

位置：当前 `Symmetry, Cache, and Recursion Scope`。  
建议替换强 theorem 为 approximate metric：

```latex
If the rule set is closed under a group \(G\),
\[
\forall g\in G,\ \forall \rho\in\mathcal R,\qquad
g\circ\rho\circ g^{-1}\in\mathcal R,
\]
and the scheduler expands complete orbits, the proposal stage is \(G\)-closed. Exact equivariance would additionally require merge, sampler, projection, codec, and sparse-grid quantization to commute with \(G\), which is not guaranteed in our implementation. We therefore evaluate symmetry as an approximate error:
\[
d_{\mathcal S}(\mathsf T(gz),g\mathsf T(z))
\le
L_{\mathrm{post}}
(\epsilon_{\mathrm{rule}}+\epsilon_{\mathrm{merge}}
+\epsilon_{\mathrm{sampler}}+\epsilon_{\mathrm{proj}}
+\epsilon_{\mathrm{codec}}+\epsilon_{\mathrm{grid}}).
\]
```

## 10. Infinite / LOD recursion 建议：有限主张 + 扩展

位置：当前 `Recursive Effective Resolution and Infinite Refinement` / `Symmetry, Cache, and Recursion Scope`。  
建议使用：

```latex
The empirical claim of this paper is finite-depth recursive asset generation:
\[
D<\infty,\qquad |\mathcal V_d|\le T_{\max}(d).
\]
Unbounded recursion is a program semantics extension. For contractive transform systems, the symbolic program may define a limiting object under standard IFS assumptions, while rendering remains a finite-depth approximation. For non-contractive assets, a bounded visible-window executor materializes only active chunks,
\[
\mathcal V_t^{\mathrm{active}}=
\bigcup_{\Omega\in W_t}\mathcal V_{\Omega,t},
\qquad
\sum_{\Omega\in W_t}|\mathcal V_{\Omega,t}|\le T_{\max},
\]
and stores off-window regions as LOD or cache descriptors. This supports infinite logical recursion under finite active memory, but it is not an infinite mesh-output claim.
```

## 11. Results / Discussion caveats to align with theory

### Results 中可加

```latex
The projection ablation should be read as evidence for recursive-state stability, not merely final mesh cleanup: per-depth projection changes which frontiers, motifs, and sampler conditions are available at later depths.
```

### Texture/PBR 中可加

```latex
Texture export is evaluated after projected geometry passes structural checks. We do not use textured appearance as evidence of connectivity, and we do not claim per-depth material recursion unless material handles are explicitly updated by the program.
```

### DLA/crystal 中必须加

```latex
The DLA and crystal-inspired cases are grammar/frontier stress tests. They demonstrate that the rule template can express stochastic accretion or symmetry closure, but they should not be interpreted as physical growth simulations.
```

## 12. 建议删除或弱化的旧式表达

如果 main text 或 draft 中出现以下表达，应替换：

- `the flow repairs recursive topology`  
  改为：`the masked sampler naturalizes local edited regions while topology is controlled by the grammar and projection`。

- `projection cleans up the final mesh`  
  改为：`projection is inside the recursive transition and removes invalid state before later rules can fire`。

- `PS-RSLG guarantees symmetry`  
  改为：`PS-RSLG can schedule group-closed proposals and reports approximate equivariance error`。

- `infinite 3D generation`  
  改为：`finite-depth assets, with unbounded logical recursion represented through contractive or LOD/windowed semantics`。

- `Trellis2 makes recursive assets realistic`  
  改为：`a frozen native 3D generator supplies local sparse-latent priors and selected texture/PBR export compatibility`。

## 13. Exact main.tex insertion map

Suggested edits, in order:

1. `abstract`: add the one-sentence masked-sampler/connected-invariant claim after projection sentence.
2. `Introduction`, paragraph 2 or 3: add the semantic failure sentence about orphan components becoming frontiers/caches.
3. `Method/Problem Setting`: replace first paragraph with Section 2 snippet above.
4. `Method/Core State and Handles`: ensure it uses \(z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d)\); insert connected invariant snippet.
5. `Method/Rule Templates`: replace rule formula with Section 4 snippet and add feasibility condition.
6. `Method/Projection-Stabilized Execution`: replace long operator-chain remnants with compact transition and algorithm paragraph.
7. Immediately after execution: insert `Masked sampler naturalization` paragraph.
8. Projection paragraph: append `Projection invariant` proof sketch.
9. `Classical Systems as Limits`: replace with Section 8 paragraph and optional table.
10. `Symmetry/Cache/Recursion`: replace strict language with approximate equivariance and finite-depth/LOD wording.
11. `Results`: add caveats from Section 11 to prevent overclaiming.

## 14. One-paragraph paper-ready method summary

可作为 Method 开头或 Section 3 lead-in 的英文版本：

```latex
PS-RSLG treats recursive 3D synthesis as grammar execution over a frozen generator's native sparse latent state. A state contains active sparse tokens, their latent features, and grammar-readable handles. Rules rewrite handles into masked sparse proposals with transforms, feasibility conditions, and optional sampler schedules. The frozen generator is used only as a masked local naturalizer and codec: edited regions may be resampled under a hard grammar mask, then decoded, projected to a connected admissible asset, and re-encoded before any later rule can fire. This execution semantics makes connected support and attached frontiers recursive invariants rather than final cleanup targets, while still recovering IFS, L-systems, space colonization, DLA-like frontier growth, shape grammars, and symmetry transform-copy programs as restricted cases.
```

