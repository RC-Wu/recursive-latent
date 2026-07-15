# Cache/Sampler Connectivity Remote Status - 2026-05-09

## Scope

- Ownership line: remote cache / sampler / LOD connectivity experiment.
- Local runner: `assets/cache_sampler_connectivity_20260509.py`.
- Local deploy wrapper: `assets/cache_sampler_connectivity_20260509_deploy.sh`.
- `paper_siga/main.tex` was not edited.

## Corrected Remote Retry

- Host: `a100-2`.
- Retry time: `2026-05-09T03:01:53+08:00` to `2026-05-09T03:01:57+08:00`.
- Remote root: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`.
- Storage check printed by the single SSH session: `64G`, below the 100GB cap.
- Remote result path: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/cache_sampler_connectivity_20260509/run_20260509_030153_1659038`.
- Remote log path: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/cache_sampler_connectivity_20260509/run_20260509_030153_1659038`.
- Local record of small printed artifacts: `docs/remote_results/cache_sampler_connectivity_20260509_run_20260509_030153_1659038/`.
- Local copied artifacts from printed wrapper output:
  - `aggregate_summary.json`
  - `aggregate_metrics.csv` (empty because no rows were produced)
  - `aggregate_projection_aware_texture_selection.csv` (empty because no selections were produced)
  - `REMOTE_SUMMARY.md`

The corrected retry command was run exactly once:

```bash
tar -C /Users/fanta/code/agent/Code/recursive_3d_generative_growth -cf - assets/cache_sampler_connectivity_20260509.py assets/cache_sampler_connectivity_20260509_deploy.sh | ssh a100-2 'ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507 PYTHON_BIN=python3 bash -lc '\''cd "$ROOT" && tar -xf - && bash assets/cache_sampler_connectivity_20260509_deploy.sh'\'''
```

The remote wrapper launched the intended jobs:

```text
launch filter=hard gpu=6 out=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/hard log=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/hard_gpu6.log
launch filter=control gpu=7 out=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/control log=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/control_gpu7.log
```

The retry failed. Exact failure surfaced by the wrapper:

```text
hard_status=1
control_status=1
```

The deploy wrapper did not print the per-job Python traceback before the single SSH session closed. The exact inner exception should be in the remote job logs listed above:

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/hard_gpu6.log`
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/control_gpu7.log`

I did not open a second SSH/scp/rsync session to fetch those logs, to respect the one-session constraint.

Aggregate metrics printed by the wrapper:

```json
{
  "hard_cases_selected": 0,
  "mean_best_lcr_gain_vs_naive": 0.0,
  "mean_best_component_drop_vs_naive": 0.0,
  "cases_with_component_drop": 0,
  "cases_with_lcr_gain": 0,
  "viable_as_standalone_paper_contribution": false,
  "viable_as_supporting_ablation": false,
  "interpretation": "supporting ablation if confirmed with true TRELLIS decode; not standalone without decoder/texture pass"
}
```

Remote aggregate paths:

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/aggregate_summary.json`
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/aggregate_metrics.csv`
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/aggregate_projection_aware_texture_selection.csv`
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/REMOTE_SUMMARY.md`

## Previous Remote Attempt

- Host: `a100-2`.
- Remote root: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`.
- Storage check printed by the single SSH session: `63G`, below the 100GB cap.
- Required remote result parent: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/cache_sampler_connectivity_20260509`.
- Required remote log parent: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/cache_sampler_connectivity_20260509`.
- Unique run directory created: `run_20260509_025433_1652583`.
- Partial remote results path: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/cache_sampler_connectivity_20260509/run_20260509_025433_1652583`.
- Partial remote logs path: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/cache_sampler_connectivity_20260509/run_20260509_025433_1652583`.

The single allowed SSH session failed before aggregate metric generation because the remote shell did not expose `python`:

```text
assets/cache_sampler_connectivity_20260509_deploy.sh: line 64: python: command not found
```

The local deploy wrapper was then fixed to use `python3` by default through `PYTHON_BIN="${PYTHON_BIN:-python3}"`.

## GPU And Cache Policy

- Corrected retry GPU query showed GPUs `6` and `7` free at launch time.
- Corrected retry jobs:
  - hard cases: `CUDA_VISIBLE_DEVICES=6`.
  - stable control: `CUDA_VISIBLE_DEVICES=7`.
