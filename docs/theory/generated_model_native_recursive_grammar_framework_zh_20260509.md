# 生成模型原生递归语法系统框架：Recursive 3D Generative Growth 的严谨理论笔记

创建时间：2026-05-09  
写作范围：只新增理论文档；不修改论文主文、脚本或实验输出。  
目标用途：为 SIGGRAPH Asia 方法节、补充材料、方法总图和 rebuttal 式答辩提供一个更强但可防守的形式化框架。  
建议方法名：**PS-RSLG: Projection-Stabilized Recursive Sparse-Latent Grammar**。  

## 0. 总体判断

当前论文最有价值的故事不是“程序化建模加 3D 生成模型”，而是：

\[
\text{recursive grammar owns topology}
\quad+\quad
\text{frozen native 3D generator supplies local realization}
\quad+\quad
\text{projection stabilizes every recursive state}.
\]

换句话说，本文应把 Trellis2 / O-Voxel / SLAT 视为递归程序的原生状态空间，而不是后处理器。语法负责 typed handles、frontiers、transforms、attachments、cache descriptors、projection policies 和 material handles；冻结生成模型只在被语法 mask 选中的局部区域内提供 learned shape/material prior，并通过 decode / project / re-encode 把候选状态拉回可继续递归的状态域。

这份笔记的目的有两个。第一，补强现有公式，使它们能真正覆盖 IFS、L-system、space colonization、DLA/frontier、shape grammar、symmetry/crystal 等传统递归系统。第二，避免 reviewer 批评的大状态大元组问题：主文只保留紧凑状态和递归转移，完整对象放在补充材料或理论附录。

安全主张应限制为：

1. PS-RSLG 是一个定义在冻结 3D 生成模型原生 sparse latent state 上的递归重写演算。
2. 经典 procedural systems 是该演算的退化实例或受限实例；这表示可表达性，不表示视觉质量或性能优越性。
3. Frozen sampler 的正确语义是 masked local naturalization，不是 global topology repair。
4. Per-depth projection 给出每层递归状态的不变量；final-only cleanup 没有这个不变量。
5. Infinite recursion 只能写成 contractive limit、bounded visible-window stream 或 cache/LOD descriptor semantics；当前实验不支持“无界 3D mesh 输出”。
6. Crystal / DLA / symmetry 目前可以作为 grammar family 和 stress-test 进入方法框架，但强实验 claim 必须看连通性、root reachability、neutral render、symmetry error 和 zoom QA。

## 1. 两层形式化：主文紧凑，附录完整

### 1.1 主文状态

主文建议只让读者记住三元状态：

\[
z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d).
\]

其中 \(\mathcal V_d\subset h\mathbb Z^3\) 是 active sparse token support，\(\mathbf F_d:\mathcal V_d\rightarrow\mathbb R^q\) 是 generator-native latent features，\(\mathcal A_d\) 是 grammar-readable anchors / handles / frontier / attachment graph。一个 handle 写为

\[
h_i=(\sigma_i,T_i,\Omega_i,\alpha_i),
\]

\(\sigma_i\) 是类型，\(T_i\) 是 local frame，\(\Omega_i\subseteq\mathcal V_d\) 是 ownership 或 target region，\(\alpha_i\) 保存 radius、age、priority、material intent、LOD level、cache id 等局部属性。

所有 masks、random seeds、rule traces、projection thresholds、diagnostics、cached motifs、texture-export metadata 都属于执行器 bookkeeping：

\[
\mathcal B_d=
\{\text{masks, seeds, traces, caches, projection schedules, material/export metadata}\}.
\]

这可以直接回应 reviewer：主状态不是任意拼出来的八元组，而是一组 sparse latent tokens 加语法可读写的 handles。

### 1.2 附录完整执行机

为了证明覆盖性和稳定性，附录可以引入完整执行机：

\[
\mathfrak M=
(\Sigma,\mathcal T,\mathcal R,\mathcal I,\mathsf{Sched},
\mathsf{Prop},\mathsf{Merge},\mathsf{Comp},
\mathcal N_\theta,\mathcal D_\theta,\Pi_\lambda,\mathcal E_\theta,
\mathsf{Cache},\mathcal O).
\]

这不是主文大 tuple，而是语义对象清单：

