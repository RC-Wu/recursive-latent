---
id: PLAN-RECURSIVE-3D-GROWTH-GEN3D-BASELINE-ABLATION-20260510
title: Recursive 3D Growth Gen-3D Baselines, Ablations, Paper Cleanup Plan
created_at: "2026-05-10T00:00:00+08:00"
status: active
tags: [plan, ralph-loop, gen3d-baseline, ablation, trellis2, hunyuan3d, paper, figures]
---

# Recursive 3D Growth Gen-3D Baseline / Ablation Ralph Plan 2026-05-10

This plan is the active recovery document for the user's 2026-05-10 request. It extends the system grammar plan and should be read first after context compaction.

## 0. Non-Negotiable Operating Constraints

- Local project root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`.
- AgentDoc root: `/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth`.
- Remote host: `a100-2`.
- Remote project root: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`.
- Use at most `3` SSH shells total for this round.
- Use only GPUs `4,5,6,7` for this project.
- Remote storage cap: `100GB`.
- Never use remote `/tmp` or `/dev/shm`; set `TMPDIR`, `XDG_CACHE_HOME`, `HF_HOME`, `HF_HUB_CACHE`, `TORCH_HOME`, `TRITON_CACHE_DIR`, and `MPLCONFIGDIR` under the remote project root.
- All formal visual results must be mesh or textured mesh renders. Matplotlib/point-cloud renders are diagnostic only.
- Standard render mode: pure white background, no visible ground plane/platform, no text inside the image; only subfigure labels below panels in Times New Roman when composing paper figures.
- Heartbeat: keep the 20-minute automation as a fallback, but do not rely on it as the main loop.

## 1. Current P0 Goal

The paper needs a rigorous comparison against ordinary 3D generation and a clean ablation/evaluation structure:

1. **Gen-3D baseline comparison:** show that one-shot 3D generation and trivial mesh-space/latent-space recursive composition do not solve controlled recursive asset generation.
2. **Same-root ablation closure:** put traditional/direct/final-only/prune/bridge/proposed and rule-only/no-N/weak-blend/masked-local-N/global-N/projection variants into fixed, comparable tables and figures.
3. **Effective-resolution evidence:** demonstrate at least two-level zoom-in where one-shot generators lose local recursive detail while the proposed finite-depth program preserves local recursive structure; report face count and GLB size.
4. **Paper cleanup:** separate main paper, figures-only pages, and appendix; rewrite the experiment section and the remaining method placeholders.
5. **Hero visual iteration:** render the strongest bismuth/pyrite/coral/Fig.24-type cases in a unified pure-white style with nested zoom-in panels.

## 2. Gen-3D Baseline Design

### 2.1 Methods to Compare

For each selected task/case:

- `TRELLIS one-shot`: image-conditioned recursive target image, plus text prompt if the available implementation supports text.
- `TRELLIS.2 one-shot`: image-conditioned recursive target image and concise recursive prompt.
- `Hunyuan3D 2.0 one-shot`: image-conditioned target and text prompt if practical.
- `TRELLIS.2 + mesh-space grammar`: generate a root mesh with Trellis2, then apply traditional recursive transforms directly to decoded mesh pieces and merge.
- `Hunyuan3D 2.0 + mesh-space grammar`: same for Hunyuan root if the model can be run in time.
- `TRELLIS.2 + trivial latent transform`: direct transform/copy sparse support or latent features without projection-stabilized grammar semantics.
- `Ours / PS-RSLG`: projection-stabilized recursive sparse-latent grammar with matched root/category/grammar.

If Hunyuan3D cannot be installed or weights are blocked, keep its row explicitly as `blocked` with exact error and still complete Trellis/Trellis2 and mesh/latent comparisons.

### 2.2 Case Selection

Use two primary controlled cases first:

1. **Branching vine/root or tree crown.**
   - Traditional target: L-system or space-colonization branching image/mesh.
   - Ours target: strongest vine/root/tree case already shown as visually acceptable.
   - Why: stable positive case, clear topology, easy zoom-in at branch junctions and terminal detail.

