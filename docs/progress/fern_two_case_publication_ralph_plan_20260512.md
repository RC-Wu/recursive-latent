# Fern Two-Case Publication Ralph Plan 20260512

Status: active, 20260512e remote iteration in progress  
Local root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU policy: use only GPUs `4,5,6,7`; at most two SSH shells from the local session.  
Output targets:

- `results/fern_two_case_recursive_remote_20260512a`: completed, rejected for weak fiddlehead root and weak fern depth changes.
- `results/fern_two_case_recursive_remote_20260512b`: completed, technically successful but not promoted to final visual evidence.
- `results/fern_two_case_recursive_remote_20260512c`: completed, rejected for torn fiddlehead sheets and subtle fern depth changes.
- `results/fern_two_case_recursive_remote_20260512d`: completed, technically stable but rejected for artificial fiddlehead rung bands and subtle fern depth changes.
- `results/fern_two_case_recursive_remote_20260512e`: active coil-surface/root-hierarchy iteration.

## Objective

Run two fern cases to publication-grade visual quality using the remote TRELLIS2/SLat recursive pipeline:

1. **Fiddlehead/crozier case**: a curled fern shoot with visible spiral/nested local detail, matching the user reference of a green curled fern tip.
2. **Compound fern frond case**: a clear fern frond with a rachis, pinnae, and smaller leaflet detail, matching the user reference of a symmetric compound fern leaf.

These are intended as important visual results, not diagnostics. They require real remote recursive outputs, not local-only procedural stand-ins.

## Prior Failure Constraints

The earlier plant/fern loops showed:

- image-conditioned roots often became flat or too heavy for clean recursion;
- conservative fern operators preserved connectivity but produced weak depth differences;
- aggressive copy operators produced dust, sheet tearing, or rod-like artifacts;
- the root mesh must already contain the correct biological handle: spiral curl for fiddlehead, rachis/pinnae handles for fern frond.

Therefore this loop changes both root candidates and grammar schedule.

## Execution Strategy

### Root Candidates

Generate root candidates on the remote machine using `assets/prepare_fern_showcase_roots_20260512.py`:

- `fiddlehead_showcase_curl_a`: thick green crozier-style support with a large curl and attached scale/leaflet details.
- `fiddlehead_nested_curl_b`: tighter nested crozier with secondary small curl details.
- `fern_showcase_compound_a`: arched compound frond with dense alternating pinnae and leaflets.
- `fern_showcase_lacy_b`: lacy compound frond variant with more fine leaflets and a stronger triangular silhouette.

These are root inputs only. Final evidence must come from remote SLat recursion and Blender render QA.

### Remote SLat Lanes

Use `assets/run_fern_two_case_recursive_remote_20260512a.sh`.

- GPU 4: fiddlehead showcase root sweep, depth 0..3, conservative and visible curl grammars.
- GPU 5: low-complexity image-root attempts for fiddlehead/fern references, then guarded recursion only if root complexity is usable.
- GPU 6: compound fern showcase root sweep, depth 0..3/4, midrib/pinnae grammars.
- GPU 7: Poly Haven fern and previous clean fern root fallback, depth 0..3, to provide a second independent frond candidate.

### Grammar Families

New aliases added to `trellis2_recursive_slat_grammar_workflow.py`:

- `v26a_fiddlehead_nested_curl`: restrained spiral echo plus tiny terminal leaflets.
- `v26a_fiddlehead_visible_curl`: stronger curl echo for visible depth changes.
- `v26a_fern_showcase_pinnae`: midrib/pinnae expansion plus tiplets.
- `v26a_fern_showcase_dense_pinnae`: denser variant for depth-visible fern fronds.

Existing safe aliases are also included:

- `v25n_fiddlehead_thick_curl`
- `v25l_fiddlehead_guarded_curl`
- `v25p_fern_midrib_pinnae_handles`
- `v25n_fern_pinnae_sparse`

## Acceptance Gates

A case is promoted only if all are true:

- OBJ outputs exist for all displayed depths.
- Metrics CSV/JSON exists and reports occupancy connectivity.
- Depth sequence has clear visual changes from depth 0 to final depth.
- No major disconnected islands, torn sheets, rod artifacts, or semantic collapse.
- Blender white/studio render QA exists for selected depths.
- Final selected view is centered, readable, and suitable for single-figure or hero use.

