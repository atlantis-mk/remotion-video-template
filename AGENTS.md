# AGENTS.md — remotion-video-template

本文件给编码 Agent 读：说明**如何用本交付仓库制作信息图口播视频**。规范见 https://agents.md/。

## 1. 项目是什么

本仓库是 **Remotion 信息图口播视频模板 + Agent Skill**：用一个选题自动完成写稿、豆包配音、分镜与素材、Remotion 动画、渲染成片、封面与分平台发布文案。技能名 `remotion-infographic-video`。

## 2. 技能位置

技能包固定在：

```
.agents/skills/remotion-infographic-video/
```

（跨客户端 Agent Skills 约定路径；不要改成仓库根平铺，也不要只放到 `.cursor/skills/`。）

`tests/` 在**仓库根**（与 `.agents/` 同级），是开发门禁/CI，不属于技能运行时，不进入「只装技能」的复制范围。

## 3. 使用步骤

1. 复制或打开本仓库（整仓克隆即可用；也可只把 `.agents/skills/remotion-infographic-video/` 复制到目标仓的同名路径）。
2. 在**技能目录**执行：`cp .env.example .env`，编辑 `.env` 填写 `DOUBAO_TTS_API_KEY`（不要引号；`.env` 只放在技能目录，不放仓库根）。
3. 对 Agent 说「开始制作」并给出选题。默认横屏 1920×1080；若要竖屏，须在选题中写「竖屏」（3:4，1080×1440）。平台名不影响画幅。

## 4. 环境前提

- Node 18+
- Python 3
- ffmpeg / ffprobe
- 网络

（与 PRD compatibility 一致；脚本不代装这些工具。唯一的依赖安装发生在生成工程内的 `npm ci`。）

## 5. 开发 / 自检命令

在仓库根：

```bash
# 跑测试门禁（默认 SKILL_DIR 相对 tests 为 ../.agents/skills/remotion-infographic-video）
cd tests && bash run_all.sh all
# 也可显式指定：
# SKILL_DIR=../.agents/skills/remotion-infographic-video bash run_all.sh all
```

对技能目录做 Skills 规范校验：

```bash
skills-ref validate .agents/skills/remotion-infographic-video
# 或
agentskills validate .agents/skills/remotion-infographic-video
```

技能内常用 CLI（路径相对技能根；先 `cd .agents/skills/remotion-infographic-video`）：

```bash
python3 scripts/check_env.py
python3 scripts/tts_doubao.py <slug>/script.md --out-dir <slug>/voice
python3 scripts/scaffold_project.py --job <slug>/job.json --out <slug>/project
python3 scripts/build_timeline.py --timeline <slug>/voice/timeline.json --storyboard <slug>/storyboard.json --subtitles <slug>/voice/subtitles.json --manifest <slug>/assets-manifest.json --project <slug>/project
bash scripts/check_project.sh <slug>
bash scripts/render.sh <slug>
python3 scripts/validate.py publish <slug>
python3 scripts/validate.py leak <slug>
```

更完整步骤见技能内 `SKILL.md`。

## 6. 两份 AGENTS.md 的区分

| 文件 | 谁写 | 约束什么 |
|---|---|---|
| **仓库根** `AGENTS.md`（本文件） | 静态源文件，随仓交付 | **如何用本模板**（技能位置、填 `.env`、跑 tests、开始制作） |
| **`<slug>/project/AGENTS.md`** | `scaffold_project.py` 按 `assets/project-template/AGENTS.md.tmpl` 生成（F-14） | **那条视频工程**（`npm ci`、预览、渲染、自检、风格与密钥约定） |

不要把二者混用：改「怎么用模板」改仓库根本文件；改「单次工程内约定」改技能内模板。

## 7. 人读文档

- 最短上手：仓库根 `使用说明.md`
- 总览：`README.md`
- 技术文档（需求 / 架构 / 接口 / 测试 / 使用）：`docs/`

## 8. Cursor Cloud 环境

- 基础镜像已有 Node 18+、Python 3.12、ffmpeg、ffprobe、ripgrep。环境安装脚本在缺少 `python3-venv` 时用 apt 安装它，然后执行 `npm ci --prefix tests/ts`，再执行 `bash tests/tools/install_skills_ref.sh`（`skills-ref==0.1.1` 进入 `tests/.venv`，静态检查 S-SK-02 依赖它）。
- 自动门禁：在仓库根执行 `cd tests && bash run_all.sh all`。离线集成用 FakeTts 和本机 ffmpeg / Remotion，不调用豆包，因此不需要 `DOUBAO_TTS_API_KEY`。
- 真实配音才要在 `.agents/skills/remotion-infographic-video/.env` 填写 Key（由 `.env.example` 复制，不要提交）。本仓库没有常驻开发服务器；Remotion Studio 只在单次视频工程目录里按需启动。

