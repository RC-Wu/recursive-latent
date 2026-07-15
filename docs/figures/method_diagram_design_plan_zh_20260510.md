# 方法图与示意图设计方案（2026-05-10）

对应 plan：`/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_method_figures_plan_20260510.md`

本轮读取了当前 `paper_siga/main.tex` 的所有 figure environment，并把“结果图”和“解释性方法图”分开处理。论文里已有大量结果图；真正需要单独设计、会影响方法论表达的图主要是以下六类。第一版 SVG/PDF/PNG 粗稿已经生成在：

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/method_diagram_drafts_20260510/`

总览预览图：

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/method_diagram_drafts_20260510/method_diagram_drafts_contact_sheet.png`

## 总体判断

目前论文最缺的不是“再多一张漂亮流程图”，而是把 PS-RSLG 的方法 claim 用图形固定下来：

1. 我们的主体是 **recursive sparse-latent grammar**，不是简单 Trellis2 wrapper。
2. Trellis2 的角色应画成 **frozen sparse codec / local realization prior**，提供 O-Voxel、Shape-SLAT、masked sampler、decoder/re-encoder、texture/PBR export。
3. Projection 必须画成 **transition 内部的 admissibility operator**，不是后处理。
4. Space competition 必须画成 **sparse-native ownership / frontier scheduling**，从而解释连通性和非重复占用。
5. Masked naturalization 必须画成 **生成模型采样过程进入语法转移**，而不是只在最后美化。
6. Recursive zoom 必须画成 **局部重进入 sparse codec 的多尺度机制**，支撑“effective resolution”和 zoom-in claim。

## Figure A：主方法总图

输出：

- `figure_A_main_method_overview.svg`
- `figure_A_main_method_overview.pdf`
- `figure_A_main_method_overview.png`
- 备选：`figure_A2_two_layer_architecture.svg/.pdf/.png`

推荐放置位置：替换或迭代当前 `fig:method-overview`。

当前粗稿采用三栏：

1. 左栏：Trellis2 sparse substrate，包括 root/condition、O-Voxel、Shape-SLAT、state interface、decoder/re-encoder。
2. 中栏：PS-RSLG recursive transition loop，包括 handle selection、typed grammar rules、masked sampler、decode、projection、re-encode。
3. 右栏：mesh/PBR assets and evidence，包括 vine、crystal、coral 结果缩略图和核心 claim 条。

这版的优点是主故事很清楚：Trellis2 是 substrate，我们的方法是中间的 recursive transition，projection 在 loop 内部。缺点是 still diagrammatic，真实 case 嵌入较小，最终发表版建议把右侧结果缩略图换成裁切后的高质量单体，而不是整张 contact strip。

备选版：

- A2：上下两层架构图。上层画冻结 Trellis2 pipeline，下层画 grammar/projection loop，中间只用 sparse state interface 连接。适合在 reviewer 质疑“到底用 Trellis2 的哪一层”时使用。本轮已经生成粗稿 `figure_A2_two_layer_architecture.*`。
- A3：以公式为中心的 state-machine 图。把 `S_d=(V_d,F_d,A_d,M_d,C_d)` 和 `S_{d+1}=P_A(E(D(G_\theta(R_\phi(S_d),\xi_d))))` 放中间，四周挂 classical operators。适合作为方法 section 的补充图，不适合作主图。

## Figure B：Trellis2 substrate / sparse generator pipeline

输出：

- `figure_B_trellis_substrate_pipeline.svg`
- `figure_B_trellis_substrate_pipeline.pdf`
- `figure_B_trellis_substrate_pipeline.png`

推荐放置位置：`main.tex` 当前 TODO “image/mesh condition -> sparse support/features -> decoder -> mesh/PBR asset” 附近。

当前粗稿是一条横向 codec strip：

`root / guide -> O-Voxel support -> Shape-SLAT features -> masked flow realization -> mesh decoder + projection -> textured GLB/PBR export`

