#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-traditional_baseline_texture_20260509}"

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
INPUT_ROOT="$ROOT/inputs/traditional_baselines_texturing_20260509"
GUIDE_ROOT="$ROOT/public_guides_20260508/processed"

run_case() {
  local gpu="$1"
  local label="$2"
  local mesh_rel="$3"
  local guide_name="$4"
  local steps="${5:-6}"
  local tex="${6:-1024}"
  local mesh="$INPUT_ROOT/$mesh_rel"
  local guide="$GUIDE_ROOT/$guide_name"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"
  echo "=== START $label gpu=$gpu mesh=$mesh_rel guide=$guide_name $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
    --mesh "$mesh" \
    --image "$guide" \
    --dinov3-model "$DINO" \
    --out "$OUT/${label}_steps${steps}_tex${tex}_xformers" \
    --steps "$steps" \
    --seed 90520 \
    --resolution 512 \
    --texture-size "$tex" \
    --preprocess
  echo "=== END $label $(date)"
}

if [[ "${1:-}" == "--worker" ]]; then
  run_case "$2" "$3" "$4" "$5" "${6:-6}" "${7:-1024}"
  exit 0
fi

declare -a CASES=(
  "4 sc_root_vine sc_root_vine.obj tree_roots_arlington_square.png 6 1024"
  "5 sc_tree_canopy sc_tree_canopy.obj spiky_plant_tendril_square.png 6 1024"
  "6 lsystem_branch lsystem_branch.obj parthenocissus_tendrils_square.png 6 1024"
  "7 dla_cluster dla_cluster_voxels.obj octopus_suckers_square.png 6 1024"
)

for spec in "${CASES[@]}"; do
  read -r gpu label mesh guide steps tex <<<"$spec"
  script="$LOG/run_gpu${gpu}_${label}.sh"
  {
    echo "#!/usr/bin/env bash"
    echo "set -euo pipefail"
    echo "ROOT='$ROOT' RUN='$RUN' source '$ROOT/assets/launch_traditional_baseline_texture_20260509.sh' --worker '$gpu' '$label' '$mesh' '$guide' '$steps' '$tex'"
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
