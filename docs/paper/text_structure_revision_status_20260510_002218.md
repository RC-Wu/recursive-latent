# Text/structure revision status (2026-05-10 00:22)

Scope: edited only `paper_siga/main.tex` and this status note.

## Completed in `main.tex`

- Reframed the title, abstract, and introduction around a generation-model-native recursive grammar over sparse 3D latents, with projection described as execution semantics rather than the sole contribution.
- Strengthened the introduction's recursive-structure motivation and preserved conservative, evidence-gated claims with existing `\EvidencePending{}` / `\ExpFigTODO{}` markers.
- Expanded Preliminaries to define recursive asset generation, selected rules `\mathcal R_d`, sparse generator state, codec functions, masked naturalization, and optional texture export.
- Tightened Method notation so `\mathcal R_d` denotes selected rules and `\mathcal P_d` denotes proposals; renamed the reachable proposal domain to `\mathcal Q_{\mathrm{reach}}` to avoid rule-symbol confusion.
- Demoted texture/PBR wording to selected export compatibility and separated it from structural recursion claims.
- Fixed the projection objective so frontier and orphan penalties are additive terms.

## Compile status

- Command used from `paper_siga/`:
  `PATH="/Users/fanta/Library/TinyTeX/bin/universal-darwin:$PATH" latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`
- Status: success.
- Output: `main.pdf`, 27 pages according to the LaTeX build log.
- Notes: `pdfinfo` is not available on this machine. Final `main.log` has no undefined citation/reference warnings. Remaining warnings are existing-style ACM metadata/image-description warnings, BibTeX field warnings, and minor overfull/underfull boxes.

## Still evidence-gated

The main unresolved blockers remain the matched baseline/projection matrix, latent-vs-mesh comparison, naturalization ablation, semantic root/tip metrics, seed robustness, runtime/memory table, and final main/figures-only/supplement split.
