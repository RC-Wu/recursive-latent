#!/usr/bin/env bash
set -euo pipefail

ROOT="${RGG_ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
DOWNLOAD_PID_FILE="$ROOT/logs/download_trellis2_deps_20260507_0256.pid"
WATCH_LOG="$ROOT/logs/watch_download_then_run_smokes_20260507.log"
SMOKE_LOG="$ROOT/logs/trellis2_basic_smokes_20260507.log"

echo "WATCH_START $(date -Is)" | tee -a "$WATCH_LOG"
while true; do
  if [ ! -s "$DOWNLOAD_PID_FILE" ]; then
    echo "WAIT_NO_PID $(date -Is)" | tee -a "$WATCH_LOG"
    sleep 60
    continue
  fi
  pid="$(cat "$DOWNLOAD_PID_FILE")"
  if ps -p "$pid" >/dev/null 2>&1; then
    size="$(du -sh "$ROOT" | cut -f1)"
    echo "WAIT_DOWNLOAD $(date -Is) pid=$pid size=$size" | tee -a "$WATCH_LOG"
    sleep 120
    continue
  fi
  echo "DOWNLOAD_EXITED $(date -Is) pid=$pid" | tee -a "$WATCH_LOG"
  break
done

tail -80 "$ROOT/logs/download_trellis2_deps_20260507_0256.log" >> "$WATCH_LOG" || true

echo "SMOKE_START $(date -Is)" | tee -a "$WATCH_LOG"
bash "$ROOT/assets/run_trellis2_smokes.sh" > "$SMOKE_LOG" 2>&1
echo "SMOKE_EXIT_CODE=$? $(date -Is)" | tee -a "$WATCH_LOG"
du -sh "$ROOT" | tee -a "$WATCH_LOG"

