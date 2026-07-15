# Untracked Asset Triage - 2026-05-13

Scope: `paper_siga` untracked figures/assets triage for the PS-RSLE revision. Read-only inspection except for this report.

## Summary

- `main.tex` is modified, but every active `\includegraphics{...}` and `\input{...}` path in the current file exists and is already tracked.
- There are no currently referenced untracked figures/tables that must be added for the present `main.tex`.
- The user-mentioned stickcase figure is active at `main.tex:280` as `figures/personal/stickcase.pdf`; it exists and is tracked.
- The active corrected metrics table is `figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex` at `main.tex:623`; it exists and is tracked.
- The untracked `drafts/publication_ablation_effective_resolution_status_20260510.tex`, `drafts/ablation_and_resolution_status_tables_20260510.tex`, and `figures/main_experiment_selected_metrics_table_20260511.tex` are not active in current `main.tex`.

## Commands Used

- `git status --short`
- `git ls-files --others --exclude-standard`
- Active-reference extraction from `main.tex` for `\includegraphics{...}` and `\input{...}`, ignoring commented lines.
- Existence/tracking check for each active referenced path.

## Currently Referenced and Must Be Tracked

All active current-main references are already tracked. No untracked asset falls in this category.

Notable active tracked references:

- `figures/personal/stickcase.pdf` - exists, tracked.
- `figures/personal/sparse_latent.pdf` - exists, tracked.
- `figures/personal/main_method.pdf` - exists, tracked.
- `figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex` - exists, tracked.
- `figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.png` - exists, tracked.
- `figures/ablation_pptx_20260511/projection_ablation_pptx_20260511.pdf` - exists, tracked.
- `figures/ablation_pptx_20260511/masked_naturalization_ablation_pptx_20260511.pdf` - exists, tracked.

The full active-reference check returned only `TRACKED` lines and no `UNTRACKED` or `MISSING` lines.

## Likely Draft / QA / Status: Do Not Upload Now

These are untracked and appear to be generated previews, QA artifacts, editable slide sources, export summaries, manifests, or draft status tables. They should not be uploaded unless a later paper edit explicitly references them.

- `_preview_pages/` - many page previews and current-ablation QA PNG/PDF renders; about 38 MB.
- `.overleaf_files` - Overleaf helper state.
- `overleaf_upload_20260509.zip` - stale upload bundle.
- `docs/progress/text_structure_patch_plan_20260513.md` - planning doc, not paper asset.
- `figures/ablation_pptx_20260512/` - newer ablation publication PDFs/PPTX, panel PNGs, JSON manifests/summaries; current `main.tex` still uses the tracked `figures/ablation_pptx_20260511/...` PDFs.
- `figures/method_diagram_pptx_20260512/` - PPTX sources, preview PNGs, component assets, JSON export summaries. The current paper uses tracked `figures/personal/*.pdf` and tracked `figures/method_projection_admissibility_gate_20260510.pdf`, not these untracked PPTX sources.
- `figures/seam_aware_pbr_qa_pptx_20260511/` - QA PPTX and summary JSON.
- `figures/traditional_vs_psrslg_one_to_one_pptx_20260510/` - PPTX previews/summaries, not active in current `main.tex`.
- `figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_QA*.png/json` - QA variants and metadata for main experiment matrix; current active image is the tracked non-QA `figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.png`.
- Contact/status sheets such as `figures/matrix_test_one_contact_sheet.png`, `figures/mesh_based_visual_status_contact_sheet*.png`, `figures/textured_glb_preview_contact_sheet.png`, and `figures/mesh_result_selection_contact_20260509.png`.
- Cache/repair QA files such as `figures/cache_repair_texture_qa_20260509.*`, `figures/cache_selected_texture_qa_20260509.*`, and `figures/connected_best_expansion_texture_qa_20260509.png`.
- Untracked draft/status tables:
  - `drafts/ablation_and_resolution_status_tables_20260510.tex`
  - `drafts/publication_ablation_effective_resolution_status_20260510.tex`
  - `drafts/experiment3_sparse_latent_vs_mesh_space_table_supplement_20260511.tex`

