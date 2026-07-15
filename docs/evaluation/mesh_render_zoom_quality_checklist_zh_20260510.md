# Mesh/PBR 渲染与 zoom-in 质量验收 checklist（2026-05-10）

适用范围：strict matched case gallery、论文主图候选、supplement zoom panel、raw render 与 contact sheet 归档。本文只定义验收标准和存储规范，不代表所有 case 已经通过。

## 0. 总原则

论文候选图必须来自真实 mesh/GLB 的 PBR 或中性 mesh render。overview、callout 和 zoom 必须能追溯到同一个 case、同一个 mesh/GLB、同一套相机/渲染参数和同一份 manifest。任何只靠 matplotlib preview、point cloud、2D crop 或局部好看但全局不合格的图，都只能做诊断材料，不能作为主文正例。

## 1. Overview 基础验收

每个 case 的 overview 先过这组硬条件；任一失败则不进入论文候选 contact sheet。

- [ ] 对象摆正：主轴、树干、根系或晶体主体不能明显歪斜；需要展示 upright 语义的 tree/pine/crown 必须垂直稳定。
- [ ] 对象居中：主体完整落在画布中央，边缘不能裁掉 terminal tip、root hair、coral branch、facet 或 lattice copy。
- [ ] 白底：背景必须为纯白或接近纯白，不能有透明棋盘、灰底、渐变、matplotlib 坐标轴、网格线或阴影平面抢视觉。
- [ ] 正方形：overview 输出为正方形画布；推荐 `1024x1024` 或统一下采样尺寸。
- [ ] 同尺度：同一对 baseline/ours 的 bbox 归一化和相机距离一致；不能把 ours 放大、baseline 缩小来制造优势。
- [ ] 真 mesh/PBR：最终候选必须来自 GLB/OBJ mesh 渲染；允许中性材质和 PBR 材质各出一版，但必须标明。
- [ ] 形态可读：全景能读出目标类别和递归模式，例如 branch hierarchy、root fan、frontier accretion、transform-copy orbit、facet/lattice。
- [ ] 没有明显渲染伪影：无黑面、破面、飞面、异常透明、贴图错位、过曝、严重锯齿或单张图里对象被阴影吞掉。

## 2. Zoom-in 与 callout 验收

zoom-in 的目的不是裁一块好看的纹理，而是证明同一个 3D mesh 在局部仍保留递归结构。

- [ ] overview 与 zoom 同尺寸：每张 zoom render 的像素尺寸必须与 overview 一致，不能把低分辨率局部 crop 放大后混用。
- [ ] 真 camera zoom：zoom 必须通过调整 3D camera target、distance、focal length 或 orthographic scale 重新渲染；2D crop 只能作为选区草稿或 diagnostic。
- [ ] callout 框来自 overview：overview 上的 callout 框必须对应 zoom 的真实相机目标区域；框的位置、大小、颜色和编号写入 manifest。
- [ ] callout 选择细节区域：优先框住 branch junction、root attachment、coral frontier neck、tip cluster、facet/cavity、transform-copy level、radial bridge、lattice contact，而不是空白、树干中段或只有纹理的平滑表面。
- [ ] baseline 与 ours 对齐：同一 matched pair 的 zoom 类型一致；baseline 看 junction，ours 也看 junction；baseline 看 terminal tip，ours 也看 terminal tip。
- [ ] 局部仍可读：zoom 后能看见连接、分叉、层级、frontier attachment、copy relation 或 facet contact；不能只是材质噪声或圆柱表面。
- [ ] 不用树干-only zoom：tree/pine/crown 类不能只 zoom 主干或粗杆，必须至少包含一个分叉、叶/针/末端或 crown 细节。
- [ ] 不用失败遮挡：不能把全局断裂、blob、歪斜、类别错误的 case 用局部 zoom 遮住；zoom 通过不等于 overview 通过。

推荐每个正例保留三类 zoom：

| Zoom | 目标区域 | 合格信号 |
|---|---|---|
| `zoom_root_or_seed` | root/seed/trunk base/initial anchor | 能看见主体从 root/seed 合理发出，不是悬浮拼接。 |
| `zoom_junction_or_frontier` | branch junction/contact/frontier neck/radial bridge | 能看见递归连接和局部拓扑，不是贴图掩盖。 |
| `zoom_tip_or_facet` | terminal tip/root hair/coral tip/facet/cavity/copy level | 能看见末端细节和层级，不是树干-only 或平面 crop。 |

## 3. Raw 图与 contact sheet 存储规范

raw render 和 contact sheet 分开存，避免后续无法追溯。

### 3.1 每个 case 的 raw 文件

建议每个 case 至少保留：

- `case_id__overview_mesh_white.png`
- `case_id__overview_pbr_white.png`
- `case_id__zoom_root_or_seed_mesh_white.png`
- `case_id__zoom_junction_or_frontier_mesh_white.png`
- `case_id__zoom_tip_or_facet_mesh_white.png`
- `case_id__overview_callout_overlay.png`
- `case_id__render_manifest.json`

