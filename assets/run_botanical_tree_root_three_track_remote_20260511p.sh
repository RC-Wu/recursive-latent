#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/botanical_tree_root_recursive_remote_20260511p"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/botanical_tree_root_recursive_remote_20260511p" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511p"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/botanical_tree_root_recursive_remote_20260511p"
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
POLY_FERN_PART="$ROOT/results/polyhaven_botanical_cc0_roots_20260511/fern_02/fern_02_part00.obj"
POLY_POTTED_LEAVES="$ROOT/results/polyhaven_botanical_cc0_roots_20260511/potted_plant_02/potted_plant_02_leaves.obj"
POLY_POTTED_PART="$ROOT/results/polyhaven_botanical_cc0_roots_20260511/potted_plant_02/potted_plant_02_part00.obj"
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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511p/gpu${gpu}_${label}"
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

lane_spider_visible() {
  run_recurse 4 spider_runner_visible_d4_yneg_20260511p "$SPIDER_RUNNER" "v25p_spider_runner_visible_chain v25k_spider_terminal_leaflet v25l_spider_leaf_tip_clean" 4 y -1 0.62 36000 202607501 || true
  run_recurse 4 spider_broad_crownfan_d4_yneg_20260511p "$SPIDER_BROAD" "v25p_spider_rosette_crown_fan v25p_spider_runner_visible_chain v25l_spider_leaf_tip_clean" 4 y -1 0.62 36000 202607502 || true
}

lane_polyhaven_visible() {
  run_recurse 5 polyhaven_fern_part_handles_d3_yneg_20260511p "$POLY_FERN_PART" "v25p_fern_midrib_pinnae_handles v25k_spider_terminal_leaflet" 3 y -1 0.62 16000 202607511 || true
  run_recurse 5 polyhaven_potted_leaves_fan_d3_yneg_20260511p "$POLY_POTTED_LEAVES" "v25p_potted_petiole_leaf_fan v25l_spider_leaf_tip_clean" 3 y -1 0.62 30000 202607512 || true
  run_recurse 5 polyhaven_potted_part_fan_d3_yneg_20260511p "$POLY_POTTED_PART" "v25p_potted_petiole_leaf_fan v25p_spider_rosette_crown_fan" 3 y -1 0.62 22000 202607513 || true
}

lane_tree_leaf_root_ypos() {
  run_recurse 6 tree_pine_leaf_visible_d4_yneg_20260511p "$V23_PINE" "v25p_pine_branch_frontier_needle_whorl v25n_pine_leaf_gated v25l_pine_leaf_cluster_clean" 4 y -1 0.62 42000 202607521 || true
  run_recurse 6 tree_rootfan_firstsplit_d4_ypos_20260511p "$V23_ROOTFAN" "v25p_root_first_split_sidecar v25p_root_first_split_then_rootlets v25l_root_primary_branch" 4 y 1 0.58 42000 202607522 || true
}

lane_tree_root_orientation() {
  run_recurse 7 tree_rootfan_firstsplit_d4_yneg_20260511p "$V23_ROOTFAN" "v25p_root_first_split_sidecar v25p_root_first_split_then_rootlets v25n_root_first_split_taper" 4 y -1 0.58 42000 202607531 || true
  run_recurse 7 tree_rootfan_firstsplit_fit052_yneg_20260511p "$V23_ROOTFAN" "v25p_root_first_split_sidecar v25p_root_first_split_then_rootlets" 4 y -1 0.52 42000 202607532 || true
}

