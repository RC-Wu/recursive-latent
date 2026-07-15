# Masked Naturalization Ablation 本地结果包 2026-05-10

## 已生成结果与用途

- 资产目录：`results/masked_naturalization_ablation_20260510`
- 资产清单：`manifest.csv` / `manifest.json`
- 白底 zoom 渲染清单：`render_manifest_pure_white_zoom.json`
- 当前指标目录：`results/masked_naturalization_ablation_20260510/evaluation_current`
- dry-run 指标目录：`results/masked_naturalization_ablation_20260510/evaluation_dryrun`
- 论文短表 CSV：`results/masked_naturalization_ablation_20260510/evaluation_current/paper_table_masked_naturalization_ablation_20260510.csv`
- 论文短表 LaTeX：`results/masked_naturalization_ablation_20260510/evaluation_current/paper_table_masked_naturalization_ablation_20260510.tex`
- 六列均值汇总：`results/masked_naturalization_ablation_20260510/evaluation_current/protocol_summary_masked_naturalization_ablation_20260510.csv`
- masked-local 相对负控 delta：`results/masked_naturalization_ablation_20260510/evaluation_current/masked_local_advantage_20260510.csv`
- 中文结果摘要：`results/masked_naturalization_ablation_20260510/evaluation_current/masked_naturalization_ablation_summary_zh_20260510.md`
- 渲染 plan-only 校验：`visuals/masked_naturalization_ablation_zoom_plan_20260510/matched_camera_zoom_plan.json`

## 六列同根消融协议

三类代表任务：

| task | family |
|---|---|
| `botanical_root` | botanical/root |
| `coral_frontier` | coral/frontier |
| `ifs_crystal` | IFS/crystal |

六个变体：

| variant | 含义 |
|---|---|
| `raw_grammar_proposal` | rule-only：原始 grammar proposal，不做 projection / naturalization |
| `final_only_projection_repair` | final-only：只在最终深度做 projection/repair |
| `per_depth_projection` | per-depth/no-N：每层 projection 后再进入下一层，不做 naturalization |
| `per_depth_weak_naturalization` | per-depth/weak：每层 projection + 弱 masked blend |
| `per_depth_global_naturalization` | per-depth/global-N：每层 projection + 全局 field smoothing，作为 locality 负控 |
| `per_depth_masked_naturalization` | per-depth/masked local-N：每层 projection + 仅当前 edit mask 自然化，旧状态 hard clamp |

## 当前指标结论

| task | recommended variant | score | LCR | locality | silhouette vs per-depth | local normal variation |
|---|---|---:|---:|---:|---:|
| `botanical_root` | `per_depth_masked_naturalization` | 0.875703 | 1.000000 | 0.923912 | 0.913689 | 11.000726 |
| `coral_frontier` | `per_depth_masked_naturalization` | 0.869856 | 1.000000 | 0.925879 | 0.904730 | 11.741637 |
| `ifs_crystal` | `per_depth_masked_naturalization` | 0.885595 | 1.000000 | 0.940559 | 0.925961 | 11.087061 |

主文建议只写保守 claim：masked local-N 在 per-depth projection 已经稳定递归状态的前提下，提升局部表面连续性并保持较高 locality/silhouette；不要把它写成全局拓扑修复器。`global-N` 有时会进一步降低 normal variation，但会显著降低 locality/preservation，因此应作为负控而不是正例。

## 指标与短表字段

| 字段 | 用途 |
|---|---|
| connectivity | LCR 与碎片惩罚，衡量能否作为递归状态继续使用 |
| locality | 相对 per-depth/no-N 的 silhouette、bbox extent 与自然化范围约束；专门惩罚全局改写 |
| roughness_deg | edit-mask 附近相邻三角面 normal variation 均值，越低越平滑 |
| silhouette | 多视角容差膨胀 2D occupancy IoU，相对 per-depth/no-N |
| mesh_quality | triangle aspect ratio 与退化面比例 proxy |
| blockiness | 轴向法线集中度 + 碎片惩罚，越高越 blocky |
| score | connectivity、locality、roughness、silhouette、mesh quality、blockiness、efficiency、projection schedule、masked scope 的联合分数 |

## 交付给主线程的文件

- `assets/masked_naturalization_ablation_assets_20260510.py`
- `assets/evaluate_masked_naturalization_ablation_20260510.py`
- `tests/test_masked_naturalization_ablation_20260510.py`
- `docs/evaluation/masked_naturalization_ablation_results_plan_zh_20260510.md`
- `results/masked_naturalization_ablation_20260510/manifest.csv`
- `results/masked_naturalization_ablation_20260510/manifest.json`
- `results/masked_naturalization_ablation_20260510/evaluation_current/metrics.csv`
- `results/masked_naturalization_ablation_20260510/evaluation_current/metrics.json`
- `results/masked_naturalization_ablation_20260510/evaluation_current/paper_table_masked_naturalization_ablation_20260510.csv`
- `results/masked_naturalization_ablation_20260510/evaluation_current/paper_table_masked_naturalization_ablation_20260510.tex`
- `results/masked_naturalization_ablation_20260510/evaluation_current/protocol_summary_masked_naturalization_ablation_20260510.csv`
- `results/masked_naturalization_ablation_20260510/evaluation_current/masked_local_advantage_20260510.csv`
- `results/masked_naturalization_ablation_20260510/evaluation_current/masked_naturalization_ablation_summary_zh_20260510.md`

## 验证记录

- `python3 -m pytest tests/test_masked_naturalization_ablation_20260510.py -q`：2 passed
- `python3 assets/masked_naturalization_ablation_assets_20260510.py --out-dir results/masked_naturalization_ablation_20260510 --resolution 56 --depth-count 3 --seed 20260510`：生成 3 tasks × 6 variants = 18 OBJ mesh assets
- `python3 assets/evaluate_masked_naturalization_ablation_20260510.py --asset-dir results/masked_naturalization_ablation_20260510 --out-dir results/masked_naturalization_ablation_20260510/evaluation_current`：生成 18 行 metrics、3 行推荐、论文 CSV/TEX、六列均值汇总、masked-local delta、中文结果摘要
- `python3 assets/evaluate_masked_naturalization_ablation_20260510.py --asset-dir results/masked_naturalization_ablation_20260510 --out-dir results/masked_naturalization_ablation_20260510/evaluation_dryrun --dry-run`：生成 18 行 dry-run metrics 与 3 行推荐
- `python3 scripts/figures/matched_camera_zoom_render_20260510.py --manifest results/masked_naturalization_ablation_20260510/render_manifest_pure_white_zoom.json --out-dir visuals/masked_naturalization_ablation_zoom_plan_20260510 --resolution 512 --zoom-levels 2 --material-mode neutral --plan-only`：白底 zoom plan 生成成功，18 cases
