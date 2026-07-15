# Formal Recursive Generative Grammar v2: 用于递归 3D 生成增长的统一操作语义

创建时间：2026-05-08  
写作范围：强化 `recursive_3d_generative_growth` 的 formal grammar / system 框架。本文只写理论文档，不修改代码、实验结果或论文主文。  
目标论文口径：SIGGRAPH Asia 方法节和补充材料可引用的形式化框架。  
建议名称：**PS-RSLG: Projection-Stabilized Sparse-Latent Recursive Grammar**。

## 0. 核心观点

本文把递归 3D asset growth 定义为一个在 **typed sparse 3D latent state** 上运行的随机上下文相关生成语法，而不是若干工程模块的串联。该语法同时包含：

1. 传统程序建模的结构规则：IFS、L-system、space colonization、DLA/frontier accretion、finite local shape grammar、symmetry/crystal transform-copy。
2. 冻结 Trellis2 / O-Voxel / SLAT 生成器提供的 learned 3D latent prior：flow/SDE sampling、masked naturalization、mesh decode、mesh re-encode、texture/PBR export。
3. 递归稳定机制：competition、attachment constraints、projection、decode/project/re-encode、cache/LOD 都是 rule semantics 的组成部分，而不是最终后处理。
4. 有界无限递归语义：当前系统输出有限深度资产；无界逻辑递归只能通过 contractive limit、visible-window streaming 或 LOD/cache descriptor 表述。

最强但诚实的论文 claim 应写成：

> PS-RSLG is a unified operational semantics for finite-depth recursive 3D asset generation in a frozen sparse native-3D generator. Classical procedural systems are recovered as degenerate grammar instances; learned sampling enters as masked local naturalization; per-depth projection makes the recursive map state-stabilizing under explicit fragment-suppression assumptions.

## 1. 状态空间

设 ambient domain 为连续空间 \(X\subset \mathbb{R}^3\)、离散 sparse grid \(L_h=h\mathbb{Z}^3\)，以及 batch-augmented sparse coordinate domain

\[
\bar L_h=\{0\}\times L_h.
\]

深度 \(d\) 的递归状态定义为

\[
S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d,K_d).
\]

### 1.1 Sparse latent support

\[
C_d\subset \bar L_h,\qquad |C_d|\leq T_{\max}(d).
\]

\(C_d\) 是 Trellis2/O-Voxel/SLAT 的 active sparse support。它不是单纯 voxel occupancy，而是 grammar 可读写的 latent coordinate substrate。为覆盖连续 IFS 或 mesh-level shape grammar，可使用解释函数把连续区域 \(\Omega\subset X\) 量化到 \(Q_h(\Omega)\subset L_h\)，并把所有连续 claim 限制为 \(h\rightarrow0\) 或固定分辨率近似。

### 1.2 Latent features

\[
F_d:C_d\rightarrow \mathbb{R}^{q_s}\times\mathbb{R}^{q_m}\times\mathbb{R}^{q_a}.
\]

其中 \(q_s\) 是 shape SLAT feature，\(q_m\) 是 material/texture/PBR latent feature，\(q_a\) 是 auxiliary grammar feature，如 age、branch radius、semantic tag、local frame code、confidence。若当前实验只使用 shape-SLAT，可令 \(q_m=0\)，但 formalism 保留 material/PBR 维度。

### 1.3 Typed symbols and anchors

\[
U_d=\{u_i\}_{i=1}^{n_d},\qquad
u_i=(\sigma_i,\ell_i,T_i,\Omega_i,\alpha_i,\nu_i).
\]

- \(\sigma_i\in\Sigma\)：typed symbol，例如 `Root`、`Tip`、`Branch`、`AttractorCell`、`Frontier`、`Patch`、`Portal`、`Tile`、`CrystalFace`、`SymOrbit`、`LODChunk`。
- \(\ell_i\)：logical recursion level 或 LOD level。
- \(T_i\in\mathcal{T}\)：local-to-global transform。
- \(\Omega_i\subseteq C_d\)：该 symbol 管辖的 sparse support 或 decoded mesh region。
- \(\alpha_i\)：属性，如 radius、growth probability、material tag、branch order、tile id。
- \(\nu_i\)：scheduler metadata，如 priority、age、parent id、cache id。

