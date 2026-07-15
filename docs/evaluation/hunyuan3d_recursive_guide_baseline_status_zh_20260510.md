# Hunyuan3D recursive guide baseline 接收 / QA / 论文可写状态（2026-05-10）

## 0. 结论

Hunyuan3D 2.0 的状态已经从“feasibility / blocked”推进到 **shape-only baseline 可运行，且 13 个 recursive guide case 已在远端产出 GLB 与基础 mesh 指标**。

但它还不是完整论文 baseline。当前证据链必须分成三层：

1. **环境 / 权重 / load / generate smoke OK**：repo、`hy3dgen` shape pipeline import、项目本地 HF cache、权重 load、官方 demo 低成本 generate smoke 均已通过。
2. **13 例 recursive guide shape-only GLB 已产出**：覆盖 L-system、IFS、DLA/frontier、space-colonization 等 guide；均使用同一 Hunyuan shape-only 设置导出 `.glb`，并记录 vertices / faces / file size / seed。
3. **本地接收和 import QA 已完成**：13/13 GLB 已拉回本地，`trimesh.load(..., force="scene")` 均 OK；前三例已完成白底 render/contact-sheet QA。
4. **后续论文级扩展项仍需谨慎拆分**：full-pool render QA/contact sheet 已补齐，Hunyuan+mesh-space generated-root 负控已补齐并合入 master baseline；仍缺 texture / paint baseline、Hunyuan one-shot 的 connectivity/occupancy/failure label 定量、以及正文级 failure-label 解释。

## 1. 已完成证据

环境和 smoke：

- Hunyuan repo / package / shape-only dependency/import blockers 已解决。
- shape pipeline full weight-load smoke 完成：`HUNYUAN_FULL_LOAD_OK seconds 2215.33`，`device cuda dtype torch.float16`。
- 官方 demo image-to-shape smoke 完成并已本地复制：
  - `results/remote_smoke_20260510/hunyuan_shape_demo_lowcost/hunyuan_demo_lowcost_steps8_oct192.glb`
  - vertices `90297`，faces `180598`，GLB size `3.101 MB`
  - settings: `num_inference_steps=8`，`octree_resolution=192`，`num_chunks=4000`，seed `12345`
  - local `trimesh` scene import OK，geometry count `1`

三例 recursive guide batch：

- remote result root: `results/publication_hunyuan_recursive_guides_20260510/`
- batch outputs:
  - `vine_lsystem_grammar/vine_lsystem_grammar_hunyuan_steps30_oct320.glb`
  - `pyrite_lattice/pyrite_lattice_hunyuan_steps30_oct320.glb`
  - `coral_frontier/coral_frontier_hunyuan_steps30_oct320.glb`
  - per-case `*_metrics.json`
  - `hunyuan_recursive_guides_batch_metrics.csv`
  - `hunyuan_recursive_guides_batch_metrics.json`

Full-pool 13-case batch：

- reusable script: `assets/hunyuan_recursive_guides_batch_20260510.py`
- remote script: `cache/tmp/hunyuan_recursive_guides_batch_20260510.py`
- remote/local output root: `results/publication_hunyuan_recursive_guides_20260510/`
- merged metrics:
  - `hunyuan_recursive_guides_fullpool_metrics.csv`
  - `hunyuan_recursive_guides_fullpool_metrics.json`
- local import QA:
  - `local_trimesh_import_qa_fullpool_20260510.json`
  - result: `13/13` GLB import OK, each with `geometry_count=1`
- first local render QA:
  - `render_qa_white_900/flattened_white/`
  - `hunyuan_recursive_guides_white_contact_20260510.png`
  - note: raw Blender PNGs are transparent; use `flattened_white/` images or the contact sheet for white-background QA.
- full-pool render QA:
  - `render_qa_fullpool_white_600/flattened_white/`
  - `render_qa_fullpool_white_600_summary.json`
  - `hunyuan_recursive_guides_fullpool_white_contact_20260510.png`
- Hunyuan mesh-space generated-root negative control:
  - script: `assets/hunyuan_mesh_space_generated_root_20260510.py`
  - outputs: `results/publication_hunyuan_mesh_space_20260510/`
  - status doc: `docs/evaluation/hunyuan_mesh_space_generated_root_status_zh_20260510.md`
- Hunyuan one-shot topology / failure-label proxy:
  - metrics: `results/publication_hunyuan_recursive_guides_20260510/hunyuan_fullpool_topology_metrics_20260510.csv`
  - labels: `results/publication_hunyuan_recursive_guides_20260510/hunyuan_fullpool_failure_labels_20260510.csv`
  - script: `assets/hunyuan_failure_label_summary_20260510.py`
- master baseline merge:
  - `results/publication_baseline_metrics_20260510/publication_baseline_master_manifest_20260510.csv`
  - `results/publication_baseline_metrics_20260510/publication_baseline_table_draft_20260510.tex`
  - Hunyuan one-shot rows now read `generated_import_render_QA_pending_topology_metrics` and include raw component count, occupancy component count, LCR, and failure label for vine/pyrite/coral.
  - Hunyuan mesh-space rows now read `fragmented_copy_paste`.

## 2. 三例关键数字

统一设置：shape-only Hunyuan3D 2.0；`num_inference_steps=30`，`octree_resolution=320`，`num_chunks=12000`，`guidance_scale=5.0`，base seed `20260510`，输出类型 `trimesh`，GLB 导出。

