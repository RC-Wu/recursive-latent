# Tree-root repair and five-case hero render QA subagent report (2026-05-10)

Scope: local-only QA in `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`. No SSH and no remote generation were used. No asset files were modified.

## 1. Tree-root repair candidate

Target:

`results/publication_repair_remote_20260510c_pull/textured_micro/micro_zpos_bud_d2_spikyguide_steps8_tex2048_seed202605304_xformers/textured.glb`

Local file status:

- `textured.glb` exists, size about `13M`.
- `summary.json` exists and records `status=ok`, `steps=8`, `texture_size=2048`, `seed=202605304`, `mesh_faces=225798`, `mesh_vertices=95659`, `glb_bytes=13986856`.
- The directory contains no rendered PNG preview.

Static GLB parse QA:

- `trimesh.load(..., force="scene")` succeeded.
- Parsed as `Scene`.
- `geometry_count=1`.
- Parsed vertex count from GLB geometry: `319895`.
- Face count: `225798`.
- Bounds: `[[-0.1987, -0.5000, -0.2041], [0.1987, 0.5000, 0.2041]]`.
- Material sample: `PBRMaterial`.
- Texture-related material attributes detected: `2`.

Replacement status for bad `lsystem_spiky_iso.png`:

- The old bad PNG exists at `visuals/public_guide_textured_glb_20260509d/renders/lsystem_spiky_iso.png`.
- Linked gallery copies also exist under `case_gallery_for_user_20260509/...` and `case_gallery_for_user_20260510_matched_selection/...`.
- No current replacement PNG was found for the new `micro_zpos_bud_d2_spikyguide.../textured.glb` candidate.
- Therefore the repair candidate is a usable textured GLB candidate, but it is not yet a drop-in image replacement for `lsystem_spiky_iso.png`.

Speckle risk:

- Since there is no local render PNG for this GLB, image-level speckle QA cannot be completed.
- The GLB is textured and parseable; this lowers file-corruption risk but does not prove paper-safe visual quality.
- Speckle risk remains `unknown / needs render`, especially because the source guide is spiky/tendril-like and may produce fine high-frequency texture on narrow geometry.

Recommended next step:

Render this GLB locally into at least `iso`, `front`, and `side` paper-safe previews, then compare against the old `lsystem_spiky_iso.png`. Only after visual QA should it replace the bad PNG in user-facing galleries or paper figures.

## 2. Five-case hero current local state

PNG render directory:

`visuals/hero_combo_publication_20260510_contrast_wide_1800/`

GLB directory:

`visuals/hero_combo_publication_20260510_contrast_wide_1200_glb/`

### 2.1 1800 PNG package

Existing files:

- `overview.png`
- `bismuth_terraced_hopper/zoom.png`
- `pyrite_lattice_crystal/zoom.png`
- `coral_branching/zoom.png`
- `tree_root_leaf/zoom.png`
- `plant_leaf_with_base/zoom.png`
- `hero_combo_publication_manifest_20260510.json`

All six PNGs are RGB, non-interlaced, and `1800 x 1800`.

Static image metrics:

| image | mean luma | foreground proxy | high-frequency residual mean | note |
| --- | ---: | ---: | ---: | --- |
| `overview.png` | `236.15` | `0.9255` | `0.739` | bright overview; light background/platform |
| `bismuth_terraced_hopper/zoom.png` | `202.01` | `0.5621` | `1.205` | readable, strongest detail |
| `pyrite_lattice_crystal/zoom.png` | `214.29` | `0.4938` | `1.086` | readable crystal detail |
| `coral_branching/zoom.png` | `220.99` | `0.2407` | `1.071` | readable but sparse foreground |
| `tree_root_leaf/zoom.png` | `239.35` | `0.2265` | `0.611` | bright; relatively low foreground occupancy |
| `plant_leaf_with_base/zoom.png` | `245.05` | `0.0981` | `0.525` | very bright; lowest foreground occupancy and strongest layout/semantic risk |

Manifest facts:

- `engine=cycles`.
- `samples=96`.
- `resolution=[1800, 1800]`.
- `exposure=0.35`.
- `world_color_rgba=[0.91, 0.95, 0.97, 1.0]`.
- `platform_color_rgba=[0.88, 0.93, 0.95, 1.0]`.
- Zoom entries are marked `kind=camera_render`.
- `combined_glb_exported=false` in this directory.
- The manifest's `actual_outputs` includes a planned combined GLB path, but that GLB does not exist in the 1800 directory.

Status:

- The 1800 PNG render package is complete for images.
- It is not complete for GLB export, by design/current state.

### 2.2 1200_glb package

Existing files:

- `hero_combo_publication_20260510.glb`
- `hero_combo_publication_manifest_20260510.json`

Missing files:

- No `overview.png`.
- No per-case `zoom.png` files.

Static GLB parse QA:

- GLB exists, size `1,107,266,516 bytes` (about `1.0 GiB`).
- Manifest records `combined_glb_exported=true` and `qa.status=glb_exported`.
- `trimesh.load(..., force="scene")` succeeded.
- Parsed as `Scene`.
- `geometry_count=12`.
- Vertices: `26447537`.
- Faces: `21260016`.
- Bounds: `[[-61.5200, ~0, -45.3400], [61.5200, 4.6125, 46.9400]]`.
- Texture-related material attributes detected: `14`.
- All five `source_glb` paths in the manifest exist.

Status:

- The 1200_glb package is complete for combined GLB.
- It is not a complete PNG render package; its manifest still contains zoom paths, but those PNGs do not exist in this directory.

## 3. Paper-safe QA still missing

Local limitations:

- `blender` was not found on PATH in this local environment.
- Therefore I could not perform Blender import QA, viewport screenshot QA, or fresh Blender re-render QA.

Remaining paper-safe QA gaps:

- Fresh Blender import of the tree-root repair GLB.
- Fresh Blender render previews of the tree-root repair candidate in paper-safe style.
- Image-level speckle/noise QA for the tree-root repair candidate.
- Direct visual comparison between repair render and bad `lsystem_spiky_iso.png`.
- Fresh Blender import of the 1.0 GiB combined hero GLB.
- Visual viewport/render QA for the combined hero GLB after import.
- Human/visual check for horizon-line absence, contact shadow quality, and no overlap/cropping in final layout.
- Optional OCR/text check for the six hero PNGs if strict no-in-image-text QA is required.
- Final caption/semantic QA for `plant_leaf_with_base`; current asset is better described as `plant leaf / climbing vine on shared platform` than as a self-based plant.
- Coral caption QA: safe wording is smooth shading / weighted normals, not geometric remesh or subdivision smoothing.

## 4. Recommendation

Use the current five-case assets as follows:

- Paper/layout PNGs: use `visuals/hero_combo_publication_20260510_contrast_wide_1800/`.
- Combined GLB: use `visuals/hero_combo_publication_20260510_contrast_wide_1200_glb/hero_combo_publication_20260510.glb`.
- Do not describe the 1200_glb directory as a complete render-image package.
- Rename or caption the fifth case as `plant leaf / climbing vine on shared platform` unless a stricter base/pedestal asset is substituted.

For tree-root repair:

- Do not yet replace `lsystem_spiky_iso.png` with the new GLB directly.
- First create local paper-safe render previews from the new GLB and run speckle/legibility QA.
- If the render passes, use that preview as the replacement image and update gallery references.

