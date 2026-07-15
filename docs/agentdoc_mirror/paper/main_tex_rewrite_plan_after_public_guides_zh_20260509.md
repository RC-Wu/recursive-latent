# main.tex rewrite plan after public-guide textured GLB metrics - 2026-05-09

目标：把 `paper_siga/main.tex` 从“状态汇总型 draft”改成 SIGGRAPH Asia 风格的 method paper skeleton。核心叙事保持 **PS-RSLG: Projection-Stabilized Sparse-Latent Recursive Grammar**，但所有 claim 必须和当前证据链对齐：formal grammar v2、projection ablation、space competition/occupancy metrics、traditional baseline render、selected textured GLB compatibility。

不可做：不要直接改 `main.tex`；不要把 public-guide texture rows 写成主方法贡献；不要把 finite-depth asset generation 写成 infinite/world-scale generation。

## 1. Abstract sentence-to-evidence map

建议 abstract 控制在 7 句。每句都必须能落到一个 result / claim / figure / table：

1. **Problem sentence.**  
   Proposed: “Recursive procedural systems provide explicit control over branching, frontier accretion, and transform-copy structure, but their outputs often remain schematic meshes or scaffolds.”  
   Evidence/claim: Related Work + traditional space-colonization Blender/Cycles baseline figure.  
   Target anchor: Fig. `space_colonization_blender_contact_sheet`; citations `lindenmayer1968lsystemsI, prusinkiewicz1990abop, runions2007spacecolonization, witten1981dla, barnsley1988fractalsEverywhere`.

2. **Gap sentence.**  
   Proposed: “Modern sparse 3D generators provide learned geometry and material priors, yet one-shot generation and single-edit workflows do not expose a stable state transition for repeated recursive programs.”  
   Evidence/claim: TRELLIS/TRELLIS.2 interface as frozen sparse state; failure mode narrative should stay qualitative unless backed by table.  
   Target anchor: Method overview + one-shot/direct recursion failure examples if available.  
   Citations: `trellis2024, trellis2project, shapE2023, dreamgaussian2023, assetgen2024, hunyuan3d2025, sdeedit2021, flowedit2024`.

3. **Method sentence.**  
   Proposed: “We introduce PS-RSLG, a training-free recursive grammar whose typed rules operate on mesh-derived sparse O-Voxel/SLAT support, anchors, masks, and features in a frozen native-3D generator.”  
   Evidence/claim: Formal definition of state \(S_d=(C,F,U,A,B,M,H,K)\), grammar tuple, rule schema.  
   Target anchor: Method Sec. 3.1-3.3 + Method Fig. `method_system_grammar_polished_20260508.pdf`.  
   Claim strength: strong.

4. **Projection sentence.**  
   Proposed: “The key transition is not final cleanup: each recursive depth proposes sparse edits, merges and constrains them, decodes to a mesh, projects to an admissible connected/renderable state, and re-encodes before the next rule application.”  
   Evidence/claim: Operational semantics equation + Algorithm 1 + projection ablation.  
   Target anchor: Algorithm 1, Proposition 2, Table `projection_ablation`, Fig. `projection_depth_curves`.  
   Claim strength: strong for implementation, medium for theory.

5. **Main quantitative result sentence.**  
   Proposed: “On matched vine/tree competition cases, per-depth projection reduces fragment accumulation relative to direct recursion and final-only cleanup, while preserving a dominant occupancy-connected component through depth.”  
   Evidence/claim: Current ablation rows: vine compete d3, tree compete d3; occupancy proxy should be primary.  
   Target anchor: Table `projection_ablation`, Fig. `projection_depth_curves`, Fig. `space_competition_depth_curves`.  
   Caveat: phrase as “matched cases” not universal guarantee.

6. **Breadth sentence.**  
   Proposed: “The same grammar interface covers conservative competition growth, fork/side-branch stress tests, DLA-like frontier accretion, and transform-copy/portal assets; expressive operators reveal the current stability-expression boundary.”  
   Evidence/claim: Current operator curves and failure/stress-test rows.  
   Target anchor: operator token-growth curves + qualitative mesh matrix.  
   Caveat: do not say all categories succeed.

7. **Texture sentence.**  
   Proposed: “Selected projected meshes can be passed through Trellis2 textured GLB export, but material quality remains category-dependent, so texture/PBR compatibility is evaluated separately from recursive geometry stability.”  
   Evidence/claim: public-guide textured GLB metric status + texture QA table.  
   Target anchor: Table `texture_qa_draft` or revised Texture/PBR QA table.  
   Claim strength: compatibility/smoke test only.

