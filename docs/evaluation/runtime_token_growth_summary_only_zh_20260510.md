# Runtime / Token Growth Summary-only 诊断（2026-05-10 00:40）

## 背景

修订文档要求补 runtime、memory、token/mesh growth、per-depth encode/decode/projection/texture cost。远端项目目录已经接近 `100GB` 上限，因此不能继续大规模写 OBJ/PNG/GLB。为此新增了低存储执行模式：

- 修改脚本：`assets/trellis2_recursive_slat_grammar_workflow.py`
- 新增参数：`--summary-only`
- 行为：仍然执行 Trellis2 mesh-to-SLat encode、grammar sparse-latent rule update、decode 和计时，但不写 `mesh.obj` / `preview.png`。

这不是视觉结果，也不是 topology 证据；它用于补 runtime / token-growth / finite-depth scaling 的实验表。

## 已完成 runs

1. `runtime_token_growth_summary_only_ralph_20260510_0030`
   - 4 GPU，depth 3
   - cases：vine、pyrite、bismuth、coral
   - output size：约 `39K`

2. `runtime_token_growth_deep_summary_only_ralph_20260510_0036`
   - 4 GPU，depth 6
   - cases：vine、pyrite、bismuth、coral
   - output：只有 `summary.json`

本地聚合：

- `results/runtime_token_growth_aggregate_20260510/runtime_token_growth_rows.csv`
- `results/runtime_token_growth_aggregate_20260510/runtime_token_growth_case_summary.csv`
- 当前聚合规模：`24` case-level rows，`1521` per-depth/per-grammar rows。

## Case summary 快照

| run | case | grammar count | max depth | max tokens | max vertices | max faces | mean decode sec | max decode sec | reserved GPU GB |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| depth3 | vine | 3 | 3 | 1178 | 238069 | 425486 | 0.054 | 0.103 | 2.02 |
| depth3 | bismuth | 4 | 3 | 4636 | 974058 | 1784440 | 0.093 | 0.141 | 3.07 |
| depth3 | coral | 4 | 3 | 4010 | 600076 | 1122742 | 0.069 | 0.115 | 2.38 |
| depth3 | pyrite | 4 | 3 | 5484 | 1833502 | 3307886 | 0.119 | 0.198 | 4.07 |
| depth6 | bismuth | 5 | 6 | 4636 | 1003052 | 1855382 | 0.094 | 0.167 | 3.29 |
| depth6 | coral | 5 | 6 | 6889 | 721055 | 1195928 | 0.068 | 0.125 | 2.55 |
| depth6 | vine | 4 | 6 | 1850 | 258142 | 440090 | 0.049 | 0.089 | 2.08 |
| depth6 | pyrite | 5 | 6 | 5644 | 1865434 | 3386358 | 0.120 | 0.210 | 4.79 |
| depth10 | vine | 4 | 10 | 2143 | 268626 | 453636 | 0.045 | 0.110 | 2.12 |
| depth10 | pyrite | 4 | 10 | 6857 | 1954486 | 3540672 | 0.142 | 0.214 | 4.42 |
| depth10 | bismuth | 4 | 10 | 6020 | 1150610 | 2081510 | 0.104 | 0.151 | 3.50 |
| depth10 | coral | 4 | 10 | 6923 | 727069 | 1207024 | 0.075 | 0.125 | 2.80 |
| broad-depth6 | vine | 18 | 6 | 2279 | 467964 | 766926 | 0.040 | 0.109 | 2.18 |
| broad-depth6 | pyrite | 18 | 6 | 7674 | 1962454 | 3635452 | 0.138 | 0.221 | 4.83 |
| broad-depth6 | bismuth | 18 | 6 | 11486 | 2171892 | 3952656 | 0.113 | 0.267 | 4.36 |
| broad-depth6 | coral | 18 | 6 | 6889 | 1009183 | 1795620 | 0.062 | 0.133 | 3.16 |
| saturation-depth12 | vine | 6 | 12 | 2279 | 486495 | 854268 | 0.046 | 0.112 | 2.35 |
| saturation-depth12 | pyrite | 6 | 12 | 7677 | 1983066 | 3572390 | 0.161 | 0.227 | 4.76 |
| saturation-depth12 | bismuth | 6 | 12 | 11486 | 2171765 | 3952310 | 0.131 | 0.271 | 5.07 |
| saturation-depth12 | coral | 6 | 12 | 6923 | 809425 | 1572826 | 0.073 | 0.132 | 2.80 |
| upper-depth20 | vine | 4 | 20 | 2279 | 492061 | 875128 | 0.050 | 0.090 | 2.35 |
| upper-depth20 | pyrite | 4 | 20 | 6857 | 2057855 | 3753624 | 0.173 | 0.220 | 4.79 |
| upper-depth20 | bismuth | 4 | 20 | 8439 | 1553014 | 2841148 | 0.132 | 0.189 | 4.03 |
| upper-depth20 | coral | 4 | 20 | 4287 | 814419 | 1595400 | 0.076 | 0.095 | 2.90 |

