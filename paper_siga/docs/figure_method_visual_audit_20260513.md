# Figure/Method Visual Audit, 2026-05-13

Scope: current `main.tex`, active figure references only. No source edits proposed here.

## Figure 4: `figures/personal/sparse_latent.pdf`

- Active label: `fig:sparse-latent-interface`.
- Current caption: "Sparse latent generator interface used by PS-RSLE: encode an optional asset, update sparse latent support and features, and decode the resulting 3D asset."
- Semantic fit: Mostly matches. It still describes the frozen generator interface: optional asset, encoder, sparse latent state, native sampler/update, decoder, output. After the codec re-entry/remap changes, the weak point is that this figure reads as a one-pass generator interface, not as a reusable codec used by the outer executor.
- Recommended label change: none. Keep `fig:sparse-latent-interface`.
- Recommended caption change:
  "Frozen sparse latent generator interface used by PS-RSLE. The generator provides codec operations, sparse token support/features, a native sparse-latent sampler, and decoding; PS-RSLE re-enters this codec after projection so later rules read generator-native state."
- Recommended text change near the figure: when first referencing the figure, explicitly separate generator-owned operations from executor-owned operations. Suggested sentence:
  "Figure~\ref{fig:sparse-latent-interface} shows only the frozen generator interface; projection, codec re-entry, and handle remapping are PS-RSLE executor operations layered around it."

## Figure 5: `figures/personal/main_method.pdf`

- Active label: `fig:method-overview`.
- Current caption: "PS-RSLE repeats rule proposals, admission gates, controlled flow resampling, projection, and codec-closed commit before each recursive depth reads the next active state."
- Semantic fit: Good, but caption should name the current codec re-entry/remap semantics directly. "Codec-closed commit" is accurate but too compressed for the revised method, where projection yields decoded support, re-encoding returns to sparse generator state, and `Remap` updates surviving handles.
- Recommended label change: none. Keep `fig:method-overview`.
- Recommended caption change:
  "PS-RSLE repeats rule proposal, admission, controlled sparse-latent resampling, decoding, projection, codec re-entry, and handle remapping before the next recursive depth reads the active state."
- Recommended text change in the nearby method overview: replace any standalone "commit" wording with "decode--project--re-encode--remap commit" at first use. The current paragraph around the generator interface already says "codec re-entry through the decode--project--encode loop"; update that phrase to "decode--project--re-encode--remap loop" for consistency with the later projection section.

## Figure 6: `figures/personal/stickcase.pdf`

- Active label: `fig:one-branch`.
- Current caption: "One PS-RSLE branch transition: budget, collision, mask, connector, and ownership gates admit a child proposal before sampling and projection commit the next active state."
- Semantic fit: Partially matches. It still works as a branch-transition schematic, but the current caption stops at projection and does not say that the committed state is re-encoded and handle-remapped before reuse. This matters after the codec re-entry/remap changes because Figure 6 is the concrete method example.
- Recommended label change: none. Keep `fig:one-branch`.
- Recommended caption change:
  "One PS-RSLE branch transition: budget, collision, mask, connector, and ownership gates admit a child proposal; controlled sparse-latent sampling realizes it; projection, codec re-entry, and handle remapping commit the next active state."
- Recommended text change before the figure: revise "Fig.~\ref{fig:one-branch} illustrates one branch transition" to:
  "Fig.~\ref{fig:one-branch} illustrates one branch transition, including the admission gates and the projected, re-encoded, handle-remapped state that later rules may read."

## Visual Supplement Requirement

User requirement: after references and before appendix, include only these visual items:

1. Projection ablation visual.
   - Current active file/label: `figures/personal/projection_ablation.pdf`, `fig:projection-ablation-mesh`.
   - Placement: after bibliography, before `\appendix`. Matches requirement.

2. Pyrite depth visual.
   - Current active file/label: `figures/personal/huangtong.png`, `fig:pyrite-hq-depth-textured`.
   - Placement: after bibliography, before `\appendix`. Matches requirement.
   - Caption is conservative and acceptable.

3. Coral density control visual.
   - Existing active file/label: `figures/personal/density_control.png`, `fig:coral-density-extreme`.
   - Current placement: before references, inside `\subsection{Controllability}`.
   - Requirement placement: after references, before appendix.
   - Action needed in `main.tex`: move this figure into the post-reference visual block.

4. One line-plot/curve figure.
   - Current active file/label: `figures/space_competition_depth_curves_tokens_20260508.pdf`, `fig:space-competition-depth-curves`.
   - Placement: after bibliography, before `\appendix`. Matches requirement.

## Placement Mismatches

- Extra post-reference visual item: `figures/personal/Traditional.pdf`, label `fig:experiment3-sparse-latent-vs-mesh-space`, currently appears after references and before appendix. This violates the "only these visual items" requirement. Move it before references with Experiment 3, move it into appendix, or remove it from the visual supplement block.
- Missing post-reference visual item: `figures/personal/density_control.png`, label `fig:coral-density-extreme`, is not in the post-reference visual supplement block. It is currently in the main-text controllability subsection before references.
- Potential stray main-text visual: `figures/personal/coral_depth.pdf`, label `fig:coral-depth-textured`, is active before references. It is not one of the required post-reference visual supplement items. Keep it only if it remains a main-text controllability figure; do not add it to the post-reference visual supplement.
- Current post-reference block order is: sparse-latent-vs-mesh-space comparison, token curve, projection ablation, pyrite depth. Required block should be: projection ablation visual, pyrite depth visual, coral density control visual, one line-plot/curve figure, with no extra visuals.
