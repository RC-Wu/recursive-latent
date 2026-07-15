#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/fern_leaf_recursive_remote_20260511f"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$OUT/raw" "$OUT/pids" "$OUT/metrics" "$LOG" \
  "$ROOT/cache/local_tmp/fern_leaf_recursive_remote_20260511f" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/fern_leaf_recursive_remote_20260511f"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/fern_leaf_recursive_remote_20260511f"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

FERN_ARCH="$ROOT/results/fern_root_candidates_20260511/fern_compound_frond_arch_a/fern_compound_frond_arch_a.obj"
FERN_LACY="$ROOT/results/fern_root_candidates_20260511/fern_compound_frond_lacy_b/fern_compound_frond_lacy_b.obj"
SPIDER_ROSETTE="$ROOT/results/fern_root_candidates_20260511/spider_rosette_strapleaf_a/spider_rosette_strapleaf_a.obj"
FIDDLE_OPEN="$ROOT/results/fern_root_candidates_20260511/fiddlehead_crozier_open_a/fiddlehead_crozier_open_a.obj"
ROOT_VINE="$ROOT/results/fern_root_candidates_20260511/root_vine_fallback_web_a/root_vine_fallback_web_a.obj"

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
  export TRITON_CACHE_DIR="$ROOT/cache/triton/fern_leaf_recursive_remote_20260511f/gpu${gpu}_${label}"
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
  cat > "$OUT/fern_leaf_recursive_manifest_20260511f.tsv" <<TSV
label	gpu	mesh	grammars	depths	growth_axis	growth_sign	fit_scale	max_tokens	seed	claim_scope
fern_arch_yneg	4	$FERN_ARCH	v25e_crown_bud_micro v25e_rim_leaflet_micro v25e_crown_tiplet_short	3	y	-1	0.62	16000	202605831	compound fern frond root; primary axis follows original +z tip mapped to latent y negative
fern_lacy_yneg	5	$FERN_LACY	v25e_crown_bud_micro v25e_rim_leaflet_micro v25e_crown_tiplet_short	3	y	-1	0.62	16000	202605832	lacy compound fern frond root; primary axis follows original +z tip mapped to latent y negative
spider_rosette_zpos	6	$SPIDER_ROSETTE	v25e_root_basal_micro v25e_root_rim_tiplet v25e_root_crown_micro	3	z	1	0.60	16000	202605833	spider rosette root; basal/vertical growth probe
fiddle_open_yneg	7	$FIDDLE_OPEN	v25e_crown_bud_micro v25e_rim_leaflet_micro fern_spiral_echo_attach	3	y	-1	0.62	16000	202605834	fiddlehead/crozier root; tip and spiral echo probe
fern_arch_zpos_control	4	$FERN_ARCH	v25e_crown_bud_micro v25e_rim_leaflet_micro	2	z	1	0.62	16000	202605835	axis/sign control for fern arch
spider_rosette_ypos_control	6	$SPIDER_ROSETTE	v25e_root_basal_micro v25e_root_rim_tiplet	2	y	1	0.60	16000	202605836	axis/sign control for spider rosette
root_vine_ypos_fallback	7	$ROOT_VINE	v25e_crown_bud_micro v25e_root_rim_tiplet v25e_root_crown_micro	3	y	1	0.64	16000	202605837	connected root-vine fallback if fern/spider roots decode poorly
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
    --out-json "$OUT/metrics/fern_leaf_recursive_metrics_20260511f.json" \
    --out-csv "$OUT/metrics/fern_leaf_recursive_metrics_20260511f.csv" \
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

start_main4() {
  write_manifest
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511f.sh" fern_arch > "$LOG/lane_fern_arch.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fern_arch.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511f.sh" fern_lacy > "$LOG/lane_fern_lacy.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fern_lacy.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511f.sh" spider > "$LOG/lane_spider.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/spider.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511f.sh" fiddle > "$LOG/lane_fiddle.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fiddle.pid"
  echo "STARTED_MAIN4 $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

start_controls() {
  write_manifest
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511f.sh" fern_arch_control > "$LOG/lane_fern_arch_control.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/fern_arch_control.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511f.sh" spider_control > "$LOG/lane_spider_control.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/spider_control.pid"
  nohup bash "$ROOT/assets/run_fern_leaf_recursive_remote_20260511f.sh" root_vine > "$LOG/lane_root_vine.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/root_vine.pid"
  echo "STARTED_CONTROLS $(date -Is) pids=$(cat "$OUT"/pids/fern_arch_control.pid "$OUT"/pids/spider_control.pid "$OUT"/pids/root_vine.pid | tr '\n' ' ')"
}

case "${1:-start-main4}" in
  start|start-main4) start_main4 ;;
  controls|start-controls) start_controls ;;
  fern_arch) run_case 4 fern_arch_yneg "$FERN_ARCH" "v25e_crown_bud_micro v25e_rim_leaflet_micro v25e_crown_tiplet_short" 3 y -1 0.62 16000 202605831 ;;
  fern_lacy) run_case 5 fern_lacy_yneg "$FERN_LACY" "v25e_crown_bud_micro v25e_rim_leaflet_micro v25e_crown_tiplet_short" 3 y -1 0.62 16000 202605832 ;;
  spider) run_case 6 spider_rosette_zpos "$SPIDER_ROSETTE" "v25e_root_basal_micro v25e_root_rim_tiplet v25e_root_crown_micro" 3 z 1 0.60 16000 202605833 ;;
  fiddle) run_case 7 fiddle_open_yneg "$FIDDLE_OPEN" "v25e_crown_bud_micro v25e_rim_leaflet_micro fern_spiral_echo_attach" 3 y -1 0.62 16000 202605834 ;;
  fern_arch_control) run_case 4 fern_arch_zpos_control "$FERN_ARCH" "v25e_crown_bud_micro v25e_rim_leaflet_micro" 2 z 1 0.62 16000 202605835 ;;
  spider_control) run_case 6 spider_rosette_ypos_control "$SPIDER_ROSETTE" "v25e_root_basal_micro v25e_root_rim_tiplet" 2 y 1 0.60 16000 202605836 ;;
  root_vine) run_case 7 root_vine_ypos_fallback "$ROOT_VINE" "v25e_crown_bud_micro v25e_root_rim_tiplet v25e_root_crown_micro" 3 y 1 0.64 16000 202605837 ;;
  metrics) metrics_all ;;
  status) status_all ;;
  *) echo "usage: $0 {start-main4|controls|status|metrics|fern_arch|fern_lacy|spider|fiddle|fern_arch_control|spider_control|root_vine}" >&2; exit 2 ;;
esac
