#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/fern_leaf_recursive_remote_20260511g"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/fern_leaf_recursive_remote_20260511g" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/fern_leaf_recursive_remote_20260511g"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/fern_leaf_recursive_remote_20260511g"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

BROAD="$ROOT/results/fern_root_candidates_20260511g/spider_rosette_broadleaf_b/spider_rosette_broadleaf_b.obj"
RUNNER="$ROOT/results/fern_root_candidates_20260511g/spider_rosette_runner_plantlets_c/spider_rosette_runner_plantlets_c.obj"
OLD="$ROOT/results/fern_root_candidates_20260511g/spider_rosette_strapleaf_a/spider_rosette_strapleaf_a.obj"

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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/fern_leaf_recursive_remote_20260511g/gpu${gpu}_${label}"
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
  cat > "$OUT/fern_leaf_recursive_manifest_20260511g.tsv" <<TSV
label	gpu	mesh	grammars	depths	growth_axis	growth_sign	fit_scale	max_tokens	seed	claim_scope
spider_broad_zpos	4	$BROAD	v25g_root_crown_conservative v25g_root_plantlet_sprout v25g_root_crown_then_sprout	3	z	1	0.60	18000	202605841	broad thick-lamina spider root; primary positive candidate
spider_runner_zpos	5	$RUNNER	v25g_root_crown_conservative v25g_root_plantlet_sprout v25g_root_crown_then_sprout	3	z	1	0.60	20000	202605842	runner/plantlet spider root; tests attached plantlet semantics
spider_broad_ypos_control	6	$BROAD	v25g_root_crown_conservative v25g_root_plantlet_sprout	2	y	1	0.60	18000	202605843	axis control for broad spider root
spider_runner_ypos_control	7	$RUNNER	v25g_root_crown_conservative v25g_root_plantlet_sprout	2	y	1	0.60	20000	202605844	axis control for runner spider root
spider_old_zpos_control	6	$OLD	v25g_root_crown_conservative v25g_root_plantlet_sprout	2	z	1	0.60	16000	202605845	old strapleaf root control
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
    --out-json "$OUT/metrics/fern_leaf_recursive_metrics_20260511g.json" \
    --out-csv "$OUT/metrics/fern_leaf_recursive_metrics_20260511g.csv" \
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

start_main4() {
  write_manifest
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511g.sh" broad > "$LOG/lane_broad.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/broad.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511g.sh" runner > "$LOG/lane_runner.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/runner.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511g.sh" broad_control > "$LOG/lane_broad_control.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/broad_control.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511g.sh" runner_control > "$LOG/lane_runner_control.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/runner_control.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

start_old_control() {
  write_manifest
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511g.sh" old_control > "$LOG/lane_old_control.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/old_control.pid"
  echo "STARTED_OLD_CONTROL $(date -Is) pid=$(cat "$OUT/pids/old_control.pid")"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  old-control|start-old-control) start_old_control ;;
  broad) run_case 4 spider_broad_zpos "$BROAD" "v25g_root_crown_conservative v25g_root_plantlet_sprout v25g_root_crown_then_sprout" 3 z 1 0.60 18000 202605841 ;;
  runner) run_case 5 spider_runner_zpos "$RUNNER" "v25g_root_crown_conservative v25g_root_plantlet_sprout v25g_root_crown_then_sprout" 3 z 1 0.60 20000 202605842 ;;
  broad_control) run_case 6 spider_broad_ypos_control "$BROAD" "v25g_root_crown_conservative v25g_root_plantlet_sprout" 2 y 1 0.60 18000 202605843 ;;
  runner_control) run_case 7 spider_runner_ypos_control "$RUNNER" "v25g_root_crown_conservative v25g_root_plantlet_sprout" 2 y 1 0.60 20000 202605844 ;;
  old_control) run_case 6 spider_old_zpos_control "$OLD" "v25g_root_crown_conservative v25g_root_plantlet_sprout" 2 z 1 0.60 16000 202605845 ;;
  metrics) metrics_all ;;
  status) status_all ;;
  *) echo "usage: $0 {start-main4|old-control|status|metrics|broad|runner|broad_control|runner_control|old_control}" >&2; exit 2 ;;
esac
