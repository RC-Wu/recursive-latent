# Connectivity-First DLA/Crystal Remote Status - 2026-05-09

## Scope

Targeted anti-fragmentation experiments for unacceptable DLA/radial/bismuth/crystal/root fragmented outputs.

Local script:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/connectivity_first_dla_crystal_20260509.py`

Remote script:

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets/connectivity_first_dla_crystal_20260509.py`

Remote output root:

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/connectivity_first_dla_crystal_20260509`

Remote log root:

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/connectivity_first_dla_crystal_20260509`

## Resource Use

- Host: `a100-2`
- GPUs used: `4`, `5`
- GPUs explicitly not used: `0`, `1`, `2`, `3`
- Storage at launch: `63G` under `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`, below the current `100GB` cap.
- GPU memory at launch: GPU 4 `0 MiB / 81920 MiB`, GPU 5 `0 MiB / 81920 MiB`.
- Cache/temp policy: `TMPDIR`, `HF_HOME`, `XDG_CACHE_HOME`, `TORCH_HOME`, `TRITON_CACHE_DIR`, `MPLCONFIGDIR`, and `TORCH_EXTENSIONS_DIR` are all under the remote project root. No remote `/tmp` or `/dev/shm` is used.

Note: the first remote pass deployed the script and checked storage/GPU state, but aborted before launching due to a shell quoting bug in GPU-memory parsing. A corrective launch pass started the jobs below. No GPU job was started in the failed pass.

## Methods Tried

- `sparse_close_bridge`: sparse occupancy morphological closing plus bridge-to-main-component before decode, followed by mesh bridge projection.
- `mesh_bridge_smooth`: decode first, then mesh projection with attachment bridges and optional voxel-union smoothing.
- `sparse_bridge_select`: sparse bridge-to-main-component before decode, mesh bridge projection, then sample selection by occupancy LCR and component count.

Selection score:

```text
selection_score = occupancy_lcr - 0.002 * occupancy_component_count
```

Texture is only attempted for the top selected candidate per job (`--texture-top-k 1`) after candidate scoring.

## Launch Commands

Common environment used inside each `nohup` job:

```bash
source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/tmp"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

GPU 4, DLA plus porous/bismuth proxy priority:

```bash
CUDA_VISIBLE_DEVICES=4 \
TRITON_CACHE_DIR=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/triton/connectivity_first_dla_crystal_20260509/gpu4 \
/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/envs/trellis2_bakeoff/bin/python \
/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets/connectivity_first_dla_crystal_20260509.py \
  --root /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507 \
  --out /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/connectivity_first_dla_crystal_20260509/gpu4_dla_porous \
  --case dla_voxel_root=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/inputs/procedural_meshes/dla_cluster_voxels.obj \
  --case porous_bismuth_crystal_proxy=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/selected_meshes_for_texture_20260508/porous_container_compete_stage03.obj \
  --grammars compete_fork_attach fork_side_attach \
  --methods sparse_close_bridge mesh_bridge_smooth \
  --stages 3 \
  --max-tokens 14000 \
  --min-vertices 1800 \
  --mesh-bridge-components 10 \
  --texture-top-k 1 \
  --texture-steps 2
```

Launch status:

- PID: `1655730`
- Log: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/connectivity_first_dla_crystal_20260509/gpu4_dla_porous.log`
- Result dir: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/connectivity_first_dla_crystal_20260509/gpu4_dla_porous`

GPU 5, bismuth/crystal proxy plus vine/root stress control:

```bash
CUDA_VISIBLE_DEVICES=5 \
TRITON_CACHE_DIR=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/triton/connectivity_first_dla_crystal_20260509/gpu5 \
/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/envs/trellis2_bakeoff/bin/python \
/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets/connectivity_first_dla_crystal_20260509.py \
  --root /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507 \
  --out /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/connectivity_first_dla_crystal_20260509/gpu5_bismuth_root_control \
  --case porous_bismuth_crystal_proxy=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/selected_meshes_for_texture_20260508/porous_container_compete_stage03.obj \
  --case vine_root_control=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/siga_root_quality_sweep/root_quality_gpu6_20260508_0505/example04_vine_curl_steps12_seed910/trellis2_dinov3_min.obj \
  --grammars compete_fork_attach \
  --methods sparse_bridge_select sparse_close_bridge \
  --stages 3 \
  --max-tokens 14000 \
  --min-vertices 1800 \
  --mesh-bridge-components 10 \
  --texture-top-k 1 \
  --texture-steps 2
```

Launch status:

- PID: `1655731`
- Log: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/connectivity_first_dla_crystal_20260509/gpu5_bismuth_root_control.log`
- Result dir: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/connectivity_first_dla_crystal_20260509/gpu5_bismuth_root_control`

## Metric Deltas

Pending at launch. The jobs write per-stage deltas in:

- `*/summary_partial.json` while running
- `*/summary.json` after completion
- `*/selected_candidates.json` after ranking

For each candidate/stage, inspect:

- `raw_metrics`: decoded proposal before connectivity operators.
- `sparse_metrics`: decoded proposal after sparse closing/bridging.
- `mesh_projection.metrics`: final projected mesh after bridge/smoothing projection.

Primary fields:

- `occupancy_component_count`
- `occupancy_lcr`
- `face_component_count`
- `face_largest_component_ratio`
- `selection_score`

The intended delta is:

```text
raw_metrics.occupancy_component_count -> mesh_projection.metrics.occupancy_component_count
raw_metrics.occupancy_lcr -> mesh_projection.metrics.occupancy_lcr
sparse_report.sparse_before.component_count -> sparse_report.sparse_after.component_count
sparse_report.sparse_before.largest_component_ratio -> sparse_report.sparse_after.largest_component_ratio
```

## Visual Artifacts To Pull

Per stage:

- `*/stage_*/raw/proposal_before_connectivity.png`
- `*/stage_*/sparse_connectivity/proposal_after_sparse_connectivity.png`
- `*/stage_*/projected/mesh_projected.png`
- `*/stage_*/projected/mesh_projected.obj`

Final selection and texture:

- `gpu4_dla_porous/selected_candidates.json`
- `gpu5_bismuth_root_control/selected_candidates.json`
- `*/selected_texturing/summary.json` if the selected texture smoke reaches that stage.

Suggested pull command:

```bash
rsync -avP \
  a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/connectivity_first_dla_crystal_20260509/ \
  /Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/remote_results/connectivity_first_dla_crystal_20260509_results/
```

## Local Verification

```bash
python3 -m pytest -q tests/test_connectivity_first_dla_crystal.py
# 3 passed

python3 -m py_compile assets/connectivity_first_dla_crystal_20260509.py
# exit 0
```
