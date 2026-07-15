#!/usr/bin/env bash
set -euo pipefail
export ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
export RUN=$ROOT/trellis_classic_dense_smoke_20260529
export REPO=$ROOT/repos/TRELLIS
export WEIGHTS=$ROOT/hf_home/hub/models--microsoft--TRELLIS-image-large/snapshots/25e0d31ffbebe4b5a97464dd851910efc3002d96
export PYTHONPATH="$RUN/stubs:$REPO:${PYTHONPATH:-}"
PY=/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/envs/trellis2_bakeoff_flashattn_20260519/bin/python
cd "$REPO"
{
  date
  "$PY" "$RUN/scripts/trellis_classic_pipeline_smoke_v2.py"
  date
} 2>&1 | tee "$RUN/logs/smoke_v5_flashenv.log"