如果同时渲染 baseline 和 ours，文件名必须包含 `method` 或 `source_run`，例如：

- `v8_frontier_refine__dla_coral_seed42__ours__overview_pbr_white.png`
- `traditional_dla__dla_coral_seed42__baseline__zoom_frontier_mesh_white.png`

### 3.2 Manifest 必填字段

每个 `render_manifest.json` 至少记录：

| 字段 | 含义 |
|---|---|
| `case_id` | 唯一 case 名。 |
| `method` | `traditional_baseline`、`ours`、`ablation` 或其他明确方法名。 |
| `source_run` | 远端或本地来源 run，不要只写 gallery 路径。 |
| `mesh_path` / `glb_path` | 渲染使用的真实资产路径。 |
| `render_engine` | Blender/Eevee/Cycles/其他；注明 mesh 或 PBR。 |
| `image_size` | overview 与 zoom 的像素尺寸，必须一致。 |
| `background` | 白底设置。 |
| `camera_overview` | overview 的相机位置、target、orthographic scale 或 focal length。 |
| `camera_zoom_*` | 每个 zoom 的相机参数。 |
| `callout_boxes` | overview 坐标系下的框坐标、编号和对应 zoom 文件。 |
| `qa_status` | `pass`、`diagnostic_only` 或 `reject_for_paper`。 |
| `reject_reason` | 不合格图必须写明原因。 |

### 3.3 Contact sheet

- [ ] contact sheet 只引用已经通过 raw QA 的图，不能直接从临时 crop 或 notebook 输出拼。
- [ ] 每格标签包含 `case_id`、`method`、`family` 和 `render_type`，不要只写漂亮别名。
- [ ] 同一 sheet 内图片尺寸、边距、背景和文本字号一致。
- [ ] 主文候选 sheet 与 diagnostic sheet 分开；失败图可以集中在 `negative`、`diagnostic` 或 `reject_for_paper` sheet。
- [ ] contact sheet 旁边保留 `contact_sheet_manifest.csv`，列出每格来源 raw 文件。

## 4. 不能进论文主文正例的图

以下图可以做 debug、appendix failure 或筛选记录，但不能作为主文正例、不能用于证明 mesh/PBR asset quality。

| 类型 | 不能进论文的原因 | 允许用途 |
|---|---|---|
| matplotlib 图 | 常含坐标轴、投影伪影、非 PBR、非真实相机 render。 | 方法示意、debug、metric 可视化。 |
| point cloud preview | 不是最终 mesh surface，不能证明 GLB/PBR 或 surface quality。 | 中间状态、occupancy/debug。 |
| 2D crop-only zoom | 不是 camera-level zoom，无法证明同一 3D 局部可渲染。 | callout 选区草稿、临时审图。 |
| 歪斜图 | 影响类别可读性和公平比较，尤其 tree/crown/root。 | 失败边界或待重渲染记录。 |
| 树干-only zoom | 避开真正递归细节，不能证明 branch/tip/junction。 | 若用于说明 trunk material，必须标 diagnostic。 |
| 只看纹理的局部图 | PBR 漂亮但结构不可读，不能支持递归 claim。 | 材质质量补充图。 |
| 全景失败但局部漂亮 | 选择性遮盖失败，不能作为 case 通过证据。 | 失败分析。 |
| 背景不统一或非正方形图 | 不能公平拼接比较，容易误导尺度。 | 原始记录，需重渲染。 |
| 无 manifest 图 | 无法追溯 mesh、相机和来源。 | 不进入正式图库。 |

## 5. 论文准入分级

| 等级 | 条件 | 论文用途 |
|---|---|---|
| `paper_main_pass` | matched-task、overview、camera zoom、callout、mesh/PBR、manifest 和指标全部通过。 | 主文正例。 |
| `paper_supp_pass` | 结构或渲染基本通过，但类别/自然度/局部细节略弱。 | supplement 或扩展矩阵。 |
| `diagnostic_only` | 可说明碎裂、过平滑、blocky、wrong mode、projection failure。 | ablation/failure。 |
| `reject_for_paper` | matplotlib/pointcloud/2D crop-only/歪斜/树干-only/无 manifest/非 matched。 | 不进论文图库。 |

## 6. 人审最小流程

1. 先看 overview：摆正、白底、正方形、类别、递归模式、全局连通感。
2. 再看 callout overlay：框是否选中真正细节区域，是否避开失败部位。
3. 再看 zoom：确认是真 camera zoom、同尺寸、局部结构可读。
4. 查 raw 文件和 manifest：确认图来自同一 mesh/GLB，路径和相机参数可复现。
5. 标注 `qa_status` 与 `reject_reason`：不要让不合格图混入主文候选 sheet。

最保守规则：如果一个图需要解释很久 reviewer 才能看出它是 tree/root/coral/frontier/IFS，或者需要依赖 2D crop 才看起来合格，则不作为主文正例。
