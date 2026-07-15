# Hero Teaser Five-Asset Zoom Plan (2026-05-11)

## Context

This document preserves the active head-figure task across Codex context compaction. The current priority is no longer the intro/related-work two small figures. The user asked to rebuild the head figure from five assets, with separate transparent-background renders and zoom-in callouts, then compose them into a high-resolution 3:2 teaser using the PPTX workflow.

## Required Output

- Five assets rendered separately on pure white / transparent alpha background.
- For each asset:
  - One clean overview render.
  - Five square zoom candidates at different positions and scales.
  - Select the best zoom region that shows recursive / fractal detail.
  - Final teaser should show a light gray square box on the overview and a small zoom-in image beside it.
- Final composition:
  - 3:2 aspect ratio.
  - Five asset groups arranged tightly but not overlapping, roughly in a 3x2 large figure.
  - Pure white background.
  - No text inside the figure.
  - Export as PPTX plus high-resolution PNG and/or PDF, target 2K-4K.
- Visual standard: publication-grade teaser. Iterate lighting, material, camera, zoom positions, and asset choice until it is clean.

## Five Asset Set

1. Keep existing head-figure case 1: bismuth crystal / pyramid-like crystal.
2. Keep existing head-figure case 2: pyrite crystal.
3. Replace/keep coral as a dense coral case, specifically use the high-density coral shown in the user's third reference image, and smooth the surface before final render.
4. Add V48 bamboo-like asset from Codex session `019e136b-4185-70a1-8b0e-8c04e1cc9c42` titled `整理R-SLG任务交接`.
   - Current V40/V48 bamboo-like branch is too sparse.
   - Need to deepen depth and/or increase density if possible.
   - Render with better colors/materials.
   - This is expected to require remote a100-2 work if local assets are insufficient.
5. Add current space-colonization comparison tree-crown case with leaves.
   - Need GLB/source.
   - Prefer textured/PBR; at minimum leaves must be green.

## User-Supplied Reference Images

- `/Users/fanta/Library/Containers/com.tencent.qq/Data/tmp/39cf6892-18a5-4dc9-a783-95d0e82ec2ef.png`
  - Shows V40 l-system branch variants. The target bamboo-like case is sparse; user wants the V48 variant from session history and to make it denser/deeper.
- `/Users/fanta/Library/Containers/com.tencent.qq/Data/tmp/d648f9cc-5ec3-4215-b5ac-77f1552e2a2e.png`
  - Shows current tree-crown comparison case with leaves; use the ours/tree-crown GLB and make leaves green.
- User's third embedded image shows coral density sweep; choose dense coral (density around 1.35 or 1.75) and smooth it.

## Constraints

- Use at most two SSH shells.
- Use remote new `a100-2` machine only if needed for rerunning/deepening cases.
- Use at most two GPUs on remote.
- Prefer local rendering/composition where possible.
- Use PPTX skill for final composition.
- Do not claim done without visual QA of overview renders, zooms, and final composition.

## Immediate Plan

1. Locate existing five asset candidates locally:
   - bismuth/pyrite/coral from previous hero or paper figure outputs.
   - V48 bamboo-like asset and/or scripts/session logs that produced it.
   - tree-crown GLB used in space-colonization comparison.
2. If V48/deeper bamboo or dense coral is missing locally, use one SSH shell to inspect a100-2 paths and rerun/generate denser variants.
3. Write reproducible Blender render script:
   - Transparent alpha output with white-preview-friendly lighting.
   - Per-case color/PBR material overrides.
   - Smooth coral via Blender shade smooth / bevel / optional remesh or smoothing modifier.
   - Center object, prevent cropping, maximize occupied area.
   - Render overview and five square zoom candidates for each case.
4. Select zoom candidates by visual inspection:
   - Prefer regions with clear recursive structure, not empty space or flat surface.
   - Avoid cropped/occluded/too-dark zooms.
5. Generate PPTX:
   - 3:2 canvas.
   - Place five grouped overview+box+zoom panels.
   - No text.
   - White background, light gray boxes.
6. Export PNG/PDF and run at least one visual QA pass.