2. **Crystal / recursive lattice / coral-like frontier.**
   - Traditional target: IFS lattice, pyrite-like lattice, bismuth stepped scaffold, or connected coral scaffold.
   - Ours target: strongest pyrite/bismuth/coral connected textured mesh.
   - Why: non-tree domain is necessary for the paper; symmetry/transform-copy/frontier claim needs evidence.

Do not spend large time on semantically unclear cases such as `porous gloss`, `snow gear`, `snow arch`, or weak portal cases unless they are needed as failure/boundary examples.

### 2.3 Required Outputs

For each case/method:

- `.glb` or `.obj` mesh asset when available.
- Pure-white rendered overview.
- At least two nested zoom-in renders for one selected resolution comparison case.
- Metrics:
  - face count;
  - vertex count;
  - GLB file size;
  - connected components / largest component ratio;
  - orphan or fragment ratio where supported;
  - local zoom retention or terminal detail proxy.
- Status flags:
  - `success`;
  - `blocked`;
  - `fragmented`;
  - `category mismatch`;
  - `not texture/PBR usable`;
  - `diagnostic only`.

## 3. Ablation Plan

### 3.1 Same-Root Projection Matrix

Rows:

- `traditional`;
- `direct`;
- `final-only`;
- `prune`;
- `bridge`;
- `proposed`.

Columns:

- case;
- root source;
- grammar/operator;
- depth;
- largest component ratio;
- components;
- root reachability;
- orphan tip ratio;
- attachment success;
- vertex/face/GLB size;
- render QA;
- paper placement.

### 3.2 Naturalization / Projection Matrix

Rows:

- `rule-only`;
- `no-N`;
- `weak blend`;
- `masked local-N`;
- `global-N`;
- `with projection`;
- `without projection`.

This must separate local masked naturalization from projection. Projection cannot be hidden as a post-hoc mesh repair step; if a traditional repair is used, it should be labeled `post-hoc repair baseline`.

### 3.3 One-Shot vs Recursive Refinement

Metrics:

- local feature scale;
- terminal detail count;
- zoom retention score;
- face count and GLB size;
- estimated full-object high-resolution blow-up if every local region were regenerated at the same detail.

Use at least one tree/vine case and one crystal/coral case if available.

## 4. Paper Revision Plan

### 4.1 Experiment Section

- Keep only claim-bearing results in the main experiment section.
- Move broad galleries, uninspected results, guide sweeps, negative/failure matrices, and long diagnostics to appendix/supplement.
- Add an appendix start on a new page with a clear title and table-of-contents style list for main/appendix material.
- Rebuild experiment writing around:
  1. task definitions;
  2. baselines;
  3. metrics;
  4. projection-stability ablation;
  5. gen-3D baseline / latent-vs-mesh comparison;
  6. naturalization and one-shot-vs-recursive ablations;
  7. effective resolution and efficiency;
  8. selected visual results and boundaries.

### 4.2 Method Section Fixes

- Rewrite the current operator scheduling/sparse competition section as a concrete algorithm with definitions, not placeholder prose.
- Merge the recursive-refinement/material/scope sections so the method makes one clean claim: finite-depth recursive execution with selected export compatibility and explicit complexity accounting.
- Keep texture/PBR as export compatibility, not as a core method contribution.
- Leave `\EvidencePending{}` or `\ExpFigTODO{}` markers where evidence is still absent.

## 5. Hero and Figure Cleanup Plan

### 5.1 Hero Candidates

Initial cases:

- Fig.16-style bismuth;
- Fig.16-style pyrite;
- Fig.16-style coral;
- Fig.24 two strongest cases, especially the root/leaf case with brown root and green leaves if present.

Required:

- holes repaired only when repair improves topology and visual quality;
- coral surface smoothing if blocky voxelization dominates;
- pure-white no-platform render;
- multi-level nested zoom-in panels for recursive details;
- enough variations of lighting/camera to choose later.

### 5.2 Paper Figure Cleanup

- Re-render or replace every figure that still has colored backgrounds, visible platform, teaser text, method boxes, or in-image labels.
- Compose side-by-side panels without text inside the image; subfigure labels only below panels.
- Any diagnostic matplotlib result should be moved to appendix or replaced by a mesh render/table.

## 6. Parallel Work Assignment

Recommended concurrent lanes:

- Lane A: gen-3D baselines and remote environment, including TRELLIS/TRELLIS.2/Hunyuan feasibility.
- Lane B: ablation scripts/tables for same-root and naturalization comparisons.
- Lane C: paper restructuring and LaTeX compilation.
- Lane D: pure-white figure classification, hero multi-zoom render, and user case folder organization.

## 7. Progress Log

### 2026-05-10 initial activation

- User requested a new long Ralph loop with three priority changes:
  - rigorous comparison against ordinary 3D generation, especially TRELLIS/TRELLIS.2/Hunyuan3D2.0 and mesh-space/latent-space trivial recursion;
  - completion of same-root, naturalization, and one-shot-vs-recursive ablations;
  - experiment-section cleanup, appendix separation, pure-white figure replacement, and hero figure multi-zoom rendering.
- Existing project state from previous closeout:
  - remote project size was about `72G`;
  - GPUs `4/5/6/7` were idle;
  - local paper compiled at `paper_siga/main.pdf` and remained a long working draft;
  - known P0 gaps were latent-vs-mesh comparison, same-root matrix, masked naturalization, and effective-resolution evidence.
- This plan document was created as the new active compaction recovery target.

### 2026-05-10 06:05 +08

- Spawned four parallel local subagents with disjoint write scopes:
  - gen-3D baseline protocol / Hunyuan-TRELLIS feasibility;
  - ablation and metric scripts;
  - paper restructuring / LaTeX;
  - pure-white gallery and hero/zoom visual organization.
- Rendered pure-white target-condition images from traditional recursive meshes for initial one-shot generator baselines:
  - `visuals/gen3d_baseline_target_images_20260510/lsys_vine_target_{iso,front}.png`;
  - `visuals/gen3d_baseline_target_images_20260510/pyrite_lattice_target_{iso,front}.png`;
  - `visuals/gen3d_baseline_target_images_20260510/coral_dla_target_{iso,front}.png`.
