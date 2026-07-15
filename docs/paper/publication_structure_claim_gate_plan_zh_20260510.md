# R-SLG 论文结构重排与 Claim Gate 计划

日期：2026-05-10  
角色：并行 worker，本文件只做论文结构、证据门控和主文/附录/补充材料重排建议。  
写入范围：仅本文件。未修改 `paper_siga/main.tex`。

## 0. 结论摘要

当前论文已经具备一条可投稿的窄主线：**PS-RSLG 是一个 generation-model-native recursive sparse-latent execution framework；grammar 持有可继续执行的递归状态，frozen 3D generator 提供 masked local realization / codec / texture export，per-depth projection 防止 detached fragments 污染下一层 handles、frontiers 和 caches。**

但现有证据还不支持宽主线：不能声称 sparse-latent language 全面优于 mesh-space recursion，不能声称 naturalization 已经解决拓扑，不能声称 effective resolution 已经定量优于 one-shot generator，也不能声称 Hunyuan3D、TRELLIS 非 2 或所有普通 3D generator 已经被公平比较。

因此建议正式投稿稿件采用：

1. 主文只保留 claim-bearing 图表，围绕 projection、gen3D/trivial recursion controls、selected connected scaffolds、local naturalization gate、export compatibility 组织。
2. 附录保留 status / diagnostic / failure-aware material，明确哪些是未闭合矩阵。
3. 补充材料容纳大 gallery、guide sweep、candidate screen、视觉候选池、blocked baseline audit、完整 QA 表。
4. 4.7 改写为 **Naturalization Claim Gate**，不要写成成功结果节。
5. 4.9/4.10 合并为 **Export Compatibility, Effective-Resolution Diagnostics, and Boundaries**，以边界和补充材料索引收束。

## 1. 主文推荐结构

建议将实验章节压缩成 claim-driven 顺序，而不是状态报告式顺序：

| 建议顺序 | 小节标题 | 主文功能 | 可承载 claim |
|---|---|---|---|
| 4.1 | Tasks, Protocol, and Metrics | 定义 recursive-state validity、occupancy-primary metric、raw mesh diagnostics、surface-voxel GLB diagnostics、texture/export diagnostics | 评估协议贡献；指标分层 |
| 4.2 | Per-Depth Projection Stabilizes Recursive State | 主结果，使用 conservative vine/tree compete subset | per-depth projection 比 direct/final-only 更能阻断 fragment propagation |
| 4.3 | Structural Baselines and Operator Admission | 传统系统作为强 structural controls；transform-copy admission 作为规则筛选 | classical baselines 不是 strawman；operator admission 需要 semantic/state/compatibility/export gate |
| 4.4 | Ordinary Gen3D and Trivial Recursion Controls | Trellis2 one-shot、latent-copy、mesh-space generated-root、PS-RSLG compact comparison | ordinary one-shot / naive recursion 不保证 grammar-readable attached state |
| 4.5 | Selected Connected Scaffolds and Export Compatibility | 少量 selected connected scaffold + selected textured export | projected recursive states can enter texture/PBR path；export 不等于 topology proof |
| 4.6 | Naturalization Claim Gate | 局部 masked naturalization，只写 gate 与限定结果 | masked local naturalization 是 local realization operator，不是 global topology repair |
| 4.7 | Effective-Resolution Diagnostics and Boundaries | 合并原 4.9/4.10 的 zoom、proxy、limitations、supplement placement | 当前只有 qualitative/proxy evidence；强 resolution claim 待闭合 |

## 2. 主文建议保留的图/表

