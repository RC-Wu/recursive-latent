# Coral/Octopus Warm 深度序列 QA 2026-05-09

## 结论

`coral_depth_octopus_warm_20260509_rerun1805` 是目前非树类方向里比较可用的一条正例线。它不是从硬 DLA 碎片事后修补出来的结果，而是 grammar-native connected volumetric coral/DLA-inspired scaffold，再通过 Trellis2 textured GLB/PBR 导出。已拉回并渲染的 stage 01-03 都是 mesh/textured GLB，不是 point cloud 或 matplotlib preview。

最重要的指标结论：已拉回的 stage 01-03 在 surface-voxel `64^3` 口径下都是单连通，`components_r0/r1/r2 = 1/1/1`，`LCR = 1.0/1.0/1.0`。

## 本地可视化

- GLB 与 summary 目录：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/coral_depth_octopus_warm_20260509_rerun1805`
- Blender 渲染目录：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/coral_depth_octopus_warm_20260509_rerun1805/renders_depth`
- contact sheet：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/coral_depth_octopus_warm_20260509_rerun1805/coral_octopus_depth_stage01_03_contact_20260509.png`
- 指标：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/coral_depth_octopus_warm_20260509_rerun1805/surface_metrics_occ64.csv`

![coral octopus stage 01-03](/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/coral_depth_octopus_warm_20260509_rerun1805/coral_octopus_depth_stage01_03_contact_20260509.png)

## 指标摘要

| stage | vertices loaded | faces | occupied @64 | components r0/r1/r2 | LCR r0/r1/r2 | box dim |
|---|---:|---:|---:|---:|---:|---:|
| 01 | 26,476 | 38,772 | 6,062 | 1 / 1 / 1 | 1.000 / 1.000 / 1.000 | 1.976 |
| 02 | 98,186 | 75,796 | 7,068 | 1 / 1 / 1 | 1.000 / 1.000 / 1.000 | 2.038 |
| 03 | 147,786 | 113,448 | 8,969 | 1 / 1 / 1 | 1.000 / 1.000 / 1.000 | 2.072 |

Stage 04 远端已成功生成，但本地传输在 5.7MB 左右卡住，已把本地不完整文件标为 `textured.glb.partial`，不作为有效 GLB 使用。远端 stage 04 摘要：68,146 vertices，136,964 faces，2,480 shape-SLAT tokens，700,053 PBR voxel tokens，GLB 7.73MB，status ok。

## 肉眼 QA

正面：

- stage 01-03 的主干、分叉和端点团块在多个视角下都是连续结构，没有明显漂浮大碎块。
- PBR/纹理已经有红褐色主干与灰白端点的材质差异，比单色 mesh 更适合做资产展示。
- 随 depth 增加，整体从简化分叉过渡到更密集的分叉/端点结构，适合做“同条件 depth 控制展示”。

风险：

- 语义更接近 octopus/coral-inspired scaffold，而不是真实珊瑚生长或真实 DLA。
- stage 03 局部有体素化块感和表面小凸块，主文中需要配 neutral render/zoom-in，避免只靠远景材质掩盖结构问题。
- 当前 contact sheet 顶部标签排版略粗糙，若进论文需要重排成正式 figure。

## 论文使用建议

可以支持的 claim：

- `A grammar-native connected scaffold can preserve root-connected recursive support across depth while remaining compatible with Trellis2 textured GLB export.`
- `The non-tree/coral-DLA-inspired line is better handled by connected support generation than by post-hoc bridge repair.`

不能支持的 claim：

- 不能写真实 DLA、真实 coral physics、真实生物生长模拟。
- 不能说 raw face-level topology 完全 clean；当前主指标应使用 surface/occupancy-level connectivity。
- 不能把 stage 04 当作已本地 QA 的结果，直到完整 GLB 拉回并渲染。

## 下一步

1. 重新拉取 stage 04 或改用压缩/分块传输，补齐完整 depth 01-04 contact sheet。
2. 对 stage 02-04 补 root/junction/tip zoom-in，确认没有隐藏漂浮碎片。
3. 把 `coral_stage4_guide_sweep_rerun1820` 的四个 guide 结果拉回筛选，选择一个最适合论文/补充材料的 stage-4 PBR 版本。
4. 在论文里把它放在 “non-tree stress positive / connected scaffold” 小节，而不是放在 DLA bridge 正例里。
