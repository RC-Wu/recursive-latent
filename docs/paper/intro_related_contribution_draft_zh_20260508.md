# Intro / Related Work / Contributions 中文注释式草稿

日期：2026-05-08

写作范围：本文档是独立论文草稿，不修改 `paper_siga/main.tex`。目标是为 SIGGRAPH Asia 风格方法论文准备 problem statement、abstract、introduction、contributions、related work 和 experiments 组织草案。

核心写作约束：

- 主问题必须收窄为 **有限深度 recursive 3D asset growth**，不是无限递归、通用 Escher geometry、通用 3D editing 或已经解决的 PBR 资产生成。
- 方法名建议使用 **Projection-Stabilized Recursive Sparse-Latent Grammar (PS-RSLG)**。若正文沿用 P-RSLG，也应统一说明。
- 当前证据最强的是：mesh-derived sparse O-Voxel/SLAT state、per-depth projection、space competition/compete operator、selected finite-depth visual cases、部分 GLB/PBR 兼容性。
- 当前缺口必须明说：non-tree 类别不均衡，PBR 质量未成为主贡献，SDE/flow naturalization 仍是 optional/ablation，infinite zoom/cache 是 preliminary extension。

## 1. 任务定义与 Problem Statement

### 1.1 任务定义草稿

给定一个 root asset 或 root condition \(y\)、递归深度预算 \(D\)、语法程序 \(G\)，以及可选 material/texture intent，目标是生成一个有限深度、可导出、可渲染的 3D 资产序列：

```tex
S_0 \xrightarrow{G} S_1 \xrightarrow{G} \cdots \xrightarrow{G} S_D,
```

其中每个状态 \(S_d\) 是 mesh-derived sparse 3D latent state，而不是单纯的三角网格、2D 草图或一次性生成结果。最终输出包括 mesh/OBJ、可选 textured GLB、多视角渲染和每深度诊断指标。

建议正文定义：

```tex
We study finite-depth recursive 3D asset growth: given a root asset, a grammar program, and a depth budget, the goal is to produce a sequence of renderable 3D assets whose geometry follows recursive structural rules while remaining connected, bounded, and usable as meshes or textured assets.
```

证据依据：

- formal grammar 文档已定义 \(S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d)\) 和 \(G=(\Sigma,\mathcal{T},R,I,P,N_\theta,\Pi,\mathrm{Caches})\)。
- evaluation plan 已把任务拆成 structure-first recursive growth、multiscale refinement/infinite-zoom proxy、texture/PBR renderability。
- outline 明确建议主线为 frozen native 3D generative representation 中的 finite-depth recursive asset growth。

风险与边界：

- 不能写成“生成无限递归场景”或“任意深度稳定”，因为 cache/LOD 仅有 proxy 证据。
- 不能写成“通用 3D 编辑框架”，因为当前操作是 grammar-driven growth，不是开放文本编辑。
- 不能写成“高质量 PBR 已解决”，因为 textured GLB 只是 selected cases 兼容，质量类别相关。

### 1.2 Problem Statement 草稿

现代 3D 生成模型能产生局部自然、材质丰富的 one-shot assets，但它们通常不暴露一个可被程序递归规则反复读写的稳定状态。传统 procedural recursion，如 L-systems、IFS、space colonization、DLA 和 shape grammars，能提供清晰的递归结构控制，却往往缺少 learned 3D asset prior、局部自然化和现代 mesh/texture export pipeline。本文研究两者之间的缺口：如何在 frozen native 3D generative representation 中执行有限深度递归生长，使 procedural grammar 的可控结构与 learned sparse latent representation 的资产化能力相结合。

关键失败模式不是“单次生成不够漂亮”，而是“递归状态不稳定”。若每一步只做 sparse copy/merge，碎片、漂浮组件和局部拓扑错误会被后续规则继续当作新的递归根放大。若只在最终深度做一次 cleanup，很多中间状态已经不可恢复。若使用强全局 flow repair，则递归 scaffold 可能被自然化过程抹平。本文因此把 projection、competition、mask、decode 和 re-encode 放进递归算子本身，而不是放在最终后处理。

建议正文关键句：

```tex
The central difficulty is not a lack of procedural rules, but the instability of repeatedly applying such rules inside a learned 3D representation: small disconnected fragments and topology drift become new recursive roots unless the recursive operator itself projects intermediate states back to an admissible asset space.
```

