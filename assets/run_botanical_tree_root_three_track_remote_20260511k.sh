#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/botanical_tree_root_recursive_remote_20260511k"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/botanical_tree_root_recursive_remote_20260511k" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511k"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/botanical_tree_root_recursive_remote_20260511k"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

SPIDER_BROAD="$ROOT/results/fern_root_candidates_20260511h/spider_rosette_publication_broad_20260511h/spider_rosette_publication_broad_20260511h.obj"
SPIDER_RUNNER="$ROOT/results/fern_root_candidates_20260511h/spider_rosette_publication_runner_20260511h/spider_rosette_publication_runner_20260511h.obj"
FIDDLE_TIGHT="$ROOT/results/fern_root_candidates_20260511h/fiddlehead_tight_spiral_b/fiddlehead_tight_spiral_b.obj"
FERN_LACY="$ROOT/results/fern_root_candidates_20260511h/fern_compound_frond_lacy_b/fern_compound_frond_lacy_b.obj"
V23_ROOTFAN="$ROOT/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_root_fan_d5_multi_root_smooth_rootlets/V23_lsys_root_fan_d5_multi_root_smooth_rootlets.obj"
V23_PINE="$ROOT/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles/V23_lsys_pine_canopy_d5_multi_root_smooth_needles.obj"
RUBBER_RAW="$ROOT/results/botanical_tree_root_recursive_remote_20260511i/image_roots/rubber_fig_aerial_roots_cc0_steps10_seed202605921_raw/trellis2_dinov3_min.obj"

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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511k/gpu${gpu}_${label}"
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

lane_spider_leaf() {
  run_recurse 4 spider_broad_leaflet_yneg_20260511k "$SPIDER_BROAD" "v25k_spider_terminal_leaflet v25k_spider_basal_leaflet_arc v25k_spider_balanced_leaflet" 4 y -1 0.62 26000 202606101 || true
  run_recurse 4 spider_runner_leaflet_yneg_20260511k "$SPIDER_RUNNER" "v25k_spider_terminal_leaflet v25k_spider_balanced_leaflet v25h_spider_runner_distal_micro" 4 y -1 0.62 26000 202606102 || true
}

lane_fern_fiddle() {
  run_recurse 5 fiddle_tight_curl_yneg_20260511k "$FIDDLE_TIGHT" "v25k_fiddlehead_curl_echo v25k_fiddlehead_curl_pinnae fern_spiral_echo_attach" 4 y -1 0.62 22000 202606111 || true
  run_recurse 5 fern_lacy_tip_yneg_20260511k "$FERN_LACY" "fern_frond_pinnae_attach v25k_spider_terminal_leaflet" 3 y -1 0.62 22000 202606112 || true
}

lane_tree_root_leaf() {
  run_recurse 6 tree_rootfan_single_ypos_20260511k "$V23_ROOTFAN" "v25k_root_single_wedge v25k_root_single_then_tiplets v25j_tree_root_wedge_fork" 4 y 1 0.64 30000 202606121 || true
  run_recurse 6 tree_pine_needles_yneg_20260511k "$V23_PINE" "v25k_pine_terminal_needles v25e_crown_tiplet_short" 4 y -1 0.62 30000 202606122 || true
}

lane_rubber_diag() {
  run_recurse 7 rubber_fig_raw_guarded_ypos_20260511k "$RUBBER_RAW" "v25k_root_single_wedge v25j_tree_root_clean_fork" 2 y 1 0.58 18000 202606131 || true
}

write_manifest() {
  cat > "$OUT/botanical_tree_root_manifest_20260511k.tsv" <<TSV
label	gpu	track	mesh	grammars	depths	growth_axis	growth_sign	seed	claim_scope
spider_broad_leaflet_yneg_20260511k	4	plant_leaf	$SPIDER_BROAD	v25k_spider_terminal_leaflet v25k_spider_basal_leaflet_arc v25k_spider_balanced_leaflet	4	y	-1	202606101	clean procedural spider/plant root; root-first repair, not fifth-hero presentation cut
spider_runner_leaflet_yneg_20260511k	4	plant_leaf	$SPIDER_RUNNER	v25k_spider_terminal_leaflet v25k_spider_balanced_leaflet v25h_spider_runner_distal_micro	4	y	-1	202606102	clean procedural spider runner/plantlet root; root-first repair
fiddle_tight_curl_yneg_20260511k	5	fern_fiddlehead	$FIDDLE_TIGHT	v25k_fiddlehead_curl_echo v25k_fiddlehead_curl_pinnae fern_spiral_echo_attach	4	y	-1	202606111	clean procedural fiddlehead root; curl recursion
fern_lacy_tip_yneg_20260511k	5	fern	$FERN_LACY	fern_frond_pinnae_attach v25k_spider_terminal_leaflet	3	y	-1	202606112	clean procedural fern frond; pinnae/tip recursion diagnostic
tree_rootfan_single_ypos_20260511k	6	tree_root_leaf	$V23_ROOTFAN	v25k_root_single_wedge v25k_root_single_then_tiplets v25j_tree_root_wedge_fork	4	y	1	202606121	V23 semantic rootfan; stronger single-wedge thick-to-thin root recursion
tree_pine_needles_yneg_20260511k	6	tree_root_leaf	$V23_PINE	v25k_pine_terminal_needles v25e_crown_tiplet_short	4	y	-1	202606122	V23 semantic pine/leaf source; local leaf/needle frontier recursion
rubber_fig_raw_guarded_ypos_20260511k	7	image_root_diagnostic	$RUBBER_RAW	v25k_root_single_wedge v25j_tree_root_clean_fork	2	y	1	202606131	CC0 rubber fig image-root diagnostic only unless QA passes unexpectedly
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
    --out-json "$OUT/metrics/botanical_tree_root_metrics_20260511k.json" \
    --out-csv "$OUT/metrics/botanical_tree_root_metrics_20260511k.csv" \
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
p = Path(sys.argv[1])
d = json.loads(p.read_text())
print(f"SUMMARY {p.parent.name} kind={d.get('kind')} status={d.get('status','ok')} base_tokens={d.get('base_tokens')} error={d.get('error')}")
for g, gd in d.get('grammars', {}).items():
    depths = gd.get('depths', [])
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
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511k.sh" spider_leaf > "$LOG/lane_spider_leaf.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/spider_leaf.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511k.sh" fern_fiddle > "$LOG/lane_fern_fiddle.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fern_fiddle.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511k.sh" tree_root_leaf > "$LOG/lane_tree_root_leaf.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/tree_root_leaf.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511k.sh" rubber_diag > "$LOG/lane_rubber_diag.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/rubber_diag.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  spider_leaf) lane_spider_leaf ;;
  fern_fiddle) lane_fern_fiddle ;;
  tree_root_leaf) lane_tree_root_leaf ;;
  rubber_diag) lane_rubber_diag ;;
  metrics) metrics_all ;;
  status) status_all ;;
  *) echo "usage: $0 {start-main4|status|metrics|spider_leaf|fern_fiddle|tree_root_leaf|rubber_diag}" >&2; exit 2 ;;
esac
