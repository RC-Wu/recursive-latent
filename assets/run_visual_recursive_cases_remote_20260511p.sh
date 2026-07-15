#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/visual_recursive_cases_remote_20260511p"
LOG="$OUT/logs"
ROOTS="$ROOT/results/visual_recursive_roots_20260511o/selected_roots"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511p" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/visual_recursive_cases_remote_20260511p"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511p"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

CITY_CLUSTER="$ROOTS/city_tower_cluster_socket_v2.obj"
CITY_ARCOLOGY="$ROOTS/city_stepped_arcology_v1.obj"
CASTLE_KEEP="$ROOTS/castle_keep_spire_socket_v2.obj"

write_manifest() {
  cat > "$OUT/root_anchor_manifest_20260511p.tsv" <<TSV
case	family	root_mesh	root_source_type	semantic_growth_frame	render_frame	growth_axis	growth_sign	fit_scale	depths	max_tokens	grammars	seed	root_anchor_semantics	visual_goal	claim_gate
city_cluster_11p_supported_child	city	$CITY_CLUSTER	authored_fused_lowpoly_visual_root	input z+ maps to SLat y-; 11p adds narrow roof support to 11o single child	presentation render uses rot_x_neg90_then_center_floor	y	-1	0.50	1	16000	v25p_rooftop_child_tight v25p_rooftop_child_readable	202606401	central roof tower and roof support mask	reduce top child gaps/fragments while keeping obvious city recursion	remote OBJ plus metrics plus controlled render QA
city_arcology_11p_supported_child	city	$CITY_ARCOLOGY	authored_fused_lowpoly_visual_root	input z+ maps to SLat y-; single child with roof support	presentation render uses rot_x_neg90_then_center_floor	y	-1	0.52	1	16000	v25p_rooftop_child_tight v25p_rooftop_child_readable	202606402	stepped roof terrace support	keep clean city arcology read while making child connection less hollow	remote OBJ plus metrics plus controlled render QA
castle_keep_11p_supported_child	castle	$CASTLE_KEEP	authored_fused_lowpoly_visual_root	input z+ maps to SLat y-; keep/spire child with roof support	presentation render uses rot_x_neg90_then_center_floor	y	-1	0.52	1	18000	v25p_rooftop_child_tight v25p_rooftop_child_readable	202606411	central keep roof plus narrow support mask	reduce castle child holes and top fragments	remote OBJ plus metrics plus controlled render QA
TSV
}

run_case() {
  local gpu="$1"; local case_name="$2"; local mesh="$3"; local depths="$4"; local fit="$5"; local max_tokens="$6"; local seed="$7"; shift 7
  local grammars=("$@")
  local log="$LOG/${case_name}.log"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/visual_recursive_cases_remote_20260511p/gpu${gpu}_${case_name}"
  mkdir -p "$TRITON_CACHE_DIR" "$OUT/raw/$case_name"
  echo "RUN_BEGIN $(date -Is) gpu=$gpu case=$case_name grammars=${grammars[*]}" | tee "$log"
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

lane_city_cluster() {
  run_case 4 city_cluster_11p_supported_child "$CITY_CLUSTER" 1 0.50 16000 202606401 v25p_rooftop_child_tight v25p_rooftop_child_readable
}

lane_city_arcology() {
  run_case 5 city_arcology_11p_supported_child "$CITY_ARCOLOGY" 1 0.52 16000 202606402 v25p_rooftop_child_tight v25p_rooftop_child_readable
}

lane_castle_keep() {
  run_case 6 castle_keep_11p_supported_child "$CASTLE_KEEP" 1 0.52 18000 202606411 v25p_rooftop_child_tight v25p_rooftop_child_readable
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
    --out-json "$OUT/metrics/visual_recursive_metrics_20260511p.json" \
    --out-csv "$OUT/metrics/visual_recursive_metrics_20260511p.csv" \
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
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511p.sh" city_cluster > "$LOG/lane_city_cluster.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/city_cluster.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511p.sh" city_arcology > "$LOG/lane_city_arcology.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/city_arcology.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511p.sh" castle_keep > "$LOG/lane_castle_keep.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/castle_keep.pid"
  echo "STARTED $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start}" in
  start) start_all ;;
  city_cluster) lane_city_cluster ;;
  city_arcology) lane_city_arcology ;;
  castle_keep) lane_castle_keep ;;
  metrics) metrics_all ;;
  manifest) write_manifest ;;
  status) status_all ;;
  *)
    echo "usage: $0 {start|city_cluster|city_arcology|castle_keep|metrics|manifest|status}" >&2
    exit 2
    ;;
esac
