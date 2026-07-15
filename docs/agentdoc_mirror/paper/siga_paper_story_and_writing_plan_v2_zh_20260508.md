# SIGA 论文主故事与写作推进计划 v2

日期：2026-05-08  
目标：在不修改 `paper_siga/main.tex` 的前提下，先形成可审阅的中文写作决策稿，用于统一论文大纲、任务定义、方法论框架、贡献、abstract / intro / conclusion / experiment plan 的写作口径。  
写作范围：本文档只做论文组织和写作推进，不做实验、不 SSH、不下载大文件。

输入依据：

- `docs/paper/intro_related_contribution_draft_zh_20260508.md`
- `docs/paper/paper_outline_method_figure_plan_zh_20260508.md`
- `docs/theory/formal_recursive_generative_grammar_v2_zh_20260508.md`
- `docs/paper/method_formal_framework_skeleton_en_20260508.md`
- `docs/subagent_strict_paper_story_audit_zh_20260508.md`
- `docs/figures/figure_aesthetic_review_zh_20260508.md`
- `paper_siga/main.tex`

## 0. 总决策

这篇 SIGGRAPH Asia 方法论文应先定成一个严格、窄而可防守的故事：

> We study finite-depth recursive 3D asset growth in a frozen native 3D generative representation. The core method is Projection-Stabilized Recursive Sparse-Latent Grammar (PS-RSLG): grammar rules operate on mesh-derived sparse O-Voxel/SLAT support and features, while decode -> component projection -> re-encode is part of every recursive transition, so fragments are suppressed before they can seed later growth.

不要把论文写成以下任一版本：

- 不写成“真正无限递归 3D 生成”；
- 不写成“通用 Escher / impossible geometry 系统”；
- 不写成“高质量 PBR 资产生成已解决”；
- 不写成“任意 3D grammar / 任意 3D editing 框架”；
- 不写成“flow / SDE repair 已经可靠保持递归拓扑”。

最稳主线是：

1. 传统 procedural recursion 有结构控制，但缺现代 learned asset representation 和 appearance pipeline。
2. 现代 3D generator 有 one-shot asset 能力，但不是为稳定重复执行 grammar 而设计。
3. 递归生成真正困难点不是“生成一次漂亮对象”，而是“中间错误会成为下一层递归根”。
4. 因此 projection 必须进入递归算子本身，而不是最终 cleanup。
5. sparse 3D latent state 让 support、features、anchors、frontiers、masks、occupancy competition 和 projection 能被统一组织。
6. 当前证据支撑 selected finite-depth assets：vine/root、tree/bush、selected ornament / portal / architecture / hard-surface transform-copy、porous/frontier stress tests。
7. texture/PBR 只能写为 selected compatibility / smoke-test，不作为主贡献。

统一命名建议：

- 正文方法名：**Projection-Stabilized Recursive Sparse-Latent Grammar (PS-RSLG)**。
- 避免同时使用 `P-RSLG` 和 `R-SLG` 造成混乱。若必须提历史名，第一次出现时说明 `R-SLG` 是 broader grammar family，本文实例为 `PS-RSLG`。

## 1. 严格主故事版本

### 1.1 一段话版本

本文研究有限深度 recursive 3D asset growth：给定 root mesh 或 generated root asset、grammar program 和 depth budget，目标是在 frozen native 3D generator 的 mesh-derived sparse state 中反复执行结构规则，输出可渲染、可导出、可诊断的有限深度 3D asset。传统 L-system、IFS、space colonization 和 DLA 等 procedural systems 提供明确的递归结构控制，但通常停留在 scaffold、curve、tube、voxel 或手工 mesh 层面；现代 3D generative models 能生成丰富 one-shot assets，却通常不暴露一个可由 formal grammar 稳定反复读写的状态。PS-RSLG 把这两者连接起来：grammar 拥有 support、attachment、occupancy、frontier 和 transform semantics；frozen generator 提供 mesh-derived O-Voxel/SLAT representation、decoder、re-encoder、optional masked local naturalization 和 texture/export route。核心设计是把 decode -> component projection -> re-encode 放进每个 recursive step，从而抑制 disconnected fragments 在后续深度被当作新 growth roots 放大。

### 1.2 正式任务定义 v0.1

给定 root asset \(x_0\)、grammar program \(\mathcal{G}\)、有限深度预算 \(D\)、可选 condition \(y\) 和 frozen native 3D generator \(\theta\)，目标是生成有限状态序列

```tex
S_0 \xrightarrow{\mathbb{T}_{\mathcal{G},\theta,0}}
S_1 \xrightarrow{\mathbb{T}_{\mathcal{G},\theta,1}}
\cdots
\xrightarrow{\mathbb{T}_{\mathcal{G},\theta,D-1}} S_D,
\qquad
x_D = \mathcal{O}(S_D).
```

