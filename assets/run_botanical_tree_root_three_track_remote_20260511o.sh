#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/botanical_tree_root_recursive_remote_20260511o"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/image_roots" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/botanical_tree_root_recursive_remote_20260511o" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511o"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/botanical_tree_root_recursive_remote_20260511o"
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
POLY_FERN="$ROOT/results/polyhaven_botanical_cc0_roots_20260511/fern_02/fern_02_all.obj"
POLY_FERN_PART="$ROOT/results/polyhaven_botanical_cc0_roots_20260511/fern_02/fern_02_part00.obj"
POLY_POTTED_LEAVES="$ROOT/results/polyhaven_botanical_cc0_roots_20260511/potted_plant_02/potted_plant_02_leaves.obj"
V23_ROOTFAN="$ROOT/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_root_fan_d5_multi_root_smooth_rootlets/V23_lsys_root_fan_d5_multi_root_smooth_rootlets.obj"
V23_PINE="$ROOT/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles/V23_lsys_pine_canopy_d5_multi_root_smooth_needles.obj"
IMGROOT="$ROOT/downloads/botanical_guides_20260511j_low_complexity"
DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"

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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511o/gpu${gpu}_${label}"
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

run_image_root() {
  local gpu="$1"
  local label="$2"
  local image="$3"
  local seed="$4"
  local steps="$5"
  local preprocess="$6"
  local target="$OUT/image_roots/${label}_steps${steps}_seed${seed}_${preprocess}"
  local log="$LOG/image_${label}_steps${steps}_seed${seed}_${preprocess}.log"
  if [[ ! -f "$image" ]]; then
    echo "MISSING_IMAGE $image" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511o/gpu${gpu}_image_${label}_${seed}"
  mkdir -p "$TRITON_CACHE_DIR" "$target"
  local preprocess_arg=()
  if [[ "$preprocess" == "preprocess" ]]; then
    preprocess_arg=(--preprocess)
  fi
  echo "IMAGE_ROOT_BEGIN $(date -Is) gpu=$gpu label=$label image=$image seed=$seed steps=$steps preprocess=$preprocess" | tee "$log"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_dinov3_official_min_smoke.py" \
    --image "$image" \
    --dinov3-model "$DINO" \
    --out "$target" \
    --steps "$steps" \
    --seed "$seed" \
    "${preprocess_arg[@]}" 2>&1 | tee -a "$log"
  local status=${PIPESTATUS[0]}
  echo "IMAGE_ROOT_END $(date -Is) label=$label status=$status" | tee -a "$log"
  return "$status"
}

lane_spider_positive() {
  run_recurse 4 spider_broad_tipclean_d4_yneg_20260511o "$SPIDER_BROAD" "v25l_spider_leaf_tip_clean v25k_spider_terminal_leaflet" 4 y -1 0.62 32000 202607401 || true
  run_recurse 4 spider_runner_terminal_d4_yneg_20260511o "$SPIDER_RUNNER" "v25k_spider_terminal_leaflet v25l_spider_leaf_tip_clean" 4 y -1 0.62 32000 202607402 || true
}

lane_polyhaven_cc0() {
  run_recurse 5 polyhaven_fern_all_yneg_20260511o "$POLY_FERN" "v25n_fern_pinnae_sparse fern_frond_pinnae_attach v25k_spider_terminal_leaflet" 3 y -1 0.62 18000 202607411 || true
  run_recurse 5 polyhaven_fern_part_yneg_20260511o "$POLY_FERN_PART" "v25k_spider_terminal_leaflet leaf_basal_handle_attach" 3 y -1 0.62 12000 202607412 || true
  run_recurse 5 polyhaven_potted_leaves_yneg_20260511o "$POLY_POTTED_LEAVES" "v25k_spider_terminal_leaflet v25l_spider_leaf_tip_clean leaf_basal_handle_attach" 3 y -1 0.62 22000 202607413 || true
}

lane_tree_root_leaf() {
  run_recurse 6 tree_rootfan_primary_ypos_20260511o "$V23_ROOTFAN" "v25l_root_primary_branch v25l_root_two_phase v25n_whole_root_corner" 4 y 1 0.64 36000 202607421 || true
  run_recurse 6 tree_pine_leaf_yneg_20260511o "$V23_PINE" "v25n_pine_leaf_gated v25k_pine_terminal_needles v25l_pine_leaf_cluster_clean" 4 y -1 0.62 36000 202607422 || true
}

lane_image_roots() {
  run_image_root 7 spider_rosette_single_pd "$IMGROOT/spider_rosette_single_pd_condition_768.png" 202607431 10 preprocess || true
  run_image_root 7 spider_photo_rosette_cc0 "$IMGROOT/spider_photo_rosette_cc0_condition_768.png" 202607432 10 preprocess || true
  run_image_root 7 rubber_fig_trunk_contact_cc0 "$IMGROOT/rubber_fig_trunk_contact_cc0_condition_768.png" 202607433 10 preprocess || true
  run_image_root 7 fiddlehead_single_curl_cc0 "$IMGROOT/fiddlehead_single_curl_cc0_condition_768.png" 202607434 10 preprocess || true
}

