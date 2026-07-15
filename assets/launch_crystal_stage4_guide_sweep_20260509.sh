#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-crystal_stage4_guide_sweep_20260509}"

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
GUIDE_ROOT="$ROOT/public_guides_20260508/processed"
DEPTH_ROOT="$ROOT/inputs/connected_scaffold_depth_cases_20260509"

run_case() {
  local gpu="$1"
  local label="$2"
  local mesh="$3"
  local guide="$4"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"
  echo "=== START $label gpu=$gpu mesh=$mesh guide=$guide $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
    --mesh "$mesh" \
    --image "$GUIDE_ROOT/$guide" \
    --dinov3-model "$DINO" \
    --out "$OUT/${label}_steps8_tex2048_xformers" \
    --steps 8 \
    --seed 9050931 \
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
  "4 bismuth_stage4_bismuth_edge $DEPTH_ROOT/bismuth_hopper_depth/bismuth_hopper_depth_stage_04/bismuth_hopper_depth_stage_04.obj bismuth_crystal_edge.png"
  "5 bismuth_stage4_bismuth_warm $DEPTH_ROOT/bismuth_hopper_depth/bismuth_hopper_depth_stage_04/bismuth_hopper_depth_stage_04.obj bismuth_crystal_warm.png"
  "6 pyrite_stage4_pyrite_edge $DEPTH_ROOT/pyrite_lattice_depth/pyrite_lattice_depth_stage_04/pyrite_lattice_depth_stage_04.obj pyrite_cubes_edge.png"
  "7 pyrite_stage4_pyrite_warm $DEPTH_ROOT/pyrite_lattice_depth/pyrite_lattice_depth_stage_04/pyrite_lattice_depth_stage_04.obj pyrite_cubes_warm.png"
)

for spec in "${CASES[@]}"; do
  read -r gpu label mesh guide <<<"$spec"
  script="$LOG/run_gpu${gpu}_${label}.sh"
  {
    echo "#!/usr/bin/env bash"
    echo "set -euo pipefail"
    printf 'ROOT=%q RUN=%q bash %q --worker %q %q %q %q\n' \
      "$ROOT" "$RUN" "$ROOT/assets/launch_crystal_stage4_guide_sweep_20260509.sh" \
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
  tail -8 "$f" || true
done
