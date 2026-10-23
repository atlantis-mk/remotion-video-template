# 架构摘要（对齐架构 v1.11）

- 版本：架构 v1.11（交付根 `AGENTS.md` + 技能落在 `.agents/skills/`；`tests/` 留仓根）
- 原则：复制即用；Python 脚本标准库；依赖安装仅在生成的 Remotion 工程内 `npm ci`

## 1. 交付仓库根布局（§2.0 / A-28）

```
remotion-video-template/
├── AGENTS.md                 # 必有：如何用本模板
├── README.md / 使用说明.md   # 给人看（可选/推荐）
├── docs/                     # 本技术文档
├── .agents/skills/remotion-infographic-video/
│   ├── SKILL.md
│   ├── .env.example / .gitignore
│   ├── scripts/ (+ lib/)
│   ├── references/
│   └── assets/（project-template、example、fonts、tokens、schemas）
└── tests/                    # TDD/CI；不进「只装技能」复制范围
```

- 不采用仓库根平铺技能包，也不采用仅 `.cursor/skills/`
- `.env` 在技能目录，不在仓库根

## 2. 技能内模块（摘要）

| 区域 | 职责 |
|---|---|
| `scripts/*.py` / `*.sh` | 步骤 CLI（check_env、tts、scaffold、build_timeline、fetch_asset、validate、check、render） |
| `scripts/lib/` | 纯函数与适配器（envfile、parser、timeline、tts、assets、verify…）可单测 |
| `references/` | STYLE / MOTION / COMPONENTS / LAYOUT / VOICE / SCRIPT / ASSETS / PUBLISH |
| `assets/project-template/` | 最小 Remotion 骨架 + 15 风格组件 + 四层（bg/scene/hud/subtitle） |
| `assets/schemas/` | 产物 JSON Schema（job、timeline、storyboard、manifest…） |
| `assets/tokens.json` | 设计 Token 唯一真源 |

## 3. 单次制作工作区

每次制作在仓库（或工作目录）下使用 `<slug>/`：

- `job.json`、`script.md`、`sources.md`、`storyboard.json`、`assets-manifest.json`
- `voice/`（full.mp3、timeline.json、subtitles.json）
- `project/`（scaffold 出的 Remotion 工程）
- `out/video.mp4`、`publish/`（封面 + 各平台文案）、`deliverable.json`

## 4. 横竖屏（F-10）

- 关键词表在 `references/LAYOUT.md` 的 JSON 块（机读唯一来源）
- 画布常量仅允许写在工程 `src/layout/presets.ts`
- 运行时用 `computeLayout(width, height, tokens.layout)` / `useLayout()`
- 封面：横 `publish/cover_1920x1080.png`；竖 `publish/cover_1080x1440.png`

## 5. `.env` 与 Key（F-17）

- 只读技能包根 `.env` 的 `DOUBAO_TTS_API_KEY`（可选 `DOUBAO_SPEAKER`）
- **不**回退进程环境变量
- 日志/产物经 Redactor；`validate.py leak` 扫泄露

## 6. CLI 约定（v1.10）

- 全部 `argparse`：`allow_abbrev=False`；拼错/缩写 → 退出码 2
- Bash 脚本遇未知参数同样退出 2
- 脚本 stdout **最后一行**为 JSON 摘要

## 7. 测试分层（摘要）

L0 门禁工具 → L1 单元 → L2 契约 → L3 集成 → L4 静态 → L5 Agent 评测（UR-1=B：无运行器 SKIP，发布另需 15 份 PASS 存档）。详见 [testing.md](./testing.md)。

## 8. 两份 AGENTS.md

| 文件 | 约束 |
|---|---|
| 仓库根 `AGENTS.md` | 如何用本模板 |
| `<slug>/project/AGENTS.md` | 单次视频工程（由 `AGENTS.md.tmpl` 生成） |
