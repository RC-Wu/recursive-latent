# Manuscript Next Safe Edit Batches - 2026-05-13

Scope: read-only review of `paper_siga/main.tex`, included table fragments, and the existing story report. I did not edit `main.tex`, stage, commit, push, or revert anything. This report is the only file written.

Context applied:

- Main story should remain per-depth admissible executable state over frozen sparse latent 3D generator states.
- Avoid grammar framing except for classical `shape grammars`.
- Classical procedural methods are strong controls.
- Render, texture, GLB, export, and material diagnostics are supplementary or supporting diagnostics, not topology proof or operator-admission proof.
- The already-applied abstract/introduction/render-diagnostics wording has improved the top-level story; the next safe edits should focus on remaining experiment-section wording and appendix/table cleanup.

## Top Next Batch: Main-Body Texture/Export De-Emphasis

This is the smallest high-value batch. It touches only prose/captions in the main body, does not change figures or table data, and should compile as a standalone push.

Targets:

- `main.tex:525`
- `main.tex:581`
- `main.tex:601`
- `main.tex:608-609`
- `main.tex:628-629`
- `main.tex:631`
- `main.tex:637`
- `main.tex:645`
- `main.tex:664`
- `main.tex:672`
- `main.tex:680`
- `main.tex:684`
- `main.tex:687`
- `main.tex:697`

Replacement intent:

1. Replace `texture-path compatibility` in the transform-copy discussion with `render/readability diagnostics for selected projected meshes`.

   At `main.tex:525`, keep the admission caveat but remove texture path as a named story role:

   Current intent:

   ```tex
   ... connected lattice/orbit scaffold evidence and texture-path compatibility, not as exact symmetry ...
   ```

   Suggested intent:

   ```tex
   ... connected lattice/orbit scaffold evidence plus selected render-readability diagnostics, not as exact symmetry ...
   ```

2. Reframe classical texture baseline language so it supports fairness without becoming a main narrative thread.

   At `main.tex:581`, replace:

   ```tex
   classical procedural supports can be connected and can even be passed through the same texture path
   ```

   with:

   ```tex
   classical procedural supports can be connected and can be inspected under the same rendering protocol
   ```

   At `main.tex:601`, replace the last clause:

   ```tex
   ... selected textured PS-RSLE renders.
   ```

   with:

   ```tex
   ... selected PS-RSLE render diagnostics.
   ```

   At `main.tex:608-609`, make the figure description/caption diagnostic rather than texture-path centered. Suggested replacement intent:

   ```tex
   \Description{Traditional procedural baselines inspected under the same selected rendering protocol for structural families including space-colonization, L-system, and DLA-like clusters.}
   \caption{Traditional procedural baselines inspected under the same selected rendering protocol used for PS-RSLE scaffolds. This rerun is intentionally a strong and fair baseline: space-colonization and L-system supports remain renderable and are near-connected or connected under the surface-voxel proxy, while the DLA-like cluster remains visually blocky. The result supports protocol separation rather than a strawman comparison: classical supports can be rendered for inspection, but recursive scaffold semantics and state validity still require separate structural evaluation.}
   ```

3. Rename the masked local realization section away from export.

   At `main.tex:628`, change label:

   ```tex
   \label{sec:naturalization-export-resolution}
   ```

   to:

   ```tex
   \label{sec:masked-local-realization}
   ```

   This label appears not to be externally referenced in `main.tex`, but run `rg "naturalization-export-resolution|masked-local-realization"` before editing to confirm.

   At `main.tex:629`, replace:

   ```tex
   Projection-stabilized states can be decoded into meshes and, for selected cases, passed through the frozen Trellis2 texture path.
   ```

   with:

   ```tex
   Projection-stabilized states can be decoded into meshes for selected visual inspection under fixed rendering protocols.
   ```

4. Replace `rendered-asset quality` phrasing with `visual-readability` or `local surface-quality proxy`.

   At `main.tex:631`, change:

   ```tex
   rendered-asset quality proxy rises ...
   lower rendered-asset quality ...
   proof of texture consistency
   ```

   to:

   ```tex
   visual-readability proxy rises ...
   lower visual-readability score ...
   proof of material consistency
   ```

   At `main.tex:637`, replace:

   ```tex
   local geometry/asset-quality proxy claim ... final texture cleanup
   ```

   with:

   ```tex
   local geometry and visual-readability proxy claim ... final render cleanup
   ```

   At `main.tex:645`, replace:

   ```tex
   rendered-asset quality
   ```

   with:

   ```tex
   visual-readability quality
   ```

