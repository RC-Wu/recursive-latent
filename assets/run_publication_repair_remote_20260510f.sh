#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
SRC="$ROOT/results/publication_repair_remote_20260510e/raw"
OUT="$ROOT/results/publication_repair_remote_20260510f"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$LOG" "$OUT/pids" "$OUT/pruned" "$OUT/textured" "$OUT/metrics"
mkdir -p "$ROOT/cache/local_tmp/publication_repair_remote_20260510f" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/publication_repair_remote_20260510f"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/publication_repair_remote_20260510f"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"
SPKY="$ROOT/public_guides_20260508/processed/spiky_plant_tendril_square.png"
ROOTGUIDE="$ROOT/inputs/strict_visual_matched_cases_V25_root_sc_refine_20260510/_guides/V23_lsystem_root_fan_grammar_pbr_guide.png"
ORNAMENT="$ROOT/inputs/strict_visual_matched_cases_V25_root_sc_refine_20260510/_guides/V23_ifs_radial_ornament_pbr_guide.png"
METAL="$ROOT/inputs/strict_visual_matched_cases_v4_20260510/_guides/v4_dark_radial_gear_pbr_guide.png"
STONE="$ROOT/inputs/strict_visual_matched_cases_V21_ifs_transform_natural_20260510/_guides/V21_escher_recursive_stairs_stone_pbr_guide.png"

TREE_V25_D1="$SRC/tree_v25_zpos_micro/crown_bud_attach/depth_01/mesh.obj"
TREE_FLIPZ_D2="$SRC/tree_flipz_zpos_micro/crown_bud_attach/depth_02/mesh.obj"
CROWN_OLD_RIM_D1="$SRC/crown_old_zpos_rim/ornament_rim_micro_attach/depth_01/mesh.obj"
CROWN_TAPERED_RIM_D1="$SRC/crown_tapered_zpos_rim/ornament_rim_micro_attach/depth_01/mesh.obj"
ORNAMENT_V24_RIM_D1="$SRC/ornament_v24_zpos_rim/ornament_rim_micro_attach/depth_01/mesh.obj"
SCIFI_OLD_TIGHT_D1="$SRC/scifi_old_ypos_tight/socket_tight_attach/depth_01/mesh.obj"
SCIFI_CLEAN_TRANSLATE_D2="$SRC/scifi_clean_ypos_tight/socket_translate_attach/depth_02/mesh.obj"
ARCH_CLEAN_KEY_D2="$SRC/arch_clean_ypos_key/arch_keystone_attach/depth_02/mesh.obj"
SNOW_ARCH_KEY_D1="$SRC/snow_arch_zpos_key/arch_keystone_attach/depth_01/mesh.obj"

cat > "$OUT/selected_texture_manifest_20260510f.tsv" <<EOF
label	source_mesh	guide	gpu	seed	status_gate	claim_scope
tree_v25_bud_d1_spiky_pruned	$TREE_V25_D1	$SPKY	4	202605601	pending_texture_render_metric_QA	paper_candidate_tree_root_repair
tree_v25_bud_d1_root_pruned	$TREE_V25_D1	$ROOTGUIDE	4	202605602	pending_texture_render_metric_QA	paper_candidate_tree_root_repair_alt_material
crown_old_rim_d1_ornament_pruned	$CROWN_OLD_RIM_D1	$ORNAMENT	5	202605611	pending_texture_render_metric_QA	appendix_or_crown_repair_candidate
ornament_v24_rim_d1_ornament_raw	$ORNAMENT_V24_RIM_D1	$ORNAMENT	5	202605612	pending_texture_render_metric_QA	appendix_positive_ornament_candidate
crown_tapered_rim_d1_ornament_pruned	$CROWN_TAPERED_RIM_D1	$ORNAMENT	5	202605613	pending_texture_render_metric_QA	appendix_crown_candidate_if_visual_improves
scifi_old_tight_d1_metal_pruned	$SCIFI_OLD_TIGHT_D1	$METAL	6	202605621	pending_texture_render_metric_QA	hard_surface_proxy_not_tank_weapon
scifi_clean_translate_d2_metal_pruned	$SCIFI_CLEAN_TRANSLATE_D2	$METAL	6	202605622	pending_texture_render_metric_QA	hard_surface_proxy_backup
arch_clean_key_d2_stone_pruned	$ARCH_CLEAN_KEY_D2	$STONE	7	202605631	pending_texture_render_metric_QA	architecture_proxy_not_city_proof
snow_arch_key_d1_stone_pruned	$SNOW_ARCH_KEY_D1	$STONE	7	202605632	pending_texture_render_metric_QA	diagnostic_architecture_backup
EOF