## 2. Introduction: 5-paragraph structure

### Paragraph 1: Motivation from recursive assets

Function: establish why recursion matters in graphics assets, not just trees.  
Content: trees, roots, vines, corals, crystals, ornaments, portals, modular architecture, hard-surface motifs.  
Required contrast: classical procedural systems give control/interpretable structure, but output quality is often scaffold-like.  
Citations: `lindenmayer1968lsystemsI`, `prusinkiewicz1990abop`, `runions2007spacecolonization`, `witten1981dla`, `sander2000dlaReview`, `barnsley1988fractalsEverywhere`, plus shape grammar/CGA placeholders if added.

Writing note: avoid “procedural outputs are bad”; write “often require hand-authored surface/material design to become production assets.”

### Paragraph 2: Opportunity and mismatch in native 3D generators

Function: motivate TRELLIS-style sparse native 3D latent state.  
Content: modern generators synthesize textured/visually rich objects; sparse structured latents can encode/decode meshes; but one-shot image/text generation does not give rule-level control over multi-depth recursive topology.  
Citations: `objaverse2023`, `objaverseXL2023`, `trellis2024`, `trellis2project`, `assetgen2024`, `hunyuan3d2025`, `dreamgaussian2023`, `shapE2023`.  
Bridge sentence: “The question is not whether a generator can make a tree once, but whether a recursive program can repeatedly edit a 3D state without losing the scaffold it just created.”

### Paragraph 3: Failure mode and design principle

Function: explain why naive bridges fail and introduce the central design principle.  
Content: 2D scaffold to image-to-3D yields sheets/fragments; global flow/repair can overwrite topology; final-only cleanup lets bad components become future growth roots.  
Design principle: grammar owns support, attachment, and recurrence; frozen generator supplies representation, local prior, decode/re-encode, and optional material export.  
Evidence anchors: direct recursion/final-only ablation; qualitative failure rows if available.  
Tone: “Our experiments indicate” rather than universal statement.

### Paragraph 4: Method overview

Function: define PS-RSLG in prose before contributions.  
Content: mesh root -> sparse state -> typed rules over support/features/anchors -> proposal/merge/competition/masked naturalization -> decode/projection/re-encode -> next depth.  
Must include: projection is inside the recursive transition.  
Method figure reference: `fig:method-overview-draft` after figure caption is cleaned.

### Paragraph 5: Contributions and evidence boundaries

Recommended contributions:

1. A formal training-free **Projection-Stabilized Sparse-Latent Recursive Grammar** over mesh-derived sparse native-3D states.
2. An operational semantics and algorithm that integrates sparse proposal, masked merge/competition, optional local naturalization, decode/project/re-encode, and cache updates.
3. Coverage propositions showing L-systems, IFS, space colonization, DLA/frontier accretion, and finite local shape grammars as restricted instances.
4. An evaluation protocol and ablation showing why per-depth projection is stronger than direct recursion or final-only cleanup for conservative competition growth.
5. A geometry-first visual and metric study, with selected textured GLB export reported as compatibility rather than as the primary success criterion.

Do not list “infinite recursion” or “symmetry equivariance” as main contributions.

## 3. Related Work rewrite plan

Use 5 compact subsections or 5 paragraphs if page budget is tight.

### 3.1 Classical recursive procedural modeling

Paragraph scope: formal/procedural roots.  
Must cite: `lindenmayer1968lsystemsI`, `prusinkiewicz1990abop`, `barnsley1988fractalsEverywhere`, `runions2007spacecolonization`, `witten1981dla`, `sander2000dlaReview`.  
Add placeholders if bib is extended: `stiny1972shapeGrammars`, `muller2006cga`, `parish2001proceduralCities`, `wonka2003instantArchitecture`.

Claim: these systems expose explicit recursive structure and rule scheduling.  
Difference: PS-RSLG changes the interpreted state from strings/curves/voxels/hand-authored geometry to sparse native-3D latent support and decoded mesh regions.

Suggested closing sentence:  
“We use these systems twice: as related formal foundations and as degenerate grammar instances in our method, rather than as unrelated baselines.”

### 3.2 Neural 3D generation and sparse latent states

