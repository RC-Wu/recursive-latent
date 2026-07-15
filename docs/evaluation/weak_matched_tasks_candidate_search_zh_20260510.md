# weak strict matched 任务候选搜索记录（2026-05-10）

## 范围

本次只做本地已有结果/视觉资产搜索，不启动远程任务，不改 `paper_siga` 或 AgentDoc plan。重点任务：

- `ifs_branch_tree_d6`
- `ifs_radial_ornament_o8_d4`
- `dla_frontier_sheet_700`
- `dla_coral_cluster_900` / `dla_aniso_crystal_800`

输出映射：

- `results/weak_matched_tasks_candidate_search_20260510/candidate_mapping.csv`

## 最强建议

1. `ifs_branch_tree_d6`：优先替换为 `results/strict_matched_psrslg_proxy_20260510_seed310_v2/ifs_transform_branching_tree/ours_psrslg_transform_copy.obj`。这是目前找到的最严格 transform-copy 对齐候选，比 `tree_compete_s3` 的语义更正确；但它仍是 proxy，manifest 中 strict surface component 很多，需要先 matched-camera render/repair 再决定能否进主文。
2. `ifs_radial_ornament_o8_d4`：优先测试 `visuals/cache_selected_texture_20260509_rerun1516/cache_radial_transform_fusion_steps8_tex2048_xformers/textured.glb`。它比当前 `transform_radial4_*` 边界候选连通性强得多；另保留 `visuals/public_guide_textured_glb_20260509e/transform_radial4_gear_steps8_tex2048_xformers/textured.glb` 作为更像 hard-surface ornament 的视觉候选，但其连通指标差，只能先做 boundary/repair。
3. `dla_frontier_sheet_700`：优先测试 `visuals/public_guide_textured_glb_20260509e/dla_side_octopus_steps8_tex2048_xformers/textured.glb`。它比通用 `coral_dla_octopus` 更接近 side/frontier mode，但 sheet silhouette 仍未确认。
4. `dla_coral_cluster_900`：优先测试 `visuals/coral_density_extreme_texture_20260509/coral_density_param_density_0p25_octopus_steps8_tex2048_xformers/textured.glb`。它是找到的更可能降低 bead/chunk 感的现有 coral 资产，且 surface r0/r1/r2 均连通。
5. `dla_aniso_crystal_800`：若只需要 crystal-like 边界候选，`visuals/connected_scaffold_v2_textured_glb_hq_20260509/bismuth_hopper_pyrite_hq_steps8_tex2048_xformers/textured.glb` 最稳；但它是 ordered crystal，不是 stochastic DLA。

## 候选明细

### 1. IFS branch tree

#### `psrslg_transform_copy_proxy`

- 路径：`results/strict_matched_psrslg_proxy_20260510_seed310_v2/ifs_transform_branching_tree/ours_psrslg_transform_copy.obj`
- 视觉证据：
  - `visuals/strict_matched_psrslg_proxy_20260510_seed310_v2/renders/ifs_transform_branching_tree__ours_psrslg_transform_copy_iso.png`
  - `visuals/strict_matched_psrslg_proxy_20260510_seed310_v2/renders/ifs_transform_branching_tree__ours_psrslg_transform_copy_front.png`
  - contact：`visuals/strict_matched_psrslg_proxy_20260510_seed310_v2/strict_matched_proxy_contact_v2_20260510.png`
- 适配度：强 mode match。manifest recipe 写明 `transform_copy`, `scale_decay`, `typed_anchor_rewrite`, `root_projection`, `tip_kernel`，比 `tree_compete_s3` 更适合回应 “IFS branch tree 不是 transform-copy” 的问题。
- 风险：proxy 视觉质量有限；manifest 中 `occ_comp_6n=61238`, `occ_lcr_6n=0.000064`，说明 strict voxel surface 很碎。不能直接说 paper-ready。
- 下一步：应做 matched-camera render + repair/naturalization smoke。如果修不好，主文可作为 “strict-mode proxy but not final visual asset”。

#### `ifs_branch_tree_textured_matched_guide`

- 路径：`visuals/traditional_baseline_texture_matched_guide_20260509/ifs_branch_tree_matched_steps6_tex1024_xformers/textured.glb`
- 视觉证据：已有严格 pair 图仍用旧映射，需单独渲染该 GLB；相关旧图 `visuals/strict_matched_pair_candidates_20260510/ifs_branch_tree_d6/ifs_branch_tree_d6__vs__tree_compete_s3.png`
- 适配度：有 IFS branch tree guide 名称，指标比 proxy 好，`results/baseline_one_to_one_metrics_20260510/metrics.csv` 中 vertex-occupancy LCR 约 0.92。
- 风险：目录名是 `traditional_baseline_texture_matched_guide`，provenance 更像 baseline-guide texturing，不应直接当 ours。
- 下一步：只做 provenance/screening；除非确认生成链路属于 ours，否则不要进 mapping 主推。

