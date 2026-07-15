#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-strict_visual_matched_texture_V67_lsystem_branch_same_scaffold_tapered_twig_BC_20260512_remote}"
SEED="${SEED:-20260512}"
INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_V67_lsystem_branch_same_scaffold_tapered_twig_20260512}"
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
    *) echo "ERROR: V67 L-system branch only allows GPU 4/5/6/7, got '$gpu'" >&2; exit 2 ;;
  esac
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"
  mkdir -p "$TRITON_CACHE_DIR"
  while IFS='|' read -r label mesh guide seed _gpu; do
    [[ -z "${label:-}" ]] && continue
    [[ "$_gpu" == "$gpu" ]] || continue
    if [[ "${V67_PRIORITY_BC_ONLY:-1}" == "1" ]]; then
      case "$label" in
        V67_lsys_branch_tapered_dense_B|V67_lsys_branch_tapered_fine_C) ;;
        *) echo "=== SKIP $label not priority B/C for first V67 remote pass"; continue ;;
      esac
    fi
    steps="${STEPS:-8}"
    tex="${TEXTURE_SIZE:-2048}"
    target="$OUT/${label}_steps${steps}_tex${tex}_seed${seed}_xformers"
    if [[ -f "$target/summary.json" ]] && grep -q '"status": "ok"' "$target/summary.json"; then
      echo "=== SKIP $label already ok $(date)"
      continue
    fi
    echo "=== START $label gpu=$gpu steps=$steps tex=$tex seed=$seed v67_lsystem_same_scaffold_tapered_twig $(date)"
    CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
      --mesh "$mesh" --image "$guide" --dinov3-model "$DINO" --out "$target" \
      --steps "$steps" --seed "$seed" --resolution 512 --texture-size "$tex" --preprocess \
      || echo "=== FAILED_NONFATAL $label exit=$? $(date)"
    echo "=== END $label $(date)"
  done < "$INPUTS/gpu${gpu}_cases.txt"
  echo "=== WORKER_DONE gpu=$gpu $(date)"
  exit 0
fi

echo "=== GENERATE V67 L-system same-scaffold tapered-twig OBJ inputs $(date)"
"$PY" "$ROOT/assets/strict_visual_matched_cases_V67_lsystem_branch_same_scaffold_tapered_twig_20260512.py" \
  --root "$ROOT" --out "$INPUTS" --seed "$SEED"
echo "=== GENERATED V67 L-system same-scaffold tapered-twig OBJ inputs $(date)"

if [[ "${1:-}" == "--generate-only" ]]; then
  echo "=== GENERATE_ONLY_DONE $INPUTS $(date)"
  exit 0
fi

for gpu in ${V67_GPUS:-4 5}; do
  case "$gpu" in
    4|5|6|7) ;;
    *) echo "ERROR: V67_GPUS must only contain 4/5/6/7, got '$gpu'" >&2; exit 2 ;;
  esac
  nohup bash "$ROOT/assets/launch_strict_visual_matched_texture_V67_lsystem_branch_same_scaffold_tapered_twig_20260512.sh" --worker "$gpu" \
    > "$LOG/gpu${gpu}_strict_visual_matched_V67_lsystem_same_scaffold_tapered_twig.log" 2>&1 &
  echo "gpu${gpu}_strict_visual_matched_V67_lsystem_same_scaffold_tapered_twig:$!"
done

sleep 5
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | sed -n '5,8p'
for f in "$LOG"/gpu*_strict_visual_matched_V67_lsystem_same_scaffold_tapered_twig.log; do
  echo "==== $(basename "$f")"
  tail -12 "$f" || true
done
