"""署名三处一致性（F-08、NF-04，架构 v1.2 Q-04）：
(a) project/src/data/shot-badges.json：[{shot_no, asset_id, text}]
(b) publish/description.txt 中以一行“素材署名：”开头的段落，每行 `- [<asset_id>] <作者> · <来源名称> · <许可>`，按 [asset_id] 匹配
(c) deliverable.json.credits[].id
被判定集合 = manifest 中 needs_attribution && usable 的条目。"""
import re
from urllib.parse import urlparse

HEADER = "素材署名："
_HEADER_RE = re.compile(r"(?m)^素材署名[：:]\s*$")
_ID_RE = re.compile(r"\[(A[0-9]{2,3})\]")
from .verify import URL_RE  # noqa: E402  （§4.6 唯一定义在 lib/verify.py）

SITE_NAMES = {"commons.wikimedia.org": "Wikimedia Commons", "wikimedia.org": "Wikimedia", "wikipedia.org": "Wikipedia",
              "unsplash.com": "Unsplash", "pexels.com": "Pexels", "pixabay.com": "Pixabay", "flickr.com": "Flickr",
              "nasa.gov": "NASA", "github.com": "GitHub"}


def assets_of(manifest):
    if isinstance(manifest, dict):
        return list(manifest.get("assets", []))
    return list(manifest or [])


def required(manifest):
    return [a for a in assets_of(manifest) if a.get("needs_attribution") and a.get("usable")]


def author_of(a):
    return a.get("author") or a.get("attribution") or ""


def source_name_of(a):
    """对外署名只用来源名称，不放链接（U-3）。"""
    if a.get("source_name"):
        return a["source_name"]
    src = a.get("source") or ""
    if not re.match(r"(?i)^https?://", src):
        return src
    host = (urlparse(src).hostname or "").lower()
    host = host[4:] if host.startswith("www.") else host
    for dom, name in SITE_NAMES.items():
        if host == dom or host.endswith("." + dom):
            return name
    parts = host.split(".")
    return (parts[-2] if len(parts) >= 2 else host).capitalize() or "未知来源"


def credit_line(a):
    return f"- [{a['id']}] {author_of(a)} · {source_name_of(a)} · {a.get('license', '')}"


def badge_text(a):
    return " · ".join(x for x in (author_of(a), source_name_of(a), a.get("license")) if x)


def description_section(text):
    m = _HEADER_RE.search(text or "")
    return text[m.end():] if m else ""


def description_ids(text):
    return set(_ID_RE.findall(description_section(text)))


def credits_diff(manifest, shot_badges, descriptions, deliverable):
    """descriptions: {platform: 简介全文}（v1.4，按平台；传 str 时视为单份）。
    返回 {badge: [缺失 id], description: {platform: [缺失 id]}, deliverable: [缺失 id]}。"""
    req = [a["id"] for a in required(manifest)]
    b = {x.get("asset_id") for x in (shot_badges or []) if x.get("text")}
    v = {c.get("id") for c in ((deliverable or {}).get("credits") or [])}
    if isinstance(descriptions, str) or descriptions is None:
        d = description_ids(descriptions or "")
        desc = [i for i in req if i not in d]
    else:
        desc = {}
        for pid, text in descriptions.items():
            d = description_ids(text or "")
            desc[pid] = [i for i in req if i not in d]
    return {"badge": [i for i in req if i not in b], "description": desc, "deliverable": [i for i in req if i not in v]}


def diff_empty(d):
    desc = d["description"]
    return not d["badge"] and not d["deliverable"] and not (any(desc.values()) if isinstance(desc, dict) else desc)


def with_credits_section(text, manifest):
    """幂等：去掉已有“素材署名：”段后按 manifest 重新追加；无需署名项时只去掉旧段。"""
    m = _HEADER_RE.search(text or "")
    body = (text[:m.start()] if m else (text or "")).rstrip()
    req = required(manifest)
    if not req:
        return body + "\n"
    return body + "\n\n" + HEADER + "\n" + "\n".join(credit_line(a) for a in req) + "\n"


def shot_badges(storyboard, manifest):
    by = {a["id"]: a for a in assets_of(manifest)}
    out = []
    for s in storyboard.get("sections", []):
        for sh in s.get("shots", []):
            for aid in sh.get("asset_ids") or []:
                a = by.get(aid)
                if a and a.get("usable") and a.get("needs_attribution"):
                    out.append({"shot_no": sh["shot_no"], "asset_id": aid, "text": badge_text(a)})
    return out


def deliverable_credits(manifest):
    """deliverable.json.credits：{id, author, source_name, license}，不含 URL（v1.3 U-3）。"""
    return [{"id": a["id"], "author": author_of(a), "source_name": source_name_of(a), "license": a.get("license", "")}
            for a in required(manifest)]
