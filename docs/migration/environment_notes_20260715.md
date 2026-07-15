# Environment Notes

Date: 2026-07-15

## Verified A100 Host

- Host alias: `a100-2`
- User: `ruocheng`
- GPU: 8 x NVIDIA A100-SXM4-80GB
- Audit-time GPU state: all 8 cards showed `0 MiB` used.
- Main project root: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`
- Upstream Trellis2/MeshVAE context: `/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff`

Do not confuse this project with `dev-intern-01` or `dev-intern-02`.

## Cache Policy

Historical A100 runs were configured to keep runtime caches under the project root rather than `/tmp` or `/dev/shm`.

Important environment variables used by launch scripts include:

```bash
HF_HOME=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/hf_home
TORCH_HOME=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/torch
TRITON_CACHE_DIR=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/triton
XDG_CACHE_HOME=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/xdg
TMPDIR=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/tmp
MPLCONFIGDIR=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/mpl_cache
```

When migrating, prefer new project-local cache paths and keep them out of Git.

## Source Dependencies

Historical source roots:

```text
/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/repos/TRELLIS.2
/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/repos/TRELLIS
/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/repos/Hunyuan3D-2
```

These upstream repositories are treated as external dependencies or archive-only snapshots. Do not vendor full upstream repos into this repository unless a minimal patch set is extracted.

## Paper Environment

Local paper source is under:

```text
paper_siga/
```

The original working paper directory was an Overleaf git checkout. In the migration source it was dirty and behind `overleaf/master` by one commit. This repository includes source and draft metadata only; large figures are managed as artifacts.

## Known Large Runtime State

These are intentionally excluded from Git:

- A100 `results`: about `81G`
- A100 `cache`: about `30G`
- A100 `hf_home`: about `23G`
- A100 `weights`: about `16G`
- local `.hf_local_cache`: about `27G`
- local `results`: about `26G`
- local `visuals`: about `15G`
