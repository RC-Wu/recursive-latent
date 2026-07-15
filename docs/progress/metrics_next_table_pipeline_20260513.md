# Metrics Next Table Pipeline - 2026-05-13

Scope: METRICS TABLE PIPELINE subagent report. I inspected existing metric outputs and source CSV/JSONs for projection ablation, masked naturalization, traditional-vs-PS-RSLE, and Experiment 3. I did not edit `paper_siga/main.tex`, stage, commit, or push.

## Fastest Valuable Next Step

Generate and integrate a value-only projection ablation table first, then add the mesh-enrichment outputs as appendix diagnostics. This is the best immediate move because projection ablation is closest to the paper's main claim: per-depth admissible executable state. Mesh/render/topology metrics should remain diagnostics/caveats, not topology proof.

The existing value-only CSV already exists:

- `results/paper_metric_refresh_20260513/projection_ablation_meanonly_20260513.csv`
- `results/paper_metric_refresh_20260513/projection_ablation_meanonly_20260513.tex`

The one required content fix before paper integration is to rename `full PS-RSLG` to `full PS-RSLE`.

Recommended main-ready schema:

| Projection variant | Occ. LCR | Root reach. | Orphan active | Handle survival | Committed pass |
|---|---:|---:|---:|---:|---:|
| no projection | 0.898 | 0.504 | 3.667 | 0.504 | 0.000 |
| final-only | 0.995 | 0.504 | 3.667 | 0.504 | 0.000 |
| per-depth prune-only | 0.964 | 1.000 | 0.000 | 0.782 | 0.250 |
| per-depth connector-aware | 0.995 | 1.000 | 0.000 | 1.000 | 0.750 |
| full PS-RSLE | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 |

Use `Committed pass = 1 - failure_rate_mean`. Do not include std columns. Put `n=12` runs, `3` seeds, `4` tasks in the caption or prose.

## Source Files Inspected

Metric scripts:

- `assets/mesh_metric_enrichment_20260513.py`
- `assets/projection_masked_ablation_matrices_20260511.py`
- `assets/experiment3_build_table_20260511.py`
- `assets/compute_main_experiment_selected_metrics_20260511.py`
- `assets/write_main_experiment_metrics_table_corrected_V67B_20260512.py`

Primary outputs:

- `results/metric_enrichment_20260513/priority_mesh_metric_enrichment_20260513.csv`
- `results/metric_enrichment_20260513/priority_mesh_metric_enrichment_20260513.json`
- `results/metric_enrichment_20260513/metric_enrichment_block_summary_20260513.csv`
- `results/metric_enrichment_20260513/masked_naturalization_topology_summary_20260513.csv`
- `results/projection_masked_ablation_matrices_20260511/metrics.csv`
- `results/projection_masked_ablation_matrices_20260511/projection_ablation_meanstd_20260511.csv`
- `results/paper_metric_refresh_20260513/projection_ablation_meanonly_20260513.csv`
- `results/paper_metric_refresh_20260513/masked_naturalization_meanonly_20260513.csv`
- `results/paper_metric_refresh_20260513/experiment3_compact_table_20260513.csv`
- `results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_master_manifest.csv`
- `results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_compact_table_20260511.csv`
- `results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_ps_rslg_metric_rows_20260511.csv`
- `results/publication_hunyuan_text_root_meshspace_20260511/hunyuan_text_root_meshspace_metrics.csv`
- `results/strict_visual_matched_cases_V24_priority_rerun_20260510_dryrun/manifest.csv`
- `results/strict_visual_matched_cases_V24_priority_rerun_20260510_dryrun/initial_metrics.csv`
- `results/real_case_ablation_inputs_20260512/manifest.csv`
- `results/masked_naturalization_ablation_20260510_seed20260512/manifest.csv`

Current paper/draft tables inspected:

- `paper_siga/drafts/projection_ablation_main_table_20260511.tex`
- `paper_siga/drafts/masked_naturalization_main_table_20260511.tex`
- `paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`
- `paper_siga/drafts/experiment3_mesh_enrichment_20260513.tex`
- `paper_siga/figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`

Progress/audit docs inspected:

- `docs/progress/ps_rsle_revision_metric_parallel_plan_20260513.md`
- `docs/progress/ps_rsle_revision_metric_parallel_progress_20260513.md`
- `docs/progress/metric_table_audit_20260513_cont.md`
- `docs/progress/metric_asset_audit_20260513.md`
- `docs/progress/metric_enrichment_integration_notes_20260513.md`

## Exact Regeneration Commands

