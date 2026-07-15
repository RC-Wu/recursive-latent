# Traditional vs selected PS-RSLG strict one-to-one 图表状态 2026-05-10

更新时间：2026-05-10 19:45 CST

## 已完成

- 生成脚本：
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/scripts/figures/compose_traditional_vs_v24_one_to_one_20260510.py`
- 输出图：
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_vs_v24_one_to_one_zoom_20260510/traditional_vs_v24_one_to_one_zoom_20260510.png`
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_vs_v24_one_to_one_zoom_20260510/traditional_vs_v24_one_to_one_zoom_20260510.pdf`
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/traditional_vs_v24_one_to_one_zoom_20260510.png`
- 论文表：
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/traditional_vs_v24_one_to_one_summary_20260510.tex`
- 正文插入：
  - `paper_siga/main.tex` 的 `Structural Baselines and Gen-3D Comparisons` 小节。

## 图像 QA

- 拼版尺寸：`2522 x 1888`。
- 非白像素比例：`0.1255`。
- 输入均为已有白底 matched-camera zoom comparison：
  - traditional target：`case_gallery_for_user_20260510_remote_matched_candidates/01_traditional_targets/*strict_matched_zoom_comparison.png`
  - V24：`visuals/strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510/*/strict_matched_zoom_comparison.png`
  - V25 root/SC refinement：`visuals/strict_visual_matched_texture_V25_root_sc_refine_zoom_white_20260510/*/strict_matched_zoom_comparison.png`
- 每个 cell 都包含 overview callout、zoom 01、zoom 02；不是低分辨率随机 crop 拼接。

## 主文四行 pairing

| family | traditional target | selected candidate | 主文口径 |
|---|---|---|---|
| DLA/frontier | `dla_coral_cluster_900` | `V24_dla_staghorn_frontier` | main-stable；不写物理 DLA/珊瑚模拟。 |
| IFS/lattice | `ifs_fractal_lattice_d4` | `V24_ifs_pyrite_lattice` | transform-copy/lattice visual positive；r1-connected，但有 tiny r0 islands。 |
| L-system/root fan | `lsys_root_fan_d5` | `V25_lsys_root_fan_smooth_anchorD_stable` | V25 root screen 中 r0 单连通、LCR 1.0，可替换 V24 root caveat；仍只写 post-GLB diagnostic。 |
| Space colonization/crown | `sc_tree_crown_260` | `V25_sc_tree_crown_tapered_B` | V25 SC screen 中 r0 单连通、LCR 1.0；作为 tapered visual candidate，不写自然树冠物理/生物学证明。 |

## 三 seed 指标入口

- 三 seed comparison：
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V24_priority_rerun_seed3_comparison_20260510.csv`
- 三 seed rows：
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V24_priority_rerun_seed3_rows_20260510.csv`
- 推荐文档：
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_visual_matched_V24_three_seed_QA_recommendation_zh_20260510.md`
- V25 root/SC refinement 指标：
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/surface_metrics_occ64.csv`
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V25_root_sc_refine_comparison_20260510.csv`
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_visual_matched_V25_root_sc_refine_QA_recommendation_zh_20260510.md`

## 论文 claim boundary

- 传统 baselines 是结构目标/control，不是 strawman。
- Surface voxel metrics 是 post-GLB renderability/connectivity diagnostics，不是 watertight topology proof。
- Pyrite lattice 不能写 strict equivariance；只能写 empirical operator admission/screening 的 positive/caveated evidence。
- DLA/frontier 只能写 frontier-attachment 或 DLA/frontier-style asset generation，不写物理模拟。
- Root fan 从 V24 visual-only 升级为 V25 r0 单连通 diagnostic row；但这仍不是 watertight topology proof，若要写 runtime topology 需要继续补 root/handle/path-to-root sidecar。
- SC crown 采用 V25 tapered B 作为指标不退化的视觉候选；不能写成自然树冠质量已经彻底解决。

## 后续建议

1. 下一轮优先不是再跑 root，而是补 SC crown 的视觉自然度和 blockiness/roughness 指标。
2. 若篇幅紧张，当前图可作为 appendix-main hybrid；主文可只保留 DLA、IFS、root、SC 四行中的三行。
3. 若要进一步发表级，给四族再补一个同表的 blockiness/roughness/terminal-detail 指标，避免单靠 LCR。

## 2026-05-11 00:50 CST PPTX-first 更新

用户要求：现在放到论文里的图都只能先把子图排列到 PPT 文件里再导出 PDF。当前状态如下：

- 已生成 PPTX-first one-to-one deck：
  - `paper_siga/figures/traditional_vs_psrslg_one_to_one_pptx_20260510/traditional_vs_psrslg_one_to_one_20260510.pptx`
  - `paper_siga/figures/traditional_vs_psrslg_one_to_one_pptx_20260510/traditional_vs_psrslg_one_to_one_main_20260510.pptx`
  - `paper_siga/figures/traditional_vs_psrslg_one_to_one_pptx_20260510/traditional_vs_psrslg_one_to_one_20260510_preview.png`
- 本机 Keynote AppleEvent 自动导出不可靠：即使给 `scripts/figures/export_pptx_with_keynote_20260510.py` 加了 `with timeout of 1800 seconds`，1 页 main PPTX 仍长时间卡住；已手动停止后台 `osascript`，避免占用本机。
- 本机未发现 `soffice/libreoffice`，因此当前最稳妥的 PDF 产出方式是手动用 Keynote 打开上面的 main PPTX，然后 `Export To PDF` 到：
  - `paper_siga/figures/traditional_vs_psrslg_one_to_one_pptx_20260510/traditional_vs_psrslg_one_to_one_main_20260510_pptx_export.pdf`

重要：`paper_siga/main.tex` 当前仍引用旧的非 PPTX 图：

- `figures/traditional_vs_v24_one_to_one_zoom_20260510.png`

在 `_pptx_export.pdf` 未实际存在前，不应替换正文引用，避免引入编译缺文件。得到 PDF 后再把正文引用改成：

- `figures/traditional_vs_psrslg_one_to_one_pptx_20260510/traditional_vs_psrslg_one_to_one_main_20260510_pptx_export.pdf`

同样，新增 seam QA deck 已生成：

- `paper_siga/figures/seam_aware_pbr_qa_pptx_20260511/seam_aware_pbr_qa_20260511.pptx`

它也是候选 deck，尚未导出 PDF，尚未接入正文。