Paragraph scope: learned 3D asset priors and why TRELLIS-style sparse states matter.  
Must cite: `objaverse2023`, `objaverseXL2023`, `shapE2023`, `dreamgaussian2023`, `assetgen2024`, `hunyuan3d2025`, `trellis2024`, `trellis2project`.  
Claim: learned models supply geometry/material priors and mesh/GLB export paths.  
Difference: they are generally one-shot or local-edit systems, not recursive rule executors.

Safe wording: “We use a frozen TRELLIS-style representation as the recursion substrate.”  
Avoid: “TRELLIS guarantees topology preservation.”

### 3.3 Training-free native 3D editing

Paragraph scope: SDEdit/FlowEdit and native 3D editing preprints.  
Must cite: `sdeedit2021`, `flowedit2024`, `nano3d2025`, `voxhammer2025`, `latte3d2025`, `inpaintslat2025` if verified.  
Claim: frozen generative priors can be reused without retraining.  
Difference: these methods usually target single semantic edits or localized completion; recursive grammar edits compound errors across depth.  
Important: write masked naturalization as optional/local, not as solved topology-preserving repair.

### 3.4 Structure control and world-scale composition

Paragraph scope: skeleton/point structural control and learned/procedural world generation.  
Must cite: `skadapter2026`, `pointsTo3D2026`, `infinigen2023`, `citydreamer2023`, `scenedreamer2023`, `trellisworld2025`.  
Claim: structure control and compositional generation are adjacent motivations.  
Difference: PS-RSLG is finite-depth asset generation, not learned adapter training and not unbounded scene generation.  
Use this paragraph to preempt “is this world generation?” answer: no, narrower asset-level recursion.

### 3.5 Evaluation of recursive assets

Paragraph scope: metrics beyond visual appeal.  
Must cite: `raumonen2013treeModels`, `martinez2018minkowskiPorosity`, `cheeseman2022fractalCaution`.  
Content: mesh validity/renderability, voxel-occupancy 6-neighborhood connectivity proxy, largest-component ratio, branch/tip/skeleton metrics for space colonization, morphology descriptors for porous/frontier cases, cautious fractal proxies.  
Required phrase: “voxel-occupancy proxy” not “topological connectivity.”  
Reason: raw face components and large-tolerance welding can be misleading for tube baselines and textured GLB exports.

## 4. Method rewrite plan: propositions and algorithm boxes

### Method section order

1. Problem setting: finite-depth recursive asset generation.
2. Typed sparse-latent state \(S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d,K_d)\).
3. Grammar tuple \(\mathcal{G}\) and rule schema.
4. Algorithm 1: Projection-Stabilized Recursive Sparse-Latent Grammar.
5. Proposition 1: classical procedural systems as degenerate instances.
6. Sparse operators: transform-copy, competition/frontier growth, masked local naturalization.
7. Proposition 2: weak projection-stability invariant.
8. Extension paragraph: symmetry/cache/infinite-visible-window as conditional support/future direction.

### Algorithm Box 1: PS-RSLG recursive transition

Title: “Projection-Stabilized Sparse-Latent Recursive Grammar”  
Inputs: root mesh \(x_0\), frozen generator \(\theta\), grammar \(\mathcal{G}\), depth \(D\), projection schedule \(\lambda_d\), optional condition \(y\).  
Steps:

1. Encode \(x_0\) into sparse state \(S_0\).
2. For each depth \(d=0,\ldots,D-1\):
   - Select active symbols/rules with scheduler \(\mathcal{S}\).
   - Propose sparse patches/anchors with `Prop`.
   - Merge with masks and boundary kernels.
   - Apply competition, occupancy, attachment, token-budget constraints.
   - Optionally run masked local naturalization; keep old scaffold clamped.
   - Decode candidate mesh.
   - Project mesh/state to admissible set via component/attachment/renderability criteria.
   - Re-encode projected mesh to sparse state.
   - Update caches/history/diagnostics.
3. Export neutral mesh renders, metrics, and optional textured GLB.

Must show equation:

\[
S_{d+1}
=
\mathcal{C}_{d+1}\circ
\mathcal{E}_\theta\circ
\mathcal{P}_{\lambda_d}\circ
\mathcal{D}_\theta\circ
\mathcal{N}_{\theta,\Omega_d}^{\tau_d\rightarrow0}\circ
\Theta_{\Pi_d}\circ
\operatorname{Merge}_{B_d}\circ
\operatorname{Prop}_{R_d^\star}(S_d).
\]

