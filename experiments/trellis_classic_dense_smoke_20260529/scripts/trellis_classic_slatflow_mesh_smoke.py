import os, sys, json, traceback, time
from pathlib import Path
RUN=Path(os.environ['RUN']); REPO=Path(os.environ['REPO']); WEIGHTS=Path(os.environ['WEIGHTS'])
sys.path.insert(0, str(RUN/'stubs')); sys.path.insert(0, str(REPO))
rows=[]
def rec(name, ok, detail=''):
    row={'name':name,'ok':bool(ok),'detail':str(detail)[:10000]}; rows.append(row); print(json.dumps(row,ensure_ascii=False),flush=True)
try:
    import torch, torch.nn as nn
    class DummyDINO(nn.Module):
        def eval(self): return self
        def forward(self, image, is_training=True): return {'x_prenorm': torch.zeros((image.shape[0],1374,1024),device=image.device,dtype=image.dtype)}
        __call__=forward
    torch.hub.load=lambda *a, **k: DummyDINO()
    try:
        lib=torch.library.Library('torchvision','DEF'); lib.define('nms(Tensor dets, Tensor scores, float iou_threshold) -> Tensor')
    except Exception: pass
    import trellis.representations.mesh.utils_cube as uc
    def _cubes_to_verts(num_verts,cubes,value,reduce='mean'):
        M=value.shape[2]; reduced=torch.zeros(num_verts,M,device=cubes.device,dtype=value.dtype)
        return torch.scatter_reduce(reduced,0,cubes.unsqueeze(-1).expand(-1,-1,M).flatten(0,1),value.flatten(0,1),reduce=reduce,include_self=False)
    def _get_dense_attrs(coords,feats,res,sdf_init=True):
        F=feats.shape[-1]; dense_attrs=torch.zeros([res]*3+[F],device=feats.device,dtype=feats.dtype)
        if sdf_init: dense_attrs[...,0]=1
        dense_attrs[coords[:,0],coords[:,1],coords[:,2],:]=feats
        return dense_attrs.reshape(-1,F)
    uc.cubes_to_verts=_cubes_to_verts; uc.get_dense_attrs=_get_dense_attrs
    import trellis.representations.mesh.cube2mesh as c2m; c2m.get_dense_attrs=_get_dense_attrs
    import trellis.models.structured_latent_vae.decoder_mesh as dm
    def _to_representation_fp32_mesh(self,x):
        ret=[]
        for i in range(x.shape[0]):
            xi=x[i]; xi=xi.replace(xi.feats.float()) if hasattr(xi,'replace') else xi
            ret.append(self.mesh_extractor(xi,training=self.training))
        return ret
    dm.SLatMeshDecoder.to_representation=_to_representation_fp32_mesh
    from PIL import Image, ImageDraw
    from trellis.pipelines import TrellisImageTo3DPipeline
    rec('imports_and_patches', True, {'torch':torch.__version__})
    t0=time.time(); pipe=TrellisImageTo3DPipeline.from_pretrained(str(WEIGHTS)); rec('pipeline_loaded', True, {'sec':time.time()-t0})
    pipe.cuda()
    img=Image.new('RGB',(518,518),(128,128,128))
    cond=pipe.get_cond([img])
    # Fixed nonempty sparse structure: a coarse cube shell in 64^3 with batch idx 0.
    vals=torch.arange(20,44,4,device='cuda',dtype=torch.int32)
    grid=torch.stack(torch.meshgrid(vals,vals,vals,indexing='ij'),dim=-1).reshape(-1,3)
    batch=torch.zeros((grid.shape[0],1),device='cuda',dtype=torch.int32)
    coords=torch.cat([batch,grid],dim=1)
    torch.cuda.reset_peak_memory_stats(); t1=time.time()
    with torch.no_grad():
        slat=pipe.sample_slat(cond, coords, {'steps':1,'cfg_strength':1.0,'cfg_interval':[0.0,1.0]})
        out=pipe.decode_slat(slat, ['mesh'])
    torch.cuda.synchronize()
    rec('slat_flow_decode', True, {'sec':time.time()-t1,'peak_gb':torch.cuda.max_memory_allocated()/1024**3,'coords':int(coords.shape[0]),'keys':list(out.keys())})
    mesh_obj=out['mesh'][0] if isinstance(out.get('mesh'),(list,tuple)) else out.get('mesh')
    verts=getattr(mesh_obj,'vertices',None) or getattr(mesh_obj,'v',None); faces=getattr(mesh_obj,'faces',None) or getattr(mesh_obj,'f',None)
    import trimesh
    vv=verts.detach().float().cpu().numpy() if hasattr(verts,'detach') else verts
    ff=faces.detach().cpu().numpy() if hasattr(faces,'detach') else faces
    mesh=trimesh.Trimesh(vertices=vv,faces=ff,process=False)
    outp=RUN/'slatflow_fixedcoords_mesh.ply'; mesh.export(outp)
    rec('mesh_export', True, {'path':str(outp),'verts':len(mesh.vertices),'faces':len(mesh.faces)})
except Exception:
    rec('failed', False, traceback.format_exc())
(RUN/'slatflow_mesh_smoke_raw.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
lines=['# TRELLIS classic SLat-flow-to-mesh smoke','','## Results']
for r in rows: lines.append(f"- {'OK' if r['ok'] else 'FAIL'} `{r['name']}`: {r['detail'][:1000].replace(chr(10),' ')}")
(RUN/'slatflow_mesh_smoke.md').write_text('\n'.join(lines)+'\n')
