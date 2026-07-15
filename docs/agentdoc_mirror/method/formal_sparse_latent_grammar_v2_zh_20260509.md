# Formal Sparse-Latent Grammar v2: grammar-based generated-model system 方法论框架

创建时间：2026-05-09  
项目：`recursive_3d_generative_growth`  
写作范围：理论/方法论草稿；不修改 `paper_siga/main.tex`。  
建议论文名词：**Projection-Stabilized Sparse-Latent Grammar (PS-SLG)**，或沿用现有 **PS-RSLG**。

## 0. 主要结论

这版框架把当前系统从“稀疏 token 复制 + 解码 + 修剪 + 贴图”的工程流水线，提升为一个 **grammar-based generated-model system**：

1. 语法是主程序：它管理 typed symbols、局部 frame、递归深度、transform、空间竞争、projection 约束、缓存和材质意图。
2. 冻结 3D 生成模型不是后处理器：它提供 sparse native 3D latent state、masked flow/SDE sampler、decoder、mesh-to-latent re-encoder、texture/material latent prior 和 PBR export。
3. 传统方法是退化实例：IFS、L-system、space colonization、DLA/frontier accretion、有限 shape grammar 和 symmetry transform-copy 都可由禁用 learned sampler/projection 或限制 scheduler 得到。
4. Projection 是递归语义的一部分：每层 decode/project/re-encode 把状态拉回 admissible recursive asset set，避免碎片、漂浮块和错误 frontier 进入下一层。
5. Infinite recursion 不能作为当前实现主张：论文应写 finite-depth asset generation；无界递归只能以 contractive limit、bounded visible window、LOD/cache streaming 或 symbolic descriptor 形式讨论。
6. Material/texture state 必须进入状态空间：否则系统只能证明 geometry recursion，不能解释 Trellis2 texture-SLAT/PBR export 如何与递归结构一致。

适合 SIGGRAPH Asia 方法节的核心 claim：

> PS-SLG defines recursive 3D asset generation as typed rewriting over the sparse native latent state of a frozen 3D generator. Classical procedural growth systems are recovered as special cases; learned flow/SDE sampling enters as masked local naturalization; per-depth projection and cache semantics make finite-depth recursion stable under explicit assumptions.

## 1. 问题定义

给定 root asset \(x_0\)、可选条件 \(y\)（image/text/category/material）、冻结 native 3D generator 参数 \(\theta\)、递归语法 \(\mathcal{G}\) 和有限深度 \(D\)，目标是生成可渲染资产

\[
x_D=\mathcal{O}(S_D),
\qquad
S_{d+1}\sim \mathbb{T}_{\mathcal{G},\theta,d}(\cdot\mid S_d,y,\xi_d),
\quad d=0,\ldots,D-1.
\]

其中 \(\xi_d\) 包括 rule choice、DLA hitting、flow/SDE sampler 和 sample selection 的随机性。该任务不是 one-shot image-to-3D，也不是传统 procedural mesh generator，而是：

\[
\text{recursive program control}
\;+\;
\text{frozen sparse 3D generative prior}
\;+\;
\text{projection-stabilized finite-depth asset export}.
\]

应避免的过强表述：

- 不说“实现真实无限 3D 生成”；
- 不说“flow/SDE sampler 保证拓扑保持”；
- 不说“严格 symmetry/equivariance”；
- 不说“所有 shape grammar 都被覆盖”。

可说的稳健表述：

- 当前系统生成 finite-depth recursive assets；
- 传统 procedural families 是语法的可表达退化实例；
- projection 给出每层状态 invariant 的假设性保证；
- 生成模型改善 local naturalization/material export，但必须被 mask、projection 和 rule ownership 约束。

## 2. 状态空间：typed sparse generated state

设连续空间 \(X\subset \mathbf{R}^3\)，离散网格 \(L_h=h\mathbf{Z}^3\)，Trellis/O-Voxel/SLAT 风格的 batch-augmented sparse coordinate domain 为

\[
\bar L_h=\{0\}\times L_h.
\]

深度 \(d\) 的状态是

\[
S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d,K_d).
\]

### 2.1 Sparse support

\[
C_d\subset \bar L_h,
\qquad |C_d|\le T_{\max}(d).
\]

\(C_d\) 是 active sparse support。它既可来自 mesh-to-O-Voxel/SLAT encoding，也可由 grammar transform-copy、frontier accretion、attractor growth 或 cache lookup 提议。对连续 procedural 方法，使用量化解释

\[
Q_h:\mathcal{P}(X)\rightarrow \mathcal{P}(L_h),
\qquad
Q_h(A)=\{q\in L_h:\operatorname{dist}(q,A)\le h/2\}.
\]