| 对象 | 作用 |
|---|---|
| \(\Sigma\) | typed handle alphabet |
| \(\mathcal T\) | transform semigroup：rigid、scale、mirror、portal、lattice、contractive maps |
| \(\mathcal R\) | stochastic context-sensitive rule templates |
| \(\mathcal I\) | interpretation map：symbol/frame/mask 到 sparse support、mesh patch、material region |
| \(\mathsf{Sched}\) | rule scheduler：parallel、priority queue、frontier sampling、group orbit expansion |
| \(\mathsf{Prop}\) | proposal generator |
| \(\mathsf{Merge}\) | masked sparse merge and feature/material blending |
| \(\mathsf{Comp}\) | occupancy / attachment / collision / symmetry competition |
| \(\mathcal N_\theta\) | frozen masked flow/SDE/local sampler |
| \(\mathcal D_\theta,\mathcal E_\theta\) | decode and re-encode between sparse latent and mesh/occupancy asset |
| \(\Pi_\lambda\) | projection to admissible recursive state |
| \(\mathsf{Cache}\) | motif、latent、transform、LOD、visible-window descriptors |
| \(\mathcal O\) | observable/export：mesh、GLB、render、metrics |

主文可把它写成一句：

> The executor maintains auxiliary masks, traces, caches, and projection schedules, but the recursive semantic state remains \(z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d)\).

## 2. 递归程序语义

### 2.1 规则模板

规则是 handle-to-proposal template：

\[
\rho:\ h_i\mapsto
\{(\sigma_j,\tau_j,\Omega_j,m_j,\kappa_j,\pi_j,\eta_j)\}_{j=1}^{k}.
\]

每个输出项的含义是：

| 符号 | 含义 |
|---|---|
| \(\sigma_j\) | 输出 handle type |
| \(\tau_j\in\mathcal T\) | local transform |
| \(\Omega_j\) | target / ownership region |
| \(m_j:\mathcal V\rightarrow[0,1]\) | edit mask |
| \(\kappa_j\) | feasibility predicate |
| \(\pi_j\) | proposal kernel：grow、branch、attach、copy、split、refine、cache lookup |
| \(\eta_j\) | random seed、sampler schedule、material condition 或 LOD policy |

规则的核心语义不是“复制 mesh”，而是发射一个可投影、可连接、可继续递归的局部程序。

### 2.2 Proposal and merge

对 transform-copy 规则，候选 support 和 features 可以写成：

\[
\widehat{\mathcal V}_j
=Q_h\bigl(\tau_j(\mathcal V_d\cap\Omega_j)\bigr),
\]

\[
\widehat{\mathbf F}_j(Q_h(\tau_j v))
=\mathcal T^F_j\mathbf F_d(v).
\]

masked merge 采用 normalized blend：

\[
\mathbf F^+(v)=
\frac{
w_0(v)\mathbf F_d(v)+\sum_j w_j(v)\widehat{\mathbf F}_j(v)}
{w_0(v)+\sum_j w_j(v)+\epsilon},
\qquad
w_j(v)=m_j(v)\beta_j(v).
\]

对于 grow / branch / attach 规则，\(\pi_j\) 直接生成新的 sparse coordinates 和 features；对于 material 规则，\(\mathbf F\) 中的 material component 或独立 material handle 按同一 mask/transform 运输，但不作为几何连通性的证据。

### 2.3 可投影可达域

proposal 不能只满足局部生成质量，还必须能成为下一层递归状态。定义可投影可达域：

\[
\Delta\mathcal V
\subset
\mathcal R_{\mathrm{proj}}(z_d;b_d,r_d),
\]

或存在 bridge certificate：

\[
\exists B:\quad
\Delta\mathcal V\cup B\in\mathcal Z_{\mathrm{adm}}(\lambda_d),
\qquad
\operatorname{cost}(B)\le b_d.
\]

\(\mathcal R_{\mathrm{proj}}\) 受 attachment distance、collision、occupancy exclusion、token budget、symmetry closure、material seam 和 renderability 约束。这一点是 PS-RSLG 和普通 latent editing 的分界：一个 patch 不因局部好看而激活，它必须能连回递归 scaffold。

### 2.4 Sparse competition

对候选 action \(a\) 和 sparse token \(v\)，定义竞争分数：

\[
\begin{aligned}
\psi(a,v;z_d)=
{}&\lambda_{\mathrm{att}}\phi_{\mathrm{att}}(a,v)
-\lambda_{\mathrm{occ}}\phi_{\mathrm{occ}}(a,v)
-\lambda_{\mathrm{col}}\phi_{\mathrm{collision}}(a,v)\\
&+\lambda_{\mathrm{front}}\phi_{\mathrm{frontier}}(a,v)
+\lambda_{\mathrm{grp}}\phi_{\mathrm{orbit}}(a,v)
+\epsilon_\theta(a,v,\xi).
\end{aligned}
\]

