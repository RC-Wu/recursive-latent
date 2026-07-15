#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"
TAG="cache_sampler_connectivity_20260509"
STAMP="$(date +%Y%m%d_%H%M%S)"
RUN_ID="run_${STAMP}_$$"
OUT_BASE="$ROOT/results/$TAG/$RUN_ID"
LOG_BASE="$ROOT/logs/$TAG/$RUN_ID"
CACHE_BASE="$ROOT/.cache/$TAG/$RUN_ID"

mkdir -p "$OUT_BASE" "$LOG_BASE" "$CACHE_BASE"/{tmp,hf,xdg,torch,triton,matplotlib}
export TMPDIR="$CACHE_BASE/tmp"
export HF_HOME="$CACHE_BASE/hf"
export XDG_CACHE_HOME="$CACHE_BASE/xdg"
export TORCH_HOME="$CACHE_BASE/torch"
export TRITON_CACHE_DIR="$CACHE_BASE/triton"
export MPLCONFIGDIR="$CACHE_BASE/matplotlib"
export PYTHONUNBUFFERED=1
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

{
  echo "tag=$TAG"
  echo "run_id=$RUN_ID"
  echo "root=$ROOT"
  echo "out_base=$OUT_BASE"
  echo "log_base=$LOG_BASE"
  echo "cache_base=$CACHE_BASE"
  echo "started_at=$(date -Iseconds)"
  echo "disk_before=$(du -sh "$ROOT" 2>/dev/null || true)"
  echo "nvidia_smi_query:"
  nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv,noheader 2>/dev/null || true
} | tee "$LOG_BASE/launch_manifest.txt"

run_case_filter() {
  local gpu="$1"
  local filter="$2"
  local out="$OUT_BASE/$filter"
  local log="$LOG_BASE/${filter}_gpu${gpu}.log"
  mkdir -p "$out"
  echo "launch filter=$filter gpu=$gpu out=$out log=$log" | tee -a "$LOG_BASE/launch_manifest.txt"
  (
    cd "$ROOT"
    CUDA_VISIBLE_DEVICES="$gpu" "$PYTHON_BIN" assets/cache_sampler_connectivity_20260509.py \
      --root "$ROOT" \
      --out "$out" \
      --case-filter "$filter" \
      --grid 64 \
      --write-previews \
      --write-selected-meshes
  ) >"$log" 2>&1 &
  echo "$!" > "$LOG_BASE/${filter}_gpu${gpu}.pid"
}

run_case_filter 6 hard
run_case_filter 7 control

set +e
wait "$(cat "$LOG_BASE/hard_gpu6.pid")"
hard_status=$?
wait "$(cat "$LOG_BASE/control_gpu7.pid")"
control_status=$?
set -e

"$PYTHON_BIN" - "$OUT_BASE" "$LOG_BASE" "$hard_status" "$control_status" <<'PY'
import csv
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
log = Path(sys.argv[2])
hard_status = int(sys.argv[3])
control_status = int(sys.argv[4])

rows = []
selections = []
summaries = {}
for split in ("hard", "control"):
    summary_path = out / split / "summary.json"
    if summary_path.exists():
        data = json.loads(summary_path.read_text())
        summaries[split] = data
        rows.extend(data.get("rows", []))
        selections.extend(data.get("projection_aware_texture_selection", []))
    else:
        summaries[split] = {"missing_summary": str(summary_path)}

def write_csv(path, data):
    if not data:
        path.write_text("")
        return
    fields = sorted({k for row in data for k in row})
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

hard_selected = [s for s in selections if str(s.get("case", "")).startswith("hard_")]
mean_lcr_gain = sum(float(s.get("lcr_delta_vs_naive", 0.0)) for s in hard_selected) / max(len(hard_selected), 1)
mean_comp_drop = sum(-int(float(s.get("component_delta_vs_naive", 0))) for s in hard_selected) / max(len(hard_selected), 1)
cases_with_comp_drop = sum(1 for s in hard_selected if int(float(s.get("component_delta_vs_naive", 0))) < 0)
cases_with_lcr_gain = sum(1 for s in hard_selected if float(s.get("lcr_delta_vs_naive", 0.0)) > 0)

