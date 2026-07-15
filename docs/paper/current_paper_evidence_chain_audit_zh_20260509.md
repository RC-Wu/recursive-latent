# Current Paper Evidence Chain Audit, reviewer view

日期：2026-05-09

范围：本文只根据 `/Users/fanta/Downloads/论文修改意见与reviewer批评整理.md`、当前 `paper_siga/main.tex`、`docs/paper/current_story_risk_audit_zh_20260509.md`、`docs/figures/depth_parameter_showcase_paper_use_zh_20260509.md` 以及 `main.tex` 当前引用的本地图表/表格判断证据链。本文不修改 `main.tex`。

## 1. 当前可投故事的最强版本

当前最强、最可审稿的故事不是“我们解决了递归 3D 生成的所有拓扑和材质问题”，而是：

> 冻结 3D 生成模型的 sparse latent 可以作为递归程序状态，但 direct sparse edit、global repair、final-only cleanup 会让碎片、拓扑漂移或无效 frontier 进入下一层递归。因此，递归语言必须由 grammar 控制 sparse support、anchors、attachment 和 rule proposal；冻结 Trellis2 只作为局部 masked prior、decoder/re-encoder 和 selected texture export path。核心贡献是把 projection 放进每一层 recursive transition，使 connected voxelized support 成为有限深度递归的执行不变量，而不是最终 mesh cleanup。

这个故事与当前 `main.tex` 已经基本一致：摘要和引言已经转向 “generation-model-native recursive language over sparse 3D latents”；方法部分已经用 `z_d=(V_d,F_d,A_d)`、rule template、masked flow naturalization、decode-project-encode transition 替代旧版大 tuple；实验部分也明确把当前 claim 收窄为 per-depth projection 的 finite-depth stability 和 selected projected meshes 的 Trellis2 texture/PBR export compatibility。

最强证据集中在三类：

1. **Projection ablation / metric evidence**：Table `projection-ablation` 中 conservative competition 的 vine/tree matched ablation 最像正式论文证据。`vine compete d3` 从 direct comps `2059`、final-only kept `2` 到 per-depth kept `1`、LCR `1.0000`；`tree compete d3` per-depth kept `2`、LCR `0.9949`。但 fork variants 明确暴露边界。
2. **Claim-aligned connectivity evidence**：`claim_aligned_metric_summary` 显示 vine/root/tree、bismuth、pyrite、volumetric coral 的 occupancy proxy 可达到 `occ_comp=1`、`occ_lcr=1.000`；同时也公开 raw mesh/face fragmentation caveat，例如 vine textured GLB face components `85381-107213`、face LCR `0.001-0.002`。
3. **Mesh/textured-mesh visual evidence**：主文已有 true Trellis2 textured GLB renders、programmatic PBR mesh renders、neutral mesh renders的协议区分。`vine_depth_textured_strip`、`depth_parameter_main_candidate`、`depth_parameter_mesh_showcase_zoom`、`bismuth_depth_textured_showcase`、`coral_depth_textured_showcase` 可以支撑 selected method-behavior 和 export compatibility，但不能单独证明 ablation、物理生长或 topology-clean mesh。

最安全的投稿措辞应是：**projection-stabilized recursive sparse-latent grammar supports finite-depth recursive assets with connected occupancy support and selected textured-mesh export compatibility**。所有关于 DLA/crystal physics、raw mesh topology clean、material recursion consistency、infinite generation、strict monotonic parameter control 的表述都必须降级或移到 limitation/supplement。

## 2. Claim 证据链表

