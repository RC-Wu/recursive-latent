# Revision requirements -> PS-RSLG 当前状态与实验优先级

创建时间：2026-05-10  
范围：方法/实验状态整理；仅新增本地文档，不修改 `paper_siga/main.tex`，不启动 SSH。  
主要依据：

- `/Users/fanta/Downloads/agent_revision_and_experiment_requirements.md`
- `docs/agentdoc_mirror/plans/recursive_3d_generative_growth_system_grammar_plan_20260508.md`
- `docs/progress/项目全任务完成情况总览_2026-05-09.md`
- `docs/method/ps_rslg_formal_framework_deep_zh_20260509.md`
- `docs/method/connectivity_invariant_ps_rslg_zh_20260509.md`
- `docs/method/ps_slg_connectivity_cache_extension_zh_20260509.md`
- `docs/experiments/occupancy_primary_connectivity_and_flow_summary_zh_20260509.md`
- `docs/evaluation/claim_aligned_metric_summary_zh_20260509.md`
- `docs/evaluation/non_tree_connectivity_update_zh_20260509.md`

## 0. 总体判断

当前最稳的论文主线已经不是“procedural grammar + mesh cleanup + Trellis2 texture”，而应收束为：

> **PS-RSLG 是定义在冻结 3D 生成模型原生 sparse latent / sparse support state 上的有限深度递归语法。** 语法负责 topology、typed handles、frontier、rule proposal、occupancy competition、projection/admissibility 与 cache/LOD descriptor；冻结 3D generator 只作为 sparse codec、masked local naturalizer 和 selected texture/PBR export path。Projection 是每层递归转移的 admissibility semantics，不是最终 mesh repair。

但当前证据仍必须保守：

- 可以主张：occupancy-primary connected support、per-depth projection 比 direct/final-only 更能抑制碎片传播、selected connected scaffolds 可进入 Trellis2 texture/PBR export。
- 不能主张：raw GLB/mesh topology clean、真实 DLA/晶体物理生长已解决、无限递归已实现、Flow/SDE/cache 已是主贡献、texture/PBR 是结构正确性证据。
- 论文主 claim 必须写成 **finite-depth recursive asset growth with connected sparse support invariant**，而不是全类递归 3D 生成问题的解决方案。

## 1. 修改要求到当前状态的映射

| 要求 | 当前状态 | 论文可写程度 | 仍缺什么 |
|---|---|---|---|
| Abstract/Intro 强调 generation-model-native recursive grammar | 方法文档和进度文档已统一到 PS-RSLG / sparse-latent grammar；不应再让 projection 或 texture 抢主线 | 可写为主叙事 | 需要在 `main.tex` 中压缩重写，并用实验/文献绑定每个强 claim |
| Related Work / Preliminaries | 参考方向已列出：procedural recursion、3D generative models、editing/control、Trellis-style sparse pipeline | 可先搭结构 | 仍需核验引用，并定义 recursive generation 与 sparse generator pipeline 的最小符号 |
| Method 主公式和符号 | 深版 PS-RSLG 草稿已把状态压到 sparse support/features/anchors；connectivity invariant 已形式化 | 可作为 Method 写作底稿 | 需要消除 `R_d`、`P_d`、`A_d` 等符号冲突，并把大 bookkeeping 放附录 |
| Projection 改为 model-native/admissibility | 已形成 connected-state invariant、projectable reachable domain、prune-only vs bridge-aware 的方法语言 | 可写，但必须谨慎 | 需要把 bridge 写成 grammar/model-proposed masked completion；传统 bridge/mesh repair 只能作 baseline/appendix 负例 |
| Occupancy-primary connectivity | 当前最强证据；6-neighborhood occupancy component/LCR 是主指标，face/mesh 是诊断 | 可作为主实验表核心 | 不能用 occupancy LCR 证明 mesh topology clean；需补 skeleton/root/tip/path 和 mesh validity |
| 非树结构 | Coral/bismuth-like connected scaffold 有正例；pyrite 是边界；hard-DLA/bridge 是负例 | Coral/bismuth 可小心进主文；DLA 多数进 appendix | 需要 neutral/zoom QA、facet/contact/cavity/frontier metrics，避免把纹理图当结构证据 |
| Flow/SDE naturalization | 当前 Flow/SDE 只有 tokens/verts/faces/seconds，没有 connectivity components | 不能作主文正例 | 必须补同一套 occupancy/face evaluator 和 masked-vs-global-vs-none ablation |
| Cache/LOD | 方法语义已写入 cache descriptor / visible-window extension；实验证据主要是 proxy smoke | 最多写成 extension/limitation | 需要 true Trellis decode、connectivity metrics、visual QA 和 token/memory budget 后才能升级 |
| Metrics/Baselines | 已有 claim-aligned summary 和 projection matrix；但 LCR 区分力不足 | 只能支撑有限 claim | 必须补 mesh/surface、skeleton、morphology、latent stability、effective resolution、runtime、seed/root mean/std |
| Figures | 白底、固定相机、无 PPT 风格的要求已明确，部分图库已整理 | 可选少量 candidate | 所有主文图必须一图一 claim，配指标或 zoom；负例和大 gallery 放 supplement |

