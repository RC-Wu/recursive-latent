#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/visual_recursive_cases_remote_20260511j"
LOG="$OUT/logs"
INPUTS="$OUT/inputs/selected_roots"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" "$INPUTS" \
  "$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511j" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/visual_recursive_cases_remote_20260511j"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511j"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

CROWN_LOCAL="$INPUTS/local_crown_ornament_attached_portal_v1.obj"
CROWN_POLY="$INPUTS/poly_crown_91ea8a96.obj"
CROWN_POLY_ALT="$INPUTS/poly_crown_e8294c9f.obj"
SCIFI_LOCAL="$INPUTS/local_scifi_module_clean_recursive_v1.obj"
TANK_POLY="$INPUTS/poly_tank_item0.obj"
MECHA_POLY="$INPUTS/poly_mecha_40d7525e.obj"
CITY_POLY="$INPUTS/poly_city_9dbf2d34.obj"
CITY_POLY_BLOCK="$INPUTS/poly_city_b946d1a0.obj"
CASTLE_POLY="$INPUTS/poly_castle_18456966.obj"
CASTLE_POLY_RING="$INPUTS/poly_castle_094ac090.obj"
ARCH_LOCAL="$INPUTS/local_architectural_arch_portal_bridge_v1.obj"

write_manifest() {
  cat > "$OUT/root_anchor_manifest_20260511j.tsv" <<TSV
case	family	root_mesh	growth_axis	growth_sign	fit_scale	depths	max_tokens	grammars	seed	visual_goal	claim_gate
crown_local_rim_ypos	crown	$CROWN_LOCAL	y	1	0.50	2	22000	v25j_crown_rim_gem v25j_crown_rim_gem_bud ornament_rim_micro_attach	202605911	rim gems/spikes on clean authored crown root	visual-first candidate; needs render QA
crown_poly_ring_ypos	crown	$CROWN_POLY	y	1	0.62	3	18000	v25j_crown_rim_gem v25j_crown_rim_gem_bud	202605912	recursive beads/spikes on external crown ring	visual-first candidate; external Poly Pizza root
crown_poly_object_ypos	crown	$CROWN_POLY_ALT	y	1	0.62	2	16000	v25j_crown_rim_gem	202605913	check alternate crown/ornament root only	diagnostic unless semantics read as crown
scifi_local_socket_ypos	mechanical	$SCIFI_LOCAL	y	1	0.52	2	22000	v25j_mecha_socket_tight_fin v25j_mecha_socket_fin socket_tight_attach	202605921	repeated attached hard-surface fins/modules on clean scifi root	visual-first candidate; not tank proof
tank_poly_socket_zpos	mechanical_tank	$TANK_POLY	z	1	0.70	2	18000	v25j_mecha_socket_fin v25j_mecha_socket_tight_fin	202605922	repeated attached armor/modules on external tank root	visual-first candidate; external Poly Pizza CC0 tank
mecha_poly_socket_ypos	mecha	$MECHA_POLY	y	1	0.48	1	22000	v25j_mecha_socket_fin	202605923	large mecha source smoke only, depth 1	diagnostic unless token/render quality is good
city_poly_rooftop_ypos	city	$CITY_POLY	y	1	0.58	2	18000	v25j_city_rooftop_tower v25j_city_nested_scale	202605931	nested rooftop towers on external city block	visual-first candidate; external Poly Pizza city/building
city_poly_block_ypos	city	$CITY_POLY_BLOCK	y	1	0.62	3	16000	v25j_city_rooftop_tower v25j_city_nested_scale	202605932	nested towers on simple city-block root	visual-first candidate; external Poly Pizza city/building
castle_poly_gate_ypos	castle	$CASTLE_POLY	y	1	0.62	3	18000	v25j_castle_turret v25j_castle_turret_keystone	202605941	turrets/battlements on compact castle gate	visual-first candidate; external Poly Pizza castle
castle_local_arch_ypos	castle_arch	$ARCH_LOCAL	y	1	0.52	2	20000	v25j_castle_turret v25j_castle_turret_keystone arch_keystone_attach	202605942	turret/battlement repair on clean arch proxy	architecture/castle proxy
castle_poly_ring_ypos	castle	$CASTLE_POLY_RING	y	1	0.52	1	20000	v25j_castle_turret	202605943	large castle root smoke only	diagnostic unless clean
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

  export TRITON_CACHE_DIR="$ROOT/cache/triton/visual_recursive_cases_remote_20260511j/gpu${gpu}_${case_name}"
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

lane_crown() {
  run_case 4 crown_local_rim_ypos "$CROWN_LOCAL" 2 0.50 22000 y 1 202605911 v25j_crown_rim_gem v25j_crown_rim_gem_bud ornament_rim_micro_attach
  run_case 4 crown_poly_ring_ypos "$CROWN_POLY" 3 0.62 18000 y 1 202605912 v25j_crown_rim_gem v25j_crown_rim_gem_bud
  run_case 4 crown_poly_object_ypos "$CROWN_POLY_ALT" 2 0.62 16000 y 1 202605913 v25j_crown_rim_gem
}

lane_mech() {
  run_case 5 scifi_local_socket_ypos "$SCIFI_LOCAL" 2 0.52 22000 y 1 202605921 v25j_mecha_socket_tight_fin v25j_mecha_socket_fin socket_tight_attach
  run_case 5 tank_poly_socket_zpos "$TANK_POLY" 2 0.70 18000 z 1 202605922 v25j_mecha_socket_fin v25j_mecha_socket_tight_fin
  run_case 5 mecha_poly_socket_ypos "$MECHA_POLY" 1 0.48 22000 y 1 202605923 v25j_mecha_socket_fin
}

lane_city() {
  run_case 6 city_poly_rooftop_ypos "$CITY_POLY" 2 0.58 18000 y 1 202605931 v25j_city_rooftop_tower v25j_city_nested_scale
  run_case 6 city_poly_block_ypos "$CITY_POLY_BLOCK" 3 0.62 16000 y 1 202605932 v25j_city_rooftop_tower v25j_city_nested_scale
}

lane_castle() {
  run_case 7 castle_poly_gate_ypos "$CASTLE_POLY" 3 0.62 18000 y 1 202605941 v25j_castle_turret v25j_castle_turret_keystone
  run_case 7 castle_local_arch_ypos "$ARCH_LOCAL" 2 0.52 20000 y 1 202605942 v25j_castle_turret v25j_castle_turret_keystone arch_keystone_attach
  run_case 7 castle_poly_ring_ypos "$CASTLE_POLY_RING" 1 0.52 20000 y 1 202605943 v25j_castle_turret
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
    --out-json "$OUT/metrics/visual_recursive_metrics_20260511j.json" \
    --out-csv "$OUT/metrics/visual_recursive_metrics_20260511j.csv" \
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

start_all() {
  write_manifest
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511j.sh" crown > "$LOG/lane_crown.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/crown.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511j.sh" mech > "$LOG/lane_mech.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/mech.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511j.sh" city > "$LOG/lane_city.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/city.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511j.sh" castle > "$LOG/lane_castle.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/castle.pid"
  echo "STARTED $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start}" in
  start) start_all ;;
  crown) lane_crown ;;
  mech) lane_mech ;;
  city) lane_city ;;
  castle) lane_castle ;;
  metrics) metrics_all ;;
  manifest) write_manifest ;;
  status) status_all ;;
  *)
    echo "usage: $0 {start|crown|mech|city|castle|metrics|manifest|status}" >&2
    exit 2
    ;;
esac
