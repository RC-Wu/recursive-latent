#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/publication_repair_remote_20260510d"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$LOG" "$OUT/raw" "$OUT/pids" "$OUT/tree_pruned" "$OUT/textured_tree_pruned"
mkdir -p "$ROOT/cache/local_tmp/publication_repair_remote_20260510d" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/publication_repair_remote_20260510d"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/publication_repair_remote_20260510d"
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
METAL="$ROOT/inputs/strict_visual_matched_cases_v4_20260510/_guides/v4_dark_radial_gear_pbr_guide.png"
STONE="$ROOT/inputs/strict_visual_matched_cases_V21_ifs_transform_natural_20260510/_guides/V21_escher_recursive_stairs_stone_pbr_guide.png"
ORNAMENT="$ROOT/inputs/strict_visual_matched_cases_V25_root_sc_refine_20260510/_guides/V23_ifs_radial_ornament_pbr_guide.png"

run_case() {
  local gpu="$1"
  local case_name="$2"
  local mesh="$3"
  local depths="$4"
  local fit="$5"
  local max_tokens="$6"
  local axis="$7"
  local sign="$8"
  local seed="$9"
  shift 9
  local grammars=("$@")
  local log="$LOG/${case_name}.log"

  if [[ ! -f "$mesh" ]]; then
    echo "MISSING_MESH $mesh" | tee "$log"
    return 2
  fi

  export TRITON_CACHE_DIR="$ROOT/cache/triton/publication_repair_remote_20260510d/gpu${gpu}"
  mkdir -p "$TRITON_CACHE_DIR"
  echo "BEGIN $(date -Is) gpu=$gpu case=$case_name mesh=$mesh axis=$axis sign=$sign fit=$fit depths=$depths grammars=${grammars[*]}" | tee "$log"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_recursive_slat_grammar_workflow.py" \
    --mesh "$mesh" \
    --out "$OUT/raw/$case_name" \
    --case-name "$case_name" \
    --grammars "${grammars[@]}" \
    --depths "$depths" \
    --fit-scale "$fit" \
    --max-tokens "$max_tokens" \
    --seed "$seed" \
    --growth-axis "$axis" \
    --growth-sign "$sign" 2>&1 | tee -a "$log"
  local status=${PIPESTATUS[0]}
  echo "END $(date -Is) case=$case_name status=$status" | tee -a "$log"
  return "$status"
}

