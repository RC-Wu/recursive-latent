# Cache / Sampler 连通性 mesh smoke 状态（2026-05-09）

## 目的

用户要求快速尝试 KV/latent/LOD/transform cache、滑动窗口和采样器替代传统随机生长等方向。当前这一支线实现的是一个轻量 proxy：在真实输入 mesh 或 GLB 上体素化，尝试若干 projection-aware / cache-like 支撑融合策略，然后导出被选中的 voxel surface mesh，用于判断它是否值得进入昂贵的 Trellis2 texture export。

这一实验不能替代真正的 Trellis2 内部 latent/cache 修改；它只是低成本筛选和负例诊断。

## 产物路径

- 脚本：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/cache_sampler_connectivity_20260509.py`
- 本地真实输入 smoke：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/cache_sampler_connectivity_20260509_local_mesh_smoke`
- 选择表：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/cache_sampler_connectivity_20260509_local_mesh_smoke/projection_aware_texture_selection.csv`
- 选中 surface OBJ：
  - `hard_dla/masked_local_sampler_boundary_schedule_selected_surface.obj`
  - `hard_radial/transform_cache_predecode_fusion_selected_surface.obj`
  - `hard_scifi/naive_transformed_copies_selected_surface.obj`
  - `hard_bismuth/transform_cache_predecode_fusion_selected_surface.obj`
- Blender 渲染：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/cache_sampler_connectivity_20260509_local_mesh_smoke/renders`

## 结果摘要

本地真实输入 smoke 的选择结果：

| case | selected method | occupancy components | LCR | 判断 |
|---|---:|---:|---:|---|
| hard_dla | masked local sampler + boundary schedule | 3 | 0.99969 | 指标改善，但视觉上过度闭合/块状，不可作为成功 DLA |
| hard_radial | transform cache predecode fusion | 2 | 0.99998 | 可作为 transform/cache 支线候选，需要进一步 Trellis2 texture 验证 |
| hard_scifi | naive transformed copies | 1 | 1.0 | 输入本身已经较连通，不能说明 cache 有贡献 |
| hard_bismuth | transform cache predecode fusion | 1 | 1.0 | 指标可用，但需人工确认是否保持 bismuth/crystal 语义 |

## 严格结论

1. 这支线目前不能作为论文主成功结果。尤其 `hard_dla` 的渲染显示，体素闭合可以提升连通指标，却会把 DLA/coral 的开放分支结构压成块状支撑，破坏语义。
2. 这支线可以作为负例或设计动机：只靠后验 cache/closing 不足以解决碎块问题，必须把 connected support 写成 grammar/projection loop 的不变量。
3. 真正值得继续的是两条线：
   - grammar-native connected scaffold：生成时就保证 6-neighborhood connected support；
   - decoder-aware local naturalization：在局部 masked region 中自然化纹理和表面，而不是全局重写拓扑。

## 后续实验建议

最小可执行下一步：

1. 对 `bismuth_hopper_cluster` 和 `pyrite_crystal_lattice_cluster` 做同条件 depth/parameter 展示，验证非树/晶体支线能否像 vine 一样支持递归阶段展示。
2. 将 `hard_radial` 和 `hard_bismuth` 选中 surface mesh 送进 Trellis2 texture export，只用于判断 cache/proxy 输出是否可被 Trellis2 PBR 处理，不作为最终主张。
3. 重新设计 DLA/coral 的 generator：不要从碎块后修补，而是在规则层显式保留父子接触桥、最小 neck radius、局部 overlap margin 和 per-depth projection。

