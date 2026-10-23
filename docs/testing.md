# 测试说明

- 用例与运行器在仓库根 [`tests/`](../tests/)（相对技能目录为 `../tests`）
- 完整说明与修订史：[`tests/README.md`](../tests/README.md)
- 追溯矩阵（自动生成，勿手改）：[`tests/TRACEABILITY.md`](../tests/TRACEABILITY.md)
- 依据：PRD v1.5、架构 v1.11；被测技能默认 `SKILL_DIR=../.agents/skills/remotion-infographic-video`

## 1. 怎么跑

```bash
cd tests   # 在仓库根
bash run_all.sh all          # 自动门禁 L1～L4 + TS + 追溯；L5 无 AGENT_RUNNER 时 SKIP
bash run_all.sh release      # 发布门禁：all + agent-eval/archive 中 AE-01～15 各至少 1 份 PASS 存档
bash run_all.sh unit|contract|static|integration|agent|ts
python3 tools/trace.py --check
SKILL_DIR=/path/to/.agents/skills/remotion-infographic-video bash run_all.sh all
```

前提：Python ≥3.9（skills-ref 需 ≥3.11）、Node 18+、ffmpeg/ffprobe、rg、git。S-SK-02：`bash tools/install_skills_ref.sh`。

## 2. 分层与数量（共 210）

| 层 | 数量 | 说明 |
|---|---|---|
| L0 门禁工具 | 7 | 含 G-PATH-01（默认技能路径） |
| L1 单元 Py | 54 | |
| L1/L2 单元 TS | 18 | vitest + ajv |
| L2 契约 | 51 | CLI 退出码 / JSON / 产物；含 allow_abbrev |
| L3 集成 | 32 | 横屏 + 竖屏流水线等 |
| L4 静态 | 33 | Skills 规范、references、根 AGENTS（S-REPO-01/02）等 |
| L5 Agent | 15 | AE-01～15；无运行器 → SKIP（manual） |

F-01～F-17、NF-01～NF-08 共 25 条需求均有覆盖。

## 3. 已上线门禁结果（交付陈述）

- **自动门禁 `all`：210 用例中自动层全绿**（L5 15 条在无 `AGENT_RUNNER` 时 **SKIP**，人工评测另做）
- 代码审查通过；公开仓已推送并线上核对
- 对应提交：`2871d6a71e4e7c36fae4c96a5646c6fc9c1ac859`（topic `aivio-template`）

> `tests/README.md` §6 保留各版本调试过程记录；**以本节「已上线门禁结果」为当前交付结论。**

## 4. 文档相关静态检查

与文档强相关的 L4 用例包括但不限于：

- S-SK-*：SKILL.md 体量、引用一层深、步骤与禁止事项
- S-ENV-*：`.env.example` / `.gitignore`
- S-PUB-* / S-LAY-*：PUBLISH.md / LAYOUT.md JSON 块
- S-REPO-01/02：仓库根 `AGENTS.md` 存在且含 §2.0 强制段落

跑：`cd tests && bash run_all.sh static`
