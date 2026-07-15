# V24 strict visual matched priority rerun 结果与渲染路线检查

日期：2026-05-10

## 1. 完成情况与路径

V24 priority rerun 共 15 个 case。当前本地同步结果显示：15/15 `summary.json` 存在且状态为 `ok`，15/15 `textured.glb` 存在，15/15 `surface_metrics_occ64` loader_status 为 `ok`。当前视觉目录下未发现 PNG 渲染图，因此主文视觉 QA 仍需补白底 overview / matched camera zoom / 框选图。

本地结果路径：

- surface metrics CSV：`results/strict_visual_matched_texture_V24_priority_rerun_20260510_remote/surface_metrics_occ64.csv`
- surface metrics JSON：`results/strict_visual_matched_texture_V24_priority_rerun_20260510_remote/surface_metrics_occ64.json`
- manifest：`results/strict_visual_matched_texture_V24_priority_rerun_20260510_remote/inputs/manifest.csv`
- GLB/summary 目录：`visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/`

远端计划路径：

- 远端输入目录：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/inputs/strict_visual_matched_cases_V24_priority_rerun_20260510`
- 远端结果目录：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/strict_visual_matched_texture_V24_priority_rerun_20260510`

视觉产物状态：每个 case 目录均有 `summary.json` 和 `textured.glb`；当前未见 `*.png`。这意味着 V24 已完成 texturing/export 与 surface metric 检查，但尚未完成论文图级别的白底渲染与局部 zoom QA。

## 2. Surface Metrics 摘要

推荐等级只基于 post-GLB surface metrics 和 manifest role 做保守分级：`strong metric` 表示 `components_r0=1` 且 `lcr_r0=1.0`；`near-stable visual QA required` 表示 `r1` 合并后为单连通但 `r0` 有少量碎片或 LCR 略低，需要白底/zoom 人工确认；`boundary appendix only` 表示 manifest 带 boundary tag。

| case | family | components r0/r1 | lcr r0/r1 | 推荐等级 |
|---|---|---:|---:|---|
| `V24_dla_coral_cluster_900_lace_porosity_boundary_seedA` | DLA/frontier | 10 / 1 | 0.998634 / 1.000000 | boundary appendix only；需 fragment QA |
| `V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA` | DLA/frontier | 1 / 1 | 1.000000 / 1.000000 | strong metric；DLA polish 主候选 |
| `V24_dla_frontier_sheet_700_open_boundary_polish_seedA` | DLA/frontier | 1 / 1 | 1.000000 / 1.000000 | strong metric；frontier sheet 主/附录候选 |
| `V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA` | IFS/transform | 4 / 1 | 0.999739 / 1.000000 | near-stable visual QA required；桥接接触需 zoom |
| `V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA` | IFS/transform | 1 / 1 | 1.000000 / 1.000000 | strong metric；IFS/radial 备选 |
| `V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA` | L-system | 1 / 1 | 1.000000 / 1.000000 | strong metric；root fan 主候选 |
| `V24_lsys_root_fan_d5_dense_rootlets_anchorB_seedB` | L-system | 1 / 1 | 1.000000 / 1.000000 | strong metric；root fan 第二候选 |
| `V24_lsys_root_fan_d5_smooth_rootlets_anchorA_seedA` | L-system | 4 / 1 | 0.997951 / 1.000000 | near-stable visual QA required；clean fallback |
| `V24_lsys_root_fan_d5_smooth_rootlets_anchorB_seedB` | L-system | 5 / 1 | 0.997666 / 1.000000 | near-stable visual QA required；clean fallback |
| `V24_sc_root_network_260_anchorA_seedA` | Space colonization | 8 / 1 | 0.998895 / 1.000000 | near-stable visual QA required；root priority |
| `V24_sc_root_network_260_anchorB_seedB` | Space colonization | 9 / 1 | 0.998915 / 1.000000 | near-stable visual QA required；root priority |
| `V24_sc_tree_crown_260_attractor_clean_seedA` | Space colonization | 1 / 1 | 1.000000 / 1.000000 | strong metric；SC tree 主候选 |
| `V24_sc_tree_crown_260_attractor_clean_seedB` | Space colonization | 3 / 1 | 0.999838 / 1.000000 | near-stable visual QA required；SC tree 备选 |
| `V24_sc_tree_crown_260_sparse_kill_clean_seedA` | Space colonization | 2 / 1 | 0.999919 / 1.000000 | near-stable visual QA required；backup |
| `V24_sc_tree_crown_260_sparse_kill_clean_seedB` | Space colonization | 4 / 1 | 0.999703 / 1.000000 | near-stable visual QA required；backup |