这张图的目的不是复刻 Trellis2 官方图，而是讲清楚本文访问的接口：`V`、`F`、mask、decoder/re-encoder、PBR export。图里已经用了本地已有 O-Voxel 和 Shape-SLAT preview，不需要远端补图。

后续精修建议：

- 如果能拿到更清楚的 O-Voxel/SLAT token render，替换当前较小 preview。
- `masked flow realization` 当前是抽象点图；如果之后能保存 sampler 中间态，可替换为真实中间 latent/mesh half-step。

## Figure C：Projection/admissibility gate

输出：

- `figure_C_projection_gate.svg`
- `figure_C_projection_gate.pdf`
- `figure_C_projection_gate.png`

推荐放置位置：projection subsection，紧接机制定义，早于 projection ablation 结果图。

当前粗稿结构：

1. Raw decoded proposal：绿色 connected tokens + 红色 orphan tokens。
2. `P_A` gate：root reachability、connect/deactivate、re-encode。
3. Admissible next state：只保留可继续递归的 attached frontier handles。
4. 下方 evidence inset：direct / final-only / per-depth projection 的已有 mesh ablation 联系。

这张图应支撑一个强 claim：projection 是递归状态转移的一部分，final-only cleanup 不能阻止错误 handles 在后续深度继续扩散。

后续精修建议：

- 把下方 evidence inset 换成三张裁切更干净的 per-depth/direct/final-only 单图，避免当前 contact sheet 太扁。
- 在 caption 或图内小字中明确 `P_A: \tilde{S}_{d+1} -> S_{d+1}\in\mathcal{A}`。

## Figure D：Operator scheduling / sparse competition

输出：

- `figure_D_operator_competition.svg`
- `figure_D_operator_competition.pdf`
- `figure_D_operator_competition.png`

推荐放置位置：grammar/operator 或 space competition subsection。

当前粗稿结构：

1. Active handles，各自产生候选 frontier tokens。
2. Frontier ownership map：绿色 accepted，红色 collision rejected，灰色 occupied。
3. Connected next support：输出仍是 rooted connected support，并产生下一轮 handles。

这张图要把“空间竞争”从传统启发式提升为本文语法执行的核心模块：不是让多个局部片段随便生成，而是在同一个 sparse occupancy 上先完成 ownership resolution。

后续精修建议：

- 增加一个小公式：`o(v)=argmax_i s_i(v)` and reject if `v in V_d` or disconnected。
- 如果实验里已有 collision reject rate / LCR 曲线，可以在右下角放一条微型 sparkline。

## Figure E：Masked local naturalization / sampler role

输出：

- `figure_E_masked_naturalization.svg`
- `figure_E_masked_naturalization.pdf`
- `figure_E_masked_naturalization.png`

推荐放置位置：naturalization / flow sampler / ablation subsection。

当前粗稿结构：

1. Rule scaffold：结构规则给出 support 和 editable mask。
2. Masked flow sampler：局部噪声调度，anchors clamped。
3. Naturalized mesh/PBR：输出可渲染 textured mesh。
4. 底部一行讲 ablation story：rule-only、global repair、masked local repair。

这张图的关键是把生成模型采样过程纳入理论框架。它不应该被写成“我们最后给 mesh 上纹理”，而应写成“采样器作为 grammar transition 的 realization operator”。

后续精修建议：

- 如果之后能导出同一 case 的 rule-only mesh、global repair mesh、masked repair mesh，替换当前抽象点图。
- 当前 naturalized output 用整张 contact sheet，最终版应改成单一高质量 case。

## Figure F：Recursive zoom / effective resolution

输出：

- `figure_F_recursive_zoom.svg`
- `figure_F_recursive_zoom.pdf`
- `figure_F_recursive_zoom.png`

推荐放置位置：depth/parameter control 或 effective resolution subsection。

当前粗稿结构：

1. 左：同一 asset 的 overview，标出嵌套 zoom box。
2. 中：recursive call tree，每个 terminal 表示一次局部 re-entry。
3. 右：同一 vine case 的多尺度 zoom evidence。

