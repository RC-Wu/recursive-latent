# Related-Work / Reference Supplement Plan - 2026-05-08

Scope: planning supplement for `paper_siga/main.tex` and `paper_siga/references.bib`.
No edits were made to those files. This document only proposes additions and
positioning refinements for the Recursive Sparse-Latent Grammars / Trellis2
SIGGRAPH Asia draft.

Inputs read:

- `docs/related_work_reference_audit_20260508.md`
- `paper_siga/references.bib`
- `paper_siga/main.tex`

Web metadata was checked for current/preprint-sensitive items on 2026-05-08.

## Executive Recommendation

The current bibliography covers the core story, but it is thin in three places:

1. procedural recursion history beyond the three already-cited anchors;
2. evaluation references for fractal/branching/porous growth assets;
3. current structure-aware and PBR/textured 3D asset generation context.

Add only a small number of references to the main paper. A SIGGRAPH Asia related
work section should stay focused on the distinction from one-shot generation and
single-edit training-free systems. Most of the items below are best used in a
short appendix/reference expansion unless the manuscript explicitly expands the
corresponding claim.

## Existing Keys To Keep And Reposition

| Existing key | Recommended role | Reliability note |
|---|---|---|
| `prusinkiewicz1990abop` | Canonical L-system and algorithmic botany foundation for recursive plant-like form. | Stable book citation with Springer DOI. Keep. |
| `runions2007spacecolonization` | Primary attractor-competition baseline for tree/root/vine growth. | Stable Eurographics Natural Phenomena paper. Current bib uses `@article`; `@inproceedings` would be cleaner later. |
| `witten1981dla` | Primary stochastic frontier-accretion baseline for porous/coral/crystal assets. | Stable PRL DOI. Keep. |
| `trellis2024` | Primary sparse structured latent baseline and representation predecessor. | Stable CVPR 2025 paper metadata exists; current key is acceptable, but venue/DOI can be updated later. |
| `trellis2project` | Direct model basis: O-Voxel, SC-VAE, PBR attributes, mesh/O-Voxel pipeline. | Confirmed arXiv 2512.14692 and official Microsoft project/GitHub. Treat as tech-report/preprint, not peer-reviewed venue unless a venue appears. |
| `nano3d2025` | Closest training-free TRELLIS editing contrast: localized edit plus voxel/SLAT merge preserving unedited regions. | Confirmed arXiv 2510.15019. Also appears as ICLR 2026 on OpenReview; use venue only after confirming camera-ready metadata. |
| `voxhammer2025` | Training-free native 3D-space editing contrast; useful for "preserve unedited geometry" discussion. | Confirmed arXiv 2508.19247. Preprint/project reliability. |
| `latte3d2025` | Training-free latent-space 3D editing from textual instruction. | Confirmed arXiv 2509.00269. Preprint/project reliability. |
| `inpaintslat2025` | Structured 3D latent inpainting / initial-noise optimization; relevant to local naturalization and masked repair. | Confirmed arXiv 2605.00664, May 2026. Very fresh preprint. Key should eventually become `inpaintslat2026` or retain key with explicit `year={2026}`. |
| `stableDiffusion35ModelCard` | Use only if the text explicitly names SD3.5. | Already in bib but unused in `main.tex`; non-archival model-card citation. |

## Priority Additions

These are the references most worth adding if the Related Work and Metrics
sections are expanded.

