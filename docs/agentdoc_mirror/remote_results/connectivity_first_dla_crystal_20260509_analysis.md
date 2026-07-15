# Connectivity-First DLA/Crystal Analysis - 2026-05-09

## Scope

Remote runs inspected:

- `gpu4_dla_porous`
- `gpu5_bismuth_root_control`

Remote output root:

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/connectivity_first_dla_crystal_20260509`

Local pulled/lightweight result root:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/remote_results/connectivity_first_dla_crystal_20260509_results`

Storage at inspection was `64G` under `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`, below the 100GB cap. No second experiment round was started.

## Remote Summary

Both jobs reached wrapper status `completed`, but no candidate completed the intended raw -> sparse -> projected pipeline. In both `summary.json` files, `candidates` and `selected_candidates` are empty, and `selected_candidates.json` is `[]`.

Failure point:

```text
stage_summary["raw_metrics"] = mesh_component_metrics(raw_obj)
from recursive_growth_mesh_metrics import load_geometry, component_stats, occupancy_stats
ModuleNotFoundError: No module named 'recursive_growth_mesh_metrics'
```

This happened immediately after the stage-01 raw decode was written. Therefore, sparse connectivity previews, projected meshes, projected previews, per-candidate summaries, texture reports, and selected meshes were not produced.

## Available Artifacts

Available locally:

- `summary.json`, `selected_candidates.json`, and `run_config.json` for both runs.
- Stage-01 raw decoded `proposal_before_connectivity.obj` and `proposal_before_connectivity.png` for all attempted candidates.
- Recomputed local raw occupancy metrics: `raw_occupancy_metrics_20260509.json`.
- Raw preview contact sheet: `raw_preview_contact_sheet_20260509.jpg`.

Not available:

- `stage_*/sparse_connectivity/proposal_after_sparse_connectivity.obj`
- `stage_*/sparse_connectivity/proposal_after_sparse_connectivity.png`
- `stage_*/projected/mesh_projected.obj`
- `stage_*/projected/mesh_projected.png`
- any `latest_mesh.txt`
- any selected textured/exported candidate

No selected meshes/previews existed remotely, so there was nothing additional to pull beyond the already mirrored summaries and raw previews.

## Before/After Metrics

The table below uses local recomputation on the pulled raw OBJ files with 64-resolution vertex occupancy. Sparse and projected fields are marked `not produced` because the run failed before those stages.

| Run | Case | Grammar | Method | Raw vertices | Raw faces | Raw occ. comps | Raw occ. LCR | Sparse after | Projected after |
|---|---|---|---|---:|---:|---:|---:|---|---|
| gpu4 | dla_voxel_root | compete_fork_attach | mesh_bridge_smooth | 568218 | 1124106 | 77 | 0.9825 | not produced | not produced |
| gpu4 | dla_voxel_root | compete_fork_attach | sparse_close_bridge | 568183 | 1124062 | 77 | 0.9825 | not produced | not produced |
| gpu4 | dla_voxel_root | fork_side_attach | mesh_bridge_smooth | 634594 | 1236934 | 4 | 0.9955 | not produced | not produced |
| gpu4 | dla_voxel_root | fork_side_attach | sparse_close_bridge | 634560 | 1236852 | 4 | 0.9955 | not produced | not produced |
| gpu4 | porous_bismuth_crystal_proxy | compete_fork_attach | mesh_bridge_smooth | 991826 | 1996728 | 60 | 0.9856 | not produced | not produced |
| gpu4 | porous_bismuth_crystal_proxy | compete_fork_attach | sparse_close_bridge | 991852 | 1996614 | 60 | 0.9855 | not produced | not produced |
| gpu4 | porous_bismuth_crystal_proxy | fork_side_attach | mesh_bridge_smooth | 1028429 | 2043300 | 14 | 0.9986 | not produced | not produced |
| gpu4 | porous_bismuth_crystal_proxy | fork_side_attach | sparse_close_bridge | 1028405 | 2043154 | 14 | 0.9986 | not produced | not produced |
| gpu5 | porous_bismuth_crystal_proxy | compete_fork_attach | sparse_bridge_select | 991899 | 1996720 | 60 | 0.9855 | not produced | not produced |
| gpu5 | porous_bismuth_crystal_proxy | compete_fork_attach | sparse_close_bridge | 991824 | 1996720 | 60 | 0.9855 | not produced | not produced |
| gpu5 | vine_root_control | compete_fork_attach | sparse_bridge_select | 250095 | 451810 | 200 | 0.9012 | not produced | not produced |
| gpu5 | vine_root_control | compete_fork_attach | sparse_close_bridge | 250122 | 451776 | 200 | 0.9012 | not produced | not produced |

