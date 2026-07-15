# Non-tree provenance diagnosis 2026-05-10

Scope: local-only provenance for the old figure
`case_gallery_for_user_20260510_matched_selection/01_lsystem_tree_root/case_gallery_for_user_20260509__01_plants_vines_roots__visuals__non_tree_recursive_20260508__head_figure_textured_non_tree_draft_20260508.png`.
No SSH or remote commands were used. No substitute geometry was generated.

## Shared source chain

- Local figure symlink target: `visuals/non_tree_recursive_20260508/head_figure_textured_non_tree_draft_20260508.png`.
- Stage-03 local OBJ index: `visuals/non_tree_recursive_20260508/non_tree_stage03_blender_cases.txt`.
- Original remote run family, from `latest_mesh.txt`: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/siga_projected_recursive_loop_20260508_0715/<case>/stage_03/projected/<case>_stage_03/mesh_pruned.obj`.
- Generation launcher: `assets/run_projected_recursive_loop.sh`, which records `LABEL`, `ROOT_MESH`, `GRAMMAR`, `ITERS`, `FIT_SCALE`, `MAX_TOKENS`, `MIN_VERTICES`, then runs `trellis2_recursive_slat_grammar_workflow.py` and prunes each stage with `prune_mesh_components.py --keep-largest`.
- Texture export route exists for snow/scifi through `visuals/public_guide_textured_glb_20260508`, `20260509`, and `20260509b`; the old `textured_glb_previews/previews_non_tree_glb.tar.gz` contains PNG previews only, not GLB bodies.

## Cases

### Crown / ornament

- Primary case in old head figure: `crown_radial_projected_portal`.
- Local OBJ: `visuals/non_tree_recursive_20260508/meshes/crown_radial_projected_portal_stage03.obj`.
- Original remote OBJ: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/siga_projected_recursive_loop_20260508_0715/crown_radial_projected_portal/stage_03/projected/crown_radial_projected_portal_stage_03/mesh_pruned.obj`.
- Preview/render paths: `visuals/non_tree_recursive_20260508/blender_neutral/crown_portal_stage03_iso.png`, `visuals/non_tree_recursive_20260508/textured_glb_previews/crown_portal_stage03_iso.png`.
- Existing metrics from `results/mesh_metric_sweep_20260508/mesh_metrics.csv`: 314,504 vertices / 727,348 faces; mesh components 5; largest mesh component vertex ratio 0.945746; occupancy 6N components 5; largest occupancy component ratio 0.918004; occupied voxels @64 14,647.
- Visual/provenance state: best old crown candidate but fragmented; no confirmed local crown GLB body in the old batch. Human report says crown portal is the best ornament/crown non-organic case, while `crown_radial_projected_radial4` is a clear failure.
- Most likely failure cause: portal/radial transform made several support islands; stage projection/pruning preserved a dominant body but did not enforce root-connected occupancy. Texture preview can hide but not fix internal floating fragments.
- Rerun value: medium. Worth rerunning only as an ornament/negative-to-repair target, not as final proof.
- Suggested rerun: keep `portal` before `radial4`; reduce aggressive fan-out, enforce per-stage root-connected pruning and occupancy 6N single-component gate. Prefer a grammar-native connected ornament/ring scaffold over post-hoc mesh bridge.

### Snow arch / architecture

