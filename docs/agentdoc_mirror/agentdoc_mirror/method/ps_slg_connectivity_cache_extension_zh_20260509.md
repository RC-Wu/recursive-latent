# PS-SLG/PS-RSLG 的 connectivity-first cache extension（中文方法草稿）

创建时间：2026-05-09  
范围：方法理论 / paper-method draft；不修改 `paper_siga/main.tex`。  
核心修正：在 texture/PBR 质量已经可以接受为兼容性证据之后，当前真正没有解决好的问题是 **fragmented chunks**。本草稿把连通性从 projection 后处理指标提升为 grammar invariant，并把它连接到 Trellis sparse representation、cache fusion 与 sampler/SDE schedule。

## 0. 论文本节的 claim 边界

本文可以安全主张三层内容。

**已经有实现证据的内容。** 当前代码和已有表格支持“per-depth projection 比 direct recursion / final-only cleanup 更能抑制 conservative competition case 的 component explosion”。`vine_compete_d3` 和 `tree_compete_d3` 中，per-depth projection 的 kept components 和 largest ratio 明显优于 direct raw state；`compete_fork` 仍碎片化，必须写成稳定性与表达性的边界。`cache_sampler_connectivity_20260509.py` 也提供了本地 occupancy proxy 诊断：cache/predecode bridge fusion、LOD fusion、sliding-window fusion 与 masked local sampler schedule 在若干 hard/control case 上能减少 component count 或保持 largest component ratio，但这仍是 voxel/occupancy proxy，不是真 Trellis decode 的强贡献证明。

**正式方法提案。** PS-SLG/PS-RSLG 应定义 connected sparse support invariant、admissible state set、bridge-aware projection、occupancy competition / exclusion / attachment energy、cache fusion 与 hard connectivity mask 下的 local naturalization。它们是方法框架的一部分，可以写成 SIGGRAPH-style method section，因为公式明确、实现路径清楚，并且与当前 failure mode 对齐。

**推测性扩展。** 严格 symmetry/crystal equivariance、无界 sliding-window recursion、sampler/SDE 保证拓扑保持、material cache 的 per-depth PBR 一致性，目前只能写成 extension 或 future experiment。不能写成已经解决。

## 1. Connectivity-first 问题重述

原始 PS-SLG 状态为

\[
S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d,K_d),
\]

其中 \(C_d\subset \{0\}\times h\mathbb{Z}^3\) 是 Trellis/O-Voxel/SLAT 风格的 active sparse support，\(F_d\) 是 shape/material/grammar feature。旧框架把 projection 写成把 candidate 拉回 admissible set：

\[
S_{d+1}
=
\mathcal C_{d+1}\circ \mathcal E_\theta\circ
\mathcal P_{\lambda_d}\circ \mathcal D_\theta\circ
\mathcal N_\theta\circ \Theta_{\Pi_d}\circ
\operatorname{Merge}_{B_d}\circ
\operatorname{Prop}_{R_d^\star}(S_d).
\]

这仍然不够，因为碎片不是最终 mesh 上的美观问题，而是递归状态错误。一个漂浮 chunk 会在下一层被误认为合法 frontier、anchor、motif source 或 sampler condition，并写入 cache。于是核心 invariant 应从“最后 renderable”改为：

\[
\boxed{\quad S_d\in \mathcal S_{\mathrm{conn}}(\lambda_d)\quad
\text{for every recursive depth } d.\quad}
\]

即每一层的 sparse state 都必须是 connected recursive state，而不是等最后再删 floating islands。

## 2. Connected sparse support invariant

### 2.1 Sparse adjacency graph

给定 active support \(C\subset h\mathbb Z^3\)，定义 \(\eta\)-邻接图

\[
G_\eta(C)=(C,E_\eta),\qquad
(p,q)\in E_\eta \Longleftrightarrow
\|p-q\|_1\le \eta h
\]

或在实现中使用 6-neighborhood / 18-neighborhood / 26-neighborhood。论文主指标建议使用 6-neighborhood occupancy proxy，因为它比 raw face connectivity 更稳定，也不会惩罚不共享顶点的 tube/GLB 导出。