| Proposed key | Citation role | Suggested cite location | Reliability note |
|---|---|---|---|
| `lindenmayer1968lsystemsI` | Original L-system formalism: cellular/filament rewriting before graphics-oriented algorithmic botany. | First paragraph of Related Work, before or with `prusinkiewicz1990abop`, if claiming lineage from formal grammars rather than just graphics practice. | Stable Journal of Theoretical Biology paper. Part I DOI: `10.1016/0022-5193(68)90079-9`; Part II DOI: `10.1016/0022-5193(68)90080-5`. Add either two keys or a combined note, but two keys are bibliographically cleaner. |
| `weber1995realisticTrees` | Classic SIGGRAPH procedural tree modeling/rendering, useful to connect rule/control parameters to renderable trees. | Procedural and Recursive Modeling subsection after L-systems. | Stable SIGGRAPH 1995 ACM paper, DOI `10.1145/218380.218427`. |
| `barnsley1988fractalsEverywhere` | IFS and transform-copy fractal foundation for portal/recursive-copy assets. | Introduction sentence that currently names iterated function systems without a citation. | Stable book citation. No DOI needed; use publisher/ISBN. |
| `mandelbrot1982fractalGeometry` | Fractal/self-similarity vocabulary and historical basis for fractal asset metrics. | Metrics or procedural foundations; use sparingly, not as technical method evidence. | Stable book citation; ISBN `0-7167-1186-9`. |
| `sander2000dlaReview` | DLA review explaining natural-object applicability, tenuous/self-similar clusters, and limitations. | DLA/coral/porous baseline discussion or appendix. | Stable Contemporary Physics review, DOI `10.1080/001075100409698`. Useful if DLA gets more than one sentence. |
| `objaverseXL2023` | Dataset-scale context for modern 3D foundation models beyond Objaverse 1.0; relevant to TRELLIS/TRELLIS.2 training-data ecosystem. | 3D Generative Models subsection if discussing scaling or training data. | Stable NeurIPS 2023 Datasets and Benchmarks/arXiv metadata. Add only if dataset scale is discussed. |
| `assetgen2024` | Text-to-mesh generation with high-quality geometry, textures, and PBR materials; helps frame "asset-quality textured mesh export" as a broader 3D generation target. | Texturing/export paragraph or 3D generation subsection. | arXiv 2407.02445; current evidence from arXiv/OpenReview/project pages. Use as preprint unless venue confirmed. |
| `dreamgaussian2023` | Efficient 3D content creation with mesh extraction and UV texture refinement; useful for downstream textured-mesh/export framing. | Texturing/export paragraph, not core method comparison. | arXiv 2309.16653; ICLR 2024 Oral according to official GitHub, but verify final proceedings before writing venue. |
| `hunyuan3d2025` | High-resolution textured 3D asset generation with separate shape and texture components. | Texturing/export or one-shot textured asset baselines. | arXiv 2501.12202. Strong current baseline context but not central to recursive editing. |
| `cheeseman2022fractalCaution` | Reliability guardrail for box-counting / sandbox fractal dimensions on branching structures. | Metrics section when reporting fractal dimension or self-similarity. | Peer-reviewed Mathematics 2022, DOI `10.3390/math10050839`. Important because it warns that branching structures are not always strictly self-similar. |
| `balankin2024fractalMorphologySurvey` | Modern survey of fractal morphology features: dimension, lacunarity, multifractality, anisotropy. | Metrics appendix for fractal/growth asset descriptors. | Peer-reviewed Fractal and Fractional 2024, DOI `10.3390/fractalfract8080440`. Broad survey, not graphics-specific. |
| `raumonen2013treeModels` | Branch topology, branch-size distribution, cylinder/QSM metrics for tree structures from 3D data. | Metrics section for tree/vine/root branch preservation and topology. | Peer-reviewed Remote Sensing 2013, DOI `10.3390/rs5020491`. Strong for branch metrics, not generative-model quality. |
| `martinez2018minkowskiPorosity` | 3D porous morphology metrics: volume, surface area, curvature, connectivity from binary volumes. | Metrics section for DLA/coral/porous cases. | Peer-reviewed Frontiers in Environmental Science 2018, DOI `10.3389/fenvs.2018.00055`. Domain is soil porosity, but metrics transfer well to voxelized porous assets. |

## Conditional / Appendix-Only Additions

These are useful if the paper expands the surrounding claim, but they should not
crowd the main Related Work.