texture_case() {
  local gpu="$1"
  local label="$2"
  local mesh="$3"
  local guide="$4"
  local seed="$5"
  local steps="${6:-8}"
  local tex="${7:-2048}"
  local target="$OUT/textured_tree_pruned/${label}_steps${steps}_tex${tex}_seed${seed}_xformers"
  local log="$LOG/texture_${label}.log"

  export TRITON_CACHE_DIR="$ROOT/cache/triton/publication_repair_remote_20260510d/gpu${gpu}"
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

lane_tree_cleanup() {
  local src="$ROOT/results/publication_repair_remote_20260510c/raw/tree_v25_zpos_micro/crown_bud_attach/depth_02/mesh.obj"
  local prune_log="$LOG/tree_cleanup_prune.log"
  echo "TREE_CLEANUP_BEGIN $(date -Is) src=$src" | tee "$prune_log"
  "$PY" "$ROOT/assets/prune_small_mesh_components_20260510.py" \
    --case "tree_zpos_bud_d2_min8=$src" \
    --out-dir "$OUT/tree_pruned/min8" \
    --min-faces 8 --min-area-ratio 5e-7 --keep-top 0 2>&1 | tee -a "$prune_log"
  "$PY" "$ROOT/assets/prune_small_mesh_components_20260510.py" \
    --case "tree_zpos_bud_d2_min16=$src" \
    --out-dir "$OUT/tree_pruned/min16" \
    --min-faces 16 --min-area-ratio 1e-6 --keep-top 0 2>&1 | tee -a "$prune_log"
  "$PY" "$ROOT/assets/prune_small_mesh_components_20260510.py" \
    --case "tree_zpos_bud_d2_min32=$src" \
    --out-dir "$OUT/tree_pruned/min32" \
    --min-faces 32 --min-area-ratio 2e-6 --keep-top 0 2>&1 | tee -a "$prune_log"

  "$PY" "$ROOT/assets/recursive_growth_mesh_metrics.py" \
    --case "tree_zpos_bud_d2_raw=$src" \
    --case "tree_zpos_bud_d2_min8=$OUT/tree_pruned/min8/tree_zpos_bud_d2_min8.obj" \
    --case "tree_zpos_bud_d2_min16=$OUT/tree_pruned/min16/tree_zpos_bud_d2_min16.obj" \
    --case "tree_zpos_bud_d2_min32=$OUT/tree_pruned/min32/tree_zpos_bud_d2_min32.obj" \
    --out-json "$OUT/metrics_tree_pruned.json" \
    --out-csv "$OUT/metrics_tree_pruned.csv" 2>&1 | tee "$LOG/tree_cleanup_metrics.log"

  texture_case 4 tree_zpos_bud_d2_min8_spiky "$OUT/tree_pruned/min8/tree_zpos_bud_d2_min8.obj" "$SPKY" 202605401 8 2048
  texture_case 4 tree_zpos_bud_d2_min16_spiky "$OUT/tree_pruned/min16/tree_zpos_bud_d2_min16.obj" "$SPKY" 202605402 8 2048
  texture_case 4 tree_zpos_bud_d2_min8_root "$OUT/tree_pruned/min8/tree_zpos_bud_d2_min8.obj" "$ROOTGUIDE" 202605403 8 2048
  echo "TREE_CLEANUP_DONE $(date -Is)" | tee -a "$prune_log"
}

lane_crown() {
  local old="$ROOT/results/siga_non_tree_root_sweep_20260508_1440/crown_radial_ornament/trellis2_dinov3_min.obj"
  local stable="$ROOT/results/publication_repair_remote_20260510b/inputs/V25_sc_tree_crown_tapered_B.obj"
  run_case 5 crown_old_masked_ypos_fit036 "$old" 2 0.36 16000 y 1 202605411 ornament_bud_attach ornament_frontier_attach radial_frontier_attach
  run_case 5 crown_old_masked_zpos_fit036 "$old" 2 0.36 16000 z 1 202605412 ornament_bud_attach ornament_frontier_attach radial_frontier_attach
  run_case 5 crown_stable_masked_ypos_fit054 "$stable" 2 0.54 18000 y 1 202605413 ornament_bud_attach ornament_frontier_attach
}

lane_scifi() {
  local scifi="$ROOT/results/siga_non_tree_root_sweep_20260508_1440/scifi_mechanical_module/trellis2_dinov3_min.obj"
  run_case 6 scifi_socket_ypos_fit044 "$scifi" 2 0.44 18000 y 1 202605421 socket_translate_attach translate_x_attach
  run_case 6 scifi_socket_ypos_fit052 "$scifi" 2 0.52 20000 y 1 202605422 socket_translate_attach translate_x_attach
  run_case 6 scifi_socket_zpos_fit044 "$scifi" 2 0.44 18000 z 1 202605423 socket_translate_attach
}

lane_arch() {
  local snow="$ROOT/results/siga_non_tree_root_sweep_20260508_1440/snow_architecture/trellis2_dinov3_min.obj"
  local ruin="$ROOT/results/publication_repair_remote_20260510b/inputs/ruin_arch_portal_stage03.obj"
  run_case 7 snow_arch_keystone_ypos_fit034 "$snow" 2 0.34 16000 y 1 202605431 arch_keystone_attach arch_portal_attach portal_attach
  run_case 7 snow_arch_keystone_zpos_fit034 "$snow" 2 0.34 16000 z 1 202605432 arch_keystone_attach arch_portal_attach
  run_case 7 ruin_arch_keystone_ypos_fit044 "$ruin" 2 0.44 18000 y 1 202605433 arch_keystone_attach portal_attach
}

start_all() {
  nohup bash "$ROOT/assets/run_publication_repair_remote_20260510d.sh" tree_cleanup > "$LOG/lane_tree_cleanup.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/tree_cleanup.pid"
  nohup bash "$ROOT/assets/run_publication_repair_remote_20260510d.sh" crown > "$LOG/lane_crown.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/crown.pid"
  nohup bash "$ROOT/assets/run_publication_repair_remote_20260510d.sh" scifi > "$LOG/lane_scifi.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/scifi.pid"
  nohup bash "$ROOT/assets/run_publication_repair_remote_20260510d.sh" arch > "$LOG/lane_arch.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/arch.pid"
  echo "STARTED $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start}" in
  start) start_all ;;
  tree_cleanup) lane_tree_cleanup ;;
  crown) lane_crown ;;
  scifi) lane_scifi ;;
  arch) lane_arch ;;
  *)
    echo "usage: $0 {start|tree_cleanup|crown|scifi|arch}" >&2
    exit 2
    ;;
esac
