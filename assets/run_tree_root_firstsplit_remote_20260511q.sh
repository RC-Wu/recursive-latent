#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/tree_root_firstsplit_recursive_remote_20260511q"
LOG="$OUT/logs"
INPUT="$ROOT/results/tree_root_firstsplit_candidates_20260511q"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/tree_root_firstsplit_recursive_remote_20260511q" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/tree_root_firstsplit_recursive_remote_20260511q"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/tree_root_firstsplit_recursive_remote_20260511q"
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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/tree_root_firstsplit_recursive_remote_20260511q/gpu${gpu}_${label}"
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

lane_down_compact() {
  run_recurse 4 firstsplit_down_compact_a_d4_20260511q "$(mesh_path first_split_root_down_compact_a)" "v25q_root_module_sidecar v25q_root_module_chain v25n_root_first_split_taper" 4 y 1 0.66 26000 202608101 || true
  run_recurse 4 firstsplit_down_smooth_b_d4_20260511q "$(mesh_path first_split_root_down_smooth_b)" "v25q_root_module_sidecar v25q_root_module_chain v25l_root_primary_branch" 4 y 1 0.66 26000 202608102 || true
}

lane_down_primary() {
  run_recurse 5 firstsplit_down_sidecar_c_d4_20260511q "$(mesh_path first_split_root_down_sidecar_c)" "v25q_root_module_sidecar v25q_root_module_chain v25q_root_module_dense_rootlets v25p_root_first_split_sidecar" 4 y 1 0.66 30000 202608111 || true
  run_recurse 5 firstsplit_down_deep_dense_d_d4_20260511q "$(mesh_path first_split_root_down_deep_dense_d)" "v25q_root_module_chain v25q_root_module_dense_rootlets v25p_root_first_split_then_rootlets" 4 y 1 0.64 32000 202608112 || true
}

lane_up_compact() {
  run_recurse 6 firstsplit_up_compact_e_d4_20260511q "$(mesh_path first_split_root_up_compact_e)" "v25q_root_module_sidecar v25q_root_module_chain v25n_root_first_split_taper" 4 y -1 0.66 26000 202608121 || true
  run_recurse 6 firstsplit_up_smooth_f_d4_20260511q "$(mesh_path first_split_root_up_smooth_f)" "v25q_root_module_sidecar v25q_root_module_chain v25l_root_primary_branch" 4 y -1 0.66 26000 202608122 || true
}

lane_up_primary() {
  run_recurse 7 firstsplit_up_sidecar_g_d4_20260511q "$(mesh_path first_split_root_up_sidecar_g)" "v25q_root_module_sidecar v25q_root_module_chain v25q_root_module_dense_rootlets v25p_root_first_split_sidecar" 4 y -1 0.66 30000 202608131 || true
  run_recurse 7 firstsplit_up_asym_deep_h_d4_20260511q "$(mesh_path first_split_root_up_asym_deep_h)" "v25q_root_module_chain v25q_root_module_dense_rootlets v25p_root_first_split_then_rootlets" 4 y -1 0.64 32000 202608132 || true
}

write_manifest() {
  cat > "$OUT/tree_root_firstsplit_manifest_20260511q.tsv" <<TSV
label	gpu	mesh	grammars	depths	growth_axis	growth_sign	fit_scale	seed	claim_scope
firstsplit_down_compact_a_d4_20260511q	4	$(mesh_path first_split_root_down_compact_a)	v25q_root_module_sidecar v25q_root_module_chain v25n_root_first_split_taper	4	y	1	0.66	202608101	compact downward first-split input sanity
firstsplit_down_smooth_b_d4_20260511q	4	$(mesh_path first_split_root_down_smooth_b)	v25q_root_module_sidecar v25q_root_module_chain v25l_root_primary_branch	4	y	1	0.66	202608102	smooth downward first-split input sanity
firstsplit_down_sidecar_c_d4_20260511q	5	$(mesh_path first_split_root_down_sidecar_c)	v25q_root_module_sidecar v25q_root_module_chain v25q_root_module_dense_rootlets v25p_root_first_split_sidecar	4	y	1	0.66	202608111	primary q downward root candidate
firstsplit_down_deep_dense_d_d4_20260511q	5	$(mesh_path first_split_root_down_deep_dense_d)	v25q_root_module_chain v25q_root_module_dense_rootlets v25p_root_first_split_then_rootlets	4	y	1	0.64	202608112	primary q downward dense-rootlet candidate
firstsplit_up_compact_e_d4_20260511q	6	$(mesh_path first_split_root_up_compact_e)	v25q_root_module_sidecar v25q_root_module_chain v25n_root_first_split_taper	4	y	-1	0.66	202608121	upward orientation stress
firstsplit_up_smooth_f_d4_20260511q	6	$(mesh_path first_split_root_up_smooth_f)	v25q_root_module_sidecar v25q_root_module_chain v25l_root_primary_branch	4	y	-1	0.66	202608122	upward orientation stress
firstsplit_up_sidecar_g_d4_20260511q	7	$(mesh_path first_split_root_up_sidecar_g)	v25q_root_module_sidecar v25q_root_module_chain v25q_root_module_dense_rootlets v25p_root_first_split_sidecar	4	y	-1	0.66	202608131	upward sidecar stress
firstsplit_up_asym_deep_h_d4_20260511q	7	$(mesh_path first_split_root_up_asym_deep_h)	v25q_root_module_chain v25q_root_module_dense_rootlets v25p_root_first_split_then_rootlets	4	y	-1	0.64	202608132	upward asym deep stress
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
    --out-json "$OUT/metrics/tree_root_firstsplit_metrics_20260511q.json" \
    --out-csv "$OUT/metrics/tree_root_firstsplit_metrics_20260511q.csv" \
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
  nohup bash "$ROOT/assets/run_tree_root_firstsplit_remote_20260511q.sh" down_compact > "$LOG/lane_down_compact.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/down_compact.pid"
  nohup bash "$ROOT/assets/run_tree_root_firstsplit_remote_20260511q.sh" down_primary > "$LOG/lane_down_primary.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/down_primary.pid"
  nohup bash "$ROOT/assets/run_tree_root_firstsplit_remote_20260511q.sh" up_compact > "$LOG/lane_up_compact.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/up_compact.pid"
  nohup bash "$ROOT/assets/run_tree_root_firstsplit_remote_20260511q.sh" up_primary > "$LOG/lane_up_primary.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/up_primary.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  down_compact) lane_down_compact ;;
  down_primary) lane_down_primary ;;
  up_compact) lane_up_compact ;;
  up_primary) lane_up_primary ;;
  metrics) metrics_all ;;
  status) status_all ;;
  manifest) write_manifest ;;
  *) echo "Usage: $0 {start-main4|down_compact|down_primary|up_compact|up_primary|metrics|status|manifest}" >&2; exit 2 ;;
esac
