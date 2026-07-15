# TRELLIS classic dense smoke v2

## Results
- OK `define_torchvision_nms`: defined
- OK `import_torchvision_after_nms_stub`: {'torchvision': '0.26.0+cu130', 'file': '/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/envs/trellis2_bakeoff_flashattn_20260519/lib/python3.10/site-packages/torchvision/__init__.py'}
- OK `import_trellis`: /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/repos/TRELLIS/trellis/__init__.py
- OK `pipeline_names`: ['TrellisImageTo3DPipeline', 'TrellisTextTo3DPipeline']
- OK `pipeline_class`: <class 'trellis.pipelines.trellis_image_to_3d.TrellisImageTo3DPipeline'>
- FAIL `pipeline_load_or_run`: Traceback (most recent call last):   File "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/repos/TRELLIS/trellis/pipelines/base.py", line 42, in from_pretrained     _models[k] = models.from_pretrained(f"{path}/{v}")   File "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/repos/TRELLIS/trellis/models/__init__.py", line 67, in from_pretrained     model = __getattr__(config['name'])(**config['args'], **kwargs)   File "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/repos/TRELLIS/trellis/models/structured_latent_vae/decoder_mesh.py", line 109, in __init__     SparseSubdivideBlock3d(   File "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/repos/