aggregate = {
    "kind": "cache_sampler_connectivity_20260509_aggregate",
    "out": str(out),
    "log": str(log),
    "gpu_jobs": {"hard": 6, "control": 7},
    "exit_status": {"hard_gpu6": hard_status, "control_gpu7": control_status},
    "rows": rows,
    "projection_aware_texture_selection": selections,
    "aggregate": {
        "hard_cases_selected": len(hard_selected),
        "mean_best_lcr_gain_vs_naive": mean_lcr_gain,
        "mean_best_component_drop_vs_naive": mean_comp_drop,
        "cases_with_component_drop": cases_with_comp_drop,
        "cases_with_lcr_gain": cases_with_lcr_gain,
        "viable_as_standalone_paper_contribution": bool(mean_lcr_gain > 0.05 and cases_with_comp_drop >= 2),
        "viable_as_supporting_ablation": bool(cases_with_comp_drop >= 2 and cases_with_lcr_gain >= 2),
        "interpretation": "supporting ablation if confirmed with true TRELLIS decode; not standalone without decoder/texture pass",
    },
    "split_summaries": summaries,
}
(out / "aggregate_summary.json").write_text(json.dumps(aggregate, indent=2))
write_csv(out / "aggregate_metrics.csv", rows)
write_csv(out / "aggregate_projection_aware_texture_selection.csv", selections)

lines = [
    "# Cache/Sampler Connectivity 20260509 Remote Summary",
    "",
    f"- Output: `{out}`",
    f"- Logs: `{log}`",
    f"- GPUs: hard cases on `6`, control on `7`",
    f"- Exit status: hard `{hard_status}`, control `{control_status}`",
    f"- Hard cases selected: `{len(hard_selected)}`",
    f"- Mean best component drop vs naive: `{mean_comp_drop:.3f}`",
    f"- Mean best LCR gain vs naive: `{mean_lcr_gain:.6f}`",
    f"- Supporting ablation viable: `{aggregate['aggregate']['viable_as_supporting_ablation']}`",
    f"- Standalone contribution viable: `{aggregate['aggregate']['viable_as_standalone_paper_contribution']}`",
    "",
    "## Projection-Aware Selected Methods",
    "",
    "| Case | Method | Components | LCR | Component Delta | LCR Delta | Source |",
    "| --- | --- | ---: | ---: | ---: | ---: | --- |",
]
for s in selections:
    lines.append(
        "| {case} | {selected_method} | {component_count} | {largest_component_ratio:.6f} | "
        "{component_delta_vs_naive} | {lcr_delta_vs_naive:.6f} | `{source}` |".format(
            case=s.get("case", ""),
            selected_method=s.get("selected_method", ""),
            component_count=int(float(s.get("component_count", 0))),
            largest_component_ratio=float(s.get("largest_component_ratio", 0.0)),
            component_delta_vs_naive=int(float(s.get("component_delta_vs_naive", 0))),
            lcr_delta_vs_naive=float(s.get("lcr_delta_vs_naive", 0.0)),
            source=s.get("source", ""),
        )
    )
(out / "REMOTE_SUMMARY.md").write_text("\n".join(lines) + "\n")
print(json.dumps(aggregate["aggregate"], indent=2))
PY

{
  echo "finished_at=$(date -Iseconds)"
  echo "hard_status=$hard_status"
  echo "control_status=$control_status"
  echo "disk_after=$(du -sh "$ROOT" 2>/dev/null || true)"
  echo "aggregate=$OUT_BASE/aggregate_summary.json"
} | tee -a "$LOG_BASE/launch_manifest.txt"

cat "$OUT_BASE/REMOTE_SUMMARY.md"
exit $(( hard_status != 0 || control_status != 0 ))
