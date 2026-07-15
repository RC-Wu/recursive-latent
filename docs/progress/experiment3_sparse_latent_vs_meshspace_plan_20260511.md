# Experiment 3 Sparse-Latent Grammar vs Mesh-Space Alternatives Plan

Date: 2026-05-11 CST  
Status: active Ralph-loop execution plan, version 0.1  
Project root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
Remote inference GPU cap for this experiment: at most 2 GPUs, use `CUDA_VISIBLE_DEVICES=4,5` unless the user changes the cap.  
SSH cap for this experiment: prefer 1 persistent SSH shell, never more than 2.  
Publication gate: do not claim closure without GLB/OBJ outputs, metrics CSV/JSON, unified renders, zoom panels, and a paper-safe provenance note.

## 0. Recovery Contract

After heartbeat, compaction, or agent handoff, read this file first, then read:

1. `docs/progress/ralph_publication_closure_plan_20260510.md`
2. `docs/evaluation/hunyuan_text_root_meshspace_protocol_zh_20260511.md`
3. `docs/progress/remote_baseline_audit_20260511_subagent.md`
4. `docs/progress/root_candidate_scout_20260511.md`
5. `docs/progress/botanical_tree_root_parallel_ralph_plan_20260511.md`
6. `docs/progress/ablation_gap_audit_20260511_subagent.md`
7. `paper_siga/main.tex`, around the Experiment Logic / novelty-gate TODO
8. latest `docs/progress/experiment3_*_subagent_20260511.md` notes, if present

The target is a SIGGRAPH-grade novelty gate, not a gallery. Each figure/table row must answer this question:

> Why is PS-RSLG more than procedural mesh copy, procedural texture export, one-shot 3D generation, or trivial latent transform-copy?

## 1. Experiment Claim

### Main Claim

PS-RSLG executes recursive structure as a sparse-latent stateful grammar. The grammar owns typed handles, admissibility, local masks, projection, and per-depth re-encoding. Classical procedural meshes, mesh-space copies after a one-shot generator, and trivial latent/voxel transform-copy can produce repeated objects, but they do not maintain grammar-readable recursive state, do not naturalize junctions under the generator prior, and fail when reused as a controlled multi-depth recursive system.

### What Experiment 3 Must Prove

1. Classical/procedural mesh baselines can express recursive topology, but their surfaces/materials remain procedural and brittle under export/texture transfer.
2. Procedural mesh plus smoothing/remesh can reduce blockiness, but it does not create generator-native local structure or semantic junctions.
3. Procedural mesh plus Trellis2 texture/PBR export tests compatibility only. It is not a recursive generation method because topology is still procedural.
4. Hunyuan mesh-space recursion is a fair mesh-based generated-root baseline only when it uses `text prompt -> generated root mesh -> deterministic mesh S/R/T copy -> direct concat`; full recursive guide-image generation is only a one-shot baseline.
5. Trellis2 one-shot image-conditioned generation can make plausible single objects, but does not enforce the target recursive attachment pattern under the same root/guide.
6. Trellis2 trivial latent transform-copy / voxel-copy can preserve local samples, but lacks handles, admission, projection, and per-depth re-encoding; failures should show fragmentation, aliasing, or uncontrolled repetition.
7. PS-RSLG should win on structure validity, local detail consistency, export/render compatibility, and human-visible zoom quality for selected high-quality recursive cases.

## 2. Method Rows

Use these rows consistently in figures, CSVs, and LaTeX tables. Do not silently merge rows.

| Row id | Paper label | Definition | Main use | Must not claim |
|---|---|---|---|---|
| `classical_proc` | Classical procedural mesh | Hand/procedural grammar directly outputs mesh for the target recursive form. | Structural lower/upper bound for topology. | Learned generation, texture/PBR naturalization, generator-native state. |
| `classical_smooth` | Procedural mesh + smooth/remesh | Same mesh after light smoothing/remesh/decimation. | Shows postprocess cannot solve recursive state/natural junctions. | Learned recursion or fair replacement for PS-RSLG. |
| `proc_trellis2_texture` | Procedural mesh + Trellis2 texture/PBR | Procedural mesh exported through Trellis2 texturing/PBR path. | Export/material compatibility baseline. | Topology improvement or recursive generation. |
| `hunyuan_root_meshcopy` | Hunyuan root + mesh-space recursion | Text prompt generates a root primitive image/mesh; the root mesh is scaled/rotated/translated and directly concatenated. | Main mesh-based generated-root baseline. | Full Hunyuan recursive generation, topology-aware recursion, handle-aware junctions. |
| `hunyuan_root_meshcopy_smooth` | Hunyuan root + mesh copy + smooth | Same as above plus light Laplacian/smoothing/remesh, reported separately. | Mesh-route upper bound. | Learned naturalization; it is only postprocess. |
| `trellis2_oneshot_image` | Trellis2 one-shot image-conditioned | Condition with either the full recursive target guide or PS-RSLG render/low-res guide and generate once. | Ordinary one-shot latent/voxel generator baseline. | Same-root recursive state execution. |
| `trellis2_root_latentcopy` | Trellis2 root + trivial latent copy | Condition/generate the root only, then transform/copy sparse latent/voxel regions without PS-RSLG admission/projection/re-encode policy. | Main latent-space trivial-copy negative control. | PS-RSLG, learned per-depth state, projection-stabilized recursion. |
| `ps_rslg` | PS-RSLG | Proposed stateful sparse-latent recursive grammar with typed handles, masked local naturalization, projection, and per-depth re-encode. | Positive row. | Universal procedural modeling or physical simulation. |

