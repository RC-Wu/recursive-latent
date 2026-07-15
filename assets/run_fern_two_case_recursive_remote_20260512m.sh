#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/fern_two_case_recursive_remote_20260512m"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/roots" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/fern_two_case_recursive_remote_20260512m" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/fern_two_case_recursive_remote_20260512m"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/fern_two_case_recursive_remote_20260512m"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

prepare_roots() {
  "$PY" "$ROOT/assets/prepare_fern_depth_roots_20260512m.py" \
    --out "$OUT/roots" \
    --depths 0 2 4 2>&1 | tee "$LOG/prepare_roots.log"
}

run_naturalize() {
  local gpu="$1"
  local case_id="$2"
  local depth="$3"
  local fit="$4"
  local seed="$5"
  local mesh="$OUT/roots/$case_id/depth_$(printf '%02d' "$depth")/${case_id}_depth_$(printf '%02d' "$depth").obj"
  local label="${case_id}_depth_$(printf '%02d' "$depth")_naturalized_20260512m"
  local out_dir="$OUT/raw/$label"
  local log="$LOG/${label}.log"
  if [[ ! -f "$mesh" ]]; then
    echo "MISSING_MESH $mesh" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/fern_two_case_recursive_remote_20260512m/gpu${gpu}_${label}"
  mkdir -p "$TRITON_CACHE_DIR" "$out_dir"
  echo "NATURALIZE_BEGIN $(date -Is) gpu=$gpu label=$label mesh=$mesh fit=$fit seed=$seed" | tee "$log"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_recursive_slat_grammar_workflow.py" \
    --mesh "$mesh" \
    --out "$out_dir" \
    --case-name "$label" \
    --grammars v26j_passthrough \
    --depths 0 \
    --resolution 512 \
    --grid-resolution 512 \
    --fit-scale "$fit" \
    --max-tokens 50000 \
    --growth-axis y \
    --growth-sign -1 \
    --restore-output-frame \
    --seed "$seed" \
    --compete-jitter 0.0 2>&1 | tee -a "$log"
  local status=${PIPESTATUS[0]}
  echo "NATURALIZE_END $(date -Is) label=$label status=$status" | tee -a "$log"
  return "$status"
}

run_lane() {
  local gpu="$1"
  shift
  local seed_base="$1"
  shift
  local n=0
  for spec in "$@"; do
    IFS=: read -r case_id depth fit <<<"$spec"
    run_naturalize "$gpu" "$case_id" "$depth" "$fit" "$((seed_base + n))" || true
    n=$((n + 1))
  done
}

write_manifest() {
  cat > "$OUT/fern_two_case_manifest_20260512m.tsv" <<TSV
label	gpu	track	mesh	grammar	depths	fit	seed	claim_scope
fiddlehead_log_organic_crozier_o_depth_00_naturalized_20260512m	4	fiddlehead_logarithmic	mesh-stage-depth-root:v26j_passthrough	depth_00	0	0.64	202614101	publication candidate only if SLat naturalization preserves log spiral and clean connected handles
fiddlehead_log_organic_crozier_o_depth_02_naturalized_20260512m	4	fiddlehead_logarithmic	mesh-stage-depth-root:v26j_passthrough	depth_02	0	0.64	202614102	publication candidate only if SLat naturalization preserves log spiral and clean connected handles
fiddlehead_log_organic_crozier_o_depth_04_naturalized_20260512m	4	fiddlehead_logarithmic	mesh-stage-depth-root:v26j_passthrough	depth_04	0	0.64	202614103	publication candidate only if SLat naturalization preserves log spiral and clean connected handles
fiddlehead_log_organic_crozier_p_depth_00_naturalized_20260512m	5	fiddlehead_logarithmic	mesh-stage-depth-root:v26j_passthrough	depth_00	0	0.64	202614201	publication candidate only if SLat naturalization preserves log spiral and clean connected handles
fiddlehead_log_organic_crozier_p_depth_02_naturalized_20260512m	5	fiddlehead_logarithmic	mesh-stage-depth-root:v26j_passthrough	depth_02	0	0.64	202614202	publication candidate only if SLat naturalization preserves log spiral and clean connected handles
fiddlehead_log_organic_crozier_p_depth_04_naturalized_20260512m	5	fiddlehead_logarithmic	mesh-stage-depth-root:v26j_passthrough	depth_04	0	0.64	202614203	publication candidate only if SLat naturalization preserves log spiral and clean connected handles
fern_mesh_frond_k_depth_00_naturalized_20260512m	6	compound_fern	mesh-stage-depth-root:v26j_passthrough	depth_00	0	0.62	202614301	publication candidate only if clear hierarchy and no detached fragments
fern_mesh_frond_k_depth_02_naturalized_20260512m	6	compound_fern	mesh-stage-depth-root:v26j_passthrough	depth_02	0	0.62	202614302	publication candidate only if clear hierarchy and no detached fragments
fern_mesh_frond_k_depth_04_naturalized_20260512m	6	compound_fern	mesh-stage-depth-root:v26j_passthrough	depth_04	0	0.62	202614303	publication candidate only if clear hierarchy and no detached fragments
fern_mesh_frond_l_depth_00_naturalized_20260512m	7	compound_fern	mesh-stage-depth-root:v26j_passthrough	depth_00	0	0.62	202614401	publication candidate only if clear hierarchy and no detached fragments
fern_mesh_frond_l_depth_02_naturalized_20260512m	7	compound_fern	mesh-stage-depth-root:v26j_passthrough	depth_02	0	0.62	202614402	publication candidate only if clear hierarchy and no detached fragments
fern_mesh_frond_l_depth_04_naturalized_20260512m	7	compound_fern	mesh-stage-depth-root:v26j_passthrough	depth_04	0	0.62	202614403	publication candidate only if clear hierarchy and no detached fragments
TSV
}

