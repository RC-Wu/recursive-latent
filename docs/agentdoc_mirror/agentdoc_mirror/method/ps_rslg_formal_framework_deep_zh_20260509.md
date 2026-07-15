# PS-RSLG / Recursive Sparse-Latent Grammar 的形式化方法框架（深版中文草稿）

创建时间：2026-05-09  
项目：Recursive 3D Generative Growth / SIGGRAPH Asia method-theory writing  
写作范围：只讨论方法与理论表述；不修改 `paper_siga/main.tex`；不声明远程实验结果之外的强结论。

## 0. 核心立场

本文档把当前方法从

```text
root mesh -> sparse latent edit -> decode -> projection -> re-encode -> texture
```

这种容易被 reviewer 读成“模块串联”的叙述，改写为一个递归语法演算：

```text
typed handles + sparse latent support
-> local rule proposal
-> masked merge / competition
-> masked frozen sampler naturalization
-> projection to admissible connected state
-> re-encode and update handles/caches
```

核心 claim 是：

> PS-RSLG 是定义在冻结 3D 生成模型原生 sparse latent state 上的递归重写演算。语法拥有拓扑、锚点、frontier、transform、cache 与投影约束；冻结生成模型只作为 masked local sampler、codec 和 material/export prior。Projection 被放进每一步递归转移，因此 connected support 是递归状态不变量，而不是最终 mesh cleanup 的视觉修补。

这个 claim 的边界必须清楚：

- 可以说：IFS、L-system、space colonization、DLA/frontier growth、有限 shape grammar、对称 transform-copy 都是该演算的限制实例或自然嵌入。
- 可以说：flow/SDE 在该框架中被自然化为 hard-mask local sampler，而不是全局 repair。
- 可以说：在假设 projection 和 codec round trip 有界误差时，每层状态有 connected/admissible invariant；final-only cleanup 没有这个递归不变量。
- 可以说：infinite recursion 目前只能作为 contractive limit 或 finite-memory LOD/window stream 的语义扩展。
- 不能说：当前方法已经实现严格无限 3D mesh、严格物理 DLA/crystal simulation、严格群等变生成、或所有 shape grammar 的完全覆盖。

## 1. 问题定义：递归资产生成而不是一次性 3D 生成

给定 root asset \(x_0\)、可选条件 \(y\)（image/text/category/material guide）、冻结 native 3D generator 参数 \(\theta\)、递归程序 \(\mathcal G\) 和有限深度 \(D\)，目标是生成可渲染资产

\[
x_D=\mathcal O(z_D),
\qquad
z_{d+1}\sim
\mathsf T_{\mathcal G,\theta,d}(\cdot\mid z_d,y,\xi_d),
\quad d=0,\ldots,D-1.
\]

这里 \(\xi_d\) 表示 rule choice、frontier sampling、DLA hitting、flow/SDE sampling、sample selection 等随机性。和 one-shot image-to-3D 不同，递归程序不把整个对象交给生成器重画。程序必须在每一层保留可寻址的 sparse support、anchors、frontier 与 ownership；生成器只在局部编辑区域提供形状与材质先验。

因此，PS-RSLG 的任务不是“让 3D 生成模型理解递归”，而是：

\[
\text{recursive grammar owns structure}
\;+\;
\text{frozen generator supplies local realization}
\;+\;
\text{projection stabilizes each recursive state}.
\]

这句话应该成为论文方法节的主线。

## 2. 最小状态：避免大元组，把语义压到三件事

Reviewer 批评的关键点是状态变量不能像工程清单。主文应只保留最小状态：

\[
z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d).
\]

其中：

- \(\mathcal V_d\subset h\mathbb Z^3\) 是 active sparse token support，可理解为 O-Voxel/SLAT 风格的稀疏坐标支撑；
- \(\mathbf F_d:\mathcal V_d\rightarrow\mathbb R^q\) 是每个 token 的生成器原生 latent feature，可包含 shape feature、可选 material feature 和少量 grammar auxiliary code；
- \(\mathcal A_d\) 是 grammar-readable anchor structure，包括 typed handles、局部 frame、frontier label、attachment graph、ownership region、material handle 和 LOD/cache descriptor。

