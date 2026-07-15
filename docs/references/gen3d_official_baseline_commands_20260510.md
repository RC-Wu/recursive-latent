# Gen-3D official baseline commands/API note（2026-05-10）

本 note 只记录 Lane A 需要引用的官方入口，不代表已经下载或运行新权重。

## TRELLIS

官方来源：

- GitHub: https://github.com/microsoft/TRELLIS
- image example: https://github.com/microsoft/TRELLIS/blob/main/example.py
- text example: https://github.com/microsoft/TRELLIS/blob/main/example_text.py
- model cards: https://huggingface.co/microsoft/TRELLIS-image-large, https://huggingface.co/microsoft/TRELLIS-text-xlarge

官方 image-to-3D 最小 API：

```python
from PIL import Image
from trellis.pipelines import TrellisImageTo3DPipeline
from trellis.utils import postprocessing_utils

pipeline = TrellisImageTo3DPipeline.from_pretrained("microsoft/TRELLIS-image-large")
pipeline.cuda()
image = Image.open("assets/example_image/T.png")
outputs = pipeline.run(image, seed=1)

glb = postprocessing_utils.to_glb(
    outputs["gaussian"][0],
    outputs["mesh"][0],
    simplify=0.95,
    texture_size=1024,
)
glb.export("sample.glb")
outputs["gaussian"][0].save_ply("sample.ply")
```

官方 text-to-3D 最小 API：

```python
from trellis.pipelines import TrellisTextTo3DPipeline
from trellis.utils import postprocessing_utils

pipeline = TrellisTextTo3DPipeline.from_pretrained("microsoft/TRELLIS-text-xlarge")
pipeline.cuda()
outputs = pipeline.run("A chair looking like a avocado.", seed=1)

glb = postprocessing_utils.to_glb(
    outputs["gaussian"][0],
    outputs["mesh"][0],
    simplify=0.95,
    texture_size=1024,
)
glb.export("sample.glb")
outputs["gaussian"][0].save_ply("sample.ply")
```

官方输出契约：`outputs` 是 dict，含 `gaussian`、`radiance_field`、`mesh` 列表；示例会写 `sample_gs.mp4`、`sample_rf.mp4`、`sample_mesh.mp4`、`sample.glb`、`sample.ply`。官方 README 同时提醒 text-to-3D 不如先用 text-to-image 再跑 image model，原因是 text-conditioned models 细节和创造性受数据限制。

## TRELLIS.2

官方来源：

- GitHub: https://github.com/microsoft/TRELLIS.2
- project page: https://microsoft.github.io/TRELLIS.2/
- model card: https://huggingface.co/microsoft/TRELLIS.2-4B
- image example: https://github.com/microsoft/TRELLIS.2/blob/main/example.py
- texturing example: https://github.com/microsoft/TRELLIS.2/blob/main/example_texturing.py

官方 image-to-3D 最小 API：

```python
import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import cv2
import imageio
import torch
from PIL import Image
from trellis2.pipelines import Trellis2ImageTo3DPipeline
from trellis2.utils import render_utils
from trellis2.renderers import EnvMap
import o_voxel

envmap = EnvMap(torch.tensor(
    cv2.cvtColor(cv2.imread("assets/hdri/forest.exr", cv2.IMREAD_UNCHANGED), cv2.COLOR_BGR2RGB),
    dtype=torch.float32,
    device="cuda",
))

pipeline = Trellis2ImageTo3DPipeline.from_pretrained("microsoft/TRELLIS.2-4B")
pipeline.cuda()
image = Image.open("assets/example_image/T.png")
mesh = pipeline.run(image)[0]
mesh.simplify(16777216)

video = render_utils.make_pbr_vis_frames(render_utils.render_video(mesh, envmap=envmap))
imageio.mimsave("sample.mp4", video, fps=15)

glb = o_voxel.postprocess.to_glb(
    vertices=mesh.vertices,
    faces=mesh.faces,
    attr_volume=mesh.attrs,
    coords=mesh.coords,
    attr_layout=mesh.layout,
    voxel_size=mesh.voxel_size,
    aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
    decimation_target=1000000,
    texture_size=4096,
    remesh=True,
    remesh_band=1,
    remesh_project=0,
    verbose=True,
)
glb.export("sample.glb", extension_webp=True)
```

