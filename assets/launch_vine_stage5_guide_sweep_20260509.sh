#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-vine_stage5_guide_sweep_20260509}"

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
MESH="$ROOT/results/siga_projected_recursive_loop_20260508_0715/vine_d5_projected_compete/stage_05/projected/vine_d5_projected_compete_stage_05/mesh_pruned.obj"

run_case() {
  local gpu="$1"
  local label="$2"
  local guide="$3"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"
  echo "=== START $label gpu=$gpu guide=$guide $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
    --mesh "$MESH" \
    --image "$GUIDE_ROOT/$guide" \
    --dinov3-model "$DINO" \
    --out "$OUT/${label}_steps8_tex2048_xformers" \
    --steps 8 \
    --seed 9050935 \
    --resolution 512 \
    --texture-size 2048 \
    --preprocess
  echo "=== END $label $(date)"
}

if [[ "${1:-}" == "--worker" ]]; then
  run_case "$2" "$3" "$4"
  exit 0
fi

declare -a CASES=(
  "4 vine_stage5_parthenocissus_square parthenocissus_tendrils_square.png"
  "5 vine_stage5_parthenocissus_warm parthenocissus_tendrils_warm.png"
  "6 vine_stage5_parthenocissus_edge parthenocissus_tendrils_edge.png"
  "7 vine_stage5_tree_roots_square tree_roots_arlington_square.png"
)

for spec in "${CASES[@]}"; do
  read -r gpu label guide <<<"$spec"
  script="$LOG/run_gpu${gpu}_${label}.sh"
  {
    echo "#!/usr/bin/env bash"
    echo "set -euo pipefail"
    printf 'ROOT=%q RUN=%q bash %q --worker %q %q %q\n' \
      "$ROOT" "$RUN" "$ROOT/assets/launch_vine_stage5_guide_sweep_20260509.sh" \
      "$gpu" "$label" "$guide"
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
