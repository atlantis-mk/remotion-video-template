#!/usr/bin/env python3
"""check_project.sh 的实现（见该脚本头注释）。退出码：0 通过；2 用法；7 自检失败或已达调用上限（3 次）。"""
import argparse, datetime, hashlib, json, shutil, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.projectctl import run, npx, parse_compositions, AspectSwitch, probe_duration  # noqa: E402
from lib.render_ts import frame_tables  # noqa: E402
from lib.timeline import sec_to_frame  # noqa: E402
from lib.job import normalize_job, PRESETS  # noqa: E402
from lib.cli import summary, write_json, read_json  # noqa: E402
from lib import schema_check  # noqa: E402

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL = SCRIPTS.parent
MAX_CALLS = 3
TZ = datetime.timezone(datetime.timedelta(hours=8))


def now():
    return datetime.datetime.now(TZ).isoformat(timespec="seconds")


def main(argv=None):
    ap = argparse.ArgumentParser(allow_abbrev=False, prog="check_project.sh", description=__doc__)
    ap.add_argument("slug"); ap.add_argument("--aspect", choices=["landscape", "portrait", "both"])
    ap.add_argument("--determinism", action="store_true", help="同一帧渲染两次比较哈希（NF-05）")
    a = ap.parse_args(argv)
    slug = Path(a.slug).resolve(); proj = slug / "project"; chk = slug / "check"
    (chk / "logs").mkdir(parents=True, exist_ok=True); (chk / "frames").mkdir(parents=True, exist_ok=True)
    att_p = chk / "attempts.json"
    attempts = read_json(att_p) if att_p.exists() else []
    if len(attempts) >= MAX_CALLS:
        msg = f"check_project.sh 已调用 {len(attempts)} 次，达到上限 {MAX_CALLS} 次（F-11）：停止修复并向用户报告 check/report.json"
        print(f"[check] {msg}", file=sys.stderr)
        return summary(False, 7, {"report": str(chk / "report.json")}, [{"kind": "max_attempts_exceeded", "attempts": len(attempts), "limit": MAX_CALLS, "message": msg}])
    n = len(attempts) + 1
    job = normalize_job(read_json(slug / "job.json"))
    aspects = ["landscape", "portrait"] if a.aspect == "both" else [a.aspect or job["aspect"]]
    steps, failed = [], None
    started = now()

    def step(name, aspect, fn):
        nonlocal failed
        log = chk / "logs" / f"{name}-{aspect}.log"
        if log.exists(): log.unlink()
        t0 = time.time()
        try:
            ok, msg = fn(log)
        except Exception as e:  # noqa: BLE001
            ok, msg = False, f"{type(e).__name__}: {e}"
            with open(log, "a", encoding="utf-8") as f: f.write(msg + "\n")
        if not log.exists(): log.write_text((msg or "") + "\n", encoding="utf-8")
        steps.append({"name": name, "aspect": aspect, "ok": ok, "log_path": str(log), "duration_ms": int((time.time() - t0) * 1000),
                      **({"message": msg[:500]} if msg else {})})
        if not ok and not failed:
            failed = steps[-1]
        print(f"[check] {aspect} {name}: {'ok' if ok else 'FAIL'} {msg or ''}", file=sys.stderr)
        return ok

    tl = read_json(slug / "voice/timeline.json")
    sb = read_json(slug / "storyboard.json")
    fps = job["fps"]
    total, _lines, sections, _shots = frame_tables(tl, sb, fps)
    audio = proj / "public/audio/full.mp3"
    audio = audio if audio.exists() else slug / "voice/full.mp3"
    a_sec = probe_duration(audio) if audio.exists() else tl["audio_seconds"]

    for aspect in aspects:
        with AspectSwitch(proj, job, aspect):
            W, H = PRESETS[aspect]   # 横 1920×1080 / 竖 1080×1440（v1.3）
            frames = {s["id"]: (s["from"] + max(s["to"] - 1, s["from"])) // 2 for s in sections}

            def tsc(log):
                p, _ = run([npx(), "tsc", "--noEmit"], proj, log); return p.returncode == 0, (p.stdout + p.stderr).strip()[-300:]

            def comps(log):
                p, _ = run([npx(), "remotion", "compositions", "src/index.ts"], proj, log)
                if p.returncode != 0: return False, p.stderr.strip()[-300:]
                c = parse_compositions(p.stdout).get("Main")
                if not c: return False, "compositions 中没有 Main"
                want = sec_to_frame(a_sec, fps)
                errs = []
                if abs(c["frames"] - want) > 1: errs.append(f"durationInFrames {c['frames']} 与 round(ffprobe×{fps})={want} 差 >1 帧")
                if c["fps"] != fps: errs.append(f"fps {c['fps']} ≠ {fps}")
                if (c["width"], c["height"]) != (W, H): errs.append(f"画布 {c['width']}x{c['height']} ≠ {W}x{H}")
                return not errs, "；".join(errs)

            def stills(log):
                bad = []
                for sid, fr in frames.items():
                    out = chk / "frames" / f"{aspect}-{sid}.png"
                    p, _ = run([npx(), "remotion", "still", "src/index.ts", "Main", str(out), f"--frame={fr}"], proj, log)
                    if p.returncode != 0 or not out.exists(): bad.append(sid)
                return not bad, (f"抽帧失败：{bad}" if bad else "")

            def safe(log):
                sa = proj / "scripts/safe-area.mjs"
                if not sa.exists(): return False, f"缺少 {sa}"
                last = sections[-1] if sections else {"to": total}
                tail = [f for f in range(max(0, last["to"] - 30), last["to"], 10)]
                out = chk / f"safe-area-{aspect}.json"
                p, _ = run(["node", str(sa), "--entry", "src/index.ts", "--composition", "Main",
                            "--frames", ",".join(map(str, sorted(set(frames.values())))), "--credits-frames", ",".join(map(str, tail)),
                            "--width", W, "--height", H, "--out", str(out)], proj, log)
                return p.returncode == 0, (p.stdout + p.stderr).strip()[-300:]

            def static(log):
                errs = []
                rg = shutil.which("rg")
                if not rg: return False, "缺少 rg"
                for pat, extra, what in ((r"1080|1440|1920", ["--glob", "!**/layout/presets.ts", "--glob", "!**/data/**"], "写死画布尺寸"),
                                         (r"Math\.random|Date\.now\(", [], "非确定性随机/时间"),
                                         (r"(?i)credits", [], "出现 Credits（无片尾署名页）")):
                    p, _ = run([rg, "-n", *extra, pat, "src"], proj, log)
                    if p.stdout.strip(): errs.append(f"{what}：{p.stdout.strip().splitlines()[0]}")
                p, _ = run([sys.executable, SCRIPTS / "validate.py", "tokens", "--json", SKILL / "assets/tokens.json",
                            "--ts", proj / "src/theme/tokens.ts"], proj, log)
                if p.returncode != 0: errs.append("tokens.ts 与 tokens.json 不一致")
                man = slug / "assets-manifest.json"
                if man.exists():
                    p, _ = run([sys.executable, SCRIPTS / "fetch_asset.py", "credits-diff", "--manifest", man, "--slug-dir", slug,
                                "--only", "badge"], proj, log)
                    if p.returncode != 0: errs.append("镜头 SourceBadge 署名缺失")
                return not errs, "；".join(errs)

            def determinism(log):
                fr = next(iter(frames.values()), 0); hs = []
                for i in range(2):
                    out = chk / f"det-{aspect}-{i}.png"
                    p, _ = run([npx(), "remotion", "still", "src/index.ts", "Main", str(out), f"--frame={fr}"], proj, log)
                    if p.returncode != 0: return False, "渲染失败"
                    hs.append(hashlib.sha256(out.read_bytes()).hexdigest())
                return hs[0] == hs[1], ("" if hs[0] == hs[1] else "同一帧两次渲染哈希不同")

            plan = [("tsc", tsc), ("compositions", comps), ("frames", stills), ("safe_area", safe), ("static", static)]
            if a.determinism: plan.append(("determinism", determinism))
            for name, fn in plan:
                if not step(name, aspect, fn): break
        if failed: break

    ok = failed is None
    rep = {"ok": ok, "attempt": n, "aspect": aspects[0] if len(aspects) == 1 else "both",
           "failed_step": None if ok else failed["name"], "steps": steps, "log_path": None if ok else failed["log_path"],
           "started_at": started}
    if a.aspect == "both" or len(aspects) == 1:
        rep["aspect"] = aspects[0] if len(aspects) == 1 else (failed["aspect"] if failed else "both")
    sch = SKILL / "assets/schemas/check-report.schema.json"
    if sch.exists():
        errs = schema_check.validate(rep, read_json(sch))
        if errs: print(f"[check] report 不合 Schema：{errs}", file=sys.stderr)
    write_json(chk / "report.json", rep)
    attempts.append({"n": n, "started_at": started, "ok": ok, "failed_step": rep["failed_step"]})
    write_json(att_p, attempts)
    left = MAX_CALLS - n
    if not ok:
        print(f"[check] 失败步骤 {rep['failed_step']}，日志 {rep['log_path']}；剩余可调用 {left} 次（上限 {MAX_CALLS}）", file=sys.stderr)
    return summary(ok, 0 if ok else 7, {"report": str(chk / "report.json"), "attempt": n, "remaining": left},
                   [] if ok else [{"kind": "check_failed", "step": rep["failed_step"], "log_path": rep["log_path"], "message": next((s.get("message", "") for s in rep["steps"] if not s["ok"]), "")}])


if __name__ == "__main__":
    sys.exit(main())
