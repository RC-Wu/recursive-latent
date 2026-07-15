# Masked Local Naturalization 发表级状态审计 Hooke 2026-05-10

## 审计范围

本审计只复核 masked local naturalization 窄任务，不改论文主文和脚本。复核对象包括：

- `results/masked_naturalization_ablation_20260510/evaluation_current/`
- `paper_siga/drafts/masked_naturalization_ablation_table_20260510.tex`
- `visuals/masked_naturalization_ablation_zoom_20260510/`

当前证据包已经形成 3 个任务乘 6 个 protocol 的本地闭合矩阵，共 18 行。任务为 `botanical_root`, `coral_frontier`, `ifs_crystal`。六列 protocol 为 `rule-only`, `final-only`, `per-depth/no-N`, `per-depth/weak`, `per-depth/global-N`, `per-depth/masked local-N`。

## 当前结论

现有 6 protocol 指标足够支持一个窄而清楚的主文结论：在 per-depth projection 已经稳定递归状态的前提下，masked local naturalization 是三类任务中最好的局部自然化策略。它同时保持 surface LCR 为 1.0，维持相对 per-depth/no-N 的较高 silhouette/locality，并降低局部法线粗糙度。

推荐行如下：

| task | recommended variant | score | LCR | silhouette vs per-depth | local normal variation |
|---|---|---:|---:|---:|---:|
| botanical_root | per_depth_masked_naturalization | 0.8757 | 1.0000 | 0.9137 | 11.00 |
| coral_frontier | per_depth_masked_naturalization | 0.8699 | 1.0000 | 0.9047 | 11.74 |
| ifs_crystal | per_depth_masked_naturalization | 0.8856 | 1.0000 | 0.9260 | 11.09 |

相对 per-depth/no-N，masked local-N 的 score 提升为 0.0822, 0.0718, 0.1211；局部法线变化降低 2.39, 2.02, 3.22 度。相对 global-N，masked local-N 的 locality 提升为 0.0822, 0.0678, 0.1128。这组数值已经足够区分 “局部 mask 内自然化” 和 “全局 smoothing/repair” 的行为差异。

## 指标是否足够区分

足够区分的部分：

- `connectivity` 能区分 raw/final-only/per-depth 结构稳定性。raw 在三个任务中分别为 0.0937, 0.4126, 0.0000；masked local-N 均为 1.0000。
- `locality` 能惩罚 global-N 对旧状态的全局改写。global-N 平均 locality 为 0.8425，masked local-N 为 0.9301。
- `roughness_deg` 能显示自然化对局部表面连续性的作用。rule-only 平均为 38.64 度，masked local-N 平均为 11.28 度。
- `silhouette` 能防止 “靠整体形变换平滑” 的假阳性。masked local-N 对 per-depth/no-N 的 silhouette 保持在 0.9047 到 0.9260。
- `mesh_quality` 和 `blockiness` 可以作为辅助 proxy，显示自然化不是单纯靠增加碎片或退化面换取分数。

不足以完全区分的部分：

- 目前 task 数只有 3，且 metadata 中 `depth`, `seed`, `root_id` 为空，不能支持跨 seed、跨 root 的统计结论。
- `main_text_score` 是复合分数，可以排序 protocol，但审稿人可能要求拆解权重、敏感性和置信区间。
- `surface_largest_component_ratio` 是 surface/mesh 诊断，不等于 watertight topology，也不等于 grammar handle reachability。
- `roughness_deg` 是相邻三角面法线 proxy，不等于人类视觉自然度或材料连续性。
- visual zoom 只覆盖 4 个 protocol：raw, final-only, per-depth/no-N, masked local-N；没有 weak/global-N 的同布局可视化，因此不能视觉上完整证明 masked local-N 优于 weak/global-N。

## 可视化状态

`visuals/masked_naturalization_ablation_zoom_20260510` 包含 12 个 case，每个 case 有：

- `overview_raw.png`
- `overview_callouts.png`
- `zoom_01.png`
- `zoom_01_callouts.png`
- `zoom_02.png`
- `strict_matched_zoom_comparison.png`

这些图满足白底、方图、真实 camera render、nested zoom 和 callout 的基本要求。它们足够作为主文或补充图来说明 raw/final-only/per-depth/no-N/masked local-N 的局部视觉差异。

缺口是：weak 和 global-N 没有同样的 zoom visual。当前表格能说明 weak/global-N 的数值差异，但如果主文要强调 masked local-N 比 weak/global-N 更合适，最好补齐同相机、同 callout 的 weak/global-N 图，或者把 weak/global-N 留在表格中作为数字控制，不在图注里过度展开。

