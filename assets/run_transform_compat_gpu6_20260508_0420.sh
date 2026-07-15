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
export CUDA_VISIBLE_DEVICES=6
export TRITON_CACHE_DIR="$ROOT/cache/triton/transform_compat_gpu6_20260508_0420"

OUT="$ROOT/results/siga_transform_compatibility/transform_tree_gpu6_20260508_0420"
MESH="$ROOT/results/trellis2_mesh_first_reconstruct/mesh_first_reconstruct_dla_tree_gpu0_projectcache_20260507_1758/trellis_example_tree_r512/shape_slat_reconstruct.obj"

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_recursive_slat_grammar_workflow.py" \
  --mesh "$MESH" \
  --out "$OUT" \
  --case-name "trellis_tree_transform_compatibility" \
  --grammars translate_x translate_y mirror rotate_z scale_down scale_up radial radial4 fork_side mirror_fork portal \
  --depths 3 \
  --resolution 512 \
  --grid-resolution 512 \
  --fit-scale 0.62 \
  --max-tokens 16000
