# Ablation Matrix Gap Closure Queue（Lane D, 2026-05-10）

本文把 selected-final-only manifest 中的 same-root / naturalization 缺口转成可执行补跑清单，并给出最小 claim-safe 主文子集建议。本文只做本地规划与 CSV 输出；未 SSH，未启动远端任务，未修改 `paper_siga/main.tex`。

## 1. 读取依据

- `results/publication_ablation_metrics_20260510/matrix_coverage_summary.csv`
- `results/publication_ablation_metrics_20260510/manifest_selected_final_rows.csv`
- `docs/evaluation/publication_ablation_effective_resolution_plan_zh_20260510.md`

新增输出：

- `results/publication_ablation_metrics_20260510/ablation_gap_queue_20260510.csv`
- `results/publication_ablation_metrics_20260510/claim_safe_miniset_20260510.csv`

## 2. Same-root Matrix 当前状态

| row | available | missing | local mesh | local GLB | 当前处理 |
|---|---:|---:|---:|---:|---|
| traditional | 30 | 8 | 29 | 0 | 可做 appendix/status；严格同根子集仍要逐 case 核验。 |
| direct | 8 | 8 | 2 | 0 | `vine_compete_d3` / `tree_compete_d3` 可做负控；coral/bismuth/pyrite 多为远端指标快照。 |
| final-only | 4 | 12 | 2 | 0 | 可与 direct/prune 组成 vine/tree 的 3 列 projection 子集。 |
| prune | 5 | 11 | 2 | 0 | `vine_compete_d3` 最强，LCR=1.0；仍缺 bridge/traditional/proposed。 |
| bridge | 1 | 15 | 0 | 0 | 只有 coral 指标快照，不能进主文正向 claim。 |
| proposed | 15 | 10 | 15 | 0 | 多数不是 `vine_compete_d3` 这种严格同 case row，不能直接补齐 projection 子集。 |

### Same-root P0

P0 是把 `vine_compete_d3` 从 3 列 projection subset 补成最小严格矩阵：

1. 补 `vine_compete_d3 / bridge`。
2. 补或严格映射 `vine_compete_d3 / traditional`。
3. 补或严格映射 `vine_compete_d3 / proposed`。
4. 给已有 `direct/final-only/prune` 导出 GLB 或完成 render-import QA。

这样可形成最小主文候选：direct vs final-only vs per-depth prune vs bridge/traditional/proposed。若 bridge 仍失败，可将 bridge 明确作为 diagnostic row，而不是空缺。

### Same-root P1/P2

- P1：把 coral `direct/prune/bridge` 的远端 final mesh 拉成本地 final asset，并补 `traditional/proposed`；这能形成 non-tree projection appendix matrix。
- P1：bismuth/pyrite 围绕已有 direct row 补 final-only/prune/bridge/traditional/proposed，作为 crystal/lattice stress appendix。
- P2：hard-DLA 只在需要 boundary failure matrix 时补，不应抢 P0 预算。

## 3. Naturalization Matrix 当前状态

| row | available | missing | local mesh | local GLB | 当前处理 |
|---|---:|---:|---:|---:|---|
| rule-only | 4 | 22 | 0 | 1 | L-system selected GLB 可用，但大多数 case 缺 row。 |
| no-N | 8 | 18 | 0 | 1 | alpha=0 控制已有 selected L-system GLB；不是完整 no-naturalizer 协议。 |
| weak blend | 8 | 18 | 0 | 3 | L-system/coral/pyrite selected GLB 可做视觉状态。 |
| masked local-N | 22 | 13 | 14 | 3 | 局部自然化候选最多，但缺 mask leakage/root/anchor 指标。 |
| global-N | 12 | 22 | 0 | 0 | 诊断/负例；不能写成 topology repair。 |
| with projection | 35 | 17 | 29 | 0 | projection 轴证据较多，但不是 naturalization 轴。 |
| without projection | 4 | 22 | 2 | 0 | 关键缺口，尤其 L-system/coral/pyrite selected rows。 |

### Naturalization P0

P0 是把最干净的 selected L-system row 做成主文可用的谨慎 4-6 列图表：

1. 对 `lsystem_branch/fork_side` 已有 `rule-only/no-N/weak blend/masked local-N` 四个 selected GLB，拉齐本地 final mesh 或重新导出 local mesh。
2. 对同一 case 计算 occupancy/root/mask leakage/anchor drift 指标。
3. 补 `with projection` 与 `without projection` 控制，分离 naturalization 与 projection 贡献。
4. 若预算允许，再补 matched `global-N` 作为负例列；否则 global-N 放 appendix diagnostic。

Coral/pyrite 的 P0 是补 `rule-only` 和 projection on/off 控制，因为当前只有 weak-vs-masked selected GLB，不能支撑完整自然化 claim。

## 4. Claim-safe 最小主文子集

已写入 `claim_safe_miniset_20260510.csv`。建议如下：

| miniset | 当前可用 | 主文措辞 |
|---|---|---|
| `SR-vine-projection-3col` | `vine_compete_d3` direct/final-only/prune；本地 OBJ 和完整 components/LCR | 可写 projection subset 趋势：direct fragmented，final-only/prune 改善；不能写 full matrix。 |
| `SR-tree-projection-3col` | `tree_compete_d3` direct/final-only/prune | 备选或 appendix，支撑同类趋势。 |
| `N-lsystem-localN-4col` | rule-only/no-N/weak/masked-local selected GLB | 可写 selected rows enter same texture/export path；不能写 topology repair。 |
| `N-coral-localN-2col` | coral weak/masked selected GLB | 只做 stress inset 或 appendix。 |
| `N-pyrite-localN-2col` | pyrite weak/masked selected GLB | 只做 boundary appendix。 |
| `ER-proxy-2group` | 32 effective-resolution method rows + 2 comparison rows | 可做 proxy table；强 zoom claim 仍需 matched render QA。 |

## 5. 不能 Claim 的内容

- 不能说 same-root matrix 已闭合；bridge、traditional/proposed strict match 仍缺。
- 不能说 masked local-N 稳定修复 topology；当前缺 root/anchor/mask leakage 和 projection-off 控制。
- 不能把 global-N 的 near-LCR row 写成成功；它是 diagnostic 或 boundary。
- 不能把 post-hoc repair baseline 混入 recursive projection。
- 不能把远端路径加本地指标快照写成“本地 final mesh/GLB 已齐”。

## 6. P0 补跑优先级

1. `vine_compete_d3` same-root：补 `bridge/traditional/proposed`，并给已有 `direct/final-only/prune` 做 GLB/render QA。
2. `lsystem_branch/fork_side` naturalization：本地化四个 selected GLB 的 source mesh，补 occupancy/root/mask leakage，补 with/without projection。
3. `coral_v3b/fork_side`：补 rule-only 和 projection on/off；已有 weak/masked GLB 只能先做 stress inset。
4. `pyrite_v3b/fork_side`：补 rule-only 和 projection on/off；建议默认 appendix/boundary。
5. Coral same-root non-tree：本地化 direct/prune/bridge 远端资产并补 traditional/proposed，用于 appendix 矩阵，不抢主文 P0。
