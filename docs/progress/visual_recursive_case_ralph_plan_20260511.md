# Visual Recursive Case Ralph Plan 20260511

Status: active long-running visual-first loop  
Created: 2026-05-11 CST  
Local root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
Remote output target: `results/visual_recursive_cases_remote_20260511`  
GPU policy: use only GPUs `4,5,6,7`  
SSH policy for this loop: at most two SSH shells; default is one persistent shell, with one emergency/debug shell unused unless required.  
Goal: publication-grade visual recursive cases, not baseline fairness.

## Recovery Contract

After heartbeat/context compaction, read this file first, then:

1. `docs/progress/ralph_publication_closure_plan_20260510.md`
2. `docs/progress/remote_repair_loop_20260510b.md`
3. `docs/progress/root_candidate_scout_20260511.md`
4. `docs/progress/plant_leaf_recursive_remote_20260511.md`
5. newest `docs/progress/*20260511*.md`

Do not call a case publication-grade unless it has:

- remote SLat/grammar generation output from our own workflow;
- OBJ/GLB or OBJ plus controlled Blender material render;
- occupancy/component metrics;
- render QA/contact sheet;
- root/anchor/growth-frame manifest;
- visual pass: obvious recursion, no major voxelization, no mesh collapse, no distracting islands/fragments, no semantically reversed growth.

## Latest User Request Captured

The user wants high-quality visual cases for:

- crown;
- mech / mecha / mechanical structure;
- city expansion;
- castle;
- plus mechanical/hard-surface structures as needed.

These are visual showcase cases. We can relax fairness/baseline constraints and choose roots, images, prompts, generated images, and grammar variants for best aesthetics. The recursion should be very obvious and should read as semantically natural for the object family.

If a strong external mesh can be found with usable license/provenance and direct access, use it as a root. If not, use images/generated guides and the remote generator to make or refine a root, then apply our grammar. Avoid spending unbounded time on one bad root: if a root collapses after two focused grammar passes, switch to a new root/source.

## Important Orientation Note

The previous `contact_sheet_textured_white_all.png` displayed several cases in visually inverted orientations. Treat those renders as camera/material QA only, not as semantic growth-frame evidence.

For every case in this loop, record two separate notions:

- `semantic_growth_frame`: axis/sign used by sparse grammar to select root/frontier/rim/socket/rooftop anchors;
- `render_frame`: Blender transform/camera used only for final presentation.

Never infer semantic recursion direction from a possibly flipped contact sheet. Inspect mesh bounds, existing manifests, preview depths, and root semantics.

## Root / Anchor Protocol

Current method status:

- the root mesh is manually selected/authored or generated before recursion;
- grammar parameters are authored per case: growth axis/sign, grammar family, fit scale, depth, seed, max token cap;
- sparse anchor selection inside an operator is automatic from coordinates after the authored growth frame:
  - crown: rim/cap frontier or short crown buds;
  - mechanical/mecha: side sockets, hard-surface protrusion handles, mirrored/tight socket attach;
  - city: rooftop/high-mass masks, nested scale-down/rooftop buds;
  - castle: tower/keystone/battlement/top masks, attached portal/turret buds.
- paper method must state this clearly as authored sparse-latent recursive programs, not automatic root discovery.

## Case Lanes

### Lane A: Crown

Current existing roots to re-screen:

- old crown ornament root: `results/siga_non_tree_root_sweep_20260508_1440/crown_radial_ornament/trellis2_dinov3_min.obj`
- V25 structural crown root: `inputs/strict_visual_matched_cases_V25_root_sc_refine_20260510/V25_sc_tree_crown_tapered_B/V25_sc_tree_crown_tapered_B.obj`
- V25 leafshield visual crown root: `inputs/strict_visual_matched_cases_V25_root_sc_refine_20260510/V25_sc_tree_crown_leafshield_B/V25_sc_tree_crown_leafshield_B.obj`

Initial grammars:

- `ornament_rim_micro_attach`
- `ornament_bud_attach`
- `v25e_rim_leaflet_micro`
- if current roots fail visually, search external crown/tiara/ornament mesh or image guide, then generate/re-root.

Desired visual: clear circular crown/ornament with recursive rim jewels/spikes/turrets, no collapsed shell.

### Lane B: Mech / Mechanical / Hard-Surface

Current existing roots to re-screen:

- old scifi mechanical module: `results/siga_non_tree_root_sweep_20260508_1440/scifi_mechanical_module/trellis2_dinov3_min.obj`
- clean scifi module from prior repair inputs: `results/publication_repair_remote_20260510e/inputs/scifi_module_clean_recursive_v1.obj` on remote, mirrored in pulled results when available.

Initial grammars:

- `socket_tight_attach`
- `socket_translate_attach`
- new case-specific mechanical socket/tower operators may be added if the current side-socket grammar is too subtle.

Desired visual: readable hard-surface/mecha structure with repeated attached modules, ports, turrets, or armor fins; no red/dirty auto texture in final render unless it is visually strong. Prefer controlled metal material/lighting for main figures.

### Lane C: City Expansion

Current existing roots:

- `results/publication_repair_remote_20260510e/inputs/island_city_scale_down_stage03.obj` exists but was previously only diagnostic and fragmented.

Action:

- scout external/direct city block, city tile, building cluster, or generated-guide root;
- if no usable mesh appears quickly, generate/synthesize a compact city-tower root remotely or locally as input only, then run remote SLat/grammar.

Initial grammars:

- `city_rooftop_scale_attach`
- `scale_down_attach`
- likely add a `city_tower_rooftop_micro` operator if existing rooftop scaling is not visibly recursive enough.

Desired visual: unmistakable nested/recursive city: towers on rooftops, smaller city blocks atop larger blocks, or expanding city islands with attached roads/bridges. No dust-like fragments.

### Lane D: Castle

Current existing roots:

- old snow architecture root: `results/siga_non_tree_root_sweep_20260508_1440/snow_architecture/trellis2_dinov3_min.obj`
- clean arch/portal root: `results/publication_repair_remote_20260510e/inputs/architectural_arch_portal_bridge_v1.obj` on remote.

