# Botanical / Tree-Root 20260511p Execution Plan

Date: 2026-05-11 15:45 CST  
Status: launching next narrow Ralph batch  
Local root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU rule: use only remote GPUs `4,5,6,7`.  
Storage rule: remote project is about `142G`, below the relaxed `200GB` cap; keep p selected and do not pull full heavy OBJ trees unless selected.  
Evidence rule: no result is publication-grade without OBJ/GLB, metrics CSV/JSON, controlled Blender QA, depth/zoom/contact sheets, provenance/license notes, and paper-safe wording.

## Why 20260511p Exists

`20260511o` closed the technical gate but not the visual depth gate.

- Spider runner and broad rosette rows are the best plant-positive directions, but controlled Blender depth sequence shows d0-d4 are too similar.
- Poly Haven potted leaves and fern part have promising metrics, but need more semantically targeted handles and render QA.
- V23 pine is still the best `tree_root_leaf` leaf-side source.
- V23 rootfan remains open: 20260511o `v25l_root_primary_branch` and `v25l_root_two_phase` are metric-rejected as weak depth change. Whole-root corner stamping is technical success but likely a no-op/diagnostic.

Therefore p is intentionally narrow: stronger but still bridged handles, no whole-root positive claim, no failed fifth-hero thin-sheet cuts, and no raw image-root positive claim.

## New Code

Modified:

- `assets/trellis2_recursive_slat_grammar_workflow.py`

Added aliases:

- `v25p_spider_runner_visible_chain`
- `v25p_spider_rosette_crown_fan`
- `v25p_potted_petiole_leaf_fan`
- `v25p_fern_midrib_pinnae_handles`
- `v25p_pine_branch_frontier_needle_whorl`
- `v25p_root_first_split_sidecar`
- `v25p_root_first_split_then_rootlets`

Added remote launcher:

- `assets/run_botanical_tree_root_three_track_remote_20260511p.sh`

## Remote Lanes

### GPU 4: Spider / Rosette Visible-Depth Check

Inputs:

- `results/fern_root_candidates_20260511h/spider_rosette_publication_runner_20260511h/spider_rosette_publication_runner_20260511h.obj`
- `results/fern_root_candidates_20260511h/spider_rosette_publication_broad_20260511h/spider_rosette_publication_broad_20260511h.obj`

Runs:

- `spider_runner_visible_d4_yneg_20260511p`
- `spider_broad_crownfan_d4_yneg_20260511p`

Goal: determine whether stronger runner/rosette handles give clear d0-d4 visual progression without turning into floating strips.

### GPU 5: CC0 Poly Haven Botanical Check

Inputs:

- `results/polyhaven_botanical_cc0_roots_20260511/fern_02/fern_02_part00.obj`
- `results/polyhaven_botanical_cc0_roots_20260511/potted_plant_02/potted_plant_02_leaves.obj`
- `results/polyhaven_botanical_cc0_roots_20260511/potted_plant_02/potted_plant_02_part00.obj`

Runs:

- `polyhaven_fern_part_handles_d3_yneg_20260511p`
- `polyhaven_potted_leaves_fan_d3_yneg_20260511p`
- `polyhaven_potted_part_fan_d3_yneg_20260511p`

Goal: try license-clean fern/potted roots with targeted petiole/midrib handles. `potted_plant_02_leaves` is high-face and needs selected pull/Blender QA only.

### GPU 6: Tree Leaf Side + Root Y-Positive Diagnostic

Inputs:

- `results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles/V23_lsys_pine_canopy_d5_multi_root_smooth_needles.obj`
- `results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_root_fan_d5_multi_root_smooth_rootlets/V23_lsys_root_fan_d5_multi_root_smooth_rootlets.obj`

Runs:

- `tree_pine_leaf_visible_d4_yneg_20260511p`
- `tree_rootfan_firstsplit_d4_ypos_20260511p`

Goal: improve leaf-side visibility and test first-split root handles under the prior root orientation.

### GPU 7: Root Orientation Stress

Input:

- V23 rootfan same as above.

Runs:

- `tree_rootfan_firstsplit_d4_yneg_20260511p`
- `tree_rootfan_firstsplit_fit052_yneg_20260511p`

Goal: answer the user's orientation concern directly by trying the opposite growth sign and lower fit scale, so child roots have more latent room. This is diagnostic until Blender confirms the growth direction and first-split semantics.

## Forbidden / Diagnostic Only