一个 handle 写为

\[
h_i=(\sigma_i,T_i,\Omega_i,\alpha_i).
\]

这里 \(\sigma_i\in\Sigma\) 是类型，\(T_i\) 是 local-to-world frame，\(\Omega_i\subseteq\mathcal V_d\) 是该 handle 管辖或指向的 support，\(\alpha_i\) 是属性，如 branch radius、age、rule priority、material tag、LOD level、cache id。

辅助 bookkeeping 不进入主状态定义，而是在执行器中作为

\[
\mathcal B_d=
\{\text{masks, caches, seeds, rule traces, projection parameters, material/export metadata}\}
\]

使用。这样读者只需要记住：

> 当前递归状态是一组 sparse latent tokens，加上语法能读写的 anchors/handles。

复杂实现细节仍然可以存在，但它们不应该支配方法节的数学表述。

## 3. Connected-support invariant：碎片是状态错误，不是视觉瑕疵

### 3.1 Sparse adjacency graph

给定 sparse support \(\mathcal V\)，定义 \(\eta\)-邻接图

\[
G_\eta(\mathcal V)=(\mathcal V,E_\eta),
\qquad
(p,q)\in E_\eta
\Longleftrightarrow
\|p-q\|_1\le \eta h.
\]

实现上可用 6-neighborhood / 18-neighborhood / 26-neighborhood。建议论文主指标用 occupancy 6-neighborhood proxy，因为它比 raw face connectivity 更适合比较 tube baselines、GLB meshes 和稀疏 voxel proxy。

令 \(R_d\subset\mathcal V_d\) 是 root support 或 root anchors。定义 root-attached support：

\[
\mathcal V_{\mathrm{att}}(z_d)=
\{v\in\mathcal V_d:\exists r\in R_d,\; v\leadsto r
\text{ in }G_\eta(\mathcal V_d)\}.
\]

连通性 violation：

\[
V_{\mathrm{conn}}(z_d)=
1-\frac{\operatorname{mass}(\mathcal V_{\mathrm{att}}(z_d))}
{\operatorname{mass}(\mathcal V_d)+\epsilon}.
\]

更严格地，PS-RSLG 不只要求 voxel 连接，还要求 active handle 不孤立：

\[
\forall h_i\in\mathcal A_d^{\mathrm{active}},\qquad
\operatorname{path}_{\mathcal A_d}(h_{\mathrm{root}},h_i)
\text{ exists}.
\]

一个 floating chunk 如果进入 \(\mathcal A_d\) 并成为 active frontier、motif source 或 sampler condition，它就会污染之后所有递归层。因此它不是“最后删掉就好”的几何残余，而是递归状态错误。

### 3.2 Admissible connected state set

定义可接受状态集合：

\[
\begin{aligned}
\mathcal Z_{\mathrm{adm}}(\lambda)=
\{z:\;&
V_{\mathrm{conn}}(z)\le\epsilon_c,\;
V_{\mathrm{frontier}}(z)=0,\;
V_{\mathrm{occ}}(z)\le\epsilon_o,\;
V_{\mathrm{attach}}(z)\le\epsilon_a,\\
&
V_{\mathrm{sym}}(z)\le\epsilon_g,\;
V_{\mathrm{mat}}(z)\le\epsilon_m,\;
|\mathcal V(z)|\le T_{\max}\}.
\end{aligned}
\]

关键项是 \(V_{\mathrm{frontier}}(z)=0\)：每个 active frontier 或 growth handle 必须有 root-attached path。允许存在未展开的 symbolic/LOD/cache descriptor，但它们不能作为下一层 visible frontier，除非先 materialize 并通过 projection。

### 3.3 不变量

PS-RSLG 的中心不变量是

\[
\boxed{\qquad
z_d\in \mathcal Z_{\mathrm{adm}}(\lambda_d),
\quad d=0,\ldots,D.
\qquad}
\]