5. Clean three main figure captions that still over-name textured GLB/material machinery.

   At `main.tex:664`, replace:

   ```tex
   solved textured GLB assets
   ```

   with:

   ```tex
   solved final assets
   ```

   At `main.tex:672`, replace:

   ```tex
   under a fixed public material guide and fixed Trellis2 texture schedule ... textured rendering for a crystal-inspired asset
   ```

   with:

   ```tex
   under a fixed rendering protocol ... visual inspection for a crystal-inspired asset
   ```

   At `main.tex:680`, replace:

   ```tex
   fixed public material guide ... all four textured stages
   ```

   with:

   ```tex
   fixed rendering protocol ... all four shown stages
   ```

6. Close the boundary/conclusion wording with diagnostics language.

   At `main.tex:684`, replace `Texture-path diagnostics` with `Rendered-asset diagnostics`.

   At `main.tex:687`, replace:

   ```tex
   uninspected-GLB cases
   ```

   with:

   ```tex
   uninspected render/export cases
   ```

   At `main.tex:697`, replace:

   ```tex
   rendered-asset diagnostics
   ```

   with:

   ```tex
   mesh and render diagnostics
   ```

Why this batch first:

- It directly addresses the remaining main-narrative texture-path/PBR/GLB/export-heavy language.
- It is prose-only and local to the experiment/discussion conclusion path.
- It preserves all current claims, figures, and metrics while making the story more closed.

Verification for this batch:

- Run `rg -n "texture path|texture-path|textured GLB|GLB|PBR|export|rendered-asset|asset-readiness|textureable" main.tex`.
- The remaining hits should either be in appendix diagnostics, file names, labels, or explicitly supplementary caveats.
- Compile once with the current project command after the label rename.

## Batch 2: Experiment Flow Closure and Section Boundary Tightening

This batch is still small, but it changes paragraph flow. It should be a separate push after Batch 1 so wording regressions are easy to isolate.

Targets:

- `main.tex:506-507`
- `main.tex:515-527`
- `main.tex:530-533`
- `main.tex:576`
- `main.tex:579-585`
- `main.tex:613-625`
- `main.tex:686-687`

Replacement intent:

1. Make the experiment opening read as three evidence blocks, not a mixed gallery/protocol list.

   At `main.tex:506-507`, preserve the current content but explicitly order the claims:

   - Experiment 2: per-depth projection as the state-validity mechanism.
   - Transform-copy screen: operator admission under a fixed contract.
   - Experiment 3 and traditional comparison: novelty/fairness against strong procedural and mesh-space controls.
   - Experiment 4: local realization under already projected state.

   Keep the final caveat sentence about no physical DLA/crystal claim.

2. In `main.tex:515-527`, reduce the transform-copy section to admission logic and move pyrite visual detail out of the admission path.

   Replacement intent:

   - Keep lines `515-522` mostly intact.
   - At `main.tex:525`, say the pyrite depth figure is visual corroboration only after admission has been decided by the V21 gate.
   - Avoid making `texture-path compatibility` part of the positive transform-copy claim.

3. In `main.tex:530-533`, split primary metrics from diagnostics in two sentences.

   Suggested structure:

   ```tex
   Primary state quantities are root reachability, orphan active handles, handle survival, committed pass rate, and depth stability. Structural mesh proxies include connected components and largest-component ratio on voxel occupancy or surface samples. Raw face components, tolerance-based vertex welding, non-manifold diagnostics, render success, and import warnings are retained as diagnostics; they support asset inspection only and are not topology or state-validity evidence.
   ```

   This avoids leading with renderability and makes the metric hierarchy unmistakable.

4. At `main.tex:576`, make the appendix table role narrower.

   Current:

   ```tex
   Table~\ref{tab:matched-structural-baseline-matrix} is moved to Appendix~\ref{app:moved-main-tables}; the main text uses it as a fairness check rather than as a superiority claim.
   ```

   Suggested:

   ```tex
   Table~\ref{tab:matched-structural-baseline-matrix} is moved to Appendix~\ref{app:moved-main-tables}; the main text relies on it only to document matched controls and metric definitions.
   ```

5. At `main.tex:579-585`, make the novelty gate paragraph less visual-quality gated.

   Replacement intent:

   - Keep the Hunyuan/Trellis fairness details.
   - Replace `quality-gated main subset` with `claim-gated main subset`.
   - Replace `visually strong cases` with `claim-bearing cases with inspected render diagnostics`.
   - End the paragraph with the current important caveat that handle-level validity is tested by projection/trace ablations, not Table 3 alone.

6. At `main.tex:613-625`, shorten the strict traditional comparison paragraph so it does not become another main claim block.

   Replacement intent:

   - Keep the one-to-one family mapping.
   - Keep the caveat that IFS/transform branch visual is not transform-copy admission.
   - Reduce detailed row-by-row visual interpretation by about 25-35%.
   - End with the current conservative sentence: no physical DLA simulation, botanical realism, watertight topology, direct IFS equivalence, or universal superiority over mature procedural systems.

Why this batch second:

- It improves the story discontinuity between projection, operator admission, classical controls, and visual diagnostics.
- It is still text-only, but touches more connective tissue than Batch 1.
- It can compile and push independently.

