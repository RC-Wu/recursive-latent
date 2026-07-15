---
title: 即时进展 Porous Mineral 纹理连通正线
date: 2026-05-09 13:45 +08
tags:
  - recursive-growth
  - trellis2
  - connectivity
  - non-tree
  - textured-glb
---

# 即时进展：Porous Mineral 纹理连通正线

## 一句话结论

今天中午的 `porous_mineral_depth_textured_showcase_20260509` 证明：非树类结果不要继续依赖 hard-DLA 后处理桥接，而应该转向“语法原生连通 scaffold + Trellis2 纹理/PBR 导出”。这条线现在是阶段性正结果，但还不是最终头图级晶体。

## 已完成

- 远端四卡完成 depth 1-4 的 Trellis2 textured GLB 导出；
- 本地拉回四个 `textured.glb`；
- 本地 Blender/Cycles 保留材质渲染完成；
- 生成论文/补充图候选：
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/porous_mineral_depth_textured_showcase_20260509.png`
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/porous_mineral_depth_textured_showcase_20260509.pdf`
- 写入技术 QA：
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/porous_mineral_depth_textured_qa_zh_20260509.md`

## 量化状态

在 `occupancy_resolution=64` 下，textured GLB 的体素连通最大连通分量比例分别是：

| depth | GLB occ LCR | 源 OBJ face LCR | 判断 |
|---:|---:|---:|---|
| 1 | 1.000 | 0.996 | 可用 |
| 2 | 0.994 | 0.994 | 可用 |
| 3 | 0.979 | 0.972 | 可用但需近景检查 |
| 4 | 0.989 | 0.970 | 可用但需近景检查 |

关键 caveat：GLB 的 raw face component 数非常高，不能直接作为漂浮碎块指标。这个现象更像 textured GLB 在 UV/material seam 处把三角面拆开。论文里应报告源 scaffold face connectivity + GLB occupancy connectivity，并补一个半径感知 surface voxelization 指标。

## 肉眼判断

优点：

- 主体没有 hard-DLA bridge 的长杆假桥；
- 保留材质渲染下有绿色、蓝色、黄褐色矿物感；
- depth 变化能展示递归团簇增加；
- 可作为非树类 connected scaffold 的方法行为图或补充图。

不足：

- 更像体素矿物/多孔块状簇，不像高质量铋晶体；
- 对称性和晶体阶梯边界不足；
- 还需要旋转/zoom-in 检查才能作为强视觉证据；
- 不适合作为头图核心 case。

## 对主线的影响

这次结果支持把论文 claim 收束为：

> 后处理桥接无法可靠修复碎块；连通性应作为递归语法状态不变量，在每层 scaffold 生成时就被维护，然后由 Trellis2 负责局部自然化与纹理/PBR 导出。

下一步应该做 `bismuth_step` / `pyrite` / `symmetric_crystal` 这样的显式对称晶体 grammar，而不是继续把 DLA bridge 当正线扩展。