这不是说每个 mesh 在视觉上完美，而是说每层递归状态都满足“可继续递归”的基本合法性：可寻址、可连接、可渲染、不过预算、frontier 不孤立。

## 4. 语法演算：三类对象而不是巨大 tuple

主文不要写一个超长 grammar tuple。建议把语言定义为三类对象：

\[
\mathcal L_{\mathrm{PS\text{-}RSLG}}
=
(\text{typed handles},\text{rules},\text{realization operators}).
\]

### 4.1 Typed handles

Typed handles 是语法可选择、可改写、可连接、可缓存的对象：

\[
h_i=(\sigma_i,T_i,\Omega_i,\alpha_i).
\]

常见类型包括：

- `Root`：根支撑；
- `Tip` / `Frontier`：可生长边界；
- `Branch`：分叉结构；
- `Patch` / `Motif`：可 transform-copy 的局部块；
- `Attractor`：space-colonization style 目标；
- `CrystalFace` / `Orbit`：晶格或对称扩展对象；
- `Tile` / `Portal`：shape grammar / transform-copy 单元；
- `LODChunk` / `Descriptor`：未完全展开的 cache 或 window 节点；
- `MaterialSeed`：材质继承和 export guide。

### 4.2 规则模板

核心规则模板写为

\[
\rho:\ h_i\mapsto
\{(\sigma_j,\tau_j,\Omega_j,m_j,\kappa_j,\pi_j,\eta_j)\}_{j=1}^{k}.
\]

各项含义：

- \(\sigma_j\)：生成或更新的 handle type；
- \(\tau_j\)：局部 transform，可以是 translation、rotation、scale、mirror、portal embedding、contractive map、lattice action；
- \(\Omega_j\)：目标区域或 ownership region；
- \(m_j\)：edit mask / blend mask；
- \(\kappa_j\)：feasibility condition，如 collision-free、attached、reachable、budgeted、symmetry-closed；
- \(\pi_j\)：proposal kernel，如 grow、branch、copy、attach、split、refine、cache lookup；
- \(\eta_j\)：randomness/sampler schedule/material condition。

规则模板的重点不是“复制几何”，而是生成一个带条件、mask、ownership、attachment 语义的 local edit program。

### 4.3 代表性规则族

| Rule family | Proposal kernel | 语义 | 用途 |
|---|---|---|---|
| grow | frontier extension | 从 attached tip 延伸局部 support | vines, roots |
| branch | handle split | 一个 handle 分裂为多个 attached child handles | trees, bushes |
| attach | frontier hit / bridge certificate | 接受靠近主 scaffold 的 frontier attachment | DLA, porous growth |
| copy | transform patch | 对 connected motif 做变换复制 | ornaments, portals |
| split/extrude | local frame decomposition | 按 frame 对面、块、tile 做切分/挤出 | shape grammar, architecture |
| refine | local densification | 对 terminal region 加细节，预算受 LOD 控制 | zoom/terminal detail |
| material | material handle transport | 继承、复制或混合材质意图 | PBR/export consistency |
| cache | descriptor lookup | 从 motif/latent/LOD cache 中取出局部 program | infinite/LOD proxy |

### 4.4 可行性条件：projectable reachable domain

对 proposal \(\Delta\mathcal V\)，不能只问它局部看起来是否合理，还要问它是否能成为下一层递归的合法状态。可行性写为

\[
\Delta\mathcal V\subset
\mathcal R_{\mathrm{proj}}(z_d;b_d,r_d),
\]

或存在 bridge certificate

\[
\exists B:\quad
\Delta\mathcal V\cup B\in
\mathcal Z_{\mathrm{adm}}(\lambda_d),
\qquad
\operatorname{cost}(B)\le b_d.
\]

其中 \(\mathcal R_{\mathrm{proj}}\) 是可投影可达区域，受距离、collision、occupancy、token budget、material seam 和 symmetry orbit 约束。这个条件使 PS-RSLG 区别于普通 latent editing：一个 patch 只有在能连回递归 scaffold 时才可以成为 active state。