令 \(R_d\subset C_d\) 是 root/anchor support，通常由 root mesh、trunk、stem、main scaffold 或 explicit attachment anchors 给出。令 \(\operatorname{Comp}_\eta(C_d)=\{Q_k\}\) 为 connected components。定义 attached component：

\[
Q_k\ \text{attached}
\quad\Longleftrightarrow\quad
\exists r\in R_d,\ \exists q\in Q_k:
\operatorname{dist}_{G_\eta(C_d)}(r,q)<\infty.
\]

如果 \(G_\eta(C_d)\) 不连通，仍可允许尚未 materialize 的 symbolic/LOD descriptor，但每个 materialized sparse chunk 必须有 explicit parent attachment record：

\[
\operatorname{parent}(Q_k)\in U_d,\qquad
\operatorname{anchor}(Q_k)\in C_d,\qquad
\operatorname{bridge\_budget}(Q_k)>0.
\]

否则它不是 “waiting-to-connect motif”，而是 orphan fragment。

### 2.2 Grammar ownership and attachment graph

每个 symbol \(u_i=(\sigma_i,\ell_i,T_i,\Omega_i,\alpha_i,\nu_i)\) 管辖 support \(\Omega_i\subseteq C_d\)。定义 symbol attachment graph

\[
\mathcal A_d=(U_d,E_d^{\mathrm{att}}),\qquad
(u_i,u_j)\in E_d^{\mathrm{att}}
\Longleftrightarrow
\operatorname{dist}_\eta(\Omega_i,\Omega_j)\le \delta_a
\ \text{or}\ 
\exists e_{ij}^{\mathrm{semantic}}.
\]

connectedness 不是只看 voxel 是否相邻，也要求 symbol graph 不出现孤立可繁殖节点：

\[
\forall u_i\in U_d,\quad
\operatorname{path}_{\mathcal A_d}(u_{\mathrm{root}},u_i)
\ \text{exists}
\quad\text{or}\quad
u_i\in U_d^{\mathrm{latent\ descriptor}}.
\]

这里 \(U_d^{\mathrm{latent\ descriptor}}\) 表示未展开的 cache/LOD/window descriptor；它不允许作为下一层 visible frontier，除非先 materialize 并通过 bridge-aware projection。

### 2.3 Admissible connected state set

定义 largest attached support

\[
C_{\mathrm{att}}(S_d)
=
\bigcup_{Q_k\in\operatorname{Comp}_\eta(C_d):Q_k\ \mathrm{attached}}Q_k.
\]

连通 violation 可写为

\[
V_{\mathrm{conn}}(S_d)
=
1-
\frac{\operatorname{mass}(C_{\mathrm{att}}(S_d))}
{\operatorname{mass}(C_d)+\epsilon}.
\]

更严格地，加入 orphan symbol、attachment gap、bad frontier 与 material seam：

\[
\begin{aligned}
V_{\mathrm{orphan}}(S)
&=\sum_{Q_k\not\leadsto R}\operatorname{mass}(Q_k),\\
V_{\mathrm{gap}}(S)
&=\sum_{(u_i,u_j)\in E^{\mathrm{att}}}
\max(0,\operatorname{dist}_\eta(\Omega_i,\Omega_j)-\delta_a),\\
V_{\mathrm{frontier}}(S)
&=\sum_{f\in\mathcal F(S)}
\mathbf 1[f\not\leadsto R],\\
V_{\mathrm{mat\_seam}}(S)
&=\sum_{(p,q)\in E_\eta(C)}
\|P^{\mathrm{brdf}}(p)-P^{\mathrm{brdf}}(q)\|_{\Sigma_m}^{2}.
\end{aligned}
\]

Connectivity-first admissible set:

\[
\boxed{
\begin{aligned}
\mathcal S_{\mathrm{conn}}(\lambda)=
\{S:\;&
V_{\mathrm{conn}}(S)\le \epsilon_c,\;
V_{\mathrm{orphan}}(S)\le \epsilon_o,\;
V_{\mathrm{gap}}(S)\le \epsilon_a,\;
V_{\mathrm{frontier}}(S)=0,\\
&
V_{\mathrm{occ}}(S)\le \epsilon_{\mathrm{occ}},\;
V_{\mathrm{sym}}(S)\le \epsilon_g,\;
V_{\mathrm{mat\_seam}}(S)\le \epsilon_m,\;
|C(S)|\le T_{\max}
\}.
\end{aligned}}
\]

