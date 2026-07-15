# Projection-Stabilized Recursive Sparse-Latent Grammar 证明包

创建时间：2026-05-08  
写作范围：本文只整理理论证明支线，不修改论文主文、已有 formal doc 或实验文档。  
对应框架：`formal_recursive_generative_grammar_zh_20260508.md` 中的 P-RSLG。

## 0. 总体结论

本文把 P-RSLG 中可证明的内容与当前不能诚实证明的内容分开。

可进入论文主文的强度应限制为：

1. 在明确退化设定下，P-RSLG 的规则语言可以表达 IFS、L-system、space-colonization、DLA/frontier accretion、有限 shape grammar、有限 symmetry transform-copy 等经典 procedural families。
2. 在有界坏碎片生成、projection 碎片抑制、decode/encode 稳定等假设下，per-depth projection 可以把每层状态的坏碎片比例重置到阈值附近。
3. Symmetry/equivariance 只能声明为近似交换误差界，且必须假设 sampler、projection、merge、量化都与群作用近似交换。
4. Infinite recursion 只能写成有限可见窗口、LOD/cache streaming，或 contractive transform 下的极限对象；不能声称当前系统已经实现或证明了无界三维资产生成。

不能进入主文强 claim 的内容：

- “P-RSLG 严格优于所有传统 procedural systems”没有理论证明。
- “Trellis2/flow/SDE 必然稳定递归 topology”当前不成立；full flow repair 的负结果反而提示必须局部 mask 化。
- “严格 symmetry/crystal equivariance”除非 sampler/projection 的交换条件被实验证明或构造保证，否则不能声明。
- “已实现无限递归”当前只能作为 LOD/cache extension 或 future work。

## 1. 统一记号

令深度 $d$ 的状态为

$$
S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d),
$$

其中 $C_d$ 是 sparse 3D support，$F_d$ 是 latent feature，$U_d$ 是 typed symbols/anchors/frontiers，$A_d$ 是 occupancy、attractor、component、frontier 等辅助场，$B_d$ 是 mask/blend/boundary 信息，$M_d$ 是 material/PBR 或 projection metadata，$H_d$ 是 history/cache。

令语法为

$$
G=(\Sigma,\mathcal{T},R,I,P,N_\theta,\Pi,\mathrm{Caches}).
$$

一层递归算子抽象为

$$
\mathcal{A}_d
=
\mathcal{C}_{d+1}\circ E\circ P_{\lambda_d}\circ
N_{\theta,\Omega_d}\circ
\Theta_{\Pi_d}\circ
\operatorname{Merge}_{B_d}\circ
\operatorname{Prop}_{r_d}.
$$

于是

$$
S_{d+1}=\mathcal{A}_d(S_d).
$$

若禁用 learned sampler、projection、competition 与 cache，可取

$$
N_{\theta,\Omega}=\mathrm{Id},\quad
P_\lambda=\mathrm{Id},\quad
\Theta_\Pi=\mathrm{Id},\quad
\mathcal{C}=\mathrm{Id}.
$$

本文中的“覆盖”只表示可表达性，即存在 P-RSLG 的一个退化或受限实例，其状态转移等于或近似等于经典系统的状态转移；不表示性能优越性。

## 2. 依赖图

1. 命题 1-6 只依赖 P-RSLG 的符号、规则、解释函数、merge 与可退化算子定义。
2. 命题 7 依赖坏碎片度量 $e$、projection 抑制假设、codec 稳定假设与有限深度 $D$。
3. 命题 8 依赖群作用 $g$ 对状态空间的定义、规则闭包、sampler/projection/merge/codec 的近似交换误差。
4. 命题 9 依赖 visible window budget 与每窗口局部展开策略。
5. 命题 10 依赖 contractive transform 的标准 IFS/Hutchinson 极限条件；在离散 sparse grid 上只给有限分辨率近似命题。

## 3. 经典系统覆盖命题

### 命题 1：IFS 覆盖

**Status: PROVABLE AS STATED**

