# Artifact Manifest

Date: 2026-07-15

This manifest separates GitHub-safe source files from archive-only artifacts.

## GitHub-Safe Source Already Migrated

- `assets/`: core method, generation, texturing, rendering, metrics, and launch scripts.
- `tests/`: lightweight test code.
- `scripts/`: helper scripts.
- `tools/`: auxiliary small tools.
- `docs/`: text docs, tables, JSON/CSV summaries, migration notes, selected AgentDoc mirrors.
- `paper_siga/`: LaTeX source, BibTeX, draft tables, lightweight metadata, and compact figures directly referenced by `main.tex`.
- `experiments/trellis_classic_dense_smoke_20260529/`: small remote-only smoke probe from A100.

Current staged repository size: about `35M`.

## Archive-Only Local Artifacts

Source root:

```text
/Users/fanta/code/agent/Code/recursive_3d_generative_growth
```

Large local artifact directories:

| Path | Size | Notes |
|---|---:|---|
| `results/` | `26G` | Local experiment outputs and derived metrics. |
| `visuals/` | `15G` | Rendered contact sheets, galleries, selected visual pulls. |
| `.hf_local_cache/` | `27G` | Re-downloadable model/cache data. |
| `docs/` | `2.2G` | Text docs plus generated inventories/galleries; text subset migrated. |
| `paper_siga/` | `495M` | Dirty Overleaf source plus many generated figures; source subset migrated. |
| `.venv_render/` | `206M` | Local rendering env; rebuildable. |
| `downloads/` | `165M` | Downloaded helper assets; archive only if needed. |
| `.worktrees/` | `128M` | Local worktree remnants. |

## Archive-Only A100 Artifacts

Remote root:

```text
a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
```

Large remote artifact directories:

| Path | Size | Notes |
|---|---:|---|
| `results/` | `81G` | Main GLB/OBJ/PLY/PBR experiment outputs, V2-V67 strict visual matched runs, gen3D baselines, Hunyuan probes. |
| `cache/` | `30G` | Rebuildable runtime cache; deletion candidate after review. |
| `hf_home/` | `23G` | Hugging Face cache; archive only if offline reproducibility matters. |
| `weights/` | `16G` | Model weights; archive or redownload policy required before deletion. |
| `inputs/` | `1.6G` | Generated OBJ inputs and manifests; keep selected final manifests/inputs. |
| `envs/` | `772M` | Environment snapshot; replace with env docs where possible. |
| `repos/` | `272M` | TRELLIS classic and Hunyuan3D snapshots/archives. |
| `runs/` | `51M` | 2026-05-29 TRELLIS classic run outputs. |
| `logs/` | `8.5M` | Logs; small enough to archive with selected runs. |

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