## 主文稳妥写法

可以写：

- “Masked local naturalization is evaluated as a local realization operator under per-depth projection.”
- “Across three matched tasks, per-depth masked local-N is the recommended row by the joint score.”
- “It preserves surface connectivity in the tested rows (LCR = 1.0) while maintaining high silhouette agreement with the per-depth/no-N control.”
- “Compared with per-depth/no-N, it improves local surface continuity as measured by local normal variation.”
- “Compared with global-N, it better preserves locality, indicating that the gain is not simply from global smoothing.”

必须保守的 claim boundary：

- 不能写成 global topology repair。
- 不能声称 masked local-N 单独保证 connectivity；当前 connectivity 与 per-depth projection 绑定。
- 不能声称物理 DLA/crystal 生长正确。
- 不能声称 watertight topology、clean manifold、最终 GLB 材质一致性。
- 不能声称 category-wide robustness；目前只有 3 个任务、无 seed/root 统计。
- 不能声称优于所有 naturalization 方法；这里只比较六个本地 protocol。

## 为了主文更稳还缺什么

最优先补齐：

1. 补 metadata：每行写入 root id、seed、depth、operator family、projection thresholds、mask schedule、naturalization step count。
2. 补 seed/root 统计：至少每任务 3 seeds 或 3 roots，报告 mean/std 和推荐行稳定性。
3. 补 weak/global-N 的同相机 zoom visual，使 6 protocol 表和可视化完全对齐。
4. 给 `main_text_score` 写清权重或提供 score ablation，避免审稿人认为 composite score 是人工调参。
5. 增加 handle-level 指标：active handle survival、orphan handle count、reachable frontier count，证明 masked local-N 没有破坏递归可执行状态。

次优先但有助于发表：

- 加 Chamfer/normal-consistency 到 per-depth/no-N 的局部 mask 区域，只在 edit mask 内评估，不混入全局形变。
- 加 before/after mask overlay，显示 naturalization 只发生在 editable mask。
- 加 mesh validity：non-manifold edges、self-intersection proxy、degenerate face rate、watertightness caveat。
- 加 runtime/memory：masked local-N 相对 no-N/weak/global-N 的额外开销。
- 加 human visual preference 或 blind pair ranking，只针对局部 continuity，不问全局 topology。

## 对 paper 表格的审计

`paper_siga/drafts/masked_naturalization_ablation_table_20260510.tex` 与 evaluation 当前表一致，包含 18 行和核心列 `Conn.`, `Locality`, `Rough.`, `Silh.`, `MeshQ`, `Score`。caption 已经包含关键边界：“selected masked-local rows support local surface continuity under per-depth projection, not global topology repair.” 这个口径是正确的。

建议后续如果进主文，表 caption 继续保留两点：

- `Rough.` 越低越好。
- `Silh.` 是相对 per-depth/no-N control，不是相对真实物理目标。

## 发表级状态判定

当前状态：可以作为主文窄表 + 窄图进入论文，但只能支撑 “masked local naturalization is a local surface-continuity operator under projected recursive state”。

还不能作为强主文结论证明 “naturalization solves topology / improves all recursive assets / is robust across seeds and roots”。如果主文空间紧，建议保留：

- 一段短叙述。
- 一个 3-task summary table。
- 一个 3-row visual contact sheet。

把完整 18 行指标、score contract、weak/global-N 细节和未闭合风险放进 supplement。

## 已复核文件

- `results/masked_naturalization_ablation_20260510/evaluation_current/summary.json`
- `results/masked_naturalization_ablation_20260510/evaluation_current/metrics.csv`
- `results/masked_naturalization_ablation_20260510/evaluation_current/paper_table_masked_naturalization_ablation_20260510.csv`
- `results/masked_naturalization_ablation_20260510/evaluation_current/protocol_summary_masked_naturalization_ablation_20260510.csv`
- `results/masked_naturalization_ablation_20260510/evaluation_current/score_recommendations.csv`
- `results/masked_naturalization_ablation_20260510/evaluation_current/masked_local_advantage_20260510.csv`
- `paper_siga/drafts/masked_naturalization_ablation_table_20260510.tex`
- `visuals/masked_naturalization_ablation_zoom_20260510/matched_camera_zoom_plan.json`
- `visuals/masked_naturalization_ablation_zoom_20260510/*/strict_matched_zoom_comparison.png`
