# PS-RSLE 论文故事链与方法闭合审稿报告

日期: 2026-05-13  
对象: `paper_siga/main.tex` 当前 Overleaf/main 版本，以及本地/远端 A100-2 相关实现和实验表格  
定位: 严格审稿和导师式结构审查。本文档不直接改论文正文，而是给出整篇文章应当如何闭合、哪些 claim 可写、哪些必须降级或补证据。

## 0. 总判定

这篇文章现在已经有一个可以成立的核心故事，但还没有闭合成一篇可投的论文。最强的故事不是“我们做了一个更好看的 3D 生成器”，而是:

> PS-RSLE 是一种面向有限深度递归 3D 生成的执行语义。它把 frozen sparse 3D generator 的 latent/support/codec 当作局部实现基底，把规则可读的 active handles 当作程序状态，并把 admissibility projection 放进每一层递归 transition，使任何会被后续规则读取的状态都必须先通过 root-attached active-state gate。

当前摘要和 Introduction 基本已经把这个故事说出来了。问题是 Method 和 Experiments 还没有完全兑现这个故事。最严重的问题有四个:

1. **强执行闭环 claim 与真实 Trellis2 runtime 证据不完全一致。** 论文方法写的是每层 `decode -> project -> re-encode -> next rule`。但当前真实 Trellis2 递归脚本主要是 `encode once -> sparse SLAT apply_op -> decode each depth`，没有看到完整的每层 decoded-domain projection 后 mesh-to-SLAT re-encode 记录。Experiment 2/4 的主表来自 deterministic primitive/mesh proxy，不是真实 Trellis runtime handle graph。
2. **方法核心还留有 TODO。** `main.tex` 里 root-seed transfer 和 handle-transfer 是 projection 算法的核心，不是文字细节。它们现在仍是 TODO，直接破坏可复现性和审稿可信度。
3. **实验段把三个不同层级的证据混在一起。** Projection ablation 是状态语义证据；Experiment 3 是 novelty gate；masked naturalization 是 local surface proxy；Trellis2 GLB/PBR export 是资产兼容性证据；effective resolution 只是 selected-case zoom/proxy 诊断。这些必须拆开写，不能互相替代。
4. **术语、表格、图和附录仍有版本残留。** `PS-RSLG` 和 `PS-RSLE` 混用；`effective_resolution_status_table_20260510.tex` 当前是空占位；`fig:one-branch` caption 是 TODO；Appendix 状态表与主文 20260511 closed ablation 有冲突；`A_d^{active}` 与 `A_d^{act}`、grid spacing `h` 与 handle `h_i`、`N_theta/Sample_theta/Phi_theta` 都需要统一。

因此，当前最合理的论文策略是: **保留 Introduction 的主线，把 Method 写成清楚的 execution semantics；同时把实验 claim 降到证据真正支持的范围。** 如果想保留最强的“真实 sparse generator 每层 projection/re-encode execution” claim，就必须补 runtime sidecar 或补实现；否则审稿人会抓住代码/实验和方法叙述之间的差距。

## 1. 全文应回答的问题

论文要回答的不是普通的 3D generation 问题，也不是“怎样让 tree/coral/crystal 更好看”。真正的问题应当写成:

> 在有限深度、用户控制的递归 3D 生成程序中，能否把 frozen sparse 3D generator 用作局部形状/材质实现基底，同时让中间状态在每一层递归后仍然是 attached、addressable、rule-readable、reusable 的可执行状态？

这个问题的关键词是 **intermediate executable state**。审稿人必须被说服: 如果一个 detached fragment 在最终 mesh 里删掉就算了，那这个工作不成立；但如果这个 fragment 在中间层会被后续规则选为 parent/frontier/motif/cache，那 final-only cleanup 就不够。这就是文章的根。

整篇文章的逻辑链应当是:

1. 递归 3D asset 不是单次 object prediction，而是多层 local expansion。中间 branch/frontier/motif/local edit region 会被后续规则读取。
2. Classical procedural systems 已经有 explicit recursive state，所以它们是强 structural controls，不是弱 baseline。但它们通常缺 learned local realization、natural variation、texture/PBR asset quality。
3. Learned structure/program methods 能学层级、图或程序，但它们不是在 frozen sparse 3D generator 的 exposed state 上执行用户写的 finite-depth rules。
4. Sparse 3D generators 有 exposed support/features/encoder/decoder/sampling path，适合做局部实现基底。但 generator 本身不定义 active handles、ownership、frontiers、attachment certificates，也不保证下一层 rule 能读的状态合法。
5. Editing/inpainting/repair 方法能做局部条件或修复，但它们的 contract 是当前 object/edit，不是跨深度生命周期的 persistent executable state。
6. Naive combination 失败点不是“最后不好看”，而是“错误状态在被清理前已经污染了后续执行”。
7. PS-RSLE 的解决方案是状态分层: `s_d=(u_d,A_d)`。`u_d=(V_d,F_d)` 是 generator-native sparse state，`A_d` 是 rule-readable active handle registry。
8. Rules 只读 active handles，提出 local sparse edits 和 candidate handles。Admission 把 proposals 变成 generator control package `C_d`。
9. Frozen generator 只负责 codec 和 masked local realization，不负责递归语义。
10. Projection 是 commit gate: decoded candidate 只有 root-attached support 和 connector-certified support 能成为下一层 active state；detached handles 必须 deactivate/remove。
11. 因为后续 rule 只读 projected `A_{d+1}^{act}`，所以 state contamination 被挡在每层 transition 里，而不是留到终局 cleanup。
12. 实验证据必须分别证明: projection state invariant、one-shot/copy 替代不了 executable state、masked local naturalization 只改善局部 surface proxy、Trellis2 export 只证明 asset pipeline compatibility。

这条链条是可成立的。现在要做的是把 Method 和 Experiments 全部收束到这条链上。

## 2. 一句话 thesis 和贡献应如何重写

建议论文的一句话 thesis 写成:

> PS-RSLE turns recursive 3D generation over frozen sparse generator states into an executable-state problem: every state visible to later rules is a sparse latent state paired with active handles and must pass a per-depth projection gate that preserves only root-attached, rule-certified support before re-encoding.

贡献不要再写成“我们定义了若干组件”的平铺列表，而要写成 problem decomposition:

1. **State abstraction.** Formulate finite-depth recursive 3D generation as execution over a generator-coupled state `s=(u,A)`, separating sparse latent tokens from rule-readable active handles.
2. **Typed proposal and admission interface.** Define typed rule proposals and admission controls that turn authored recursive operations into local sparse edits with ownership, attachment, budget, collision, mask, and connector metadata.
3. **Projection-stabilized transition.** Introduce per-depth admissibility projection as the commit step that converts decoded generator candidates into root-attached active state before later rule selection.
4. **Frozen-generator instantiation and evaluation protocol.** Instantiate the interface around a frozen sparse 3D generator and separate structural state validity, local naturalization proxies, mesh diagnostics, and texture/PBR export compatibility.

如果当前不补真实 per-depth projection/re-encode runtime，那么第 3 条必须加限定:

> We formalize and evaluate the projection invariant through deterministic state/mesh proxies, and use Trellis2 runtime exports as compatibility evidence.

这句话会弱一些，但不会被代码证据反杀。

## 3. 摘要和 Introduction

### 3.1 摘要

摘要第 30 行整体方向正确，已经包含 finite-depth programs、intermediate reusable states、frozen sparse generator、state as latent tokens plus handles、projection before later rules。这是全篇最完整的版本之一。

需要改的地方:

- 最后一句的 “stronger mesh-quality diagnostics and rendered visual quality” 必须继续收窄。它不能读成 PS-RSLE 普遍强于成熟 procedural systems 或全部 3D baselines。
- 摘要里不应出现任何 TODO 注释。
- 如果不补真实 Trellis runtime projection/re-encode，摘要中 “executor for recursive 3D generation over frozen sparse 3D generator states” 可以保留，但 “experiments show PS-RSLE preserves executable state” 必须明确是 “state/mesh proxy ablations and selected generator-runtime exports”。

建议收束句:

> On matched finite-depth benchmarks, projection ablations show that per-depth projection prevents orphan active handles that final-only cleanup cannot remove from the execution history; selected Trellis2 exports further show that projected scaffolds can enter a frozen asset pipeline, while local naturalization improves surface proxies under the projection gate.

这比“更强 mesh/render quality”更硬，因为它直接服务主线。

### 3.2 Introduction

Introduction 目前主线完整，但有点长。它应该保留以下段落功能:

- 第 72-82 行: 递归 asset 的应用和“中间状态会被读取”。
- 第 84 行: classical procedural systems 是强 structural state controls，但 surfacing/asset quality 受限。
- 第 86 行: learned structure/program models 不是这个问题。
- 第 88-90 行: sparse generators/editing 有 local realization prior，但没有 recursive validity。
- 第 92 行: naive combination 和 final-only cleanup 为什么失败。
- 第 94-96 行: PS-RSLE 解决方案和本文 scope。

需要压缩的是 related-work 型背景。Introduction 中 classical/generator/editing 的文献综述不要写得像 Related Work；每段只需要完成一个论证动作:

1. “已有系统解决了 state，但缺 local realization。”
2. “已有 generator 解决了 realization，但缺 executable state。”
3. “已有 editing 解决了 local condition，但缺 state lifecycle。”

现在 Related Work 里又重复了这些判断，所以 Introduction 可以更短，让主线更锋利。

### 3.3 Introduction 的逻辑缺口

当前 Introduction 已经说“final-only cleanup 太晚”，但可以再补一句机制化表述:

> The failure is temporal: once a detached component has been exposed to the scheduler, a terminal cleanup cannot undo the fact that later rules may already have branched from it, copied it, or cached it.

这句话能把“为什么必须 per-depth projection”钉死。

## 4. Related Work

Related Work 现在方向正确，但要避免重复 Introduction。它的任务不是再讲一遍背景，而是帮审稿人排除替代解释:

1. **Procedural recursive modeling:** 它们有 state，所以不是弱 baseline。PS-RSLE 的差异是 learned local realization plus projection-stabilized sparse generator state。
2. **Learned structure/program generation:** 它们学习结构/程序，但不是用户规则在 frozen sparse generator exposed state 上执行。
3. **Native 3D generation/sparse latents:** 它们提供 substrate，不提供 recursive validity。
4. **Editing/control:** mask、prompt、skeleton、inpainting 是 conditioning signal，不是 persistent active handle lifecycle。

Related Work 的每一节末尾都应当落到同一个缺口:

> Prior work either gives explicit recursive state without learned local realization, or learned realization/editing without an executable state contract across recursive depths.

目前第 134 行已经接近这个结论。建议把每小节最后一句都改成更短、更判别式的表述，减少“我们也能做 roots/coral/crystal”的展开。

## 5. Preliminaries

Preliminaries 应该只做两件事: 定义 finite-depth execution 和定义 sparse generator interface。现在基本正确，但符号层面不够干净。

### 5.1 `x_D=Output(s_D)` 与 `x_D^\star`

第 140-145 行写 `x_D=\operatorname{Output}(s_D)`，Algorithm 最后返回 `x_D^\star`。这不是小问题，因为 `x_D^\star` 表示 projected committed output，而 `x_D` 可能是 raw decoded candidate。

建议统一:

```latex
s_{d+1}=\operatorname{Step}(s_d,\mathcal R_d,\xi_d),\qquad
x_D^\star=\operatorname{Output}(s_D).
```

并解释 `\star` 表示 committed/projected asset。

### 5.2 Grid spacing `h` 与 handle `h_i`

第 155 行 `V\subset h\mathbb Z^3` 用 `h` 表示 grid spacing；第 198 行 `h_i` 又是 handle。审稿人读符号会混乱。

建议:

- grid spacing 改成 `\delta`: `V\subset \delta\mathbb Z^3`
- handle 改成 `a_i` 或 `\alpha_i` 不能，因为 `\alpha_i` 已用于 attributes。最清楚是 `a_i=(\sigma_i,T_i,\Omega_i,\beta_i)`。
- active set 写成 `A_d^{act}`，全篇不要再用 `A_d^{active}`。

### 5.3 Generator sampler 符号

现在 `\mathcal N_\theta`、`\operatorname{Sample}_\theta`、`\Phi_{\theta,t}` 都出现了。建议层级化:

- `\mathcal N_\theta` 是 abstract native sparse-latent update。
- `Sample_\theta` 是 method transition 中调用的受控 wrapper。
- `\Phi_{\theta,t}` 是 masked flow/diffusion step 的内部一步。

如果不想解释这么多，就只保留 `Sample_\theta` 和一个 masked specialization:

```latex
\bar u_{d+1}=\operatorname{Sample}_\theta(\widetilde u_{d+1};m_d,y,C_d,\epsilon_d).
```

然后把 `\Phi_{\theta,t}` 当实现细节放入 paragraph，而不是主公式。

### 5.4 `V` 与 `U`

Method 中 `V` 是 sparse latent token support，projection 中 `U` 是 decoded/voxelized projection support。这一区分必须显式说:

- `V_d`: generator-native sparse token coordinates, rule proposal/edit domain。
- `U`: decoded geometric support used for projection and reachability tests。

否则审稿人会问: 为什么 state admissibility 用 `V_d^{att}`，projection 又用 `U^{att}`，两者如何对应？答案应该是: projection 在 decoded domain 判断，commit 后通过 encoder 回到 `V_{d+1}`；handle transfer 是桥梁。

## 6. Method 逐节审查

### 6.1 Program State

这一节是全篇方法的地基。它的主张应当是:

> Sparse latent state is not a recursive program state until it is paired with rule-readable active handles and an admissibility predicate.

当前写法基本对，但必须补三类具体内容:

1. **Root descriptor.** `V_d^{root}` 不能凭空来。需要定义 root descriptor 是什么: root mask、root handle support、manifest seed region、local frame descriptor，还是 decoded support 上的 nearest assignment。
2. **Active handle lifecycle.** handle 不只是 tuple，还需要状态: active / inactive diagnostic / deleted。只有 active handles 可被 scheduler 读取。
3. **Ownership and support assignment.** `\Omega_i\subseteq V_d` 在 projection 后如何更新，是 method 的核心，而非实现细节。

建议把 handle 定义改成:

```latex
a_i=(\sigma_i,T_i,\Omega_i,\beta_i,\ell_i),
```

其中 `\ell_i\in{active,inactive,deleted}` 或者用 registry 外部状态表。这样后文 “deactivate detached handles” 有正式对象。

### 6.2 Rule Proposals and Admission

第 221-233 行的 proposal record 很重要，但 `AdmitApply` 现在仍是黑箱。审稿人会问: 什么被 admit？什么被 reject？为什么 admission 与 projection 不重复？

建议把 admission gates 明确成表或算法:

- semantic match: rule type 与 handle type 兼容；
- attachment intent: proposed child/motif 必须有 parent/connector；
- budget: token/primitive/support 增长不超过 `T_max(d)`；
- collision/clearance: local edit region 不破坏 locked old support；
- mask validity: editable mask 与 clamped anchors 不冲突；
- connector certificate: connector 必须在 proposal 前声明，不能 projection 时凭空发明；
- cache policy: candidate motif 只有 projection 后才能写入 reusable cache。

这样 `C_d` 就不是“很多东西的袋子”，而是 generator-control package with declared masks, anchors, certificates, budgets。

### 6.3 Projection-Stabilized Recursive Transition

这一节的主线正确，但现在有一个关键风险: **论文 formal transition 写得强于当前真实 Trellis2 runtime 证据。**

论文写法:

```latex
\widetilde u_{d+1} -> Sample_\theta -> Dec_\theta -> x_{d+1}
-> \Pi_{\lambda_d} -> x^\star_{d+1}, A_{d+1}
-> Enc_\theta -> u_{d+1}
```

真实 Trellis2 workflow 代码证据:

- `assets/trellis2_recursive_slat_grammar_workflow.py` 先把 input mesh 转 O-Voxel/flexible dual grid，再 `base_slat = encoder(...)`。
- 每个 grammar 里 `st = base_slat`。
- 每个 depth 先 `decoded = decoder(st)[0]` 输出 mesh/preview。
- 如果还没到终深，则对 `st` 执行 `st = apply_op(st, op, limit)`。
- 主循环里没有看到每层 decoded-domain projection 后再 mesh-to-SLAT re-encode 的完整闭环。

这意味着当前 method 有两个选择:

#### 选择 A: 补真实闭环，然后保留强 claim

需要实现并记录:

1. 每 depth decode raw candidate。
2. 在 decoded mesh/support domain 做 root-attached projection。
3. 输出 projected mesh/support。
4. mesh-to-FDG/O-Voxel。
5. shape SLAT encoder re-encode 成 `u_{d+1}`。
6. 更新 handle sidecar。
7. 下一层 rules 只读 projected sidecar。

同时每个 depth 写出 sidecar:

```json
{
  "depth": 2,
  "raw_tokens": 8340,
  "raw_components": 7,
  "root_seed_rule": "...",
  "active_handles_before": 18,
  "projected_support_mass": 0.93,
  "deactivated_handles": [...],
  "connector_certificates_used": [...],
  "reencoded_tokens": 7212,
  "active_handles_after": 13
}
```

#### 选择 B: 不补闭环，降级 method claim

如果当前时间不够，论文应写成:

> PS-RSLE defines the execution semantics and the projection invariant. The current Trellis2 runtime instantiation uses sparse SLAT grammar operations and per-depth decoded diagnostics; the closed projection/naturalization matrices are deterministic primitive/mesh proxies used to test the state invariant before full runtime integration. Trellis2 GLB/PBR exports demonstrate compatibility of selected projected scaffolds with a frozen asset pipeline.

这会牺牲一部分强度，但比让 reviewer 发现“method pseudocode 与实际 runtime 不符”安全得多。

