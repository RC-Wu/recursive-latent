# Transform / Operator Admission 叙事 Gap Review

日期：2026-05-10  
对象：`paper_siga/main.tex` 中 Method / Grammar / Operator / Experiment 相关叙事  
结论级别：审稿式 gap review，不修改正文。

## 1. 总体判断

当前正文已经基本把 transform 写成了 **grammar operator admission / screening**，而不是孤立 gallery。最关键的完成点有三处：

1. Method 里已有独立小节 `Operator Admission and Screening`，明确 operator 不是视觉 mesh macro，而是能否留下下一层规则可读取的 recursive state。这里已经包括 semantic/state/compatibility/projection/export 五类 gate，并特别说明 export 不能作为 operator admission shortcut。
2. Transform-copy 实验小节已经把 V21 定位为 grammar-design evidence，而不是视觉结果展示。正文明确写了 transform-copy 不证明 sparse-latent execution 优于 procedural OBJ construction，只筛哪些 transform-copy operators 可进入 positive rule library。
3. 表格和文字已经把正负例分开：radial、pyrite/lattice、bismuth、stair-loop、compatible affine stack 是 screen-positive 或 caveated positive；branch-tree 是 boundary；axis-mismatch 是 connectivity-positive 但 compatibility-negative 的对照。

所以主叙事方向是对的。现在的 gap 不是“没有 operator admission 故事”，而是 **admission certificate 的证据层还偏表面**：V21/V23/V24 的 connectivity 指标能支撑 “screened candidate / boundary diagnostic”，但还不足以支撑更强的 “transform operator 已在 sparse-latent recursive execution 中被严格验证”。

## 2. 可能过强或需要再降级的 claim

### A. `screen-positive` 的语义需要更窄

正文 Table `v21-transform-admission` 写 `screen-positive`，但 pyrite/lattice 的 V21/V24 指标都是 r0 四组件、r1 单组件，属于 “near-connected / tiny-island caveat”。建议正文避免让读者把 `screen-positive` 读成 clean topology 或 watertight positive。

建议用语：

- `screen-positive under the admission protocol`
- `candidate admitted for transform-copy state screening`
- `with tiny-island/export-surface caveat`

避免用语：

- `successful IFS operator`
- `validated lattice recursion`
- `clean transform-copy result`

### B. strict equivariance / symmetry 不应暗示已证明

正文第 309 行附近已经很好地说 exact group equivariance 需要 scheduler、merge、sampler、projection、codec、grid quantization 全部 commute。这个限制必须保留。任何 figure caption 或 discussion 中如果出现 symmetry/equivariance，应写成 approximate orbit / lattice scaffold metric。

建议统一：

- `approximate orbit consistency`
- `lattice/symmetry-inspired scaffold`
- `voxelized transform-overlap diagnostic`

不要写：

- `equivariant generation`
- `strict symmetry preservation`
- `group-equivariant sparse latent operator`

### C. full IFS generality 仍然过强

V21 branch-tree IFS 被拒绝为 positive，V23 `V23_ifs_fractal_tree_d5_branch_copy` 在 enhanced summary 里也是 boundary-control。这说明当前 transform-copy admission 支撑的是 radial/lattice/stepped/shared-axis affine 等子类，不是 full IFS family。

建议将 `IFS/fractal` 行写成：

> transform-copy screening over selected IFS-style orbit/lattice/stepped programs

而不是：

> IFS programs are solved / covered experimentally

### D. “sparse-latent execution outperforms mesh-space” 仍需证据隔离

正文第 551 行已经声明 transform-copy 结果不证明 sparse-latent superiority，这是必要的。第 667 行的 gen-3D baseline 叙事还要继续小心，因为 vine 行使用 stronger selected candidate，而不是弱 strict-matched vine row；如果表格没有完全 same-root/same-depth/same-seed，应避免 universal superiority。

建议主张收束为：

