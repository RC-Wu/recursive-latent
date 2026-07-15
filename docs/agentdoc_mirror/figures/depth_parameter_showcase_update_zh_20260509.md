# Depth / Parameter 展示图更新 2026-05-09

## 目标与约束

- 只使用本地已有 Blender/PNG 渲染，不启动远端任务，不使用 matplotlib 点云。
- 视觉重点从“调参截图”改为“论文 qualitative evidence”：图像占主导，文字只标明锁定条件和变化轴。
- 输出只写入：
  - `docs/figures/depth_parameter_showcase_update_zh_20260509.md`
  - `paper_siga/figures/depth_parameter_showcase_20260509_worker.*`

## 新增图

新增文件：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/depth_parameter_showcase_20260509_worker.png`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/depth_parameter_showcase_20260509_worker.py`

图面结构：

1. **A. Same-condition textured recursive depth**
   - 来源：`visuals/bismuth_depth_textured_showcase_20260509/renders/stage{01..04}_{iso,front}.png`
   - 语义：同一个 bismuth hopper case，在 guide / material family / lighting / render protocol 锁定条件下，只展示 depth 1-4 的递归变化。
   - 版式：四列 iso 主图，front 小 inset，低饱和进度轴。

2. **B. Fixed-depth grammar-control row**
   - 来源：`visuals/paper_quality_renders_20260508/matrix_test_one/vine_prune_{compete,fork_side,radial4,portal}_iso.png`
   - 语义：同一 vine root/render family 的 fixed-depth mesh-only 控制诊断，展示 competition / branch bias / radial copies / portal transform 的视觉影响。
   - 注意：这行是 mesh-only diagnostic，不应在正文中表述为和上方完全同等条件的 textured parameter sweep。

## 简短后续计划

1. **主论文 Fig. Depth Study**
   - 优先使用 bismuth depth top row 或已有 `bismuth_depth_textured_showcase_20260509.png` 作为同条件 depth 证据。
   - caption 必须明确：同一 guide、同一 material/render protocol，仅 depth 变化。
   - 若后续有 mesh stats，旁边补一张 compact metric plot；不要把参数 sweep 混入同一个定量比较。

2. **Parameter / Control Study**
   - 当前只能作为 qualitative control diagnostic。
   - 最终论文需要重新补一组真正锁定 seed / camera / material / lighting / depth 的 textured renders，每次只扫一个语义参数：
     - branching pressure
     - competition radius
     - attachment bias
     - transform-copy mode

3. **视觉规范**
   - 白底或极浅暖灰底，细线分隔，不使用大色块。
   - 图内只保留变量名、depth、view 标签；机制解释放 caption。
   - 不再使用 `mesh-only method-control visualization` 这类过大的标题，也不把行标题竖排放大。

## Visual QA 判断

- **合规性**：通过。新图只复用本地 PNG 渲染，没有点云、没有远端生成、没有新实验结果伪造。
- **论文可用性**：部分通过。上半部分可作为 same-condition textured depth 展示候选；下半部分只能作为临时 control diagnostic。
- **颜色与版式**：较旧 `depth_parameter_showcase_20260509.png` 明显更克制。标签、留白、分隔线、背景色更接近论文图，但 bismuth 材质本身仍偏黄绿，属于源渲染限制。
- **可比性**：上半部分较强，因为相机/材质/渲染协议一致；下半部分一般，因为是低分辨率 neutral mesh render，且 operator/control 变化较大。
- **风险**：不要在 paper caption 中声称下半部分是严格同条件 parameter sweep；应称为 fixed-depth grammar-control qualitative diagnostic。
