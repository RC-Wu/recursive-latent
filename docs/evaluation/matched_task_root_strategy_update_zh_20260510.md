# 严格一对一评估中的 root 选择修正（2026-05-10）

## 1. 本轮用户补充的核心含义

用户最新补充不是降低“对比要严格”的要求，而是修正 root 选择策略：

- 传统方法生成什么任务，我们仍然要生成同一类任务。
- 例如 L-system 生成树冠，我们也要生成树冠；DLA 生成晶体/珊瑚式前沿附着，我们也要生成晶体/珊瑚式前沿附着；IFS 生成 transform-copy/fractal tree/ornament，我们也要用对应 transform-copy/递归模式生成。
- 但 ours 不必被迫使用当前很差的方块 root 或 proxy root。只要最终结果在物品类别、整体轮廓、递归层级、复杂度、增长模式上与传统任务对齐，就可以换更好的 root、guide image、public mesh、Trellis2 生成 mesh 或已有项目内高质量 root。
- 因此评估目标不是“同一个低质量 primitive 上做 copy”，而是“同一个递归任务 family 下，传统 procedural primitive 与 PS-RSLG 的 generator-native root/operator/naturalization 组合的结果对比”。

这点非常重要：如果 root 很差，PS-RSLG 的视觉上限会被 root 限制；而论文想证明的是 PS-RSLG 在同类递归任务中能把传统可控递归模式和生成模型资产质量结合起来。

## 2. 新的严格匹配定义

对每个 exemplar task，记录：

```text
Task = (family, object_category, recursive_mode, target_silhouette,
        depth_range, control_params, evaluation_views)
```

其中：

- `family`：L-system、space colonization、DLA/frontier、IFS/transform-copy、shape grammar 等。
- `object_category`：松树/树冠、根系/藤蔓、灌木壳层、珊瑚、晶体、递归饰件等。
- `recursive_mode`：branch rewriting、attractor competition、frontier attachment、contractive transform orbit、split/extrude/replace。
- `target_silhouette`：粗形状约束，如 upright crown、radial root curtain、clustered crystal aggregate、spiral/portal transform。
- `depth_range`：传统方法与 ours 都要展示同等可见递归深度，不能只用浅层漂亮资产冒充深递归。
- `control_params`：角度、缩放、attractor radius、stickiness、transform set、mask radius、projection schedule 等。
- `evaluation_views`：白底 overview、相同相机或语义可比相机、多层 camera zoom、局部 callout。

PS-RSLG 允许变更 root 的前提：

```text
category(ours) ~= category(baseline)
silhouette(ours) ~= silhouette(baseline)
mode(ours) ~= mode(baseline)
depth_visible(ours) ~= depth_visible(baseline)
```

但 root 来源必须记录：

```text
root source -> guide source -> grammar operators -> depth schedule
-> projection/naturalization schedule -> texture/PBR route -> selection budget
```

## 3. 当前已有强 root 和推荐用途

### 3.1 植物 / 树 / 根系

强参考图：

- `visuals/programmatic_pbr_renders_20260508/vine_auto_iso.png`
- `visuals/programmatic_pbr_renders_20260508/tree_auto_iso.png`

强 textured GLB / root 候选：

- `visuals/textured_glb_20260508/tree_compete_s3/textured.glb`
- `visuals/textured_glb_20260508/vine_d5_compete_s5_inference/textured.glb`
- `visuals/public_guide_textured_glb_20260509/tree_compete_d4_pruned_tree_roots_steps8_tex2048_xformers/textured.glb`
- `visuals/public_guide_textured_glb_20260509/vine_compete_stage03_spiky_tendril_steps8_tex2048_xformers/textured.glb`
- `visuals/public_guide_textured_glb_20260509/vine_compete_stage03_parthenocissus_steps8_tex2048_xformers/textured.glb`

推荐匹配任务：

| 传统任务 | baseline | ours 策略 | 当前判断 |
|---|---|---|---|
| L-system tree/canopy | symbolic branch rewriting + turtle mesh | `tree_compete_s3` 或 `tree_roots_hq`，operator 解释为 branch/side/fork + projection | 可推进，必须避免 blob proxy |
| L-system vine/root | branching root/vine grammar | `vine_d5_compete_s5`，operator 解释为 fork/side/compete + attachment | 当前最强 |
| Space colonization tree canopy | attractor-filled crown | `tree_compete_s3`，operator 解释为 attractor/occupancy competition | 需要重新做白底/zoom/CLIP |
| Space colonization root/vine | attractor-guided downward/root field | `vine_d5_compete_s5` 或 public vine roots | 可推进 |

