# paper_siga/main.tex revision requirements compliance check

Date: 2026-05-09

Scope:
- Checked: `paper_siga/main.tex`
- Requirements source: `/Users/fanta/Downloads/agent_revision_and_experiment_requirements.md`
- Constraint followed: did not modify `paper_siga/main.tex`

## Overall assessment

The current `main.tex` is a substantially revised draft that already implements many text-structure requirements: the title includes `Training-Free`, colored TODO macros exist, abstract/intro/related work/preliminaries/method have been reframed around sparse-latent recursive grammar, classical-system reductions have moved to the appendix, and experiments are now framed with protocol separation.

The remaining gaps are mostly submission-readiness gaps rather than first-pass structure gaps: many major claims are still marked as evidence/TODO, the main text still contains too many claim-adjacent gallery figures, the figures-only/supplement boundary is described but not physically enforced, visual render standards are only partially met, and the baseline/metric matrix remains too weak to support final quantitative claims.

## Compliance table

| Requirement | Current status | Must change | Suggested change | Can defer to experiments |
|---|---|---|---|---|
| Title must include training-free | Compliant. `\title{Recursive Sparse-Latent Grammars for Training-Free 3D Generative Growth}` at `main.tex:14`. | None. | Consider whether "Training-Free" should be lowercase in title style only if venue style prefers it. | No. |
| Add two visible TODO macros | Compliant. `\EvidencePending` and `\ExpFigTODO` defined with orange/red `xcolor` at `main.tex:6-9`. | None. | Use `\newcommand` instead of `\providecommand` only if you want stricter compile-time duplicate detection. | No. |
| Mark unfinished evidence and experiment/figure gaps | Mostly compliant. Many `\EvidencePending` and `\ExpFigTODO` markers are present at abstract, intro, preliminaries, projection, scheduling, refinement, experiments, metrics, baselines, rendering. | Keep all unsupported quantitative or comparative claims marked until experiments exist. | Add TODO marker near masked naturalization section itself for naturalization ablation; current naturalization TODO appears later in Baselines, but method-local TODO would be clearer. | Actual evidence can defer; markers cannot. |
| Remove internal revision trace / stale draft comments | Not compliant for clean manuscript. Large commented old abstracts/intros/method blocks remain at `main.tex:27-29`, `38-47`, `80`, `85`, `135-151`, `250-263`, `375-397`, and commented figure alternatives at `553-561`, `608-612`, `661-667`. | Must remove before submission and before any final compliance claim. Comments can confuse collaborators and reviewers if source is shared. | Delete all old revision-trace comments after the current narrative is accepted. | No. This is text cleanup, not experiment-dependent. |
| Main text / figures-only / supplement boundary | Partially compliant. Boundary is explicitly discussed at `main.tex:464-467`, `522-525`, appendix `725-726`; main text says it does not rely on appendix figure numbers. But main manuscript still contains many full-width result/gallery figures before references. | Must physically split the current gallery-heavy figure set before submission. Figures-only pages cannot contain tables or long text, and current manuscript still keeps all figures in main flow. | Keep only projection ablation, matched baseline matrix, strongest connected assets, and texture QA in main; move guide sweeps/result matrices/cache/extra depth/weak cases to supplement or figures-only pages. | Figure placement can wait until near submission, but claim-bearing text should be corrected now. |
| Abstract rewrite around recursive grammar, not projection-only | Mostly compliant. Abstract now leads with recursive structures and "generation-model-native recursive grammar" at `main.tex:30`; projection is described as execution semantics; texture is treated as export. | Replace "Current evidence shows..." with either final numbers or keep evidence-pending language. It currently has `\EvidencePending`, so acceptable for draft. | Shorten abstract by removing boundary details if page pressure appears. | Final quantitative improvement numbers defer to experiment completion. |
| Intro first paragraph: recursive algorithms and applications | Mostly compliant. Covers trees, roots, vines, corals, porous aggregates, crystals, ornaments, architecture, L-systems, IFS, DLA, space colonization, shape grammars at `main.tex:49`. | Add missing procedural modeling survey/classic survey citation if required by literature standard. | Include scientific/design applications slightly more concretely if space allows. | Literature polish can be done without new experiments. |
| Intro traditional methods paragraph | Mostly compliant. Current intro integrates traditional methods in paragraph 1 and related work section rather than a standalone paragraph. It treats them respectfully and notes asset-readiness gap. | None structurally, unless the desired intro must be exactly five paragraphs. | Keep current compact version; it matches the logic even if not exactly separated. | No. |
| Intro modern 3D generator paragraph | Mostly compliant. Discusses set-latent/object-latent and sparse structured latent families, Trellis/Trellis2 middleware, and marks missing comparison at `main.tex:51`. | Need evidence before claiming sparse route is superior. Already marked. | Add one sentence distinguishing mesh-only baselines from set-latent baselines in the intro. | Controlled sparse-vs-object-latent/mesh evidence can defer to experiments. |
| Intro failure chain | Partially compliant. Lists 2D scaffold, direct sparse edit, global flow repair, final-only cleanup at `main.tex:53` and marks missing diagnostic panels. | Need actual failure panels or keep `\EvidencePending`. | Make failure evidence references point to a specific subsection/table once available. | Yes, failure panels and matched protocol can defer. |
| Contributions: merge projection items; texture not core contribution | Compliant. Projection-stabilized execution is one item at `main.tex:64`; texture is outside contribution list at `main.tex:67`. | None. | Consider changing "connected projection" to "admissibility-constrained state selection" to avoid sounding like manual repair. | Final quantitative contribution numbers defer. |
| Related Work procedural and recursive modeling | Mostly compliant. Section `2.1` covers L-systems, IFS, DLA, space colonization, shape grammars/CGA at `main.tex:78-81`. | Add survey references if available. | Keep the non-strawman framing; it is aligned with requirements. | No. |
| Related Work 3D generative models | Mostly compliant. Section `2.2` covers datasets, object latents, image/text 3D systems, Trellis/Trellis2, sparse structured latent middleware at `main.tex:83-86`. | Add implicit/Gaussian/mesh literature coverage if currently too citation-light. | Expand only if page budget permits. | No, unless comparison experiment is required for claims. |
| Related Work merge editing/control | Compliant in structure. Section `2.3` merges training-free editing, SDEdit/FlowEdit, mask editing, native 3D latent editing, structure-conditioned generation at `main.tex:88-89`. | None. | Add clearer 3D inpainting citation if available. | No. |
| Move infinite/world-scale generation out of main related work | Compliant. World-scale appears only in appendix scope notes at `main.tex:743-744`; no main related-work subsection remains. | None. | Keep one discussion sentence only if needed. | No. |
| Add Preliminaries after Related Work | Compliant. `\section{Preliminaries}` starts at `main.tex:93`, before Method. | None. | None. | No. |
| Preliminaries recursive generation definition | Partially compliant. A modest grammar-derived definition is present at `main.tex:95-103`, with `\EvidencePending` for graph/shape-grammar terminology. | Need literature-grounded tightening before removing TODO. | Add graph grammar / derivation terminology citations if this definition becomes central. | Literature verification can be done before final; no experiment needed. |
| Preliminaries sparse voxel / Trellis pipeline | Mostly compliant. Defines `z=(V,F)`, `Enc`, `Dec`, `N`, `Tex`, condition `y`, token support/features at `main.tex:105-120`; includes required pipeline figure TODO. | Need actual pipeline figure before final. | Define whether `V` means support only while later Method uses `\mathcal V`; currently understandable but could be unified. | Pipeline figure can defer to figure production. |
| Method opening formula and symbol inheritance | Mostly compliant. Compact recursive transition at `main.tex:133-146` inherits `Enc`, `Dec`, `N/T`, projection. | Fix projection notation consistency if final version distinguishes mesh-domain `x` and state-domain `z`. | Use one symbol for the generator local operator: current text has `\mathcal T_\theta` wrapping rule/naturalization and `\mathcal N_\theta` later; acceptable but dense. | No. |
| Symbol conflicts: root anchors vs selected rules; proposals; anchors/attractors; `Z_t`/`z_t`; Eq. 7 type | Mostly compliant. Uses `\mathcal V_d^{root}` for roots, `\mathcal R_d` for selected rules, `\mathcal P_d` for proposals, `u_t` for sampler trajectory, and fixes support/state admissibility form around `main.tex:175-207`, `268-279`, `320-339`. | Check `\mathcal R` as both reachable-domain prefix and rule-library calligraphic R does not confuse readers at `main.tex:202-204`. | Rename reachable domain to `\mathcal U_{\mathrm{proj}}` or similar if polishing. | No. |
| Core State should be shortened | Compliant. Current state is compact `(\mathcal V_d,\mathbf F_d,\mathcal A_d)` with handles at `main.tex:152-187`; old verbose state is only in comments. | Remove old commented verbose state before final. | None. | No. |
| Rule table operators must be strict, bold, relevant | Mostly compliant. Table at `main.tex:211-237` uses bold names and formulas/definitions; material is excluded as core operator; cache not in table. | Some entries still need stronger formula specificity, especially Attach/Split/Refine. | Move Refine out or mark as planned if not experimentally used; it currently says planned in feasibility role. | Strong operator validation can defer to experiments, but table polish should not. |
| Masked local naturalization section | Partially compliant. Section exists at `main.tex:320-339`, distinguishes sampler trajectory `u_t` from recursive state, says local not global repair, and gives masked clamp. | Must add method-local TODO/evidence marker for ablation and support; currently explicit naturalization ablation TODO appears in experiments at `main.tex:476`, not inside the section. | Clarify actual Trellis2 latent/schedule/step count/mask projection; say feature blend is heuristic if so. | Ablations and precise schedules can defer to experiments if TODO remains. |
| Classical systems as limits moved to appendix | Compliant. Main text only has one sentence at `main.tex:285`; details are in appendix `main.tex:728-741`. | None. | Ensure no main text references appendix equation/figure numbers; current text does not. | No. |
| Symmetry/cache/scope moved out of main | Mostly compliant. Symmetry reductions in appendix `main.tex:740-741`; main `Scope, Complexity, and Export` at `main.tex:435-438`; cache/LOD probes described as supplemental at `main.tex:525`. | Remove or minimize main-text mentions of cache if not supported; current mentions are mostly boundary-routing. | Add runtime/memory table once measured. | Runtime/memory and symmetry metrics can defer to experiments. |
| Visual render requirements | Partially compliant. Some current figures explicitly use pure-white/no-ground renders (`main.tex:610`, `665-668`), and a global TODO exists at `main.tex:467`. But many included assets predate standardization; captions still mention galleries, guide sweeps, textured renders, zoom crops, and result matrices. | Must re-render or replace all final main figures to pure white, consistent camera/framing, no labels beyond subfigure letters, no PPT panels/borders. | Prefer the newer `standard_pure_white_selected_textured_contact_v2_20260509` style if it meets the standard; audit each included figure visually. | Yes, full re-render can defer to figure production, but noncompliant figures should not remain in final. |
| Projection mechanism rewritten as model-native, not manual repair | Mostly compliant in text. Projection section at `main.tex:345-361` says state selection, inactive descriptors, prune-only policy, optional model-completed connector, and marks variants needed. | Need remove terms/captions implying post-hoc bridging as method; current DLA caption at `main.tex:654-655` discusses sparse bridging as smoke test and must remain clearly boundary/baseline. | Change "connected projection" in contribution to "admissibility-constrained projection" to avoid repair connotation. | Projection variants and metrics can defer. |
| Operator scheduling / sparse competition | Partially compliant. Terms are now defined at `main.tex:399-413` and figure TODO is present. | Need at least one concrete operator walkthrough if this section remains in main method. | Put the generic score in appendix if not used by all operators. | Figure and case examples can defer. |
| Effective resolution / recursive refinement | Partially compliant and conservative. Section `main.tex:415-422` explicitly avoids strong claims and adds major experiment TODO. | Must not claim exceeding generator resolution until metrics exist. Current wording is safe. | Keep this as scope/hypothesis unless experiments are completed. | Yes, major effective-resolution experiment can defer. |
| Prove not procedural grammar + mesh projection + Trellis2 export | Partially compliant. Narrative repeatedly says operations happen in sparse latent state and texture is separated, but the decisive comparison is still TODO at `main.tex:475`. | Must run/insert critical latent-space vs mesh-space/postprocessing baseline before final strong novelty claim. | In current draft, keep claim language conservative and foreground missing experiment. | Yes, critical proof can defer to experiment, but final submission needs it. |
| Metrics suite | Partially compliant. Metrics section at `main.tex:479-482` lists mesh validity, skeleton topology, morphology, latent stability, effective resolution, material diagnostics as TODO. Current included baseline table still uses Occ comps/LCR/root ratio/tips/branch nodes/mesh comps and is weak. | Need more discriminative metrics before final quantitative claims. | Add raw mesh validity, orphan handles, branch/tip precision, non-manifold, boundary, runtime, seed mean/std tables. | Yes, implementation/reporting can defer. |
| Baselines suite | Partially compliant. Baselines are listed at `main.tex:472-477`; matched structural table exists via `paper_siga/drafts/baseline_matrix_table_20260509.tex`, but current matrix is too limited and all Occ/LCR/root ratios are saturated. | Need fair matrix across mesh-space recursion, one-shot Trellis2, direct sparse edit, global/masked repair, final-only/per-depth projection, and ours. | Keep classical baselines non-strawman; current text does this well. | Yes, baseline execution can defer. |
| Naturalization ablation | Not yet satisfied experimentally. Explicit TODO at `main.tex:476`; no completed ablation table/figure in current main file. | Must keep TODO and avoid unsupported claims that masked naturalization improves quality without topology drift. | Add method-local TODO in `Masked Local Naturalization`. | Yes. |
| Root quality / seed variation / success rate | Not yet satisfied experimentally. Explicit TODO at `main.tex:477`; appendix boundary says root/seed variation goes to supplement at `main.tex:726`. | Need at least summary mean/std and success rates before final claims. | Put full root/seed tables in supplement, one summary in main. | Yes. |
| Runtime / complexity / memory | Not yet satisfied experimentally. Scope section has TODO at `main.tex:436`. | Need hardware, per-depth time, memory, token/mesh growth, texture/export cost. | Add an implementation details paragraph or table. | Yes. |
| Texture/PBR should not be core contribution | Compliant in framing. Texture is export compatibility at `main.tex:67`, `424-433`, `516-517`, and table `690-710`. | Ensure textured figures never imply structural proof; captions mostly already prevent this. | Add warnings/channel completeness fields if table space allows. | GLB/PBR diagnostics can defer. |
| Negative/boundary results move to appendix/supplement | Partially compliant. Text says boundary cases are diagnostics and should be supplement at `main.tex:522-525`, `743-744`; however DLA bridge smoke and result matrix remain in main figures at `main.tex:556-567`, `652-656`. | Move broad/negative/boundary figures out of main before final. | Keep one concise boundary paragraph in Discussion rather than many diagnostic figures. | Physical relocation can defer to final layout, but main narrative should stay clean. |
| Experiments chapter merged and restructured | Partially compliant. Single `Experiments and Results` section exists at `main.tex:440`, with tasks, baselines, metrics, projection, baselines, texture, depth, boundaries. Missing explicit Implementation Details and full protocol tables. | Add implementation details and fairness protocol when final experiment set is known. | Reorder to match requirement: Implementation Details, Tasks/Baselines, Metrics, Projection, Latent-vs-mesh, Naturalization, Resolution, Qualitative, Texture, Robustness. | Detailed experiment content can defer. |

