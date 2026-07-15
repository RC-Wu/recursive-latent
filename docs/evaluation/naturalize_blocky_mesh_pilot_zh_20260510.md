# blocky mesh naturalization CPU pilot 评估（2026-05-10）

## 目标

本轮只做本地 CPU pilot：把 DLA/frontier/radial/transform mesh 的表面支撑转成 voxel occupancy，在局部做 dilation、closing、可选最短 voxel bridge 和轻量平滑，再用 marching cubes 重建 OBJ。目标是观察它是否能减少 chunk/fragment 外观，同时保留连通支撑；不把它包装成最终论文方法或强 claim。

脚本：

- `assets/naturalize_blocky_mesh_pilot_20260510.py`
- 输出目录：`results/naturalize_blocky_mesh_pilot_20260510/`
- 可视化：`visuals/naturalize_blocky_mesh_pilot_20260510/before_after_contact_sheet.png`

## 运行设置

```bash
python3 assets/naturalize_blocky_mesh_pilot_20260510.py \
  --input results/strict_matched_task_targets_20260510/dla_coral_cluster_900/traditional_target.obj \
  --input results/strict_matched_task_targets_20260510/dla_aniso_crystal_800/traditional_target.obj \
  --input results/strict_matched_task_targets_20260510/dla_frontier_sheet_700/traditional_target.obj \
  --input visuals/connected_scaffold_v2_textured_glb_hq_20260509/volumetric_dla_coral_octopus_hq_steps8_tex2048_xformers/textured.glb \
  --input visuals/public_guide_textured_glb_20260509c/transform_radial4_pyrite_steps8_tex2048_xformers/textured.glb \
  --out-dir results/naturalize_blocky_mesh_pilot_20260510 \
  --resolution 88 \
  --sample-count 90000 \
  --initial-dilate 1 \
  --close-iterations 1 \
  --smooth-sigma 0.45 \
  --bridge-radius 1 \
  --simplify-faces 70000
```

Blender 当前不在 `PATH`，所以本轮没有生成 Blender render；改用已有 `assets/render_mesh_contact_sheet.py` 生成软件 shaded contact sheet。

## 结果表

| case | occupancy comps | largest ratio | occupied voxels | faces | area retention | bbox retention | 初步判断 |
|---|---:|---:|---:|---:|---:|---:|---|
| `dla_aniso_crystal_800` | 1 -> 1 | 1.0000 -> 1.0000 | 20533 -> 30354 | 9600 -> 35026 | 1.046 | 1.072 | 已连通；形体变厚，主要是去块状平滑 pilot |
| `dla_coral_cluster_900` | 1 -> 1 | 1.0000 -> 1.0000 | 46357 -> 66822 | 10800 -> 67954 | 0.736 | 1.065 | 已连通；局部填补明显，可能削弱枝状细节 |
| `dla_frontier_sheet_700` | 1 -> 1 | 1.0000 -> 1.0000 | 91273 -> 123696 | 8400 -> 89560 | 0.460 | 1.067 | 已连通；sheet 被重建为厚壳，论文图风险较高 |
| `volumetric_dla_coral_octopus_hq...` | 1 -> 1 | 1.0000 -> 1.0000 | 21783 -> 30238 | 180132 -> 33896 | 0.888 | 1.066 | 可作为 GLB repair/simplify 预处理候选，但不是连通性改进证据 |
| `transform_radial4_pyrite...` | 118 -> 8 | 0.9649 -> 0.9983 | 100580 -> 176659 | 705768 -> 275446 | 6.228 | 1.057 | 连通碎片显著下降，但面积膨胀过大；只能算诊断候选 |

完整指标见：

- `results/naturalize_blocky_mesh_pilot_20260510/summary.csv`
- `results/naturalize_blocky_mesh_pilot_20260510/summary.json`

## 是否有帮助

有帮助，但范围有限：

- 对 textured radial/transform GLB，voxel bridge + closing 能把很多小碎片并回主体，`transform_radial4_pyrite` 的 occupancy components 从 118 降到 8，largest ratio 从 0.9649 到 0.9983。
- 对这些 traditional DLA/frontier OBJ，本轮 occupancy 在 dilation 后本来就是单连通，所以指标上没有“连通性修复”收益；它的作用更接近 blocky support 的重采样和平滑。
- 对 DLA/frontier，marching-cubes 重建会改变表面表达：能缓解硬块边界，但也会让细枝、sheet 和局部空隙变厚或被吞掉。
- 对 HQ DLA GLB，输出面数从 180132 降到 33896，面积和 bbox 保留尚可，适合作为后续 mesh cleanup 的候选输入；但这不证明生成结果更自然。

## 是否 paper-usable

当前不建议作为论文主结果或方法 claim 使用。

可以使用的定位：

- 作为 appendix/engineering note：说明我们做过 masked/local naturalization pilot，能在部分 radial/transform GLB 上降低 occupancy fragmentation。
- 作为视觉资产预处理候选：对单个 case 人工筛选 before/after，如果形体语义没有被破坏，再进入正式 render。
- 作为后续方法雏形：需要加入 mask、局部半径约束、体积/面积变化阈值、中心线或骨架保护，才能避免把 frontier sheet 和 DLA 细枝过度膨胀。

不能使用的定位：

- 不能声称这是通用 mesh repair。
- 不能声称它 preserves geometry，只能说 preserves connected support in voxel occupancy under chosen resolution。
- 不能把 radial4 的改进直接外推到 DLA/non-tree 全部样本。

## 下一步建议

1. 加入局部 mask：只对小组件、接触缝、低置信 voxel 边界做 closing/bridge，不对全局表面做 dilation。
2. 加入保守阈值：如果 `area_retention > 1.5` 或 `bbox_retention > 1.1`，自动标记为 shape-risk。
3. 对 DLA 使用骨架保护：先提取粗 skeleton 或主干 voxel，再只填补主干附近的一到两个 voxel 半径。
4. 对论文图只保留人工 QA 后的 case；本轮最接近候选的是 `volumetric_dla_coral_octopus_hq...` 的简化清理版，不是 `transform_radial4_pyrite...` 的膨胀版。
