#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-dla_bridge_smoke_stage1_20260509}"

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

HARD_DLA="$ROOT/inputs/hard_cases_20260509/dla_fork_side_s2_a0p25_d3.obj"
VOL_DLA="$ROOT/inputs/connected_scaffold_cases_v2_20260509/volumetric_dla_coral_cluster/volumetric_dla_coral_cluster.obj"

run_worker() {
  local gpu="$1"
  local label="$2"
  local mesh="$3"
  local method="$4"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"
  echo "=== START $label method=$method gpu=$gpu $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/connectivity_first_dla_crystal_20260509.py" \
    --root "$ROOT" \
    --out "$OUT/${label}_${method}" \
    --case "$label=$mesh" \
    --grammars fork_side_attach \
    --methods "$method" \
    --stages 1 \
    --resolution 512 \
    --grid-resolution 512 \
    --fit-scale 0.62 \
    --max-tokens 9000 \
    --min-vertices 2400 \
    --mesh-bridge-components 10 \
    --bridge-radius-ratio 0.003 \
    --voxel-pitch-ratio 0.004 \
    --texture-top-k 0
  echo "=== END $label method=$method gpu=$gpu $(date)"
}

if [[ "${1:-}" == "--worker" ]]; then
  run_worker "$2" "$3" "$4" "$5"
  exit 0
fi

declare -a CASES=(
  "4 hard_dla $HARD_DLA raw"
  "5 hard_dla $HARD_DLA sparse_close_bridge"
  "6 volumetric_dla $VOL_DLA raw"
  "7 volumetric_dla $VOL_DLA sparse_close_bridge"
)

for spec in "${CASES[@]}"; do
  read -r gpu label mesh method <<<"$spec"
  script="$LOG/run_gpu${gpu}_${label}_${method}.sh"
  {
    echo "#!/usr/bin/env bash"
    echo "set -euo pipefail"
    printf 'ROOT=%q RUN=%q bash %q --worker %q %q %q %q\n' \
      "$ROOT" "$RUN" "$ROOT/assets/launch_dla_bridge_smoke_stage1_20260509.sh" \
      "$gpu" "$label" "$mesh" "$method"
  } > "$script"
  chmod +x "$script"
  nohup "$script" > "$LOG/gpu${gpu}_${label}_${method}.log" 2>&1 &
  echo "gpu${gpu}_${label}_${method}:$!"
done

sleep 3
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | sed -n '5,8p'
for f in "$LOG"/gpu*.log; do
  echo "==== $(basename "$f")"
  tail -10 "$f" || true
done
