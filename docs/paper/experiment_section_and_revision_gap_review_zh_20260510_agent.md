# 论文实验结构与 2026-05-10 修订缺口审查

日期：2026-05-10  
角色：并行子任务 B  
范围：读取 `paper_siga/main.tex`、`docs/paper/`、`docs/evaluation/`、`/Users/fanta/Downloads/agent_revision_and_experiment_requirements.md` 后形成执行建议。本文不修改 `main.tex`，不改图，不跑新实验。

## 0. 总体判断

当前稿件已经把故事从“内部结果堆叠”推进到较清晰的 claim-bearing 结构：先讲 PS-RSLG / sparse-latent grammar，再讲 per-depth projection，随后放 structural baseline、gen3D baseline、naturalization/export/effective-resolution gate 和 appendix。`main.tex` 已包含 TODO 宏、Preliminaries、符号修正、teaser 更新、gen3D baseline 表、effective-resolution proxy 表、appendix 路线图。

但用户今天要求的若干实验闭环仍没有完成。最核心缺口不是文字，而是：latent-space vs mesh-space 的正式同根同预算比较、完整 ablation matrices、effective resolution 的定量证据、以及 4.7/4.9/4.10 的主文压缩和 claim 降级。当前主文能安全写的主线应收窄为：

1. per-depth projection 在 conservative tree/vine competition 中能抑制 fragment propagation；
2. ordinary Trellis2 one-shot、trivial latent-copy、mesh-space generated-root copy 不能替代 grammar-owned recursive state；
3. selected PS-RSLG pyrite/coral 与 stronger vine stage5 是可用的 connected candidate；
4. texture/PBR 与 zoom/effective-resolution 只能作为 compatibility / diagnostic，不能作为结构贡献或完成的分辨率结论。

## 1. 逐项对应用户今日要求

