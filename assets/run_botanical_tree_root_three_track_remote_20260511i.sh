#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/botanical_tree_root_recursive_remote_20260511i"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/image_roots" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/botanical_tree_root_recursive_remote_20260511i" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511i"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/botanical_tree_root_recursive_remote_20260511i"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"
GUIDES="$ROOT/downloads/botanical_guides_20260511/processed"

BROAD="$ROOT/results/fern_root_candidates_20260511h/spider_rosette_publication_broad_20260511h/spider_rosette_publication_broad_20260511h.obj"
RUNNER="$ROOT/results/fern_root_candidates_20260511h/spider_rosette_publication_runner_20260511h/spider_rosette_publication_runner_20260511h.obj"
FERN_ARCH="$ROOT/results/fern_root_candidates_20260511h/fern_compound_frond_arch_a/fern_compound_frond_arch_a.obj"
FERN_LACY="$ROOT/results/fern_root_candidates_20260511h/fern_compound_frond_lacy_b/fern_compound_frond_lacy_b.obj"
V23_PINE="$ROOT/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles/V23_lsys_pine_canopy_d5_multi_root_smooth_needles.obj"
V23_ROOTFAN="$ROOT/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_lsys_root_fan_d5_multi_root_smooth_rootlets/V23_lsys_root_fan_d5_multi_root_smooth_rootlets.obj"
V23_ROOTNET="$ROOT/results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/inputs/V23_sc_root_network_260_attractor_rootlets/V23_sc_root_network_260_attractor_rootlets.obj"

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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511i/gpu${gpu}_${label}"
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
  local preprocess="$6"
  local label="${key}_steps${steps}_seed${seed}_${preprocess}"
  local target="$OUT/image_roots/$label"
  local log="$LOG/image_${label}.log"
  if [[ ! -f "$image" ]]; then
    echo "MISSING_IMAGE $image" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/botanical_tree_root_recursive_remote_20260511i/gpu${gpu}_image_${label}"
  mkdir -p "$target" "$TRITON_CACHE_DIR"
  echo "IMAGE_ROOT_BEGIN $(date -Is) gpu=$gpu label=$label image=$image seed=$seed steps=$steps preprocess=$preprocess" | tee "$log"
  local preprocess_arg=()
  if [[ "$preprocess" == "preprocess" ]]; then
    preprocess_arg=(--preprocess)
  fi
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
raise SystemExit(0 if 0 < faces <= 900000 and 0 < tokens <= 2600 else 1)
PY
}

lane_plant_broad() {
  run_recurse 4 plant_broad_yneg_20260511i "$BROAD" "v25h_spider_basal_crown_micro v25h_spider_leaf_tiplet_micro v25h_spider_basal_then_tiplet" 4 y -1 0.62 26000 202605901
  run_recurse 4 fern_arch_yneg_20260511i "$FERN_ARCH" "fern_frond_tip_attach fern_frond_pinnae_attach v25e_crown_tiplet_short" 3 y -1 0.62 22000 202605902
}

lane_plant_runner() {
  run_recurse 5 plant_runner_yneg_20260511i "$RUNNER" "v25h_spider_runner_distal_micro v25h_spider_basal_then_tiplet v25h_spider_leaf_tiplet_micro" 4 y -1 0.62 28000 202605911
  run_recurse 5 fern_lacy_yneg_20260511i "$FERN_LACY" "fern_frond_tip_attach fern_frond_pinnae_attach v25e_rim_leaflet_micro" 3 y -1 0.62 22000 202605912
}