**校正命题。** 设经典 IFS 在连续紧致度量空间 $(X,d_X)$ 上由有限个映射

$$
f_i:X\rightarrow X,\quad i=1,\ldots,m
$$

给出，状态转移为

$$
A_{k+1}=\bigcup_{i=1}^m f_i(A_k).
$$

若 P-RSLG 使用连续 support $C_d\subset X$，取

$$
\Sigma=\{A\},\quad
\mathcal{T}=\{f_i\}_{i=1}^m,\quad
N_\theta=P_\lambda=\Theta_\Pi=\mathcal{C}=\mathrm{Id},
$$

解释函数只把符号 $A$ 解释为当前 support，feature transport 为 identity，merge 为集合并，则存在规则集 $R$ 使得 P-RSLG 的 support 转移满足

$$
C_{d+1}=\bigcup_{i=1}^m f_i(C_d).
$$

因此该 P-RSLG 实例与 IFS 的有限步迭代完全一致。

**证明。** 构造唯一规则

$$
A\rightarrow \{(A,f_i,1,\rho_i,\top,0,1,\emptyset)\}_{i=1}^m.
$$

对状态 $C_d$ 应用 proposal 得到候选

$$
\hat C_i=f_i(C_d),\quad i=1,\ldots,m.
$$

由于 $N_\theta$、$P_\lambda$、$\Theta_\Pi$ 与 cache update 都取 identity，且 merge 是集合并，所以

$$
C_{d+1}
=
\operatorname{Merge}(\hat C_1,\ldots,\hat C_m)
=
\bigcup_{i=1}^m f_i(C_d).
$$

这正是 IFS 迭代。证毕。

**边界。** 若使用离散 voxel grid 与量化算子 $Q_h$，则只能得到

$$
C_{d+1}^{(h)}=\bigcup_i Q_h(f_i(C_d^{(h)})),
$$

这是量化 IFS，不是连续 IFS 的严格相等版本。连续 claim 需要在连续 support 中表述，或把误差写成随 grid size $h$ 变化的近似。

### 命题 2：L-system 覆盖

**Status: PROVABLE AS STATED**

**校正命题。** 对一个确定性上下文无关 L-system

$$
\mathcal{L}=(V,\omega_0,\{a\mapsto w_a\}_{a\in V}),
$$

其字符串迭代为

$$
\omega_{d+1}=\mathcal{L}(\omega_d).
$$

若 P-RSLG 的 $U_d$ 是有序 typed anchor 序列，且解释函数 $I$ 保留该顺序，则存在规则集 $R$ 使得 P-RSLG 的符号序列投影等于 $\omega_d$。

**假设。**

- L-system 是有限 alphabet 上的并行重写系统。
- P-RSLG rule scheduler 对当前序列中的每个符号同步应用对应规则。
- merge 对符号序列执行稳定拼接，而不是集合去重。

**证明。** 把 $V$ 嵌入 $\Sigma$。若

$$
\omega_d=a_1a_2\cdots a_n,
$$

则令

$$
U_d=((a_1,T_1,\ell_1,\alpha_1),\ldots,(a_n,T_n,\ell_n,\alpha_n)).
$$

对每个 $a_i$ 定义 P-RSLG 规则

$$
a_i\rightarrow w_{a_i}=b_{i1}\cdots b_{im_i}.
$$

同步 rule application 后，稳定拼接给出

$$
U_{d+1}
=
(w_{a_1},w_{a_2},\ldots,w_{a_n}),
$$

因此符号投影为

$$
\pi_\Sigma(U_{d+1})
=
w_{a_1}w_{a_2}\cdots w_{a_n}
=
\mathcal{L}(\omega_d).
$$

对 $d$ 作归纳可得 $\pi_\Sigma(U_d)=\omega_d$。turtle interpretation 是 $I$ 的一个具体选择，不影响符号重写等价。证毕。

**边界。** 若 P-RSLG 使用异步 rule scheduling、随机 rule choice 或集合式 merge，则只能覆盖 stochastic/asynchronous L-system 的某个变体，不能声称等于标准同步 L-system。