前几项复现传统 growth / collision / frontier / symmetry 逻辑；\(\epsilon_\theta\) 是来自 frozen generator 或 sample selection 的弱随机偏好。当前论文应强调：实验中不把稳定性归因于 \(\epsilon_\theta\)，而归因于 grammar feasibility、competition 和 per-depth projection。

### 2.5 中心递归转移

主文公式保持简洁：

\[
z_{d+1}=
\operatorname{Enc}_{\theta}
\left[
\Pi_{\lambda_d}
\left(
\operatorname{Dec}_{\theta}
\left(
\mathcal T_{\theta}(z_d;\mathcal R_d,y)
\right)
\right)
\right].
\]

其中

\[
\mathcal R_d=\operatorname{SelectRules}(z_d,\mathcal G,\mathcal B_d),
\]

\[
\tilde z_{d+1}=
\mathsf{Merge}\bigl(z_d,\mathsf{Prop}_{\mathcal R_d}(z_d)\bigr),
\]

\[
\bar z_{d+1}=
\mathcal N_\theta(\tilde z_{d+1};m_d,y,\eta_d),
\]

\[
x_{d+1}=\operatorname{Dec}_{\theta}(\bar z_{d+1}),
\quad
x_{d+1}^{\star}=\Pi_{\lambda_d}(x_{d+1},\mathcal A_d),
\quad
z_{d+1}=\operatorname{Enc}_{\theta}(x_{d+1}^{\star}).
\]

Projection 在递归转移内部，而不是最终 cleanup，这是论文最核心的设计选择。

## 3. 生成采样器语义：masked local naturalization

### 3.1 Flow / SDE 形式

冻结生成模型可以写成 deterministic flow：

\[
\frac{dz_t}{dt}=v_\theta(z_t,t,y),
\]

或 SDE：

\[
dZ_t=f_\theta(Z_t,t,y)\,dt+g(t)\,dW_t.
\]

但在 PS-RSLG 中，它只作用在 rule mask 上。令 \(m_d\) 是 sparse edit mask，anchor region hard-clamped，则一阶反向步写成：

\[
z_{t-\Delta t}
=
(1-m_d)\odot z_{\mathrm{anchor}}
+m_d\odot\Phi_{\theta,t}(z_t,y).
\]

feature-level blend 写成：

\[
\mathbf f_i'=
(1-\alpha_i)\mathbf f_i^{\mathrm{rule}}
+\alpha_i\mathbf f_i^\theta,
\qquad i\in m_d.
\]

这说明 naturalization 是局部形状和材质先验，不是全局 topology repair。

### 3.2 Sampler as conditional kernel

更一般地，\(\mathcal N_\theta\) 是一个条件 Markov kernel：

\[
\mathcal N_\theta(d\bar z\mid \tilde z,m,y,\eta)
\]

并满足 hard clamp 条件：

\[
\bar z|_{\mathcal V\setminus m}=\tilde z|_{\mathcal V\setminus m}
\quad\text{almost surely}.
\]

若只能做到 soft clamp，可定义泄漏误差：

\[
\epsilon_{\mathrm{leak}}
=
\mathbb E\left[
d\bigl(\bar z|_{\mathcal V\setminus m},\tilde z|_{\mathcal V\setminus m}\bigr)
\right].
\]

论文中应把 full flow repair 的负结果解释为 \(\epsilon_{\mathrm{leak}}\) 太大：全局生成器会覆盖语法拓扑。因此正方法必须是 hard-mask / local sampler。

### 3.3 Projection-aware sample selection

如果一个 mask 内采样多次，选择标准不应只是视觉质量，而应是：

\[
s(\bar z)
=
-\lambda_c V_{\mathrm{conn}}(\bar z)
-\lambda_f V_{\mathrm{frontier}}(\bar z)
-\lambda_o V_{\mathrm{occ}}(\bar z)
-\lambda_b \operatorname{bridge\_cost}(\bar z)
+\lambda_q Q_{\mathrm{local}}(\bar z,y).
\]

即优先选择能被 projection 接受并能继续递归的样本。这样 sampler 语义才和 recursion semantics 对齐。

## 4. 经典系统覆盖命题

以下覆盖命题只表示“存在一个 PS-RSLG 退化实例等价或近似于经典系统”。它不表示 PS-RSLG 在视觉质量、效率或理论性质上支配这些系统。

### 4.1 IFS