Action:

- scout direct castle/tower/fortress mesh or generate/synthesize a compact castle root if needed.

Initial grammars:

- `arch_keystone_attach`
- `portal_attach`
- likely add a `castle_turret_attach` or `battlement_micro_attach` operator if no existing grammar produces obvious castle recursion.

Desired visual: recursive towers/battlements/arches nested on larger towers, visually clean from multiple camera angles.

## Ralph Loop

For each iteration:

1. Choose or create root candidates; record provenance and semantic growth frame.
2. Run remote SLat grammar on GPUs 4-7 only with small, parallel sweeps.
3. Pull summaries, preview PNGs, OBJs, metrics.
4. Render controlled Blender material QA with white and studio backgrounds.
5. Select winners/failures:
   - winner: send to GLB/material/zoom pass;
   - near miss: one targeted grammar/root-frame change;
   - failure: document reason and switch root/source.
6. Update this progress doc or a sibling progress note with exact paths.

## Current Next Actions

1. Create this plan document and refresh heartbeat target.
2. Run local read-only scout for existing crown/mechanical/city/castle assets and prior metrics/renders.
3. Open one SSH shell to `a100-2`, check storage/GPU state, sync current workflow.
4. Search for stronger external roots. If direct mesh access is not quick, prefer generated/image-guided roots over fighting bad local meshes.
5. Prepare a `20260511j` remote sweep with:
   - crown old + V25 crown;
   - scifi old + clean mechanical module;
   - city existing root + at least one new/guided root if found;
   - castle/arch existing root + at least one castle/turret root if found.
6. Add/adjust grammar operators only where the existing operator is semantically too broad or too subtle.
7. Continue until at least one strong candidate per family has OBJ/metrics/render QA, then promote strongest cases to PBR/controlled-render GLB pass.

## Live Log

### 2026-05-11

- User clarified this loop is visual-first and specifically requested crown/mecha/mechanical/city/castle cases.
- User flagged that previous QA contact sheet orientations are reversed, which can corrupt grammar direction if treated as semantic evidence.
- This plan was created to preserve scope, constraints, root/anchor protocol, and acceptance gates.
- Heartbeat was updated to point to this plan.
- Remote audit at launch: `a100-2` project size was about `128G`, within the user-relaxed `200GB` cap; GPUs `4,5,6,7` were idle.
- Added visual-first attached sparse operators to `assets/trellis2_recursive_slat_grammar_workflow.py`:
  - `v25j_crown_rim_gem`, `v25j_crown_rim_gem_bud`;
  - `v25j_mecha_socket_fin`, `v25j_mecha_socket_tight_fin`;
  - `v25j_city_rooftop_tower`, `v25j_city_nested_scale`;
  - `v25j_castle_turret`, `v25j_castle_turret_keystone`.
- Downloaded and converted Poly Pizza candidate GLBs for visual root scouting. The first selected external roots are mirrored under `results/visual_recursive_sources_20260511/selected_roots/`; preview sheet: `results/visual_recursive_sources_20260511/poly_pizza_candidate_contact_sheet.png`.
- First selected roots:
  - crown: `poly_crown_91ea8a96.obj`, `poly_crown_e8294c9f.obj`, plus local `local_crown_ornament_attached_portal_v1.obj`;
  - mechanical: `poly_tank_item0.obj`, `poly_mecha_40d7525e.obj`, plus local `local_scifi_module_clean_recursive_v1.obj`;
  - city: `poly_city_9dbf2d34.obj`, `poly_city_b946d1a0.obj`;
  - castle: `poly_castle_18456966.obj`, `poly_castle_094ac090.obj`, plus local `local_architectural_arch_portal_bridge_v1.obj`.
- Created launcher `assets/run_visual_recursive_cases_remote_20260511j.sh`.
- Synced workflow, launcher, and selected roots to `a100-2`.
- Launched first remote SLat/grammar sweep at `2026-05-11T07:41:02+08:00`:
  - GPU 4: crown lane;
  - GPU 5: mechanical/tank/mecha lane;
  - GPU 6: city lane;
  - GPU 7: castle lane.
- Remote output root: `results/visual_recursive_cases_remote_20260511j`; root/anchor manifest: `results/visual_recursive_cases_remote_20260511j/root_anchor_manifest_20260511j.tsv`.
- First remote sweep `20260511j` completed with 70 OBJ/preview outputs and no crash/token stop.
- Selected metrics were computed for 8 rows at occupancy resolution 48:
  - `crown_poly_ring_gem_d3`: occ LCR `0.9837`, occ comps `18`;
  - `scifi_local_fin_d2`: occ LCR `0.9925`, occ comps `10`;
  - `tank_poly_fin_d2`: occ LCR `0.9988`, occ comps `3`;
  - `city_poly_block_rooftop_d3`: occ LCR `0.9951`, occ comps `12`;
  - `castle_poly_gate_turret_d3`: occ LCR `0.9987`, occ comps `4`;
  - `castle_local_arch_turret_d2`: occ LCR `0.9899`, occ comps `5`;
  - `city_poly_rooftop_d2` is not good enough metrically, occ LCR `0.6668`.
- Local selected pull:
  - metrics: `results/visual_recursive_cases_remote_20260511j_pull/metrics/visual_recursive_selected_metrics_20260511j.csv`;
  - selected raw meshes: `results/visual_recursive_cases_remote_20260511j_pull_selected/`;
  - selected contact sheet: `results/visual_recursive_cases_remote_20260511j_pull_selected/visual_selected_contact_sheet.png`;
  - Blender QA: `results/visual_recursive_cases_remote_20260511j_pull_selected/blender_qa_contact_sheet.png`;
  - pruned diagnostic render QA: `results/visual_recursive_cases_remote_20260511j_pull_selected/pruned_blender_qa_contact_sheet.png`.
