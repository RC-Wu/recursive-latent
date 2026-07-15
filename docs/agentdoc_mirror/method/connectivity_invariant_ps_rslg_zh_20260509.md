# Connectivity-Invariant PS-RSLG 方法论补充

创建时间：2026-05-09  
项目：`recursive_3d_generative_growth`  
范围：方法论 / 论文 Method 补充；**不修改 `paper_siga/main.tex`**。  
核心命题：把 **连通性不变量（connectivity invariant）**、**可投影可达域（projectable reachable domain）**、**桥接-自然化-重编码（bridge-naturalize-reencode）** 定义为 PS-RSLG 的主体语义，而不是工程修补。

## 0. 一句话结论

当前系统不应被写成“recursive rule 先生成碎片，后面再 cleanup”。更强、更适合 SIGGRAPH Asia 的表述是：

> **Projection-Stabilized Recursive Sparse-Latent Grammar (PS-RSLG)** 在每个递归深度上维护一个 connected sparse latent state。语法规则只能提出位于可投影可达域内、或可通过低成本 bridge 投影回 attached scaffold 的候选；冻结 Trellis2 sampler 只在 hard connectivity mask 内做局部自然化；随后状态被 decode/project/re-encode，并且 cache 只记录带 attachment certificate 的 motif。连通性因此成为递归语法的不变量，而不是最终 mesh 的美观后处理。

这一定义直接解释了目前最严重的 failure mode：DLA、crystal、radial、非树结构和部分树结构会碎块化，不是因为纹理/PBR 不够，而是因为 naive frontier/transform-copy 在 sparse latent recursion 中没有强制每个 materialized chunk 都能回连到 root scaffold。

## 1. 从工程补丁到方法主体

旧叙事容易落入如下流水线：

\[
\text{root mesh}\rightarrow
\text{sparse latent rule proposal}\rightarrow
\text{decode}\rightarrow
\text{projection/pruning}\rightarrow
\text{texture export}.
\]

这种写法的问题是 projection 像一个后处理模块，cache 像一个加速技巧，sampler 像一个修图器。对当前项目而言，这个叙事无法解释最关键的现象：一个小 floating chunk 如果在第 \(d\) 层没有被阻止，它会在第 \(d+1\) 层成为合法 frontier、symbol owner、motif source 或 cache entry，进而把局部碎片扩散成递归污染。因此方法主体应改写为：

\[
\boxed{
\text{PS-RSLG is a recursive grammar over connected sparse latent states.}
}
\]

每一层状态必须满足：

\[
\boxed{
S_d\in \mathcal S_{\mathrm{conn}}(\lambda_d),\qquad d=0,\ldots,D.
}
\]

这里 \(\mathcal S_{\mathrm{conn}}\) 不是渲染前的清理目标，而是 grammar transition 的定义域和值域。换句话说，PS-RSLG 的每条规则都不是自由生成几何，而是在 connected-state manifold 上做受约束重写。

## 2. 状态空间

令连续空间为 \(X\subset\mathbb R^3\)，离散 sparse coordinate grid 为

\[
L_h=h\mathbb Z^3,\qquad \bar L_h=\{0\}\times L_h.
\]

第 \(d\) 层 recursive sparse latent state 定义为：

\[
\boxed{
S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d,K_d).
}
\]

各项含义如下。

\[
C_d\subset \bar L_h,\qquad |C_d|\le T_{\max}(d)
\]

是 Trellis/O-Voxel/SLAT 风格的 active sparse support。

\[
F_d:C_d\rightarrow
\mathbb R^{q_s}\times\mathbb R^{q_m}\times\mathbb R^{q_a}
\]

是 shape latent、material latent 和 grammar auxiliary feature。即使当前实验主要证明 shape/occupancy connectivity，论文公式也应保留 \(q_m\)，否则 PBR/material 只能被写成最后导出，而不是状态语义的一部分。

\[
U_d=\{u_i\}_{i=1}^{n_d},\qquad
u_i=(\sigma_i,\ell_i,T_i,\Omega_i,\alpha_i,\nu_i)
\]

是 typed symbols、递归层级、局部 frame、symbol ownership support、局部属性与 scheduler/cache metadata。为了覆盖标准 L-system，\(U_d\) 也可以是有序串或有序 symbol graph：

\[
U_d\in\Sigma^\star
\quad\text{or}\quad
U_d=(V_d,E_d,\operatorname{ord}_d,\sigma,T,\alpha).
\]

\[
A_d=(O_d,\Gamma_d,\mathcal F_d,\mathcal A_d,\mathcal Q_d,\mathcal G_d)
\]

是辅助场：occupancy/exclusion \(O_d\)、attractor/density field \(\Gamma_d\)、frontier set \(\mathcal F_d\)、attachment/component graph \(\mathcal A_d\)、quality diagnostics \(\mathcal Q_d\)、group/lattice/orbit metadata \(\mathcal G_d\)。

\[
B_d=(\partial C_d,\{\mu_k\},\{\omega_k\},\{\chi_k\})
\]

是 boundary、soft edit mask、blend kernel 与 hard clamp indicator。

\[
M_d=(F_d^m,P_d^{\mathrm{brdf}},Y_d^m,\tau_d^m,\mu_d^m,\kappa_d^m,\operatorname{atlas}_d)
\]

是 material/PBR state。当前可安全写成“final geometry 后的 compatible Trellis2 texture export 已有实现证据”；per-depth material bridge 和 material cache fusion 是方法定义与待验证扩展。

\[
H_d=(d,\xi_{0:d},R_{0:d},T_{0:d},\lambda_{0:d},\operatorname{diag}_{0:d})
\]

记录随机种子、已用规则、transform、projection 参数与诊断。

