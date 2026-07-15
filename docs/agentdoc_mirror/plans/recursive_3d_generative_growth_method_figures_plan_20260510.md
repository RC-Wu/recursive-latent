# Recursive 3D Generative Growth 方法图 Ralph Plan（2026-05-10）

## 任务边界

本轮身份是“画图助手”。目标不是新增算法实验，而是读取当前 `paper_siga/main.tex`，把论文中所有需要解释方法的示意图找出来，设计发表级图形逻辑，并产出可编辑的 SVG/PNG/PDF 粗稿，供后续论文排版和人工精修。

硬约束：

- 先使用本地已有 case、中间态和渲染资产。
- 找不到必要中间态时，最多开 1 个 SSH shell 到 `a100-2`，最多使用 1 张 GPU 补生成。
- 图形必须服务论文 claim，不能只做漂亮流程图。
- 每个图要说明：放在论文哪里、支撑什么 claim、读者如何阅读、需要哪些素材、当前素材是否足够。
- Ralph loop：每完成一个有意义步骤，在本 plan 的“进度日志”追加记录，并同步镜像到本地 `docs/agentdoc_mirror/plans/`。

## 从 main.tex 识别出的解释性图需求

当前 `main.tex` 已经有大量结果图。真正需要本轮系统设计的“示意图/方法图”有以下六类：

1. **主方法总图：PS-RSLG overview**
   - 当前文件：`paper_siga/figures/method_system_ps_rslg_tog_draft_20260509.pdf`
   - 当前 label：`fig:method-overview`
   - 作用：定义 Projection-Stabilized Recursive Sparse-Latent Grammar 的整体故事。
   - 问题：已有图能表达模块，但仍偏 slide-like；需要更强的论文图逻辑、更少背景卡片、更清楚的“冻结 Trellis2 substrate + 我们的 grammar/projection loop”关系。

2. **Trellis2 sparse substrate / generator pipeline 图**
   - `main.tex` 仍有 TODO：`image/mesh condition -> sparse support/features -> decoder -> mesh/PBR asset`
   - 作用：说明我们不是黑箱调用 3D 生成器，而是把 Trellis2 当作 sparse codec / local realization prior。
   - 需要展示 O-Voxel、Shape-SLAT、decoder/re-encoder、texture/PBR export。

3. **Projection/admissibility gate 图**
   - `main.tex` TODO：`invalid orphan tokens become inactive vs model-proposed connector under mask vs re-encoded admissible state`
   - 作用：解释为什么 projection 必须在每个 depth 内部执行，而不是 final-only cleanup。
   - 需要和现有 projection ablation mesh 图配合：一个讲机制，一个讲结果。

4. **Operator scheduling / sparse competition 图**
   - `main.tex` TODO：`active handles, candidate frontier tokens, collision rejections, accepted attached proposal, next-depth handles`
   - 作用：把 space competition 从工程实现提升为方法模块：同一 sparse support 上的 handles 竞争 occupancy，避免重复占用，形成 rooted connected growth。

5. **Masked local naturalization / sampler role 图**
   - 与 `main.tex` 中 no-naturalization / masked / global repair 等 ablation 关联。
   - 作用：把生成模型采样过程纳入方法框架：grammar 提供可验证结构，Trellis2 sampler 在局部 mask 内自然化几何和纹理，projection 保持 admissible state。

6. **Recursive zoom / effective resolution 图**
   - `main.tex` TODO：recursive effective resolution, zooms。
   - 作用：说明递归资产不是一次性全局生成，而是沿 grammar handles 局部重进入 sparse codec，实现尺度递进和 zoom-in 展示。

补充候选图：

7. **Classical procedural systems as restricted PS-RSLG families**
   - 作用：公式框架图/表，说明 IFS、L-system、space colonization、DLA、symmetry/tiling 是我们 grammar 的限制情形。
   - 这张更适合作为方法 section 的小图或 supplement 图。

## 推荐图形系统

统一风格：

