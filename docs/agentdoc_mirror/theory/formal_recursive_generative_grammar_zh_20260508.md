# Projection-Stabilized Recursive Sparse-Latent Generative Grammar

本文档给出 Recursive 3D Generative Growth 项目的理论/公式化框架草案。目标不是把当前系统描述成若干工程模块的串联，而是把它定义为一个在 typed sparse 3D latent state 上运行的递归生成语法。传统程序建模方法提供可解释的递归、分裂、吸附、聚集和对称规则；冻结的 Trellis2/O-Voxel/SLAT 生成器提供 learned 3D naturalization、局部修复、形状再编码和外观/PBR 合成。核心观点是：递归生成的稳定性不能依赖最终一次 cleanup，而必须把 projection、竞争、mask、re-encode 和 cache update 放进每一层 rule semantics。

为便于后续论文写作，下文暂称该系统为 **P-RSLG: Projection-Stabilized Recursive Sparse-Latent Grammar**。

## 1. 问题定义

给定一个 root asset、条件输入 \(y\)（可为空、文本、图像、mesh 或 material intent）、递归深度预算 \(D\)，以及一个语法程序 \(G\)，目标是生成一族有限深度 3D 资产：

$$
S_0 \xrightarrow{G} S_1 \xrightarrow{G} \cdots \xrightarrow{G} S_D,
$$

并从最终状态导出 mesh / textured GLB / 多视角 render。这里 \(S_D\) 是潜在无限递归程序的有限截断，而不是声称已经物化无限几何。每一层递归不是直接操作 triangle soup，也不是只在 2D guidance 上约束一次采样，而是在 Trellis2 mesh-derived sparse O-Voxel/SLAT 状态中执行 typed rewrite。

一个理想的递归生成系统需要同时满足四类要求：

1. **程序性结构可控**：能表达 IFS、L-system、space colonization、DLA/frontier accretion、shape grammar、symmetry/crystal 等图形学递归系统。
2. **现代 3D asset 可用性**：能进入 learned 3D representation、mesh decode、re-encode、texture/PBR/export pipeline。
3. **递归稳定性**：误差、碎片、漂浮组件和 topology drift 不随深度失控放大。
4. **随机自然化**：随机性不只来自手写 random walk，也可以来自冻结 3D flow/SDE sampler 的条件分布。

## 2. Typed Sparse Generative Grammar State

在深度 \(d\) 处，递归资产状态定义为：

$$
S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d).
$$

各分量含义如下。

### 2.1 Sparse support 与 latent features

\[
C_d \subseteq \{0\}\times \mathbb{Z}^3
\]

表示 Trellis2/O-Voxel/SLAT 的稀疏坐标支撑。实际实现中坐标通常写为 batch-augmented coordinate：

\[
c=(b,x,y,z), \quad b=0.
\]

几何与外观特征为：

\[
F_d:C_d\rightarrow \mathbb{R}^{q_s}\times \mathbb{R}^{q_m},
\]

其中 \(q_s\) 对应 shape-SLAT / geometry latent，\(q_m\) 对应 material / texture latent 或外观条件。若当前实验只操作 shape-SLAT，可取 \(q_m=0\) 或把 material intent 放入 \(M_d\)。

### 2.2 Symbols, anchors, fields, masks

\[
U_d=\{u_i\}_{i=1}^{n_d},\quad
u_i=(\sigma_i,\ell_i,T_i,\Omega_i,\alpha_i)
\]

是符号非终结符、typed anchors、局部 frame 和 frontier symbols 的集合。这里 \(\sigma_i\in\Sigma\) 是符号类型，如 `Tip`、`Branch`、`Frame`、`Portal`、`CrystalFace`、`Patch`、`AttractorCell`；\(\ell_i\) 是递归层级或 LOD；\(T_i\in\mathcal{T}\) 是局部到全局变换；\(\Omega_i\subseteq C_d\) 是该符号关联的局部区域；\(\alpha_i\) 是属性，如 branch radius、material tag、semantic type、growth probability。

辅助场写为：

\[
A_d=(O_d,\Gamma_d,\mathcal{F}_d,\mathcal{K}_d,\mathcal{E}_d,\mathcal{Q}_d).
\]

其中：

- \(O_d:\mathbb{Z}^3\rightarrow\{0,1\}\) 是 occupancy field；
- \(\Gamma_d\) 是 attractor field 或目标密度场；
- \(\mathcal{F}_d\) 是 frontier / tip candidate 集合；
- \(\mathcal{K}_d\) 是 connected component / adjacency / attachment graph；
- \(\mathcal{E}_d\) 是 exclusion / collision field；
- \(\mathcal{Q}_d\) 是质量或可渲染性估计，例如 attachment score、fragment risk、symmetry error。

边界和混合核写为：

\[
B_d=(\partial C_d,\{\mu_k\},\{\omega_k\}),
\]

其中 \(\mu_k:\mathbb{Z}^3\rightarrow[0,1]\) 是局部 mask，\(\omega_k\) 是 blend kernel。它们决定哪些坐标可被新 proposal 改写，哪些旧 latent 必须保持。

