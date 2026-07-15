# Visual Result Matrix and Render Protocol - 2026-05-08

This document is the visual-asset execution protocol for the next 30+ result display, head figure, and demo video pass. It is intentionally a local visual/rendering branch: do not modify the main Trellis2 texturing script while it is running, and do not start heavy GPU jobs from this checklist.

## Current Read

The project has moved past point-cloud previews. The strongest presentable line is mesh-first recursive growth:

```text
root mesh -> O-Voxel/FDG -> shape SLAT encode
-> recursive sparse grammar
-> shape SLAT decode to mesh
-> projection/pruning per depth
-> final OBJ
-> optional Trellis2 texture latent / GLB export
-> Blender/Cycles render
```

Local visual root:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals`

Current local render helper:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/blender_render_recursive_mesh.py`

Current local Blender outputs:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/paper_quality_renders_20260508/blender_tiles/`

Existing textured/GLB status:

- No local `.glb` was found under `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`.
- Texture latent/PBR voxel compatibility is confirmed for selected OBJ cases, but the present local artifacts are summaries and pipeline metadata, not paper-ready textured renders.
- Remote notes record the official Trellis2 path as `preprocess_mesh -> get_cond -> encode_shape_slat -> sample_tex_slat -> decode_tex_slat -> postprocess_mesh -> output.export(...glb...)`.

## Four Head Asset Categories

### 1. Organic Vine / Root

Use as the primary hero category. This is the best current geometry story because `vine_d5_projected_compete` reaches depth 5 and remains mostly connected after projection.

Primary candidates:

| Priority | Candidate | Existing mesh / image path | Current evidence | Needs before head figure |
|---|---|---|---|---|
| A | Vine depth-5 compete | Remote latest mesh recorded in `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/siga_projected_recursive_loop_0715/vine_d5_projected_compete/latest_mesh.txt`; local Blender render `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/paper_quality_renders_20260508/blender_tiles/vine_d5_compete_iso.png` | Stage 5 projected summary: 192861 input vertices, 669 components -> 2 kept components, 190564 output vertices | Pull/sync the final OBJ locally if not already mirrored; render iso/front/side/detail; try GLB texture export when GPU worker is free |
| A- | Vine depth-3 compete | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_vine_meshes/vine_direct_gpu4_20260508_0615/compete/depth_03/mesh.obj` and `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_vine_meshes/vine_masked_gpu5_20260508_0615/compete/steps_1/alpha_0p25/depth_03/masked/mesh.obj` | Strong stable operator and root family | Render in same camera as depth-5 to show depth scaling |
| B | Vine fork / fork-side variants | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_vine_meshes/vine_direct_gpu4_20260508_0615/compete_fork/depth_03/mesh.obj`, `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_vine_meshes/vine_masked_gpu5_20260508_0615/fork_side/steps_1/alpha_0p25/depth_03/masked/mesh.obj` | More expressive but fragments more | Keep as secondary/detail panels unless projection improves |
| C | Lattice vine | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_vine_meshes/lattice_direct_gpu6_20260508_0615/compete/depth_03/mesh.obj` | Good variation, less central than vine example04 | Use for 30+ matrix, not first hero unless rendered result beats vine |

Root images available:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis_example_inputs_subset_20260507/04_130c2b18f1651a70f8aa15b2c99f8dba29bb943044d92871f9223bd3e989e8b1.webp`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis_example_inputs_subset_20260507/33_7d6f4da4eafcc60243daf6ed210853df394a8bad7e701cadf551e21abcc77869.webp`
- Root quality previews: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/root_quality_sweep/root_quality_steps12_contact_sheet.png`

### 2. Branching Tree / Bush

Use as the second main head category. It supports the paper's recursive/procedural modeling narrative better than DLA, though current tree geometry has more holes than vine.

Primary candidates:

| Priority | Candidate | Existing mesh / image path | Current evidence | Needs before head figure |
|---|---|---|---|---|
| A | Tree projected compete depth 3 | Remote latest mesh recorded in `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/siga_projected_recursive_loop_0715/tree_projected_compete/latest_mesh.txt`; Blender render `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/paper_quality_renders_20260508/blender_tiles/tree_compete_iso.png` | Stage 3 projected summary: 280581 input vertices, 752 components -> 2 kept components, 277556 output vertices | Render iso/front/side; choose camera that hides underside holes but does not misrepresent topology |
| A- | Tree portal | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/paper_quality_renders_20260508/blender_tiles/tree_portal_iso.png`; latest mesh recorded in `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/siga_projected_recursive_loop_0715/tree_projected_portal/latest_mesh.txt` | Visually distinct transform-copy example | Use as ornamental/transform category if it reads better than radial/portal selected meshes |
| B | Pruned L-system fork-side | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_meshes/lsystem_fork_side_a0p25_pruned.obj` and preview `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/component_pruning_20260507_1953/lsystem_fork_side_a0p25_preview_pruned.png` | Earlier strongest visual candidate; component pruning reduced 13549 components -> 14 | Render as baseline/ablation or backup tree asset |
| B | Pruned L-system fork | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_meshes/lsystem_fork_a0p5_pruned.obj` | Strong quantitative post-prune candidate | Use in ablation row, not hero unless render is clean |

