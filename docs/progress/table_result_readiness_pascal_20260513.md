# Table Result Readiness Audit - Pascal - 2026-05-13

Scope: audit of existing quantitative assets under `results/`, `paper_siga/drafts/`, `paper_siga/figures/*metrics*`, and manifest/CSV files. I did not edit `paper_siga/main.tex` and did not push. The only write in this pass is this progress report.

## Executive Status

Several quantitative tables are now safe to summarize without rerunning experiments, provided the paper uses conservative metric language:

- Main-ready now: projection ablation, masked naturalization proxy ablation, compact Experiment 3 occupancy table, corrected traditional-vs-ours metrics table after resolving one table-source mismatch.
- Appendix-ready now: Experiment 3 mesh-fragmentation audit, masked-naturalization topology audit, depth scaling diagnostics, broader status/inventory tables.
- Needs reconciliation before main integration: corrected metrics table vs current refresh/remote table for the IFS/Ours row, PS-RSLG labels in source CSV/refresh outputs, and the stale/non-main `gen3d_baseline_summary_table_20260510.tex`.
- Needs rerun only if the manuscript wants stronger claims than the current proxies support: exact Trellis runtime handle metrics, watertight topology comparisons, full 8-case Experiment 3 main table, or cross-seed depth scaling beyond the current curated rows.

## Sources Checked

Primary table drafts:

- `paper_siga/drafts/projection_ablation_main_table_20260511.tex`
- `paper_siga/drafts/masked_naturalization_main_table_20260511.tex`
- `paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`
- `paper_siga/drafts/depth_scaling_diagnostics_20260513.tex`
- `paper_siga/drafts/experiment3_mesh_enrichment_20260513.tex`
- `paper_siga/drafts/masked_naturalization_topology_audit_20260513.tex`
- `paper_siga/figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`

Primary CSV/JSON sources:

- `results/projection_masked_ablation_matrices_20260511/metrics.csv`
- `results/projection_masked_ablation_matrices_20260511/projection_ablation_meanstd_20260511.csv`
- `results/projection_masked_ablation_matrices_20260511/masked_naturalization_projection_meanstd_20260511.csv`
- `results/paper_metric_refresh_20260513/projection_ablation_meanonly_20260513.csv`
- `results/paper_metric_refresh_20260513/masked_naturalization_meanonly_20260513.csv`
- `results/paper_metric_refresh_20260513/experiment3_compact_table_20260513.csv`
- `results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_master_manifest.csv`
- `results/main_experiment_case_metrics_20260511/main_experiment_selected_corrected_V67B_metrics_20260512/*.csv`
- `results/metric_enrichment_20260513/*.csv`
- `results/fern_two_case_recursive_remote_20260512{o,p}_pull/roots/initial_metrics.json`

## Main/Appendix Readiness Matrix

| Result block | Current evidence | Main table readiness | Appendix readiness | Action |
|---|---|---|---|---|
| Projection ablation | 60 rows: 5 variants x 4 tasks x 3 seeds in `metrics.csv`; value-only draft exists | Ready | Ready with per-task detail | Use current draft; keep trace-proxy caveat |
| Masked naturalization | 120 rows: 10 variants x 4 tasks x 3 seeds; six-row value-only draft exists | Ready as secondary proxy table | Ready with topology audit | Keep "proxy" wording; do not claim topology repair |
| Traditional-vs-ours corrected metrics | 8 rows, surface metrics + welded mesh diagnostics | Ready after mismatch resolved | Ready | Choose included V67B/Overleaf row or refreshed row; document decision |
| Experiment 3 compact | 20 rows from 101-row master manifest | Ready if using compact occupancy schema | Ready with supplement | Rename PS-RSLG to PS-RSLE before integration |
| Experiment 3 mesh enrichment | 52/65 priority assets measured; 13 skipped by face guard | Not main evidence | Ready caveat table | Use as diagnostic only |
| Depth scaling | Curated depth 0/2/4/6 rows, LCR 1.0, comp 1 for selected fiddlehead rows | Optional main/short table | Ready | Use as appendix or compact controllability table |
| Status/inventory tables | ablation/status tables show partial matrices | Not main evidence | Appendix only | Keep as closure inventory |

## Corrected Metrics vs Remote/Refresh Table

The included/Overleaf table is:

- `paper_siga/figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`
- `git -C paper_siga show overleaf/master:figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex` matches it.

It uses readable headers: `Surf. comp. r0`, `Surf. LCR r0`, `Surf. comp. r1`, and avoids the older opaque `$C_{r0}$` header.

The refresh table differs:

- `results/paper_metric_refresh_20260513/main_experiment_selected_metrics_table_20260513.tex`
- It reverts to `$C_{r0}$`, `LCR$_{r0}$`, `$C_{r1}$` headers and says "texture-export islands".
- It differs in the IFS/Ours row:
  - Included/Overleaf V67B: `Surf. comp. r0 = 1`, `LCR = 1.000`, `Faces = 37,274`, `Box dim. = 2.071`.
  - Refresh table/source CSV: `Surf. comp. r0 = 6`, `LCR = 0.999`, `Faces = 19,454`, `Box dim. = 2.111`.

