# Projection Metric Enrichment Audit - 2026-05-13

Scope: read-only inspection of `results/projection_masked_ablation_matrices_20260511/metrics.csv`, adjacent aggregate artifacts, and the generating script/table drafts. No edits were made to `paper_siga/main.tex` or tracked LaTeX tables.

## Files Checked

- `results/projection_masked_ablation_matrices_20260511/metrics.csv`
- `results/projection_masked_ablation_matrices_20260511/metrics.json`
- `results/projection_masked_ablation_matrices_20260511/projection_ablation_meanstd_20260511.csv`
- `results/projection_masked_ablation_matrices_20260511/masked_naturalization_projection_meanstd_20260511.csv`
- `results/projection_masked_ablation_matrices_20260511/summary.json`
- `assets/projection_masked_ablation_matrices_20260511.py`
- `paper_siga/drafts/projection_ablation_main_table_20260511.tex`
- `paper_siga/drafts/masked_naturalization_main_table_20260511.tex`

The project path is not a Git repository in this local checkout, so no stage/commit/push action was possible or attempted.

## Dataset Shape

`metrics.csv` has 180 per-run rows and 40 columns:

- 60 projection-ablation rows: 5 variants x 4 task families x 3 seeds.
- 120 naturalization/projection rows: 10 variants x 4 task families x 3 seeds.
- Task families: `botanical/root`, `coral/frontier`, `IFS/crystal`, `vine/branch`.
- Seeds: `20260510`, `20260511`, `20260512`.

The adjacent aggregate CSVs already contain means and sample standard deviations:

- `projection_ablation_meanstd_20260511.csv`: 5 rows, includes `_mean` and `_std` columns.
- `masked_naturalization_projection_meanstd_20260511.csv`: 10 rows, includes `_mean` and `_std` columns.

## Available Metrics

Per-run columns in `metrics.csv` fall into four groups.

1. Identity/protocol columns:
   `experiment`, `task_id`, `task_family`, `variant`, `seed`, `mesh_path`, `metadata_path`, `projection_schedule`, `naturalization_policy`, `connector_aware_projection`, `prune_only_projection`.

2. Mesh/export diagnostics:
   `vertex_count`, `triangle_count`, `occupancy_component_count_6n`, `occupancy_lcr_6n`, `raw_face_component_count`, `raw_face_lcr`, `mean_triangle_aspect_ratio`, `degenerate_face_fraction`, `mesh_quality_score`, `axis_aligned_normal_fraction`, `blockiness_score`, `connectivity_blockiness_index`, `local_normal_variation_mean_deg`, `global_normal_variation_mean_deg`.

3. Controlled trace/state proxies:
   `recursive_root_reachability_proxy`, `recursive_orphan_active_handles_proxy`, `recursive_handle_survival_proxy`, `recursive_deleted_active_handles_mean_proxy`.

4. Derived proxy scores:
   `local_artifact_index_proxy`, `surface_roughness_proxy`, `normal_consistency_proxy`, `locality_policy_score_proxy`, `projection_policy_score_proxy`, `rendered_asset_quality_proxy`, `silhouette_iou_vs_control_proxy`, `silhouette_iou_vs_rule_only_proxy`, `bbox_extent_l1_vs_control_proxy`, `topology_drift_proxy`, `failure_proxy`.

The generator script explicitly writes the limitation: these are "deterministic primitive trace and mesh proxy; not a Trellis sparse-latent runtime graph." The summary repeats: "local deterministic primitive/mesh proxy; remote Trellis runtime visual rerun still required for final PBR asset claims."

## Publication-Safe Metrics

Safe for the main projection-ablation claim, with conservative wording:

- `occupancy_lcr_6n`: surface-sampled, dilated voxel occupancy largest-component ratio. Use as terminal connectedness/renderability diagnostic, not topology proof.
- `recursive_root_reachability_proxy`: controlled trace proxy for whether active recursive handles remain root-reachable before later rules can consume them.
- `recursive_orphan_active_handles_proxy`: controlled trace proxy for invalid active handles left in the executable state.
- `recursive_handle_survival_proxy`: controlled trace proxy for preserving useful reachable active handles.
- `failure_proxy` or `1 - failure_proxy`: usable only if named as a thresholded diagnostic gate, not "success" in an absolute sense.