Verification for this batch:

- Compile.
- Skim only Section 5 from `Claims under test` through `Boundaries and Supplement Placement`.
- Confirm the reader can identify which experiment proves state validity versus which figures are diagnostics.

## Batch 3: Appendix/Table Caption Diagnostic Cleanup

This batch is safe but lower priority because most hits are already after the appendix boundary. It should be separate so appendix churn does not obscure main-story edits.

Targets:

- `main.tex:722`
- `main.tex:732`
- `main.tex:758`
- `main.tex:763`
- `main.tex:786`
- `main.tex:817`
- `main.tex:847`
- `main.tex:855`
- `main.tex:862-863`
- `main.tex:879`
- `main.tex:915-916`
- `main.tex:940`
- `main.tex:948`
- `main.tex:971-972`
- `main.tex:980`
- `main.tex:988`
- `main.tex:996`
- `main.tex:1010`
- `drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex:9`
- `drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex:36`

Replacement intent:

1. In moved-table captions, replace `Texture-path compatibility`, `asset-readiness`, and `textured columns` with diagnostic language.

   At `main.tex:722`, replace:

   ```tex
   Texture-path compatibility is an asset-readiness diagnostic after structural gates have passed.
   ```

   with:

   ```tex
   Render and surface diagnostics are supplementary checks after structural gates have passed.
   ```

   At `main.tex:732`, replace `Rendered-asset diagnostics` row label with `Render and surface diagnostics`, and replace `asset compatibility` with `visual inspection`.

   At `main.tex:758`, replace:

   ```tex
   textured columns are surface-voxel diagnostics after frozen Trellis2 realization
   texture-path connectivity is diagnostic
   ```

   with:

   ```tex
   rendered columns are surface-voxel diagnostics after selected realization
   rendered-surface connectivity is diagnostic
   ```

   At `main.tex:763`, rename:

   ```tex
   GLB r0 comps. & GLB r1 comps.
   ```

   to:

   ```tex
   Render r0 comps. & Render r1 comps.
   ```

   if width permits; otherwise use `Surf. r0` and `Surf. r1`.

2. In `main.tex:786`, replace `textured rendering` with `selected render diagnostics`.

3. At `main.tex:817`, replace `export fragmentation` with `mesh fragmentation after export/import`, preserving the caveat that this is not a state metric.

4. In appendix figure captions from `main.tex:847-996`, keep them diagnostic but remove heavy `textured GLB`, `texture schedule`, `texture path`, and `visual/export closure` wording unless the exact file format is necessary.

   Practical rule:

   - Use `rendered selected meshes` instead of `textured GLBs`.
   - Use `fixed rendering protocol` instead of `Trellis2 texture schedule`.
   - Use `render/import diagnostic caveat` instead of `raw GLB face components`.
   - Keep exact GLB mentions only where the diagnostic is explicitly about GLB import/export failure.

5. At `main.tex:1010`, replace:

   ```tex
   material export
   ```

   with:

   ```tex
   render diagnostics
   ```

6. In `drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`, simplify table headers and caption.

   At line 9, current headers:

   ```tex
   Case & Method & State & Proj. & Copy & Raw comp. & Occ. comp. & LCR & Status
   ```

   Suggested:

   ```tex
   Case & Method & Rec. state & Proj. & Direct copy & Raw mesh comp. & Occ. comp. & Occ. LCR & Status
   ```

   At line 36, keep the same data but clarify:

   - `Rec. state` means the row performs recursive latent-state updates with rule-readable handles.
   - `Raw mesh comp.` is a mesh-fragmentation diagnostic.
   - `Occ. LCR` is a structural proxy, not topology proof.

Why this batch third:

- It reduces residual terminology drift without changing core claims.
- It is mostly appendix material and included-table captions, so it can be delayed if the main manuscript needs fast stabilization.
- It compiles independently if each caption is edited without changing labels or table structure.

Verification for this batch:

- Run `rg -n "texture path|texture-path|textured GLB|GLB|PBR|export|asset-readiness|textureable|visual/export" main.tex drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`.
- Remaining hits should be either file names, diagnostic-specific appendix caveats, or old unused draft files outside included manuscript flow.
- Compile and inspect overfull boxes around the renamed table headers.

## Do Not Include in These Batches

- Do not edit generated figure pixels/PDFs in these small pushes.
- Do not rewrite abstract/introduction again unless a later full pass decides to shorten the introduction.
- Do not remove classical procedural baselines or weaken them into strawmen.
- Do not introduce new topology claims from render/surface diagnostics.
- Do not rename classical `shape grammar` related-work terms.

## Recommended Order

1. Batch 1: main-body texture/export de-emphasis.
2. Batch 2: experiment-flow closure.
3. Batch 3: appendix/table caption diagnostic cleanup.

Each batch is prose/table-caption scoped, should compile independently, and can be pushed separately.