ensure_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "MISSING $path" >&2
    return 2
  fi
}

prune_one() {
  local label="$1"
  local mesh="$2"
  local min_faces="${3:-8}"
  local min_area_ratio="${4:-5e-7}"
  local keep_top="${5:-0}"
  local out_dir="$OUT/pruned/$label"
  local log="$LOG/prune_${label}.log"
  ensure_file "$mesh"
  mkdir -p "$out_dir"
  echo "PRUNE_BEGIN $(date -Is) label=$label mesh=$mesh min_faces=$min_faces min_area_ratio=$min_area_ratio" | tee "$log"
  "$PY" "$ROOT/assets/prune_small_mesh_components_20260510.py" \
    --case "$label=$mesh" \
    --out-dir "$out_dir" \
    --min-faces "$min_faces" \
    --min-area-ratio "$min_area_ratio" \
    --keep-top "$keep_top" 2>&1 | tee -a "$log"
  echo "$out_dir/$label.obj"
}

texture_case() {
  local gpu="$1"
  local label="$2"
  local mesh="$3"
  local guide="$4"
  local seed="$5"
  local steps="${6:-8}"
  local tex="${7:-2048}"
  local target="$OUT/textured/${label}_steps${steps}_tex${tex}_seed${seed}_xformers"
  local log="$LOG/texture_${label}.log"

  ensure_file "$mesh"
  ensure_file "$guide"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/publication_repair_remote_20260510f/gpu${gpu}"
  mkdir -p "$TRITON_CACHE_DIR" "$target"
  echo "TEXTURE_BEGIN $(date -Is) gpu=$gpu label=$label mesh=$mesh guide=$guide" | tee "$log"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
    --mesh "$mesh" \
    --image "$guide" \
    --dinov3-model "$DINO" \
    --out "$target" \
    --steps "$steps" \
    --seed "$seed" \
    --resolution 512 \
    --texture-size "$tex" \
    --preprocess 2>&1 | tee -a "$log"
  local status=${PIPESTATUS[0]}
  echo "TEXTURE_END $(date -Is) label=$label status=$status" | tee -a "$log"
  return "$status"
}

metrics_selected() {
  local log="$LOG/metrics_selected.log"
  "$PY" "$ROOT/assets/recursive_growth_mesh_metrics.py" \
    --case "tree_v25_bud_d1=$TREE_V25_D1" \
    --case "tree_flipz_bud_d2=$TREE_FLIPZ_D2" \
    --case "crown_old_rim_d1=$CROWN_OLD_RIM_D1" \
    --case "crown_tapered_rim_d1=$CROWN_TAPERED_RIM_D1" \
    --case "ornament_v24_rim_d1=$ORNAMENT_V24_RIM_D1" \
    --case "scifi_old_tight_d1=$SCIFI_OLD_TIGHT_D1" \
    --case "scifi_clean_translate_d2=$SCIFI_CLEAN_TRANSLATE_D2" \
    --case "arch_clean_key_d2=$ARCH_CLEAN_KEY_D2" \
    --case "snow_arch_key_d1=$SNOW_ARCH_KEY_D1" \
    --out-json "$OUT/metrics/selected_texture_source_metrics_20260510f.json" \
    --out-csv "$OUT/metrics/selected_texture_source_metrics_20260510f.csv" 2>&1 | tee "$log"
}

lane_tree() {
  local tree_pruned
  tree_pruned="$(prune_one tree_v25_bud_d1_pruned "$TREE_V25_D1" 4 2e-7 0 | tail -n 1)"
  texture_case 4 tree_v25_bud_d1_spiky_pruned "$tree_pruned" "$SPKY" 202605601 8 2048
  texture_case 4 tree_v25_bud_d1_root_pruned "$tree_pruned" "$ROOTGUIDE" 202605602 8 2048
}

