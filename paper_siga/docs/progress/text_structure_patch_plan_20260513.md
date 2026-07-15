# Text Structure Patch Plan - 2026-05-13

Role: subagent 4, body-structure and publication-level revision review.

Scope read:
- Full requirement document: `/Users/fanta/Downloads/三部分整理稿合并分节版.md`.
- Current manuscript: `main.tex`.

Constraint: do not edit `main.tex` in this pass. This document gives a patch plan and reusable LaTeX fragments.

## 1. Current Structural Diagnosis

The current manuscript already has the right core story: finite-depth recursive 3D asset generation needs an executable state, not only terminal mesh cleanup. The main remaining problem is not the claim itself but the body structure around it. The draft still reads like a status report in several places: it has inline TODOs, main-text export/PBR/GLB inventory, an explicit "claims under test" paragraph, a standalone weak transform-copy screening subsection, and a large inline appendix.

The publication-level structure should make one invariant carry the whole paper:

> PS-RSLE keeps every committed recursive state root-attached, addressable, and rule-readable before later rules can use it, while the frozen sparse latent 3D generator supplies local realization and codec operations.

Everything in the main paper should either define that invariant, instantiate it, or evaluate it. Export compatibility, broad galleries, weak diagnostics, and not-yet-closed screens should move to appendix/supplement.

## 2. Publication-Level Target Structure

### Abstract

Keep the current first seven sentences mostly intact. Replace only the final claim sentence with a tighter distinction between structural metrics and mesh/visual diagnostics. Avoid saying the method generally beats procedural systems on structure; say it approaches or matches their connectivity/stability while improving generator-quality diagnostics against generator/copy/cleanup alternatives.

Direct replacement for final sentence:

```latex
On the reported finite-depth benchmarks, PS-RSLE approaches the structural connectivity and state-stability of strong procedural controls while improving mesh-quality and rendered-visual diagnostics relative to direct generator, copy-based, and post-hoc cleanup baselines.
```

If "approaches" feels too weak after final metrics, use:

```latex
On the reported finite-depth benchmarks, PS-RSLE retains procedural-level structural connectivity and state stability while improving mesh-quality and rendered-visual diagnostics relative to direct generator, copy-based, and post-hoc cleanup baselines.
```

### Introduction

Compress by roughly 20-30%. The present Intro repeats Related Work material in paragraphs on classical methods, learned structure, native 3D generation, and editing. Keep the story chain, but cut citation-heavy detail.

Target paragraph plan:

1. Task and examples, with early reference to Figure 2.
2. Why recursion differs from one-shot 3D generation: intermediate fragments may become future state.
3. Classical procedural controls are structurally strong but visually/surface limited.
4. Sparse latent 3D generators offer learned local realization, but not recursive state semantics.
5. Existing editing/control methods are local or object-level, not persistent recursive execution.
6. Missing piece: admissible state transition before the next rule.
7. PS-RSLE solution.
8. Scope and contributions.

Concrete compression moves:
- Keep Figure 2 in the opening page, but remove photo credits from caption and place credits in a footnote/comment if needed.
- Move most citation clusters from Intro paragraphs 3-5 into Related Work.
- Delete phrases that sound like a literature survey: "Surveys of...", long method lists, "Editing and control methods further suggest...".
- Keep "finite-depth", "sparse latent 3D generator", "generator-native sparse latent tokens", "rule-readable active handles", "admissibility projection", and "decode--project--re-encode" as the fixed terminology.

Suggested compressed Intro skeleton:

```latex
Recursive 3D asset generation targets structured objects whose form is produced by repeated local expansion rather than by a single object sample. We focus on finite-depth, user-controlled programs spanning branching assets such as roots, crowns, vines, and fern-like forms, and non-tree recursive assets such as crystals, lattices, coral-like aggregates, porous growth, and repeated architectural motifs (Fig.~\ref{fig:natural-recursive-structures}).

The key difficulty is that intermediate geometry is executable. A branch, frontier, copied motif, or local edit region at depth $d$ may be selected, copied, expanded, or cached at depth $d+1$. A detached fragment is therefore not only a terminal artifact: if it remains active, it can contaminate all later derivation steps.

Classical procedural systems provide strong recursive control through explicit symbols, tips, frontiers, transforms, and parts. Their limitation is complementary to their structural strength: high-quality mesh geometry, natural local variation, fine detail, and appearance usually require family-specific surfacing and cleanup machinery. Modern sparse latent 3D generators provide the opposite ingredient. Their exposed token support, latent features, encoders, decoders, and local sampling paths are useful learned substrates for realizing local edits, but they do not define recursive validity or decide which intermediate components remain active state.

Existing editing, inpainting, and structure-conditioned generation methods can modify a current object under masks, prompts, or geometric conditions. They do not define a persistent program state with typed handles, ownership, attachment certificates, frontier labels, and a lifecycle across derivation depths. What is missing is an admissible state transition whose output can be read safely by later rules.
```

### Contributions

The current contribution list is close but should be sharpened to match Abstract/Intro/Experiments and avoid "separating" language. Use exactly four bullets:

```latex
\paragraph{Contributions.}
This paper makes the following contributions:
\begin{itemize}
  \item We formulate finite-depth recursive 3D asset generation as execution over a generator-coupled program state that combines generator-native sparse latent tokens with rule-readable active handles.
  \item We define typed active-handle and proposal semantics for local frames, ownership, frontiers, attachments, and reusable motifs, giving recursive rules a concrete interface for proposing sparse latent edits.
  \item We introduce controlled sparse-latent resampling, admissibility projection, and re-encoding as a per-depth state-stabilization loop, so each committed state is root-attached, addressable, and rule-readable before the next rule fires.
  \item We instantiate PS-RSLE on a frozen sparse latent 3D generator and evaluate it against procedural, generator-based, copy-based, and cleanup baselines, separating structural connectivity and state stability from mesh-quality and rendered-visual diagnostics.
\end{itemize}
```

### Related Work

Keep the first three subsections. Rename 2.4 and remove the global "Taken together" summary from the end of 2.4.

Target section titles:
- 2.1 Procedural Recursive Modeling
- 2.2 Learned Structure and Programmatic Shape Generation
- 2.3 Native 3D Generation and Sparse Latents
- 2.4 Sparse Editing and Structure-Conditioned Control

2.4 should only say: prior editing/control methods motivate masked sparse latent sampling, but their contract is current-object editing/conditioning, not persistent executable state. Do not make 2.4 the paper's final positioning statement.

Direct 2.4 title and ending replacement:

```latex
\subsection{Sparse Editing and Structure-Conditioned Control}

Editing and control methods show that frozen generative priors can be reused locally. Diffusion and flow-based editing can partially resample a current sample, while attention, feature, mask, skeleton, point, or image conditions can guide localized changes or structure-aware synthesis. In 3D, related methods edit neural fields, voxel fields, meshes, or structured latents while preserving selected regions. These works motivate our use of masked sparse-latent resampling as a local realization mechanism.

Their contract is nevertheless different from recursive execution. A mask, prompt, skeleton, or point prior conditions the current edit; it is not a persistent program state with active handles, ownership, attachment certificates, frontier labels, and a lifecycle across derivation depths. PS-RSLE uses local generator control only inside an executor that projects each decoded candidate into an admissible state before later rules can read it.
```

Move any "Taken together..." positioning into the last paragraph of Intro or the first paragraph of Method, shortened to one sentence if needed. Also cite Figure 3 in Related Work 2.1 with one sentence after the procedural-family list:

```latex
Figure~\ref{fig:traditional-recursive-baselines} shows representative procedural controls used to define our comparison domains.
```

### Preliminaries

Keep as two subsections but enforce symbol hygiene:
- 3.1 Finite-Depth Recursive Programs: define $s_d$, $\mathcal R$, $D$, executability.
- 3.2 Sparse Latent Generator Interface: define $u=(V,F)$, $\operatorname{Enc}_\theta$, $\mathcal N_\theta$, $\operatorname{Dec}_\theta$.