metrics_all() {
  local case_args=()
  while IFS= read -r mesh; do
    local rel="${mesh#$OUT/raw/}"
    local label="${rel%/mesh.obj}"
    label="${label//\//__}"
    case_args+=(--case "$label=$mesh")
  done < <(find "$OUT/raw" -path '*/depth_00/mesh.obj' -type f | sort)
  if [[ ${#case_args[@]} -eq 0 ]]; then
    echo "NO_MESHES_FOR_METRICS"
    return 0
  fi
  "$PY" "$ROOT/assets/recursive_growth_mesh_metrics.py" \
    "${case_args[@]}" \
    --out-json "$OUT/metrics/fern_two_case_metrics_20260512m.json" \
    --out-csv "$OUT/metrics/fern_two_case_metrics_20260512m.csv" \
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
  find "$OUT/raw" -maxdepth 2 -name summary.json -print 2>/dev/null | sort | while read -r summary; do
    "$PY" - <<'PY' "$summary"
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
d = json.loads(p.read_text())
print(f"SUMMARY {p.parent.name} status={d.get('status','ok')} base_tokens={d.get('base_tokens')}")
for g, gd in d.get("grammars", {}).items():
    depths = gd.get("depths", [])
    if depths:
        last = depths[-1]
        print(f"  GRAMMAR {g} depth_count={len(depths)} last_depth={last.get('depth')} tokens={last.get('tokens')} verts={last.get('vertices')} faces={last.get('faces')} stop={gd.get('stop_reason','')}")
PY
  done
  find "$OUT/raw" -path '*/depth_00/preview.png' -type f | wc -l | awk '{print "PREVIEW_COUNT "$1}'
  find "$OUT/raw" -path '*/depth_00/mesh.obj' -type f | wc -l | awk '{print "OBJ_COUNT "$1}'
}

start_main4() {
  write_manifest
  prepare_roots
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512m.sh" lane4 > "$LOG/lane4.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/lane4.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512m.sh" lane5 > "$LOG/lane5.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/lane5.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512m.sh" lane6 > "$LOG/lane6.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/lane6.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512m.sh" lane7 > "$LOG/lane7.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/lane7.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  prepare_roots) prepare_roots ;;
  lane4) run_lane 4 202614101 fiddlehead_log_organic_crozier_o:0:0.64 fiddlehead_log_organic_crozier_o:2:0.64 fiddlehead_log_organic_crozier_o:4:0.64 ;;
  lane5) run_lane 5 202614201 fiddlehead_log_organic_crozier_p:0:0.64 fiddlehead_log_organic_crozier_p:2:0.64 fiddlehead_log_organic_crozier_p:4:0.64 ;;
  lane6) run_lane 6 202614301 fern_mesh_frond_k:0:0.62 fern_mesh_frond_k:2:0.62 fern_mesh_frond_k:4:0.62 ;;
  lane7) run_lane 7 202614401 fern_mesh_frond_l:0:0.62 fern_mesh_frond_l:2:0.62 fern_mesh_frond_l:4:0.62 ;;
  metrics) metrics_all ;;
  status) status_all ;;
  manifest) write_manifest ;;
  *) echo "usage: $0 {start|prepare_roots|status|metrics|lane4|lane5|lane6|lane7}" >&2; exit 2 ;;
esac