\[
K_d=(K^{\mathrm{motif}},K^{\mathrm{latent}},K^{\mathrm{transform}},
K^{\mathrm{LOD}},K^{\mathrm{window}},K^{\mathrm{sampler}},K^{\mathrm{material}})
\]

是 cache state。重要的是：cache 不是加速附录，而是递归语义的一部分，因为它决定哪些 motif 能被复用、哪些 frontier 能继续繁殖、哪些窗口外结构只保留为 LOD descriptor。

## 3. Grammar 对象与 production

定义 PS-RSLG grammar：

\[
\boxed{
\mathcal G=(\Sigma,\mathcal T,\mathcal R,\mathcal I,\Pi,
\mathcal P_{\mathrm{conn}},\mathcal N_\theta,K).
}
\]

其中：

- \(\Sigma\)：typed symbols，例如 `Root`、`Tip`、`Branch`、`Frontier`、`Attractor`、`CrystalFace`、`SymOrbit`、`Tile`、`Portal`、`LODChunk`。
- \(\mathcal T\)：transform semigroup/group，包括 translation、rotation、scale、mirror、portal、contraction、lattice vector、symmetry orbit action。
- \(\mathcal R\)：stochastic context-sensitive productions。
- \(\mathcal I\)：symbol 到 sparse support/features/material 的解释映射。
- \(\Pi\)：hard/soft constraints，包括 occupancy、attachment、symmetry、collision、budget、renderability。
- \(\mathcal P_{\mathrm{conn}}\)：connectivity-preserving projection operator。
- \(\mathcal N_\theta\)：冻结 Trellis2 flow/SDE/local naturalization sampler。
- \(K\)：motif/latent/transform/LOD/window/material caches。

一条 production 写成：

\[
\boxed{
r:\;
X_i(\mathrm{frame},\mathrm{scale},\mathrm{type},d,\alpha)
\rightarrow
\{(X_j,T_j,\mu_j,\rho_j,\kappa_j,\epsilon_j,\beta_j,\pi_j)\}_{j=1}^{m}.
}
\]

其中 \(T_j\) 是局部到全局 transform，\(\mu_j\) 是 edit mask，\(\rho_j\) 是 proposal kernel，\(\kappa_j\) 是 attachment/condition，\(\epsilon_j\) 是 noise/sampler seed，\(\beta_j\) 是 blend/material assignment，\(\pi_j\) 是 hard constraints。

该 production 的语义不是 copy-paste，而是：

\[
\boxed{
\operatorname{proposal}
\rightarrow
\operatorname{sparse\ merge}
\rightarrow
\operatorname{competition/exclusion}
\rightarrow
\operatorname{bridge\ projection}
\rightarrow
\operatorname{masked\ naturalization}
\rightarrow
\operatorname{decode/reencode}
\rightarrow
\operatorname{connected\ cache\ update}.
}
\]

写成算子组合：

\[
\boxed{
\begin{aligned}
X_{d+1}
&=
\Theta_{\Pi_d}
\circ
\operatorname{Merge}_{B_d}
\circ
\operatorname{Prop}_{R_d^\star}(S_d),\\
\widetilde S_{d+1}
&=
\mathcal P_{\mathrm{conn},\lambda_d}(X_{d+1};S_d),\\
\bar S_{d+1}
&=
\mathcal N_{\theta,\mu_{\mathrm{hard}}}^{\tau_d\rightarrow0}
(\widetilde S_{d+1}\mid S_d,y),\\
S_{d+1}
&=
\operatorname{UpdateCache}
\circ
\mathcal E_\theta
\circ
\operatorname{ProjectDecode}_\lambda
\circ
\mathcal D_\theta
(\bar S_{d+1}).
\end{aligned}
}
\]

这里 \(\mathcal D_\theta\) decode 到 mesh/observable geometry，\(\operatorname{ProjectDecode}_\lambda\) 在 mesh/occupancy/material proxy 上执行几何与连通性投影，\(\mathcal E_\theta\) re-encode 回 sparse latent state。若某实现只做 occupancy projection，也应在论文里明确它是 \(\operatorname{ProjectDecode}_\lambda\) 的 proxy，而不是完整 latent optimizer。

## 4. Connected support invariant

给定 active support \(C\subset L_h\)，定义 \(\eta\)-邻接图：

\[
G_\eta(C)=(C,E_\eta),\qquad
(p,q)\in E_\eta
\Longleftrightarrow
\|p-q\|_1\le \eta h.
\]

实际指标建议使用 6-neighborhood occupancy proxy；18/26-neighborhood 可作为补充。令 \(R_d\subset C_d\) 为 root anchors、主 trunk、scaffold 或 explicit attachment anchors。令

\[
\operatorname{Comp}_\eta(C_d)=\{Q_k\}
\]

为 connected components。attached support 定义为：

\[
C_{\mathrm{att}}(S_d)=
\bigcup_{Q_k:\;Q_k\leadsto R_d}Q_k.
\]

基础 connectivity violation：

\[
V_{\mathrm{conn}}(S_d)
=
1-
\frac{\operatorname{mass}(C_{\mathrm{att}}(S_d))}
{\operatorname{mass}(C_d)+\epsilon}.
\]

但只看 voxel 连通性不够，还要保证 symbol graph 不产生孤立可繁殖节点。定义 symbol attachment graph：

\[
\mathcal A_d=(U_d,E_d^{\mathrm{att}}),
\]

\[
(u_i,u_j)\in E_d^{\mathrm{att}}
\Longleftrightarrow
\operatorname{dist}_\eta(\Omega_i,\Omega_j)\le \delta_a
\quad\text{or}\quad
\exists e_{ij}^{\mathrm{semantic}}.
\]