## Iteration Policy

If the first remote sweep is not publication-grade:

1. Inspect metrics and preview images.
2. Reject failure mode explicitly: no-op, fragmentation, bad root, bad axis, excessive tokens, or poor render.
3. Modify either root generation or grammar parameters.
4. Launch the next remote suffix (`20260512b`, `20260512c`, ...).
5. Stop only when both cases have paper-usable depth sequences and render QA, or a concrete external blocker is documented.

## 20260512a Verdict

Completed remotely on `a100-2` and pulled locally to
`results/fern_two_case_recursive_remote_20260512a_pull`.

- Produced 87 previews/OBJs plus metrics.
- Fiddlehead result was rejected: the root read as a straight stem with a small terminal knot, so recursion produced a long curved rod with basal clutter rather than a publication-grade crozier.
- Compound fern was clean and connected but depth changes were weak; much of the sequence read as density/length variation rather than recursive structure.

## 20260512b Verdict

Completed remotely on `a100-2` and pulled locally to
`results/fern_two_case_recursive_remote_20260512b_pull`.

- Produced 72 previews/OBJs plus metrics.
- Stable candidate: `fiddlehead_macro_crozier_c_d3_20260512b/v26b_fiddlehead_scale_buds/depth_03`.
  Metrics: occupancy largest component ratio `1.0`, raw face largest component ratio about `0.9959`.
- Rejected aggressive fiddlehead variants: `v26b_fiddlehead_macro_then_buds` and most macro echo rows fragment visibly by depth 3.
- Stable fern candidates: `fern_broad_frond_c_d4_20260512b/v26b_fern_branchlet_pinnae/depth_04` and
  `fern_branching_frond_d_d4_20260512b/v26b_fern_branchlet_pinnae/depth_04`.
  Metrics are strong, but depth 0 to 4 remains visually too subtle for a main visual.
- Render QA exists at
  `results/fern_two_case_recursive_remote_20260512b_pull/blender_qa/selected_render_contact_20260512b_white.png`.
- Conclusion: 12b is a valid backup/diagnostic sweep but not final publication-grade evidence.

## 20260512c Plan

Purpose: promote the two cases from "technically successful" to main-figure candidates.

- New roots from `assets/prepare_fern_showcase_roots_20260512c.py`.
- Fiddlehead changes:
  - compact crozier-first roots: `fiddlehead_compact_crozier_e`, `fiddlehead_hook_crozier_f`;
  - shorter main stem, larger readable coil, more attached scale leaflets.
- Fern changes:
  - broader hierarchical roots: `fern_wide_frond_e`, `fern_fractal_frond_f`;
  - more second-order pinna handles before SLat recursion.
- Grammar changes in `assets/trellis2_recursive_slat_grammar_workflow.py`:
  - `v26c_fiddlehead_supported_scales`;
  - `v26c_fiddlehead_compact_echo`;
  - `v26c_fiddlehead_scales_then_echo`;
  - `v26c_fern_visible_sidecars`;
  - `v26c_fern_fractal_sidecars`;
  - `v26c_fern_sidecars_then_fractal`.
- Important: these c-grammars use supported sidecar copies via the existing tube-support helper to reduce the floating-fragment failure seen in aggressive 12b rows.
- Acceptance remains strict: final selected results need remote OBJ outputs, metrics, local Blender render QA, clear depth progression, and no obvious floating debris or semantic collapse.

## 20260512c Verdict

Completed remotely on `a100-2`, pulled locally to
`results/fern_two_case_recursive_remote_20260512c_pull`, and rendered locally with Blender to
`results/fern_two_case_recursive_remote_20260512c_pull/blender_qa/selected_render_contact_20260512c_white.png`.

- Produced 72 preview/OBJ outputs plus metrics.
- Fiddlehead verdict: rejected for main-figure use. The compact crozier is readable, but `v26c_fiddlehead_supported_scales` and related rows produce torn sheet fragments around the lower/right coil; `v26b_fiddlehead_scale_buds` stays cleaner but creates artificial ladder-like support detail rather than a natural fern crozier.
- Compound fern verdict: rejected for main-figure use. `v26b_fern_branchlet_pinnae` is connected and clean but the depth 0 to 4 change remains too subtle; the c-sidecar variants create more visible changes but fragment into speckles and side islands.
- Claim status: 12c is valid diagnostic evidence only. It does not satisfy the publication-grade gate because the two target cases are not simultaneously clean, natural, and depth-visible.

