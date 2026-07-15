# 论文修改要求逐项合规矩阵

生成时间：2026-05-09 23:15  
输入依据：

- `/Users/fanta/Downloads/agent_revision_and_experiment_requirements.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex`
- `/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_system_grammar_plan_20260508.md`

说明：本文档只做合规审计与下一步分工，不修改 `main.tex`，不修改实验结果，不触发远端任务。状态分级为：`已满足`、`部分满足`、`未满足`、`投稿级阻塞`。

## 总体结论

当前稿件已从“工程流水线叙事”推进到“generation-model-native recursive grammar over sparse 3D latents”的论文框架。正文侧的摘要、引言、相关工作、Preliminaries、Method 主线、TODO 标注、texture 降级、projection 语义改写和实验协议分离已经有明显落地。

但投稿级证据仍不足。最大的缺口不是继续加视觉 gallery，而是需要证明：稀疏 latent 递归语言确实优于 mesh-space procedural postprocessing + Trellis2 texture export；projection 不是手工 mesh repair；naturalization、effective resolution、metrics、baselines、seed/root robustness 和 runtime 均有完整可复现实验支撑。

## 合规矩阵

| 编号 | 要求 | 当前状态 | 当前完成证据 | 还缺什么 | 下一步主线 |
|---|---|---:|---|---|---|
| 0.1 | 区分正文主干、figures-only pages、附录；正文不能依赖附录图表 | 部分满足 | `main.tex` 已有 “Main paper, figures-only pages, and supplement boundary” 段落，明确主文证据、figures-only pages、supplement 边界；正文写了不依赖附录编号 | 实际 LaTeX 结构尚未拆成正式主文、references 后最多 2 页 figures-only、supplement；当前仍是工作稿合并形态 | 正文 + 图 + 附录 |
| 0.2 | 加入 `\EvidencePending{}` 与 `\ExpFigTODO{}` 并标注未完成内容 | 已满足 | preamble 已定义两个宏；摘要、intro、related work、preliminaries、projection、visual、baseline、metric、runtime 等多处已标注 | 最终投稿前必须清除所有 TODO；部分强 claim 仍需补充更精确 EvidencePending | 正文 |
| 1 | 摘要重写：突出 recursive grammar/language，弱化 projection 和 texture | 部分满足 | 摘要第一句已写递归结构、one-shot 3D generator 难点、generation-model-native recursive grammar；texture 仅作为 selected projected meshes export；projection 写成 execution semantics | 摘要仍包含 “current evidence shows...” 但定量结果未填；需要最终 matched baseline matrix 后替换 EvidencePending | 正文 + 实验 |
| 2.1 | Intro 第一段：递归算法/结构重要性，覆盖自然、科学、设计应用与经典文献 | 部分满足 | 引言已覆盖 trees、roots、vines、corals、porous aggregates、crystals、ornaments、architectural elements；引用 L-system、IFS、DLA、space colonization、shape grammar、survey | 科学/设计应用文献仍偏概括；若投稿需要更强 literature grounding，可补少量应用引用 | 正文 |
| 2.2 | Intro 第二段：传统递归 3D 方法，客观说明优势与局限 | 已满足 | 引言和 Related Work 均强调传统方法结构显式、可控、可检查，并将局限限定为 surface/material/asset readiness 成本 | 可进一步压缩措辞，避免显得贬低 classical baselines | 正文 |
| 2.3 | Intro 第三段：现代 3D 生成，区分 object latent 与 sparse latent，说明 Trellis/Trellis2 middleware | 部分满足 | 引言与 Related Work 已区分 Shape2VecSet/Shap-E object latent 与 TRELLIS/TRELLIS.2 sparse structured latent；列出 sparse support、features、encode/decode、masked sampling、texture/PBR path | 控制实验尚未完成，稿中已标 `Need controlled comparison...` | 正文 + 实验 |
| 2.4 | Intro 第四段：说明 naive adaptation 失败链条 | 部分满足 | 引言列出 2D scaffold、direct sparse edit、global flow repair、final-only cleanup 失败链条，并标 EvidencePending | 需要同 root/depth 协议的失败图或实验小节支撑 | 实验 + 图 |
| 2.5 | Intro 第五段：从失败导出本文方法 | 已满足 | 引言明确 grammar owns topology、sparse latent support as substrate、handles、rule templates、frozen generator local masked realization、projection admissibility | 需要方法图和实验继续支撑这个叙事 | 正文 + 图 |
| 2.6 | Contributions 重写：合并 projection 贡献，texture 不做核心贡献，最后一条留定量 TODO | 已满足 | Contributions 已合并 projection-stabilized execution；texture 单独一句 capability；最后一条含 EvidencePending | 最终需要替换定量 TODO | 正文 + 实验 |
| 3.1 | Related Work procedural/recursive modeling 系统化 | 已满足 | Related Work 2.1 覆盖 L-system、IFS、DLA、space colonization、shape grammar/CGA，并强调其结构控制价值 | 可补更近期 survey 或应用引用，但不阻塞结构 | 正文 |
| 3.2 | Related Work 3D generation 重写，说明 sparse route | 部分满足 | Related Work 2.2 已覆盖 datasets、object latents、DreamGaussian/AssetGen/Hunyuan/TRELLIS/TRELLIS.2，说明 sparse support/codecs/masked updates | 缺直接 empirical comparison 到 object-latent 或 mesh-only alternatives | 正文 + 实验 |
| 3.3 | 合并 editing/control，说明 single edit 与 repeated recursive execution 区别 | 已满足 | “Generative Control, Editing, and Evaluation” 已覆盖 SDEdit/FlowEdit、mask editing、native 3D latent editing、structure-conditioned generation，并区分 repeated grammar-driven execution | 相关 3D editing 引用可继续核对版本年份 | 正文 |
| 3.4 | Infinite/world-scale generation 不放主 related work | 已满足 | 主 Related Work 未单列 world-scale；Scope 里只保留 finite-depth 与 future extension | 若附录要讲 cache/infinite recursion，需独立补充 | 附录 |
| 4.1 | 新增 Preliminaries：递归生成定义 | 部分满足 | 已新增 Preliminaries，给出 state、rule library、scheduler、depth、interpretation map、finite-depth asset 公式 | 文中自己标了需核对 graph grammar / shape grammar derivation terminology；还需文献 grounding | 正文 |
| 4.2 | Preliminaries：Sparse voxel / Trellis-style generator pipeline 符号定义 | 已满足 | 已定义 `z=(V,F)`、`Enc_theta`、`Dec_theta`、`N_theta`、`Tex_theta`、condition `y`、sparse support/features、texture export | 图尚未补 | 正文 + 图 |
| 4.3 | 需要 Trellis-style pipeline 图并标 TODO | 已满足 | 已有 `\ExpFigTODO{User needs to provide sparse voxel / Trellis-style generator pipeline figure...}` | 需要实际白底论文风流程图 | 图 |
| 5.1 | Method 开头重调：继承 preliminaries，给出简洁总公式 | 已满足 | Method “Problem Setting” 给出 PS-RSLG 名称、grammar over sparse generator states、handles、rules、masked realization、projection、总公式 | 公式需最终与 projection/naturalization 实现完全对齐 | 正文 |
| 5.2 | 修复符号冲突 | 部分满足 | 已用 `V_d^{root}` 表 root anchors，`\mathcal R_d` 表 selected rules，`\mathcal P_d` 表 proposals；`u_t` 区分 sampler state 与 `z_d` program state；Eq 类型问题已改成 state set 写法 | 仍需全文最终 pass，尤其旧注释和附录若保留，不能重新引入冲突 | 正文 |
| 5.3 | Core State 大幅缩短 | 已满足 | Core State 改为 `z_d=(V_d,F_d,A_d)`，handles 单独定义，bookkeeping 作为 auxiliary | 需要把更大 tuple 的细节转入 supplement/appendix，主文不再展开 | 正文 + 附录 |
| 6 | Rule Table 和 operators 重写：加粗、定义/公式、只保留用到的 operator | 部分满足 | Table “Representative rule families” 已加粗 Grow/Branch/Attach/Copy/Split/Extrude/Refine，并有 Definition/proposal 与 Feasibility role；material 不再作为 core operator | 部分 operator 仍是自然语言定义，未全部挂公式号；Refine 是 planned experiment，是否留主表需最终取舍 | 正文 |
| 7 | Masked Flow Naturalization 具体化并补 ablation TODO | 部分满足 | 已新增 “Masked Local Naturalization”，明确 frozen generator local prior、mask、anchor clamp、`u_t` sampler state、feature blend；区分不做 global topology repair | 缺实际 Trellis2 latent/step/schedule/alpha/mask dilation 实现参数；缺 naturalization ablation；需说明 feature blend 是否 heuristic | 正文 + 实验 |
| 8 | Classical Systems as Limits 移到附录，正文只留一句 | 已满足 | Method 中只保留一句 classical systems as restricted rule families，details in supplementary appendix；主文未展开长 reductions | 需要真正建立附录文本，且主文不得引用附录公式/图 | 附录 |
| 9 | 3.8/3.9 合并为 Scope/Complexity/Export，移走 symmetry/visible-window 公式 | 已满足 | 已有 “Scope, Complexity, and Export”，讲 per-depth cost、token budget、runtime/memory TODO、finite depth、texture export 非结构证据；symmetry/cache/visible-window 只作为 supplement/future extension | runtime 实验未补 | 正文 + 实验 |
| 10 | 全部视觉结果重渲染：白底、无 PPT 风、无边框、标准 subfigure | 部分满足 | `main.tex` 已标完整 re-render TODO；已有纯白 no-ground projection ablation、connected scaffold、surface-voxel 等新图迹象；AgentDoc 计划也规定 paper/user-facing 只能 mesh/textured-mesh | 不是所有图都已重渲染；仍有 gallery-heavy/contact-sheet 风险；需要统一相机、尺度、白底、无标签排版 | 图 |
| 11.1-11.3 | Projection 重写为 model-native/state admissibility，不像手工 repair；bridge 分 native/model-proposed/traditional baseline | 部分满足 | `Model-Native Projection` 已明确不是 manual mesh repair；detached components inactive/delete before re-encoding；optional connectors 必须 grammar proposed + frozen generator naturalized；traditional repair 是 baseline | 当前实现仍承认 conservative prune-only approximation；model-proposed bridge 尚未形成主实验；需要避免算法框和图像给人 mesh repair 感 | 正文 + 实验 + 图 |
| 11.4 | Projection variants 实验：deletion mass、orphan handles、branch/tip、LCR 等 | 投稿级阻塞 | 已有 AgentDoc projection ablation：direct/final-only/per-depth，vine/tree compete 有强结果；`main.tex` 有 projection ablation table/figure | 缺完整 variant matrix：prune-only per-depth、model-proposed bridge、traditional repair baseline；缺 deletion mass/orphan handle/active handle survival/branch-tip preservation/topology drift | 实验 |
| 11.5 | Projection mechanism 图 | 未满足 | `main.tex` 已标用户需提供/approve projection mechanism figure | 尚无最终白底 mechanism figure | 图 |
| 12 | Operator Scheduling / Sparse Competition 重写并补图 | 部分满足 | 已定义 attachment/occupancy/collision/frontier/orbit/generator preference term；AgentDoc 认为 compete 是最强 operator，需作为 paper method subsection | term 仍偏概念；缺一个 concrete operator 的完整计算流程、可视化图、case examples；未说明哪些项实验实际用到 | 正文 + 实验 + 图 |
| 13 | Effective Resolution / Recursive Refinement 重写、定义指标、补实验 | 投稿级阻塞 | 正文已降级为 “hypothesis about effective addressable detail, not measured resolution claim”；列出 terminal handle count、minimum feature scale、detail survival 等指标，并标 major experiment TODO | 缺 one-shot vs recursive refinement、same token budget、depth curves、terminal detail preservation、高 depth、multi-level naturalization、failure threshold | 正文 + 实验 + 图 |
| 14 | 证明不是 procedural grammar + mesh projection + Trellis2 export | 投稿级阻塞 | 正文叙事已强化 sparse-latent language、handles、attachment、masked naturalization、projection invariant；claim map 标出 controlled comparison 缺口；AgentDoc 明确这是核心故事 | 缺关键实验证明：latent-space vs mesh-space recursion、ordinary procedural + Trellis texture、latent transform-copy vs mesh copy/re-encode、language ablation | 实验 |
| 15 | Metrics 大补强，不只 LCR | 投稿级阻塞 | 正文已有 protocol separation，列出 occupancy、surface-voxel、raw face components、renderability、GLB/PBR diagnostics；claim-aligned metric figure 已存在 | 缺文献支撑和完整实现：mesh validity、skeleton topology、morphology、latent stability、effective resolution、material diagnostics、mean/std；当前 LCR/connectedness 仍占主导 | 实验 |
| 16 | Baselines 更公平完整 | 投稿级阻塞 | 正文 Baselines 小节列出 classical、one-shot、image-entry、direct coordinate、flow repair、masked repair、weak blend、final-only、ours；AgentDoc 有 traditional space-colonization baseline 和 texture baseline 结果 | 缺完整量化：mesh-space recursion + repair/texture、one-shot Trellis2、global/masked/weak repair、external methods或合理排除、latent transform-copy comparison | 实验 |
| 17 | Naturalization ablation | 投稿级阻塞 | 文中已标 `Naturalization ablation required...`；Method 已把 naturalization 写成 local prior | 缺 rule-only、encode/decode only、no-N、weak blend、masked-N、global-N、projection/no-projection 组合实验及 metrics | 实验 |
| 18 | Root quality、seed variation、success rate | 投稿级阻塞 | 文中已标 root-quality/seed TODO；AgentDoc 有 selected examples 和多 guide sweep 证据 | 缺多 roots、多 seeds、多 prompts/guides、success/failure rate、mean/std、category/operator robustness | 实验 |
| 19 | Runtime / complexity / memory | 投稿级阻塞 | Scope 里已说明每 depth 成本，并标 runtime/GPU memory/encode/decode/projection/texture cost TODO | 缺 per-depth runtime、memory、token/mesh curves、projection cost、texture cost、hardware/batch size、公平 baseline cost | 实验 |
| 20 | Texture/PBR 降级为 compatibility 并独立评估 | 部分满足 | Contributions 弱化 texture；Material Handles 和 Experiments 明确 texture is not structural evidence；Texture QA table 存在；caption 多次说明 selected projected meshes | 仍需完整 GLB/PBR diagnostics、channel availability、warnings、统一白底；失败/holes/material mismatch 应主要进 appendix | 正文 + 实验 + 图 + 附录 |
| 21 | Negative results 移到附录 | 部分满足 | 主文多处把 DLA bridge、fragmented variants、bismuth guide sensitivity、uninspected GLBs 定义为 diagnostic/boundary；要求 supplement | 当前主文仍展示较多 boundary/diagnostic figures；需要最终删减主文，只留 strongest examples + clean ablations + key quantitative charts | 正文 + 图 + 附录 |
| 22 | 实验章节重构：Implementation、Tasks/Baselines、Metrics、Projection、Sparse vs Mesh、Naturalization、Resolution、Qualitative、Texture、Robustness | 部分满足 | 现有 Experiments 已有 claims under test、claim map、boundary、Tasks、Baselines、Metrics、projection、baselines、texture 等段落 | 结构仍未完全按建议拆分；Implementation Details、Sparse-vs-Mesh、Naturalization Ablation、Resolution、Robustness 独立小节和数据缺失 | 正文 + 实验 |
| 第三类 claim 1 | “Sparse latent grammar better than mesh-space procedural postprocessing” 必须标证据缺口 | 已满足标注 / 未满足证据 | claim map 与 experiment TODO 已标 controlled comparison 和 critical experiment | 需要直接 latent-space vs mesh-space comparison | 实验 |
| 第三类 claim 2 | “Sparse voxel supports transform/cache/addressability advantage” 必须标证据缺口 | 部分满足 | 正文说明 sparse support/features/handles/cache；AgentDoc 有 cache/LOD diagnostic 初步迹象 | 缺 transform/cache/addressability advantage 定量实验 | 实验 |
| 第三类 claim 3 | “Masked local naturalization improves quality without topology drift” 必须标证据缺口 | 已满足标注 / 未满足证据 | Naturalization TODO 已存在 | 缺 ablation | 实验 |
| 第三类 claim 4 | “Projection model-native not manual repair” 必须标证据缺口 | 已满足标注 / 未满足证据 | Projection section 有 EvidencePending；文字已重写 | 缺 projection variants 和 mechanism figure | 实验 + 图 |
| 第三类 claim 5 | “Recursive refinement exceeds one-shot effective resolution” 必须标证据缺口 | 已满足标注 / 未满足证据 | Recursive Refinement Scope 降级并标 major experiment TODO | 缺高 depth/multiscale/token budget comparison | 实验 |
| 第三类 claim 6 | “Baselines fairly compared” 必须标证据缺口 | 已满足标注 / 未满足证据 | Baseline TODO 已存在，traditional baseline 初步完成 | 缺完整 baseline matrix 与 mean/std | 实验 |
| 第三类 claim 7 | “Texture export compatible with selected projected meshes” 必须标证据缺口 | 部分满足 | 已有 Trellis2 textured GLB exports、texture QA table、surface-voxel diagnostic；文字强调 selected | 需要统一 GLB/PBR diagnostics、warnings、clean figures | 实验 + 图 |
| 23 | 总体评价：从 technical report 收紧成投稿论文 | 部分满足 | 正文主线明显收紧，claim map 保守，protocol separation 存在 | 当前仍过长、figure 多、TODO 多，实验支撑不足 | 正文 + 实验 + 图 |
| 24.1 | 最高优先级：证明 generation-model-native recursive language 必要性 | 投稿级阻塞 | 叙事已有 | 缺 latent-vs-mesh、transform/cache/addressability、procedural+texture baseline 实验 | 实验 |
| 24.2 | 最高优先级：重写 projection | 部分满足 | 文本已完成第一轮改写 | 缺 model-native variant 实验与机制图 | 正文 + 实验 + 图 |
| 24.3 | 最高优先级：metrics 和 baselines | 投稿级阻塞 | 初步列出 | 缺完整实现、文献、mean/std | 实验 |
| 24.4 | 最高优先级：effective resolution | 投稿级阻塞 | claim 已降级 | 缺方法闭环与实验 | 正文 + 实验 |
| 24.5 | 最高优先级：重做视觉 | 部分满足 | 部分纯白图已进入草稿 | 全部视觉需统一重渲染和重排版 | 图 |
| 24.6 | 最高优先级：intro/related/preliminaries | 部分满足 | 当前已基本重写 | 需最终文献核对、压缩、删 TODO | 正文 |
| 24.7 | 最高优先级：naturalization ablation | 投稿级阻塞 | TODO 已在稿中 | 缺实验 | 实验 |
| 24.8 | 最高优先级：runtime/root/seed/robustness | 投稿级阻塞 | TODO 已在稿中 | 缺数据 | 实验 |
| 24.9 | 最高优先级：texture 降级 compatibility | 部分满足 | 文本已降级，QA table 已有 | 需补完整诊断和主/附录拆分 | 正文 + 实验 + 附录 |
| 24.10 | 最高优先级：附录整理 | 未满足 | 正文已有 supplement boundary | 附录内容尚未正式组织：classical reductions、failures、extra cases、long details | 附录 |
| 25 | 建议执行顺序 | 部分满足 | Skeleton、abstract/intro/RW/prelim/method/TODO 已推进；若干关键 experiments 有初步结果 | 仍需按顺序完成 critical experiments、重渲染、附录、压页数、删 TODO | 全线 |
| 26 | 不要做的事情 | 部分满足 | 已弱化 texture、避免正文引用附录图、修复多数符号冲突、标 unsupported claims | 当前仍有 gallery-heavy 风险、LCR 依赖偏重、projection 实现感需继续控制、Figure 2/结果图需最终论文化 | 正文 + 图 + 实验 |