### 命题 3：Space Colonization 覆盖

**Status: PROVABLE AS STATED**

**校正命题。** 设 space colonization 的一次迭代由 attractor 集合 $\Gamma_d$、tip 集合 $B_d=\{b_i\}$、最近 tip 分配、方向平均、步长 $\delta$ 与吸引点删除半径 $r_{\mathrm{kill}}$ 定义。若 P-RSLG 的辅助场 $A_d$ 显式保存 $\Gamma_d$ 与 $B_d$，proposal generator $\rho_{\mathrm{sc}}$ 执行同一最近分配和方向更新，projection 与 sampler 取 identity，则 P-RSLG 的 tip/attractor 转移与该 space-colonization 算法一致。

**证明。** 对每个 tip $b_i$ 定义分配集合

$$
\mathcal{A}(b_i)=\{a\in \Gamma_d:\ i=\arg\min_j \|a-b_j\|\}.
$$

若 $\mathcal{A}(b_i)\neq\emptyset$，定义

$$
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
$$

P-RSLG proposal generator 产生

$$
b_i'=b_i+\delta v_i
$$

并通过 occupancy exclusion 保留 $b_i'\notin O_d$ 的候选。merge 把保留的新 tip 与旧 branch graph 拼接；history update 删除满足

$$
\operatorname{dist}(a,B_{d+1})\leq r_{\mathrm{kill}}
$$

的 attractor。由于这些步骤逐项等同于 space-colonization 的算法定义，且 sampler/projection 不改变状态，故一层转移一致。归纳得到有限步一致。证毕。

**边界。** 该命题证明的是算法覆盖，不证明 P-RSLG 的 learned latent feature 或 Trellis2 decoding 会保持传统 space-colonization 的视觉质量。若启用 projection 或 sampler，则得到带修正的扩展算法，不再与经典算法严格相等。

### 命题 4：DLA / Frontier Accretion 覆盖

**Status: PROVABLE AS STATED**

**校正命题。** 离散 DLA 若定义为 cluster $C_d\subset\mathbb{Z}^3$ 与 hitting distribution

$$
c_{\mathrm{new}}\sim p_{\mathrm{hit}}(\cdot\mid C_d),
$$

其中 $c_{\mathrm{new}}\notin C_d$ 且 $\operatorname{dist}(c_{\mathrm{new}},C_d)=1$，更新为

$$
C_{d+1}=C_d\cup\{c_{\mathrm{new}}\},
$$

则存在 P-RSLG 规则使其 support Markov kernel 等于该 DLA Markov kernel。

**证明。** 令 $\mathcal{F}_d=\partial C_d$，定义 proposal distribution

$$
\rho_{\mathrm{hit}}(c\mid S_d)=p_{\mathrm{hit}}(c\mid C_d).
$$

规则 `FrontierAttach` 从 $\rho_{\mathrm{hit}}$ 采样一个 $c_{\mathrm{new}}$，并由 attachment constraint 检查

$$
c_{\mathrm{new}}\notin C_d,\quad
\operatorname{dist}(c_{\mathrm{new}},C_d)=1.
$$

merge 为集合并，因此

$$
C_{d+1}=C_d\cup\{c_{\mathrm{new}}\}.
$$

该条件分布与 DLA 的一层条件分布相同，所以二者的 Markov kernel 相同。证毕。

**边界。** 如果 $\rho_{\mathrm{hit}}$ 只是随机游走 hitting distribution 的近似，或者加入 learned sampler 改变新增 patch 的 support，则只得到 DLA-like frontier accretion，不是严格 DLA。

### 命题 5：Shape Grammar / CGA 覆盖

**Status: PROVABLE AFTER WEAKENING**

**原强说法的风险。** “P-RSLG 覆盖所有 shape grammar”过强，因为 shape grammar 可以包含无限精度几何谓词、布尔操作、全局约束或连续参数求解；当前 P-RSLG formal doc 没有为所有这些操作给出语义。

