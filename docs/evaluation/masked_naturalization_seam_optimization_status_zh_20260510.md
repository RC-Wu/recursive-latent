# Masked naturalization seam optimization status

日期：2026-05-10

## 本轮结论

用户指出白底 zoom 中接缝仍明显是成立的：已有 masked local-N 证据主要覆盖 projection/trace/local surface proxy，尚未把 junction band 和最终材质/UV seam 作为一等目标。

本轮新增一个 claim-bounded 的 seam-band QA 和 `junction collar` 方案：在 grammar trace 中对新旧递归状态交界处加入保守过渡壳/transition lobe，再重建 mesh，用来筛选下一轮远端 Trellis2 texture/PBR 输入。它是下一轮算法候选，不是把现有 Trellis textured GLB 追认为无接缝。

## 输出

- summary: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/masked_naturalization_seam_optimization_20260510/summary.json`
- CSV: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/masked_naturalization_seam_optimization_20260510/masked_naturalization_seam_band_metrics_20260510.csv`
- JSON: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/masked_naturalization_seam_optimization_20260510/masked_naturalization_seam_band_metrics_20260510.json`
- contact sheet: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/masked_naturalization_seam_optimization_20260510/masked_naturalization_seam_optimization_contact_sheet_20260510.png`

## 指标表

| task | collars | LCR before | LCR after | boundary jump delta | band normal delta |
|---|---:|---:|---:|---:|---:|
| botanical_root | 18 | 1.000000 | 1.000000 | 0.000 | 0.004 |
| coral_frontier | 34 | 1.000000 | 1.000000 | 0.111 | 0.516 |
| ifs_crystal | 41 | 1.000000 | 1.000000 | 0.625 | 0.119 |

## 论文口径

- 可以写：接缝问题需要显式 junction-band 约束；我们用 seam-band metrics 作为下一轮筛选门槛。
- 不能写：现有 masked local-N 已经在最终 PBR/UV textured GLB 中完全消除接缝，或证明 watertight/manifold。
- 视觉图进入论文前仍需走 PPTX 排版再导出 PDF，并优先使用无 callout 原图做接缝 QA。

## 2026-05-11 00:50 CST 继续推进记录

用户指出“mask naturalization 没起什么作用，接缝仍有问题”后，本轮做了三层验证与修正。结论是：masked local-N / junction collar 对结构连通性有效，但 Trellis 原生 UV/PBR 贴图仍会产生肉眼可见的材质岛；如果论文要展示“接缝自然”，需要把材质连续性作为单独的 material realization claim，而不能只靠 masked naturalization。

### A. seam-aware v1 远端结果已回收

远端 run：

- `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/seam_aware_texturing_batch_20260510_remote`

本地结果：

- GLB：`results/seam_aware_texturing_batch_20260510_remote/*/textured.glb`
- metrics：`results/seam_aware_texturing_batch_20260510_remote/surface_metrics_occ64.csv`
- white zoom：`visuals/seam_aware_texturing_batch_20260510_zoom_white/seam_aware_texturing_contact_sheet_20260510.png`

结构指标：3/3 post-GLB 都是 occ64 `r0/r1/r2 components=1`，`LCR=1.0`。

视觉结论：

- `S01_root_seam_aware`：结构连通，但仍有深色环状纹理，像接缝。
- `S02_coral_seam_aware`：红/黄高对比块状贴图明显，像 UV/material island。
- `S03_ifs_seam_aware`：黑白条纹高对比，局部 seam 被放大。

因此 v1 不能作为“接缝已自然”的正例，更适合作为“仅靠 seam-aware guide 不够”的诊断。

### B. seam-aware v2 低对比多 guide 批次

新增脚本：

- `assets/prepare_seam_aware_texturing_batch_v2_20260510.py`
- `assets/launch_seam_aware_texturing_v2_20260510.sh`
- `tests/test_prepare_seam_aware_texturing_batch_v2_20260510.py`

本地输入：

- `results/seam_aware_texturing_batch_v2_20260510/`

远端 run：

- `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/seam_aware_texturing_batch_v2_20260510_remote`

本地输出：

- GLB：`results/seam_aware_texturing_batch_v2_20260510_remote/*/textured.glb`
- metrics：`results/seam_aware_texturing_batch_v2_20260510_remote/surface_metrics_occ64.csv`
- fast zoom：`visuals/seam_aware_texturing_batch_v2_20260510_zoom_white_fast/seam_aware_texturing_v2_contact_sheet_20260510.png`
- true-white flattened raw：`visuals/seam_aware_texturing_batch_v2_20260510_zoom_white_fast/*/*_white.png`

8/8 远端生成成功，8/8 surface metrics 都为 occ64 `r0/r1/r2 components=1`，`LCR=1.0`。

v2 视觉筛选：

- root 最好：`S01a_root_continuous_bark_grain_lowcontrast`。比 v1 少了强环带，但仍有局部块状阴影。
- coral：`S02b/S02c` 比 v1 色块弱一些，但 Trellis 仍会生成大块材质岛，不够发表级。
- IFS：`S03a` 干净但过于光滑/陶土感；`S03b` 太暗。

v2 的价值是证明：低对比 guide 可以降低 seam 可见性，但 Trellis UV/PBR 本身仍不稳定，不能单独支撑“最终纹理无接缝”。

### C. object-space procedural PBR 候选

新增脚本：

- `scripts/figures/seam_aware_procedural_pbr_render_20260511.py`
- `scripts/figures/flatten_zoom_raw_to_white_20260510.py`
- `scripts/figures/compose_seam_aware_pbr_qa_pptx_20260511.js`

输出：

- contact sheet：`visuals/seam_aware_procedural_pbr_20260511_zoom_white/seam_aware_procedural_pbr_contact_sheet_20260511.png`
- true-white raw：`visuals/seam_aware_procedural_pbr_20260511_zoom_white/*/*_white.png`
- PPTX-first QA deck：`paper_siga/figures/seam_aware_pbr_qa_pptx_20260511/seam_aware_pbr_qa_20260511.pptx`

视觉结论：

- `S02c_coral_procedural_ivory_pbr` 是当前最干净的 seam-continuity 候选：object-space 材质不会出现 UV 分岛，白底 zoom 中接缝自然，但视觉更像中性象牙/骨质 coral，需要 caption 写明是程序化 PBR materialization。
- `S03a_pyrite_procedural_facets_pbr` 目前是最适合 transform/lattice 叙事的 PBR 候选：金属 facet 视觉强，seam 不刺眼，但几何仍偏圆，需要只写 material/asset visualization，不写真实晶体几何。
- `S01a_root_procedural_bark_pbr` seam 最自然，但过于中性/土质，不够“漂亮 root bark”。root 下一步应继续做 object-space bark shader，而不是回到高对比 Trellis guide。

### D. 当前推荐口径

1. Masked local naturalization 的主文 claim 保持窄口径：局部 surface/material realization + junction QA，不能写 global topology repair。
2. 结构指标可以写：v1/v2 seam-aware GLB 在三/八个候选上保持 occ64 `r0/r1/r2` 单连通，`LCR=1.0`。
3. 视觉 claim 要分开：
   - Trellis UV/PBR 贴图：仍不可靠，只能作为候选/诊断。
   - object-space procedural PBR：当前最能给出自然接缝，但它是 grammar-owned material realization / rendering route，不是 Trellis 原生 texture export 已解决 seam 的证明。
4. 进入论文前，所有 seam QA 图必须从 `paper_siga/figures/*_pptx_*/*.pptx` 导出 PDF 后引用；当前已有 PPTX，尚未得到 PDF。