| 图/表 | 建议位置 | 保留理由 | Caption/正文必须限制 |
|---|---|---|---|
| `figures/hero_multi_zoom_white_20260510.png` | Teaser，可临时保留 | 展示多类 recursive assets 和 zoom 意图 | 只称 selected recursive assets / visual summary；不要称 final hero 或完整实验结论。后续五 case combo GLB 完成后替换 |
| `figures/method_system_ps_rslg_tog_draft_20260509.pdf` | 方法图，建议重画但可暂保留 | 支撑 recursive sparse-latent execution 主线 | 降低 PPT 风格；主图应突出 state -> rule proposal -> masked local realization -> decode/project/re-encode |
| `tab:operator-admission-gates` | 方法或实验前 | 把 transform-copy 正/负例从 gallery 变成 admission protocol | 不能把 export success 当 operator admission；axis-mismatch 即使 connected 也应保持 negative compatibility control |
| `figures/projection_depth_curves_20260508.pdf` | 主文 projection 小节 | 展示 depth stability 趋势 | 只对 tested conservative operators 有效；aggressive variants 是 boundary |
| `figures/space_competition_depth_curves_tokens_20260508.pdf` | 主文 projection 或 appendix，二选一 | 支撑 stability-expression tradeoff 和 token growth | 若页数紧张移附录；不要让 token curve 抢主结果 |
| `figures/projection_ablation_pure_white_zoom_20260509.pdf` | 主文核心图 | 目前最 claim-bearing 的 mesh render figure | 明确是 pure-white mesh render；不靠 texture/material cues |
| `tab:projection-ablation` | 主文核心表 | 支撑 direct/final-only/per-depth projection 对比 | raw mesh diagnostics 和 occupancy-primary metrics 分开；不能只用 terminal LCR 证明中间状态有效 |
| `drafts/baseline_matrix_table_20260509.tex` 的 compact 版本 | 主文或附录前置 | 传统 baseline fairness sanity | 传统方法是 strong controls，不是视觉 strawman |
| `figures/gen3d_baseline_texture_fair_clean_20260510.png` | 主文 gen3D/trivial controls | 对 reviewer 的“为什么不用普通 3D generator / mesh recursion”有直接回应 | 标注 missing rows；vine selected candidate 与 strict row 不混同；Hunyuan/TRELLIS 非 2不进入已完成结论 |
| `drafts/gen3d_baseline_summary_table_20260510.tex` | 主文 compact table | 当前 one-shot / latent-copy / mesh-space / ours 的核心数值表 | 明确 blocked/missing rows；PS-RSLG vine 使用 stronger stage5 是 selected row，不是 strict same-row victory |
| `figures/masked_naturalization_ablation_contact_sheet_20260510.png` | 主文短节或 appendix，取决于页数 | 新增三任务 masked naturalization 局部证据 | 只支持 local surface/material realization；不支持 global repair 或 complete matrix |
| `drafts/masked_naturalization_ablation_table_20260510.tex` | 主文短表或 appendix | 给 naturalization gate 一点定量基础 | 必须与 missing rule-only/no-N/weak/global rows 区分 |
| `figures/connected_scaffold_v2_hq_selected_contact_pure_white_rerun2115_20260509.png` | 主文 selected scaffold 图 | 白底 mesh scaffold，少依赖 texture | 支持 connected scaffold visual evidence，不支持所有 family solved |
| `figures/pyrite_hq_depth_textured_showcase_20260509.pdf` | 主文 selected non-tree 二选一 | 当前 crystal/symmetry-inspired 最强视觉线之一 | 不是物理 pyrite growth，不是 exact symmetry/watertight claim |
| `figures/coral_depth_textured_showcase_rerun1640_20260509.pdf` | 主文 selected non-tree 二选一或与 pyrite 同留 | 当前 coral/DLA-inspired depth line 有连接证据 | 不是物理 DLA，不代表 coral mesh-space baseline 已闭合 |

## 3. 附录/补充材料建议移动的图/表

