#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/log_spiral_image_root_remote_20260512n"
COND="$ROOT/results/log_spiral_conditions_20260512n"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"
DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"

mkdir -p "$OUT/image_roots" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/log_spiral_image_root_remote_20260512n" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/log_spiral_image_root_remote_20260512n"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/log_spiral_image_root_remote_20260512n"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

run_root() {
  local gpu="$1"
  local case_id="$2"
  local image="$3"
  local seed="$4"
  local steps="$5"
  local label="${case_id}_steps${steps}_seed${seed}"
  local target="$OUT/image_roots/$label"
  local log="$LOG/$label.log"
  if [[ ! -f "$image" ]]; then
    echo "MISSING_IMAGE $image" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/log_spiral_image_root_remote_20260512n/gpu${gpu}_${label}"
  mkdir -p "$target" "$TRITON_CACHE_DIR"
  echo "IMAGE_ROOT_BEGIN $(date -Is) gpu=$gpu label=$label image=$image seed=$seed steps=$steps" | tee "$log"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_dinov3_official_min_smoke.py" \
    --image "$image" \
    --dinov3-model "$DINO" \
    --out "$target" \
    --steps "$steps" \
    --seed "$seed" 2>&1 | tee -a "$log"
  local status=${PIPESTATUS[0]}
  echo "IMAGE_ROOT_END $(date -Is) label=$label status=$status" | tee -a "$log"
  return "$status"
}

run_lane() {
  case "$1" in
    lane6)
      run_root 6 log_spiral_surface_d4_soft "$COND/log_spiral_surface_d4_soft_condition.png" 202615601 6 || true
      run_root 6 log_spiral_surface_d4_ink "$COND/log_spiral_surface_d4_ink_condition.png" 202615602 6 || true
      ;;
    lane7)
      run_root 7 log_spiral_dense_surface_d4_soft "$COND/log_spiral_dense_surface_d4_soft_condition.png" 202615701 6 || true
      run_root 7 log_spiral_dense_surface_d4_ink "$COND/log_spiral_dense_surface_d4_ink_condition.png" 202615702 6 || true
      ;;
    *) echo "unknown lane $1" >&2; return 2 ;;
  esac
}

write_manifest() {
  cat > "$OUT/log_spiral_image_root_manifest_20260512n.tsv" <<TSV
label	gpu	source_image	seed	steps	intended_role	claim_scope
log_spiral_surface_d4_soft_steps6_seed202615601	6	$COND/log_spiral_surface_d4_soft_condition.png	202615601	6	image-conditioned root diagnostic	not a final result until mesh preview/metrics pass
log_spiral_surface_d4_ink_steps6_seed202615602	6	$COND/log_spiral_surface_d4_ink_condition.png	202615602	6	image-conditioned root diagnostic	not a final result until mesh preview/metrics pass
log_spiral_dense_surface_d4_soft_steps6_seed202615701	7	$COND/log_spiral_dense_surface_d4_soft_condition.png	202615701	6	image-conditioned root diagnostic	not a final result until mesh preview/metrics pass
log_spiral_dense_surface_d4_ink_steps6_seed202615702	7	$COND/log_spiral_dense_surface_d4_ink_condition.png	202615702	6	image-conditioned root diagnostic	not a final result until mesh preview/metrics pass
TSV
}

metrics_all() {
  local case_args=()
  while IFS= read -r mesh; do
    local label
    label="$(basename "$(dirname "$mesh")")"
    case_args+=(--case "$label=$mesh")
  done < <(find "$OUT/image_roots" -name trellis2_dinov3_min.obj -type f | sort)
  if [[ ${#case_args[@]} -eq 0 ]]; then
    echo "NO_IMAGE_ROOTS_FOR_METRICS"
    return 0
  fi
  "$PY" "$ROOT/assets/recursive_growth_mesh_metrics.py" \
    "${case_args[@]}" \
    --out-json "$OUT/metrics/log_spiral_image_root_metrics_20260512n.json" \
    --out-csv "$OUT/metrics/log_spiral_image_root_metrics_20260512n.csv" \
    --occupancy-resolution 64 \
    --primary-connectivity occupancy 2>&1 | tee "$LOG/metrics_all.log"
}

status_all() {
  echo "STATUS $(date -Is)"
  for pid_file in "$OUT"/pids/*.pid; do
    [[ -f "$pid_file" ]] || continue
    local pid
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" 2>/dev/null; then
      echo "RUNNING $(basename "$pid_file" .pid) pid=$pid"
    else
      echo "DONE_OR_EXITED $(basename "$pid_file" .pid) pid=$pid"
    fi
  done
  find "$OUT/image_roots" -maxdepth 2 -name summary.json -print 2>/dev/null | sort | while read -r summary; do
    "$PY" - <<'PY' "$summary"
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text())
print(f"SUMMARY {p.parent.name} status={d.get('status','ok')} verts={d.get('vertices')} faces={d.get('faces')} tokens={d.get('shape_latent_tokens')} error={d.get('error')}")
PY
  done
  find "$OUT/image_roots" -name trellis2_dinov3_min.obj -type f | wc -l | awk '{print "IMAGE_ROOT_OBJ_COUNT "$1}'
  find "$OUT/image_roots" -name trellis2_dinov3_min_preview.png -type f | wc -l | awk '{print "PREVIEW_COUNT "$1}'
}

start_all() {
  write_manifest
  nohup bash "$ROOT/assets/run_log_spiral_image_root_remote_20260512n.sh" lane6 > "$LOG/lane6.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/lane6.pid"
  nohup bash "$ROOT/assets/run_log_spiral_image_root_remote_20260512n.sh" lane7 > "$LOG/lane7.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/lane7.pid"
  echo "STARTED_IMAGE_ROOTS $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start}" in
  start) start_all ;;
  lane6|lane7) run_lane "$1" ;;
  metrics) metrics_all ;;
  status) status_all ;;
  manifest) write_manifest ;;
  *) echo "usage: $0 {start|status|metrics|lane6|lane7|manifest}" >&2; exit 2 ;;
esac