| Proposed key | Citation role | Reliability note |
|---|---|---|
| `runions2005leafVenation` | Precursor attractor/venation model behind space-colonization thinking. Add if explaining the biological/leaf-venation origin of attractor competition. | Stable graphics paper, but less direct than `runions2007spacecolonization` for 3D tree assets. |
| `skadapter2026` | Skeleton-conditioned native 3D structural control; useful contrast because it trains an adapter while this paper stays training-free. | arXiv 2603.14152, March 2026. Very current preprint. Cite as "recent preprint" only. |
| `pointsTo3D2026` | Point-cloud-prior structure-aware 3D generation in TRELLIS; contrast with direct recursive sparse support control. | arXiv 2603.18782, March 2026. Very current preprint. It trains/adds a structure inpainting network, so it is not training-free in the same sense. |
| `preditor3d2024` | Broader training-free 3D object/shape editing context before NANO3D/VoxHammer. | arXiv 2412.06592; use only if expanding the editing subsection. |
| `repaint2022` | Foundational diffusion inpainting method if discussing TRELLIS editing internals or mask-based repair ancestry. | Stable CVPR 2022 paper. Indirect for this draft unless Naturalize/Inpaint is expanded. |
| `metatexturegen2024` | Dedicated 3D texture generation context if texture quality becomes a claimed result. | arXiv 2407.02430. Appendix-only unless texture becomes a contribution. |
| `fuse3d2026` | Multi-image region-level controlled 3D asset generation through TRELLIS lifting; contrast for control mechanisms. | SIGGRAPH Asia 2025 project page reports ACM DOI and arXiv 2602.17040, but verify final ACM metadata before adding. |

## Proposed Bib Key Details

The following entries are not inserted into `references.bib`; they are planning
targets. Verify capitalization/style before final import.

### Procedural / Recursive Modeling

```bibtex
@article{lindenmayer1968lsystemsI,
  title={Mathematical Models for Cellular Interactions in Development I. Filaments with One-Sided Inputs},
  author={Lindenmayer, Aristid},
  journal={Journal of Theoretical Biology},
  volume={18},
  pages={280--299},
  year={1968},
  doi={10.1016/0022-5193(68)90079-9}
}

@article{lindenmayer1968lsystemsII,
  title={Mathematical Models for Cellular Interactions in Development II. Simple and Branching Filaments with Two-Sided Inputs},
  author={Lindenmayer, Aristid},
  journal={Journal of Theoretical Biology},
  volume={18},
  pages={300--315},
  year={1968},
  doi={10.1016/0022-5193(68)90080-5}
}

@inproceedings{weber1995realisticTrees,
  title={Creation and Rendering of Realistic Trees},
  author={Weber, Jason and Penn, Joseph},
  booktitle={Proceedings of the 22nd Annual Conference on Computer Graphics and Interactive Techniques},
  pages={119--128},
  year={1995},
  doi={10.1145/218380.218427}
}

@book{barnsley1988fractalsEverywhere,
  title={Fractals Everywhere},
  author={Barnsley, Michael F.},
  publisher={Academic Press},
  address={Boston},
  year={1988},
  isbn={0120790629}
}

@book{mandelbrot1982fractalGeometry,
  title={The Fractal Geometry of Nature},
  author={Mandelbrot, Benoit B.},
  publisher={W. H. Freeman},
  address={New York},
  year={1982},
  isbn={0716711869}
}

@article{sander2000dlaReview,
  title={Diffusion-Limited Aggregation: A Kinetic Critical Phenomenon?},
  author={Sander, Leonard M.},
  journal={Contemporary Physics},
  volume={41},
  number={4},
  pages={203--218},
  year={2000},
  doi={10.1080/001075100409698}
}
```

### Modern 3D Generation / Texturing / Export