连续等价命题应在 \(X\) 上陈述；实际实现只得到固定 \(h\) 下的量化近似。

### 2.2 Latent features

\[
F_d:C_d\rightarrow
\mathbf{R}^{q_s}\times \mathbf{R}^{q_m}\times \mathbf{R}^{q_a}.
\]

- \(q_s\)：shape sparse latent feature。
- \(q_m\)：material/texture/PBR latent feature。
- \(q_a\)：grammar auxiliary feature，如 age、radius、semantic type、local frame code、confidence、owner id、frontier score。

现有实验若主要操作 shape-SLAT，可令 \(q_m=0\)；但 paper-level formalism 应保留 \(q_m\)，否则 texture material state 无法进入语义。

### 2.3 Symbols and ownership

\[
U_d=\{u_i\}_{i=1}^{n_d},
\qquad
u_i=(\sigma_i,\ell_i,T_i,\Omega_i,\alpha_i,\nu_i).
\]

- \(\sigma_i\in\Sigma\)：typed symbol，例如 `Root`、`Tip`、`Branch`、`AttractorCell`、`Frontier`、`Patch`、`Portal`、`Tile`、`CrystalFace`、`SymOrbit`、`MaterialSeed`、`LODChunk`。
- \(\ell_i\)：logical recursion level 或 LOD level。
- \(T_i\)：local-to-global transform 或 frame。
- \(\Omega_i\subseteq C_d\)：该 symbol 管辖的 support。
- \(\alpha_i\)：局部属性，如 radius、growth probability、branch order、material tag。
- \(\nu_i\)：scheduler/cache metadata，如 parent id、priority、random seed、cache handle。

为了覆盖 L-system，\(U_d\) 必须允许有序结构：

\[
U_d\in \Sigma^\star
\quad\text{or}\quad
U_d=(V_d,E_d,\operatorname{ord}_d,\sigma,T,\alpha).
\]

无序集合只能覆盖无序 graph grammar 或 asynchronous rewriting，不能严格覆盖标准同步 L-system。

### 2.4 Auxiliary fields

\[
A_d=(O_d,\Gamma_d,\mathcal{F}_d,\mathcal{K}_d,\mathcal{E}_d,\mathcal{Q}_d,\mathcal{G}_d).
\]

- \(O_d:L_h\rightarrow\{0,1\}\)：occupancy/exclusion。
- \(\Gamma_d:L_h\rightarrow \mathbf{R}_{\ge0}\)：attractor/density/target field。
- \(\mathcal{F}_d\subset L_h\)：frontier 或 tip candidate set。
- \(\mathcal{K}_d\)：component graph、attachment graph、adjacency graph。
- \(\mathcal{E}_d\)：collision、forbidden region、self-intersection estimates。
- \(\mathcal{Q}_d\)：quality estimates，如 fragment risk、attachment score、renderability、symmetry error。
- \(\mathcal{G}_d\)：group/lattice/orbit metadata。

### 2.5 Masks and boundary state

\[
B_d=(\partial C_d,\{\mu_k\},\{\omega_k\},\{\chi_k\}).
\]

\(\mu_k:L_h\rightarrow[0,1]\) 是 edit mask，\(\omega_k\) 是 blend kernel，\(\chi_k\) 是 hard clamp indicator。Masked naturalization 必须依赖 \(B_d\)，否则 sampler 会把全局 scaffold 当作可重采样内容，导致 topology overwrite。

### 2.6 Material and texture state

材质状态定义为

\[
M_d=(F_d^{m},P_d^{\mathrm{brdf}},Y_d^{m},\tau_d^m,\mu_d^m,\kappa_d^m,\operatorname{atlas}_d).
\]

- \(F_d^{m}:C_d\rightarrow\mathbf{R}^{q_m}\)：texture/material sparse latent。
- \(P_d^{\mathrm{brdf}}\)：可解释 PBR 参数场，如 base color、roughness、metallic、normal、alpha。
- \(Y_d^{m}\)：material condition，例如 text、reference image、style id、category id。
- \(\tau_d^m\)：texture sampler schedule。
- \(\mu_d^m\)：texture edit mask。
- \(\kappa_d^m\)：material continuity constraints，如 seam consistency、part consistency、symmetry material tying。
- \(\operatorname{atlas}_d\)：UV/atlas/GLB export metadata。

材质递归不应简单写作最终贴图。更正确的语义是：

