# Teaser candidate layout v3 notes

日期：2026-05-09

输出图：`paper_siga/figures/teaser_candidate_layout_v3_20260509.png`  
合成脚本：`assets/compose_teaser_layout_v3_20260509.py`

## 目标

v3 的目标是修正 v2 左侧 vine hero 因为正方形 render 被 `contain` 到宽幅 panel 后产生的大面积留白，同时让整体更接近论文 teaser：

- 左侧仍使用 true Trellis2 textured GLB 的 Recursive Vine 作为主视觉，但改成 cover crop，避免左右大块纸白边。
- 右侧改为 3x2 true Trellis2 textured GLB 结果网格，补足递归植物、transform-copy、DLA/branch、portal 和机械结构的 breadth。
- 底部 zoom strip 独立成一条 programmatic PBR fallback 证据带，只说明局部递归几何，不暗示这些局部图是 Trellis2 texture。
- 全图只拼接已有 mesh render PNG，不使用 matplotlib 点云预览或 generated-asset preview。

## Panel 来源和真实性标注

### True Trellis2 textured mesh / GLB panels

这些 panel 使用已有 Trellis2 textured GLB render，图内以绿色 `TRUE Trellis2 GLB` 标记。

| Panel | 图内标签 | 来源 PNG | 对应 textured GLB |
|---|---|---|---|
| 左侧大图 | Recursive Vine | `visuals/public_guide_textured_glb_20260509/renders/vine_parthenocissus_iso.png` | `visuals/public_guide_textured_glb_20260509/vine_compete_stage03_parthenocissus_steps8_tex2048_xformers/textured.glb` |
| 右侧第 1 行第 1 列 | Tree Roots | `visuals/public_guide_textured_glb_20260509/renders/tree_roots_iso.png` | `visuals/public_guide_textured_glb_20260509/tree_compete_d4_pruned_tree_roots_steps8_tex2048_xformers/textured.glb` |
| 右侧第 1 行第 2 列 | L-system Fork | `visuals/public_guide_textured_glb_20260509c/renders/lsystem_parthenocissus_iso.png` | `visuals/public_guide_textured_glb_20260509c/lsystem_fork_side_parthenocissus_steps8_tex2048_xformers/textured.glb` |
| 右侧第 1 行第 3 列 | Radial Copy | `visuals/public_guide_textured_glb_20260509c/renders/radial_pyrite_iso.png` | `visuals/public_guide_textured_glb_20260509c/transform_radial4_pyrite_steps8_tex2048_xformers/textured.glb` |
| 右侧第 2 行第 1 列 | Portal Gear | `visuals/public_guide_textured_glb_20260509c/renders/portal_gear_iso.png` | `visuals/public_guide_textured_glb_20260509c/transform_portal_gear_steps8_tex2048_xformers/textured.glb` |
| 右侧第 2 行第 2 列 | DLA Branch | `visuals/public_guide_textured_glb_20260509d/renders/dla_fork_pyrite_iso.png` | `visuals/public_guide_textured_glb_20260509d/dla_fork_side_pyrite_steps8_tex2048_xformers/textured.glb` |
| 右侧第 2 行第 3 列 | Sci-fi Module | `visuals/public_guide_textured_glb_20260509/renders/scifi_gear_iso.png` | `visuals/public_guide_textured_glb_20260509/scifi_module_projected_translate_stage03_gear_steps8_tex2048_xformers/textured.glb` |

### Programmatic PBR fallback panels

这些 panel 不是 true Trellis2 textured GLB。它们来自同一类 mesh 的 Blender/Cycles programmatic material render，仅用于展示局部几何层级；图内以棕色 `PBR fallback` 标记。

| Panel | 图内标签 | 来源 PNG | 说明 |
|---|---|---|---|
| 底部左 | A overview | `visuals/vine_zoom_in_multiscale_20260509/A_overview.png` | OBJ mesh + procedural PBR material |
| 底部中 | B branch recursion | `visuals/vine_zoom_in_multiscale_20260509/B_branch_zoom.png` | OBJ mesh + procedural PBR material |
| 底部右 | C terminal detail | `visuals/vine_zoom_in_multiscale_20260509/C_tip_zoom.png` | OBJ mesh + procedural PBR material |

## 版式和配色

- 背景继续使用暖白纸色，但 v3 取消 v2 的大标题式留白，把空间让给 mesh render 本身。
- 左侧 hero 从 v2 的 `contain` 改成 `cover`，面板也更接近正方形比例，避免大面积左右留白。
- True Trellis2 GLB panel 使用绿色 badge；programmatic PBR fallback 使用棕色 badge，两类资产在视觉和说明上都分组明确。
- 右侧 3x2 true GLB 网格比 v2 的 2x2 更像结果 breadth overview，并且不会让 bottom zoom strip 抢主视觉。
- 底部 zoom strip 保持为横向 evidence band；它是 mesh-based，但不是 Trellis2 textured GLB 结果。

## 当前局限

- 左侧 hero 的局部放大是从现有正方形 true Trellis2 render 裁切得到，并非重新横构图渲染；如果最终版时间允许，最好重渲染专门的 teaser hero camera。
- `L-system Fork`、`Radial Copy`、`DLA Branch` 等来自后续 `public_guide_textured_glb_20260509c/d` 批次，和 v2 的首批 true GLB 资产同为 true Trellis2 textured GLB render，但批次不同。
- 底部 zoom strip 的材质体系与上方 true GLB panel 不同，正式 caption 需要继续明确它只是 programmatic PBR fallback geometry evidence。

## 建议 caption 写法

建议 caption 中显式写：

> Teaser candidate using true Trellis2 textured GLB renders for the main result panels. The bottom zoom strip uses programmatic PBR material on mesh renders only to expose local recursive geometry and is not a Trellis2 texture result.
