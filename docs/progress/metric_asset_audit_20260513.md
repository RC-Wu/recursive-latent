# Metric Asset Audit 2026-05-13

Scope: subagent 1, read-only audit plus disjoint outputs. `paper_siga/main.tex` was not modified. Table numbering below follows the current `main.tex` inclusion order and the user request; actual final numbering may change when the main thread restructures experiments.

## Generated Files

- Asset inventory CSV: `results/paper_metric_refresh_20260513/table_asset_inventory_20260513.csv` (210 rows)
- This report: `docs/progress/metric_asset_audit_20260513.md`

## Current Table Assets

### Main traditional-target comparison / current `tab:main-experiment-selected-metrics`

- Tex: `paper_siga/figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`
- Source manifest: `results/main_experiment_case_metrics_20260511/main_experiment_traditional_vs_ours_manifest_corrected_V67B_20260512.json`
- Surface CSV/JSON: `results/main_experiment_case_metrics_20260511/main_experiment_selected_corrected_V67B_metrics_20260512/main_experiment_selected_surface_metrics_occ64.{csv,json}`
- Mesh CSV/JSON: `results/main_experiment_case_metrics_20260511/main_experiment_selected_corrected_V67B_metrics_20260512/main_experiment_selected_recursive_mesh_metrics.{csv,json}`
- Scripts: `assets/compute_main_experiment_selected_metrics_20260511.py`, `assets/write_main_experiment_metrics_table_corrected_V67B_20260512.py`
- Row assets: see inventory rows with table=`main_traditional_target_current_tab_main_experiment_selected_metrics`; includes traditional GLB/OBJ and ours GLB paths for SC, L-system, DLA/frontier, IFS/transform.

### Experiment 3 sparse-latent vs mesh-space / likely current Table 3 target

- Tex: `paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`
- Compact CSV/JSON: `results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_compact_table_20260511.{csv,json}`
- Master manifest: `results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_master_manifest.csv`
- Method metric sources include `experiment3_trellis2_baseline_metrics.csv`, `trellis2_generatedroot_meshcopy/trellis2_generatedroot_meshcopy_metrics.csv`, `experiment3_ps_rslg_metric_rows_20260511.csv`, and Hunyuan metric rows from `results/remote_pull_hunyuan_text_root_meshspace_20260511/hunyuan_text_root_meshspace_metrics.csv`.
- Scripts: `assets/experiment3_build_table_20260511.py`, plus existing metric loader `assets/recursive_growth_mesh_metrics.py`.
- Row assets: see inventory rows with table=`experiment3_sparse_latent_vs_mesh_space_current_table3_candidate`.

### Projection ablation

- Tex: `paper_siga/drafts/projection_ablation_main_table_20260511.tex`
- CSV/JSON: `results/projection_masked_ablation_matrices_20260511/manifest.{csv,json}`, `metrics.{csv,json}`, `projection_ablation_meanstd_20260511.csv`, `summary.json`
- Visual manifest: `paper_siga/figures/ablation_pptx_20260511/projection_ablation_visual_manifest_20260511.json`
- Script: `assets/projection_masked_ablation_matrices_20260511.py`
- Row meshes: local OBJ paths under `results/projection_masked_ablation_matrices_20260511/projection/<task>/seed_<seed>/<variant>/mesh.obj`; see inventory rows with table=`projection_ablation_current_table`.

### Masked naturalization ablation

- Tex: `paper_siga/drafts/masked_naturalization_main_table_20260511.tex`
- CSV/JSON: same matrix directory as projection, especially `masked_naturalization_projection_meanstd_20260511.csv` and `metrics.{csv,json}`
- Visual manifest: `paper_siga/figures/ablation_pptx_20260511/masked_naturalization_visual_manifest_20260511.json`
- Script: `assets/projection_masked_ablation_matrices_20260511.py`
- Row meshes: local OBJ paths under `results/projection_masked_ablation_matrices_20260511/naturalization/<task>/seed_<seed>/<variant>/mesh.obj`; see inventory rows with table=`masked_naturalization_ablation_current_table`.

## Metric Feasibility

- Fast and already supported: occupancy component count/LCR via `assets/recursive_growth_mesh_metrics.py` for vertex occupancy and `assets/batch_surface_voxel_metrics_20260509.py` / `assets/surface_voxel_connectivity_20260509.py` for surface-sampled `components_r0/r1/r2` and `lcr_r0/r1/r2`.
- Fast and already supported: welded component count via `assets/recursive_growth_mesh_metrics.py --weld-tolerance 0.002`; face count and raw face component count are also available.
- Fast but not yet in a general loader script: non-manifold edge count and boundary edge count. These can be added as a small `trimesh` diagnostic or computed from face edge incidence, but I did not add a new script because existing code should be preferred and this task was read-only-first.
- Existing proxy but currently ablation-specific: roughness / local artifact proxy / normal consistency / mesh quality proxy are computed by `assets/projection_masked_ablation_matrices_20260511.py` for Experiment 4. They are not yet generalized to arbitrary GLB/OBJ rows in Tables 3/4.
- CLIP is feasible as a lightweight render-based auxiliary metric: `assets/multiview_clip_prompt_metrics_20260510.py` exists and previous outputs are in `results/baseline_one_to_one_clip_metrics_20260510/` and `results/visual_semantic_metrics_20260510/`. It uses cached `openai/clip-vit-base-patch32` if available and CPU/CUDA automatically. Needs prompt standardization before entering main tables.
- Aesthetic score: no closed local script/result found beyond review notes; would require selecting/installing a model and is not quick-safe for the paper tables today.
- GPT-4o visual columns: feasible only through external API/manual eval, not reproducible/local; keep controlled or omit from main quantitative tables for now.