Safe for a compact naturalization ablation, with conservative wording:

- `surface_roughness_proxy`: local normal variation in degrees; lower is smoother.
- `normal_consistency_proxy`: derived from roughness; higher is smoother/more consistent.
- `local_artifact_index_proxy`: derived artifact proxy using mesh quality, blockiness, and component count.
- `topology_drift_proxy`: silhouette/bounding-box drift proxy relative to the projection control.
- `recursive_handle_survival_proxy`: same controlled trace proxy as above.
- `rendered_asset_quality_proxy`: composite diagnostic score; useful only if called a proxy/score.
- `failure_rate_mean`: thresholded diagnostic gate.

Not safe as main claims:

- Do not call any row "watertight", "topology clean", or "physically valid"; this matrix does not provide watertight/boundary/nonmanifold evidence.
- Do not imply handle metrics are recovered from arbitrary Trellis textured GLBs. They are controlled deterministic primitive-trace proxies.
- Do not use `rendered_asset_quality_proxy` as a perceptual-quality ground truth. It is a weighted diagnostic score.
- Do not use `normal_consistency_proxy` and `surface_roughness_proxy` as independent evidence; `normal_consistency_proxy` is derived from roughness in the script.

## Exact Projection Candidate Values

Aggregate values from `projection_ablation_meanstd_20260511.csv`, all over 12 runs per row:

| Variant | Occ. LCR | Root reach. | Orphan active | Handle survival | Failure rate |
|---|---:|---:|---:|---:|---:|
| no projection | 0.8976109849967746 +/- 0.013758907616748913 | 0.5041666666666667 +/- 0.31106488653713976 | 3.6666666666666665 +/- 2.640018365409031 | 0.5041666666666667 +/- 0.31106488653713976 | 1.0 +/- 0.0 |
| final-only | 0.9952272173449469 +/- 0.007552165059005903 | 0.5041666666666665 +/- 0.31106488653713976 | 3.6666666666666665 +/- 2.6400183654090306 | 0.5041666666666665 +/- 0.31106488653713976 | 1.0 +/- 0.0 |
| per-depth prune-only | 0.9641010319739102 +/- 0.043431685258978885 | 1.0 +/- 0.0 | 0.0 +/- 0.0 | 0.7820767195767195 +/- 0.14821510267235583 | 0.75 +/- 0.45226701686664544 |
| per-depth connector-aware | 0.9951155175844267 +/- 0.007510391935793243 | 1.0 +/- 0.0 | 0.0 +/- 0.0 | 1.0 +/- 0.0 | 0.25 +/- 0.45226701686664544 |
| full PS-RSLG | 1.0 +/- 0.0 | 1.0 +/- 0.0 | 0.0 +/- 0.0 | 1.0 +/- 0.0 | 0.0 +/- 0.0 |

Mean-only values recommended for main table:

| Variant | Occ. LCR | Root reach. | Orphan active | Handle survival | Committed pass |
|---|---:|---:|---:|---:|---:|
| no projection | 0.898 | 0.504 | 3.667 | 0.504 | 0.000 |
| final-only | 0.995 | 0.504 | 3.667 | 0.504 | 0.000 |
| per-depth prune-only | 0.964 | 1.000 | 0.000 | 0.782 | 0.250 |
| per-depth connector-aware | 0.995 | 1.000 | 0.000 | 1.000 | 0.750 |
| full PS-RSLE/PS-RSLG | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 |

Naming note: the CSV says `full PS-RSLG`, while `main.tex` and current table text use `PS-RSLE`. The manuscript should use one term consistently. For `paper_siga`, `PS-RSLE` appears to be the current method name.

## Per-Task Projection Values

These are means over the three seeds, useful for supplement or caption support. They expose why "final-only cleanup" is the wrong conclusion even when terminal LCR is high.