### 6.4 `fig:one-branch`

第 335-340 行现在用 `figures/personal/stickcase.pdf`，但 caption 是 `TODO`，Description 还复制了 sparse latent generator interface。这是显眼硬伤。

该图应该承担一个任务: 用一个 branch transition 把 active handle、proposal、mask、decode、projection、surviving child handle 串起来。建议 caption:

> One branch transition under PS-RSLE. An active tip handle defines a local frame and owned support; a branch rule proposes child support, a connector certificate, and candidate child-tip handles; the frozen sparse generator realizes the admitted local edit; projection keeps only root-attached or connector-certified decoded support and deactivates any detached child handle before the next rule can read it.

如果 `stickcase.pdf` 只是新上传的 branch schematic，可以用；但它必须配合上面语义，而不是作为普通图。

### 6.5 Admissibility Projection

这是全篇最关键的方法节。现在文字解释有力量，但 TODO 破坏了可复现性。

必须补的两个规则:

#### Root seed transfer

可写的安全版本:

> The root descriptor is stored as a persistent root handle in the run manifest. During projection, the descriptor is transformed into the current object frame and assigned to decoded projection support by nearest-support matching within tolerance. If fewer than a threshold number of support samples can be assigned, the candidate fails the projection gate. In the deterministic proxy ablations, the same contract is approximated by depth-0/root primitives and contact-graph reachability.

如果代码没有完整实现，不要写成“我们的 runtime 已经如此”。写成 implementation contract 或 proxy approximation。

#### Handle transfer

可写的安全版本:

> Each candidate handle carries a local frame and an owned or target support descriptor. Projection relocates the descriptor onto projected support by nearest support, voxel overlap, or rule-declared connector support. A handle remains active only if its support is root-attached or connector-certified and all rule-local constraints still hold; otherwise it is demoted to inactive diagnostics or removed. In the deterministic proxy ablations, primitive roles and contact-graph reachability approximate this handle lifecycle.

这里不能说“visual repair”。handle transfer 是 active state lifecycle。

### 6.6 Masked Sparse-Latent Sampling

这节应该被写成辅助机制，不是结构主贡献。正确口径:

- masked sampling/naturalization 改局部 surface/features；
- old state 外部 anchors/clamped；
- 它不决定 active topology；
- projection 决定下一层可执行 state。

Experiment 4 的数字支持这个口径: projection 开启后 no-N 已恢复 handle survival；masked/+proj 相比 no-N/+proj 改善 roughness、normal consistency、artifact、quality proxy。

错误口径:

- “masked naturalization solves topology”
- “PBR seam/material propagation solved”
- “global repair is our method”

这些都应避免。

### 6.7 Scope and Implementation Notes

第 463-479 行很重要，应该保留并更具体。尤其要把 texture/PBR export 的角色钉死:

> Exported GLB import, texture channels, and render quality support asset compatibility; they do not by themselves prove recursive connectivity, material propagation, or topology cleanliness.

这句话是对抗 reviewer 的保护伞。建议在 Experiments 的 4.5 再重复一次。

### 6.8 方法图计划

当前 `figures/personal/main_method.pdf` 只有 17K，像占位或旧图；`figures/method_diagram_pptx_20260512/ps_rsle_method_overview_20260512.pdf` 有 1.5M，更像完整主方法图。建议:

- 主方法图换成 `figures/method_diagram_pptx_20260512/ps_rsle_method_overview_20260512.pdf`，前提是实际渲染检查无误。
- sparse interface 图可以考虑换成 `figures/method_diagram_pptx_20260512/sparse_latent_generator_interface_20260512.pdf`。
- `fig:one-branch` 用用户新传的 `stickcase.pdf`，但 caption 和 Description 必须重写。
- Projection gate 和 masked naturalization mechanism 图现在被注释掉。若版面允许，至少保留一个 compact projection gate 图；它比很多 gallery 更服务主线。

## 7. Experiments 总体重排

实验现在最大问题是层级混乱。建议按照 claim-evidence matrix 写:

| Claim | Evidence | 当前强度 | 应写成 |
|---|---|---:|---|
| Final-only cleanup 不能阻止 state contamination | Projection ablation: final-only LCR 高但 root reachability/handle survival 与 no projection 一样差 | 强，但 proxy | Per-depth projection stabilizes active recursive state in deterministic state/mesh proxy ablations |
| Per-depth projection 是结构核心 | prune-only、connector-aware、full PS-RSLE 对比 | 强，但 proxy | Projection inside the loop removes orphan active handles and preserves root-reachable active state |
| One-shot/latent-copy/mesh-copy 不能替代 executable state | Experiment 3 selected 4-case novelty gate | 中等 | Baselines can make plausible/copy shapes but lack typed handles/projection/state update |
| Masked local naturalization 改善局部 surface | Experiment 4 four-task three-seed proxy | 中等 | Local surface-realization proxy improves under projection |
| Trellis2 PBR/GLB export compatible | V21/V23/export figures and `trellis2_texturing_export_glb.py` | 中等偏弱 | Selected projected scaffolds can enter frozen Trellis2 texture export path |
| Effective resolution 普遍更强 | 当前证据弱，且 table input 为空 | 弱 | Selected zoom/proxy diagnostic only |

这个矩阵建议放进 internal revision notes，主文可以简化成 Claims under test 段。

## 8. Transform-Copy Operator Screening

当前 4.2 写得比之前安全: 它说这是 operator-admission test，不是 visual gallery，也不是证明 sparse-latent execution 超过 procedural OBJ construction。这是正确方向。

但它仍需更严:

1. V21 table 的 admission 只能证明 “under this grammar contract, some transform-copy candidates pass connectivity/export diagnostics”。
2. 不能把 pyrite/radial/bismuth 写成 exact equivariance 或 exact IFS recursion。
3. 需要额外指标才能更强:
   - transform/orbit error；
   - source-target motif correspondence；
   - handle survival across transform depth；
   - active connector certificate；
   - old support mutation rate。
4. Axis-mismatch row 是好 negative control，应保留并明确: connected does not mean semantically admissible。

