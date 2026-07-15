# 当前论文 story-chain 中文审阅

日期: 2026-05-13

范围: 本审阅基于当前 `main.tex` 以及被主文显式 `\input` 的活动表格、2026-05-13 指标补充草稿和结构修订记录。本文档只评估论文叙事链、claim 边界、方法-实验对齐和审稿风险，不修改论文正文或表格。

## 0. 一句话总评

当前论文的核心 story 已经成立: 递归 3D 生成不是终端 mesh 美化问题，而是一个有限深度执行问题。PS-RSLE 的主张是把 frozen sparse latent 3D generator 变成一个可执行递归 substrate: 规则读 active handles, 提出 typed sparse edits, generator 只负责 admitted local edit 的 realized geometry, projection + codec re-entry 在每一层提交 root-attached 或 connector-certified 的 active state, 然后下一层规则只能读这个已投影状态。

最强证据也很明确: projection ablation 显示 final-only projection 可以改善 terminal occupancy LCR, 但不能修复 root reachability、orphan handles、handle survival 和 valid execution; per-depth projection 才是 state mechanism。论文现在的问题主要不是没有故事，而是压缩后有几处逻辑桥被省略，容易让审稿人把 PS-RSLE 误读成 “procedural scaffold + generator beautification + post-hoc cleanup”。正文必须持续强调: projection 是递归状态提交操作，不是最终几何清理; controlled resampling 是局部实现操作，不是状态合法性来源。

## 1. 核心问题、claim、task、贡献和完整逻辑链

### 1.1 核心问题

论文研究的核心问题是 finite-depth recursive 3D asset generation。对象不是一次性生成一个终端 3D asset, 而是通过多个 depth 的局部扩展形成 branching vegetation、frontier/accretion aggregates、crystals/lattices、copied motifs 等结构。

关键困难是 intermediate geometry 是 executable state。第 d 层的 branch、frontier、motif、connector、local edit region 可能在第 d+1 层被选择、复制、扩展或缓存。如果一个 detached fragment 仍被登记为 active handle, 它不是普通 artifact, 而会污染后续 derivation。

因此论文真正要解决的是:

- 如何在 frozen sparse latent generator 上定义递归程序状态;
- 如何让规则可以稳定读取这个状态;
- 如何在每层 local generation 后决定哪些 decoded support 和 handles 可以进入下一层;
- 如何避免 final cleanup 只能修终端几何、不能修执行历史的问题。

### 1.2 中心 claim

中心 claim 可以写成:

> PS-RSLE makes admissibility a per-depth execution invariant for finite-depth recursive 3D generation over frozen sparse latent generator states.

这个 claim 包含四个子命题:

- 递归程序需要 generator-coupled executable state, 不只是 terminal sample。
- sparse latent generator 提供 support/features/codec/local priors, 但不提供 recursive validity。
- typed handles + proposals 给规则一个可读写接口。
- per-depth projection + codec re-entry 把 decoded candidate 转成下一层可读 active state。

### 1.3 任务定义

当前主文任务定义是三类:

- branching assets: roots, tree crowns, vines, branch/fork structures;
- frontier-growth/accretion assets: coral-like aggregates, porous growth, DLA-inspired frontier growth;
- transform-copy assets: bismuth, pyrite/lattice, repeated motifs。

这个范围是合理的，但必须坚持有限深度、user-authored rules、frozen generator、fixed root/rule/depth/seed/projection policy/camera/render protocol。不能暗示自动发现任意对象的 root semantics, 也不能暗示物理生长、无限递归、watertight production assets。

### 1.4 贡献对齐

当前贡献三条基本对，但第二条把 “typed proposals” 和 “state-stabilization loop” 合在一起，导致贡献边界略糊。更清晰的贡献链应是四层:

1. 问题表述: finite-depth recursive 3D asset generation as execution over generator-coupled state。
2. 状态接口: sparse latent tokens + rule-readable handles for local frames, ownership, frontiers, attachments, motifs。
3. 执行机制: proposals/admission -> controlled resampling -> projection -> codec re-entry/remap。
4. 评估: procedural/generator/copy/projection/local-realization comparisons, separating state validity, connectivity, mesh diagnostics, visual/readability proxies。

这四层需要和 abstract、intro、method、experiments 一一对应。现在主文可读性最大的问题是: contribution 2 提到 “controlled sparse-latent sampling realizes local edits” 和 “projection commits support”, 但 Introduction 中没有充分铺垫 “local realization” 和 “state admissibility” 的分工; Experiments 中 local realization ablation 又容易被读成另一个主 claim。

### 1.5 全文逻辑链

推荐全文 logic chain:

1. 递归 3D asset generation 的对象是 repeated local expansion, 不是 one-shot terminal generation。
2. 递归中的中间几何会成为后续规则输入，所以需要 executable state。
3. classical procedural systems 有 explicit state, 但 surface/detail/natural local variation 需要大量 family-specific surfacing。
4. sparse latent 3D generators 有 learned local priors、sparse support、features、codec, 但没有 recursive state semantics。
5. 现有 editing/conditioning 能改当前对象，但不维护跨 depth 的 typed handles、ownership、frontier lifecycle。
6. PS-RSLE 引入 active handle state 和 proposal/admission 接口。
7. Controlled resampling 用 frozen generator 实现 admitted local edits, 但不决定什么能成为 state。
8. Projection 在 decoded domain 检查 root reachability 和 connector certificates, 保留可执行 support/handles。
9. Codec re-entry 把 projected geometry 回到 generator-native sparse state, Remap 恢复 handles。
10. 因为下一层只读 projected active state, admissibility 成为 per-depth invariant。
11. 实验证明 final-only cleanup 不能修 state failure; per-depth projection 修 root reachability/orphans/handle survival/valid execution。
12. 在这个 state 稳定前提下，masked local realization 改善局部 deterministic proxy metrics。
13. 结论收束到 finite-depth executor, 不扩展到物理、无限、watertight、perceptual superiority。

