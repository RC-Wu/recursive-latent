---
id: NOTE-THEORY-DIRECTION-FEASIBILITY-20260507
title: 递归 3D 生成增长理论路线可行性评估
tags: [theory, feasibility, trellis2, recursive_generation, masked_repair, research_direction]
created_at: "2026-05-07T21:04:00+08:00"
---

# 递归 3D 生成增长理论路线可行性评估

本文回到原始 proposal `/Users/fanta/Downloads/recursive_3d_generative_growth_proposal.md`，结合目前已经完成的 Trellis2 基础诊断、mesh-first、递归 grammar、masked repair、blend 消融、texture latent、mesh quality metrics 和 component pruning，重新判断理论部分哪些能继续推进，哪些需要降级，哪些新理论方向值得尝试。

## 0. 当前总判断

原 proposal 的大方向没有被推翻，但理论重心需要收敛。

最初 proposal 的核心表述是：

```text
procedural grammar -> latent rewrite / transform / merge / re-noise
  -> frozen Trellis2 flow naturalization
  -> recursive finite-depth 3D asset
```

现在的实验结果支持更窄、更可靠的版本：

```text
high-quality mesh root
  -> O-Voxel / FDG
  -> shape SLAT
  -> grammar controls sparse coordinate support
  -> weak/mid masked flow blend naturalizes only new coordinates
  -> decode
  -> component pruning / smoothing
  -> optional texture latent
```

也就是说，值得继续做的理论主线不是“证明 Trellis2 是任意递归结构的通用生成器”，而是：

> 冻结的 structured 3D generator 可以作为一个局部自然化算子，但递归拓扑必须由 mesh/O-Voxel/SLAT 层的显式 grammar 和投影/剪枝机制控制。

这个版本更弱，但更可实验、更接近现在的正结果，也更容易形成可辩护的论文主张。

## 1. 实验现象到理论判断

| 实验现象 | 理论含义 | 对 proposal 的影响 |
|---|---|---|
| zero-condition 大量 collapse，成功 seed 也多是薄片/碎片 | Trellis2 不是无条件稳定采样器；必须有有效 condition 或 native latent state | 不能把“flow prior 自然产生结构”作为理论起点 |
| handcrafted feature proxy scale 弱则空、强则爆 | 非语义条件不能提供稳定 manifold projection | 不能继续把任意 scaffold 图像视为有效条件 |
| 官方 DINOv3 对正常 object-like image 有效，对程序线稿/点图失败 | 条件分布很关键；问题主要在表示适配，不在环境 | image-entry 只能作为 first mesh 入口，不能作为主理论路线 |
| mesh -> O-Voxel/FDG -> shape SLAT -> decode 保结构 | Trellis2 native geometry interface 可以承载递归 coarse structure | mesh-first 是主线 |
| sparse coordinate mirror/copy 可以 bounded decode | SLAT 坐标支持有限的空间 rewrite | 递归算子应定义在 sparse coordinates/features 上 |
| recursive grammar over shape SLAT 完整跑通 | grammar 可以控制 token 拓扑增长 | “grammar-as-sampler”成立，但目前更像 coordinate grammar |
| full flow repair 更生成式但 blob/sheet drift | 全量 flow 会覆盖结构先验，存在 topology erasure | 不宜用全局/全强度 naturalization |
| masked repair 比 full repair 稳定 | 保留旧 feature、只采样新坐标是合理分工 | 支持“local naturalizer”理论 |
| blend alpha 0.25/0.5 优于 alpha 1 | naturalization strength 存在 preservation-quality trade-off | alpha/tau 曲线可成为核心理论诊断 |
| image-entry root 的 sheet/grid artifact 被递归继承 | masked repair 是保守算子，不会修复坏 root | root quality 是上限变量，需要理论化 |
| component pruning 大幅降低 fragmentation | projection/post-process 可以稳定递归输出 | 可引入“grammar + naturalizer + projection”三段式理论 |

## 2. 最值得继续推进的理论主线

### 2.1 主线 A：Grammar 控拓扑，Trellis2 控局部自然化

这是当前最强的理论主线。

设 shape SLAT state 为：

$$
S_k=(C_k,F_k),
$$

其中 $C_k\subset\mathbb{Z}^3$ 是 sparse coordinate support，$F_k$ 是每个 coordinate 的 shape latent feature。递归 grammar 先产生新的坐标集合：

$$
\tilde C_{k+1}=G_r(C_k),
$$

然后对旧坐标和新增坐标分开处理：