其中 \(S_d\) 是 mesh-derived sparse 3D latent state，\(\mathcal{O}\) 输出 mesh、OBJ/GLB、fixed-camera render 和 per-depth diagnostics。本文不要求无限深度，也不要求任意 grammar 都成功；核心目标是使 selected grammar programs 在有限深度内保持 connected、bounded、renderable，并能被同协议指标诊断。

建议英文定义：

```tex
We study finite-depth recursive 3D asset growth: given a root asset, a recursive grammar program, and a depth budget, the goal is to produce a sequence of renderable 3D assets whose geometry follows recursive structural rules while remaining connected, bounded, and usable as meshes or selected textured assets.
```

### 1.3 Problem statement v0.1

建议英文段落：

```tex
Modern 3D generative models can produce plausible one-shot meshes and textured assets, but their standard interface is not a stable program state for repeated recursive execution. Classical procedural systems provide this explicit recursive control, but typically require hand-designed geometry and surfacing to become modern assets. The missing interface is therefore neither a better prompt nor a final cleanup pass, but a recursive state operator that lets grammar rules modify a learned sparse 3D representation while projecting intermediate states back to an admissible asset space.
```

核心失败模式：

- 2D scaffold / line drawing / point cloud as image condition 容易产生 sheets、fragments、out-of-distribution geometry。
- Direct sparse coordinate copy / merge 会让小碎片存活，并在下一层成为合法 anchor。
- Final-only projection 可以改善最终 mesh，但不能阻止中间碎片影响 frontier、sampler condition、history 和后续 rule choice。
- Full global flow repair 可能抹掉 recursive scaffold，所以不能作为主解法。

建议关键句：

```tex
The central difficulty is not applying a procedural rule once, but iterating it inside a learned 3D representation: small disconnected components that survive one depth can be interpreted as valid anchors at the next depth.
```

```tex
This makes projection a state-transition requirement rather than a cosmetic post-process.
```

### 1.4 Method identity v0.1

最短方法公式：

```tex
S_{d+1}
=
E_\theta \circ P_{\lambda_d} \circ D_\theta
\circ \mathrm{Merge}_{\Pi_d}
\circ \mathrm{Rule}_{r_d}(S_d).
```

完整方法语义可写为：

```tex
S_{d+1}
=
\mathcal{C}_{d+1}\circ
\mathcal{E}_\theta\circ
\mathcal{P}_{\lambda_d}\circ
\mathcal{D}_\theta\circ
\mathcal{N}_{\theta,\Omega_d}^{\tau_d\rightarrow0}\circ
\Theta_{\Pi_d}\circ
\operatorname{Merge}_{B_d}\circ
\operatorname{Prop}_{R_d^\star}(S_d).
```

正文要解释清楚：

- \(\operatorname{Prop}\)：typed grammar rules 生成 transform-copy、frontier growth、branching、portal、scale-copy 等 sparse proposals。
- \(\operatorname{Merge}\)：support union 和 feature blending。
- \(\Theta_{\Pi}\)：occupancy、attachment、competition、collision、token budget 等约束。
- \(\mathcal{N}_\theta\)：可选 masked local naturalization，不拥有全局 scaffold。
- \(\mathcal{D}_\theta\)：decode candidate sparse state to mesh。
- \(\mathcal{P}_{\lambda}\)：component / attachment / renderability projection。
- \(\mathcal{E}_\theta\)：projected mesh re-encode，成为下一层 grammar 的输入。
- \(\mathcal{C}\)：cache / LOD / history update，目前主要作为 extension boundary。

### 1.5 论文一句话贡献定位

建议放在 Introduction 末尾 contributions 前：

```tex
This framing leads to three contributions: a recursive sparse-latent grammar formulation for finite-depth 3D assets, a projection-stabilized recursive operator that feeds projected meshes back into the sparse state at every depth, and a mesh-first evaluation protocol that separates recursive geometry stability from selected texture/PBR export.
```

## 2. 各 Section 中文注释大纲

下面的中文注释可以先进入审阅稿，之后再迁移到 `main.tex` 的 `%` 注释或写作大纲中。

### Abstract

```tex
% Abstract goal:
% 1. 用一句话说明 recursive structure 是 graphics assets 的核心，而 classical procedural systems 有显式控制但资产真实感和材质路径不足。
% 2. 用一句话说明 modern 3D generators 有 rich one-shot assets，但不是 stable substrate for repeated grammar execution。
% 3. 引入 PS-RSLG：training-free framework over mesh-derived O-Voxel/SLAT support and features from a frozen native 3D generator。
% 4. 说明 grammar 更新 support/features/anchors/masks/occupancy constraints，能表达 transform-copy, branching, frontier growth, space competition。
% 5. 点出核心设计：decode -> component projection -> re-encode at every depth。
% 6. 说明 evaluation：selected finite-depth programs，用 connectivity/component/renderability diagnostics 对比 direct recursion / final-only projection / baselines。
% 7. 明确 texture/PBR 只是 selected compatibility；material quality, non-tree generality, unbounded recursion remain open。
```

