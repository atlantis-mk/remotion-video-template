# 需求摘要（对齐 PRD v1.5）

- 产品：Remotion 信息图口播视频 **Agent Skill**（`remotion-infographic-video`）
- 定稿版本：PRD v1.5｜对齐架构 v1.11｜日期 2026-10-23（Asia/Shanghai）
- 目标：用户说「开始制作」→ Agent **只问选题** → 自动产出成片、封面、分平台文案；**不自动发布**

## 1. 用户故事（摘要）

| ID | 要点 |
|---|---|
| US-1 | 「开始制作」后只问选题；之后全自动交付 |
| US-2 | 默认横屏 1920×1080；选题含「竖屏」→ 1080×1440 |
| US-6 | 豆包 Key 填在技能目录 `.agents/skills/remotion-infographic-video/.env`，不入库 |
| US-7 | 根有 `AGENTS.md`；可整仓用，或只复制技能目录到同名路径 |
| US-3～5 | Agent 按 SKILL 执行；改风格只改 tokens/references；数据与素材有出处与署名 |

## 2. 交付形态

- **复制即用，无云端部署**
- 整仓克隆，或把 `.agents/skills/remotion-infographic-video/` 复制到目标仓同名路径
- `tests/` 在仓库根，属开发/CI，不进「只装技能」范围
- `.env` 始终在**技能包根**，不是仓库根

## 3. 功能清单（F）与验收要点

| ID | 能力 | 实现落点（摘要） |
|---|---|---|
| F-01 | Agent Skills 规范 | `SKILL.md` 元数据 + `skills-ref`/`agentskills validate`；根 `AGENTS.md`（A-28） |
| F-02 | 渐进式加载 | SKILL &lt;500 行 / &lt;5000 tokens；references 单文件 ≤300 行 |
| F-03 | 触发与只问选题 | 「开始制作」；缺选题只问一句；默认横屏 |
| F-04 | 写稿 + 出处 | `script.md` / `sources.md`；`validate.py sources` |
| F-05 | 豆包配音 | `tts_doubao.py`；Key 只读技能 `.env`；timeline Schema |
| F-06 | 片长 = 配音 | 无片尾补静音；无 Credits 层 |
| F-07 | 分镜 | `storyboard.json`；组件/转场/入场枚举 |
| F-08 | 素材与署名 | `fetch_asset.py`；三处署名一致且无链接 |
| F-09 | 风格 Token | `assets/tokens.json` → 工程 `tokens.ts`；15 组件 |
| F-10 | 横竖屏 | LAYOUT 关键词；`computeLayout` / presets |
| F-11 | 自检 | `check_project.sh`；最多 3 轮 |
| F-12 | 渲染 | `render.sh` → `out/video.mp4` + 封面 |
| F-13 | 发布文案 | 每平台 title/description/tags；不上传 |
| F-14 | 工程内 AGENTS.md | scaffold 由 tmpl 生成 |
| F-15 | MCP 可替换配音 | 同等 I/O 可用 MCP，否则脚本；同一 Schema |
| F-16 | 交付摘要 | `deliverable.json` 一次性回报 |
| F-17 | Key 安全 | 只读技能 `.env`；产物/日志脱敏；`validate.py leak` |

非功能（NF-01～08）：自动化、无泄露、数据真实、署名、确定性随机、Token 单一真源、TTS 重试上限、体量限制等，详见 `tests/TRACEABILITY.md`。

## 4. 固定制作步骤（0–9）

0. `check_env.py` → 1. `job.json` → 2. 写稿校验 → 3. TTS → 4. 分镜 → 5. 素材 → 6. scaffold + `build_timeline` + `npm ci` → 7. `check_project.sh` → 8. `render.sh` → 9. 发布文案 + deliverable + leak

权威步骤正文：技能内 [`SKILL.md`](../.agents/skills/remotion-infographic-video/SKILL.md)。

## 5. 画幅约定（U-1）

- 只认关键词「横屏」「竖屏」；同时出现取**最后**出现者
- 平台名（抖音、B 站等）**不影响**画幅
- 横屏 16:9 **1920×1080**；竖屏 3:4 **1080×1440**