Root images available:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis_example_inputs_subset_20260507/09_26717a7dad644a5cf7554e8e6d06cf82d3dd9bbae31620b36cc7eb38b8de7ac9.webp`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis_example_inputs_subset_20260507/05_154c88671d9e8785bd909e9283bc87fb2709ac7ce13890832603ea7533981a46.webp`

### 3. Coral / Crystal / Porous Stress-Test

Treat this as a stress-test category unless a better root appears. The DLA/porous family is numerically stabilized but visually blocky and not yet a safe hero.

Primary candidates:

| Priority | Candidate | Existing mesh / image path | Current evidence | Needs before head figure |
|---|---|---|---|---|
| B | DLA projected compete depth 3 | Remote latest mesh recorded in `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/siga_projected_recursive_loop_0715/dla_projected_compete/latest_mesh.txt`; Blender render `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/paper_quality_renders_20260508/blender_tiles/dla_compete_iso.png` | Stage 3 projected summary: 446965 input vertices, 110 components -> 1 kept component | Use as stress-test tile; avoid making it the most prominent hero panel |
| B- | DLA compete fork smoothed | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/smoothing/dla_compete_fork_d4_pruned/smoothed_l0p35_i12.obj` and `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/contact_sheets/dla_compete_fork_smoothing_shaded_20260508.png` | Smoothing may improve shaded readability | Render side-by-side with raw pruned to show geometry cleanup |
| C | DLA masked fork-side / radial | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_meshes/dla_fork_side_s2_a0p25_d3.obj`, `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_meshes/dla_side_s1_a0p25_d3.obj` | Texture latent compatibility exists for DLA fork-side/radial but no GLB render | Put in matrix/failure analysis; do not lead the paper |

Root images available:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/dla_cluster_points.png`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/contact_sheets/dla_projected_loop_pruned_preview_20260508.png`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/contact_sheets/shaded_dla_projected_loop_final_s3_20260508.png`

### 4. Architectural / Ornamental Transform-Copy

Use as a fourth head category only if the render reads as a deliberate artifact: portal, radial, lattice, ornamental branching. Do not overclaim transform equivariance.

Primary candidates:

| Priority | Candidate | Existing mesh / image path | Current evidence | Needs before head figure |
|---|---|---|---|---|
| A- | Tree portal projected | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/paper_quality_renders_20260508/blender_tiles/tree_portal_iso.png`; latest mesh recorded in `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/siga_projected_recursive_loop_0715/tree_projected_portal/latest_mesh.txt` | Already has Blender tile; visually different from compete | Render detail crop and side view; label as transform-copy variant |
| B | Transform portal selected mesh | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_meshes/transform_portal_d3.obj` | Texture latent compatibility confirmed on remote summary | Need GLB export or neutral render; compare against tree portal |
| B | Transform radial selected mesh | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_meshes/transform_radial4_d3.obj` | Texture latent compatibility confirmed on remote summary | Render iso/top-ish view; only use if radial symmetry is obvious |
| C | Vine/lattice portal variants | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_vine_meshes/vine_direct_gpu4_20260508_0615/portal/depth_03/mesh.obj`, `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_vine_meshes/lattice_direct_gpu6_20260508_0615/portal/depth_03/mesh.obj` | More matrix variety than hero certainty | Use in 30+ result matrix |

Contact sheet:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/contact_sheets/transform_compat_tree_gpu6_0420_sheet.png`

## 30+ Result Matrix

Target structure: 4 categories x 8 result tiles = 32 outputs, plus 4-6 ablation/failure tiles. The matrix should use one uniform render protocol, with only small labels outside the image crop.

Recommended rows:

| Row | Category | 8 tile candidates |
|---|---|---|
| 1 | Organic vine/root | vine d3 compete direct, vine d3 compete masked, vine d3 compete_fork, vine d3 fork_side, vine d3 radial, vine d3 portal, vine d5 compete, vine d5 compete_fork/fork_side if render is acceptable |
| 2 | Tree/bush | tree projected compete, tree projected compete_fork, tree projected fork_side, tree projected portal, L-system fork-side pruned, L-system fork pruned, tree compete direct preview result, tree masked compete result |
| 3 | Coral/porous stress-test | DLA projected compete, DLA projected compete_fork, DLA projected radial, DLA projected echo, DLA fork-side selected, DLA side selected, smoothed DLA compete fork, DLA raw/pruned ablation |
| 4 | Transform/ornamental | tree portal, transform_portal_d3, transform_radial4_d3, vine portal d3, vine radial4 d3, lattice portal d3, lattice scale_down d3, lattice translate_x d3 |

Minimum metadata per tile:

- root family and root source;
- operator;
- depth;
- direct/masked/projected/pruned status;
- mesh path;
- render path;
- component stats when available;
- GLB status: `success`, `pending`, `failed`, or `not attempted`.

Do not mix matplotlib previews with Blender/Cycles renders inside the final matrix. Contact sheets can be used for selection, appendix, or planning only.

## Blender / Cycles Render Protocol

Use local Blender for paper renders after OBJ/GLB files are present locally. Do not run remote Blender; current notes say remote `bpy` failed and no remote system Blender exists.

Blender binary:

`/Applications/Blender.app/Contents/MacOS/Blender`

Render script:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/blender_render_recursive_mesh.py`

Baseline command shape:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python /Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/blender_render_recursive_mesh.py -- \
  --out-dir /Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/paper_quality_renders_20260508/<batch_name> \
  --views iso front side \
  --case vine_d5_compete=/absolute/path/to/mesh.obj \
  --case tree_compete=/absolute/path/to/mesh.obj
```

Current script behavior to preserve:

- imports OBJ, joins mesh objects, centers by bounds;
- scales largest object dimension to 3.0;
- uses Cycles, 96 samples, denoising, Filmic, Medium High Contrast;
- renders 1800 x 1800;
- orthographic camera with `ortho_scale = 4.2`;
- matte warm-gray ground plane;
- neutral clay/teal material with weighted normals;
- saves `.blend` next to `.png`.

Protocol requirements for the next render pass:

1. Render every final candidate at `iso`, `front`, and `side`.
2. Keep one camera/material/light setup across the 30+ matrix.
3. Use `iso` for the matrix, `front/side` for appendix QA and selected figure insets.
4. Save output under a new timestamped folder, for example:
   `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/paper_quality_renders_20260508/matrix_20260508_<hhmm>/`.
5. Keep `.blend` files for the 4 head assets and delete or archive non-selected `.blend` files later if disk pressure matters.
6. For hero crops, use the same render output first; only then make layout crops, so the figure can be traced back to source mesh and render settings.

Suggested script upgrades before large batch rendering:

- Add GLB import support while keeping OBJ import as default.
- Add `--resolution`, `--samples`, `--material-style`, and `--transparent` options.
- Add an optional shadowless diagnostic material for thin fragmented meshes.
- Add a camera auto-fit pass based on object dimensions after normalization, with category-specific safe margins.
- Add optional height/depth color material for appendix diagnostics only.

Do not add these upgrades unless the main scripts are idle or the edit is strictly local to the render helper.

## GLB Success Strategy

If Trellis2 texturing export succeeds and produces valid GLB/PBR assets:

1. Use GLB only for 4 head assets and 8-12 selected matrix stars; do not wait for all 30+ assets to be textured.
2. Render GLB in Blender/Cycles using the same cameras and lighting as the OBJ path.
3. Head figure layout:
   - four large panels: vine/root, tree/bush, porous stress-test, transform/ornamental;
   - each panel uses textured GLB as the main image;
   - add a small neutral-geometry inset only for the method/projection story, not as decoration.
4. Matrix layout:
   - textured GLB stars at the left or top of each category row;
   - remaining tiles as neutral geometry renders;
   - mark texture status in caption, not on-image.
5. Video:
   - use textured GLB turntables for the four head assets;
   - cut to neutral matrix sweeps for breadth.

Quality gate for GLB inclusion:

- GLB imports into Blender without missing-material warnings that affect visible surfaces.
- Texture does not hide holes by noise or make topology unreadable.
- Rendered material supports the method story: local naturalization/appearance is improved while recursive support remains visible.
- If texture creates smeared, melted, or object-identity-confusing appearance, use neutral render instead.

## GLB Failure Strategy

If GLB export/postprocess fails, stalls, or produces unusable material:

1. Do not delay the 30+ matrix. Use neutral OBJ Blender/Cycles renders as the official visual protocol.
2. Make the head figure a geometry-first figure:
   - four large neutral renders;
   - one compact row of root/source images or method thumbnails beneath, if useful;
   - a caption line that texture latent compatibility is tested separately.
