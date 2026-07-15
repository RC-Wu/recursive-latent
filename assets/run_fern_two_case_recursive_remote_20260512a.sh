#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/fern_two_case_recursive_remote_20260512a"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/roots" "$OUT/image_roots" "$OUT/pids" "$OUT/metrics" "$OUT/blender_qa" "$LOG" \
  "$ROOT/cache/local_tmp/fern_two_case_recursive_remote_20260512a" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/fern_two_case_recursive_remote_20260512a"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/fern_two_case_recursive_remote_20260512a"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"
FIDDLE_IMG_A="$ROOT/downloads/fern_spider_sources_20260511/fiddlehead_golden_spiral_ccby4_condition_1024.png"
FIDDLE_IMG_B="$ROOT/downloads/botanical_guides_20260511j_low_complexity/fiddlehead_single_curl_cc0_condition_768.png"
FERN_IMG_A="$ROOT/downloads/fern_spider_sources_20260511/new_fern_fronds_ccby2_condition_1024.png"
FERN_IMG_B="$ROOT/results/intro_related_figures_20260511/natural_refs/user_requested_20260512/leaf_leaves_branch_texture_fern_pd.jpg"

prepare_roots() {
  "$PY" "$ROOT/assets/prepare_fern_showcase_roots_20260512.py" \
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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/fern_two_case_recursive_remote_20260512a/gpu${gpu}_${label}"
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
  local target="$OUT/image_roots/${label}_steps${steps}_seed${seed}"
  local log="$LOG/image_${label}_steps${steps}_seed${seed}.log"
  if [[ ! -f "$image" ]]; then
    echo "MISSING_IMAGE $image" | tee "$log"
    return 2
  fi
  export TRITON_CACHE_DIR="$ROOT/cache/triton/fern_two_case_recursive_remote_20260512a/gpu${gpu}_image_${label}_${seed}"
  mkdir -p "$TRITON_CACHE_DIR" "$target"
  echo "IMAGE_ROOT_BEGIN $(date -Is) gpu=$gpu label=$label image=$image seed=$seed steps=$steps" | tee "$log"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_dinov3_official_min_smoke.py" \
    --image "$image" \
    --dinov3-model "$DINO" \
    --out "$target" \
    --steps "$steps" \
    --seed "$seed" \
    --preprocess 2>&1 | tee -a "$log"
  local status=${PIPESTATUS[0]}
  echo "IMAGE_ROOT_END $(date -Is) label=$label status=$status" | tee -a "$log"
  return "$status"
}

lane_fiddlehead_showcase() {
  local root_a="$OUT/roots/fiddlehead_showcase_curl_a/fiddlehead_showcase_curl_a.obj"
  local root_b="$OUT/roots/fiddlehead_nested_curl_b/fiddlehead_nested_curl_b.obj"
  run_recurse 4 fiddlehead_curl_a_d3_20260512a "$root_a" "v26a_fiddlehead_nested_curl v26a_fiddlehead_visible_curl v25n_fiddlehead_thick_curl v25l_fiddlehead_guarded_curl" 3 y -1 0.62 26000 202608101 || true
  run_recurse 4 fiddlehead_nested_b_d3_20260512a "$root_b" "v26a_fiddlehead_nested_curl v26a_fiddlehead_visible_curl v25k_fiddlehead_curl_echo" 3 y -1 0.62 26000 202608102 || true
}

lane_image_roots() {
  run_image_root 5 fiddlehead_reference_golden "$FIDDLE_IMG_A" 202608201 10 || true
  run_image_root 5 fiddlehead_reference_single "$FIDDLE_IMG_B" 202608202 10 || true
  run_image_root 5 fern_reference_fronds "$FERN_IMG_A" 202608203 10 || true
  run_image_root 5 fern_reference_user_leaf "$FERN_IMG_B" 202608204 10 || true
}