- GPUs `0`, `1`, `2`, and `3` were not launched on.
- Corrected retry remote cache env was set under the project root:
  - `TMPDIR=$ROOT/.cache/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/tmp`
  - `HF_HOME=$ROOT/.cache/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/hf`
  - `XDG_CACHE_HOME=$ROOT/.cache/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/xdg`
  - `TORCH_HOME=$ROOT/.cache/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/torch`
  - `TRITON_CACHE_DIR=$ROOT/.cache/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/triton`
  - `MPLCONFIGDIR=$ROOT/.cache/cache_sampler_connectivity_20260509/run_20260509_030153_1659038/matplotlib`
- No remote `/tmp` or `/dev/shm` path was used by the wrapper.

## Commands

Single SSH command used:

```bash
tar -C /Users/fanta/code/agent/Code/recursive_3d_generative_growth -cf - \
  assets/cache_sampler_connectivity_20260509.py \
  assets/cache_sampler_connectivity_20260509_deploy.sh \
| ssh a100-2 'ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507 bash -lc '\''cd "$ROOT" && tar -xf - && bash assets/cache_sampler_connectivity_20260509_deploy.sh'\'''
```

Corrected retry command, if another session is allowed:

```bash
tar -C /Users/fanta/code/agent/Code/recursive_3d_generative_growth -cf - \
  assets/cache_sampler_connectivity_20260509.py \
  assets/cache_sampler_connectivity_20260509_deploy.sh \
| ssh a100-2 'ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507 PYTHON_BIN=python3 bash -lc '\''cd "$ROOT" && tar -xf - && bash assets/cache_sampler_connectivity_20260509_deploy.sh'\'''
```

Local smoke command used before remote launch:

```bash
python3 assets/cache_sampler_connectivity_20260509.py \
  --root /Users/fanta/code/agent/Code/recursive_3d_generative_growth \
  --out /Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/cache_sampler_connectivity_20260509_local_smoke_all \
  --case-filter all \
  --grid 48
```

## Methods Tested By The Runner

- `naive_transformed_copies`: baseline transformed motif copies.
- `transform_cache_predecode_fusion`: cached motif fusion before decode with bridge insertion and closing.
- `lod_cache_fusion`: coarse LOD cache closing then high-resolution support gating.
- `sliding_window_cache_fusion`: local window cache repair over overlapping windows.
- `masked_local_sampler_boundary_schedule`: proxy masked local sampler/SDE schedule restricted to new-growth and boundary neighborhoods.
- Projection-aware sample selection: choose the candidate with best component count / largest-component-ratio / voxel-cost score before texture export.

## Local Smoke Metric Deltas

These are local preflight diagnostics, not completed remote metrics.

| Case | Source | Selected method | Components | LCR | Component delta vs naive | LCR delta vs naive |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `hard_dla` | `visuals/siga_night_20260508/selected_meshes/dla_fork_side_s2_a0p25_d3.obj` | `masked_local_sampler_boundary_schedule` | 3 | 0.999693 | -13 | +0.001560 |
| `hard_radial` | `visuals/siga_night_20260508/selected_meshes/transform_radial4_d3.obj` | `transform_cache_predecode_fusion` | 2 | 0.999984 | -4 | +0.000706 |
| `hard_scifi` | `visuals/non_tree_recursive_20260508/meshes/scifi_module_projected_translate_stage03.obj` | `naive_transformed_copies` | 1 | 1.000000 | 0 | +0.000000 |
| `hard_bismuth` | `visuals/public_guide_textured_glb_20260509b/porous_container_compete_stage03_bismuth_steps8_tex2048_xformers/textured.glb` | `transform_cache_predecode_fusion` | 1 | 1.000000 | -1 | +0.000020 |
| `control_vine` | `visuals/siga_night_20260508/siga_vine_projection_pruning_0700/minv_1000/vine_compete_d3/mesh_pruned.obj` | `masked_local_sampler_boundary_schedule` | 1 | 1.000000 | -3 | +0.018559 |

Local aggregate:

- Hard cases selected: 4.
- Mean best component drop vs naive: 4.5.
- Mean best LCR gain vs naive: 0.000572.
- Current viability judgment: not a standalone paper contribution yet. It is a plausible supporting ablation if repeated on remote at grid 64 and then confirmed with true TRELLIS decode / texture export.

## Paper Contribution Judgment

The proxy evidence supports the direction that cache fusion and masked boundary repair can reduce fragmented chunks, especially for DLA, radial, bismuth, and the stable vine control. The LCR gains are small because several existing meshes are already dominated by one large component after prior projection pruning. This should be framed as an engineering ablation for projection-aware selection and local naturalization, not as the main paper contribution until a successful remote run produces true TRELLIS decoded samples and texture-export pass/fail data.