若要覆盖 L-system，\(U_d\) 必须允许有序序列或有序图，而不能只当成无序集合：

\[
U_d\in \Sigma^\star
\quad\text{or}\quad
U_d=(V_d,E_d,\mathrm{ord}_d,\sigma,T,\alpha).
\]

### 1.4 Auxiliary fields

\[
A_d=(O_d,\Gamma_d,\mathcal{F}_d,\mathcal{K}_d,\mathcal{E}_d,\mathcal{Q}_d,\mathcal{G}_d).
\]

- \(O_d:L_h\rightarrow\{0,1\}\)：occupancy/exclusion。
- \(\Gamma_d:L_h\rightarrow\mathbb{R}_{\ge0}\)：attractor、density 或 target field。
- \(\mathcal{F}_d\subset L_h\)：frontier/tip candidate set。
- \(\mathcal{K}_d\)：component graph、attachment graph、adjacency graph。
- \(\mathcal{E}_d\)：collision、self-intersection、forbidden region。
- \(\mathcal{Q}_d\)：quality estimates，如 attachment score、renderability、fragment risk、symmetry error。
- \(\mathcal{G}_d\)：group/lattice metadata，用于 symmetry、crystal 和 periodic rules。

### 1.5 Masks, material, history, caches

\[
B_d=(\partial C_d,\{\mu_k\},\{\omega_k\},\{\chi_k\}).
\]

\(\mu_k:L_h\rightarrow[0,1]\) 是 edit mask，\(\omega_k\) 是 blend kernel，\(\chi_k\) 是 boundary condition 或 hard clamp indicator。

\[
M_d=(m_d,p_d,\tau_d,y_d,\chi_d).
\]

\(m_d\) 是 material latent，\(p_d\) 是 PBR intent，\(\tau_d\) 是 naturalization/noise schedule，\(y_d\) 是 text/image/mesh/material condition，\(\chi_d\) 是 category/style condition。

\[
H_d=(d,\xi_d,\mathcal{R}_{0:d},\mathcal{T}_{0:d},\lambda_d,\mathrm{diag}_d).
\]

记录深度、随机种子、rule trace、transform trace、projection 参数和 diagnostics。

\[
K_d=(K_d^{\mathrm{motif}},K_d^{\mathrm{latent}},K_d^{\mathrm{transform}},
K_d^{\mathrm{LOD}},K_d^{\mathrm{window}},K_d^{\mathrm{sampler}}).
\]

cache 不是实现细节，而是递归语义的一部分，因为它决定 repeated motif、infinite zoom、sliding-window recursion 是否可在有限 token budget 下执行。

## 2. 语法对象

定义 PS-RSLG 为

\[
\mathcal{G}=
(\Sigma,\mathcal{T},\mathcal{R},\mathcal{I},\mathcal{S},
\Pi,\mathcal{N}_\theta,\mathcal{D}_\theta,\mathcal{E}_\theta,
\mathcal{P},\mathcal{C},\mathcal{O},\mathcal{L}).
\]

各项含义如下。

- \(\Sigma\)：typed alphabet，包括 terminal、nonterminal、anchor、frontier、material、cache、LOD symbols。
- \(\mathcal{T}\)：transform group/semigroup。包括 rigid transform、scale、anisotropic scale、mirror、portal embedding、octree/LOD transform、lattice translation、contractive map。称 semigroup 是因为 projection、scale-down、LOD collapse、cache bake 不可逆。
- \(\mathcal{R}\)：stochastic context-sensitive rewrite rules。
- \(\mathcal{I}\)：interpretation map，把 symbols/frames/masks 解释为 sparse support、latent features、decoded mesh patches 或 material regions。
- \(\mathcal{S}\)：scheduler，决定同步、异步、priority queue、frontier sampling 或 group-orbit expansion。
- \(\Pi\)：constraints，包括 occupancy、attachment、topology、competition、symmetry、lattice、renderability、token budget。
- \(\mathcal{N}_\theta\)：冻结 Trellis2 flow/SDE sampler 或 local naturalization kernel。
- \(\mathcal{D}_\theta\)：frozen decoder，从 sparse latent state 到 mesh/material asset。
- \(\mathcal{E}_\theta\)：mesh-to-O-Voxel/SLAT re-encoder。
- \(\mathcal{P}\)：projection family，把 decoded candidate 投影到 admissible recursive asset set。
- \(\mathcal{C}\)：cache update and lookup semantics。
- \(\mathcal{O}\)：observable/export map，如 mesh、GLB、render、metric record。
- \(\mathcal{L}\)：loss/score family，仅用于 rule choice、projection 和 sample selection；不是训练 loss。

