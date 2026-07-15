# TRELLIS classic mesh decoder smoke

## Results
- OK `imports`: {'torch': '2.10.0+cu128', 'cuda': '12.8'}
- OK `decoder_loaded`: {'sec': 6.06833553314209, 'type': "<class 'trellis.models.structured_latent_vae.decoder_mesh.SLatMeshDecoder'>"}
- OK `runtime_patch_cubes_to_verts_dtype`: enabled+c2m_get_dense_attrs
- OK `runtime_patch_to_representation_fp32_mesh`: enabled
- OK `decoder_forward`: {'sec': 2.670569658279419, 'peak_gb': 5.610955238342285, 'type': "<class 'list'>", 'len': 1}
- OK `out_repr`: <trellis.representations.mesh.cube2mesh.MeshExtractResult object at 0x7fae028d2800>
- OK `mesh_export`: {'path': '/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/trellis_classic_dense_smoke_20260529/mesh_decoder_random_slat_smoke.ply', 'verts': 258, 'faces': 468}
