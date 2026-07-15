# Projection / Masked Naturalization 主消融矩阵状态 2026-05-11

## 结论

本地 deterministic runner 已闭合 Experiment 2 与 Experiment 4 的指标矩阵，用于论文主表和视觉候选筛选。字段后缀为 `_proxy` 的项目均来自 primitive trace / mesh proxy，不是 Trellis runtime sparse-handle graph。2026-05-11 12:07 CST 状态：论文主文表图已写入 `paper_siga/main.tex`，LaTeX 编译通过，undefined references/citations 均为 0，并已通过 commit `83d1de0` 推送到 Overleaf `master`。

## Experiment 2 Projection Ablation

| variant | runs | Occ. LCR | Root reach. | Orphan active | Handle survival | Fail rate |
|---|---:|---:|---:|---:|---:|---:|
| no projection | 12 | 0.898±0.014 | 0.504±0.311 | 3.67±2.64 | 0.504±0.311 | 1.000±0.000 |
| final-only | 12 | 0.995±0.008 | 0.504±0.311 | 3.67±2.64 | 0.504±0.311 | 1.000±0.000 |
| per-depth prune-only | 12 | 0.964±0.043 | 1.000±0.000 | 0.00±0.00 | 0.782±0.148 | 0.750±0.452 |
| per-depth connector-aware | 12 | 0.995±0.008 | 1.000±0.000 | 0.00±0.00 | 1.000±0.000 | 0.250±0.452 |
| full PS-RSLG | 12 | 1.000±0.000 | 1.000±0.000 | 0.00±0.00 | 1.000±0.000 | 0.000±0.000 |

## Experiment 4 Masked Naturalization Ablation

| variant | runs | roughness | normal | artifacts | drift | handle survival | quality |
|---|---:|---:|---:|---:|---:|---:|---:|
| rule-only | 12 | 50.00±4.48 | 0.000±0.000 | 0.487±0.015 | 0.203±0.050 | 0.500±0.307 | 0.529±0.036 |
| no-N/no-proj | 12 | 50.04±4.53 | 0.000±0.000 | 0.487±0.016 | 0.202±0.047 | 0.504±0.311 | 0.530±0.036 |
| weak/no-proj | 12 | 47.77±4.68 | 0.001±0.002 | 0.487±0.018 | 0.202±0.050 | 0.508±0.315 | 0.531±0.038 |
| masked/no-proj | 12 | 47.45±4.66 | 0.003±0.006 | 0.488±0.016 | 0.201±0.051 | 0.500±0.307 | 0.530±0.038 |
| global/no-proj | 12 | 47.58±4.74 | 0.003±0.005 | 0.479±0.018 | 0.205±0.058 | 0.508±0.315 | 0.458±0.037 |
| no-N/+proj | 12 | 16.94±1.46 | 0.597±0.035 | 0.348±0.032 | 0.000±0.000 | 1.000±0.000 | 0.771±0.006 |
| weak/+proj | 12 | 14.11±1.10 | 0.664±0.026 | 0.228±0.012 | 0.088±0.009 | 1.000±0.000 | 0.805±0.004 |
| masked/+proj | 12 | 13.92±1.12 | 0.669±0.027 | 0.227±0.011 | 0.090±0.016 | 1.000±0.000 | 0.807±0.006 |
| global/+proj | 12 | 13.58±1.00 | 0.677±0.024 | 0.229±0.012 | 0.090±0.011 | 1.000±0.000 | 0.735±0.003 |
| final-only ctrl | 12 | 17.04±1.36 | 0.594±0.032 | 0.348±0.033 | 0.004±0.005 | 0.504±0.311 | 0.678±0.040 |

## 论文输出

- Projection 主表：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/projection_ablation_main_table_20260511.tex`
- Naturalization 主表：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/masked_naturalization_main_table_20260511.tex`
- Projection PPTX source manifest：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/ablation_pptx_20260511/projection_ablation_visual_manifest_20260511.json`
- Naturalization PPTX source manifest：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/ablation_pptx_20260511/masked_naturalization_visual_manifest_20260511.json`
- Projection visual tasks：`coral_frontier, ifs_crystal`
- Naturalization visual tasks：`botanical_root, vine_trellis`

## 当前论文落地状态

1. `scripts/figures/compose_ablation_pptx_20260511.js` 已生成两张 PPTX-first 主文图，并由 Keynote 导出 PDF。
2. `paper_siga/main.tex` 已引用 `figures/ablation_pptx_20260511/projection_ablation_pptx_20260511.pdf` 与 `figures/ablation_pptx_20260511/masked_naturalization_ablation_pptx_20260511.pdf`。
3. `drafts/projection_ablation_main_table_20260511.tex` 与 `drafts/masked_naturalization_main_table_20260511.tex` 已作为主文表引入。
4. 这轮主文 claim 已收窄为 deterministic structural/local-surface proxy，不声称 PBR seam 或真实 Trellis runtime handle graph 已完全解决。
5. 若后续继续推进，建议另开 PBR/真实 Trellis showcase 或传统 baseline 视觉任务，而不是重复本轮主消融闭环。
