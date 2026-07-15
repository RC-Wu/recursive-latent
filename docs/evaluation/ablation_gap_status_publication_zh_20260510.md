# Ablation gap closure status for publication（2026-05-10）

本文件整理 same-root matrix、naturalization matrix、coral mesh-space generated-root baseline，以及 one-shot vs recursive refinement/effective-resolution 的当前闭合程度。本文只做本地状态汇总；未使用 SSH，未修改 `paper_siga/main.tex`。

## 读取依据

- `docs/progress/ralph_publication_closure_plan_20260510.md`
- `docs/evaluation/ablation_matrix_gap_closure_queue_zh_20260510.md`
- `docs/evaluation/same_root_miniset_render_qa_status_zh_20260510.md`
- `docs/evaluation/naturalization_lsystem_miniset_status_zh_20260510.md`
- `docs/evaluation/coral_mesh_space_generated_root_status_zh_20260510.md`
- `results/publication_ablation_metrics_20260510/matrix_coverage_summary.csv`
- `results/publication_ablation_metrics_20260510/manifest_selected_final_rows.csv`
- `results/publication_ablation_metrics_20260510/claim_safe_miniset_20260510.csv`
- `results/publication_ablation_metrics_20260510/ablation_gap_queue_20260510.csv`
- `results/publication_ablation_metrics_20260510/effective_resolution_schema.csv`

新增机器可读状态表：

- `results/publication_ablation_metrics_20260510/ablation_gap_status_publication_20260510.csv`

## Status vocabulary

- `complete`: 本地资产、指标和 QA 足以支撑限定 claim。
- `partial`: 有可用证据，但矩阵列、matched controls、或 claim-critical 指标仍缺。
- `proxy`: 指标可作为方向性或诊断 proxy，不能支撑强视觉/拓扑 claim。
- `blocked`: 当前本地闭合被缺 row、缺本地 source mesh/asset、或缺 matched render QA 阻塞。

## P0 缺口与闭合程度

| area | item | status | 当前闭合 | 主文 claim gate |
|---|---|---|---|---|
| same-root | `vine_compete_d3` direct/final-only/prune | complete | 三列本地 OBJ、GLB export/import、白底 render QA、components/LCR 均齐；direct 2059 comps/LCR=0.9049，final-only 2/LCR=0.9934，prune 1/LCR=1.0。 | 可写 matched depth-3 projection subset 趋势；不能写 full same-root matrix。 |
| same-root | `tree_compete_d3` direct/final-only/prune | complete | 三列同样已本地 QA；direct 3201 comps/LCR=0.9169，final-only 4/LCR=0.9842，prune 2/LCR=0.9949。 | 备选主文或 appendix，同向支撑；仍不是 full matrix。 |
| same-root | `vine_compete_d3` traditional/bridge/proposed | blocked | `ablation_gap_queue_20260510.csv` 标为 P0 missing required rows。 | 缺这三列前，不能宣称 same-root matrix 闭合。 |
| naturalization | `lsystem_branch/fork_side` rule-only/no-N/weak/masked local-N | partial | 四个 selected textured GLB 本地 import OK，PBR material/1024 texture/face count 与 summary 对齐；source OBJ 仍是 remote-only，缺 topology/root/mask leakage/anchor drift。 | 可作为 visual/export ablation；不能写 topology repair、root reachability、anchor preservation。 |
| naturalization | `lsystem_branch/fork_side` with projection / without projection | blocked | matched projection on/off 控制仍缺。 | 缺这两列前，不能分离 naturalization 与 projection 贡献。 |
| naturalization | coral/pyrite fork-side rule-only 和 projection controls | blocked | coral/pyrite 当前主要是 weak-vs-masked selected GLB；rule-only、global-N、projection on/off、topology metrics 不齐。 | 只可作 stress inset 或 appendix visual status。 |
| coral mesh-space | coral generated-root mesh-space baseline | complete | 12 行本地输出；推荐 `coral_frontier_branch full_srt depth=2 direct merge` 有 OBJ/GLB/preview/metrics，raw comps=250404，occ comps=8，occ LCR=0.992，copy_repetition_score=1.0。 | 可作为 coral 负控 baseline；必须写明 direct copy-paste、无 generator/projection/repair。 |
| effective-resolution | one-shot vs recursive comparison table | proxy | schema 已定义；comparison CSV 有 tree/vine 与 crystal/coral 两组，proxy 包含 local feature scale、terminal detail、zoom retention、estimated high-res blow-up。 | 可写 proxy table；强 zoom-retention/visual effective-resolution claim 仍需 matched zoom render QA。 |

