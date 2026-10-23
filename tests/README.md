# 测试与验收标准：remotion-infographic-video 技能包（TDD 第 3 步）

- 依据：PRD `requirements/remotion-video-template-PRD.md`、架构 **v1.11** `requirements/remotion-video-template-architecture.md`、架构答复 `requirements/remotion-video-template-arch-QA.md`（含 V11；相对工作区根，不随仓发布）
- 日期：2026-10-23（UTC+8）。修订：… → **v1.11（默认技能路径 `.agents/skills/`，A-28 仓库根 AGENTS.md）**。
- 用例只会 FAIL，不应出现 ERROR。被测实现内部抛出的异常（例如签名不符导致的 TypeError）会被记为 FAIL 并标“实现异常”；测试代码自身出错仍然报 ERROR，这样能区分“实现不合规”和“测试写错”。
- 被测技能包位置：`../.agents/skills/remotion-infographic-video/`（相对本 tests/ 目录；v1.11 修订 Q-01/A-21），可用环境变量 `SKILL_DIR` 覆盖。仓库根另有静态 `AGENTS.md`（A-28）。
- **函数模块与签名一律以架构 §7.5 为准**，用例按固定模块导入（如 `lib/verify.py`、`lib/credits.py`、`lib/tts_pipeline.py`），不再按函数名到处查找。

## 1. 技术选型（按架构 §1、§7.3）

| 部分 | 框架 | 说明 |
|---|---|---|
| Python 脚本（scripts/、scripts/lib/） | `unittest`（标准库） | 无需 pip 安装 |
| TS 纯函数 / Schema 交叉校验 | `vitest` + `ajv`（2020-12） | 放 `tests/ts/`，独立 package.json；实现后 project-template 也会带 vitest |
| 离线集成 | unittest 驱动 bash 脚本 + ffmpeg/ffprobe + Remotion | FakeTtsClient 代替豆包，不联网调 TTS |
| Agent 对话评测 | `agent-eval/evaluate.py`（规则判定器）+ unittest 包装 | 判定 Agent 回放导出的对话记录 |

## 2. 运行方式

```bash
cd tests   # 在仓库根执行
bash run_all.sh all          # 自动门禁：L1～L4 + TS + 追溯检查；L5 无 AGENT_RUNNER 时 SKIP（人工评测）
bash run_all.sh release      # 发布门禁：python3 tools/release_gate.py（先跑 all，再核对 agent-eval/archive/ 中 AE-01～AE-15 的 15 份 PASS 存档）
bash run_all.sh unit|contract|static|integration|agent|ts   # 单层
python3 tools/trace.py --check   # 重新生成 TRACEABILITY.md，并检查 25 条需求均有用例、用例 ID 不重复
python3 agent-eval/evaluate.py [AE-01 ...]   # 单独跑对话评测
SKILL_DIR=/path/to/.agents/skills/remotion-infographic-video bash run_all.sh all   # 指定被测技能包
```

前提：Python ≥3.9、Node 18+、ffmpeg/ffprobe、rg、git；集成层需要生成工程内 `npm ci` 能用（L3 不调用豆包，但允许访问 npm 源或缓存，Q-12）。

S-SK-02 需要 Agent Skills 校验器：先运行 `bash tools/install_skills_ref.sh`，它会把 PyPI `skills-ref==0.1.1` 装进 `tests/.venv`（需要 Python ≥3.11，Q-16）。CLI 名叫 `agentskills` 或 `skills-ref` 都接受；两者都没有时改调 `skills_ref.validate()`。当前环境已经装好。

对话评测回放：`AGENT_RUNNER="<命令>" python3 agent-eval/run_case.py [--out <dir>] [AE-xx]`。运行器接口（R-02）：`$AGENT_RUNNER <case.json> <out_dir>`，运行器写 `<ID>.jsonl`，`run_case.py` 写 `<ID>.meta.json`（R-01，固定字段 `{case_id, skill_dir, workdir, slug_dir|null, fake_key, started_at, finished_at, runner}`，`fake_key = TEST-<uuid4>`）。

## 3. 目录结构