```tex
Our problem is therefore to define and evaluate a recursive state operator over sparse 3D latents, where grammar rules control support, attachment, and competition, while a frozen 3D generator supplies representation, decoding, re-encoding, and optional local naturalization.
```

边界句：

```tex
We target finite-depth asset programs rather than unbounded scene synthesis, and treat texture/PBR export and infinite-zoom behavior as secondary capabilities rather than solved core problems.
```

## 2. Abstract 逐句草稿：句子、证据、风险

### Sentence 1

英文草稿：

```tex
Recursive structure is central to many graphics assets, from plants and roots to ornaments, porous forms, and repeated architectural motifs, but classical procedural systems often trade asset realism for explicit control.
```

证据：

- Related work 可引用 procedural recursion：`prusinkiewicz1990abop`, `lindenmayer1968lsystemsI`, `barnsley1988fractalsEverywhere`, `runions2007spacecolonization`, `witten1981dla`, `sander2000dlaReview`。
- 评估计划将树、藤、root、porous、architecture/ornament 都作为任务类别。

风险：

- “asset realism” 不要写成传统方法完全不能生成真实资产；应说 often trade 或 can require substantial hand modeling。

### Sentence 2

英文草稿：

```tex
Conversely, recent 3D generative models produce rich meshes and textured assets, yet they are primarily one-shot generators and are not designed as stable substrates for repeated grammar execution.
```

证据：

- bib 中有 `trellis2024`, `trellis2project`, `assetgen2024`, `hunyuan3d2025`, `dreamgaussian2023`, `shapE2023`。
- outline 明确 “3D generators are rich but one-shot and unstable under repeated recursion”。

风险：

- 不要声称所有 3D 生成模型都不能递归；措辞用 “primarily” 和 “not designed as”。

### Sentence 3

英文草稿：

```tex
We introduce Projection-Stabilized Recursive Sparse-Latent Grammar (PS-RSLG), a training-free framework that runs typed recursive rules on mesh-derived O-Voxel/SLAT support and features from a frozen native 3D generator.
```

证据：

- formal doc 已定义 typed sparse state、rule format、O-Voxel/SLAT support/features。
- outline 建议 “mesh-derived sparse O-Voxel/SLAT state” 和 “frozen Trellis2 decode/projection/re-encode”。
- Trellis/Trellis2 引用：`trellis2024`, `trellis2project`。

风险：

- “training-free” 只指本文方法不训练新的模型，不能暗示底层 generator 未训练。
- 如果实现主要是 Trellis2，应避免把 O-Voxel/SLAT 说成通用于所有 generator。

### Sentence 4

英文草稿：

```tex
Grammar rules update sparse support, transported latent features, anchors, masks, and occupancy constraints, enabling transform-copy, branching, frontier growth, and space competition within a unified state transition.
```

证据：

- formal doc rule format 覆盖 transform-copy、frontier、compete、fork、portal、radial 等。
- coverage sketch 可归约 IFS/L-system/space colonization/DLA/shape grammar/symmetry。

风险：

- “unified” 是语义框架统一，不是所有 family 都有同等强实验。
- symmetry/crystal 只能作为覆盖或次要实验，不能暗示已经鲁棒验证。

### Sentence 5

英文草稿：

```tex
The key design is to make decode--component projection--re-encode part of every recursive step, preventing disconnected fragments from propagating as future growth seeds.
```

证据：

- projection ablation 中 vine/tree direct vs final-only vs per-depth projection 有 component 数和 largest-component ratio 差异。
- outline 明确 central claim：projection suppresses fragment propagation。

风险：

- projection 不能保证 semantic correctness；只能说 preventing/suppressing disconnected fragments，或 “reduces the propagation” 更保守。
- 如果 reviewer 挑战 “preventing”，可改为 “substantially reducing in our tested programs”。

### Sentence 6

英文草稿：

```tex
Across selected finite-depth programs, including vines, tree-like growth, ornaments, transform-copy structures, and porous/frontier stress tests, PS-RSLG improves recursive stability under connectivity, component, and renderability diagnostics compared with direct sparse recursion and final-only projection.
```

证据：

- evaluation plan 的 baselines 和 metrics。
- progress report 中 vine/tree projection ablation 数字、space colonization baseline、non-tree/proxy cases。

风险：