### 1. Introduction

```tex
% Intro goal:
% 1. 从 recursive structure in graphics assets 开场，不从 Trellis2 或工程实现开场。
% 2. 对比 classical procedural recursion 和 modern native 3D generation。
% 3. 提出 gap：one-shot 3D generation does not expose a stable repeated-growth state。
% 4. 解释 naive bridge failure：2D scaffold/image condition leads to sheets/fragments; global repair washes out topology。
% 5. 提出 insight：recursive generation should be a state operator; projection must be inside the recursive loop。
% 6. 概述 PS-RSLG：typed grammar rules over mesh-derived O-Voxel/SLAT state plus frozen generator decode/projection/re-encode。
% 7. 绑定 scope：finite-depth recursive assets, not infinite scenes, universal editing, or solved PBR。
% 8. 贡献列表必须绑定证据：grammar formalization, projection-stabilized loop, sparse occupancy competition / operator family, mesh-first evaluation。
```

建议段落顺序：

1. 递归结构是图形资产基础语言：plants, roots, vines, ornaments, porous forms, repeated architecture。
2. Procedural systems 有 explicit rules，但现代 asset appearance 和 learned representation 弱。
3. 现代 3D generators 有 one-shot asset quality，但缺 repeated grammar state。
4. Naive recursion in learned state 会 fragment propagation；final-only cleanup 不足；global flow repair 可能过度自然化。
5. PS-RSLG 方法概述和核心 loop。
6. Scope and evidence：selected finite-depth programs + mesh-first diagnostics。
7. Contributions。

### 2. Related Work

```tex
% Related work should be gap-driven, not chronological.
% Paragraph 1: Procedural recursion and growth grammars: L-systems, IFS, space colonization, DLA/frontier, shape grammar. Strength: explicit structure. Limitation for this paper: not learned sparse 3D asset states with decode/re-encode/texture path。
% Paragraph 2: Native 3D generation and sparse latent asset models: TRELLIS/TRELLIS2, AssetGen, Hunyuan3D, Shap-E, DreamGaussian, Objaverse. Strength: one-shot assets. Gap: not designed as repeated grammar substrate。
% Paragraph 3: Training-free editing and local repair: SDEdit/FlowEdit/native latent editing/inpainting. Gap: single edit or local completion, not recursive map where errors compound。
% Paragraph 4: Structure control / skeleton / point priors: relevant for structure-aware 3D generation but often learned adapters or one-step conditioning。
% Paragraph 5: World-scale / infinite generation: adjacent motivation; our paper is finite-depth assets and repeated-state stability。
% Paragraph 6: Recursive asset evaluation: connectivity, component stability, morphology, renderability, texture QA; image similarity alone is insufficient。
```

正式版 related work 写法建议见第 8 节。

### 3. Problem Definition and Grammar Semantics

```tex
% Define the task before the algorithm.
% Input: root mesh or generated root asset, grammar program, finite depth budget, optional condition/material intent。
% Output: finite-depth renderable mesh/OBJ/GLB plus fixed-camera renders and diagnostics。
% State: S_d = (C_d, F_d, U_d, A_d, B_d, M_d, H_d, K_d)。
% Grammar: G = (Sigma, T, R, I, S, Pi, N_theta, D_theta, E_theta, P, C, O)。
% Rule schema: typed symbol/frame -> transformed sparse proposals with masks, blend kernels, sampler schedule, local constraints。
% Important distinction: grammar owns support/attachment; frozen generator supplies representation, decoder, re-encoder, optional local prior and appearance route。
% Coverage table: IFS, L-system, space colonization, DLA/frontier, finite local shape grammar, symmetry/crystal, infinite/cache extension。
```

主文状态建议：

```tex
S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d,K_d).
```

其中：

- \(C_d\)：active sparse support。
- \(F_d\)：shape / optional material features。
- \(U_d\)：typed symbols and anchors。
- \(A_d\)：occupancy, attractors, frontiers, component/attachment graph, quality fields。
- \(B_d\)：masks and blend kernels。
- \(M_d\)：material intent / texture latent / naturalization schedule。
- \(H_d\)：depth, seed, rule trace, diagnostics。
- \(K_d\)：motif / latent / transform / LOD / window cache，当前主要作为 formal extension。

### 4. Method: PS-RSLG

```tex
% Technical core. Keep it concrete.
% 4.1 Mesh-derived sparse state: encode root mesh into O-Voxel/SLAT support and features。
% 4.2 Rule proposal: transform-copy, branching, frontier, portal, scale-copy, competition proposals。
% 4.3 Merge and occupancy competition: resolve candidate support under occupied cells, frontier scores, attachment, collision, token budget。
% 4.4 Optional masked local naturalization: only new/boundary regions; do not claim full flow repair preserves topology。
% 4.5 Projection-stabilized recursion: decode -> component/attachment projection -> re-encode before next depth。
% 4.6 Texture/export branch: final stable mesh can pass to texture/PBR export; evaluated separately。
```