| 用户要求 | 当前状态 | 已完成证据 | 未完成缺口 | 建议位置 | 最小继续实验 |
|---|---|---|---|---|---|
| gen3D baseline | partial，可主文保守使用 | `paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex`；`docs/paper/gen3d_baseline_paper_integration_qa_zh_20260510.md`；`docs/evaluation/ablation_and_gen3d_status_zh_20260510.md`。Trellis2 one-shot 三例、latent-copy 三例、mesh-space vine/pyrite、PS-RSLG pyrite/coral/stronger vine stage5 已汇总。 | TRELLIS 非 2 缺失；Hunyuan3D 只 audit 未跑；mesh-space coral missing；strict ours_vine 弱，必须换 stronger stage5；现有 contact sheet 有空 panel/裁切/尺度问题。 | 主文放 compact table + 一张 diagnostic contact sheet；Hunyuan、missing rows、weak strict vine 放附录/status。 | 补 coral mesh-space generated-root；至少补 Hunyuan image-to-3D one-shot 或明确 blocked audit 表；重渲染主文 gen3D contact sheet，标 missing、统一尺度、避免底部裁切。 |
| latent-vs-mesh-space | partial，不足以支撑强 claim | `results/latent_vs_mesh_texture_evidence_20260510/*.csv` 与传统 texture-only 诊断可支持“texture alone 不是 topology repair”。mesh-space vine/pyrite generated-root copy 有高 raw components，pyrite LCR 低。 | 缺正式 same-root/same-budget 矩阵：mesh procedural+texture、mesh procedural+repair、mesh copy+re-encode、sparse rule-only、sparse masked-N、one-shot、image scaffold、final-only、ours。当前不能证明 sparse-latent language 必要性，只能证明朴素 mesh-copy/texture 不够。 | 主文只作为 gen3D/trivial recursion control；理论必要性和完整矩阵进附录或未来实验。 | 选 1 个 tree/vine + 1 个 non-tree，固定 root、depth、token/face budget、camera、renderer，跑 mesh-space direct/repair/re-encode vs sparse latent direct/projection/masked-N/ours，输出 occupancy LCR、raw/welded components、root reachability、fixed zoom verdict。 |
| effective resolution | missing/diagnostic only | `paper_siga/drafts/effective_resolution_status_table_20260510.tex` 有 proxy：crystal/coral scale improvement 4.09、detail ratio 2.46；tree/vine scale improvement 3.79、detail ratio 0.54。`gen3d_baseline_texture_fair_zoom_clean_20260510.png` 是两级 zoom 诊断。 | 缺 terminal-detail count、local feature scale 的严格定义与人工/自动 QA；缺 one-shot vs recursive 同 token budget；缺 zoom retention score、full-object high-resolution blow-up estimate；zoom 图有白色 mask/空 panel/裁切问题。 | 主文最多一句 qualitative diagnostic；proxy table 建议附录或主文 very cautious。不能在摘要/结论写“提升有效分辨率”。 | 跑 one-shot vs recursive under same token budget，至少 tree/vine + crystal/coral 各一例；记录 minimum visible feature scale、terminal count、local token density、zoom retention、face/GLB size、runtime/memory，并重渲染灰底或可见 alpha 的 matched zoom。 |
| ablation matrices | partial，不能声称完成 | `ablation_status_tables_20260510.tex` 有 coverage table：projection rows traditional/direct/final/prune/bridge/proposed 均 partial；naturalization rows rule-only/no-N/weak blend 为 0，masked local-N/global-N/with projection partial。projection ablation clean subset 有 vine/tree compete。 | same-root projection matrix 未闭合；bridge 只有一行；root case 和 repair variants 不完整；naturalization 缺 rule-only、no-N、weak blend；global-N 多是 negative/diagnostic；fixed-camera root/junction/tip zoom 缺失。 | 主文只放已闭合 projection subset；全量 coverage、missing counts、global-N negatives、post-hoc repair 进附录。 | tree/root/vine depth 1-4 跑 traditional、direct sparse、final-only、prune-per-depth、model-bridge、traditional repair、proposed；另跑 naturalization dropout：rule-only、no-N、weak blend、masked-N、global-N、with/without projection。每行输出 per-depth OBJ/CSV + fixed zoom。 |
| 4.7 | needs rewrite/降级 | `main.tex` 当前 `Naturalization, Export, and Effective Resolution` 已写“claims remain gated”；`docs/paper/experiment_section_restructure_review_zh_20260510_agent.md` 建议 4.7 改成 Naturalization Claim Gate。 | 如果 4.7 仍被当作成功结果，会 overclaim masked naturalization。缺 rule-only/no-N/weak blend 支撑。 | 主文短节或段落：`Naturalization and Projection Are Not Interchangeable`。 | 不一定先跑实验；最小文字动作是把 4.7 写成 gate。若补实验，跑上面的 naturalization dropout 小矩阵。 |
| 4.9/4.10 | needs merge/压缩 | `main.tex` 现在分别有 Naturalization/Export/Effective Resolution 与 Boundaries/Supplement Placement；appendix 也有 roadmap。 | 主文仍放了较多 selected showcase、texture table、zoom figure，页数和 claim 负担偏重。 | 合并为 3-5 段：`Export Compatibility, Effective-Resolution Diagnostics, and Boundaries`。texture QA 长表、zoom 弱图、guide sweep、candidate screens 进附录。 | 不一定先跑实验；最小文字动作是合并 4.9/4.10，主文只留 compact export summary 或一张 selected figure。 |
| appendix/TOC | partial，结构方向正确 | `main.tex` 已有 `\appendix`、Supplementary Material Roadmap、Ablation Coverage Status、Moved Gallery、Classical Procedural Systems、Scope Notes。正文写了正式 SIGGRAPH Asia 时 figures-only pages 与 text-heavy supplement 分离。 | 还没有最终“主文 figures-only pages vs supplement appendix”的清单映射；正文仍可能引用或依赖附录图；status table 与 gallery 混在 LaTeX 工作稿中可编译，但正式投稿需拆包。 | 主文不引用 appendix 图表编号，只写一句 additional diagnostics in supplement；附录应有 TOC/roadmap；figures-only pages 只放 figure/caption，不放 table。 | 建一张 appendix index：figure/table、role、allowed claim、main/supplement/figures-only；编译前检查正文是否引用 appendix labels。 |
| 纯白图 | partial，可用但需筛选 | 已有 `projection_ablation_pure_white_zoom_20260509.pdf`、`connected_scaffold_v2_hq_selected_contact_pure_white_rerun2115_20260509.png`、`hero_multi_zoom_white_20260510.png`、`gen3d_baseline_texture_fair_clean_20260510.png` 等。`docs/visuals/standard_pure_white_render_protocol_20260510.md`、`pure_white_rendering_protocol_zh_20260509.md` 提供协议。 | gen3D zoom 图白色 alpha/mask artifact 明显；contact sheet 有空 panel、裁切、尺度不一致；纯白背景会让淡色碎片不可见。不是所有纯白图都是投稿级。 | 主文优先用 projection ablation 白底图和 connected scaffold 白底图；有 artifact 的 zoom/diagnostic 图进附录或重渲染。 | 对主 claim 图统一 fixed camera、no ground、white/very light gray 备份背景、bbox scale、root/junction/tip/failure zoom；输出 render QA CSV。 |
| teaser/hero | partial，已替换但仍是 draft | `main.tex` teaser 使用 `figures/hero_multi_zoom_white_20260510.png`，caption 明确是 visual selection draft；`docs/visuals/hero_multi_zoom_status_zh_20260510.md` 与相关计划存在。 | hero 仍不是 final camera/layout pass；多类别 PBR 风格可能让 texture 承担过多贡献；需要确认每个 panel 对应主 claim 且无白洞、裁切、尺度不一致。 | 主文 teaser 可留，但 caption 必须保持“visual selection draft / selected recursive assets”，不写成完成实验结论。最终版应服务四个主 claim：projection、non-tree、frontier、zoom/asset export。 | 重渲染 final hero：同背景/光照/尺度，保留 nested zoom，但每个 zoom 对应主文表中可追溯 case；附 asset path、metric row、allowed claim。 |

