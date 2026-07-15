#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/botanical_tree_root_recursive_remote_20260511l"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/image_roots" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/botanical_tree_root_recursive_remote_20260511l" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511l"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/botanical_tree_root_recursive_remote_20260511l"
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
PLANT_POLY_CC0="$ROOT/results/plant_leaf_recursive_root_20260511/spider_inputs/poly_pizza_small_plant_cc0_root.obj"
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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511l/gpu${gpu}_${label}"
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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511l/gpu${gpu}_image_${label}"
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
raise SystemExit(0 if 0 < faces <= 520000 and 0 < tokens <= 2200 else 1)
PY
}

lane_plant_leaf() {
  run_recurse 4 plant_leaf_basemid_v25l_yneg_20260511l "$PLANT_BASEMID" "v25l_spider_leaf_cluster_compact v25l_spider_leaf_treecrown v25l_spider_leaf_tip_clean" 4 y -1 0.58 30000 202606201 || true
  run_recurse 4 plant_leaf_green_v25l_yneg_20260511l "$PLANT_GREEN" "v25l_spider_leaf_cluster_compact v25l_spider_leaf_treecrown v25l_spider_leaf_tip_clean" 3 y -1 0.58 28000 202606202 || true
  run_recurse 4 plant_poly_cc0_v25l_yneg_20260511l "$PLANT_POLY_CC0" "v25l_spider_leaf_cluster_compact v25l_spider_leaf_treecrown" 4 y -1 0.62 28000 202606203 || true
}

lane_spider_fern() {
  run_recurse 5 spider_broad_v25l_yneg_20260511l "$SPIDER_BROAD" "v25l_spider_leaf_cluster_compact v25l_spider_leaf_treecrown v25l_spider_leaf_tip_clean" 4 y -1 0.62 30000 202606211 || true
  run_recurse 5 spider_runner_v25l_yneg_20260511l "$SPIDER_RUNNER" "v25l_spider_leaf_treecrown v25l_spider_leaf_tip_clean v25k_spider_terminal_leaflet" 4 y -1 0.62 30000 202606212 || true
  run_recurse 5 fiddle_guarded_v25l_yneg_20260511l "$FIDDLE_TIGHT" "v25l_fiddlehead_guarded_curl fern_frond_tip_attach" 4 y -1 0.62 22000 202606213 || true
  run_recurse 5 fern_arch_v25l_yneg_20260511l "$FERN_ARCH" "fern_frond_pinnae_attach v25l_spider_leaf_tip_clean" 3 y -1 0.62 22000 202606214 || true
}

lane_tree_root_leaf() {
  run_recurse 6 tree_rootfan_v25l_ypos_20260511l "$V23_ROOTFAN" "v25l_root_relaxed_wedge v25l_root_primary_branch v25l_root_two_phase v25l_root_two_phase_rootlets" 4 y 1 0.64 34000 202606221 || true
  run_recurse 6 tree_pine_v25l_yneg_20260511l "$V23_PINE" "v25l_pine_leaf_cluster_clean v25l_pine_branch_tip_cluster v25k_pine_terminal_needles" 4 y -1 0.62 34000 202606222 || true
}

