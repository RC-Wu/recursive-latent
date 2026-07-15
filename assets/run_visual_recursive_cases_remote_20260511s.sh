#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/visual_recursive_cases_remote_20260511s"
LOG="$OUT/logs"
ROOTS_O="$ROOT/results/visual_recursive_roots_20260511o/selected_roots"
ROOTS_L="$ROOT/results/visual_recursive_lowpoly_roots_20260511l/selected_roots"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511s" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/visual_recursive_cases_remote_20260511s"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511s"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

CITY_ARCOLOGY="$ROOTS_O/city_stepped_arcology_v1.obj"
CITY_COURTYARD="$ROOTS_L/city_courtyard_tower_anchor_v1.obj"
CASTLE_GATE="$ROOTS_O/castle_tower_gate_socket_v2.obj"
CASTLE_KEEP="$ROOTS_O/castle_keep_spire_socket_v2.obj"
MECH_FRAME="$ROOTS_L/mech_socket_frame_lowpoly_v1.obj"
MECHA_CRUCIFORM="$ROOTS_O/mecha_socket_cruciform_v2.obj"

write_manifest() {
  cat > "$OUT/root_anchor_manifest_20260511s.tsv" <<TSV
case	family	root_mesh	root_source_type	semantic_growth_frame	render_frame	growth_axis	growth_sign	fit_scale	depths	max_tokens	grammars	seed	root_anchor_semantics	visual_goal	claim_gate
city_arcology_11s_topbody_protrude	city	$CITY_ARCOLOGY	authored_fused_lowpoly_visual_root	input z+ maps to SLat y-; compact top-body child protrudes above roof band	presentation render uses rot_x_neg90_then_center_floor	y	-1	0.52	2	22000	v25s_city_topbody_protruding	202606701	upper body q0.56-q0.90 central mask plus support bridge	clear terrace/arcology tower-on-roof hierarchy without city_cluster side graft	remote OBJ plus metrics plus controlled render QA
city_courtyard_11s_topbody_protrude	city	$CITY_COURTYARD	synthetic_11l_lowpoly	input z+ maps to SLat y-; courtyard tower/body child protrudes above roof band	presentation render uses rot_x_neg90_then_center_floor	y	-1	0.54	2	22000	v25s_city_topbody_protruding	202606702	central tower body and courtyard roof support	clean fallback city tower recursion with obvious top child	remote OBJ plus metrics plus controlled render QA
castle_gate_11s_cap_pair_protrude	castle	$CASTLE_GATE	authored_fused_lowpoly_visual_root	input z+ maps to SLat y-; turret caps are lifted above cap anchors	presentation render uses rot_x_neg90_then_center_floor	y	-1	0.52	2	24000	v25s_castle_cap_pair_protruding	202606711	tower cap/corner mask with small radial drift	recursive castle gate cap/turret hierarchy without side blocks	remote OBJ plus metrics plus controlled render QA
castle_keep_11s_cap_pair_protrude	castle	$CASTLE_KEEP	authored_fused_lowpoly_visual_root	input z+ maps to SLat y-; keep/spire caps are lifted above cap anchors	presentation render uses rot_x_neg90_then_center_floor	y	-1	0.50	1	22000	v25s_castle_cap_pair_protruding	202606712	keep corner/spire cap mask	clean shallow castle backup if gate fragments	remote OBJ plus metrics plus controlled render QA
mech_frame_11s_socket_pods	mechanical	$MECH_FRAME	synthetic_11l_lowpoly	input z+ maps to SLat y-; side sockets grow lateral pods	presentation render uses rot_x_neg90_then_center_floor	y	-1	0.56	2	18000	v25l_mecha_socket_pods v25s_mecha_socket_pods_emphatic	202606721	side socket/frame handles	readable hard-surface repeated modules with minimal dust	remote OBJ plus metrics plus controlled render QA
mecha_cruciform_11s_socket_pods	mechanical	$MECHA_CRUCIFORM	authored_fused_lowpoly_visual_root	input z+ maps to SLat y-; cruciform side sockets grow pods	presentation render uses rot_x_neg90_then_center_floor	y	-1	0.56	2	18000	v25s_mecha_socket_pods_emphatic v25o_mecha_socket_cluster	202606722	left/right/front/back socket handles	mecha/mechanical breadth case with attached repeated pods	remote OBJ plus metrics plus controlled render QA
TSV
}

run_case() {
  local gpu="$1"
  local case_name="$2"
  local mesh="$3"
  local depths="$4"
  local fit="$5"
  local max_tokens="$6"
  local seed="$7"
  shift 7
  local grammars=("$@")
  local log="$LOG/${case_name}.log"
  if [[ ! -f "$mesh" ]]; then
    echo "MISSING_MESH $mesh" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/visual_recursive_cases_remote_20260511s/gpu${gpu}_${case_name}"
  mkdir -p "$TRITON_CACHE_DIR" "$OUT/raw/$case_name"
  echo "RUN_BEGIN $(date -Is) gpu=$gpu case=$case_name mesh=$mesh axis=y sign=-1 fit=$fit depths=$depths grammars=${grammars[*]}" | tee "$log"
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
    --growth-axis y \
    --growth-sign -1 \
    --seed "$seed" \
    --compete-jitter 0.0 2>&1 | tee -a "$log"
  local status=${PIPESTATUS[0]}
  echo "RUN_END $(date -Is) case=$case_name status=$status" | tee -a "$log"
  return "$status"
}

lane_city() {
  run_case 4 city_arcology_11s_topbody_protrude "$CITY_ARCOLOGY" 2 0.52 22000 202606701 v25s_city_topbody_protruding
  run_case 4 city_courtyard_11s_topbody_protrude "$CITY_COURTYARD" 2 0.54 22000 202606702 v25s_city_topbody_protruding
}

lane_castle() {
  run_case 5 castle_gate_11s_cap_pair_protrude "$CASTLE_GATE" 2 0.52 24000 202606711 v25s_castle_cap_pair_protruding
  run_case 5 castle_keep_11s_cap_pair_protrude "$CASTLE_KEEP" 1 0.50 22000 202606712 v25s_castle_cap_pair_protruding
}

lane_mechanical() {
  run_case 6 mech_frame_11s_socket_pods "$MECH_FRAME" 2 0.56 18000 202606721 v25l_mecha_socket_pods v25s_mecha_socket_pods_emphatic
  run_case 6 mecha_cruciform_11s_socket_pods "$MECHA_CRUCIFORM" 2 0.56 18000 202606722 v25s_mecha_socket_pods_emphatic v25o_mecha_socket_cluster
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
    --out-json "$OUT/metrics/visual_recursive_metrics_20260511s.json" \
    --out-csv "$OUT/metrics/visual_recursive_metrics_20260511s.csv" \
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
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511s.sh" city > "$LOG/lane_city.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/city.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511s.sh" castle > "$LOG/lane_castle.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/castle.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511s.sh" mechanical > "$LOG/lane_mechanical.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/mechanical.pid"
  echo "GPU7 intentionally left free for metrics/QA or one emergency fallback."
  echo "STARTED $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start}" in
  start) start_all ;;
  city) lane_city ;;
  castle) lane_castle ;;
  mechanical) lane_mechanical ;;
  metrics) metrics_all ;;
  manifest) write_manifest ;;
  status) status_all ;;
  *)
    echo "usage: $0 {start|city|castle|mechanical|metrics|manifest|status}" >&2
    exit 2
    ;;
esac