- 白底或极浅暖灰底，不使用大面积渐变。
- 核心颜色采用 Okabe-Ito / 色盲友好色：
  - Sparse/Trellis codec：蓝 `#0072B2`
  - Grammar/operators：绿 `#009E73`
  - Projection/admissibility：朱橙 `#D55E00`
  - Frozen prior / decoder：灰 `#7B858F`
  - Invalid/orphan：红 `#C85A4A`
  - Texture/PBR：赭金 `#CC79A7` 或 `#B8860B` 少量点缀
- 真实 case 缩略图优先使用已有 mesh/render，不使用 point cloud 和 matplotlib 点云。
- 每张图最多 2 层视觉层级：主流程 + 少量证据 inset。避免 dashboard 式堆叠。

## 每张图的详细设计

### Figure A：主方法总图（推荐替换/迭代 fig:method-overview）

**核心 claim**：PS-RSLG 是一个在冻结 Trellis2 sparse substrate 上执行的递归生成语法。Grammar 负责 typed symbols/anchors/transforms，Trellis2 负责 local realization and materialization，projection 让每步状态回到 admissible sparse-latent manifold。

**版式 A1（推荐，TOG horizontal loop）**

左：Root / condition and Trellis2 substrate

- 输入 root mesh/render + guide image。
- `Encode -> O-Voxel support V_d -> Shape SLAT F_d -> typed handles A_d`。
- Trellis2 模块标注为 frozen substrate，不抢方法主体。

中：PS-RSLG loop

- `Select handles -> Apply grammar rules -> Emit masked sparse proposals -> Local sampler -> Decode -> Project -> Re-encode`
- Projection gate 放在 loop 的最醒目位置，使用橙色边框。
- 在 loop 下方放状态公式：`S_d=(V_d,F_d,A_d,M_d,C_d)`，`S_{d+1}=P(E(D(G_\theta(R_\phi(S_d),\xi_d))))`，但不要塞太满。

右：Outputs and evidence

- Textured mesh/PBR asset。
- 三个小缩略图：vine/root、coral/DLA、pyrite/crystal。
- 小指标条：connected support、depth control、PBR export。

**版式 A2（备选，two-layer architecture）**

上层是冻结 Trellis2 pipeline，底层是我们递归 grammar loop，中间用 sparse state interface 连接。优点是 Trellis2 关系清楚；缺点是 loop 动势弱。

**本地素材**

- Trellis sparse 中间态：`visuals/trellis2_mesh_first_reconstruct_20260507_1745/*/{input_normalized_preview,ovoxel_roundtrip_preview,shape_slat_reconstruct_preview}.png`
- Textured output：`paper_siga/figures/vine_depth_textured_strip_20260509_vizworker.png`、`pyrite_hq_depth_textured_showcase_20260509.png`、`coral_depth_textured_showcase_rerun1640_20260509.png`

### Figure B：Trellis2 substrate / sparse generator pipeline

**核心 claim**：Trellis2 在本文中提供可反复进入的 sparse codec：条件 mesh/image 被转成 O-Voxel support 和 Shape-SLAT features，局部 masked sampler 可在固定支持附近补全/自然化，decoder 输出 mesh/PBR，re-encoder 把结果送回递归状态。

**版式 B1（推荐，codec strip）**

一条清晰横向管线：

`condition/root` -> `O-Voxel support` -> `Shape-SLAT features` -> `masked sampler / flow prior` -> `mesh decoder` -> `texture/PBR export`

在 `O-Voxel` 和 `Shape-SLAT` 两个框下方直接嵌入现有 preview 图。右侧放一张 textured GLB 小图。

**版式 B2（备选，interface view）**

画成“我们可读/可写的接口”：read `V,F,A`，write masked proposal `\Delta V,\Delta F`，Trellis2 owns decode/re-encode。

### Figure C：Projection/admissibility gate

**核心 claim**：projection 不是后处理，而是 recursive transition 的一部分。它把 decoded proposal 转为下一步可递归的 admissible sparse state，防止 orphan tokens 和 invalid handles 继续扩散。

**版式 C1（推荐，before/after gate）**

左：raw proposal，绿色 root-connected component + 红色 orphan fragments。

中：projection gate `P_\mathcal{A}`，内含三步：

1. support connectivity / root reachability；
2. masked connector or deactivate invalid tokens；
3. re-encode to `S_{d+1}`。

右：admissible state，只有绿色 connected support，active handles 在边界上。