## 2. Abstract 中文翻译与逐句映射

### 2.1 中文翻译

原摘要句 1:

> We study finite-depth recursive 3D asset generation, where authored rules expand branches, frontiers, copied motifs, and local regions that must remain readable by later steps, while sparse latent 3D generators provide native support, token features, codec operations, and learned local priors.

翻译:

我们研究有限深度的递归 3D 资产生成。在这个任务中，人工编写的规则会扩展分支、前沿、复制 motif 和局部区域，而这些中间结构必须能被后续步骤继续读取; 同时，sparse latent 3D generator 提供原生 sparse support、token features、codec 操作和学习到的局部先验。

映射:

- Introduction 第 1-2 段定义 recursive generation 和 executable state。
- Related Work 2.1 对应 authored rules/classical recursive systems。
- Preliminaries 3.1 定义 finite-depth execution。
- Preliminaries 3.2 定义 sparse latent generator interface。

缺口:

- 摘要把 “must remain readable” 说得很强，但 Introduction 压缩后没有用具体 failure mode 说明 detached active fragment 为什么危险。建议在 Intro 加一句: if detached support remains active, it may become a parent/frontier/motif in later steps。

原摘要句 2:

> Projection-Stabilized Recursive Sparse-Latent Execution (PS-RSLE) adds the execution layer that turns decoded geometry into reusable executable state by wrapping a frozen sparse latent generator with active handles for local frames, ownership, frontiers, attachments, and motifs.

翻译:

PS-RSLE 增加了一个执行层: 它在 frozen sparse latent generator 外包一层 active handles, 用来表示 local frames、ownership、frontiers、attachments 和 motifs, 从而把 decoded geometry 转化为可复用的 executable state。

映射:

- Method 4.1 Program State 定义 `s_d=(u_d,r_d,A_d)`。
- handle 公式 `h_i=(sigma_i,T_i,Omega_i^own,Omega_i^tar,mu_i,b_i)` 对应 local frames/ownership/frontier/reuse metadata。
- Projection 4.5 解释 decoded geometry 到 state 的提交。

缺口:

- “turns decoded geometry into reusable executable state” 实际上是 projection + re-encode + remap 的结果，不只是 wrapping generator with handles。摘要句容易让人以为 handle layer 单独完成转换。正文需要持续说明 active handles 只有通过 projection/remap 后才 executable。

原摘要句 3:

> Rules emit typed proposals, controlled sparse-latent sampling realizes admitted local edits, and projection with codec re-entry commits root-attached or connector-certified support before the next rule fires.

翻译:

规则发出 typed proposals; controlled sparse-latent sampling 实现已经通过 admission 的局部编辑; projection 与 codec re-entry 在下一条规则触发之前提交 root-attached 或 connector-certified 的 support。

映射:

- Method 4.2 Rule Proposals and Admission。
- Method 4.3 Recursive Transition 和 Algorithm 1。
- Method 4.4 Controlled Sparse-Latent Resampling。
- Method 4.5 Projection 和 Appendix Operational Projection Routine。
- Experiment 5.4 Projection ablation 是这句话的主要证据。

缺口:

- 4.4 目前公式层面比较细，但和实验 local realization 的连接需要更显式: resampling 的作用是 local surface/readability, projection 才是 state validity。
- `connector-certified` 在 Method 中需要有 operational certificate 条件，当前写了 endpoint attachment/mask/collision/budget, 但公式化程度有限。可以接受，但不要把 connector-aware projection 写成任意 bridge optimizer。

原摘要句 4:

> With frozen Trellis2, PS-RSLE stabilizes per-depth executable state, spans branching, frontier-growth, and transform-copy assets, retains procedural-level connectivity under tolerance-based surface metrics, and improves welded mesh fragmentation and rendered local readability.

翻译:

在 frozen Trellis2 上，PS-RSLE 稳定了逐层 executable state, 覆盖 branching、frontier-growth 和 transform-copy assets, 在 tolerance-based surface metrics 下保持 procedural-level connectivity, 并改善 welded mesh fragmentation 和 rendered local readability。

映射:

- Experiment 5.2 traditional comparison: surface r1 components, welded components。
- Experiment 5.3 generator/mesh-space comparison: occupancy components/LCR, welded comps/open edges。
- Experiment 5.4 projection ablation: root reachability/orphans/handle survival/valid exec。
- Experiment 5.5 local realization: roughness/normal/artifacts/deterministic proxy score。

风险:

- “retains procedural-level connectivity” 要限定在 tolerance-based surface metrics 和 reported finite-depth benchmarks。传统 procedural 的 structure 很强，表中 Space colonization traditional surface r0/r1 都是 1, 但 welded comp 是 627; PS-RSLE r0 是 6, LCR 0.996, r1 是 1, welded 是 1。这个结论必须说成 “under radius-one/tolerance surface metric and mesh fragmentation diagnostics”, 不能说全面结构优于 procedural。
- “rendered local readability” 当前主要来自 deterministic proxy metrics 和 selected figures, 不是 human preference 或 perceptual score。

