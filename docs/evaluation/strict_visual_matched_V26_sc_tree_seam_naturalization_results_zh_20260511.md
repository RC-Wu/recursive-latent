# V26 SC tree seam naturalization 结果

日期：2026-05-11

## 结论

V26 是针对用户指出的 V24/V25 树枝-树冠接缝问题做的小批次修复。它没有扩展 baseline 矩阵，而是把 `sc_tree_crown_260` 的 branch/crown junction band 显式写入 grammar mask，并在该局部加入 junction collar / cambium sleeve / leafshield 过渡几何，再配低对比连续 guide 送 Trellis2。

远端 4/4 生成成功；post-GLB surface metrics 中 3/4 达到 r0 单连通、LCR=1.0，剩余 1/4 为 r1 单连通且 LCR 高于 0.9995。白底 zoom QA 仍是最终是否替换 V24/V25 SC tree 图的决定项。

## 证据文件

- metrics CSV: `results/strict_visual_matched_texture_V26_sc_tree_seam_naturalization_rows_20260511.csv`
- metrics JSON: `results/strict_visual_matched_texture_V26_sc_tree_seam_naturalization_rows_20260511.json`
- post-GLB occ64: `results/strict_visual_matched_texture_V26_sc_tree_seam_naturalization_20260511_remote/surface_metrics_occ64.csv`
- GLB: `visuals/strict_visual_matched_texture_V26_sc_tree_seam_naturalization_20260511/*/textured.glb`
- zoom 目录：`visuals/strict_visual_matched_texture_V26_sc_tree_seam_naturalization_zoom_white_20260511/`

## 候选表

| case | r0 comps | r0 LCR | seam centers | collars | leafshield | grade | recommendation |
|---|---:|---:|---:|---:|---:|---|---|
| `V26_sc_tree_crown_cambium_sleeve_C_lowcontrast` | 1 | 1.000000 | 34 | 34 | 36 | main-metric-stable | passes V25 SC metric floor; visual seam QA decides main replacement |
| `V26_sc_tree_crown_leafshield_B_lowcontrast` | 1 | 1.000000 | 24 | 24 | 68 | main-metric-stable | passes V25 SC metric floor; visual seam QA decides main replacement |
| `V26_sc_tree_crown_soft_canopy_D_lowcontrast` | 1 | 1.000000 | 30 | 30 | 56 | main-metric-stable | passes V25 SC metric floor; visual seam QA decides main replacement |
| `V26_sc_tree_crown_junction_collar_A_lowcontrast` | 2 | 0.999867 | 28 | 28 | 42 | near-stable-high | appendix or conditional visual candidate; tiny r0 island must be invisible |

## 论文口径

- 可以写：针对 V24/V25 暴露出的 branch/crown seam，局部 masked naturalization 需要显式 junction-band 设计；V26 是这个设计的 SC tree stress-test。
- 不能写：Trellis 原生 UV/PBR 已普遍消除接缝。若最终采用 object-space PBR 图，必须称为 grammar-owned material/rendering route。
- 与 V24/V25 比较时，指标只说明 post-GLB renderability/connectivity floor；自然度和接缝改善必须由同相机白底 zoom 支撑。
