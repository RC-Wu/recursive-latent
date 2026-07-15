# 非树结构连通性更新 2026-05-09 19:10

## 结论

当前非树结构线必须分成两类写：

- **正例**：grammar-native connected scaffold，再交给 Trellis2 做 textured GLB/PBR export。
- **负例或边界**：hard-DLA/post-hoc bridge/mesh repair。这些方法有时能让 face-level component 看起来变好，但 occupancy support 仍然碎，不能证明资产拓扑可用。

这直接回应用户的核心批评：DLA、晶体、根系、履带车一类碎块绝不能作为正例。论文主文必须用 surface/occupancy connectivity 指标，而不能只看 Blender render 或 face component。

## Bismuth-like Stage-4 Candidate

来源：`crystal_stage4_guide_sweep_rerun1845/bismuth_stage4_bismuth_warm_steps8_tex2048_xformers`

本地文件：

- GLB：`visuals/crystal_stage4_guide_sweep_rerun1845/bismuth_stage4_bismuth_warm_steps8_tex2048_xformers/textured.glb`
- 渲染：`visuals/crystal_stage4_guide_sweep_rerun1845/renders/bismuth_warm_stage4_{iso,front,side}.png`
- contact sheet：`visuals/crystal_stage4_guide_sweep_rerun1845/bismuth_warm_stage4_contact_20260509.png`
- 指标：`visuals/crystal_stage4_guide_sweep_rerun1845/bismuth_warm_surface_metrics_occ64.{csv,json}`

指标：

- occupied voxels @64：`17,460`
- components r0/r1/r2：`1 / 1 / 1`
- LCR r0/r1/r2：`1.000 / 1.000 / 1.000`
- box-counting dimension proxy：`2.029`

判断：

- 可作为 `crystal-like / bismuth-inspired connected scaffold` 的候选。
- 不应写成真实晶体生长或物理 bismuth；视觉更像氧化矿物/建筑化 voxel lattice。
- 如果进主文，需要配 neutral/zoom 图，避免 texture 让读者误判连通性证据。

## Coral/DLA-inspired Density Parameter Sequence

来源：`coral_density_extreme_texture_20260509`

本地文件：

- 渲染：`visuals/coral_density_extreme_texture_20260509/renders/coral_density_{0p25,0p45,1p35,1p75}_iso.png`
- contact sheet：`visuals/coral_density_extreme_texture_20260509/coral_density_extreme_contact_20260509.png`
- 论文图副本：`paper_siga/figures/coral_density_extreme_texture_rerun1900_20260509.png`
- 指标：`visuals/coral_density_extreme_texture_20260509/surface_metrics_occ64.{csv,json}`

指标：

| density | occupied @64 | components r0/r1/r2 | LCR r0/r1/r2 | box dim |
| --- | ---: | --- | --- | ---: |
| 0.25 | 7,686 | 1/1/1 | 1.000/1.000/1.000 | 2.067 |
| 0.45 | 8,551 | 1/1/1 | 1.000/1.000/1.000 | 2.074 |
| 1.35 | 9,600 | 1/1/1 | 1.000/1.000/1.000 | 2.136 |
| 1.75 | 11,942 | 1/1/1 | 1.000/1.000/1.000 | 2.128 |

判断：

- 这是目前非树线里比较稳的正例：同一输入/guide 下，density 参数改变带来更密集的连接 scaffold，且 surface-voxel 连通性保持为单一分量。
- 可用于“方法行为展示”，不是消融；caption 应写为 parameter control under a fixed connected grammar and Trellis2 texture export。
- 仍需补 zoom-in 和 neutral render，尤其展示连接处而不是只看整体。

## DLA Bridge Ablation Rerun

来源：`dla_bridge_ablation_rerun1907`

关键结果：

- hard-DLA：occupancy component count 约 `5-7`，occupancy LCR 约 `0.516-0.521`。
- volumetric-DLA：occupancy component count 约 `7-9`，occupancy LCR 约 `0.418-0.472`。
- 有一个 bridge variant 的 face component count 达到 `1`，但 occupancy support 仍是多分量，因此不能作为拓扑正例。

判断：

- post-hoc bridge/repair 当前不可靠。
- 可以作为负例支持主张：递归生成的连通性必须进入 grammar semantics 和 per-depth projection，而不是最终 mesh 后处理。
- 不建议继续把 hard-DLA bridge 放进头图或主文正例，除非之后出现 occupancy-level 单分量结果。

## 写作建议

主文应该这样组织：

1. 先定义 support-level connectedness，说明为什么 raw face components 和 textured renders 不是充分证据。
2. 方法部分强调 grammar-native support construction、occupancy competition、per-depth projection 共同维持连接。
3. 实验部分把 coral/bismuth-like scaffold 作为非树正例，把 DLA bridge 作为边界或补充负例。
4. 所有 textured GLB 图都必须配指标表或 neutral/zoom 图，避免被 reviewer 认为只是在展示 PBR。
