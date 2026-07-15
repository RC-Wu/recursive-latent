# 用户重复要求完成情况验收矩阵 - 2026-05-08

本文依据当前本地文档与最近中文状态材料汇总，不运行远端命令，不新增实验结果。重点读取材料包括：

- `/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_system_grammar_plan_20260508.md`
- `docs/theory/formal_recursive_generative_grammar_v2_zh_20260508.md`
- `docs/evaluation/space_competition_metric_protocol_v2_zh_20260508.md`
- `docs/paper/siga_paper_story_and_writing_plan_v2_zh_20260508.md`
- `docs/visuals/open_image_model_and_public_guides_status_zh_20260508.md`
- `docs/baseline_mesh_visual_status_zh_20260508.md`
- `docs/evaluation/mesh_metric_sweep_status_zh_20260508.md`
- `docs/obsidian_human_reports/后续改进要求完成情况与下一步_2026-05-08_2030.md`

## 0. 总体结论

当前项目已经从“递归 Trellis2 工程管线”推进为可防守的 SIGGRAPH Asia 方法故事雏形：**Projection-Stabilized Sparse-Latent Recursive Grammar (PS-RSLG)**。最强主线是 finite-depth recursive 3D asset growth：grammar 操作 mesh-derived sparse O-Voxel/SLAT state，递归步骤中包含 proposal、merge、competition、masked naturalization、decode、projection、re-encode、cache。

但验收上必须严格区分三类证据：

1. **可进入论文主文的证据**：formal grammar v2、projection-stabilized recursion claim、space competition protocol、projection ablation 数值、mesh-based Blender/Cycles render、统一 mesh/asset 指标、传统 space-colonization OBJ/Blender baseline。
2. **可进入论文 appendix / application / limitation 的证据**：SDE/flow masked naturalization、cache/LOD visible-window proxy、symmetry/Escher/crystal proxy、公开 guide / open image route、selected textured GLB。
3. **只能作为诊断的证据**：matplotlib scatter/contact preview、未固定相机的快速预览、未检查 GLB/PBR 通道的 texture preview、只来自 remote log 或 prototype manifest 的结果。

最关键风险仍然是：**头图和最终视觉还没达到论文级；PBR/textured mesh 只有局部成功；space competition 主表还没有完全按同 root、同 depth、同 render、同 metric 固化。**

## 1. 六大要求验收矩阵