3. Use texture latent summaries as an appendix compatibility table, not as main visual proof.
4. For appearance, use controlled neutral materials only:
   - clay/teal for main figures;
   - optional category color accents in captions or layout, not different material per tile.
5. If reviewers need appearance evidence, include one small `texture latent/PBR voxel compatibility` table:
   - mesh;
   - guide image;
   - shape SLAT tokens;
   - texture SLAT tokens;
   - PBR voxel tokens;
   - memory;
   - status.

Existing texture latent summaries that can support this fallback:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_texture/selected_texture_gpu4_20260508_0505/dla_fork_side_s2_a0p25_d3_texture/summary.json`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_texture/selected_texture_gpu4_20260508_0505/dla_radial_s1_a0p25_d3_texture/summary.json`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_texture/selected_texture_gpu5_20260508_0505/transform_portal_d3_texture/summary.json`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/selected_texture/selected_texture_gpu5_20260508_0505/transform_radial4_d3_texture/summary.json`

## Video Demo Initial Plan

Goal: a 60-90 second demo that explains recursive control and visual breadth without overpromising texture quality.

Structure:

1. 0-8 s: problem/method visual hook. Four final assets on screen as a 2 x 2 grid, preferably rendered turntables.
2. 8-25 s: one vine/root case over depth. Show root -> depth 1 -> depth 3 -> depth 5 with projection/pruning markers.
3. 25-40 s: operator breadth. Quick cuts: compete, fork_side, radial, portal.
4. 40-55 s: category breadth. Tree, vine, porous, ornamental rows from the 30+ matrix.
5. 55-70 s: stabilization ablation. Raw fragmented result -> projected/pruned result -> Blender render.
6. 70-90 s: texture status path. If GLB succeeds, show textured turntable. If not, show neutral render plus texture latent compatibility table as a short technical note.

Implementation notes:

- Use Blender turntables for selected OBJ/GLB assets; 120 frames, 24 fps, orthographic camera, same lighting as stills.
- Export each turntable as PNG sequence or ProRes/H.264 only after visual QA.
- Avoid direct screen recordings of contact sheets for the final video.
- Keep labels minimal: category, operator, depth, projected/pruned.
- Use contact sheets only as planning plates or quick internal review.

## Figures That Must Not Go Into Main Paper

Do not use these as main-paper positive evidence:

- Zero-condition Trellis2 outputs:
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_zero_cond_shmtriton_20260507_1228_seed123/trellis2_zero_cond_preview.png`
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_zero_cond_seed_sweep_20260507_1231_seeds120_129/`
- Handcrafted condition proxy outputs as positive results:
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_handcrafted_cond_contact_sheet_20260507.png`
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_handcrafted_cond_*`
- Direct procedural point/line image -> Trellis2 results as positive evidence:
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_dinov3_min_ifs_*`
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_dinov3_min_all_20260507_seed300/`
- Full flow repair as the main method:
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_recursive_flow_repair_20260507_1912/recursive_flow_repair_contact_sheet.png`
- Raw matplotlib/preview-only contact sheets as final result figures:
  - use them for selection, QA, or appendix diagnostics only.
- Any image-entry root that is artifact-heavy and then poisons recursion:
  - especially if it looks like a sheet/blob rather than a usable 3D root.
- DLA/porous results as a hero unless the final Blender render is visibly asset-like:
  - current DLA is acceptable as a stress-test or ablation, not as the strongest visual claim.
- Texture latent summaries or PBR voxel metadata as visual proof:
  - they can support compatibility claims, but they are not substitutes for a rendered textured mesh.

## Immediate Safe Checklist

1. Build a local candidate manifest from the paths above.
2. Confirm which `latest_mesh.txt` remote paths have local OBJ mirrors; pull only if the remote worker is idle and this will not disturb running texturing.
3. Run Blender/Cycles neutral renders for the 32 matrix candidates.
4. Select the best 4 head assets from the uniform renders, not from mixed preview sheets.
5. Try GLB render replacement only for the chosen 4 if export finishes successfully.
6. Assemble video from Blender renders/turntables, not from low-quality previews.

## Short Decision Rules

- Main paper positive visual = local OBJ/GLB rendered in Blender/Cycles with stable camera.
- Appendix diagnostic = contact sheet, component/pruning comparison, preview grid.
- Negative result = zero-condition, handcrafted proxy, direct procedural image condition, full flow repair drift.
- Stress-test = DLA/porous until a better coral/crystal root exists.
- Hero order today = vine/root first, tree/bush second, transform/ornamental third or fourth, DLA/porous last unless it unexpectedly renders best.