```
tests/
├── README.md               本文件
├── TRACEABILITY.md         追溯矩阵（tools/trace.py 自动生成）
├── run_all.sh              一键运行与判定
├── py/
│   ├── support.py          公共支撑：定位技能包、covers(用例ID, 需求...) 装饰器、被测缺失时 FAIL 而非 ERROR
│   ├── unit/               L1 单元：envfile、timeline、script_parser、assets、renderers、validators、schema_check
│   ├── contract/           L2 接口契约：run_tts+Fake 依赖；全部 CLI 的退出码/JSON 摘要/产物契约
│   ├── static/             L4 静态规范：Agent Skills 规范、SKILL.md/references 体量、.env/.gitignore、rg 守卫
│   ├── integration/        L3 离线集成：示例视频 横屏、竖屏 各一遍完整流水线；自检失败报告；同工程横竖切换；改 tokens
│   ├── agent_eval/         L5 对话评测包装（每个 case 一个用例；无 AGENT_RUNNER 时 SKIP）
│   └── gate/               L0 门禁工具：release_gate.py 与 run_all.sh 的 SKIP 规则（不依赖技能包）
├── ts/                     vitest：computeLayout、presets、particles、useLines、registry、ajv 交叉校验
├── agent-eval/
│   ├── cases/AE-*.json     15 条对话评测用例 AE-01～AE-15（输入、环境设定、判定规则）
│   ├── run_case.py         回放 harness：准备隔离环境 → 调用 AGENT_RUNNER → 导出记录（Q-18）
│   ├── evaluate.py         判定器：读取 transcripts/<ID>.jsonl + <ID>.meta.json
│   ├── transcripts/        回放导出的对话记录
│   └── archive/            发布存档 <ID>/<run>/{<ID>.jsonl, <ID>.meta.json, <ID>.verdict.json}（格式见其 README）
├── fixtures/               PNG 尺寸样例、MCP timeline 正/反例、署名三处一致的 slug 样例、用户自带稿件
├── tools/trace.py          追溯矩阵生成与完整性检查
├── tools/release_gate.py   发布门禁（架构 v1.7 §7.3.1）
└── tools/install_skills_ref.sh  安装 skills-ref==0.1.1 到 tests/.venv（Q-16）
```

## 4. 用例数量分布（共 210；v1.10 为 207，v1.9 为 199，v1.7 为 185，v1.6 为 175，v1.5 为 172，v1.4 为 169，v2 为 152，v1 为 137）

