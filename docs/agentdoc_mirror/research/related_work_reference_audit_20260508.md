# Related Work Reference Audit - 2026-05-08

Scope: audited `paper_siga/references.bib` against citations used in `paper_siga/main.tex` Introduction and Related Work. I did not edit `main.tex` or `references.bib`.

Sources checked: arXiv metadata/API, CrossRef, DBLP/CVF where applicable, official project pages, official GitHub/model cards, Springer, Eurographics Digital Library, APS/DOI pages. I avoided downloading large PDFs.

## Citation Coverage

All bib keys currently used in Introduction/Related Work are present in `references.bib`:

`prusinkiewicz1990abop`, `runions2007spacecolonization`, `witten1981dla`, `trellis2024`, `trellis2project`, `stableDiffusion3`, `shapE2023`, `objaverse2023`, `sdeedit2021`, `flowedit2024`, `nano3d2025`, `voxhammer2025`, `latte3d2025`, `inpaintslat2025`, `infinigen2023`, `citydreamer2023`, `scenedreamer2023`, `trellisworld2025`.

## High-Level Risks

- `trellis2project` is the largest metadata risk. TRELLIS.2 now has a formal arXiv/tech-report citation, arXiv:2512.14692, titled "Native and Compact Structured Latents for 3D Generation"; the current bib entry is a project-page placeholder with incomplete title/authors.
- `inpaintslat2025` is confirmed but the key is misleading: the paper is arXiv:2605.00664 and was published on arXiv in 2026. Keep the citation if needed, but consider renaming the key or at least correcting the year consistency.
- Several recent editing/world papers are confirmed arXiv preprints but not peer-reviewed as of this audit: NANO3D, VoxHammer, 3D-LATTE, InpaintSLat, TRELLISWorld, and TRELLIS.2. They are acceptable for a fast-moving SIGGRAPH/3D generation related-work draft, but should be described as recent/preprint/project work rather than established venues unless later venue data appears.
- `stableDiffusion3` is a paper citation for SD3/MMDiT. If the manuscript explicitly claims SD3.5, add an official SD3.5 model-card/blog citation; arXiv:2403.03206 is still the technical paper linked by Stability for SD3/SD3.5 model cards.

## Per-Key Audit

