# Metric Extension Linnaeus - 2026-05-13

Scope: CPU-safe extension of the existing 2026-05-13 mesh metric enrichment. I did not edit `paper_siga/main.tex`, did not stage/commit/push, and did not load large OBJ files. New writes are limited to this report and new files under `results/metric_enrichment_20260513/`.

## Inputs Audited

- `assets/mesh_metric_enrichment_20260513.py`
- `results/metric_enrichment_20260513/priority_mesh_metric_enrichment_20260513.csv`
- `results/metric_enrichment_20260513/metric_enrichment_block_summary_20260513.csv`
- `results/metric_enrichment_20260513/masked_naturalization_topology_summary_20260513.csv`
- Existing CSV/JSON results, especially:
  - `results/experiment3_sparse_latent_vs_meshspace_20260511/*`
  - `results/projection_masked_ablation_matrices_20260511/metrics.csv`
  - `results/baseline_one_to_one_surface_metrics_20260510/surface_metrics_occ64.csv`
  - `results/surface_voxel_connectivity_20260509/surface_voxel_connectivity_summary.csv`

## Audit Findings

`assets/mesh_metric_enrichment_20260513.py` already covers the main CPU mesh diagnostics: watertight flag, boundary and nonmanifold edge counts, raw face-edge components, tolerance-welded components, bbox extents, triangle quality/aspect, surface area, volume for watertight meshes, and an OBJ face-count guard. The safest extension is therefore not another mesh loader pass, but a derived-metric layer over the existing CSVs.

The current enrichment output remains conservative:

- Experiment 3 priority assets: 65 requested, 52 measured, 13 skipped by guard, 0 watertight.
- Masked-naturalization manifest subset: 18 measured, all watertight in that subset, but only 3 rows per variant and not a replacement for handle-state evidence.
- Raw/welded mesh components and surface-voxel LCR often disagree; they should stay in separate evidence tiers.

## New Files

- `results/metric_enrichment_20260513/metric_extension_linnaeus_20260513.py`
  - Derived aggregation script.
  - Reads existing CSVs only.
  - Does not load meshes or scan large OBJ files.

- `results/metric_enrichment_20260513/test_metric_extension_linnaeus.py`
  - Smoke/unit tests for radius sensitivity, budget/readiness derivation, projection pass logic, and CLI table writes.

- `results/metric_enrichment_20260513/linnaeus_mesh_budget_readiness_20260513.csv`
- `results/metric_enrichment_20260513/linnaeus_mesh_budget_readiness_20260513.json`
  - Per-row derived budget/readiness classes from existing mesh enrichment.
  - Adds face/vertex budget pass flags, fragmentation class, and topology readiness class.

- `results/metric_enrichment_20260513/linnaeus_method_budget_summary_20260513.csv`
- `results/metric_enrichment_20260513/linnaeus_method_budget_summary_20260513.json`
  - Method-level medians for triangles, raw/welded components, boundary/nonmanifold edges, watertight rows, and budget pass counts.

- `results/metric_enrichment_20260513/linnaeus_case_budget_summary_20260513.csv`
- `results/metric_enrichment_20260513/linnaeus_case_budget_summary_20260513.json`
  - Case-level version of the same derived summary.

- `results/metric_enrichment_20260513/linnaeus_surface_radius_sensitivity_20260513.csv`
- `results/metric_enrichment_20260513/linnaeus_surface_radius_sensitivity_20260513.json`
  - Surface-voxel radius sensitivity from existing r0/r1/r2 CSVs.
  - Labels rows as `stable-r0`, `alias-sensitive-connected-after-r1`, `alias-sensitive-connected-after-r2`, or `fragmented-across-tested-radii`.

- `results/metric_enrichment_20260513/linnaeus_projection_admissible_state_summary_20260513.csv`
- `results/metric_enrichment_20260513/linnaeus_projection_admissible_state_summary_20260513.json`
  - Projection/admissible-state proxy summary over existing projection ablation metrics.
  - Uses root reachability proxy, orphan active handle proxy, handle survival proxy, and committed pass.

## Stable Paper-Usable Metrics

Use these as diagnostics/proxies, not as topology proof.

1. Mesh budget/readiness classes
   - Source: `linnaeus_mesh_budget_readiness_20260513.csv`
   - Safe wording: "CPU mesh-readiness diagnostics with a face-count guard."
   - Useful fields: `face_budget_pass`, `vertex_budget_pass`, `mesh_fragmentation_class`, `topology_readiness_class`.

2. Method-level fragmentation summary
   - Source: `linnaeus_method_budget_summary_20260513.csv`
   - Safe numbers:
     - `ps_rslg`: 10 ok rows, median welded components 131.5, 0 watertight rows, 1 welded-single row.
     - `trellis2_generatedroot_meshcopy`: 14 ok rows, median welded components 61257.5, 0 watertight rows.
     - `hunyuan_root_meshcopy`: 4 ok rows, median welded components 152126.5, 0 watertight rows.
   - Safe interpretation: generated-root mesh-copy baselines are highly fragmented under raw/welded mesh diagnostics; PS-RSLE rows are less fragmented in this selected enrichment but still not watertight.

3. Surface voxel radius sensitivity
   - Source: `linnaeus_surface_radius_sensitivity_20260513.csv`
   - 32 derived rows.
   - Useful for separating stable r0 connectivity from alias-sensitive r1/r2 connectivity.
   - Safe wording: "surface-sampled voxel connectivity is radius-sensitive and should be reported with the radius."

4. Projection/admissible-state proxy summary
   - Source: `linnaeus_projection_admissible_state_summary_20260513.csv`
   - Safe numbers:
     - `full_ps_rslg`: 12/12 admissible-state proxy pass rows, median root reachability 1.0, median orphan active handles 0.0, median handle survival 1.0.
     - `final_only_projection`: 0/12 pass rows, median root reachability 0.629, median orphan active handles 2.5.
     - Projected naturalization variants with projection show 12/12 proxy pass rows; no-projection variants show 0/12.
   - Safe interpretation: this supports the projection-inside-the-loop story as a controlled trace proxy, not arbitrary GLB handle recovery.

## Metrics Still Needing Remote GPU or Large-File Runs

- Full raw/welded mesh diagnostics for the 13 skipped Experiment 3 priority rows. They were skipped by face-count guard and should stay skipped locally unless run on a more suitable machine.
- Surface voxel r0/r1/r2 sensitivity for all priority mesh enrichment rows. The new script summarizes existing surface CSVs only; it does not resample every mesh.
- Full per-depth decoded-mesh re-encoding evidence. Current summaries remain sparse-latent trace plus decoded mesh/occupancy diagnostics.
- General handle recovery from arbitrary Trellis2 GLB exports. Existing handle survival/root reachability values are controlled trace proxies.
- Token-budget/runtime metrics from actual GPU execution traces. Local CSVs contain face/vertex/bbox budgets but not full GPU memory or token scheduling telemetry.

## Verification

- Red test confirmed first: `python3 -m pytest results/metric_enrichment_20260513/test_metric_extension_linnaeus.py -q` failed because the extension script was absent.
- After implementation: `python3 -m pytest results/metric_enrichment_20260513/test_metric_extension_linnaeus.py -q` passed with 3 tests.
- Generation command: `python3 results/metric_enrichment_20260513/metric_extension_linnaeus_20260513.py`
  - Wrote 120 mesh budget/readiness rows.
  - Wrote 8 method summary rows.
  - Wrote 9 case summary rows.
  - Wrote 32 surface radius-sensitivity rows.
  - Wrote 15 projection admissible-state summary rows.
