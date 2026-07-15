#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
T2="${T2:-/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/repos/TRELLIS.2}"
ENV_FILE="${ENV_FILE:-/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env}"
DINO="${DINO:-$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local}"
PY="${PY:-${MESHVAE_ENV:-}/bin/python}"
LOG_DIR="$ROOT/logs/public_guide_texturing_20260508"
OUT_ROOT="$ROOT/results/public_guide_textured_glb_20260508"

if [[ ! -x "$PY" ]]; then
  # PATHS.new_a100.env defines MESHVAE_ENV; source it when PY was not injected.
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  PY="${MESHVAE_ENV}/bin/python"
fi

mkdir -p "$LOG_DIR" "$OUT_ROOT" "$ROOT/tmp" "$ROOT/triton_cache" "$ROOT/mpl_cache"

export PYTHONPATH="$ROOT/assets:$T2:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export XDG_CACHE_HOME="$ROOT/.cache"
export TORCH_HOME="$ROOT/torch_home"
export TRITON_CACHE_DIR="$ROOT/triton_cache"
export TMPDIR="$ROOT/tmp"
export MPLCONFIGDIR="$ROOT/mpl_cache"
export ATTN_BACKEND="${ATTN_BACKEND:-xformers}"
export SPARSE_ATTN_BACKEND="${SPARSE_ATTN_BACKEND:-xformers}"

run_case() {
  local gpu="$1"
  local name="$2"
  local mesh="$3"
  local guide="$4"
  local steps="${5:-4}"
  local seed="${6:-7351}"
  local out="$OUT_ROOT/${name}_steps${steps}_xformers"
  local log="$LOG_DIR/${name}_steps${steps}_gpu${gpu}.log"

  if [[ -f "$out/textured.glb" && -f "$out/summary.json" ]]; then
    echo "skip existing $name -> $out"
    return 0
  fi

  echo "launch $name gpu=$gpu log=$log out=$out"
  CUDA_VISIBLE_DEVICES="$gpu" nohup "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
    --mesh "$mesh" \
    --image "$guide" \
    --dinov3-model "$DINO" \
    --out "$out" \
    --steps "$steps" \
    --seed "$seed" \
    --resolution 512 \
    --texture-size 1024 \
    --preprocess \
    > "$log" 2>&1 &
  echo "$!" > "$LOG_DIR/${name}_steps${steps}_gpu${gpu}.pid"
}

case "${1:-launch}" in
  launch)
    run_case 5 \
      "tree_compete_d4_pruned_tree_roots_arlington_square" \
      "$ROOT/selected_meshes_for_texture_20260508/tree_compete_d4_pruned.obj" \
      "$ROOT/public_guides_20260508/processed/tree_roots_arlington_square.png" \
      4 7353
    run_case 6 \
      "ruin_arch_portal_stage03_washington_square_arch_square" \
      "$ROOT/selected_meshes_for_texture_20260508/ruin_arch_portal_stage03.obj" \
      "$ROOT/public_guides_20260508/processed/washington_square_arch_square.png" \
      4 7354
    run_case 7 \
      "porous_container_compete_stage03_bismuth_crystal_square" \
      "$ROOT/selected_meshes_for_texture_20260508/porous_container_compete_stage03.obj" \
      "$ROOT/public_guides_20260508/processed/bismuth_crystal_square.png" \
      4 7355
    ;;
  status)
    echo "processes:"
    pgrep -af "trellis2_texturing_export_glb" || true
    echo "outputs:"
    find "$OUT_ROOT" -maxdepth 2 -type f \( -name textured.glb -o -name summary.json \) -printf "%TY-%Tm-%Td %TH:%TM %s %p\n" | sort | tail -30
    echo "logs:"
    find "$LOG_DIR" -maxdepth 1 -type f -name "*.log" -printf "%TY-%Tm-%Td %TH:%TM %s %p\n" | sort | tail -12
    ;;
  *)
    echo "usage: $0 [launch|status]" >&2
    exit 2
    ;;
esac
