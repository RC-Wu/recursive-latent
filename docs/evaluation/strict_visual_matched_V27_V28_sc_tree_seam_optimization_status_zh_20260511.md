# V24--V32 SC Tree 接缝优化状态

日期：2026-05-11  
状态：V32 remote running / V31 metric-improved but visual boundary / V27--V30 not main-positive  
目标 case：`sc_tree_crown_260`

## 当前结论

用户指出 V24 的树枝和树冠不自然、有接缝，这个判断继续成立。V26 和 V27 都证明“局部 masked naturalization”是正确方向，但 V27 远端 GLB 仍不能作为主文正例：

- V26：post-GLB 连通性最稳，3/4 r0 单连通且 LCR=1.0，但 close zoom 仍有硬圆管、截断端帽和树冠插接感。
- V27：把 terminal bud 和 junction feather 加进 mask，OBJ seam-target 比 V26 自然一些；但 Trellis2 GLB 后出现明显小碎片，且粗主枝仍像一根平滑圆棒穿进树冠。
- V28：新建 compact flare/bark-ridge 路线，减少 V27 的独立小叶/细枝负担，改用更少、更厚、更连接的局部 flare、bark ridge、structural split 和 compact terminal bud。V28 post-GLB 指标恢复，但白底 zoom 仍有单根长杆/材质突变读感，因此不能作为主文正例。
- V29：hidden-trunk / multi-stem 路线移除了最明显的长杆，但 post-GLB r0 仍低于主文偏好门槛，不能作为主文正例。
- V30：occluded-hub / short-segment 路线继续改善 metric，最佳 C 的 r0 LCR 到 `0.998595`，但白底 GLB 仍读成稀疏枝架并有材质岛/小碎片，最多 appendix/boundary。
- V31：compact-crown 路线把 pre-GLB 外露支撑段压到 `<=0.160`，测试通过；但 OBJ seam-target 仍明显是裸 tube skeleton / sparse branch lattice，因此不启动远端主文选择，保留为“metric 进步但视觉不足”的边界证据。
- V32：canopy-veil 路线改为在 3D object-space 中把外层支撑视觉降权，并用 shared-vertex canopy veil pads 与 attached leaf-mass clusters 覆盖 branch/crown entry。V32 本地测试通过、OBJ 视觉明显优于 V31，已在远端 GPU 4/5/6/7 启动真实 Trellis2 GLB。

重要边界：当前项目仍没有闭合的 `2D seam SDEdit/inpaint -> UV/3D/GLB 回投` pipeline。图像生成模型只能安全作为 whole-object low-contrast guide / reference source；不能把局部 2D seam inpaint 写成已完成的 3D seam 修复证据。当前 V32 仍是 grammar-owned object-space local geometry naturalization + whole-object Trellis2 texturing guide。

## V27 远端证据

远端 run：

- `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/strict_visual_matched_texture_V27_sc_tree_organic_seam_20260511`

本地证据：

- GLB：`visuals/strict_visual_matched_texture_V27_sc_tree_organic_seam_20260511/*/textured.glb`
- post-GLB metrics：`results/strict_visual_matched_texture_V27_sc_tree_organic_seam_20260511_remote/surface_metrics_occ64.csv`
- GLB seam-target zoom：`visuals/strict_visual_matched_texture_V27_sc_tree_organic_seam_zoom_white_seamtarget_20260511/V27_glb_sc_tree_organic_seam_contact_sheet_20260511.png`
- OBJ seam-target zoom：`visuals/strict_visual_matched_cases_V27_sc_tree_organic_seam_obj_zoom_seamtarget_20260511/V27_sc_tree_organic_seam_obj_seamtarget_contact_sheet_20260511.png`

V27 post-GLB occ64:

| case | r0 comps | r0 LCR | r1 comps | r1 LCR | verdict |
|---|---:|---:|---:|---:|---|
| `V27_sc_tree_organic_feather_A` | 3 | 0.999218 | 1 | 1.0 | metric backup only |
| `V27_sc_tree_bark_leaf_C` | 9 | 0.974817 | 1 | 1.0 | reject for main |
| `V27_sc_tree_soft_canopy_D` | 8 | 0.978981 | 1 | 1.0 | reject for main |
| `V27_sc_tree_terminal_bud_B` | 9 | 0.963722 | 1 | 1.0 | reject for main |