Required cleanup:
- Do not introduce symbols unused later.
- Keep $V$ for sparse token support and $U$ for projected/voxelized decoded support.
- If the figure still says "Sample" or uses a different symbol than $\mathcal N_\theta$, update the figure manually or note the mismatch in caption.
- Avoid "Sparse 3D Generators"; use "sparse latent 3D generators".

### Method

Rename Section 4 to:

```latex
\section{Method}
```

Target 4.1-4.5 structure:

#### 4.1 Program State

Purpose: define $s_d=(u_d,A_d)$, root descriptor, active handles, support graph, admissible active state.

Required additions:
- Explicit root descriptor paragraph. The root descriptor is not arbitrary semantic discovery; it is declared from the root asset/program manifest and instantiated on current support.
- Active handle definition should include active/inactive lifecycle.
- Avoid "automatic semantic handle discovery" beyond one scope sentence.

Suggested root descriptor paragraph:

```latex
The root descriptor anchors the execution. It is supplied by the authored program manifest and may denote an initial trunk/root region, a seed motif, a lattice cell, or a frontier-bearing base component depending on the asset family. PS-RSLE does not infer this descriptor from an arbitrary mesh; it carries the descriptor through the object frame and uses it to instantiate root support when projection tests reachability.
```

#### 4.2 Rule Proposals and Admission

Rename from "Rule Proposals as Tentative Sparse-State Edits" to:

```latex
\subsection{Rule Proposals and Admission}
```

Merge proposal records and admission gates. Current 4.2 has proposals, while admission appears in 4.3. For publication clarity, 4.2 should define both:
- proposal $p_j=(e_j,H_j,\mathrm{meta}_j)$;
- gates: token budget, collision clearance, mask validity, attachment/connector certificate, ownership compatibility.

Remove the duplicate/misleading stickcase figure currently labeled as sparse latent interface. If it is a one-branch example, relabel it as that and fix the caption/label.

#### 4.3 Recursive Transition

Rename:

```latex
\subsection{Recursive Transition}
```

Keep the four-stage transition:
1. propose;
2. admit-and-apply;
3. resample-and-decode;
4. project-and-commit.

Algorithm 1 should be concise and use the same symbols as 4.1-4.2. It should not contain unresolved TODOs.

Figure 5 / method overview required figure-edit notes for the user:
- Change "Outputs Textured Optional Asset" to "Output Asset".
- Change "Inputs" to "Input" if the diagram refers to one input package.
- Add a repeat/depth label on the arrow from next state to current state, e.g. "repeat for $d=0,\ldots,D-1$".
- Add colored shading around the recursive closed-loop portion.
- Check whether "Rule library / grammar" should feed directly into proposal generation, not into $P_S$ unless the diagram defines $P_S$ as proposal state.
- Use "sparse latent 3D generator" and "active handles"; avoid "grammar" as the main term unless referring to baselines.

#### 4.4 Controlled Sparse-Latent Resampling

Make this short, roughly half a page. Remove SDEdit and the long noise-and-denoise derivation. Keep only:
- flow-matching sampler as native generator process;
- editable mask $M_d$ and anchor/boundary $B_d$;
- optional cache/context blending in prose;
- decode.

Direct replacement skeleton:

