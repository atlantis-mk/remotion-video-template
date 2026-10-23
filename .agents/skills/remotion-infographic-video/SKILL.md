---
name: remotion-infographic-video
description: 用一个选题全自动制作深色信息图风格的口播视频：写口播稿、豆包配音、分镜与素材、Remotion 动画、渲染成片、封面与发布文案。用户说“开始制作”、要做口播/信息图/财经科技解说视频时使用。支持横屏与竖屏。
compatibility: 需要 Node 18+、Python 3、ffmpeg/ffprobe 与网络；配音 Key 放在本技能目录 .env（交付仓路径 .agents/skills/remotion-infographic-video/.env）。
---

# 信息图口播视频

## 位置与交付布局（架构 v1.11）
- 交付仓根必有 `AGENTS.md`（如何用本模板）；本技能固定在 `.agents/skills/remotion-infographic-video/`。
- `tests/` 在仓库根（与 `.agents/` 同级），属开发门禁/CI，**不属于**技能运行时，不随「只装技能」复制。
- `.env` 只在本技能目录，**不是**仓库根。

## 使用前准备（复制即用）
1. **复制**：
   - **整仓使用**：克隆/复制交付仓库根并打开（含根 `AGENTS.md` 与 `tests/`）。
   - **只装技能**：把 `.agents/skills/remotion-infographic-video/` 复制到目标项目的**同名路径**（含 `scripts/` 与其下 `lib/`）。
   - 技能包本身不需要 `pip` / `npm` 安装；`scripts/` 只用 Python 标准库，配好 `.env` 后即可跑步骤 0–5。
2. **配置 `.env`**：在本技能目录执行 `cp .env.example .env`，编辑 `.env` 填写：
   - 必填：`DOUBAO_TTS_API_KEY=`（等号后写入 Key，不要引号）
   - 可选：`DOUBAO_SPEAKER=`（默认音色见 [VOICE](references/VOICE.md)）
   - `.env` 已被 `.gitignore` 忽略，不要把 Key 贴进聊天，也不要换其他配音引擎。
3. **环境前提**（自行安装，脚本不代装）：Node 18+、Python 3、ffmpeg、ffprobe、网络。
4. **开始制作**：用户说「开始制作」或同等意图时：
   - 先跑 `python3 scripts/check_env.py`（可用 `--skill-dir <本技能包绝对路径>`；默认即本目录）。
   - 退出码 3：提示在 `.agents/skills/remotion-infographic-video/.env`（或本技能绝对路径下的 `.env`）填写 `DOUBAO_TTS_API_KEY`，等用户回复「填好了」后重跑；此前不配音、不建工程。
   - 通过后：消息里已有选题则直接进入固定步骤；否则**只问一句**选题（可注明「竖屏」；默认横屏 1920×1080，竖屏 1080×1440，规则见 [LAYOUT](references/LAYOUT.md)）。平台名不影响画幅。

## 硬规则
- Key 只从本技能目录 `.env`（交付仓为 `.agents/skills/remotion-infographic-video/.env`）的 `DOUBAO_TTS_API_KEY` 读取；不让用户在聊天里贴 Key，不换配音引擎，不在任何输出里显示 Key。
- 不发布、不上传：只产出成片、封面和文案文件。
- 数字必须有出处；上屏数字带来源角标；示意图标“示意”。
- 每个脚本 stdout 最后一行是 JSON 摘要；按退出码处理：3 缺 Key（提示填 `.env`，停止）、4 鉴权失败（停止）、5 修正上游产物、6 只重跑失败项、7 进入修复。

