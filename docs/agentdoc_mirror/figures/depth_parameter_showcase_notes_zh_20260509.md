# depth / parameter showcase 图说明（2026-05-09）

图文件：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/depth_parameter_showcase_20260509.png`

生成脚本：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/generate_depth_parameter_showcase_20260509.py`

## 目的

该图是 **method-control visualization**，用于展示同一 case 在递归 depth 增加时的几何变化，以及固定 depth 下不同 grammar / control 参数带来的形态差异。它不是 ablation，不用于比较最终质量，也不用于证明某个 depth 或 control 更优。

图采用 mesh triangle render，白底、固定相机、统一材质和统一 panel 排版；没有使用点云，也没有使用 texture render。

## Panel 构成

上排：fixed-case depth progression。

- case：`vine_d5_projected_compete`
- control / grammar：`compete`
- 展示项：stage/depth 1, 2, 3, 4
- 用途：展示在同一 vine case 和同一 compete control 下，递归迭代会改变枝蔓方向、密度和局部分叉。

下排：fixed-depth parameter/control sweep。

- case family：vine / root recursive mesh
- fixed depth：`depth_03`
- pruning threshold：`min_vertices=300`
- controls：`compete`, `fork-side`, `radial-4`, `portal`
- 用途：展示同一 depth 条件下，control 选择会改变空间展开方式和局部重复结构。

## 数据来源

上排 mesh：

| panel | OBJ | vertices | faces |
|---|---|---:|---:|
| depth 1 | `visuals/siga_night_20260508/siga_projected_recursive_loop_0715/vine_d5_projected_compete/stage_01/projected/vine_d5_projected_compete_stage_01/mesh_pruned.obj` | 181730 | 377432 |
| depth 2 | `visuals/siga_night_20260508/siga_projected_recursive_loop_0715/vine_d5_projected_compete/stage_02/projected/vine_d5_projected_compete_stage_02/mesh_pruned.obj` | 183503 | 399336 |
| depth 3 | `visuals/siga_night_20260508/siga_projected_recursive_loop_0715/vine_d5_projected_compete/stage_03/projected/vine_d5_projected_compete_stage_03/mesh_pruned.obj` | 188403 | 429002 |
| depth 4 | `visuals/siga_night_20260508/siga_projected_recursive_loop_0715/vine_d5_projected_compete/stage_04/projected/vine_d5_projected_compete_stage_04/mesh_pruned.obj` | 189956 | 444214 |

下排 mesh：

| panel | OBJ | vertices | faces |
|---|---|---:|---:|
| compete | `visuals/siga_night_20260508/siga_vine_projection_pruning_0700/minv_300/vine_compete_d3/mesh_pruned.obj` | 186461 | 387414 |
| fork-side | `visuals/siga_night_20260508/siga_vine_projection_pruning_0700/minv_300/vine_fork_side_d3/mesh_pruned.obj` | 246993 | 479102 |
| radial-4 | `visuals/siga_night_20260508/siga_vine_projection_pruning_0700/minv_300/vine_radial4_d3/mesh_pruned.obj` | 65886 | 122962 |
| portal | `visuals/siga_night_20260508/siga_vine_projection_pruning_0700/minv_300/vine_portal_d3/mesh_pruned.obj` | 73758 | 152336 |

## Trellis2 / procedural 状态

这张图没有使用新生成的 procedural placeholder。所有 panel 都来自现有 OBJ mesh。

上排 `vine_d5_projected_compete/config.json` 记录的 root mesh 为远端实验中的 `trellis2_dinov3_min.obj`；各 stage 的 `raw/summary.json` 标记 `kind=trellis2_recursive_slat_grammar_workflow`。因此，上排可描述为基于 Trellis2 mesh seed 的 recursive SLAT / grammar workflow 输出，再经过 connected-component pruning 得到的 mesh-only 可视化。

下排来自 `siga_vine_projection_pruning_0700/minv_300/summary.json`，源路径对应 `siga_vine_root_recursion/vine_direct_gpu4_20260508_0615/.../depth_03/mesh.obj`，并经 `min_vertices=300` component pruning。它是现有 recursive vine/root mesh 结果的 control sweep，不是 Trellis2 textured result。

整张图不展示 Trellis2 texture / GLB 材质质量。渲染材质是脚本中的 neutral shaded triangle material，仅用于几何可读性。

## 支持的 claim

可支持：

- 在同一 case 和相同 control 下，递归 depth / stage 会产生可观察的几何演化。
- 在固定 depth 下，不同 grammar / control 会产生不同的空间组织和重复模式。
- 方法输出为 triangle mesh，可进行 mesh-only render，不依赖点云截图。

不应支持：

- 不应写成 ablation 或 quantitative comparison。
- 不应声称这些 panel 是最终 paper-quality textured Trellis2 results。
- 不应声称某个 control 在质量上优于另一个 control；该图只展示可控性和形态差异。

## 可用性判断

当前 PNG 可用于论文草稿中的 method-control / qualitative showcase 小图。它适合放在方法或结果支线中，作为“same case across depth”和“same depth across controls”的直观证据。

风险是图中几何来自已有实验的 pruned mesh，部分 control panel 仍有碎片化组件；如放主文，应在 caption 中写明是 neutral mesh visualization / method-control visualization，而不是 final textured asset comparison。
