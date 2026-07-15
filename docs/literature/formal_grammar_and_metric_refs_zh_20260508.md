# Recursive Sparse-Latent Generative Grammar：形式语法、递归程序建模与评估参考

创建时间：2026-05-08  
用途：服务 `paper_siga/main.tex` 的 Method / Related Work / Experiments 重写。  
写作口径：把本文定位为 **Projection-Stabilized Sparse-Latent Recursive Grammar (PS-RSLG)**，即在冻结 native 3D generator 的 sparse latent state 上运行的有限深度递归生成语法。不要写成“训练了一个新 3D 生成器”、不要声称无限生成已经解决，也不要声称 masked flow 一定保持拓扑。

## 0. 可直接放进论文的核心定位

建议 related work 过渡句：

> Classical procedural grammars offer explicit recursive structure, while modern 3D generative models offer learned local shape and material priors. PS-RSLG treats these as complementary: the grammar owns the recursive scaffold, anchors, transforms, and admissibility constraints; the frozen sparse 3D generator supplies mesh-derived latent coordinates, local naturalization, decoding, re-encoding, and optional material export.

建议 method 过渡句：

> Projection is part of the recursive transition, not a final cleanup. This distinction matters because disconnected fragments can become growth roots at later depths; per-depth projection enforces an invariant on the state seen by the next grammar rule.

## 1. 关键论文/系统与一句话相关性

### 1.1 Procedural modeling grammars / shape grammars / graph grammars