## 3. 推荐主文视觉 QA 候选

Strong metric candidates：

1. `V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA`：L-system root fan，r0/r1 均单连通，优先做 rootlet attachment close-up。
2. `V24_lsys_root_fan_d5_dense_rootlets_anchorB_seedB`：第二 root fan seed，作为 A 的鲁棒性对照。
3. `V24_sc_tree_crown_260_attractor_clean_seedA`：SC tree 中唯一 r0 单连通 clean candidate，优先检查 crop、端帽和拥挤度。
4. `V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA`：DLA polish 指标最干净，优先检查 staghorn tip caps。
5. `V24_dla_frontier_sheet_700_open_boundary_polish_seedA`：frontier sheet 指标干净，检查 open boundary、branch thickness 和切端。
6. `V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA`：IFS radial 指标干净，可作为 transform/orbit appendix 或主文备选。

Visual-QA-required near-stable：

7. `V24_sc_root_network_260_anchorB_seedB`：root network 是 V24 priority 缺口；虽然 r0 有 9 个 components，但 r1 为单连通且 LCR 接近 0.999，需要 zoom 检查 orphan fragments 是否可见。
8. `V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA`：r0 为 4、LCR 0.999739，指标接近稳定；需要 zoom 判断 pyrite copy bridges 是否读作接触而非机械穿插。

不建议当前直接进主文：`V24_dla_coral_cluster_900_lace_porosity_boundary_seedA`。它带 `near_stable_v23_components_r0_up_to_7_requires_post_glb_fragment_QA` boundary tag，且本次 r0 components=10；只能在 fragment 不可见且图注边界清楚时作为 appendix 备选。

## 4. 白底多级 zoom / 框选图下一步命令草案

本机检查结果：`blender` 当前不在 PATH。因此下面命令是可执行草案；可在装有 Blender 的本机环境执行，或在远端项目环境执行。若只需验证 matched zoom manifest/输出计划，可先用 `--plan-only` 路径，无需 Blender。

先生成 pure-white overview 渲染：

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth

blender -b --python assets/blender_render_recursive_mesh.py -- \
  --case "lsys_dense_A=visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA_steps8_tex2048_seed20284511_xformers/textured.glb" \
  --case "lsys_dense_B=visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/V24_lsys_root_fan_d5_dense_rootlets_anchorB_seedB_steps8_tex2048_seed20284512_xformers/textured.glb" \
  --case "sc_tree_A=visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/V24_sc_tree_crown_260_attractor_clean_seedA_steps8_tex2048_seed20284517_xformers/textured.glb" \
  --case "dla_staghorn=visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA_steps8_tex2048_seed20284521_xformers/textured.glb" \
  --case "dla_frontier_sheet=visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/V24_dla_frontier_sheet_700_open_boundary_polish_seedA_steps8_tex2048_seed20284522_xformers/textured.glb" \
  --case "ifs_radial=visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA_steps8_tex2048_seed20284525_xformers/textured.glb" \
  --case "sc_root_B=visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/V24_sc_root_network_260_anchorB_seedB_steps8_tex2048_seed20284516_xformers/textured.glb" \
  --case "ifs_pyrite=visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA_steps8_tex2048_seed20284524_xformers/textured.glb" \
  --out-dir visuals/strict_visual_matched_texture_V24_priority_rerun_20260510_pure_white_alpha \
  --views iso front \
  --samples 96 \
  --resolution 1800 \
  --material-mode preserve \
  --background white

python3 assets/flatten_png_to_white.py \
  visuals/strict_visual_matched_texture_V24_priority_rerun_20260510_pure_white_alpha \
  --out-dir visuals/strict_visual_matched_texture_V24_priority_rerun_20260510_pure_white_flat
```

再生成 matched camera zoom / 框选图：

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth

blender -b --python scripts/figures/matched_camera_zoom_render_20260510.py -- \
  --case "lsys_dense_A=visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA_steps8_tex2048_seed20284511_xformers/textured.glb" \
  --case "sc_tree_A=visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/V24_sc_tree_crown_260_attractor_clean_seedA_steps8_tex2048_seed20284517_xformers/textured.glb" \
  --case "dla_staghorn=visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA_steps8_tex2048_seed20284521_xformers/textured.glb" \
  --case "ifs_pyrite=visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA_steps8_tex2048_seed20284524_xformers/textured.glb" \
  --out-dir visuals/strict_visual_matched_texture_V24_priority_rerun_20260510_matched_zoom \
  --resolution 1600 \
  --samples 96 \
  --zoom-levels 2 \
  --camera iso \
  --material-mode preserve
```

