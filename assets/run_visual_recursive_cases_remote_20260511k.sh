#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/visual_recursive_cases_remote_20260511k"
LOG="$OUT/logs"
INPUTS_J="$ROOT/results/visual_recursive_cases_remote_20260511j/inputs/selected_roots"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511k" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/visual_recursive_cases_remote_20260511k"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511k"
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
CITY_POLY="$INPUTS_J/poly_city_b946d1a0.obj"
CITY_TOWER="$INPUTS_J/poly_city_9dbf2d34.obj"
CASTLE_GATE="$INPUTS_J/poly_castle_18456966.obj"
ARCH_LOCAL="$INPUTS_J/local_architectural_arch_portal_bridge_v1.obj"

write_manifest() {
  cat > "$OUT/root_anchor_manifest_20260511k.tsv" <<TSV
case	family	root_mesh	growth_axis	growth_sign	fit_scale	depths	max_tokens	grammars	seed	visual_goal	claim_gate
crown_poly_clean_ypos	crown	$CROWN_POLY	y	1	0.62	2	16000	v25k_crown_clean_gem v25j_crown_rim_gem	202605951	cleaner crown rim recursion with fewer side beads	candidate if cleaner than 11j
scifi_local_clean_ypos	mechanical	$SCIFI_LOCAL	y	1	0.52	2	18000	v25k_mecha_clean_fin socket_tight_attach	202605961	cleaner attached fins on scifi module	candidate if d1/d2 less noisy
tank_poly_clean_zpos	mechanical_tank	$TANK_POLY	z	1	0.70	1	16000	v25k_mecha_clean_fin	202605962	tank armor/module recursion at shallow depth	candidate if d1 reads clean
city_block_clean_ypos	city	$CITY_POLY	y	1	0.62	2	14000	v25k_city_clean_tower	202605971	clean nested roof towers without scale clone	candidate if top surface not shredded
city_tower_clean_ypos	city	$CITY_TOWER	y	1	0.58	1	14000	v25k_city_clean_tower	202605972	shallow clean tower nesting on tall city root	diagnostic if LCR remains low
castle_gate_clean_ypos	castle	$CASTLE_GATE	y	1	0.62	2	15000	v25k_castle_clean_turret	202605981	cleaner small turrets/battlements on castle gate	candidate if towers not hairy
arch_local_clean_ypos	castle_arch	$ARCH_LOCAL	y	1	0.52	2	16000	v25k_castle_clean_turret arch_keystone_attach	202605982	clean arch/castle proxy without side hair	architecture proxy only unless castle semantics improve
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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/visual_recursive_cases_remote_20260511k/gpu${gpu}_${case_name}"
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
  run_case 4 crown_poly_clean_ypos "$CROWN_POLY" 2 0.62 16000 y 1 202605951 v25k_crown_clean_gem v25j_crown_rim_gem
  run_case 4 scifi_local_clean_ypos "$SCIFI_LOCAL" 2 0.52 18000 y 1 202605961 v25k_mecha_clean_fin socket_tight_attach
}

lane_tank() {
  run_case 5 tank_poly_clean_zpos "$TANK_POLY" 1 0.70 16000 z 1 202605962 v25k_mecha_clean_fin
}

lane_city() {
  run_case 6 city_block_clean_ypos "$CITY_POLY" 2 0.62 14000 y 1 202605971 v25k_city_clean_tower
  run_case 6 city_tower_clean_ypos "$CITY_TOWER" 1 0.58 14000 y 1 202605972 v25k_city_clean_tower
}

lane_castle() {
  run_case 7 castle_gate_clean_ypos "$CASTLE_GATE" 2 0.62 15000 y 1 202605981 v25k_castle_clean_turret
  run_case 7 arch_local_clean_ypos "$ARCH_LOCAL" 2 0.52 16000 y 1 202605982 v25k_castle_clean_turret arch_keystone_attach
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
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511k.sh" crown_mech > "$LOG/lane_crown_mech.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/crown_mech.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511k.sh" tank > "$LOG/lane_tank.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/tank.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511k.sh" city > "$LOG/lane_city.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/city.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511k.sh" castle > "$LOG/lane_castle.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/castle.pid"
  echo "STARTED $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start}" in
  start) start_all ;;
  crown_mech) lane_crown_mech ;;
  tank) lane_tank ;;
  city) lane_city ;;
  castle) lane_castle ;;
  manifest) write_manifest ;;
  status) status_all ;;
  *)
    echo "usage: $0 {start|crown_mech|tank|city|castle|manifest|status}" >&2
    exit 2
    ;;
esac
