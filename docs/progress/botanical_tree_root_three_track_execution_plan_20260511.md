# Botanical / Tree-Root Three-Track Execution Plan

Date: 2026-05-11 09:22 CST  
Status: active Ralph loop  
Local root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU rule: use only remote GPUs `4,5,6,7`; at most four GPU lanes.  
Storage rule: remote project must stay under `200GB`; delete only disposable caches or clearly obsolete generated intermediates, never unreviewed result evidence.  
Completion rule: no case is complete without remote OBJ/GLB, metrics CSV/JSON, controlled Blender render QA, zoom/contact sheets, provenance/license note, and paper-safe wording.

## Active Objective

The user wants three difficult visual cases pushed to publication grade:

1. **Fifth hero plant leaf.** A good root leaf/petiole module is the core. The current full-cluster cuts are too fragmented. Try better root selection, root cuts, direct external spider-plant/leaf assets, and tree-crown-like leaf growth schedules. The final sequence must have multiple depths that are all attractive and clearly different.
2. **Spider plant / fern / recursive roots.** Search and use license-clean meshes/images. Generate image roots with TRELLIS2 where useful, but simplify/crop before recursion. Final candidates must be semantically clear, natural, and not just connected by metrics.
3. **Fourth hero `tree_root_leaf`.** Use real semantic sources, not the presentation GLB. Make roots and leaves recursive. Root side must show thick-to-thin branching from a selected first-split/root-branch module for at least depth 4. Leaf side should attach repeated leaf/needle modules along branch/crown frontiers.

## Known Good And Bad Evidence

### 20260511l Positive Directions

- `tree_pine_v25l_yneg_20260511l/v25l_pine_leaf_cluster_clean/depth_04`: best current leaf/crown direction. Metrics: `PLCR=0.997`, vertex LCR `0.992`, occupancy components `5`, tokens `311 -> 335`, bbox delta `0.108`.
- `tree_pine_v25l_yneg_20260511l/v25l_pine_branch_tip_cluster/depth_04`: more visible growth, `PLCR=0.994`, vertex LCR `0.987`, tokens `311 -> 361`, bbox delta `0.167`.
- `spider_runner_v25l_yneg_20260511l/*/depth_04`: all main runner rows are metric-clean (`PLCR~0.997`, vertex LCR `0.986`, tokens `404 -> 436`) and should get Blender QA.
- `spider_broad_v25l_yneg_20260511l/v25l_spider_leaf_tip_clean` and `v25l_spider_leaf_treecrown`: backup rosette directions.

### 20260511l Negative Evidence

- Fifth hero plant true cuts still fail: `plant_leaf_basemid` and `plant_leaf_green` rows either fragment badly or become too subtle. Do not promote them.
- V23 `tree_rootfan` still fails the hero-root requirement: root rows either barely move or drop below clean connectivity. The requested four-depth thick-to-thin root hierarchy is not solved.
- Fiddlehead/crozier remains diagnostic: guarded curl fragments, alternative row is a no-op.
- Image roots remain diagnostic: low-complexity image roots are still too fragmented, plane-like, or too heavy.

## Source And Root Policy

- The presentation GLB `visuals/hero_botanical_variants_20260510/tree_compete_s3_green_leaf_brown_root.glb` is not a semantic recursion source. It is a height/material-split PBR visual asset.
- Preferred tree leaf source: `results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles/V23_lsys_pine_canopy_d5_multi_root_smooth_needles.obj`.
- Preferred tree root source: `results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_root_fan_d5_multi_root_smooth_rootlets/V23_lsys_root_fan_d5_multi_root_smooth_rootlets.obj`.
- Current SLat anchors are geometry-derived sparse-latent masks unless explicitly backed by a sidecar. Paper wording must say roots/anchors are authored or geometry-derived; it must not claim automatic semantic part discovery.

## Next Remote Batch Design

### Lane 4: Plant Leaf Root Selection

Goal: replace full-cluster copying with a cleaner root module.

Inputs to prepare:

- single or paired leaf/petiole cuts from `plant_leaf_green_cluster_root.obj` and `plant_leaf_base_mid_cluster_root.obj`;
- possible CC0/PD image-root plant/leaf candidate if a generated root can be simplified under token/face gates;
- attribution-lane direct spider plant mesh if a reproducible download is available.

Grammars:

- basal petiole handle copy;
- leaf fan with 2-4 children from a shared crown;
- depth schedule that increases leaf count and reduces size, like tree crown growth;
- no whole-thin-sheet cluster copy as primary operator.