必须强调：

- Method figure 不是线性 pipeline，而是 recursive loop。
- Projection / re-encode 的箭头必须回到 \(S_{d+1}\)。
- Texture/PBR branch 必须在 final output 侧边，不在每一步核心 loop 中。

### 5. Experiments

```tex
% Organize experiments by claims, not chronology.
% 5.1 Experimental setup: tasks, roots, grammar programs, depth budgets, mesh-first protocol。
% 5.2 Projection ablation: direct sparse recursion vs final-only projection vs per-depth projection。
% 5.3 Sparse occupancy competition: traditional space-colonization scaffold, direct competition, competition + projection, fork variants。
% 5.4 Baselines: procedural-only, one-shot generator, image-entry failure, direct grammar, full flow repair, masked weak blend, PS-RSLG。
% 5.5 Category breadth: selected finite-depth visual matrix under uniform Blender/Cycles protocol。
% 5.6 Texture/PBR compatibility: selected GLB export and texture QA table, separate from geometry stability。
% 5.7 Applications/preliminary extensions: ornament, portal/architecture, scale-down/zoom proxy, porous/frontier stress tests。
```

实验必须回答的问题：

1. Per-depth projection 是否比 direct / final-only 更能稳定递归状态？
2. 哪些 operator 当前足够稳定，哪些只是表达性 stress test？
3. Sparse occupancy competition 是否能作为 graphics-method contribution，而不是工程 trick？
4. 是否有 selected non-tree categories 支撑“recursive asset programs”而不是“植物小技巧”？
5. Texture/PBR 是否只是兼容路径，而不是遮盖几何问题？

### 6. Results and Analysis

```tex
% Results should be evidence-first.
% Start with projection table / figure because it proves central claim。
% Then show space competition because it is the strongest concrete operator。
% Then show baseline comparison to explain why mesh-first PS-RSLG is needed。
% Then show selected category matrix; fewer but cleaner is better than 30 weak tiles。
% Then show texture/PBR as compatibility and QA。
% Analysis paragraph should discuss stability-expression tradeoff: compete stable/conservative, fork/side/portal more expressive but fragile。
```

### 7. Discussion, Limitations, and Conclusion

```tex
% Limitations must be explicit and specific.
% finite-depth only; no true infinite streaming evidence。
% non-tree coverage remains uneven。
% texture/PBR quality category-dependent。
% projection can remove intentional small details。
% global flow repair can wash out recursive topology。
% transform/symmetry/equivariance behavior is empirical, not guaranteed。
% roots, camera, render protocol strongly affect visual quality。
% frozen generator biases are inherited。
% Conclusion should restate recursive generation as a stable state operator over sparse 3D latents。
```

Conclusion 要收在这个观点上：

```tex
PS-RSLG does not make a frozen generator universally recursive; it shows that recursive 3D generation can be made into a finite-depth state transition problem in sparse native-3D latents, with projection closing the loop between procedural structure and learned asset representation.
```

## 3. Abstract v0.1 英文逐句设计

以下不是最终 abstract，而是逐句设计稿。每句都绑定证据和风险。

### Sentence 1: Motivation

```tex
Recursive structure is central to many graphics assets, from plants and roots to ornaments, porous forms, and repeated architectural motifs, but classical procedural systems often trade modern asset realism for explicit structural control.
```

功能：建立 procedural recursion 的重要性和 limitation。  
风险控制：用 `often trade`，不要说 classical methods cannot produce realistic assets。

### Sentence 2: Gap in modern 3D generation

```tex
Conversely, recent 3D generative models produce rich meshes and textured assets, yet they are primarily one-shot generators and are not designed as stable substrates for repeated grammar execution.
```

功能：建立 frozen 3D generator 的互补缺口。  
风险控制：用 `primarily` 和 `not designed as`，不要绝对化。

### Sentence 3: Method

```tex
We introduce Projection-Stabilized Recursive Sparse-Latent Grammar (PS-RSLG), a training-free framework that runs typed recursive rules on mesh-derived O-Voxel/SLAT support and features from a frozen native 3D generator.
```

功能：给方法名、training-free、state substrate。  
风险控制：training-free 指不训练新模型，不暗示底层 generator 未训练。

### Sentence 4: Grammar capability

```tex
Grammar rules update sparse support, transported latent features, anchors, masks, and occupancy constraints, enabling transform-copy, branching, frontier growth, and space competition within a unified state transition.
```

