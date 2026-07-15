---
title: 纹理 / Flow / 连通性迭代证据整理 2026-05-09 23:15
date: 2026-05-09
project: recursive_3d_generative_growth
tags:
  - recursive-3d-generative-growth
  - trellis2
  - connectivity
  - texture
  - flow-sde
  - siga
status: current
---

# 纹理 / Flow / 连通性迭代证据整理 2026-05-09 23:15

本文只整理已经同步到本地的证据，不新增远端 SSH 操作，不启动 GPU 任务。结论服务于当前 PS-SLG / PS-RSLG 主线：递归语法负责 sparse support、anchors、competition、projection 和连通性约束；冻结 Trellis2 sampler / texture route 作为局部 naturalization 与 textured GLB export 兼容性证据。Texture/PBR 不能替代 geometry / connectivity 证明。

## 0. 输入证据

- AgentDoc 计划：`/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_system_grammar_plan_20260508.md`
- 新拉回 textured GLB summaries：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/ralph_positive_method_texture_xformers_20260509_223618/**/summary.json`
- Ralph method compare 摘要：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/remote_results/ralph_method_compare_20260509_221704.md`
- 现有总览：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/progress/项目全任务完成情况总览_2026-05-09.md`

## 1. 一句话结论

本轮最强新增证据不是“DLA/晶体/纹理全部解决”，而是：**connectivity-first method compare 产出了可分级的非树 case 证据，并且其中 bismuth、pyrite、coral 三个 selected projected mesh 已经成功通过 true Trellis2 textured GLB export；DLA raw boundary 也能导出 textured GLB，但只适合作为边界/反例。**

主文可写的强度应控制为：

- 可写：selected non-tree / crystal-like / coral-like projected scaffolds can be exported as true Trellis2 textured GLB assets after connectivity-aware selection.
- 可写：connectivity correction is case- and grammar-dependent; voxel connectivity and mesh-face connectivity must be reported separately.
- 不可写：full DLA solved、physical DLA reproduced、all repairs monotonically improve connectivity、textured GLB topology is clean。
- 不可写：masked flow/SDE repair 已系统性胜过 projection；当前只证明低步数 frozen sampler / texture route 对 selected meshes 跑通。

## 2. 四个新 textured GLB 产物

本轮本地新产物位于：

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/ralph_positive_method_texture_xformers_20260509_223618`

| case | method source | local GLB | status | steps | texture | mesh faces | SLAT tokens | GLB size | 主文定位 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| bismuth | `fork_side_attach/sparse_close_bridge/stage_01/projected` | `bismuth_fork_sparse_bridge/textured.glb` | ok | 8 | 2048 | 1,622,792 | 5,361 | 52.1 MB | 正结果 |
| pyrite | `fork_side_attach/sparse_close_bridge/stage_01/projected` | `pyrite_fork_sparse_bridge/textured.glb` | ok | 8 | 2048 | 1,835,232 | 6,257 | 66.6 MB | 边界正结果 |
| coral | `fork_side_attach/sparse_close/stage_02/projected` | `coral_fork_sparse_close/textured.glb` | ok | 8 | 2048 | 264,544 | 1,140 | 12.7 MB | 正结果候选 |
| DLA | `compete_fork_attach/raw/stage_01/projected` | `dla_raw_boundary/textured.glb` | ok | 6 | 1536 | 304,588 | 4,400 | 10.6 MB | 边界/负例 |

对应白底渲染和 contact sheet：

- contact sheet：`visuals/ralph_positive_method_texture_xformers_20260509_223618/ralph_positive_method_texture_contact_pure_white_20260509.png`
- flat renders：`visuals/ralph_positive_method_texture_xformers_20260509_223618/pure_white_renders_2315/flat/*.png`
- rgba renders：`visuals/ralph_positive_method_texture_xformers_20260509_223618/pure_white_renders_2315/rgba/*.png`

这些 GLB 都证明了 true Trellis2 mesh texturing export route 对 selected projected meshes 可运行：summary 中 `kind=trellis2_mesh_texturing_export_glb` 且 `status=ok`。但它们不是 topology proof；主文图若使用 textured render，必须配同 case 的 connectivity table 或 neutral mesh / support 诊断。

## 3. Method Compare 连通性结论

### 3.1 可写入主文的正结果

**Bismuth hopper / fork_side_attach 是当前最稳非树正例。**