\[
M_{d+1}
=
\operatorname{ProjectMaterial}_{\lambda_m}
\circ
\operatorname{DecodeTexture}_{\theta}
\circ
\mathcal{N}_{\theta,m}^{\tau_d^m\rightarrow0}
\circ
\operatorname{MergeMaterial}_{\mu_d^m}
(M_d,\widehat M_d).
\]

若当前实验只在最终 geometry 后运行 Trellis2 texturing，也应在文中诚实写为：

\[
M_{D}=\operatorname{TextureExport}_{\theta}(E_\theta(x_D),Y^m),
\]

并说明这是 geometry recursion 之后的 compatible export，而不是已证明的 per-depth material recursion。

### 2.7 History and caches

\[
H_d=(d,\xi_{0:d},\mathcal{R}_{0:d},\mathcal{T}_{0:d},\lambda_{0:d},\operatorname{diag}_{0:d}).
\]

\[
K_d=(K_d^{\mathrm{motif}},K_d^{\mathrm{latent}},K_d^{\mathrm{transform}},
K_d^{\mathrm{LOD}},K_d^{\mathrm{window}},K_d^{\mathrm{sampler}},K_d^{\mathrm{material}}).
\]

缓存不是实现细节。它决定 repeated motif 是否按相同 latent/material state 复用，决定 infinite zoom 是否以 descriptor 而非完整 mesh 展开，也决定 sampler 是否能复用局部条件和 noise seed。一个 cache entry 可写作

\[
k=(\operatorname{id},\sigma,T,\Omega,C_\Omega,F_\Omega,M_\Omega,\ell,\eta,\operatorname{validity},\operatorname{cost}).
\]

Cache lookup 是 proposal kernel 的一种：

\[
(\widehat C,\widehat F,\widehat M)
=
\operatorname{Lookup}(K_d,\operatorname{id})\circ T.
\]

Cache update 是递归转移的一部分：

\[
K_{d+1}=\operatorname{UpdateCache}(K_d,S_{d+1},R_d^\star,\operatorname{diag}_{d+1}).
\]

## 3. 语法对象

定义

\[
\mathcal{G}=
(\Sigma,\mathcal{T},\mathcal{R},\mathcal{I},\mathcal{S},\Pi,
\mathcal{N}_{\theta}^{s},\mathcal{N}_{\theta}^{m},
\mathcal{D}_{\theta},\mathcal{E}_{\theta},
\mathcal{P},\mathcal{C},\mathcal{O},\mathcal{L}).
\]

其中：

- \(\Sigma\)：typed alphabet。
- \(\mathcal{T}\)：transform group/semigroup，包括 rigid transform、scale、anisotropic scale、mirror、portal embedding、lattice translation、contractive map、LOD transform。称 semigroup 是因为 projection、LOD collapse 和 cache bake 可不可逆。
- \(\mathcal{R}\)：stochastic context-sensitive rewrite rules。
- \(\mathcal{I}\)：把 symbols/frames/masks 解释为 sparse support、features、mesh regions 和 material regions。
- \(\mathcal{S}\)：scheduler，支持 synchronous、asynchronous、priority queue、frontier sampling、group-orbit expansion。
- \(\Pi\)：occupancy、attachment、topology、competition、symmetry、renderability、token/material budget constraints。
- \(\mathcal{N}_{\theta}^{s}\)：shape latent masked flow/SDE naturalizer。
- \(\mathcal{N}_{\theta}^{m}\)：material/texture latent sampler。
- \(\mathcal{D}_{\theta}\)：decoder/exporter，从 sparse latent state 到 mesh/material asset。
- \(\mathcal{E}_{\theta}\)：mesh-to-sparse re-encoder。
- \(\mathcal{P}\)：projection family。
- \(\mathcal{C}\)：cache lookup/update semantics。
- \(\mathcal{O}\)：observable/export map，如 mesh、GLB、render、metric record。
- \(\mathcal{L}\)：rule selection、projection、sample selection 的 score family。

一条规则写作

\[
r:\;X(\omega,\Omega,\ell,a,h)
\Rightarrow
\{(X_j,T_j,\Omega_j,\rho_j,\mu_j,\beta_j,\psi_j,\zeta_j,\tau_j,\pi_j,\kappa_j)\}_{j=1}^{m}.
\]

各项含义：