QA：Trellis2 纹理让叶片更绿，但没有解决 coarse geometry。主枝仍读成圆棒/斜棍；B/C/D 的 zoom 有小碎片和低模叶片。因此 V27 只能作为 V28 的设计依据或 appendix negative/boundary，不进入主文正例。

## V28 设计

新增文件：

- `assets/strict_visual_matched_cases_V28_sc_tree_flare_bark_naturalization_20260511.py`
- `assets/launch_strict_visual_matched_texture_V28_sc_tree_flare_bark_naturalization_20260511.sh`
- `tests/test_strict_visual_matched_cases_V28_sc_tree_flare_bark_naturalization_20260511.py`

核心变化：

- 保持 strict target `sc_tree_crown_260`，不扩大 baseline。
- 保留 branch/crown junction band + terminal cap mask。
- 用 compact junction flare 替代 V27 的大量 feather twigs。
- 用 connected bark ridges 和非圆截面降低“光滑圆管”读感。
- 用少量 structural split 和 compact terminal bud 遮掉端帽。
- 降低叶片/细枝数量，目标是 post-GLB 后恢复 V26-like connectivity floor。
- 不引入 seam-only 2D SDEdit 作为主证据；当前项目没有闭合的 seam-only 3D 回投 pipeline。图像生成/SD3.5 guide 可作为后续 guide source，但不能替代 mesh/GLB 证据。

V28 本地验证：

- 测试：`python3 -m pytest -q tests/test_strict_visual_matched_cases_V28_sc_tree_flare_bark_naturalization_20260511.py`
- 结果：`2 passed`，仅 matplotlib/pyparsing warnings。
- dry-run：`results/strict_visual_matched_cases_V28_sc_tree_flare_bark_naturalization_20260511_dryrun`
- OBJ seam-target zoom：`visuals/strict_visual_matched_cases_V28_sc_tree_flare_bark_obj_zoom_seamtarget_20260511/V28_sc_tree_flare_bark_obj_contact_sheet_20260511.png`

V28 dry-run metrics:

| case | verts | faces | LCR | semantic details | seam | buds | flares | ridges | splits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `V28_sc_tree_branch_flare_A` | 49484 | 99116 | 1.0 | 208 | 34 | 28 | 34 | 24 | 18 |
| `V28_sc_tree_bark_ridge_B` | 54141 | 108370 | 1.0 | 196 | 28 | 24 | 28 | 42 | 14 |
| `V28_sc_tree_multiscale_canopy_C` | 53793 | 107706 | 1.0 | 190 | 28 | 24 | 28 | 20 | 24 |
| `V28_sc_tree_hybrid_flare_bud_D` | 52592 | 105320 | 1.0 | 198 | 30 | 26 | 30 | 24 | 20 |

OBJ QA：V28 比 V27 少碎片；局部连接更厚、更稳。但主枝仍可见直杆感，因此 V28 仍必须等 Trellis2 GLB、post-GLB metrics 和 GLB seam-target zoom 决定是否能进入主文。

## V28 远端证据

远端 run：

- `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/strict_visual_matched_texture_V28_sc_tree_flare_bark_naturalization_20260511`

本地证据：

- GLB：`visuals/strict_visual_matched_texture_V28_sc_tree_flare_bark_naturalization_20260511/*/textured.glb`
- post-GLB metrics：`results/strict_visual_matched_texture_V28_sc_tree_flare_bark_naturalization_20260511_remote/surface_metrics_occ64.csv`
- GLB seam-target zoom：`visuals/strict_visual_matched_texture_V28_sc_tree_flare_bark_naturalization_zoom_white_seamtarget_20260511/V28_glb_sc_tree_flare_bark_contact_sheet_20260511.png`
- OBJ seam-target zoom：`visuals/strict_visual_matched_cases_V28_sc_tree_flare_bark_obj_zoom_seamtarget_20260511/V28_sc_tree_flare_bark_obj_contact_sheet_20260511.png`