Gate:

- depth `0..4` if stable, otherwise `0..3`;
- object-scale visible growth and no severe strip/dust fragments;
- target `PLCR >= 0.98` and vertex LCR `>= 0.98` for positive claim, but visual QA is decisive.

### Lane 5: Spider / Fern / External Botanical Roots

Goal: find a cleaner external or generated root than the current fifth-hero cuts.

Inputs:

- CC0/PD images: rubber fig aerial roots, tree aerial prop roots, spider plant CC0 photo/PD illustration, fiddlehead single curl, beech root strip;
- direct mesh candidates if downloadable: CC0 fern meshes, CC BY spider plant/root structure in separate attribution lane.

Process:

- crop to one semantic subject before image-root generation;
- generate root OBJ using TRELLIS2 image conditioning;
- if too heavy, decimate/remesh/crop before recursion;
- run only guarded depth `0..1/2` until root quality is proven.

Gate:

- root must be visually meaningful at depth 0 after decode;
- no positive recursion claim from raw high-poly image roots;
- CC BY assets need attribution and separate figure/table note.

### Lane 6: Tree Root Leaf

Goal: close the high-value fourth hero case.

Leaf side:

- continue from V23 pine with `v25l_pine_leaf_cluster_clean` and branch-tip variants;
- run Blender QA for 20260511l candidates before widening.

Root side:

- prepare explicit first-split/root-branch cuts or sidecar handles from V23 rootfan;
- recurse a coherent thick branch with shrink/taper first, then add fine rootlets late;
- avoid terminal fine-root masks as primary source because they produce dust.

Gate:

- root depth `0..4` with visible thick-to-thin branching;
- leaf depth `0..4` with branch/crown frontier recursion;
- merge only if both subprograms pass separately.

### Lane 7: Image Roots / Asset Generation

Goal: use TRELLIS2/image generation only where it improves root quality.

Inputs:

- low-complexity 512/768 crops, not full 1024 busy photos;
- optional generated images on a100-2 if needed to create cleaner guide images.

Gate:

- face/token gates before recursion: prefer under `250k` faces and under `2200` shape tokens after simplification;
- image-root outputs must have provenance and a root quality contact sheet.

## QA And Reporting

For every candidate promoted beyond diagnostics:

1. Pull selected OBJ sequences only, not full batch directories.
2. Run mesh metrics and record final-depth plus per-depth deltas.
3. Render controlled Blender white/studio contact sheets and zooms.
4. Mark one of:
   - `positive_candidate`
   - `diagnostic_only`
   - `rejected_noop`
   - `rejected_fragmented`
   - `rejected_semantic_mismatch`
5. Update this file and `botanical_tree_root_parallel_ralph_plan_20260511.md`.

## If The Next Batch Fails

- For plant leaf: stop trying full cluster cuts; acquire/directly build a cleaner leaf/petiole root mesh, even if it is an attribution-lane spider plant mesh.
- For spider/fern: treat image-root generation as root candidate creation only; simplify before recursion.
- For tree root: implement explicit sidecar handles from source construction, not quantile masks alone.
- For paper: write these as honest diagnostic limits until a visual-positive case passes all gates.

## Asset Scout Update

External asset probing found three useful lanes:

- **CC0/PD main-claim lane:** CGTrader `Forest Roots` is reported on-page as CC0 but must be screenshot/rechecked before final use; PRMI/Dryad and ChronoRoot2 provide CC0 root-image statistics; Sketchfab `CC0 Green Leopard Plant` is the best current plant-leaf direct mesh candidate if downloadable; CC0/PD spider/fern guide images remain safe for image-root generation.
- **Attribution visual lane:** Sketchfab tree-root scans, `Root-bound Chlorophytum`, `Spider Plant by sauti`, and PlantCatalog fern meshes are useful if the paper records title, author, URL, license, and modification notes. Keep these separate from CC0/PD claims.
- **Reference-only lane:** unclear-license large root downloads should only guide human root-cut/grammar design unless explicit permission is confirmed.

Most actionable next assets:

1. `CC0 Green Leopard Plant / broad leaf mesh` for a cleaner plant-leaf root than the current fifth-hero thin cluster.
2. `Forest Roots` or CC BY root scans for visual/root-shape root recursion, pending download/login and license capture.
3. `Root-bound Chlorophytum` image plus spider-plant crown mesh/image for a true spider-plant track.

## 20260511l Early-Depth QA Queue

