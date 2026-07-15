# 方法图与 depth/parameter 展示图视觉改进建议

日期：2026-05-09

范围：只评审并重排现有 `paper_siga/figures/` 与 `visuals/*/renders/` 中的真实 PNG 素材；不引入点云，不生成伪结果，不修改 LaTeX 或现有 plan 文档。

## 1. 当前图的主要问题

### 1.1 方法图 `method_system_grammar_polished_20260508.png`

主要问题不是“画得不够复杂”，而是图面语言仍偏工程流程图：

- 信息层级过平。模块、箭头、文字说明、示例图块的视觉权重接近，读者第一眼难以判断核心贡献是递归生成机制、空间竞争约束、还是 mesh/material 输出链路。
- 箭头语义不够分层。数据流、控制流、递归回路、约束反馈如果都用同一种箭头，会让方法看起来像软件 pipeline，而不是论文中的概念模型。
- 文本密度偏高。方法图应让审稿人 3 秒内看到“grammar -> recursive expansion -> geometric arbitration -> textured mesh”，细节算法名可以放小，不应和主路径抢权重。
- 真实 case 的角色偏弱。若图中真实生成结果只是末端小图，方法说服力会下降；SIGGRAPH 图更常把 pipeline 与一个贯穿 case 绑定，让每个阶段都对应可见几何变化。
- 视觉风格偏“办公软件/技术汇报”。若存在大面积彩色块、过多圆角框、强边框、默认字体和默认箭头，会削弱图形学论文的质感。

### 1.2 `vine_depth_textured_showcase_20260509.png`

- 横向展示方向正确，但同条件变量表达不够强。读者应立刻知道“只改 depth”，而不是把它读成四个独立结果。
- 图像之间留白和尺度控制需要更严格。递归 depth 的形态变化很大，如果每张图用自己的视觉中心和相机占比，会弱化可比性。
- 标签层级偏松。Depth 标签、视角标签、说明文字应形成轻量系统；不要使用大标题压过生成结果。
- 深色 render 背景、地面阴影、主体棕色材质本身已经很重，外部版式应更克制，避免再用重色块或装饰性背景。

### 1.3 `depth_parameter_showcase_20260509.png`

- depth 与 parameter sweep 容易混在一个认知层级里。论文图应区分“递归深度带来结构复杂度变化”和“参数调制带来形态族变化”。
- 如果每个 cell 的相机、材质、seed、尺度不完全锁定，矩阵会被误读为定量可比。需要在图面中明确哪些维度是 locked，哪些是 varied。
- 参数名若直接使用脚本变量名，会显得像调参截图。图中应使用论文概念名，例如 branching pressure、competition radius、curvature gain、attachment bias。
- 矩阵图不宜塞太多文字。列/行标题最多保留概念名和数值，解释放 caption。

## 2. 推荐视觉规范

### 2.1 总体风格

- 目标气质：SIGGRAPH-style qualitative figure，干净、克制、以渲染结果为主，不像 matplotlib 默认图。
- 背景：论文白底或极浅暖灰 `#F7F7F5`；不要使用渐变、纹理底、彩色大底。
- 分隔：使用 1 px 浅灰线 `#D8DAD8` 或留白分组，不用厚边框卡片。
- 图像：真实 render 占据主要面积，标签和解释只做导航，不做主视觉。
- 版心：优先按双栏宽度设计，横图建议 3200-3600 px 宽，最终 LaTeX 中可用 `\includegraphics[width=\linewidth]`。

### 2.2 字体与文字

- 英文字体：Helvetica Neue / Helvetica / Arial；LaTeX caption 里可保持论文主字体。
- 图内字号层级：主标签 8-9 pt 等效，次标签 6-7 pt，禁止大面积说明段落。
- 大小写：模块名用 Title Case，参数名用 concise noun phrase；不要全部大写。
- 图内文字原则：只标变量、阶段和必要符号；机制解释放 caption 或正文。

### 2.3 配色

建议色板：

- Ink: `#222426`
- Muted text: `#5C5F62`
- Hairline: `#D8DAD8`
- Warm off-white: `#F7F7F5`
- Controlled accent: `#B15337`
- Secondary blue-gray: `#496A7A`
- Method green: `#5D7F66`

使用原则：

- accent 只用于当前变量、递归回路、或关键贡献路径。
- 模块框不要每类一个鲜艳颜色；最多使用 2 个低饱和色区分 generation / arbitration / rendering。
- 数据曲线若并排出现，使用 colorblind-safe palette，避免 matplotlib `tab10` 的默认视觉味道。

### 2.4 版式规则