功能：说明 PS-RSLG 不只是一个 projection trick，而是 grammar state semantics。  
风险控制：`unified state transition` 指语义统一，不代表所有 operator 实验同等强。

### Sentence 5: Key design

```tex
The key design is to make decode--component projection--re-encode part of every recursive step, reducing the chance that disconnected fragments propagate as future growth seeds.
```

功能：点出本文最强贡献。  
风险控制：用 `reducing the chance`，比 `preventing` 更稳。

### Sentence 6: Evaluation

```tex
Across selected finite-depth programs, including vines, tree-like growth, ornaments, transform-copy structures, and porous/frontier stress tests, we evaluate PS-RSLG with connectivity, component, and renderability diagnostics against direct sparse recursion, final-only projection, and procedural/generative baselines.
```

功能：说明实验范围和 baselines。  
风险控制：用 `selected finite-depth programs`；如果完整表未补齐，不写 `outperforms` 或 `improves` 太满。

### Sentence 7: Appearance and limitations

```tex
We further show that projected recursive geometries can be passed to a texture/PBR export pipeline for selected cases, while material quality, non-tree generality, and unbounded recursive streaming remain open limitations.
```

功能：展示 texture/PBR 兼容，同时主动限定。  
风险控制：必须保留 `selected cases` 和 `remain open limitations`。

### Abstract v0.1 连贯版

```tex
Recursive structure is central to many graphics assets, from plants and roots to ornaments, porous forms, and repeated architectural motifs, but classical procedural systems often trade modern asset realism for explicit structural control.
Conversely, recent 3D generative models produce rich meshes and textured assets, yet they are primarily one-shot generators and are not designed as stable substrates for repeated grammar execution.
We introduce Projection-Stabilized Recursive Sparse-Latent Grammar (PS-RSLG), a training-free framework that runs typed recursive rules on mesh-derived O-Voxel/SLAT support and features from a frozen native 3D generator.
Grammar rules update sparse support, transported latent features, anchors, masks, and occupancy constraints, enabling transform-copy, branching, frontier growth, and space competition within a unified state transition.
The key design is to make decode--component projection--re-encode part of every recursive step, reducing the chance that disconnected fragments propagate as future growth seeds.
Across selected finite-depth programs, including vines, tree-like growth, ornaments, transform-copy structures, and porous/frontier stress tests, we evaluate PS-RSLG with connectivity, component, and renderability diagnostics against direct sparse recursion, final-only projection, and procedural/generative baselines.
We further show that projected recursive geometries can be passed to a texture/PBR export pipeline for selected cases, while material quality, non-tree generality, and unbounded recursive streaming remain open limitations.
```

## 4. Contribution v0.1

主文建议三条贡献，最多四条。不要把 texture/PBR 单独写成主贡献。

### Contribution 1: Task and grammar semantics

```tex
We formulate finite-depth recursive 3D asset growth as typed grammar execution over mesh-derived sparse 3D latent states, including support, features, anchors, masks, occupancy fields, history, and optional cache state needed for repeated rule execution.
```

中文解释：这是 task / formalism contribution。可以在 Method 里用 coverage table 表示 IFS、L-system、space colonization、DLA-like frontier、finite local shape grammar、symmetry / crystal 是 degenerate or restricted instances。

安全补句：

```tex
The formulation subsumes several classical procedural families as finite-step rule patterns, but we do not claim equal empirical coverage for all of them.
```

### Contribution 2: Projection-stabilized recursive operator

```tex
We introduce a projection-stabilized recursive operator that interleaves sparse rule proposals with occupancy competition, mesh decoding, component projection, and re-encoding at every depth, reducing fragment propagation compared with direct recursion and final-only cleanup in our tested programs.
```

中文解释：这是核心算法贡献，应该排第一或第二。它必须绑定 projection ablation table / figure。

禁用写法：

- `guarantees stable recursion`
- `solves topology drift`
- `prevents all fragments`
- `general training-free 3D editing`

### Contribution 3: Sparse occupancy competition and operator family

```tex
We instantiate the grammar with sparse occupancy-competition growth and transform-copy/frontier operators, connecting classical space-colonization and recursive procedural rules to editable sparse O-Voxel/SLAT support.
```

中文解释：这条把 `compete` 从工程实现提升为 graphics-method operator。不要说它对所有类别最佳；应说 among tested operators, competition is the most stable。

安全补句：

```tex
Our results show a stability-expression tradeoff: conservative competition is stable across depth, while fork, side-branch, radial, and portal variants are more expressive but require stronger attachment and projection policies.
```

### Contribution 4: Mesh-first evaluation protocol

```tex
We provide a mesh-first evaluation protocol for recursive assets, including projection ablations, procedural and generative baselines, connectivity and renderability diagnostics, uniform visual matrices, and selected texture/PBR export checks.
```

中文解释：这是让论文不像 demo 的关键。实验表和 figure 必须按 claim 组织。

安全补句：

