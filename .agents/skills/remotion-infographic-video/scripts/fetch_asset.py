#!/usr/bin/env python3
"""步骤 5：素材登记与核验（F-08、NF-04）。
  add          下载(--url)或复制(--file)素材，探测尺寸、判定授权与用途，写入 assets-manifest.json（顶层 {version:1, assets:[...]}）
  prune        未被 storyboard 任何镜头 asset_ids 引用的条目置 usable=false
  verify       按画布重新判定所有条目
  credits-diff 需署名且可用的素材须同时出现在：project/src/data/shot-badges.json、每个目标平台 publish/<平台>/description.txt 的“素材署名：”段（并检查无链接）、deliverable.json.credits
退出码：0 通过；2 用法；5 输入不合格；7 署名差集非空。"""
import argparse, json, shutil, sys, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.cli import summary, write_json, read_json  # noqa: E402
from lib import assets as A, credits as C, schema_check  # noqa: E402
from lib.job import PRESETS  # noqa: E402


def _canvas(aspect=None, canvas=None):
    if canvas:
        w, h = canvas.lower().split("x"); return int(w), int(h)
    return PRESETS[aspect or "landscape"]


def cmd_add(a):
    allowed, no_attr, denied = A.load_license_rules(with_denied=True)
    man = A.load_manifest(a.manifest)
    dest = Path(a.dest); dest.mkdir(parents=True, exist_ok=True)
    src_name = Path(a.file).name if a.file else Path(a.url.split("?")[0]).name or f"{a.id}.bin"
    target = dest / f"{a.id}-{src_name}"
    try:
        if a.file:
            shutil.copy2(a.file, target)
        else:
            req = urllib.request.Request(a.url, headers={"User-Agent": "remotion-infographic-video/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                target.write_bytes(r.read())
        data = target.read_bytes()
        fetched = True
    except (OSError, ValueError) as e:
        print(f"[fetch_asset] 获取失败：{e}", file=sys.stderr); data, fetched = b"", False
    size = A.image_size_from_header(data) if fetched else None
    opens = size is not None
    source = "AI 生成" if a.ai_generated else (a.source_url or a.url or "")
    lic = a.license or ("AI 生成" if a.ai_generated else "unknown")
    lic_ok = A.license_known(lic, allowed, denied)
    need = A.needs_attribution(lic, no_attr) if lic_ok else bool(a.author)
    cw, ch = _canvas(a.aspect, a.canvas)
    usage = A.classify_usage(size[0] if size else None, size[1] if size else None, cw, ch, lic_ok, opens)
    e = {"id": a.id, "file": str(target), "kind": a.kind, "content": a.content, "source": source or "unknown", "license": lic,
         "needs_attribution": bool(need), "opens": opens, "usage": usage,
         "source_name": a.source_name or ("AI 生成" if a.ai_generated else ""),
         "usable": usage != "rejected" and (not need or bool(a.author))}
    if a.author:
        e["author"] = a.author
    if size:
        e["width"], e["height"] = size
    man = [x for x in man if x.get("id") != a.id] + [e]
    write_json(a.manifest, A.manifest_doc(man))
    notes = []
    if not lic_ok: notes.append("授权不明：已登记但 usable=false，不得使用")
    if not opens: notes.append("文件无法打开/不是可识别图片：usable=false")
    if need and not a.author: notes.append("需署名但缺 --author：usable=false")
    return summary(True, 0, {"entry": e, "notes": notes})


def cmd_prune(a):
    man = A.load_manifest(a.manifest)
    used = A.storyboard_asset_ids(read_json(a.storyboard))
    pruned = []
    for e in man:
        if e["id"] not in used and e.get("usable"):
            e["usable"] = False; pruned.append(e["id"])
    write_json(a.manifest, A.manifest_doc(man))
    return summary(True, 0, {"pruned": pruned, "used": sorted(used)})


def cmd_verify(a):
    allowed, _, denied = A.load_license_rules(with_denied=True)
    man = A.load_manifest(a.manifest)
    errs = schema_check.validate(A.manifest_doc(man), schema_check.load_schema("assets-manifest.schema.json"))
    if errs:
        return summary(False, 5, {}, [{"kind": "schema", "message": e} for e in errs])
    cw, ch = _canvas(a.aspect, a.canvas)
    changed = []
    for e in man:
        p = Path(e["file"])
        opens = e.get("opens", False)
        if p.is_file():
            sz = A.image_size_from_header(p.read_bytes()) if e.get("kind", "image") == "image" else (e.get("width"), e.get("height"))
            opens = bool(sz and sz[0]); 
            if sz and sz[0]: e["width"], e["height"] = sz
        u = A.classify_usage(e.get("width"), e.get("height"), cw, ch, A.license_known(e.get("license"), allowed, denied), opens)
        usable = u != "rejected" and (not e.get("needs_attribution") or bool(e.get("author") or e.get("attribution")))
        if (u, usable, opens) != (e.get("usage"), e.get("usable"), e.get("opens")):
            changed.append(e["id"])
        e.update(usage=u, usable=usable, opens=opens)
    write_json(a.manifest, A.manifest_doc(man))
    return summary(True, 0, {"changed": changed, "canvas": f"{cw}x{ch}"})


def credits_report(manifest_path, slug):
    """返回 (diff, man, url_hits)。简介按平台逐个比对；缺平台目录 = 该平台全缺。"""
    from lib.job import normalize_job
    from lib.verify import resolve_targets, find_urls
    import validate as V
    man = A.load_manifest(manifest_path)
    slug = Path(slug)
    bp = slug / "project" / "src" / "data" / "shot-badges.json"
    badges = read_json(bp) if bp.exists() else []
    job = normalize_job(read_json(slug / "job.json")) if (slug / "job.json").exists() else {}
    targets = resolve_targets(job, V.publish_table()["default_targets"])
    descs, hits = {}, []
    for pid in targets:
        for n in ("title.txt", "description.txt", "tags.txt"):
            p = slug / "publish" / pid / n
            t = p.read_text(encoding="utf-8") if p.is_file() else None
            if n == "description.txt": descs[pid] = t or ""
            if t and find_urls(t): hits.append(f"publish/{pid}/{n}")
    dl_p = slug / "deliverable.json"
    dl = read_json(dl_p) if dl_p.exists() else {}
    if find_urls(json.dumps(dl.get("credits") or [], ensure_ascii=False)): hits.append("deliverable.json.credits")
    return C.credits_diff(A.manifest_doc(man), badges, descs, dl), man, hits


def cmd_credits_diff(a):
    d, man, hits = credits_report(a.manifest, a.slug_dir)
    parts = [p.strip() for p in a.only.split(",")] if a.only else ["badge", "description", "deliverable"]
    d = {k: v for k, v in d.items() if k in parts}
    bad = {k: v for k, v in d.items() if (any(v.values()) if isinstance(v, dict) else v)}
    errs = [{"kind": "credits_missing", "where": k, "ids": v} for k, v in bad.items()]
    if not a.only:
        errs += [{"kind": "url_found", "where": h} for h in hits]
    for e in errs:
        print(f"[credits-diff] {e}", file=sys.stderr)
    if errs:
        return summary(False, 7, {"diff": d}, errs)
    return summary(True, 0, {"diff": d, "required": [x["id"] for x in C.required(man)]})


def main(argv=None):
    ap = argparse.ArgumentParser(allow_abbrev=False, description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add", allow_abbrev=False); p.add_argument("--manifest", required=True); p.add_argument("--id", required=True)
    g = p.add_mutually_exclusive_group(required=True); g.add_argument("--url"); g.add_argument("--file")
    p.add_argument("--content", required=True)
    s = p.add_mutually_exclusive_group(); s.add_argument("--source-url"); s.add_argument("--ai-generated", action="store_true")
    p.add_argument("--license"); p.add_argument("--author"); p.add_argument("--source-name", help="来源名称（不含链接），写入 source_name"); p.add_argument("--kind", default="image", choices=["image", "video", "audio"])
    p.add_argument("--aspect", choices=["landscape", "portrait"], default="landscape"); p.add_argument("--canvas")
    p.add_argument("--dest", required=True)
    p = sub.add_parser("prune", allow_abbrev=False); p.add_argument("--manifest", required=True); p.add_argument("--storyboard", required=True)
    p = sub.add_parser("verify", allow_abbrev=False); p.add_argument("--manifest", required=True); p.add_argument("--canvas")
    p.add_argument("--aspect", choices=["landscape", "portrait"])
    p = sub.add_parser("credits-diff", allow_abbrev=False); p.add_argument("--manifest", required=True); p.add_argument("--slug-dir", required=True)
    p.add_argument("--only", help="只比对部分去处：badge,description,deliverable（步骤 7 用 badge）")
    a = ap.parse_args(argv)
    try:
        A.load_license_rules()
    except A.LicenseRulesError as e:
        print(f"[fetch_asset] {e}", file=sys.stderr)
        return summary(False, 5, {}, [{"kind": "licenses_invalid", "message": str(e)}])
    return {"add": cmd_add, "prune": cmd_prune, "verify": cmd_verify, "credits-diff": cmd_credits_diff}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
