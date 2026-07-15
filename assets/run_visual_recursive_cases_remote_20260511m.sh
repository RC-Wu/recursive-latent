#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/visual_recursive_cases_remote_20260511m"
LOG="$OUT/logs"
LOWPOLY="$ROOT/results/visual_recursive_lowpoly_roots_20260511l/selected_roots"
INPUTS_J="$ROOT/results/visual_recursive_cases_remote_20260511j/inputs/selected_roots"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511m" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/visual_recursive_cases_remote_20260511m"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511m"
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
  cat > "$OUT/root_anchor_manifest_20260511m.tsv" <<TSV
case	family	root_mesh	root_source_type	growth_axis	growth_sign	fit_scale	depths	max_tokens	grammars	seed	root_anchor_semantics	semantic_growth_frame_reason	visual_goal	claim_gate
city_block_11m_macro_zpos	city	$CITY_BLOCK	synthetic_11l_lowpoly	z	1	0.56	3	18000	v25m_city_macro_stack v25m_city_stack_then_quadrants	202606001	central upper block/podium body and four roof quadrants	mesh z+ is semantic up; SLat z+ was too subtle in 11l but remains the primary semantic check	large nested city tower stack plus quadrant child towers	visual QA plus token/bbox growth plus metrics
city_block_11m_macro_ypos	city	$CITY_BLOCK	synthetic_11l_lowpoly	y	1	0.56	2	18000	v25m_city_macro_stack	202606002	central upper block/podium body	SLat y+ frame contrast because 11l y+ showed bbox movement when z+ collided	diagnose whether SLat y+ produces clearer macroscopic growth	diagnostic unless visually stronger than z+
city_courtyard_11m_quadrants_zpos	city	$CITY_COURTYARD	synthetic_11l_lowpoly	z	1	0.54	2	18000	v25m_city_quadrant_stamps v25m_city_stack_then_quadrants	202606003	central tower body stamped to courtyard roof quadrants	mesh z+ semantic up; quadrant stamps must show visible rooftop recursion	courtyard/tower city with obvious repeated child towers	visual QA plus token/bbox growth plus metrics
castle_gate_11m_macro_ypos	castle	$CASTLE_GATE	synthetic_11l_lowpoly	y	1	0.56	3	18000	v25m_castle_macro_turret_stack v25m_castle_turret_then_crown	202606011	turret bodies/caps and top battlement band	SLat y+ was the effective 11l frame for castle gate token/bbox growth; record as diagnostic/effective frame, not mesh semantic up	large recursive gate turrets plus battlement crown	main castle gate candidate if no detached modules
castle_gate_11m_macro_zpos	castle	$CASTLE_GATE	synthetic_11l_lowpoly	z	1	0.56	2	18000	v25m_castle_macro_turret_stack	202606012	turret bodies/caps	mesh z+ semantic up; included to test whether macro displacement fixes 11l z+ collision	semantic z+ castle gate contrast	diagnostic unless visually stronger than y+
castle_keep_11m_turret_zpos	castle	$CASTLE_KEEP	synthetic_11l_lowpoly	z	1	0.54	2	20000	v25m_castle_macro_turret_stack v25m_castle_turret_then_crown	202606013	four turret bodies/caps plus battlement strips	mesh z+ semantic up; 11l keep already had bbox growth, 11m makes it visually larger	recursive castle keep turrets and crown	visual QA plus token/bbox growth plus metrics
castle_keep_11m_battlement_zpos	castle	$CASTLE_KEEP	synthetic_11l_lowpoly	z	1	0.54	2	20000	v25m_castle_battlement_crown	202606014	top edge crenellation band excluding corner mass	mesh z+ semantic up; isolates battlement crown from turret-body operator	recursive battlement crown diagnostic	diagnostic/appendix unless cleaner than turret stack
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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/visual_recursive_cases_remote_20260511m/gpu${gpu}_${case_name}"
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
  run_case 4 city_block_11m_macro_zpos "$CITY_BLOCK" 3 0.56 18000 z 1 202606001 v25m_city_macro_stack v25m_city_stack_then_quadrants
}

lane_city_b() {
  run_case 5 city_block_11m_macro_ypos "$CITY_BLOCK" 2 0.56 18000 y 1 202606002 v25m_city_macro_stack
  run_case 5 city_courtyard_11m_quadrants_zpos "$CITY_COURTYARD" 2 0.54 18000 z 1 202606003 v25m_city_quadrant_stamps v25m_city_stack_then_quadrants
}

lane_castle_a() {
  run_case 6 castle_gate_11m_macro_ypos "$CASTLE_GATE" 3 0.56 18000 y 1 202606011 v25m_castle_macro_turret_stack v25m_castle_turret_then_crown
  run_case 6 castle_gate_11m_macro_zpos "$CASTLE_GATE" 2 0.56 18000 z 1 202606012 v25m_castle_macro_turret_stack
}

lane_castle_b() {
  run_case 7 castle_keep_11m_turret_zpos "$CASTLE_KEEP" 2 0.54 20000 z 1 202606013 v25m_castle_macro_turret_stack v25m_castle_turret_then_crown
  run_case 7 castle_keep_11m_battlement_zpos "$CASTLE_KEEP" 2 0.54 20000 z 1 202606014 v25m_castle_battlement_crown
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
    --out-json "$OUT/metrics/visual_recursive_metrics_20260511m.json" \
    --out-csv "$OUT/metrics/visual_recursive_metrics_20260511m.csv" \
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
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511m.sh" city_a > "$LOG/lane_city_a.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/city_a.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511m.sh" city_b > "$LOG/lane_city_b.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/city_b.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511m.sh" castle_a > "$LOG/lane_castle_a.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/castle_a.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511m.sh" castle_b > "$LOG/lane_castle_b.nohup.log" 2>&1 &
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
