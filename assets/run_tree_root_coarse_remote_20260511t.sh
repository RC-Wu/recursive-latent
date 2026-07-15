#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/tree_root_coarse_recursive_remote_20260511t"
LOG="$OUT/logs"
INPUT="$ROOT/results/tree_root_coarse_candidates_20260511r"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/tree_root_coarse_recursive_remote_20260511t" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/tree_root_coarse_recursive_remote_20260511t"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/tree_root_coarse_recursive_remote_20260511t"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

mesh_path() {
  local case_id="$1"
  printf '%s/%s/%s.obj' "$INPUT" "$case_id" "$case_id"
}

run_recurse() {
  local gpu="$1"
  local label="$2"
  local mesh="$3"
  local grammars="$4"
  local depths="$5"
  local axis="$6"
  local sign="$7"
  local fit="$8"
  local max_tokens="$9"
  local seed="${10}"
  local out_dir="$OUT/raw/$label"
  local log="$LOG/${label}.log"
  if [[ ! -f "$mesh" ]]; then
    echo "MISSING_MESH $mesh" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/tree_root_coarse_recursive_remote_20260511t/gpu${gpu}_${label}"
  mkdir -p "$TRITON_CACHE_DIR" "$out_dir"
  echo "RECURSE_BEGIN $(date -Is) gpu=$gpu label=$label mesh=$mesh grammars=$grammars depths=$depths axis=$axis sign=$sign fit=$fit max_tokens=$max_tokens seed=$seed" | tee "$log"
  # shellcheck disable=SC2086
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_recursive_slat_grammar_workflow.py" \
    --mesh "$mesh" \
    --out "$out_dir" \
    --case-name "$label" \
    --grammars $grammars \
    --depths "$depths" \
    --resolution 512 \
    --grid-resolution 512 \
    --fit-scale "$fit" \
    --max-tokens "$max_tokens" \
    --growth-axis "$axis" \
    --growth-sign "$sign" \
    --seed "$seed" \
    --compete-jitter 0.0 2>&1 | tee -a "$log"
  local status=${PIPESTATUS[0]}
  echo "RECURSE_END $(date -Is) label=$label status=$status" | tee -a "$log"
  return "$status"
}

lane_down_simple() {
  run_recurse 4 coarse_down_compact_a_d4_20260511t "$(mesh_path coarse_root_down_compact_a)" "v25t_root_supported_child_single v25t_root_supported_child_pair v25t_root_supported_child_micro" 4 y 1 0.66 24000 202608401 || true
  run_recurse 4 coarse_down_smooth_b_d4_20260511t "$(mesh_path coarse_root_down_smooth_b)" "v25t_root_supported_child_single v25t_root_supported_child_micro v25r_root_coarse_visible" 4 y 1 0.66 24000 202608402 || true
}

lane_down_structured() {
  run_recurse 5 coarse_down_thick_stub_c_d4_20260511t "$(mesh_path coarse_root_down_thick_stub_c)" "v25t_root_supported_child_single v25t_root_supported_child_pair v25t_root_supported_child_micro" 4 y 1 0.64 26000 202608411 || true
  run_recurse 5 coarse_down_swept_asym_d_d4_20260511t "$(mesh_path coarse_root_down_swept_asym_d)" "v25t_root_supported_child_single v25t_root_supported_child_micro v25r_root_coarse_visible" 4 y 1 0.64 26000 202608412 || true
}

lane_up_simple() {
  run_recurse 6 coarse_up_compact_e_d4_20260511t "$(mesh_path coarse_root_up_compact_e)" "v25t_root_supported_child_single v25t_root_supported_child_pair v25t_root_supported_child_micro" 4 y -1 0.66 24000 202608421 || true
  run_recurse 6 coarse_up_smooth_f_d4_20260511t "$(mesh_path coarse_root_up_smooth_f)" "v25t_root_supported_child_single v25t_root_supported_child_micro v25r_root_coarse_visible" 4 y -1 0.66 24000 202608422 || true
}

lane_up_structured() {
  run_recurse 7 coarse_up_thick_stub_g_d4_20260511t "$(mesh_path coarse_root_up_thick_stub_g)" "v25t_root_supported_child_single v25t_root_supported_child_pair v25t_root_supported_child_micro" 4 y -1 0.64 26000 202608431 || true
  run_recurse 7 coarse_up_swept_asym_h_d4_20260511t "$(mesh_path coarse_root_up_swept_asym_h)" "v25t_root_supported_child_single v25t_root_supported_child_micro v25r_root_coarse_visible" 4 y -1 0.64 26000 202608432 || true
}

