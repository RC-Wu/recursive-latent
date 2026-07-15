# Hunyuan Text-Root Mesh-Space Baseline Protocol (2026-05-11)

## 0. 为什么重做

之前的 Hunyuan 结果使用的是完整递归 guide image，一次性生成整棵树 / 晶格 / 珊瑚。这只能作为 ordinary one-shot image-to-3D baseline，不能公平代表用户要求的 mesh-space recursive route。

公平的 Hunyuan mesh-based baseline 必须是：

1. 用文本 prompt 生成一个可复用的 root primitive。
2. 用 Hunyuan3D shape pipeline 把该 root primitive 变成一个 root mesh。
3. 对同一个 root mesh 做传统 grammar 的缩放、旋转、平移、复制。
4. 直接 merge / concat mesh，并可额外报告一个轻度 smoothing 的 mesh-route upper-bound。

因此旧的 `publication_hunyuan_recursive_guides_20260510` 只能保留为 one-shot baseline / broad pool，不再用于证明 mesh-space recursion 的好坏。

## 1. 新 baseline 定义

脚本：

```text
assets/hunyuan_text_root_meshspace_baseline_20260511.py
```

输出目录：

```text
results/publication_hunyuan_text_root_meshspace_20260511/
```

链路：

```text
text prompt
-> HunyuanDiT text-to-image root primitive
-> background removal
-> Hunyuan3D 2.0 shape-only root GLB
-> deterministic S/R/T grammar instances
-> direct mesh concat
-> optional Laplacian smoothing row reported separately
```

禁止项：

- 不使用完整递归 guide image。
- root 之后不再调用 Hunyuan / TRELLIS / 任何生成模型。
- 不做 latent update。
- 不做 projection。
- 主 row 不做 weld / boolean / remesh / repair。
- smoothing row 只能写成 mesh-route upper-bound，不能和 direct row 混称。

## 2. Case 与 prompt

当前先跑三类主比较 case：

| case_id | family | prompt | grammar |
|---|---|---|---|
| `tree_trunk_branch` | L-system tree | `single upright cedar tree trunk with one forked branch segment, isolated 3D object` | `tree_branching` |
| `pyrite_crystal_root` | IFS crystal | `single faceted pyrite crystal block, isolated 3D object` | `pyrite_lattice` |
| `coral_branch_root` | DLA coral | `single smooth branching coral stem segment, isolated 3D object` | `coral_frontier` |

主文优先使用 `tree_trunk_branch` 展示用户关心的“先生成树干 root，再复制成递归树”的 mesh-route baseline；`pyrite/coral` 用来和已有非树优势 case 对齐。

## 3. 指标

主表必须同时报告：

- root 生成状态：prompt、root image、root GLB、root vertices/faces、root visual QA。
- mesh copy 状态：instance count、depth、copy repetition score。
- geometry：vertices、faces、file size MB。
- connectivity：raw face components、occupancy components 6N、occupancy LCR。
- route flags：`generator_calls_after_root=0`、`projection_used=0`、`latent_update_used=0`、`weld_boolean_or_remesh_used=0`。
- smoothing 区分：`post_copy_smoothing_iterations=0` 是正式 direct row；大于 0 是 upper-bound row。

解释规则：

- 高 occupancy LCR 不能自动代表成功；mesh-route 可能只是空间上接近但仍是重复 root islands。
- 高 raw component count 与 `copy_repetition_score=1.0` 是 mesh copy-paste 的核心失败证据。
- 如果视觉效果还可以，也只能说明 mesh-space copying can produce a plausible repeated object；不能说明它有 grammar-readable recursive state、typed handles、junction naturalization 或可继续局部递归。

## 4. 当前闭合状态（2026-05-11 05:36 CST）

远端：

```text
a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
```

环境：

```text
envs/hy3d_trellisclassic_probe_20260510/bin/python
```

GPU policy：

```text
CUDA_VISIBLE_DEVICES=4,5,6,7 only
```

本轮修复后的正式命令由下面脚本启动：

```text
assets/run_hunyuan_text_root_meshspace_after_weights_20260511.sh
```

关键修复：

- HunyuanDiT text-to-image 权重已完整放在：
  `weights/HunyuanDiT-v1.1-Diffusers-Distilled`。
- Hunyuan3D shape 权重使用本地 snapshot：
  `cache/huggingface/hub/models--tencent--Hunyuan3D-2/snapshots/9cd649ba6913f7a852e3286bad86bfa9a2d83dcf`。