经典 IFS 在紧致度量空间 \(X\) 上由 contraction maps \(f_i:X\to X\) 给出：

\[
A_{d+1}=\bigcup_{i=1}^m f_i(A_d).
\]

构造 PS-RSLG 实例：\(\Sigma=\{\mathrm{Patch}\}\)，\(\mathcal T=\{f_i\}_{i=1}^m\)，merge 为集合并，\(\mathcal N_\theta=\mathrm{Id}\)，\(\Pi_\lambda=\mathrm{Id}\)，feature transport 为 identity。规则：

\[
\mathrm{Patch}\mapsto\{(\mathrm{Patch},f_i,X,1,\top,\pi_i,\varnothing)\}_{i=1}^m.
\]

则 support 转移为

\[
\mathcal V_{d+1}
=\bigcup_i f_i(\mathcal V_d),
\]

这与 IFS 有限步迭代一致。若使用 sparse grid，只得到量化版本：

\[
\mathcal V_{d+1}^{(h)}
=\bigcup_i Q_h(f_i(\mathcal V_d^{(h)})),
\]

连续 IFS 极限 claim 需要令 \(h\rightarrow0\) 或明确为 finite-resolution approximation。

### 4.2 L-system

设确定性上下文无关 L-system 为

\[
\mathcal L=(V,\omega_0,\{a\mapsto w_a\}_{a\in V}),
\qquad
\omega_{d+1}=\mathcal L(\omega_d).
\]

令 \(\mathcal A_d\) 保存有序 handle 序列：

\[
\mathcal A_d=(h_1,\ldots,h_n),\qquad \sigma(h_i)\in V.
\]

调度器同步重写每个 handle，规则 \(a\mapsto w_a\) 直接转为 handle rewrite，merge 为稳定拼接。则符号投影满足

\[
\pi_\Sigma(\mathcal A_{d+1})
=
\mathcal L(\pi_\Sigma(\mathcal A_d)).
\]

Turtle interpretation 是 \(\mathcal I\) 的一种选择：它把符号序列和 frame stack 解释为 branch support、radii、materials 和 frontier handles。若调度器异步或规则随机，则覆盖的是 stochastic/asynchronous L-system 变体。

### 4.3 Space colonization

Space colonization 的状态包含 tips \(B_d=\{b_i\}\) 和 attractors \(\Gamma_d\)。每个 attractor 分配到最近 tip：

\[
\mathcal A(b_i)=
\{a\in\Gamma_d:
i=\arg\min_j\|a-b_j\|\}.
\]

若 \(\mathcal A(b_i)\neq\emptyset\)，方向为

\[
u_i=
\frac{
\sum_{a\in\mathcal A(b_i)}
\frac{a-b_i}{\|a-b_i\|}
}{
\left\|
\sum_{a\in\mathcal A(b_i)}
\frac{a-b_i}{\|a-b_i\|}
\right\|
},
\qquad
b_i'=b_i+\delta u_i.
\]

PS-RSLG 覆盖方式：把 tips 作为 `Tip` handles，把 attractors 作为 field 或 `Attractor` handles，proposal kernel \(\pi_{\mathrm{sc}}\) 执行最近分配和方向平均，occupancy competition 执行 collision/exclusion，kill radius 删除已覆盖 attractors。若 sampler 和 projection identity，则 tip/attractor 转移等同经典算法。若加 projection，则得到 projection-stabilized space-colonization variant。

### 4.4 DLA / frontier accretion

离散 DLA 可写成对 frontier hitting distribution \(\mu_{\partial O_d}\) 的采样：

\[
q_d\sim \mu_{\partial O_d},\qquad
O_{d+1}=O_d\cup\{q_d\},
\]

其中 \(\mu_{\partial O_d}\) 可由 random walk hitting probabilities 诱导。PS-RSLG 构造：`Frontier` handles 保存 exposed boundary，\(\pi_{\mathrm{dla}}\) 从 hitting distribution 或其近似中采样 attachment site，feasibility 要求 face-contact 或 bridge certificate，occupancy exclusion 防止重叠。

得到的覆盖命题是：

若 \(\pi_{\mathrm{dla}}=\mu_{\partial O_d}\)、merge 为集合并、sampler/projection identity，PS-RSLG 的 occupancy 转移等于离散 DLA 的一次 accretion。若使用 finite candidate set、learned sampler 或 bridge projection，则它是 DLA-inspired frontier grammar，而不是严格物理 DLA。当前论文的 DLA/coral 结果应按 stress-test 或 connected scaffold 写，不应宣称真实 DLA 已解决。

