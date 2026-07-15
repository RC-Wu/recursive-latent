#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/fern_leaf_recursive_remote_20260511e"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/fern_leaf_recursive_remote_20260511e" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/fern_leaf_recursive_remote_20260511e"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/fern_leaf_recursive_remote_20260511e"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

SC_TAPERED="$ROOT/inputs/strict_visual_matched_cases_V25_root_sc_refine_20260510/V25_sc_tree_crown_tapered_B/V25_sc_tree_crown_tapered_B.obj"
SC_LEAFSHIELD="$ROOT/inputs/strict_visual_matched_cases_V25_root_sc_refine_20260510/V25_sc_tree_crown_leafshield_B/V25_sc_tree_crown_leafshield_B.obj"
ROOT_FAN="$ROOT/inputs/strict_visual_matched_cases_V25_root_sc_refine_20260510/V25_lsys_root_fan_dense_anchorD_stable/V25_lsys_root_fan_dense_anchorD_stable.obj"
ROOT_NETWORK="$ROOT/inputs/strict_visual_matched_cases_V24_priority_rerun_seed20260511_20260510/V24_sc_root_network_260_anchorA_seedA/V24_sc_root_network_260_anchorA_seedA.obj"
VINE_RUNNER="$ROOT/inputs/strict_visual_matched_cases_V22_botanical_smooth_20260510/V22_lsys_climbing_vine_d6_smooth_leaf_tendrils/V22_lsys_climbing_vine_d6_smooth_leaf_tendrils.obj"

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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/fern_leaf_recursive_remote_20260511e/gpu${gpu}_${label}"
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

write_manifest() {
  cat > "$OUT/fern_leaf_recursive_manifest_20260511e.tsv" <<TSV
label	gpu	mesh	grammars	depths	growth_axis	growth_sign	fit_scale	max_tokens	seed	claim_scope
v25sc_tapered_micro_ypos	5	$SC_TAPERED	v25e_crown_bud_micro v25e_crown_scatter_fork v25e_rim_leaflet_micro v25e_crown_tiplet_short	3	y	1	0.54	24000	202605821	V25 structural crown root; short local crown/leaflet bud repair sweep, no broad fan copies
v25sc_leafshield_micro_ypos	6	$SC_LEAFSHIELD	v25e_crown_bud_micro v25e_crown_scatter_fork v25e_rim_leaflet_micro v25e_crown_tiplet_short	3	y	1	0.54	26000	202605822	V25 visual leafshield crown root; same micro grammars for paper-safe crown candidate
v25_rootfan_micro_zneg	7	$ROOT_FAN	v25e_root_basal_micro v25e_root_rim_tiplet v25e_root_crown_micro	3	z	-1	0.56	24000	202605823	V25 root-fan/spider-rhizome fallback; basal/rim micro growth only
v24_rootnet_micro_zpos	4	$ROOT_NETWORK	v25e_rim_leaflet_micro v25e_root_crown_micro v25e_crown_bud_micro	2	z	1	0.54	24000	202605824	V24 root-network rhizome; short local buds, depth 2 gate because root is already dense
v22_vine_micro_ypos	6	$VINE_RUNNER	v25e_crown_bud_micro v25e_crown_tiplet_short v25e_rim_leaflet_micro	3	y	1	0.64	18000	202605825	light vine/runner fallback to test stable hanging plantlet semantics
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
    --out-json "$OUT/metrics/fern_leaf_recursive_metrics_20260511e.json" \
    --out-csv "$OUT/metrics/fern_leaf_recursive_metrics_20260511e.csv" \
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
p=Path(sys.argv[1]); d=json.loads(p.read_text())
print(f"SUMMARY {p.parent.name} status={d.get('status','ok')} base_tokens={d.get('base_tokens')} error={d.get('error')}")
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

start_micro4() {
  write_manifest
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511e.sh" tapered > "$LOG/lane_tapered.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/tapered.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511e.sh" leafshield > "$LOG/lane_leafshield.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/leafshield.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511e.sh" rootfan > "$LOG/lane_rootfan.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/rootfan.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511e.sh" rootnet > "$LOG/lane_rootnet.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/rootnet.pid"
  echo "STARTED_MICRO4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

start_vine() {
  write_manifest
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511e.sh" vine > "$LOG/lane_vine.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/vine.pid"
  echo "STARTED_VINE $(date -Is) pid=$(cat "$OUT/pids/vine.pid")"
}

case "${1:-start-micro4}" in
  start|start-micro4) start_micro4 ;;
  start-vine|vine-lane) start_vine ;;
  tapered) run_case 5 v25sc_tapered_micro_ypos "$SC_TAPERED" "v25e_crown_bud_micro v25e_crown_scatter_fork v25e_rim_leaflet_micro v25e_crown_tiplet_short" 3 y 1 0.54 24000 202605821 ;;
  leafshield) run_case 6 v25sc_leafshield_micro_ypos "$SC_LEAFSHIELD" "v25e_crown_bud_micro v25e_crown_scatter_fork v25e_rim_leaflet_micro v25e_crown_tiplet_short" 3 y 1 0.54 26000 202605822 ;;
  rootfan) run_case 7 v25_rootfan_micro_zneg "$ROOT_FAN" "v25e_root_basal_micro v25e_root_rim_tiplet v25e_root_crown_micro" 3 z -1 0.56 24000 202605823 ;;
  rootnet) run_case 4 v24_rootnet_micro_zpos "$ROOT_NETWORK" "v25e_rim_leaflet_micro v25e_root_crown_micro v25e_crown_bud_micro" 2 z 1 0.54 24000 202605824 ;;
  vine) run_case 6 v22_vine_micro_ypos "$VINE_RUNNER" "v25e_crown_bud_micro v25e_crown_tiplet_short v25e_rim_leaflet_micro" 3 y 1 0.64 18000 202605825 ;;
  metrics) metrics_all ;;
  status) status_all ;;
  *) echo "usage: $0 {start-micro4|start-vine|status|metrics|tapered|leafshield|rootfan|rootnet|vine}" >&2; exit 2 ;;
esac