$$
F_{k+1}(c)=
\begin{cases}
F_k(c), & c\in C_k,\\
\alpha F_{\theta}(c\mid \tilde C_{k+1},q) + (1-\alpha)F_{\text{copy}}(c), & c\in \tilde C_{k+1}\setminus C_k.
\end{cases}
$$

这里 $F_\theta$ 是 Trellis2 shape flow 采样出来的新坐标 feature，$F_{\text{copy}}$ 是 grammar copy/transform 传播来的 feature，$\alpha$ 是 repair strength。

这个 formulation 直接解释了已经看到的现象：

- $\alpha=1$ 时，Trellis2 对新增区域接管太强，容易过密、blob/sheet drift；
- $\alpha=0$ 时，只是 latent copy，不一定自然；
- $\alpha=0.25/0.5$ 是当前实验上更好的折中；
- 旧坐标保留原 feature，所以坏 root artifact 会被继承。

可行性：高。

这条线已经有完整 executable baseline 和数值/视觉证据。它也最像可以写进方法章节的核心算法。

### 2.2 主线 B：Preservation-Naturalization Pareto 曲线

原 proposal 中的“re-noise preservation curve”现在应改成更一般的 preservation-naturalization trade-off。当前最清楚的控制变量不是只有 $\tau$，而是至少包括：

- flow steps；
- blend strength $\alpha$；
- grammar type；
- mask 范围；
- post-process pruning threshold。

可以定义：

$$
P(\alpha)=\operatorname{Preserve}(S_{\text{grammar}},S_{\text{out}}),
$$

$$
N(\alpha)=Q(S_{\text{out}})-Q(S_{\text{raw grammar}}),
$$

目标不是最大化单个指标，而是找 Pareto frontier：

```text
high preservation + enough naturalization + bounded fragmentation
```

已有证据：

- full masked L-system 更连通但视觉过密；
- weak blend L-system 视觉更自然但 fragmentation 更高；
- pruning 后 weak blend 的 largest component ratio 从约 `0.62` 提升到 `0.77-0.83`。

可行性：高。

这可以成为论文中最核心的实证-理论图：Trellis2 不是越强越好，递归任务需要受控、局部、弱生成。

### 2.3 主线 C：Root Quality / Error Inheritance

当前最重要的负结果之一是：image-entry root 一旦有 sheet/grid artifact，后续 masked/blend repair 基本会继承它。这个现象可以理论化为“保守 masked operator 的误差继承”。

设 root error 为：

$$
e_0=d(D(S_0), X^\star_0),
$$

递归步骤分成旧区域 $O_k$ 和新增区域 $N_k$。如果旧区域 feature 被保留，则旧区域误差不会被算法主动修复：

$$
F_{k+1}|_{O_k}=F_k|_{O_k}.
$$

因此至少在 latent feature 层面，root artifact 是 invariant 的。decoder 的全局相互作用可能改变表面形态，但不能指望它系统性消除旧 root 的错误。

这解释了：

- image-entry L-system warm 的 sheet/grid artifact 在后续递归中持续存在；
- object-like image entry 可以做 first mesh，但 first mesh 质量决定 ceiling；
- mesh-first 的传统高质量粗 mesh 比“让 Trellis2 猜线稿”更合理。

可行性：高。

这个方向可以写成方法设计原则，而不是大定理：递归生成的第一层必须尽量在 native geometry manifold 上。

### 2.4 主线 D：Projection-Stabilized Recursive Operator

component pruning 的结果非常关键。它说明递归生成可以被看成：

$$
S_{k+1}=P_\lambda\left(\mathcal{N}_{\theta,\alpha}(G_r(S_k))\right),
$$

其中：

- $G_r$：grammar rewrite；
- $\mathcal{N}_{\theta,\alpha}$：weak masked Trellis2 naturalizer；
- $P_\lambda$：投影/剪枝/合法化算子。

目前的 $P_\lambda$ 很简单：

```text
keep largest component
keep components with vertices >= lambda
remove the rest
```

但它已经把上万个 floating components 降到十几个 retained components，并显著提高 largest component ratio。

这里有一个可以严格证明的小性质：如果只删除非最大连通分量，那么最大分量占比不会下降。设最大分量大小为 $L$，总大小为 $T$，删除一部分非最大分量大小 $R$ 后：

$$
\frac{L}{T-R}\ge \frac{L}{T}.
$$

所以 fragmentation score $1-L/T$ 不会因为这种剪枝变差。这个性质很小，但很干净，适合支撑“projection stabilizes recursive output”的工程理论。

可行性：高。