lane_fern_showcase() {
  local root_a="$OUT/roots/fern_showcase_compound_a/fern_showcase_compound_a.obj"
  local root_b="$OUT/roots/fern_showcase_lacy_b/fern_showcase_lacy_b.obj"
  run_recurse 6 fern_compound_a_d4_20260512a "$root_a" "v26a_fern_showcase_pinnae v26a_fern_showcase_dense_pinnae v25p_fern_midrib_pinnae_handles v25n_fern_pinnae_sparse" 4 y -1 0.62 34000 202608301 || true
  run_recurse 6 fern_lacy_b_d4_20260512a "$root_b" "v26a_fern_showcase_pinnae v26a_fern_showcase_dense_pinnae fern_frond_pinnae_attach" 4 y -1 0.62 36000 202608302 || true
}

lane_fern_fallbacks() {
  local old_arch="$ROOT/results/fern_root_candidates_20260511h/fern_compound_frond_arch_a/fern_compound_frond_arch_a.obj"
  local old_lacy="$ROOT/results/fern_root_candidates_20260511h/fern_compound_frond_lacy_b/fern_compound_frond_lacy_b.obj"
  local poly_part="$ROOT/results/polyhaven_botanical_cc0_roots_20260511/fern_02/fern_02_part00.obj"
  run_recurse 7 fern_arch_old_d3_20260512a "$old_arch" "v26a_fern_showcase_pinnae v25p_fern_midrib_pinnae_handles" 3 y -1 0.62 24000 202608401 || true
  run_recurse 7 fern_lacy_old_d3_20260512a "$old_lacy" "v26a_fern_showcase_dense_pinnae v25n_fern_pinnae_sparse" 3 y -1 0.62 24000 202608402 || true
  run_recurse 7 fern_polyhaven_part_d3_20260512a "$poly_part" "v26a_fern_showcase_pinnae v25p_fern_midrib_pinnae_handles" 3 y -1 0.62 16000 202608403 || true
}

