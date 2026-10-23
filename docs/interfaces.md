# 接口说明（与实现一致）

技能根：`.agents/skills/remotion-infographic-video/`。下列路径均相对技能根，除非标明仓库根。

## 1. 统一约定

- stdout **最后一行** = JSON 摘要（成功/失败都尽量给出）
- `argparse` 一律 `allow_abbrev=False`；未知/缩写参数 → **退出码 2**
- 退出码（架构 §4.0 / `scripts/lib/errors.py`）：

| 码 | 常量 | 含义 |
|---|---|---|
| 0 | OK | 成功 |
| 1 | UNEXPECTED | 未预期错误 |
| 2 | USAGE | 用法/参数错误 |
| 3 | MISSING_CONFIG | 缺 `.env` / Key（或前置命令缺失） |
| 4 | AUTH | 鉴权失败（Key 无效） |
| 5 | BAD_INPUT | 输入不合 Schema / 稿件不合法 |
| 6 | SERVICE | 服务侧失败或句级重试耗尽 |
| 7 | CHECK_FAILED | 自检/响度/发布校验等未通过 |

## 2. 步骤 CLI

| 步骤 | 命令 | 主要输入 → 产出 |
|---|---|---|
| 0 | `python3 scripts/check_env.py [--skill-dir D] [--no-cmd-check]` | 读技能 `.env`；检查 node/python3/ffmpeg/ffprobe |
| 1 | （Agent 写）`<slug>/job.json` | topic、slug、aspect/width/height、platforms? |
| 2 | `python3 scripts/validate.py sources <script.md> <sources.md>` | 稿中数字均有出处 |
| 3 | `python3 scripts/tts_doubao.py <script.md> --out-dir <slug>/voice [--only] [--max-attempts 1..3] [--dry-run]` | `full.mp3` + `timeline.json` + `subtitles.json` |
| 4 | `python3 scripts/validate.py storyboard <storyboard.json> --timeline T [--manifest M] [--sources S]` | 句覆盖、枚举、组件名 |
| 5 | `python3 scripts/fetch_asset.py add|prune|verify|credits-diff …` | `assets-manifest.json` |
| 6 | `python3 scripts/scaffold_project.py --job job.json --out <slug>/project` | Remotion 工程 + 工程内 AGENTS.md |
| 6 | `python3 scripts/build_timeline.py --timeline … --storyboard … --subtitles … --manifest … --project …` | `src/data/*.ts` |
| 7 | `bash scripts/check_project.sh <slug>` | `check/report.json` |
| 8 | `bash scripts/render.sh <slug>` | `out/video.mp4` + 封面 PNG |
| 9 | `python3 scripts/validate.py publish\|deliverable\|leak <slug>` | 文案校验 / `deliverable.json` / 泄露扫描 |

可选：环境中有同等 I/O 的 MCP `tts_synthesize` 时可替代步骤 3 的脚本；timeline 仍须过同一 Schema。

## 3. `validate.py` 子命令

```
timeline | subtitles | manifest | job | storyboard | sources |
tokens | video | publish | deliverable | leak
```

退出码：0 通过；2 用法；3 缺 Key（leak）；5 Schema；7 校验未通过。

## 4. 关键产物 Schema

目录：`assets/schemas/`

| 文件 | 用途 |
|---|---|
| `job.schema.json` | 选题任务：aspect landscape/portrait；宽高 1920×1080 或 1080×1440；fps=30 |
| `timeline.schema.json` | 配音时间轴；句必填 `speech_end_s`（v1.9） |
| `subtitles.schema.json` | 字幕 cues |
| `storyboard.schema.json` | 分镜 sections/shots |
| `assets-manifest.schema.json` | `{version:1, assets:[…]}` |
| `sources.schema.json` | sources.md 内嵌 JSON |
| `script-lines.schema.json` | 解析后的句列表 |
| `platforms.schema.json` | PUBLISH.md 机读平台表 |
| `publish-check.schema.json` | `publish/check.json` |
| `check-report.schema.json` | `check/report.json` |
| `licenses.schema.json` | `assets/licenses.json` |

## 5. timeline 句字段（v1.9）

每句必填：`id, section, text, context, silence_ms, speech_rate, start, speech_end_s, end, duration_s`

- `speech_end_s` = start + 发声时长
- `end` = speech_end_s + silence_ms/1000（末句可钳位到 `audio_seconds`）
- `duration_s` = end − start（**含**句后停顿）
- 字幕窗口：`[start, speech_end_s]`；段/镜头：`[start, end)`

详见 `references/VOICE.md`。

## 6. 发布文案目录

```
<slug>/publish/
├── cover_1920x1080.png   # 或 cover_1080x1440.png
├── check.json
├── <platform>/title.txt
├── <platform>/description.txt   # 末尾「素材署名：」段由 validate publish 幂等补全
└── <platform>/tags.txt          # 一行一个；无全局「5–10 个」规则
```

默认平台（`PUBLISH.md` → `default_targets`）：douyin、bilibili、xiaohongshu、channels、youtube。用户点名平台时写入 `job.platforms`。

## 7. 机读规范块

- `references/LAYOUT.md`：恰好一个 JSON（`version, portrait_keywords, landscape_keywords`）
- `references/PUBLISH.md`：恰好一个 JSON（`version, default_targets, platforms`）
