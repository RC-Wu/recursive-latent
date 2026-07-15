# Gen-3D baseline 对比协议（2026-05-10）

## 目标

用最小但严格的矩阵回答一个问题：普通 one-shot 3D generation，以及在输出 mesh 或 sparse latent 上做平凡递归复制，是否能解决本文的受控递归 3D asset 生成任务。

本协议只覆盖 Lane A，不改 `paper_siga/main.tex`，不改 `assets/` 脚本，不下载新大权重。

## 两个受控 case

### Case A：branching vine/root or tree crown

任务语义：递归分叉、局部 junction、terminal tips、root reachability。

输入统一：

- target/reference image：使用同一个传统 L-system/space-colonization 或 ours rendered target，白底、无文字、正交相机。
- text prompt：`a recursive branching vine root structure with repeated fork junctions and fine terminal tips, isolated on a white background`。
- ours root：优先使用已有 vine/tree 正例，例如 `vine_stage5_warm` 或 same-root `proposed_connected/vine`。

必须检查的局部区域：

- root/seed attachment；
- primary branch junction；
- terminal tip cluster；
- second-level zoom 中 junction 是否仍保持分叉结构而不是 sheet/blob。

### Case B：crystal / recursive lattice / coral-like frontier

任务语义：transform-copy、lattice symmetry、frontier attachment、non-tree recursive asset。

输入统一：

- target/reference image：优先选 pyrite/bismuth lattice 正例；若用 coral，则写明是 frontier/attachment asset，不声称物理 DLA 复现。
- text prompt：`a recursive crystal lattice or coral-like frontier scaffold with repeated local motifs, connected structure, sharp details, isolated on a white background`。
- ours root：优先使用已有 `pyrite_lattice_hq`、`bismuth` 或 connected coral positive/boundary positive。

必须检查的局部区域：

- lattice/facet contact；
- repeated motif orbit；
- cavity/frontier contact；
- second-level zoom 中 motif 是否保留而不是被 one-shot 先验平均掉。

## 方法矩阵

| method | 输入 | 执行 | 输出 | 状态策略 |
|---|---|---|---|---|
| TRELLIS one-shot image | target/reference image | `TrellisImageTo3DPipeline.from_pretrained("microsoft/TRELLIS-image-large")` | `sample.glb`, `sample.ply`, `sample_mesh.mp4` 等 | 可行但需定位 env；远端已有 image-large cache |
| TRELLIS one-shot text | text prompt | `TrellisTextTo3DPipeline.from_pretrained("microsoft/TRELLIS-text-xlarge")` | 同上 | optional/blocked；text 权重未确认，官方也建议 image-first |
| TRELLIS.2 one-shot image | target/reference image | `Trellis2ImageTo3DPipeline.from_pretrained("microsoft/TRELLIS.2-4B")` | `sample.mp4`, PBR-ready `sample.glb` | P0；远端已有 4B cache 和项目经验 |
| TRELLIS.2 text-assisted | text prompt 先经外部 T2I 成图 | 外部 T2I image -> TRELLIS.2 image pipeline | `sample.glb` | 非 native；不得写成官方 text-to-3D |
| Hunyuan3D 2.0 one-shot image | target/reference image | `Hunyuan3DDiTFlowMatchingPipeline.from_pretrained("tencent/Hunyuan3D-2")` | `trimesh` -> `.glb/.obj` | 当前 blocked: no local/remote install/cache |
| Hunyuan3D 2.0 image+texture | target/reference image | shape pipeline + `Hunyuan3DPaintPipeline` | textured `.glb` | blocked until install/cache exists |
| Hunyuan3D 2.0 text/API | text prompt | API server `/generate` text path | `.glb` | blocked-risk；官方源码 text worker 需额外 T2I 初始化 |
| mesh-space trivial recursion | one-shot root mesh | decode/generate root mesh, apply recursive transforms in mesh space, merge/remesh only | `.obj/.glb` | 必跑；用来证明 mesh 后处理不是本文方法 |
| latent-space trivial recursion | TRELLIS.2 sparse support/features | 直接 copy/transform support 或 latent features，不做 projection-stabilized grammar semantics | decoded `.obj/.glb` | 必跑；用来证明平凡 latent transform 会传播碎片/handle 污染 |
| Ours / PS-RSLG | same root/category/grammar | per-depth rule proposal + masked realization + projection/admissibility + re-encode | `.glb/.obj`, white renders | 主方法 |

官方命令/API 见 [docs/references/gen3d_official_baseline_commands_20260510.md](/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/references/gen3d_official_baseline_commands_20260510.md)。