| case | input guide | seed_used | vertices | faces | GLB MB | elapsed | 状态 |
|---|---|---:|---:|---:|---:|---:|---|
| `vine_lsystem_grammar` | `V23_lsystem_vine_grammar_pbr_guide.png` | `20260510` | `745382` | `1484726` | `25.522` | `15.16s` | shape-only GLB produced |
| `pyrite_lattice` | `V23_ifs_lattice_pyrite_pbr_guide.png` | `20260511` | `2058208` | `4119162` | `70.695` | `16.59s` | shape-only GLB produced |
| `coral_frontier` | `V23_dla_coral_frontier_pbr_guide.png` | `20260512` | `837923` | `1675900` | `28.769` | `14.89s` | shape-only GLB produced |

## 2.5 Full-pool 13-case 数字

同一设置下，13 个 guide case 已全部完成，状态均为 `ok`：

| case | seed_used | vertices | faces | GLB MB | skipped existing |
|---|---:|---:|---:|---:|---|
| `branch_ornament` | `20260515` | `645778` | `1284416` | `22.090` | false |
| `branch_tree` | `20260516` | `571112` | `1133892` | `19.513` | false |
| `bush_shell` | `20260520` | `603547` | `1207092` | `20.722` | false |
| `coral_frontier` | `20260512` | `837923` | `1675900` | `28.769` | true |
| `crystal_frontier` | `20260513` | `603372` | `1206740` | `20.716` | false |
| `frontier_sheet` | `20260514` | `603748` | `1207488` | `20.729` | false |
| `pine_grammar` | `20260518` | `603556` | `1207108` | `20.722` | false |
| `pyrite_lattice` | `20260511` | `2058208` | `4119162` | `70.695` | true |
| `radial_ornament` | `20260517` | `671760` | `1334676` | `22.963` | false |
| `root_fan_grammar` | `20260519` | `603644` | `1207276` | `20.725` | false |
| `root_network` | `20260521` | `690084` | `1372808` | `23.609` | false |
| `tree_crown` | `20260522` | `621097` | `1234552` | `21.237` | false |
| `vine_lsystem_grammar` | `20260510` | `745382` | `1484726` | `25.522` | true |

文件大小交叉核对：

- `vine_lsystem_grammar` GLB: `26762120` bytes，约 `26M`
- `pyrite_lattice` GLB: `74129268` bytes，约 `71M`
- `coral_frontier` GLB: `30166696` bytes，约 `29M`

## 3. 论文 claim gate

可以写：

- Hunyuan3D 2.0 已完成 shape-only 环境、权重 load、官方 demo generate smoke。
- 在同一批 recursive guide 输入上，Hunyuan shape-only baseline 已为 vine / pyrite / coral 三例导出 GLB，并有基础 geometry 指标。
- 在 13 个 guide 输入上，Hunyuan shape-only baseline 已导出 GLB，并有本地 import QA；这可以作为 secondary ordinary image-to-3D baseline 的 generated pool，替代旧文档中“repo/package/weights missing, planned/blocked”的绝对表述。
- Hunyuan 作为 one-shot shape generator，可用于检查普通 3D 生成器在 recursive guide image 上是否能合成单体形状。
- 前三例白底 contact sheet 可作为视觉 QA 草图；它显示 one-shot Hunyuan 会生成可导入 mesh，但不是 grammar-readable recursive state。

不能写：

- 不能写 Hunyuan baseline 已完整闭合，或已进入主表最终比较。
- 不能写 Hunyuan 失败、弱于/强于 PS-RSLG，直到 full-pool render QA、connectivity/occupancy metrics、failure labels 与同协议 comparison merge 完成。
- 不能写 Hunyuan texture baseline 已完成；当前三例是 shape-only GLB，不是 image+texture / paint pipeline。
- 不能写 Hunyuan text-to-3D 已复现；当前是 image guide to shape。
- 不能把 Hunyuan shape-only 的 vertices/faces/MB 解释为 recursive semantics、root reachability、可继续执行 grammar state 或 topology correctness。
- 不能把这三例当作完整 10-case pool；它们只是 vine / pyrite / coral 三个主 comparison case 的 first pass。

## 4. 下一步本地 QA 清单

1. **failure label 人工审阅**：当前 labels 是 topology proxy + first visual-note 草稿；进入论文前仍需对 full-pool contact sheet 做人工确认。
2. **texture baseline**：单独评估 Hunyuan image+texture / paint pipeline；当前不能混入 shape-only 行。
3. **正文表筛选**：主文建议只保留 pyrite、coral，vine 作为可选第三例；13-case Hunyuan pool 放 appendix/secondary table。

## 5. 当前论文表格建议

在主表或附录表中保留 Hunyuan 行时，建议临时状态如下：

| method row | vine | pyrite | coral | claim-safe status |
|---|---|---|---|---|
| Hunyuan3D shape-only image one-shot | GLB/import/render QA first pass done | GLB/import/render QA first pass done | GLB/import/render QA first pass done | secondary baseline generated; full-pool render/failure labels pending |
| Hunyuan3D image+texture | missing | missing | missing | blocked / not run |
| Hunyuan3D + mesh-space generated-root | missing | missing | missing | requires Hunyuan root mesh local QA first |

旧的 `planned / blocked: install and weights missing` 口径应更新为：**shape-only install/weights/load/generate 已通过；formal recursive guide 13-case pool 已生成并本地 import QA；full-pool render/failure labels、texture、mesh-space rows 仍未闭合。**