Optional diagnostic rows can appear in supplement: `trellis_classic_oneshot` if TRELLIS non-2 ever becomes runnable, old Hunyuan full-guide one-shot, global post-hoc repair, and final-only cleanup.

## 3. Shared-Root / Same-Condition Protocol

### Strict Shared-Root Protocol

For each selected case, prepare:

1. `root_image`: an image of the non-recursive root primitive or a single-depth root view.
2. `recursive_guide_image`: a low-res render of the full target PS-RSLG case or traditional recursive guide.
3. `root_mesh`: the same root OBJ/GLB when a method can consume mesh or when a root mesh is generated by Hunyuan/Trellis2.
4. `grammar_trace`: target depth, instance transforms, handles/anchors if available.

Apply rows as follows:

- Classical rows use the same grammar family and depth.
- Procedural + Trellis2 texture uses the classical mesh topology, then Trellis2 texture/PBR only.
- Hunyuan mesh-copy uses text to generate only the root primitive, then the same S/R/T grammar depth and instance schedule.
- Trellis2 one-shot uses `recursive_guide_image` for the full object; if image-conditioning requires the strongest guide, use our own PS-RSLG render as input and disclose it.
- Trellis2 latent-copy uses `root_image` or `root_mesh` to create the root latent/voxel, then applies the same transform schedule without projection/admission.
- PS-RSLG uses the same root family, target depth, and grammar trace.

### Fairness Rule

The comparison is fair when the competing methods receive a root or guide that is at least as informative as PS-RSLG's root. It is acceptable to condition Trellis2/Hunyuan with our own root or target render because the test is not prompt creativity; the test is whether the method can preserve a controlled recursive structure.

## 4. Case Quality Gate And Candidate Pool

### Main-Paper Gate

As of the 2026-05-11 user update, the main paper must not use weak or merely diagnostic cases as primary evidence. The main Experiment 3 figure/table is quality-gated, not just coverage-gated.

Main-paper candidates:

1. `tree_crown` / `V25_sc_tree_crown_tapered_B`: strongest botanical/tree state-execution candidate with Hunyuan text-root mesh-copy coverage.
2. `bismuth` / `V21_ifs_bismuth_stepped_transform_d5_iridescent`: user-preferred visually strong terraced crystal case; use as a main non-tree case only after the fair Hunyuan text-root mesh-copy row is generated and ingested.
3. `coral` / `V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA`: strong organic/frontier case with Trellis2 and Hunyuan mesh-space coverage; do not describe as biological simulation.
4. `pyrite` / `V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA`: useful crystal/lattice novelty-gate row, but caption and table status must keep the component caveat.

Supplement/diagnostic unless improved:

- `root_fan`: topology-safe but not visually strong enough for the new main-paper gate.
- `vine`: interesting, but current selected-vs-strict caveat and component caveat make it supplement unless re-rendered/upgraded.
- `spider_rosette`: QA-gated and not yet main-paper ready.
- `radial_ornament`: metric-stable but visually abstract/diagnostic under the new gate.

Implementation rule:

- `assets/experiment3_build_table_20260511.py` now emits a quality-gated main table for `tree_crown`, `bismuth`, `coral`, and caveated `pyrite`, plus a separate eight-case supplement table. Do not manually re-expand the main table to all eight rows unless the visual QA gate is re-opened and documented.
- The main visual matrix should be regenerated with the same main-case subset once the bismuth Hunyuan row is available. The full eight-case matrix remains supplement/status evidence.

### Eight Candidate Cases

Version 0.1 case list below is a working shortlist from current local evidence. It is no longer identical to the main-paper evidence set. The quality gate above decides which rows can enter the main paper.

### Botanical / Tree / Plant Cases