- First visual interpretation:
  - `crown_poly_ring_d3` is the current strongest crown candidate; recursive beads/spikes are obvious and geometry is readable after controlled material rendering.
  - `scifi_local_fin_d2` is a usable mechanical proxy candidate; repeated socket/fins read clearly but still need lighting/material cleanup.
  - `tank_poly_fin_d2` is readable as a tank/mechanical case, but recursive detail is subtle and some side dust remains; keep as mechanical breadth candidate, not yet hero-grade.
  - city and castle first-round outputs have real shredded/mottled top geometry. Metrics are high, but visual gate fails. Pruning removes only tiny dust and does not fix semantic roughness, so this must be solved by cleaner grammar/root selection rather than postprocess.
- Added clean second-round operators:
  - `v25k_crown_clean_gem`;
  - `v25k_mecha_clean_fin`;
  - `v25k_city_clean_tower`;
  - `v25k_castle_clean_turret`.
- Created and launched `assets/run_visual_recursive_cases_remote_20260511k.sh` at `2026-05-11T08:03:53+08:00`:
  - GPU 4: cleaner crown + scifi;
  - GPU 5: shallow tank;
  - GPU 6: cleaner city;
  - GPU 7: cleaner castle/arch.
- Pulled and inspected `20260511k` selected outputs:
  - contact sheet: `results/visual_recursive_cases_remote_20260511k_pull_selected/visual_clean_contact_sheet.png`;
  - selected metrics: `results/visual_recursive_cases_remote_20260511k_pull_selected/metrics_selected_20260511k_occ48.csv`;
  - `crown_poly_clean_ypos_d02` is clean/readable and may be better than 11j depending on final material/zoom;
  - `scifi_local_clean_ypos_d02` is geometry-usable but less visually emphatic than 11j `scifi_local_fin_d2`;
  - `tank_poly_clean_zpos_d01` is readable but shallow/subtle;
  - `city_block_clean_ypos_d02`, `city_tower_clean_ypos_d01`, `castle_gate_clean_ypos_d02`, and `arch_local_clean_ypos_d02` still fail the visual gate: they are connected or nearly connected metrically but surfaces are mottled/shredded/hairy. Do not claim city/castle solved from 11j/11k.
- Pascal explorer independently confirmed the city/castle failure mode: existing detailed external roots have dirty top/corner masks, so masked attached operators copy high-frequency facade/window/top fragments. Lowering `fraction` in 11k did not solve root-mask dirt.
- Added 11l low-complexity fused root generator:
  - script: `assets/create_visual_recursive_lowpoly_roots_20260511l.py`;
  - local roots: `results/visual_recursive_lowpoly_roots_20260511l/selected_roots/`;
  - QA sheet: `results/visual_recursive_lowpoly_roots_20260511l/root_contact_sheet.png`;
  - metrics: `results/visual_recursive_lowpoly_roots_20260511l/root_metrics_occ48.csv`.
- 11l root gate:
  - all five generated roots are fused/watertight-style surfaces and have face-component LCR `1.0`;
  - `mech_socket_frame_lowpoly_v1` also has occupancy LCR `1.0`;
  - `city_block`, `city_courtyard`, and `castle_keep` have low vertex-occupancy LCR because the current occupancy metric uses vertex voxels only and undersamples broad low-poly faces; this is a root-input diagnostic caveat, not a remote result claim. Final decoded outputs must still pass normal render QA and mesh metrics.
- Added 11l narrow visual-first sparse operators in `assets/trellis2_recursive_slat_grammar_workflow.py`:
  - `v25l_city_roof_podium`;
  - `v25l_city_roof_corners`;
  - `v25l_city_podium_then_corners`;
  - `v25l_castle_turret_caps`;
  - `v25l_castle_battlement_strip`;
  - `v25l_castle_turret_then_battlement`;
  - `v25l_mecha_socket_pods`.
- Created launcher `assets/run_visual_recursive_cases_remote_20260511l.sh` and synced it with the updated workflow and fused roots to `a100-2`.
- Remote storage and GPU preflight before 11l:
  - remote project size: about `134G`, below the user-relaxed `200GB` cap;
  - GPUs 4,5,6,7 were idle.
- Launched 11l at `2026-05-11T08:37:30+08:00`:
  - GPU 4: crown/mechanical controls plus lowpoly mech;
  - GPU 5: city fused lowpoly z+/y+ growth-frame checks;
  - GPU 6: castle fused lowpoly z+/y+ growth-frame checks;
  - GPU 7: reserved for follow-up/metrics/texture pass.
- 11l acceptance remains open. Do not call any 11l case complete until remote OBJ outputs are pulled, metrics are computed, and controlled render QA passes.
- 11l completed and was pulled locally:
  - preview/summary pull: `results/visual_recursive_cases_remote_20260511l_preview_pull/`;
  - remote manifest: `results/visual_recursive_cases_remote_20260511l_preview_pull/root_anchor_manifest_20260511l.tsv`;
  - final-depth preview sheet: `results/visual_recursive_cases_remote_20260511l_preview_pull/preview_contact_sheet_final_depths.png`;
  - metrics: `results/visual_recursive_cases_remote_20260511l_preview_pull/metrics/visual_recursive_metrics_20260511l.csv` and `results/visual_recursive_cases_remote_20260511l_preview_pull/metrics/final_depth_metrics_compact_20260511l.csv`;
  - selected OBJ pull: `results/visual_recursive_cases_remote_20260511l_selected_meshes/`;
  - selected OBJ contact sheet: `results/visual_recursive_cases_remote_20260511l_selected_meshes/selected_obj_contact_sheet.png`;
  - controlled Blender material QA: `results/visual_recursive_cases_remote_20260511l_selected_meshes/blender_controlled_qa/stone_contact_sheet.png`.