### 3.2 DLA / 珊瑚 / 晶体 / frontier

候选：

- `visuals/connected_scaffold_v2_textured_glb_hq_20260509/volumetric_dla_coral_octopus_hq_steps8_tex2048_xformers/textured.glb`
- `visuals/connected_scaffold_v2_textured_glb_hq_20260509/volumetric_dla_coral_bismuth_hq_steps8_tex2048_xformers/textured.glb`
- `visuals/connected_scaffold_v2_textured_glb_hq_20260509/bismuth_hopper_bismuth_hq_steps8_tex2048_xformers/textured.glb`
- `visuals/pyrite_depth_hq_warm_showcase_20260509/stage04_textured.glb`

注意事项：

- 不能再把碎块 DLA 直接作为正例。DLA/frontier 的主 claim 应当是“frontier attachment + connectivity-first projection 可以在 selected scaffold 上保持连通并导出 textured GLB”，而不是“真实物理 DLA 已解决”。
- 对晶体类，pyrite lattice 比 bismuth/porous 更接近 transform/symmetry 成功 case；bismuth hopper 可以作为 crystal-like stepped growth，但需要避免声称严格晶体物理。
- 若最终结果仍有高 component 或破碎面，则只能放 failure/boundary，不进主文正图。

### 3.3 IFS / transform-copy

当前宽松 IFS tree -> pyrite 的比较不成立。应拆成两类：

1. IFS fractal tree/branch：ours 必须生成 transform-copy branch/tree-like asset，而不是 pyrite。
2. IFS/lattice/ornament：可以定义为 transform orbit / group-like repetition，此时 pyrite lattice 是合理候选。

推荐论文写法：

- 对 IFS coverage claim，方法论上证明 contractive transform-copy 是 PS-RSLG 的子类。
- 实验上分两个 exemplar：
  - `IFS fractal tree`：需要继续生成或筛选 branch/tree-like ours。
  - `transform lattice / symmetry orbit`：使用 pyrite lattice 作为正例，并报告 transform consistency / symmetry error / depth zoom。

## 4. 现有不合格材料降级

以下材料只能作为 screening 或负例，不能直接当最终一对一 evidence：

- `visuals/strict_matched_psrslg_proxy_20260510_seed310_v2/strict_matched_proxy_contact_v2_20260510.png` 中的 L-system ours：轮廓变成 blob canopy，不像树冠/分枝。
- 同一图中的 IFS ours：transform tree 目标与结果不匹配。
- 早先 `L-system branch -> vine`、`IFS tree -> pyrite`：语义和递归模式都太松，只能作为探索记录。

## 5. 下一步执行原则

1. 先从传统任务定义出发，而不是从漂亮 ours 出发。
2. 对每个任务生成多个 ours root/operator candidate。
3. 用严格筛选：
   - 类型是否一致；
   - 粗形是否接近；
   - 递归深度是否可见；
   - 生长/变换模式是否可解释；
   - 连通性与 mesh/PBR 渲染是否过关；
   - 多层 camera zoom 中是否仍然有细节，而不是只有中心树干或模糊块。
4. 只把 paper-grade candidates 放入主文；其余作为 appendix screening 或 failure。
5. 所有最终图必须是 mesh 或 textured mesh render。Matplotlib、point cloud、二维 crop 不能作为论文证据。

## 6. 当前优先级

1. 用 `tree_compete_s3`、`tree_roots_hq`、`vine_d5_compete_s5` 做白底真实相机 zoom，作为 L-system/space-colonization 植物类候选。
2. 对 DLA/coral/crystal 选择连通性和视觉同时过关的 GLB，再和传统 DLA/frontier baseline 一对一比较。
3. 对 IFS 不再用 pyrite 直接冒充 tree；要么生成 transform-copy tree-like ours，要么把 task 改成 lattice/orbit 并用 pyrite 做对应比较。
4. 为每个 candidate 写清楚算子组合，而不是只写“像某类东西”。
