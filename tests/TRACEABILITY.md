# 追溯矩阵（自动生成：`python3 tools/trace.py`，勿手改）

用例总数：210；需求条目：25；未覆盖：无；重复 ID：无

## 按层统计

| 层 | 用例数 |
|---|---|
| L0 门禁工具 | 7 |
| L1 单元(Py) | 54 |
| L1/L2 单元(TS) | 18 |
| L2 接口契约 | 51 |
| L3 离线集成 | 32 |
| L4 静态规范 | 33 |
| L5 Agent 对话评测 | 15 |

## 需求 → 用例

| 需求 | 用例数 | 覆盖层 | 用例 ID |
|---|---|---|---|
| F-01 | 9 | L0 门禁工具, L4 静态规范 | G-PATH-01, S-CPY-01, S-SK-03, S-SK-01, S-SK-05, S-REPO-01, S-REPO-02, S-SK-04, S-SK-02 |
| F-02 | 2 | L4 静态规范 | S-SK-07, S-SK-06 |
| F-03 | 8 | L4 静态规范, L5 Agent 对话评测 | AE-01, AE-02, AE-03, AE-11, AE-12, AE-14, AE-15, S-SK-09 |
| F-04 | 8 | L1 单元(Py), L2 接口契约, L5 Agent 对话评测 | AE-12, AE-13, C-SRC-01, C-TTS-11, U-SP-03, U-SP-02, U-SP-04, U-SP-01 |
| F-05 | 29 | L1 单元(Py), L1/L2 单元(TS), L2 接口契约, L3 离线集成 | C-ABR-01, C-TTS-09, C-TL-01, C-TTS-11, C-TTS-12, C-TTS-07, C-TTS-10, C-TTS-08, C-TTS-06, C-TTS-04, C-TTS-01, C-TTS-03, C-TTS-02, I-LS-11, I-LS-01, I-PT-11, I-PT-01, U-ENV-06, U-SC-01, U-SP-04, U-SP-01, U-TL-01, U-TL-08, U-TL-07, U-TL-06, U-TL-05, U-TL-10, U-TL-02, T-AJV-02 |
| F-06 | 18 | L1 单元(Py), L1/L2 单元(TS), L2 接口契约, L3 离线集成, L4 静态规范 | C-ABR-05, C-TTS-07, C-TTS-10, C-TTS-06, I-LS-02, I-LS-08, I-LS-03, I-PT-02, I-PT-08, I-PT-03, S-DUR-01, U-RD-03, U-TL-09, U-TL-03, U-TL-04, T-FR-01, T-FR-02, T-FR-03 |
| F-07 | 7 | L1 单元(Py), L1/L2 单元(TS), L2 接口契约, L4 静态规范 | C-ABR-05, C-SB-01, S-EX-01, U-SC-02, T-REG-01, T-AJV-01, T-AJV-03 |
| F-08 | 30 | L1 单元(Py), L2 接口契约, L3 离线集成, L4 静态规范, L5 Agent 对话评测 | AE-13, C-ABR-03, C-AS-04, C-AS-07, C-AS-03, C-AS-01, C-AS-02, C-AS-06, C-AS-05, C-PUB-01, I-CK-05, I-LS-10, I-PT-10, S-LAY-03, S-LAY-05, S-SCH-01, U-AS-01, U-AS-03, U-AS-04, U-AS-05, U-AS-06, U-AS-02, U-AS-08, U-AS-07, U-AS-10, U-AS-09, U-AS-11, U-SC-03, U-VD-09, U-VD-07 |
| F-09 | 18 | L1 单元(Py), L1/L2 单元(TS), L2 接口契约, L3 离线集成, L4 静态规范 | C-ABR-04, C-SCF-01, C-TOK-01, I-NF6-01, I-CK-05, I-LS-13, I-LS-12, I-PT-13, I-PT-12, S-CMP-01, S-LAY-03, S-EX-01, S-FNT-01, S-LAY-05, S-VER-01, S-LAY-02, U-RD-01, T-REG-01 |
| F-10 | 50 | L1 单元(Py), L1/L2 单元(TS), L2 接口契约, L3 离线集成, L4 静态规范, L5 Agent 对话评测 | AE-07, AE-08, AE-14, AE-15, C-ABR-04, I-JOB-01, I-CK-02, I-LS-09, I-LS-13, I-LS-05, I-LS-10, I-LS-07, I-LS-02, I-LS-08, I-LS-06, I-LS-06, I-LS-11, I-LS-01, I-LS-03, I-LS-12, I-LS-04, I-PT-09, I-PT-13, I-PT-05, I-PT-10, I-PT-07, I-PT-02, I-PT-08, I-PT-06, I-PT-06, I-PT-11, I-PT-01, I-PT-03, I-PT-12, I-PT-04, S-LAY-04, S-LAY-01, U-RD-04, U-RD-07, U-RD-06, U-RD-05, T-DET-02, T-LAY-01, T-LAY-02, T-LAY-03, T-LAY-04, T-LAY-05, T-LAY-06, T-LAY-07, T-PRE-01 |
| F-11 | 9 | L1 单元(Py), L2 接口契约, L3 离线集成, L4 静态规范, L5 Agent 对话评测 | AE-09, C-ABR-07, C-CLI-01, I-CK-03, I-CK-01, I-LS-06, I-PT-06, S-SCH-01, U-SC-04 |
| F-12 | 7 | L1 单元(Py), L2 接口契约, L3 离线集成, L5 Agent 对话评测 | AE-06, C-ABR-08, C-ABR-06, I-LS-04, I-PT-04, U-VD-02, U-VD-01 |
| F-13 | 24 | L1 单元(Py), L1/L2 单元(TS), L2 接口契约, L3 离线集成, L4 静态规范, L5 Agent 对话评测 | AE-06, AE-10, AE-15, C-PUB-01, C-PUB-04, C-PUB-02, C-PUB-05, C-PUB-03, I-LS-05, I-PT-05, S-PUB-01, S-PUB-02, S-PUB-03, U-VD-12, U-VD-04, U-VD-10, U-VD-03, U-VD-09, U-VD-05, U-VD-08, U-VD-07, U-VD-11, U-VD-06, T-PRE-01 |
| F-14 | 6 | L1 单元(Py), L2 接口契约, L3 离线集成, L4 静态规范 | C-SCF-01, I-LS-09, I-PT-09, S-REPO-01, S-REPO-02, U-RD-02 |
| F-15 | 4 | L1 单元(Py), L1/L2 单元(TS), L2 接口契约, L4 静态规范 | C-TL-01, S-SK-08, U-SC-01, T-AJV-02 |
| F-16 | 10 | L0 门禁工具, L2 接口契约, L4 静态规范, L5 Agent 对话评测 | AE-06, AE-11, C-DLV-01, G-REL-01, G-REL-02, G-REL-05, G-REL-06, G-REL-03, G-REL-04, S-SK-09 |
| F-17 | 25 | L1 单元(Py), L2 接口契约, L3 离线集成, L4 静态规范, L5 Agent 对话评测 | AE-03, AE-04, AE-05, C-ABR-02, C-ENV-02, C-ENV-01, C-ENV-03, C-ENV-04, C-ENV-06, C-ENV-05, C-LEAK-01, C-LEAK-02, C-TTS-05, I-LS-11, I-PT-11, S-CPY-01, S-ENV-01, S-ENV-02, S-ENV-03, S-SK-09, U-ENV-03, U-ENV-04, U-ENV-02, U-ENV-05, U-ENV-01 |
| NF-01 | 4 | L2 接口契约, L4 静态规范, L5 Agent 对话评测 | AE-02, AE-06, C-CLI-01, S-AUTO-01 |
| NF-02 | 24 | L1 单元(Py), L2 接口契约, L3 离线集成, L4 静态规范, L5 Agent 对话评测 | AE-05, AE-10, C-ABR-06, C-ENV-03, C-LEAK-06, C-LEAK-05, C-LEAK-04, C-LEAK-03, C-ENV-06, C-LEAK-01, C-LEAK-02, C-PUB-05, C-PUB-03, C-TTS-05, I-LS-11, I-PT-11, S-ENV-01, S-ENV-02, S-PUB-01, U-AS-06, U-ENV-05, U-ENV-06, U-VD-07, U-VD-11 |
| NF-03 | 3 | L1 单元(Py), L2 接口契约, L5 Agent 对话评测 | AE-13, C-SRC-01, U-SP-03 |
| NF-04 | 10 | L1 单元(Py), L2 接口契约, L3 离线集成, L5 Agent 对话评测 | AE-13, C-AS-04, C-AS-05, I-LS-10, I-PT-10, U-AS-03, U-AS-04, U-AS-05, U-AS-06, U-AS-08 |
| NF-05 | 5 | L1/L2 单元(TS), L3 离线集成, L4 静态规范 | I-LS-07, I-PT-07, S-DET-01, T-DET-01, T-DET-03 |
| NF-06 | 4 | L1 单元(Py), L2 接口契约, L3 离线集成, L4 静态规范 | C-TOK-01, I-NF6-01, S-NF6-01, U-RD-01 |
| NF-07 | 5 | L2 接口契约, L3 离线集成, L5 Agent 对话评测 | AE-09, C-TTS-04, C-TTS-03, C-TTS-02, I-CK-03 |
| NF-08 | 2 | L4 静态规范 | S-SK-10, S-SK-04 |