- 11l metric/visual verdict:
  - `crown_clean_gem_d2`: connected and readable crown candidate, but token count did not grow beyond base (`492 -> 492`); keep as crown control/candidate, not proof of new recursive growth without zoom QA.
  - `mech_socket_pods_d2`: readable lowpoly mechanical recursion candidate; token count grew (`448 -> 504`) and occupancy LCR is `1.0`.
  - `scifi_socket_tight_d2`: visually obvious hard-surface growth but face fragmentation remains high; keep as appendix/mechanical breadth unless pruned/render QA improves.
  - `tank_clean_fin_d1`: readable but shallow, best treated as mechanical breadth rather than weapon/mecha proof.
  - `castle_gate_zpos` and `city_block_zpos`: metrics are clean but token counts remained unchanged in the main z+ rows, so the apparent detail is mostly source geometry or decoder surface change. Do not claim city/castle recursion solved from these rows.
  - `castle_keep_zpos`: token and bbox growth are real (`1776 -> 2024`; z max grows from about `0.236` to `0.298`) and controlled render is clean, but the child detail still reads like normal turret/battlement decoration rather than very obvious recursive hierarchy.
  - `city_block_podium_corners_d3` and `city_courtyard_corners_d2`: controlled renders reveal dark cut/void artifacts and weak macro recursion; fail the main visual gate.
- Root/anchor documentation gap for 11l/11m:
  - record `root_source_type`, provenance/license, root path, anchor semantics, semantic growth frame, render frame, grammar ops, selector masks, scale/lift/shift, bridge steps, seed, depth, fit scale, max tokens, token delta, bbox growth-side delta, metrics, and visual verdict for every promoted case.
  - paper-safe method wording: "We evaluate authored sparse-latent recursive programs. For each visual case, a root mesh and semantic growth frame are specified before encoding; grammar operators then select anchors automatically from sparse latent coordinates using geometric masks."
  - avoid wording that implies automatic root discovery or fully automatic semantic anchor discovery.
- Added 11m macro visual operators to `assets/trellis2_recursive_slat_grammar_workflow.py`:
  - `v25m_city_macro_stack` / `city_macro_tower_stack_20260511m`;
  - `v25m_city_quadrant_stamps` / `city_quadrant_tower_stamps_20260511m`;
  - `v25m_city_stack_then_quadrants`;
  - `v25m_castle_macro_turret_stack` / `castle_macro_turret_stack_20260511m`;
  - `v25m_castle_battlement_crown` / `castle_battlement_crown_20260511m`;
  - `v25m_castle_turret_then_crown`.
- 11m launcher: `assets/run_visual_recursive_cases_remote_20260511m.sh`.
  - It reuses the clean 11l synthetic lowpoly roots under `results/visual_recursive_lowpoly_roots_20260511l/selected_roots/`.
  - It intentionally runs only city/castle macro-repair lanes on GPUs 4,5,6,7, avoiding redundant crown/mech reruns.
  - Claim gate: first reject any row with unchanged token counts/bbox growth before visual promotion; then require metrics and controlled render QA.
- 11m planned cases:
  - GPU 4: `city_block_11m_macro_zpos`, depth 3, grammars `v25m_city_macro_stack` and `v25m_city_stack_then_quadrants`;
  - GPU 5: `city_block_11m_macro_ypos`, depth 2, grammar `v25m_city_macro_stack`; `city_courtyard_11m_quadrants_zpos`, depth 2, grammars `v25m_city_quadrant_stamps` and `v25m_city_stack_then_quadrants`;
  - GPU 6: `castle_gate_11m_macro_ypos`, depth 3, grammars `v25m_castle_macro_turret_stack` and `v25m_castle_turret_then_crown`; `castle_gate_11m_macro_zpos`, depth 2, grammar `v25m_castle_macro_turret_stack`;
  - GPU 7: `castle_keep_11m_turret_zpos`, depth 2, grammars `v25m_castle_macro_turret_stack` and `v25m_castle_turret_then_crown`; `castle_keep_11m_battlement_zpos`, depth 2, grammar `v25m_castle_battlement_crown`.
- 11m completed and was pulled locally:
  - preview/metrics: `results/visual_recursive_cases_remote_20260511m_preview_pull/`;
  - final-depth preview sheet: `results/visual_recursive_cases_remote_20260511m_preview_pull/preview_contact_sheet_final_depths.png`;
  - selected meshes: `results/visual_recursive_cases_remote_20260511m_selected_meshes/`;
  - controlled render QA: `results/visual_recursive_cases_remote_20260511m_selected_meshes/blender_controlled_qa/stone_contact_sheet.png`.
- 11m verdict: macro recursion became visible and token/bbox growth passed sanity checks, but controlled renders showed thin sheets, black artifacts, and facade-like fragments. `castle_gate_ypos_macro_turret_stack_d3` is the best diagnostic row, but not publication-grade.
- Added 11n whole-root latent-copy operators:
  - `v25n_whole_root_stack`;
  - `v25n_whole_root_twin`;
  - `v25n_whole_root_corner`;
  - `v25n_whole_root_stack_then_twin`.
- 11n completed and was pulled locally:
  - preview/summary/metrics: `results/visual_recursive_cases_remote_20260511n_preview_pull/`;
  - final-depth preview sheet: `results/visual_recursive_cases_remote_20260511n_preview_pull/preview_contact_sheet_final_depths.png`;
  - compact metrics: `results/visual_recursive_cases_remote_20260511n_preview_pull/metrics/final_depth_metrics_compact_20260511n.csv`;
  - selected depth-1 OBJ: `results/visual_recursive_cases_remote_20260511n_selected_meshes/`;
  - controlled render QA: `results/visual_recursive_cases_remote_20260511n_selected_meshes/blender_controlled_qa/stone_contact_sheet.png`.
- 11n metric/visual verdict:
  - token growth is real across city/castle whole-root rows, for example city block `1052 -> 1631/1776`, city courtyard `1240 -> 1898/1970`, castle keep `1548 -> 2516/2625/2638`;
  - occupancy LCR is often high, but face components are numerous and controlled renders reveal black holes, many small components, box-like shells, and weak city semantics;
  - conservative small-island pruning removes many components but does not fix the core visual problem;
  - keep 11n as a diagnostic/near-miss, not publication-grade evidence.
