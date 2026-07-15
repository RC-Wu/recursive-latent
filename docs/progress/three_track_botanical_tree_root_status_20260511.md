# Three-Track Botanical / Tree-Root Status Report 20260511

Date: 2026-05-11 CST  
Status: paused for user review after multiple remote SLat loops  
Acceptance folder: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/three_track_botanical_tree_root_acceptance_20260511`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU policy used: GPUs `4,5,6,7` only  
Claim policy: no result below is publication-grade unless explicitly marked so. Current state has supplement candidates and strong negative evidence, but no fully closed headline case.

## Executive Summary

The three requested tasks were pursued with real remote TRELLIS2/SLat recursive runs, guide/image search, external CC0/CC-BY asset scouting, local root candidate generation, metrics, selected OBJ pulls, and controlled Blender QA.

Current outcome:

1. **Plant leaf / fifth hero true cut:** not complete; now strong negative evidence. The existing true cuts (`plant_leaf_green_cluster_root.obj`, `plant_leaf_base_mid_cluster_root.obj`) repeatedly fragment into torn leaf sheets and floating strips. They should not be promoted.
2. **Spider plant / fern / recursive roots:** partially successful as supplement candidates. Spider runner, Poly Haven fern part, potted leaves, and pine leaf-side rows have metric-positive or visually plausible candidates, but none is yet a clean headline multi-depth botanical case.
3. **Fourth hero `tree_root_leaf`:** leaf/branch-side candidate exists; root-side remains open. p/q/r/s/t root-side loops isolate the blocker: whole rootfan or clean first-split roots do not yet survive four-depth SLat recursion as a natural thick-to-thin hierarchy.

## Visual Review Package

All curated review images and metrics are copied to:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/three_track_botanical_tree_root_acceptance_20260511`

Recommended first-pass review order:

1. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/three_track_botanical_tree_root_acceptance_20260511/01_plant_leaf_true_cut/20260511n_true_cut_retest_failure_sheet.png`
2. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/three_track_botanical_tree_root_acceptance_20260511/02_spider_fern_polyhaven/20260511p_spider_runner_depth_sequence_supplement.png`
3. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/three_track_botanical_tree_root_acceptance_20260511/02_spider_fern_polyhaven/20260511p_selected_spider_fern_polyhaven_sheet.png`
4. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/three_track_botanical_tree_root_acceptance_20260511/03_tree_root_leaf/leaf_side_tree_pine_depth_sequence_candidate.png`
5. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/three_track_botanical_tree_root_acceptance_20260511/03_tree_root_leaf/t_supported_child_near_noop_failure_sheet.png`

The folder also contains `README_zh.md` explaining every selected image.

## Task 1: Plant Leaf / Fifth Hero Case

### What Was Tried

- Exported three roots from the fifth hero botanical presentation asset:
  - `plant_leaf_full_upright_root.obj`
  - `plant_leaf_green_cluster_root.obj`
  - `plant_leaf_base_mid_cluster_root.obj`
- Ran remote SLat sweeps on a100-2 with basal fan, basal micro, crown bud, crown micro, fork-side, basal-handle, and later basal/midrib operators.
- Re-tested the true cuts in later `20260511n` batch after grammar improvements.
- Compared true cuts against spider/rosette/fern substitutes in controlled Blender QA.

### Result

Rejected as publication evidence.

Evidence:

- Initial QA: `results/plant_leaf_recursive_remote_20260511_pull/blender_selected_white/selected_blender_contact_sheet_white.png`
- Later selected QA: `results/botanical_tree_root_recursive_remote_20260511l_selected_meshes/blender_qa_20260511l/contact_sheet_20260511l_selected_blender_whitecomposite.png`
- Final retest QA: `results/botanical_tree_root_recursive_remote_20260511n_selected_meshes/blender_qa_20260511n/contact_sheet_20260511n_selected_blender_whitecomposite.png`

Metric/visual notes:

- First green-cluster rows reached about `occ LCR=0.947..0.949`, but they lack base/root emergence semantics and still show thin-sheet artifacts.
- Base-mid rows preserve more semantics but are worse: first pass best base-mid around `occ LCR=0.9044`; later n retest falls near `PLCR~0.75` for base-mid and `~0.81` for green under stricter selected rows.
- Visual failure is consistent: torn lamina sheets, floating strips, no reliable petiole/root-handle emergence.

### Why It Failed

The selected root mesh is the wrong root for this proof. It is a presentation/root-stamped plant asset with thin overlapping leaf sheets, not a clean petiole/root module. Sparse latent operators copy fragile sheet regions instead of a biological handle, so stronger grammars make visible debris, while conservative grammars become subtle/no-op.

### Current Completion

- Root/source diagnosis: complete.
- Remote SLat evidence: complete for negative verdict.
- Publication-grade plant-leaf asset: not complete.

Next correct move: choose a new root source, either a clean single petiole/leaf module, a direct spider/rosette mesh, or a CC0 potted/fern source after simplification. Do not keep burning GPUs on the rejected true cuts without a new extraction.

## Task 2: Spider Plant / Fern / Recursive Roots

### What Was Tried

- Downloaded/scouted public and CC botanical guide images:
  - spider plant / Chlorophytum public domain image;
  - fiddlehead / fern CC0 and CC-BY images;
  - rubber fig and beech aerial roots;
  - root-bound spider plant and other attribution-lane references.
- Generated guide crops and low-complexity condition images.
- Ran TRELLIS2 image-root attempts; raw image roots were often connected but flat/heavy.
- Generated local spider/fern/root candidate pool with corrected axis semantics.
- Downloaded/exported CC0 Poly Haven botanical assets (`fern_02`, `potted_plant_02`) and ran conservative remote recursion.
- Ran successive remote batches `g/h/i/j/k/l/n/o/p` to test spider rosette, runner, fern frond, fiddlehead/crozier, potted leaves, and root/rhizome candidates.

### Best Current Candidates

- `spider_runner_visible_d4_yneg_20260511p / v25p_spider_runner_visible_chain`: metric positive candidate with `PLCR=0.9706`, vertex LCR `0.9732`, max bbox delta `0.1542`. Visual depth change is better than earlier spider rows, but leaf tearing and sheet noise remain.
- `polyhaven_fern_part_handles_d3_yneg_20260511p / v25k_spider_terminal_leaflet`: clean supplement candidate with `PLCR=0.9948`, vertex LCR `0.9936`, primary components `3`, max bbox delta `0.0940`.
- `polyhaven_potted_leaves_fan_d3_yneg_20260511p / v25l_spider_leaf_tip_clean`: semantically useful potted-plant supplement with `PLCR=0.9811`, vertex LCR `0.9948`, but high face/render pressure and some bottom fragmentation.

Evidence:

- `results/botanical_tree_root_recursive_remote_20260511p_pull/blender_qa_20260511p/contact_sheet_blender_selected_20260511p_whitecomposite.png`
- `results/botanical_tree_root_recursive_remote_20260511p_pull/blender_qa_20260511p/spider_runner_p_depth_sequence_blender_20260511p_whitecomposite.png`
- `results/botanical_tree_root_recursive_remote_20260511o_pull/blender_qa_20260511o/spider_depth_sequence_blender_20260511o_whitecomposite.png`
- `downloads/botanical_guides_20260511/manifest_botanical_guides_20260511.json`
- `docs/progress/external_botanical_asset_scout_20260511.md`

### Why Not Complete

The best spider/fern rows are supplement-grade, not headline-grade:

- spider runner has more visible depth change, but still shows leaf tearing/noise;
- earlier spider rows were cleaner but too similar across depth;
- fern part is clean, but too flat/schematic and not visually rich enough for the main claim;
- raw image-root outputs were too flat/heavy or root-quality diagnostics only;
- true downloadable spider plant GLB from Sketchfab remains attribution/login constrained, so no clean direct spider mesh has been fully integrated as final evidence.

### Current Completion

- Asset scout: complete enough to guide next work.
- Public guide image preparation: complete.
- Remote SLat supplement candidates: complete.
- Publication-grade spider/fern headline case: not complete.

Next correct move: use the best external direct mesh lane if download is feasible (`Spider Plant by sauti`, CC BY) or continue with CC0 Poly Haven/fern/potted roots after crop/decimate and more biologically constrained petiole/runner grammar.

## Task 3: Fourth Hero `tree_root_leaf`

### What Was Tried

The task was split into leaf-side and root-side subprograms.

Leaf-side:

- Preferred source became V23/V25 pine/canopy semantics rather than the presentation GLB.
- Ran `tree_pine_leaf_visible_d4_yneg_20260511p` with `v25n_pine_leaf_gated` and `v25p_pine_branch_frontier_needle_whorl`.

Root-side:

- p: V23 rootfan sidecar/firstsplit variants, y-positive/y-negative orientation stress.
- q: new clean first-split input modules with explicit trunk/split/terminal anchors; remote SLat recursion.
- r: suppressed terminal rootlets, coarse first-split input pool; remote SLat recursion.
- s: visible-child operator to force readable depth change; remote SLat recursion.
- t: supported-child operator with explicit sparse tube support; remote SLat recursion.

### Leaf-Side Result

Supplement candidate exists:

- `tree_pine_leaf_visible_d4_yneg_20260511p / v25p_pine_branch_frontier_needle_whorl`: `PLCR=0.9935`, vertex LCR `0.9856`, max bbox delta `0.1882`.
- `tree_pine_leaf_visible_d4_yneg_20260511p / v25n_pine_leaf_gated`: `PLCR=0.9969`, vertex LCR `0.9915`, max bbox delta `0.1240`.

Evidence:

- `results/botanical_tree_root_recursive_remote_20260511p_pull/blender_qa_20260511p/tree_pine_p_depth_sequence_blender_20260511p_whitecomposite.png`

This can support a leaf/branch-side supplement, but it does not prove dual root+leaf recursion.

### Root-Side Result

Root side is not solved.

Key evidence:

- p rootfan sidecar: `results/botanical_tree_root_recursive_remote_20260511p_pull/blender_qa_20260511p/root_yneg_sidecar_depth_sequence_blender_20260511p_whitecomposite.png`
- q first-split: `results/tree_root_firstsplit_recursive_remote_20260511q_pull/blender_qa_20260511q/tree_root_firstsplit_q_selected_depth_sequences_contact_sheet.png`
- s visible-child: `results/tree_root_coarse_recursive_remote_20260511s_pull/blender_qa_20260511s/tree_root_coarse_20260511s_blender_iso_sheet.png`
- t supported-child: `results/tree_root_coarse_recursive_remote_20260511t_pull/blender_qa_20260511t/tree_root_coarse_20260511t_blender_iso_sheet.png`

Metric highlights:

- q best target down row `firstsplit_down_sidecar_c / v25p_root_first_split_sidecar`: final `PLCR=0.9320`, vertex LCR `0.9488`, primary components `17`, rejected by metric and visual gates.
- q best up diagnostic `firstsplit_up_sidecar_g / v25q_root_module_chain`: final `PLCR=0.9536`, vertex LCR `0.9816`, but `14` primary components and weak depth-change proxy.
- s best visible row had visible displacement but fragmented: final `PLCR=0.9643`, primary components `6`, vertex LCR `0.8826`, torn side sheets/fragments in Blender.
- t best rows were clean but near-no-op: e.g. `coarse_down_compact_a / v25t_root_supported_child_pair` final `PLCR=0.9895`, vertex LCR `0.9948`, but bbox diag ratio only `1.0013`; Blender shows no convincing four-depth hierarchy.

### Why Not Complete

The blocker is now localized:

- the presentation GLB is not a semantic recursion source;
- V23 rootfan is too diffuse for stable first-split handle selection;
- q/r clean input modules show that input connectivity alone is not enough;
- s can create visible movement but decodes as torn sheets/fragments;
- t improves support/metrics but collapses to visually weak near-no-op.

A successful next loop must change input acquisition and root handle design more substantially: create a stronger multiscale root module where the desired thick-to-thin hierarchy exists as continuous geometry before encode/decode, then use remote SLat recursion/naturalization as evidence.

### Current Completion

- Leaf-side supplement: mostly complete.
- Root-side four-depth hierarchy: not complete.
- Dual root+leaf hero proof: not complete.

## Files Changed During This Pause

- Updated `docs/progress/tree_root_supported_child_20260511t_execution_plan.md` with t closeout.
- Created acceptance package: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/three_track_botanical_tree_root_acceptance_20260511`.
- Created this report: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/progress/three_track_botanical_tree_root_status_20260511.md`.

No new remote `u` loop was launched after the pause request.
