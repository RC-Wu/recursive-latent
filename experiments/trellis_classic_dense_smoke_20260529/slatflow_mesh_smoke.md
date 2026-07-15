# TRELLIS classic SLat-flow-to-mesh smoke

## Results
- OK `imports_and_patches`: {'torch': '2.10.0+cu128'}
- OK `pipeline_loaded`: {'sec': 19.139832019805908}
- OK `slat_flow_decode`: {'sec': 2.597020387649536, 'peak_gb': 7.639690399169922, 'coords': 216, 'keys': ['mesh']}
- FAIL `failed`: Traceback (most recent call last):   File "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/trellis_classic_dense_smoke_20260529/scripts/trellis_classic_slatflow_mesh_smoke.py", line 56, in <module>     verts=getattr(mesh_obj,'vertices',None) or getattr(mesh_obj,'v',None); faces=getattr(mesh_obj,'faces',None) or getattr(mesh_obj,'f',None) RuntimeError: Boolean value of Tensor with no values is ambiguous 