这里 \(V_{\mathrm{frontier}}=0\) 是关键：即使 mesh 上有小碎片可以被最后删除，也不能让 orphan frontier 进入下一步 rule scheduler。

## 3. Bridge-aware projection，而不是 prune-only projection

### 3.1 Prune-only projection 的局限

现有 projection/pruning 可抽象为

\[
\mathcal P_{\mathrm{prune}}(X)
=
\operatorname*{arg\,min}_{Y\subseteq X,\ Y\in\mathcal S_{\mathrm{conn}}}
d_{\mathcal S}(X,Y)
+\lambda_{\mathrm{del}}\operatorname{mass}(X\setminus Y).
\]

它能删除 floating chunks，但会带来两个问题。第一，表达性强的 fork/DLA/radial/crystal proposal 可能本来需要细桥、根系、晶格连接或 symmetry orbit closure；直接删掉会把结构变成保守主干。第二，如果只做最终 pruning，中间层孤岛已经影响了 frontier、sampler condition、history 和 cache，删掉几何残余也无法撤销递归污染。

### 3.2 Bridge-aware projection

更合适的 projection 允许在小预算内添加 bridge support：

\[
Y=(X\setminus R)\cup B,\qquad
B=\bigcup_\ell \gamma_\ell,
\]

其中 \(R\) 是要删的 orphan/noisy support，\(\gamma_\ell\) 是连接 component 到 attached scaffold 的离散路径。路径集合来自候选集

\[
\Gamma(Q,R_d)=
\{\gamma=(q_0,\ldots,q_T):
q_0\in Q,\ q_T\in C_{\mathrm{att}},\
q_{t+1}-q_t\in\mathcal N_\eta\}.
\]

Bridge-aware projection：

\[
\boxed{
\begin{aligned}
\mathcal P_{\mathrm{bridge}}(X)
=
\operatorname*{arg\,min}_{Y\in\mathcal S_{\mathrm{conn}}}
&\ d_{\mathcal S}(X,Y)
+\eta_{\mathrm{obs}}d_{\mathrm{obs}}(\mathcal O(X),\mathcal O(Y))
+\eta_m d_{\mathrm{mat}}(M_X,M_Y)\\
&+\lambda_{\mathrm{del}}\operatorname{mass}(R)
+\lambda_{\mathrm{br}}\sum_{\gamma\subset B}\operatorname{len}(\gamma)
+\lambda_{\kappa}\sum_{\gamma\subset B}\operatorname{curv}(\gamma)\\
&+\lambda_{\mathrm{rad}}\sum_{\gamma\subset B}
\|\operatorname{radius}(\gamma)-\operatorname{radius}_{\mathrm{parent}}\|^2
+\lambda_{\mathrm{sym}}V_{\mathrm{sym}}(Y).
\end{aligned}}
\]

Prune-only 是该算子的退化情形：

\[
\lambda_{\mathrm{br}}\rightarrow\infty
\quad\Rightarrow\quad
\mathcal P_{\mathrm{bridge}}\approx \mathcal P_{\mathrm{prune}}.
\]

实现上可用三种近似：occupancy shortest path / geodesic bridge、morphological close、或 cache motif bridge。当前本地 smoke 中 `bridge_components`、`close_gaps`、`masked_local_sampler_boundary_schedule` 属于 occupancy-level 近似；论文不能把它写成已经完成的 Trellis latent bridge optimizer。

### 3.3 Bridge feature/material assignment

bridge 不能只补坐标，还要补 latent/material。对 \(b\in B\)，令端点为 \(a_0,a_1\)，定义

\[
F_Y(b)=
\omega_0(b)F_X(a_0)+\omega_1(b)F_X(a_1)
+\omega_\theta(b)\,\widehat F_\theta(b\mid \gamma,Y^m),
\]

\[
P_Y^{\mathrm{brdf}}(b)=
\operatorname{ProjectPBR}\left(
\omega_0P_X^{\mathrm{brdf}}(a_0)+
\omega_1P_X^{\mathrm{brdf}}(a_1)
+\omega_\theta \widehat P_\theta^{\mathrm{brdf}}(b)
\right).
\]