建议主文一句话:

> V21 is an admission screen: connectivity and export diagnostics are necessary but not sufficient; rows are admitted only when their transform role is compatible with the declared recursive operator.

## 9. Projection Ablation

这是当前最强实验，应该成为文章 Results 的核心。

表格数字非常有力:

- no projection: LCR `0.898`, root reachability `0.504`, orphan active `3.667`, handle survival `0.504`, fail `1.0`
- final-only: LCR `0.995`,但 root reachability `0.504`, orphan active `3.667`, handle survival `0.504`, fail `1.0`
- prune-only: root reachability `1.0`, orphan active `0`, handle survival `0.782`, fail `0.750`
- connector-aware: root reachability `1.0`, orphan active `0`, handle survival `1.0`, fail `0.250`
- full PS-RSLG/PS-RSLE: 全部理想，fail `0`

最强论点是 final-only 与 no projection 的 active-state 指标完全一样差。这个直接证明“terminal cleanup cannot undo execution history”。

但必须明确限制:

- 表格来自 `assets/projection_masked_ablation_matrices_20260511.py`，脚本自述为 deterministic/local。
- `summary.json` 明确写 `local deterministic primitive/mesh proxy; remote Trellis runtime visual rerun still required for final PBR asset claims`。
- 字段里大量 `_proxy`，不是真实 Trellis sparse-handle graph。

主文建议写:

> The projection ablation is a deterministic trace/mesh proxy designed to isolate the execution invariant. It does not claim that the current Trellis2 runtime has already logged a full sparse-handle graph for every row.

这句话看似降级，实际会增强可信度。

## 10. Experiment 3: Sparse-Latent Grammar vs Mesh-Space Alternatives

这节应该写成 “novelty gate”，而不是全面 SOTA comparison。

当前表格有四个 case: tree crown, bismuth, coral, pyrite。每个 case 对比:

- Trellis2 one-shot；
- Trellis2 latent-copy；
- Trellis2 root+mesh-copy；
- Hunyuan root+mesh-copy；
- PS-RSLG/PS-RSLE。

可写的核心:

1. One-shot 可以合成 plausible object，但没有 recursive state。
2. Latent-copy 和 mesh-copy 更强，因为它们确实复用了 generated root 并做 copy，但仍没有 typed handles/projection/re-encode lifecycle。
3. Hunyuan row 是公平 mesh-space route: text root -> mesh root -> deterministic transform/copy，不是故意让 Hunyuan 做它不擅长的 full recursive guide。
4. PS-RSLE row 是唯一带 State/Proj 的 row。
5. LCR 不单独证明 topology，因为 one-shot/copy 也可能 LCR 很高但 raw components 很多。

必须修:

- 表格和 caption 仍写 `PS-RSLG`，应改 `PS-RSLE`，或在脚注里声明 `PS-RSLG` 是 legacy implementation label。最佳是统一成 `PS-RSLE`。
- Pyrite PS row raw comp 和 occ comp 都是 `3`，虽然 LCR `1.0`。必须保留 caveat，不能作为 clean topology proof。
- 不要把四个 selected cases 写成 universal coverage。full eight-case sweep 如果质量不齐，应放 supplementary diagnostics。

建议小节开头:

> This experiment is a novelty gate, not a universal model ranking. It asks whether generous one-shot generation, direct latent copying, or generated-root mesh copying can replace the executable-state contract tested in the projection ablation.

## 11. Naturalization, Export, and Effective Resolution

当前 4.5 把三个不同问题放在一起:

1. masked local naturalization；
2. Trellis2 texture/PBR export；
3. effective resolution / zoom detail。

建议拆成三个 paragraph 或三个 subsubsection，否则 reviewer 会以为它们互相证明。

### 11.1 Masked Naturalization

当前表格支持的准确 claim:

> Under projection, masked local naturalization improves local surface-realization proxies while preserving handle survival.

数字:

- rule-only: roughness `50.00`, normal `0.000`, artifacts `0.487`, handle survival `0.500`, fail `1.0`
- masked/no-proj: handle survival 仍 `0.500`, fail `1.0`
- no-N/+proj: roughness `16.94`, normal `0.597`, artifacts `0.348`, quality `0.771`, handle survival `1.0`, fail `0.25`
- masked/+proj: roughness `13.92`, normal `0.669`, artifacts `0.227`, quality `0.807`, handle survival `1.0`, fail `0`
- global/+proj: roughness `13.58`, normal `0.677`,但 quality `0.735`

解释应是:

- projection 是 handle gate；
- no-N/+proj 已经修复结构状态；
- masked local-N 改善局部 surface/quality proxy；
- global-N 更 smooth 但 mutates old state，质量 proxy 下降；
- no projection 时 naturalization 不能救 active state。

不能写:

- masked local naturalization 证明真实 Trellis sparse-latent handle graph 已闭环；
- masked local naturalization 解决了 topology；
- global repair 是 ours；
- PBR seam solved。

### 11.2 Export

真实导出路径来自 `assets/trellis2_texturing_export_glb.py`:

1. load mesh/image；
2. `pipe.encode_shape_slat(mesh, resolution)`；
3. `pipe.sample_tex_slat(...)`；
4. `pipe.decode_tex_slat(tex_slat)`；
5. `pipe.postprocess_mesh(...)`；
6. export `textured.glb`。

这能证明:

- selected scaffolds can enter Trellis2 texturing/PBR export；
- GLB can be imported/rendered；
- texture channels/PBR voxel path works for selected assets。

这不能证明:

- recursive topology；
- active-handle validity；
- material propagation across recursion；
- seam-free PBR；
- clean watertight mesh。

主文必须把 export 作为 asset compatibility，不要作为 structural proof。

### 11.3 Effective Resolution

这是目前最弱的一块。

硬事实:

- `main.tex` 第 637 行 input 的 `drafts/effective_resolution_status_table_20260510.tex` 实际只是注释占位，没有真实 table。
- 真实 proxy table 在 `drafts/ablation_and_resolution_status_tables_20260510.tex` 第 48 行附近，但该文件是 untracked/status table，而且 caption 自己说这是 proxy metrics。
- effective-resolution 脚本定义 `local_feature_scale = bbox_diag / sqrt(face_count)`，`terminal_detail` 用 occupied voxels 或 vertices/faces，`zoom_retention = LCR * (1 + boxDim/3)`。
- tree/vine row 的 detail ratio 是 `0.54`，不能支持 universal terminal-detail superiority。

建议:

- 主文删除空 `\input{drafts/effective_resolution_status_table_20260510.tex}`，或者替换为明确标注 proxy 的 compact table。
- 如果用户之前已经删掉 effective 表格，那么更安全是不要恢复主表，只保留 qualitative zoom diagnostic。
- 写法应是 “selected local zoom/effective recursive detail diagnostic”，不是 theorem，也不是全面优于 one-shot。

建议句:

> Effective resolution is treated as a selected zoom diagnostic. The current proxy suggests finer local feature scale in selected recursive assets, but it does not support a universal terminal-detail superiority claim.

## 12. 主传统对比表与 corrected metrics

当前 `figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex` 是 corrected metrics 表，且没有 std columns。这符合之前“如果只是去掉 std，就用本地版本”的方向。

关键数字:

- Space colonization Ours: `C_r0=6`, `LCR_r0=0.996`, `C_r1=1`, Faces `84,062`, Welded comp. `1`
- L-system Ours: `C_r0=107`, `LCR_r0=0.979`, `C_r1=1`, Faces `75,528`, Welded comp. `9`
- DLA/frontier Ours: `C_r0=1`, `LCR_r0=1.000`, `C_r1=1`, Faces `42,491`, Welded comp. `1`
- IFS/transform Ours: `C_r0=1`, `LCR_r0=1.000`, `C_r1=1`, Faces `37,274`, Welded comp. `1`, Box dim `2.071`

可写结论:

- DLA/frontier 和 IFS/transform selected rows 在 exact surface-voxel connectivity 上干净。
- Space colonization 和 L-system rows 需要 caveat: exact r0 有多个 components，但 r1 连通；L-system 尤其有 fine tapered spikes/aliasing caveat。
- 这个表支持 selected visual/mesh diagnostics，不支持“所有 family 结构都严格优于 procedural”。

风险:

- 需要确认 `main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.png` 与 corrected V67B table 是否完全对应。若图和表不是同一批 case，会被 reviewer 抓住。

## 13. 远端 A100-2 与真实实现核查

远端 root:

```text
/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
```

远端和本地关键脚本一致:

- `assets/trellis2_recursive_slat_grammar_workflow.py`
- `assets/trellis2_texturing_export_glb.py`
- projection/naturalization proxy scripts
- Experiment 3 route/baseline scripts

### 13.1 真实 Trellis2 recursive SLAT workflow

当前真实 workflow 是:

1. 读入 mesh。
2. 做 preencode transform、center/scale、axis conversion。
3. `o_voxel.convert.mesh_to_flexible_dual_grid(...)`。
4. 构造 sparse vertices/intersected。
5. `base_slat = encoder(sparse_vertices, sparse_intersected)`。
6. 对每个 grammar:
   - `st = base_slat`
   - depth loop:
     - `decoded = decoder(st)[0]`
     - 写 mesh/preview/summary
     - 若未到终深: `st = apply_op(st, op, limit)`
7. token 超过 `max_tokens` 则 stop。

这说明真实 runtime 里确实有 sparse-coordinate/feature operators 和 per-depth decode diagnostics，但没有当前 method 算法所写的 per-depth decoded projection 后 re-encode。

### 13.2 Transform/visual admission V21

V21 dry-run input generator做了:

- connected OBJ supports；
- shared-vertex anchors；
- attached natural mesh detail；
- PBR guides；
- largest-component gate；
- manifest certificate chain。

V21 remote launcher 在 A100-2 上跑 Trellis2 texturing export。它是 transform-copy operator screening + export compatibility，不是完整 recursive state proof。

### 13.3 Experiment 3 baselines

Experiment 3 的真实实现分清楚了:

- Trellis2 one-shot: full target guide；
- Trellis2 latent-copy: root guide 后直接 latent/copy transform；
- Trellis2 generated-root mesh-copy: generated root mesh 后 deterministic S/R/T concat；
- Hunyuan root+mesh-copy: text prompt 生成 root mesh，再 deterministic mesh transform/copy；
- PS row: selected PS metrics，仍有 proxy caveat。

这套 baseline 设计是合理的。写作时不要说它全面战胜 Hunyuan/Trellis2，而要说它证明这些 route 缺少 executable state contract。

### 13.4 Experiment 2/4 proxy nature

`projection_masked_ablation_matrices_20260511.py` 自述:

> deterministic and local; closes the metric contract before remote Trellis/PBR reruns.

`summary.json` 自述:

> local deterministic primitive/mesh proxy; remote Trellis runtime visual rerun still required for final PBR asset claims.

所以 4.4/4.5 不能写成“真实 Trellis sparse-latent runtime handle graph 已验证”。应写成:

> deterministic trace/mesh proxy ablation for the execution invariant, plus selected frozen-generator export compatibility evidence.

## 14. 4.4 和 4.5 的建议写法

用户特别提到 4.4、4.5 需要澄清具体步骤。这里按当前主文编号理解:

### 14.1 4.4: Sparse-Latent Grammar versus Mesh-Space Alternatives

建议标题保留或改成:

> Quality-Gated Novelty Test Against One-Shot and Copy-Based Routes

建议结构:

1. 先说本节不做 universal model ranking。
2. 定义四类替代 route:
   - one-shot generator with full recursive target guide；
   - root-conditioned latent-copy；
   - generated-root mesh-space copy；
   - Hunyuan text-root mesh-space copy。
3. 明确这些 route 为什么是强 negative controls:
   - 有 generated prior；
   - 有 root reuse；
   - 有 deterministic recursive copy；
   - 但没有 typed handles/projection/state lifecycle。