The existing text-structure plan also warns not to include the effective-resolution placeholder table in main text unless rewritten as a real control metric table. Current `main.tex` no longer inputs the tracked `drafts/effective_resolution_status_table_20260510.tex`, and the two untracked effective/status variants are not referenced.

## Potentially Useful But Not Yet Referenced

These untracked files look like possible alternate figures, polished candidates, or source/export sidecars. Keep locally for author decision, but do not upload now because current `main.tex` does not reference them.

- Alternate method diagram exports:
  - `figures/method_diagram_drafts_20260510/*.pdf/png/svg`
  - root-level untracked method diagram PNG/SVG variants such as `figures/method_ps_rslg_overview_publication_20260510.png/svg`, `figures/method_masked_local_naturalization_20260510.*`, `figures/method_trellis2_substrate_prelim_20260510.*`
- Alternate main-experiment matrices:
  - `figures/main_experiment_traditional_vs_ours_white_zoom_matrix_20260511.png`
  - `figures/main_experiment_traditional_vs_ours_white_zoom_matrix_cropped_20260511.png`
  - QA variants with `v23`, `v59`, `v63B`, `v63C`, and `flip_v63C`
- Earlier or alternate metric table:
  - `figures/main_experiment_selected_metrics_table_20260511.tex`
  - This is untracked and not referenced; current main uses tracked corrected `V67B`.
- Alternate showcase/rerun visuals:
  - `figures/bismuth_*`
  - `figures/coral_*` except currently tracked active references
  - `figures/depth_parameter_*` unreferenced PNG/PDF/PY variants
  - `figures/pyrite_depth_textured_showcase_20260509.png`
  - `figures/porous_mineral_depth_textured_showcase_20260509.*`
  - `figures/vine_depth_textured_showcase_20260509.png`
  - `figures/standard_pure_white_selected_textured_contact_v2_20260509.*`
  - `figures/ralph_positive_method_texture_contact_pure_white_20260509.pdf`
- Alternate baseline/visual-control assets:
  - `figures/gen3d_baseline_geometry_control_clean_20260510.png`
  - `figures/gen3d_baseline_overview_clean_20260510.png`
  - `figures/traditional_baseline_texture_20260509.png`
  - `figures/traditional_baseline_texture_rerun1554_20260509.png` (PNG; active paper uses tracked PDF)
- Alternate metric plots and source data:
  - `figures/space_competition_depth_curves_20260508.csv`
  - `figures/space_competition_depth_curves_compact_20260508.*`
  - `figures/space_competition_depth_curves_faces_20260508.*`
  - `figures/space_competition_depth_curves_vertices_20260508.*`
  - `figures/space_competition_metrics_20260509.png`
  - `figures/symmetry_orbit_metrics_20260509.*`
  - `figures/projection_ablation_lcr_components_20260508.*`

## Specific Checks Requested

### Stickcase Figure

- Referenced in current `main.tex`: yes, `main.tex:280`.
- Path: `figures/personal/stickcase.pdf`.
- Exists: yes.
- Git status: tracked.
- Upload implication: no untracked asset needed for this figure.

### Corrected Metrics Table

- Referenced in current `main.tex`: yes, `main.tex:623`.
- Path: `figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`.
- Exists: yes.
- Git status: tracked.
- Upload implication: no untracked metrics table needed for current main text.

### Effective / Resolution Tables

- `drafts/effective_resolution_status_table_20260510.tex` is tracked but not referenced by current `main.tex`.
- `drafts/publication_ablation_effective_resolution_status_20260510.tex` is untracked and not referenced.
- `drafts/ablation_and_resolution_status_tables_20260510.tex` is untracked and not referenced.
- Upload implication: do not upload effective-resolution/status placeholder tables now unless the paper text is explicitly changed to include a vetted table.

## Urgent Missing Referenced File Risk

No urgent missing referenced file risk found from current `main.tex`: every active figure/table input exists and is tracked.

The main practical risk is accidentally uploading large untracked QA/generated directories or stale draft tables. The safest upload set for the current paper is the tracked repository content plus the modified `main.tex`, not the untracked asset pile.
