import os, sys, json, traceback, subprocess, importlib, inspect, glob, time
from pathlib import Path
ROOT=Path(os.environ["ROOT"])
RUN=Path(os.environ["RUN"])
REPO=Path(os.environ["REPO"])
WEIGHTS=Path(os.environ["WEIGHTS"])
STUB=RUN/"stubs"
sys.path.insert(0, str(STUB))
sys.path.insert(0, str(REPO))
log=[]
def rec(name, ok, detail=""):
    msg={"name":name,"ok":bool(ok),"detail":str(detail)[:6000]}
    log.append(msg)
    print(json.dumps(msg, ensure_ascii=False), flush=True)

def run(cmd, name, timeout=60):
    try:
        p=subprocess.run(cmd, cwd=str(REPO), shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        rec(name, p.returncode==0, p.stdout)
        return p.returncode, p.stdout
    except Exception:
        rec(name, False, traceback.format_exc())
        return 999, traceback.format_exc()

rec("paths", True, {"repo":str(REPO),"weights":str(WEIGHTS),"weights_exists":WEIGHTS.exists(),"run":str(RUN)})
run("find . -maxdepth 4 -type f -name '*.py' | sed -n '1,240p'", "python_file_inventory", 40)
run("grep -R \"kaolin\\|open3d\\|TrellisImageTo3DPipeline\\|from_pretrained\\|to_glb\\|decode\" -n trellis example.py app.py scripts 2>/dev/null | sed -n '1,260p'", "grep_key_symbols", 60)
for m in ["torch","trimesh","DracoPy","utils3d","rembg","kaolin","open3d"]:
    try:
        mod=importlib.import_module(m)
        rec("import:"+m, True, getattr(mod, "__file__", "builtin"))
    except Exception:
        rec("import:"+m, False, traceback.format_exc())
try:
    import torch
    rec("torch_cuda", torch.cuda.is_available(), {"version":torch.__version__, "cuda":torch.version.cuda, "gpu_count":torch.cuda.device_count(), "name0":torch.cuda.get_device_name(0) if torch.cuda.is_available() else None})
except Exception:
    rec("torch_cuda", False, traceback.format_exc())

# Import package modules progressively.
mods=["trellis", "trellis.pipelines", "trellis.representations", "trellis.modules", "trellis.utils"]
for m in mods:
    try:
        mod=importlib.import_module(m)
        rec("import:"+m, True, getattr(mod,"__file__",None))
    except Exception:
        rec("import:"+m, False, traceback.format_exc())

# Introspect pipeline API.
try:
    import trellis.pipelines as pipes
    names=[n for n in dir(pipes) if "Pipeline" in n or "Trellis" in n or "Image" in n]
    rec("pipeline_names", True, names)
    for n in names:
        obj=getattr(pipes,n)
        try:
            rec("pipeline_class:"+n, True, inspect.signature(obj.from_pretrained) if hasattr(obj,"from_pretrained") else inspect.signature(obj))
        except Exception as e:
            rec("pipeline_class:"+n, True, "signature_failed:"+repr(e))
except Exception:
    rec("pipeline_introspect", False, traceback.format_exc())

# Try official image pipeline load and minimal run with a synthetic RGBA image, if API exists.
try:
    from PIL import Image, ImageDraw
    import torch
    import trellis.pipelines as pipes
    cls=None
    for cand in ["TrellisImageTo3DPipeline", "TrellisImageTo3DPipelineWithPretrained", "ImageTo3DPipeline"]:
        if hasattr(pipes, cand):
            cls=getattr(pipes,cand); break
    if cls is None:
        raise RuntimeError("no known image-to-3d pipeline class in trellis.pipelines")
    rec("selected_pipeline", True, cls)
    t0=time.time()
    pipe=cls.from_pretrained(str(WEIGHTS))
    rec("pipeline_loaded", True, {"seconds":time.time()-t0, "type":str(type(pipe))})
    if hasattr(pipe, "cuda") and torch.cuda.is_available():
        pipe=pipe.cuda()
        rec("pipeline_cuda", True, "moved")
    img=Image.new("RGBA", (256,256), (0,0,0,0))
    d=ImageDraw.Draw(img)
    d.ellipse((48,48,208,208), fill=(180,180,180,255))
    img_path=RUN/"synthetic_input.png"
    img.save(img_path)
    # Try several run signatures. Keep steps small where supported.
    outputs=None
    errors=[]
    for kwargs in [
        {"image":img, "seed":1, "formats":["mesh"]},
        {"image":img, "seed":1},
        {"image":img},
    ]:
        try:
            t1=time.time(); outputs=pipe.run(**kwargs); rec("pipeline_run", True, {"kwargs":list(kwargs.keys()), "seconds":time.time()-t1, "type":str(type(outputs)), "keys":list(outputs.keys()) if isinstance(outputs, dict) else None}); break
        except Exception as e:
            errors.append((kwargs, traceback.format_exc()))
    if outputs is None:
        raise RuntimeError("all pipeline.run attempts failed: "+json.dumps([(k, e[-1500:]) for k,e in errors], ensure_ascii=False))
    out_txt=RUN/"pipeline_outputs_repr.txt"
    out_txt.write_text(repr(outputs)[:20000])
    rec("pipeline_outputs_saved", True, str(out_txt))
except Exception:
    rec("pipeline_smoke", False, traceback.format_exc())

# Try locating mesh decoder modules and importing them directly.
run("find trellis -type f | grep -Ei 'mesh|slat|decoder|pipeline' | sed -n '1,220p'", "mesh_related_files", 40)
try:
    # These names vary; this block is diagnostic only.
    candidates=[]
    for py in REPO.joinpath("trellis").rglob("*.py"):
        txt=py.read_text(errors="ignore")
        if "Mesh" in txt and ("Decoder" in txt or "decode" in txt):
            candidates.append(str(py.relative_to(REPO)))
    rec("mesh_decoder_candidates", True, candidates[:80])
except Exception:
    rec("mesh_decoder_candidates", False, traceback.format_exc())

(RUN/"report_raw.json").write_text(json.dumps(log, ensure_ascii=False, indent=2))
# Short markdown report.
lines=["# TRELLIS classic dense smoke report", "", f"repo: `{REPO}`", f"weights: `{WEIGHTS}`", "", "## Results"]
for item in log:
    status="OK" if item["ok"] else "FAIL"
    lines.append(f"- {status} `{item['name']}`: {item['detail'][:500].replace(chr(10),' ')}")
(RUN/"report.md").write_text("\n".join(lines)+"\n")
