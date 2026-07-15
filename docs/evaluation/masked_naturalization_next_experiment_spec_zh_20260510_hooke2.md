# Masked Local Naturalization 下一步发表级实验规格 Hooke2 2026-05-10

## 范围和原则

本规格只推进 masked local naturalization 支线，不修改 `paper_siga/main.tex`，不启动远端任务，不删除已有文件。目标是把当前 3 tasks × 6 protocols × single root/seed 的结果，推进为可落地、可复跑、可进入主文或补充材料的剩余实验矩阵。

已读并对齐以下文件：

- `docs/evaluation/masked_naturalization_publication_closure_plan_zh_20260510_hooke.md`
- `assets/masked_naturalization_ablation_assets_20260510.py`
- `assets/evaluate_masked_naturalization_ablation_20260510.py`
- `results/masked_naturalization_ablation_20260510/evaluation_current/*.csv`

本轮新增一个只读/导出型规格脚本，不改现有 evaluator 逻辑：

- `assets/export_masked_naturalization_next_experiment_spec_20260510.py`

该脚本输出：

- `results/masked_naturalization_ablation_20260510/next_experiment_spec_hooke2_20260510/manifest.json`
- `results/masked_naturalization_ablation_20260510/next_experiment_spec_hooke2_20260510/m1_minimal_replicate_manifest_20260510.csv`
- `results/masked_naturalization_ablation_20260510/next_experiment_spec_hooke2_20260510/m2_visual_closure_manifest_20260510.csv`
- `results/masked_naturalization_ablation_20260510/next_experiment_spec_hooke2_20260510/m3_handle_state_metric_schema_20260510.json`
- `results/masked_naturalization_ablation_20260510/next_experiment_spec_hooke2_20260510/next_experiment_commands_20260510.json`

## 当前已有结果结构

现有结果目录：

- `results/masked_naturalization_ablation_20260510/`

已有生成脚本可本地生成：

```bash
python3 assets/masked_naturalization_ablation_assets_20260510.py \
  --out-dir results/masked_naturalization_ablation_20260510 \
  --resolution 56 \
  --depth-count 3 \
  --seed 20260510
```

已有 evaluator 可评估：

```bash
python3 assets/evaluate_masked_naturalization_ablation_20260510.py \
  --asset-dir results/masked_naturalization_ablation_20260510 \
  --out-dir results/masked_naturalization_ablation_20260510/evaluation_current
```

当前固定任务：

- `botanical_root`
- `coral_frontier`
- `ifs_crystal`

当前固定 protocols / variants：

| protocol label | variant |
|---|---|
| rule-only | `raw_grammar_proposal` |
| final-only | `final_only_projection_repair` |
| per-depth/no-N | `per_depth_projection` |
| per-depth/weak | `per_depth_weak_naturalization` |
| per-depth/global-N | `per_depth_global_naturalization` |
| per-depth/masked local-N | `per_depth_masked_naturalization` |

当前 evaluator 已有字段：

- identity: `task_id`, `task_family`, `variant`, `protocol_column`, `ablation_read`
- recommendation: `score_recommendation`, `main_text_score`
- connectivity: `surface_component_count`, `surface_largest_component_ratio`, `surface_largest_component_vertices`, `surface_small_component_count_lt100`, `connectivity_score`
- locality/shape preservation: `silhouette_iou_vs_raw`, `silhouette_iou_vs_per_depth_projection`, `locality_preservation_score`, `bbox_extent_l1_vs_per_depth_projection`
- roughness: `local_normal_variation_mean_deg`, `global_normal_variation_mean_deg`, `roughness_score`, `roughness_gain_vs_raw`
- mesh quality: `mean_triangle_aspect_ratio`, `degenerate_face_fraction`, `mesh_quality_score`, `blockiness_score`, `connectivity_blockiness_index`, `axis_aligned_normal_fraction`
- size/cost proxy: `vertex_count`, `triangle_count`, `surface_area`, `bbox_diag`, `mask_change_voxel_ratio_proxy`, `triangle_efficiency_score`
- provenance: `projection_schedule`, `naturalization_scope`, `mesh_path`, `metadata_path`