**校正命题。** 对任意有限规则、有限参数、局部 frame/mask 可表达的 split/extrude/replace/subdivide/scope-transform shape grammar，若每条规则的几何作用都可写成 P-RSLG 的

$$
X(\Omega,T,\alpha)\rightarrow
\{X_j(\Omega_j,T\Delta T_j,\alpha_j)\}_{j=1}^m,
$$

其中 $\Omega_j$ 是可枚举 sparse mask 或 mesh region，$\Delta T_j\in\mathcal{T}$，则 P-RSLG 可表达该 grammar 的有限步展开。

**证明。** 对 shape grammar 中每条规则建立同名 P-RSLG 规则：输入 symbol 为 $X$，输入 region 为 $\Omega$，输入 frame 为 $T$；输出第 $j$ 个 symbol 的 frame 为 $T\Delta T_j$，mask 为 $\Omega_j$，属性为 $\alpha_j$。解释函数 $I$ 把每个 scope patch 映射到对应 sparse support 或 decoded mesh region。若 rule scheduler 与原 shape grammar 相同，且 projection/sampler 取 identity，则每一步输出 symbol、frame 与 region 均逐项相同。归纳得到有限步展开相同。证毕。

**仍不能证明的部分。** 带全局优化、任意布尔几何、连续碰撞求解或非局部语义的 shape grammar 需要额外解释函数与可计算性假设。当前只能作为 appendix 中的“可覆盖子类”。

### 命题 6：Symmetry / Crystal Transform-Copy 覆盖

**Status: PROVABLE AFTER WEAKENING**

**原强说法的风险。** “P-RSLG 支持 symmetry/crystal”容易被误读成生成结果严格群不变或严格等变。当前系统含 sparse grid 量化、learned sampler、projection、mesh decode/re-encode，这些算子一般不严格与群作用交换。

**校正命题。** 设 $G_s$ 是有限群，作用在状态空间上。若 P-RSLG 的规则集对 $G_s$ 闭合，即

$$
\forall g\in G_s,\quad g\circ r\circ g^{-1}\in R,
$$

且当前使用的 rule scheduler 对 $G_s$ 不偏置，则在禁用 sampler/projection/codec 误差，且 merge 与群作用严格交换时，P-RSLG 的 transform-copy 递归严格等变：

$$
\mathcal{A}_d(gS)=g\mathcal{A}_d(S).
$$

若初始状态 $S_0$ 满足 $gS_0=S_0$，则所有深度满足

$$
gS_d=S_d.
$$

**证明。** 对任意规则 $r$，闭包条件保证对 $gS$ 应用规则等价于先对 $S$ 应用共轭规则再施加 $g$。scheduler 不偏置保证两侧选择的规则轨道一致。merge 与群作用严格交换，因此

$$
\operatorname{Merge}(g\hat S_1,\ldots,g\hat S_m)
=
g\operatorname{Merge}(\hat S_1,\ldots,\hat S_m).
$$

禁用 sampler/projection/codec 后，$\mathcal{A}_d$ 只由 proposal 与 merge 组成，所以 $\mathcal{A}_d(gS)=g\mathcal{A}_d(S)$。若 $S_0$ 不变，则

$$
gS_{d+1}
=g\mathcal{A}_d(S_d)
=\mathcal{A}_d(gS_d)
=\mathcal{A}_d(S_d)
=S_{d+1}.
$$

归纳得到结论。证毕。

**当前论文可写法。** 对实际 P-RSLG，应使用第 5 节的近似等变命题，而不是把本命题写成当前系统的无条件性质。

## 4. Per-depth Projection 稳定性

### 命题 7：有界坏碎片比例的弱稳定命题

**Status: PROVABLE AFTER WEAKENING**

**校正命题。** 令 $e(S)\in[0,1]$ 表示状态 $S$ 中坏碎片、无附着组件、不可渲染 support 或违反 occupancy/attachment 约束的归一化质量。考虑有限深度 $d=0,\ldots,D$ 的递归

$$
S_{d+1}=E\circ P_{\lambda_d}\circ D\circ G_d(S_d),
$$