## 2. 对当前实验章节的执行建议

### 2.1 主文最小安全结构

建议第 4 节按以下顺序收敛：

1. `Tasks, Protocol, and Metrics`：定义 occupancy-primary、raw mesh diagnostics、surface-voxel GLB diagnostics、texture/export diagnostics，明确 LCR 不是 watertight topology。
2. `Per-Depth Projection Ablation`：主结果，只用 vine/tree conservative compete 的 closed subset；fork 行标 stability-expression boundary。
3. `Structural Baselines Are Strong Controls`：传统 L-system/space-colonization/IFS 是 fairness sanity，不是 strawman。
4. `Ordinary Gen3D and Trivial Recursion Controls`：放 Trellis2 one-shot、latent-copy、mesh-space、PS-RSLG compact table。
5. `Selected Connected Scaffolds and Export Compatibility`：最多一张 neutral white scaffold 图 + 可选 pyrite/coral depth showcase。
6. `Export Compatibility, Effective-Resolution Diagnostics, and Boundaries`：合并原 4.7/4.9/4.10 中所有 gate、limitation、supplement placement。

### 2.2 主文推荐保留

- `figures/projection_ablation_pure_white_zoom_20260509.pdf`
- `tab:projection-ablation`
- `drafts/baseline_matrix_table_20260509.tex` 的 compact/fairness 版本
- `figures/gen3d_baseline_texture_fair_clean_20260510.png`，前提是 caption 标 missing/diagnostic
- `drafts/gen3d_baseline_summary_table_20260510.tex`
- `figures/connected_scaffold_v2_hq_selected_contact_pure_white_rerun2115_20260509.png`
- pyrite 或 coral depth/export showcase 二选一；若页数允许，两者都可留，但 caption 必须限制 claim。