| Claim in current `main.tex` | 当前证据 | 证据类型 | 风险 | 下一步 |
|---|---|---|---|---|
| 生成模型原生 sparse latent 可作为递归语言状态，grammar owns topology，generator supplies local priors。 | `main.tex` 方法部分已有 minimal state `z_d=(V_d,F_d,A_d)`、rule template、masked flow clamp、decode-project-encode transition；方法图 `method_system_ps_rslg_v3_20260509.pdf` 对应这个叙事。 | method/formalism + method figure | 这是方法定义，不是实验结果；如果读者要求“为什么必须这样”，仍需要 trivial baselines 的可见失败证据闭环。 | 在实验中把 2D scaffold、direct sparse edit、global repair、final-only cleanup 与 proposed 对齐到同一 claim-driven subsection。 |
| Direct use of 3D generator / 2D scaffold / global repair / final-only cleanup 不稳定。 | 引言和 Results 有文字说明；Table `projection-ablation` 直接覆盖 direct recursion 与 final-only cleanup；但 2D scaffold 和 full/global flow repair 的可视化/数值证据未在当前主文中形成完整表格。 | metric table for direct/final-only; partial textual evidence for 2D/global repair | “trivial ways fail” 是强动机，但当前证据展示不均衡。reviewer 会要求看到同条件失败图或明确 baseline 表。 | 补一个 compact diagnostic figure/table：2D condition、direct sparse edit、global flow repair、final-only cleanup、per-depth projection，同 root/depth/renderer。 |
| Per-depth projection stabilizes finite-depth recursive growth better than direct recursion and final-only cleanup。 | Table `projection-ablation`: vine compete d3 per-depth kept `1`, LCR `1.0000`; tree compete d3 per-depth kept `2`, LCR `0.9949`; direct/final-only 数值较差。`projection_depth_curves` 和 `space_competition_depth_curves_tokens` 支撑跨 depth 趋势。 | table + metric curves | 证据最强，但主要强在 conservative competition；fork variants 的 per-depth LCR `0.5758/0.6141` 不能包装成成功。 | 结果小节按 operator family 分层：competition 是正证据，fork/radial/echo 是 boundary evidence。表 caption 明确 LCR/comp 的计算对象。 |
| Projection turns connected support into recursive invariant, not final cleanup。 | 方法中有 admissible state、projection steps、final-only cleanup insufficiency 论证；Table `projection-ablation` 是对应实证。 | method proof sketch + ablation metric | Projection 实际算法仍容易被问：mesh-level 还是 voxel-level、root attachment 如何找、threshold 如何选、handle 如何 reattach。 | 保留或加强 Algorithm 2 风格 projection procedure，并在 metric section 定义 occupancy 6N proxy、root ratio、kept component。 |
| 支持 depth-5 vine/root growth。 | `claim_aligned_metric_summary` 中 `vine_d5_projected_compete` 为 `occ_comp=1`, `occ_lcr=1.000`，但 mesh/face comp `85381-107213`、face LCR `0.001-0.002`。主文 `vine_depth_textured_strip` 是 d=1..4 的 true textured GLB depth progression。 | metric + textured mesh figure | 若摘要写 depth-5，而主文最清晰 visual strip 只显示 d=1..4，会有 visual closure gap；raw face fragmentation 不能支持 topology-clean GLB。 | 要么补 depth-5 visual/neutral QA，要么把主文可见 figure 写成 depth progression selected stages，并把 depth-5 作为 metric-only run。 |
| Branching/root/tree conservative competition 是当前最强成功案例。 | Projection ablation 和 matched structural baseline matrix 均覆盖 tree/root/vine；matched matrix 中 L-system、space colonization、connected scaffold proxy 都可达到 occupancy connected，说明公平 protocol 下不是单纯“我们更连通”。 | table/metric + mesh renders | matched structural matrix 是 sanity/fairness check，不是 superiority evidence；branch/tip morphology 还缺和 baseline 的更强解释。 | 主文明确：强证据是 direct/final-only/proposed ablation；matched classical matrix 是 fairness check。补 branch/tip/path span 指标对比。 |
| Frontier-growth / coral / DLA-inspired scaffold 可做 connected depth behavior。 | `volumetric_coral_depth` 在 claim summary 中 `occ_comp=1`, `occ_lcr=1.000`, mesh/face comp `1-12`、LCR `0.999-1.000`；`coral_depth_textured_showcase` 和 depth/parameter figures 提供 textured/mesh visual。 | textured mesh + metric | 只能写 connected coral/DLA-inspired scaffold；不能写 DLA physics 已解决。`dla_bridge_ablation` 仍是 `occ_comp=4-9`、LCR `0.387-0.961` 的 negative/partial result。 | Coral 作为 grammar-native connected scaffold 正例；DLA bridge ablation 放 failure/diagnostic，补 fake bridge/over-closing label。 |
| Bismuth / pyrite crystal-inspired non-tree depth control。 | `bismuth_hopper_depth` `occ_comp=1`, `occ_lcr=1.000`, mesh/face comp `2-4`; `pyrite_lattice_depth` `occ_comp=1`, `occ_lcr=1.000`, mesh/face comp `1-139`; `bismuth_depth_textured_showcase` 提供 textured visual。 | textured mesh + metric | 不能写真实晶体生长或物理 faceting；pyrite mesh components 到 `139`，不适合做主文核心成功拓扑证据。 | 主文如需非树类，优先 bismuth；pyrite 放 supplement 或 boundary case，并补 facet/contact/symmetry/cavity metrics。 |
| Transform-copy / portal / architecture / hard-surface examples 可进入 selected asset export path。 | Texture QA table 中 crown portal、scifi translate、snow arch、island city scale-down 等 GLB export status 为 ok；result matrix 有对应 mesh/textured panels。 | textured mesh/export table | 当前主要证明 export/import/render compatibility，不证明 transform-copy topology 稳定或语义质量。 | 给 transform-copy 单独补 metric row：component/LCR、symmetry error、motif preservation、visual zoom；否则作为 qualitative breadth。 |
| Trellis2 texture/PBR export 对 selected projected meshes 技术可行。 | Texture QA table 列出 vine/root compete `26.81 MB`, tree compete `27.59 MB`, crown portal `38.48 MB` 等；`vine_depth_textured_strip`、teaser、green protocol panels 是 true textured GLB renders。 | textured mesh + table/export metric | Texture export 不是 recursive connectivity proof。材质质量 category-dependent，holes/thin sheets/material mismatch 仍存在。 | 在正文保持“selected projected meshes export compatibility”；不要写 “material recursion solved”。表格中避免 draft/smoke 语气。 |
| Programmatic PBR / neutral mesh renders 可用于 geometry QA。 | `result_matrix_mesh` caption 区分 green true Trellis2 GLB、blue programmatic PBR、gray neutral mesh；`vine_zoom_in_multiscale` 明确是 fixed programmatic PBR to expose geometry。 | mesh visual | 如果图中颜色太像 texture result，reviewer 可能误解协议。 | 图例和 caption 继续强制协议标签；主文只把 blue/gray 当 geometry visual QA。 |
| Traditional baseline texture diagnostic 支持 “texture alone is insufficient”。 | `traditional_baseline_texture` 和 matched-guide version：传统 baseline 通过同一 Trellis2 texture path 后仍有高 occupancy comps/低 LCR；story audit 给出 root `218/0.524`, tree `278/0.364`, L-system `315/0.115`, DLA `2511/0.002`。 | textured mesh + metric diagnostic | 这是 diagnostic baseline，不是 full fair baseline matrix；输入 root/category/guide 仍可能不完全一致。 | 写成 texture-path diagnostic；完整 baseline 仍需 same-root/same-depth/same-seed/same-renderer matrix。 |
| Matched structural baseline matrix 已经关闭公平 baseline 问题。 | 当前 input table 显示 tree/root/vine 下 L-system、space colonization、connected scaffold proxy 都可 `Occ comps=1`, `Occ LCR=1.0000`, `Root ratio=1.0000`。 | metric table | 它反而说明 classical methods 在 occupancy proxy 下也连通；不能作为 proposed superiority evidence。缺 one-shot Trellis2/direct/final-only/texture path 的完整同条件矩阵。 | 保留为 sanity/fairness check；真正 baseline closure 仍需 methods matrix：classical、one-shot、direct、final-only、per-depth proposed。 |
| Effective resolution / recursive refinement 超过 one-shot global pass。 | 方法中有 token budget/effective structural resolution 论述；`vine_zoom_in_multiscale` 和 depth figures 提供 overview/branch/terminal visual。 | method argument + mesh visual | 目前缺 metric：没有和 one-shot Trellis2、higher global grid、fixed-token budget 的可量化对比。 | 若保留为贡献，补 terminal detail metric、token allocation、depth vs local feature/branch density；否则写成 observation。 |
| Material handles and material propagation 是方法能力。 | `main.tex` 有 material handle method section；texture table 证明 selected export path 可跑通。 | method text + export table | 没有 per-depth material coherence、UV seam、material continuity 指标；不能把材质递归一致作为结果。 | 将 material section 写成 pipeline integration；结果只评估 export/import/render/channel availability。 |
| Depth/parameter figure 证明同条件控制能力。 | `depth_parameter_main_candidate_20260509.pdf`、`depth_parameter_mesh_showcase_zoom_20260509.pdf`、`coral_density_param_showcase_20260509.png` 均为 mesh/textured-mesh Blender renders；caption 已写明 fixed grammar family/guide/camera/renderer within row。 | mesh/textured mesh visual | 这是 method-behavior visualization，不是 ablation；coral density visible effect modest，occupied voxels/box-count 不严格单调。 | 主文只放 vine depth + coral depth，参数行可弱写或放 supplement；caption 必须继续写 “not an ablation”。 |
| DLA/radial/echo boundary cases 展示广度。 | `result_matrix_mesh`、teaser、texture QA table 中有 DLA radial/boundary case；claim summary 标红 DLA bridge negative/partial。 | mesh/textured mesh visual + negative metric | 如果放在主结果核心，会被当成失败证据；不支撑 solved porous/DLA claim。 | 放 supplement/failure analysis；主文只用作 stability-expression boundary。 |
| Infinite / unbounded recursion 或 world-scale extension。 | 方法 discussion 中仅有限深度 claim，并提 visible-window/cache descriptors。 | method speculation | 无实验证据；不能作为投稿 claim。 | 保持 limitation/extension 语气，标题和摘要避免暗示 infinite generation。 |