- `raw`、`mesh_bridge_smooth`、`sparse_close_bridge` 均达到 `occupancy_component_count=1`、`occupancy_lcr=1.000`、`face_component_count=1`、`face_largest_component_ratio=1.000`。
- `sparse_close` 也保持 occupancy 完全连通，只剩 `face_component_count=2`、`face_lcr=0.998`。
- 主文适合表述为：connectivity-first grammar 在 bismuth-like crystal scaffold 上可稳定产生 voxel 和 surface-face 双重连通候选；texture export 可作为资产化兼容性展示。

**Coral / volumetric DLA-inspired case 的 fork_side_attach+sparse_close 是修复型正结果候选。**

- `volumetric_dla_coral/fork_side_attach/sparse_close` 达到 `occupancy_component_count=1`、`occupancy_lcr=1.000`，face 侧为 `face_component_count=2`、`face_lcr=0.987`。
- 这说明 grammar choice 与 connectivity correction method 有强交互：同一 coral case 下，`fork_side_attach` 明显优于 `compete_fork_attach`。
- 主文可写为 DLA-coral-inspired connected scaffold / coral-like stress case，不能写成 physical DLA 成功。

**True Trellis2 textured GLB route 对 bismuth/pyrite/coral selected candidates 跑通。**

- bismuth、pyrite、coral 都以 `steps=8`、`resolution=512`、`texture_size=2048` 导出 `status=ok` 的 GLB。
- 这支撑“selected projected recursive scaffolds are compatible with native Trellis2 appearance export”，不支撑“texture 修复了拓扑”。

### 3.2 只可作为边界/负结果

**Pyrite lattice 是 occupancy 正、surface 边界。**

- `raw`、`sparse_close`、`sparse_close_bridge` 的 occupancy 都是完全连通。
- 但 face components 分别为 3、5、4；`sparse_close_bridge` 可把 face LCR 恢复到约 0.994，却没有完全消除 face 碎片。
- 主文可作为“voxel support connectivity and mesh-face connectivity are not equivalent”的边界案例；如果放图，必须标注 face component residual。

**DLA voxel root / raw 是边界正面，sparse_close 系列是负结果。**

- selected `raw`：`occupancy_component_count=3`、`occupancy_lcr=0.999353`、`face_component_count=1`、`face_largest_component_ratio=1.000`。
- `sparse_close` 和 `sparse_close_bridge` 将 occupancy components 增至 11，LCR 降至约 0.887-0.888；`sparse_close_bridge` 虽改善 face LCR 到 0.943，但 occupancy 仍碎裂。
- 新导出的 `dla_raw_boundary/textured.glb` 只能说明 DLA 边界 candidate 可以 texture/export，不能作为 DLA 主正例。

**Volumetric coral / compete_fork_attach 是负面或弱边界。**

- `raw`：occupancy 9 components、LCR 0.687；face 10 components、LCR 0.739。
- `sparse_close`：occupancy 改善到 7 components、LCR 0.745，但仍碎。
- `mesh_bridge_smooth`：face 改善到 5 components、face LCR 0.938，但 occupancy 仍 9 components。
- 适合用来说明 mesh-level bridge/repair 可改善表面诊断，却不能保证 support-level invariant。

## 4. Flow / SDE 跑通状态

AgentDoc 计划中要求 Generative SDE / Flow stochastic growth 从低风险 masked local sampling 开始，网格包括 flow steps、blend alpha、mask dilation 和 per-depth schedule；正标准是保持 LCR、改善局部 surface/texture、不抹掉 branch/portal topology。

截至本轮本地证据，状态应写成：

- **已跑通的部分**：Trellis2 frozen sampler / texture route 对 selected projected meshes 可运行。四个 summary 都进入 latent / texture / PBR voxel 后处理，并导出 `status=ok` 的 GLB；bismuth/pyrite/coral 使用 8 steps，DLA boundary 使用 6 steps。
- **可作为方法叙事的部分**：`N_theta` 可以在论文方法中描述为 frozen Trellis2 flow/SDE/texture naturalization operator，但实验证据目前主要支持“selected mesh appearance export”和“低步数 sampler 兼容性”，不是系统性 topology repair。
- **不能作为正 claim 的部分**：full flow repair 仍按计划和总览中的结论处理为风险点，容易 wash out recursive topology；当前没有完整 flow-step / alpha / mask-dilation 网格和多 seed 统计可证明它优于 projection-stabilized grammar。
- **建议表述**：Masked naturalization remains a bounded local operator under grammar masks; connectivity is enforced and evaluated by support/projection metrics, not delegated to the sampler.

## 5. 可写入主文的正结果

1. **Connectivity-first non-tree evidence**

   bismuth hopper 可作为最稳正例：多个 method 同时达到 occupancy 和 face 完全连通。它支撑非树 / crystal-like scaffold 不只是树状 vine/tree 的偶然成功。

