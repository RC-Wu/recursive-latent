#!/usr/bin/env bash
set -euo pipefail
PY=/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/envs/trellis2_bakeoff_flashattn_20260519/bin/python
{
  date
  "$PY" -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --extra-index-url https://pypi.org/simple --prefer-binary --no-input spconv-cu120==2.3.6
  "$PY" - <<'PY'
import spconv, spconv.pytorch as sp
print('spconv ok', spconv.__file__)
PY
  date
} 2>&1 | tee /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/trellis_classic_dense_smoke_20260529/logs/install_spconv_flashenv.log
