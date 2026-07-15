#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-strict_visual_matched_texture_V24_priority_rerun_20260510}"
SEED="${SEED:-20260510}"
INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_V24_priority_rerun_20260510}"
INPUTS="$ROOT/inputs/$INPUT_NAME"
OUT="$ROOT/results/$RUN"
LOG="$ROOT/logs/$RUN"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$LOG" "$OUT" "$INPUTS" "$ROOT/cache/local_tmp/$RUN" "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/$RUN"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/$RUN"
export TEMP="$ROOT/cache/local_tmp/$RUN"
export TMP="$ROOT/cache/local_tmp/$RUN"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"

if [[ "${1:-}" == "--worker" ]]; then
  gpu="$2"
  case "$gpu" in
    4|5|6|7) ;;
    *) echo "ERROR: V24 priority rerun only allows GPU 4/5/6/7, got '$gpu'" >&2; exit 2 ;;
  esac
  while IFS='|' read -r label mesh guide seed _gpu; do
    [[ -z "${label:-}" ]] && continue
    steps="${STEPS:-8}"
    tex="${TEXTURE_SIZE:-2048}"
    target="$OUT/${label}_steps${steps}_tex${tex}_seed${seed}_xformers"
    export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"
    mkdir -p "$TRITON_CACHE_DIR"
    if [[ -f "$target/summary.json" ]] && grep -q '"status": "ok"' "$target/summary.json"; then
      echo "=== SKIP $label already ok $(date)"
      continue
    fi
    echo "=== START $label gpu=$gpu steps=$steps tex=$tex seed=$seed v24_priority_rerun_obj_pbr_only $(date)"
    CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
      --mesh "$mesh" --image "$guide" --dinov3-model "$DINO" --out "$target" \
      --steps "$steps" --seed "$seed" --resolution 512 --texture-size "$tex" --preprocess \
      || echo "=== FAILED_NONFATAL $label exit=$? $(date)"
    echo "=== END $label $(date)"
  done < "$INPUTS/gpu${gpu}_cases.txt"
  echo "=== WORKER_DONE gpu=$gpu $(date)"
  exit 0
fi

echo "=== GENERATE V24 priority rerun strict matched OBJ inputs $(date)"
"$PY" "$ROOT/assets/strict_visual_matched_cases_V24_priority_rerun_20260510.py" \
  --root "$ROOT" --out "$INPUTS" --seed "$SEED"
echo "=== GENERATED V24 priority rerun strict matched OBJ inputs $(date)"

if [[ "${1:-}" == "--generate-only" ]]; then
  echo "=== GENERATE_ONLY_DONE $INPUTS $(date)"
  exit 0
fi

for gpu in 4 5 6 7; do
  nohup bash "$ROOT/assets/launch_strict_visual_matched_texture_V24_priority_rerun_20260510.sh" --worker "$gpu" \
    > "$LOG/gpu${gpu}_strict_visual_matched_V24_priority_rerun.log" 2>&1 &
  echo "gpu${gpu}_strict_visual_matched_V24_priority_rerun:$!"
done

sleep 5
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | sed -n '5,8p'
for f in "$LOG"/gpu*_strict_visual_matched_V24_priority_rerun.log; do
  echo "==== $(basename "$f")"
  tail -12 "$f" || true
done
