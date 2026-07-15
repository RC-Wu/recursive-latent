# Paper Revision Follow-up - 2026-05-09

Scope edited in this pass:
- `paper_siga/main.tex`

What changed:
- Harmonized post-3.5 visible method notation with the current sparse-latent state `z_d=(\mathcal V_d,\mathbf F_d,\mathcal A_d)`.
- Replaced the duplicate old `S_d`/`C_d` projection and sampler text after "Classical Systems as Limits" with:
  - `Operator Scheduling and Sparse Competition`
  - `Recursive Effective Resolution and Infinite Refinement`
  - `Material Handles and Trellis2 Texture Export`
  - a revised finite-depth recursion-scope paragraph using `\mathcal V_d`.
- Preserved the replaced projection/sampler block as LaTeX comments in `main.tex` for later recovery.
- Reframed the experiment section around two current claims:
  - connected recursive sparse-latent grammar with per-depth projection stabilizes finite-depth recursion;
  - projected meshes can be exported through the Trellis2 texture/PBR path as selected inspectable assets.
- Added caveats that smoke/candidate texture exports, DLA/crystal-inspired examples, and aggressive operators are not yet final-quality or universal success claims.

Checks performed:
- Searched `main.tex` for old `S_d`, `C_d`, `F_d`, and `P_\lambda` notation after the edit.
- Remaining `S_d`/`C_d` hits are in LaTeX comments retained as revision trace.
- Visible `F_d` occurrences are part of the current `\mathbf F_d` notation.
- Attempted `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`; compile could not start because `latexmk` is not available in the current PATH. `pdflatex`, `bibtex`, `xelatex`, `lualatex`, `tectonic`, and `chktex` were also unavailable, so only static checks were possible in this pass.

Still needing main-agent decisions:
- Whether to physically move the detailed "Classical Systems as Limits" derivation to an appendix or keep it in Method.
- Whether to merge `Experiments` and `Results` into a single conventional experimental section in this submission draft.
- Which connected scaffold v2 assets should be promoted to main figures: current QA suggests `bismuth_hopper_bismuth_hq` and possibly `pyrite_lattice_pyrite_hq`; DLA/coral-inspired assets should remain appendix/stress-test unless stronger true mesh evidence is added.
- Whether bridge-aware per-depth projection is ready for a visible main-table column, or should remain a future/diagnostic item until true mesh and Blender evidence is complete.
