# Hunyuan3D 2.0 / ordinary 3D generator baseline 可行性核对（2026-05-10）

## 结论

Hunyuan3D 2.0 **不适合在当前 a100-2 项目目录内立刻作为主 baseline 跑**。只读检查显示：

- a100-2 项目目录存在：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`
- BeeGFS 空间充足：约 `22T` 可用。
- 已有 TRELLIS.2 权重 cache：`hf_home/hub/models--microsoft--TRELLIS.2-4B`，实测约 `16G`。
- 未发现 Hunyuan3D/HY3D repo、Hugging Face cache 或结果目录。
- a100-2 base `python3` 下 `hy3dgen`、`diffusers`、`torch`、`trimesh` 均不可 import；说明 Hunyuan 需要新建/定位环境、编译 texture 相关扩展并下载权重。

因此 Hunyuan3D 2.0 可以作为 **planned / secondary baseline** 写入论文或附录，但本轮主比较应优先使用已经有 cache/结果基础的 TRELLIS.2 ordinary one-shot baseline，以及 mesh-space / latent-space trivial recursion baseline。

## Hunyuan3D 2.0 最小安装与命令

官方 README 给出的安装路径是先安装 PyTorch，再：

```bash
git clone https://github.com/Tencent-Hunyuan/Hunyuan3D-2
cd Hunyuan3D-2
pip install -r requirements.txt
pip install -e .
```

如果需要 texture，还要编译：

```bash
cd hy3dgen/texgen/custom_rasterizer
python3 setup.py install
cd ../../..
cd hy3dgen/texgen/differentiable_renderer
python3 setup.py install
```

最小 image-to-3D Python 调用：

```python
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline

pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained("tencent/Hunyuan3D-2")
mesh = pipeline(image="assets/demo.png")[0]
mesh.export("sample.glb")
```

最小 image-to-3D + texture 调用：

```python
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
from hy3dgen.texgen import Hunyuan3DPaintPipeline

shape = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained("tencent/Hunyuan3D-2")
mesh = shape(image="assets/demo.png")[0]