- Important 11n/11o orientation finding:
  - `trellis2_recursive_slat_grammar_workflow.py` maps input mesh vertices to SLat as `(x, y, z) -> (x, -z, y)` before encoding;
  - therefore an input z-up semantic root should use SLat `growth_axis=y`, `growth_sign=-1`;
  - earlier contact sheets and some 11l/11n rows used visually inverted/effective frames, which can make recursion look reversed;
  - a first 11o diagnostic patched the workflow to restore decoded output vertices back to input frame before writing OBJ/preview: `restore_output_frame(vertices_slat) = (x, z, -y)`;
  - controlled render QA then showed that semantic frame and presentation frame must be kept separate: the restored-frame OBJ can make the object look sideways in the current Blender camera even when bbox growth is semantic z-up;
  - workflow was adjusted again so the default keeps the decoder/render frame used by prior runs, with explicit `--restore-output-frame` available only for diagnostics. Future launchers should record `semantic_growth_frame` and `render_frame` separately rather than assuming one inverse transform solves both.
- Added 11o restored-frame visual roots:
  - script: `assets/create_visual_recursive_roots_20260511o.py`;
  - root directory: `results/visual_recursive_roots_20260511o/selected_roots/`;
  - root manifest: `results/visual_recursive_roots_20260511o/selected_roots_manifest_20260511o.csv`;
  - root QA sheet: `results/visual_recursive_roots_20260511o/root_contact_sheet.png`;
  - cases: `city_tower_cluster_socket_v2`, `city_stepped_arcology_v1`, `castle_tower_gate_socket_v2`, `castle_keep_spire_socket_v2`, `crown_spire_ring_socket_v2`, `mecha_socket_cruciform_v2`.
- Added 11o grammar/operator/launcher:
  - workflow operators: `whole_root_rooftop_child_20260511o`, `whole_root_rooftop_twins_20260511o`, `whole_root_rooftop_corner_cluster_20260511o`, `mecha_socket_cluster_20260511o`;
  - grammars: `v25o_rooftop_child`, `v25o_rooftop_twins`, `v25o_rooftop_corner_cluster`, `v25o_rooftop_child_then_twins`, `v25o_mecha_socket_cluster`;
  - launcher: `assets/run_visual_recursive_cases_remote_20260511o.sh`.
- 11o remote launch:
  - synced workflow, launcher, and roots to `a100-2`;
  - remote storage before launch: about `141G`, below the `200GB` cap;
  - GPUs 4,5,6 were idle and started at `2026-05-11T15:04:34+08:00`; GPU7 intentionally left free for metrics/follow-up;
  - remote output root: `results/visual_recursive_cases_remote_20260511o`;
  - cases use restored-frame semantic z-up via SLat `growth_axis=y`, `growth_sign=-1`.
- 11o completed and was pulled locally:
  - preview/summary/metrics: `results/visual_recursive_cases_remote_20260511o_preview_pull/`;
  - final-depth preview sheet: `results/visual_recursive_cases_remote_20260511o_preview_pull/preview_contact_sheet_final_depths.png`;
  - compact final-depth metrics: `results/visual_recursive_cases_remote_20260511o_preview_pull/metrics/final_depth_metrics_compact_20260511o.csv`;
  - selected final-depth OBJ pull: `results/visual_recursive_cases_remote_20260511o_selected_meshes/`;
  - raw controlled render QA: `results/visual_recursive_cases_remote_20260511o_selected_meshes/blender_controlled_qa/stone_contact_sheet.png`;
  - render-frame diagnostics: `results/visual_recursive_cases_remote_20260511o_selected_meshes/render_frame_diagnostics/contact_sheet.png` and `.../blender_transform_contact_sheet.png`;
  - presentation-frame candidate QA: `results/visual_recursive_cases_remote_20260511o_selected_meshes/presentation_candidates_rot_x_neg90/presentation_stone_contact_sheet.png`.
- 11o metric/visual verdict:
  - direction issue is mostly closed for the semantic growth frame: z-up roots should use SLat `y -1`, and bbox max-z grows clearly for the best rows.
  - `city_arcology_rooftop_yneg_11o/v25o_rooftop_child/depth_02` is the cleanest city candidate so far: tokens `1152 -> 1332`, bbox max-z delta about `0.213`, occupancy LCR `1.0`, face LCR `0.985`, controlled presentation render is readable but the child tower top is still a little noisy.
  - `city_cluster_rooftop_yneg_11o/v25o_rooftop_child/depth_02` is visually more obviously recursive in the presentation render, but metrics are weaker: face LCR `0.874`, occ LCR `0.993`, fragmentation score `0.126`.
  - `castle_keep_rooftop_yneg_11o/v25o_rooftop_child/depth_02` is the best castle candidate: tokens `1812 -> 2064`, bbox max-z delta about `0.234`, occ LCR `1.0`, face LCR `0.923`; visual is readable but top child still has holes/sparse fragments.
  - `castle_keep_twins` and `castle_keep_corner` show stronger recursion but more top fragmentation; keep as diagnostics, not main figures.
  - crown ring and mecha socket 11o are not main winners: crown fragments badly in metrics/QA; mecha is readable but not yet a strong mecha/mechanical hero.
  - The current candidates are useful near-misses and may be appendix/iteration evidence, but should not yet be called publication-grade final because the child modules still show missing/black/sparse areas under controlled render.
- 11p target:
  - keep `semantic_growth_frame` as SLat `y -1` for z-up roots;
  - keep presentation-frame render transform explicit, currently `rot_x_neg90_then_center_floor` for the best 11o candidates;
  - reduce child/source complexity and top child gaps for `city_arcology_child`, `city_cluster_child`, and `castle_keep_child`;
  - prefer a single coherent child/tower over twins/corner clusters unless the latter can pass controlled render without fragmenting.