> The baseline rows diagnose why typed handles, attachment feasibility, and per-depth projection are needed.

而不是：

> PS-RSLG generally outperforms mesh-space recursion.

## 3. 推荐插入的中文修改大纲与英文正文要点

### 建议插入位置 1：Method / Operator Admission 小节末尾

中文大纲：

- 补一句 “admission 不是成功/失败二分，而是将 operator 分成 positive scheduler candidate、boundary diagnostic、negative compatibility control”。
- 明确 transform-copy 的最低证据链：locked transform contract -> attached/shared support -> projection/readable handles -> export diagnostics。
- 把 exact equivariance 放入 future dedicated experiment。

英文正文要点：

> We use admission as a scheduler-level decision, not as a visual success label. A transform-copy family is admitted only when the declared transform contract, shared or certified support, projection behavior, and next-depth handle readability are all satisfied. Rows that are connected but violate compatibility assumptions remain negative controls, and approximate orbit scores are diagnostics rather than proofs of equivariance.

### 建议插入位置 2：Experiments / Transform-Copy Operator Screening 开头

中文大纲：

- 先给 “certificate chain” 的一段，避免读者觉得 V21 是另一张 gallery。
- 说明 V21 是 strict one-to-one transform screening batch，V23/V24 是 all-family / priority rerun 的支撑或 polish，不替代 V21 的 admission protocol。
- 把 pyrite/radial 明确写成 positive scaffold cases，branch-tree/axis-mismatch 写成 negative/boundary cases。

英文正文要点：

> The certificate chain for each row is: a locked classical transform target, a generated OBJ scaffold with attached shared support, a declared projection/export policy, post-export surface-voxel diagnostics, and a decision about whether later grammar rules may read the result. V23 and V24 reruns are used only as visual/metric corroboration for selected rows; they do not relax the V21 admission gates.

### 建议插入位置 3：Discussion / Limitations

中文大纲：

- 将 transform compatibility 写成 empirical and case-dependent。
- 单独列出未完成：handle-level transform error、orbit consistency under decode/re-encode、multi-depth operator survival、negative controls beyond axis mismatch。
- 明确 pyrite/radial 是 admission evidence，不是 material/topology/symmetry proof。

英文正文要点：

> Transform compatibility is empirical in the current system. The present evidence supports selected orbit, lattice, stepped, and shared-axis affine candidates under fixed gates, but not full IFS generality, exact equivariance, or clean watertight topology. Future versions should report handle-level transform error and orbit survival across decode/project/re-encode loops.

## 4. 正负 case 支撑链

### Positive / near-positive: pyrite lattice

证据链：

- V21 strict transform batch：`V21_ifs_pyrite_lattice_transform_d4_faceted`，OBJ LCR = 1.000；GLB surface r0 components = 4，r0 LCR = 0.999739；r1 components = 1。
- V23 all-family：`V23_ifs_fractal_lattice_d4_pyrite_copy_bridges`，enhanced summary 里是 IFS/transform main-candidate，runs = 4，mean family score = 0.889，min r0 LCR = 0.999739，max r0 components = 4。
- V24 priority rerun：`V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA` 指标仍为 r0 4 components、LCR 0.999739、r1 single component。

可支撑：

- lattice / pyrite-like transform-copy 是 screen-positive candidate；
- 支持 connected lattice scaffold and export compatibility；
- 是当前最强 crystal/symmetry visual line 之一。

不可支撑：

- strict equivariance；
- watertight surface topology；
- physical pyrite crystallization；
- full IFS generality。

### Positive: radial ornament

证据链：

- V21 radial ornament：r0/r1 均 single component，LCR 1.0。
- V23 radial ornament：enhanced summary 里 `V23_ifs_radial_ornament_o8_d4_orbit_spokes` 是 main-candidate，runs = 4，mean family score = 0.905，min r0 LCR = 0.999888，max r0 components = 2。
- V24 radial polish：`V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA` r0/r1 均 single component，LCR 1.0。

