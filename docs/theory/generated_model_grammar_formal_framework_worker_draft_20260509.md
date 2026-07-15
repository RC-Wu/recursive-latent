# 生成模型原生递归语法的形式化方法框架（worker 中文草稿）

创建时间：2026-05-09  
项目：Recursive 3D Generative Growth  
写作范围：formal grammar / theory / SIGGRAPH Asia method draft；本文件只作为支线草稿，不修改 plan、paper 或实验脚本。  
建议方法名：**PS-RSLG: Projection-Stabilized Recursive Sparse-Latent Grammar**。若主文希望更短，可写作 **PS-SLG: Projection-Stabilized Sparse-Latent Grammar**。  

## 0. 一句话主张

本文应把递归 3D 资产生成表述为一个定义在冻结 3D 生成模型原生 sparse latent state 上的递归重写演算：

\[
\text{typed grammar controls topology}
\;+\;
\text{frozen native 3D sampler realizes local geometry/material}
\;+\;
\text{projection stabilizes every recursive state}.
\]

这和“程序化建模 + 最后交给生成模型修一下”有本质区别。语法不是前处理器，而是递归程序；Trellis2/O-Voxel/SLAT 不是黑盒后处理器，而是可解码、可重编码、可局部采样、可缓存的状态空间；projection、competition、cache、LOD 也不是工程补丁，而是规则语义的一部分。

安全且有价值的主文 claim 是：

> PS-RSLG defines recursive 3D asset generation as typed rewriting over the sparse native latent state of a frozen 3D generator. Classical procedural systems are recovered as restricted grammar instances; learned sampling enters as masked local naturalization; projection and competition enforce a per-depth admissible-state invariant.

必须避免的过强 claim 是：

- 不说当前系统已经实现严格无限 3D mesh 输出；
- 不说 frozen sampler 保证拓扑保持；
- 不说已经严格解决 DLA/crystal/physical crystallization；
- 不说导出的所有 textured GLB 都 topology-clean；
- 不说在 matched structural baseline 中 connectivity 系统性击败 L-system 或 space colonization，因为当前公平 occupancy 协议下传统 baseline 也能保持单连通。

## 1. 问题定义

给定 root asset \(x_0\)、可选条件 \(y\)（image/text/category/material guide）、冻结 3D 生成模型参数 \(\theta\)、递归语法程序 \(\mathcal G\) 和有限深度 \(D\)，目标是生成可渲染资产

\[
x_D=\mathcal O(S_D),\qquad
S_{d+1}\sim
\mathbb T_{\mathcal G,\theta,d}(\cdot\mid S_d,y,\xi_d),
\quad d=0,\ldots,D-1.
\]

\(\xi_d\) 包含 rule choice、frontier sampling、DLA hitting、sampler noise、sample selection 等随机性。输出 \(x_D\) 可以是 mesh、textured GLB、render set 或 metric record。本文的任务不是 one-shot image-to-3D，也不是传统 procedural mesh generator，而是有限深度的 recursive asset generation：

\[
\text{root asset}
\rightarrow
\text{sparse native latent state}
\rightarrow
\text{recursive grammar transitions}
\rightarrow
\text{projection-stabilized renderable asset}.
\]

核心限制也应在问题定义中说明：当前论文证明和实验都应围绕 finite-depth assets。无界递归只能作为 contractive limit、visible-window stream 或 cache/LOD descriptor semantics 讨论。

## 2. 状态空间

### 2.1 主文最小状态

主文不宜从一个工程式大元组开始。建议先给出最小状态：

\[
z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d).
\]

- \(\mathcal V_d\subset h\mathbb Z^3\)：active sparse token support，可理解为 O-Voxel/SLAT 风格的稀疏坐标支撑。
- \(\mathbf F_d:\mathcal V_d\rightarrow\mathbb R^q\)：每个 sparse token 的 native latent feature，可包含 shape feature、material feature 和少量 grammar auxiliary code。
- \(\mathcal A_d\)：grammar-readable anchor/handle structure，包括 typed symbols、local frames、frontiers、ownership regions、attachment graph、material handles、cache/LOD descriptors。

一个 handle 写作

\[
h_i=(\sigma_i,T_i,\Omega_i,\alpha_i).
\]

\(\sigma_i\in\Sigma\) 是类型，\(T_i\in\mathcal T\) 是 local-to-world frame，\(\Omega_i\subseteq\mathcal V_d\) 是该 handle 管辖或指向的 sparse support，\(\alpha_i\) 保存 radius、age、priority、material tag、LOD level、cache id 等属性。

主文可把其他信息称为 executor bookkeeping：

\[
\mathcal B_d=
\{\text{masks, seeds, traces, caches, projection schedules, material/export metadata}\}.
\]

这样方法节读者只需记住：递归状态是一组 sparse latent tokens，加上语法可读写的 handles。

### 2.2 附录完整状态

为了证明覆盖性、稳定性和 cache/LOD 语义，附录可以使用完整执行状态：

\[
S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d,K_d).
\]

各项含义如下。

