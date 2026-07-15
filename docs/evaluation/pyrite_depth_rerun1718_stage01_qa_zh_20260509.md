# Pyrite depth rerun1718 stage01 本地 QA

时间：2026-05-09 17:31 +08

## 结论

`pyrite_depth_textured_showcase_20260509_rerun1718` 在远端四个 stage 均已成功导出 Trellis2 textured GLB。由于当前本地到 `a100-2` 的大文件传输异常慢，本轮只完整拉取并检查了 stage01；stage02/03/04 仍保留在远端，后续需要用更稳的传输窗口或替代方案拉取。

stage01 是正向结果：它是完整 textured mesh，不是点云或单色材质；Blender preserve-material render 能读出黄铁矿/晶格式块状结构；surface-voxel 连通性在 `r0/r1/r2` 均为单组件。

## 本地视觉证据

- contact sheet: `visuals/pyrite_depth_textured_showcase_20260509_rerun1718/pyrite_stage01_blender_contact_20260509.png`
- iso render: `visuals/pyrite_depth_textured_showcase_20260509_rerun1718/renders/pyrite_depth_stage01_iso.png`
- front render: `visuals/pyrite_depth_textured_showcase_20260509_rerun1718/renders/pyrite_depth_stage01_front.png`
- side render: `visuals/pyrite_depth_textured_showcase_20260509_rerun1718/renders/pyrite_depth_stage01_side.png`

## Stage01 指标

来源：`visuals/pyrite_depth_textured_showcase_20260509_rerun1718/surface_metrics_occ64.csv`

| metric | value |
|---|---:|
| vertices | 63,561 |
| faces | 87,944 |
| occupied voxels @64 | 17,353 |
| components r0 | 1 |
| LCR r0 | 1.000 |
| components r1 | 1 |
| LCR r1 | 1.000 |
| components r2 | 1 |
| LCR r2 | 1.000 |
| box dimension 32-96 | 2.024 |

## 远端四阶段导出状态

`$ROOT/results/pyrite_depth_textured_showcase_20260509_rerun1718`

| stage | status | mesh vertices | faces | shape-SLAT tokens | PBR voxel tokens | GLB size |
|---|---|---:|---:|---:|---:|---:|
| 01 | ok | 43,656 | 87,944 | 4,300 | 1,320,410 | 3.47MB |
| 02 | ok | 117,162 | 240,872 | 5,919 | 1,960,016 | 13.61MB |
| 03 | ok | 217,298 | 450,312 | 6,143 | 2,283,479 | 25.78MB |
| 04 | ok | 232,568 | 482,348 | 6,736 | 2,409,034 | 27.49MB |

## 研究解释

这条线比 hard-DLA post-hoc bridge 更适合做论文正例，因为它从 grammar-native connected crystal/pyrite scaffold 出发，再走 Trellis2 texturing/PBR export。stage01 已经证明“规则晶格 scaffold + Trellis2 texture”可以得到视觉上可读、指标上连通的 textured mesh。

当前还不能声称完整 depth sequence 已通过本地视觉 QA，因为 stage02/03/04 尚未完整拉到本地。后续需要补：

1. stage02/03/04 的完整 GLB 拉取；
2. Blender preserve-material 三视图和 zoom-in；
3. 四阶段 surface-voxel metrics；
4. 和已有 `coral_depth_textured_showcase_20260509_rerun1640` 一起比较，决定哪条 depth sequence 进入主文。

## 传输问题

`scp` 和 `rsync --partial` 对 10MB 以上 GLB 都非常慢，`ssh cat > local` 也没有明显改善。已避免把 partial 文件当作有效 GLB：

- stage02 的未完成传输文件已重命名为 `textured.glb.partial`；
- 之前 connectivity-first 的两个 partial 文件也仍以 `.partial` 标记。
