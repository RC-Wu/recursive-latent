# PS-RSLE Story/Structure Next Edit Plan - 2026-05-13

Scope: read-only analysis of `paper_siga/main.tex` and nearby audit notes, with this single planning report as the only created file. I did not edit paper files, stage, commit, push, or revert any work. Current `paper_siga` HEAD is `976e1c0bbb13a79b2b46685fa49dbac19f0bc2cd` on `main`; the worktree already contains unrelated modified/untracked figure and draft assets.

User constraints applied:

- Use `Sparse Latent 3D Generators` as the preferred concept label where a title/heading/capitalized phrase is needed.
- Avoid framing the method as a grammar except for classical related-work terms such as `shape grammars`.
- Main claim: per-depth admissible executable state.
- Mesh/render metrics are supportive diagnostics and caveats.
- Remove or de-emphasize PBR/GLB/export/texture-path framing in the main story.
- Classical procedural methods are strong controls, not weak baselines.
- No std columns or mean-plus-std values in main tables.
- Prioritize closure using existing text/assets/results, without requiring new data.

## Current Story Diagnosis

The current draft is much stronger than earlier versions: the abstract, introduction, method, projection section, and discussion already center the right claim, namely that PS-RSLE commits only a projected, root-attached, rule-readable state before later rule selection. The remaining closure problems are mostly structural and rhetorical rather than experimental:

1. The experiment section still mixes four roles in the main flow: state-validity evidence, operator admission, traditional-control comparison, and texture/export compatibility. This weakens the per-depth executable-state story.
2. Several main paragraphs still foreground texture path, textured assets, GLB/export, or optional rendering compatibility even though the user wants these de-emphasized.
3. The included table files are not aligned with the manuscript story: projection and masked-naturalization tables still contain `\pm` values; Experiment 3 still says `PS-RSLG` and includes weak columns (`State`, `Proj.`, `Copy`, `Raw comp.`); metric headers such as `C_{r0}` are not reader-friendly.
4. The method text avoids grammar language, but figure-file text and older draft/table assets still use grammar/PS-RSLG terminology. The manuscript should not reintroduce that framing through included tables or figure labels.
5. The conclusion still says `asset export` is one of the distinct roles. That phrase is now off-claim and should become `rendered asset inspection` or simply `visual diagnostics`.

The safest next pass is not a rewrite. It should be a sequence of small, reviewable edits that first remove contradictions, then tighten experiment flow, then adjust captions/tables.

## Batch 1 - Global Naming and Claim Hygiene

Goal: remove terminology that conflicts with the current framing. This is the lowest-risk batch because it does not alter the experiment claims or require new data.

Targets:

- `main.tex:57` keywords.
- `main.tex:122`, `126`, `132`, `147-169`, and any title/caption phrase that names the substrate.
- Included tables under `drafts/*.tex` that still say `PS-RSLG`.
- Figure text files or editable sources for `figures/personal/main_method.pdf` and `figures/method_projection_admissibility_gate_20260510.pdf` if/when figure assets are edited.

Suggested edits:

1. Keywords line:

Current:

```tex
\keywords{recursive 3D generation, procedural modeling, sparse latent representation, projection, executable state, Trellis2}
```

Suggested:

```tex
\keywords{recursive 3D generation, procedural modeling, Sparse Latent 3D Generators, projection, executable state}
```

2. Related work subsection heading at `main.tex:124`:

Current:

```tex
\subsection{Native 3D Generation and Sparse Latents}
```

Suggested:

```tex
\subsection{Native 3D Generation and Sparse Latent 3D Generators}
```

3. First sentence of generator interface at `main.tex:149`:

Current:

```tex
Let $\theta$ denote a pretrained sparse latent 3D generator with fixed parameters.
```

Suggested:

```tex
Let $\theta$ denote a pretrained Sparse Latent 3D Generator with fixed parameters.
```

Use the capitalized phrase sparingly for headings/definitions; keep lowercase in running prose when grammar requires it.

4. Replace all included-table `PS-RSLG` labels with `PS-RSLE`.

Known files:

- `paper_siga/drafts/projection_ablation_main_table_20260511.tex`: `full PS-RSLG`.
- `paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`: PS-RSLG rows/caption.

Suggested replacement:

```tex
full PS-RSLE
```

and

```tex
PS-RSLE
```

5. Do not replace classical `shape grammars` in Introduction/Related Work/Appendix. Those are legitimate related-work terms.

## Batch 2 - Abstract/Introduction Closure Tune

Goal: make the abstract and introduction end with the exact story the paper can close: per-depth admissible executable state first; mesh/render evidence second.

Targets:

- Abstract: `main.tex:30`.
- Introduction scope/question: `main.tex:95`.
- Contributions: `main.tex:100-103`.

Suggested abstract replacement for the last two sentences:

Current ending:

```tex
Experiments on branching, frontier-growth, and transform-copy recursive programs show that PS-RSLE preserves executable state across recursive steps. On the reported finite-depth benchmarks, PS-RSLE matches the structural connectivity and stability expected from strong procedural controls while improving mesh-quality and visual diagnostics relative to direct generator, copy-based, and post-hoc cleanup baselines.
```

Suggested:

```tex
Experiments on branching, frontier-growth, and transform-copy recursive programs show that PS-RSLE preserves per-depth executable state across recursive steps: detached candidates are not allowed to become future parents, frontiers, or motif sources. Mesh and render diagnostics then show where this state invariant supports selected finite-depth assets, while remaining separate from topology, material, and universal-quality claims.
```

Suggested replacement for `main.tex:95`:

```tex
Within this scope, the main question is whether a sparse-generator-coupled program state can remain attached, addressable, and reusable at every derivation depth. Mesh quality and rendered appearance are evaluated as downstream diagnostics of the realized assets, not as substitutes for executable-state validity.
```

Suggested contribution 4 replacement at `main.tex:103`:

```tex
\item We instantiate PS-RSLE on a frozen Sparse Latent 3D Generator and evaluate it against procedural, generator-based, copy-based, and cleanup baselines, treating classical procedures as strong structural controls and mesh/render quantities as supporting diagnostics.
```

Rationale: this makes the paper's closure criteria explicit before the experiments.

## Batch 3 - Related Work Positioning Tightening

Goal: keep the related work strong but reduce appearance/material emphasis and avoid implying the paper competes on broad asset-generation quality.

Targets:

- Procedural related work: `main.tex:110`.
- Native 3D generation paragraph: `main.tex:126`.
- Related work synthesis: `main.tex:132`.

Suggested replacement for the end of `main.tex:110`:

Current ending:

```tex
As a result, purely procedural assets can preserve the intended recursive layout while remaining visually rigid, repetitive, or limited to the local detail and material variation encoded by the handcrafted operators. PS-RSLE targets the same recursive asset families, but uses a frozen sparse latent 3D generator as a learned local realization prior and uses projection to keep rule-produced structure and generator-produced geometry inside a single recursive execution loop.
```

Suggested:

```tex
As a result, purely procedural assets can preserve the intended recursive layout while leaving surface realization and local variation to separate hand-authored machinery. PS-RSLE treats these systems as strong structural controls: it keeps their explicit recursive-state contract, but couples rule-proposed local edits to a frozen sparse latent generator and projects each realized candidate before later rules can read it.
```

Suggested replacement for the first half of `main.tex:126`:

```tex
Large-scale 3D datasets and recent generative models have made learned shape priors increasingly useful for geometry realization~\cite{objaverse2023,objaverseXL2023}. Object-latent and set-latent models such as Shap-E and 3DShape2VecSet synthesize 3D shapes from compact latent codes or high-level conditions~\cite{shapE2023,shape2vecset2023}. Optimization-based and feed-forward systems can synthesize or optimize geometry and asset-like outputs from image or text prompts~\cite{poole2023dreamfusion,lin2023magic3d,chen2023fantasia3d,dreamgaussian2024,assetgen2024,hunyuan3d2025}. Sparse Latent 3D Generators are especially relevant to our setting because they expose token support, latent features, encoders, decoders, and local sampling paths~\cite{trellis2025,trellis2project}.
```

