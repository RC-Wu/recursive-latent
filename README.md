# Recursive Latent

This repository contains the source code, experiment scripts, documentation, and paper-facing materials for the SIGGRAPH Asia-oriented **Projection-Stabilized Recursive Sparse-Latent Grammar** project.

The project studies how a frozen sparse 3D generator, primarily TRELLIS/TRELLIS.2-style sparse latent models, can be reused as a recursive 3D asset generation substrate. The current method line is usually referred to in the project notes as **PS-RSLG**:

```text
recursive grammar owns topology/support
generator owns local sparse-latent realization and texture/material priors
projection/re-encoding stabilizes every recursive step
```

## Repository Scope

This GitHub repository is intentionally source-first. It contains code, launchers, tests, text documentation, and lightweight paper source. It does **not** contain the full experiment outputs, model caches, raw GLB/OBJ/PLY pools, or visual galleries.

Large artifacts are tracked separately in the migration manifests under `docs/migration/`.

## Directory Map

- `assets/`: core scripts for procedural roots, sparse-latent grammar experiments, texturing/export, metrics, rendering, and ablations.
- `tests/`: lightweight tests for selected generators and evaluation helpers.
- `scripts/`: small helper scripts.
- `tools/`: auxiliary local tools.
- `docs/`: method notes, evaluation protocols, migration inventories, AgentDoc mirrors, and handoff documents.
- `paper_siga/`: LaTeX source, BibTeX, draft tables, lightweight figure metadata, and the compact figures directly referenced by `main.tex`. Large generated figure galleries are intentionally excluded.
- `experiments/trellis_classic_dense_smoke_20260529/`: small remote-only TRELLIS classic dense smoke probe recovered from `a100-2`.

## What Is Not Included

Excluded by design:

- `results/`
- `visuals/`
- `runs/`
- `weights/`
- `hf_home/` or `.hf_local_cache/`
- full generated `inputs/`
- raw GLB/OBJ/PLY/PBR outputs
- generated paper image pools and contact sheets

See `docs/migration/artifact_manifest_20260715.md` for the large artifact map and `docs/migration/deletion_review_20260715.md` for deletion candidates that require owner confirmation before removal.

## Main Historical Roots

Local Mac source root:

```text
/Users/fanta/code/agent/Code/recursive_3d_generative_growth
```

A100 root:

```text
a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
```

AgentDoc project root:

```text
/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth
```

## Current Method Summary

The strongest documented algorithmic spine is:

1. Start from a procedural or generated root mesh.
2. Encode into sparse 3D support / sparse latent state.
3. Apply a recursive grammar operator such as L-system branching, space-colonization competition, DLA/frontier growth, transform copy, radial/portal growth, or connector-aware variants.
4. Apply masked weak generator naturalization only where new growth was introduced.
5. Decode to mesh, project/prune/repair into an admissible state, and re-encode before the next recursive step.
6. Export texture/PBR-compatible assets for paper visualization.

The key empirical lesson in the current docs is that one-shot 3D generation, trivial latent copy, and mesh-space generated-root copy are useful baselines but do not reliably replace grammar-owned recursive state.

## Important Docs

- `docs/migration/a100_siga_project_inventory_20260715.md`
- `docs/migration/artifact_manifest_20260715.md`
- `docs/migration/deletion_review_20260715.md`
- `docs/agent_handoff_2026-05-10.md`
- `docs/evaluation/gen3d_and_ablation_evidence_audit_zh_20260510_agent.md`
- `docs/evaluation/evidence_matrix_for_revision_zh_20260510.md`
- `docs/evaluation/main_experiment_convergence_corrected_V67B_status_zh_20260512.md`
- `docs/evaluation/projection_masked_ablation_matrices_zh_20260511.md`

## Reproducibility Notes

The launch scripts still contain historical absolute paths from the A100 environment. Before rerunning experiments on a new machine, update:

- project root
- TRELLIS/TRELLIS.2 repo path
- model cache paths
- `HF_HOME`, `TORCH_HOME`, `TRITON_CACHE_DIR`, `XDG_CACHE_HOME`, `TMPDIR`
- GPU IDs

See `docs/migration/environment_notes_20260715.md`.

## Migration Status

This repository is the GitHub-uploadable subset of a larger local and A100 project. The full raw project footprint was about:

- local project root: `72G`
- A100 project root: `152G`

Only the compact source/documentation subset is committed here.