## 20260512d Plan

Purpose: replace 12c's fragile sidecar emphasis with stronger roots and conservative visible refinement.

- New root script: `assets/prepare_fern_showcase_roots_20260512d.py`.
- New runner: `assets/run_fern_two_case_recursive_remote_20260512d.sh`.
- New grammar aliases in `assets/trellis2_recursive_slat_grammar_workflow.py`:
  - `v26d_fiddlehead_inner_buds`;
  - `v26d_fiddlehead_solid_echo`;
  - `v26d_fiddlehead_echo_then_buds`;
  - `v26d_fern_visible_refinement`;
  - `v26d_fern_bounded_sidelets`;
  - `v26d_fern_refinement_then_sidelets`.
- Root candidates:
  - `fiddlehead_solid_koru_g`: tube-dominant crozier, short stem, connected tubular buds, no thin scale cards as the primary handle.
  - `fiddlehead_bud_crozier_h`: denser crozier variant with the same tube-dominant contract.
  - `fern_triangular_frond_g`: broad triangular compound frond with thick primary and secondary pinna handles.
  - `fern_lacy_frond_h`: denser lacy compound frond with explicit refinement anchors.
- Remote lanes:
  - GPU 4: `fiddlehead_solid_koru_g_d4_20260512d`, depth 4, d-fiddlehead grammars plus `v26b_fiddlehead_scale_buds` backup.
  - GPU 5: `fiddlehead_bud_crozier_h_d4_20260512d`, same grammar set.
  - GPU 6: `fern_triangular_frond_g_d4_20260512d`, depth 4, d-fern grammars plus `v26b_fern_branchlet_pinnae` backup.
  - GPU 7: `fern_lacy_frond_h_d4_20260512d`, same grammar set.
- Local preflight completed: `results/fern_showcase_roots_20260512d/fern_showcase_roots_contact_sheet_20260512d.png` shows stronger root handles than 12c. This is not final evidence; final evidence still requires remote SLat OBJ outputs, metrics, and Blender QA.

## 20260512d Verdict

Completed remotely on `a100-2`, pulled locally to
`results/fern_two_case_recursive_remote_20260512d_pull`, and rendered locally with Blender to
`results/fern_two_case_recursive_remote_20260512d_pull/blender_qa/selected_render_contact_20260512d_white.png`.

- Produced 80 preview/OBJ outputs plus metrics.
- Fiddlehead verdict: improved over 12c but rejected for main-figure use. The crozier silhouette is readable and stable, but `v26d_fiddlehead_inner_buds`/`v26b_fiddlehead_scale_buds` accumulate a horizontal ladder/rung band under the coil by depth 3/4. This is not natural enough for a publication visual.
- Compound fern verdict: clean and centered, with strong connectivity metrics, but rejected as a recursive showcase because depth 0 to 4 changes are visually too subtle. The result reads as nearly the same frond rather than a multi-scale recursive asset.
- Claim status: 12d is backup/diagnostic evidence only. It should not be promoted unless explicitly used as a conservative stability example.

## 20260512e Plan

Purpose: remove the 12d fiddlehead rung artifact and make compound-fern depth changes visible without returning to 12c-style fragmentation.

- New root script: `assets/prepare_fern_showcase_roots_20260512e.py`.
- New runner: `assets/run_fern_two_case_recursive_remote_20260512e.sh`.
- New grammar aliases in `assets/trellis2_recursive_slat_grammar_workflow.py`:
  - `v26e_fiddlehead_surface_microbuds`;
  - `v26e_fiddlehead_tiny_coil_echo`;
  - `v26e_fiddlehead_surface_then_echo`;
  - `v26e_fern_outer_pinnae_refinement`;
  - `v26e_fern_hierarchical_visible`;
  - `v26e_fern_hierarchical_then_tiplets`.
- Fiddlehead change:
  - roots `fiddlehead_surface_crozier_i` and `fiddlehead_dense_crozier_j` are coil-dominant with surface-distributed buds;
  - grammar uses a surface-band mask around the crozier rather than a terminal underside mask, so repeated depths should add small radial buds around the coil instead of a ladder under it.
