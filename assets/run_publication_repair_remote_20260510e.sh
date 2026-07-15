#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
OUT="$ROOT/results/publication_repair_remote_20260510e"
LOG="$OUT/logs"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

mkdir -p "$LOG" "$OUT/raw" "$OUT/pids" "$OUT/inputs" "$OUT/metrics"
mkdir -p "$ROOT/cache/local_tmp/publication_repair_remote_20260510e" \
  "$ROOT/cache/torch" "$ROOT/cache/xdg" "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/publication_repair_remote_20260510e"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/local_tmp/publication_repair_remote_20260510e"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

TREE_FLIPZ="$ROOT/results/publication_repair_remote_20260510/inputs/lsystem_tree_root_flip_z_crown_up.obj"
TREE_V25="$ROOT/results/publication_repair_remote_20260510b/inputs/V25_lsys_root_fan_smooth_anchorD_stable.obj"
CROWN_V25="$ROOT/inputs/strict_visual_matched_cases_V25_root_sc_refine_20260510/V25_sc_tree_crown_tapered_B/V25_sc_tree_crown_tapered_B.obj"
CROWN_OLD="$ROOT/results/siga_non_tree_root_sweep_20260508_1440/crown_radial_ornament/trellis2_dinov3_min.obj"
ORNAMENT_V24="$ROOT/inputs/strict_visual_matched_cases_V24_priority_rerun_20260510/V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA/V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA.obj"
SCIFI_OLD="$ROOT/results/siga_non_tree_root_sweep_20260508_1440/scifi_mechanical_module/trellis2_dinov3_min.obj"
SCIFI_CLEAN="$OUT/inputs/scifi_module_clean_recursive_v1.obj"
ARCH_CLEAN="$OUT/inputs/architectural_arch_portal_bridge_v1.obj"
ISLAND_CITY="$OUT/inputs/island_city_scale_down_stage03.obj"
SNOW_ARCH="$ROOT/results/siga_non_tree_root_sweep_20260508_1440/snow_architecture/trellis2_dinov3_min.obj"

write_manifest() {
  cat > "$OUT/root_anchor_manifest_20260510e.tsv" <<EOF
case	family	root_mesh	growth_axis	growth_sign	fit_scale	depths	max_tokens	grammar_role	grammars	seed	claim_gate
tree_flipz_zpos_micro	tree_root	$TREE_FLIPZ	z	1	0.60	2	18000	top crown frontier from flipped old root	crown_bud_attach crown_micro_fork_attach	202605501	structure screen only until render QA
tree_v25_zpos_micro	tree_root	$TREE_V25	z	1	0.58	2	18000	top frontier from V25 stable root	crown_bud_attach crown_micro_fork_attach	202605502	structure screen only until render QA
crown_tapered_zpos_rim	crown	$CROWN_V25	z	1	0.54	2	18000	rim/cap micro buds on SC crown	ornament_rim_micro_attach ornament_bud_attach	202605511	structure screen only until render QA
crown_old_zpos_rim	crown	$CROWN_OLD	z	1	0.36	2	16000	old crown root as failure-to-repair target	ornament_rim_micro_attach ornament_frontier_attach	202605512	likely appendix unless render improves
ornament_v24_zpos_rim	crown_ornament	$ORNAMENT_V24	z	1	0.50	1	18000	radial ornament rim detail	ornament_rim_micro_attach radial_frontier_attach	202605513	appendix/ornament backup
scifi_old_ypos_tight	hard_surface_proxy	$SCIFI_OLD	y	1	0.44	2	18000	side socket tight attach on old scifi root	socket_tight_attach socket_translate_attach	202605521	not tank/weapon; hard-surface proxy
scifi_clean_ypos_tight	hard_surface_proxy	$SCIFI_CLEAN	y	1	0.54	2	20000	side socket tight attach on clean scifi root	socket_tight_attach socket_translate_attach	202605522	not tank/weapon; hard-surface proxy
arch_clean_ypos_key	architecture_proxy	$ARCH_CLEAN	y	1	0.50	2	18000	keystone/top arch anchors	arch_keystone_attach portal_attach	202605531	architecture proxy, not city proof
snow_arch_zpos_key	architecture_proxy	$SNOW_ARCH	z	1	0.34	2	16000	keystone/top anchors on old snow arch	arch_keystone_attach	202605532	diagnostic unless visual arch reads clean
island_city_zpos_scale	city_proxy	$ISLAND_CITY	z	1	0.42	1	22000	rooftop/scale-down proxy anchors	city_rooftop_scale_attach scale_down_attach	202605533	city/LOD diagnostic only
EOF
}

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

  export TRITON_CACHE_DIR="$ROOT/cache/triton/publication_repair_remote_20260510e/gpu${gpu}"
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