无 Blender 的替代检查：

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth

python3 scripts/figures/matched_camera_zoom_render_20260510.py \
  --case "toy=/absolute/path/to/toy.obj" \
  --out-dir /tmp/matched_camera_zoom_plan \
  --plan-only \
  --zoom-levels 2
```

注意：`--plan-only` 对 OBJ 顶点计划更有用；GLB 的实际顶点/材质检查仍应通过 Blender 路径完成。

## 5. 可复用脚本与协议

已确认可复用协议：

- `docs/visuals/standard_pure_white_render_protocol_20260510.md`
- `docs/visuals/matched_camera_zoom_render_protocol_20260510.md`

已确认可复用脚本：

- `assets/blender_render_recursive_mesh.py`：支持 GLB/OBJ、`--background white`、`--material-mode preserve`，白底模式不加 ground plane。
- `assets/flatten_png_to_white.py`：将透明 PNG 压平成纯白 RGB。
- `scripts/figures/matched_camera_zoom_render_20260510.py`：生成 overview、zoom、callout、comparison panel；支持 `--plan-only`。
- `assets/render_mesh_contact_sheet.py`：无需 Blender 的 matplotlib/trimesh contact sheet，可作快速几何预览，但不能替代论文白底 PBR 渲染。
- `assets/pyrender_glb_preview.py`、`assets/render_mesh_object_like_conditions.py`、`assets/render_vine_zoom_in_multiscale.py`、`assets/compose_vine_zoom_in_multiscale.py`、`assets/hero_zoom_prepare_manifest_20260510.py`：与 render/zoom 相关，可作为补充参考；主线建议优先使用上面三个白底/zoom 脚本。


## 7. 本轮白底多级相机 zoom QA 更新

2026-05-10 18:20--18:30 CST，本地确认 `/Applications/Blender.app/Contents/MacOS/Blender` 可用（5.1.1），已对 7 个 V24 主候选生成真实 Blender/Cycles 白底相机 zoom。

首轮 `v1` 使用输入 OBJ 作为 zoom target 规划源，发现 root fan 与 DLA staghorn 的第二级 zoom 存在明显空白/错位风险，因此该目录只作为诊断保留：

- `visuals/strict_visual_matched_texture_V24_priority_rerun_zoom_white_20260510_v1/`

随后启动 `v2_render_target`，改用实际渲染 GLB 顶点选择 zoom target，避免 OBJ/GLB 坐标错位。目标目录：

- `visuals/strict_visual_matched_texture_V24_priority_rerun_zoom_white_20260510_v2_render_target/`

每个 case 的目标输出为：`overview_raw.png`、`overview_callouts.png`、`zoom_01.png`、`zoom_01_callouts.png`、`zoom_02.png`、`strict_matched_zoom_comparison.png`。Blender 自带 Python 缺 PIL，因此 callout/comparison 由系统 Python 对 `matched_camera_zoom_plan.json` 后处理生成。

当前 QA 规则：只有 `v2_render_target` 通过像素方差/尺寸检查后，才允许作为论文视觉候选；`v1` 不用于主文或最终附录。

## 6. Claim Boundary

1. 不把 textured GLB 当作拓扑证明。当前 `surface_metrics_occ64` 是 post-GLB 体素化/表面采样连通性证据，只能支持渲染资产的连通性 QA，不等同于严格拓扑证明。
2. 不说 traditional baseline 都碎。可说 V24 priority rerun 针对 root quality、SC tree、DLA/IFS polish 等高风险视觉缺口筛选更稳定候选。
3. 不说 DLA 是物理模拟。可称为 DLA/frontier-style 或 frontier-attachment asset generation；避免把它表述为真实扩散或物理过程模拟。
4. 对 boundary-tagged lace porosity，只能称为 appendix/backup candidate，必须先通过 post-GLB fragment visibility QA。
5. 主文升级前仍需白底 overview、matched camera zoom、局部框选图和人工视觉 QA；当前 PNG 渲染缺失，不应宣称已完成论文图 QA。
