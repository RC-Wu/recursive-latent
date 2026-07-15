# Same-root / same-depth baseline matrix 20260509

范围：本地 CPU 第一版；没有 SSH、远端或 GPU；没有修改 `paper_siga/main.tex`。

输出目录：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/baseline_matrix_seed_20260511`

Contact sheet：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/baseline_matrix_seed_20260511/contact_sheet_final_depth.png`

## 协议

- Cases：`tree`, `root`, `vine`。
- Methods：传统 `lsystem`、传统 `space_colonization`、`proposed_connected` projection-positive scaffold。
- Same-root：每个 case/method/depth 都从 `(0, 0, 0)` root anchor 出发。
- Same-seed：`20260511`，脚本内部只加固定 case/method offset，避免 Python hash 随进程漂移。
- Same-depth：`1..4`；CSV 每行都记录 `same_max_depth=4`。
- Same renderer：最终深度全部用同一个 mesh renderer 生成 `contact_sheet_final_depth.png`，不是点云 scatter。

## 最终深度指标

| case | method | occ comp 6N | occ LCR | root ratio | tips | branch nodes | mesh comps |
|---|---|---:|---:|---:|---:|---:|---:|
| tree | lsystem | 1 | 1.0000 | 1.0000 | 27 | 13 | 3 |
| tree | space_colonization | 1 | 1.0000 | 1.0000 | 64 | 47 | 1 |
| tree | proposed_connected | 1 | 1.0000 | 1.0000 | 9 | 4 | 1 |
| root | lsystem | 1 | 1.0000 | 1.0000 | 27 | 13 | 1 |
| root | space_colonization | 1 | 1.0000 | 1.0000 | 69 | 46 | 4 |
| root | proposed_connected | 1 | 1.0000 | 1.0000 | 7 | 3 | 1 |
| vine | lsystem | 1 | 1.0000 | 1.0000 | 4 | 3 | 1 |
| vine | space_colonization | 1 | 1.0000 | 1.0000 | 70 | 42 | 1 |
| vine | proposed_connected | 1 | 1.0000 | 1.0000 | 6 | 4 | 1 |

## 第一版结论

- `proposed_connected` 在三个 case 的最终深度保持 root-attached occupancy：tree=1/1.000, root=1/1.000, vine=1/1.000。
- 传统 L-system 和 space-colonization 这版也通过 skeleton-to-voxel tube 输出 mesh，因此不应用连通性指标把它们简单判负：tree:lsystem=1/1.000, tree:space_colonization=1/1.000, root:lsystem=1/1.000, root:space_colonization=1/1.000, vine:lsystem=1/1.000, vine:space_colonization=1/1.000。
- 当前最有信息量的差异不是“是否连通”，而是结构复杂度和控制方式：L-system 给出规则化分叉，space-colonization 给出吸引子覆盖，proposed_connected 给出每层 projection-positive 的 root-attached 支撑。

## Fairness 限制

1. 这是 structure-first CPU mesh matrix，不经过 Trellis2 texture/GLB，因此不能回答材质一致性或生成模型外观质量。
2. 传统 baseline 由 skeleton 转 occupancy tube mesh，避免用未焊接 cylinder face components 不公平惩罚传统方法；相应地，它们的连通性会偏乐观。
3. `proposed_connected` 是本地 connected scaffold/projection-positive 代理，不是完整 sparse latent decode-project-encode 管线。
4. Space-colonization 的递归 depth 用 iteration budget 对齐，不等同于 grammar derivation depth；CSV 同时报 `graph_max_depth` 以暴露这个不完全公平点。
5. 本版 contact sheet 只渲染最终深度；每层 OBJ 和 metrics 已保存，后续需要补 front/top/zoom QA。

## 下一步缺口

- 加入 direct sparse grammar、final-only projection、prune-per-depth、bridge-per-depth 列，形成文档中要求的四列/六列闭环。
- 对 tree/root/vine 增加 root attachment、junction、tip zoom 的 Blender/Cycles 或同等 mesh render。
- 增加 proposed 的真实 sparse latent/Trellis2 本地可复现实验入口；当前只是 scaffold/projection-positive proxy。
- 补 coverage/collision metrics，让 space-colonization 的传统优势能被公平记录。