```tex
The experiments support finite-depth recursive asset growth, while high-quality material synthesis, broad non-tree robustness, and unbounded streaming recursion remain open.
```

## 5. Intro Opening v0.1

### Paragraph 1: Recursive structure as graphics language

```tex
Recursive structure is one of the oldest and most useful abstractions in procedural graphics. It gives artists and algorithms compact control over growth, repetition, branching, attachment, and scale. Trees branch through repeated local rules, roots and vines compete for free space, porous forms and corals accrete along exposed frontiers, and ornaments or architectural motifs repeat transformed copies across a surface or volume. Classical systems such as L-systems, iterated function systems, space colonization, and diffusion-limited aggregation expose this structure directly, but their outputs often remain procedural scaffolds unless substantial modeling, surfacing, and material work is added by hand.
```

功能：从 graphics asset 需求进入，不先讲 Trellis2。

### Paragraph 2: One-shot generators and missing state

```tex
Native 3D generative models have changed the asset pipeline by making plausible geometry and appearance available from compact conditions. However, their standard interface is still a single generation or localized edit rather than a repeated program state. For recursive assets, the missing interface is not only a better prompt. A grammar must be able to inspect, modify, decode, project, and feed a 3D state back into the next recursive depth.
```

功能：承认 modern generator 强，但指出 gap。

### Paragraph 3: Failure mode

```tex
Naively inserting procedural copies into a learned sparse latent is deceptively easy; iterating the operation is the hard part. Once a small disconnected component survives one depth, the grammar can treat it as a legitimate anchor at the next depth, amplifying a local artifact into a structural error. Final cleanup is therefore insufficient: invalid intermediate states may already have affected frontier selection, sampler conditions, and rule history before the last mesh is pruned.
```

功能：把 central problem 讲清。

### Paragraph 4: Method overview

```tex
We propose PS-RSLG, a projection-stabilized recursive sparse-latent grammar that treats a frozen 3D generator as a representation and local prior, while keeping structural ownership in the grammar. Each recursive step proposes sparse support and feature updates from typed rules, resolves occupancy and attachment constraints, optionally naturalizes local edited regions, decodes the candidate state to a mesh, projects it to an admissible connected asset, and re-encodes the result before the next rule fires.
```

功能：用自然语言讲 loop。

### Paragraph 5: Scope

```tex
Our scope is deliberately finite and asset-level. We target finite-depth recursive programs rather than unbounded scene synthesis, universal 3D editing, or solved material generation. Texture/PBR export is evaluated as an appearance compatibility path for selected projected meshes, while the main technical question is whether repeated grammar execution can remain stable in a frozen sparse 3D generative state.
```

功能：提前降低 overclaim。

## 6. Experiment Sections and Ablations Plan

### 6.1 Experimental Setup

目标：让所有实验围绕同一任务定义，而不是像日志。

必须写：

- Tasks：vine/root、tree/bush、ornament/crown、architecture/portal、hard-surface transform-copy、porous/frontier stress tests。
- Inputs：root mesh 或 generated root asset、grammar program、depth budget、optional material intent。
- Outputs：per-depth OBJ/mesh、optional GLB、fixed-camera Blender/Cycles renders、metrics JSON/CSV。
- Protocol：mesh-first；所有方法必须转为 traceable mesh/GLB 再评价。
- Metrics：connected components、largest-component ratio、fragmentation score、vertices/faces、bbox、depth success、render success、GLB/PBR import/export validity、visible holes/thin sheets/material mismatch。

建议关键句：

```tex
We use a mesh-first evaluation protocol: every compared method produces a traceable mesh or GLB before rendering and metric computation.
```

### 6.2 Projection Ablation: direct vs final-only vs per-depth

目标：证明 central claim。

方法：

- Direct sparse recursion：每层 rule/merge，不 decode/project/re-encode。
- Final-only projection：到 depth \(D\) 后一次 projection。
- Per-depth projection：每层 decode -> component projection -> re-encode。
- Optional：full flow repair、masked weak blend 作为 naturalization 对照。

指标：

- raw components per depth。
- projected / kept components。
- largest-component ratio。
- small-component count。
- vertices/faces before and after。
- re-encode success。
- render success。

结果写法：

```tex
Per-depth projection is not merely a final visual cleanup. It changes the state seen by the next recursive rule, so disconnected fragments are less likely to become future anchors.
```

风险控制：

- 如果 final-only 个别结果也不错，不写 final-only always fails。
- 写 `final-only lacks the per-depth invariant`，并用 intermediate state 曲线说明。

### 6.3 Space Competition: sparse occupancy competition as a method operator

目标：让 `compete` 成为 graphics contribution。

比较：

- Traditional space-colonization scaffold / tube mesh baseline。
- Direct sparse competition without projection。
- Competition + final-only projection。
- Competition + per-depth projection (PS-RSLG)。
- Competition+Fork / Side Fork 作为 expression boundary。