- 11o depth-1 follow-up:
  - pulled selected depth-1 OBJs to `results/visual_recursive_cases_remote_20260511o_depth1_candidates/`;
  - presentation QA: `results/visual_recursive_cases_remote_20260511o_depth1_candidates/presentation_rot_x_neg90/depth1_presentation_stone_contact_sheet.png`;
  - pruned large-component diagnostic: `results/visual_recursive_cases_remote_20260511o_depth1_candidates/presentation_rot_x_neg90/pruned_keep_large/pruned_depth1_stone_contact_sheet.png`;
  - surface repair diagnostic: `results/visual_recursive_cases_remote_20260511o_depth1_candidates/presentation_rot_x_neg90/pruned_keep_large/surface_repair_fill_smooth/surface_repair_stone_contact_sheet.png`.
  - depth-1 is cleaner than depth-2. `city_cluster_child_d1` is the most visually recursive, `city_arcology_child_d1` is cleanest but less emphatic, and `castle_keep_child_d1` is readable but still has top holes.
- Added 11p single-child support grammar:
  - workflow operators: `whole_root_rooftop_child_with_support_20260511p`, `whole_root_rooftop_child_tight_20260511p`, `whole_root_rooftop_child_readable_20260511p`;
  - grammars: `v25p_rooftop_child_tight`, `v25p_rooftop_child_readable`;
  - launcher: `assets/run_visual_recursive_cases_remote_20260511p.sh`;
  - launch time: `2026-05-11T19:11:16+08:00` on `a100-2`, GPUs 4,5,6 for city cluster / city arcology / castle keep respectively;
  - output root: `results/visual_recursive_cases_remote_20260511p`;
  - claim gate remains open until preview/metrics/selected OBJ/control render QA are pulled and inspected.
- 11p completed, was pulled, and received local presentation/QA at `2026-05-11 20:00 CST`:
  - remote storage at audit time: about `144G`, still below the user-relaxed `200GB` cap;
  - GPUs 4,5,6,7 were idle after the run;
  - preview/metrics/log pull: `results/visual_recursive_cases_remote_20260511p_preview_pull/`;
  - selected depth-1 OBJ pull: `results/visual_recursive_cases_remote_20260511p_selected_meshes/`;
  - audited presentation transform helper added: `assets/apply_mesh_presentation_transform.py`;
  - main presentation-frame OBJ/manifest/case file: `results/visual_recursive_cases_remote_20260511p_selected_meshes/presentation_rot_x_neg90/`;
  - quick mesh QA: `results/visual_recursive_cases_remote_20260511p_selected_meshes/presentation_rot_x_neg90/quick_mesh_contact_sheet.png`;
  - controlled Blender QA: `results/visual_recursive_cases_remote_20260511p_selected_meshes/presentation_rot_x_neg90/blender_qa_stone_contact_sheet.png`;
  - compact metrics: `results/visual_recursive_cases_remote_20260511p_selected_meshes/presentation_rot_x_neg90/compact_metrics_20260511p.csv`;
  - frame diagnostic: `results/visual_recursive_cases_remote_20260511p_selected_meshes/render_frame_diagnostics/frame_diagnostic_quick_contact_sheet.png`;
  - conservative prune diagnostic: `results/visual_recursive_cases_remote_20260511p_selected_meshes/presentation_rot_x_neg90/pruned_keep_large/pruned_quick_mesh_contact_sheet.png`.
- 11p metric verdict:
  - `city_cluster_11p_supported_child/v25p_rooftop_child_tight/depth_01`: occ LCR `1.0`, vertex LCR `0.9978`, fragmentation `0.0022`, faces `578752`.
  - `city_cluster_11p_supported_child/v25p_rooftop_child_readable/depth_01`: occ LCR `1.0`, vertex LCR `0.9976`, fragmentation `0.0024`, faces `598604`.
  - `city_arcology_11p_supported_child/v25p_rooftop_child_tight/depth_01`: occ LCR `0.9999`, vertex LCR `0.9976`, fragmentation `0.0024`, faces `589328`.
  - `city_arcology_11p_supported_child/v25p_rooftop_child_readable/depth_01`: occ LCR `1.0`, vertex LCR `0.9847`, fragmentation `0.0153`.
  - `castle_keep_11p_supported_child` remains weaker: tight fragmentation `0.0478`, readable fragmentation `0.0516`; face components remain high.
- 11p visual verdict:
  - `rot_x_neg90_then_center_floor` is still the best presentation transform; the frame diagnostic shows the child can read as a vertical/top hierarchy in the quick mesh view.
  - The controlled Blender sheet at the default camera made some children read like front/side grafts, so camera/view choice matters and must be recorded separately from semantic growth.
  - Conservative pruning improves small-island dust but does not solve the top-child surface: city rows still have granular/missing top details, and castle rows still show holes/fragments.
  - Current strongest visual candidates are `city_cluster_11p_tight_d1` and `city_cluster_11p_readable_d1` as near-main candidates after better camera/material/possibly one more grammar pass; `city_arcology_11p_tight_d1` is cleaner but less obviously recursive; `castle_keep_11p_tight_d1` is still only a near-miss/diagnostic.
  - Do not label 11p city/castle as publication-grade final yet. It is a substantial metric/orientation improvement over 11o, but still needs a narrow 11q or equivalent controlled rendering/root-grammar pass before promotion.
- 11q target:
  - keep semantic growth frame as SLat `y -1` for z-up roots and preserve the explicit render-frame transform contract;
  - make the child a simpler vertical tower/spire mass with less copied facade/interior detail, a wider support/plinth, and fewer top high-frequency fragments;
  - prefer one or two rows only: `city_cluster` first, `castle_keep` second; `city_arcology` only as a clean fallback;
  - verify with remote OBJ, metrics, `rot_x_neg90_then_center_floor` presentation QA, controlled Blender white-background QA, and conservative-prune diagnostic before any promotion.
