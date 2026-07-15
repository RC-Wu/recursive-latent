# Reviewer 修改完成度映射与下一步合并建议 2026-05-09

本文件是论文/方法论支线 worker 对 `/Users/fanta/Downloads/论文修改意见与reviewer批评整理.md`、当前 `paper_siga/main.tex`、`paper_siga/drafts/method_formal_system_v2_20260509.tex`、`docs/paper/siga_claim_tightening_after_connected_crystal_coral_zh_20260509.md` 和当前 system grammar plan 的整合结果。  

本次严格遵守支线约束：没有修改 AgentDoc plan，没有跑远端，没有碰 GPU；只写入两个指定文件：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/reviewer_method_results_patch_20260509.tex`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/paper/reviewer_revision_completion_map_zh_20260509.md`

## 1. 总体判断

当前论文已经比早期版本更接近可 defend 的故事：`main.tex` 已经从“传统程序化 + 生成模型互补”转向“generation-model-native recursive language over sparse 3D latents”，并已经引入 compact state、rule template、projection-stabilized transition、material/export separation。  

但 reviewer 批评仍然有两类风险没有完全闭环：

1. **结构性论证风险**：方法虽然有公式，但 claim map 没有显式地约束“什么是主贡献、什么只是边界/补充”。读者仍可能把结果图读成“通用递归 3D 生成系统”，这会被 DLA/cache/radial/fork 的负例击穿。
2. **实验组织风险**：实验仍偏状态报告式，baseline/metric/texture/PBR/negative cases 没有完全围绕 claim 排序。特别是 texture/PBR 不能被误读成 topology proof。

我新增的 LaTeX patch 的核心作用是：把“可投稿主线”收紧成一个明确的、可合并进主文的组织框架。

## 2. 对用户反复批评的逐条回应

### 2.1 “Grammar 公式太弱，像工程模块组合”

当前 `main.tex` 已经比旧版大 tuple 改好了，但仍需要把复杂性放到更合适的位置：不是把所有变量塞进一个 tuple，而是让规则语义、投影约束、生成采样、传统系统覆盖分别承担复杂性。

我在 `reviewer_method_results_patch_20260509.tex` 中补了以下可合并内容：

- `State, Handles, and Admissible Domain`：保留 compact state
  \[
  z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d)
  \]
  同时给出 attached support、connectivity violation、admissible domain。
- `Rule Templates and Proposal Semantics`：把 grammar 具体化为 handle-to-proposal rule：
  \[
  \rho:\ h_i \mapsto
  \{(\sigma_j,\tau_j,\Omega_j,m_j,\pi_j,\kappa_j,\eta_j)\}_{j=1}^{k}.
  \]
- 增加 proposal distribution、projectable reachable domain、bridge certificate、space competition score。
- `Classical Procedural Systems as Restricted Domains`：给出 IFS、L-system、space colonization、DLA/frontier growth、shape grammar、symmetry/lattice 的公式化覆盖。

这基本回应了“公式太弱”的问题，但合并时建议不要把所有内容都塞进主文。主文保留核心规则和 coverage 表，详细推导放 appendix 更稳。

### 2.2 “Baseline/metric 不闭环”

我在 patch 中新增 `Experiment, Baseline, and Metric Organization Patch`，把结果按 claim 组织：

1. Projection ablation：direct vs final-only vs per-depth。
2. Baseline fairness：L-system / space-colonization 是强结构 baseline，不是 strawman。
3. Non-tree connected scaffold：coral/DLA-inspired 与 crystal/lattice-like 只在连通和视觉 QA 同时通过时进主文。
4. Texture/PBR export：单独作为 selected projected mesh 的资产化兼容性。
5. Depth/parameter method behavior：不是 ablation，除非真正只变一个设计点。
6. Boundary cases：DLA bridge、cache/radial/scifi/fork 等负例归入诊断。

指标部分明确拆成：

- primary structure：occupancy / surface-voxel components、LCR、root reachability、orphan mass、path-to-root rate；
- mesh diagnostics：raw face components、non-manifold、holes、Blender import/render；
- texture/PBR diagnostics：GLB size、guide、PBR channels、seam warnings；
- symmetry/lattice：只作为 approximate screening，不作为 theorem。

剩余未闭环部分：还需要真正补一个 same-root / same-depth / same-seed 的 tree/root/vine matched baseline matrix。当前 patch 只能把实验结构写清楚，不能替代缺失实验。

### 2.3 “非树结构连通性，DLA/晶体碎块不能接受”

patch 中明确把非树结果分成三类：

- 主文可用：通过 mesh render 和 occupancy/surface-voxel connectivity 的 coral/DLA-inspired connected scaffold、crystal/lattice-like connected scaffold。
- 补充可用：guide sweep、density endpoint、bismuth/pyrite variants、symmetry screening。
- 负例/边界：hard-DLA post-hoc bridge、cache/radial/scifi blocky result、fragmented fork/echo。

建议论文中坚决避免：

- “DLA solved”
- “physical coral growth”
- “physical crystallization”
- “watertight topology”

推荐用语：

- `coral/DLA-inspired connected scaffold`
- `crystal-like / lattice-inspired recursive scaffold`
- `grammar-native connected support`

### 2.4 “Texture/PBR 不能当 topology proof”

patch 中专门新增 `Material Handles and Texture/PBR Boundary`，把 material handle、Treillis2 texture export 和结构 claim 分开：