lane_crown() {
  local crown_old_pruned crown_tapered_pruned
  crown_old_pruned="$(prune_one crown_old_rim_d1_pruned "$CROWN_OLD_RIM_D1" 8 5e-7 0 | tail -n 1)"
  crown_tapered_pruned="$(prune_one crown_tapered_rim_d1_pruned "$CROWN_TAPERED_RIM_D1" 8 5e-7 0 | tail -n 1)"
  texture_case 5 crown_old_rim_d1_ornament_pruned "$crown_old_pruned" "$ORNAMENT" 202605611 8 2048
  texture_case 5 ornament_v24_rim_d1_ornament_raw "$ORNAMENT_V24_RIM_D1" "$ORNAMENT" 202605612 8 2048
  texture_case 5 crown_tapered_rim_d1_ornament_pruned "$crown_tapered_pruned" "$ORNAMENT" 202605613 8 2048
}

lane_scifi() {
  local scifi_old_pruned scifi_clean_pruned
  scifi_old_pruned="$(prune_one scifi_old_tight_d1_pruned "$SCIFI_OLD_TIGHT_D1" 12 8e-7 0 | tail -n 1)"
  scifi_clean_pruned="$(prune_one scifi_clean_translate_d2_pruned "$SCIFI_CLEAN_TRANSLATE_D2" 12 8e-7 0 | tail -n 1)"
  texture_case 6 scifi_old_tight_d1_metal_pruned "$scifi_old_pruned" "$METAL" 202605621 8 2048
  texture_case 6 scifi_clean_translate_d2_metal_pruned "$scifi_clean_pruned" "$METAL" 202605622 8 2048
}

lane_arch() {
  local arch_clean_pruned snow_arch_pruned
  arch_clean_pruned="$(prune_one arch_clean_key_d2_pruned "$ARCH_CLEAN_KEY_D2" 12 8e-7 0 | tail -n 1)"
  snow_arch_pruned="$(prune_one snow_arch_key_d1_pruned "$SNOW_ARCH_KEY_D1" 12 8e-7 0 | tail -n 1)"
  texture_case 7 arch_clean_key_d2_stone_pruned "$arch_clean_pruned" "$STONE" 202605631 8 2048
  texture_case 7 snow_arch_key_d1_stone_pruned "$snow_arch_pruned" "$STONE" 202605632 8 2048
}

start_all() {
  metrics_selected || true
  nohup bash "$ROOT/assets/run_publication_repair_remote_20260510f.sh" tree > "$LOG/lane_tree.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/tree.pid"
  nohup bash "$ROOT/assets/run_publication_repair_remote_20260510f.sh" crown > "$LOG/lane_crown.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/crown.pid"
  nohup bash "$ROOT/assets/run_publication_repair_remote_20260510f.sh" scifi > "$LOG/lane_scifi.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/scifi.pid"
  nohup bash "$ROOT/assets/run_publication_repair_remote_20260510f.sh" arch > "$LOG/lane_arch.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/arch.pid"
  echo "STARTED $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

status_all() {
  echo "STATUS $(date -Is)"
  if [[ -d "$OUT/pids" ]]; then
    for pid_file in "$OUT"/pids/*.pid; do
      [[ -f "$pid_file" ]] || continue
      pid="$(cat "$pid_file")"
      if kill -0 "$pid" 2>/dev/null; then
        echo "RUNNING $(basename "$pid_file" .pid) pid=$pid"
      else
        echo "DONE_OR_EXITED $(basename "$pid_file" .pid) pid=$pid"
      fi
    done
  fi
  find "$OUT/textured" -maxdepth 2 -name summary.json -print 2>/dev/null | sort | while read -r summary; do
    "$PY" - <<'PY' "$summary"
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
d = json.loads(p.read_text())
print(f"SUMMARY {p.parent.name} status={d.get('status')} glb_bytes={d.get('glb_bytes')} error={d.get('error')}")
PY
  done
}

case "${1:-start}" in
  start) start_all ;;
  tree) lane_tree ;;
  crown) lane_crown ;;
  scifi) lane_scifi ;;
  arch) lane_arch ;;
  metrics) metrics_selected ;;
  status) status_all ;;
  *)
    echo "usage: $0 {start|tree|crown|scifi|arch|metrics|status}" >&2
    exit 2
    ;;
esac
