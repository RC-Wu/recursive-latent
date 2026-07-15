#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-gapfill_non_tree_texturing_selected_20260510}"
SRC_RUN="${SRC_RUN:-masked_naturalization_gapfill_20260510}"
OUT="$ROOT/results/$RUN"
LOG="$ROOT/logs/$RUN"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT" "$LOG" \
  "$ROOT/cache/tmp" "$ROOT/cache/torch" "$ROOT/cache/xdg" \
  "$ROOT/cache/matplotlib" "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/$RUN"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/tmp"
export TEMP="$ROOT/cache/tmp"
export TMP="$ROOT/cache/tmp"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"

run_one() {
  local gpu="$1"
  local label="$2"
  local mesh="$3"
  local image="$4"
  local seed="$5"
  local target="$OUT/$label"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}_${label}"
  mkdir -p "$TRITON_CACHE_DIR" "$target"
  if [[ -f "$target/summary.json" ]] && grep -q '"status": "ok"' "$target/summary.json"; then
    echo "=== SKIP $label already ok $(date)"
    return 0
  fi
  echo "=== START $label gpu=$gpu seed=$seed $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
    --mesh "$mesh" \
    --image "$image" \
    --dinov3-model "$DINO" \
    --out "$target" \
    --steps 4 \
    --texture-size 1024 \
    --resolution 512 \
    --seed "$seed"
  echo "=== END $label $(date)"
}

case "${1:-launch}" in
  worker-coral-weak)
    run_one 4 coral_weakblend_alpha025_fork_d2 "$ROOT/results/$SRC_RUN/coral_v3b_masked_alpha_grid/fork_side/steps_2/alpha_0p25/depth_02/masked/mesh.obj" "$ROOT/inputs/strict_visual_matched_cases_v3b_connected_20260510/_guides/v3_coral_porosity_guide.png" 9604
    ;;
  worker-coral-localN)
    run_one 5 coral_masked_localN_alpha1_fork_d2 "$ROOT/results/$SRC_RUN/coral_v3b_masked_alpha_grid/fork_side/steps_2/alpha_1p0/depth_02/masked/mesh.obj" "$ROOT/inputs/strict_visual_matched_cases_v3b_connected_20260510/_guides/v3_coral_porosity_guide.png" 9605
    ;;
  worker-pyrite-weak)
    run_one 6 pyrite_weakblend_alpha025_fork_d2 "$ROOT/results/$SRC_RUN/pyrite_v3b_masked_alpha_grid/fork_side/steps_2/alpha_0p25/depth_02/masked/mesh.obj" "$ROOT/inputs/strict_visual_matched_cases_v3b_connected_20260510/_guides/v3_pyrite_facets_guide.png" 9606
    ;;
  worker-pyrite-localN)
    run_one 7 pyrite_masked_localN_alpha1_fork_d2 "$ROOT/results/$SRC_RUN/pyrite_v3b_masked_alpha_grid/fork_side/steps_2/alpha_1p0/depth_02/masked/mesh.obj" "$ROOT/inputs/strict_visual_matched_cases_v3b_connected_20260510/_guides/v3_pyrite_facets_guide.png" 9607
    ;;
  launch)
    nohup bash "$ROOT/assets/launch_gapfill_non_tree_texturing_selected_20260510.sh" worker-coral-weak > "$LOG/gpu4_coral_weak.log" 2>&1 &
    echo "gpu4_coral_weak:$!"
    nohup bash "$ROOT/assets/launch_gapfill_non_tree_texturing_selected_20260510.sh" worker-coral-localN > "$LOG/gpu5_coral_localN.log" 2>&1 &
    echo "gpu5_coral_localN:$!"
    nohup bash "$ROOT/assets/launch_gapfill_non_tree_texturing_selected_20260510.sh" worker-pyrite-weak > "$LOG/gpu6_pyrite_weak.log" 2>&1 &
    echo "gpu6_pyrite_weak:$!"
    nohup bash "$ROOT/assets/launch_gapfill_non_tree_texturing_selected_20260510.sh" worker-pyrite-localN > "$LOG/gpu7_pyrite_localN.log" 2>&1 &
    echo "gpu7_pyrite_localN:$!"
    sleep 8
    nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | sed -n '5,8p'
    for f in "$LOG"/*.log; do
      echo "==== $(basename "$f")"
      tail -20 "$f" || true
    done
    ;;
  *)
    echo "unknown mode: ${1:-}" >&2
    exit 2
    ;;
esac