write_manifest() {
  cat > "$OUT/fern_two_case_manifest_20260512a.tsv" <<TSV
label	gpu	track	mesh_or_image	grammars_or_steps	depths	axis	sign	fit	seed	claim_scope
fiddlehead_curl_a_d3_20260512a	4	fiddlehead	root:fiddlehead_showcase_curl_a	v26a_fiddlehead_nested_curl v26a_fiddlehead_visible_curl v25n_fiddlehead_thick_curl v25l_fiddlehead_guarded_curl	3	y	-1	0.62	202608101	publication candidate if Blender QA passes
fiddlehead_nested_b_d3_20260512a	4	fiddlehead	root:fiddlehead_nested_curl_b	v26a_fiddlehead_nested_curl v26a_fiddlehead_visible_curl v25k_fiddlehead_curl_echo	3	y	-1	0.62	202608102	publication candidate if Blender QA passes
image_roots	5	image_root	reference images	steps10 preprocess	0	NA	NA	NA	202608201-204	root-quality gate only
fern_compound_a_d4_20260512a	6	compound_fern	root:fern_showcase_compound_a	v26a_fern_showcase_pinnae v26a_fern_showcase_dense_pinnae v25p_fern_midrib_pinnae_handles v25n_fern_pinnae_sparse	4	y	-1	0.62	202608301	publication candidate if Blender QA passes
fern_lacy_b_d4_20260512a	6	compound_fern	root:fern_showcase_lacy_b	v26a_fern_showcase_pinnae v26a_fern_showcase_dense_pinnae fern_frond_pinnae_attach	4	y	-1	0.62	202608302	publication candidate if Blender QA passes
fern_arch_old_d3_20260512a	7	fern_fallback	old fern arch root	v26a_fern_showcase_pinnae v25p_fern_midrib_pinnae_handles	3	y	-1	0.62	202608401	fallback comparison
fern_lacy_old_d3_20260512a	7	fern_fallback	old fern lacy root	v26a_fern_showcase_dense_pinnae v25n_fern_pinnae_sparse	3	y	-1	0.62	202608402	fallback comparison
fern_polyhaven_part_d3_20260512a	7	fern_fallback	Poly Haven fern part	v26a_fern_showcase_pinnae v25p_fern_midrib_pinnae_handles	3	y	-1	0.62	202608403	CC0 fallback
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
  while IFS= read -r mesh; do
    local label="image_root__$(basename "$(dirname "$mesh")")"
    case_args+=(--case "$label=$mesh")
  done < <(find "$OUT/image_roots" -name trellis2_dinov3_min.obj -type f | sort)
  if [[ ${#case_args[@]} -eq 0 ]]; then
    echo "NO_MESHES_FOR_METRICS"
    return 0
  fi
  "$PY" "$ROOT/assets/recursive_growth_mesh_metrics.py" \
    "${case_args[@]}" \
    --out-json "$OUT/metrics/fern_two_case_metrics_20260512a.json" \
    --out-csv "$OUT/metrics/fern_two_case_metrics_20260512a.csv" \
    --occupancy-resolution 64 \
    --primary-connectivity occupancy 2>&1 | tee "$LOG/metrics_all.log"
}

render_selected() {
  local cases="$OUT/blender_qa/selected_cases.txt"
  : > "$cases"
  find "$OUT/raw" -path '*/depth_*/mesh.obj' -type f | sort | while read -r mesh; do
    local rel="${mesh#$OUT/raw/}"
    local label="${rel%/mesh.obj}"
    case "$label" in
      fiddlehead_curl_a_d3_20260512a/v26a_fiddlehead_nested_curl/depth_03|\
      fiddlehead_curl_a_d3_20260512a/v26a_fiddlehead_visible_curl/depth_03|\
      fiddlehead_nested_b_d3_20260512a/v26a_fiddlehead_nested_curl/depth_03|\
      fern_compound_a_d4_20260512a/v26a_fern_showcase_pinnae/depth_04|\
      fern_compound_a_d4_20260512a/v26a_fern_showcase_dense_pinnae/depth_04|\
      fern_lacy_b_d4_20260512a/v26a_fern_showcase_pinnae/depth_04|\
      fern_lacy_b_d4_20260512a/v26a_fern_showcase_dense_pinnae/depth_04|\
      fern_polyhaven_part_d3_20260512a/v26a_fern_showcase_pinnae/depth_03)
        echo "${label//\//__}=$mesh" >> "$cases"
        ;;
    esac
  done
  if [[ ! -s "$cases" ]]; then
    echo "NO_SELECTED_CASES_FOR_RENDER"
    return 0
  fi
  blender -b --python "$ROOT/assets/blender_render_recursive_mesh.py" -- \
    --case-file "$cases" \
    --out-dir "$OUT/blender_qa/renders" \
    --views iso front \
    --samples 96 \
    --resolution 1800 \
    --material-mode botanical \
    --background white 2>&1 | tee "$LOG/blender_render_selected.log"
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
  find "$OUT/blender_qa/renders" -name '*.png' -type f 2>/dev/null | wc -l | awk '{print "BLENDER_RENDER_COUNT "$1}'
}

start_main4() {
  write_manifest
  prepare_roots
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512a.sh" fiddlehead_showcase > "$LOG/lane_fiddlehead_showcase.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fiddlehead_showcase.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512a.sh" image_roots > "$LOG/lane_image_roots.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/image_roots.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512a.sh" fern_showcase > "$LOG/lane_fern_showcase.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fern_showcase.pid"
  nohup bash "$ROOT/assets/run_fern_two_case_recursive_remote_20260512a.sh" fern_fallbacks > "$LOG/lane_fern_fallbacks.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fern_fallbacks.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  prepare_roots) prepare_roots ;;
  fiddlehead_showcase) lane_fiddlehead_showcase ;;
  image_roots) lane_image_roots ;;
  fern_showcase) lane_fern_showcase ;;
  fern_fallbacks) lane_fern_fallbacks ;;
  metrics) metrics_all ;;
  render_selected) render_selected ;;
  status) status_all ;;
  manifest) write_manifest ;;
  *) echo "Usage: $0 {start-main4|prepare_roots|fiddlehead_showcase|image_roots|fern_showcase|fern_fallbacks|metrics|render_selected|status|manifest}" >&2; exit 2 ;;
esac