material/PBR 状态写为：

\[
M_d=(m_d,p_d,\chi_d),
\]

其中 \(m_d\) 是 material latent 或 texture-SLAT，\(p_d\) 是 PBR intent（base color、roughness、metallic、alpha 等），\(\chi_d\) 是 prompt/category/style condition。

历史与缓存索引写为：

\[
H_d=(d,\xi_d,\mathcal{T}_{0:d},\mathcal{R}_{0:d},\lambda_d,\kappa_d),
\]

包括深度、随机种子、parent-child trace、已用 rule 序列、projection 参数、cache ids、LOD schedule 和 diagnostics。

## 3. Grammar 定义

定义递归生成语法：

$$
G=(\Sigma,\mathcal{T},R,I,P,N_\theta,\Pi,\mathrm{Caches}).
$$

其中：

- \(\Sigma\)：typed symbol alphabet，包括 terminal / nonterminal / anchor / frontier / material symbols。
- \(\mathcal{T}\)（Tau）：变换群或半群，包括 translation、rotation、uniform/anisotropic scaling、mirror、portal embedding、contraction map、local frame transform、octree-level transform。半群而非群允许不可逆 projection、scale-down 和 LOD collapse。
- \(R\)：随机上下文相关重写规则集合。
- \(I\)：解释函数，把符号和规则 proposal 映射到 sparse support、features、masks 和 local frames。
- \(P=\{P_\lambda\}\)：projection family，把 raw generated state 投影到 admissible state set。
- \(N_\theta\)：冻结 Trellis2 flow/SDE/texture naturalization sampler。
- \(\Pi\)：竞争、拓扑、连接、排斥、对称和 equivariance 约束。
- \(\mathrm{Caches}\)：motif cache、latent cache、transform cache、LOD cache、KV/sampler cache、window cache。

### 3.1 Admissible states

设可接受状态空间为：

\[
\mathcal{S}_{\mathrm{adm}}=\{S:\; \mathcal{V}_{\mathrm{topo}}(S)\leq \epsilon_t,\;
\mathcal{V}_{\mathrm{occ}}(S)\leq \epsilon_o,\;
\mathcal{V}_{\mathrm{sym}}(S)\leq \epsilon_g,\;
|C(S)|\leq T_{\max}\}.
\]

这里 \(\mathcal{V}_{\mathrm{topo}}\) 可包含 disconnected fragment mass、attachment violations、largest-component ratio loss；\(\mathcal{V}_{\mathrm{occ}}\) 是 occupancy/collision 违例；\(\mathcal{V}_{\mathrm{sym}}\) 是 group action 下的 symmetry/equivariance error；\(T_{\max}\) 是 sparse token budget。

Projection 不是后处理，而是递归映射的一部分：

\[
P_\lambda:\mathcal{S}_{\mathrm{raw}}\rightarrow\mathcal{S}_{\mathrm{adm}}.
\]

## 4. Rule Format

一个规则写为：

$$
r:\;X_i(\mathrm{frame},s,\tau,\mathrm{type},d,\mathrm{attr})
\rightarrow
\left\{
(X_j,T_j,\mu_j,\rho_j,\psi_j,\zeta_j,\beta_j,\pi_j)
\right\}_{j=1}^{m}.
$$

其中：

- \(X_i,X_j\in\Sigma\) 是输入/输出 symbol type；
- \(T_j\in\mathcal{T}\) 是局部变换；
- \(\mu_j\) 是 proposal mask；
- \(\rho_j\) 是 proposal generator，可由复制、分裂、吸附、frontier sampling 或 \(N_\theta\) 给出；
- \(\psi_j\) 是 context condition，例如 attractor、material type、depth、camera、symmetry group；
- \(\zeta_j\) 是随机变量或 sampler seed；
- \(\beta_j\) 是 blend kernel；
- \(\pi_j\in\Pi\) 是局部约束。

规则的触发概率是 context-sensitive 的：

\[
\Pr(r\mid S_d,u_i)=
\frac{\exp a_r(S_d,u_i)}{\sum_{r'\in R(u_i)}\exp a_{r'}(S_d,u_i)},
\]

其中 \(a_r\) 可以由手写 grammar score、frontier score、attractor coverage、depth schedule 或实验中的 deterministic operator 选择给定。当前代码中的 `continue`、`fork`、`side`、`radial`、`echo`、`mirror`、`translate_x/y`、`rotate_z`、`scale_up/down`、`radial4`、`portal`、`compete`、`compete_fork` 等均可视为 \(R\) 的具体实例。

## 5. Rule Semantics

P-RSLG 的一个 rule application 不是简单 copy-paste，而是以下复合算子：

$$
S_{d+1}
=
\mathcal{C}_{d+1}\circ E\circ P_\lambda\circ
N_{\theta,\Omega}^{\eta\rightarrow 0}\circ
\Theta_\Pi\circ
\operatorname{Merge}_B\circ
\operatorname{Prop}_r(S_d).
$$