可繁殖 symbol 的 invariant 为：

\[
\forall u_i\in U_d^{\mathrm{active}},
\qquad
\operatorname{path}_{\mathcal A_d}(u_{\mathrm{root}},u_i)
\ \text{exists}.
\]

未展开的 cache/LOD descriptor 可以暂时不 materialize，但它不能进入 active frontier：

\[
u_i\in U_d^{\mathrm{latent\ descriptor}}
\Rightarrow
u_i\notin \mathcal F_d^{\mathrm{active}}
\quad\text{until}\quad
\mathcal P_{\mathrm{conn}}(u_i)\ \text{succeeds}.
\]

最终 admissible connected state set：

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
\end{aligned}
}
\]

其中：

\[
V_{\mathrm{orphan}}(S)=\sum_{Q_k\not\leadsto R}\operatorname{mass}(Q_k),
\]

\[
V_{\mathrm{gap}}(S)=
\sum_{(u_i,u_j)\in E^{\mathrm{att}}}
\max(0,\operatorname{dist}_\eta(\Omega_i,\Omega_j)-\delta_a),
\]

\[
V_{\mathrm{frontier}}(S)=
\sum_{f\in\mathcal F(S)}\mathbf 1[f\not\leadsto R],
\]

\[
V_{\mathrm{mat\_seam}}(S)=
\sum_{(p,q)\in E_\eta(C)}
\|P^{\mathrm{brdf}}(p)-P^{\mathrm{brdf}}(q)\|_{\Sigma_m}^{2}.
\]

这里最关键的是 \(V_{\mathrm{frontier}}(S)=0\)：floating chunk 即使最后能被删掉，也不能被下一层语法当成 parent、frontier 或 cache source。

## 5. 可投影可达域

“可投影可达域”是把连通性放进 grammar 主体的关键概念。给定当前 attached scaffold \(C_{\mathrm{att}}\)、路径预算 \(b_d\)、最大 attachment 距离 \(r_d\)、障碍/排斥场 \(O_d\)，定义从候选点 \(c\) 到 scaffold 的最小 bridge cost：

\[
\operatorname{cost}_{\mathrm{br}}(c,C_{\mathrm{att}})
=
\min_{\gamma:c\leadsto C_{\mathrm{att}}}
\sum_{t}
\left[
w_\ell
+w_o O_d(\gamma_t)
+w_\kappa \kappa(\gamma_t,\gamma_{t+1})
+w_m \phi_{\mathrm{mat}}(\gamma_t)
\right].
\]

可投影可达域为：

\[
\boxed{
\mathcal R_{\mathrm{proj}}(S_d;b_d,r_d)
=
\left\{
c\in L_h:
\operatorname{dist}(c,C_{\mathrm{att}})\le r_d,\;
\operatorname{cost}_{\mathrm{br}}(c,C_{\mathrm{att}})\le b_d
\right\}.
}
\]

一个 materialized proposal \(\Delta C\) 只有满足以下条件之一，才可进入 active state：

\[
\Delta C\subset \mathcal R_{\mathrm{proj}}(S_d;b_d,r_d),
\]

或存在 bridge set \(B\) 使得

\[
\Delta C\cup B\in\mathcal S_{\mathrm{conn}}(\lambda_d),
\qquad
\operatorname{cost}(B)\le b_d.
\]

否则该 proposal 必须被拒绝、保留为 inactive latent descriptor，或在更大 LOD/window budget 下重新调度。这个定义把 DLA/crystal/radial 的问题说清楚：它们不是不能提出远端结构，而是远端结构必须携带可投影回主 scaffold 的证据。

## 6. Projection operator：bridge-aware，而不是 prune-only

Prune-only projection 是：

\[
\mathcal P_{\mathrm{prune}}(X)
=
\operatorname*{arg\,min}_{Y\subseteq X,\;Y\in\mathcal S_{\mathrm{conn}}}
d_{\mathcal S}(X,Y)
+\lambda_{\mathrm{del}}\operatorname{mass}(X\setminus Y).
\]

它能删除孤岛，但会牺牲 fork、DLA、crystal、radial symmetry 所需要的细桥、晶格边、中心 hub 或 ring connector。PS-RSLG 主体应使用 bridge-aware projection：

\[
Y=(X\setminus R)\cup B,
\qquad
B=\bigcup_\ell\gamma_\ell.
\]

其中 \(R\) 是被删除的 orphan/noisy support，\(\gamma_\ell\) 是把 component 接回 \(C_{\mathrm{att}}\) 的离散路径。候选路径集合：

\[
\Gamma(Q,C_{\mathrm{att}})
=
\{\gamma=(q_0,\ldots,q_T):
q_0\in Q,\;
q_T\in C_{\mathrm{att}},\;
q_{t+1}-q_t\in\mathcal N_\eta\}.
\]

投影优化：

\[
\boxed{
\begin{aligned}
\mathcal P_{\mathrm{conn}}(X;S_d)
=
\operatorname*{arg\,min}_{Y\in\mathcal S_{\mathrm{conn}}(\lambda_d)}
&
d_{\mathcal S}(X,Y)
+\eta_{\mathrm{obs}}d_{\mathrm{obs}}(\mathcal O(X),\mathcal O(Y))
+\eta_m d_{\mathrm{mat}}(M_X,M_Y)\\
&
+\lambda_{\mathrm{del}}\operatorname{mass}(R)
+\lambda_{\mathrm{br}}\sum_{\gamma\subset B}\operatorname{len}(\gamma)
+\lambda_{\kappa}\sum_{\gamma\subset B}\operatorname{curv}(\gamma)\\
&
+\lambda_{\mathrm{rad}}\sum_{\gamma\subset B}
\|\operatorname{radius}(\gamma)-\operatorname{radius}_{\mathrm{parent}}\|^2
+\lambda_{\mathrm{reach}}\mathbf 1[C(Y)\not\subset\mathcal R_{\mathrm{proj}}^{+}]\\
&
+\lambda_{\mathrm{sym}}V_{\mathrm{sym}}(Y)
+\lambda_{\mathrm{front}}V_{\mathrm{frontier}}(Y).
\end{aligned}
}
\]