其中

$$
G_d=\Theta_{\Pi_d}\circ
\operatorname{Merge}_{B_d}\circ
\operatorname{Prop}_{r_d}
$$

或包含满足同样误差界的 masked sampler。假设存在常数 $\epsilon_P,\epsilon_E\geq0$，使得对所有 $d<D$：

**A1. Projection 碎片抑制。**

$$
e(P_{\lambda_d}(X))\leq \epsilon_P
$$

对所有进入 projection 的 decoded state $X$ 成立。

**A2. Encode/decode 后坏碎片增量有界。**

$$
e(E(Y))\leq e(Y)+\epsilon_E
$$

对所有 projected decoded state $Y=P_{\lambda_d}(X)$ 成立。这里把 $E$ 理解为重新编码后再用于下一层的 state；若实际链路中还有一次 decode，则 $\epsilon_E$ 需要吸收该 codec loop 的误差。

**A3. 每层 projection 成功返回 admissible state。** 即 $P_{\lambda_d}(X)$ 有定义且没有返回空失败状态；若 projection 失败，应把该层标为失败而不是套用本命题。

则对所有 $1\leq d\leq D$，

$$
e(S_d)\leq \epsilon_P+\epsilon_E.
$$

**证明策略。** 直接使用每层 projection 的重置性质，而不是证明 raw proposal 不增长。

**证明。** 固定任意 $d<D$。令

$$
X_d=D\circ G_d(S_d).
$$

由 A1，

$$
e(P_{\lambda_d}(X_d))\leq \epsilon_P.
$$

再令

$$
S_{d+1}=E(P_{\lambda_d}(X_d)).
$$

由 A2，

$$
e(S_{d+1})
\leq
e(P_{\lambda_d}(X_d))+\epsilon_E
\leq
\epsilon_P+\epsilon_E.
$$

由于该推导对任意 $d<D$ 成立，结论对所有 $1\leq d\leq D$ 成立。证毕。

**重要解释。** 该命题没有证明 raw proposal 的坏碎片不会增长，也没有证明视觉质量、branch semantics 或 material consistency 随深度稳定。它只证明：在 projection 每层确实能把坏碎片比例压到 $\epsilon_P$，且 codec loop 最多增加 $\epsilon_E$ 的前提下，每个输出层的坏碎片比例被统一上界控制。

### 对 final-only cleanup 的可证明对比

**Status: PROVABLE AFTER WEAKENING**

**校正命题。** 若无 per-depth projection 的 raw recursion 满足

$$
e(\bar S_{d+1})\leq \alpha e(\bar S_d)+\eta_d,
$$

则

$$
e(\bar S_D)
\leq
\alpha^D e(\bar S_0)
+
\sum_{k=0}^{D-1}\alpha^{D-1-k}\eta_k.
$$

**证明。** 对递推式展开。$D=1$ 时成立。假设 $D$ 成立，则

$$
e(\bar S_{D+1})
\leq
\alpha e(\bar S_D)+\eta_D
\leq
\alpha^{D+1}e(\bar S_0)
+
\sum_{k=0}^{D-1}\alpha^{D-k}\eta_k
+
\eta_D,
$$

即

$$
e(\bar S_{D+1})
\leq
\alpha^{D+1}e(\bar S_0)
+
\sum_{k=0}^{D}\alpha^{D-k}\eta_k.
$$

归纳完成。证毕。

**不能过 claim 的地方。** 上式只是 raw error upper bound。它不能单独证明 final-only projection 一定失败，因为最终 $P_\lambda$ 可能仍删除几何碎片。更诚实的说法是：若中间层坏碎片会改变后续 proposal、frontier、sampler condition 或 material trace，则 final-only cleanup 不能从该递推式推出与 per-depth projection 等价。要证明“final-only 不可恢复”，还需要额外的历史依赖或不可逆污染假设，例如存在状态函数 $h(S_d)$ 进入后续 proposal 分布，且坏碎片对 $h$ 的扰动不能被最终 projection 逆转。

