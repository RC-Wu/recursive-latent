# Tree Root Leaf Source Trace - 2026-05-11

Scope: trace the hero `tree_root_leaf` lineage around:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/hero_botanical_variants_20260510/tree_compete_s3_green_leaf_brown_root.glb`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_matched_root_stamped_20260510/lsys_pine_canopy_d5__rootstamped_tree_compete/root_stamped_candidate.glb`

No code was modified and no remote job was launched.

## Lineage

### Hero botanical presentation GLB

Path:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/hero_botanical_variants_20260510/tree_compete_s3_green_leaf_brown_root.glb`

Manifest:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/hero_botanical_variants_20260510/hero_botanical_variants_manifest_20260510.json`

Source GLB:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/textured_glb_20260508/tree_compete_s3/textured.glb`

Remote source OBJ recorded by the source summary:

`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/siga_projected_recursive_loop_20260508_0715/tree_projected_compete/stage_03/projected/tree_projected_compete_stage_03/mesh_pruned.obj`

Source summary:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/textured_glb_20260508/tree_compete_s3/summary.json`

Important source summary values:

- `kind`: `trellis2_mesh_texturing_export_glb`
- `image`: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/inputs/trellis_example_images_subset/04_130c2b18f1651a70f8aa15b2c99f8dba29bb943044d92871f9223bd3e989e8b1.webp`
- `mesh_vertices`: `277556`
- `mesh_faces`: `575342`
- `shape_slat_tokens`: `3126`
- `tex_slat_tokens`: `3126`
- `pbr_voxel_tokens`: `778755`
- `steps`: `2`
- `texture_size`: `512`
- `glb_bytes`: `27588820`

The hero GLB is not a new TRELLIS2 generation. It is a deterministic Blender postprocess of `tree_compete_s3/textured.glb`.

Existing script:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/scripts/figures/prepare_hero_botanical_variants_20260510.py`

Relevant behavior:

- Imports and joins `TREE_SOURCE = visuals/textured_glb_20260508/tree_compete_s3/textured.glb`.
- Assigns materials by local vertex/face height.
- Applies weighted normals.
- Exports the selected joined object as the hero botanical variant.

Recorded split:

- `min_z`: `-0.48869943618774414`
- `max_z`: `0.48869943618774414`
- `split_z`: `-0.03909595489501949`
- `low_faces`: `226776`
- `middle_faces`: `96029`
- `high_faces`: `252537`

Material groups in the hero GLB:

- `brown_root_and_trunk_pbr`: lower/root/trunk region, material index 0
- `olive_transition_branch_pbr`: middle transition branch band, material index 1
- `deep_green_leaf_pbr`: upper/crown/leaf region, material index 2

GLB structure:

- One mesh: `tree_compete_s3_green_leaf_brown_root_mesh`
- Three primitives, one per material group
- One node: `tree_compete_s3_green_leaf_brown_root`

This file is a useful visual source for root/branch/leaf appearance, but the root/leaf separation is a height-split color cut, not a semantic mesh-part extraction.

### Root-stamped L-system pine/tree candidate

Path:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_matched_root_stamped_20260510/lsys_pine_canopy_d5__rootstamped_tree_compete/root_stamped_candidate.glb`

Metadata:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_matched_root_stamped_20260510/lsys_pine_canopy_d5__rootstamped_tree_compete/metadata.json`

Plan:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_matched_root_stamped_20260510/anchor_plan.json`

Manifest:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_matched_root_stamped_20260510/manifest.json`

Root asset stamped into candidate:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/textured_glb_20260508/tree_compete_s3/textured.glb`

Controls:

- `matched_traditional_case`: `lsys_pine_canopy_d5`
- `family`: `L-system`
- `target_category`: `pine/tree canopy`
- `recursive_mode`: `symbolic turtle branch rewriting; same branch depth and branching family as traditional target`
- `depth`: `5`
- `seed`: `20260510`
- `branch_source`: `baseline_matrix_20260509.lsystem_case(tree)`
- `material_preset`: `bark_leaf`
- `edges`: `121`
- `anchors`: `26`
- `token_instances`: `18`

Existing scripts:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/strict_matched_root_stamped_plan_20260510.py`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/strict_matched_root_stamped_blender_20260510.py`

Relevant behavior:

- `strict_matched_root_stamped_plan_20260510.py` builds the L-system tree skeleton from `baseline_matrix_20260509.lsystem_case("tree", depth=5, seed=20260510)`, computes terminal-tip and junction anchors, and assigns `tree_compete_s3/textured.glb` as a `leafy_tree_token`.
- `strict_matched_root_stamped_blender_20260510.py` creates tapered support-edge frustums, accent bulbs, imports the root asset, hides the source, then duplicates root-token mesh objects at anchors with rotation and scale.

Material/object groups in the root-stamped GLB:

- Procedural support edges: material name `warm_branch_bark`, used by `lsys_pine_canopy_d5__rootstamped_tree_compete_edge_####` meshes.
- Procedural anchor accents: material name `leaf_accent`, used by accent spheres.
- Imported token instances: `Material_0`, textured, inherited from `tree_compete_s3/textured.glb`.