- \(X,X_j\in\Sigma\)：输入/输出 symbol type。
- \(\omega\)：local frame。
- \(\Omega\)：局部 support 或 mesh/material region。
- \(\ell\)：depth/LOD。
- \(a\)：attributes and context。
- \(h\)：history/cache handle。
- \(T_j\in\mathcal{T}\)：输出 transform。
- \(\rho_j\)：proposal kernel，可为 transform-copy、space-colonization direction、DLA hitting、shape split、cache lookup、masked sampler。
- \(\mu_j,\beta_j\)：edit mask 和 blend kernel。
- \(\psi_j\)：precondition/context predicate。
- \(\zeta_j\)：random seed/noise。
- \(\tau_j\)：shape/material flow/SDE schedule。
- \(\pi_j\)：local geometry constraints。
- \(\kappa_j\)：material/texture continuity constraints。

Rule choice 可写作

\[
\Pr(r\mid S_d,u_i)
=
\frac{\exp a_r(S_d,u_i)}
{\sum_{r'\in\mathcal{R}(u_i)}\exp a_{r'}(S_d,u_i)}.
\]

当前实验多数可设为 deterministic 或 low-entropy，以减少 prompt/sampling variance 对 stability claim 的干扰。

## 4. 一层递归操作语义

选中规则集合

\[
R_d^\star=\mathcal{S}(S_d,\mathcal{R}).
\]

一层递归转移为 Markov kernel

\[
S_{d+1}\sim \mathbb{T}_{\mathcal{G},\theta,d}(\cdot\mid S_d,y,\xi_d),
\]

可实现分解为

\[
S_{d+1}
=
\mathcal{C}_{d+1}\circ
\mathcal{E}_\theta\circ
\mathcal{P}_{\lambda_d}\circ
\mathcal{D}_\theta\circ
\mathcal{N}_{\theta,m}^{\tau_d^m\rightarrow0}\circ
\mathcal{N}_{\theta,s}^{\tau_d^s\rightarrow0}\circ
\Theta_{\Pi_d}\circ
\operatorname{Merge}_{B_d,M_d}\circ
\operatorname{Prop}_{R_d^\star}(S_d).
\]

这是建议放进 SIGA Method 的中心公式。它表达四个立场：

1. Grammar proposal 先于生成模型。
2. Flow/SDE sampler 只在 mask 和 constraints 下自然化局部区域。
3. Projection 在递归 loop 内，不是最终 cleanup。
4. Re-encoding 和 cache update 是下一层 rule semantics 的输入。

### 4.1 Proposal

\[
\operatorname{Prop}_{r}(S_d)
=
\{(\widehat C_j,\widehat F_j,\widehat U_j,\widehat A_j,\widehat B_j,\widehat M_j)\}_{j=1}^{m}.
\]

Transform-copy:

\[
\widehat C_j=Q_h(T_j(C_d\cap\Omega)),
\qquad
\widehat F_j(Q_h(T_jc))=\mathcal{T}_j^F F_d(c).
\]

Material transport:

\[
\widehat M_j(Q_h(T_jc))
=\mathcal{T}_j^M M_d(c),
\]

其中 \(\mathcal{T}_j^M\) 可是 copy、style-tie、randomize、symmetry-tie 或 material-condition replacement。

### 4.2 Merge

\[
C^+=C_d\cup\bigcup_j\widehat C_j.
\]

\[
F^+(c)
=
\frac{w_0(c)F_d(c)+\sum_j w_j(c)\widehat F_j(c)}
{w_0(c)+\sum_j w_j(c)+\epsilon},
\qquad
w_j(c)=\mu_j(c)\beta_j(c).
\]

材质 merge：

\[
M^+(c)
=
\operatorname{BlendMaterial}
\left(M_d(c),\{\widehat M_j(c)\}_j,\{\mu_j(c),\kappa_j(c)\}_j\right).
\]

### 4.3 Competition and constraints

对 candidate action \(a\) 和坐标 \(c\)，竞争分数可写为

\[
\psi(a,c;S_d)=
\lambda_{\mathrm{att}}\phi_{\mathrm{att}}(a,c)
-\lambda_{\mathrm{occ}}\phi_{\mathrm{occ}}(a,c)
-\lambda_{\mathrm{col}}\phi_{\mathrm{collision}}(a,c)
+\lambda_{\mathrm{front}}\phi_{\mathrm{frontier}}(a,c)
+\lambda_{\mathrm{grp}}\phi_{\mathrm{orbit}}(a,c)
+\epsilon_{\theta}(a,c,\xi).
\]

\[
a^\star(c)=\operatorname*{arg\,max}_{a\in\mathcal{A}(c)}\psi(a,c;S_d).
\]

前四项覆盖 space-colonization、occupancy、collision 和 DLA/frontier 逻辑；\(\phi_{\mathrm{orbit}}\) 覆盖 symmetry/crystal orbit；\(\epsilon_{\theta}\) 表示生成模型的局部不确定性或 sampler preference。现阶段若 \(\epsilon_{\theta}\) 尚未稳定实现，应在论文中写为 optional formal component。