### Proposition 1: coverage of classical systems

Name: “Degenerate procedural instances.”  
Claim: finite-depth IFS, L-system/turtle grammar, Runions-style space colonization, DLA-like frontier accretion, and finite local shape/CGA-style rules are recovered when learned sampler/projection/material terms are disabled or restricted and the interpretation map is chosen appropriately.  
Proof style: one paragraph + small table, no long proof in main text.

Table columns:

- Classical system
- PS-RSLG restriction
- State/rule mapping
- Current experimental use

Rows:

- L-system: \(U_d\in\Sigma^\star\), synchronous rewrite, turtle/frame interpretation; use for branching/tree motivation.
- IFS: single patch symbol, transform-copy \(C_{d+1}=\cup_iT_i(C_d)\); use for portal/scale-down/self-similar stress tests.
- Space colonization: tips/attractors/occupancy competition; use as main conservative growth operator and traditional baseline.
- DLA/frontier: frontier hitting kernel; use as porous/coral stress test.
- Finite shape/CGA grammar: typed faces/tiles/portals with split/extrude/repeat/replace; use for arch/portal/ornament cases.

Required caveat: “Coverage is about finite-step operational equivalence or quantized approximation; it is not a claim of visual superiority or complete shape-grammar expressiveness.”

### Proposition 2: weak projection-stability invariant

Name: “Per-depth projection bounds fragment mass under explicit assumptions.”  
Claim: if each depth introduces bounded new bad mass and projection returns an admissible nonempty state with fragment violation at most \(\epsilon_P\), then the recursively fed state satisfies a per-depth fragment bound of approximately \(\epsilon_P+\epsilon_E\), where \(\epsilon_E\) captures decode/re-encode error.  
Use: justify why projection belongs inside recursion.  
Do not overstate: this is not a convergence guarantee and does not prove final-only projection always fails.  
Experimental connection: pair with ablation table and depth curves showing direct/final-only vs per-depth behavior.

### Optional Proposition / Metric Definition: symmetry/cache

Keep in appendix or a short method limitation paragraph:

- Group-orbit rules can define a symmetry error \(E_G(S)=|G|^{-1}\sum_g d(gS,S)\).
- Cache/LOD visible-window recursion can bound active tokens under a windowed decoder.

Do not title this as a main proposition unless stable radial/crystal/cache figures exist.

## 5. Experiments rewrite plan: table and figure order

Experiments should be question-driven, not chronological.

### 5.1 Protocol first

Write before results:

- Assets/categories: vine/root/tree competition; fork/side stress tests; portal/arch/scale-down/hard-surface transform-copy; DLA/porous/frontier stress tests.
- Baselines: traditional procedural mesh, smoothed/remeshed procedural where available, one-shot Trellis2/image-to-3D, direct sparse recursion, final-only projection, per-depth projection.
- Primary connectivity metric: `primary_connectivity_metric = occupancy_6n_vertex_voxel`.
- Diagnostics: raw face components, welded components under sensitivity analysis, token/vertex/face counts, projection survival, branch/tip/skeleton metrics for traditional SC.
- Texture/PBR evaluated separately from geometry.

### Figure/Table order in main paper

1. **Fig. 1 Teaser / Head figure.**  
   Prefer neutral mesh render + selected textured GLB insets. Use only assets that pass visual QA. Caption must say texture exports are selected examples, not universal quality.

2. **Fig. 2 Method overview.**  
   Use `method_system_grammar_polished_20260508.pdf` after caption rewrite. Include grammar state, rule proposal, decode/project/re-encode loop, and classical-system degenerate instances.

3. **Table 1 Coverage table.**  
   Classical systems as PS-RSLG restrictions: L-system, IFS, space colonization, DLA, finite shape/CGA grammar. This can be in Method, not Experiments.

4. **Fig. 3 Projection depth curves.**  
   Use `projection_depth_curves_20260508.pdf`. Caption must identify largest connected component ratio under the primary occupancy proxy if that is what the data uses; otherwise update figure/caption.

5. **Table 2 Projection ablation.**  
   Direct recursion vs final-only projection vs per-depth projection. Keep vine/tree compete rows as strong evidence; fork rows as boundary evidence. Add metric names explicitly: component count, LCR, kept components.

