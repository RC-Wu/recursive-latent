# Masked Local Naturalization 论文插入就绪更新 2026-05-10

## 范围

本更新只整合 masked local naturalization 的本地 M1 三 seed 结果和已有发表闭合计划，不修改 `paper_siga/main.tex`、baseline/V24 脚本或远端任务。已核对输入文件存在：

- `results/masked_naturalization_ablation_m1_20260510/m1_publication_summary.md`
- `results/masked_naturalization_ablation_m1_20260510/m1_protocol_meanstd.csv`
- `results/masked_naturalization_ablation_m1_20260510/m1_task_recommendation_stability.csv`
- `results/masked_naturalization_ablation_m1_20260510/m1_protocol_meanstd.json`
- `results/masked_naturalization_ablation_m1_20260510/m1_task_recommendation_stability.json`
- `docs/evaluation/masked_naturalization_next_experiment_spec_zh_20260510_hooke2.md`
- `docs/evaluation/masked_naturalization_publication_closure_plan_zh_20260510_hooke.md`
- `paper_siga/main.tex`（只读）

## 当前判定

M1 已达到“窄主文消融”门槛：3 个 matched tasks、6 个 protocol、3 个 deterministic seeds，共 54 个评估行被聚合为 18 行 mean/std 和 3 行推荐稳定性。三个任务的 `per-depth/masked local-N` 均为 3/3 seeds 推荐行，`acceptance_gate_pass=True`。

可进入主文的结论应限定为：在 per-depth projection 已经维持可递归状态的前提下，masked local naturalization 是当前测试的局部 realization controls 中最稳定的选择。它支持 local surface-continuity / material-realization 口径，不支持 global topology repair 口径。

## 已达主文消融门槛的部分

| 项目 | 状态 | 证据 |
|---|---|---|
| 3 tasks x 6 protocols x 3 seeds | 已达 | `m1_protocol_meanstd.csv` 为 18 行，每行 `seed_count=3` |
| masked local-N 推荐稳定性 | 已达 | 三任务均 `masked_local_wins=3`, `win_rate=1.0` |
| LCR gate | 已达 | 三任务 masked local-N 的 `masked_lcr_mean=1.0` |
| score vs no-N | 已达 | mean gain 为 0.0831 / 0.0780 / 0.1183 |
| score vs global-N | 已达 | mean gain 为 0.0578 / 0.0575 / 0.0631 |
| locality vs global-N | 已达 | mean gain 为 0.0841 / 0.0842 / 0.1023 |
| silhouette 保守性 | 已达 | masked local-N mean silhouette 为 0.9117 / 0.9108 / 0.9187，均高于 M1 gate 0.84 |

## 推荐指标口径

主文建议使用“推荐稳定性 + 拆解指标”的口径，而不是只报告 composite score：

- `main_text_score_mean/std`：只作为 protocol ranking 的 compact score，caption 必须说明它是 composite score。
- `surface_largest_component_ratio_mean` 或 LCR：作为 surface connectivity proxy。它不是 watertightness、manifoldness 或 topology repair 证明。
- `locality_preservation_score_mean`：用于说明 masked local-N 相对 global-N 更少改写旧状态。
- `local_normal_variation_mean_deg_mean/std`：用于说明局部 surface continuity；越低越平滑，但不是人类视觉自然度的充分证明。
- `silhouette_iou_vs_per_depth_projection_mean`：用于约束“不是靠全局形变换取平滑”。建议写作 silhouette agreement with the per-depth/no-N projection control。
- `seed_count` 和 `masked_local_win_rate`：用于把 single-run 结论升级为 minimal three-seed stability。

不建议单独用 `connectivity_score` 替代 LCR，也不建议把 `roughness_score` 或 `mesh_quality_score` 作为主文核心列。它们可放补充材料。

## 建议主文表格和图

主文 compact table 建议一行一个 task，只放 masked local-N 的 mean/std 和关键对比：

| Task | Win rate | Score mean/std | LCR | Locality | Roughness deg | Silhouette | Gain vs no-N | Locality gain vs global-N |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| botanical root | 3/3 | 0.8763 / 0.0005 | 1.0000 | 0.9242 | 10.95 | 0.9117 | 0.0831 | 0.0841 |
| coral frontier | 3/3 | 0.8708 / 0.0009 | 1.0000 | 0.9297 | 11.67 | 0.9108 | 0.0780 | 0.0842 |
| IFS crystal | 3/3 | 0.8833 / 0.0029 | 1.0000 | 0.9333 | 11.19 | 0.9187 | 0.1183 | 0.1023 |

图建议：

