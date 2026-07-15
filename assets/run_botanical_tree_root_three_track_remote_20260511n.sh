#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/botanical_tree_root_recursive_remote_20260511n"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/botanical_tree_root_recursive_remote_20260511n" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511n"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/botanical_tree_root_recursive_remote_20260511n"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

PLANT_BASEMID="$ROOT/results/plant_leaf_recursive_root_20260511/inputs/plant_leaf_base_mid_cluster_root.obj"
PLANT_GREEN="$ROOT/results/plant_leaf_recursive_root_20260511/inputs/plant_leaf_green_cluster_root.obj"
SPIDER_BROAD="$ROOT/results/fern_root_candidates_20260511h/spider_rosette_publication_broad_20260511h/spider_rosette_publication_broad_20260511h.obj"
SPIDER_RUNNER="$ROOT/results/fern_root_candidates_20260511h/spider_rosette_publication_runner_20260511h/spider_rosette_publication_runner_20260511h.obj"
FIDDLE_TIGHT="$ROOT/results/fern_root_candidates_20260511h/fiddlehead_tight_spiral_b/fiddlehead_tight_spiral_b.obj"
FERN_ARCH="$ROOT/results/fern_root_candidates_20260511h/fern_compound_frond_arch_a/fern_compound_frond_arch_a.obj"
V23_ROOTFAN="$ROOT/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_root_fan_d5_multi_root_smooth_rootlets/V23_lsys_root_fan_d5_multi_root_smooth_rootlets.obj"
V23_PINE="$ROOT/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles/V23_lsys_pine_canopy_d5_multi_root_smooth_needles.obj"

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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511n/gpu${gpu}_${label}"
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

lane_plant_leaf() {
  run_recurse 4 plant_leaf_green_v25n_yneg_20260511n "$PLANT_GREEN" "v25n_plant_basal_midrib_leaflet v25n_plant_basal_crown_leaflets" 2 y -1 0.58 26000 202606301 || true
  run_recurse 4 plant_leaf_basemid_v25n_yneg_20260511n "$PLANT_BASEMID" "v25n_plant_basal_midrib_leaflet v25n_plant_basal_crown_leaflets" 2 y -1 0.58 28000 202606302 || true
}

lane_spider_fern() {
  run_recurse 5 spider_broad_v25n_yneg_20260511n "$SPIDER_BROAD" "v25n_spider_runner_leaflet_gated v25l_spider_leaf_tip_clean" 2 y -1 0.62 28000 202606311 || true
  run_recurse 5 spider_runner_v25n_yneg_20260511n "$SPIDER_RUNNER" "v25n_spider_runner_leaflet_gated v25k_spider_terminal_leaflet" 2 y -1 0.62 28000 202606312 || true
  run_recurse 5 fern_arch_v25n_yneg_20260511n "$FERN_ARCH" "v25n_fern_pinnae_sparse fern_frond_pinnae_attach" 2 y -1 0.62 22000 202606313 || true
  run_recurse 5 fiddle_guarded_v25n_yneg_20260511n "$FIDDLE_TIGHT" "v25n_fiddlehead_thick_curl v25l_fiddlehead_guarded_curl" 2 y -1 0.62 22000 202606314 || true
}

lane_tree_root_leaf() {
  run_recurse 6 tree_rootfan_v25n_ypos_20260511n "$V23_ROOTFAN" "v25n_root_short_terminal_rootlets v25n_root_first_split_taper v25l_root_relaxed_wedge" 2 y 1 0.64 32000 202606321 || true
  run_recurse 6 tree_pine_v25n_yneg_20260511n "$V23_PINE" "v25n_pine_leaf_gated v25l_pine_leaf_cluster_clean" 2 y -1 0.62 32000 202606322 || true
}

lane_depth4_check() {
  run_recurse 7 spider_runner_v25n_depth4_yneg_20260511n "$SPIDER_RUNNER" "v25n_spider_runner_leaflet_gated" 4 y -1 0.62 28000 202606331 || true
  run_recurse 7 tree_pine_v25n_depth4_yneg_20260511n "$V23_PINE" "v25n_pine_leaf_gated" 4 y -1 0.62 32000 202606332 || true
}

