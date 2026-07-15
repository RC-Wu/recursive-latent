#!/usr/bin/env bash
set -euo pipefail

ROOT="${RGG_ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
EXISTING="/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff"
source "$EXISTING/PATHS.new_a100.env"

export HF_HOME="$ROOT/hf_home"
export HTTPS_PROXY="${HTTPS_PROXY:-http://127.0.0.1:27890}"
export HTTP_PROXY="${HTTP_PROXY:-http://127.0.0.1:27890}"
unset ALL_PROXY all_proxy
export PYTHONPATH="$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"

mkdir -p "$ROOT/results/trellis2_basic_smokes" "$ROOT/logs"

run_one() {
  local name="$1"
  local image="$2"
  local out="$ROOT/results/trellis2_basic_smokes/$name"
  mkdir -p "$out"
  echo "RUN_START $name image=$image out=$out"
  "$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_basic_smoke.py" \
    --out "$out" \
    --image "$image" \
    --pipeline "microsoft/TRELLIS.2-4B" \
    --pipeline-type 512 \
    --steps 4 \
    --seed 42
  echo "RUN_DONE $name"
}

run_one official_T "$MESHVAE_TRELLIS/assets/example_image/T.png"
run_one scaffold_lsystem "$ROOT/inputs/procedural_baselines/lsystem_branch.png"
run_one scaffold_dla "$ROOT/inputs/procedural_baselines/dla_cluster_points.png"

