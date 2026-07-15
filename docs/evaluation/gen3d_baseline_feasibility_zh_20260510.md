# Gen-3D baseline 可行性盘点（2026-05-10）

## 结论摘要

本轮只做官方入口核对、环境盘点和协议设计，不下载大权重、不改 `paper_siga/main.tex`、不改 `assets/` 脚本。

| baseline | 官方能力 | 本项目当前可行性 | 风险/处理 |
|---|---|---|---|
| TRELLIS image-to-3D | 官方 `TrellisImageTo3DPipeline`，输出 gaussian/radiance_field/mesh，可导出 GLB/PLY | 远端已有 `microsoft/TRELLIS-image-large` cache；但默认 Python 包 `trellis` 未在 base Python 可见 | 可作为可跑候选；需要使用既有项目环境或重新定位旧实验 env，不应在本轮盲装 |
| TRELLIS text-to-3D | 官方 `TrellisTextTo3DPipeline`，`microsoft/TRELLIS-text-xlarge` | 未发现 text 权重 cache；官方也建议先 text-to-image 再 image model | 主表可列 native text baseline 为 blocked/optional；不应作为核心可交付依赖 |
| TRELLIS.2 image-to-3D | 官方 `Trellis2ImageTo3DPipeline`，输出 PBR mesh 和 `sample.glb` | 远端已有 `microsoft/TRELLIS.2-4B` cache 与大量项目结果；本项目已经有 TRELLIS.2 one-shot/recursive 结果 | 最可行；需要用项目既有运行环境而不是 base Python |
| TRELLIS.2 text-to-3D | 官方 README 当前只写 image-to-3D 与 shape-conditioned texture | 不存在 native text-to-3D 官方命令 | 协议中不得写成 TRELLIS.2 native text baseline；只能写 text-to-image 前端 + TRELLIS.2 image-to-3D，并标注非原生 |
| Hunyuan3D 2.0 image-to-3D | 官方 `Hunyuan3DDiTFlowMatchingPipeline` 返回 `trimesh`，可保存 GLB/OBJ；Gradio/API 也支持 image-to-3D | 本地只发现参考图；远端项目树和 HF cache 未发现 Hunyuan/HY3D；base Python `hy3dgen` 缺失 | 当前为 install-needed；除非找到已有轻量 env/cache，否则本轮表格写 blocked |
| Hunyuan3D 2.0 text-to-3D | 官方 API server 文档声称 Image/Text to 3D；源码 text 分支需要 `pipeline_t2i` | `api_server.py` 中 `pipeline_t2i` 初始化是注释状态，且会引入额外 HunyuanDiT T2I 权重 | 不作为可承诺 baseline；若论文要列 text row，写 blocked-risk fallback |

## 官方命令/API 核对

详细命令记录在 [docs/references/gen3d_official_baseline_commands_20260510.md](/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/references/gen3d_official_baseline_commands_20260510.md)。关键点：

- TRELLIS 官方 README 明确支持 text/image prompts，输出 Radiance Fields、3D Gaussians、meshes；示例导出 `sample.glb` 和 `sample.ply`。链接：https://github.com/microsoft/TRELLIS
- TRELLIS.2 官方 README 明确是 high-fidelity image-to-3D，使用 O-Voxel 和 PBR material，示例导出 `sample.mp4` 与 `sample.glb`。链接：https://github.com/microsoft/TRELLIS.2
- Hunyuan3D 2.0 官方 README 提供 diffusers-like Python API 和 API server；image API 输出 `trimesh`，API server `/generate` 可输出 GLB。链接：https://github.com/Tencent-Hunyuan/Hunyuan3D-2

## 环境盘点

### Local

本地项目 `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`：

- 存在大量 TRELLIS.2 相关脚本和结果，例如 `assets/trellis2_basic_smoke.py`、`assets/trellis2_texturing_export_glb.py`、`visuals/trellis2_*`、`results/strict_matched_root_stamped_20260510/anchor_plan.json`。
- 未发现 Hunyuan3D/HY3D 代码或权重；只发现参考图：
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/downloads/reference_figures/hunyuan3d2_system.jpg`
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/downloads/reference_figures/hunyuan3d2_arch.jpg`

### Remote `a100-2`

在一次只读 SSH 盘点中，远端 root `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507` 存在：

- `hf_home/hub/models--microsoft--TRELLIS.2-4B`
- `hf_home/hub/models--microsoft--TRELLIS-image-large`
- 多个 `results/trellis2_*` 输出目录，包含 `.obj` 与 preview。

未发现：

- Hunyuan/HY3D repo、cache 或结果目录。
- base Python 下 `trellis`、`trellis2`、`hy3dgen`、`hunyuan3d`、`diffusers` 可 import。

解释：TRELLIS.2 很可能依赖项目先前使用的 conda/env 或脚本注入路径；base Python import 缺失不能否定已有结果，但说明新 baseline 运行前必须定位既有 env。Hunyuan3D 则没有发现可复用安装痕迹。

## 安装/下载策略

1. TRELLIS.2：优先复用远端已有 `TRELLIS.2-4B` cache 和项目旧实验环境；不要重新下载 4B 权重。
2. TRELLIS image：远端已有 `TRELLIS-image-large` cache，可在找到旧 env 后做 one-shot image baseline；text 权重未见 cache，不列为 P0。
3. Hunyuan3D 2.0：当前需要 install + weight cache。官方 VRAM 需求看似可控，但权重与依赖下载不属于本轮轻量路径；若没有外部确认的既有 env/cache，状态写 `blocked: install/weights missing`。
4. Hunyuan text：除安装外还需要确认 HunyuanDiT T2I worker；官方源码里 text 分支不是开箱即用，应写为 blocked-risk。

## 可执行优先级

| 优先级 | 项 | 原因 |
|---|---|---|
| P0 | TRELLIS.2 image one-shot vs ours | 已有 cache/结果基础，最贴近论文 generator substrate |
| P0 | TRELLIS.2 + mesh-space grammar / trivial sparse-latent recursion | 不需要新外部模型；能直接回答“普通递归/mesh 后处理是否足够” |
| P1 | TRELLIS image one-shot | 官方命令清楚，远端有 image-large cache，但要定位 env |
| P2 | TRELLIS text one-shot | 官方支持但官方自己建议 image-conditioned 更好，且 text 权重未确认 |
| P2/blocked | Hunyuan3D image one-shot | 对 reviewer 有价值，但当前无安装/权重 |
| blocked | Hunyuan3D text-to-3D | API 文档声称支持，源码 text worker 未启用，且额外 T2I 权重未就绪 |

## 论文写法边界

- 可以写“TRELLIS.2 one-shot image-to-3D 是最强且最公平的普通 gen-3D baseline 候选”。
- 不能写“Hunyuan3D 已经可跑”。
- 不能写“TRELLIS.2 官方支持 text-to-3D”；只能写“若需要 text prompt，使用外部 T2I 生成 target image 后进入 TRELLIS.2 image-to-3D，作为非原生辅助设置”。
- 对 Hunyuan 行，主文表格应保留明确的 blocked/fallback 说明，而不是静默删除。
