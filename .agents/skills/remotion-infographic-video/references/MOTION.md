# MOTION：弹簧、缓动、段转场、镜头入场、3D 倾斜

> 数值唯一真源是 `assets/tokens.json` 的 `motion` 字段；工程内统一由 `src/theme/motion.ts` 读取。场景与组件不要自己写弹簧参数。

## 1. 帧率
- 固定 30fps（`motion.fps`，F-12）。时间换算用帧：秒 → 帧 `floor(s × 30 + 0.5)`（由 `build_timeline.py` 完成）。

## 2. 弹簧与缓动
| 用途 | 取值（tokens.json） | 说明 |
|---|---|---|
| 通用入场 `spring` | `motion.spring`：damping 12、stiffness 130、mass 1 | 允许区间 damping 10–14、stiffness 100–160 |
| 砸入大字 `SlamTitle` | `motion.slam`：damping 10、stiffness 160 | 低阻尼、高刚度，有回弹 |
| 缓动 | `motion.easing` = bezier(0.2, 0.8, 0.2, 1) | 所有 `interpolate` 的入场缓动 |
| 出场 | `Easing.in(Easing.cubic)` | 淡出、缩出 |

- 入场统一用 `spring`；需要线性映射时用 `interpolate` + 上面的缓动，并 `extrapolateLeft/Right: 'clamp'`。
- 一个镜头内同时入场的元素建议错开 3–6 帧（`delay` / `at`），避免一起弹出。

## 3. 段转场 `SectionTransition`（段级，storyboard `sections[].transition`）
五种，枚举固定：`wipe | zoom | blur | slide | iris`。
- 入场 `motion.sectionIn` = 14 帧，出场 `motion.sectionOut` = 10 帧。
- 入场时扫过一道段色光带（取该段 `palette`，`screen` 混合）。
- 建议：钩子段用 `zoom` 或 `blur`，流程类用 `slide` / `wipe`，结尾用 `iris`；相邻两段不要用同一种。

## 4. 镜头入场 `Shot`（镜级，storyboard `shots[].entrance`）
三种，枚举固定：`push | rise | zoom`。
- 时长 `motion.shotIn` = 12 帧，从 `motion.shotBlur` = 12px 模糊变清晰。
- `push`：轻微放大推进；`rise`：自下而上升起；`zoom`：由小到大。
- 段转场与镜头入场是两个字段（架构 A-11），不要把 `push` 写进 `transition`，也不要把 `wipe` 写进 `entrance`；`validate.py storyboard` 按 Schema 枚举校验（F-07）。

## 5. 强调动效
- `ImpactShake`：配合 `SlamTitle` 落地时震动，强度 `intensity` 可选，持续几帧即停。
- `KeywordPulse`：在指定帧区间 `range` 内对关键词做脉冲辉光，适合口播里的重读词。
- `NumberRoll`：数字从 `from` 滚到 `value`，`duration` 帧内完成，数字用 mono 字体。
- `StepList`：按 `ranges` 逐项点亮，当前项用 `activeTone`。

## 6. 3D 倾斜（MediaCard）
- `perspective: 1400`，`rotateY` 倾斜（`tilt` 可调），入场时带 `rotateX(4deg)` 回正。
- 倾斜只用于媒体卡片，文字面板保持正视，保证可读。

## 7. 与口播对齐
- 动画触发点以句为单位：场景拿到的 `shots[].from/to` 已是帧；句内本地帧由 `timing/lines.ts` 的工具函数换算（段内本地帧 = `useCurrentFrame()`）。
- 结尾：没有片尾附加帧，片长 = 配音长度（F-06）；收尾动效用 `HoldFade` 在末句区间内完成，末句的停顿长度在稿件里设置（见 [SCRIPT](SCRIPT.md)、[VOICE](VOICE.md)）。

## 8. 确定性
- 任何随机量只用 Remotion 的 `random(seed)`，禁止 `Math.random`、`Date.now`（NF-05）；同一帧两次渲染像素一致（`check_project.sh --determinism` 可选检查）。
