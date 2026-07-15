#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/visual_recursive_cases_remote_20260511u"
LOG="$OUT/logs"
ROOTS_U="$ROOT/results/visual_recursive_solid_roots_20260511u/selected_roots"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511u" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/visual_recursive_cases_remote_20260511u"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/visual_recursive_cases_remote_20260511u"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

CITY_PODIUM="$ROOTS_U/city_solid_podium_v1.obj"
CITY_KEEP="$ROOTS_U/city_solid_keep_v1.obj"
CASTLE_KEEP="$ROOTS_U/castle_solid_keep_v1.obj"
CASTLE_GATE="$ROOTS_U/castle_solid_gate_v1.obj"

write_manifest() {
  cat > "$OUT/root_anchor_manifest_20260511u.tsv" <<TSV
case	family	root_mesh	root_source_type	preencode_root_transform	semantic_growth_frame	render_frame	growth_axis	growth_sign	fit_scale	depths	max_tokens	grammars	seed	root_anchor_semantics	visual_goal	claim_gate
city_solid_podium_11u	city	$CITY_PODIUM	authored_low_frequency_fused_solid_root	rot_x_neg90 before fixed mesh-to-SLat conversion	original z+ becomes SLat z+ after preencode transform	identity and rot_x_neg90 both audited	z	1	0.54	2	18000	v25u_solid_rooftop_child_clean v25u_solid_rooftop_child_large	202606901	central solid upper body and broad support platform	clean recursive city podium with no shell gaps	remote OBJ plus metrics plus controlled render QA
city_solid_keep_11u	city	$CITY_KEEP	authored_low_frequency_fused_solid_root	rot_x_neg90 before fixed mesh-to-SLat conversion	original z+ becomes SLat z+ after preencode transform	identity and rot_x_neg90 both audited	z	1	0.54	2	18000	v25u_solid_rooftop_child_clean v25u_solid_rooftop_child_large	202606902	square roof terrace and central solid tower	clean recursive city/keep tower with visible top child	remote OBJ plus metrics plus controlled render QA
castle_solid_keep_11u	castle	$CASTLE_KEEP	authored_low_frequency_fused_solid_root	rot_x_neg90 before fixed mesh-to-SLat conversion	original z+ becomes SLat z+ after preencode transform	identity and rot_x_neg90 both audited	z	1	0.52	2	18000	v25u_solid_rooftop_child_clean v25u_solid_rooftop_child_large	202606911	central keep body, not corner cap detail	nested castle keep recursion without shredded caps	remote OBJ plus metrics plus controlled render QA
castle_solid_gate_11u	castle	$CASTLE_GATE	authored_low_frequency_fused_solid_root	rot_x_neg90 before fixed mesh-to-SLat conversion	original z+ becomes SLat z+ after preencode transform	identity and rot_x_neg90 both audited	z	1	0.52	2	18000	v25u_solid_rooftop_child_clean v25u_solid_rooftop_child_large	202606912	solid twin-tower/gate body and central support	fallback gate/tower recursion with fewer cap holes	remote OBJ plus metrics plus controlled render QA
TSV
}

run_case() {
  local gpu="$1"
  local case_name="$2"
  local mesh="$3"
  local fit="$4"
  local seed="$5"
  local log="$LOG/${case_name}.log"
  if [[ ! -f "$mesh" ]]; then
    echo "MISSING_MESH $mesh" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/visual_recursive_cases_remote_20260511u/gpu${gpu}_${case_name}"
  mkdir -p "$TRITON_CACHE_DIR" "$OUT/raw/$case_name"
  echo "RUN_BEGIN $(date -Is) gpu=$gpu case=$case_name mesh=$mesh preencode=rot_x_neg90 axis=z sign=1 fit=$fit" | tee "$log"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_recursive_slat_grammar_workflow.py" \
    --mesh "$mesh" \
    --out "$OUT/raw/$case_name" \
    --case-name "$case_name" \
    --grammars v25u_solid_rooftop_child_clean v25u_solid_rooftop_child_large \
    --depths 2 \
    --resolution 512 \
    --grid-resolution 512 \
    --fit-scale "$fit" \
    --max-tokens 18000 \
    --preencode-transform rot_x_neg90 \
    --growth-axis z \
    --growth-sign 1 \
    --seed "$seed" \
    --compete-jitter 0.0 2>&1 | tee -a "$log"
  local status=${PIPESTATUS[0]}
  echo "RUN_END $(date -Is) case=$case_name status=$status" | tee -a "$log"
  return "$status"
}

lane_city_a() { run_case 4 city_solid_podium_11u "$CITY_PODIUM" 0.54 202606901; }
lane_city_b() { run_case 5 city_solid_keep_11u "$CITY_KEEP" 0.54 202606902; }
lane_castle_a() { run_case 6 castle_solid_keep_11u "$CASTLE_KEEP" 0.52 202606911; }
lane_castle_b() { run_case 7 castle_solid_gate_11u "$CASTLE_GATE" 0.52 202606912; }

metrics_all() {
  local log="$LOG/metrics_all.log"
  mapfile -t meshes < <(find "$OUT/raw" -path '*/depth_*/mesh.obj' -type f | sort)
  if [[ "${#meshes[@]}" -eq 0 ]]; then
    echo "NO_MESHES_FOR_METRICS" | tee "$log"
    return 0
  fi
  "$PY" "$ROOT/assets/recursive_growth_mesh_metrics.py" \
    "${meshes[@]}" \
    --out-json "$OUT/metrics/visual_recursive_metrics_20260511u.json" \
    --out-csv "$OUT/metrics/visual_recursive_metrics_20260511u.csv" \
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
print(f"SUMMARY {p.parent.name} status={d.get('status','ok')} preencode={d.get('preencode_transform')} axis={d.get('growth_axis')} sign={d.get('growth_sign')} base_tokens={d.get('base_tokens')} error={d.get('error')}")
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
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511u.sh" city_a > "$LOG/lane_city_a.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/city_a.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511u.sh" city_b > "$LOG/lane_city_b.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/city_b.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511u.sh" castle_a > "$LOG/lane_castle_a.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/castle_a.pid"
  nohup bash "$ROOT/assets/run_visual_recursive_cases_remote_20260511u.sh" castle_b > "$LOG/lane_castle_b.nohup.log" 2>&1 &
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
