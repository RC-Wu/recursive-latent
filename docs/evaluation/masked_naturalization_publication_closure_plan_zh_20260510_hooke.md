# Masked Local Naturalization 发表级闭合计划 Hooke 2026-05-10

## 任务边界

本文件只服务 masked local naturalization 指标/消融线。遵守当前计划中的口径：masked naturalization 是局部 surface/material realization operator，不能写成 global topology repair；connectivity 结论必须绑定 per-depth projection；不修改 `paper_siga/main.tex`。

本轮新增了一个无冲突导出脚本：

- `assets/export_masked_naturalization_publication_summary_20260510.py`

该脚本只读取现有 `evaluation_current` CSV，不改已有 evaluator，不启动远端任务，并导出 paper-ready summary 到：

- `results/masked_naturalization_ablation_20260510/evaluation_current/publication_summary_hooke_20260510/`

## 已完成证据

### 1. 六列协议已闭合

当前 `results/masked_naturalization_ablation_20260510/evaluation_current` 覆盖 3 个任务乘 6 个 protocol，共 18 行：

- `rule-only`
- `final-only`
- `per-depth/no-N`
- `per-depth/weak`
- `per-depth/global-N`
- `per-depth/masked local-N`

任务为：

- `botanical_root`
- `coral_frontier`
- `ifs_crystal`

### 2. 区分度指标已可用

可用于发表级窄结论的指标包括：

- connectivity / surface LCR：区分 raw/final-only/per-depth 是否保留可复用 connected support。
- locality：区分 masked local-N 与 global-N，后者会改写旧状态。
- roughness/local normal variation：区分是否提升局部表面连续性。
- silhouette vs per-depth/no-N：防止以全局形变换平滑。
- mesh quality / blockiness：辅助证明不是靠退化面、碎片或轴对齐块状几何获得分数。
- compact score：用于排序 protocol，但必须公开其 composite 性质和边界。

当前 protocol 均值显示区分度明确：

| protocol | mean score | mean connectivity | mean locality | mean roughness | recommended tasks |
|---|---:|---:|---:|---:|---:|
| rule-only | 0.4414 | 0.1687 | 0.8257 | 38.64 | 0 |
| final-only | 0.7519 | 0.8007 | 0.9925 | 13.77 | 0 |
| per-depth/no-N | 0.7854 | 0.8342 | 1.0000 | 13.82 | 0 |
| per-depth/weak | 0.8462 | 1.0000 | 0.9278 | 11.68 | 0 |
| per-depth/global-N | 0.8180 | 1.0000 | 0.8425 | 10.83 | 0 |
| per-depth/masked local-N | 0.8771 | 1.0000 | 0.9301 | 11.28 | 3 |

### 3. Paper-ready 导出已完成

新增导出包含：

- compact summary：3 行主文摘要表。
- contrast summary：每个任务的 masked-vs-no-N / masked-vs-global-N / masked-vs-weak 对比。
- protocol discrimination：6 protocol 均值区分表。
- compact TEX：可直接进入论文草稿或 supplement。
- claim boundary JSON：列出支持和不支持的 claim。

核心 compact summary：

| task | score | LCR | locality | roughness | silhouette | score gain vs no-N |
|---|---:|---:|---:|---:|---:|---:|
| botanical_root | 0.8757 | 1.0000 | 0.9239 | 11.00 | 0.9137 | 0.0822 |
| coral_frontier | 0.8699 | 1.0000 | 0.9259 | 11.74 | 0.9047 | 0.0718 |
| ifs_crystal | 0.8856 | 1.0000 | 0.9406 | 11.09 | 0.9260 | 0.1211 |

## 目前可以写入论文的结论

可以写：

- 在三个 matched tasks 中，`per-depth/masked local-N` 是 joint score 推荐行。
- masked local-N 在 per-depth projection 下保持 surface LCR = 1.0。
- 相对 per-depth/no-N，masked local-N 的 score 提升为 0.0718 到 0.1211，并降低局部 normal variation 2.02 到 3.22 度。
- 相对 global-N，masked local-N 保持更高 locality，说明不是单纯全局 smoothing。
- 该结果支持局部 surface-continuity / material-realization 口径。

必须保守：

- 不写 global topology repair。
- 不写 naturalization 单独保证 connectivity。
- 不写 watertight topology / clean manifold。
- 不写 category-wide robustness。
- 不写物理 DLA/coral/crystal 生长。
- 不把 composite score 当唯一证据；应搭配 LCR、locality、roughness、silhouette 拆解列。

## 缺口

### A. 发表级统计缺口

当前只有 3 个任务、每任务一个 root/seed 组合，且 metadata 中 `depth`, `seed`, `root_id` 为空。因此不能报告 mean/std robust claim。

需要补：

- 每个任务至少 3 seeds 或 3 roots。
- 每行 metadata 填 root/source provenance、seed、depth、operator family。
- naturalization schedule：mask 规则、step count、alpha、global/weak/masked 设置。
- projection thresholds：连接半径、组件过滤阈值、active support 保留策略。

