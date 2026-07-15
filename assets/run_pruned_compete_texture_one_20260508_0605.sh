#!/usr/bin/env bash
set -euo pipefail

GPU="$1"
LABEL="$2"
MESH="$3"
IMAGE="$4"
SEED="$5"

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
export CUDA_VISIBLE_DEVICES="$GPU"
export TRITON_CACHE_DIR="$ROOT/cache/triton/pruned_compete_texture_gpu${GPU}_20260508_0605"

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"
OUT="$ROOT/results/siga_pruned_compete_texture/pruned_compete_texture_20260508_0605/$LABEL"

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_texturing_latent_smoke.py" \
  --mesh "$MESH" \
  --image "$IMAGE" \
  --dinov3-model "$DINO" \
  --out "$OUT" \
  --steps 2 \
  --seed "$SEED"