当前实现证据主要是 geometry/occupancy；per-depth material bridge 是正式提案，不是已完成结果。

## 4. Occupancy competition / exclusion / attachment energy

候选 action 写成

\[
a=(c,\Delta F,\Delta M,u_{\mathrm{parent}},\rho,\mu,\tau),
\]

其中 \(c\in h\mathbb Z^3\) 是候选坐标，\(\Delta F,\Delta M\) 是 shape/material update，\(u_{\mathrm{parent}}\) 是父 symbol，\(\rho\) 是 proposal kernel，\(\mu\) 是 mask，\(\tau\) 是 sampler schedule。

定义候选能量：

\[
\begin{aligned}
E(a;S_d)=&
\lambda_{\mathrm{occ}}\,O_d(c)
+\lambda_{\mathrm{excl}}\sum_{q\in C_d}
\mathbf 1[\|c-q\|_\infty<r_{\mathrm{excl}}]\,
\mathbf 1[\operatorname{owner}(q)\ne u_{\mathrm{parent}}]\\
&+\lambda_{\mathrm{col}}\phi_{\mathrm{collision}}(a,S_d)
+\lambda_{\mathrm{budget}}\max(0,|C_d|+|\Delta C_a|-T_{\max})\\
&-\lambda_{\mathrm{att}}\exp\!\left(
-\frac{\operatorname{dist}(c,C_{\mathrm{att}})^2}{2\sigma_a^2}
\right)
-\lambda_{\mathrm{front}}\phi_{\mathrm{frontier}}(c,\mathcal F_d)\\
&+\lambda_{\mathrm{gap}}\operatorname{dist}(c,C_{\mathrm{att}})
+\lambda_{\mathrm{orphan}}\mathbf 1[\operatorname{path}(c,R_d)=\varnothing]\\
&+\lambda_{\mathrm{mat}}\phi_{\mathrm{mat\_seam}}(\Delta M,M_d)
+\lambda_{\mathrm{sym}}\phi_{\mathrm{orbit}}(a,G_d).
\end{aligned}
\]

采纳概率或 priority 可写为

\[
\Pr(a\mid S_d)\propto
\exp(-E(a;S_d)/T_d),
\]

并加 hard feasibility：

\[
a\in\mathcal A_{\mathrm{hard}}(S_d)
\Longleftrightarrow
O_d(c)=0,\quad
\operatorname{dist}(c,C_{\mathrm{att}})\le r_{\max},\quad
\exists \gamma(c,C_{\mathrm{att}})\ \text{with}\ \operatorname{cost}(\gamma)\le b_d.
\]

这把“看起来合理的生长方向”改为“必须可连接的生长方向”。DLA/random frontier/radial/crystal proposals 只有在能连接回 attached scaffold 时才允许成为 active sparse support。

## 5. Cache fusion：复用 coherent connected motifs，而不是累积独立碎片

原框架已经有

\[
K_d=(K^{\mathrm{motif}},K^{\mathrm{latent}},K^{\mathrm{transform}},
K^{\mathrm{LOD}},K^{\mathrm{window}},K^{\mathrm{sampler}},K^{\mathrm{material}}).
\]

Connectivity-first 的关键是 cache entry 必须携带连接 contract：

\[
k=
(\operatorname{id},C_k,F_k,M_k,T_k,\ell_k,
A_k^{\mathrm{in}},A_k^{\mathrm{out}},
\Gamma_k^{\mathrm{bridge}},
\operatorname{conn\_cert}_k,
\operatorname{lod\_err}_k,
\operatorname{validity}_k).
\]

其中 \(A_k^{\mathrm{in}}\) 是 motif 的接入 anchor，\(A_k^{\mathrm{out}}\) 是后续可生长 frontier，\(\Gamma_k^{\mathrm{bridge}}\) 是预计算 bridge template，\(\operatorname{conn\_cert}_k\) 证明或近似记录：

\[
V_{\mathrm{conn}}(k)\le \epsilon_c,\qquad
\forall a\in A_k^{\mathrm{out}},\ a\leadsto A_k^{\mathrm{in}}.
\]

Cache lookup 不是独立复制 chunk，而是 attached lookup：