### 4.5 Shape grammar / CGA

有限 local shape grammar 的规则通常形如 split、extrude、replace、repeat：

\[
\mathrm{Face}(T,\Omega,\alpha)
\mapsto
\{\mathrm{Face}_j(T_j,\Omega_j,\alpha_j)\}_{j=1}^{k}.
\]

PS-RSLG 覆盖方式：把 faces、tiles、volumes、portals、module sockets 表示为 typed handles；\(\tau_j\) 和 \(\Omega_j\) 记录局部坐标系中的 split/extrude/replace；\(\mathcal I\) 把 handles realization 到 sparse support 或 mesh patches。对于有限 derivation 和局部上下文条件，PS-RSLG 可以表达 CGA-style 规则。边界是：任意全局优化型 shape grammar、复杂语义约束和无限 constraint solving 不是本框架自动覆盖的内容。

### 4.6 Symmetry and crystal cases

令 \(G\) 是有限群、晶格群或离散 transform semigroup。若 rule set 对 \(G\) 闭包：

\[
\forall g\in G,\forall\rho\in\mathcal R,\qquad
g\rho g^{-1}\in\mathcal R,
\]

且 scheduler 每次扩展完整 orbit，则 proposal support 是 \(G\)-closed。严格等变还要求 merge、sampler、projection、codec、quantization 与群作用交换：

\[
\mathsf T(gz)=g\mathsf T(z).
\]

现实中只能给近似误差界：

\[
d_{\mathcal S}(\mathsf T(gz),g\mathsf T(z))
\le
L_{\mathrm{post}}
(\epsilon_{\mathrm{rule}}
+\epsilon_{\mathrm{merge}}
+\epsilon_{\mathrm{sampler}}
+\epsilon_{\mathrm{proj}}
+\epsilon_{\mathrm{codec}}
+\epsilon_{\mathrm{grid}}).
\]

Crystal / bismuth / pyrite 类别可以写成 lattice-orbit transform-copy 加 face-contact invariant：

\[
\tau_{n,k}=T_{\mathrm{lattice}}(n)\circ R_k\circ S_k,
\qquad
\operatorname{contact}(\Omega_{n,k},\Omega_{\mathrm{parent}})\ge c_{\min}.
\]

这支持“connected crystal-like scaffold / lattice grammar”主张，但不支持材料物理意义上的晶体成核与真实生长模拟。

## 5. Projection stability 证明草图

### 5.1 Admissible state and violation

定义 violation：

\[
e(z)=
w_cV_{\mathrm{conn}}(z)
+w_fV_{\mathrm{frontier}}(z)
+w_oV_{\mathrm{occ}}(z)
+w_aV_{\mathrm{attach}}(z)
+w_rV_{\mathrm{render}}(z)
+w_mV_{\mathrm{mat}}(z).
\]

可接受集合：

\[
\mathcal Z_{\mathrm{adm}}(\lambda)
=
\{z:e(z)\le\epsilon_\lambda,\ |\mathcal V(z)|\le T_{\max}\}.
\]

Projection 满足：

\[
e(\Pi_\lambda(x))\le \epsilon_P,
\]

codec round trip 满足：

\[
e(\operatorname{Enc}_\theta(\Pi_\lambda(\operatorname{Dec}_\theta(z))))
\le
e(\Pi_\lambda(\operatorname{Dec}_\theta(z)))+\epsilon_E.
\]

则每一步执行后：

\[
e(z_{d+1})\le \epsilon_P+\epsilon_E.
\]

这给出 per-depth invariant：

\[
z_d\in\mathcal Z_{\mathrm{adm}}(\lambda_d)
\quad d=1,\ldots,D.
\]

这不是证明每个视觉结果完美，而是证明递归状态不会携带超过阈值的 orphan/frontier/connection 违例进入下一层。

### 5.2 与 final-only cleanup 的差异

Final-only cleanup 只保证：

\[
e(\Pi_\lambda(x_D))\le\epsilon_P,
\]

但不保证中间 \(z_1,\ldots,z_{D-1}\) 合法。若某个 orphan component \(Q\) 在深度 \(t\) 成为 active handle：

\[
Q\not\leadsto R_t,\qquad
h_Q\in\mathcal A_t^{\mathrm{active}},
\]

则后续规则可能从 \(h_Q\) 派生：

\[
h_Q\mapsto\{h_{Q,1},\ldots,h_{Q,k}\}.
\]