| 记号 | 含义 | 论文角色 |
|---|---|---|
| \(C_d\subset \{0\}\times h\mathbb Z^3\) | sparse coordinate support | native 3D latent substrate |
| \(F_d:C_d\to\mathbb R^{q_s}\times\mathbb R^{q_m}\times\mathbb R^{q_a}\) | shape/material/aux latent features | geometry 与 material 的统一载体 |
| \(U_d\) | typed symbols / handles / anchors | grammar 可改写对象 |
| \(A_d\) | occupancy, attractor, frontier, component, attachment, symmetry fields | competition 与 feasibility |
| \(B_d\) | masks, blend kernels, hard clamps, boundary state | masked editing 与 sampler clamp |
| \(M_d\) | material/PBR latent state, material intent, atlas/export metadata | textured GLB 与 material consistency |
| \(H_d\) | depth, random seeds, rule trace, transform trace, diagnostics | reproducibility 与 debugging |
| \(K_d\) | motif/latent/transform/LOD/window/sampler/material caches | repeated motif 与 infinite-zoom proxy |

其中

\[
U_d=\{u_i\}_{i=1}^{n_d},\qquad
u_i=(\sigma_i,\ell_i,T_i,\Omega_i,\alpha_i,\nu_i).
\]

为了严格覆盖 L-system，\(U_d\) 必须允许有序结构，而不只是无序集合：

\[
U_d\in\Sigma^\star
\quad\text{or}\quad
U_d=(V_d,E_d,\operatorname{ord}_d,\sigma,T,\alpha).
\]

这点很重要：无序 handle set 可以覆盖很多 graph grammar 与 asynchronous rewriting，但不能完全表达标准同步字符串 L-system 的顺序语义。

## 3. 语法对象

定义 PS-RSLG 为

\[
\mathcal G=
(\Sigma,\mathcal T,\mathcal R,\mathcal I,\mathcal S,
\Pi,\mathcal N_\theta^s,\mathcal N_\theta^m,
\mathcal D_\theta,\mathcal E_\theta,
\mathcal P,\mathcal C,\mathcal O,\mathcal L).
\]

每项含义如下。

- \(\Sigma\)：typed alphabet，包括 terminal、nonterminal、anchor、frontier、material、cache、LOD symbols。
- \(\mathcal T\)：transform group/semigroup，包括 translation、rotation、scale、anisotropic scale、mirror、portal embedding、lattice action、contractive map、LOD transform。称 semigroup 是因为 projection、cache bake、LOD collapse 通常不可逆。
- \(\mathcal R\)：stochastic context-sensitive rewrite rules。
- \(\mathcal I\)：interpretation map，把 symbol/frame/mask 解释为 sparse support、latent features、mesh regions 或 material regions。
- \(\mathcal S\)：scheduler，支持 synchronous rewriting、asynchronous priority queue、frontier sampling、group orbit expansion、cache materialization。
- \(\Pi\)：constraint and competition family，包括 occupancy exclusion、attachment、topology、symmetry、renderability、token budget。
- \(\mathcal N_\theta^s\)：冻结 shape latent masked flow/SDE/local sampler。
- \(\mathcal N_\theta^m\)：冻结 material/texture sampler 或 compatible texture export prior。
- \(\mathcal D_\theta\)：decoder/exporter，从 sparse latent state 到 mesh/material asset。
- \(\mathcal E_\theta\)：mesh-to-sparse re-encoder，把 projected asset 拉回可继续递归的 native state。
- \(\mathcal P\)：projection family，把 decoded candidate 投影到 admissible recursive asset set。
- \(\mathcal C\)：cache lookup/update semantics。
- \(\mathcal O\)：observable/export map，如 mesh、GLB、render、metric record。
- \(\mathcal L\)：rule selection、sample selection、projection optimization 的 score family；它不是训练 loss。

主文可以避免这个长 tuple，只写：

\[
\mathcal L_{\mathrm{PS\text{-}RSLG}}
=
(\text{typed handles},\text{rewrite rules},\text{realization operators}).
\]

完整 tuple 放补充材料或方法附录。

## 4. 规则模板与操作语义

### 4.1 规则格式

一条规则写成 handle-to-proposal template：

\[
\rho:\ h_i\mapsto
\{(\sigma_j,\tau_j,\Omega_j,m_j,\kappa_j,\pi_j,\eta_j)\}_{j=1}^{k}.
\]

含义：

- \(\sigma_j\)：输出或更新的 handle type；
- \(\tau_j\in\mathcal T\)：local transform；
- \(\Omega_j\)：target / ownership region；
- \(m_j:\mathcal V\rightarrow[0,1]\)：edit mask / blend mask；
- \(\kappa_j\)：feasibility predicate，如 attached、collision-free、reachable、budgeted、symmetry-closed；
- \(\pi_j\)：proposal kernel，如 grow、branch、copy、attach、split、extrude、refine、cache lookup、sampler proposal；
- \(\eta_j\)：random seed、sampler schedule、material condition 或 LOD policy。

更展开的附录规则可写成

\[
r:\;X(\omega,\Omega,\ell,a,h)
\Rightarrow
\{(X_j,T_j,\Omega_j,\rho_j,\mu_j,\beta_j,\psi_j,\zeta_j,\tau_j,\pi_j,\kappa_j)\}_{j=1}^m.
\]

这里 \(\rho_j\) 是 proposal kernel，\(\mu_j\) 是 mask，\(\beta_j\) 是 blend kernel，\(\psi_j\) 是 context predicate，\(\zeta_j\) 是 noise，\(\tau_j\) 是 sampler schedule，\(\pi_j\) 是 local constraint。

### 4.2 一层递归转移

给定当前状态 \(S_d\)，scheduler 选择规则集合

\[
R_d^\star=\mathcal S(S_d,\mathcal R,\mathcal B_d).
\]

每条规则生成候选 proposal：