| 图/表 | 建议去向 | 原因 | 允许用途 |
|---|---|---|---|
| `figures/gen3d_baseline_texture_fair_zoom_clean_20260510.png` | 附录，或重渲染后再进主文 | 当前 effective-resolution 仍是 qualitative/proxy；zoom 图存在 artifact/裁切风险 | 只作 zoom diagnostic |
| `drafts/effective_resolution_status_table_20260510.tex` | 附录 status table | proxy-only，未完成 same-budget one-shot vs recursive 定量 | 标注 open gate |
| `drafts/ablation_status_tables_20260510.tex` | 附录 | coverage/status inventory，不是 closed ablation | 暴露 missing rows，避免主文 overclaim |
| `figures/gapfill_naturalization_textured_overview_raw_clean_20260510.png` | 附录 | same-root naturalization gap-fill 不足以证明完整 matrix | failure-aware diagnostic |
| `figures/gapfill_non_tree_naturalization_textured_overview_raw_clean_20260510.png` | 附录 | non-tree frontier 仍碎，不能主文正例 | weak/partial naturalization diagnostic |
| `figures/strict_visual_matched_texture_V22_botanical_smooth_contact_sheet_20260510.png` | 补充材料 | 最新候选 screen，视觉仍有低多边形/token artifact | connectivity-positive diagnostic |
| `figures/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_contact_sheet_20260510.png` | 补充材料 | operator-screening sheet 信息量大，非主 claim 图 | transform admission diagnostics |
| `figures/strict_visual_matched_texture_V23_all_family_selected8_render_target_contact_sheet_20260510.png` | 补充材料 | all-family status sheet，像候选池而非论文主图 | visual QA / future selection |
| `figures/strict_matched_pair_candidates_v2_20260510.png` | 补充材料 | candidate screen，不是 closed evidence | 说明 case selection |
| `figures/strict_mode_matched_boundary_candidates_20260510.png` | 补充材料 | boundary candidates 视觉较弱 | 说明 exact mode matching 与 asset quality 的 tension |
| `figures/claim_aligned_metric_summary_20260509.png` | 附录 | 有用但像状态总览/PPT | 指标层级解释 |
| `figures/surface_voxel_connectivity_metric_20260509.pdf` | 附录 | metric explanation，不是结果主图 | 定义 surface-voxel diagnostic |
| `figures/result_matrix_mesh_20260509.png` | 补充材料 | 大矩阵/PPT 风格，协议混合 | qualitative status overview |
| `figures/vine_zoom_in_multiscale_20260509.png` | 补充材料 | zoom 诊断，不是 Trellis2 per-depth texture proof | local recursive structure illustration |
| `figures/vine_depth_textured_strip_20260509_vizworker.png` | 补充材料或 selected export appendix | guide-specific selected display | textureable selected asset |
| `figures/vine_stage5_guide_sweep_20260509.png` | 补充材料 | guide sweep，不是 ablation | material guide sensitivity |
| `figures/depth_parameter_main_candidate_20260509.pdf` | 补充材料 | method-behavior gallery | qualitative parameter behavior |
| `figures/depth_parameter_mesh_showcase_zoom_20260509.pdf` | 补充材料 | zoom gallery，不是 calibrated ablation | local inspection |
| `figures/texture_latest_occpos_paperstyle_contact_20260509.pdf` | 补充材料 | selected textured contact sheet | export compatibility candidates |
| `figures/crystal_stage4_guide_sweep_20260509.png` | 补充材料 | guide sweep | material sensitivity |
| `figures/depth_parameter_mesh_showcase_20260509.png` | 补充材料 | broad gallery | qualitative support only |
| `figures/coral_density_extreme_texture_rerun1900_20260509.png` | 补充材料 | endpoint sweep，不是 ablation | density/compactness behavior |
| `figures/dla_bridge_smoke_stage1_rerun1455_20260509.pdf` | 补充材料 | smoke/negative diagnostic | 支持 “post-hoc bridge 不足” 的边界说明 |
| Hunyuan3D / TRELLIS 非 2 blocked audit | 附录或 supplement | 未完成 runnable comparison | 环境/权重/命令状态，不可进主文已评估表 |

## 4. 4.7 重写要点：Naturalization Claim Gate

4.7 不应写成 “Naturalization improves results” 的主结果节。建议改成：

**Naturalization Is a Local Realization Operator, Not a Topology Repair Mechanism**

重写要点：

1. 先定义角色分工：grammar/projection 持有 topology 与 admissible recursive state；frozen generator 的 naturalization 只在 mask 内改善 local surface/material continuity。
2. 写成 masked flow/local sampling 语义，而不是抽象黑箱：anchor region hard-clamped，editable mask 内运行 local prior，projection 仍在每层之后执行。
3. 把当前三任务 masked naturalization evidence 写成 **focused gate**：botanical-root、coral-frontier、IFS-crystal 可支持局部 surface continuity / silhouette preservation / export compatibility。
4. 明确未闭合矩阵：rule-only、no-N、weak blend、masked local-N、global-N、with/without projection 还不是完整 same-root same-budget matrix。
5. 把 global naturalization 写成 control：它可能平滑局部，但可能降低 locality 或改变 crown/support distribution。
6. 所有文本避免暗示 naturalization 可以替代 projection、修复拓扑或保证 material coherence。

