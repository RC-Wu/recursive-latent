# Sci-fi Arch Recursive Module QA 2026-05-09

## 结论

`scifi_module_guide_sweep_rerun1825/scifi_arch_hq` 是一个比早期 `portal arch / snow arch / porous gloss` 更清楚的非有机递归模块候选。它是 Trellis2 textured GLB，本地已拉回、Blender 渲染并做 surface-voxel 连通性指标。

该结果可以作为“非植物、非晶体的规则模块/建筑模块递归”候选，但目前只能作为 breadth 或 supplement 候选。主文是否使用，需要和 scifi gear / pyrite / bismuth 另外三个 guide 版本一起筛选。

## 本地文件

- GLB：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/scifi_module_guide_sweep_rerun1825/scifi_arch_hq_steps8_tex2048_xformers/textured.glb`
- Blender renders：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/scifi_module_guide_sweep_rerun1825/renders/scifi_arch_{iso,front,side}.png`
- contact sheet：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/scifi_module_guide_sweep_rerun1825/scifi_arch_render_contact_20260509.png`
- metrics：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/scifi_module_guide_sweep_rerun1825/scifi_arch_surface_metrics_occ64.csv`

![scifi arch](/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/scifi_module_guide_sweep_rerun1825/scifi_arch_render_contact_20260509.png)

## 指标

| label | vertices loaded | faces | occupied @64 | components r0/r1/r2 | LCR r0/r1/r2 | box dim |
|---|---:|---:|---:|---:|---:|---:|
| scifi_arch_hq_steps8_tex2048_xformers | 28,624 | 43,228 | 11,067 | 1 / 1 / 1 | 1.000 / 1.000 / 1.000 | 2.014 |

## 肉眼 QA

正面：

- 形态清楚：前视图能读出 arch/frame + repeated module blocks，比此前意义不明的 portal/snow/porous case 更适合讲“非有机模块递归”。
- 材质不是单色；有石材/建筑纹理和蓝绿色主框架，PBR 可接受。
- surface-voxel connectivity 是单连通，适合作为候选 breadth panel。

风险：

- 结构较“建筑/模块化”，不直接支撑 DLA、空间竞争或分形自然生长主张。
- 侧视图厚度较大，递归细节更多是 repeated block，而不是强 scale-recursion。
- 目前只拉回 arch guide 版本，不能证明 sci-fi 线整体都好。

## 论文使用建议

- 可作为 supplement 或 main breadth panel：`recursive module / architectural module / non-organic grammar case`。
- 不要作为主 contribution 的核心证据；核心仍应是 projection ablation、connected crystal/coral/vine/root、baseline/metric closure。
- caption 中应写“textured GLB render; occupancy-level connected under the surface-voxel diagnostic”，不要写 raw GLB topology 完全 clean。
