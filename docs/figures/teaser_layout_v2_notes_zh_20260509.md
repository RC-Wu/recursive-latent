# Teaser candidate layout v2 notes

日期：2026-05-09

输出图：`paper_siga/figures/teaser_candidate_layout_v2_20260509.png`  
合成脚本：`assets/compose_teaser_layout_v2_20260509.py`

## 目标

本版目标是把 teaser 从“素材预览 contact sheet”推进到更像论文头图的非对称版式：

- 左侧放一个最大主视觉，优先建立递归植物/藤蔓的第一印象。
- 右侧使用 2x2 小面板展示非树形、树形、机械和 porous 类结果，强调方法 breadth。
- 底部保留一条局部 zoom-in 证据带，用于展示分支层级和 terminal detail。
- 全图不使用 matplotlib 点云预览；所有 panel 都来自 mesh render composite。

## Panel 来源和真实性标注

### True Trellis2 textured mesh / GLB panels

这些 panel 使用已有 Trellis2 textured GLB render，图内以绿色 `TRUE Trellis2 GLB` 标记：

| Panel | 图内标签 | 来源 PNG | 对应 textured GLB |
|---|---|---|---|
| 左侧大图 | Recursive Vine | `visuals/public_guide_textured_glb_20260509/renders/vine_parthenocissus_iso.png` | `visuals/public_guide_textured_glb_20260509/vine_compete_stage03_parthenocissus_steps8_tex2048_xformers/textured.glb` |
| 右上左 | Portal Arch | `visuals/public_guide_textured_glb_20260509/renders/portal_arch_iso.png` | `visuals/public_guide_textured_glb_20260509/ruin_arch_portal_stage03_arch_steps8_tex2048_xformers/textured.glb` |
| 右上右 | Tree Roots | `visuals/public_guide_textured_glb_20260509/renders/tree_roots_iso.png` | `visuals/public_guide_textured_glb_20260509/tree_compete_d4_pruned_tree_roots_steps8_tex2048_xformers/textured.glb` |
| 右下左 | Sci-fi Module | `visuals/public_guide_textured_glb_20260509/renders/scifi_gear_iso.png` | `visuals/public_guide_textured_glb_20260509/scifi_module_projected_translate_stage03_gear_steps8_tex2048_xformers/textured.glb` |
| 右下右 | Porous Pyrite | `visuals/public_guide_textured_glb_20260509/renders/porous_pyrite_iso.png` | `visuals/public_guide_textured_glb_20260509/porous_container_compete_stage03_pyrite_steps8_tex2048_xformers/textured.glb` |

### Programmatic PBR fallback panels

这些 panel 不是 true Trellis2 textured GLB；它们来自同一类 mesh 的 Blender/Cycles programmatic material render，仅作为局部几何 zoom-in 证据，图内以棕色 `PBR fallback` 标记：

| Panel | 图内标签 | 来源 PNG | 说明 |
|---|---|---|---|
| 底部左 | A overview | `visuals/vine_zoom_in_multiscale_20260509/A_overview.png` | OBJ mesh + procedural PBR material |
| 底部中 | B branch recursion | `visuals/vine_zoom_in_multiscale_20260509/B_branch_zoom.png` | OBJ mesh + procedural PBR material |
| 底部右 | C terminal detail | `visuals/vine_zoom_in_multiscale_20260509/C_tip_zoom.png` | OBJ mesh + procedural PBR material |

## 版式和配色

- 背景使用暖白 `#f5f3ec`，面板底色接近纸白，避免前一版偏灰、偏预览页的感觉。
- True Trellis2 GLB 使用绿色标记，PBR fallback 使用棕色标记；两类资产在视觉上保持明确分组。
- 大面板采用 asymmetrical hero + 2x2 support grid，而不是平均 2x2。原因是 vine 结果最有视觉辨识度，适合作为 teaser anchor。
- 底部 zoom strip 被压低为证据条，不与 true textured GLB 主结果争主视觉。

## 当前局限

- 左侧 true textured vine 是完整保真 render，但由于原始相机是正方形画幅，放入宽幅 hero 面板后左右留白明显。后续若有时间，建议重渲染 true textured GLB 的横构图版本。
- 底部 zoom strip 的 PBR material 和上方 true textured GLB 的材质体系不同，已用 `PBR fallback` 明确标注；正式 caption 也应避免暗示它是 Trellis2 texture。
- Portal Arch 是目前最能表达 transform-copy / non-tree 的 true textured GLB，但仍偏“建筑场景”而非抽象圆环；如果需要更强 portal ornament 叙事，应单独重渲染更正面的 portal/ring 视角。

## 建议 caption 写法

建议 caption 中显式写：

> Teaser candidate using true Trellis2 textured GLB renders for the main result panels. The bottom zoom strip uses programmatic PBR material on mesh renders only to expose local recursive geometry and is not a Trellis2 texture result.