GLB structure:

- `148` meshes / `148` primitives.
- First `121` meshes are support edges.
- Additional meshes are anchor accents and imported `tree_compete_s3` token instances.

This is a usable screening candidate for tree-root/tree-leaf semantics, but it is a root-stamped composition rather than a clean root/branch/leaf module extraction. It is also medium risk for a final figure because previous notes flag it as more "root-stamped tree canopy" than pure root/leaf close-up.

## Existing cuts and extractions

Found existing cut/postprocess scripts:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/scripts/figures/prepare_hero_botanical_variants_20260510.py`
  - Height-split recolor for `tree_compete_s3_green_leaf_brown_root`.
  - Similar base/leaf height split for the vine botanical variant.
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/strict_matched_root_stamped_plan_20260510.py`
  - Anchor plan, support graph, root-token selection, material preset.
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/strict_matched_root_stamped_blender_20260510.py`
  - Materializes root-stamped GLBs.

I did not find an existing semantic extractor that writes separate root OBJ, branch OBJ, and leaf OBJ modules from `tree_compete_s3_green_leaf_brown_root.glb`. The only existing separation is material/height based in Blender. Therefore, for module selection, prefer already generated strict OBJ modules whose construction records root/leaf counts and attachment rules, rather than trying to infer leaf geometry from the hero presentation GLB.

## Usable Source Components

### Visual/source-token components

Primary tree token:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/textured_glb_20260508/tree_compete_s3/textured.glb`

Pros:

- Proven TRELLIS2 textured export.
- Strong botanical/root/crown visual token.
- Already used by both hero botanical variant and root-stamped candidate.

Cons:

- Single textured primitive in the original GLB; no semantic material split.
- Hero root/leaf split is a presentation recolor, not a true source-part extraction.

Presentation split:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/hero_botanical_variants_20260510/tree_compete_s3_green_leaf_brown_root.glb`

Use only as a visual guide or Blender-side material reference, not as the clean recursive source geometry for SLat recursion.

### Procedural/root-branch modules

Best branch/root module for SLat recursion:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles/V23_lsys_pine_canopy_d5_multi_root_smooth_needles.obj`

Metadata:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles/V23_lsys_pine_canopy_d5_multi_root_smooth_needles_metadata.json`

Textured GLB:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_visual_matched_texture_V23_all_family_seed20260512_20260510/V23_lsys_pine_canopy_d5_multi_root_smooth_needles_steps8_tex2048_seed20262812_xformers/textured.glb`

Why this is the recommended branch/root module:

- It directly matches `lsys_pine_canopy_d5`.
- It records `recursive_depth=5`, `support_edge_count=121`, `shared_vertex_anchor_count=122`, `needle_count=158`, `leaf_count=18`, and `connected_support=true`.
- It is much cleaner as a recursive module than the root-stamped GLB because it is a single generated input OBJ with explicit connected support and semantic details.
- Textured export succeeded: `mesh_vertices=7310`, `mesh_faces=14444`, `shape_slat_tokens=888`, `tex_slat_tokens=888`, `pbr_voxel_tokens=363274`.

Fallback branch/tree module if the desired target is space-colonization crown rather than L-system pine:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_sc_tree_crown_260_attractor_leaf_shell/V23_sc_tree_crown_260_attractor_leaf_shell.obj`

Textured GLB:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_visual_matched_texture_V23_all_family_seed20260512_20260510/V23_sc_tree_crown_260_attractor_leaf_shell_steps8_tex2048_seed20262816_xformers/textured.glb`