| Case id | Target family | PS-RSLG candidate | Why it belongs | Risk / gate |
|---|---|---|---|---|
| `bot_vine_tendrils` | Climbing vine / tendrils | `visuals/strict_visual_matched_texture_V22_botanical_smooth_20260510/V22_lsys_climbing_vine_d6_smooth_leaf_tendrils_steps8_tex2048_seed20260732_xformers/textured.glb` | Existing visually strong vine with leaves/tendrils and zoom renders; good for tree/plant recursive growth. | Must avoid mixing selected vine row with older weak strict row. |
| `bot_pine_canopy_root` | Pine canopy + root/needles | `visuals/strict_visual_matched_texture_V23_all_family_20260510/V23_lsys_pine_canopy_d5_multi_root_smooth_needles_steps8_tex2048_seed20262810_xformers/textured.glb` and seed variants | Good tree/canopy recursive case with needle/leaf detail and shared-vertex procedural root provenance. | Needs final selection among seed 20260510/11/12/13 and unified render QA. |
| `bot_tree_crown_leafshield` | Space-colonization tree crown | `visuals/strict_visual_matched_texture_V25_root_sc_refine_20260510/V25_sc_tree_crown_leafshield_B_steps8_tex2048_seed20285524_xformers/textured.glb` | Strong crown-like root, good for showing controlled branching/crown recursion. | Leaf shield can hide topology; include structural/tapered variant if used. |
| `bot_plant_leaf_base` | Plant leaf with base / rosette | `results/plant_leaf_recursive_root_20260511/inputs/plant_leaf_base_mid_cluster_root.obj` plus 20260511i/j recursive outputs after QA | Directly addresses user-requested plant-leaf case; can show root/leaf module recursion. | Current 20260511g/i evidence is diagnostic until Blender QA and semantic depth-change pass. |

Fallback botanical candidates: `V25_sc_tree_crown_tapered_B`, `V25_lsys_root_fan_dense_anchorD_stable`, `V24_sc_root_network_260_anchorA_seedA`, `V22_lsys_climbing_vine_d6_smooth_leaf_tendrils`, `V29_sc_tree_hidden_trunk`, `V27_sc_tree_organic_seam`, corrected spider rosette, corrected fern arch/lacy roots.

### Non-Tree Cases

| Case id | Target family | PS-RSLG candidate | Why it belongs | Risk / gate |
|---|---|---|---|---|
| `non_bismuth_terraced` | Bismuth terraced crystal | `visuals/hero_combo_publication_20260510_contrast_wide_1200/overview.png` plus underlying hero bismuth GLB to resolve | Very strong pyramid/terraced recursive visual and requested hero case. | Need exact GLB provenance and a per-case render, not only combined overview. |
| `non_pyrite_lattice` | Pyrite / IFS crystal | `visuals/strict_visual_matched_texture_V21_ifs_transform_natural_20260510` family and Hunyuan `pyrite_crystal_root` mesh-copy row | Good non-tree case where mesh-copy and latent-copy should visibly repeat blocks without valid junctions. | Pick one seed with connected PS-RSLG and clean PBR. |
| `non_coral_branching` | Coral / DLA frontier | `visuals/strict_visual_matched_texture_v14_branching_coral_20260510` or `visuals/strict_visual_matched_texture_v16_natural_coral_20260510` family | Strong organic branching, directly matches completed Hunyuan/coral mesh-space baseline and user hero coral. | Coral must be smoothed for hero if voxel-like; DLA fragmentation risk must be gated. |
| `non_radial_or_ifs_ornament` | Radial / IFS ornament / frontier sheet | `visuals/matched_camera_zoom_transform_dla_candidates_20260510` or `visuals/strict_visual_matched_texture_V20_paper_coral_crystal_20260510` family | Gives a fourth non-tree category beyond crystal/coral; useful to avoid overfitting to two families. | Must choose a case with clear recursive support and no large fragments. |

Fallback non-tree candidates: bismuth depth textured showcase, pyrite V21 seed20292500/20293300/20293700, coral V11/V12/V13/V14/V16 seeds, DLA organic v7/v8/v9 if connected, radial transform candidates, V20 paper coral/crystal, weak-search candidates only as negative controls.

## 5. Baseline Expansion Queue

### P0 Rows Needed For Each Main Case

For all 8 cases:

- `classical_proc`: locate/generate procedural mesh and metric row.
- `classical_smooth`: smooth/remesh row from the same classical mesh.
- `proc_trellis2_texture`: Trellis2 texture/PBR export from the same classical mesh.
- `trellis2_oneshot_image`: image-conditioned one-shot from the full recursive guide or PS-RSLG render.
- `trellis2_root_latentcopy`: root-conditioned trivial latent/voxel transform-copy.
- `ps_rslg`: final selected OBJ/GLB, metrics, overview and zoom renders.

For at least 4 representative cases, preferably 2 botanical and 2 non-tree:

- `hunyuan_root_meshcopy`: text-root Hunyuan root -> S/R/T mesh-copy direct row.
- `hunyuan_root_meshcopy_smooth`: light smoothing upper-bound row.

Current Hunyuan fair mesh-copy rows already closed for:

- `tree_trunk_branch`
- `pyrite_crystal_root`
- `coral_branch_root`

These should be mapped to selected main cases or extended to better-matched roots if visual comparison demands it.

### P1 Rows

- Hunyuan text-root mesh-copy for the plant-leaf/base case and bismuth/radial case if prompt/primitive generation is stable.
- Same-root root image conditions for every Trellis2 one-shot and latent-copy row.
- Unified Blender renders and zoom-in panels for completed baseline GLBs/OBJs.
- Runtime/peak-memory logging for all remote rows.

### P2 Rows / Supplement