| 层 | v1.11 数量 | v1.10 | 文件 |
|---|---|---|---|
| L0 门禁工具 | 7 | 6 | py/gate/*（G-REL-01～06、**G-PATH-01**） |
| L1 单元（Python） | 54 | 54 | py/unit/* |
| L1/L2 单元（TS，vitest） | 18 | 18 | ts/*.test.ts |
| L2 接口契约 | 51 | 51 | py/contract/* |
| L3 离线集成 | 32 | 32 | 横屏 + 竖屏 + 补充 |
| L4 静态规范 | 33 | 31 | py/static/test_skill_spec.py（**S-REPO-01/02** A-28） |
| L5 Agent 对话评测 | 15 | 15 | agent-eval/cases/AE-01～AE-15（门禁中 SKIP，原因 manual；发布门禁见 §5） |

F-01～F-17、NF-01～NF-08 共 25 条全部有用例，明细见 `TRACEABILITY.md`。

### 4.0 v1.3～v1.6 修订明细（以架构 v1.6 为准）

| 版本 | 修改 |
|---|---|
| v1.11（Q-01/A-21/A-28 交付布局） | 默认 `SKILL_DIR` 改为 `../.agents/skills/remotion-infographic-video`（`support.py` / `run_all.sh` / `release_gate.py` / `run_case.py` / `ts/helpers.ts`）；**新增 G-PATH-01**（默认相对路径公式与各入口同步）；**新增 S-REPO-01/02**（仓库根静态 `AGENTS.md` 存在且含 §2.0 强制段落：技能路径、使用步骤、环境、tests/skills-ref、两份 AGENTS 区分）。验收不放宽；源码目录迁移由后端执行。**C-DLV-01 / c_deliverable**：缺 `out/video.mp4` 仍退出 0（notes 提示、`duration_s` 可为 null）；成片由 F-12 `validate.py video` / `render` 验收，与架构 §4.10 交付摘要 + §7.4 F-16（字段齐全）/ F-12（成片存在）分工一致 |
| v1.10（§4.0 allow_abbrev=False） | 所有 CLI 禁用参数前缀缩写，参数不完整或拼错一律退出 2。C-LEAK-06 收紧：`--extra-secret`、`--extra`、`--sca`、`--skill` 等缩写必须退出 2 且 stderr 指出该参数。新增 C-ABR-01～08（`py/contract/test_cli_abbrev.py`），每个 CLI 各一条：tts_doubao.py（`--dry`、`--max`）、check_env.py（`--skill`、`--no-cmd`）、fetch_asset.py（add `--source-n`、prune `--story`）、scaffold_project.py（`--for`）、build_timeline.py（`--time`）、validate.py（storyboard `--time`、tokens `--js`、video `--vid`）、check_project.sh（`--asp`、`--determ`）、render.sh（`--covers`、`--video`）；其余必需参数给全，并断言 stderr 含该缩写，排除因缺参数退出 2 的假阳性 |
| v1.10.1（测试缺陷修复，用例数不变，验收未放宽；介于 v1.10 与路径迁移 v1.11 之间） | ① I-LS-02/I-PT-02：`remotion compositions --quiet` 只输出 ID（实测 `Main Cover`），改为默认表格输出并去 ANSI，断言不变。② S-LAY-01：`rg --glob '!layout/presets.ts'` 对绝对路径搜索根不生效（已复现），改为 Python 遍历，仅豁免 `src/layout/presets.ts` 这一个文件；其余文件按数值检测 1080/1440/1920 的各种写法（数字分隔符 `1_920`、`1080.0`、`1.92e3`、`0x780`/0o/0b、BigInt、字符串内、两字面量相乘如 `960 * 2`）；presets.ts 自身须用普通十进制写出三个尺寸、不得用数字分隔符。③ 流水线用例跨用例缓存的技能副本被首个用例的 addCleanup 删除（credits/leak 报缺 scripts），改为模块级 tearDownModule 清理。④ I-CK-02/05 的静音 mp3：24 kHz anullsrc 编码补齐实测 57.600s≠57.548s，改为 48 kHz + ffprobe 实测 + 按 24 ms 裁短，测试数据自身断言差 ≤12 ms；实现 ≤1 帧容差不变 |
| v1.9（V9-1～V9-3） | **V9-1 timeline**：句后停顿计入本句区间；`start` = 上一句 `end`，`speech_end_s`（必填）= start + 发声时长，`end` = speech_end_s + silence，`duration_s` = end − start > 0，字幕只在 `[start, speech_end_s]`。C-TTS-07 改为三条断言（`speech_end_s − start ≈ 字数×0.22`、`end − speech_end_s ≈ silence`、`end − start ≈ duration_s`，±1ms）；新增 U-TL-06（缺 speech_end_s → Schema 失败）、U-TL-07（speech_end_s > end 报错）、U-TL-08（非末句停顿 ≠ silence_ms 报错）、U-TL-09（末句钳位后 speech_end_s ≤ end）、U-TL-10（最后一个 cue 的 end = speech_end_s）；U-TL-01 不变，U-TL-02/03/05 的样例补 `speech_end_s=end、silence_ms=0`（断言不变）；旧口径“end − start = duration_s + silence”已从用例与 README 清除（仅变更记录保留）。**V9-2 licenses.json**：新增 U-AS-07（CC BY-NC 4.0 等被拒）、U-AS-08（CC-BY 4.0 可用且需署名）、U-AS-09（Unsplash 不被 nd 误伤，CC BY-ND 仍被拒）、U-AS-10（no_attribution 非 allowed 子集或 allowed∩denied≠∅ → 退出 5）、U-AS-11（licenses.json 过 licenses.schema.json，denied 必填并含 A-27 默认 11 项）。**V9-3 leak 参数**：新增 C-LEAK-03（--extra-secret-file 不存在 → 2；--extra-secret-file、--scan 可重复且都生效）、C-LEAK-04（--scan 文件不存在 → 2）、C-LEAK-05（密钥文件为空/空白/非 UTF-8 → 5）、C-LEAK-06（参数拼错、缺 slug、slug 不存在 → 2）。L5 SKIP 原因改为 `manual`（与架构 §7.3 一致） |
| v1.7（RV-1～RV-3） | **RV-1** 新增 `tools/release_gate.py` 与 **G-REL-01～06**（15 份 PASS 存档、缺失列 case_id、sha 不一致失效、verdict 字段严格、evaluate 复判、多份存档取有效 PASS、run_all 中 L1～L4 SKIP 计 FAIL / L5 SKIP 不计、release 调用 release_gate.py）；`agent-eval/archive/` 取代 `manual-results/`，删除 `check_manual_ae.py`；README 中“13 个”更正为 15。**RV-2** 新增 U-SP-04（`parse` 对 `[05] ……`、`[06] ？` 抛 `kind=empty_line` 且带 `line_id`）、C-TTS-11（含空句稿件 → `tts_doubao.py` 退出 5、`errors[0].kind=empty_line`、无产物；进程内替换为计数 FakeTts 后构造/调用 0 次）、C-TTS-12（`duration_for("")`、`("。")` = 0.220，`("你好")` = 0.440）；C-TTS-01 增加每句 `duration_s > 0`。**RV-3** C-LEAK-01 改写：临时技能包 `.env` 写入真实 Key 样本、同值写入日志第 3 行 → 退出 7，`hits == [{file, line: 3, which: "real"}]`，输出不含该值及其前后缀，`.env` 不算命中；假 Key 经 `--extra-secret-file` 传入，命中报 `which: "fake"`；新增 C-LEAK-02（`.env` 不存在或为空 → `real_key="absent"`、退出 0，且不读环境变量）。顺带：README 中已废弃的 `title_max_chars` 改为历史说明 |
| v1.6（R 系列） | **R-01** `run_case.py` 生成 meta.json（固定 8 个字段），假 Key 为 `TEST-<uuid4>`；`evaluate.py` 校验 meta 字段，AE 泄露检查要求 fake_key 在对话 JSONL 及 slug_dir、workdir 下的 `*.log/*.jsonl/*.txt` 中出现 0 次。**R-02 / UR-1=B** 运行器接口改为 `$AGENT_RUNNER <case.json> <out_dir>`；无运行器时 AE-01～15 判 SKIP（no runner），见 §5。**R-03** C-TTS-07：FakeTts 须产出 WAV（RIFF，24 kHz 单声道 16-bit，样本数 = round(时长×24000)），落盘 `parts/NN.wav`，发声时长与公式值差 ≤1ms（v1.9 起按 speech_end_s 判定，见 v1.9 行）；**新增 C-TTS-10**：FfmpegAudioTool 真实编码后 ffprobe(full.mp3) 与末句 end 差 ≤50ms。**R-05** T-DET-02：Particle 六字段均为有限数，0≤x<w、0≤y<h、r>0、0<opacity≤1，同参数深相等。**R-06** S-PUB-02/03 与 U-RD-04 改为“恰好一个 json 块 + json.loads”，PUBLISH.md 顶层 `{version:1, default_targets, platforms:{<id>:rule}}` 并过 Schema、不得出现 `title_max_chars`；**新增 S-LAY-04**（LAYOUT.md 块恰为 `{version:1, portrait_keywords:["竖屏"], landscape_keywords:["横屏"]}`）。**R-07** I-JOB-01：横屏回写 1920×1080、竖屏回写 1080×1440，job.ts 无 1080/1440/1920。**R-08** I-CK-03：主断言 stdout 末行 JSON `errors[0].kind == "max_attempts_exceeded"`、`attempts == 3`、退出码 7，stderr 含“上限”为辅助。**R-09** I-CK-05 只在 `{/* @test-inject:layers */}` 锚点处注入；**新增 S-LAY-05**（锚点恰好 1 处）。R-04、R-10 不变 |
| v1.3 | 竖屏改为 1080×1440（U-AS-*、U-RD-*、I-PT-*、T-LAY/T-PRE、AE-07）；画幅只由“横屏 / 竖屏”两个词决定，以最后出现者为准，平台名（抖音、B 站等）一律横屏（U-RD-04～07、AE-14）；平台规范表 official 不满足为错误、unofficial 为警告（U-VD-03～10、S-PUB-02/03）；credits 为 `{id, author, source_name, license}`、不含 URL，新增 `find_urls`（U-AS-06、C-DLV-01）；`--attribution` 拆为 `--author` / `--source-name`（C-AS-07） |
| v1.4 | 标题、简介按平台：`publish/<p>/title.txt`、`description.txt`，简介长度含署名段（U-VD-03/05～09、C-PUB-01～04）；credits-diff 逐平台（U-AS-03～05）；`publish/check.json` 按 `publish-check.schema.json`（C-PUB-*、S-SCH-01）；deliverable 增加 `publish` 按平台（C-DLV-01、AE-06）；**删除 I-CK-04**，F-08 仍由 I-CK-05、S-LAY-03、S-LAY-02 等覆盖 |
| v1.5 | 标签按平台：每个平台一份 `publish/<p>/tags.txt`，封面仍共用；**取消全局“5–10 个”**（U-VD-03 删掉 5/10/4/11 断言，改为 1 个标签即合规、缺某平台 tags.txt 失败）；**新增 U-VD-11**（B 站逗号连接 199 过 / 200 败；YouTube 500 过 / 501 败，含空格标签 +2；抖音 6 个只告警且 ok=true；小红书、视频号只查非空；任一平台含链接失败）；**新增 U-VD-12**（`count_tags`）；**新增 C-PUB-05**（CLI 退出码与 check.json 中 douyin 告警）；C-PUB-* 断言 check.json 每平台 `tags{items, rule}`、无 `shared.tags`；C-DLV-01 去掉顶层 `tags`，断言 `publish.<p>.tags` 与 `tags_path`；S-PUB-03 断言标签规则取值并禁止 PUBLISH.md 出现“5–10 个”；AE-06/AE-15 产物改为按平台 tags.txt；fixtures/credits_slug 同步 |

### 4.1 v2 修订明细（对齐架构 v1.2 / QA；其中被 v1.3～v1.5 覆盖的条目以 4.0 为准）

| 依据 | 修改的用例 |
|---|---|
| Q-02 §7.5 签名 | U-TL-01（`build_timeline_lines(lines, durations_s)`，end 含 silence_ms）、U-TL-02（返回错误列表，1ms 容差，末句超出音频也算错）、U-TL-04（`floor(s*fps+0.5)`，补银行家舍入反例，默认 fps=30）、U-SP-03（`lib/sources.normalize_number` 返回 Decimal / None）、U-ENV-06 与 C-TTS-*（Redactor 改在 `lib/log.py`）、U-RD-01～04（`lib/render_ts`、`lib/render_md`、`render_agents_md(ctx)`、`lib/job.resolve_aspect(topic, keywords)`）、U-VD-01～03（`lib/verify`，当时签名 `validate_publish(publish_dir, job, …)`，v1.4 起为 `validate_publish(publish_dir, job, rules, targets)`，补 0.1s 边界与封面尺寸）、C-TTS-01～06（`lib/tts_pipeline.run_tts`，`speaker`、`only: set`、`max_attempts=3`） |
| Q-03 | U-SC-03（manifest 顶层为 `{version:1, assets:[…]}`，顶层数组判失败）、C-AS-01～03（CLI 只接受对象）、**新增 C-AS-06**（不存在 `render-md`）、fixtures、集成用例中默认 manifest |
| Q-04 | U-AS-03/04 改用新签名 `credits_diff(manifest, shot_badges, description_text, deliverable)`；**新增 U-AS-05**（只认“素材署名：”段内的 `[id]`）；C-AS-04 拆成三处各缺一次；**新增 C-AS-05**（`prune`）；C-PUB-01（署名段格式与幂等）；I-LS/PT-10 检查 `shot-badges.json`；fixture 新增 `project/src/data/shot-badges.json` |
| Q-06 | **新增 I-CK-03**（3 次失败后第 4 次调用仍退出 7；`attempts.json` 记录 n=1..3）；AE-09 维持总调用 ≤3 |
| Q-07 | S-SK-06（估算公式改为 `CJK×2 + 其他÷3`）、S-SK-07（色值正则 `#[0-9A-Fa-f]{3,8}`，并禁止 `rgb(`/`hsl(`） |
| Q-09 / U-2 | **新增 U-VD-04**（`count_title_chars` 按字素簇计数）；S-PUB-02（当时检查标题上限 ≤30；v1.3 起改为平台规范表，v1.6 R-06 起该字段已废弃，S-PUB-02 只断言 PUBLISH.md 中**不得出现** `title_max_chars`） |
| Q-10 | I-CK-01（`failed_step=="tsc"`、`attempt`、`log_path` 为绝对路径且存在、通过 Schema 校验）、I-LS/PT-06（report 各字段与步骤名）；**新增 U-SC-04**（`check-report.schema.json` 正反例）；**新增 S-SCH-01** |
| Q-13 | **新增 S-LAY-03**（`data-layer` 只能是四个值；SourceBadge 带 `data-role`）、**新增 I-CK-04**（末段出现“鸣谢 / Credits”文本 → 失败）、**新增 I-CK-05**（多出一个 `data-layer` → 失败）；S-LAY-02 改为 `rg -i credits`。**v1.4 已删除 I-CK-04；S-LAY-02 已回到 PRD F-09 的区分大小写 `rg Credits`** |
| Q-14 | I-LS/PT-09 增加 studio 冒烟检查（后台启动，90s 内 GET / 返回 200） |
| Q-16 | S-SK-02（接受 `skills-ref` / `agentskills` / `skills_ref.validate()`）；新增 `tools/install_skills_ref.sh` |
| Q-17 | C-TTS-03（失败句恰好尝试 3 次）；**新增 C-TTS-08**（`max_attempts=4` 被拒）、**新增 C-TTS-09**（CLI `--max-attempts 4` 与旧参数 `--retries` 都退出 2） |
| Q-18 | `evaluate.py` 改为读 JSONL，并校验每行必需字段；新增 `run_case.py` 回放 harness |
| Q-19 | **新增 C-TTS-07**（FakeTts：发声时长 = 220ms × 有效字数；当时容差 30ms。现行口径见 4.0 v1.9：`speech_end_s − start ≈ 字数×0.22`、`end − speech_end_s ≈ silence`、`end − start ≈ duration_s`，均 ±1ms） |
| Q-20 / U-1 | U-RD-04 改为从 LAYOUT.md 的 JSON 块读取 `portrait_keywords`，必须包含 PRD 明列的 4 个词，B 站判横屏；**新增 U-RD-05**（U-1 建议 C 的扩展词） |
| Q-21 | I-JOB-01（缺 aspect 时，scaffold 回写 `job.json.aspect=landscape`） |
| Q-22 | T-DET-01～03（`layers/particles.ts`，`particles(w,h,seed,count)`，粒子数等于 count，禁用 Math.random）、T-FR-01/02（`timing/lines.ts` 新签名）；**新增 T-FR-03**（lines.ts 不导入 remotion） |
| Q-23 | I-NF6-01 改为像素级判定：bg 改为 #3A0000、gold 改为 #00E5FF 后，S03 中点帧 SHA256 不同且平均 R 升高 ≥8，同时保留原有判据 |
| Q-24 | AE-03 问号数改为恰好 1；AE-01/03 新增“问句必须是在问选题”，AE-03 新增“Key 提示必须是陈述句” |
| 沿用（Q-01/05/08/11/12/15） | 用例不变，只更新说明文字 |

