# Experiment Narrative Review - 2026-05-13

Scope: read-only review of `paper_siga/main.tex`, experiment/discussion/appendix captions, `paper_siga/drafts/*.tex`, and `paper_siga/figures/*metrics*.tex` / `*table*.tex`. No paper source, table source, git stage, commit, or push action was performed. This file is the only written output of this review.

## Executive Assessment

The current experiment section is much cleaner than the older status-report draft. The main line now reads as:

1. Experiment 2: projection inside the recursive transition enforces per-depth executable state.
2. Experiment 3: one-shot generation, latent copy, and mesh-space copy are novelty/negative controls that do not provide rule-readable recursive state.
3. Experiment 4: masked local naturalization is a local surface-realization aid under the projection gate, not the structural mechanism.

This separation is mostly successful. The strongest remaining risks are not in the main projection/naturalization tables, which are now mean-only and claim-aligned, but in appendix/status material that still contains older PS-RSLG naming, effective-resolution/export/GLB inventory language, and "selected positive" labels that can blur the evidential hierarchy if cited too aggressively.

## Main Findings

### 1. Experiment 2 claim is now properly centered

Target: `paper_siga/main.tex:537-582`, `drafts/projection_ablation_main_table_20260511.tex`.

Current status:

- The paragraph at `main.tex:539-541` correctly states that the empirical claim is executable-state change, not terminal mesh cleanup.
- `tab:projection-ablation` now uses the right compact columns: `Occ. LCR`, `Root reach.`, `Orphan active`, `Handle survival`, `Exec. pass`.
- No standard-deviation columns remain in `drafts/projection_ablation_main_table_20260511.tex`.
- The caption at `main.tex:582` correctly says values are means and that handle columns are deterministic trace/mesh proxies, not recovered handle metrics from arbitrary textured GLBs.

Recommended small tightening:

- `main.tex:555` says conservative occupancy competition is "the strongest stability baseline." This is mostly fine, but "baseline" could be read as evidence for the central state claim. Safer replacement:

```latex
Conservative occupancy competition is the most stable geometry-level depth diagnostic in the current operator set; fork and side-branch variants increase expressive capacity but consume more sparse support.
```

- `main.tex:574` says connector-aware projection and full PS-RSLE "keep the zoomed support root-attached and available for later rules." This is acceptable because the table caption defines proxies, but the figure itself is visual. Safer replacement:

```latex
Final-only projection improves terminal occupancy but does not repair the recursive active state; connector-aware per-depth projection and full PS-RSLE correspond to the trace rows that keep active support root-attached before later rules consume it.
```

### 2. New depth-scaling table is useful but must stay secondary

Target: `main.tex:559-568`, `drafts/depth_scaling_diagnostics_20260513.tex`.

Current status:

- The new compact table is a good main-text addition if space allows.
- It is framed correctly as geometry-level depth scaling, not handle-state admission.
- It has no std columns and no export/PBR fields.

Recommended role:

- Keep it in main only if the paper needs a compact quantitative bridge between depth curves and projection ablation.
- Otherwise move it to appendix and leave the depth curves in main.
- Do not add mesh topology, watertightness, render quality, or GLB size to this table.

Best wording if retained:

```latex
This table only shows that selected realized meshes remain connected and envelope-stable as explicit depth increases; it does not show that arbitrary recursive candidates are admissible executable states.
```

### 3. Experiment 3 claim is mostly distinct, with one wording risk

Target: `main.tex:592-638`, `drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`, `figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`.

Current status:

- The narrative correctly separates the novelty gate from the projection/state-validity gate.
- The table caption says occupancy components and LCR are diagnostics, not topology proof.
- The text at `main.tex:598` correctly says handle-level validity is tested by projection/trace ablations rather than this table.
- `figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex` has no std columns and no GLB/PBR/export columns.

Risk:

- `drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex:36` uses "visually strong claim-bearing cases." This is slightly stronger than needed because the claim is a novelty/diagnostic comparison, not visual quality as evidence of state validity.

Recommended caption replacement phrase:

