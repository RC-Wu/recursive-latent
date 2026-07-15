#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/fern_image_root_generation_remote_20260512k"
LOWCOND="$ROOT/downloads/botanical_guides_20260511j_low_complexity"
SRC1024="$ROOT/downloads/fern_spider_sources_20260511"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"
DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"

mkdir -p "$OUT/image_roots" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/fern_image_root_generation_remote_20260512k" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/fern_image_root_generation_remote_20260512k"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/fern_image_root_generation_remote_20260512k"
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
  local preprocess="$6"
  local label="${case_id}_steps${steps}_seed${seed}_${preprocess}"
  local target="$OUT/image_roots/$label"
  local log="$LOG/$label.log"
  if [[ ! -f "$image" ]]; then
    echo "MISSING_IMAGE $image" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/fern_image_root_generation_remote_20260512k/gpu${gpu}_${label}"
  mkdir -p "$target" "$TRITON_CACHE_DIR"
  echo "IMAGE_ROOT_BEGIN $(date -Is) gpu=$gpu case=$case_id image=$image seed=$seed steps=$steps preprocess=$preprocess" | tee "$log"
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
  echo "IMAGE_ROOT_END $(date -Is) label=$label status=$status" | tee -a "$log"
  return "$status"
}

run_lane() {
  case "$1" in
    fiddle_low)
      run_root 4 fiddlehead_single_curl_cc0 "$LOWCOND/fiddlehead_single_curl_cc0_condition_768.png" 202612501 6 preprocess || true
      run_root 4 fiddlehead_single_curl_cc0 "$LOWCOND/fiddlehead_single_curl_cc0_condition_768.png" 202612502 8 raw || true
      ;;
    fiddle_ref)
      run_root 5 golden_spiral_fiddlehead_ccby4 "$SRC1024/fiddlehead_golden_spiral_ccby4_condition_1024.png" 202612511 6 raw || true
      run_root 5 koru_unfurling_ccby25 "$SRC1024/koru_unfurling_ccby25_condition_1024.png" 202612512 6 raw || true
      ;;
    fiddle_low_gpu7)
      run_root 7 fiddlehead_single_curl_cc0 "$LOWCOND/fiddlehead_single_curl_cc0_condition_768.png" 202612541 6 preprocess || true
      run_root 7 golden_spiral_fiddlehead_ccby4 "$SRC1024/fiddlehead_golden_spiral_ccby4_condition_1024.png" 202612542 6 raw || true
      ;;
    fern_ref)
      run_root 6 new_fern_fronds_ccby2 "$SRC1024/new_fern_fronds_ccby2_condition_1024.png" 202612521 6 raw || true
      run_root 6 new_fern_fronds_ccby2 "$SRC1024/new_fern_fronds_ccby2_condition_1024.png" 202612522 8 preprocess || true
      ;;
    fern_low)
      run_root 7 fiddlehead_single_curl_edge_cc0 "$LOWCOND/fiddlehead_single_curl_cc0_edge_768.png" 202612531 6 raw || true
      run_root 7 spider_rosette_single_pd "$LOWCOND/spider_rosette_single_pd_condition_768.png" 202612532 6 raw || true
      ;;
    *) echo "unknown lane $1" >&2; return 2 ;;
  esac
}

write_manifest() {
  cat > "$OUT/fern_image_root_generation_manifest_20260512k.tsv" <<TSV
label	gpu	source_image	seed	steps	preprocess	intended_role	claim_scope
fiddlehead_single_curl_cc0_steps6_seed202612501_preprocess	4	$LOWCOND/fiddlehead_single_curl_cc0_condition_768.png	202612501	6	preprocess	fiddlehead root candidate	diagnostic root only until visual/metrics QA
fiddlehead_single_curl_cc0_steps8_seed202612502_raw	4	$LOWCOND/fiddlehead_single_curl_cc0_condition_768.png	202612502	8	raw	fiddlehead root candidate	diagnostic root only until visual/metrics QA
golden_spiral_fiddlehead_ccby4_steps6_seed202612511_raw	5	$SRC1024/fiddlehead_golden_spiral_ccby4_condition_1024.png	202612511	6	raw	log-spiral/fiddlehead root candidate	diagnostic root only until visual/metrics QA
koru_unfurling_ccby25_steps6_seed202612512_raw	5	$SRC1024/koru_unfurling_ccby25_condition_1024.png	202612512	6	raw	unfurling spiral root candidate	diagnostic root only until visual/metrics QA
new_fern_fronds_ccby2_steps6_seed202612521_raw	6	$SRC1024/new_fern_fronds_ccby2_condition_1024.png	202612521	6	raw	compound fern root candidate	diagnostic root only until visual/metrics QA
new_fern_fronds_ccby2_steps8_seed202612522_preprocess	6	$SRC1024/new_fern_fronds_ccby2_condition_1024.png	202612522	8	preprocess	compound fern root candidate	diagnostic root only until visual/metrics QA
fiddlehead_single_curl_edge_cc0_steps6_seed202612531_raw	7	$LOWCOND/fiddlehead_single_curl_cc0_edge_768.png	202612531	6	raw	simplified spiral edge root candidate	diagnostic root only until visual/metrics QA
spider_rosette_single_pd_steps6_seed202612532_raw	7	$LOWCOND/spider_rosette_single_pd_condition_768.png	202612532	6	sraw	plant rosette fallback root candidate	diagnostic root only until visual/metrics QA
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
    --out-json "$OUT/metrics/fern_image_root_metrics_20260512k.json" \
    --out-csv "$OUT/metrics/fern_image_root_metrics_20260512k.csv" \
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
  nohup bash "$ROOT/assets/run_fern_image_root_generation_remote_20260512k.sh" fiddle_low > "$LOG/lane_fiddle_low.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fiddle_low.pid"
  nohup bash "$ROOT/assets/run_fern_image_root_generation_remote_20260512k.sh" fiddle_ref > "$LOG/lane_fiddle_ref.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fiddle_ref.pid"
  nohup bash "$ROOT/assets/run_fern_image_root_generation_remote_20260512k.sh" fern_ref > "$LOG/lane_fern_ref.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fern_ref.pid"
  nohup bash "$ROOT/assets/run_fern_image_root_generation_remote_20260512k.sh" fern_low > "$LOG/lane_fern_low.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fern_low.pid"
  echo "STARTED_IMAGE_ROOTS $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start}" in
  start) start_all ;;
  fiddle_low|fiddle_ref|fiddle_low_gpu7|fern_ref|fern_low) run_lane "$1" ;;
  metrics) metrics_all ;;
  status) status_all ;;
  manifest) write_manifest ;;
  *) echo "usage: $0 {start|status|metrics|fiddle_low|fiddle_ref|fiddle_low_gpu7|fern_ref|fern_low}" >&2; exit 2 ;;
esac
