#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/plant_leaf_recursive_remote_20260511"
IN="$OUT/inputs"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$LOG" "$OUT/pids" "$OUT/raw" "$OUT/metrics" \
  "$ROOT/cache/local_tmp/plant_leaf_recursive_remote_20260511" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/plant_leaf_recursive_remote_20260511"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/plant_leaf_recursive_remote_20260511"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

GREEN="$IN/plant_leaf_green_cluster_root.obj"
BASEMID="$IN/plant_leaf_base_mid_cluster_root.obj"
FULL="$IN/plant_leaf_full_upright_root.obj"

audit_inputs() {
  echo "AUDIT $(date -Is)"
  for f in "$GREEN" "$BASEMID" "$FULL"; do
    if [[ -f "$f" ]]; then
      ls -lh "$f"
    else
      echo "MISSING $f"
    fi
  done
  "$PY" - <<'PY'
import os
from pathlib import Path
root=Path(os.environ.get('ROOT','/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507'))
print('root', root)
PY
}

run_case() {
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
    echo "MISSING $mesh" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/plant_leaf_recursive_remote_20260511/gpu${gpu}_${label}"
  mkdir -p "$TRITON_CACHE_DIR" "$out_dir"
  echo "RUN_BEGIN $(date -Is) gpu=$gpu label=$label mesh=$mesh grammars=$grammars depths=$depths axis=$axis sign=$sign fit=$fit max_tokens=$max_tokens seed=$seed" | tee "$log"
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
  echo "RUN_END $(date -Is) label=$label status=$status" | tee -a "$log"
  return "$status"
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
    --out-json "$OUT/metrics/plant_leaf_recursive_metrics_20260511.json" \
    --out-csv "$OUT/metrics/plant_leaf_recursive_metrics_20260511.csv" \
    --occupancy-resolution 64 \
    --primary-connectivity occupancy 2>&1 | tee "$LOG/metrics_all.log"
}

write_manifest() {
  cat > "$OUT/plant_leaf_recursive_manifest_20260511.tsv" <<TSV
label	gpu	mesh	grammars	depths	growth_axis	growth_sign	fit_scale	max_tokens	seed	claim_scope
leaf_green_basal_fan_zpos	4	$GREEN	leaf_basal_fan_attach leaf_basal_micro_attach	3	z	1	0.62	22000	202605701	primary_leaf_from_base_attempt
leaf_green_crown_micro_zpos	5	$GREEN	crown_bud_attach crown_micro_fork_attach	3	z	1	0.62	22000	202605702	comparison_tip_or_crown_growth
leaf_basemid_basal_fan_zpos	6	$BASEMID	leaf_basal_fan_attach leaf_basal_micro_attach	3	z	1	0.60	24000	202605703	base_to_leaf_emergence_attempt
leaf_basemid_fork_side_zpos	7	$BASEMID	fork_side_attach crown_micro_fork_attach	2	z	1	0.58	20000	202605704	higher_risk_branching_diagnostic
TSV
}

start_all() {
  write_manifest
  audit_inputs | tee "$LOG/audit_inputs.log"
  nohup bash "$ROOT/assets/run_plant_leaf_recursive_remote_20260511.sh" leaf_green_basal > "$LOG/lane_leaf_green_basal.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/leaf_green_basal.pid"
  nohup bash "$ROOT/assets/run_plant_leaf_recursive_remote_20260511.sh" leaf_green_crown > "$LOG/lane_leaf_green_crown.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/leaf_green_crown.pid"
  nohup bash "$ROOT/assets/run_plant_leaf_recursive_remote_20260511.sh" leaf_basemid_basal > "$LOG/lane_leaf_basemid_basal.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/leaf_basemid_basal.pid"
  nohup bash "$ROOT/assets/run_plant_leaf_recursive_remote_20260511.sh" leaf_basemid_fork > "$LOG/lane_leaf_basemid_fork.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/leaf_basemid_fork.pid"
  echo "STARTED $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

status_all() {
  echo "STATUS $(date -Is)"
  if [[ -d "$OUT/pids" ]]; then
    for pid_file in "$OUT"/pids/*.pid; do
      [[ -f "$pid_file" ]] || continue
      pid="$(cat "$pid_file")"
      if kill -0 "$pid" 2>/dev/null; then
        echo "RUNNING $(basename "$pid_file" .pid) pid=$pid"
      else
        echo "DONE_OR_EXITED $(basename "$pid_file" .pid) pid=$pid"
      fi
    done
  fi
  find "$OUT/raw" -maxdepth 2 -name summary.json -print 2>/dev/null | sort | while read -r summary; do
    "$PY" - <<'PY' "$summary"
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text())
status=d.get('status','ok') if 'error' not in d else d.get('status','failed')
base=d.get('base_tokens')
print(f"SUMMARY {p.parent.name} status={status} base_tokens={base} error={d.get('error')}")
for g, gd in d.get('grammars',{}).items():
    depths=gd.get('depths',[])
    if depths:
        last=depths[-1]
        print(f"  GRAMMAR {g} depths={len(depths)} last_depth={last.get('depth')} tokens={last.get('tokens')} verts={last.get('vertices')} faces={last.get('faces')} stop={gd.get('stop_reason','')}")
PY
  done
  find "$OUT/raw" -path '*/depth_*/preview.png' -type f | wc -l | awk '{print "PREVIEW_COUNT "$1}'
  find "$OUT/raw" -path '*/depth_*/mesh.obj' -type f | wc -l | awk '{print "OBJ_COUNT "$1}'
}

case "${1:-start}" in
  start) start_all ;;
  leaf_green_basal) run_case 4 leaf_green_basal_fan_zpos "$GREEN" "leaf_basal_fan_attach leaf_basal_micro_attach" 3 z 1 0.62 22000 202605701 ;;
  leaf_green_crown) run_case 5 leaf_green_crown_micro_zpos "$GREEN" "crown_bud_attach crown_micro_fork_attach" 3 z 1 0.62 22000 202605702 ;;
  leaf_basemid_basal) run_case 6 leaf_basemid_basal_fan_zpos "$BASEMID" "leaf_basal_fan_attach leaf_basal_micro_attach" 3 z 1 0.60 24000 202605703 ;;
  leaf_basemid_fork) run_case 7 leaf_basemid_fork_side_zpos "$BASEMID" "fork_side_attach crown_micro_fork_attach" 2 z 1 0.58 20000 202605704 ;;
  metrics) metrics_all ;;
  status) status_all ;;
  *) echo "usage: $0 {start|status|metrics|leaf_green_basal|leaf_green_crown|leaf_basemid_basal|leaf_basemid_fork}" >&2; exit 2 ;;
esac
