# Ablation Completion and Main/Appendix Recommendation

日期：2026-05-10  
范围：仅依据以下材料判断：

- `results/ablation_summary_20260510/*.csv`
- `results/gen3d_baseline_metrics_20260510/*.csv`
- `results/gen3d_baseline_metrics_20260510/gen3d_baseline_mesh_metrics.csv/mesh_quality_metrics.csv`
- `AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_gen3d_baseline_ablation_plan_20260510.md`

本文不修改 `main.tex`，只给出完成度、主文/附录放置建议和当前可支持的论文主张边界。

## 1. 总体结论

当前证据已经足够支持一个收敛后的主文故事：在 Trellis2 ordinary one-shot、Trellis2 trivial latent copy、Trellis2 generated-root mesh-space copy 与 PS-RSLG 的对比中，普通 3D 生成或朴素递归复制不能稳定解决受控递归资产生成；PS-RSLG 在 pyrite/coral 非树类案例上有强连接性证据，vine/root 类需要使用更强的 stage-5 vine reference，而不是严格匹配批次里的弱 vine 行。

但当前不应声称“所有 ablation 已完成”。`ablation_gap_counts_20260510.csv` 显示 same-root projection matrix 和 naturalization/projection matrix 均仍有缺口；尤其 bridge、final-only、prune、without projection、rule-only、no-N、weak blend 不能作为完整矩阵主文结论。

主文建议只保留以下 claim-bearing 内容：

1. Trellis2 one-shot / latent-copy / mesh-space-copy / PS-RSLG 的核心对比表。
2. pyrite 和 coral 的 PS-RSLG 非树类成功证据。
3. vine/root 使用 stronger vine stage5 reference 作为视觉与指标证据，并明确它不是 strict matched ours_vine 弱行。
4. same-root projection 只展示已闭合的局部对比或作为趋势证据，不写成完整矩阵。
5. naturalization/projection 只展示 masked local-N + projection 与 global-N/post-hoc repair 的边界性证据；rule-only/no-N/weak blend 暂不能主文下结论。

## 2. Gen-3D Baseline 完成度

计划要求的方法包括 TRELLIS one-shot、TRELLIS.2 one-shot、Hunyuan3D 2.0 one-shot、TRELLIS.2 + mesh-space grammar、Hunyuan3D + mesh-space grammar、TRELLIS.2 + trivial latent transform、Ours/PS-RSLG。

按当前 CSV 可见结果：

| 方法 | 完成度 | 当前证据 | 主文建议 |
|---|---:|---|---|
| TRELLIS one-shot | missing | 指定 CSV 中没有 TRELLIS 非 2 行 | 不进主文；若保留计划痕迹，放附录待补 |
| TRELLIS.2 one-shot | complete for 3 cases | vine/pyrite/coral 三行均有；vine occupancy LCR=1.000，pyrite=0.127，coral=0.600 | 可进主文核心 baseline |
| Hunyuan3D 2.0 one-shot | missing from requested CSVs | 指定 CSV 中没有 Hunyuan 行，也没有 blocked row/error | 不进主文结论；附录列为未完成/待补 |
| TRELLIS.2 + mesh-space grammar | partial | vine、pyrite 有 generated-root mesh-space direct merge；coral missing | vine/pyrite 可进主文或附录表；coral 缺失必须标注 |
| Hunyuan3D + mesh-space grammar | missing | 指定 CSV 中没有 Hunyuan mesh-space 行 | 不进主文 |
| TRELLIS.2 + trivial latent transform | complete for 3 cases | vine/pyrite/coral 均有 copy_shift_upper_z；三者 status 均为 fragmented | 可进主文核心 baseline |
| Ours / PS-RSLG | partial but usable | pyrite/coral strict rows success；strict vine 行 LCR=0.072 且标注 needs_vine_candidate_swap_or_QA；stronger vine stage5 reference LCR=0.999 | pyrite/coral strict 可进主文；vine 主文应换 stage5 reference 并说明选择理由 |

关键指标：

- Trellis2 one-shot：vine 成功但 pyrite/coral fragmented。pyrite occupancy LCR=0.127，coral occupancy LCR=0.600。
- Trellis2 trivial latent：三例均 fragmented。vine LCR=0.689，pyrite LCR=0.102，coral LCR=0.824；不能解释为受控递归语义成功。
- Mesh-space generated-root baseline：vine 有 101699 个 raw mesh components，pyrite 有 173575 个 raw mesh components；pyrite occupancy LCR=0.033，说明朴素 mesh copy-paste 极端破碎。coral 缺失。
- Ours / PS-RSLG：pyrite 和 coral strict textured rows occupancy LCR=1.000；stronger vine stage5 reference occupancy LCR=0.999。

