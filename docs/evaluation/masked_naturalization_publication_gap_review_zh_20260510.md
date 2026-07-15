# Masked Local Naturalization 发表级 Gap Review 2026-05-10

## 结论

当前 M1 已经达到“主文 narrow ablation”的最小发表闭合：3 个 matched local tasks、6 个 realization protocols、3 个 deterministic seeds，聚合为 18 行 protocol mean/std 和 3 行 task-level recommendation stability。三任务中 `per-depth/masked local-N` 均为 3/3 seeds 推荐，`masked_local_win_rate=1.0`，`acceptance_gate_pass=True`。

可进入主文的限定结论是：在 per-depth projection 已经维持递归状态可投影的前提下，masked local naturalization 是当前测试的局部 realization controls 中最稳定的选择；它改善局部 surface continuity / material realization，同时比 global naturalization 更保守地保留旧状态。M1 不能支撑 global topology repair、watertight/manifold mesh、物理生长真实性或类别级鲁棒性的声明。

## 已可进主文的 Narrow Ablation

M1 可作为主文窄消融表/段落进入论文，理由如下：

- 任务覆盖：`botanical_root`、`coral_frontier`、`ifs_crystal` 三个 matched local tasks，覆盖 root-like attachment、frontier-like branching、crystal/IFS-like angular growth 三种局部结构压力。
- 协议覆盖：每个 task 均包含 `rule-only`、`final-only`、`per-depth/no-N`、`per-depth/weak`、`per-depth/global-N`、`per-depth/masked local-N` 六个协议。
- seed 闭合：每个 task-protocol 均有 `seed_count=3`，`m1_protocol_meanstd.csv` 共 18 行，每行均有 mean/std。
- 推荐稳定性：`m1_task_recommendation_stability.csv` 中三任务 `masked_local_wins=3`、`masked_local_win_rate=1.0`，winner variants 全部为 `per_depth_masked_naturalization`。
- acceptance gates：三任务均 `acceptance_gate_pass=True`；masked local-N 的 `masked_lcr_mean=1.0`，masked silhouette 均高于 M1 gate，且主分数均优于 no-N、weak、global-N。

主文 compact table 建议只报告三行 masked local-N，同时在正文或 supplement 给完整 18 行表。三行主文数值建议如下：

| Task | Wins | Score mean/std | LCR | Locality | Rough. deg | Silh. | Gain vs no-N | Locality gain vs global-N |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| botanical root | 3/3 | 0.8763 / 0.0005 | 1.0000 | 0.9242 | 10.95 | 0.9117 | 0.0831 | 0.0841 |
| coral frontier | 3/3 | 0.8708 / 0.0009 | 1.0000 | 0.9297 | 11.67 | 0.9108 | 0.0780 | 0.0842 |
| IFS crystal | 3/3 | 0.8833 / 0.0029 | 1.0000 | 0.9333 | 11.19 | 0.9187 | 0.1183 | 0.1023 |

## 推荐指标组合

最适合衡量 masked local naturalization 的指标不应是单一 composite score，而应是“连通性 + 形状保守性 + 局部编辑性 + 表面质量 + 视觉 QA”的组合：

- Connectivity：主列使用 `surface_largest_component_ratio` / LCR，并可在 supplement 附 `connectivity_score`。解释为 mesh surface largest-component proxy，不解释为 watertightness、manifoldness 或 topology repair。
- Silhouette / projection：使用 `silhouette_iou_vs_per_depth_projection`，说明 naturalization 后与 per-depth/no-N 投影控制的一致性；它约束“不是靠全局形变换取平滑”。如需更完整，可在补充材料报告 `silhouette_iou_vs_raw`。
- Locality / mask-change：使用 `locality_preservation_score` 作为主文列，并在方法中说明它综合 per-depth silhouette、bounding-box extent preservation 和 naturalization scope locality；`mask_change_voxel_ratio_proxy` 可作为 supplement/方法中的 mask edit-size 证据，不宜作为唯一主文结论。
- Root attachment：M1 只有 mesh-level proxy，尚无 `root_attached_mass_ratio` 或 handle/frontier sidecar；主文可把 botanical root 作为 task 名称与视觉案例，但不能声称已通过 root-attachment 指标证明根部语义连接。M2/M3 应补 root attachment / reachable frontier sidecar 后再加强该口径。
- Mesh roughness / blockiness：主文用 `local_normal_variation_mean_deg` 作为 Rough.，并在 supplement 附 `connectivity_blockiness_index` 或 `blockiness_score`、`mesh_quality_score`。写法应是 adjacent-face normal variation / axis-aligned blockiness proxies，不是人类视觉自然度的充分证明。
- Visual QA：必须配同相机 visual contact sheet。M1 数值可闭合主文窄消融，但发表级视觉说服仍依赖 M2 的 3 tasks x 6 protocols contact sheet、mask overlay、before/after edit-region overlay。

推荐主文指标最小集合：`Wins`、`Score mean/std`、`LCR`、`Locality`、`Rough. deg`、`Silh.`、`Gain vs no-N`。若版面允许，加 `Locality gain vs global-N`；若版面紧张，把该列放正文一句话。

## M1 不能 Claim 的内容

M1 不能写成以下声明：

- masked local naturalization 是 global topology repair 或全局 mesh repair 方法。
- naturalization 单独保证 connectivity；当前 connectivity 改善绑定 per-depth projection 和本地测试协议。
- 输出为 watertight、clean manifold、self-intersection-free 或 production-ready mesh。
- 结果证明真实 botanical/coral/crystal/DLA 物理生长正确性。
- 结果证明 category-wide robustness；当前只有 3 个 matched local tasks 和 3 deterministic seeds。
- 结果优于所有外部 naturalization、remeshing、surface repair 或 reconstruction 方法；当前只比较本地 6 个协议。
- masked local-N 已被证明不破坏下一步 grammar-readable state；M1 没有 active handle / frontier reachability / root attachment sidecar。
- visual naturalness 已完全证明；M1 数值指标需要 M2 contact sheet 和视觉 QA 补强。

