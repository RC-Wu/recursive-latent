# Botanical / Tree-Root Parallel Ralph Plan

Date: 2026-05-11 CST  
Status: active, publication-grade closure loop  
Local root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU policy: use only GPUs `4,5,6,7`; at most four concurrent GPU lanes.  
Evidence rule: no result is complete without OBJ/GLB outputs, metrics CSV/JSON, Blender render QA, and a paper-safe provenance note.

## User Objective

Run three high-intensity tracks in parallel until publication-grade assets exist:

1. **Plant-leaf recursive case**: choose or cut a strong leaf/root mesh first, then run TRELLIS2/SLat recursive grammar sweeps with clear multi-depth differences, clean semantics, and minimal mesh breakage.
2. **Spider plant / fern / recursive-root case**: search/download license-compatible meshes and images; generate TRELLIS2 roots from the best images where useful; recursively grow them with root-first grammar choices.
3. **Hero `tree_root_leaf` case**: make both root and leaf structures recursive. The root side should show natural thick-to-thin branching with at least four depths, no seams, no major islands, and no obvious voxel artifacts.

Heartbeat `r-slg-long-task-heartbeat` has been updated to this three-track goal. It is a fallback only; the active loop should continue directly.

## Current Findings To Preserve

### 20260511g Plant/Spider Sweep

Remote outputs: `results/fern_leaf_recursive_remote_20260511g`  
Local pull: `results/fern_leaf_recursive_remote_20260511g_pull`  
Metrics: `results/fern_leaf_recursive_remote_20260511g_pull/metrics/fern_leaf_recursive_metrics_20260511g.csv`  
Blender QA: `results/fern_leaf_recursive_remote_20260511g_pull/blender_qa_selected/selected_blender_qa_sheet_20260511g.png`

Verdict: diagnostic, not publication-grade.

- `spider_broad_zpos` has the cleanest rosette body. `v25g_root_crown_conservative` keeps good occupancy connectivity through depth 3, with depth-3 occupancy LCR about `0.991`, but visual depth difference is too weak and growth is partly sideways.
- `spider_runner_zpos` preserves runner/plantlet semantics, but `v25g_root_plantlet_sprout` depth-3 occupancy LCR drops to about `0.976` and visible floating speckles accumulate.
- `v25g_root_crown_then_sprout` is excluded for positive claims because it compounds masks each depth and increases fragmentation.
- Blender QA shows useful broad-leaf and hanging-plant silhouettes, but not clean recursive leaf growth. It reads as rod/strip extension plus dust rather than natural multi-scale recursion.

### Root Cause Fixes For 20260511h

- The TRELLIS2 recursive workflow rotates input vertices before encoding: original `z` becomes latent `-y`, and original `y` becomes latent `z`. Therefore botanical upward growth for OBJ roots should first use `--growth-axis y --growth-sign -1`, not `z,+1` or `y,+1`.
- The 20260511g runner candidate has an indexing bug: basal roots are appended before runners/plantlets, but later rootlet details iterate the last `root_count` nodes, which are plantlet/runner nodes when `plantlets=True`. This mixes rootlets into child plantlets and creates semantic clutter.
- The 20260511g masks are generic. On a flat rosette, crown/rim/base can select leaves, runner tips, or rootlets depending on axis. The next sweep should use smaller single-op aliases first and avoid broad sector copying.

## Track A: Plant-Leaf Recursive Case

### Inputs

- Existing fifth hero plant-derived roots:
  - `results/plant_leaf_recursive_root_20260511/inputs/plant_leaf_green_cluster_root.obj`
  - `results/plant_leaf_recursive_root_20260511/inputs/plant_leaf_base_mid_cluster_root.obj`
  - `results/plant_leaf_recursive_root_20260511/inputs/plant_leaf_full_upright_root.obj`
- Existing 20260511g generated/procedural roots:
  - `results/fern_root_candidates_20260511g/spider_rosette_broadleaf_b/spider_rosette_broadleaf_b.obj`
  - `results/fern_root_candidates_20260511g/spider_rosette_runner_plantlets_c/spider_rosette_runner_plantlets_c.obj`
- New 20260511h corrected roots should include:
  - cleaner broad rosette root with fewer arms, thicker closed leaves, and explicit basal root indices;
  - corrected runner/plantlet root with rootlets attached only to basal root nodes;
  - leaf-only or leaf-cluster cuts from the existing fifth hero plant, if they remain connected after TRELLIS2 encode/decode.

### Experiments

Run axis-corrected sweeps first:

- root: corrected broad rosette; grammars: basal crown micro, leaf tiplet micro, broad crown then very small tiplet; depth `0..4`; axis/sign `y,-1`.
- root: corrected runner/plantlet; grammars: runner distal micro, basal crown micro; depth `0..3`; axis/sign `y,-1`.
- root: fifth-hero plant cut roots; grammars: conservative single-op aliases only; depth `0..2` first, extend only if visually strong.

### Acceptance

- Every displayed depth is attractive in Blender white/studio renders.
- Depth differences are visible at object scale and in zoom; no “same mesh with dust”.
- Occupancy LCR target is `>=0.98` for main images, with no visually significant islands.
- If postprocess is used, before/after metrics and renders must show that it removes small defects without hiding a failed grammar.

## Track B: Spider Plant / Fern / Recursive Roots

### External Sources To Download Or Verify

Preferred license-clean image seeds:

- Wikimedia Commons `Spider plants (Chlorophytum comosum).jpg`, CC0/Public Domain.
- Wikimedia Commons `Fiddlehead-ferns.jpg`, CC0/Public Domain.
- PublicDomainPictures aerial prop roots, CC0/Public Domain.
- PublicDomainPictures green succulent rosette, CC0/Public Domain.

Mesh sources worth testing:

