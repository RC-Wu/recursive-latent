# 主实验核心节修改笔记

日期：2026-05-11  
状态：draft notes；等待 V35 L-system textured GLB、统一白底图和完整 metrics 后局部写入 `paper_siga/main.tex`。

## 本节目标

核心实验节要回答一个问题：在严格 matched family targets 下，我们的方法是否能把传统递归家族的结构意图转化为可渲染、局部自然、可导出 textured GLB 的视觉资产。

## 推荐主张

- 我们不是声称传统 L-system / DLA / IFS / space colonization 本身失败，而是将它们作为受控递归目标。
- 贡献点应落在：grammar-owned local naturalization、projection/export stability、multi-scale camera-zoom visual evidence、post-GLB diagnostics。
- 四类主实验正例：
  - SC：V32 balanced/leafmass tree crown。
  - L-system：V35 branch-with-side-branches，等待远端 textured GLB。
  - IFS：HQ pyrite lattice stage04。
  - DLA：v14 branching table coral b。

## 指标展示建议

主表分三组：

1. **Connectivity/export readiness**
   - r0/r1/r2 surface voxel components 与 LCR。
   - GLB import/render success。
   - GLB size、vertex/face count。

2. **Mesh quality**
   - component count、largest component ratio。
   - boundary/degenerate/non-manifold diagnostics（若脚本可直接跑）。
   - face/vertex budget、surface area 或 occupied voxels。

3. **Family-specific diagnostics**
   - L-system：branch junction count、terminal sleeve/bud count、junction zoom target count。
   - SC：r1-connected、crown visual QA、tiny r0 island caveat。
   - DLA：r0 single connected、occupied voxel count、box dimension。
   - IFS：stage depth、mesh budget、ordered lattice visual evidence；当前 HQ metrics 无 r0/r1 LCR，需补或作为 visual row。

## 写作边界

- 不写 universal grammar。
- 不写 physical DLA/coral simulation。
- 不写 strict equivariance。
- 不写 2D seam SDEdit/inpaint backprojection 已闭合。
- 可以写 image generation / whole-object guide 被考虑，但最终证据来自 3D object-space grammar naturalization 和 GLB/PBR render。

## 待闭环后写入 main.tex 的内容

- 一段介绍 strict family targets 和四类 case。
- 一段解释 local naturalization 为什么是接缝/管感问题的解法，L-system V35 作为最直接例子。
- 一个四类 comparison figure 引用。
- 一个 metrics table 引用。
- 一段 limitations/caveat：SC/IFS tiny components、HQ pyrite metrics schema、DLA stylization、L-system 需 post-GLB QA。