## 3. Same-Root Projection Matrix 完成度

计划要求固定矩阵行：`traditional`、`direct`、`final-only`、`prune`、`bridge`、`proposed`。

`ablation_gap_counts_20260510.csv` 给出的完成度如下：

| variant | available | missing | 完成度判断 | 说明 |
|---|---:|---:|---|---|
| traditional | 30 | 8 | partial | 可作为传统 baseline 证据，但不是完整矩阵 |
| direct | 8 | 8 | partial | 有 bismuth/coral/hard_dla/pyrite 与 tree/vine compete 类行 |
| final-only | 4 | 12 | partial | 仅 tree/vine compete 类有行 |
| prune | 5 | 11 | partial | coral 与 tree/vine compete 类有行 |
| bridge | 1 | 15 | partial/minimal | 只有 coral bridge 一行；不能主文泛化 |
| proposed | 15 | 10 | partial | root/tree/vine 与若干 PS-RSLG proxy 行可用，但矩阵仍未闭合 |

建议：

- 主文不要写“same-root projection ablation 完整完成”。
- 主文可以展示一个较小的、已对齐的 same-root subset，重点说明 direct/prune/bridge/proposed 在可比案例上的连接性趋势。
- 完整矩阵、缺失行、source file 混杂问题放附录或 evaluation report。
- bridge 只有一行，最多作为 qualitative/diagnostic supporting result；不能支撑“bridge 普遍有效”或“bridge 已被系统比较”的主张。

## 4. Naturalization / Projection Matrix 完成度

计划要求行：`rule-only`、`no-N`、`weak blend`、`masked local-N`、`global-N`、`with projection`、`without projection`，并要求把 local masked naturalization 与 projection 分开。

当前 gap counts：

| variant | available | missing | 完成度判断 | 说明 |
|---|---:|---:|---|---|
| rule-only | 0 | 18 | missing | 不能写入主文实验结论 |
| no-N | 0 | 18 | missing | 不能写入主文实验结论 |
| weak blend | 0 | 18 | missing | 不能写入主文实验结论 |
| masked local-N | 14 | 13 | partial | 有 tree/root/vine、crystal/coral/lattice proxy 行，但仍缺近半 |
| global-N | 12 | 14 | partial | bismuth/coral/pyrite/vine 有 global flow-SDE 行，结果多为 negative 或 near_lcr_fragmented |
| with projection | 35 | 9 | partial | 证据最多，但仍非完整矩阵 |
| without projection | 4 | 14 | partial/minimal | 只有 tree/vine compete 类四行 |
| post-hoc repair baseline | 5 | 0 reported | supporting only | 这是额外 baseline，不等同 projection；不应混入 projection 成功主张 |

建议：

- 主文可以保留“projection-stabilized recursion 与 masked local naturalization 的组合在选定案例上更可靠”的有限主张。
- 主文不应声称 rule-only/no-N/weak blend 已被实证比较。
- global-N 行适合放主文的反例或边界小表：例如 bismuth steps=2 LCR=0.007、coral steps=2 LCR=0.141、pyrite steps=2 LCR=0.219，说明 global naturalization 不稳定；但高 LCR 且 fragmented 的行要谨慎解释。
- post-hoc repair baseline 必须标为 mesh-space surface repair，不可称为 projection。

## 5. One-Shot vs Recursive Refinement / Effective Resolution

计划要求至少一个 tree/vine 和一个 crystal/coral 案例，包含 local feature scale、terminal detail count、zoom retention score、face count、GLB size，以及 full-object high-resolution blow-up estimate。

当前 CSV 支持：

- face count、vertex count、file size、component count、occupancy LCR 已有。
- vine/pyrite/coral 的 one-shot、latent-copy、部分 mesh-space、PS-RSLG 对比已可形成基础表。
- stronger vine stage5 reference 有 647958 vertices、455964 faces、26.230 MB、occupancy LCR=0.999，可替换弱 strict vine 行。

当前 CSV 不支持：

