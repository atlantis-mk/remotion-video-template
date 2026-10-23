# L5 发布存档（架构 v1.7 §7.3.1 / QA RV-1）

建议布局：`archive/<ID>/<YYYYMMDD-HHMMSS>/`，每份存档 3 个文件：

- `<ID>.jsonl`：对话记录（Q-18 格式），由宿主 Agent 如实导出，不得手写或改写
- `<ID>.meta.json`：R-01 固定字段 `{case_id, skill_dir, workdir, slug_dir|null, fake_key, started_at, finished_at, runner}`，`fake_key` 为 `TEST-<uuid4>`
- `<ID>.verdict.json`：字段恰为 `{case_id, result:"PASS"|"FAIL", skill_md_sha256, judged_by:"auto"|"human", judged_at}`；`skill_md_sha256` 为当前 SKILL.md 文件字节的 sha256，`judged_at` 为带时区的 ISO8601

发布前 AE-01～AE-15 每个用例至少 1 份有效 PASS 存档（共 15 份）。SKILL.md 一改，旧存档全部失效。
核对：`bash run_all.sh release`（= `python3 tools/release_gate.py`），它还会用 `evaluate.py` 复判每份存档。
