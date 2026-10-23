#!/usr/bin/env python3
"""render.sh 的实现（见该脚本头注释）。退出码：0 通过；2 用法；7 渲染或验收失败。"""
import argparse, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.projectctl import run, npx, cover_presets  # noqa: E402
from lib.job import normalize_job  # noqa: E402
from lib.cli import summary, read_json  # noqa: E402

SCRIPTS = Path(__file__).resolve().parents[1]


def main(argv=None):
    ap = argparse.ArgumentParser(allow_abbrev=False, prog="render.sh", description=__doc__)
    ap.add_argument("slug"); g = ap.add_mutually_exclusive_group()
    g.add_argument("--covers-only", action="store_true"); g.add_argument("--video-only", action="store_true")
    a = ap.parse_args(argv)
    slug = Path(a.slug).resolve(); proj = slug / "project"
    job = normalize_job(read_json(slug / "job.json"))
    logs = slug / "check" / "logs"; logs.mkdir(parents=True, exist_ok=True)
    log = logs / "render.log"
    outputs, errs = {}, []
    if not a.covers_only:
        video = slug / "out" / "video.mp4"; video.parent.mkdir(parents=True, exist_ok=True)
        p, _ = run([npx(), "remotion", "render", "src/index.ts", "Main", str(video), "--codec=h264", "--audio-codec=aac"], proj, log)
        if p.returncode != 0 or not video.exists():
            return summary(False, 7, {"log": str(log)}, [{"kind": "render_failed", "log_path": str(log)}])
        outputs["video"] = str(video)
        v = subprocess.run([sys.executable, str(SCRIPTS / "validate.py"), "video", str(slug)], capture_output=True, text=True)
        with open(log, "a", encoding="utf-8") as f: f.write(v.stdout + v.stderr)
        if v.returncode != 0:
            errs.append({"kind": "verify_failed", "detail": v.stdout.strip().splitlines()[-1] if v.stdout.strip() else v.stderr[-300:]})
    if not a.video_only:
        pub = slug / "publish"; pub.mkdir(parents=True, exist_ok=True)
        covers = []
        for w, h in cover_presets(proj).get(job["aspect"], []):
            out = pub / f"cover_{w}x{h}.png"
            p, _ = run([npx(), "remotion", "still", "src/index.ts", "Cover", str(out), "--frame=0",
                        f'--props={{"width":{w},"height":{h}}}'], proj, log)
            if p.returncode != 0 or not out.exists():
                errs.append({"kind": "cover_failed", "size": f"{w}x{h}", "log_path": str(log)})
            else:
                covers.append(str(out))
        outputs["covers"] = covers
    if errs:
        return summary(False, 7, {**outputs, "log": str(log)}, errs)
    return summary(True, 0, outputs)


if __name__ == "__main__":
    sys.exit(main())