Metric screening shows some final depth-4 rows are worse than early depths. Blender QA should therefore include early depths:

- `tree_pine/v25l_pine_leaf_cluster_clean/depth_01` and `depth_04`;
- `tree_pine/v25k_pine_terminal_needles/depth_01` and `depth_04`;
- `tree_rootfan/v25l_root_relaxed_wedge/depth_01` plus `depth_04` only as failure comparison;
- `spider_runner/v25k_spider_terminal_leaflet/depth_02`;
- `spider_broad/v25l_spider_leaf_tip_clean/depth_01`;
- `spider_broad/v25l_spider_leaf_treecrown/depth_01`;
- `fern_arch/fern_frond_pinnae_attach/depth_01`;
- `plant_leaf_green/v25l_spider_leaf_tip_clean/depth_02` and `plant_leaf_basemid/v25l_spider_leaf_tip_clean/depth_02` only as diagnostic evidence that current fifth-hero cuts are not enough.

Do not use these as final evidence until controlled material renders confirm that they are not just lateral strip growth, dust, or decode artifacts.

## 20260511l Selected Blender QA Verdict

Selected OBJ sequences were pulled to `results/botanical_tree_root_recursive_remote_20260511l_selected_meshes/` and rendered with controlled Blender material/white background:

- Contact sheet: `results/botanical_tree_root_recursive_remote_20260511l_selected_meshes/blender_qa_20260511l/contact_sheet_20260511l_selected_blender_whitecomposite.png`.

Visual verdict:

- `plant_leaf_green_tip_d02` and `plant_basemid_tip_d02` are not salvageable as paper positives. They look like torn, disconnected leaf-sheet piles with floating strips. This confirms the user critique that the current fifth-case root/grammar is semantically wrong, not just poorly lit.
- `spider_broad_tip_d01`, `spider_broad_treecrown_d01`, and `spider_runner_leaflet_d02` are the most natural-looking botanical shapes from 20260511l. They look like plausible rosette/runner plants and are worth one more controlled early-depth/gated sweep, though they are still procedural spider proxies rather than the fifth hero plant leaf.
- `fern_arch_pinnae_d01` is clean but too synthetic/flat to be a headline case. It can support a fern-frond supplement if later naturalized.
- `tree_pine_leaf_clean` and `tree_pine_terminal` look more like root/branch bundles than leaf/crown recursion under neutral botanical material. They are useful source semantics but not final hero leaf visuals.
- `tree_rootfan_relaxed_d01/d04` has a stronger tree/root silhouette but the recursive change is weak and top details are messy. It does not satisfy the requested four-depth thick-to-thin root hierarchy.

Action taken after this QA:

- Added v25n operators to `assets/trellis2_recursive_slat_grammar_workflow.py`:
  - `v25n_plant_basal_midrib_leaflet`
  - `v25n_plant_basal_crown_leaflets`
  - `v25n_spider_runner_leaflet_gated`
  - `v25n_fern_pinnae_sparse`
  - `v25n_fiddlehead_thick_curl`
  - `v25n_root_short_terminal_rootlets`
  - `v25n_root_first_split_taper`
  - `v25n_pine_leaf_gated`
- Added remote launcher `assets/run_botanical_tree_root_three_track_remote_20260511n.sh`.
- Local validation passed:
  - `python3 -m py_compile assets/trellis2_recursive_slat_grammar_workflow.py`
  - `bash -n assets/run_botanical_tree_root_three_track_remote_20260511n.sh`
- Synced to `a100-2`, remote validation passed, and launched 20260511n at `2026-05-11T09:35:09+08:00`.

20260511n remote output:

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/botanical_tree_root_recursive_remote_20260511n`

20260511n lane design:

- GPU 4: true fifth-hero plant cuts with basal/midrib leaf operators, depth 2 only.
- GPU 5: spider broad/runner plus fern/fiddlehead with gated early-depth grammars, depth 2 only.
- GPU 6: V23 rootfan and V23 pine with gated root/leaf repair, depth 2 only.
- GPU 7: depth-4 stress checks for the two most plausible directions, `spider_runner` and `tree_pine`, to test whether early-depth improvements survive deep recursion.

This is intentionally a small discriminative batch. Success means “promote to Blender QA and maybe extend”; failure means switch root assets/cuts rather than keep perturbing the same operators.

## Update 2026-05-11 09:58 CST: 20260511n Pull, Blender QA, And 20260511o Direction

20260511n is now fully pulled and QA-rendered locally.

Evidence:

- Remote output: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/botanical_tree_root_recursive_remote_20260511n`.
- Local pull: `results/botanical_tree_root_recursive_remote_20260511n_pull/`.
- Metrics: `results/botanical_tree_root_recursive_remote_20260511n_pull/metrics/botanical_tree_root_metrics_20260511n.csv` and `.json`.
- Preview sheet: `results/botanical_tree_root_recursive_remote_20260511n_pull/preview_contact_sheet_all_20260511n.png`.
- Selected OBJ pull: `results/botanical_tree_root_recursive_remote_20260511n_selected_meshes/`.
- Blender QA sheet: `results/botanical_tree_root_recursive_remote_20260511n_selected_meshes/blender_qa_20260511n/contact_sheet_20260511n_selected_blender_whitecomposite.png`.
- Compact selected metrics: `results/botanical_tree_root_recursive_remote_20260511n_pull/metrics/selected_depth_metrics_compact_20260511n.tsv`.