```latex
The table keeps only quality-gated cases used for the novelty comparison: tree crown, bismuth, coral, and a caveated pyrite/lattice row.
```

Target: `main.tex:638`.

The sentence "These results support the claim that a projection-stabilized sparse-latent executor can produce selected finite-depth recursive assets across classical targets" is defensible but broad. Safer:

```latex
These results support a selected-asset compatibility claim: under fixed target-matched protocols, projected sparse-latent execution can realize finite-depth recursive assets across several classical target families, while the state-validity claim remains tied to the projection ablation.
```

### 4. Experiment 4 claim is clean but "Quality" should remain explicitly proxy-level

Target: `main.tex:640-660`, `drafts/masked_naturalization_main_table_20260511.tex`.

Current status:

- The current text correctly says masked naturalization does not repair executable state without projection.
- The table is mean-only and uses the right columns: roughness, normal, artifacts, drift, handle survival, quality, execution pass.
- Caption at `main.tex:660` says all columns are deterministic proxies.

Risk:

- The column label `Quality` is compact but can be misread as perceptual quality. The caption defines it as `rendered-asset quality`, but that still sounds broader than the deterministic score.

Recommended options:

- Best if table width allows: rename `Quality` to `Quality proxy`.
- If table source stays unchanged, add one phrase to caption:

```latex
The quality column is the deterministic rendered-asset quality proxy from the ablation script, not a human perceptual score.
```

Target: `main.tex:652`.

The masked-naturalization figure caption is strong but safe. The phrase "improves local boundary smoothness" is supported by roughness/normal metrics. Keep as is.

### 5. Discussion is aligned

Target: `main.tex:706-708`.

Current status:

- Discussion correctly identifies projection ablation as strongest evidence.
- It correctly states masked local realization is secondary and projection remains structural.
- It avoids topology, material consistency, or universal resolution claims.

No required change.

## Caption Risk Audit

### Safe main captions

- `main.tex:547`, projection depth curves: safe; explicitly says geometry-level diagnostic and points state validity to Table `tab:projection-ablation`.
- `main.tex:563`, depth-scaling table: safe; explicitly excludes handle validity, perceptual quality, and executable-state admission.
- `main.tex:582`, projection ablation table: safe and claim-aligned.
- `main.tex:604`, Experiment 3 figure: safe; identifies four-case quality-gated visual novelty gate.
- `figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex:6`: safe; defines surface voxel and welded diagnostics and separates visual quality.
- `main.tex:660`, masked-naturalization table: safe if `Quality` is understood as proxy-level.

### Captions needing small downgrades

- `main.tex:687`, pyrite depth showcase: "strongest current crystal/symmetry visual line" is acceptable but slightly promotional. Safer: "preferred crystal/lattice visual diagnostic."
- `main.tex:695`, coral depth showcase: "rule-native connected-scaffold alternative" is acceptable, but avoid reading it as a general replacement for DLA. Safer: "a selected rule-native connected-scaffold example."
- `main.tex:995`, crystal guide sweep appendix: "strongest current crystal/symmetry positive case" should be downgraded in appendix to "strongest current crystal/lattice diagnostic case" unless there is a dedicated symmetry metric table in the same section.
- `main.tex:1019`, DLA smoke test: "strongest route in this test" is fine, but keep it appendix-only.

### Captions already doing the right caveating

- `main.tex:679`: connected-scaffold visual evidence only.
- `main.tex:699`: rendered-asset diagnostics are not main evidence.
- `main.tex:832-851`: mesh diagnostic captions explicitly do not replace projection/handle-state evidence.
- `main.tex:947-955`, `main.tex:963`, `main.tex:971-979`, `main.tex:987`: appendix visual captions consistently avoid topology/material-overclaim.

## Table Input Audit

### Main-ready tables

`drafts/projection_ablation_main_table_20260511.tex`

- Good main table.
- Mean-only.
- No std columns.
- No export/PBR fields.
- Method name is `PS-RSLE`, consistent with main text.

`drafts/depth_scaling_diagnostics_20260513.tex`

- Good compact geometry diagnostic.
- No std/export/PBR.
- Keep secondary to projection table.

