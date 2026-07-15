#!/usr/bin/env bash
set -euo pipefail

ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
mkdir -p "$ROOT/logs" "$ROOT/cache/tmp" "$ROOT/cache/matplotlib" "$ROOT/cache/torch_extensions"
export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home" TRANSFORMERS_CACHE="$ROOT/hf_home/transformers" TORCH_HOME="$ROOT/cache/torch" XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/tmp" MPLCONFIGDIR="$ROOT/cache/matplotlib" TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers CUDA_VISIBLE_DEVICES=4 TRITON_CACHE_DIR="$ROOT/cache/triton/vine_root_direct_gpu4_20260508_0615"

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_recursive_slat_grammar_workflow.py" \
  --mesh "$ROOT/results/siga_root_quality_sweep/root_quality_gpu6_20260508_0505/example04_vine_curl_steps12_seed910/trellis2_dinov3_min.obj" \
  --out "$ROOT/results/siga_vine_root_recursion/vine_direct_gpu4_20260508_0615" \
  --case-name "vine_root_direct" \
  --grammars compete compete_fork fork_side portal radial4 scale_down \
  --depths 3 \
  --resolution 512 \
  --grid-resolution 512 \
  --fit-scale 0.62 \
  --max-tokens 18000
