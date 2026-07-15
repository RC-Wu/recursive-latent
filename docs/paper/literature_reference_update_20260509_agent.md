# Literature Reference Update for Recursive 3D Generative Growth / PS-RSLG

Date: 2026-05-09  
Scope: quick source check for Introduction / Related Work / Preliminaries. Primary sources preferred: ACM TOG/CGF, CVPR/ICCV/ICLR, arXiv/project pages where no proceedings version was found. I did not modify `main.tex` or `references.bib`.

## 1. Procedural Recursive Modeling

| Suggested key | Exact title | Venue / year | Why cite | Source |
|---|---|---:|---|---|
| `lindenmayer1968lsystemsI` | Mathematical Models for Cellular Interactions in Development I. Filaments with One-Sided Inputs | Journal of Theoretical Biology, 1968 | Foundational L-system formalism for rewriting-based growth and recursive production rules. | DOI in existing bib |
| `prusinkiewicz1990abop` | The Algorithmic Beauty of Plants | Springer, 1990 | Canonical bridge from L-systems to plant/branching morphology; useful in preliminaries for grammar-like growth. | DOI in existing bib |
| `hutchinson1981fractals` | Fractals and Self Similarity | Indiana University Mathematics Journal, 1981 | More precise mathematical source for IFS than a general textbook; cite when discussing contractive maps/self-similar recursive sets. | https://doi.org/10.1512/iumj.1981.30.30055 |
| `barnsley1988fractalsEverywhere` | Fractals Everywhere | Academic Press, 1988 | Standard IFS/fractal reference; cite for accessible fractal modeling context rather than new algorithmic contribution. | existing bib |
| `witten1981dla` | Diffusion-Limited Aggregation, a Kinetic Critical Phenomenon | Physical Review Letters, 1981 | Foundation for particle-attachment growth and dendritic/porous aggregates; supports contrast with deterministic grammar growth. | existing bib |
| `sander2000dlaReview` | Diffusion-Limited Aggregation: A Kinetic Critical Phenomenon? | Contemporary Physics, 2000 | Review-style DLA reference for related work if space permits. | existing bib |
| `runions2007spacecolonization` | Modeling Trees with a Space Colonization Algorithm | Eurographics Workshop on Natural Phenomena, 2007 | Direct precedent for attraction-point-driven recursive tree growth. | https://doi.org/10.2312/NPH/NPH07/063-070 |
| `stiny1972shapegrammars` | Shape Grammars and the Generative Specification of Painting and Sculpture | Information Processing 71, 1972 | Foundational shape grammar reference for rule-based geometry generation. | existing bib |
| `mueller2006procedural` | Procedural Modeling of Buildings | ACM Transactions on Graphics, 2006 | CGA/procedural building modeling; useful contrast between hand-designed rules and learned 3D generation. | https://doi.org/10.1145/1141911.1141931 |
| `smelik2014survey` | A Survey on Procedural Modelling for Virtual Worlds | Computer Graphics Forum, 2014 | Compact survey covering procedural modeling methods, controllability, and virtual-world composition. | https://doi.org/10.1111/cgf.12276 |

Recommended missing BibTeX:

```bibtex
@article{hutchinson1981fractals,
  title={Fractals and Self Similarity},
  author={Hutchinson, John E.},
  journal={Indiana University Mathematics Journal},
  volume={30},
  number={5},
  pages={713--747},
  year={1981},
  doi={10.1512/iumj.1981.30.30055}
}

@article{smelik2014survey,
  title={A Survey on Procedural Modelling for Virtual Worlds},
  author={Smelik, Ruben M. and Tutenel, Tim and Bidarra, Rafael and Benes, Bedrich},
  journal={Computer Graphics Forum},
  volume={33},
  number={6},
  pages={31--50},
  year={2014},
  doi={10.1111/cgf.12276}
}
```

## 2. Modern 3D Generation

