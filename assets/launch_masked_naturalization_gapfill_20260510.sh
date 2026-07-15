#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-masked_naturalization_gapfill_20260510}"
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

run_masked() {
  local gpu="$1"
  local label="$2"
  local mesh="$3"
  local image="$4"
  local seed="$5"
  local target="$OUT/${label}_masked_alpha_grid"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}_masked"
  mkdir -p "$TRITON_CACHE_DIR"
  if [[ -f "$target/summary.json" ]] && grep -q '"status": "ok"' "$target/summary.json"; then
    echo "=== SKIP masked $label already ok $(date)"
    return 0
  fi
  echo "=== START masked $label gpu=$gpu seed=$seed $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_recursive_masked_repair_workflow.py" \
    --mesh "$mesh" \
    --image "$image" \
    --dinov3-model "$DINO" \
    --out "$target" \
    --case-name "$label" \
    --grammars fork_side continue \
    --depths 3 \
    --steps 2 \
    --blend-alphas 0.0 0.25 1.0 \
    --fit-scale 0.62 \
    --seed "$seed"
  echo "=== END masked $label $(date)"
}

run_ruleonly() {
  local gpu="$1"
  local label="$2"
  local mesh="$3"
  local seed="$4"
  local target="$OUT/${label}_rule_only_direct"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}_ruleonly"
  mkdir -p "$TRITON_CACHE_DIR"
  if [[ -f "$target/summary.json" ]]; then
    echo "=== SKIP ruleonly $label summary exists $(date)"
    return 0
  fi
  echo "=== START ruleonly $label gpu=$gpu seed=$seed $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_recursive_slat_grammar_workflow.py" \
    --mesh "$mesh" \
    --out "$target" \
    --case-name "$label" \
    --grammars fork_side continue \
    --depths 3 \
    --fit-scale 0.62 \
    --max-tokens 16000 \
    --seed "$seed" \
    --compete-jitter 0.0
  echo "=== END ruleonly $label $(date)"
}

case "${1:-launch}" in
  worker-masked-lsys)
    run_masked 4 lsystem_branch "$ROOT/inputs/procedural_meshes/lsystem_branch.obj" "$ROOT/inputs/object_like_conditions/recursive_image_entry_gpu1_20260507_1842/lsystem/lsystem_warm_silhouette.png" 9104
    ;;
  worker-masked-ifs)
    run_masked 5 ifs_branch "$ROOT/inputs/procedural_meshes/ifs_branch_tree.obj" "$ROOT/inputs/object_like_conditions/recursive_image_entry_gpu1_20260507_1842/ifs/ifs_solid_depth_front.png" 9105
    ;;
  worker-rule-lsys)
    run_ruleonly 6 lsystem_branch "$ROOT/inputs/procedural_meshes/lsystem_branch.obj" 9106
    ;;
  worker-rule-ifs)
    run_ruleonly 7 ifs_branch "$ROOT/inputs/procedural_meshes/ifs_branch_tree.obj" 9107
    ;;
  launch)
    nohup bash "$ROOT/assets/launch_masked_naturalization_gapfill_20260510.sh" worker-masked-lsys > "$LOG/gpu4_lsystem_masked.log" 2>&1 &
    echo "gpu4_lsystem_masked:$!"
    nohup bash "$ROOT/assets/launch_masked_naturalization_gapfill_20260510.sh" worker-masked-ifs > "$LOG/gpu5_ifs_masked.log" 2>&1 &
    echo "gpu5_ifs_masked:$!"
    nohup bash "$ROOT/assets/launch_masked_naturalization_gapfill_20260510.sh" worker-rule-lsys > "$LOG/gpu6_lsystem_ruleonly.log" 2>&1 &
    echo "gpu6_lsystem_ruleonly:$!"
    nohup bash "$ROOT/assets/launch_masked_naturalization_gapfill_20260510.sh" worker-rule-ifs > "$LOG/gpu7_ifs_ruleonly.log" 2>&1 &
    echo "gpu7_ifs_ruleonly:$!"
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