## 公平性控制

1. 每个 case 使用同一 target/reference image；text row 只作为辅助，不替代 image row。
2. one-shot baseline 只允许一次完整对象生成，不允许人工选局部再拼接。
3. mesh-space trivial recursion 只能用输出 mesh 做 transform-copy、merge、可记录的 remesh/smooth；不能调用 generator 做 per-depth projection 或 masked latent naturalization。
4. latent-space trivial recursion 只能做直接 sparse/feature copy-transform 或 direct edit；不能使用本文的 typed handles、admissibility projection、root reachability gate。
5. ours 使用同一 case/root/category，depth 和 growth budget 必须写入表格。
6. 所有正式视觉结果必须是 mesh/textured mesh render，白底、无平台、无图内文字；matplotlib/point cloud 只作诊断。

## 输出契约

每个 `case x method x seed` 保存：

- mesh asset：`.glb` 优先，`.obj` 可接受；
- overview 白底 render；
- 至少两级 camera zoom render，不使用 2D crop 冒充 zoom；
- manifest：输入图、prompt、seed、model path、commit/command、输出路径；
- metrics JSON/CSV。

建议目录：

```text
results/gen3d_baselines_20260510/
  case_branching_vine/
    trellis_image_seed001/
    trellis2_image_seed001/
    hunyuan_image_seed001_blocked/
    mesh_space_trivial_seed001/
    latent_trivial_seed001/
    ours_psrslg_seed001/
  case_pyrite_lattice_or_coral/
    ...
```

## 指标

通用 mesh/asset 指标：

- vertices；
- faces；
- GLB/OBJ file size；
- connected components；
- largest component ratio；
- orphan/fragment ratio；
- nonmanifold/degenerate faces；
- Blender import/render success；
- texture/PBR usable flag。

递归结构指标：

- Case A：tip count、branch node count、path-to-root rate、junction survival、branch length/angle distribution；
- Case B：motif count、transform orbit error、symmetry/contact consistency、cavity/frontier attachment survival；
- zoom retention：overview、zoom_01、zoom_02 的 terminal detail proxy 和 CLIP/DINO consistency 只作辅助，不替代拓扑指标。

状态 flag：

- `success`：输出 mesh 可导入、可渲染、指标完整；
- `blocked`：安装/权重/API 失败，必须记录 exact reason；
- `fragmented`：生成有输出但 component/orphan 指标失败；
- `category mismatch`：生成对象不是任务类别；
- `not texture/PBR usable`：geometry 可用但 texture/export 失败；
- `diagnostic only`：点云、matplotlib 或非 mesh 结果。

## blocked-risk fallback rows

| row | 触发条件 | 表格写法 | fallback |
|---|---|---|---|
| TRELLIS text | text weights/env 不可用，或输出明显弱于 image baseline | `blocked/optional: TRELLIS text-xlarge cache/env not available; official README recommends image-conditioned route` | 保留 TRELLIS image row |
| TRELLIS.2 text | 需要 native text-to-3D | `not applicable: no official native TRELLIS.2 text-to-3D command found` | 用 external T2I -> TRELLIS.2 image，标为 text-assisted |
| Hunyuan image | 未发现 `hy3dgen`、repo 或 HF cache | `blocked: install/weights missing; no large download in this lane` | 不删行；继续 TRELLIS/TRELLIS.2 与 mesh/latent trivial comparisons |
| Hunyuan text | API text path 需要额外 `pipeline_t2i` | `blocked-risk: official API text branch requires extra T2I worker not enabled in current source` | 只保留 image row 或 blocked row |
| one-shot category mismatch | 生成 chair/toy/object 而非递归结构 | `category mismatch` | 不手工挑最好视角掩盖；保留失败图和指标 |
| mesh-space trivial output fragmented | merge/remesh 后碎片多 | `fragmented` | 正是负例，进入 appendix 或主文失败列 |
| latent trivial output invalid | direct support/feature transform 解码失败或 orphan handles 爆炸 | `fragmented/diagnostic only` | 记录 failure，和 PS-RSLG per-depth projection 对比 |

## 主文最小汇报

主文只需要两行 case、四到五列方法：

1. TRELLIS.2 one-shot image；
2. strongest available external one-shot baseline：TRELLIS image 或 Hunyuan image blocked row；
3. mesh-space trivial recursion；
4. latent-space trivial recursion；
5. Ours / PS-RSLG。

Hunyuan 若仍 blocked，不应静默删除；表格保留状态和原因，附录给官方命令与本项目环境盘点。