- Compound fern change:
  - roots `fern_tiered_frond_i` and `fern_hierarchical_frond_j` have thicker primary/secondary pinna handles;
  - grammar extends outer pinnae and midrib handles with bounded, attached copies to create visible depth progression while preserving connectivity.
- Remote lanes:
  - GPU 4: `fiddlehead_surface_crozier_i_d4_20260512e`, depth 4, e-fiddlehead grammars plus 12d inner-bud backup.
  - GPU 5: `fiddlehead_dense_crozier_j_d4_20260512e`, same grammar set.
  - GPU 6: `fern_tiered_frond_i_d4_20260512e`, depth 4, e-fern grammars plus `v26b_fern_branchlet_pinnae` backup.
  - GPU 7: `fern_hierarchical_frond_j_d4_20260512e`, same grammar set.
- Acceptance remains unchanged: remote OBJ outputs, metrics, local Blender render QA, clear depth progression, and no obvious floating debris, rung artifacts, torn sheets, or semantic collapse.

## 20260512e Verdict

Completed remotely on `a100-2`, pulled locally to
`results/fern_two_case_recursive_remote_20260512e_pull`, and rendered locally with Blender to
`results/fern_two_case_recursive_remote_20260512e_pull/blender_qa/selected_render_contact_20260512e_white.png`.

- Produced 80 preview/OBJ outputs plus metrics.
- Fiddlehead verdict: cleaner than 12d but rejected. `v26e_fiddlehead_surface_microbuds` removes the rung band and has excellent connectivity, but depth 0 to 4 is visually too close to no-op. The echo variants create more visible differences, but reintroduce underside bars/fragment risk.
- Compound fern verdict: still rejected for main-figure use. `v26b_fern_branchlet_pinnae` is the most visible and connected row, but the visual effect reads mainly as length/density growth rather than a clear recursive hierarchy. The e-fern rows are even more subtle.
- Claim status: 12e is useful diagnostic evidence for stability but not publication-grade showcase evidence. Continue with 12f using stronger macro-local child modules rather than microbud refinement.

## 20260512f Plan

Purpose: force clear depth-visible recursion while preserving the clean connectivity learned from 12e.

- Root strategy:
  - reuse the stable 12e roots for the first 12f pass to avoid confounding root quality;
  - if the first 12f pass still fails, generate roots with pre-existing larger side handles.
- Grammar strategy:
  - fiddlehead: add sparse, larger coil-attached bud modules using surface-band source tokens and explicit support tubes; avoid terminal underside masks and avoid whole-coil echo.
  - compound fern: add larger alternating pinna/branchlet modules with bounded source tokens and tube support, using side-aware displacement large enough to survive SLat decode.
- Remote lanes:
  - GPU 4/5: two fiddlehead roots, depth 4, 12f macro-bud grammars.
  - GPU 6/7: two fern roots, depth 4, 12f visible-pinna grammars.
- Acceptance remains strict: depth progression must be visually obvious, not merely measurable; no large disconnected side islands, rung bands, torn sheets, or semantic collapse.

## 20260512g Plan

Purpose: incorporate the user correction that the fiddlehead/crozier case must be a true logarithmic spiral, not an equal-spacing spiral.

- New root script: `assets/prepare_fern_showcase_roots_20260512g.py`.
- New runner: `assets/run_fern_two_case_recursive_remote_20260512g.sh`.
- Fiddlehead root contract:
  - `fiddlehead_log_spiral_i` and `fiddlehead_log_dense_j`;
  - metadata records `r(theta)=r0*exp(-b*theta)`;
  - buds are placed at approximately equal arc-length intervals along the logarithmic spiral.
- Compound fern root contract:
  - `fern_tiered_frond_i` and `fern_hierarchical_frond_j`;
  - root has explicit rachis, primary pinnae, second-order branchlets, attached laminae, and refinement anchors.
- Remote lanes:
  - GPU 4: `fiddlehead_log_spiral_i_d4_20260512g`, depth 4, log-open root, macro surface-bud grammars.
  - GPU 5: `fiddlehead_log_dense_j_d4_20260512g`, depth 4, log-dense root, macro surface-bud plus light echo grammars.
  - GPU 6: `fern_tiered_frond_i_d4_20260512g`, depth 4, macro pinnae/branchlet grammars.
  - GPU 7: `fern_hierarchical_frond_j_d4_20260512g`, depth 4, macro pinnae/branchlet grammars.
