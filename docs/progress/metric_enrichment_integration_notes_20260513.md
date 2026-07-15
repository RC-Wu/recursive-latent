# Metric Enrichment Integration Notes - 2026-05-13

Scope: read-only inspection of `paper_siga/main.tex`, current included tables, and the 2026-05-13 metric enrichment outputs. No paper files were edited.

Primary inputs:

- `assets/mesh_metric_enrichment_20260513.py`
- `results/metric_enrichment_20260513/priority_mesh_metric_enrichment_20260513.csv`
- `results/metric_enrichment_20260513/metric_enrichment_block_summary_20260513.csv`
- `results/metric_enrichment_20260513/masked_naturalization_topology_summary_20260513.csv`
- `paper_siga/main.tex`
- `paper_siga/figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`
- `paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`
- `paper_siga/drafts/masked_naturalization_main_table_20260511.tex`

## Recommended Integrations

### 1. Main-text caveat plus appendix mesh-diagnostic summary for Experiment 3

This is the safest publishable integration. It does not alter the claim hierarchy: the main structural metrics remain occupancy or surface-voxel connectivity, while the enrichment CSV adds raw face-edge and welded-fragment mesh diagnostics as a cautionary supplement.

Safe exact numbers from `metric_enrichment_block_summary_20260513.csv`:

| Block | Requested | Measured | Skipped | Welded single | Watertight | Median boundary edges | Median nonmanifold edges | Median triangle quality |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Experiment 3 priority assets | 65 | 52 | 13 | 1 | 0 | 154,193.5 | 0.0 | 0.727 |
| V24 main-comparison scaffolds | 15 | 15 | 0 | 0 | 0 | 934.0 | 944.0 | 0.566 |
| Real-case projection/naturalization inputs | 22 | 22 | 0 | 8 | 8 | 1,892.5 | 0.0 | 0.643 |
| Masked-naturalization manifest inputs | 18 | 18 | 0 | 9 | 18 | 0.0 | 0.0 | 0.692 |

Safe exact method-level summary for main-ready, successful, unique rows in `priority_mesh_metric_enrichment_20260513.csv`:

| Method id | Rows | Median raw comp. | Median welded comp. | Welded comp. range | Median boundary edges | Median nonmanifold edges | Median triangle quality | Watertight |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `hunyuan_root_meshcopy` | 4 | 272,162.5 | 152,126.5 | 79,496-256,216 | 820,314.5 | 0.0 | 0.697 | 0 |
| `trellis2_generatedroot_meshcopy` | 6 | 182,031.0 | 69,565.5 | 36,037-145,803 | 548,062.0 | 0.0 | 0.745 | 0 |
| `trellis2_oneshot_image` | 6 | 5,816.0 | 85.5 | 5-1,522 | 42,457.0 | 0.5 | 0.747 | 0 |
| `trellis2_root_latentcopy` | 2 | 95.0 | 80.5 | 26-135 | 7,661.0 | 2,660.5 | 0.774 | 0 |
| `ps_rslg` | 9 | 7,444.0 | 132.0 | 1-442 | 38,764.0 | 0.0 | 0.596 | 0 |

Interpretation that is safe:

- Mesh-space generated-root copy baselines remain extremely fragmented under raw face-edge and tolerance-welded mesh diagnostics.
- PS-RSLE rows are not watertight and should not be described as topology-clean.
- The enrichment supports the existing caution in Table `tab:experiment3-sparse-latent-vs-mesh-space`: high occupancy or surface LCR is not a watertight topology proof.
- Triangle quality should be kept as a mesh/export diagnostic, not as evidence of structural superiority. PS-RSLE median triangle quality is lower than several baselines in this enrichment, so do not frame this as a universal mesh-quality win.

Exact PS-RSLE rows that can be cited selectively, preferably in appendix/supplement:

| Case | Variant | Vertices | Triangles | Raw comp. | Welded comp. | Largest welded face ratio | Boundary edges | Nonmanifold edges | Watertight | Triangle quality |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| bismuth | V21 stepped transform textured | 16,960 | 11,166 | 2,973 | 179 | 0.674 | 15,848 | 0 | false | 0.588 |
| coral | V24 coral frontier textured | 17,786 | 14,342 | 1,944 | 131 | 0.764 | 17,114 | 0 | false | 0.419 |
| coral | strict visual matched texture | 146,885 | 117,340 | 19,659 | 2 | 1.000 | 139,122 | 0 | false | 0.866 |
| pyrite | V24 lattice textured | 28,641 | 18,498 | 5,473 | 187 | 0.795 | 27,118 | 0 | false | 0.596 |
| pyrite | strict visual matched texture | 294,399 | 226,088 | 50,396 | 1 | 1.000 | 262,572 | 0 | false | 0.866 |
| root fan | V25 root fan textured | 40,410 | 27,168 | 7,444 | 442 | 0.365 | 38,764 | 0 | false | 0.215 |
| tree crown | V25 tree crown textured | 99,455 | 74,138 | 14,172 | 169 | 0.948 | 96,428 | 0 | false | 0.551 |