### 4.2 U-1～U-3：用户已拍板（v1.3～v1.5），用例已按拍板结果改写

| 编号 | 拍板口径 | 受影响用例 |
|---|---|---|
| U-1 画幅关键词 | 只认“横屏 / 竖屏”，最后出现者为准；平台名判横屏；竖屏 1080×1440 | U-RD-04～07、AE-07、AE-14、T-LAY/T-PRE、I-PT-* |
| U-2 平台规则 | 平台规范表逐平台校验标题、简介、标签；official 失败为错误，unofficial 只告警；标签规则见 4.0 v1.5 | U-VD-03～12、C-PUB-01～05、S-PUB-02/03 |
| U-3 署名不带 URL | credits `{id, author, source_name, license}`，简介与交付物都不含 URL | U-AS-03～06、U-VD-07、C-AS-04/07、C-PUB-*、C-DLV-01、AE-06 |

## 5. 验收判定规则

1. **自动门禁** `bash run_all.sh all` 退出码为 0：L1～L4 与 TS 共 188 个用例**全部通过**，追溯检查无缺口。L1～L4、TS 中出现任何 FAIL、ERROR 或 SKIP，退出码都不为 0。**唯一例外**：L5（AE-01～15）按用户拍板 UR-1=B 改为人工评测，未设置 `AGENT_RUNNER` 时判 SKIP（原因 no runner），不计入失败；设置了运行器时 L5 照常判定，FAIL 同样阻断。
1a. **发布门禁** `bash run_all.sh release`（= `python3 tools/release_gate.py`，架构 v1.7 §7.3.1 / QA RV-1）退出码为 0：先跑自动门禁 `all`（L1～L4、TS 的 SKIP 按 FAIL 计）；再核对 `agent-eval/archive/` 中 AE-01～AE-15 **每个用例至少 1 份有效 PASS 存档，共 15 份**。每份存档 = `<ID>.jsonl` + `<ID>.meta.json` + `<ID>.verdict.json`，verdict 字段恰为 `{case_id, result, skill_md_sha256, judged_by: auto|human, judged_at}`；`skill_md_sha256` 必须等于当前 SKILL.md 的 sha256（SKILL.md 一改旧存档全部失效）；并用 `evaluate.py` 对存档复判，复判不通过也算失效。缺失或失效时退出非 0 并列出 case_id。格式见 `agent-eval/archive/README.md`。原 `manual-results/` + `check_manual_ae.py` 方案已并入此处，严格程度不变（额外要求 judged_at 带时区）。
2. 不允许修改、删除、跳过用例或放宽阈值来变绿。如果觉得用例与需求不符，提给调度和测试门禁，评审通过后由测试门禁修改。
3. L5 对话评测必须用**实现后的真实技能包**跑 Agent，对话记录如实导出为 `<ID>.jsonl`（每个 case 一份），人工评测结果存档见 1a。记录必须如实导出，不能手写或伪造。
4. 集成层必须横屏、竖屏都通过，单个画幅通过不算。
5. 硬阈值（来自 PRD，或架构 v1.2 / QA 更严格的读法，均不放宽）：片长帧数 = floor(ffprobe×30+0.5) ±1；音视频时长差 ≤0.1s（含 0.1）；尾部静音 ≤50ms；LUFS −16±1；每句总尝试 ≤3；check_project 总调用 ≤3；SKILL.md <500 行、<5000 tokens；references 单文件 ≤300 行；标题、简介、标签按平台规范表逐平台校验（official 违规为错误、unofficial 只告警；标签：B 站逗号连接 <200、YouTube ≤500（youtube_tags）、抖音 ≤5 个只告警、小红书 / 视频号非空且无链接；无全局个数规则）；示例片长 50–70s；对话首问问号恰好 1 个。
6. U-1～U-3 已拍板（见 4.2），相关用例与其他用例同等参与判定。