## 3. Introduction 段落逻辑与压缩后的缺失桥

当前 Introduction 有 5 个主要段落:

1. 任务对象: finite-depth user-controlled programs, examples, Fig. natural structures。
2. 核心要求: recursive generation is an execution problem; executable state。
3. classical procedural systems 提供 structural side。
4. sparse latent generators 提供 complementary realization strength。
5. PS-RSLE solution + experiments + contributions。

整体顺序正确，压缩后更干净，但有几个桥需要补强。

### 3.1 从自然结构到任务定义的桥

当前开头列举 branching vegetation, accretive aggregates, crystals, lattices, repeated motifs。它说明了 breadth, 但尚未明确 “这些不是物理模拟目标，而是 asset task families”。审稿人可能攻击 DLA/coral/crystal 是否物理真实。

建议在 Intro 或 Experiments 5.1 加边界句:

> We use DLA-, coral-, and crystal-inspired families as recursive asset structures, not as physical growth or crystallization simulations.

### 3.2 从 executable state 到 sparse generator 的桥

当前第 2 段说 executable state must remain editable/addressable/attached/iterable。第 3-4 段说 classical 和 sparse latent generator 互补。缺少一句解释: sparse latent generator 的 native state 为什么不能直接当 executable state。

需要补:

> Native sparse support and features are useful carrier variables, but they do not by themselves identify which support is a parent, frontier, connector, reusable motif, or invalid orphan.

这句能直接引出 active handles。

### 3.3 从 editing/control 到 PS-RSLE 的桥在 Intro 中缺席

Related Work 2.4 讨论 editing/control, Intro 没有提。可以不加长，但至少在 Intro solution 前加一句:

> Local editing or masked generation can modify a current object, but does not define a lifecycle for handles across recursive depths.

这会防止审稿人说这只是 3D editing/inpainting 的组合。

### 3.4 Contribution 与 Introduction 的 alignment

Introduction 末尾实验 claim 写:

> sparse-latent execution gives stronger recursive connectivity than one-shot or copy-based generator controls

这个说法对 Experiment 3 成立，但 “stronger recursive connectivity” 需要强调 one-shot 没有 recursive state。否则 Trellis2 one-shot 在 bismuth LCR=1.000, pyrite LCR=0.999, 会被拿来反问为什么 one-shot 不够。

建议改成:

> one-shot generation can produce connected terminal samples, but it does not expose reusable recursive state; copy-based controls expose repetition but fragment under mesh/occupancy diagnostics.

## 4. 贡献与 Abstract/Intro/Method/Experiments 的一致性

### 4.1 贡献 1

贡献 1: generator-coupled program state。

对齐良好:

- Abstract 句 1-2。
- Intro executable state。
- Preliminaries finite-depth programs。
- Method 4.1 `s_d=(u_d,r_d,A_d)`。

风险:

- `r_d` root descriptor 在 Method 中定义得较正式，但没有明确 “authored/provided, not inferred”。如果不澄清，审稿人会问任意 mesh 的 root 怎么来。

### 4.2 贡献 2

贡献 2: typed active-handle proposals + per-depth state-stabilization loop。

对齐部分良好:

- Method 4.2 定义 proposals。
- Method 4.3 定义 transition。
- 4.4/4.5 实现 loop。

风险:

- Contribution 把 proposal semantics 和 projection loop 混成一条。正文中 4.2 的 admission gates 比较抽象，`Gamma_d` 的 certificate 内容在 4.5 prose 中才出现。建议在 review 文档后续改正文时让 4.2 明确列 gates: budget, collision, mask, ownership, connector feasibility。

### 4.3 贡献 3

贡献 3: instantiate on frozen generator and evaluate against controls。

对齐良好:

- Experiments 5.2 procedural controls。
- 5.3 generator/copy controls。
- 5.4 projection ablation。
- 5.5 local realization ablation。

风险:

- 当前 `Metrics` 段说 “deterministic proxy score” 和 “artifact score”, 但没有在主文定义质量分数的计算方式。若保留这些指标，需要 appendix 或 caption 明确是 deterministic proxy, not perceptual/human preference。
- Experiment 3 表中 PS-RSLE pyrite occupancy components = 3, LCR=1.000。主文写 “PS-RSLE returns one occupancy component on tree crown, bismuth, and coral, and three on pyrite, with LCR equal to 1.000 in all four cases。” 这很诚实，但摘要 “retains procedural-level connectivity” 必须允许 pyrite 3 components 的 nuance。

## 5. Related Work 角色与 transition

Related Work 当前分四块，角色基本合理:

- 2.1 Procedural Recursive Modeling: 说明 explicit recursive state 的来源和强 baseline。
- 2.2 Learned Structure and Programmatic Shape Generation: 说明 explicit hierarchy/programs 在 learned shape 中也重要。
- 2.3 Native 3D Generation and Sparse Latent 3D Generators: 说明 frozen generator 的 substrate 能力。
- 2.4 Sparse Editing and Structure-Conditioned Control: 说明 local control 可用，但不是 recursive executor。

### 5.1 2.1 的角色

