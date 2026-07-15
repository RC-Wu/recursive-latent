import os, sys, json, traceback, time
from pathlib import Path
RUN=Path(os.environ['RUN']); REPO=Path(os.environ['REPO']); WEIGHTS=Path(os.environ['WEIGHTS'])
sys.path.insert(0, str(RUN/'stubs')); sys.path.insert(0, str(REPO))
rows=[]
def rec(name, ok, detail=''):
    row={'name':name,'ok':bool(ok),'detail':str(detail)[:8000]}; rows.append(row); print(json.dumps(row,ensure_ascii=False),flush=True)
try:
    import torch
    import trellis.models as models
    from trellis.modules import sparse as sp
    rec('imports', True, {'torch':torch.__version__, 'cuda':torch.version.cuda})
    path=str(WEIGHTS/'ckpts/slat_dec_mesh_swin8_B_64l8m256c_fp16')
    t0=time.time(); dec=models.from_pretrained(path); rec('decoder_loaded', True, {'sec':time.time()-t0, 'type':str(type(dec))})
    dec=dec.cuda().eval()
    N=512
    g=torch.Generator(device='cuda').manual_seed(123)
    coords=torch.randint(8,56,(N,3),generator=g,device='cuda',dtype=torch.int32)
    batch=torch.zeros((N,1),device='cuda',dtype=torch.int32)
    coords4=torch.cat([batch,coords],dim=1)
    feats=torch.randn((N,8),generator=g,device='cuda',dtype=torch.float16)
    slat=sp.SparseTensor(feats=feats, coords=coords4)
    # Runtime-only diagnostic patch: classic TRELLIS creates a float32
    # scatter buffer in cubes_to_verts, while the fp16 mesh decoder emits
    # fp16 attributes. Match the buffer dtype to the source tensor.
    try:
        import trellis.representations.mesh.utils_cube as uc
        def _cubes_to_verts(num_verts, cubes, value, reduce='mean'):
            M = value.shape[2]
            reduced = torch.zeros(num_verts, M, device=cubes.device, dtype=value.dtype)
            return torch.scatter_reduce(
                reduced, 0,
                cubes.unsqueeze(-1).expand(-1, -1, M).flatten(0, 1),
                value.flatten(0, 1), reduce=reduce, include_self=False,
            )
        uc.cubes_to_verts = _cubes_to_verts
        def _get_dense_attrs(coords, feats, res, sdf_init=True):
            F = feats.shape[-1]
            dense_attrs = torch.zeros([res] * 3 + [F], device=feats.device, dtype=feats.dtype)
            if sdf_init:
                dense_attrs[..., 0] = 1
            dense_attrs[coords[:, 0], coords[:, 1], coords[:, 2], :] = feats
            return dense_attrs.reshape(-1, F)
        uc.get_dense_attrs = _get_dense_attrs
        # cube2mesh imported get_dense_attrs by value; patch that module too.
        import trellis.representations.mesh.cube2mesh as c2m
        c2m.get_dense_attrs = _get_dense_attrs
        rec('runtime_patch_cubes_to_verts_dtype', True, 'enabled+c2m_get_dense_attrs')
        import trellis.models.structured_latent_vae.decoder_mesh as dm
        def _to_representation_fp32_mesh(self, x):
            ret = []
            for i in range(x.shape[0]):
                xi = x[i]
                if hasattr(xi, 'replace'):
                    xi = xi.replace(xi.feats.float())
                elif hasattr(xi, 'feats'):
                    xi.feats = xi.feats.float()
                ret.append(self.mesh_extractor(xi, training=self.training))
            return ret
        dm.SLatMeshDecoder.to_representation = _to_representation_fp32_mesh
        rec('runtime_patch_to_representation_fp32_mesh', True, 'enabled')
    except Exception as e:
        rec('runtime_patch_cubes_to_verts_dtype', False, repr(e))
    torch.cuda.reset_peak_memory_stats()
    t1=time.time()
    with torch.no_grad(), torch.autocast('cuda', dtype=torch.float16):
        out=dec(slat)
    torch.cuda.synchronize()
    rec('decoder_forward', True, {'sec':time.time()-t1, 'peak_gb':torch.cuda.max_memory_allocated()/1024**3, 'type':str(type(out)), 'len':len(out) if hasattr(out,'__len__') else None})
    # Export first mesh-like rep if possible.
    obj=out[0] if isinstance(out,(list,tuple)) and out else out
    rec('out_repr', True, repr(obj)[:2000])
    verts=getattr(obj,'vertices',None); faces=getattr(obj,'faces',None)
    if verts is None and hasattr(obj,'v'): verts=getattr(obj,'v')
    if faces is None and hasattr(obj,'f'): faces=getattr(obj,'f')
    if verts is not None and faces is not None:
        import trimesh
        vv=verts.detach().float().cpu().numpy() if hasattr(verts,'detach') else verts
        ff=faces.detach().cpu().numpy() if hasattr(faces,'detach') else faces
        mesh=trimesh.Trimesh(vertices=vv, faces=ff, process=False)
        outp=RUN/'mesh_decoder_random_slat_smoke.ply'; mesh.export(outp)
        rec('mesh_export', True, {'path':str(outp),'verts':len(mesh.vertices),'faces':len(mesh.faces)})
    else:
        rec('mesh_export', False, 'no vertices/faces attrs found')
except Exception:
    rec('failed', False, traceback.format_exc())
(RUN/'mesh_decoder_smoke_raw.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
lines=['# TRELLIS classic mesh decoder smoke','','## Results']
for r in rows: lines.append(f"- {'OK' if r['ok'] else 'FAIL'} `{r['name']}`: {r['detail'][:900].replace(chr(10),' ')}")
(RUN/'mesh_decoder_smoke.md').write_text('\n'.join(lines)+'\n')