指标：

- attractor coverage。
- accepted support count。
- occupancy exclusion / collision violations。
- tip/frontier count。
- component stability。
- renderability。

应得结论：

```tex
Sparse O-Voxel support turns space competition into a native occupancy-exclusion rule inside the learned 3D state, while projection keeps accepted growth from being polluted by disconnected fragments.
```

### 6.4 Baselines

目标：避免 reviewer 认为只是 Trellis2 engineering demo。

Baseline groups：

- Procedural-only mesh：IFS / L-system / DLA / space-colonization scaffold。
- One-shot 3D generation：root or prompt/image-to-3D without recursive state。
- 2D scaffold / image-entry failure：仅作为 diagnostic，谨慎展示。
- Direct sparse grammar。
- Final-only projection。
- Full flow repair。
- Masked weak blend。
- PS-RSLG。

建议关键句：

```tex
The baselines are not intended to rank all 3D generators; they isolate failure modes relevant to recursive execution: missing structural control, fragment accumulation, final-only cleanup, and over-aggressive naturalization.
```

### 6.5 Category Breadth and Visual Matrix

目标：证明不是只会 vine/tree。

推荐正文矩阵：

- Row 1：Organic vine/root。
- Row 2：Tree/bush。
- Row 3：Ornament / architecture / portal / hard-surface transform-copy。
- Row 4：Porous / DLA / frontier stress tests。

图审美约束：

- 主矩阵统一 neutral material。
- 不混用 matplotlib preview 和 Blender/Cycles final render。
- 少而干净优于 30 个弱 tile。
- 每 tile 短标签：category, operator, depth。
- Textured GLB 用 star 或单独 figure 表示，不直接与 neutral matrix 混成同一质量证据。

### 6.6 Texture/PBR Compatibility

目标：展示 downstream route，而不是主 claim。

内容：

- Selected GLB export cases：vine/root、tree、crown/ornament、arch/scifi 中视觉过关者。
- 每个 case 同时给 neutral geometry render 和 textured render，避免 texture 掩盖 holes。
- QA table：GLB status、Blender import status、shape tokens、PBR tokens、base color / roughness / metallic / opacity status、visible holes/thin sheets/material mismatch、paper use。

建议关键句：

```tex
We evaluate texture/PBR as renderability compatibility rather than as a claim of universal material synthesis.
```

### 6.7 Applications and Preliminary Extensions

目标：展示潜力，但不支撑核心 claim。

可放：

- ornament/crown portal；
- architecture / arch portal；
- hard-surface translate；
- island-city / scale-down zoom proxy；
- porous / DLA stress tests。

写法：

```tex
These examples illustrate how the same state semantics can express transform-copy and zoom-like programs; they do not establish unbounded streaming recursion or camera-aware impossible geometry.
```

### 6.8 Limitations Section Plan

必须明确：

- finite-depth only；
- non-tree categories 仍不均衡；
- texture/PBR quality category-dependent；
- projection 可能删除有效小结构；
- global flow repair 会 wash out recursive scaffold；
- symmetry / crystal / portal equivariance 当前只是 conditional / empirical；
- mesh root quality 和 render protocol 对结果影响大；
- no retraining means inheriting frozen generator biases。

## 7. 哪些 Claim 现在不能写太满

### 7.1 可以作为主文安全 claim

- `finite-depth recursive 3D asset growth`
- `training-free use of a frozen native 3D generator`
- `mesh-derived sparse O-Voxel/SLAT state`
- `typed recursive grammar over sparse support/features`
- `projection-stabilized recursive map`
- `per-depth projection reduces fragment propagation in tested programs`
- `sparse occupancy competition is a stable operator among tested operators`
- `selected texture/PBR export compatibility`
- `coverage sketch / finite-step specialization of classical grammar families`

### 7.2 必须弱化或加限定的 claim

- `improves stability`：必须限定为 tested programs / selected finite-depth programs，并绑定 metrics。
- `supports non-tree assets`：写 selected ornament/architecture/hard-surface cases，不写 general。
- `texture/PBR works`：写 selected export compatibility，不写 material quality solved。
- `naturalization helps`：写 optional / mixed evidence / local masked design，不写 robust topology-preserving flow。
- `coverage of classical systems`：写 degenerate or restricted instances / finite-step patterns，不写 covers all grammars。
- `symmetry/crystal`：写 conditional approximate commutation，不写 guaranteed equivariance。

### 7.3 现在不应写的 claim

- `solves infinite recursive generation`
- `unbounded streaming recursion is demonstrated`
- `photorealistic recursive assets`
- `state-of-the-art 3D generation`
- `universal PBR texture synthesis`
- `general-purpose 3D grammar`
- `guarantees stable topology`
- `full flow/SDE repair preserves recursive topology`
- `Escher / impossible geometry is solved`
- `all classical procedural systems are empirically covered`
- `30+ result matrix proves broad generality`，除非最终统一 QA 完成。

