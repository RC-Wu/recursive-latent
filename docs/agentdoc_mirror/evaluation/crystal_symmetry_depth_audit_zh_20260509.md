---
title: Crystal Symmetry Depth Audit
date: 2026-05-09 13:52 +08
tags: [recursive-growth, crystal, symmetry, trellis2, textured-glb, mesh-qa]
---

# Crystal / Symmetry Depth Audit 2026-05-09

## 当前判断

晶体/对称线现在比 DLA 线更适合进入论文正结果。主要原因：

- `pyrite_lattice_depth` 的 geometry 语义非常清楚：立方晶块、octahedral/facet 暗示、晶格递归增长都能直接看懂；
- textured GLB 的 occupancy LCR 在 depth 1-4 基本为 `0.999-1.000`；
- pyrite 的 PBR 颜色和金属/矿物质感比 bismuth square guide 更稳定；
- 该线可以自然支撑 grammar 中的 group-orbit / lattice rule 小节，而不是只作为“看起来好看”的工程 case。

`bismuth_hopper_depth` 结构也能读出 recursive stepped hopper，但旧 guide 结果偏绿，视觉上不像铋。它更适合作为正在改进的 texture-guide sensitivity / appearance sweep case。已经追加一条 HQ warm bismuth depth run，专门测试能否把它提升为主结果。

## 已有正结果

### Pyrite lattice depth

文件：

- 图：`paper_siga/figures/pyrite_depth_textured_showcase_20260509.png`
- GLB：`visuals/pyrite_depth_textured_showcase_20260509/*/textured.glb`
- 指标：`results/pyrite_depth_textured_showcase_metrics_20260509/metrics.csv`

关键指标：

| depth | GLB occupancy comps | GLB occupancy LCR | box-count D | 视觉判断 |
|---:|---:|---:|---:|---|
| 1 | 10 | 0.999 | 2.10 | 可用；有晶格但还稀疏 |
| 2 | 1 | 1.000 | 2.39 | 强正例 |
| 3 | 1 | 1.000 | 2.36 | 强正例 |
| 4 | 1 | 1.000 | 2.36 | 强正例 |

注意：raw face comps 对 GLB 仍然非常高，不能作为主连通指标。这个现象在 textured GLB 中普遍存在，应在方法/指标小节解释为 export/UV seam diagnostic。

### Bismuth hopper depth

文件：

- 图：`paper_siga/figures/bismuth_depth_textured_showcase_20260509.png`
- GLB：`visuals/bismuth_depth_textured_showcase_20260509/*/textured.glb`
- 指标：`results/bismuth_depth_textured_showcase_metrics_20260509/metrics.csv`

关键指标：

| depth | GLB occupancy comps | GLB occupancy LCR | box-count D | 视觉判断 |
|---:|---:|---:|---:|---|
| 1 | 1 | 1.000 | 2.19 | 结构可用，颜色偏绿 |
| 2 | 1 | 1.000 | 2.17 | 结构可用，颜色偏绿 |
| 3 | 1 | 1.000 | 2.20 | 结构可用，颜色偏绿 |
| 4 | 1 | 1.000 | 2.19 | 结构可用，颜色偏绿 |

## 对方法论的意义

晶体/对称线可以在 PS-RSLG 里这样写：

1. **Orbit proposal rule**：一个非终结符发射一个 group/lattice orbit，而不是独立发射多个 chunk。
2. **Shared anchor certificate**：每个 orbit element 必须通过 lattice edge、hub 或 backbone anchor 连接回已有 support。
3. **Equivariance as soft claim**：如果 rule set 对群作用闭合且 projection 与群作用近似交换，则 geometry 在 voxel support 上有可测的 symmetry consistency；但 frozen sampler/texture export 不保证严格等变。
4. **Appearance separation**：同一 scaffold 不同 guide 可以隔离 structure 和 appearance，因此 crystal stage-4 guide sweep 是合理实验。

这比 DLA bridge 的故事更强：DLA bridge 是“修失败后的诊断”，而 pyrite/crystal 是“语法约束先验直接带来可用资产”的正证据。

## 不能过度宣称

当前不能写：

- 我们模拟了真实晶体生长；
- Trellis2 保证 symmetry/equivariance；
- raw GLB face topology 是干净单连通；
- bismuth 已经达到头图级视觉质量。

可以写：

- 我们支持 crystal-inspired group/lattice recursive grammars；
- 连通 scaffold 在所有递归深度保持 coarse support connectivity；
- frozen generative texture stage 能把这种 scaffold 导出为 textured GLB；
- pyrite lattice 是当前最强非树类/对称 positive case。

## 下一步

1. 等待 `bismuth_depth_hq_warm_showcase_20260509`，拉回 GLB 并用同协议渲染。
2. 如果 warm bismuth 视觉显著改善，生成新版 bismuth depth figure；否则保留 pyrite 为主晶体 case。
3. 给 pyrite/bismuth 增加 symmetry error：对预期 lattice/orbit 采样点做最近邻/occupancy overlap 误差，作为定量表的一个小指标。
4. 在 paper method 中把 crystal/symmetry 写成 group-orbit grammar 的实例，而不是泛泛的“非树类结果”。

## 13:58 更新

`bismuth_depth_hq_warm_showcase_20260509` 已完成并拉回本地：

- GLB：`visuals/bismuth_depth_hq_warm_showcase_20260509/stage*_textured.glb`
- 渲染：`visuals/bismuth_depth_hq_warm_showcase_20260509/renders`
- 指标：`visuals/bismuth_depth_hq_warm_showcase_20260509/metrics_occ64.{csv,json}`

结果判断：