建议主文可写句式：

> Masked naturalization is evaluated only as a local realization step under an already projected recursive state. It can improve local surface/material continuity in the tested rows, but topology admission remains governed by projection and root-attached recursive-state validity.

## 5. 4.9/4.10 合并重写要点

建议把原 `Naturalization, Export, and Effective Resolution` 与 `Boundaries and Supplement Placement` 拆分后重新合并为一个收束小节：

**Export Compatibility, Effective-Resolution Diagnostics, and Boundaries**

重写要点：

1. Export compatibility 放第一段：selected projected meshes can enter Trellis2 texture/PBR export path；这证明 pipeline compatibility，不证明 topology、material propagation 或 final asset quality。
2. Effective resolution 放第二段并降级：当前只有 two-level zoom、local feature scale proxy、terminal detail proxy、face/GLB size；还缺 same token/face budget one-shot vs recursive。
3. Boundaries 放第三段：aggressive fork/radial/echo/hard-DLA/post-hoc bridge/guide-sensitive/holed/dirty texture/uninspected GLB 都进 supplement。
4. Supplement placement 放最后：主文只引用 claim-bearing figures；appendix 只放 status/gates；supplement 放 gallery/guide sweep/candidate screen。
5. 避免 `current`, `draft`, `smoke`, `candidate`, `planned`, `blocked` 等内部日志口吻出现在正式主文；这些可以留在 supplement audit 表。

## 6. 未闭合证据表

| Claim / 实验问题 | 当前证据状态 | 主文可写 | 不能写 | 闭合所需最小证据 |
|---|---|---|---|---|
| Per-depth projection stabilizes conservative recursive programs | 较强。vine/tree conservative compete 有 matched table 和 mesh render | 在 tested conservative vine/tree programs 中，per-depth projection 比 direct/final-only 更能阻断 fragment propagation | 所有 operators / all grammars 都稳定；projection 普遍提升所有 family | 多 seed mean/std；handle-level invalid frontier/cache metrics；connector-aware variants |
| Final-only cleanup 不足 | 中等。terminal table 支持，但 handle-level 中间污染证据不足 | final-only cleanup cannot guarantee admissible intermediate recursive state | final-only 一定视觉更差或所有 case 都失败 | active orphan handles、invalid fired handles、frontier/cache contamination per depth |
| Ordinary one-shot 3D generation 不替代 recursive state | 中等。Trellis2 one-shot 三例可用 | one-shot can synthesize plausible objects but does not enforce requested recursive attachment state in tested tasks | 所有 3D generators 都失败；Hunyuan/TRELLIS 非 2已失败 | Hunyuan3D/TRELLIS 非 2 runnable or blocked exact audit；更多 cases |
| Direct sparse-latent copy 不足 | 中等。vine/pyrite/coral latent-copy 证据存在 | naive sparse copy lacks typed handles, attachment feasibility, projection, re-encoding | sparse latent operation 本身无效；所有 latent editing 失败 | same-root/same-budget latent direct vs projected vs masked-N matrix |
| Mesh-space generated-root recursion 不足 | partial。vine/pyrite 有，coral missing | naive mesh-space generated-root copy exposes disconnected/non-readable support in available rows | sparse-latent language 全面优于 mesh-space；mesh-space baseline 已完整 | coral mesh-space generated-root；mesh repair/re-encode variants；same root/depth/camera/token/face budget |
| Classical procedural baselines | 中等。space colonization/L-system/IFS/DLA controls 和 texture export evidence | classical baselines are strong structural controls; protocol separates structure and export | PS-RSLG universally outperforms classical procedural systems | one-to-one family comparisons with metrics and seeds |
| Operator admission / transform-copy | 中等。V21 screening 支持部分正/负例 | semantic/state/compatibility/export gates screen transform-copy operators | connected export implies valid operator; exact symmetry solved | formal operator-specific metrics；axis mismatch negative retained |
| Masked local naturalization | partial。三任务 focused ablation 有新证据 | local naturalization can improve local realization under projected state in selected rows | naturalization repairs topology；masked-N matrix complete；material coherence solved | rule-only/no-N/weak/global/with-without projection complete matrix |
| Effective resolution / recursive refinement | weak/proxy。two-level zoom + proxy table | qualitative diagnostics suggest recursive motifs can be inspected at attached regions | quantitative effective-resolution superiority；universal terminal-detail improvement | same token/face budget one-shot vs recursive；minimum visible feature scale；terminal detail count；zoom retention score；runtime/memory |
| Texture/PBR export | 中等。多个 selected GLB exports | projected recursive meshes can enter frozen Trellis2 texture/PBR export path | texture proves topology；material propagation solved；all exports are final-quality assets | export success rate, channel QA, render warnings, material coherence metrics |
| Coral/DLA/crystal non-tree connectedness | partial。pyrite/coral selected rows较强，但 DLA/frontier仍风险 | selected coral/pyrite-inspired scaffolds are connected recursive assets under stated diagnostics | physical DLA/crystal growth solved；DLA bridge repair works generally | family-specific metrics；fragmentation audit；mesh-space coral baseline |
| Root/seed robustness | missing/partial | selected cases are evidence-backed examples | robust success rate across seeds/roots | multi-seed tables with mean/std and failure labels |
| Hunyuan3D / TRELLIS non-2 baselines | missing/blocked pending | planned/blocked secondary baseline, not in quantitative table | evaluated, failed, or outperformed | install/run or exact blocked logs with command, env, weights |