即使最终删除 \(Q\) 及其子树，递归历史、cache、sampler condition、material handle、预算分配已经被污染。这个反例说明 final-only cleanup 不等价于 per-depth projection。

### 5.3 稳定性和表达性的边界

若 proposal 每层生成坏碎片比例 \(\delta_d\)，per-depth projection 的碎片抑制率为 \(\rho_P\)，codec 误差为 \(\epsilon_E\)，可写一个粗略递推：

\[
e_{d+1}\le
\rho_P(e_d+\delta_d)+\epsilon_E.
\]

若 \(\rho_P<1\) 且 \(\delta_d\le\bar\delta\)，则

\[
e_d\le
\rho_P^d e_0+
\frac{1-\rho_P^d}{1-\rho_P}
(\rho_P\bar\delta+\epsilon_E).
\]

强 `compete` case 对应较小 \(\bar\delta\)，因此 per-depth projection 表现稳定；`compete_fork` 对应较大 \(\bar\delta\) 或 projection 表达性不足，因此虽然 raw components 下降，最终仍可能多 component。这正好对应当前实验：conservative competition 是主文强结果，expressive fork 是 stability-expression boundary。

## 6. Cache / LOD / infinite recursion 语义

### 6.1 三种无界递归语义

PS-RSLG 可讨论三种“无界”概念，但只有第一种和当前实验较接近：

| 类型 | 定义 | 当前论文定位 |
|---|---|---|
| finite-depth deep recursion | \(D\) 有限但较深，所有 geometry realized | 主实验范围 |
| visible-window stream | 逻辑深度无界，但只 materialize 当前窗口 | 方法扩展 / appendix |
| contractive limit object | 类 IFS 的极限集合 | 理论覆盖，不是 mesh 输出 |

### 6.2 Active window bound

令 \(W_t\) 是当前可见窗口集合：

\[
\mathcal V_t^{\mathrm{active}}
=
\bigcup_{\Omega\in W_t}\mathcal V_{\Omega,t},
\qquad
\sum_{\Omega\in W_t}|\mathcal V_{\Omega,t}|
\le T_{\max}.
\]

窗口外区域不展开为 geometry，而表示为 descriptor：

\[
\mathcal D_{\mathrm{off}}=
\{(k,\tau,\ell,\theta_{\mathrm{LOD}},b_{\mathrm{proj}})\}.
\]

cache lookup 不是直接复制大 mesh，而是返回局部 program 或 latent motif descriptor：

\[
\mathsf{CacheLookup}(k,\tau,\ell)
\rightarrow
(\Delta\mathcal V,\Delta\mathbf F,\Delta\mathcal A,\kappa_{\mathrm{bridge}}).
\]

只有当 descriptor materialize 并通过 feasibility / projection 后，它才成为 active state。

### 6.3 LOD consistency

LOD cache 应满足跨层一致性：

\[
d_{\mathrm{LOD}}
\left(
\mathcal O(\mathsf{Expand}_{\ell}(k)),
\mathcal O(\mathsf{Down}_{\ell+1\to\ell}(\mathsf{Expand}_{\ell+1}(k)))
\right)
\le\epsilon_{\mathrm{LOD}}.
\]

若无法证明或测量该关系，cache/LOD 只能作为工程扩展，不应作为主贡献。当前 cache/sampler remote summary 显示 supporting ablation viable 为 false；本地 smoke 只能作为 proxy 诊断。因此主文应保守写：cache/LOD gives a finite-memory semantics and a future path, not a demonstrated standalone contribution。

## 7. 实验证据如何支持 claim

| Claim | 需要的证据 | 当前证据状态 | 论文定位 |
|---|---|---|---|
| PS-RSLG 可表达 IFS / L-system / space colonization / DLA / shape grammar / symmetry | 构造性证明和规则映射 | 理论上可写；不依赖实验 | Method / appendix |
| Frozen generator 应作为 masked local naturalizer | full flow repair 会改写拓扑；masked/local 公式和局部实验 | 负结果和公式支撑设计选择；强正证据有限 | Method 设计动机 |
| Per-depth projection 优于 direct / final-only | 同 root、同 depth、direct/final-only/per-depth 表 | `vine_compete_d3`、`tree_compete_d3` 强；fork 只部分 | 主文核心结果 |
| Space competition 是主线 operator | conservative compete 的 component/LCR/depth 稳定性、传统 baseline | 已有 projection ablation 和 traditional baseline | 主实验 |
| Expressive fork 有稳定性边界 | fork raw component 降低但 final remains fragmented | 当前表格直接支持 | Ablation / limitation |
| DLA/frontier grammar 可写 | frontier hitting / bridge certificate 证明 | 理论可写；视觉结果仍弱 | Stress-test / appendix |
| Crystal/symmetry grammar 可写 | group closure、symmetry error、connected lattice scaffold | scaffold 正例可用；不是物理 crystal | Non-tree breadth / appendix |
| Cache/LOD/infinite recursion | window bound、LOD consistency、cache ablation | remote cache run 不支持 standalone；本地 smoke 是 proxy | Extension / future work |
| Texture/PBR export 可兼容 projected meshes | GLB export、Blender import、PBR channels、same-camera render | selected meshes 可用，但不能证明拓扑 | Asset readiness |
| Method behavior depth/parameter controls | 同条件 depth strips、fixed camera/material/render protocol | vine / pyrite / bismuth 等已有展示文档 | Method behavior figure |