为了避免歧义，下面逐项定义。

### 5.1 Proposal

对被选中的 symbol \(u_i\)，规则 \(r\) 产生若干候选：

\[
\mathcal{P}_r(S_d,u_i)=
\{(\hat{C}_{j},\hat{F}_{j},\hat{U}_{j},\hat{A}_{j},\mu_j,\beta_j,\pi_j)\}_{j=1}^{m}.
\]

最常见的 transform-copy proposal 为：

\[
\hat{C}_{j}=Q_{\mathbb{Z}^3}\big(T_j(C_d\cap\Omega_i)\big),
\qquad
\hat{F}_{j}(T_jc)=\mathcal{T}^{F}_{j}F_d(c),
\]

其中 \(Q_{\mathbb{Z}^3}\) 是坐标量化，\(\mathcal{T}^{F}_{j}\) 是 feature transport。现有实现中很多 operator 近似采用 identity feature transport，即复制 sparse features 并变换 coords。

竞争式生长 proposal 可写为：

\[
\hat{C}_{\mathrm{new}}=
\left\{
c+\Delta(c): c\in\mathcal{F}_d,\;
O_d(c+\Delta(c))=0,\;
\rho(c+\Delta(c);A_d)>\eta
\right\},
\]

\[
\Delta(c)=
Q\left(
\epsilon \frac{\bar{a}(c)-c}{\|\bar{a}(c)-c\|+\delta}
\right),
\]

其中 \(\bar{a}(c)\) 是分配给 frontier \(c\) 的 attractor 均值。代码中的 `compete_grow` 即是该类方法的简化版本：选 tip/frontier，构造 shell attractors，按最近 tip 分配，向平均 attractor 方向增长，并用 sparse occupancy 排除重复坐标。

### 5.2 Sparse merge

多个 proposal 与旧状态合并：

\[
(C^+,F^+)=\operatorname{Merge}_B
\left((C_d,F_d),\{(\hat{C}_j,\hat{F}_j,\mu_j,\beta_j)\}_{j=1}^{m}\right).
\]

坐标支撑为：

\[
C^+=C_d\cup\bigcup_j \hat{C}_j.
\]

对重复坐标 \(c\)，可采用 mask/blend 加权：

\[
F^+(c)=
\frac{
w_0(c)F_d(c)+\sum_j w_j(c)\hat{F}_j(c)
}{
w_0(c)+\sum_j w_j(c)+\epsilon
},
\quad
w_j(c)=\mu_j(c)\beta_j(c).
\]

现有 `sparse_merge` 使用 duplicate-coordinate averaging，可视为上式的均匀权重特例。

### 5.3 Competition and thinning

合并后执行稀疏竞争、topology thinning 和排斥：

