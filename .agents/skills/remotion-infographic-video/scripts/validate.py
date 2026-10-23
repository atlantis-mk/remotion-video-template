#!/usr/bin/env python3
"""产物校验（全部基于 assets/schemas，与 MCP 工具产出共用同一 Schema）。
  timeline <timeline.json>                         Schema + 连续性（F-05、F-15）
  subtitles <subtitles.json>
  storyboard <storyboard.json> --timeline T [--manifest M] [--sources S]   句全覆盖、枚举、组件（F-07）
  sources <script.md> <sources.md>                 稿中每个数字都有出处（F-04、NF-03）
  manifest <assets-manifest.json>
  job <job.json>
  tokens --json assets/tokens.json --ts project/src/theme/tokens.ts       （F-09、NF-06）
  video <slug> [--video out/video.mp4]             分辨率/30fps/AAC/音视频差 ≤0.1s（F-12）
  publish <slug>                                   标题/简介/标签/封面；自动补“素材署名”段（F-13、F-08）
  deliverable <slug>                               生成 deliverable.json（F-16）
  leak <slug> [--skill-dir D]                      产物与日志中不得出现 Key（只报文件名）（NF-02）
退出码：0 通过；2 用法；3 缺 Key（leak）；5 输入不合 Schema；7 校验未通过。"""
import argparse, json, json, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.cli import summary, write_json, read_json, atomic_write  # noqa: E402
from lib import schema_check, assets as A, credits as C, sources as SRC, script_parser  # noqa: E402
from lib.timeline import validate_continuity  # noqa: E402
from lib.storyboard import check_storyboard  # noqa: E402
from lib.render_ts import render_tokens_ts  # noqa: E402
from lib.verify import verify_video, validate_publish, resolve_targets, find_urls  # noqa: E402
from lib.job import normalize_job  # noqa: E402

SKILL = Path(__file__).resolve().parents[1]


def _fail(code, errs, outputs=None):
    for e in errs: print(f"[validate] {e}", file=sys.stderr)
    return summary(False, code, outputs or {}, [{"message": e} for e in errs])


def _schema(doc, name):
    return schema_check.validate(doc, schema_check.load_schema(name))


def _load(p):
    try:
        return read_json(p), None
    except (OSError, ValueError) as e:
        return None, f"无法读取 {p}：{e}"


def c_timeline(a):
    d, e = _load(a.file)
    if e: return _fail(5, [e])
    errs = _schema(d, "timeline.schema.json")
    if not errs:
        errs = validate_continuity(d["lines"], d["audio_seconds"])
        ids = [l["id"] for l in d["lines"]]
        if len(set(ids)) != len(ids): errs.append("句 id 重复")
    return _fail(5, errs) if errs else summary(True, 0, {"lines": len(d["lines"]), "audio_seconds": d["audio_seconds"]})


def c_simple(name):
    def f(a):
        d, e = _load(a.file)
        if e: return _fail(5, [e])
        if name == "job.schema.json" and "aspect" not in d: d = normalize_job(d)
        errs = _schema(d, name)
        if name == "subtitles.schema.json" and not errs:
            ids = [c["id"] for c in d["cues"]]
            if len(set(ids)) != len(ids): errs.append("cue id 重复")
        return _fail(5, errs) if errs else summary(True, 0, {})
    return f


def c_storyboard(a):
    sb, e = _load(a.file)
    if e: return _fail(5, [e])
    tl = man = srcs = None
    if a.timeline:
        tl, e = _load(a.timeline)
        if e: return _fail(5, [e])
    if a.manifest: man = A.load_manifest(a.manifest)
    if a.sources: srcs = SRC.parse_sources_md(Path(a.sources).read_text(encoding="utf-8"))
    errs = check_storyboard(sb, tl, man, srcs)
    return _fail(5, errs) if errs else summary(True, 0, {"sections": len(sb["sections"])})