## 5. Flow/SDE sampler 作为局部 naturalization

Shape latent naturalization 可写为 SDE：

\[
dZ_t=f_\theta(Z_t,t,y,\Omega)\,dt+g(t)\,dW_t,
\qquad t:\tau_d^s\rightarrow0,
\]

或 deterministic flow/ODE：

\[
\frac{dZ_t}{dt}=v_\theta(Z_t,t,y,\Omega).
\]

Masked clamp 语义：

\[
Z_{t-\Delta t}
\leftarrow
(1-\mu_\Omega)\odot Z_{\mathrm{anchor}}
+\mu_\Omega\odot \Phi_{\theta,t}(Z_t,y).
\]

对应到 feature：

\[
F^{n}(c)=
\begin{cases}
F^+(c), & \mu_\Omega(c)=0,\\
(1-\alpha_d(c))F^+(c)+\alpha_d(c)F_\theta(c), & \mu_\Omega(c)>0.
\end{cases}
\]

Material sampler：

\[
dZ_t^m=f_{\theta,m}(Z_t^m,t,Y_d^m,C^+,F^+)\,dt+g_m(t)\,dW_t^m,
\qquad t:\tau_d^m\rightarrow0.
\]

Material clamp：

\[
Z_{t-\Delta t}^m
\leftarrow
(1-\mu_d^m)\odot Z_{\mathrm{anchor}}^m
+\mu_d^m\odot\Phi_{\theta,m,t}(Z_t^m,Y_d^m).
\]

Sample selection 不能只看 aesthetic score，应看 projection 后是否保留递归结构：

\[
k^\star=
\operatorname*{arg\,min}_{k}
\Big[
V_{\mathrm{frag}}(P(D_\theta(S^{(k)})))
+\lambda_a V_{\mathrm{attach}}(P(D_\theta(S^{(k)})))
+\lambda_s V_{\mathrm{sym}}(P(D_\theta(S^{(k)})))
+\lambda_m V_{\mathrm{mat}}(P(D_\theta(S^{(k)})))
-\lambda_q Q_{\mathrm{nat}}(S^{(k)})
\Big].
\]

论文中的安全表述：

> The frozen sampler is a masked local prior, not the owner of global recursion. Global repair may overwrite recursive topology; therefore local masks, hard clamps, projection and sample selection are part of the grammar semantics.

## 6. Projection and admissible recursive states

定义可接受状态集合

\[
\mathcal{S}_{\mathrm{adm}}(\lambda)=
\{S:
V_{\mathrm{frag}}(S)\le\epsilon_f,\;
V_{\mathrm{attach}}(S)\le\epsilon_a,\;
V_{\mathrm{occ}}(S)\le\epsilon_o,\;
V_{\mathrm{sym}}(S;G)\le\epsilon_g,\;
V_{\mathrm{mat}}(S)\le\epsilon_m,\;
V_{\mathrm{render}}(\mathcal{O}(S))\le\epsilon_r,\;
|C(S)|\le T_{\max}
\}.
\]

示例 violation：

\[
V_{\mathrm{frag}}(S)
=
1-\frac{\operatorname{mass}(C_{\mathrm{largest\ attached}})}
{\operatorname{mass}(C)+\epsilon}.
\]

\[
V_{\mathrm{attach}}(S)
=
\frac{1}{|U_{\mathrm{new}}|}
\sum_{u\in U_{\mathrm{new}}}
\mathbf{1}\{\operatorname{dist}(\Omega_u,C_{\mathrm{parent}})>r_{\mathrm{attach}}\}.
\]

\[
V_{\mathrm{sym}}(S;G)=
\frac{1}{|G|}\sum_{g\in G}d_{\mathcal{S}}(gS,S).
\]

\[
V_{\mathrm{mat}}(S)
=
\lambda_{\mathrm{seam}}V_{\mathrm{seam}}(M)
+\lambda_{\mathrm{part}}V_{\mathrm{part}}(M,U)
+\lambda_{\mathrm{pbr}}V_{\mathrm{pbr}}(P^{\mathrm{brdf}}).
\]

Ideal projection：

\[
P_\lambda(S)
=
\operatorname*{arg\,min}_{Y\in\mathcal{S}_{\mathrm{adm}}(\lambda)}
d_{\mathcal{S}}(S,Y)
+\eta_o d_{\mathrm{obs}}(\mathcal{O}(S),\mathcal{O}(Y))
+\eta_m d_{\mathrm{mat}}(M_S,M_Y).
\]

