# PS-RSLE Revision and Metric Parallel Plan

Date: 2026-05-13

## Required Reading Links

- User response and requirements: `/Users/fanta/Downloads/三部分整理稿合并分节版.md`
- Current paper source: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex`
- Previous review report: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/paper/ps_rsle_story_method_closure_review_zh_20260513.md`
- Paper repo: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga`
- Project root for assets/results/scripts: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`
- Remote A100-2 root to inspect when needed: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`

## Current Baseline

- `paper_siga` was fast-forwarded to `overleaf/master` commit `e0f76b3`.
- Latest `main.tex` now contains new controlled sparse-latent resampling and projection text, but still has TODOs in abstract/contributions, 4.4, and 4.5.
- User explicitly says the strong projection/reprojection claim should be used and that the remote implementation exists; therefore the revision should write the strong method story while removing TODOs by inspecting code and using implementable descriptions.
- User requires two parallel tracks: paper rewriting and metric evaluation.
- User requires four subagents.

## Workstreams

### A. Metrics and Results

Goal: choose and compute compact metrics for Table 3, Table 4, and the two ablation tables, using consistent metrics where possible.

Tasks:
- Locate meshes/GLBs/OBJs and existing CSV/JSON results for traditional comparison, mesh-online/generator baselines, projection ablation, and naturalization/control ablation.
- Identify reusable mesh metrics: occupancy component count, occupancy largest-component ratio, welded component count, non-manifold/boundary diagnostics, face count, possibly roughness or local artifact proxy.
- Avoid metrics the user explicitly does not want: GLB size, runtime, broad PBR/export discussion.
- Produce regenerated or supplemental tables with no std columns unless absolutely required.
- Decide whether CLIP/aesthetic/GPT-4o can be run quickly; if not, document exact blocker and leave stable mesh metrics.

### B. Paper Rewrite

Goal: rewrite the manuscript to match the user's requested story and structure.

Priority edits:
- Abstract final sentence: structural/connectivity metrics comparable to classical controls, mesh/visual diagnostics stronger.
- Introduction: shorten by about 20-30%, cite Fig. 2, remove photo credits from caption or move them to less intrusive text.
- Contributions: four aligned claims: state formulation, handle/rule/proposal executor, controlled resampling plus projection/reprojection stabilizes state, empirical comparison with structural and mesh/visual metrics.
- Related Work: rename 2.4 to sparse editing and structure-conditioned control; remove standalone "Taken together" position paragraph or merge it tightly; cite Fig. 3.
- Preliminaries: clean symbols; use Sparse Latent 3D Generators wording; define `V` and decoded/projection support `U` only where needed.
- Method title: `Method`.
- Program State and Executor: define root descriptor, active handles, active/inactive state, support update, and admission gates without over-formal tables.
- 4.4 Controlled Sparse-Latent Resampling: short, practical; flow-matching sampling, mask, blend, decode, KV cache proportional blending; remove SDEdit wording and excessive formulas.
- 4.5 Projection: shorter, operational; decode/project/re-encode or naturalize/re-encode round trip; remove vague TODOs.
- Delete or absorb 4.6 Scope and Implementation Notes.
- Experiments: remove claims-under-test paragraph and weak transform-admission section as main section; combine task definitions, baselines, metrics into 5.1; organize comparisons as traditional methods, mesh-online/generator methods, two ablations, controllability.
- Remove PBR/GLB/export-heavy discussion from main text.
- Discussion/Conclusion: update after revised story.
- Appendix: split appendix into a separate `.tex` file and keep only necessary main figures/tables in main text.

### C. Figure/Table Audit

Goal: render and inspect method figures and identify exact text edits needed.

Tasks:
- Render/read Figure 4 sparse latent generator interface.
- Render/read Figure 5 `figures/personal/main_method.pdf`; the user says the small file is the correct overview figure. Do not assume it is wrong by file size.
- Find and inspect current Figure 6 voxel/projection schematic from latest Overleaf update.
- Table 1 (`tab:rule-families`): assess position, column widths, language, and whether it should remain in Method near Program State.
- Figure 10: identify columns and write concise explanation or instructions for labels.
- Figure 7/8 line plots: decide whether they serve the revised story; keep only if they support controllability or projection stability.

### D. Remote Implementation and Citations

Goal: inspect code for strong projection/reprojection and resampling/KV-cache descriptions, and verify citation needs.

Tasks:
- Search local and remote assets for projection/reprojection, `decode`, `project`, `reencode`, `reproject`, `roundtrip`, `cache`, `kv`, `flow`, `mask`, and metric scripts.
- Identify exact implementation language for root descriptor, handle transfer, mask/boundary handling, sparse transform support discretization, and KV cache blending. If code is split across machines and not present, write a conservative implementable description consistent with user's statement.
- Verify existing BibTeX keys for baselines: L-system/procedural references, Hunyuan3D, Trellis/Trellis2, TripoSR/TripoSR2 if used, CLIP or aesthetic metrics if introduced.
- Do not invent citations; use existing BibTeX or official/verified sources only.

## Integration Rules

- Main thread owns `paper_siga/main.tex` edits to avoid conflicts.
- Subagents are read-only unless explicitly scoped to create reports/scripts in disjoint paths.
- New metric scripts/results should go under project-root `results/` or `docs/progress/`, not inside Overleaf unless integrated intentionally.
- All edits should preserve user's current Overleaf text updates as the base.
- Use `apply_patch` for manual edits.
- Compile with `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` before claiming paper compiles.

## Deliverables

- Updated `main.tex` and any needed table/appendix files.
- Metric report and generated/updated table files for main quantitative tables.
- Figure audit note with exact figure text changes for the user to make manually.
- Progress log at `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/progress/ps_rsle_revision_metric_parallel_progress_20260513.md`.
