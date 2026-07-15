# Transform-as-Grammar-Design 修改大纲（2026-05-10）

## 责任边界

本轮只处理 `transform-as-grammar-design` 论文故事线，不修改 baseline / naturalization 脚本，不把并行 worker 的 baseline 或 naturalization 结果改写成主贡献。正文修改只服务于一个目标：把 V21 IFS / transform 结果解释为 grammar operator admission / screening 的实证依据，而不是把它们当作泛泛的视觉展示或纹理成功案例。

## 核心叙事

Transform-copy 不是附加 gallery，而是 PS-RSLG operator library 中最容易被 reviewer 追问的类别：复制、旋转、缩放、平移、晶格和径向 orbit 看似是传统 IFS / shape grammar 已经解决的问题，但在 sparse-latent recursive execution 中，operator 是否可录入 grammar 库取决于它能否在后续深度中继续作为 attached, addressable, projectable state 使用。

因此，V21 的实证角色应写成：

1. **Admission protocol**：一个候选 operator 只有同时通过传统目标锁定、transform compatibility、shared support attachment、connectivity gate、OBJ-only mesh input、fresh remote PBR export、positive/negative control labeling，才被录入正向 operator family。
2. **Screening evidence**：V21 覆盖 branch IFS、radial ornament、pyrite lattice、bismuth stepped terrace、Escher-style stair loop、positive affine stack、negative axis mismatch control；它证明 transform-copy family 可以被严格筛选，而不是只靠“看起来像”。
3. **Boundary**：PBR export 和 surface-voxel connectivity 只证明 selected projected / screened meshes 能进入冻结 Trellis2 asset path；它不证明 watertight topology、exact equivariance、physical pyrite growth、physical DLA / crystal simulation，negative axis mismatch 即使连通也不能作为正向 operator admission。

## 可引用证据

来自 `docs/evaluation/strict_visual_matched_V21_ifs_transform_natural_zh_20260510.md`：

- V21 定位：补齐 IFS / transform / radial / lattice 类 case，本地只生成远端输入，不生成最终结果，不筛选本地图像，不做后处理修复。
- 输入策略：`obj_mesh_inputs_only`；远端必须走 mesh/PBR route，禁止 local selected render、2D-only image、posthoc repair mesh、non-OBJ mesh input。
- Grammar mapping：`affine_transform_grammar -> recursive_copy_depth_schedule -> strict_traditional_target_mapping -> shared_vertex_connected_support -> attached_natural_mesh_detail -> obj_mesh_input_only -> pbr_material_prompt -> largest_component_gate`。
- Dry-run gate：输入 OBJ 必须 `LCR >= 0.999`，实际 7 个输入 OBJ 的 mesh component count 均为 1，largest mesh component vertex ratio 均为 1.0。
- Positive / negative pair：`transform_compat_positive_affine_stack_d4` 是 commuting/shared-axis positive；`transform_compat_negative_axis_mismatch_d4` 是 connected but incompatible 的 negative control，不计正向 grammar match。

来自 `results/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_20260510_remote`：

- 7 个 V21 输入 OBJ：branch tree d6、radial ornament o12 d5、pyrite lattice d4、bismuth stepped d5、Escher stair loop d4、positive affine stack d4、negative axis mismatch d4。
- Textured GLB surface-voxel diagnostic：radial、bismuth、Escher、positive/negative compat 在 radius-0 已单连通；branch tree 和 pyrite 在 radius-0 有 tiny islands，但 LCR 分别为 0.99959 和 0.99974，radius-1 后均单连通。
- 该结果应作为 export/readability diagnostic，而不是 topology proof。

来自 `docs/visuals/pyrite_depth_textured_showcase_zh_20260509.md`：

- pyrite lattice depth showcase 支撑“symmetry/lattice family can be expressed by the same connected scaffold grammar”。
- stage 2--4 在 occupancy primary proxy 下单连通，stage 1 只有 tiny proxy islands；但 raw face components 很高，必须保留 faceted GLB/export caveat。

来自 `assets/symmetry_orbit_metrics_20260509.py`：

- symmetry/orbit metric 是 normalized voxelized-vertex overlap under mirror / z-rotation transforms。
- 它是 screening / supplement diagnostic，不是 exact equivariance proof；正文只能写 approximate symmetry/orbit screening，不能写 group-equivariant guarantee。

## 正文修改位置

### Method

在 `Rule Templates as a Recursive Language` 之后加入 `Operator Admission and Screening`：

- 定义 candidate operator admission 为一个 gate，而不是一个视觉选择。
- 给出四类 admission 条件：semantic match、state feasibility、positive/negative compatibility、export diagnostics。
- 对 transform-copy 明确：commuting/shared-axis transform stack 和 orbit schedule 可以作为 positive operator；axis mismatch / non-commuting stack 即使 connected，也只作为 negative control。
- 强调 screening 是 grammar design 的一部分：它决定哪些 operator 能进入 scheduler，哪些只能进入 appendix diagnostic pool。

### Experiments

在 `Task Definitions and Protocol` 后或 `Structural Baselines and Gen-3D Comparisons` 前加入 `Transform-Copy Operator Admission`：

- 将 V21 写成 strict one-to-one screening batch。
- 表格列出 case、role、transform controls、input OBJ gate、textured surface-voxel diagnostic、admission status。
- 正向结论：radial / lattice / stepped / stair / positive affine stack 支撑 transform-copy operator admission；pyrite/lattice 结合 pyrite depth showcase 支撑 lattice/symmetry family 的 connected scaffold + export compatibility。
- 负向结论：axis mismatch control 说明 connectivity alone is insufficient。

### Appendix

保留 V21 contact sheet，但 caption 从 “status sheet” 调整为 “operator-screening/status sheet”：说明它支持 transform-copy admission diagnostics，不支持 IFS-tree universal success 或 exact equivariance。

## Claim 边界

正文允许写：

- `Transform-copy candidates are admitted only when they preserve a strict one-to-one traditional mapping, attached shared support, and compatibility metadata.`
- `The V21 batch provides empirical operator-screening evidence for radial, lattice, stepped, stair-loop, and affine-stack transform-copy families.`
- `Connectivity alone is not sufficient for admission: the negative axis-mismatch row is connected but remains a negative compatibility control.`
- `Pyrite/lattice depth results support connected scaffold recursion and PBR export compatibility for a crystal-inspired lattice family.`

正文避免写：

- `solves IFS / crystal growth / symmetry`
- `exact equivariance`
- `watertight topology`
- `PBR proves topology`
- `all transform operators are stable`
- `negative compatibility row is a positive result because it is connected`

## Reviewer 预期风险

1. Reviewer 可能认为 transform 结果只是 procedural OBJ 送进 Trellis2 texture，不是 sparse-latent grammar 贡献。正文需要把它定位为 operator admission protocol，而不是最终方法效果。
2. Reviewer 可能认为 connectedness 是人为 shared vertices 造成的。正文需要承认这是 gate 的一部分：operator admission 要求候选 transform-copy operator 先能生成 attached support，再允许进入 sparse-latent recursive execution。
3. Reviewer 可能质疑 symmetry / lattice claim。正文只写 approximate orbit screening 和 lattice-like connected scaffold，不写 exact symmetry。
4. Reviewer 可能质疑 texture/PBR 混入结构结论。正文必须把 dry-run OBJ gate、textured GLB surface diagnostic、visual PBR export 三层分开。
