#!/usr/bin/env bash
set -euo pipefail
export ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
export RUN=$ROOT/trellis_classic_dense_smoke_20260529
export REPO=$ROOT/repos/TRELLIS
export WEIGHTS=$ROOT/hf_home/hub/models--microsoft--TRELLIS-image-large/snapshots/25e0d31ffbebe4b5a97464dd851910efc3002d96
export PYTHONPATH="$RUN/stubs:$REPO:${PYTHONPATH:-}"
PY=$ROOT/envs/hy3d_trellisclassic_probe_20260510/bin/python
cd "$REPO"
{
  date
  hostname
  nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits || true
  "$PY" "$RUN/scripts/trellis_classic_dense_smoke.py"
  date
} 2>&1 | tee "$RUN/logs/smoke.log"
