# STYLE：配色、字体、质感与背景层

> 数值唯一真源是 `assets/tokens.json`；`scaffold_project.py` 由它生成工程内 `src/theme/tokens.ts`，`validate.py tokens` 比对两者一致（F-09、NF-06）。本文件说明用法，改配色只改 tokens.json，不改流程和 SKILL.md。

## 1. 配色（tokens.json `colors`）

| 色名 | 用途 | 值 |
|---|---|---|
| `bg` | 全局背景 | `#070A0F` |
| `card` | 卡片底 | `#121821` |
| `text` | 正文 | `#F2F5F8` |
| `textDim` | 次要文字 | `#8B98A8` |
| `gold` | 主数字、重点 | `#F5C542` |
| `green` | 正向、增长 | `#3DDC97` |
| `red` | 警示、下跌 | `#FF5C5C` |
| `blue` | 信息 | `#4DA3FF` |
| `purple` | 辅助强调 | `#9B7BFF` |
| `line` | 线条、坐标轴 | `#2A3544` |
| `badge` / `badgeStroke` | 来源角标底 / 描边 | `#1A2330` / `#3A4A5C` |

- 渐变（`gradients`）：gold、green、red、blue、purple 各三档（亮→主→暗），如金 `#FFE08A→#F5C542→#C8901A`。
- 色调键（`tones`）：`gold | green | red | blue | purple`。组件的 `tone` 与 storyboard 的 `palette` **只写色名，不写色值**。
- 段双色调：每段在 storyboard 里给 `palette: {a, b}`（两个色名），用于背景光晕与 HUD 强调；段与段之间交叉淡化。相邻段建议换一组，避免整片单色。
- 语义约定：上涨/正向用 green，下跌/风险用 red，核心数字用 gold；不要用红绿以外的颜色表达涨跌。

## 2. 字体（tokens.json `fonts`，文件在 `assets/fonts/`）
- `sans` = NotoSansSC（Regular 用于 100–500 字重，Bold 用于 600–900）；`mono` = JetBrainsMono（数字、代码）。均为 OFL 许可，随技能包分发。
- 本地加载：scaffold 把字体复制到工程 `public/fonts/`，加载时用 `delayRender` 等字体就绪，禁止引用在线字体。
- 字号基准（`layout.fontSizes`，按短边 1080 设计）：display 168、h1 120、h2 68、h3 42、body 30、caption 22。实际字号一律经 `useLayout().font(k)` 换算（竖屏 display/h1/h2 会缩小，见 [LAYOUT](LAYOUT.md)），组件里不写像素字号。
- 数字一律用 mono 字体，避免滚动时宽度抖动。

## 3. 质感：伪三维 / 玻璃（tokens.json `glass`、`radius`）
- 玻璃面板 `GlassPanel`：半透明白渐变填充 + 1px 白边（12% 透明度）+ `backdrop-filter: blur(18px) saturate(140%)` + 深色投影 + 内高光。具体值取 `glass.fill / border / blur / saturate / shadow`。
- 圆角：`radius.sm / md / lg / pill`（10 / 18 / 28 / 胶囊）。
- 数字、标题用对应色调的彩色辉光阴影（同色、低透明度）。
- 媒体卡片 `MediaCard`：`perspective: 1400` + `rotateY` 倾斜 + `rotateX(4deg)` 入场，做出三维感（动效细节见 [MOTION](MOTION.md)）。

## 4. 全局背景层 `BackgroundLayer`（tokens.json `background`）
从下到上：
1. 渐变底（`bg` 为基色）。
2. 滚动透视网格：行数 `ceil(height / cell)`，按画布尺寸生成。
3. 段色径向光晕：取当前段 `palette.a / b`，缓慢正弦漂移，`blur` = `background.glowBlur`（30px）。
4. 上浮粒子：数量 `background.particles`（46）；坐标由确定性种子生成（`layers/particles.ts` 的 `particles(w, h, seed, count)`），禁止 `Math.random` / `Date.now`（NF-05）。
5. 分形噪点：overlay 混合，不透明度 `background.noiseOpacity`（7%）。
6. 暗角。

背景层全部按 `useVideoConfig()` 的 width/height 生成，不写死画布尺寸（修正参考项目的问题，F-10）。

## 5. 工程分层（固定四种 `data-layer`）
| 层 | `data-layer` | 内容 |
|---|---|---|
| BackgroundLayer | `background` | 上节背景 |
| 场景（各段 `src/scenes/Sxx.tsx`） | `scene` | 组件与素材 |
| HUDLayer | `hud` | 段名 + 进度 |
| SubtitleLayer | `subtitle` | 字幕，位置取 `layout.subtitleY` |

- DOM 中不允许出现其他 `data-layer` 取值，`check_project.sh` 的 safe_area 步骤会检查（F-09）。
- **没有片尾署名层**：署名只出现在镜头内 `SourceBadge`、各平台简介署名段和 `deliverable.json.credits`（见 [ASSETS](ASSETS.md)）。

## 6. 内容与标注规则
- 上屏数字必须带来源角标（`SourceBadge`，如“据 XX”）；示意性质的图表必须带 `IllustrativeTag`（固定文字“示意”）。
- 角标和署名只写来源名称，不放链接。
- 字幕与正文颜色用 `text`，次要信息用 `textDim`；不要在深色背景上用 `line` 色写字。

## 7. 改风格的正确方式
1. 改 `assets/tokens.json`（颜色、字号、玻璃、背景参数）。
2. 重新 `scaffold_project.py --force` 生成工程（或重新生成 `src/theme/tokens.ts`）。
3. 跑 `python3 scripts/validate.py tokens --json assets/tokens.json --ts <slug>/project/src/theme/tokens.ts` 与 `check_project.sh`。
不需要改 SKILL.md、脚本或场景代码；场景代码中如出现色值，即违反本规范。
