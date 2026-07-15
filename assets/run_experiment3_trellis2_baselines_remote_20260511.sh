#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/experiment3_sparse_latent_vs_meshspace_20260511"
LOG="$ROOT/logs/experiment3_sparse_latent_vs_meshspace_20260511"
MANIFEST="$OUT/conditions/condition_manifest.csv"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"
DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"

mkdir -p "$OUT/trellis2_oneshot" "$OUT/trellis2_latentcopy" "$OUT/pids" "$LOG" \
  "$ROOT/cache/local_tmp/experiment3_sparse_latent_vs_meshspace_20260511" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/experiment3_sparse_latent_vs_meshspace_20260511"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/experiment3_sparse_latent_vs_meshspace_20260511"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

need_manifest() {
  if [[ ! -f "$MANIFEST" ]]; then
    echo "missing manifest: $MANIFEST" >&2
    exit 2
  fi
}

case_rows_json() {
  "$PY" - <<'PY' "$MANIFEST" "$@"
import csv, json, sys
manifest = sys.argv[1]
want = set(sys.argv[2:])
rows = []
with open(manifest, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        if not want or row["case_short"] in want:
            rows.append(row)
print(json.dumps(rows))
PY
}

run_one_row() {
  local gpu="$1"
  local mode="$2"
  local row_json="$3"
  local case_short
  local image
  local seed
  case_short="$("$PY" - <<'PY' "$row_json"
import json, sys
print(json.loads(sys.argv[1])["case_short"])
PY
)"
  if [[ "$mode" == "oneshot" ]]; then
    image="$("$PY" - <<'PY' "$row_json"
import json, sys
print(json.loads(sys.argv[1])["target_guide"])
PY
)"
    seed=2026061101
    out_dir="$OUT/trellis2_oneshot/${case_short}_target_seed${seed}"
    script="$ROOT/assets/trellis2_dinov3_official_min_smoke.py"
  elif [[ "$mode" == "latentcopy" ]]; then
    image="$("$PY" - <<'PY' "$row_json"
import json, sys
print(json.loads(sys.argv[1])["root_guide"])
PY
)"
    seed=2026061201
    out_dir="$OUT/trellis2_latentcopy/${case_short}_root_seed${seed}"
    script="$ROOT/assets/trellis2_dinov3_latent_transform_baseline_20260510.py"
  else
    echo "bad mode: $mode" >&2
    return 2
  fi
  local abs_image="$ROOT/$image"
  local log="$LOG/${mode}_${case_short}.log"
  if [[ -f "$out_dir/summary.json" ]]; then
    echo "SKIP_EXISTING mode=$mode case=$case_short out=$out_dir" | tee -a "$log"
    return 0
  fi
  if [[ ! -f "$abs_image" ]]; then
    echo "MISSING_IMAGE mode=$mode case=$case_short image=$abs_image" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/experiment3_sparse_latent_vs_meshspace_20260511/gpu${gpu}_${mode}_${case_short}"
  mkdir -p "$out_dir" "$TRITON_CACHE_DIR"
  echo "BEGIN $(date -Is) mode=$mode gpu=$gpu case=$case_short image=$abs_image out=$out_dir" | tee "$log"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$script" \
    --image "$abs_image" \
    --dinov3-model "$DINO" \
    --out "$out_dir" \
    --steps 8 \
    --seed "$seed" 2>&1 | tee -a "$log"
  local status=${PIPESTATUS[0]}
  echo "END $(date -Is) mode=$mode case=$case_short status=$status" | tee -a "$log"
  return "$status"
}

run_lane() {
  local gpu="$1"
  local mode="$2"
  shift 2
  need_manifest
  local rows_json
  rows_json="$(case_rows_json "$@")"
  "$PY" - <<'PY' "$rows_json" | while IFS= read -r row_json; do
import json, sys
for row in json.loads(sys.argv[1]):
    print(json.dumps(row))
PY
    run_one_row "$gpu" "$mode" "$row_json" || true
  done
}

metrics() {
  local case_args=()
  while IFS= read -r mesh; do
    rel="${mesh#$OUT/}"
    label="${rel%/trellis2_dinov3_min.obj}"
    label="${label//\//__}"
    case_args+=(--case "$label=$mesh")
  done < <(find "$OUT/trellis2_oneshot" -name trellis2_dinov3_min.obj -type f | sort)
  while IFS= read -r mesh; do
    rel="${mesh#$OUT/}"
    label="${rel%/mesh.obj}"
    label="${label//\//__}"
    case_args+=(--case "$label=$mesh")
  done < <(find "$OUT/trellis2_latentcopy" -path '*/copy_shift_upper_z/mesh.obj' -type f | sort)
  if [[ ${#case_args[@]} -eq 0 ]]; then
    echo "NO_MESHES_FOR_METRICS"
    return 0
  fi
  "$PY" "$ROOT/assets/recursive_growth_mesh_metrics.py" \
    "${case_args[@]}" \
    --out-json "$OUT/experiment3_trellis2_baseline_metrics.json" \
    --out-csv "$OUT/experiment3_trellis2_baseline_metrics.csv" \
    --occupancy-resolution 64 \
    --primary-connectivity occupancy 2>&1 | tee "$LOG/metrics_trellis2.log"
}

status() {
  echo "STATUS $(date -Is)"
  for pid_file in "$OUT"/pids/experiment3_*.pid; do
    [[ -f "$pid_file" ]] || continue
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" 2>/dev/null; then
      echo "RUNNING $(basename "$pid_file" .pid) pid=$pid"
    else
      echo "DONE_OR_EXITED $(basename "$pid_file" .pid) pid=$pid"
    fi
  done
  find "$OUT/trellis2_oneshot" "$OUT/trellis2_latentcopy" -name summary.json -type f 2>/dev/null | sort | while read -r s; do
    "$PY" - <<'PY' "$s"
import json, sys
from pathlib import Path
p=Path(sys.argv[1])
d=json.loads(p.read_text())
print(f"SUMMARY {p.parent} status={d.get('status','ok')} kind={d.get('kind')} faces={d.get('faces')} base_tokens={d.get('base_shape_tokens')} error={d.get('error')}")
PY
  done
  find "$OUT/trellis2_oneshot" -name trellis2_dinov3_min.obj -type f | wc -l | awk '{print "ONESHOT_OBJ_COUNT "$1}'
  find "$OUT/trellis2_latentcopy" -path '*/copy_shift_upper_z/mesh.obj' -type f | wc -l | awk '{print "LATENTCOPY_OBJ_COUNT "$1}'
}

start_p0() {
  need_manifest
  nohup bash "$ROOT/assets/run_experiment3_trellis2_baselines_remote_20260511.sh" lane 4 oneshot \
    tree_crown root_fan bismuth radial_ornament spider_rosette > "$LOG/lane_oneshot_p0.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/experiment3_oneshot_p0.pid"
  nohup bash "$ROOT/assets/run_experiment3_trellis2_baselines_remote_20260511.sh" lane 5 latentcopy \
    tree_crown root_fan bismuth radial_ornament spider_rosette > "$LOG/lane_latentcopy_p0.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/experiment3_latentcopy_p0.pid"
  echo "STARTED_P0 $(date -Is) pids=$(cat "$OUT"/pids/experiment3_*.pid | tr '\n' ' ')"
}

case "${1:-status}" in
  start-p0) start_p0 ;;
  lane) shift; run_lane "$@" ;;
  metrics) metrics ;;
  status) status ;;
  *) echo "usage: $0 {start-p0|lane <gpu> <oneshot|latentcopy> [case_short...]|metrics|status}" >&2; exit 2 ;;
esac
