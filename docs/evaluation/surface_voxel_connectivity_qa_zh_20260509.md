# Surface-Voxel 连通性诊断 QA（2026-05-09）

## 目的

这次补充的指标解决一个论文评审会追问的问题：Trellis2 textured GLB 的 raw face component 数量很高，但这经常来自 UV/material seam 和导出三角面拆分，不能直接说明资产在视觉上是碎块。因此新增 surface-sampled voxel connectivity：

1. 从 mesh/GLB 表面采样点；
2. 在规范化 bounding box 中 voxelize；
3. 做 6-neighborhood connected component；
4. 同时报告 strict radius-0 和 seam/alias-tolerant radius-1。

这个指标是 renderability/connectivity diagnostic，不是 watertight topology proof。

## 文件

- 脚本：`assets/surface_voxel_connectivity_20260509.py`
- 图脚本：`scripts/figures/compose_surface_voxel_connectivity_20260509.py`
- 数据：`results/surface_voxel_connectivity_20260509/surface_voxel_connectivity_summary.{csv,json}`
- 图：`paper_siga/figures/surface_voxel_connectivity_metric_20260509.{png,pdf}`

## 关键结论

| case | strict radius-0 result | radius-1 result | 论文使用方式 |
|---|---|---|---|
| Pyrite HQ GLB depth 1-4 | 全部 `1 comp, LCR=1.000` | 全部 `1 comp, LCR=1.000` | 主晶体/对称正例 |
| Bismuth HQ GLB depth 1-4 | 全部 `1 comp, LCR=1.000` | 全部 `1 comp, LCR=1.000` | 结构可用但材质弱，保留为 guide-sensitivity |
| Porous mineral GLB depth 1-4 | `1/4/4/4` comps，LCR 最低 `0.979` | 全部 `1 comp, LCR=1.000` | 非树 connected scaffold 正例，但附 surface seam caveat |

## 和 raw face component 的关系

raw GLB face components 仍然保留为导出诊断，但不应作为主连通性 claim。主文中建议这样写：

- **Structural claim**：source scaffold / projected support 用 occupancy/root-reachability 指标。
- **Textured asset claim**：GLB export + Blender render + surface-sampled voxel connectivity。
- **Topology caveat**：raw face graph、non-manifold、hole filling 等保留为 caveat 或 supplement。

## 当前论文动作

已更新 `paper_siga/main.tex`：

- metrics 小节加入 surface-sampled voxel connectivity；
- 新增 `fig:surface-voxel-connectivity`；
- crystal 主 depth figure 替换为 `pyrite_hq_depth_textured_showcase_20260509.pdf`；
- `crystal_stage4_guide_sweep` caption 改为 Pyrite 主正例、Bismuth 为 guide sensitivity。

`paper_siga/main.pdf` 已成功编译。