## 5. 操作语义：递归程序执行

给定 \(z_d\)，一次递归转移不是一条线性 pipeline，而是一个语义步骤：

\[
z_{d+1}
=
\operatorname{Enc}_\theta
\Big[
\Pi_{\lambda_d}
\big(
\operatorname{Dec}_\theta(
\mathcal T_\theta(z_d;\mathcal R_d,y)
)
\big)
\Big].
\]

其中

\[
\mathcal R_d=\operatorname{SelectRules}(z_d,\mathcal G)
\]

是当层选中的规则集合，而

\[
\mathcal T_\theta
=
\operatorname{Naturalize}_{\theta,m_d}
\circ
\operatorname{Compete}
\circ
\operatorname{Merge}
\circ
\operatorname{Prop}_{\mathcal R_d}
\]

只在局部 rule mask 内操作。

展开为算法：

1. 从 \(\mathcal A_d\) 中选择 active handles。
2. 根据类型、depth、frontier、budget、symmetry orbit 和 cache 状态选择规则 \(\mathcal R_d\)。
3. 对每条规则生成 sparse proposals：\(\operatorname{Prop}_{\mathcal R_d}(z_d)\)。
4. 拒绝 projectable domain 外的 proposal，除非它带有有效 bridge certificate。
5. 用 masks 和 blend kernels 合并 support/features/material handles：

   \[
   \tilde z_{d+1}=
   \mathcal M(z_d,\operatorname{Prop}_{\mathcal R_d}(z_d)).
   \]

6. 在 proposal 区域做 occupancy competition、thinning、collision rejection、orbit completion。
7. 需要时，用冻结 flow/SDE sampler 在 hard mask 内做 local naturalization：

   \[
   \bar z_{d+1}=
   \mathcal N_\theta(\tilde z_{d+1};m_d,y).
   \]

8. Decode：

   \[
   x_{d+1}=\operatorname{Dec}_\theta(\bar z_{d+1}).
   \]

9. Project 到 connected/admissible asset：

   \[
   x_{d+1}^\star=\Pi_{\lambda_d}(x_{d+1},\mathcal A_d).
   \]

10. Re-encode：

    \[
    z_{d+1}=\operatorname{Enc}_\theta(x_{d+1}^\star).
    \]

11. 更新 anchors/frontiers/material handles/cache/diagnostics，删除 orphan handles 或把不确定 descriptor 标为 inactive。

这个算法的论文表述重点是：decode/project/re-encode 在每一层发生。Projection 不是最后一步视觉清理，而是递归转移的一部分。

## 6. Sparse merge 和 competition

### 6.1 Transform-copy proposal

对 transform-copy rule，连续支撑通过 transform \(\tau_j\) 后量化到 sparse grid：

\[
\widehat{\mathcal V}_j
=
Q_h(\tau_j(\mathcal V_d\cap\Omega_j)).
\]

feature transport：

\[
\widehat{\mathbf F}_j(Q_h(\tau_j v))
=
\mathcal T^F_j\mathbf F_d(v).
\]

masked feature merge：

\[
\mathbf F^+(v)=
\frac{
w_0(v)\mathbf F_d(v)+
\sum_j w_j(v)\widehat{\mathbf F}_j(v)
}{
w_0(v)+\sum_j w_j(v)+\epsilon
},
\qquad
w_j(v)=m_j(v)\beta_j(v).
\]

Material handles 可以同样 transport/merge，但论文中要分开 claim：当前实验最可靠的是 geometry recursion + selected Trellis2 texture/PBR export compatibility；per-depth material recursion 仍是扩展。

### 6.2 Sparse competition score

对候选 action \(a\) 和 sparse token \(v\)，竞争分数可写为