- Do not rerun `plant_leaf_green_cluster_root.obj` or `plant_leaf_base_mid_cluster_root.obj` as main lanes. They are rejected fragmented unless a new clean root extraction is made first.
- Do not use `v25n_spider_runner_leaflet_gated`; prior depth-4 row fragments badly.
- Do not use `v25n_whole_root_single_corner`; it is an invalid alias. `v25n_whole_root_corner` exists but remains diagnostic/no-op-like.
- Do not promote raw image roots from 20260511o without simplification and root-quality QA.
- Do not promote `polyhaven_fern_all` rows; they were metric-rejected as fragmented.

## QA Gate

After remote completion:

1. Run launcher `metrics`.
2. Pull light artifacts only: manifest, logs, summary JSON, metrics, previews.
3. Select final-depth OBJ plus full depth sequences for any possible positive.
4. Render Blender selected final sheet and depth sequence with `assets/blender_render_recursive_mesh.py`.
5. Pass/fail:
   - Positive candidate needs `PLCR >= 0.95`, preferred vertex LCR `>= 0.95`, visible object-scale depth change, no major islands in Blender, and correct semantic handle.
   - Reject as weak-depth if bbox/extent change is tiny or d0-dN reads as the same mesh with more tokens.
   - Reject as semantic mismatch if the new growth appears on the wrong side, becomes sheet debris, or fails to read as attached root/leaf modules.

## Baseline Status To Preserve

- TRELLIS1/classic is still blocked by runnable environment (`open3d`, `kaolin`, `torchvision::nms`, CUDA/PyTorch extension compatibility). This is not a fair model failure unless a runnable one-shot smoke exists.
- Hunyuan text-root mesh-copy negative control exists for the fair mesh-space comparison, but Hunyuan paint/texture and unified render/table integration remain open.

## Closeout 2026-05-11 16:45 CST

`20260511p` completed remote SLat runs, metrics, selected OBJ pull, and controlled Blender QA. Output root:

- Remote: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/botanical_tree_root_recursive_remote_20260511p`
- Local pull: `results/botanical_tree_root_recursive_remote_20260511p_pull/`
- Metrics: `results/botanical_tree_root_recursive_remote_20260511p_pull/metrics/botanical_tree_root_metrics_20260511p.csv`
- Gate summary: `results/botanical_tree_root_recursive_remote_20260511p_pull/analysis/metric_gate_summary_20260511p.csv`
- Blender QA: `results/botanical_tree_root_recursive_remote_20260511p_pull/blender_qa_20260511p/contact_sheet_blender_selected_20260511p_whitecomposite.png`

Supplement candidates only:

- `spider_runner_visible_d4_yneg_20260511p/v25p_spider_runner_visible_chain`: depth change is more visible than previous spider rows, but leaf tearing and fragment/sheet noise remain. Use only as supplement/diagnostic.
- `polyhaven_fern_part_handles_d3_yneg_20260511p/v25k_spider_terminal_leaflet`: clean fern/leaf supplement candidate (`PLCR=0.9948`, vertex LCR `0.9936`, low primary component count).
- `polyhaven_potted_leaves_fan_d3_yneg_20260511p/v25l_spider_leaf_tip_clean`: semantically useful potted-plant supplement, but high face/render pressure and some bottom fragmentation.
- `tree_pine_leaf_visible_d4_yneg_20260511p/v25n_pine_leaf_gated` and `v25p_pine_branch_frontier_needle_whorl`: usable leaf/branch supplement candidates, not proof of the requested root-side hierarchy.

Rejected root-side rows:

- `tree_rootfan_firstsplit_d4_yneg_20260511p/v25p_root_first_split_sidecar`
- `tree_rootfan_firstsplit_d4_ypos_20260511p/v25p_root_first_split_sidecar`
- `tree_rootfan_firstsplit_fit052_yneg_20260511p/v25p_root_first_split_then_rootlets`

Reason: root rows either have weak bbox/depth change or high fragmentation/component counts. The whole V23 rootfan is too diffuse for the current masks to reliably lock onto the first-split semantic handle.

Next loop:

- `docs/progress/tree_root_firstsplit_20260511q_execution_plan.md`
- `assets/prepare_tree_root_firstsplit_candidates_20260511q.py`
- `assets/run_tree_root_firstsplit_remote_20260511q.sh`

q changes the root-acquisition step: use clean first-split input modules with explicit trunk/split/terminal-rootlet anchors, then run remote SLat recursion. Do not present the local modules themselves as final evidence.
