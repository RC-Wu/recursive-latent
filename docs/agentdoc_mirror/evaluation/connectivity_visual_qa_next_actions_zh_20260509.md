# Mesh 连通性可视化 QA 与下一步动作 20260509

## 证据口径

本支线只把 mesh triangle render 作为最终视觉证据，不把点云图、scatter preview、occupancy slice 或 matplotlib 点状预览作为论文主图证据。点云/voxel 图可以用于定位问题，但不能单独证明 mesh 可渲染、几何连续或语义清楚。

本地修复结果中的以下 15 张 contact sheet 均按 `connectivity_repair_local_zh_20260509.md` 的口径视为 mesh 三角面软件渲染 contact sheet，用于 before/after 视觉保守性检查：

- `results/connectivity_repair_local_20260509/contact_sheets/non_tree_recursive_20260508_meshes_scifi_module_projected_translate_stage03_contact.png`
- `results/connectivity_repair_local_20260509/contact_sheets/porous_container_compete_stage03_bismuth_steps8_tex2048_xformers_contact.png`
- `results/connectivity_repair_local_20260509/contact_sheets/scifi_module_projected_translate_stage03_pyrite_steps8_tex2048_xformers_contact.png`
- `results/connectivity_repair_local_20260509/contact_sheets/dla_fork_side_octopus_steps8_tex2048_xformers_contact.png`
- `results/connectivity_repair_local_20260509/contact_sheets/lsystem_fork_side_parthenocissus_steps8_tex2048_xformers_contact.png`
- `results/connectivity_repair_local_20260509/contact_sheets/transform_radial4_pyrite_steps8_tex2048_xformers_contact.png`
- `results/connectivity_repair_local_20260509/contact_sheets/dla_fork_side_pyrite_steps8_tex2048_xformers_contact.png`
- `results/connectivity_repair_local_20260509/contact_sheets/dla_side_bismuth_steps8_tex2048_xformers_contact.png`
- `results/connectivity_repair_local_20260509/contact_sheets/transform_radial4_bismuth_steps8_tex2048_xformers_contact.png`
- `results/connectivity_repair_local_20260509/contact_sheets/dla_side_octopus_steps8_tex2048_xformers_contact.png`
- `results/connectivity_repair_local_20260509/contact_sheets/lsystem_fork_bismuth_steps8_tex2048_xformers_contact.png`
- `results/connectivity_repair_local_20260509/contact_sheets/siga_night_20260508_projection_pruning_compete_0550_dla_compete_fork_d4_pruned_contact.png`
- `results/connectivity_repair_local_20260509/contact_sheets/siga_night_20260508_projection_pruning_compete_0550_masked_tree_compete_fork_s1_a025_d3_pruned_contact.png`
- `results/connectivity_repair_local_20260509/contact_sheets/siga_night_20260508_selected_meshes_dla_fork_side_s2_a0p25_d3_contact.png`
- `results/connectivity_repair_local_20260509/contact_sheets/siga_night_20260508_selected_meshes_transform_radial4_d3_contact.png`

这些 sheet 可用于 QA 结论，但还不是最终论文图。最终论文视觉证据仍应使用统一相机、统一光照、统一 Blender render 的 neutral mesh render；带纹理 GLB 只能补充资产化效果，不能替代 neutral geometry render。

## Local repair 结论

本地结果覆盖 15 个输入资产、7 种 repair 变体、105 个导出 mesh 变体。primary connectivity 使用 surface/edge/centroid voxel occupancy 的 6-neighbor 连通性；辅助诊断包含 face component count、largest face component ratio、voxel/area/bbox retention 和 mesh triangle render contact sheet。

可作为“局部正结果”的 case 只有 radial4 系列：

| case | selected method | before occ comps / LCR | after occ comps / LCR | 视觉/指标状态 |
|---|---|---:|---:|---|
| `transform_radial4_pyrite_steps8_tex2048_xformers` | `voxel_close` | 4 / 0.99932 | 1 / 1.00000 | 可用候选；occupancy 连通性改善，contact sheet 保守，但面积增长约 4.39x，需要论文中说明是 repair/closure ablation 而非无损重建。 |
| `transform_radial4_bismuth_steps8_tex2048_xformers` | `voxel_close` | 4 / 0.99932 | 1 / 1.00000 | 可用候选；结论同上，材质差异不影响几何 QA。 |
| `siga_night_20260508_selected_meshes_transform_radial4_d3` | `voxel_close` | 4 / 0.99932 | 1 / 1.00000 | 可用候选；occupancy 从 4 components 到 1 component，contact sheet 视觉保守。 |

这些 radial4 case 也有 `voxel_bridge_close` / `voxel_bridge_close_simplify` 的 safe rows：after occupancy component 为 1、LCR 为 1.0，face component 数约 9-10，面积增长约 3.46-3.53x，voxel retention 约 0.94-0.95。若论文需要更保守的外形体积，可优先比较 `voxel_close` 与 `voxel_bridge_close`，不要只报最漂亮的一列。

不可作为“修复成功”的 case：