## 当前可作为证据的具体进展

1. 正文重写证据：`main.tex` 已包含新的 abstract、Introduction、Related Work、Preliminaries、Method、Experiments and Results，并保留 `EvidencePending`/`ExpFigTODO`。
2. 方法框架证据：`main.tex` 已使用 PS-RSLG/recursive sparse-latent grammar、handles、rule templates、projection-stabilized execution、masked local naturalization、model-native projection、scope/complexity/export。
3. 实验事实证据来自 AgentDoc：Trellis2 mesh-first O-Voxel/shape-SLAT encode/decode 可用；真实 Trellis2 textured GLB export 可用；per-depth projection loop 可用。
4. 强结果证据来自 AgentDoc：`vine_d5_projected_compete` LCR 约 0.9822；`tree_projected_compete` stage 3 LCR 约 0.9841；`porous_container_compete` final LCR 约 0.9917；`compete` 是当前最稳定 operator。
5. Projection ablation 证据来自 AgentDoc：`vine_compete_d3` direct 2059 comps/LCR 0.9049，final-only 2 comps/LCR 0.9934，per-depth keeps 1 comp/LCR 1.0000；`tree_compete_d3` direct 3201 comps/LCR 0.9169，final-only 4 comps/LCR 0.9842，per-depth keeps 2 comps/LCR 0.9949。
6. 负面/边界证据来自 AgentDoc：full flow repair 会 wash out recursive topology；DLA/porous/crystal visually weak unless root/operator/camera improved；attachment-aware bridge prototypes reduce components but geometry crude；texture export category-dependent。
7. 视觉策略证据：AgentDoc 明确 paper/user-facing qualitative results 必须 mesh-based 或 textured-mesh-based，point-cloud/matplotlib 只能作为内部调试。