- 当前 venv 缺 `sentencepiece/tiktoken`，已补齐。
- 当前 venv 与 TRELLIS2 base env 有混用，`torchvision::nms` 缺 operator；脚本和 baseline 内部注册了最小 stub，T2I/shape 已验证可跑。
- `rembg` 首次运行下载了 `u2net.onnx` 到 `/mnt/beegfs/ruocheng/.u2net/u2net.onnx`。

正式输出目录：

```text
results/publication_hunyuan_text_root_meshspace_20260511/
```

正式日志：

```text
logs/hunyuan_text_root_meshspace_autorun_20260511.log
```

闭合标记：

```text
[2026-05-11 05:32:13] AUTORUN_START ...
[2026-05-11 05:36:36] BASELINE_ALL_DONE
```

本地拉回的轻量 QA 目录：

```text
results/remote_pull_hunyuan_text_root_meshspace_20260511/
```

本地 contact sheet：

```text
results/remote_pull_hunyuan_text_root_meshspace_20260511/hunyuan_text_root_meshspace_contact_sheet_20260511.png
```

注意：contact sheet 是快速三视图 / root 图检查；论文最终图仍需用统一 Blender/论文渲染 pipeline 对 GLB 重新渲染和人工 QA。

## 5. 已验证输出

Fresh verification command on remote confirmed:

```text
manifest_rows 3 statuses ['ok']
metrics_rows 6 statuses ['fragmented_copy_paste', 'smoothed_copy_paste']
missing_or_empty 0
cases ['coral_branch_root', 'pyrite_crystal_root', 'tree_trunk_branch']
```

Root generation manifest:

| case_id | status | root faces | root GLB MB | T2I sec | shape sec |
|---|---:|---:|---:|---:|---:|
| `tree_trunk_branch` | ok | 2,440,474 | 41.873 | 12.50 | 15.65 |
| `pyrite_crystal_root` | ok | 738,700 | 12.681 | 12.02 | 14.44 |
| `coral_branch_root` | ok | 289,648 | 4.973 | 11.92 | 14.14 |

Mesh-space rows:

| case_id | row | faces | raw components | occupancy components | LCR | GLB MB |
|---|---|---:|---:|---:|---:|---:|
| `tree_trunk_branch` | direct | 156,000 | 153,608 | 40 | 0.9977 | 19.147 |
| `tree_trunk_branch` | laplacian3 | 156,000 | 153,608 | 56 | 0.9814 | 19.147 |
| `pyrite_crystal_root` | direct | 300,000 | 283,875 | 3 | 0.9293 | 36.953 |
| `pyrite_crystal_root` | laplacian3 | 300,000 | 283,875 | 3 | 0.9293 | 36.953 |
| `coral_branch_root` | direct | 252,000 | 213,465 | 3 | 0.9159 | 29.935 |
| `coral_branch_root` | laplacian3 | 252,000 | 213,465 | 3 | 0.9159 | 29.935 |

Interpretation gate:

- 这次可以正式说 Hunyuan fair mesh-space baseline 已经跑通并产出三类 case 的 root/mesh/metrics。
- direct rows 是论文主对比中的 mesh-space route；laplacian3 rows 是“简单平滑上界”，不能当成 learned recursion。
- raw component count 极高且 `copy_repetition_score=1.0`，是 mesh copy-paste 路线缺少连接/自然化/递归状态的主要负证据。
- occupancy LCR 在部分行很高，不能单独解释为成功，因为它只说明体素邻近连通，不能否定原始 mesh components 和重复 copy 的问题。

## 6. 仍需闭合的下一步

- 对拉回的 preview/contact sheet 做人工视觉选择；必要时对 root prompt/case 再跑一组 seed 扩展候选。
- 将 GLB/OBJ 拉入统一 Blender render pipeline，输出白底或论文风格对比图。
- 把 Hunyuan direct/smoothed rows 合并进 master baseline CSV/LaTeX table，和 TRELLIS2/ours 同表比较。
- 在正文中不要再使用旧 `publication_hunyuan_recursive_guides_20260510` 作为 mesh-space baseline；它只能作为 one-shot guide-image baseline。
- 若主文需要“每类至少 10 个可选 case”，本次只是三类主比较 seed 的闭合；还需要扩展 case pool。