2. **Grammar-method interaction**

   coral case 中 `fork_side_attach+sparse_close` 明显优于 `compete_fork_attach` 系列，可用于说明递归生成语法中的 rule family 与 projection/repair operator 不是可交换后处理，必须共同设计。

3. **Texture/export compatibility**

   bismuth、pyrite、coral 的 true Trellis2 textured GLB 都成功导出；这可以放在结果图或补充视频/资产表中，作为 selected projected scaffold 的 asset pipeline 证据。

4. **Metric design necessity**

   DLA、pyrite、coral 都显示 occupancy connectivity 与 face connectivity 可能分歧；主文表必须同时报告 `occupancy_component_count`、`occupancy_lcr`、`face_component_count`、`face_largest_component_ratio`，不能只报单一 score。

## 6. 只可作为边界/负结果

1. **DLA raw boundary**

   `dla_raw_boundary/textured.glb` 是可导出的边界产物，但 occupancy 仍有 3 个组件。适合作为“mesh face 连通不等于 support 完全连通”的反例或 limitation。

2. **Sparse close 非单调**

   DLA root 上 `sparse_close*` 让 occupancy 明显变差；pyrite 上 `sparse_close` 也让 face components 增加。不能把 sparse closing 写成通用改进。

3. **Mesh bridge / smooth 不是主方法保证**

   coral compete case 的 `mesh_bridge_smooth` 改善 face 指标但 occupancy 不变坏点仍在；应放入 supplementary ablation 或 failure analysis。

4. **Flow repair 不能包装为已解决**

   计划和总览都提示 full flow repair 可能洗掉递归拓扑；当前没有足够网格证据改写这个判断。

## 7. 需要继续跑的缺口

1. **完整 root-level 结果补齐**

   method compare 摘要指出采样时 `gpu5_pyrite_lattice`、`gpu6_volumetric_dla_coral`、`gpu7_bismuth_hopper` 的 root-level `summary.json` / `selected_candidates.json` 尚未全部完成或尚未拉齐。后续应优先补齐这些文件，再决定最终主文表。

2. **Flow/SDE grid**

   需要真正按计划跑 flow steps `1/2/4/8`、blend alpha `0.1/0.25/0.5`、mask dilation `none/small/medium`、per-depth schedule 的小网格，并对 LCR、face components、local texture/surface QA 和 topology preservation 做表格。

3. **多 seed / 多 root 统计**

   目前四个 textured GLB 使用同一 seed `905092236`；method compare 也是单轮采样摘要为主。主文若做量化 claim，应补 mean/std 或至少 seed sensitivity。

4. **纹理 QA 与几何 QA 绑定**

   每个 textured figure 需要同时列出 mesh/source、occupancy metrics、face metrics、render warning、file size、texture size。避免“美图替代结构证据”。

5. **DLA/coral 的真实 frontier 指标**

   如果要把 DLA/coral 放进主文，应补 frontier attachment、orphan branch、porosity/cavity、path-to-root 或 fake-bridge label；否则只写 DLA-inspired / coral-like stress case。

6. **Pyrite/bismuth 的晶体属性指标**

   Bismuth 可进主文正图，但若要支持 crystal-like claim，还需 facet/contact/symmetry/cavity 或 orientation statistics；否则只写 bismuth-inspired connected scaffold。

## 8. 建议放入论文的最保守表述

可以写：

> On non-tree stress cases, our connectivity-first grammar produces selected projected scaffolds that remain compatible with native Trellis2 appearance export. Bismuth is fully connected at both voxel-support and face-component levels, while pyrite and coral expose useful boundary cases where support connectivity and surface connectivity diverge. These results motivate reporting both occupancy and mesh-face diagnostics rather than treating texture export as a topology certificate.

中文对应：

> 在非树 stress case 上，connectivity-first 递归语法可以产出可进入 Trellis2 原生纹理导出路径的 selected projected scaffold。Bismuth 是当前最强正例，voxel support 与 face component 均完全连通；pyrite 和 coral 则显示 support 连通性与表面连通性并不等价。因此论文应同时报告 occupancy 与 mesh-face 诊断，而不能把 textured GLB export 当作拓扑证明。

## 9. 当前优先级

- 主文正图优先：bismuth textured + neutral/support metric；coral fork sparse_close 作为修复型候选；pyrite 作为边界正例。
- 主文/补充边界：DLA raw boundary、DLA sparse_close failure、coral compete failure。
- 下一轮实验优先：补 root-level selected summaries、flow/SDE 小网格、多 seed、texture QA 绑定 metric table。