- TRELLIS classic/non-2 one-shot if dependency stack becomes runnable.
- Hunyuan full recursive guide-image one-shot, clearly labeled as one-shot only.
- Global repair and final-only cleanup diagnostics.
- More seeds for robustness when time allows.

## 6. Metrics

Do not center the table on vertex/face/file size. Those can be supplement or runtime/export accounting. Main metrics must cover structure, surface, local detail, export, and semantic/visual consistency.

### Structure Validity

| Metric | Definition | Primary rows |
|---|---|---|
| `root_reachable_active_ratio` | Fraction of active grammar/frontier samples reachable from the root component. | PS-RSLG, classical, latent-copy where trace exists. |
| `invalid_fired_handle_count` | Handles that fired from orphan/invalid components. | PS-RSLG ablation and latent-copy. |
| `orphan_frontier_ratio` | Active frontier samples not attached to root-reachable support. | PS-RSLG, latent-copy. |
| `raw_component_count` | Connected components in raw face adjacency. | All mesh/OBJ rows. |
| `occupancy_component_count_6n` | 6-neighbor components after voxelization. | All rows. |
| `largest_occupancy_component_ratio_6n` | Occupancy largest-component ratio. | All rows, but never alone. |
| `copy_repetition_score` | Fraction or flag indicating exact repeated root instances after copy. | Mesh-copy and latent-copy rows. |
| `projection_used`, `latent_update_used`, `generator_calls_after_root` | Route flags, used to prevent row conflation. | All rows. |

### Surface Quality

| Metric | Definition | Input |
|---|---|---|
| `small_island_ratio` | Vertex/face mass outside the root-largest component or below island threshold. | OBJ/GLB mesh. |
| `degenerate_face_ratio` | Zero/near-zero area faces divided by total faces. | OBJ/GLB mesh. |
| `nonmanifold_edge_ratio` | Edges incident to not exactly two faces, normalized. | OBJ/GLB mesh. |
| `normal_consistency` | Neighboring face normal agreement or trimesh equivalent. | OBJ/GLB mesh. |
| `roughness_proxy` | Local normal/curvature variation at a normalized scale. | OBJ/GLB mesh. |

### Local Detail Consistency

| Metric | Definition | Input |
|---|---|---|
| `zoom_retention_score` | Similarity/visibility of recursive local features across overview, zoom1, zoom2. | Render crops or camera renders. |
| `terminal_detail_count` | Count of terminal leaves/tips/crystal facets/coral branches detected by geometry or trace. | Trace + mesh. |
| `multiscale_feature_density` | Feature counts per surface area or bbox scale at root, mid, terminal regions. | Mesh + trace. |
| `patch_style_consistency` | DINO/LPIPS or geometry histogram consistency across repeated local modules. | Render patches or mesh patches. |

### Texture / Export Compatibility

| Metric | Definition | Input |
|---|---|---|
| `glb_import_success` | Blender/trimesh can import GLB without fatal errors. | GLB. |
| `material_channel_count` | Count of usable base color/roughness/normal/metallic channels. | GLB material tree. |
| `texture_coverage_ratio` | Non-missing UV/material coverage, if available. | GLB/texture files. |
| `render_nonblank_qa` | Render has nonblank foreground and no all-white/all-black failure. | Render PNG. |
| `render_warning_count` | Warnings during Blender import/render. | Render log. |

### Visual / Semantic

| Metric | Definition | Status |
|---|---|---|
| `clip_image_text_score` | CLIP similarity between render and case prompt. | Useful appendix/main secondary. |
| `dino_reference_similarity` | DINO similarity to root or target guide where applicable. | Diagnostic. |
| `gpt_preference_score` | GPT visual preference/critique score. | Placeholder for later; leave blank until run. |
| `human_preference_rate` | User study preference rate. | Optional; leave blank until user supplies/approves. |

### Runtime / Memory

| Metric | Definition |
|---|---|
| `inference_seconds_total` | End-to-end generation/runtime for the method row. |
| `peak_gpu_mem_gb` | Peak memory from logs or `nvidia-smi`. |
| `generator_calls_total` | Number of calls to Trellis2/Hunyuan after initial root. |
| `export_seconds` | GLB/texture/export time. |
| `render_seconds` | Blender render time for QA figure. |

## 7. Figure Design

### Main Figure For Experiment 3

Use a compact matrix, likely 4 selected cases in main paper and 8 in supplement:

Rows: selected cases.  
Columns:

1. root / condition inset
2. classical procedural mesh
3. procedural + smoothing/remesh
4. procedural + Trellis2 texture/PBR
5. Hunyuan root + mesh-space copy
6. Trellis2 one-shot image-conditioned
7. Trellis2 root + trivial latent-copy
8. PS-RSLG
9. PS-RSLG zoom pair or nested zoom

If this is too wide, split into two figures:

- Fig. 1: visual method matrix, four cases, no text inside panels.
- Fig. 2: zoom-in failure/success panels, two botanical and two non-tree cases.

Panel rules:

- Pure white or consistent paper background unless matching the hero style; no colored blocks, titles, or teaser text inside images.
- Subfigure labels only below panels, Times New Roman when assembled for paper.
- Baseline failures should be honest, readable failures, not artificially destroyed.
- Zoom panels must be camera renders when possible, not just 2D crops.

### Supplement Figure

Eight-case full matrix plus per-case zoom:

- four botanical/tree/plant cases
- four non-tree cases
- method rows above
- route flags and concise failure labels in caption or side table, not overlaid on the images

## 8. Table 3 / Quantitative Layout

Main table should be an expanded but compact Table 3:

Columns:

1. `Case group`
2. `Method`
3. `Struct. valid` composite or `root reach. / orphan`
4. `Raw comp.`
5. `Occ. comp. / LCR`
6. `Small island / nonmanifold`
7. `Local detail`
8. `Export QA`
9. `CLIP` or visual-semantic score
10. `Runtime / peak mem`

Use arrows in header: higher/lower is better. Use mean/std over cases where row coverage is complete; otherwise report selected-case values and mark supplement.

Supplement tables:

- full per-case metrics CSV
- vert/face/file size
- route flags
- runtime/memory logs
- Hunyuan root-generation details
- failure labels and blocked rows

## 9. Paper Writing Contract

The main experiment section should be claim-driven:

1. Define the novelty gate: procedural topology, texture export, one-shot generation, mesh-copy, and latent-copy are not enough for stateful recursive generation.
2. Explain the matched protocol: same target root/guide/depth where possible; generated-root baselines get generous conditioning.
3. Present the visual matrix: alternatives can make repeated objects, but fail at junction continuity, root reachability, local detail stability, or controlled recursion.
4. Present metrics: combine handle/structure, mesh quality, detail, export, and runtime. Do not lean on LCR alone.
5. State Hunyuan result carefully: Hunyuan is strong as a one-shot/root generator, but after root generation, mesh-space copy produces repeated surface islands and lacks recursive state; smoothing is a postprocess upper-bound, not a learned grammar.
6. State Trellis2 result carefully: one-shot Trellis2 can synthesize plausible objects, and trivial latent-copy can repeat local chunks, but without typed handles, projection, and re-encoding it does not maintain valid recursive execution.
7. State PS-RSLG advantage: it is not just better-looking; it maintains active recursive state and supports local generator realization across depths.

Do not write:

- "Hunyuan cannot generate trees/coral/crystals." It can generate one-shot roots/objects; the failure is mesh-space recursive reuse.
- "Trellis2 fails." It is the frozen generator backbone and a strong one-shot baseline; the failure is trivial copy without PS-RSLG controls.
- "Mesh-space is impossible." The claim is narrower: direct mesh copy/smoothing/texture export does not provide generator-native stateful recursive execution.
- "Effective resolution is proven" unless the zoom-retention pipeline is completed. Treat current effective-resolution as proxy/diagnostic.

## 10. Execution Tasks

### Task A: Case Inventory And Asset Mapping

Owner: local subagent `experiment3_case_inventory`.

- [ ] Read current candidate docs/results/visuals.
- [ ] Select 8 main cases and 20 backups.
- [ ] For each main case, record PS-RSLG GLB/OBJ, preview, root mesh, root/recursive condition image, existing baseline rows, missing rows.
- [ ] Write `docs/progress/experiment3_case_inventory_subagent_20260511.md`.

Acceptance:

- No main case is selected without a PS-RSLG asset and visual preview.
- Missing baseline rows are explicit P0/P1/P2 tasks.

### Task B: Metric Protocol And Table Design

Owner: local subagent `experiment3_metrics_protocol`.

- [ ] Read current metric scripts and CSVs.
- [ ] Map each proposed metric to existing script or needed script.
- [ ] Propose Table 3 main/supplement split.
- [ ] Write `docs/progress/experiment3_metrics_protocol_subagent_20260511.md`.

Acceptance:

- Every main metric has a definition, input, and calculation path.
- Current evidence boundaries are stated explicitly.

### Task C: Build Master Manifest

Owner: main agent after Task A/B returns.

- [ ] Create or update `results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_master_manifest.csv`.
- [ ] Include all 8 cases x method rows with status: `ready`, `needs_remote`, `needs_local_render`, `blocked`, `diagnostic`, or `excluded`.
- [ ] Include path columns for root, condition image, OBJ/GLB, preview, render, metrics.

Acceptance:

- A single CSV can drive both remote runs and figure/table assembly.

### Task D: Remote Baseline Runs

Owner: main agent, one SSH shell, GPUs 4 and 5 only.

Remote run policy:

- GPU 4: Trellis2 one-shot and trivial latent-copy queue.
- GPU 5: Hunyuan text-root mesh-copy expansion queue.
- Keep cache under remote project root.
- Write logs, command snapshots, manifests, and metrics under `results/experiment3_sparse_latent_vs_meshspace_20260511/` and `logs/experiment3_sparse_latent_vs_meshspace_20260511/`.
- Stop/pause a lane if storage approaches 200GB or if repeated outputs are visually unusable after two corrected attempts.

