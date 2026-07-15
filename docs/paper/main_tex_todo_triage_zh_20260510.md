# main.tex TODO triage（2026-05-10）

范围：只根据 `paper_siga/main.tex`、`agent_revision_and_experiment_requirements.md`、`focused_revision_status_20260509_235104.md` 与当前主文已整合的最新结果判断。未改 `main.tex`，未启动远端实验。

计数说明：本地扫描 `main.tex` 得到 30 个正文中的活跃 `\EvidencePending{}` / `\ExpFigTODO{}` 标记；另有 2 个是 preamble 中的宏定义，不应当作待办。如果上游清单称“32 active markers”，需要先确认是否有未同步版本或是否误把宏定义计入。

## 已部分覆盖但仍不能删除的标记

1. **Texture export compatibility 已部分覆盖**：最新主文已有 selected Trellis2 textured GLB contact sheet、vine depth textured strip、traditional texture baseline rerun、texture/PBR 作为 export compatibility 的保守写法。相关标记：line 496（texture export 只作为 compatibility）、line 456 的 texture export cost 字段、line 120 的 pipeline figure 需求。仍缺最终表格化 QA：GLB import/render、PBR channel、render warnings、UV/seam caveat、texture cost。
2. **Surface-voxel metrics 已部分覆盖**：主文已有 `surface_voxel_connectivity_metric_20260509.pdf`，并在 Metrics 中把 surface-sampled voxel connectivity 定义为 GLB export 后的诊断代理。相关标记：line 495（metric implementation）、line 496（texture/geometry 分离）、line 480（主文 claim figures）。仍缺系统化扩展到全矩阵、mean/std、root/tip/skeleton/latent stability/effective-resolution 指标。

## P0：投稿前必须先闭环的证据/实验

这些标记直接支撑摘要、contribution、claim map、baseline 和主结果；不闭环就只能继续保留保守措辞。

| line | marker | triage |
|---:|---|---|
| 30 | final quantitative improvement numbers | 需要 matched baseline matrix 后才能填摘要量化结论。 |
| 51 | sparse-latent vs set/object/mesh alternatives | 需要 controlled comparison；latest results 尚未覆盖。 |
| 65 | final quantitative claims, root/tip metrics | contribution 量化 claim gate；需要新实验/表。 |
| 86 | direct empirical comparison to object-latent/mesh-only | 与 line 51 同一 P0 baseline gap。 |
| 91 | root/branch/tip, mesh, latent, seed stats | surface-voxel 只覆盖一小块；semantic/seed/latent 仍缺。 |
| 369 | projection variants matrix | 核心因果实验：no/final-only/prune/bridge/repair。 |
| 371 | projection variants prove model-native state selection | 必须配合 line 369 的变体矩阵。 |
| 453 | same-root tree/root/vine matched matrix | 当前摘要/Results 量化 claim 的主 gate。 |
| 457 | latent-space vs mesh-space implementation comparison | 必须证明不是 mesh procedural + texture export。 |
| 468 | controlled comparison in claim map | 与 line 51/86 重复，但表格中会被 reviewer 看到。 |
| 473 | semantic branching metrics | branch/tip/root 语义 claim 仍缺。 |
| 488 | fair baselines matrix | 需要 mesh-space、one-shot、direct、global、masked、final-only、ours。 |
| 489 | sparse-latent grammar vs mesh postprocessing/Trellis texture | 最关键 superiority/necessity 实验。 |
| 491 | root-quality and seed variation | success rate、mean/std 是投稿可信度 gate。 |
| 495 | metric implementation/literature | surface-voxel 已部分覆盖；其余 mesh validity、skeleton、morphology、latent stability、effective resolution 仍缺。 |

## P1：强相关方法/图表/诊断，影响可读性和审稿防御

这些项目不一定全部需要大规模远端实验，但需要图、表、协议或小型 diagnostic 才能把故事讲稳。

| line | marker | triage |
|---:|---|---|
| 53 | 2D scaffold/direct/global/final-only failure panels | 需要同 root/depth protocol 的失败诊断图；支撑 intro 动机。 |
| 120 | sparse voxel / Trellis-style pipeline figure | 用户需提供或批准图；也可结合 texture compatibility 已有结果。 |
| 346 | naturalization ablation matrix | 与 P0 line 490 相关；如果不跑，只能降级 masked naturalization claim。 |
| 347 | masked naturalization improves surface without drift | 需要局部 surface metric + topology drift 指标。 |
| 348 | exact Trellis2 latent/mask/schedule/step/blend details | 可主要靠实现记录和 implementation table 补齐。 |
| 370 | projection mechanism figure | 用户需提供/批准；支撑“不是手工修 mesh”。 |
| 423 | operator scheduling / sparse competition figure and cases | 方法可读性图；最好配一个小例子。 |
| 446 | runtime/memory/per-depth cost | 需要新 profiling 或整理日志；投稿前应有表。 |
| 456 | implementation table | 可部分由日志/文档整理，texture cost 仍需补。 |
| 480 | main/figures-only/supplement split | 论文组织 gate；latest results 已给出候选边界。 |
| 481 | pure-white standardized rerender | 已部分覆盖 latest contact sheets；仍需全主文视觉统一。 |
| 490 | naturalization ablation required | 与 line 346/347 同组；如果缺实验，不能主张 naturalization 贡献。 |
| 496 | texture export as compatibility only | 已部分覆盖；还需最终 GLB/PBR diagnostic table。 |

## P2：文字、术语和较远期扩展

这些不应阻塞当前 evidence-first pass，但投稿前仍要清掉或降级。

| line | marker | triage |
|---:|---|---|
| 103 | graph/shape grammar derivation terminology | 文献/术语校对为主，低成本。 |
| 432 | recursive effective resolution experiment | 若不做 one-shot/detail/token 对比，应降级为 future/observation。 |

## 新实验优先顺序

1. **P0 baseline/projection 闭环**：same-root tree/root/vine 上跑 one-shot/image-entry、direct sparse edit、global/full repair、masked repair、final-only、per-depth prune/bridge/proposed；输出 occ/surface-voxel、root ratio、orphan mass、branch/tip、render success、mean/std。
2. **Latent-vs-mesh 证明**：同一 root 和同一递归规则，对比 sparse-latent grammar 与 mesh-space procedural postprocessing + ordinary Trellis texture export。
3. **Naturalization ablation**：rule-only、no-N、masked-N、global-N、weak blend，分别 with/without projection；指标分 topology drift 与 local surface quality。
4. **Implementation/profiling table**：model/version、hardware、seed count、renderer、grid/token setting、projection threshold、per-depth encode/decode/projection/runtime/memory、texture export cost。
5. **视觉与组织收尾**：pipeline figure、projection mechanism figure、operator scheduling figure、纯白标准化重渲染、main / two figures-only pages / supplement 分流。

## 当前 top blockers

1. **统一 baseline matrix 仍缺**：现在有 projection ablation、matched structural sanity check、texture diagnostics，但还不是同 root/seed/depth/renderer 的完整方法矩阵。
2. **latent-space superiority 尚未证明**：必须避免 reviewer 认为结果只是 procedural mesh 递归后接 Trellis2 texture。
3. **semantic metrics 不足**：root/tip/branch、orphan handle、seed variation、mean/std 还没支撑摘要和 contribution 的量化写法。
4. **naturalization claim 不稳**：masked naturalization 的表面质量收益和 topology drift 代价还没闭环。
5. **texture 与 topology 必须继续分离**：texture export compatibility 和 surface-voxel diagnostic 已部分覆盖，但不能替代 watertight/topology-clean mesh claim。