- 必须写 “selected finite-depth programs”，不能写 broad generality。
- porous/frontier 应写 stress tests，不作为强主结果。
- “improves” 最终需要完整同协议表支撑；若未补齐，需要改成 “we evaluate” 或 “preliminary results indicate”。

### Sentence 7

英文草稿：

```tex
We further show that projected recursive geometries can be passed to a texture/PBR export pipeline for selected cases, while material quality, non-tree generality, and unbounded recursive streaming remain open limitations.
```

证据：

- progress report 记录 `tree_compete_s3/textured.glb` 和 `vine_d5_compete_s5_inference/textured.glb`。
- outline 明确 texture/PBR compatible for selected cases but not core solved problem。

风险：

- 这句必须保留 “selected cases” 和 “open limitations”，避免过 claim。

## 3. Introduction 段落级大纲与关键英文句子

### Paragraph 1：递归结构是图形资产中的基础形态

目标：从 graphics asset 的需求进入，不从模型架构进入。

内容：

- 植物、根系、藤蔓、珊瑚/孔隙、装饰纹样、建筑重复 motif 都依赖递归、分裂、吸附、尺度重复。
- 传统 procedural graphics 给出显式控制，但需要大量手工建模才能达到现代资产质量。

关键英文句子：

```tex
Recursive structure is one of the oldest and most useful abstractions in procedural graphics: it gives artists and algorithms compact control over growth, repetition, branching, and scale.
```

```tex
However, the same explicitness that makes classical grammars controllable often leaves the resulting geometry visually synthetic unless substantial modeling, surfacing, and material work is added by hand.
```

引用建议：`prusinkiewicz1990abop`, `lindenmayer1968lsystemsI`, `barnsley1988fractalsEverywhere`, `runions2007spacecolonization`, `witten1981dla`。

### Paragraph 2：现代 3D 生成模型补上 realism，但缺少递归状态

目标：建立 gap，不贬低生成模型。

内容：

- TRELLIS/TRELLIS2、AssetGen、Hunyuan3D、DreamGaussian 等模型推动 one-shot 3D asset generation。
- 它们提供 mesh、texture、PBR 或 structured latent，但 typical use case 是一次条件生成，不是程序递归执行。
- 用户如果想要“继续长出下一层结构”，需要一个可读写、可投影、可重编码的状态。

关键英文句子：

```tex
Native 3D generative models have changed the asset pipeline by making plausible geometry and appearance available from compact conditions, but their standard interface remains a single generation or edit rather than a repeated program state.
```

```tex
For recursive assets, the missing interface is not only a better prompt, but a stable state that grammar rules can inspect, modify, decode, and feed back into the next depth.
```

引用建议：`trellis2024`, `trellis2project`, `assetgen2024`, `hunyuan3d2025`, `dreamgaussian2023`, `shapE2023`。

### Paragraph 3：直接递归编辑 learned state 会失稳

目标：提出论文真正问题。

内容：

- Naive sparse coordinate copy/merge 会产生碎片、漂浮组件、collision、局部 topology drift。
- Final-only cleanup 不够，因为中间碎片会成为后续递归种子。
- 强全局 flow repair 又可能抹掉 scaffold。

关键英文句子：

```tex
Naively inserting procedural copies into a learned sparse latent is deceptively easy; iterating the operation is the hard part.
```

```tex
Once a small disconnected component survives one depth, the grammar can treat it as a legitimate anchor at the next depth, amplifying a local artifact into a structural error.
```

```tex
This makes final cleanup insufficient: the projection must be part of the recursive map rather than a cosmetic post-process.
```

证据建议：

- 引用 projection ablation 表：direct component explosion、final-only 保留少量 component、per-depth largest ratio 更高。

### Paragraph 4：PS-RSLG 方法概述

目标：用一段讲清方法。

内容：

- State：mesh-derived sparse O-Voxel/SLAT support/features + symbols/anchors/frontiers/masks/history。
- Rules：typed rewrite, transform-copy, branching, frontier, space competition。
- Loop：Rule proposal -> sparse merge/competition -> optional masked naturalization -> decode -> component projection -> re-encode。

关键英文句子：

```tex
We propose PS-RSLG, a projection-stabilized recursive sparse-latent grammar that treats a frozen 3D generator as a representation and local prior, while keeping structural ownership in the grammar.
```

```tex
Each recursive step proposes sparse support and feature updates from typed rules, resolves occupancy competition, decodes the candidate state, projects it to an admissible connected asset, and re-encodes the result before the next rule fires.
```