最强主文 claim 应围绕：

> finite-depth, projection-stabilized recursive sparse-latent asset growth, demonstrated on conservative space-competition / branch-like cases, with selected textured GLB export after projected mesh validation.

需要降调的 claim：

> true infinite recursion, strict symmetry equivariance, true physical DLA/crystal growth, full sampler-based topology repair, universal superiority over procedural systems.

## 8. 论文 Method 组织建议

建议 Method 节按以下顺序写，不要按工程模块堆叠：

### 8.1 Problem Setting

一句话定义任务：

\[
x_D=\mathcal O(z_D),
\qquad
z_{d+1}\sim
\mathsf T_{\mathcal G,\theta,d}(\cdot\mid z_d,y,\xi_d).
\]

强调：finite-depth recursive 3D asset generation over frozen native sparse state。

### 8.2 Core State and Handles

只写：

\[
z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d),
\qquad
h_i=(\sigma_i,T_i,\Omega_i,\alpha_i).
\]

然后解释 connected-state invariant 和 active handle 必须 root-attached。

### 8.3 Rule Templates

写 handle-to-proposal template：

\[
\rho:\ h_i\mapsto
\{(\sigma_j,\tau_j,\Omega_j,m_j,\kappa_j,\pi_j,\eta_j)\}_{j=1}^{k}.
\]

用一张小表列 grow、branch、attach、copy、split/extrude、refine、material、cache。主文表格不需要展开所有 proof。

### 8.4 Projection-Stabilized Execution

写中心公式和 Algorithm 1：

1. select active handles；
2. apply rules；
3. generate proposals；
4. merge and compete；
5. masked local naturalization；
6. decode；
7. project to admissible connected asset；
8. re-encode；
9. update handles/material/caches。

Projection 子过程可作为 Algorithm 2：

1. build mesh/occupancy connectivity graph；
2. find root-attached components；
3. score components by mass、attachment、bridge cost、renderability、material consistency；
4. keep attached / bridgeable components；
5. prune orphans；
6. weld/close/bridge conservatively；
7. remove orphan handles and validate frontier。

### 8.5 Masked Naturalization

写 flow/SDE + hard clamp 公式。强调 sampler is local prior, not topology owner。

### 8.6 Classical Systems as Limits

主文只保留短段和一条表；详细证明放 appendix。避免让 coverage proof 打断核心方法。

### 8.7 Effective Resolution, Material, Cache Scope

把 recursive effective resolution 写成 finite-depth / finite-window 细化，不写成无限资产输出。Material 写成 handles + selected projected mesh texture export。Cache 写成 extension。

### 8.8 Experiments and Claims

实验不按时间线写，按 claim 写：

1. trivial baselines fail；
2. projection ablation；
3. space competition and depth behavior；
4. operator stability boundary；
5. non-tree / symmetry / DLA stress tests；
6. texture/PBR compatibility；
7. limitations。

## 9. 方法图组织建议

### Figure 2：主方法总图

目标：一眼看懂 projection inside recursion。

建议布局：

```text
root mesh / condition
  -> Enc_theta
  -> z_d = (V,F,A)
  -> grammar handles/rules
  -> proposals + masks + feasibility
  -> competition + masked sampler
  -> Dec_theta
  -> Projection Pi_lambda
  -> Enc_theta
  -> update handles/caches
  -> loop
  -> selected finite-depth mesh / textured GLB export
```

图内短语只保留：

- grammar controls topology；
- generator naturalizes masked regions；
- projection stabilizes each depth；
- cache/LOD are descriptors unless materialized；
- texture export is after projected mesh validation。

