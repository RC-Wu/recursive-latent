---
title: Porous Mineral Depth Textured QA
date: 2026-05-09 13:40 +08
tags: [recursive-growth, trellis2, mesh-qa, non-tree, connectivity, pbr]
---

# Porous Mineral Depth Textured QA 2026-05-09

## 结论

`porous_mineral_depth_textured_showcase_20260509` 是目前非树类分支里比 hard-DLA bridge 更可用的一条正线。它的价值不是证明“真实 DLA / 铋晶体生成已经解决”，而是证明：

1. 语法原生连通 scaffold 比后处理 bridge 更可靠；
2. 同一 guide / 同一渲染协议下，深度 1-4 都能导出 Trellis2 textured GLB；
3. Blender/Cycles 保留材质渲染下没有出现 hard-DLA 那类明显漂浮碎块；
4. 递归深度增加能形成更丰富的块状/多孔矿物结构。

这组结果可以放在补充材料或方法行为图中作为“非树类连通 scaffold 的阶段性正例”。它还不能作为头图级晶体，因为目前视觉语义更像多孔体素矿物簇，而不是有强对称、阶梯边界和金属虹彩的铋晶体。

## 产物

- 远端 run：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/porous_mineral_depth_textured_showcase_20260509`
- 本地 GLB：`visuals/porous_mineral_depth_textured_showcase_20260509/*/textured.glb`
- Blender 渲染：`visuals/porous_mineral_depth_textured_showcase_20260509/renders`
- 论文/补充图候选：`paper_siga/figures/porous_mineral_depth_textured_showcase_20260509.{png,pdf}`
- 图生成脚本：`scripts/figures/compose_porous_mineral_depth_20260509.py`
- GLB 指标：`visuals/porous_mineral_depth_textured_showcase_20260509/porous_mineral_depth_textured_glb_metrics_occ64.{csv,json}`
- 源 OBJ 指标：`results/connected_coral_depth_cases_20260509/porous_mineral_depth/source_metrics_occ64.{csv,json}`

## 指标摘要

使用 `occupancy_resolution=64` 时，GLB 的顶点体素连通指标为：

| stage | GLB occ comps | GLB occ LCR | source face comps | source face LCR | box-count D |
|---|---:|---:|---:|---:|---:|
| 1 | 1 | 1.000 | 2 | 0.996 | 2.06 |
| 2 | 4 | 0.994 | 4 | 0.994 | 2.09 |
| 3 | 4 | 0.979 | 6 | 0.972 | 2.10 |
| 4 | 4 | 0.989 | 11 | 0.970 | 2.11 |

注意：GLB raw face component 数非常高，原因很可能是 textured GLB 导出时 UV/material seams 或三角面分块导致 face-graph 被拆散；它不能直接等价为资产视觉上的漂浮碎块。当前更可信的读法是：

- 源 OBJ 的 face LCR 表示语法 scaffold 的结构连通性；
- GLB 的 occupancy LCR 表示纹理导出后几何支持的粗体素连通性；
- 对 textured GLB 的 raw face comps 只作为导出诊断，不作为论文主指标。

`occupancy_resolution=96` 会把 stage 1/2 的细管/细连接打碎，因此对这类细结构不应只报告单一分辨率的 vertex-occupancy 连接性。后续最好实现“半径感知体素膨胀/mesh surface voxelization”的连通指标，避免把细连杆误判为不连通。

## 视觉 QA

人工查看 `porous_mineral_depth_render_contact.png` 与论文候选图后：

- 正面：主体整体可读，PBR/纹理已经有绿色、蓝色、黄褐色的矿物感；没有 hard-DLA bridge 的长杆假桥；
- 正面：stage 1-4 的深度变化可以看出更复杂的附着和团簇增长；
- 负面：结构仍偏“体素块状团簇”，晶体阶梯/对称性不足；
- 负面：stage 3/4 的局部颜色有漂移，语义不是严格 bismuth；
- 负面：阴影下方仍可能显得悬浮，需要后续决定是否加接地/支撑或改相机。

## 对论文故事的影响

这组结果支持一个更严格的 claim：

> 对于非树类递归资产，后处理桥接很容易制造假连接；把连通性作为 grammar state invariant，并在每层生成 connected scaffold，再交给 Trellis2 做 texture/PBR export，是更稳定的路线。

不应写成：

> 我们已经解决 DLA、晶体或所有非树类生成。

更好的写法是把 hard-DLA bridge smoke 放在失败诊断或消融中，把 porous mineral / connected coral / bismuth-like scaffold 放在“connected non-tree scaffold”小节里，并明确下一步是把对称群和阶梯晶体规则加入 grammar。

## 下一步

1. 为晶体类单独写对称/阶梯 grammar，而不是继续用圆球状 porous scaffold 冒充 bismuth。
2. 实现半径感知 voxel connectivity 或 surface voxelization 指标，避免高分辨率 vertex voxelization 对细连接过敏。
3. 对这组 GLB 做 zoom-in 或短旋转视频，检查近景下纹理是否仍可接受。
4. 尝试 `pyrite` / `bismuth_step` 两个更强几何先验的 connected scaffold，再走同一 Trellis2 texture pipeline。