公式建议：

```tex
S_{d+1}=E \circ P_\tau \circ D \circ \mathrm{Merge}_{\Pi} \circ \mathrm{Rule}_{r_d}(S_d).
```

边界句：

```tex
The projection does not guarantee semantic correctness; its role is to bound a practical failure mode by preventing small fragments from becoming recursive roots.
```

### Paragraph 5：为什么 space competition 是主 operator

目标：把最稳实验变成方法贡献，而不是只做 case study。

内容：

- Sparse occupancy competition 自然对应 space colonization 的 attractor/tip/exclusion 思想。
- 它在 O-Voxel/SLAT support 上有清楚实现：frontier selection、attractor assignment、occupied-coordinate exclusion、candidate acceptance。
- 和 projection 组合后，在 vine/tree/root 等有限深度任务中最稳。

关键英文句子：

```tex
Among the rule families we test, sparse occupancy competition is the most stable growth operator because it gives every proposal a local spatial opponent: occupied support, competing frontiers, and projection all constrain where new recursive mass can survive.
```

引用建议：传统 counterpart `runions2007spacecolonization`，可结合 `raumonen2013treeModels` 作为 tree structure/scan modeling 背景。

风险：

- 不要说 compete 是所有类别最佳；应说 “among tested operators”。

### Paragraph 6：实验组织与 scope

目标：让 reviewer 预期正确。

内容：

- Main experiments：projection ablation、space competition、baselines、category matrix、texture/PBR selected export、applications/zoom。
- Explicit limitations：finite depth、selected categories、PBR 不作为主 solved problem。

关键英文句子：

```tex
We evaluate the method under a mesh-first protocol: every compared method produces traceable meshes, fixed-camera renders, and per-depth diagnostics rather than only preview images.
```

```tex
Our results support a narrower claim than general recursive generation: per-depth projection stabilizes selected finite-depth sparse-latent asset programs, with texture export and zoom-like applications remaining secondary capabilities.
```

### Paragraph 7：Contributions 过渡

目标：引出三条保守贡献。

关键英文句子：

```tex
This framing leads to three contributions: a grammar semantics for recursive sparse 3D latent states, a projection-stabilized recursive operator with sparse occupancy competition, and an evaluation protocol for finite-depth recursive assets.
```

## 4. Contributions 三条：避免 overclaim

### Contribution 1：递归 sparse-latent grammar 任务与语义

英文草稿：

```tex
We formulate finite-depth recursive 3D asset growth as a typed grammar over mesh-derived sparse 3D latent states, covering support, features, anchors, masks, occupancy fields, and history needed for repeated rule execution.
```

中文解释：

- 这是任务和方法语义贡献。
- 可以说 coverage sketch 包括 IFS、L-system、space colonization、DLA/frontier、shape grammar、symmetry/transform-copy。
- 不要说“完整统一所有 procedural modeling”。

保守补句：

```tex
The formulation subsumes several classical procedural families as rule patterns, but we do not claim equal empirical coverage for all of them.
```

### Contribution 2：per-depth projection-stabilized recursive operator

英文草稿：

```tex
We introduce a projection-stabilized recursive operator that interleaves sparse rule proposals with occupancy competition, mesh decoding, component projection, and re-encoding at every depth, reducing fragment propagation compared with direct recursion and final-only cleanup in our tested programs.
```

中文解释：

- 这是核心算法贡献。
- 强 evidence 是 projection ablation。
- 必须保留 “in our tested programs”。

避免写法：

- 不写 “guarantees stable recursion”。
- 不写 “solves topology drift”。
- 不写 “general training-free 3D editing”。

### Contribution 3：评估协议和 selected finite-depth evidence

英文草稿：

```tex
We provide a mesh-first evaluation protocol for recursive assets, including projection ablations, sparse space-competition comparisons, procedural and generative baselines, connectivity/renderability diagnostics, and selected texture/PBR and zoom-style applications.
```

中文解释：

- 这是实验组织贡献，不是把所有结果吹成全面胜出。
- texture/PBR 和 zoom-style applications 要放在 “selected” 和 “applications”。

保守补句：

```tex
These experiments support finite-depth recursive asset growth, while broader non-tree generality, high-quality material synthesis, and unbounded streaming recursion remain open.
```

## 5. Related Work 分组结构与 bib keys

写作原则：

