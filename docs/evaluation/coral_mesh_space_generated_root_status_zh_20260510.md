# Coral mesh-space generated-root baseline 状态（2026-05-10）

本文件对应 R-SLG Lane B 的 coral mesh-space generated-root 缺口闭合。全程本地执行，无 SSH/远端操作，未修改 `paper_siga/main.tex` 或 Ralph 总计划。

## 1. 输入定位

优先使用与已有 vine/pyrite generated-root baseline 同口径的 Trellis2 one-shot coral root：

```text
visuals/gen3d_baseline_trellis2_one_shot_more_20260510/coral_one_shot_iso_seed612_steps8_nopre/trellis2_dinov3_min.obj
```

该 root 本地存在，文件大小约 72 MB。脚本记录的源 mesh 为：

- source vertices: 944056
- source faces: 1917216
- used root vertices: 35914
- used root faces: 12000
- face limited: true

`max_root_faces=12000` 与已有 mesh-space protocol 一致，只是 deterministic face subset + compact，用于让本地负控可运行；不是修复、生成或自然化。

## 2. 本轮输出

脚本：

```text
assets/coral_mesh_space_generated_root_20260510.py
```

输出目录：

```text
results/publication_coral_mesh_space_20260510/
```

核心文件：

- `results/publication_coral_mesh_space_20260510/manifest.csv`
- `results/publication_coral_mesh_space_20260510/coral_mesh_space_metrics.csv`
- `results/publication_coral_mesh_space_20260510/coral_mesh_space_metrics.json`
- `results/publication_coral_mesh_space_20260510/summary.json`

每个 row 都输出：

- OBJ: `<grammar>/<variant>/depth_XX/*.obj`
- white PBR GLB: `<grammar>/<variant>/depth_XX/*_white_pbr.glb`
- mesh preview PNG: `<grammar>/<variant>/depth_XX/*_white_preview.png`

## 3. Baseline 定义

本 baseline 是负控，只做：

1. 读取现有 Trellis2 coral one-shot root mesh。
2. 归一化 root。
3. 对 root 应用传统 S/R/T 复制变换。
4. 直接 concat triangle mesh。
5. 导出 OBJ/GLB/PNG 并计算 metrics。

明确不做：

- Trellis2/Hunyuan 或任何 generator 调用；
- latent update；
- projection / root reachability repair；
- mesh weld；
- boolean union；
- remesh / voxel close / hole fill；
- post-hoc naturalization。

脚本中每行写入：

- `copy_repetition_score=1.0`
- `latent_or_mesh_repair_used=0`
- `projection_used=0`
- `weld_boolean_or_remesh_used=0`

## 4. 生成矩阵

本轮生成 12 行：

| grammar | variant | depth | instance count |
| --- | --- | ---: | ---: |
| `coral_frontier_branch` | `full_srt` | 0/1/2 | 1 / 5 / 21 |
| `coral_frontier_branch` | `no_scale` | 0/1/2 | 1 / 5 / 21 |
| `coral_sheet_lattice` | `full_srt` | 0/1/2 | 1 / 5 / 13 |
| `coral_sheet_lattice` | `no_scale` | 0/1/2 | 1 / 5 / 13 |

推荐补入主表的 row 是：

```text
coral_frontier_branch full_srt depth=2 direct merge
```

理由：它最接近 coral/frontier 递归分叉任务，同时与已有 vine/pyrite `full_srt depth=2 direct merge` 口径一致。

## 5. 核心指标

推荐主表 row：

| case | method | variant | V | F | file MB | raw comps | occ comps 6N | occ LCR | status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| coral | Mesh-space generated-root baseline | coral_frontier_branch full_srt depth=2 direct merge | 754194 | 252000 | 31.281 | 250404 | 8 | 0.992 | fragmented_copy_paste |

对照 row：

| variant | depth | instances | raw comps | occ comps 6N | occ LCR | note |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| frontier full_srt | 2 | 21 | 250404 | 8 | 0.992 | 主推荐负控；raw face islands 极高 |
| frontier no_scale | 2 | 21 | 250404 | 10 | 0.996 | 禁用 scale 不改变 copy-paste 本质 |
| sheet full_srt | 2 | 13 | 155012 | 10 | 0.433 | occupancy 也明显破碎 |
| sheet no_scale | 2 | 13 | 155012 | 1 | 1.000 | 只说明 bbox voxel proxy 连通；仍是 direct repeated root copies |

解释边界：

- Raw face component 数极高，是 direct concat 后 face-level islands 的强诊断。
- Occupancy LCR 在部分 rows 很高，不能单独解释为递归任务成功。它只说明低分辨率 vertex occupancy proxy 中主体相邻或近邻。
- 本 baseline 没有生成新局部结构，也没有接缝自然化；`copy_repetition_score=1.0` 是关键负控标记。

## 6. Claim gates

可以写：

- Coral mesh-space generated-root baseline 已有本地输出、manifest 和 metrics。
- 该 baseline 直接复制 Trellis2 coral one-shot root mesh，经 S/R/T 实例化后 direct merge；无 generator、无 projection、无 weld/repair。
- 推荐 row `coral_frontier_branch full_srt depth=2 direct merge` 的 raw components=250404，说明 face-level copy-paste fragmentation 极强。
- 该 row 的 occupancy comps=8、occ LCR=0.992；因此不能用 occupancy LCR 单独声明失败，必须结合 raw face islands、copy repetition 和 visual QA。

不能写：

- 不能写 mesh-space coral 已通过递归生成任务。
- 不能把 `coral_sheet_lattice no_scale depth=2` 的 occ LCR=1.0 写成成功；它仍是 direct repeated root copy。
- 不能写该 baseline 使用了 naturalization、projection、repair 或 learned recursion。
- 不能把 raw face components 当作唯一视觉失败指标；主文应同时报告 render/import success、occupancy proxy、copy repetition 和人工 visual QA。

## 7. 可接入主 manifest 的行

Lane B master manifest 后续可追加：

```csv
case,method,variant,status,asset_path,source_path,render_path,manifest_path,notes
coral,Mesh-space generated-root baseline,coral_frontier_branch full_srt depth=2 direct merge,fragmented_copy_paste,results/publication_coral_mesh_space_20260510/coral_frontier_branch/full_srt/depth_02/coral_frontier_branch_full_srt_depth_02_white_pbr.glb,results/publication_coral_mesh_space_20260510/coral_frontier_branch/full_srt/depth_02/coral_frontier_branch_full_srt_depth_02.obj,results/publication_coral_mesh_space_20260510/coral_frontier_branch/full_srt/depth_02/coral_frontier_branch_full_srt_depth_02_white_preview.png,results/publication_coral_mesh_space_20260510/manifest.csv,Generated-root coral one-shot mesh copied by S/R/T and directly concatenated; no repair or projection.
```

本轮没有更新 `results/publication_baseline_metrics_20260510/`，因为当前任务独占写入范围不包含该目录。