\[
\Theta_\Pi(S)=
\arg\max_{S'\subseteq S}
\left[
Q_{\mathrm{grow}}(S';A_d)
-\lambda_{\mathrm{col}}V_{\mathrm{col}}(S')
-\lambda_{\mathrm{frag}}V_{\mathrm{frag}}(S')
-\lambda_{\mathrm{sym}}V_{\mathrm{sym}}(S')
\right].
\]

具体可近似为局部贪心选择：

\[
c\in C_{\mathrm{keep}}
\Longleftrightarrow
O_d(c)=0,\quad
\operatorname{dist}(c,C_d)\leq r_{\mathrm{attach}},\quad
q(c)>\eta_q.
\]

该步骤把 space competition、frontier exclusion、component-aware pruning 和 symmetry closure 合并进统一约束 \(\Pi\)。其作用不是美化，而是阻止 proposal 在 sparse state 内形成会继续繁殖的无连接碎片。

### 5.4 Masked stochastic naturalization

冻结的 Trellis2/flow/SDE sampler 被定义为条件自然化算子，而不是最终后处理：

\[
N_{\theta,\Omega}^{\eta\rightarrow 0}:
(C^+,F^+,U^+,A^+,B^+,M^+,H^+)\mapsto
(\bar{C},\bar{F},\bar{U},\bar{A},\bar{B},\bar{M},\bar{H}).
\]

若以 flow/SDE 形式写，局部 masked state \(Z_t=(C_t,F_t,M_t)\) 满足：

\[
dZ_t = v_\theta(Z_t,t,y,\Omega)\,dt+\sigma(t)\,dW_t,
\quad t:\eta\rightarrow 0.
\]

mask preservation 约束为：

\[
Z_t=(1-\mu_\Omega)\odot Z_{\mathrm{old}}
\;+\;
\mu_\Omega\odot Z_t^{\mathrm{sample}},
\]

或在每个 denoise step 后做 hard/soft clamp：

\[
Z_{t-\Delta t}\leftarrow
(1-\mu_\Omega)\odot Z_{\mathrm{old}}
\;+\;
\mu_\Omega\odot \Phi_{\theta,t}(Z_t,y).
\]

因此，随机生长不必来自手写 Brownian walk。可以改写为：

\[
\hat{F}_{\mathrm{new}}^{(k)}
\sim
p_\theta(F_{\mathrm{new}}\mid C_d,F_d,\mu_{\mathrm{new}},y,H_d),
\]

\[
k^\star=\arg\max_k Q\left(P_\lambda(D(S_{d+1}^{(k)}))\right).
\]

这说明 Trellis2 sampler 可以替代或增强传统随机生长：传统 DLA 采样的是随机游走 hitting point，而 P-RSLG 采样的是 learned 3D latent patch / material / local geometry，并由 projection 与 competition 保留满足结构约束的样本。当前实验事实是 full flow repair 容易洗掉递归 topology，因此论文主张应限制为 masked/local naturalization 的理论框架与待验证计划，而不能声称全局 flow repair 已经成功。

### 5.5 Projection

Decode、projection、re-encode 是每一层递归映射的一部分：

\[
\tilde{M}_{d+1}=D(\bar{S}_{d+1}),
\quad
M_{d+1}^{\star}=P_\lambda(\tilde{M}_{d+1};A_d,H_d),
\quad
S_{d+1}=E(M_{d+1}^{\star}).
\]

其中 \(D\) 是 Trellis2 shape decoder，\(E\) 是 mesh/O-Voxel/SLAT encoder。Projection 可包含 largest attached component selection、component score threshold、boundary trimming、hole/sheet rejection、attachment-preserving pruning、symmetry projection 等。

可写为优化问题：

\[
P_\lambda(M)=
\arg\min_{M'\in\mathcal{M}_{\mathrm{adm}}}
d_{\mathrm{geom}}(M',M)
\;+\;\lambda_1V_{\mathrm{frag}}(M')
\;+\;\lambda_2V_{\mathrm{attach}}(M')
\;+\;\lambda_3V_{\mathrm{render}}(M').
\]

当前已工作的 per-depth pipeline 对应：

\[
S_{d+1}=E\circ P_\lambda\circ D\circ G_\phi(S_d),
\]

而不是：

\[
S_D^{\mathrm{bad}}=
P_\lambda\circ D\circ G_\phi^D(S_0).
\]

两者的区别是本文理论贡献的关键。

### 5.6 Cache update

更新 cache：

\[
\mathrm{Caches}_{d+1}
=
\mathcal{U}_{\mathrm{cache}}(\mathrm{Caches}_d,S_{d+1},r_d,H_d).
\]

可缓存对象包括：

- **Motif cache**：常用 motif 的 mesh、support、features、frame；
- **Latent cache**：\((C,F)\) blocks，供 transform-copy 直接复用；
- **Transform cache**：\((T,C,F)\) 的已量化结果，减少重复坐标变换；
- **LOD cache**：低分辨率/低 token 版本，服务小尺度递归；
- **Window cache**：滑动窗口内的局部 decode/projection/re-encode 结果；
- **Sampler cache**：局部条件、KV 或 noise schedule 的复用。

Cache 使理论上的无限递归可实现为有限内存 stream，而不是一次性维护无界 sparse state。

## 6. Classical Procedural Systems as Special Cases

本节给出覆盖证明草图。严格证明不是要说明 P-RSLG 优于所有传统方法，而是说明它的规则空间足够表达这些经典程序建模系统，并能在必要时退化为它们。

### 6.1 IFS

经典 IFS 定义为一组收缩映射 \(f_i:X\rightarrow X\)，迭代：

\[
A_{k+1}=\bigcup_{i=1}^{m}f_i(A_k).
\]

令 P-RSLG 中 \(\Sigma=\{A\}\)，\(U_d=\{A\}\)，\(\mathcal{T}=\{f_i\}_{i=1}^{m}\)，\(N_\theta=\mathrm{Id}\)，\(P_\lambda=\mathrm{Id}\)，\(\Pi=\emptyset\)，feature transport 为 identity，Merge 为集合并。规则：

\[
A\rightarrow \{(A,f_i,1,\rho_i,\top,0,1,\emptyset)\}_{i=1}^{m}
\]

则：

\[
C_{d+1}=\bigcup_i Q_{\mathbb{Z}^3}(f_i(C_d)).
\]

当量化步长趋于 0 或在连续 support 中表述时，这正是 Hutchinson iteration。因此 IFS 是 P-RSLG 的 \(N_\theta,P,\Pi\) 退化特例。

### 6.2 L-system

L-system 是字符串重写：

\[
\omega_{d+1}=\mathcal{L}(\omega_d),\quad
a\mapsto w_a.
\]

在 P-RSLG 中，把字符串符号看作 ordered typed anchors：

\[
U_d=\{(\sigma_i,T_i,\ell_i,\alpha_i)\}_{i=1}^{n_d}.
\]

L-system 规则 \(a\mapsto b_1\cdots b_m\) 对应：

\[
(\sigma_i=a,T_i)\rightarrow
\{(\sigma_{ij}=b_j,T_i\Delta T_j,\mu_j,\rho_j,\top,0,\beta_j,\emptyset)\}_{j=1}^{m}.
\]

Turtle interpretation 是 \(I\) 的特例：

\[
I(\sigma_i,T_i)=\text{cylinder/curve/voxel patch in local frame }T_i.
\]

若 \(N_\theta=\mathrm{Id}\)，\(P_\lambda=\mathrm{Id}\)，并用 curve/tube decoder 替代 Trellis2 decoder，则恢复标准 L-system plant/tree 生成。若保留 \(N_\theta\) 和 projection，则得到 learned sparse-latent L-system。

### 6.3 Space colonization

Runions-style space colonization 包含吸引点集合 \(A\)、生长 tips \(B\)、最近 tip 分配、沿吸引点均值方向延伸、删除被覆盖吸引点。P-RSLG 中令：

\[
\Gamma_d=\{a_k\}_{k=1}^{K},\quad \mathcal{F}_d=\{b_i\}_{i=1}^{n}.
\]

分配：

\[
\mathcal{A}(b_i)=\{a_k:\; i=\arg\min_j \|a_k-b_j\|\}.
\]

生长方向：

\[
v_i=
\frac{\sum_{a\in\mathcal{A}(b_i)}(a-b_i)/(\|a-b_i\|+\epsilon)}
{\left\|\sum_{a\in\mathcal{A}(b_i)}(a-b_i)/(\|a-b_i\|+\epsilon)\right\|+\epsilon}.
\]

新 tip：

\[
b_i'=b_i+\delta v_i,\quad
b_i'\notin O_d.
\]

这正是第 5.1 节 competition proposal 的一个实例。occupancy exclusion \(O_d(b_i')=0\)、frontier attachment 和 attractor deletion 分别由 \(A_d,\Pi,H_d\) 维护。当前实现中的 `compete_grow` 已经是该类规则的简化可运行版本。

### 6.4 DLA / frontier accretion

经典 DLA 可写为粒子随机游走直到命中已有 cluster frontier：

\[
\tau=\inf\{t:\operatorname{dist}(W_t,C_d)\leq 1\},
\quad
C_{d+1}=C_d\cup\{W_\tau\}.
\]

P-RSLG 中令 \(\mathcal{F}_d=\partial C_d\)，proposal distribution 为 hitting distribution 的离散近似：

\[
c_{\mathrm{new}}\sim p_{\mathrm{hit}}(c\mid \partial C_d),\quad
c_{\mathrm{new}}\notin C_d,\quad
\operatorname{dist}(c_{\mathrm{new}},C_d)=1.
\]

规则为 frontier attach：

\[
\mathrm{Frontier}\rightarrow
(\mathrm{Frontier},I,c_{\mathrm{new}},\rho_{\mathrm{hit}},\psi,\zeta,\beta,\pi_{\mathrm{attach}}).
\]

当 \(N_\theta=\mathrm{Id}\) 时恢复 DLA/晶体聚集；当 \(N_\theta\) 为 masked sampler 时，hitting point 只决定结构 scaffold，新坐标的 feature/material 可由 learned distribution 采样。当前 DLA/porous 实验属于数值可跑但视觉较弱，应在论文中作为 stress-test 或待改进方向，而非强主图贡献。

### 6.5 Shape grammar / CGA

Shape grammar 中的 split、extrude、replace、subdivide、scope transform 可以写成 frame/mask 上的 contextual rewrite：

\[
X(\Omega,T,\alpha)\rightarrow
\{X_j(\Omega_j,T\Delta T_j,\alpha_j)\}_{j=1}^{m},
\quad
\Omega_j\subseteq \Omega.
\]

在 P-RSLG 中，\(\Omega_j\) 是 sparse mask 或 decoded mesh region；\(T\Delta T_j\) 是 scope transform；\(\rho_j\) 可以产生 wall/window/portal/arch 等 patch；\(P_\lambda\) 保证 split 后组件仍附着并可 re-encode。`portal`、`translate`、`scale_down`、建筑/arch/island-city proxy 都应放在这一类解释中。

### 6.6 Symmetry, crystal, equivariance

设 \(G_s\) 是一个有限 symmetry group，如 \(C_n\)、dihedral group、mirror group、crystal translation group。若规则集和 projection 满足：

\[
\forall g\in G_s,\; r\in R,\quad g\circ r\circ g^{-1}\in R,
\]

\[
P_\lambda(gS)=gP_\lambda(S),
\]

且自然化近似 equivariant：

\[
d(N_\theta(gS),gN_\theta(S))\leq \epsilon_N,
\]

则一层递归算子 \(\mathcal{T}_G\) 满足：

\[
d(\mathcal{T}_G(gS),g\mathcal{T}_G(S))
\leq
\epsilon_P+\epsilon_N+\epsilon_Q.
\]

若初始状态 \(S_0\) 是 \(G_s\)-invariant，则：

\[
d(S_d,gS_d)\leq
d(\mathcal{T}_G^d(S_0),g\mathcal{T}_G^d(S_0))
\leq
O(d(\epsilon_P+\epsilon_N+\epsilon_Q))
\]

在无误差或 contraction 条件下可得到严格不变性。这里 \(\epsilon_Q\) 是坐标量化和 sparse merge 引入的误差。该命题为 radial4、mirror、crystal/crown 类实验提供理论解释，同时也说明为什么 rotation/radial 类结果若碎片多，需要报告 symmetry error 与 projection tolerance，而不能只展示图像。

## 7. Projection Stability

### 7.1 假设

把 decoded mesh 或 sparse support 的坏碎片质量记为：

\[
e(S)=\frac{\operatorname{mass}(C_{\mathrm{bad}}(S))}
{\operatorname{mass}(C(S))+\epsilon}.
\]

这里 \(C_{\mathrm{bad}}\) 指不满足 attachment、component、occupancy 或 renderability 条件的支撑。作如下假设。

**A1. 有界 proposal 噪声。** 每层 raw grammar proposal 至多产生 \(\eta_d\) 的新坏碎片：

\[
e(\operatorname{Merge}\circ\operatorname{Prop}_r(S_d))
\leq
\alpha e(S_d)+\eta_d,
\]

其中 \(\alpha\geq 1\) 表示已有碎片在下一层继续繁殖的放大系数。

**A2. Projection 保持主结构。** 对 admissible main component \(C_{\mathrm{main}}\)，projection 的几何扰动有界：

\[
d_{\mathrm{geom}}(P_\lambda(S),S_{\mathrm{main}})\leq \delta_P.
\]

**A3. Projection 抑制坏碎片。** 对任意 raw state：

\[
e(P_\lambda(S))\leq \epsilon_P.
\]

**A4. Re-encode 稳定。** Trellis2 re-encode 对 projected mesh 的支撑误差有界：

\[
d(E(P_\lambda(D(S))),P_\lambda(D(S)))\leq \delta_E.
\]

### 7.2 命题：per-depth projection 抑制碎片误差传播

若每一层都执行：

\[
S_{d+1}=E\circ P_\lambda\circ D\circ \mathcal{G}_r(S_d),
\]

且 A1-A4 成立，则：

\[
e(S_d)\leq \epsilon_P+\epsilon_E
\quad \forall d\leq D,
\]

其中 \(\epsilon_E\) 是 re-encode/decode 误差对应的坏碎片上界。也就是说，坏碎片比例不随递归深度指数增长，而被每层 projection 重置到阈值附近。

相反，如果只在最终执行一次 projection：

\[
\bar{S}_{d+1}=\mathcal{G}_r(\bar{S}_d),
\quad
S_D=P_\lambda(D(\bar{S}_D)),
\]

则由 A1 得：

\[
e(\bar{S}_D)
\leq
\alpha^D e(S_0)+
\sum_{k=0}^{D-1}\alpha^{D-1-k}\eta_k.
\]

当 \(\alpha>1\) 时，即使最终 cleanup 能删除一部分碎片，碎片已经在中间层作为新的 parent/frontier 参与了生长、遮挡、竞争和 naturalization，导致结构语义、local features、material intent 与主组件混合。最终 cleanup 只能删除几何残余，不能撤销中间层错误对后续 proposal 分布的影响。

### 7.3 为什么 per-depth projection 比 final cleanup 更合理

递归系统与一次性生成不同：第 \(d\) 层的输出是第 \(d+1\) 层的 root state。漂浮碎片、错误组件和边界破洞如果不在当前层处理，会被下一层 rule 当作合法 frontier、anchor 或 patch source，并产生子结构。于是错误不只是加性噪声，而会变成新的递归生产源。

Per-depth projection 的图形学意义是把每层状态重新投影到可解释的 shape manifold / sparse-latent grammar manifold：

\[
\mathcal{S}_{\mathrm{adm}}
\xrightarrow{\mathcal{G}_r}
\mathcal{S}_{\mathrm{raw}}
\xrightarrow{P_\lambda}
\mathcal{S}_{\mathrm{adm}}.
\]

这与物理仿真中的 time-step constraint projection 类似：约束必须在每步积分后施加，而不是等整段模拟结束后修补。当前实验中 `vine_d5_projected_compete`、`tree_projected_compete`、`porous_container_compete`、`ruin_arch_portal`、`island_city_scale_down` 的 component reduction 和 largest-component ratio 结果，是该命题的初步经验支持。

## 8. Trellis2 / Flow / SDE Sampler 在框架中的位置

P-RSLG 中 Trellis2 不是最终美化器，而是三个算子的实现基础。

### 8.1 Native sparse substrate

Trellis2 O-Voxel/SLAT 提供 sparse 3D coordinate support \(C_d\) 和 latent features \(F_d\)。这使递归规则能直接表达坐标变换、occupancy exclusion、frontier selection、component projection 和 re-encode loop。传统程序建模通常直接生成 mesh；现代 one-shot 3D generator 通常不暴露可反复改写的 sparse 3D grammar state。P-RSLG 的关键是把 learned sparse state 变成程序语法的状态空间。

### 8.2 Naturalization distribution

冻结 sampler 定义条件分布：

\[
p_\theta(S_{\Omega}^{\mathrm{nat}}\mid
S_{\bar{\Omega}},\mu_\Omega,y,H_d).
\]

语法给出 scaffold 和 mask，sampler 在局部生成更自然的 shape/material latent。这样，传统 stochastic growth 中的 random direction、random walk、random branching probability 可以被 learned local latent proposal 替代或增强：

\[
\rho_{\mathrm{classic}}(c)
\quad\leadsto\quad
\rho_\theta(C_\Omega,F_\Omega,M_\Omega\mid S_d,y).
\]

### 8.3 Projection-aware sampling

因为 \(N_\theta\) 可能破坏 topology，所以 sampler 的正确使用方式是 projection-aware：

\[
S_{d+1}^{(k)}
=
E\circ P_\lambda\circ D\circ
N_{\theta,\Omega}^{(k)}\circ\Theta_\Pi\circ\operatorname{Merge}\circ\operatorname{Prop}_r(S_d),
\]

\[
k^\star=\arg\max_k
\left[
Q_{\mathrm{conn}}(S_{d+1}^{(k)})
+Q_{\mathrm{attach}}(S_{d+1}^{(k)})
+Q_{\mathrm{render}}(S_{d+1}^{(k)})
-Q_{\mathrm{drift}}(S_{d+1}^{(k)},S_d)
\right].
\]

该公式把 flow/SDE 随机性变成 grammar 内部的候选生成机制，而不是把 flow 作为一次全局 repair。已有负结果显示 full flow repair 会 wash out recursive topology；因此本文应主张“masked stochastic naturalization 是理论上正确且待实验强化的路径”，并把已验证贡献放在 mesh-first sparse grammar + per-depth projection。

## 9. Infinite Recursion, LOD, and Cache

无限递归需要谨慎表述：系统输出有限深度资产，但 rule program 可以定义无界逻辑深度。理论上限与可实现路径如下。

### 9.1 Contractive recursion

若每个递归变换 \(T_i\) 是收缩映射：

\[
\|T_i x-T_i y\|\leq s_i\|x-y\|,
\quad 0<s_i<1,
\]

且 \(\sum_i s_i^p<\infty\)，则连续极限支撑可定义为 IFS attractor。有限分辨率 sparse grid 中，当尺度低于 voxel size 或 LOD threshold \(\epsilon_{\mathrm{lod}}\) 时，后续递归可由 cache motif 或 material/detail shader 近似：

\[
d_{\mathrm{screen}}(T_{0:k}\Omega)<\epsilon_{\mathrm{px}}
\Longrightarrow
\mathrm{UseCache}(T_{0:k},\mathrm{LOD}_k).
\]

### 9.2 Token-budgeted LOD scheduling

令 \(n_d=|C_d|\)。没有压缩时，branching factor \(b\) 会导致：

\[
n_d=O(b^d n_0).
\]

引入 LOD collapse 和 cache 后，可要求：

\[
\sum_{\Omega\in\mathcal{W}_d}|C_\Omega^{\mathrm{active}}|
\leq T_{\max},
\]

其中 \(\mathcal{W}_d\) 是当前视窗或可见尺度集合。小尺度区域不再展开为完整 token，而是记录为：

\[
(\mathrm{cache\_id},T,\ell,\mathrm{material\_intent},\mathrm{error\_bound}).
\]

### 9.3 Sliding-window recursion

无限场景或 infinite-zoom proxy 可维护有限活动窗口：

\[
S_d^{\mathrm{stream}}=
(S_d^{\mathrm{active}},\mathcal{B}_d^{\mathrm{baked}},\mathrm{Caches}_d),
\]

其中 \(S_d^{\mathrm{active}}\) 在窗口内可 decode/project/re-encode，\(\mathcal{B}_d^{\mathrm{baked}}\) 是已烘焙 mesh/GLB chunk 或低阶 proxy。窗口移动时：

\[
S_{d+1}^{\mathrm{active}}
=
\operatorname{LoadCache}(\mathcal{W}_{d+1})
\cup
\operatorname{GenerateMissing}(\mathcal{W}_{d+1}).
\]

因此，逻辑深度可以无界，但实际内存由窗口大小、LOD 和 cache 控制。当前项目尚未证明该路径，只能写作 future work / theoretical extension / diagnostic plan，不能写成已经完成的 claim。

## 10. 已有实验支持与计划/假说边界

### 10.1 已有实验支持的 claim

1. **Mesh-first Trellis2 O-Voxel/shape-SLAT encode/decode 可作为递归状态入口。** 代码已实现 mesh to flexible dual grid、shape-SLAT encode、sparse grammar operator、decode mesh 的 workflow。
2. **Per-depth projection loop 是当前最强稳定器。** 多个案例显示 raw recursive output 组件多，projection 后 largest-component ratio 明显提高，并能继续 re-encode。
3. **`compete`/space competition 是目前最稳的 sparse growth operator。** 它利用 frontier、attractor-like shell、occupancy exclusion，在 vine/tree/porous 等案例中稳定性强于许多 naive transform-copy。
4. **Transform-copy/portal/scale/mirror 能覆盖非树类别，但质量不均。** crown、scifi、architecture、ruin arch、island city 等证明系统不局限于植物；但碎片、孔洞、暗材质和视角依赖仍明显。
5. **Trellis2 texture/GLB export 技术上跑通。** 多个 projected recursive mesh 可进入 texturing pipeline 并导出 textured GLB；但视觉/PBR 质量类别依赖强。

### 10.2 只能作为计划或假说的 claim

1. **Masked flow/SDE naturalization 能显著提升局部质量。** 理论上成立，当前 full flow repair 负结果提示必须局部化、mask 化、projection-aware；尚缺强实验。
2. **Learned sampler 可替代传统 stochastic growth。** 公式上可作为 \(\rho_\theta\) proposal distribution，但需 grid sweep 和 ablation 证明。
3. **Infinite recursion / sliding-window / cache streaming。** 有清晰理论路径，但当前未实现完整 demo。
4. **严格 symmetry/crystal equivariance。** 需要 symmetry error metric 和 \(C_n\)/mirror/crystal 实验支持；当前只能写 proof sketch 和实验计划。
5. **Camera-aware Escher/impossible recursion。** `portal`/`scale_down`/`island_city` 是 proxy，不等于解决视错觉场景生成。

## 11. 可直接搬进论文的方法节结构

### 3. Problem Definition

定义任务：给定 root asset、递归 grammar、深度预算和冻结 3D generator，生成有限深度的递归 3D asset。强调输出是 potentially infinite recursive program 的 finite realization。给出 \(S_0,\ldots,S_D\) 和 render/export 目标。

### 4. Projection-Stabilized Recursive Sparse-Latent Grammar

#### 4.1 Typed Sparse State

引入：

\[
S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d).
\]

逐项解释 sparse coordinates、latent features、symbols/anchors/frontiers、occupancy/attractor/component fields、boundary masks、material/PBR intent、history/cache ids。

#### 4.2 Grammar and Rule Language

定义：

\[
G=(\Sigma,\mathcal{T},R,I,P,N_\theta,\Pi,\mathrm{Caches}).
\]

给出 rule：

\[
r:X_i(\mathrm{frame},s,\tau,\mathrm{type},d,\mathrm{attr})
\rightarrow
\{(X_j,T_j,\mu_j,\rho_j,\psi_j,\zeta_j,\beta_j,\pi_j)\}_j.
\]

说明当前 operators 如何映射到 rule families：branching、competition、frontier accretion、transform-copy、portal/shape grammar、symmetry。

#### 4.3 Rule Semantics

给出总算子：

\[
S_{d+1}
=
\mathcal{C}_{d+1}\circ E\circ P_\lambda\circ
N_{\theta,\Omega}^{\eta\rightarrow 0}\circ
\Theta_\Pi\circ
\operatorname{Merge}_B\circ
\operatorname{Prop}_r(S_d).
\]

分段解释 proposal、sparse merge、competition/thinning、masked stochastic naturalization、projection、re-encode、cache update。

#### 4.4 Projection-Stabilized Recursion

写核心 loop：

\[
S_{d+1}=E\circ P_\lambda\circ D\circ G_\phi(S_d).
\]

对比 final-only cleanup：

\[
S_D^{\mathrm{final}}=P_\lambda\circ D\circ G_\phi^D(S_0).
\]

给出命题：在有界 proposal 噪声、projection 抑制坏碎片、re-encode 稳定假设下，per-depth projection 将 fragment error 控制在阈值附近，而 final-only cleanup 会允许错误以 \(\alpha^d\) 传播。

#### 4.5 Relation to Classical Procedural Grammars

用一段或一个表证明 P-RSLG 覆盖 IFS、L-system、space colonization、DLA/frontier accretion、shape grammar、symmetry/crystal。关键写法是“当 \(N_\theta\)、\(P_\lambda\)、\(\Pi\) 退化为 identity/empty 时恢复经典方法；保留它们时得到 learned sparse-latent generative extension”。

#### 4.6 Trellis2 Naturalization and Appearance

把 Trellis2 写成 native sparse substrate + masked stochastic naturalizer + texture/PBR exporter。明确 full flow repair 当前不是主贡献；主张局部 masked naturalization 和 projection-aware sampling 是计划中的增强路径。

#### 4.7 Infinite Recursion and LOD Extension

谨慎写作：本文生成有限深度资产，但 grammar 可定义无限逻辑深度。给出 contractive transforms、LOD cache、sliding-window recursion 的公式和未来实现路径。

#### 4.8 Implementation Notes

简述 mesh-first encode、sparse grammar operators、decode/project/re-encode、texturing/export。避免把实现写成主贡献，但说明系统确实可运行，并为 experiments 中的 ablation 提供对应关系。