- 主文图：优先使用 3 rows x 4 columns 的现有 visual（raw / final-only / per-depth no-N / masked local-N）说明局部连续性变化，caption 明确它不是完整 6 protocol visual proof。
- 若主线程能补 M2：改用 3 rows x 6 columns contact sheet，与表格列完全一致，weak/global-N 作为 controls。
- 补充材料：完整 18 行 protocol mean/std 表，展示 rule-only、final-only、no-N、weak、global-N、masked local-N 全部指标。

## 还缺的 M2 / M3

M2 visual closure 仍缺：

- `per-depth/weak` 和 `per-depth/global-N` 的同相机 zoom visual。
- 3 tasks x 6 protocols 的完整 contact sheet。
- mask overlay / before-after edit-region overlay。
- 对 weak/global-N 的图注边界：若视觉更平滑，只能解释为 control，不可写成拓扑修复。

M3 sidecar metric 仍缺：

- `active_handle_survival_rate`
- `orphan_handle_count`
- `reachable_frontier_count` 和 `frontier_reachability_rate`
- `root_attached_mass_ratio`
- `deleted_active_support_mass`
- `handle_drift_l2_mean`
- `mask_overlap_with_active_handles`

没有 M3 时，不能声称 masked local-N “不破坏下一步 grammar-readable state” 已被 handle/frontier 指标证明。当前只能说 mesh-level proxies 和 locality/silhouette 没显示明显全局改写。

## 不能夸大的边界

论文中应避免以下表述：

- 不写 masked local-N 是 global topology repair。
- 不写 naturalization 单独保证 connectivity；当前 connectivity 结论绑定 per-depth projection。
- 不写 watertight topology、clean manifold、self-intersection-free 或 production-ready mesh。
- 不写物理生长正确性，例如真实 coral/crystal/DLA 生长。
- 不写 category-wide robustness；当前只覆盖 3 个 matched local tasks 和 3 deterministic seeds。
- 不写优于所有 naturalization/repair 方法；只比较当前 6 个本地 protocol。
- 不把 composite score 当唯一证据；必须同时给 LCR、locality、roughness、silhouette。

## 可直接插入论文的英文段落草稿

For masked local naturalization, we report a minimal three-seed ablation over three matched local tasks and six realization protocols: rule-only proposals, final-only projection, per-depth projection without naturalization, weak local naturalization, global naturalization, and masked local naturalization. Under per-depth projection, the masked local variant is selected by the joint score in all three seeds for all tasks. Its mean scores are 0.8763, 0.8708, and 0.8833 for botanical-root, coral-frontier, and IFS-crystal cases, respectively, with surface LCR equal to 1.0 in all rows. Compared with the per-depth no-naturalization control, masked local naturalization improves the score by 0.0780--0.1183 while maintaining silhouette agreement above 0.91 with the per-depth control. Compared with global naturalization, it preserves higher locality by 0.0841--0.1023. These results support masked naturalization as a local surface-continuity and realization operator under an already projected recursive state, not as a global topology repair mechanism.

## Compact table 草稿

```latex
\begin{table}[t]
\centering
\caption{Three-seed masked local naturalization ablation. Scores are mean/std over deterministic seeds. LCR is a surface largest-component proxy; Rough. is local normal variation in degrees, where lower is smoother. The table supports local realization under per-depth projection, not global topology repair.}
\label{tab:masked-naturalization-m1-compact}
\begin{tabular}{lccccccc}
\toprule
Task & Wins & Score & LCR & Locality & Rough. & Silh. & Gain vs no-N \\
\midrule
Botanical root & 3/3 & 0.8763 / 0.0005 & 1.0000 & 0.9242 & 10.95 & 0.9117 & 0.0831 \\
Coral frontier & 3/3 & 0.8708 / 0.0009 & 1.0000 & 0.9297 & 11.67 & 0.9108 & 0.0780 \\
IFS crystal & 3/3 & 0.8833 / 0.0029 & 1.0000 & 0.9333 & 11.19 & 0.9187 & 0.1183 \\
\bottomrule
\end{tabular}
\end{table}
```

如主文空间允许，可在 table 中追加 `Locality gain vs global-N` 一列：0.0841 / 0.0842 / 0.1023。若空间紧，该列可放正文句子或 supplement。

## 验证记录

- `m1_protocol_meanstd.csv`：18 rows，20 columns。
- `m1_task_recommendation_stability.csv`：3 rows，15 columns。
- JSON 与 CSV 行数一致：`m1_protocol_meanstd.json` 为 18 entries，`m1_task_recommendation_stability.json` 为 3 entries。
- 三任务 `acceptance_gate_pass=True`。
- 本轮未修改聚合脚本，未启动远端任务，未启动 GPU，未编辑 `paper_siga`。