This removes `PBR-capable outputs` without weakening citations.

Suggested replacement for `main.tex:132`:

```tex
Taken together, prior work provides procedural structure generators, learned program or hierarchy priors, native 3D asset generators, and local editing or structural control. What remains missing is an admissible recursive transition over frozen sparse latent generator states. PS-RSLE addresses this gap by executing user-authored finite-depth rules over sparse latent tokens and active handles, projecting each decoded candidate into root-attached active support, and re-encoding the projected state before later rules can read it. This positioning also shapes evaluation: recursive-state validity is primary; structural connectivity, mesh quality, and rendered views are diagnostics. Morphology and fractal descriptors can be useful for branching or porous examples~\cite{raumonen2013treeModels,martinez2018minkowskiPorosity,cheeseman2022fractalCaution}, but the core question is whether the active state remains valid before the next recursive step.
```

## Batch 4 - Method Figure/Table Text Alignment

Goal: avoid letting figures/tables undermine the method story. This batch is partly LaTeX and partly editable figure assets; no new experimental data is needed.

Targets:

- Method overview figure: `main.tex:175-180`, asset `figures/personal/main_method.pdf`.
- Projection gate figure: `main.tex:417-445` body and figure around current Figure 6.
- Rule family table: `main.tex:235-276`.

Method overview figure-file text changes:

- `Rule library / Grammar` -> `Typed Rule Library` or `Rule Library`.
- `Inputs` -> `Input`.
- `Outputs Textured (optional) asset` -> `Output Asset`.
- `AdmitApply` -> `Admit / Apply`.
- Add a loop arrow/label from next state to current state: `repeat for d = 0 ... D-1`.
- If space permits: `Current Projected State` -> `Current State s_d`; `Next Projected State` -> `Projected Next State s_{d+1}`.

Caption addition for `main.tex:179` after the final sentence:

```tex
The return arrow denotes repeating this committed transition until the prescribed finite depth $D$.
```

Projection gate figure-file text changes:

- Replace `z_d active state` with `s_d active state`.
- Replace `projected z_{d+1}` with `projected s_{d+1}`.
- Replace formula using `z`/`Pi_{\theta,\lambda_d}` with notation consistent with the paper:

```tex
(x^\star_{d+1}, A_{d+1})=\Pi_{\lambda_d}(x_{d+1},\widetilde A_{d+1},s_d,\Gamma_d)
u_{d+1}=\operatorname{Enc}_{\theta}(x^\star_{d+1},y)
```

- Replace `conservative prune-only policy` with `conservative projection policy` or `prune/demote policy`.
- Replace `budget / renderability` with `budget / validity` if the figure is redrawn.

Rule family table edits:

Current table spec at `main.tex:239`:

```tex
\begin{tabular}{@{}p{0.16\textwidth}p{0.24\textwidth}p{0.34\textwidth}p{0.20\textwidth}@{}}
```

Suggested:

```tex
\small
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}p{0.18\textwidth}p{0.18\textwidth}p{0.35\textwidth}p{0.23\textwidth}@{}}
```

Header:

```tex
Rule family & Reads active handles & Proposal record & Supported structures \\
```

Conservative row wording:

```tex
Roots, vines, tree crowns, branching forms.
```

```tex
Attraction- or stochastic-guided support seeds with attachment certificates and frontier updates.
```

```tex
Transformed support seeds, copied or seeded features, candidate motif handles, and transform metadata.
```

```tex
Local support allocation and feature-seed refinement under a token budget.
```

Rationale: table becomes a compact executor vocabulary map, not a broad capability claim.

## Batch 5 - Experiment Section Opening and Metrics Taxonomy

Goal: make the experiment section read like a claim-bearing sequence instead of a gallery plus compatibility report.

Targets:

- `main.tex:506-533`.

Suggested replacement for `main.tex:506-507`:

```tex
\paragraph{Claims under test.}
The main experiments are organized around the execution claim. First, we test whether per-depth projection prevents invalid decoded support from remaining executable. Second, we test whether ordinary one-shot generation, direct latent copy, and mesh-space recursion can replace a projected sparse-latent state. Third, we compare selected PS-RSLE outputs with classical procedural controls while keeping structural metrics separate from mesh and render diagnostics. We do not claim that every operator family is solved, that rendered appearance proves topology, or that DLA/crystal-inspired examples are physical simulations.
```

Suggested replacement for `main.tex:509-512`:

```tex
\subsection{Task Definitions and Protocol}
We evaluate three task families chosen to stress different executable-state operations: tree/root/vine branching for connected handle recursion, coral/crystal/porous frontier growth for attachment and fragmentation stress tests, and transform-copy assets for reusable motifs and local zoom structure. The executor is training-free around a frozen Sparse Latent 3D Generator. No generator weights are updated. Each run fixes the root, rule family, depth, token budget, projection schedule, condition, seed, renderer, and camera before evaluation.

Table~\ref{tab:coverage-exemplar-tasks} is moved to Appendix~\ref{app:moved-main-tables}; the main protocol uses the same coverage matrix to define comparison domains and metrics.
```

Suggested replacement for `main.tex:530-533`:

```tex
\subsection{Baselines and Metrics}
Baselines include pure procedural meshes, smoothed/remeshed procedural meshes, one-shot Trellis2 image-to-3D, image-entry then recursion, direct coordinate recursion, mesh-space recursion, trivial latent transform/copy, full flow repair, masked flow repair, weak masked blend, final-only projection, projection-stabilized masked blend, and attachment-aware executor variants. Procedural baselines are structural controls, not material-quality strawmen.

We group measurements by claim role. Recursive-state validity is measured by root reachability, orphan active handles, handle survival, and committed-pass rate. Structural connectivity is measured by occupancy or surface-sampled voxel component count and largest-component ratio under a stated radius/graph. Mesh diagnostics include raw or welded components, face count, non-manifold or boundary indicators when available, and render success. Rendered views are used for qualitative inspection of local realization and recursive detail. These diagnostics support the state-validity claim but do not replace it.
```

Rationale: this directly resolves the texture/export drift and gives table captions a vocabulary to reuse.

## Batch 6 - Projection Ablation Main Evidence

Goal: keep this as the empirical centerpiece and make it table-compliant.

Targets:

- `main.tex:535-576`.
- Included file `drafts/projection_ablation_main_table_20260511.tex`.

Main text: current prose is good. Make only two small changes.

1. At `main.tex:537`, avoid leaning on token curve as main proof:

Current:

```tex
Figure~\ref{fig:space-competition-depth-curves} reports the corresponding token-growth curves: conservative competition grows slowly, while fork and side-branch variants consume more support and enter the current stability-expression boundary.
```

Suggested:

```tex
Figure~\ref{fig:space-competition-depth-curves} reports token-growth diagnostics for the same runs: conservative competition grows slowly, while fork and side-branch variants consume more support and mark the current stability-expression boundary.
```

2. Figure 2 projection ablation caption at `main.tex:561`:

Current ending:

```tex
The visual is a deterministic structural ablation; textured asset quality is evaluated separately.
```

Suggested:

```tex
The visual is a deterministic structural ablation; local surface quality is evaluated separately.
```

Table file required edit:

- Remove all `\pm` entries from `drafts/projection_ablation_main_table_20260511.tex`.
- Replace each `mean \pm std` cell with the mean value only.
- Replace `full PS-RSLG` with `full PS-RSLE`.
- Caption already says four families and three seeds, so sample count is preserved without std columns.

Suggested caption tweak at `main.tex:569`:

```tex
\caption{Experiment 2 projection ablation over four root families and three deterministic seeds, reported as aggregate values without standard-deviation columns. Occ. LCR is the largest-component ratio under the stated occupancy/surface-sampled voxel graph. Root reachability, orphan active handles, handle survival, and committed pass are trace/mesh proxies for whether active recursive state remains attached to the root before the next rule fires. Final-only projection reaches high terminal LCR but keeps the same invalid active-state statistics as no projection; the benefit of projection inside the loop appears in the handle-state and commit columns.}
```