Interpretation:

- Raw DLA and porous/bismuth decodes have high largest-component occupancy ratios, but still retain multiple occupancy components.
- `fork_side_attach` raw proposals look numerically more connected than `compete_fork_attach` for DLA and porous/bismuth, but this is only a pre-connectivity raw observation.
- Vine/root raw proposals are the weakest numerically: about 200 occupancy components and only about 0.901 occupancy LCR.
- Because sparse and projected stages did not run, there is no valid before/after delta for any method.

## Method Winner

No method won.

The intended score was:

```text
selection_score = occupancy_lcr - 0.002 * occupancy_component_count
```

No candidate reached final projected metrics, so no `selection_score` was computed and both `selected_candidates.json` files are empty.

## Visual Read

The raw contact sheet suggests:

- DLA raw previews read as dense cloudy clusters with some visible small floaters. They may be salvageable as a connected porous asset only if bridge/projection successfully removes or attaches the floaters.
- Porous/bismuth raw previews read as a coherent jar/container-like mass, but the preview has speckled/floating boundary artifacts; it is not yet a clean usable connected asset.
- Vine/root raw previews are visually expressive and asset-like, but the recomputed raw metrics show severe fragmentation, so they should not be trusted without projected cleanup.

Current conclusion: the raw previews are useful diagnostics, not deliverable connected assets. There is no selected usable connected asset from this run.

## Exact Next Experiments

Do not launch a full second round from these results. The next work should first validate the harness on a small candidate because the current failure is an import/runtime packaging issue, not a method result.

1. Fix the remote import path or script dependency.
   - Ensure `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets/recursive_growth_mesh_metrics.py` exists.
   - Launch command must export `PYTHONPATH=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets/python_shims:$MESHVAE_TRELLIS:${PYTHONPATH:-}`.
   - Add a preflight import check before model load:

```bash
python - <<'PY'
import recursive_growth_mesh_metrics
print(recursive_growth_mesh_metrics.__file__)
PY
```

2. Run one small smoke candidate only, no texturing.
   - GPU: use only GPU 4 or GPU 5 after checking it is free.
   - Storage: proceed only if project-root usage remains below 80GB, leaving margin under the 100GB cap.
   - Output: use a new subdirectory such as `results/connectivity_first_dla_crystal_20260509_fix_import_smoke`.
   - Case: start with `dla_voxel_root`.
   - Grammar: `fork_side_attach`.
   - Method: `sparse_close_bridge`.
   - Stages: `1`.
   - Texture: `--texture-top-k 0`.
   - Keep `TMPDIR`, `HF_HOME`, `XDG_CACHE_HOME`, `TORCH_HOME`, `TRITON_CACHE_DIR`, `MPLCONFIGDIR`, and `TORCH_EXTENSIONS_DIR` under the project root; do not use `/tmp` or `/dev/shm`.

3. Acceptance check for the smoke run.
   - Required files: raw, sparse, and projected OBJ/PNG for stage 01.
   - Required metrics: raw occupancy component count/LCR, sparse before/after component count/LCR, projected occupancy component count/LCR.
   - Continue only if projected occupancy component count is lower than raw and projected LCR is at least as high as raw.

4. If the smoke run passes, run a narrow comparison.
   - Cases: `dla_voxel_root`, `porous_bismuth_crystal_proxy`, `vine_root_control`.
   - Grammars: `fork_side_attach` and `compete_fork_attach`.
   - Methods: `sparse_close_bridge`, `sparse_bridge_select`, `mesh_bridge_smooth`.
   - Stages: `1` first; do not return to `--stages 3` until stage-01 projection is confirmed.
   - Texture remains disabled until selected projected meshes exist.

5. Only after a valid stage-01 comparison should a small stage-3 run be considered.
   - Promote only the best one or two method/case pairs by projected occupancy LCR and component count.
   - Pull selected projected meshes/previews and then decide whether any candidate is worth texturing.