| Bib key | Confidence | Correct source identifiers | Relationship to our work | Recommendation |
|---|---|---|---|---|
| `prusinkiewicz1990abop` | confirmed | DOI: [10.1007/978-1-4613-8476-2](https://doi.org/10.1007/978-1-4613-8476-2); Springer page: <https://link.springer.com/book/10.1007/978-1-4613-8476-2> | Canonical L-system/procedural plant modeling foundation for recursive symbolic growth and self-similar structures. | Keep. Add DOI/ISBN/publisher fields if polishing bib. |
| `runions2007spacecolonization` | confirmed | DOI: [10.2312/NPH/NPH07/063-070](https://doi.org/10.2312/NPH/NPH07/063-070); Eurographics DL: <https://diglib.eg.org/items/b5d756ee-0ab3-436e-a5cb-617d50df78fb> | Direct basis for occupancy/attractor competition growth and tree/root branching baselines. | Keep. Change entry type to `@inproceedings`; add DOI, pages 63-70, ISBN/ISSN if desired. |
| `witten1981dla` | confirmed | DOI: [10.1103/PhysRevLett.47.1400](https://doi.org/10.1103/PhysRevLett.47.1400) | Foundational stochastic attachment model for porous/coral/crystal-like frontier accretion. | Keep. Add DOI and URL. |
| `infinigen2023` | confirmed | arXiv: [2306.09310](https://arxiv.org/abs/2306.09310); DOI: [10.1109/CVPR52729.2023.01215](https://doi.org/10.1109/CVPR52729.2023.01215); project: <https://infinigen.org> | Procedural world-generation reference showing high-coverage hand-designed rules and compositional assets/scenes. | Keep. Update from `@misc` to CVPR `@inproceedings` metadata. |
| `citydreamer2023` | confirmed | arXiv: [2309.00610](https://arxiv.org/abs/2309.00610); DOI: [10.1109/CVPR52733.2024.00923](https://doi.org/10.1109/CVPR52733.2024.00923); project: <https://haozhexie.com/project/city-dreamer> | Unbounded city generation via compositional neural fields; useful contrast to finite recursive assets. | Keep. Update year/venue to CVPR 2024 in bib if using publication metadata. |
| `scenedreamer2023` | confirmed | arXiv: [2302.01330](https://arxiv.org/abs/2302.01330); DOI: [10.1109/TPAMI.2023.3321857](https://doi.org/10.1109/TPAMI.2023.3321857); project: <https://scene-dreamer.github.io/> | Unbounded 3D scene generation from 2D collections; supports world-scale comparison but not asset-recursive latent editing. | Keep. Current `@misc` should be replaced by TPAMI article metadata. |
| `nano3d2025` | confirmed | arXiv: [2510.15019](https://arxiv.org/abs/2510.15019); project: <https://jamesyjl.github.io/Nano3D> | Training-free 3D object editing without masks; uses TRELLIS/FlowEdit-style localized editing and merging, a close baseline/contrast. | Keep, but mark as arXiv preprint unless venue appears. |
| `voxhammer2025` | confirmed | arXiv: [2508.19247](https://arxiv.org/abs/2508.19247); project: <https://huanngzh.github.io/VoxHammer-Page/> | Training-free native 3D-space editing; closest in spirit to preserving unedited 3D regions while editing local areas. | Keep, but mark as arXiv preprint unless venue appears. |
| `latte3d2025` | confirmed | arXiv: [2509.00269](https://arxiv.org/abs/2509.00269); project: <https://mparelli.github.io/3d-latte> | Training-free latent-space 3D editing from textual instructions; relevant as a native 3D latent editing baseline, but single-edit rather than recursive. | Keep, but mark as arXiv preprint unless venue appears. |
| `inpaintslat2025` | confirmed | arXiv: [2605.00664](https://arxiv.org/abs/2605.00664); project: <https://robot0321.github.io/InpaintSLat/index.html> | Training-free inpainting in structured 3D latents via initial-noise optimization; relevant to masked local naturalization/completion. | Keep if discussing latest 3D latent inpainting. Rename key to `inpaintslat2026` or fix year consistency. |
| `trellisworld2025` | confirmed | arXiv: [2510.23880](https://arxiv.org/abs/2510.23880); HF paper page: <https://huggingface.co/papers/2510.23880> | Training-free scene/world construction by reusing object generators as modular tile generators. Good contrast to finite recursive assets. | Keep, but mark as arXiv preprint. |
| `flowedit2024` | confirmed | arXiv: [2412.08629](https://arxiv.org/abs/2412.08629); DOI: [10.1109/ICCV51701.2025.01834](https://doi.org/10.1109/ICCV51701.2025.01834); project: <https://matankleiner.github.io/flowedit/> | 2D flow-model editing reference motivating inversion-free/training-free flow reuse; indirectly relevant to 3D latent editing systems. | Keep. Update venue to ICCV 2025 if using publication metadata. |
| `trellis2024` | confirmed | arXiv: [2412.01506](https://arxiv.org/abs/2412.01506); DOI: [10.1109/CVPR52734.2025.02000](https://doi.org/10.1109/CVPR52734.2025.02000); official GitHub/project: <https://github.com/Microsoft/TRELLIS> | Core sparse structured latent representation (SLAT), mesh/3D generation, local editing capabilities; foundational for our sparse-latent grammar state. | Keep. Update venue to CVPR 2025 and add DOI. |
| `trellis2project` | confirmed source exists, current bib metadata likely placeholder | arXiv: [2512.14692](https://arxiv.org/abs/2512.14692); official project: <https://microsoft.github.io/TRELLIS.2/>; official GitHub: <https://github.com/microsoft/TRELLIS.2> | Direct model basis in this draft: O-Voxel, compact structured latents, high-res PBR image-to-3D generation, mesh-to-O-Voxel conversion. | Replace current placeholder with formal tech-report/arXiv entry. Use title "Native and Compact Structured Latents for 3D Generation" and authors Xiang, Chen, Xu, Wang, Lv, Deng, Zhu, Dong, Zhao, Yuan, Yang. |
| `stableDiffusion3` | confirmed | arXiv: [2403.03206](https://arxiv.org/abs/2403.03206); SD3 Medium model card: <https://huggingface.co/stabilityai/stable-diffusion-3-medium>; SD3.5 Large model card: <https://huggingface.co/stabilityai/stable-diffusion-3.5-large>; SD3.5 blog: <https://stability.ai/news-updates/introducing-stable-diffusion-3-5> | Text/image prior and rectified-flow transformer background; relevant because TRELLIS/FlowEdit ecosystems use flow-transformer ideas and image-conditioned priors. | Keep for SD3. If manuscript says SD3.5 explicitly, add model card/blog citation as a separate non-paper source. |
| `shapE2023` | confirmed | arXiv: [2305.02463](https://arxiv.org/abs/2305.02463); official GitHub: <https://github.com/openai/shap-e> | Earlier text/image-conditioned 3D implicit function generator; good baseline for one-shot 3D asset generation before sparse-latent models. | Keep. No DOI found; arXiv/GitHub are appropriate. |
| `objaverse2023` | confirmed | arXiv: [2212.08051](https://arxiv.org/abs/2212.08051); DOI: [10.1109/CVPR52729.2023.01263](https://doi.org/10.1109/CVPR52729.2023.01263); project: <https://objaverse.allenai.org/> | Dataset-scale reference explaining why learned object-level 3D asset distributions became possible. | Keep. Add arXiv and DOI. Consider also citing Objaverse-XL if discussing TRELLIS/TRELLIS.2 training data specifically. |
| `sdeedit2021` | confirmed | arXiv: [2108.01073](https://arxiv.org/abs/2108.01073); OpenReview: <https://openreview.net/forum?id=aBsCjcPu_tE>; project: <https://sde-image-editing.github.io/> | Foundational noising-denoising image editing method; supports the contrast between partial resampling and scaffold preservation. | Keep. Current `@inproceedings` ICLR 2022 is appropriate; add arXiv/OpenReview URL. |

## Suggested Replacement Metadata For Highest-Risk Entries

### `trellis2project`

Current entry should be replaced or upgraded:

```bibtex
@misc{trellis2project,
  title={Native and Compact Structured Latents for 3D Generation},
  author={Xiang, Jianfeng and Chen, Xiaoxue and Xu, Sicheng and Wang, Ruicheng and Lv, Zelong and Deng, Yu and Zhu, Hongyuan and Dong, Yue and Zhao, Hao and Yuan, Nicholas Jing and Yang, Jiaolong},
  year={2025},
  eprint={2512.14692},
  archivePrefix={arXiv},
  primaryClass={cs.CV},
  url={https://microsoft.github.io/TRELLIS.2/}
}
```

### `inpaintslat2025`

The content is real, but the key/year should be made consistent:

```bibtex
@misc{inpaintslat2026,
  title={InpaintSLat: Inpainting Structured 3D Latents via Initial Noise Optimization},
  author={Chung, Jaeyoung and Lee, Suyoung and Lee, Kyoung Mu},
  year={2026},
  eprint={2605.00664},
  archivePrefix={arXiv},
  primaryClass={cs.CV},
  url={https://robot0321.github.io/InpaintSLat/index.html}
}
```

If preserving cite-key stability is more important than naming consistency, keep the key `inpaintslat2025` but correct/retain `year={2026}` and add the URL.

## Related-Work Positioning Notes

- Procedural foundations (`prusinkiewicz1990abop`, `runions2007spacecolonization`, `witten1981dla`) are strong and should stay. The relationship is structural control, not learned asset realism.
- Learned 3D generation references (`objaverse2023`, `shapE2023`, `trellis2024`, `trellis2project`) are well aligned. TRELLIS/TRELLIS.2 should be emphasized over Shap-E because the method operates over sparse structured latents/O-Voxel-like states.
- Training-free editing references are relevant but should not be overstated as recursive-generation methods. Their main role is to show frozen generators can be reused for local edits/inpainting; our distinction is repeated grammar application with projection-stabilized recursion.
- World/unbounded-scene references (`infinigen2023`, `citydreamer2023`, `scenedreamer2023`, `trellisworld2025`) should remain as contrastive motivation. The paper should continue to state that our scope is finite-depth recursive assets rather than unbounded scene/world synthesis.