\[
\operatorname{Lookup}_{\mathrm{conn}}(K_d,k,T,a_{\mathrm{host}})
=
\operatorname{Attach}\bigl(T(C_k,F_k,M_k),a_{\mathrm{host}},A_k^{\mathrm{in}}\bigr)
\cup \Gamma_k^{\mathrm{bridge}}.
\]

### 5.1 Motif / latent cache

motif cache 存储已经通过 projection 的 connected motif。latent cache 存储 \((C,F,M)\) blocks，但只有当 transform 后 anchor 能落在 host attached support 上时才可复用：

\[
\operatorname{dist}_\eta(TA_k^{\mathrm{in}},C_{\mathrm{att}})\le \delta_a.
\]

这避免每次 transform-copy 都把 motif 当作新 independent island。

### 5.2 Transform cache

transform cache 记录 \((T,C,F,M)\) 的量化结果和连接证书：

\[
K^{\mathrm{transform}}[k,T]
=
(Q_h(TC_k),T_\#F_k,T_\#M_k,
Q_h(TA_k^{\mathrm{in}}),\operatorname{conn\_cert}).
\]

对于 radial symmetry，如果复制 \(n\) 个 orbit 元素，cache 必须存储 orbit closure 和 hub/ring bridge，而不是 \(n\) 个互不相干的 rotated chunks。

### 5.3 LOD cache

LOD cache 的正确用途是把远处或小尺度递归折叠为 connected descriptor：

\[
k_{\mathrm{LOD}}=(\operatorname{id},T,\ell,
\widetilde C,\widetilde F,\widetilde M,
\epsilon_{\mathrm{geom}},\epsilon_{\mathrm{conn}},A^{\mathrm{in}},A^{\mathrm{out}}).
\]

active state 只保留窗口内高分辨率 support：

\[
C_t^{\mathrm{active}}=\bigcup_{\Omega\in W_t} C_{\Omega,t},
\qquad
\sum_{\Omega\in W_t}|C_{\Omega,t}|\le T_{\max},
\]

窗口外只能作为 descriptor 参与 bounds 和 rendering，不能作为 active frontier 继续繁殖。无界递归/zoom 的主张应保持为 speculative extension。

### 5.4 Sliding-window cache

sliding-window fusion 应在窗口边界强制 overlap connectivity：

\[
\operatorname{Overlap}(W_i,W_j)
=C_{W_i}\cap C_{W_j},\qquad
\operatorname{mass}(\operatorname{Overlap})\ge m_{\min}
\]

或要求存在 cross-window bridge：

\[
\exists \gamma_{ij}: A_{W_i}^{\mathrm{out}}\leadsto A_{W_j}^{\mathrm{in}},
\qquad
\operatorname{cost}(\gamma_{ij})\le b_{\mathrm{win}}.
\]

否则窗口级 cache 会稳定地产生 tile seams 和独立 chunks。

## 6. Sampler/SDE schedule：hard connectivity mask 下的 local naturalization

冻结 Trellis sampler/SDE 不应拥有全局拓扑。设局部 latent state 为 \(Z_t=(C_t,F_t,M_t)\)，proposal 区域为 \(\Omega_d\)，hard connected anchor 为 \(C_{\mathrm{att}}\)。SDE 写成

\[
dZ_t=f_\theta(Z_t,t,y,\Omega_d)\,dt+g(t)\,dW_t,\qquad t:\tau_d\rightarrow 0.
\]

Hard connectivity mask：

\[
\mu_{\mathrm{hard}}(c)=
\mathbf 1[c\in\Omega_d]\,
\mathbf 1[\operatorname{dist}(c,C_{\mathrm{att}})\le r_t]\,
\mathbf 1[\exists\gamma(c,C_{\mathrm{att}}):\operatorname{cost}(\gamma)\le b_t].
\]

Clamp update：

\[
Z_{t-\Delta t}\leftarrow
(1-\mu_{\mathrm{hard}})\odot Z_{\mathrm{anchor}}
+\mu_{\mathrm{hard}}\odot
\Phi_{\theta,t}(Z_t,y).
\]

同时 schedule \(r_t,b_t,T_t\) 从保守到局部自然化：