6. **Fig. 4 Operator growth/stability curves.**  
   Use `space_competition_depth_curves_tokens_20260508.pdf`. Explain token growth and stability-expression tradeoff: conservative competition vs fork/side/portal/radial stress tests.

7. **Fig. 5 Qualitative mesh matrix.**  
   Fixed-camera Blender/Cycles neutral renders: proposed per-depth projection vs traditional procedural baseline vs unstable/aggressive operator examples. This should replace any matplotlib asset preview.

8. **Fig. 6 Traditional space-colonization baseline.**  
   Use `space_colonization_blender_contact_sheet.png` either as a standalone figure or part of Fig. 5. Caption: structurally meaningful but schematic/untextured; metrics use skeleton or occupancy proxy.

9. **Table 3 Mesh metric table.**  
   Primary occupancy components/LCR, occupied voxels, token count, branch/tip metrics where applicable. Do not use traditional raw face component count as the main comparison.

10. **Table 4 Texture/PBR compatibility table.**  
   Merge current `texture_qa_draft` with public-guide metric rows. Required columns: case, guide/source type, GLB export/import status, primary occupancy comps/LCR, visual QA label, paper use.  
   Rows to position carefully:
   - vine tendril: good structure, texture holes/white speckles.
   - tree roots: readable, material dirty/broken.
   - portal arch: strongest non-tree candidate.
   - porous/gloss: PBR/gloss smoke only, semantic mismatch.
   - scifi gear: mechanical read, holes/color issues.
   - snow arch: architecture candidate, local breaks.

11. **Appendix figures/tables.**  
   Weld tolerance sensitivity; raw face vs welded vs occupancy diagnostics; failed radial/echo/fork examples; public guide source/license notes; optional symmetry/cache proxy.

### Results narrative order

1. Direct recursion accumulates fragments; final-only cleanup is insufficient because intermediate fragments affect future growth.
2. Per-depth projection stabilizes conservative competition growth in matched vine/tree cases.
3. Conservative competition has the best stability; fork/side/radial/echo increase expression but reveal the boundary.
4. Traditional procedural baselines preserve skeleton-like structure but lack learned asset/material priors.
5. Texture export works technically for selected projected meshes, but visual material quality is category-dependent.

## 6. Overclaims to delete or weaken

### Delete from abstract/contributions

- “infinite 3D generation,” “unbounded recursive worlds,” “world-scale generation.”  
  Replace with: “finite-depth recursive 3D assets”; put visible-window/cache as extension.

- “strict symmetry/equivariance guarantee.”  
  Replace with: “group-orbit rules and symmetry error metrics are supported by the formalism.”

- “full flow/SDE repair preserves topology.”  
  Replace with: “masked local naturalization is optional; global flow repair can overwrite recursive topology.”

- “texture/PBR quality is solved.”  
  Replace with: “selected projected meshes are compatible with textured GLB export; material quality is category-dependent.”

- “all procedural systems / all shape grammars are covered.”  
  Replace with: “finite-step instances of L-systems, IFS, space colonization, DLA/frontier accretion, and finite local shape/CGA-style rules are recovered under restrictions.”

- “fractal dimension proves recursive quality.”  
  Replace with: “box-counting/fractal proxies are diagnostics; branching assets are not necessarily strict self-similar fractals.”

### Weaken in Results

- “supports depth-5 vine/root growth” should become “supports selected depth-5 conservative competition vine/root cases.”  
- “extends to branching, porous, ornamental, architectural, and hard-surface programs” should become “we evaluate these categories as breadth/stress tests; success varies by operator and category.”  
- “projection improves mesh connectedness” should specify “under the primary voxel-occupancy 6-neighborhood proxy” unless using raw face metrics for the exact table.  
- “public-guide textured results demonstrate quality” should become “public-guide rows test texture/PBR compatibility and export behavior, not standalone method superiority.”

## 7. Highest-priority writing advice

The top priority is to make every strong sentence pass a **claim -> mechanism -> evidence** test:

- Claim: finite-depth PS-RSLG stabilizes recursive asset growth.
- Mechanism: grammar-controlled support plus per-depth decode/project/re-encode.
- Evidence: projection ablation, depth curves, occupancy-proxy metrics, fixed-camera mesh renders.

Everything else, including masked flow, texture/PBR, symmetry, cache/LOD, public guides, and DLA/radial cases, should be written as secondary evidence, stress tests, or extensions unless a matching table/figure proves it under the same protocol.