这张图可用于支撑“递归深度带来局部有效分辨率”的展示逻辑。注意它不是定量消融，而是方法行为图。

后续精修建议：

- 右侧应该优先使用视觉质量最高、语义最清楚的 vine/root 或 pyrite case。
- 如果要展示 infinite/long-horizon recursion，需要把中间 call tree 改成 sliding window / LOD cache 图，而不是普通树。

## Figure G：Classical procedural systems as restricted PS-RSLG programs

输出：

- `figure_G_classical_system_coverage.svg`
- `figure_G_classical_system_coverage.pdf`
- `figure_G_classical_system_coverage.png`

推荐放置位置：方法 section 的 formal grammar 小节，或 supplement 的框架/表达能力小节。

当前粗稿把五类传统系统映射到 PS-RSLG rule family：

- IFS -> copy / transform rules
- L-system -> typed handle expansion
- Space colonization -> frontier ownership map
- DLA / frontier -> masked stochastic growth
- Symmetry / tiling -> equivariant transform family

这张图对当前论文很重要，因为它可以直接回应“方法看起来像工程模块拼接”的批评：我们不是列模块，而是在一个统一 state `S_d=(V_d,F_d,A_d,M_d,C_d)` 上把传统 procedural family 写成限制情形，再用 Trellis2 sparse prior 补充自然化和可渲染资产输出。

后续精修建议：

- 每一列最好加一条对应公式，例如 IFS 的 contraction map、L-system 的 rewrite、space competition 的 ownership、DLA 的 frontier probability、symmetry 的 group action。
- 如果主文页数紧，这张图可以压缩成表格；如果方法论争议大，建议保留为主文图。

## 素材清单与缺口

已使用本地素材：

- Trellis intermediate：
  - `visuals/trellis2_mesh_first_reconstruct_20260507_1745/ifs_branch_tree_r512/input_normalized_preview.png`
  - `visuals/trellis2_mesh_first_reconstruct_20260507_1745/ifs_branch_tree_r512/ovoxel_roundtrip_preview.png`
  - `visuals/trellis2_mesh_first_reconstruct_20260507_1745/ifs_branch_tree_r512/shape_slat_reconstruct_preview.png`
- Textured mesh / PBR result：
  - `paper_siga/figures/vine_depth_textured_strip_20260509_vizworker.png`
  - `paper_siga/figures/pyrite_hq_depth_textured_showcase_20260509.png`
  - `paper_siga/figures/coral_depth_textured_showcase_rerun1640_20260509.png`
  - `paper_siga/figures/texture_latest_occpos_paperstyle_contact_20260509.png`
- Projection / zoom：
  - `paper_siga/figures/projection_ablation_pure_white_flat_contact_rerun2105_20260509.png`
  - `visuals/matched_camera_zoom_existing_roots_20260510/vine_stage5/{overview_raw,zoom_01,zoom_02}.png`

本轮没有使用远端生成，因为已有本地素材足以支撑第一版方法图。

仍缺的高价值素材：

1. 真正可视化的 sparse feature / token ownership map，而不是示意方块。
2. 同一 case 的 rule-only、masked local repair、global repair 三联图。
3. 更干净的 projection before/after 单图裁切。
4. sampler 中间步或半生成 mesh，用于 Figure E。

## 下一轮迭代优先级

1. **先精修 Figure A 和 C**：这两张决定方法是否可信。A 要替换现有 `fig:method-overview`；C 要补掉 projection TODO。
2. **再精修 Figure B**：明确 Trellis2 substrate 后，文章里关于模型使用边界会更稳。
3. **D/E/F 可先作为方法 subsection 小图或 supplement**：等相关实验图和 ablation 更成熟后再决定是否进主文。
4. **把 SVG 交给 Illustrator/Inkscape 或 PPT 人工排版**：当前 SVG 是结构草稿，后续应裁图、统一字号、减少小字、提高真实结果图占比。