其中 \(\mathcal R_{\mathrm{proj}}^{+}\) 表示原 proposal support 加上预算内 bridge 可覆盖的 support。Prune-only 是退化情形：

\[
\lambda_{\mathrm{br}}\rightarrow\infty
\quad\Rightarrow\quad
\mathcal P_{\mathrm{conn}}\approx\mathcal P_{\mathrm{prune}}.
\]

Bridge feature/material assignment：

\[
F_Y(b)
=
\omega_0(b)F_X(a_0)
+\omega_1(b)F_X(a_1)
+\omega_\theta(b)\widehat F_\theta(b\mid\gamma,Y^m),
\]

\[
P_Y^{\mathrm{brdf}}(b)
=
\operatorname{ProjectPBR}
\left(
\omega_0P_X^{\mathrm{brdf}}(a_0)
+\omega_1P_X^{\mathrm{brdf}}(a_1)
+\omega_\theta\widehat P_\theta^{\mathrm{brdf}}(b)
\right).
\]

当前可安全写：已有 geometry/occupancy proxy 支持 projection-stabilized connectivity；完整 Trellis latent bridge optimizer 与 per-depth material bridge 仍是待验证方法扩展。

## 7. 桥接-自然化-重编码

PS-RSLG 的核心稳定循环应被命名为 **bridge-naturalize-reencode**。

第一步，语法提出候选：

\[
X_{d+1}=
\Theta_{\Pi_d}
\circ
\operatorname{Merge}_{B_d}
\circ
\operatorname{Prop}_{R_d^\star}(S_d).
\]

第二步，投影到 connected state：

\[
\widetilde S_{d+1}=
\mathcal P_{\mathrm{conn}}(X_{d+1};S_d),
\qquad
\widetilde S_{d+1}\in\mathcal S_{\mathrm{conn}}(\lambda_d).
\]

第三步，只在 hard connectivity mask 内调用冻结生成模型自然化：

\[
dZ_t=f_\theta(Z_t,t,y,\Omega_d)\,dt+g(t)\,dW_t,
\qquad t:\tau_d\rightarrow0.
\]

Hard mask：

\[
\mu_{\mathrm{hard}}(c)
=
\mathbf 1[c\in\Omega_d]\,
\mathbf 1[c\in\mathcal R_{\mathrm{proj}}(S_d;b_t,r_t)]\,
\mathbf 1[\operatorname{owner}(c)\leadsto u_{\mathrm{root}}].
\]

Clamp update：

\[
Z_{t-\Delta t}
\leftarrow
(1-\mu_{\mathrm{hard}})\odot Z_{\mathrm{anchor}}
+\mu_{\mathrm{hard}}\odot \Phi_{\theta,t}(Z_t,y).
\]

Schedule：

\[
r_t=r_{\min}+(r_{\max}-r_{\min})\alpha(t),
\qquad
b_t=b_{\min}+(b_{\max}-b_{\min})\alpha(t),
\qquad
T_t\downarrow0.
\]

Sample selection 也必须 projection-aware：

\[
s^\star
=
\arg\min_s
E_{\mathrm{local}}(s)
+\lambda_c V_{\mathrm{conn}}(\mathcal P_{\mathrm{conn}}(s))
+\lambda_r V_{\mathrm{render}}(s)
+\lambda_m V_{\mathrm{mat}}(s).
\]

第四步，decode/project/re-encode：

\[
S_{d+1}
=
\mathcal E_\theta
\circ
\operatorname{ProjectDecode}_{\lambda_d}
\circ
\mathcal D_\theta
(\bar S_{d+1}).
\]

这一步的论文表述要很谨慎：global/full flow repair 已有负面经验，可能 wash out recursive topology。因此 sampler 不拥有全局拓扑；全局拓扑由 grammar ownership、reachable domain、projection 和 cache certificate 共同维护。

## 8. Cache fusion：复用 connected motif，而不是积累 fragments

Connectivity-first cache entry 必须包含 attachment contract：

\[
\boxed{
k=(\operatorname{id},C_k,F_k,M_k,T_k,\ell_k,
A_k^{\mathrm{in}},A_k^{\mathrm{out}},
\Gamma_k^{\mathrm{bridge}},
\operatorname{conn\_cert}_k,
\operatorname{lod\_err}_k,
\operatorname{validity}_k).
}
\]

其中：

\[
V_{\mathrm{conn}}(k)\le \epsilon_c,
\qquad
\forall a\in A_k^{\mathrm{out}},\ a\leadsto A_k^{\mathrm{in}}.
\]

Connected lookup：

\[
\boxed{
\operatorname{Lookup}_{\mathrm{conn}}(K_d,k,T,a_{\mathrm{host}})
=
\operatorname{Attach}(T(C_k,F_k,M_k),a_{\mathrm{host}},A_k^{\mathrm{in}})
\cup T(\Gamma_k^{\mathrm{bridge}}).
}
\]

Transform cache：

\[
K^{\mathrm{transform}}[k,T]
=
(Q_h(TC_k),T_\#F_k,T_\#M_k,
Q_h(TA_k^{\mathrm{in}}),Q_h(TA_k^{\mathrm{out}}),
\operatorname{conn\_cert}).
\]

LOD cache 把远处或小尺度递归折叠为 connected descriptor：