```bibtex
@misc{objaverseXL2023,
  title={Objaverse-XL: A Universe of 10M+ 3D Objects},
  author={Deitke, Matt and Liu, Ruoshi and Wallingford, Matthew and Ngo, Huong and Michel, Oscar and Kusupati, Aditya and Fan, Alan and Laforte, Christian and Voleti, Vikram and Gadre, Samir Yitzhak and VanderBilt, Eli and Kembhavi, Aniruddha and Vondrick, Carl and Gkioxari, Georgia and Ehsani, Kiana and Schmidt, Ludwig and Farhadi, Ali},
  year={2023},
  eprint={2307.05663},
  archivePrefix={arXiv},
  primaryClass={cs.CV}
}

@misc{assetgen2024,
  title={Meta 3D AssetGen: Text-to-Mesh Generation with High-Quality Geometry, Texture, and PBR Materials},
  author={Siddiqui, Yawar and Monnier, Tom and Kokkinos, Filippos and Kariya, Mahendra and Kleiman, Yanir and Garreau, Emilien and Gafni, Oran and Neverova, Natalia and Vedaldi, Andrea and Shapovalov, Roman and Novotny, David},
  year={2024},
  eprint={2407.02445},
  archivePrefix={arXiv},
  primaryClass={cs.CV},
  url={https://assetgen.github.io}
}

@misc{dreamgaussian2023,
  title={DreamGaussian: Generative Gaussian Splatting for Efficient 3D Content Creation},
  author={Tang, Jiaxiang and Ren, Jiawei and Zhou, Hang and Liu, Ziwei and Zeng, Gang},
  year={2023},
  eprint={2309.16653},
  archivePrefix={arXiv},
  primaryClass={cs.CV},
  url={https://dreamgaussian.github.io/}
}

@misc{hunyuan3d2025,
  title={Hunyuan3D 2.0: Scaling Diffusion Models for High Resolution Textured 3D Assets Generation},
  author={{Tencent Hunyuan3D Team}},
  year={2025},
  eprint={2501.12202},
  archivePrefix={arXiv},
  primaryClass={cs.CV},
  url={https://github.com/Tencent-Hunyuan/Hunyuan3D-2}
}
```

Reliability notes:

- `assetgen2024`, `dreamgaussian2023`, and `hunyuan3d2025` should be used as
  context for textured/PBR mesh expectations, not as direct baselines unless
  experiments actually compare against them.
- `dreamgaussian2023` appears to have ICLR 2024 Oral metadata via the official
  repository, but keep the arXiv entry until proceedings metadata is verified.
- For `hunyuan3d2025`, replace the organization author with the full author
  list before final bibliography polish if space/style requires it.

### Structure-Aware / TRELLIS-Adjacent Control

```bibtex
@misc{skadapter2026,
  title={SK-Adapter: Skeleton-Based Structural Control for Native 3D Generation},
  author={Wang, Anbang and Ao, Yuzhuo and Wu, Shangzhe and Tang, Chi-Keung},
  year={2026},
  eprint={2603.14152},
  archivePrefix={arXiv},
  primaryClass={cs.CV},
  url={https://sk-adapter.github.io/}
}

@misc{pointsTo3D2026,
  title={Points-to-3D: Structure-Aware 3D Generation with Point Cloud Priors},
  author={Xia, Jiatong and Duan, Zicheng and van den Hengel, Anton and Liu, Lingqiao},
  year={2026},
  eprint={2603.18782},
  archivePrefix={arXiv},
  primaryClass={cs.CV}
}
```

Reliability notes:

- Both are March 2026 arXiv preprints. They are relevant because they show that
  structure control for native/TRELLIS-like 3D generation is becoming active.
- They should be framed as contrastive: they add/train control mechanisms,
  whereas this project repurposes a frozen generator through recursive sparse
  support operators and projection.

### Evaluation Metrics For Growth / Fractal Assets

