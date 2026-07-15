# V25 root/SC refine QA recommendation

日期：2026-05-10

## 0. Evidence files

- rows: `results/strict_visual_matched_texture_V25_root_sc_refine_rows_20260510.csv`
- comparison: `results/strict_visual_matched_texture_V25_root_sc_refine_comparison_20260510.csv`
- json: `results/strict_visual_matched_texture_V25_root_sc_refine_comparison_20260510.json`
- surface metrics: `results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/surface_metrics_occ64.csv`
- manifest: `results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/inputs/manifest.csv`

## 1. Replacement decision

V25 is a root/SC refinement screen. It can replace the current V24 one-to-one rows only after both metric gates and white-background zoom QA pass.

- `root` best: `V25_lsys_root_fan_smooth_anchorD_stable` (replace-metric-eligible), r0=1 / LCR 1.000000; V24 reference `V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA` had max r0=4, min LCR=0.998593. root row can upgrade from visual panel to topology/main-stable candidate, pending zoom QA
- `sc` best: `V25_sc_tree_crown_tapered_B` (replace-metric-eligible), r0=1 / LCR 1.000000; V24 reference `V24_sc_tree_crown_260_attractor_clean_seedA` had max r0=1, min LCR=1.000000. SC row preserves V24 metric floor; replacement depends on visibly better trunk/cap zoom

## 2. Candidate table

| case | family | r0 comps | r0 LCR | r1 comps | gate | recommendation |
|---|---:|---:|---:|---:|---|---|
| `V25_lsys_root_fan_dense_anchorC_stable` | L-system | 6 | 0.998345 | 1 | reject-main | root row is weaker than the V24 caveated baseline |
| `V25_lsys_root_fan_dense_anchorD_stable` | L-system | 4 | 0.997915 | 1 | reject-main | root row is weaker than the V24 caveated baseline |
| `V25_lsys_root_fan_smooth_anchorC_stable` | L-system | 2 | 0.999682 | 1 | visual-only-candidate | root row remains visual-family evidence; tiny r0 islands must be invisible in zoom |
| `V25_lsys_root_fan_smooth_anchorD_stable` | L-system | 1 | 1.000000 | 1 | replace-metric-eligible | root row can upgrade from visual panel to topology/main-stable candidate, pending zoom QA |
| `V25_sc_tree_crown_leafshield_A` | Space colonization | 3 | 0.999750 | 1 | appendix-only | SC visual may improve but metric regresses from V24 SC A |
| `V25_sc_tree_crown_leafshield_B` | Space colonization | 3 | 0.999758 | 1 | appendix-only | SC visual may improve but metric regresses from V24 SC A |
| `V25_sc_tree_crown_tapered_A` | Space colonization | 2 | 0.999868 | 1 | appendix-only | SC visual may improve but metric regresses from V24 SC A |
| `V25_sc_tree_crown_tapered_B` | Space colonization | 1 | 1.000000 | 1 | replace-metric-eligible | SC row preserves V24 metric floor; replacement depends on visibly better trunk/cap zoom |

## 3. Claim boundary

- Root candidates with r0 islands remain visual-family evidence only, even if r1 is connected.
- SC candidates must not regress below the V24 SC A metric floor; otherwise they can only be appendix visual variants.
- Surface metrics are post-GLB renderability/connectivity diagnostics, not watertight topology proofs.
