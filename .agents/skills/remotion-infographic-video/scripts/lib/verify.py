"""成片与发布物验收纯函数（F-12、F-13）。"""
import re, unicodedata
from fractions import Fraction
from pathlib import Path

TOL = 0.1 + 1e-6
COVER_SIZES = {"landscape": [(1920, 1080)], "portrait": [(1080, 1440)]}   # v1.3：竖屏只出 3:4 封面


def verify_video(probe: dict, job: dict, audio_seconds) -> list:
    errs = []
    streams = probe.get("streams", [])
    vs = [s for s in streams if s.get("codec_type") == "video"]
    aus = [s for s in streams if s.get("codec_type") == "audio"]
    if not vs:
        return ["无视频流"]
    v = vs[0]
    if (v.get("width"), v.get("height")) != (job.get("width"), job.get("height")):
        errs.append(f"分辨率 {v.get('width')}x{v.get('height')} ≠ {job.get('width')}x{job.get('height')}")
    try:
        fps = Fraction(v.get("r_frame_rate", "0/1"))
    except (ValueError, ZeroDivisionError):
        fps = Fraction(0)
    if fps != Fraction(int(job.get("fps", 30))):
        errs.append(f"帧率 {v.get('r_frame_rate')} ≠ {job.get('fps', 30)}/1")
    if not aus or aus[0].get("codec_name") != "aac":
        errs.append("缺少 AAC 音轨")
    vdur = float(v.get("duration") or probe.get("format", {}).get("duration") or 0)
    if aus:
        adur = float(aus[0].get("duration") or 0)
        if abs(vdur - adur) > TOL:
            errs.append(f"音视频时长差 {abs(vdur - adur):.3f}s > 0.1s")
    if audio_seconds is not None and abs(vdur - float(audio_seconds)) > TOL:
        errs.append(f"视频时长 {vdur:.3f}s 与配音 {float(audio_seconds):.3f}s 差 > 0.1s")
    return errs


# ---- 扩展字素簇（简化版 UAX #29：组合符、ZWJ 序列、变体选择符、肤色修饰、区旗对、韩文音节块）----
def _is_extend(ch):
    o = ord(ch)
    return (unicodedata.category(ch) in ("Mn", "Me", "Mc") or 0xFE00 <= o <= 0xFE0F or 0x1F3FB <= o <= 0x1F3FF
            or 0xE0020 <= o <= 0xE007F or o == 0x200C)


def _is_ri(ch):
    return 0x1F1E6 <= ord(ch) <= 0x1F1FF


def graphemes(s: str):
    s = unicodedata.normalize("NFC", s or "")
    out, i, n = [], 0, len(s)
    while i < n:
        j = i + 1
        if s[i] == "\r" and j < n and s[j] == "\n":
            out.append(s[i:j + 1]); i = j + 1; continue
        if _is_ri(s[i]) and j < n and _is_ri(s[j]):
            j += 1
        while j < n:
            if _is_extend(s[j]):
                j += 1
            elif s[j] == "\u200d" and j + 1 < n:
                j += 2
            elif s[j] == "\u200d":
                j += 1
            else:
                break
        out.append(s[i:j]); i = j
    return out


def count_title_chars(s: str) -> int:
    """NFC 后按扩展字素簇计数：中文/英文字母/数字/标点/空格/emoji 各算 1。"""
    return len(graphemes(s))


def count_text(s: str, mode: str = "grapheme") -> int:
    if mode == "grapheme":
        return count_title_chars(s)
    if mode == "utf8_bytes":
        return len((s or "").encode("utf-8"))
    if mode == "cjk1_ascii_half":
        import math
        half = sum(1 for g in graphemes(s) if len(g) == 1 and g.isascii() and g.isalnum())
        return math.ceil(len(graphemes(s)) - half + half / 2)
    raise ValueError(f"未知计数模式 {mode}")


def png_size(p):
    b = Path(p).read_bytes()[:32]
    if b[:8] == b"\x89PNG\r\n\x1a\n" and b[12:16] == b"IHDR":
        return int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")
    return None


YOUTUBE_FORBID = "<>"   # YouTube 官方：标题、简介不得含 < >
PLATFORM_IDS = ["douyin", "bilibili", "xiaohongshu", "channels", "youtube"]


def resolve_targets(job: dict, default_targets) -> list:
    """job.platforms 优先（去重保序），缺省用 default_targets；未知平台 id → ValueError（退出 5）。"""
    src = job.get("platforms") or list(default_targets)
    out = []
    for p in src:
        if p not in PLATFORM_IDS:
            raise ValueError(f"未知平台 id：{p}（可选 {PLATFORM_IDS}）")
        if p not in out:
            out.append(p)
    return out


