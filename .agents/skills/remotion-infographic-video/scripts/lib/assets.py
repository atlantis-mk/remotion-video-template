"""素材：尺寸探测、授权判定、manifest 读写、署名差集（F-08、NF-04）。"""
import json, re, struct
from pathlib import Path

import re as _re

# 内置默认值（与 assets/licenses.json 一致；文件存在时以文件为准）。架构 v1.9 V9-2 / A-27。
LICENSE_OK = ("cc0", "cc by", "cc by sa", "public domain", "公有领域", "pexels", "unsplash", "pixabay",
              "ai 生成", "自制", "原创", "用户提供", "代码绘制")
NO_ATTR = ("cc0", "public domain", "公有领域", "pexels", "unsplash", "pixabay", "ai 生成", "自制", "原创", "用户提供", "代码绘制")
DENIED = ("nc", "nd", "noncommercial", "non commercial", "noderivs", "no derivatives", "all rights reserved", "editorial",
          "版权所有", "非商业", "禁止演绎")


class LicenseRulesError(ValueError):
    """licenses.json 不合格（退出 5）。"""


def norm_license(s) -> str:
    """规范化：转小写；连续的空格、-、_ 合并为一个空格；去首尾空白。中文与 ASCII 之间的空格也去掉（"ai生成" ≡ "ai 生成"）。"""
    t = _re.sub(r"[\s\-_]+", " ", str(s or "").lower()).strip()
    return _re.sub(r"(?<=[a-z0-9]) ?(?=[\u4e00-\u9fff])|(?<=[\u4e00-\u9fff]) ?(?=[a-z0-9])", " ", t)


def _dedupe(items):
    out = []
    for x in items:
        n = norm_license(x)
        if n and n not in out:
            out.append(n)
    return out


def _is_ascii(s):
    return all(ord(c) < 128 for c in s)


def is_denied(lic, denied=DENIED) -> bool:
    """ASCII 项按词元匹配（前后补空格后包含 " 项 "）；中文项按子串匹配。"""
    l = norm_license(lic); padded = f" {l} "
    for d in (norm_license(x) for x in denied):
        if d and ((f" {d} " in padded) if _is_ascii(d) else (d in l)):
            return True
    return False


def _matches(l, items) -> bool:
    """与某项相等，或以“该项 + 空格/数字”开头（不做子串匹配）。"""
    for a in (norm_license(x) for x in items):
        if a and (l == a or (l.startswith(a) and len(l) > len(a) and (l[len(a)] == " " or l[len(a)].isdigit()))):
            return True
    return False


def load_license_rules(skill_dir=None, with_denied=False):
    """读取 assets/licenses.json（按 licenses.schema.json 校验 + no_attribution ⊆ allowed + allowed∩denied=∅；不满足 → LicenseRulesError，退出 5）。
    返回 (allowed, no_attribution) 或 with_denied=True 时 (allowed, no_attribution, denied)，均为规范化去重后的列表。"""
    root = Path(skill_dir or Path(__file__).resolve().parents[2])
    p = root / "assets" / "licenses.json"
    if p.is_file():
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
            raise LicenseRulesError(f"{p} 无法解析：{e}")
        sp = root / "assets" / "schemas" / "licenses.schema.json"
        if sp.is_file():
            from .schema_check import validate
            errs = validate(d, json.loads(sp.read_text(encoding="utf-8")))
            if errs:
                raise LicenseRulesError(f"{p} 不符合 licenses.schema.json：{errs[:3]}")
        allowed, no_attr, denied = _dedupe(d.get("allowed") or []), _dedupe(d.get("no_attribution") or []), _dedupe(d.get("denied") or [])
        if not denied:
            raise LicenseRulesError(f"{p} 缺必填字段 denied")
    else:
        allowed, no_attr, denied = _dedupe(LICENSE_OK), _dedupe(NO_ATTR), _dedupe(DENIED)
    extra = [x for x in no_attr if x not in allowed]
    if extra:
        raise LicenseRulesError(f"licenses.json：no_attribution 必须是 allowed 的子集，多出 {extra}")
    both = [x for x in allowed if x in denied]
    if both:
        raise LicenseRulesError(f"licenses.json：allowed 与 denied 有相同项 {both}")
    return (allowed, no_attr, denied) if with_denied else (allowed, no_attr)


def license_known(lic, allowed=LICENSE_OK, denied=DENIED) -> bool:
    """先查 denied（命中 → 不可用）；再与 allowed 规范化匹配；其余 → 授权不明。"""
    l = norm_license(lic)
    if not l or l in ("unknown", "未知", "不明", "?"):
        return False
    if is_denied(l, denied):
        return False
    return _matches(l, allowed)


def needs_attribution(lic, no_attr=NO_ATTR) -> bool:
    return not _matches(norm_license(lic), no_attr)


def classify_usage(w, h, canvas_w, canvas_h, license_ok, opens) -> str:
    if not opens or not license_ok or not w or not h:
        return "rejected"
    return "fullscreen" if min(w, h) >= min(canvas_w, canvas_h) else "card-only"


def image_size_from_header(data: bytes):
    try:
        if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
            return struct.unpack(">II", data[16:24])
        if data[:6] in (b"GIF87a", b"GIF89a"):
            return struct.unpack("<HH", data[6:10])
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            c = data[12:16]
            if c == b"VP8X":
                return (int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1)
            if c == b"VP8 ":
                w, h = struct.unpack("<HH", data[26:30]); return (w & 0x3FFF, h & 0x3FFF)
            if c == b"VP8L":
                b = int.from_bytes(data[21:25], "little"); return ((b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1)
            return None
        if data[:2] == b"\xff\xd8":
            i = 2
            while i + 9 < len(data):
                if data[i] != 0xFF:
                    i += 1; continue
                m = data[i + 1]
                if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
                    i += 2; continue
                seg = struct.unpack(">H", data[i + 2:i + 4])[0]
                if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = struct.unpack(">HH", data[i + 5:i + 9]); return (w, h)
                i += 2 + seg
    except (struct.error, IndexError):
        return None
    return None


def load_manifest(path):
    """读取 manifest，返回条目列表；文件不存在 → []。顶层格式 {"version":1,"assets":[...]}（兼容旧数组）。"""
    p = Path(path)
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding="utf-8") or "{}")
    return list(d.get("assets", [])) if isinstance(d, dict) else list(d)


def manifest_doc(entries):
    return {"version": 1, "assets": list(entries)}


def storyboard_asset_ids(storyboard):
    ids = set()
    for s in storyboard.get("sections", []):
        for sh in s.get("shots", []):
            ids.update(sh.get("asset_ids") or [])
    return ids