- local feature scale。
- terminal detail count。
- zoom retention score。
- estimated full-object high-resolution blow-up。
- 两级 zoom-in 定量保真对比。

因此 effective-resolution claim 目前只能写成“有初步资产和基础复杂度指标”，不能写成“已定量证明 two-level zoom retention / effective resolution advantage”。

## 6. 主文 vs 附录建议

### 建议进入主文

1. `gen3d_baseline_summary_table_20260510.csv` 的精简版：保留 Trellis2 one-shot、Trellis2 trivial latent、mesh-space generated-root、Ours/PS-RSLG。
2. pyrite/coral 非树类主结果：Ours strict rows LCR=1.000，对比 Trellis2 one-shot 与 latent-copy fragmented。
3. vine/root 主结果：使用 stronger vine stage5 reference，不使用 strict ours_vine 弱行作为正例；表注说明 strict row failed QA and was replaced by stronger available vine candidate。
4. mesh-space copy-paste 失败证据：vine 101699 raw components、pyrite 173575 raw components，作为朴素 mesh recursion 不成立的强证据。
5. 一个小型 projection/naturalization ablation 表：只放可比且证据清楚的 subset，并明确其不是完整矩阵。

### 建议进入附录

1. same-root projection 全量 available rows 与 missing counts。
2. naturalization/projection 全量 available rows 与 missing counts。
3. global-N negative/near_lcr_fragmented 详细行。
4. post-hoc repair baseline，单独标注为 repair diagnostic。
5. Hunyuan3D、TRELLIS 非 2、coral mesh-space generated-root 的 missing/blocked 状态表。
6. weak strict vine row 与 candidate swap rationale。
7. 所有 broad gallery、uninspected visual、diagnostic-only render、source-file inventory。

## 7. 当前支持与不支持的论文主张

### 当前支持

- 支持：Trellis2 one-shot 对 tree/vine 较容易，但在 pyrite/coral 非树递归结构上出现明显 fragmentation。
- 支持：trivial latent/support copy 没有 projection-stabilized grammar semantics，三例均标为 fragmented，不能替代受控递归生成。
- 支持：generated-root mesh-space direct merge 在 vine/pyrite 上严重 copy-paste fragmentation，尤其 raw mesh component 数极高。
- 支持：PS-RSLG strict pyrite/coral 在 occupancy proxy 下保持 connected，LCR=1.000。
- 支持：存在 paper-grade vine 替代候选，stronger vine stage5 reference 的 occupancy LCR=0.999。
- 支持：global-N naturalization 在多个设置下不稳定，存在 negative 或 near_lcr_fragmented 结果。

### 当前不支持

- 不支持：Hunyuan3D2.0 baseline 已完成。
- 不支持：TRELLIS 非 2 baseline 已完成。
- 不支持：coral mesh-space generated-root baseline 已完成。
- 不支持：same-root projection matrix 全部闭合。
- 不支持：naturalization/projection matrix 全部闭合。
- 不支持：rule-only、no-N、weak blend ablation 已比较。
- 不支持：local feature scale、terminal detail count、zoom retention score、effective-resolution blow-up 已定量完成。
- 不支持：bridge/prune/final-only 的普遍结论；当前只能说有局部或少量证据。

## 8. 推荐写法边界

主文可以写：

> In the controlled Trellis2 comparison, ordinary one-shot generation and trivial latent/mesh recursive controls fail to preserve connected recursive structure on non-tree cases, while PS-RSLG remains connected for the pyrite and coral cases under the occupancy connectivity proxy.

主文不应写：

> We completed all ablations across all baselines.

主文可以写：

> The same-root and naturalization matrices are reported as partially completed ablations; the main paper uses only claim-bearing rows and the appendix reports missing entries explicitly.

主文不应写：

> Projection, bridge, pruning, and naturalization variants have all been exhaustively evaluated.

## 9. 最短行动建议

若只为当前论文版本做最小安全整合：

1. 主文放 Gen-3D baseline 精简表，并把 missing Hunyuan/TRELLIS/coral mesh-space rows 标成 missing 或移至附录。
2. 主文采用 pyrite/coral strict PS-RSLG，vine 使用 stronger stage5 reference。
3. 主文只做 limited ablation claim；把 gap counts 明确放附录。
4. 所有 effective-resolution/zoom-retention 定量语句保留为 pending，除非补齐 zoom metrics。
5. 不要把 post-hoc repair baseline 混称为 projection。