下一步应把 pruning 从 final post-process 提前到每个递归 depth 之后，测试是否能抑制 error accumulation。

### 2.5 主线 E：Transform Compatibility / Approximate Equivariance

原 proposal 中的 transform-denoise equivariance：

$$
\Phi_\theta(Tx)\approx T\Phi_\theta(x)
$$

仍然是好理论，但现在不能过度声称。

实验上我们只证明了较弱事实：

- mirror/copy/shift sparse coordinates 后可以 decode；
- 某些 coordinate rewrite 不会立刻爆炸；
- full flow repair 可能自然化，也可能漂移。

要真正做 TDE，需要能比较：

```text
transform -> flow
flow -> transform
```

并且要在同一 condition、同一 timestep 或近似 flow state 上对齐。Trellis2 sampler hook 如果不好接，可以先做弱替代指标：

1. **Decoder transform compatibility**
   $$
   D(TS)\approx T D(S)
   $$
2. **Repair transform stability**
   $$
   D(\mathcal{N}_\theta(TS)) \text{ 是否仍保持 } T \text{ 后的 bbox/PCA/skeleton}
   $$
3. **Grammar outcome boundedness**
   $$
   \frac{\operatorname{extent}(S_{k+1})}{\operatorname{extent}(S_k)},\quad
   \frac{|C_{k+1}|}{|C_k|},\quad
   \frac{\#\operatorname{components}_{k+1}}{\#\operatorname{components}_{k}}
   $$

可行性：中。

它很适合做诊断图，但暂时不应作为论文主贡献。论文里可以说“we empirically characterize transform compatibility”，不要说“we prove Trellis2 is equivariant”。

### 2.6 主线 F：弱收缩 / 递归稳定性

原 proposal 写了弱 contraction：

$$
d(\mathcal{F}(x),\mathcal{F}(y))\le \alpha d(x,y)+\epsilon.
$$

这个方向有启发，但目前不能按定理写。原因是：

- Trellis2 flow 的 Lipschitz 常数未知；
- sparse coordinate merge 是离散/非光滑的；
- decoder 可能产生全局拓扑变化；
- full flow repair 的 blob/sheet drift 已经说明强 naturalization 不稳定。

但可以改成更实际的“递归稳定性预算”：

$$
M_{k+1}\le b_r M_k + a_\theta M^{new}_k - p_\lambda M^{small}_k,
$$

其中 $M_k$ 可以是 token 数、组件数、bbox extent 或 face count。这里：

- $b_r$ 来自 grammar branching factor；
- $a_\theta$ 来自 flow/blend 引入的额外碎片或表面密度；
- $p_\lambda$ 来自 projection/pruning 删除的小组件。

这个 recurrence 不需要证明 Trellis2 是 contraction，只需要实测每一项的增长系数。它和现有 metrics 非常匹配。

可行性：中到高。

建议作为“empirical stability model”，而不是数学定理。

### 2.7 主线 G：Persistent Topology Stability

原 proposal 提到如果 Hausdorff 扰动小于拓扑 persistence margin，则大尺度拓扑特征稳定。这个理论方向是对的，但目前还没有实验基础。

可以保留为评估工具：

1. 从 mesh 采样 point cloud；
2. 计算 persistent homology 或更轻量的 component/tree skeleton proxy；
3. 比较 grammar scaffold、raw copy、masked repair、blend repair、pruned output；
4. 看哪些 topology features 在 repair 后保留。

但不要声称 Trellis2 满足小 Hausdorff 扰动。已有 full flow repair 的 sheet/blob drift 说明这个假设经常不成立。

可行性：中。

适合做补充指标，不适合作当前主理论。

## 3. 可以继续做的原 proposal 内容

### 3.1 继续做：Recursive Fractal Asset Growth

这是最可行的任务。应该继续，但定义要收窄：

- 主形态：tree/root/coral/cluster；
- 主入口：mesh-first；
- 主算子：SLAT sparse coordinate grammar；
- 主 naturalizer：weak/mid masked flow blend；
- 必需 post-process：component pruning，之后再 smoothing/remeshing。

当前最佳子方向：

```text
L-system or space-colonization high-quality mesh root
  -> fork / fork_side grammar
  -> alpha 0.25/0.5 masked blend
  -> per-depth pruning
  -> texture latent
```

### 3.2 继续做：Transform / Rewrite Operator Diagnostics

仍然重要，但实验目标要从“证明 equivariance”改成“建立 safe operator table”：

| Operator | 当前判断 |
|---|---|
| translate/copy high-y/high-z subset | 已有正信号，可继续 |
| mirror | 可 decode，适合作 symmetry/IFS |
| scale-center duplicate | bounded，但容易加厚/重叠 |
| fork/fork_side | 当前最强 |
| full flow repair | 有生成性，但应降级为对照 |
| masked weak blend | 主路线 |

### 3.3 继续做：Preservation-Naturalization Evaluation

这应成为论文评估骨架。指标至少包括：

- token growth；
- vertex/face growth；
- connected components；
- largest component ratio；
- fragmentation；
- PCA linearity/planarity；
- bbox drift；
- visual contact sheet；
- texture/PBR voxel success；
- root-to-final morphology preservation。

### 3.4 谨慎继续：Droste / Escher / Illusion

这些仍然有艺术和展示价值，但不适合作当前核心论文路线。

原因：

- 现在 asset-level recursive growth 刚刚打通；
- scene-level composition 比 branch/cluster growth 多了相机、portal、局部语义一致性；
- Trellis2 image-entry 对非普通条件仍不稳定。

建议把 Droste 改成后续 demo：

```text
simple arch/frame mesh root
  -> mesh-first SLAT
  -> portal coordinate transform
  -> local weak repair
  -> target-view render
```

它可以验证“recursive embedding”，但不应挤占主线。

## 4. 应该停止或降级的理论说法

### 4.1 停止：Trellis2 可以直接理解任意递归 scaffold

实验已经反证。程序线稿/点图对 DINOv3-conditioned Trellis2 是 out-of-distribution，不能作为主理论。

### 4.2 停止：full flow repair 会单调提升自然性

full repair 更生成式，但 blob/sheet drift 明显。理论上它不是 local naturalizer，而是强 prior projection，可能删除或重写 topology。

### 4.3 降级：弱 contraction theorem

目前没有条件证明 Trellis2 flow 是 contraction。可以改成 empirical boundedness/stability recurrence。

### 4.4 降级：true infinite geometry

只能说“finite-depth realization of a recursive program”。无限性是 grammar 的潜在延展性，不是输出资产属性。

### 4.5 降级：image-entry root 作为主路线

image-entry 可以从图片得到第一 mesh，但 root 质量不稳定。理论上它是 optional initialization，不是核心递归 operator。

## 5. 新理论方向

### 5.1 Branch Attachment Field

当前 fork/fork_side 还是比较粗的 coordinate copy。下一步可以引入 attachment field：

$$
A(c)=\Pr(c\text{ is a valid growth attachment site})
$$

它可以由 local PCA、skeleton tip、component boundary、curvature 或 grammar state 定义。然后 grammar 不再盲目复制高坐标区域，而是只在 attachment candidates 上生长。

可行性：高。

这可以解释和改善 IFS 条带化：问题可能不是 Trellis2 完全失败，而是复制区域不是语义上的 branch tip。

### 5.2 Grammar-Projected Flow

不要让 flow 直接决定坐标集合，只让它决定 feature。每次 flow 后再投影回 grammar-allowed coordinate support：

$$
C_{k+1}=P_G(C^\theta_{k+1})
$$

或者更保守：

$$
C_{k+1}=G(C_k),\quad F_{k+1}=P_F(F^\theta_{k+1}).
$$

当前 masked repair 已经接近这个思想。可以进一步做：

- 坐标完全由 grammar 决定；
- feature 由 Trellis2 给；
- 小组件由 projection 删除；
- branch smoothing 由 geometry operator 修。

可行性：高。

### 5.3 Per-Depth Projection Loop

目前 pruning 是最终后处理。理论上更合理的是每一层递归后投影：

```text
for depth:
  grammar expand
  weak repair
  decode or latent proxy metric
  prune/project
  re-encode
```

这会把 projection 变成递归算子的一部分，可能显著减少 error accumulation。

风险是每层 decode/re-encode 成本高，但可以先在 depth 2/3 上验证。

可行性：高。

### 5.4 Root Mesh Quality Theory

可以系统测试 root mesh quality 对最终结果的影响：

```text
raw L-system
smoothed L-system
space-colonization tree
thickened/remeshed L-system
Trellis2-generated tree recycled root
image-entry root
```

理论问题：

> 在 conservative masked recursive generator 中，root quality 是否决定最终可用性上限？

这和已有 image-entry 负结果高度一致。

可行性：高。

### 5.5 Low-Training Controller

如果允许很小训练量，最值得训练的不是新 3D generator，而是一个很小的 controller：

```text
local SLAT neighborhood + grammar state
  -> attachment score
  -> alpha / steps / pruning threshold
  -> feature blend weights
```

训练监督可以来自程序生成 pairs 和已有 metrics/pseudo-label。Trellis2 仍然冻结。

可行性：中。

这比训练 adapter 更轻，也更贴近当前实验证据。它可以成为第二阶段贡献，但当前论文主线最好先保持 training-free。

### 5.6 Texture After Geometry Stabilization

texture latent 已经能接上最终递归候选。理论上应把 texture 从 topology 控制中分离：

```text
geometry recursion first
projection/pruning/smoothing second
texture latent last
```

原因是 texture flow 不解决拓扑错误；过早 texture 只会增加评估复杂度。

可行性：高。

## 6. 推荐论文主张

当前最稳的 paper framing：

> We repurpose a frozen structured 3D generator as a local naturalization operator inside a recursive grammar, by keeping recursive topology in mesh-derived sparse SLAT coordinates and using weak masked flow only to synthesize features for newly grown regions.

中文表述：

> 本文研究如何把冻结的 structured 3D 生成模型从一次性 asset generator 重新解释为递归 grammar 的局部自然化算子。核心不是让模型自由生成递归拓扑，而是在 mesh/O-Voxel/SLAT 中显式控制拓扑，并用弱 Trellis2 flow 对新增区域进行局部 feature 自然化。

主贡献建议保留三个：

1. **Mesh-rooted sparse latent grammar**：把传统递归结构转换为 Trellis2 native sparse latent rewrite，而不是 2D scaffold guidance。
2. **Weak masked flow naturalization**：旧结构保留，新坐标弱 flow blend，自然化强度由 $\alpha$ 控制。
3. **Projection-stabilized recursive evaluation**：用 pruning/fragmentation/Pareto curve 分析递归稳定性和 asset usability。

不要把贡献写成：

- 新 3D generator；
- 通用无限递归生成；
- 任意 transform equivariance 证明；
- scene-level Droste/illusion 主任务。

## 7. 下一批理论驱动实验

### 实验 1：Per-depth pruning vs final pruning

问题：

> projection 是否能稳定递归深度，而不只是最后清理结果？

对照：

- final-only pruning；
- depth-1/2/3 每层 pruning；
- 不 pruning。

指标：

- components；
- largest ratio；
- visual branch continuity；
- face count；
- texture latent success。

优先级：最高。

### 实验 2：Attachment-aware grammar

问题：

> IFS 条带化和 L-system 过密是否来自 patch selection 不够语义化？

方法：

- skeleton/PCA tip selection；
- branch boundary selection；
- local tangent frame fork；
- 和当前 high-y/high-z subset copy 对照。

优先级：最高。

### 实验 3：Root quality sweep

问题：

> conservative masked generator 的最终质量是否主要由 root mesh 决定？

root：

- raw L-system；
- smoothed/thickened L-system；
- space colonization；
- DLA cluster；
- Trellis2 example tree recycled mesh；
- image-entry mesh。

优先级：高。

### 实验 4：Alpha-depth schedule

问题：

> 是否应该让 $\alpha$ 随 depth 变化？

候选：

- constant alpha 0.25；
- early high, late low；
- early low, late high；
- alpha by local component size。

假设：

- early high 可能改善粗 surface，但风险是拓扑漂移；
- late high 可能只增加局部密度；
- alpha by local size 可能最稳。

优先级：中高。

### 实验 5：Weak TDE / decoder compatibility table

问题：

> 哪些 transform 在 Trellis2 SLAT decoder/repair 下是安全的？

先做弱版：

- mirror；
- translate；
- scale；
- rotate 90；
- fork copy；
- portal scale-insert。

指标：

- bbox drift；
- component growth；
- largest ratio；
- feature/token growth；
- visual decode success。

优先级：中。

## 8. 结论

现在项目最有希望的理论不是“大而泛”的递归生成理论，而是一个更具体的结构：

```text
grammar defines support
frozen generator defines local feature naturalization
projection defines recursive stability
texture comes after geometry stabilizes
```

这四句话能解释几乎所有当前实验现象：

- 2D scaffold 失败：support 没进入 native geometry space；
- mesh-first 成功：support 正确；
- full repair 漂移：generator 接管了过多结构；
- weak blend 成功：generator 只做局部 feature；
- image-entry artifact 继承：旧 support/feature 被保守保留；
- pruning 有效：projection 修正了递归累积的小组件错误。

因此，下一步最值得投入的是：per-depth projection、attachment-aware grammar、root quality sweep，以及把 preservation-naturalization trade-off 系统化为论文级指标。
