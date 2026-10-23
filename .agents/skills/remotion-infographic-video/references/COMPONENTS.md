# COMPONENTS：风格组件目录

> 组件位于工程 `src/components/`（来自 `assets/project-template`），注册表 `components/registry.ts` 同时供 `GenericScene` 渲染和 `validate.py storyboard` 校验：storyboard 的 `component` 必须是注册表中的名字。清单按架构 §4.12：15 个组件 + 3 个层。
> 通用约定：尺寸一律来自 `useLayout()`，颜色来自 tokens（`tone` 只写色名 `gold|green|red|blue|purple`）；`at`、`range` 等帧数是**场景内本地帧**；props 为最小集，未列出的不要传。

## 1. 容器与布局
| 组件 | props | 用途 / 适用口播内容 |
|---|---|---|
| `GlassPanel` | `children`；`tone?`；`radius?: 'sm'\|'md'\|'lg'\|'pill'`；`delay?` | 使用最多的承载容器：要点、定义、结论卡片 |
| `Split` | `primary`；`secondary`；`ratio?` | 图文并排；横屏左右分栏、竖屏自动上下堆叠（`columns` 1/2） |
| `Shot` | `entrance: 'push'\|'rise'\|'zoom'`；`at`；`children` | 镜头入场包装，12 帧由模糊到清晰 |
| `SectionTransition` | `type: 'wipe'\|'zoom'\|'blur'\|'slide'\|'iris'`；`durationInFrames`；`tone: {a, b}`；`children` | 段转场，入 14 帧 / 出 10 帧 + 段色光带（由 Main 按 SECTIONS 自动套用） |

## 2. 文字与强调
| 组件 | props | 用途 |
|---|---|---|
| `SlamTitle` | `text`；`at`；`size?: 'display'\|'h1'`；`tone?` | 钩子、结论大字砸入 |
| `ImpactShake` | `at`；`intensity?`；`children` | 包住 SlamTitle 做落地震动 |
| `KeywordPulse` | `text`；`range: {from, to}`；`tone?` | 口播重读词的脉冲强调 |
| `StepList` | `items: string[]`；`ranges: Range[]`；`activeTone?` | 流程、清单、“三点原因”，随口播逐项点亮 |

## 3. 数据信息图
| 组件 | props | 用途 |
|---|---|---|
| `NumberRoll` | `value`；`from?`；`at`；`duration?`；`prefix?`；`suffix?`；`decimals?`；`tone?`；`source?`；`size?: 'display'\|'h1'\|'h2'` | 单个关键数字（金额、增速、排名） |
| `CompareBars` | `items: {label, value, tone?}[]`；`at`；`unit?`；`source?`；`illustrative?` | 两到多项对比 |

- 数字组件的 `source` 语义上必填：storyboard 中 `display_numbers` 必须带 `source_claim_id`，否则校验失败；传了 `source` 会自动渲染 `SourceBadge`。
- `illustrative: true` 时组件自带“示意”标。

## 4. 合规标注
| 组件 | props | 用途 |
|---|---|---|
| `SourceBadge` | `text` | 来源角标“据 XX”或素材署名“作者 · 来源名称 · 许可简写”；只写名称不放链接；根节点带 `data-role="source-badge"` |
| `IllustrativeTag` | 无 | 固定文字“示意” |

## 5. 媒体与收尾
| 组件 | props | 用途 |
|---|---|---|
| `MediaCard` | `src`；`at`；`tilt?`；`attribution?`；`fit?: 'cover'\|'contain'` | 图片/视频卡片，3D 倾斜入场；`attribution` 由 `build_timeline.py` 从 manifest 注入，不要手填 |
| `FollowCTA` | `text`；`at` | 结尾关注引导 |
| `HoldFade` | `startAt`；`durationInFrames`；`children` | 末句内定格淡出，代替片尾附加帧 |

## 6. 层（不计入组件清单，由 Main 固定挂载）
- `BackgroundLayer`（`data-layer="background"`）：渐变、透视网格、段色光晕、确定性粒子、噪点、暗角，按 width/height 生成。
- `HUDLayer`（`hud`）：段名 + 进度。
- `SubtitleLayer`（`subtitle`）：读 subtitles 数据，位置取 `layout.subtitleY`。
- 场景内容包在 `data-layer="scene"` 中。不要新增其他层，也不要做片尾署名画面。

## 7. 场景写法
- 每段一个 `src/scenes/<Sxx>.tsx`，导出 `React.FC<SceneProps>`，`SceneProps = {section, shots}`；`src/scenes/index.ts` 注册表由 `build_timeline.py` 生成。
- 某段没写场景文件时回退 `GenericScene`：按 `shot.component` 从注册表渲染、`shot.props` 作为 props，保证 `tsc` 能过。
- 写法范例：`assets/example/scenes/S01..S05.tsx`。示例分段与组件对应：

| 段 | 手法 | 组件 |
|---|---|---|
| S01 钩子 | 砸入大字 + 震动、段色光晕 | SlamTitle、ImpactShake、KeywordPulse |
| S02 流程 | 玻璃面板列表、步骤条逐个入场 | GlassPanel、StepList、Shot |
| S03 数字 | 数字滚动、对比柱、来源角标、示意标 | NumberRoll、CompareBars、SourceBadge、IllustrativeTag |
| S04 画幅 | 横竖分栏、媒体卡片 3D 倾斜 | Split、MediaCard、SourceBadge |
| S05 结尾 | 关注引导、定格淡出 | FollowCTA、HoldFade |

## 8. 组合建议
- 一个镜头一个视觉焦点：大字 / 一个数字 / 一组对比 / 一张图，不要堆叠。
- 数据段：`GlassPanel` 包 `NumberRoll`，下一镜用 `CompareBars` 给参照系。
- 论证段：`Split`（左观点 `GlassPanel`、右 `MediaCard` 或 `CompareBars`）。
- 清单外的视觉可以在**本次工程内**新写组件，但必须用 `useLayout()` 与 tokens、不写死尺寸和色值，且不回写技能包；要让 GenericScene 能用，需登记到工程的 `registry.ts`。