20260511n verdict:

- **True fifth-hero plant cuts remain rejected.** `plant_leaf_green_v25n` and `plant_leaf_basemid_v25n` with `v25n_plant_basal_*` operators still render as torn leaf-sheet piles with floating islands. Metrics agree: green depth-2 rows have `PLCR~0.81`, base-mid depth-2 rows have `PLCR~0.75`, and both have 90-100+ primary components. This is a root/grammar semantic failure, not lighting.
- **Best botanical positives are spider substitutes, not the original fifth hero.** `spider_broad_v25n/v25l_spider_leaf_tip_clean/depth_02` and `spider_runner_v25n/v25k_spider_terminal_leaflet/depth_02` are the cleanest natural plant candidates. They render as plausible rosette/runner plants and pass the metric gate (`PLCR 0.9939/0.9983`, vertex LCR `0.9956/0.9967`). `v25n_spider_runner_leaflet_gated` is rejected despite looking plausible in previews because metrics and Blender show fragmentation (`PLCR` falls to `0.14` by depth 4).
- **Fern is a clean supplement, not a headline.** `fern_arch_v25n/v25n_fern_pinnae_sparse/depth_02` is single-primary-component and visually clean, but the geometry is too flat/schematic to lead the paper.
- **Fiddlehead remains diagnostic.** `v25n_fiddlehead_thick_curl` still falls below the connectivity gate at depth 2 (`PLCR~0.76`) and does not form a strong recursive crozier.
- **Tree-root-leaf is still open.** `tree_pine_v25n_depth4/v25n_pine_leaf_gated/depth_04` is the cleanest four-depth root/bundle visual so far (`PLCR=0.9969`, vertex LCR `0.9915`), but it reads as a root/branch bundle rather than a complete root+leaf dual-recursion proof. `tree_rootfan_v25n/root_first_split_taper` improves early-depth semantics but depth 2 drops to `PLCR=0.9738` and 35 primary components, so it cannot satisfy the requested four-depth natural root hierarchy.

External asset update:

- Downloaded CC0 Poly Haven assets for cleaner root candidates under `downloads/polyhaven_botanical_cc0_20260511/`.
- Current direct assets are `fern_02` and `potted_plant_02` with local FBX/Blend/USD/gltf geometry plus API/license manifest.
- These are now preferred over further perturbing the failed fifth-hero thin-sheet cuts. Use them as CC0 main-claim root candidates if export/QA succeeds; keep Sketchfab/CC-BY assets separate as attribution-lane only.

20260511o design:

1. GPU 4: spider/plant positive extension. Re-run only metric/Blender-positive spider roots with `v25l_spider_leaf_tip_clean` and `v25k_spider_terminal_leaflet`; explicitly avoid `v25n_spider_runner_leaflet_gated`.
2. GPU 5: CC0 Poly Haven root/leaf candidates. Export `fern_02` and `potted_plant_02` to OBJ roots, simplify if needed, then run conservative fern/leaf grammars. If export quality is bad, skip recursion and mark as root-acquisition failure.
3. GPU 6: tree-root-leaf root side. Run V23 pine/rootfan with `v25n_pine_leaf_gated`, `v25l_root_primary_branch`, and whole-root macroscopic variants as a controlled stress test. Do not promote whole-root stamping unless it is visually natural and connected in Blender.
4. GPU 7: image/root fallback. Use low-complexity CC0/PD image conditions only after root-quality gating; no positive claims from heavy raw image roots.

Claim policy after 20260511n:

