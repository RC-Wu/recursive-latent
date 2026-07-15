#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/fern_two_case_recursive_remote_20260512d"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/roots" "$OUT/pids" "$OUT/metrics" "$OUT/blender_qa" "$LOG" \
  "$ROOT/cache/local_tmp/fern_two_case_recursive_remote_20260512d" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/fern_two_case_recursive_remote_20260512d"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/fern_two_case_recursive_remote_20260512d"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

prepare_roots() {
  "$PY" "$ROOT/assets/prepare_fern_showcase_roots_20260512d.py" \
    --out "$OUT/roots" \
    --seed 20260512 2>&1 | tee "$LOG/prepare_roots.log"
}

run_recurse() {
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
    echo "MISSING_MESH $mesh" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/fern_two_case_recursive_remote_20260512d/gpu${gpu}_${label}"
  mkdir -p "$TRITON_CACHE_DIR" "$out_dir"
  echo "RECURSE_BEGIN $(date -Is) gpu=$gpu label=$label mesh=$mesh grammars=$grammars depths=$depths axis=$axis sign=$sign fit=$fit max_tokens=$max_tokens seed=$seed" | tee "$log"
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
  echo "RECURSE_END $(date -Is) label=$label status=$status" | tee -a "$log"
  return "$status"
}

lane_fiddlehead_compact() {
  local root="$OUT/roots/fiddlehead_solid_koru_g/fiddlehead_solid_koru_g.obj"
  run_recurse 4 fiddlehead_solid_koru_g_d4_20260512d "$root" "v26d_fiddlehead_inner_buds v26d_fiddlehead_solid_echo v26d_fiddlehead_echo_then_buds v26b_fiddlehead_scale_buds" 4 y -1 0.64 30000 202609901 || true
}

lane_fiddlehead_hook() {
  local root="$OUT/roots/fiddlehead_bud_crozier_h/fiddlehead_bud_crozier_h.obj"
  run_recurse 5 fiddlehead_bud_crozier_h_d4_20260512d "$root" "v26d_fiddlehead_inner_buds v26d_fiddlehead_solid_echo v26d_fiddlehead_echo_then_buds v26b_fiddlehead_scale_buds" 4 y -1 0.64 30000 202609902 || true
}

lane_fern_wide() {
  local root="$OUT/roots/fern_triangular_frond_g/fern_triangular_frond_g.obj"
  run_recurse 6 fern_triangular_frond_g_d4_20260512d "$root" "v26d_fern_visible_refinement v26d_fern_bounded_sidelets v26d_fern_refinement_then_sidelets v26b_fern_branchlet_pinnae" 4 y -1 0.62 42000 202609903 || true
}

lane_fern_fractal() {
  local root="$OUT/roots/fern_lacy_frond_h/fern_lacy_frond_h.obj"
  run_recurse 7 fern_lacy_frond_h_d4_20260512d "$root" "v26d_fern_visible_refinement v26d_fern_bounded_sidelets v26d_fern_refinement_then_sidelets v26b_fern_branchlet_pinnae" 4 y -1 0.62 44000 202609904 || true
}

