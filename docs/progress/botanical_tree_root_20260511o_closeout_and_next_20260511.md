# Botanical / Tree-Root 20260511o Closeout And Next Loop

Date: 2026-05-11 14:40 CST  
Status: closed for diagnostics; 20260511p launched as the next narrow repair batch  
Local root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU rule: use only GPUs `4,5,6,7`.  
Evidence rule: do not call any case publication-grade without OBJ/GLB, metrics, controlled Blender QA, zoom/contact sheets, provenance/license notes, and paper-safe writing.

## Latest Remote State

`20260511o` remote batch has finished all four lanes:

- `spider_positive`: completed.
  - `spider_broad_tipclean_d4_yneg_20260511o`
  - `spider_runner_terminal_d4_yneg_20260511o`
- `polyhaven_cc0`: completed.
  - `polyhaven_fern_all_yneg_20260511o`
  - `polyhaven_fern_part_yneg_20260511o`
  - `polyhaven_potted_leaves_yneg_20260511o`
- `tree_root_leaf`: completed with partial failure status caused by a wrong alias in the original launcher.
  - Valid outputs exist for `v25l_root_primary_branch` and `v25l_root_two_phase`.
  - `v25n_whole_root_single_corner` was wrong; the actual grammar alias is `v25n_whole_root_corner`.
  - The launcher was fixed locally and synced to remote.
  - A separate one-off rerun was completed as `tree_rootfan_wholeroot_corner_fix_ypos_20260511o`.
- `image_roots`: completed.
  - `spider_photo_rosette_cc0` is the only relatively low-face image root (`~99k` faces), but still has high token count (`3545`) and remains diagnostic until Blender/root-quality QA.
  - `spider_rosette_single_pd`, `rubber_fig_trunk_contact_cc0`, and `fiddlehead_single_curl_cc0` are too heavy for positive recursion claims in their raw form. They are root-quality diagnostics unless simplified/cropped/remeshed.

Remote batch size after completion is about `1.1G`; total remote project size is about `139-140G`, below the relaxed `200GB` cap.

## Immediate Gate

Completed:

1. Full `20260511o` remote metrics were pulled locally:
   - `results/botanical_tree_root_recursive_remote_20260511o_pull/metrics/botanical_tree_root_metrics_20260511o.csv`
   - `results/botanical_tree_root_recursive_remote_20260511o_pull/metrics/botanical_tree_root_metrics_20260511o.json`
2. The one-off `tree_rootfan_wholeroot_corner_fix_ypos_20260511o` was included in selected OBJ pull and Blender QA.
3. Lightweight outputs and selected OBJs were pulled locally.
4. Controlled Blender QA was rendered:
   - `results/botanical_tree_root_recursive_remote_20260511o_pull/blender_qa_20260511o/contact_sheet_blender_selected_20260511o_whitecomposite.png`
   - `results/botanical_tree_root_recursive_remote_20260511o_pull/blender_qa_20260511o/spider_depth_sequence_blender_20260511o_whitecomposite.png`

Primary selected QA targets:

- `spider_broad_tipclean_d4_yneg_20260511o/v25l_spider_leaf_tip_clean/depth_04`
- `spider_broad_tipclean_d4_yneg_20260511o/v25k_spider_terminal_leaflet/depth_04`
- `spider_runner_terminal_d4_yneg_20260511o/v25k_spider_terminal_leaflet/depth_04`
- `spider_runner_terminal_d4_yneg_20260511o/v25l_spider_leaf_tip_clean/depth_04`
- `polyhaven_fern_all_yneg_20260511o/v25n_fern_pinnae_sparse/depth_03`
- `polyhaven_fern_part_yneg_20260511o/v25k_spider_terminal_leaflet/depth_03`
- `polyhaven_potted_leaves_yneg_20260511o/v25k_spider_terminal_leaflet/depth_03`
- `tree_rootfan_primary_ypos_20260511o/v25l_root_primary_branch/depth_04`
- `tree_rootfan_primary_ypos_20260511o/v25l_root_two_phase/depth_04`
- `tree_rootfan_wholeroot_corner_fix_ypos_20260511o/v25n_whole_root_corner/depth_04`
- `tree_pine_leaf_yneg_20260511o/v25n_pine_leaf_gated/depth_04`
- `tree_pine_leaf_yneg_20260511o/v25l_pine_leaf_cluster_clean/depth_04`
- `tree_pine_leaf_yneg_20260511o/v25k_pine_terminal_needles/depth_04`