\[
\widehat S_d=\operatorname{Prop}_{R_d^\star}(S_d).
\]

对 transform-copy 规则，候选 support 可写作

\[
\widehat C_j
=
Q_h\bigl(\tau_j(C_d\cap\Omega_j)\bigr),
\]

对应 feature transport 为

\[
\widehat F_j(Q_h(\tau_j c))
=
\mathcal T_j^F F_d(c).
\]

masked merge 采用 normalized blend：

\[
F^+(v)=
\frac{
w_0(v)F_d(v)+\sum_j w_j(v)\widehat F_j(v)}
{w_0(v)+\sum_j w_j(v)+\epsilon},
\qquad
w_j(v)=m_j(v)\beta_j(v).
\]

随后执行 competition、sampler naturalization、decode/project/re-encode 和 cache update：

\[
\begin{aligned}
S_d^{\mathrm{merge}} &= \operatorname{Merge}_{B_d}(S_d,\widehat S_d),\\
S_d^{\mathrm{comp}} &= \Theta_{\Pi_d}(S_d^{\mathrm{merge}}),\\
\bar S_d &= \mathcal N_{\theta,\Omega_d}^{\eta_d\rightarrow0}(S_d^{\mathrm{comp}};m_d,y),\\
x_{d+1}^{\mathrm{raw}} &= \mathcal D_\theta(\bar S_d),\\
x_{d+1}^{\star} &= \mathcal P_{\lambda_d}(x_{d+1}^{\mathrm{raw}},\mathcal A_d),\\
S_{d+1} &= \mathcal C_{d+1}\circ\mathcal E_\theta(x_{d+1}^{\star}).
\end{aligned}
\]

可以合并为中心公式：

\[
\boxed{
S_{d+1}
=
\mathcal C_{d+1}\circ\mathcal E_\theta\circ
\mathcal P_{\lambda_d}\circ\mathcal D_\theta\circ
\mathcal N_{\theta,\Omega_d}^{\eta_d\rightarrow0}\circ
\Theta_{\Pi_d}\circ
\operatorname{Merge}_{B_d}\circ
\operatorname{Prop}_{R_d^\star}(S_d).
}
\]

这条公式的论文意义是：projection 和 re-encode 位于每一层递归转移内部，不是最终 cleanup。

## 5. Sampler 的数学角色：masked local naturalization

冻结 3D 生成模型不能被写成“全局修复拓扑”的神秘算子。它的安全语义是 masked local naturalization。

若生成模型是 deterministic flow：

\[
\frac{dz_t}{dt}=v_\theta(z_t,t,y),
\]

或 SDE：

\[
dZ_t=f_\theta(Z_t,t,y)\,dt+g(t)dW_t,
\]

则在 PS-RSLG 中只允许它在 edit mask \(m_d\) 上更新，anchor region hard-clamped：

\[
z_{t-\Delta t}
=
(1-m_d)\odot z_{\mathrm{anchor}}
+m_d\odot\Phi_{\theta,t}(z_t,y).
\]

feature-level blend 可以写成

\[
f_i'=
(1-\alpha_i)f_i^{\mathrm{rule}}
+\alpha_i f_i^\theta,
\qquad i\in m_d.
\]

\(\alpha_i\) 由 depth、fragment risk、mask boundary distance、projection diagnostics 控制。论文应强调：

- sampler 只在 grammar 允许的局部区域提供 learned shape/material prior；
- sampler 输出必须通过 competition 和 projection 才能成为下一层 active state；
- sampler 的随机性可以提供形态多样性，但不承担拓扑保证；
- 若实验只在最终 geometry 后做 texture export，应诚实写作 compatible final export，而不是已证明的 per-depth material recursion。

Material 递归的理想语义是

\[
M_{d+1}
=
\operatorname{ProjectMaterial}_{\lambda_m}\circ
\operatorname{DecodeTexture}_\theta\circ
\mathcal N_{\theta,m}^{\tau_d^m\rightarrow0}\circ
\operatorname{MergeMaterial}_{\mu_d^m}(M_d,\widehat M_d).
\]

当前若只有最终 textured GLB route，则应写为

\[
M_D=\operatorname{TextureExport}_\theta(\mathcal E_\theta(x_D),Y^m),
\]

并把 per-depth material cache/recursion 放扩展或未来工作。

## 6. Projection、competition、cache、LOD 的数学角色

### 6.1 Admissible state set

定义可接受递归状态集合：

\[
\begin{aligned}
\mathcal S_{\mathrm{adm}}(\lambda)=
\{S:\;&
V_{\mathrm{conn}}(S)\le \epsilon_c,\;
V_{\mathrm{frontier}}(S)=0,\;
V_{\mathrm{occ}}(S)\le \epsilon_o,\;
V_{\mathrm{attach}}(S)\le \epsilon_a,\\
&
V_{\mathrm{sym}}(S)\le \epsilon_g,\;
V_{\mathrm{mat}}(S)\le \epsilon_m,\;
V_{\mathrm{render}}(\mathcal O(S))\le \epsilon_r,\;
|C(S)|\le T_{\max}
\}.
\end{aligned}
\]

其中 connectedness 不只看 mesh face components。更合适的主指标是 voxelized occupancy 6-neighborhood connectedness。给定 sparse support \(C\)，定义邻接图

\[
G_\eta(C)=(C,E_\eta),
\qquad
(p,q)\in E_\eta\Longleftrightarrow \|p-q\|_1\le \eta h.
\]

令 \(C_{\mathrm{att}}(S)\) 是可从 root support 到达的 attached support：