`drafts/masked_naturalization_main_table_20260511.tex`

- Good main Experiment 4 table.
- Mean-only.
- No std columns.
- Consider `Quality proxy` label or caption definition.

`drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`

- Good compact Experiment 3 table.
- No std columns.
- No MB/GLB/PBR fields.
- Consider replacing "selected positive" statuses with "selected PS-RSLE" or "selected proxy row" to avoid treating occupancy as positive state proof.

`figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`

- Good target-matched diagnostic table.
- No std columns.
- No export/PBR fields.
- `Box dim.` is less central than the other columns; okay if width allows, removable if space tight.

### Appendix-only tables

`drafts/experiment3_mesh_enrichment_20260513.tex`

- Correctly appendix-only.
- Contains watertight counts, raw components, welded components, boundary medians.
- Should never be cited as topology success; use as mesh-fragmentation caveat.

`drafts/masked_naturalization_topology_audit_20260513.tex`

- Correctly appendix-only.
- Shows all rows watertight in this small manifest subset, but the main text correctly says this is not recursive-state validity.
- Do not use it to distinguish masked from global topology-wise, since weak/masked/global all have median raw/welded component count 1 and watertight 3/3.

`drafts/ablation_status_tables_20260510.tex`

- Appendix/status only.
- Captions are appropriately caveated.
- Risk: rows such as "main proxy + appendix gaps" can look like main evidence if referenced without context. Prefer "status inventory" language in surrounding text.

### Risky old or non-main tables

`drafts/ablation_and_resolution_status_tables_20260510.tex`

- Contains `effective-resolution` table with `Scale impr.`, `Detail ratio`, `One MB`, `Rec. MB`.
- Keep out of main text. If retained in supplement, label as exploratory zoom/detail proxy and asset-budget diagnostic.
- Do not cite as universal detail superiority.

`drafts/publication_ablation_effective_resolution_status_20260510.tex`

- Contains `Local GLB`, `Publication status`, `face / GLB size`, `full-object high-res blow-up`.
- This is internal publication inventory, not paper evidence.
- Best placement: omit from paper appendix or keep only in internal progress docs.

`drafts/gen3d_baseline_summary_table_20260510.tex`

- Uses old `PS-RSLG` naming and MB/file-size columns.
- Also says Hunyuan is reserved for future evaluation, which conflicts with the current Experiment 3 table that includes Hunyuan text-root mesh-copy rows.
- Do not include or cite in the current paper.

`drafts/masked_naturalization_ablation_table_20260510.tex`

- Older table includes `Score reports mean/std`.
- Superseded by `drafts/masked_naturalization_main_table_20260511.tex`.
- Do not cite as current main evidence.

`drafts/experiment3_sparse_latent_vs_mesh_space_table_supplement_20260511.tex`

- Contains old `PS-RSLG` naming and "selected positive" statuses.
- If included in appendix, update naming to `PS-RSLE` and downgrade statuses to "selected diagnostic", "proxy row", or "supplemental coverage."

`figures/claim_aligned_metric_summary_table_20260509.tex`

- Useful historical summary, but has "textured asset exists; neutral/zoom QA missing" and huge mesh/face component ranges.
- Keep as diagnostic appendix only, or omit if the current cleaner tables supersede it.

## Metrics: Evidential Role Consistency

### Primary state metrics

Use in main claim:

- `Root reach.`
- `Orphan active`
- `Handle survival`
- `Exec. pass`

These belong in Experiment 2 and, secondarily, Experiment 4. They should be described as controlled trace/mesh proxies measured before later rules consume the state.

### Geometry/support diagnostics

Use in main text as supporting diagnostics:

- `Occ. LCR`
- `Occ. comp.`
- `Surf. comp. r0`
- `Surf. LCR r0`
- `Surf. comp. r1`
- depth-scaling final component/LCR and bbox drift

These support coherent occupied support and depth behavior, not handle-state validity.

### Mesh/export diagnostics

Keep appendix or caveat-only:

- raw face components
- welded components
- boundary edges
- nonmanifold edges
- watertight counts
- face count
- GLB/MB/file size
- render/import warnings