- 11q bottom-aligned stack executed and QAed:
  - workflow additions: `whole_root_rooftop_child_aligned_20260511q`, `whole_root_city_rooftop_stack_aligned_20260511q`, `whole_root_castle_rooftop_stack_aligned_20260511q`;
  - launcher: `assets/run_visual_recursive_cases_remote_20260511q.sh`;
  - remote launch: `2026-05-11T20:08:22+08:00`; GPUs 4/5/6; GPU7 stayed free;
  - remote output: `results/visual_recursive_cases_remote_20260511q`;
  - local preview/metric pull: `results/visual_recursive_cases_remote_20260511q_preview_pull/`;
  - local selected meshes: `results/visual_recursive_cases_remote_20260511q_selected_meshes/`;
  - presentation QA: `results/visual_recursive_cases_remote_20260511q_selected_meshes/presentation_rot_x_neg90/quick_mesh_contact_sheet.png`;
  - Blender QA: `results/visual_recursive_cases_remote_20260511q_selected_meshes/presentation_rot_x_neg90/blender_qa_stone_contact_sheet.png`;
  - compact metrics: `results/visual_recursive_cases_remote_20260511q_selected_meshes/presentation_rot_x_neg90/compact_metrics_20260511q.csv`.
- 11q verdict:
  - `city_cluster_11q_aligned_stack/depth_02` is the best metric row of 11q: occ LCR `0.9999`, vertex LCR `0.9960`, fragmentation `0.0040`, faces `506260`.
  - In quick mesh view, city cluster d1/d2 reads more like vertical tower-on-tower than 11p.
  - In controlled Blender view, however, the child still reads as a front/side block rather than a clearly protruding rooftop child. BBox height barely changes for city cluster (`z` extent stays about `0.3245`), so the bottom-align rule placed the child too far inside the roof band.
  - `city_arcology_11q_aligned_stack/depth_02` is not usable: occ LCR drops to `0.8780` and fragmentation rises to `0.1024`.
  - `castle_keep_11q_aligned_stack/depth_02` remains near-miss only: fragmentation about `0.0503`, visible top noise/holes remain.
  - Do not promote 11q as publication-grade. Keep it as evidence that support/bottom alignment helps frame readability but is insufficient.
- 11r target:
  - keep city cluster only for the first narrow repair, with optional castle backup after the city result;
  - use a top-protruding child transform: align child bottom near roof band but add a positive protrusion offset so the child stands above the parent in the presentation frame, not embedded in the facade/roof mass;
  - reduce child scale further (`0.22-0.24`) and use a wider plinth/support bridge so the top module is simple, readable, and attached;
  - run depth `2` for city cluster only first; require bbox growth, controlled Blender QA, metrics, and optional pruning before any promotion.
- 11r completed and was locally QAed:
  - remote output: `results/visual_recursive_cases_remote_20260511r`;
  - preview/metrics/log pull: `results/visual_recursive_cases_remote_20260511r_preview_pull/`;
  - selected meshes and presentation transform: `results/visual_recursive_cases_remote_20260511r_selected_meshes/presentation_rot_x_neg90/`;
  - quick mesh QA: `results/visual_recursive_cases_remote_20260511r_selected_meshes/presentation_rot_x_neg90/quick_mesh_contact_sheet.png`;
  - controlled Blender QA: `results/visual_recursive_cases_remote_20260511r_selected_meshes/presentation_rot_x_neg90/blender_qa_stone_contact_sheet.png`;
  - metrics: `results/visual_recursive_cases_remote_20260511r_preview_pull/metrics/visual_recursive_metrics_20260511r.csv`.
- 11r verdict:
  - metrics show real protrusion but worse fragmentation than 11q: depth 2 occ LCR about `0.9908`, vertex LCR about `0.9833`, fragmentation about `0.0167`, and SLat/presentation height extent grows in the intended direction;
  - quick mesh QA reads more like an upward tower-on-tower hierarchy than 11p/11q;
  - controlled Blender QA still reads as a front/side graft with black holes and sparse detached sheet fragments, especially in side view;
  - freeze `city_cluster_11r_protruding_stack` as diagnostic evidence. Do not keep tuning the same `city_tower_cluster_socket_v2` root as the main path.
- 11s cross-family pivot:
  - launcher: `assets/run_visual_recursive_cases_remote_20260511s.sh`;
  - workflow additions: `v25s_city_topbody_protruding`, `v25s_castle_cap_pair_protruding`, `v25s_mecha_socket_pods_emphatic`;
  - use semantic SLat frame `growth_axis=y`, `growth_sign=-1` for all z-up authored roots and keep render frame as `rot_x_neg90_then_center_floor`;
  - roots/cases:
    - `city_arcology_11s_topbody_protrude`: `results/visual_recursive_roots_20260511o/selected_roots/city_stepped_arcology_v1.obj`, depth 2;
    - `city_courtyard_11s_topbody_protrude`: `results/visual_recursive_lowpoly_roots_20260511l/selected_roots/city_courtyard_tower_anchor_v1.obj`, depth 2;
    - `castle_gate_11s_cap_pair_protrude`: `results/visual_recursive_roots_20260511o/selected_roots/castle_tower_gate_socket_v2.obj`, depth 2;
    - `castle_keep_11s_cap_pair_protrude`: `results/visual_recursive_roots_20260511o/selected_roots/castle_keep_spire_socket_v2.obj`, depth 1;
    - `mech_frame_11s_socket_pods`: `results/visual_recursive_lowpoly_roots_20260511l/selected_roots/mech_socket_frame_lowpoly_v1.obj`, depth 2;
    - `mecha_cruciform_11s_socket_pods`: `results/visual_recursive_roots_20260511o/selected_roots/mecha_socket_cruciform_v2.obj`, depth 2.
  - GPU plan: run city on GPU 4, castle on GPU 5, mechanical on GPU 6, leave GPU 7 open for metrics/QA or one emergency fallback.
  - claim gate: promote only after remote OBJ, metrics, presentation transform, controlled Blender QA, and visual pass. City/castle must show a visible top/protruding hierarchy without black holes/sheet fragments; mechanical must show attached lateral socket growth without dust-like islands.