## Current Status

- Plan doc created and updated for the 2026-05-12 continuation.
- Local candidate assets selected for the first reproducible render pass:
  - bismuth: `visuals/strict_visual_matched_texture_V21_ifs_transform_natural_tex4096_seed20292500_20260510/V21_ifs_bismuth_stepped_transform_d5_iridescent_steps8_tex4096_seed20294604_xformers/textured.glb`
  - pyrite: `visuals/strict_visual_matched_texture_V21_ifs_transform_natural_tex4096_seed20292500_20260510/V21_ifs_pyrite_lattice_transform_d4_faceted_steps8_tex4096_seed20294603_xformers/textured.glb`
  - dense coral: `visuals/coral_density_extreme_texture_20260509/coral_density_param_density_1p75_octopus_steps8_tex2048_xformers/textured.glb`
  - bamboo-like branch: V48 is recorded as the requested source family, but V48 dense-C was known to be coarse/faceted. First render pass uses the later denser/smoother V59 compact-D smoothpost GLB: `results/strict_visual_matched_texture_V59_lsystem_branch_smooth_short_bough_yfork_BD_smoothpost_20260511/V59_lsys_branch_smooth_short_bough_compact_D_smoothpost/textured.glb`. If the visual still reads too sparse, rerun/deepen remotely on `a100-2` with at most two GPUs.
  - tree crown with leaves: `visuals/strict_visual_matched_texture_V32_sc_tree_canopy_veil_naturalization_20260511/V32_sc_tree_balanced_canopy_D_steps8_tex2048_seed20292515_xformers/textured.glb`
- New reproducible files:
  - render manifest: `scripts/figures/hero_teaser_five_asset_manifest_20260512.json`
  - transparent Blender renderer: `scripts/figures/hero_teaser_five_asset_transparent_render_20260512.py`
  - PNG/contact-sheet composer: `scripts/figures/compose_hero_teaser_five_asset_20260512.py`
- Planned first output directory: `visuals/hero_teaser_five_asset_transparent_20260512_v1/`.
- The render script preserves RGBA alpha. The composer makes white QA previews and the 3:2 white-background teaser separately.
- PPTX export is still pending because local `python-pptx` is not installed in `/usr/bin/python3`; high-resolution PNG/contact-sheet generation proceeds first, then PPTX can be added after installing/using a compatible Python environment.

## 2026-05-12 Local Render Iteration Log

### v1 Pipeline Proof

- Output directory: `visuals/hero_teaser_five_asset_transparent_20260512_v1/`.
- Status: useful only as a pipeline proof; not paper-ready.
- Main failures:
  - The first slot used a V21 IFS transform frame instead of the old hero bismuth hopper.
  - The coral density endpoint was still visibly voxel/blocky.
  - The V59 branch asset was too sparse for the user's requested bamboo-like recursive head-figure slot.
  - Composition had too much whitespace and the callout boxes were partly misregistered after alpha-content cropping.

### v2 Corrected Asset Pass

- Output directory: `visuals/hero_teaser_five_asset_transparent_20260512_v2/`.
- Asset changes:
  - Restored old hero bismuth hopper: `visuals/connected_scaffold_v2_textured_glb_hq_20260509/bismuth_hopper_bismuth_hq_steps8_tex2048_xformers/textured.glb`.
  - Restored old hero pyrite lattice: `visuals/connected_scaffold_v2_textured_glb_hq_20260509/pyrite_lattice_pyrite_hq_steps8_tex2048_xformers/textured.glb`.
  - Replaced the blocky density-endpoint coral with the less-voxel V14 table-coral candidate: `visuals/strict_visual_matched_texture_v14_branching_coral_seed20279100_20260510/v14_dla_branching_table_coral_b_steps8_tex2048_seed20279804_xformers/textured.glb`.
  - Tested V49 dense-C branch for the bamboo-like slot: `results/strict_visual_matched_texture_V49_lsystem_branch_highres_smooth_yfork_naturalization_20260511_remote/V49_lsys_branch_highres_smooth_yfork_dense_C_steps8_tex2048_seed20303514_xformers/textured.glb`.
  - Kept the tree-crown asset with green/brown material override.
