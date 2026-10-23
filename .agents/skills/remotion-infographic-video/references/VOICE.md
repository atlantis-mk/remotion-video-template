# VOICE：豆包配音参数与表现力

> 配音只用豆包（`scripts/tts_doubao.py`，或输入输出等同的 MCP 工具 `tts_synthesize`）。不改用其他引擎绕过，Key 只从本技能目录 `.env` 读取（交付仓为 `.agents/skills/remotion-infographic-video/.env`，不是仓库根；F-05、F-17）。

## 1. 命令
```
python3 scripts/tts_doubao.py <slug>/script.md --out-dir <slug>/voice \
       [--speaker ID] [--only 03,07] [--max-attempts 3] [--dry-run]
```
- 产出：`voice/full.mp3`、`voice/timeline.json`、`voice/subtitles.json`（以及 `parts/` 下每句音频）。
- `--only`：只重合成指定句并重新拼接；默认跳过 `parts/` 中已存在且文本哈希一致的句（NF-07）。
- `--max-attempts`：每句总尝试次数，上限 3（首发 + 最多 2 次重试）；取值须为 1–3，否则 argparse 以退出码 2 拒绝（不接受旧参数 `--retries`）。
- `--dry-run`：只解析稿件、检查配置，不调用接口。
- 校验：`python3 scripts/validate.py timeline <slug>/voice/timeline.json`（脚本与 MCP 产出用同一 Schema `assets/schemas/timeline.schema.json`）。

## 2. 音色（speaker）
- 优先级：`--speaker` > `.env` 的 `DOUBAO_SPEAKER` > 本文件默认值。
- **默认音色：`zh_male_m191_uranus_bigtts`**（与参考项目一致）。
- 换默认音色只改 `.env` 的 `DOUBAO_SPEAKER`，不改流程。

## 3. 句级参数（写在 script.md 每句末尾的 `{}` 中）
| 字段 | 写法 | 默认 | 说明 |
|---|---|---|---|
| `context` | `context: 用略带惊讶但克制的播报语气说` | 无 | 语气提示，传给豆包作上下文（context_texts），不会被读出来 |
| `rate` | `rate: -8` | 0 | 语速，取值 -50..100；负数更慢 |
| `pause` | `pause: 350` | 300（ms） | 本句之后的静音 `silence_ms`，计入时间轴 |

字段可省略，省略即用默认值。格式详见 [SCRIPT](SCRIPT.md)。

## 4. 表现力做法
- **语气靠 context，不靠标点堆叠**：每段第一句写清语气（如“笃定”“轻松收尾”“强调规则”），同段后续句可省。
- **重点句放慢**：结论句 `rate: -5 ~ -10`，配合 `pause: 450–500` 留出画面强调时间。
- **段落边界加长停顿**：段末句 `pause` 400–500，段内 250–350。
- **末句**：没有片尾补静音（片长 = 配音长度，F-06），收尾留白只能来自末句的 `pause`；建议末句 200–500ms，并用 `HoldFade` 在末句内淡出。
- 数字用汉字读法写进稿件（如“一千五百亿”），上屏写法放 storyboard 的 `display_numbers`。
- 英文缩写容易误读时，在稿件里写成读法（如“A I”），或换中文说法。

## 5. 时间轴与字幕
- `timeline.json` 每句含 `id, section, text, context, silence_ms, speech_rate, start, speech_end_s, end, duration_s`（v1.9：`speech_end_s` 必填）。
  - `start` = 上一句 `end`（首句 0）；`speech_end_s` = start + 发声时长；`end` = speech_end_s + silence_ms/1000（末句可被钳位到 `audio_seconds`）；`duration_s` = end − start（含句后停顿）。
  - 相邻句首尾相接（容差 1ms）；字幕只在发声窗口 `[start, speech_end_s]` 显示；段/镜头区间用 `[start, end)`。
- `full.mp3` = 各句音频 + 各句 `silence_ms` 顺序拼接，不额外追加尾部静音。
- `subtitles.json`：豆包未返回字级时间时，按标点切分并按字数比例在**发声窗口**内分配；cue `id` 唯一。

## 6. 响度
- 拼接后统一做两遍 `loudnorm`（目标 -16 LUFS、TP -1.5、LRA 11），再测量；不在 -16±1 LUFS 内返回退出码 7（F-05）。

## 7. 失败处理（退出码）
| 码 | 含义 | 做法 |
|---|---|---|
| 3 | `.env` 缺失或 Key 为空 | 提示用户在本技能目录 `.env`（`.agents/skills/remotion-infographic-video/.env`）填写 `DOUBAO_TTS_API_KEY`，等待“填好了”后重跑 `check_env.py` |
| 4 | 鉴权失败（Key 无效） | 停止，提示检查 `.env` 中的 Key；不换引擎 |
| 5 | 稿件格式或参数不合法 | 修稿后重跑 |
| 6 | 个别句重试耗尽 | 只对失败句 `--only` 重跑；此时不生成拼接半成品 |
| 7 | 响度不达标 | 检查稿件与音色后重跑 |

日志与产物经脱敏处理，任何输出都不显示 Key、Key 长度或前缀。

## 8. 用户自带配音
用户主动提供配音时跳过 TTS，但仍须产出通过同一 Schema 的 `timeline.json`（对齐方式由开发阶段决定，本技能包当前不内置对齐工具），并在交付备注中说明。
