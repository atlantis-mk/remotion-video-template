# LAYOUT：横竖屏与安全区

> 下方 JSON 块是画幅关键词表的唯一来源（`scripts/lib/job.py` 的 `resolve_aspect` 读取）；本文件恰好只有这一个 json 代码块。

## 画幅判定
- 默认横屏 16:9 1920×1080；用户说“竖屏” → 竖屏 3:4 1080×1440。
- 只认“横屏/竖屏”两个词；平台名（抖音、视频号、小红书等）不影响画幅。两个词都出现时取最后出现的那个。
- 下方 JSON 块是关键词表的唯一来源（`scripts/lib/job.py` 读取），改词只改这里。

```json
{
  "version": 1,
  "portrait_keywords": ["竖屏"],
  "landscape_keywords": ["横屏"]
}
```

## 画布与封面预设
- 唯一常量处：工程内 `src/layout/presets.ts`（`CANVAS_PRESETS`、`COVER_PRESETS`），其他文件禁止写死画布尺寸。
- 封面：横屏 `publish/cover_1920x1080.png`；竖屏 `publish/cover_1080x1440.png`（各平台共用，由 `render.sh` 写出）。

## 安全区
- 安全边距、字幕区位置等比例数值在 `assets/tokens.json` 的 `layout` 字段；组件一律通过 `useLayout()` 取尺寸。
- `check_project.sh` 的 safe_area 步骤检查所有文本元素包围盒位于安全区内。

## 布局核心 `computeLayout`
- 纯函数 `src/layout/computeLayout.ts`：`computeLayout(width, height, tokens.layout)`；Hook `useLayout()` = 用 `useVideoConfig()` 的宽高调用它。所有组件只读 `useLayout()`，禁止读画布常量。
- 返回：`width/height`、`orientation`、`unit`（= 短边 / 1080，两种画幅下都是 1）、`safe`（四边绝对 px）、`content`（安全区减去字幕带）、`columns`、`font(k)`、`subtitleY`、`hud`。
- `check_project.sh` 的安全区检测与渲染用的是同一个 `computeLayout`，保证判定口径一致。

| 项 | 横屏 1920×1080 | 竖屏 1080×1440 |
|---|---|---|
| columns | 2（左右分栏，图文并排） | 1（单列堆叠） |
| 标题字号 display/h1/h2 | 基准 × 1.0 | 基准 × 0.8（防止 6 个汉字的大标题溢出） |
| h3/body/caption | 基准 | 基准（不缩，保证可读） |
| 安全边距、字幕带 | 取 `tokens.json.layout.safe.landscape` | 取 `tokens.json.layout.safe.portrait` |

比例数值以 `assets/tokens.json` 为准，调整只改那里。

## 写场景时的规则
- 并排内容用 `<Split>`：横屏左右、竖屏自动上下，不要自己按画幅写分支。
- `GlassPanel`、`MediaCard` 的宽度取 `content.w` 的比例；字号用 `font(k)`，不写像素值。
- 文本元素不得越出安全区；字幕带内只放字幕，HUD 放在上安全边距内。
- 背景粒子坐标、网格行数按 width/height 生成（粒子种子固定，见 [STYLE](STYLE.md)）。
- 禁止在 `src/` 中写 `1080`、`1440`、`1920`（presets.ts 除外）；`check_project.sh` 的 static 步骤用 rg 检查。

## 同一工程切换画幅
- 画幅存在 `job.json.aspect`（scaffold 时缺省补为 `landscape`，并回写一致的 width/height）；工程内 `src/data/job.ts` 只导出 `ASPECT`、`PLATFORMS`，不含像素数字。
- 渲染另一种画幅：`--props='{"aspect":"portrait"}'`，由 `calculateMetadata` 覆盖宽高；自检可用 `check_project.sh <slug> --aspect both` 横竖各跑一遍。
- 封面跟随画幅，只出一份，各平台共用。
