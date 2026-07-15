# Metric Table Audit - 2026-05-13

Scope: read-only audit of `paper_siga/main.tex` and the included quantitative table files requested by the user. I did not edit `main.tex` and did not run heavy GPU/training jobs.

## User Requirements Checked

- `/Users/fanta/Downloads/三部分整理稿合并分节版.md:255-283`: metrics need clear definitions, shared use across main tables/ablations, citations/explanations, and additional mesh/visual quality metrics where useful.
- `/Users/fanta/Downloads/三部分整理稿合并分节版.md:261`: current Table 3 should drop weak/non-discriminative columns such as state/projection/copy/raw components, retaining occupancy component count and LCR as core metrics.
- `/Users/fanta/Downloads/三部分整理稿合并分节版.md:271`: `C_{r0}` in Table 4 is unclear to the user and must be explained or renamed.
- `/Users/fanta/Downloads/三部分整理稿合并分节版.md:275`: all quantitative results should not include variance/std; use values only.
- `/Users/fanta/Downloads/三部分整理稿合并分节版.md:307`: experiments should not discuss PBR or GLB export.
- `/Users/fanta/Downloads/三部分整理稿合并分节版.md:336`: GLB size and generation time are unnecessary; runtime is not important for the current traditional comparison.

## Included Quantitative Tables

`main.tex` includes the requested tables here:

- Projection ablation: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex:565-573`, input file `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/projection_ablation_main_table_20260511.tex`.
- Experiment 3 sparse-latent vs mesh-space: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex:579-595`, input file `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`.
- Main selected metrics: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex:613-623`, input file `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`.
- Masked naturalization: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex:641-649`, input file `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/masked_naturalization_main_table_20260511.tex`.
- Effective resolution status: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex:652-660`, input file `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/effective_resolution_status_table_20260510.tex`.

## Findings by Table

### Projection ablation table

File: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/projection_ablation_main_table_20260511.tex`

- Still has std/variance-style entries in every data row: lines `6-10` use `$\pm$`.
- Still says `full PS-RSLG` instead of `full PS-RSLE`: line `10`.
- Metrics are mostly aligned with the execution claim, but abbreviations remain compact: line `4` uses `Occ. LCR`, `Root reach.`, `Orphan active`, `Handle survival`, `Fail rate`.
- Recommended change: regenerate/write a value-only table. If multiple seeds must be summarized, use one deterministic aggregate value per metric, not `mean ± std`; include `n=12` or `4 families x 3 seeds` in caption/body text rather than std columns. Rename `full PS-RSLG` to `full PS-RSLE`.

Source script/results located:

- Generator script: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/projection_masked_ablation_matrices_20260511.py`.
- Variant label bug source: `PROJECTION_LABELS["full_ps_rslg"] = "full PS-RSLG"` at `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/projection_masked_ablation_matrices_20260511.py:68-74`.
- Mean/std aggregation source: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/projection_masked_ablation_matrices_20260511.py:661-696`.
- `\pm` formatter and table writer: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/projection_masked_ablation_matrices_20260511.py:754-777`.
- Existing aggregate outputs: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/projection_masked_ablation_matrices_20260511/projection_ablation_meanstd_20260511.csv` and `metrics.json` in the same directory.

### Experiment 3 sparse-latent vs mesh-space table

File: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`

- No std columns.
- Still says `PS-RSLG` in rows and caption: lines `15`, `21`, `27`, `33`, and caption line `36`.
- Contains columns the user explicitly called weak/non-discriminative for current Table 3: line `9` has `State`, `Proj.`, `Copy`, and `Raw comp.`. The user requirement says to retain only occupancy component count and LCR from the old table direction and add clearer mesh/visual metrics if available.
- `Raw comp.` is a face-connectivity/export-sensitive diagnostic. It is useful as an internal caveat but should not be a main result column if the goal is a compact publication table with common metrics.
- Recommended change: rename method to `PS-RSLE`; remove `State`, `Proj.`, `Copy`, and likely `Raw comp.` from the main table; keep `Occ. comp.` and `LCR`; add selected mesh quality metrics only if they are defined in the metrics subsection and available for all rows. If raw components are retained, move to supplement or footnote as a caveat.

Source script/results located:

- Generator script: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/experiment3_build_table_20260511.py`.
- Method id/label source uses `ps_rslg` and `PS-RSLG`: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/experiment3_build_table_20260511.py:42-56`.
- Table columns are written at `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/experiment3_build_table_20260511.py:220-230`.
- Caption uses `PS-RSLG` at `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/experiment3_build_table_20260511.py:257-267`.
- Source manifest: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_master_manifest.csv`.
- A newer refreshed copy exists outside the paper include path: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/paper_metric_refresh_20260513/experiment3_sparse_latent_vs_mesh_space_table_20260513.tex`; it still has the same `PS-RSLG` labels and same table schema.

### Main selected metrics table

Current included file: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`

