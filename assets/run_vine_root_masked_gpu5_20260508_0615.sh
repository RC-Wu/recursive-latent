#!/usr/bin/env bash
set -euo pipefail

ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
mkdir -p "$ROOT/logs" "$ROOT/cache/tmp" "$ROOT/cache/matplotlib" "$ROOT/cache/torch_extensions"
export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home" TRANSFORMERS_CACHE="$ROOT/hf_home/transformers" TORCH_HOME="$ROOT/cache/torch" XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/tmp" MPLCONFIGDIR="$ROOT/cache/matplotlib" TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers CUDA_VISIBLE_DEVICES=5 TRITON_CACHE_DIR="$ROOT/cache/triton/vine_root_masked_gpu5_20260508_0615"
DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_recursive_masked_repair_workflow.py" \
  --mesh "$ROOT/results/siga_root_quality_sweep/root_quality_gpu6_20260508_0505/example04_vine_curl_steps12_seed910/trellis2_dinov3_min.obj" \
  --image "$ROOT/inputs/trellis_example_images_subset/04_130c2b18f1651a70f8aa15b2c99f8dba29bb943044d92871f9223bd3e989e8b1.webp" \
  --dinov3-model "$DINO" \
  --out "$ROOT/results/siga_vine_root_recursion/vine_masked_gpu5_20260508_0615" \
  --case-name "vine_root_masked" \
  --grammars compete compete_fork fork_side radial echo \
  --depths 3 \
  --steps 1 2 \
  --blend-alphas 0.25 0.5 \
  --resolution 512 \
  --grid-resolution 512 \
  --fit-scale 0.62 \
  --seed 921