当前实现中的 largest component pruning、attachment-aware component selection、mesh export、re-encode、texture export QA 是该 projection 的可运行近似。建议在论文中把实现写成

\[
\widetilde P_\lambda
=
E_\theta\circ
\operatorname{ComponentProject}_{\lambda}\circ
D_\theta,
\]

并说明它是 ideal projection 的近似，而不是全局最优解。

### 6.1 Per-depth invariant proposition

设 \(e(S)\) 是 bad fragment/material/renderability 综合错误。若对所有 candidate \(X\)：

\[
e(P_\lambda(X))\le\epsilon_P,
\]

且 codec roundtrip 满足

\[
e(E_\theta(D_\theta(S)))\le e(S)+\epsilon_E,
\]

则 per-depth projected recursion 满足

\[
e(S_d)\le \epsilon_P+\epsilon_E,\qquad d=1,\ldots,D.
\]

证明草稿：由递归公式

\[
S_{d+1}=E_\theta(P_\lambda(X_d))
\]

直接得到

\[
e(S_{d+1})
\le e(P_\lambda(X_d))+\epsilon_E
\le \epsilon_P+\epsilon_E.
\]

Final-only cleanup 不提供这个 invariant，因为错误 fragment 可在 \(d<D\) 时参与 frontier、scheduler、sampler、history 和 cache 更新。注意这不是证明 final-only 一定失败；只是证明它缺少每层状态保证。

## 7. 传统方法包含性命题与证明草稿

这里的“包含”只指可表达性：存在 PS-SLG 的退化或受限实例，使其有限步状态转移等于或近似等于经典系统。不表示视觉质量或性能优越。

### 命题 1：IFS 覆盖

经典 IFS 在紧致空间 \(X\) 上由映射 \(f_i:X\rightarrow X\) 给出：

\[
A_{k+1}=\bigcup_{i=1}^m f_i(A_k).
\]

构造 PS-SLG：\(\Sigma=\{A\}\)，\(\mathcal{T}=\{f_i\}\)，禁用 sampler/projection/cache，即

\[
\mathcal{N}_{\theta}^{s}=\mathcal{N}_{\theta}^{m}=P_\lambda=\mathcal{C}=\operatorname{Id}.
\]

唯一规则：

\[
A\Rightarrow \{(A,f_i,\Omega,\rho_i,\mathbf{1},1,\top,\zeta_i,0,\emptyset,\emptyset)\}_{i=1}^m.
\]

Merge 为集合并，则

\[
C_{d+1}=\bigcup_{i=1}^{m}f_i(C_d).
\]

证明草稿：proposal 产生所有 \(f_i(C_d)\)，identity operators 不改变候选，merge 为 union，因此逐层等于 Hutchinson iteration。离散实现得到 \(Q_h(f_i(C_d))\) 的量化 IFS。

### 命题 2：L-system 覆盖

确定性上下文无关 L-system：

\[
\mathcal{L}=(V,\omega_0,\{a\mapsto w_a\}_{a\in V}),
\qquad
\omega_{d+1}=\mathcal{L}(\omega_d).
\]

构造 PS-SLG：令 \(U_d\in\Sigma^\star\)，scheduler 同步重写，merge 执行稳定拼接。对每个 \(a\in V\) 设置规则

\[
a\Rightarrow w_a.
\]

若

\[
\omega_d=a_1a_2\cdots a_n,
\]

则

\[
U_{d+1}=(w_{a_1},w_{a_2},\ldots,w_{a_n}),
\qquad
\pi_\Sigma(U_{d+1})=\mathcal{L}(\omega_d).
\]

证明草稿：对深度归纳。turtle/frame interpretation 是 \(\mathcal{I}\) 的一个选择；符号重写等价不依赖具体渲染。

### 命题 3：Space colonization 覆盖

设 tip 集合 \(B_d=\{b_i\}\)，attractor 集合 \(\Gamma_d\)。经典一步分配：

\[
\mathcal{A}(b_i)
=
\{a\in\Gamma_d:\ i=\operatorname*{arg\,min}_j\|a-b_j\|\}.
\]

方向：

\[
v_i=
\frac{
\sum_{a\in\mathcal{A}(b_i)}
(a-b_i)/(\|a-b_i\|+\epsilon)
}{
\left\|
\sum_{a\in\mathcal{A}(b_i)}
(a-b_i)/(\|a-b_i\|+\epsilon)
\right\|+\epsilon
}.
\]

新 tip：

\[
b_i'=b_i+\delta v_i.
\]

