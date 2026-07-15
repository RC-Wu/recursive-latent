#!/usr/bin/env bash
set -Eeuo pipefail

# Wait for HunyuanDiT weights to become complete, then run the official
# text-root -> Hunyuan3D shape -> mesh-space copy baseline.

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
PY="${PY:-$ROOT/envs/hy3d_trellisclassic_probe_20260510/bin/python}"
MODEL_DIR="${MODEL_DIR:-$ROOT/weights/HunyuanDiT-v1.1-Diffusers-Distilled}"
SHAPE_MODEL="${SHAPE_MODEL:-$ROOT/cache/huggingface/hub/models--tencent--Hunyuan3D-2/snapshots/9cd649ba6913f7a852e3286bad86bfa9a2d83dcf}"
OUT_DIR="${OUT_DIR:-$ROOT/results/publication_hunyuan_text_root_meshspace_20260511}"
LOG_DIR="${LOG_DIR:-$ROOT/logs}"
GPU_ID="${GPU_ID:-4}"
CHECK_INTERVAL_SEC="${CHECK_INTERVAL_SEC:-60}"
MAX_WAIT_SEC="${MAX_WAIT_SEC:-28800}"

mkdir -p "$LOG_DIR" "$OUT_DIR"
MAIN_LOG="$LOG_DIR/hunyuan_text_root_meshspace_autorun_20260511.log"

cd "$ROOT"
exec > >(tee -a "$MAIN_LOG") 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] AUTORUN_START root=$ROOT gpu=$GPU_ID"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] python=$PY"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] shape_model=$SHAPE_MODEL"

deadline=$(( $(date +%s) + MAX_WAIT_SEC ))
while true; do
  if "$PY" assets/download_hunyuan_dit_with_resume_20260511.py \
    --model-dir "$MODEL_DIR" \
    --log "$LOG_DIR/hunyuan_dit_resume_check_20260511.log" \
    --check-only; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WEIGHTS_COMPLETE"
    break
  fi
  now=$(date +%s)
  if (( now >= deadline )); then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WEIGHTS_WAIT_TIMEOUT"
    exit 2
  fi
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] waiting for weights; sleeping ${CHECK_INTERVAL_SEC}s"
  sleep "$CHECK_INTERVAL_SEC"
done

export CUDA_VISIBLE_DEVICES="$GPU_ID"
export PYTHONPATH="$ROOT/repos/Hunyuan3D-2:${PYTHONPATH:-}"
export PYTHONNOUSERSITE=1
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export DIFFUSERS_OFFLINE=1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] T2I_SMOKE_START"
"$PY" - <<'PY'
import torch
from pathlib import Path

try:
    lib = torch.library.Library("torchvision", "DEF")
    lib.define("nms(Tensor dets, Tensor scores, float iou_threshold) -> Tensor")
except Exception:
    pass

from hy3dgen.text2image import HunyuanDiTPipeline

root = Path("/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507")
model = root / "weights/HunyuanDiT-v1.1-Diffusers-Distilled"
out = root / "results/publication_hunyuan_text_root_meshspace_20260511/text_root_smoke.png"
out.parent.mkdir(parents=True, exist_ok=True)
pipe = HunyuanDiTPipeline(str(model), device="cuda")
img = pipe("single upright cedar tree trunk with one forked branch segment, isolated 3D object", seed=2026051101)
img.save(out)
print(f"T2I_SMOKE_OK {out} {out.stat().st_size}")
PY
echo "[$(date '+%Y-%m-%d %H:%M:%S')] T2I_SMOKE_DONE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] BASELINE_ALL_START"
"$PY" assets/hunyuan_text_root_meshspace_baseline_20260511.py \
  --mode all \
  --case all \
  --out "$OUT_DIR" \
  --t2i-model "$MODEL_DIR" \
  --shape-model "$SHAPE_MODEL" \
  --force-roots
echo "[$(date '+%Y-%m-%d %H:%M:%S')] BASELINE_ALL_DONE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] OUTPUTS"
find "$OUT_DIR" -maxdepth 4 -type f \( -name '*.png' -o -name '*.glb' -o -name '*.obj' -o -name '*.csv' -o -name '*.json' \) -printf '%p %s\n' | sort