Acceptance per remote row:

- input condition/root exists
- output OBJ/GLB exists and is non-empty
- metrics row exists
- preview render exists
- command/log exists
- status/failure label is explicit

### Task E: Local Classical / Smooth / Texture Rows

Owner: main/local worker.

- [ ] For every selected case, locate or generate classical procedural mesh.
- [ ] Generate smoothing/remesh row with conservative settings.
- [ ] Export procedural mesh through Trellis2 texture/PBR route where feasible.
- [ ] Compute metrics and render previews.

Acceptance:

- Classical rows are not strawmen; they should be competent procedural baselines.
- Smoothing rows are separated from texture/PBR rows.

### Task F: Unified Render And Zoom QA

Owner: main/local worker.

- [ ] Render all selected rows with the same Blender camera/background style.
- [ ] Render zoom panels for at least two levels: overview -> local recursion -> terminal detail.
- [ ] Run render QA: nonblank, foreground size, background uniformity, no horizon seam if used.
- [ ] Assemble draft contact sheets for user visual review.

Acceptance:

- Every promoted row has a render and at least one zoom where relevant.
- Main-paper images contain no in-image text except later subfigure labels assembled in LaTeX.

### Task G: Paper Integration

Owner: main agent after data closes.

- [ ] Replace old `gen3d_baseline_summary_table_20260510.tex` with an Experiment 3 table draft.
- [ ] Add a clean subsection in `paper_siga/main.tex` or a draft file first if data is still arriving.
- [ ] Move diagnostic rows to appendix/supplement.
- [ ] Compile LaTeX before claiming paper integration.

Acceptance:

- No Hunyuan old full-guide one-shot is mislabeled as mesh-space recursion.
- No selected-vs-strict row conflation.
- No unsupported effective-resolution or user-study claim.

## 11. Current Evidence Snapshot

Closed / usable:

- Trellis2 exists and has one-shot/latent-copy evidence from 20260510 outputs, but coverage must be remapped to the final 8 cases.
- Hunyuan fair text-root mesh-space baseline is closed for `tree_trunk_branch`, `pyrite_crystal_root`, and `coral_branch_root`.
- Coral mesh-space direct copy baseline exists locally as a negative control.
- Multiple strong PS-RSLG visual pools exist for vine, pine/tree, bismuth, pyrite, and coral.

Partial / not claim-safe:

- Full same-root matrix remains partial.
- Full naturalization matrix remains partial.
- Effective-resolution / zoom-retention remains proxy.
- Botanical plant-leaf/base and tree-root-leaf cases have promising runs, but not all are publication-grade.
- Hunyuan texture/paint baseline is not closed.
- TRELLIS classic/non-2 remains blocked by dependency stack.

## 12. Live Progress Log

### 2026-05-11 Initial Plan Write

- User requested full Experiment 3 closure after Trellis2 and Hunyuan baselines became ready.
- This plan created the recovery contract, method rows, shared-root protocol, initial 8-case shortlist, metric taxonomy, figure/table design, and execution tasks.
- Two local subagents were launched:
  - `experiment3_case_inventory_subagent_20260511.md`
  - `experiment3_metrics_protocol_subagent_20260511.md`
- Heartbeat should be updated to point at this file and the Experiment 3 closure goal.

### 2026-05-11 v0.2 Subagent Integration

Subagent outputs:

- Case inventory: `docs/progress/experiment3_case_inventory_subagent_20260511.md`
- Metrics protocol: `docs/progress/experiment3_metrics_protocol_subagent_20260511.md`

Updated 8-case recommendation:

1. `V25_sc_tree_crown_tapered_B` - structural SC tree crown.
2. `V25_lsys_root_fan_smooth_anchorD_stable` - topology-safe root fan.
3. `v15_lsys_climbing_vine_d6_smooth_leafy_curl` - best botanical-like row with existing baseline coverage.
4. `spider_rosette_publication_broad_20260511h` / `plant_broad_yneg_20260511i` - high-value plant/rosette row, still QA-gated.
5. `V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA` - coral/frontier non-tree row with broad baseline coverage.
6. `V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA` - pyrite/IFS row with broad baseline coverage.
7. `V21_ifs_bismuth_stepped_transform_d5_iridescent` - visually strongest terraced bismuth row, baseline-incomplete.
8. `V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA` - abstract IFS/radial row, baseline-incomplete.

Important evidence boundaries:

- Hunyuan text-root mesh-space direct rows are closed for tree trunk branch, pyrite crystal root, and coral branch root. These are fair mesh-based recursion rows because Hunyuan is used only to generate a root primitive; root copies are then produced by deterministic S/R/T mesh concat.
- Hunyuan old full recursive guide rows are one-shot/object-generation rows only, not fair mesh-space recursion rows.
- V15 vine has extensive existing baselines but the older strict vine row is weak. Do not mix "strict protocol" and "selected visual" rows without explicit labels.
- V25 tree crown, V25 root fan, bismuth, radial, and spider/plant rows need P0 baseline completion before they can appear in an 8-case claim-bearing table.
- Current effective-resolution and zoom-retention numbers remain proxy/diagnostic.