- Sketchfab `CC0 Old World Forked Fern`, CC0/Public Domain, high-poly and should be decimated before deep recursion.
- Sketchfab `CC0 Japanese Rockcap Fern`, CC0/Public Domain, very high-poly and only useful after simplification.
- Sketchfab `Spider Plant` by sauti, CC BY attribution required, manageable triangle count; use if license attribution is acceptable.
- Sketchfab `Root Structure`, CC BY attribution required, promising for recursive roots.
- Kenney/Eclair Nature Kit GLB pack, CC0, useful as low-poly fallback but not botanically detailed.

Avoid NoAI assets as generative inputs.

### Experiments

- Download/crop the best CC0/public-domain images and run TRELLIS2 image-to-root generation on GPUs 4-7.
- Run depth-0 encode/decode QA before recursive sweeps.
- Use root-specific grammar:
  - fern frond: tiplet and pinnae growth along a midrib, but with very small lateral displacement;
  - fiddlehead/crozier: spiral echo only if the root has a true curl;
  - spider plant: basal/runner/plantlet micro aliases with corrected `y,-1` axis;
  - dangling roots: thick-to-thin root branch copy, shrink, and naturalization.

### Acceptance

- At least 10 candidates per category should be available for selection when practical: plant/leaf, spider/rosette, fern/crozier, and root/tree-root.
- Final promoted case must have mesh/root provenance, license note, input guide image if used, remote command manifest, metrics, and Blender QA.

## Track C: Hero `tree_root_leaf` Case

### Current Known Assets

Hero combo records identify `tree_root_leaf` as:

- `visuals/hero_botanical_variants_20260510/tree_compete_s3_green_leaf_brown_root.glb`
- related source family: tree/root/canopy assets in `strict_visual_matched_texture_*`, especially V23/V25/V27/V28 tree and root candidates.

The current hero render is visually useful, but it is not yet proof that both root and leaves are recursive.

### Target Geometry Program

Root side:

- Extract or select a root-branch module near the first natural split.
- Run recursive root grammar with shrink factors and anchor bridges: large root branch -> smaller fork -> fine rootlets.
- Use reprojection/naturalization or conservative small-island pruning only after recursive semantics are clear.
- At least four depths must exist and remain visually coherent.

Leaf side:

- Add many leaf-like modules along main branches, analogous to tree-crown iteration.
- Leaf repetition should follow branch tips and crown frontier, not a global radial clone.

### Experiments

- First locate the source GLB/OBJ and export candidate root and leaf submeshes.
- Run separate root-recursion and leaf-recursion sweeps.
- Merge only if both subprograms pass; otherwise document the better subprogram and continue.
- Run PBR/texturing after geometry passes; texture is secondary to geometry.

### Acceptance

- Depth `0..4` outputs for root-recursive sequence.
- No visible seams at attached roots/leaves, no disconnected large islands, no obvious voxel stairsteps.
- Blender zoom renders show thick-to-thin branching and leaf/crown recursion distinctly.
- Metrics must include occupancy LCR, components, vertex/face/file size, and postprocess before/after if used.

## Immediate Execution Plan

1. Write this document and keep it updated after each sweep.
2. Download/crop the CC0/public-domain images and record source/license metadata.
3. Patch root-prep and grammar code for 20260511h:
   - corrected basal-root indexing;
   - axis-corrected plant lanes;
   - conservative 20260511h single-op grammar aliases.
4. Generate 20260511h root candidates locally, inspect the contact sheet, then sync roots/scripts to `a100-2`.
5. Launch four remote lanes:
   - GPU 4: corrected plant-leaf/broad rosette root, depth `0..4`;
   - GPU 5: spider/runner/plantlet root, depth `0..3`;
   - GPU 6: external-image/TRELLIS2 generated fern/spider/root roots, depth-0 and depth-1/2 promotion;
   - GPU 7: `tree_root_leaf` root/leaf module sweep.
6. Pull previews/metrics, render selected candidates in Blender white/studio mode, and update this file with pass/fail and next actions.

## Claim Policy

- 20260511g is not a paper-positive plant case.
- Image-conditioned roots are not final until depth-0 decode and recursive-depth QA pass.
- External CC BY assets require attribution and should be marked separately from CC0/Public Domain assets.
- Effective-resolution / zoom-retention remains proxy evidence unless a stronger measurement pipeline is completed.
- Do not describe scifi/architecture proxies as tank/weapon/city unless true task-specific roots and grammars are introduced.

## Update 2026-05-11 15:45 CST: Active 20260511p Ralph Loop

The active loop has advanced from broad search to a narrow repair batch.

20260511o status:

- Metrics, selected OBJ pull, Blender final sheet, and spider depth sequence are complete.
- Spider/rosette rows are clean but depth change remains too weak for a final multi-depth claim.
- Poly Haven fern part and potted leaves are promising but still require better semantic handles and Blender QA.
- V23 pine is a plausible `tree_root_leaf` leaf-side subprogram.
- V23 rootfan is still unsolved; old rootfan and whole-root rows are diagnostic/failure evidence.

20260511p assets:

- Plan: `docs/progress/botanical_tree_root_20260511p_execution_plan_20260511.md`
- Launcher: `assets/run_botanical_tree_root_three_track_remote_20260511p.sh`
- Grammar code: `assets/trellis2_recursive_slat_grammar_workflow.py`

20260511p rules:

- Use only GPUs `4,5,6,7`.
- Do not rerun failed fifth-hero plant cuts as a main lane.
- Do not promote raw image roots.
- Do not promote rootfan unless first-split depth sequence visibly changes and Blender confirms correct growth direction.
- Pull light artifacts first, then selected OBJ depth sequences only.

## Update 2026-05-11 06:58 CST: 20260511i Four-Lane Launch Plan