Main vs appendix placement:

- Main text: add one caveat sentence after the Experiment 3 table discussion, not a new main table.
- Appendix/supplement: add the method-level mesh-diagnostic table above, or a compact version with rows for method id, count, median raw comp., median welded comp., median boundary edges, median nonmanifold edges, watertight count.

Suggested edit location:

- `paper_siga/main.tex`, after the paragraph ending near line 625 that starts "The comparison separates visual asset quality from structural diagnostics."
- `paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`, caption already contains the correct caveat. It can receive one short sentence if there is room.

Suggested main-text snippet:

```latex
The enriched CPU mesh diagnostics reinforce this separation: among the main-ready successful rows, PS-RSLE outputs have lower median tolerance-welded fragmentation than mesh-space generated-root copy baselines (132 welded components over 9 PS-RSLE rows, versus 69,565.5 over 6 Trellis2 generated-root copy rows and 152,126.5 over 4 Hunyuan root-copy rows), but none of these rows is watertight. We therefore use these metrics as mesh/export diagnostics only, not as topology-cleanliness or physical-simulation evidence.
```

Suggested appendix table snippet:

```latex
\begin{table*}[t]
\centering
\small
\setlength{\tabcolsep}{4pt}
\caption{CPU mesh-diagnostic enrichment for main-ready successful Experiment 3 rows. Raw comp. counts face-edge connected components. Welded comp. repeats the diagnostic after quantized vertex welding at tolerance $0.002$. These are export/fragmentation diagnostics and do not replace the occupancy or surface-voxel structural metrics used in the main claims.}
\label{tab:experiment3-mesh-enrichment-20260513}
\begin{tabular}{lrrrrrrr}
\toprule
Method & Rows & Raw comp. med. & Welded comp. med. & Welded range & Boundary med. & Nonmanifold med. & Watertight \\
\midrule
Hunyuan root+mesh-copy & 4 & 272,162.5 & 152,126.5 & 79,496--256,216 & 820,314.5 & 0.0 & 0/4 \\
Trellis2 root+mesh-copy & 6 & 182,031.0 & 69,565.5 & 36,037--145,803 & 548,062.0 & 0.0 & 0/6 \\
Trellis2 one-shot & 6 & 5,816.0 & 85.5 & 5--1,522 & 42,457.0 & 0.5 & 0/6 \\
Trellis2 latent-copy & 2 & 95.0 & 80.5 & 26--135 & 7,661.0 & 2,660.5 & 0/2 \\
PS-RSLE & 9 & 7,444.0 & 132.0 & 1--442 & 38,764.0 & 0.0 & 0/9 \\
\bottomrule
\end{tabular}
\end{table*}
```

### 2. Appendix-only topology diagnostic for masked naturalization

This is safe only as a small supplement to Experiment 4. Do not promote it as a main topology result, because it is 18 manifest-input meshes summarized over only three rows per variant and does not replace the existing four-task, three-seed trace/surface proxy table.

Safe exact numbers from `masked_naturalization_topology_summary_20260513.csv`:

| Variant | Raw comp. median | Welded comp. median | Boundary median | Nonmanifold median | Triangle quality median | Watertight |
|---|---:|---:|---:|---:|---:|---:|
| raw grammar proposal | 16 | 16 | 0 | 0 | 0.703 | 3/3 |
| final-only projection repair | 4 | 4 | 0 | 0 | 0.690 | 3/3 |
| per-depth projection | 4 | 4 | 0 | 0 | 0.688 | 3/3 |
| per-depth weak naturalization | 1 | 1 | 0 | 0 | 0.688 | 3/3 |
| per-depth masked naturalization | 1 | 1 | 0 | 0 | 0.691 | 3/3 |
| per-depth global naturalization | 1 | 1 | 0 | 0 | 0.694 | 3/3 |

Interpretation that is safe:

- In this small manifest-input subset, weak, masked, and global naturalization variants are single-component after raw and welded mesh diagnostics, while raw grammar proposals and projection-only variants remain multi-component by median.
- This supports the statement that masked local naturalization is compatible with projected state and can improve local mesh continuity in this subset.
- It does not show that masked naturalization is the topology mechanism. Projection remains the structural mechanism in the main paper.
- It does not distinguish masked from global topology-wise in this subset: both have median raw/welded component count 1 and 3/3 watertight meshes. The existing main-text argument for masked over global should remain based on locality, rendered-asset quality, and old-state mutability, not topology.

Main vs appendix placement:

- Main text: at most add one sentence to the Experiment 4 paragraph saying a supplementary CPU mesh check is consistent with the surface-proxy trend on the manifest-input subset.
- Appendix/supplement: add the six-row table above.
- Do not add these topology columns to the main Experiment 4 table. The current main table has no std columns and focuses on roughness, normal consistency, artifacts, drift, handle survival, quality, and failure rate; keep that structure.