```latex
\subsection{Controlled Sparse-Latent Resampling}

Admission yields a sparse latent candidate $\widetilde u_{d+1}$ together with an editable mask $M_d$, anchor or boundary tokens $B_d$, and a depth policy $\psi_d$. The frozen generator is used only to realize the admitted local edit; it does not decide which decoded components become executable state. We write the masked native sampler abstractly as
\[
\bar u_{d+1}
=
\operatorname{Resample}_{\theta}(\widetilde u_{d+1};y,M_d,B_d,\psi_d,\epsilon_d),
\]
where tokens outside $M_d$ are clamped or weakly blended according to the boundary policy, and editable tokens follow the generator's native sparse-latent flow-matching update.

For repeated motifs or transform-copy rules, the implementation may reuse source context through the rule-induced correspondence $\pi_d$ when it is available. In overlap or seam regions, cached keys/values or token features are blended with current-token values using fixed per-run weights from $\psi_d$; outside valid correspondences the sampler uses the current latent state. This cache policy is a local consistency aid, not a separate recursive-state mechanism.

The resampled latent is decoded as $x_{d+1}=\operatorname{Dec}_{\theta}(\bar u_{d+1},y)$. The result is still only a generator candidate. Whether its support and handles are executable is decided by admissibility projection.
```

#### 4.5 Admissibility Projection

Keep, but compress and make operational. Remove unresolved root-transfer and handle-transfer TODOs from main text. Use implementation-neutral but concrete language if exact code detail is unavailable:
- voxelize/sample decoded asset to $U$;
- instantiate root seeds from root descriptor;
- build $G_\eta(U)$;
- compute $U^{att}$;
- keep root-attached or certified connector support;
- deactivate handles not recoverable on projected support;
- re-encode.

Figure 6 / projection gate should appear in 4.5 near this operational paragraph, not as a commented-out block. Caption must say it illustrates the commit step, not an experiment.

Remove entire current 4.6 "Scope and Implementation Notes" from main Method. Salvage one short scope paragraph into the end of 4.5 or Discussion. Delete PBR/GLB/export equations from Method.

### Experiments

Replace the current 5.x order with a conventional AI-paper flow. Delete the paragraph `\paragraph{Claims under test.}` and integrate a short evaluation overview into 5.1.

Target structure:

#### 5.1 Tasks, Baselines, and Metrics

Merge current 5.1 and current baseline/metrics material. Include:
- task families: branching, frontier/accretion, transform-copy;
- baselines: procedural controls, one-shot sparse latent generator, direct copy/mesh-space recursion, final-only cleanup, ablations;
- common metrics: occupancy components/LCR, root reachability, orphan active handles, handle survival, mesh validity, non-manifold/fragment diagnostics, render/visual scores if available.

Avoid GLB/PBR/export-heavy claims. Export/import can be a supplementary diagnostic only.

Suggested 5.1 opening:

```latex
\subsection{Tasks, Baselines, and Metrics}
We evaluate finite-depth recursive asset generation on three task families: branching programs, frontier/accretion programs, and transform-copy programs. Each task fixes an authored root, rule family, recursion depth, seed, projection policy, renderer, and camera before evaluation. The evaluation separates recursive-state validity from terminal mesh and visual quality.
```

#### 5.2 Comparison with Procedural Recursive Controls

This should be the traditional-method comparison, not the current transform-copy screening subsection. Use Figure 10/current traditional-vs-ours matrix and the corrected metrics table. Treat procedural methods as strong structural controls.

Title:

```latex
\subsection{Comparison with Procedural Recursive Controls}
```

#### 5.3 Comparison with Generator and Mesh-Space Baselines

Use current Experiment 3 material: Trellis2 one-shot, latent copy, generated-root mesh copy, Hunyuan text-root mesh copy, PS-RSLE. Explain Figure columns clearly.

Title:

```latex
\subsection{Comparison with Generator and Mesh-Space Baselines}
```

Figure-column note to send to user if figure labels need manual editing:
- target/guide;
- Trellis2 one-shot;
- Trellis2 latent/copy control;
- Trellis2 generated-root mesh-copy;
- Hunyuan text-root mesh-copy;
- PS-RSLE.

#### 5.4 Projection Ablation

Move current "Per-Depth Projection Stabilizes..." here. Keep the main projection table and the projection ablation figure. The key result is active-state validity, not terminal cleanup.

#### 5.5 Masked Local Realization Ablation

Use masked naturalization only as a local surface-realization ablation under projection. Rename "naturalization" to "masked local realization" in section title and text where possible.

Title:

```latex
\subsection{Masked Local Realization Ablation}
```

