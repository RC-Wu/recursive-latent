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
export CUDA_VISIBLE_DEVICES=5
export TRITON_CACHE_DIR="$ROOT/cache/triton/selected_texture_gpu5_20260508_0505"

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"
IMAGE="$ROOT/inputs/trellis_example_images_subset/09_26717a7dad644a5cf7554e8e6d06cf82d3dd9bbae31620b36cc7eb38b8de7ac9.webp"
OUT="$ROOT/results/siga_selected_texture/selected_texture_gpu5_20260508_0505"

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_texturing_latent_smoke.py" \
  --mesh "$ROOT/results/siga_transform_compatibility/transform_tree_gpu6_20260508_0420/radial4/depth_03/mesh.obj" \
  --image "$IMAGE" \
  --dinov3-model "$DINO" \
  --out "$OUT/transform_radial4_d3_texture" \
  --steps 2 \
  --seed 883

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_texturing_latent_smoke.py" \
  --mesh "$ROOT/results/siga_transform_compatibility/transform_tree_gpu6_20260508_0420/portal/depth_03/mesh.obj" \
  --image "$IMAGE" \
  --dinov3-model "$DINO" \
  --out "$OUT/transform_portal_d3_texture" \
  --steps 2 \
  --seed 884
