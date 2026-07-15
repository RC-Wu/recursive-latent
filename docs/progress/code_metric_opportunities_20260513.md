# Code and Metric Opportunities - 2026-05-13

Scope: remote/code implementation evidence plus new metric opportunities for PS-RSLE revision Sections 4.4 and 4.5. This report is read-only except for this file.

## Bottom Line

Strongest safely supported implementation statement:

> The repository contains executable Trellis2 mesh-first Shape-SLat workflows that encode an input mesh into sparse latent tokens, apply recursive coordinate/feature grammar edits, decode each depth to OBJ/preview meshes, and also contains a masked flow/blend repair variant that samples Shape-SLat flow on candidate coordinates while preserving/blending prior tokens. Projection/admissibility is strongly implemented as mesh/occupancy connectivity repair and controlled trace/metric diagnostics, but I did not find code evidence for a full decoded-domain project -> re-encode step executed at every recursive depth in the main Trellis2 grammar loop.

Therefore, Sections 4.4/4.5 should keep the manuscript conservative:

- KV/cache: optional/conditional only.
- Decode/project/re-encode: describe as the conceptual contract or implementation boundary only if qualified; the verified local code path is encode -> sparse-latent grammar edit -> decode, plus separate masked flow/blend repair and mesh/occupancy projection diagnostics.
- Root reach, handle survival, orphan-active: available as proxy/controlled trace metrics, not general GLB-derived runtime handle recovery.

## Remote Reachability

Local evidence:

- `~/.ssh/config` has a configured `Host a100-2`.
- Safe read-only probe run on 2026-05-13:
  - `ssh -o BatchMode=yes -o ConnectTimeout=8 a100-2 'hostname; ls -ld /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507 ...'`
  - Result: host returned `a100-2`; exact project root exists as `drwxrwxr-x ... /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`; `ROOT_PRESENT`.

Repo evidence:

- `docs/evaluation/case_inventory_v1_v60_20260512/remote_a1002_v1_v60_files.txt` is a bounded prior listing of remote files under `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`.
- Many manifests point to `remote_target: a100-2` and `storage_root: /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`.

No remote jobs were launched.

## Implementation Evidence

### Supported by code

- Sparse-latent grammar recursion:
  - `assets/trellis2_recursive_slat_grammar_workflow.py`
  - Encodes mesh via `shape_slat_encoder`, applies grammar ops to `SparseTensor` coordinates/features, decodes each depth with `shape_slat_decoder`, and records token/vertex/face/decode timing summaries.

- Masked flow/blend repair:
  - `assets/trellis2_recursive_masked_repair_workflow.py`
  - Applies grammar ops to candidate coordinates, calls `pipe.sample_shape_slat(...)`, then `masked_repair(prev, candidate, flowed, alpha)` preserving old tokens and blending candidate/flowed features for new coordinates.

- Shape-SLat flow repair:
  - `assets/trellis2_recursive_slat_flow_repair.py`
  - Encodes mesh, applies coordinate rewrite grammar, samples Shape-SLat flow, decodes repaired states, and logs `input_tokens`, `repaired_tokens`, vertices/faces.

- Mesh/occupancy projection and repair diagnostics:
  - `assets/mesh_connectivity_repair_20260509.py`
  - Implements face components, largest-component extraction, bridge-to-largest, occupancy voxelization, 6-neighbor components, occupancy bridging/closing, voxel remeshing, and LCR/component metrics.

- Cache/sampler opportunity prototype:
  - `assets/cache_sampler_connectivity_20260509.py`
  - Implements occupancy-level cache/motif fusion, LOD/sliding-window fusion, masked local sampler, and component/LCR deltas. Its own summary language says true TRELLIS decode evidence is still needed before contribution claims.

### Not fully supported by code evidence found

- A main-loop decoded-domain `project -> re-encode` at every recursive depth.
  - The main Trellis2 grammar loop decodes each `st` and then applies the next sparse op to `st`; I did not find a per-depth mesh projection result being fed through `shape_slat_encoder` as the next recursive state.

- Transformer KV-cache reuse as a result-bearing implementation.
  - Cache-related scripts are occupancy/prototype diagnostics, not verified transformer key/value reuse in main results.

## Existing Metric Evidence

