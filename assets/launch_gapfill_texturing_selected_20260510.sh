#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-gapfill_texturing_selected_20260510}"
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
IMAGE="$ROOT/inputs/object_like_conditions/recursive_image_entry_gpu1_20260507_1842/lsystem/lsystem_warm_silhouette.png"

run_one() {
  local gpu="$1"
  local label="$2"
  local mesh="$3"
  local seed="$4"
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
    --image "$IMAGE" \
    --dinov3-model "$DINO" \
    --out "$target" \
    --steps 4 \
    --texture-size 1024 \
    --resolution 512 \
    --seed "$seed"
  echo "=== END $label $(date)"
}

case "${1:-launch}" in
  worker-ruleonly)
    run_one 4 lsystem_rule_only_direct_fork_d3 "$ROOT/results/$SRC_RUN/lsystem_branch_rule_only_direct/fork_side/depth_03/mesh.obj" 9504
    ;;
  worker-noN)
    run_one 5 lsystem_noN_alpha0_fork_d3 "$ROOT/results/$SRC_RUN/lsystem_branch_masked_alpha_grid/fork_side/steps_2/alpha_0p0/depth_03/masked/mesh.obj" 9505
    ;;
  worker-weak)
    run_one 6 lsystem_weakblend_alpha025_fork_d3 "$ROOT/results/$SRC_RUN/lsystem_branch_masked_alpha_grid/fork_side/steps_2/alpha_0p25/depth_03/masked/mesh.obj" 9506
    ;;
  worker-localN)
    run_one 7 lsystem_masked_localN_alpha1_fork_d3 "$ROOT/results/$SRC_RUN/lsystem_branch_masked_alpha_grid/fork_side/steps_2/alpha_1p0/depth_03/masked/mesh.obj" 9507
    ;;
  launch)
    nohup bash "$ROOT/assets/launch_gapfill_texturing_selected_20260510.sh" worker-ruleonly > "$LOG/gpu4_ruleonly.log" 2>&1 &
    echo "gpu4_ruleonly:$!"
    nohup bash "$ROOT/assets/launch_gapfill_texturing_selected_20260510.sh" worker-noN > "$LOG/gpu5_noN.log" 2>&1 &
    echo "gpu5_noN:$!"
    nohup bash "$ROOT/assets/launch_gapfill_texturing_selected_20260510.sh" worker-weak > "$LOG/gpu6_weak.log" 2>&1 &
    echo "gpu6_weak:$!"
    nohup bash "$ROOT/assets/launch_gapfill_texturing_selected_20260510.sh" worker-localN > "$LOG/gpu7_localN.log" 2>&1 &
    echo "gpu7_localN:$!"
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
