# Root Candidate Scout for Botanical/Fern/Spider-Plant R-SLG Cases (2026-05-11)

Scope: local read-only scout plus this lightweight markdown note. I did not launch remote jobs and did not edit the main workflow.

Goal: identify high-quality local root meshes or conditioning references for pushing plant / fern / spider-plant recursive cases toward publication quality, with emphasis on a tree-crown-like grammar.

## Shortlist Verdict

Best immediate roots:

1. `V25_sc_tree_crown_leafshield_B`
   - Path: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/inputs/V25_sc_tree_crown_leafshield_B/V25_sc_tree_crown_leafshield_B.obj`
   - Why: strongest tree-crown-like procedural root. It uses space-colonization attractor competition, connected swept support, shared-vertex leaf/needle detail, and a leaf-shield variant intended to hide cut caps and improve local zoom.
   - Mesh size: about 37.6k vertices / 75.4k faces.

2. `V25_sc_tree_crown_tapered_B`
   - Path: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/inputs/V25_sc_tree_crown_tapered_B/V25_sc_tree_crown_tapered_B.obj`
   - Why: nearly as strong as leafshield_B, but more honest exposed crown topology. It is tuned for a denser canopy with slimmer exported tubes, good for showing recursive structure rather than just visual cover.
   - Mesh size: about 37.1k vertices / 74.3k faces.

3. `V25_lsys_root_fan_dense_anchorD_stable`
   - Path: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/inputs/V25_lsys_root_fan_dense_anchorD_stable/V25_lsys_root_fan_dense_anchorD_stable.obj`
   - Why: best light root-fan anchor. It has a depth-5 root L-system, dense attached rootlets, downward tropism, shared-vertex attachment, and explicit detached-island forbidding. Good base for spider plant or fern rhizome cases.
   - Mesh size: about 15.3k vertices / 29.6k faces.

4. `V22_lsys_climbing_vine_d6_smooth_leaf_tendrils`
   - Path: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_cases_V22_botanical_smooth_20260510_dryrun/V22_lsys_climbing_vine_d6_smooth_leaf_tendrils/V22_lsys_climbing_vine_d6_smooth_leaf_tendrils.obj`
   - Why: best compact vine/runner root. It is only about 6.2k vertices and already encodes connected curl, tendrils, and leaves. Good grammar bridge from existing vine success to hanging spider-plant runners.
   - Mesh size: about 6.2k vertices / 13.0k faces.

