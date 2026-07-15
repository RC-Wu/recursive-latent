# Fig35/Fig36 Depth-Density 白底 Zoom 重渲计划

日期：2026-05-11  
状态：plan ready；等待本地/远端 Blender 渲染执行。

## 当前正文位置

- `paper_siga/main.tex` 中 `fig:depth-parameter-main-candidate` 引用 `figures/depth_parameter_main_candidate_20260509.pdf`，约在 `main.tex:1013--1018`。
- `fig:depth-parameter-mesh-showcase-zoom` 引用 `figures/depth_parameter_mesh_showcase_zoom_20260509.pdf`，约在 `main.tex:1022--1026`。
- `fig:depth-parameter-mesh-showcase` 引用 `figures/depth_parameter_mesh_showcase_20260509.png`，约在 `main.tex:1045--1050`。

注意：旧脚本 `paper_siga/figures/depth_parameter_mesh_showcase_20260509.py` 的 B/C/D 行是 bismuth depth、pyrite depth、coral depth；正文 caption 又写 vine/coral/coral-density 三行。重渲时应新增版本化图，不直接覆盖旧图。

## 推荐重渲源

优先做一个更干净的 **depth + density control** 图组：

- Coral depth：
  - `visuals/coral_depth_textured_showcase_20260509/volumetric_coral_depth_stage_01_coral_steps6_tex1024_xformers/textured.glb`
  - `...stage_02.../textured.glb`
  - `...stage_03.../textured.glb`
  - `...stage_04.../textured.glb`
- Coral density moderate：
  - `visuals/coral_density_param_texture_20260509/coral_density_param_density_0p45_octopus_steps8_tex2048_xformers/textured.glb`
  - `...density_0p70.../textured.glb`
  - `...density_0p95.../textured.glb`
  - `...density_1p20.../textured.glb`
- Coral density extreme：
  - `visuals/coral_density_extreme_texture_20260509/coral_density_param_density_0p25_octopus_steps8_tex2048_xformers/textured.glb`
  - `...density_0p45.../textured.glb`
  - `...density_1p35.../textured.glb`
  - `...density_1p75.../textured.glb`

如用户仍想严格保留旧 B/C/D 三行，则重渲 bismuth/pyrite/coral depth：

- `visuals/bismuth_depth_textured_showcase_20260509/bismuth_hopper_depth_stage_0*_bismuth_steps6_tex1024_xformers/textured.glb`
- `visuals/pyrite_depth_textured_showcase_20260509/pyrite_lattice_depth_stage_0*_pyrite_steps6_tex1024_xformers/textured.glb`
- `visuals/coral_depth_textured_showcase_20260509/volumetric_coral_depth_stage_0*_coral_steps6_tex1024_xformers/textured.glb`

## 渲染协议

- 使用 `scripts/figures/matched_camera_zoom_render_20260510.py`。
- 每个 GLB 输出 `overview_raw.png`、`overview_callouts.png`、`zoom_01.png`、`zoom_02.png`、`strict_matched_zoom_comparison.png`。
- 背景纯白；远景必须有矩形框标出 zoom 区域。
- `fig35` 建议作为 clean row grid；`fig36` 作为带 zoom 的 local-structure evidence。

## 推荐输出

- 中间产物：`visuals/matched_camera_zoom_depth_density_20260511/`
- paper 图：
  - `paper_siga/figures/fig35_depth_density_controls_20260511.pdf`
  - `paper_siga/figures/fig36_depth_density_zoom_20260511.pdf`
- TeX 草稿：`paper_siga/drafts/depth_density_control_subfigures_20260511.tex`

## TeX 接入原则

- 不覆盖用户保留的中文。
- 不直接替换旧图，先新增 fig35/fig36 版本化引用，确认编译和视觉后再决定是否删除旧图。
- Caption 写“same-condition control visualization”，不要写 calibrated ablation。

