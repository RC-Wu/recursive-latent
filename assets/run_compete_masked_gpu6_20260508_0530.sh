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
export TRITON_CACHE_DIR="$ROOT/cache/triton/compete_masked_gpu6_20260508_0530"

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_recursive_masked_repair_workflow.py" \
  --mesh "$ROOT/results/siga_root_quality_sweep/root_quality_gpu7_20260508_0505/example09_tree_steps12_seed912/trellis2_dinov3_min.obj" \
  --image "$ROOT/inputs/trellis_example_images_subset/09_26717a7dad644a5cf7554e8e6d06cf82d3dd9bbae31620b36cc7eb38b8de7ac9.webp" \
  --dinov3-model "$DINO" \
  --out "$ROOT/results/siga_compete_masked/compete_masked_tree_gpu6_20260508_0530" \
  --case-name "compete_masked_tree_root" \
  --grammars compete compete_fork fork_side \
  --depths 3 \
  --steps 1 2 \
  --blend-alphas 0.25 0.5 \
  --resolution 512 \
  --grid-resolution 512 \
  --fit-scale 0.62 \
  --seed 891
