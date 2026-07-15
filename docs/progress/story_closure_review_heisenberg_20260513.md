# Story Closure Review - 2026-05-13

Scope: full-story review of `paper_siga/main.tex` plus the actually included core tables under `paper_siga/drafts/` and `paper_siga/figures/`. This was a read-mostly review: no edits were made to `main.tex`, and no stage/commit/push action was performed.

## Executive Verdict

The current manuscript is much closer to a closed story than earlier drafts. The abstract, introduction, related work, method, experiments, discussion, and conclusion now repeatedly center the same claim:

> recursive 3D generation over frozen sparse latent 3D generator states needs a per-depth admissible executable state, because detached or invalid fragments are harmful before the terminal mesh, when they can become parents, frontiers, motifs, or cached sources for later rules.

The strongest closure is the chain:

1. Introduction defines the failure mode: one-shot generation, copy, direct sparse edits, and final-only cleanup do not create or preserve rule-readable executable state.
2. Related Work positions procedural systems as strong state controls and frozen 3D generators as local realization priors.
3. Method formalizes `s_d=(u_d,A_d)`, active handles, admission, controlled resampling, projection, and the codec-closed transition.
4. Experiments use projection ablation as the main evidence: final-only projection recovers terminal occupancy but leaves root reachability, handle survival, and orphan-active statistics unchanged.
5. Discussion and Conclusion return to the execution claim and explicitly separate mesh/render diagnostics from topology and universal-quality claims.

Main remaining risks are not conceptual. They are presentation and closure risks:

- Several experiment subsections still carry visual-gallery pressure after the projection-ablation result.
- The appendix and historical draft files still contain `PS-RSLG` and grammar-first wording, including included or potentially includable supplementary tables.
- Some method wording over-explains codec-closed semantics and repeats the "current Trellis2 evidence is proxy/conservative" caveat in multiple places.
- The traditional-vs-ours section supports asset-readiness and visual diagnosis more than executable-state validity, so its role should be reduced or framed even more explicitly as secondary.
- The title omits "frozen sparse latent 3D generator states" and "executable state", which are now the paper's actual story anchors.

## 1. Mainline Closure

### Abstract

Status: mostly closed.

The abstract is aligned with the desired story. It starts from finite-depth programs, states that sparse latent generators provide local realization but not recursive execution, names PS-RSLE, defines state as sparse tokens plus rule-readable handles, and claims per-depth executable state rather than topology or material success.

Strong lines:

- `main.tex:30`: "used directly, they do not provide an admissible state transition whose output remains a well-defined executable state for subsequent rules."
- `main.tex:30`: "Experiments ... show that PS-RSLE preserves per-depth executable state..."
- `main.tex:30`: "Mesh and render diagnostics ... remain separate from topology, material, and universal-quality claims."

Risk:

- The abstract is long and dense. The key result is buried after many mechanism clauses. A reviewer may understand the method but not the one empirical punchline until the end.
- It says "the formal transition returns the projected state through the generator codec"; this is accurate only because later it is qualified, but the abstract's local wording could still be read as all reported runs perform per-depth codec re-entry.

Closure suggestion:

- Keep the current conservative evidence sentence, but make the result sentence more metric-like: final-only terminal cleanup can recover occupancy but not executable-state proxies; per-depth projection closes that gate.

### Introduction

Status: strong closure.

The introduction now does the right job. It distinguishes recursive generation from object synthesis at `main.tex:81`, identifies procedural systems as strong state controls at `main.tex:83`, separates learned structure/program priors from frozen sparse generator execution at `main.tex:85`, and directly states the missing unit at `main.tex:91`: an admissible state transition.

Strong lines:

- `main.tex:81`: "an invalid fragment is not only a visual artifact, but a possible future executable state."
- `main.tex:91`: "final-only cleanup is too late..."
- `main.tex:93`: "validity as an execution invariant rather than as a terminal mesh cleanup step."
- `main.tex:95`: "the main question is whether a sparse-generator-coupled program state can remain attached, addressable, and reusable at every derivation depth."

Risk:

- The first paragraph `main.tex:71` is broad and venue-facing, but it slightly delays the actual contribution. This is acceptable but could be tightened if page pressure returns.
- "shape grammars" in `main.tex:83` is clearly prior work, not a method-name problem. It is safe.

### Related Work

Status: closed and well-framed.

Related Work supports the story rather than becoming a taxonomy. Each subsection ends by re-centering the admissible-state gap. The final synthesis at `main.tex:132` is especially effective: recursive-state validity is primary; connectivity, mesh quality, and rendered views are diagnostics.

Potential issue:

- `main.tex:110` and `main.tex:126` are long paragraphs. They are logically correct but heavy. If the manuscript needs concision, these can be split or shortened without changing content.

### Method

Status: strong but slightly over-qualified.

The method is now coherent:

- Preliminaries define executable finite-depth state (`main.tex:140-145`).
- Sparse generator interface is explicitly not recursive validity (`main.tex:163`).
- Program state defines `s_d=(u_d,A_d)` and active handles (`main.tex:185-215`).
- Proposal records clarify what rules emit and what later rules may read (`main.tex:217-233`).
- Transition places projection inside the recursive loop (`main.tex:288-342`).
- Resampling is local realization, not state admission (`main.tex:381-417`).
- Projection is the state-stabilizing commit step (`main.tex:421-479`).

Most important closure line:

- `main.tex:479`: "This is why final-only cleanup is insufficient..."

Risks:

- The method repeatedly says the codec-closed loop is formal while current Trellis2 evidence is sparse-latent updates plus decoded projection/trace diagnostics (`main.tex:179`, `main.tex:342`, `main.tex:377`, `main.tex:474`). This is truthful, but repetition may make the implementation sound weaker than necessary.
- Algorithm 1 includes per-depth `Enc` at line `main.tex:369`; the caveats are nearby, but a skimming reviewer may read Algorithm 1 as implemented for all experiments.
- The term "rule library" is stable and better than grammar-first language. No method-name `PS-RSLG` appears in `main.tex`.

Recommended framing adjustment:

- Keep the full caveat once in Method transition and once in the projection-ablation caption. Remove or shorten duplicate caveats elsewhere if space is needed.

### Experiments

Status: mostly closed; one section still feels secondary.

The experiment preamble at `main.tex:506-514` is excellent: it states the claims under test, declares frozen generator/training-free evaluation, and warns that per-depth projected-mesh re-encoding should be reported only where explicitly run.

#### Transform-Copy Operator Screening

Role: operator-admission boundary.

This section serves the main story if read as "which transform-copy rules are admissible state operators". It does not overclaim visual superiority. The pyrite/radial caveats are good.

Risk:

- The section appears before Baselines/Metrics and before the projection ablation. Since projection ablation is the main claim, a reader may wonder why operator screening comes first.

Suggestion:

- Consider moving this after projection ablation, or add one opening sentence: "Before evaluating visual transform-copy examples, we first screen whether the transform-copy rows satisfy the same executable-state gate."

#### Baselines and Metrics

Role: evidence taxonomy.

This is clear and should stay. `main.tex:532-536` correctly separates state metrics, occupancy diagnostics, mesh/export diagnostics, surface-voxel diagnostics, and render metadata.

No major issue.

#### Per-Depth Projection

Role: central result.

This is the best-closed experiment. `main.tex:541` directly maps numbers to the central claim:

- final-only: Occ. LCR 0.995, root/handle 0.504, orphan active 3.667;
- full PS-RSLE: 1.000 / 1.000 / 0.000 / 1.000 / 1.000.

The table columns in `drafts/projection_ablation_main_table_20260511.tex` are exactly aligned with the story and use `PS-RSLE`, not `PS-RSLG`.

Risk:

- `tab:depth-scaling-diagnostics` is a new main-text table after the projection paragraph. It is labeled as geometry-level and not state-validity evidence, but it may still dilute the main table by adding another quantitative object before the central projection table appears visually. If page/attention pressure exists, this table is a candidate for appendix.

#### Sparse-Latent Execution versus Mesh-Space Alternatives

Role: novelty gate and baseline comparison.

This section supports the story by showing one-shot/copy/mesh-space alternatives lack typed handles, projection, latent update, and recursive state. The table in `drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex` is compact and uses `PS-RSLE`.

Risk:

- `main.tex:598` says "PS-RSLE is the only evaluated row that runs the intended state-transition machinery"; this is fine conceptually, but the table itself reports only occupancy components/LCR. The paragraph already says handle validity is tested by projection/trace ablations, which is necessary.
- This section can be misread as a visual superiority claim because the figure is prominent. The caption is conservative enough.

#### Traditional-vs-Ours Matched Comparison

Role: visual asset-readiness and target-matched diagnostic.

This is the least central main-text experiment. It has value because it treats procedural baselines as strong controls and shows selected PS-RSLE outputs under matched camera/zoom. But it serves asset-readiness and local realization more than per-depth executable-state validity.

Risks:

- The IFS/transform row explicitly uses a visually clearer recursive branch asset and is not an admitted IFS operator (`main.tex:626`, `main.tex:638`). This is honest but weakens the row's evidential role.
- The paragraph at `main.tex:638` is long and mixes several claims: space-colonization quality, L-system caveat, DLA visual regime, IFS branch visual, transform-copy claim relocation, and non-claims. It is correct but too much work for one paragraph.

Suggestion:

- Keep the figure/table, but make the lead sentence say it is "secondary target-matched visual/diagnostic evidence", not a main state-validity experiment.
- Split `main.tex:638` into a short result paragraph and a short caveat paragraph.