\[
k_{\mathrm{LOD}}
=
(\operatorname{id},T,\ell,\widetilde C,\widetilde F,\widetilde M,
\epsilon_{\mathrm{geom}},\epsilon_{\mathrm{conn}},A^{\mathrm{in}},A^{\mathrm{out}}).
\]

Sliding-window fusion 要求 overlap 或 cross-window bridge：

\[
\operatorname{mass}(C_{W_i}\cap C_{W_j})\ge m_{\min}
\quad\text{or}\quad
\exists\gamma_{ij}:A_{W_i}^{\mathrm{out}}\leadsto A_{W_j}^{\mathrm{in}},
\quad
\operatorname{cost}(\gamma_{ij})\le b_{\mathrm{win}}.
\]

这样 cache fusion 的贡献不是“跑得更快”，而是“递归 motif 只能以 connected contract 的形式复用”。这对 DLA/crystal/radial 尤其重要，因为 naive transform cache 会稳定复制多个相似但互不连接的 chunks。

## 9. 空间竞争能量

候选 action：

\[
a=(c,\Delta C,\Delta F,\Delta M,u_{\mathrm{parent}},\rho,\mu,\tau).
\]

其中 \(c\in L_h\) 是候选坐标或 patch center，\(\Delta C,\Delta F,\Delta M\) 是新增 support/features/material，\(u_{\mathrm{parent}}\) 是父 symbol，\(\rho\) 是 proposal kernel，\(\mu\) 是 mask，\(\tau\) 是 sampler schedule。

空间竞争 / 排斥 / attachment energy：

\[
\boxed{
\begin{aligned}
E(a;S_d)=&
\lambda_{\mathrm{occ}}\,O_d(c)
+\lambda_{\mathrm{excl}}\sum_{q\in C_d}
\mathbf 1[\|c-q\|_\infty<r_{\mathrm{excl}}]\,
\mathbf 1[\operatorname{owner}(q)\ne u_{\mathrm{parent}}]\\
&
+\lambda_{\mathrm{col}}\phi_{\mathrm{collision}}(a,S_d)
+\lambda_{\mathrm{budget}}\max(0,|C_d|+|\Delta C|-T_{\max})\\
&
-\lambda_{\mathrm{att}}\exp
\left(-\frac{\operatorname{dist}(c,C_{\mathrm{att}})^2}{2\sigma_a^2}\right)
-\lambda_{\mathrm{front}}\phi_{\mathrm{frontier}}(c,\mathcal F_d)\\
&
+\lambda_{\mathrm{gap}}\operatorname{dist}(c,C_{\mathrm{att}})
+\lambda_{\mathrm{orphan}}\mathbf 1[\operatorname{path}(c,R_d)=\varnothing]\\
&
+\lambda_{\mathrm{reach}}\mathbf 1[c\notin\mathcal R_{\mathrm{proj}}(S_d;b_d,r_d)]
+\lambda_{\mathrm{br}}\operatorname{cost}_{\mathrm{br}}(c,C_{\mathrm{att}})\\
&
+\lambda_{\mathrm{mat}}\phi_{\mathrm{mat\_seam}}(\Delta M,M_d)
+\lambda_{\mathrm{sym}}\phi_{\mathrm{orbit}}(a,\mathcal G_d).
\end{aligned}
}
\]

Soft scheduler：

\[
\Pr(a\mid S_d)
\propto
\exp(-E(a;S_d)/T_d).
\]

Hard feasibility：

\[
\boxed{
a\in\mathcal A_{\mathrm{hard}}(S_d)
\Longleftrightarrow
O_d(c)=0,\quad
c\in\mathcal R_{\mathrm{proj}}(S_d;b_d,r_d),\quad
\exists\gamma(c,C_{\mathrm{att}}):\operatorname{cost}(\gamma)\le b_d.
}
\]

这将“看起来在 frontier 附近”改为“可连接、可投影、可继续递归”的候选定义。

## 10. 经典系统如何嵌入 PS-RSLG

这里的“嵌入”是可表达性命题：存在 PS-RSLG 的退化或受限实例，使其有限步状态转移等于或近似等于经典系统。不表示视觉质量更好，也不表示当前实验已经完整覆盖这些 family。

### 10.1 IFS

经典 IFS：

\[
A_{d+1}=\bigcup_i f_i(A_d),
\qquad f_i:X\rightarrow X.
\]

PS-RSLG 嵌入：令 \(\Sigma=\{A\}\)，\(\mathcal T=\{f_i\}\)，规则为

\[
A(T)\rightarrow\{A(f_i\circ T)\}_i.
\]

禁用 sampler、projection、competition、material update：

\[
\mathcal N_\theta=\mathrm{Id},\qquad
\mathcal P_{\mathrm{conn}}=\mathrm{Id},\qquad
\Theta_\Pi=\mathrm{Id}.
\]

解释映射 \(\mathcal I\) 输出 \(Q_h(A_d)\)，merge 为 union，则得到量化 Hutchinson iteration：

\[
C_{d+1}=Q_h\left(\bigcup_i f_i(C_d)\right).
\]

若要保持 connectivity-first 版本，则 contractive copies 必须共享 anchor、overlap 或 bridge；否则 IFS 仍可表达，但不一定属于 \(\mathcal S_{\mathrm{conn}}\)。

### 10.2 L-system

确定性 L-system：

\[
\omega_{d+1}=P(\omega_d),
\qquad
\mathcal T_{\mathrm{turtle}}(\omega_d)\rightarrow \text{curve/surface}.
\]

PS-RSLG 嵌入：令 \(U_d\in\Sigma^\star\)，scheduler 同步重写：