Heartbeat `r-slg-long-task-heartbeat` was updated to this Experiment 3 plan with a 30-minute fallback interval.

### 2026-05-11 07:34 CST Remote P0 Trellis2 Launch

Local scripts/files added:

- `assets/experiment3_route_manifest_normalize_20260511.py`
- `assets/experiment3_prepare_conditions_20260511.py`
- `assets/run_experiment3_trellis2_baselines_remote_20260511.sh`

Local outputs:

- `results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_master_manifest.csv`
- `results/experiment3_sparse_latent_vs_meshspace_20260511/summary.json`
- `results/experiment3_sparse_latent_vs_meshspace_20260511/conditions/condition_manifest.csv`
- per-case `root_guide.png` and `target_guide.png` for all 8 cases.

Remote sync:

- Synced Experiment 3 scripts and 3.9MB condition images to `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`.

Remote preflight:

- Remote project size: `128G`, below the 200GB cap.
- GPUs 4 and 5 were free before launch.

Launched P0 Trellis2 baselines:

- GPU 4: `trellis2_oneshot_image` from target guide for `tree_crown`, `root_fan`, `bismuth`, `radial_ornament`, `spider_rosette`.
- GPU 5: `trellis2_root_latentcopy` from root guide for the same five cases.
- Command: `bash assets/run_experiment3_trellis2_baselines_remote_20260511.sh start-p0`
- Pids: `experiment3_oneshot_p0.pid`, `experiment3_latentcopy_p0.pid`.

First health check:

- Both lanes were running.
- GPU 4 and 5 reached about 3.2GB used and 99-100% utilization during sparse-structure sampling for `tree_crown`.
- No immediate import/env failure was observed.

Next actions:

1. Monitor until both lanes finish.
2. Run remote `bash assets/run_experiment3_trellis2_baselines_remote_20260511.sh metrics`.
3. Pull Experiment 3 remote outputs/metrics locally.
4. Re-run `assets/experiment3_route_manifest_normalize_20260511.py` after adding Trellis2 metric ingestion if needed.
5. Decide whether generated-root mesh-copy rows for bismuth/radial/tree/root fan need a separate local/remote copy baseline pass from the one-shot root meshes.

### 2026-05-11 v0.3 Paper-Integrated Diagnostic Closure

Current integrated status:

- Trellis2 one-shot image-conditioned rows are available for all 8 selected cases.
- Trellis2 root trivial latent-copy rows are available for all 8 selected cases.
- Trellis2 generated-root mesh-copy rows are available for all 8 selected cases.
- Hunyuan fair text-root mesh-space rows are available for 3 representative completed cases only: `tree_crown`, `coral`, and `pyrite`. Do not describe Hunyuan as 8/8 coverage.
- PS-RSLG metric rows are present for all 8 selected cases, but `vine` and `pyrite` are labeled `proxy-positive+caveat` because raw/occupancy components are not clean enough for an unconditional selected-positive label. `spider_rosette` remains `QA-gated positive`.

Generated/updated local artifacts:

- Master manifest: `results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_master_manifest.csv`
- Compact table CSV/JSON: `results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_compact_table_20260511.csv`
- Compact table TeX: `paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`
- Main paper visual matrix: `paper_siga/figures/experiment3_sparse_latent_vs_mesh_space_matrix_20260511.png`
- Clean matrix source: `results/experiment3_sparse_latent_vs_meshspace_20260511/visual_matrix_clean/experiment3_clean_matrix_3case_hunyuan_complete_20260511.png`
- Scripts:
  - `assets/experiment3_build_table_20260511.py`
  - `assets/experiment3_compose_visual_matrix_20260511.py`
  - `assets/experiment3_render_clean_matrix_20260511.py`
  - `assets/experiment3_ps_rslg_metric_rows_20260511.py`
  - `assets/experiment3_route_manifest_normalize_20260511.py`

Paper integration:

- `paper_siga/main.tex` now contains `\subsection{Sparse-Latent Grammar versus Mesh-Space Alternatives}`.
- The subsection explicitly states that Figure 9 is a 3-case visual subset, while Table 3 is the 8-target compact diagnostic table.
- Hunyuan wording was corrected to "three representative completed targets"; it is not 8-case coverage and not a full recursive-guide one-shot failure row.
- The final explanatory sentence was downgraded: Experiment 3 now says PS-RSLG is the only row running the intended state-transition machinery, and that the component/occupancy metrics are selected proxy evidence, not standalone proof of typed-handle validity.
- The old unsupported Hunyuan-future-work wording in the older gen-3D table is no longer referenced from the main text.

Verification:

- Command run from `paper_siga`: `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`
- Result: `main.pdf` generated successfully, 51 pages, `39915104` bytes.
- Log check: no `undefined`, `Reference ... undefined`, `Citation ... undefined`, `Fatal`, or `Emergency stop` matches in the final compile log / `main.log`.
- Python `pypdf` text extraction confirmed the Experiment 3 table/caption text appears in the PDF: `Hunyuan rows are text-root representative mesh-space baselines` and `proxy-positive+caveat` appear on page 13.

