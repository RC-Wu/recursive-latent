#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/fern_root_image_generation_remote_20260511c"
IMGROOT="$ROOT/downloads/fern_spider_sources_20260511"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/image_roots" "$OUT/logs" "$OUT/pids" "$OUT/metrics" \
  "$ROOT/cache/local_tmp/fern_root_image_generation_remote_20260511c" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/fern_root_image_generation_remote_20260511c"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/fern_root_image_generation_remote_20260511c"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"

run_root() {
  local gpu="$1"
  local case_id="$2"
  local image="$3"
  local seed="$4"
  local steps="$5"
  local preprocess="$6"
  local label="${case_id}_steps${steps}_seed${seed}_${preprocess}"
  local target="$OUT/image_roots/$label"
  local log="$LOG/$label.log"
  if [[ ! -f "$image" ]]; then
    echo "MISSING_IMAGE $image" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/fern_root_image_generation_remote_20260511c/gpu${gpu}_${label}"
  mkdir -p "$target" "$TRITON_CACHE_DIR"
  echo "ROOT_BEGIN $(date -Is) gpu=$gpu case=$case_id image=$image seed=$seed steps=$steps preprocess=$preprocess" | tee "$log"
  local preprocess_arg=()
  if [[ "$preprocess" == "preprocess" ]]; then
    preprocess_arg=(--preprocess)
  fi
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_dinov3_official_min_smoke.py" \
    --image "$image" \
    --dinov3-model "$DINO" \
    --out "$target" \
    --steps "$steps" \
    --seed "$seed" \
    "${preprocess_arg[@]}" 2>&1 | tee -a "$log"
  local status=${PIPESTATUS[0]}
  echo "ROOT_END $(date -Is) label=$label status=$status" | tee -a "$log"
  return "$status"
}

run_lane() {
  local lane="$1"
  case "$lane" in
    spider)
      run_root 4 spider_plant_commons_pd "$IMGROOT/spider_plant_commons_pd_condition_1024.png" 202605801 10 preprocess
      run_root 4 spider_plant_commons_pd "$IMGROOT/spider_plant_commons_pd_condition_1024.png" 202605805 14 raw
      ;;
    frond)
      run_root 5 new_fern_fronds_ccby2 "$IMGROOT/new_fern_fronds_ccby2_condition_1024.png" 202605802 10 preprocess
      run_root 5 new_fern_fronds_ccby2 "$IMGROOT/new_fern_fronds_ccby2_condition_1024.png" 202605806 14 raw
      ;;
    fiddlehead)
      run_root 6 fiddlehead_golden_spiral_ccby4 "$IMGROOT/fiddlehead_golden_spiral_ccby4_condition_1024.png" 202605803 10 preprocess
      run_root 6 fiddlehead_golden_spiral_ccby4 "$IMGROOT/fiddlehead_golden_spiral_ccby4_condition_1024.png" 202605807 14 raw
      ;;
    koru)
      run_root 7 koru_unfurling_ccby25 "$IMGROOT/koru_unfurling_ccby25_condition_1024.png" 202605804 10 preprocess
      run_root 7 koru_unfurling_ccby25 "$IMGROOT/koru_unfurling_ccby25_condition_1024.png" 202605808 14 raw
      ;;
    *)
      echo "unknown lane $lane" >&2
      return 2
      ;;
  esac
}

run_preprocess_retry_lane() {
  local lane="$1"
  case "$lane" in
    spider)
      run_root 4 spider_plant_commons_pd "$IMGROOT/spider_plant_commons_pd_condition_1024.png" 202605801 10 preprocess
      ;;
    frond)
      run_root 5 new_fern_fronds_ccby2 "$IMGROOT/new_fern_fronds_ccby2_condition_1024.png" 202605802 10 preprocess
      ;;
    fiddlehead)
      run_root 6 fiddlehead_golden_spiral_ccby4 "$IMGROOT/fiddlehead_golden_spiral_ccby4_condition_1024.png" 202605803 10 preprocess
      ;;
    koru)
      run_root 7 koru_unfurling_ccby25 "$IMGROOT/koru_unfurling_ccby25_condition_1024.png" 202605804 10 preprocess
      ;;
    *)
      echo "unknown preprocess retry lane $lane" >&2
      return 2
      ;;
  esac
}

write_manifest() {
  cat > "$OUT/fern_root_image_generation_manifest_20260511c.tsv" <<TSV
label	gpu	source_image	seed	steps	preprocess	source/license	intended_role
spider_plant_commons_pd_steps10_seed202605801_preprocess	4	$IMGROOT/spider_plant_commons_pd_condition_1024.png	202605801	10	preprocess	Wikimedia Commons public domain	spider plant / rosette root candidate
spider_plant_commons_pd_steps14_seed202605805_raw	4	$IMGROOT/spider_plant_commons_pd_condition_1024.png	202605805	14	raw	Wikimedia Commons public domain	spider plant / rosette root candidate
new_fern_fronds_ccby2_steps10_seed202605802_preprocess	5	$IMGROOT/new_fern_fronds_ccby2_condition_1024.png	202605802	10	preprocess	Wikimedia Commons CC BY 2.0	compound fern frond root candidate
new_fern_fronds_ccby2_steps14_seed202605806_raw	5	$IMGROOT/new_fern_fronds_ccby2_condition_1024.png	202605806	14	raw	Wikimedia Commons CC BY 2.0	compound fern frond root candidate
fiddlehead_golden_spiral_ccby4_steps10_seed202605803_preprocess	6	$IMGROOT/fiddlehead_golden_spiral_ccby4_condition_1024.png	202605803	10	preprocess	Wikimedia Commons CC BY 4.0	fiddlehead spiral root candidate
fiddlehead_golden_spiral_ccby4_steps14_seed202605807_raw	6	$IMGROOT/fiddlehead_golden_spiral_ccby4_condition_1024.png	202605807	14	raw	Wikimedia Commons CC BY 4.0	fiddlehead spiral root candidate
koru_unfurling_ccby25_steps10_seed202605804_preprocess	7	$IMGROOT/koru_unfurling_ccby25_condition_1024.png	202605804	10	preprocess	Wikimedia Commons CC BY 2.5	unfurling fern / spiral root candidate
koru_unfurling_ccby25_steps14_seed202605808_raw	7	$IMGROOT/koru_unfurling_ccby25_condition_1024.png	202605808	14	raw	Wikimedia Commons CC BY 2.5	unfurling fern / spiral root candidate
TSV
}