| 用户要求 | 已完成 | 部分完成 | 未完成 | 下一步 | 论文可用性判断 |
|---|---|---|---|---|---|
| 1. 完整 grammar-based system 框架，而不是简单工程拼接 | 已形成 PS-RSLG v2：状态 \(S_d=(C,F,U,A,B,M,H,K)\)，grammar tuple，递归语义 `proposal -> merge -> competition -> masked naturalization -> decode -> projection -> re-encode -> cache`。已明确覆盖 IFS、L-system、space colonization、DLA/frontier、finite local shape grammar、symmetry/crystal、cache/LOD proxy。 | coverage proposition 和 weak stability proposition 已有中文 formal spine，但还没有完全压缩进正式英文 Method；method figure 仍是 draft。 | 还缺最终 algorithm box、主文级 rule taxonomy 图、每个理论 claim 与实验表的逐项绑定。严格 symmetry/equivariance、真正 infinite recursion、覆盖所有 shape grammars 都不能 claim。 | 把 v2 formal doc 改写为 Method 正文：task definition、state、grammar tuple、rule schema、operator semantics、coverage proposition、projection-stability proposition、limitations。 | **可进论文主文**，但必须保守表述。强 claim 是 finite-depth PS-RSLG 与 per-depth projection；symmetry/infinite 只能 appendix 或 limitation。 |
| 2. baseline / metric / PBR / texture 要形成图形学论文级实验协议 | 已有 `space_competition_metric_protocol_v2`、`recursive_growth_mesh_metrics.py`、traditional space-colonization baseline、mesh metric sweep、projection ablation 表。指标已分为 mesh/asset、occupancy proxy、branch/tip、competition/projection、texture/PBR QA。 | traditional baseline 已有 OBJ 和 Blender/Cycles render；mesh metric sweep 覆盖 traditional / non-tree / projection-pruned candidates。但 traditional tube OBJ 未焊接，face component 不能直接公平比较；trace 层 proposal/collision/accepted ratio 仍缺。 | 还没有完整主实验表：traditional SC、direct sparse grammar、final-only projection、proposed per-depth projection + sparse competition 同 root、同 depth、同相机、同 metric。PBR/import success table 未完成。 | 固化四列主表和曲线；补 skeleton-level metrics；补 trace metrics；对 selected GLB 做 Blender import/PBR channel QA；传统 tube 做 weld/remesh 或只用 skeleton 指标。 | **metric protocol 和部分结果可进主文**。matplotlib asset preview 不能进主图；metric 曲线可用 matplotlib，因为它们是定量图。 |
| 3. SDE/flow stochastic sampling、cache/LOD、Escher/symmetry、infinite recursion 要进入系统视角 | 已有理论位置：Trellis2 sampler 是 masked local naturalization，不接管 topology；cache/LOD 是 bounded visible-window proxy；symmetry/crystal 需要近似交换条件。已有 masked low-step grid、cache_lod diagnostic、symmetry_escher proxy 的状态记录。 | `compete_fork alpha` sweep、cache/lod prototype、crown/island-city proxy 都有初步证据，但更多是 proof-of-concept。 | 不能 claim full flow/SDE repair 保持递归 topology；不能 claim strict symmetry equivariance；不能 claim 真正 infinite 3D generation。缺 Blender render、symmetry metric、zoom panel、cache policy。 | 把 SDE 写成 optional local naturalization；cache/LOD 写成 extension；Escher/symmetry 做固定相机 mesh render + symmetry error；cache 做 zoom panel。 | **可进 Method/Appendix/Limitations**。除非补强视觉和指标，否则不应进 abstract 或主贡献。 |
| 4. 头图、大圆环、多类别、方法总图、最终视觉必须像 graphics paper | 已有 method system grammar draft v2、traditional baseline mesh Blender contact sheet、若干 neutral mesh render、两个 true textured GLB：`tree_compete_s3/textured.glb`、`vine_d5_compete_s5_inference/textured.glb`。已有四类视觉矩阵方向：vine/root、tree/bush、ornament/portal/hard-surface、porous/DLA/frontier。 | 公开 guide 已准备 8 张 Wikimedia 参考图，并衔接 Trellis2 textured mesh route。selected mesh/textured attempts 已规划 vine/tree/portal/crystal。 | 大圆环 head figure 还未真正搭 Blender scene；强 textured assets 不足四类；non-tree、octopus/animal、mechanical、crystal、Escher/infinite city 还没达到头图级。method figure 仍需 vector/final layout 和真实 result insets。 | 先做四类资产筛选表，每类同时给 neutral mesh render 和 textured/PBR attempt；只选 mesh/GLB/Blender 结果进头图；大圆环布局最后做，不能用构图掩盖资产质量。 | **neutral mesh renders 可进主实验图**。selected textured GLB 可做 compatibility / asset-quality evidence。未检查 texture/PBR 的 preview 只能诊断。 |
| 5. 正式论文写作要收束 story、abstract、intro、method、experiments | 已有 `siga_paper_story_and_writing_plan_v2`，主故事收束到 finite-depth PS-RSLG、projection-stabilized recursion、mesh-first evaluation。贡献句、intro 段落、related work 方向、实验章节结构均已草拟。 | `paper_siga/main.tex` 已有增强骨架和部分 figure/table 接入；但本文档读取范围内仍提示 Abstract/Introduction/Related Work/Method/Experiments 未最终投稿化。 | 实验章节不能写满，因为同协议主表和 texture QA 未完成；本地 LaTeX 编译工具不可用的历史限制仍需处理；final language 未打磨。 | 先正式化 Method；Experiments 按 projection ablation 和 space competition 写，不按实验时间线写；Abstract/Contributions 等主实验稳定后再定稿。 | **写作计划可直接指导论文**。当前文案可做 draft，不宜当 final submission text。 |
| 6. 执行约束、远端/本地协同、heartbeat、资源边界 | 既有计划记录：远端项目只用 GPU 4/5/6/7，不碰 GPU 0/1/2/3；project-local HF/TMP/Torch/Triton cache；远端 artifacts 保留；本地 Blender 可用。本次文档支线仅本地读取和写文档。 | 远端大 mesh 传输慢，历史上远端 Blender/bpy 有环境限制，因此本地 mesh-based render 是优先路线。thread limit 曾出现但旧 subagent 已关闭。 | 当前任务明确要求不 SSH、不远端命令，因此不能刷新远端 running status、不能确认 remote textured batch 是否完成。 | 后续由主线/远端支线继续执行实验；本地文档支线只消费已同步结果。大 mesh 应远端 decimate/compress 后再拉 selected mesh。 | **执行约束可写入内部计划**，不作为论文内容。资源/heartbeat 状态只服务项目管理。 |

## 2. Mesh / Textured Mesh 与 Matplotlib / Preview 的严格分级

### 2.1 可进入论文主图或主实验图

- OBJ/GLB 经 Blender/Cycles 或等价 mesh renderer 的 fixed-camera render。
- traditional space-colonization 的 tube OBJ Blender render，可作为 procedural structure baseline visual row。
- proposed 方法的 neutral mesh render，用于公平判断 geometry、connectivity、fragmentation、scale 和 renderability。
- 由统一 CSV/JSON 生成的 metric 曲线，例如 component count、LCR、faces/vertices/token growth、occupancy proxy。这里 matplotlib 是定量绘图工具，允许进入论文。

