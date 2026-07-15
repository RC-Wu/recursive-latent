#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
OUT="$ROOT/results/publication_repair_remote_20260510b"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/tmp"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

mkdir -p "$OUT/logs" "$OUT/raw"

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
  local log="$OUT/logs/${case_name}.log"

  if [[ ! -f "$mesh" ]]; then
    echo "MISSING_MESH $mesh" | tee "$log"
    return 2
  fi

  echo "BEGIN $(date -Is) gpu=$gpu case=$case_name mesh=$mesh axis=$axis sign=$sign fit=$fit depths=$depths grammars=${grammars[*]}" | tee "$log"
  CUDA_VISIBLE_DEVICES="$gpu" "$MESHVAE_ENV/bin/python" \
    "$ROOT/assets/trellis2_recursive_slat_grammar_workflow.py" \
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
  echo "END $(date -Is) case=$case_name status=${PIPESTATUS[0]}" | tee -a "$log"
}

lane_tree() {
  local v25="$OUT/inputs/V25_lsys_root_fan_smooth_anchorD_stable.obj"
  local v23="$OUT/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles.obj"
  run_case 4 tree_v25_ypos "$v25" 3 0.58 18000 y 1 202605101 fork_side_attach compete_fork_attach
  run_case 4 tree_v25_yneg "$v25" 3 0.58 18000 y -1 202605102 fork_side_attach compete_fork_attach
  run_case 4 tree_v25_zpos "$v25" 3 0.58 18000 z 1 202605103 fork_side_attach compete_fork_attach
  run_case 4 tree_v25_zneg "$v25" 3 0.58 18000 z -1 202605104 fork_side_attach compete_fork_attach
  run_case 4 pine_v23_ypos "$v23" 3 0.60 18000 y 1 202605105 fork_side_attach compete_fork_attach
  run_case 4 pine_v23_yneg "$v23" 3 0.60 18000 y -1 202605106 fork_side_attach compete_fork_attach
}

lane_crown_stable() {
  local sc="$OUT/inputs/V25_sc_tree_crown_tapered_B.obj"
  run_case 5 sc_crown_ypos_portal "$sc" 3 0.54 18000 y 1 202605111 portal_attach compete_fork_attach
  run_case 5 sc_crown_yneg_portal "$sc" 3 0.54 18000 y -1 202605112 portal_attach compete_fork_attach
  run_case 5 sc_crown_zpos_portal "$sc" 3 0.54 18000 z 1 202605113 portal_attach compete_fork_attach
  run_case 5 sc_crown_zneg_portal "$sc" 3 0.54 18000 z -1 202605114 portal_attach compete_fork_attach
}

lane_crown_old() {
  local crown="$ROOT/results/siga_non_tree_root_sweep_20260508_1440/crown_radial_ornament/trellis2_dinov3_min.obj"
  run_case 6 old_crown_portal_ypos_fit034 "$crown" 2 0.34 14000 y 1 202605121 portal_attach
  run_case 6 old_crown_portal_yneg_fit034 "$crown" 2 0.34 14000 y -1 202605122 portal_attach
  run_case 6 old_crown_portal_ypos_fit040 "$crown" 2 0.40 16000 y 1 202605123 portal_attach
  run_case 6 old_crown_portal_yneg_fit040 "$crown" 2 0.40 16000 y -1 202605124 portal_attach
}

lane_arch_scifi() {
  local scifi="$ROOT/results/siga_non_tree_root_sweep_20260508_1440/scifi_mechanical_module/trellis2_dinov3_min.obj"
  local arch="$ROOT/results/siga_non_tree_root_sweep_20260508_1440/snow_architecture/trellis2_dinov3_min.obj"
  local ruin="$OUT/inputs/ruin_arch_portal_stage03.obj"
  run_case 7 scifi_translate_x_fit036 "$scifi" 2 0.36 16000 y 1 202605131 translate_x_attach portal_attach
  run_case 7 scifi_translate_x_fit044 "$scifi" 2 0.44 18000 y 1 202605132 translate_x_attach
  run_case 7 snow_arch_portal_ypos "$arch" 2 0.34 16000 y 1 202605133 portal_attach arch_portal_attach
  run_case 7 snow_arch_portal_yneg "$arch" 2 0.34 16000 y -1 202605134 portal_attach arch_portal_attach
  run_case 7 ruin_arch_portal_ypos "$ruin" 2 0.44 18000 y 1 202605135 portal_attach arch_portal_attach
}

case "${1:-all}" in
  tree) lane_tree ;;
  crown_stable) lane_crown_stable ;;
  crown_old) lane_crown_old ;;
  arch_scifi) lane_arch_scifi ;;
  all)
    lane_tree
    lane_crown_stable
    lane_crown_old
    lane_arch_scifi
    ;;
  *)
    echo "usage: $0 {tree|crown_stable|crown_old|arch_scifi|all}" >&2
    exit 2
    ;;
esac
