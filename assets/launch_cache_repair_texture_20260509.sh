#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-cache_repair_texture_20260509}"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

LOG="$ROOT/logs/$RUN"
OUT="$ROOT/results/$RUN"
INPUT_ROOT="$ROOT/inputs/cache_repair_selected_20260509"
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
GUIDE_ROOT="$ROOT/public_guides_20260508/processed"

run_case() {
  local gpu="$1"
  local label="$2"
  local mesh_name="$3"
  local guide_name="$4"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"
  echo "=== START $label gpu=$gpu mesh=$mesh_name guide=$guide_name $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
    --mesh "$INPUT_ROOT/$mesh_name" \
    --image "$GUIDE_ROOT/$guide_name" \
    --dinov3-model "$DINO" \
    --out "$OUT/${label}_steps8_tex2048_xformers" \
    --steps 8 \
    --seed 9050917 \
    --resolution 512 \
    --texture-size 2048 \
    --preprocess
  echo "=== END $label $(date)"
}

if [[ "${1:-}" == "--worker" ]]; then
  run_case "$2" "$3" "$4" "$5"
  exit 0
fi

declare -a CASES=(
  "4 repaired_dla_voxel_bridge repaired_dla_voxel_bridge_close_simplify.obj octopus_suckers_square.png"
  "5 repaired_radial_voxel_bridge repaired_radial_voxel_bridge_close_simplify.obj gear_train_square.png"
  "6 repaired_bismuth_bridge repaired_bismuth_bridge_to_largest.obj bismuth_crystal_square.png"
  "7 repaired_scifi_bridge repaired_scifi_bridge_to_largest.obj gear_train_square.png"
)

for spec in "${CASES[@]}"; do
  read -r gpu label mesh guide <<<"$spec"
  script="$LOG/run_gpu${gpu}_${label}.sh"
  {
    echo "#!/usr/bin/env bash"
    echo "set -euo pipefail"
    printf 'ROOT=%q RUN=%q bash %q --worker %q %q %q %q\n' \
      "$ROOT" "$RUN" "$ROOT/assets/launch_cache_repair_texture_20260509.sh" \
      "$gpu" "$label" "$mesh" "$guide"
  } > "$script"
  chmod +x "$script"
  nohup "$script" > "$LOG/gpu${gpu}_${label}.log" 2>&1 &
  echo "gpu${gpu}_${label}:$!"
done

sleep 3
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | sed -n '5,8p'
for f in "$LOG"/gpu*.log; do
  echo "==== $(basename "$f")"
  tail -10 "$f" || true
done
