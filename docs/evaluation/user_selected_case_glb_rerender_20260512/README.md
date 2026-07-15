# User-selected GLB rerender pack 20260512

Direct GLB rerenders for the user-selected cases. Outputs are white-background Blender renders, not edits of the old PNGs.

- Rendered GLB cases: 35
- Missing local GLB records: 5
- Per-case files: `overview_raw.png`, `overview_gray_callout.png`, `zoom_01.png`
- Full manifest: `rendered_glb_pack_manifest.json`
- Missing GLB list: `missing_glb_records.json`

Render command base:
`/Applications/Blender.app/Contents/MacOS/Blender -b --python scripts/figures/matched_camera_zoom_render_20260510.py -- --manifest docs/evaluation/user_selected_case_glb_rerender_20260512/glb_rerender_manifest.json --out-dir docs/evaluation/user_selected_case_glb_rerender_20260512/rendered_glb_white_1200 --resolution 1200 --samples 48 --zoom-levels 1 --camera iso --engine cycles --material-mode preserve --skip-comparison`
