# 本地 mesh connectivity/repair 诊断 20260509

## 结论

- 输入资产数：4；评估方法数：7；导出 mesh 变体数：28。
- occupancy-primary 改善方法行：7；同时满足保守视觉保真阈值的方法行：7；最终按 case 选出的 safe candidates：2。
- 判定口径：primary connectivity 使用 surface/edge/centroid voxel occupancy 的 6-neighbor 连通性；视觉可用性用 mesh 三角面软件渲染的 contact sheet 和 voxel/面积/bbox 保留率联合判断。
- 本轮只有 radial4 系列在 before/after metrics 和视觉保守性上同时改善；DLA/scifi/tree-leaf/bismuth 多数在该 occupancy 分辨率下已经是单连通，不能据此宣称修复成功。
- 不把 largest_component 单独视为论文图安全修复；它常能让连通性指标变好，但会删除碎片结构，适合作为诊断下界。

## 每个 case 的改善候选

| case | source | selected method | before comps | after comps | before LCR | after LCR | retention(voxel/area/bbox) | judgement |
|---|---|---:|---:|---:|---:|---:|---|---|
| cache_bismuth_transform_fusion_steps8_tex2048_xformers | `visuals/cache_selected_texture_20260509/cache_bismuth_transform_fusion_steps8_tex2048_xformers/textured.glb` | bridge_to_largest | 4 | 1 | 0.751 | 1.000 | 1.00/1.00/1.00 | safe_candidate |
| cache_dla_masked_sampler_steps8_tex2048_xformers | `visuals/cache_selected_texture_20260509/cache_dla_masked_sampler_steps8_tex2048_xformers/textured.glb` | none_no_metric_improvement | 1 | 1 | 1.000 | 1.000 | 1.00/1.00/1.00 | not_improved |
| cache_radial_transform_fusion_steps8_tex2048_xformers | `visuals/cache_selected_texture_20260509/cache_radial_transform_fusion_steps8_tex2048_xformers/textured.glb` | none_no_metric_improvement | 1 | 1 | 1.000 | 1.000 | 1.00/1.00/1.00 | not_improved |
| cache_scifi_connected_steps8_tex2048_xformers | `visuals/cache_selected_texture_20260509/cache_scifi_connected_steps8_tex2048_xformers/textured.glb` | bridge_to_largest | 3 | 1 | 0.998 | 1.000 | 0.98/0.99/1.00 | safe_candidate |

## 方法安全性判断

| method | improved variants | safe candidates | 说明 |
|---|---:|---:|---|
| bridge_to_largest | 2 | 2 | 保留原结构但会引入细桥；适合可接受连接杆的工程图，不宜默认做美术图。 |
| conservative_hole_fill | 0 | 0 | 低风险清理；通常不解决远距离碎片。 |
| largest_component | 2 | 2 | 只推荐诊断使用；删除结构风险高。 |
| vertex_weld | 0 | 0 | 低风险但改善有限。 |
| voxel_bridge_close | 1 | 1 | 本轮只在 radial4 系列安全改善；其他 case 不能宣称成功，需逐图看 contact sheet。 |
| voxel_bridge_close_simplify | 1 | 1 | 本轮只在 radial4 系列安全改善；其他 case 不能宣称成功，需逐图看 contact sheet。 |
| voxel_close | 1 | 1 | 本轮 radial4 安全改善；其他 case 多为 no-op 或仅改变表面。 |

## 输出文件

- Metrics JSON: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/cache_selected_connectivity_repair_20260509/metrics.json`
- Metrics CSV: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/cache_selected_connectivity_repair_20260509/metrics.csv`
- Selection JSON: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/cache_selected_connectivity_repair_20260509/selection.json`
- Repaired meshes and contact sheets: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/cache_selected_connectivity_repair_20260509`

## 使用限制

- 本轮没有把任一修复结果声明为自动成功；只有同时改善 metrics 且 contact sheet 视觉保守的条目才标记为 paper_safe_candidate。
- GLB 纹理不会在 voxel remesh 后保留；这些结果主要用于几何连通性修复诊断。若要用于论文最终图，需要重新贴图或使用原 GLB 渲染作为材质参考。
