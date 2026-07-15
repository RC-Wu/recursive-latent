#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/botanical_tree_root_recursive_remote_20260511j"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/image_roots" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/botanical_tree_root_recursive_remote_20260511j" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511j"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/botanical_tree_root_recursive_remote_20260511j"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"
LOWCOND="$ROOT/downloads/botanical_guides_20260511j_low_complexity"

PLANT_BASEMID="$ROOT/results/plant_leaf_recursive_root_20260511/inputs/plant_leaf_base_mid_cluster_root.obj"
PLANT_GREEN="$ROOT/results/plant_leaf_recursive_root_20260511/inputs/plant_leaf_green_cluster_root.obj"
SPIDER_BROAD="$ROOT/results/fern_root_candidates_20260511h/spider_rosette_publication_broad_20260511h/spider_rosette_publication_broad_20260511h.obj"
SPIDER_RUNNER="$ROOT/results/fern_root_candidates_20260511h/spider_rosette_publication_runner_20260511h/spider_rosette_publication_runner_20260511h.obj"
V23_ROOTFAN="$ROOT/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_root_fan_d5_multi_root_smooth_rootlets/V23_lsys_root_fan_d5_multi_root_smooth_rootlets.obj"

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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511j/gpu${gpu}_${label}"
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
  local key="$2"
  local image="$3"
  local seed="$4"
  local steps="$5"
  local label="${key}_steps${steps}_seed${seed}_lowcond"
  local target="$OUT/image_roots/$label"
  local log="$LOG/image_${label}.log"
  if [[ ! -f "$image" ]]; then
    echo "MISSING_IMAGE $image" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511j/gpu${gpu}_image_${label}"
  mkdir -p "$target" "$TRITON_CACHE_DIR"
  echo "IMAGE_ROOT_BEGIN $(date -Is) gpu=$gpu label=$label image=$image seed=$seed steps=$steps" | tee "$log"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_dinov3_official_min_smoke.py" \
    --image "$image" \
    --dinov3-model "$DINO" \
    --out "$target" \
    --steps "$steps" \
    --seed "$seed" 2>&1 | tee -a "$log"
  local status=${PIPESTATUS[0]}
  echo "IMAGE_ROOT_END $(date -Is) label=$label status=$status" | tee -a "$log"
  return "$status"
}

generated_root_ok() {
  local root_dir="$1"
  "$PY" - <<'PY' "$root_dir"
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
s = p / "summary.json"
m = p / "trellis2_dinov3_min.obj"
if not s.exists() or not m.exists():
    raise SystemExit(1)
d = json.loads(s.read_text())
if d.get("status") == "failed":
    raise SystemExit(1)
faces = int(d.get("faces") or 0)
tokens = int(d.get("shape_latent_tokens") or 0)
raise SystemExit(0 if 0 < faces <= 650000 and 0 < tokens <= 2400 else 1)
PY
}

lane_true_plant() {
  run_recurse 4 plant_leaf_basemid_visible_yneg_20260511j "$PLANT_BASEMID" "v25j_spider_leaf_handle_visible v25j_spider_leaf_handle_compact v25j_spider_leaf_schedule" 4 y -1 0.60 30000 202606001 || true
  run_recurse 4 plant_leaf_green_visible_yneg_20260511j "$PLANT_GREEN" "v25j_spider_leaf_handle_visible v25j_spider_leaf_handle_compact" 3 y -1 0.60 28000 202606002 || true
}

lane_spider_visible() {
  run_recurse 5 spider_broad_visible_yneg_20260511j "$SPIDER_BROAD" "v25j_spider_leaf_handle_visible v25j_spider_leaf_schedule v25j_spider_leaf_handle_compact" 4 y -1 0.62 32000 202606011 || true
  run_recurse 5 spider_runner_visible_yneg_20260511j "$SPIDER_RUNNER" "v25j_spider_leaf_handle_visible v25j_spider_leaf_schedule v25h_spider_runner_distal_micro" 4 y -1 0.62 32000 202606012 || true
}

lane_tree_root_clean() {
  run_recurse 6 tree_rootfan_clean_ypos_20260511j "$V23_ROOTFAN" "v25j_tree_root_clean_fork v25j_tree_root_wedge_fork v25j_tree_root_wedge_then_clean" 4 y 1 0.64 32000 202606021 || true
}