def _field(path, text, rule, pid, part):
    """按本平台单条规则检查一个字段，返回 (FieldCheck, errors, warnings)。"""
    errs, warns = [], []
    mode = (rule or {}).get("count", "grapheme")
    raw = text if text is not None else ""
    body = raw.strip()
    n = count_text(raw if part == "简介" else body, mode)   # 简介按全文计（含署名段与换行），标题去首尾空白
    fc = {"path": path, "count": n, "mode": mode, "status": (rule or {}).get("status", "none"), "severity": "ok",
          "urls": find_urls(raw)}
    if text is None:
        errs.append(f"{pid}: 缺少 {path}")
    elif not body:
        errs.append(f"{pid}: {path} 为空")
    if fc["urls"]:
        errs.append(f"{pid}: {path} 含链接 {fc['urls'][:3]}（文案不放链接）")
    if rule and body:
        mx, mn = rule.get("max"), rule.get("min")
        if mx is not None: fc["max"] = mx
        if mn is not None: fc["min"] = mn
        bad = []
        if mx is not None and (n >= mx if rule.get("strict_less_than") else n > mx):
            bad.append(f"{part} {n}（{mode}）超过上限 {'<' if rule.get('strict_less_than') else '≤'}{mx}")
        if mn is not None and n < mn:
            bad.append(f"{part} {n} 少于下限 {mn}")
        forbid = rule.get("forbid_chars", "") + (YOUTUBE_FORBID if pid == "youtube" else "")
        fc_chars = sorted({c for c in forbid if c in body})
        if fc_chars:
            bad.append(f"{part} 含不允许的字符 {fc_chars}")
        for m in bad:
            (errs if rule.get("status") == "official" else warns).append(f"{pid}: {m}（{rule.get('status')}，{rule.get('source', '')}）")
    fc["severity"] = "error" if errs else ("warning" if warns else "ok")
    return fc, errs, warns


def count_tags(tags, rule) -> int:
    """标签连接后的总长：Σ计数 + 连接符；youtube_tags 模式下含空格的标签按两侧加引号计（+2）。"""
    rule = rule or {}
    mode = rule.get("count", "grapheme")
    base = "grapheme" if mode == "youtube_tags" else mode
    join = rule.get("join", ",")
    n = sum(count_text(t, base) + (2 if mode == "youtube_tags" and " " in t else 0) for t in tags)
    return n + count_text(join, base) * max(len(tags) - 1, 0)


def _tags(pid, path, text, rule):
    errs, warns = [], []
    tags = [x.strip() for x in (text or "").splitlines() if x.strip()]
    if text is None:
        errs.append(f"{pid}: 缺少 {path}")
    elif not tags:
        errs.append(f"{pid}: {path} 为空")
    urls = [u for t in tags for u in find_urls(t)]
    if urls:
        errs.append(f"{pid}: 标签含链接 {urls[:3]}（文案不放链接）")
    if rule and tags:
        bad = []
        if rule.get("max_items") is not None and len(tags) > rule["max_items"]:
            bad.append(f"标签 {len(tags)} 个，超过 {rule['max_items']} 个")
        if rule.get("joined_max") is not None:
            n = count_tags(tags, rule); mx = rule["joined_max"]
            if (n >= mx) if rule.get("strict_less_than") else (n > mx):
                bad.append(f"标签连接后总长 {n} 超过上限 {'<' if rule.get('strict_less_than') else '≤'}{mx}")
        for m in bad:
            (errs if rule.get("status") == "official" else warns).append(f"{pid}: {m}（{rule.get('status')}，{rule.get('source', '')}）")
    info = {"path": path, "items": len(tags), "rule": "platform" if rule else "nonempty_only",
            "status": (rule or {}).get("status", "none"), "severity": "error" if errs else ("warning" if warns else "ok"), "urls": urls}
    return info, errs, warns


def validate_publish(publish_dir, job: dict, rules, targets) -> dict:
    """逐平台校验 publish/<p>/title.txt、description.txt、tags.txt（v1.5），每套只用本平台规则：
    official 不满足 → error，unofficial → warning；任一处含链接 → error；无规则的标签只查非空与无链接。封面各平台共用、按画幅。
    返回 PublishCheck：{ok, targets, platforms:[{id, dir, title, description, tags, errors, warnings}], shared:{covers, errors, warnings}}。"""
    d = Path(publish_dir)
    rules = {r["id"]: r for r in rules} if isinstance(rules, list) else dict(rules or {})
    rd = lambda p: p.read_text(encoding="utf-8") if p.is_file() else None
    platforms, shared_errs = [], []
    for pid in targets:
        rule = rules.get(pid, {})
        pdir, rel = d / pid, f"publish/{pid}"
        t_fc, te, tw = _field(f"{rel}/title.txt", rd(pdir / "title.txt"), rule.get("title"), pid, "标题")
        d_fc, de, dw = _field(f"{rel}/description.txt", rd(pdir / "description.txt"), rule.get("description"), pid, "简介")
        d_fc["credits_missing"] = []
        g_fc, ge, gw = _tags(pid, f"{rel}/tags.txt", rd(pdir / "tags.txt"), rule.get("tags"))
        platforms.append({"id": pid, "dir": rel, "title": t_fc, "description": d_fc, "tags": g_fc,
                          "errors": te + de + ge, "warnings": tw + dw + gw})
    want = sorted(COVER_SIZES[job.get("aspect", "landscape")])
    covers = []
    for p in sorted(d.glob("*.png")):
        sz = png_size(p)
        covers.append({"path": f"publish/{p.name}", "width": sz[0] if sz else 0, "height": sz[1] if sz else 0,
                       "ok": bool(sz and tuple(sz) in want)})
    have = sorted((c["width"], c["height"]) for c in covers)
    if have != want:
        shared_errs.append(f"封面尺寸 {have} ≠ {want}（{job.get('aspect')}）")
    ok = not shared_errs and not any(p["errors"] for p in platforms)
    return {"ok": ok, "targets": list(targets), "platforms": platforms,
            "shared": {"covers": covers, "errors": shared_errs, "warnings": []}}


URL_RE = re.compile(r"(?i)\b(?:https?://|www\.)\S+|\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:com|cn|net|org|io|tv|me|co|info|gov|edu)(?:/\S*)?\b")


def find_urls(text: str) -> list:
    """对外文案（简介署名段、SourceBadge、deliverable.credits）不得含链接（v1.3 U-3，§4.6 URL_RE）。"""
    return [m.group(0) for m in URL_RE.finditer(text or "")]