- 11s completed and was locally QAed:
  - remote launch: `2026-05-11T21:11:29+08:00`; lanes ran on GPUs 4/5/6, GPU 7 reserved;
  - remote output: `results/visual_recursive_cases_remote_20260511s`;
  - remote storage after pull/QA audit: about `145G`, below the user-relaxed `200GB` cap; GPUs 4/5/6/7 idle;
  - preview/summary/metrics pull: `results/visual_recursive_cases_remote_20260511s_preview_pull/`;
  - selected raw meshes: `results/visual_recursive_cases_remote_20260511s_selected_meshes/`;
  - selected presentation meshes: `results/visual_recursive_cases_remote_20260511s_selected_meshes/presentation_rot_x_neg90/`;
  - quick mesh QA: `results/visual_recursive_cases_remote_20260511s_selected_meshes/presentation_rot_x_neg90/quick_mesh_contact_sheet.png`;
  - controlled stone QA: `results/visual_recursive_cases_remote_20260511s_selected_meshes/presentation_rot_x_neg90/blender_qa_stone_contact_sheet.png`;
  - controlled metal QA for mechanical rows: `results/visual_recursive_cases_remote_20260511s_selected_meshes/presentation_rot_x_neg90/blender_qa_metal_contact_sheet.png`;
  - token deltas: `results/visual_recursive_cases_remote_20260511s_selected_meshes/summary_token_deltas_20260511s.csv`;
  - compact metrics: `results/visual_recursive_cases_remote_20260511s_selected_meshes/compact_selected_metrics_20260511s.csv` and `results/visual_recursive_cases_remote_20260511s_selected_meshes/presentation_rot_x_neg90/compact_metrics_20260511s.csv`.
- 11s metric/visual verdict:
  - all six remote cases completed with OBJ/preview outputs and no crash;
  - token growth is real but modest for city/castle: city arcology `1152 -> 1200`, city courtyard `1288 -> 1322`, castle gate `872 -> 988`, castle keep `1701 -> 1798`;
  - `city_arcology_11s_topbody_protrude` has good metrics after presentation transform (occ LCR about `0.9987`, fragmentation about `0.0050`) and a cleaner front/side profile than 11r, but controlled render still reads as a side/front module rather than a paper-ready rooftop hierarchy;
  - `city_courtyard_11s_topbody_protrude` fails the main metric/visual gate: occ LCR about `0.951`, fragmentation about `0.041`, and the child still reads as a front protrusion;
  - `castle_gate_11s_cap_pair_protrude` has clean occupancy (about `0.9993`) and visible cap growth in quick view, but controlled render shows horizontal/side growth plus shredded cap ends; keep as diagnostic;
  - `castle_keep_11s_cap_pair_protrude` is similarly not promotable: occupancy is high, but cap/turret ends remain fragmented and the presentation reads sideward;
  - `mech_frame_11s_socket_pods_l` and `mech_frame_11s_socket_pods_s` are the best 11s visual candidates: token delta `+56`, occ LCR `1.0`, fragmentation about `0.0051-0.0055`, controlled metal render has readable symmetric hard-surface socket modules with limited dust. Treat as near-main mechanical candidate after one cleanup/material pass;
  - `mecha_cruciform_11s_socket_pods_*` should remain diagnostic: occupancy LCR is high, but face LCR is only about `0.545-0.556`, so the root/decoder segmentation is not paper-safe.
- 11s next action:
  - promote only the mech-frame branch to a PBR/lighting cleanup candidate;
  - for city/castle, the sparse-latent semantic frame may be correct but the presentation/camera still exposes side-grafting. Next city/castle pass should either use authored roots whose visible top plane is aligned with the current render frame, or add a render-frame-aware root transform before SLat encoding rather than applying only post-hoc presentation rotation;
  - do not call any 11s city/castle result publication-grade. The best city/castle rows are useful evidence for the anchor/protrusion search, not final figures.
- 11t/11u continuation status:
  - 11t tested `--preencode-transform rot_x_neg90`; it improved top-frame legibility but controlled Blender QA still exposed black holes, shell gaps, and shredded top/cap modules.
  - 11u replaced the roots/operators with low-frequency solid city/castle roots and a clean single-child rooftop grammar. Remote 11u completed on `a100-2` with GLB/OBJ-equivalent OBJ outputs, metrics, and local Blender 5.1.1 controlled QA.
  - 11u QA paths:
    - preview/metrics: `results/visual_recursive_cases_remote_20260511u_preview_pull/`;
    - raw selected OBJ: `results/visual_recursive_cases_remote_20260511u_selected_meshes/raw_selected/`;
    - identity presentation QA: `results/visual_recursive_cases_remote_20260511u_selected_meshes/identity_center_floor/blender_qa_stone_white_contact_sheet.png`;
    - `rot_x_neg90_then_center_floor` presentation QA: `results/visual_recursive_cases_remote_20260511u_selected_meshes/rot_x_neg90_then_center_floor/blender_qa_stone_white_contact_sheet.png`;
    - detailed 11u plan/verdict: `docs/progress/visual_recursive_case_11u_execution_plan_20260511.md`.
  - 11u best metric rows are clean by occupancy proxy: `city_solid_keep_clean_d2` has occ LCR about `0.9951`, fragmentation about `0.0034`; `castle_solid_keep_clean_d2` has occ LCR `1.0`, fragmentation about `0.0011`.
  - 11u visual verdict is still negative for publication: the main bodies are cleaner, but the recursive caps/children still show black holes, shell breaks, thin floating fragments, and in identity frame still read as front/side grafts. Do not promote city/castle as solved from 11u.
  - Next city/castle pivot should change root/source and anchor construction, not just presentation transform or child scale. Author explicit top anchors/support plinths before SLat encoding, or choose a simpler external/generated topologically solid root.
- 2026-05-12 heartbeat continuation:
  - Added the 11v pivot execution contract: `docs/progress/visual_recursive_case_11v_execution_plan_20260512.md`.
  - 11v is explicitly a root/source and top-anchor/support-plinth pivot after 11r/11t/11u diagnostics, not another presentation-frame or child-scale tuning pass.
  - No remote job was launched during this heartbeat; next real work should first choose or author simpler topologically solid city/castle/mechanical roots with visible top anchors, then run a narrow remote batch and controlled Blender QA.
