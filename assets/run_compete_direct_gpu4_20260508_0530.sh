#!/usr/bin/env bash
set -euo pipefail

ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env

mkdir -p "$ROOT/logs" "$ROOT/cache/tmp" "$ROOT/cache/matplotlib" "$ROOT/cache/torch_extensions"
export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/tmp"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export CUDA_VISIBLE_DEVICES=4
export TRITON_CACHE_DIR="$ROOT/cache/triton/compete_direct_gpu4_20260508_0530"

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_recursive_slat_grammar_workflow.py" \
  --mesh "$ROOT/results/siga_root_quality_sweep/root_quality_gpu7_20260508_0505/example09_tree_steps12_seed912/trellis2_dinov3_min.obj" \
  --out "$ROOT/results/siga_compete_grammar/compete_direct_tree_gpu4_20260508_0530" \
  --case-name "compete_direct_tree_root" \
  --grammars compete compete_fork fork_side portal \
  --depths 4 \
  --resolution 512 \
  --grid-resolution 512 \
  --fit-scale 0.62 \
  --max-tokens 18000
