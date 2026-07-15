# SIGGRAPH Asia Paper Skeleton

This folder contains the rough working paper skeleton for the Recursive 3D Generative Growth project.

- `main.tex`: early ACM/SIGGRAPH-style draft skeleton.
- `references.bib`: rough bibliography; some 2025 training-free TRELLIS-related entries need verified author metadata.
- `template/`: CTAN `acmart` package mirror. The direct ACM portal download was blocked by Cloudflare, so CTAN is used as the local template source.

Current compile status: compiled locally on 2026-05-09 with TinyTeX:
`PATH=/Users/fanta/Library/TinyTeX/bin/universal-darwin:$PATH latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`.
The generated `main.pdf` is 9 pages. Remaining warnings are template/accessibility metadata, BibTeX metadata completeness, and minor layout overfull/underfull boxes.
