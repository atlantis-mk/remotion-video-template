#!/usr/bin/env python3
"""步骤 6：建工程。复制 assets/project-template → 生成 src/theme/tokens.ts、src/data/job.ts、AGENTS.md，复制配音与字体。
用法：python3 scripts/scaffold_project.py --job <slug>/job.json --out <slug>/project [--force]
job.json 缺 aspect 时默认横屏 1920×1080。目录已存在且无 --force → 退出 2。"""
import argparse, json, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.cli import summary, atomic_write, read_json  # noqa: E402
from lib.render_ts import render_tokens_ts, render_job_ts  # noqa: E402
from lib.render_md import render_agents_md  # noqa: E402
from lib.job import normalize_job  # noqa: E402

SKILL = Path(__file__).resolve().parents[1]
IGNORE = shutil.ignore_patterns("node_modules", ".env", "out", "*.log", "AGENTS.md.tmpl", "__pycache__")
GITIGNORE = ["node_modules/", ".env", "out/", "*.log"]


def scaffold(job_path, out, force=False, skill=SKILL):
    raw = read_json(job_path)
    job = normalize_job(raw)
    if raw.get("aspect") != job["aspect"] or raw.get("width") != job["width"] or raw.get("height") != job["height"]:
        atomic_write(job_path, json.dumps({**raw, "aspect": job["aspect"], "width": job["width"], "height": job["height"],
                                           "fps": job["fps"]}, ensure_ascii=False, indent=2) + "\n")  # Q-21：回写默认画幅
    out = Path(out)
    tmpl = skill / "assets" / "project-template"
    if out.exists() and any(out.iterdir()):
        if not force:
            raise FileExistsError(f"{out} 已存在（加 --force 覆盖生成文件）")
    if tmpl.is_dir():
        shutil.copytree(tmpl, out, ignore=IGNORE, dirs_exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    tokens = read_json(skill / "assets" / "tokens.json")
    atomic_write(out / "src/theme/tokens.ts", render_tokens_ts(tokens))
    atomic_write(out / "src/data/job.ts", render_job_ts(job))
    t = tmpl / "AGENTS.md.tmpl"
    atomic_write(out / "AGENTS.md", render_agents_md({"slug": job["slug"], "skill_dir": str(skill), "project_dir": str(out.resolve())},
                                                     template=t.read_text(encoding="utf-8") if t.is_file() else None))
    gi = out / ".gitignore"
    have = gi.read_text().splitlines() if gi.exists() else []
    atomic_write(gi, "\n".join(have + [x for x in GITIGNORE if x not in have]) + "\n")
    copied = []
    voice = Path(job_path).resolve().parent / "voice" / "full.mp3"
    if voice.is_file():
        (out / "public/audio").mkdir(parents=True, exist_ok=True)
        shutil.copy2(voice, out / "public/audio/full.mp3"); copied.append("public/audio/full.mp3")
    fonts = skill / "assets" / "fonts"
    if fonts.is_dir():
        shutil.copytree(fonts, out / "public/fonts", dirs_exist_ok=True); copied.append("public/fonts/")
    return job, copied


def main(argv=None):
    ap = argparse.ArgumentParser(allow_abbrev=False, description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--job", required=True); ap.add_argument("--out", required=True); ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    try:
        job, copied = scaffold(a.job, a.out, a.force)
    except FileExistsError as e:
        print(f"[scaffold] {e}", file=sys.stderr)
        return summary(False, 2, {}, [{"kind": "exists", "message": str(e)}])
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"[scaffold] {e}", file=sys.stderr)
        return summary(False, 5, {}, [{"kind": "bad_input", "message": str(e)}])
    return summary(True, 0, {"project": str(Path(a.out).resolve()), "aspect": job["aspect"], "width": job["width"],
                             "height": job["height"], "copied": copied})


if __name__ == "__main__":
    sys.exit(main())