这些字段已经足够支持“局部 masked naturalization 在 per-depth projection 下提升局部连续性”的窄结论，但还不能支持 seed/root robust claim。

## M1: 最小发表级重复矩阵

### 目标

把当前 single seed 结果扩成本地可跑的 3-seed mean/std。优先使用现有 `assets/masked_naturalization_ablation_assets_20260510.py` 和 `assets/evaluate_masked_naturalization_ablation_20260510.py`，不改 evaluator。

### Exact inputs

Tasks：

- `botanical_root`
- `coral_frontier`
- `ifs_crystal`

Seeds：

- `20260510`
- `20260511`
- `20260512`

Depth / resolution：

- `--depth-count 3`
- `--resolution 56`

Variants：

- `raw_grammar_proposal`
- `final_only_projection_repair`
- `per_depth_projection`
- `per_depth_weak_naturalization`
- `per_depth_global_naturalization`
- `per_depth_masked_naturalization`

Total rows：

- `3 tasks × 3 seeds × 6 variants = 54 rows`

### 输出路径

每个 seed 独立输出一个 asset/eval 目录，避免覆盖现有单 seed 结果：

- `results/masked_naturalization_ablation_20260510_seed20260510/`
- `results/masked_naturalization_ablation_20260510_seed20260511/`
- `results/masked_naturalization_ablation_20260510_seed20260512/`

每个目录内保持现有结构：

- `manifest.json`
- `manifest.csv`
- `tasks/{task_id}/{variant}/mesh.obj`
- `tasks/{task_id}/{variant}/metadata.json`
- `evaluation_current/metrics.csv`
- `evaluation_current/paper_table_masked_naturalization_ablation_20260510.csv`
- `evaluation_current/protocol_summary_masked_naturalization_ablation_20260510.csv`
- `evaluation_current/score_recommendations.csv`
- `evaluation_current/masked_local_advantage_20260510.csv`

本轮已导出 M1 manifest：

- `results/masked_naturalization_ablation_20260510/next_experiment_spec_hooke2_20260510/m1_minimal_replicate_manifest_20260510.csv`

### Metrics 字段

直接复用 evaluator 字段，M1 后处理应额外聚合：

- group keys: `task_id`, `variant`, `protocol_column`
- mean/std: `main_text_score`, `connectivity_score`, `surface_largest_component_ratio`, `locality_preservation_score`, `local_normal_variation_mean_deg`, `silhouette_iou_vs_per_depth_projection`, `mesh_quality_score`, `connectivity_blockiness_index`
- stability: `recommended_task_count_by_seed`, `masked_local_wins_count`, `masked_local_win_rate`
- failure flags: `lcr_below_0p98_count`, `silhouette_below_0p84_count`, `metadata_missing_seed_count`

### Acceptance gate

M1 进入发表级补充表的最低 gate：

- 所有 54 个 expected mesh/metadata/eval rows 存在。
- 每个 seed 的 evaluator 正常完成，无空 mesh。
- 每个 task 中，`per_depth_masked_naturalization` 至少 2/3 seeds 为推荐行；如果不是，必须写 failure boundary。
- `per_depth_masked_naturalization` 的 mean surface LCR >= 0.98。
- `per_depth_masked_naturalization` 的 mean silhouette vs no-N >= 0.84。
- `per_depth_masked_naturalization` 的 mean score > `per_depth_projection` mean score。
- `per_depth_masked_naturalization` 的 mean locality > `per_depth_global_naturalization` mean locality。