- Related Work 不按时间罗列，而按 gap 合成。
- 每组末尾用一句话连接到本文。
- 只引用 `references.bib` 中已有 keys。缺少 Stiny/Gips、CGA split grammar、Hutchinson 等引用时，正文暂不强依赖，或后续补 bib 后再写。

### 5.1 Procedural recursion and growth grammars

要点：

- L-systems 和 ABOP：植物/分枝递归的符号 grammar 基础。
- IFS/fractal：transform-copy、自相似、contractive recursion。
- Space colonization：attractor-driven tree/root/vine growth，和本文 `compete` operator 直接相关。
- DLA/frontier：随机边界吸附和 porous/coral/crystal stress tests 的背景。

bib keys：

- `lindenmayer1968lsystemsI`
- `prusinkiewicz1990abop`
- `barnsley1988fractalsEverywhere`
- `runions2007spacecolonization`
- `witten1981dla`
- `sander2000dlaReview`
- `raumonen2013treeModels`（可用于 tree structure/modeling 背景，谨慎使用）

连接句草稿：

```tex
These systems provide the structural vocabulary we want to preserve, but their output is usually a procedural scaffold rather than a learned sparse 3D asset state that can be decoded, projected, textured, and re-encoded.
```

### 5.2 Native 3D generation and asset models

要点：

- 现代 3D generation 能从 text/image/prompt 生成 mesh、implicit、Gaussian 或 textured asset。
- TRELLIS/TRELLIS2 对本文最关键，因为 structured/native sparse latents 可作为 grammar 操作 substrate。
- AssetGen/Hunyuan3D 等强调 geometry+texture/PBR asset quality，是本文外观导出路径的相关背景。
- Objaverse/Objaverse-XL 是现代 3D asset 数据生态背景，不必展开过多。

bib keys：

- `trellis2024`
- `trellis2project`
- `assetgen2024`
- `hunyuan3d2025`
- `dreamgaussian2023`
- `shapE2023`
- `objaverse2023`
- `objaverseXL2023`

连接句草稿：

```tex
Our goal is complementary to one-shot 3D generation: we use a frozen native 3D generator as a representation, decoder, and optional appearance pipeline, but move recursive structural control into an explicit grammar state.
```

### 5.3 Training-free 3D editing, structural control, and local repair

要点：

- Training-free/native 3D editing 关注无需重训的局部编辑、latent editing、inpainting、mask-free 或 precise coherent editing。
- Skeleton/point prior methods关注结构条件控制。
- Flow/SDE editing 提供 local naturalization 思想，但在本文中只是 optional masked weak blend，不是主贡献。
- 本文差异：不是单次 edit，而是 repeated recursive map，错误会随 depth 放大。

bib keys：

- `nano3d2025`
- `voxhammer2025`
- `latte3d2025`
- `inpaintslat2025`
- `skadapter2026`
- `pointsTo3D2026`
- `flowedit2024`
- `sdeedit2021`

连接句草稿：

```tex
Unlike single-edit settings, recursive growth exposes each intermediate artifact to future rule execution, which makes projection scheduling and state admissibility central rather than optional cleanup details.
```

风险：

- `inpaintslat2025` bib year 是 2026、key 是 2025，写正文时只用 key，不在文中写错年份。
- `nano3d2025`, `voxhammer2025`, `latte3d2025`, `inpaintslat2025` 是未来/近期 arXiv 条目，最终 submission 前需要核验元数据。

### 5.4 Infinite/world generation and unbounded scenes

要点：

- Infinite worlds/unbounded 3D scenes 与本文 motivation 邻近，但本文不解决 unbounded world generation。
- SceneDreamer/CityDreamer/Infinigen/TRELLISWorld 可作为 “large/unbounded generation” 背景。
- 本文只把 cache/LOD/zoom 作为 preliminary extension，不把它设为主问题。

bib keys：

- `infinigen2023`
- `citydreamer2023`
- `scenedreamer2023`
- `trellisworld2025`

连接句草稿：

```tex
Unbounded world generation studies spatial scale and scene continuation; our scope is narrower, focusing on finite-depth recursive assets and the stability of repeated edits within a bounded sparse state.
```

### 5.5 Evaluation metrics for recursive assets

要点：

- Recursive assets 不能只看 image similarity；需要 connectivity、component stability、branch/tip structure、occupancy competition、renderability/PBR。
- Fractal dimension 可作为辅助，但 branching structures 的 fractal interpretation 有风险。
- Minkowski/topology metrics 可用于 porous/frontier/voxel occupancy stress tests。