#### 5.6 Controllability and Boundary Cases

Replace current "Naturalization, Export, and Effective Resolution" with controllability:
- depth control;
- density/compactness control for applicable programs;
- short boundary paragraph.

Do not include `effective_resolution_status_table_20260510.tex` in main text unless it is rewritten as a real control metric table. Move export inventory, guide sweeps, broad galleries, and effective-resolution placeholder to appendix/supplement.

Suggested opening:

```latex
\subsection{Controllability and Boundary Cases}
Because PS-RSLE keeps rule-readable handles across depths, authored program parameters remain inspectable during execution. We show two controls used across the reported tasks: recursion depth, which changes the number of committed derivation steps, and density or compactness, which changes local support allocation for applicable frontier-growth programs. These controls are qualitative behavior checks rather than universal optimality claims.
```

### Discussion

Keep concise. It should state:
- strongest evidence is projection ablation;
- finite-depth and rule-authored scope;
- root selection, transform compatibility, connector design affect quality;
- masked local realization improves surface proxies but projection is the state mechanism;
- no unbounded world generation, physical growth, watertight topology, or universal superiority claim.

### Conclusion

Current conclusion is good. Remove or downweight "asset export" as a core closing role. End on execution semantics, not export readiness.

Suggested final sentence:

```latex
The result is a finite-depth execution semantics that lets procedural recursive control and frozen sparse latent 3D priors cooperate without allowing invalid intermediate geometry to become future state.
```

### Appendix Split

Do not keep appendix inline in `main.tex`. Split into separate files:
- `appendix/moved_tables.tex`
- `appendix/diagnostic_figures.tex`
- `appendix/ablation_status.tex`
- `appendix/classical_systems.tex`
- optional `appendix/scope_notes.tex`

Main `main.tex` should use:

```latex
\clearpage
\appendix
\input{appendix/moved_tables}
\input{appendix/ablation_status}
\input{appendix/diagnostic_figures}
\input{appendix/classical_systems}
\input{appendix/scope_notes}
```

If SIGGRAPH page policy requires separate visual-only pages, keep main text after references lean and move text-heavy diagnostics to supplementary material rather than in-main appendix.

## 3. Must-Delete or Must-Move Items

Hard delete from main body:
- `\paragraph{Claims under test.}` and its paragraph at current experiment start.
- Standalone current 5.2 "Transform-Copy Operator Screening for Admission" as a main subsection. Fold one-sentence admission summary into 5.1/5.2 or move full screening to appendix.
- All inline `TODO` markers in Method, especially boundary token policy, timestep/solver/noise strengths, cache layers/weights, transform discretization, root transfer, and handle transfer.
- "SDEdit-style noise-and-denoise" in Method. If SDEdit is cited, keep it only in Related Work and do not describe PS-RSLE as SDEdit.
- Current `Naturalization, Export, and Effective Resolution` section title and effective-resolution placeholder table.
- `\input{drafts/effective_resolution_status_table_20260510.tex}` from main text unless replaced by a closed metric table.
- Entire inline appendix from main file after `\appendix`; split into separate files.

Move to appendix/supplement:
- PBR/GLB/export-heavy claims, inventories, and captions that present export success as main evidence.
- Broad guide sweeps, result matrix, candidate screens, V21/V22/V23 status sheets, DLA bridge smoke tests, uninspected GLB cases.
- Full V21 transform-copy screening table unless it becomes a concise ablation/metric table.
- Five-column protocol table if it is explanatory rather than result-bearing.

Wording to remove or replace in main claims:
- Replace "texture/PBR export" with "rendered visual quality" or "asset-level visual diagnostics" when the point is visual result quality.
- Replace "GLB export compatibility" with "supplementary export diagnostic" outside appendix.
- Replace "grammar" with "rules", "executor", or "program state" except when discussing classical grammar systems or mesh-space grammar baselines.
- Replace "naturalization" in main section titles with "masked local realization"; keep "naturalize" only if already established as an implementation term.