| Suggested key | Exact title | Venue / year | Why cite | Source |
|---|---|---:|---|---|
| `objaverse2023` | Objaverse: A Universe of Annotated 3D Objects | CVPR, 2023 | Dataset-scale reference for text/metadata-paired 3D object corpora; CVF page reports pp. 13142-13153. | https://openaccess.thecvf.com/content/CVPR2023/html/Deitke_Objaverse_A_Universe_of_Annotated_3D_Objects_CVPR_2023_paper.html |
| `objaverseXL2023` | Objaverse-XL: A Universe of 10M+ 3D Objects | NeurIPS Datasets and Benchmarks, 2023 | Larger web-scale 3D dataset; cite if discussing scale beyond Objaverse 1.0. | https://arxiv.org/abs/2307.05663 |
| `shape2vecset2023` | 3DShape2VecSet: A 3D Shape Representation for Neural Fields and Generative Diffusion Models | ACM Transactions on Graphics, 2023 | Strong representation baseline for neural fields and 3D diffusion. | https://doi.org/10.1145/3592442 |
| `shapE2023` | Shap-E: Generating Conditional 3D Implicit Functions | arXiv, 2023 | Early OpenAI conditional 3D implicit-function generator; useful for pre-SLAT 3D generative model lineage. | https://arxiv.org/abs/2305.02463 |
| `dreamgaussian2023` | DreamGaussian: Generative Gaussian Splatting for Efficient 3D Content Creation | ICLR, 2024 | Fast optimization-based text/image-to-3D via Gaussian splatting; cite as efficient SDS/3DGS-era generator. | https://openreview.net/forum?id=UyNXMqnN3c |
| `trellis2024` | Structured 3D Latents for Scalable and Versatile 3D Generation | CVPR Highlight, 2025; arXiv 2024 | Native structured 3D latent model; central modern baseline for SLAT-style generation. | https://microsoft.github.io/TRELLIS/ |
| `trellis2project` | Native and Compact Structured Latents for 3D Generation | Tech report / arXiv, 2025 | TRELLIS.2 follow-up: O-Voxel, PBR attributes, compact sparse compression VAE; cite as very recent preprint/tech report. | https://arxiv.org/abs/2512.14692 |
| `assetgen2024` | Meta 3D AssetGen: Text-to-Mesh Generation with High-Quality Geometry, Texture, and PBR Materials | arXiv, 2024 | Production-oriented text-to-mesh asset generation with geometry, texture, and PBR material maps. | https://arxiv.org/abs/2407.02445 |
| `hunyuan3d2025` | Hunyuan3D 2.0: Scaling Diffusion Models for High Resolution Textured 3D Assets Generation | arXiv, 2025 | Two-stage shape/texture open-source 3D asset generator; relevant to high-resolution textured asset claims. | https://arxiv.org/abs/2501.12202 |

Recommended BibTeX revisions/additions:

```bibtex
@inproceedings{dreamgaussian2024,
  title={DreamGaussian: Generative Gaussian Splatting for Efficient 3D Content Creation},
  author={Tang, Jiaxiang and Ren, Jiawei and Zhou, Hang and Liu, Ziwei and Zeng, Gang},
  booktitle={International Conference on Learning Representations},
  year={2024},
  url={https://openreview.net/forum?id=UyNXMqnN3c}
}

@inproceedings{trellis2025,
  title={Structured 3D Latents for Scalable and Versatile 3D Generation},
  author={Xiang, Jianfeng and Lv, Zelong and Xu, Sicheng and Deng, Yu and Wang, Ruicheng and Zhang, Bowen and Chen, Dong and Tong, Xin and Yang, Jiaolong},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  year={2025},
  note={CVPR Highlight},
  eprint={2412.01506},
  archivePrefix={arXiv},
  primaryClass={cs.CV},
  url={https://microsoft.github.io/TRELLIS/}
}
```

## 3. Editing and Control

| Suggested key | Exact title | Venue / year | Why cite | Source |
|---|---|---:|---|---|
| `sdeedit2021` | SDEdit: Guided Image Synthesis and Editing with Stochastic Differential Equations | ICLR, 2022 | Foundational image editing by noising plus reverse SDE; useful analogy for stochastic partial regeneration. | https://sde-image-editing.github.io/ |
| `flowedit2025` | FlowEdit: Inversion-Free Text-Based Editing Using Pre-Trained Flow Models | ICCV, 2025 | Modern flow-model text editing without inversion/optimization; relevant if PS-RSLG discusses prompt-preserving edits. | https://openaccess.thecvf.com/content/ICCV2025/html/Kulikov_FlowEdit_Inversion-Free_Text-Based_Editing_Using_Pre-Trained_Flow_Models_ICCV_2025_paper.html |
| `skadapter2026` | SK-Adapter: Skeleton-Based Structural Control for Native 3D Generation | arXiv, 2026 | Native 3D structural control using skeleton coordinates/topology; very relevant but very recent/unreviewed. | https://arxiv.org/abs/2603.14152 |
| `pointsTo3D2026` | Points-to-3D: Structure-Aware 3D Generation with Point Cloud Priors | arXiv, 2026 | Structure-aware control using point-cloud priors; recent/unreviewed. | https://arxiv.org/abs/2603.18782 |
| `latte3d2025` | 3D-LATTE: Latent Space 3D Editing from Textual Instructions | arXiv, 2025 | Native/latent 3D editing direction; cite cautiously pending venue. | https://arxiv.org/abs/2509.00269 |
| `voxhammer2025` | VoxHammer: Training-Free Precise and Coherent 3D Editing in Native 3D Space | arXiv, 2025 | Training-free native 3D-space editing; useful if arguing local edits remain hard. | https://arxiv.org/abs/2508.19247 |
| `inpaintslat2026` | InpaintSLat: Inpainting Structured 3D Latents via Initial Noise Optimization | arXiv, 2026 | TRELLIS/SLAT-adjacent inpainting; promising but should be labeled preprint. | https://arxiv.org/abs/2605.00664 |

Recommended BibTeX revision for FlowEdit:

```bibtex
@inproceedings{flowedit2025,
  title={FlowEdit: Inversion-Free Text-Based Editing Using Pre-Trained Flow Models},
  author={Kulikov, Vladimir and Kleiner, Matan and Huberman-Spiegelglas, Inbar and Michaeli, Tomer},
  booktitle={Proceedings of the IEEE/CVF International Conference on Computer Vision},
  pages={19721--19730},
  year={2025}
}
```