5. `V24_sc_root_network_260_anchorA_seedA`
   - Path: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_visual_matched_texture_V24_priority_rerun_seed20260511_20260510_remote/inputs/V24_sc_root_network_260_anchorA_seedA/V24_sc_root_network_260_anchorA_seedA.obj`
   - Why: strongest rerun root-network candidate with QA priority `root_quality`; metadata says the previous V23 root network was not main-text safe, making this the intended improved replacement. Good for below-ground/root-web or rhizome-like fern cases.
   - Mesh size: about 38.1k vertices / 75.9k faces.

## Candidate Inventory

| Rank | Candidate | Asset type | Provenance | Suitability |
|---:|---|---|---|---|
| 1 | `V25_sc_tree_crown_leafshield_B` | OBJ mesh | Generated local mirror of remote V25 root/SC refine inputs; source `space_colonization_baseline.grow_space_colonization`; connectivity gate LCR >= 0.999; shared-vertex leaf/needle attachments. | Best for tree-crown-like grammar. Leaf shield hides caps and gives publishable botanical silhouette. Risk: leaf shield can mask underlying recursive topology if used alone. |
| 2 | `V25_sc_tree_crown_tapered_B` | OBJ mesh | Same V25 refine batch; SC attractor competition, 900 attractors, 874 covered, tapered connected support. | Best structural crown root. Slightly less visually forgiving than leafshield_B, but better for demonstrating grammar. |
| 3 | `V25_lsys_root_fan_dense_anchorD_stable` | OBJ mesh | V25 root refine; source `baseline_matrix_20260509.lsystem_case(root)`; depth-5 root fan, 490 rootlets, negative-z tropism. | Best lightweight spider/fern root/rhizome base. Dense but not huge. Risk: visually more root than leaf/crown unless paired with rosette/frond grammar. |
| 4 | `V22_lsys_climbing_vine_d6_smooth_leaf_tendrils` | OBJ mesh | V22 smooth botanical dryrun; hand-authored L-system vine equivalent to baseline matrix vine; connected support, 96 leaves, 70 tendrils. | Best hanging-runner / spider-plant stolon candidate. Very light, easy to iterate. Risk: existing vine lineage may read as vine rather than spider plant unless rosette leaves are added. |
| 5 | `V24_sc_root_network_260_anchorA_seedA` | OBJ mesh | V24 priority rerun; SC root network; QA priority `root_quality`; rerun reason says it replaces not-main-text-safe V23 root network. | Best root-network rerun. Good for rhizome/web roots and path-to-root metrics. Risk: below-ground semantics, not crown-like by itself. |
| 6 | `V22_sc_root_network_parameter_sweep_dense_smooth_rootlets` | OBJ mesh | V22 smooth botanical; dense SC root-network parameter sweep, 1250 attractors, 1194 covered, 220 rootlets. | Very detailed root web. Good for fern rhizome/root mat. Risk: 54k vertices, denser than needed for a root seed and may burden Trellis/local checks. |
| 7 | `V22_sc_tree_crown_260_smooth_needled_crown` | OBJ mesh | V22 smooth botanical; SC crown attractor target, 900 attractors, 876 covered, 52 leaves, 130 needles. | Good baseline crown before V25 refinement. Risk: V25 candidates are likely cleaner for cap/trunk issues. |
| 8 | `V22_sc_bush_shell_220_smooth_leaf_shell` | OBJ mesh | V22 smooth botanical; SC bush-shell outward coverage, 180 leaves and 28 needles. | Good spider-plant rosette analog because the shell can become radial leaves. Risk: bush-shell may look like generic shrub instead of fern/spider plant. |
| 9 | `V25_lsys_root_fan_smooth_anchorD_stable` | OBJ mesh | V25 root refine; depth-5 root fan, 440 rootlets, smoother/lighter than dense anchorD. | Safer if dense rootlets produce visual clutter. Risk: less impressive fine detail than dense anchorD. |
| 10 | `root_vine_connected_control` | OBJ mesh | Existing connected expansion input: `/inputs/connected_best_expansion_20260509/root_vine_connected_control.obj`; 14.6k vertices / 29.5k faces. | Stable connected vine control. Good if strict continuity is more important than botanical novelty. Risk: older generic vine/root provenance and less fern/spider specificity. |
| 11 | `v17_lsys_climbing_vine_d6_reference_leafy_swept_curl` | OBJ mesh | V17 reference-seeded plants/roots; source references vine GLB/PBR placement; 2.7k vertices / 5.1k faces. | Ultra-light fallback for quick grammar tests. Risk: V17 quality is earlier than V22/V25. |
| 12 | `lsystem_tree_root_upward_crown_handles_fix` | GLB | Local orientation-fix result: `/results/lsystem_tree_root_orientation_fix_20260510_local_v2/glb/lsystem_tree_root_upward_crown_handles_fix.glb`; documented orientation/root-upward fix. | Useful for tree/root/crown handle sanity checks and GLB pipeline compatibility. Risk: not specifically fern/spider and should be treated as a technical root, not final visual root. |
| 13 | `poly_pizza_small_plant_CC0_ab53ddde` | GLB | Downloaded CC0 Poly Pizza small plant: `/downloads/spider_plant_sources_20260511/poly_pizza_small_plant_CC0_ab53ddde.glb`; 14 KB. | Only true external CC0 plant mesh in the scout. Good legal/provenance seed. Risk: tiny/simple mesh, likely too low-detail for publication root unless regenerated/naturalized. |
| 14 | `spider_plant_commons_pd_condition_1024` | PNG condition image | Wikimedia Commons `Chlorophytum comosum.png`, public domain; local condition image under `/downloads/fern_spider_sources_20260511/`. | Best spider-plant visual guide: radial basal rosette plus dangling plantlets can steer grammar/texturing. Risk: it is a 2D reference, not a mesh root. |
| 15 | `new_fern_fronds_ccby2_condition_1024` / `koru_unfurling_ccby25_condition_1024` | PNG condition images | Wikimedia Commons fern references, CC BY 2.0 / CC BY 2.5. | Best fern grammar guides: frond cluster and curled crozier. Risk: attribution required and 2D-only; use as guide, not mesh root. |

## Notes on Provenance and Existing Evidence

- The V22/V24/V25 OBJ candidates are generated procedural inputs mirrored locally from remote-oriented batches, not downloaded public plant meshes. Their provenance is explicit in metadata JSON: grammar family, source baseline, connectivity gate, and generation policy.
- V25 is the best batch for immediate main-text root selection because it was explicitly refined for root/SC crown quality and has `do_not_launch_remote: true` in its local input summary.
- V24 is useful where V25 lacks a matching family; its metadata includes rerun reasons and QA priorities, especially root-quality reruns.
- V22 remains useful as a broad smooth botanical pool and fallback for vine/leaf/tendril variations.
- The fern/spider downloads are strong condition/provenance assets, but only the Poly Pizza item is a mesh. The Wikimedia items are better used as conditioning images or grammar references.

## Recommended Grammar Pairings

### A. Spider Plant / Chlorophytum Case

Root: `V25_lsys_root_fan_dense_anchorD_stable` or `poly_pizza_small_plant_CC0_ab53ddde` as legal/public mesh seed if external provenance matters.

Guide: `spider_plant_commons_pd_condition_1024.png`.

Grammar:

- Base rosette: radial crown module with 18-32 strap leaves, each leaf a tapered curved ribbon attached by shared vertices to a crown/root collar.
- Runner recursion: use the V22 vine grammar as a stolon operator: `runner -> runner segment + plantlet(anchor) + optional aerial roots`.
- Plantlet rule: terminal nodes instantiate a mini rosette at scale 0.35-0.55 with 3-8 leaves and 2-5 rootlets.
- Connectivity invariant: every runner, plantlet, and aerial root must share at least one anchor with the root/collar support before texturing.

### B. Fern / Fiddlehead Case

Root: `V24_sc_root_network_260_anchorA_seedA` or `V22_sc_root_network_parameter_sweep_dense_smooth_rootlets`.

Guide: `koru_unfurling_ccby25_condition_1024.png`, `fiddlehead_golden_spiral_ccby4_condition_1024.png`, and `new_fern_fronds_ccby2_condition_1024.png`.

Grammar:

- Rhizome support: SC root network with low, lateral, connected root/rhizome web.
- Crozier recursion: curled spiral tip with decreasing-radius copies along a logarithmic or turtle-arc frame.
- Frond expansion: each frond spine emits alternating pinnae; pinnae density increases with depth, but pinnae must be attached laminae, not floating cards.
- Best experimental split: one curled-fiddlehead hero and one mature frond-cluster row, using the same rhizome root for same-root comparison.

### C. Tree-Crown-Like Botanical Main Case

Root: `V25_sc_tree_crown_leafshield_B` for publishable render, paired with `V25_sc_tree_crown_tapered_B` as structural ablation.

Grammar:

- Use SC attractor competition as the macro skeleton: nodes grow toward attractor averages, with top radial shrink and small positive z gain.
- Attach recursive leaf/frond modules only at terminal and near-terminal nodes; use leafshield only as terminal cover, not as hidden postprocess.
- Add a crown collar/junction rule from the root-fan cases to avoid trunk cut caps.
- Report same-root rows: tapered_B raw structural crown, leafshield_B visual crown, and a no-leaf/low-leaf ablation.

## Practical Next Step

For the next local/remote iteration, I would build a small, fixed-root grid:

1. Crown hero: `V25_sc_tree_crown_leafshield_B` + SC crown grammar + terminal leaf/frond cover.
2. Crown structure ablation: `V25_sc_tree_crown_tapered_B` + same grammar, reduced leafshield.
3. Spider plant: `V25_lsys_root_fan_dense_anchorD_stable` + rosette + runner/plantlet recursion, conditioned by the public-domain spider plant image.
4. Fern: `V24_sc_root_network_260_anchorA_seedA` + rhizome + curled crozier/frond recursion, conditioned by CC fern images with attribution.
5. Vine bridge: `V22_lsys_climbing_vine_d6_smooth_leaf_tendrils` + hanging runner grammar to connect prior vine success to spider-plant semantics.

This gives one strong main-text crown row, one root/rhizome fern row, one spider-plant row, and one continuity bridge from the already strong vine evidence.
