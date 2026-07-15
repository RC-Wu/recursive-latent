#!/usr/bin/env bash
set -euo pipefail

ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env

mkdir -p "$ROOT/logs" "$ROOT/cache/tmp" "$ROOT/cache/matplotlib" "$ROOT/cache/torch_extensions"
export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home" TRANSFORMERS_CACHE="$ROOT/hf_home/transformers" TORCH_HOME="$ROOT/cache/torch" XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/tmp" MPLCONFIGDIR="$ROOT/cache/matplotlib" TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"
IMG="$ROOT/inputs/object_like_conditions/recursive_image_entry_gpu1_20260507_1842/lsystem/lsystem_warm_silhouette.png"
PRUNE="$ROOT/results/component_pruning/prune_20260507_1953"
OUT="$ROOT/results/trellis2_pruned_texture/pruned_texture_gpu45_20260508_0400"
mkdir -p "$OUT"

(
  export CUDA_VISIBLE_DEVICES=4
  export TRITON_CACHE_DIR="$ROOT/cache/triton/pruned_texture_gpu4_20260508_0400"
  "$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_texturing_latent_smoke.py" \
    --mesh "$PRUNE/lsystem_fork_side_a0p25/mesh_pruned.obj" \
    --image "$IMG" \
    --dinov3-model "$DINO" \
    --out "$OUT/lsystem_fork_side_a0p25_pruned_texture" \
    --steps 2 \
    --seed 861
) > "$ROOT/logs/pruned_texture_gpu4_20260508_0400.log" 2>&1 &
PID4=$!

(
  export CUDA_VISIBLE_DEVICES=5
  export TRITON_CACHE_DIR="$ROOT/cache/triton/pruned_texture_gpu5_20260508_0400"
  "$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_texturing_latent_smoke.py" \
    --mesh "$PRUNE/lsystem_fork_a0p5/mesh_pruned.obj" \
    --image "$IMG" \
    --dinov3-model "$DINO" \
    --out "$OUT/lsystem_fork_a0p5_pruned_texture" \
    --steps 2 \
    --seed 862
) > "$ROOT/logs/pruned_texture_gpu5_20260508_0400.log" 2>&1 &
PID5=$!

wait "$PID4"
wait "$PID5"
