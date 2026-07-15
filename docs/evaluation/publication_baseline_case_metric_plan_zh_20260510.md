# Publication baseline case pool + metrics 状态计划（2026-05-10）

本文件对应本地 Lane B。范围只使用本地现有文件，不 SSH，不触碰 `paper_siga/main.tex`。

## 1. 本轮产物

- 聚合入口：`assets/publication_baseline_metrics_20260510.py`
- 输出目录：`results/publication_baseline_metrics_20260510/`
- master manifest：`results/publication_baseline_metrics_20260510/publication_baseline_master_manifest_20260510.csv`
- case pool CSV：`results/publication_baseline_metrics_20260510/publication_case_pool_candidates_20260510.csv`
- LaTeX 草案表：`results/publication_baseline_metrics_20260510/publication_baseline_table_draft_20260510.tex`
- 运行摘要：`results/publication_baseline_metrics_20260510/summary.json`

脚本是 selected-final-only aggregator：默认只读现有 `gen3d_baseline_summary_table_20260510.csv` 和整理好的 case selection symlink；若 Lane A 后续拉回 TRELLIS/Hunyuan 结果，用 `--input-manifest` 追加显式行。脚本不递归扫描 `results/` 或 `visuals/` 大目录。

## 2. Case pool 汇总

已汇总 `visuals/case_selection_by_type_20260510/` 下的本地候选，共 70 行，其中 67 个可用候选 + 3 个显式缺口行。

| 类别 | 可用候选数 | 是否达到每类 10 个 | 备注 |
| --- | ---: | --- | --- |
| `plant_root_tree` | 12 | 是 | root / vine / pine canopy / tree crown 足够，主文优先用 001、002、005、007、009 |
| `crystal_coral_dla` | 11 | 是 | bismuth / pyrite / coral / DLA 足够，是 ours 优势最强类别 |
| `gen3d_baselines` | 12 | 是 | 已有 ours、Trellis2 one-shot、latent-copy、mesh-space 对照 |
| `ablation_depth` | 13 | 是 | projection ablation 与 depth progression 充足 |
| `sci_fi_mechanical` | 7 | 缺 3 | 可作为 appendix diversity，暂不建议主文核心 baseline |
| `hero_zoom` | 5 | 缺 5 | 这是组合/zoom 来源，不是独立类别池 |
| `needs_repair_or_discard` | 7 | 缺 3 | failure/boundary 池，缺口记录即可，不建议补成主文正例 |

推荐展示子集：

1. Pyrite lattice：`crystal_coral_dla/002` 或 `005`，baseline 行使用 Trellis2 one-shot、latent-copy、mesh-space、ours。
2. Coral/frontier：`crystal_coral_dla/003` 或 `006`，baseline 行使用 Trellis2 one-shot、latent-copy、ours；mesh-space coral 当前 missing，保留显式缺口。
3. Vine/root：视觉用 `plant_root_tree/002` 或 `003` 的 stronger vine stage5；strict baseline 表中保留 weak strict vine row 并标为 `needs_vine_candidate_swap_or_QA`。
4. Bismuth：`crystal_coral_dla/001` 或 `004` 适合 qualitative/hero，但当前 baseline numeric matrix 还没有完整一对一 rows。
5. Mechanical/radial gear：`sci_fi_mechanical/001`、`004`、`006` 只建议 appendix diversity，不作为主 claim。

## 3. Master manifest 状态

`publication_baseline_master_manifest_20260510.csv` 当前 25 行：

- `success`: 4
- `fragmented`: 5
- `fragmented_copy_paste`: 2
- `needs_vine_candidate_swap_or_QA`: 1
- `blocked`: 9
- `missing`: 4

已包含的本地证据：

