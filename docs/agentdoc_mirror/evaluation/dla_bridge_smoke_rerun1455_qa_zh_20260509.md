# DLA Bridge Smoke 复测 QA（2026-05-09 15:18）

## 目的

这次复测专门回答用户指出的核心问题：DLA/晶体/非树线不能是碎块，post-hoc bridge 是否能把 hard-DLA 修成可用 asset？

结论：**不能把 post-hoc bridge 当主路线**。它可以改善 face-level diagnostic，但 occupancy/support connectivity 仍然碎，甚至在 volumetric-DLA 上会把原本单连通 support 破坏成多组件。当前更可靠的路线是 grammar-native / attachment-aware / volumetric connected scaffold。

## 文件

- 远端结果：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/dla_bridge_smoke_stage1_20260509_rerun1455`
- 本地结果：`visuals/dla_bridge_smoke_stage1_20260509_rerun1455`
- Blender renders：`visuals/dla_bridge_smoke_stage1_20260509_rerun1455/renders`
- 论文图：`paper_siga/figures/dla_bridge_smoke_stage1_rerun1455_20260509.{png,pdf}`
- 图脚本：`scripts/figures/compose_dla_bridge_smoke_rerun1455_20260509.py`

## 指标

所有数值是 final mesh projection 后的指标。

| case | method | occupancy components | occupancy LCR | face components | face LCR | 判断 |
|---|---|---:|---:|---:|---:|---|
| hard DLA | raw | 4 | 0.380 | 4 | 0.378 | 失败，明显碎块 |
| hard DLA | sparse close bridge | 5 | 0.591 | 3 | 0.811 | face 变好但 support 仍碎，不能作为正例 |
| volumetric DLA | raw | 1 | 1.000 | 3 | 0.521 | 当前最强正向路线 |
| volumetric DLA | sparse close bridge | 7 | 0.873 | 2 | 0.990 | face 变好但 occupancy 变差，说明过桥接会损伤 support |

## 视觉判断

![DLA bridge smoke rerun](/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/dla_bridge_smoke_stage1_rerun1455_20260509.png)

- hard-DLA raw 是碎块，不能用。
- hard-DLA sparse bridge 仍然有漂浮/长杆/假连接感，不能用作正例。
- volumetric-DLA raw 虽然 face component 不完美，但 occupancy support 是单连通，且视觉上读作一个整体 scaffold。
- volumetric-DLA sparse bridge 的 face LCR 很高，但 occupancy 变成 7 个组件，这正好证明不能只看 face metric。

## 论文用法

主文应该把这张图作为 **boundary / negative diagnostic**，不是成功图：

- 支持 claim：post-hoc repair 不是解决 DLA 碎块的主路线；
- 支持 claim：PS-RSLG 需要 attachment-aware / grammar-native connected support；
- 不支持 claim：我们已经解决了真实 DLA 物理生长；
- 不支持 claim：bridge/cache 一定能提升连通性；
- 不支持 claim：face component 指标可以单独作为结构质量指标。

`paper_siga/main.tex` 已加入 `fig:dla-bridge-smoke-rerun`，当前 PDF 编译成功，长度 25 页。

## 下一步

1. 不再扩展 hard-DLA bridge 作为正例。
2. DLA/coral 线继续优先做 grammar-native volumetric connected scaffold，并配合 texture/PBR。
3. 如果要测试 cache，应明确当成 cache/repair diagnostic，不要在视觉没有通过时写成主贡献。