下方小条：Direct recursion / Final-only / Per-depth projection 三种策略对比，用已有 ablation render 做 evidence inset。

### Figure D：Operator scheduling / sparse competition

**核心 claim**：space competition 是 sparse-native grammar execution，不只是传统 space colonization。多个 handles 在同一 occupancy lattice 上竞争候选 tokens，冲突 token 只能由一个 owner 接收，被拒绝 proposal 不能形成 disconnected mesh。

**版式 D1（推荐，frontier ownership map）**

左：active handles `a_i` 和 frontier token set `F_i`。

中：candidate proposals with ownership/NMS：

- green accepted attached tokens；
- red rejected collisions；
- gray already occupied support；
- arrow to next handles。

右：增长后的 connected support + 指标：`collision reject rate`、`LCR`、`frontier coverage`。

### Figure E：Masked local naturalization / sampler role

**核心 claim**：采样器进入 grammar transition，而不是单纯纹理美化。Grammar 给出 hard constraints / mask / anchors，Trellis2 flow sampler 在局部 mask 内把 scaffold naturalize 为可渲染 mesh/PBR，同时 projection 回收状态。

**版式 E1（推荐，local mask + noise schedule）**

左：blocky scaffold with editable mask。

中：noise schedule / local flow repair，anchor region clamped。

右：naturalized textured mesh。

下方小型 ablation：rule-only / global repair / masked local repair。

### Figure F：Recursive zoom / effective resolution

**核心 claim**：递归深度提供局部有效分辨率：每个 depth 不是简单全局放大，而是在 selected handles 上重新进入 sparse codec；zoom-in 图应展示同一 asset 在 overview、mid-level、terminal-level 的结构连续性。

**版式 F1（推荐，asset + recursive call tree）**

左：overview render，3 个嵌套 zoom boxes。

中：递归调用树 `root -> branch -> terminal`，每个节点带 `decode/project/re-encode` 小环。

右：三层 zoom-in 实图（vine 或 pyrite），用已有 matched camera zoom render。

## 粗稿产出计划

输出目录：

- `paper_siga/figures/method_diagram_drafts_20260510/`

计划产物：

- `figure_A_main_method_overview.svg/.png/.pdf`
- `figure_B_trellis_substrate_pipeline.svg/.png/.pdf`
- `figure_C_projection_gate.svg/.png/.pdf`
- `figure_D_operator_competition.svg/.png/.pdf`
- `figure_E_masked_naturalization.svg/.png/.pdf`
- `figure_F_recursive_zoom.svg/.png/.pdf`
- `method_diagram_drafts_contact_sheet.png`
- `method_diagram_design_plan_zh_20260510.md`

初稿原则：

- 先保证结构、逻辑、claim 对齐；不追求最终美术。
- 尽量嵌入已有真实 render/preview，缺图位置用明确 placeholder 标出。
- 只要本地素材能支持解释，就不启动远端生成。

## 进度日志

- 2026-05-10 06:24:52 CST：读取 `main.tex` figure environments，确认方法图需求集中在主方法总图、Trellis2 substrate、projection gate、operator scheduling/space competition、masked naturalization、recursive zoom 六类；本地找到足够的 Trellis/O-Voxel/SLAT preview、textured mesh render、projection ablation、matched zoom 素材，暂不需要远端生成。

- 2026-05-10 06:34:00 CST：完成第一轮方法图粗稿与一次修正迭代。产出 6 张 SVG/PDF/PNG：A 主方法总图、B Trellis2 substrate、C projection gate、D operator/space competition、E masked naturalization、F recursive zoom；总览 contact sheet 位于 paper_siga/figures/method_diagram_drafts_20260510/method_diagram_drafts_contact_sheet.png。同步写入中文设计文档 docs/figures/method_diagram_design_plan_zh_20260510.md。

- 2026-05-10 06:42:00 CST：补充两张备选/理论图：A2 two-layer architecture（强调冻结 Trellis2 substrate 与 PS-RSLG 的上下层关系）和 G classical-system coverage（IFS/L-system/space colonization/DLA/symmetry 作为 PS-RSLG 限制情形）。contact sheet 更新为 8 张图。