def c_sources(a):
    try:
        lines = script_parser.parse(Path(a.script).read_text(encoding="utf-8"))
        srcs = SRC.parse_sources_md(Path(a.sources).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return _fail(5, [str(e)])
    errs = _schema(srcs, "sources.schema.json") + SRC.check_sources(lines, srcs)
    return _fail(5, errs) if errs else summary(True, 0, {"lines": len(lines), "sources": len(srcs)})


def c_tokens(a):
    try:
        want = render_tokens_ts(read_json(a.json))
        have = Path(a.ts).read_text(encoding="utf-8")
    except (OSError, ValueError) as e:
        return _fail(5, [str(e)])
    norm = lambda s: re.sub(r"\s+", "", s).lower()
    if norm(want) != norm(have):
        cj = {c.lower() for c in re.findall(r"#[0-9A-Fa-f]{6}\b", want)}
        ct = {c.lower() for c in re.findall(r"#[0-9A-Fa-f]{6}\b", have)}
        return _fail(7, [f"tokens.ts 与 tokens.json 不一致（缺 {sorted(cj - ct)}，多 {sorted(ct - cj)}）；请重新运行 scaffold 生成，勿手改"])
    return summary(True, 0, {})


def ffprobe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(p)], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


def c_video(a):
    slug = Path(a.slug)
    job = normalize_job(read_json(slug / "job.json"))
    v = Path(a.video) if a.video else slug / "out/video.mp4"
    if not v.exists(): return _fail(7, [f"缺少成片 {v}"])
    pr = ffprobe(v)
    if not pr: return _fail(7, [f"ffprobe 无法读取 {v}"])
    full = slug / "voice/full.mp3"
    aud = None
    if full.exists():
        fp = ffprobe(full); aud = float(fp["format"]["duration"]) if fp else None
    errs = verify_video(pr, job, aud)
    return _fail(7, errs) if errs else summary(True, 0, {"video": str(v)})


def publish_table(skill=SKILL):
    """PUBLISH.md 中含 platforms 的 JSON 块（平台规范表唯一来源）。"""
    t = (skill / "references" / "PUBLISH.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```json\s*\n(.*?)```", t, re.S)
    if len(blocks) == 1:
        return json.loads(blocks[0])
    raise ValueError("PUBLISH.md 应恰好 1 个含 platforms 的 json 块")


def _targets(job):
    tb = publish_table()
    return tb, resolve_targets(job, tb["default_targets"])


def c_publish(a):
    slug = Path(a.slug); pub = slug / "publish"
    job = normalize_job(read_json(slug / "job.json"))
    try:
        tb, targets = _targets(job)
    except ValueError as e:
        return summary(False, 5, {}, [{"kind": "input", "message": str(e)}])
    man = A.load_manifest(slug / "assets-manifest.json")
    for pid in targets:
        dp = pub / pid / "description.txt"
        if dp.is_file():
            desc = dp.read_text(encoding="utf-8")
            if desc.strip():
                new = C.with_credits_section(desc, man)
                if new != desc: atomic_write(dp, new)
    r = validate_publish(pub, job, {k: dict(v, id=k) for k, v in tb["platforms"].items()}, targets)
    req = [x["id"] for x in C.required(man)]
    for p in r["platforms"]:
        dp = pub / p["id"] / "description.txt"
        ids = C.description_ids(dp.read_text(encoding="utf-8")) if dp.is_file() else set()
        p["description"]["credits_missing"] = [i for i in req if i not in ids]
        if p["description"]["credits_missing"]:
            p["errors"].append(f"{p['id']}: 简介缺署名 {p['description']['credits_missing']}"); r["ok"] = False
    if pub.is_dir():
        write_json(pub / "check.json", r)
    errs = [e for p in r["platforms"] for e in p["errors"]] + r["shared"]["errors"]
    for w in (w for p in r["platforms"] for w in p["warnings"]):
        print(f"[publish] 告警：{w}", file=sys.stderr)
    return _fail(7, errs, {"check": str(pub / "check.json")}) if not r["ok"] else summary(True, 0, {"publish": str(pub), "check": str(pub / "check.json")})