write_manifest() {
  cat > "$OUT/fern_two_case_manifest_20260512d.tsv" <<TSV
label	gpu	track	mesh	grammars	depths	axis	sign	fit	seed	claim_scope
fiddlehead_solid_koru_g_d4_20260512d	4	fiddlehead	root:fiddlehead_solid_koru_g	v26d_fiddlehead_inner_buds v26d_fiddlehead_solid_echo v26d_fiddlehead_echo_then_buds v26b_fiddlehead_scale_buds	4	y	-1	0.64	202609901	publication candidate if render QA passes
fiddlehead_bud_crozier_h_d4_20260512d	5	fiddlehead	root:fiddlehead_bud_crozier_h	v26d_fiddlehead_inner_buds v26d_fiddlehead_solid_echo v26d_fiddlehead_echo_then_buds v26b_fiddlehead_scale_buds	4	y	-1	0.64	202609902	publication candidate if render QA passes
fern_triangular_frond_g_d4_20260512d	6	compound_fern	root:fern_triangular_frond_g	v26d_fern_visible_refinement v26d_fern_bounded_sidelets v26d_fern_refinement_then_sidelets v26b_fern_branchlet_pinnae	4	y	-1	0.62	202609903	publication candidate if render QA passes
fern_lacy_frond_h_d4_20260512d	7	compound_fern	root:fern_lacy_frond_h	v26d_fern_visible_refinement v26d_fern_bounded_sidelets v26d_fern_refinement_then_sidelets v26b_fern_branchlet_pinnae	4	y	-1	0.62	202609904	publication candidate if render QA passes
TSV
}

metrics_all() {
  local case_args=()
  while IFS= read -r mesh; do
    local rel="${mesh#$OUT/raw/}"
    local label="${rel%/mesh.obj}"
    label="${label//\//__}"
    case_args+=(--case "$label=$mesh")
  done < <(find "$OUT/raw" -path '*/depth_*/mesh.obj' -type f | sort)
  if [[ ${#case_args[@]} -eq 0 ]]; then
    echo "NO_MESHES_FOR_METRICS"
    return 0
  fi
  "$PY" "$ROOT/assets/recursive_growth_mesh_metrics.py" \
    "${case_args[@]}" \
    --out-json "$OUT/metrics/fern_two_case_metrics_20260512d.json" \
    --out-csv "$OUT/metrics/fern_two_case_metrics_20260512d.csv" \
    --occupancy-resolution 64 \
    --primary-connectivity occupancy 2>&1 | tee "$LOG/metrics_all.log"
}

status_all() {
  echo "STATUS $(date -Is)"
  for pid_file in "$OUT"/pids/*.pid; do
    [[ -f "$pid_file" ]] || continue
    local pid
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
p = Path(sys.argv[1])
d = json.loads(p.read_text())
print(f"SUMMARY {p.parent.name} status={d.get('status','ok')} base_tokens={d.get('base_tokens')}")
for g, gd in d.get("grammars", {}).items():
    depths = gd.get("depths", [])
    if depths:
        last = depths[-1]
        print(f"  GRAMMAR {g} depth_count={len(depths)} last_depth={last.get('depth')} tokens={last.get('tokens')} verts={last.get('vertices')} faces={last.get('faces')} stop={gd.get('stop_reason','')}")
PY
  done
  find "$OUT/raw" -path '*/depth_*/preview.png' -type f | wc -l | awk '{print "PREVIEW_COUNT "$1}'
  find "$OUT/raw" -path '*/depth_*/mesh.obj' -type f | wc -l | awk '{print "OBJ_COUNT "$1}'
}

start_main4() {
  write_manifest
  prepare_roots
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512d.sh" fiddlehead_compact > "$LOG/lane_fiddlehead_compact.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fiddlehead_compact.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512d.sh" fiddlehead_hook > "$LOG/lane_fiddlehead_hook.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fiddlehead_hook.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512d.sh" fern_wide > "$LOG/lane_fern_wide.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fern_wide.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512d.sh" fern_fractal > "$LOG/lane_fern_fractal.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fern_fractal.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  prepare_roots) prepare_roots ;;
  fiddlehead_compact) lane_fiddlehead_compact ;;
  fiddlehead_hook) lane_fiddlehead_hook ;;
  fern_wide) lane_fern_wide ;;
  fern_fractal) lane_fern_fractal ;;
  metrics) metrics_all ;;
  status) status_all ;;
  manifest) write_manifest ;;
  *) echo "Usage: $0 {start-main4|prepare_roots|fiddlehead_compact|fiddlehead_hook|fern_wide|fern_fractal|metrics|status|manifest}" >&2; exit 2 ;;
esac