## 3. Admissible state set

定义可接受递归资产状态集合：

\[
\mathcal{S}_{\mathrm{adm}}(\lambda)=
\left\{
S:
\begin{array}{l}
V_{\mathrm{frag}}(S)\leq \epsilon_f,\quad
V_{\mathrm{attach}}(S)\leq \epsilon_a,\quad
V_{\mathrm{occ}}(S)\leq \epsilon_o,\\
V_{\mathrm{sym}}(S;G)\leq \epsilon_g,\quad
V_{\mathrm{render}}(D_\theta(S))\leq \epsilon_r,\quad
|C(S)|\leq T_{\max}
\end{array}
\right\}.
\]

这些 violation 可具体化为：

\[
V_{\mathrm{frag}}=1-\frac{\mathrm{mass}(C_{\mathrm{largest\ attached}})}
{\mathrm{mass}(C)+\epsilon},
\]

\[
V_{\mathrm{attach}}=
\frac{1}{|U_{\mathrm{new}}|}
\sum_{u\in U_{\mathrm{new}}}
\mathbf{1}\{\operatorname{dist}(\Omega_u,C_{\mathrm{parent}})>r_{\mathrm{attach}}\},
\]

\[
V_{\mathrm{sym}}(S;G)=
\frac{1}{|G|}
\sum_{g\in G}
d_{\mathcal S}(gS,S).
\]

Projection 是递归映射的一部分：

\[
P_\lambda:\mathcal{S}_{\mathrm{raw}}\rightarrow\mathcal{S}_{\mathrm{adm}}(\lambda).
\]

当前实现中的 largest component pruning、attachment-aware component selection、mesh export、re-encode 是该理想 projection 的可运行近似。

## 4. Rule schema

一条规则写成：

\[
r:\; X(\omega,\Omega,\ell,a,h)
\Rightarrow
\left\{
(X_j,T_j,\Omega_j,\rho_j,\mu_j,\beta_j,\psi_j,\zeta_j,\tau_j,\pi_j)
\right\}_{j=1}^{m}.
\]

含义：

- \(X,X_j\in\Sigma\)：输入/输出 symbol type。
- \(\omega\)：local frame。
- \(\Omega\)：输入局部 support 或 mesh region。
- \(\ell\)：logical depth / LOD。
- \(a\)：attributes and context。
- \(h\)：history/cache handle。
- \(T_j\in\mathcal{T}\)：输出 transform。
- \(\Omega_j\)：target edit region。
- \(\rho_j\)：proposal kernel，可为 deterministic transform-copy、attractor direction、hitting distribution、shape split、masked sampler。
- \(\mu_j\)：edit mask。
- \(\beta_j\)：blend kernel。
- \(\psi_j\)：precondition 或 context predicate。
- \(\zeta_j\)：random seed/noise。
- \(\tau_j\)：flow/SDE re-noising or integration schedule。
- \(\pi_j\in\Pi\)：local constraints。

规则选择可写成 context-sensitive Markov policy：

\[
\Pr(r\mid S_d,u_i)=
\frac{\exp a_r(S_d,u_i)}
\sum_{r'\in \mathcal{R}(u_i)}\exp a_{r'}(S_d,u_i)}.
\]

\(a_r\) 可以由手写 grammar score、frontier score、attractor coverage、symmetry orbit priority、token budget、projection diagnostics 或 deterministic operator choice 给出。