## Batch 7 - Experiment 3 Novelty Gate

Goal: make Experiment 3 answer one question: can one-shot/copy/mesh-space alternatives replace executable sparse-latent state? Avoid texture-path fairness as the lead.

Targets:

- `main.tex:579-595`.
- Included file `drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`.

Suggested replacement for `main.tex:581-583`:

```tex
Traditional L-system, IFS, DLA, and space-colonization programs are strong structural controls, so Experiment~3 asks a different question: whether generator-only or mesh-space alternatives can replace a native projected sparse-latent state. The one-shot row receives the full recursive target guide. The trivial-copy row receives a generated root and then copies decoded support without typed handles, projection, or re-encoding. The mesh-space rows generate or import a root primitive and then apply the same deterministic scale/rotate/translate schedule. These rows are not weak baselines; they isolate what is missing when recursion is performed outside the executable sparse-latent state.
```

Keep `main.tex:585` mostly as is, but replace the final sentence:

Current:

```tex
PS-RSLE is the only evaluated row that runs the intended state-transition machinery; the component and occupancy diagnostics here are selected proxy evidence, while handle-level validity is tested by the projection and trace ablations rather than by this table alone.
```

Suggested:

```tex
PS-RSLE is the only evaluated row that runs the intended state-transition machinery; the component and occupancy diagnostics here are supportive evidence, while handle-level validity is established by the projection and trace ablations rather than by this table alone.
```

Table file required edit:

- Replace all `PS-RSLG` with `PS-RSLE`.
- Remove main-table columns `State`, `Proj.`, `Copy`, and likely `Raw comp.`.
- Keep `Occ. comp.` and `LCR`.
- Add only already-defined common diagnostics if available for every row, e.g. `Faces` or `Welded comp.`. If not consistent, keep the table compact and move raw-face components to supplementary diagnostics.

Suggested main table schema:

```tex
Case & Method & Occ. comp. & LCR & Faces & Notes
```

or, if width is tight:

```tex
Case & Method & Occ. comp. & LCR & Diagnostic caveat
```

Do not add new metrics that require new runs.

## Batch 8 - Traditional Controls Comparison

Goal: preserve the important fair-control story while resolving current figure/caption mismatch and metric naming.

Targets:

- `main.tex:597-625`.
- Figure 10 asset/caption: `figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.png`.
- Included table `figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`.

Suggested structural edit:

Move or remove the two standalone figures at `main.tex:597-611` from the main flow unless page budget allows them as supplemental evidence. They interrupt the Experiment 3 -> traditional comparison story and reintroduce texture-path language.

If keeping the space-colonization figure in main, use a tighter caption:

```tex
\caption{Traditional space-colonization OBJ tube baseline under a fixed Blender/Cycles protocol. The baseline is structurally useful for branch/tip/coverage metrics and is treated as a strong recursive-state control; visual schematicness is not used as structural failure evidence.}
```

Move `traditional_baseline_texture_rerun1554_20260509.pdf` to appendix or keep only as a supplement. If it must remain in main, replace caption with:

```tex
\caption{Traditional procedural supports rendered under the same inspection protocol used for selected PS-RSLE outputs. The figure is a fairness check: classical supports can be connected and visually inspectable, so the comparison is not against intentionally weak structures. Structural metrics and executable-state claims remain separate from appearance.}
```

Figure 10 caption at `main.tex:619`: add explicit column order and remove any mismatch with selected asset.

Suggested replacement:

```tex
\caption{Strict traditional targets and selected PS-RSLE assets under a matched white-background overview and single-level camera-zoom protocol. Columns are, from left to right, traditional overview, traditional zoom, PS-RSLE overview, and PS-RSLE zoom. Traditional programs provide explicit recursive structure and are treated as strong structural controls. PS-RSLE adds generator-native local realization while retaining finite-depth execution semantics. The DLA/frontier row uses a coral asset rather than a semantically unrelated object. The IFS/transform row is a target-matched branch-hierarchy stress test; transform-copy operator admission for lattice and pyrite cases is evaluated separately. Gray rectangles indicate the camera footprint used for the zoom panel. Quantitative diagnostics and caveats are reported in Table~\ref{tab:main-experiment-selected-metrics}.}
```