write_manifest() {
  cat > "$OUT/botanical_tree_root_manifest_20260511o.tsv" <<TSV
label	gpu	track	mesh_or_image	grammars_or_steps	depths	growth_axis	growth_sign	seed	claim_scope
spider_broad_tipclean_d4_yneg_20260511o	4	spider_positive	$SPIDER_BROAD	v25l_spider_leaf_tip_clean v25k_spider_terminal_leaflet	4	y	-1	202607401	extension of 20260511n positive rosette candidate
spider_runner_terminal_d4_yneg_20260511o	4	spider_positive	$SPIDER_RUNNER	v25k_spider_terminal_leaflet v25l_spider_leaf_tip_clean	4	y	-1	202607402	extension of 20260511n positive runner candidate
polyhaven_fern_all_yneg_20260511o	5	cc0_polyhaven	$POLY_FERN	v25n_fern_pinnae_sparse fern_frond_pinnae_attach v25k_spider_terminal_leaflet	3	y	-1	202607411	CC0 Poly Haven fern_02 root candidate
polyhaven_fern_part_yneg_20260511o	5	cc0_polyhaven	$POLY_FERN_PART	v25k_spider_terminal_leaflet leaf_basal_handle_attach	3	y	-1	202607412	CC0 Poly Haven fern_02 single-leaf candidate
polyhaven_potted_leaves_yneg_20260511o	5	cc0_polyhaven	$POLY_POTTED_LEAVES	v25k_spider_terminal_leaflet v25l_spider_leaf_tip_clean leaf_basal_handle_attach	3	y	-1	202607413	CC0 Poly Haven potted_plant_02 leaves-only candidate
tree_rootfan_primary_ypos_20260511o	6	tree_root_leaf_root	$V23_ROOTFAN	v25l_root_primary_branch v25l_root_two_phase v25n_whole_root_corner	4	y	1	202607421	root-side first-split/macroscopic stress; not final unless Blender QA passes
tree_pine_leaf_yneg_20260511o	6	tree_root_leaf_leaf	$V23_PINE	v25n_pine_leaf_gated v25k_pine_terminal_needles v25l_pine_leaf_cluster_clean	4	y	-1	202607422	leaf/crown-side depth4 subprogram
spider_rosette_single_pd_image	7	image_root	$IMGROOT/spider_rosette_single_pd_condition_768.png	steps10 preprocess	0	NA	NA	202607431	image-root quality gate only
spider_photo_rosette_cc0_image	7	image_root	$IMGROOT/spider_photo_rosette_cc0_condition_768.png	steps10 preprocess	0	NA	NA	202607432	image-root quality gate only
rubber_fig_trunk_contact_cc0_image	7	image_root	$IMGROOT/rubber_fig_trunk_contact_cc0_condition_768.png	steps10 preprocess	0	NA	NA	202607433	image-root quality gate only
fiddlehead_single_curl_cc0_image	7	image_root	$IMGROOT/fiddlehead_single_curl_cc0_condition_768.png	steps10 preprocess	0	NA	NA	202607434	image-root quality gate only
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
  while IFS= read -r mesh; do
    label="image_root__$(basename "$(dirname "$mesh")")"
    case_args+=(--case "$label=$mesh")
  done < <(find "$OUT/image_roots" -name trellis2_dinov3_min.obj -type f | sort)
  if [[ ${#case_args[@]} -eq 0 ]]; then
    echo "NO_MESHES_FOR_METRICS"
    return 0
  fi
  "$PY" "$ROOT/assets/recursive_growth_mesh_metrics.py" \
    "${case_args[@]}" \
    --out-json "$OUT/metrics/botanical_tree_root_metrics_20260511o.json" \
    --out-csv "$OUT/metrics/botanical_tree_root_metrics_20260511o.csv" \
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
  find "$OUT/image_roots" -maxdepth 2 -name summary.json -print 2>/dev/null | sort | while read -r summary; do
    "$PY" - <<'PY' "$summary"
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text())
print(f"IMAGE_SUMMARY {p.parent.name} status={d.get('status','ok')} verts={d.get('vertices')} faces={d.get('faces')} tokens={d.get('shape_latent_tokens')} error={d.get('error')}")
PY
  done
  find "$OUT/raw" -path '*/depth_*/preview.png' -type f | wc -l | awk '{print "PREVIEW_COUNT "$1}'
  find "$OUT/raw" -path '*/depth_*/mesh.obj' -type f | wc -l | awk '{print "OBJ_COUNT "$1}'
  find "$OUT/image_roots" -name trellis2_dinov3_min.obj -type f | wc -l | awk '{print "IMAGE_ROOT_OBJ_COUNT "$1}'
}

start_main4() {
  write_manifest
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511o.sh" spider_positive > "$LOG/lane_spider_positive.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/spider_positive.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511o.sh" polyhaven_cc0 > "$LOG/lane_polyhaven_cc0.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/polyhaven_cc0.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511o.sh" tree_root_leaf > "$LOG/lane_tree_root_leaf.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/tree_root_leaf.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511o.sh" image_roots > "$LOG/lane_image_roots.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/image_roots.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  spider_positive) lane_spider_positive ;;
  polyhaven_cc0) lane_polyhaven_cc0 ;;
  tree_root_leaf) lane_tree_root_leaf ;;
  image_roots) lane_image_roots ;;
  metrics) metrics_all ;;
  status) status_all ;;
  manifest) write_manifest ;;
  *) echo "Usage: $0 {start-main4|spider_positive|polyhaven_cc0|tree_root_leaf|image_roots|metrics|status|manifest}" >&2; exit 2 ;;
esac
