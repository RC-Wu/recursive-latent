# Publication Ablation / Effective Resolution Closure Plan（Lane D, 2026-05-10）

本文档记录本地 Lane D 的 selected-final-only 盘点与 publication closure 草案。范围仅限本地聚合、CSV manifest、指标定义和表格草案；未启动远端任务，未 SSH，未修改 `paper_siga/main.tex`。

## 1. 输入与输出

### 输入

- `results/same_root_projection_matrix_20260510/same_root_projection_matrix.csv`
- `results/naturalization_projection_ablation_20260510/naturalization_projection_ablation.csv`
- `results/effective_resolution_metrics_20260510/effective_resolution_metrics.csv`
- selected Trellis2 texturing summaries:
  - `results/gapfill_texturing_selected_20260510/*/summary.json`
  - `results/gapfill_non_tree_texturing_selected_20260510/*/summary.json`

### 新增输出

- 脚本：`assets/publication_ablation_selected_final_aggregation_20260510.py`
- Manifest：`results/publication_ablation_metrics_20260510/manifest_selected_final_rows.csv`
- Coverage：`results/publication_ablation_metrics_20260510/matrix_coverage_summary.csv`
- Effective-resolution schema：`results/publication_ablation_metrics_20260510/effective_resolution_schema.csv`
- Summary：`results/publication_ablation_metrics_20260510/summary.json`
- Draft table：`paper_siga/drafts/publication_ablation_effective_resolution_status_20260510.tex`

脚本只读取显式列出的 CSV/JSON 和 selected final summaries，不递归扫描大目录，也不重新计算 mesh connectivity。

## 2. Same-root Matrix 盘点

当前 same-root manifest 共 127 行：63 available，64 missing。

| row | available | missing | local final mesh | local final GLB | 备注 |
|---|---:|---:|---:|---:|---|
| traditional | 30 | 8 | 29 | 0 | 多数来自本地 OBJ/proxy 或 baseline metrics；部分缺 component/LCR。 |
| direct | 8 | 8 | 2 | 0 | 6 行是远端 final mesh 路径加本地指标快照，需拉回 final mesh/GLB 后才能当本地 final asset。 |
| final-only | 4 | 12 | 2 | 0 | 目前只适合 matched subset 或 appendix status。 |
| prune | 5 | 11 | 2 | 0 | coral sparse_close 有指标但 final asset 仍是远端路径。 |
| bridge | 1 | 15 | 0 | 0 | 只有 coral sparse_close_bridge 指标快照；不能写成闭合正例。 |
| proposed | 15 | 10 | 15 | 0 | 本地 OBJ 较完整，但 GLB 不是 same-root matrix 的统一本地产物。 |

结论：same-root matrix 仍是 partial。可用于主文的只应是同 root、同 depth、同 renderer、local final asset 可检查的 matched subset；完整矩阵应放 appendix/status。

## 3. Naturalization Matrix 盘点

当前 naturalization manifest 共 230 行：98 available，132 missing。

| row | available | missing | local final mesh | local final GLB | 备注 |
|---|---:|---:|---:|---:|---|
| rule-only | 4 | 22 | 0 | 1 | L-system selected textured GLB 已本地存在；大多数 case 缺同根 row。 |
| no-N | 8 | 18 | 0 | 1 | alpha=0 masked-executor control；可做 status/gap-fill，不是完整 no-naturalizer 协议。 |
| weak blend | 8 | 18 | 0 | 3 | L-system/coral/pyrite selected GLB 已本地存在；仍缺完整同根矩阵。 |
| masked local-N | 22 | 13 | 14 | 3 | selected GLB 覆盖 L-system/coral/pyrite；local-N claim 仍需 anchor/mask leakage 与 topology 指标闭合。 |
| global-N | 12 | 22 | 0 | 0 | Flow/SDE diagnostic rows；多为 negative 或 near-LCR-fragmented，不是正面 topology repair。 |
| with projection | 35 | 17 | 29 | 0 | projection 轴 evidence 较多，但和 naturalization 轴必须分开解释。 |
| without projection | 4 | 22 | 2 | 0 | 缺口最大之一，不足以支撑完整消融。 |
| post-hoc repair baseline | 5 | 0 | 5 | 0 | 单独列为 mesh repair baseline，不可混为 recursive projection。 |

结论：naturalization matrix 已有 selected final GLB 可做视觉 appendix/status，但不能删除 `EvidencePending`。主文 claim 应限于“selected meshes can enter texture/export path”和“masked local-N 是局部自然化候选”，不能写成稳定 topology repair。

## 4. Effective-resolution / Zoom-retention 指标定义

这些指标是 publication closure 的 proxy schema，不替代 matched zoom render 和人工 QA。

| 指标 | 定义 | 越大/越小 | 用途 |
|---|---|---|---|
| `local_feature_scale` | `bbox_diag / sqrt(face_count)` | 越小越细 | 估计整体尺度归一化后可表达的局部三角面尺度。 |
| `terminal_detail_count` | 优先 terminal occupied voxels / surface voxels / tokens；缺失时 fallback 到 vertices/faces | 越大越细节丰富 | 衡量终端深度仍保留多少可寻址局部细节。 |
| `zoom_retention` | `connectivity_lcr * (1 + box_count_dimension_proxy / 3)` | 越大越好 | 粗略估计 zoom 后结构是否既连通又有空间复杂度。 |
| `face_count` | final selected asset 的 triangle count | 诊断项 | 和文件大小、局部尺度一起解释，不单独作为质量指标。 |
| `glb_size_mb` | 本地 selected GLB 文件大小 | 诊断项 | 资产预算/导出代价。 |
| `full_object_highres_blowup_estimate_faces` | comparison row 中使用 one-shot faces 按 local-feature-scale improvement 的平方放大，并以下限 recursive faces 截断 | 越大表示 one-shot 全物体同等局部尺度代价越高 | 支持 effective-resolution 叙事的保守估计。 |

CSV schema 草案已写入 `results/publication_ablation_metrics_20260510/effective_resolution_schema.csv`。当前 effective-resolution manifest 有 32 行 method_metric，全部有本地 final GLB 和基础 proxy 指标；comparison 仍应沿用 `results/effective_resolution_metrics_20260510/effective_resolution_comparisons.csv`。

## 5. Claim Gate

Manifest 中 `claim_gate` 的解释：

- `appendix_missing_or_gap`：required row 缺失，或只应作为缺口显式化。
- `metrics_snapshot_needs_local_final_asset`：有指标但 final mesh/GLB 仍是远端路径或本地不可解析。
- `asset_or_status_only_needs_metrics`：有资产/status，但关键指标为空。
- `appendix_diagnostic`：可作为 failure/boundary/negative 诊断。
- `appendix_candidate_claim_gated`：本地 final asset 与部分指标存在，但仍需 matched visual QA 或更严格指标后才能进主文。

当前没有把任何 row 自动标成主文强 claim。主文 promotion 需要人工检查：local final asset、matched camera/renderer、connectivity/root/mask 指标和 zoom panel。

## 6. 下一步最小闭环

1. 从主 agent 处接收或拉齐 same-root 远端 final meshes/GLB 的本地产物，再重跑 selected-final-only aggregation。
2. 对 `lsystem_branch/fork_side` 的 rule-only/no-N/weak/masked-local selected GLB 做同相机 render + local zoom QA。
3. 对 coral/pyrite weak vs masked-local 增加 occupancy/root/mask leakage 指标；否则只放 appendix diagnostic。
4. effective-resolution 只在有 matched zoom render 后进入主文；当前 proxy 可放 method/appendix table。