## 6. 运行结果

### v1.11（2026-10-23 UTC+8）

**已上线结论（流程第 8 步同步）**：自动门禁 `bash run_all.sh all` — **210 用例自动层全绿**；L5（AE-01～15）无 `AGENT_RUNNER` 时 **15 SKIP**（人工评测另做）。公开仓 commit `2871d6a71e4e7c36fae4c96a5646c6fc9c1ac859`。对外摘要见仓库 `docs/testing.md`。

以下为同日调试过程记录（保留）：

- 入口校验：`sha256sum -c /tmp/tests_v110/SHA256SUMS` 全部 OK，无新增/缺失文件。
- 旧用例（v1.10）跑当前实现 integration：22/32 pass（前端日志）→ 本轮复跑 24/32；8 个失败全部归因为测试缺陷（见 4.0 v1.11 ①③④）。
- 修复后当前实现：ts 18/18；integration 32/32（1724 s）；static 30/31，S-LAY-01 FAIL：presets.ts 用 `1_920` 等数字分隔符书写，属前端须恢复项。
- 变形检测自测：presets.ts 恢复为普通十进制后 S-LAY-01 PASS；在 Cover.tsx 追加 `0x780` 后 FAIL。

### v1.10（2026-10-23 UTC+8）

契约层：空技能包 51 个全部 FAIL，0 ERROR；当前实现 51/51 通过。变异检查：把临时副本里的 `allow_abbrev=False` 去掉后，C-ABR-01～08 与 C-LEAK-06 共 9 条全部 FAIL，说明用例确实能抓住缩写。`trace.py --check`：207 个用例，25 条需求全覆盖，无重复 ID。


