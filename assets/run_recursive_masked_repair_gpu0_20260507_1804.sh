#!/usr/bin/env bash
set -euo pipefail

ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env

mkdir -p "$ROOT/logs" "$ROOT/cache/tmp" "$ROOT/cache/matplotlib" "$ROOT/cache/torch_extensions"
export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home" TRANSFORMERS_CACHE="$ROOT/hf_home/transformers" TORCH_HOME="$ROOT/cache/torch" XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/tmp" MPLCONFIGDIR="$ROOT/cache/matplotlib" TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export TRITON_CACHE_DIR="$ROOT/cache/triton/recursive_masked_repair_gpu0_20260507_1804"
export ATTN_BACKEND=xformers CUDA_VISIBLE_DEVICES=0

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"
BASE_OUT="$ROOT/results/trellis2_recursive_masked_repair/recursive_masked_repair_gpu0_20260507_1804"

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_recursive_masked_repair_workflow.py" \
  --mesh "$ROOT/inputs/procedural_meshes/ifs_branch_tree.obj" \
  --image "$ROOT/inputs/object_like_conditions/recursive_image_entry_gpu1_20260507_1842/ifs/ifs_solid_depth_front.png" \
  --dinov3-model "$DINO" \
  --out "$BASE_OUT/ifs_procedural" \
  --case-name ifs_procedural_masked_repair \
  --grammars fork fork_side continue side echo \
  --depths 3 \
  --steps 1 2 4 \
  --fit-scale 0.62 \
  --seed 721

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_recursive_masked_repair_workflow.py" \
  --mesh "$ROOT/inputs/procedural_meshes/lsystem_branch.obj" \
  --image "$ROOT/inputs/object_like_conditions/recursive_image_entry_gpu1_20260507_1842/lsystem/lsystem_warm_silhouette.png" \
  --dinov3-model "$DINO" \
  --out "$BASE_OUT/lsystem_procedural" \
  --case-name lsystem_procedural_masked_repair \
  --grammars fork fork_side continue side echo \
  --depths 3 \
  --steps 1 2 4 \
  --fit-scale 0.62 \
  --seed 722
