#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/visual_recursive_cases_remote_20260511r"
LOG="$OUT/logs"
ROOTS="$ROOT/results/visual_recursive_roots_20260511o/selected_roots"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511r" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/visual_recursive_cases_remote_20260511r"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511r"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

CITY_CLUSTER="$ROOTS/city_tower_cluster_socket_v2.obj"

write_manifest() {
  cat > "$OUT/root_anchor_manifest_20260511r.tsv" <<TSV
case	family	root_mesh	root_source_type	semantic_growth_frame	render_frame	growth_axis	growth_sign	fit_scale	depths	max_tokens	grammars	seed	root_anchor_semantics	visual_goal	claim_gate
city_cluster_11r_protruding_stack	city	$CITY_CLUSTER	authored_fused_lowpoly_visual_root	input z+ maps to SLat y-; 11r explicitly protrudes child above roof band	presentation render uses rot_x_neg90_then_center_floor	y	-1	0.46	2	22000	v25r_city_rooftop_stack_protruding	202606601	roof q0.92 plus positive protrusion and broad support bridge	obvious tower-on-tower hierarchy that grows outside the roof/facade mass	remote OBJ plus metrics plus controlled render QA
TSV
}

run_case() {
  local gpu="$1"; local case_name="$2"; local mesh="$3"; local depths="$4"; local fit="$5"; local max_tokens="$6"; local seed="$7"; local grammar="$8"
  local log="$LOG/${case_name}.log"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/visual_recursive_cases_remote_20260511r/gpu${gpu}_${case_name}"
  mkdir -p "$TRITON_CACHE_DIR" "$OUT/raw/$case_name"
  echo "RUN_BEGIN $(date -Is) gpu=$gpu case=$case_name grammar=$grammar" | tee "$log"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_recursive_slat_grammar_workflow.py" \
    --mesh "$mesh" \
    --out "$OUT/raw/$case_name" \
    --case-name "$case_name" \
    --grammars "$grammar" \
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
  run_case 4 city_cluster_11r_protruding_stack "$CITY_CLUSTER" 2 0.46 22000 202606601 v25r_city_rooftop_stack_protruding
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
    --out-json "$OUT/metrics/visual_recursive_metrics_20260511r.json" \
    --out-csv "$OUT/metrics/visual_recursive_metrics_20260511r.csv" \
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
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511r.sh" city_cluster > "$LOG/lane_city_cluster.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/city_cluster.pid"
  echo "STARTED $(date -Is) pid=$(cat "$OUT/pids/city_cluster.pid")"
}

case "${1:-start}" in
  start) start_all ;;
  city_cluster) lane_city_cluster ;;
  metrics) metrics_all ;;
  manifest) write_manifest ;;
  status) status_all ;;
  *)
    echo "usage: $0 {start|city_cluster|metrics|manifest|status}" >&2
    exit 2
    ;;
esac
