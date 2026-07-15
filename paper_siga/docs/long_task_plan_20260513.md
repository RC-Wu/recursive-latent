# PS-RSLE Paper Revision and Metrics Enrichment Plan

Goal: converge the Overleaf `main` branch into a publication-level paper with a closed story, stable method semantics, clean evidence boundaries, and strengthened quantitative metrics.

Current branch state:
- Working branch: `main`.
- Overleaf remote: `overleaf/master`.
- Latest pushed paper commit after the 2026-05-13 continuation batch: `ee0e319 Remove empty visual-score columns from active tables`.
- Rule: fetch Overleaf before every push; merge/rebase only after inspecting remote text changes; do not force push.
- Rule: do not bulk-add untracked images or generated visual assets unless they are referenced by the active paper.

## Story Contract

The paper answers one central question:

Can a frozen sparse latent 3D generator be used as a learned local realization substrate for finite-depth recursive 3D asset programs while every committed intermediate state remains attached, addressable, and rule-readable before later rules consume it?

The main invariant:

PS-RSLE keeps only root-attached or connector-certified support and active handles visible to later rules. Detached fragments may remain as inactive diagnostics, but they cannot become future parents, frontiers, or motif sources.

The paper must not claim:
- general topology recovery from arbitrary meshes;
- watertightness or physical growth simulation;
- universal superiority over mature procedural systems;
- that every reported run executed the full codec-closed decode-project-reencode loop unless explicitly reported;
- that deterministic projection/masked-naturalization proxy experiments are Trellis2 runtime handle graphs.

## Workstreams

### 1. Paper Structure

Target order:
- Abstract: problem, PS-RSLE state/projection idea, strongest evidence, boundary.
- Introduction: compress background and foreground state contamination before terminal cleanup.
- Related Work: procedural state, learned structure/programs, native sparse latent generators, sparse editing/control.
- Preliminaries: finite-depth programs and sparse latent generator interface only.
- Method: program state, proposal/admission, recursive transition, controlled sparse-latent resampling, admissibility projection.
- Experiments: tasks/baselines/metrics, projection ablation, sparse-latent versus mesh-space alternatives, traditional target comparison, masked local realization.
- Appendix: broad galleries, rule matrices, diagnostic audits, depth/space competition curves, non-claim-bearing material.

Immediate structural edits:
- Keep projection ablation as the central claim-bearing experiment.
- Continue compressing the main body toward the target 7-page core plus separate visual/supplement material.
- Split or quarantine appendix/status material so the main manuscript, visual-only pages, and supplement are clearly separated.
- Continue final-paper tone cleanup in appendix captions and table titles.
- Keep visual-scoring experiments out of active tables unless they are fully reviewed and explicitly added.

### 2. Metrics Enrichment

Primary metrics to preserve in the main evidence chain:
- Occupancy largest-component ratio (Occ. LCR): realized-support connectivity diagnostic.
- Root reachability: controlled trace/proxy state reachability before later rules fire.
- Orphan active handles: count of active handles not allowed to be future state.
- Handle survival: projected active handles retained after the state gate.
- Execution pass: controlled admissible-state proxy.

Candidate derived metrics from existing files:
- Occupancy-state gap: median Occ. LCR minus median root reachability.
- Connector survival gain: connector-aware handle survival minus prune-only handle survival.
- Failure localization counts: clean/state/surface/drift/multi causes by variant.
- Matched component deltas in Experiment 3: PS-RSLE versus one-shot, latent-copy, and mesh-copy controls.

Remote/model-dependent metrics needing separate runs:
- Additional deterministic image/mesh diagnostics only if explicitly reviewed and added later.
- Additional mesh quality metrics on GLB/OBJ assets not already measured; the current offline dry-run discovers existing tables/assets but does not compute rich GLB metrics.
- Any Trellis2 runtime handle/token audit beyond the current deterministic proxy and sparse-latent workflow artifacts.

### 3. Subagent Use

Completed read-only reports:
- Story/structure review.
- Method/preliminaries symbol review.
- Metrics audit.
- Experiments/figures/tables evidence-chain audit.
- Remote/A100-2 implementation audit.

Recent subagent batches:
- Story/structure, citation/caption, method-symbol, and metrics agents reviewed the current draft.
- Metrics agent added an offline dry-run mesh metrics discovery pipeline for deterministic local metrics.

### 4. Push Discipline

For every small paper edit:
1. `git fetch overleaf`.
2. Rebase local `main` if remote moved.
3. Make one scoped edit.
4. Compile with `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` when the edit affects active LaTeX.
5. Run marker scans for conflict markers, active TODOs, empty visual-score columns, and overclaiming phrases.
6. Commit with a short descriptive message.
7. Fetch again and push `main:master`.

Verification commands:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
rg -n "undefined|Citation.*undefined|Reference.*undefined|Fatal|Emergency|multiply defined|Label.*multiply|Undefined control sequence|LaTeX Error|Package .* Error|There were undefined references" main.log
rg -n "TODO|<<<<<<<|=======|>>>>>>>|FlowSample|topology drift|full PS-RSLE|full sparse-latent executor" main.tex drafts figures -g '*.{tex,md}'
git diff --check
```