\[
V_{\mathrm{conn}}(S)
=
1-\frac{\operatorname{mass}(C_{\mathrm{att}}(S))}
{\operatorname{mass}(C(S))+\epsilon}.
\]

关键约束是

\[
V_{\mathrm{frontier}}(S)=0,
\]

即每个 active frontier/growth handle 必须有 root-attached path。一个 floating chunk 如果进入下一层 scheduler 或 cache，会污染递归程序；它不是最终视觉瑕疵，而是状态错误。

Projection 是映射

\[
\mathcal P_\lambda:\mathcal S_{\mathrm{raw}}\rightarrow\mathcal S_{\mathrm{adm}}(\lambda).
\]

当前实现中的 largest component pruning、attachment-aware selection、bridge candidate、decode/project/re-encode 都是该理想 projection 的可运行近似。

### 6.2 Competition

对候选 action \(a\) 和 sparse token \(v\)，定义竞争分数

\[
\begin{aligned}
\psi(a,v;S_d)=
{}&\lambda_{\mathrm{att}}\phi_{\mathrm{att}}(a,v)
-\lambda_{\mathrm{occ}}\phi_{\mathrm{occ}}(a,v)
-\lambda_{\mathrm{col}}\phi_{\mathrm{collision}}(a,v)\\
&+\lambda_{\mathrm{front}}\phi_{\mathrm{frontier}}(a,v)
+\lambda_{\mathrm{grp}}\phi_{\mathrm{orbit}}(a,v)
+\lambda_{\mathrm{mat}}\phi_{\mathrm{mat}}(a,v)
+\epsilon_\theta(a,v,\xi).
\end{aligned}
\]

其中 attachment、occupancy、collision、frontier、group orbit、material seam 是 grammar/geometry terms；\(\epsilon_\theta\) 是 frozen sampler 或 sample selection 的弱随机偏好。competition 的角色是把多个局部 proposal 变成互斥、可附着、预算内、可投影的 sparse state。

选择可写为 softmax 或 hard argmax：

\[
P(a\mid v,S_d)=
\frac{\exp \psi(a,v;S_d)}
\sum_{a'}\exp \psi(a',v;S_d)}.
\]

实践中可用 deterministic pruning/selection，但主文数学上把它写成 competition family 更强，因为它统一了 space competition、DLA frontier attachment、symmetry orbit closure 和 material seam control。

### 6.3 Bridge-aware projection

Prune-only projection 是

\[
\mathcal P_{\mathrm{prune}}(X)
=
\operatorname*{arg\,min}_{Y\subseteq X,\;Y\in\mathcal S_{\mathrm{adm}}}
d_{\mathcal S}(X,Y)+\lambda_{\mathrm{del}}\operatorname{mass}(X\setminus Y).
\]

它能删除碎片，但会损失 DLA、crystal、radial、portal 等结构中本应通过细颈、接触面或 symmetry orbit 连接的部分。更好的表述是 bridge-aware projection：

\[
Y=(X\setminus R)\cup B,
\]

其中 \(R\) 是要删除的 orphan/noisy support，\(B=\bigcup_\ell \gamma_\ell\) 是小预算连接路径。候选路径

\[
\Gamma(Q,R_d)=
\{\gamma=(q_0,\ldots,q_T):
q_0\in Q,\ q_T\in C_{\mathrm{att}},\
q_{t+1}-q_t\in\mathcal N_\eta\}.
\]

Projection optimization:

\[
\begin{aligned}
\mathcal P_{\mathrm{bridge}}(X)
=
\operatorname*{arg\,min}_{Y\in\mathcal S_{\mathrm{adm}}}
&\ d_{\mathcal S}(X,Y)
+\eta_{\mathrm{obs}}d_{\mathrm{obs}}(\mathcal O(X),\mathcal O(Y))
+\eta_m d_{\mathrm{mat}}(M_X,M_Y)\\
&+\lambda_{\mathrm{del}}\operatorname{mass}(R)
+\lambda_{\mathrm{br}}\sum_{\gamma\subset B}\operatorname{len}(\gamma)
+\lambda_{\kappa}\sum_{\gamma\subset B}\operatorname{curv}(\gamma)
+\lambda_{\mathrm{sym}}V_{\mathrm{sym}}(Y).
\end{aligned}
\]

当前 DLA bridge QA 说明 post-hoc bridge 容易产生 fake bridge 和 over-closing，因此主文不能把 bridge 后处理作为正例。它更适合支撑这样的设计选择：连通性必须在 grammar proposal/competition/projection inside recursion 中维护，而不是最后用长桥线缝合。

### 6.4 Cache

Cache entry 可定义为

\[
k=(\operatorname{id},\sigma,T,\Omega,C_\Omega,F_\Omega,M_\Omega,
\ell,\eta,\operatorname{validity},\operatorname{cost}).
\]

Cache lookup 是 proposal kernel 的一种：

\[
(\widehat C,\widehat F,\widehat M)
=
\operatorname{Lookup}(K_d,\operatorname{id})\circ T.
\]

Cache update 是递归转移的一部分：

\[
K_{d+1}
=
\operatorname{UpdateCache}(K_d,S_{d+1},R_d^\star,\operatorname{diag}_{d+1}).
\]

Cache 的数学角色有四个。