- Image-conditioned root lane remains in scope after 12g starts: use the existing golden spiral/koru/frond conditioning images through the TRELLIS2 Dinov3 route, then only recurse roots that survive metric and visual preflight.
- Acceptance remains strict: final claims require remote OBJ outputs, metrics CSV/JSON, local Blender render QA, preserved log-spiral readability, visible depth progression, and no rung bands, underside bars, torn sheets, large islands, or semantic collapse.

Local preflight status: `results/fern_showcase_roots_20260512g/fern_showcase_roots_contact_sheet_20260512g.png` exists and is only a root check, not final evidence.

## 20260512g Verdict

Completed remotely on `a100-2`, pulled locally to
`results/fern_two_case_recursive_remote_20260512g_pull`, and rendered locally with Blender to
`results/fern_two_case_recursive_remote_20260512g_pull/blender_qa/selected_render_contact_20260512g_white.png`.

- Produced 70 OBJ/preview outputs plus metrics.
- Root contract passed: the new fiddlehead roots are true logarithmic spirals and preserve the corrected crozier silhouette at depth 0.
- Fiddlehead verdict: rejected for main-figure use. `v26e_fiddlehead_surface_microbuds` is clean but visually near no-op; `v26f_fiddlehead_macro_*` creates visible recursion but decodes into scattered, detached leaf/point clouds around the spiral.
- Compound fern verdict: rejected for main-figure use. `v26b_fern_branchlet_pinnae` is connected but too subtle; `v26f_fern_macro_*` creates strong depth change but produces large floating grids/clouds in Blender QA.
- Claim status: 12g is valid diagnostic evidence for the corrected logarithmic root and for the failure boundary of aggressive macro grammars, but it is not publication-grade visual evidence.

## 20260512h Plan

Purpose: keep the corrected 12g roots but replace the v26f scattered macro operators with low-count, tube-supported attached child modules.

- New runner: `assets/run_fern_two_case_recursive_remote_20260512h.sh`.
- New grammar aliases in `assets/trellis2_recursive_slat_grammar_workflow.py`:
  - `v26h_fiddlehead_attached_surface_buds`;
  - `v26h_fiddlehead_attached_buds_then_micro`;
  - `v26h_fern_attached_pinnae`;
  - `v26h_fern_attached_pinnae_then_tiplets`.
- Key operator change:
  - use stricter `_surface_band_mask_20260512e`/height-band masks capped to roughly 28-34 source tokens;
  - use one target per pass, not two simultaneous target clouds;
  - reduce displacement to about half of v26f;
  - call `masked_target_copies_with_tube_support_20260511t` instead of `attached_transform_masked_copies`.
- Remote lanes:
  - GPU 4: `fiddlehead_log_spiral_i_d4_20260512h`, depth 4, h-fiddlehead grammars plus clean microbud control.
  - GPU 5: `fiddlehead_log_dense_j_d4_20260512h`, depth 4, h-fiddlehead grammars plus one v26f stress row.
  - GPU 6: `fern_tiered_frond_i_d4_20260512h`, depth 4, h-fern grammars plus v26b clean control.
  - GPU 7: `fern_hierarchical_frond_j_d4_20260512h`, depth 4, h-fern grammars plus v26f stress row and v26b clean control.
- Acceptance remains strict: remote OBJ outputs, metrics CSV/JSON, local Blender render QA, clear depth progression, preserved log spiral, and no visible floating debris, torn sheets, rung bands, or semantic collapse.

## 20260512h Verdict And Repair Probe

Completed remotely on `a100-2`, pulled locally to
`results/fern_two_case_recursive_remote_20260512h_pull`, and rendered locally with Blender to
`results/fern_two_case_recursive_remote_20260512h_pull/blender_qa/selected_render_contact_20260512h_white.png`.

- Produced 65 OBJ/preview outputs plus metrics.
- Fiddlehead verdict: improved over v26f but still rejected. The true logarithmic spiral is preserved, and token counts are moderate, but Blender QA still shows detached small modules/fragments around the crozier.
- Compound fern verdict: rejected. The h rows are less explosive than v26f, but the visible recursive modules still scatter around the main frond rather than reading as attached pinnae.
- Repair probe: local mesh repair generated 28 variants in
  `results/fern_two_case_recursive_remote_20260512h_repair_probe`; metrics improved for several variants, but Blender QA at
  `results/fern_two_case_recursive_remote_20260512h_repair_probe/blender_qa/repair_candidates_contact_20260512h_white.png`
  shows bridge rods or voxel-blobby surfaces. These are not publication-grade final visuals and may only be cited as postprocess diagnostics.