\[
\begin{aligned}
\psi(a,v;z_d)=
{}&
\lambda_{\mathrm{att}}\phi_{\mathrm{att}}
-\lambda_{\mathrm{occ}}\phi_{\mathrm{occ}}
-\lambda_{\mathrm{col}}\phi_{\mathrm{collision}}
+\lambda_{\mathrm{front}}\phi_{\mathrm{frontier}}
\\
&
+\lambda_{\mathrm{grp}}\phi_{\mathrm{orbit}}
+\lambda_{\mathrm{lod}}\phi_{\mathrm{lod}}
+\epsilon_\theta(a,v,\xi).
\end{aligned}
\]

前几项对应 classical procedural logic：attachment、occupancy exclusion、collision、frontier preference、symmetry orbit。最后的 \(\epsilon_\theta\) 是冻结生成器或 sampler 引入的弱随机偏好。当前论文应强调该项是弱项，否则 reviewer 会质疑稳定性来自 prompt/random sampling 而不是语法结构。

## 7. Flow / SDE naturalization：冻结生成器是 masked sampler

### 7.1 SDE/flow 形式

若冻结生成模型以 SDE 表示：

\[
dZ_t=f_\theta(Z_t,t,y)\,dt+g(t)\,dW_t,
\qquad t:\tau_d\rightarrow0.
\]

若以 deterministic flow 表示：

\[
\frac{dZ_t}{dt}=v_\theta(Z_t,t,y).
\]

PS-RSLG 中的 naturalization 不是全局运行这个 sampler，而是在语法给出的 mask 上运行：

\[
Z_{t-\Delta t}
=
(1-m_d)\odot Z_{\mathrm{anchor}}
+
m_d\odot\Phi_{\theta,t}(Z_t,y).
\]

这里 \(Z_{\mathrm{anchor}}\) 是 hard-clamped scaffold state，\(m_d\) 是 rule mask，\(\Phi_{\theta,t}\) 是一步或若干步 frozen sampler update。

对于 sparse feature，可写为

\[
\mathbf f_i'
=
(1-\alpha_i)\mathbf f_i^{\mathrm{rule}}
+
\alpha_i\mathbf f_i^\theta,
\qquad i\in m_d.
\]

其中 \(\alpha_i\) 可以随 depth、mask distance、attachment confidence、rule family 变化。典型安全 schedule 是靠近 anchor 的 \(\alpha_i\) 小，远离 anchor 的 terminal/proposal 区域 \(\alpha_i\) 稍大。

### 7.2 Mask 必须受 connectivity 限制

Naturalization mask 不能只来自用户编辑区域，还要被 projectable/reachable domain 截断：

\[
m_d(v)=0
\quad\text{if}\quad
v\notin \mathcal R_{\mathrm{proj}}(z_d;b_d,r_d).
\]

否则 frozen sampler 可能把局部补全扩散成 floating island 或薄片。论文可以把这个称为 connectivity-clipped masked sampler。

### 7.3 为什么不是 global repair

全局 flow repair 的风险是：

\[
\mathcal N_\theta^{\mathrm{global}}(z_d)
\approx
\arg\max_z p_\theta(z\mid y),
\]

它会向生成器偏好的完整 object manifold 移动，而不是向 grammar-prescribed topology 移动。PS-RSLG 的 sampler 只允许解决局部 surface/feature/material naturalization：

\[
\text{topology from grammar},\qquad
\text{local plausibility from generator}.
\]

这句话可以直接写进论文方法节。

## 8. Projection：bridge-aware projection 而不是 prune-only cleanup

### 8.1 Projection objective

Projection 在 decoded mesh、voxel occupancy 或 occupancy proxy 上执行，然后 re-encode。理想形式：

\[
\begin{aligned}
\Pi_{\lambda}(x)=
\operatorname*{arg\,min}_{y\in\mathcal X_{\mathrm{adm}}(\lambda)}
&
d_{\mathcal X}(x,y)
+
\eta_{\mathrm{obs}}d_{\mathrm{obs}}(x,y)
+
\eta_m d_{\mathrm{mat}}(x,y)
\\
&
+
\lambda_{\mathrm{del}}\operatorname{mass}(R)
+
\lambda_{\mathrm{br}}\sum_{\gamma\subset B}\operatorname{len}(\gamma)
+
\lambda_{\mathrm{front}}V_{\mathrm{frontier}}(y).
\end{aligned}
\]