\[
u_i=\sigma_i(T_i,\alpha_i)
\rightarrow
(\sigma_{i1}(T_{i1},\alpha_{i1}),\ldots,\sigma_{im}(T_{im},\alpha_{im})).
\]

解释映射 \(\mathcal I\) 是 turtle/frame interpreter，将 symbol string 转成 branch/tube/support。Connectivity-first 版本要求每个新 branch 的 parent frame 继承 attachment path：

\[
\operatorname{parent}(u_{ij})=u_i,
\qquad
\Omega_{ij}\leadsto \Omega_i.
\]

因此传统 L-system 是 PS-RSLG 的有序 symbol rewrite 子类；PS-RSLG 增加了 sparse latent naturalization、projection 和 cache certificate。

### 10.3 Space colonization

Space colonization 以 attractor 分配和 tip 生长为核心：

\[
v_i=\frac{\sum_{a\in\mathcal A_i}(a-p_i)/\|a-p_i\|}
{\left\|\sum_{a\in\mathcal A_i}(a-p_i)/\|a-p_i\|\right\|},
\qquad
p_i^+=p_i+\Delta v_i.
\]

PS-RSLG 嵌入：tip symbols 存在于 \(U_d\)，attractor field 存在于 \(\Gamma_d\)，proposal kernel \(\rho_{\mathrm{sc}}\) 执行最近 attractor 分配与方向平均：

\[
\rho_{\mathrm{sc}}(u_i,S_d)
=
p_i+\Delta v_i.
\]

occupancy/exclusion 是 \(\Pi\) 的一部分，attachment invariant 由 parent tip 继承：

\[
p_i^+\in\mathcal R_{\mathrm{proj}}(S_d;b_d,r_d),
\qquad
\exists \gamma(p_i^+,\Omega_i).
\]

禁用 learned sampler 时，PS-RSLG 退化为经典 space colonization；启用 sampler 时，它变成 “attractor-guided sparse-latent branch growth under hard connectivity masks”。

### 10.4 DLA / frontier accretion

离散 DLA：

\[
c_{d+1}\sim H(\cdot\mid\partial C_d),
\qquad
C_{d+1}=C_d\cup\{c_{d+1}\}.
\]

PS-RSLG 嵌入：frontier symbols 表示 \(\partial C_d\)，\(\rho_{\mathrm{dla}}\) 采样 hitting distribution：

\[
c\sim H(\cdot\mid\partial C_{\mathrm{att}}).
\]

Connectivity-first DLA 不能只保留 hit point，还必须保留 bridge certificate：

\[
\boxed{
c\sim H(\cdot\mid\partial C_{\mathrm{att}}),
\qquad
\gamma(c,C_{\mathrm{att}})\ \text{exists},
\qquad
C^+=C_d\cup\{c\}\cup\gamma.
}
\]

这解释了当前 DLA-like sparse latent 结果为什么容易碎片化：连续 DLA 的粒子通过 random walk hit 自然 attached，但 sparse latent proposal 经 transform、decode/re-encode、quantization 和 sampler naturalization 后，hit patch 可能变成 disconnected thin sheets 或 floaters。PS-RSLG 的 DLA 嵌入必须把 hitting distribution 与 projectable reachability 同时写入规则。

### 10.5 Symmetry / radial orbit

Symmetry transform-copy：

\[
C^+=\bigcup_{g\in G}gC.
\]

PS-RSLG 嵌入：\(\mathcal G_d\) 存储 group/orbit metadata，\(\mathcal T\) 包含 group action，规则为

\[
X(T)\rightarrow\{X(gT)\}_{g\in G}.
\]

如果 rule set 闭合于 \(G\)，并且 projection 近似交换：

\[
\mathcal P_{\mathrm{conn}}(gS)\approx g\mathcal P_{\mathrm{conn}}(S),
\]

则可讨论近似 equivariance：

\[
V_{\mathrm{sym}}(S)
=
\sum_{g\in G}d_{\mathcal S}(gS,S).
\]

但 connectivity-first radial rule 必须加入 hub/ring connector：

\[
\boxed{
C^+
=
\left(\bigcup_{g\in G}gC\right)
\cup C_{\mathrm{hub}}
\cup\bigcup_{g\in G}\gamma(gA^{\mathrm{in}},C_{\mathrm{hub}}).
}
\]

否则 radial orbit expansion 会稳定地产生多个形状相似但互不连接的 chunks。严格 equivariance 当前只能写成待验证扩展；主文可安全写 “symmetry-aware constraints and diagnostics”。

### 10.6 Crystal / lattice growth

Crystal/lattice growth 可写为：

\[
C_{d+1}=C_d\cup\bigcup_{v\in\mathcal B}(C_d+v)
\]

或沿晶面 normal 扩张：

\[
C_{d+1}=C_d\cup \operatorname{GrowFace}(F_i,n_i,\Delta_i).
\]

PS-RSLG 嵌入：`CrystalFace`、`LatticeCell`、`FacetFrontier` 是 typed symbols；\(\mathcal T\) 包含 lattice vector、facet normal extrusion 与 symmetry group；\(\phi_{\mathrm{orbit}}\) 和 \(V_{\mathrm{sym}}\) 约束晶格一致性。Connectivity-first lattice rule 要求 face contact 或 bridge certificate：

\[
\boxed{
\forall v\in\mathcal B,\quad
\operatorname{area}(\partial C_d\cap\partial(C_d+v))\ge a_{\min}
\quad\text{or}\quad
\exists\gamma_v:(C_d+v)\leadsto C_{\mathrm{att}}.
}
\]

这比“复制晶格块”强：每个 lattice copy 必须以可接触、可桥接、可投影的方式进入 active sparse support。当前 bismuth/crystal 远程结果只支持 raw diagnostic，不支持 projected method win，因此 crystal 应写成 stress case 与待验证目标。