| Variant | Task | Occ. LCR | Root reach. | Orphan active | Handle survival | Failure |
|---|---|---:|---:|---:|---:|---:|
| no projection | botanical_root | 0.912531 | 0.583333 | 2.500000 | 0.583333 | 1.000000 |
| no projection | coral_frontier | 0.895229 | 0.675000 | 2.500000 | 0.675000 | 1.000000 |
| no projection | ifs_crystal | 0.898393 | 0.000000 | 8.000000 | 0.000000 | 1.000000 |
| no projection | vine_trellis | 0.884291 | 0.758333 | 1.666667 | 0.758333 | 1.000000 |
| final-only | botanical_root | 1.000000 | 0.583333 | 2.500000 | 0.583333 | 1.000000 |
| final-only | coral_frontier | 1.000000 | 0.675000 | 2.500000 | 0.675000 | 1.000000 |
| final-only | ifs_crystal | 0.982778 | 0.000000 | 8.000000 | 0.000000 | 1.000000 |
| final-only | vine_trellis | 0.998131 | 0.758333 | 1.666667 | 0.758333 | 1.000000 |
| per-depth prune-only | botanical_root | 0.969995 | 1.000000 | 0.000000 | 0.619048 | 1.000000 |
| per-depth prune-only | coral_frontier | 0.991607 | 1.000000 | 0.000000 | 0.708333 | 1.000000 |
| per-depth prune-only | ifs_crystal | 1.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 |
| per-depth prune-only | vine_trellis | 0.894802 | 1.000000 | 0.000000 | 0.800926 | 1.000000 |
| per-depth connector-aware | botanical_root | 1.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 |
| per-depth connector-aware | coral_frontier | 1.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 |
| per-depth connector-aware | ifs_crystal | 0.982779 | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| per-depth connector-aware | vine_trellis | 0.997683 | 1.000000 | 0.000000 | 1.000000 | 0.000000 |
| full PS-RSLG | botanical_root | 1.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 |
| full PS-RSLG | coral_frontier | 1.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 |
| full PS-RSLG | ifs_crystal | 1.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 |
| full PS-RSLG | vine_trellis | 1.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 |

Best main-story rows:

- `final_only_projection`: terminal Occ. LCR is 0.995, but root reachability and handle survival remain 0.504 with 3.667 orphan active handles. This directly supports the claim that final cleanup does not create per-depth executable state.
- `per_depth_prune_only`: root reachability reaches 1.000 and orphan active handles reach 0.000, but handle survival drops to 0.782. This separates admissibility from expressive handle preservation.
- `per_depth_connector_aware`: root reachability 1.000, orphan active 0.000, handle survival 1.000, but failure rate 0.25 due to the IFS/crystal LCR threshold.
- `full PS-RSLE`: all five headline diagnostics pass at the aggregate level: Occ. LCR 1.000, root reachability 1.000, orphan active 0.000, handle survival 1.000, committed pass 1.000.

## Exact Naturalization Candidate Values

Aggregate values from `masked_naturalization_projection_meanstd_20260511.csv`, all over 12 runs per row. The current main table keeps six rows, but the final-only control is useful in text if space permits.

