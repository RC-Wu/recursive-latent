#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
RUN="${RUN:-connected_scaffold_v2_textured_glb_20260509}"

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

run_case() {
  local gpu="$1"
  local label="$2"
  local mesh="$3"
  local guide="$4"
  local steps="$5"
  local tex="$6"
  export TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"
  echo "=== START $label $(date)"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/assets/trellis2_texturing_export_glb.py" \
    --mesh "$mesh" \
    --image "$guide" \
    --dinov3-model "$DINO" \
    --out "$OUT/${label}_steps${steps}_tex${tex}_xformers" \
    --steps "$steps" \
    --seed 90509 \
    --resolution 512 \
    --texture-size "$tex" \
    --preprocess
  echo "=== END $label $(date)"
}

write_gpu_script() {
  local gpu="$1"
  local script="$LOG/run_gpu${gpu}.sh"
  shift
  {
    echo "#!/usr/bin/env bash"
    echo "set -euo pipefail"
    echo "ROOT='$ROOT' RUN='$RUN' source '$ROOT/assets/launch_connected_scaffold_v2_texture_20260509.sh' --worker '$gpu' \"\$@\""
  } > "$script"
  chmod +x "$script"
}

if [[ "${1:-}" == "--worker" ]]; then
  gpu="$2"
  case "$gpu" in
    4)
      run_case 4 "bismuth_hopper_bismuth" \
        "$ROOT/inputs/connected_scaffold_cases_v2_20260509/bismuth_hopper_cluster/bismuth_hopper_cluster.obj" \
        "$ROOT/public_guides_20260508/processed/bismuth_crystal_square.png" 2 1024
      run_case 4 "bismuth_hopper_pyrite" \
        "$ROOT/inputs/connected_scaffold_cases_v2_20260509/bismuth_hopper_cluster/bismuth_hopper_cluster.obj" \
        "$ROOT/public_guides_20260508/processed/pyrite_cubes_square.png" 2 1024
      ;;
    5)
      run_case 5 "volumetric_dla_coral_bismuth" \
        "$ROOT/inputs/connected_scaffold_cases_v2_20260509/volumetric_dla_coral_cluster/volumetric_dla_coral_cluster.obj" \
        "$ROOT/public_guides_20260508/processed/bismuth_crystal_square.png" 2 1024
      run_case 5 "volumetric_dla_coral_octopus" \
        "$ROOT/inputs/connected_scaffold_cases_v2_20260509/volumetric_dla_coral_cluster/volumetric_dla_coral_cluster.obj" \
        "$ROOT/public_guides_20260508/processed/octopus_suckers_square.png" 2 1024
      ;;
    7)
      run_case 7 "pyrite_lattice_pyrite" \
        "$ROOT/inputs/connected_scaffold_cases_v2_20260509/pyrite_crystal_lattice_cluster/pyrite_crystal_lattice_cluster.obj" \
        "$ROOT/public_guides_20260508/processed/pyrite_cubes_square.png" 2 1024
      run_case 7 "porous_coral_bismuth" \
        "$ROOT/inputs/connected_scaffold_cases_v2_20260509/porous_coral_mineral/porous_coral_mineral.obj" \
        "$ROOT/public_guides_20260508/processed/bismuth_crystal_square.png" 2 1024
      ;;
    *)
      echo "Unsupported worker gpu: $gpu" >&2
      exit 2
      ;;
  esac
  exit 0
fi

write_gpu_script 4
write_gpu_script 5
write_gpu_script 7

nohup "$LOG/run_gpu4.sh" > "$LOG/gpu4_v2_texture.log" 2>&1 &
echo "gpu4_v2_texture:$!"
nohup "$LOG/run_gpu5.sh" > "$LOG/gpu5_v2_texture.log" 2>&1 &
echo "gpu5_v2_texture:$!"
nohup "$LOG/run_gpu7.sh" > "$LOG/gpu7_v2_texture.log" 2>&1 &
echo "gpu7_v2_texture:$!"

sleep 3
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader,nounits | sed -n '5,8p'
for f in "$LOG"/gpu*_v2_texture.log; do
  echo "==== $(basename "$f")"
  tail -8 "$f" || true
done