Interpretation: the included table appears to use a newer manually corrected IFS/Ours row than the refresh source CSV. Do not overwrite the included/Overleaf table from `results/paper_metric_refresh_20260513` until the chosen IFS asset is confirmed. If the refresh row is actually the intended `V21_ifs_branch_tree_natural_bark` asset, the table/figure pairing must be updated together.

## Std / Variance Status

Current included draft tables checked:

- `paper_siga/drafts/projection_ablation_main_table_20260511.tex`: no `\pm`, no std columns.
- `paper_siga/drafts/masked_naturalization_main_table_20260511.tex`: no `\pm`, no std columns.
- `paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`: no `\pm`, no std columns.
- `paper_siga/figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`: no `\pm`, no std columns.
- `paper_siga/drafts/depth_scaling_diagnostics_20260513.tex`: no `\pm`, no std columns.

Std still exists in source aggregates:

- `results/projection_masked_ablation_matrices_20260511/projection_ablation_meanstd_20260511.csv`
- `results/projection_masked_ablation_matrices_20260511/masked_naturalization_projection_meanstd_20260511.csv`
- `results/masked_naturalization_ablation_m1_20260510/m1_protocol_meanstd.csv`

Conclusion: main/draft table outputs have already removed std. The remaining mean/std CSVs are archival sources and should not be directly included in paper tables.

## Projection Ablation Consistency

Current value-only draft:

| Variant | Occ. LCR | Root reach. | Orphan active | Handle survival | Exec. pass |
|---|---:|---:|---:|---:|---:|
| no projection | 0.898 | 0.504 | 3.667 | 0.504 | 0.000 |
| final-only | 0.995 | 0.504 | 3.667 | 0.504 | 0.000 |
| per-depth prune-only | 0.964 | 1.000 | 0.000 | 0.782 | 0.250 |
| per-depth connector-aware | 0.995 | 1.000 | 0.000 | 1.000 | 0.750 |
| full PS-RSLE | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 |

This is internally consistent with the source mean-only CSV except for label polarity/name:

- Source CSV stores `failure_rate_mean`; table reports `Exec. pass = 1 - failure_rate_mean`.
- Source CSV label still says `full PS-RSLG`; table correctly says `full PS-RSLE`.

Safe claim: final-only projection improves terminal occupancy LCR but does not improve root reachability, orphan-active handles, or handle survival. Per-depth projection changes executable-state metrics.

Do not claim: watertight topology, true Trellis sparse-runtime handle recovery, or arbitrary GLB handle validity.

## Masked Naturalization Consistency

Current value-only draft:

| Variant | Rough. | Normal | Artifacts | Drift | Handle surv. | Quality | Exec. pass |
|---|---:|---:|---:|---:|---:|---:|---:|
| rule-only | 50.00 | 0.000 | 0.487 | 0.203 | 0.500 | 0.529 | 0.000 |
| masked/no-proj | 47.45 | 0.003 | 0.488 | 0.201 | 0.500 | 0.530 | 0.000 |
| no-N/+proj | 16.94 | 0.597 | 0.348 | 0.000 | 1.000 | 0.771 | 0.750 |
| weak/+proj | 14.11 | 0.664 | 0.228 | 0.088 | 1.000 | 0.805 | 1.000 |
| masked/+proj | 13.92 | 0.669 | 0.227 | 0.090 | 1.000 | 0.807 | 1.000 |
| global/+proj | 13.58 | 0.677 | 0.229 | 0.090 | 1.000 | 0.735 | 1.000 |

This is consistent with `results/paper_metric_refresh_20260513/masked_naturalization_meanonly_20260513.csv` after converting `failure_rate_mean` to `Exec. pass`.

Table-safe interpretation:

- Projection is the structural gate: no-projection rows keep handle survival around 0.5 and exec pass 0.0.
- Masked/+proj has the best composite quality proxy among reported projected variants, while global/+proj has slightly smoother roughness/normal values but lower locality-weighted quality.

Metric risk:

- `Quality` is a composite proxy. It should not be described as human perceptual quality.
- `Normal` is derived from roughness in the generator script, so do not present roughness and normal as independent evidence.

Appendix support:

- `results/metric_enrichment_20260513/masked_naturalization_topology_summary_20260513.csv` shows masked/weak/global projected variants have median raw/welded comp 1 and 3/3 watertight rows, while rule-only is 16/16 and final-only/per-depth projection are 4/4. Use this only as mesh-fragmentation audit, not as the primary reason to prefer masked over global.

## Experiment 3 Consistency

Current paper draft has compact schema:

| Case | Method | Occ. comp. | LCR | Status |
|---|---|---:|---:|---|

This is preferable for main text. It removes weak/non-discriminative columns from the CSV (`state_update`, `projection`, `copy_rep`, `raw_components`) while preserving occupancy component count and LCR.

Source issues to fix before integration:

- `results/paper_metric_refresh_20260513/experiment3_compact_table_20260513.csv` still labels positive rows as `PS-RSLG`.
- The draft table has manually corrected labels to `PS-RSLE`.
- The supplement refresh file `results/paper_metric_refresh_20260513/experiment3_sparse_latent_vs_mesh_space_table_supplement_20260513.tex` still contains `PS-RSLG`.