### 7.4 最危险缺口

第一危险缺口：projection ablation 必须干净。同 root / operator / depth 下，no projection、final-only、per-depth 的 component counts、largest-component ratio、render results 要形成一张不可回避的 figure/table。

第二危险缺口：baseline fairness。Procedural-only、one-shot generator、direct sparse grammar、full flow repair、PS-RSLG 必须在相同任务定义和 render protocol 下比较。

第三危险缺口：non-tree visual breadth。Vine/root 很强，但如果 teaser 和 matrix 只有 tree-like assets，会被看作植物递归技巧；至少需要一个清晰 ornament/architecture/hard-surface result。

## 8. Related Work 正式版写作骨架

### 8.1 Procedural recursion and growth grammars

建议英文段落：

```tex
Procedural modeling provides the structural vocabulary for recursive assets. L-systems and botanical grammars describe branching structures through symbolic rewriting; iterated function systems formalize transform-copy self-similarity; space-colonization models generate branches by assigning attractors to competing tips; and diffusion-limited aggregation captures stochastic frontier accretion. These systems expose the explicit rules that recursive assets require, but their outputs are typically procedural geometry rather than learned sparse 3D asset states that can be decoded, projected, textured, and re-encoded. PS-RSLG preserves this structural vocabulary while moving the executable state into a mesh-derived sparse 3D representation.
```

### 8.2 Native 3D generation and sparse latent asset models

```tex
Recent 3D generative models synthesize meshes, implicit objects, Gaussian representations, and textured assets from images, text, or learned object priors. Sparse native-3D representations are particularly relevant because they provide a structured state that can be encoded from meshes and decoded back to assets. Our goal is complementary to one-shot 3D generation: we use a frozen generator as a representation, decoder, re-encoder, and optional appearance pipeline, while recursive structural control is handled by an explicit grammar state.
```

### 8.3 Training-free 3D editing and local repair

```tex
Training-free editing methods show that frozen generative models can be reused for local modification, inpainting, or preservation-naturalization without retraining. However, most such settings treat editing as a single operation. Recursive growth changes the problem: every intermediate artifact is exposed to future rule execution. This makes projection scheduling and state admissibility central components of the method rather than optional cleanup details.
```

### 8.4 Structure control and world-scale generation

```tex
Skeleton, point-prior, and structure-aware generation methods demonstrate the importance of explicit geometry constraints, while world-scale and unbounded scene generators study continuation across large domains. PS-RSLG addresses a narrower problem: finite-depth recursive assets inside a bounded sparse state. This narrower scope allows us to analyze how grammar rules, sparse support, projection, and re-encoding interact during repeated edits.
```

### 8.5 Evaluation

```tex
Recursive assets require diagnostics beyond image similarity. We therefore evaluate per-depth connectivity, component stability, branch or frontier preservation, occupancy and collision behavior, renderability, and selected texture/PBR export validity. Fractal or morphology descriptors can provide auxiliary signals, but they should not replace direct mesh and component diagnostics.
```

## 9. Conclusion v0.1

建议 conclusion 不要讲宏大愿景，回到 task 和 evidence：

```tex
We presented PS-RSLG, a projection-stabilized recursive sparse-latent grammar for finite-depth 3D asset growth in a frozen native 3D generative representation. The method treats recursive generation as repeated state transition: typed grammar rules propose sparse support and feature updates, occupancy and attachment constraints resolve growth, and each candidate is decoded, projected, and re-encoded before the next depth. This design makes projection part of the recursive semantics, reducing the propagation of disconnected fragments in selected programs. Our experiments should establish the resulting stability through projection ablations, space-competition growth, mesh-first baselines, and selected recursive asset categories. The current system remains limited to finite-depth assets; material quality, non-tree robustness, topology-preserving naturalization, and unbounded streaming recursion remain open. Even with these limits, PS-RSLG provides a concrete framework for combining procedural recursive control with frozen sparse 3D generative asset representations.
```

## 10. 立即写作优先级

1. 先改写 Abstract、Introduction、Contributions 和 Method opening，使全篇口径统一到 PS-RSLG / finite-depth / projection-stabilized。
2. 在 Method 前半部分正式定义 task、state、grammar tuple、rule schema 和 operational semantics。
3. Related Work 可以先写正式版，但必须围绕 repeated recursive state stability，不要泛泛罗列 3D generation。
4. Experiments 先按 projection ablation 和 space competition 组织，不要按实验时间线组织。
5. Figures 优先级：projection ablation table/figure > method loop figure > baseline comparison > selected visual matrix > texture QA。
6. Texture/PBR 和 zoom/Escher 放 secondary / applications / limitations，不要进入 abstract 的强 claim。