## 初步结论

1. **summary-only 模式可作为过夜/低存储 runtime 证据通道。**  
   两批实验只写几十 KB 到本地/远端 summary，但完整经过 Trellis2 encoder/decoder 与 sparse-latent rule update，因此适合补 `Implementation Details` 和 `Runtime/Complexity` 表。

2. **decode time 本身很短，但这不是完整 pipeline runtime。**  
   单次 decode 多数在 `0.05-0.21s` 范围；但完整运行还包括 model load、o-voxel conversion、encode、projection/naturalization/texture 等，目前只覆盖其中一部分。论文里不能把这些数写成 end-to-end 运行时间。

3. **pyrite/crystal 类是当前 token/mesh footprint 最大的 stress case。**  
   depth6 pyrite 达到约 `5.6k` sparse tokens、`1.87M` vertices、`3.39M` faces，GPU reserved memory 约 `4.8GB`。这支持“crystal/transform-copy 家族是 scaling 压力更大的类别”的诊断，但不是视觉质量或连通性证据。

4. **finite-depth 目前应写成受 token budget 控制的执行，而非无限生成。**  
   depth6 在 summary-only 下可运行，但没有证明 effective resolution 超越 one-shot generator，也没有证明 topology/texture 在高 depth 仍好。对应 TODO 仍不能删除。

## 论文写法建议

- 可在 Implementation / Complexity 中写：we report per-depth token count, decoded mesh size, decode time, and peak reserved memory under a summary-only profiling mode that avoids material export.
- 保留 `\ExpFigTODO{Measure runtime, GPU memory, per-depth encode/decode/projection cost, token growth, mesh growth, and texture export cost.}`，因为 projection、naturalization、texture export 的完整分项还没闭合。
- 不要把这些数字用于支持 final asset quality；它们只支持 computational characterization。

## 当前继续运行

Stress run 已完成并纳入聚合：

- remote：`results/runtime_token_growth_stress_summary_only_ralph_20260510_0042`
- depth：10
- output：summary-only
- 结果：四类 case 均达到 depth 10，未写 mesh/PNG/GLB；pyrite stress 最大，约 `6.9k` tokens、`3.54M` decoded faces。

Broad grammar profiling 已完成并纳入聚合：

- remote：`results/runtime_token_growth_broad_summary_only_ralph_20260510_0048`
- grammars：18 个 grammar family，包括 branch、frontier、transform-copy、scale、portal、competition/attachment variants
- depth：6
- 结果：bismuth broad 是当前最大 token/mesh footprint，约 `11.5k` tokens、`3.95M` decoded faces；所有输出仍为 summary-only。

Operator-saturation profiling 已完成并纳入聚合：

- remote：`results/runtime_operator_saturation_summary_only_ralph_20260510_0055`
- grammars：6 个高压力/边界 grammar family
- depth：12
- 结果：bismuth saturation 保持当前最大 reserved memory（约 `5.07GB`）和 `3.95M` decoded faces；pyrite saturation 达到 `3.57M` faces；所有输出仍为 summary-only。

Depth-20 upper-bound profiling 已完成并纳入聚合：

- remote：`results/runtime_upper_bound_depth20_summary_only_ralph_20260510_0100`
- depth：20
- grammars：4 个代表性高 depth grammar family
- 结果：四类 case 均达到 depth 20；pyrite d20 最大 decoded faces 约 `3.75M`，bismuth d20 最大 tokens 约 `8.4k`。注意这些数字只说明 finite-depth executor 和 decoder 可运行，并不说明高 depth 视觉结果或拓扑质量合格。