\[
g_d=\operatorname{Tex}_{\theta}(x_d^\star,y_m)
\]

这里 \(g_d\) 是 GLB/PBR asset，支持的是 asset-readiness/export compatibility，不支持 topology correctness。  

实验组织中也明确要求每张图/表区分四种 evidence：

1. Structural recursion
2. Mesh diagnostics
3. Texture/PBR export
4. Method behavior

这可以直接回应 reviewer 对“好看贴图是否掩盖碎 mesh”的质疑。

## 3. 可直接主文合并的内容

建议优先从 `reviewer_method_results_patch_20260509.tex` 合并以下部分：

1. **Problem Definition and Claim Map**  
   放在 Method 开头或 Introduction 末尾。它能迅速告诉 reviewer 本文到底 claim 什么、不 claim 什么。

2. **Table: Claim map**  
   如果版面紧张，可改成正文段落或 appendix table。但这个表对内部写作非常有用，能避免后续结果越写越散。

3. **Metric Definitions to Make Reproducible**  
   当前论文最需要补的是 metrics 的定义和 protocol separation。这部分应该尽快进入 Experiments。

4. **Text-Level Replacement Guidance 的四段安全句子**  
   可以直接替换主文里容易过强或 draft-like 的表述。

5. **Classical Procedural Systems as Restricted Domains**  
   建议主文压缩成 1 段 + 1 小表，详细公式进 appendix。这样既回应“domain coverage”，又不打断方法主线。

## 4. 哪些结果适合主文、补充、负例

### 主文优先

- projection ablation：尤其 conservative vine/tree competition。
- connected vine/root textured depth sequence：作为 selected textureable recursive asset。
- traditional textured baseline diagnostic：用于证明 texture alone is insufficient，同时承认传统 baseline 是强结构 baseline。
- best coral/DLA-inspired connected scaffold：仅当 mesh render 和 surface/occupancy metrics 都通过。
- best crystal/lattice-like connected scaffold：推荐用 pyrite/lattice 或 bismuth/pyrite cross-guide 这类连通可读结果。

### 补充材料

- full result matrix。
- guide sweep。
- bismuth variants / cross-guide variants。
- coral density endpoint。
- symmetry/orbit screening。
- cache/LOD visible-window demos。
- depth/parameter gallery。

### 负例或边界诊断

- hard-DLA post-hoc bridge。
- fragmented radial/echo/fork variants。
- cache-selected blocky DLA/radial/scifi。
- visually unclear porous/snow/portal cases。

这些负例应该服务一个论点：post-hoc repair 和盲目 cache/bridge 不能替代 grammar-native connected support。

## 5. 建议的主文结构

推荐主文结果组织顺序：

1. `Problem and Claim Map`
2. `Projection-Stabilized Recursive Sparse-Latent Grammar`
3. `Rule Templates and Classical Restricted Domains`
4. `Masked Generator Naturalization`
5. `Connected Projection and Recursive Invariant`
6. `Material Handles and Texture/PBR Export`
7. `Experimental Protocol and Metrics`
8. `Projection Ablation`
9. `Baseline Fairness`
10. `Connected Non-tree Scaffolds`
11. `Texture/PBR Export`
12. `Depth and Parameter Method Behavior`
13. `Boundary Cases and Limitations`

当前 `main.tex` 已有很多素材，但建议把 broad gallery 和多个弱 visual 退到 supplement，把主文变成 claim-driven。

## 6. 当前最重要的剩余缺口

1. **same-root baseline matrix 仍需补实验**  
   tree/root/vine 下传统 L-system、space-colonization、direct sparse grammar、final-only、per-depth 的统一矩阵仍是 reviewer 最可能追问的地方。

2. **root/branch/tip 语义指标还不够系统**  
   只有 connected support 还不够说明“递归结构干净”。需要 root reachability、orphan tips、branch endpoints、path length span、junction zoom。

3. **non-tree 正例必须非常谨慎筛选**  
   coral/crystal 可以作为 connected scaffold，但 DLA bridge/cache 类不要包装成成功。

4. **raw mesh topology 与 occupancy connectivity 的 gap 必须公开**  
   如果 raw face component 很高，caption 中要说这是 export/UV/material seam diagnostic，不要隐藏。

5. **论文图需要更像论文图**  
   现在 gallery 类图仍像状态汇报。主文图应一图一 claim、白底、subfigure 规范、caption 解释 protocol。

## 7. 对最终论文故事的建议

最稳的一句话版本：

> We introduce a projection-stabilized recursive sparse-latent grammar that executes finite-depth recursive asset programs inside the native sparse state of a frozen 3D generator. The grammar owns topology and attachment, the generator supplies masked local realization and selected PBR export, and projection inside each transition turns connected support into a recursive invariant rather than a terminal cleanup target.

中文版：

> 我们提出的是一种投影稳定的递归稀疏潜变量语法：递归程序在冻结 3D 生成模型的原生 sparse state 上执行，语法负责拓扑、连接和规则，生成模型只负责局部自然化和 selected PBR 导出；关键是把 connected projection 放进每一层递归 transition，使连通支撑成为递归不变量，而不是最终 mesh cleanup 的目标。

这个故事比“传统程序化 + Trellis2 美化”更像 SIGGRAPH/SIGA 方法论文，也更能解释为什么 DLA/bridge/cache 的负例并不是失败，而是支持设计选择的边界证据。