- v2 QA:
  - Left three assets now match the requested old hero family more closely.
  - Bismuth and pyrite are structurally correct, but the current material override is too flat/dull for a teaser.
  - V14 coral has a better silhouette and less voxel-block endpoint behavior, but zoom selection and final placement need refinement.
  - V49 is still a weak "bamboo-like" substitute; it reads as a sparse root/branch, not a dense recursive bamboo asset.
  - The final 3:2 composition is valid and high-resolution, but still has too much uneven whitespace and one top-row zoom sits too close to the image edge.
- Gate: v2 is not publication-grade. Continue to v3 before any PPTX/PDF export.

### v3 Immediate Targets

- Preserve or improve original PBR/textured look for bismuth and pyrite instead of forcing flat single-material colors.
- Use manual or more stable zoom selections after contact-sheet inspection.
- Increase image occupancy without clipping callouts.
- Keep V49/V59 as temporary fourth-slot candidates only; if v3 still fails visually, run a remote denser/deeper fourth-slot asset experiment on `a100-2` with at most two GPUs.

### v3 Local QA Package

- Output directory: `visuals/hero_teaser_five_asset_transparent_20260512_v3/`.
- Delivery/inspection package: `visuals/hero_teaser_five_asset_transparent_20260512_delivery_v3/`.
- Package contents:
  - `composed/hero_teaser_five_asset_3x2_3600x2400.png`.
  - `composed/hero_teaser_five_asset_3x2_3600x2400.pdf`.
  - `composed/hero_teaser_five_asset_3x2_3600x2400.pptx`.
  - `composed/hero_teaser_zoom_candidate_contact_sheet.png`.
  - five transparent overview PNGs in `individual_rgba/`.
  - five transparent square zoom candidates per asset in `zoom_candidates/`.
- v3 QA:
  - Corrected bismuth/pyrite to preserve the old hero PBR/texture instead of the flat single-material override.
  - The final image is 3600x2400, white background, no labels/text, with gray zoom boxes.
  - The left three and tree-crown assets are current usable candidates.
  - The fourth bamboo-like/branch slot remains below the head-figure bar. Local V48/V49/V59/V60/V61/V62/V63 candidates were inspected; they are either sparse, too root-like, or only OBJ/QA-level.
- Current gate: v3 is ready for user visual inspection, but should not be described as the final publication-grade head figure until the fourth asset is replaced or rerun remotely with denser/deeper grammar.

### Remote V63 Fourth-Slot Rerun

- Remote target: `a100-2`, one SSH shell, GPUs 4 and 5 only.
- Run name: `strict_visual_matched_texture_V63_lsystem_branch_distributed_recursive_bough_BC_hero_20260512_remote`.
- Command family: `assets/launch_strict_visual_matched_texture_V63_lsystem_branch_distributed_recursive_bough_20260512.sh` with `V63_GPUS="4 5"` and `V63_PRIORITY_BC_ONLY=1`.
- Completed outputs pulled back locally:
  - `results/strict_visual_matched_texture_V63_lsystem_branch_distributed_recursive_bough_BC_hero_20260512_remote/V63_lsys_branch_distributed_dense_B_steps8_tex2048_seed20323514_xformers/textured.glb`.
  - `results/strict_visual_matched_texture_V63_lsystem_branch_distributed_recursive_bough_BC_hero_20260512_remote/V63_lsys_branch_balanced_fan_C_steps8_tex2048_seed20323515_xformers/textured.glb`.
- Both remote `summary.json` files report `status: ok`.
- v4b tested V63 dense B in the fourth slot.
- v4c tested V63 balanced C in the fourth slot.
- Visual decision:
  - v4c is the current-best fourth-slot candidate because the branch structure is more distributed and reads more naturally than v4b.
  - v4b is greener but has a swollen/tube-like plant look.
  - Neither remote V63 candidate fully satisfies the user's original "dense bamboo-like recursive asset" target, so the fourth slot remains a visual-risk item for final publication. For current inspection, use v4c.
