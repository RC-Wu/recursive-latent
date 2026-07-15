# Deletion Review List

Date: 2026-07-15

Nothing in this file has been deleted yet. This is the review list that must be approved before cleanup.

## High-Confidence Cache Deletion Candidates

These are rebuildable caches or temporary files.

### A100

Remote root:

```text
a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
```

| Candidate | Size | Proposed action | Rationale |
|---|---:|---|---|
| `cache/` | `30G` | delete after approval | Runtime cache; main reclaim target. |
| `triton_cache/` | `18M` | delete after approval | Rebuildable Triton cache. |
| `.cache/` | `7.6M` | delete after approval | Rebuildable local cache. |
| `.tmp/`, `tmp/` | tiny | delete after approval | Temporary directories. |
| `.torch/`, `.triton/`, `.xdg_cache/` | tiny/empty | delete after approval | Rebuildable runtime cache. |
| Python `__pycache__/`, `*.pyc` | unknown small | delete after approval | Rebuildable bytecode. |
| `repos/Hunyuan3D-2.zip.bad` | unknown | delete after approval | Broken archive. |

### Local

Local root:

```text
/Users/fanta/code/agent/Code/recursive_3d_generative_growth
```

| Candidate | Size | Proposed action | Rationale |
|---|---:|---|---|
| `.hf_local_cache/` | `27G` | delete after approval | Re-downloadable model/cache data. |
| `.cache/` | `117M` | delete after approval | Rebuildable local cache. |
| `.pytest_cache/` | `40K` | delete after approval | Rebuildable test cache. |
| `.DS_Store` files | small | delete after approval | OS metadata. |
| Python `__pycache__/`, `*.pyc` | unknown small | delete after approval | Rebuildable bytecode. |

## Larger Results / Visuals Requiring Explicit Decision

These may contain unique experiment evidence. Do not delete until archived or explicitly abandoned.

### A100

| Candidate | Size | Proposed action | Risk |
|---|---:|---|---|
| `results/` | `81G` | archive selected subsets, then delete or prune | Contains main experimental outputs and GLB/OBJ/PLY/PBR evidence. |
| `inputs/` | `1.6G` | archive selected manifests/final inputs, then prune | Contains generated task inputs and metadata. |
| `hf_home/` | `23G` | delete only if redownload is acceptable | Cache may save time and avoid network issues. |
| `weights/` | `16G` | keep or archive; do not delete by default | Model weights may be difficult to redownload. |
| `envs/` | `772M` | archive env metadata first; then optional delete | Exact environment can help reproduce old runs. |
| `repos/` | `272M` | keep or archive source snapshots; delete zip duplicates only | Contains upstream source snapshots. |
| `runs/` | `51M` | archive with 2026-05-29 smoke docs if useful | Small but unique smoke evidence. |

### Local

| Candidate | Size | Proposed action | Risk |
|---|---:|---|---|
| `results/` | `26G` | archive selected, then prune/delete | Local experiment outputs. |
| `visuals/` | `15G` | archive final selected figures/galleries first | Contains user-facing visual review assets. |
| `docs/` generated galleries/inventories | part of `2.2G` | prune only generated media, not text docs | Text docs are important provenance. |
| `paper_siga/figures/` | part of `495M` | curate final figures; delete duplicates/build artifacts | Paper figures may be needed. |
| `.venv_render/` | `206M` | delete after approval | Rebuildable env. |
| `downloads/` | `165M` | inspect/archive if needed, then delete | May contain downloaded source/reference assets. |
| `.worktrees/` | `128M` | inspect, then delete stale worktrees | Could contain unmerged edits. |

## Suggested First Cleanup Command Set

Run only after approval:

```bash
# A100 cache cleanup
rm -rf /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache
rm -rf /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/triton_cache
rm -rf /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.cache
rm -rf /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.tmp
rm -rf /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/tmp
rm -rf /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.torch
rm -rf /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.triton
rm -rf /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.xdg_cache
find /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507 -type d -name __pycache__ -prune -exec rm -rf {} +
find /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507 -type f -name '*.pyc' -delete
rm -f /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/repos/Hunyuan3D-2.zip.bad
```

```bash
# Local cache cleanup
rm -rf /Users/fanta/code/agent/Code/recursive_3d_generative_growth/.hf_local_cache
rm -rf /Users/fanta/code/agent/Code/recursive_3d_generative_growth/.cache
rm -rf /Users/fanta/code/agent/Code/recursive_3d_generative_growth/.pytest_cache
find /Users/fanta/code/agent/Code/recursive_3d_generative_growth -type d -name __pycache__ -prune -exec rm -rf {} +
find /Users/fanta/code/agent/Code/recursive_3d_generative_growth -type f -name '*.pyc' -delete
find /Users/fanta/code/agent/Code/recursive_3d_generative_growth -type f -name '.DS_Store' -delete
```

## Approval Needed

Please explicitly approve which group to delete:

- `A`: high-confidence caches only.
- `B`: caches plus local rebuildable env/worktree/download candidates after inspection.
- `C`: selected old results/visuals after a separate archive manifest is prepared.