Important asset consistency note:

- Current `main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.json` reportedly says the IFS ours variant is `current_v21` and visually weak.
- Nearby QA variants, especially `main_experiment_traditional_vs_ours_upright_4x4_zoom_QA_v63C_20260512.png`, appear intended to match the caption's "visually clearer recursive branch asset."
- Before editing prose, select the intended Figure 10 asset. If the asset is not changed, revise `main.tex:613` and `625` to stop claiming a clearer branch asset.

Main selected metrics table required edits:

- Rename `C_{r0}` header to `Comp. r0` or `Surf. comp. r0`.
- Define in caption: `connected component count at radius 0 under the surface-sampled voxel graph`.
- Replace `texture-export islands` with `tiny surface islands` or `aliasing-scale islands`.
- Consider dropping `Box dim.` if width is tight; it is less story-critical than component/LCR/welded component diagnostics.
- Reconcile the included V67B table against the refreshed `results/paper_metric_refresh_20260513/main_experiment_selected_metrics_table_20260513.tex`, especially the IFS/Ours row, before final integration.

Suggested replacement for `main.tex:625` if keeping current claim conservative:

```tex
The comparison separates structural controls from visual and mesh diagnostics. In the space-colonization row, the procedural target gives a connected branch/tip scaffold, while the selected PS-RSLE tree crown adds learned local realization and remains connected after one-voxel surface dilation. In the L-system row, the selected PS-RSLE asset matches the target's depth and density better than earlier sparse branch attempts, but fine tapered spikes create exact radius-0 surface-voxel islands; we therefore report it as radius-1 connected rather than as a watertight or exact-contact proof. In the DLA/frontier row, PS-RSLE changes the visual regime from blocky accretion to a coral-like connected frontier asset and is single-component under the exact surface-voxel diagnostic. In the IFS/transform row, the displayed branch asset is a branch-hierarchy stress test, while formal transform-copy admission remains attached to the lattice, radial, and pyrite rows in the operator-screening experiment. These results support selected finite-depth recursive asset realization under a projected executor; they do not claim physical DLA simulation, botanical realism, watertight topology, direct IFS equivalence for the branch visual, or universal superiority over mature hand-authored procedural systems.
```

## Batch 9 - Masked Local Realization Section

Goal: retain the local-realization ablation but remove export/effective-resolution framing and std-style prose.

Targets:

- `main.tex:627-684`.
- Included table `drafts/masked_naturalization_main_table_20260511.tex`.

Section label/title:

Current:

```tex
\subsection{Masked Local Realization and Recursive Detail}
\label{sec:naturalization-export-resolution}
```

Suggested:

```tex
\subsection{Masked Local Realization under Projected State}
\label{sec:masked-local-realization}
```

Replacement for `main.tex:629`:

```tex
Projection-stabilized states can be decoded into meshes for local realization and visual inspection. Figure~\ref{fig:connected-best-expansion-textured}, Figure~\ref{fig:pyrite-hq-depth-textured}, and Figure~\ref{fig:coral-depth-textured} are retained as selected visual evidence because they correspond to connected scaffold families and fixed rendering protocols. Broad guide sweeps, result matrices, depth galleries, bismuth sensitivity, and DLA bridge smoke tests remain appendix diagnostics.
```

Replacement for `main.tex:631`:

```tex
Figure~\ref{fig:masked-naturalization-ablation-20260510} and Table~\ref{tab:masked-naturalization-ablation-20260510} report Experiment 4, a focused four-task, three-seed ablation that crosses local realization with the projection schedule. Without projection, rule-only and naturalized variants fail the handle-state gate: handle survival remains low and failure rate remains high. With projection enabled, no-naturalization already restores handle survival; masked local naturalization then improves local surface proxies such as roughness, normal consistency, local artifacts, and rendered-inspection quality while keeping handle survival at $1.0$ and failure rate at $0.0$. Global naturalization is a useful control because it can smooth the surface, but it is less faithful to local controlled realization because old state is mutable. We therefore cite masked naturalization only as a local realization operator under an already projected recursive state, not as global topology repair or proof of texture consistency. Figure~\ref{fig:gen3d-baseline-zoom} provides a qualitative recursive-detail diagnosis: two-level camera zooms show whether selected one-shot, trivial-copy, and PS-RSLE cases keep readable local motifs at attached regions. This diagnostic is case-specific and does not replace same-root handle-level survival tests.
```