### v1.9（2026-10-23 UTC+8）

**A. 空技能包**：`SKILL_DIR=/tmp/empty/.agents/skills/remotion-infographic-video bash run_all.sh all` → 单元 54、契约 43、静态 31、集成 32 全部 FAIL，0 ERROR；L5 15 个 SKIP（manual）；TS 18 个全部 FAIL；L0 门禁工具 6 个通过（只测测试侧工具）；`trace.py --check`：199 个用例，25 条需求全覆盖，无重复 ID；退出码 1。

**B. 当前实现（单元 + 契约）**：单元 54/54、契约 43/43 通过。

**v1.9 遗留（已在 v1.10 解决）**：前缀缩写问题由架构 v1.10 §4.0 裁定为禁止（allow_abbrev=False），见 4.0。

### v1.7（2026-10-23 UTC+8）

**A. 空技能包**：`SKILL_DIR=/tmp/empty/.agents/skills/remotion-infographic-video bash run_all.sh all` → 单元 44、契约 39、静态 31、集成 32 全部 FAIL，0 ERROR；L5 15 个 SKIP；TS 18 个全部 FAIL；L0 门禁工具 6 个通过（只测测试侧工具，不依赖技能包）；`trace.py --check`：185 个用例，25 条需求全覆盖，无重复 ID；退出码 1。`release_gate.py --archive-only`：0/15，列出 AE-01～AE-15。