## 7. Claim 语言门控

### 可以强写

- Recursive 3D asset generation requires intermediate states that remain attached, addressable, and reusable across depth.
- Direct/final-only cleanup can leave invalid fragments available to future rule selection before terminal pruning.
- Per-depth projection stabilizes the tested conservative recursive programs by enforcing an admissible state before the next depth.
- Ordinary one-shot 3D generation and naive latent/mesh recursion are useful controls but do not provide grammar-owned typed recursive state under the tested protocol.
- Selected projected recursive meshes can be decoded, projected, re-encoded, and exported through the frozen Trellis2 texture/PBR path.

### 只能弱写

- Masked naturalization improves local realization in selected rows.
- Recursive assets show qualitative zoom/terminal-detail diagnostics.
- Pyrite/coral-inspired cases demonstrate connected non-tree scaffold candidates.
- Classical systems can be represented as restricted rule families for framing and evaluation, not dominated as mature procedural systems.

### 不能强 claim

- PS-RSLG universally outperforms classical procedural methods.
- Sparse-latent recursion is categorically superior to mesh-space recursion.
- Naturalization repairs topology or replaces projection.
- Effective resolution is quantitatively superior to one-shot generation.
- Hunyuan3D, TRELLIS 非 2, or all current 3D generators have been evaluated and beaten.
- Occupancy LCR implies watertightness, manifoldness, physical validity, or clean face topology.
- Coral/DLA/crystal cases solve physical growth simulation.
- Texture/PBR export demonstrates material propagation, UV consistency, or final production asset quality.

## 8. 正式投稿前的最小结构清理清单

1. 主文每张图只服务一个 claim；large matrix、candidate screen、guide sweep 全部移出主文。
2. 所有主文 caption 删除 `draft/current/smoke/candidate/planned/blocked` 这类工作日志词。
3. 在主文表 caption 中明确每个 metric 是 occupancy、raw mesh、welded mesh、surface-voxel 还是 render/export diagnostic。
4. `Hunyuan3D` 和 `TRELLIS non-2` 只在 blocked/planned audit 中出现，除非已有可复现结果。
5. `strict` row 与 `selected` row 不混写。尤其 vine baseline 表必须说明 selected stronger stage5 candidate 的角色。
6. Appendix 开头保留 roadmap，但不让主文依赖 appendix 图编号来完成核心论证。
7. 补充材料建立 figure/table index：文件名、角色、允许 claim、主文/附录/补充材料位置、是否闭合。

