# R-SLG Ablation / Metrics Gap Audit

Date: 2026-05-11 CST  
Scope: local-only audit; no SSH; no large batch runs.  
Project root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`

## 0. Read Order And Version Note

Read sources:

- `docs/progress/ralph_publication_closure_plan_20260510.md`
- `docs/evaluation/gen3d_and_ablation_evidence_audit_zh_20260510_agent.md`
- `docs/obsidian_human_reports/2026-05-10_gen3d_ablation_round_closeout.md`

Important version delta: the older audit says coral mesh-space generated-root was missing. Current local state has since added `results/publication_coral_mesh_space_20260510/` and the current baseline master manifest includes the coral mesh-space row. Treat the current local CSVs as newer than the early closeout text.

## 1. Existing Evidence Paths

### Same-root matrix

- Coverage/status:
  - `results/ablation_summary_20260510/same_root_projection_available_rows_20260510.csv`
  - `results/ablation_summary_20260510/ablation_gap_counts_20260510.csv`
  - `results/publication_ablation_metrics_20260510/matrix_coverage_summary.csv`
  - `results/publication_ablation_metrics_20260510/ablation_gap_status_publication_20260510.csv`
  - `results/publication_ablation_metrics_20260510/claim_safe_miniset_20260510.csv`
  - `results/publication_ablation_metrics_20260510/ablation_gap_queue_20260510.csv`
  - `results/publication_ablation_metrics_20260510/manifest_selected_final_rows.csv`
- Tables/docs:
  - `paper_siga/drafts/ablation_status_tables_20260510.tex`
  - `paper_siga/drafts/publication_ablation_effective_resolution_status_20260510.tex`
- Script:
  - `assets/publication_ablation_selected_final_aggregation_20260510.py`

### Naturalization matrix

- Coverage/status:
  - `results/ablation_summary_20260510/naturalization_projection_available_rows_20260510.csv`
  - `results/publication_ablation_metrics_20260510/matrix_coverage_summary.csv`
  - `results/publication_ablation_metrics_20260510/ablation_gap_status_publication_20260510.csv`
  - `results/publication_ablation_metrics_20260510/claim_safe_miniset_20260510.csv`
  - `results/publication_ablation_metrics_20260510/ablation_gap_queue_20260510.csv`
  - `results/publication_ablation_metrics_20260510/manifest_selected_final_rows.csv`
- Focused three-task/three-seed masked-local evidence:
  - `results/masked_naturalization_ablation_20260510/evaluation_current/`
  - `results/masked_naturalization_ablation_20260510_seed20260510/evaluation_current/`
  - `results/masked_naturalization_ablation_20260510_seed20260511/evaluation_current/`
  - `results/masked_naturalization_ablation_20260510_seed20260512/evaluation_current/`
- Tables/docs:
  - `paper_siga/drafts/ablation_status_tables_20260510.tex`
  - `paper_siga/drafts/masked_naturalization_ablation_table_20260510.tex`
  - `paper_siga/drafts/publication_ablation_effective_resolution_status_20260510.tex`
- Scripts:
  - `assets/naturalization_projection_ablation_aggregation_20260510.py`
  - `assets/evaluate_masked_naturalization_ablation_20260510.py`
  - `assets/export_masked_naturalization_publication_summary_20260510.py`

### Coral mesh-space generated-root

- Current complete local evidence:
  - `results/publication_coral_mesh_space_20260510/coral_mesh_space_metrics.csv`
  - `results/publication_coral_mesh_space_20260510/manifest.csv`
  - `results/publication_coral_mesh_space_20260510/summary.json`
  - selected table row: `results/publication_coral_mesh_space_20260510/coral_frontier_branch/full_srt/depth_02/coral_frontier_branch_full_srt_depth_02_white_pbr.glb`
  - selected OBJ: `results/publication_coral_mesh_space_20260510/coral_frontier_branch/full_srt/depth_02/coral_frontier_branch_full_srt_depth_02.obj`
  - selected preview: `results/publication_coral_mesh_space_20260510/coral_frontier_branch/full_srt/depth_02/coral_frontier_branch_full_srt_depth_02_white_preview.png`
- Integrated baseline manifest:
  - `results/publication_baseline_metrics_20260510/publication_baseline_master_manifest_20260510.csv`
  - `results/publication_baseline_metrics_20260510/summary.json`
- Scripts:
  - `assets/mesh_space_trivial_recursion_baseline_20260510.py`
  - `assets/publication_baseline_metrics_20260510.py`

### Effective-resolution / zoom-retention

- Proxy schema/status:
  - `results/publication_ablation_metrics_20260510/effective_resolution_schema.csv`
  - `results/publication_ablation_metrics_20260510/matrix_coverage_summary.csv`
  - `results/publication_ablation_metrics_20260510/claim_safe_miniset_20260510.csv`
- Comparison table:
  - `paper_siga/drafts/effective_resolution_status_table_20260510.tex`
  - `paper_siga/drafts/publication_ablation_effective_resolution_status_20260510.tex`
- Script:
  - `assets/effective_resolution_metrics_20260510.py`

## 2. Row Status Summary

### Same-root matrix

Current selected-final coverage from `matrix_coverage_summary.csv`:

| variant | status | evidence boundary |
|---|---|---|
| traditional | partial/proxy | 30 available, 8 missing; 29 local meshes, no local GLBs. Useful as inventory/proxy, not closed same-root proof. |
| direct | partial | 8 available, 8 missing; only 2 local meshes. Strongest use is matched subset, not full matrix. |
| final-only | partial | 4 available, 12 missing; local tree/vine subset only. |
| prune | partial | 5 available, 11 missing; vine/tree compete subset is strongest. |
| bridge | blocked/diagnostic | 1 available, 15 missing; insufficient for claim. |
| proposed | partial/proxy | 15 available, 10 missing; local meshes exist, but no local GLB/render QA in this matrix summary. |

Claim-safe miniset:

- `SR-vine-projection-3col`: complete as metrics subset for direct/final-only/prune; main candidate only after render/GLB QA.
- `SR-tree-projection-3col`: complete as metrics subset; backup main or appendix.
- Strict six-row same-root matrix remains blocked by missing traditional/bridge/proposed rows for the exact same root/depth/operator.

### Naturalization matrix

Current selected-final coverage:

| variant | status | evidence boundary |
|---|---|---|
| rule-only | partial | 4 available, 22 missing; selected L-system GLB only in publication summary. |
| no-N | partial | 8 available, 18 missing; alpha-0 masked-executor control, incomplete matrix. |
| weak blend | partial | 8 available, 18 missing; selected L-system/coral/pyrite GLBs, appendix candidate. |
| masked local-N | partial/main-local claim only | 22 available, 13 missing; three-task/three-seed focused ablation supports local surface continuity under projection, not global topology repair. |
| global-N | proxy/diagnostic | 12 available, 22 missing; diagnostic negative/control rows, no main success claim. |
| with projection | partial | 35 available, 17 missing; projection-axis evidence, separate from naturalization-axis claim. |
| without projection | blocked/partial | 4 available, 22 missing; insufficient for causal naturalization-vs-projection claim. |
| post-hoc repair baseline | proxy/appendix | 5 available, 0 missing; must stay separate from recursive projection/naturalization. |

Focused masked-local table:

- `paper_siga/drafts/masked_naturalization_ablation_table_20260510.tex` is the cleanest current naturalization evidence: botanical_root, coral_frontier, and ifs_crystal across rule-only/final-only/per-depth no-N/weak/global/masked, aggregated over three deterministic seeds.
- This can support a cautious main-text statement about masked local naturalization as a local surface-continuity operator under per-depth projection.
- It cannot support full naturalization matrix closure, topology repair, mask leakage, root reachability, or handle-graph proof by itself.

### Coral mesh-space generated-root

Status: complete as negative-control row.

- `publication_coral_mesh_space_20260510` has 12 local rows across two grammars, two S/R/T variants, and depths 0-2.
- Recommended table row in `summary.json`: `coral_frontier_branch full_srt depth=2 direct merge`.
- Metrics: vertices 754194, faces 252000, raw face components 250404, occupancy components 8, occupancy LCR 0.9917599502487562, file size 31.281006 MB, copy repetition score 1.0.
- Paper boundary: this is a direct mesh copy-paste negative control with no generator call, projection, weld, boolean, remesh, or repair. High occupancy LCR must not be read as recursive success because raw face islands and copy repetition remain the diagnostic failure.

### Effective-resolution / zoom-retention

Status: proxy.

- Current table has two comparison groups:
  - crystal/coral: DLA baseline vs pyrite recursive depth stage, scale improvement 4.09, detail ratio 2.46.
  - tree/vine: SC tree baseline vs ours vine stage5, scale improvement 3.79, detail ratio 0.54.
- Existing schema covers local feature scale, terminal detail count, zoom retention proxy, face/GLB size, and full-object high-res blow-up estimate.
- Paper boundary: appendix/status or carefully caveated main proxy only. It does not prove same-budget effective-resolution superiority or universal terminal-detail improvement.

## 3. Minimal Next Commands

All commands are local, selected-final-only, and do not recursively scan giant directories.

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
python assets/publication_ablation_selected_final_aggregation_20260510.py --out-dir results/publication_ablation_metrics_20260510
```

