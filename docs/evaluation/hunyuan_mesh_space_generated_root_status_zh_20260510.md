# Hunyuan mesh-space generated-root baseline 状态（2026-05-10）

## 0. 结论

Hunyuan3D 2.0 的 `mesh-space generated-root` 负控已完成 vine / pyrite / coral 三个主 comparison case。

这个结果只闭合一个非常具体的负控：先用 Hunyuan shape-only image one-shot 得到 root mesh，再按传统 grammar 的 S/R/T 规则复制 root，最后直接 concat mesh。它不调用 Hunyuan 生成新局部，不做 latent update，不做 projection，不做 weld / boolean / remesh / repair。

因此它可以支持“直接在 mesh space 复制 generated root 并不能提供 grammar-owned recursive state / naturalized junction”的论证；不能写成 Hunyuan 递归生成成功或失败的总判定。

## 1. 输出路径

脚本：

```text
assets/hunyuan_mesh_space_generated_root_20260510.py
```

输出目录：

```text
results/publication_hunyuan_mesh_space_20260510/
```

核心文件：

- `results/publication_hunyuan_mesh_space_20260510/hunyuan_mesh_space_metrics.csv`
- `results/publication_hunyuan_mesh_space_20260510/hunyuan_mesh_space_metrics.json`
- `results/publication_hunyuan_mesh_space_20260510/manifest.csv`
- `results/publication_hunyuan_mesh_space_20260510/summary.json`

已同步进 master baseline：

- `results/publication_baseline_metrics_20260510/publication_baseline_master_manifest_20260510.csv`
- `results/publication_baseline_metrics_20260510/publication_baseline_table_draft_20260510.tex`

## 2. Baseline 定义

每个 case 的 root mesh 来自 Hunyuan full-pool shape-only GLB：

- vine: `results/publication_hunyuan_recursive_guides_20260510/vine_lsystem_grammar/vine_lsystem_grammar_hunyuan_steps30_oct320.glb`
- pyrite: `results/publication_hunyuan_recursive_guides_20260510/pyrite_lattice/pyrite_lattice_hunyuan_steps30_oct320.glb`
- coral: `results/publication_hunyuan_recursive_guides_20260510/coral_frontier/coral_frontier_hunyuan_steps30_oct320.glb`

统一设置：

- `depth=2`
- `variant=full_srt`
- `max_root_faces=8000`
- direct concat triangle mesh
- output OBJ + white PBR GLB + white preview PNG
- no generator / no projection / no weld / no boolean / no remesh / no repair

## 3. 指标摘要

| case | grammar | instances | vertices | faces | GLB MB | raw comps | occ comps 6N | occ LCR | status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| vine | `vine_tree` | 13 | 309764 | 104000 | 12.783 | 101985 | 885 | 0.843 | `fragmented_copy_paste` |
| pyrite | `pyrite_lattice` | 25 | 599000 | 200000 | 25.135 | 199050 | 15 | 0.965 | `fragmented_copy_paste` |
| coral | `coral_frontier_branch` | 21 | 500535 | 168000 | 20.775 | 165123 | 50 | 0.998 | `fragmented_copy_paste` |

解释边界：

- `raw_component_count` 极高，说明 direct concat 后仍是大量 root-copy face islands。
- `occupancy LCR` 在 pyrite/coral 很高，不能单独解释为成功；它只是低分辨率 voxel occupancy proxy 中大部分 vertices 落在相邻 occupied cells。
- 关键失败标签不是“无法导入 mesh”，而是 `copy_repetition_score=1.0`、无 junction naturalization、无 projection、无 typed handles、无可继续执行的 recursive state。

## 4. Claim gate

可以写：

- Hunyuan shape-only one-shot root mesh 可以被传统 grammar 直接复制合并，形成一个可导入的 mesh-space negative control。
- 该 direct-copy baseline 在三个主 comparison case 中都保留高 raw face island count 与 copy repetition，本质上只是重复 root mesh。
- 这个负控补齐了 `Hunyuan + mesh-space generated-root` 行，可与 Trellis2 mesh-space generated-root 一起说明 naive mesh-space recursion 的局限。

不能写：

- 不能写 Hunyuan 递归生成失败或 Hunyuan 模型整体弱。
- 不能写 Hunyuan shape-only one-shot 具有递归语义、root reachability 或 grammar-readable state。
- 不能把高 occupancy LCR 当作成功；必须同时报告 raw components、copy repetition 和 no projection/repair。
- 不能把该 row 混同为 Hunyuan texture baseline；texture / paint pipeline 仍未完成。