- Remote/pulled recursive metrics:
  - `results/botanical_tree_root_recursive_remote_20260511p_pull/metrics/botanical_tree_root_metrics_20260511p.csv` has 109 rows with `depth_hint`, `method_hint`, `component_count`, `occupancy_component_count_6n`, `largest_occupancy_component_ratio_6n`, `fragmentation_score`, vertices/faces, occupancy coverage, and paths.
  - `results/fern_two_case_recursive_remote_20260512i_pull/metrics/fern_two_case_metrics_20260512i.csv` has 60 rows with the same useful metric schema.

- Projection/handle proxy metrics:
  - `results/projection_masked_ablation_matrices_20260511/metrics.csv` has 180 rows with `recursive_handle_survival_proxy`, `recursive_root_reachability_proxy`, `recursive_orphan_active_handles_proxy`, occupancy components/LCR, raw face components, triangle quality proxies.

- Root-reach proxy metrics:
  - `results/branch_path_metrics_20260509/branch_path_metrics.csv` and compact version have 19 rows with `root_component_ratio`, `root_reachable_tip_ratio`, `orphan_mass_ratio`, path span, tip/branch proxies.

- Mesh diagnostic enrichment:
  - `results/metric_enrichment_20260513/priority_mesh_metric_enrichment_20260513.csv` has 120 rows with raw/welded components, boundary/nonmanifold edges, watertightness, triangle aspect/quality, surface area, and manifest metadata.

## Feasible New Metrics Without GPU

1. Depth stability and regression metrics from pulled trace CSVs.
   - Inputs: botanical and fern recursive metric CSVs.
   - Compute per `(case_hint, method_hint)`:
     - `component_growth_per_depth = slope(occupancy_component_count_6n vs depth_hint)`
     - `lcr_drop_per_depth = slope(largest_occupancy_component_ratio_6n vs depth_hint)`
     - `worst_depth_lcr`, `max_components`, `final_vs_initial_occupied_voxel_ratio`
   - Why useful: directly supports stability across recursion depth without rerunning Trellis2.

2. Projection survival/readiness summary across controlled ablations.
   - Input: `projection_masked_ablation_matrices_20260511/metrics.csv`.
   - Compute grouped means/quantiles by `task_family`, `projection_schedule`, `naturalization_policy`:
     - mean handle survival proxy
     - mean orphan-active proxy
     - pass rate under thresholds such as LCR >= 0.98 and orphan-active <= 0.02
   - Why useful: gives a clean table for projection schedule vs failure mode, while explicitly remaining controlled-trace proxy evidence.

3. Mesh readiness/failure index from existing mesh enrichment CSV.
   - Input: `priority_mesh_metric_enrichment_20260513.csv`.
   - Compute a normalized diagnostic index from:
     - boundary edge density
     - nonmanifold edge density
     - largest raw/welded component face ratio
     - triangle aspect p95
     - watertight flag as diagnostic only
   - Why useful: strengthens failure/readiness discussion and prevents overclaiming watertightness.

## Metrics Requiring Remote Reruns or New Instrumentation

- True per-depth decoded-domain projection followed by re-encode timing and token survival.
  - Need remote/GPU run that explicitly decodes, projects mesh/occupancy support, calls `shape_slat_encoder` on projected geometry, then continues recursion.

- True transformer KV-cache reuse impact.
  - Need sampler hooks exposing keys/values plus A/B runs with and without KV reuse; current cache scripts are occupancy/cache-fusion proxies.

- General handle survival/orphan-active from arbitrary textured GLBs.
  - Existing handle metrics are controlled trace proxies. General GLB recovery would need saved runtime handle traces or a new trace export format.

## Recommended Paper Wording

- For 4.4: "Our implementation preserves previous sparse tokens and realizes new candidate support through feature-level masked blending; when sampler hooks expose transformer keys/values, cached context can optionally be reused."
- For 4.5: "Projection is evaluated through decoded mesh/occupancy connectivity and root-reachability proxies; controlled ablations measure handle survival and orphan-active proxies."
- Avoid: "KV cache improves results", "exact handle recovery from decoded GLBs", "watertight topology", and "the current main loop always performs decode -> project -> re-encode" unless future remote code evidence is added.