## 投稿级阻塞项 Top 8

1. **缺少 sparse-latent grammar vs mesh-space/procedural+texture 的关键 novelty 实验。**  
   需要同 root/depth/budget 下比较 mesh-space procedural recursion、procedural + Trellis texture、sparse-latent without/with naturalization、one-shot Trellis2、image scaffold entry、final-only projection。

2. **Projection 仍缺 model-native 证据闭环。**  
   文本已改成 state admissibility，但实验还缺 prune-only、model-proposed bridge、traditional repair baseline、deletion mass、orphan handle、branch/tip preservation、topology drift。

3. **Metrics 体系不够投稿级。**  
   LCR/connectedness 只能做初级稳定性证据；还需要 mesh validity、skeleton topology、morphology、latent stability、effective resolution、material diagnostics 与 mean/std。

4. **Baselines 不完整。**  
   traditional space-colonization baseline 和 texture baseline 是进展，但还缺 one-shot 3D generator、direct sparse edit、global/masked/weak repair、mesh postprocessing、latent transform-copy 对比。

5. **Naturalization ablation 缺失。**  
   当前无法证明 frozen generator 的 local prior 真正改善 surface/asset quality 且不造成 topology drift。

6. **Effective resolution 仍只是保守假设。**  
   当前文字已降级是正确的，但若论文主打 recursive/multiscale，需要 one-shot vs recursive refinement、same token budget、depth curves、detail preservation、高 depth 和 multi-level naturalization。