## 3. Depth / Parameter figure 的正确用法

用户新补充的判断是正确的：**同条件不同 depth / 不同参数控制的 case 可视化是方法展示，不是消融**。当前 `main.tex` 的两个 caption 已经接近正确写法：

- `depth_parameter_main_candidate_20260509.pdf`：写成 same-condition method-behavior cases，每行只改变一个 control variable，固定 grammar family、material/image guide、camera、renderer；明确 “not an ablation study”。
- `depth_parameter_mesh_showcase_zoom_20260509.pdf`：写成 same-condition method-behavior visualization with zoom crops；depth rows 展示 recursive enrichment；parameter row 是 qualitative control evidence，不是 calibrated monotonic response。
- `coral_density_param_showcase_20260509.png`：caption 已承认 visible parameter effect modest，更适合 supplement。

建议主文用法：

| Figure row / material | 适合位置 | 可写 claim | 不应写成 |
|---|---|---|---|
| Vine family depth `d=1..4`，带 branch/tip zoom | 主文 | same-condition recursive depth behavior；selected textured mesh progression；局部末端结构随 depth 改变 | projection ablation；depth-5 全视觉证明；texture quality uniform |
| Connected coral scaffold depth `d=1..4` | 主文或主文第二行 | depth control extends beyond vine/tree-like forms；connected scaffold geometric complexity increases | physical coral/DLA simulation；DLA bridge repair solved |
| Coral density/compactness parameter `lambda={0.45,0.70,0.95,1.20}` | Supplement 优先；主文仅在必须回应参数控制时作为第三行弱写 | fixed-stage parameter-control case display；可见但温和的外观变化 | strict ablation；monotonic metric response；strong controllability proof |
| Bismuth depth row | Supplement 或主文备选非树类 | crystal-inspired connected scaffold depth visualization | physical bismuth crystallization；face-welded topology |
| Pyrite depth row | Supplement/boundary | lattice scaffold occupancy connectedness | 主文核心成功案例；clean mesh topology |
| Full `depth_parameter_mesh_showcase_20260509` gallery | Supplement overview | multiple same-condition depth/guide-control examples | 主文核心证据矩阵 |