其中 \(R\) 是删除的 orphan support，\(B\) 是加入或认证的 bridge support。Prune-only projection 是 \(\lambda_{\mathrm{br}}\rightarrow\infty\) 的退化情况。

Bridge 候选路径：

\[
\Gamma(Q,R_d)=
\{\gamma=(q_0,\ldots,q_T):
q_0\in Q,\ q_T\in R_d,\ 
q_{t+1}-q_t\in\mathcal N_\eta\}.
\]

论文中的实现可写得保守：当前主要实现近似为 component selection、attachment-aware pruning、optional bridge/weld/remesh、re-encoding；更完整的 bridge-aware projection 是方法扩展和下一步实验方向。

### 8.2 Projection 步骤

一层 projection 可以描述为：

1. 从 decoded asset 建立 mesh/occupancy connectivity graph。
2. 由 root anchors 找 root-attached components。
3. 对每个 component 计算 mass、bridge cost、renderability、material seam、rule ownership。
4. 保留 root-attached components 和低成本可桥接 components。
5. 删除不可桥接 orphan support，或将其对应 handle 标为 inactive descriptor。
6. 可选地做 weld、gap closing、remesh、bridge insertion。
7. 更新 \(\mathcal A_d\)：删除 orphan frontier，重新绑定 surviving handles。
8. 验证 token budget、frontier connectedness、material seam、renderability 后 re-encode。

## 9. Projection stability sketch

令 \(e(z)\) 是坏状态度量，合并 connectivity、orphan frontier、occupancy、material seam、renderability、token budget violation。

假设 projection 使

\[
e(\Pi_{\lambda_d}(x))\le\epsilon_P,
\]

而 decode/re-encode round trip 引入至多

\[
e(\operatorname{Enc}_\theta(\Pi_{\lambda_d}(x)))
\le
e(\Pi_{\lambda_d}(x))+\epsilon_E.
\]

则每层执行后的状态满足

\[
e(z_{d+1})\le\epsilon_P+\epsilon_E.
\]

证明很直接：由操作语义

\[
z_{d+1}
=
\operatorname{Enc}_\theta(
\Pi_{\lambda_d}(
\operatorname{Dec}_\theta(\bar z_{d+1})
)),
\]

先由 projection 把 decoded candidate 拉回 admissible set，再由 codec 误差界得到结论。归纳即可得到

\[
e(z_d)\le\epsilon_P+\epsilon_E,
\qquad d=1,\ldots,D.
\]

final-only cleanup 没有同样不变量，因为错误 component 可以在中间层被：

- 选成 parent handle；
- 当作 frontier 继续生长；
- 存入 motif/cache；
- 作为 sampler condition；
- transport material handle；
- 参与 symmetry orbit completion。

最终删除 geometry 不能撤销这些历史污染。论文中应把这作为 per-depth projection 的核心理论理由。

## 10. 经典系统覆盖草图

这些覆盖草图是“语义包含/退化实例”，不是“视觉质量优于传统方法”的声明。

### 10.1 IFS

IFS 给定一组 contraction maps \(\{\tau_i\}_{i=1}^k\)，Hutchinson 迭代为

\[
K_{d+1}=\bigcup_i \tau_i(K_d).
\]

在 PS-RSLG 中取单一 `Patch` handle，规则族只含 transform-copy：

\[
\rho(h)=\{(\texttt{Patch},\tau_i,\Omega,m_i,\top,\pi_{\mathrm{copy}},0)\}_{i=1}^k.
\]

令 sampler 为 identity、projection 为 identity、feature transport 为常数或 identity、merge 为 union，则

\[
\mathcal V_{d+1}=\bigcup_i Q_h(\tau_i(\mathcal V_d)).
\]

当 \(h\rightarrow0\) 且 \(\tau_i\) 为 contraction 时，它收敛到 Hutchinson attractor 的量化近似。因此 IFS 是 PS-RSLG 的 transform-copy + identity naturalizer 的限制实例。