构造 PS-SLG：tip symbols 存在于 \(U_d\)，attractor field 存在于 \(A_d\)，proposal kernel \(\rho_{\mathrm{sc}}\) 执行同一最近分配和方向平均；occupancy exclusion 作为 \(\Pi\)；禁用 sampler/projection。则 tip/attractor 更新与经典算法一致。

证明草稿：逐项对齐分配、方向、步长、kill radius 和 branch graph merge。由于所有 learned components 为 identity，有限步转移一致。

### 命题 4：DLA / frontier accretion 覆盖

离散 DLA 定义 cluster \(C_d\subset\mathbf{Z}^3\) 和 hitting distribution：

\[
c_{\mathrm{new}}\sim p_{\mathrm{hit}}(\cdot\mid C_d),
\qquad
C_{d+1}=C_d\cup\{c_{\mathrm{new}}\}.
\]

构造 PS-SLG：frontier symbols 表示 \(\partial C_d\)，proposal kernel \(\rho_{\mathrm{dla}}\) 采样 \(p_{\mathrm{hit}}\)，merge 为 union，constraints 要求新点邻接 cluster。则

\[
\Pr(C_{d+1}=C_d\cup\{c\}\mid C_d)=p_{\mathrm{hit}}(c\mid C_d).
\]

证明草稿：PS-SLG 一层 Markov kernel 与 DLA Markov kernel 相同；有限步分布相同。若使用近似 frontier sampler，则得到 DLA-like accretion，而非严格 DLA。

### 命题 5：有限 shape grammar / CGA 子类覆盖

考虑有限 scope 的 shape grammar，其规则只读写有限 symbol neighborhood，并执行 split、extrude、repeat、replace、transform-copy。令每个 face/tile/portal 是 typed symbol，local region 是 \(\Omega_i\)，几何操作写入 \(\mathcal{T}\) 和 \(\mathcal{I}\)。禁用 learned sampler/projection 后，PS-SLG 的 symbol graph transition 与该有限 grammar 一致。

证明草稿：每条 shape grammar rule 逐一映射为 PS-SLG rule。Scheduler 按相同顺序或同步策略应用；interpretation map 输出相同 geometry/support；merge 是规则指定的 replacement/union。全局属性 grammar 或无限约束 grammar 不在该命题范围内。

### 命题 6：Symmetry / crystal transform-copy 覆盖与 equivariance

设有限群或晶格作用 \(G\curvearrowright\mathcal{S}\)。如果规则集满足闭包

\[
\forall g\in G,\ \forall r\in\mathcal{R},
\qquad
g\circ r\circ g^{-1}\in\mathcal{R},
\]

并且 scheduler 选择完整 orbit，则 transform-copy 程序生成 \(G\)-closed support：

\[
C_{d+1}=C_d\cup \bigcup_{g\in G}g\widehat C.
\]

Exact equivariance 还需要

\[
\mathbb{T}(gS)=g\mathbb{T}(S).
\]

这要求 merge、sampler、projection、codec、quantization 与 \(g\) 全部交换。实际系统只能给 approximate bound：

\[
d_{\mathcal{S}}(\mathbb{T}(gS),g\mathbb{T}(S))
\le
L_{\mathrm{post}}
(\epsilon_{\mathrm{rule}}+\epsilon_{\mathrm{merge}}
+\epsilon_{\mathrm{sampler}}+\epsilon_{\mathrm{proj}}
+\epsilon_{\mathrm{codec}}+\epsilon_{\mathrm{grid}}).
\]

证明草稿：把递归转移分解为 operator composition，逐个使用近似交换误差，再用 Lipschitz bound 累加。当前论文可把它作为 metric/proposition，不应宣称严格 equivariance。

## 8. 有限递归、无限递归与缓存语义

当前主任务：

\[
D<\infty,\qquad |C_d|\le T_{\max}(d).
\]

这对应 finite-depth recursive asset。无限递归有三种可写形式。

### 8.1 Contractive limit

若 transform \(f_i\) 是 contractions，存在 \(\alpha<1\) 使

\[
d(f_i(x),f_i(y))\le \alpha d(x,y),
\]

则 IFS 有 Hutchinson limit \(A^\star\)。在 PS-SLG 中，如果 sampler/projection 也满足非扩张或 bounded perturbation，可讨论近似极限：

\[
d_H(C_d,A^\star)\le \alpha^d d_H(C_0,A^\star)+O(\epsilon_P+\epsilon_E+\epsilon_{\mathrm{grid}}).
\]

这只能用于 contractive 子类，不适用于任意递归资产。

### 8.2 Visible-window recursion

定义相机或用户关注窗口 \(W_t\)，只展开窗口内 active support：