- Claim status: 12h is diagnostic evidence only. Do not promote repair variants as raw method success.

## 20260512i Plan

Purpose: replace global scattered token masks with connected local handle patches and strengthen the root contract so SLat recursion extends already-attached structures rather than inventing children from sparse surface dust.

- New root script: `assets/prepare_fern_showcase_roots_20260512i.py`.
- New runner: `assets/run_fern_two_case_recursive_remote_20260512i.sh`.
- New root candidates:
  - `fiddlehead_log_handle_k` and `fiddlehead_log_handle_l`: true logarithmic spiral roots with fewer, thicker, equal-arc-length connected side handles and pre-attached secondary buds.
  - `fern_handle_frond_k` and `fern_handle_frond_l`: connected rachis, primary/secondary pinna handles, fewer/thicker laminae, and explicit handle tips for low-amplitude recursion.
- New SLat helpers:
  - `connected_patch_mask_20260512i`: selects one local handle patch instead of scattered global top-k surface tokens.
  - `masked_target_copies_with_patch_support_20260512i`: final patch copy plus centroid and sampled per-token supports with radius >= 1 voxel.
- New grammar aliases:
  - `v26i_fiddlehead_log_attached_patch`;
  - `v26i_fiddlehead_log_attached_patch_double`;
  - `v26i_fern_handle_pinnae`;
  - `v26i_fern_handle_pinnae_light_tiplets`.
- Local preflight status:
  - `python3 -m py_compile assets/prepare_fern_showcase_roots_20260512i.py assets/trellis2_recursive_slat_grammar_workflow.py` passed.
  - `bash -n assets/run_fern_two_case_recursive_remote_20260512i.sh` passed.
  - Root contact sheet exists at `results/fern_showcase_roots_20260512i_preflight/fern_showcase_roots_contact_sheet_20260512i.png`.
  - All four root meshes have mesh component LCR `1.0`.
- Remote lanes:
  - GPU 4: `fiddlehead_log_handle_k_d4_20260512i`, depth 4, i-fiddlehead patch grammars plus h-control.
  - GPU 5: `fiddlehead_log_handle_l_d4_20260512i`, depth 4, i-fiddlehead patch grammars plus h-control.
  - GPU 6: `fern_handle_frond_k_d4_20260512i`, depth 4, i-fern handle grammars plus h-control.
  - GPU 7: `fern_handle_frond_l_d4_20260512i`, depth 4, i-fern handle grammars plus h-control.
- Acceptance remains strict: remote OBJ outputs, metrics CSV/JSON, local Blender render QA, preserved true log spiral, visible depth progression, no detached floating fragments, and no voxel-blobby postprocess substitution.

## 20260512i Verdict

Completed remotely on `a100-2`, pulled locally to
`results/fern_two_case_recursive_remote_20260512i_pull`, and rendered locally with Blender to
`results/fern_two_case_recursive_remote_20260512i_pull/blender_qa/selected_render_contact_20260512i_white.png`.

- Produced 60 OBJ/preview outputs plus metrics.
- Technical status: all four lanes finished with status `0`; metrics CSV/JSON exist at
  `results/fern_two_case_recursive_remote_20260512i_pull/metrics/fern_two_case_metrics_20260512i.csv` and `.json`.
- Metrics verdict: rejected. Depth-4 occupancy LCR is below a publication-safe threshold for every selected row. Examples:
  - `fiddlehead_log_handle_k / v26i_fiddlehead_log_attached_patch / d4`: occupancy LCR `0.876`, face LCR `0.968`.
  - `fiddlehead_log_handle_l / v26i_fiddlehead_log_attached_patch / d4`: occupancy LCR `0.873`, face LCR `0.963`.
  - `fern_handle_frond_k / v26i_fern_handle_pinnae / d4`: occupancy LCR `0.869`, face LCR `0.958`.
  - `fern_handle_frond_l / v26i_fern_handle_pinnae / d4`: occupancy LCR `0.824`, face LCR `0.503`.