- Synced the new plan and target images to `a100-2`.
- Launched a remote four-GPU strict matched texture/PBR preparation batch using existing matched OBJ inputs:
  - remote run: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/strict_visual_matched_texture_gen3dprep_20260510`;
  - GPUs: `4,5,6,7`;
  - settings: `steps=6`, `texture_size=1024` to control storage while producing inspectable PBR/textured GLBs;
  - purpose: produce more category-matched textured mesh candidates for gen-3D baseline comparisons, hero/zoom selection, and non-tree case screening.

### 2026-05-10 06:27 +08

- Local LaTeX is now usable through `/Users/fanta/Library/TinyTeX/bin/universal-darwin`; `paper_siga/main.pdf` compiles to `33` pages after installing missing algorithm packages. Remaining issues are mostly undefined citations/references and appendix float warnings, so a dedicated cleanup worker is active.
- Completed remote Trellis2 ordinary-generator baseline pass:
  - `gen3d_baseline_trellis2_one_shot_latent_nopre_20260510`: `vine/pyrite/coral` trivial latent transforms plus one vine one-shot all succeeded;
  - `gen3d_baseline_trellis2_one_shot_more_20260510`: additional `pyrite`, `coral`, and front-view `vine/pyrite` one-shot runs all succeeded and were pulled locally;
  - first preprocess attempt failed because white RGB images did not contain alpha for Trellis2 preprocessing, so the valid evidence uses `preprocess_image=False`.
- Launched a corrected remote Trellis2 texturing/PBR pass for the ordinary one-shot meshes:
  - `results/gen3d_baseline_trellis2_one_shot_textured_20260510`;
  - GPUs `4/5/6/7`;
  - settings `steps=4`, `texture_size=1024`;
  - an earlier launch had an image-path shell-variable bug and was killed/removed before use.
- Pulled `strict_visual_matched_texture_20260510` locally and started pure-white Blender renders for matched ordinary-vs-latent-vs-ours comparisons at:
  - `visuals/gen3d_baseline_matched_white_renders_20260510`;
  - the rendered evidence is mesh/PBR raw camera output; any generated comparison sheets with internal labels are not planned as final paper figures.
- Started metric aggregation for gen-3D baselines:
  - `results/gen3d_baseline_metrics_20260510`;
  - first OBJ-only metric pass works for ordinary/latent OBJ outputs but reports zero for GLB, so a GLB-aware `recursive_growth_mesh_metrics.py` pass is running.
- New subagents after closing older completed lanes:
  - mesh-space trivial recursion baseline implementation;
  - LaTeX reference/label cleanup;
  - hero multi-zoom pure-white render;
  - Hunyuan3D2.0 feasibility and fair-baseline protocol.

### 2026-05-10 07:18 +08

- Completed the first rigorous ordinary-3D-generator baseline block:
  - Trellis2 one-shot image-conditioned baselines for vine, pyrite, and coral;
  - Trellis2 trivial sparse-latent `copy_shift_upper_z` baselines for vine, pyrite, and coral;
  - generated-root mesh-space S/R/T direct-merge baselines for vine and pyrite;
  - PS-RSLG candidate rows for vine, pyrite, and coral.
- A dedicated worker produced:
  - `results/gen3d_baseline_metrics_20260510/gen3d_baseline_summary_table_20260510.csv`;
  - `paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex`;
  - `docs/evaluation/ablation_and_gen3d_status_zh_20260510.md`;
  - `results/ablation_summary_20260510/*`.
- Key quantitative finding:
  - Trellis2 one-shot is acceptable only for the easy vine row (`occupancy LCR=1.000`) but fragmented for pyrite (`0.127`) and coral (`0.600`);
  - trivial latent copy remains fragmented for pyrite (`0.102`) and semantically uncontrolled for coral despite higher occupancy LCR;
  - mesh-space generated-root copy-paste produces extreme raw mesh fragmentation (`101699` / `173575` face components for vine/pyrite depth-2);
  - PS-RSLG pyrite/coral strict textured rows remain connected under the occupancy proxy (`LCR=1.000`), while the exact strict vine row is weak and should be replaced by the stronger vine stage-5 reference in paper figures.
- Fixed the Blender render scripts so future paper renders use a real white RGB background rather than transparent alpha:
  - `scripts/figures/matched_camera_zoom_render_20260510.py`;
  - `scripts/figures/hero_multi_zoom_render_20260510.py`.
- Generated a first clean white-background gen-3D overview figure:
  - `paper_siga/figures/gen3d_baseline_overview_clean_20260510.png`.
  - This is acceptable as interim visual evidence but still uses an older neutral/material mix and does not include the mesh-space column.
- Completed two remote Trellis2 2048-texture fairness batches and pulled the first batch locally:
  - `visuals/gen3d_baseline_texture_fairness_20260510`;
  - `visuals/gen3d_baseline_texture_fairness2_20260510`.
  - These include textured one-shot, latent-copy, and mesh-space generated-root controls for a fairer visual comparison.
- Started local Blender rendering for the final fair 3x4 textured comparison matrix at:
  - `visuals/gen3d_baseline_texture_fair_matched_20260510`;
  - target paper output: `paper_siga/figures/gen3d_baseline_texture_fair_clean_20260510.png`.
- Hero multi-zoom render produced a candidate image, but it used the older transparent/gray-background setup. It must be rerun or flattened/recomposed under the corrected white-background renderer before it can enter the paper.


### 2026-05-10 07:51 +08

- Updated heartbeat instructions for the active 2026-05-10 gen-3D baseline / ablation Ralph loop.
- Closed two read-only subagents after incorporating their reports:
  - `docs/evaluation/ablation_completion_and_main_appendix_recommendation_zh_20260510_agent.md`;
  - `docs/paper/experiment_section_restructure_review_zh_20260510_agent.md`.
- Integrated cautious paper updates:
  - `paper_siga/drafts/effective_resolution_status_table_20260510.tex` added to the effective-resolution discussion;
  - `paper_siga/drafts/ablation_status_tables_20260510.tex` added to the appendix as status/coverage evidence, not as completed ablation;
  - `main.tex` now states Hunyuan3D is an environment/reproducibility audit, not a model-quality claim.
- Recompiled `paper_siga/main.pdf` successfully after these changes; no undefined references remain in `main.log`; current PDF is a 38-page working draft with expected appendix float/accessibility warnings.
- Completed and flattened v3b connected multi-zoom renders to pure-white RGB:
  - `visuals/strict_visual_matched_texture_v3b_connected_zoom_20260510_flatwhite`;
  - `paper_siga/figures/strict_visual_v3b_connected_overview_clean_20260510.png`;
  - `paper_siga/figures/strict_visual_v3b_connected_multizoom_clean_20260510.png`.
- Launched remote gap-fill ablation jobs under `results/masked_naturalization_gapfill_20260510`:
  - GPUs 4/5: L-system and IFS masked alpha grids with alpha 0.0 / 0.25 / 1.0;
  - GPUs 6/7: rule-only direct L-system/IFS;
  - follow-up GPUs 6/7: non-tree coral_v3b and pyrite_v3b masked alpha grids.
- First summary inspection shows all six gap-fill summaries completed `ok` or wrote expected rule-only summaries. Remote metrics are now running over `results/masked_naturalization_gapfill_20260510/mesh_metrics.csv` to convert this into rule-only/no-N/weak-blend/masked-local-N evidence.

### 2026-05-10 08:20 +08

- Completed the requested pause-point closeout for the gen-3D baseline / ablation subtask.
- Gen-3D baseline paper table was corrected:
  - `paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex` now uses the measured mesh-space generated-root GLB sizes (`4.7` MB vine, `8.8` MB pyrite) rather than the stale larger values.
  - `paper_siga/main.pdf` recompiles successfully as a 39-page working draft after the new appendix figures.
- Naturalization/projection ablation aggregator was updated:
  - `assets/naturalization_projection_ablation_aggregation_20260510.py` now ingests the first masked-naturalization gap-fill summaries.
  - `paper_siga/drafts/ablation_status_tables_20260510.tex` now reports partial rows for rule-only, no-N, weak blend, and masked local-N instead of incorrectly listing them as completely absent.
- Exported new same-root textured GLB ablation rows through Trellis2:
  - L-system/fork-side: rule-only, no-N alpha 0, weak blend alpha 0.25, masked local-N alpha 1.0.
  - Non-tree: coral weak/local-N and pyrite weak/local-N.
  - Local GLB folders:
    - `results/gapfill_texturing_selected_20260510`;
    - `results/gapfill_non_tree_texturing_selected_20260510`.
- Rendered new pure-white appendix/status figures:
  - `paper_siga/figures/gapfill_naturalization_textured_overview_raw_clean_20260510.png`;
  - `paper_siga/figures/gapfill_naturalization_textured_zoom_01_clean_20260510.png`;
  - `paper_siga/figures/gapfill_non_tree_naturalization_textured_overview_raw_clean_20260510.png`;
  - `paper_siga/figures/gapfill_non_tree_naturalization_textured_zoom_01_clean_20260510.png`.
- Updated `paper_siga/main.tex` to include the L-system and non-tree naturalization status figures in the appendix, with captions explicitly stating that they are diagnostic/status evidence rather than closed positive claims.
- Created the user-facing case-selection folder:
  - `visuals/case_selection_by_type_20260510/`;
  - 67 valid symlinks grouped by plant/root/tree, crystal/coral/DLA, sci-fi/mechanical, gen-3D baselines, ablation depth, hero zoom, and discard/repair candidates.
- Wrote the closeout human report:
  - `docs/obsidian_human_reports/2026-05-10_gen3d_ablation_round_closeout.md`.
- Stopped the over-broad full recursive metric scan over `masked_naturalization_gapfill_20260510` after it ran for more than 20 minutes without producing CSV output. Follow-up should replace it with a selected-final-only metric script.
- Cleaned remote reusable caches only:
  - removed remote `cache/triton/*` and `cache/tmp/*`;
  - remote project size dropped from about `78G` to about `74G`;
  - no experiment results, weights, GLBs, OBJs, or CSV summaries were deleted.
- Current state:
  - remote GPUs `4/5/6/7` are idle;
  - no required remote experiment process is left running;
  - a queue-style `strict_visual_matched_texture_v4_seed20260512_20260510` launcher was found still starting additional v4 texture candidates during closeout, so it and its active child processes were stopped to honor the user-requested pause; already completed v4 GLBs were preserved;
  - remaining high-priority gaps are coral mesh-space generated-root baseline, selected-final-only naturalization metrics, DLA/crystal connectedness repair/cache experiments, and paper section compression.