- Trellis2 one-shot：vine / pyrite / coral。
- Trellis2 trivial latent-copy：vine / pyrite / coral。
- Mesh-space generated-root：vine / pyrite；coral 明确 missing。
- Ours / PS-RSLG：pyrite / coral strict rows；vine strict weak row；stronger vine stage5 reference。
- TRELLIS non-2：vine / pyrite / coral 三行 blocked slot。
- Hunyuan image / Hunyuan image+texture：vine / pyrite / coral blocked slot。
- Hunyuan mesh-space generated-root：vine / pyrite / coral missing slot，等待 Hunyuan root mesh。

注意：Trellis2 vine one-shot 的 occupancy LCR 为 1.0，但这只说明该几何的 occupancy 连通 proxy 强，不等于通过递归结构任务。主文若使用 vine，必须结合 junction/tip survival、zoom panel 和人工 QA。

## 4. 指标口径

master manifest 统一列：

- mesh/asset：`vertices`、`faces`、`file_size_mb`
- 连通性：`raw_component_count`、`welded_component_count`、`occupancy_component_count_6n`、`largest_occupancy_component_ratio_6n`、`LCR`
- 递归/结构占位：`root_reachability`、`orphan_fragment_ratio`
- 可用性：`render_import_success`、`visual_qa_status`、`failure_label`
- 缺口：`status`、`missing_reason`、`remote_drop_expected`

现有 gen3d summary 已提供主要 rows 的 vertices/faces/file size/raw components/occupancy components/LCR。新增脚本也能对 `--input-manifest` 中显式列出的 mesh/GLB/OBJ 调用 `assets/recursive_growth_mesh_metrics.py` 的 `metric_one()` 补算指标；不做目录递归。

## 5. 如何接 Lane A 远端结果

Lane A 拉回 TRELLIS non-2 或 Hunyuan 输出后，新增一个小 CSV，例如：

```csv
case,method,variant,status,asset_path,source_path,render_path,manifest_path,notes
pyrite,Hunyuan3D 2.0 image one-shot,seed001,success,results/pulled_hunyuan/pyrite/final.glb,results/pulled_hunyuan/pyrite/final.obj,visuals/pulled_hunyuan/pyrite/overview.png,results/pulled_hunyuan/pyrite/manifest.json,pulled by Lane A
```

然后运行：

```bash
python3 assets/publication_baseline_metrics_20260510.py \
  --input-manifest results/publication_baseline_metrics_20260510/lane_a_drop_manifest.csv \
  --out results/publication_baseline_metrics_20260510
```

要求：

- 每个远端 row 必须是 final selected artifact，不要给一个目录。
- `asset_path` 优先填 GLB；若 GLB metrics 导入失败，可同时填 `source_path` 指向 OBJ。
- blocked row 不删除，等成功 row 到达后由主 agent 决定主文表使用成功 row 还是保留 blocked history。
- Hunyuan mesh-space generated-root 需要 Hunyuan root mesh 先到本地，再由 mesh-space baseline 脚本生成 local copy/merge row。

## 6. 主文 claim gate

当前最稳主文 baseline 对比是：

- Pyrite：Trellis2 one-shot fragmented、latent-copy fragmented、mesh-space copy-paste fragmented，ours LCR=1.0。
- Coral：Trellis2 one-shot fragmented、latent-copy fragmented，ours LCR=1.0；mesh-space coral missing，不能静默省略。
- Vine/root：使用 stronger vine stage5 作为正向视觉候选；strict matched vine row 暂不支持强 claim。

可以写：

- 普通 one-shot 和 naive latent/mesh recursion 不能稳定替代 grammar-owned recursive state。
- 对 pyrite/coral，本地已有数值和渲染证据支持 PS-RSLG 更稳定地保持 occupancy-connected recursive support。

不能写：

- Hunyuan 或 TRELLIS non-2 已完成并失败。
- 所有 3D generator 都失败。
- Vine strict row 已经完全通过 recursive structure QA。
- Raw face component count 单独证明拓扑失败；它只作为诊断，主口径仍是 occupancy 6N + visual QA + root/tip/junction 指标。