paint = Hunyuan3DPaintPipeline.from_pretrained("tencent/Hunyuan3D-2")
mesh = paint(mesh, image="assets/demo.png")
mesh.export("sample_textured.glb")
```

官方 API server 可启动：

```bash
python api_server.py --host 0.0.0.0 --port 8080
```

image-to-3D POST 示例可输出 GLB。**text-to-3D 不能按当前官方源码视为开箱即用**：README 写 API server 支持 Image/Text to 3D，但 `api_server.py` 中 text 分支调用 `self.pipeline_t2i(text)`，而 `pipeline_t2i = HunyuanDiTPipeline(...)` 初始化在源码中处于注释状态。因此 text-to-3D 至少需要额外启用/配置 HunyuanDiT text-to-image worker，再把生成图送入 image-to-3D；不宜承诺为本轮可复现 native text baseline。

## 权重、显存和磁盘成本

官方 README 声称 Hunyuan3D 2.0 shape generation 约需 `6GB VRAM`，shape+texture 总计约需 `16GB VRAM`。A100 显存本身应足够。

磁盘成本按官方模型表和 Hugging Face HEAD 只读探测估算：

- 完整 `tencent/Hunyuan3D-2` repo 文件合计约 `69.7GB`，因为仓库同时包含 normal/fast/turbo、多套 `.ckpt`/`.safetensors`、paint/turbo、delight、VAE 等重复权重。
- shape-only 的核心 `hunyuan3d-dit-v2-0/model.fp16.safetensors` 约 `4.6GB`；再加 `hunyuan3d-vae-v2-0` fp16 约 `0.6GB`、rembg/辅助模型和环境 cache，建议预留 `8-12GB`。
- shape+texture 再加 `Hunyuan3D-Paint-v2-0` 的 UNet safetensors 约 `3.4GB`、text encoder 约 `1.3GB`、image encoder/其他 texture 组件约 `1-2GB`；若还启用 delight，UNet 约 `3.2GB`。建议预留 `15-25GB`。
- 对照：`microsoft/TRELLIS.2-4B` HEAD 探测约 `14.5GB`，a100-2 当前 cache 实测约 `16GB`；`microsoft/TRELLIS-image-large` 约 `3.1GB`。

当前 a100-2 磁盘空间不是问题；主要成本是环境安装、CUDA/扩展编译、Hugging Face 下载时间，以及 text-to-3D 分支需要额外 T2I worker。

## TRELLIS / TRELLIS.2 ordinary baseline 的公平输入输出定义

### 输入

每个任务固定同一组输入，不能给 ours 和 ordinary baseline 不同目标：

- `reference_image`：同一张白底、无文字、同相机/尺度的 target/reference render。
- `text_prompt`：只作为 text-only 或 text-assisted row；不得替代 image row。
- `seed`：记录 seed；每个 method 使用同一 seed budget。
- `task_metadata`：类别、递归模式、depth/growth budget、root policy、camera、render setup。

### 输出

每个 `case x method x seed` 至少保存：

- mesh asset：`.glb` 优先，`.obj` 可接受；
- overview 白底 render；
- 至少两个真实 3D camera zoom render，不能用 2D crop 冒充；
- manifest：输入图、prompt、seed、model repo/cache path、命令、输出路径；
- metrics：connected components、largest component ratio、orphan/fragment ratio、vertices/faces、GLB import/render success、类别/结构 failure label。

### baseline 行定义

- **TRELLIS image one-shot**：`microsoft/TRELLIS-image-large`，输入同一 `reference_image`，输出 mesh/GLB/PLY。TRELLIS 官方支持 text 或 image prompts，并可输出 radiance fields、3D Gaussians 和 meshes；官方也建议 image-conditioned 版本通常表现更好。
- **TRELLIS text one-shot**：`microsoft/TRELLIS-text-xlarge`，输入同一 `text_prompt`。若 text 权重/env 不可用，标为 optional/blocked，不替代 image row。
- **TRELLIS.2 image one-shot**：`microsoft/TRELLIS.2-4B`，输入同一 `reference_image`，输出 PBR-ready `sample.glb`。当前 a100-2 已有 `16G` cache 和大量项目 TRELLIS.2 结果，是最公平且最可执行的 ordinary 3D generator baseline。
- **TRELLIS.2 text-assisted**：外部 T2I 先生成 reference image，再进 TRELLIS.2 image pipeline。必须标注为非 native TRELLIS.2 text-to-3D。
- **mesh-space trivial recursion**：先让 one-shot generator 生成 root mesh，再只在 mesh 空间做 transform-copy / merge / remesh；不得使用本文的 projection/admissibility/typed handle。
- **latent-space trivial recursion**：直接复制/变换 TRELLIS.2 sparse support 或 latent feature；不得使用本文的 per-depth projection、root reachability gate 或 masked realization。

## 论文中如何透明处理 Hunyuan

建议写为 planned/secondary baseline，而不是静默删除：

> We additionally audited Hunyuan3D 2.0 as a secondary image-to-3D baseline. Although its official shape and texture pipelines fit A100 memory budgets, the current project environment on a100-2 did not contain the Hunyuan3D repository, `hy3dgen` package, or cached weights. We therefore report it as a planned baseline and provide the official commands and resource estimate. The primary ordinary-generator comparison uses TRELLIS.2, whose 4B checkpoint cache and prior outputs are already present in the project environment.

如果表格中保留 Hunyuan 行：

- `Hunyuan3D image-to-3D`: `planned / blocked: install and weights missing in current a100-2 project environment`
- `Hunyuan3D image+texture`: `planned / blocked: requires paint pipeline and texture extension build`
- `Hunyuan3D text-to-3D`: `blocked-risk: official API text branch requires an additional T2I worker; current source does not enable it by default`

这样比删除该 baseline 更透明，也避免把未跑过的系统写成已完成实验。

## 需要引用的官方链接 / 论文

- Hunyuan3D 2.0 GitHub: https://github.com/Tencent-Hunyuan/Hunyuan3D-2
- Hunyuan3D 2.0 Hugging Face model: https://huggingface.co/tencent/Hunyuan3D-2
- Hunyuan3D 2.0 paper / project links: 以官方 GitHub README 中列出的 paper/project 为准。
- TRELLIS GitHub: https://github.com/microsoft/TRELLIS
- TRELLIS paper: https://arxiv.org/abs/2412.01506
- TRELLIS.2 GitHub: https://github.com/microsoft/TRELLIS.2
- TRELLIS.2 Hugging Face model: https://huggingface.co/microsoft/TRELLIS.2-4B
- TRELLIS.2 paper link from official README: https://arxiv.org/abs/2512.14692
