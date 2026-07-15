#!/usr/bin/env bash
set -euo pipefail

ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env

mkdir -p "$ROOT/logs" "$ROOT/cache/tmp" "$ROOT/cache/matplotlib" "$ROOT/cache/torch_extensions"
export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home" TRANSFORMERS_CACHE="$ROOT/hf_home/transformers" TORCH_HOME="$ROOT/cache/torch" XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/tmp" MPLCONFIGDIR="$ROOT/cache/matplotlib" TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export TRITON_CACHE_DIR="$ROOT/cache/triton/recursive_blend_texture_gpu0_20260507_1854"
export ATTN_BACKEND=xformers CUDA_VISIBLE_DEVICES=0

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"
IMG="$ROOT/inputs/object_like_conditions/recursive_image_entry_gpu1_20260507_1842/lsystem/lsystem_warm_silhouette.png"
BASE="$ROOT/results/trellis2_recursive_masked_blend/recursive_masked_blend_gpu0_20260507_1824/lsystem_procedural_blend"
OUT="$ROOT/results/trellis2_recursive_blend_texture/recursive_blend_texture_gpu0_20260507_1854"

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_texturing_latent_smoke.py" \
  --mesh "$BASE/fork_side/steps_2/alpha_0p25/depth_03/masked/mesh.obj" \
  --image "$IMG" \
  --dinov3-model "$DINO" \
  --out "$OUT/lsystem_fork_side_alpha0p25_d3_texture" \
  --steps 2 \
  --seed 761

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_texturing_latent_smoke.py" \
  --mesh "$BASE/fork/steps_2/alpha_0p5/depth_03/masked/mesh.obj" \
  --image "$IMG" \
  --dinov3-model "$DINO" \
  --out "$OUT/lsystem_fork_alpha0p5_d3_texture" \
  --steps 2 \
  --seed 762