可支撑：

- radial/orbit transform-copy 是最干净的 positive operator admission case；
- 适合放在主文作为 transform screening positive row。

注意：

- 它证明的是 orbit-schedule candidate under gates，不是 strict rotational equivariance。

### Boundary: branch-tree / IFS tree

证据链：

- V21 branch-tree：r0 components = 3，r1 single；正文表格已经写 rejected as positive。
- V23 `V23_ifs_fractal_tree_d5_branch_copy` 在 enhanced summary 中是 boundary-control，min r0 LCR = 0.998948，max r0 components = 5。

可支撑：

- full branch-copy IFS tree 仍然是 boundary；
- 说明 transform-copy admission 不能靠 “看起来像树/连得上” 通过。

应避免：

- 把 branch-tree 作为 IFS positive。

### Negative compatibility control: axis mismatch

证据链：

- V21 axis-mismatch stack：OBJ LCR 1.000，GLB r0/r1 都 single component。
- 但正文明确拒绝为 positive operator，因为 non-commuting anisotropic scale / axis mismatch 违反 compatibility gate。

价值：

- 这是整个 operator admission 叙事最有力的负例：它证明 admission 不是 connectivity 或 renderability 打分，而是 grammar contract 判断。

建议主文强调：

> The negative row is intentionally connected; its rejection demonstrates that compatibility, not only connectivity, controls admission.

## 5. 三个必须修的 main.tex 位置 / 主题

1. `paper_siga/main.tex:287` 附近，`Operator Admission and Screening`：补 “admission class taxonomy”，把 positive candidate / boundary diagnostic / negative compatibility control 写清楚，避免 screen-positive 被读成最终成功。
2. `paper_siga/main.tex:551` 附近，`Transform-Copy Operator Screening for Admission`：在第一段加入 certificate chain，并说明 V21 是 admission protocol，V23/V24 是 corroboration/polish；不要让 V23/V24 candidate screen 反向放宽 V21 gates。
3. `paper_siga/main.tex:667` 和 `paper_siga/main.tex:697` 附近，baseline/effective-resolution 叙事：继续降级 “outperform / preserve recursive detail” 类语言，明确当前证据是 selected cases + controls，不能替代 same-root handle-level metrics。

## 6. Pyrite lattice case 最新可看路径

优先看 V24 polish GLB：

`visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA_steps8_tex2048_seed20284524_xformers/textured.glb`

配套 summary：

`visuals/strict_visual_matched_texture_V24_priority_rerun_20260510/V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA_steps8_tex2048_seed20284524_xformers/summary.json`

优先看 zoom/callout 图：

`visuals/strict_visual_matched_texture_V23_all_family_seed3_stable_pool_zoom_render_target_20260510/V23_ifs_fractal_lattice_d4_pyrite_copy_bridges/strict_matched_zoom_comparison.png`

V21 严格 transform screening 的 pyrite zoom：

`visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293300_zoom_20260510/V21_ifs_pyrite_lattice_transform_d4_faceted/strict_matched_zoom_comparison.png`

对应 V21 GLB：

`visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_20260510/V21_ifs_pyrite_lattice_transform_d4_faceted_steps8_tex2048_seed20295803_xformers/textured.glb`

## 7. 最短审稿式 verdict

当前 transform/operator admission 故事已经达到 “主文可成立的骨架”：方法中有 gate，实验中有 V21 strict batch，正负例能解释为什么 admission 是 grammar contract 而不是 gallery selection。下一轮主要不是再堆图，而是把 `screen-positive` 的语义进一步收窄，并在正文中把 pyrite/radial/branch-tree/axis-mismatch 串成一条明确证据链：radial 是 clean positive，pyrite 是 caveated positive，branch-tree 是 IFS boundary，axis-mismatch 是 connected negative control。