Suggested edit location:

- `paper_siga/main.tex`, after the Experiment 4 paragraph near line 631.
- Optional new appendix table near the moved ablation/status material around line 812.
- `paper_siga/drafts/masked_naturalization_main_table_20260511.tex` should not be edited for this integration.

Suggested main-text snippet:

```latex
A supplementary CPU mesh check on the 18 masked-naturalization manifest inputs is consistent with this interpretation: projection-only variants reduce the median raw mesh component count from 16 to 4, while weak, masked-local, and global naturalization are single-component in this small mesh subset. Because global and masked variants tie on these topology diagnostics, we use this check only as a supplement; the main preference for masked local naturalization comes from locality and rendered-quality proxies, not from a topology-cleanliness claim.
```

Suggested appendix table snippet:

```latex
\begin{table}[t]
\centering
\small
\caption{CPU mesh topology diagnostics for the masked-naturalization manifest-input subset. Each row summarizes three meshes. Raw and welded component counts are mesh diagnostics; they do not replace the handle-state gates in Table~\ref{tab:masked-naturalization-ablation-20260510}.}
\label{tab:masked-naturalization-mesh-topology-20260513}
\begin{tabular}{lrrrrrr}
\toprule
Variant & Raw comp. med. & Weld comp. med. & Boundary med. & Nonmanifold med. & Quality med. & Watertight \\
\midrule
raw grammar proposal & 16 & 16 & 0 & 0 & 0.703 & 3/3 \\
final-only projection repair & 4 & 4 & 0 & 0 & 0.690 & 3/3 \\
per-depth projection & 4 & 4 & 0 & 0 & 0.688 & 3/3 \\
per-depth weak naturalization & 1 & 1 & 0 & 0 & 0.688 & 3/3 \\
per-depth masked naturalization & 1 & 1 & 0 & 0 & 0.691 & 3/3 \\
per-depth global naturalization & 1 & 1 & 0 & 0 & 0.694 & 3/3 \\
\bottomrule
\end{tabular}
\end{table}
```

## Existing Table and Caption Edits

### `figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`

Current caption is already appropriately conservative: it defines surface-voxel metrics, identifies welded components as a tolerance-based mesh-fragmentation diagnostic, and routes visual quality to the figure. No required table-column change.

Optional caption addition:

```latex
Raw and welded mesh components are retained as export-fragmentation diagnostics and are not watertight-topology proof.
```

Do not add standard-deviation columns.

### `drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`

Current caption already says LCR is not topology proof and high occupancy LCR can coexist with thousands of raw mesh islands. That is aligned with the enrichment. The only useful update is to reference the appendix enrichment table if added:

```latex
Additional CPU mesh-fragmentation diagnostics are reported in Table~\ref{tab:experiment3-mesh-enrichment-20260513}.
```

### `main.tex` Experiment 3 paragraph

The paragraph near line 625 should receive a caveat sentence if space permits. Use the main-text snippet above. It strengthens rigor without expanding claims.

### `main.tex` Experiment 4 paragraph and table caption

The paragraph near line 631 is already strong and caveated. Add only the short supplementary CPU mesh sentence above if the appendix topology table is included.

Optional caption addition for `tab:masked-naturalization-ablation-20260510`:

```latex
Supplementary raw/welded mesh component diagnostics for the manifest-input subset are reported separately and are not used to rank topology-cleanliness between masked and global naturalization.
```

Do not add raw/welded topology columns to the main Experiment 4 table.

## Caveats and Blockers

- Thirteen of 65 Experiment 3 priority assets were skipped by the enrichment script, mostly because some OBJ files exceed the face-count limit. Do not state full coverage for Experiment 3 mesh diagnostics.
- None of the main-ready successful Experiment 3 method groups has watertight positive rows in the enrichment summary. Any wording such as "topology-clean", "watertight", "manifold", or "solves topology" would be unsupported.
- Raw face-edge components can be overly harsh for exported textured assets and can disagree with occupancy/surface-voxel metrics. Keep the current metric hierarchy: occupancy/surface-voxel for structural support, raw/welded mesh components for export fragmentation.
- The masked-naturalization topology table has only three meshes per variant and uses manifest-input meshes, not the full four-task main Experiment 4 table. It should be appendix-only.
- The masked-naturalization topology subset does not separate masked local naturalization from global naturalization on topology: both are median one component and 3/3 watertight. The masked-vs-global preference must continue to come from locality, quality, and old-state mutability.
- Triangle-quality medians should not be used as a main superiority claim. Several baselines have higher median triangle quality than PS-RSLE in the enrichment summary.
- The current `main_experiment_selected_metrics_table_corrected_V67B_20260512.tex` appears internally aligned with the "no std columns in main tables" constraint; avoid widening it unless the appendix table is added.
