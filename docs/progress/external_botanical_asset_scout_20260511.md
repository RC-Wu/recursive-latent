# External Botanical Asset Scout - 2026-05-11

Scope: license-compatible public-domain, CC0, and CC-BY botanical assets for the current three-track R-SLG plan. I did not modify code or launch remote jobs. I avoided assets that were marked AI-generated/NoAI where visible in source metadata; still re-check the source page at download time because Sketchfab/Fab metadata can change.

## Best Picks

1. **Best direct fern mesh:** [CC0 Old World Forked Fern, D. linearis](https://sketchfab.com/3d-models/cc0-old-world-forked-fern-d-linearis-cff6433937b748be82ea571afe536739)
   - License: CC0 Public Domain.
   - Attribution: not required; credit `ffish.asia / floraZia.com` if convenient.
   - Mesh: 422.6k triangles / 211.2k vertices.
   - Use: direct mesh after decimation; also useful as a TRELLIS2 depth-0 encode/decode quality probe.
   - Fit: fern/frond track. Better direct mesh than image seed because it already has fern geometry, but too heavy for deep recursion without simplification.

2. **Best direct spider-plant mesh:** [Spider Plant by sauti](https://sketchfab.com/3d-models/spider-plant-e21199e3cb874bc2be8a13588813f9f5)
   - License: CC Attribution.
   - Attribution: required. Suggested note: `"Spider Plant" by sauti, Sketchfab, CC BY.`
   - Mesh: 9.2k triangles / 5.9k vertices.
   - Use: direct mesh and rosette/runner semantics reference.
   - Fit: spider plant track. Best manageable direct mesh, but keep it in an attribution-required lane separate from CC0/public-domain assets.

3. **Best root mesh:** [Root Structure by arloopa](https://sketchfab.com/3d-models/root-structure-c294d45510664ae790fba5767d03d9d2)
   - License: CC Attribution.
   - Attribution: required. Suggested note: `"Root Structure" by arloopa, Sketchfab, CC BY.`
   - Mesh: 40.5k triangles / 20.5k vertices.
   - Use: direct root mesh or root-shape grammar reference.
   - Fit: recursive-root/TRELLIS2 root track. Good triangle count for root-first testing, but less botanical-species-specific than aerial-root photos.

4. **Best CC0 aerial/root image seed:** [Rubber fig aerial roots](https://commons.wikimedia.org/wiki/File:Rubber_fig_(Ficus_elastica)_aerial_roots.jpg)
   - License: CC0 1.0.
   - Attribution: not required; optional credit `David E Mead`.
   - Image: 4171 x 3128.
   - Use: TRELLIS2 image-to-root generation; crop vertical dangling roots and trunk contact.
   - Fit: best for recursive/aerial-root generation, not direct mesh use.

5. **Best CC0 fiddlehead image seed:** [Fiddlehead-ferns.jpg](https://commons.wikimedia.org/wiki/File:Fiddlehead-ferns.jpg)
   - License: CC0 1.0.
   - Attribution: not required; optional credit `Janhatesmarcia`.
   - Image: 1024 x 680.
   - Use: TRELLIS2 image seed for crozier/fiddlehead shape; crop one curled tip if the generator collapses the cluster.
   - Fit: best clean CC0 crozier seed.

## Candidate Table

| Asset | Exact URL | License | Attribution | Best Use | Notes |
|---|---|---|---|---|---|
| Old World Forked Fern mesh | https://sketchfab.com/3d-models/cc0-old-world-forked-fern-d-linearis-cff6433937b748be82ea571afe536739 | CC0 | None required | Direct mesh | Strong fern geometry; decimate before recursion. |
| Japanese Rockcap Fern mesh | https://sketchfab.com/3d-models/cc0-japanese-rockcap-fern-ddbce6470cde4d31b1589fece79b60c3 | CC0 | None required | Direct mesh after heavy simplification | 1.1M tris / 528.3k verts; too heavy raw, good high-quality reference. |
| Spider Plant mesh | https://sketchfab.com/3d-models/spider-plant-e21199e3cb874bc2be8a13588813f9f5 | CC BY | Credit sauti | Direct mesh | Light, semantically on target; attribution lane. |
| Root Structure mesh | https://sketchfab.com/3d-models/root-structure-c294d45510664ae790fba5767d03d9d2 | CC BY | Credit arloopa | Direct mesh / root grammar reference | Good size for root-first testing. |
| Kenney Nature Kit | https://kenney.nl/assets/nature-kit | CC0 | None required, credit appreciated | Low-poly fallback direct meshes | Not botanically detailed; useful only as fallback props or simple GLB pipeline checks. |
| Eclair GLB Nature Kit redistribution | https://eclair-assets.itch.io/nature-kit-glb-pack-329-free-cc0-3d-models | CC0 source redistribution | None required; credit Kenney/Eclair optional | GLB fallback | Convenient GLB packaging of Kenney CC0 Nature Kit; page notes AI-assisted packaging text, not AI-generated models. |
| Chlorophytum botanical illustration | https://commons.wikimedia.org/wiki/File:Chlorophytum_comosum.png | Public Domain Mark / PD-old | None required | TRELLIS2 guide image | Clean spider-plant form guide; low resolution but excellent silhouette. |
| Root-bound spider plant | https://commons.wikimedia.org/wiki/File:Root-bound_Chlorophytum_comosum.jpg | CC BY 2.0 | Credit Keith Williamson | TRELLIS2 root seed | Good exposed spider-plant root mass; attribution required. |
| Spider Plant photo | https://commons.wikimedia.org/wiki/File:Spider_Plant_(Chlorophytum_comosum).jpg | CC BY-SA 3.0 | Credit Mokkie; ShareAlike applies to derivatives | Reference only | Useful visual rosette/leaf guide, but ShareAlike makes it less attractive for generated assets. |
| Fiddlehead-ferns | https://commons.wikimedia.org/wiki/File:Fiddlehead-ferns.jpg | CC0 | None required | TRELLIS2 crozier seed | Best CC0 fiddlehead option found. |
| Golden spiral fiddlehead | https://commons.wikimedia.org/wiki/File:Golden_spiral_in_a_fiddlehead_fern.jpg | CC BY 4.0 | Credit Albarubescens | TRELLIS2 crozier/spiral guide | Strong spiral semantics; attribution required. |
| Koru Unfurling | https://commons.wikimedia.org/wiki/File:Koru_Unfurling.JPG | CC BY 2.5 or CC BY-SA 3.0 or GFDL | Credit Jon Radoff; choose CC BY 2.5 to avoid ShareAlike | TRELLIS2 crozier guide | Good macro curl; attribution required. |
| New Fern fronds | https://commons.wikimedia.org/wiki/File:New_Fern_fronds_(3672804706).jpg | CC BY 2.0 | Credit Tony Hisgett | TRELLIS2 fern-frond guide | Good clustered new fronds and pinnae guide. |
| Tree Aerial Prop Roots | https://www.publicdomainpictures.net/en/view-image.php?image=151005&picture=tree-aerial-prop-roots | CC0 Public Domain | None required; optional credit RAJESH misra | TRELLIS2 aerial/root seed | Strong dangling-root/trunk contact seed; use free 1276 x 1920 download or paid full-res if needed. |
| Beech Aerial Roots | https://commons.wikimedia.org/wiki/File:Beech_Aerial_Roots.JPG | Public domain release | None required; optional credit Roger Griffith / Rosser1954 | TRELLIS2 root texture/attachment guide | Smaller but clean root-on-trunk structure. |
| Rubber fig aerial roots | https://commons.wikimedia.org/wiki/File:Rubber_fig_(Ficus_elastica)_aerial_roots.jpg | CC0 | None required; optional credit David E Mead | TRELLIS2 aerial/root seed | Best clean CC0 aerial-root photo. |
| Root Systems diagram | https://commons.wikimedia.org/wiki/File:Root_Systems.svg | CC BY-SA 4.0 | Credit KaitlinLiu; ShareAlike applies | Reference only | Useful taproot/fibrous topology guide, but not ideal as a generative input due to ShareAlike. |
| Leaf morphology diagram | https://commons.wikimedia.org/wiki/File:Leaf_morphology_no_title.svg | CC BY-SA 3.0 / GFDL | Credit Debivort/McSush; ShareAlike/GFDL | Reference only | Clean leaf-shape taxonomy, not recommended as TRELLIS2 seed. |

## TRELLIS2 vs Direct Mesh Ranking

**Use for TRELLIS2 root generation first:**

1. `Rubber fig aerial roots` - CC0, high resolution, best dangling/aerial root structure.
2. `Tree Aerial Prop Roots` - CC0, strong old-tree hanging-root semantics.
3. `Fiddlehead-ferns.jpg` - CC0, best clean crozier seed.
4. `Chlorophytum_comosum.png` - public domain, clean spider-plant silhouette.
5. `Root-bound Chlorophytum comosum.jpg` - CC BY, best exposed spider-plant root mass.
6. `Golden spiral in a fiddlehead fern.jpg` / `Koru Unfurling.JPG` - attribution-required but strong spiral guides.

**Use as direct meshes first:**

1. `Spider Plant by sauti` - light and semantically exact; attribution required.
2. `Root Structure by arloopa` - good root mesh size; attribution required.
3. `Old World Forked Fern` - best CC0 fern mesh, but decimate.
4. `Japanese Rockcap Fern` - CC0 and detailed, but heavy enough that it should be a reference or simplified mesh, not raw recursion input.
5. `Kenney/Eclair Nature Kit` - CC0 fallback only; likely too low-poly/generic for publication botanical claims.

## Recommendation for the Three-Track Plan

- **Track B spider plant:** run two lanes: `sauti` direct mesh as an attribution-required direct baseline, and `Chlorophytum_comosum.png` plus `Root-bound Chlorophytum comosum.jpg` as TRELLIS2 image seeds for root/rosette generation.
- **Track B fern/crozier:** use `Fiddlehead-ferns.jpg` as the clean CC0 seed; add `Golden spiral` or `Koru Unfurling` if attribution is acceptable. Use `Old World Forked Fern` as the direct-mesh fern baseline after decimation.
- **Recursive/aerial roots:** prioritize `Rubber fig aerial roots` and `Tree Aerial Prop Roots` for TRELLIS2 root generation. Use `Root Structure by arloopa` only if a direct mesh root is needed quickly and CC BY attribution is acceptable.
- **Clean guide images:** keep ShareAlike/GFDL diagrams (`Root Systems.svg`, `Leaf morphology`) as human/grammar design references, not as generated-input sources for final assets.

## License Cautions

- CC BY assets are compatible if the paper/project records title, author, source URL, license URL, and modification notice.
- CC BY-SA/GFDL assets are technically free but create ShareAlike/GFDL obligations; avoid them for final generated-input assets unless the downstream licensing plan is explicit.
- Sketchfab pages did not show NoAI tags in the crawled metadata for the selected `sauti`, `arloopa`, or `ffish/floraZia` models, but re-check before download because platform metadata can change.