- Case: `snow_arch_projected_portal`.
- Local OBJ: `visuals/non_tree_recursive_20260508/meshes/snow_arch_projected_portal_stage03.obj`.
- Original remote OBJ: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/siga_projected_recursive_loop_20260508_0715/snow_arch_projected_portal/stage_03/projected/snow_arch_projected_portal_stage_03/mesh_pruned.obj`.
- Local extracted original: `visuals/non_tree_recursive_20260508/tar_extract_full/snow_arch_projected_portal/stage_03/projected/snow_arch_projected_portal_stage_03/mesh_pruned.obj`.
- Texture GLB routes:
  - `visuals/public_guide_textured_glb_20260508/snow_arch_projected_portal_stage03_washington_square_arch_square_steps4_xformers/textured.glb`
  - `visuals/public_guide_textured_glb_20260509/snow_arch_projected_portal_stage03_arch_steps8_tex2048_xformers/textured.glb`
  - `visuals/public_guide_textured_glb_20260509b/snow_arch_projected_portal_stage03_gear_steps8_tex2048_xformers/textured.glb`
- Texture summaries: mesh source is `/mnt/beegfs/.../selected_meshes_for_texture_20260508/snow_arch_projected_portal_stage03.obj`; 318,537 vertices / 645,682 faces; 4,757 shape/texture tokens; GLB status ok; GLB size about 27.6-28.4 MB depending batch.
- Existing metrics from OBJ sweep: mesh components 2; largest mesh component vertex ratio 0.923519; occupancy components 3; largest occupancy component ratio 0.920124; occupied voxels @64 20,369.
- Existing GLB metrics in public-guide batch: primary components 3, LCR about 0.920, box-count proxy about 2.16.
- Visual state: architecture volume is readable, but gaps/broken arch pieces are obvious; texture emphasizes broken regions.
- Most likely failure cause: `portal` duplication around an arch source left disconnected side/upper chunks; projection did not provide bridge/root path certificates. Texture guide made the semantic label stronger but did not solve support fragmentation.
- Rerun value: medium-high if architecture is needed, but use it as a rerun candidate, not final proof.
- Suggested rerun: grammar-native arch/portal with explicit left-right pier and crown-stone parent anchors, face-contact at each copied module, lower depth or stricter component pruning. Gate on `occupancy_component_count_6n=1`, LCR 1.0, and neutral front/iso render before GLB texturing.

### Scifi / mechanical

- Case: `scifi_module_projected_translate`.
- Local OBJ: `visuals/non_tree_recursive_20260508/meshes/scifi_module_projected_translate_stage03.obj`.
- Original remote OBJ: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/siga_projected_recursive_loop_20260508_0715/scifi_module_projected_translate/stage_03/projected/scifi_module_projected_translate_stage_03/mesh_pruned.obj`.
- Local extracted original: `visuals/non_tree_recursive_20260508/tar_extract_full/scifi_module_projected_translate/stage_03/projected/scifi_module_projected_translate_stage_03/mesh_pruned.obj`.
- Texture GLB routes:
  - `visuals/public_guide_textured_glb_20260508/scifi_module_projected_translate_stage03_gear_train_square_steps4_xformers/textured.glb`
  - `visuals/public_guide_textured_glb_20260509/scifi_module_projected_translate_stage03_gear_steps8_tex2048_xformers/textured.glb`
  - `visuals/public_guide_textured_glb_20260509b/scifi_module_projected_translate_stage03_pyrite_steps8_tex2048_xformers/textured.glb`
- Texture summaries: mesh source is `/mnt/beegfs/.../selected_meshes_for_texture_20260508/scifi_module_projected_translate_stage03.obj`; 453,050 vertices / 879,950 faces; 5,860 shape/texture tokens; GLB status ok; GLB size about 36.1-37.1 MB.
- Existing metrics from OBJ sweep: mesh components 1; largest mesh component vertex ratio 1.0; occupancy components 2; largest occupancy component ratio 0.999956; occupied voxels @64 22,814.
- Existing GLB/connectivity notes: public-guide GLB has nearly single support; `connectivity_repair_local_zh_20260509.md` marks both OBJ and pyrite GLB as no metric improvement needed at mesh level. Visual status docs still report yellow-green texture, holes, and broken mechanical pile appearance.
- Visual state: best topology among the three; hard-surface/mechanical semantics read, but it is not a clean hero because holes, cavities, and fractured piles remain visible.
- Most likely failure cause: `translate` makes the support almost connected, but repeated hard modules intersect/occlude unevenly and leave visual cavities; texture guide color/noise amplifies the damage. This is a visual-quality and semantic-cleanliness failure more than a gross connectivity failure.
- Rerun value: high. This is the best candidate to rescue because connectivity is already close.
- Suggested rerun: keep `translate`, add controlled overlap/contact between modules, use fewer/larger modules, graphite/steel guide rather than pyrite/yellow gear, and run neutral render QA plus occupancy single-component gate before texture. Avoid post-hoc bridge unless only used as diagnostic.

## Bottom line

- Crown portal: usable as ornament evidence only with caveats; rerun with connected ornament grammar if needed.
- Snow arch: semantically useful but currently too broken for positive proof; rerun only with parent-anchored arch grammar and strict occupancy gate.
- Scifi translate: most worth remote rerun; topology is near-good, visual/material choices are the main issue.
- Crown radial4: do not rerun as a positive route without redesign; it is a failure boundary (`occupancy LCR 0.257`, 7 occupancy components).
