# Figure/Table Audit Continuation - 2026-05-13

Scope: read-only audit for `paper_siga/main.tex` and figure/table assets. `main.tex` was not edited.

Inputs checked:
- User requirements: `/Users/fanta/Downloads/三部分整理稿合并分节版.md`
- Paper source: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex`
- Figure 5 current asset: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/personal/main_method.pdf`
- Figure 6 candidate: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/method_projection_admissibility_gate_20260510.pdf` and `.png`
- Figure 7/8 curve assets: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/projection_depth_curves_20260508.pdf`, `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/space_competition_depth_curves_tokens_20260508.pdf`
- Figure 10 current asset: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.png`
- Nearby Figure 10 QA variants: `main_experiment_traditional_vs_ours_upright_4x4_zoom_QA_20260512.png`, `_QA_v23_20260512.png`, `_QA_v59_dense_20260512.png`, `_QA_v59_lowfrag_20260512.png`, `_QA_v63B_20260512.png`, `_QA_v63C_20260512.png`

## Figure 5 - method overview

Rendered/read directly from `figures/personal/main_method.pdf`. Current embedded text is:
- `Rule library / Grammar`
- `Inputs Image / Mesh Condition`
- `Encoder`
- `Current Projected State`
- `Rule Proposals`
- `AdmitApply`
- `Controlled Sampling`
- `Decode Candidate`
- `Projection & Re-encode`
- `Next Projected State`
- `Outputs Textured (optional) asset`

Required exact text changes for the figure file:
1. Change `Inputs` to `Input`.
2. Change `Outputs Textured (optional) asset` to `Output Asset`.
3. Change `Rule library / Grammar` to a cleaner term consistent with the method text. Recommended figure label: `Rule Library` or `Typed Rule Library`; avoid slash wording because the paper now describes a rule library that emits typed proposal records, not a separate grammar object.
4. Change `AdmitApply` to `Admit / Apply` or split into two labels, `Admit` then `Apply`. Current joined text reads like a typo and hides the admission/control-bundle role.
5. Add an explicit loop/depth indicator between `Next Projected State` and `Current Projected State`, e.g. `repeat for d = 0 ... D-1` or `repeat until depth D`. User specifically requested that the next-to-current transition explain repeat count/depth.
6. Consider changing `Current Projected State` and `Next Projected State` to `Current State s_d` and `Projected Next State s_{d+1}` if there is space. This would match the caption and method notation more tightly.
7. Keep `Projection & Re-encode`; it is method-consistent. If the figure is redrawn, `Decode Candidate` could become `Decoded Candidate x_{d+1}` and `Controlled Sampling` could become `Controlled Sparse-Latent Sampling`, but these are optional refinements rather than required corrections.
8. Layout issue: the bottom output box is clipped/partially occluded in the rendered PDF. When changing `Output Asset`, also resize/reposition that box so the text is fully visible.

Caption/body citation status: `main.tex` already cites Figure 5 at the top of Method and the caption accurately explains the top sparse-generator interface and bottom recursive transition loop. After adding the depth-repeat indicator, no major caption rewrite is required; optionally add a short phrase such as `The dashed return arrow denotes repeating the committed state transition until the prescribed finite depth D.`

## Figure 6 - projection/admissibility gate

Rendered/read directly from `figures/method_projection_admissibility_gate_20260510.pdf` and `.png`. The current figure text is broadly aligned with Sec. 4.5/current `main.tex` lines 417-445:
- It presents projection as active-state selection.
- It shows decoded candidate -> admissibility gate -> projected active state -> re-encoding.
- It explicitly says only the projected sparse state is visible to the next derivation depth.
- It includes the right concepts: root reachability, keep attached support, orphan handles, deactivate/prune, budget/renderability, reject invalid state, inactive descriptor/deleted, optional connector mask, surviving handles, later rules read the projected state only.

Judgment: use this as Figure 6. It matches the 4.5 method story better than a generic voxel-only diagram because it emphasizes the key claim: projection is an active-state commit before the next rule selection, not final mesh cleanup.

Recommended minor figure text changes:
1. Top-left `z_d active state` and bottom `projected z_{d+1}` should preferably be `s_d active state` and `projected s_{d+1}`. The paper uses `s_d=(u_d,A_d)` for executable state; `z` is not the main state variable in current text.
2. Formula at bottom currently reads like `z_{d+1}=Enc_theta(Pi_{theta,lambda_d}(Dec_theta(bar z_{d+1}), A_d))`. Replace with notation consistent with current source: `u_{d+1}=Enc_theta(x^*_{d+1}, y)`, `(x^*_{d+1}, A_{d+1})=Pi_{lambda_d}(x_{d+1}, \widetilde A_{d+1}, s_d, \Gamma_d)`, or a compact two-line version. Avoid `Pi_{theta,lambda_d}` unless the text defines theta-dependent projection, which it currently does not.
3. Replace `conservative prune-only policy` with `conservative projection policy` or `prune/demote policy`. Current 4.5 allows rule-certified connector support, so the main gate should not imply prune-only as the overall policy.
4. `budget / renderability` is acceptable but slightly experimental; for method purity, `budget / validity` or `budget / constraints` would match Sec. 4.5 more closely.
5. Keep `optional connector mask` but retain the note `rule-proposed and certified; not the default repair path`. This is important and method-consistent.

Caption/body recommendation:
- Current placement in Sec. 4.5 is correct: immediately after introducing projection and before Algorithm 2.
- Current body citation is good: `Figure~\ref{fig:method-projection-gate} illustrates this active-state selection: only the projected state is visible to later rule selection.`
- Current caption is mostly correct. Recommended final caption language: `Admissibility projection as active-state selection. After decoding a candidate, projection keeps support that is root-reachable or covered by a rule-certified connector, deactivates orphan handles, and commits only the projected state for re-encoding. Later rules read this projected state, not the raw decoded candidate. The diagram illustrates the method commit step; quantitative projection ablations are reported in Sec.~\ref{sec:projection-ablation}.`

## Table 1 - rule families

Current LaTeX location: `paper_siga/main.tex` lines 235-276. Current columns:
- `Rule family` width `0.16\textwidth`
- `Reads from active state` width `0.24\textwidth`
- `Proposal record` width `0.34\textwidth`
- `Supported structures` width `0.20\textwidth`

Recommendation for width/language:
1. The second column is too wide relative to its content. Reduce `Reads from active state` from `0.24\textwidth` to about `0.18\textwidth` or `0.19\textwidth`.
2. Give the saved width to `Rule family` and/or `Supported structures` so each root family can finish in one or two lines. Suggested table spec: `@{}p{0.18\textwidth}p{0.18\textwidth}p{0.35\textwidth}p{0.23\textwidth}@{}`. If the table still runs wide, use `\small` and `\setlength{\tabcolsep}{3pt}` rather than shrinking the proposal text too much.
3. Change column header `Reads from active state` to `Reads active handles` or `Reads`. The current phrase is clear but long and forces wrapping.
4. Keep the table as a vocabulary map near Sec. 4.2. It is doing real narrative work and should be cited before the one-branch transition, as current text does.
5. Language refinements by row:
   - `Branch / grow`: supported structures should avoid overclaiming botanical realism. Suggested: `Roots, vines, tree crowns, branching forms.`
   - `Frontier attach / accrete`: good; optionally change proposal text to `Attraction- or stochastic-guided support seeds with attachment certificates and frontier updates.`
   - `Transform-copy`: good; optionally say `copied or seeded features` instead of only `copied feature seeds` because the method text allows feature seeds and copied features.
   - `Split / extrude`: good but `Hard-surface motifs, architectural ornaments, repeated segments` may be broad. Keep if these examples are used elsewhere; otherwise shorten to `Hard-surface motifs and repeated segments.`
   - `Refine / zoom`: currently says `Local support allocation, feature-seed refinement, and local detail.` This is acceptable, but if effective-resolution claims are being downweighted, make it conservative: `Local support allocation and feature-seed refinement under a token budget.` Supported structures: `Local detail and motif enlargement.`

## Figure 7/8 depth curves

Files inspected:
- `figures/projection_depth_curves_20260508.pdf`
- `figures/space_competition_depth_curves_tokens_20260508.pdf`

Current source references these at `main.tex` lines 553-573 in `Per-Depth Projection Stabilizes Conservative Recursive Programs`.

Judgment:
- The LCR curve figure is useful if kept as a compact diagnostic for the projection-stabilization claim. It clearly separates stable conservative programs from boundary/failure operators. However, the title inside the figure is large and repeats the caption. For publication, remove or reduce the in-figure title and let the caption carry the claim.
- The token-growth figure is weaker as main-story evidence. It reports resource/support growth rather than state validity, and its legend/classes are more implementation-screening than claim-bearing. Keep only if the experiment section explicitly uses it to explain token budget/depth controllability; otherwise move it to appendix/supplement and mention token budget in prose/table.
- If both stay in the main paper, label them as diagnostics rather than primary proof. The current prose already partly does this.

## Figure 10 - traditional vs ours matrix

Current source uses:
- `figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.png`

Rendered inspection:
- It is a 4x4 matrix with row labels only: `Space colonization`, `L-system`, `DLA`, `IFS`.
- Column semantics are not visible inside the figure. From caption/source, columns are: traditional overview, traditional zoom, PS-RSLE overview, PS-RSLE zoom.
- This matches the user request that the paper or figure should explain what each column means.

Recommendation:
1. Prefer adding column labels in the figure if allowed: `Traditional`, `Traditional zoom`, `PS-RSLE`, `PS-RSLE zoom`. If labels are intentionally excluded, the caption must explicitly state these four columns in the first sentence.
2. Current caption already explains the four columns only indirectly. Strengthen it to say: `Columns are, from left to right, traditional overview, traditional zoom, PS-RSLE overview, and PS-RSLE zoom.`
3. Nearby QA replacement variants exist. `main_experiment_traditional_vs_ours_upright_4x4_zoom_QA_v63C_20260512.png` is a smaller QA variant with `ifs_ours_variant: v63_balanced_fan_C` and note `visual recursive-branch replacement with distributed side-branch depth/density; generated by the L-system branch grammar, not a formal IFS operator`. It is visually cleaner/less oversized than the current large PNG, but the semantic caveat is still important. If replacing Figure 10, update caption/table caveat to match the chosen JSON manifest.
4. Current asset's JSON says `ifs_ours_variant: current_v21` and `ifs_ours_note: legacy V21 branch-tree candidate; visually weak recursion in the 4x4 matrix`, while current text/caption discusses a visually clearer recursive branch asset. This is a mismatch. Either switch to a QA replacement variant with the intended stronger IFS/branch visual, or revise the caption/body to acknowledge the current V21 weakness.

## Overall recommendations

- Do not edit `main.tex` until figure replacements are selected. The current text is already partly updated for Figure 6 and Table 1.
- Highest-priority figure-file fixes are Figure 5 text/loop and Figure 10 chosen replacement/caption alignment.
- Figure 6 is method-consistent, but its variable names should be updated from `z` to `s/u` notation and its formula should match Sec. 4.5.
- Table 1 should stay, with narrower second column and slightly more conservative language.
