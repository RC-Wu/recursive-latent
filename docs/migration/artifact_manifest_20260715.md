# Artifact Manifest

Date: 2026-07-15

This manifest separates GitHub-safe source files from archive-only artifacts.

Cleanup status: after this manifest was written, the user approved deletion groups `A`, `B`, and `C`. The large local and A100 artifact directories listed below were removed on 2026-07-15. See `deletion_review_20260715.md` for the exact cleanup log.

## GitHub-Safe Source Already Migrated

- `assets/`: core method, generation, texturing, rendering, metrics, and launch scripts.
- `tests/`: lightweight test code.
- `scripts/`: helper scripts.
- `tools/`: auxiliary small tools.
- `docs/`: text docs, tables, JSON/CSV summaries, migration notes, selected AgentDoc mirrors.
- `paper_siga/`: LaTeX source, BibTeX, draft tables, lightweight metadata, and compact figures directly referenced by `main.tex`.
- `experiments/trellis_classic_dense_smoke_20260529/`: small remote-only smoke probe from A100.

Current GitHub-uploaded working-tree payload after adding compact paper figures: about `55M`; the local clone is about `83M` including `.git` objects.

## Removed Local Artifacts

Source root:

```text
/Users/fanta/code/agent/Code/recursive_3d_generative_growth
```

Large local artifact directories that were removed after approval:

| Path | Size | Notes |
|---|---:|---|
| `results/` | `26G` | Deleted. Local experiment outputs and derived metrics. |
| `visuals/` | `15G` | Deleted. Rendered contact sheets, galleries, selected visual pulls. |
| `.hf_local_cache/` | `27G` | Deleted. Re-downloadable model/cache data. |
| `docs/` generated media | part of `2.2G` | Generated media deleted; text docs kept where present. |
| `paper_siga/figures/` | `243M` | Deleted; compact main-paper figures were already migrated. |
| `.venv_render/` | `206M` | Deleted. Local rendering env; rebuildable. |
| `downloads/` | `165M` | Deleted. Downloaded helper assets. |
| `.worktrees/` | `128M` | Deleted. Local worktree remnants. |

## Removed A100 Artifacts

Remote root:

```text
a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
```

Large remote artifact directories that were removed after approval:

| Path | Size | Notes |
|---|---:|---|
| `results/` | `81G` | Deleted. Main GLB/OBJ/PLY/PBR experiment outputs, V2-V67 strict visual matched runs, gen3D baselines, Hunyuan probes. |
| `cache/` | `30G` | Deleted. Rebuildable runtime cache. |
| `hf_home/` | `23G` | Deleted. Hugging Face cache. |
| `weights/` | `16G` | Deleted. Model weights. |
| `inputs/` | `1.6G` | Deleted. Generated OBJ inputs and manifests. |
| `envs/` | `772M` | Deleted. Environment snapshot. |
| `repos/` | `272M` | Deleted. TRELLIS classic and Hunyuan3D snapshots/archives. |
| `runs/` | `51M` | Deleted. 2026-05-29 TRELLIS classic run outputs. |
| `logs/` | `8.5M` | Deleted. Logs. |

## Suggested External Archive Groups

Group A, high priority:

- A100 `results/strict_visual_matched_texture_V23*` through `V67*`
- A100 `results/real_case_ablation*`
- A100 `results/experiment3_sparse_latent_vs_meshspace_20260511`
- Local selected `visuals/` and `paper_siga/figures/` final images
- Local `docs/evaluation/case_inventory_v1_v60_20260512`

Group B, reproducibility:

- A100 `inputs/`
- A100 selected `logs/`
- A100 `runs/`
- model `weights/` if redownload is not guaranteed

Group C, rebuildable:

- A100 `cache/`
- A100 `hf_home/` if model cache can be reconstructed
- local `.hf_local_cache/`
- local `.venv_render/`

## Do Not Put In Normal Git

- raw GLB/OBJ/PLY/DRC pools
- model weights
- HF/Torch/Triton caches
- generated video files
- complete visual galleries
- Overleaf compile products