Remaining claim gates:

- Classical procedural, procedural smoothing/remesh, and procedural + Trellis2 texture/PBR are still not fully expanded into the new Experiment 3 compact 8-case table. They exist elsewhere as protocol/fairness evidence, but not as closed rows in the new diagnostic table.
- Hunyuan fair mesh-space recursion is representative 3-case coverage, not 8-case coverage. Extending to plant/bismuth/radial remains P1.
- The current 3-case visual matrix is paper-usable as a diagnostic subset, but the full 8-case supplement matrix and per-case zoom panels are still needed for a publication-grade supplement.
- Effective-resolution / zoom retention remains proxy/diagnostic; do not write it as a quantitative proof.
- Runtime/peak-memory and CLIP/DINO/human preference columns remain future or supplement work unless explicitly computed.
- The current LaTeX float placement puts the Experiment 3 visual caption near page 12 and the table on page 13. It compiles cleanly but still needs human visual layout review before a polished submission draft.

Next recommended actions:

1. Produce a supplement-only 8-case matrix and at least two zoom levels for the strongest 4 cases.
2. Add or explicitly quarantine the classical/smooth/proc+texture rows in the Experiment 3 table design.
3. Extend fair Hunyuan text-root mesh-copy to at least one more botanical and one more non-tree case if remote time allows under the 2-GPU cap.
4. Add runtime/peak-memory records from remote logs and render QA status into the compact table or supplement.
5. Visually inspect `paper_siga/main.pdf` pages 12-13 and decide whether the table should be reduced, rotated, or moved to supplement with a smaller main summary.

### 2026-05-11 v0.4 Main-Case Quality Gate

User clarified that the main paper should use visually strong cases that actually support the conclusion, with bismuth crystal and tree crown explicitly preferred. The plan and table generator were updated accordingly.

Main-paper Experiment 3 subset:

- `tree_crown`
- `bismuth`
- `coral`
- `pyrite` with explicit component/occupancy caveat

Supplement/diagnostic until improved:

- `root_fan`
- `vine`
- `spider_rosette`
- `radial_ornament`

Code/documentation changes:

- `assets/experiment3_build_table_20260511.py` now writes a quality-gated main table plus a full eight-case supplement table.
- `assets/hunyuan_text_root_meshspace_baseline_20260511.py` now includes a `bismuth_crystal_root` text-root case and `bismuth_terrace` deterministic S/R/T mesh-copy grammar.
- `assets/experiment3_route_manifest_normalize_20260511.py` maps `bismuth_crystal_root` to the V21 bismuth case for manifest ingestion.
- Heartbeat `r-slg-long-task-heartbeat` now points to this Experiment 3 plan and the main-case quality gate.

Current closure status:

- The one-shell remote run on `a100-2`, `CUDA_VISIBLE_DEVICES=4`, completed the Hunyuan fair text-root mesh-space bismuth row.
- `bismuth_crystal_root` outputs were pulled locally under `results/publication_hunyuan_text_root_meshspace_20260511/bismuth_crystal_root/`.
- Hunyuan mesh-copy metrics were rebuilt locally for all four main cases so the CSV contains `tree_trunk_branch`, `bismuth_crystal_root`, `coral_branch_root`, and `pyrite_crystal_root` direct and smoothing rows.
- The quality-gated main table now has 20 rows: 4 cases x 5 methods. The main Hunyuan rows are:
  - `tree crown`: raw components `153608`, occupancy components `40`, LCR `0.998`.
  - `bismuth`: raw components `293725`, occupancy components `22`, LCR `0.999`.
  - `coral`: raw components `213465`, occupancy components `3`, LCR `0.916`.
  - `pyrite`: raw components `283875`, occupancy components `3`, LCR `0.929`.
- The main visual matrix was regenerated as `results/experiment3_sparse_latent_vs_meshspace_20260511/visual_matrix_clean/experiment3_clean_matrix_main_quality_gate_4case_20260511.png` and copied to `paper_siga/figures/experiment3_sparse_latent_vs_mesh_space_matrix_20260511.png`.
- `paper_siga/main.tex` now describes Experiment 3 as a quality-gated main subset plus broader supplementary diagnostics.
- `paper_siga/main.pdf` was recompiled successfully: 51 pages, about 39 MB; log check found no fatal errors, undefined refs, or undefined citations.

Next closure steps:

1. Produce real two-level zoom panels for the four main cases, not just the compact matrix.
2. Decide whether the full eight-case supplement table should be input into the appendix or kept as a draft artifact.
3. Integrate or explicitly quarantine `classical_proc`, `classical_smooth`, and `proc_trellis2_texture` rows in the Experiment 3 story.
4. Replace the stale teaser/hero placeholder and caption with the user-requested five-case hero combo.
5. Inspect `paper_siga/main.pdf` pages 12-13 for float layout; current build is valid but still float-heavy.
