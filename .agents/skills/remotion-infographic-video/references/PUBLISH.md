# PUBLISH：发布文案规范

> 下方 JSON 块是 `validate.py publish` 读取的平台规范表（唯一来源，Schema `assets/schemas/platforms.schema.json`）；本文件只有这一个 json 代码块。改规则只改 JSON 块，不改流程。

## 交付结构
- 每个目标平台各一套：`publish/<平台>/title.txt`、`publish/<平台>/description.txt`；`publish/<平台>/tags.txt`（一行一个，v1.5 按平台）。
- 目标平台：`job.json` 的 `platforms`（用户点名平台时才写）> 下表 `default_targets`。
- 封面各平台共用、按画幅出图：横屏 `publish/cover_1920x1080.png`，竖屏 `publish/cover_1080x1440.png`（由 `bash scripts/render.sh <slug>` 生成）。
- 标签按本平台规则：B 站逗号连接后总长 <200、YouTube ≤500（含空格的标签加引号计）为官方，不满足判错误；抖音 ≤5 个为非官方，只告警；小红书、视频号只查非空与无链接。
- 标题、简介、标签都不得含链接；`validate.py publish` 会在每个平台的简介末尾补“素材署名：”段，每行 `- [素材id] 作者 · 来源名称 · 许可`（简介长度包含该段）。
- 规则状态：`official` 不满足判错误（退出 7）；`unofficial` 只告警（写入 `publish/check.json`）。
- 没有全局标题上限：v1.3 起统一的“≤30 字”已由下表逐平台规则取代。
- 只产出文案与封面，不上传、不发布到任何平台。

## 平台规范表

格式（架构 v1.6 R-06）：顶层 `{version, default_targets, platforms}`，`platforms` 以平台 id 为键；每条规则含 `max`（可有 `min`、`strict_less_than`）、`count`（`grapheme` / `cjk1_ascii_half` / `utf8_bytes`，标签另有 `youtube_tags`）、`status`（`official` / `unofficial`）、`source`。没有 `tags` 的平台只校验非空与无链接。

```json
{
  "version": 1,
  "default_targets": [
    "douyin",
    "bilibili",
    "xiaohongshu",
    "channels",
    "youtube"
  ],
  "platforms": {
    "douyin": {
      "name": "抖音",
      "title": {
        "max": 30,
        "count": "grapheme",
        "status": "unofficial",
        "source": "第三方统计 reddit.com/r/China_irl（待核实）"
      },
      "description": {
        "max": 1000,
        "count": "grapheme",
        "status": "unofficial",
        "source": "抖音开放平台 create-video 接口 text 字段（API 上限，非端内标准）"
      },
      "tags": {
        "max_items": 5,
        "status": "unofficial",
        "source": "第三方统计（待核实）"
      }
    },
    "bilibili": {
      "name": "B 站",
      "title": {
        "max": 80,
        "count": "grapheme",
        "status": "official",
        "source": "B 站开放平台“视频稿件提交”接口",
        "strict_less_than": true
      },
      "description": {
        "max": 249,
        "count": "grapheme",
        "status": "official",
        "source": "B 站开放平台“视频稿件提交”接口（<250）"
      },
      "tags": {
        "joined_max": 200,
        "join": ",",
        "strict_less_than": true,
        "count": "grapheme",
        "status": "official",
        "source": "B 站开放平台“视频稿件提交”接口 tag 字段"
      }
    },
    "xiaohongshu": {
      "name": "小红书",
      "title": {
        "max": 20,
        "count": "cjk1_ascii_half",
        "status": "official",
        "source": "小红书小程序 xhs.postNote（计字方式待核实）"
      },
      "description": {
        "max": 1000,
        "count": "cjk1_ascii_half",
        "status": "official",
        "source": "小红书小程序 xhs.postNote"
      }
    },
    "channels": {
      "name": "视频号",
      "title": {
        "max": 16,
        "count": "grapheme",
        "status": "unofficial",
        "source": "第三方资料（待核实）",
        "min": 6
      },
      "description": {
        "max": 1000,
        "count": "grapheme",
        "status": "unofficial",
        "source": "微信开放社区文章（1 分钟内视频；待核实）"
      }
    },
    "youtube": {
      "name": "YouTube",
      "title": {
        "max": 100,
        "count": "grapheme",
        "status": "official",
        "source": "YouTube 帮助中心 / Data API",
        "forbid_chars": "<>"
      },
      "description": {
        "max": 5000,
        "count": "utf8_bytes",
        "status": "official",
        "source": "YouTube Data API snippet.description（5000 字节）",
        "forbid_chars": "<>"
      },
      "tags": {
        "joined_max": 500,
        "join": ",",
        "count": "youtube_tags",
        "status": "official",
        "source": "YouTube Data API snippet.tags"
      }
    }
  }
}
```

## 写作规范

### 标题
- 每个平台各写一份，只按本平台规则计字：小红书 ≤20（中文算 1、ASCII 字母数字算 0.5）；视频号 6–16；抖音 ≤30；B 站 <80；YouTube ≤100 且不含 `<` `>`。
- 结构：结论 / 反差 + 关键数字或对象，例如“半年融资 1500 亿，它贵吗？”。数字用阿拉伯数字写法，且必须是稿件中有出处的数字。
- 不做标题党：标题里的说法必须在视频里兑现；不放链接、话题网址、联系方式。
- 短上限平台（小红书、视频号）先保留核心对象和数字，再删修饰语。

### 简介
- 2–4 句概括视频的结论与看点，可附 1–3 个要点短句；数据只写稿件里有出处的。
- 末尾的“素材署名：”段由 `validate.py publish` 自动补全（每个平台恰好一段，计入长度），不要手写或改格式。
- B 站简介 <250（含署名段），写得最短；YouTube 按 UTF-8 字节 ≤5000，中文约 1600 字以内。
- 不放任何链接（含 `www.`、裸域名），来源只写名称，如“数据来源：国家统计局”。

### 标签（`publish/<平台>/tags.txt`，一行一个）
- 不设全局个数要求，按平台规则：B 站逗号连接后 <200；YouTube 总长 ≤500（含空格的标签按两侧加引号计）；抖音建议不超过 5 个（超出只告警）；小红书、视频号非空即可。
- 标签写主题词、对象名、领域词，不写 `#`、不写链接；同一平台内不重复。

### 封面
- `render.sh` 按画幅渲染 `Cover` Still：横屏 1920×1080，竖屏 1080×1440，PNG，各平台共用一份；风格与正片一致（深色背景、金色主数字、玻璃面板，见 [STYLE](STYLE.md)）。
- 封面文字：一个短标题（建议 ≤10 字）+ 至多一个关键数字；数字同样需有出处。

## 校验与交付
```
python3 scripts/validate.py publish <slug>       # 补署名段 → 逐平台校验 → 写 publish/check.json
python3 scripts/validate.py deliverable <slug>   # 汇总 deliverable.json（publish.<平台>.title/description/tags 与 warnings）
python3 scripts/validate.py leak <slug>          # 产物与日志中不得含 Key
python3 scripts/fetch_asset.py credits-diff --manifest <slug>/assets-manifest.json --slug-dir <slug>
```
- `publish/check.json` 通过 `publish-check.schema.json`；每个平台列出 title / description / tags 的计数、规则与严重度，`ok` 只受 error 影响。
- 退出码 7：按 `check.json` 中该平台的 errors 修改对应文件后重跑；warnings 不阻断，但要写进交付回报。
- 交付回报按平台列出标题、简介、标签及告警（来自 `deliverable.json.publish`）。
