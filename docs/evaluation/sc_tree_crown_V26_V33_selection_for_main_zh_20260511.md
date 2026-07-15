# SC Tree Crown V26--V33 主视觉收束记录

日期：2026-05-11  
状态：active selection；等待最终四类主实验统一排版图。

## 结论

树冠 case 不再继续无边界追新。本轮建议采用“视觉主候选 + 用户认可备份 + 指标备份”的分层口径：

1. **主视觉优先：`V32_sc_tree_balanced_canopy_D`**
   - GLB：`visuals/strict_visual_matched_texture_V32_sc_tree_canopy_veil_naturalization_20260511/V32_sc_tree_balanced_canopy_D_steps8_tex2048_seed20292515_xformers/textured.glb`
   - GLB 白底 zoom：`visuals/strict_visual_matched_texture_V32_sc_tree_canopy_veil_naturalization_zoom_white_seamtarget_20260511/V32_sc_tree_balanced_canopy_D_glb_seamtarget/`
   - metrics：`results/strict_visual_matched_texture_V32_sc_tree_canopy_veil_naturalization_20260511_remote/surface_metrics_occ64.json`
   - 指标：r0 `9` comps，LCR `0.9916065573770492`；r1/r2 单连通。
   - 选择理由：整体更轻、更像树冠，避免 V29 某些团块堆叠感；适合主视觉比较。
   - caveat：r0 有小碎片，近景仍有低面片和枝段感；正文不能写成拓扑最稳。

2. **视觉备选：`V32_sc_tree_leafmass_shell_B`**
   - GLB：`visuals/strict_visual_matched_texture_V32_sc_tree_canopy_veil_naturalization_20260511/V32_sc_tree_leafmass_shell_B_steps8_tex2048_seed20292513_xformers/textured.glb`
   - GLB 白底 zoom：`visuals/strict_visual_matched_texture_V32_sc_tree_canopy_veil_naturalization_zoom_white_seamtarget_20260511/V32_sc_tree_leafmass_shell_B_glb_seamtarget/`
   - metrics：同 V32 metrics 文件。
   - 指标：r0 `12` comps，LCR `0.9934910501940167`；r1/r2 单连通。
   - 选择理由：冠层 mass/veil 读感强，可在主图排版中和 balanced D 比较后择优。
   - caveat：材质岛/小岛更明显，caption 需写 r1-connected/tiny r0 islands。

3. **用户认可上色备份：`V29_sc_tree_softleaf_entry_D`**
   - GLB：`visuals/strict_visual_matched_texture_V29_sc_tree_hidden_trunk_naturalization_20260511/V29_sc_tree_softleaf_entry_D_steps8_tex2048_seed20289515_xformers/textured.glb`
   - OBJ zoom：`visuals/strict_visual_matched_cases_V29_sc_tree_hidden_trunk_obj_zoom_seamtarget_20260511/`
   - metrics：`results/strict_visual_matched_texture_V29_sc_tree_hidden_trunk_naturalization_20260511_remote/surface_metrics_occ64.json`
   - 指标：r0 `5` comps，LCR `0.9956612287400208`；r1/r2 单连通。
   - 选择理由：用户明确认可“上完色质量不错”；作为主视觉备份和补充很稳。
   - caveat：比 V32 更厚、更偏枝段/团块遮挡。

## 推荐论文口径

- 主文图优先比较 `V32_sc_tree_balanced_canopy_D` 和传统 space-colonization tree crown；如果视觉排版里 leafmass 更抓眼，可替换为 `V32_sc_tree_leafmass_shell_B`。
- Caption 明确：SC 树冠是 strict matched family target 下的视觉/asset-readiness 证据，surface voxel r1-connected，但 r0 tiny islands 仍作为诊断公开。
- `V29_sc_tree_softleaf_entry_D` 保留为用户认可备份，不和 V32 同时都作为唯一正例，以免主图显得重复。