def c_deliverable(a):
    slug = Path(a.slug).resolve(); pub = slug / "publish"
    job = normalize_job(read_json(slug / "job.json"))
    try:
        tb, targets = _targets(job)
    except ValueError as e:
        return summary(False, 5, {}, [{"kind": "input", "message": str(e)}])
    man = A.load_manifest(slug / "assets-manifest.json")
    rd = lambda p: p.read_text(encoding="utf-8").strip() if p.is_file() else ""
    chk = read_json(pub / "check.json") if (pub / "check.json").is_file() else {}
    cw = {p.get("id"): p.get("warnings", []) for p in chk.get("platforms", [])}
    publish = {}
    for pid in targets:
        publish[pid] = {"title": rd(pub / pid / "title.txt"), "description": rd(pub / pid / "description.txt"),
                        "tags": [t.strip() for t in rd(pub / pid / "tags.txt").splitlines() if t.strip()],
                        "title_path": f"publish/{pid}/title.txt", "description_path": f"publish/{pid}/description.txt",
                        "tags_path": f"publish/{pid}/tags.txt", "warnings": cw.get(pid, [])}
    video = slug / "out/video.mp4"
    dur = None
    if video.exists():
        pr = ffprobe(video); dur = round(float(pr["format"]["duration"]), 3) if pr else None
    old = read_json(slug / "deliverable.json") if (slug / "deliverable.json").exists() else {}
    d = {"video": str(video), "duration_s": dur, "aspect": job["aspect"], "width": job["width"], "height": job["height"],
         "covers": sorted(str(p) for p in pub.glob("*.png")), "publish": publish,
         "credits": C.deliverable_credits(man),
         "out_dir": str(slug), "notes": list(dict.fromkeys((old.get("notes") or []) + (job.get("notes") or [])))}
    write_json(slug / "deliverable.json", d)
    # F-16：摘要字段齐全即可；成片是否存在由 validate.py video / render 验收，缺成片时 duration_s 为 null，不阻断摘要
    notes_extra = [] if video.exists() else ["缺少 out/video.mp4（成片尚未渲染）"]
    if notes_extra:
        d["notes"] = list(dict.fromkeys(list(d.get("notes") or []) + notes_extra))
        write_json(slug / "deliverable.json", d)
    errs = [f"署名不完整：{c['id']}" for c in d["credits"] if not (c["author"] and c["source_name"] and c["license"])]
    errs += [f"credits 含链接：{c['id']}" for c in d["credits"] if find_urls(json.dumps(c, ensure_ascii=False))]
    return _fail(7, errs, {"deliverable": str(slug / "deliverable.json")}) if errs else summary(True, 0, {"deliverable": str(slug / "deliverable.json")})


def _leak_scan(path, needles, hits, shown):
    """按字面子串查找；文本文件报告行号，二进制文件 line=None。绝不输出 Key 本身及其长度/前后缀/哈希。"""
    try:
        data = path.read_bytes()
    except OSError:
        return
    for which, k in needles:
        if not k or k not in data:
            continue
        try:
            text = data.decode("utf-8")
            lines = [i for i, ln in enumerate(text.splitlines(), 1) if k.decode("utf-8") in ln] or [None]
        except UnicodeDecodeError:
            lines = [None]
        for ln in lines:
            key = (str(path), ln, which)
            if key not in shown:
                shown.add(key); hits.append({"file": str(path), "line": ln, "which": which})


