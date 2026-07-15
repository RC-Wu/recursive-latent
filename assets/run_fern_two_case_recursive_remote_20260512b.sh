#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/fern_two_case_recursive_remote_20260512b"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/roots" "$OUT/pids" "$OUT/metrics" "$OUT/blender_qa" "$LOG" \
  "$ROOT/cache/local_tmp/fern_two_case_recursive_remote_20260512b" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/fern_two_case_recursive_remote_20260512b"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/fern_two_case_recursive_remote_20260512b"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

prepare_roots() {
  "$PY" "$ROOT/assets/prepare_fern_showcase_roots_20260512b.py" \
    --out "$OUT/roots" \
    --seed 20260512 2>&1 | tee "$LOG/prepare_roots.log"
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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/fern_two_case_recursive_remote_20260512b/gpu${gpu}_${label}"
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

lane_fiddlehead_macro() {
  local root="$OUT/roots/fiddlehead_macro_crozier_c/fiddlehead_macro_crozier_c.obj"
  run_recurse 4 fiddlehead_macro_crozier_c_d3_20260512b "$root" "v26b_fiddlehead_macro_curl v26b_fiddlehead_macro_then_buds v26b_fiddlehead_scale_buds v26a_fiddlehead_visible_curl" 3 y -1 0.60 34000 202609101 || true
}

lane_fiddlehead_hook() {
  local root="$OUT/roots/fiddlehead_hook_crozier_d/fiddlehead_hook_crozier_d.obj"
  run_recurse 5 fiddlehead_hook_crozier_d_d3_20260512b "$root" "v26b_fiddlehead_macro_curl v26b_fiddlehead_macro_then_buds v26b_fiddlehead_scale_buds v26a_fiddlehead_nested_curl" 3 y -1 0.60 32000 202609201 || true
}

lane_fern_broad() {
  local root="$OUT/roots/fern_broad_frond_c/fern_broad_frond_c.obj"
  run_recurse 6 fern_broad_frond_c_d4_20260512b "$root" "v26b_fern_broad_pinnae v26b_fern_branchlet_pinnae v26b_fern_broad_then_branchlet v26a_fern_showcase_dense_pinnae" 4 y -1 0.60 42000 202609301 || true
}

lane_fern_branching() {
  local root="$OUT/roots/fern_branching_frond_d/fern_branching_frond_d.obj"
  run_recurse 7 fern_branching_frond_d_d4_20260512b "$root" "v26b_fern_broad_pinnae v26b_fern_branchlet_pinnae v26b_fern_broad_then_branchlet v26a_fern_showcase_pinnae" 4 y -1 0.60 42000 202609401 || true
}

write_manifest() {
  cat > "$OUT/fern_two_case_manifest_20260512b.tsv" <<TSV
label	gpu	track	mesh	grammars	depths	axis	sign	fit	seed	claim_scope
fiddlehead_macro_crozier_c_d3_20260512b	4	fiddlehead	root:fiddlehead_macro_crozier_c	v26b_fiddlehead_macro_curl v26b_fiddlehead_macro_then_buds v26b_fiddlehead_scale_buds v26a_fiddlehead_visible_curl	3	y	-1	0.60	202609101	publication candidate if render QA passes
fiddlehead_hook_crozier_d_d3_20260512b	5	fiddlehead	root:fiddlehead_hook_crozier_d	v26b_fiddlehead_macro_curl v26b_fiddlehead_macro_then_buds v26b_fiddlehead_scale_buds v26a_fiddlehead_nested_curl	3	y	-1	0.60	202609201	publication candidate if render QA passes
fern_broad_frond_c_d4_20260512b	6	compound_fern	root:fern_broad_frond_c	v26b_fern_broad_pinnae v26b_fern_branchlet_pinnae v26b_fern_broad_then_branchlet v26a_fern_showcase_dense_pinnae	4	y	-1	0.60	202609301	publication candidate if render QA passes
fern_branching_frond_d_d4_20260512b	7	compound_fern	root:fern_branching_frond_d	v26b_fern_broad_pinnae v26b_fern_branchlet_pinnae v26b_fern_broad_then_branchlet v26a_fern_showcase_pinnae	4	y	-1	0.60	202609401	publication candidate if render QA passes
TSV
}

metrics_all() {
  local case_args=()
  while IFS= read -r mesh; do
    local rel="${mesh#$OUT/raw/}"
    local label="${rel%/mesh.obj}"
    label="${label//\//__}"
    case_args+=(--case "$label=$mesh")
  done < <(find "$OUT/raw" -path '*/depth_*/mesh.obj' -type f | sort)
  if [[ ${#case_args[@]} -eq 0 ]]; then
    echo "NO_MESHES_FOR_METRICS"
    return 0
  fi
  "$PY" "$ROOT/assets/recursive_growth_mesh_metrics.py" \
    "${case_args[@]}" \
    --out-json "$OUT/metrics/fern_two_case_metrics_20260512b.json" \
    --out-csv "$OUT/metrics/fern_two_case_metrics_20260512b.csv" \
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
  find "$OUT/raw" -path '*/depth_*/preview.png' -type f | wc -l | awk '{print "PREVIEW_COUNT "$1}'
  find "$OUT/raw" -path '*/depth_*/mesh.obj' -type f | wc -l | awk '{print "OBJ_COUNT "$1}'
}

start_main4() {
  write_manifest
  prepare_roots
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512b.sh" fiddlehead_macro > "$LOG/lane_fiddlehead_macro.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fiddlehead_macro.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512b.sh" fiddlehead_hook > "$LOG/lane_fiddlehead_hook.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fiddlehead_hook.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512b.sh" fern_broad > "$LOG/lane_fern_broad.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fern_broad.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512b.sh" fern_branching > "$LOG/lane_fern_branching.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fern_branching.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  prepare_roots) prepare_roots ;;
  fiddlehead_macro) lane_fiddlehead_macro ;;
  fiddlehead_hook) lane_fiddlehead_hook ;;
  fern_broad) lane_fern_broad ;;
  fern_branching) lane_fern_branching ;;
  metrics) metrics_all ;;
  status) status_all ;;
  manifest) write_manifest ;;
  *) echo "Usage: $0 {start-main4|prepare_roots|fiddlehead_macro|fiddlehead_hook|fern_broad|fern_branching|metrics|status|manifest}" >&2; exit 2 ;;
esac
