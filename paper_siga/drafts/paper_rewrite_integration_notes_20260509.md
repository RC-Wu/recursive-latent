# Paper Rewrite Integration Notes - 2026-05-09

Scope edited:
- `paper_siga/main.tex`

Integrated material:
- Replaced the abstract with the generation-model-native recursive language framing from `reviewer_rewrite_intro_method_20260509.tex`.
- Rewrote the Introduction opening and contributions around the failure of direct generator use, grammar-owned topology, masked local priors, and per-depth projection.
- Replaced Method 3.2--3.4 with:
  - minimal state `z_d=(V_d,F_d,A_d)`;
  - handle-based rule templates;
  - rule-family table;
  - compact recursive transition `Enc[Pi(Dec(T_theta(...)))]`;
  - paragraph/enumerate algorithms for recursive execution and connected projection;
  - masked flow naturalization equations.

Preserved:
- The old abstract, Introduction opening, 3.2 state tuple, 3.3 grammar tuple, and 3.4 long operator chain are retained as LaTeX comments in `main.tex`.

Still open:
- Later Method sections still partially use old `S_d`, `C_d`, and `F_d` notation and should be harmonized with `z_d`, `V_d`, and `F_d`.
- Results/Experiments remain mostly status-report style and still need the larger claim-based restructure from `docs/paper/reviewer_revision_action_plan_zh_20260509.md`.
- Texture/PBR has a cleaned compatibility table, but the method still needs a fuller material propagation/export subsection.
- Recursive refinement/effective resolution has not yet been added.
- No LaTeX compilation was run in this pass by request.