1. Motif cache：保证 repeated motifs 不是每次重新采样导致漂移，而是复用经过 projection 验证的局部状态。
2. Latent cache：复用 \((C,F,M)\) block，降低 decode/re-encode 噪声。
3. Sampler/noise cache：对称或重复区域共享 noise seed 或 sampler schedule，减少 material/geometry inconsistency。
4. Window cache：在 infinite zoom 或 sliding-window recursion 中只 materialize visible window，其余保留 symbolic descriptor。

### 6.5 LOD

LOD 是 token budget 下的递归语义，不只是渲染优化。令 logical depth \(d\) 的 visible token budget 为 \(T_{\max}(d)\)，LOD scheduler 决定一个 handle 是否 materialize：

\[
\operatorname{mat}(h_i,d)=
\mathbf 1\{
\operatorname{screen\_size}(h_i)>\tau_{\mathrm{pix}}
\;\wedge\;
\operatorname{cost}(h_i)\le B_d
\}.
\]

未 materialize 的 handle 保留为 descriptor：

\[
h_i^{\mathrm{desc}}=(\sigma_i,T_i,\operatorname{bbox}_i,\ell_i,\operatorname{cache\_id}_i).
\]

因此无界逻辑递归可以定义成有限内存流：

\[
S_d^{\mathrm{view}}
=
\operatorname{Materialize}_{W_d,B_d}(K_d,\mathcal A_d),
\qquad
|C(S_d^{\mathrm{view}})|\le T_{\max}.
\]

主文最多称为 extension / proxy：bounded visible-window recursion 或 cache/LOD stream。不要写成已经输出无限 mesh。

## 7. 经典系统的表达能力与 proof sketch

本节只证明可表达性或退化实例，不证明视觉质量优于传统方法。

### 7.1 IFS

经典 IFS 由一组 contraction maps \(\{\tau_i\}_{i=1}^m\) 构成，Hutchinson operator 为

\[
H(A)=\bigcup_{i=1}^m \tau_i(A).
\]

在 PS-RSLG 中取一个 `Motif` handle，规则为

\[
\rho_{\mathrm{IFS}}:h\mapsto
\{(\sigma,\tau_i,\Omega,m_i,\top,\operatorname{copy},\eta_0)\}_{i=1}^m.
\]

禁用 sampler：\(\mathcal N_\theta=\operatorname{Id}\)，禁用 projection 或令 projection 为 identity，feature transport 只做 copy。则 support recurrence 为

\[
C_{d+1}=Q_h\left(\bigcup_i\tau_i(C_d)\right).
\]

当 \(h\rightarrow0\) 且 \(\tau_i\) 为 contraction 时，该迭代收敛到 IFS attractor 的量化近似。Proof sketch：PS-RSLG 的 proposal/merge 退化为 Hutchinson union；contractive IFS 的 Banach fixed point theorem 给出唯一 compact attractor；量化误差由 \(Q_h\) 控制。

### 7.2 L-system

标准 deterministic L-system 是字符串重写

\[
w_{d+1}=\prod_{X\in w_d} P(X),
\]

再由 turtle interpretation 将符号解释为曲线/branch geometry。

在 PS-RSLG 中令 \(U_d\in\Sigma^\star\)，scheduler 采用同步 parallel rewrite，规则只改写 symbol sequence：

\[
\rho_X:X(\ell,a)\mapsto X_1X_2\ldots X_k.
\]

解释函数 \(\mathcal I_{\mathrm{turtle}}\) 把有序符号、frame stack、branch radius 映射到 sparse support 和 handles：

\[
(U_d,T_{\mathrm{turtle}})\xrightarrow{\mathcal I} (C_d,F_d,\mathcal A_d).
\]

禁用 sampler 和复杂 projection，或只把 projection 作为 tube connectivity cleanup。则 PS-RSLG 完全包含 L-system 的同步字符串重写和 turtle interpretation。Proof sketch：有序 \(U_d\) 保留字符串顺序；scheduler 同步应用所有 productions；interpretation map 等价于 turtle evaluator。

### 7.3 Space colonization

Runions-style space colonization 用 attractor points \(A\)、tips \(T\)、kill radius 与 influence radius 更新树枝方向。每个 tip 接收邻近 attractors 的平均方向：

\[
\Delta t
\propto
\sum_{a\in A(t)}
\frac{a-t}{\|a-t\|}.
\]

在 PS-RSLG 中设置：

- `Tip` handle 为 active frontier；
- \(\Gamma_d\) 为 attractor/density field；
- competition term 包含 attractor coverage、occupancy exclusion 和 collision；
- grow rule 从 tip 生成新 token 和 child tip。

规则为

