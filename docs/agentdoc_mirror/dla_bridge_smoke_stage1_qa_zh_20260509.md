# DLA Bridge Stage-1 Smoke QA（2026-05-09）

## 目的

本次 `dla_bridge_smoke_stage1_20260509` 是一个很窄的结构诊断，不是纹理实验，也不是头图候选。它只回答一个问题：对于用户指出“DLA/晶体/非树 case 全是碎块，完全不可接受”的问题，post-hoc sparse close / bridge 是否还值得作为主线继续推进？

结论很明确：**hard DLA 后修仍失败；volumetric DLA 的正向证据来自 grammar-native connected support，而不是 bridge 后修。**

## 实验设置

- 远端 run：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/dla_bridge_smoke_stage1_20260509`
- 本地镜像：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/dla_bridge_smoke_stage1_20260509`
- 递归 stage：`1`
- 纹理：关闭
- grammar：`fork_side_attach`
- methods：
  - `raw`
  - `sparse_close_bridge`
- 输入：
  - `hard_dla`：旧碎块 hard case；
  - `volumetric_dla`：connected scaffold v2 的 volumetric DLA/coral-inspired root。

## 指标结果

| case | method | face comps | face LCR | occupancy comps | occupancy LCR | 结论 |
|---|---:|---:|---:|---:|---:|---|
| hard_dla | raw | 4 | 0.356 | 4 | 0.357 | 明显碎块，不能用 |
| hard_dla | sparse_close_bridge | 4 | 0.742 | 4 | 0.642 | LCR 提升但仍多组件，仍不能用 |
| volumetric_dla | raw | 3 | 0.520 | 1 | 1.000 | occupancy 单连通，face-level 仍碎；可作为 connected scaffold 支持证据但需 neutral render caveat |
| volumetric_dla | sparse_close_bridge | 1 | 1.000 | 7 | 0.870 | face 看似修好，occupancy 变差；后修 bridge 不能作为主线 |

## 严格解释

1. `hard_dla` 不是可修复正例。`sparse_close_bridge` 让 face LCR 从 `0.356` 提高到 `0.742`，但 occupancy component 仍是 `4`，说明碎块问题没有真正解决。
2. `volumetric_dla raw` 的 occupancy 已经是 `1` 个组件，说明“生成时就保持 connected support”的路线有效；但 raw face component 仍是 `3`、face LCR `0.520`，所以它只能支持 occupancy-primary connected scaffold，不能支持 clean raw mesh topology。
3. `volumetric_dla sparse_close_bridge` 是关键负证据：face component 变成 `1`，但 occupancy component 退化到 `7`，LCR 降到 `0.870`。这说明只看 face-level 或只做后处理桥接会误导论文结论。

## 对主线的影响

正向主线应固定为：

> grammar-native connected scaffold -> per-depth projection -> selected Trellis2 texture/PBR export。

DLA/coral/crystal 的写法应非常保守：

> DLA/coral/crystal-inspired connected scaffolds test non-tree rule families and texture/export compatibility, but we do not claim physical DLA/crystal growth or clean raw GLB topology.

post-hoc bridge/cache 的论文角色应降级为：

- 负例；
- 设计动机；
- 说明 occupancy-primary metric 必须和 raw mesh face diagnostics 分开；
- 说明 connected-support invariant 必须在 grammar/projection loop 内部维护，而不是最终修补。

## 下一步

1. 拉回 `mesh_projected.obj/png` 后做 Blender/Cycles fixed-camera neutral render。
2. 如果视觉确认 `volumetric_dla raw` 无明显漂浮块，可作为 supplement 的 connected scaffold stress case；否则只作为指标诊断。
3. 不再扩展 `hard_dla` 后修矩阵，除非有新的 grammar-native anchor/path 设计，而不是更强后处理。
4. 论文 Results / Discussion 中用这批结果支持“post-hoc bridge is insufficient; projection/grammar must define the state invariant”的论点。
