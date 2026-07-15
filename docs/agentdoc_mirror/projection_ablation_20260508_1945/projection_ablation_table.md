# Projection Ablation Table - 2026-05-08 19:45

| Case | Direct comps | Direct largest ratio | Final-only kept | Final-only largest ratio | Per-depth raw comps | Per-depth kept | Per-depth largest ratio | Read |
|---|---:|---:|---:|---:|---:|---:|---|---|
| vine_compete_d3 | 2059 | 0.9049 | 2 | 0.9934 | 819 | 1 | 1.0000 | Per-depth strongly reduces raw components before final stage and preserves one dominant asset. |
| tree_compete_d3 | 3201 | 0.9169 | 4 | 0.9842 | 835 | 2 | 0.9949 | Per-depth strongly reduces raw components before final stage and preserves one dominant asset. |
| vine_compete_fork_d3 | 11490 | 0.5178 | 11 | 0.6863 | 2581 | 24 | 0.5758 | Per-depth lowers raw component explosion but expression remains fragmented; needs stricter projection or attachment. |
| tree_compete_fork_d3 | 12166 | 0.5869 | 20 | 0.6937 | 5538 | 53 | 0.6141 | Per-depth lowers raw component explosion but expression remains fragmented; needs stricter projection or attachment. |

## Interpretation

For conservative `compete`, per-depth projection is clearly stronger than final-only cleanup: the raw component count entering the final stage is much lower (`vine`: 2059 -> 819, `tree`: 3201 -> 835) and the projected result keeps a nearly single dominant component. For expressive `compete_fork`, per-depth projection still reduces raw component explosion (`vine`: 11490 -> 2581, `tree`: 12166 -> 5538), but the final projected mesh remains distributed across many components. This should be written as the stability-expression boundary, not as a universal win.

## Preview Visual

Preview contact sheet:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/projection_ablation_20260508_1945/projection_ablation_preview_contact_sheet.png`

Obsidian asset mirror:

`/Users/fanta/Documents/Obsidian Vault/HumanLibrary/10_Projects/recursive_3d_generative_growth/Assets/2026-05-08/projection_ablation_preview_contact_sheet.png`

Visual judgement:

- Direct recursion visibly leaves small floating fragments around the asset.
- Final-only projection removes final fragments but does not demonstrate that intermediate recursive states were valid.
- Per-depth projection changes the evolving shape because every stage is decoded, projected, and re-encoded before the next rule. This is the correct visual story for the method, but the current contact sheet is only a matplotlib/scatter preview; final paper should use Blender/Cycles renders from selected meshes.