官方输出契约：`sample.mp4` 是 PBR/environment lighting 预览视频；`sample.glb` 是 PBR-ready GLB。官方 README 的 released inference scope 是 image-to-3D 和 shape-conditioned PBR texturing；没有官方 text-to-3D pipeline 示例。若论文矩阵需要 TRELLIS.2 文本条件，应标为 text-to-image 前端产生图片后再 image-to-3D，不应写成 TRELLIS.2 native text-to-3D。

官方 shape-conditioned PBR texturing API：

```python
import trimesh
from PIL import Image
from trellis2.pipelines import Trellis2TexturingPipeline

pipeline = Trellis2TexturingPipeline.from_pretrained(
    "microsoft/TRELLIS.2-4B",
    config_file="texturing_pipeline.json",
)
pipeline.cuda()
mesh = trimesh.load("assets/example_texturing/the_forgotten_knight.ply")
image = Image.open("assets/example_texturing/image.webp")
output = pipeline.run(mesh, image)
output.export("textured.glb", extension_webp=True)
```

## Hunyuan3D 2.0

官方来源：

- GitHub: https://github.com/Tencent-Hunyuan/Hunyuan3D-2
- model card/root: https://huggingface.co/tencent/Hunyuan3D-2
- API server: https://github.com/Tencent-Hunyuan/Hunyuan3D-2/blob/main/api_server.py

官方 Python image-to-shape API：

```python
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline

pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained("tencent/Hunyuan3D-2")
mesh = pipeline(image="assets/demo.png")[0]
mesh.export("sample.glb")
```

官方 Python image-to-shape + image-conditioned texture API：

```python
from hy3dgen.texgen import Hunyuan3DPaintPipeline
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline

shape_pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained("tencent/Hunyuan3D-2")
mesh = shape_pipeline(image="assets/demo.png")[0]

paint_pipeline = Hunyuan3DPaintPipeline.from_pretrained("tencent/Hunyuan3D-2")
mesh = paint_pipeline(mesh, image="assets/demo.png")
mesh.export("sample_textured.glb")
```

官方 Gradio 启动命令：

```bash
python3 gradio_app.py --model_path tencent/Hunyuan3D-2 --subfolder hunyuan3d-dit-v2-0 --texgen_model_path tencent/Hunyuan3D-2 --low_vram_mode
python3 gradio_app.py --model_path tencent/Hunyuan3D-2 --subfolder hunyuan3d-dit-v2-0-turbo --texgen_model_path tencent/Hunyuan3D-2 --low_vram_mode --enable_flashvdm
```

官方 API server image-to-3D：

```bash
python api_server.py --host 0.0.0.0 --port 8080

img_b64_str=$(base64 -i assets/demo.png)
curl -X POST "http://localhost:8080/generate" \
  -H "Content-Type: application/json" \
  -d '{
        "image": "'"$img_b64_str"'"
      }' \
  -o test2.glb
```

官方输出契约：Python shape API 返回 `trimesh` mesh，可保存为 GLB/OBJ 等；API server `/generate` 返回 GLB 文件。官方 README 写明 shape-only 约 6GB VRAM，shape+texture 约 16GB VRAM。官方 `api_server.py` 的 text 分支依赖 `pipeline_t2i`，但当前源码中 `pipeline_t2i` 初始化是注释状态；因此 text-to-3D 应视为“API 文档声称支持，但本轮未验证且可能需要额外 HunyuanDiT text-to-image 组件”。