## 2. PS-RSLG 主线应如何落地

### 2.1 方法定义

主文应把 PS-RSLG 写成三件事，而不是长工程链：

1. **State**：`z_d=(V_d,F_d,A_d)`，其中 `V_d` 是 sparse token support，`F_d` 是 generator-native feature，`A_d` 是 typed handles / anchors / frontiers / ownership / optional cache descriptors。
2. **Rules**：handle-to-proposal templates。规则输出局部 transform、edit mask、proposal kernel、attachment feasibility、sampler schedule 和 ownership，而不是直接复制最终 mesh。
3. **Realization and projection**：masked merge/competition -> masked local naturalization -> projection to admissible connected state -> decode/re-encode/cache update。

核心不变量应写成：

```text
z_d in Z_adm(lambda_d), for every depth d.
```

`Z_adm` 至少包含 connected occupancy support、active frontier root reachability、token budget、collision/occupancy constraint、可渲染性 proxy。重点是：floating chunk 一旦成为下一层 frontier/cache source，就是递归状态错误，不是最终可删的视觉残余。

### 2.2 Projection 的正确措辞

主文不应使用会让 reviewer 联想到人工修网格的词作为本文方法主体，例如 weld、close holes、remesh、insert bridge geometry。更稳的写法是：

- projection is admissibility-constrained state selection;
- orphan materialized components are made inactive before they become recursive handles;
- optional connector must be grammar-proposed and model-naturalized under a mask;
- post-hoc mesh repair is an appendix/baseline, not PS-RSLG.

实验上必须分清：

- `no projection`;
- `final-only cleanup`;
- `per-depth prune-only projection`;
- `model-proposed bridge projection`;
- `traditional repair baseline`.

当前最强可写数值仍是 `vine_compete_d3`：无投影组件数约 `2059`、LCR `0.9049`；final-only 组件数 `2`、LCR `0.9934`；per-depth 组件数 `1`、LCR `1.000`。这支持“每层 projection 抑制碎片传播”，但还不能证明所有 case 或所有 mesh topology clean。

## 3. Occupancy-primary connectivity 的边界

当前主指标应明确采用 voxelized occupancy 6-neighborhood component count 与 LCR。原因是 raw face connectivity 会被 GLB export、UV/material seam、tube surface split、非共享顶点等因素强烈干扰；但 occupancy support 更接近 PS-RSLG 所需的 recursive state connectedness。

可进入主文的写法：

> We report connected support as a per-depth invariant using voxelized 6-neighborhood component count and largest-component ratio, while separately reporting face/mesh diagnostics to expose surface fragmentation and export artifacts.

不可进入主文的写法：

> Our exported GLB meshes are topology-clean.

还需补充的指标：

