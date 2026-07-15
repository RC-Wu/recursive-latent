#!/usr/bin/env bash
set -euo pipefail
export ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
export RUN=$ROOT/trellis_classic_dense_smoke_20260529
export REPO=$ROOT/repos/TRELLIS
export WEIGHTS=$ROOT/hf_home/hub/models--microsoft--TRELLIS-image-large/snapshots/25e0d31ffbebe4b5a97464dd851910efc3002d96
export PYTHONPATH="$RUN/stubs:$REPO:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/envs/hy3d_trellisclassic_probe_20260510/lib/python3.10/site-packages:/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/envs/trellis2_bakeoff/lib/python3.10/site-packages:/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/envs/trellis2_bakeoff_flashattn_20260519/lib/python3.10/site-packages:${PYTHONPATH:-}"
PY=/mnt/beegfs/xiyu/miniconda3/envs/vae-v4-t211/bin/python
cd "$REPO"
{
  date
  "$PY" "$RUN/scripts/trellis_classic_mesh_decoder_smoke.py"
  date
} 2>&1 | tee "$RUN/logs/mesh_decoder_smoke.log"