2.1 不应把 procedural systems 写成弱 strawman。当前句子 “PS-RSLE keeps these explicit symbol, frontier, and transform contracts while coupling rule proposals to a learned sparse-latent realization substrate” 是正确的。

建议 transition:

- procedural systems are structural references, not defeated old methods;
- PS-RSLE borrows their state contracts and changes realization substrate。

### 5.2 2.2 的角色

2.2 目前较短，作用是把 “learned + explicit structure” 合法化。它可以更明确地区分 family-specific learned programs 与 user-authored finite-depth rules:

- GRASS/StructureNet/ShapeAssembly learn structure models from object families。
- PS-RSLE executes authored local rules through a frozen generator and keeps state reusable。

当前文字已基本满足。

### 5.3 2.3 的角色

2.3 是 PS-RSLE substrate 的来源。要注意 “Sparse Latent 3D Generators expose token support...” 这一句是对 Trellis/Trellis2 的能力描述。若审稿人质疑 “expose” 的具体程度，Method 3.2 应给出 abstract interface, 而不是暗示所有 generator 都可 drop-in。

边界建议:

> We assume access to sparse support, token features, codec operations, and a native local sampling/update path.

### 5.4 2.4 的角色

2.4 目前结尾很好:

> PS-RSLE uses this local control inside a recursive executor...

但可进一步强调 transition:

- editing/control 的单位是 current edit;
- PS-RSLE 的单位是 executable state transition。

这是防止 “incremental 3D editing” 攻击的关键。

## 6. Preliminaries 与 Method 逻辑、符号一致性风险

### 6.1 Preliminaries 3.1

当前定义:

`s_{d+1}=Step(s_d,R_d,xi_d), x_D=Output(s_D)`

作用清晰: 先抽象地定义 finite-depth execution, 再在 Method 4.1 实例化 state。

风险:

- `R_d subset R` 与 Method 中 `mathcal R`/`Propose(s_d, mathcal R)` 可接受，但建议统一说明 `R_d` 是 selected rule set。
- `xi_d` 后文不再出现。它可作为 stochastic choices, 但若压缩进一步加强，可能删除或在 `psi_d, epsilon_d` 处映射。

### 6.2 Preliminaries 3.2

当前定义:

- `u=(V,F)`;
- `V subset delta_g Z^3`;
- `F:V -> R^q`;
- `Enc_theta`, `N_theta`, `Dec_theta`;
- `Resample_theta` 是 masked/anchored use of `N_theta`;
- `FM_theta` 是 Trellis2 flow-matching instantiation。

这为 4.4 打基础。主要符号风险:

- `F` 同时可能和 figures 或 feature notation 无冲突，但应持续表示 token features。
- `\widehat u` 在 3.2 表示 generator output, 4.3 用 `\bar u` 表示 resampled latent。可接受，但要避免 `u^\theta`、`\widehat u`、`\bar u` 三者含义混淆。
- `delta_g` 后文没有回到 grid discretization，4.4 有 transformed coordinates rounded to sparse-grid locations。可以保留。

### 6.3 Method 4.1 Program State

当前 state:

`s_d=(u_d,r_d,A_d)`, `u_d=(V_d,F_d)`, `r_d=(T_root,V_root,U_root,beta)`, handle `h_i=(sigma_i,T_i,Omega_own,Omega_tar,mu_i,b_i)`。

逻辑是完整的:

- `u_d` 是 generator-native sparse state;
- `r_d` 是 root anchor;
- `A_d` 是 rule-readable handles;
- active flag `b_i` 控制 lifecycle;
- admissible set `S_adm(lambda_d)` 定义 active owned support must be attached or connector-certified。

符号/逻辑风险:

- `C_d^{com}` 在 admissibility 公式中出现，但不是 state tuple 的显式成员。它被 prose 说成 committed connector support certified during previous projection。审稿人可能问它存在于哪里。建议将它放入 `mu_i`/`r_d`/projection metadata, 或在 state tuple 加 metadata `m_d`。如果不改公式，至少写 “stored in handle/root metadata”。
- `V_d^{att}` 用 token support graph `G_eta(V_d)` 定义; 4.5 projection 又在 decoded domain 用 `U^{att}`。这是合理的双域定义，但要持续解释 `V` 是 sparse token support, `U` 是 decoded sampled/voxel support。
- `operatorname{path}_{G_eta(V_d)}(v,V_root)` 不是标准函数。可读，但数学严谨性上建议定义 “there exists a path in graph...”。
- `owner(Omega_i^own) is unique` 中 owner 函数未定义。可以作为 prose-level constraint, 但公式可能被攻击过于形式化。

### 6.4 Method 4.2 Rule Proposals and Admission

当前 proposal:

`p_j=(Delta V_j, Delta F_j^seed,H_j,mu_j)`。

逻辑:

- rules read `A_d^act`;
- emit local support edits and feature seeds;
- admission resolves conflicts, writes accepted metadata, records `Gamma_d`。

缺口:

- “Deterministic admission orders proposals, resolves mergeable conflicts...” 太快。它没有列出 admission gates, 但 Figure caption 提到 budget/collision/mask/connector/ownership。
- `H_j` 和 `\widetilde A_{d+1}` 的关系没有展开。建议说明 `H_j` contains proposed child/frontier/motif handles that become tentative active handles only after admission and projection。

### 6.5 Method 4.3 Recursive Transition

当前 transition sequence 很清楚:

1. `Propose`;
2. `AdmitApply`;
3. `Resample_theta`;
4. `Dec_theta`;
5. `Pi_lambda`;
6. `Enc_theta`;
7. `Remap`;
8. `s_{d+1}`。

这个是全篇最重要的 chain。建议在正文中把一句话加粗思路:

> Later rules never read `x_{d+1}` directly; they read only `A_{d+1}^{act}` after projection, re-encoding, and remapping.

符号风险:

- `V_{d+1}` 在 `Remap(...,V_{d+1})` 中由 `u_{d+1}=Enc(...)` 产生，但公式行没有显式写 `u_{d+1}=(V_{d+1},F_{d+1})`。可接受，但 reviewer 可能挑。
- `\kappa_{d+1}: U^* -> V_{d+1}` 在 projection 中被说成先返回，但 `V_{d+1}` 是 re-encoding 后才产生。更严谨地说 projection returns decoded correspondence data, and re-encoding instantiates `kappa`/or `Remap` computes it after `Enc`。当前写法有时间顺序问题。

## 7. 重点: Sections 4.4 Controlled Resampling 与 4.5 Projection

### 7.1 4.4 Controlled Sparse-Latent Resampling 的逻辑

4.4 的角色应该非常窄:

- Admission 已经决定哪些 sparse support edits 可以尝试。
- Frozen generator 的 native flow sampler 在 editable mask 内更新 token features。
- Anchors/boundary tokens 被 hard-clamped。
- Optional copied motif correspondence 复用 source context/features/KV。
- Decode 得到 candidate geometry。
- Candidate 仍未成为 executable state; projection 决定 state validity。

当前正文符合这个方向，但有几个公式关注点。

### 7.2 4.4 公式关注点

公式:

`du_t/dt = v_theta(u_t,t,y)`

风险:

- `u_t` 此处是整个 sparse latent state 还是 features only? 下一句说 implementation freezes admitted support and updates token features。若 `u_t` 包含 support `V`, ODE 写法会让人以为 support 连续演化。建议注明 flow is applied to token features on fixed admitted support in this implementation。

公式:

`u^\theta_{d+1}=(V^\theta_{d+1},F^\theta_{d+1})=FM_theta(\widetilde u_{d+1};y,\psi_d)`

风险:

- 前文说 controlled resampling freezes admitted support `\widetilde V_{d+1}`, 但这里又引入 `V^\theta_{d+1}`。随后 `\bar u=(\widetilde V,\bar F)`。若 support frozen, `V^\theta` 应该等于或 correspond to `\widetilde V`。否则 `chi(v)` 的 nearest correspondence 看起来是在弥补 support mismatch。
- 建议改成: `F^\theta_{d+1}=FM^F_theta(\widetilde V_{d+1},\widetilde F_{d+1};...)` 或明确 `V^\theta` is used only for correspondence when the native sampler returns a sparse support。

公式:

`\bar F(v) = \widetilde F(v)` outside `M_d`, blend inside。

风险:

- 如果 `M_d` 是 editable sparse region, `B_d` anchors hard-clamped by `alpha_v=0` for `v in B_d`。但 `B_d` 是否必然 subset of `M_d`? 若不是, outside M 已经 clamp; 若是, clamp 在 editable 内覆盖。建议说明 `B_d` may intersect `M_d`; anchors always override blend。

公式:

`KV_{d+1}(v) <- (1-gamma) KV^theta(v) + gamma KV^src(pi(v))`

风险:

- `KV` 没有在 Preliminaries 中定义。它是 implementation detail, 可能引发 “where do keys/values come from in Trellis2?” 的攻击。
- 如果保留，建议降为 prose: implementation may blend cached token features or attention context where available。不要把未定义的 KV 作为核心公式。

### 7.3 4.4 与实验 linkage

4.4 对应 Experiment 5.5 Local Realization:

- rule-only / masked-no-proj / no-realization+proj / blend+proj / masked+proj / global+proj。
- 结果显示 projection 先把 handle survival 提到 1.000; masked+proj 在 deterministic proxy score 0.807 最高, roughness 13.92, normal 0.669, artifact 0.227。

安全解释:

- masked local realization 是 surface/local readability component;
- 它依赖 projection-stabilized state;
- 它不是 topology repair, 不是 global semantic fix, 不是 human-perceptual superiority。

攻击点:

- global/+proj normal consistency 0.677、roughness 13.58 比 masked/+proj 更好，但 deterministic proxy score 0.735 低。需要解释 deterministic proxy score weighting 或谨慎说 masked is preferred by reported deterministic proxy score, while global is smoothest on surface metrics。
- rule-only 和 masked/no-proj valid exec 都是 0, 说明没有 projection 时 resampling 没救 state。这应作为正面证据讲清楚。

### 7.4 4.5 Projection 的逻辑

4.5 是方法核心:

1. 输入 decoded realization `x_{d+1}`, tentative handles, previous state, certificates, thresholds。
2. 在 decoded domain sample/voxelize 得到 `U`。
3. 从 persistent root descriptor instantiate root seeds `U_root`。
4. 构造 `G_eta(U)`。
5. 求 `U_att` root-reachable support。
6. 结合 connector certificates 形成 eligible active support。
7. child/frontier/connector/motif handles 只有满足 attachment/ownership/frontier/budget 才 survive。
8. 得到 `U^*`, `\widehat A`, correspondence。
9. Re-encode 得到 `V_{d+1}`。
10. Remap handles, 下一层读 active subset。