## 用例清单

| 用例 ID | 层 | 覆盖需求 | 说明 |
|---|---|---|---|
| AE-01 | L5 Agent 对话评测 | F-03 | F-03 只说“开始制作”→只问选题 |
| AE-02 | L5 Agent 对话评测 | F-03 NF-01 | F-03 NF-01 “开始制作：<选题>”→不提问直接进入步骤 1 |
| AE-03 | L5 Agent 对话评测 | F-17 F-03 | F-17 F-03 .env 缺失 + “开始制作”→提示填写路径与变量名，不调用 TTS、不建工程（Q-24：问号恰好 1 个且在选题问句里；Key 提示为陈述句） |
| AE-04 | L5 Agent 对话评测 | F-17 | F-17 用户回复“填好了”→重新读取 .env 并继续，不再重复提示 |
| AE-05 | L5 Agent 对话评测 | F-17 NF-02 | F-17 NF-02 Key 无效（鉴权错误）→停止并提示检查 .env，不换引擎，不泄露 Key |
| AE-06 | L5 Agent 对话评测 | F-16 NF-01 F-12 F-13 | F-16 NF-01 F-12 F-13 端到端：选题之后到交付之间无提问；一次性交付全部字段，按平台（默认 5 个）列出标题、简介与标签（v1.5 标签按平台）（v1.4）；交付消息不含任何链接 |
| AE-07 | L5 Agent 对话评测 | F-10 | F-10 选题注明“竖屏”→ 3:4 1080×1440（v1.3 U-1） |
| AE-08 | L5 Agent 对话评测 | F-10 | F-10 选题未提画幅→默认横屏 1920×1080 |
| AE-09 | L5 Agent 对话评测 | F-11 NF-07 | F-11 NF-07 自检持续失败→最多 3 轮修复后停止，报告失败步骤与日志路径 |
| AE-10 | L5 Agent 对话评测 | F-13 NF-02 | F-13 NF-02 全流程不调用任何发布/上传 |
| AE-11 | L5 Agent 对话评测 | F-03 F-16 | F-03 F-16 选题含糊（一个词）→不追问，交付时说明切入角度 |
| AE-12 | L5 Agent 对话评测 | F-03 F-04 | F-03 F-04 用户主动给稿→跳过写稿，仍不索要其他素材 |
| AE-13 | L5 Agent 对话评测 | F-04 NF-03 F-08 NF-04 | F-04 NF-03 F-08 NF-04 产物规则：稿件数字均有出处、三处署名差集为空 |
| AE-14 | L5 Agent 对话评测 | F-10 F-03 | F-10 F-03 只提平台名（“做一条抖音”）→ 仍按横屏 1920×1080，且不追问画幅（v1.3 U-1） |
| AE-15 | L5 Agent 对话评测 | F-13 F-03 F-10 | F-13 F-03 F-10 选题点名平台（“只发 B 站”）→ 不提问；job.platforms=[bilibili]，只出 publish/bilibili/ 一套文案；画幅仍为横屏（v1.4 A-25） |
| C-ABR-01 | L2 接口契约 | F-05 | F-05 tts_doubao.py：--dry（--dry-run 的前缀）、--max（--max-attempts）→ 2 |
| C-ABR-02 | L2 接口契约 | F-17 | F-17 check_env.py：--skill（--skill-dir 的前缀）、--no-cmd（--no-cmd-check）→ 2 |
| C-ABR-03 | L2 接口契约 | F-08 | F-08 fetch_asset.py add：--source-n（--source-name 的前缀）→ 2；prune：--story（--storyboard）→ 2 |
| C-ABR-04 | L2 接口契约 | F-09 F-10 | F-09 F-10 scaffold_project.py：--for（--force 的前缀）→ 2 |
| C-ABR-05 | L2 接口契约 | F-06 F-07 | F-06 F-07 build_timeline.py：--time（--timeline 的前缀）→ 2（其余必需参数给全） |
| C-ABR-06 | L2 接口契约 | F-12 NF-02 | F-12 NF-02 validate.py 子命令同样禁用缩写：storyboard --time（--timeline）、tokens --js（--json）、video --vid（--video）→ 2 |
| C-ABR-07 | L2 接口契约 | F-11 | F-11 check_project.sh：--asp（--aspect 的前缀）、--determ（--determinism）→ 2 |
| C-ABR-08 | L2 接口契约 | F-12 | F-12 render.sh：--covers（--covers-only 的前缀）、--video（--video-only）→ 2 |
| C-AS-01 | L2 接口契约 | F-08 | F-08 授权 unknown 的素材可登记但 usable=false、usage=rejected |
| C-AS-02 | L2 接口契约 | F-08 | F-08 横屏画布：短边 1200≥1080 → fullscreen；短边 600 → card-only；已登记字段齐全 |
| C-AS-03 | L2 接口契约 | F-08 | F-08 打不开的文件 → opens=false、usable=false |
| C-AS-04 | L2 接口契约 | F-08 NF-04 | F-08 NF-04 credits-diff（Q-04，v1.3）：shot-badges.json / “素材署名：”段 [id] / deliverable.credits 三处齐全且无链接 → 0；任一处缺（简介按平台逐个，缺平台目录视为该平台全缺）、或任一平台 title/description、credits 含 URL → 7（v1.4） |
| C-AS-05 | L2 接口契约 | F-08 NF-04 | F-08 NF-04 fetch_asset.py prune（Q-04）：未被任何镜头 asset_ids 引用的条目置 usable=false；被引用的保持不变 |
| C-AS-06 | L2 接口契约 | F-08 | F-08 Q-03：不生成 assets-manifest.md，fetch_asset.py 没有 render-md 子命令（调用返回 2） |
| C-AS-07 | L2 接口契约 | F-08 | F-08 v1.3：add 用 --author 与 --source-name 记录 author、source_name（source 仍留 URL）；旧参数 --attribution 退出 2 |
| C-CLI-01 | L2 接口契约 | F-11 NF-01 | F-11 NF-01 所有 CLI 支持 --help 且退出 0；stdin 关闭时不阻塞（无交互） |
| C-DLV-01 | L2 接口契约 | F-16 | F-16 validate.py deliverable 产出 deliverable.json，字段齐全（v1.4/v1.5：publish 按平台组织标题、简介、标签，替代顶层 title/description/tags）；credits 来自 manifest 需署名且可用项，字段为 {id, author, source_name, license}，不含 URL（v1.3） |
| C-ENV-01 | L2 接口契约 | F-17 | F-17 .env 缺失 → 退出 3，errors[0].kind=missing_env，含绝对 env_path 与 var |
| C-ENV-02 | L2 接口契约 | F-17 | F-17 Key 为空 → 退出 3，kind=empty_key |
| C-ENV-03 | L2 接口契约 | F-17 NF-02 | F-17 NF-02 有效 Key → 退出 0；stdout/stderr 不含 Key、不含其长度或前缀 |
| C-ENV-04 | L2 接口契约 | F-17 | F-17 先缺失(3) → 写入 Key 后重跑 → 0（对应“填好了”后重新读取） |
| C-ENV-05 | L2 接口契约 | F-17 | F-17 缺 Key 时 tts_doubao.py 退出 3，且不产出任何音频/时间轴 |
| C-ENV-06 | L2 接口契约 | F-17 NF-02 | F-17 NF-02 --dry-run 输出鉴权说明但不含 Key 明文 |
| C-LEAK-01 | L2 接口契约 | NF-02 F-17 | NF-02 F-17 RV-3：技能包 .env 写入真实 Key 样本，同值写入日志第 3 行 → 退出 7，hits == [{file, line:3, which:"real"}]（只报文件、行号、类别），
stdout/stderr 全文不含该值，.env 本身不算命中；干净 → 0 且 real_key="checked"；测试假 Key 经 --extra-secret-file 传入，命中报 which="fake" |
| C-LEAK-02 | L2 接口契约 | NF-02 F-17 | NF-02 F-17 RV-3：技能包 .env 不存在或 Key 为空 → real_key="absent"，不判失败（退出 0），且不读环境变量里的 Key |
| C-LEAK-03 | L2 接口契约 | NF-02 | NF-02 V9-3：--extra-secret-file 指向不存在的文件 → 退出 2（修正调用）；--extra-secret-file 与 --scan 可重复传入，全部合法时 → 0 |
| C-LEAK-04 | L2 接口契约 | NF-02 | NF-02 V9-3：--scan 指定的文件不存在 → 退出 2（不得静默跳过） |
| C-LEAK-05 | L2 接口契约 | NF-02 | NF-02 V9-3：--extra-secret-file 可读但为空（含只有空白）或非 UTF-8 → 退出 5 |
| C-LEAK-06 | L2 接口契约 | NF-02 | NF-02 V9-3 + v1.10 §4.0（allow_abbrev=False）：参数拼错（--extra-secrets-file / --scna / --skilldir）、前缀缩写（--extra-secret / --extra / --sca / --skill）、缺 slug、slug 不存在 → 一律退出 2；缩写时 stderr 指出该参数 |
| C-PUB-01 | L2 接口契约 | F-13 F-08 | F-13 F-08 validate.py publish（v1.4）：合规 → 0；在每个平台的 description.txt 末尾补“素材署名：”段（幂等，每份恰好 1 个，行格式 - [id] 作者 · 来源名称 · 许可，无链接）；
publish/check.json 通过 publish-check.schema.json，targets 与 platforms 为默认 5 个平台 |
| C-PUB-02 | L2 接口契约 | F-13 | F-13 逐平台判定：31 字标题写入 xiaohongshu/ → 7；同样写入 youtube/ → 0；B 站简介含署名段总长 250 → 7；
只有 unofficial 不满足（视频号标题 4 字 <6）→ 0 且 check.json 中 channels.title.severity=warning |
| C-PUB-03 | L2 接口契约 | F-13 NF-02 | F-13 NF-02 任一平台 description.txt 或 title.txt 含链接 → validate.py publish 退出 7（v1.4） |
| C-PUB-04 | L2 接口契约 | F-13 | F-13 job.json.platforms 指定 ["bilibili"] 时只校验 bilibili：其他平台目录缺失也通过，check.json.targets == ["bilibili"]；未知平台 id → 非 0 |
| C-PUB-05 | L2 接口契约 | F-13 NF-02 | F-13 NF-02 v1.5：B 站 tags 逗号连接总长 200 → 7；抖音 6 个标签 → 0 且 check.json 记 douyin 告警；任一平台 tags 含链接 → 7；缺 publish/<p>/tags.txt → 7 |
| C-SB-01 | L2 接口契约 | F-07 | F-07 示例 storyboard 通过；有句未被任何镜覆盖 → 退出 5 |
| C-SCF-01 | L2 接口契约 | F-09 F-14 | F-09 F-14 scaffold：生成工程含 AGENTS.md、src/theme/tokens.ts、src/data/job.ts、.gitignore(.env)；目录已存在且无 --force → 退出 2 |
| C-SRC-01 | L2 接口契约 | F-04 NF-03 | F-04 NF-03 示例 script/sources 通过(0)；删掉一条来源 → 退出 5 |
| C-TL-01 | L2 接口契约 | F-15 F-05 | F-15 F-05 外部（MCP）工具产出的 timeline fixture 与脚本产出用同一 Schema：合法通过、非法失败 |
| C-TOK-01 | L2 接口契约 | F-09 NF-06 | F-09 NF-06 tokens.ts 被手改与 tokens.json 不一致 → validate.py tokens 非 0（7） |
| C-TTS-01 | L2 接口契约 | F-05 | F-05 产出 full.mp3、timeline.json、subtitles.json；timeline 每句 9 字段（v1.9 含 speech_end_s）齐全且连续 |
| C-TTS-02 | L2 接口契约 | F-05 NF-07 | F-05 NF-07 单句前 2 次瞬时失败 → 第 3 次（总尝试上限）成功；该句共 3 次尝试，其余句各 1 次 |
| C-TTS-03 | L2 接口契约 | F-05 NF-07 | F-05 NF-07 每句总尝试恰好 3 次后停止（首发 + 2 次重试，Q-17）；耗尽后不生成 full.mp3 半成品，并以“外部服务失败”报错（退出码 6 语义） |
| C-TTS-04 | L2 接口契约 | NF-07 F-05 | NF-07 F-05 第一次跑完后，用 only={'03'} 重跑：只调用第 03 句；未改动句走 parts/ 缓存不再调用 |
| C-TTS-05 | L2 接口契约 | F-17 NF-02 | F-17 NF-02 鉴权失败立即停止、不重试；异常消息与产物不含 Key |
| C-TTS-06 | L2 接口契约 | F-06 F-05 | F-06 F-05 full.mp3 时长 = Σ(句音频) + Σ(silence_ms)，不额外追加尾部静音 |
| C-TTS-07 | L2 接口契约 | F-05 F-06 | F-05 F-06 FakeTtsClient（Q-19、R-03、V9-1）：产出 PCM WAV（24 kHz 单声道 16-bit，样本数 = round(220ms×有效字数×24000)），落盘 parts/NN.wav；timeline 每句 speech_end_s − start ≈ 字数×0.22、end − speech_end_s ≈ silence_ms/1000、end − start ≈ duration_s（均 ±1ms） |
| C-TTS-08 | L2 接口契约 | F-05 | F-05 max_attempts 上限 3：传 4 → 抛参数错误（不得放宽到 4 次） |
| C-TTS-09 | L2 接口契约 | F-05 | F-05 tts_doubao.py --max-attempts 上限 3（Q-17）：传 4 → 退出 2；旧参数 --retries 不再接受（退出 2） |
| C-TTS-10 | L2 接口契约 | F-05 F-06 | F-05 F-06 R-03③ / Q-08：run_tts(FakeTtsClient, FfmpegAudioTool) 真实编码后，ffprobe(full.mp3) 与 timeline 末句 end 之差 ≤50ms |
| C-TTS-11 | L2 接口契约 | F-04 F-05 | F-04 F-05 RV-2(b)：稿件含空句 → tts_doubao.py 退出 5，stdout 末行 errors[0].kind == "empty_line"，不产出文件；
进程内把 DoubaoHttpClient 换成计数的 FakeTtsClient 后再跑同一 CLI main，FakeTts 构造与调用次数均为 0 |
| C-TTS-12 | L2 接口契约 | F-05 | F-05 RV-2(c)(d)：FakeTtsClient().duration_for("") == duration_for("。") == 0.220（防御性兜底）；duration_for("你好") == 0.440 |
| G-PATH-01 | L0 门禁工具 | F-01 | F-01 v1.11 A-21：默认 SKILL_DIR = 仓库根/.agents/skills/remotion-infographic-video（相对 tests/ 为 ../.agents/skills/remotion-infographic-video） |
| G-REL-01 | L0 门禁工具 | F-16 | F-16 cases/ 下恰有 AE-01～AE-15 共 15 个；15 份有效 PASS 存档 → 全部 OK，无缺失 |
| G-REL-02 | L0 门禁工具 | F-16 | F-16 缺 1 份 → 列出该 case_id；release_gate.py --archive-only 对空 archive 退出非 0 并列出全部 15 个 case_id |
| G-REL-03 | L0 门禁工具 | F-16 | F-16 skill_md_sha256 与当前 SKILL.md 不一致 → 视为失效；改 SKILL.md 后旧存档全部失效 |
| G-REL-04 | L0 门禁工具 | F-16 | F-16 result=FAIL、多余/缺失字段、judged_by 非 auto/human、judged_at 非 ISO8601、缺 jsonl 或 meta.json → 均失效 |
| G-REL-05 | L0 门禁工具 | F-16 | F-16 evaluate.py 复判不通过 → 失效（即使 verdict 写 PASS）；同一用例一份 FAIL + 一份有效 PASS → OK；默认用真实 evaluate.py 复判伪造的空记录 → 失效 |
| G-REL-06 | L0 门禁工具 | F-16 | F-16 run_all.sh：L1–L4 出现 SKIP → 退出非 0（SKIP 按 FAIL 计）；L5 的 SKIP 不计失败；release 子命令调用 release_gate.py |
| I-CK-01 | L3 离线集成 | F-11 | F-11 注入 TS 错误 → 退出 7；report.json（Q-10）ok=false、failed_step="tsc"、log_path 为存在的绝对路径；report 通过 check-report.schema.json |
| I-CK-02 | L3 离线集成 | F-10 | F-10 同一工程 check_project.sh --aspect both：横、竖各生成每段抽帧且安全区检测通过（report ok） |
| I-CK-03 | L3 离线集成 | F-11 NF-07 | F-11 NF-07 Q-06 / R-08：check_project.sh 总调用 ≤3。连续 3 次失败后修好错误，第 4 次调用仍退出 7，stdout 末行 JSON errors[0].kind == max_attempts_exceeded（attempts=3），stderr 含“上限”；attempts.json 记录 n=1..3 |
| I-CK-05 | L3 离线集成 | F-08 F-09 | F-08 F-09 Q-13② / R-09：在 src/Main.tsx 的 {/* @test-inject:layers */} 锚点处注入 data-layer="endcard" → 自检失败 failed_step='safe_area' |
| I-JOB-01 | L3 离线集成 | F-10 | F-10 Q-21 / R-07：job.json 缺 aspect → scaffold 回写 aspect=landscape、width=1920、height=1080；竖屏回写 1080×1440；src/data/job.ts 不含像素数字（1080/1440/1920） |
| I-LS-01 | L3 离线集成 | F-05 F-10 | F-05 F-10 landscape lufs： |
| I-LS-02 | L3 离线集成 | F-06 F-10 | F-06 F-10 landscape duration： |
| I-LS-03 | L3 离线集成 | F-06 F-10 | F-06 F-10 landscape no_tail_silence： |
| I-LS-04 | L3 离线集成 | F-12 F-10 | F-12 F-10 landscape video： |
| I-LS-05 | L3 离线集成 | F-13 F-10 | F-13 F-10 landscape covers： |
| I-LS-06 | L3 离线集成 | F-10 F-11 F-10 | F-10 F-11 F-10 landscape frames_safe： |
| I-LS-07 | L3 离线集成 | NF-05 F-10 | NF-05 F-10 landscape determinism： |
| I-LS-08 | L3 离线集成 | F-06 F-10 | F-06 F-10 landscape example_length： |
| I-LS-09 | L3 离线集成 | F-14 F-10 | F-14 F-10 landscape agents_md： |
| I-LS-10 | L3 离线集成 | F-08 NF-04 F-10 | F-08 NF-04 F-10 landscape credits： |
| I-LS-11 | L3 离线集成 | F-05 F-17 NF-02 F-10 | F-05 F-17 NF-02 F-10 landscape leak： |
| I-LS-12 | L3 离线集成 | F-09 F-10 | F-09 F-10 landscape tsc： |
| I-LS-13 | L3 离线集成 | F-09 F-10 | F-09 F-10 landscape components_used：§7.3 L3：清单组件全部在示例中被渲染（storyboard 组件 + scenes 引用） |
| I-NF6-01 | L3 离线集成 | NF-06 F-09 | NF-06 F-09 Q-23：只改 tokens.json（colors.bg→#3A0000、colors.gold→#00E5FF）重新生成工程：S03 中点帧 SHA256 改变且全帧平均 R 升高 ≥8；
tokens.ts 随之变化、validate.py tokens 通过、SKILL.md 无 diff |
| I-PT-01 | L3 离线集成 | F-05 F-10 | F-05 F-10 portrait lufs： |
| I-PT-02 | L3 离线集成 | F-06 F-10 | F-06 F-10 portrait duration： |
| I-PT-03 | L3 离线集成 | F-06 F-10 | F-06 F-10 portrait no_tail_silence： |
| I-PT-04 | L3 离线集成 | F-12 F-10 | F-12 F-10 portrait video： |
| I-PT-05 | L3 离线集成 | F-13 F-10 | F-13 F-10 portrait covers： |
| I-PT-06 | L3 离线集成 | F-10 F-11 F-10 | F-10 F-11 F-10 portrait frames_safe： |
| I-PT-07 | L3 离线集成 | NF-05 F-10 | NF-05 F-10 portrait determinism： |
| I-PT-08 | L3 离线集成 | F-06 F-10 | F-06 F-10 portrait example_length： |
| I-PT-09 | L3 离线集成 | F-14 F-10 | F-14 F-10 portrait agents_md： |
| I-PT-10 | L3 离线集成 | F-08 NF-04 F-10 | F-08 NF-04 F-10 portrait credits： |
| I-PT-11 | L3 离线集成 | F-05 F-17 NF-02 F-10 | F-05 F-17 NF-02 F-10 portrait leak： |
| I-PT-12 | L3 离线集成 | F-09 F-10 | F-09 F-10 portrait tsc： |
| I-PT-13 | L3 离线集成 | F-09 F-10 | F-09 F-10 portrait components_used：§7.3 L3：清单组件全部在示例中被渲染（storyboard 组件 + scenes 引用） |
| S-AUTO-01 | L4 静态规范 | NF-01 | NF-01 scripts/ 中无交互读取（input()、read -p、sys.stdin.readline） |
| S-CMP-01 | L4 静态规范 | F-09 | F-09 components/ 含架构 §4.12 清单列出的全部组件文件（清单实际列了 15 个名字，见歧义 Q-05） |
| S-CPY-01 | L4 静态规范 | F-01 F-17 | F-01 F-17 复制即用：复制到临时目录 + 假 Key，不执行任何 pip/uv 安装即可跑 check_env.py 与 tts_doubao.py --dry-run |
| S-DET-01 | L4 静态规范 | NF-05 | NF-05 project-template 与 example/scenes 中不出现 Math.random / Date.now |
| S-DUR-01 | L4 静态规范 | F-06 | F-06 project-template 中 durationInFrames= 只取计算值 TOTAL_FRAMES/变量，不含数字字面量；无 CREDITS 帧/尾静音参数 |
| S-ENV-01 | L4 静态规范 | F-17 NF-02 | F-17 NF-02 .env.example 含 DOUBAO_TTS_API_KEY= 且值为空；.gitignore 含 .env；技能包不分发 .env |
| S-ENV-02 | L4 静态规范 | F-17 NF-02 | F-17 NF-02 在技能包 git 仓库中：git check-ignore .env 命中；git ls-files 不含 .env |
| S-ENV-03 | L4 静态规范 | F-17 | F-17 脚本不从进程环境变量读取 Key（禁止 os.environ/getenv 读 DOUBAO_TTS_API_KEY） |
| S-EX-01 | L4 静态规范 | F-07 F-09 | F-07 F-09 assets/example 含 script.md、sources.md、storyboard.json、timeline.fixture.json、scenes/ |
| S-FNT-01 | L4 静态规范 | F-09 | F-09 assets/fonts 含 NotoSansSC Regular/Bold、JetBrainsMono 及 OFL 许可文本 |
| S-LAY-01 | L4 静态规范 | F-10 | F-10 画布尺寸 1080/1440/1920 只允许出现在 src/layout/presets.ts（v1.3）。v1.11：豁免只针对这一个文件（Python 遍历，不再依赖 rg glob）；
其他文件中任何写法都判失败——十进制、数字分隔符（1_920）、小数/指数（1920.0、1.92e3）、十六进制/八进制/二进制（0x780）、
字符串内数字、两个数字字面量相乘（960 * 2、192*10）；presets.ts 自身须用普通十进制写出 1920、1080、1440（不得用分隔符等变形），且无 9:16 竖屏 |
| S-LAY-02 | L4 静态规范 | F-09 | F-09 project-template 只有 Background/HUD/Subtitle 三层：rg Credits src/ 无结果（PRD F-09 原文；v1.4 删除 Q-13④ 的大小写不敏感扩展） |
| S-LAY-03 | L4 静态规范 | F-08 F-09 | F-08 F-09 Q-13②：project-template 中 data-layer 只取 background/scene/hud/subtitle，且四个值都出现；SourceBadge 带 data-role=source-badge |
| S-LAY-04 | L4 静态规范 | F-10 | F-10 R-06：LAYOUT.md 恰好一个 json 块，且恰为 {version:1, portrait_keywords:["竖屏"], landscape_keywords:["横屏"]} |
| S-LAY-05 | L4 静态规范 | F-08 F-09 | F-08 F-09 R-09：模板 src/Main.tsx 中注入锚点 {/* @test-inject:layers */} 恰好出现 1 次（供 I-CK-05 使用） |
| S-NF6-01 | L4 静态规范 | NF-06 | NF-06 SKILL.md 不含 tokens.json 中的任何色值（除 #070A0F），保证改 tokens 不需改 SKILL.md |
| S-PUB-01 | L4 静态规范 | F-13 NF-02 | F-13 NF-02 scripts/ 与 project-template 不含任何平台上传/发布接口 |
| S-PUB-02 | L4 静态规范 | F-13 | F-13 R-06：PUBLISH.md 恰好一个 json 块，顶层 {version:1, default_targets, platforms:{<id>: rule}}，通过 assets/schemas/platforms.schema.json；
不再出现 title_max_chars；恰好 5 个平台；default_targets 为全部 5 个（v1.4）；写明封面尺寸 1920×1080 / 1080×1440 |
| S-PUB-03 | L4 静态规范 | F-13 | F-13 平台规范表数值与 arch-QA v1.3 §U-2 一致：官方——B 站标题 <80、简介 <250；小红书标题 20、简介 1000（cjk1_ascii_half）；YouTube 标题 100、简介 5000（utf8_bytes）；非官方——抖音 30/1000、视频号 6–16/1000；标签（v1.5）——B 站逗号连接 <200、YouTube ≤500（youtube_tags）官方，抖音 ≤5 个非官方，小红书/视频号无规则 |
| S-REPO-01 | L4 静态规范 | F-01 F-14 | F-01 F-14 A-28：交付仓库根必须有静态 AGENTS.md（与 <slug>/project/AGENTS.md 分工；真源在仓库根，不是 AGENTS.md.tmpl） |
| S-REPO-02 | L4 静态规范 | F-01 F-14 | F-01 F-14 A-28 / §2.0：仓库根 AGENTS.md 须含项目说明、技能路径、使用步骤、环境前提、开发自检、与工程内 AGENTS.md 的区分 |
| S-SCH-01 | L4 静态规范 | F-11 F-08 | F-11 F-08 v1.2 新增/调整的 Schema 齐全：check-report、assets-manifest（对象顶层）、timeline、storyboard、subtitles |
| S-SK-01 | L4 静态规范 | F-01 | F-01 PRD 3.2 / 架构 v1.11：技能包内目录结构全部存在（技能根 = .agents/skills/remotion-infographic-video/） |
| S-SK-02 | L4 静态规范 | F-01 | F-01 skills-ref validate 通过（Q-16）：CLI 名 skills-ref 或 agentskills（PyPI skills-ref==0.1.1）均可，找不到 CLI 时调 skills_ref.validate()；先运行 tools/install_skills_ref.sh 安装到 tests/.venv |
| S-SK-03 | L4 静态规范 | F-01 | F-01 name 小写/数字/连字符 ≤64 且 = 目录名；description ≤1024 且含“开始制作”“口播”“横屏”“竖屏” |
| S-SK-04 | L4 静态规范 | F-01 NF-08 | F-01 NF-08 SKILL.md < 500 行 |
| S-SK-05 | L4 静态规范 | F-01 | F-01 SKILL.md 中所有相对文件引用为一层深（目录/文件），且文件存在 |
| S-SK-06 | L4 静态规范 | F-02 | F-02 SKILL.md 正文（去前置元数据）< 5000 tokens（Q-07）：tiktoken cl100k_base；无法导入时用上界估算 CJK字符×2 + 其他字符÷3 |
| S-SK-07 | L4 静态规范 | F-02 | F-02 SKILL.md 除 #070A0F 外不得出现任何 #[0-9A-Fa-f]{3,8} 色值及 rgb(/hsl(（Q-07）；不含组件 props 定义、TTS 参数 |
| S-SK-08 | L4 静态规范 | F-15 | F-15 SKILL.md 写明：有同等输入输出的 MCP 配音工具可用，否则运行 scripts/tts_doubao.py，两者 timeline 用同一 Schema |
| S-SK-09 | L4 静态规范 | F-03 F-16 F-17 | F-03 F-16 F-17 SKILL.md 含：只问选题（默认横屏 1920×1080）、前置 .env 检查、固定步骤 0–9、禁止事项（不发布/不泄露 Key）、交付清单 |
| S-SK-10 | L4 静态规范 | NF-08 | NF-08 references/ 每个文件 ≤ 300 行 |
| S-VER-01 | L4 静态规范 | F-09 | F-09 project-template/package.json 锁定 remotion 4.0.537，devDeps 含 typescript、vitest、ajv |
| T-AJV-01 | L1/L2 单元(TS) | F-07 | 示例 storyboard.json 通过 storyboard.schema.json（ajv 2020-12） |
| T-AJV-02 | L1/L2 单元(TS) | F-05 F-15 | 示例 timeline.fixture.json 与 MCP fixture 通过同一 timeline.schema.json |
| T-AJV-03 | L1/L2 单元(TS) | F-07 | storyboard 中 palette 只能用 tokens 色名，不能用色值 |
| T-DET-01 | L1/L2 单元(TS) | NF-05 | 相同 width/height/seed/count 输出完全一致；不同 seed 输出不同 |
| T-DET-02 | L1/L2 单元(TS) | F-10 | R-05 Particle{x,y,r,speed,opacity,phase} 均为有限数；0≤x<w、0≤y<h、r>0、0<opacity≤1；同参数深相等；随画布尺寸变化（不写死 1080/1920） |
| T-DET-03 | L1/L2 单元(TS) | NF-05 | 粒子数严格等于 count 参数（参考项目 46），且不依赖 Math.random |
| T-FR-01 | L1/L2 单元(TS) | F-06 | resolveLine(frame, lines, sectionStartFrame)：段内本地帧 → 所在句；末帧 300 属于末句 |
| T-FR-02 | L1/L2 单元(TS) | F-06 | lineLocalRange(id, lines, sectionStartFrame) 返回句相对段起点的本地帧区间 |
| T-FR-03 | L1/L2 单元(TS) | F-06 | timing/lines.ts 是纯函数模块：不导入 remotion（vitest 无需 Remotion 运行时） |
| T-LAY-01 | L1/L2 单元(TS) | F-10 | 横屏 1920×1080：landscape、2 列、unit=1、content ⊆ safe ⊆ canvas |
| T-LAY-02 | L1/L2 单元(TS) | F-10 | 竖屏 3:4 1080×1440：portrait、1 列堆叠、unit=1、content ⊆ safe ⊆ canvas |
| T-LAY-03 | L1/L2 单元(TS) | F-10 | 字号：unit=min(w,h)/1080；横屏标题级 168/120/68，竖屏 headingScale 0.8 → 134/96/54；h3/body/caption 两种画幅均 42/30/22（随 unit 缩放） |
| T-LAY-04 | L1/L2 单元(TS) | F-10 | 安全边距按画布尺寸推导（缩放画布，安全边距等比缩放） |
| T-LAY-05 | L1/L2 单元(TS) | F-10 | 字幕 Y 与 HUD 位置位于画布安全区内（横 1920×1080、竖 1080×1440） |
| T-LAY-06 | L1/L2 单元(TS) | F-10 | v1.3 比例表：横屏 左右 0.06w、上 0.07h、下 0.06h；竖屏 左右 0.07w、上 0.06h、下 0.06h（±1px） |
| T-LAY-07 | L1/L2 单元(TS) | F-10 | 竖屏 6 个汉字 display 标题放得下：font(display)×6 ≤ content.w；横屏单栏宽 ≥ font(display)×4 |
| T-PRE-01 | L1/L2 单元(TS) | F-10 F-13 | CANVAS_PRESETS 横 1920×1080 / 竖 1080×1440；COVER_PRESETS 横 [[1920,1080]] / 竖仅 [[1080,1440]] |
| T-REG-01 | L1/L2 单元(TS) | F-09 F-07 | components/registry 注册架构 §4.12 清单全部组件 |
| U-AS-01 | L1 单元(Py) | F-08 | F-08 打不开/授权不明→rejected；短边≥画布短边→fullscreen；否则 card-only |
| U-AS-02 | L1 单元(Py) | F-08 | F-08 PNG 头部解析宽高；非图片返回 None 或抛错 |
| U-AS-03 | L1 单元(Py) | F-08 NF-04 | F-08 NF-04 需署名且 usable 的素材在 shot-badges / 每个平台简介的“素材署名：”段 / deliverable.credits 三处都有 → 全空；usable=false 与无需署名的不参与 |
| U-AS-04 | L1 单元(Py) | F-08 NF-04 | F-08 NF-04 任一处缺失 → 对应差集为 ["A01"]；简介按平台逐个比对，只缺 bilibili 时只有 bilibili 报缺 |
| U-AS-05 | L1 单元(Py) | F-08 NF-04 | F-08 NF-04 只按“素材署名：”段内的 [asset_id] 匹配：作者名写法不同仍通过；id 只出现在段落外不算 |
| U-AS-06 | L1 单元(Py) | F-08 NF-02 NF-04 | F-08 NF-02 NF-04 lib/verify.find_urls（v1.3 U-3，URL_RE §4.6）：http(s)://、www.、裸域名（.com/.cn/.net/.org/.io/.tv/.me/.co/.info/.gov/.edu）均命中；纯来源名称不命中 |
| U-AS-07 | L1 单元(Py) | F-08 | F-08 V9-2：CC BY-NC 4.0 / CC-BY-NC-SA / cc_by_nc 均命中 denied（nc 词元）→ usage=rejected、usable=false（不被 allowed 的 cc by 前缀误放行） |
| U-AS-08 | L1 单元(Py) | F-08 NF-04 | F-08 NF-04 V9-2：CC-BY 4.0（规范化为 cc by 4.0，以“cc by + 空格/数字”开头）→ 可用（fullscreen）且 needs_attribution=true |
| U-AS-09 | L1 单元(Py) | F-08 | F-08 V9-2：nc/nd 按词元匹配：Unsplash、Unsplash License 不被 nd 误伤 → 可用且无需署名；“CC BY-ND 4.0”仍被拒 |
| U-AS-10 | L1 单元(Py) | F-08 | F-08 V9-2：licenses.json 中 no_attribution 不是 allowed 的子集（或 allowed 与 denied 有相同项）→ fetch_asset.py 加载时退出 5 |
| U-AS-11 | L1 单元(Py) | F-08 | F-08 V9-2：assets/licenses.json 通过 assets/schemas/licenses.schema.json；Schema 要求 denied 必填、additionalProperties=false、全小写；
denied 含 A-27 默认 11 项；no_attribution ⊆ allowed；allowed ∩ denied = ∅；缺 denied 的反例校验失败 |
| U-ENV-01 | L1 单元(Py) | F-17 | F-17 解析 KEY=VALUE、忽略注释和空行、去引号 |
| U-ENV-02 | L1 单元(Py) | F-17 | F-17 .env 不存在 → MissingKeyError，消息含 .env 绝对路径与变量名 |
| U-ENV-03 | L1 单元(Py) | F-17 | F-17 Key 为空或空白 → MissingKeyError |
| U-ENV-04 | L1 单元(Py) | F-17 | F-17 只从 .env 读取：进程环境变量有 Key 但 .env 缺失时仍报缺失 |
| U-ENV-05 | L1 单元(Py) | F-17 NF-02 | F-17 NF-02 有效 Key：Secret 的 repr/str 为 ***，reveal() 返回原值，不写入 os.environ |
| U-ENV-06 | L1 单元(Py) | NF-02 F-05 | NF-02 F-05 Redactor 把 Key 原文替换为 *** |
| U-RD-01 | L1 单元(Py) | F-09 NF-06 | F-09 NF-06 render_tokens_ts：tokens.json 中每个色值都出现在输出中；改一个色值输出随之改变 |
| U-RD-02 | L1 单元(Py) | F-14 | F-14 render_agents_md(ctx)：含安装/预览/渲染/自检命令和两条约定 |
| U-RD-03 | L1 单元(Py) | F-06 | F-06 render_timeline_ts：TOTAL_FRAMES = sec_to_frame(audio_seconds)，最后一段 to == TOTAL_FRAMES；无 CREDITS |
| U-RD-04 | L1 单元(Py) | F-10 | F-10 LAYOUT.md 关键词表恰好为 {portrait_keywords:["竖屏"], landscape_keywords:["横屏"]}（v1.3 U-1，不含平台名） |
| U-RD-05 | L1 单元(Py) | F-10 | F-10 resolve_aspect(topic, kw)：只含“竖屏”→portrait；只含“横屏”或都没有→landscape |
| U-RD-06 | L1 单元(Py) | F-10 | F-10 只提平台名（抖音/视频号/小红书/快手/B站/TikTok…）→ landscape；“竖版”“9:16”等非关键词也不切竖屏 |
| U-RD-07 | L1 单元(Py) | F-10 | F-10 “横屏”“竖屏”同时出现时取最后出现的那个（A-23） |
| U-SC-01 | L1 单元(Py) | F-05 F-15 | F-05 F-15 timeline 正例通过；缺 9 个必需字段任一（v1.9 含 speech_end_s）/ id 格式错 / lines 为空均失败 |
| U-SC-02 | L1 单元(Py) | F-07 | F-07 storyboard 正例通过；非法转场/入场、缺镜号/句 id/画面描述/组件均失败 |
| U-SC-03 | L1 单元(Py) | F-08 | F-08 manifest 顶层为对象 {version:1, assets:[...]}（Q-03）：正例通过；顶层数组失败；缺 文件/内容/来源/许可/是否需署名 任一失败 |
| U-SC-04 | L1 单元(Py) | F-11 | F-11 check-report.schema.json（Q-10）：ok/attempt/aspect/failed_step/steps/log_path；failed_step 枚举外取值失败 |
| U-SP-01 | L1 单元(Py) | F-04 F-05 | F-04 F-05 段数由稿件决定；句含 id/section/text/context/speech_rate/silence_ms，缺省 rate 0、pause 300 |
| U-SP-02 | L1 单元(Py) | F-04 | F-04 重复句 id 报错 |
| U-SP-03 | L1 单元(Py) | F-04 NF-03 | F-04 NF-03 lib/sources.normalize_number：汉字写法与阿拉伯写法归一为相等的 Decimal；非数字返回 None |
| U-SP-04 | L1 单元(Py) | F-04 F-05 | F-04 F-05 RV-2(a)：去空白与标点后有效字数为 0 的句子（如 [05] ……、[06] ？）→ ScriptError(kind="empty_line", line_id) |
| U-TL-01 | L1 单元(Py) | F-05 | F-05 build_timeline_lines(lines, durations_s)：首句从 0、首尾相接、end 含 silence_ms、duration_s=end-start、3 位小数、保留 id/section |
| U-TL-02 | L1 单元(Py) | F-05 | F-05 validate_continuity 返回错误列表（空=通过；v1.9 样例补 speech_end_s=end、silence_ms=0）：重叠、空隙、首句非 0、duration 不符、末句超出音频均不通过 |
| U-TL-03 | L1 单元(Py) | F-06 | F-06 末句 end 超出 ffprobe 时长时钳位到 audio_seconds（参考项目 134.419 > 133.608） |
| U-TL-04 | L1 单元(Py) | F-06 | F-06 sec_to_frame = floor(s*fps+0.5)（四舍五入，非银行家舍入） |
| U-TL-05 | L1 单元(Py) | F-05 | F-05 split_cues(line)：按标点切分并按字数比例分配，cue 在句区间内、连续、id 唯一 |
| U-TL-06 | L1 单元(Py) | F-05 | F-05 V9-1：timeline.schema.json 中 lines.items.required 含 speech_end_s，缺失 → Schema 校验失败；speech_end_s 为 number 且 >0；duration_s exclusiveMinimum 0 |
| U-TL-07 | L1 单元(Py) | F-05 | F-05 V9-1：validate_continuity 对 speech_end_s > end（及 speech_end_s ≤ start）报错；合规样例通过 |
| U-TL-08 | L1 单元(Py) | F-05 | F-05 V9-1：非末句 end − speech_end_s 与 silence_ms/1000 不符（超出 1ms）→ 报错；恰好相等通过 |
| U-TL-09 | L1 单元(Py) | F-06 | F-06 V9-1：clamp_to_audio 钳位末句后 end == audio_seconds、duration_s = end − start、speech_end_s = min(speech_end_s, end) ≤ end，且 validate_continuity 通过 |
| U-TL-10 | L1 单元(Py) | F-05 | F-05 V9-1：字幕只在 [start, speech_end_s] 显示：split_cues 首个 cue start = start，最后一个 cue end = speech_end_s，所有 cue 不进入停顿 |
| U-VD-01 | L1 单元(Py) | F-12 | F-12 分辨率=画幅（横 1920×1080 / 竖 1080×1440）、30fps、AAC、音视频差≤0.1s（含 0.100）→ [] |
| U-VD-02 | L1 单元(Py) | F-12 | F-12 分辨率错（含旧 9:16 1080×1920）、帧率错、无 AAC、时长差>0.1s 均返回非空错误列表 |
| U-VD-03 | L1 单元(Py) | F-13 | F-13 合规（5 平台各一套 title/description/tags）→ ok 且无 error；任一平台标题/简介为空或缺文件失败；缺某平台 tags.txt 失败；封面尺寸与画幅不符失败（v1.5 无全局标签个数规则） |
| U-VD-04 | L1 单元(Py) | F-13 | F-13 count_text(s, mode) 三种模式（v1.3 U-2）：grapheme（NFC 后扩展字素簇）、cjk1_ascii_half（中文 1、ASCII 字母数字 0.5，总数向上取整）、utf8_bytes |
| U-VD-05 | L1 单元(Py) | F-13 | F-13 各套只按本平台 official 规则：小红书标题 21（cjk1_ascii_half）；B 站标题 80（须 <80）、简介 250（须 ≤249）；YouTube 标题含 < >、简介 >5000 UTF-8 字节 → 本平台 error |
| U-VD-06 | L1 单元(Py) | F-13 | F-13 unofficial 规则不满足 → 本平台只告警、ok 仍为 true：抖音标题 31；视频号标题 5（<6）或 17（>16） |
| U-VD-07 | L1 单元(Py) | F-13 F-08 NF-02 | F-13 F-08 NF-02 任一平台的 title.txt 或 description.txt 出现链接（https、www.、裸域名）→ 该平台 error（v1.4） |
| U-VD-08 | L1 单元(Py) | F-13 | F-13 v1.4：每套只用本平台规则——25 字标题放 youtube/ 通过，放 xiaohongshu/ 判 xiaohongshu 错误；其他平台不受牵连 |
| U-VD-09 | L1 单元(Py) | F-13 F-08 | F-13 F-08 简介长度包含“素材署名：”段：正文 240 字 + 署名段使 B 站简介超 249 → bilibili error |
| U-VD-10 | L1 单元(Py) | F-13 | F-13 resolve_targets(job, default_targets)：job.platforms 优先（去重保序）；缺省用默认 5 个；未知平台 id → 报错 |
| U-VD-11 | L1 单元(Py) | F-13 NF-02 | F-13 NF-02 v1.5 标签逐平台：B 站逗号连接 199 通过 / 200 失败；YouTube 500 通过 / 501 失败；抖音 6 个只告警且 ok=true；小红书 1 个通过、空文件失败；任一平台标签含 URL 失败 |
| U-VD-12 | L1 单元(Py) | F-13 | F-13 count_tags(tags, rule)：grapheme 模式 = Σ字素 + 连接符；youtube_tags 模式下含空格的标签另加 2（引号） |