## Special checks requested

- **Title contains training-free:** yes, line `14`.
- **TODO macros:** yes, lines `6-9`; active uses throughout the draft.
- **Main / figures-only / supplement boundary:** described but not physically enforced. Main still contains many figure-heavy pages and boundary/gallery figures.
- **Abstract:** largely aligned; still draft because final quantitative numbers are pending.
- **Intro:** largely aligned with required five-part logic, though not literally split into five paragraphs.
- **Related work:** mostly aligned; world-scale moved out of main related work.
- **Preliminaries:** present and useful; recursive definition still flagged for literature tightening.
- **Method state/rule/operator:** mostly aligned; state compact, rule table improved, projection/naturalization/scheduling sections exist.
- **Masked naturalization:** conceptually aligned but lacks actual Trellis2 schedule/mask details and local ablation evidence.
- **Classical systems move appendix:** yes.
- **Symmetry/cache/scope:** mostly moved or scoped; runtime/memory still TODO.
- **Visual render requirements:** only partially met; global TODO remains and visual audit/re-render is still necessary.
- **Metrics/baseline TODO:** present and correctly conservative, but current matrices are insufficient for final claims.

## Minimum completable edit list, ordered by `main.tex` position

These are the smallest text/layout edits that can be completed without running new experiments. They should be applied before heavier experiment insertion.