Rebuild the selected-final ablation inventory, coverage summary, claim-safe miniset, queue, and effective-resolution schema from named CSV/JSON inputs.

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
python assets/publication_baseline_metrics_20260510.py --out-dir results/publication_baseline_metrics_20260510
```

Rebuild the baseline master manifest, including the current coral mesh-space row and any locally available Hunyuan/TRELLIS rows.

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
python assets/evaluate_masked_naturalization_ablation_20260510.py --asset-dir results/masked_naturalization_ablation_20260510 --out-dir results/masked_naturalization_ablation_20260510/evaluation_current
python assets/evaluate_masked_naturalization_ablation_20260510.py --asset-dir results/masked_naturalization_ablation_20260510_seed20260511 --out-dir results/masked_naturalization_ablation_20260510_seed20260511/evaluation_current
python assets/evaluate_masked_naturalization_ablation_20260510.py --asset-dir results/masked_naturalization_ablation_20260510_seed20260512 --out-dir results/masked_naturalization_ablation_20260510_seed20260512/evaluation_current
```

Refresh the local masked-naturalization metrics for the existing three-seed task directories.

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth
python assets/effective_resolution_metrics_20260510.py --out-dir results/effective_resolution_metrics_20260510
```

Refresh proxy effective-resolution comparisons from existing named metric sources.

## 4. Main Text vs Appendix / Diagnostic

Can enter main text with careful wording:

- Coral mesh-space generated-root as a negative-control row, because the current local evidence is complete and integrated into the baseline master manifest.
- Same-root vine/tree direct vs final-only vs prune as a narrow matched subset trend, provided the text says it is not the full same-root matrix.
- Focused masked-local naturalization table as local surface-continuity evidence under per-depth projection, not as topology repair.
- Effective-resolution proxy only if worded as selected-case accounting/diagnostic, not as proof.

Should stay appendix/status:

- Full same-root coverage table.
- Full naturalization coverage table.
- Naturalization L-system selected GLB status rows until source meshes, topology/root/mask metrics, and with/without projection controls are localized.
- Coral/pyrite weak-vs-masked local-N stress insets.
- Post-hoc repair baseline.
- Global-N rows.
- Effective-resolution table if the main paper is already overloaded.

Should stay diagnostic/blocked:

- Bridge same-root as a positive row.
- Strict six-row same-root matrix closure.
- Full naturalization/projection matrix closure.
- Naturalization topology/root reachability/mask leakage claims.
- Strong same-budget effective-resolution or zoom-retention superiority.