审稿写法建议：

> These figures visualize method behavior under controlled rendering and guidance conditions. They are not ablations: an ablation removes or changes a method component and reports a metric under matched conditions. Here, each row keeps the pipeline fixed and changes a program control variable, so the evidence is qualitative control/display evidence.

主文 caption 必须继续保留四个限制：固定条件、mesh/textured-mesh render、非 ablation、参数行非单调校准。

## 4. Reviewer 口吻：5 个最高风险点与修补动作

### 风险 1：occupancy connectedness 被误读成 clean mesh topology

当前最强指标是 voxel-occupancy 6-neighborhood connectedness，不是 raw mesh/GLB face connectivity。vine textured GLB 的 raw face components `85381-107213`、face LCR `0.001-0.002` 是不能回避的反证。如果论文写 “connected mesh” 或 “topologically clean GLB”，reviewer 会直接否定。

修补动作：
- 全文统一写 “connected occupancy support / voxelized support”，避免 “topologically clean mesh”。
- Table/Figure caption 明确 raw face components 是 diagnostic caveat。
- 对主文最强案例补 neutral mesh QA、welded tolerance diagnostics、root path ratio；但即使补了，也不要删除 occupancy 与 face topology 的边界说明。

### 风险 2：baseline closure 仍不完整

`projection-ablation` 能支撑 direct vs final-only vs per-depth；`matched structural baseline matrix` 能说明 classical baselines 在同条件 occupancy proxy 下也连通；traditional texture baseline 能说明 texture alone insufficient。但这三者还不是一个完整、公平、统一的 baseline matrix。reviewer 仍会问：one-shot Trellis2、image-entry recursion、direct sparse grammar、full flow repair、masked flow、final-only、proposed 是否同 root/seed/depth/camera/renderer？