- Visual verdict: rejected. Blender QA shows the main log spiral and fern backbone remain readable, but the recursive additions decode as detached dust/sheet fragments. This is not a small repair issue and should not be promoted.
- Failure interpretation: connected-patch latent selection reduced global explosion but still leaves moved sparse coordinates semantically under-supported. Repeating the move across depths accumulates detached small components.
- Next action: 12j should move recursion back into the connected mesh/root construction stage and use TRELLIS2/SLat as a per-depth naturalization/reprojection pass. Each displayed depth should be a fully connected mesh before encoding, rather than repeatedly translating sparse latent patches.

## 20260512j/12k/12l Handoff Update

Purpose: respond to the user correction that the second fiddlehead/log-spiral case must not contain two long rods. It should be only a true logarithmic spiral plus recursive self-similar spirals growing along it.

### 20260512j Status

- Implemented mesh-stage per-depth roots and passthrough SLat naturalization, but rejected before remote promotion.
- Root issue: `_build_log_fiddlehead` still built a short stem before the spiral, which visually read as the two unwanted long rods/stems.
- Claim status: rejected.

### 20260512k Status

- New local script: `assets/prepare_fern_depth_roots_20260512k.py`.
- New remote runner: `assets/run_fern_two_case_recursive_remote_20260512k.sh`.
- Fiddlehead case ids: `fiddlehead_log_spiral_pure_k`, `fiddlehead_log_spiral_pure_l`.
- Root contract: no long stem rods; main `r(theta)=r0*exp(-b*theta)` logarithmic spiral plus attached self-similar logarithmic child spirals.
- Local preflight: `results/fern_depth_roots_20260512k_preflight/fern_depth_roots_contact_sheet_20260512k.png`; all root mesh LCR rows were `1.0`.
- Remote run on `a100-2`, GPUs 4/5 only, completed 6 OBJ/preview outputs under `results/fern_two_case_recursive_remote_20260512k_pull/`.
- Metrics: occupancy LCR `1.0` for all six outputs; face LCR approximately `0.9993-0.9997`.
- Visual verdict: rejected as final. It fixed the unwanted rods, but the first contact sheet kept the decoder frame, making the output read as a flattened hard ornamental spiral. Not publication-grade.

### 20260512k Image-Conditioned Root Attempt

- New remote runner: `assets/run_fern_image_root_generation_remote_20260512k.sh`.
- Remote output: `results/fern_image_root_generation_remote_20260512k_pull/`.
- Tried low-complexity and public/CC guide images:
  - `fiddlehead_single_curl_cc0_condition_768.png`;
  - `fiddlehead_golden_spiral_ccby4_condition_1024.png`;
  - `new_fern_fronds_ccby2_condition_1024.png`.
- Visual verdict: rejected. The single-curl result decoded as a thin plane; the golden-spiral and fern-frond results decoded as dense cube-like noise volumes. These image-conditioned roots are diagnostic failures only.

### 20260512l Status

- New local script: `assets/prepare_fern_depth_roots_20260512l.py`.
- New remote runner: `assets/run_fern_two_case_recursive_remote_20260512l.sh`.
- Fiddlehead case ids: `fiddlehead_log_crozier_pure_m`, `fiddlehead_log_crozier_pure_n`.
- Main technical change: add `--restore-output-frame` in the remote runner so decoded meshes are written back in the original root frame.
- Remote run on `a100-2`, GPUs 4/5 only, completed 6 OBJ/preview outputs under `results/fern_two_case_recursive_remote_20260512l_pull/`.
- Metrics: occupancy LCR `1.0` for all six outputs; face LCR approximately `0.9993-0.9997`; outputs are clean enough by connectivity metrics.
- Visual verdict: partial success, not final. The unwanted rods are gone and the restored-frame output now reads as an upright crozier/log spiral with visible recursive small spirals at depth 2/4. However, the visual style is still too hard-tube/mechanical and not natural enough for publication-grade botanical evidence.
- Local Blender QA could not run in this environment because `blender` is not installed locally. Current QA is matplotlib contact sheets only; final paper evidence still requires controlled Blender rendering.

### Next Action

Proceed to 20260512m rather than promoting 12l. Keep the corrected contracts from 12l, but improve naturalness:

- keep a true logarithmic main spiral and no long rods;
- reduce mechanical child-loop distribution;
- make child spirals read like attached curled leaflet/crozier growth instead of metal ornament loops;
- use fewer but more organic child spirals with tapered radii and softer attachment offsets;
- optionally generate clean synthetic condition renders from the 12m root for another image-conditioned TRELLIS2 attempt, but do not reuse the failed raw natural-photo roots as positive evidence.

## 20260512o Plan

Purpose: respond to the latest visual feedback on the two fern cases.

- Fiddlehead/log-spiral case: keep the true logarithmic spiral contract and no long rods. Increase main-stem and child-stem thickness, enlarge child spirals, add welded collars at attachment points, and add depth-gated child-on-child spirals at depth 4/6.
- Compound fern/frond case: keep the elongated frond shape but avoid SLat patch-copy collapse by constructing each depth as a connected mesh-stage root before TRELLIS2/SLat passthrough naturalization. Depths are 0/2/4/6.
- Remote lanes: GPU 4/5 for two log-spiral variants; GPU 6/7 for two compound fern variants. Use only `a100-2` and GPUs 4,5,6,7.
- Promotion gate: OBJ outputs, metrics CSV/JSON, local contact sheet/render QA, and no visible major mesh collapse/fragments. Image-conditioned 12n roots remain diagnostic only due fragmentation/flatness.

## 20260512o Verdict

Completed remotely on `a100-2` with 16 OBJ/preview outputs and metrics under `results/fern_two_case_recursive_remote_20260512o_pull/`.

- Fiddlehead/log-spiral: improved over 12n. Main stem is thicker, child spirals are larger, depth 4/6 includes child-on-child curls, and no long rods are present. Metrics are stable: occupancy LCR `1.0` for all displayed depths; raw face LCR remains above roughly `0.9997`.
- Image-conditioned 12n roots remain diagnostic only: several are flat or fragmented despite some occupancy proxies looking connected.
- Long fern/frond: no mesh collapse and occupancy LCR `1.0`, but depth progression is still visually conservative. It should not yet be promoted as publication-grade visual evidence.
- Output contact sheet: `results/fern_two_case_recursive_remote_20260512o_pull/preview_contact_depth0246_20260512o.png`.

## 20260512p Plan

Purpose: keep 12o's stable log-spiral controls and make the long fern/frond depth progression more visible.

- New scripts: `assets/prepare_fern_depth_roots_20260512p.py`, `assets/run_fern_two_case_recursive_remote_20260512p.sh`.
- Fern changes: thicker rachis, longer primary pinnae, stronger secondary/tertiary pinnae at depth 4/6, wider/thicker laminae, still connected mesh-stage depth roots before SLat passthrough naturalization.
- Preflight contact sheet: `results/fern_depth_roots_20260512p_preflight/fern_depth_roots_contact_sheet_20260512p.png`.
- Remote launched on `a100-2` at 2026-05-12 21:56 CST using GPUs 4/5/6/7. PID files are under `results/fern_two_case_recursive_remote_20260512p/pids/`.
- Promotion gate remains unchanged: OBJ outputs, metrics CSV/JSON, contact-sheet/render QA, and no visible mesh collapse/fragments.

## 20260512p Verdict

Completed remotely on `a100-2` with 16 OBJ/preview outputs and metrics under `results/fern_two_case_recursive_remote_20260512p_pull/`.

- Long fern/frond: improved over 12o. `fern_mesh_frond_p` has clearer depth progression from d0 to d6, with visibly larger/wider recursive frond structure while preserving connectivity. `fern_mesh_frond_q` remains a conservative backup.
- Metrics: all 12p outputs have occupancy LCR `1.0`. Broad fern `p` raw face LCR remains roughly `0.99966-0.99987`; conservative fern `q` raw face LCR remains roughly `0.99970-0.99990`. No major collapse or large fragment failure is indicated by metrics.
- Fiddlehead/log-spiral: 12p keeps the same stable 12o log-spiral design. Current candidate remains `fiddlehead_log_surface_recursive_u/s` at depth 6, with true logarithmic main spiral, no long rods, thicker stems, larger child spirals, and child-on-child curls.
- User review bundle: `visuals/fern_two_case_user_review_20260512/` contains contact sheets, metrics CSVs, and a README with recommended paths.
- Claim gate: this is strong OBJ/contact-sheet evidence, but still not final paper/PBR evidence. Before calling it publication-grade, run controlled Blender/PBR rendering, choose final views, and optionally texture with botanical green material/guide.