- Qualitative depth strip：一行四列或两行四列；列为 depth，行可为 iso/front/detail。只在变量轴上加一个轻量 progression marker。
- Parameter sweep：使用小 multiples。每个 sweep 单独成图，不要把 depth sweep 和参数 sweep 混入同一个大矩阵，除非 seed/camera/material 全锁定且 caption 明确。
- Teaser：3-5 个代表性 mesh/textured results，按形态类别而非脚本文件名排列：vine / porous scaffold / lattice / hopper / DLA coral。
- 方法图：左到右主路径，递归反馈用单独颜色的弧形箭头，真实 case 沿主路径逐步变复杂。

## 3. 已合成的新图

新建文件：

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/vine_depth_textured_strip_20260509_vizworker.png`

设计意图：

- 使用现有 `visuals/vine_depth_textured_showcase_20260509/renders/vine_depth{1..4}_{iso,front}.png`。
- 每列对应 Depth 1-4，主图使用 iso render，小 inset 使用 front render。
- 没有引入新生成结果、点云或伪实验，只做透明边界裁剪、统一排版、标签与轻量进度轴。
- 适合放在 qualitative depth subsection，旁边可配一张 compact metric plot，而不是把所有参数 sweep 塞进同一张图。

注意：当前原始 render 自带深灰背景与地面，视觉重量较重。若远端后续能输出透明背景或统一 studio-light 背景版本，这张 strip 可以进一步提升到更接近最终论文质量。

## 4. 方法论总图建议

建议画成“一个真实 case 贯穿的概念系统图”，而不是模块堆叠图。

### 4.1 推荐模块

从左到右：

1. Seed / substrate
   - 显示初始 anchor、support surface、或目标 bounding region。
2. Grammar state
   - 用 3-4 个符号 token 表达 local rule，不要展示完整工程配置。
3. Recursive expansion
   - 展示 depth 递增的局部生成片段；突出 parent-child attachment、branch transform、termination。
4. Space arbitration
   - 展示 occupancy / collision / competition radius / pruning，建议用半透明 envelope 或局部放大图。
5. Surface realization
   - 展示 skeleton/scaffold 到 mesh 的转换，必要时放 normals/thickness/material slots。
6. Textured mesh output
   - 放真实 textured render，最好是和前面阶段同一个 case。

### 4.2 应放入的公式/算法信息

只放最能解释贡献的三类信息：

- 递归状态更新：`s_{d+1} = G(s_d, z_d, c_d)` 或论文中真实定义的等价形式。
- 空间竞争/接受准则：用一行 score 或 accept/reject gate 表示，不要贴完整伪代码。
- mesh realization：用简短标注说明 sweep / skinning / remeshing / material assignment 的接口。

不建议在方法总图中塞：

- 完整配置文件字段。
- 过多 Blender/GLB/export 工程环节。
- 每个 loss/metric 的曲线。
- 和主贡献关系弱的 implementation detail。

### 4.3 如何避免工程堆叠感

- 用一个 case 贯穿所有阶段，减少“多个孤立方框”的感觉。
- 把递归回路画成结构性视觉元素，而不是普通箭头。
- 每个阶段只保留一个核心名词和一个视觉证据。
- 工程输出链路放到最后一小段：`mesh -> material -> render`，不要让它占据主图中心。
- 若需要展示多样性，把多 case 放在方法图底部作为 output gallery，不要插在流程中间打断主路径。

## 5. 需要主 agent 或远端实验补充的素材

优先级从高到低：

1. 同一 seed、同一 camera、同一 material、同一 lighting 的 depth 1-5 或 1-6 textured mesh renders。
2. 每个 depth 对应的 mesh statistics：vertices、faces、connected components、bbox、surface area、平均/最大 branch length。
3. 同一 case 的中间阶段图：seed/substrate、grammar scaffold、post-arbitration scaffold、mesh before texture、final textured render。
4. 参数 sweep 的锁定条件说明：哪些变量固定，哪些变量变化，数值范围和语义名。
5. 透明背景或统一浅灰 studio 背景 render，最好同时给 iso/front/detail 三个视角。
6. 每个展示图对应的 caption 草稿，明确“qualitative only”还是支持某个定量 claim。

## 6. 建议进入论文的图组结构

- Fig. 1 Teaser：3-5 个高质量 textured mesh，展示形态跨度和材质质量。
- Fig. 2 Method：单 case 贯穿的 recursive grammar + space arbitration + mesh realization。
- Fig. 3 Depth study：同条件 depth strip + compact metrics。
- Fig. 4 Parameter study：每次只扫一个语义参数的小 multiples。
- Fig. 5 Ablation / failure：去掉 competition、去掉 pruning、不同 material/render limitation，保持克制但诚实。

