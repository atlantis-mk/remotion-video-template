# SCRIPT：口播稿写法与 sources.md

> 产物：`<slug>/script.md`（人可读 + 机可解析，解析器 `script_parser.parse`）与 `<slug>/sources.md`（末尾附 JSON 块）。校验：`python3 scripts/validate.py sources <slug>/script.md <slug>/sources.md`（F-04、NF-03）。范例：`assets/example/script.md`、`assets/example/sources.md`。

## 1. 叙事结构（段数不固定）
钩子 → 若干论证段 → （可选）回应质疑 → 结尾互动。

| 段 | 作用 | 写法要点 |
|---|---|---|
| 钩子（S01） | 前 5–10 秒抓住人 | 一个反常识结论或最有冲击的数字，1–2 句 |
| 论证（S02…） | 用事实支撑结论 | 每段一个论点，2–4 句；每段最好有一个可视化的数字或对比 |
| 回应 | 预判观众的反驳 | “你可能会说……但是……”，可省 |
| 结尾 | 收束 + 互动 | 一句总结 + 关注 / 提问引导，1–2 句 |

- 段数和总时长都由内容决定；片长 = 配音长度，不在别处写死。
- 选题含糊时自行确定切入角度，不追问，交付时在备注说明。
- 用户已提供稿件时直接使用（按本格式整理），跳过写稿。

## 2. script.md 格式
```markdown
# <标题>
## S01 钩子
- [01] 半年融资一千五百亿，估值五千亿。 {context: 用略带惊讶但克制的播报语气说 | rate: 0 | pause: 350}
- [02] 我的结论是：一点都不贵。 {context: 笃定 | rate: -8 | pause: 500}
## S02 公司
- [03] ……
```
- `## Sxx <段名>`：段，`Sxx` 两位数字递增（S01、S02…），段名会作为 HUD 段名。
- `- [id] 文本 {…}`：句，`id` 为 2–3 位数字、全稿唯一且递增。
- `{}` 内字段用 `|` 分隔，可省：`context`（语气提示）、`rate`（语速，默认 0）、`pause`（句后静音 ms，默认 300）。参数含义与建议值见 [VOICE](VOICE.md)。
- 稿件中没有任何句时解析失败。

## 3. 句子写法
- 口语化、短句：一句 10–25 个字为宜，一句只讲一件事；一句对应一个镜头最好分镜。
- **数字写汉字读法**（“一千五百亿”“百分之三十”），供配音；上屏写法（“1500亿”“30%”）放 storyboard 的 `display_numbers`。
- 不写链接、不读网址；来源用“据 XX 报道”口播或只放角标。
- 末句留白靠 `pause`，不要指望片尾补静音。

## 4. 数据真实性（硬规则）
- 稿中每个含数字的句，数字都必须能在 `sources.md` 中找到对应条目，否则 `validate.py sources` 返回退出码 5。
- **查不到出处的数字不写进稿件**：删掉，或改成不含数字的定性表述。不编造、不估算后当事实写。
- 比对时数字会归一化（`normalize_number("一千五百亿") == normalize_number("1500亿")`），所以 `value_spoken` 与 `value_display` 写同一个数即可。

## 5. sources.md 格式
上半部分给人读（来源列表、说明），**末尾附一个 JSON 块**（数组），每条：

| 字段 | 必填 | 说明 |
|---|---|---|
| `claim_id` | 是 | 如 `C01`，storyboard `display_numbers.source_claim_id` 引用它 |
| `line_id` | 是 | 对应 script.md 的句 id |
| `value_display` | 是 | 上屏写法，如 `1500亿` |
| `value_spoken` | 是 | 稿中读法，如 `一千五百亿` |
| `url` | 是 | 来源链接（只留在内部，不出现在任何对外文案） |
| `publisher` | 否 | 发布机构，角标“据 XX”取它 |
| `accessed` | 是 | 访问日期 |

```json
[
  {"claim_id": "C01", "line_id": "01", "value_display": "1500亿", "value_spoken": "一千五百亿",
   "url": "https://example.org/report", "publisher": "某机构", "accessed": "2026-10-22"}
]
```

## 6. 自查清单
- [ ] 有钩子、有结尾互动；每段一个论点。
- [ ] 句 id 唯一递增，段号 Sxx 递增。
- [ ] 每个数字都在 sources.md JSON 块中，`validate.py sources` 退出码 0。
- [ ] 稿中无链接、无 Key、无向用户的提问。