修补动作：
- 补同 root、同 depth、同 seed、同 renderer 的 tree/root/vine baseline matrix。
- Methods 至少包括 L-system、space colonization、one-shot/image-entry Trellis2、direct sparse edit、global/full flow repair、final-only cleanup、per-depth proposed。
- Metrics 至少包括 `occ_comp_6n`、`occ_lcr_6n`、root ratio、orphan mass/tips、branch/tip counts、path span、render success。

### 风险 3：depth/parameter figure 若被当成 ablation，会削弱论文严谨性

同条件 depth/parameter 可视化是展示 method behavior，不是 component ablation。尤其 coral density 参数目前视觉差异温和，且指标不严格单调；如果写成 “parameter ablation proves controllability”，证据不够。

修补动作：
- 主文 caption 保持 “not an ablation study”。
- 主文优先使用 vine depth + coral depth 两行；参数行弱写或放 supplement。
- 如要做真正 ablation，必须改变方法组件，如 no projection/final-only/no masked clamp/no bridge certificate，并报告 matched metrics。

### 风险 4：texture/PBR export 容易被写成 material recursion 成功

当前 Trellis2 texture/PBR path 证明 selected projected meshes 可以导出 inspectable GLB，不证明材质递归一致，也不证明结构正确。`main.tex` 已经较好地区分 green true GLB、blue programmatic PBR、gray neutral mesh，但 reviewer 仍可能质疑图中视觉协议混合。

修补动作：
- 结果分成 geometry recursion、texture/export compatibility 两条证据链。
- 所有 programmatic PBR 图只写 geometry QA，不写 Trellis2 texture result。
- Texture table 的 `ok` 只代表 export/import/render path；补 UV seam/material continuity/render warning 字段会更严谨。

### 风险 5：scope overclaim：DLA/crystal/infinite/effective resolution 都还缺闭环

DLA bridge ablation 仍是 partial/negative；pyrite 有 occupancy connectedness 但 mesh components 可到 `139`；bismuth/coral 是 scaffold-connected visual，不是物理生长；effective resolution 目前主要是论述和 zoom visual，缺 one-shot/token-budget metric；infinite recursion 只是 extension。

修补动作：
- DLA/radial/echo 放 boundary/failure/supplement，不做主 claim。
- Crystal 类写 “crystal-inspired scaffold”，不写 physical crystallization。
- Effective resolution 若作为贡献，需要补 depth-vs-detail、token allocation、one-shot comparison；否则降级为 qualitative multi-scale observation。
- Infinite/visible-window 只放 discussion，不放摘要贡献。

## 5. 总体结论

当前 `main.tex` 的论文方向比 reviewer 批评中的旧版强很多：叙事已经从“procedural + generator 拼接”转成 “generation-model-native recursive language”，方法也已经从大 tuple / 长算子链转成更清晰的 sparse-latent state、rule template 和 projection-stabilized transition。

但证据链必须收窄到当前真能支撑的版本：**per-depth projection 对 finite-depth recursive sparse-latent programs 的 occupancy connectedness 有最强证据；selected projected meshes 可以进入 Trellis2 textured GLB export path；depth/parameter figures 是同条件方法行为展示，不是 ablation。**

如果按这个边界写，当前故事可以投出一个诚实且有核心贡献的版本。如果写成 topology-clean textured asset generation、solved DLA/crystal growth、material recursion consistency、或严格参数可控，证据会被 reviewer 轻易击穿。