**B. 当前实现（单元 + 契约）**：单元 44/44，契约 38/39；失败 C-TTS-07（FakeTts 仍产出 mp3，R-03 要求 WAV）。


### v1.6（2026-10-23 00:03 UTC+8）

**A. 空技能包**：`SKILL_DIR=/tmp/empty/.agents/skills/remotion-infographic-video bash run_all.sh all` → 单元 43、契约 36、静态 31、集成 32 全部 FAIL，0 ERROR；L5 15 个 SKIP（no runner）；TS 18 个全部 FAIL；`trace.py --check`：175 个用例，25 条需求全覆盖，无重复 ID；退出码 1。`release` 另报 0/15 人工存档。

**B. 当前实现（单元 + 契约两层）**：v1.5 用例 单元 43/43、契约 35/35 通过；v1.6 用例 单元 42/43、契约 35/36 通过。失败：U-RD-04（LAYOUT.md 的 json 块缺 `version: 1`）、C-TTS-07（FakeTts 仍产出 mp3，不是 WAV）。


### v1.5（2026-10-22 UTC+8）

**A. 空技能包（红灯基线）**：Python 154 个全部 FAIL（单元 43、契约 35、静态 29、集成 32、Agent 15），0 ERROR；TS 18 个全部 FAIL；`trace.py --check`：172 个用例，25 条需求全覆盖，无重复 ID。