### 2. IFS radial ornament

#### `cache_radial_transform_fusion`

- 路径：`visuals/cache_selected_texture_20260509_rerun1516/cache_radial_transform_fusion_steps8_tex2048_xformers/textured.glb`
- 视觉证据：
  - `visuals/cache_selected_texture_20260509_rerun1516/renders/cache_radial_iso.png`
  - `visuals/cache_selected_texture_20260509_rerun1516/renders/cache_radial_front.png`
  - contact：`visuals/cache_selected_texture_20260509_rerun1516/renders/cache_selected_rerun1516_contact.png`
- 指标证据：`visuals/cache_selected_texture_20260509_rerun1516/surface_metrics_occ64.csv` 中 r0: 18 comps, LCR 0.9996；r1: 1 comp, LCR 1.0。
- 适配度：当前搜索中最强 “radial + connected” 候选。比 mode-matched `transform_radial4_pyrite/bismuth` 更可用。
- 风险：需要人工看渲染判断是否真像 radial ornament；可能只是 transform fusion，不一定有清晰 ornament 轮廓。
- 下一步：优先 matched-camera render/test，若视觉成立就替换旧 `transform_radial4_*`。

#### `transform_radial4_gear`

- 路径：`visuals/public_guide_textured_glb_20260509e/transform_radial4_gear_steps8_tex2048_xformers/textured.glb`
- 视觉证据：
  - `visuals/public_guide_textured_glb_20260509e/renders/radial_gear_iso.png`
  - contact：`visuals/public_guide_textured_glb_20260509e/renders/public_guide_textured_glb_contact_sheet_20260509e.png`
- 指标证据：`results/public_guide_textured_glb_metrics_20260509e/metrics.csv` 中 vertex-occupancy `occupancy_component_count_6n=862`, LCR 约 0.618。
- 适配度：更像 hard-surface/radial ornament，语义强。
- 风险：连通性差，不能直接取代主文候选。
- 下一步：作为视觉/repair 候选；若要主文使用，先做 repair 或 naturalization。

### 3. DLA frontier sheet

#### `dla_side_octopus_public_guide`

- 路径：`visuals/public_guide_textured_glb_20260509e/dla_side_octopus_steps8_tex2048_xformers/textured.glb`
- 视觉证据：
  - `visuals/public_guide_textured_glb_20260509e/renders/dla_side_octopus_iso.png`
  - contact：`visuals/public_guide_textured_glb_20260509e/renders/public_guide_textured_glb_contact_sheet_20260509e.png`
- 指标证据：`results/public_guide_textured_glb_metrics_20260509e/metrics.csv` 中 vertex-occupancy r0 26 comps, LCR 约 0.966。
- 适配度：比当前 `coral_dla_octopus` 更接近 side/frontier mode。
- 风险：仍未证明是 sheet silhouette；可能只是 side-branch coral/octopus。
- 下一步：做 matched-camera pair，和 `dla_frontier_sheet_700` 并排看轮廓；当前标记为 `candidate_boundary`。

#### `psrslg_frontier_naturalized_proxy`

- 路径：`results/strict_matched_psrslg_proxy_20260510_seed310_v2/dla_crystal_cluster/ours_psrslg_frontier_naturalized.obj`
- 视觉证据：
  - `visuals/strict_matched_psrslg_proxy_20260510_seed310_v2/renders/dla_crystal_cluster__ours_psrslg_frontier_naturalized_iso.png`
  - `visuals/strict_matched_psrslg_proxy_20260510_seed310_v2/renders/dla_crystal_cluster__ours_psrslg_frontier_naturalized_front.png`
- 适配度：strict DLA/frontier 方法证据强；manifest recipe 包含 `frontier_attachment`, `masked_local_naturalization`, `neighbor_bridge`, `largest_root_projection`，且 manifest occupancy connected。
- 风险：case 是 `dla_crystal_cluster`，不是 explicit frontier sheet。若替代 `dla_frontier_sheet_700` 会被质疑 silhouette 不一致。
- 下一步：作为 DLA/coral-crystal strict proxy evidence；不直接替 sheet，除非补 sheet render/shape check。

### 4. DLA coral / crystal

#### `coral_density_0p25_octopus`