metrics_all() {
  local case_args=()
  while IFS= read -r mesh; do
    label="$(basename "$(dirname "$mesh")")"
    case_args+=(--case "$label=$mesh")
  done < <(find "$OUT/image_roots" -name trellis2_dinov3_min.obj -type f | sort)
  if [[ ${#case_args[@]} -eq 0 ]]; then
    echo "NO_ROOTS_FOR_METRICS"
    return 0
  fi
  "$PY" "$ROOT/assets/recursive_growth_mesh_metrics.py" \
    "${case_args[@]}" \
    --out-json "$OUT/metrics/fern_root_image_metrics_20260511c.json" \
    --out-csv "$OUT/metrics/fern_root_image_metrics_20260511c.csv" \
    --occupancy-resolution 64 \
    --primary-connectivity occupancy 2>&1 | tee "$LOG/metrics_all.log"
}

status_all() {
  echo "STATUS $(date -Is)"
  for pid_file in "$OUT"/pids/*.pid; do
    [[ -f "$pid_file" ]] || continue
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" 2>/dev/null; then
      echo "RUNNING $(basename "$pid_file" .pid) pid=$pid"
    else
      echo "DONE_OR_EXITED $(basename "$pid_file" .pid) pid=$pid"
    fi
  done
  find "$OUT/image_roots" -maxdepth 2 -name summary.json -print | sort | while read -r summary; do
    "$PY" - <<'PY' "$summary"
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text())
print(f"SUMMARY {p.parent.name} status={d.get('status','ok')} verts={d.get('vertices')} faces={d.get('faces')} tokens={d.get('shape_latent_tokens')} error={d.get('error')}")
PY
  done
  find "$OUT/image_roots" -name trellis2_dinov3_min.obj -type f | wc -l | awk '{print "ROOT_OBJ_COUNT "$1}'
  find "$OUT/image_roots" -name trellis2_dinov3_min_preview.png -type f | wc -l | awk '{print "PREVIEW_COUNT "$1}'
}

start_all() {
  write_manifest
  nohup bash "$ROOT/assets/run_fern_root_image_generation_remote_20260511c.sh" spider > "$LOG/lane_spider.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/spider.pid"
  nohup bash "$ROOT/assets/run_fern_root_image_generation_remote_20260511c.sh" frond > "$LOG/lane_frond.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/frond.pid"
  nohup bash "$ROOT/assets/run_fern_root_image_generation_remote_20260511c.sh" fiddlehead > "$LOG/lane_fiddlehead.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fiddlehead.pid"
  nohup bash "$ROOT/assets/run_fern_root_image_generation_remote_20260511c.sh" koru > "$LOG/lane_koru.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/koru.pid"
  echo "STARTED $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

start_preprocess_retry() {
  write_manifest
  nohup bash "$ROOT/assets/run_fern_root_image_generation_remote_20260511c.sh" preprocess-spider > "$LOG/lane_preprocess_spider.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/preprocess_spider.pid"
  nohup bash "$ROOT/assets/run_fern_root_image_generation_remote_20260511c.sh" preprocess-frond > "$LOG/lane_preprocess_frond.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/preprocess_frond.pid"
  nohup bash "$ROOT/assets/run_fern_root_image_generation_remote_20260511c.sh" preprocess-fiddlehead > "$LOG/lane_preprocess_fiddlehead.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/preprocess_fiddlehead.pid"
  nohup bash "$ROOT/assets/run_fern_root_image_generation_remote_20260511c.sh" preprocess-koru > "$LOG/lane_preprocess_koru.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/preprocess_koru.pid"
  echo "STARTED_PREPROCESS_RETRY $(date -Is) pids=$(cat "$OUT"/pids/preprocess_*.pid | tr '\n' ' ')"
}

case "${1:-start}" in
  start) start_all ;;
  preprocess-retry) start_preprocess_retry ;;
  preprocess-spider) run_preprocess_retry_lane spider ;;
  preprocess-frond) run_preprocess_retry_lane frond ;;
  preprocess-fiddlehead) run_preprocess_retry_lane fiddlehead ;;
  preprocess-koru) run_preprocess_retry_lane koru ;;
  spider|frond|fiddlehead|koru) run_lane "$1" ;;
  metrics) metrics_all ;;
  status) status_all ;;
  *) echo "usage: $0 {start|preprocess-retry|status|metrics|spider|frond|fiddlehead|koru}" >&2; exit 2 ;;
esac