这条链非常强，应在正文突出。当前 4.5 写得可用，但有三类风险。

### 7.5 4.5 公式与实现关注点

风险 1: `kappa_{d+1}:U^* -> V_{d+1}` 的先后顺序。

正文说 projection first produces `kappa:U^* -> V_{d+1}`; re-encoding yields `V_{d+1}`。严格说 `V_{d+1}` 在 re-encoding 后才存在。建议改成 “projection returns correspondence data used to construct kappa after re-encoding” 或把 `Enc` 嵌入 projection。

风险 2: connector-certified support 过于抽象。

主文说 certificates satisfy endpoint attachment, mask validity, collision clearance, budget tolerances。这个够作为 high-level method, 但如果 claim connector-aware projection 很强，审稿人会问 connector 如何构造、是否 bridge arbitrary gaps。必须限制:

- connector support must be rule-certified during admission;
- projection does not invent arbitrary bridges;
- connector-aware row tests declared connector certificates, not unconstrained topology repair。

风险 3: root descriptor 来源。

`U_root` from persistent root descriptor。必须说明 root descriptor 由 authored program/root asset manifest 给定，不是自动语义识别。否则 root reachability metric 可能被质疑为 oracle。

### 7.6 4.5 与 projection ablation linkage

Projection ablation 表是全篇最强证据:

- no projection: Occ LCR 0.898, Root reach 0.504, Orphans 3.667, Handle survival 0.504, Valid exec 0。
- final-only: Occ LCR 0.995, Root reach 0.504, Orphans 3.667, Handle survival 0.504, Valid exec 0。
- per-depth prune-only: Root reach 1, Orphans 0, Handle survival 0.782, Valid exec 0.25。
- per-depth connector-aware: Root reach 1, Orphans 0, Handle survival 1, Valid exec 0.75。
- PS-RSLE: all state metrics 1/0 as desired, Valid exec 1。

这说明:

- final-only projection repairs terminal geometry proxy but leaves state lineage broken;
- per-depth projection is necessary for executable state;
- connector-aware projection preserves handles better than prune-only;
- full PS-RSLE closes remaining valid execution gap。

注意 `projection_admissible_state_proxy_summary_20260513` 中又给出 medians and strict pass:

- no/final-only strict pass 0/12, median root reach 0.629, orphan active 2.5, handle survival 0.629。
- per-depth connector-aware strict pass 9/12, PS-RSLE 12/12。

如果正文想引用这个补充表，应明确是 deterministic proxy audit, not runtime Trellis handle graph proof。

## 8. Experiment section 逻辑与可用结果

### 8.1 5.1 Experimental Setup

当前 5.1 包含 Tasks、Baselines、Metrics。逻辑正确但过短。建议明确:

- 每个任务固定 root, rule family, depth, seed, projection schedule, renderer/camera。
- evaluation separates recursive-state validity from terminal mesh/visual quality。

Metrics 段要更审慎:

- occupancy/surface LCR 是 connectivity proxy;
- root reachability/orphan handles/handle survival/valid execution 是 state proxy;
- welded components/open edges/roughness/normal/artifact/quality 是 mesh/local-realization diagnostics;
- deterministic proxy score 不是 perceptual human preference。

### 8.2 5.2 Traditional procedural comparison

主文结论:

- Traditional controls retain explicit structure。
- PS-RSLE adds generator-realized surface detail/natural appearance。
- Across four families, PS-RSLE outputs single connected support under radius-one surface metric。
- PS-RSLE reduces welded fragmentation in space-colonization, L-system, IFS; DLA both one welded component。

表格支持:

- Space colonization: Traditional r1=1, welded=627; PS-RSLE r1=1, welded=1。
- L-system: Traditional r1=1, welded=508; PS-RSLE r1=1, welded=9。
- DLA/frontier: both r1=1, welded=1。
- IFS/transform: Traditional r1=1, welded=15; PS-RSLE r1=1, welded=1。

安全 claim:

- Under tolerance-based surface connectivity, PS-RSLE matches procedural support connectivity in these rows while improving welded fragmentation diagnostics in three families。

不安全 claim:

- PS-RSLE is structurally better than procedural modeling。
- PS-RSLE universally outperforms L-systems/space colonization。
- Procedural baselines are weak strawmen。

审稿攻击:

- Traditional L-system r0 surface components 6, PS-RSLE r0 107, though r1 both 1。必须解释 r1/tolerance accounts for seam/alias tolerance and raw r0 fragments are disclosed。
- Welded component count for PS-RSLE L-system is 9, not 1; claims should not say all welded single。

### 8.3 5.3 Generator and mesh-space recursion comparison

主文结论:

- One-shot generation synthesizes terminal object, not editable recursive state。
- Generated-root mesh recursion fragments badly。
- PS-RSLE has better occupancy connectivity and welded fragmentation in selected rows。

表格关键数字:

- tree crown: PS-RSLE occ comp 1, LCR 1.000, welded 169 vs Trellis root+mesh 32 occ comps, welded 48,931; Hunyuan root+mesh 40, welded 90,895。
- bismuth: PS-RSLE 1/LCR1/welded179 vs Trellis root+mesh 53/LCR0.112/welded132,816。
- coral: PS-RSLE 1/LCR1/welded2 vs Trellis root+mesh 43/welded57,917; Hunyuan 3/welded79,496。
- pyrite: PS-RSLE occ comp 3 but LCR1.000, welded1; Trellis root+mesh 46/LCR0.750/welded155,894。