| Variant | Rough. | Normal | Artifacts | Drift | Handle surv. | Quality | Failure rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| rule-only | 50.00037475859525 +/- 4.476768131534836 | 0.0 +/- 0.0 | 0.48743580474508647 +/- 0.015463862560551683 | 0.20328841063218928 +/- 0.05014159789452212 | 0.49999999999999994 +/- 0.3074208447024628 | 0.5292545206836484 +/- 0.036302724937842486 | 1.0 +/- 0.0 |
| masked/no-proj | 47.45120461004148 +/- 4.664817792640184 | 0.003290654712672684 +/- 0.006156753240567029 | 0.48802229120126217 +/- 0.015835436397773718 | 0.2011809194068399 +/- 0.0505699085255475 | 0.5 +/- 0.3074208447024628 | 0.5299513290513747 +/- 0.037543474704675936 | 1.0 +/- 0.0 |
| no-N/+proj | 16.937185904843684 +/- 1.455155871690399 | 0.5967336689322933 +/- 0.034646568373580926 | 0.34798663700916843 +/- 0.03222302334590481 | 0.0 +/- 0.0 | 1.0 +/- 0.0 | 0.7708710428142892 +/- 0.005812701577131682 | 0.25 +/- 0.45226701686664544 |
| weak/+proj | 14.111043686671321 +/- 1.1008008361753714 | 0.6640227693649684 +/- 0.02620954371846124 | 0.2283561560399552 +/- 0.011644155438356594 | 0.08836464811416457 +/- 0.008589752418506817 | 1.0 +/- 0.0 | 0.804793634646669 +/- 0.004335495993727798 | 0.0 +/- 0.0 |
| masked/+proj | 13.922825981106676 +/- 1.123916150923292 | 0.6685041433069839 +/- 0.026759908355316466 | 0.2273257378452892 +/- 0.010975352963203913 | 0.09019129948009778 +/- 0.01625136766135228 | 1.0 +/- 0.0 | 0.806747579221788 +/- 0.005760598744328865 | 0.0 +/- 0.0 |
| global/+proj | 13.578489295938217 +/- 0.9959315556781337 | 0.6767026358109948 +/- 0.023712656087574623 | 0.2292784479664827 +/- 0.011590045324524746 | 0.08988412589694104 +/- 0.010608794759325208 | 1.0 +/- 0.0 | 0.7353051078516254 +/- 0.0031825738569417296 | 0.0 +/- 0.0 |
| final-only ctrl | 17.040401307202885 +/- 1.3552426534576354 | 0.5942761593523121 +/- 0.032267682225181796 | 0.34810983520361893 +/- 0.03270848070158977 | 0.003507539903760524 +/- 0.005253125577752164 | 0.5041666666666667 +/- 0.31106488653713976 | 0.6780301122068777 +/- 0.040351809033525976 | 0.75 +/- 0.45226701686664544 |

Mean-only values recommended for main table:

| Variant | Rough. | Normal | Artifacts | Drift | Handle surv. | Quality | Committed pass |
|---|---:|---:|---:|---:|---:|---:|---:|
| rule-only | 50.00 | 0.000 | 0.487 | 0.203 | 0.500 | 0.529 | 0.000 |
| masked/no-proj | 47.45 | 0.003 | 0.488 | 0.201 | 0.500 | 0.530 | 0.000 |
| no-N/+proj | 16.94 | 0.597 | 0.348 | 0.000 | 1.000 | 0.771 | 0.750 |
| weak/+proj | 14.11 | 0.664 | 0.228 | 0.088 | 1.000 | 0.805 | 1.000 |
| masked/+proj | 13.92 | 0.669 | 0.227 | 0.090 | 1.000 | 0.807 | 1.000 |
| global/+proj | 13.58 | 0.677 | 0.229 | 0.090 | 1.000 | 0.735 | 1.000 |

Interpretation:

- Projection is the structural gate: without projection, handle survival remains about 0.5 and committed pass remains 0.0 even when naturalization is enabled.
- Masked local naturalization has the best composite quality among the listed naturalization variants: 0.807 vs 0.805 for weak and 0.735 for global.
- Global naturalization has slightly better roughness/normal numbers, but worse composite quality because the script penalizes global mutable state/locality. Word this as a locality/quality tradeoff, not a topology win.

## Standard-Deviation Columns

Std columns exist in both aggregate CSVs. They were produced with sample standard deviation (`ddof=1`) across the 12 runs per variant.

For the main paper table, omit std columns. Reasons:

- Existing progress notes already identify a no-std main-table constraint.
- The main projection table is about a mechanistic invariant; std values widen the table and obscure the invariant pattern.
- Several std values are structurally zero because the proxy gate is deterministic for many rows; including them implies statistical uncertainty analysis that the deterministic ablation does not really support.
- The exact mean/std values can be reported in an appendix or this progress note.

Recommended wording for captions: "Values are means over four task families and three deterministic seeds." If std is omitted, do not say "mean +/- std" in the caption.

## Manuscript Wording

Suggested projection paragraph:

```latex
Table~\ref{tab:projection-ablation} reports means over four root families and three deterministic seeds. The metrics are controlled trace/mesh proxies: Occ. LCR is a surface-sampled voxel largest-component diagnostic, while root reachability, orphan active handles, and handle survival are measured on the deterministic recursive state trace before later rules consume it. Final-only projection raises terminal Occ. LCR to 0.995, but it leaves the same root reachability and handle survival as no projection (0.504) and the same orphan-active count (3.667). In contrast, per-depth projection removes orphan active handles before the next rule fires. Connector-aware projection preserves all reachable handles in this matrix, and full PS-RSLE reaches Occ. LCR 1.000, root reachability 1.000, orphan active 0.000, handle survival 1.000, and committed pass 1.000. The result supports per-depth admissible executable state, not a claim of watertight topology.
```

Suggested naturalization paragraph:

```latex
The naturalization table should be read as a local-quality diagnostic under the projection gate. Without projection, masked local naturalization does not repair executable state: handle survival remains 0.500 and committed pass remains 0.000. With per-depth projection, all naturalization variants preserve handle survival at 1.000; masked local naturalization gives the best composite quality proxy in this matrix (0.807), while global naturalization gives slightly smoother roughness/normal values but lower quality because it violates the locality policy. We therefore use masked local naturalization as a local realization aid, not as the structural mechanism that enforces admissibility.
```

Caption wording for projection table:

```latex
Experiment 2 projection ablation over four task families and three deterministic seeds. Values are means. Occ. LCR is a surface-sampled voxel largest-component diagnostic. Root reachability, orphan active handles, handle survival, and committed pass are deterministic trace/mesh proxies for whether active recursive state remains root-attached and executable before the next rule fires. Final-only projection improves terminal occupancy but leaves invalid active-state statistics unchanged; per-depth projection enforces the executable-state gate.
```

Caption wording for naturalization table:

```latex
Experiment 4 masked-naturalization ablation over four task families and three deterministic seeds. Values are means. Roughness, normal consistency, artifact index, drift, quality, and committed pass are deterministic proxy diagnostics. The table separates the structural projection gate from local surface realization: naturalization without projection does not make the recursive state admissible.
```

## Table and Caption Changes Best Supporting the Claim

1. Keep the projection ablation as the main evidence table for the "per-depth admissible executable state" claim. It directly contrasts terminal mesh cleanup against state validity.

2. Rename the last projection column from "Committed pass" only if the caption defines it precisely. Good alternatives:
   - `State pass`
   - `Exec. pass`
   - `Gate pass`
   If space allows, use `Exec. pass`; it better matches the claim.

3. Keep these five projection columns:
   `Occ. LCR`, `Root reach.`, `Orphan active`, `Handle survival`, `Exec. pass`.
   Do not add raw mesh components, triangle quality, roughness, or rendered quality to this table. Those dilute the executable-state argument.

4. Add a one-sentence caption caveat that all handle columns are controlled trace proxies, not recovered sparse-latent runtime graph metrics.

5. Use mean-only rows in the main table. Put exact mean/std values in appendix/progress notes if needed.

6. Fix naming consistency: use `full PS-RSLE` in the paper if PS-RSLE is the manuscript method name. The aggregate CSV says `full PS-RSLG`, and one table draft has shown both PS-RSLG/PS-RSLE spellings across revisions.

7. The naturalization table should support a secondary claim: masked local realization improves local-quality proxies after projection, but projection remains the structural gate. It should not be presented as proof of topology repair.

8. If an appendix table is added later, include per-task projection values for `final-only`, `per-depth connector-aware`, and `full PS-RSLE`. The IFS/crystal row is particularly useful because `final-only` has high terminal LCR but root reachability and handle survival are 0.000, making the difference between terminal cleanup and executable state unambiguous.

## Bottom Line

The available matrix is publication-safe for one focused claim: per-depth projection changes the recursive executable state, while final-only cleanup mostly changes terminal occupancy. The strongest evidence is the projection aggregate table: final-only has Occ. LCR 0.995 but root reachability/handle survival 0.504 and orphan active 3.667; full PS-RSLE has 1.000/1.000/0.000/1.000 with committed pass 1.000. Keep std columns out of the main tables, define all handle quantities as deterministic trace proxies, and avoid topology-clean or Trellis-runtime-handle claims.