\[
\rho_{\mathrm{SC}}:\operatorname{Tip}(t,r)
\mapsto
\operatorname{Tip}(t+\delta \hat v,r')
\quad
\hat v=
\operatorname{norm}\sum_{a\in\mathcal A(t)}
\frac{a-t}{\|a-t\|}.
\]

当 sampler identity、projection 只执行 occupancy pruning、scheduler 按 tip 并行更新时，PS-RSLG 退化为空间殖民算法。Proof sketch：attractor assignment 由 \(\Gamma_d\) 和 nearest-tip policy 实现；occupancy exclusion 实现 kill radius；grow rule 实现 tip advance。

### 7.4 DLA / frontier growth

DLA 可视为随机游走粒子击中已有 cluster frontier 后附着。PS-RSLG 中定义 `Frontier` handle 和 hitting proposal kernel：

\[
q\sim p_{\mathrm{hit}}(\cdot\mid C_d),
\qquad
\rho_{\mathrm{DLA}}:\operatorname{Frontier}\mapsto
\operatorname{Attach}(q).
\]

可行性条件要求

\[
\operatorname{dist}(q,C_{\mathrm{att}})\le r_{\mathrm{attach}},
\qquad
q\notin O_d,
\]

并用 competition/projection 删除或拒绝 orphan hits。若 \(p_{\mathrm{hit}}\) 取随机游走首次命中分布、sampler identity、projection 只保留 attached cluster，则 PS-RSLG 近似 DLA/frontier accretion。Proof sketch：frontier proposal 的采样分布等价于 hitting distribution；attachment predicate 实现 accretion；occupancy exclusion 防止重复占据。

当前实验口径必须谨慎：可以说 DLA/frontier 是表达能力覆盖和 stress test；不能说已解决真实 DLA asset generation。现有 DLA bridge ablation 更支持“post-hoc bridge 不足，需 grammar-native connected frontier”。

### 7.5 Shape grammar / CGA

有限 shape grammar 可写成在局部 frame 上的 split/extrude/replace：

\[
X(\Omega,T,a)\Rightarrow
\{X_j(\Omega_j,T_j,a_j)\}_{j=1}^k.
\]

PS-RSLG 中把 face、tile、portal、room、arch、ornament 等作为 typed handles；\(\tau_j\) 给出局部 frame decomposition；\(\mathcal I\) 把 split/extrude 解释为 support mask 或 mesh patch。禁用 learned sampler 时得到传统 shape grammar；启用 masked sampler 时可对 terminal patch 做 local naturalization。Proof sketch：每个有限 split/extrude/replace action 都可编码为 handle rule；ownership masks 保留局部 frame；scheduler 控制 derivation order。

需要限定：本文覆盖 finite local shape grammar 或 CGA-style split grammar 的核心操作，不宣称覆盖所有带全局约束、优化或语义推理的 shape grammar 系统。

### 7.6 Symmetry / crystal

设群或有限群 \(G\) 作用在空间与状态上：

\[
g\cdot S=(gC,gF,gU,gA).
\]

若规则集对 \(G\) 闭合：

\[
\rho\in\mathcal R
\Rightarrow
g\rho g^{-1}\in\mathcal R,\quad \forall g\in G,
\]

且 projection 与群作用近似交换：

\[
d_{\mathcal S}(\mathcal P(gS),g\mathcal P(S))\le\epsilon_g,
\]

则递归转移满足近似等变：

\[
d_{\mathcal S}(\mathbb T(gS),g\mathbb T(S))\le
L\epsilon_g+\epsilon_{\mathrm{num}}+\epsilon_{\theta}.
\]

如果初始状态 \(S_0\) 对 \(G\) 不变，且 rule scheduler 采用 group orbit expansion 或 shared seed，则每层输出在 projection tolerance 内保持 \(G\)-invariant。Proof sketch：对 \(d\) 做归纳；规则闭合保证 proposals 成 orbit；competition 和 projection 近似交换保证选择与修正不破坏 orbit；sampler 若使用共享 seed/hard mask 则只引入有界误差。

当前应写作 symmetry/crystal scaffold 或 lattice/orbit grammar。不要写物理晶体生长已解决；bismuth/pyrite 目前更适合作为 non-tree connected scaffold 和 symmetry/contact stress case。

## 8. Projection stability 与 finite-memory recursion proof sketch

### 8.1 Per-depth projection 稳定性

令 \(e_d=V_{\mathrm{conn}}(S_d)\)。假设 raw proposal 每层引入 spurious fragment mass 不超过 \(\alpha_d\)，projection 至少移除或桥接比例 \(\rho\) 的 fragment，并且 decode/re-encode round trip 引入误差 \(\beta_d\)。则

\[
e_{d+1}\le (1-\rho)e_d+\alpha_d+\beta_d.
\]

若 \(\rho>0\)、\(\alpha_d+\beta_d\le \bar\alpha\)，则

\[
e_d\le (1-\rho)^d e_0+
\frac{\bar\alpha}{\rho}.
\]

这说明 per-depth projection 能把 fragment error 控制在有界范围；final-only cleanup 没有这个递推约束，因为中间 orphan frontier 已经参与后续 rule、sampler 和 cache update。

该 proof sketch 的条件必须明确：projection threshold、bridge budget、codec round-trip error 和 per-rule fragment rate 都需有界。这不是无条件拓扑定理，而是解释为什么 projection inside recursion 比 final-only cleanup 更合理。

### 8.2 Infinite recursion / LOD stream

无界递归有三种安全语义。

**Contractive limit.** 若所有 transform 的 Lipschitz 常数 \(s_i<1\)，且 state metric 是 Hausdorff/occupancy metric，则 support recurrence 定义 compact limit set。这覆盖 IFS 类别。

**Visible-window stream.** 给定相机窗口 \(W_t\) 和 token budget \(T_{\max}\)，每步只 materialize 与窗口相交且 screen size 足够的 descriptors：

\[
S_t^{W}
=
\operatorname{Materialize}_{W_t,T_{\max}}(K_t,\mathcal A_t).
\]

只要 materialization policy 保证

\[
|C(S_t^W)|\le T_{\max},
\]

逻辑深度可无界，但任意时刻实际状态有限。

**Cache/LOD descriptor semantics.** 远处或小尺度递归不展开为 mesh，而保存为 descriptor：

\[
h^{\mathrm{desc}}=(\sigma,T,\operatorname{bbox},\ell,\operatorname{cache\_id},\operatorname{error\_bound}).
\]

当 descriptor 被观察或编辑时再展开。当前实验可把这作为扩展路线；除非补齐 sliding-window/cache diagnostic 和 visual QA，不应作为主文强 claim。

## 9. SIGGRAPH Asia 方法章节建议组织

建议方法章节采用“主文紧凑、附录严谨”的结构。

### 9.1 Section 3: Problem and State

目标：明确本文不是 one-shot 3D generation，也不是 traditional procedural modeling，而是 finite-depth recursive asset generation in a frozen native 3D generator。

内容：

1. 输入输出：\(x_0,y,\theta,\mathcal G,D\rightarrow x_D\)。
2. 最小状态：\(z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d)\)。
3. Handle definition：\(h_i=(\sigma_i,T_i,\Omega_i,\alpha_i)\)。
4. Admissible-state invariant：connected support、active frontier attached、renderable、within token budget。

