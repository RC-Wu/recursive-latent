# Remote Baseline/Storage Audit 20260511 Subagent

Date: 2026-05-11 02:53-03:00 CST  
Scope: read-only audit of `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
Constraints honored: one SSH shell, no training, no download, no file changes on remote, GPUs 4/5/6/7 only for future work, storage cap 200GB.

## Commands Run

Local reads:

- `sed -n '1,240p' docs/progress/ralph_publication_closure_plan_20260510.md`
- `sed -n '1,260p' docs/progress/remote_repair_loop_20260510b.md`
- `rg -n "hy3d_trellisclassic|Hunyuan3D|TRELLIS-image-large|TRELLIS\\.2-4B|TRELLIS-image|hunyuan_shape_demo|gen3d_baseline_trellis2" docs assets`

Single remote shell:

- `ssh a100-2 'bash -s'`
- remote checks included `hostname`, `date`, `du -sh`, `du -h --max-depth=1`, `nvidia-smi`, `nvidia-smi pmon -c 1`, `ps -u "$USER"`, `conda env list || micromamba env list`, and read-only `find` probes for TRELLIS/Hunyuan repos, caches, scripts, logs, and outputs.

## Remote Storage / Process State

- Remote root exists: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`.
- Project size at audit: `95G`, below the `200GB` cap.
- Largest top-level directories:
  - `results`: `55G`
  - `hf_home`: `23G`
  - `cache`: `13G`
  - `weights`: `2.3G`
  - `inputs`: `1.3G`
  - `envs`: `391M`
  - `repos`: `271M`
- GPUs `0-7` all showed `0 MiB` used and `0%` utilization. `nvidia-smi pmon -c 1` showed no GPU processes.
- User process list showed only long-lived shell/tmux/rclone/proxy helpers plus this audit SSH process; no active training/inference job was visible.

## TRELLIS Classic / Non-2

Present:

- Repo: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/repos/TRELLIS`
- Python package directory: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/repos/TRELLIS/trellis`
- Cached image checkpoint: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/hf_home/hub/models--microsoft--TRELLIS-image-large`
- Probe env directory: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/envs/hy3d_trellisclassic_probe_20260510`

Known blocker from local progress log:

- TRELLIS classic is not yet runnable.
- Import probes progressed through earlier missing deps and FlexiCubes repair, then stopped at missing `kaolin`; real `open3d` is also missing/unstable because the `open3d-0.19.0` wheel download is large (`447.7 MB`) and was stopped/hung.
- Current status: repo + checkpoint + partial environment exist, but runnable image-to-3D baseline is blocked by environment/compiled dependency stack (`torchvision::nms` stub need, `open3d`, `kaolin`, likely CUDA/PyTorch compatibility).

## Hunyuan3D 2.0

Present:

- Repo: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/repos/Hunyuan3D-2`
- Package dirs: `repos/Hunyuan3D-2/hy3dgen`, `repos/Hunyuan3D-2/hy3dgen.egg-info`
- Probe env directory: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/envs/hy3d_trellisclassic_probe_20260510`
- Cache dirs:
  - `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/huggingface/hub/models--tencent--Hunyuan3D-2`
  - `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/hy3dgen`
- Smoke output:
  - `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/remote_smoke_20260510/hunyuan_shape_demo_lowcost`
- Full-pool output:
  - `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/publication_hunyuan_recursive_guides_20260510`

Interpretation:

- Hunyuan3D shape-only repo/package/weights/load/generate are available according to the 20260510 progress log and current path audit.
- Hunyuan shape-only 13-case pool exists; Hunyuan mesh-space generated-root negative controls were later completed locally.
- Remaining gap: no Hunyuan texture/paint baseline was found/claimed complete; do not report Hunyuan image+texture as closed.

## TRELLIS.2

Present and usable:

- Cached weights:
  - `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/hf_home/hub/models--microsoft--TRELLIS.2-4B`
  - `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/hf_home/hub/models--microsoft--TRELLIS-image-large`
- TRELLIS.2 scripts:
  - `assets/trellis2_recursive_slat_grammar_workflow.py`
  - `assets/trellis2_texturing_export_glb.py`
  - `assets/trellis2_dinov3_latent_transform_baseline_20260510.py`
  - `assets/run_trellis2_smokes.sh`
- Evidence directories:
  - `results/gen3d_baseline_trellis2_one_shot_*_20260510`
  - `logs/gen3d_baseline_trellis2_one_shot_*_20260510`
  - `results/trellis2_*`
  - `results/publication_repair_remote_20260510b`
  - `results/publication_repair_remote_20260510c`
  - `results/publication_repair_remote_20260510e`
  - `results/publication_repair_remote_20260510f`

Interpretation:

- TRELLIS.2 is the currently usable baseline/generation stack with cache, scripts, logs, and multiple completed output directories.
- The non-interactive audit shell did not expose `conda env list`, so env usability is inferred from existing successful logs/outputs rather than a fresh import smoke in this audit.

## Blockers

1. TRELLIS classic/non-2: not runnable; missing/blocked dependency stack (`kaolin`, real `open3d`, `torchvision::nms` compatibility, possible compiled extension compatibility).
2. Hunyuan image+texture: not closed; shape-only is runnable, but paint/texture pipeline was not verified complete in this audit.
3. Conda env listing did not print in this SSH non-interactive shell; env directories were found by path, but fresh import smokes were not rerun to avoid starting jobs or changing state.

## Next Minimal Smoke Commands

Use only after coordinating GPU availability and keeping `CUDA_VISIBLE_DEVICES=4`.

TRELLIS.2 no-new-download smoke:

```bash
cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
CUDA_VISIBLE_DEVICES=4 HF_HOME=$PWD/hf_home python assets/trellis2_dinov3_official_min_smoke.py --help
```

Hunyuan shape-only cached demo smoke:

```bash
cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
CUDA_VISIBLE_DEVICES=4 HF_HOME=$PWD/cache/huggingface HF_HUB_CACHE=$PWD/cache/huggingface/hub HY3DGEN_MODELS=$PWD/cache/hy3dgen \
  envs/hy3d_trellisclassic_probe_20260510/bin/python cache/tmp/hunyuan_shape_generate_smoke_20260510.py
```

TRELLIS classic import-only probe:

```bash
cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
envs/hy3d_trellisclassic_probe_20260510/bin/python - <<'PY'
import importlib.util
print("trellis", bool(importlib.util.find_spec("trellis")))
print("kaolin", bool(importlib.util.find_spec("kaolin")))
print("open3d", bool(importlib.util.find_spec("open3d")))
PY
```