write_manifest() {
  cat > "$OUT/botanical_tree_root_manifest_20260511n.tsv" <<TSV
label	gpu	track	mesh	grammars	depths	growth_axis	growth_sign	seed	claim_scope
plant_leaf_green_v25n_yneg_20260511n	4	plant_leaf_true_cut	$PLANT_GREEN	v25n_plant_basal_midrib_leaflet v25n_plant_basal_crown_leaflets	2	y	-1	202606301	diagnostic repair of fifth-hero green cut; early-depth only
plant_leaf_basemid_v25n_yneg_20260511n	4	plant_leaf_true_cut	$PLANT_BASEMID	v25n_plant_basal_midrib_leaflet v25n_plant_basal_crown_leaflets	2	y	-1	202606302	diagnostic repair of fifth-hero base-mid cut; early-depth only
spider_broad_v25n_yneg_20260511n	5	spider_rosette	$SPIDER_BROAD	v25n_spider_runner_leaflet_gated v25l_spider_leaf_tip_clean	2	y	-1	202606311	early-depth rosette QA after 20260511l depth4 clutter
spider_runner_v25n_yneg_20260511n	5	spider_runner	$SPIDER_RUNNER	v25n_spider_runner_leaflet_gated v25k_spider_terminal_leaflet	2	y	-1	202606312	early-depth runner QA after 20260511l
fern_arch_v25n_yneg_20260511n	5	fern_frond	$FERN_ARCH	v25n_fern_pinnae_sparse fern_frond_pinnae_attach	2	y	-1	202606313	sparser pinnae repair
fiddle_guarded_v25n_yneg_20260511n	5	fern_crozier	$FIDDLE_TIGHT	v25n_fiddlehead_thick_curl v25l_fiddlehead_guarded_curl	2	y	-1	202606314	thicker guarded curl repair
tree_rootfan_v25n_ypos_20260511n	6	tree_root_leaf_root	$V23_ROOTFAN	v25n_root_short_terminal_rootlets v25n_root_first_split_taper v25l_root_relaxed_wedge	2	y	1	202606321	rootfan early-depth repair; not final depth4 proof
tree_pine_v25n_yneg_20260511n	6	tree_root_leaf_leaf	$V23_PINE	v25n_pine_leaf_gated v25l_pine_leaf_cluster_clean	2	y	-1	202606322	pine leaf early-depth repair
spider_runner_v25n_depth4_yneg_20260511n	7	depth4_check	$SPIDER_RUNNER	v25n_spider_runner_leaflet_gated	4	y	-1	202606331	depth4 stress check only if early rows remain clean
tree_pine_v25n_depth4_yneg_20260511n	7	depth4_check	$V23_PINE	v25n_pine_leaf_gated	4	y	-1	202606332	depth4 stress check only
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
    --out-json "$OUT/metrics/botanical_tree_root_metrics_20260511n.json" \
    --out-csv "$OUT/metrics/botanical_tree_root_metrics_20260511n.csv" \
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
print(f"SUMMARY {p.parent.name} kind={d.get('kind')} status={d.get('status','ok')} base_tokens={d.get('base_tokens')}")
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
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511n.sh" plant_leaf > "$LOG/lane_plant_leaf.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/plant_leaf.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511n.sh" spider_fern > "$LOG/lane_spider_fern.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/spider_fern.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511n.sh" tree_root_leaf > "$LOG/lane_tree_root_leaf.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/tree_root_leaf.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511n.sh" depth4_check > "$LOG/lane_depth4_check.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/depth4_check.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  plant_leaf) lane_plant_leaf ;;
  spider_fern) lane_spider_fern ;;
  tree_root_leaf) lane_tree_root_leaf ;;
  depth4_check) lane_depth4_check ;;
  metrics) metrics_all ;;
  status) status_all ;;
  manifest) write_manifest ;;
  *) echo "Usage: $0 {start-main4|plant_leaf|spider_fern|tree_root_leaf|depth4_check|metrics|status|manifest}" >&2; exit 2 ;;
esac
