# System Grammar Experiment Status - 2026-05-08 19:35

本文档汇总 2026-05-08 system-grammar 计划启动后的第一批远端实验结果。远端路径：

`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/system_grammar_remote_20260508_1839`

本地 summary 镜像：

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/remote_results/system_grammar_remote_20260508_1839/summaries`

## 1. 远端状态

- 本批实验只使用 GPU 4/5/6/7。
- GPU 0/1 未触碰；它们属于用户的 meshvae v4.7 jobs。
- 本批所有 jobs 均已结束，GPU 4/5/6/7 已释放。
- 远端项目目录从约 `54G` 增至约 `57G`，低于 `70G` 限制。
- 所有 caches/TMP 均由远端 worker 指向 project root。

## 2. Job 状态

| Job | GPU | 状态 | 主要输出 |
|---|---:|---|---|
| `space_competition_gpu4` | 4 | completed | `space_competition_curves/{vine,tree,non_tree_porous}/summary.json` |
| `masked_lowstep_grid_gpu5` | 5 | completed | `masked_lowstep_grid/tree_stable_root/summary.json` |
| `cache_lod_diagnostic_gpu6` | 6 | completed | `cache_lod_probe/island_city_lod256/summary.json` |
| `symmetry_escher_proxy_gpu7` | 7 | completed | `symmetry_escher_proxy/{crown,island_city}/summary.json` |

## 3. Space Competition / Operator Curves

### 3.1 Vine

| Operator | Depth | Tokens | Vertices | Faces | 判断 |
|---|---:|---:|---:|---:|---|
| `compete` | 3 | 921 | 199470 | 405886 | 最稳，低 token 增长，适合主实验 |
| `compete_fork` | 3 | 2198 | 360521 | 659002 | 更表达，但 token/mesh 约翻倍 |
| `fork_side` | 3 | 2193 | 328236 | 568296 | 更表达，但仍需 projection/连通性指标 |

Vine base tokens: `781`，FDG voxels: `184294`。

### 3.2 Tree

| Operator | Depth | Tokens | Vertices | Faces | 判断 |
|---|---:|---:|---:|---:|---|
| `compete` | 3 | 1546 | 321242 | 640084 | 稳定主线 |
| `compete_fork` | 3 | 3211 | 528155 | 986260 | 表达增强，体量明显增加 |
| `fork_side` | 3 | 3223 | 516315 | 939016 | 表达增强，需视觉筛选 |
| `portal` | 3 | 1609 | 222819 | 412252 | 非树/transform-copy 对照可用 |

Tree base tokens: `1425`，FDG voxels: `311366`。

### 3.3 Non-tree porous

| Operator | Depth | Tokens | Vertices | Faces | 判断 |
|---|---:|---:|---:|---:|---|
| `compete` | 2 | 1876 | 814727 | 1749032 | 稳，但 mesh 非常重 |
| `scale_down` | 2 | 2114 | 782409 | 1512528 | 可用于 infinite/scale proxy，但视觉待检 |
| `portal` | 2 | 1998 | 810557 | 1635166 | 可用于 non-tree transform-copy，但 mesh 重 |

Non-tree porous base tokens: `1726`，FDG voxels: `784597`。

## 4. Masked Flow / SDE Low-Step Grid

Root: `tree_stable_root`。Grid: steps `[1,2,4]`，alpha `[0.1,0.25]`，operators `compete` 和 `compete_fork`。

### 4.1 Compete

| Steps | Alpha | Depth | Tokens | Preserved | New | Vertices | Faces | 判断 |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 0.1 | 2 | 1500 | 1462 | 38 | 319208 | 636598 | 几乎只做轻微局部采样 |
| 1 | 0.25 | 2 | 1500 | 1462 | 38 | 318490 | 635374 | 体量略小 |
| 2 | 0.1 | 2 | 1500 | 1462 | 38 | 319131 | 636380 | 与 step1 接近 |
| 2 | 0.25 | 2 | 1500 | 1462 | 38 | 318357 | 635188 | 与 step1 接近 |
| 4 | 0.1 | 2 | 1500 | 1462 | 38 | 319066 | 636282 | 与 step1 接近 |
| 4 | 0.25 | 2 | 1500 | 1462 | 38 | 318329 | 635272 | 与 step1 接近 |

结论：`compete` 的新增区域太少，low-step sampler 对几何体量影响很小。它适合稳定主线，不适合展示 flow stochastic growth 的强效果。

### 4.2 Compete-fork

| Steps | Alpha | Depth | Tokens | Preserved | New | Vertices | Faces | 判断 |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 0.1 | 2 | 3099 | 2179 | 920 | 555630 | 1052330 | 表达多，体量大 |
| 1 | 0.25 | 2 | 3099 | 2179 | 920 | 448344 | 811426 | alpha=0.25 明显收缩/简化 |
| 2 | 0.1 | 2 | 3099 | 2179 | 920 | 567269 | 1079034 | 更重 |
| 2 | 0.25 | 2 | 3099 | 2179 | 920 | 479075 | 872196 | 收缩但仍重 |
| 4 | 0.1 | 2 | 3099 | 2179 | 920 | 559244 | 1060468 | 与 steps1/2 接近 |
| 4 | 0.25 | 2 | 3099 | 2179 | 920 | 477002 | 865304 | 仍是较好的压缩点 |

结论：masked sampler 对 `compete_fork` 有可测影响，alpha=0.25 可显著降低 vertex/face 体量。但这还不是视觉质量证据，必须拉取 mesh/渲染确认是否是合理自然化还是过度塌缩。

## 5. Symmetry / Escher Proxy

### 5.1 Crown

| Operator | Depth | Tokens | Vertices | Faces | 判断 |
|---|---:|---:|---:|---:|---|
| `radial4` | 2 | 1360 | 186014 | 262902 | symmetry case 候选，需 symmetry error 和视觉 |
| `portal` | 2 | 1358 | 489751 | 998054 | 结构更重，可能适合 ornament |
| `scale_down` | 2 | 1713 | 629340 | 1271272 | 重，可能更像递归嵌套 |

### 5.2 Island city

| Operator | Depth | Tokens | Vertices | Faces | 判断 |
|---|---:|---:|---:|---:|---|
| `scale_down` | 2 | 1957 | 599410 | 1241930 | infinite / Escher proxy 主候选 |
| `portal` | 2 | 1908 | 642927 | 1408462 | 结构重，需相机筛选 |
| `radial4` | 2 | 2884 | 652054 | 1163040 | 目前更像压力测试 |

结论：island-city scale-down 仍是最接近 infinite / Escher proxy 的现有方向，但需要本地 Blender 视觉检查。

## 6. Cache / LOD Probe

Case: `island_city_lod256`，base tokens `342`，FDG voxels `146785`。

| Operator | Depth | Tokens | Vertices | Faces | 判断 |
|---|---:|---:|---:|---:|---|
| `scale_down` | 2 | 362 | 96493 | 189858 | 有 token-budget 递归潜力 |
| `radial4` | 2 | 512 | 94443 | 151818 | token cap 明显，适合 LOD/cache 论证 |

结论：这是无限递归/LOD 叙事的第一条有用证据。它不证明无限递归已完成，但证明在较低 latent resolution/token cap 下可以让递归状态保持有界，适合写成 cache/LOD extension 的实验起点。

## 7. 下一步必须补的实验

1. **Projection ablation 主实验**
   - no projection；
   - final-only projection；
   - per-depth projection；
   - 同 root、同 operator、同 depth、同 render 协议。
2. **Space colonization 公平 baseline**
   - traditional space colonization skeleton/mesh；
   - proposed sparse competition；
   - direct grammar；
   - per-depth projection。
3. **Masked flow visual inspection**
   - 拉取 `compete_fork alpha=0.1/0.25` 的 depth2 mesh；
   - Blender 同相机渲染；
   - 判断 alpha=0.25 是自然化还是塌缩。
4. **Symmetry metric**
   - crown radial4 / portal；
   - island_city scale_down；
   - 计算旋转/镜像后 occupancy/mesh 对齐误差。
5. **LOD/zoom figure**
   - 用 `island_city_lod256` 生成 zoom panel；
   - 把 token cap 与 visual level 关联起来，支持 infinite recursion extension。