4. 再报告四个 selected claim-bearing cases。
5. 最后 caveat: high LCR alone not topology proof; handle validity tested elsewhere。

可直接改写的英文段落:

> Experiment 3 is a novelty gate rather than a model-ranking benchmark. We give the one-shot baseline the full recursive target guide, and we give copy-based baselines generated roots before deterministic recursive transforms. These controls therefore test a strong alternative: reuse a native 3D generator once, then perform recursion in latent or mesh space. Their limitation is not that they cannot produce plausible geometry, but that the copied fragments do not become typed, projected, rule-readable state for the next depth.

### 14.2 4.5: Naturalization, Export, and Effective Resolution

建议拆为三个短段:

#### A. Masked local realization under projection

> Experiment 4 isolates local realization from structural validity. Projection closes the active-state gate; masked local naturalization then improves roughness, normal consistency, local artifact, and rendered-quality proxies under the same projection schedule.

#### B. Frozen Trellis2 export compatibility

> Selected projected scaffolds are passed through the frozen Trellis2 texture/PBR export path. This tests whether projected meshes can be consumed by the asset pipeline; it does not certify recursive topology or material propagation.

#### C. Effective recursive detail

> Effective resolution is reported only as selected zoom/proxy diagnostics. It should not be used as a universal detail-superiority claim until same-root, handle-level, multi-scale metrics are complete.

如果保留一个 combined subsection，段首必须说:

> This subsection reports three separate diagnostics and should not be read as a single proof chain.

## 15. 图、算法、表格必须修的清单

### P0: 投前必须修

1. 删除或解决 `main.tex` 中所有 TODO:
   - abstract final sentence TODO；
   - contributions TODO；
   - `fig:one-branch` caption TODO；
   - projection root transfer TODO；
   - projection handle transfer TODO；
   - Algorithm 2 中 root/handle transfer TODO。
2. 统一名称:
   - 主文统一 `PS-RSLE`；
   - included tables 里的 `PS-RSLG` 改为 `PS-RSLE`，或加 legacy label 说明。建议直接改。
3. 统一符号:
   - grid spacing `h` 改 `\delta`；
   - handle `h_i` 改 `a_i`；
   - `A_d^{active}` 改 `A_d^{act}`；
   - projection signature 前后一致，建议都写 `\Pi_{\lambda_d}(x_{d+1},\widetilde A_{d+1},s_d,C_d)`；
   - `x_D` 与 `x_D^\star` 统一。
4. 修 `fig:one-branch`:
   - caption、Description、正文引用都必须对应 branch transition。
5. 修空 effective-resolution input:
   - 删除 `\input{drafts/effective_resolution_status_table_20260510.tex}`，或替换为真实且明确 proxy 的 table。
6. 修 Appendix stale/conflict:
   - `drafts/ablation_status_tables_20260510.tex` 说 naturalization rows missing，但主文有 20260511 table。要么删掉旧状态表，要么标成 historical status。
7. 修 Appendix five-column caption:
   - 现在说 columns two through five 都是 executor variants，但 column 2 是 classical baseline。应改。
8. 明确 proxy limitation:
   - Projection and masked naturalization tables必须说 deterministic primitive/mesh proxy，不是真实 Trellis runtime handle graph。
9. 解决 method/runtime mismatch:
   - 要么补真实 per-depth projection/re-encode sidecar；
   - 要么把 method/experiments 的强 claim 降为 semantics + proxy validation + selected export compatibility。

### P1: 强烈建议修

1. Introduction 压缩 20-30%，把重复的 related-work 综述移到 Related Work。
2. Method 加一个 compact claim/evidence/contract table:
   - state；
   - proposal/admission；
   - projection；
   - masked realization；
   - export。
3. Projection gate 图重新启用或放入主文。
4. Experiment section 开头放 claim-bearing organization，不要以 gallery 逻辑组织。
5. V21 transform admission 加 transform/orbit/handle certificate 说明，哪怕指标还未完整也要把不足说清楚。
6. Main visual figure 与 corrected V67B table 做 provenance 对齐检查。

### P2: 如果时间允许

1. 补真实 Trellis runtime per-depth projection/re-encode 最小闭环，只跑 1-2 个 case，也比完全没有强。
2. 补每 depth JSON sidecar，记录 active handles/root reachability/deactivated handles/reencoded tokens。
3. 补同根 effective-resolution multi-scale zoom metric，不只 selected-case proxy。
4. 补 runtime/memory/token growth table，用于说明 projection 代价。
5. 补 transform-copy orbit consistency metric。

## 16. 语义融合方案

基于当前用户要求“远端当成最新方案”“stickcase 图是刚传的”“effective 表被删掉”“corrected metrics 如果只是去 std 就用本地版本”，建议的主分支语义融合原则是:

1. **文本基底采用远端 main/Overleaf 最新版本。** 因为用户已在远端更新多版文本，摘要和 Introduction 也最完整。
2. **保留用户新传 `stickcase.pdf`。** 但必须重写 caption/Description，让它服务 one-branch transition。
3. **不恢复空 effective table。** 如果 effective 表被用户删除，当前空 input 应删除；effective-resolution 只作为 qualitative zoom/proxy paragraph。
4. **保留 corrected V67B metrics table。** 该表没有 std columns，并且当前数字与主文 caveat 匹配；但要确认对应的 visual matrix 是同一批。
5. **不上传未引用图片。** 当前未跟踪图片很多，主文没有引用的视觉候选先不进 Overleaf，避免污染项目和增加审稿混乱。
6. **统一 PS-RSLE。** 历史脚本/表格中的 PS-RSLG 作为 legacy internal name，不应出现在主文 claim-bearing table 里。
7. **远端代码证据按真实范围写。** A100-2 的 Trellis2 code 支持 sparse SLAT ops 和 texture export，不支持未记录的 full per-depth projection/re-encode runtime claim。

## 17. 建议的新版文章结构

### Abstract