主文避免大元组；完整 \(S_d=(C,F,U,A,B,M,H,K)\) 放 appendix。

### 9.2 Section 4: Projection-Stabilized Recursive Grammar

目标：给出规则模板和一层递归操作语义。

内容：

1. Rule template：\(\rho:h_i\mapsto\{(\sigma,\tau,\Omega,m,\kappa,\pi,\eta)\}\)。
2. Proposal/merge/competition。
3. Masked local naturalization：sampler 只在 grammar mask 内工作。
4. Decode/project/re-encode：projection inside recursion。
5. Algorithm box：`Select rules -> Propose -> Merge -> Compete -> Masked sample -> Decode -> Project -> Re-encode -> Update cache`。

### 9.3 Section 5: Expressive Coverage

目标：简短证明 PS-RSLG 覆盖经典递归/procedural families。

主文只放一张表和 1-2 段文字：

| Classical system | PS-RSLG restriction |
|---|---|
| IFS | contractive transform-copy rules, identity sampler/projection |
| L-system | ordered symbols + synchronous rewriting + turtle interpretation |
| Space colonization | attractor-conditioned tip rules + occupancy exclusion |
| DLA/frontier | stochastic hitting/frontier attachment + attached projection |
| Shape grammar | typed frame split/extrude/replace rules |
| Symmetry/crystal | group-orbit rule closure + commuting projection |

详细 proof sketches 放 appendix。

### 9.4 Section 6: Stabilization, Cache, and Material

目标：解释为什么 projection/competition/cache/LOD 是方法，而不是实现细节。

内容：

1. Projection stability bound：\(e_{d+1}\le(1-\rho)e_d+\alpha_d+\beta_d\)。
2. Competition score：attachment、occupancy、frontier、symmetry、material terms。
3. Cache semantics：motif/latent/transform/LOD/window/material cache。
4. Material/PBR：当前 geometry recursion + compatible texture export；per-depth material recursion 是 extension，除非实验已补齐。

### 9.5 Experiments section 的 claim alignment

实验叙事应分成四类，而不是把所有结果混成“成功”。

1. **Projection ablation**：direct / final-only / per-depth projection。  
   主 claim：projection inside recursion 抑制 component explosion 和 orphan frontier 传播。

2. **Matched structural baseline matrix**：L-system、space colonization、proposed connected scaffold。  
   主 claim：传统 structural baselines 在公平 tube-occupancy 协议下也很强；该矩阵是 fairness sanity check，不是 proposed connectivity superiority 证明。

3. **Method-behavior visualizations**：same condition depth strips / parameter controls。  
   主 claim：展示递归深度、density、competition 或 projection schedule 如何改变结构；不称为 causal ablation，除非 isolate 了单一变量。

4. **Texture/PBR and visual asset export**：textured GLB 或 programmatic PBR。  
   主 claim：递归 geometry 可以被导出为 textured assets；但 mesh face fragmentation 与 material seams 需单独诊断。

## 10. 当前实验支持程度与 claim 分流

### 10.1 可以作为主文正面 claim

**Claim A: PS-RSLG 的形式化可表达性。**  
IFS、L-system、space colonization、DLA/frontier、shape grammar、symmetry/crystal 都可作为限制实例或自然嵌入。注意这是 expressiveness claim，不是性能或视觉质量 claim。

**Claim B: Per-depth projection 是递归语义核心。**  
现有 projection ablation 与 connectivity-first notes 支持：把 projection 放在每层 transition 内，比 final-only cleanup 更符合递归状态不变量；碎片如果进入下一层会污染 frontier/cache/sampler。

**Claim C: Occupancy 6-neighborhood connected support 是当前最稳的结构证据。**  
vine/root/tree、bismuth-like、pyrite-like、volumetric coral scaffold 等当前正面证据主要是 voxelized occupancy support connectedness，而不是 raw face topology。

**Claim D: Procedural baselines 是强 structural controls。**  
matched structural matrix 可说明 L-system 和 space colonization 在 tube occupancy 协议下也能保持 root-attached connectivity。论文可以把它写成公平性检查，避免 strawman baseline。

**Claim E: Textured GLB/PBR export 是兼容性证据。**  
可以说 recursive geometry can be exported or rendered with material/PBR routes under selected cases；不能说所有 textured meshes 都 topology clean。

### 10.2 只能作为附录、诊断或负面结果

**DLA bridge post-processing.**  
现有 DLA bridge QA 中 face-level 指标有时变好，但 occupancy component 仍多，视觉上出现 fake bridge / over-closing。它应作为负面诊断：post-hoc bridge 不足以替代 grammar-native connected frontier。