## 4. Evaluation Metrics and Morphology

| Suggested key | Exact title | Venue / year | Why cite | Source |
|---|---|---:|---|---|
| `raumonen2013treeModels` | Fast Automatic Precision Tree Models from Terrestrial Laser Scanner Data | Remote Sensing, 2013 | QSM/cylinder-tree model source; supports topology, branch structure, branch-size distributions, volume, and reachability-like structural metrics. | https://doi.org/10.3390/rs5020491 |
| `martinez2018minkowskiPorosity` | Minkowski Functionals of Connected Soil Porosity as Indicators of Soil Tillage and Depth | Frontiers in Environmental Science, 2018 | Example of using Minkowski functionals for connected porous morphology; good precedent for volume/surface/connectivity-style metrics. | https://doi.org/10.3389/fenvs.2018.00055 |
| `cheeseman2022fractalCaution` | Estimating the Fractal Dimensions of Vascular Networks and Other Branching Structures: Some Words of Caution | Mathematics, 2022 | Useful cautionary citation: fractal dimension on branching structures can be unstable/misleading without scale and sampling discipline. | https://doi.org/10.3390/math10050839 |

Optional stronger morphology background if space allows:

```bibtex
@article{mecke1994minkowski,
  title={Robust Morphological Measures for Large-Scale Structure in the Universe},
  author={Mecke, Klaus R. and Buchert, Thomas and Wagner, Herbert},
  journal={Astronomy and Astrophysics},
  volume={288},
  pages={697--704},
  year={1994},
  eprint={astro-ph/9312028},
  archivePrefix={arXiv}
}
```

## Suspicious or Risky Entries in `paper_siga/references.bib`

These are not necessarily fake, but should be treated carefully before final camera-ready use.

| Existing key | Current issue | Suggested action |
|---|---|---|
| `flowedit2024` | Existing BibTeX lists arXiv/year 2024, but CVF now lists FlowEdit as ICCV 2025 with pages 19721-19730. | Replace with `@inproceedings{flowedit2025,...}` or keep key but update venue/year/pages. |
| `dreamgaussian2023` | Existing entry is arXiv-style, but OpenReview lists it as ICLR 2024 oral. | Prefer ICLR 2024 proceedings entry. |
| `trellis2024` | Existing entry is arXiv-style, but official project page says CVPR 2025 Highlight. | Prefer CVPR 2025 entry if citing as peer-reviewed baseline; keep arXiv ID. |
| `trellis2project` | arXiv ID `2512.14692` is valid and submitted 2025-12-16, but no peer-reviewed venue found; project page labels citation as `Tech report`. | Cite as arXiv/tech report, not as conference paper. |
| `inpaintslat2025` | Key says 2025 but entry year is 2026 and arXiv ID is `2605.00664`. It is current-month preprint relative to 2026-05-09. | Rename key to `inpaintslat2026`; cite only as very recent arXiv preprint. |
| `skadapter2026` | Valid-looking arXiv page found, submitted 2026-03-14; no venue. | Keep only if the paper needs current native-3D structural control evidence; mark preprint. |
| `pointsTo3D2026` | Valid-looking arXiv page found for `2603.18782`; no venue. | Keep only as current preprint, not as established baseline. |
| `nano3d2025`, `voxhammer2025`, `latte3d2025`, `trellisworld2025` | Searchable as recent/preprint-style entries, but no peer-reviewed venue confirmed in this quick pass. | Use sparingly in Related Work footnote/table, or omit unless needed for editing-control coverage. |
| `hunyuan3d2025` | Entry author is `Tencent Hunyuan3D Team`; arXiv page lists many named authors. | If formal bibliography quality matters, replace team author with arXiv author list or `Tencent Hunyuan3D Team` only if intentionally citing the technical report/model card style. |

## Short Placement Suggestions

- Introduction: cite `lindenmayer1968lsystemsI`, `prusinkiewicz1990abop`, `runions2007spacecolonization`, `smelik2014survey`, then contrast with `objaverse2023`, `shape2vecset2023`, `trellis2025`.
- Related Work / procedural generation: cite L-systems, IFS/fractals, DLA, shape grammars/CGA, and survey; avoid implying these methods solve modern learned 3D asset synthesis.
- Related Work / modern 3D generation: cite `Objaverse`, `3DShape2VecSet`, `Shap-E`, `DreamGaussian`, `TRELLIS`, `TRELLIS.2`, `AssetGen`, `Hunyuan3D 2.0`.
- Editing/control paragraph: cite `SDEdit` and `FlowEdit` for image/flow editing, then clearly label `SK-Adapter`, `Points-to-3D`, `3D-LATTE`, `VoxHammer`, `InpaintSLat` as recent 3D-control/editing preprints.
- Evaluation paragraph: cite QSM (`raumonen2013treeModels`) for tree topology/branch metrics, Minkowski functionals for porous morphology, and `cheeseman2022fractalCaution` to justify using fractal dimension only as a cautionary auxiliary statistic.
