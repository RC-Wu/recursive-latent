# Bismuth depth rerun1729 本地 QA

时间：2026-05-09 17:40 +08

## 结论

`bismuth_depth_textured_showcase_20260509_rerun1729` 是目前晶体/对称线里最完整的一组 mesh/textured-mesh depth sequence：四个 stage 都完整拉到本地，四个 stage 都是 Trellis2 textured GLB，Blender preserve-material 渲染可读，surface-voxel 连通性全部为单组件。

这组结果比 hard-DLA bridge/cache 更适合进入主文或 supplement 的正例，因为它是 grammar-native connected scaffold，而不是事后把碎块硬连起来。

## 本地视觉证据

- 四阶段 contact sheet: `visuals/bismuth_depth_textured_showcase_20260509_rerun1729/bismuth_depth_blender_contact_20260509.png`
- 四阶段 Blender render: `visuals/bismuth_depth_textured_showcase_20260509_rerun1729/renders_depth/stage{01,02,03,04}_iso.png`
- paper figure candidate:
  - `paper_siga/figures/bismuth_depth_textured_showcase_rerun1729_20260509.png`
  - `paper_siga/figures/bismuth_depth_textured_showcase_rerun1729_20260509.pdf`

## 指标

来源：`visuals/bismuth_depth_textured_showcase_20260509_rerun1729/surface_metrics_occ64.csv`

| stage | vertices | faces | occupied @64 | comp r0 | LCR r0 | comp r1 | LCR r1 | comp r2 | LCR r2 | box dim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 01 | 37,696 | 44,592 | 14,300 | 1 | 1.000 | 1 | 1.000 | 1 | 1.000 | 2.037 |
| 02 | 39,685 | 46,980 | 15,117 | 1 | 1.000 | 1 | 1.000 | 1 | 1.000 | 2.038 |
| 03 | 43,397 | 50,436 | 16,297 | 1 | 1.000 | 1 | 1.000 | 1 | 1.000 | 2.032 |
| 04 | 47,055 | 54,036 | 17,460 | 1 | 1.000 | 1 | 1.000 | 1 | 1.000 | 2.029 |

## 视觉判断

优点：

- 全部是 mesh/Textured GLB，不是点云或 matplotlib；
- 纹理/PBR 比单色程序材质更接近可展示 asset；
- 四阶段在同一 grammar family、同一 guide、同一 render protocol 下展示 depth 控制；
- stage 之间占用体素和 mesh 复杂度递增，连通性保持不变。

局限：

- 颜色偏绿，bismuth 语义不如真实彩虹氧化铋鲜明；
- 几何更像规则递归建筑/晶体装饰结构，不应写成物理晶体生长；
- 当前 contact sheet 没有 zoom-in，后续若进主文应补局部递归细节 inset。

## 论文使用建议

可作为 “crystal-like / symmetry-aware recursive scaffold” 的正例，支撑以下 claim：

1. PS-RSLG 可以在非植物、规则/对称/晶体样结构上保持 connected support；
2. Trellis2 texture export 能把 connected scaffold 变成可渲染 PBR/textured mesh；
3. depth 控制可以增加局部复杂度而不破坏 surface-voxel connectivity。

不建议声称：

- 真实晶体生长或物理 DLA；
- raw mesh topology watertight；
- bismuth 材质已经达到头图最终质量。

下一步：用 HQ 2048 texture/warm bismuth guide 再跑一轮，如果颜色更像铋晶体，可替换当前 1024 版本作为主文图。
