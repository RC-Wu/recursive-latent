#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-strict_visual_matched_texture_v5c_detail_20260510}"
SEED="${SEED:-20260510}"
INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_v5c_detail_naturalized_20260510}"
INPUTS="$ROOT/inputs/$INPUT_NAME"
OUT="$ROOT/results/$RUN"
LOG="$ROOT/logs/$RUN"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$LOG" "$OUT" "$INPUTS" \
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

generate_inputs() {
  echo "=== GENERATE strict visual matched V5c detail OBJ inputs $(date)"
  "$PY" "$ROOT/assets/strict_visual_matched_cases_v5c_detail_naturalized_20260510.py" \
    --root "$ROOT" \
    --out "$INPUTS" \
    --seed "$SEED"
  "$PY" - "$INPUTS" <<'PY'
import csv
import sys
from pathlib import Path

inp = Path(sys.argv[1])
rows = list(csv.DictReader((inp / "manifest.csv").open(newline="", encoding="utf-8")))
for gpu in (4, 5, 6, 7):
    selected = [row for i, row in enumerate(rows) if i % 4 == gpu - 4]
    lines = [f"{r['case_id']}|{r['mesh_path']}|{r['guide_image']}|{r['seed']}" for r in selected]
    (inp / f"gpu{gpu}_cases.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
print({gpu: len((inp / f"gpu{gpu}_cases.txt").read_text().splitlines()) for gpu in (4, 5, 6, 7)})
PY
  echo "=== GENERATED V5c detail $(date)"
}

summary_ok() {
  local summary="$1"
  [[ -f "$summary" ]] && grep -q '"status": "ok"' "$summary"
}

run_case() {
  local gpu="$1"
  local label="$2"
  local mesh="$3"
  local guide="$4"
  local seed="$5"
  local steps="${STEPS:-8}"
  local tex="${TEXTURE_SIZE:-2048}"
  local target="$OUT/${label}_steps${steps}_tex${tex}_seed${seed}_xformers"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"
  mkdir -p "$TRITON_CACHE_DIR"
  if summary_ok "$target/summary.json"; then
    echo "=== SKIP $label already ok $(date)"
    return 0
  fi
  echo "=== START $label gpu=$gpu steps=$steps tex=$tex seed=$seed $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
    --mesh "$mesh" \
    --image "$guide" \
    --dinov3-model "$DINO" \
    --out "$target" \
    --steps "$steps" \
    --seed "$seed" \
    --resolution 512 \
    --texture-size "$tex" \
    --preprocess || echo "=== FAILED_NONFATAL $label exit=$? $(date)"
  echo "=== END $label $(date)"
}

if [[ "${1:-}" == "--worker" ]]; then
  gpu="$2"
  while IFS='|' read -r label mesh guide seed; do
    [[ -z "${label:-}" ]] && continue
    run_case "$gpu" "$label" "$mesh" "$guide" "$seed"
  done < "$INPUTS/gpu${gpu}_cases.txt"
  echo "=== WORKER_DONE gpu=$gpu $(date)"
  exit 0
fi

generate_inputs
for gpu in 4 5 6 7; do
  nohup bash "$ROOT/assets/launch_strict_visual_matched_texture_v5c_detail_20260510.sh" --worker "$gpu" \
    > "$LOG/gpu${gpu}_strict_visual_matched_v5c_detail.log" 2>&1 &
  echo "gpu${gpu}_strict_visual_matched_v5c_detail:$!"
done

sleep 5
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | sed -n '5,8p'
for f in "$LOG"/gpu*_strict_visual_matched_v5c_detail.log; do
  echo "==== $(basename "$f")"
  tail -12 "$f" || true
done
