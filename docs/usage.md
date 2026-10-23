# 使用说明（复制即用 · 无部署）

本模板**没有**云端部署步骤。交付物是可复制的文件夹 + Agent Skill。

## 1. 复制即用（两种方式）

### A. 整仓（推荐）

```bash
git clone https://github.com/atlantis-mk/remotion-video-template.git
cd remotion-video-template
```

包含根 `AGENTS.md`、`docs/`、`tests/` 与技能包。

### B. 只装技能

把目录 `.agents/skills/remotion-infographic-video/` **原样**复制到目标仓库的同名路径（含 `scripts/lib/`）。不含根 `tests/` 门禁。

## 2. 配置豆包 Key（必做）

Key **只**放在技能目录 `.env`，**不要**放在仓库根，也不要贴进聊天。

```bash
cd .agents/skills/remotion-infographic-video
cp .env.example .env
# 编辑 .env：
# DOUBAO_TTS_API_KEY=你的Key     （等号后直接写，不要引号）
# # DOUBAO_SPEAKER=…            （可选，默认见 references/VOICE.md）
```

- `.env` 已被技能内 `.gitignore` 忽略
- 脚本**只读**该文件，不回退进程环境变量（F-17）
- 缺 Key 时 `check_env.py` 退出码 3，提示填写路径后再继续

## 3. 开始制作

对支持 Agent Skills 的编码 Agent（会加载 `.agents/skills/`）说：

> 开始制作  
> （可选）附上选题；要竖屏就在选题里写「竖屏」

行为约定：

1. 先跑 `python3 scripts/check_env.py`
2. 消息里已有选题 → 直接进入固定步骤 1–9；否则**只问一句**选题
3. 选题之后到交付之间不再提问、不索要素材
4. 交付成片、封面、各平台文案与 `deliverable.json`；**不上传、不发布**

权威流程：技能内 [`SKILL.md`](../.agents/skills/remotion-infographic-video/SKILL.md)。

## 4. 横竖屏约定

| 规则 | 说明 |
|---|---|
| 默认 | 横屏 **1920×1080**（16:9） |
| 竖屏 | 选题中出现「竖屏」→ **1080×1440**（3:4） |
| 关键词 | 只认「横屏」「竖屏」；同时出现取**最后**出现者 |
| 平台名 | 「做一条抖音」等**不影响**画幅，仍默认横屏 |
| 真源 | `references/LAYOUT.md` 的 JSON 块（`portrait_keywords` / `landscape_keywords`） |

## 5. 环境前提

自行安装（脚本不代装）：**Node 18+**、**Python 3**、**ffmpeg / ffprobe**、网络。  
唯一自动安装：步骤 6 生成工程内的 `npm ci`。

## 6. 自检（维护者可选）

```bash
cd tests && bash run_all.sh all
```

见 [testing.md](./testing.md)。

## 7. 相关文件

- 最短人读：[`使用说明.md`](../使用说明.md)
- Agent 读：[`AGENTS.md`](../AGENTS.md)
- 发布文案规则：`references/PUBLISH.md`
- 配音参数：`references/VOICE.md`
