#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-coral_density_extreme_texture_20260509}"
FAMILY="${FAMILY:-coral_density_param}"
GUIDE_NAME="${GUIDE_NAME:-octopus_suckers_square.png}"

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
GUIDE="$ROOT/public_guides_20260508/processed/$GUIDE_NAME"
INPUT_ROOT="$ROOT/inputs/connected_parameter_cases_extreme_20260509/$FAMILY"

run_case() {
  local gpu="$1"
  local token="$2"
  local label="${FAMILY}_density_${token}_octopus"
  local mesh="$INPUT_ROOT/${FAMILY}_density_${token}/${FAMILY}_density_${token}.obj"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"
  echo "=== START $label gpu=$gpu $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
    --mesh "$mesh" \
    --image "$GUIDE" \
    --dinov3-model "$DINO" \
    --out "$OUT/${label}_steps8_tex2048_xformers" \
    --steps 8 \
    --seed 90520 \
    --resolution 512 \
    --texture-size 2048 \
    --preprocess
  echo "=== END $label $(date)"
}

if [[ "${1:-}" == "--worker" ]]; then
  run_case "$2" "$3"
  exit 0
fi

declare -a CASES=(
  "4 0p25"
  "5 0p45"
  "6 1p35"
  "7 1p75"
)

for spec in "${CASES[@]}"; do
  read -r gpu token <<<"$spec"
  script="$LOG/run_gpu${gpu}_${token}.sh"
  {
    echo "#!/usr/bin/env bash"
    echo "set -euo pipefail"
    echo "ROOT='$ROOT' RUN='$RUN' FAMILY='$FAMILY' GUIDE_NAME='$GUIDE_NAME' source '$ROOT/assets/launch_coral_density_extreme_texture_20260509.sh' --worker '$gpu' '$token'"
  } > "$script"
  chmod +x "$script"
  nohup "$script" > "$LOG/gpu${gpu}_${token}.log" 2>&1 &
  echo "gpu${gpu}_${token}:$!"
done

sleep 3
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader,nounits | sed -n '5,8p'
for f in "$LOG"/gpu*.log; do
  echo "==== $(basename "$f")"
  tail -8 "$f" || true
done
