# remotion-video-template

Remotion **信息图口播视频**模板 + Agent Skill（`remotion-infographic-video`）。

说一句「开始制作」并给出选题，即可自动完成：写稿 → 豆包配音 → 分镜与素材 → Remotion 动画 → 渲染成片 → 封面与分平台发布文案。**不会自动发布到任何平台。**

> **无云端部署步骤**：克隆/复制本仓库（或只复制技能目录）即可用。

## 快速开始

1. 克隆本仓库（或复制到本地）。
2. 在技能目录配置豆包 Key：

```bash
cd .agents/skills/remotion-infographic-video
cp .env.example .env
# 编辑 .env，填写 DOUBAO_TTS_API_KEY=（不要引号）
```

3. 对 Agent 说「**开始制作**」并给出选题。

- 默认画幅：横屏 **1920×1080**
- 竖屏：选题里写「竖屏」→ **1080×1440**（3:4）；平台名不影响画幅
- `.env` **只放在技能目录**，不要放在仓库根

更短的人读说明见 [`使用说明.md`](./使用说明.md)；给编码 Agent 的说明见根目录 [`AGENTS.md`](./AGENTS.md)。

## 仓库布局（架构 v1.11）

```
remotion-video-template/
├── AGENTS.md / README.md / 使用说明.md
├── docs/                    # 技术文档（需求摘要、架构、接口、测试、使用）
├── .agents/skills/remotion-infographic-video/   # 技能包（SKILL.md、scripts/、references/、assets/）
└── tests/                   # 开发门禁 / CI（不属于「只装技能」复制范围）
```

## 技术文档

| 文档 | 内容 |
|---|---|
| [docs/requirements.md](./docs/requirements.md) | 需求摘要（对齐 PRD v1.5） |
| [docs/architecture.md](./docs/architecture.md) | 架构摘要（对齐架构 v1.11） |
| [docs/interfaces.md](./docs/interfaces.md) | CLI / Schema / 退出码 |
| [docs/testing.md](./docs/testing.md) | 测试说明与门禁结果 |
| [docs/usage.md](./docs/usage.md) | 复制即用、`.env`、横竖屏、制作流程 |
| 技能内 `SKILL.md` + `references/` | Agent 执行时的权威步骤与风格规范 |

## 环境前提

Node 18+、Python 3、ffmpeg / ffprobe、网络。技能包脚本只用 Python 标准库；唯一的 `npm ci` 发生在生成的单次视频工程内。

## 自检（可选）

```bash
cd tests && bash run_all.sh all
```

当前交付门禁：210 用例自动层全绿；L5（15 条对话评测）无 `AGENT_RUNNER` 时 SKIP，人工另做。详见 [docs/testing.md](./docs/testing.md)。

## 许可证与密钥

- 豆包 TTS Key 仅存在于技能目录 `.env`（已被 `.gitignore`），切勿提交或粘贴到聊天。
- 字体为 OFL，随技能包分发；第三方素材须符合 `assets/licenses.json` 白名单并署名。