This removes inline exact mean values that can conflict with a no-std/value-only table refresh. If exact values are kept, ensure they are value-only and match the regenerated table.

Figure/table caption edits:

- At `main.tex:637`, replace `asset-quality proxy` with `local surface/visual-inspection proxy`.
- At `main.tex:645`, replace `rendered-asset quality` with `rendered-inspection quality` or define the metric precisely.

Table file required edit:

- Remove all `\pm` entries from `drafts/masked_naturalization_main_table_20260511.tex`.
- Keep mean/aggregate values only.
- Rename unclear columns:
  - `Rough.` -> `Roughness`
  - `Normal` -> `Normal cons.`
  - `Artifacts` -> `Artifact score`
  - `Drift` -> `Topo. drift`
  - `Quality` -> `Render proxy` or remove unless defined.
  - `Fail` -> `Fail rate`

Visual figure captions:

Replace GLB/export-heavy phrasing at `main.tex:664`, `672`, `680`.

Suggested `connected-best` caption:

```tex
\caption{Pure-white no-ground Blender contact sheet for selected connected scaffold families. The panels emphasize mesh silhouette, attachment, and local scaffold readability, so the figure supports connected-scaffold visual inspection rather than a claim that all families are solved final assets.}
```

Suggested pyrite caption:

```tex
\caption{Non-tree depth-control visualization on a connected pyrite-like lattice scaffold under a fixed render protocol. The stages remain occupancy-connected and surface-voxel connected while occupied support and local crystal facets increase with depth. This is the current preferred crystal/symmetry visual line; it supports connected scaffold recursion for a crystal-inspired asset, not physical pyrite growth simulation or watertight topology.}
```

Suggested coral caption:

```tex
\caption{Connected coral/DLA-inspired depth-control visualization under a fixed rule family and render protocol. In the rerun shown here, all four stages are single components under the strict surface-voxel diagnostic with LCR $1.000$. The result is a rule-native connected-scaffold alternative to post-hoc DLA bridge repair, not a claim that the object follows a physical DLA process.}
```

Remove or move `main.tex:684`:

Current paragraph is almost entirely texture-path/export inventory. Best action: delete from main or move to appendix status note. If a replacement is needed:

```tex
Remaining visual-inventory cases are kept as supplementary diagnostics. They document holes, thin sheets, material mismatch, camera artifacts, and guide sensitivity that are useful for boundary analysis, but they do not carry the main positive evidence.
```

## Batch 10 - Boundaries, Discussion, Conclusion

Goal: close on the execution invariant, not asset export.

Targets:

- `main.tex:686-697`.

Suggested replacement for `main.tex:686-687`:

```tex
\subsection{Boundaries and Supplement Placement}
Aggressive fork, radial, echo, hard-DLA, post-hoc bridge, blocky cache-selected, guide-sensitivity, partial-transfer, uninspected render cases, and demo-video prototypes remain diagnostic. They explain why projection, attachment feasibility, and rule-native connected support are necessary, but they are not presented as main positive evidence. The appendix keeps those figures as compile-preserving supplementary material, while the main text cites only figures and tables needed for the executable-state claim.
```

Suggested replacement for `main.tex:693`:

```tex
The current implementation is intentionally finite-depth and rule-authored. Root selection, transform compatibility, connector design, and rendering settings remain implementation choices that affect visual quality. Masked local realization improves local surface proxies under projection, but projection remains the structural mechanism. Likewise, recursive-detail zoom figures are best interpreted as selected local-allocation diagnostics rather than a universal resolution theorem. These boundaries do not change the main result: projection inside the recursive transition gives the executor a state-validity semantics that one-shot generation, direct sparse edits, and final-only cleanup lack.
```

