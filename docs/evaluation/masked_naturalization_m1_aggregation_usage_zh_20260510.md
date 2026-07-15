# Masked Local Naturalization M1 聚合脚本说明 2026-05-10

脚本：

- `assets/aggregate_masked_naturalization_m1_20260510.py`

用途：

- 只读取三个 seed 的 `evaluation_current/metrics.csv`。
- 不修改 `assets/evaluate_masked_naturalization_ablation_20260510.py`。
- 不修改 `paper_siga/main.tex`。
- 输出 M1 mean/std、masked local win rate、masked-vs-baseline deltas 和 acceptance gates。

默认输入：

- `results/masked_naturalization_ablation_20260510_seed20260510/evaluation_current/metrics.csv`
- `results/masked_naturalization_ablation_20260510_seed20260511/evaluation_current/metrics.csv`
- `results/masked_naturalization_ablation_20260510_seed20260512/evaluation_current/metrics.csv`

默认输出目录：

- `results/masked_naturalization_ablation_m1_20260510/`

正式运行命令：

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
python3 assets/aggregate_masked_naturalization_m1_20260510.py
```

输出文件：

- `results/masked_naturalization_ablation_m1_20260510/m1_protocol_meanstd.csv`
- `results/masked_naturalization_ablation_m1_20260510/m1_task_recommendation_stability.csv`
- `results/masked_naturalization_ablation_m1_20260510/m1_publication_summary.md`
- `results/masked_naturalization_ablation_m1_20260510/m1_publication_summary.json`

本地 smoke test 可用同一个现有单 seed metrics 重复三次，只检查输出形状，不作为正式结论：

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
python3 assets/aggregate_masked_naturalization_m1_20260510.py \
  --metrics \
  results/masked_naturalization_ablation_20260510/evaluation_current/metrics.csv \
  results/masked_naturalization_ablation_20260510/evaluation_current/metrics.csv \
  results/masked_naturalization_ablation_20260510/evaluation_current/metrics.csv \
  --out-dir /tmp/masked_naturalization_m1_smoke
```

Acceptance gates：

- 三个 seed 输入均存在。
- observed rows 等于 `3 tasks × observed seeds × 6 protocols`。
- 每个 task 中 masked local 至少 2/3 seeds 为最高 `main_text_score`。
- masked local mean surface LCR >= 0.98。
- masked local mean silhouette vs no-N >= 0.84。
- masked local mean score > no-N mean score。
- masked local mean locality > global-N mean locality。

Claim boundary：

- 可以支持 tested local tasks 下的 masked local naturalization seed-level stability。
- 不能支持 global topology repair、watertight topology、category-wide robustness 或 naturalization-alone connectivity guarantee。
