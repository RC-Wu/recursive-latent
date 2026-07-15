# Face 连通与 Occupancy 连通边界（2026-05-09）

## 结论

最新远程烟测 `connectivity_first_dla_crystal_20260509_fix_import_smoke` 可以作为两件事的证据：

1. 远程 harness 的 `recursive_growth_mesh_metrics` 导入问题已经修复，stage-1 DLA 连通性烟测完整跑通，退出状态为 `0`。
2. mesh projection / bridge 可以把碎片表面合并成单一 face component，但这不等价于 occupancy 连通性改善。

它不能作为 DLA/crystal 正例写入强 claim。严格解释应是：**face-level repair 有效，但 occupancy-primary 指标退化；因此它只能支持“claim 边界”和“指标拆分”的诊断，不支持“DLA/crystal topology 已解决”。**

## 新烟测关键数值

来源：`docs/remote_results/ralph_connectivity_fix_smoke_20260509_2140.md`

远程 run：

- Host: `a100-2`
- Run ID: `run_20260509_213606_2501185`
- Case: `dla_voxel_root`
- Grammar: `fork_side_attach`
- Method: `sparse_close_bridge`
- Stage: `1`
- GPU: `CUDA_VISIBLE_DEVICES=4`
- 退出状态: `0`

| 阶段 | face components | face LCR | occupancy components | occupancy LCR | 解释 |
|---|---:|---:|---:|---:|---|
| raw decode | 3157 | 0.980987 | 4 | 0.995475 | raw 表面碎片很多，但体素占据几乎集中在主组件 |
| decoded sparse result | 4226 | 0.971899 | 29 | 0.994233 | sparse token 支持本身为 1 组件，但重新 decode 后 face 和 occupancy 都更碎 |
| mesh projection | 1 | 1.000000 | 6 | 0.939027 | face 被修成单组件；occupancy 组件数从 4 变 6，LCR 从 0.995475 降到 0.939027 |

## 与既有 claim summary 的关系

这条结果加强了 `claim_aligned_metric_summary_zh_20260509.md` 中的边界：

- 主指标仍应是 voxelized 6-neighborhood occupancy component count 和 LCR。
- face component / face LCR 必须作为单独诊断报告，不能替代 occupancy 指标。
- post-hoc bridge / projection 即使能让面片拓扑看起来更干净，也可能损伤占据连通、填洞或产生假桥。

与 `dla_bridge_smoke_stage1_qa_zh_20260509.md` 的旧烟测一致：旧结果里 `volumetric_dla sparse_close_bridge` 已经出现 face component 变为 `1`、但 occupancy components 退化到 `7` 的现象；新结果再次出现同类反例，只是这次 projection 的 face repair 更彻底。

## 可写与不可写

当前可写：

- 远程导入和最小 stage-1 连通性 smoke 已修复并跑通。
- mesh projection 能把本次 DLA-root proposal 的 face components 从 `3157` 降到 `1`。
- face-level connectivity 与 occupancy connectivity 不一致，必须分开报告。
- DLA/coral/crystal 路线目前仍是 stress test 和负例诊断，用来说明后处理桥接不足。

当前不可写：

- 不可写 DLA/crystal 生成已经拓扑连通。
- 不可写 face component 为 `1` 就代表结构连通。
- 不可写 `sparse_close_bridge` / projection 是 DLA-root 的正例解法。
- 不可把本轮作为主文强正例图或成功 claim，除非后续补齐 occupancy-aware selection 并证明 projected occupancy 不退化。

## 后续最小补实验

下一步不要直接扩大到 stage 3。应在同一 stage-1 设置下做小矩阵：

- `sparse_close_bridge`
- `sparse_bridge_select`
- `mesh_bridge_smooth`

选择标准必须同时满足：

- face components 明显下降；
- projected occupancy components 不高于 raw；
- projected occupancy LCR 不低于 raw；
- 视觉 QA 不出现 fake bridge / over-closing。

只有通过这组 occupancy-aware 边界后，才适合继续 DLA / porous / vine 小批量。