#### Masked Local Realization

Role: secondary mechanism under projection.

This section is well-closed. It states that projection is the structural gate, naturalization is a local realization aid, and masked local wins on quality proxy while global is smoother but locality-penalized.

Strong lines:

- `main.tex:644`: "Without projection, masked local naturalization does not repair executable state..."
- `main.tex:646`: "not as the structural mechanism that enforces admissibility."

Risk:

- The section includes three large visual figures after the table (`connected scaffold`, `pyrite`, `coral`). They are all captioned conservatively, but the visual load may make the end of Experiments feel gallery-like again.

Suggestion:

- Keep only the minimum visual figures needed for selected asset compatibility in the main text; move any extra visual showcase to appendix if the paper feels long.

### Discussion and Conclusion

Status: closed and concise.

Discussion returns to the central execution claim and explains the final-only cleanup distinction. Conclusion restates finite-depth, frozen sparse latent generator states, active handles, masked local realization, and projection before next rule firing.

Risk:

- Discussion is very short. That is not necessarily a problem; it is better than overclaiming. If reviewer-facing polish is desired, add one sentence explicitly naming the three evidence channels: controlled trace state metrics, surface/occupancy diagnostics, and mesh/render diagnostics.

## 2. PS-RSLE Terminology Stability

### Main manuscript

`main.tex` itself appears stable: no active `PS-RSLG` occurrences were found in `main.tex`. The active text consistently uses `PS-RSLE`.

The use of "grammar" in active `main.tex` is safe where it refers to classical shape grammars (`main.tex:83`, `main.tex:110`, `main.tex:1036`) or rule families. It no longer presents the method as "Projection-Stabilized Recursive Sparse-Latent Grammar."

### Included core tables

Safe:

- `drafts/projection_ablation_main_table_20260511.tex`: uses `full PS-RSLE`.
- `drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`: uses `PS-RSLE`.
- `drafts/masked_naturalization_main_table_20260511.tex`: no method-name issue.
- `figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`: uses "Ours", no `PS-RSLG`.
- `drafts/experiment3_mesh_enrichment_20260513.tex`: uses `PS-RSLE`.

### Residual risk files

Historical drafts still contain `PS-RSLG` and grammar-first wording. They are not necessarily in the active compile path, but they are risky because future `\input{}` changes could reintroduce stale terminology.

Notable files:

- `drafts/gen3d_baseline_summary_table_20260510.tex`
- `drafts/experiment3_sparse_latent_vs_mesh_space_table_supplement_20260511.tex`
- `drafts/algorithm_boxes_20260509.tex`
- `drafts/connectivity_method_section_20260509.tex`
- `drafts/strict_revision_section_rewrites_20260509.tex`
- `drafts/reviewer_method_results_patch_20260509.tex`

Action:

- Do not bulk-edit historical scratch files unless needed, but mark them as stale or avoid including them. If any are intended for supplement inclusion, replace `PS-RSLG` with `PS-RSLE` and replace "grammar owns topology" with "executor/rules maintain active handles and admission certificates."

## 3. Experiment-to-Claim Mapping

| Section | Evidence role | Serves main story? | Closure judgment |
|---|---|---:|---|
| Transform-copy screening | Decides which transform-copy rows are admissible operators | Yes, but secondary | Good if kept as operator-admission boundary |
| Baselines and Metrics | Defines evidence hierarchy | Yes | Strong |
| Projection ablation | Tests per-depth executable-state gate | Yes, primary | Strongest section |
| Depth/token curves | Geometry-level stability diagnostics | Partly | Useful, but should not precede/dilute main table too much |
| Experiment 3 one-shot/copy/mesh-space | Tests whether ordinary generation/copy replaces executable state | Yes | Good, provided handle validity remains delegated to projection ablation |
| Traditional-vs-ours | Target-matched visual/diagnostic comparison | Partly | Useful but secondary; risk of visual-gallery drift |
| Masked naturalization | Local realization under projection | Yes, secondary | Good and well-caveated |
| Rendered asset showcases | Compatibility/readability diagnostics | Weakly | Keep minimal in main; appendix for most |

## 4. Forward-Promise Closure Check

| Earlier promise | Later closure | Status |
|---|---|---|
| Need admissible recursive transition over frozen sparse latent states | Method defines active handles, admissible state, transition, projection; projection ablation tests it | Closed |
| Classical procedures are strong structural controls | Experiment 3/traditional comparisons treat them as controls, not strawmen | Mostly closed |
| Frozen generator is local realization, not recursive validity | Method resampling section and masked-naturalization ablation preserve this | Closed |
| Final-only cleanup is insufficient | Projection table directly shows final-only high LCR but bad handle/root/orphan metrics | Closed |
| Mesh/render metrics are diagnostics, not topology proof | Repeated in metrics section, experiment captions, appendix | Closed, perhaps over-repeated |
| Transform-copy examples need admission gates | V21 operator screening and appendix gate table address this | Mostly closed |
| Codec-closed transition includes re-encoding | Method defines it, but experiments only proxy it unless explicitly run | Truthful but still a reviewer-sensitive gap |
| Branching/frontier/transform-copy all evaluated | Yes, but not equally strong; transform-copy branch-tree is caveated | Partially closed |