### 10.7 Shape grammar / architectural split

虽然用户当前重点是 IFS/L-system/space colonization/DLA/symmetry/crystal，主文也可保留有限 shape grammar 的嵌入，因为 portal、tile、arch、city cases 需要它。有限 scope shape grammar 的 split、extrude、repeat、replace 可写成：

\[
X(\Omega,T,\alpha)
\rightarrow
\{X_j(\Omega_j,T_j,\alpha_j)\}_j.
\]

PS-RSLG 中 \(\Omega_j\) 是 support mask，\(T_j\) 是 frame transform，\(\mathcal I\) 输出 sparse support，\(\mathcal P_{\mathrm{conn}}\) 保证 split/repeat 后仍 attached。全局约束 grammar 或无限城市语义不能作为已实现 claim。

## 11. 实验支持与 claim 边界

### 11.1 已有实验支持的 claim

可以在主文中较安全地写：

1. **连通性必须作为递归状态约束。** 当前 DLA/crystal/tree/fork failure 都说明 fragmented chunks 是 recursive state 错误，而不是最终渲染瑕疵。
2. **Per-depth projection 优于只看 final cleanup 的叙事。** 已有 matched projection ablation 支持 conservative `compete` cases：`vine_compete_d3` 和 `tree_compete_d3` 中，per-depth projection 明显降低 component explosion，并在 final attached/LCR 指标上优于 direct recursion，且比 final-only 更能说明中间状态被约束。
3. **`compete` 是当前最稳定的 sparse occupancy growth operator。** 已有 vine/tree/porous/container 等结果支持 conservative competition 是主线。
4. **Texture/PBR 导出已经足够作为兼容性证据。** 纹理不是当前最大瓶颈；主贡献应转向 connectivity-first recursive geometry。
5. **Full/global flow repair 不是拓扑保证器。** 已有负面经验表明 global repair 会 wash out recursive topology，因此 sampler 必须写成 masked local naturalization。
6. **DLA/crystal 最新远程实验目前只有 raw diagnostic。** wrapper completed 但 sparse/projected pipeline 因 import 问题未产出 selected candidates；不能写成 method win。

### 11.2 可以作为正式方法提案但仍需实验加强的 claim

这些可以在 Method 中定义，但 Results 中要谨慎：

1. Bridge-aware projection generalizes prune-only projection。
2. 可投影可达域能解释 DLA/crystal/radial fragmentation，并给出统一 rule feasibility。
3. Cache entry 应携带 anchors、bridge templates 和 connectivity certificate。
4. Masked local sampler schedule 可以在不破坏 scaffold 的前提下自然化局部 geometry/material。
5. Bridge survival、frontier validity、orphan mass 是比最终 mesh face component 更贴近递归错误的指标。

### 11.3 目前不能写成已解决的 claim

不能写：

1. Trellis2 sampler guarantees connected topology。
2. Cache fusion has solved fragmentation in true decoded assets。
3. DLA/crystal/radial cases already have selected connected projected assets。
4. Strict symmetry/crystal equivariance is achieved。
5. Infinite recursive worlds are implemented。
6. Per-depth material bridge/PBR continuity is experimentally validated。

### 11.4 建议补充的最小实验表

必须同 root、同 depth、同 renderer、同 metric，对比：

| Protocol | Direct recursion | Final-only projection | Prune-only per-depth | Bridge-aware per-depth | Bridge+cache+masked sampler |
|---|---:|---:|---:|---:|---:|
| vine/tree conservative competition | required | required | required | required | optional |
| fork expression stress | required | required | required | required | optional |
| DLA/porous frontier | required | required | required | required | optional |
| radial symmetry | required | required | required | required | optional |
| crystal/lattice | required | required | required | required | optional |

核心指标：

\[
\operatorname{LCR}_{\mathrm{occ}}
=
\frac{|C_{\mathrm{largest\ attached}}|}{|C|+\epsilon},
\qquad
\operatorname{Frag}=1-\operatorname{LCR}_{\mathrm{occ}},
\]

\[
\operatorname{Comp}_{6n}=|\operatorname{Comp}_{6n}(C)|,
\qquad
\operatorname{OrphanMass}=\sum_{Q_k\not\leadsto R}|Q_k|,
\]