Regenerate CPU mesh enrichment:

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
python3 assets/mesh_metric_enrichment_20260513.py \
  --priority-defaults \
  --scan-priority-dirs \
  --out-dir results/metric_enrichment_20260513 \
  --prefix priority_mesh_metric_enrichment_20260513 \
  --weld-tolerance 0.002 \
  --max-faces 750000
python3 -m pytest results/metric_enrichment_20260513/test_mesh_metric_enrichment.py -q
```

Regenerate Experiment 3 compact CSV/TEX without touching `paper_siga`:

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
python3 assets/experiment3_build_table_20260511.py \
  --manifest results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_master_manifest.csv \
  --out-csv results/paper_metric_refresh_20260513/experiment3_compact_table_20260513.csv \
  --out-json results/paper_metric_refresh_20260513/experiment3_compact_table_20260513.json \
  --out-tex results/paper_metric_refresh_20260513/experiment3_sparse_latent_vs_mesh_space_table_20260513.tex \
  --out-supp-tex results/paper_metric_refresh_20260513/experiment3_sparse_latent_vs_mesh_space_table_supplement_20260513.tex
```

Regenerate projection and masked-naturalization matrices in a disjoint path. This is CPU-local but may recreate visual assets:

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
python3 assets/projection_masked_ablation_matrices_20260511.py \
  --out-dir results/paper_metric_refresh_20260513/projection_masked_ablation_matrices \
  --visual-dir results/paper_metric_refresh_20260513/projection_masked_ablation_visuals \
  --drafts-dir results/paper_metric_refresh_20260513/drafts \
  --figures-dir results/paper_metric_refresh_20260513/figures \
  --status-doc results/paper_metric_refresh_20260513/projection_masked_ablation_status.md
```

Regenerate traditional-vs-PS-RSLE selected metrics in a disjoint path:

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
python3 assets/compute_main_experiment_selected_metrics_20260511.py \
  --manifest results/main_experiment_case_metrics_20260511/main_experiment_traditional_vs_ours_manifest_corrected_V67B_20260512.json \
  --out-dir results/paper_metric_refresh_20260513/main_experiment_selected_corrected_V67B_metrics \
  --resolution 64 --sample-count 50000 --seed 20260511 --weld-tolerance 0.002
python3 assets/write_main_experiment_metrics_table_corrected_V67B_20260512.py \
  --surface-csv results/paper_metric_refresh_20260513/main_experiment_selected_corrected_V67B_metrics/main_experiment_selected_surface_metrics_occ64.csv \
  --mesh-csv results/paper_metric_refresh_20260513/main_experiment_selected_corrected_V67B_metrics/main_experiment_selected_recursive_mesh_metrics.csv \
  --out results/paper_metric_refresh_20260513/main_experiment_selected_metrics_table_meanonly_20260513.tex
```

## Experiment 3 Recommendation

Keep the main Experiment 3 table compact and claim-aligned. Recommended main schema:

| Case | Method | Occ. comp. | LCR | Status |
|---|---|---:|---:|---|

Use `results/paper_metric_refresh_20260513/experiment3_compact_table_20260513.csv` as source, but before paper integration:

- Rename `PS-RSLG` to `PS-RSLE`.
- Remove `state_update`, `projection`, `copy_rep`, and `raw_components` from the main table.
- Keep `raw_components` only in appendix/caveat tables.

Example rows already available from the CSV:

| Case | Method | Occ. comp. | LCR | Status |
|---|---|---:|---:|---|
| tree crown | Trellis2 one-shot | 19 | 0.978 | one-shot control |
| tree crown | Trellis2 latent-copy | 11 | 0.995 | copy-state control |
| tree crown | Trellis2 root+mesh-copy | 32 | 0.993 | copy-state control |
| tree crown | Hunyuan root+mesh-copy | 40 | 0.998 | copy-state control |
| tree crown | PS-RSLE | 1 | 1.000 | selected positive |
| bismuth | Trellis2 root+mesh-copy | 53 | 0.112 | copy-state control |
| bismuth | PS-RSLE | 1 | 1.000 | selected positive |
| coral | Trellis2 root+mesh-copy | 43 | 0.990 | copy-state control |
| coral | PS-RSLE | 1 | 1.000 | selected positive |

Do not use raw face-component counts as a main success metric here. They are sensitive to mesh export tessellation and stitching, and the enrichment shows all Experiment 3 priority rows are non-watertight.

## Masked Naturalization Recommendation

For the main table, use the existing value-only mean-only CSV only after renaming columns to defined metrics:

Source: `results/paper_metric_refresh_20260513/masked_naturalization_meanonly_20260513.csv`

Recommended schema:

| Naturalization variant | Roughness down | Normal consistency up | Artifact index down | Topology drift down | Handle survival | Committed pass |
|---|---:|---:|---:|---:|---:|---:|
| rule-only | 50.00 | 0.000 | 0.487 | 0.203 | 0.500 | 0.000 |
| masked/no-proj | 47.45 | 0.003 | 0.488 | 0.201 | 0.500 | 0.000 |
| no-N/+proj | 16.94 | 0.597 | 0.348 | 0.000 | 1.000 | 0.750 |
| weak/+proj | 14.11 | 0.664 | 0.228 | 0.088 | 1.000 | 1.000 |
| masked/+proj | 13.92 | 0.669 | 0.227 | 0.090 | 1.000 | 1.000 |
| global/+proj | 13.58 | 0.677 | 0.229 | 0.090 | 1.000 | 1.000 |

Use `Committed pass = 1 - failure_rate_mean`. Consider dropping `rendered_asset_quality_mean` from the main table unless the metric protocol is defined in text; it is a proxy and can be misleading if read as human visual quality.

Appendix-only topology audit for masked naturalization:

Source: `results/metric_enrichment_20260513/masked_naturalization_topology_summary_20260513.csv`

| Variant | Raw comp. med. | Weld comp. med. | Boundary med. | Nonmanifold med. | Quality med. | Watertight |
|---|---:|---:|---:|---:|---:|---:|
| raw grammar proposal | 16 | 16 | 0 | 0 | 0.703 | 3/3 |
| final-only projection repair | 4 | 4 | 0 | 0 | 0.690 | 3/3 |
| per-depth projection | 4 | 4 | 0 | 0 | 0.688 | 3/3 |
| per-depth weak naturalization | 1 | 1 | 0 | 0 | 0.688 | 3/3 |
| per-depth masked naturalization | 1 | 1 | 0 | 0 | 0.691 | 3/3 |
| per-depth global naturalization | 1 | 1 | 0 | 0 | 0.694 | 3/3 |

This audit supports continuity as a diagnostic, but it does not distinguish masked from global topology-wise. The main preference for masked local naturalization should remain locality, old-state preservation, and quality/artifact proxies, not topology proof.

## Traditional-vs-PS-RSLE Recommendation

For the current traditional comparison table, the immediate table-pipeline action is not to add new raw topology columns. Instead:

- Expand `C_{r0}` to a readable header such as `Surface comp. r0`.
- Define it as connected component count under the radius-0 surface-sampled voxel graph.
- Define `LCR_{r0}` as largest connected component ratio under the same graph.
- Remove export/PBR wording from captions.
- Reconcile the included V67B table with `results/paper_metric_refresh_20260513/main_experiment_selected_metrics_table_20260513.tex`; the IFS/Ours row differs between the included table and refreshed table.

Do not add std columns.

## Mesh-Enrichment Appendix Audit

The mesh enrichment measured 107/120 priority assets and skipped 13 oversized OBJ rows using the 750,000-face guard.

Source: `results/metric_enrichment_20260513/metric_enrichment_block_summary_20260513.csv`

| Block | Requested | Measured | Skipped | Welded single | Watertight | Boundary med. | Nonmanifold med. | Triangle quality med. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Experiment 3 priority assets | 65 | 52 | 13 | 1 | 0 | 154,193.5 | 0.0 | 0.727 |
| V24 main-comparison scaffolds | 15 | 15 | 0 | 0 | 0 | 934.0 | 944.0 | 0.566 |
| Real-case projection/naturalization inputs | 22 | 22 | 0 | 8 | 8 | 1,892.5 | 0.0 | 0.643 |
| Masked-naturalization manifest inputs | 18 | 18 | 0 | 9 | 18 | 0.0 | 0.0 | 0.692 |

Use this as an appendix audit or one caveat sentence only. It is not a main topology result.

## Misleading Metrics to Flag

- Raw face-component count: useful for export/fragmentation audit, misleading as topology proof.
- Welded component count: tolerance-dependent; useful only with `weld_tolerance=0.002` stated.
- Watertight/volume/compactness: absent for most Experiment 3 and traditional rows; do not compare methods by volume.
- Triangle quality: PS-RSLE is not uniformly better, so do not frame it as a win metric.
- `rendered_asset_quality_mean`: proxy name is too broad unless the protocol is defined.
- `raw_components` in Experiment 3: should be appendix-only because it depends on mesh representation and loader behavior.
- `GLB` size, runtime, export/PBR status: not useful for the current claim and conflicts with the requested main story.

## Bottom Line

Advance the metrics track now by producing a claim-aligned, value-only projection ablation table with `Committed pass`, and push mesh topology enrichment to appendix/caveat tables. This gives the paper a first-class quantitative metrics workstream without overstating mesh diagnostics as proof of topology.