- mesh/surface：face components、boundary edges、holes、non-manifold edges、watertightness、thin sheets、normal consistency；
- skeleton/recursive topology：tip count、branch node count、path-to-root rate、orphan handle rate、frontier validity、terminal handle survival；
- morphology：porosity、cavity/pore components、surface-to-volume ratio、local density、Minkowski-style descriptors；
- latent stability：token count/depth、re-encoding drift、deleted mass、orphan mass、transform-copy consistency；
- effective resolution：terminal detail count、minimum feature scale、local token density、detail survival after decode/project/re-encode；
- asset readiness：GLB export/import success、PBR channel completeness、render warnings、UV/material seam diagnostics、file size。

## 4. 非树与边界案例的当前归类

### 4.1 可作为正例但需限缩措辞

- `volumetric_dla_coral / fork_side_attach / sparse_close` depth=3：当前汇总中 occ=1、occ_lcr=1.000、face=1、face_lcr=1.000，是非树线最强正面候选。可写成 DLA/coral-inspired connected scaffold，不能写成真实 DLA 过程。
- `bismuth_hopper` / bismuth-like scaffold：occupancy-primary 证据较稳，可写成 bismuth-inspired connected scaffold。不能写物理 bismuth crystallization。
- Coral density sequence：同一条件下 density 参数变化仍保持 surface-voxel 单分量，适合“method behavior / parameter control”图，不是 ablation。

### 4.2 边界或补充

- `pyrite_lattice`：method-compare 中可见 occupancy 正面，但 depth/close grid 显示参数敏感，face/occupancy 不等价。适合 appendix 或边界讨论，不建议作为主文核心成功例。
- 传统 L-system / space-colonization：在公平 tube-occupancy 协议下也可 comp=1、LCR=1，因此不能把“occupancy connectedness”当作击败传统方法的唯一证据。

### 4.3 负例

- hard-DLA、DLA bridge、post-hoc bridge/mesh repair：可出现 face component 改善但 occupancy 仍碎，或者视觉 over-closing / fake bridge。它们应作为“为什么 projection 必须进入 grammar semantics”的负例，而不是正例。
- fork/radial/echo 等表达性更强但更碎的 variants：适合展示 stability-expression tradeoff，不能作为主图胜例。

## 5. Flow/SDE/cache 当前状态

### 5.1 Flow/SDE

当前 Flow/SDE 输出缺少 occupancy/face component 指标，只记录 depth-level input tokens、repaired tokens、vertices、faces、runtime。它只能说明 sampler path 可运行或可生成 mesh，不能说明 topology/connectedness 被改善。

下一步最小闭环：

1. 对所有 Flow/SDE 输出跑同一套 occupancy/face evaluator；
2. 与 no naturalization、weak feature blend、masked local naturalization、global flow repair、projection-only 做同 root/depth 对比；
3. 报 topology drift、branch/tip preservation、deleted mass、mesh validity、runtime；
4. 如果仍不能改善，就将 Flow/SDE 写成 appendix negative/boundary，支撑“global generative repair may wash out recursive topology”。

### 5.2 Cache/LOD

Cache 当前更适合写成 PS-RSLG 的语义扩展：motif/latent/transform/LOD/window descriptors 只允许保存带 attachment certificate 的片段，未 materialize 的 descriptor 不能作为 visible frontier。已有 smoke/proxy 说明它有实现路径，但还不足以做主贡献。

升级为主文 supporting ablation 的条件：

- true Trellis decode/re-encode 通过；
- occupancy/face connectivity 指标齐全；
- cache 与 no-cache 在同 root/depth/token budget 下公平比较；
- 有 fixed-camera neutral/zoom QA；
- 报 token budget、GPU memory、per-depth runtime。

## 6. 阻塞 SIGA-level claim 的指标与图

当前离 SIGA-level 论证主要还差以下证据，而不是更多 gallery：

