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
export TRITON_CACHE_DIR="$ROOT/cache/triton/root_quality_gpu6_20260508_0505"

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"
OUT="$ROOT/results/siga_root_quality_sweep/root_quality_gpu6_20260508_0505"

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_dinov3_official_min_smoke.py" \
  --image "$ROOT/inputs/trellis_example_images_subset/04_130c2b18f1651a70f8aa15b2c99f8dba29bb943044d92871f9223bd3e989e8b1.webp" \
  --dinov3-model "$DINO" \
  --out "$OUT/example04_vine_curl_steps12_seed910" \
  --steps 12 \
  --seed 910 \
  --preprocess

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_dinov3_official_min_smoke.py" \
  --image "$ROOT/inputs/trellis_example_images_subset/33_7d6f4da4eafcc60243daf6ed210853df394a8bad7e701cadf551e21abcc77869.webp" \
  --dinov3-model "$DINO" \
  --out "$OUT/example33_lattice_vine_steps12_seed911" \
  --steps 12 \
  --seed 911 \
  --preprocess
