# Rendering and Texturing Setup Notes - 2026-05-08

## Current Decision

Use two rendering paths:

1. **Remote A100 Trellis2 texturing/export path** for true PBR GLB attempts.
2. **Local Blender/Cycles path** for paper-quality neutral mesh rendering and visual QA.

This split is intentional. The remote environment has the Trellis2 CUDA stack, `nvdiffrast`, `cumesh`, and sparse ops; the local Mac has a working Blender binary with `bpy`.

## Remote A100-2 State

Project root:

`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`

Trellis2 env and source:

- env: `/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/envs/trellis2_bakeoff`
- source: `/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/repos/TRELLIS.2`
- path setup: `/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env`

Verified packages:

- `nvdiffrast==0.4.0`: installed and CUDA smoke passed.
- `pyrender==0.1.45`: EGL offscreen smoke passed.
- `trimesh==4.11.3`, `pygltflib==1.16.5`, `PyOpenGL==3.1.0`: installed.
- `cumesh`, `o_voxel`, `flex_gemm`: available through the Trellis2 stack.

Known failures:

- `bpy` remote install failed because no compatible wheel was available.
- No remote system `blender` binary was found.

Important logs:

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/render_deps_nvdiffrast_zip_20260508_125129.log`
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/render_deps_bpy_20260508_125948.log`
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/render_deps_smoke_20260508_130128.log`
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/render_deps_trellis_postprocess_smoke_box_patched_20260508_130807.log`

## Required Remote Environment Block

Do not use `/tmp` or `/dev/shm`; keep all caches under the project root.

```bash
ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
source /mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env

export PYTHONPATH="$ROOT/assets/python_shims:$ROOT/assets:$MESHVAE_TRELLIS:${PYTHONPATH:-}"
export HF_HOME="$ROOT/hf_home"
export TRANSFORMERS_CACHE="$ROOT/hf_home/transformers"
export TORCH_HOME="$ROOT/cache/torch"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/cache/tmp"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$ROOT/cache/torch_extensions"
export TRITON_CACHE_DIR="$ROOT/cache/triton/<run_name>"
export ATTN_BACKEND=xformers
export CUDA_VISIBLE_DEVICES=<gpu>
```

Every Trellis2 script that may compile Triton kernels on BeEGFS should call:

```python
from triton_beegfs_cache_patch import apply_triton_beegfs_cache_patch
apply_triton_beegfs_cache_patch()
```

Without this patch, Triton can fail on BeEGFS with `OSError: [Errno 16] Device or resource busy ... os.replace(...)`.

## Trellis2 Texturing Export Path

Official Trellis2 pipeline:

`$MESHVAE_TRELLIS/trellis2/pipelines/trellis2_texturing.py`

Expected flow:

`preprocess_mesh -> get_cond -> encode_shape_slat -> sample_tex_slat -> decode_tex_slat -> postprocess_mesh -> output.export(...glb...)`

Project export smoke script:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/trellis2_texturing_export_glb.py`

Remote synced path:

`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets/trellis2_texturing_export_glb.py`

Current smoke:

- input mesh: `results/siga_projected_recursive_loop_20260508_0715/vine_d5_projected_compete/stage_05/projected/vine_d5_projected_compete_stage_05/mesh_pruned.obj`
- guide image: `inputs/trellis_example_images_subset/04_130c2b18f1651a70f8aa15b2c99f8dba29bb943044d92871f9223bd3e989e8b1.webp`
- output dir: `results/siga_textured_glb_export/textured_glb_20260508/vine_d5_compete_s5`
- log: `logs/textured_glb_vine_d5_compete_s5_20260508_131659.log`
- status at 2026-05-08 13:18 +08: texture sampling completed; postprocess/export still running.

## Local Blender State

Blender binary:

`/Applications/Blender.app/Contents/MacOS/Blender`

Version observed:

`Blender 5.1.1`, Python `3.13.9`

Local render helper env:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/.venv_render`

Local render script:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/blender_render_recursive_mesh.py`

Rendered outputs:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/paper_quality_renders_20260508/blender_tiles/`

Current Blender render judgement:

- Better than matplotlib contact sheets for paper QA.
- Still neutral material only; no true texture.
- The best current geometry render is `vine_d5_compete_iso.png`, but it exposes holes/mesh defects and cannot be treated as final asset quality.

## Practical Rule

Use remote A100 only for Trellis2 encode/decode/texturing/export. Use local Blender for final paper render whenever the asset is already available as OBJ/GLB.