\[
r_t=r_{\min}+(r_{\max}-r_{\min})\alpha(t),
\qquad
b_t=b_{\min}+(b_{\max}-b_{\min})\alpha(t),
\qquad
T_t\downarrow 0.
\]

sample selection 也必须 projection-aware：

\[
s^\star=
\arg\min_{s\in\mathcal S_{\mathrm{samples}}}
E_{\mathrm{local}}(s)
+\lambda_c V_{\mathrm{conn}}(\mathcal P_{\mathrm{bridge}}(s))
+\lambda_r V_{\mathrm{render}}(s)
+\lambda_m V_{\mathrm{mat}}(s).
\]

当前项目已有 global/full repair 容易 wash out recursive topology 的负面经验。因此主文应写：sampler 是 **local naturalization prior under hard connectivity masks**，不是全局 repair，也不是拓扑保证器。

## 7. DLA / crystal / radial symmetry cases：为什么 naive frontier accretion 会碎片化

### 7.1 DLA / porous accretion

DLA-like rule 可写为

\[
c_{d+1}\sim H(\cdot\mid \partial C_d),\qquad
C_{d+1}=C_d\cup \{c_{d+1}\}.
\]

在连续 DLA 中粒子通过 hitting frontier 自然 attach；但在 sparse latent recursion 中，proposal 往往经过 transform、decode/re-encode、mesh quantization 和 sampler naturalization。若只保留“命中分布”而不保留 explicit bridge/path certificate，则 hit point 附近的 latent patch 可能变成多个 disconnected voxels 或 thin sheets。Connectivity-first DLA 应改为：

\[
c\sim H(\cdot\mid\partial C_{\mathrm{att}}),
\qquad
\gamma(c,C_{\mathrm{att}})\ \text{exists},
\qquad
C^+=C_d\cup\{c\}\cup\gamma.
\]

### 7.2 Crystal / lattice growth

Crystal/lattice rule 常写为

\[
C_{d+1}=C_d\cup \bigcup_{v\in\mathcal B} (C_d+v)
\]

或沿晶面 normal 扩张。naive transform-copy 的问题是每个 lattice translate 都可能单独落在相邻但不接触的 sparse cells 上，尤其在 quantization 或 decoder smoothing 后形成多组件。需要 lattice bridge/face contact invariant：

\[
\forall v\in\mathcal B,\quad
\operatorname{area}\bigl(\partial C_d\cap \partial(C_d+v)\bigr)\ge a_{\min}
\quad\text{or}\quad
\exists \gamma_v:(C_d+v)\leadsto C_{\mathrm{att}}.
\]

### 7.3 Radial symmetry / orbit expansion

Radial rule 可写为

\[
C^+=\bigcup_{g\in C_n} gC.
\]

如果 \(C\) 不包含 central hub 或 ring connector，orbit expansion 会把一个 motif 复制成 \(n\) 个相似但互不连接的 chunks。Connectivity-first radial rule 应加 orbit attachment：

\[
C^+=
\left(\bigcup_{g\in C_n}gC\right)
\cup C_{\mathrm{hub}}
\cup \bigcup_{g\in C_n}\gamma(gA^{\mathrm{in}},C_{\mathrm{hub}}).
\]

因此 radial/crystal 图像不能只报告 symmetry error，也要报告 occupancy component count、largest attached ratio 和 bridge survival ratio。

## 8. Safe metrics / safe claims / needed experiments

### 8.1 安全指标

主文建议使用以下指标，且每个指标都说明口径。

\[
\operatorname{LCR}_{\mathrm{occ}}
=
\frac{|C_{\mathrm{largest\ attached}}|}
{|C|+\epsilon},
\qquad
\operatorname{Frag}=1-\operatorname{LCR}_{\mathrm{occ}}.
\]

\[
\operatorname{Comp}_{6n}=|\operatorname{Comp}_{6n}(C)|,
\qquad
\operatorname{OrphanMass}=\sum_{Q_k\not\leadsto R}|Q_k|.
\]

