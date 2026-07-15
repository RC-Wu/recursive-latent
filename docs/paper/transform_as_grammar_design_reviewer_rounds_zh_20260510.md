# Transform-as-Grammar-Design Reviewer 自审与修正记录（2026-05-10）

## Round 1 Reviewer 批评

**R1.1 贡献定位仍可能被误读为“程序生成 OBJ + Trellis2 texture”。**

新增的 admission 表解释了 operator gate，但正文仍没有足够强调 V21 的作用是筛选 grammar operator，而不是证明最终资产质量。Reviewer 可能会说：这些 V21 输入已经是 connected OBJ，Trellis2 只负责 texture，和 sparse-latent recursive grammar 的核心贡献距离较远。

建议修正：在 `Transform-Copy Operator Admission` 开头增加一句更硬的限定：V21 不被用来证明 sparse-latent execution 优于 procedural OBJ，而是作为 operator library 的 admission / rejection evidence；真正的 recursive state 贡献仍由 projection-stabilized execution 支撑。

**R1.2 “admit” 这个词太强。**

表格里的 `admit` 容易被理解为该 operator 已经完全解决。实际证据只支持 `admit for scheduler as screened positive candidate` 或 `admit as positive screened family under current gates`。Pyrite 更应该是 `screen-positive with caveat`。

建议修正：把表格列名或状态改成更保守的 `Screening decision`，正文解释 admission 是有限范围内的 operator-library decision。

**R1.3 负例的价值还不够突出。**

当前段落说 negative axis mismatch connected but rejected，但没有说明这如何支持 screening protocol。Reviewer 可能认为 negative row 只是人为标签。

建议修正：强调 negative row 的作用是证明 gate 不等同于 connectivity / renderability：同样通过 OBJ LCR 和 GLB surface connectivity，仍因 transform-compatibility metadata 被拒绝。这让 grammar design 从 visual selection 变成 rule-contract selection。

**R1.4 Symmetry/orbit 说法仍有风险。**

`lattice/symmetry-inspired` 与 `orbit scaffold` 可接受，但如果正文同时出现 `symmetry/orbit metrics`，要明确该度量来自 normalized voxelized-vertex overlap，不证明 exact equivariance。

建议修正：在 pyrite 段保留 exact caveat，并避免把 stage 2--4 的 occupancy-connected 写成 surface-topology clean。

## Round 1 对应修正计划

1. 收紧 `Transform-Copy Operator Admission` 开头，明确 V21 是 operator-library screening evidence，不是 sparse-latent execution superiority proof。
2. 将表格 `Admission status` 改为 `Screening decision`，把 `admit` 改为 `screen-positive` / `screen-positive with caveat` / `reject as positive`。
3. 增加一句：negative row 的 connected/renderable 状态正是 screening protocol 的反例价值。
4. 在 pyrite 段强调 occupancy-connected / export caveat / approximate overlap metric 三层边界。

## Round 1 已执行修正

- `paper_siga/main.tex` 的 Method 中将 admission 定义收紧为 `screened positive candidate`，并声明 texture/PBR export 不能作为 operator-admission shortcut。
- `Transform-Copy Operator Admission` 段落增加限定：V21 不证明 sparse-latent execution superiority；它只筛选哪些 transform-copy operator 足够规范，可以进入 positive rule library。
- V21 表格状态从 `admit` 改为 `screen-positive`，pyrite 改为 `screen-positive with tiny-island/export caveat`，negative axis mismatch 改为 `reject as positive operator`。
- 增加 negative row 的解释：它通过 OBJ / GLB connectivity，但因 non-commuting transform stack 违反 operator contract，所以证明 connectivity / renderability alone 不足以 admission。

## Round 2 Reviewer 批评

**R2.1 Introduction / Contributions 没有承接新故事线。**

Method 和 Experiments 现在有 operator screening，但 contribution bullets 仍只说 rule-template semantics 和 broad evaluation。Reviewer 读完 introduction 可能不知道 transform-as-grammar-design 是一个主线，而不是后面临时加的表。

建议修正：在 contributions 中把 `transform-copy` 从普通 rule-template 例子升级为 “operator screening/admission protocol”；在 claims-under-test 段落中写明 V21 transform batch 是测试 rule-library admission，而不是 texture success。

**R2.2 `Operator Admission` 标题仍略强，但可以保留。**

标题可以保留，因为正文已经定义为 screened candidate；不过最好在实验 subsection 标题里也强调 screening，避免读者只看目录时误会。

建议修正：把实验 subsection 改成 `Transform-Copy Operator Screening` 或 `Transform-Copy Operator Screening for Admission`。

**R2.3 表格缺少和 classical coverage matrix 的关系。**

V21 表应明确它是 coverage matrix 中 IFS/fractal row 的 screened instantiation，而不是额外 unrelated evaluation。

建议修正：在 V21 段增加一句：this instantiates the IFS/fractal row of Table~coverage with strict one-to-one targets.

## Round 2 对应修正计划

1. 修改 contribution bullet：加入 operator-screening protocol for transform-copy / lattice / radial candidates。
2. 修改 claims-under-test 段落：把 transform-copy rule-library admission 列为一个被测试 claim。
3. 将实验小节标题从 `Transform-Copy Operator Admission` 改为 `Transform-Copy Operator Screening for Admission`。
4. 在 V21 段落中连接 `Table~\ref{tab:coverage-exemplar-tasks}` 的 IFS/fractal row。

## Round 2 已执行修正

- Contributions 第二条现在明确包含 `operator-screening gates`，让 transform-as-grammar-design 成为正文承诺而不是孤立结果段。
- `Claims under test` 段落加入 transform-copy candidates under strict one-to-one targets and compatibility gates。
- 实验小节标题改为 `Transform-Copy Operator Screening for Admission`。
- V21 段落明确说明该 batch 是 Table~`\ref{tab:coverage-exemplar-tasks}` 中 IFS/fractal row 的 strict instantiation。
