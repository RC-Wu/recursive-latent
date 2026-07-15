#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/visual_recursive_cases_remote_20260511l"
LOG="$OUT/logs"
LOWPOLY="$ROOT/results/visual_recursive_lowpoly_roots_20260511l/selected_roots"
INPUTS_J="$ROOT/results/visual_recursive_cases_remote_20260511j/inputs/selected_roots"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511l" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/visual_recursive_cases_remote_20260511l"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511l"
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
  cat > "$OUT/root_anchor_manifest_20260511l.tsv" <<TSV
case	family	root_mesh	growth_axis	growth_sign	fit_scale	depths	max_tokens	grammars	seed	visual_goal	claim_gate
crown_poly_clean_ypos	crown	$CROWN_POLY	y	1	0.62	2	16000	v25k_crown_clean_gem	202605971	clean crown control; retain if 11k/11j crown remains best	visual QA plus metrics
scifi_local_socket_ypos	mechanical	$SCIFI_LOCAL	y	1	0.52	2	18000	v25j_mecha_socket_tight_fin v25k_mecha_clean_fin	202605972	scifi hard-surface control with clear repeated socket modules	visual QA plus metrics
mech_socket_lowpoly_ypos	mechanical	$MECH_SOCKET	y	1	0.56	2	16000	v25l_mecha_socket_pods v25k_mecha_clean_fin	202605973	low-complexity fused mechanical root with repeated socket pods	visual QA plus metrics
tank_poly_socket_zpos	mechanical_tank	$TANK_POLY	z	1	0.70	1	16000	v25k_mecha_clean_fin	202605974	shallow tank/mechanical breadth candidate	visual QA plus metrics
city_block_lowpoly_zpos	city	$CITY_BLOCK	z	1	0.58	3	15000	v25l_city_podium_then_corners v25l_city_roof_podium	202605981	nested city towers from fused block roof anchors	main city candidate if clean
city_block_lowpoly_ypos	city	$CITY_BLOCK	y	1	0.58	2	15000	v25l_city_podium_then_corners	202605982	growth-frame contrast for city block	diagnostic unless better than zpos
city_courtyard_lowpoly_zpos	city	$CITY_COURTYARD	z	1	0.56	2	15000	v25l_city_roof_corners v25l_city_roof_podium	202605983	courtyard/tower city recursion with explicit corner anchors	candidate if clean
castle_gate_lowpoly_zpos	castle	$CASTLE_GATE	z	1	0.58	3	15000	v25l_castle_turret_then_battlement v25l_castle_turret_caps	202605991	recursive battlements/turrets on fused castle gate	main castle candidate if clean
castle_gate_lowpoly_ypos	castle	$CASTLE_GATE	y	1	0.58	2	15000	v25l_castle_turret_then_battlement	202605992	growth-frame contrast for castle gate	diagnostic unless better than zpos
castle_keep_lowpoly_zpos	castle	$CASTLE_KEEP	z	1	0.56	2	15000	v25l_castle_turret_caps v25l_castle_battlement_strip	202605993	recursive keep towers/battlements from fused keep root	candidate if clean
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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/visual_recursive_cases_remote_20260511l/gpu${gpu}_${case_name}"
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

lane_crown_mech() {
  run_case 4 crown_poly_clean_ypos "$CROWN_POLY" 2 0.62 16000 y 1 202605971 v25k_crown_clean_gem
  run_case 4 scifi_local_socket_ypos "$SCIFI_LOCAL" 2 0.52 18000 y 1 202605972 v25j_mecha_socket_tight_fin v25k_mecha_clean_fin
  run_case 4 mech_socket_lowpoly_ypos "$MECH_SOCKET" 2 0.56 16000 y 1 202605973 v25l_mecha_socket_pods v25k_mecha_clean_fin
  run_case 4 tank_poly_socket_zpos "$TANK_POLY" 1 0.70 16000 z 1 202605974 v25k_mecha_clean_fin
}

lane_city() {
  run_case 5 city_block_lowpoly_zpos "$CITY_BLOCK" 3 0.58 15000 z 1 202605981 v25l_city_podium_then_corners v25l_city_roof_podium
  run_case 5 city_block_lowpoly_ypos "$CITY_BLOCK" 2 0.58 15000 y 1 202605982 v25l_city_podium_then_corners
  run_case 5 city_courtyard_lowpoly_zpos "$CITY_COURTYARD" 2 0.56 15000 z 1 202605983 v25l_city_roof_corners v25l_city_roof_podium
}

lane_castle() {
  run_case 6 castle_gate_lowpoly_zpos "$CASTLE_GATE" 3 0.58 15000 z 1 202605991 v25l_castle_turret_then_battlement v25l_castle_turret_caps
  run_case 6 castle_gate_lowpoly_ypos "$CASTLE_GATE" 2 0.58 15000 y 1 202605992 v25l_castle_turret_then_battlement
  run_case 6 castle_keep_lowpoly_zpos "$CASTLE_KEEP" 2 0.56 15000 z 1 202605993 v25l_castle_turret_caps v25l_castle_battlement_strip
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
    --out-json "$OUT/metrics/visual_recursive_metrics_20260511l.json" \
    --out-csv "$OUT/metrics/visual_recursive_metrics_20260511l.csv" \
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
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511l.sh" crown_mech > "$LOG/lane_crown_mech.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/crown_mech.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511l.sh" city > "$LOG/lane_city.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/city.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511l.sh" castle > "$LOG/lane_castle.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/castle.pid"
  echo "STARTED $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start}" in
  start) start_all ;;
  crown_mech) lane_crown_mech ;;
  city) lane_city ;;
  castle) lane_castle ;;
  metrics) metrics_all ;;
  manifest) write_manifest ;;
  status) status_all ;;
  *)
    echo "usage: $0 {start|crown_mech|city|castle|metrics|manifest|status}" >&2
    exit 2
    ;;
esac
