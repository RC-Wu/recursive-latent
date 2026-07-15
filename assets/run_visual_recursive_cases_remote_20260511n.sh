#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/visual_recursive_cases_remote_20260511n"
LOG="$OUT/logs"
LOWPOLY="$ROOT/results/visual_recursive_lowpoly_roots_20260511l/selected_roots"
INPUTS_J="$ROOT/results/visual_recursive_cases_remote_20260511j/inputs/selected_roots"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511n" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/visual_recursive_cases_remote_20260511n"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511n"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

CROWN_POLY="$INPUTS_J/poly_crown_91ea8a96.obj"
SCIFI_LOCAL="$INPUTS_J/local_scifi_module_clean_recursive_v1.obj"
TANK_POLY="$INPUTS_J/poly_tank_item0.obj"
CITY_BLOCK="$LOWPOLY/city_block_lowpoly_roof_anchor_v1.obj"
CITY_COURTYARD="$LOWPOLY/city_courtyard_tower_anchor_v1.obj"
CASTLE_GATE="$LOWPOLY/castle_gate_lowpoly_turret_anchor_v1.obj"
CASTLE_KEEP="$LOWPOLY/castle_keep_battlement_anchor_v1.obj"
MECH_SOCKET="$LOWPOLY/mech_socket_frame_lowpoly_v1.obj"

write_manifest() {
  cat > "$OUT/root_anchor_manifest_20260511n.tsv" <<TSV
case	family	root_mesh	root_source_type	growth_axis	growth_sign	fit_scale	depths	max_tokens	grammars	seed	root_anchor_semantics	semantic_growth_frame_reason	visual_goal	claim_gate
city_block_11n_whole_zpos	city	$CITY_BLOCK	synthetic_11l_lowpoly	z	1	0.54	1	12000	v25n_whole_root_stack v25n_whole_root_corner	202606101	whole city root copied as coherent smaller child module	mesh z+ is semantic up; 11n tests whole-root latent copy to avoid 11m facade-sheet artifacts	clean nested city block/child building with minimal thin sheets	visual QA plus token/bbox growth plus metrics
city_courtyard_11n_whole_zpos	city	$CITY_COURTYARD	synthetic_11l_lowpoly	z	1	0.52	1	14000	v25n_whole_root_stack v25n_whole_root_twin	202606102	whole courtyard root copied as one/two smaller rooftop modules	mesh z+ semantic up; complete-root stamp should preserve building coherence	clean courtyard city recursion candidate	visual QA plus token/bbox growth plus metrics
castle_gate_11n_whole_ypos	castle	$CASTLE_GATE	synthetic_11l_lowpoly	y	1	0.54	1	12000	v25n_whole_root_stack v25n_whole_root_corner	202606111	whole gate root copied as coherent child gate/turret	SLat y+ was the effective growth frame for gate in 11m; treated as diagnostic/effective frame	clean recursive gate/turret without thin spires	main castle gate candidate if render is clean
castle_gate_11n_whole_zpos	castle	$CASTLE_GATE	synthetic_11l_lowpoly	z	1	0.54	1	12000	v25n_whole_root_stack	202606112	whole gate root copied as semantic z+ child	mesh z+ semantic up; contrast against y+ effective frame	clean semantic-up recursive gate diagnostic	diagnostic unless visually stronger than y+
castle_keep_11n_whole_zpos	castle	$CASTLE_KEEP	synthetic_11l_lowpoly	z	1	0.52	1	16000	v25n_whole_root_stack v25n_whole_root_twin v25n_whole_root_corner	202606113	whole keep root copied as one/two smaller child keeps	mesh z+ semantic up; complete-root copy should avoid turret/crown sheet artifacts	clean recursive keep/castle candidate	visual QA plus token/bbox growth plus metrics
TSV
}

run_case() {
  local gpu="$1"
  local case_name="$2"
  local mesh="$3"
  local depths="$4"
  local fit="$5"
  local max_tokens="$6"
  local axis="$7"
  local sign="$8"
  local seed="$9"
  shift 9
  local grammars=("$@")
  local log="$LOG/${case_name}.log"
  if [[ ! -f "$mesh" ]]; then
    echo "MISSING_MESH $mesh" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/visual_recursive_cases_remote_20260511n/gpu${gpu}_${case_name}"
  mkdir -p "$TRITON_CACHE_DIR" "$OUT/raw/$case_name"
  echo "RUN_BEGIN $(date -Is) gpu=$gpu case=$case_name mesh=$mesh axis=$axis sign=$sign fit=$fit depths=$depths grammars=${grammars[*]}" | tee "$log"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_recursive_slat_grammar_workflow.py" \
    --mesh "$mesh" \
    --out "$OUT/raw/$case_name" \
    --case-name "$case_name" \
    --grammars "${grammars[@]}" \
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
  echo "RUN_END $(date -Is) case=$case_name status=$status" | tee -a "$log"
  return "$status"
}

lane_city_a() {
  run_case 4 city_block_11n_whole_zpos "$CITY_BLOCK" 1 0.54 12000 z 1 202606101 v25n_whole_root_stack v25n_whole_root_corner
}

lane_city_b() {
  run_case 5 city_courtyard_11n_whole_zpos "$CITY_COURTYARD" 1 0.52 14000 z 1 202606102 v25n_whole_root_stack v25n_whole_root_twin
}

lane_castle_a() {
  run_case 6 castle_gate_11n_whole_ypos "$CASTLE_GATE" 1 0.54 12000 y 1 202606111 v25n_whole_root_stack v25n_whole_root_corner
  run_case 6 castle_gate_11n_whole_zpos "$CASTLE_GATE" 1 0.54 12000 z 1 202606112 v25n_whole_root_stack
}

lane_castle_b() {
  run_case 7 castle_keep_11n_whole_zpos "$CASTLE_KEEP" 1 0.52 16000 z 1 202606113 v25n_whole_root_stack v25n_whole_root_twin v25n_whole_root_corner
}

metrics_all() {
  local log="$LOG/metrics_all.log"
  mapfile -t meshes < <(find "$OUT/raw" -path '*/depth_*/mesh.obj' -type f | sort)
  if [[ "${#meshes[@]}" -eq 0 ]]; then
    echo "NO_MESHES_FOR_METRICS" | tee "$log"
    return 0
  fi
  "$PY" "$ROOT/assets/recursive_growth_mesh_metrics.py" \
    "${meshes[@]}" \
    --out-json "$OUT/metrics/visual_recursive_metrics_20260511n.json" \
    --out-csv "$OUT/metrics/visual_recursive_metrics_20260511n.csv" \
    --occupancy-resolution 48 \
    --primary-connectivity occupancy 2>&1 | tee "$log"
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

start_all() {
  write_manifest
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511n.sh" city_a > "$LOG/lane_city_a.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/city_a.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511n.sh" city_b > "$LOG/lane_city_b.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/city_b.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511n.sh" castle_a > "$LOG/lane_castle_a.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/castle_a.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511n.sh" castle_b > "$LOG/lane_castle_b.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/castle_b.pid"
  echo "STARTED $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start}" in
  start) start_all ;;
  city_a) lane_city_a ;;
  city_b) lane_city_b ;;
  castle_a) lane_castle_a ;;
  castle_b) lane_castle_b ;;
  metrics) metrics_all ;;
  manifest) write_manifest ;;
  status) status_all ;;
  *)
    echo "usage: $0 {start|city_a|city_b|castle_a|castle_b|metrics|manifest|status}" >&2
    exit 2
    ;;
esac