write_manifest() {
  cat > "$OUT/tree_root_coarse_manifest_20260511t.tsv" <<TSV
label	gpu	mesh	grammars	depths	growth_axis	growth_sign	fit_scale	seed	claim_scope
coarse_down_compact_a_d4_20260511t	4	$(mesh_path coarse_root_down_compact_a)	v25t_root_supported_child_single v25t_root_supported_child_pair v25t_root_supported_child_micro	4	y	1	0.66	202608401	downward compact supported-child coarse first-split diagnostic
coarse_down_smooth_b_d4_20260511t	4	$(mesh_path coarse_root_down_smooth_b)	v25t_root_supported_child_single v25t_root_supported_child_micro v25r_root_coarse_visible	4	y	1	0.66	202608402	downward smooth supported-child coarse first-split diagnostic
coarse_down_thick_stub_c_d4_20260511t	5	$(mesh_path coarse_root_down_thick_stub_c)	v25t_root_supported_child_single v25t_root_supported_child_pair v25t_root_supported_child_micro	4	y	1	0.64	202608411	downward thick supported-child coarse branch candidate
coarse_down_swept_asym_d_d4_20260511t	5	$(mesh_path coarse_root_down_swept_asym_d)	v25t_root_supported_child_single v25t_root_supported_child_micro v25r_root_coarse_visible	4	y	1	0.64	202608412	downward swept asym supported-child coarse branch candidate
coarse_up_compact_e_d4_20260511t	6	$(mesh_path coarse_root_up_compact_e)	v25t_root_supported_child_single v25t_root_supported_child_pair v25t_root_supported_child_micro	4	y	-1	0.66	202608421	upward compact supported-child orientation diagnostic
coarse_up_smooth_f_d4_20260511t	6	$(mesh_path coarse_root_up_smooth_f)	v25t_root_supported_child_single v25t_root_supported_child_micro v25r_root_coarse_visible	4	y	-1	0.66	202608422	upward smooth supported-child orientation diagnostic
coarse_up_thick_stub_g_d4_20260511t	7	$(mesh_path coarse_root_up_thick_stub_g)	v25t_root_supported_child_single v25t_root_supported_child_pair v25t_root_supported_child_micro	4	y	-1	0.64	202608431	upward thick supported-child orientation diagnostic
coarse_up_swept_asym_h_d4_20260511t	7	$(mesh_path coarse_root_up_swept_asym_h)	v25t_root_supported_child_single v25t_root_supported_child_micro v25r_root_coarse_visible	4	y	-1	0.64	202608432	upward swept asym supported-child orientation diagnostic
TSV
}

metrics_all() {
  local case_args=()
  while IFS= read -r mesh; do
    rel="${mesh#$OUT/raw/}"
    label="${rel%/mesh.obj}"
    label="${label//\//__}"
    case_args+=(--case "$label=$mesh")
  done < <(find "$OUT/raw" -path '*/depth_*/mesh.obj' -type f | sort)
  if [[ ${#case_args[@]} -eq 0 ]]; then
    echo "NO_MESHES_FOR_METRICS"
    return 0
  fi
  "$PY" "$ROOT/assets/recursive_growth_mesh_metrics.py" \
    "${case_args[@]}" \
    --out-json "$OUT/metrics/tree_root_coarse_metrics_20260511t.json" \
    --out-csv "$OUT/metrics/tree_root_coarse_metrics_20260511t.csv" \
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
  find "$OUT/raw" -maxdepth 2 -name summary.json -print 2>/dev/null | sort | while read -r summary; do
    "$PY" - <<'PY' "$summary"
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
d = json.loads(p.read_text())
print(f"SUMMARY {p.parent.name} status={d.get('status','ok')} base_tokens={d.get('base_tokens')} growth={d.get('growth_axis')},{d.get('growth_sign')}")
for g, gd in d.get("grammars", {}).items():
    depths = gd.get("depths", [])
    if depths:
        last = depths[-1]
        print(f"  GRAMMAR {g} depth_count={len(depths)} last_depth={last.get('depth')} tokens={last.get('tokens')} verts={last.get('vertices')} faces={last.get('faces')} stop={gd.get('stop_reason','')}")
PY
  done
  find "$OUT/raw" -path '*/depth_*/preview.png' -type f | wc -l | awk '{print "PREVIEW_COUNT "$1}'
  find "$OUT/raw" -path '*/depth_*/mesh.obj' -type f | wc -l | awk '{print "OBJ_COUNT "$1}'
}

start_main4() {
  write_manifest
  nohup bash "$ROOT/assets/run_tree_root_coarse_remote_20260511t.sh" down_simple > "$LOG/lane_down_simple.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/down_simple.pid"
  nohup bash "$ROOT/assets/run_tree_root_coarse_remote_20260511t.sh" down_structured > "$LOG/lane_down_structured.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/down_structured.pid"
  nohup bash "$ROOT/assets/run_tree_root_coarse_remote_20260511t.sh" up_simple > "$LOG/lane_up_simple.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/up_simple.pid"
  nohup bash "$ROOT/assets/run_tree_root_coarse_remote_20260511t.sh" up_structured > "$LOG/lane_up_structured.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/up_structured.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  down_simple) lane_down_simple ;;
  down_structured) lane_down_structured ;;
  up_simple) lane_up_simple ;;
  up_structured) lane_up_structured ;;
  metrics) metrics_all ;;
  status) status_all ;;
  manifest) write_manifest ;;
  *) echo "Usage: $0 {start-main4|down_simple|down_structured|up_simple|up_structured|metrics|status|manifest}" >&2; exit 2 ;;
esac
