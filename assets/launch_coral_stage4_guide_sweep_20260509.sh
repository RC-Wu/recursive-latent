#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-coral_stage4_guide_sweep_20260509}"
FAMILY="${FAMILY:-volumetric_coral_depth}"
STAGE="${STAGE:-04}"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

LOG="$ROOT/logs/$RUN"
OUT="$ROOT/results/$RUN"
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
INPUT_ROOT="$ROOT/inputs/connected_coral_depth_cases_20260509/$FAMILY"
MESH="$INPUT_ROOT/${FAMILY}_stage_${STAGE}/${FAMILY}_stage_${STAGE}.obj"

run_case() {
  local gpu="$1"
  local guide_name="$2"
  local label="$3"
  local guide="$ROOT/public_guides_20260508/processed/$guide_name"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"
  echo "=== START ${label} gpu=$gpu guide=$guide_name $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
    --mesh "$MESH" \
    --image "$guide" \
    --dinov3-model "$DINO" \
    --out "$OUT/${label}_steps8_tex2048_xformers" \
    --steps 8 \
    --seed 90509 \
    --resolution 512 \
    --texture-size 2048 \
    --preprocess
  echo "=== END ${label} $(date)"
}

if [[ "${1:-}" == "--worker" ]]; then
  run_case "$2" "$3" "$4"
  exit 0
fi

declare -a CASES=(
  "4 octopus_suckers_square.png coral_octopus_hq"
  "5 spiky_plant_tendril_square.png coral_spikyplant_hq"
  "6 bismuth_crystal_square.png coral_bismuth_hq"
  "7 pyrite_cubes_square.png coral_pyrite_hq"
)

for spec in "${CASES[@]}"; do
  read -r gpu guide label <<<"$spec"
  script="$LOG/run_gpu${gpu}_${label}.sh"
  {
    echo "#!/usr/bin/env bash"
    echo "set -euo pipefail"
    echo "ROOT='$ROOT' RUN='$RUN' FAMILY='$FAMILY' STAGE='$STAGE' source '$ROOT/assets/launch_coral_stage4_guide_sweep_20260509.sh' --worker '$gpu' '$guide' '$label'"
  } > "$script"
  chmod +x "$script"
  nohup "$script" > "$LOG/gpu${gpu}_${label}.log" 2>&1 &
  echo "gpu${gpu}_${label}:$!"
done

sleep 3
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader,nounits | sed -n '5,8p'
for f in "$LOG"/gpu*.log; do
  echo "==== $(basename "$f")"
  tail -8 "$f" || true
done