### 可直接运行命令

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
python3 assets/masked_naturalization_ablation_assets_20260510.py --seed 20260510 --depth-count 3 --resolution 56 --out-dir results/masked_naturalization_ablation_20260510_seed20260510
python3 assets/evaluate_masked_naturalization_ablation_20260510.py --asset-dir results/masked_naturalization_ablation_20260510_seed20260510 --out-dir results/masked_naturalization_ablation_20260510_seed20260510/evaluation_current
python3 assets/masked_naturalization_ablation_assets_20260510.py --seed 20260511 --depth-count 3 --resolution 56 --out-dir results/masked_naturalization_ablation_20260510_seed20260511
python3 assets/evaluate_masked_naturalization_ablation_20260510.py --asset-dir results/masked_naturalization_ablation_20260510_seed20260511 --out-dir results/masked_naturalization_ablation_20260510_seed20260511/evaluation_current
python3 assets/masked_naturalization_ablation_assets_20260510.py --seed 20260512 --depth-count 3 --resolution 56 --out-dir results/masked_naturalization_ablation_20260510_seed20260512
python3 assets/evaluate_masked_naturalization_ablation_20260510.py --asset-dir results/masked_naturalization_ablation_20260510_seed20260512 --out-dir results/masked_naturalization_ablation_20260510_seed20260512/evaluation_current
```

## M2: 六列可视化闭合矩阵

### 目标

让图和表完全对齐。当前 `visuals/masked_naturalization_ablation_zoom_20260510` 只有 3 tasks × 4 protocols，即 raw/final-only/per-depth/no-N/masked local-N。M2 要补齐 weak/global-N 的同相机 zoom，并生成完整 3 rows × 6 columns contact sheet。

### Exact inputs

Source meshes 使用当前主结果目录：

- `results/masked_naturalization_ablation_20260510/tasks/{task_id}/{variant}/mesh.obj`

Tasks：

- `botanical_root`
- `coral_frontier`
- `ifs_crystal`

Variants：

- `raw_grammar_proposal`
- `final_only_projection_repair`
- `per_depth_projection`
- `per_depth_weak_naturalization`
- `per_depth_global_naturalization`
- `per_depth_masked_naturalization`

优先补齐 currently missing：

- `per_depth_weak_naturalization`
- `per_depth_global_naturalization`

### 输出路径

建议新目录，避免覆盖现有 4-protocol zoom：

- `visuals/masked_naturalization_ablation_zoom_6protocol_20260510/`

每个 case 输出：

- `{task_id}__{variant}/overview_raw.png`
- `{task_id}__{variant}/overview_callouts.png`
- `{task_id}__{variant}/zoom_01.png`
- `{task_id}__{variant}/zoom_01_callouts.png`
- `{task_id}__{variant}/zoom_02.png`
- `{task_id}__{variant}/strict_matched_zoom_comparison.png`

汇总输出：

- `visuals/masked_naturalization_ablation_zoom_6protocol_20260510/matched_camera_zoom_plan.json`
- `visuals/masked_naturalization_ablation_zoom_6protocol_20260510/masked_naturalization_ablation_6protocol_contact_sheet_20260510.png`

本轮已导出 M2 manifest：

- `results/masked_naturalization_ablation_20260510/next_experiment_spec_hooke2_20260510/m2_visual_closure_manifest_20260510.csv`

### Metrics/QA 字段

M2 不是新增 mesh metric，而是 visual QA。建议每个 case 记录：

- `task_id`
- `variant`
- `overview_exists`
- `zoom_01_exists`
- `zoom_02_exists`
- `callout_exists`
- `white_background_ok`
- `square_resolution_ok`
- `camera_render_not_crop`
- `zoom_region_informative`
- `visual_boundary_note`

### Acceptance gate

- 18 个 cases 全部有 overview + two-level camera zoom。
- weak/global-N 的相机、白底、正方图和 masked local-N 对齐。
- contact sheet 中列顺序与 paper table 六列一致。
- 图注只写 local naturalization/control，不写 topology repair。
- 若 weak 或 global-N 视觉更平滑，必须用 caption 解释其 locality/control 边界。

## M3: 递归状态指标矩阵

### 目标

证明 masked local-N 没有破坏下一步 grammar-readable state。当前 evaluator 是 mesh-only，缺 handle/frontier/root attachment 指标；M3 不应硬塞进现有 mesh evaluator，而应通过 metadata/sidecar collector 补充。

### Exact inputs

优先在 M1 生成时记录 sidecar metadata。每个 `tasks/{task_id}/{variant}/metadata.json` 或独立 sidecar 中补：

- `root_id`
- `seed`
- `operator_family`
- `depth_count`
- `projection_thresholds`
- `naturalization_step_count`
- `mask_schedule`
- `root_source_provenance`
- per-depth active handle/frontier state

### 输出路径

建议新建：

- `results/masked_naturalization_ablation_20260510_handle_state_20260510/`

输出文件：

- `handle_state_metrics.csv`
- `handle_state_metrics.json`
- `handle_state_summary_by_protocol.csv`
- `handle_state_acceptance_report_zh_20260510.md`

本轮已导出 schema：

- `results/masked_naturalization_ablation_20260510/next_experiment_spec_hooke2_20260510/m3_handle_state_metric_schema_20260510.json`

### Metrics 字段

新增字段必须至少包括：

- `active_handle_count_before`
- `active_handle_count_after`
- `active_handle_survival_rate`
- `orphan_handle_count`
- `reachable_frontier_count`
- `frontier_reachability_rate`
- `root_attached_mass_ratio`
- `deleted_active_support_mass`
- `handle_drift_l2_mean`
- `mask_overlap_with_active_handles`

### Acceptance gate

- masked local-N 的 `active_handle_survival_rate` 不低于 no-N 均值的 95%。
- masked local-N 的 `frontier_reachability_rate` >= 0.95，或明确说明某任务是终端自然化、不需要继续递归。
- masked local-N 的 `orphan_handle_count` 不高于 no-N。
- global-N 若引起旧状态改写，应在 `handle_drift_l2_mean` 或 `root_attached_mass_ratio` 中可见。
- M3 只支持 “does not disrupt recursive state under tested settings”，不能支持 topology repair。

## 如果今天要最快补成主文级，先做哪一步

优先顺序：

1. 先做 M2 的 weak/global-N 可视化补齐。原因：当前数值表已经能区分 6 protocol，但主文图只覆盖 4 protocol；补齐 6-column visual closure 最快提升说服力，且不需要改 evaluator。
2. 同时或随后做 M1 的 3-seed 本地重跑。原因：这是从 single-root/single-seed 变成 mean/std 的最短路，现有脚本已有 `--seed` 和 `--out-dir`，可以直接落地。
3. M3 放在第二天或下一轮。原因：它需要新增 handle/frontier sidecar instrumentation；当前 mesh-only evaluator 无法直接给出这些字段，硬做会污染现有逻辑。

最短主文补强路径：

- 今日先补 M2 weak/global-N zoom。
- 跑 M1 三个 seed。
- 新增一个只读 aggregator，把三个 seed 的 `evaluation_current/metrics.csv` 合成 `meanstd` 表。
- 主文只写 “three local tasks, six protocols, three seeds/local roots where available”，并保留 claim boundary。

## 本轮新增规格脚本命令

生成 M1/M2/M3 规格文件：

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
python3 assets/export_masked_naturalization_next_experiment_spec_20260510.py \
  --eval-dir results/masked_naturalization_ablation_20260510/evaluation_current \
  --out-dir results/masked_naturalization_ablation_20260510/next_experiment_spec_hooke2_20260510
```

检查规格输出：

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
sed -n '1,20p' results/masked_naturalization_ablation_20260510/next_experiment_spec_hooke2_20260510/m1_minimal_replicate_manifest_20260510.csv
sed -n '1,24p' results/masked_naturalization_ablation_20260510/next_experiment_spec_hooke2_20260510/m2_visual_closure_manifest_20260510.csv
sed -n '1,80p' results/masked_naturalization_ablation_20260510/next_experiment_spec_hooke2_20260510/m3_handle_state_metric_schema_20260510.json
```