- `non_tree_recursive_20260508_meshes_scifi_module_projected_translate_stage03`、`porous_container_compete_stage03_bismuth_steps8_tex2048_xformers`、`scifi_module_projected_translate_stage03_pyrite_steps8_tex2048_xformers`：occupancy before 已为 1 component、LCR=1.0；只能说 repair 没有带来 primary metric 改善。
- 所有本轮 DLA textured GLB/OBJ：`dla_fork_side_octopus`、`dla_fork_side_pyrite`、`dla_side_bismuth`、`dla_side_octopus`、`siga_night...dla...` 在 occupancy 口径下 before 已单连通，不能用本地 repair 宣称 DLA 连接性被修好。
- L-system / tree-leaf case：`lsystem_fork_side_parthenocissus`、`lsystem_fork_bismuth`、`masked_tree...` occupancy before 也是单连通，但 face component 诊断显示大量三角面碎片或较低 largest face ratio，说明它们更像“surface stitching / face fragmentation”问题，不是 occupancy component repair 的正例。
- `largest_component` 不能作为论文图修复方法。它可以让某些 component 指标变好，但通过删除结构实现，适合作为诊断下界或负 ablation。
- `bridge_to_largest` 不应默认作为美术图方法。它可能引入显眼连接杆，且 radial4 上反而出现 occupancy component/LCR 恶化，应作为负例或工程连接策略。

## DLA/晶体下一轮视觉 QA 标准

远端四卡结果拉回后，DLA/晶体结果必须按“指标 + face diagnostic + Blender render + zoom-in + 语义清晰度”五项一起验收。任何单项通过都不能单独进入论文主图。

1. Occupancy component / LCR：
   - 固定 occupancy resolution 和 6-neighbor 口径，至少报告 `occupancy_component_count_6n`、`largest_occupancy_component_ratio_6n`、`occupied_voxels`。
   - 正结果最低标准：component count 不增加；若输入有碎片，after component count 明确下降且 LCR 上升到接近 1.0。
   - 若 before 已经是 1 component、LCR=1.0，只能报告“保持连通”，不能写成“修复连通性”。

2. Face diagnostic：
   - 报告 `face_component_count`、`largest_face_component_ratio`、watertight 状态、face/vertex 数变化。
   - DLA/晶体常见风险是 occupancy 单连通但 triangle soup 极碎；如果 face component 极多或 largest face ratio 很低，需要在文中标为 surface fragmentation，而不是 connectivity failure。
   - repair 后如果 face component 大幅下降但几何语义被抹平，应归为 over-smoothing negative。

3. Blender render：
   - 每个候选必须有 fixed-camera neutral Blender render；若有 GLB，再补充 textured/PBR render。
   - 主图优先使用 neutral render 证明几何结构，textured render 只展示材质可用性。
   - 渲染设置要同相机、同焦距、同光照、同背景；baseline 和 proposed 不允许使用不同视觉协议。

4. Zoom-in 检查：
   - 每个候选至少检查 2-3 个局部区域：branch junction / crystal contact、thin bridge、high-curvature tip 或 porous cavity。
   - zoom-in 必须看 mesh render 或 Blender crop，不用点云 crop 作最终证据。
   - 标记 failure 类型：floating shard、fake bridge、surface sheet、melted tip、over-closed cavity、texture masking。

5. 语义清晰度：
   - DLA 结果应能读出随机前沿增长、分枝/团簇、孔隙或晶簇轮廓，而不是不可解释的噪声云。
   - 晶体结果应能读出 faceted/crystalline planes、层级重复或晶体簇，而不是仅靠 bismuth/pyrite 纹理暗示类别。
   - 如果 geometry neutral render 不能读出 DLA/晶体语义，即使 textured render 好看，也只能作为 texture/renderability 结果。

## 论文实验表达建议

正结果要窄写、实写：本地 repair 只能支持“在 radial transform-copy / radial4 结构上，voxel closure 类方法可以把少量 occupancy fragments 合并为单一 occupancy component，并在 contact sheet 中保持整体形状”。不要把该结论泛化到所有 DLA、L-system、tree 或 scifi case。

负结果要主动呈现：DLA/leaf/textured GLB 多数 before occupancy 已单连通，但 face diagnostics 显示 surface fragmentation 或 low largest-face ratio。这说明 occupancy connectivity 与 mesh surface quality 是两个不同问题。论文中可以把它写成 diagnostic finding，而不是失败回避。

Ablation 建议按方法风险排序：

| ablation | 应报告的结论 |
|---|---|
| no repair / before | 原始 mesh 的 occupancy component、face fragmentation、render 语义基线。 |
| vertex weld / conservative hole fill | 低风险清理，通常不改变 occupancy connectivity；可作为保守 baseline。 |
| largest component | metric-only 下界；显示“删碎片”能改善某些指标但破坏结构，不作为主方法。 |
| bridge_to_largest | 工程桥接负例；可能产生假桥或使 occupancy 指标恶化。 |
| voxel_close | radial4 正候选；连通性改善明显，但面积增长大，需要说明 closure 代价。 |
| voxel_bridge_close / simplify | 更可控的 closure 候选；应和 `voxel_close` 一起比较视觉保真与体积/面积代价。 |

实验文字中建议使用三类标签：

- `paper_safe_candidate`：metrics 改善、contact sheet 保守、Blender render 和 zoom-in 通过。
- `diagnostic_only`：指标有信息量，但视觉或语义不足；可进 appendix，不进主图。
- `negative_ablation`：展示方法局限，例如 largest-component 删除结构、bridge 假连接、voxel closure 过度膨胀。

最终主实验应把 claim 拆开写：connectivity repair claim 只对应 occupancy component/LCR；mesh quality claim 需要 face diagnostic 和 render；semantic claim 需要 neutral render 下可读的 DLA/晶体结构。三者都通过时才写成完整正结果。