可用结果:

- Mesh-space copy baselines have enormous welded components/open edges; PS-RSLE reduces fragmentation by orders of magnitude in the reported selected cases。
- One-shot can have high LCR, but lacks state_update/projection/reusable handles。

风险:

- `Open edges` for PS-RSLE can still be high: pyrite 262,572, tree crown 96,428, coral 139,122。不能说 mesh quality solved or watertight。
- Supplement `experiment3_mesh_enrichment_20260513` reports watertight 0/9 for PS-RSLE priority assets。必须避免 “watertight”, “simulation-ready”, “production-ready topology”。
- PS-RSLE raw/welded components in supplement medians are not always single; main table selected rows should be framed as selected finite-depth benchmark, not universal。

### 8.4 5.4 Projection ablation

这是主结果。建议正文将它定位为 “causal mechanism ablation”, 而不是普通 ablation。

当前写法很好:

- final-only improves terminal occupancy LCR but not state。
- per-depth projection preserves executable state。
- PS-RSLE combines perfect metrics。

可加强:

- 用一句话解释 why final-only fails: later rules already read invalid active handles before terminal cleanup。
- 用一句话解释 prune-only vs connector-aware: prune-only removes orphans but may delete valid connector-dependent motifs; connector-aware preserves certified connectors。

### 8.5 5.5 Local realization ablation

当前结果:

- projection enables handle survival 1.000 for realization variants。
- masked/+proj quality 0.807 best; blend 0.805 close; global smoothest。

这应作为 secondary result:

- after projection stabilizes state, local realization affects surface/readability proxies。
- masked local is preferred because it improves quality without global rewrite。

风险:

- “naturalization” 一词可能听起来像 material/semantic realism。建议用 “local realization” 或 “masked local realization”。
- deterministic proxy score 未定义，必须叫 deterministic quality proxy。

### 8.6 5.6 Controllability

当前是 qualitative showcase: depth and density controls。可用但不是核心证明。

边界:

- “exposes interpretable recursive parameters” 可以说。
- 不要说 “full controllability”, “precise semantic control”, “arbitrary user edits”。

## 9. Conclusion 对齐

当前 Conclusion:

> We presented PS-RSLE, a projection-stabilized executor for finite-depth recursive programs over frozen sparse latent 3D generator states...

总体对齐好，结尾没有过度宣称。它正确强调:

- finite-depth;
- frozen sparse latent generator;
- generator-native sparse tokens + active handles;
- typed rules;
- controlled local realization;
- projection before next rule fires;
- admissibility as per-depth execution invariant;
- distinct roles for recursive structure, generator priors, mesh/render metrics。

建议加一小句边界:

> The method does not claim physical growth simulation or watertight topology; it provides an execution semantics and evaluated state-stability mechanism for the reported finite-depth tasks.

如果篇幅有限，可放 Discussion 而非 Conclusion。

## 10. 用词范围、边界不一致与需要统一的术语

### 10.1 PS-RSLE / PS-RSLG / PS-RSLE

主文标题和摘要使用 PS-RSLE。历史草稿中有 PS-RSLG。当前 main visible text 应统一 PS-RSLE。附录/旧草稿若不进主文问题不大，但所有 active visible text 和 figure labels/captions 要统一。

### 10.2 “retains procedural-level connectivity”

安全版本:

- “retains procedural-level connectivity under tolerance-based surface metrics on the reported finite-depth benchmarks”
- “matches procedural controls under radius-one surface connectivity while reducing welded fragmentation diagnostics in selected rows”

危险版本:

- “outperforms procedural methods”
- “solves recursive structure better than classical procedural systems”

### 10.3 “rendered local readability / quality”

安全版本:

- “rendered local readability diagnostics”
- “deterministic local-realization proxy”
- “selected visual companion”

危险版本:

- “perceptually better”
- “human-preferred”
- “perceptually aligned”
- “photorealistic” unless measured and visually verified。

### 10.4 “connectivity / topology / watertight”

安全版本:

- occupancy connectivity proxy;
- surface LCR under radius/tolerance;
- welded mesh fragmentation diagnostic;
- open-edge diagnostics disclose readiness issues。

危险版本:

- watertight topology;
- manifold mesh;
- simulation-ready;
- topology guaranteed。

当前 supplement 明确 Experiment 3 priority assets watertight 0/9, 所以任何 watertight claim 都会被攻击。

### 10.5 “DLA / coral / crystal”

安全版本:

- DLA-inspired frontier growth;
- coral-like aggregate;
- pyrite-like lattice;
- bismuth-like stepped transform-copy asset。

危险版本:

- physical DLA simulation;
- biological coral growth model;
- crystallization model;
- exact symmetry/physics。

### 10.6 “projection”

安全版本:

- per-depth admissibility projection;
- root-attached or connector-certified active support selection;
- state commit step。

危险版本:

- arbitrary topology repair;
- bridge any fragmented output;
- final cleanup solves recursive state。

### 10.7 “sparse latent generator”

主文有 “Sparse Latent 3D Generators” capitalized in keywords。建议正文中除专有名词外统一小写 “sparse latent 3D generators”。如果 “Sparse Latent 3D Generator” 是引用类别可保留一次定义。