- 路径：`visuals/coral_density_extreme_texture_20260509/coral_density_param_density_0p25_octopus_steps8_tex2048_xformers/textured.glb`
- 视觉证据：
  - `visuals/coral_density_extreme_texture_20260509/renders/density_0p25_iso.png`
  - `visuals/coral_density_extreme_texture_20260509/renders/density_0p25_front.png`
  - contact：`visuals/coral_density_extreme_texture_20260509/coral_density_extreme_contact_20260509.png`
- 指标证据：`visuals/coral_density_extreme_texture_20260509/surface_metrics_occ64.csv` 中 r0/r1/r2 都是 1 component, LCR 1.0。
- 适配度：比当前 `coral_dla_octopus` 更值得试，因为低 density 可能减少 bead/chunk 观感，同时保持 coral/DLA 语义和连通。
- 风险：仍是 octopus guide/material，不一定像传统 DLA cluster。
- 下一步：优先 matched-camera render/test；若视觉确实更自然，可替换 `dla_coral_cluster_900 -> coral_dla_octopus`。

#### `volumetric_dla_coral_bismuth_hq`

- 路径：`visuals/connected_scaffold_v2_textured_glb_hq_20260509/volumetric_dla_coral_bismuth_hq_steps8_tex2048_xformers/textured.glb`
- 视觉证据：
  - `visuals/connected_scaffold_v2_textured_glb_hq_20260509/renders/volumetric_dla_coral_bismuth_hq_iso.png`
  - `visuals/connected_scaffold_v2_textured_glb_hq_20260509/renders/volumetric_dla_coral_bismuth_hq_front.png`
  - contact：`visuals/connected_scaffold_v2_textured_glb_hq_20260509/connected_scaffold_v2_hq_selected_contact_white_seamless_rerun2035.png`
- 指标证据：`visuals/connected_scaffold_v2_textured_glb_hq_20260509/surface_metrics_occ64_rerun1925.csv` 中 r0/r1/r2 全连通。
- 适配度：适合 DLA coral/crystal hybrid。比 octopus material 更偏 crystal/hard surface。
- 风险：几何 scaffold 与当前 `volumetric_dla_coral_octopus_hq` 相同，不能解决 chunk scaffold 本身。
- 下一步：作为 crystal/coral material alternate；不是首选 coral naturalization。

#### `bismuth_hopper_pyrite_hq`

- 路径：`visuals/connected_scaffold_v2_textured_glb_hq_20260509/bismuth_hopper_pyrite_hq_steps8_tex2048_xformers/textured.glb`
- 视觉证据：
  - `visuals/connected_scaffold_v2_textured_glb_hq_20260509/renders_white_seamless_rerun2035/bismuth_hopper_iso.png`
  - `visuals/connected_scaffold_v2_textured_glb_hq_20260509/renders_white_seamless_rerun2035/bismuth_hopper_front.png`
- 指标证据：`visuals/connected_scaffold_v2_textured_glb_hq_20260509/surface_metrics_occ64_rerun1925.csv` 中 r0 2 comps, LCR 0.9996；r1/r2 连通。
- 适配度：目前最稳 crystal-like asset。
- 风险：ordered crystal，不是 stochastic DLA。只能用于 `dla_aniso_crystal_800` 的 boundary/lattice/crystal 叙述，不能替代 DLA coral。
- 下一步：只在需要 crystal boundary 时使用。

## 不建议直接提升的候选

- `transform_radial4_pyrite` / `transform_radial4_bismuth`：mode 对，但之前已记录视觉碎、透明片多；新找到的 `cache_radial_transform_fusion` 和 `transform_radial4_gear` 更值得继续。
- `coral_dla_octopus`：指标强，但当前失败点就是 bead/chunk 感；优先用 `coral_density_0p25_octopus` 做替代测试。
- `dla_side_bismuth`：mode 接近 frontier sheet，但已有评价是碎片明显；`dla_side_octopus` 更值得先看。
- `tree_compete_s3` for `ifs_branch_tree_d6`：视觉树类强，但不是 transform-copy，建议从 strict branch mapping 中降级。

## 下一步最小测试清单

1. 对 `psrslg_transform_copy_proxy`, `cache_radial_transform_fusion`, `dla_side_octopus_public_guide`, `coral_density_0p25_octopus` 做 matched-camera 白底对比图。
2. 对 `cache_radial_transform_fusion` 和 `transform_radial4_gear` 同屏比较：前者看连通/整体，后者看 hard-surface ornament 语义。
3. 对 `coral_density_0p25_octopus` 与当前 `coral_dla_octopus` 做局部 zoom，重点看 bead/chunk 是否下降。
4. 如果 `dla_frontier_sheet_700` 仍找不到 sheet silhouette，就保留为 screening failure，不要硬配 coral。