lane_external_guides() {
  run_image_root 6 rubber_fig_aerial_roots_cc0 "$GUIDES/rubber_fig_aerial_roots_cc0_condition_1024.png" 202605921 10 raw || true
  run_image_root 6 fiddlehead_ferns_cc0 "$GUIDES/fiddlehead_ferns_cc0_condition_1024.png" 202605922 10 raw || true
  run_image_root 6 spider_plant_commons_pd "$GUIDES/spider_plant_commons_pd_condition_1024.png" 202605923 10 raw || true
  run_image_root 6 beech_aerial_roots_pd "$GUIDES/beech_aerial_roots_pd_condition_1024.png" 202605924 10 raw || true

  for root_dir in "$OUT"/image_roots/*_raw; do
    [[ -d "$root_dir" ]] || continue
    if generated_root_ok "$root_dir"; then
      local label
      label="$(basename "$root_dir")"
      local grammar="v25h_tree_root_shrink_fork v25h_tree_root_fork_tiplet"
      local axis="y"
      local sign="1"
      if [[ "$label" == spider_plant* ]]; then
        grammar="v25h_spider_basal_crown_micro v25h_spider_leaf_tiplet_micro"
        sign="-1"
      elif [[ "$label" == fiddlehead* ]]; then
        grammar="fern_spiral_echo_attach fern_frond_tip_attach"
        sign="-1"
      fi
      run_recurse 6 "generated_${label}_recurse" "$root_dir/trellis2_dinov3_min.obj" "$grammar" 2 "$axis" "$sign" 0.60 22000 202605929 || true
    else
      echo "SKIP_GENERATED_RECURSE $(date -Is) root_dir=$root_dir reason=missing_failed_or_too_large" | tee -a "$LOG/external_guides_skips.log"
    fi
  done
}

lane_tree_root_leaf() {
  run_recurse 7 tree_leaf_v23_pine_yneg_d4_20260511i "$V23_PINE" "v25h_tree_root_fork_tiplet v25e_crown_tiplet_short fern_frond_tip_attach" 4 y -1 0.64 30000 202605931
  run_recurse 7 tree_root_v23_rootfan_ypos_d4_20260511i "$V23_ROOTFAN" "v25h_tree_root_shrink_fork v25h_tree_root_fork_tiplet" 4 y 1 0.64 30000 202605932
  run_recurse 7 tree_root_v23_rootnet_ypos_d3_20260511i "$V23_ROOTNET" "v25h_tree_root_shrink_fork v25e_root_rim_tiplet" 3 y 1 0.64 28000 202605933
}

write_manifest() {
  cat > "$OUT/botanical_tree_root_manifest_20260511i.tsv" <<TSV
label	gpu	track	mesh_or_image	grammars_or_mode	depths_or_steps	growth_axis	growth_sign	seed	claim_scope
plant_broad_yneg_20260511i	4	plant_leaf	$BROAD	v25h_spider_basal_crown_micro v25h_spider_leaf_tiplet_micro v25h_spider_basal_then_tiplet	4	y	-1	202605901	axis-corrected broad plant-leaf/spider rosette root
fern_arch_yneg_20260511i	4	fern	$FERN_ARCH	fern_frond_tip_attach fern_frond_pinnae_attach v25e_crown_tiplet_short	3	y	-1	202605902	compound fern procedural root fallback
plant_runner_yneg_20260511i	5	spider_runner	$RUNNER	v25h_spider_runner_distal_micro v25h_spider_basal_then_tiplet v25h_spider_leaf_tiplet_micro	4	y	-1	202605911	axis-corrected spider runner/plantlet candidate
fern_lacy_yneg_20260511i	5	fern	$FERN_LACY	fern_frond_tip_attach fern_frond_pinnae_attach v25e_rim_leaflet_micro	3	y	-1	202605912	lacy fern procedural root fallback
external_guides	6	spider_fern_roots	$GUIDES	TRELLIS2 image-root generation then guarded depth-2 recursion	10/raw	mixed	mixed	202605921-202605929	CC0/PD/CC-BY image-conditioned root acquisition and fast recursion
tree_leaf_v23_pine_yneg_d4_20260511i	7	tree_root_leaf	$V23_PINE	v25h_tree_root_fork_tiplet v25e_crown_tiplet_short fern_frond_tip_attach	4	y	-1	202605931	attached-needle/leaf V23 L-system tree module; leaf/crown recursion
tree_root_v23_rootfan_ypos_d4_20260511i	7	tree_root_leaf	$V23_ROOTFAN	v25h_tree_root_shrink_fork v25h_tree_root_fork_tiplet	4	y	1	202605932	V23 root-fan module; downward thick-to-thin root recursion
tree_root_v23_rootnet_ypos_d3_20260511i	7	tree_root_leaf	$V23_ROOTNET	v25h_tree_root_shrink_fork v25e_root_rim_tiplet	3	y	1	202605933	root-network backup for natural root branching
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
    --out-json "$OUT/metrics/botanical_tree_root_metrics_20260511i.json" \
    --out-csv "$OUT/metrics/botanical_tree_root_metrics_20260511i.csv" \
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
print(f"SUMMARY {p.parent.name} kind={d.get('kind')} status={d.get('status','ok')} base_tokens={d.get('base_tokens')} faces={d.get('faces')} error={d.get('error')}")
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
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511i.sh" plant_broad > "$LOG/lane_plant_broad.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/plant_broad.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511i.sh" plant_runner > "$LOG/lane_plant_runner.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/plant_runner.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511i.sh" external_guides > "$LOG/lane_external_guides.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/external_guides.pid"
  nohup bash "$ROOT/assets/run_botanical_tree_root_three_track_remote_20260511i.sh" tree_root_leaf > "$LOG/lane_tree_root_leaf.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/tree_root_leaf.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  plant_broad) lane_plant_broad ;;
  plant_runner) lane_plant_runner ;;
  external_guides) lane_external_guides ;;
  tree_root_leaf) lane_tree_root_leaf ;;
  metrics) metrics_all ;;
  status) status_all ;;
  *) echo "usage: $0 {start-main4|status|metrics|plant_broad|plant_runner|external_guides|tree_root_leaf}" >&2; exit 2 ;;
esac