- No std columns.
- Does not contain `PS-RSLG`; methods are `Traditional` and `Ours`.
- `C_{r0}` and `LCR_{r0}` are partly explained in the caption: line `6` says exact surface-sampled voxel connectivity; line `10` uses the compact headers.
- However, the user explicitly did not know what `C_{r0}` means. The current caption may still be too terse because `C` is never expanded in the header. Recommended header: `Comp. r0` or `Surface voxel comp. (r0)`. Recommended caption: spell out "connected component count at radius 0" and "largest connected component ratio at radius 0".
- The caption still says `texture-export islands`: line `6`. This conflicts with the requirement to remove GLB/export framing from experiments.
- `Welded comp.` is a tolerance-based mesh diagnostic at line `10`, with tolerance described in line `6`. It is useful, but it should be named and justified as a mesh-quality/fragmentation metric, not as an export diagnostic.
- `Faces` and `Box dim.` are geometry/scale descriptors, not quality metrics. They may be retained only if needed for normalization/context; otherwise they consume main-table width without addressing the requested metric gap.

Comparison against older/remote-like nearby tables:

- Older local table: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/main_experiment_selected_metrics_table_20260511.tex`.
- Corrected local V67B table removed no std columns because the older table also had no std columns. The actual changes are selected cases/metrics: older line `8` had `Dim.` and `Faces`; corrected line `10` has `Faces`, `Welded comp.`, and `Box dim.`. Corrected row values also changed, especially L-system and IFS rows.
- Remote-like/refreshed table: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/paper_metric_refresh_20260513/main_experiment_selected_metrics_table_20260513.tex`. It is not included by `main.tex`. It differs from the included V67B table at least in the IFS/Ours row: included table line `22` reports `C_r0=1`, `LCR=1.000`, `Faces=37,274`, `Box dim.=2.071`; refreshed table line `22` reports `C_r0=6`, `LCR=0.999`, `Faces=19,454`, `Box dim.=2.111`. This needs reconciliation before paper update.

Source script/results located:

- Corrected table script: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/write_main_experiment_metrics_table_corrected_V67B_20260512.py`.
- Caption/header source: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/write_main_experiment_metrics_table_corrected_V67B_20260512.py:55-66`.
- Rows are pulled from surface and mesh CSVs by labels at `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/write_main_experiment_metrics_table_corrected_V67B_20260512.py:70-82`.
- Corrected metric results: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/main_experiment_case_metrics_20260511/main_experiment_selected_corrected_V67B_metrics_20260512/main_experiment_selected_surface_metrics_occ64.csv` and `main_experiment_selected_recursive_mesh_metrics.csv`.
- Manifest for corrected cases: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/main_experiment_case_metrics_20260511/main_experiment_traditional_vs_ours_manifest_corrected_V67B_20260512.json`.

### Masked naturalization table