```bibtex
@article{cheeseman2022fractalCaution,
  title={Estimating the Fractal Dimensions of Vascular Networks and Other Branching Structures: Some Words of Caution},
  author={Cheeseman, Alison K. and Vrscay, Edward R.},
  journal={Mathematics},
  volume={10},
  number={5},
  pages={839},
  year={2022},
  doi={10.3390/math10050839}
}

@article{balankin2024fractalMorphologySurvey,
  title={Morphological Features of Mathematical and Real-World Fractals: A Survey},
  author={Pati{\~n}o-Ortiz, Miguel and Pati{\~n}o-Ortiz, Juli{\'a}n and Mart{\'i}nez-Cruz, Miguel {\'A}ngel and Esquivel-Pati{\~n}o, Fernando Ren{\'e} and Balankin, Alexander S.},
  journal={Fractal and Fractional},
  volume={8},
  number={8},
  pages={440},
  year={2024},
  doi={10.3390/fractalfract8080440}
}

@article{raumonen2013treeModels,
  title={Fast Automatic Precision Tree Models from Terrestrial Laser Scanner Data},
  author={Raumonen, Pasi and Kaasalainen, Mikko and {\AA}kerblom, Markku and Kaasalainen, Sanna and Kaartinen, Harri and Vastaranta, Mikko and Holopainen, Markus and Disney, Mathias and Lewis, Philip},
  journal={Remote Sensing},
  volume={5},
  number={2},
  pages={491--520},
  year={2013},
  doi={10.3390/rs5020491}
}

@article{martinez2018minkowskiPorosity,
  title={Minkowski Functionals of Connected Soil Porosity as Indicators of Soil Tillage and Depth},
  author={San Jos{\'e} Mart{\'i}nez, Fernando and Mart{\'i}n, Luisa and Garc{\'i}a-Guti{\'e}rrez, Carlos},
  journal={Frontiers in Environmental Science},
  volume={6},
  pages={55},
  year={2018},
  doi={10.3389/fenvs.2018.00055}
}
```

Metric use notes:

- Report connected-component count, largest-component ratio, non-manifold/open
  edge indicators, and render/export success as primary reliability metrics
  because they directly test recursive stability and asset usability.
- Use branch/tip preservation, bifurcation count, branch length distribution,
  and attachment survival for tree/root/vine cases. `raumonen2013treeModels`
  supports this style of topology-aware tree measurement.
- Use fractal dimension only as a descriptive statistic, not as proof of
  fractality. `cheeseman2022fractalCaution` should be cited if box-counting or
  sandbox dimensions appear in a table.
- Use lacunarity/anisotropy/multifractal descriptors only if there is enough
  resolution and scale range. The current outputs may not support strong claims.
- For porous/DLA cases, add volume fraction, surface-area-to-volume proxy,
  Euler/connectivity proxy, and pore/void connectedness after voxelization.
  `martinez2018minkowskiPorosity` supports the volume/surface/curvature/
  connectivity vocabulary, even though the application domain is soil.

## Related-Work Positioning Plan

### Procedural Foundations

Recommended paragraph role:

- Keep the current L-system, space-colonization, and DLA anchors.
- Add IFS explicitly if transform-copy/portal recursion remains in the paper:
  cite `barnsley1988fractalsEverywhere`.
- Add `weber1995realisticTrees` only if the paper discusses renderable
  procedural trees rather than abstract symbolic grammars.

Reliability framing:

- These are stable and low-risk citations.
- Do not overclaim that the method inherits biological realism from these
  models. The paper borrows operators and control structure, not plant biology.

### TRELLIS / TRELLIS.2 And Sparse Latents

Recommended paragraph role:

- Keep TRELLIS/TRELLIS.2 as central.
- State TRELLIS provides sparse structured latents and TRELLIS.2 extends this
  toward O-Voxel/SC-VAE, complex topology, and PBR attributes.
- Use `objaverseXL2023` only if explaining why 3D foundation training can scale.

Reliability framing:

- `trellis2024` has CVPR 2025 metadata, stable enough for main text.
- `trellis2project` is currently an arXiv/project-page citation; describe as a
  recent model/tech report unless venue data appears.

### Training-Free 3D Editing

Recommended paragraph role:

- Existing keys already cover the strongest contrast set:
  `nano3d2025`, `voxhammer2025`, `latte3d2025`, `inpaintslat2025`.
- The manuscript should say these methods target a single localized edit or
  completion, whereas R-SLG applies a recursive program repeatedly and evaluates
  compounded stability.
- If space allows, use NANO3D as the named closest comparison because it uses
  TRELLIS plus FlowEdit-style editing and voxel/SLAT merge preservation.

Reliability framing:

- NANO3D is now more reliable than a normal preprint if citing the ICLR 2026
  OpenReview version, but final metadata should be checked before changing the
  bib entry.