## 5. Symmetry / Equivariance 的近似交换命题

### 命题 8：近似等变误差界

**Status: PROVABLE AFTER WEAKENING**

**校正命题。** 设有限群 $G_s$ 作用在状态空间上，度量为 $d_{\mathcal S}$。令一层算子分解为

$$
\mathcal{A}
=
E\circ P\circ N\circ M\circ R,
$$

其中 $R$ 是 proposal/rule，$M$ 是 merge/competition，$N$ 是 sampler，$P$ 是 projection，$E$ 是 encode/re-encode。假设这些算子对任意 $g\in G_s$ 满足近似交换：

$$
d_{\mathcal S}(R(gS),gR(S))\leq \epsilon_R,
$$

$$
d_{\mathcal S}(M(gX),gM(X))\leq L_M\epsilon_X+\epsilon_M,
$$

$$
d_{\mathcal S}(N(gX),gN(X))\leq L_N\epsilon_X+\epsilon_N,
$$

$$
d_{\mathcal S}(P(gX),gP(X))\leq L_P\epsilon_X+\epsilon_P,
$$

$$
d_{\mathcal S}(E(gX),gE(X))\leq L_E\epsilon_X+\epsilon_E.
$$

这里 $\epsilon_X$ 表示输入两侧已经存在的状态差异。则一层算子满足

$$
d_{\mathcal S}(\mathcal{A}(gS),g\mathcal{A}(S))
\leq
L_E L_P L_N L_M \epsilon_R
+
L_E L_P L_N \epsilon_M
+
L_E L_P \epsilon_N
+
L_E \epsilon_P
+
\epsilon_E.
$$

**证明。** 逐个算子传播误差。令

$$
\Delta_R=d_{\mathcal S}(R(gS),gR(S))\leq\epsilon_R.
$$

应用 $M$ 的近似交换条件，得到

$$
\Delta_M\leq L_M\Delta_R+\epsilon_M.
$$

应用 $N$，

$$
\Delta_N\leq L_N\Delta_M+\epsilon_N.
$$

应用 $P$，

$$
\Delta_P\leq L_P\Delta_N+\epsilon_P.
$$

应用 $E$，

$$
\Delta_E\leq L_E\Delta_P+\epsilon_E.
$$

把前四个不等式代入最后一个不等式，得到所列界。证毕。

**多层界。** 若每层同样满足

$$
d_{\mathcal S}(\mathcal{A}_d(gS),g\mathcal{A}_d(S))
\leq
L\, d_{\mathcal S}(gS,S)+\epsilon,
$$

且 $S_0$ 严格 invariant，则

$$
d_{\mathcal S}(S_d,gS_d)
\leq
\begin{cases}
\epsilon(1-L^d)/(1-L), & L<1,\\
d\epsilon, & L=1,\\
\epsilon(L^d-1)/(L-1), & L>1.
\end{cases}
$$

因此只有在 $L<1$ 或 $d$ 有限且 $\epsilon$ 足够小的情况下，近似 symmetry error 才可控。

**风险说明。**

- Sparse coordinate quantization 通常不与任意 rotation 严格交换，尤其是非轴对齐旋转。
- Projection 如果选择 largest component，遇到两个几乎等大的 symmetric component 时可能破坏 symmetry。
- Learned sampler 若没有 group-equivariant architecture 或 group-averaged sampling，不能假设 $\epsilon_N$ 小。
- Mesh decode/re-encode 的数值误差可能对 mirror/radial 操作产生非对称 drift。

**论文写法。** 主文可写“when sampler and projection approximately commute with the group action, symmetry error is bounded by accumulated commutation errors”。不要写“our method guarantees exact equivariance”。

## 6. Infinite Recursion / LOD / Cache

### 命题 9：有界 visible window 下的有限内存递归

**Status: PROVABLE AS STATED**

**校正命题。** 设每一时刻只需要维护可见窗口集合 $\mathcal{W}_t$ 内的 active sparse states，并假设窗口内 active support 满足预算