\[
\operatorname{BridgeSurvival}
=
\frac{\#\{\gamma\ \text{present after decode/re-encode}\}}
{\#\{\gamma\ \text{inserted before decode}\}+\epsilon}.
\]

\[
\operatorname{ProjectionSurvival}
=
\frac{|C_{\mathrm{after\ projection}}|}
{|C_{\mathrm{before\ projection}}|+\epsilon}.
\]

\[
\operatorname{FrontierValidity}
=
\frac{\#\{f\in\mathcal F:f\leadsto R\}}
{|\mathcal F|+\epsilon}.
\]

对于传统 space colonization/L-system，仍应报告 skeleton coverage、tips、branch nodes、depth、total length。不能用 raw face components 贬低 tube baseline。

### 8.2 安全 claim

可以写：

- “We formalize connected sparse support as an invariant of recursive sparse-latent grammars.”
- “Per-depth projection provides a stronger recursive-state guarantee than final-only cleanup, because invalid fragments cannot become future frontiers or cache entries.”
- “Bridge-aware projection generalizes prune-only projection by allowing low-cost connector insertion under geometry/material/renderability constraints.”
- “Cache entries must carry attachment anchors and connectivity certificates; otherwise motif reuse degenerates into independent fragment accumulation.”
- “Masked local naturalization is used under hard connectivity masks; the sampler does not own global recursive topology.”
- “Existing conservative competition cases support the projection-stabilized connectivity story; expressive fork/DLA/radial/crystal cases remain stress tests.”

不应写：

- “Trellis sampler guarantees connected topology.”
- “Cache fusion is proven to solve fragmentation in true decoded assets.”
- “Radial/crystal symmetry is exact.”
- “Infinite recursive worlds are implemented.”
- “Texture/PBR quality is the main contribution.”

### 8.3 需要补的实验

最小充分实验表应包含同 root、同 depth、同 renderer、同 metric 的四列：

| Protocol | Direct recursion | Final-only projection | Prune-only per-depth | Bridge-aware per-depth |
|---|---:|---:|---:|---:|
| vine/tree conservative competition | required | required | required | required |
| fork expression stress | required | required | required | required |
| DLA/porous frontier | required | required | required | required |
| radial symmetry | required | required | required | required |
| crystal/lattice | required | required | required | required |

每列报告：

- per-depth \( \operatorname{Comp}_{6n} \)、\( \operatorname{LCR}_{\mathrm{occ}} \)、orphan mass；
- accepted proposal ratio、collision/exclusion rejection ratio；
- projection survival ratio、bridge survival ratio；
- frontier validity；
- optional textured GLB import success and material seam score。

最关键的 ablation 是：

\[
\mathcal P_{\mathrm{final}}
\quad\text{vs}\quad
\mathcal P_{\mathrm{prune-per-depth}}
\quad\text{vs}\quad
\mathcal P_{\mathrm{bridge-per-depth}}
\quad\text{vs}\quad
\mathcal P_{\mathrm{bridge+cache+masked-sampler}}.
\]

如果 bridge-aware projection 只在 occupancy proxy 上有效而 true Trellis decode 后不稳定，应诚实写成 diagnostic/future work；如果 true decode 后也保持 lower component count 和 higher attached LCR，才能升级为主贡献。

## 9. 可放入 SIGGRAPH-style method section 的压缩版核心段落

PS-RSLG 的 connectivity-first 版本把递归生成定义为在 connected sparse latent state 上的约束重写。每个深度 \(d\) 的状态 \(S_d\) 必须属于 \(\mathcal S_{\mathrm{conn}}(\lambda_d)\)，其中 active sparse support 通过 6-neighborhood occupancy graph 或显式 attachment graph 连接到 root anchors；任何未连接 chunk 都不能成为下一层 frontier、symbol owner 或 cache source。给定 rule proposals 后，系统先用 occupancy/exclusion/attachment energy 过滤候选，再用 bridge-aware projection 在删除 orphan fragments 与插入低成本 connector 之间优化，而不是只做 largest-component pruning。Projection 后的 mesh 被 re-encoded 回 Trellis sparse representation，cache 只记录带 attachment anchors 和 connectivity certificate 的 motifs/latents/transforms/LOD/window entries。Frozen sampler/SDE 只在 hard connectivity mask 内做 local naturalization，不能全局重采样 scaffold。这个设计把碎片控制从最终 mesh cleanup 提前到递归语义本身，也解释了为什么 DLA、crystal 和 radial frontier accretion 在 naive transform-copy 或 frontier hitting 下容易变成多个独立 chunks。