## Final 20260511o Interpretation Boundary

Do not overclaim from summary JSON alone or from metric positives without Blender depth QA.

- The one-off `tree_rootfan_wholeroot_corner_fix_ypos_20260511o` completed successfully, but token counts and bbox barely change after depth 1. It is likely a weak/no-op macroscopic stress row unless Blender QA reveals clear recursive structure.
- The user-requested `tree_root_leaf` dual recursion is still open until the root-side branch hierarchy passes depth 4 visually and the leaf-side recursion is merged or shown as a coherent paired subprogram.
- `polyhaven_potted_leaves` is high-face but semantically useful; it needs Blender QA because metrics alone may hide flat sheets or leaf islands.
- `spider_*` rows remain the strongest plant-positive direction, but they are spider/rosette substitutes rather than proof that the original fifth hero plant cut works.
- Blender depth sequence confirms that the strongest spider rows are clean-ish but too similar across depths. They are positive directions, not final multi-depth evidence.
- `tree_rootfan_primary_ypos_20260511o/v25l_root_primary_branch` and `v25l_root_two_phase` are rejected as weak-depth-change rows.
- `tree_v25_bud_d1_spiky`, `scifi_old_tight_d1`, `arch_clean_key_d2`, and `crown_old_rim_d1` remain geometry candidates from the earlier 20260510f repair/PBR batch, but this botanical p loop should not mix them into plant/tree-root completion claims.

## Baseline Status To Preserve

TRELLIS1 / classic:

- Not OK because the environment is not runnable yet, not because the model has been fairly tested and failed.
- Repo/checkpoint/partial env exist.
- Current blockers are dependency/runtime stack issues: `torchvision::nms`, missing or unstable `open3d`, missing `kaolin`, and likely CUDA/PyTorch extension compatibility.
- Paper wording should say `blocked/not completed` unless a runnable one-shot smoke is produced.

Hunyuan3D:

- Shape-only and fair text-root mesh-space baselines have substantially progressed.
- `publication_hunyuan_recursive_guides_20260510` is a one-shot guide-image pool, not the fair mesh-space recursion baseline.
- `publication_hunyuan_text_root_meshspace_20260511` closes the fair text-root mesh-copy negative control for tree, pyrite, coral, and bismuth-style comparison rows.
- Remaining Hunyuan gaps are paint/texture baseline closure plus unified Blender render/table integration.
- Do not write high occupancy LCR as success for Hunyuan mesh-copy rows; raw component counts and `copy_repetition_score=1.0` are the negative-control evidence.

## Next Loop After 20260511o QA

20260511p is now the next loop:

- Plan: `docs/progress/botanical_tree_root_20260511p_execution_plan_20260511.md`
- Launcher: `assets/run_botanical_tree_root_three_track_remote_20260511p.sh`
- Output root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/botanical_tree_root_recursive_remote_20260511p`

If 20260511p passes at least one plant/fern candidate:

1. Create paper-safe Blender contact sheets and per-case zooms.
2. Export selected OBJ/GLB with provenance and license notes.
3. Add rows to the candidate matrix with `positive_candidate`, `supplement_candidate`, or `diagnostic_only`.

If 20260511o does not pass:

1. Stop perturbing the failed original fifth-hero true cuts.
2. Use CC0 Poly Haven or a cleaner manually extracted petiole/leaf root as the next root source.
3. For tree roots, implement explicit sidecar handles or root-first-split cuts rather than quantile/global masks alone.
4. Treat image-root outputs as root-acquisition diagnostics and simplify before recursion.