write_manifest() {
  cat > "$OUT/botanical_tree_root_manifest_20260511p.tsv" <<TSV
label	gpu	track	mesh	grammars	depths	growth_axis	growth_sign	fit_scale	seed	claim_scope
spider_runner_visible_d4_yneg_20260511p	4	spider_depth_visible	$SPIDER_RUNNER	v25p_spider_runner_visible_chain v25k_spider_terminal_leaflet v25l_spider_leaf_tip_clean	4	y	-1	0.62	202607501	test stronger depth-visible runner recursion; not complete without Blender depth QA
spider_broad_crownfan_d4_yneg_20260511p	4	spider_depth_visible	$SPIDER_BROAD	v25p_spider_rosette_crown_fan v25p_spider_runner_visible_chain v25l_spider_leaf_tip_clean	4	y	-1	0.62	202607502	test rosette crown-fan handles without whole thin-cluster copy
polyhaven_fern_part_handles_d3_yneg_20260511p	5	cc0_polyhaven	$POLY_FERN_PART	v25p_fern_midrib_pinnae_handles v25k_spider_terminal_leaflet	3	y	-1	0.62	202607511	CC0 single-frond fern part; positive only if semantics and connectivity pass
polyhaven_potted_leaves_fan_d3_yneg_20260511p	5	cc0_polyhaven	$POLY_POTTED_LEAVES	v25p_potted_petiole_leaf_fan v25l_spider_leaf_tip_clean	3	y	-1	0.62	202607512	CC0 potted leaves; high-face candidate requiring selected Blender QA
polyhaven_potted_part_fan_d3_yneg_20260511p	5	cc0_polyhaven	$POLY_POTTED_PART	v25p_potted_petiole_leaf_fan v25p_spider_rosette_crown_fan	3	y	-1	0.62	202607513	lighter CC0 potted component backup
tree_pine_leaf_visible_d4_yneg_20260511p	6	tree_root_leaf_leaf	$V23_PINE	v25p_pine_branch_frontier_needle_whorl v25n_pine_leaf_gated v25l_pine_leaf_cluster_clean	4	y	-1	0.62	202607521	leaf-side tree_root_leaf subprogram
tree_rootfan_firstsplit_d4_ypos_20260511p	6	tree_root_leaf_root	$V23_ROOTFAN	v25p_root_first_split_sidecar v25p_root_first_split_then_rootlets v25l_root_primary_branch	4	y	1	0.58	202607522	root-side first-split candidate using prior root orientation
tree_rootfan_firstsplit_d4_yneg_20260511p	7	tree_root_leaf_root_orientation	$V23_ROOTFAN	v25p_root_first_split_sidecar v25p_root_first_split_then_rootlets v25n_root_first_split_taper	4	y	-1	0.58	202607531	root orientation stress test after user concern about inverted growth direction
tree_rootfan_firstsplit_fit052_yneg_20260511p	7	tree_root_leaf_root_orientation	$V23_ROOTFAN	v25p_root_first_split_sidecar v25p_root_first_split_then_rootlets	4	y	-1	0.52	202607532	lower fit-scale root orientation stress to leave latent room for children
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
    --out-json "$OUT/metrics/botanical_tree_root_metrics_20260511p.json" \
    --out-csv "$OUT/metrics/botanical_tree_root_metrics_20260511p.csv" \
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
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511p.sh" spider_visible > "$LOG/lane_spider_visible.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/spider_visible.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511p.sh" polyhaven_visible > "$LOG/lane_polyhaven_visible.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/polyhaven_visible.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511p.sh" tree_leaf_root_ypos > "$LOG/lane_tree_leaf_root_ypos.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/tree_leaf_root_ypos.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511p.sh" tree_root_orientation > "$LOG/lane_tree_root_orientation.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/tree_root_orientation.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  spider_visible) lane_spider_visible ;;
  polyhaven_visible) lane_polyhaven_visible ;;
  tree_leaf_root_ypos) lane_tree_leaf_root_ypos ;;
  tree_root_orientation) lane_tree_root_orientation ;;
  metrics) metrics_all ;;
  status) status_all ;;
  manifest) write_manifest ;;
  *) echo "Usage: $0 {start-main4|spider_visible|polyhaven_visible|tree_leaf_root_ypos|tree_root_orientation|metrics|status|manifest}" >&2; exit 2 ;;
esac
