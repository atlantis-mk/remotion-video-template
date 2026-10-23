"""渲染生成工程的 AGENTS.md（F-14）。"""
from pathlib import Path

DEFAULT_TMPL = """# AGENTS.md — {slug}

本工程由技能包 remotion-infographic-video 的 `scaffold_project.py` 生成。技能包位置：`{skill_dir}`

## 安装依赖
```bash
npm ci
```
（工程内唯一的安装步骤）

## 预览
```bash
npx remotion studio
```

## 渲染
```bash
bash {skill_dir}/scripts/render.sh {slug_dir}
# 或工程内
npm run render
```

## 自检
```bash
npm run check
bash {skill_dir}/scripts/check_project.sh {slug_dir} --aspect both
```

## 约定
- 风格以技能包 references 为准（`{skill_dir}/references/`），不要在本工程里另起风格。
- 不提交密钥：`.env` 不入库（已写入 .gitignore），Key 只放在技能包根目录的 `.env`。
- `src/data/*.ts`、`src/theme/tokens.ts` 为自动生成文件，勿手改；改配色请改技能包 `assets/tokens.json` 后重新生成。
- 代码风格：禁止写死画布尺寸（只允许出现在 `src/layout/presets.ts`），尺寸一律来自 `useLayout()`；随机只用 Remotion 的 `random(seed)`。
"""


def render_agents_md(ctx=None, template=None, **kw):
    """ctx: {slug, skill_dir, project_dir}；template 为 AGENTS.md.tmpl 文本（缺省用内置模板）。"""
    c = dict(ctx or {}); c.update(kw)
    slug, skill_dir, project_dir = c.get("slug", ""), c.get("skill_dir", ""), c.get("project_dir")
    slug_dir = str(Path(project_dir).parent) if project_dir else f"<{slug}>"
    t = template or DEFAULT_TMPL
    return t.replace("{slug}", str(slug)).replace("{skill_dir}", str(skill_dir)).replace("{slug_dir}", slug_dir)
