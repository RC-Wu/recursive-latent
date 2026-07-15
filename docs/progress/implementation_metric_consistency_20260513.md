# Implementation/Metric Consistency Audit - 2026-05-13

Scope: audit whether the currently proposed metrics map to actual generated files/scripts and to the PS-RSLE implementation described in Method Sec. 4.4/4.5. This note does not edit paper files.

Remote A100-2 path check: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507` is not mounted/reachable from this local machine. All evidence below is from the local project tree under `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`.

## Exact Files Checked

Paper/method:

- `paper_siga/main.tex`, especially lines 300-347, 377-415, and 429-477. These describe controlled sparse-latent resampling, feature-level masked merge, optional KV/cache reuse when hooks expose keys/values, decoded-domain projection, root-trace proxy transfer, handle deactivation, and re-encoding.

Metric and evaluation scripts:

- `assets/mesh_metric_enrichment_20260513.py`
- `assets/surface_voxel_connectivity_20260509.py`
- `assets/batch_surface_voxel_metrics_20260509.py`
- `assets/branch_path_metrics_20260509.py`
- `assets/recursive_growth_mesh_metrics.py`
- `assets/projection_masked_ablation_matrices_20260511.py`
- `assets/cache_sampler_connectivity_20260509.py`
- `assets/strict_visual_matched_cases_V63_lsystem_branch_distributed_recursive_bough_20260512.py`

Generated metric/output files:

- `results/metric_enrichment_20260513/priority_mesh_metric_enrichment_20260513.csv`
- `results/metric_enrichment_20260513/priority_mesh_metric_enrichment_20260513.json`
- `results/metric_enrichment_20260513/metric_enrichment_block_summary_20260513.csv`
- `results/metric_enrichment_20260513/smoke_manifest_metric_enrichment_20260513.csv`
- `results/surface_voxel_connectivity_20260509/surface_voxel_connectivity_summary.csv`
- `results/surface_voxel_connectivity_20260509/surface_voxel_connectivity_summary.json`
- `results/branch_path_metrics_20260509/branch_path_metrics.csv`
- `results/branch_path_metrics_20260509/branch_path_metrics_compact.csv`
- `results/projection_masked_ablation_matrices_20260511/metrics.csv`
- `results/projection_masked_ablation_matrices_20260511/summary.json`
- `results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_ps_rslg_metrics.csv`
- `results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_trellis2_baseline_metrics.csv`
- `results/real_case_ablation_inputs_20260512/manifest.csv`
- `results/strict_visual_matched_cases_V24_priority_rerun_20260510_dryrun/manifest.csv`
- `results/strict_visual_matched_cases_V63_lsystem_branch_distributed_recursive_bough_20260512_dryrun/manifest.csv`

## Supported Claims

The following metric claims are supported by actual local scripts and generated files, provided they are framed as diagnostics/proxies rather than proofs of topology or full runtime semantics.

1. Surface-voxel LCR and component counts are implemented and have generated outputs.
   - `assets/surface_voxel_connectivity_20260509.py` samples mesh surfaces, voxelizes points, optionally dilates occupied voxels, and reports 6-neighborhood components and LCR fields such as `surface_occ64_r0_lcr_6n`, `surface_occ64_r1_lcr_6n`, and component counts.
   - `assets/batch_surface_voxel_metrics_20260509.py` provides batch GLB folder evaluation with `components_r0/r1/r2` and `lcr_r0/r1/r2`.
   - Output exists in `results/surface_voxel_connectivity_20260509/surface_voxel_connectivity_summary.csv` with 24 rows and surface LCR/component columns.
   - Safe wording: "surface-sampled voxel connectivity diagnostic" or "seam/alias-tolerant renderability proxy." Do not call it watertightness, physical topology, or exact sparse-latent connectivity.

2. Raw/welded mesh component metrics are implemented and generated for priority assets.
   - `assets/mesh_metric_enrichment_20260513.py` loads OBJ/PLY/GLB/GLTF where possible, filters invalid/degenerate faces, computes raw face-edge components, quantized-welded components, largest-component face ratios, and small-component counts.
   - Output exists in `results/metric_enrichment_20260513/priority_mesh_metric_enrichment_20260513.csv` with 120 rows and fields including `raw_component_count`, `largest_raw_component_face_ratio`, `welded_component_count`, and `largest_welded_component_face_ratio`.
   - `assets/recursive_growth_mesh_metrics.py` independently supports face, welded, and occupancy component metrics for experiment outputs.
   - Safe wording: "raw face-edge component count" and "tolerance-welded face component count." Avoid implying these are identical to sparse-token components.

3. Watertight, boundary-edge, nonmanifold-edge, and triangle-quality diagnostics are implemented in the 20260513 enrichment script.
   - `assets/mesh_metric_enrichment_20260513.py` computes `boundary_edge_count`, `nonmanifold_edge_count`, `is_watertight`, `triangle_aspect_mean/p95/max`, `triangle_quality_mean/min`, degenerate faces, surface area, and volume only when watertight.
   - Output exists in `results/metric_enrichment_20260513/priority_mesh_metric_enrichment_20260513.csv`.
   - The block summary reports, for example, 0 watertight meshes in the inspected blocks and large median boundary-edge counts, so the metrics currently support "diagnostic failure/readiness evidence" more than a strong quality win.
   - Safe wording: "mesh-quality diagnostics reveal open boundaries and triangle-shape artifacts." Do not say the method produces watertight assets unless a specific table row actually has `is_watertight=True`.

4. Root reachability is implemented as a proxy and has generated outputs.
   - `assets/branch_path_metrics_20260509.py` computes `root_component_ratio`, `root_reachable_units`, `orphan_mass_ratio`, `root_reachable_tip_ratio`, and related path proxies from saved skeletons or mesh voxel occupancy.
   - Output exists in `results/branch_path_metrics_20260509/branch_path_metrics_compact.csv` with 19 rows.
   - The script explicitly labels mesh rows as `mesh_voxel_proxy` and warns that mesh tip/path counts are not reliable skeleton metrics.
   - Safe wording: "root-reachability proxy from voxelized mesh or saved skeleton." Use skeleton rows as stronger evidence than mesh proxy rows.

5. Handle survival and orphan-active metrics are implemented for deterministic projection/naturalization ablations.
   - `assets/projection_masked_ablation_matrices_20260511.py` computes `handle_survival_proxy`, `root_reachability_proxy`, and `orphan_active_handles_proxy` from deterministic primitive traces before/after per-depth projection.
   - Generated output exists in `results/projection_masked_ablation_matrices_20260511/metrics.csv` with 180 rows and columns `recursive_handle_survival_proxy`, `recursive_root_reachability_proxy`, and `recursive_orphan_active_handles_proxy`.
   - Metadata explicitly states the limitation: "deterministic primitive trace and mesh proxy; not a Trellis sparse-latent runtime graph."
   - Safe wording: "trace-level proxy in controlled ablations" or "executor-state proxy for deterministic ablation assets." Do not present it as recovered handle survival from arbitrary decoded GLBs.

6. Method Sec. 4.4/4.5 is mostly consistent with implementation boundaries if kept conservative.
   - Sec. 4.4 says current implementation preserves old tokens and blends newly inserted/transformed tokens with flowed/candidate features; this matches the conservative feature-level masked-blend implementation boundary.
   - Sec. 4.4 says KV/cache reuse is optional and only when sampler hooks expose transformer keys/values; experiments without hooks use feature-level masked blend. This is consistent with local evidence.
   - Sec. 4.5 says projection uses decoded-domain sampling/voxelization, root-trace proxy transfer through the object frame, contact/reachability tests, and conservative deactivation. This matches available proxy metric scripts.

## Unsupported or Too-Strong Claims

1. "Watertight assets" or "topologically clean meshes" is too strong.
   - The 20260513 metric output includes watertightness checks, but the inspected summary reports 0 watertight meshes in the metric-enrichment blocks. Boundary-edge counts are often large.
   - Recommended replacement: "mesh diagnostics report boundary/nonmanifold edges and triangle quality; these are used as readiness/failure diagnostics."

2. "Surface voxel LCR proves connectivity/topology" is too strong.
   - Surface-voxel metrics are sampled/dilated 6-neighborhood proxies and are explicitly not watertight topology proofs.
   - Recommended replacement: "surface-sampled voxel LCR provides a seam-tolerant connectivity/renderability proxy."

3. "Handle survival/root reach/orphan active are measured for all Trellis decoded assets" is unsupported.
   - These fields exist for deterministic primitive-trace ablations and some branch/path proxy scripts. They are not generally reconstructed from arbitrary Trellis textured GLBs.
   - Recommended replacement: "handle-level validity is evaluated in controlled projection trace ablations; mesh/GLB tables use component and occupancy proxies."

4. "KV cache implementation improves reported results" is unsupported as a main result.
   - `paper_siga/main.tex` correctly says KV reuse is optional/conditional. Local scripts contain cache/connectivity prototypes and cache-policy metadata, but not a robust true decoded-asset KV-cache result.
   - `assets/cache_sampler_connectivity_20260509.py` is an occupancy/cache-fusion smoke/proxy script, not evidence that transformer KV reuse is deployed in main experiments.
   - Recommended replacement: "when hooks are available, cache reuse can be used as an optional consistency aid; reported experiments rely on feature-level masked blending unless stated otherwise."

5. "Root/handle proxy transfer is exact" is too strong.
   - Method currently says root seeds are instantiated from a persistent root descriptor and that the current implementation uses a root-trace proxy transferred through object frame/contact tests. This is appropriately conservative.
   - Recommended replacement: keep "proxy transferred through object frame" and avoid "exact semantic root recovery from mesh."

6. "PS-RSLE is the only evaluated row with full sparse-latent state transition machinery" needs careful qualification.
   - Experiment 3 mesh-space and Trellis baseline metrics are generated, but handle-level validity is not measured in those rows. The paper can say those baselines lack the state/handle/projection contract by design, but quantitative handle survival should come from the projection ablation table, not Experiment 3 alone.

7. "Metric enrichment closes the full implementation evidence gap" is too strong.
   - `assets/mesh_metric_enrichment_20260513.py` closes mesh diagnostics for loaded assets, but it does not compute surface-voxel LCR, handle survival, root reachability, or orphan-active metrics. Those come from separate scripts with different evidence tiers.

## Metric-to-Claim Mapping

Use this mapping when deciding which table/paragraph can carry each claim.

| Metric | Script/output | Evidence tier | Safe use |
|---|---|---:|---|
| Surface voxel LCR/components | `assets/surface_voxel_connectivity_20260509.py`; `results/surface_voxel_connectivity_20260509/*`; batch script | Medium proxy | Connectivity/renderability diagnostic for GLB/mesh surfaces |
| Raw mesh components | `assets/mesh_metric_enrichment_20260513.py`; `priority_mesh_metric_enrichment_20260513.csv`; `recursive_growth_mesh_metrics.py` | Medium diagnostic | Fragmentation/open-surface diagnostic |
| Welded mesh components | Same as above | Medium diagnostic | Tolerance-sensitive connectivity after vertex quantization |
| Watertight | `mesh_metric_enrichment_20260513.py` | Diagnostic/failure evidence | Report whether closed; do not imply success unless row says true |
| Boundary/nonmanifold edges | `mesh_metric_enrichment_20260513.py` | Strong mesh diagnostic | Mesh readiness and artifact reporting |
| Triangle quality/aspect | `mesh_metric_enrichment_20260513.py`; projection ablation metrics | Strong mesh diagnostic | Mesh quality/readiness, not recursive-state validity |
| Root reachability | `branch_path_metrics_20260509.py`; projection ablation trace metrics | Proxy, stronger for saved skeletons | Root-attached support proxy |
| Handle survival | `projection_masked_ablation_matrices_20260511.py` | Controlled trace proxy | Projection-ablation state-validity evidence only |
| Orphan active handles | `projection_masked_ablation_matrices_20260511.py` | Controlled trace proxy | Projection-ablation evidence for deactivation behavior |
| KV/cache | `cache_sampler_connectivity_20260509.py`; method text; cache metadata | Prototype/optional | Optional implementation path or diagnostic, not main result |

## Recommended Main-Text Wording Constraints

- Use "diagnostic", "proxy", "surface-sampled", "voxelized", "tolerance-welded", and "controlled trace ablation" whenever discussing these metrics.
- Keep Sec. 4.4 wording conditional for KV cache: "may reuse cached transformer context when hooks expose keys/values"; "experiments without such hooks use feature-level masked blend."
- Keep Sec. 4.5 wording conservative: "root-trace proxy transferred through the object frame and evaluated by contact/reachability tests."
- For main quantitative claims, separate three evidence channels:
  - recursive-state validity: controlled projection/naturalization trace ablations (`projection_masked_ablation_matrices_20260511`);
  - surface/mesh connectivity: surface-voxel and raw/welded component metrics;
  - mesh/readiness quality: boundary/nonmanifold/watertight/triangle diagnostics.
- Avoid saying "watertight", "topology proof", "exact skeleton", "exact handle recovery", "implemented KV-cache result", or "full runtime sparse-latent graph metric" unless a specific script and output row directly supports it.
- For Experiment 3 and mesh-space baselines, say component/occupancy diagnostics are selected proxy evidence, while handle-level validity is tested in projection/trace ablations.
- Treat cache/LOD/KV material as an optional extension or implementation hook, not as a result-bearing contribution, unless future reachable remote artifacts provide true decoded-asset evidence.

## Bottom Line

The proposed metric set is usable if split by evidence tier. Mesh enrichment now supports raw/welded components, watertight/boundary/nonmanifold diagnostics, and triangle quality. Surface voxel LCR/components are supported by separate 20260509 scripts and outputs. Root reachability is a proxy, and handle survival/orphan-active are controlled trace-ablation proxies, not general GLB-derived metrics. KV/cache should remain optional/conditional wording only.