1. `main.tex:27-29`  
   Remove old commented abstract variants.

2. `main.tex:38-47`  
   Remove old commented introduction variants.

3. `main.tex:69-74`  
   Decide whether the teaser is allowed under the "no teaser" visual requirement. If not, remove or move it to supplement/figures-only candidate pool.

4. `main.tex:80` and `85`  
   Remove old commented related-work paragraphs.

5. `main.tex:95-103`  
   Tighten or keep TODO for recursive-generation definition. If not adding graph grammar citations yet, leave `\EvidencePending` in place.

6. `main.tex:120`  
   Keep the pipeline figure TODO until the figure exists. Optionally move it into a dedicated placeholder paragraph so it is easy to find.

7. `main.tex:135-151`  
   Remove old commented verbose state definition.

8. `main.tex:211-237`  
   Either remove `Refine` from Table 1 or mark it visibly as planned/evaluation-pending, since current evidence is not complete.

9. `main.tex:320-339`  
   Add method-local TODO/evidence markers for masked naturalization ablation and implementation details: mask projection, actual latent, schedule/steps, feature blend status.

10. `main.tex:345-361`  
    Audit wording for projection so "connected projection" cannot be mistaken for manual mesh repair. Prefer "admissibility-constrained state selection" where possible.

11. `main.tex:375-397`  
    Remove old commented sparse-competition/projection-stability text.

12. `main.tex:399-413`  
    Add one concrete operator scheduling example or move the generic score details to appendix if not supported by experiments.

13. `main.tex:440-482`  
    Insert a short `Implementation Details` subsection before `Tasks`, even if it contains TODOs for hardware/model/version/renderer/projection settings.

14. `main.tex:486-669`  
    Triage every current figure into: main claim figure, figures-only page candidate, supplement, or remove. Current main body is still too gallery-heavy.

15. `main.tex:548-567`, `638-656`  
    Move result matrix, broad depth gallery, and DLA bridge smoke/boundary figures out of the main evidence path unless they are distilled to one claim-specific panel.

16. `main.tex:672-710` and `paper_siga/drafts/baseline_matrix_table_20260509.tex`  
    Keep tables conservative. Do not convert saturated Occ/LCR results into superiority claims until stronger metrics are added.

17. `main.tex:716-718`  
    Expand Discussion by one compact paragraph listing which TODO experiments gate final claims: latent-vs-mesh, projection variants, naturalization ablation, effective resolution, seed/root robustness, runtime.

18. `main.tex:723-744`  
    Keep appendix content, but ensure formal submission packaging separates text-heavy appendix from the figures-only exception.