## Recommended Unified Columns

Use compact deterministic columns and no standard deviations:

1. `C_r0`: surface-sampled occupancy component count at radius 0.
2. `LCR_r0`: largest-component ratio at radius 0.
3. `C_r1`: one-voxel dilated component count, useful for aliasing/tiny export islands.
4. `Faces`: face count.
5. `Welded comp.`: tolerance-welded component count, tolerance 0.002 unless the main thread changes protocol.
6. Optional `Rough.` or `Artifacts`: only for naturalization/local-quality ablation unless generalized across all rows.
7. Optional `CLIP`: only if the same render protocol and prompts are fixed for every row in that table.

Do not include `std`, GLB size, runtime, broad PBR/export status, or file size in the main quantitative tables.

## Current Table-Column Problems

- `paper_siga/drafts/projection_ablation_main_table_20260511.tex` and `paper_siga/drafts/masked_naturalization_main_table_20260511.tex` currently contain `\pm` std values, conflicting with the user request. Regenerate or post-process to mean-only before integration.
- `paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex` still contains old columns `State`, `Proj.`, `Copy`, and raw component emphasis. The user specifically said Table 3 should keep occupancy component count and LCR from the old table and add better mesh/visual metrics.
- Current main traditional-target table uses `Box dim.`; it is computable but less central than boundary/non-manifold or roughness proxies. Consider dropping it if width is tight.
- `C_{r0}` should be expanded in the metrics text as surface-sampled voxel occupancy component count; it is not self-explanatory.

## Runnable Commands

Recompute main traditional-target metrics and tex in a disjoint output:

```bash
python3 assets/compute_main_experiment_selected_metrics_20260511.py \
  --manifest results/main_experiment_case_metrics_20260511/main_experiment_traditional_vs_ours_manifest_corrected_V67B_20260512.json \
  --out-dir results/paper_metric_refresh_20260513/main_experiment_selected_corrected_V67B_metrics \
  --resolution 64 --sample-count 50000 --seed 20260511 --weld-tolerance 0.002
python3 assets/write_main_experiment_metrics_table_corrected_V67B_20260512.py \
  --surface-csv results/paper_metric_refresh_20260513/main_experiment_selected_corrected_V67B_metrics/main_experiment_selected_surface_metrics_occ64.csv \
  --mesh-csv results/paper_metric_refresh_20260513/main_experiment_selected_corrected_V67B_metrics/main_experiment_selected_recursive_mesh_metrics.csv \
  --out results/paper_metric_refresh_20260513/main_experiment_selected_metrics_table_meanonly_20260513.tex
```

Rebuild Experiment 3 compact CSV/TEX without touching `paper_siga`:

```bash
python3 assets/experiment3_build_table_20260511.py \
  --manifest results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_master_manifest.csv \
  --out-csv results/paper_metric_refresh_20260513/experiment3_compact_table_20260513.csv \
  --out-json results/paper_metric_refresh_20260513/experiment3_compact_table_20260513.json \
  --out-tex results/paper_metric_refresh_20260513/experiment3_sparse_latent_vs_mesh_space_table_20260513.tex \
  --out-supp-tex results/paper_metric_refresh_20260513/experiment3_sparse_latent_vs_mesh_space_table_supplement_20260513.tex
```

Recompute projection/masked-naturalization matrices in a disjoint path. This is local CPU and may regenerate many PNG/PDF visual assets; run only if needed:

```bash
python3 assets/projection_masked_ablation_matrices_20260511.py \
  --out-dir results/paper_metric_refresh_20260513/projection_masked_ablation_matrices \
  --visual-dir results/paper_metric_refresh_20260513/projection_masked_ablation_visuals \
  --drafts-dir results/paper_metric_refresh_20260513/drafts \
  --figures-dir results/paper_metric_refresh_20260513/figures \
  --status-doc results/paper_metric_refresh_20260513/projection_masked_ablation_status.md
```

Run existing mesh metrics for arbitrary assets:

```bash
python3 assets/recursive_growth_mesh_metrics.py \
  --case label=path/to/asset.glb \
  --occupancy-resolution 64 --weld-tolerance 0.002 --primary-connectivity occupancy \
  --out-json results/paper_metric_refresh_20260513/example_metrics.json \
  --out-csv results/paper_metric_refresh_20260513/example_metrics.csv
```

Run existing CLIP metric on already-rendered PNGs:

```bash
python3 assets/multiview_clip_prompt_metrics_20260510.py \
  --case-file results/visual_semantic_metrics_20260510/baseline_one_to_one_clip_cases.txt \
  --render-dir <render_png_dir> \
  --out-prefix results/paper_metric_refresh_20260513/multiview_clip_prompt_scores
```

## Blockers / Risks

- No universal non-manifold/boundary-edge metric is currently wired into the table-generation scripts.
- Roughness/artifact metrics exist for synthetic ablation meshes only; applying them to all GLB/OBJ tables requires generalization and validation.
- CLIP has existing code/results but prompt and view protocols must be standardized before adding a column; aesthetic/GPT-4o are not local reproducible metrics at present.
- Current projection and naturalization tables violate the no-std requirement.
- The repository root is not a git repository in this checkout, so I could not use `git status` to distinguish my files from pre-existing untracked files.

## Inventory Counts

- `experiment3_sparse_latent_vs_mesh_space_current_table3_candidate`: 20 rows
- `main_traditional_target_current_tab_main_experiment_selected_metrics`: 8 rows
- `masked_naturalization_ablation_current_table`: 120 rows
- `projection_ablation_current_table`: 60 rows
- `visual_semantic_aux_existing`: 2 rows
