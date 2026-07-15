# Ablation / Metric Protocol 20260510

本文档对应 Lane B：ablation/metric implementation。范围只覆盖本地已有 CSV/JSON/mesh 输出的聚合与缺口显式化，不修改 `paper_siga/main.tex`。

## 输出脚本

新增三个聚合脚本：

| 目标 | 脚本 | 默认输出 |
|---|---|---|
| same-root projection matrix | `assets/same_root_projection_matrix_20260510.py` | `results/same_root_projection_matrix_20260510/same_root_projection_matrix.csv` |
| naturalization / projection ablation | `assets/naturalization_projection_ablation_aggregation_20260510.py` | `results/naturalization_projection_ablation_20260510/naturalization_projection_ablation.csv` |
| one-shot vs recursive effective-resolution | `assets/effective_resolution_metrics_20260510.py` | `results/effective_resolution_metrics_20260510/effective_resolution_metrics.csv` |

所有脚本都是 aggregator，不启动远端任务、不跑 Trellis2、不重渲染。若输入缺失或某个 required variant 没有本地证据，脚本写出 `status=missing` 的显式行，而不是失败退出。

## 运行命令

```bash
python3 assets/same_root_projection_matrix_20260510.py
python3 assets/naturalization_projection_ablation_aggregation_20260510.py
python3 assets/effective_resolution_metrics_20260510.py
```

测试：

```bash
python3 -m pytest -q tests/test_ablation_aggregators_20260510.py
```

## Same-root Projection Matrix

固定 variant：

| variant | 含义 | 证据来源优先级 |
|---|---|---|
| `traditional` | 传统程序化 root / same-depth baseline | `strict_matched_baseline_matrix_20260510_seed310_depth5`, `baseline_matrix_seed_20260510`, `baseline_matrix_20260509`, strict proxy manifest |
| `direct` | no projection / raw recursion | `projection_matrix_gap_closure_20260509`, projection variant final summaries |
| `final-only` | 只在最终层 projection / cleanup | `projection_matrix_gap_closure_20260509` |
| `prune` | per-depth prune / sparse close | projection gap closure and projection-variant summaries |
| `bridge` | model bridge / sparse close bridge / mesh bridge | projection gap closure and projection-variant summaries |
| `proposed` | PS-RSLG / proposed connected recursive state | baseline matrix proposed rows and strict proxy manifest |

关键列：

- `root_source`：源表明确给出 root anchor 时使用源表；否则标为 same local root if source row reports it。
- `grammar_operator`：原始 `grammar` / `method` / `operators` / `variant`。
- `component_count`, `largest_component_ratio`：优先使用源表已有 mesh/face/occupancy component 指标。
- `root_reachability`, `orphan_tip_ratio`, `attachment_success`：若源表有 `root_component_ratio`, `path_to_root_rate`, `orphan_mass_ratio` 则填入；否则保留空。
- `missing_reason`：说明某 case 缺哪一类 required variant。

解释原则：不同来源不是完全同一实验协议时，CSV 只作为 evidence inventory 和 matrix closure，不直接作为主文最终数值表。主文只应使用 same-root/same-depth/same-render QA 通过的子集。

## Naturalization / Projection Ablation

固定 variant：

| variant | 含义 |
|---|---|
| `rule-only` | 只有规则/程序 scaffold，不做 learned naturalization |
| `no-N` | 显式关闭 naturalizer |
| `weak blend` | 弱 masked/feature blend |
| `masked local-N` | frontier/local masked naturalization |
| `global-N` | global flow/SDE repair/naturalization |
| `with projection` | projection axis 单独开启 |
| `without projection` | projection axis 单独关闭 |
| `post-hoc repair baseline` | 如果使用传统 mesh repair，必须单独标注，不可混为 projection |

关键约束：

- `naturalization_role` 和 `projection_role` 必须分开读。
- `post-hoc repair baseline` 的 `projection_role` 固定为 `post_hoc_mesh_repair_not_projection`。
- `global-N` 目前主要来自 `flow_sde_naturalization_metrics_20260510_0008`；其负例/near-lcr-fragmented 结论不能写成 projection 证据。
- `masked local-N` 可来自 strict proxy / strict visual manifest，但仍需同 root/depth 的强对照才能进入主文。

## Effective-resolution Metrics

脚本输出两类行：

| row_type | 内容 |
|---|---|
| `method_metric` | 单个 one-shot 或 recursive 输出的局部尺度、detail、zoom retention proxy |
| `comparison` | 每个 case group 中 best one-shot 与 best recursive 的对比 |

当前 proxy 定义：

- `local_feature_scale_proxy = bbox_diag / sqrt(face_count)`。数值越小，表示单位整体尺度下可表达的局部三角面尺度越细。
- `terminal_detail_count_proxy` 优先用 `occupied_voxels` / surface occupied voxels；缺失时才退化为 vertices/faces。
- `zoom_retention_score = connectivity_lcr * (1 + box_count_dimension_proxy / 3)`。这是筛选 proxy，不是视觉 zoom panel 的替代品。
- `estimated_full_object_highres_faces` 使用 one-shot faces 按 local feature scale improvement 的平方放大，并以下限 `recursive_faces` 截断。它只是 full-object 高分辨率代价的保守 proxy。

主文使用限制：

1. 指标可以支持“recursive local detail retention / effective resolution”方向，但最终仍需 matched zoom render。
2. `box_count_dimension_proxy` 是 occupancy proxy，不应写成严格 fractal dimension。
3. GLB size 只在本地路径存在时填入；远端 `/mnt/beegfs/...` 路径不会假造大小。

## 当前数据缺口

- Same-root projection matrix 仍有多个 case 缺 `traditional` / `final-only` / `bridge` / `proposed` 的严格同根同深 row。
- Naturalization matrix 中 `rule-only`, `no-N`, `weak blend` 多数仍是 missing row，需要同 root/depth 的新实验证据。
- `masked local-N` 已能从 strict visual/proxy manifest 聚合，但不是全部 case 都有同一协议下的 negative/positive pair。
- Effective-resolution 已有 tree/vine 与 crystal/coral 两个 group 的 comparison proxy，但还缺 paper-grade nested zoom render 与人工 QA 标注。