1. **Novelty-critical comparison**：latent-space recursive grammar vs mesh-space procedural recursion + repair + Trellis texture export。必须证明操作发生在 generator-native sparse state 上带来 transform/cache/addressability 或 local naturalization 优势。
2. **Projection variants**：no projection / final-only / prune-per-depth / model-bridge / traditional repair baseline。必须报告 deletion mass、orphan handles、active handle survival、branch/tip preservation、LCR 与 face diagnostics。
3. **Naturalization ablation**：rule-only、encode/decode-only、no naturalization、weak blend、masked local naturalization、global flow repair、with/without projection。
4. **Effective resolution**：same one-shot Trellis2 vs recursive refinement；same total token budget vs local token allocation；depth curves；terminal detail survival；zoom panels；minimum feature scale。
5. **Root/seed robustness**：multiple roots、seeds、prompts/guides，报告 success/failure rate 和 mean/std。
6. **Runtime/complexity**：per-depth encode/decode/projection/naturalization/texture time、GPU memory、token/mesh growth、projection cost。
7. **Paper-grade figures**：纯白背景、固定相机、无边框、无解释性图内文字，只保留子图编号；每张主图绑定一个 claim 和对应指标/zoom。

## 7. 下一轮实验优先级

### P0：锁主 claim 与主表

目标：先让论文有可防守的主结论。

- 主 claim 限定为 finite-depth PS-RSLG with occupancy-primary connected support invariant。
- 主表只放最强正例与关键 ablation：vine projection、coral connected scaffold、bismuth selected positive，以及对应 no/final/per-depth controls。
- Texture/PBR 只作为 selected export compatibility，表格中和 geometry/connectivity 指标分列。

### P1：证明“不是 mesh procedure + texture”

这是最重要的 novelty 实验。

- Baselines：mesh-space procedural recursion + smoothing/remeshing、mesh recursion + Trellis texture only、one-shot Trellis2、2D scaffold -> Trellis2、direct sparse edit、sparse-latent recursion with/without masked naturalization。
- Metrics：connectedness、branch/tip preservation、surface quality、transform-copy consistency、re-encoding drift、texture export compatibility、runtime/token budget。
- 图：同 root、同 depth、同 renderer的 neutral + zoom comparison。

### P2：Projection 与 naturalization 闭环

- Projection variants 必须和 manual repair 分开写，避免“手工补丁”印象。
- Flow/SDE 先补 connectivity evaluator；如果不能稳定改善，就保留为负例，不再硬写正面。
- Model-proposed bridge 只有在 mask、naturalization、re-encode 和指标都闭环后才能进主方法正线。

### P3：非树结果筛选

- 主文优先 coral/bismuth；pyrite 只作边界或补充；hard-DLA 停止追正面，作为 limitation/negative。
- 给 coral/bismuth 补 neutral render、root/junction/contact zoom、occupancy/face metric table。
- 给 DLA/coral stress 补 frontier attachment、porosity/cavity、fake bridge/over-closing label。

### P4：Effective resolution / cache / LOD

- 先不要把 infinite recursion 放入 abstract/contribution。
- 做一个最小 zoom/refinement strip：固定 root、固定 grammar、不同 depth/local token allocation，报告 terminal detail、local token density、detail survival。
- Cache/LOD 只在 metrics、visual QA、runtime 都通过后升级为 supporting result。

## 8. 建议写入论文的保守结论

可以写：

> PS-RSLG treats connectivity as a recursive-state invariant over generator-native sparse support. Per-depth projection prevents orphan components from becoming future handles, and selected connected scaffolds can be decoded, re-encoded, and exported through the frozen Trellis2 texture path.

不要写：

> We solve recursive 3D topology, DLA/crystal generation, infinite recursion, or topology-clean textured GLB export.

当前最合适的论文定位是：**一个生成模型原生的递归 sparse-latent grammar 框架，加上 occupancy-primary 连通性不变量和有限深度资产生成证据**。SIGA-level 还需要的不是更多漂亮图，而是 novelty-critical baseline、projection/naturalization ablation、effective-resolution 证据、seed/root robustness 和严格主图-指标绑定。