V28 post-GLB occ64：

| case | r0 comps | r0 LCR | r1 comps | r1 LCR | verdict |
|---|---:|---:|---:|---:|---|
| `V28_sc_tree_branch_flare_A` | 1 | 1.000000 | 1 | 1.0 | metric success, visual caveat |
| `V28_sc_tree_bark_ridge_B` | 3 | 0.996725 | 1 | 1.0 | metric backup only |
| `V28_sc_tree_multiscale_canopy_C` | 1 | 1.000000 | 1 | 1.0 | metric success, visual caveat |
| `V28_sc_tree_hybrid_flare_bud_D` | 1 | 1.000000 | 1 | 1.0 | metric success, visual caveat |

QA：V28 解决了 V27 B/C/D 的 post-GLB r0 碎片问题，但 GLB zoom 中主枝仍读成一根长直杆/梁，green/brown 材质突变仍明显。V28 可作为“masked local geometry improves metrics but does not by itself solve visual naturalness”的 appendix/boundary，不进主文正例。

## V29 设计与本地证据

新增文件：

- `assets/strict_visual_matched_cases_V29_sc_tree_hidden_trunk_naturalization_20260511.py`
- `assets/launch_strict_visual_matched_texture_V29_sc_tree_hidden_trunk_naturalization_20260511.sh`
- `tests/test_strict_visual_matched_cases_V29_sc_tree_hidden_trunk_naturalization_20260511.py`

核心变化：

- 保持 strict target `sc_tree_crown_260`，不扩大 baseline。
- 把低层可见 trunk chain 裁成隐藏 root + 3--5 个短 entry hub，目标是从结构上消除“一根长圆杆插入树冠”。
- naturalization 区域只包括 object-space hidden entry junction band 与 terminal caps。
- 继续使用 compact entry sheaths、junction flares、bark ridges、structural splits、terminal buds，但把 semantic detail budget 收紧到约 212--222，降低 post-GLB 小碎片风险。
- 图像生成/guide 只作为 whole-object low-contrast guide source。当前项目没有闭合的 2D seam SDEdit/inpaint -> UV/3D 回投 pipeline，因此 metadata 明确 `sdedit_seam_backprojection_available=false`，不写 2D seam inpaint claim。

V29 本地验证：

- 测试：`python3 -m pytest -q tests/test_strict_visual_matched_cases_V29_sc_tree_hidden_trunk_naturalization_20260511.py`
- 结果：`2 passed`，仅 matplotlib/pyparsing warnings。
- dry-run：`results/strict_visual_matched_cases_V29_sc_tree_hidden_trunk_naturalization_20260511_dryrun`
- OBJ seam-target zoom：`visuals/strict_visual_matched_cases_V29_sc_tree_hidden_trunk_obj_zoom_seamtarget_20260511/V29_sc_tree_hidden_trunk_obj_contact_sheet_20260511.png`

V29 dry-run metrics：

| case | verts | faces | mesh comps | LCR | semantic details | seam centers | entry sheaths | hubs | external max segment |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `V29_sc_tree_hidden_multistem_A` | 53936 | 108112 | 1 | 1.0 | 222 | 50 | 28 | 4 | 0.293 |
| `V29_sc_tree_canopy_occlusion_B` | 54290 | 108828 | 1 | 1.0 | 222 | 56 | 28 | 5 | 0.314 |
| `V29_sc_tree_braided_bark_C` | 56722 | 113616 | 1 | 1.0 | 216 | 44 | 26 | 3 | 0.344 |
| `V29_sc_tree_softleaf_entry_D` | 51289 | 102826 | 1 | 1.0 | 212 | 48 | 24 | 5 | 0.256 |

OBJ QA：V29 相比 V27/V28 明显移除了长杆失败模式，overview 与 seam zoom 都读成多短枝/多 hub 的内部入口。但这只是输入级证据，必须等真实 Trellis2 textured GLB、post-GLB metrics 和 GLB seam-target zoom 后才能决定是否主文使用。

## V29--V30 远端结论