### 2.3 建议移入附录/补充材料

- `figures/gen3d_baseline_texture_fair_zoom_clean_20260510.png`：当前更适合 appendix diagnostic。
- `drafts/ablation_and_resolution_status_tables_20260510.tex`：是 status table，不是 completed ablation。
- guide sweeps、density sweeps、candidate screens、strict matched weak rows、DLA bridge smoke、surface-voxel metric explanation、full texture QA table。
- Hunyuan3D/TRELLIS 非 2/coral mesh-space missing 或 blocked audit。

## 3. 当前可写与不可写的论文主张

### 可写

- Ordinary one-shot 3D generation can synthesize plausible individual objects, but does not enforce requested recursive attachment or reusable grammar state.
- Direct sparse-latent copy and mesh-space generated-root copy are negative controls lacking typed handles, attachment feasibility, projection, and re-encoding.
- Per-depth projection stabilizes conservative recursive programs relative to direct recursion and final-only cleanup in the tested vine/tree competition subset.
- Selected projected/scaffold meshes can enter the frozen Trellis2 texture/PBR export path, but export compatibility is separate from topology evidence.
- Traditional procedural baselines are strong structural controls under favorable occupancy/tube protocols.

### 不可写

- PS-RSLG universally outperforms classical procedural methods.
- All ablations are complete.
- masked naturalization is proven to improve surface quality without topology drift.
- effective resolution has been quantitatively proven superior to one-shot generation.
- Hunyuan3D was evaluated, failed, or was outperformed.
- occupancy LCR implies watertight, manifold, or physically correct topology.
- coral/DLA-inspired or pyrite/crystal-inspired cases solve physical DLA or crystal growth.

## 4. 最小继续实验清单

如果只为下一版论文最大化闭合度，建议按优先级跑：

1. **P0 projection matched mini-matrix**：tree/root/vine depth 1-4，methods 为 traditional、direct sparse、final-only、prune-per-depth、model-bridge、traditional repair、proposed；输出 per-depth metrics 和 fixed zoom。
2. **P0 latent-vs-mesh mini-matrix**：1 个 vine/root + 1 个 non-tree，比较 mesh procedural+texture、mesh repair、mesh copy+re-encode、sparse rule-only、sparse projection、sparse masked-N、one-shot/image scaffold、ours。
3. **P1 naturalization dropout**：vine + pyrite/coral，固定 rule/projection，跑 rule-only、no-N、weak blend、masked local-N、global-N、with/without projection。
4. **P1 effective-resolution quantification**：same token/face budget 的 one-shot vs recursive refinement，记录 local feature scale、terminal detail count、zoom retention、face/GLB size、runtime/memory。
5. **P1 render QA pass**：只对主文候选图做纯白/浅灰 fixed-camera overview + root/junction/tip/failure zoom，生成 verdict CSV。

## 5. 本次读取依据

- `paper_siga/main.tex`
- `paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex`
- `paper_siga/drafts/effective_resolution_status_table_20260510.tex`
- `paper_siga/drafts/ablation_and_resolution_status_tables_20260510.tex`
- `docs/paper/experiment_section_restructure_review_zh_20260510_agent.md`
- `docs/paper/gen3d_baseline_paper_integration_qa_zh_20260510.md`
- `docs/evaluation/evidence_matrix_for_revision_zh_20260510.md`
- `docs/evaluation/ablation_and_gen3d_status_zh_20260510.md`
- `docs/evaluation/ablation_completion_and_main_appendix_recommendation_zh_20260510_agent.md`
- `docs/evaluation/baseline_metric_gap_closure_plan_zh_20260509.md`
- `/Users/fanta/Downloads/agent_revision_and_experiment_requirements.md`