## 4. Small-Step Commit and Push Order

The user's workflow preference is "edit a small section, then push once." Each commit below should be small enough to review independently. After each commit, run at least a fast compile or syntax check if possible, then push.

1. `docs: add text structure patch plan`
   - Add this document only.
   - No `main.tex` changes.

2. `paper: tighten abstract and contributions`
   - Replace abstract final sentence.
   - Replace four contribution bullets.
   - Compile and push.

3. `paper: compress introduction narrative`
   - Compress Intro by 20-30%.
   - Add early Figure 2 reference.
   - Move/remove citation-heavy RW material.
   - Remove Figure 2 credits from caption or move to note.
   - Compile and push.

4. `paper: simplify related work positioning`
   - Rename 2.4 to "Sparse Editing and Structure-Conditioned Control".
   - Remove/move "Taken together" summary.
   - Add Figure 3 reference in 2.1.
   - Compile and push.

5. `paper: clean preliminaries symbols`
   - Enforce $V$ for sparse support and $U$ for projected decoded support.
   - Remove unused symbols.
   - Check Figure 4 text against symbols; document any manual figure edits.
   - Compile and push.

6. `paper: restructure method state and proposals`
   - Rename Section 4 to "Method".
   - Revise 4.1 root descriptor and active handle lifecycle.
   - Rename/rewrite 4.2 as proposal plus admission gates.
   - Fix or remove duplicate/mislabeled stickcase figure.
   - Compile and push.

7. `paper: tighten recursive transition`
   - Rename 4.3.
   - Align Algorithm 1 with symbols.
   - Update Figure 5 caption and list figure asset edits for user.
   - Compile and push.

8. `paper: shorten sparse latent resampling`
   - Replace 4.4 with short flow-matching masked resampling text.
   - Remove SDEdit-style language and unresolved TODOs.
   - Keep cache blending only as concise implementation prose.
   - Compile and push.

9. `paper: make projection operational`
   - Compress 4.5.
   - Move Figure 6 into 4.5 with corrected caption.
   - Remove root/handle TODOs from main text.
   - Delete 4.6 or salvage only one scope paragraph.
   - Compile and push.

10. `paper: merge experiment setup metrics`
    - Delete "Claims under test".
    - Merge task definitions, baselines, and metrics into 5.1.
    - Remove export/PBR-heavy metric claims from main.
    - Compile and push.

11. `paper: reorder main comparisons`
    - Make 5.2 procedural controls comparison.
    - Make 5.3 generator/mesh-space baselines comparison.
    - Move standalone transform-copy screening to appendix or fold into comparison text.
    - Compile and push.

12. `paper: isolate ablations`
    - Make 5.4 projection ablation.
    - Make 5.5 masked local realization ablation.
    - Remove weak naturalization/global export claims.
    - Compile and push.

13. `paper: replace effective resolution with controllability`
    - Delete effective-resolution placeholder table from main.
    - Add depth and density/compactness controllability section.
    - Move broad galleries/export inventories to appendix.
    - Compile and push.

14. `paper: split appendix files`
    - Create appendix `.tex` files.
    - Replace inline appendix with `\input{...}` calls.
    - Compile and push.

15. `paper: align discussion conclusion`
    - Make Discussion and Conclusion reflect final main structure.
    - Remove export as a core claim.
    - Final compile and push.

## 5. Immediate Risk Notes

- The current abstract/contributions may already have been edited by another agent. Do not overwrite blindly; apply only if the current text still differs materially from the snippets above.
- The current Method contains many TODOs. A publication draft cannot contain any TODO marker in main text or algorithm.
- Current main body overweights export/PBR/GLB evidence. This risks distracting reviewers from the real contribution and making the paper look like an asset pipeline paper instead of an execution semantics/method paper.
- The appendix is too large for `main.tex`. Splitting files is a structural cleanup, not a content deletion.
- Figures 5 and 6 need manual figure-text QA after text changes. The method overview must show the depth loop and the projection commit loop clearly.