File: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/masked_naturalization_main_table_20260511.tex`

- Still has std/variance-style entries in every data row: lines `6-11` use `$\pm$`.
- Metric names are unclear or proxy-like: line `4` uses `Rough.`, `Normal`, `Artifacts`, `Drift`, `Quality`, and `Fail`. The caption in `main.tex:641-645` says these are deterministic surface/trace proxies, but the table itself does not define what is being measured.
- No `PS-RSLG` label in this table.
- No explicit GLB/runtime/export-heavy metric column, but `Quality` is called `rendered-asset quality proxy` in `main.tex:631` and `main.tex:641-645`; it needs a precise definition or should be removed/renamed.
- Recommended change: value-only entries; rename columns to defined metric names; ensure they match the common metric taxonomy in the metrics subsection. Consider reducing to projection-validity metrics plus 2-3 mesh-quality metrics shared with other tables, e.g. local roughness, normal consistency, artifact/fragment score, handle survival/fail.

Source script/results located:

- Same generator script as projection table: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/projection_masked_ablation_matrices_20260511.py`.
- Mean/std aggregation source: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/projection_masked_ablation_matrices_20260511.py:699-738`.
- `\pm` writer: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/projection_masked_ablation_matrices_20260511.py:780-811`.
- Existing aggregate outputs: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/projection_masked_ablation_matrices_20260511/masked_naturalization_projection_meanstd_20260511.csv` and `metrics.json`.

### Effective resolution status table

File: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/effective_resolution_status_table_20260510.tex`

- This included file is effectively empty/commented placeholder content: lines `1-7` are commented figure boilerplate.
- `main.tex:660` still inputs it, so the paper includes a no-op placeholder where a table is expected.
- Recommended change: either remove the `\input` from the experiment flow or replace it with a real, value-only table after the metric is defined. Per the user requirement, the current "effective resolution" discussion is supposed to be deleted or converted into controllability, so this table should likely be removed from the main quantitative table set.

## Main Text Issues Around Tables

- `main.tex:581`, `main.tex:601`, `main.tex:609`, `main.tex:619`, `main.tex:627-631`, `main.tex:637`, `main.tex:674`, `main.tex:682`, `main.tex:686`, and `main.tex:695` still discuss texture/PBR/GLB/export. This conflicts with `/Users/fanta/Downloads/三部分整理稿合并分节版.md:307`.
- `main.tex:631` still reports `mean ± std` values inline for naturalization, even if the table is later fixed.
- `main.tex:627-631` still frames the subsection as `Naturalization, Export, and Effective Resolution`, while user requirements ask to delete/replace neutralization/effective-resolution content with controllability (`/Users/fanta/Downloads/三部分整理稿合并分节版.md:303-307`).
- `main.tex:551` defines a broad metrics set including texture-latent compatibility and texture/PBR metrics; this should be narrowed for the main paper metric story.

## Recommended Table Changes

1. Standardize method name to `PS-RSLE` everywhere in tables and table-generation scripts. The paper text already uses PS-RSLE, but table files/scripts still use `PS-RSLG`.
2. Remove `\pm`/std from projection and masked-naturalization tables. Keep single aggregate values only, with sample count in caption or text.
3. Rename `C_{r0}` to an expanded header such as `Comp. r0` or `Surface comp. r0`; define as connected component count under the radius-0 surface-sampled voxel graph. Define `LCR_{r0}` as largest connected component ratio under the same graph.
4. Remove export-specific wording from captions, especially `texture-export islands` in the main selected metrics table. Use neutral language such as "one-voxel dilation for aliasing/tiny surface islands."
5. For Experiment 3, remove `State`, `Proj.`, `Copy`, and likely `Raw comp.` from the main table. Keep `Occ. comp.` and `LCR`, and add only clearly defined common mesh/visual metrics if available across all rows.
6. Treat raw/welded face components as diagnostics, not primary structural metrics. If kept, move raw component details to supplementary tables.
7. Remove or replace `effective_resolution_status_table_20260510.tex`; the current included file is a commented placeholder.
8. Reconcile the included V67B main selected metrics table with the newer refreshed table under `results/paper_metric_refresh_20260513`, especially the IFS/Ours row.

## Suggested Publication Metric Set

- Structural connectivity: occupancy or surface-voxel component count and LCR, with radius/graph specified.
- Recursive-state validity: root reachability, orphan active handles, handle survival, fail rate for projection/trace ablations.
- Mesh quality/fragmentation: welded/tolerance component count only after defining tolerance and normalization; optionally non-manifold/watertight/degenerate-face metrics if available consistently.
- Visual/alignment metrics: CLIP/GPT-4o/aesthetic metrics only if actually computed and defined; do not leave proxy names such as `Quality` without protocol.