## 5. 一层递归操作语义

对选中的规则集合 \(R_d^\star=\mathcal{S}(S_d,\mathcal{R})\)，一层转移是 Markov kernel

\[
S_{d+1}\sim \mathbb{T}_{\mathcal{G},\theta,d}(\cdot\mid S_d),
\]

其可实现分解为

\[
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
\]

这是全文最重要的公式。它把 traditional grammar、learned sampler、projection、re-encode、cache update 放在一个递归算子内。

### 5.1 Proposal

\[
\operatorname{Prop}_{r}(S_d)
=
\{(\hat C_j,\hat F_j,\hat U_j,\hat A_j,\hat B_j,\hat M_j,\hat H_j)\}_{j=1}^{m}.
\]

Transform-copy proposal：

\[
\hat C_j=Q_h(T_j(C_d\cap\Omega)),\qquad
\hat F_j(Q_h(T_j c))=\mathcal{T}_j^F F_d(c).
\]

IFS、symmetry、crystal、portal、radial、translate、scale-down 都可写为该形式。当前很多实现采用 identity feature transport：

\[
\mathcal{T}_j^F=\mathrm{Id}.
\]

Attractor/space-colonization proposal：

\[
\mathcal{A}(b_i)=\{a\in\Gamma_d:\ i=\arg\min_j \|a-b_j\|\},
\]

\[
v_i=
\frac{
\sum_{a\in\mathcal{A}(b_i)}(a-b_i)/(\|a-b_i\|+\epsilon)
}{
\left\|
\sum_{a\in\mathcal{A}(b_i)}(a-b_i)/(\|a-b_i\|+\epsilon)
\right\|+\epsilon
},
\qquad
b_i'=Q_h(b_i+\delta v_i).
\]

DLA/frontier proposal：

\[
c_{\mathrm{new}}\sim p_{\mathrm{hit}}(c\mid C_d),\qquad
c_{\mathrm{new}}\notin C_d,\qquad
\operatorname{dist}(c_{\mathrm{new}},C_d)=1.
\]

Shape-grammar proposal：

\[
X(\Omega,T,\alpha)\rightarrow
\{X_j(\Omega_j,T\Delta T_j,\alpha_j)\}_{j=1}^{m},
\qquad
\Omega_j\subseteq\Omega.
\]

### 5.2 Merge

支撑集合合并为

\[
C^+=C_d\cup\bigcup_j \hat C_j.
\]

重复坐标的 feature merge 使用 mask/blend：

\[
F^+(c)=
\frac{
w_0(c)F_d(c)+\sum_j w_j(c)\hat F_j(c)
}{
w_0(c)+\sum_j w_j(c)+\epsilon
},
\qquad
w_j(c)=\mu_j(c)\beta_j(c).
\]

当前 `sparse_merge` 的 duplicate-coordinate averaging 是上式的均匀权重特例。

### 5.3 Competition and constrained thinning

合并后的 candidate 通过 competition/constraint operator：