Suggested replacement for conclusion `main.tex:697`:

```tex
We presented PS-RSLE, a projection-stabilized executor for finite-depth recursive programs over frozen sparse latent 3D generator states. The central observation is that recursive 3D generation fails through state contamination: detached fragments are harmful not only because they degrade the final mesh, but because they can become executable handles for later derivation steps. PS-RSLE separates generator-native sparse tokens from rule-readable active handles, uses typed rules to propose local sparse edits, applies the frozen generator for local realization and codec operations, and projects each decoded candidate to root-attached active state before the next rule can fire. This makes admissibility a per-depth execution invariant rather than a final cleanup step. The resulting framework gives finite-depth recursive asset generation a clear execution semantics on top of frozen Sparse Latent 3D Generators, while leaving mesh quality and rendered appearance as downstream diagnostics.
```

## Batch 11 - Appendix Routing and Compile-Preserving Cleanup

Goal: keep the main paper focused while preserving useful diagnostics.

Targets:

- Appendix roadmap and figure gallery from `main.tex:703` onward.
- Main-text references to moved figures/tables.

Recommended moves/labels:

1. Keep in main:
   - Method interface and overview figures.
   - Projection gate.
   - Rule family table.
   - Projection ablation figure/table after table is value-only.
   - Experiment 3 visual matrix/table after table is PS-RSLE and compact.
   - Traditional-vs-PS-RSLE matrix/table after asset/caption reconciliation.
   - Masked local realization ablation figure/table after value-only table.

2. Move or leave in appendix:
   - Broad guide sweeps.
   - Texture/export inventories.
   - Candidate screens.
   - DLA bridge smoke tests.
   - Effective-resolution/status placeholders.
   - GLB/file-size/runtime/export-success notes.

3. Remove main `\input` of any empty/commented placeholder table such as `drafts/effective_resolution_status_table_20260510.tex` if it is currently present in a local branch. In the current inspected `main.tex`, that placeholder is not in the visible main flow, but the metric audit noted a previous include; verify before final compile.

## Batch 12 - Final Table Compliance Pass

Goal: make all main tables publication-consistent without new data.

Checklist:

- No `\pm` anywhere in main included tables.
- No `std`, `Std.`, `variance`, or `mean/std` language in main captions.
- No `PS-RSLG` in main tables/captions.
- No `PBR`, `GLB`, `export`, `file size`, or runtime columns in main tables.
- `C_{r0}` either renamed or explicitly defined.
- Raw/welded components framed as mesh diagnostics, not structural proof.
- Classical controls described as strong structural controls.

Useful commands before applying edits:

```bash
rg -n "PS-RSLG|\\\\pm|std|Std|PBR|GLB|export|file size|runtime|grammar" \
  /Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex \
  /Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts \
  /Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/*.tex
```

Expected allowed `grammar` hits:

- `shape grammars` in classical related work.
- Appendix classical scope notes if phrased as historical/classical methods.

Expected disallowed `grammar` hits:

- Method overview figure `Rule library / Grammar`.
- Table/script labels implying PS-RSLE itself is a grammar.
- Old draft imports if they are included in main.

## Recommended Edit Order

1. Batch 1: naming and PS-RSLG cleanup.
2. Batch 5: experiment opening and metrics taxonomy.
3. Batch 6: projection ablation table value-only and caption cleanup.
4. Batch 7: Experiment 3 table schema and prose cleanup.
5. Batch 8: traditional-controls figure/caption/table reconciliation.
6. Batch 9: masked-local-realization section/table cleanup.
7. Batch 2 and Batch 3: abstract/introduction/related-work polish after experiments are stable.
8. Batch 4: figure-file text updates, because figure regeneration may require separate asset work.
9. Batch 10: discussion/conclusion closure.
10. Batch 11 and Batch 12: appendix routing and final compliance grep.

This order minimizes conflict: first fix contradictions that reviewers will notice immediately, then tighten the main evidence chain, then polish framing and figures.

