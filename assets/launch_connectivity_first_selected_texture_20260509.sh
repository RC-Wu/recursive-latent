#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-connectivity_first_selected_texture_20260509_rerun1705}"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

LOG="$ROOT/logs/$RUN"
OUT="$ROOT/results/$RUN"
GUIDE_ROOT="$ROOT/public_guides_20260508/processed"
mkdir -p "$LOG" "$OUT" \
  "$ROOT/cache/tmp" "$ROOT/cache/torch" "$ROOT/cache/xdg" \
  "$ROOT/cache/matplotlib" "$ROOT/cache/torch_extensions" "$ROOT/cache/triton/$RUN"

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/tmp"
export TEMP="$ROOT/cache/tmp"
export TMP="$ROOT/cache/tmp"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export SPARSE_ATTN_BACKEND=xformers
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"

run_case() {
  local gpu="$1"
  local label="$2"
  local mesh="$3"
  local guide="$4"
  local steps="$5"
  local tex="$6"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"
  echo "=== START $label gpu=$gpu steps=$steps tex=$tex mesh=$mesh guide=$guide $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
    --mesh "$mesh" \
    --image "$GUIDE_ROOT/$guide" \
    --dinov3-model "$DINO" \
    --out "$OUT/${label}_steps${steps}_tex${tex}_xformers" \
    --steps "$steps" \
    --seed 905091705 \
    --resolution 512 \
    --texture-size "$tex" \
    --preprocess
  echo "=== END $label $(date)"
}

if [[ "${1:-}" == "--worker" ]]; then
  run_case "$2" "$3" "$4" "$5" "$6" "$7"
  exit 0
fi

BASE="$ROOT/results/connectivity_first_dla_crystal_20260509_bridgefix_grid"

declare -a CASES=(
  "4 dla_best_pyrite $BASE/gpu4_dla_raw_vs_sparse/dla_voxel_root/fork_side_attach/raw_bridge_smooth/stage_01/projected/mesh_projected.obj pyrite_cubes_square.png 6 1536"
  "5 bismuth_best_bismuth $BASE/gpu6_crystal_radial/porous_bismuth_crystal_proxy/fork_side_attach/mesh_bridge_smooth/stage_01/projected/mesh_projected.obj bismuth_crystal_square.png 6 1536"
  "6 radial_bismuth_pyrite $BASE/gpu6_crystal_radial/porous_bismuth_crystal_proxy/radial/raw_bridge_smooth/stage_01/projected/mesh_projected.obj pyrite_cubes_square.png 6 1536"
  "7 dla_side_octopus $BASE/gpu5_dla_extra_lowtoken/dla_side_extra/fork_side_attach/sparse_close_bridge/stage_01/projected/mesh_projected.obj octopus_suckers_square.png 6 1536"
)

for spec in "${CASES[@]}"; do
  read -r gpu label mesh guide steps tex <<<"$spec"
  script="$LOG/run_gpu${gpu}_${label}.sh"
  {
    echo "#!/usr/bin/env bash"
    echo "set -euo pipefail"
    printf 'ROOT=%q RUN=%q bash %q --worker %q %q %q %q %q %q\n' \
      "$ROOT" "$RUN" "$ROOT/assets/launch_connectivity_first_selected_texture_20260509.sh" \
      "$gpu" "$label" "$mesh" "$guide" "$steps" "$tex"
  } > "$script"
  chmod +x "$script"
  nohup "$script" > "$LOG/gpu${gpu}_${label}.log" 2>&1 &
  echo "gpu${gpu}_${label}:$!"
done

sleep 3
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | sed -n '5,8p'
for f in "$LOG"/gpu*.log; do
  echo "==== $(basename "$f")"
  tail -12 "$f" || true
done
