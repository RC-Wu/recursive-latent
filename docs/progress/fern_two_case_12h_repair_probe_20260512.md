# 本地 mesh connectivity/repair 诊断 20260509

## 结论

- 输入资产数：4；评估方法数：7；导出 mesh 变体数：28。
- occupancy-primary 改善方法行：28；同时满足保守视觉保真阈值的方法行：26；最终按 case 选出的 safe candidates：4。
- 判定口径：primary connectivity 使用 surface/edge/centroid voxel occupancy 的 6-neighbor 连通性；视觉可用性用 mesh 三角面软件渲染的 contact sheet 和 voxel/面积/bbox 保留率联合判断。
- 本轮只有 radial4 系列在 before/after metrics 和视觉保守性上同时改善；DLA/scifi/tree-leaf/bismuth 多数在该 occupancy 分辨率下已经是单连通，不能据此宣称修复成功。
- 不把 largest_component 单独视为论文图安全修复；它常能让连通性指标变好，但会删除碎片结构，适合作为诊断下界。

## 每个 case 的改善候选

| case | source | selected method | before comps | after comps | before LCR | after LCR | retention(voxel/area/bbox) | judgement |
|---|---|---:|---:|---:|---:|---:|---|---|
| v26h_fern_attached_pinnae_depth_04_mesh | `results/fern_two_case_recursive_remote_20260512h_pull/raw/fern_hierarchical_frond_j_d4_20260512h/v26h_fern_attached_pinnae/depth_04/mesh.obj` | voxel_bridge_close | 14 | 2 | 0.932 | 0.992 | 2.15/1.88/1.06 | safe_candidate |
| v26h_fern_attached_pinnae_depth_04_mesh_02 | `results/fern_two_case_recursive_remote_20260512h_pull/raw/fern_tiered_frond_i_d4_20260512h/v26h_fern_attached_pinnae/depth_04/mesh.obj` | voxel_bridge_close | 14 | 1 | 0.885 | 1.000 | 2.26/2.40/1.06 | safe_candidate |
| v26h_fiddlehead_attached_surface_buds_depth_04_mesh | `results/fern_two_case_recursive_remote_20260512h_pull/raw/fiddlehead_log_dense_j_d4_20260512h/v26h_fiddlehead_attached_surface_buds/depth_04/mesh.obj` | voxel_bridge_close | 10 | 1 | 0.962 | 1.000 | 2.10/2.01/1.06 | safe_candidate |
| v26h_fiddlehead_attached_surface_buds_depth_04_mesh_04 | `results/fern_two_case_recursive_remote_20260512h_pull/raw/fiddlehead_log_spiral_i_d4_20260512h/v26h_fiddlehead_attached_surface_buds/depth_04/mesh.obj` | voxel_close | 2 | 1 | 0.999 | 1.000 | 1.68/1.79/1.03 | safe_candidate |

## 方法安全性判断

| method | improved variants | safe candidates | 说明 |
|---|---:|---:|---|
| bridge_to_largest | 4 | 4 | 保留原结构但会引入细桥；适合可接受连接杆的工程图，不宜默认做美术图。 |
| conservative_hole_fill | 4 | 4 | 低风险清理；通常不解决远距离碎片。 |
| largest_component | 4 | 2 | 只推荐诊断使用；删除结构风险高。 |
| vertex_weld | 4 | 4 | 低风险但改善有限。 |
| voxel_bridge_close | 4 | 4 | 本轮只在 radial4 系列安全改善；其他 case 不能宣称成功，需逐图看 contact sheet。 |
| voxel_bridge_close_simplify | 4 | 4 | 本轮只在 radial4 系列安全改善；其他 case 不能宣称成功，需逐图看 contact sheet。 |
| voxel_close | 4 | 4 | 本轮 radial4 安全改善；其他 case 多为 no-op 或仅改变表面。 |

## 输出文件

- Metrics JSON: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/fern_two_case_recursive_remote_20260512h_repair_probe/metrics.json`
- Metrics CSV: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/fern_two_case_recursive_remote_20260512h_repair_probe/metrics.csv`
- Selection JSON: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/fern_two_case_recursive_remote_20260512h_repair_probe/selection.json`
- Repaired meshes and contact sheets: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/fern_two_case_recursive_remote_20260512h_repair_probe`

## 使用限制

- 本轮没有把任一修复结果声明为自动成功；只有同时改善 metrics 且 contact sheet 视觉保守的条目才标记为 paper_safe_candidate。
- GLB 纹理不会在 voxel remesh 后保留；这些结果主要用于几何连通性修复诊断。若要用于论文最终图，需要重新贴图或使用原 GLB 渲染作为材质参考。
