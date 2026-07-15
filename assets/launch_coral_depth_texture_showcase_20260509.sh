#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-coral_depth_textured_showcase_20260509}"
FAMILY="${FAMILY:-volumetric_coral_depth}"
GUIDE_NAME="${GUIDE_NAME:-octopus_suckers_square.png}"

source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env
PY="$MESHVAE_ENV/bin/python"

LOG="$ROOT/logs/$RUN"
OUT="$ROOT/results/$RUN"
mkdir -p "$LOG" "$OUT" \
  "$ROOT/cache/tmp" \
  "$ROOT/cache/torch" \
  "$ROOT/cache/xdg" \
  "$ROOT/cache/matplotlib" \
  "$ROOT/cache/torch_extensions" \
  "$ROOT/cache/triton/$RUN"

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
INPUT_ROOT="$ROOT/inputs/connected_coral_depth_cases_20260509/$FAMILY"

run_stage() {
  local gpu="$1"
  local stage="$2"
  local label="${FAMILY}_stage_${stage}_coral"
  local mesh="$INPUT_ROOT/${FAMILY}_stage_${stage}/${FAMILY}_stage_${stage}.obj"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"
  echo "=== START $label gpu=$gpu guide=$GUIDE_NAME $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
    --mesh "$mesh" \
    --image "$GUIDE" \
    --dinov3-model "$DINO" \
    --out "$OUT/${label}_steps6_tex1024_xformers" \
    --steps 6 \
    --seed 90509 \
    --resolution 512 \
    --texture-size 1024 \
    --preprocess
  echo "=== END $label $(date)"
}

if [[ "${1:-}" == "--worker" ]]; then
  run_stage "$2" "$3"
  exit 0
fi

for pair in "4 01" "5 02" "6 03" "7 04"; do
  gpu="${pair%% *}"
  stage="${pair##* }"
  script="$LOG/run_gpu${gpu}_stage${stage}.sh"
  {
    echo "#!/usr/bin/env bash"
    echo "set -euo pipefail"
    echo "ROOT='$ROOT' RUN='$RUN' FAMILY='$FAMILY' GUIDE_NAME='$GUIDE_NAME' source '$ROOT/assets/launch_coral_depth_texture_showcase_20260509.sh' --worker '$gpu' '$stage'"
  } > "$script"
  chmod +x "$script"
  nohup "$script" > "$LOG/gpu${gpu}_stage${stage}.log" 2>&1 &
  echo "gpu${gpu}_stage${stage}:$!"
done

sleep 3
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader,nounits | sed -n '5,8p'
for f in "$LOG"/gpu*_stage*.log; do
  echo "==== $(basename "$f")"
  tail -8 "$f" || true
done