- 四个 stage 的 GLB occupancy LCR 都是 `1.000`，连通性通过；
- warm guide 没有把 bismuth 从绿色/黄绿色显著拉到虹彩金属，视觉提升有限；
- 因此 bismuth 仍不应作为最强晶体主结果，最多作为 appearance-guide sensitivity 或 stepped scaffold 示例；
- pyrite lattice 仍是当前最强 crystal/symmetry 正例。

新增 symmetry/orbit screening metric：

- 脚本：`assets/symmetry_orbit_metrics_20260509.py`
- 数据：`results/symmetry_orbit_metrics_20260509/symmetry_orbit_metrics_stage4.{csv,json}`
- 图：`paper_siga/figures/symmetry_orbit_metrics_20260509.{png,pdf}`

Stage-4 结果：

| case | mirror mean IoU | z-rotation mean IoU | overall mean IoU | 判断 |
|---|---:|---:|---:|---|
| pyrite lattice | 0.610 | 0.608 | 0.609 | 明显高，支持 group/lattice orbit claim |
| bismuth hopper | 0.138 | 0.112 | 0.125 | 非严格对称，更像多中心 stepped hopper |
| porous mineral | 0.127 | 0.116 | 0.121 | 非对称 organic/mineral scaffold |

这个指标只能作为 screening/supplement，不是严格等变性证明；但它能支持论文把 pyrite crystal 单独作为 symmetry/lattice grammar 例子，而不是和 porous/DLA 混在一起。

## 14:38 更新

`pyrite_depth_hq_warm_showcase_20260509` 已完成、拉回并渲染：

- GLB：`visuals/pyrite_depth_hq_warm_showcase_20260509/stage*_textured.glb`
- 渲染：`visuals/pyrite_depth_hq_warm_showcase_20260509/renders/stage{01..04}_{iso,front}.png`
- contact sheet：`visuals/pyrite_depth_hq_warm_showcase_20260509/renders/pyrite_hq_warm_render_contact.png`
- 指标：`visuals/pyrite_depth_hq_warm_showcase_20260509/metrics_occ64.{csv,json}`

指标：

| depth | GLB occupancy comps | GLB occupancy LCR | box-count D | 判断 |
|---:|---:|---:|---:|---|
| 1 | 10 | 0.999 | 2.10 | 可用，低深度较稀疏 |
| 2 | 1 | 1.000 | 2.39 | 强正例 |
| 3 | 1 | 1.000 | 2.36 | 强正例 |
| 4 | 1 | 1.000 | 2.36 | 强正例 |

肉眼判断：

- warm HQ pyrite 比 bismuth 明显更适合作为 crystal/symmetry 主结果；
- 正面视图能看清 lattice/orbit 增长，iso 视图能看清块状晶体簇；
- 金属/矿物 PBR 质感稳定，但局部仍有 Trellis 纹理噪声；
- 需要重新做一张干净的 paper figure，把旧 pyrite depth 图替换为 HQ warm 版本或两者并排选优。

当前建议：

1. 主文 crystal/symmetry case 用 `pyrite_lattice_depth`。
2. bismuth 只作为 stepped scaffold / material guide sensitivity，不放强 claim。
3. symmetry/orbit metric 图可作为小定量或 supplement。
4. crystal 小节的 claim 写成 “group/lattice-inspired recursive scaffold with generative appearance export”，不要写真实晶体生长。

## 14:53 更新：Pyrite HQ 主图与 surface-voxel 连通性

新增 surface-sampled voxel connectivity 诊断，目的是处理一个之前反复混淆的问题：Trellis2 textured GLB 的 raw face component 数量会被 UV/material seam 放大，不能直接等同于视觉碎片或资产碎裂。

文件：

- 指标脚本：`assets/surface_voxel_connectivity_20260509.py`
- 作图脚本：`scripts/figures/compose_surface_voxel_connectivity_20260509.py`
- 数据：`results/surface_voxel_connectivity_20260509/surface_voxel_connectivity_summary.{csv,json}`
- 图：`paper_siga/figures/surface_voxel_connectivity_metric_20260509.{png,pdf}`
- Pyrite HQ 主图：`paper_siga/figures/pyrite_hq_depth_textured_showcase_20260509.{png,pdf}`

surface voxel 指标结果：

| family | strict r0 components by depth | strict r0 LCR by depth | radius-1 seam-tolerant result |
|---|---|---|---|
| Pyrite HQ GLB | `1 / 1 / 1 / 1` | `1.000 / 1.000 / 1.000 / 1.000` | 全部 `1 comp, LCR=1.000` |
| Bismuth HQ GLB | `1 / 1 / 1 / 1` | `1.000 / 1.000 / 1.000 / 1.000` | 全部 `1 comp, LCR=1.000` |
| Porous mineral GLB | `1 / 4 / 4 / 4` | `1.000 / 0.994 / 0.979 / 0.989` | 全部 `1 comp, LCR=1.000` |

解释：

- Pyrite HQ GLB 在 surface-sampled voxel metric 下也是严格单连通，因此比旧的 raw GLB face component 诊断更能支持“不是碎块”的视觉结论。
- Bismuth 结构上其实也连通，但材质/颜色不够像高质量 bismuth，因此仍不作为主晶体图。
- Porous mineral 的严格半径下有小组件，但 radius-1 后合并，说明主要是 seam/alias 或细表面采样层面的碎片；作为 supplement/method-boundary 更合适。
- 这个指标仍然不是 watertight topology proof，也不是物理晶体生长证明。

论文状态：

- `paper_siga/main.tex` 已把主晶体 depth figure 从 Bismuth 替换为 Pyrite HQ。
- metrics 小节新增 surface-sampled GLB connectivity 的解释。
- `paper_siga/main.pdf` 已成功编译，当前 24 页；主要剩余问题是版面过长、float 过多、accessibility alt-text/ACM 元信息 warning，不是构建错误。
