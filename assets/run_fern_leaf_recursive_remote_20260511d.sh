#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/fern_leaf_recursive_remote_20260511d"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/fern_leaf_recursive_remote_20260511d" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/fern_leaf_recursive_remote_20260511d"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/fern_leaf_recursive_remote_20260511d"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

SPIDER_RAW="$ROOT/results/fern_root_image_generation_remote_20260511c/image_roots/spider_plant_commons_pd_steps14_seed202605805_raw/trellis2_dinov3_min.obj"
KORU_RAW="$ROOT/results/fern_root_image_generation_remote_20260511c/image_roots/koru_unfurling_ccby25_steps14_seed202605808_raw/trellis2_dinov3_min.obj"
ROOT_FAN="$ROOT/inputs/strict_visual_matched_cases_V25_root_sc_refine_20260510/V25_lsys_root_fan_dense_anchorD_stable/V25_lsys_root_fan_dense_anchorD_stable.obj"
VINE_RUNNER="$ROOT/inputs/strict_visual_matched_cases_V22_botanical_smooth_20260510/V22_lsys_climbing_vine_d6_smooth_leaf_tendrils/V22_lsys_climbing_vine_d6_smooth_leaf_tendrils.obj"
ROOT_NETWORK="$ROOT/inputs/strict_visual_matched_cases_V24_priority_rerun_seed20260511_20260510/V24_sc_root_network_260_anchorA_seedA/V24_sc_root_network_260_anchorA_seedA.obj"
SC_CROWN="$ROOT/inputs/strict_visual_matched_cases_V25_root_sc_refine_20260510/V25_sc_tree_crown_tapered_B/V25_sc_tree_crown_tapered_B.obj"

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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/fern_leaf_recursive_remote_20260511d/gpu${gpu}_${label}"
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
  cat > "$OUT/fern_leaf_recursive_manifest_20260511d.tsv" <<TSV
label	gpu	mesh	grammars	depths	growth_axis	growth_sign	fit_scale	max_tokens	seed	claim_scope
spider_raw_rosette_ypos	4	$SPIDER_RAW	leaf_basal_handle_attach leaf_basal_handle_micro_attach crown_bud_attach	2	y	1	0.62	20000	202605811	TRELLIS2 image-root spider/rosette recursion probe; use only if depth-0 visual is not flat/noisy
koru_raw_spiral_zpos	5	$KORU_RAW	fern_spiral_echo_attach fern_frond_tip_attach fern_recursive_frond_attach	2	z	1	0.60	22000	202605812	TRELLIS2 image-root koru/fiddlehead recursion probe; spiral/frond attached grammar
v25_rootfan_spider_runner_zneg	6	$ROOT_FAN	leaf_basal_handle_attach leaf_basal_handle_micro_attach fern_frond_pinnae_attach	2	z	-1	0.58	22000	202605813	strong connected V25 root-fan as spider/fern rhizome fallback; not external mesh claim
v22_vine_runner_plantlet_ypos	7	$VINE_RUNNER	crown_bud_attach crown_micro_fork_attach fern_frond_tip_attach	2	y	1	0.64	18000	202605814	light connected vine runner/plantlet bridge; tests hanging runner grammar stability
v24_rootnet_fern_rhizome_zpos	6	$ROOT_NETWORK	fern_frond_pinnae_attach fern_recursive_frond_attach crown_micro_fork_attach	2	z	1	0.54	24000	202605815	root-network rhizome candidate; run manually if first four lanes finish cleanly
v25_sc_crown_leaf_growth_ypos	7	$SC_CROWN	crown_bud_attach crown_micro_fork_attach fern_frond_tip_attach	2	y	1	0.54	24000	202605816	tree-crown-like structural control; run manually if first four lanes finish cleanly
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
    --out-json "$OUT/metrics/fern_leaf_recursive_metrics_20260511d.json" \
    --out-csv "$OUT/metrics/fern_leaf_recursive_metrics_20260511d.csv" \
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

start_first4() {
  write_manifest
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511d.sh" spider_raw > "$LOG/lane_spider_raw.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/spider_raw.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511d.sh" koru_raw > "$LOG/lane_koru_raw.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/koru_raw.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511d.sh" rootfan > "$LOG/lane_rootfan.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/rootfan.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511d.sh" vine_runner > "$LOG/lane_vine_runner.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/vine_runner.pid"
  echo "STARTED_FIRST4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

start_followup2() {
  write_manifest
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511d.sh" rootnet > "$LOG/lane_rootnet.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/rootnet.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511d.sh" sc_crown > "$LOG/lane_sc_crown.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/sc_crown.pid"
  echo "STARTED_FOLLOWUP2 $(date -Is) pids=$(cat "$OUT"/pids/rootnet.pid "$OUT"/pids/sc_crown.pid | tr '\n' ' ')"
}

case "${1:-start-first4}" in
  start|start-first4) start_first4 ;;
  followup2) start_followup2 ;;
  spider_raw) run_case 4 spider_raw_rosette_ypos "$SPIDER_RAW" "leaf_basal_handle_attach leaf_basal_handle_micro_attach crown_bud_attach" 2 y 1 0.62 20000 202605811 ;;
  koru_raw) run_case 5 koru_raw_spiral_zpos "$KORU_RAW" "fern_spiral_echo_attach fern_frond_tip_attach fern_recursive_frond_attach" 2 z 1 0.60 22000 202605812 ;;
  rootfan) run_case 6 v25_rootfan_spider_runner_zneg "$ROOT_FAN" "leaf_basal_handle_attach leaf_basal_handle_micro_attach fern_frond_pinnae_attach" 2 z -1 0.58 22000 202605813 ;;
  vine_runner) run_case 7 v22_vine_runner_plantlet_ypos "$VINE_RUNNER" "crown_bud_attach crown_micro_fork_attach fern_frond_tip_attach" 2 y 1 0.64 18000 202605814 ;;
  rootnet) run_case 6 v24_rootnet_fern_rhizome_zpos "$ROOT_NETWORK" "fern_frond_pinnae_attach fern_recursive_frond_attach crown_micro_fork_attach" 2 z 1 0.54 24000 202605815 ;;
  sc_crown) run_case 7 v25_sc_crown_leaf_growth_ypos "$SC_CROWN" "crown_bud_attach crown_micro_fork_attach fern_frond_tip_attach" 2 y 1 0.54 24000 202605816 ;;
  metrics) metrics_all ;;
  status) status_all ;;
  *) echo "usage: $0 {start-first4|followup2|status|metrics|spider_raw|koru_raw|rootfan|vine_runner|rootnet|sc_crown}" >&2; exit 2 ;;
esac