bib keys：

- `cheeseman2022fractalCaution`
- `martinez2018minkowskiPorosity`
- `raumonen2013treeModels`

连接句草稿：

```tex
We therefore evaluate recursive assets through per-depth connectivity, component stability, branch/frontier diagnostics, topology proxies, and renderability checks, with fractal measures treated as auxiliary rather than decisive evidence.
```

## 6. Experiments 章节组织草稿

总原则：

- 实验按 claim 组织，不按实验时间线组织。
- 所有比较尽量使用同 root、同 depth、同 mesh/OBJ/GLB、同 Blender/Cycles render protocol。
- 明确报告失败：empty mesh、component explosion、GLB import fail、PBR channel invalid 都要进入表。

### 6.1 Experimental Setup：任务、状态、协议

应包含：

- Tasks：vine/root, tree/bush, ornament/crown, transform-copy architecture, porous/frontier stress tests, optional zoom/portal applications。
- Inputs：root mesh or image-to-mesh root, grammar program, depth budget, optional texture/material intent。
- Outputs：per-depth mesh/OBJ, optional GLB, fixed-camera renders, metrics JSON/CSV。
- Metrics：component count, largest-component ratio, fragmentation score, vertices/faces/bbox, branch/tip proxy, occupancy collision/exclusion, render success, GLB/PBR validity。

关键句：

```tex
We use a mesh-first evaluation protocol: every method is converted to a traceable mesh or GLB before rendering and metric computation.
```

### 6.2 Projection Ablation：direct vs final-only vs per-depth

目的：

- 验证核心 claim：projection 必须在递归 loop 内，而不是最终后处理。

比较：

- Direct sparse grammar：rule/merge 后不做 projection。
- Final-only projection：depth D 后一次 projection。
- Per-depth projection：每 depth decode -> component projection -> re-encode。
- 可选加入 full flow repair 和 masked weak blend 作为 naturalization 对照。

指标：

- component count per depth。
- largest-component vertex ratio。
- small component count。
- fragmentation score。
- mesh/render success。

应写结果方向：

- vine/tree 当前证据显示 per-depth projection 抑制 fragment propagation。
- final-only 可以改善最终连通性，但不能保证中间状态可用，且 topology 已可能不可恢复。
- direct recursion 容易产生 component explosion。

风险：

- 若结果表还不完整，正文用 “we observe” 并避免统计显著性语言。

### 6.3 Space Competition：sparse occupancy competition as growth operator

目的：

- 把 `compete` 从工程 trick 写成方法核心。
- 对比传统 space colonization scaffold 与 sparse latent competition + projection。

比较：

- Traditional space colonization baseline：`runions2007spacecolonization` 风格 skeleton/tapered cylinders。
- Direct sparse competition without per-depth projection。
- Final-only projection。
- Proposed PS-RSLG with per-depth projection and sparse occupancy competition。
- Optional `compete_fork` 作为 expressiveness/stability boundary case。

指标：

- attractor coverage。
- tip/frontier count。
- collision/exclusion success。
- accepted new support。
- component stability。
- visual renderability。

应写结论：

- Traditional baseline 给出清楚 scaffold，但 asset realism/material pipeline 弱。
- Proposed 方法在 selected vine/tree/root cases 中把 competition 的结构控制放入 learned sparse asset state。
- `compete_fork` 表达力更高但更不稳，用于分析 stability-expression tradeoff。

### 6.4 Baselines：procedural, one-shot, direct recursion, repair

目的：

- 回应 “baseline/metric 离方法远” 的批评。

Baseline groups：

- Procedural-only：IFS/L-system/DLA/space-colonization scaffold -> mesh -> render。
- One-shot 3D generation：Trellis2 or other generator from prompt/image/root condition。
- Direct grammar：sparse grammar without projection。
- Final-only projection。
- Full flow repair：强 repair，检查 topology washout。
- Masked weak blend：局部 naturalization，检查 Pareto tradeoff。
- Proposed PS-RSLG。

指标：

- structure fidelity。
- depth stability。
- mesh renderability。
- GLB/PBR optional success。
- visual matrix under fixed protocol。

关键句：

```tex
The baselines are not intended to rank all 3D generators; they isolate failure modes relevant to recursive execution: missing structural control, fragment accumulation, final-only cleanup, and over-aggressive naturalization.
```