\[
\operatorname{BridgeSurvival}
=
\frac{\#\{\gamma\ \text{present after decode/re-encode}\}}
{\#\{\gamma\ \text{inserted before decode}\}+\epsilon},
\]

\[
\operatorname{FrontierValidity}
=
\frac{\#\{f\in\mathcal F:f\leadsto R\}}
{|\mathcal F|+\epsilon},
\]

\[
\operatorname{ProjectionSurvival}
=
\frac{|C_{\mathrm{after\ projection}}|}
{|C_{\mathrm{before\ projection}}|+\epsilon}.
\]

对 L-system/space-colonization baseline，还应报告 skeleton coverage、tip count、branch nodes、total length、branch angle/length distribution，避免用 mesh component 指标误伤传统 tube/skeleton baseline。

## 12. 给 main paper Method 的结构建议

不改 `main.tex`，但建议 Method 结构按以下顺序重排。这样连通性会成为方法主线，而不是中段补丁。

### 12.1 Problem and state

标题建议：**Recursive Generation as Connected Sparse-Latent State Transition**。

内容：

\[
S_{d+1}\sim\mathbb T_{\mathcal G,\theta,d}(\cdot\mid S_d,y),
\qquad
S_d\in\mathcal S_{\mathrm{conn}}(\lambda_d).
\]

先定义任务是 finite-depth recursive asset generation，而不是无限世界生成。紧接着给出 \(S_d=(C,F,U,A,B,M,H,K)\)，并说明 active sparse support、typed symbols、material state、history/cache 都是递归状态。

### 12.2 Grammar productions

标题建议：**Projection-Stabilized Recursive Sparse-Latent Grammar**。

内容：

\[
\mathcal G=(\Sigma,\mathcal T,\mathcal R,\mathcal I,\Pi,
\mathcal P_{\mathrm{conn}},\mathcal N_\theta,K)
\]

和 production 格式。强调 classical procedural systems 是 restricted productions，而 Trellis2 是 frozen sparse 3D prior。

### 12.3 Connectivity invariant and projectable reachable domain

标题建议：**Connectivity as a Grammar Invariant**。

这是主文 Method 的核心，应放在 sampler 前面，而不是 projection 后面。先定义 \(G_\eta(C)\)、\(C_{\mathrm{att}}\)、\(\mathcal S_{\mathrm{conn}}\)、\(\mathcal R_{\mathrm{proj}}\)。讲清楚为什么 \(V_{\mathrm{frontier}}=0\) 比最终 component count 更关键。

### 12.4 Competition and rule feasibility

标题建议：**Attachment-Certified Spatial Competition**。

放空间竞争能量 \(E(a;S)\) 和 hard feasibility：

\[
a\in\mathcal A_{\mathrm{hard}}(S)
\Longleftrightarrow
c\in\mathcal R_{\mathrm{proj}}(S;b,r)
\quad\text{and}\quad
\exists\gamma(c,C_{\mathrm{att}}).
\]

这部分连接 space colonization、DLA/frontier、crystal/lattice 和 fork/tree。

### 12.5 Bridge-naturalize-reencode loop

标题建议：**Bridge-Naturalize-Reencode Transition**。

这里再讲 projection、sampler 和 re-encoding。顺序必须是 connectivity 先行，sampler 局部自然化：

\[
\operatorname{Prop/Merge/Compete}
\rightarrow
\mathcal P_{\mathrm{conn}}
\rightarrow
\mathcal N_{\theta,\mu_{\mathrm{hard}}}
\rightarrow
\mathcal D_\theta
\rightarrow
\operatorname{ProjectDecode}
\rightarrow
\mathcal E_\theta.
\]

明确写：global flow repair is not the topology owner。

### 12.6 Connected cache fusion

标题建议：**Connectivity-Certified Cache Fusion**。

把 cache 从 implementation detail 升级为 semantics：motif/latent/transform/LOD/window/material cache 都必须带 anchors 和 connectivity certificate。这里可作为 infinite recursion/zoom 的谨慎扩展，不要声称已实现无界递归。

### 12.7 Classical systems as embedded grammars

标题建议：**Classical Procedural Systems as Restricted PS-RSLG Instances**。

用一个短表加少量公式覆盖：

| Classical family | PS-RSLG restriction | Connectivity-first addition |
|---|---|---|
| IFS | transform-copy union, no sampler/projection | overlap/anchor/bridge required for connected active state |
| L-system | ordered symbol rewrite + turtle/frame interpretation | child symbols inherit parent attachment |
| Space colonization | attractor-conditioned tip proposal | tip proposal must be in projectable reachable domain |
| DLA | frontier hitting proposal | hit point must carry bridge/path certificate |
| Symmetry/radial | group orbit transform-copy | hub/ring connector and projection-commutation diagnostic |
| Crystal/lattice | lattice/facet transform-copy | face-contact or bridge certificate |

### 12.8 Evidence paragraph in Method or Results bridge

Method 末尾建议加一个 evidence-boundary paragraph：本文已经验证的是 conservative competition + per-depth projection 对 component explosion 的抑制；DLA/crystal/radial/fork 是 stress tests；cache fusion、masked sampler 和 per-depth material bridge 是定义清楚但仍需更多 decoded-asset 实验的扩展。

## 13. 主文可用的压缩段落

可以改写为英文 Method 段落的中文版本如下：

PS-RSLG 将递归 3D 生成定义为 connected sparse latent state 上的约束重写。每个深度 \(d\) 的状态 \(S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d,K_d)\) 必须属于 admissible set \(\mathcal S_{\mathrm{conn}}(\lambda_d)\)：active sparse support 通过 occupancy graph 或 symbol attachment graph 连接到 root anchors，且任何未连接 chunk 都不能成为下一层 frontier、parent symbol 或 cache source。语法规则首先提出 transform-copy、attractor growth、frontier/DLA accretion、symmetry orbit 或 cache lookup 候选；候选经过 attachment-certified spatial competition，只允许落在可投影可达域 \(\mathcal R_{\mathrm{proj}}\) 内，或携带低成本 bridge path。随后 bridge-aware projection 在删除 orphan fragments 与插入自然 connector 之间优化，冻结 Trellis2 sampler 只在 hard connectivity mask 内做局部 naturalization，最后 decode/project/re-encode 回 sparse latent state 并更新带 connectivity certificate 的 cache。这样，projection、sampler 和 cache 都成为递归语义的一部分，而不是最终清理模块。

## 14. 当前优先级

短期写作优先级：

1. 把主贡献改成 connectivity-invariant PS-RSLG，而不是 texture/PBR 或 generic recursive grammar。
2. 用 conservative `compete` projection ablation 支撑主 claim。
3. 把 DLA/crystal/radial/fork 明确写成 stress tests，展示为什么 naive growth 会碎片化。
4. 尽快补一轮 import 修复后的 stage-01 DLA/crystal smoke，只要能产出 raw/sparse/projected before-after，就能决定 bridge-aware projection 是否进入主结果。
5. 如果 true decoded assets 仍不稳定，bridge/cache/sampler 就保留在 Method proposal + diagnostic evidence，不升级为 solved result。