lane_lowcond_images() {
  run_image_root 7 spider_rosette_single_pd "$LOWCOND/spider_rosette_single_pd_condition_768.png" 202606031 8 || true
  run_image_root 7 rubber_fig_3_7_roots_cc0 "$LOWCOND/rubber_fig_3_7_roots_cc0_condition_768.png" 202606032 8 || true
  run_image_root 7 rubber_fig_trunk_contact_cc0 "$LOWCOND/rubber_fig_trunk_contact_cc0_condition_768.png" 202606033 8 || true
  run_image_root 7 fiddlehead_single_curl_cc0 "$LOWCOND/fiddlehead_single_curl_cc0_condition_768.png" 202606034 8 || true

  for root_dir in "$OUT"/image_roots/*_lowcond; do
    [[ -d "$root_dir" ]] || continue
    if generated_root_ok "$root_dir"; then
      local label
      label="$(basename "$root_dir")"
      local grammar="v25j_tree_root_clean_fork v25j_tree_root_wedge_fork"
      local sign="1"
      if [[ "$label" == spider* ]]; then
        grammar="v25j_spider_leaf_handle_compact v25j_spider_leaf_schedule"
        sign="-1"
      elif [[ "$label" == fiddlehead* ]]; then
        grammar="fern_spiral_echo_attach fern_frond_tip_attach"
        sign="-1"
      fi
      run_recurse 7 "generated_${label}_recurse" "$root_dir/trellis2_dinov3_min.obj" "$grammar" 2 y "$sign" 0.60 22000 202606039 || true
    else
      echo "SKIP_GENERATED_RECURSE $(date -Is) root_dir=$root_dir reason=missing_failed_or_too_large" | tee -a "$LOG/lowcond_image_skips.log"
    fi
  done
}

write_manifest() {
  cat > "$OUT/botanical_tree_root_manifest_20260511j.tsv" <<TSV
label	gpu	track	mesh_or_image	grammars_or_mode	depths_or_steps	growth_axis	growth_sign	seed	claim_scope
plant_leaf_basemid_visible_yneg_20260511j	4	true_plant_leaf	$PLANT_BASEMID	v25j_spider_leaf_handle_visible v25j_spider_leaf_handle_compact v25j_spider_leaf_schedule	4	y	-1	202606001	true fifth-hero plant-leaf base/mid cut with visible leaf recursion
plant_leaf_green_visible_yneg_20260511j	4	true_plant_leaf	$PLANT_GREEN	v25j_spider_leaf_handle_visible v25j_spider_leaf_handle_compact	3	y	-1	202606002	true fifth-hero green leaf cluster cut
spider_broad_visible_yneg_20260511j	5	spider_leaf	$SPIDER_BROAD	v25j_spider_leaf_handle_visible v25j_spider_leaf_schedule v25j_spider_leaf_handle_compact	4	y	-1	202606011	procedural broad rosette with stronger visible leaf schedule
spider_runner_visible_yneg_20260511j	5	spider_leaf	$SPIDER_RUNNER	v25j_spider_leaf_handle_visible v25j_spider_leaf_schedule v25h_spider_runner_distal_micro	4	y	-1	202606012	procedural runner/plantlet root with visible leaf schedule
tree_rootfan_clean_ypos_20260511j	6	tree_root_leaf	$V23_ROOTFAN	v25j_tree_root_clean_fork v25j_tree_root_wedge_fork v25j_tree_root_wedge_then_clean	4	y	1	202606021	cleaned V23 rootfan thick-to-thin recursion attempt
lowcond_images	7	image_root	$LOWCOND	TRELLIS2 image-root generation from 768 low-complexity crops then guarded depth-2 recursion	8/mixed	y	mixed	202606031-202606039	diagnostic low-complexity spider/root/fern image roots
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
    --out-json "$OUT/metrics/botanical_tree_root_metrics_20260511j.json" \
    --out-csv "$OUT/metrics/botanical_tree_root_metrics_20260511j.csv" \
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
  find "$OUT/raw" "$OUT/image_roots" -maxdepth 2 -name summary.json -print 2>/dev/null | sort | while read -r summary; do
    "$PY" - <<'PY' "$summary"
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
d = json.loads(p.read_text())
print(f"SUMMARY {p.parent.name} kind={d.get('kind')} status={d.get('status','ok')} base_tokens={d.get('base_tokens')} faces={d.get('faces')} tokens={d.get('shape_latent_tokens')} error={d.get('error')}")
for g, gd in d.get("grammars", {}).items():
    depths = gd.get("depths", [])
    if depths:
        last = depths[-1]
        print(f"  GRAMMAR {g} depth_count={len(depths)} last_depth={last.get('depth')} tokens={last.get('tokens')} verts={last.get('vertices')} faces={last.get('faces')} stop={gd.get('stop_reason','')}")
PY
  done
  find "$OUT/raw" -path '*/depth_*/preview.png' -type f | wc -l | awk '{print "PREVIEW_COUNT "$1}'
  find "$OUT/raw" -path '*/depth_*/mesh.obj' -type f | wc -l | awk '{print "OBJ_COUNT "$1}'
  find "$OUT/image_roots" -name trellis2_dinov3_min.obj -type f | wc -l | awk '{print "IMAGE_ROOT_OBJ_COUNT "$1}'
}

start_main4() {
  write_manifest
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511j.sh" true_plant > "$LOG/lane_true_plant.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/true_plant.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511j.sh" spider_visible > "$LOG/lane_spider_visible.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/spider_visible.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511j.sh" tree_root_clean > "$LOG/lane_tree_root_clean.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/tree_root_clean.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511j.sh" lowcond_images > "$LOG/lane_lowcond_images.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/lowcond_images.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  true_plant) lane_true_plant ;;
  spider_visible) lane_spider_visible ;;
  tree_root_clean) lane_tree_root_clean ;;
  lowcond_images) lane_lowcond_images ;;
  metrics) metrics_all ;;
  status) status_all ;;
  *) echo "usage: $0 {start-main4|status|metrics|true_plant|spider_visible|tree_root_clean|lowcond_images}" >&2; exit 2 ;;
esac
