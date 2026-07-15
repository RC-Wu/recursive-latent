import os, sys, json, traceback, time
from pathlib import Path
RUN=Path(os.environ['RUN']); REPO=Path(os.environ['REPO']); WEIGHTS=Path(os.environ['WEIGHTS'])
sys.path.insert(0, str(RUN/'stubs'))
sys.path.insert(0, str(REPO))
rows=[]
def rec(name, ok, detail=''):
    row={'name':name,'ok':bool(ok),'detail':str(detail)[:10000]}
    rows.append(row); print(json.dumps(row, ensure_ascii=False), flush=True)
try:
    import torch
    # Work around mismatched torchvision wheel where meta registration expects
    # the torchvision::nms op to exist before import.
    try:
        lib = torch.library.Library('torchvision', 'DEF')
        lib.define('nms(Tensor dets, Tensor scores, float iou_threshold) -> Tensor')
        rec('define_torchvision_nms', True, 'defined')
    except Exception as e:
        rec('define_torchvision_nms', True, 'already defined or ignored: '+repr(e))
    import torchvision
    rec('import_torchvision_after_nms_stub', True, {'torchvision': getattr(torchvision,'__version__',None), 'file': getattr(torchvision,'__file__',None)})
except Exception:
    rec('torchvision_fix', False, traceback.format_exc())
try:
    import trellis
    rec('import_trellis', True, getattr(trellis,'__file__',None))
except Exception:
    rec('import_trellis', False, traceback.format_exc())
try:
    import trellis.pipelines as pipes
    names=[n for n in dir(pipes) if 'Pipeline' in n or 'Trellis' in n or 'Image' in n]
    rec('pipeline_names', True, names)
except Exception:
    rec('pipeline_names', False, traceback.format_exc())
try:
    from trellis.pipelines import TrellisImageTo3DPipeline
    rec('pipeline_class', True, str(TrellisImageTo3DPipeline))
    t0=time.time()
    pipe=TrellisImageTo3DPipeline.from_pretrained(str(WEIGHTS))
    rec('pipeline_loaded', True, {'sec':time.time()-t0, 'type':str(type(pipe))})
    if hasattr(pipe,'cuda') and torch.cuda.is_available():
        pipe=pipe.cuda()
        rec('pipeline_cuda', True, 'ok')
    from PIL import Image, ImageDraw
    img=Image.new('RGBA',(256,256),(0,0,0,0)); d=ImageDraw.Draw(img); d.rectangle((64,64,192,192), fill=(180,180,180,255))
    (RUN/'synthetic_input_v2.png').parent.mkdir(parents=True, exist_ok=True); img.save(RUN/'synthetic_input_v2.png')
    tries=[
        {'image':img,'seed':1,'formats':['mesh']},
        {'image':img,'seed':1},
        {'image':img},
    ]
    out=None; errs=[]
    for kw in tries:
        try:
            t1=time.time(); out=pipe.run(**kw); rec('pipeline_run', True, {'kw':list(kw.keys()), 'sec':time.time()-t1, 'type':str(type(out)), 'keys':list(out.keys()) if isinstance(out,dict) else None}); break
        except Exception:
            errs.append((kw, traceback.format_exc()))
            rec('pipeline_run_try_failed', False, {'kw':list(kw.keys()), 'err':errs[-1][1][-3000:]})
    if out is not None:
        (RUN/'pipeline_outputs_repr_v2.txt').write_text(repr(out)[:30000])
        rec('pipeline_outputs_repr', True, str(RUN/'pipeline_outputs_repr_v2.txt'))
        # Try exporting first mesh-like object if present.
        if isinstance(out, dict):
            for k,v in out.items():
                if isinstance(v, (list,tuple)) and v:
                    vv=v[0]
                else:
                    vv=v
                if hasattr(vv, 'vertices') and hasattr(vv, 'faces'):
                    import trimesh
                    mesh=trimesh.Trimesh(vertices=vv.vertices.detach().cpu().numpy() if hasattr(vv.vertices,'detach') else vv.vertices, faces=vv.faces.detach().cpu().numpy() if hasattr(vv.faces,'detach') else vv.faces, process=False)
                    path=RUN/f'pipeline_{k}_v2.ply'; mesh.export(path); rec('mesh_export', True, str(path)); break
    else:
        raise RuntimeError('all pipeline run attempts failed')
except Exception:
    rec('pipeline_load_or_run', False, traceback.format_exc())
try:
    (RUN/'report_v2_raw.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    lines=['# TRELLIS classic dense smoke v2','','## Results']
    for r in rows:
        lines.append(f"- {'OK' if r['ok'] else 'FAIL'} `{r['name']}`: {r['detail'][:700].replace(chr(10),' ')}")
    (RUN/'report_v2.md').write_text('\n'.join(lines)+'\n')
except Exception:
    pass
