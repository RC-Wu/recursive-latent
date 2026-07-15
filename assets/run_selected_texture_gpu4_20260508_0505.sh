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
export TRITON_CACHE_DIR="$ROOT/cache/triton/selected_texture_gpu4_20260508_0505"

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"
IMAGE="$ROOT/inputs/procedural_baselines/dla_cluster_points.png"
OUT="$ROOT/results/siga_selected_texture/selected_texture_gpu4_20260508_0505"

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_texturing_latent_smoke.py" \
  --mesh "$ROOT/results/siga_dla_cluster_masked_blend/dla_cluster_gpu7_20260508_0420/fork_side/steps_2/alpha_0p25/depth_03/masked/mesh.obj" \
  --image "$IMAGE" \
  --dinov3-model "$DINO" \
  --out "$OUT/dla_fork_side_s2_a0p25_d3_texture" \
  --steps 2 \
  --seed 881

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_texturing_latent_smoke.py" \
  --mesh "$ROOT/results/siga_dla_cluster_masked_blend/dla_cluster_gpu7_20260508_0420/radial/steps_1/alpha_0p25/depth_03/masked/mesh.obj" \
  --image "$IMAGE" \
  --dinov3-model "$DINO" \
  --out "$OUT/dla_radial_s1_a0p25_d3_texture" \
  --steps 2 \
  --seed 882
