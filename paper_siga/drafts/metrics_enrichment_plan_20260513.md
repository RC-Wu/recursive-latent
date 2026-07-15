# Metrics Enrichment Plan 20260513

Scope: paper-integration proposal only. This draft uses existing CSV/JSON artifacts and does not require rerunning remote generation, CLIP, or mesh rendering.

## 1. Verified Data Sources And Commands

Working directory:

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
```

Artifact inventory verified with:

```bash
find results/metric_enrichment_20260513 -maxdepth 3 -type f \( -name '*.csv' -o -name '*.json' -o -name '*.md' -o -name '*.txt' \) | sort
find results/projection_masked_ablation_matrices_20260511 -maxdepth 3 -type f \( -name '*.csv' -o -name '*.json' -o -name '*.md' -o -name '*.txt' \) | sort
find results/experiment3_sparse_latent_vs_meshspace_20260511 -maxdepth 4 -type f \( -name '*.csv' -o -name '*.json' -o -name '*.md' -o -name '*.txt' \) | sort
```

CSV schemas and representative rows verified with:

```bash
for f in results/metric_enrichment_20260513/*.csv; do sed -n '1,8p' "$f"; done
for f in results/projection_masked_ablation_matrices_20260511/*.csv; do sed -n '1,10p' "$f"; done
for f in results/experiment3_sparse_latent_vs_meshspace_20260511/*.csv results/experiment3_sparse_latent_vs_meshspace_20260511/trellis2_generatedroot_meshcopy/*.csv; do sed -n '1,10p' "$f"; done
```

Relevant producer scripts inspected:

```bash
sed -n '1,260p' assets/mesh_metric_enrichment_20260513.py
sed -n '1,240p' assets/projection_masked_ablation_matrices_20260511.py
sed -n '1,220p' assets/experiment3_build_table_20260511.py
sed -n '1,220p' assets/experiment3_ps_rslg_metric_rows_20260511.py
```

Derived-number aggregation verified with a read-only `python3` CSV script over:

- `results/metric_enrichment_20260513/metric_enrichment_block_summary_20260513.csv`
- `results/metric_enrichment_20260513/linnaeus_handle_lineage_audit_20260513.csv`
- `results/metric_enrichment_20260513/linnaeus_failure_localization_audit_20260513.csv`
- `results/metric_enrichment_20260513/linnaeus_method_budget_summary_20260513.csv`
- `results/projection_masked_ablation_matrices_20260511/projection_ablation_meanstd_20260511.csv`
- `results/projection_masked_ablation_matrices_20260511/masked_naturalization_projection_meanstd_20260511.csv`
- `results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_compact_table_supplement_8case_20260511.csv`

No generation scripts, rendering jobs, remote jobs, or table-building scripts were rerun for this draft.

## 2. Candidate Common Metric Set For Tables 3/4/Ablations

Use one common compact metric vocabulary across the main and ablation tables:

| Metric | Column label | Source columns | Intended use |
|---|---:|---|---|
| State update present | State | `latent_update_used`, `state_update`, variant metadata | Binary design variable, not a quality score. |
| Projection present/schedule | Proj. | `projection_used`, `projection_schedule`, `projection` | Binary or schedule label for PS-RSLE components. |
| Copy repetition score | Copy rep. | `copy_repetition_score`, `copy_rep` | Marks mesh-space/latent-copy baselines; should not be read as visual similarity. |
| Raw face components | Raw comps. | `raw_component_count`, `component_count`, `raw_components` | Fragmentation proxy before occupancy merging. |
| Occupancy components | Occ. comps. | `occupancy_component_count_6n`, `occ_components` | Coarse 6-neighbor voxel connectivity proxy. |
| Largest occupancy component ratio | LCR | `LCR`, `largest_occupancy_component_ratio_6n`, `occupancy_lcr_*` | Connectivity proxy; use with resolution caveat. |
| Handle/root survival | Handle surv. / Reach | `recursive_handle_survival_proxy`, `root_reachability_*`, `median_handle_survival_proxy` | State-lineage diagnostic for ablation tables. |
| Orphan active handles | Orphans | `recursive_orphan_active_handles_proxy`, `orphan_active_handles_*` | Failure localization for projection ablation. |
| Surface/mesh readiness | Boundary / nonmanifold / watertight | `boundary_edge_count`, `nonmanifold_edge_count`, `is_watertight` | Engineering-readiness supplement, not visual quality. |
| Triangle budget/quality | Tris / tri. qual. | `triangles`, `triangle_quality_mean`, budget pass flags | Supplementary comparability and renderability context. |

Recommended integration:

- Table 3/Experiment 3: keep `State`, `Proj.`, `Copy rep.`, `Raw comps.`, `Occ. comps.`, `LCR`, `Status`.
- Table 4/projection-naturalization ablation: use `failure_rate`, `handle_survival`, `root_reachability`, `orphan_handles`, `occupancy_lcr`, plus the render-proxy columns only if the caption states they are deterministic proxies.
- Supplementary mesh-readiness table: use `triangles`, `raw_components`, `welded_components`, `boundary_edges`, `nonmanifold_edges`, `watertight`, `welded_single`.

## 3. Derived Numbers Already Computable Locally

CPU-only enrichment coverage:

| Block | Requested | Measured | Skipped | Welded single | Watertight | Median boundary | Median nonmanifold | Median tri. quality |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Experiment 3 priority assets | 65 | 52 | 13 | 1 | 0 | 154193.5 | 0.0 | 0.727 |
| V24 main-comparison scaffolds | 15 | 15 | 0 | 0 | 0 | 934.0 | 944.0 | 0.566 |
| Real-case projection/naturalization inputs | 22 | 22 | 0 | 8 | 8 | 1892.5 | 0.0 | 0.643 |
| Masked-naturalization manifest inputs | 18 | 18 | 0 | 9 | 18 | 0.0 | 0.0 | 0.692 |

Projection ablation, 12 runs per row over 4 tasks x 3 seeds:

| Variant | Failure rate | Handle survival | Root reachability | Orphans | Occupancy LCR |
|---|---:|---:|---:|---:|---:|
| no projection | 1.00 | 0.504 | 0.504 | 3.667 | 0.898 |
| final-only projection | 1.00 | 0.504 | 0.504 | 3.667 | 0.995 |
| per-depth prune-only | 0.75 | 0.782 | 1.000 | 0.000 | 0.964 |
| per-depth connector-aware | 0.25 | 1.000 | 1.000 | 0.000 | 0.995 |
| reported PS-RSLE proxy row | 0.00 | 1.000 | 1.000 | 0.000 | 1.000 |

Immediate derived deltas:

- Connector-aware per-depth projection raises mean handle survival by 0.496 over no projection.
- The reported PS-RSLE proxy row lowers the deterministic failure proxy from 1.00 to 0.00 relative to no projection.
- Final-only projection improves occupancy LCR but does not improve state reachability or orphan handles, so it should be described as a geometry repair that misses the recursive state failure.

State-geometry gap and failure localization:

| Variant | Median state-geometry gap | Median handle survival | Reach gain vs no projection | Orphan reduction | Clean proxy rows | Dominant failure |
|---|---:|---:|---:|---:|---:|---|
| no projection | 0.266 | 0.629 | 0.000 | 0.0 | 0/12 | state |
| final-only projection | 0.370 | 0.629 | 0.000 | 0.0 | 0/12 | state |
| per-depth prune-only | -0.019 | 0.736 | 0.371 | 2.5 | 6/12 | geometry |
| per-depth connector-aware | -0.001 | 1.000 | 0.371 | 2.5 | 0/12 | drift |
| masked local + projection | 0.000 | 1.000 | 0.371 | 2.5 | 12/12 | none |
| global + projection | 0.000 | 1.000 | 0.371 | 2.5 | 12/12 | none |
| weak blend + projection | 0.000 | 1.000 | 0.371 | 2.5 | 12/12 | none |

Naturalization pairing result:

| Variant pair | Failure rate | Rendered quality proxy | Surface roughness | Local artifact index | Normal consistency |
|---|---:|---:|---:|---:|---:|
| masked local, no projection | 1.00 | 0.530 | 47.451 | 0.488 | 0.003 |
| masked local, with projection | 0.00 | 0.807 | 13.923 | 0.227 | 0.669 |
| global, no projection | 1.00 | 0.458 | 47.582 | 0.479 | 0.003 |
| global, with projection | 0.00 | 0.735 | 13.578 | 0.229 | 0.677 |
| weak blend, no projection | 1.00 | 0.531 | 47.771 | 0.487 | 0.001 |
| weak blend, with projection | 0.00 | 0.805 | 14.111 | 0.228 | 0.664 |

Experiment 3 supplement summary over 8 cases:

| Method | n | Median LCR | Median raw comps. | Median occ. comps. | Statuses |
|---|---:|---:|---:|---:|---|
| Trellis2 one-shot | 8 | 0.998 | 1173.0 | 3.5 | one-shot control |
| Trellis2 latent-copy | 8 | 0.951 | 2385.0 | 8.5 | copy-state control |
| Trellis2 root+mesh-copy | 8 | 0.477 | 196904.5 | 44.5 | copy-state control |
| Hunyuan root+mesh-copy | 4 | 0.964 | 248670.0 | 12.5 | copy-state control |
| PS-RSLE | 8 | 1.000 | 1.0 | 1.0 | selected positive, proxy-positive+caveat, QA-gated positive |

Mesh budget/readiness summary by method:

| Method | Rows | OK | Median tris | Median raw comps. | Median welded comps. | Welded single | Watertight |
|---|---:|---:|---:|---:|---:|---:|---:|
| Hunyuan root+mesh-copy | 4 | 4 | 275989.5 | 272162.5 | 152126.5 | 0 | 0 |
| Hunyuan root+mesh-copy smooth | 8 | 8 | 91584.0 | 78077.5 | 28375.0 | 0 | 0 |
| Trellis2 generated-root mesh-copy | 14 | 14 | 184000.0 | 182031.0 | 61257.5 | 0 | 0 |
| Trellis2 one-shot image | 16 | 10 | 710573.0 | 399.5 | 131.0 | 0 | 0 |
| Trellis2 root latent-copy | 11 | 4 | 107299.0 | 95.0 | 80.5 | 0 | 0 |
| PS-RSLE | 10 | 10 | 22833.0 | 6458.5 | 131.5 | 1 | 0 |

## 4. Requires Remote A100/CLIP Or Mesh Rendering

Remote A100 or model jobs are required for:

- Any new Trellis2, Hunyuan, image-conditioned, latent-copy, generated-root, or texture generation beyond the existing artifacts.
- CLIP/DINO/semantic prompt alignment, perceptual image scores, or language-image quality comparisons.
- Claims about learned generator behavior under new seeds or prompts.

Mesh rendering or visual QA is required for:

- Final main-paper inclusion of rows marked `needs_visual_qa`, `QA-gated positive`, or `proxy-positive+caveat`.
- Camera-matched visual comparisons and screenshots for Table 3/4 figure panels.
- PBR appearance, texture seam quality, color/material naturalness, and visual artifact localization.
- Any statement that a mesh is visually successful, publication-ready, or perceptually better than a baseline.

No remote job is required for:

- CSV-level connectivity, component, handle-state proxy, state-geometry gap, budget, boundary, nonmanifold, watertight, or triangle-quality summaries already listed above.

## 5. Wording Boundaries To Avoid Overclaiming

Safe wording:

- "In deterministic proxy audits over 4 tasks x 3 seeds, per-depth connector-aware projection restores handle survival and root reachability to 1.0, while final-only projection leaves the state-proxy failure unchanged."
- "The mesh diagnostics indicate fragmentation and open-boundary readiness issues in mesh-space copy baselines; these are CPU geometry proxies, not perceptual quality judgments."
- "Masked/global/weak naturalization improves the measured render-proxy suite only when paired with projection in the audited variants."
- "Experiment 3 rows separate one-shot generation, trivial latent/mesh copy controls, and PS-RSLE positives using state/projection/copy indicators plus connectivity proxies."
- "Rows marked QA-gated or proxy-positive+caveat should remain supplementary unless visually reviewed."

Avoid wording:

- Do not say "proves semantic superiority", "human-preferred", "CLIP-aligned", or "perceptually better" from these CPU metrics.
- Do not say "watertight" or "simulation-ready" for Experiment 3 priority assets; the enrichment summary reports 0 watertight rows for that block.
- Do not describe one-shot Trellis2 high LCR as recursive success; its `state_update` is N/A and `projection` is 0.
- Do not call final-only projection a state fix; it improves occupancy LCR but leaves handle survival/root reachability at no-projection levels.
- Do not generalize beyond the audited local tasks/seeds without remote reruns or additional validation.

## 6. Suggested Paper Integration

Table 3 can keep the compact Experiment 3 structure, adding one caption sentence: "Connectivity numbers are CPU mesh/occupancy proxies; state/projection/copy columns define the intervention rather than learned quality."

Table 4 can use the projection ablation row set above to make the state-vs-geometry point: final-only projection repairs geometry proxies but not handle-state validity; per-depth connector-aware projection restores handles/reachability; the reported PS-RSLE proxy row adds naturalization and removes the failure proxy in this audit.

Supplementary ablation tables should carry the mesh-readiness block summary and method budget summary, explicitly labeling them as engineering diagnostics for existing artifacts.