Cleaner SC-crown refinement candidate:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_cases_V25_root_sc_refine_20260510_dryrun/V25_sc_tree_crown_leafshield_A/V25_sc_tree_crown_leafshield_A.obj`

Textured GLB:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_visual_matched_texture_V25_root_sc_refine_20260510/V25_sc_tree_crown_leafshield_A_steps8_tex2048_seed20285523_xformers/textured.glb`

Use this only if the remote recursion target is explicitly SC tree-crown, because its recursive mode is attractor competition rather than L-system rewriting.

### Leaf module candidates

Recommended leaf module for the tree-root-leaf case:

Use the attached semantic leaf/needle details inside:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles/V23_lsys_pine_canopy_d5_multi_root_smooth_needles.obj`

Reason:

- Its metadata explicitly records `needle_count=158` and `leaf_count=18`.
- The details are shared-vertex attached to the swept support, which is safer for SLat recursion than detaching a leaf cut from a GLB.
- It stays in the same `lsys_pine_canopy_d5` recursive mode as the root/branch support.

Leaf-shell alternative for broader deciduous/crown look:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_sc_tree_crown_260_attractor_leaf_shell/V23_sc_tree_crown_260_attractor_leaf_shell.obj`

Use only if the desired visual is a crown leaf shell rather than conifer needles.

Avoid as primary leaf module:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/hero_botanical_variants_20260510/tree_compete_s3_green_leaf_brown_root.glb`

Reason: it has a clear `deep_green_leaf_pbr` material group, but that group is produced by a height split and is not guaranteed to be a connected, reusable semantic leaf component.

## Recommendation for Remote TRELLIS2 SLat Recursion

Use a two-tier strategy:

1. Primary L-system pine/tree-root-leaf recursion
   - Root/branch source OBJ:
     `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles/V23_lsys_pine_canopy_d5_multi_root_smooth_needles.obj`
   - Leaf source:
     the same OBJ's attached leaf/needle semantic details, not a separately cut GLB part.
   - Visual/PBR reference:
     `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/hero_botanical_variants_20260510/tree_compete_s3_green_leaf_brown_root.glb`
     and
     `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_visual_matched_texture_V23_all_family_seed20260512_20260510/V23_lsys_pine_canopy_d5_multi_root_smooth_needles_steps8_tex2048_seed20262812_xformers/textured.glb`
   - Rationale:
     best match to `lsys_pine_canopy_d5`, small enough for module experimentation, explicit connected support and attached semantic details, existing successful TRELLIS2 textured export.

2. SC crown backup if the goal is a more leafy canopy than pine needles
   - Root/branch/leaf source OBJ:
     `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_sc_tree_crown_260_attractor_leaf_shell/V23_sc_tree_crown_260_attractor_leaf_shell.obj`
   - Stronger refinement candidate:
     `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_cases_V25_root_sc_refine_20260510_dryrun/V25_sc_tree_crown_leafshield_A/V25_sc_tree_crown_leafshield_A.obj`
   - Rationale:
     better leaf-shell semantics, but different recursive mode from L-system pine.

Do not use the root-stamped GLB as the primary SLat recursion input. It is valuable as proof of source provenance and visual screen, but its structure is many duplicated token objects plus procedural support edges. For recursion, the V23/V25 input OBJs are cleaner and encode the recursive module before texture/export.

## Exact Path Shortlist

Hero presentation:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/hero_botanical_variants_20260510/tree_compete_s3_green_leaf_brown_root.glb`

Original tree token:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/textured_glb_20260508/tree_compete_s3/textured.glb`

Root-stamped screening candidate:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_matched_root_stamped_20260510/lsys_pine_canopy_d5__rootstamped_tree_compete/root_stamped_candidate.glb`

Primary SLat recursion OBJ:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles/V23_lsys_pine_canopy_d5_multi_root_smooth_needles.obj`

Primary SLat recursion metadata:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles/V23_lsys_pine_canopy_d5_multi_root_smooth_needles_metadata.json`

Primary textured reference:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_visual_matched_texture_V23_all_family_seed20260512_20260510/V23_lsys_pine_canopy_d5_multi_root_smooth_needles_steps8_tex2048_seed20262812_xformers/textured.glb`

SC leaf-shell backup OBJ:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_sc_tree_crown_260_attractor_leaf_shell/V23_sc_tree_crown_260_attractor_leaf_shell.obj`

SC leafshield backup OBJ:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_cases_V25_root_sc_refine_20260510_dryrun/V25_sc_tree_crown_leafshield_A/V25_sc_tree_crown_leafshield_A.obj`