### B. 可视化缺口

现有 `visuals/masked_naturalization_ablation_zoom_20260510` 覆盖 12 case，即 3 tasks × 4 protocols：

- raw
- final-only
- per-depth/no-N
- masked local-N

缺少：

- per-depth/weak 的同 camera zoom。
- per-depth/global-N 的同 camera zoom。
- mask overlay / before-after edit-region overlay。

因此图可以支持 raw/no-N/masked 的局部视觉差异，但不能完整视觉证明 masked local-N 优于 weak/global-N。weak/global-N 目前主要靠表格和数值。

### C. 指标缺口

还缺以下发表级指标：

- handle-level recursive state：active handle survival、orphan handle count、reachable frontier count。
- root attachment：path-to-root rate、root-attached mass。
- edit-mask 局部几何：mask 内 Chamfer、normal consistency、surface displacement。
- topology caveat：non-manifold edges、boundary edges、self-intersection proxy、watertightness flag。
- runtime/memory：masked local-N 相对 no-N/weak/global-N 的开销。
- score sensitivity：改变 score 权重后推荐行是否稳定。

## 新增实验矩阵建议

### Matrix M1: 最小发表级重复

目标：把当前 3 tasks × 6 protocols 从单例变成最小 mean/std。

矩阵：

- tasks：`botanical_root`, `coral_frontier`, `ifs_crystal`
- roots/seeds：每 task 3 个 seeds 或 3 个 root variants
- protocols：6 个现有 protocol
- 总行数：3 × 3 × 6 = 54

输出：

- `metrics.csv/json`
- `protocol_summary_meanstd.csv`
- `score_recommendation_stability.csv`
- `metadata_completeness.json`

验收：

- masked local-N 在每个 task 至少 2/3 seeds 中仍为推荐行，或明确记录 failure boundary。
- 每个 task 报 mean/std，不再只报单值。

### Matrix M2: 可视化闭合

目标：让 6 protocol 图和 6 protocol 表完全对齐。

矩阵：

- 对当前 3 tasks 的 weak/global-N 补同 camera zoom。
- 每行输出 overview、zoom_01、zoom_02、callouts、strict comparison。
- 生成一张 3 rows × 6 columns 的 contact sheet，弱化 gallery 感，强调 protocol。

验收：

- 每列 protocol 名与表格一致。
- caption 明确 weak/global-N 是 controls。
- 不把 global-N 的平滑外观解释成拓扑修复。

### Matrix M3: 递归状态指标

目标：证明 masked local-N 没有破坏下一步 grammar-readable state。

矩阵：

- 在 M1 的每行增加 active handles/frontiers/cache metadata。
- 指标：active handle survival、orphan handle count、frontier reachability、deleted active support mass。

验收：

- masked local-N 相比 no-N 不显著降低 reachable frontier/handle survival。
- global-N 若改变旧状态，应在 locality 和 handle drift 中体现。

## 新增导出文件说明

本轮新增目录：

- `results/masked_naturalization_ablation_20260510/evaluation_current/publication_summary_hooke_20260510/`

文件：

- `manifest.json`：导出清单。
- `masked_local_n_publication_compact_summary_20260510.csv`：3 行主文摘要。
- `masked_local_n_publication_compact_summary_20260510.tex`：compact LaTeX 表。
- `masked_local_n_publication_contrast_summary_20260510.csv`：9 行对比表。
- `masked_local_n_protocol_discrimination_20260510.csv`：6 protocol 均值表。
- `masked_local_n_claim_boundaries_20260510.json`：可写/不可写 claim 边界。

## 下一步具体命令

复跑现有 evaluator：

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
python3 assets/evaluate_masked_naturalization_ablation_20260510.py \
  --asset-dir results/masked_naturalization_ablation_20260510 \
  --out-dir results/masked_naturalization_ablation_20260510/evaluation_current
```

复跑本轮 publication summary 导出：

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
python3 assets/export_masked_naturalization_publication_summary_20260510.py \
  --eval-dir results/masked_naturalization_ablation_20260510/evaluation_current \
  --out-dir results/masked_naturalization_ablation_20260510/evaluation_current/publication_summary_hooke_20260510
```

复查导出：

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
sed -n '1,20p' results/masked_naturalization_ablation_20260510/evaluation_current/publication_summary_hooke_20260510/masked_local_n_publication_compact_summary_20260510.csv
sed -n '1,40p' results/masked_naturalization_ablation_20260510/evaluation_current/publication_summary_hooke_20260510/masked_local_n_claim_boundaries_20260510.json
```

## 当前状态判定

Masked local naturalization 线已经达到“可写窄主文结果”的最低门槛：有 6 protocol 表、区分度指标、compact summary 和 claim boundary。它尚未达到“强发表级稳健结论”的门槛：缺 seed/root mean/std、弱/全局自然化视觉闭合、handle-level state 指标和 score sensitivity。

建议主文只写窄结论，把完整 18 行表和 protocol discrimination 放 supplement；下一批优先跑 M1 和 M2，而不是继续扩大无统计的单例 gallery。