### 10.2 L-system

L-system 的状态是有序符号串 \(w_d\in\Sigma^\star\)，同步重写

\[
w_{d+1}=P(w_d).
\]

在 PS-RSLG 中让 \(\mathcal A_d\) 存储 ordered handle sequence 或 ordered graph：

\[
\mathcal A_d=(h_1,\ldots,h_n,\operatorname{ord}_d).
\]

规则只改写 symbol/type 和 turtle/frame attributes，realization operator 把 frame sequence 解释为 branch support。若禁用 sampler/projection，或 projection 仅做曲线到 support 的合法化，则标准 turtle L-system 是 typed anchor rewriting 的特例。

### 10.3 Space colonization

Runions-style space colonization 可表示为 tips \(T_d\) 与 attractors \(A_d\)。每个 attractor 分配给最近可见 tip，tip 沿平均方向生长：

\[
\Delta p_t
\propto
\sum_{a\in \operatorname{Attr}(t)}
\frac{a-p_t}{\|a-p_t\|}.
\]

PS-RSLG 中 tips 和 attractors 都是 handles/fields。`grow` rule 的 proposal kernel 根据 attractor assignment 生成新 support；occupancy exclusion 通过 \(\phi_{\mathrm{occ}}\) 实现；attachment 由 tip parent edge 保证。禁用 learned sampler 时，该规则退化为空间殖民树/根生长。启用 masked sampler 时，它只 naturalize 新 branch 附近的 sparse feature，不改变 tip-attractor 拓扑。

### 10.4 DLA / frontier growth

DLA 的核心是随机游走击中 exposed frontier 后附着。PS-RSLG 中定义 frontier handles \(\mathcal F_d\)，proposal kernel 从 hitting distribution 或其近似中采样：

\[
q\sim H(\cdot\mid \mathcal F_d),
\qquad
\Delta\mathcal V=\{q\}
\]

并要求

\[
\operatorname{dist}_{G_\eta}(q,\mathcal V_{\mathrm{att}})\le 1
\]

或存在低成本 bridge certificate。Occupancy exclusion 防止重复占用；projection 删除未附着 random chunks。这样得到的是 frontier accretion 的 grammar approximation。当前论文不能声称严格物理 DLA，只能说 coverage of DLA-like stochastic frontier attachment。

### 10.5 Shape grammar / CGA

有限 shape grammar 可看成 typed face/tile/volume handles 的局部替换：

\[
\texttt{Facade}(T,\Omega)
\mapsto
\texttt{Window}(T_1,\Omega_1)+\texttt{Wall}(T_2,\Omega_2)+\cdots
\]

在 PS-RSLG 中 split、extrude、repeat、replace 都是 proposal kernels；\(\tau_j\) 给 local frame transform，\(\Omega_j\) 给 region ownership，\(\kappa_j\) 给 collision/material/attachment constraints。禁用 learned sampler 时是传统有限 shape grammar；启用 sampler 时可对局部窗口、ornament、portal、material seam 做 naturalization。

### 10.6 Symmetry / crystal / transform-copy

设 \(G\) 是有限群或晶格作用。若 rule set 在 \(G\) 下闭合：

\[
\forall g\in G,\ \forall \rho\in\mathcal R,\qquad
g\circ \rho\circ g^{-1}\in\mathcal R,
\]

且 scheduler 展开完整 orbit，则 proposal support 是 \(G\)-closed。若 merge、sampler、projection、codec、grid quantization 都与 \(G\) 对易，则转移严格等变：

\[
\mathsf T(gz)=g\mathsf T(z).
\]

现实中这些条件不严格成立，尤其是 sparse grid quantization、decoder、projection 和 material export。因此论文应写 approximate symmetry，并用误差界表述：

\[
d_{\mathcal S}(\mathsf T(gz),g\mathsf T(z))
\le
L_{\mathrm{post}}
(\epsilon_{\mathrm{rule}}+\epsilon_{\mathrm{merge}}
+\epsilon_{\mathrm{sampler}}+\epsilon_{\mathrm{proj}}
+\epsilon_{\mathrm{codec}}+\epsilon_{\mathrm{grid}}).
\]