- 一句话问题: recursive programs need executable intermediate states。
- 一句话 gap: sparse generators provide local realization but not admissible transitions。
- 一句话方法: state = sparse tokens + active handles; rules propose; generator realizes; projection commits。
- 一句话实验: projection ablation proves final-only failure; novelty gate separates one-shot/copy; masked naturalization/export are scoped diagnostics。

### 1 Introduction

1. Recursive asset generation and intermediate state contamination。
2. Procedural systems: state yes, learned realization no。
3. Generators/editing: realization yes, executable state no。
4. Naive combination and final-only cleanup failure。
5. PS-RSLE thesis。
6. Scope。
7. Contributions。

### 2 Related Work

1. Procedural recursive modeling。
2. Learned structures/programs。
3. Sparse/native 3D generators。
4. Editing/control versus persistent executable state。

### 3 Preliminaries

1. Finite-depth recursive programs。
2. Sparse generator interface。

### 4 Method

1. Program state and active handles。
2. Typed rule proposals。
3. Admission and control package。
4. Projection-stabilized transition。
5. Admissibility projection with root/handle transfer。
6. Masked local realization。
7. Scope and implementation notes。

### 5 Experiments

1. Protocol, tasks, metrics, claim-evidence organization。
2. Transform-copy operator admission。
3. Projection ablation: core evidence。
4. Novelty gate against one-shot/copy routes。
5. Masked naturalization under projection。
6. Export compatibility and selected zoom diagnostics。
7. Boundaries and supplementary placement。

### 6 Discussion

- What is proven: state contamination and projection invariant in proxy ablations; selected export compatibility。
- What is not proven: universal topology, material propagation, physical growth, unbounded recursion, full real-runtime handle graph unless added。

### 7 Conclusion

- Return to state contamination and per-depth projection invariant。

## 18. 可直接使用的关键英文改写片段

### 18.1 Core thesis

> Recursive 3D generation fails not only when the terminal mesh contains artifacts, but when invalid intermediate fragments remain executable. A detached component that is later selected as a parent, copied as a motif, or cached as a frontier has already contaminated the derivation, even if a final cleanup removes it.

### 18.2 Projection claim

> Projection is the commit operation of the recursive transition. It is not a terminal repair pass: only the projected state is visible to the next scheduler, so detached decoded support cannot become an active parent, frontier, or reusable motif.

### 18.3 Proxy limitation

> The projection and naturalization matrices are deterministic trace/mesh proxy ablations designed to isolate the execution invariant. They do not by themselves certify a full Trellis2 runtime sparse-handle graph; selected Trellis2 exports are reported separately as asset-pipeline compatibility evidence.

### 18.4 Experiment 3

> The one-shot and copy-based controls are deliberately strong: they receive generated roots or full target guides before deterministic recursion is applied in latent or mesh space. Their failure mode is not simply poor visual quality, but the absence of typed handles, projection, and committed recursive state.

### 18.5 Naturalization

> Projection closes the active-state gate; masked local naturalization improves local surface-realization proxies under that gate. Global repair is a control because it can smooth the asset while mutating old state, which is precisely what the executable-state contract tries to avoid.

### 18.6 Export

> GLB/PBR export success shows that selected projected scaffolds can be consumed by the frozen asset pipeline. It is not used as evidence of recursive topology, handle survival, or material propagation.

## 19. 最严厉 reviewer 会问的问题

1. 你的主算法写了每层 re-encode，但真实 runtime 是否真的这样做？如果没有，为什么 Method 写成这样？
2. Active handle 到底是什么数据结构？在哪里存？projection 后如何更新？
3. Root seeds 如何从上一层状态转移到 decoded support？
4. Projection table 是真实 Trellis sparse-latent execution，还是 primitive/mesh proxy？
5. 为什么 PS-RSLG 和 PS-RSLE 混用？
6. 为什么主文还有 TODO？
7. Effective-resolution table 为什么是空的？
8. PBR export 和 recursive connectivity 的关系是什么？
9. Pyrite raw components 为 3，为什么仍作为 positive？
10. One-shot/Hunyuan baselines是不是公平？它们到底被要求做什么？
11. Traditional procedural systems是不是 strawman？如果它们 structural state 很强，PS-RSLE 优势到底在哪里？
12. Full PS-RSLE 的 visual quality 是否来自 root/case selection，而不是方法？

这些问题现在都可以回答，但必须在文中主动回答，不能等 reviewer 自己发现。

## 20. 最终修订优先级

如果只能做一天修改，按这个顺序:

1. 删全部 TODO，补 root/handle transfer 规则，哪怕是 proxy/contract 版本。
2. 统一 `PS-RSLE`、符号、projection signature。
3. 删除空 effective table input；effective-resolution 降级为 selected zoom diagnostic。
4. 把 Experiment 2/4 明确写成 deterministic proxy ablations。
5. 修 `fig:one-branch` caption/Description。
6. 修 Appendix stale table/caption。
7. 在 4.4/4.5 加真实实现范围说明: Trellis2 recursive SLAT workflow 与 export path 分别证明什么。
8. 最后再压缩 Introduction 和 Related Work。

如果能补代码/结果，最高收益是补一个最小真实 Trellis2 per-depth projection/re-encode sidecar。哪怕只覆盖一个 branch/root case，也能把 method 从“semantics + proxy”推进到“semantics with runtime evidence”。

## 21. 结论

这篇文章的主线应该坚决收束到“recursive execution state validity”。不要把论文写成 visual gallery，不要让 masked naturalization、PBR export、effective resolution 抢走主贡献。最好的写法是承认 classical procedural systems 的结构强度，承认 sparse generators/editing 的 realization 强度，然后指出二者都没有提供“每一层递归后可被下一层安全读取的 generator-coupled state”。PS-RSLE 的价值就在这个接口和 invariant。

当前文本最需要修的不是再加图，而是把 claim 和 evidence 对齐。Projection ablation 可以撑住核心故事；Experiment 3 可以撑住 novelty gate；Experiment 4 可以撑住 local surface proxy；Trellis2 export 可以撑住 asset compatibility。除此之外的 claim 都应该降级、移到 appendix、或等真实 runtime sidecar 补齐后再写。
