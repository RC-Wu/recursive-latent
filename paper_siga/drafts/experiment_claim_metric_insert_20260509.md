# Experiment Claim / Metric Insert Draft 20260509

Pasteable paragraph draft:

We evaluate recursive growth outputs with a claim-aligned metric protocol rather than treating textured renders as topology evidence. For each reported depth, we voxelize the support and measure 6-neighborhood occupancy component count and largest-component ratio (LCR), while reporting mesh or raw-face component diagnostics separately. Under this protocol, the vine depth showcase remains occupancy-connected across the displayed stages (`Comp6N=1`, `LCR6N=1.0`), and the bismuth-like and pyrite-like scaffold depth cases also maintain connected voxel support across four stages. These results support the narrower claim that the recursive proposal can preserve connected voxelized support for selected scaffold families. They do not, by themselves, establish clean face-level topology or physically faithful growth: textured vine exports have highly fragmented raw face components, the pyrite scaffold shows increasing mesh component counts with depth, and post-hoc DLA bridge ablations can improve face-level or LCR diagnostics while still failing occupancy connectivity and visual QA. We therefore treat DLA/coral as a stress-test and negative-ablation setting unless matched frontier baselines, porosity/cavity metrics, bridge-survival labels, and neutral zoom-in QA are added.

Optional short table reference sentence:

The claim-aligned summary in Fig./Table X reports occupancy connectedness, LCR, mesh/face diagnostics, effective-resolution proxies, root/branch/path proxies where available, and visual pass/fail status; missing branch/path metrics and same-root matched baselines are marked explicitly rather than inferred from render quality.