Current active batch: `botanical_tree_root_recursive_remote_20260511i`.

Local scripts added:

- `assets/download_botanical_guide_images_20260511.py`
- `assets/run_botanical_tree_root_three_track_remote_20260511i.sh`

Prepared local inputs:

- Botanical guide images: `downloads/botanical_guides_20260511/`, 6 images with manifest/contact sheet.
- Root pool regenerated: `results/fern_root_candidates_20260511h/`, 10 OBJ roots; all local connectivity gates pass.
- Tree-root-leaf provenance trace: `docs/progress/tree_root_leaf_source_trace_20260511.md`.
- External asset scout: `docs/progress/external_botanical_asset_scout_20260511.md`.

Subagent conclusions to preserve:

- Use CC0/PD guide images first for generation: rubber fig aerial roots, Fiddlehead-ferns, Chlorophytum illustration, beech/aerial roots. CC-BY assets are attribution-required fallback; avoid ShareAlike/GFDL as final generative inputs unless licensing is explicit.
- Do not use `visuals/hero_botanical_variants_20260510/tree_compete_s3_green_leaf_brown_root.glb` as the semantic root/leaf module. It is a height-split PBR presentation asset.
- Primary tree-root-leaf SLat source should be `results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles/V23_lsys_pine_canopy_d5_multi_root_smooth_needles.obj`, because it records shared-vertex support, `needle_count=158`, `leaf_count=18`, and L-system depth-5 provenance.

Remote lanes planned on `a100-2`, GPUs 4-7 only:

- GPU 4: `plant_broad_yneg_20260511i` depth 4 with `v25h_spider_*` grammars; then `fern_arch_yneg_20260511i` depth 3.
- GPU 5: `plant_runner_yneg_20260511i` depth 4; then `fern_lacy_yneg_20260511i` depth 3.
- GPU 6: CC0/PD image-conditioned TRELLIS2 root generation from botanical guide images, followed by guarded depth-2 recursion only if root OBJ exists and is not too large.
- GPU 7: tree-root-leaf track: V23 pine/needle OBJ depth 4, V23 root fan depth 4, V23 root network depth 3.

Claim gates after this batch:

1. Pull OBJ/preview outputs and metrics CSV/JSON.
2. Exclude any lane with semantically weak depth change, large islands, or occupancy LCR below the visual-safe threshold.
3. Run Blender white/studio QA only for selected candidates.
4. Do not call any botanical/tree-root case publication-grade until there are GLB/OBJ outputs, metrics, render QA, and provenance docs.

## Update 2026-05-11 07:11 CST: 20260511i Completion And 20260511j Gate

Remote status checked on `a100-2`:

- All four 20260511i lanes have exited.
- Remote output root: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/botanical_tree_root_recursive_remote_20260511i`.
- Generated evidence count before metrics pull: 87 recursive OBJ/preview outputs and 4 image-root OBJ outputs.
- Recursive summaries are `status=ok` for:
  - `plant_broad_yneg_20260511i`: base tokens 421, depth 4 for 3 grammars.
  - `plant_runner_yneg_20260511i`: base tokens 404, depth 4 for 3 grammars.
  - `fern_arch_yneg_20260511i`: base tokens 147, depth 3 for 3 grammars.
  - `fern_lacy_yneg_20260511i`: base tokens 118, depth 3 for 3 grammars.
  - `tree_leaf_v23_pine_yneg_d4_20260511i`: base tokens 339, depth 4 for 3 grammars.
  - `tree_root_v23_rootfan_ypos_d4_20260511i`: base tokens 296, depth 4 for 2 grammars.
  - `tree_root_v23_rootnet_ypos_d3_20260511i`: base tokens 1669, depth 3 for 2 grammars; this lane is probably too heavy for main visuals unless Blender QA is surprisingly strong.

Image-root line status:

- `rubber_fig_aerial_roots_cc0`, `fiddlehead_ferns_cc0`, `spider_plant_commons_pd`, and `beech_aerial_roots_pd` generated OBJ roots, but guarded recursion skipped them because token/face complexity exceeded the current threshold.
- These are diagnostic only. Do not claim image-root recursive success from 20260511i.
- Next image-root attempt should crop to a single subject first: 3-7 aerial roots plus trunk contact, one fiddlehead curl, one spider rosette/plantlet, or one fern frond. Prefer 512 or 768 condition images. If an image-root still comes out high-poly, semantic-crop or decimate/remesh it before any recursion.

Local semantic-source priorities after explorer review:

- `plant_leaf`: first QA `results/plant_leaf_recursive_root_20260511/inputs/plant_leaf_base_mid_cluster_root.obj`, then `plant_leaf_green_cluster_root.obj`, then `plant_leaf_full_upright_root.obj`.
- `spider/fern`: first QA 20260511h roots `spider_rosette_publication_broad_20260511h`, `spider_rosette_publication_runner_20260511h`, `fern_compound_frond_arch_a`, and `fern_compound_frond_lacy_b`.
- `tree_root_leaf`: use V23 strict matched sources as semantic roots:
  - `results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles/V23_lsys_pine_canopy_d5_multi_root_smooth_needles.obj`.
  - `results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_root_fan_d5_multi_root_smooth_rootlets/V23_lsys_root_fan_d5_multi_root_smooth_rootlets.obj`.
  - `results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_sc_root_network_260_attractor_rootlets/V23_sc_root_network_260_attractor_rootlets.obj`.
- Do not use `visuals/hero_botanical_variants_20260510/tree_compete_s3_green_leaf_brown_root.glb` as the semantic root/leaf module. It is only a height-split PBR presentation asset.

20260511i pull and QA gate:

1. Finish remote metrics and pull metrics, previews, summaries, and selected OBJs locally.
2. Primary metric screen: prefer deepest output per grammar, require `primary_largest_component_ratio >= 0.98` and `largest_component_vertex_ratio >= 0.98` for positive candidates; exclude large component counts, many small islands, or face counts too heavy for paper rendering.
3. Visual screen: reject depth changes that read as dust/speckles or as nearly identical meshes; promote only cases with clear multi-depth recursion at object scale and zoom scale.
4. Blender QA priorities:
   - `tree_leaf_v23_pine_yneg_d4_20260511i/*/depth_04`.
   - `tree_root_v23_rootfan_ypos_d4_20260511i/*/depth_04`.
   - `plant_broad_yneg_20260511i/*/depth_04`.
   - `plant_runner_yneg_20260511i/*/depth_04`.
   - `fern_arch_yneg_20260511i/*/depth_03`.
   - `fern_lacy_yneg_20260511i/*/depth_03`.

20260511j launch rule:

- Launch the next four-GPU sweep only after the 20260511i metrics/preview/Blender gate identifies which grammars are semantically promising.
- 20260511j should not blindly widen grammar search. It should run:
  - cleaned/cropped image roots only after token/face reduction;
  - plant-leaf roots with selected root cuts and tree-crown-like leaf-size schedules;
  - V23 tree root/leaf tracks with separate root-recursive and leaf-recursive programs, then optional merge only if both pass.

## Update 2026-05-11 08:40 CST: 20260511k Verdict And 20260511l Plan

20260511k artifacts are present locally:

- Pull root: `results/botanical_tree_root_recursive_remote_20260511k_pull`.
- Metrics: `metrics/botanical_tree_root_metrics_20260511k.csv` and `.json`.
- Ranking: `analysis/candidate_ranking_20260511k.tsv` and `.json`.
- Preview sheets: `analysis/preview_depth_sequences_20260511k.png` and `analysis/preview_ranking_sheet_20260511k.png`.

20260511k claim-gated verdict:

- `tree_pine_needles_yneg_20260511k/v25k_pine_terminal_needles` is the best current leaf-recursive direction. It has visible depth change and depth-4 occupancy LCR about `0.990`, but component counts remain high (`544` face components in the raw OBJ metric row). It is a direction, not a paper-safe final.
- `spider_broad_leaflet_yneg_20260511k/v25k_spider_terminal_leaflet` and `spider_runner_leaflet_yneg_20260511k/v25k_spider_terminal_leaflet` show visible plant/leaf depth change and acceptable occupancy LCR (`~0.989` and `~0.997` respectively), but the geometry still reads as a decorated root/rosette with small detached detail rather than a clean publication-grade plant asset.
- `tree_rootfan_single_ypos_20260511k/v25k_root_single_wedge` is a no-op: depth 0-4 are effectively identical (`change_score=0`, zero bbox/voxel/vertex deltas). Do not promote it despite pretty connectivity metrics.
- `tree_rootfan_single_ypos_20260511k/v25k_root_single_then_tiplets` and `v25j_tree_root_wedge_fork` are not enough for the hero root requirement. They either barely change bbox or drop below the positive root LCR target (`~0.956` and `~0.972`) while adding terminal dust.
- `fiddle_tight_curl_yneg_20260511k` variants visibly change, but connectivity collapses (`occupancy LCR ~0.55-0.60`), so they are failure diagnostics only.
- `fern_lacy_tip_yneg_20260511k` includes clean/static rows; static rows must be penalized and not used as evidence of recursion.

Root-cause interpretation from the 20260511k audit:

- The rootfan no-op happens because the single-wedge mask is too narrow for the sparse V23 rootfan source; the operator requires at least 18 selected sparse tokens and returns unchanged when this gate fails.
- The rootfan variants that do change are selecting terminal fine rootlets, so the visible effect is small dust/rootlet growth rather than a thick-to-thin root hierarchy.
- The pine/leaf direction works because the V23 pine source has enough terminal needle/crown frontier tokens, but the mask still touches too many tiny terminal pieces and produces many small components.
- The plant-leaf true fifth-hero cuts remain risky because previous component audits showed extreme fragmentation. They must be tested, but a CC0 cleaner plant fallback and clean procedural spider roots should run in parallel.

New code prepared locally for 20260511l:

- `assets/trellis2_recursive_slat_grammar_workflow.py` now has additive v25l botanical/root aliases:
  - `v25l_root_relaxed_wedge`
  - `v25l_root_primary_branch`
  - `v25l_root_two_phase`
  - `v25l_root_two_phase_rootlets`
  - `v25l_spider_leaf_cluster_compact`
  - `v25l_spider_leaf_treecrown`
  - `v25l_spider_leaf_tip_clean`
  - `v25l_fiddlehead_guarded_curl`
  - `v25l_pine_leaf_cluster_clean`
  - `v25l_pine_branch_tip_cluster`
- These are designed to fix specific 20260511k failures:
  - relaxed root masks accept 8-10 sparse tokens instead of silently no-oping;
  - primary-branch root masks select a thicker branch band before adding rootlets;
  - two-phase root schedules try hierarchy first, details later;
  - plant/leaf operators use compact basal/terminal masks and longer bridges;
  - pine leaf operators reduce terminal drift to lower island growth.
- Local validation passed:
  - `python3 -m py_compile assets/trellis2_recursive_slat_grammar_workflow.py assets/download_botanical_guide_images_20260511.py assets/prepare_botanical_low_complexity_conditions_20260511j.py`
  - `bash -n assets/run_botanical_tree_root_three_track_remote_20260511l.sh`

External/guide asset update:

- Added CC0 spider-plant photo guide `File:Spider plants (Chlorophytum comosum).jpg` to `assets/download_botanical_guide_images_20260511.py`.
- Regenerated `downloads/botanical_guides_20260511/` with 7 guide rows and `downloads/botanical_guides_20260511j_low_complexity/` with 7 low-complexity crops.
- New low-complexity condition: `downloads/botanical_guides_20260511j_low_complexity/spider_photo_rosette_cc0_condition_768.png`.
- License preference remains CC0/Public Domain for final generated-input evidence; CC BY direct meshes/images are fallback lanes with attribution.

20260511l four-lane remote plan:

- GPU 4 / plant leaf:
  - true fifth-hero cuts `plant_leaf_base_mid_cluster_root.obj`, `plant_leaf_green_cluster_root.obj`;
  - CC0 small-plant direct fallback `poly_pizza_small_plant_cc0_root.obj`;
  - grammars `v25l_spider_leaf_cluster_compact`, `v25l_spider_leaf_treecrown`, `v25l_spider_leaf_tip_clean`.
- GPU 5 / spider and fern:
  - clean procedural broad/runner roots from `results/fern_root_candidates_20260511h`;
  - fiddlehead and fern arch diagnostics;
  - grammars `v25l_spider_*`, `v25l_fiddlehead_guarded_curl`, `fern_frond_pinnae_attach`.
- GPU 6 / hero tree_root_leaf:
  - V23 rootfan with `v25l_root_relaxed_wedge`, `v25l_root_primary_branch`, `v25l_root_two_phase`, `v25l_root_two_phase_rootlets`;
  - V23 pine with `v25l_pine_leaf_cluster_clean`, `v25l_pine_branch_tip_cluster`, and `v25k_pine_terminal_needles` as comparison.
- GPU 7 / image-root diagnostics:
  - CC0/PD conditions `spider_photo_rosette_cc0`, `spider_rosette_single_pd`, `rubber_fig_3_7_roots_cc0`, `rubber_fig_trunk_contact_cc0`, `fiddlehead_single_curl_cc0`;
  - guarded depth-2 recursion only if generated root face/token gates pass.

Launch script:

- `assets/run_botanical_tree_root_three_track_remote_20260511l.sh`

Next gate:

1. Sync updated scripts and guide images to `a100-2`.
2. Check remote storage and GPU 4-7 availability.
3. Launch 20260511l with at most one SSH shell.
4. After completion, run remote metrics, pull summaries/previews/metrics, build ranking/contact sheets, then run Blender QA only for candidates with real depth change and acceptable connectivity.
5. Do not call any case publication-grade until OBJ/GLB outputs, metrics, controlled render QA, provenance/license notes, and paper-safe pass/fail text are all present.

## Update 2026-05-11 09:22 CST: Three-Track Publication Loop Re-Scoped

User clarified that external asset/image downloads are allowed, remote image generation is allowed, and the active work should run as three high-intensity parallel tracks:

1. **Optimize the fifth hero `plant_leaf` case.** The current fifth-case root cuts are not good enough. The next loop must select or cut a stronger root leaf mesh first, then run TRELLIS2/SLat recursion with tree-crown-like leaf-size schedules and multiple grammars. Depths should be visually distinct, semantically clear, and attractive at every displayed depth. Fragment cleanup is allowed only after the recursive semantics are clear.
2. **Spider plant / fern / recursive roots.** Search hard for license-compatible meshes and images. Direct meshes, image-guided TRELLIS2 roots, and clean procedural fallback roots can all be tested, but final claims should separate CC0/PD lanes from attribution lanes. Root quality and grammar choice are the two main bottlenecks.
3. **Hero `tree_root_leaf`, especially the 4th hero case.** The goal is not just a pretty material split. Both the root system and the leaf/branch frontier should become true recursive structures. Root recursion must show natural thick-to-thin branching from a selected first-split/root-branch module, with at least depth 4, no obvious seams, no major islands, and no voxelized/broken surfaces.

Heartbeat `r-slg-long-task-heartbeat` was updated to this exact three-track goal. It is a fallback only; the active loop continues directly in this thread.

### 20260511l Metric Verdict

Local lightweight pull exists at `results/botanical_tree_root_recursive_remote_20260511l_pull`; it contains metrics, summaries, logs, and image-root summaries, but not full OBJ/GLB meshes. Metrics table has 125 rows.

Promising directions:

- `tree_pine_v25l_yneg_20260511l/v25l_pine_leaf_cluster_clean/depth_04` is the best current positive-direction leaf/crown candidate: `PLCR=0.997`, vertex LCR `0.992`, occupancy components `5`, face components `428`, tokens `311 -> 335`, bbox diagonal delta `0.108`. This needs Blender QA because face component count is still high, but it is currently the cleanest leaf-recursive track.
- `tree_pine_v25l_yneg_20260511l/v25l_pine_branch_tip_cluster/depth_04`: `PLCR=0.994`, vertex LCR `0.987`, tokens `311 -> 361`, bbox delta `0.167`. More visible growth than leaf-cluster-clean, but slightly more fragmented.
- `spider_runner_v25l_yneg_20260511l` with `v25l_spider_leaf_treecrown`, `v25l_spider_leaf_tip_clean`, or `v25k_spider_terminal_leaflet` all reach depth 4 with `PLCR~0.997`, vertex LCR `0.986`, tokens `404 -> 436`, bbox delta `0.111`. This is the best current spider/runner direction, but visual QA must confirm it is not just lateral strip extension.
- `spider_broad_v25l_yneg_20260511l/v25l_spider_leaf_tip_clean` and `/v25l_spider_leaf_treecrown` have visible bbox change and `PLCR~0.986-0.989`; they are backup rosette candidates.
- `fern_arch_v25l_yneg_20260511l/fern_frond_pinnae_attach/depth_03` grows visibly (`tokens 147 -> 246`, bbox delta `0.113`, `PLCR=0.995`) but vertex LCR is only `0.493`, so it is visually/diagnostic unless pruning/remeshing proves harmless.

Rejected or diagnostic:

- True fifth-hero plant cuts are still not paper-safe. `plant_leaf_basemid` with compact/treecrown grammars falls to `PLCR~0.78` and hundreds to thousands of face components; `plant_leaf_green` is cleaner only for no-op-ish rows and still lacks base/root emergence semantics. The failure mode remains copying too much thin leaf-sheet geometry.
- `tree_rootfan_v25l_ypos_20260511l` is still too subtle for the requested four-depth root hero. The best row, `v25l_root_relaxed_wedge`, reaches `PLCR=0.988`, but vertex LCR is `0.977` and bbox delta is only `0.002`; the other rootfan rows fall to `PLCR~0.93-0.97`. This is not a natural thick-to-thin root hierarchy yet.
- `fiddle_guarded_v25l_fiddlehead_guarded_curl` collapses (`PLCR=0.634`), while `fern_frond_tip_attach` is a no-op for fiddlehead (`tokens 74 -> 74`).
- Image-root outputs from 20260511l remain diagnostic. `spider_photo_rosette_cc0`, `spider_rosette_single_pd`, `rubber_fig_*`, and `fiddlehead_single_curl` either fragment, become near-planes, or are too heavy. They cannot be used as positive evidence without root simplification/crop/remesh and a successful recursion pass.

### Current Root/Anchor Methodology To Preserve

Current SLat grammar masks are mostly coordinate-derived sparse-latent masks, not automatic semantic part discovery from GLBs. Semantic provenance comes from authored/procedural source OBJs and metadata; anchors are currently either explicit in those sources or derived geometrically by quantiles/wedges over sparse support. The paper should add a short root-module/anchor-selection paragraph:

- root mesh/module is the initial sparse-latent state derived from a semantic/procedural source OBJ or a documented image/mesh seed;
- anchors can be explicit semantic handles from source metadata or geometry-derived masks over the sparse support;
- the `tree_root_leaf` presentation GLB is only a material/render asset, while recursive evidence must use V23 strict matched source OBJs with support/needle/rootlet provenance;
- do not claim automatic semantic root/leaf discovery from arbitrary height/material splits.

### Next Experimental Design

The 20260511m/n next round should not simply widen v25l. It should change root selection and grammar style:

- **Plant leaf:** create or find stronger root leaf modules before recursion. Preferred paths are a cleaner spider-plant direct mesh, a CC0/PD spider plant image-root that is simplified before recursion, or a manually cut single leaf/petiole module from the fifth hero asset rather than full cluster copying. New grammars should copy basal petiole/leaf handles, not entire thin leaf sheets.
- **Spider/fern:** keep `spider_runner_v25l` and `spider_broad_v25l` as candidates for Blender QA, but run a new direct/external-root lane if license-clean assets can be acquired. Fern/crozier image roots need single-subject crop and simplification before recursion.
- **Tree root leaf:** keep V23 pine leaf recursion for QA. For roots, introduce explicit first-split/root-branch source cuts or sidecar handles from the V23 rootfan source, then recurse a coherent branch module with shrink/taper and late rootlets. Avoid terminal fine-root masks as primary anchors.

Immediate gate order:

1. Pull only selected 20260511l OBJ sequences for Blender QA: V23 pine leaf-cluster/branch-tip/terminal, spider runner/broad, maybe fern arch.
2. Write new source/handle preparation scripts for plant leaf and tree root first-split cuts.
3. Launch the next four-GPU remote sweep only after the cut/handle inputs exist and local syntax checks pass.
4. Keep storage below the user-relaxed 200GB cap and record provenance/license notes for every external asset.

## Update 2026-05-11 07:45 CST: 20260511i QA Verdict And 20260511j Implementation

20260511i evidence pulled locally:

- Pull root: `results/botanical_tree_root_recursive_remote_20260511i_pull`.
- Metrics: `metrics/botanical_tree_root_metrics_20260511i.csv` and `.json`.
- Preview sheet: `analysis/preview_ranking_sheet_20260511i.png`.
- Blender QA sheet: `analysis/blender_sequence_sheet_20260511i_white.png`.
- Selected OBJ sequences pulled under `remote_abs/.../botanical_tree_root_recursive_remote_20260511i/raw`.

20260511i metric/visual verdict:

- `plant_broad_yneg_20260511i/v25h_spider_basal_crown_micro/depth_04`: metric-clean (`primary LCR=1.0`, vertex LCR about `0.997`) but visual depth changes are too small. It is not publication-grade recursive growth.
- `plant_runner_yneg_20260511i/v25h_spider_runner_distal_micro/depth_04`: metric-clean (`primary LCR=1.0`, vertex LCR about `0.997`) and the runner is readable, but depth changes remain weak and mostly local. It is a useful root/grammar direction, not final.
- `plant_runner_yneg_20260511i/v25h_spider_leaf_tiplet_micro/depth_04`: visually starts to add leaf/rim detail, but some side debris appears and it still lacks a strong multi-depth story.
- `fern_lacy` and `fern_arch` sequences are clean but mostly static regular fronds. They can be diagnostic or minor supplement, not a headline plant case.
- `tree_root_v23_rootfan_ypos_d4_20260511i`: source semantics are promising, but depth changes are weak and terminal fine branches show dust/speckle risk. Do not use as a final hero root without 20260511j cleanup.
- `tree_leaf_v23_pine_yneg_d4_20260511i`: contains the right V23 tree/root/leaf provenance, but current grammars read more like root/needle noise than clean leaf recursion.
- `tree_root_v23_rootnet_ypos_d3_20260511i`: excluded from main visuals; too heavy and fails the connectivity/fragmentation gate.
- Image-root outputs are still diagnostic only. Full 1024 image roots are either too high-token or too fragmented for recursive evidence.

Important correction:

- Remote `a100-2` did not yet have `results/plant_leaf_recursive_root_20260511/inputs`, so 20260511i plant lanes were based on procedural 20260511h spider/fern roots, not the fifth hero `plant_leaf` root. 20260511j must sync and test the true fifth-hero plant leaf cuts.

20260511j code changes prepared locally:

- `assets/trellis2_recursive_slat_grammar_workflow.py` now has additive 20260511j aliases only:
  - `v25j_spider_leaf_handle_visible`
  - `v25j_spider_leaf_handle_compact`
  - `v25j_spider_leaf_schedule`
  - `v25j_tree_root_clean_fork`
  - `v25j_tree_root_wedge_fork`
  - `v25j_tree_root_wedge_then_clean`
- These aliases preserve older results. They are designed to fix 20260511i failure modes:
  - plant: visible basal handle/leaf-sector copying instead of almost invisible micro buds;
  - root: coherent terminal wedge copy with longer bridges instead of all-tip dust clouds.
- Low-complexity image conditions were generated at `downloads/botanical_guides_20260511j_low_complexity/` with a contact sheet and manifest. Best first-pass conditions are `spider_rosette_single_pd`, `rubber_fig_3_7_roots_cc0`, and `rubber_fig_trunk_contact_cc0`.

20260511j launch plan:

- GPU 4: true fifth-hero `plant_leaf_base_mid_cluster_root.obj` and `plant_leaf_green_cluster_root.obj` with visible/compact leaf-handle grammars.
- GPU 5: procedural 20260511h spider broad/runner roots with visible leaf-handle schedule to test whether stronger growth can stay clean.
- GPU 6: V23 rootfan with `v25j_tree_root_*` grammars; depth 4 only if metrics stay clean.
- GPU 7: low-complexity image roots from selected 768 conditions, followed by guarded depth-1/2 recursion only if face/token gates pass.

20260511j acceptance gate is stricter than 20260511i:

- A candidate must show visible object-scale depth change from depth 0 to final depth.
- It must avoid terminal dust/speckle in Blender white-background QA.
- It must pass `primary_largest_component_ratio >= 0.98` unless a visually justified exception is explicitly documented as diagnostic only.
- It must have the true source/root provenance in the manifest before entering a paper figure.

## Update 2026-05-11 07:45 CST: 20260511j Remote Launch

20260511j has been synced and launched on `a100-2` with GPUs 4-7 only.

Synced inputs:

- `assets/trellis2_recursive_slat_grammar_workflow.py`
- `assets/run_botanical_tree_root_three_track_remote_20260511j.sh`
- `assets/prepare_botanical_low_complexity_conditions_20260511j.py`
- true fifth-hero plant roots under remote `results/plant_leaf_recursive_root_20260511/inputs/`
- low-complexity image conditions under remote `downloads/botanical_guides_20260511j_low_complexity/`

Remote output root:

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/botanical_tree_root_recursive_remote_20260511j`