## M2 / M3 还要跑什么

M2 应补视觉闭合，目标是让审稿人能直接看出 masked local-N 的局部连续性收益和 global-N 的旧状态改写风险：

- 3 tasks x 6 protocols 同相机 contact sheet：`rule-only`、`final-only`、`per-depth/no-N`、`per-depth/weak`、`per-depth/global-N`、`per-depth/masked local-N`。
- 每个 task 至少一组 zoom visual：raw / final-only / no-N / weak / global-N / masked local-N。
- mask overlay 与 before-after edit-region overlay，显示 masked local-N 的实际编辑区域。
- 对 global-N 和 weak 的 caption 边界：它们是 controls；即使视觉更平滑，也不解释为递归状态或拓扑修复优越。

M3 应补状态语义闭合，目标是证明 masked local-N 不只是 mesh-level 更好，而是保留下一步递归可读状态：

- `active_handle_survival_rate`
- `orphan_handle_count`
- `reachable_frontier_count`
- `frontier_reachability_rate`
- `root_attached_mass_ratio`
- `deleted_active_support_mass`
- `handle_drift_l2_mean`
- `mask_overlap_with_active_handles`

M3 的接受口径应是：masked local-N 相比 global-N 保留更高 handle/frontier/root attachment，同时相比 no-N/weak 改善 surface continuity。没有 M3 时，论文只能说 mesh-level proxies 和 locality/silhouette 未显示明显全局改写。

## 论文实验与方法写法建议

实验段落建议使用窄而稳的写法：

> We evaluate masked local naturalization with a minimal three-seed ablation over three matched local tasks and six realization protocols. The protocols include rule-only proposals, final-only projection, per-depth projection without naturalization, weak local naturalization, global naturalization, and masked local naturalization. Across all three tasks, the masked local variant is selected in all three deterministic seeds under the acceptance gate. We report a composite ranking score together with surface LCR, locality preservation, local normal variation, silhouette agreement with the per-depth/no-naturalization control, and gains against no-naturalization and global-naturalization controls. The result supports masked naturalization as a local surface-continuity operator under per-depth projection, not as a global topology repair mechanism.

方法段落建议明确 score contract：

- `main_text_score` 是 ranking score，不是单独物理指标；它组合 connectivity、locality/preservation、roughness gain、silhouette、mesh quality、blockiness、triangle efficiency、per-depth projection、masked-scope evidence。
- LCR 是 surface largest-component proxy；locality 是 silhouette/bbox/scope-locality proxy；roughness 是 adjacent-face normal variation；silhouette 是 tolerance-dilated multiview 2D occupancy IoU。
- acceptance gate 应写为推荐筛选条件：候选需满足 LCR 和 silhouette 下限，再按 composite score 选主文候选。
- 所有结论需绑定“matched local tasks, deterministic seeds, tested protocols”。

## 最终图表清单

主文建议：

- Table 1 / compact ablation：三任务 masked local-N 三 seed mean/std、win rate、LCR、locality、roughness、silhouette、gain vs no-N，可选 locality gain vs global-N。
- Figure 1 / visual ablation：3 rows x 6 columns 同相机 contact sheet，列为六个协议；若版面不足，主文放 3 rows x 4 columns，supplement 放完整六列。
- Figure 2 / mask locality visual：每个 task 一例 mask overlay + before/after edit-region zoom，用于解释 masked local-N 的编辑范围。

补充材料建议：

- Supplement Table S1：完整 18 行 protocol mean/std，包含 Score、LCR、connectivity_score、locality、roughness、silhouette、mesh_quality、blockiness。
- Supplement Table S2：三任务 recommendation stability，包含 3/3 wins、win rate、gain vs no-N/weak/global-N、locality gain vs global-N、acceptance gate。
- Supplement Figure S1：每个 seed 的 full contact sheet，展示稳定性不是单个 seed cherry-pick。
- Supplement Figure S2：M3 sidecar 若完成，展示 handle/frontier/root attachment 指标。

## 当前缺口优先级

1. 先跑 M2 完整 visual contact sheet，补齐 weak/global-N/masked local-N 同相机图和 mask overlay。
2. 补 M3 sidecar 指标，尤其是 root attachment、active handle survival、frontier reachability 和 deleted active support mass。
3. 主文 table 采用三行 compact 版本，完整 18 行放 supplement；caption 必须写明“不支持 global topology repair”。
4. 方法段落加入 metric contract 和 acceptance gate，避免 reviewer 把 composite score 误读为单一几何质量指标。
5. 视觉 QA 后再决定是否把 `mesh_quality_score` / `blockiness` 放主文；目前更适合作为 supplement 支撑 roughness/blockiness 口径。

## 本轮读取依据

- `docs/evaluation/masked_naturalization_publication_ready_update_zh_20260510.md`
- `results/masked_naturalization_ablation_m1_20260510/m1_publication_summary.md`
- `results/masked_naturalization_ablation_m1_20260510/m1_protocol_meanstd.csv`
- `results/masked_naturalization_ablation_m1_20260510/m1_task_recommendation_stability.csv`
- `paper_siga/drafts/masked_naturalization_ablation_table_20260510.tex`
- `assets/evaluate_masked_naturalization_ablation_20260510.py`
- `tests/test_masked_naturalization_ablation_20260510.py`