## 固定步骤
0. 前置检查：`python3 scripts/check_env.py`。退出码 3 时按上文提示填 `.env` 后重跑。
1. 收题：确定 topic、slug、画幅，写 `<slug>/job.json`（未提画幅默认横屏）；用户点名平台时写 `platforms`，否则按 [PUBLISH](references/PUBLISH.md) 的默认平台。
2. 写稿：写 `script.md`（`## Sxx 段名` + `- [01] 文本 {context: … | rate: 0 | pause: 300}`）和 `sources.md`（末尾 json 块），运行 `python3 scripts/validate.py sources <slug>/script.md <slug>/sources.md`；无出处的数字必须删掉或补来源。
3. 配音：如果环境中有输入输出等同的 MCP 配音工具（tts_synthesize）可用就用它，否则运行 `python3 scripts/tts_doubao.py <slug>/script.md --out-dir <slug>/voice`；两者产出的 timeline.json 用同一 Schema（`assets/schemas/`）校验：`python3 scripts/validate.py timeline <slug>/voice/timeline.json`。失败句用 `--only` 重跑。
4. 分镜：写 `storyboard.json`（每句至少被一个镜头覆盖，段转场与镜头入场取枚举值），运行 `python3 scripts/validate.py storyboard <slug>/storyboard.json --timeline <slug>/voice/timeline.json`。
5. 素材：用 `python3 scripts/fetch_asset.py` 的 `add` 登记每个素材，`prune` 清掉未用素材；授权不明的素材不得使用。
6. 建工程：`python3 scripts/scaffold_project.py --job <slug>/job.json --out <slug>/project` 生成工程，按示例写各段场景（`assets/example/`），再运行 `python3 scripts/build_timeline.py --timeline <slug>/voice/timeline.json --storyboard <slug>/storyboard.json --subtitles <slug>/voice/subtitles.json --manifest <slug>/assets-manifest.json --project <slug>/project`，然后在工程内 `npm ci`。
7. 自检：`bash scripts/check_project.sh <slug>`；失败时读 `check/report.json` 修复后重跑，总共最多 3 次，仍失败就停下报告。
8. 渲染：`bash scripts/render.sh <slug>` 产出成片（`<slug>/out/video.mp4`）与封面（`<slug>/publish/cover_<W>x<H>.png`），并自动验收。
9. 发布文案与交付：按 [PUBLISH](references/PUBLISH.md) 为每个目标平台各写一套 `publish/<平台>/title.txt`、`description.txt`，标签按平台写 `publish/<平台>/tags.txt`（一行一个），运行 `python3 scripts/validate.py publish <slug>`、`python3 scripts/validate.py deliverable <slug>`、`python3 scripts/validate.py leak <slug>`，再用 `python3 scripts/fetch_asset.py credits-diff --manifest <slug>/assets-manifest.json --slug-dir <slug>` 复核署名。

## 风格硬规则摘要
- 配色、字号、动效数值只来自 `assets/tokens.json`，背景色基调 #070A0F；场景代码不写色值（[STYLE](references/STYLE.md)）。
- 入场统一弹簧，段转场 5 种、镜头入场 3 种，取 storyboard 枚举（[MOTION](references/MOTION.md)）。
- 组件只用注册表内的 15 个，清单外的在工程内新写并用 tokens + `useLayout()`（[COMPONENTS](references/COMPONENTS.md)）。
- 只有四层 background / scene / hud / subtitle，没有片尾署名画面；片长 = 配音长度。
- 随机只用 `random(seed)`，禁止 Math.random。
- 布局从画布宽高推导，`src/` 中只有 `src/layout/presets.ts` 可写画布尺寸（[LAYOUT](references/LAYOUT.md)）。
- 稿件写法见 [SCRIPT](references/SCRIPT.md)，配音参数见 [VOICE](references/VOICE.md)，素材授权与署名见 [ASSETS](references/ASSETS.md)。

## 禁止事项
- 不发布、不上传到任何平台。
- 不泄露 Key：不显示、不写入产物，不让用户在聊天中贴 Key，不换其他配音引擎。
- 不用授权不明的素材；署名、简介、标题不放链接。
- 不编造数据：没有出处的数字不进稿件、不上屏。
- 选题之后到交付之间不向用户提问，也不索要任何素材。

## 交付
一次性回报 `deliverable.json` 中的内容：成片路径与时长、画幅、封面、各平台标题与简介、标签、素材署名、输出目录和备注。