### Figure 3：规则族和经典系统覆盖

做成 taxonomy 表或矩阵：

| Classical family | State object | Rule kernel | Disabled components | Evidence |
|---|---|---|---|---|
| IFS | patch support | transform-copy | sampler/projection | proof |
| L-system | ordered handles | sync rewrite | learned prior | proof |
| Space colonization | tips + attractors | average direction | sampler optional | baseline + proof |
| DLA/frontier | frontier support | hitting distribution | sampler optional | stress |
| Shape grammar | typed faces/tiles | split/extrude/replace | learned prior optional | proof |
| Symmetry/crystal | orbit/lattice handles | group closure | exact equivariance not claimed | scaffold/metric |

这张图不必放在主文前半，如果空间紧可放 supplement。

### Figure 4：Projection stability

主图应是 claim-driven：

- direct recursion；
- final-only cleanup；
- per-depth projection；
- component count vs depth；
- LCR vs depth；
- zoom in on orphan/frontier contamination。

重点 caption：

> Final cleanup can remove final geometry but cannot prevent invalid intermediate components from becoming parents, frontiers, or cached motifs.

### Figure 5：Space competition / method behavior

用同 root、同 depth、同 camera、同 material protocol：

- depth 1/2/3/4 strip；
- conservative `compete` vs expressive `fork`；
- branch/tip metrics；
- projection survival ratio；
- zoom panels for attachments。

不要把它命名为 ablation，除非变量被严格控制。更合适叫 method-behavior visualization。

### Figure 6：Non-tree breadth

只放过 gate 的 mesh/GLB：

- connected bismuth / pyrite scaffold；
- hard-surface transform-copy；
- portal / radial if connected；
- DLA/coral 只作为 stress or appendix。

caption 必须降调：crystal-like lattice grammar / DLA-inspired connected scaffold，不写真实物理生长。

### Figure 7：Texture/PBR compatibility

与结构图分开。只证明：

- projected mesh 可导出 GLB；
- PBR channels 存在；
- Blender 可 import/render；
- selected assets 具备 asset-readiness。

不要让 texture beauty render 承担连通性证明。

## 10. 叙事评估和风险控制

### 10.1 强叙事

最强的论文叙事是：

> Native sparse 3D generators look suitable for recursive generation, but naive use fails because generators are not recursive execution engines. PS-RSLG turns the sparse generative state into a typed recursive grammar state. Grammar owns topology and handles; the frozen generator locally naturalizes; projection is executed at each depth, making connected projectable state a recursive invariant.

这比“procedural + generative hybrid”更必然，也更像方法贡献。

### 10.2 最大风险

| 风险 | 处理 |
|---|---|
| 公式又变成大元组 | 主文只保留 \(z=(V,F,A)\)、rule template、compact transition |
| 经典覆盖打断主线 | 主文短表，证明放 appendix |
| DLA/crystal 被质疑 | 写成 frontier / lattice grammar stress，不写物理模拟 |
| Texture 掩盖结构 | 结构指标和 neutral render 先行，texture 单独作为 compatibility |
| Cache/infinite recursion 过强 | 写 finite-window descriptor semantics，不写 infinite mesh |
| Sampler 被认为接管拓扑 | hard clamp 和 masked local naturalization 公式必须清楚 |
| Final-only cleanup 看似等价 | 用 orphan handle contamination 反例解释为什么不等价 |

### 10.3 可直接进入论文的贡献句

可以写：

> We formulate recursive 3D asset growth as execution of a typed grammar over the sparse latent state of a frozen native 3D generator. Classical recursive modeling systems arise as restricted rule families, while the learned generator contributes masked local naturalization, codec operations, and optional material export. The key stability mechanism is to project every decoded intermediate state to an admissible connected asset before re-encoding and continuing recursion.

不建议写：

> Our method solves infinite recursive 3D generation, DLA, crystals, and all shape grammars with a generative model.

## 11. 最终建议

新方法框架应被命名和呈现为 **Projection-Stabilized Recursive Sparse-Latent Grammar**。主文必须紧凑：状态三元组、规则模板、递归转移、masked sampler、projection algorithm。补充材料再给完整执行机和覆盖证明。

实验叙事应与理论 claim 对齐：conservative competition + per-depth projection 是主结果；fork、DLA、crystal、cache、symmetry 是边界、广度和 stress-test；texture/PBR 是 projected mesh 的资产兼容性证据。这样能把“当前公式太弱”的问题转化为一个复杂但 coherent 的 grammar/system framework，同时避免过度 claim。