### 6.5 Texture / PBR：selected compatibility, not main solved problem

目的：

- 展示 projected recursive geometries 可以进入 texture/PBR export pipeline。
- 明确 PBR quality 不是核心已解决问题。

内容：

- Selected true textured GLB cases：tree/vine 等。
- Neutral geometry render 与 textured render 并列，证明 texture 没有掩盖结构。
- PBR table：GLB export success, Blender import success, material assignment, base color valid, roughness/metallic/opacity valid, missing texture count, render warning。

关键句：

```tex
We evaluate texture/PBR as renderability compatibility rather than as a claim of universal material synthesis.
```

风险：

- 不要把 textured GLB 少数成功 case 写成 broad PBR asset generation。

### 6.6 Applications / Zoom：ornaments, portals, scale-down, infinite-zoom proxy

目的：

- 展示方法潜力，但不把 weak evidence 写成主 claim。

内容：

- Recursive ornament/crown。
- Architecture/portal/transform-copy。
- Island-city/scale-down or zoom panel。
- Porous/frontier stress tests。

写法：

- “illustrative applications” 或 “preliminary extensions”。
- zoom/infinite recursion 只说 bounded visible state / finite logical depth proxy。
- Escher 只说 proxy 或 camera-aware transform-copy future direction。

关键句：

```tex
These examples are intended to show how the same state semantics can express transform-copy and zoom-like programs; they do not establish unbounded streaming recursion or camera-aware impossible geometry.
```

### 6.7 Limitations：必须主动承认

建议列出：

- finite-depth only；无真正 infinite recursion/streaming cache 证明。
- non-tree/general category coverage 不均衡。
- PBR/texture quality category-dependent。
- projection improves connectivity but can remove small intentional details。
- strong flow repair may wash out recursive scaffold。
- current symmetry/portal/equivariant behavior is proxy-level。
- image-entry pipeline weaker than mesh-first root。

关键句：

```tex
PS-RSLG is a stability mechanism for finite-depth recursive sparse-latent programs, not a guarantee that every grammar, category, or material intent will produce a high-quality asset.
```

## 7. 当前写作缺口清单

- 需要把 `PS-RSLG` 与 `P-RSLG` 命名统一。
- 需要补完整同协议实验表，尤其是 projection ablation、space competition、baselines 三组。
- 需要确认 `references.bib` 中 2025/2026 arXiv 条目的元数据和最终可引用性。
- 如要正式讨论 shape grammar/CGA，应补相应 bib；当前 bib 中没有可直接引用的 Stiny/Gips 或 Muller CGA key。
- Abstract 第 6 句里的 “improves” 最终取决于完整 metrics 表；若实验未补齐，应改成更保守的 “we evaluate”。
- Texture/PBR 图必须配 neutral render，否则容易被质疑 texture 隐藏几何问题。
- Zoom/Escher 只能放 applications/future work，不能进入 main solved problem。

## 8. 可直接迁移到论文的短版 Abstract 草案

```tex
Recursive structure is central to many graphics assets, from plants and roots to ornaments, porous forms, and repeated architectural motifs, but classical procedural systems often trade asset realism for explicit control.
Conversely, recent 3D generative models produce rich meshes and textured assets, yet they are primarily one-shot generators and are not designed as stable substrates for repeated grammar execution.
We introduce Projection-Stabilized Recursive Sparse-Latent Grammar (PS-RSLG), a training-free framework that runs typed recursive rules on mesh-derived O-Voxel/SLAT support and features from a frozen native 3D generator.
Grammar rules update sparse support, transported latent features, anchors, masks, and occupancy constraints, enabling transform-copy, branching, frontier growth, and space competition within a unified state transition.
The key design is to make decode--component projection--re-encode part of every recursive step, reducing the chance that disconnected fragments propagate as future growth seeds.
Across selected finite-depth programs, including vines, tree-like growth, ornaments, transform-copy structures, and porous/frontier stress tests, PS-RSLG is evaluated with connectivity, component, and renderability diagnostics against direct sparse recursion, final-only projection, and procedural/generative baselines.
We further show that projected recursive geometries can be passed to a texture/PBR export pipeline for selected cases, while material quality, non-tree generality, and unbounded recursive streaming remain open limitations.
```

## 9. 本文档路径

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/paper/intro_related_contribution_draft_zh_20260508.md`
