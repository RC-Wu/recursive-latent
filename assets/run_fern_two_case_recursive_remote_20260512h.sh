#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/fern_two_case_recursive_remote_20260512h"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/roots" "$OUT/pids" "$OUT/metrics" "$OUT/blender_qa" "$LOG" \
  "$ROOT/cache/local_tmp/fern_two_case_recursive_remote_20260512h" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/fern_two_case_recursive_remote_20260512h"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/fern_two_case_recursive_remote_20260512h"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

prepare_roots() {
  "$PY" "$ROOT/assets/prepare_fern_showcase_roots_20260512g.py" \
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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/fern_two_case_recursive_remote_20260512h/gpu${gpu}_${label}"
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

lane_fiddlehead_log_open() {
  local root="$OUT/roots/fiddlehead_log_spiral_i/fiddlehead_log_spiral_i.obj"
  run_recurse 4 fiddlehead_log_spiral_i_d4_20260512h "$root" "v26h_fiddlehead_attached_surface_buds v26h_fiddlehead_attached_buds_then_micro v26e_fiddlehead_surface_microbuds" 4 y -1 0.64 30000 202610801 || true
}

lane_fiddlehead_log_dense() {
  local root="$OUT/roots/fiddlehead_log_dense_j/fiddlehead_log_dense_j.obj"
  run_recurse 5 fiddlehead_log_dense_j_d4_20260512h "$root" "v26h_fiddlehead_attached_surface_buds v26h_fiddlehead_attached_buds_then_micro v26f_fiddlehead_macro_surface_buds" 4 y -1 0.64 32000 202610802 || true
}

lane_fern_tiered() {
  local root="$OUT/roots/fern_tiered_frond_i/fern_tiered_frond_i.obj"
  run_recurse 6 fern_tiered_frond_i_d4_20260512h "$root" "v26h_fern_attached_pinnae v26h_fern_attached_pinnae_then_tiplets v26b_fern_branchlet_pinnae" 4 y -1 0.62 36000 202610803 || true
}

lane_fern_hierarchical() {
  local root="$OUT/roots/fern_hierarchical_frond_j/fern_hierarchical_frond_j.obj"
  run_recurse 7 fern_hierarchical_frond_j_d4_20260512h "$root" "v26h_fern_attached_pinnae v26h_fern_attached_pinnae_then_tiplets v26f_fern_macro_pinnae v26b_fern_branchlet_pinnae" 4 y -1 0.62 38000 202610804 || true
}

write_manifest() {
  cat > "$OUT/fern_two_case_manifest_20260512h.tsv" <<TSV
label	gpu	track	mesh	grammars	depths	axis	sign	fit	seed	claim_scope
fiddlehead_log_spiral_i_d4_20260512h	4	fiddlehead_logarithmic	root:fiddlehead_log_spiral_i	v26h_fiddlehead_attached_surface_buds v26h_fiddlehead_attached_buds_then_micro v26e_fiddlehead_surface_microbuds	4	y	-1	0.64	202610801	publication candidate only if log spiral, no rung band, and render QA pass
fiddlehead_log_dense_j_d4_20260512h	5	fiddlehead_logarithmic	root:fiddlehead_log_dense_j	v26h_fiddlehead_attached_surface_buds v26h_fiddlehead_attached_buds_then_micro v26f_fiddlehead_macro_surface_buds	4	y	-1	0.64	202610802	publication candidate only if log spiral, no underside bars, and render QA pass
fern_tiered_frond_i_d4_20260512h	6	compound_fern	root:fern_tiered_frond_i	v26h_fern_attached_pinnae v26h_fern_attached_pinnae_then_tiplets v26b_fern_branchlet_pinnae	4	y	-1	0.62	202610803	publication candidate only if clear recursive hierarchy and render QA pass
fern_hierarchical_frond_j_d4_20260512h	7	compound_fern	root:fern_hierarchical_frond_j	v26h_fern_attached_pinnae v26h_fern_attached_pinnae_then_tiplets v26f_fern_macro_pinnae v26b_fern_branchlet_pinnae	4	y	-1	0.62	202610804	publication candidate only if clear recursive hierarchy and render QA pass
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
    --out-json "$OUT/metrics/fern_two_case_metrics_20260512h.json" \
    --out-csv "$OUT/metrics/fern_two_case_metrics_20260512h.csv" \
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
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512h.sh" fiddlehead_log_open > "$LOG/lane_fiddlehead_log_open.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fiddlehead_log_open.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512h.sh" fiddlehead_log_dense > "$LOG/lane_fiddlehead_log_dense.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fiddlehead_log_dense.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512h.sh" fern_tiered > "$LOG/lane_fern_tiered.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fern_tiered.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512h.sh" fern_hierarchical > "$LOG/lane_fern_hierarchical.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fern_hierarchical.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  prepare_roots) prepare_roots ;;
  fiddlehead_log_open) lane_fiddlehead_log_open ;;
  fiddlehead_log_dense) lane_fiddlehead_log_dense ;;
  fern_tiered) lane_fern_tiered ;;
  fern_hierarchical) lane_fern_hierarchical ;;
  metrics) metrics_all ;;
  status) status_all ;;
  manifest) write_manifest ;;
  *) echo "usage: $0 {start|prepare_roots|status|metrics|fiddlehead_log_open|fiddlehead_log_dense|fern_tiered|fern_hierarchical}" >&2; exit 2 ;;
esac
