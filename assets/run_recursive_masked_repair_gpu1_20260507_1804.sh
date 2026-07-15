#!/usr/bin/env bash
set -euo pipefail

ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env

mkdir -p "$ROOT/logs" "$ROOT/cache/tmp" "$ROOT/cache/matplotlib" "$ROOT/cache/torch_extensions"
export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home" TRANSFORMERS_CACHE="$ROOT/hf_home/transformers" TORCH_HOME="$ROOT/cache/torch" XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/tmp" MPLCONFIGDIR="$ROOT/cache/matplotlib" TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export TRITON_CACHE_DIR="$ROOT/cache/triton/recursive_masked_repair_gpu1_20260507_1804"
export ATTN_BACKEND=xformers CUDA_VISIBLE_DEVICES=1

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"
BASE_OUT="$ROOT/results/trellis2_recursive_masked_repair/recursive_masked_repair_gpu1_20260507_1804"

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_recursive_masked_repair_workflow.py" \
  --mesh "$ROOT/inputs/procedural_meshes/dla_cluster_voxels.obj" \
  --image "$ROOT/inputs/procedural_baselines/dla_cluster_points.png" \
  --dinov3-model "$DINO" \
  --out "$BASE_OUT/dla_procedural" \
  --case-name dla_procedural_masked_repair \
  --grammars radial side echo \
  --depths 2 \
  --steps 1 2 4 \
  --fit-scale 0.58 \
  --seed 731

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_recursive_masked_repair_workflow.py" \
  --mesh "$ROOT/results/trellis2_object_like_image_entry/recursive_image_entry_gpu1_retryshim_20260507_1845/ifs_solid_depth_front_steps4_seed410/trellis2_dinov3_min.obj" \
  --image "$ROOT/inputs/object_like_conditions/recursive_image_entry_gpu1_20260507_1842/ifs/ifs_solid_depth_front.png" \
  --dinov3-model "$DINO" \
  --out "$BASE_OUT/image_ifs_solid_root" \
  --case-name image_ifs_solid_root_masked_repair \
  --grammars fork side continue echo \
  --depths 2 \
  --steps 1 2 4 \
  --fit-scale 0.60 \
  --seed 732

"$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_recursive_masked_repair_workflow.py" \
  --mesh "$ROOT/results/trellis2_object_like_image_entry/recursive_image_entry_gpu1_retryshim_20260507_1845/lsystem_warm_silhouette_steps4_seed410/trellis2_dinov3_min.obj" \
  --image "$ROOT/inputs/object_like_conditions/recursive_image_entry_gpu1_20260507_1842/lsystem/lsystem_warm_silhouette.png" \
  --dinov3-model "$DINO" \
  --out "$BASE_OUT/image_lsystem_warm_root" \
  --case-name image_lsystem_warm_root_masked_repair \
  --grammars fork side continue echo \
  --depths 2 \
  --steps 1 2 4 \
  --fit-scale 0.58 \
  --seed 733