V29/V30 已完成并拉回；结论是 metric 逐步改善但视觉仍未达到主文正例。

V29 best metric：

- `V29_sc_tree_softleaf_entry_D`：r0 comps `5`，r0 LCR `0.995661`。

V30 post-GLB occ64：

| case | r0 comps | r0 LCR | r1 comps | r1 LCR | verdict |
|---|---:|---:|---:|---:|---|
| `V30_sc_tree_softleaf_occluded_hubs_A` | 4 | 0.997706 | 1 | 1.0 | boundary only |
| `V30_sc_tree_short_hub_bark_transition_B` | 4 | 0.996903 | 1 | 1.0 | boundary only |
| `V30_sc_tree_lowdetail_connected_entry_C` | 3 | 0.998595 | 1 | 1.0 | best metric, visual still weak |
| `V30_sc_tree_broad_occlusion_shell_D` | 6 | 0.968860 | 1 | 1.0 | reject |

V30 本地证据：

- GLB：`visuals/strict_visual_matched_texture_V30_sc_tree_occluded_hub_naturalization_20260511/`
- post-GLB metrics：`results/strict_visual_matched_texture_V30_sc_tree_occluded_hub_naturalization_20260511_remote/surface_metrics_occ64.csv`
- GLB seam-target zoom：`visuals/strict_visual_matched_texture_V30_sc_tree_occluded_hub_naturalization_zoom_white_seamtarget_20260511/V30_glb_sc_tree_occluded_hub_contact_sheet_20260511.png`
- OBJ seam-target zoom：`visuals/strict_visual_matched_cases_V30_sc_tree_occluded_hub_obj_zoom_seamtarget_20260511/V30_sc_tree_occluded_hub_obj_contact_sheet_20260511.png`

QA：V30 相比 V29 降低了长杆读感，但 GLB 仍像稀疏枝架，且有灰/黑材质岛和局部小碎片。不能进入主文正例。

## V31 本地结论

新增文件：

- `assets/strict_visual_matched_cases_V31_sc_tree_compact_crown_naturalization_20260511.py`
- `assets/launch_strict_visual_matched_texture_V31_sc_tree_compact_crown_naturalization_20260511.sh`
- `tests/test_strict_visual_matched_cases_V31_sc_tree_compact_crown_naturalization_20260511.py`

本地验证：

- 测试：`python3 -m pytest -q tests/test_strict_visual_matched_cases_V31_sc_tree_compact_crown_naturalization_20260511.py`
- 结果：`2 passed`
- dry-run：`results/strict_visual_matched_cases_V31_sc_tree_compact_crown_naturalization_20260511_dryrun`
- OBJ seam-target zoom：`visuals/strict_visual_matched_cases_V31_sc_tree_compact_crown_obj_zoom_seamtarget_20260511/V31_sc_tree_compact_crown_obj_contact_sheet_20260511.png`

V31 dry-run metrics：

| case | verts | faces | LCR | semantic details | seam | entry | hidden hubs | external max segment |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `V31_sc_tree_compact_entry_A` | 38530 | 77128 | 1.0 | 124 | 66 | 12 | 5 | 0.156962 |
| `V31_sc_tree_crown_mass_B` | 38392 | 76880 | 1.0 | 124 | 70 | 10 | 5 | 0.159541 |
| `V31_sc_tree_lowfrag_shell_C` | 34992 | 70050 | 1.0 | 109 | 62 | 8 | 5 | 0.149594 |
| `V31_sc_tree_balanced_leafmass_D` | 39953 | 79988 | 1.0 | 125 | 68 | 12 | 6 | 0.155857 |

QA：V31 pre-GLB 指标比 V30 更稳，最长支撑段进一步缩短；但 OBJ overview/zoom 仍明显是裸 tube skeleton 和 sparse branch lattice。该结果证明“短 hub + compact pad”还不够解决视觉自然度，不应作为主文正例。

## V32 设计与当前远端状态

新增文件：