| 方向 | 参考 | 与本文关系 | 建议写进哪里 |
|---|---|---|---|
| Shape grammar | Stiny and Gips, 1972, *Shape Grammars and the Generative Specification of Painting and Sculpture* | 早期把图形/形状生成写成 rewrite grammar；可作为“程序建模的形式源头”。 | Related Work 第一段，说明本文不是把 grammar 当比喻，而是真的定义 alphabet、rules、interpretation。 |
| CGA shape grammar | Müller et al., 2006, *Procedural Modeling of Buildings* ([ETH page](https://cgl.ethz.ch/publications/papers/paperMue06.php), [ACM TOG record](https://dl.acm.org/doi/10.1145/1179352.1141931)) | split / repeat / component split / extrusion 等规则是建筑 procedural grammar 的标准范式；本文的 `Tile`、`Portal`、`Split/Extrude` symbols 可说是 sparse-latent 版本。 | Related Work + Method “coverage of classical procedural systems”。 |
| Graph grammar procedural modeling | Krecklau, Kobbelt, et al. graph-grammar / example-based procedural modeling 系列；另见近年 “Example-based procedural modeling using graph grammars” | 支持把结构表示成 graph 而非 string；适合为本文的 typed symbol graph、attachment graph、component graph 找先例。 | Method 中解释 `U_d` 为什么可为 sequence or graph。 |
| Procedural facade/building modeling | Parish and Müller, 2001, *Procedural Modeling of Cities*；Wonka et al., 2003, instant architecture | 建筑/城市 procedural modeling 强调 rule scheduling、split hierarchy、local-to-global transforms；可用于 non-tree portal/arch/ornament case 的相关工作。 | Related Work non-tree recursive asset 段。 |

主文可借鉴写法：

```tex
Shape and graph grammars define geometry by applying typed rewrite rules to symbols, graphs, or spatial regions. We adopt this grammar view, but change the state space: symbols are interpreted as sparse native-3D latent support, masks, anchors, and decoded mesh regions rather than only curves, polygons, or hand-authored mesh templates.
```

### 1.2 L-system / turtle grammar

| 参考 | 与本文关系 | 可借鉴点 |
|---|---|---|
| Lindenmayer, 1968, *Mathematical models for cellular interactions in development* | L-system 源头，符号 rewrite 生成 branching/developmental form。 | 把 `U_d \in \Sigma^\star` 写成特殊情况；强调并行 rewriting / depth-wise derivation。 |
| Prusinkiewicz and Lindenmayer, 1990, *The Algorithmic Beauty of Plants* ([Algorithmic Botany](https://algorithmicbotany.org/papers/#abop)) | 植物/树/藤蔓 procedural grammar 的标准引用。 | 可以借 turtle interpretation：grammar string -> turtle frame -> geometry；本文是 symbol/anchor -> sparse support/features -> decoded mesh。 |

可放入 method 的退化实例：

```tex
An L-system is recovered when \(U_d\) is an ordered string or graph of turtle-frame symbols, \(\mathcal{R}\) rewrites symbols synchronously, and \(\mathcal{I}\) maps the derivation to branch support. PS-RSLG differs by interpreting rewritten symbols as sparse latent patches that are decoded, projected, and re-encoded after each depth.
```

### 1.3 IFS / fractal transform-copy

| 参考 | 与本文关系 | 可借鉴点 |
|---|---|---|
| Hutchinson, 1981, *Fractals and self similarity* | IFS 的 fixed-point / contraction mapping 形式基础。 | 可以把 transform-copy recursion 写为 Hutchinson operator \(H(A)=\cup_i T_i(A)\)。 |
| Barnsley, 1988, *Fractals Everywhere* | IFS 的图形学/生成建模常用引用。 | 用作 portal、scale-down、self-similar motif case 的传统 baseline。 |

可借鉴公式：

```tex
C_{d+1}=\bigcup_i Q_h(T_i(C_d\cap\Omega_i)).
```

如果要稍微理论化：

```tex
When all \(T_i\) are contractive and decoding/projection are disabled, the support update reduces to a discretized Hutchinson iteration. In PS-RSLG, the same transform-copy rule is followed by masked merge, admissibility projection, and re-encoding.
```

注意：不要 claim 当前结果已经达到严格 fractal attractor convergence。当前是 finite-depth asset growth。

### 1.4 Space colonization

| 参考 | 与本文关系 | 可借鉴点 |
|---|---|---|
| Runions, Lane, and Prusinkiewicz, 2007, *Modeling Trees with a Space Colonization Algorithm* ([Algorithmic Botany page](https://algorithmicbotany.org/papers/colonization.egwnp2007.html)) | 最直接对应本文 `compete` / attractor / tip growth operator。 | 用 attractor coverage、tip assignment、kill radius、influence radius 来定义 sparse competition。 |

可借鉴 method 句式：

```tex
Space colonization can be viewed as a grammar whose active symbols are tips and attractor cells. Rule application selects a tip direction from nearby attractors, proposes new support, and removes consumed attractors. Our sparse competition operator generalizes this rule by adding occupancy, collision, frontier, and learned-latent terms.
```

可借鉴公式：

\[
\psi(a,c;S_d)=
\lambda_{\mathrm{att}}\phi_{\mathrm{att}}
-\lambda_{\mathrm{occ}}\phi_{\mathrm{occ}}
-\lambda_{\mathrm{col}}\phi_{\mathrm{collision}}
+\lambda_{\mathrm{front}}\phi_{\mathrm{frontier}}
+\epsilon_\theta(c,\xi).
\]

其中前四项是传统程序建模项，\(\epsilon_\theta\) 只能写成 optional / future or weak evidence，避免被问“生成器真的参与了规则选择吗”。

### 1.5 DLA / frontier accretion

| 参考 | 与本文关系 | 可借鉴点 |
|---|---|---|
| Witten and Sander, 1981, *Diffusion-Limited Aggregation* ([PRL DOI](https://doi.org/10.1103/PhysRevLett.47.1400)) | porous/coral/crystal/frontier growth 的传统随机过程 baseline。 | 把 DLA 写成 frontier hitting kernel；适合 porous and accretion case。 |
| Sander, 2000, DLA review | 用于解释 DLA 是 stochastic growth / fractal aggregate，不是树模型。 | 用于 related work，不一定进主实验。 |

可借鉴公式：

\[
\rho_{\mathrm{DLA}}(c\mid S_d)\propto
\Pr[\text{random walk first hits frontier at }c].
\]

本文里的安全写法：

> DLA-like baselines are useful stress tests for frontier attachment and porous topology, but they do not provide learned mesh surface or material priors. We therefore compare them after converting occupied voxels to meshes under the same rendering and component-metric protocol.

### 1.6 Symmetry / equivariant grammar

可用参考应谨慎，因为“symmetry-equivariant grammar”不是一个像 L-system 那样统一的标准标签。建议分成两类引用：

| 方向 | 参考 | 与本文关系 |
|---|---|---|
| Procedural symmetry | CGA / shape grammar / architecture grammar 文献 | symmetry、repeat、mirror、lattice 本来就是 procedural rule 的常用 transform。 |
| Equivariant generative modeling | E(3)/SE(3)-equivariant graph/point diffusion 或 equivariant neural fields 文献 | 只能作为“如果 sampler/projection 近似 commuting with group action，可定义 equivariance error”的理论类比。 |

建议 method 写法：

\[
E_{\mathrm{sym}}(S;G)=\frac{1}{|G|}\sum_{g\in G} d_{\mathcal S}(gS,S).
\]

\[
\mathcal{T}_{r,\theta}(gS)\approx g\mathcal{T}_{r,\theta}(S).
\]

审稿风险：如果没有稳定 radial/crystal 图，不要把 symmetry-equivariant grammar 写成主贡献。只说 formalism supports group-orbit rules and reports symmetry error for applicable cases。

### 1.7 Neural / generative procedural assets

| 参考 | 与本文关系 | 可借鉴点 |
|---|---|---|
| ShapeAssembly / ShapeMOD / neural program induction for 3D shapes | 学习或生成结构化 shape programs，通常关注部件/程序表示。 | 用来区分：它们学习/推断程序，本文手写 grammar + frozen 3D latent prior。 |
| Infinigen, 2023, procedural photorealistic scenes ([project](https://infinigen.org/), [CVPR paper](https://arxiv.org/abs/2306.09310)) | 证明高质量程序建模仍然是生成数据/场景的重要路线。 | 相关工作：程序规则可以高质量，但需要大量 domain engineering；本文聚焦 asset-level sparse latent recursion。 |
| SceneDreamer / CityDreamer / TRELLISWorld 类 world generation | 局部生成器 + compositional world layout。 | 只作动机，不要把本文写成 unbounded scene generation。 |
| Objaverse / Objaverse-XL | 现代 3D 生成模型训练数据背景。 | Related Work 里支撑“large 3D generators now offer learned priors”。 |

建议 related work 对比句：

> Neural program and procedural-scene systems either learn/generate programs or hand-author large procedural rule sets. Our question is narrower: given a frozen sparse 3D generator and a finite recursive grammar, can repeated edits remain connected, renderable, and structurally faithful across depth?

### 1.8 TRELLIS / sparse structured 3D latent

| 参考 | 与本文关系 | 可借鉴点 |
|---|---|---|
| TRELLIS, *Structured 3D Latents for Scalable and Versatile 3D Generation* ([project](https://trellis3d.github.io/), [arXiv](https://arxiv.org/abs/2412.01506)) | 最关键的 generator-side 参考：sparse structured latent / asset decode。 | 本文不是新 generator，而是把 sparse state 当 grammar substrate。 |
| TRELLIS.2 project / native 3D asset generation | 若主文引用 Trellis2，需用项目页或技术报告核验具体能力：mesh-to-O-Voxel/SLAT encoding、texture/PBR export、decoder。 | Method 里写“frozen native 3D generator such as TRELLIS/TRELLIS.2”；具体接口以实验实现为准。 |

安全写法：

> We use a frozen TRELLIS-style sparse 3D representation as the state space of recursion. This differs from one-shot generation: the sparse state is repeatedly edited, decoded, projected, and re-encoded under a grammar-controlled transition.

不要写：

> TRELLIS guarantees topology preservation under recursive editing.

### 1.9 Training-free 3D editing：TRELLIS/NANO3D-like

| 参考 | 与本文关系 | 可借鉴点 |
|---|---|---|
| SDEdit, 2021 | training-free editing / stochastic resampling 的 2D 源头之一。 | 用作 “frozen generative prior can edit without retraining” 的基础类比。 |
| FlowEdit, 2024 | flow-based training-free editing。 | 可支持 “partial flow trajectory / local naturalization” 的写法。 |
| NANO3D, *A Training-Free Approach for Efficient 3D Editing Without Masks* ([arXiv](https://arxiv.org/abs/2510.15019), [project](https://jamesyjl.github.io/Nano3D)) | 与本文同样强调 frozen 3D priors / no retraining，并把 FlowEdit/TRELLIS 思路用于 3D editing；但目标是 efficient mask-free single/object-part editing。 | 用来区分本文是 repeated grammar edits，错误会跨深度累积；可借鉴 Voxel/Slat merge 的 preserved/edited region 分离。 |
| VoxHammer, *Training-Free Precise and Coherent 3D Editing in Native 3D Space* ([arXiv](https://arxiv.org/abs/2508.19247), [project](https://huanngzh.github.io/VoxHammer-Page/)) | 直接在 native 3D latent space 做局部编辑，强调 preserved region consistency、latent/KV replacement。 | 可借鉴 unedited-region preservation 指标：Chamfer、masked PSNR/SSIM/LPIPS；但本文不能声称有同等 precise local edit benchmark。 |
| InpaintSLat, *Inpainting Structured 3D Latents via Noise Optimization* ([project](https://robot0321.github.io/InpaintSLat/index.html)) | 训练自由 3D inpainting，使用 structured 3D latent diffusion，并强调 preserved structure 与 plausible content 的权衡。 | 支持 masked sparse latent inpainting / local naturalization 相关工作；本文区别是 grammar recursion 而非单次 inpainting。 |

安全 related work 句式：

> Training-free 3D editing methods reuse frozen generative priors for a single semantic or localized edit. PS-RSLG changes the failure mode: the same edit operator is applied recursively, so fragments, disconnected patches, and scaffold drift can compound into later grammar states.

method 中可以借鉴的公式风格：

\[
Z_{t-\Delta t}\leftarrow
(1-\mu_\Omega)\odot Z_{\mathrm{anchor}}
+\mu_\Omega\odot \Phi_{\theta,t}(Z_t,y).
\]

但主文必须说明当前证据：

> In our current experiments, global flow repair tends to wash out recursive topology; masked local naturalization is therefore treated as a controlled component with mixed evidence rather than a solved topology-preserving sampler.

## 2. 哪些公式/证明风格可以借鉴

### 2.1 Grammar object tuple：来自 shape grammar / formal language 风格

建议保留当前 tuple，但减少主文解释负担：

\[
\mathcal{G}=
(\Sigma,\mathcal{T},\mathcal{R},\mathcal{I},\mathcal{S},
\Pi,\mathcal{N}_\theta,\mathcal{D}_\theta,\mathcal{E}_\theta,
\mathcal{P},\mathcal{C},\mathcal{O},\mathcal{L}).
\]

写法重点：

- \(\Sigma,\mathcal{R},\mathcal{I},\mathcal{S}\)：继承 grammar 传统。
- \(\mathcal{T}\)：继承 IFS / CGA / symmetry transforms。
- \(\Pi\)：继承 procedural constraints / collision / occupancy。
- \(\mathcal{N}_\theta,\mathcal{D}_\theta,\mathcal{E}_\theta\)：本文新增，把 frozen generator 纳入语法语义。
- \(\mathcal{P}\)：本文最重要，projection-stabilized recursion。

### 2.2 Degenerate-instance proof：证明“传统方法是特例”

这比写很泛的 related work 更有力。建议放一小段 proposition：

> Several classical procedural systems are recovered by disabling the learned naturalizer and choosing specialized state and rule types.

具体对应：

- L-system：\(U_d\in\Sigma^\star\)，同步 rewrite，\(\mathcal{I}\) 为 turtle interpretation。
- IFS：单一 patch symbol，规则为 \(C_{d+1}=\cup_iT_i(C_d)\)。
- Space colonization：symbols 为 tips/attractors，score 只保留 \(\phi_{\mathrm{att}},\phi_{\mathrm{occ}}\)。
- DLA：proposal kernel 为 frontier first-hitting distribution。
- Shape grammar/CGA：symbols 为 faces/tiles/portals，rules 为 split/extrude/repeat/replace。

### 2.3 Stability proof：用 invariant，而不是强收敛

不要证明“递归一定收敛到好形状”。建议只证明 per-depth projection 的弱 invariant：

定义错误：

\[
e(S)=V_{\mathrm{frag}}(S)+\lambda_aV_{\mathrm{attach}}(S)+\lambda_rV_{\mathrm{render}}(S).
\]

假设：

1. projection 近似压制错误：\(e(P_\lambda(x))\le \epsilon_P\)；
2. decode/re-encode 引入有界错误：\(e(E_\theta(D_\theta(S)))\le e(S)+\epsilon_E\) 或更弱地下一步前新增坏质量不超过 \(\epsilon_E\)；
3. grammar proposal 每步新增错误质量有界：\(\epsilon_G(d)\)。

得到：

\[
e(S_d)\le \epsilon_P+\epsilon_E+\epsilon_G(d)
\]

或写成深度逐步上界：

\[
e(S_{d+1}) \le \epsilon_P+\epsilon_E.
\]

对比 final-only：

\[
S_D^{\mathrm{final}}=P\circ G_{D-1}\circ\cdots\circ G_0(S_0)
\]

无法保证 \(G_k\) 看到的是 admissible state，所以 fragments can become new growth roots。

这类证明风格服务当前实验：projection-depth curves / largest-component ratio 可以直接验证 invariant，而不需要证明 topology theorem。

### 2.4 Equivariance proof：只能作为 metric，不作为保证

如果要写 symmetry：

\[
E_{\mathrm{eq}}(S;G)=\frac{1}{|G|}\sum_{g\in G}
d_{\mathcal S}(\mathcal{T}(gS),g\mathcal{T}(S)).
\]

正文措辞：

> This provides an error metric for group-orbit rules; exact equivariance is not assumed because the frozen generator and projection operator need not commute with arbitrary transforms.

## 3. Baseline / metric 应借鉴哪些传统图形学评估

### 3.1 Baseline 组织方式

建议 experiments 不按“算法名字”散列，而按 failure question 分组：

| 问题 | Baseline | 目的 |
|---|---|---|
| 传统递归是否结构更清楚但资产质量弱？ | L-system / space colonization / DLA / IFS / CGA mesh baselines | 证明本文不是靠“没有 baseline”赢；传统结构强，但 mesh/material/schema 较弱。 |
| one-shot 生成能不能直接解决？ | One-shot TRELLIS/TRELLIS.2 | 检验 recursive structure 是否丢失。 |
| 直接 sparse grammar 是否会累积错误？ | Direct coordinate/latent grammar without projection | 支撑 projection 必要性。 |
| 最后清理一次够不够？ | Final-only projection | 支撑 per-depth projection。 |
| frozen sampler 能否直接 repair？ | Full flow repair / strong denoise | 证明 topology wash-out。 |
| 弱 masked prior 是否有帮助？ | Masked weak blend / local naturalization | 展示 stability-expression tradeoff。 |
| 主方法 | Projection-stabilized grammar | 报 depth curves、component stats、renderability、selected texture export。 |

### 3.2 Mesh validity / renderability：基础资产指标

必须报告：

- `component_count`
- `largest_component_vertex_ratio`
- `fragmentation_score = 1 - largest_component_vertex_ratio`
- `small_component_count`
- vertices / faces / bbox extent / bbox volume
- watertight / non-manifold edge count，如果工具稳定
- GLB import success / material channels present / render success

理由：这是 3D asset 论文最容易被问的“能不能用”的底线。

### 3.3 Branching / tree metrics：借 L-system、space-colonization、QSM

参考：

- Runions et al. space colonization：tip、attractor、kill radius、influence radius。
- Raumonen et al., 2013, quantitative structure models for trees ([PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0064570))：tree reconstruction 常用 branch graph / cylinder model / branch topology 思路。

建议指标：

- tip count：degree-1 non-root nodes。
- branch node count：degree >= 3。
- branch length distribution。
- branching angle distribution。
- radius taper consistency。
- attachment success rate：新增 proposal 与 parent/largest component 相接的比例。
- attractor coverage：每个 attractor 到最近 branch/tip 的距离分布。

对 generated mesh，优先用 grammar trace/anchor trace；没有 trace 时再做 voxel skeleton proxy，并在论文里标注 proxy。

### 3.4 Space competition / occupancy metrics

适合本文最直接的 compete operator：

- occupancy coverage：occupied voxel / bbox voxel。
- collision violation rate：proposal 互相冲突或与 forbidden region 冲突比例。
- exclusion success：competition 后移除冲突 proposal 的比例。
- new support acceptance：新增 support 中通过 projection 并保留到下一深度的比例。
- frontier compactness：frontier 与已有 support 的接触边数或距离。

这些指标可以直接写进 method/experiments，因为它们和 \(\psi(a,c;S_d)\) 一一对应。

### 3.5 Porous / DLA / crystal：Minkowski functionals 与拓扑 proxy

参考方向：

- Minkowski functionals for binary/porous media：volume、surface area、mean breadth、Euler characteristic 是 3D binary morphology 的经典描述。
- Porous media / material characterization 文献可支持 Euler characteristic / connectivity / void descriptors。

建议指标：

- voxel volume。
- surface area proxy。
- Euler characteristic。
- connected components。
- cavity/void count proxy。
- porosity = empty volume ratio within normalized bbox。

适用场景：DLA、coral、porous、crystal。不要对树强行用 Euler characteristic 做主指标。

### 3.6 Fractal / self-similarity：谨慎作为辅助指标

可用：

- box-counting dimension。
- \(\log N(d)\) vs depth slope。
- transform self-similarity error：把子结构用 grammar inverse transform 对齐到 root/motif 后算 Chamfer / occupancy IoU。
- zoom consistency：visible-window recursion 的相邻 zoom render feature similarity。

警告：

- branching assets 不一定是严格 self-similar fractal；
- box-counting 对 resolution、bbox normalization、threshold 很敏感；
- 不要把 fractal dimension 作为主结论，只作为 appendix / diagnostic。

### 3.7 Symmetry / equivariance metrics

适用于 radial、mirror、crystal、portal：

\[
E_{\mathrm{occ}}(g)=1-\operatorname{IoU}(gO,O).
\]

\[
E_{\mathrm{chamfer}}(g)=\operatorname{Chamfer}(gP,P).
\]

\[
E_{\mathrm{render}}(g)=\|f(\operatorname{render}(gM))-f(g\operatorname{render}(M))\|.
\]

主文建议只报 \(E_{\mathrm{occ}}\) 或 \(E_{\mathrm{chamfer}}\)，render feature metric 容易被问 feature choice / camera alignment。

## 4. 哪些 claim 容易被审稿人质疑

### 4.1 “Grammar” 是否只是包装词

风险：如果 Method 只写 root mesh -> Trellis2 -> cleanup，审稿人会说不是 grammar。

补强方式：

- 明确写 \(\mathcal{G}\) tuple。
- 给 rule schema。
- 给 degenerate instances：L-system、IFS、space colonization、DLA、CGA。
- 把 `projection / decode / re-encode / cache` 写成 operational semantics，而不是工程步骤。

### 4.2 “Training-free” 是否成立

风险：如果用了任何 finetune、learned adapter、custom texture training，不能叫 training-free。

补强方式：

- 写清楚 frozen parts：\(\theta\) fixed。
- 所有选择是 hand-authored rules、projection、sample selection、mesh operations。
- 如果用了 SD3.5 guide image 或 Trellis texture export，说明是 inference-time conditioning / postprocessing。

### 4.3 “Learned generator contributes local prior” 是否有证据

风险：如果当前主要效果来自 coordinate copy + projection，生成器贡献会被质疑。

补强方式：

- 把 claim 降成：generator supplies sparse state, decoder/re-encoder, material/export prior。
- 不要过强 claim masked naturalization。
- 实验上给 direct procedural mesh vs encoded/decoded/projected asset 的 visual / metric 对比。

### 4.4 “Per-depth projection improves recursion” 是否可能只是删掉坏东西

风险：projection 可能降低 complexity，只保留 largest component。

补强方式：

- 同时报 structure preservation：tip count、branch count、bbox growth、accepted new support。
- 报 projection 前后 vertex/token retention。
- 与 final-only projection 比：不仅 final component 好，还要中间 depth 都可用。
- 图中展示 raw vs projected vs re-encoded next-depth。

### 4.5 “Recursive growth depth-5” 是否只是少量稳定 case

风险：只 cherry-pick vine/tree。

补强方式：

- 把强 claim 限定到 conservative competition operators。
- 把 fork/side/radial/echo 写成 stress tests。
- 表格列失败和 unstable operators，不只展示成功图。

### 4.6 “Symmetry-equivariant” claim

风险：frozen decoder、projection、mesh operations 很可能不严格 equivariant。

补强方式：

- 用 “group-orbit rules” 或 “symmetry error metric”，不要写 exact equivariance。
- 如果没有 radial/crystal 稳定结果，不放主贡献。

### 4.7 “Infinite / zoomable recursion”

风险：当前系统是有限 depth + sparse token budget，不是无限场景。

补强方式：

- 主文只说 finite-depth recursive assets。
- infinite / visible-window / cache 写 appendix/future extension。
- 如果展示 portal/scale-down，只叫 infinite-zoom proxy。

### 4.8 Texture / PBR quality

风险：geometry 递归和 texture export 混成一个 claim，图好看但结构被材质遮盖。

补强方式：

- neutral geometry render 和 textured GLB render 分开展示。
- GLB/PBR 通道以 smoke test / compatibility 呈现。
- 承认 category-dependent material mismatch。

## 5. 建议加到 `main.tex` 的最小引用组

优先级从高到低：

1. Procedural grammar backbone：Lindenmayer 1968；Prusinkiewicz and Lindenmayer 1990；Stiny and Gips 1972；Müller et al. 2006 CGA。
2. Recursive growth algorithms：Runions et al. 2007 space colonization；Witten and Sander 1981 DLA；Hutchinson 1981 / Barnsley 1988 IFS。
3. Sparse 3D generator：TRELLIS 2024 / TRELLIS.2 project documentation or technical report。
4. Training-free editing：SDEdit；FlowEdit；NANO3D/VoxHammer/InpaintSLAT-like native 3D editing preprints, only if bib verified。
5. Evaluation：Raumonen et al. 2013 QSM tree metrics；Minkowski functionals / porous media morphology；mesh validity / connected-component metrics from 3D asset evaluation practice。

## 6. 推荐论文结构改法

### Related Work

建议四段：

1. Classical recursive procedural modeling：L-system / IFS / space colonization / DLA / shape grammars。
2. Neural 3D generation and sparse latent states：Objaverse/TRELLIS/TRELLIS.2。
3. Training-free 3D editing：single-edit methods vs repeated recursive edits。
4. Evaluation of recursive assets：structure, connectivity, morphology, renderability。

### Method

建议顺序：

1. Problem setting。
2. State \(S_d\)。
3. Grammar tuple \(\mathcal{G}\) and rule schema。
4. Operational semantics equation。
5. Classical systems as degenerate cases。
6. Projection-stabilized recursion and invariant proposition。
7. Operators：competition、transform-copy、masked naturalization。

### Experiments

建议问题导向：

1. Does direct recursion accumulate fragments?
2. Is final-only projection enough?
3. Do conservative competition rules remain stable with depth?
4. What is the stability-expression tradeoff for fork/side/portal/radial operators?
5. Does texture/PBR export remain compatible with projected geometry?

## 7. 参考链接清单（写 bib 前核验）

- Lindenmayer, 1968, L-systems: https://doi.org/10.1016/0022-5193(68)90079-9
- Prusinkiewicz and Lindenmayer, 1990, *The Algorithmic Beauty of Plants*: https://algorithmicbotany.org/papers/#abop
- Runions et al., 2007, space colonization: https://algorithmicbotany.org/papers/colonization.egwnp2007.html
- Witten and Sander, 1981, DLA: https://doi.org/10.1103/PhysRevLett.47.1400
- Müller et al., 2006, CGA shape grammar: https://cgl.ethz.ch/publications/papers/paperMue06.php
- TRELLIS project: https://trellis3d.github.io/
- TRELLIS arXiv: https://arxiv.org/abs/2412.01506
- NANO3D arXiv: https://arxiv.org/abs/2510.15019
- VoxHammer arXiv: https://arxiv.org/abs/2508.19247
- InpaintSLat project: https://robot0321.github.io/InpaintSLat/index.html
- Infinigen: https://infinigen.org/
- Raumonen et al., 2013, QSM trees: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0064570