**Raw mesh face connectivity。**  
textured GLB face components 很多，mesh islands 和 material/UV splitting 会干扰 face component metric。主文应把 face metrics 作为 diagnostic，不作为唯一连通性证据。

**Pyrite/crystal mesh topology。**  
pyrite-like scaffold 的 occupancy connectedness 可写；mesh components 随 depth 增长必须交代，不能写 clean crystal topology。

**Space colonization vs grammar depth 公平性。**  
space colonization 的 depth 更像 iteration budget，不完全等同 grammar derivation depth。放 protocol caveat。

### 10.3 只能作为 future work / extension

**严格无限递归。**  
当前只能给 contractive/visible-window/cache descriptor semantics；不要宣称输出无界 mesh。

**严格群等变或物理晶体生长。**  
需要 shared-seed sampler、group-commuting projection、symmetry/contact metrics 和 visual QA。当前只能写 orbit grammar / crystal-like scaffold。

**Per-depth material recursion。**  
若现有流程主要是最终 texturing/export，则 per-depth material cache、BRDF seam projection、symmetry material tying 都应写为 extension。

**Sampler/SDE 保证拓扑保持。**  
当前 sampler 应作为 masked local naturalizer，不承担 topology guarantee。任何“sampler improves topology”的 claim 都需要单独 ablation。

## 11. 建议写进论文的贡献表述

可用贡献句：

1. We formulate recursive 3D asset generation as typed rewriting over sparse native 3D generator states, rather than as procedural geometry followed by one-shot generative cleanup.
2. We introduce projection-stabilized recursive transitions that combine grammar proposals, occupancy competition, masked local generative naturalization, decode/project/re-encode, and cache updates.
3. We show that classical recursive/procedural families, including IFS, L-systems, space colonization, frontier/DLA-like accretion, finite shape grammars, and symmetry transform-copy systems, arise as restricted instances of the same grammar.
4. We evaluate connected support as a per-depth invariant using voxelized occupancy connectivity, while reporting mesh/face diagnostics separately to expose export fragmentation.

不建议写的贡献句：

- We solve recursive 3D generation in general.
- We guarantee topology preservation of frozen 3D generative samplers.
- We outperform L-system and space colonization on connectivity under all fair settings.
- We generate physically valid DLA/crystal structures.
- We support infinite recursive 3D meshes.

## 12. 推荐图表与附录材料

### 12.1 主文图

**Fig. Method overview.**  
左：typed handles on sparse latent support。中：rule proposal + competition + masked sampler。右：decode/project/re-encode + cache/LOD update。图中必须标出 projection inside recursion。

**Fig. Rule family taxonomy.**  
一行六列：IFS、L-system、space colonization、DLA/frontier、shape grammar、symmetry/crystal；每列写 PS-RSLG restriction。

**Fig. Projection ablation.**  
direct recursion vs final-only cleanup vs per-depth projection。配 connected components、largest component ratio、root reachability、orphan frontier。

**Fig. Method behavior / depth controls.**  
same root / same camera / same material / depth strip。只用 mesh 或 textured mesh render，不用 point-cloud/matplotlib 作为证据图。

### 12.2 主文表

**Table: Expressive coverage.**  
列：classical system、required state fields、rule restriction、sampler role、projection role、claim type。

**Table: Claim-aligned metrics.**  
列：case family、positive evidence、caveat、paper-safe claim、not supported。

### 12.3 附录

- 完整 \(S_d=(C,F,U,A,B,M,H,K)\) state definition。
- Proof sketches for six classical systems。
- Projection stability bound。
- Matched structural baseline matrix protocol and caveats。
- DLA bridge negative QA。
- Cache/LOD finite-memory semantics。

## 13. 可直接进入方法节的短版段落

下面是一段可压缩后进入英文主文的中文底稿。

我们将递归 3D 资产生成定义为冻结原生 3D 生成模型状态空间上的类型化重写过程。深度 \(d\) 的状态 \(z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d)\) 包含 active sparse token support、token-wise latent features，以及语法可读写的 typed handles。每条规则从一个 handle 发射局部 proposal，包括输出类型、局部变换、目标 mask、可行性谓词、proposal kernel 和 sampler schedule。一次递归转移不是简单复制几何，而是执行 proposal、masked merge、occupancy/attachment competition、masked frozen-sampler naturalization、decode/project/re-encode 和 cache update。Projection 被放入每层递归转移，使 root-attached connected support、active frontier validity、token budget 和 renderability 成为可继续递归的状态不变量。经典 IFS、L-system、space colonization、DLA/frontier、shape grammar 和 symmetry transform-copy 都可由禁用或限制 sampler/projection/scheduler 得到；学习型生成模型的角色则是 grammar mask 下的局部自然化和材质/外观先验，而不是全局拓扑修复器。

## 14. 当前 worker 结论

本支线建议主文把方法名和核心变量统一到 **PS-RSLG**。主文公式保持短：\(z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d)\)、rule template、中心 transition、projection invariant。大状态、proof sketches、cache/LOD、material recursion 放附录或 supplement。

论文最稳的理论贡献是统一操作语义和 classical-system coverage；最稳的实验贡献是 per-depth connected support / projection stabilization，而不是 mesh-face topology 或 DLA/crystal 成功。DLA、crystal、infinite recursion、per-depth material recursion 应分别放 stress test、extension 或 future work，除非后续补齐对应的 matched metrics 和 zoom QA。