lane_lowcond_images() {
  run_image_root 7 spider_photo_rosette_cc0 "$LOWCOND/spider_photo_rosette_cc0_condition_768.png" 202606231 8 || true
  run_image_root 7 spider_rosette_single_pd "$LOWCOND/spider_rosette_single_pd_condition_768.png" 202606232 8 || true
  run_image_root 7 rubber_fig_3_7_roots_cc0 "$LOWCOND/rubber_fig_3_7_roots_cc0_condition_768.png" 202606233 8 || true
  run_image_root 7 rubber_fig_trunk_contact_cc0 "$LOWCOND/rubber_fig_trunk_contact_cc0_condition_768.png" 202606234 8 || true
  run_image_root 7 fiddlehead_single_curl_cc0 "$LOWCOND/fiddlehead_single_curl_cc0_condition_768.png" 202606235 8 || true

  for root_dir in "$OUT"/image_roots/*_lowcond; do
    [[ -d "$root_dir" ]] || continue
    if generated_root_ok "$root_dir"; then
      local label
      label="$(basename "$root_dir")"
      local grammar="v25l_root_relaxed_wedge v25l_root_two_phase"
      local sign="1"
      if [[ "$label" == spider* ]]; then
        grammar="v25l_spider_leaf_cluster_compact v25l_spider_leaf_treecrown"
        sign="-1"
      elif [[ "$label" == fiddlehead* ]]; then
        grammar="v25l_fiddlehead_guarded_curl fern_frond_tip_attach"
        sign="-1"
      fi
      run_recurse 7 "generated_${label}_recurse" "$root_dir/trellis2_dinov3_min.obj" "$grammar" 2 y "$sign" 0.60 22000 202606239 || true
    else
      echo "SKIP_GENERATED_RECURSE $(date -Is) root_dir=$root_dir reason=missing_failed_or_too_large" | tee -a "$LOG/lowcond_image_skips.log"
    fi
  done
}

write_manifest() {
  cat > "$OUT/botanical_tree_root_manifest_20260511l.tsv" <<TSV
label	gpu	track	mesh_or_image	grammars_or_mode	depths_or_steps	growth_axis	growth_sign	seed	claim_scope
plant_leaf_basemid_v25l_yneg_20260511l	4	plant_leaf_true_cut	$PLANT_BASEMID	v25l_spider_leaf_cluster_compact v25l_spider_leaf_treecrown v25l_spider_leaf_tip_clean	4	y	-1	202606201	true fifth-hero plant cut; compact/tree-crown leaf recursion after 20260511j fragmentation
plant_leaf_green_v25l_yneg_20260511l	4	plant_leaf_true_cut	$PLANT_GREEN	v25l_spider_leaf_cluster_compact v25l_spider_leaf_treecrown v25l_spider_leaf_tip_clean	3	y	-1	202606202	true fifth-hero green cluster; diagnostic unless connectivity improves
plant_poly_cc0_v25l_yneg_20260511l	4	plant_leaf_cc0_fallback	$PLANT_POLY_CC0	v25l_spider_leaf_cluster_compact v25l_spider_leaf_treecrown	4	y	-1	202606203	CC0 small-plant direct root fallback for plant-leaf recursion
spider_broad_v25l_yneg_20260511l	5	spider_fern_root	$SPIDER_BROAD	v25l_spider_leaf_cluster_compact v25l_spider_leaf_treecrown v25l_spider_leaf_tip_clean	4	y	-1	202606211	clean procedural broad rosette with v25l compact leaf growth
spider_runner_v25l_yneg_20260511l	5	spider_fern_root	$SPIDER_RUNNER	v25l_spider_leaf_treecrown v25l_spider_leaf_tip_clean v25k_spider_terminal_leaflet	4	y	-1	202606212	clean procedural runner/plantlet root with conservative growth
fiddle_guarded_v25l_yneg_20260511l	5	fern_crozier	$FIDDLE_TIGHT	v25l_fiddlehead_guarded_curl fern_frond_tip_attach	4	y	-1	202606213	guarded fiddlehead recursion after 20260511k fragmentation
fern_arch_v25l_yneg_20260511l	5	fern_frond	$FERN_ARCH	fern_frond_pinnae_attach v25l_spider_leaf_tip_clean	3	y	-1	202606214	fern frond/pinnae diagnostic
tree_rootfan_v25l_ypos_20260511l	6	tree_root_leaf_root	$V23_ROOTFAN	v25l_root_relaxed_wedge v25l_root_primary_branch v25l_root_two_phase v25l_root_two_phase_rootlets	4	y	1	202606221	V23 rootfan; relaxed/primary/two-phase root recursion to avoid 20260511k no-op and dust
tree_pine_v25l_yneg_20260511l	6	tree_root_leaf_leaf	$V23_PINE	v25l_pine_leaf_cluster_clean v25l_pine_branch_tip_cluster v25k_pine_terminal_needles	4	y	-1	202606222	V23 pine/needle; cleaner branch-tip leaf recursion
lowcond_images_v25l	7	image_root	$LOWCOND	TRELLIS2 image-root generation from CC0/PD 768 crops then guarded depth-2 recursion	8/mixed	y	mixed	202606231-202606239	image-root diagnostics; promote only if root generation and recursion both pass QA
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
    --out-json "$OUT/metrics/botanical_tree_root_metrics_20260511l.json" \
    --out-csv "$OUT/metrics/botanical_tree_root_metrics_20260511l.csv" \
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
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511l.sh" plant_leaf > "$LOG/lane_plant_leaf.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/plant_leaf.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511l.sh" spider_fern > "$LOG/lane_spider_fern.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/spider_fern.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511l.sh" tree_root_leaf > "$LOG/lane_tree_root_leaf.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/tree_root_leaf.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511l.sh" lowcond_images > "$LOG/lane_lowcond_images.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/lowcond_images.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  plant_leaf) lane_plant_leaf ;;
  spider_fern) lane_spider_fern ;;
  tree_root_leaf) lane_tree_root_leaf ;;
  lowcond_images) lane_lowcond_images ;;
  metrics) metrics_all ;;
  status) status_all ;;
  *) echo "usage: $0 {start-main4|status|metrics|plant_leaf|spider_fern|tree_root_leaf|lowcond_images}" >&2; exit 2 ;;
esac
