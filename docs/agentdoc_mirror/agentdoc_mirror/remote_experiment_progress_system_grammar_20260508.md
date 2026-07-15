# Remote Experiment Progress - System Grammar 2026-05-08

## 2026-05-08 18:40 +08

- Remote host: `a100-2`.
- Remote project root: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`.
- Remote progress log: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/docs/agentdoc_mirror/remote_experiment_progress_system_grammar_20260508.md`.
- Initial size check: `54G`, below the `70G` cap.
- Initial GPU check: GPUs `4,5,6,7` were free before launch. GPUs `0,1,2` had unrelated meshvae/v47 jobs and were not touched.
- Launch root: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/experiments/system_grammar_remote_20260508_1839`.
- Shared output root: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/system_grammar_remote_20260508_1839`.
- Shared log dir: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/system_grammar_remote_20260508_1839`.

## Jobs Started

| Job | GPU | PID | Log | Output |
| --- | --- | ---: | --- | --- |
| `space_competition_gpu4` | 4 | 1299498 | `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/system_grammar_remote_20260508_1839/space_competition_gpu4.log` | `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/system_grammar_remote_20260508_1839/space_competition_curves` |
| `masked_lowstep_grid_gpu5` | 5 | 1299501 | `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/system_grammar_remote_20260508_1839/masked_lowstep_grid_gpu5.log` | `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/system_grammar_remote_20260508_1839/masked_lowstep_grid/tree_stable_root` |
| `cache_lod_diagnostic_gpu6` | 6 | 1299506 | `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/system_grammar_remote_20260508_1839/cache_lod_diagnostic_gpu6.log` | `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/system_grammar_remote_20260508_1839/cache_lod_probe` |
| `symmetry_escher_proxy_gpu7` | 7 | 1299512 | `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/system_grammar_remote_20260508_1839/symmetry_escher_proxy_gpu7.log` | `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/system_grammar_remote_20260508_1839/symmetry_escher_proxy` |

All launch scripts set `TMPDIR`, `XDG_CACHE_HOME`, `HF_HOME`, `TORCH_HOME`, `TRITON_CACHE_DIR`, and `MPLCONFIGDIR` under the project root.

## 2026-05-08 18:41 +08 Snapshot

- `cache_lod_diagnostic_gpu6` exited successfully and produced:
  - `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/system_grammar_remote_20260508_1839/cache_lod_probe/prototype_manifest/manifest.json`
  - `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/system_grammar_remote_20260508_1839/cache_lod_probe/island_city_lod256/summary.json`
- Still running at snapshot:
  - `space_competition_gpu4` PID `1299498`, with vine summary already present.
  - `masked_lowstep_grid_gpu5` PID `1299501`, with base direct mesh/preview already present.
  - `symmetry_escher_proxy_gpu7` PID `1299512`, with crown summary already present.
- New output root size: `954M`.
- Whole project size after launch: `54G`, still below the `70G` cap.