- The fifth hero plant-leaf true cuts are now **negative evidence** unless a new root extraction is introduced.
- The strongest near-term plant case should be a cleaner spider/rosette or CC0 broad-leaf asset, not the current fifth-hero cut.
- The fourth hero `tree_root_leaf` still requires a new root-handle/first-split subprogram before it can be called complete.

## Update 2026-05-11 14:40 CST: 20260511o Finished, Metrics/QA Gate Active

## Update 2026-05-11 15:45 CST: 20260511p Narrow Repair Batch

20260511o is now closed as diagnostic evidence, not final publication evidence.

Key verdicts:

- Spider runner and broad rosette are the best plant-positive directions, but Blender depth sequence shows d0-d4 are visually too similar.
- Poly Haven `fern_02_part00` and `potted_plant_02_leaves` remain useful CC0 candidates, but require targeted handles and selected Blender QA.
- V23 pine remains the best `tree_root_leaf` leaf-side source.
- V23 rootfan is still open; prior rootfan rows were rejected for weak depth change. Whole-root corner stamping is not a positive root recursion proof.

New plan:

- `docs/progress/botanical_tree_root_20260511p_execution_plan_20260511.md`
- `assets/run_botanical_tree_root_three_track_remote_20260511p.sh`

New `v25p_*` aliases were added to `assets/trellis2_recursive_slat_grammar_workflow.py`:

- `v25p_spider_runner_visible_chain`
- `v25p_spider_rosette_crown_fan`
- `v25p_potted_petiole_leaf_fan`
- `v25p_fern_midrib_pinnae_handles`
- `v25p_pine_branch_frontier_needle_whorl`
- `v25p_root_first_split_sidecar`
- `v25p_root_first_split_then_rootlets`

20260511p lanes:

- GPU 4: stronger spider/rosette visible-depth check.
- GPU 5: CC0 Poly Haven fern/potted plant targeted handles.
- GPU 6: V23 pine leaf side plus rootfan first-split with prior y-positive root orientation.
- GPU 7: rootfan first-split orientation stress using y-negative and lower fit-scale.

Claim policy:

- 20260511p is a discriminative repair batch. A clean metric row is not final unless Blender depth QA shows readable depth change and semantic handle placement.
- Failed fifth-hero thin-sheet cuts remain rejected unless a new root extraction is created.
- Raw image roots remain root-acquisition diagnostics only.

Detailed continuation note:

- `docs/progress/botanical_tree_root_20260511o_closeout_and_next_20260511.md`

Current facts to preserve:

- `20260511o` all lanes have exited on `a100-2`; remote output root is `results/botanical_tree_root_recursive_remote_20260511o`.
- `spider_positive`, `polyhaven_cc0`, `tree_root_leaf`, and `image_roots` all wrote OBJ/preview/image-root outputs.
- The `tree_root_leaf` lane summary was marked failed because the launcher used the wrong alias `v25n_whole_root_single_corner`; the correct alias is `v25n_whole_root_corner`.
- The launcher has been fixed locally and synced to remote.
- A separate one-off rootfan rerun `tree_rootfan_wholeroot_corner_fix_ypos_20260511o` completed successfully, but summary stats suggest it may be weak/no-op; metrics and Blender QA are required before judgment.
- Full `20260511o` metrics are running; next steps are lightweight pull, selected OBJ pull, controlled Blender QA, candidate ranking, and this doc update.
- TRELLIS1/classic should be reported as environment-blocked, not model-failed.
- Hunyuan text-root mesh-space negative control exists, but paint/texture and unified render/table integration remain open.

## Update 2026-05-11 16:45 CST: Tree-Root q Pivot

`20260511p` is closed:

- Remote outputs, metrics, selected OBJ pull, and Blender QA exist.
- Spider/fern/potted/tree-pine rows can be kept as supplement candidates.
- Rootfan sidecar rows are rejected for the fourth hero root side because depth change is weak and fragmentation remains high.

The next tree-root loop is `20260511q`:

- Plan: `docs/progress/tree_root_firstsplit_20260511q_execution_plan.md`
- Input generator: `assets/prepare_tree_root_firstsplit_candidates_20260511q.py`
- Remote launcher: `assets/run_tree_root_firstsplit_remote_20260511q.sh`
- Local input root pool: `results/tree_root_firstsplit_candidates_20260511q/`

Important boundary:

- The q input pool is a clean root-handle acquisition step only. It is not final evidence and cannot replace remote SLat recursion.
- Promote only if remote q outputs pass metrics and controlled Blender QA with visible depth-4 thick-to-thin first-split hierarchy.
