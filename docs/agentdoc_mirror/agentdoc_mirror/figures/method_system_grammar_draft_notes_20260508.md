# Method Figure Draft Notes - 2026-05-08

Figure draft:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/figures/method_system_grammar_draft_v2_20260508.png`

Paper copy:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/method_system_grammar_draft_v2_20260508.png`

## Purpose

This is the first paper-method figure draft for the strengthened grammar/system story. It should make the following points visible without reading the full method section:

1. The method is not a simple engineering chain. It is a typed grammar semantics over a recursive sparse state.
2. Trellis2 is part of the state transition: encode, masked sampler, decode, re-encode, and texture/PBR export.
3. Projection is inside the recursive loop, not a final cleanup.
4. Classical procedural systems are covered as special cases when the learned sampler/projection/constraints are disabled or simplified.
5. The bottom evidence strip maps the method blocks to current experiments.

## Current Visual Read

Useful:

- The top row communicates root -> encode -> state -> rule -> proposal.
- The middle row communicates proposal -> competition -> sampler -> decode -> projection -> re-encode.
- The feedback loop makes per-depth projection explicit.
- The lower panels keep the IFS/L-system/space-colonization/DLA/symmetry coverage visible.

Problems:

- It is still a draft bitmap, not a final vector figure.
- It does not include real result insets yet.
- The feedback line and texture branch are acceptable for planning but should be redrawn cleaner in Illustrator/Slides/TikZ/Figma.
- The formulas use ASCII approximations (`theta`, `lambda`) rather than typeset math.

## Required Next Iteration

1. Redraw as vector art.
2. Add 2-3 small real visual insets:
   - root mesh / sparse state preview;
   - projection ablation mini visual;
   - textured GLB result.
3. Replace ASCII formulas with LaTeX-rendered equations.
4. Separate the `Texture/PBR Export` branch from the recursive state loop more clearly.
5. Make the bottom coverage panel compact enough for a two-column paper figure if needed.

## Paper Placement

Inserted into:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex`

as `Figure~\\ref{fig:method-overview-draft}` near the start of the Method section.