def c_leak(a):
    """审计（架构 v1.7 §6.6）：真实 Key 只读 <skill-dir>/.env 的 DOUBAO_TTS_API_KEY（不读环境变量；缺失/为空 → real_key="absent"，不算失败）；
    测试假 Key 由 --extra-secret-file 传入。范围：<slug>/（不含 node_modules）、技能包目录（除 .env 本身）、--scan 额外文件（如对话 JSONL）。"""
    from lib.envfile import parse_env
    skill = Path(a.skill_dir).resolve()
    env_p = skill / ".env"
    real = ""
    if env_p.is_file():
        real = (parse_env(env_p.read_text(encoding="utf-8")).get("DOUBAO_TTS_API_KEY") or "").strip()
    needles = []
    if real:
        needles.append(("real", real.encode()))
    # 退出码（V9-3）：显式路径不存在或不可读 → 2；密钥文件可读但为空或非 UTF-8 → 5
    if not Path(a.slug).exists():
        return summary(False, 2, {}, [{"kind": "usage", "message": f"slug 路径不存在：{a.slug}"}])
    for f in a.scan or []:
        try:
            with open(f, "rb"):
                pass
        except OSError as e:
            return summary(False, 2, {}, [{"kind": "usage", "message": f"--scan 文件不存在或不可读：{f}（{e.strerror}）"}])
    for f in a.extra_secret_file or []:
        try:
            raw = Path(f).read_bytes()
        except OSError as e:
            return summary(False, 2, {}, [{"kind": "usage", "message": f"--extra-secret-file 不存在或不可读：{f}（{e.strerror}）"}])
        try:
            v = raw.decode("utf-8").strip()
        except UnicodeDecodeError:
            return summary(False, 5, {}, [{"kind": "input", "message": f"--extra-secret-file 不是 UTF-8：{f}"}])
        if not v:
            return summary(False, 5, {}, [{"kind": "input", "message": f"--extra-secret-file 为空：{f}"}])
        needles.append(("fake", v.encode()))
    secret_files = {Path(f).resolve() for f in (a.extra_secret_file or [])}
    hits, shown = [], set()
    roots = [Path(a.slug).resolve(), skill]
    seen = set()
    for root in roots:
        if not root.exists():
            continue
        it = [root] if root.is_file() else sorted(root.rglob("*"))
        for p in it:
            if not p.is_file() or "node_modules" in p.parts or p.resolve() in seen:
                continue
            rp = p.resolve(); seen.add(rp)
            if rp == env_p.resolve() or rp in secret_files:
                continue
            _leak_scan(p, needles, hits, shown)
    for f in a.scan or []:
        p = Path(f)
        if p.is_dir():
            for q in sorted(p.rglob("*")):
                if q.is_file() and q.resolve() not in seen:
                    seen.add(q.resolve()); _leak_scan(q, needles, hits, shown)
        elif p.resolve() not in seen:
            seen.add(p.resolve()); _leak_scan(p, needles, hits, shown)
    report = {"ok": not hits, "real_key": "checked" if real else "absent", "hits": hits}
    if hits:
        for h in hits:
            print(f"[leak] 发现 Key 明文（{h['which']}）：{h['file']}" + (f":{h['line']}" if h["line"] else "（二进制）"), file=sys.stderr)
        return summary(False, 7, report, [{"kind": "key_leak", **h} for h in hits])
    return summary(True, 0, report)


def main(argv=None):
    ap = argparse.ArgumentParser(allow_abbrev=False, description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("timeline", "subtitles", "manifest", "job"):
        sub.add_parser(n, allow_abbrev=False).add_argument("file")
    p = sub.add_parser("storyboard", allow_abbrev=False); p.add_argument("file"); p.add_argument("--timeline"); p.add_argument("--manifest"); p.add_argument("--sources")
    p = sub.add_parser("sources", allow_abbrev=False); p.add_argument("script"); p.add_argument("sources")
    p = sub.add_parser("tokens", allow_abbrev=False); p.add_argument("--json", default=str(SKILL / "assets/tokens.json")); p.add_argument("--ts", required=True)
    p = sub.add_parser("video", allow_abbrev=False); p.add_argument("slug"); p.add_argument("--video")
    sub.add_parser("publish", allow_abbrev=False).add_argument("slug")
    sub.add_parser("deliverable", allow_abbrev=False).add_argument("slug")
    p = sub.add_parser("leak", allow_abbrev=False); p.add_argument("slug"); p.add_argument("--skill-dir", default=str(SKILL))
    p.add_argument("--extra-secret-file", action="append", help="含测试假 Key 的文件（可多次）")
    p.add_argument("--scan", action="append", help="额外要查的文件，如对话 JSONL（可多次）")
    a = ap.parse_args(argv)
    fn = {"timeline": c_timeline, "subtitles": c_simple("subtitles.schema.json"), "manifest": c_simple("assets-manifest.schema.json"),
          "job": c_simple("job.schema.json"), "storyboard": c_storyboard, "sources": c_sources, "tokens": c_tokens,
          "video": c_video, "publish": c_publish, "deliverable": c_deliverable, "leak": c_leak}[a.cmd]
    return fn(a)


if __name__ == "__main__":
    sys.exit(main())