\[
\Theta_{\Pi}(S)=
\arg\max_{S'\subseteq S}
\left[
Q_{\mathrm{grow}}(S';A_d)
-\lambda_{\mathrm{occ}}V_{\mathrm{occ}}(S')
-\lambda_{\mathrm{col}}V_{\mathrm{col}}(S')
-\lambda_{\mathrm{frag}}V_{\mathrm{frag}}(S')
-\lambda_{\mathrm{sym}}V_{\mathrm{sym}}(S')
-\lambda_{\mathrm{tok}}\max(0,|C(S')|-T_{\max})
\right].
\]

局部贪心近似可写为：

\[
c\in C_{\mathrm{keep}}
\Longleftrightarrow
\begin{cases}
O_d(c)=0,\\
\operatorname{dist}(c,C_{\mathrm{parent}})\leq r_{\mathrm{attach}},\\
\psi(c;S_d)>\eta,\\
\Delta V_{\mathrm{sym}}(c)\leq \epsilon_g.
\end{cases}
\]

泛化 competition score：

\[
\psi(a,c;S_d)
=
\lambda_{\mathrm{att}}\phi_{\mathrm{att}}
-\lambda_{\mathrm{occ}}\phi_{\mathrm{occ}}
-\lambda_{\mathrm{col}}\phi_{\mathrm{collision}}
+\lambda_{\mathrm{front}}\phi_{\mathrm{frontier}}
+\lambda_{\mathrm{grp}}\phi_{\mathrm{orbit}}
+\epsilon_\theta(c,\xi).
\]

前几项覆盖 classical attractor、occupancy、collision、frontier logic；\(\epsilon_\theta\) 表示 learned sampler 的 stochastic preference 或 uncertainty。

### 5.4 Masked SDE / flow naturalization

冻结 Trellis2 sampler 不应被写成最终 cleanup，而应写成条件 naturalization kernel：

\[
\bar S\sim
\mathcal{N}_{\theta,\Omega}^{\tau\rightarrow0}(\cdot\mid S^+,y,\mu,H).
\]

以 SDE/flow 形式：

\[
dZ_t=v_\theta(Z_t,t,y,\Omega)\,dt+\sigma(t)\,dW_t,\qquad t:\tau\rightarrow0,
\]

其中 \(Z_t=(C_t,F_t,M_t)\) 或只包含 features/material latents。mask preservation 可写为 hard/soft clamp：

\[
Z_{t-\Delta t}\leftarrow
(1-\mu_\Omega)\odot Z_{\mathrm{anchor}}
+
\mu_\Omega\odot \Phi_{\theta,t}(Z_t,y).
\]

Feature-level naturalization：

\[
F_{\mathrm{new}}^{(k)}
\sim
p_\theta(F_{\mathrm{new}}\mid C^+,F^+,\mu_\Omega,y,H_d),
\]

sample selection：

\[
k^\star=
\arg\min_k
\left[
V_{\mathrm{frag}}(P_\lambda(D_\theta(S^{(k)})))
+\lambda_a V_{\mathrm{attach}}(P_\lambda(D_\theta(S^{(k)})))
+\lambda_s V_{\mathrm{sym}}(P_\lambda(D_\theta(S^{(k)})))
-\lambda_q Q_{\mathrm{nat}}(S^{(k)})
\right].
\]

这给出 Trellis2/frozen generative sampler 的统一语义：它不是替代 grammar 的全局生成器，而是在 grammar 指定的 mask、condition、constraint 内给新增长区域或边界区域提供 local naturalization。

当前实验边界必须写清楚：full flow repair 容易 wash out recursive topology；主文只能把 masked/local naturalization 作为 framework component 和部分 smoke test，不能声称已经证明 topology-preserving SDE。

### 5.5 Decode, projection, re-encode

\[
\tilde x_{d+1}=\mathcal{D}_\theta(\bar S_{d+1}),
\]

\[
x_{d+1}^\star=
\mathcal{P}_{\lambda_d}(\tilde x_{d+1};A_d,H_d),
\]

\[
S_{d+1}^{\mathrm{precache}}=
\mathcal{E}_\theta(x_{d+1}^\star).
\]

Projection 可写成优化：

\[
\mathcal{P}_{\lambda}(x)=
\arg\min_{y\in\mathcal{X}_{\mathrm{adm}}}
d_{\mathrm{mesh}}(x,y)
+\lambda_1V_{\mathrm{frag}}(y)
+\lambda_2V_{\mathrm{attach}}(y)
+\lambda_3V_{\mathrm{render}}(y)
+\lambda_4V_{\mathrm{sym}}(y)
+\lambda_5d_{\mathrm{support}}(E_\theta(x),E_\theta(y)).
\]

Per-depth projection：

\[
S_{d+1}
=
\mathcal{E}_\theta\circ\mathcal{P}_{\lambda_d}\circ\mathcal{D}_\theta
\circ \mathcal{G}_{r_d}(S_d),
\]

不同于 final-only cleanup：

\[
S_D^{\mathrm{final}}
=
\mathcal{E}_\theta\circ\mathcal{P}_{\lambda_D}\circ\mathcal{D}_\theta
\circ \mathcal{G}_{r_{D-1}}\circ\cdots\circ\mathcal{G}_{r_0}(S_0).
\]

前者把 projection 后的状态反馈给下一层 grammar，后者让中间坏碎片参与后续 frontier、competition、sampler condition 和 history trace。

### 5.6 Cache and LOD update

\[
K_{d+1}=
\mathcal{C}(K_d,S_{d+1}^{\mathrm{precache}},R_d^\star,H_d).
\]

cache lookup 可参与 proposal：

\[
(\hat C,\hat F,\hat U)
=
\operatorname{Lookup}(K_d^{\mathrm{motif}},k,T,\ell),
\]

LOD collapse：

\[
\operatorname{Collapse}_\ell(C,F)
=(C^{(\ell)},F^{(\ell)},\epsilon_\ell),
\qquad |C^{(\ell)}|\ll |C|.
\]

Sliding-window active state：

\[
S_t^{\mathrm{active}}=
\{S_{\Omega,t}:\Omega\in W_t\},
\qquad
\sum_{\Omega\in W_t}|C_{\Omega,t}^{\mathrm{active}}|\leq T_{\max}.
\]

窗口外区域表示为 cache descriptor：

\[
\kappa=(\mathrm{cache\_id},T,\ell,\mathrm{material\_intent},\epsilon_{\mathrm{cache}}).
\]

因此 infinite recursion 的诚实语义不是“当前系统物化了无限 3D mesh”，而是：

1. contractive maps 的有限深度近似；
2. fixed visible window 内的 on-demand expansion；
3. LOD/cache descriptor 表示窗口外逻辑递归。

## 6. 经典系统覆盖

本节的“覆盖”只表示存在一个 PS-RSLG 的退化或受限实例，其有限步状态转移与经典系统相同或在量化误差内相同。它不表示视觉质量更好，也不表示当前实现已经对每类都有强实验结果。

### 6.1 IFS

经典 IFS：

\[
A_{k+1}=\bigcup_{i=1}^{m}f_i(A_k),
\qquad f_i:X\rightarrow X.
\]

取 \(\Sigma=\{A\}\)、\(\mathcal{T}=\{f_i\}_{i=1}^m\)、\(N_\theta=P_\lambda=\Theta_\Pi=\mathcal{C}=\mathrm{Id}\)，merge 为集合并，规则

\[
A\rightarrow\{(A,f_i,\Omega,\rho_i,1,1,\top,0,0,\emptyset)\}_{i=1}^{m}.
\]

则连续 support 下

\[
C_{d+1}=\bigcup_i f_i(C_d).
\]

离散 grid 下得到

\[
C_{d+1}^{(h)}=\bigcup_i Q_h(f_i(C_d^{(h)})).
\]

若 \(f_i\) 是 contraction，则 contractive IFS 的 Hutchinson 极限可作为 appendix 理论命题；当前 pipeline 只能声明 finite-depth approximation。

### 6.2 L-system

确定性同步 L-system：

\[
\omega_{d+1}=w_{a_1}w_{a_2}\cdots w_{a_n},
\qquad \omega_d=a_1a_2\cdots a_n.
\]

取 \(U_d\in\Sigma^\star\) 为有序 typed anchor 序列，scheduler 同步应用每个 symbol 的规则，merge 是稳定拼接。规则 \(a\mapsto b_1\cdots b_m\) 写成

\[
a(T_i)\rightarrow
\{b_j(T_i\Delta T_j)\}_{j=1}^{m}.
\]

解释函数 \(\mathcal{I}\) 是 turtle/frame-to-geometry map。若禁用 sampler/projection，则恢复标准 L-system；若保留 Trellis2 naturalization 和 projection，则得到 sparse-latent L-system variant。

### 6.3 Space colonization

显式保存 attractors \(\Gamma_d\) 和 tips \(\mathcal{F}_d\)，使用最近 tip 分配和平均方向增长，即第 5.1 节公式。occupancy exclusion、attachment、attractor deletion 分别由 \(O_d,\Pi,H_d\) 维护。禁用 learned sampler 时，该 rule 等价于 Runions-style space colonization 的一次迭代。当前 `compete_grow` 是该规则的简化实现，适合作为主文 coverage 和实验主线。

### 6.4 DLA / frontier accretion

将 hitting distribution 写入 proposal kernel：

\[
c_{\mathrm{new}}\sim p_{\mathrm{hit}}(\cdot\mid C_d),
\qquad
C_{d+1}=C_d\cup\{c_{\mathrm{new}}\}.
\]

禁用 sampler/projection 时可表达离散 DLA Markov kernel；启用 masked sampler 时，hitting point 决定 structural scaffold，latent/material 由 learned distribution naturalize。当前 DLA/porous 应作为 stress test 或 appendix，除非补足视觉和 metric。

### 6.5 Finite local shape grammar

对有限规则、有限参数、局部 frame/mask 可表达的 shape grammar：

\[
X(\Omega,T,\alpha)
\rightarrow
\{X_j(\Omega_j,T\Delta T_j,\alpha_j)\}_{j=1}^m,
\qquad
\Omega_j\subseteq\Omega.
\]

PS-RSLG 逐条建立同名 typed rule，\(\Omega_j\) 解释为 sparse mask 或 decoded mesh region，\(T\Delta T_j\) 解释为 scope transform。可覆盖 split、extrude、replace、subdivide、repeat、portal/tile 等有限局部子类。

不能声称覆盖所有 shape grammar，因为任意布尔几何、连续约束求解、全局优化和无限精度谓词需要额外语义。

### 6.6 Symmetry and crystal

设有限群或有限窗口内的晶格群 \(G\) 作用在状态空间上。规则闭包：

\[
\forall g\in G,\ r\in R,\qquad g\circ r\circ g^{-1}\in R.
\]

若 proposal、merge、projection、sampler、codec 都与 \(G\) 近似交换：

\[
d_{\mathcal S}(A_i(gX),gA_i(X))\leq L_i\epsilon_X+\epsilon_i,
\]

则一层算子的 symmetry error 由各模块交换误差累积控制：

\[
d_{\mathcal S}(\mathbb{T}(gS),g\mathbb{T}(S))
\leq
\epsilon_{\mathrm{rule}}
\epsilon_{\mathrm{merge}}
\epsilon_{\mathrm{sampler}}
\epsilon_{\mathrm{proj}}
\epsilon_{\mathrm{codec}}
\quad\text{up to Lipschitz factors}.
\]

晶体/周期规则用 lattice action \(\Lambda\) 表述：

\[
C_{d+1}=C_d\cup\bigcup_{\lambda\in\Lambda\cap W_d} Q_h(T_\lambda C_{\mathrm{cell}}),
\]

其中 \(W_d\) 是有限可见窗口或 token budget。无限晶格只能通过窗口或 cache descriptor 表示。

### 6.7 Infinite recursion

有两种严谨语义：

**Contractive limit.** 若 \(\{f_i\}\) 是 contraction，则 IFS 有唯一 attractor。PS-RSLG 在退化设定下表达其有限步 Hutchinson iteration。

**Visible-window streaming.** 若每一时刻只展开 \(W_t\) 内 active support，且调度器保持

\[
\sum_{\Omega\in W_t}|C_{\Omega,t}^{\mathrm{active}}|\leq T_{\max},
\]

则 active token memory 有界。窗口外逻辑递归由 cache descriptor 表示。该命题只证明 memory bound，不证明无损重建或 stitching。

## 7. Projection stability 命题

令 \(e(S)\in[0,1]\) 表示坏碎片、无附着组件、不可渲染 support 或违反约束区域的归一化质量。

考虑每层 projection recursion：

\[
S_{d+1}=
\mathcal{E}_\theta\circ
P_{\lambda_d}\circ
\mathcal{D}_\theta\circ
G_d(S_d),
\]

其中 \(G_d=\mathcal{N}_{\theta}\circ\Theta_\Pi\circ\operatorname{Merge}\circ\operatorname{Prop}\)，或禁用 sampler 的版本。

若：

\[
e(P_{\lambda_d}(X))\leq\epsilon_P
\]

且

\[
e(\mathcal{E}_\theta(Y))\leq e(Y)+\epsilon_E,
\]

并且 projection 每层返回非空 admissible state，则

\[
e(S_d)\leq \epsilon_P+\epsilon_E,\qquad 1\leq d\leq D.
\]

证明是直接的：每层 projection 把 bad mass 重置到 \(\epsilon_P\)，codec loop 最多增加 \(\epsilon_E\)。

对 final-only cleanup，只能写：

\[
e(\bar S_{d+1})\leq \alpha e(\bar S_d)+\eta_d
\Rightarrow
e(\bar S_D)\leq \alpha^D e(\bar S_0)+
\sum_{k=0}^{D-1}\alpha^{D-1-k}\eta_k.
\]

这说明中间状态不享有同一逐层上界。不能仅凭该式证明 final-only 一定失败；更强 claim 需要说明坏碎片会污染后续 frontier、sampler condition 或 history，且最终 projection 无法恢复这些历史依赖。

## 8. 可主文写、可附录写、风险 claim

| Claim | 建议位置 | 强度 |
|---|---|---|
| PS-RSLG 定义了 typed sparse-latent recursive grammar，状态为 \(S_d=(C,F,U,A,B,M,H,K)\) | 主文 Method | 强 |
| 一层递归是 proposal -> merge -> competition -> masked naturalization -> decode -> projection -> re-encode -> cache | 主文 Method | 强 |
| IFS、L-system、space colonization、DLA-like frontier、finite local shape grammar 是退化/受限实例 | 主文简表 + appendix 证明 | 中强 |
| Space competition 是当前最稳的主线 operator，连接传统 space colonization 和 sparse support growth | 主文 Method/Experiment | 强，需绑定实验 |
| Frozen Trellis2 sampler 提供 masked local naturalization，不接管全局 topology | 主文 Method | 中等，需写 mixed evidence |
| Per-depth projection 在显式假设下界定 bad fragment mass | 主文 proposition + appendix proof | 中强 |
| Symmetry/crystal 需要近似交换条件，误差可累积界定 | 主文短句 + appendix | 中等 |
| Infinite recursion 只能是 finite-depth realization、contractive limit 或 bounded visible-window/cache proxy | 主文 limitation/extension | 强但保守 |
| Full flow/SDE repair preserves recursive topology | 不应写 | 当前负证据 |
| 严格 symmetry/crystal equivariance guaranteed by implementation | 不应写 | 需要 sampler/projection/codec 证据 |
| 已实现真正 infinite 3D generation | 不应写 | 当前只有限深度和 proxy |
| 覆盖所有 shape grammars | 不应写 | 只能覆盖有限局部子类 |

## 9. 给论文方法节的压缩结构

建议主文 Method 组织如下：

1. **Problem and state.** 定义 finite-depth recursive asset、sparse state \(S_d\)。
2. **Grammar definition.** 给出 \(\mathcal{G}\) tuple、rule schema 和 rule selection。
3. **Operational semantics.** 给出核心复合算子：

\[
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
\]

4. **Coverage proposition.** 一段文字 + table，不把完整证明放主文。
5. **Sparse competition and naturalization.** 给 competition score 和 masked SDE clamp。
6. **Projection-stabilized recursion.** 给 admissible set、projection optimization 和 weak stability proposition。
7. **Symmetry/cache/infinite recursion.** 只写 conditional support 和 extension boundary。

## 10. 最终边界

PS-RSLG v2 足以支撑一篇 graphics method paper 的 formal spine，但它必须和实验 claim 对齐。最稳的主贡献不是“我们实现了所有递归宇宙”，而是：

1. 用一个统一 grammar state 把传统递归程序和 frozen sparse 3D generator 接起来；
2. 把 learned sampler 限制为 masked local naturalization；
3. 把 projection/re-encode 放进每一层 recursive semantics；
4. 用 coverage propositions 说明该语法不是临时 operator list；
5. 用 projection ablation 和 space-competition 实验证明该 semantics 对稳定性有实际意义。
