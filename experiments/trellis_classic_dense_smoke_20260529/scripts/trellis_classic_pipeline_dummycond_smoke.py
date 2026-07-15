import os, sys, json, traceback, time
from pathlib import Path
RUN=Path(os.environ['RUN']); REPO=Path(os.environ['REPO']); WEIGHTS=Path(os.environ['WEIGHTS'])
sys.path.insert(0, str(RUN/'stubs')); sys.path.insert(0, str(REPO))
rows=[]
def rec(name, ok, detail=''):
    row={'name':name,'ok':bool(ok),'detail':str(detail)[:10000]}; rows.append(row); print(json.dumps(row,ensure_ascii=False),flush=True)
try:
    import torch
    import torch.nn as nn
    # dummy DINO to avoid network/hub during pipeline init; validates TRELLIS model chain.
    class DummyDINO(nn.Module):
        def eval(self): return self
        def forward(self, image, is_training=True):
            b=image.shape[0]
            return {'x_prenorm': torch.zeros((b, 1374, 1024), device=image.device, dtype=image.dtype)}
        __call__ = forward
    torch.hub.load = lambda *args, **kwargs: DummyDINO()
    try:
        lib=torch.library.Library('torchvision','DEF'); lib.define('nms(Tensor dets, Tensor scores, float iou_threshold) -> Tensor')
    except Exception: pass
    import trellis.representations.mesh.utils_cube as uc
    def _cubes_to_verts(num_verts, cubes, value, reduce='mean'):
        M=value.shape[2]
        reduced=torch.zeros(num_verts, M, device=cubes.device, dtype=value.dtype)
        return torch.scatter_reduce(reduced,0,cubes.unsqueeze(-1).expand(-1,-1,M).flatten(0,1),value.flatten(0,1),reduce=reduce,include_self=False)
    def _get_dense_attrs(coords, feats, res, sdf_init=True):
        F=feats.shape[-1]
        dense_attrs=torch.zeros([res]*3+[F],device=feats.device,dtype=feats.dtype)
        if sdf_init: dense_attrs[...,0]=1
        dense_attrs[coords[:,0],coords[:,1],coords[:,2],:]=feats
        return dense_attrs.reshape(-1,F)
    uc.cubes_to_verts=_cubes_to_verts; uc.get_dense_attrs=_get_dense_attrs
    import trellis.representations.mesh.cube2mesh as c2m
    c2m.get_dense_attrs=_get_dense_attrs
    import trellis.models.structured_latent_vae.decoder_mesh as dm
    def _to_representation_fp32_mesh(self,x):
        ret=[]
        for i in range(x.shape[0]):
            xi=x[i]
            xi=xi.replace(xi.feats.float()) if hasattr(xi,'replace') else xi
            ret.append(self.mesh_extractor(xi, training=self.training))
        return ret
    dm.SLatMeshDecoder.to_representation=_to_representation_fp32_mesh
    from trellis.pipelines import TrellisImageTo3DPipeline
    rec('imports_and_patches', True, {'torch':torch.__version__})
    t0=time.time(); pipe=TrellisImageTo3DPipeline.from_pretrained(str(WEIGHTS)); rec('pipeline_loaded', True, {'sec':time.time()-t0, 'models':list(pipe.models.keys())})
    pipe.cuda()
    from PIL import Image, ImageDraw
    img=Image.new('RGBA',(256,256),(0,0,0,0)); d=ImageDraw.Draw(img); d.ellipse((48,48,208,208), fill=(180,180,180,255))
    img.save(RUN/'dummycond_input.png')
    torch.cuda.reset_peak_memory_stats(); t1=time.time()
    with torch.no_grad():
        out=pipe.run(
            img, seed=1, formats=['mesh'], preprocess_image=True,
            sparse_structure_sampler_params={'steps':1, 'cfg_strength':1.0, 'cfg_interval':[0.0,1.0]},
            slat_sampler_params={'steps':1, 'cfg_strength':1.0, 'cfg_interval':[0.0,1.0]},
        )
    torch.cuda.synchronize()
    rec('pipeline_run_dummycond', True, {'sec':time.time()-t1, 'peak_gb':torch.cuda.max_memory_allocated()/1024**3, 'keys':list(out.keys())})
    mesh_obj=out['mesh'][0] if isinstance(out.get('mesh'), (list,tuple)) else out.get('mesh')
    verts=getattr(mesh_obj,'vertices',None) or getattr(mesh_obj,'v',None)
    faces=getattr(mesh_obj,'faces',None) or getattr(mesh_obj,'f',None)
    if verts is not None and faces is not None:
        import trimesh
        vv=verts.detach().float().cpu().numpy() if hasattr(verts,'detach') else verts
        ff=faces.detach().cpu().numpy() if hasattr(faces,'detach') else faces
        mesh=trimesh.Trimesh(vertices=vv, faces=ff, process=False)
        outp=RUN/'pipeline_dummycond_mesh.ply'; mesh.export(outp)
        rec('pipeline_mesh_export', True, {'path':str(outp),'verts':len(mesh.vertices),'faces':len(mesh.faces)})
    else:
        rec('pipeline_mesh_export', False, repr(mesh_obj)[:2000])
except Exception:
    rec('failed', False, traceback.format_exc())
(RUN/'pipeline_dummycond_smoke_raw.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
lines=['# TRELLIS classic pipeline dummy-condition smoke','','## Results']
for r in rows: lines.append(f"- {'OK' if r['ok'] else 'FAIL'} `{r['name']}`: {r['detail'][:1000].replace(chr(10),' ')}")
(RUN/'pipeline_dummycond_smoke.md').write_text('\n'.join(lines)+'\n')
