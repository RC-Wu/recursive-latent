#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-dla_bridge_ablation_20260509}"

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
  shift
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"
  echo "=== START gpu=$gpu $* $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/connectivity_first_dla_crystal_20260509.py" \
    --root "$ROOT" \
    --out "$OUT/gpu${gpu}" \
    --stages 2 \
    --resolution 512 \
    --grid-resolution 512 \
    --fit-scale 0.62 \
    --max-tokens 12000 \
    --min-vertices 2400 \
    --mesh-bridge-components 12 \
    --bridge-radius-ratio 0.003 \
    --voxel-pitch-ratio 0.005 \
    "$@"
  echo "=== END gpu=$gpu $(date)"
}

if [[ "${1:-}" == "--worker" ]]; then
  gpu="$2"
  case "$gpu" in
    4)
      run_worker 4 \
        --case "hard_dla=$HARD_DLA" \
        --grammars fork_side_attach \
        --methods raw raw_bridge_smooth
      ;;
    5)
      run_worker 5 \
        --case "hard_dla=$HARD_DLA" \
        --grammars fork_side_attach \
        --methods sparse_close_bridge mesh_bridge_smooth
      ;;
    6)
      run_worker 6 \
        --case "volumetric_dla=$VOL_DLA" \
        --grammars compete_fork_attach \
        --methods raw raw_bridge_smooth
      ;;
    7)
      run_worker 7 \
        --case "volumetric_dla=$VOL_DLA" \
        --grammars fork_side_attach \
        --methods sparse_close_bridge mesh_bridge_smooth
      ;;
    *)
      echo "Unsupported worker gpu: $gpu" >&2
      exit 2
      ;;
  esac
  exit 0
fi

for gpu in 4 5 6 7; do
  script="$LOG/run_gpu${gpu}.sh"
  {
    echo "#!/usr/bin/env bash"
    echo "set -euo pipefail"
    echo "ROOT='$ROOT' RUN='$RUN' source '$ROOT/assets/launch_dla_bridge_ablation_20260509.sh' --worker '$gpu'"
  } > "$script"
  chmod +x "$script"
  nohup "$script" > "$LOG/gpu${gpu}.log" 2>&1 &
  echo "gpu${gpu}:$!"
done

sleep 3
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader,nounits | sed -n '5,8p'
for f in "$LOG"/gpu*.log; do
  echo "==== $(basename "$f")"
  tail -8 "$f" || true
done