## 5. Paragraphs Still Long or Not Fully Closed

1. `main.tex:30` abstract: accurate but too dense. It compresses motivation, method, implementation boundary, experiments, and caveats into one long paragraph.

2. `main.tex:110` procedural related work: correct but long; can be split after the classical-system list.

3. `main.tex:126` native 3D generation related work: correct but could be shorter because the key point is only "frozen sparse latent generators expose support/codecs but not recursive execution."

4. `main.tex:342`, `main.tex:377`, `main.tex:474`: the same codec-closed-vs-current-evidence caveat appears in several forms. Keep the strongest one at `main.tex:474`; shorten the others.

5. `main.tex:526-530` transform-copy screening setup: logically clear, but its position before the main projection ablation may disrupt the story order.

6. `main.tex:638` traditional-vs-ours result paragraph: too much in one paragraph and only partially serves the main state-validity story.

7. `main.tex:642-699` masked local realization plus rendered asset figures: the table closes the secondary claim; the following three visuals risk reopening gallery mode.

8. Appendix `main.tex:793-803`, five-column protocol: "Enabled components" says "decode/project/re-encode every depth" for per-depth projection. Given the implementation caveat, this should be marked as formal protocol / intended codec-closed semantics, not blanket implemented evidence.

## 6. Highest-Priority Direct Edits

1. Move or subordinate transform-copy screening after projection ablation.

   Rationale: the central claim is per-depth executable state. Projection ablation should be the first experiment after metrics. Transform-copy screening is important, but it is an operator-admission application of the same gate.

   Minimal edit: keep the section where it is, but add one bridge sentence: "This screen is secondary to the projection ablation below; it applies the same executable-state gate to transform-copy rows."

2. Split and demote the traditional-vs-ours paragraph at `main.tex:638`.

   Rationale: this is secondary visual/diagnostic evidence, not a primary state-validity proof. Its current single paragraph mixes result, caveat, and claim boundaries.

   Minimal edit: split into:
   - result paragraph: each row's surface/visual diagnostic;
   - caveat paragraph: L-system r1 caveat, IFS branch not admitted operator, no physical/topology/universal-superiority claims.

3. Reduce duplicate codec-closed caveats in Method.

   Rationale: the caveat is necessary, but repeated too often it weakens perceived implementation confidence.

   Minimal edit: keep `main.tex:474` as the full truthfulness statement; shorten `main.tex:342` and `main.tex:377` to a brief cross-reference.

4. Quarantine stale `PS-RSLG` draft files.

   Rationale: active `main.tex` is clean, but stale draft tables can re-enter through future `\input{}`. This is a process risk.

   Minimal edit: do not edit historical files now if they are intentionally archival; instead create/maintain an inclusion checklist saying only PS-RSLE-clean tables may be included. If supplement tables from `experiment3_sparse_latent_vs_mesh_space_table_supplement_20260511.tex` are used, replace all `PS-RSLG` labels first.

5. Move one or more rendered-asset showcase figures from main to appendix.

   Rationale: after the masked-naturalization table closes the secondary claim, the connected scaffold / pyrite / coral figures may make the paper feel gallery-driven again.

   Minimal edit: keep one representative visual compatibility figure in Section 4.5 and move the other two to appendix, or explicitly label them in one sentence as "selected asset-readiness diagnostics, not additional claims."

## 7. Suggested Closing Language

If only one story-closing sentence is added near the start of Experiments, use:

```latex
The projection ablation is the claim-bearing experiment: all other comparisons are interpreted through the same evidence hierarchy, with handle-state proxies testing executable state and mesh/render metrics serving only as diagnostics of realized assets.
```

If one sentence is added to Discussion:

```latex
The evidence therefore has three tiers: controlled trace metrics test executable-state validity, occupancy and surface-voxel metrics diagnose realized support, and mesh/render audits report asset-readiness without implying topology-cleanliness.
```

## 8. Bottom Line

The paper's story is now fundamentally closed around PS-RSLE as per-depth admissible executable state over frozen sparse latent 3D generator states. The main fixes are ordering, concision, and preventing secondary visual diagnostics from competing with the projection-ablation result. The highest-value next edit is to make projection ablation the unmistakable first and central experiment, then explicitly mark Experiment 3, traditional-vs-ours, masked naturalization, and rendered asset figures as supporting diagnostics under that state-validity hierarchy.
