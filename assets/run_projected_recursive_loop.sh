#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 8 ]]; then
  echo "usage: $0 GPU LABEL ROOT_MESH GRAMMAR ITERS FIT_SCALE MAX_TOKENS MIN_VERTICES" >&2
  exit 2
fi

GPU="$1"
LABEL="$2"
ROOT_MESH="$3"
GRAMMAR="$4"
ITERS="$5"
FIT_SCALE="$6"
MAX_TOKENS="$7"
MIN_VERTICES="$8"

ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env

mkdir -p "$ROOT/logs" "$ROOT/cache/tmp" "$ROOT/cache/matplotlib" "$ROOT/cache/torch_extensions"
export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/tmp"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export ATTN_BACKEND=xformers
export CUDA_VISIBLE_DEVICES="$GPU"
export TRITON_CACHE_DIR="$ROOT/cache/triton/projected_loop_${LABEL}_gpu${GPU}"

OUTROOT="$ROOT/results/siga_projected_recursive_loop_20260508_0715/$LABEL"
mkdir -p "$OUTROOT"

CURRENT_MESH="$ROOT_MESH"
echo "{\"label\":\"$LABEL\",\"grammar\":\"$GRAMMAR\",\"iters\":$ITERS,\"fit_scale\":$FIT_SCALE,\"max_tokens\":$MAX_TOKENS,\"min_vertices\":$MIN_VERTICES,\"root_mesh\":\"$ROOT_MESH\"}" > "$OUTROOT/config.json"

for ((i = 1; i <= ITERS; i++)); do
  STAGE=$(printf "stage_%02d" "$i")
  RAW_DIR="$OUTROOT/$STAGE/raw"
  PROJ_DIR="$OUTROOT/$STAGE/projected"
  mkdir -p "$RAW_DIR" "$PROJ_DIR"

  "$MESHVAE_ENV/bin/python" "$ROOT/assets/trellis2_recursive_slat_grammar_workflow.py" \
    --mesh "$CURRENT_MESH" \
    --out "$RAW_DIR" \
    --case-name "${LABEL}_${STAGE}" \
    --grammars "$GRAMMAR" \
    --depths 1 \
    --fit-scale "$FIT_SCALE" \
    --max-tokens "$MAX_TOKENS"

  NEXT_RAW="$RAW_DIR/$GRAMMAR/depth_01/mesh.obj"
  "$MESHVAE_ENV/bin/python" "$ROOT/assets/prune_mesh_components.py" \
    --min-vertices "$MIN_VERTICES" \
    --keep-largest \
    --out "$PROJ_DIR" \
    --case "${LABEL}_${STAGE}=$NEXT_RAW"

  CURRENT_MESH="$PROJ_DIR/${LABEL}_${STAGE}/mesh_pruned.obj"
  echo "$CURRENT_MESH" > "$OUTROOT/latest_mesh.txt"
done
