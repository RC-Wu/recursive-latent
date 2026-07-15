# Depth / density 控制图白底重渲状态

日期：2026-05-11  
状态：已完成第一版白底 GLB camera zoom 重渲；尚未替换 `paper_siga/main.tex`。

## 已生成文件

- manifest：`results/main_experiment_case_metrics_20260511/depth_density_control_white_zoom_manifest_20260511.json`
- raw / callout / per-case zoom 目录：`visuals/fig35_fig36_depth_density_rerender_20260511/`
- contact sheet：`visuals/fig35_fig36_depth_density_rerender_20260511/depth_density_control_contact_sheet_20260511.png`
- depth progression 新图：`paper_siga/figures/fig35_depth_parameter_mesh_showcase_white_zoom_20260511.png`
- density sweep 新图：`paper_siga/figures/fig36_coral_density_extreme_white_zoom_20260511.png`

## 对应正文位置

当前 `paper_siga/main.tex` 中相关 figure 环境为：

- `fig:depth-parameter-mesh-showcase`：当前引用 `figures/depth_parameter_mesh_showcase_20260509.png`，约在 `main.tex:1045--1050`。
- `fig:coral-density-extreme`：当前引用 `figures/coral_density_extreme_texture_rerun1900_20260509.png`，约在 `main.tex:1053--1058`。

如果替换，只应局部改对应 `\includegraphics{...}` 路径，不动 caption、label、中文块或其他正文。

## QA 结论

- Bismuth / pyrite / coral depth 三行均已使用纯白背景、square overview、camera zoom 和红框 callout 重渲。
- Pyrite depth 行读感最好，stage 递进和晶格结构清晰。
- Bismuth 行可作为 stepped scaffold / guide sensitivity 的控制图，但视觉仍偏黄绿材质，不建议写成最强主文视觉。
- Coral depth 与 density 行能说明参数变化，但近景仍有球头、管状和局部低模感；适合保留为 method-behavior/control evidence，不适合写成 natural coral 主视觉。
- 新图可作为正文/附录替换候选；若最终主文空间紧张，建议正文只保留 pyrite/depth 或 density 的最强一行，完整 3 行进补充。

## 下一步

1. 若要接入 TeX，先确认用户允许替换当前旧图。
2. 若作为主文图，建议对 pyrite/bismuth 使用更高分辨率重渲；coral 行保守进入补充。
3. Caption 需要继续保持 conservative：这是 same-condition control visualization，不是 ablation，不是物理生长或拓扑完美声明。