### 2.2 可进入论文 secondary figure / appendix / asset compatibility

- textured GLB 的 Blender import 成功、PBR/material channel 检查通过、且 neutral mesh 已经验证结构的结果。
- 公开 guide 或 open image model 生成的 root/texture guide，只能作为 root-source / appearance-route 支撑，不是方法贡献。
- cache/LOD zoom panel、symmetry/Escher proxy、DLA/porous stress test，可进入 appendix 或 applications，但要标明条件和失败边界。

### 2.3 只能作为诊断，不应进入论文主视觉

- matplotlib scatter/contact sheet 表示 asset 外观的 preview。
- 未经 mesh/GLB 导入和固定相机渲染的截图。
- 只靠 texture 遮盖结构缺陷的图。
- 未记录 license/attribution 的公开参考图结果。
- 只从 prototype manifest 或 log 推断的视觉结论。

## 3. 论文可写 Claim 清单

### 3.1 可以主文强写

- PS-RSLG 是一个 finite-depth recursive 3D asset growth framework。
- grammar 在 mesh-derived sparse O-Voxel/SLAT state 上执行 typed recursive rules。
- per-depth decode -> projection -> re-encode 是递归语义的一部分，而不是最终 cleanup。
- IFS、L-system、space colonization、DLA/frontier、finite local shape grammar 可作为受限/退化实例进入 coverage table。
- mesh-first evaluation protocol 将 recursive geometry stability 与 selected texture/PBR compatibility 分开。

### 3.2 可以主文保守写或 appendix 写

- masked flow/SDE 是 local naturalization prior，但不保证保 topology。
- symmetry/crystal 需要 projection/sampler/codec 的近似交换条件，当前是 conditional support。
- cache/LOD 支持 bounded visible-window 或 finite-depth proxy，不等于无限生成。
- selected projected meshes can be passed to texture/PBR export pipeline。

### 3.3 当前不应写

- 已解决真正 infinite 3D recursive generation。
- 实现严格 symmetry/equivariance guarantee。
- full flow/SDE repair preserves recursive topology。
- 覆盖所有 shape grammars。
- texture/PBR 质量是主贡献或普遍成功。
- matplotlib preview 可代表最终 asset quality。

## 4. 10 个最高优先级 Next Actions

1. **固化 space competition 主实验四列**：traditional SC、direct sparse grammar、final-only projection、proposed per-depth projection + sparse competition，在 vine/tree/bush/portal case 上使用同 root、同 depth、同 render、同 metric。
2. **补全 trace-level 指标**：proposal count、accepted proposal ratio、collision violation、projection survival ratio、per-depth LCR AUC。
3. **重做主视觉为 mesh/GLB/Blender 渲染**：所有候选结果统一相机、光照、分辨率、裁切；matplotlib asset preview 全部降级为诊断。
4. **完成 traditional baseline 公平指标**：优先 skeleton JSON 的 coverage/tips/branches/length/angle；若要用 face component，先 weld/remesh tube OBJ。
5. **筛选四类头图资产**：plant/root/vine、crystal/symmetry、sci-fi/mechanical/island-city、portal/recursive art；每类至少一个 neutral mesh render 和一个 textured/PBR attempt。
6. **做 GLB / PBR QA 表**：GLB export/import、material count、base color、roughness、metallic、opacity、missing texture、render warnings、human QA。
7. **把 formal grammar v2 压缩进正式 Method**：给出 task/state/grammar/operator/algorithm box/coverage proposition/projection-stability proposition。
8. **将 projection ablation 与 space competition 绑定到论文实验**：metric 曲线、表格、qualitative mesh row 三者互相对应，避免只讲好看的个案。
9. **处理 secondary claims**：SDE 写成 optional local naturalization；cache/LOD 写成 visible-window proxy；symmetry/Escher 写成 application candidate 或 appendix，不进入 abstract 强 claim。
10. **更新论文写作骨架**：Experiments 按 projection ablation、space competition、category breadth、texture QA 组织；Abstract/Contributions 在主实验表稳定后再最终定稿。

## 5. 最终验收判断

六大要求中，**要求 1 和要求 5 的文档/理论/写作框架已达到可继续写论文的状态**；**要求 2 的 baseline/metric 协议和局部结果已经可用，但主实验表未完全闭环**；**要求 3 已有系统位置和 proxy，但不能作为强贡献**；**要求 4 是最大短板，尤其是四类 textured mesh/PBR 头图资产不足**；**要求 6 的执行约束在历史计划中基本落实，本次本地支线也遵守了不 SSH、不远端命令的限制**。

下一阶段不应再扩散新概念，而应把已有 PS-RSLG 故事压到可审稿的证据链：**formal method -> projection ablation -> space competition main table -> mesh-first visual matrix -> selected texture/PBR compatibility**。