\[
C_t^{\mathrm{active}}=\bigcup_{\Omega\in W_t} C_{\Omega,t},
\qquad
\sum_{\Omega\in W_t}|C_{\Omega,t}|\le T_{\max}.
\]

窗口外区域由 descriptors/cache 表示：

\[
S_t=(C_t^{\mathrm{active}},K_t^{\mathrm{window}},K_t^{\mathrm{LOD}}).
\]

命题：若每个窗口最多激活 \(B\) 个 cache entries，且每 entry token 数不超过 \(T_b\)，则 active token budget 有界：

\[
|C_t^{\mathrm{active}}|\le BT_b.
\]

### 8.3 LOD/cache streaming

递归 symbol 可转为 cache descriptor：

\[
u=(\sigma,T,\ell,\operatorname{cache\_id},\operatorname{lod},\operatorname{validity}).
\]

只有当 descriptor 进入可见窗口或需要局部编辑时才 decode：

\[
(C_\Omega,F_\Omega,M_\Omega)=
\operatorname{MaterializedDecode}(K,\operatorname{cache\_id},T,\operatorname{lod}).
\]

这支持 infinite logical recursion 的有限展开，但不是无限 mesh 输出。

## 9. 与当前实现的对应

当前代码/实验可对应到以下 formal components：

- `trellis2_recursive_slat_grammar_workflow.py`：mesh-to-SLAT encoding、transform-copy/competition/radial/portal/scale/attached fork proposals、decoder、token budget。
- `trellis2_recursive_slat_flow_repair.py`：shape flow sampler 作为 repair/naturalization，但负结果提示必须 masked/local。
- projection ablation：\(\widetilde P_\lambda\) 的 per-depth vs final-only 证据。
- texture export summary：最终 geometry 后运行 texture-SLAT/PBR export，证明 compatibility，但不应夸大为 fully recursive material propagation。
- cache/LOD prototype manifest：对应 \(K_d^{\mathrm{motif}},K_d^{\mathrm{transform}},K_d^{\mathrm{LOD}},K_d^{\mathrm{window}}\) 的工程入口。

## 10. 可写进 SIGA Method 的组织方案

建议 Method 顺序：

1. **Problem setting**：finite-depth recursive 3D asset generation with a frozen native 3D generator。
2. **State**：定义 \(S_d=(C,F,U,A,B,M,H,K)\)，强调 structure ownership 和 material state。
3. **Grammar**：定义 \(\mathcal{G}\)、rule schema、scheduler、proposal kernels。
4. **Operational semantics**：放中心公式 \(Prop\rightarrow Merge\rightarrow Constraints\rightarrow Naturalization\rightarrow Decode\rightarrow Project\rightarrow Encode\rightarrow Cache\)。
5. **Classical systems as limits**：用短表覆盖 IFS、L-system、space colonization、DLA、shape grammar、symmetry。
6. **Masked generative naturalization**：说明 flow/SDE sampler 是 local prior，给 mask clamp 公式。
7. **Projection-stabilized recursion**：admissible set、projection objective、per-depth invariant proposition。
8. **Material and cache semantics**：texture/PBR state、final export vs future per-depth material recursion、bounded visible-window/cache。
9. **Limitations**：finite-depth only；exact equivariance and topology-preserving flow are not claimed。

主文建议只放 1 个 proposition：

> Under bounded projection and codec errors, per-depth projection bounds bad state mass at every recursive depth, whereas final-only projection lacks such an invariant.

附录建议放：

- IFS/L-system/space-colonization/DLA/shape grammar 覆盖证明；
- approximate equivariance bound；
- visible-window/cache active-token bound；
- material state extension。

## 11. 一段可直接改写进论文的中文摘要

PS-SLG 把递归 3D 资产表示为冻结 native 3D generator 的 typed sparse latent state。语法规则在该状态上提出 transform-copy、attractor/frontier growth、DLA accretion、portal/symmetry 和 cache reuse 等候选；候选先经过 mask merge、空间竞争和约束，再由冻结 flow/SDE sampler 在局部区域自然化，随后 decode 成 mesh/material asset，投影到 admissible recursive asset set，re-encode 回 sparse latent state 并更新缓存。传统 IFS、L-system、space colonization、DLA 和有限 shape grammar 都是该系统禁用 learned sampler/projection 后的退化实例。核心稳定机制是 per-depth projection：错误几何在成为下一层 frontier、history 或 cache 之前被压制。当前实现应主张 finite-depth recursive asset generation；无限递归、严格 equivariance 和 per-depth material recursion 是有明确语义但尚需更多实验证据的扩展方向。