## 11. 审稿人可能攻击点

1. 这是否只是 procedural scaffold + generator rendering?

回答链:

- No, because the contribution is codec-closed recursive execution state, not terminal rendering。
- 每层 decoded candidate 必须 projection, re-encode, remap handles 后才能被下一层读。
- Projection ablation shows final-only cleanup fails state metrics。

2. One-shot generator 已经能有高 LCR, 为什么需要 PS-RSLE?

回答链:

- One-shot 是 terminal synthesis, 没有 active handles/frontiers/motifs/ownership lifecycle。
- Recursive task requires later rules to read intermediate state。
- Experiment 3 separates terminal connectivity from recursive-state access。

3. Procedural baselines 是否 strawman?

回答链:

- 论文承认 classical procedural systems are strong structural controls。
- PS-RSLE keeps their state contracts and adds learned local realization。
- Claims are limited to reported metrics: tolerance surface connectivity, welded fragmentation, local readability diagnostics。

4. Projection 是否只是 final cleanup?

回答链:

- No, final-only projection raises terminal LCR from 0.898 to 0.995 but leaves root reachability 0.504, orphan handles 3.667, handle survival 0.504, valid exec 0。
- Per-depth projection changes what later rules can read。

5. Connector-aware projection 是否会作弊，人工修桥?

回答链:

- It only admits connector support certified by rule/admission metadata under endpoint attachment, mask validity, collision clearance, and budget constraints。
- It is not arbitrary post-hoc topology repair。
- Prune-only and connector-aware rows isolate this difference。

6. Symbol formalism 是否比实现更强?

攻击面:

- `C_d^{com}` not in state tuple;
- `kappa:U^* -> V_{d+1}` before `V_{d+1}` exists;
- `KV` formula undefined;
- `owner` and `viol_frontier` prose-level。

修法:

- 把这些定义降为 operational prose 或补充 metadata definition。

7. Metrics 是否证明 visual quality?

回答:

- No, deterministic quality/artifact/normal/roughness are proxies。
- Visual figures are companions, not human preference evidence。
- No perceptual or human-preference score is claimed unless separately measured。

8. Mesh 是否 watertight?

回答:

- No watertight claim。Supplement metrics disclose open edges and 0/9 watertight for Experiment 3 priority PS-RSLE assets。
- Paper claims connectivity/state stability and fragmentation diagnostics, not production topology。

9. Pyrite row occ comp = 3, 是否违反 connected claim?

回答:

- LCR=1.000 indicates dominant support under proxy; row should be described with nuance。
- Abstract claim should say tolerance-based surface/connectivity metrics, not all raw component counts are one。

10. Local realization ablation 中 global normal/roughness 更好，为什么 masked preferred?

回答:

- Masked has best reported deterministic proxy score and lowest artifact score, while global is smoothest。
- Claim should be “preferred under the reported deterministic proxy score after projection”, not universally best。

## 12. 建议的主线措辞

可以安全贯穿全文的主线句:

> PS-RSLE does not ask the frozen generator to decide recursive validity. Rules propose local edits over active handles, the generator realizes admitted local candidates, and projection decides which realized support and handles become the next executable state.

中文解释:

PS-RSLE 不让 frozen generator 决定递归合法性。规则通过 active handles 提出局部编辑; generator 只实现已通过 admission 的候选; projection 决定哪些 realized support 和 handles 能成为下一层可执行状态。

这个句子能同时保护 4.4、4.5、5.4、5.5 的边界。

## 13. 优先修订清单

1. 在 Introduction 中补一句 sparse latent state 不等于 executable recursive state。
2. 在 Method 4.1 说明 root descriptor is authored/provided, not inferred from arbitrary meshes。
3. 在 4.1 或 4.5 说明 `C_d^{com}` 存储在哪个 metadata 中。
4. 在 4.2 列出 admission gates, 不只说 deterministic admission。
5. 在 4.3 强调 later rules read only projected/remapped active state。
6. 在 4.4 降低 `KV` 公式地位或定义它; 明确 flow updates features on fixed support。
7. 在 4.5 修正 `kappa` 与 `V_{d+1}` 的先后关系。
8. 在 Experiments 的 Metrics 段把所有 quality/visual/table values 标成 deterministic proxies or diagnostics。
9. 在 Traditional comparison 中避免 general superiority over procedural methods。
10. 在 Experiment 3 中明确 one-shot high LCR is not recursive-state success。
11. 在 Projection ablation 中突出 final-only projection cannot repair state history。
12. 在 Conclusion 或 Discussion 加有限范围: no physical growth, no watertight topology, no unbounded generation。

## 14. 最终判断

当前论文有一个可 defend 的核心: per-depth projection-stabilized executable state for finite-depth recursive 3D generation over frozen sparse latent generators。只要把 claim 限定在 “finite-depth, authored rules, state validity/connectivity/mesh diagnostics/local realization proxies” 上，故事链是完整的。

最大的风险来自用词过宽和符号过强: 如果把 results 写成普遍 visual superiority、topology guarantee、physical growth 或任意 generator editing, 会被表格中的 open edges、watertight 0/9、pyrite comp=3、quality proxy 未定义、connector certificate 抽象等点攻击。最佳策略是把 projection ablation 作为主证据，把 local realization 和 visual figures 放在次级诊断位置，把 procedural baselines 作为强结构参考而不是被击败的 strawman。