lane_tree() {
  run_case 4 tree_flipz_zpos_micro "$TREE_FLIPZ" 2 0.60 18000 z 1 202605501 crown_bud_attach crown_micro_fork_attach
  run_case 4 tree_v25_zpos_micro "$TREE_V25" 2 0.58 18000 z 1 202605502 crown_bud_attach crown_micro_fork_attach
}

lane_crown() {
  run_case 5 crown_tapered_zpos_rim "$CROWN_V25" 2 0.54 18000 z 1 202605511 ornament_rim_micro_attach ornament_bud_attach
  run_case 5 crown_old_zpos_rim "$CROWN_OLD" 2 0.36 16000 z 1 202605512 ornament_rim_micro_attach ornament_frontier_attach
  run_case 5 ornament_v24_zpos_rim "$ORNAMENT_V24" 1 0.50 18000 z 1 202605513 ornament_rim_micro_attach radial_frontier_attach
}

lane_scifi() {
  run_case 6 scifi_old_ypos_tight "$SCIFI_OLD" 2 0.44 18000 y 1 202605521 socket_tight_attach socket_translate_attach
  run_case 6 scifi_clean_ypos_tight "$SCIFI_CLEAN" 2 0.54 20000 y 1 202605522 socket_tight_attach socket_translate_attach
}

lane_city_arch() {
  run_case 7 arch_clean_ypos_key "$ARCH_CLEAN" 2 0.50 18000 y 1 202605531 arch_keystone_attach portal_attach
  run_case 7 snow_arch_zpos_key "$SNOW_ARCH" 2 0.34 16000 z 1 202605532 arch_keystone_attach
  run_case 7 island_city_zpos_scale "$ISLAND_CITY" 1 0.42 22000 z 1 202605533 city_rooftop_scale_attach scale_down_attach
}

metrics() {
  mapfile -t meshes < <(find "$OUT/raw" -path '*/depth_0[12]/mesh.obj' -type f | sort)
  if [[ "${#meshes[@]}" -eq 0 ]]; then
    echo "NO_MESHES_FOR_METRICS" >&2
    return 1
  fi
  local case_args=()
  local mesh label
  for mesh in "${meshes[@]}"; do
    label="${mesh#$OUT/raw/}"
    label="${label%/mesh.obj}"
    label="${label//\//__}"
    case_args+=(--case "$label=$mesh")
  done
  "$PY" "$ROOT/assets/recursive_growth_mesh_metrics.py" \
    "${case_args[@]}" \
    --occupancy-resolution 64 \
    --out-json "$OUT/metrics/selected_metrics_20260510e.json" \
    --out-csv "$OUT/metrics/selected_metrics_20260510e.csv" 2>&1 | tee "$LOG/metrics.log"
}

start_all() {
  write_manifest
  nohup bash "$ROOT/assets/run_publication_repair_remote_20260510e.sh" tree > "$LOG/lane_tree.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/tree.pid"
  nohup bash "$ROOT/assets/run_publication_repair_remote_20260510e.sh" crown > "$LOG/lane_crown.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/crown.pid"
  nohup bash "$ROOT/assets/run_publication_repair_remote_20260510e.sh" scifi > "$LOG/lane_scifi.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/scifi.pid"
  nohup bash "$ROOT/assets/run_publication_repair_remote_20260510e.sh" city_arch > "$LOG/lane_city_arch.nohup.log" 2>&1 &
  echo "$!" > "$OUT/pids/city_arch.pid"
  echo "STARTED $(date -Is) pids=$(cat "$OUT"/pids/*.pid | tr '\n' ' ')"
}

case "${1:-start}" in
  start) start_all ;;
  tree) lane_tree ;;
  crown) lane_crown ;;
  scifi) lane_scifi ;;
  city_arch) lane_city_arch ;;
  metrics) metrics ;;
  manifest) write_manifest ;;
  *)
    echo "usage: $0 {start|tree|crown|scifi|city_arch|metrics|manifest}" >&2
    exit 2
    ;;
esac
