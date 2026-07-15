# PS-RSLG Paper Rewrite Plan: Projection-Stabilized Execution

Date: 2026-05-11  
Paper root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga`  
Primary files: `main.tex`, `references.bib`  
Status: active rewrite plan for context-compaction recovery

## 0. Recovery Contract

If context is compacted, read this document first, then read:

1. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex`
2. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/projection_masked_ablation_matrices_zh_20260511.md`
3. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/effective_resolution_zoom_retention_claim_gate_20260511.md`
4. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/progress/experiment3_case_inventory_subagent_20260511.md`
5. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/progress/experiment3_metrics_protocol_subagent_20260511.md`
6. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/progress/ablation_gap_audit_20260511_subagent.md`
7. `/Users/fanta/Downloads/论文修改意见与reviewer批评整理.md`

Do not restart the framing from “broad recursive sparse-latent grammar.” The current target framing is:

> Recursive 3D generation fails through intermediate executable-state contamination. PS-RSLG is a projection-stabilized executor that couples frozen sparse generator tokens with grammar-readable active handles, and places admissibility projection inside every recursive transition.

## 1. Core Story

The manuscript should not read like a feature inventory for a Trellis2 asset pipeline. Its single memorable claim should be:

- one-shot 3D generation predicts a terminal object;
- recursive 3D generation repeatedly exposes intermediate states to later rules;
- detached or invalid fragments are harmful because they may become future parents, frontiers, cached motifs, or handles;
- therefore recursive generation needs per-depth state-validity semantics;
- frozen sparse 3D generators provide useful local priors and a codec, but do not define recursive validity;
- PS-RSLG separates generator-native sparse latent tokens from grammar-readable active handles;
- admissibility projection selects root-attached active support, deactivates detached handles, and re-encodes the projected state before later rules can read it.

Preferred title direction:

- `Projection-Stabilized Execution for Recursive Sparse 3D Latents`

Keep PS-RSLG as an acronym if useful, but do not oversell “grammar” as the largest contribution. Grammar rules are proposal sources; projection-stabilized execution is the contribution.

## 2. Claim Boundaries

Strong, evidence-backed main claims:

- Per-depth projection stabilizes conservative finite-depth recursion. Current Experiment 2 table supports this with full PS-RSLG `Occ. LCR=1.000`, `Root reach.=1.000`, `Orphan active=0`, `Handle survival=1.000`, `Fail rate=0`.
- Final-only cleanup is insufficient for recursive state validity. It can obtain high terminal occupancy LCR while leaving low root reachability and orphan active handles.
- Masked local naturalization improves local surface/asset-quality proxies under projection. It is not global topology repair.
- One-shot generation, trivial latent copy, and generated-root mesh-space copy are negative controls for lacking typed handles, projection, and recursive state update. This is a novelty gate, not a universal claim against all 3D generators.

Claims that must remain narrow or supplementary:

- Effective resolution and zoom retention are selected-case diagnostics/proxies, not universal quantitative proof.
- Coral/DLA/frontier and crystal examples are inspired/scaffold examples, not physical simulations.
- Pyrite/crystal rows are lattice/crystal-inspired scaffolds and export compatibility, not exact symmetry or watertight topology evidence.
- Same-root matrix remains partial except for closed subsets.
- Hunyuan baseline is not a full comprehensive one-shot/texture baseline unless new evidence is added.

Avoid these phrases in main claims unless carefully qualified:

- “universal recursive generator”
- “model-native projection” as if pure latent optimization
- “topology repair” for masked naturalization
- “physical DLA/crystal growth”
- “watertight” or “manifold” without direct diagnostics
- “effective resolution superiority” without the proxy caveat

## 3. Section Rewrite Plan

### Title and Abstract

Replace the old grammar-centered title and abstract. Abstract must be one paragraph and follow this logic:

1. Recursive 3D generation is a state-validity problem.
2. Frozen sparse generators provide priors but do not prevent invalid components from contaminating later derivation steps.
3. PS-RSLG couples sparse latent tokens with grammar-readable handles.
4. Rules propose local edits; generator is used for masked realization and codec operations.
5. Per-depth admissibility projection selects root-attached active support and deactivates detached handles before later rule selection.
6. Controlled finite-depth programs show active-state preservation relative to direct recursion/final-only cleanup.
7. Texture/PBR export is asset compatibility, not the structural contribution.

### Introduction

Rewrite around one-shot vs recursive execution, not category coverage:

1. Opening paragraph: recursive assets are sequences of local decisions; invalid fragments become executable state.
2. Procedural paragraph: classical systems already maintain explicit state, but require separate asset-ready realization.
3. Generator paragraph: modern sparse generators provide complementary local priors/codecs but no recursive state validity semantics.
4. Failure paragraph: 2D scaffolds, direct sparse edits, global repair, and final-only cleanup fail for recursive reasons.
5. Proposed paragraph: PS-RSLG as projection-stabilized executor.
6. Contributions: four bullets centered on state, rule proposals, per-depth projection, implementation on frozen sparse generator.

### Related Work

Rewrite into five subsections:

1. Procedural recursive modeling.
2. Structured and programmatic shape generation.
3. 3D asset generators and sparse structured latents.
4. 3D editing and structure-conditioned control.
5. Positioning.

Add verified citations for:

- GRASS: `grass2017`, DOI `10.1145/3072959.3073637`
- StructureNet: `structurenet2019`, DOI `10.1145/3355089.3356527`
- ShapeAssembly: `shapeassembly2020`, DOI `10.1145/3414685.3417812`

Existing relevant keys include `trellis2025`, `trellis2project`, `hunyuan3d2025`, `voxhammer2025`, `latte3d2025`, `inpaintslat2026`, `skadapter2026`, `shape2vecset2023`, `shapE2023`.

### Problem Setup and Generator Interface

Rename `Preliminaries` to `Problem Setup and Generator Interface`.

Keep only:

- finite-depth recursive program execution;
- frozen sparse generator interface.

Use notation:

- native generator state: `u_d=(V_d,F_d)`;
- recursive program state: `s_d=(u_d,A_d)`.

Do not repeat related work. Do not list all classical systems again except as brief context.

### Method

Rename method to `Projection-Stabilized Recursive Sparse-Latent Execution`.

Target subsections:

1. `Program State`: define `u_d`, `s_d`, active handles, root reachability, admissibility.
2. `Rule Proposals`: simplify rule output to sparse edits, handle updates, masks, and attachment certificates.
3. `Recursive Transition`: select -> propose -> filter -> merge -> masked realization -> decode -> project -> encode.
4. `Admissibility Projection`: core contribution; add standalone algorithm and invariant/proposition.
5. `Masked Local Realization`: generator only modifies masked region; projection decides executable topology.
6. `Scope and Implementation Notes`: finite-depth authored programs, budgets, export compatibility.

Remove or compress:

- lengthy operator admission contract from method;
- scheduling score details, unless appendix;
- material handles as core state;
- method-section experimental results;
- “model-native projection” language.

### Discussion and Conclusion

Do not end with limitations. Keep limitations concise and move fuller limitations to appendix if needed. Add a positive conclusion that restates:

- state contamination;
- separation of native sparse tokens and active handles;
- per-depth admissibility projection;
- finite-depth executor over a frozen generator.

## 4. Citation Verification Notes

Verified through Crossref on 2026-05-11:

- GRASS returned BibTeX for DOI `10.1145/3072959.3073637`.
- StructureNet returned BibTeX for DOI `10.1145/3355089.3356527`.
- ShapeAssembly returned BibTeX for DOI `10.1145/3414685.3417812`.

Do not invent citations. If additional citations are needed, verify through Crossref, arXiv, ACM DL, CVF, OpenReview, or project pages before adding BibTeX.

## 5. Verification Checklist

Before reporting completion:

- `main.tex` compiles with `latexmk -g -xelatex -interaction=nonstopmode -halt-on-error main.tex`.
- No undefined citations or references caused by the rewrite.
- Abstract, Introduction, Related Work, Problem Setup, Method, and Conclusion use the same story.
- No internal Chinese writing plan remains in the main submission narrative unless deliberately kept in appendix as internal draft material.
- Chinese modification log is updated at `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/progress/paper_rewrite_log_zh_20260511.md`.