7. **Root/seed/robustness 与 runtime/memory 缺失。**  
   目前结果仍像 selected examples；需要多 root、多 seed、success rate、mean/std，以及 per-depth encode/decode/projection/texture cost。

8. **视觉与主/附录拆分尚未最终论文化。**  
   需要统一白底、无 PPT 风、无内嵌解释标签、asset 占满画面；主文只保留 claim-bearing figures，失败和大 gallery 进入附录/supplement。

## 推荐下一步分工

| 主线 | 应完成内容 | 优先级 |
|---|---|---:|
| 正文线 | 压缩主线；保留 generation-model-native language、projection invariant、protocol separation；删弱 claim 或保留 TODO | 高 |
| 实验线 | novelty 实验、projection variants、naturalization ablation、metrics/baselines、seed/root/runtime/effective-resolution | 最高 |
| 图线 | pipeline 图、projection mechanism 图、operator competition 图、全部结果统一白底重渲染与标准 subfigure 排版 | 高 |
| 附录线 | classical systems reductions、失败/边界案例、extra galleries、long implementation details、texture diagnostics、完整 metrics tables | 中高 |

## 当前不应做

1. 不应继续扩展无控制变量的 result gallery。
2. 不应把 texture/PBR 写回 contribution。
3. 不应在主文用 LCR 单指标支撑 topology、branch semantics 或 asset readiness。
4. 不应把 bridge/repair 图画成传统 mesh repair。
5. 不应在 critical experiments 完成前删除 EvidencePending/ExpFigTODO。