- `assets/strict_visual_matched_cases_V32_sc_tree_canopy_veil_naturalization_20260511.py`
- `assets/launch_strict_visual_matched_texture_V32_sc_tree_canopy_veil_naturalization_20260511.sh`
- `tests/test_strict_visual_matched_cases_V32_sc_tree_canopy_veil_naturalization_20260511.py`

核心变化：

- 保持 strict target `sc_tree_crown_260`。
- 将 V31 的“缩短裸支撑”改成“支撑仍连通但视觉降权”：outer support radius 乘 `support_visibility_fraction=0.28--0.36`。
- 使用 attached canopy veil pads 与 mid-canopy leaf-mass clusters，全部从已有 support center shared-vertex attach，不做独立漂浮叶片。
- 把 `EXTERNAL_SUPPORT_MAX_SEGMENT_GATE` 收紧到 `0.145`。
- 继续使用 whole-object low-contrast guide；metadata 明确 `sdedit_seam_backprojection_available=false`。

本地验证：

- 测试：`python3 -m pytest -q tests/test_strict_visual_matched_cases_V32_sc_tree_canopy_veil_naturalization_20260511.py`
- 结果：`2 passed`
- dry-run：`results/strict_visual_matched_cases_V32_sc_tree_canopy_veil_naturalization_20260511_dryrun`
- OBJ seam-target zoom：`visuals/strict_visual_matched_cases_V32_sc_tree_canopy_veil_obj_zoom_seamtarget_20260511/V32_sc_tree_canopy_veil_obj_contact_sheet_20260511.png`

V32 dry-run metrics：

| case | verts | faces | LCR | semantic details | seam | canopy pads | mid veils | support visibility | external max segment |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `V32_sc_tree_canopy_veil_A` | 40105 | 81702 | 1.0 | 324 | 218 | 28 | 42 | 0.34 | 0.128129 |
| `V32_sc_tree_leafmass_shell_B` | 42783 | 87276 | 1.0 | 366 | 222 | 32 | 48 | 0.30 | 0.135870 |
| `V32_sc_tree_lowrod_crown_C` | 40626 | 83122 | 1.0 | 385 | 214 | 34 | 54 | 0.28 | 0.129116 |
| `V32_sc_tree_balanced_canopy_D` | 41713 | 84990 | 1.0 | 346 | 224 | 30 | 44 | 0.36 | 0.138478 |

OBJ QA：V32 比 V31 明显多了冠层叶团和接缝遮挡，入口不再只是裸短杆；但外圈仍有部分 tube skeleton 可见。值得跑真实 GLB 检验 texture 是否能把 leaf-mass 读感拉到主文级。

远端启动：

```bash
ssh a100-2 'cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507 && RUN=strict_visual_matched_texture_V32_sc_tree_canopy_veil_naturalization_20260511 INPUT_NAME=strict_visual_matched_cases_V32_sc_tree_canopy_veil_naturalization_20260511 SEED=20260511 bash assets/launch_strict_visual_matched_texture_V32_sc_tree_canopy_veil_naturalization_20260511.sh'
```

启动 PID：

- GPU 4：`V32_sc_tree_canopy_veil_A`，pid `164135`
- GPU 5：`V32_sc_tree_leafmass_shell_B`，pid `164136`
- GPU 6：`V32_sc_tree_lowrod_crown_C`，pid `164137`
- GPU 7：`V32_sc_tree_balanced_canopy_D`，pid `164138`

当前下一步：

1. 等待 V32 `4/4 summary.json` 和 `textured.glb`。
2. 拉回 `results/strict_visual_matched_texture_V32_sc_tree_canopy_veil_naturalization_20260511`、inputs、logs。
3. 跑 `assets/batch_surface_voxel_metrics_20260509.py`，要求优先 r0 LCR >= 0.999，否则最多作为 appendix/boundary。
4. 生成 GLB seam-target 白底 zoom；重点看是否仍出现裸 tube lattice、terminal cap 是否自然、是否有材质岛/小碎片。
5. 若 V32 GLB 视觉成功，从 A/B/C/D 中挑主文候选；若 V32 仍像枝架，则进入 V33：进一步降低 outer support 可见度、增大 leaf-mass cluster 覆盖，同时控制 post-GLB 碎片风险。