- InpaintSLat is the freshest and highest-risk item. It is useful for currency,
  but should not be a pillar of the argument.

### Texturing / Export

Recommended paragraph role:

- Add this only if the paper keeps the claim that true textured GLB/PBR export
  works for multiple examples.
- Use `assetgen2024` and/or `hunyuan3d2025` to show that modern 3D generators
  are judged as textured, PBR/exportable assets, not just neutral meshes.
- Use `dreamgaussian2023` if discussing mesh extraction plus UV texture
  refinement as a downstream usability target.

Reliability framing:

- These citations support expectations and evaluation vocabulary. They should
  not be treated as direct baselines unless the experiments compare them.

### Evaluation

Recommended paragraph role:

- The paper's main quantitative table should stay implementation-grounded:
  components, largest-component ratio, token growth, mesh validity, texture
  export success, and render contact sheets.
- Add a short "growth metrics" paragraph or appendix note with tree/topology,
  fractal/porous descriptors, and caveats.

Reliability framing:

- Fractal metrics are easy to misuse. Cite the caution paper if reporting them.
- Do not claim natural fractal correctness unless there is scale-range evidence.
- Use morphology descriptors as secondary characterization, not primary proof
  of method quality.

## Suggested Minimal Main-Text Citation Changes Later

Do not apply here; this is just a future-edit sketch.

1. Introduction first paragraph:
   `... L-systems, iterated function systems, diffusion-limited aggregation, and space-colonization algorithms~\cite{lindenmayer1968lsystemsI,lindenmayer1968lsystemsII,prusinkiewicz1990abop,barnsley1988fractalsEverywhere,runions2007spacecolonization,witten1981dla}.`

2. Procedural Related Work:
   add one sentence after the current L-system sentence:
   `Classic procedural tree systems also exposed compact rule parameters for renderable trees~\cite{weber1995realisticTrees}.`

3. 3D Generation Related Work:
   append:
   `Recent textured asset generators further emphasize PBR materials, mesh extraction, and UV/texture refinement as practical output criteria~\cite{assetgen2024,dreamgaussian2023,hunyuan3d2025}.`

4. Metrics subsection:
   append:
   `For branching and porous growth, we report topology and morphology descriptors while treating fractal dimension only as a descriptive statistic because finite branching structures can violate the assumptions behind standard fractal estimators~\cite{cheeseman2022fractalCaution,raumonen2013treeModels,martinez2018minkowskiPorosity}.`

## Source Links Checked

- TRELLIS.2 arXiv: https://arxiv.org/abs/2512.14692
- TRELLIS.2 project: https://microsoft.github.io/TRELLIS.2/
- NANO3D arXiv: https://arxiv.org/abs/2510.15019
- NANO3D project: https://jamesyjl.github.io/Nano3D
- InpaintSLat project/arXiv pointer: https://robot0321.github.io/InpaintSLat/index.html
- Space colonization paper page: https://algorithmicbotany.org/papers/colonization.egwnp2007.html
- Algorithmic Beauty of Plants Springer page: https://link.springer.com/book/10.1007/978-1-4613-8476-2
- Witten and Sander DLA DOI page: https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.47.1400
- Weber and Penn SIGGRAPH metadata: https://dl.acm.org/doi/10.1145/218380.218427
- Meta 3D AssetGen arXiv: https://arxiv.org/abs/2407.02445
- DreamGaussian arXiv: https://arxiv.org/abs/2309.16653
- Objaverse-XL arXiv: https://arxiv.org/abs/2307.05663
- SK-Adapter arXiv: https://arxiv.org/abs/2603.14152
- Points-to-3D arXiv: https://arxiv.org/abs/2603.18782
- Tree/QSM metrics paper: https://www.mdpi.com/2072-4292/5/2/491
- Fractal dimension caution paper: https://www.mdpi.com/2227-7390/10/5/839
- Fractal morphology survey: https://www.mdpi.com/2504-3110/8/8/440
- Minkowski functionals / connected porosity paper: https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2018.00055/full