## P1 缺口与闭合程度

| area | item | status | 当前闭合 | 升级条件 |
|---|---|---|---|---|
| same-root | coral direct/prune/bridge | partial/proxy | metrics snapshot 存在，但 final mesh 指向 remote path，本地 GLB/render QA 不齐；traditional/proposed 缺。 | 拉取/本地化 direct/prune/bridge，补 traditional/proposed，导出 GLB/render QA。 |
| same-root | bismuth/pyrite projection variants | blocked | bismuth/pyrite 目前主要是 direct 或远端 metrics snapshot，缺 final-only/prune/bridge/traditional/proposed matched rows。 | 补齐 matched variants 后只能优先进 appendix/stress matrix。 |
| naturalization | coral/pyrite global-N | blocked | matched global-N 控制缺。 | 补齐后默认作为 diagnostic negative，除非 topology/root metrics 强。 |
| naturalization | IFS branch secondary naturalization subset | partial | 有部分 rows/summary，但不如 L-system 四列 clean；local GLB/render QA 仍需补。 | 只作为 secondary appendix。 |

## P2 缺口与闭合程度

| area | item | status | 当前闭合 | 使用边界 |
|---|---|---|---|---|
| same-root | hard-DLA full variants | blocked | direct metrics snapshot 或零散 rows 不足以成 matrix。 | 仅在需要 boundary failure appendix 时补。 |
| naturalization | global-N representative assets | proxy | coverage summary 有 global-N rows，但本地资产和 matched controls 不完整。 | 只能做 diagnostic negative，不能写 topology success。 |
| naturalization | post-hoc repair baseline | proxy/excluded | coverage summary 有 5 行且 missing=0，但该轴不是 recursive projection。 | 可放 appendix repair baseline，不能混入 PS-RSLG projection claim。 |

## 主文可安全使用的最小子集

| subset | status | 可安全写法 | 不可写法 |
|---|---|---|---|
| `SR-vine-projection-3col` | complete | matched vine depth-3 子集上，final-only 与 per-depth prune/projection 相比 direct recursion 显著降低 fragmentation；prune 达到 components=1/LCR=1.0。 | same-root matrix 已闭合；bridge/traditional/proposed 已比较。 |
| `SR-tree-projection-3col` | complete | 作为备选或 appendix，tree depth-3 子集显示同向趋势。 | full six-row same-root conclusion。 |
| `Coral-mesh-space-generated-root` | complete | coral one-shot root 经 S/R/T copy-paste direct merge 的 mesh-space generated-root 负控已闭合，raw face islands 极高；可报告 copy repetition 与无 repair/projection。 | coral mesh-space baseline 递归生成成功；单靠 occ LCR 判定成功/失败。 |
| `N-lsystem-localN-4col` | partial | 四列 selected L-system GLB 均进入同一 texture/export path，适合谨慎 visual/export ablation。 | masked local-N 修复拓扑、保持 root/anchor、无 mask leakage，或 naturalization effect 已与 projection 分离。 |
| `N-coral-localN-2col` | partial | coral weak-vs-masked selected GLB 可做 stress inset/appendix visual status。 | coral naturalization matrix 闭合或 topology repair 成功。 |
| `N-pyrite-localN-2col` | partial | pyrite weak-vs-masked selected GLB 可做 boundary appendix。 | crystal/lattice naturalization 稳定成功。 |
| `ER-proxy-2group` | proxy | 可作为 effective-resolution proxy table，报告 local feature scale、terminal detail、zoom-retention proxy 与 estimated blow-up。 | abstract/contribution-level 的强 zoom retention claim，除非补 matched zoom panels 与 human/render QA。 |

## 当前总判断

- same-root 当前不是 full matrix close；主文只能使用 vine/tree 三列 projection subset，且要避免把它写成六列 same-root matrix。
- naturalization 当前不是 topology close；最干净的是 L-system 四列 visual/export subset，仍被 source mesh 本地化与 projection on/off 控制阻塞。
- coral mesh-space generated-root baseline 已经作为负控闭合，可进入 baseline/ablation 表，但措辞必须强调 copy-paste direct merge。
- one-shot vs recursive refinement/effective-resolution 当前是 proxy close，不是 visual close；适合表格或 appendix claim gate，不适合强主张。