$$
\sum_{\Omega\in\mathcal{W}_t}|C_{\Omega,t}^{\mathrm{active}}|\leq T_{\max}.
$$

窗口外状态只以 baked chunk 或 cache descriptor 表示：

$$
(\mathrm{cache\_id},T,\ell,\mathrm{material\_intent},\epsilon_{\mathrm{cache}}).
$$

若每次窗口更新只展开 $\mathcal{W}_{t+1}$ 中缺失的 active region，并把离开窗口的 region 烘焙回 cache，则任意时刻的 active token 数不超过 $T_{\max}$。

**证明。** 这是由调度策略直接给出的不变量。初始时假设

$$
\sum_{\Omega\in\mathcal{W}_0}|C_{\Omega,0}^{\mathrm{active}}|\leq T_{\max}.
$$

每次更新后，调度器只保留 $\mathcal{W}_{t+1}$ 中的 active region，并在生成缺失 region 后执行 LOD collapse 或拒绝展开，直到满足

$$
\sum_{\Omega\in\mathcal{W}_{t+1}}|C_{\Omega,t+1}^{\mathrm{active}}|\leq T_{\max}.
$$

离开窗口的 region 不计入 active support，而由 cache descriptor 替代。因此对所有 $t$，active token 数均不超过 $T_{\max}$。证毕。

**边界。** 该命题只证明 active memory budget，不证明 cache descriptor 能无损重建，也不证明视觉连续性。若要证明视觉误差，需要给出每个 cache descriptor 的误差界与跨窗口 stitching 条件。

### 命题 10：Contractive transform 下的极限对象

**Status: PROVABLE AFTER WEAKENING**

**校正命题。** 设 $(X,d_X)$ 是完备紧致度量空间，有限映射族 $\{f_i\}_{i=1}^m$ 都是 contraction：

$$
d_X(f_i(x),f_i(y))\leq s_i d_X(x,y),\quad 0<s_i<1.
$$

令 Hutchinson operator 为

$$
\mathcal{H}(A)=\bigcup_{i=1}^m f_i(A)
$$

作用在非空紧集空间 $\mathcal{K}(X)$ 上，并以 Hausdorff 距离度量。则存在唯一 attractor $A^\star$，且

$$
\mathcal{H}^d(A_0)\rightarrow A^\star.
$$

P-RSLG 在命题 1 的退化设定下可表达该有限步迭代；因此它可表达 contractive recursive program 的有限深度近似。

**证明。** 由 Banach fixed-point theorem 与 Hutchinson operator 的标准结论：若每个 $f_i$ 为 contraction，则 $\mathcal{H}$ 在 $\mathcal{K}(X)$ 的 Hausdorff metric 下也是 contraction，其 Lipschitz 常数不超过

$$
s=\max_i s_i<1.
$$

因此 $\mathcal{H}$ 有唯一不动点 $A^\star$，且从任意非空紧集 $A_0$ 出发，$\mathcal{H}^d(A_0)$ 收敛到 $A^\star$。命题 1 已证明 P-RSLG 退化实例的一步转移等于 $\mathcal{H}$，所以有限步近似由 P-RSLG 表达。证毕。

**不能过 claim 的地方。** 这不是当前 mesh/SLAT/Trellis2 pipeline 的无界收敛证明。只要引入非 contractive transform、projection、sampler、quantization 或 material state，就需要新的闭性、紧性和误差传播假设。当前论文只能把 infinite recursion 写成：

$$
\text{finite-depth realization of a recursive program}
$$

或

$$
\text{bounded visible-window / LOD approximation of an unbounded logical recursion}.
$$

## 7. 命题状态总表