Launched lanes:

- GPU 4 / pid `157329`: `true_plant` lane, true fifth-hero `plant_leaf_base_mid_cluster_root.obj` and `plant_leaf_green_cluster_root.obj`.
- GPU 5 / pid `157330`: `spider_visible` lane, procedural broad/runner roots with visible leaf-handle schedule.
- GPU 6 / pid `157331`: `tree_root_clean` lane, V23 rootfan with clean/wedge root grammars.
- GPU 7 / pid `157333`: `lowcond_images` lane, 768 low-complexity image roots plus guarded recursion.

Immediate monitor rule:

- First check logs/summaries for syntax/import failures or token explosions.
- Then run metrics only after all lanes exit.
- Do not call 20260511j complete until metrics, Blender QA, and pass/fail notes are written.

## Update 2026-05-11 09:58 CST: 20260511n Gate And Continuing Ralph Loop

Current latest fully QA-rendered batch is `botanical_tree_root_recursive_remote_20260511n`.

Evidence paths:

- Remote: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/botanical_tree_root_recursive_remote_20260511n`.
- Local pull: `results/botanical_tree_root_recursive_remote_20260511n_pull/`.
- Blender QA: `results/botanical_tree_root_recursive_remote_20260511n_selected_meshes/blender_qa_20260511n/contact_sheet_20260511n_selected_blender_whitecomposite.png`.
- Selected mesh index: `results/botanical_tree_root_recursive_remote_20260511n_selected_meshes/blender_cases_20260511n.txt`.

Pass/fail summary:

- `plant_leaf_green_v25n` and `plant_leaf_basemid_v25n` are **rejected_fragmented**. They look like torn leaf-sheet clusters under controlled Blender material, with many islands. Do not spend another main GPU lane on these exact cuts unless a new root extraction or postprocess root-cleaning step is introduced first.
- `spider_broad_v25n/v25l_spider_leaf_tip_clean/depth_02` is `positive_candidate_pending_extension`: visually plausible rosette, `PLCR=0.9939`, vertex LCR `0.9956`.
- `spider_runner_v25n/v25k_spider_terminal_leaflet/depth_02` is `positive_candidate_pending_extension`: visually plausible runner/plantlet, `PLCR=0.9983`, vertex LCR `0.9967`.
- `v25n_spider_runner_leaflet_gated` is **rejected_fragmented** even when the preview looks acceptable; by depth 4 it has `PLCR=0.1449` and component collapse.
- `fern_arch_v25n/v25n_fern_pinnae_sparse/depth_02` is `supplement_candidate`: clean, single primary component, but visually too schematic/flat for headline.
- `tree_pine_v25n_depth4/v25n_pine_leaf_gated/depth_04` is the best current four-depth root/bundle candidate, but not sufficient for the user-requested `tree_root_leaf` root+leaf dual recursion.
- `tree_rootfan_v25n/root_first_split_taper` is **diagnostic_only**; early depth improves shape, but depth 2 drops below the connectivity gate and does not show a robust four-depth thick-to-thin root hierarchy.

New external/root-acquisition state:

- CC0 Poly Haven assets were downloaded to `downloads/polyhaven_botanical_cc0_20260511/`.
- `fern_02` and `potted_plant_02` have local FBX/Blend/USD/gltf geometry plus manifest. They are now the preferred CC0 root candidates for the plant/fern track.
- Attribution-lane assets remain useful only if provenance is recorded separately; they must not be mixed into CC0 main-claim rows.

Ralph continuation rule:

1. Preserve 20260511n as the latest completed gate.
2. Export/simplify CC0 Poly Haven roots, sync to remote, and launch the next four-lane 20260511o batch.
3. Keep spider positive rows as extension candidates, not final claims.
4. Keep tree-root-leaf open until explicit root-handle or first-split branch recursion passes depth 4 with Blender QA.
5. Continue heartbeat and do not declare publication-grade completion without OBJ/GLB, metrics, Blender QA, zooms, provenance/license, and paper-safe text.

## Update 2026-05-11 14:40 CST: Active 20260511o Closeout

Use the detailed note `docs/progress/botanical_tree_root_20260511o_closeout_and_next_20260511.md` as the latest checkpoint for this loop.

Facts:

- `20260511o` remote lanes have all exited.
- The immediate task is not another broad sweep; it is metrics, selected local pull, Blender QA, candidate ranking, and paper-safe status labels.
- A rootfan alias bug was fixed: `v25n_whole_root_single_corner` -> `v25n_whole_root_corner`.
- The one-off fix row `tree_rootfan_wholeroot_corner_fix_ypos_20260511o` ran successfully, but likely has weak depth change; it must be judged by metrics/Blender.
- Keep `tree_root_leaf` open until explicit root-side depth-4 thick-to-thin recursion and leaf-side recursion pass QA.
- Keep original fifth-hero plant true cuts marked `rejected_fragmented`.
- TRELLIS1/classic remains a runnable-environment blocker; Hunyuan text-root mesh-space negative controls exist but still need final render/table integration.

## Update 2026-05-11 16:45 CST: 20260511p Closed, 20260511q Prepared

Use the detailed q plan:

- `docs/progress/tree_root_firstsplit_20260511q_execution_plan.md`

20260511p verdict:

- Supplement candidates: `spider_runner_visible_chain`, `polyhaven_fern_part/v25k`, `polyhaven_potted_leaves/v25l`, and V23 `tree_pine` leaf-side rows.
- Rejected root rows: `root_yneg_sidecar`, `root_ypos_sidecar`, and `root_fit052_then`.
- Reason: the V23 whole rootfan rows either barely change across depth or fragment heavily. This is now a root-acquisition/mask-semantics blocker, not merely a lighting issue.

20260511q changes:

- Added local first-split input generator: `assets/prepare_tree_root_firstsplit_candidates_20260511q.py`.
- Generated 8 clean input root modules in `results/tree_root_firstsplit_candidates_20260511q/`.
- All local inputs have single mesh component and largest-component vertex ratio `1.0`.
- Added q grammar aliases in `assets/trellis2_recursive_slat_grammar_workflow.py`.
- Added q remote launcher: `assets/run_tree_root_firstsplit_remote_20260511q.sh`.

Claim boundary:

- q local root modules are input acquisition only.
- Publication evidence requires remote SLat recursive outputs plus metrics and Blender QA.

## Update 2026-05-11 18:55 CST: Current Three-Track State After q/r Audit

Use `docs/progress/tree_root_firstsplit_20260511q_execution_plan.md` as the detailed tree-root recovery note.

Current facts to preserve after context compaction:

- The fourth and fifth hero combo botanical cases are presentation/root-stamped assets, not completed dual-recursion proofs. Keep them visually useful but caption-safe until new recursive evidence exists.
- The true fifth-hero plant cuts (`plant_leaf_green_cluster_root.obj` and `plant_leaf_base_mid_cluster_root.obj`) remain `rejected_fragmented`; do not rerun them as main positives without new root extraction.
- The best near-term plant replacements remain spider/rosette and CC0 Poly Haven fern/potted candidates, but they are supplement/positive-candidate directions until depth-change Blender QA passes.
- `20260511q` first-split roots are diagnostic negative evidence: clean input roots, but weak recursive depth change and terminal dust.
- `20260511r` coarse-root rerun produced real remote outputs despite an `r_fix` launcher bookkeeping bug. Successful OBJ/preview outputs are under `results/tree_root_coarse_recursive_remote_20260511r`, not the empty `...20260511r_fix` directory.
- `20260511r` metrics are complete. Some down-direction final rows pass the PLCR threshold, but d0-d4 bbox deltas are tiny; controlled Blender depth-sequence QA is required before any positive claim.
- TRELLIS1/classic remains environment-blocked, not model-failed. Hunyuan text-root mesh-space copy is closed for three representative primary cases, but Hunyuan texture/paint and final table/render integration remain open.

Next action order:

1. Pull selected `20260511r` OBJ depth sequences and run Blender white-background QA.
2. If `20260511r` is visual-weak/no-op, author a new remote batch that visibly extends one coarse root child branch before adding fine rootlets.
3. Keep plant/spider/fern candidates in scope, but do not spend GPU on old true-cut plant roots unless a cleaner petiole/root module is extracted first.
4. Keep paper wording claim-safe: authored/geometric handles, no automatic semantic root discovery, effective-resolution as proxy, Hunyuan limited to three primary text-root mesh-copy controls.