Main-safe rows:

- tree crown: PS-RSLE `Occ. comp. 1`, `LCR 1.000`; controls have 11-40 occupancy components.
- bismuth: PS-RSLE `1`, `1.000`; root+mesh-copy has `53`, `0.112`.
- coral: PS-RSLE `1`, `1.000`; controls have `3-43` components and lower LCR.
- pyrite: PS-RSLE `3`, `1.000`, status `proxy-positive+caveat`; keep caveat.

Appendix-only:

- `raw_components` and mesh-fragmentation rows. The enrichment summary says Experiment 3 priority assets are non-watertight in the measured subset (`watertight = 0`) and 13/65 priority assets were skipped by the face-count guard. This is valuable as a caveat, not a main success metric.

## Depth Scaling Readiness

`paper_siga/drafts/depth_scaling_diagnostics_20260513.tex` is already a compact value-only table:

| Case | Depths | Final comp. | Final LCR | Vertices d0 to d6 | Faces d0 to d6 | Max bbox drift |
|---|---|---:|---:|---|---|---:|
| fiddlehead surface s | 0,2,4,6 | 1 | 1.000 | 5,644 to 13,820 | 11,275 to 27,501 | 0.00% |
| fiddlehead surface t | 0,2,4,6 | 1 | 1.000 | 7,032 to 16,484 | 14,042 to 32,802 | 0.00% |
| fiddlehead surface u | 0,2,4,6 | 1 | 1.000 | 5,644 to 13,820 | 11,275 to 27,501 | 0.00% |
| fiddlehead surface v | 0,2,4,6 | 1 | 1.000 | 7,032 to 16,484 | 14,042 to 32,802 | 0.00% |

Source: explicit root-depth manifests/metrics under `results/fern_two_case_recursive_remote_20260512{o,p}_pull/roots/`.

Safe claim: selected depth sweeps increase vertex/face counts while retaining single-component final meshes and stable bounding boxes under the available geometry metrics.

Need more runs only if claiming cross-family or statistical depth scaling. The current rows are curated fiddlehead surface cases; broader fern/botanical rows exist but have more visual/status caveats.

## Missing Metrics / Rerun Needs

No rerun needed for:

- A main projection ablation table.
- A main masked-naturalization proxy table.
- A compact main Experiment 3 occupancy table.
- A corrected traditional-vs-ours table once the IFS/Ours row source is selected.
- Appendix mesh-enrichment and depth-scaling tables.

Rerun or recompute needed if any of these claims are desired:

- Per-depth Trellis codec-closed re-encode evidence for every reported run, rather than controlled trace/mesh proxies.
- Watertight/clean topology claim across Experiment 3 or traditional-vs-ours rows.
- Full 8-case Experiment 3 main table with Hunyuan coverage for every case and no missing/skipped oversized rows.
- Cross-seed depth-scaling statistics beyond the four curated `0,2,4,6` fiddlehead rows.
- Consistent refreshed traditional-vs-ours metrics if the included V67B IFS/Ours row is not the selected figure asset.

## Naming / Exposure Risks

Still present in non-main or source artifacts:

- `PS-RSLG` in `results/paper_metric_refresh_20260513/*.csv/*.tex`, `paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex`, and older draft method files.
- `ps_rslg` as variant IDs in CSVs.
- `PBR`, `GLB`, and `texture-export` in older draft/status files and refresh table captions.

Current main-ready drafts mostly avoid these issues:

- Projection draft uses `full PS-RSLE`.
- Experiment 3 draft uses `PS-RSLE`.
- Included corrected metrics table uses readable `Surf. comp. r0` headers and avoids `texture-export islands`.

Do not integrate `paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex` as-is: it still has `PS-RSLG`, GLB/MB framing, and older control framing.

## Recommended Table Landing Plan

1. Keep `paper_siga/drafts/projection_ablation_main_table_20260511.tex` as the main quantitative anchor. It is value-only and claim-aligned.
2. Keep `paper_siga/drafts/masked_naturalization_main_table_20260511.tex` as a secondary local-realization proxy table, with metric definitions/caveats in text.
3. Use `paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex` for main Experiment 3 if a compact occupancy table is desired; keep raw/welded components in appendix.
4. Resolve the IFS/Ours row before regenerating or replacing `paper_siga/figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`.
5. Add `paper_siga/drafts/depth_scaling_diagnostics_20260513.tex` to appendix or a short controllability subsection, not as broad statistical proof.
6. Keep `results/metric_enrichment_20260513/metric_enrichment_block_summary_20260513.csv` and `masked_naturalization_topology_summary_20260513.csv` as appendix audits/caveats.

## Verification Notes

Commands run in this audit included direct `sed` reads of draft tables, CSV schema/value inspection with `python3 csv.DictReader`, `rg` checks for `\pm`, `std`, `PS-RSLG`, `PBR`, `GLB`, and comparison against `git -C paper_siga show overleaf/master:figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`.

I did not modify `paper_siga/main.tex`.