| 编号 | 内容 | Status | 适合位置 |
|---:|---|---|---|
| 1 | IFS 覆盖，连续 support 退化设定 | PROVABLE AS STATED | 主文或 appendix |
| 2 | L-system 覆盖，同步有序重写 | PROVABLE AS STATED | 主文或 appendix |
| 3 | Space colonization 覆盖，显式 attractor/tip state | PROVABLE AS STATED | 主文 |
| 4 | DLA/frontier accretion 覆盖，以 hitting kernel 为 proposal | PROVABLE AS STATED | appendix/stress-test |
| 5 | 有限局部 shape grammar 覆盖 | PROVABLE AFTER WEAKENING | appendix，主文只放简表 |
| 6 | Symmetry transform-copy 严格等变 | PROVABLE AFTER WEAKENING | appendix，主文用近似版 |
| 7 | Per-depth projection 坏碎片比例弱稳定 | PROVABLE AFTER WEAKENING | 主文可放简化命题 |
| 8 | sampler/projection 近似交换下的 equivariance bound | PROVABLE AFTER WEAKENING | 主文短句 + appendix 证明 |
| 9 | 有界 visible window / LOD active memory | PROVABLE AS STATED | future work 或 appendix |
| 10 | Contractive transform 的 IFS 极限 | PROVABLE AFTER WEAKENING | appendix/future work |

## 8. 可以进主文的表述

建议主文只写以下强度：

1. **Coverage proposition.** “By disabling the learned sampler/projection or choosing identity variants, P-RSLG reduces to standard finite-step procedural systems including IFS, L-systems, space colonization, DLA-like frontier accretion, and finite local shape grammars.”
2. **Projection stability proposition.** “Under explicit assumptions that projection removes invalid fragments up to tolerance and the encode/decode loop adds bounded error, per-depth projection bounds the invalid fragment mass at every recursive depth.”
3. **Approximate symmetry statement.** “For symmetric rules, if projection, sampler, merge, and codec approximately commute with the group action, the symmetry error is bounded by the accumulated commutation errors.”
4. **LOD statement.** “The system outputs finite-depth assets; unbounded logical recursion can only be handled through bounded visible windows, contractive transforms, or LOD/cache descriptors.”

## 9. 只能进 Appendix / Future Work 的内容

建议 appendix 放：

- IFS 与 L-system 的完整构造证明。
- DLA kernel 覆盖证明与 stress-test 说明。
- Shape grammar 的有限局部子类证明。
- Symmetry 近似交换误差界。
- Contractive recursion 与 visible-window LOD 命题。
- Projection stability 的完整假设清单，以及为什么 final-only cleanup 不能由同一弱命题保证。

建议 future work 放：

- 严格 group-equivariant sampler 或 group-averaged projection。
- Sliding-window infinite recursion 的实际实现与 cache stitching error。
- Masked SDE/flow naturalization 的 topology-preserving 条件。
- 对 material/PBR latent 的稳定性证明。

## 10. 当前未能证明的 claim 清单

1. **NOT CURRENTLY JUSTIFIED:** “Full flow/SDE repair preserves recursive topology.” 当前上下文反而记录了 full repair 可能 wash out topology。
2. **NOT CURRENTLY JUSTIFIED:** “P-RSLG guarantees exact symmetry/crystal equivariance in implementation.” 需要 sampler/projection/codec 严格或近似交换的证据。
3. **NOT CURRENTLY JUSTIFIED:** “Final-only projection is always worse than per-depth projection.” 现有理论只能说明 final-only 不享有每层状态的同一上界；严格劣势需要额外反例或分布假设。
4. **NOT CURRENTLY JUSTIFIED:** “Infinite recursion is implemented.” 当前只能说 finite depth output plus LOD/cache/infinite-zoom proxy plan。
5. **NOT CURRENTLY JUSTIFIED:** “Coverage of all shape grammars.” 当前只覆盖有限、局部、frame/mask 可表达的 shape grammar 子类。

## 11. 最终核查

- 每条命题都给出了 Status。
- Projection 稳定性只证明坏碎片比例上界，没有证明视觉质量或拓扑语义完全稳定。
- Symmetry/equivariance 明确依赖 sampler/projection/codec 近似交换。
- Infinite recursion 明确限制为 finite-depth realization、contractive IFS limit、bounded visible window 或 LOD/cache descriptor。
- 没有把当前尚未实验支撑的 SDE/cache/Escher claim 写成已完成理论结果。