These are valuable because they show disagreements between occupancy connectivity and mesh fragmentation, but they should not enter the central claim.

### Local realization proxies

Use for Experiment 4 only:

- roughness
- normal consistency
- local artifacts
- topology drift proxy
- quality proxy

Do not generalize these to Experiment 2 or 3 unless the same deterministic script/protocol is generalized and validated.

## Claims Under Test: Recommended One-Line Map

Suggested experiment framing if the section needs a compact roadmap:

```latex
Experiment 2 tests the executable-state invariant: projection must occur before later rules read the state. Experiment 3 tests whether ordinary generation or copy-based recursion can replace that state machinery. Experiment 4 tests a secondary realization question: once projection has made the state admissible, masked local naturalization can improve local surface proxies without becoming the topology mechanism.
```

This would make the claims under test more explicit than the current paragraph, though the current version is already mostly acceptable.

## Best New Metrics to Promote

### Main text

1. Projection table metrics: `Root reach.`, `Orphan active`, `Handle survival`, `Exec. pass`.
   - Already in main; these are the most important metrics.

2. Compact depth-scaling diagnostics: final component count, final LCR, vertices/faces d0-to-d6, max bbox drift.
   - Worth keeping in main only as geometry-level depth support.

3. Experiment 3 compact occupancy table: `Occ. comp.`, `LCR`.
   - Worth keeping in main for novelty comparison, but with caveat that it is not handle-state proof.

4. Experiment 4 local-quality table: roughness, normal, artifacts, drift, handle survival, quality proxy, exec pass.
   - Worth keeping in main as the masked-local realization result.

### Appendix

1. Experiment 3 mesh enrichment: raw components, welded components/range, boundary median, watertight count.
   - Strong appendix diagnostic showing occupancy and mesh fragmentation can diverge.

2. Masked-naturalization topology audit.
   - Appendix only; useful as a small mesh-fragmentation check, not a topology or state-validity claim.

3. Full Experiment 3 eight-case supplement.
   - Appendix only after PS-RSLG naming and "selected positive" statuses are cleaned.

4. Status/inventory tables.
   - Keep as supplemental progress/status if needed, but avoid main citations.

### Do Not Promote

- Standard deviations in main tables.
- GLB size / MB columns.
- PBR/export availability.
- Effective-resolution / zoom-retention proxy as a main claim.
- CLIP/aesthetic/GPT-4o visual scores unless prompt/view protocols are standardized and reproducible.
- Watertightness as a positive claim for PS-RSLE.

## Priority Fix List

1. Rename remaining appendix `PS-RSLG` to `PS-RSLE` where those tables are still included or likely to be cited.
   - Targets: `drafts/experiment3_sparse_latent_vs_mesh_space_table_supplement_20260511.tex`, `drafts/gen3d_baseline_summary_table_20260510.tex` if retained.

2. Downgrade "selected positive" in appendix diagnostic tables.
   - Prefer "selected diagnostic", "selected PS-RSLE row", or "proxy-positive+caveat".

3. Keep old effective-resolution/export/GLB inventory tables out of the paper main flow.
   - Targets: `drafts/ablation_and_resolution_status_tables_20260510.tex`, `drafts/publication_ablation_effective_resolution_status_20260510.tex`, `drafts/gen3d_baseline_summary_table_20260510.tex`.

4. Add a caption phrase defining `Quality` in the masked naturalization table as a deterministic proxy if the column cannot be renamed.

5. Slightly downgrade "strongest current crystal/symmetry positive case" in appendix captions unless a symmetry metric table is cited immediately.

## Bottom Line

The current main experiment section is publication-directionally sound: Experiment 2 carries the central per-depth admissible executable-state claim; Experiment 3 is a novelty/control comparison; Experiment 4 is a local realization ablation under projection. The main tables no longer have std columns or broad export/PBR inventory fields. The biggest cleanup remaining is appendix hygiene: remove old PS-RSLG naming, keep effective-resolution/GLB/MB/status tables away from claim-bearing text, and consistently label mesh/render/topology quantities as diagnostics rather than proof.