**B. 当前目录**：Python 154 个中 FAIL 79、通过 75、ERROR 0；TS 18 个 FAIL。新增的标签用例（U-VD-11/12、C-PUB-05）全部 FAIL，因为实现还没有按平台的 tags 和 `count_tags`。


### v2（2026-10-22 23:58 UTC+8）

**A. 对空技能包跑（红灯基线）**：`SKILL_DIR=/tmp/empty/.agents/skills/remotion-infographic-video bash run_all.sh all`
- Python 136 个：136 FAIL，0 ERROR，0 通过；TS 16 个：16 FAIL
- `trace.py --check`：152 个用例，25 条需求全部覆盖，没有重复 ID

**B. 对当前目录跑**：`bash run_all.sh all`
- 23:39 起开发已经在 `remotion-infographic-video/` 写入部分代码，所以这次**不是全红**。
- Python 136 个：通过 31、FAIL 105、ERROR 0；TS 16 个：16 FAIL
- 通过的主要是 envfile、timeline、render_ts、部分 Schema、run_tts 重试与缓存、.env 规范等
- 已经暴露出实现与 v1.2 不符的地方（都记为 FAIL），例如：`build_timeline_lines` 还是旧签名；`validate_publish` 还是旧签名；manifest Schema 顶层仍是数组；`fetch_asset.py` 仍有 `render-md`；`normalize_number` 返回元组而不是 Decimal；`verify_video` 在 0.100s 边界上误判；FakeTts 时长偏差 72ms

### v1（2026-10-22 23:35 UTC+8，当时技能包不存在）

- 137 个用例，全部 FAIL，0 ERROR

## 7. 歧义处理状态

### 7.1 Q-01～Q-24：架构已答复（见 arch-QA.md），用例已全部按答复对齐（明细见 4.1）

| 状态 | 编号 |
|---|---|
| 按答复修改了用例 | Q-02、Q-03、Q-04、Q-06、Q-07、Q-09、Q-10、Q-13、Q-14、Q-16、Q-17、Q-18、Q-19、Q-20、Q-21、Q-22、Q-23、Q-24 |
| 答复是“沿用当前写法”，已逐条核对 | Q-01、Q-05、Q-08、Q-11、Q-12、Q-15 |
| 用户已拍板 | U-1、U-2、U-3（见 4.2） |

### 7.2 遗留问题 R-01～R-10（v2 提出；v1.6 架构已答复，处理结果见 4.0。下表为原始描述，留档）

| 编号 | 问题 | 当前用例写法 |
|---|---|---|
| R-01 | Q-18 的 JSONL 只有对话行，判定还需要技能包路径、slug 目录和本次使用的假 Key（用于泄露检查、读取产物） | 新增 `transcripts/<ID>.meta.json`，由 `run_case.py` 生成 |
| R-02 | 还没有可以接入的宿主 Agent 运行器（`AGENT_RUNNER`）。缺了它，15 个 L5 用例永远是红灯（v1.7：UR-1=B，无运行器时 L5 判 SKIP，发布前须有 15 份 PASS 存档） | 已写好 harness 和调用约定，需要指定由谁来提供运行器 |
| R-03 | FakeTts 时长允许多大误差没有定义（MP3 编码帧约 26ms） | C-TTS-07 用 ±30ms。当前实现偏差 72ms，需要确认是实现问题还是容差需要明确 |
| R-04 | `resolveLine(frame, …, sectionStartFrame)` 里的 `frame` 是段内本地帧还是全局帧没有写明 | 按段内本地帧写 |
| R-05 | `particles()` 返回元素的结构没有定义 | 假定每个元素有 `x`、`y` |
| R-06 | PUBLISH.md、LAYOUT.md 机读 JSON 块的格式与键名没有定义 | v1.6 已答复：各恰好一个 json 块并 json.loads + Schema 校验（见 4.0）；旧的标题字段已废弃 |
| R-07 | Q-21 只说要回写 `aspect`，没说是否同时回写 width/height | 只断言 aspect（`job.ts` 受“禁止写死 1080/1920”规则约束） |
| R-08 | check_project 第 4 次调用提示的文字没有约定 | 断言输出里含“上限” |
| R-09 | I-CK-05 往 `Main.tsx` 注入额外 `data-layer` 时，依赖 `return (<…>` 和 `<AbsoluteFill>` 这两种写法（I-CK-04 已在 v1.4 删除） | 实现如果改用别的写法，需要同步调整注入方式 |
| R-10 | 开发在测试定稿前已经开始，当前目录不是全红 | 红灯基线改用空 SKILL_DIR 证明；建议调度确认开发以 v2 用例为准 |