这适合支撑 symmetry/crystal metrics，但不能写成已证明严格 crystal generator。

## 11. Infinite recursion / LOD recursion

当前主实验应声明 finite-depth：

\[
D<\infty,\qquad |\mathcal V_d|\le T_{\max}(d).
\]

无限递归只能作为语义扩展，有两条安全路线。

### 11.1 Contractive recursion

如果 transform-copy 规则全部 contractive：

\[
\operatorname{Lip}(\tau_i)<1,
\]

且 sampler/projection 被禁用或满足 contractive perturbation bound，则逻辑递归定义一个极限集。实际渲染仍是 finite-depth approximation。

### 11.2 Bounded visible-window / LOD stream

定义 active window set \(W_t\)。只 materialize 与当前可见窗口相交的 chunks：

\[
\mathcal V_t^{\mathrm{active}}
=
\bigcup_{\Omega\in W_t}\mathcal V_{\Omega,t},
\qquad
\sum_{\Omega\in W_t}|\mathcal V_{\Omega,t}|
\le T_{\max}.
\]

窗口外区域存为 descriptor：

\[
k=(\operatorname{id},\sigma,\tau,\Omega,\ell,
\mathcal V_\Omega,\mathbf F_\Omega,M_\Omega,
\operatorname{validity},\operatorname{cost}).
\]

当视角或 recursion request 进入该区域时，descriptor materialize 为 sparse proposal，再经过 feasibility、projection、re-encoding。这样可以说：

> PS-RSLG supports infinite logical recursion as a finite-memory stream under LOD/window scheduling.

不能说：

> PS-RSLG outputs an actual infinite 3D mesh.

## 12. Paper-safe claim map

### 12.1 强 claim

- PS-RSLG 把递归 3D asset synthesis 定义为 sparse latent state 上的 typed rewriting。
- Frozen 3D generator 被用作 local masked naturalizer、decoder、encoder、texture/export prior，而不是全局拓扑生成器。
- Projection 在每层递归转移内部，因此 connected support / attached frontier 是 state invariant。
- Classical procedural systems 可作为限制实例嵌入同一个 rule template。
- Per-depth projection 的理论价值是阻止 orphan component 在中间层成为 parent/frontier/cache/sampler condition。

### 12.2 中等 claim

- Space competition 是当前最稳的主线，因为 occupancy exclusion 与 attachment condition 对齐。
- Transform-copy/portal/scale-down 适合展示非树形递归，但质量取决于 root/motif/quantization/projection。
- Symmetry/crystal 可以作为 approximate equivariance metric，而不是严格保证。
- Trellis2 texture/PBR export 可以作为 selected projected meshes 的 asset-readiness evidence。

### 12.3 必须加 caveat 的 claim

- Flow/SDE naturalization：只能 local mask；global repair 会洗掉拓扑。
- DLA/crystal：目前是 frontier/accretion grammar approximation，不是物理仿真。
- Infinite recursion：目前是 logical/LOD/window semantics，不是无限 mesh output。
- Material recursion：当前最安全说法是 projected geometry 后的 compatible texture/PBR export；per-depth material state 是方法扩展。

## 13. 建议论文方法节结构

建议把 Method 重排为：

1. **Problem Setting**：定义 finite-depth recursive asset synthesis。
2. **Minimal Sparse-Latent State**：\(z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d)\)。
3. **Rule Templates**：handle-to-proposal template 与 rule family table。
4. **Operational Semantics**：Algorithm 1 + compact transition。
5. **Masked Flow/SDE Naturalization**：hard-mask sampler。
6. **Connected Projection and Invariant**：admissible state + projection stability sketch。
7. **Classical Systems as Limits**：IFS/L-system/space-colonization/DLA/shape/symmetry。
8. **Finite and LOD Recursion**：finite-depth claim + bounded visible-window extension。

如果篇幅紧，可以把第 7 节压成一个 subsection + table，把证明草图移到 appendix。

