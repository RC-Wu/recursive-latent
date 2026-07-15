# Reviewer 修改意见行动计划 2026-05-09

来源：`/Users/fanta/Downloads/论文修改意见与reviewer批评整理.md`

本文档把 reviewer 式批评纳入当前 Ralph loop。它不是替代实验计划，而是论文写作与方法论收束的新增子任务。原则：先保留有用旧文本为 LaTeX 注释，再重写主文，避免把还可能有用的公式/实验叙述直接删掉。

## 最高优先级

1. 重写故事线。
   当前稿子容易被读成“传统程序化方法 + 生成模型”的拼接。新的主线应是：我们尝试直接把 Trellis2 / sparse voxel latent 用于递归结构，但 2D scaffold、direct sparse coordinate edit、global flow repair、final-only cleanup 都会导致拓扑覆盖、碎片累积或语义漂移；因此提出一个生成模型原生的 recursive language over sparse 3D latents。论文贡献是递归语言与稳定执行语义，不是工程拼接。

2. 重写 Method 3.2--3.4。
   旧版 `S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d,K_d)` 和巨大 grammar tuple 信息密度太高但不优雅。主文改成：
   \[
   z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d),
   \]
   其中 \(\mathcal V_d\) 是 sparse token support，\(\mathbf F_d\) 是 latent features，\(\mathcal A_d\) 是 anchors / handles / attachment graph。masks、caches、material handles、traces 放入 auxiliary state 或算法步骤，不做主状态并列项。

3. 把方法写成递归算法。
   主公式压缩为：
   \[
   z_{d+1}=
   \operatorname{Enc}_{\theta}
   \left[
   \Pi_\lambda
   \left(
   \operatorname{Dec}_{\theta}
   \left(
   \mathcal T_\theta(z_d;\mathcal R_d)
   \right)
   \right)
   \right].
   \]
   其中 \(\mathcal T_\theta\) 包含 rule selection、proposal、merge、masked local naturalization。然后用 Algorithm 1 展开执行流。

4. Projection 必须算法化。
   新增 Algorithm 2：输入 mesh/occupancy candidate、anchors、阈值；构建 voxel 或 mesh connectivity graph；寻找 root-attached component；按 mass/attachment/distance/renderability 评分；剪枝、桥接或 remesh；decode/project/re-encode；更新 handles。当前 bridge-after-decode 的负结果要用来说明 naive bridge 会制造假连接，因此 connected support invariant 必须前置到 grammar/projection loop。

5. Naturalization 必须写成 masked flow sampling。
   写清楚：
   \[
   \frac{dz_t}{dt}=v_\theta(z_t,t,y),
   \qquad
   z_{t-\Delta t}=(1-m)\odot z_{\mathrm{anchor}}+m\odot\Phi_{\theta,t}(z_t,y).
   \]
   强调 frozen generator 不拥有全局拓扑，只在 grammar mask 内自然化局部 shape/material。

## 章节结构调整

建议的新 Method 结构：

1. Problem Setting: recursive sparse-latent program execution。
2. Core State and Handles: minimal \(z_d\)，auxiliary bookkeeping 下沉。
3. Rule Templates: handles、local transforms、target regions、masks、proposal kernels。
4. Algorithm 1: Recursive Sparse-Latent Program Execution。
5. Algorithm 2: Projection to Connected Admissible Assets。
6. Masked Generative Naturalization。
7. Recursive Refinement and Effective Resolution。
8. Material Propagation and Trellis2 Texture Export。
9. Classical Systems as Limits: 主文压缩，细节放附录或 Related Work 后。

## 实验结构调整

实验章节应按 claim 组织：

1. Direct use of native 3D generators does not preserve recursive topology。
2. Per-depth projection stabilizes recursive sparse-latent growth。
3. Rule families expose a stability-expression tradeoff。
4. Connected-support grammar/root design resolves DLA/crystal fragmentation better than post-hoc repair。
5. Recursive sparse-latent programs support multiple asset families。
6. Trellis2 texture/PBR export is compatible with selected connected/projected meshes。

负面结果仍要保留，但放在 ablation、diagnostic 或 appendix。主图只展示支撑 claim 的强结果。

## 新增展示图任务

用户补充要求：需要同一 case 在不同 recursion depth 或不同参数控制下的可视化展示，不是为了消融，而是为了展示方法可控性。建议做两组：

1. Same-root depth progression：例如 connected vine/root 或 connected DLA/coral，从 depth 1 到 depth 4/5，固定 camera/material，展示结构逐步长出。
2. Same-root parameter sweep：例如 space competition 的 attractor density / branch angle / attachment threshold，固定 depth 和 guide，展示可控形态变化。

要求：所有图用 mesh 或 textured mesh render，不使用点云预览；最好包含 zoom-in crop。

## 文字清理任务

主文中应逐步移除或改写以下词：

- draft
- candidate
- smoke test
- technically compatible
- current paper use
- stress-test only
- initial export failed
- bug fixed

这些词可以保留在内部文档或 supplement diagnostic，但不应出现在正式 main paper 的主叙事中。

## 与当前实验状态的对应

- 当前 texture/PBR pipeline 已经能导出 Trellis2 textured GLB，方法章节可以正式写 Material Export，而不是只在表格中报告。
- 当前 bridge-after-decode DLA 指标可改善但视觉出现假连接，适合作为 negative ablation。
- 当前 connected scaffold v1 已证明 occupancy-connected roots 可进入 Trellis2 texturing，但 v1 视觉还不够强；v2 scaffold 和后续 textured GLB 是 DLA/crystal 正例的主要候选。
- 本地 traditional repair 只对 radial4 有安全改善，应作为 boundary finding，不作为 DLA/crystal 主方案。

## 立即执行队列

1. 把本文件和 reviewer source 加入 AgentDoc 总计划。
2. 先重写 `paper_siga/main.tex` 的 abstract、intro contribution 和 Method 3.2--3.4；旧文本用 LaTeX comments 暂存。
3. 添加 `Algorithm 1` 和 `Algorithm 2` 的草稿。
4. 在 Experiments 中把 task/baseline/metrics/results 的松散结构改成 claim-based outline。
5. 生成 depth/parameter visualization 的 first draft figure。
6. 编译 PDF，检查是否还有 `draft/smoke/candidate` 等正式论文不应出现的词。
